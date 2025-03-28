import os

def display_structure(path='.', indent=0, max_depth=None, exclude_dirs=None):
    """
    Display the directory structure starting from the given path.
    
    Parameters:
        path (str): The path to start from. Default is current directory.
        indent (int): The current indentation level.
        max_depth (int): Maximum depth to traverse. None for unlimited.
        exclude_dirs (list): List of directory names to exclude.
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', '.venv', 'venv', '.idea', '.vs', 'node_modules']
    
    if max_depth is not None and indent > max_depth:
        return
    
    if os.path.isdir(path):
        # Print directory name
        print('  ' * indent + '├── ' + os.path.basename(path) + '/')
        
        # List items in directory
        items = sorted(os.listdir(path))
        for i, item in enumerate(items):
            item_path = os.path.join(path, item)
            
            # Skip excluded directories
            if os.path.isdir(item_path) and item in exclude_dirs:
                continue
                
            # Recursively display subdirectories and files
            display_structure(item_path, indent + 1, max_depth, exclude_dirs)
    else:
        # Print file name
        print('  ' * indent + '├── ' + os.path.basename(path))

if __name__ == "__main__":
    import sys
    
    # Get path from command line arguments, or use current directory
    target_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    # Display structure with optional depth limit
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"Structure of {os.path.abspath(target_path)}:")
    display_structure(target_path, 0, max_depth)