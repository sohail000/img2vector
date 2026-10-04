"""
img2vector: Intelligent Image to SVG Vectorization

Created by Sohail Khan
https://github.com/sohail000/img2vector
"""

__version__ = "1.2.0"

from .core.converter import Img2Vector, convert_image
from .models.detector import detect_image_type, IMAGE_TYPES
from .core.preprocessing import preprocess_image

# Make key classes and functions available at package level
__all__ = [
    'Img2Vector',
    'convert_image',
    'detect_image_type',
    'preprocess_image',
    'IMAGE_TYPES'
]