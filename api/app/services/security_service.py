"""
Synkora API — Security Service

Runs automated security scanners (e.g., Bandit for Python) on cloned repositories
to detect vulnerabilities and hardcoded secrets.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger("security_service")


@dataclass
class SecurityIssue:
    issue_id: str
    rule_name: str
    description: str
    severity: str
    file_path: str
    start_line: int
    end_line: int


class SecurityService:
    """Service to run security scanners on cloned repositories."""

    @staticmethod
    async def scan_repository(repo_path: Path) -> List[SecurityIssue]:
        """
        Run applicable security scanners on the given repository path.
        Currently supports Python (Bandit).
        """
        issues: List[SecurityIssue] = []
        
        # Check if there are any Python files in the repo
        python_files = list(repo_path.rglob("*.py"))
        if python_files:
            logger.info("running_bandit_scan", repo_path=str(repo_path))
            bandit_issues = await SecurityService._run_bandit(repo_path)
            issues.extend(bandit_issues)
            
        return issues

    @staticmethod
    async def _run_bandit(repo_path: Path) -> List[SecurityIssue]:
        """
        Run Bandit AST-based security scanner on Python files.
        """
        issues: List[SecurityIssue] = []
        
        # Create a temporary file to store bandit JSON output
        temp_output_file = repo_path / ".bandit_output.json"
        
        try:
            # We run bandit using python -m bandit to ensure it runs from the current environment
            cmd = [
                "python", "-m", "bandit",
                "-r", str(repo_path),
                "-f", "json",
                "-o", str(temp_output_file),
                "-q"  # quiet
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Bandit returns exit code 1 if issues are found, which is expected.
            await process.communicate()
            
            if temp_output_file.exists():
                with open(temp_output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                for result in data.get("results", []):
                    # Severity mapping
                    sev_raw = result.get("issue_severity", "LOW").lower()
                    severity = "critical" if sev_raw == "high" else ("high" if sev_raw == "medium" else "moderate")
                    
                    # File path relative to repo_path
                    abs_path = result.get("filename", "")
                    try:
                        rel_path = str(Path(abs_path).relative_to(repo_path))
                    except ValueError:
                        rel_path = abs_path
                        
                    issue = SecurityIssue(
                        issue_id=f"bandit_{result.get('test_id', 'unknown')}_{hash(rel_path + str(result.get('line_number', 0)))}",
                        rule_name=f"Bandit: {result.get('test_name', 'Security Issue')}",
                        description=result.get("issue_text", "Unknown security issue detected."),
                        severity=severity,
                        file_path=rel_path,
                        start_line=result.get("line_number", 0),
                        end_line=result.get("line_number", 0),
                    )
                    issues.append(issue)
                    
        except Exception as e:
            logger.error("bandit_scan_failed", error=str(e))
        finally:
            # Clean up temp file
            if temp_output_file.exists():
                try:
                    temp_output_file.unlink()
                except Exception:
                    pass
                    
        return issues
