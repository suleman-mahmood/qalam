import os
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from collections import defaultdict

# Download and build the Python grammar for Tree-sitter
PYTHON_LANGUAGE = Language(tspython.language())


def parse_file(file_path):
    parser = Parser(PYTHON_LANGUAGE)

    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    tree = parser.parse(bytes(source_code, "utf-8"))
    return tree, source_code


def get_imports(tree, source_code):
    query = PYTHON_LANGUAGE.query("""
    (import_from_statement
        module_name: (dotted_name) @module_name) @import_from
    
    (import_statement
        name: (dotted_name) @import_name) @import
    """)

    imports = []
    captures = query.captures(tree.root_node)

    for node, tags in captures.items():
        if node == "module_name" or node == "import_name":
            for t in tags:
                imports.append(source_code[t.start_byte : t.end_byte])

    return imports


def get_classes_and_functions(tree, source_code):
    class_query = PYTHON_LANGUAGE.query("""
    (class_definition
        name: (identifier) @class_name) @class
    """)

    function_query = PYTHON_LANGUAGE.query("""
    (function_definition
        name: (identifier) @function_name) @function
    """)

    classes = []
    functions = []

    for node, tags in class_query.captures(tree.root_node).items():
        if node == "class_name":
            for t in tags:
                classes.append(source_code[t.start_byte : t.end_byte])

    for node, tags in function_query.captures(tree.root_node).items():
        if node == "function_name":
            for t in tags:
                functions.append(source_code[t.start_byte : t.end_byte])

    return classes, functions


def analyze_directory(directory):
    structure = defaultdict(lambda: {"classes": [], "functions": [], "imports": []})

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                tree, source_code = parse_file(file_path)

                classes, functions = get_classes_and_functions(tree, source_code)
                imports = get_imports(tree, source_code)

                structure[file_path]["classes"] = classes
                structure[file_path]["functions"] = functions
                structure[file_path]["imports"] = imports

    # Add file relationships based on imports
    # BUG: Doesn't work

    # for file_path, data in structure.items():
    #     data["imported_by"] = []
    #     imported_modules = [imp.split(".")[0] for imp in data["imports"]]
    #
    #     for other_file, other_data in structure.items():
    #         module_name = os.path.splitext(os.path.basename(other_file))[0]
    #         if module_name in imported_modules:
    #             other_data["imported_by"].append(file_path)

    return structure


if __name__ == "__main__":
    directory = input("Enter directory path to analyze: ")
    result = analyze_directory(directory)

    # Print results
    for file, data in result.items():
        print(f"\nFile: {file}")
        print(f"Classes: {data['classes']}")
        print(f"Functions: {data['functions']}")
        print(f"Imports: {data['imports']}")
        print(f"Imported by: {data['imported_by']}")
