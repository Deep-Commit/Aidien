import os
import json
from typing import Dict, Any
from tree_sitter_language_pack import get_language, get_parser
from .file_processor import FileProcessor

def detect_language(filename: str) -> str:
    """
    Detects the programming language based on the file extension.
    """
    ext = filename.split(".")[-1]
    return FileProcessor.SUPPORTED_LANGUAGES.get(ext, None)


def get_ast_for_file(filename: str) -> Dict[str, Any]:
    """
    Extracts top-level AST elements (imports, functions, classes) from a file.
    Uses tree-sitter-language-pack to support multiple languages.
    """
    lang = detect_language(filename)
    if not lang:
        return {"error": f"Unsupported language for {filename}"}

    parser = get_parser(lang)
    language_obj = get_language(lang)

    with open(filename, "r", encoding="utf-8") as f:
        source_code = f.read()
    source_bytes = source_code.encode("utf-8")
    tree = parser.parse(source_bytes)
    root_node = tree.root_node

    ast_summary = []
    for child in root_node.children:
        if "import" in child.type or child.type == "using_declaration":
            ast_summary.append({
                "type": "import",
                "text": source_code[child.start_byte:child.end_byte]
            })
        elif "class" in child.type:
            name_node = child.child_by_field_name("name")
            if name_node:
                try:
                    name_text = name_node.text.decode("utf-8")
                except AttributeError:
                    name_text = name_node.text
                ast_summary.append({"type": "class", "name": name_text})
        elif "function" in child.type or "method" in child.type:
            name_node = child.child_by_field_name("name")
            if name_node:
                try:
                    name_text = name_node.text.decode("utf-8")
                except AttributeError:
                    name_text = name_node.text
                ast_summary.append({"type": "function", "name": name_text})
    return {"filename": filename, "ast_summary": ast_summary} 