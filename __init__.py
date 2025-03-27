"""
VectorMorph: Intelligent Image to SVG Vectorization

Created by Your Name
https://github.com/yourusername/vectormorph
"""

__version__ = "0.1.0"

from .core.converter import VectorMorph, convert_image
from .models.detector import detect_image_type, IMAGE_TYPES
from .core.preprocessing import preprocess_image

# Make key classes and functions available at package level
__all__ = [
    'VectorMorph',
    'convert_image',
    'detect_image_type',
    'preprocess_image',
    'IMAGE_TYPES'
]