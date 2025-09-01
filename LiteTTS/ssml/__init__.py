# SSML processing package

from .parser import SSMLParser, ParsedSSML, BackgroundConfig, BackgroundType
from .background_generator import BackgroundGenerator
from .processor import SSMLProcessor

__all__ = [
    'SSMLParser',
    'ParsedSSML', 
    'BackgroundConfig',
    'BackgroundType',
    'BackgroundGenerator',
    'SSMLProcessor'
]
