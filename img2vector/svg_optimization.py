"""
SVG optimization tools for img2vector.

This module provides functions to optimize SVG files after conversion
to reduce file size and improve rendering performance.
"""

import re
import os
import shutil
import subprocess
import tempfile
from xml.dom import minidom

# Extra SVGO plugins (on top of preset-default) for each optimization level
SVGO_LEVELS = {
    'light': {'precision': 3, 'plugins': []},
    'moderate': {'precision': 2, 'plugins': []},
    'aggressive': {
        'precision': 1,
        'plugins': ['removeDimensions', 'removeStyleElement', 'removeScriptElement'],
    },
}

def find_svgo():
    """
    Return the path to the SVGO executable, or None if it isn't installed.

    SVGO is a Node.js tool for optimizing SVG files (npm install -g svgo).
    """
    return shutil.which('svgo')

def install_svgo():
    """
    Check if SVGO is available.

    Kept for backwards compatibility. SVGO is no longer installed automatically;
    install it yourself with: npm install -g svgo
    """
    return find_svgo() is not None

def optimize_svg(svg_path, output_path=None, level='moderate'):
    """
    Optimize an SVG file to reduce file size.

    Uses SVGO if it is installed, otherwise falls back to a basic
    pure-Python optimizer.
    
    Args:
        svg_path (str): Path to SVG file
        output_path (str, optional): Path to save optimized SVG. If None, overwrites input file.
        level (str): Optimization level - 'light', 'moderate', or 'aggressive'
        
    Returns:
        tuple: (output_path, size_before, size_after, reduction_percentage)
    """
    if level not in SVGO_LEVELS:
        raise ValueError(f"Invalid level '{level}'. Choose from 'light', 'moderate', 'aggressive'.")

    if output_path is None:
        output_path = svg_path
    
    # Get file size before optimization
    size_before = os.path.getsize(svg_path)
    
    svgo = find_svgo()
    if svgo:
        if not run_svgo(svgo, svg_path, output_path, level):
            print("Falling back to basic optimization...")
            basic_optimize_svg(svg_path, output_path, level)
    else:
        # Fall back to basic optimization
        basic_optimize_svg(svg_path, output_path, level)
    
    # Get file size after optimization
    size_after = os.path.getsize(output_path)
    reduction_percentage = ((size_before - size_after) / size_before) * 100 if size_before > 0 else 0
    
    return (output_path, size_before, size_after, reduction_percentage)

def run_svgo(svgo, svg_path, output_path, level):
    """Run SVGO with settings for the given level. Returns True on success."""
    settings = SVGO_LEVELS[level]
    plugins = [
        "{ name: 'preset-default', params: { overrides: { "
        f"cleanupNumericValues: {{ floatPrecision: {settings['precision']} }}, "
        f"convertPathData: {{ floatPrecision: {settings['precision']} }} "
        "} } }"
    ] + [f"'{plugin}'" for plugin in settings['plugins']]

    # SVGO loads .cjs config files as CommonJS regardless of project settings
    with tempfile.NamedTemporaryFile('w', suffix='.cjs', delete=False, encoding='utf-8') as temp:
        config_path = temp.name
        temp.write(f"module.exports = {{ plugins: [{', '.join(plugins)}] }};\n")

    try:
        subprocess.run(
            [svgo, '--config', config_path, '-i', svg_path, '-o', output_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except (OSError, subprocess.SubprocessError) as e:
        detail = getattr(e, 'stderr', b'') or b''
        print(f"SVGO optimization failed: {str(e)} {detail.decode(errors='replace').strip()}")
        return False
    finally:
        os.unlink(config_path)

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
        
        # Remove comments
        svg_str = re.sub(r'<!--.*?-->', '', svg_str, flags=re.DOTALL)

        # Apply optimizations
        if level in ('moderate', 'aggressive'):
            # Remove whitespace between tags
            svg_str = re.sub(r'>\s+<', '><', svg_str)

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
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_str)
            
    except Exception as e:
        print(f"Basic SVG optimization failed: {str(e)}")
        # If optimization fails, copy the original file (unless optimizing in place)
        if os.path.abspath(svg_path) != os.path.abspath(output_path):
            shutil.copyfile(svg_path, output_path)