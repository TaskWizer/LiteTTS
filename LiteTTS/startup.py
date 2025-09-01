#!/usr/bin/env python3
"""
Startup validation and initialization for LiteTTS
"""

import logging
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import asyncio

from .config import config
from .logging_config import setup_logging, log_system_info
from .exceptions import ConfigurationError, ModelError

logger = logging.getLogger(__name__)


class StartupValidator:
    """Validates system requirements and configuration at startup"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_python_version(self) -> bool:
        """Validate Python version requirements"""
        min_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < min_version:
            self.errors.append(
                f"Python {min_version[0]}.{min_version[1]}+ required, "
                f"but {current_version[0]}.{current_version[1]} found"
            )
            return False
        
        logger.info(f"✅ Python version: {sys.version}")
        return True
    
    def validate_dependencies(self) -> bool:
        """Validate required dependencies are installed"""
        required_packages = [
            ('fastapi', 'FastAPI'),
            ('uvicorn', 'Uvicorn'),
            ('numpy', 'NumPy'),
            ('onnxruntime', 'ONNX Runtime'),
            ('pydantic', 'Pydantic'),
        ]
        
        optional_packages = [
            ('torch', 'PyTorch (for CUDA support)'),
            ('psutil', 'psutil (for system monitoring)'),
        ]
        
        missing_required = []
        missing_optional = []
        
        for package, description in required_packages:
            try:
                __import__(package)
                logger.debug(f"✅ {description} available")
            except ImportError:
                missing_required.append(description)
        
        for package, description in optional_packages:
            try:
                __import__(package)
                logger.debug(f"✅ {description} available")
            except ImportError:
                missing_optional.append(description)
                self.warnings.append(f"Optional dependency missing: {description}")
        
        if missing_required:
            self.errors.append(f"Missing required dependencies: {', '.join(missing_required)}")
            return False
        
        if missing_optional:
            logger.warning(f"Missing optional dependencies: {', '.join(missing_optional)}")
        
        return True
    
    def validate_directories(self) -> bool:
        """Validate required directories exist or can be created"""
        directories = [
            Path(config.tts.model_path).parent,
            Path(config.tts.voices_path).parent,
        ]
        
        # Add log directory if file logging is enabled
        if config.logging.file_path:
            directories.append(Path(config.logging.file_path).parent)
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"✅ Directory available: {directory}")
            except Exception as e:
                self.errors.append(f"Cannot create directory {directory}: {e}")
                return False
        
        return True
    
    def validate_model_files(self) -> bool:
        """Validate model files exist or can be downloaded"""
        model_path = Path(config.tts.model_path)
        voices_path = Path(config.tts.voices_path)
        
        if not model_path.exists():
            self.warnings.append(f"Model file not found: {model_path} (will be downloaded)")
        else:
            logger.info(f"✅ Model file found: {model_path}")
        
        if not voices_path.exists():
            self.warnings.append(f"Voices file not found: {voices_path} (will be downloaded)")
        else:
            logger.info(f"✅ Voices file found: {voices_path}")
        
        return True
    
    def validate_device_availability(self) -> bool:
        """Validate device (CPU/CUDA) availability"""
        if config.tts.device == "cuda":
            try:
                import torch
                if not torch.cuda.is_available():
                    self.warnings.append("CUDA requested but not available, falling back to CPU")
                    config.tts.device = "cpu"
                else:
                    logger.info(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            except ImportError:
                self.warnings.append("CUDA requested but PyTorch not available, falling back to CPU")
                config.tts.device = "cpu"
        
        logger.info(f"✅ Using device: {config.tts.device}")
        return True
    
    def validate_network_ports(self) -> bool:
        """Validate network port availability"""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((config.api.host, config.api.port))
                logger.info(f"✅ Port {config.api.port} available")
                return True
        except OSError as e:
            if e.errno == 98:  # Address already in use
                self.warnings.append(f"Port {config.api.port} already in use")
            else:
                self.errors.append(f"Cannot bind to {config.api.host}:{config.api.port}: {e}")
                return False
        
        return True
    
    def validate_configuration(self) -> bool:
        """Validate configuration settings"""
        return config.validate()
    
    def run_all_validations(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks"""
        logger.info("🔍 Running startup validations...")
        
        validations = [
            ("Python version", self.validate_python_version),
            ("Dependencies", self.validate_dependencies),
            ("Directories", self.validate_directories),
            ("Model files", self.validate_model_files),
            ("Device availability", self.validate_device_availability),
            ("Network ports", self.validate_network_ports),
            ("Configuration", self.validate_configuration),
        ]
        
        all_passed = True
        for name, validation_func in validations:
            try:
                if not validation_func():
                    all_passed = False
                    logger.error(f"❌ {name} validation failed")
                else:
                    logger.debug(f"✅ {name} validation passed")
            except Exception as e:
                all_passed = False
                self.errors.append(f"{name} validation error: {e}")
                logger.error(f"❌ {name} validation error: {e}")
        
        return all_passed, self.errors, self.warnings


async def initialize_system() -> bool:
    """Initialize the Kokoro TTS system"""
    logger.info("🚀 Initializing Kokoro ONNX TTS API...")
    
    try:
        # Set up logging first
        setup_logging(
            level=config.logging.level,
            file_path=config.logging.file_path,
            max_file_size=config.logging.max_file_size,
            backup_count=config.logging.backup_count,
            json_format=False,  # Can be made configurable
        )
        
        # Log system information
        log_system_info()
        
        # Run startup validations
        validator = StartupValidator()
        success, errors, warnings = validator.run_all_validations()
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"⚠️  {warning}")
        
        # Handle errors
        if errors:
            logger.error("❌ Startup validation failed:")
            for error in errors:
                logger.error(f"   • {error}")
            raise ConfigurationError("Startup validation failed", details={"errors": errors})
        
        logger.info("✅ System initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        raise


def create_startup_script():
    """Create a standalone startup script for testing"""
    script_content = '''#!/usr/bin/env python3
"""
Standalone startup validation script for Kokoro ONNX TTS API
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import LiteTTS
sys.path.insert(0, str(Path(__file__).parent.parent))

from LiteTTS.startup import initialize_system

async def main():
    """Main startup function"""
    try:
        await initialize_system()
        print("✅ Kokoro ONNX TTS API is ready to start!")
        return 0
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
'''
    
    script_path = Path("LiteTTS/scripts/validate_startup.py")
    script_path.parent.mkdir(exist_ok=True)
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    
    logger.info(f"Created startup validation script: {script_path}")


if __name__ == "__main__":
    # Run initialization if called directly
    asyncio.run(initialize_system())