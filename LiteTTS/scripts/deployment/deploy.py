#!/usr/bin/env python3
"""
Deployment automation script for Kokoro ONNX TTS API
Handles model downloading, configuration validation, and service deployment
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List
import requests
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """Manages deployment of Kokoro ONNX TTS API"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.config_file = self.project_root / "config.json"
        self.models_dir = self.project_root / "kokoro" / "models"
        self.voices_dir = self.project_root / "kokoro" / "voices"
        
    def validate_environment(self) -> bool:
        """Validate deployment environment"""
        logger.info("🔍 Validating deployment environment...")
        
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check required directories
        required_dirs = [self.models_dir, self.voices_dir]
        for dir_path in required_dirs:
            if not dir_path.exists():
                logger.info(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
        
        # Check configuration file
        if not self.config_file.exists():
            issues.append(f"Configuration file not found: {self.config_file}")
        else:
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.info("✅ Configuration file valid")
            except Exception as e:
                issues.append(f"Invalid configuration file: {e}")
        
        # Check disk space (need at least 1GB for models)
        try:
            import shutil
            free_space = shutil.disk_usage(self.project_root).free
            free_gb = free_space / (1024**3)
            if free_gb < 1:
                issues.append(f"Insufficient disk space: {free_gb:.1f}GB available, need at least 1GB")
            else:
                logger.info(f"✅ Disk space OK: {free_gb:.1f}GB available")
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
        
        if issues:
            logger.error("❌ Environment validation failed:")
            for issue in issues:
                logger.error(f"  • {issue}")
            return False
        
        logger.info("✅ Environment validation passed")
        return True
    
    def install_dependencies(self, use_uv: bool = True) -> bool:
        """Install Python dependencies"""
        logger.info("📦 Installing dependencies...")
        
        try:
            if use_uv and self._check_uv_available():
                cmd = ["uv", "sync", "--no-dev"]
                logger.info("Using uv for dependency installation")
            else:
                cmd = ["pip", "install", "-r", "REQUIREMENTS.txt"]
                logger.info("Using pip for dependency installation")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            return False
    
    def _check_uv_available(self) -> bool:
        """Check if uv is available"""
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def download_models(self, force: bool = False) -> bool:
        """Download required model files"""
        logger.info("🔄 Checking model files...")
        
        # Check if models already exist
        model_files = list(self.models_dir.glob("*.onnx"))
        if model_files and not force:
            logger.info(f"✅ Found {len(model_files)} model files, skipping download")
            return True
        
        try:
            # Import the downloader
            sys.path.insert(0, str(self.project_root))
            from LiteTTS.downloader import ensure_model_files
            
            logger.info("📥 Downloading model files...")
            success = ensure_model_files()
            
            if success:
                logger.info("✅ Model files downloaded successfully")
                return True
            else:
                logger.error("❌ Failed to download model files")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error downloading models: {e}")
            return False
    
    def download_voices(self, voices: List[str] = None, force: bool = False) -> bool:
        """Download voice files"""
        logger.info("🎤 Checking voice files...")
        
        # Default voices to download
        if voices is None:
            voices = ["af_heart", "am_puck"]
        
        # Check if voices already exist
        voice_files = list(self.voices_dir.glob("*.bin"))
        if len(voice_files) >= len(voices) and not force:
            logger.info(f"✅ Found {len(voice_files)} voice files, skipping download")
            return True
        
        try:
            # Import voice management
            sys.path.insert(0, str(self.project_root))
            from LiteTTS.voice import get_voice_manager
            
            voice_manager = get_voice_manager()
            if not voice_manager:
                logger.warning("⚠️ Voice manager not available, skipping voice download")
                return True
            
            logger.info(f"📥 Downloading voices: {voices}")
            success_count = 0
            
            for voice_name in voices:
                try:
                    if voice_manager.downloader.download_voice(voice_name):
                        success_count += 1
                        logger.info(f"✅ Downloaded voice: {voice_name}")
                    else:
                        logger.warning(f"⚠️ Failed to download voice: {voice_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Error downloading voice {voice_name}: {e}")
            
            logger.info(f"✅ Downloaded {success_count}/{len(voices)} voices")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error downloading voices: {e}")
            return False
    
    def validate_deployment(self, host: str = "localhost", port: int = 8354) -> bool:
        """Validate deployment by testing the API"""
        logger.info("🧪 Validating deployment...")
        
        base_url = f"http://{host}:{port}"
        
        # Wait for service to start
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{base_url}/", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Service is responding")
                    break
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    logger.info(f"Waiting for service... ({attempt + 1}/{max_attempts})")
                    time.sleep(2)
                else:
                    logger.error("❌ Service failed to start within timeout")
                    return False
        
        # Test endpoints
        tests = [
            ("Health Check", f"{base_url}/v1/health"),
            ("Voices List", f"{base_url}/v1/voices"),
            ("Root Endpoint", f"{base_url}/")
        ]
        
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ {test_name}: OK")
                else:
                    logger.warning(f"⚠️ {test_name}: HTTP {response.status_code}")
            except Exception as e:
                logger.error(f"❌ {test_name}: {e}")
                return False
        
        # Test TTS endpoint
        try:
            tts_payload = {
                "input": "Hello, deployment test!",
                "voice": "af_heart",
                "response_format": "mp3"
            }
            
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                json=tts_payload,
                timeout=30
            )
            
            if response.status_code == 200 and len(response.content) > 0:
                logger.info("✅ TTS Endpoint: OK")
            else:
                logger.warning(f"⚠️ TTS Endpoint: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ TTS Endpoint: {e}")
            return False
        
        logger.info("✅ Deployment validation completed successfully")
        return True
    
    def create_systemd_service(self, user: str = None, port: int = 8080) -> bool:
        """Create systemd service file"""
        logger.info("🔧 Creating systemd service...")
        
        if user is None:
            user = os.getenv("USER", "kokoro")
        
        service_content = f"""[Unit]
Description=Kokoro ONNX TTS API Service
After=network.target
Wants=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/.venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH={self.project_root}
ExecStart={sys.executable} LiteTTS/scripts/start_production.py --port {port}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kokoro-tts

# Performance optimizations
Environment=OMP_NUM_THREADS=4
Environment=ONNX_DISABLE_SPARSE_TENSORS=1
Environment=ENVIRONMENT=production

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths={self.project_root}/LiteTTS/cache
ReadWritePaths={self.project_root}/LiteTTS/models
ReadWritePaths={self.project_root}/LiteTTS/voices

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/tmp/kokoro-tts.service")
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            logger.info(f"✅ Service file created: {service_file}")
            logger.info("To install the service, run:")
            logger.info(f"  sudo cp {service_file} /etc/systemd/system/")
            logger.info("  sudo systemctl daemon-reload")
            logger.info("  sudo systemctl enable kokoro-tts")
            logger.info("  sudo systemctl start kokoro-tts")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create service file: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Deploy Kokoro ONNX TTS API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full deployment
  python LiteTTS/scripts/deploy.py --full

  # Just download models and voices
  python LiteTTS/scripts/deploy.py --models --voices

  # Deploy and validate
  python LiteTTS/scripts/deploy.py --full --validate

  # Create systemd service
  python LiteTTS/scripts/deploy.py --systemd --port 9001
        """
    )
    
    parser.add_argument("--full", action="store_true", help="Full deployment (models, voices, dependencies)")
    parser.add_argument("--models", action="store_true", help="Download model files")
    parser.add_argument("--voices", action="store_true", help="Download voice files")
    parser.add_argument("--deps", action="store_true", help="Install dependencies")
    parser.add_argument("--validate", action="store_true", help="Validate deployment")
    parser.add_argument("--systemd", action="store_true", help="Create systemd service file")
    parser.add_argument("--force", action="store_true", help="Force re-download of existing files")
    parser.add_argument("--port", type=int, default=8354, help="Service port (default: 8354)")
    parser.add_argument("--host", default="localhost", help="Service host for validation")
    parser.add_argument("--no-uv", action="store_true", help="Don't use uv, use pip instead")
    
    args = parser.parse_args()
    
    # If no specific actions, show help
    if not any([args.full, args.models, args.voices, args.deps, args.validate, args.systemd]):
        parser.print_help()
        return
    
    logger.info("🚀 Kokoro ONNX TTS API Deployment")
    logger.info("=" * 50)
    
    deployer = DeploymentManager()
    
    # Validate environment
    if not deployer.validate_environment():
        logger.error("❌ Environment validation failed")
        sys.exit(1)
    
    success = True
    
    # Install dependencies
    if args.full or args.deps:
        if not deployer.install_dependencies(use_uv=not args.no_uv):
            success = False
    
    # Download models
    if args.full or args.models:
        if not deployer.download_models(force=args.force):
            success = False
    
    # Download voices
    if args.full or args.voices:
        if not deployer.download_voices(force=args.force):
            success = False
    
    # Create systemd service
    if args.systemd:
        if not deployer.create_systemd_service(port=args.port):
            success = False
    
    # Validate deployment
    if args.validate:
        if not deployer.validate_deployment(host=args.host, port=args.port):
            success = False
    
    if success:
        logger.info("🎉 Deployment completed successfully!")
        logger.info(f"🌐 Service should be available at: http://{args.host}:{args.port}")
        logger.info(f"📊 Dashboard: http://{args.host}:{args.port}/dashboard")
        logger.info(f"📚 API docs: http://{args.host}:{args.port}/docs")
    else:
        logger.error("❌ Deployment completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()