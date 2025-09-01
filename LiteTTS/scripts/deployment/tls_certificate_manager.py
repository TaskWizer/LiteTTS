#!/usr/bin/env python3
"""
TLS Certificate Manager
Implement self-signed TLS certificate generation and configuration for HTTPS enforcement
"""

import os
import sys
import json
import logging
import subprocess
import time
import socket
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TLSCertificate:
    """TLS certificate information"""
    cert_path: str
    key_path: str
    ca_cert_path: str
    common_name: str
    subject_alt_names: List[str]
    valid_from: str
    valid_until: str
    key_size: int
    algorithm: str
    fingerprint: str

@dataclass
class TLSConfiguration:
    """TLS configuration settings"""
    enable_https: bool
    force_https_redirect: bool
    cert_directory: str
    cert_filename: str
    key_filename: str
    ca_filename: str
    https_port: int
    http_port: int
    cert_validity_days: int
    key_size: int
    cipher_suites: List[str]
    protocols: List[str]
    hsts_enabled: bool
    hsts_max_age: int

class TLSCertificateManager:
    """TLS certificate generation and management system"""
    
    def __init__(self):
        self.results_dir = Path("test_results/tls_certificates")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Default certificate directory
        self.cert_dir = Path("certs")
        self.cert_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.default_config = self._create_default_tls_config()
        
    def _create_default_tls_config(self) -> TLSConfiguration:
        """Create default TLS configuration"""
        return TLSConfiguration(
            enable_https=True,
            force_https_redirect=True,
            cert_directory=str(self.cert_dir),
            cert_filename="kokoro-tts.crt",
            key_filename="kokoro-tts.key",
            ca_filename="kokoro-ca.crt",
            https_port=8443,
            http_port=8354,
            cert_validity_days=365,
            key_size=2048,
            cipher_suites=[
                "ECDHE-RSA-AES256-GCM-SHA384",
                "ECDHE-RSA-AES128-GCM-SHA256",
                "ECDHE-RSA-AES256-SHA384",
                "ECDHE-RSA-AES128-SHA256"
            ],
            protocols=["TLSv1.2", "TLSv1.3"],
            hsts_enabled=True,
            hsts_max_age=31536000  # 1 year
        )
    
    def check_openssl_availability(self) -> bool:
        """Check if OpenSSL is available"""
        try:
            result = subprocess.run(['openssl', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"OpenSSL available: {result.stdout.strip()}")
                return True
            else:
                logger.error("OpenSSL not available")
                return False
        except Exception as e:
            logger.error(f"Error checking OpenSSL: {e}")
            return False
    
    def get_system_hostnames(self) -> List[str]:
        """Get system hostnames for certificate SAN"""
        hostnames = []
        
        # Add localhost variants
        hostnames.extend(["localhost", "127.0.0.1", "::1"])
        
        # Add system hostname
        try:
            hostname = socket.gethostname()
            hostnames.append(hostname)
            
            # Add FQDN if different
            fqdn = socket.getfqdn()
            if fqdn != hostname:
                hostnames.append(fqdn)
        except Exception as e:
            logger.warning(f"Could not get system hostname: {e}")
        
        # Add local IP addresses
        try:
            # Get local IP by connecting to a remote address
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                if local_ip not in hostnames:
                    hostnames.append(local_ip)
        except Exception as e:
            logger.warning(f"Could not get local IP: {e}")
        
        # Add common development hostnames
        dev_hostnames = ["kokoro-tts", "kokoro-tts.local", "tts.local"]
        for hostname in dev_hostnames:
            if hostname not in hostnames:
                hostnames.append(hostname)
        
        return hostnames
    
    def generate_ca_certificate(self, config: TLSConfiguration) -> Tuple[bool, str]:
        """Generate Certificate Authority certificate"""
        logger.info("Generating CA certificate...")
        
        ca_key_path = Path(config.cert_directory) / "ca.key"
        ca_cert_path = Path(config.cert_directory) / config.ca_filename
        
        try:
            # Generate CA private key
            ca_key_cmd = [
                'openssl', 'genrsa',
                '-out', str(ca_key_path),
                str(config.key_size)
            ]
            
            result = subprocess.run(ca_key_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, f"CA key generation failed: {result.stderr}"
            
            # Generate CA certificate
            ca_cert_cmd = [
                'openssl', 'req', '-new', '-x509',
                '-key', str(ca_key_path),
                '-out', str(ca_cert_path),
                '-days', str(config.cert_validity_days),
                '-subj', '/C=US/ST=Local/L=Local/O=Kokoro TTS/OU=Development/CN=Kokoro TTS CA'
            ]
            
            result = subprocess.run(ca_cert_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, f"CA certificate generation failed: {result.stderr}"
            
            # Set appropriate permissions
            os.chmod(ca_key_path, 0o600)
            os.chmod(ca_cert_path, 0o644)
            
            logger.info(f"CA certificate generated: {ca_cert_path}")
            return True, str(ca_cert_path)
            
        except Exception as e:
            return False, f"CA generation error: {str(e)}"
    
    def generate_server_certificate(self, config: TLSConfiguration, 
                                  common_name: str = "localhost") -> Tuple[bool, TLSCertificate]:
        """Generate server certificate signed by CA"""
        logger.info(f"Generating server certificate for {common_name}...")
        
        cert_path = Path(config.cert_directory) / config.cert_filename
        key_path = Path(config.cert_directory) / config.key_filename
        ca_cert_path = Path(config.cert_directory) / config.ca_filename
        ca_key_path = Path(config.cert_directory) / "ca.key"
        csr_path = Path(config.cert_directory) / "server.csr"
        
        try:
            # Get subject alternative names
            san_list = self.get_system_hostnames()
            if common_name not in san_list:
                san_list.insert(0, common_name)
            
            # Generate server private key
            key_cmd = [
                'openssl', 'genrsa',
                '-out', str(key_path),
                str(config.key_size)
            ]
            
            result = subprocess.run(key_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, None
            
            # Create certificate signing request
            csr_cmd = [
                'openssl', 'req', '-new',
                '-key', str(key_path),
                '-out', str(csr_path),
                '-subj', f'/C=US/ST=Local/L=Local/O=Kokoro TTS/OU=Server/CN={common_name}'
            ]
            
            result = subprocess.run(csr_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, None
            
            # Create SAN extension file
            san_ext_path = Path(config.cert_directory) / "san.ext"
            san_entries = []
            for i, hostname in enumerate(san_list):
                if hostname.replace('.', '').replace(':', '').isdigit() or ':' in hostname:
                    san_entries.append(f"IP.{i+1}={hostname}")
                else:
                    san_entries.append(f"DNS.{i+1}={hostname}")
            
            san_config = f"""[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
{chr(10).join(san_entries)}
"""
            
            with open(san_ext_path, 'w') as f:
                f.write(san_config)
            
            # Sign certificate with CA
            sign_cmd = [
                'openssl', 'x509', '-req',
                '-in', str(csr_path),
                '-CA', str(ca_cert_path),
                '-CAkey', str(ca_key_path),
                '-CAcreateserial',
                '-out', str(cert_path),
                '-days', str(config.cert_validity_days),
                '-extensions', 'v3_req',
                '-extfile', str(san_ext_path)
            ]
            
            result = subprocess.run(sign_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, None
            
            # Get certificate information
            cert_info = self._get_certificate_info(cert_path)
            
            # Set appropriate permissions
            os.chmod(key_path, 0o600)
            os.chmod(cert_path, 0o644)
            
            # Clean up temporary files
            csr_path.unlink(missing_ok=True)
            san_ext_path.unlink(missing_ok=True)
            
            certificate = TLSCertificate(
                cert_path=str(cert_path),
                key_path=str(key_path),
                ca_cert_path=str(ca_cert_path),
                common_name=common_name,
                subject_alt_names=san_list,
                valid_from=cert_info.get("valid_from", ""),
                valid_until=cert_info.get("valid_until", ""),
                key_size=config.key_size,
                algorithm="RSA",
                fingerprint=cert_info.get("fingerprint", "")
            )
            
            logger.info(f"Server certificate generated: {cert_path}")
            return True, certificate
            
        except Exception as e:
            logger.error(f"Server certificate generation error: {e}")
            return False, None
    
    def _get_certificate_info(self, cert_path: Path) -> Dict[str, str]:
        """Get certificate information using OpenSSL"""
        info = {}
        
        try:
            # Get certificate dates
            dates_cmd = ['openssl', 'x509', '-in', str(cert_path), '-noout', '-dates']
            result = subprocess.run(dates_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('notBefore='):
                        info['valid_from'] = line.split('=', 1)[1]
                    elif line.startswith('notAfter='):
                        info['valid_until'] = line.split('=', 1)[1]
            
            # Get certificate fingerprint
            fingerprint_cmd = ['openssl', 'x509', '-in', str(cert_path), '-noout', '-fingerprint', '-sha256']
            result = subprocess.run(fingerprint_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                fingerprint_line = result.stdout.strip()
                if '=' in fingerprint_line:
                    info['fingerprint'] = fingerprint_line.split('=', 1)[1]
            
        except Exception as e:
            logger.warning(f"Could not get certificate info: {e}")
        
        return info
    
    def verify_certificate(self, certificate: TLSCertificate) -> Dict[str, Any]:
        """Verify certificate validity and configuration"""
        logger.info("Verifying certificate...")
        
        verification_results = {
            "certificate_exists": False,
            "key_exists": False,
            "ca_exists": False,
            "certificate_valid": False,
            "key_matches_cert": False,
            "san_configured": False,
            "expiry_check": False,
            "permissions_correct": False,
            "issues": []
        }
        
        try:
            # Check file existence
            cert_path = Path(certificate.cert_path)
            key_path = Path(certificate.key_path)
            ca_path = Path(certificate.ca_cert_path)
            
            verification_results["certificate_exists"] = cert_path.exists()
            verification_results["key_exists"] = key_path.exists()
            verification_results["ca_exists"] = ca_path.exists()
            
            if not verification_results["certificate_exists"]:
                verification_results["issues"].append("Certificate file not found")
            
            if not verification_results["key_exists"]:
                verification_results["issues"].append("Private key file not found")
            
            if not verification_results["ca_exists"]:
                verification_results["issues"].append("CA certificate file not found")
            
            # Verify certificate validity
            if cert_path.exists():
                verify_cmd = ['openssl', 'x509', '-in', str(cert_path), '-noout', '-text']
                result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=10)
                verification_results["certificate_valid"] = result.returncode == 0
                
                if not verification_results["certificate_valid"]:
                    verification_results["issues"].append("Certificate is not valid")
            
            # Check key-certificate match
            if cert_path.exists() and key_path.exists():
                cert_modulus_cmd = ['openssl', 'x509', '-in', str(cert_path), '-noout', '-modulus']
                key_modulus_cmd = ['openssl', 'rsa', '-in', str(key_path), '-noout', '-modulus']
                
                cert_result = subprocess.run(cert_modulus_cmd, capture_output=True, text=True, timeout=10)
                key_result = subprocess.run(key_modulus_cmd, capture_output=True, text=True, timeout=10)
                
                if cert_result.returncode == 0 and key_result.returncode == 0:
                    verification_results["key_matches_cert"] = cert_result.stdout == key_result.stdout
                    
                    if not verification_results["key_matches_cert"]:
                        verification_results["issues"].append("Private key does not match certificate")
            
            # Check SAN configuration
            if cert_path.exists():
                san_cmd = ['openssl', 'x509', '-in', str(cert_path), '-noout', '-text']
                result = subprocess.run(san_cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    verification_results["san_configured"] = "Subject Alternative Name" in result.stdout
                    
                    if not verification_results["san_configured"]:
                        verification_results["issues"].append("Subject Alternative Names not configured")
            
            # Check expiry
            if cert_path.exists():
                expiry_cmd = ['openssl', 'x509', '-in', str(cert_path), '-noout', '-checkend', '2592000']  # 30 days
                result = subprocess.run(expiry_cmd, capture_output=True, text=True, timeout=10)
                verification_results["expiry_check"] = result.returncode == 0
                
                if not verification_results["expiry_check"]:
                    verification_results["issues"].append("Certificate expires within 30 days")
            
            # Check file permissions
            if cert_path.exists() and key_path.exists():
                cert_stat = cert_path.stat()
                key_stat = key_path.stat()
                
                cert_perms = oct(cert_stat.st_mode)[-3:]
                key_perms = oct(key_stat.st_mode)[-3:]
                
                verification_results["permissions_correct"] = (cert_perms == "644" and key_perms == "600")
                
                if not verification_results["permissions_correct"]:
                    verification_results["issues"].append(f"Incorrect permissions: cert={cert_perms}, key={key_perms}")
            
        except Exception as e:
            verification_results["issues"].append(f"Verification error: {str(e)}")
        
        return verification_results

    def generate_nginx_ssl_config(self, config: TLSConfiguration, certificate: TLSCertificate) -> str:
        """Generate Nginx SSL configuration"""
        logger.info("Generating Nginx SSL configuration...")

        nginx_config = f"""# Kokoro TTS HTTPS Configuration
server {{
    listen {config.https_port} ssl http2;
    server_name {' '.join(certificate.subject_alt_names[:5])};  # First 5 SANs

    # SSL Certificate Configuration
    ssl_certificate {certificate.cert_path};
    ssl_certificate_key {certificate.key_path};
    ssl_trusted_certificate {certificate.ca_cert_path};

    # SSL Security Configuration
    ssl_protocols {' '.join(config.protocols)};
    ssl_ciphers '{':'.join(config.cipher_suites)}';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # Security Headers
    add_header Strict-Transport-Security "max-age={config.hsts_max_age}; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Proxy to Kokoro TTS
    location / {{
        proxy_pass http://127.0.0.1:{config.http_port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
}}

# HTTP to HTTPS redirect
server {{
    listen {config.http_port};
    server_name {' '.join(certificate.subject_alt_names[:5])};
    return 301 https://$host:{config.https_port}$request_uri;
}}
"""

        # Save configuration
        nginx_config_file = self.results_dir / "nginx_ssl.conf"
        with open(nginx_config_file, 'w') as f:
            f.write(nginx_config)

        logger.info(f"Nginx SSL configuration saved: {nginx_config_file}")
        return nginx_config

    def generate_docker_ssl_config(self, config: TLSConfiguration, certificate: TLSCertificate) -> str:
        """Generate Docker Compose SSL configuration"""
        logger.info("Generating Docker SSL configuration...")

        docker_config = f"""version: '3.8'

services:
  kokoro-tts-ssl:
    build: .
    container_name: kokoro-tts-ssl
    restart: unless-stopped
    ports:
      - "{config.https_port}:{config.https_port}"
      - "{config.http_port}:{config.http_port}"
    volumes:
      - ./certs:/app/certs:ro
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - ENABLE_HTTPS=true
      - HTTPS_PORT={config.https_port}
      - HTTP_PORT={config.http_port}
      - SSL_CERT_PATH=/app/certs/{Path(certificate.cert_path).name}
      - SSL_KEY_PATH=/app/certs/{Path(certificate.key_path).name}
      - FORCE_HTTPS_REDIRECT={str(config.force_https_redirect).lower()}
    healthcheck:
      test: ["CMD", "curl", "-f", "-k", "https://localhost:{config.https_port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    networks:
      - kokoro-ssl-network

  nginx-ssl-proxy:
    image: nginx:alpine
    container_name: kokoro-nginx-ssl
    restart: unless-stopped
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./certs:/etc/nginx/certs:ro
      - ./nginx_ssl.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - kokoro-tts-ssl
    networks:
      - kokoro-ssl-network

networks:
  kokoro-ssl-network:
    driver: bridge
"""

        # Save configuration
        docker_config_file = self.results_dir / "docker-compose-ssl.yml"
        with open(docker_config_file, 'w') as f:
            f.write(docker_config)

        logger.info(f"Docker SSL configuration saved: {docker_config_file}")
        return docker_config

    def generate_ssl_test_script(self, config: TLSConfiguration, certificate: TLSCertificate) -> str:
        """Generate SSL testing script"""
        logger.info("Generating SSL test script...")

        test_script = f"""#!/bin/bash
# Kokoro TTS SSL Test Script
# Generated automatically - do not edit manually

set -e

echo "Starting SSL/TLS configuration tests..."

# Test certificate validity
echo "Testing certificate validity..."
openssl x509 -in {certificate.cert_path} -noout -text
if [ $? -eq 0 ]; then
    echo "✅ Certificate is valid"
else
    echo "❌ Certificate is invalid"
    exit 1
fi

# Test private key
echo "Testing private key..."
openssl rsa -in {certificate.key_path} -check -noout
if [ $? -eq 0 ]; then
    echo "✅ Private key is valid"
else
    echo "❌ Private key is invalid"
    exit 1
fi

# Test certificate-key match
echo "Testing certificate-key match..."
CERT_MODULUS=$(openssl x509 -in {certificate.cert_path} -noout -modulus | openssl md5)
KEY_MODULUS=$(openssl rsa -in {certificate.key_path} -noout -modulus | openssl md5)

if [ "$CERT_MODULUS" = "$KEY_MODULUS" ]; then
    echo "✅ Certificate and key match"
else
    echo "❌ Certificate and key do not match"
    exit 1
fi

# Test certificate expiry
echo "Testing certificate expiry..."
openssl x509 -in {certificate.cert_path} -noout -checkend 2592000  # 30 days
if [ $? -eq 0 ]; then
    echo "✅ Certificate is not expiring soon"
else
    echo "⚠️  Certificate expires within 30 days"
fi

# Test SSL connection (if server is running)
echo "Testing SSL connection..."
if curl -k -f --connect-timeout 5 https://localhost:{config.https_port}/health >/dev/null 2>&1; then
    echo "✅ HTTPS connection successful"
else
    echo "⚠️  HTTPS connection failed (server may not be running)"
fi

# Test HTTP redirect (if enabled)
if [ "{str(config.force_https_redirect).lower()}" = "true" ]; then
    echo "Testing HTTP to HTTPS redirect..."
    REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{{http_code}}" http://localhost:{config.http_port}/health || echo "000")
    if [ "$REDIRECT_STATUS" = "301" ] || [ "$REDIRECT_STATUS" = "302" ]; then
        echo "✅ HTTP to HTTPS redirect working"
    else
        echo "⚠️  HTTP to HTTPS redirect not working (status: $REDIRECT_STATUS)"
    fi
fi

# Test SSL configuration
echo "Testing SSL configuration..."
if command -v nmap >/dev/null 2>&1; then
    nmap --script ssl-enum-ciphers -p {config.https_port} localhost
else
    echo "⚠️  nmap not available for SSL cipher testing"
fi

echo "SSL/TLS tests completed!"
"""

        # Save test script
        test_script_file = self.results_dir / "test_ssl.sh"
        with open(test_script_file, 'w') as f:
            f.write(test_script)
        os.chmod(test_script_file, 0o755)

        logger.info(f"SSL test script saved: {test_script_file}")
        return test_script

    def run_comprehensive_tls_setup(self, common_name: str = "localhost") -> Dict[str, Any]:
        """Run comprehensive TLS certificate setup"""
        logger.info("Starting comprehensive TLS certificate setup...")

        # Check OpenSSL availability
        if not self.check_openssl_availability():
            return {
                "success": False,
                "error": "OpenSSL not available",
                "setup_timestamp": time.time()
            }

        config = self.default_config

        # Generate CA certificate
        ca_success, ca_result = self.generate_ca_certificate(config)
        if not ca_success:
            return {
                "success": False,
                "error": f"CA generation failed: {ca_result}",
                "setup_timestamp": time.time()
            }

        # Generate server certificate
        cert_success, certificate = self.generate_server_certificate(config, common_name)
        if not cert_success:
            return {
                "success": False,
                "error": "Server certificate generation failed",
                "setup_timestamp": time.time()
            }

        # Verify certificate
        verification_results = self.verify_certificate(certificate)

        # Generate configurations
        nginx_config = self.generate_nginx_ssl_config(config, certificate)
        docker_config = self.generate_docker_ssl_config(config, certificate)
        test_script = self.generate_ssl_test_script(config, certificate)

        # Compile results
        setup_results = {
            "success": True,
            "setup_timestamp": time.time(),
            "tls_configuration": asdict(config),
            "certificate_info": asdict(certificate),
            "verification_results": verification_results,
            "generated_files": {
                "nginx_config": "nginx_ssl.conf",
                "docker_config": "docker-compose-ssl.yml",
                "test_script": "test_ssl.sh"
            },
            "setup_summary": self._generate_tls_summary(config, certificate, verification_results),
            "next_steps": self._generate_tls_next_steps(config, certificate)
        }

        # Save complete configuration
        config_file = self.results_dir / f"tls_setup_results_{int(time.time())}.json"
        with open(config_file, 'w') as f:
            json.dump(setup_results, f, indent=2, default=str)

        logger.info(f"TLS setup completed. Results saved to: {config_file}")
        return setup_results

    def _generate_tls_summary(self, config: TLSConfiguration,
                             certificate: TLSCertificate,
                             verification: Dict[str, Any]) -> Dict[str, Any]:
        """Generate TLS setup summary"""
        verification_score = sum(1 for key, value in verification.items()
                               if key != "issues" and value is True)
        total_checks = len([key for key in verification.keys() if key != "issues"])

        summary = {
            "https_enabled": config.enable_https,
            "https_port": config.https_port,
            "certificate_validity_days": config.cert_validity_days,
            "subject_alt_names_count": len(certificate.subject_alt_names),
            "verification_score": f"{verification_score}/{total_checks}",
            "verification_percentage": (verification_score / total_checks * 100) if total_checks > 0 else 0,
            "issues_found": len(verification["issues"]),
            "security_features": {
                "hsts_enabled": config.hsts_enabled,
                "force_https_redirect": config.force_https_redirect,
                "modern_ciphers": len(config.cipher_suites) > 0,
                "tls_1_3_support": "TLSv1.3" in config.protocols
            }
        }

        return summary

    def _generate_tls_next_steps(self, config: TLSConfiguration,
                                certificate: TLSCertificate) -> List[str]:
        """Generate next steps for TLS deployment"""
        next_steps = [
            "Review generated SSL certificates and configuration files",
            "Test SSL configuration using the generated test script",
            "Update application to use HTTPS endpoints",
            "Configure reverse proxy (Nginx) for SSL termination",
            "Test certificate validation with external tools",
            "Set up certificate renewal process for production",
            "Configure firewall rules for HTTPS traffic",
            "Update DNS records to point to HTTPS endpoints",
            "Test SSL/TLS security with online tools (SSL Labs)",
            "Document SSL certificate management procedures"
        ]

        # Add specific recommendations
        if config.force_https_redirect:
            next_steps.append("Verify HTTP to HTTPS redirect is working correctly")

        if config.hsts_enabled:
            next_steps.append("Test HSTS header configuration in browsers")

        if len(certificate.subject_alt_names) > 5:
            next_steps.append("Consider reducing Subject Alternative Names for better compatibility")

        return next_steps

def main():
    """Main function to run TLS certificate setup"""
    manager = TLSCertificateManager()

    try:
        # Run comprehensive TLS setup
        results = manager.run_comprehensive_tls_setup()

        print("\n" + "="*80)
        print("TLS CERTIFICATE SETUP SUMMARY")
        print("="*80)

        if not results["success"]:
            print(f"❌ Setup failed: {results.get('error', 'Unknown error')}")
            return

        config = results["tls_configuration"]
        cert_info = results["certificate_info"]
        summary = results["setup_summary"]
        verification = results["verification_results"]

        print(f"✅ TLS setup completed successfully")
        print(f"HTTPS Port: {config['https_port']}")
        print(f"Certificate Validity: {config['cert_validity_days']} days")
        print(f"Common Name: {cert_info['common_name']}")
        print(f"Subject Alt Names: {len(cert_info['subject_alt_names'])}")

        print(f"\nVerification Results:")
        print(f"  Score: {summary['verification_score']} ({summary['verification_percentage']:.1f}%)")
        print(f"  Issues Found: {summary['issues_found']}")

        if verification["issues"]:
            print(f"\nIssues:")
            for issue in verification["issues"]:
                print(f"  ⚠️  {issue}")

        print(f"\nSecurity Features:")
        security = summary["security_features"]
        print(f"  HSTS Enabled: {'✅' if security['hsts_enabled'] else '❌'}")
        print(f"  HTTPS Redirect: {'✅' if security['force_https_redirect'] else '❌'}")
        print(f"  Modern Ciphers: {'✅' if security['modern_ciphers'] else '❌'}")
        print(f"  TLS 1.3 Support: {'✅' if security['tls_1_3_support'] else '❌'}")

        print(f"\nGenerated Files:")
        for file_type, filename in results["generated_files"].items():
            print(f"  {file_type}: {filename}")

        print(f"\nNext Steps:")
        for i, step in enumerate(results["next_steps"][:5], 1):
            print(f"  {i}. {step}")

        if len(results["next_steps"]) > 5:
            print(f"  ... and {len(results['next_steps']) - 5} more steps")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"TLS setup failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
