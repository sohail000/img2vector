"""
Batch processing utility for img2vector.
"""
import os
import concurrent.futures
from tqdm import tqdm
from .core.converter import Img2Vector

def batch_convert(
    input_folder,
    output_folder,
    num_workers=4,
    recursive=False,
    file_extensions=('.jpg', '.jpeg', '.png', '.bmp', '.gif'),
    auto_optimize=True,
    preprocessing_level="none",
    **kwargs
):
    """
    Convert multiple images to SVG in batch mode with parallel processing.
    
    Args:
        input_folder (str): Path to folder containing input images
        output_folder (str): Path to folder for output SVG files
        num_workers (int): Number of parallel workers (default: 4)
        recursive (bool): Whether to search for images in subfolders (default: False)
        file_extensions (tuple): Supported file extensions (default: '.jpg', '.jpeg', '.png', '.bmp', '.gif')
        auto_optimize (bool): Whether to use auto-optimization (default: True)
        preprocessing_level (str): Preprocessing level (default: "none")
        **kwargs: Additional parameters to pass to the converter
    
    Returns:
        list: List of (input_path, output_path, success) tuples
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all image files
    image_files = []
    
    if recursive:
        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith(file_extensions):
                    # Preserve relative path structure when recursive
                    rel_path = os.path.relpath(root, input_folder)
                    if rel_path != '.':
                        # Create corresponding output subfolder
                        output_subfolder = os.path.join(output_folder, rel_path)
                        os.makedirs(output_subfolder, exist_ok=True)
                        output_file = os.path.join(output_subfolder, os.path.splitext(file)[0] + '.svg')
                    else:
                        output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.svg')
                    
                    image_files.append((os.path.join(root, file), output_file))
    else:
        for file in os.listdir(input_folder):
            if file.lower().endswith(file_extensions):
                input_file = os.path.join(input_folder, file)
                output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.svg')
                image_files.append((input_file, output_file))
    
    if not image_files:
        raise ValueError(f"No image files found in {input_folder}")
    
    print(f"Found {len(image_files)} images to convert")
    
    # Initialize converter
    converter = Img2Vector()
    
    # Process function for each worker
    def process_image(input_output_pair):
        input_path, output_path = input_output_pair
        try:
            converter.convert(
                input_path,
                output_path=output_path,
                auto_optimize=auto_optimize,
                preprocessing_level=preprocessing_level,
                **kwargs
            )
            return (input_path, output_path, True)  # Success
        except Exception as e:
            print(f"Error converting {input_path}: {str(e)}")
            return (input_path, output_path, False)  # Failed
    
    # Process images in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Use tqdm for progress bar
        for result in tqdm(
            executor.map(process_image, image_files),
            total=len(image_files),
            desc="Converting images"
        ):
            results.append(result)
    
    # Summary
    successful = sum(1 for _, _, success in results if success)
    print(f"Conversion complete: {successful}/{len(results)} images successfully converted")
    
    return results