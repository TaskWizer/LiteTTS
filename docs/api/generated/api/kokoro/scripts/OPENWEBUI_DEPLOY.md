# openwebui_deploy.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


OpenWebUI Deployment Script (Python version)
Cross-platform deployment utility for OpenWebUI with TLS and multiple API providers
Replaces openwebui-deploy.sh with better error handling and cross-platform support


## Class: OpenWebUIDeployer

OpenWebUI deployment utility

### __init__()

### create_directories()

Create necessary directories

### set_api_keys()

Set API keys

### generate_docker_compose()

Generate docker-compose.yml content

### write_docker_compose()

Write docker-compose.yml file

### check_certificates()

Check if TLS certificates exist

### setup_letsencrypt()

Setup Let's Encrypt certificates

### start_container()

Start the OpenWebUI container

### deploy()

Run the complete deployment process

## Function: main()

Main function with argument parsing

