#!/usr/bin/env python3
"""
Directory Structure Reorganization Script
Reorganizes the repository structure for production deployment
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectoryReorganizer:
    """Handles systematic directory structure reorganization"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.backup_dir = Path("structure_backup")
        
        # Define reorganization rules
        self.moves_to_perform = [
            # Merge tests directories
            {
                "source": "tests",
                "destination": "LiteTTS/tests/root_tests",
                "description": "Merge root tests with LiteTTS tests"
            },
            # Move JSON configs to LiteTTS/config
            {
                "source": "LiteTTS/tokenizer.json",
                "destination": "LiteTTS/config/tokenizer.json",
                "description": "Move tokenizer config"
            },
            {
                "source": "LiteTTS/tokenizer_config.json", 
                "destination": "LiteTTS/config/tokenizer_config.json",
                "description": "Move tokenizer config"
            },
            {
                "source": "LiteTTS/openapi.json",
                "destination": "LiteTTS/config/openapi.json", 
                "description": "Move OpenAPI spec"
            },
            # Move test scripts to LiteTTS/tests
            {
                "source": "LiteTTS/scripts/test_*.py",
                "destination": "LiteTTS/tests/scripts",
                "description": "Move test scripts"
            },
            {
                "source": "LiteTTS/scripts/comprehensive_*.py",
                "destination": "LiteTTS/tests/scripts",
                "description": "Move comprehensive test scripts"
            },
            {
                "source": "LiteTTS/scripts/debug_*.py",
                "destination": "LiteTTS/tests/scripts", 
                "description": "Move debug scripts"
            },
            {
                "source": "LiteTTS/scripts/validate_*.py",
                "destination": "LiteTTS/tests/scripts",
                "description": "Move validation scripts"
            }
        ]
        
        logger.info("Directory reorganizer initialized")
    
    def run_reorganization(self):
        """Run the complete directory reorganization"""
        logger.info("Starting directory structure reorganization")
        
        try:
            # Step 1: Create backup
            self._create_backup()
            
            # Step 2: Create new directory structure
            self._create_new_directories()
            
            # Step 3: Merge tests directories
            self._merge_tests_directories()
            
            # Step 4: Move JSON configs
            self._move_json_configs()
            
            # Step 5: Move test scripts
            self._move_test_scripts()
            
            # Step 6: Update import references
            self._update_import_references()
            
            # Step 7: Clean up empty directories
            self._cleanup_empty_directories()
            
            # Step 8: Generate reorganization summary
            self._generate_summary()
            
            logger.info("Directory reorganization completed successfully")
            
        except Exception as e:
            logger.error(f"Directory reorganization failed: {e}")
            raise
    
    def _create_backup(self):
        """Create backup of current structure"""
        logger.info("Creating structure backup")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Backup key directories
        backup_dirs = ["tests", "kokoro", "scripts"]
        
        self.backup_dir.mkdir()
        
        for dir_name in backup_dirs:
            source = Path(dir_name)
            if source.exists():
                dest = self.backup_dir / dir_name
                shutil.copytree(source, dest)
                logger.info(f"Backed up {dir_name}/")
    
    def _create_new_directories(self):
        """Create new directory structure"""
        logger.info("Creating new directory structure")
        
        new_dirs = [
            "LiteTTS/tests/scripts",
            "LiteTTS/tests/root_tests",
            "LiteTTS/benchmarks"
        ]
        
        for dir_path in new_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def _merge_tests_directories(self):
        """Merge root tests with kokoro tests"""
        logger.info("Merging tests directories")
        
        root_tests = Path("tests")
        litetts_tests = Path("LiteTTS/tests")
        root_tests_dest = litetts_tests / "root_tests"
        
        if root_tests.exists():
            # Copy all files from root tests to LiteTTS/tests/root_tests
            for item in root_tests.iterdir():
                if item.name == "__pycache__":
                    continue  # Skip cache directories
                
                dest = root_tests_dest / item.name
                
                if item.is_file():
                    shutil.copy2(item, dest)
                    logger.info(f"Copied {item.name} to root_tests/")
                elif item.is_dir():
                    shutil.copytree(item, dest)
                    logger.info(f"Copied {item.name}/ to root_tests/")
            
            # Remove original tests directory
            shutil.rmtree(root_tests)
            logger.info("Removed original tests/ directory")
    
    def _move_json_configs(self):
        """Move JSON configuration files to LiteTTS/config"""
        logger.info("Moving JSON configuration files")
        
        config_dir = Path("LiteTTS/config")
        
        # Files to move
        files_to_move = [
            "LiteTTS/tokenizer.json",
            "LiteTTS/tokenizer_config.json",
            "LiteTTS/openapi.json"
        ]
        
        for file_path in files_to_move:
            source = Path(file_path)
            if source.exists():
                dest = config_dir / source.name
                shutil.move(str(source), str(dest))
                logger.info(f"Moved {source.name} to config/")
    
    def _move_test_scripts(self):
        """Move test-related scripts to LiteTTS/tests/scripts"""
        logger.info("Moving test scripts")
        
        scripts_dir = Path("scripts")
        test_scripts_dest = Path("LiteTTS/tests/scripts")
        
        # Patterns for test scripts
        test_script_patterns = [
            "test_*.py",
            "comprehensive_*.py", 
            "debug_*.py",
            "validate_*.py",
            "benchmark_*.py"
        ]
        
        moved_files = []
        
        if scripts_dir.exists():
            for pattern in test_script_patterns:
                for script_file in scripts_dir.glob(pattern):
                    dest = test_scripts_dest / script_file.name
                    shutil.move(str(script_file), str(dest))
                    moved_files.append(script_file.name)
                    logger.info(f"Moved {script_file.name} to tests/LiteTTS/scripts/")
        
        # Create __init__.py in scripts directory
        init_file = test_scripts_dest / "__init__.py"
        with open(init_file, 'w') as f:
            f.write("# Test scripts package\n")
        
        logger.info(f"Moved {len(moved_files)} test scripts")
    
    def _update_import_references(self):
        """Update import references in moved files"""
        logger.info("Updating import references")
        
        # This is a simplified update - in practice, you might need more sophisticated handling
        # For now, we'll create a note about manual updates needed
        
        update_notes = [
            "Import references may need manual updates in:",
            "- LiteTTS/tests/root_tests/ files",
            "- LiteTTS/tests/LiteTTS/scripts/ files", 
            "- Any files importing moved JSON configs",
            "",
            "Common updates needed:",
            "- Update relative imports for moved test files",
            "- Update config file paths in code",
            "- Update test discovery paths in pytest configuration"
        ]
        
        notes_file = Path("IMPORT_UPDATE_NOTES.md")
        with open(notes_file, 'w') as f:
            f.write("# Import Reference Updates Needed\n\n")
            for note in update_notes:
                f.write(f"{note}\n")
        
        logger.info("Created import update notes")
    
    def _cleanup_empty_directories(self):
        """Remove empty directories"""
        logger.info("Cleaning up empty directories")
        
        # Check for empty directories and remove them
        dirs_to_check = [
            "scripts",  # May be empty after moving test scripts
        ]
        
        for dir_path in dirs_to_check:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                try:
                    # Check if directory is empty (ignoring hidden files)
                    if not any(path.iterdir()):
                        path.rmdir()
                        logger.info(f"Removed empty directory: {dir_path}")
                except OSError:
                    # Directory not empty
                    pass
    
    def _generate_summary(self):
        """Generate reorganization summary"""
        logger.info("Generating reorganization summary")
        
        summary = {
            "reorganization_date": "2025-08-16",
            "changes_made": [
                "Merged ./tests/ with ./LiteTTS/tests/root_tests/",
                "Moved JSON configs to ./LiteTTS/config/",
                "Moved test scripts to ./LiteTTS/tests/LiteTTS/scripts/",
                "Created backup at ./structure_backup/",
                "Updated directory structure for production readiness"
            ],
            "new_structure": {
                "LiteTTS/tests/": "All test files (root tests + kokoro tests)",
                "LiteTTS/tests/root_tests/": "Original root-level test files",
                "LiteTTS/tests/LiteTTS/scripts/": "Test and debug scripts",
                "LiteTTS/config/": "All JSON configuration files",
                "LiteTTS/benchmarks/": "Benchmark-related code"
            },
            "manual_updates_needed": [
                "Update import paths in moved test files",
                "Update pytest configuration for new test locations",
                "Update any hardcoded config file paths",
                "Review and test all moved functionality"
            ]
        }
        
        summary_file = Path("DIRECTORY_REORGANIZATION_SUMMARY.md")
        
        content = "# Directory Structure Reorganization Summary\n\n"
        content += f"**Date:** {summary['reorganization_date']}\n\n"
        content += "## Changes Made\n\n"
        
        for change in summary['changes_made']:
            content += f"- {change}\n"
        
        content += "\n## New Directory Structure\n\n"
        
        for path, description in summary['new_structure'].items():
            content += f"- **{path}** - {description}\n"
        
        content += "\n## Manual Updates Needed\n\n"
        
        for update in summary['manual_updates_needed']:
            content += f"- {update}\n"
        
        content += f"\n## Backup Location\n\n"
        content += f"Original structure backed up to: `{self.backup_dir}`\n"
        
        with open(summary_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Summary saved to {summary_file}")

def main():
    """Main reorganization execution"""
    print("Directory Structure Reorganization")
    print("=" * 50)
    
    try:
        reorganizer = DirectoryReorganizer()
        reorganizer.run_reorganization()
        
        print("\n✅ Directory reorganization completed successfully!")
        print("\nNew structure:")
        print("- LiteTTS/tests/ - All test files consolidated")
        print("- LiteTTS/config/ - All JSON configuration files")
        print("- LiteTTS/benchmarks/ - Benchmark code")
        print("\nBackup created at: structure_backup/")
        print("\n⚠️  Manual updates may be needed - see IMPORT_UPDATE_NOTES.md")
        
    except Exception as e:
        logger.error(f"Reorganization failed: {e}")
        print(f"\n❌ Reorganization failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
