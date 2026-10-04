"""
Core img2vector conversion engine.
"""
import os
import tempfile
import uuid
from PIL import Image
import numpy as np

# Import from other modules
from ..models.detector import detect_image_type, get_optimal_params
from .preprocessing import preprocess_image

# Try to import vtracer
try:
    import vtracer
except ImportError:
    raise ImportError(
        "The vtracer library is required. Install with: pip install vtracer"
    )

class Img2Vector:
    """
    Main class for img2vector - an intelligent image to SVG converter.
    """
    
    def __init__(self):
        """Initialize the img2vector converter."""
        self.temp_dir = tempfile.mkdtemp()
        
    def convert(
        self,
        input_image,
        output_path=None,
        auto_optimize=True,
        preprocessing_level="none",
        colormode="color",
        hierarchical="stacked",
        mode="spline",
        filter_speckle=4,
        color_precision=6,
        layer_difference=16,
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        path_precision=3
    ):
        """
        Convert an image to SVG.
        
        Args:
            input_image: Path to image file or PIL Image object
            output_path: Path to save the SVG file (if None, returns SVG content)
            auto_optimize: Whether to automatically optimize parameters
            preprocessing_level: Level of preprocessing to apply
            colormode: Color mode ("color" or "binary")
            hierarchical: Hierarchical mode ("stacked" or "cutout")
            mode: Path mode ("spline" or "polygon")
            filter_speckle: Speckle filtering level (0-20)
            color_precision: Color precision level (1-10)
            layer_difference: Layer difference threshold (1-32)
            corner_threshold: Corner detection threshold (0-180)
            length_threshold: Length threshold for path simplification (0-10)
            max_iterations: Maximum iterations for path optimization (1-20)
            splice_threshold: Splice threshold for path joining (0-90)
            path_precision: Path coordinate precision (1-10)
            
        Returns:
            If output_path is None, returns the SVG content as a string.
            Otherwise, returns the path to the saved SVG file.
        """
        # Handle different input types
        if isinstance(input_image, str):
            # It's a file path
            try:
                pil_image = Image.open(input_image)
                # Always create a clean copy for vtracer to avoid path issues
                clean_path = os.path.join(self.temp_dir, f"clean_input_{uuid.uuid4()}.png")
                pil_image.save(clean_path)
                image_path = clean_path
            except Exception as e:
                raise ValueError(f"Could not open image at path '{input_image}': {str(e)}")
        elif isinstance(input_image, Image.Image):
            # It's a PIL Image
            pil_image = input_image
            # We need to save it temporarily
            image_path = os.path.join(self.temp_dir, f"input_{uuid.uuid4()}.png")
            pil_image.save(image_path)
        else:
            raise ValueError("input_image must be a file path or PIL Image object")
            
        # Create output path if not provided
        if output_path is None:
            output_path = os.path.join(self.temp_dir, f"output_{uuid.uuid4()}.svg")
            return_content = True
        else:
            output_path = os.path.abspath(output_path)
            return_content = False
        
        # Auto-optimize parameters if requested
        if auto_optimize:
            # Detect image type
            image_type = detect_image_type(pil_image)
            
            # Get optimal parameters
            optimal_params = get_optimal_params(image_type)
            
            # Update parameters only if not explicitly specified by user
            # This is the key fix - only override default values, not user-specified ones
            if colormode == "color":  # Default value, can be overridden
                colormode = optimal_params["colormode"]
            if hierarchical == "stacked":  # Default value, can be overridden
                hierarchical = optimal_params["hierarchical"]
            if mode == "spline":  # Default value, can be overridden
                mode = optimal_params["mode"]
            if filter_speckle == 4:  # Default value, can be overridden
                filter_speckle = optimal_params["filter_speckle"]
            if color_precision == 6:  # Default value, can be overridden
                color_precision = optimal_params["color_precision"]
            if layer_difference == 16:  # Default value, can be overridden
                layer_difference = optimal_params["layer_difference"]
            if corner_threshold == 60:  # Default value, can be overridden
                corner_threshold = optimal_params["corner_threshold"]
            if length_threshold == 4.0:  # Default value, can be overridden
                length_threshold = optimal_params["length_threshold"]
            if max_iterations == 10:  # Default value, can be overridden
                max_iterations = optimal_params["max_iterations"]
            if splice_threshold == 45:  # Default value, can be overridden
                splice_threshold = optimal_params["splice_threshold"]
            if path_precision == 3:  # Default value, can be overridden
                path_precision = optimal_params["path_precision"]
        
        # Preprocess the image if needed
        if preprocessing_level != "none":
            preprocessed_path = os.path.join(self.temp_dir, f"preprocessed_{uuid.uuid4()}.png")
            preprocess_image(image_path, preprocessed_path, preprocessing_level)
            input_path = preprocessed_path
        else:
            input_path = image_path
        
        # Verify the file exists before passing to vtracer
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Image file does not exist at path: {input_path}")
        
        # Make sure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Convert the image to SVG using VTracer
        try:
            vtracer.convert_image_to_svg_py(
                input_path,
                output_path,
                colormode=colormode,
                hierarchical=hierarchical,
                mode=mode,
                filter_speckle=int(filter_speckle),
                color_precision=int(color_precision),
                layer_difference=int(layer_difference),
                corner_threshold=int(corner_threshold),
                length_threshold=float(length_threshold),
                max_iterations=int(max_iterations),
                splice_threshold=int(splice_threshold),
                path_precision=int(path_precision)
            )
        except Exception as e:
            raise Exception(f"VTracer conversion failed: {str(e)}\nParameters: colormode={colormode}, hierarchical={hierarchical}, mode={mode}")
        
        # Return SVG content or file path
        if return_content:
            with open(output_path, "r") as f:
                svg_content = f.read()
            return svg_content
        else:
            return output_path

# Convenience function
def convert_image(
    input_path, 
    output_path=None,
    auto_optimize=True,
    preprocessing_level="none",
    **kwargs
):
    """
    Convert an image to SVG using intelligent optimization.
    
    Args:
        input_path (str): Path to the input image file
        output_path (str, optional): Path to save the output SVG file. If None, returns SVG content.
        auto_optimize (bool): Whether to automatically optimize parameters based on image type
        preprocessing_level (str): Level of preprocessing ("none", "light", "medium", "heavy")
        **kwargs: Additional parameters to pass to the converter
        
    Returns:
        str: SVG content if output_path is None, otherwise path to the output file
    """
    # Create a temporary directory for processing if needed
    import tempfile
    import os
    from PIL import Image
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Try to open and validate the image with PIL
        img = Image.open(input_path)
        
        # Save as a clean PNG to ensure compatibility with VTracer
        clean_path = os.path.join(temp_dir, "clean_input.png")
        img.save(clean_path)
        
        # Use the clean PNG for conversion
        converter = Img2Vector()
        result = converter.convert(
            clean_path,  # Always use the clean path, even for "none" preprocessing
            output_path=output_path,
            auto_optimize=auto_optimize,
            preprocessing_level=preprocessing_level,  # Pass the original preprocessing level
            **kwargs  # Pass any additional user-provided parameters
        )
        
        return result
        
    except Exception as e:
        # Add more context to the error
        raise Exception(f"Error converting image '{input_path}': {str(e)}") from e