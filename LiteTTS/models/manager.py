#!/usr/bin/env python3
"""
Model management system for Kokoro ONNX TTS API with multi-model support
"""

import os
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Information about a model variant"""
    name: str
    path: str
    size: int
    sha: str
    download_url: str
    variant_type: str  # e.g., "base", "fp16", "quantized"
    description: str = ""
    backend_type: str = "onnx"  # "onnx", "gguf"
    quantization_level: Optional[str] = None  # "Q4", "Q5", "Q8", "F16", etc.

@dataclass
class DownloadProgress:
    """Download progress information"""
    filename: str
    downloaded_bytes: int
    total_bytes: int
    percentage: float
    speed_mbps: float = 0.0

class ModelManager:
    """Manages ONNX model variants with dynamic discovery and caching"""
    
    def __init__(self, models_dir: str = "LiteTTS/models", config=None):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration with defensive null checks
        self.config = config
        if config and hasattr(config, 'repository') and config.repository:
            self.hf_repo = getattr(config.repository, 'huggingface_repo', 'onnx-community/Kokoro-82M-v1.0-ONNX')
            self.base_url = getattr(config.repository, 'base_url', 'https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main')
            self.models_path = getattr(config.repository, 'models_path', 'onnx')
        else:
            logger.warning("❌ Repository configuration not available - using defaults")
            self.hf_repo = 'onnx-community/Kokoro-82M-v1.0-ONNX'
            self.base_url = 'https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main'
            self.models_path = 'onnx'

        if config and hasattr(config, 'model') and config.model:
            self.available_variants = getattr(config.model, 'available_variants', ['model_q4.onnx'])
            self.default_variant = getattr(config.model, 'default_variant', 'model_q4.onnx')
            self.auto_discovery = getattr(config.model, 'auto_discovery', True)
            self.cache_models = getattr(config.model, 'cache_models', True)
        else:
            logger.warning("❌ Model configuration not available - using defaults")
            self.available_variants = [
                "model.onnx", "model_fp16.onnx", "model_q4.onnx",
                "model_q4f16.onnx", "model_q8f16.onnx", "model_quantized.onnx",
                "model_uint8.onnx", "model_uint8f16.onnx"
            ]
            self.default_variant = "model_q4.onnx"
            self.auto_discovery = True
            self.cache_models = True

        # GGUF repository configuration
        self.gguf_repo = "mmwillet2/Kokoro_GGUF"
        self.gguf_base_url = "https://huggingface.co/mmwillet2/Kokoro_GGUF/resolve/main"
        self.gguf_variants = [
            "Kokoro_espeak.gguf", "Kokoro_espeak_F16.gguf", "Kokoro_espeak_Q4.gguf",
            "Kokoro_espeak_Q5.gguf", "Kokoro_espeak_Q8.gguf",
            "Kokoro_no_espeak.gguf", "Kokoro_no_espeak_F16.gguf", "Kokoro_no_espeak_Q4.gguf",
            "Kokoro_no_espeak_Q5.gguf", "Kokoro_no_espeak_Q8.gguf"
        ]
        self.default_gguf_variant = "Kokoro_espeak_Q4.gguf"  # Match Q4 quantization level
        
        # Cache for discovered models
        self.discovered_models: Dict[str, ModelInfo] = {}
        self.discovery_cache_file = self.models_dir / "model_discovery_cache.json"
        self.cache_expiry_hours = 24
        
        # Load cached discovery data
        self._load_discovery_cache()
        
        # Discover models if cache is empty or expired
        if self.auto_discovery and (not self.discovered_models or self._is_cache_expired()):
            self.discover_models_from_huggingface()
            self.discover_gguf_models_from_huggingface()
    
    def _load_discovery_cache(self) -> None:
        """Load discovery cache from JSON file"""
        if not self.discovery_cache_file.exists():
            return
        
        try:
            with open(self.discovery_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            if 'models' in cache_data and 'timestamp' in cache_data:
                self.discovered_models = {
                    name: ModelInfo(**info)
                    for name, info in cache_data['models'].items()
                }
                logger.info(f"Loaded model discovery cache with {len(self.discovered_models)} models")
        
        except Exception as e:
            logger.warning(f"Failed to load model discovery cache: {e}")
            self.discovered_models = {}
    
    def _save_discovery_cache(self) -> None:
        """Save discovery cache to JSON file"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'models': {
                    name: {
                        'name': info.name,
                        'path': info.path,
                        'size': info.size,
                        'sha': info.sha,
                        'download_url': info.download_url,
                        'variant_type': info.variant_type,
                        'description': info.description
                    }
                    for name, info in self.discovered_models.items()
                }
            }
            
            with open(self.discovery_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Saved model discovery cache with {len(self.discovered_models)} models")
        
        except Exception as e:
            logger.error(f"Failed to save model discovery cache: {e}")
    
    def _is_cache_expired(self) -> bool:
        """Check if discovery cache is expired"""
        if not self.discovery_cache_file.exists():
            return True
        
        try:
            with open(self.discovery_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            if 'timestamp' not in cache_data:
                return True
            
            cache_age_hours = (time.time() - cache_data['timestamp']) / 3600
            return cache_age_hours > self.cache_expiry_hours
        
        except Exception:
            return True
    
    def discover_models_from_huggingface(self) -> bool:
        """Discover all model files from HuggingFace repository"""
        logger.info(f"Discovering models from HuggingFace repository: {self.hf_repo}")
        
        try:
            # Get repository tree from HuggingFace API
            tree_url = f"https://huggingface.co/api/models/{self.hf_repo}/tree/main/{self.models_path}"
            response = requests.get(tree_url, timeout=30)
            response.raise_for_status()
            
            repo_data = response.json()
            model_files = []
            
            # Find all .onnx files
            for item in repo_data:
                if (item.get('type') == 'file' and 
                    item.get('path', '').endswith('.onnx')):
                    model_files.append(item)
            
            # Process discovered model files
            self.discovered_models = {}
            for file_info in model_files:
                model_name = Path(file_info['path']).name
                
                # Determine variant type
                variant_type = self._determine_variant_type(model_name)
                
                # For LFS files, use the actual file hash from lfs.oid
                lfs_info = file_info.get('lfs', {})
                actual_hash = lfs_info.get('oid', file_info.get('oid', ''))
                actual_size = lfs_info.get('size', file_info.get('size', 0))
                
                model_info = ModelInfo(
                    name=model_name,
                    path=file_info['path'],
                    size=actual_size,
                    sha=actual_hash,
                    download_url=f"{self.base_url}/{file_info['path']}",
                    variant_type=variant_type,
                    description=self._get_variant_description(variant_type),
                    backend_type="onnx",
                    quantization_level=self._extract_quantization_level(model_name)
                )
                
                self.discovered_models[model_name] = model_info
            
            logger.info(f"Discovered {len(self.discovered_models)} model files from HuggingFace")
            
            # Save to cache
            if self.cache_models:
                self._save_discovery_cache()
            return True
        
        except Exception as e:
            logger.error(f"Failed to discover models from HuggingFace: {e}")
            return False

    def discover_gguf_models_from_huggingface(self) -> bool:
        """Discover GGUF model files from HuggingFace repository"""
        logger.info(f"Discovering GGUF models from HuggingFace repository: {self.gguf_repo}")

        try:
            # Get repository tree from HuggingFace API
            tree_url = f"https://huggingface.co/api/models/{self.gguf_repo}/tree/main"
            response = requests.get(tree_url, timeout=30)
            response.raise_for_status()

            repo_data = response.json()
            gguf_files = []

            # Find all .gguf files
            for item in repo_data:
                if (item.get('type') == 'file' and
                    item.get('path', '').endswith('.gguf')):
                    gguf_files.append(item)

            # Process discovered GGUF model files
            for file_info in gguf_files:
                model_name = Path(file_info['path']).name

                # Determine variant type for GGUF
                variant_type = self._determine_gguf_variant_type(model_name)

                # For LFS files, use the actual file hash from lfs.oid
                lfs_info = file_info.get('lfs', {})
                actual_hash = lfs_info.get('oid', file_info.get('oid', ''))
                actual_size = lfs_info.get('size', file_info.get('size', 0))

                model_info = ModelInfo(
                    name=model_name,
                    path=file_info['path'],
                    size=actual_size,
                    sha=actual_hash,
                    download_url=f"{self.gguf_base_url}/{file_info['path']}",
                    variant_type=variant_type,
                    description=self._get_gguf_variant_description(variant_type, model_name),
                    backend_type="gguf",
                    quantization_level=self._extract_gguf_quantization_level(model_name)
                )

                self.discovered_models[model_name] = model_info

            logger.info(f"Discovered {len(gguf_files)} GGUF model files from HuggingFace")

            # Save to cache
            if self.cache_models:
                self._save_discovery_cache()
            return True

        except Exception as e:
            logger.error(f"Failed to discover GGUF models from HuggingFace: {e}")
            return False
    
    def _determine_variant_type(self, model_name: str) -> str:
        """Determine the variant type from model filename"""
        name_lower = model_name.lower()
        
        if "fp16" in name_lower:
            return "fp16"
        elif "q4f16" in name_lower:
            return "q4f16"
        elif "q4" in name_lower:
            return "q4"
        elif "q8f16" in name_lower:
            return "q8f16"
        elif "uint8f16" in name_lower:
            return "uint8f16"
        elif "uint8" in name_lower:
            return "uint8"
        elif "quantized" in name_lower:
            return "quantized"
        elif name_lower == "model.onnx":
            return "base"
        else:
            return "unknown"

    def _determine_gguf_variant_type(self, model_name: str) -> str:
        """Determine the variant type from GGUF model filename"""
        name_lower = model_name.lower()

        if "f16" in name_lower:
            return "f16"
        elif "q4" in name_lower:
            return "q4"
        elif "q5" in name_lower:
            return "q5"
        elif "q8" in name_lower:
            return "q8"
        elif "espeak" in name_lower and "no_espeak" not in name_lower:
            return "espeak_base"
        elif "no_espeak" in name_lower:
            return "no_espeak_base"
        else:
            return "gguf_unknown"

    def _extract_quantization_level(self, model_name: str) -> Optional[str]:
        """Extract quantization level from ONNX model filename"""
        name_lower = model_name.lower()

        if "q4f16" in name_lower:
            return "Q4F16"
        elif "q4" in name_lower:
            return "Q4"
        elif "q8f16" in name_lower:
            return "Q8F16"
        elif "uint8f16" in name_lower:
            return "UINT8F16"
        elif "uint8" in name_lower:
            return "UINT8"
        elif "fp16" in name_lower:
            return "FP16"
        elif "quantized" in name_lower:
            return "QUANTIZED"
        else:
            return None

    def _extract_gguf_quantization_level(self, model_name: str) -> Optional[str]:
        """Extract quantization level from GGUF model filename"""
        name_lower = model_name.lower()

        if "_f16" in name_lower:
            return "F16"
        elif "_q4" in name_lower:
            return "Q4_0"
        elif "_q5" in name_lower:
            return "Q5_0"
        elif "_q8" in name_lower:
            return "Q8_0"
        else:
            return "FP32"  # Base model without quantization suffix
    
    def _get_variant_description(self, variant_type: str) -> str:
        """Get description for variant type"""
        descriptions = {
            "base": "Full precision base model",
            "fp16": "Half precision (16-bit float)",
            "q4": "4-bit quantized",
            "q4f16": "4-bit quantized with 16-bit float",
            "q8f16": "8-bit quantized with 16-bit float (recommended)",
            "uint8": "8-bit unsigned integer quantized",
            "uint8f16": "8-bit unsigned integer with 16-bit float",
            "quantized": "General quantized model",
            "unknown": "Unknown variant type"
        }
        return descriptions.get(variant_type, "Unknown variant type")

    def _get_gguf_variant_description(self, variant_type: str, model_name: str) -> str:
        """Get description for GGUF variant type"""
        descriptions = {
            "espeak_base": "Full precision with eSpeak phonemization",
            "no_espeak_base": "Full precision with native phonemization",
            "f16": "16-bit float precision",
            "q4": "4-bit quantization (Q4_0)",
            "q5": "5-bit quantization (Q5_0)",
            "q8": "8-bit quantization (Q8_0)",
            "gguf_unknown": "GGUF format with unknown quantization"
        }

        base_desc = descriptions.get(variant_type, "GGUF format")

        # Add phonemization info
        if "espeak" in model_name.lower() and "no_espeak" not in model_name.lower():
            phoneme_info = " (eSpeak compatible)"
        elif "no_espeak" in model_name.lower():
            phoneme_info = " (native phonemization)"
        else:
            phoneme_info = ""

        return base_desc + phoneme_info
    
    def get_available_models(self) -> List[str]:
        """Get list of all available model names"""
        return sorted(list(self.discovered_models.keys()))
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return self.discovered_models.get(model_name)
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if a model is already downloaded"""
        if model_name not in self.discovered_models:
            return False
        
        local_path = self.models_dir / model_name
        if not local_path.exists():
            return False
        
        model_info = self.discovered_models[model_name]
        return self._validate_file_integrity(local_path, model_info)
    
    def get_model_path(self, model_name: Optional[str] = None) -> Path:
        """Get local path for a model (default or specified)"""
        if model_name is None:
            model_name = self.default_variant
        
        return self.models_dir / model_name
    
    def download_model(self, model_name: str, 
                      progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """Download a specific model"""
        if model_name not in self.discovered_models:
            logger.error(f"Unknown model: {model_name}. Available models: {list(self.discovered_models.keys())}")
            return False
        
        model_info = self.discovered_models[model_name]
        local_path = self.models_dir / model_name
        
        # Check if model already exists and is valid
        if local_path.exists():
            if self._validate_file_integrity(local_path, model_info):
                logger.info(f"Model {model_name} already exists and is valid")
                return True
            else:
                logger.warning(f"Model {model_name} exists but validation failed, re-downloading")
        
        # Download the model
        url = model_info.download_url
        
        try:
            logger.info(f"Downloading {model_name} from {url}")
            
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', model_info.size))
            downloaded_size = 0
            start_time = time.time()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            elapsed_time = time.time() - start_time
                            speed_mbps = (downloaded_size / (1024 * 1024)) / max(elapsed_time, 0.001)
                            
                            progress = DownloadProgress(
                                filename=model_name,
                                downloaded_bytes=downloaded_size,
                                total_bytes=total_size,
                                percentage=(downloaded_size / total_size) * 100,
                                speed_mbps=speed_mbps
                            )
                            progress_callback(progress)
            
            # Validate downloaded model
            if self._validate_file_integrity(local_path, model_info):
                logger.info(f"Successfully downloaded {model_name}")
                return True
            else:
                logger.error(f"Downloaded model {model_name} failed validation")
                local_path.unlink()
                return False
        
        except Exception as e:
            logger.error(f"Failed to download {model_name}: {e}")
            if local_path.exists():
                local_path.unlink()
            return False
    
    def _validate_file_integrity(self, file_path: Path, model_info: ModelInfo) -> bool:
        """Validate file integrity against expected size and hash"""
        try:
            # Check file size
            actual_size = file_path.stat().st_size
            if model_info.size > 0 and actual_size != model_info.size:
                logger.warning(f"File size mismatch for {model_info.name}: expected {model_info.size}, got {actual_size}")
                return False
            
            # Check SHA hash if available
            if model_info.sha and model_info.sha != "":
                actual_hash = self._calculate_file_hash(file_path)
                if actual_hash != model_info.sha:
                    logger.warning(f"Hash mismatch for {model_info.name}: expected {model_info.sha}, got {actual_hash}")
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating file integrity for {model_info.name}: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
