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

def detect_image_type(image):
    """
    Detect the type of image to apply optimal parameters.
    
    Args:
        image: PIL Image, numpy array, or path to image file
        
    Returns:
        str: One of the predefined image types
    """
    # Handle different input types
    if isinstance(image, str):
        # It's a file path
        img_array = np.array(Image.open(image))
    elif isinstance(image, Image.Image):
        # It's a PIL Image
        img_array = np.array(image)
    elif isinstance(image, np.ndarray):
        # It's already a numpy array
        img_array = image
    else:
        raise ValueError("Image must be a PIL Image, numpy array, or path to image file")
    
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Check if it's mostly black and white
    unique_values = len(np.unique(gray))
    is_binary = unique_values < 5
    
    # Calculate edge density
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.mean(edges) / 255
    
    # Calculate histogram for texture analysis
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_norm = hist / hist.sum()
    hist_entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-10))
    
    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    line_count = 0 if lines is None else len(lines)
    
    # Detect circles
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=0, maxRadius=0)
    circle_count = 0 if circles is None else len(circles[0])
    
    # Additional features for enhanced detection
    straight_lines_ratio = detect_straight_lines_ratio(edges)
    texture_complexity = calculate_texture_complexity(gray)
    color_complexity = calculate_color_complexity(img_array)
    
    # Decision logic with feature importance weighting
    if is_binary and edge_density > 0.1 and line_count > 10:
        if circle_count > 5 or straight_lines_ratio > 0.7:
            return TECHNICAL_DRAWING
        else:
            return LINE_DRAWING
    elif edge_density < 0.05 and hist_entropy < 7 and straight_lines_ratio > 0.8:
        return GEOMETRIC_SHAPES
    elif edge_density > 0.1 and line_count > 5 and circle_count > 2:
        if texture_complexity < 0.3:
            return DIAGRAM
        else:
            return TECHNICAL_DRAWING
    elif color_complexity > 0.6:
        return PHOTO
    else:
        # Fallback with confidence scoring
        scores = {
            LINE_DRAWING: score_line_drawing(edge_density, is_binary, texture_complexity),
            TECHNICAL_DRAWING: score_technical_drawing(straight_lines_ratio, circle_count),
            GEOMETRIC_SHAPES: score_geometric_shapes(edge_density, hist_entropy),
            DIAGRAM: score_diagram(line_count, circle_count),
            PHOTO: score_photo(color_complexity, texture_complexity)
        }
        
        # Return the type with highest score
        return max(scores.items(), key=lambda x: x[1])[0]

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
    """Calculate the ratio of straight lines to total edges."""
    # Implementation details would go here
    # This is a simplified placeholder
    return 0.5  # Example value

def calculate_texture_complexity(gray_image):
    """Calculate texture complexity using GLCM or similar methods."""
    # Implementation details would go here
    # This is a simplified placeholder
    return 0.3  # Example value

def calculate_color_complexity(image):
    """Calculate color complexity using color histogram variance."""
    # Implementation details would go here
    # This is a simplified placeholder
    return 0.7  # Example value

# Scoring functions
def score_line_drawing(edge_density, is_binary, texture_complexity):
    """Score likelihood of being a line drawing."""
    # Implementation details would go here
    return 0.7 if (is_binary and edge_density > 0.1) else 0.3

def score_technical_drawing(straight_lines_ratio, circle_count):
    """Score likelihood of being a technical drawing."""
    # Implementation details would go here
    return 0.8 if (straight_lines_ratio > 0.7 and circle_count > 3) else 0.4

def score_geometric_shapes(edge_density, hist_entropy):
    """Score likelihood of containing geometric shapes."""
    # Implementation details would go here
    return 0.9 if (edge_density < 0.05 and hist_entropy < 7) else 0.2

def score_diagram(line_count, circle_count):
    """Score likelihood of being a diagram."""
    # Implementation details would go here
    return 0.85 if (line_count > 5 and circle_count > 2) else 0.3

def score_photo(color_complexity, texture_complexity):
    """Score likelihood of being a photo."""
    # Implementation details would go here
    return 0.95 if (color_complexity > 0.6 and texture_complexity > 0.5) else 0.25