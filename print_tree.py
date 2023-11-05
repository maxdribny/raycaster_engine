import os


def print_tree(directory, depth, max_depth, ignore_list):
    # Check if maximum depth is reached
    if depth > max_depth:
        return

    # Check if current directory is in ignore_list
    if os.path.basename(directory) in ignore_list:
        return

    # Print indentation for current depth
    indent = '    ' * depth

    # Print the current directory name
    print(f'{indent}{os.path.basename(directory)}/')

    # Loop over all files and directories in the current directory
    for filename in os.listdir(directory):
        # Skip files/directories in ignore_list
        if filename in ignore_list:
            continue

        filepath = os.path.join(directory, filename)

        # If it's a directory, recursively print its content to a certain depth
        if os.path.isdir(filepath):
            print_tree(filepath, depth + 1, max_depth, ignore_list)
        else:
            # If it's a file, just print its name
            print(f'{indent}    {filename}')


# Example usage
print_tree('.', 0, 2, ignore_list=[
    '__pycache__', 'pyopengl', 'build', 'dist', 'config',
    'venv', '__init__.py', 'main.spec', 'copyright.txt', 'lines_of_code.py',
    'print_tree.py', '.idea',
])
