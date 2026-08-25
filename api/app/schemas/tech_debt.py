"""
Synkora API — Technical Debt Schemas

Pydantic models representing detected technical debt issues, code smells,
and the aggregated tech debt report for a repository.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class TechDebtIssue(BaseModel):
    """A single technical debt issue or code smell."""
    
    issue_id: str = Field(description="Unique identifier for the issue")
    rule_name: str = Field(description="Name of the broken rule (e.g., 'God Class')")
    description: str = Field(description="Detailed explanation of the issue")
    severity: str = Field(description="Severity: 'low', 'moderate', 'high', 'critical'")
    
    # Location
    file_path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    
    # Impact
    estimated_remediation_minutes: int = Field(default=30)
    related_metrics: dict = Field(default_factory=dict, description="Metrics that triggered this rule")


class TechDebtReport(BaseModel):
    """Aggregated technical debt report for an entire repository."""
    
    total_issues: int = 0
    total_remediation_minutes: int = 0
    
    # Severity breakdowns
    critical_issues: int = 0
    high_issues: int = 0
    moderate_issues: int = 0
    low_issues: int = 0
    
    # The actual issues
    issues: List[TechDebtIssue] = Field(default_factory=list)
    
    @property
    def total_remediation_hours(self) -> float:
        return round(self.total_remediation_minutes / 60, 1)

    @property
    def debt_grade(self) -> str:
        """
        Calculate a letter grade (A-F) based on remediation time per issue.
        This is a rough heuristic.
        """
        if self.total_issues == 0:
            return "A"
            
        avg_minutes_per_issue = self.total_remediation_minutes / self.total_issues
        
        if avg_minutes_per_issue <= 15 and self.critical_issues == 0:
            return "A"
        elif avg_minutes_per_issue <= 30 and self.critical_issues <= 2:
            return "B"
        elif avg_minutes_per_issue <= 60:
            return "C"
        elif avg_minutes_per_issue <= 120:
            return "D"
        else:
            return "F"
