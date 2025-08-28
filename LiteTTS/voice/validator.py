#!/usr/bin/env python3
"""
Voice model validator for integrity checking
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Voice validation result"""
    is_valid: bool
    voice_name: str
    file_path: str
    file_size: int
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class VoiceValidator:
    """Validates voice model files for integrity and compatibility"""
    
    def __init__(self):
        # Expected tensor shapes and properties for Kokoro voices
        self.expected_properties = {
            'embedding_dim': 256,  # Expected embedding dimension
            'min_file_size': 1024 * 1024,  # Minimum 1MB
            'max_file_size': 100 * 1024 * 1024,  # Maximum 100MB
            'required_keys': ['embedding', 'metadata'],  # Expected keys in the model
        }
    
    def validate_voice(self, voice_name: str, file_path: Path) -> ValidationResult:
        """Validate a single voice model file"""
        result = ValidationResult(
            is_valid=False,
            voice_name=voice_name,
            file_path=str(file_path),
            file_size=0,
            errors=[],
            warnings=[],
            metadata={}
        )

        # Check if file exists
        if not file_path.exists():
            result.errors.append(f"Voice file does not exist: {file_path}")
            return result

        # Get file size
        result.file_size = file_path.stat().st_size

        # Check file size - adjust for .bin files (smaller than .pt files)
        min_size = 100 * 1024 if file_path.suffix == '.bin' else self.expected_properties['min_file_size']  # 100KB for .bin files
        if result.file_size < min_size:
            result.errors.append(f"File too small: {result.file_size} bytes")

        if result.file_size > self.expected_properties['max_file_size']:
            result.warnings.append(f"File very large: {result.file_size} bytes")

        # Try to load the model based on file type
        try:
            if file_path.suffix == '.bin':
                # Handle .bin files (numpy arrays)
                import numpy as np
                voice_data = np.fromfile(file_path, dtype=np.float32)

                # Validate .bin file structure
                if len(voice_data) % 256 == 0:
                    voice_data = voice_data.reshape(-1, 256)
                    result.metadata['embedding_shape'] = voice_data.shape
                    result.metadata['embedding_dim'] = 256
                    result.metadata['loaded_successfully'] = True
                else:
                    result.warnings.append(f"Unexpected voice data size: {len(voice_data)} (not divisible by 256)")
                    result.metadata['loaded_successfully'] = True  # Still valid, just unusual

                result.metadata['file_type'] = 'binary'
                result.metadata['data_type'] = str(voice_data.dtype)

            else:
                # Handle .pt files (PyTorch tensors)
                model_data = torch.load(file_path, map_location='cpu')
                result.metadata['loaded_successfully'] = True
                result.metadata['file_type'] = 'pytorch'

                # Validate model structure
                self._validate_model_structure(model_data, result)

                # Validate embedding data
                self._validate_embedding_data(model_data, result)

                # Additional checks
                self._perform_additional_checks(model_data, result)

        except Exception as e:
            result.errors.append(f"Failed to load model: {str(e)}")
            result.metadata['loaded_successfully'] = False

        # Set overall validity
        result.is_valid = len(result.errors) == 0

        return result
    
    def _validate_model_structure(self, model_data: Any, result: ValidationResult):
        """Validate the structure of the loaded model"""
        if isinstance(model_data, dict):
            result.metadata['model_type'] = 'dictionary'
            result.metadata['keys'] = list(model_data.keys())
            
            # Check for required keys
            missing_keys = []
            for key in self.expected_properties.get('required_keys', []):
                if key not in model_data:
                    missing_keys.append(key)
            
            if missing_keys:
                result.warnings.append(f"Missing expected keys: {missing_keys}")
                
        elif isinstance(model_data, torch.Tensor):
            result.metadata['model_type'] = 'tensor'
            result.metadata['tensor_shape'] = list(model_data.shape)
            result.metadata['tensor_dtype'] = str(model_data.dtype)
            
        else:
            result.metadata['model_type'] = type(model_data).__name__
            result.warnings.append(f"Unexpected model type: {type(model_data)}")
    
    def _validate_embedding_data(self, model_data: Any, result: ValidationResult):
        """Validate embedding data within the model"""
        embedding_tensor = None
        
        if isinstance(model_data, dict):
            # Look for embedding data in common keys
            for key in ['embedding', 'embeddings', 'voice_embedding', 'data']:
                if key in model_data:
                    embedding_tensor = model_data[key]
                    break
        elif isinstance(model_data, torch.Tensor):
            embedding_tensor = model_data
        
        if embedding_tensor is not None and isinstance(embedding_tensor, torch.Tensor):
            shape = embedding_tensor.shape
            result.metadata['embedding_shape'] = list(shape)
            result.metadata['embedding_dtype'] = str(embedding_tensor.dtype)
            result.metadata['embedding_size'] = embedding_tensor.numel()
            
            # Check for reasonable embedding dimensions
            if len(shape) < 1:
                result.errors.append("Embedding tensor has no dimensions")
            elif len(shape) > 3:
                result.warnings.append(f"Embedding tensor has many dimensions: {len(shape)}")
            
            # Check for NaN or infinite values
            if torch.any(torch.isnan(embedding_tensor)):
                result.errors.append("Embedding contains NaN values")
            
            if torch.any(torch.isinf(embedding_tensor)):
                result.errors.append("Embedding contains infinite values")
            
            # Check value range
            min_val = torch.min(embedding_tensor).item()
            max_val = torch.max(embedding_tensor).item()
            result.metadata['embedding_min'] = min_val
            result.metadata['embedding_max'] = max_val
            
            if abs(min_val) > 100 or abs(max_val) > 100:
                result.warnings.append(f"Embedding values seem large: [{min_val}, {max_val}]")
        else:
            result.warnings.append("No embedding tensor found in model")    
    
    def _perform_additional_checks(self, model_data: Any, result: ValidationResult):
        """Perform additional validation checks"""
        # Check for metadata
        if isinstance(model_data, dict) and 'metadata' in model_data:
            metadata = model_data['metadata']
            result.metadata['has_metadata'] = True
            
            if isinstance(metadata, dict):
                result.metadata['metadata_keys'] = list(metadata.keys())
                
                # Check for common metadata fields
                expected_metadata = ['voice_name', 'gender', 'language', 'sample_rate']
                for field in expected_metadata:
                    if field in metadata:
                        result.metadata[f'metadata_{field}'] = metadata[field]
            else:
                result.warnings.append(f"Metadata is not a dictionary: {type(metadata)}")
        else:
            result.metadata['has_metadata'] = False
            result.warnings.append("No metadata found in model")
        
        # Check model size consistency
        if isinstance(model_data, dict):
            total_params = 0
            for key, value in model_data.items():
                if isinstance(value, torch.Tensor):
                    total_params += value.numel()
            
            result.metadata['total_parameters'] = total_params
            
            # Rough size check
            expected_size = total_params * 4  # Assuming float32
            actual_size = result.file_size
            
            if abs(actual_size - expected_size) > expected_size * 0.5:
                result.warnings.append(
                    f"File size mismatch: expected ~{expected_size}, got {actual_size}"
                )
        
        return result
    
    def validate_all_voices(self, voices_dir: Path) -> Dict[str, ValidationResult]:
        """Validate all voice files in a directory"""
        results = {}

        # Look for .pt files
        for voice_file in voices_dir.glob("*.pt"):
            voice_name = voice_file.stem
            logger.info(f"Validating voice: {voice_name}")
            results[voice_name] = self.validate_voice(voice_name, voice_file)

        # Look for .bin files
        for voice_file in voices_dir.glob("*.bin"):
            voice_name = voice_file.stem
            logger.info(f"Validating voice: {voice_name}")
            results[voice_name] = self.validate_voice(voice_name, voice_file)

        return results
    
    def get_validation_summary(self, results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Get summary of validation results"""
        total_voices = len(results)
        valid_voices = sum(1 for r in results.values() if r.is_valid)
        invalid_voices = total_voices - valid_voices
        
        all_errors = []
        all_warnings = []
        
        for result in results.values():
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        return {
            'total_voices': total_voices,
            'valid_voices': valid_voices,
            'invalid_voices': invalid_voices,
            'validation_rate': valid_voices / total_voices if total_voices > 0 else 0,
            'total_errors': len(all_errors),
            'total_warnings': len(all_warnings),
            'unique_errors': list(set(all_errors)),
            'unique_warnings': list(set(all_warnings))
        }
    
    def repair_voice_file(self, voice_name: str, file_path: Path) -> bool:
        """Attempt to repair a corrupted voice file"""
        logger.info(f"Attempting to repair voice file: {voice_name}")
        
        try:
            # Try to load the model
            model_data = torch.load(file_path, map_location='cpu')
            
            # Perform basic repairs
            repaired = False
            
            if isinstance(model_data, dict):
                # Remove NaN values from tensors
                for key, value in model_data.items():
                    if isinstance(value, torch.Tensor):
                        if torch.any(torch.isnan(value)):
                            logger.info(f"Removing NaN values from {key}")
                            model_data[key] = torch.nan_to_num(value, nan=0.0)
                            repaired = True
                        
                        if torch.any(torch.isinf(value)):
                            logger.info(f"Removing infinite values from {key}")
                            model_data[key] = torch.nan_to_num(value, posinf=1.0, neginf=-1.0)
                            repaired = True
            
            elif isinstance(model_data, torch.Tensor):
                if torch.any(torch.isnan(model_data)) or torch.any(torch.isinf(model_data)):
                    logger.info("Removing NaN/infinite values from tensor")
                    model_data = torch.nan_to_num(model_data, nan=0.0, posinf=1.0, neginf=-1.0)
                    repaired = True
            
            # Save repaired model if changes were made
            if repaired:
                backup_path = file_path.with_suffix('.pt.backup')
                file_path.rename(backup_path)  # Create backup
                
                torch.save(model_data, file_path)
                logger.info(f"Repaired voice file saved: {file_path}")
                return True
            else:
                logger.info("No repairs needed")
                return True
                
        except Exception as e:
            logger.error(f"Failed to repair voice file {voice_name}: {e}")
            return False
    
    def check_compatibility(self, voice_name: str, file_path: Path, 
                          target_device: str = 'cpu') -> Dict[str, Any]:
        """Check compatibility with target device and system"""
        compatibility = {
            'compatible': False,
            'device_compatible': False,
            'memory_requirements': 0,
            'issues': []
        }
        
        try:
            # Try loading on target device
            if target_device == 'cuda' and not torch.cuda.is_available():
                compatibility['issues'].append("CUDA not available")
                target_device = 'cpu'
            
            model_data = torch.load(file_path, map_location=target_device)
            compatibility['device_compatible'] = True
            
            # Estimate memory requirements
            if isinstance(model_data, dict):
                memory_bytes = sum(
                    v.element_size() * v.numel() 
                    for v in model_data.values() 
                    if isinstance(v, torch.Tensor)
                )
            elif isinstance(model_data, torch.Tensor):
                memory_bytes = model_data.element_size() * model_data.numel()
            else:
                memory_bytes = 0
            
            compatibility['memory_requirements'] = memory_bytes
            
            # Check available memory
            if target_device == 'cuda':
                available_memory = torch.cuda.get_device_properties(0).total_memory
                if memory_bytes > available_memory * 0.8:  # Leave 20% buffer
                    compatibility['issues'].append("Insufficient GPU memory")
            
            compatibility['compatible'] = len(compatibility['issues']) == 0
            
        except Exception as e:
            compatibility['issues'].append(f"Compatibility check failed: {str(e)}")
        
        return compatibility