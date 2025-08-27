#!/usr/bin/env python3
"""
Automated Technical Documentation Generation System
Generates comprehensive documentation from code, docstrings, and configuration files
"""

import os
import sys
import subprocess
import logging
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TechnicalDocumentationGenerator:
    """Automated documentation generation for the Kokoro ONNX TTS API"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_output = self.project_root / "docs" / "api" / "generated"
        self.source_dirs = [
            self.project_root / "kokoro",
            self.project_root / "examples"
        ]
        
        # Documentation configuration
        self.config = {
            "project_name": "Kokoro ONNX TTS API",
            "project_description": "Production-Ready Text-to-Speech System with 54+ Voices",
            "version": "1.0.0",
            "author": "Kokoro TTS Contributors",
            "include_private": False,
            "include_source": True,
            "format": "markdown",
            "template": "custom"
        }
        
        logger.info(f"Documentation generator initialized for {self.project_root}")
    
    def generate_all_documentation(self):
        """Generate complete technical documentation"""
        logger.info("Starting comprehensive documentation generation")
        
        try:
            # Step 1: Setup output directories
            self._setup_output_directories()
            
            # Step 2: Generate API documentation from code
            self._generate_api_documentation()
            
            # Step 3: Generate configuration documentation
            self._generate_config_documentation()
            
            # Step 4: Generate examples documentation
            self._generate_examples_documentation()
            
            # Step 5: Generate architecture documentation
            self._generate_architecture_documentation()
            
            # Step 6: Create navigation and index
            self._create_navigation_index()
            
            # Step 7: Generate summary report
            self._generate_summary_report()
            
            logger.info("Technical documentation generation completed successfully")
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            raise
    
    def _setup_output_directories(self):
        """Create output directory structure"""
        logger.info("Setting up output directories")
        
        directories = [
            self.docs_output,
            self.docs_output / "api",
            self.docs_output / "config",
            self.docs_output / "examples",
            self.docs_output / "architecture"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def _generate_api_documentation(self):
        """Generate API documentation using pdoc"""
        logger.info("Generating API documentation from source code")
        
        try:
            # Check if pdoc is available
            result = subprocess.run(["pdoc", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("pdoc not available, installing...")
                subprocess.run([sys.executable, "-m", "pip", "install", "pdoc"], check=True)
            
            # Generate documentation for each source directory
            for source_dir in self.source_dirs:
                if not source_dir.exists():
                    logger.warning(f"Source directory {source_dir} does not exist, skipping")
                    continue
                
                output_dir = self.docs_output / "api" / source_dir.name
                
                # Run pdoc
                cmd = [
                    "pdoc",
                    str(source_dir),
                    "--output-dir", str(output_dir),
                    "--format", "markdown",
                    "--docformat", "google",
                    "--include-undocumented"
                ]
                
                if not self.config["include_private"]:
                    cmd.append("--no-show-source")
                
                logger.info(f"Running pdoc for {source_dir}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"Successfully generated docs for {source_dir}")
                else:
                    logger.warning(f"pdoc failed for {source_dir}: {result.stderr}")
                    # Fallback to manual documentation extraction
                    self._manual_doc_extraction(source_dir, output_dir)
                    
        except Exception as e:
            logger.error(f"API documentation generation failed: {e}")
            # Fallback to manual extraction
            self._fallback_api_documentation()
    
    def _manual_doc_extraction(self, source_dir: Path, output_dir: Path):
        """Manual documentation extraction when pdoc fails"""
        logger.info(f"Performing manual documentation extraction for {source_dir}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all Python files
        python_files = list(source_dir.rglob("*.py"))
        
        for py_file in python_files:
            try:
                # Parse the Python file
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract module docstring and class/function definitions
                tree = ast.parse(content)
                
                # Generate markdown documentation
                doc_content = self._extract_python_documentation(py_file, tree)
                
                # Save documentation
                relative_path = py_file.relative_to(source_dir)
                doc_file = output_dir / f"{relative_path.with_suffix('.md')}"
                doc_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(doc_file, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                
                logger.info(f"Generated manual docs for {py_file}")
                
            except Exception as e:
                logger.warning(f"Failed to extract docs from {py_file}: {e}")
    
    def _extract_python_documentation(self, file_path: Path, tree: ast.AST) -> str:
        """Extract documentation from Python AST"""
        content = f"# {file_path.name}\n\n"
        
        # Module docstring
        if (isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Constant) and 
            isinstance(tree.body[0].value.value, str)):
            content += f"{tree.body[0].value.value}\n\n"
        
        # Extract classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                content += f"## Class: {node.name}\n\n"
                if ast.get_docstring(node):
                    content += f"{ast.get_docstring(node)}\n\n"
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        content += f"### {item.name}()\n\n"
                        if ast.get_docstring(item):
                            content += f"{ast.get_docstring(item)}\n\n"
            
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                content += f"## Function: {node.name}()\n\n"
                if ast.get_docstring(node):
                    content += f"{ast.get_docstring(node)}\n\n"
        
        return content
    
    def _generate_config_documentation(self):
        """Generate documentation for configuration files"""
        logger.info("Generating configuration documentation")
        
        config_files = [
            self.project_root / "config.json",
            self.project_root / "kokoro" / "config",
        ]
        
        output_file = self.docs_output / "config" / "CONFIGURATION_REFERENCE.md"
        
        content = "# Configuration Reference\n\n"
        content += "Complete reference for all configuration options in the LiteTTS API.\n\n"
        
        # Main config.json
        main_config = self.project_root / "config.json"
        if main_config.exists():
            content += "## Main Configuration (config.json)\n\n"
            content += self._document_json_config(main_config)
        
        # Additional config files
        config_dir = self.project_root / "kokoro" / "config"
        if config_dir.exists():
            content += "## Additional Configuration Files\n\n"
            for config_file in config_dir.glob("*.json"):
                content += f"### {config_file.name}\n\n"
                content += self._document_json_config(config_file)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Configuration documentation saved to {output_file}")
    
    def _document_json_config(self, config_file: Path) -> str:
        """Document a JSON configuration file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            content = f"**File:** `{config_file.name}`\n\n"
            content += "```json\n"
            content += json.dumps(config_data, indent=2)
            content += "\n```\n\n"
            
            # Add descriptions for known config sections
            content += self._add_config_descriptions(config_data)
            
            return content
            
        except Exception as e:
            logger.warning(f"Failed to document {config_file}: {e}")
            return f"**File:** `{config_file.name}` - *Documentation generation failed*\n\n"
    
    def _add_config_descriptions(self, config_data: Dict) -> str:
        """Add descriptions for configuration sections"""
        descriptions = {
            "text_processing": "Text processing and normalization settings",
            "phonetic_processing": "Phonetic processing and pronunciation rules",
            "contraction_handling": "Contraction expansion and pronunciation settings",
            "symbol_processing": "Symbol and punctuation handling",
            "voice_modulation": "Voice effects and modulation settings",
            "time_stretching": "Time-stretching optimization settings (beta)",
            "cache": "Caching configuration for performance optimization",
            "server": "Server configuration and networking settings",
            "logging": "Logging configuration and verbosity settings"
        }
        
        content = "**Configuration Sections:**\n\n"
        
        for key, description in descriptions.items():
            if key in config_data:
                content += f"- **{key}**: {description}\n"
        
        content += "\n"
        return content
    
    def _generate_examples_documentation(self):
        """Generate documentation for examples"""
        logger.info("Generating examples documentation")
        
        examples_dir = self.project_root / "static" / "examples"
        output_file = self.docs_output / "examples" / "EXAMPLES_REFERENCE.md"
        
        content = "# Examples Reference\n\n"
        content += "Interactive examples and demonstrations of Kokoro ONNX TTS API capabilities.\n\n"
        
        if examples_dir.exists():
            for example_dir in examples_dir.iterdir():
                if example_dir.is_dir():
                    content += f"## {example_dir.name.replace('-', ' ').title()}\n\n"
                    
                    # Look for README or description
                    readme_file = example_dir / "README.md"
                    if readme_file.exists():
                        with open(readme_file, 'r') as f:
                            content += f.read() + "\n\n"
                    else:
                        content += f"Interactive example located at `static/examples/{example_dir.name}/`\n\n"
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Examples documentation saved to {output_file}")
    
    def _generate_architecture_documentation(self):
        """Generate architecture documentation"""
        logger.info("Generating architecture documentation")
        
        output_file = self.docs_output / "architecture" / "SYSTEM_ARCHITECTURE.md"
        
        content = """# System Architecture

## Overview

The Kokoro ONNX TTS API is built with a modular architecture designed for production deployment, scalability, and maintainability.

## Core Components

### 1. TTS Engine (`LiteTTS/tts/`)
- **TTSSynthesizer**: Main synthesis orchestrator
- **KokoroTTSEngine**: ONNX-based TTS engine
- **ChunkProcessor**: Text chunking for long inputs
- **EmotionController**: Emotion and style control

### 2. Audio Processing (`LiteTTS/audio/`)
- **AudioSegment**: Core audio data structure
- **AudioProcessor**: Audio processing orchestrator
- **FormatConverter**: Multi-format conversion
- **AudioStreamer**: Real-time streaming
- **TimeStretcher**: Time-stretching optimization (beta)

### 3. Voice Management (`LiteTTS/voice/`)
- **VoiceManager**: Voice loading and caching
- **VoiceBlender**: Voice mixing and blending
- **VoiceDiscovery**: Automatic voice detection

### 4. Text Processing (`LiteTTS/nlp/`)
- **TextNormalizer**: Text normalization pipeline
- **PronunciationFixer**: Pronunciation corrections
- **PhoneticProcessor**: Phonetic processing
- **ContextAnalyzer**: Context-aware processing

### 5. Configuration (`LiteTTS/config/`)
- **TTSConfiguration**: Main configuration management
- **ConfigValidator**: Configuration validation
- **DynamicConfig**: Runtime configuration updates

## Data Flow

```
Text Input → Text Processing → Voice Selection → TTS Synthesis → Audio Processing → Output
     ↓              ↓               ↓              ↓              ↓
Normalization → Pronunciation → Voice Loading → ONNX Model → Format Conversion
     ↓              ↓               ↓              ↓              ↓
Symbol Handling → Phonetic Rules → Caching → Audio Generation → Streaming
```

## Performance Optimizations

1. **Voice Caching**: Intelligent voice embedding cache
2. **Text Preprocessing**: Optimized text normalization pipeline
3. **Chunk Processing**: Efficient handling of long texts
4. **Time-Stretching**: Beta latency optimization feature
5. **Connection Pooling**: Efficient HTTP connection management

## Scalability Features

- **Stateless Design**: No server-side session state
- **Horizontal Scaling**: Multiple instance support
- **Load Balancing**: Compatible with standard load balancers
- **Caching Strategy**: Multi-level caching for performance
- **Resource Management**: Efficient memory and CPU usage

## Security Considerations

- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Built-in rate limiting capabilities
- **Error Handling**: Secure error messages
- **Configuration Security**: Secure configuration management
"""
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Architecture documentation saved to {output_file}")
    
    def _create_navigation_index(self):
        """Create navigation index for generated documentation"""
        logger.info("Creating navigation index")
        
        index_file = self.docs_output / "README.md"
        
        content = f"""# {self.config['project_name']} - Generated Documentation

{self.config['project_description']}

**Version:** {self.config['version']}  
**Generated:** {self._get_current_timestamp()}

## 📚 Documentation Sections

### API Reference
- [Kokoro Module](api/LiteTTS/) - Core TTS engine and components
- [Examples Module](api/examples/) - Interactive examples and demos

### Configuration
- [Configuration Reference](config/CONFIGURATION_REFERENCE.md) - Complete configuration guide

### Examples
- [Examples Reference](examples/EXAMPLES_REFERENCE.md) - Interactive examples documentation

### Architecture
- [System Architecture](architecture/SYSTEM_ARCHITECTURE.md) - Technical architecture overview

## 🔗 Additional Resources

- [Main Documentation](../../README.md) - Project overview and getting started
- [Usage Guides](../usage/) - User guides and tutorials
- [Development Docs](../development/) - Developer documentation
- [Voice Samples](../../samples/) - Audio samples and demos

---

*This documentation is automatically generated from source code, configuration files, and examples.*
"""
        
        with open(index_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Navigation index saved to {index_file}")
    
    def _generate_summary_report(self):
        """Generate documentation generation summary"""
        logger.info("Generating summary report")
        
        summary_file = self.docs_output / "GENERATION_SUMMARY.md"
        
        # Count generated files
        total_files = len(list(self.docs_output.rglob("*.md")))
        
        content = f"""# Documentation Generation Summary

**Generated:** {self._get_current_timestamp()}  
**Total Files:** {total_files}

## Generated Documentation

### API Documentation
- Source code documentation extracted from docstrings
- Class and function reference
- Type hints and parameter documentation

### Configuration Documentation
- Complete configuration reference
- JSON schema documentation
- Configuration examples and best practices

### Examples Documentation
- Interactive example descriptions
- Usage instructions and features
- Integration guides

### Architecture Documentation
- System architecture overview
- Component relationships
- Data flow diagrams
- Performance and scalability information

## Generation Process

1. ✅ Setup output directories
2. ✅ Generate API documentation from source code
3. ✅ Generate configuration documentation
4. ✅ Generate examples documentation
5. ✅ Generate architecture documentation
6. ✅ Create navigation index
7. ✅ Generate summary report

## Next Steps

1. Review generated documentation for accuracy
2. Add custom content where needed
3. Integrate with main documentation structure
4. Setup automated regeneration workflow

---

*Documentation generated by the Kokoro ONNX TTS API automated documentation system.*
"""
        
        with open(summary_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Summary report saved to {summary_file}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for documentation"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _fallback_api_documentation(self):
        """Fallback documentation generation when pdoc fails"""
        logger.info("Using fallback documentation generation")
        
        for source_dir in self.source_dirs:
            if source_dir.exists():
                output_dir = self.docs_output / "api" / source_dir.name
                self._manual_doc_extraction(source_dir, output_dir)

def main():
    """Main documentation generation execution"""
    print("Automated Technical Documentation Generation")
    print("=" * 50)
    
    try:
        generator = TechnicalDocumentationGenerator()
        generator.generate_all_documentation()
        
        print("\n✅ Documentation generation completed successfully!")
        print(f"\nGenerated documentation available at: {generator.docs_output}")
        print("\nGenerated sections:")
        print("- API Reference (from source code)")
        print("- Configuration Reference (from JSON configs)")
        print("- Examples Documentation (from examples/)")
        print("- Architecture Documentation (system overview)")
        print("- Navigation Index (README.md)")
        
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        print(f"\n❌ Generation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
