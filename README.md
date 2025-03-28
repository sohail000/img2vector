# img2vector: Intelligent Image to SVG Conversion

![img2vector](https://github.com/user-attachments/assets/f979fda2-8680-4d48-9ad1-f64214627ec5)



[![PyPI version](https://badge.fury.io/py/img2vector.svg)](https://badge.fury.io/py/img2vector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Versions](https://img.shields.io/pypi/pyversions/img2vector.svg)

img2vector is an advanced image-to-SVG conversion library with intelligent detection technology that automatically analyzes image types and optimizes vectorization parameters for superior results. Created to solve the challenge of finding optimal conversion settings for different types of images.

## 🔥 Features

- **Intelligent Image Analysis:** Automatically identifies whether your image is a line drawing, technical diagram, photo, or geometric shapes using a custom-built computer vision algorithm
- **Parameter Optimization:** Selects the perfect conversion parameters based on content analysis, eliminating trial-and-error
- **Multiple Vectorization Modes:** Choose between spline mode (for smooth curves) and polygon mode (for precise edges) based on your needs
- **Smart Preprocessing:** Four levels of image enhancement from light to heavy to handle noisy or low-quality source images
- **Clean, Optimized SVGs:** Produces high-quality vector graphics with minimal file size and node count
- **Intuitive Web Interface:** Easy-to-use Gradio UI for quick conversions without coding
- **Programmer API:** Full Python API for integration into automated workflows

## 🚀 Quick Start

### Web Interface

The easiest way to try img2vector is through the web interface:

```bash
pip install img2vector
python -m img2vector.app
```

### Python API

```python
from img2vector import convert_image

# Simple conversion with auto-optimization
convert_image("input.png", "output.svg")

# Advanced usage
from img2vector import img2vector

converter = img2vector()
# Detect image type
image_type = converter.detect_image_type("input.png")
print(f"Detected image type: {image_type}")

# Custom conversion
converter.convert(
    "input.png", 
    "output.svg",
    auto_optimize=True,
    preprocessing_level="medium"
)
```

## 📊 Supported Image Types and Optimization

img2vector's intelligent detection model recognizes these image types and applies specialized optimization:

| Image Type | Description | Optimized For |
|------------|-------------|---------------|
| Line Drawing | Hand-drawn sketches, illustrations | Clean lines with minimal nodes, smooth curves |
| Technical Drawing | Blueprints, schematics, CAD | Precise corners, straight edges, accurate dimensions |
| Geometric Shapes | Simple shapes, logos | Accurate curves and angles, clean intersections |
| Diagram | Flowcharts, mind maps | Connected elements, text preservation, relationship clarity |
| Photo | Photographs, complex images | Color accuracy, detail preservation, tonal ranges |

## 🔧 Installation

```bash
pip install img2vector
```

### System Requirements

- Python 3.7+
- Dependencies: vtracer, scikit-image, opencv-python, numpy, pillow, gradio
- Works on Windows, macOS, and Linux

### Troubleshooting

If you encounter import errors after installation:
```bash
# Make sure to install all dependencies
pip install vtracer scikit-image opencv-python numpy pillow gradio

# If the package still can't be found, try:
pip uninstall img2vector -y
pip install -e .
```

## 💡 Real-World Applications

img2vector excels in diverse professional scenarios:

- **Cartography**: Convert geographic images into SVGs for scalable, editable maps suitable for both print and digital mediums
- **Web Development**: Transform raster images to SVGs for websites, ensuring graphics are crisp and load efficiently
- **Technical Documentation**: Convert technical drawings and schematics into SVG format for clear, scalable illustrations in manuals and guides
- **Logo Recreation**: Recreate logos from bitmap images for high-quality branding across all media
- **Architecture & Engineering**: Transform blueprints and diagrams into clean vector formats for professional documentation
- **Illustration Enhancement**: Convert hand-drawn illustrations to vectors for professional publishing

## ✨ Why img2vector?

Traditional vectorization tools use one-size-fits-all settings, requiring users to manually tweak numerous parameters through trial and error. img2vector leverages computer vision to analyze your specific image and automatically apply custom-tailored optimization. The result?

- Cleaner SVGs with fewer unnecessary nodes
- Smaller file sizes without quality loss
- Better visual quality with appropriate path types
- Significant time savings from automated parameter selection
- Consistent results across different image types

## 🌟 Technical Highlights

img2vector's image detection algorithm uses multiple factors to analyze images:

- Edge density analysis for determining image complexity
- Histogram entropy calculation for texture analysis
- Hough transform for line and shape detection
- Texture complexity scoring for material differentiation
- Color complexity measurement for photo identification

After detection, the system applies specialized parameter sets optimized through extensive testing for each image category.

## 🛠️ Future Development

Upcoming features planned for img2vector:

- Batch processing for converting multiple images
- Enhanced color quantization options
- Custom presets for recurring image types
- Web API for remote processing
- Additional output formats including PDF and EPS



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [VTracer](https://github.com/visioncortex/vtracer) for the core vectorization engine
- [Gradio](https://gradio.app/) for the web interface framework
- [OpenCV](https://opencv.org/) and [scikit-image](https://scikit-image.org/) for image processing

---

*Created with ❤️ by Sohail Khan*
