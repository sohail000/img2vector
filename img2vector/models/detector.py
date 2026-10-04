"""
img2vector Image Type Detection Model

This module contains the core intelligence of img2vector - an advanced
image classification model that detects the type of image to apply optimal
vectorization parameters.
"""

import numpy as np
import cv2
from PIL import Image

# Define image types as constants
LINE_DRAWING = "Line Drawing"
TECHNICAL_DRAWING = "Technical Drawing"
PHOTO = "Photo"
GEOMETRIC_SHAPES = "Geometric Shapes"
DIAGRAM = "Diagram"

# Export image types
IMAGE_TYPES = [LINE_DRAWING, TECHNICAL_DRAWING, PHOTO, GEOMETRIC_SHAPES, DIAGRAM]

# Images are downscaled to at most this many pixels per side before analysis
MAX_DETECTION_SIZE = 1000

def _to_rgb_array(image):
    """Convert a PIL Image, numpy array, or image path to an 8-bit RGB array."""
    if isinstance(image, str):
        image = Image.open(image)

    if isinstance(image, Image.Image):
        if image.mode in ("RGBA", "LA", "PA") or (image.mode == "P" and "transparency" in image.info):
            # Composite transparent areas onto white instead of black
            rgba = image.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            image = Image.alpha_composite(background, rgba)
        elif image.mode in ("I", "I;16", "F"):
            # 16-bit / float images: scale down to 8-bit
            arr = np.asarray(image, dtype=np.float64)
            rng = arr.max() - arr.min()
            arr = (arr - arr.min()) / rng * 255 if rng > 0 else np.zeros_like(arr)
            image = Image.fromarray(arr.astype(np.uint8))
        return np.array(image.convert("RGB"))

    if isinstance(image, np.ndarray):
        arr = image
        if arr.dtype != np.uint8:
            arr = arr.astype(np.float64)
            if arr.max() <= 1.0:
                arr = arr * 255
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        if arr.ndim == 2:
            return cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
        if arr.ndim == 3 and arr.shape[2] == 4:
            return cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
        if arr.ndim == 3 and arr.shape[2] == 3:
            return arr
        raise ValueError(f"Unsupported image array shape: {arr.shape}")

    raise ValueError("Image must be a PIL Image, numpy array, or path to image file")

def detect_image_type(image):
    """
    Detect the type of image to apply optimal parameters.
    
    Args:
        image: PIL Image, numpy array, or path to image file
        
    Returns:
        str: One of the predefined image types
    """
    img_array = _to_rgb_array(image)

    # Work on a bounded size so features (and speed) don't depend on resolution
    height, width = img_array.shape[:2]
    scale = MAX_DETECTION_SIZE / max(height, width)
    if scale < 1:
        img_array = cv2.resize(img_array, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    edge_density = np.mean(edges) / 255
    straight_lines_ratio = detect_straight_lines_ratio(edges)
    texture_complexity = calculate_texture_complexity(gray)
    color_complexity = calculate_color_complexity(img_array)

    # Mostly black/white with little color: drawings rather than illustrations
    saturation = np.mean(cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)[..., 1]) / 255
    midtones = np.mean((gray > 50) & (gray < 205))
    is_monochrome = saturation < 0.1 and midtones < 0.05

    # Decision logic
    if color_complexity > 0.6:
        return PHOTO
    if is_monochrome:
        if straight_lines_ratio > 0.8:
            # Many straight edges: dense = technical drawing, sparse = simple shape
            return TECHNICAL_DRAWING if edge_density > 0.03 else GEOMETRIC_SHAPES
        return LINE_DRAWING
    if color_complexity < 0.3 and texture_complexity < 0.15:
        # Flat-colored artwork
        return GEOMETRIC_SHAPES if straight_lines_ratio > 0.85 else DIAGRAM
    return PHOTO if texture_complexity > 0.3 else DIAGRAM

def get_optimal_params(image_type):
    """Return optimal parameters based on image type."""
    params = {
        LINE_DRAWING: {
            "colormode": "binary",
            "hierarchical": "stacked",
            "mode": "spline",
            "filter_speckle": 2,
            "color_precision": 6,
            "layer_difference": 8,
            "corner_threshold": 60,
            "length_threshold": 3.0,
            "max_iterations": 10,
            "splice_threshold": 45,
            "path_precision": 3
        },
        TECHNICAL_DRAWING: {
            "colormode": "binary",
            "hierarchical": "stacked",
            "mode": "polygon",
            "filter_speckle": 3,
            "color_precision": 4,
            "layer_difference": 10,
            "corner_threshold": 80,
            "length_threshold": 2.0,
            "max_iterations": 15,
            "splice_threshold": 30,
            "path_precision": 5
        },
        GEOMETRIC_SHAPES: {
            "colormode": "color",
            "hierarchical": "stacked",
            "mode": "polygon",
            "filter_speckle": 5,
            "color_precision": 8,
            "layer_difference": 20,
            "corner_threshold": 90,
            "length_threshold": 4.0,
            "max_iterations": 5,
            "splice_threshold": 60,
            "path_precision": 2
        },
        DIAGRAM: {
            "colormode": "color",
            "hierarchical": "stacked",
            "mode": "spline",
            "filter_speckle": 4,
            "color_precision": 7,
            "layer_difference": 15,
            "corner_threshold": 70,
            "length_threshold": 3.5,
            "max_iterations": 12,
            "splice_threshold": 40,
            "path_precision": 4
        },
        PHOTO: {
            "colormode": "color",
            "hierarchical": "cutout",
            "mode": "spline",
            "filter_speckle": 8,
            "color_precision": 5,
            "layer_difference": 25,
            "corner_threshold": 50,
            "length_threshold": 5.0,
            "max_iterations": 8,
            "splice_threshold": 35,
            "path_precision": 3
        }
    }
    return params.get(image_type, params[PHOTO])  # Default to PHOTO if not found

# Helper functions for advanced image analysis
def detect_straight_lines_ratio(edges):
    """Calculate the fraction of edge pixels that lie on straight line segments."""
    edge_pixels = np.count_nonzero(edges)
    if edge_pixels == 0:
        return 0.0
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=20, maxLineGap=5)
    if lines is None:
        return 0.0
    # Draw the detected segments and count how many edge pixels they cover,
    # so overlapping segments aren't counted twice
    line_mask = np.zeros_like(edges)
    for x1, y1, x2, y2 in lines.reshape(-1, 4):
        cv2.line(line_mask, (int(x1), int(y1)), (int(x2), int(y2)), 255, 3)
    covered = np.count_nonzero((edges > 0) & (line_mask > 0))
    return float(covered / edge_pixels)

def calculate_texture_complexity(gray_image):
    """Calculate texture complexity as the fraction of pixels with noticeable gradient."""
    smoothed = cv2.GaussianBlur(gray_image, (3, 3), 0)
    gx = cv2.Sobel(smoothed, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(smoothed, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(gx, gy)
    return float(np.mean(magnitude > 30))

def calculate_color_complexity(image):
    """
    Calculate color complexity from how many distinct colors are needed
    to cover most of the image (0 = flat colors, 1 = photo-like).
    """
    # Quantize to 4 bits per channel so compression noise doesn't count as new colors
    quantized = (image.reshape(-1, image.shape[-1]) >> 4).astype(np.int32)
    keys = (quantized[:, 0] << 8) | (quantized[:, 1] << 4) | quantized[:, 2]
    counts = np.sort(np.bincount(keys))[::-1]
    coverage = np.cumsum(counts) / counts.sum()
    colors_for_95 = int(np.searchsorted(coverage, 0.95)) + 1
    return float(min(colors_for_95 / 256, 1.0))
