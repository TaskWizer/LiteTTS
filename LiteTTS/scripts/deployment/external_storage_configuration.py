#!/usr/bin/env python3
"""
External Storage Configuration System
Set up external storage volumes for models, voices, cache, and logs to enable easier backups and persistence
"""

import os
import sys
import json
import logging
import shutil
import time
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
class StorageVolume:
    """Storage volume configuration"""
    name: str
    internal_path: str
    external_path: str
    volume_type: str  # models, voices, cache, logs, config
    size_estimate_gb: float
    backup_priority: str  # critical, high, medium, low
    mount_options: List[str]
    permissions: str
    description: str

@dataclass
class StorageConfiguration:
    """Complete storage configuration"""
    base_storage_path: str
    enable_external_storage: bool
    volumes: List[StorageVolume]
    backup_configuration: Dict[str, Any]
    monitoring_configuration: Dict[str, Any]
    migration_strategy: Dict[str, Any]

class ExternalStorageConfigurator:
    """External storage configuration system"""
    
    def __init__(self):
        self.results_dir = Path("test_results/storage_configuration")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Default storage paths
        self.default_storage_base = Path("/opt/kokoro-storage")
        
        # Current internal paths
        self.internal_paths = {
            "models": "models",
            "voices": "voices", 
            "cache": "cache",
            "logs": "logs",
            "config": "config",
            "test_results": "test_results",
            "dictionaries": "docs/dictionaries"
        }
        
    def create_optimal_storage_configuration(self, base_path: Optional[str] = None) -> StorageConfiguration:
        """Create optimal external storage configuration"""
        logger.info("Creating optimal external storage configuration...")
        
        if base_path is None:
            base_path = str(self.default_storage_base)
        
        base_storage_path = Path(base_path)
        
        # Define storage volumes with realistic size estimates
        volumes = [
            StorageVolume(
                name="models",
                internal_path="models",
                external_path=str(base_storage_path / "models"),
                volume_type="models",
                size_estimate_gb=2.5,  # ONNX models are typically 1-3GB
                backup_priority="critical",
                mount_options=["ro"],  # Read-only for models
                permissions="755",
                description="ONNX model files for TTS inference"
            ),
            StorageVolume(
                name="voices",
                internal_path="voices",
                external_path=str(base_storage_path / "voices"),
                volume_type="voices",
                size_estimate_gb=1.0,  # Voice embeddings and metadata
                backup_priority="critical",
                mount_options=["ro"],  # Read-only for voices
                permissions="755",
                description="Voice embeddings and configuration files"
            ),
            StorageVolume(
                name="cache",
                internal_path="cache",
                external_path=str(base_storage_path / "cache"),
                volume_type="cache",
                size_estimate_gb=5.0,  # Cache can grow significantly
                backup_priority="low",
                mount_options=["rw"],  # Read-write for cache
                permissions="755",
                description="Audio generation cache and temporary files"
            ),
            StorageVolume(
                name="logs",
                internal_path="logs",
                external_path=str(base_storage_path / "logs"),
                volume_type="logs",
                size_estimate_gb=1.0,  # Log files
                backup_priority="medium",
                mount_options=["rw"],  # Read-write for logs
                permissions="755",
                description="Application logs and monitoring data"
            ),
            StorageVolume(
                name="config",
                internal_path="config",
                external_path=str(base_storage_path / "config"),
                volume_type="config",
                size_estimate_gb=0.1,  # Configuration files are small
                backup_priority="critical",
                mount_options=["rw"],  # Read-write for config
                permissions="644",
                description="Configuration files and overrides"
            ),
            StorageVolume(
                name="dictionaries",
                internal_path="dictionaries",
                external_path=str(base_storage_path / "dictionaries"),
                volume_type="dictionaries",
                size_estimate_gb=0.5,  # Dictionary files
                backup_priority="high",
                mount_options=["ro"],  # Read-only for dictionaries
                permissions="644",
                description="Pronunciation dictionaries and phonetic data"
            ),
            StorageVolume(
                name="test_results",
                internal_path="test_results",
                external_path=str(base_storage_path / "test_results"),
                volume_type="test_results",
                size_estimate_gb=2.0,  # Test results and benchmarks
                backup_priority="medium",
                mount_options=["rw"],  # Read-write for test results
                permissions="755",
                description="Test results, benchmarks, and analysis data"
            )
        ]
        
        # Backup configuration
        backup_config = {
            "enabled": True,
            "schedule": {
                "critical": "daily",
                "high": "weekly", 
                "medium": "monthly",
                "low": "never"
            },
            "retention": {
                "critical": "30 days",
                "high": "14 days",
                "medium": "7 days",
                "low": "3 days"
            },
            "backup_location": str(base_storage_path / "backups"),
            "compression": True,
            "encryption": False  # Can be enabled for sensitive data
        }
        
        # Monitoring configuration
        monitoring_config = {
            "enabled": True,
            "disk_usage_threshold": 85,  # Alert at 85% usage
            "free_space_minimum_gb": 5,  # Alert if less than 5GB free
            "check_interval_minutes": 15,
            "alerts": {
                "email": False,
                "webhook": False,
                "log": True
            }
        }
        
        # Migration strategy
        migration_config = {
            "enabled": True,
            "backup_before_migration": True,
            "verify_after_migration": True,
            "rollback_on_failure": True,
            "migration_batch_size": "1GB",
            "preserve_permissions": True,
            "create_symlinks": True  # Create symlinks for backward compatibility
        }
        
        config = StorageConfiguration(
            base_storage_path=base_path,
            enable_external_storage=True,
            volumes=volumes,
            backup_configuration=backup_config,
            monitoring_configuration=monitoring_config,
            migration_strategy=migration_config
        )
        
        logger.info(f"Created storage configuration with {len(volumes)} volumes, total estimated size: {sum(v.size_estimate_gb for v in volumes):.1f}GB")
        return config
    
    def create_storage_directories(self, config: StorageConfiguration) -> Dict[str, bool]:
        """Create external storage directories"""
        logger.info("Creating external storage directories...")
        
        results = {}
        
        for volume in config.volumes:
            try:
                external_path = Path(volume.external_path)
                external_path.mkdir(parents=True, exist_ok=True)
                
                # Set permissions
                os.chmod(external_path, int(volume.permissions, 8))
                
                # Create subdirectories if needed
                if volume.volume_type == "logs":
                    (external_path / "app").mkdir(exist_ok=True)
                    (external_path / "access").mkdir(exist_ok=True)
                    (external_path / "error").mkdir(exist_ok=True)
                elif volume.volume_type == "cache":
                    (external_path / "audio").mkdir(exist_ok=True)
                    (external_path / "models").mkdir(exist_ok=True)
                    (external_path / "temp").mkdir(exist_ok=True)
                elif volume.volume_type == "test_results":
                    (external_path / "benchmarks").mkdir(exist_ok=True)
                    (external_path / "audio_quality").mkdir(exist_ok=True)
                    (external_path / "performance").mkdir(exist_ok=True)
                
                results[volume.name] = True
                logger.info(f"Created directory: {external_path}")
                
            except Exception as e:
                results[volume.name] = False
                logger.error(f"Failed to create directory for {volume.name}: {e}")
        
        return results
    
    def migrate_existing_data(self, config: StorageConfiguration) -> Dict[str, Any]:
        """Migrate existing data to external storage"""
        logger.info("Migrating existing data to external storage...")
        
        migration_results = {
            "successful_migrations": [],
            "failed_migrations": [],
            "skipped_migrations": [],
            "total_size_migrated_gb": 0.0,
            "migration_time_seconds": 0.0
        }
        
        start_time = time.time()
        
        for volume in config.volumes:
            internal_path = Path(volume.internal_path)
            external_path = Path(volume.external_path)
            
            try:
                if not internal_path.exists():
                    migration_results["skipped_migrations"].append({
                        "volume": volume.name,
                        "reason": "Internal path does not exist"
                    })
                    continue
                
                if config.migration_strategy["backup_before_migration"]:
                    # Create backup before migration
                    backup_path = external_path.parent / f"{volume.name}_backup_{int(time.time())}"
                    if external_path.exists():
                        shutil.copytree(external_path, backup_path)
                        logger.info(f"Created backup: {backup_path}")
                
                # Calculate size before migration
                size_bytes = self._calculate_directory_size(internal_path)
                size_gb = size_bytes / (1024**3)
                
                # Perform migration
                if external_path.exists():
                    shutil.rmtree(external_path)
                
                shutil.copytree(internal_path, external_path)
                
                # Verify migration if enabled
                if config.migration_strategy["verify_after_migration"]:
                    if not self._verify_migration(internal_path, external_path):
                        raise Exception("Migration verification failed")
                
                # Create symlink for backward compatibility
                if config.migration_strategy["create_symlinks"]:
                    if internal_path.exists() and not internal_path.is_symlink():
                        shutil.rmtree(internal_path)
                    if not internal_path.exists():
                        internal_path.symlink_to(external_path)
                        logger.info(f"Created symlink: {internal_path} -> {external_path}")
                
                migration_results["successful_migrations"].append({
                    "volume": volume.name,
                    "size_gb": size_gb,
                    "internal_path": str(internal_path),
                    "external_path": str(external_path)
                })
                
                migration_results["total_size_migrated_gb"] += size_gb
                logger.info(f"Successfully migrated {volume.name}: {size_gb:.2f}GB")
                
            except Exception as e:
                migration_results["failed_migrations"].append({
                    "volume": volume.name,
                    "error": str(e),
                    "internal_path": str(internal_path),
                    "external_path": str(external_path)
                })
                logger.error(f"Failed to migrate {volume.name}: {e}")
        
        migration_results["migration_time_seconds"] = time.time() - start_time
        logger.info(f"Migration completed in {migration_results['migration_time_seconds']:.1f} seconds")
        
        return migration_results
    
    def _calculate_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            logger.warning(f"Error calculating size for {path}: {e}")
        return total_size
    
    def _verify_migration(self, source: Path, destination: Path) -> bool:
        """Verify migration by comparing file counts and sizes"""
        try:
            source_files = list(source.rglob("*"))
            dest_files = list(destination.rglob("*"))
            
            # Compare file counts
            if len(source_files) != len(dest_files):
                logger.error(f"File count mismatch: {len(source_files)} vs {len(dest_files)}")
                return False
            
            # Compare total sizes
            source_size = self._calculate_directory_size(source)
            dest_size = self._calculate_directory_size(destination)
            
            if abs(source_size - dest_size) > 1024:  # Allow 1KB difference
                logger.error(f"Size mismatch: {source_size} vs {dest_size}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            return False
    
    def generate_docker_compose_volumes(self, config: StorageConfiguration) -> str:
        """Generate Docker Compose volume configuration"""
        logger.info("Generating Docker Compose volume configuration...")
        
        volumes_section = "volumes:\n"
        services_volumes = []
        
        for volume in config.volumes:
            # Add to volumes section
            volumes_section += f"  {volume.name}:\n"
            volumes_section += f"    driver: local\n"
            volumes_section += f"    driver_opts:\n"
            volumes_section += f"      type: none\n"
            volumes_section += f"      o: bind\n"
            volumes_section += f"      device: {volume.external_path}\n\n"
            
            # Add to service volumes
            mount_option = "ro" if "ro" in volume.mount_options else "rw"
            services_volumes.append(f"      - {volume.name}:/app/{volume.internal_path}:{mount_option}")
        
        # Complete docker-compose section
        compose_config = f"""version: '3.8'

services:
  kokoro-tts:
    build: .
    container_name: kokoro-tts-prod
    restart: unless-stopped
    ports:
      - "8354:8354"
    volumes:
{chr(10).join(services_volumes)}
    environment:
      - ENVIRONMENT=production
      - EXTERNAL_STORAGE_ENABLED=true
      - STORAGE_BASE_PATH={config.base_storage_path}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8354/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    networks:
      - kokoro-network

networks:
  kokoro-network:
    driver: bridge

{volumes_section}"""
        
        # Save configuration
        compose_file = self.results_dir / "docker-compose-external-storage.yml"
        with open(compose_file, 'w') as f:
            f.write(compose_config)
        
        logger.info(f"Docker Compose configuration saved to: {compose_file}")
        return compose_config
    
    def generate_backup_scripts(self, config: StorageConfiguration) -> Dict[str, str]:
        """Generate backup scripts for different priorities"""
        logger.info("Generating backup scripts...")
        
        scripts = {}
        
        # Critical backup script (daily)
        critical_volumes = [v for v in config.volumes if v.backup_priority == "critical"]
        critical_script = self._create_backup_script(critical_volumes, config, "critical")
        scripts["critical_backup.sh"] = critical_script
        
        # High priority backup script (weekly)
        high_volumes = [v for v in config.volumes if v.backup_priority == "high"]
        high_script = self._create_backup_script(high_volumes, config, "high")
        scripts["high_backup.sh"] = high_script
        
        # Medium priority backup script (monthly)
        medium_volumes = [v for v in config.volumes if v.backup_priority == "medium"]
        medium_script = self._create_backup_script(medium_volumes, config, "medium")
        scripts["medium_backup.sh"] = medium_script
        
        # Save scripts
        for script_name, script_content in scripts.items():
            script_file = self.results_dir / script_name
            with open(script_file, 'w') as f:
                f.write(script_content)
            os.chmod(script_file, 0o755)  # Make executable
            logger.info(f"Backup script saved: {script_file}")
        
        return scripts
    
    def _create_backup_script(self, volumes: List[StorageVolume], config: StorageConfiguration, priority: str) -> str:
        """Create backup script for specific priority volumes"""
        backup_location = config.backup_configuration["backup_location"]
        compression = config.backup_configuration["compression"]
        
        script = f"""#!/bin/bash
# Kokoro TTS {priority.title()} Priority Backup Script
# Generated automatically - do not edit manually

set -e

BACKUP_BASE="{backup_location}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$BACKUP_BASE/{priority}_$TIMESTAMP"

echo "Starting {priority} priority backup at $(date)"
mkdir -p "$BACKUP_DIR"

"""
        
        for volume in volumes:
            if compression:
                script += f"""
# Backup {volume.name} ({volume.description})
echo "Backing up {volume.name}..."
tar -czf "$BACKUP_DIR/{volume.name}.tar.gz" -C "{volume.external_path}" .
echo "Completed backup of {volume.name}"
"""
            else:
                script += f"""
# Backup {volume.name} ({volume.description})
echo "Backing up {volume.name}..."
cp -r "{volume.external_path}" "$BACKUP_DIR/{volume.name}"
echo "Completed backup of {volume.name}"
"""
        
        # Add cleanup based on retention policy
        retention = config.backup_configuration["retention"][priority]
        if retention != "never":
            if "days" in retention:
                days = retention.split()[0]
                script += f"""
# Cleanup old backups (retention: {retention})
find "$BACKUP_BASE" -name "{priority}_*" -type d -mtime +{days} -exec rm -rf {{}} \\;
echo "Cleaned up backups older than {retention}"
"""
        
        script += """
echo "Backup completed successfully at $(date)"
"""
        
        return script

    def create_monitoring_script(self, config: StorageConfiguration) -> str:
        """Create storage monitoring script"""
        logger.info("Creating storage monitoring script...")

        monitoring_script = f"""#!/bin/bash
# Kokoro TTS Storage Monitoring Script
# Generated automatically - do not edit manually

set -e

STORAGE_BASE="{config.base_storage_path}"
THRESHOLD={config.monitoring_configuration["disk_usage_threshold"]}
MIN_FREE_GB={config.monitoring_configuration["free_space_minimum_gb"]}
LOG_FILE="$STORAGE_BASE/logs/storage_monitor.log"

# Create log file if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

echo "$(date): Starting storage monitoring check" >> "$LOG_FILE"

# Check overall disk usage
USAGE=$(df "$STORAGE_BASE" | awk 'NR==2 {{print $5}}' | sed 's/%//')
AVAILABLE_GB=$(df -BG "$STORAGE_BASE" | awk 'NR==2 {{print $4}}' | sed 's/G//')

echo "$(date): Disk usage: $USAGE%, Available: ${{AVAILABLE_GB}}GB" >> "$LOG_FILE"

# Check usage threshold
if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "$(date): WARNING - Disk usage ($USAGE%) exceeds threshold ($THRESHOLD%)" >> "$LOG_FILE"
    echo "ALERT: Kokoro TTS storage usage critical: $USAGE%" >&2
fi

# Check minimum free space
if [ "$AVAILABLE_GB" -lt "$MIN_FREE_GB" ]; then
    echo "$(date): WARNING - Available space (${{AVAILABLE_GB}}GB) below minimum (${{MIN_FREE_GB}}GB)" >> "$LOG_FILE"
    echo "ALERT: Kokoro TTS storage space low: ${{AVAILABLE_GB}}GB remaining" >&2
fi

# Check individual volume sizes
"""

        for volume in config.volumes:
            monitoring_script += f"""
# Monitor {volume.name} volume
if [ -d "{volume.external_path}" ]; then
    SIZE=$(du -sh "{volume.external_path}" | cut -f1)
    echo "$(date): {volume.name} volume size: $SIZE" >> "$LOG_FILE"
fi
"""

        monitoring_script += """
echo "$(date): Storage monitoring check completed" >> "$LOG_FILE"
"""

        # Save monitoring script
        script_file = self.results_dir / "storage_monitor.sh"
        with open(script_file, 'w') as f:
            f.write(monitoring_script)
        os.chmod(script_file, 0o755)

        logger.info(f"Storage monitoring script saved: {script_file}")
        return monitoring_script

    def run_comprehensive_storage_setup(self, base_path: Optional[str] = None) -> Dict[str, Any]:
        """Run comprehensive external storage setup"""
        logger.info("Starting comprehensive external storage setup...")

        # Create optimal configuration
        config = self.create_optimal_storage_configuration(base_path)

        # Create storage directories
        directory_results = self.create_storage_directories(config)

        # Migrate existing data
        migration_results = self.migrate_existing_data(config)

        # Generate Docker Compose configuration
        docker_compose_config = self.generate_docker_compose_volumes(config)

        # Generate backup scripts
        backup_scripts = self.generate_backup_scripts(config)

        # Create monitoring script
        monitoring_script = self.create_monitoring_script(config)

        # Generate summary report
        setup_results = {
            "setup_timestamp": time.time(),
            "storage_configuration": asdict(config),
            "directory_creation_results": directory_results,
            "migration_results": migration_results,
            "docker_compose_generated": True,
            "backup_scripts_generated": list(backup_scripts.keys()),
            "monitoring_script_generated": True,
            "total_estimated_storage_gb": sum(v.size_estimate_gb for v in config.volumes),
            "setup_summary": self._generate_setup_summary(config, directory_results, migration_results),
            "next_steps": self._generate_next_steps(config)
        }

        # Save complete configuration
        config_file = self.results_dir / f"external_storage_setup_{int(time.time())}.json"
        with open(config_file, 'w') as f:
            json.dump(setup_results, f, indent=2, default=str)

        logger.info(f"External storage setup completed. Results saved to: {config_file}")
        return setup_results

    def _generate_setup_summary(self, config: StorageConfiguration,
                               directory_results: Dict[str, bool],
                               migration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate setup summary"""
        successful_dirs = sum(1 for success in directory_results.values() if success)
        successful_migrations = len(migration_results["successful_migrations"])
        failed_migrations = len(migration_results["failed_migrations"])

        summary = {
            "total_volumes_configured": len(config.volumes),
            "directories_created_successfully": successful_dirs,
            "directories_failed": len(directory_results) - successful_dirs,
            "successful_migrations": successful_migrations,
            "failed_migrations": failed_migrations,
            "total_data_migrated_gb": migration_results["total_size_migrated_gb"],
            "migration_time_seconds": migration_results["migration_time_seconds"],
            "setup_success_rate": (successful_dirs + successful_migrations) / (len(directory_results) + len(config.volumes)) if config.volumes else 0
        }

        return summary

    def _generate_next_steps(self, config: StorageConfiguration) -> List[str]:
        """Generate next steps for deployment"""
        next_steps = [
            "Review generated docker-compose-external-storage.yml configuration",
            "Test storage volume mounts before production deployment",
            "Set up backup schedule using generated backup scripts",
            "Configure storage monitoring with generated monitoring script",
            "Update application configuration to use external storage paths",
            "Test data persistence across container restarts",
            "Implement log rotation for external log volumes",
            "Set up automated backup verification",
            "Configure storage alerts and notifications",
            "Document storage maintenance procedures"
        ]

        # Add specific recommendations based on configuration
        if config.backup_configuration["enabled"]:
            next_steps.append("Schedule backup scripts in cron or systemd timers")

        if config.monitoring_configuration["enabled"]:
            next_steps.append("Integrate storage monitoring with existing monitoring systems")

        total_size = sum(v.size_estimate_gb for v in config.volumes)
        if total_size > 10:
            next_steps.append("Consider implementing storage tiering for large datasets")

        return next_steps

def main():
    """Main function to run external storage configuration"""
    configurator = ExternalStorageConfigurator()

    try:
        # Run comprehensive storage setup
        results = configurator.run_comprehensive_storage_setup()

        print("\n" + "="*80)
        print("EXTERNAL STORAGE CONFIGURATION SUMMARY")
        print("="*80)

        config = results["storage_configuration"]
        summary = results["setup_summary"]

        print(f"Storage Base Path: {config['base_storage_path']}")
        print(f"Total Volumes Configured: {summary['total_volumes_configured']}")
        print(f"Total Estimated Storage: {results['total_estimated_storage_gb']:.1f}GB")

        print(f"\nSetup Results:")
        print(f"  Directories Created: {summary['directories_created_successfully']}/{summary['total_volumes_configured']}")
        print(f"  Successful Migrations: {summary['successful_migrations']}")
        print(f"  Failed Migrations: {summary['failed_migrations']}")
        print(f"  Data Migrated: {summary['total_data_migrated_gb']:.2f}GB")
        print(f"  Migration Time: {summary['migration_time_seconds']:.1f}s")
        print(f"  Setup Success Rate: {summary['setup_success_rate']:.1%}")

        print(f"\nVolume Configuration:")
        for volume in config["volumes"]:
            print(f"  {volume['name']}: {volume['external_path']} ({volume['size_estimate_gb']:.1f}GB, {volume['backup_priority']} priority)")

        print(f"\nGenerated Files:")
        print(f"  Docker Compose: docker-compose-external-storage.yml")
        print(f"  Backup Scripts: {', '.join(results['backup_scripts_generated'])}")
        print(f"  Monitoring Script: storage_monitor.sh")

        print(f"\nNext Steps:")
        for i, step in enumerate(results["next_steps"][:5], 1):  # Show first 5 steps
            print(f"  {i}. {step}")

        if len(results["next_steps"]) > 5:
            print(f"  ... and {len(results['next_steps']) - 5} more steps")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"External storage configuration failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
