"""
SVG optimization tools for img2vector.

This module provides functions to optimize SVG files after conversion
to reduce file size and improve rendering performance.
"""

import re
import os
import subprocess
import tempfile
from xml.dom import minidom

def install_svgo():
    """
    Check if SVGO is installed, and install it if not.
    
    SVGO is a Node.js tool for optimizing SVG files.
    """
    try:
        # Check if SVGO is installed
        result = subprocess.run(['svgo', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               check=False)
        if result.returncode != 0:
            raise FileNotFoundError("SVGO not found")
    except (FileNotFoundError, subprocess.SubprocessError):
        print("SVGO not found. Attempting to install...")
        try:
            # Install SVGO globally
            subprocess.run(['npm', 'install', '-g', 'svgo'], 
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=True)
            print("SVGO installed successfully")
        except Exception as e:
            print(f"Failed to install SVGO: {str(e)}")
            print("Please install SVGO manually: npm install -g svgo")
            return False
    return True

def optimize_svg(svg_path, output_path=None, level='moderate'):
    """
    Optimize an SVG file to reduce file size.
    
    Args:
        svg_path (str): Path to SVG file
        output_path (str, optional): Path to save optimized SVG. If None, overwrites input file.
        level (str): Optimization level - 'light', 'moderate', or 'aggressive'
        
    Returns:
        tuple: (output_path, size_before, size_after, reduction_percentage)
    """
    if output_path is None:
        output_path = svg_path
    
    # Get file size before optimization
    size_before = os.path.getsize(svg_path)
    
    # Check if SVGO is available for better optimization
    svgo_available = install_svgo()
    
    if svgo_available:
        # Configure SVGO options based on optimization level
        if level == 'light':
            precision = 3
            plugins = [
                'cleanupAttrs',
                'removeDoctype',
                'removeXMLProcInst',
                'removeComments',
                'removeMetadata',
                'removeEditorsNSData',
                'cleanupEnableBackground',
                'convertPathData',
                'convertTransform',
                'removeEmptyAttrs',
                'removeEmptyContainers',
                'mergePaths',
                'removeUnusedNS',
                'sortDefsChildren'
            ]
        elif level == 'moderate':
            precision = 2
            plugins = [
                'cleanupAttrs',
                'removeDoctype',
                'removeXMLProcInst',
                'removeComments',
                'removeMetadata',
                'removeEditorsNSData',
                'cleanupEnableBackground',
                'convertPathData',
                'convertTransform',
                'removeEmptyAttrs',
                'removeEmptyContainers',
                'mergePaths',
                'removeUnusedNS',
                'sortDefsChildren',
                'removeUselessDefs',
                'cleanupNumericValues',
                'cleanupListOfValues',
                'convertColors',
                'removeUnknownsAndDefaults',
                'removeNonInheritableGroupAttrs',
                'removeUselessStrokeAndFill'
            ]
        else:  # aggressive
            precision = 1
            plugins = [
                'cleanupAttrs',
                'removeDoctype',
                'removeXMLProcInst',
                'removeComments',
                'removeMetadata',
                'removeEditorsNSData',
                'cleanupEnableBackground',
                'convertPathData',
                'convertTransform',
                'removeEmptyAttrs',
                'removeEmptyContainers',
                'mergePaths',
                'removeUnusedNS',
                'sortDefsChildren',
                'removeUselessDefs',
                'cleanupNumericValues',
                'cleanupListOfValues',
                'convertColors',
                'removeUnknownsAndDefaults',
                'removeNonInheritableGroupAttrs',
                'removeUselessStrokeAndFill',
                'removeViewBox',
                'cleanupIDs',
                'collapseGroups',
                'removeDimensions',
                'removeStyleElement',
                'removeScriptElement'
            ]
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as temp:
            config_path = temp.name
            temp.write(f"""
                module.exports = {{
                    plugins: [
                        {{
                            name: 'preset-default',
                            params: {{
                                overrides: {{
                                    {', '.join(f"'{plugin}': true" for plugin in plugins)},
                                    cleanupNumericValues: {{
                                        floatPrecision: {precision}
                                    }},
                                    convertPathData: {{
                                        floatPrecision: {precision}
                                    }}
                                }}
                            }}
                        }}
                    ]
                }};
            """)
        
        try:
            # Run SVGO with config
            subprocess.run([
                'svgo',
                '--config', config_path,
                '-i', svg_path,
                '-o', output_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Clean up temp file
            os.unlink(config_path)
        except Exception as e:
            print(f"SVGO optimization failed: {str(e)}")
            print("Falling back to basic optimization...")
            basic_optimize_svg(svg_path, output_path, level)
    else:
        # Fall back to basic optimization
        basic_optimize_svg(svg_path, output_path, level)
    
    # Get file size after optimization
    size_after = os.path.getsize(output_path)
    reduction_percentage = ((size_before - size_after) / size_before) * 100 if size_before > 0 else 0
    
    return (output_path, size_before, size_after, reduction_percentage)

def basic_optimize_svg(svg_path, output_path, level='moderate'):
    """
    Basic SVG optimization using Python's built-in XML tools.
    Less effective than SVGO but works without dependencies.
    
    Args:
        svg_path (str): Path to SVG file
        output_path (str): Path to save optimized SVG
        level (str): Optimization level - 'light', 'moderate', or 'aggressive'
    """
    try:
        # Parse the SVG file
        dom = minidom.parse(svg_path)
        
        # Get the SVG content as a string
        svg_str = dom.toxml()
        
        # Apply optimizations
        if level in ('moderate', 'aggressive'):
            # Remove comments
            svg_str = re.sub(r'<!--.*?-->', '', svg_str, flags=re.DOTALL)
            
            # Simplify decimal precision
            precision = 3 if level == 'moderate' else 1
            svg_str = re.sub(r'(\d+\.\d{' + str(precision+1) + r',})', 
                            lambda m: f"{float(m.group(1)):.{precision}f}", 
                            svg_str)
        
        if level == 'aggressive':
            # Remove unnecessary whitespace
            svg_str = re.sub(r'\s+', ' ', svg_str)
            svg_str = re.sub(r'> <', '><', svg_str)
        
        # Write optimized SVG
        with open(output_path, 'w') as f:
            f.write(svg_str)
            
    except Exception as e:
        print(f"Basic SVG optimization failed: {str(e)}")
        # If optimization fails, copy the original file
        with open(svg_path, 'rb') as src, open(output_path, 'wb') as dst:
            dst.write(src.read())