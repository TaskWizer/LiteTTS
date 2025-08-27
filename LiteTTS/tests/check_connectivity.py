#!/usr/bin/env python3
"""
Check connectivity between Docker containers and native services
"""

import requests
import socket
import subprocess
import sys

def check_network_connectivity():
    """Check basic network connectivity"""
    print("🌐 Network Connectivity Check")
    print("=" * 40)
    
    # Check if we can reach the TTS API
    tts_urls = [
        "http://localhost:8000",
        "http://127.0.0.1:8000", 
        "http://192.168.1.139:8000"
    ]
    
    for url in tts_urls:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            print(f"✅ {url}: Reachable (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {url}: Not reachable - {e}")
    
    # Check if port 8000 is listening
    print(f"\n🔌 Port Check")
    print("-" * 20)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('192.168.1.139', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Port 8000 is open and listening")
        else:
            print("❌ Port 8000 is not accessible")
    except Exception as e:
        print(f"❌ Port check failed: {e}")

def check_docker_status():
    """Check Docker container status"""
    print(f"\n🐳 Docker Status Check")
    print("-" * 25)
    
    try:
        # Check if Docker is running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running")
            
            # Look for OpenWebUI container
            if 'open-webui' in result.stdout.lower() or 'openwebui' in result.stdout.lower():
                print("✅ OpenWebUI container found")
            else:
                print("⚠️  OpenWebUI container not found in docker ps")
                
            print(f"\nRunning containers:")
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ Docker not running or not accessible")
            
    except FileNotFoundError:
        print("❌ Docker command not found")
    except Exception as e:
        print(f"❌ Docker check failed: {e}")

def suggest_solutions():
    """Suggest potential solutions"""
    print(f"\n💡 Potential Solutions")
    print("-" * 25)
    
    print("1. **Container Network Issue**:")
    print("   - If OpenWebUI is in Docker, it might not reach host services")
    print("   - Try using host network: docker run --network=host")
    print("   - Or use host.docker.internal instead of localhost")
    
    print("\n2. **Firewall/Port Issue**:")
    print("   - Check if port 8000 is blocked by firewall")
    print("   - Try: sudo ufw allow 8000")
    
    print("\n3. **Service Not Running**:")
    print("   - Make sure TTS API is running: uv run uvicorn app:app --host 0.0.0.0 --port 8000")
    print("   - Check server logs for startup errors")
    
    print("\n4. **IP Address Issue**:")
    print("   - Use actual IP (192.168.1.139) instead of localhost")
    print("   - Check if IP changed: ip addr show")

def main():
    check_network_connectivity()
    check_docker_status()
    suggest_solutions()
    
    print(f"\n🔍 Debug Commands to Try:")
    print("   curl http://192.168.1.139:8000/health")
    print("   curl http://192.168.1.139:8000/debug")
    print("   docker logs <openwebui-container-name>")

if __name__ == "__main__":
    main()