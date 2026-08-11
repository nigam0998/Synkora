"""
Synkora API — Code Metrics Service

Calculates code quality metrics from AST-parsed data:
  - Cyclomatic Complexity (decision points in control flow)
  - Cognitive Complexity (how hard code is to understand)
  - Lines of Code breakdown (code, blank, comments)
  - Maintainability Index (composite quality score)
  - Technical Debt estimation (in minutes)
  - Nesting depth analysis
"""

import math
import re
from pathlib import Path
from typing import Optional

from app.schemas.ast import ParsedFile, FunctionDef as ASTFunction
from app.schemas.metrics import (
    FunctionMetrics,
    ClassMetrics,
    FileMetrics,
    RepositoryMetrics,
)
from app.services.ast_service import ASTService
from app.core.logging import get_logger

logger = get_logger("metrics_service")

# ── Comment patterns per language ────────────────────────────────────────────
COMMENT_PATTERNS = {
    "python": re.compile(r"^\s*#"),
    "javascript": re.compile(r"^\s*//"),
    "typescript": re.compile(r"^\s*//"),
    "tsx": re.compile(r"^\s*//"),
    "go": re.compile(r"^\s*//"),
    "rust": re.compile(r"^\s*//"),
}

# ── Decision keywords that increase cyclomatic complexity ────────────────────
DECISION_KEYWORDS = {
    "python": {"if", "elif", "for", "while", "except", "with", "and", "or"},
    "javascript": {"if", "else if", "for", "while", "do", "case", "catch", "&&", "||", "??"},
    "typescript": {"if", "else if", "for", "while", "do", "case", "catch", "&&", "||", "??"},
    "tsx": {"if", "else if", "for", "while", "do", "case", "catch", "&&", "||", "??"},
    "go": {"if", "for", "case", "&&", "||"},
    "rust": {"if", "for", "while", "loop", "match", "&&", "||"},
}

# ── Nesting keywords ────────────────────────────────────────────────────────
NESTING_KEYWORDS = {
    "python": {"if", "elif", "else", "for", "while", "with", "try", "except", "def", "class"},
    "javascript": {"if", "else", "for", "while", "do", "switch", "try", "catch", "function"},
    "typescript": {"if", "else", "for", "while", "do", "switch", "try", "catch", "function"},
    "tsx": {"if", "else", "for", "while", "do", "switch", "try", "catch", "function"},
    "go": {"if", "else", "for", "switch", "select", "func"},
    "rust": {"if", "else", "for", "while", "loop", "match", "fn", "impl"},
}

# ── Tech debt cost (minutes per complexity point above threshold) ────────────
DEBT_MINUTES_PER_COMPLEXITY = 5.0
COMPLEXITY_THRESHOLD = 5


class MetricsService:
    """Service for calculating code quality metrics."""

    # ── Line Analysis ────────────────────────────────────────────────────────

    @staticmethod
    def analyze_lines(source: str, language: str) -> dict:
        """
        Break down source into code lines, blank lines, and comment lines.

        Returns: {"total": int, "code": int, "blank": int, "comment": int}
        """
        lines = source.splitlines()
        total = len(lines)
        blank = 0
        comment = 0
        in_block_comment = False
        comment_re = COMMENT_PATTERNS.get(language)

        for line in lines:
            stripped = line.strip()

            # Blank line
            if not stripped:
                blank += 1
                continue

            # Block comment detection (/* ... */ and """ ... """)
            if language in ("javascript", "typescript", "tsx", "go", "rust"):
                if in_block_comment:
                    comment += 1
                    if "*/" in stripped:
                        in_block_comment = False
                    continue
                if stripped.startswith("/*"):
                    comment += 1
                    if "*/" not in stripped:
                        in_block_comment = False  # single-line block
                        in_block_comment = True
                    continue

            if language == "python":
                if in_block_comment:
                    comment += 1
                    if '"""' in stripped or "'''" in stripped:
                        in_block_comment = False
                    continue
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    comment += 1
                    # Check if it's a single-line docstring
                    quote = stripped[:3]
                    if stripped.count(quote) >= 2 and len(stripped) > 3:
                        continue  # Single-line docstring
                    in_block_comment = True
                    continue

            # Single-line comment
            if comment_re and comment_re.match(line):
                comment += 1
                continue

        code = total - blank - comment
        return {"total": total, "code": max(code, 0), "blank": blank, "comment": comment}

    # ── Cyclomatic Complexity ────────────────────────────────────────────────

    @staticmethod
    def calculate_cyclomatic_complexity(
        source_lines: list[str], language: str
    ) -> int:
        """
        Calculate cyclomatic complexity by counting decision points.

        Starts at 1 (the function itself is one path) and increments
        for each decision keyword found.
        """
        complexity = 1
        keywords = DECISION_KEYWORDS.get(language, set())

        for line in source_lines:
            stripped = line.strip()
            # Skip comments and blank lines
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue

            for keyword in keywords:
                if keyword in ("&&", "||", "??"):
                    # Count operator occurrences
                    complexity += stripped.count(keyword)
                else:
                    # Check if keyword appears as a statement start
                    if re.match(rf"\b{re.escape(keyword)}\b", stripped):
                        complexity += 1

        return complexity

    # ── Cognitive Complexity ─────────────────────────────────────────────────

    @staticmethod
    def calculate_cognitive_complexity(
        source_lines: list[str], language: str
    ) -> int:
        """
        Calculate cognitive complexity — a measure of how hard code is
        to understand (unlike cyclomatic, nesting increases the penalty).
        """
        cognitive = 0
        nesting_level = 0
        nesting_kws = NESTING_KEYWORDS.get(language, set())
        indent_stack: list[int] = []

        for line in source_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue

            # Track indentation for nesting
            indent = len(line) - len(line.lstrip())

            # Pop nesting levels when indentation decreases
            while indent_stack and indent <= indent_stack[-1]:
                indent_stack.pop()
                nesting_level = max(0, nesting_level - 1)

            for keyword in nesting_kws:
                if re.match(rf"\b{re.escape(keyword)}\b", stripped):
                    # Structural increment + nesting penalty
                    cognitive += 1 + nesting_level

                    # Push nesting for block-opening keywords
                    if keyword not in ("else", "elif", "except", "catch"):
                        indent_stack.append(indent)
                        nesting_level += 1
                    break  # Only count the first keyword per line

        return cognitive

    # ── Nesting Depth ────────────────────────────────────────────────────────

    @staticmethod
    def calculate_max_nesting(source_lines: list[str], language: str) -> int:
        """Calculate the maximum nesting depth in a block of code."""
        max_depth = 0
        current_depth = 0

        if language == "python":
            base_indent: Optional[int] = None
            for line in source_lines:
                stripped = line.strip()
                if not stripped:
                    continue
                indent = len(line) - len(line.lstrip())
                if base_indent is None:
                    base_indent = indent
                relative = max(0, indent - base_indent)
                # Python uses 4 spaces per indent level typically
                depth = relative // 4
                max_depth = max(max_depth, depth)
        else:
            # For brace-based languages, count { and }
            for line in source_lines:
                stripped = line.strip()
                if not stripped:
                    continue
                current_depth += stripped.count("{") - stripped.count("}")
                max_depth = max(max_depth, current_depth)

        return max_depth

    # ── Maintainability Index ────────────────────────────────────────────────

    @staticmethod
    def calculate_maintainability_index(
        loc: int, complexity: int, comment_ratio: float
    ) -> float:
        """
        Calculate the Maintainability Index (MI).

        Based on the Software Engineering Institute formula:
        MI = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC) + 50 * sin(sqrt(2.4 * CM))

        Simplified version using LOC and complexity:
        MI = max(0, (171 - 5.2 * ln(LOC) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
        """
        if loc <= 0:
            return 100.0

        ln_loc = math.log(max(loc, 1))
        # Halstead Volume approximation (use LOC as proxy)
        ln_vol = math.log(max(loc * 5, 1))

        mi = 171 - 5.2 * ln_vol - 0.23 * complexity - 16.2 * ln_loc

        # Add comment bonus
        if comment_ratio > 0:
            mi += 50 * math.sin(math.sqrt(2.4 * min(comment_ratio, 1.0)))

        # Normalize to 0-100
        mi = max(0.0, min(100.0, mi * 100 / 171))

        return round(mi, 1)

    # ── Tech Debt Estimation ─────────────────────────────────────────────────

    @staticmethod
    def estimate_tech_debt(complexity: int, loc: int) -> float:
        """
        Estimate technical debt in minutes.

        Based on complexity above threshold + long functions penalty.
        """
        debt = 0.0

        # Complexity debt
        if complexity > COMPLEXITY_THRESHOLD:
            debt += (complexity - COMPLEXITY_THRESHOLD) * DEBT_MINUTES_PER_COMPLEXITY

        # Long function penalty (> 50 lines)
        if loc > 50:
            debt += (loc - 50) * 0.5

        # Very long function penalty (> 100 lines)
        if loc > 100:
            debt += (loc - 100) * 1.0

        return round(debt, 1)

    # ── File-Level Analysis ──────────────────────────────────────────────────

    @staticmethod
    def analyze_file(filepath: Path) -> Optional[FileMetrics]:
        """
        Perform a complete metrics analysis on a single source file.

        Combines AST parsing with line analysis, complexity calculation,
        and maintainability scoring.
        """
        # Parse the AST
        parsed = ASTService.parse_file(filepath)
        if not parsed:
            return None

        # Read source
        try:
            source = filepath.read_text(encoding="utf-8")
        except Exception:
            return None

        source_lines = source.splitlines()
        lang = parsed.language

        # Line breakdown
        line_info = MetricsService.analyze_lines(source, lang)

        # Analyze each function
        func_metrics: list[FunctionMetrics] = []
        all_complexities: list[int] = []

        for func in parsed.functions:
            func_lines = source_lines[func.start_line - 1 : func.end_line]
            func_loc = len([l for l in func_lines if l.strip()])

            cc = MetricsService.calculate_cyclomatic_complexity(func_lines, lang)
            cognitive = MetricsService.calculate_cognitive_complexity(func_lines, lang)
            nesting = MetricsService.calculate_max_nesting(func_lines, lang)
            comment_ratio = line_info["comment"] / max(line_info["code"], 1)
            mi = MetricsService.calculate_maintainability_index(func_loc, cc, comment_ratio)
            debt = MetricsService.estimate_tech_debt(cc, func_loc)

            all_complexities.append(cc)

            func_metrics.append(
                FunctionMetrics(
                    name=func.name,
                    start_line=func.start_line,
                    end_line=func.end_line,
                    lines_of_code=func_loc,
                    cyclomatic_complexity=cc,
                    cognitive_complexity=cognitive,
                    nesting_depth=nesting,
                    parameter_count=len(func.parameters),
                    is_async=func.is_async,
                    is_method=func.is_method,
                    maintainability_index=mi,
                )
            )

        # Analyze each class
        class_metrics: list[ClassMetrics] = []

        for cls in parsed.classes:
            method_complexities: list[int] = []

            for method in cls.methods:
                method_lines = source_lines[method.start_line - 1 : method.end_line]
                mc = MetricsService.calculate_cyclomatic_complexity(method_lines, lang)
                method_complexities.append(mc)
                all_complexities.append(mc)

            avg_mc = sum(method_complexities) / max(len(method_complexities), 1)
            max_mc = max(method_complexities) if method_complexities else 0

            class_metrics.append(
                ClassMetrics(
                    name=cls.name,
                    start_line=cls.start_line,
                    end_line=cls.end_line,
                    lines_of_code=cls.end_line - cls.start_line + 1,
                    method_count=len(cls.methods),
                    avg_method_complexity=round(avg_mc, 1),
                    max_method_complexity=max_mc,
                    base_class_count=len(cls.base_classes),
                )
            )

        # File-level aggregation
        avg_cc = sum(all_complexities) / max(len(all_complexities), 1)
        max_cc = max(all_complexities) if all_complexities else 0
        comment_ratio = line_info["comment"] / max(line_info["code"], 1)
        file_mi = MetricsService.calculate_maintainability_index(
            line_info["code"], round(avg_cc), comment_ratio
        )
        total_debt = sum(
            MetricsService.estimate_tech_debt(f.cyclomatic_complexity, f.lines_of_code)
            for f in func_metrics
        )

        return FileMetrics(
            filepath=str(filepath),
            language=lang,
            total_lines=line_info["total"],
            code_lines=line_info["code"],
            blank_lines=line_info["blank"],
            comment_lines=line_info["comment"],
            import_count=len(parsed.imports),
            function_count=len(func_metrics),
            class_count=len(class_metrics),
            avg_complexity=round(avg_cc, 1),
            max_complexity=max_cc,
            maintainability_index=file_mi,
            tech_debt_minutes=total_debt,
            functions=func_metrics,
            classes=class_metrics,
        )

    # ── Repository-Level Analysis ────────────────────────────────────────────

    @staticmethod
    def analyze_repository(repo_path: Path) -> RepositoryMetrics:
        """
        Analyze all supported source files in a repository directory.

        Walks the directory tree, skipping common non-source directories,
        and aggregates metrics across all files.
        """
        SKIP_DIRS = {
            ".git", "node_modules", "__pycache__", ".next", ".venv",
            "venv", "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
            "target",  # Rust
            "vendor",  # Go
        }

        file_metrics: list[FileMetrics] = []
        language_lines: dict[str, int] = {}
        risk_dist: dict[str, int] = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
        high_risk_funcs: list[FunctionMetrics] = []

        for path in repo_path.rglob("*"):
            # Skip directories
            if path.is_dir():
                continue

            # Skip excluded directories
            parts = path.relative_to(repo_path).parts
            if any(part in SKIP_DIRS for part in parts):
                continue

            # Only analyze supported file types
            lang = ASTService.get_language_from_extension(path)
            if lang is None:
                continue
            try:
                fm = MetricsService.analyze_file(path)
                if fm:
                    file_metrics.append(fm)

                    # Aggregate language lines
                    language_lines[fm.language] = language_lines.get(fm.language, 0) + fm.code_lines

                    # Aggregate risk distribution
                    for func in fm.functions:
                        risk_dist[func.risk_level] = risk_dist.get(func.risk_level, 0) + 1
                        if func.risk_level in ("high", "critical"):
                            high_risk_funcs.append(func)

            except Exception as e:
                logger.warning("file_analysis_error", filepath=str(path), error=str(e))

        # Sort high-risk functions by complexity (descending)
        high_risk_funcs.sort(key=lambda f: f.cyclomatic_complexity, reverse=True)

        # Repository aggregation
        total_files = len(file_metrics)
        total_lines = sum(f.total_lines for f in file_metrics)
        total_code = sum(f.code_lines for f in file_metrics)
        total_blank = sum(f.blank_lines for f in file_metrics)
        total_comment = sum(f.comment_lines for f in file_metrics)
        total_funcs = sum(f.function_count for f in file_metrics)
        total_classes = sum(f.class_count for f in file_metrics)
        total_debt = sum(f.tech_debt_minutes for f in file_metrics)

        all_complexities = [
            f.avg_complexity for f in file_metrics if f.avg_complexity > 0
        ]
        avg_cc = sum(all_complexities) / max(len(all_complexities), 1)
        max_cc = max((f.max_complexity for f in file_metrics), default=0)

        all_mi = [f.maintainability_index for f in file_metrics]
        avg_mi = sum(all_mi) / max(len(all_mi), 1)

        return RepositoryMetrics(
            total_files=total_files,
            total_lines=total_lines,
            total_code_lines=total_code,
            total_blank_lines=total_blank,
            total_comment_lines=total_comment,
            total_functions=total_funcs,
            total_classes=total_classes,
            avg_complexity=round(avg_cc, 1),
            max_complexity=max_cc,
            avg_maintainability=round(avg_mi, 1),
            total_tech_debt_minutes=total_debt,
            language_breakdown=language_lines,
            risk_distribution=risk_dist,
            high_risk_functions=high_risk_funcs[:20],  # Top 20 riskiest
            file_metrics=file_metrics,
        )
