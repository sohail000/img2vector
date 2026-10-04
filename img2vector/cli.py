"""
Command line interface for img2vector.

This module provides a command-line interface for the img2vector library,
allowing easy conversion of images to SVG from the terminal.
"""

import os
import sys
import argparse
from pathlib import Path

# Import from the package
from .core.converter import convert_image
from .batch_processing import batch_convert
from .svg_optimization import optimize_svg, install_svgo

def create_parser():
    """Create the command line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="img2vector - Intelligent image to SVG converter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Single file conversion
    convert_parser = subparsers.add_parser(
        "convert", 
        help="Convert a single image to SVG"
    )
    convert_parser.add_argument(
        "input", 
        help="Input image file path"
    )
    convert_parser.add_argument(
        "-o", "--output", 
        help="Output SVG file path (default: <input_filename>.svg in current directory)"
    )
    
    # Batch conversion
    batch_parser = subparsers.add_parser(
        "batch", 
        help="Convert multiple images in a directory"
    )
    batch_parser.add_argument(
        "input_dir", 
        help="Input directory containing images"
    )
    batch_parser.add_argument(
        "-o", "--output-dir", 
        help="Output directory for SVG files (default: ./svg_output)",
        default="svg_output"
    )
    batch_parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Recursively process subdirectories"
    )
    batch_parser.add_argument(
        "-w", "--workers", 
        type=int, 
        default=4,
        help="Number of worker threads for parallel processing"
    )
    
    # Optimization
    optimize_parser = subparsers.add_parser(
        "optimize", 
        help="Optimize an existing SVG file"
    )
    optimize_parser.add_argument(
        "input", 
        help="Input SVG file or directory of SVG files"
    )
    optimize_parser.add_argument(
        "-o", "--output", 
        help="Output SVG file or directory (default: overwrite input)"
    )
    optimize_parser.add_argument(
        "-l", "--level", 
        choices=["light", "moderate", "aggressive"],
        default="moderate",
        help="Optimization level"
    )
    optimize_parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Recursively process subdirectories"
    )
    
    # Common arguments for conversion options
    for p in [convert_parser, batch_parser]:
        p.add_argument(
            "--no-auto-optimize", 
            action="store_true",
            help="Disable automatic parameter optimization"
        )
        p.add_argument(
            "--preprocessing", 
            choices=["none", "light", "medium", "heavy"],
            default="none",
            help="Preprocessing level"
        )
        p.add_argument(
            "--colormode", 
            choices=["color", "binary"],
            help="Color mode"
        )
        p.add_argument(
            "--hierarchical", 
            choices=["stacked", "cutout"],
            help="Hierarchical mode"
        )
        p.add_argument(
            "--mode", 
            choices=["spline", "polygon"],
            help="Path mode"
        )
        p.add_argument(
            "--optimize", 
            choices=["none", "light", "moderate", "aggressive"],
            default="none",
            help="SVG optimization level"
        )
        
        # Advanced options group
        adv_group = p.add_argument_group("Advanced Options")
        adv_group.add_argument("--filter-speckle", type=int, help="Speckle filtering level (0-20)")
        adv_group.add_argument("--color-precision", type=int, help="Color precision (1-10)")
        adv_group.add_argument("--layer-difference", type=int, help="Layer difference threshold (1-32)")
        adv_group.add_argument("--corner-threshold", type=int, help="Corner detection threshold (0-180)")
        adv_group.add_argument("--length-threshold", type=float, help="Length threshold (0-10)")
        adv_group.add_argument("--max-iterations", type=int, help="Maximum iterations (1-20)")
        adv_group.add_argument("--splice-threshold", type=int, help="Splice threshold (0-90)")
        adv_group.add_argument("--path-precision", type=int, help="Path precision (1-10)")
    
    # UI command
    ui_parser = subparsers.add_parser(
        "ui", 
        help="Launch the web user interface"
    )
    ui_parser.add_argument(
        "--port", 
        type=int,
        default=7860,
        help="Port to run the UI on"
    )
    ui_parser.add_argument(
        "--share", 
        action="store_true",
        help="Create a public link for the UI"
    )
    
    return parser

def get_conversion_kwargs(args):
    """Extract conversion keyword arguments from parsed args."""
    kwargs = {}
    
    # Only include non-None values
    if args.colormode:
        kwargs["colormode"] = args.colormode
    if args.hierarchical:
        kwargs["hierarchical"] = args.hierarchical
    if args.mode:
        kwargs["mode"] = args.mode
    if args.filter_speckle is not None:
        kwargs["filter_speckle"] = args.filter_speckle
    if args.color_precision is not None:
        kwargs["color_precision"] = args.color_precision
    if args.layer_difference is not None:
        kwargs["layer_difference"] = args.layer_difference
    if args.corner_threshold is not None:
        kwargs["corner_threshold"] = args.corner_threshold
    if args.length_threshold is not None:
        kwargs["length_threshold"] = args.length_threshold
    if args.max_iterations is not None:
        kwargs["max_iterations"] = args.max_iterations
    if args.splice_threshold is not None:
        kwargs["splice_threshold"] = args.splice_threshold
    if args.path_precision is not None:
        kwargs["path_precision"] = args.path_precision
    
    return kwargs

def run_cli():
    """Run the command-line interface."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "convert":
            # Single file conversion
            if not os.path.isfile(args.input):
                print(f"Error: Input file '{args.input}' does not exist.")
                return 1
            
            # Default output path if not specified
            if not args.output:
                input_path = Path(args.input)
                args.output = str(input_path.with_suffix('.svg'))
            
            print(f"Converting '{args.input}' to '{args.output}'...")
            
            # Extract conversion options
            kwargs = get_conversion_kwargs(args)
            
            # Convert the image
            convert_image(
                args.input,
                args.output,
                auto_optimize=not args.no_auto_optimize,
                preprocessing_level=args.preprocessing,
                **kwargs
            )
            
            print(f"Conversion successful: '{args.output}'")
            
            # Apply SVG optimization if requested
            if args.optimize != "none":
                print(f"Optimizing SVG with '{args.optimize}' level...")
                result = optimize_svg(args.output, level=args.optimize)
                _, size_before, size_after, reduction = result
                print(f"Optimization reduced file size by {reduction:.1f}% " + 
                      f"({size_before/1024:.1f} KB → {size_after/1024:.1f} KB)")
        
        elif args.command == "batch":
            # Batch conversion
            if not os.path.isdir(args.input_dir):
                print(f"Error: Input directory '{args.input_dir}' does not exist.")
                return 1
            
            # Ensure output directory exists
            os.makedirs(args.output_dir, exist_ok=True)
            
            print(f"Batch converting images from '{args.input_dir}' to '{args.output_dir}'...")
            print(f"Using {args.workers} workers and {'recursive mode' if args.recursive else 'non-recursive mode'}")
            
            # Extract conversion options
            kwargs = get_conversion_kwargs(args)
            
            # Perform batch conversion
            results = batch_convert(
                args.input_dir,
                args.output_dir,
                num_workers=args.workers,
                recursive=args.recursive,
                auto_optimize=not args.no_auto_optimize,
                preprocessing_level=args.preprocessing,
                **kwargs
            )
            
            # Count successes and failures
            successes = sum(1 for _, _, success in results if success)
            failures = len(results) - successes
            
            print(f"\nBatch conversion completed: {successes} succeeded, {failures} failed.")
            
            # Apply SVG optimization if requested
            if args.optimize != "none" and successes > 0:
                print(f"Optimizing SVGs with '{args.optimize}' level...")
                optimization_results = []
                for _, output_path, success in results:
                    if success:
                        try:
                            result = optimize_svg(output_path, level=args.optimize)
                            optimization_results.append(result)
                        except Exception as e:
                            print(f"Optimization failed for {output_path}: {str(e)}")
                
                # Calculate total savings
                if optimization_results:
                    total_before = sum(before for _, before, _, _ in optimization_results)
                    total_after = sum(after for _, _, after, _ in optimization_results)
                    total_reduction = ((total_before - total_after) / total_before) * 100 if total_before > 0 else 0
                    
                    print(f"Optimization reduced total file size by {total_reduction:.1f}% " + 
                          f"({total_before/1024:.1f} KB → {total_after/1024:.1f} KB)")
        
        elif args.command == "optimize":
            # SVG optimization
            if os.path.isfile(args.input):
                # Single file optimization
                output_path = args.output if args.output else args.input
                
                print(f"Optimizing '{args.input}' with '{args.level}' level...")
                result = optimize_svg(args.input, output_path, args.level)
                _, size_before, size_after, reduction = result
                
                print(f"Optimization reduced file size by {reduction:.1f}% " + 
                      f"({size_before/1024:.1f} KB → {size_after/1024:.1f} KB)")
            
            elif os.path.isdir(args.input):
                # Directory optimization
                output_dir = args.output if args.output else args.input
                os.makedirs(output_dir, exist_ok=True)
                
                # Find SVG files
                svg_files = []
                
                if args.recursive:
                    for root, _, files in os.walk(args.input):
                        for file in files:
                            if file.lower().endswith('.svg'):
                                # Preserve relative path structure
                                rel_path = os.path.relpath(root, args.input)
                                input_file = os.path.join(root, file)
                                
                                if rel_path != '.':
                                    # Create corresponding output subfolder
                                    output_subfolder = os.path.join(output_dir, rel_path)
                                    os.makedirs(output_subfolder, exist_ok=True)
                                    output_file = os.path.join(output_subfolder, file)
                                else:
                                    output_file = os.path.join(output_dir, file)
                                
                                svg_files.append((input_file, output_file))
                else:
                    for file in os.listdir(args.input):
                        if file.lower().endswith('.svg'):
                            input_file = os.path.join(args.input, file)
                            output_file = os.path.join(output_dir, file)
                            svg_files.append((input_file, output_file))
                
                if not svg_files:
                    print(f"No SVG files found in '{args.input}'")
                    return 1
                
                print(f"Optimizing {len(svg_files)} SVG files with '{args.level}' level...")
                
                # Process all SVG files
                total_before = 0
                total_after = 0
                
                for i, (input_file, output_file) in enumerate(svg_files):
                    try:
                        print(f"[{i+1}/{len(svg_files)}] Optimizing '{input_file}'...")
                        result = optimize_svg(input_file, output_file, args.level)
                        _, size_before, size_after, reduction = result
                        
                        total_before += size_before
                        total_after += size_after
                        
                        print(f"  Reduced by {reduction:.1f}% ({size_before/1024:.1f} KB → {size_after/1024:.1f} KB)")
                    except Exception as e:
                        print(f"  Error: {str(e)}")
                
                # Calculate total savings
                total_reduction = ((total_before - total_after) / total_before) * 100 if total_before > 0 else 0
                print(f"\nTotal optimization reduced file size by {total_reduction:.1f}% " + 
                      f"({total_before/1024:.1f} KB → {total_after/1024:.1f} KB)")
            
            else:
                print(f"Error: Input path '{args.input}' does not exist.")
                return 1
        
        elif args.command == "ui":
            # Launch the web UI
            from .app import create_interface
            
            print(f"Starting img2vector web interface on port {args.port}...")
            app = create_interface()
            app.launch(server_port=args.port, share=args.share)
        
        return 0  # Success
    
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
        return 130  # Standard Unix exit code for SIGINT
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1  # General error

def main():
    """Entry point for the CLI."""
    sys.exit(run_cli())

if __name__ == "__main__":
    main()