"""
Synkora API — Code Metrics Schemas

Pydantic models for representing code quality metrics at file, function,
class, and repository levels.
"""

from typing import Optional
from pydantic import BaseModel


class FunctionMetrics(BaseModel):
    """Metrics for a single function or method."""
    name: str
    start_line: int
    end_line: int
    lines_of_code: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    cyclomatic_complexity: int = 1
    parameter_count: int = 0
    nesting_depth: int = 0
    is_async: bool = False
    is_method: bool = False
    cognitive_complexity: int = 0
    maintainability_index: float = 100.0

    @property
    def risk_level(self) -> str:
        """Categorize function risk based on complexity."""
        if self.cyclomatic_complexity <= 5:
            return "low"
        elif self.cyclomatic_complexity <= 10:
            return "moderate"
        elif self.cyclomatic_complexity <= 20:
            return "high"
        return "critical"


class ClassMetrics(BaseModel):
    """Metrics for a single class."""
    name: str
    start_line: int
    end_line: int
    lines_of_code: int = 0
    method_count: int = 0
    avg_method_complexity: float = 0.0
    max_method_complexity: int = 0
    base_class_count: int = 0
    cohesion_score: float = 1.0  # LCOM-like metric (0-1, higher = more cohesive)

    @property
    def risk_level(self) -> str:
        if self.avg_method_complexity <= 5:
            return "low"
        elif self.avg_method_complexity <= 10:
            return "moderate"
        return "high"


class FileMetrics(BaseModel):
    """Metrics for a single source file."""
    filepath: str
    language: str
    total_lines: int = 0
    code_lines: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    import_count: int = 0
    function_count: int = 0
    class_count: int = 0
    avg_complexity: float = 0.0
    max_complexity: int = 0
    maintainability_index: float = 100.0
    tech_debt_minutes: float = 0.0
    functions: list[FunctionMetrics] = []
    classes: list[ClassMetrics] = []

    @property
    def risk_level(self) -> str:
        if self.avg_complexity <= 5 and self.maintainability_index >= 65:
            return "low"
        elif self.avg_complexity <= 10 and self.maintainability_index >= 40:
            return "moderate"
        return "high"


class RepositoryMetrics(BaseModel):
    """Aggregated metrics across an entire repository."""
    total_files: int = 0
    total_lines: int = 0
    total_code_lines: int = 0
    total_blank_lines: int = 0
    total_comment_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    avg_complexity: float = 0.0
    max_complexity: int = 0
    avg_maintainability: float = 100.0
    total_tech_debt_minutes: float = 0.0
    language_breakdown: dict[str, int] = {}  # lang -> lines of code
    risk_distribution: dict[str, int] = {}   # risk level -> function count
    high_risk_functions: list[FunctionMetrics] = []  # Top complex functions
    file_metrics: list[FileMetrics] = []

    @property
    def tech_debt_hours(self) -> float:
        return round(self.total_tech_debt_minutes / 60, 1)

    @property
    def comment_ratio(self) -> float:
        if self.total_code_lines == 0:
            return 0.0
        return round(self.total_comment_lines / self.total_code_lines * 100, 1)
