"""
Image preprocessing module for img2vector.

This module provides functions for preprocessing images before vectorization
to improve conversion quality and results.
"""

import cv2
import numpy as np

def preprocess_image(image_path, output_path, preprocessing_level="none"):
    """
    Apply preprocessing to improve vectorization results.
    
    Args:
        image_path: Path to the input image
        output_path: Path to save the preprocessed image
        preprocessing_level: Preprocessing intensity level
            - "none": No preprocessing
            - "light": Basic noise reduction and contrast enhancement
            - "medium": Edge enhancement with aggressive denoising
            - "heavy": Thresholding and morphological operations
    
    Returns:
        None, saves preprocessed image to output_path
    """
    # Return if no preprocessing is needed
    if preprocessing_level == "none":
        return

    if preprocessing_level not in ("light", "medium", "heavy"):
        raise ValueError(
            f"Invalid preprocessing_level '{preprocessing_level}'. "
            "Choose from 'none', 'light', 'medium', 'heavy'."
        )

    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image for preprocessing: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    if preprocessing_level == "light":
        # Light preprocessing
        # Simple noise reduction and contrast enhancement
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        result = enhanced
        
    elif preprocessing_level == "medium":
        # Medium preprocessing
        # More aggressive denoising and edge enhancement
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        enhanced = cv2.equalizeHist(denoised)
        edges = cv2.Canny(enhanced, 50, 150)
        kernel = np.ones((2, 2), np.uint8)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)
        result = dilated_edges
        
    elif preprocessing_level == "heavy":
        # Heavy preprocessing
        # Threshold and morphological operations
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        # Apply morphological operations
        kernel = np.ones((2, 2), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        result = opening
    
    # Save the preprocessed image
    cv2.imwrite(output_path, result)

def enhance_lines(image, strength=1.0):
    """
    Enhance lines in an image to improve vectorization of line drawings.
    
    Args:
        image: Image array or path to image
        strength: Enhancement strength (0.5-2.0)
    
    Returns:
        Enhanced image array
    """
    # Load image if path is provided
    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = image.copy()
    
    # Convert to grayscale if needed
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    # Apply line enhancement
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)
    enhanced = cv2.addWeighted(gray, 1 + strength, blurred, -strength, 0)
    
    return enhanced

def enhance_colors(image, saturation=1.2, value=1.1):
    """
    Enhance colors in an image to improve vectorization of colored images.
    
    Args:
        image: Image array or path to image
        saturation: Color saturation multiplier
        value: Color value (brightness) multiplier
    
    Returns:
        Enhanced image array
    """
    # Load image if path is provided
    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = image.copy()
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype("float32")
    
    # Scale saturation and value channels
    (h, s, v) = cv2.split(hsv)
    s = s * saturation
    v = v * value
    
    # Clip values to valid range
    s = np.clip(s, 0, 255)
    v = np.clip(v, 0, 255)
    
    # Merge channels and convert back to BGR
    hsv = cv2.merge([h, s, v])
    enhanced = cv2.cvtColor(hsv.astype("uint8"), cv2.COLOR_HSV2BGR)
    
    return enhanced

def reduce_noise(image, method="gaussian", strength=5):
    """
    Reduce noise in an image to improve vectorization.
    
    Args:
        image: Image array or path to image
        method: Noise reduction method
            - "gaussian": Gaussian blur
            - "median": Median filter
            - "bilateral": Bilateral filter (preserves edges)
        strength: Noise reduction strength (1-10)
    
    Returns:
        Noise-reduced image array
    """
    # Load image if path is provided
    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = image.copy()
    
    # Apply noise reduction based on method
    if method == "gaussian":
        kernel_size = 2 * int(strength) + 1
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    
    elif method == "median":
        kernel_size = 2 * int(strength) + 1
        return cv2.medianBlur(img, kernel_size)
    
    elif method == "bilateral":
        d = int(strength) * 2
        sigma_color = int(strength) * 15
        sigma_space = int(strength) * 15
        return cv2.bilateralFilter(img, d, sigma_color, sigma_space)
    
    return img