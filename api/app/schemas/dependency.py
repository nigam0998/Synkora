"""
Synkora API — Dependency Graph Schemas

Pydantic models for representing dependency relationships between
files, modules, and packages in a codebase.
"""

from typing import Optional
from pydantic import BaseModel


class DependencyNode(BaseModel):
    """A node in the dependency graph representing a source file."""
    id: str                     # Unique identifier (relative filepath)
    filepath: str               # Relative path from repo root
    language: str
    lines_of_code: int = 0
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    in_degree: int = 0          # Number of files that import this file
    out_degree: int = 0         # Number of files this file imports
    is_entry_point: bool = False  # No incoming deps (leaf consumer)
    is_utility: bool = False    # High in_degree, used by many files

    @property
    def coupling_score(self) -> float:
        """Higher = more coupled (many connections)."""
        return self.in_degree + self.out_degree

    @property
    def instability(self) -> float:
        """
        Robert C. Martin's Instability metric.
        I = out_degree / (in_degree + out_degree)
        0.0 = maximally stable (many dependents, few deps)
        1.0 = maximally unstable (few dependents, many deps)
        """
        total = self.in_degree + self.out_degree
        if total == 0:
            return 0.5
        return round(self.out_degree / total, 2)


class DependencyEdge(BaseModel):
    """An edge representing an import relationship."""
    source: str       # File that imports (relative path)
    target: str       # File being imported (relative path)
    import_names: list[str] = []  # Specific items imported
    is_type_import: bool = False  # TypeScript type-only import


class CircularDependency(BaseModel):
    """A detected circular dependency chain."""
    cycle: list[str]  # List of file paths forming the cycle
    length: int       # Number of files in the cycle

    @property
    def severity(self) -> str:
        if self.length <= 2:
            return "warning"
        elif self.length <= 4:
            return "moderate"
        return "critical"


class DependencyGraph(BaseModel):
    """The complete dependency graph for a repository."""
    nodes: list[DependencyNode] = []
    edges: list[DependencyEdge] = []
    circular_dependencies: list[CircularDependency] = []
    total_files: int = 0
    total_edges: int = 0
    avg_in_degree: float = 0.0
    avg_out_degree: float = 0.0
    max_in_degree: int = 0
    max_out_degree: int = 0
    most_depended_on: list[str] = []   # Top files by in_degree
    most_dependent: list[str] = []     # Top files by out_degree
    hotspots: list[str] = []           # Files with high coupling

    @property
    def has_circular_deps(self) -> bool:
        return len(self.circular_dependencies) > 0

    @property
    def circular_dep_count(self) -> int:
        return len(self.circular_dependencies)
