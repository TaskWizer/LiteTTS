#!/usr/bin/env python3
"""
Create comprehensive README files for all directories
"""

import os
import logging
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectoryReadmeCreator:
    """Creates comprehensive README files for all directories"""
    
    def __init__(self):
        self.project_root = Path(".")
        
        # Define README content for each directory
        self.readme_templates = {
            "kokoro": {
                "title": "Kokoro TTS Core Engine",
                "description": "Core TTS engine implementation with ONNX runtime, voice management, and audio processing.",
                "sections": [
                    "## Architecture\n\nThe Kokoro TTS engine is organized into modular components:",
                    "- **Audio Processing** - Audio format conversion, streaming, and effects",
                    "- **Voice Management** - Voice loading, caching, and blending",
                    "- **Text Processing** - NLP pipeline with pronunciation fixes",
                    "- **TTS Engine** - Core synthesis with ONNX runtime",
                    "- **Configuration** - Centralized configuration management",
                    "- **Models** - Data structures and model definitions"
                ]
            },
            "LiteTTS/audio": {
                "title": "Audio Processing System",
                "description": "Comprehensive audio processing pipeline with format conversion, streaming, and effects.",
                "sections": [
                    "## Components\n",
                    "- **AudioSegment** - Core audio data structure with processing methods",
                    "- **AudioProcessor** - Main audio processing orchestrator", 
                    "- **FormatConverter** - Multi-format audio conversion (WAV, MP3, OGG, FLAC)",
                    "- **AudioStreamer** - Chunked streaming for real-time playback",
                    "- **TimeStretcher** - Beta time-stretching optimization feature"
                ]
            },
            "LiteTTS/voice": {
                "title": "Voice Management System", 
                "description": "Advanced voice loading, caching, and blending system with 54+ voice support.",
                "sections": [
                    "## Features\n",
                    "- **Dynamic Discovery** - Automatic voice detection and loading",
                    "- **Intelligent Caching** - Memory-efficient voice embedding cache",
                    "- **Voice Blending** - Mix multiple voices with custom weights",
                    "- **Metadata Management** - Voice statistics and usage tracking"
                ]
            },
            "LiteTTS/nlp": {
                "title": "Natural Language Processing Pipeline",
                "description": "Advanced text processing with pronunciation fixes, phonetic processing, and natural speech enhancement.",
                "sections": [
                    "## Processing Pipeline\n",
                    "1. **Text Normalization** - Currency, dates, URLs, symbols",
                    "2. **Phonetic Processing** - RIME AI notation, IPA support",
                    "3. **Pronunciation Fixes** - Contractions, proper names, technical terms",
                    "4. **Prosody Analysis** - Emotion detection and intonation",
                    "5. **Context Adaptation** - Homograph resolution and context awareness"
                ]
            },
            "LiteTTS/tts": {
                "title": "TTS Synthesis Engine",
                "description": "Core text-to-speech synthesis with ONNX runtime and advanced features.",
                "sections": [
                    "## Components\n",
                    "- **TTSSynthesizer** - Main synthesis orchestrator",
                    "- **KokoroTTSEngine** - ONNX-based TTS engine",
                    "- **ChunkProcessor** - Text chunking for long inputs",
                    "- **EmotionController** - Emotion and style control"
                ]
            },
            "LiteTTS/config": {
                "title": "Configuration Management",
                "description": "Centralized configuration system with JSON configs and runtime management.",
                "sections": [
                    "## Configuration Files\n",
                    "- **config.json** - Main application configuration",
                    "- **pronunciation_*.json** - Pronunciation rules and overrides",
                    "- **tokenizer*.json** - Tokenizer configuration",
                    "- **openapi.json** - API specification"
                ]
            },
            "LiteTTS/tests": {
                "title": "Test Suite",
                "description": "Comprehensive test suite covering all TTS functionality with performance regression testing.",
                "sections": [
                    "## Test Organization\n",
                    "- **root_tests/** - Original root-level test files",
                    "- **LiteTTS/scripts/** - Test and debug scripts",
                    "- **Integration Tests** - End-to-end API testing",
                    "- **Performance Tests** - RTF and latency benchmarks",
                    "- **Pronunciation Tests** - Text processing validation"
                ]
            },
            "examples": {
                "title": "Usage Examples and Demos",
                "description": "Interactive examples, demos, and integration samples for the Kokoro ONNX TTS API.",
                "sections": [
                    "## Available Examples\n",
                    "- **Voice Studio** - Interactive voice testing interface",
                    "- **Audio Suite** - Comprehensive audio processing demos",
                    "- **Voice Chat** - Real-time voice chat integration",
                    "- **Sample Generator** - Batch voice sample generation",
                    "- **Pronunciation Validator** - Text processing validation tool"
                ]
            },
            "scripts": {
                "title": "Utility Scripts",
                "description": "Development, deployment, and maintenance scripts for the TTS system.",
                "sections": [
                    "## Script Categories\n",
                    "- **Deployment** - Production deployment and setup",
                    "- **Performance** - Benchmarking and optimization",
                    "- **Maintenance** - System cleanup and organization",
                    "- **Development** - Development utilities and helpers"
                ]
            },
            "samples": {
                "title": "Voice Samples and Audio Examples",
                "description": "Collection of voice samples demonstrating the capabilities of all 54+ available voices.",
                "sections": [
                    "## Voice Categories\n",
                    "- **American Female (af_*)** - Various American female voices",
                    "- **American Male (am_*)** - Various American male voices", 
                    "- **British Female/Male (bf_*, bm_*)** - British accents",
                    "- **International (ef_*, em_*, etc.)** - Global voice collection",
                    "- **Specialized** - Character and unique voices"
                ]
            }
        }
        
        logger.info("Directory README creator initialized")
    
    def create_all_readmes(self):
        """Create README files for all directories"""
        logger.info("Creating comprehensive README files")
        
        try:
            # Create README for each defined directory
            for dir_path, template in self.readme_templates.items():
                self._create_readme(dir_path, template)
            
            # Create CONTRIBUTIONS.md
            self._create_contributions_file()
            
            # Create LICENSE file
            self._create_license_file()
            
            # Update CHANGELOG.md
            self._update_changelog()
            
            logger.info("All README files created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create README files: {e}")
            raise
    
    def _create_readme(self, dir_path: str, template: Dict):
        """Create README for a specific directory"""
        directory = Path(dir_path)
        
        if not directory.exists():
            logger.warning(f"Directory {dir_path} does not exist, skipping")
            return
        
        readme_path = directory / "README.md"
        
        content = f"# {template['title']}\n\n"
        content += f"{template['description']}\n\n"
        
        # Add template sections
        for section in template['sections']:
            content += f"{section}\n"
        
        content += "\n## Directory Contents\n\n"
        
        # List actual files and directories
        items = []
        for item in sorted(directory.iterdir()):
            if item.name.startswith('.') or item.name == 'README.md':
                continue
                
            if item.is_file():
                items.append(f"- **{item.name}** - {self._get_file_description(item)}")
            elif item.is_dir():
                items.append(f"- **{item.name}/** - {self._get_dir_description(item)}")
        
        if items:
            content += "\n".join(items) + "\n"
        else:
            content += "*(Directory contents will be populated as development progresses)*\n"
        
        # Add navigation
        content += "\n## Navigation\n\n"
        content += "- [← Back to Main README](../README.md)\n"
        content += "- [📚 Documentation](../docs/README.md)\n"
        content += "- [🎵 Voice Samples](../samples/README.md)\n"
        content += "- [💡 Examples](../examples/README.md)\n"
        
        with open(readme_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Created README for {dir_path}")
    
    def _get_file_description(self, file_path: Path) -> str:
        """Get description for a file based on its name and extension"""
        name = file_path.name.lower()
        
        descriptions = {
            '__init__.py': 'Package initialization',
            'app.py': 'Main application entry point',
            'config.py': 'Configuration management',
            'models.py': 'Data models and structures',
            'processor.py': 'Main processing logic',
            'engine.py': 'Core engine implementation',
            'synthesizer.py': 'TTS synthesis orchestrator',
            'manager.py': 'Resource management',
            'controller.py': 'Control logic',
            'server.py': 'Server implementation',
            'client.py': 'Client implementation',
            'utils.py': 'Utility functions',
            'helpers.py': 'Helper functions',
            'constants.py': 'Application constants',
            'exceptions.py': 'Custom exceptions',
            'validation.py': 'Input validation',
            'logging_config.py': 'Logging configuration',
            'startup.py': 'Application startup logic'
        }
        
        if name in descriptions:
            return descriptions[name]
        elif name.endswith('.json'):
            return 'JSON configuration file'
        elif name.endswith('.py'):
            return 'Python module'
        elif name.endswith('.md'):
            return 'Documentation file'
        elif name.endswith('.yml') or name.endswith('.yaml'):
            return 'YAML configuration'
        elif name.endswith('.txt'):
            return 'Text file'
        else:
            return 'Project file'
    
    def _get_dir_description(self, dir_path: Path) -> str:
        """Get description for a directory based on its name"""
        name = dir_path.name.lower()
        
        descriptions = {
            'audio': 'Audio processing components',
            'voice': 'Voice management system',
            'nlp': 'Natural language processing',
            'tts': 'Text-to-speech engine',
            'config': 'Configuration files',
            'models': 'Data models and ML models',
            'tests': 'Test suite',
            'scripts': 'Utility scripts',
            'examples': 'Usage examples',
            'docs': 'Documentation',
            'samples': 'Audio samples',
            'cache': 'Cache storage',
            'logs': 'Log files',
            'temp': 'Temporary files',
            'api': 'API components',
            'utils': 'Utility modules',
            'core': 'Core functionality',
            'features': 'Feature implementations',
            'monitoring': 'Monitoring and metrics',
            'performance': 'Performance optimization',
            'benchmarks': 'Benchmark code',
            'root_tests': 'Root-level test files'
        }
        
        return descriptions.get(name, 'Project directory')
    
    def _create_contributions_file(self):
        """Create CONTRIBUTIONS.md file"""
        content = """# Contributing to Kokoro ONNX TTS API

Thank you for your interest in contributing to the Kokoro ONNX TTS API! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Make your changes** with clear, descriptive commits
5. **Test your changes** thoroughly
6. **Submit a pull request** with a clear description

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/kokoro_onnx_tts_api.git
cd kokoro_onnx_tts_api

# Install dependencies
uv sync

# Run tests
python -m pytest LiteTTS/tests/

# Start development server
python LiteTTS/start_server.py
```

## 🧪 Testing

- **Run all tests**: `python -m pytest LiteTTS/tests/`
- **Performance tests**: `python LiteTTS/tests/LiteTTS/scripts/benchmark_tts.py`
- **Integration tests**: `python LiteTTS/tests/test_api_endpoints.py`

## 📝 Code Style

- Follow **PEP 8** Python style guidelines
- Use **type hints** for function parameters and return values
- Write **clear docstrings** for all public functions and classes
- Keep **line length under 100 characters**

## 🐛 Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **System information** (OS, Python version, etc.)
- **Relevant logs** or error messages

## 💡 Feature Requests

For new features:

- **Check existing issues** to avoid duplicates
- **Describe the use case** and benefits
- **Provide implementation suggestions** if possible
- **Consider backward compatibility**

## 🔧 Pull Request Guidelines

- **One feature per PR** - keep changes focused
- **Update tests** for any new functionality
- **Update documentation** as needed
- **Ensure all tests pass** before submitting
- **Write clear commit messages**

## 📚 Documentation

- Update relevant **README files** for new features
- Add **API documentation** for new endpoints
- Include **usage examples** where appropriate
- Update **CHANGELOG.md** with your changes

## 🏷️ Commit Message Format

```
type(scope): brief description

Longer description if needed

- List any breaking changes
- Reference related issues (#123)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Documentation** - Check the `docs/` directory

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
"""
        
        with open("CONTRIBUTIONS.md", 'w') as f:
            f.write(content)
        
        logger.info("Created CONTRIBUTIONS.md")
    
    def _create_license_file(self):
        """Create LICENSE file with MIT license"""
        content = """MIT License

Copyright (c) 2025 Kokoro ONNX TTS API Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        with open("LICENSE", 'w') as f:
            f.write(content)
        
        logger.info("Created LICENSE file")
    
    def _update_changelog(self):
        """Update CHANGELOG.md with recent changes"""
        changelog_path = Path("docs/CHANGELOG.md")
        
        if changelog_path.exists():
            # Read existing changelog
            with open(changelog_path, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        
        # Add new entry for current changes
        new_entry = """## [1.0.0] - 2025-08-16

### Added
- ✨ **Time-Stretching Optimization** - Beta feature for improved latency
- 📝 **Comprehensive Text Processing Configuration** - Expanded config.json with detailed options
- 🗂️ **Repository Structure Reorganization** - Production-ready directory structure
- 📚 **Documentation Cleanup** - Consolidated and organized all documentation
- 📋 **Comprehensive README Files** - Added README files for all directories
- 🤝 **CONTRIBUTIONS.md** - Contributing guidelines for developers
- 📄 **LICENSE** - MIT license for open source distribution

### Changed
- 🔄 **Merged test directories** - Consolidated tests into LiteTTS/tests/
- 📁 **Moved voice samples** - Relocated to samples/ directory with clean naming
- ⚙️ **Centralized JSON configs** - Moved all configs to LiteTTS/config/
- 🧹 **Cleaned documentation** - Removed outdated and redundant files

### Technical Improvements
- 🎯 **Enhanced phonetic processing** - RIME AI integration and pronunciation fixes
- 🔧 **Advanced symbol processing** - Improved handling of punctuation and special characters
- 💬 **Better contraction handling** - Natural pronunciation rules for contractions
- 🌐 **Improved URL processing** - Natural web address pronunciation
- 💰 **Enhanced currency processing** - Better financial data pronunciation
- 📅 **Advanced date/time processing** - Natural date and time pronunciation

### Performance
- ⚡ **Time-stretching optimization** - Experimental feature for reduced latency
- 📊 **Performance regression testing** - Automated testing framework
- 🧪 **Comprehensive test suite** - Extensive validation and edge case testing

"""
        
        # Insert new entry after the header
        lines = existing_content.split('\n')
        header_end = 2  # After "# Changelog" and description
        
        new_lines = lines[:header_end] + new_entry.split('\n') + lines[header_end:]
        
        with open(changelog_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        logger.info("Updated CHANGELOG.md")

def main():
    """Main execution"""
    print("Creating Comprehensive Directory README Files")
    print("=" * 50)
    
    try:
        creator = DirectoryReadmeCreator()
        creator.create_all_readmes()
        
        print("\n✅ All README files created successfully!")
        print("\nFiles created/updated:")
        print("- README.md files in all major directories")
        print("- CONTRIBUTIONS.md - Contributing guidelines")
        print("- LICENSE - MIT license")
        print("- docs/CHANGELOG.md - Updated with recent changes")
        
    except Exception as e:
        logger.error(f"Failed to create README files: {e}")
        print(f"\n❌ Failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
