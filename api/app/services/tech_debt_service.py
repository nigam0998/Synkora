"""
Synkora API — Technical Debt Service

A rules engine that synthesizes data from Code Metrics, Dependency Graphs,
and Git History to identify and quantify technical debt and code smells.
"""

import uuid
from typing import List, Optional

from app.schemas.metrics import RepositoryMetrics, FileMetrics, ClassMetrics, FunctionMetrics
from app.schemas.dependency import DependencyGraph
from app.schemas.git_history import GitHistoryReport
from app.schemas.tech_debt import TechDebtIssue, TechDebtReport
from app.core.logging import get_logger

logger = get_logger("tech_debt_service")


class TechDebtService:
    """Service for detecting and quantifying technical debt."""

    @staticmethod
    def analyze_repository(
        metrics: RepositoryMetrics,
        dependencies: Optional[DependencyGraph] = None,
        history: Optional[GitHistoryReport] = None,
    ) -> TechDebtReport:
        """
        Run the tech debt rules engine across all available repository data.
        """
        issues: List[TechDebtIssue] = []

        # 1. AST/Metrics Rules
        for file_metric in metrics.file_metrics:
            # Rule: God Class
            for cls in file_metric.classes:
                if issue := TechDebtService._check_god_class(cls, file_metric.filepath):
                    issues.append(issue)

            # Rule: Complex Method (Spaghetti Code)
            for func in file_metric.functions:
                if issue := TechDebtService._check_complex_method(func, file_metric.filepath):
                    issues.append(issue)

        # 2. Dependency Rules
        if dependencies:
            # Rule: Circular Dependencies
            for circ_dep in dependencies.circular_dependencies:
                if issue := TechDebtService._check_circular_dependency(circ_dep.cycle):
                    issues.append(issue)

            # Rule: High Coupling (Hotspots)
            for node in dependencies.nodes:
                if issue := TechDebtService._check_high_coupling(node):
                    issues.append(issue)

        # 3. Git History Rules
        if history:
            # Rule: Volatile Code (High Churn)
            for churn in history.file_churn:
                if issue := TechDebtService._check_volatile_code(churn):
                    issues.append(issue)

        # Aggregate Report
        report = TechDebtReport(issues=issues)
        report.total_issues = len(issues)
        
        for issue in issues:
            report.total_remediation_minutes += issue.estimated_remediation_minutes
            if issue.severity == "critical":
                report.critical_issues += 1
            elif issue.severity == "high":
                report.high_issues += 1
            elif issue.severity == "moderate":
                report.moderate_issues += 1
            elif issue.severity == "low":
                report.low_issues += 1

        logger.info(
            "tech_debt_analyzed",
            total_issues=report.total_issues,
            debt_grade=report.debt_grade,
            remediation_hours=report.total_remediation_hours
        )
        return report

    # ─── Rule Implementations ─────────────────────────────────────────

    @staticmethod
    def _check_god_class(cls: ClassMetrics, filepath: str) -> Optional[TechDebtIssue]:
        """Flags classes that are too large or have too many methods."""
        # Thresholds
        MAX_LOC = 300
        MAX_METHODS = 20

        if cls.lines_of_code > MAX_LOC or cls.method_count > MAX_METHODS:
            severity = "critical" if cls.lines_of_code > 500 else "high"
            return TechDebtIssue(
                issue_id=f"smell_god_class_{uuid.uuid4().hex[:8]}",
                rule_name="God Class",
                description=f"Class '{cls.name}' is too large, violating the Single Responsibility Principle.",
                severity=severity,
                file_path=filepath,
                start_line=cls.start_line,
                end_line=cls.end_line,
                estimated_remediation_minutes=120 if severity == "critical" else 60,
                related_metrics={"loc": cls.lines_of_code, "methods": cls.method_count}
            )
        return None

    @staticmethod
    def _check_complex_method(func: FunctionMetrics, filepath: str) -> Optional[TechDebtIssue]:
        """Flags functions with excessive complexity."""
        # Thresholds
        MAX_CC = 15

        if func.cyclomatic_complexity > MAX_CC:
            severity = "critical" if func.cyclomatic_complexity > 25 else "high"
            return TechDebtIssue(
                issue_id=f"smell_complex_method_{uuid.uuid4().hex[:8]}",
                rule_name="Complex Method",
                description=f"Function '{func.name}' has high cyclomatic complexity, making it hard to test and maintain.",
                severity=severity,
                file_path=filepath,
                start_line=func.start_line,
                end_line=func.end_line,
                estimated_remediation_minutes=60 if severity == "critical" else 30,
                related_metrics={"cyclomatic_complexity": func.cyclomatic_complexity}
            )
        return None

    @staticmethod
    def _check_circular_dependency(cycle: list[str]) -> Optional[TechDebtIssue]:
        """Flags architectural cycles."""
        # A cycle is a list of node IDs (filepaths)
        if not cycle:
            return None
            
        file_path = cycle[0]  # Just anchor it to the first file in the cycle
        path_str = " -> ".join(cycle) + f" -> {cycle[0]}"
        
        return TechDebtIssue(
            issue_id=f"smell_cycle_{uuid.uuid4().hex[:8]}",
            rule_name="Circular Dependency",
            description=f"Architectural cycle detected: {path_str}",
            severity="critical",
            file_path=file_path,
            estimated_remediation_minutes=120,
            related_metrics={"cycle_length": len(cycle), "path": path_str}
        )

    @staticmethod
    def _check_high_coupling(node) -> Optional[TechDebtIssue]:
        """Flags files that depend on too many other files (high fan-out)."""
        from app.schemas.dependency import DependencyNode
        
        MAX_OUT_DEGREE = 15
        
        if isinstance(node, DependencyNode) and node.out_degree > MAX_OUT_DEGREE:
            return TechDebtIssue(
                issue_id=f"smell_coupling_{uuid.uuid4().hex[:8]}",
                rule_name="High Coupling",
                description=f"File imports {node.out_degree} other modules, indicating it might be a God Object or lack cohesion.",
                severity="high" if node.out_degree > 25 else "moderate",
                file_path=node.id,
                estimated_remediation_minutes=45,
                related_metrics={"out_degree": node.out_degree, "in_degree": node.in_degree}
            )
        return None

    @staticmethod
    def _check_volatile_code(churn) -> Optional[TechDebtIssue]:
        """Flags files that change frequently across many authors."""
        from app.schemas.git_history import FileChurn
        
        if isinstance(churn, FileChurn) and churn.risk_level == "high":
            return TechDebtIssue(
                issue_id=f"smell_churn_{uuid.uuid4().hex[:8]}",
                rule_name="Volatile Code",
                description=f"File is frequently modified ({churn.change_count} times by {churn.distinct_authors} authors), indicating a potential hotspot for bugs.",
                severity="high",
                file_path=churn.filepath,
                estimated_remediation_minutes=60,
                related_metrics={"churn_score": round(churn.churn_score, 1), "changes": churn.change_count}
            )
        return None
