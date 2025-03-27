"""
VectorMorph Web Interface

A Gradio web application for the VectorMorph library.
"""
import os
import tempfile
import uuid
import gradio as gr
from PIL import Image

# Import from the VectorMorph package
from .core.converter import VectorMorph
from .models.detector import detect_image_type, IMAGE_TYPES

# Check for dependencies
try:
    import vtracer
except ImportError:
    print("WARNING: vtracer not found. Please install with: pip install vtracer")

# Custom CSS for better appearance
css = """
.container {
    max-width: 1100px;
    margin: 0 auto;
}
.title {
    text-align: center;
    margin-bottom: 10px;
}
.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 20px;
}
.convert-btn {
    background: linear-gradient(90deg, #4B79A1 0%, #283E51 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
}
.convert-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
.output-container {
    min-height: 350px;
    border: 1px dashed #ccc;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f9f9f9;
}
.params-container {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 15px;
    margin-top: 10px;
    background-color: #f9f9f9;
}
.result-message {
    padding: 10px;
    border-radius: 4px;
    background-color: #f0f8ff;
    margin-bottom: 10px;
    text-align: center;
}
"""

def convert_to_vector(
    image, 
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
    """Handle the conversion request from Gradio UI."""
    if image is None:
        return "Please upload an image first.", None, None
    
    # Create temp directory for files
    temp_dir = tempfile.mkdtemp()
    
    # Generate unique filenames
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(temp_dir, f"input_{unique_id}.png")
    output_path = os.path.join(temp_dir, f"output_{unique_id}.svg")
    
    # Save the input image
    if isinstance(image, dict) and 'path' in image:
        img = Image.open(image['path'])
        img.save(input_path)
    else:
        image.save(input_path)
    
    # Create VectorMorph instance
    converter = VectorMorph()
    
    # Auto-optimize message
    optimizer_message = ""
    
    try:
        # Process with VectorMorph
        if auto_optimize:
            # Detect image type
            if isinstance(image, dict) and 'path' in image:
                image_type = detect_image_type(image['path'])
            else:
                image_type = detect_image_type(image)
            
            optimizer_message = f"✅ Auto-optimization applied: Detected '{image_type}'"
            
            # Convert with auto-optimization
            converter.convert(
                input_path,
                output_path,
                auto_optimize=True,
                preprocessing_level=preprocessing_level
            )
        else:
            # Convert with manual parameters
            converter.convert(
                input_path,
                output_path,
                auto_optimize=False,
                preprocessing_level=preprocessing_level,
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
        
        # Read the SVG output
        with open(output_path, "r") as f:
            svg_content = f.read()
        
        # Get image dimensions for proper display
        img = Image.open(input_path)
        width, height = img.size
        
        # Create HTML for display
        html_display = f'<svg width="100%" height="100%" viewBox="0 0 {width} {height}">{svg_content}</svg>'
        
        # Create result message
        if optimizer_message:
            result_message = optimizer_message
        else:
            result_message = "Conversion successful!"
            
        if preprocessing_level != "none":
            result_message += f" | Preprocessing: {preprocessing_level}"
        
        return result_message, gr.HTML(html_display), output_path
    
    except Exception as e:
        return f"Error during conversion: {str(e)}", None, None

def update_ui_for_auto_optimize(auto_optimize):
    """Update UI interactivity based on auto-optimize selection."""
    if auto_optimize:
        return [
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False)
        ]
    else:
        return [
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True)
        ]

def clear_inputs():
    """Reset all inputs to default values."""
    return [
        None, True, "none", None, None,
        "color", "stacked", "spline",
        4, 6, 16, 60, 4.0, 10, 45, 3
    ]

def create_interface():
    """Create and return the Gradio interface."""
    with gr.Blocks(css=css) as app:
        with gr.Column(elem_classes=["container"]):
            gr.HTML(
                """
                <div class="title">
                    <h1>✨ VectorMorph - Intelligent Image to SVG Converter</h1>
                </div>
                <div class="subtitle">
                    <p>Convert raster images to high-quality vector graphics with AI-powered optimization</p>
                </div>
                """
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    image_input = gr.Image(type="pil", label="Upload Image")
                    
                    with gr.Group():
                        auto_optimize = gr.Checkbox(
                            value=True, 
                            label="Auto-optimize parameters",
                            info="Automatically detect image type and select optimal parameters"
                        )
                        
                        preprocessing = gr.Radio(
                            choices=["none", "light", "medium", "heavy"],
                            value="none",
                            label="Preprocessing",
                            info="Apply image preprocessing to improve vectorization"
                        )
                    
                    # Changed from gr.Box to gr.Group with custom CSS class
                    with gr.Group(elem_classes=["params-container"]):
                        gr.Markdown("### Conversion Parameters")
                        
                        with gr.Row():
                            colormode = gr.Radio(
                                choices=["color", "binary"], 
                                value="color", 
                                label="Color Mode",
                                interactive=False
                            )
                            hierarchical = gr.Radio(
                                choices=["stacked", "cutout"], 
                                value="stacked", 
                                label="Hierarchical Mode",
                                interactive=False
                            )
                            mode = gr.Radio(
                                choices=["spline", "polygon"], 
                                value="spline", 
                                label="Mode",
                                interactive=False
                            )
                        
                        with gr.Accordion("Advanced Settings", open=False):
                            with gr.Row():
                                with gr.Column():
                                    filter_speckle = gr.Slider(
                                        minimum=0, maximum=20, value=4, 
                                        label="Filter Speckle",
                                        interactive=False
                                    )
                                    color_precision = gr.Slider(
                                        minimum=1, maximum=10, value=6, 
                                        label="Color Precision",
                                        interactive=False
                                    )
                                    layer_difference = gr.Slider(
                                        minimum=1, maximum=32, value=16, 
                                        label="Layer Difference",
                                        interactive=False
                                    )
                                    corner_threshold = gr.Slider(
                                        minimum=0, maximum=180, value=60, 
                                        label="Corner Threshold",
                                        interactive=False
                                    )
                                
                                with gr.Column():
                                    length_threshold = gr.Slider(
                                        minimum=0, maximum=10, value=4.0, 
                                        label="Length Threshold",
                                        interactive=False
                                    )
                                    max_iterations = gr.Slider(
                                        minimum=1, maximum=20, value=10, 
                                        label="Max Iterations",
                                        interactive=False
                                    )
                                    splice_threshold = gr.Slider(
                                        minimum=0, maximum=90, value=45, 
                                        label="Splice Threshold",
                                        interactive=False
                                    )
                                    path_precision = gr.Slider(
                                        minimum=1, maximum=10, value=3, 
                                        label="Path Precision",
                                        interactive=False
                                    )
                    
                    with gr.Row():
                        convert_button = gr.Button(
                            "Convert to SVG", 
                            variant="primary",
                            elem_classes=["convert-btn"]
                        )
                        clear_button = gr.Button(
                            "Clear", 
                            variant="secondary"
                        )
                
                with gr.Column(scale=1):
                    result_message = gr.Textbox(
                        label="Status", 
                        elem_classes=["result-message"]
                    )
                    output_html = gr.HTML(
                        label="SVG Preview", 
                        elem_classes=["output-container"]
                    )
                    svg_file = gr.File(label="Download SVG")
                    
                    with gr.Accordion("Image Type Detection", open=True):
                        gr.Markdown(
                            """
                            VectorMorph's intelligent detection model recognizes these image types:
                            
                            - **Line Drawing**: Black and white sketches, hand drawings
                            - **Technical Drawing**: Technical diagrams, blueprints, schematics
                            - **Geometric Shapes**: Simple shapes like circles, squares, triangles
                            - **Diagram**: Flowcharts, mind maps, organizational charts
                            - **Photo**: Photographs or complex images
                            
                            Each type gets optimized parameters for best results.
                            """
                        )
                    
                    with gr.Accordion("Tips & Usage", open=False):
                        gr.Markdown(
                            """
                            ### Tips for Best Results
                            
                            - **For technical diagrams**: Use the 'binary' color mode with 'polygon' option
                            - **For smooth curves**: Use 'spline' mode with low corner threshold values
                            - **For crisp edges**: Use 'polygon' mode with high corner threshold values
                            - **For noisy images**: Try 'medium' or 'heavy' preprocessing and increase Filter Speckle
                            - **For color images**: Auto-optimization works best, or manually use 'color' mode with higher color precision
                            
                            ### Preprocessing Options
                            
                            - **Light**: Basic noise reduction and contrast enhancement
                            - **Medium**: Edge enhancement with more aggressive denoising
                            - **Heavy**: Thresholding and morphological operations for maximum clarity
                            
                            ### File Size Optimization
                            
                            - Lower Path Precision values create smaller file sizes
                            - Higher Filter Speckle values remove small details but reduce file size
                            - Higher Length Threshold values simplify paths and reduce file size
                            """
                        )

        # Event handlers
        auto_optimize.change(
            update_ui_for_auto_optimize,
            inputs=auto_optimize,
            outputs=[
                colormode, 
                hierarchical, 
                mode, 
                filter_speckle, 
                color_precision, 
                layer_difference, 
                corner_threshold, 
                length_threshold, 
                max_iterations, 
                splice_threshold, 
                path_precision
            ]
        )

        clear_button.click(
            clear_inputs,
            outputs=[
                image_input,
                auto_optimize,
                preprocessing,
                result_message,
                output_html,
                colormode,
                hierarchical,
                mode,
                filter_speckle,
                color_precision,
                layer_difference,
                corner_threshold,
                length_threshold,
                max_iterations,
                splice_threshold,
                path_precision
            ]
        )

        convert_button.click(
            convert_to_vector,
            inputs=[
                image_input,
                auto_optimize,
                preprocessing,
                colormode,
                hierarchical,
                mode,
                filter_speckle,
                color_precision,
                layer_difference,
                corner_threshold,
                length_threshold,
                max_iterations,
                splice_threshold,
                path_precision
            ],
            outputs=[result_message, output_html, svg_file]
        )
    
    return app

def main():
    """Launch the VectorMorph web interface."""
    try:
        import vtracer
    except ImportError:
        print("WARNING: vtracer not found. Please install with: pip install vtracer")
        print("The app will run but conversion won't work properly.")
    
    print("Starting VectorMorph...")
    print("For best results, the auto-optimization feature will analyze your image type")
    print("and apply optimal parameters automatically.")
    
    app = create_interface()
    app.launch(share=True)  # Set share=True to create a public link

if __name__ == "__main__":
    main()