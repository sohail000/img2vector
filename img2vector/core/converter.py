"""
Core img2vector conversion engine.
"""
import os
import tempfile
import uuid
from PIL import Image

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

# Parameters used when auto-optimization is off and the user doesn't set them
DEFAULT_PARAMS = {
    "colormode": "color",
    "hierarchical": "stacked",
    "mode": "spline",
    "filter_speckle": 4,
    "color_precision": 6,
    "layer_difference": 16,
    "corner_threshold": 60,
    "length_threshold": 4.0,
    "max_iterations": 10,
    "splice_threshold": 45,
    "path_precision": 3,
}

def _to_savable(pil_image):
    """Return a copy of the image in a mode that can be written as PNG."""
    if pil_image.mode in ("RGB", "RGBA", "L", "LA"):
        return pil_image
    if pil_image.mode == "P" and "transparency" not in pil_image.info:
        return pil_image.convert("RGB")
    return pil_image.convert("RGBA")

class Img2Vector:
    """
    Main class for img2vector - an intelligent image to SVG converter.
    """

    def convert(
        self,
        input_image,
        output_path=None,
        auto_optimize=True,
        preprocessing_level="none",
        colormode=None,
        hierarchical=None,
        mode=None,
        filter_speckle=None,
        color_precision=None,
        layer_difference=None,
        corner_threshold=None,
        length_threshold=None,
        max_iterations=None,
        splice_threshold=None,
        path_precision=None
    ):
        """
        Convert an image to SVG.

        Any parameter left as None is filled in automatically: from the detected
        image type when auto_optimize is True, otherwise from DEFAULT_PARAMS.
        Parameters you pass explicitly are always respected.

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
        if isinstance(input_image, (str, os.PathLike)):
            try:
                pil_image = Image.open(input_image)
                pil_image.load()
            except Exception as e:
                raise ValueError(f"Could not open image at path '{input_image}': {str(e)}")
        elif isinstance(input_image, Image.Image):
            pil_image = input_image
        else:
            raise ValueError("input_image must be a file path or PIL Image object")

        user_params = {
            "colormode": colormode,
            "hierarchical": hierarchical,
            "mode": mode,
            "filter_speckle": filter_speckle,
            "color_precision": color_precision,
            "layer_difference": layer_difference,
            "corner_threshold": corner_threshold,
            "length_threshold": length_threshold,
            "max_iterations": max_iterations,
            "splice_threshold": splice_threshold,
            "path_precision": path_precision,
        }

        # Start from optimal or default parameters, then apply the user's choices
        if auto_optimize:
            params = dict(get_optimal_params(detect_image_type(pil_image)))
        else:
            params = dict(DEFAULT_PARAMS)
        params.update({k: v for k, v in user_params.items() if v is not None})

        with tempfile.TemporaryDirectory() as temp_dir:
            # Always write a clean PNG copy for vtracer to avoid path/format issues
            image_path = os.path.join(temp_dir, f"input_{uuid.uuid4()}.png")
            _to_savable(pil_image).save(image_path)

            # Preprocess the image if needed
            if preprocessing_level != "none":
                input_path = os.path.join(temp_dir, f"preprocessed_{uuid.uuid4()}.png")
                preprocess_image(image_path, input_path, preprocessing_level)
            else:
                input_path = image_path

            if output_path is None:
                svg_path = os.path.join(temp_dir, f"output_{uuid.uuid4()}.svg")
            else:
                svg_path = os.path.abspath(output_path)
                os.makedirs(os.path.dirname(svg_path), exist_ok=True)

            # Convert the image to SVG using VTracer
            try:
                vtracer.convert_image_to_svg_py(
                    input_path,
                    svg_path,
                    colormode=params["colormode"],
                    hierarchical=params["hierarchical"],
                    mode=params["mode"],
                    filter_speckle=int(params["filter_speckle"]),
                    color_precision=int(params["color_precision"]),
                    layer_difference=int(params["layer_difference"]),
                    corner_threshold=int(params["corner_threshold"]),
                    length_threshold=float(params["length_threshold"]),
                    max_iterations=int(params["max_iterations"]),
                    splice_threshold=int(params["splice_threshold"]),
                    path_precision=int(params["path_precision"])
                )
            except Exception as e:
                raise RuntimeError(
                    f"VTracer conversion failed: {str(e)}\n"
                    f"Parameters: colormode={params['colormode']}, "
                    f"hierarchical={params['hierarchical']}, mode={params['mode']}"
                ) from e

            # Return SVG content or file path
            if output_path is None:
                with open(svg_path, "r", encoding="utf-8") as f:
                    return f.read()
            return svg_path

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
    try:
        return Img2Vector().convert(
            input_path,
            output_path=output_path,
            auto_optimize=auto_optimize,
            preprocessing_level=preprocessing_level,
            **kwargs
        )
    except Exception as e:
        # Add more context to the error
        raise RuntimeError(f"Error converting image '{input_path}': {str(e)}") from e
