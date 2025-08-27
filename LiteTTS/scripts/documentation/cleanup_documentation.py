#!/usr/bin/env python3
"""
Documentation Cleanup and Consolidation Script
Systematically cleans up and organizes documentation for production readiness
"""

import os
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List, Set
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentationCleanup:
    """Handles systematic documentation cleanup and consolidation"""
    
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.backup_dir = Path("docs_backup")
        
        # Define cleanup rules
        self.directories_to_remove = {
            "logs", "memories", "tasks", "prompts", "tests"
        }
        
        self.directories_to_consolidate = {
            "assessments": "analysis",
            "audit_reports": "analysis", 
            "improvements": "analysis",
            "reports": "analysis"
        }
        
        self.files_to_remove = {
            "NOTES.md~",  # Backup file
            "PERFORMANCE-OPTIMIZATION-RESEARCH.md~",  # Backup file
            "dashboard.html",  # Move to examples
            "comprehensive_optimization_summary.md",  # Consolidate
            "configuration_optimization_analysis.md",  # Consolidate
            "feature_implementation_analysis.md",  # Consolidate
            "performance_analysis_results.md"  # Consolidate
        }
        
        self.files_to_move_to_usage = {
            "QUICKSTART.md",
            "QUICK_START_COMMANDS.md", 
            "STARTUP_GUIDE.md",
            "USAGE.md",
            "DEPLOYMENT_GUIDE.md",
            "DOCKER_DEPLOYMENT.md",
            "troubleshooting_guide.md",
            "ssml_guide.md",
            "performance_guide.md"
        }
        
        logger.info(f"Documentation cleanup initialized for {self.docs_dir}")
    
    def run_cleanup(self):
        """Run the complete documentation cleanup process"""
        logger.info("Starting documentation cleanup process")
        
        try:
            # Step 1: Create backup
            self._create_backup()
            
            # Step 2: Create new directory structure
            self._create_new_structure()
            
            # Step 3: Move files to usage directory
            self._move_usage_files()
            
            # Step 4: Consolidate analysis documents
            self._consolidate_analysis_documents()
            
            # Step 5: Move voice samples
            self._move_voice_samples()
            
            # Step 6: Remove unnecessary directories and files
            self._remove_unnecessary_content()
            
            # Step 7: Create directory READMEs
            self._create_directory_readmes()
            
            # Step 8: Generate cleanup summary
            self._generate_cleanup_summary()
            
            logger.info("Documentation cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Documentation cleanup failed: {e}")
            raise
    
    def _create_backup(self):
        """Create backup of current documentation"""
        logger.info("Creating documentation backup")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        shutil.copytree(self.docs_dir, self.backup_dir)
        logger.info(f"Backup created at {self.backup_dir}")
    
    def _create_new_structure(self):
        """Create new documentation directory structure"""
        logger.info("Creating new documentation structure")
        
        new_dirs = [
            "usage",
            "analysis", 
            "api",
            "development"
        ]
        
        for dir_name in new_dirs:
            dir_path = self.docs_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def _move_usage_files(self):
        """Move usage-related files to usage directory"""
        logger.info("Moving usage files")
        
        usage_dir = self.docs_dir / "usage"
        
        for filename in self.files_to_move_to_usage:
            source = self.docs_dir / filename
            if source.exists():
                dest = usage_dir / filename
                shutil.move(str(source), str(dest))
                logger.info(f"Moved {filename} to usage/")
    
    def _consolidate_analysis_documents(self):
        """Consolidate analysis documents into analysis directory"""
        logger.info("Consolidating analysis documents")
        
        analysis_dir = self.docs_dir / "analysis"
        
        # Move directories to consolidate
        for old_dir, new_location in self.directories_to_consolidate.items():
            old_path = self.docs_dir / old_dir
            if old_path.exists():
                new_path = analysis_dir / old_dir
                shutil.move(str(old_path), str(new_path))
                logger.info(f"Moved {old_dir}/ to analysis/{old_dir}/")
        
        # Move standalone analysis files
        analysis_files = [
            "comprehensive_optimization_summary.md",
            "configuration_optimization_analysis.md", 
            "feature_implementation_analysis.md",
            "performance_analysis_results.md"
        ]
        
        for filename in analysis_files:
            source = self.docs_dir / filename
            if source.exists():
                dest = analysis_dir / filename
                shutil.move(str(source), str(dest))
                logger.info(f"Moved {filename} to analysis/")
    
    def _move_voice_samples(self):
        """Move voice samples to samples directory"""
        logger.info("Moving voice samples")
        
        voices_dir = self.docs_dir / "voices"
        samples_dir = Path("samples")
        
        if voices_dir.exists():
            # Create samples directory if it doesn't exist
            samples_dir.mkdir(exist_ok=True)
            
            # Move all voice files
            for voice_file in voices_dir.glob("*.mp3"):
                # Remove "sample" prefix from filename
                new_name = voice_file.name.replace("_sample", "")
                dest = samples_dir / new_name
                shutil.move(str(voice_file), str(dest))
                logger.info(f"Moved {voice_file.name} to samples/{new_name}")
            
            # Move README if it exists
            readme_path = voices_dir / "README.md"
            if readme_path.exists():
                shutil.move(str(readme_path), str(samples_dir / "README.md"))
            
            # Remove empty voices directory
            if voices_dir.exists() and not any(voices_dir.iterdir()):
                voices_dir.rmdir()
                logger.info("Removed empty voices directory")
    
    def _remove_unnecessary_content(self):
        """Remove unnecessary directories and files"""
        logger.info("Removing unnecessary content")
        
        # Remove directories
        for dir_name in self.directories_to_remove:
            dir_path = self.docs_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f"Removed directory: {dir_name}/")
        
        # Remove files
        for filename in self.files_to_remove:
            file_path = self.docs_dir / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed file: {filename}")
        
        # Remove empty benchmark directories
        benchmark_dirs = ["benchmark", "benchmark_results"]
        for dir_name in benchmark_dirs:
            dir_path = self.docs_dir / dir_name
            if dir_path.exists():
                # Move to analysis if not empty, otherwise remove
                if any(dir_path.iterdir()):
                    dest = self.docs_dir / "analysis" / dir_name
                    shutil.move(str(dir_path), str(dest))
                    logger.info(f"Moved {dir_name}/ to analysis/")
                else:
                    dir_path.rmdir()
                    logger.info(f"Removed empty directory: {dir_name}/")
    
    def _create_directory_readmes(self):
        """Create README files for each directory"""
        logger.info("Creating directory README files")
        
        readme_content = {
            "usage": {
                "title": "Usage Documentation",
                "description": "User guides, tutorials, and how-to documentation for the Kokoro ONNX TTS API.",
                "contents": [
                    "Quick start guides and setup instructions",
                    "Deployment and configuration guides", 
                    "API usage examples and tutorials",
                    "Troubleshooting and performance guides"
                ]
            },
            "analysis": {
                "title": "System Analysis",
                "description": "Technical analysis, audit reports, and system improvement documentation.",
                "contents": [
                    "Performance analysis and benchmarks",
                    "Code quality audits and improvements",
                    "Feature implementation analysis",
                    "System optimization reports"
                ]
            },
            "api": {
                "title": "API Documentation", 
                "description": "Technical API reference and integration documentation.",
                "contents": [
                    "API endpoint reference",
                    "Request/response schemas",
                    "Integration examples",
                    "Authentication and configuration"
                ]
            },
            "development": {
                "title": "Development Documentation",
                "description": "Documentation for developers working on the TTS system.",
                "contents": [
                    "Architecture and design documents",
                    "Development setup and guidelines",
                    "Testing and quality assurance",
                    "Contributing guidelines"
                ]
            }
        }
        
        for dir_name, info in readme_content.items():
            dir_path = self.docs_dir / dir_name
            if dir_path.exists():
                readme_path = dir_path / "README.md"
                
                content = f"# {info['title']}\n\n"
                content += f"{info['description']}\n\n"
                content += "## Contents\n\n"
                
                for item in info['contents']:
                    content += f"- {item}\n"
                
                content += "\n## Files in this Directory\n\n"
                
                # List actual files
                for file_path in sorted(dir_path.glob("*.md")):
                    if file_path.name != "README.md":
                        content += f"- [{file_path.name}](./{file_path.name})\n"
                
                # List subdirectories
                for subdir in sorted(dir_path.iterdir()):
                    if subdir.is_dir():
                        content += f"- [{subdir.name}/](./{subdir.name}/)\n"
                
                with open(readme_path, 'w') as f:
                    f.write(content)
                
                logger.info(f"Created README for {dir_name}/")
    
    def _generate_cleanup_summary(self):
        """Generate summary of cleanup actions"""
        logger.info("Generating cleanup summary")
        
        summary = {
            "cleanup_date": "2025-08-16",
            "actions_performed": [
                "Created backup of original documentation",
                "Reorganized directory structure",
                "Moved usage files to docs/usage/",
                "Consolidated analysis documents to docs/analysis/",
                "Moved voice samples to samples/ (removed 'sample' prefix)",
                "Removed unnecessary directories and files",
                "Created README files for each directory"
            ],
            "new_structure": {
                "docs/usage/": "User guides and tutorials",
                "docs/analysis/": "Technical analysis and reports", 
                "docs/api/": "API reference documentation",
                "docs/development/": "Developer documentation",
                "samples/": "Voice samples and audio examples"
            },
            "files_removed": list(self.files_to_remove),
            "directories_removed": list(self.directories_to_remove),
            "backup_location": str(self.backup_dir)
        }
        
        summary_path = self.docs_dir / "CLEANUP_SUMMARY.md"
        
        content = "# Documentation Cleanup Summary\n\n"
        content += f"**Date:** {summary['cleanup_date']}\n\n"
        content += "## Actions Performed\n\n"
        
        for action in summary['actions_performed']:
            content += f"- {action}\n"
        
        content += "\n## New Directory Structure\n\n"
        
        for path, description in summary['new_structure'].items():
            content += f"- **{path}** - {description}\n"
        
        content += f"\n## Backup Location\n\n"
        content += f"Original documentation backed up to: `{summary['backup_location']}`\n"
        
        with open(summary_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Cleanup summary saved to {summary_path}")

def main():
    """Main cleanup execution"""
    print("Documentation Cleanup and Consolidation")
    print("=" * 50)
    
    try:
        cleanup = DocumentationCleanup()
        cleanup.run_cleanup()
        
        print("\n✅ Documentation cleanup completed successfully!")
        print("\nNew structure:")
        print("- docs/usage/ - User guides and tutorials")
        print("- docs/analysis/ - Technical analysis and reports")
        print("- docs/api/ - API reference documentation") 
        print("- docs/development/ - Developer documentation")
        print("- samples/ - Voice samples and audio examples")
        print("\nBackup created at: docs_backup/")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        print(f"\n❌ Cleanup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
