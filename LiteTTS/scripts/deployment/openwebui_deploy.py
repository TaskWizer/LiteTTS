#!/usr/bin/env python3
"""
OpenWebUI Deployment Script (Python version)
Cross-platform deployment utility for OpenWebUI with TLS and multiple API providers
Replaces openwebui-deploy.sh with better error handling and cross-platform support
"""

import os
import sys
import subprocess
import logging
import argparse
import secrets
from pathlib import Path
from typing import Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenWebUIDeployer:
    """OpenWebUI deployment utility"""
    
    def __init__(self, domain: str, email: str):
        self.domain = domain
        self.email = email
        self.secret_key = secrets.token_hex(32)
        self.jwt_secret = secrets.token_hex(32)
        
        # API keys (to be set by user)
        self.api_keys = {
            "openrouter": "",
            "google_ai_studio": "",
            "huggingface": "",
            "groq": ""
        }
        
        # Directories
        self.data_dir = Path("data")
        self.certs_dir = Path("certs")
    
    def create_directories(self):
        """Create necessary directories"""
        try:
            self.data_dir.mkdir(exist_ok=True)
            self.certs_dir.mkdir(exist_ok=True)
            logger.info("✅ Created necessary directories")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create directories: {e}")
            return False
    
    def set_api_keys(self, api_keys: Dict[str, str]):
        """Set API keys"""
        self.api_keys.update(api_keys)
        logger.info("✅ API keys configured")
    
    def generate_docker_compose(self, use_https: bool = True) -> str:
        """Generate docker-compose.yml content"""
        
        # Base environment variables
        env_vars = [
            f"WEBUI_SECRET_KEY={self.secret_key}",
            "OLLAMA_API_BASE_URL=",  # Empty to disable Ollama
            "OPENROUTER_API_BASE_URL=https://openrouter.ai/api/v1",
            f"OPENROUTER_API_KEY={self.api_keys['openrouter']}",
            f"GOOGLE_AI_STUDIO_API_KEY={self.api_keys['google_ai_studio']}",
            f"HUGGINGFACE_API_KEY={self.api_keys['huggingface']}",
            f"GROQ_API_KEY={self.api_keys['groq']}",
            "DISABLE_SIGNUP=false",
            "ENABLE_SIGNUP=false",
            "WEBUI_AUTH=login",
            f"WEBUI_JWT_SECRET={self.jwt_secret}"
        ]
        
        # Add HTTPS configuration if enabled
        if use_https:
            env_vars.extend([
                "WEBUI_HTTPS=true",
                "WEBUI_CERT_FILE=/app/backend/certs/fullchain.pem",
                "WEBUI_KEY_FILE=/app/backend/certs/privkey.pem"
            ])
        else:
            env_vars.append("WEBUI_HTTPS=false")
        
        # Format environment variables for YAML
        env_section = "\n".join(f"      - {var}" for var in env_vars)
        
        compose_content = f"""version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: openwebui
    restart: unless-stopped
    ports:
      - "{'443' if use_https else '80'}:8080"
    volumes:
      - ./data:/app/backend/data
      - ./certs:/app/backend/certs
    environment:
{env_section}
    networks:
      - webnet

networks:
  webnet:
    driver: bridge
"""
        return compose_content
    
    def write_docker_compose(self, use_https: bool = True):
        """Write docker-compose.yml file"""
        try:
            content = self.generate_docker_compose(use_https)
            with open("docker-compose.yml", "w") as f:
                f.write(content)
            logger.info("✅ Generated docker-compose.yml")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write docker-compose.yml: {e}")
            return False
    
    def check_certificates(self) -> bool:
        """Check if TLS certificates exist"""
        fullchain = self.certs_dir / "fullchain.pem"
        privkey = self.certs_dir / "privkey.pem"
        return fullchain.exists() and privkey.exists()
    
    def setup_letsencrypt(self) -> bool:
        """Setup Let's Encrypt certificates"""
        try:
            logger.info("🔒 Setting up Let's Encrypt certificates...")
            
            # Check if certbot is installed
            result = subprocess.run(["which", "certbot"], capture_output=True)
            if result.returncode != 0:
                logger.info("📦 Installing certbot...")
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "certbot"], check=True)
            
            # Generate certificates
            cmd = [
                "sudo", "certbot", "certonly", "--standalone",
                "-d", self.domain,
                "--non-interactive",
                "--agree-tos",
                "-m", self.email
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"❌ Certbot failed: {result.stderr}")
                return False
            
            # Copy certificates to local directory
            src_fullchain = f"/etc/letsencrypt/live/{self.domain}/fullchain.pem"
            src_privkey = f"/etc/letsencrypt/live/{self.domain}/privkey.pem"
            
            subprocess.run(["sudo", "cp", src_fullchain, str(self.certs_dir)], check=True)
            subprocess.run(["sudo", "cp", src_privkey, str(self.certs_dir)], check=True)
            
            # Fix permissions
            user = os.getenv("USER", "root")
            subprocess.run(["sudo", "chown", "-R", f"{user}:{user}", str(self.certs_dir)], check=True)
            
            logger.info("✅ Let's Encrypt certificates configured")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to setup Let's Encrypt: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error setting up certificates: {e}")
            return False
    
    def start_container(self):
        """Start the OpenWebUI container"""
        try:
            logger.info("🚀 Starting OpenWebUI container...")
            result = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ OpenWebUI container started successfully")
                return True
            else:
                logger.error(f"❌ Failed to start container: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start container: {e}")
            return False
    
    def deploy(self, cert_choice: str = "auto"):
        """Run the complete deployment process"""
        logger.info("🚀 Starting OpenWebUI deployment...")
        logger.info(f"🌐 Domain: {self.domain}")
        logger.info(f"📧 Email: {self.email}")
        
        # Create directories
        if not self.create_directories():
            return False
        
        # Handle certificates
        use_https = True
        
        if cert_choice == "letsencrypt" or (cert_choice == "auto" and not self.check_certificates()):
            if not self.setup_letsencrypt():
                logger.warning("⚠️  Certificate setup failed, continuing without HTTPS")
                use_https = False
        elif cert_choice == "none":
            logger.info("ℹ️  Continuing without HTTPS")
            use_https = False
        elif cert_choice == "existing":
            if not self.check_certificates():
                logger.error("❌ Certificates not found in certs/ directory")
                return False
            logger.info("✅ Using existing certificates")
        
        # Generate docker-compose.yml
        if not self.write_docker_compose(use_https):
            return False
        
        # Start container
        if not self.start_container():
            return False
        
        # Success message
        protocol = "https" if use_https else "http"
        port = "" if (use_https and "443") or (not use_https and "80") else ":8080"
        
        logger.info("🎉 OpenWebUI deployment complete!")
        logger.info(f"🌐 Access your instance at: {protocol}://{self.domain}{port}")
        logger.info("")
        logger.info("📋 Initial setup:")
        logger.info("1. Visit the URL above")
        logger.info("2. Create your first admin account")
        logger.info("3. Configure your preferred models in settings")
        
        return True

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Deploy OpenWebUI with TLS and multiple API providers",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--domain",
        type=str,
        required=True,
        help="Domain name for the deployment"
    )
    
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Email for Let's Encrypt notifications"
    )
    
    parser.add_argument(
        "--cert-method",
        choices=["auto", "letsencrypt", "existing", "none"],
        default="auto",
        help="Certificate method (default: auto)"
    )
    
    parser.add_argument(
        "--openrouter-key",
        type=str,
        default="",
        help="OpenRouter API key"
    )
    
    parser.add_argument(
        "--google-key",
        type=str,
        default="",
        help="Google AI Studio API key"
    )
    
    parser.add_argument(
        "--huggingface-key",
        type=str,
        default="",
        help="HuggingFace API key"
    )
    
    parser.add_argument(
        "--groq-key",
        type=str,
        default="",
        help="Groq API key"
    )
    
    args = parser.parse_args()
    
    # Create deployer
    deployer = OpenWebUIDeployer(args.domain, args.email)
    
    # Set API keys
    api_keys = {
        "openrouter": args.openrouter_key,
        "google_ai_studio": args.google_key,
        "huggingface": args.huggingface_key,
        "groq": args.groq_key
    }
    deployer.set_api_keys(api_keys)
    
    # Run deployment
    success = deployer.deploy(args.cert_method)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
