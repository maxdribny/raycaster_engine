import os


def count_lines_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for line in f)


def count_lines_in_directory(directory):
    total_lines = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_lines += count_lines_in_file(filepath)

    return total_lines


directory_path = input("Enter the directory path: ")
print(f"Total lines of Python code in {directory_path}: {count_lines_in_directory(directory_path)}")
