# C:\Users\2013k\OneDrive\Desktop\final\robust_test.py
import os
import sys
import time
from PIL import Image
from img2vector import Img2Vector, convert_image, detect_image_type

def test_with_image(image_path, output_dir):
    """Test conversion with a single image, with better error handling."""
    print(f"\nTesting image: {os.path.basename(image_path)}")
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found at: {image_path}")
        return
        
    # Check file size
    file_size = os.path.getsize(image_path)
    print(f"File size: {file_size} bytes")
    
    # Try to open with PIL first to verify the image is valid
    try:
        img = Image.open(image_path)
        img.verify()  # Verify the image is valid
        print(f"Image format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        
        # Close and reopen to reset file pointer
        img.close()
        img = Image.open(image_path)
        
        # Save a clean copy in PNG format to ensure compatibility
        clean_path = os.path.join(output_dir, "clean_input.png")
        img.save(clean_path)
        print(f"Saved clean copy to: {clean_path}")
        
        # Detect image type
        image_type = detect_image_type(clean_path)
        print(f"Detected image type: {image_type}")
        
        # Convert using the clean PNG
        output_path = os.path.join(output_dir, "output.svg")
        print(f"Converting with auto-optimization...")
        start_time = time.time()
        result = convert_image(clean_path, output_path, auto_optimize=True)
        elapsed = time.time() - start_time
        print(f"Conversion successful! Saved to: {output_path}")
        print(f"Time taken: {elapsed:.2f} seconds")
        
    except Exception as e:
        print(f"ERROR processing image: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide an image path as argument")
        print("Usage: python robust_test.py C:/path/to/image.jpg")
        sys.exit(1)
        
    # Get image path from command line
    image_path = sys.argv[1]
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg_output")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Run the test
    test_with_image(image_path, output_dir)