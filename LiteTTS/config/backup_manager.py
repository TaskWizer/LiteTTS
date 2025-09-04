#!/usr/bin/env python3
"""
Configuration Backup and Restore Manager for LiteTTS

Provides backup and restore capabilities for configuration files
with timestamped versioning and rollback functionality.
"""

import os
import json
import shutil
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Configuration backup and restore manager.
    
    Provides functionality to create timestamped backups of configuration
    files and restore them when needed.
    """
    
    def __init__(self, backup_dir: str = "config/backups"):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory to store configuration backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration files to backup
        self.config_files = [
            "config/settings.json",
            "config/override.json",
            "config/production.json"
        ]
        
        self.logger.info(f"BackupManager initialized with backup directory: {self.backup_dir}")
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a backup of all configuration files.
        
        Args:
            backup_name: Optional custom name for the backup
            
        Returns:
            Dictionary containing backup information
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if backup_name:
            backup_id = f"{backup_name}_{timestamp}"
        else:
            backup_id = f"auto_backup_{timestamp}"
        
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
        backup_info = {
            "backup_id": backup_id,
            "timestamp": timestamp,
            "backup_path": str(backup_path),
            "files_backed_up": [],
            "files_failed": [],
            "success": True
        }
        
        self.logger.info(f"Creating configuration backup: {backup_id}")
        
        try:
            for config_file in self.config_files:
                source_path = Path(config_file)
                
                if source_path.exists():
                    dest_path = backup_path / source_path.name
                    
                    try:
                        shutil.copy2(source_path, dest_path)
                        backup_info["files_backed_up"].append(str(source_path))
                        self.logger.debug(f"Backed up: {source_path} -> {dest_path}")
                    except Exception as e:
                        backup_info["files_failed"].append({
                            "file": str(source_path),
                            "error": str(e)
                        })
                        self.logger.error(f"Failed to backup {source_path}: {e}")
                else:
                    self.logger.warning(f"Configuration file not found: {source_path}")
            
            # Create backup metadata
            metadata = {
                "backup_id": backup_id,
                "created_at": timestamp,
                "files": backup_info["files_backed_up"],
                "failed_files": backup_info["files_failed"],
                "total_files": len(backup_info["files_backed_up"])
            }
            
            metadata_path = backup_path / "backup_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            if backup_info["files_failed"]:
                backup_info["success"] = False
                self.logger.warning(f"Backup completed with {len(backup_info['files_failed'])} failures")
            else:
                self.logger.info(f"✅ Backup created successfully: {backup_id}")
            
            return backup_info
            
        except Exception as e:
            backup_info["success"] = False
            backup_info["error"] = str(e)
            self.logger.error(f"Backup creation failed: {e}")
            return backup_info
    
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Restore configuration from a backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            Dictionary containing restore operation results
        """
        backup_path = self.backup_dir / backup_id
        
        restore_info = {
            "backup_id": backup_id,
            "backup_path": str(backup_path),
            "files_restored": [],
            "files_failed": [],
            "success": True
        }
        
        if not backup_path.exists():
            restore_info["success"] = False
            restore_info["error"] = f"Backup not found: {backup_id}"
            self.logger.error(f"Backup not found: {backup_id}")
            return restore_info
        
        self.logger.info(f"Restoring configuration from backup: {backup_id}")
        
        try:
            # Create a backup of current config before restoring
            pre_restore_backup = self.create_backup("pre_restore")
            self.logger.info(f"Created pre-restore backup: {pre_restore_backup['backup_id']}")
            
            # Restore files from backup
            for backup_file in backup_path.glob("*.json"):
                if backup_file.name == "backup_metadata.json":
                    continue
                
                # Determine target path
                if backup_file.name in ["settings.json", "override.json", "production.json"]:
                    target_path = Path("config") / backup_file.name
                else:
                    continue  # Skip unknown files
                
                try:
                    # Ensure target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file from backup
                    shutil.copy2(backup_file, target_path)
                    restore_info["files_restored"].append(str(target_path))
                    self.logger.debug(f"Restored: {backup_file} -> {target_path}")
                    
                except Exception as e:
                    restore_info["files_failed"].append({
                        "file": str(backup_file),
                        "target": str(target_path),
                        "error": str(e)
                    })
                    self.logger.error(f"Failed to restore {backup_file}: {e}")
            
            if restore_info["files_failed"]:
                restore_info["success"] = False
                self.logger.warning(f"Restore completed with {len(restore_info['files_failed'])} failures")
            else:
                self.logger.info(f"✅ Configuration restored successfully from: {backup_id}")
            
            return restore_info
            
        except Exception as e:
            restore_info["success"] = False
            restore_info["error"] = str(e)
            self.logger.error(f"Restore operation failed: {e}")
            return restore_info
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        try:
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    metadata_path = backup_dir / "backup_metadata.json"
                    
                    if metadata_path.exists():
                        try:
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                            backups.append(metadata)
                        except Exception as e:
                            self.logger.warning(f"Failed to read backup metadata: {metadata_path}: {e}")
                    else:
                        # Create basic info for backups without metadata
                        backups.append({
                            "backup_id": backup_dir.name,
                            "created_at": "unknown",
                            "files": [],
                            "total_files": len(list(backup_dir.glob("*.json")))
                        })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
        
        return backups
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a specific backup.
        
        Args:
            backup_id: ID of the backup to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            self.logger.warning(f"Backup not found for deletion: {backup_id}")
            return False
        
        try:
            shutil.rmtree(backup_path)
            self.logger.info(f"✅ Deleted backup: {backup_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10) -> Dict[str, Any]:
        """
        Clean up old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
            
        Returns:
            Dictionary containing cleanup results
        """
        backups = self.list_backups()
        
        cleanup_info = {
            "total_backups": len(backups),
            "kept_backups": 0,
            "deleted_backups": 0,
            "deleted_backup_ids": [],
            "success": True
        }
        
        if len(backups) <= keep_count:
            cleanup_info["kept_backups"] = len(backups)
            self.logger.info(f"No cleanup needed. {len(backups)} backups <= {keep_count} limit")
            return cleanup_info
        
        # Delete oldest backups
        backups_to_delete = backups[keep_count:]
        
        for backup in backups_to_delete:
            backup_id = backup["backup_id"]
            if self.delete_backup(backup_id):
                cleanup_info["deleted_backups"] += 1
                cleanup_info["deleted_backup_ids"].append(backup_id)
            else:
                cleanup_info["success"] = False
        
        cleanup_info["kept_backups"] = len(backups) - cleanup_info["deleted_backups"]
        
        self.logger.info(f"Backup cleanup completed: kept {cleanup_info['kept_backups']}, deleted {cleanup_info['deleted_backups']}")
        
        return cleanup_info


# Global instance
_backup_manager = None


def get_backup_manager() -> BackupManager:
    """Get or create global backup manager instance"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
