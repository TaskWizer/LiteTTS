#!/usr/bin/env python3
"""
Cloudflare DNS Integration Manager
Configure DNS settings and prepare infrastructure for Cloudflare integration with HTTPS enforcement
"""

import os
import sys
import json
import logging
import time
import socket
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DNSRecord:
    """DNS record configuration"""
    name: str
    record_type: str
    content: str
    ttl: int
    proxied: bool
    priority: Optional[int] = None
    comment: str = ""

@dataclass
class CloudflareZone:
    """Cloudflare zone configuration"""
    zone_name: str
    zone_id: str
    nameservers: List[str]
    status: str
    plan: str

@dataclass
class CloudflareConfiguration:
    """Cloudflare integration configuration"""
    api_token: str
    zone_name: str
    subdomain: str
    enable_proxy: bool
    enable_ssl: bool
    ssl_mode: str  # off, flexible, full, strict
    enable_hsts: bool
    enable_always_https: bool
    enable_automatic_https_rewrites: bool
    security_level: str  # off, essentially_off, low, medium, high, under_attack
    cache_level: str  # aggressive, basic, simplified
    development_mode: bool
    dns_records: List[DNSRecord]

class CloudflareDNSManager:
    """Cloudflare DNS integration manager"""
    
    def __init__(self):
        self.results_dir = Path("test_results/cloudflare_dns")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Cloudflare API base URL
        self.api_base = "https://api.cloudflare.com/client/v4"
        
        # Default configuration
        self.default_config = self._create_default_cloudflare_config()
        
    def _create_default_cloudflare_config(self) -> CloudflareConfiguration:
        """Create default Cloudflare configuration"""
        
        # Get local IP for DNS records
        local_ip = self._get_local_ip()
        
        # Default DNS records for TTS service
        dns_records = [
            DNSRecord(
                name="tts",
                record_type="A",
                content=local_ip,
                ttl=300,  # 5 minutes for development
                proxied=True,
                comment="Kokoro TTS API endpoint"
            ),
            DNSRecord(
                name="api",
                record_type="CNAME",
                content="tts",
                ttl=300,
                proxied=True,
                comment="API alias for TTS service"
            ),
            DNSRecord(
                name="www",
                record_type="CNAME",
                content="tts",
                ttl=300,
                proxied=True,
                comment="WWW redirect to TTS service"
            )
        ]
        
        return CloudflareConfiguration(
            api_token="",  # To be provided by user
            zone_name="example.com",  # To be configured by user
            subdomain="tts",
            enable_proxy=True,
            enable_ssl=True,
            ssl_mode="strict",
            enable_hsts=True,
            enable_always_https=True,
            enable_automatic_https_rewrites=True,
            security_level="medium",
            cache_level="basic",
            development_mode=False,
            dns_records=dns_records
        )
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to get local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def validate_api_token(self, api_token: str) -> Tuple[bool, str]:
        """Validate Cloudflare API token"""
        logger.info("Validating Cloudflare API token...")
        
        if not api_token:
            return False, "API token is required"
        
        try:
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base}/user/tokens/verify",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info("API token validation successful")
                    return True, "Valid API token"
                else:
                    return False, f"Token validation failed: {data.get('errors', [])}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Token validation error: {str(e)}"
    
    def get_zones(self, api_token: str) -> Tuple[bool, List[CloudflareZone]]:
        """Get Cloudflare zones"""
        logger.info("Retrieving Cloudflare zones...")
        
        try:
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base}/zones",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    zones = []
                    for zone_data in data.get("result", []):
                        zone = CloudflareZone(
                            zone_name=zone_data["name"],
                            zone_id=zone_data["id"],
                            nameservers=zone_data.get("name_servers", []),
                            status=zone_data.get("status", "unknown"),
                            plan=zone_data.get("plan", {}).get("name", "unknown")
                        )
                        zones.append(zone)
                    
                    logger.info(f"Retrieved {len(zones)} zones")
                    return True, zones
                else:
                    return False, []
            else:
                return False, []
                
        except Exception as e:
            logger.error(f"Error retrieving zones: {e}")
            return False, []
    
    def create_dns_records(self, config: CloudflareConfiguration, zone_id: str) -> Dict[str, Any]:
        """Create DNS records in Cloudflare"""
        logger.info("Creating DNS records...")
        
        results = {
            "successful_records": [],
            "failed_records": [],
            "total_records": len(config.dns_records)
        }
        
        headers = {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json"
        }
        
        for record in config.dns_records:
            try:
                # Construct full domain name
                if record.name == "@":
                    full_name = config.zone_name
                else:
                    full_name = f"{record.name}.{config.zone_name}"
                
                record_data = {
                    "type": record.record_type,
                    "name": full_name,
                    "content": record.content,
                    "ttl": record.ttl,
                    "proxied": record.proxied
                }
                
                if record.priority is not None:
                    record_data["priority"] = record.priority
                
                if record.comment:
                    record_data["comment"] = record.comment
                
                response = requests.post(
                    f"{self.api_base}/zones/{zone_id}/dns_records",
                    headers=headers,
                    json=record_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        results["successful_records"].append({
                            "name": full_name,
                            "type": record.record_type,
                            "content": record.content,
                            "record_id": data["result"]["id"]
                        })
                        logger.info(f"Created DNS record: {full_name} -> {record.content}")
                    else:
                        results["failed_records"].append({
                            "name": full_name,
                            "error": data.get("errors", [])
                        })
                else:
                    results["failed_records"].append({
                        "name": full_name,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                results["failed_records"].append({
                    "name": record.name,
                    "error": str(e)
                })
                logger.error(f"Failed to create DNS record {record.name}: {e}")
        
        return results
    
    def configure_ssl_settings(self, config: CloudflareConfiguration, zone_id: str) -> Dict[str, Any]:
        """Configure SSL settings in Cloudflare"""
        logger.info("Configuring SSL settings...")
        
        results = {
            "ssl_mode": False,
            "always_https": False,
            "hsts": False,
            "automatic_https_rewrites": False,
            "errors": []
        }
        
        headers = {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Configure SSL mode
            ssl_response = requests.patch(
                f"{self.api_base}/zones/{zone_id}/settings/ssl",
                headers=headers,
                json={"value": config.ssl_mode},
                timeout=10
            )
            
            if ssl_response.status_code == 200:
                data = ssl_response.json()
                results["ssl_mode"] = data.get("success", False)
                logger.info(f"SSL mode set to: {config.ssl_mode}")
            else:
                results["errors"].append(f"SSL mode configuration failed: {ssl_response.status_code}")
            
            # Configure Always HTTPS
            if config.enable_always_https:
                https_response = requests.patch(
                    f"{self.api_base}/zones/{zone_id}/settings/always_use_https",
                    headers=headers,
                    json={"value": "on"},
                    timeout=10
                )
                
                if https_response.status_code == 200:
                    data = https_response.json()
                    results["always_https"] = data.get("success", False)
                    logger.info("Always HTTPS enabled")
                else:
                    results["errors"].append(f"Always HTTPS configuration failed: {https_response.status_code}")
            
            # Configure Automatic HTTPS Rewrites
            if config.enable_automatic_https_rewrites:
                rewrites_response = requests.patch(
                    f"{self.api_base}/zones/{zone_id}/settings/automatic_https_rewrites",
                    headers=headers,
                    json={"value": "on"},
                    timeout=10
                )
                
                if rewrites_response.status_code == 200:
                    data = rewrites_response.json()
                    results["automatic_https_rewrites"] = data.get("success", False)
                    logger.info("Automatic HTTPS rewrites enabled")
                else:
                    results["errors"].append(f"HTTPS rewrites configuration failed: {rewrites_response.status_code}")
            
        except Exception as e:
            results["errors"].append(f"SSL configuration error: {str(e)}")
            logger.error(f"SSL configuration error: {e}")
        
        return results
    
    def configure_security_settings(self, config: CloudflareConfiguration, zone_id: str) -> Dict[str, Any]:
        """Configure security settings in Cloudflare"""
        logger.info("Configuring security settings...")
        
        results = {
            "security_level": False,
            "cache_level": False,
            "development_mode": False,
            "errors": []
        }
        
        headers = {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Configure security level
            security_response = requests.patch(
                f"{self.api_base}/zones/{zone_id}/settings/security_level",
                headers=headers,
                json={"value": config.security_level},
                timeout=10
            )
            
            if security_response.status_code == 200:
                data = security_response.json()
                results["security_level"] = data.get("success", False)
                logger.info(f"Security level set to: {config.security_level}")
            else:
                results["errors"].append(f"Security level configuration failed: {security_response.status_code}")
            
            # Configure cache level
            cache_response = requests.patch(
                f"{self.api_base}/zones/{zone_id}/settings/cache_level",
                headers=headers,
                json={"value": config.cache_level},
                timeout=10
            )
            
            if cache_response.status_code == 200:
                data = cache_response.json()
                results["cache_level"] = data.get("success", False)
                logger.info(f"Cache level set to: {config.cache_level}")
            else:
                results["errors"].append(f"Cache level configuration failed: {cache_response.status_code}")
            
            # Configure development mode
            dev_mode_value = "on" if config.development_mode else "off"
            dev_response = requests.patch(
                f"{self.api_base}/zones/{zone_id}/settings/development_mode",
                headers=headers,
                json={"value": dev_mode_value},
                timeout=10
            )
            
            if dev_response.status_code == 200:
                data = dev_response.json()
                results["development_mode"] = data.get("success", False)
                logger.info(f"Development mode: {dev_mode_value}")
            else:
                results["errors"].append(f"Development mode configuration failed: {dev_response.status_code}")
            
        except Exception as e:
            results["errors"].append(f"Security configuration error: {str(e)}")
            logger.error(f"Security configuration error: {e}")
        
        return results
    
    def generate_cloudflare_config_template(self) -> str:
        """Generate Cloudflare configuration template"""
        logger.info("Generating Cloudflare configuration template...")
        
        config_template = f"""# Cloudflare DNS Integration Configuration
# Copy this file to cloudflare_config.json and update with your values

{{
    "api_token": "YOUR_CLOUDFLARE_API_TOKEN_HERE",
    "zone_name": "yourdomain.com",
    "subdomain": "tts",
    "enable_proxy": true,
    "enable_ssl": true,
    "ssl_mode": "strict",
    "enable_hsts": true,
    "enable_always_https": true,
    "enable_automatic_https_rewrites": true,
    "security_level": "medium",
    "cache_level": "basic",
    "development_mode": false,
    "dns_records": [
        {{
            "name": "tts",
            "record_type": "A",
            "content": "{self._get_local_ip()}",
            "ttl": 300,
            "proxied": true,
            "comment": "Kokoro TTS API endpoint"
        }},
        {{
            "name": "api",
            "record_type": "CNAME",
            "content": "tts.yourdomain.com",
            "ttl": 300,
            "proxied": true,
            "comment": "API alias for TTS service"
        }}
    ]
}}

# Instructions:
# 1. Replace YOUR_CLOUDFLARE_API_TOKEN_HERE with your actual API token
# 2. Replace yourdomain.com with your actual domain name
# 3. Update the IP address in the A record to your server's public IP
# 4. Adjust DNS records as needed for your setup
# 5. Run the Cloudflare integration script with this configuration
"""
        
        # Save template
        template_file = self.results_dir / "cloudflare_config_template.json"
        with open(template_file, 'w') as f:
            f.write(config_template)
        
        logger.info(f"Configuration template saved: {template_file}")
        return config_template
    
    def generate_dns_verification_script(self, config: CloudflareConfiguration) -> str:
        """Generate DNS verification script"""
        logger.info("Generating DNS verification script...")
        
        verification_script = f"""#!/bin/bash
# Cloudflare DNS Verification Script
# Generated automatically - do not edit manually

set -e

echo "Starting Cloudflare DNS verification..."

DOMAIN="{config.zone_name}"
SUBDOMAIN="{config.subdomain}"
FULL_DOMAIN="$SUBDOMAIN.$DOMAIN"

echo "Verifying DNS records for $FULL_DOMAIN..."

# Check A record
echo "Checking A record..."
A_RECORD=$(dig +short A "$FULL_DOMAIN" @8.8.8.8)
if [ -n "$A_RECORD" ]; then
    echo "✅ A record found: $A_RECORD"
else
    echo "❌ A record not found"
fi

# Check CNAME records
echo "Checking CNAME records..."
for subdomain in api www; do
    CNAME_RECORD=$(dig +short CNAME "$subdomain.$DOMAIN" @8.8.8.8)
    if [ -n "$CNAME_RECORD" ]; then
        echo "✅ CNAME record found: $subdomain.$DOMAIN -> $CNAME_RECORD"
    else
        echo "⚠️  CNAME record not found: $subdomain.$DOMAIN"
    fi
done

# Check SSL certificate
echo "Checking SSL certificate..."
if openssl s_client -connect "$FULL_DOMAIN:443" -servername "$FULL_DOMAIN" </dev/null 2>/dev/null | openssl x509 -noout -text | grep -q "CN=$FULL_DOMAIN"; then
    echo "✅ SSL certificate is valid for $FULL_DOMAIN"
else
    echo "⚠️  SSL certificate issue for $FULL_DOMAIN"
fi

# Check HTTPS redirect
echo "Checking HTTPS redirect..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{{http_code}}" "http://$FULL_DOMAIN" || echo "000")
if [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
    echo "✅ HTTP to HTTPS redirect working (status: $HTTP_STATUS)"
else
    echo "⚠️  HTTP to HTTPS redirect not working (status: $HTTP_STATUS)"
fi

# Check Cloudflare proxy
echo "Checking Cloudflare proxy..."
CF_RAY=$(curl -s -I "https://$FULL_DOMAIN" | grep -i "cf-ray" || echo "")
if [ -n "$CF_RAY" ]; then
    echo "✅ Cloudflare proxy is active"
else
    echo "⚠️  Cloudflare proxy not detected"
fi

echo "DNS verification completed!"
"""
        
        # Save verification script
        script_file = self.results_dir / "verify_dns.sh"
        with open(script_file, 'w') as f:
            f.write(verification_script)
        os.chmod(script_file, 0o755)
        
        logger.info(f"DNS verification script saved: {script_file}")
        return verification_script

    def run_comprehensive_cloudflare_setup(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Run comprehensive Cloudflare DNS setup"""
        logger.info("Starting comprehensive Cloudflare DNS setup...")

        # Generate configuration template if no config provided
        if not config_file:
            self.generate_cloudflare_config_template()

            setup_results = {
                "success": False,
                "setup_timestamp": time.time(),
                "message": "Configuration template generated",
                "template_file": "cloudflare_config_template.json",
                "next_steps": [
                    "Update the generated configuration template with your Cloudflare API token",
                    "Set your domain name in the configuration",
                    "Update DNS record IP addresses",
                    "Run the setup again with the configuration file"
                ]
            }

            return setup_results

        # Load configuration
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)

            config = CloudflareConfiguration(**config_data)

        except Exception as e:
            return {
                "success": False,
                "error": f"Configuration loading failed: {str(e)}",
                "setup_timestamp": time.time()
            }

        # Validate API token
        token_valid, token_message = self.validate_api_token(config.api_token)
        if not token_valid:
            return {
                "success": False,
                "error": f"API token validation failed: {token_message}",
                "setup_timestamp": time.time()
            }

        # Get zones
        zones_success, zones = self.get_zones(config.api_token)
        if not zones_success:
            return {
                "success": False,
                "error": "Failed to retrieve Cloudflare zones",
                "setup_timestamp": time.time()
            }

        # Find target zone
        target_zone = None
        for zone in zones:
            if zone.zone_name == config.zone_name:
                target_zone = zone
                break

        if not target_zone:
            return {
                "success": False,
                "error": f"Zone '{config.zone_name}' not found in Cloudflare account",
                "available_zones": [zone.zone_name for zone in zones],
                "setup_timestamp": time.time()
            }

        # Create DNS records
        dns_results = self.create_dns_records(config, target_zone.zone_id)

        # Configure SSL settings
        ssl_results = self.configure_ssl_settings(config, target_zone.zone_id)

        # Configure security settings
        security_results = self.configure_security_settings(config, target_zone.zone_id)

        # Generate verification script
        verification_script = self.generate_dns_verification_script(config)

        # Compile results
        setup_results = {
            "success": True,
            "setup_timestamp": time.time(),
            "cloudflare_configuration": asdict(config),
            "zone_information": asdict(target_zone),
            "dns_results": dns_results,
            "ssl_results": ssl_results,
            "security_results": security_results,
            "generated_files": {
                "verification_script": "verify_dns.sh",
                "config_template": "cloudflare_config_template.json"
            },
            "setup_summary": self._generate_cloudflare_summary(dns_results, ssl_results, security_results),
            "next_steps": self._generate_cloudflare_next_steps(config, target_zone)
        }

        # Save complete configuration
        results_file = self.results_dir / f"cloudflare_setup_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(setup_results, f, indent=2, default=str)

        logger.info(f"Cloudflare setup completed. Results saved to: {results_file}")
        return setup_results

    def _generate_cloudflare_summary(self, dns_results: Dict[str, Any],
                                   ssl_results: Dict[str, Any],
                                   security_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cloudflare setup summary"""

        total_dns_records = dns_results["total_records"]
        successful_dns = len(dns_results["successful_records"])
        failed_dns = len(dns_results["failed_records"])

        ssl_features_enabled = sum(1 for key, value in ssl_results.items()
                                 if key != "errors" and value is True)
        ssl_total_features = len([key for key in ssl_results.keys() if key != "errors"])

        security_features_enabled = sum(1 for key, value in security_results.items()
                                      if key != "errors" and value is True)
        security_total_features = len([key for key in security_results.keys() if key != "errors"])

        summary = {
            "dns_records": {
                "total": total_dns_records,
                "successful": successful_dns,
                "failed": failed_dns,
                "success_rate": (successful_dns / total_dns_records * 100) if total_dns_records > 0 else 0
            },
            "ssl_configuration": {
                "features_enabled": ssl_features_enabled,
                "total_features": ssl_total_features,
                "success_rate": (ssl_features_enabled / ssl_total_features * 100) if ssl_total_features > 0 else 0,
                "errors": len(ssl_results.get("errors", []))
            },
            "security_configuration": {
                "features_enabled": security_features_enabled,
                "total_features": security_total_features,
                "success_rate": (security_features_enabled / security_total_features * 100) if security_total_features > 0 else 0,
                "errors": len(security_results.get("errors", []))
            },
            "overall_success_rate": (
                (successful_dns + ssl_features_enabled + security_features_enabled) /
                (total_dns_records + ssl_total_features + security_total_features) * 100
            ) if (total_dns_records + ssl_total_features + security_total_features) > 0 else 0
        }

        return summary

    def _generate_cloudflare_next_steps(self, config: CloudflareConfiguration,
                                      zone: CloudflareZone) -> List[str]:
        """Generate next steps for Cloudflare deployment"""
        next_steps = [
            "Run the DNS verification script to test configuration",
            "Update your application to use the new domain name",
            "Test HTTPS endpoints with the configured domain",
            "Verify SSL certificate is properly configured",
            "Test HTTP to HTTPS redirects",
            "Configure firewall rules for the new domain",
            "Update monitoring systems with new endpoints",
            "Test API functionality through Cloudflare proxy",
            "Configure rate limiting rules if needed",
            "Set up Cloudflare analytics and monitoring"
        ]

        # Add specific recommendations
        if config.development_mode:
            next_steps.append("Disable development mode for production deployment")

        if config.enable_proxy:
            next_steps.append("Verify Cloudflare proxy is working correctly")

        if zone.plan == "Free":
            next_steps.append("Consider upgrading Cloudflare plan for additional features")

        return next_steps

def main():
    """Main function to run Cloudflare DNS integration"""
    manager = CloudflareDNSManager()

    try:
        # Check if configuration file exists
        config_file = "cloudflare_config.json"
        if not Path(config_file).exists():
            print("Configuration file not found. Generating template...")
            results = manager.run_comprehensive_cloudflare_setup()
        else:
            print(f"Using configuration file: {config_file}")
            results = manager.run_comprehensive_cloudflare_setup(config_file)

        print("\n" + "="*80)
        print("CLOUDFLARE DNS INTEGRATION SUMMARY")
        print("="*80)

        if not results["success"]:
            print(f"❌ Setup failed: {results.get('error', 'Unknown error')}")
            if "next_steps" in results:
                print(f"\nNext Steps:")
                for i, step in enumerate(results["next_steps"], 1):
                    print(f"  {i}. {step}")
            return

        summary = results["setup_summary"]

        print(f"✅ Cloudflare setup completed successfully")
        print(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")

        print(f"\nDNS Records:")
        dns = summary["dns_records"]
        print(f"  Created: {dns['successful']}/{dns['total']} ({dns['success_rate']:.1f}%)")

        print(f"\nSSL Configuration:")
        ssl = summary["ssl_configuration"]
        print(f"  Features Enabled: {ssl['features_enabled']}/{ssl['total_features']} ({ssl['success_rate']:.1f}%)")
        print(f"  Errors: {ssl['errors']}")

        print(f"\nSecurity Configuration:")
        security = summary["security_configuration"]
        print(f"  Features Enabled: {security['features_enabled']}/{security['total_features']} ({security['success_rate']:.1f}%)")
        print(f"  Errors: {security['errors']}")

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
        logger.error(f"Cloudflare setup failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
