# Configuration package for LiteTTS

# Import from the main config module to maintain compatibility
import sys
from pathlib import Path

# Add the parent directory to path to import from config.py
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import ConfigManager, config
except ImportError:
    # Fallback: try importing from the config.py file directly
    import importlib.util
    config_file = Path(__file__).parent.parent / "config.py"
    spec = importlib.util.spec_from_file_location("config", config_file)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    ConfigManager = config_module.ConfigManager
    config = config_module.config

# Also expose the robust config loader
from .robust_config_loader import RobustConfigurationLoader, load_and_apply_configuration
