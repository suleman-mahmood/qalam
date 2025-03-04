import os
from pydantic import BaseModel
import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser
from collections import defaultdict

# Download and build the Python grammar for Tree-sitter
PYTHON_LANGUAGE = Language(tspython.language())


class PythonFileAnalysis(BaseModel):
    file_path: str
    classes: list[str]
    functions: list[str]
    imports: list[str]


class StaticAnalyser:
    def __init__(self) -> None:
        self.parser = Parser(PYTHON_LANGUAGE)

    def get_imports(self, tree, source_code):
        query = PYTHON_LANGUAGE.query(
            """
            (import_from_statement
                module_name: (dotted_name) @module_name) @import_from
            
            (import_statement
                name: (dotted_name) @import_name) @import
            """
        )

        imports = []
        captures = query.captures(tree.root_node)

        for node, tags in captures.items():
            if node == "module_name" or node == "import_name":
                for t in tags:
                    imports.append(source_code[t.start_byte : t.end_byte])

        return imports

    def get_qualified_name(self, node: Node, source_code):
        """Get fully qualified name with parent hierarchy"""
        hierarchy = []
        current_node = node.parent
        if current_node:
            current_node = current_node.parent

        while current_node:
            if current_node.type in ["class_definition", "function_definition"]:
                # Extract class / function name
                for child in current_node.children:
                    if child.type == "identifier":
                        hierarchy.append(source_code[child.start_byte : child.end_byte])
                        break
            current_node = current_node.parent

        return ".".join(reversed(hierarchy))

    def get_classes_and_functions(self, tree, source_code):
        """Capture all classes and functions with their hierarchy"""
        query = PYTHON_LANGUAGE.query(
            """
            (class_definition
                name: (identifier) @class_name) @class_def
            
            (function_definition
                name: (identifier) @func_name) @func_def
            """
        )

        results = {"classes": [], "functions": []}

        for node, tags in query.captures(tree.root_node).items():
            if node in ["class_name", "func_name"]:
                for t in tags:
                    class_func_name = source_code[t.start_byte : t.end_byte]
                    parent_hierarchy = self.get_qualified_name(t, source_code)
                    qualified_name = (
                        f"{parent_hierarchy}.{class_func_name}"
                        if parent_hierarchy
                        else class_func_name
                    )
                    if node == "class_name":
                        results["classes"].append(qualified_name)
                    elif node == "func_name":
                        results["functions"].append(qualified_name)

        return results

    def parse_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        tree = self.parser.parse(bytes(source_code, "utf-8"))
        return tree, source_code

    def analyze_directory(self, directory) -> list[PythonFileAnalysis]:
        structure = defaultdict(
            lambda: {"classes": [], "functions": [], "imports": [], "imported_by": []}
        )

        # First pass: collect all declarations
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith(".py") or file.startswith("__init__.py"):
                    continue

                file_path = os.path.join(root, file)

                tree, source_code = self.parse_file(file_path)

                declarations = self.get_classes_and_functions(tree, source_code)
                imports = self.get_imports(tree, source_code)

                structure[file_path].update(
                    {
                        "classes": declarations["classes"],
                        "functions": declarations["functions"],
                        "imports": imports,
                    }
                )

        return [
            PythonFileAnalysis(
                file_path=os.path.relpath(file_path, directory),
                classes=data.get("classes", []),
                functions=data.get("functions", []),
                imports=data.get("imports", []),
            )
            for file_path, data in structure.items()
        ]

        # BUG: Doesn't work
        # Second pass: resolve relationships

        # for file_path, data in structure.items():
        #     for imp in data["imports"]:
        #         # Simple module resolution (expand for packages as needed)
        #         target_module = imp.split(".")[0]
        #         target_path = None
        #
        #         # Find matching files
        #         for fpath in structure:
        #             if os.path.splitext(os.path.basename(fpath))[0] == target_module:
        #                 target_path = fpath
        #                 break
        #
        #         if target_path and target_path != file_path:
        #             structure[target_path]["imported_by"].append(file_path)
        #
