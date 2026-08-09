"""
Synkora API — AST Parsing Service

Service for parsing source code into Abstract Syntax Trees (ASTs) using Tree-sitter.
Extracts structural elements (functions, classes, imports) for code analysis.

Uses tree-sitter 0.26.x with recursive tree-walking (version-agnostic approach).
"""

from pathlib import Path
from typing import Optional

import tree_sitter
from tree_sitter import Language, Parser

import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript
import tree_sitter_go
import tree_sitter_rust

from app.schemas.ast import ParsedFile, FunctionDef, ClassDef, ImportDef
from app.core.logging import get_logger

logger = get_logger("ast_service")

# ── Load Language Bindings ───────────────────────────────────────────────────
LANGUAGES = {
    "python": Language(tree_sitter_python.language()),
    "javascript": Language(tree_sitter_javascript.language()),
    "typescript": Language(tree_sitter_typescript.language_typescript()),
    "tsx": Language(tree_sitter_typescript.language_tsx()),
    "go": Language(tree_sitter_go.language()),
    "rust": Language(tree_sitter_rust.language()),
}

# ── File Extension Mapping ───────────────────────────────────────────────────
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
}

# ── Node types that represent functions in each language ─────────────────────
FUNCTION_TYPES = {
    "python": {"function_definition"},
    "javascript": {"function_declaration", "arrow_function", "method_definition"},
    "typescript": {"function_declaration", "arrow_function", "method_definition"},
    "tsx": {"function_declaration", "arrow_function", "method_definition"},
    "go": {"function_declaration", "method_declaration"},
    "rust": {"function_item"},
}

# ── Node types that represent classes/structs in each language ───────────────
CLASS_TYPES = {
    "python": {"class_definition"},
    "javascript": {"class_declaration"},
    "typescript": {"class_declaration"},
    "tsx": {"class_declaration"},
    "go": {"type_declaration"},  # We'll check for struct_type inside
    "rust": {"struct_item", "enum_item", "impl_item"},
}

# ── Node types that represent imports in each language ───────────────────────
IMPORT_TYPES = {
    "python": {"import_statement", "import_from_statement"},
    "javascript": {"import_statement"},
    "typescript": {"import_statement"},
    "tsx": {"import_statement"},
    "go": {"import_declaration", "import_spec"},
    "rust": {"use_declaration"},
}


def _get_child_by_field(node, field_name: str):
    """Get a child node by field name."""
    return node.child_by_field_name(field_name)


def _get_node_text(node) -> str:
    """Get the text content of a node."""
    if node is None:
        return ""
    text = node.text
    return text.decode("utf-8") if text is not None else ""


def _find_name(node, lang: str) -> str:
    """Extract the name from a definition node."""
    # Try the 'name' field first (works for most languages)
    name_node = _get_child_by_field(node, "name")
    if name_node:
        return _get_node_text(name_node)

    # For arrow functions, try to find the parent variable declaration
    if node.type == "arrow_function" and node.parent:
        parent = node.parent
        if parent.type == "variable_declarator":
            name_node = _get_child_by_field(parent, "name")
            if name_node:
                return _get_node_text(name_node)

    return "<anonymous>"


def _extract_params(node, lang: str) -> list[str]:
    """Extract parameter names from a function definition."""
    params_node = _get_child_by_field(node, "parameters")
    if not params_node:
        return []

    params = []
    for child in params_node.children:
        if child.is_named:
            if child.type == "identifier":
                params.append(_get_node_text(child))
            elif child.type in ("typed_parameter", "typed_default_parameter"):
                name_node = _get_child_by_field(child, "name")
                if name_node:
                    params.append(_get_node_text(name_node))
            elif child.type == "default_parameter":
                name_node = _get_child_by_field(child, "name")
                if name_node:
                    params.append(_get_node_text(name_node))
    return params


def _extract_return_type(node, lang: str) -> Optional[str]:
    """Extract return type annotation from a function definition."""
    ret_node = _get_child_by_field(node, "return_type")
    if ret_node:
        return _get_node_text(ret_node).lstrip("-> ").strip()
    return None


def _extract_docstring(node, lang: str) -> Optional[str]:
    """Extract docstring from a function or class definition."""
    if lang != "python":
        return None

    body_node = _get_child_by_field(node, "body")
    if body_node and body_node.child_count > 0:
        first_stmt = body_node.children[0]
        if first_stmt.type == "expression_statement":
            expr = first_stmt.children[0] if first_stmt.child_count > 0 else None
            if expr and expr.type == "string":
                text = _get_node_text(expr)
                # Strip triple quotes
                for q in ('"""', "'''"):
                    if text.startswith(q) and text.endswith(q):
                        return text[3:-3].strip()
                return text.strip("\"'")
    return None


def _is_async(node, lang: str) -> bool:
    """Check if a function is async."""
    if lang == "python":
        # In Python, async functions have a parent that wraps them
        # or may have 'async' as a keyword child
        for child in node.children:
            if _get_node_text(child) == "async":
                return True
    if lang in ("javascript", "typescript", "tsx"):
        for child in node.children:
            if _get_node_text(child) == "async":
                return True
    if lang == "rust":
        for child in node.children:
            if _get_node_text(child) == "async":
                return True
    return False


def _extract_import_module(node, lang: str) -> Optional[str]:
    """Extract the module name from an import node."""
    if lang == "python":
        if node.type == "import_statement":
            name_node = _get_child_by_field(node, "name")
            if name_node:
                return _get_node_text(name_node)
        elif node.type == "import_from_statement":
            module_node = _get_child_by_field(node, "module_name")
            if module_node:
                return _get_node_text(module_node)
    elif lang in ("javascript", "typescript", "tsx"):
        source_node = _get_child_by_field(node, "source")
        if source_node:
            return _get_node_text(source_node).strip("\"'")
    elif lang == "go":
        if node.type == "import_spec":
            path_node = _get_child_by_field(node, "path")
            if path_node:
                return _get_node_text(path_node).strip("\"'")
        elif node.type == "import_declaration":
            # Skip the declaration itself; we handle import_spec children
            return None
    elif lang == "rust":
        arg_node = _get_child_by_field(node, "argument")
        if arg_node:
            return _get_node_text(arg_node)
    return None


class ASTService:
    """Service for parsing source code into ASTs and extracting metadata."""

    @staticmethod
    def get_language_from_extension(filepath: Path) -> Optional[str]:
        """Determine the programming language from file extension."""
        return EXTENSION_MAP.get(filepath.suffix.lower())

    @staticmethod
    def parse_file(filepath: Path) -> Optional[ParsedFile]:
        """
        Parse a source code file and extract its structural entities.

        Returns None if the language is unsupported or the file cannot be read.
        """
        lang_key = ASTService.get_language_from_extension(filepath)
        if not lang_key:
            return None

        language = LANGUAGES[lang_key]
        parser = Parser(language)

        try:
            source_code = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("unsupported_file_encoding", filepath=str(filepath))
            return None
        except Exception as e:
            logger.error("file_read_error", filepath=str(filepath), error=str(e))
            return None

        total_lines = len(source_code.splitlines())

        # Parse the source code into an AST
        source_bytes = source_code.encode("utf-8")
        tree = parser.parse(source_bytes)

        functions: list[FunctionDef] = []
        classes: list[ClassDef] = []
        imports: list[ImportDef] = []

        func_types = FUNCTION_TYPES.get(lang_key, set())
        class_types = CLASS_TYPES.get(lang_key, set())
        import_types = IMPORT_TYPES.get(lang_key, set())

        # ── Recursive tree walk ──────────────────────────────────────────
        def walk(node, is_method: bool = False):
            # Functions
            if node.type in func_types:
                name = _find_name(node, lang_key)
                params = _extract_params(node, lang_key)
                ret_type = _extract_return_type(node, lang_key)
                docstring = _extract_docstring(node, lang_key)
                is_async_fn = _is_async(node, lang_key)

                func = FunctionDef(
                    name=name,
                    start_line=node.start_point.row + 1,
                    end_line=node.end_point.row + 1,
                    parameters=params,
                    return_type=ret_type,
                    docstring=docstring,
                    is_async=is_async_fn,
                    is_method=is_method,
                )

                if is_method:
                    # Don't add to top-level, it will be added to the class
                    return func
                else:
                    functions.append(func)
                    # Don't recurse into function body for nested functions
                    return None

            # Classes
            if node.type in class_types:
                # For Go, only match struct type declarations
                if lang_key == "go" and node.type == "type_declaration":
                    has_struct = False
                    for child in node.children:
                        if child.type == "type_spec":
                            for sc in child.children:
                                if sc.type == "struct_type":
                                    has_struct = True
                    if not has_struct:
                        return None

                name = _find_name(node, lang_key)
                docstring = _extract_docstring(node, lang_key)

                # Find methods inside the class body
                methods = []
                body_node = _get_child_by_field(node, "body")
                if body_node:
                    for child in body_node.children:
                        if child.type in func_types:
                            method = walk(child, is_method=True)
                            if method:
                                methods.append(method)

                # Extract base classes (Python)
                base_classes = []
                if lang_key == "python":
                    superclasses_node = _get_child_by_field(node, "superclasses")
                    if superclasses_node:
                        for child in superclasses_node.children:
                            if child.is_named:
                                base_classes.append(_get_node_text(child))

                classes.append(
                    ClassDef(
                        name=name,
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        docstring=docstring,
                        methods=methods,
                        base_classes=base_classes,
                    )
                )
                return None

            # Imports
            if node.type in import_types:
                module = _extract_import_module(node, lang_key)
                if module:
                    imports.append(ImportDef(module=module))
                # For Go import declarations, recurse to find import_spec children
                if lang_key == "go" and node.type == "import_declaration":
                    for child in node.children:
                        walk(child)
                return None

            # Recurse into children
            for child in node.children:
                walk(child)

        walk(tree.root_node)

        return ParsedFile(
            filepath=str(filepath),
            language=lang_key,
            total_lines=total_lines,
            functions=functions,
            classes=classes,
            imports=imports,
        )
