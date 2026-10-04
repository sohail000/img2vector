"""
img2vector: Intelligent Image to SVG Vectorization

Created by Sohail Khan
https://github.com/sohail000/img2vector
"""

__version__ = "1.2.1"

from .core.converter import Img2Vector, convert_image
from .models.detector import detect_image_type, IMAGE_TYPES
from .core.preprocessing import preprocess_image
from .batch_processing import batch_convert
from .svg_optimization import optimize_svg

# Make key classes and functions available at package level
__all__ = [
    'Img2Vector',
    'convert_image',
    'detect_image_type',
    'preprocess_image',
    'batch_convert',
    'optimize_svg',
    'IMAGE_TYPES',
]
