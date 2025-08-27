#!/usr/bin/env python3
"""
Voice loading system with fallback mechanisms for torch dependencies
"""

import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import torch, but don't fail if it's not available
try:
    import torch
    _TORCH_AVAILABLE = True
    logger.debug("Torch available for voice loading")
except ImportError:
    _TORCH_AVAILABLE = False
    logger.info("Torch not available, using fallback voice loading")

@dataclass
class VoiceLoadResult:
    """Result of voice loading operation"""
    success: bool
    embedding_data: Optional[np.ndarray]
    metadata: Optional[Dict[str, Any]]
    loader_used: str
    error_message: Optional[str] = None

class VoiceLoader:
    """
    Robust voice loading system with multiple fallback mechanisms
    
    Loading priority:
    1. PyTorch (.pt files) - if torch available
    2. NumPy binary (.bin files) - always available
    3. Mock data - for testing environments
    """
    
    def __init__(self, voices_dir: str, enable_mock: bool = False):
        self.voices_dir = Path(voices_dir)
        self.enable_mock = enable_mock
        self.torch_available = _TORCH_AVAILABLE
        
        # Statistics
        self.load_stats = {
            'torch_loads': 0,
            'numpy_loads': 0,
            'mock_loads': 0,
            'failed_loads': 0
        }
        
        logger.info(f"VoiceLoader initialized: torch={self.torch_available}, mock={self.enable_mock}")
    
    def load_voice(self, voice_name: str) -> VoiceLoadResult:
        """
        Load voice embedding with fallback mechanisms
        
        Args:
            voice_name: Name of the voice to load
            
        Returns:
            VoiceLoadResult with embedding data and metadata
        """
        logger.debug(f"Loading voice: {voice_name}")
        
        # Try PyTorch loading first (if available)
        if self.torch_available:
            result = self._load_with_torch(voice_name)
            if result.success:
                self.load_stats['torch_loads'] += 1
                return result
            logger.debug(f"Torch loading failed for {voice_name}: {result.error_message}")
        
        # Try NumPy binary loading
        result = self._load_with_numpy(voice_name)
        if result.success:
            self.load_stats['numpy_loads'] += 1
            return result
        logger.debug(f"NumPy loading failed for {voice_name}: {result.error_message}")
        
        # Try mock data (if enabled)
        if self.enable_mock:
            result = self._load_mock_data(voice_name)
            if result.success:
                self.load_stats['mock_loads'] += 1
                logger.warning(f"Using mock data for voice: {voice_name}")
                return result
        
        # All loading methods failed
        self.load_stats['failed_loads'] += 1
        return VoiceLoadResult(
            success=False,
            embedding_data=None,
            metadata=None,
            loader_used="none",
            error_message=f"All loading methods failed for voice: {voice_name}"
        )
    
    def _load_with_torch(self, voice_name: str) -> VoiceLoadResult:
        """Load voice using PyTorch (.pt files)"""
        if not self.torch_available:
            return VoiceLoadResult(
                success=False,
                embedding_data=None,
                metadata=None,
                loader_used="torch",
                error_message="Torch not available"
            )
        
        voice_file = self.voices_dir / f"{voice_name}.pt"
        
        if not voice_file.exists():
            return VoiceLoadResult(
                success=False,
                embedding_data=None,
                metadata=None,
                loader_used="torch",
                error_message=f"PyTorch file not found: {voice_file}"
            )
        
        try:
            # Load the voice model
            model_data = torch.load(voice_file, map_location='cpu')
            
            # Extract embedding data and metadata
            embedding_data = None
            metadata = {}
            
            if isinstance(model_data, dict):
                # Handle dictionary format
                if 'embedding' in model_data:
                    embedding_data = model_data['embedding']
                elif 'style_vector' in model_data:
                    embedding_data = model_data['style_vector']
                elif 'data' in model_data:
                    embedding_data = model_data['data']
                else:
                    # Try to find tensor data
                    for key, value in model_data.items():
                        if isinstance(value, torch.Tensor):
                            embedding_data = value
                            break
                
                # Extract metadata
                metadata = {k: v for k, v in model_data.items() 
                           if not isinstance(v, torch.Tensor)}
                
            elif isinstance(model_data, torch.Tensor):
                embedding_data = model_data
            
            if embedding_data is None:
                return VoiceLoadResult(
                    success=False,
                    embedding_data=None,
                    metadata=None,
                    loader_used="torch",
                    error_message="No tensor data found in PyTorch file"
                )
            
            # Convert to numpy
            if isinstance(embedding_data, torch.Tensor):
                embedding_data = embedding_data.detach().cpu().numpy()
            
            # Add file metadata
            metadata.update({
                'file_path': str(voice_file),
                'file_size': voice_file.stat().st_size,
                'loaded_at': datetime.now().isoformat(),
                'loader': 'torch'
            })
            
            return VoiceLoadResult(
                success=True,
                embedding_data=embedding_data,
                metadata=metadata,
                loader_used="torch"
            )
            
        except Exception as e:
            return VoiceLoadResult(
                success=False,
                embedding_data=None,
                metadata=None,
                loader_used="torch",
                error_message=f"PyTorch loading error: {str(e)}"
            )
    
    def _load_with_numpy(self, voice_name: str) -> VoiceLoadResult:
        """Load voice using NumPy (.bin files)"""
        voice_file = self.voices_dir / f"{voice_name}.bin"
        
        if not voice_file.exists():
            return VoiceLoadResult(
                success=False,
                embedding_data=None,
                metadata=None,
                loader_used="numpy",
                error_message=f"Binary file not found: {voice_file}"
            )
        
        try:
            # Load voice data as numpy array
            voice_data = np.fromfile(voice_file, dtype=np.float32)
            
            # Reshape based on expected format (style vectors are typically 256-dimensional)
            if len(voice_data) % 256 == 0:
                voice_data = voice_data.reshape(-1, 256)
            else:
                logger.warning(f"Voice '{voice_name}' has unexpected size: {len(voice_data)}")
                # Try to use as-is
                voice_data = voice_data.reshape(-1, len(voice_data))
            
            # Create metadata
            metadata = {
                'file_path': str(voice_file),
                'file_size': voice_file.stat().st_size,
                'loaded_at': datetime.now().isoformat(),
                'loader': 'numpy',
                'original_shape': voice_data.shape,
                'data_type': str(voice_data.dtype)
            }
            
            return VoiceLoadResult(
                success=True,
                embedding_data=voice_data,
                metadata=metadata,
                loader_used="numpy"
            )
            
        except Exception as e:
            return VoiceLoadResult(
                success=False,
                embedding_data=None,
                metadata=None,
                loader_used="numpy",
                error_message=f"NumPy loading error: {str(e)}"
            )
    
    def _load_mock_data(self, voice_name: str) -> VoiceLoadResult:
        """Generate mock voice data for testing"""
        try:
            # Generate deterministic mock data based on voice name
            np.random.seed(hash(voice_name) % (2**32))
            
            # Create mock embedding data (typical voice embedding shape)
            embedding_data = np.random.randn(512, 256).astype(np.float32)
            
            # Normalize to typical range
            embedding_data = embedding_data * 0.1
            
            metadata = {
                'voice_name': voice_name,
                'loaded_at': datetime.now().isoformat(),
                'loader': 'mock',
                'mock_seed': hash(voice_name) % (2**32),
                'shape': embedding_data.shape,
                'data_type': str(embedding_data.dtype)
            }
            
            return VoiceLoadResult(
                success=True,
                embedding_data=embedding_data,
                metadata=metadata,
                loader_used="mock"
            )
            
        except Exception as e:
            return VoiceLoadResult(
                success=False,
                embedding_data=None,
                metadata=None,
                loader_used="mock",
                error_message=f"Mock data generation error: {str(e)}"
            )
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Get loading statistics"""
        total_loads = sum(self.load_stats.values())
        
        stats = self.load_stats.copy()
        stats['total_loads'] = total_loads
        
        if total_loads > 0:
            stats['success_rate'] = (total_loads - stats['failed_loads']) / total_loads
            stats['torch_percentage'] = stats['torch_loads'] / total_loads
            stats['numpy_percentage'] = stats['numpy_loads'] / total_loads
            stats['mock_percentage'] = stats['mock_loads'] / total_loads
        else:
            stats['success_rate'] = 0.0
            stats['torch_percentage'] = 0.0
            stats['numpy_percentage'] = 0.0
            stats['mock_percentage'] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """Reset loading statistics"""
        self.load_stats = {
            'torch_loads': 0,
            'numpy_loads': 0,
            'mock_loads': 0,
            'failed_loads': 0
        }
        logger.info("Voice loader statistics reset")

# Global voice loader instance
_voice_loader: Optional[VoiceLoader] = None

def get_voice_loader(voices_dir: str = None, enable_mock: bool = False) -> VoiceLoader:
    """Get or create the global voice loader instance"""
    global _voice_loader
    
    if _voice_loader is None:
        if voices_dir is None:
            try:
                from ..config import config
                voices_dir = config.paths.voices_dir
            except ImportError:
                voices_dir = "LiteTTS/voices"  # Fallback
        
        _voice_loader = VoiceLoader(voices_dir, enable_mock)
    
    return _voice_loader
