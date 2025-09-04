#!/usr/bin/env python3
"""
Phase 6: Advanced Text Processing and Pronunciation Enhancement Integration
Integrates enhanced number processing, units processing, homograph resolution, and contraction processing
"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Import Phase 6 processors
from .enhanced_number_processor import EnhancedNumberProcessor, NumberProcessingResult
from .enhanced_units_processor import EnhancedUnitsProcessor, UnitsProcessingResult
from .enhanced_homograph_resolver import EnhancedHomographResolver, HomographProcessingResult
from .phase6_contraction_processor import Phase6ContractionProcessor, ContractionProcessingResult

logger = logging.getLogger(__name__)

@dataclass
class Phase6ProcessingResult:
    """Comprehensive result of Phase 6 text processing"""
    processed_text: str
    original_text: str
    processing_time: float
    
    # Individual processor results
    number_result: Optional[NumberProcessingResult] = None
    units_result: Optional[UnitsProcessingResult] = None
    homograph_result: Optional[HomographProcessingResult] = None
    contraction_result: Optional[ContractionProcessingResult] = None
    
    # Summary statistics
    total_changes: int = 0
    changes_by_category: Dict[str, int] = field(default_factory=dict)
    all_changes_made: List[str] = field(default_factory=list)
    
    # Performance metrics
    stage_timings: Dict[str, float] = field(default_factory=dict)
    performance_impact: float = 0.0  # RTF impact

class Phase6TextProcessor:
    """Comprehensive Phase 6 text processor integrating all enhancements"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Phase 6 text processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Load configuration
        self._load_config()
        
        # Initialize processors
        self._init_processors()
        
        logger.info("Phase 6 Text Processor initialized")
    
    def _load_config(self):
        """Load configuration settings"""
        try:
            import json
            from pathlib import Path
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path) as f:
                    main_config = json.load(f)
                    text_processing = main_config.get('text_processing', {})
                    
                    # Phase 6 specific settings
                    self.enabled = text_processing.get('phase6_enabled', True)
                    self.enable_number_processing = text_processing.get('enhanced_numbers', True)
                    self.enable_units_processing = text_processing.get('enhanced_units', True)
                    self.enable_homograph_resolution = text_processing.get('enhanced_homographs', True)
                    self.enable_contraction_processing = text_processing.get('enhanced_contractions', True)
                    
                    # Performance settings
                    self.max_rtf_impact = text_processing.get('max_rtf_impact', 0.1)  # 10% max impact
                    self.max_memory_overhead = text_processing.get('max_memory_overhead', 100)  # 100MB max
                    
            else:
                # Default settings
                self.enabled = True
                self.enable_number_processing = True
                self.enable_units_processing = True
                self.enable_homograph_resolution = True
                self.enable_contraction_processing = True
                self.max_rtf_impact = 0.1
                self.max_memory_overhead = 100
                
        except Exception as e:
            logger.warning(f"Failed to load Phase 6 configuration: {e}")
            # Safe defaults
            self.enabled = True
            self.enable_number_processing = True
            self.enable_units_processing = True
            self.enable_homograph_resolution = True
            self.enable_contraction_processing = True
            self.max_rtf_impact = 0.1
            self.max_memory_overhead = 100
    
    def _init_processors(self):
        """Initialize all Phase 6 processors"""
        try:
            if self.enable_number_processing:
                self.number_processor = EnhancedNumberProcessor(self.config)
                logger.debug("Enhanced Number Processor initialized")
            else:
                self.number_processor = None
                
            if self.enable_units_processing:
                self.units_processor = EnhancedUnitsProcessor(self.config)
                logger.debug("Enhanced Units Processor initialized")
            else:
                self.units_processor = None
                
            if self.enable_homograph_resolution:
                self.homograph_resolver = EnhancedHomographResolver(self.config)
                logger.debug("Enhanced Homograph Resolver initialized")
            else:
                self.homograph_resolver = None
                
            if self.enable_contraction_processing:
                self.contraction_processor = Phase6ContractionProcessor(self.config)
                logger.debug("Phase 6 Contraction Processor initialized")
            else:
                self.contraction_processor = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Phase 6 processors: {e}")
            # Disable all processors on initialization failure
            self.number_processor = None
            self.units_processor = None
            self.homograph_resolver = None
            self.contraction_processor = None
    
    def process_text(self, text: str) -> Phase6ProcessingResult:
        """Main Phase 6 text processing method
        
        Args:
            text: Input text to process
            
        Returns:
            Phase6ProcessingResult with comprehensive processing results
        """
        if not self.enabled:
            logger.debug("Phase 6 processing disabled")
            return Phase6ProcessingResult(
                processed_text=text,
                original_text=text,
                processing_time=0.0
            )
        
        logger.debug(f"Starting Phase 6 processing for text: {text[:100]}...")
        start_time = time.perf_counter()
        original_text = text
        
        result = Phase6ProcessingResult(
            processed_text=text,
            original_text=original_text,
            processing_time=0.0
        )
        
        try:
            # Stage 1: Enhanced Number Processing
            if self.number_processor:
                stage_start = time.perf_counter()
                number_result = self.number_processor.process_numbers(text)
                text = number_result.processed_text
                result.number_result = number_result
                result.stage_timings['number_processing'] = time.perf_counter() - stage_start
                
                if number_result.changes_made:
                    result.changes_by_category['numbers'] = number_result.numbers_processed
                    result.all_changes_made.extend(number_result.changes_made)
                    logger.debug(f"Number processing: {number_result.numbers_processed} numbers processed")
            
            # Stage 2: Enhanced Units Processing
            if self.units_processor:
                stage_start = time.perf_counter()
                units_result = self.units_processor.process_units(text)
                text = units_result.processed_text
                result.units_result = units_result
                result.stage_timings['units_processing'] = time.perf_counter() - stage_start
                
                if units_result.changes_made:
                    result.changes_by_category['units'] = units_result.units_processed
                    result.all_changes_made.extend(units_result.changes_made)
                    logger.debug(f"Units processing: {units_result.units_processed} units processed")
            
            # Stage 3: Enhanced Homograph Resolution
            if self.homograph_resolver:
                stage_start = time.perf_counter()
                homograph_result = self.homograph_resolver.resolve_homographs(text)
                text = homograph_result.processed_text
                result.homograph_result = homograph_result
                result.stage_timings['homograph_resolution'] = time.perf_counter() - stage_start
                
                if homograph_result.changes_made:
                    result.changes_by_category['homographs'] = len(homograph_result.homographs_resolved)
                    result.all_changes_made.extend(homograph_result.changes_made)
                    logger.debug(f"Homograph resolution: {len(homograph_result.homographs_resolved)} homographs resolved")
            
            # Stage 4: Enhanced Contraction Processing
            if self.contraction_processor:
                stage_start = time.perf_counter()
                contraction_result = self.contraction_processor.process_contractions(text)
                text = contraction_result.processed_text
                result.contraction_result = contraction_result
                result.stage_timings['contraction_processing'] = time.perf_counter() - stage_start
                
                if contraction_result.changes_made:
                    result.changes_by_category['contractions'] = len(contraction_result.contractions_processed)
                    result.all_changes_made.extend(contraction_result.changes_made)
                    logger.debug(f"Contraction processing: {len(contraction_result.contractions_processed)} contractions processed")
            
            # Finalize result
            result.processed_text = text
            result.processing_time = time.perf_counter() - start_time
            result.total_changes = sum(result.changes_by_category.values())
            result.performance_impact = result.processing_time / max(len(original_text), 1) * 1000  # ms per character
            
            logger.info(f"Phase 6 processing complete: {result.total_changes} total changes in {result.processing_time:.3f}s")
            
            # Check performance impact
            if result.performance_impact > self.max_rtf_impact * 1000:
                logger.warning(f"Phase 6 processing exceeded RTF impact threshold: {result.performance_impact:.3f}ms/char")
            
            return result
            
        except Exception as e:
            logger.error(f"Phase 6 processing failed: {e}")
            result.processed_text = original_text  # Return original on error
            result.processing_time = time.perf_counter() - start_time
            result.all_changes_made.append(f"Processing error: {e}")
            return result
    
    def get_processor_status(self) -> Dict[str, Any]:
        """Get status of all Phase 6 processors"""
        return {
            'phase6_enabled': self.enabled,
            'processors': {
                'number_processor': self.number_processor is not None,
                'units_processor': self.units_processor is not None,
                'homograph_resolver': self.homograph_resolver is not None,
                'contraction_processor': self.contraction_processor is not None
            },
            'performance_limits': {
                'max_rtf_impact': self.max_rtf_impact,
                'max_memory_overhead': self.max_memory_overhead
            }
        }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        stats = {
            'processors_available': 0,
            'total_capabilities': {}
        }
        
        if self.number_processor:
            stats['processors_available'] += 1
            # Add number processor specific stats if available
        
        if self.units_processor:
            stats['processors_available'] += 1
            # Add units processor specific stats if available
        
        if self.homograph_resolver:
            stats['processors_available'] += 1
            stats['total_capabilities']['homographs'] = self.homograph_resolver.get_homograph_statistics()
        
        if self.contraction_processor:
            stats['processors_available'] += 1
            stats['total_capabilities']['contractions'] = self.contraction_processor.get_contraction_statistics()
        
        return stats
