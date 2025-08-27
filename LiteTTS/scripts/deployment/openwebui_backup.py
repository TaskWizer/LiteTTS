#!/usr/bin/env python3
"""
OpenWebUI Backup Script (Python version)
Cross-platform backup utility for OpenWebUI configuration and data
Replaces openwebui-backup.sh with better error handling and cross-platform support
"""

import os
import sys
import shutil
import tarfile
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenWebUIBackup:
    """OpenWebUI backup utility"""
    
    def __init__(self, backup_dir="./openwebui_backups"):
        self.backup_dir = Path(backup_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"openwebui_backup_{self.timestamp}"
        self.backup_path = self.backup_dir / self.backup_name
        
        # Configuration files to backup
        self.config_files = [
            "docker-compose.yml",
            "docker-compose.yaml", 
            ".env",
            ".env.local",
            ".env.production"
        ]
        
        # Directories to backup
        self.data_dirs = [
            "data",
            "certs",
            "config",
            "logs"
        ]
    
    def create_backup_directory(self):
        """Create backup directory structure"""
        try:
            self.backup_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created backup directory: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create backup directory: {e}")
            return False
    
    def backup_config_files(self):
        """Backup configuration files"""
        backed_up = []
        
        for config_file in self.config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    dest_path = self.backup_path / config_file
                    shutil.copy2(config_path, dest_path)
                    backed_up.append(config_file)
                    logger.info(f"✅ Backed up config file: {config_file}")
                except Exception as e:
                    logger.error(f"❌ Failed to backup {config_file}: {e}")
            else:
                logger.info(f"ℹ️  Config file not found: {config_file}")
        
        if backed_up:
            logger.info(f"✅ Backed up {len(backed_up)} configuration files")
        else:
            logger.warning("⚠️  No configuration files found to backup")
        
        return backed_up
    
    def backup_data_directories(self):
        """Backup data directories as compressed archives"""
        backed_up = []
        
        for data_dir in self.data_dirs:
            data_path = Path(data_dir)
            if data_path.exists() and data_path.is_dir():
                try:
                    # Create compressed tar archive
                    archive_name = f"{data_dir}.tar.gz"
                    archive_path = self.backup_path / archive_name
                    
                    with tarfile.open(archive_path, "w:gz") as tar:
                        tar.add(data_path, arcname=data_dir)
                    
                    backed_up.append(data_dir)
                    
                    # Get archive size for reporting
                    size_mb = archive_path.stat().st_size / (1024 * 1024)
                    logger.info(f"✅ Backed up directory: {data_dir} ({size_mb:.1f} MB)")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to backup directory {data_dir}: {e}")
            else:
                logger.info(f"ℹ️  Directory not found: {data_dir}")
        
        if backed_up:
            logger.info(f"✅ Backed up {len(backed_up)} data directories")
        else:
            logger.warning("⚠️  No data directories found to backup")
        
        return backed_up
    
    def create_backup_manifest(self, config_files, data_dirs):
        """Create a manifest file with backup details"""
        try:
            manifest = {
                "backup_name": self.backup_name,
                "timestamp": self.timestamp,
                "datetime": datetime.now().isoformat(),
                "config_files": config_files,
                "data_directories": data_dirs,
                "backup_path": str(self.backup_path),
                "total_files": len(config_files) + len(data_dirs)
            }
            
            manifest_path = self.backup_path / "backup_manifest.json"
            import json
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"✅ Created backup manifest: {manifest_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create backup manifest: {e}")
            return False
    
    def run_backup(self):
        """Run the complete backup process"""
        logger.info("🔄 Starting OpenWebUI backup process...")
        logger.info(f"📁 Backup location: {self.backup_path}")
        
        # Create backup directory
        if not self.create_backup_directory():
            return False
        
        # Backup configuration files
        config_files = self.backup_config_files()
        
        # Backup data directories
        data_dirs = self.backup_data_directories()
        
        # Create manifest
        self.create_backup_manifest(config_files, data_dirs)
        
        # Calculate total backup size
        try:
            total_size = sum(
                f.stat().st_size for f in self.backup_path.rglob('*') if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            logger.info(f"📊 Total backup size: {size_mb:.1f} MB")
        except Exception as e:
            logger.warning(f"Could not calculate backup size: {e}")
        
        logger.info("✅ OpenWebUI backup completed successfully!")
        logger.info(f"📁 Backup saved to: {self.backup_path}")
        
        return True

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Backup OpenWebUI configuration and data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python openwebui_backup.py                           # Default backup
  python openwebui_backup.py --backup-dir ./backups   # Custom backup directory
  python openwebui_backup.py --list                   # List existing backups
        """
    )
    
    parser.add_argument(
        "--backup-dir",
        type=str,
        default="./openwebui_backups",
        help="Backup directory (default: ./openwebui_backups)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing backups"
    )
    
    args = parser.parse_args()
    
    if args.list:
        # List existing backups
        backup_dir = Path(args.backup_dir)
        if backup_dir.exists():
            backups = list(backup_dir.glob("openwebui_backup_*"))
            if backups:
                logger.info(f"📋 Found {len(backups)} backups in {backup_dir}:")
                for backup in sorted(backups):
                    logger.info(f"  - {backup.name}")
            else:
                logger.info(f"📋 No backups found in {backup_dir}")
        else:
            logger.info(f"📋 Backup directory does not exist: {backup_dir}")
        return 0
    
    # Run backup
    backup = OpenWebUIBackup(args.backup_dir)
    success = backup.run_backup()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
