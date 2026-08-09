"""
Synkora API — AST Models

Pydantic models for representing data extracted via AST parsing.
These models standardize the structural information across different languages.
"""

from typing import Optional
from pydantic import BaseModel


class EntityDef(BaseModel):
    """Base model for any parsed entity."""
    name: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None


class FunctionDef(EntityDef):
    """Represents a function or method definition."""
    parameters: list[str] = []
    return_type: Optional[str] = None
    is_async: bool = False
    is_method: bool = False
    complexity: Optional[int] = None  # Cyclomatic complexity (calculated later)


class ClassDef(EntityDef):
    """Represents a class definition."""
    methods: list[FunctionDef] = []
    base_classes: list[str] = []


class ImportDef(BaseModel):
    """Represents a module import."""
    module: str
    imported_names: list[str] = []  # e.g., ["Component", "useState"]
    is_type_import: bool = False


class ParsedFile(BaseModel):
    """The complete representation of a parsed source file."""
    filepath: str
    language: str
    total_lines: int
    functions: list[FunctionDef] = []
    classes: list[ClassDef] = []
    imports: list[ImportDef] = []
    
    @property
    def total_functions(self) -> int:
        return len(self.functions) + sum(len(c.methods) for c in self.classes)
    
    @property
    def total_classes(self) -> int:
        return len(self.classes)
