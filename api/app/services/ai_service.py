"""
Synkora API — AI Service

Integrates with OpenAI-compatible APIs (OpenRouter / DeepSeek) to provide intelligent code analysis.
Capabilities:
  - Enrich tech debt insights with actionable refactoring advice
  - Generate natural-language summaries of repository health
  - Produce context-aware fix suggestions for detected code smells
"""

from typing import Optional

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.tech_debt import TechDebtIssue, TechDebtReport

logger = get_logger("ai_service")


# ── Prompt Templates ──────────────────────────────────────────────────────

REFACTORING_SYSTEM_PROMPT = """\
You are Synkora AI, an expert software architect specializing in code quality \
and refactoring. You analyze technical debt issues detected by static analysis \
tools and provide clear, actionable remediation guidance.

Your responses must be:
- Concise and practical (no filler)
- Written for a senior developer audience
- Include concrete code patterns or pseudocode when helpful
- Prioritize the highest-impact fix first
"""

INSIGHT_PROMPT_TEMPLATE = """\
## Detected Issue

**Rule:** {rule_name}
**Severity:** {severity}
**File:** `{file_path}`
**Lines:** {start_line}–{end_line}
**Description:** {description}

### Related Metrics
{metrics_block}

---

Provide a structured response with:
1. **Root Cause** — Why this issue exists (1–2 sentences)
2. **Recommended Fix** — The concrete refactoring steps (numbered list)
3. **Code Pattern** — A brief pseudocode or design pattern to apply
4. **Estimated Effort** — Quick / Medium / Large
"""

REPO_SUMMARY_SYSTEM_PROMPT = """\
You are Synkora AI. Given the analysis metrics for a software repository, \
write a concise executive summary (3–5 sentences) of the repository's overall \
health. Highlight the most critical risks and the strongest positives. \
Use plain English suitable for a technical project manager.
"""

REPO_SUMMARY_PROMPT_TEMPLATE = """\
## Repository Analysis Summary

- **Total Files:** {total_files}
- **Total Lines of Code:** {total_lines}
- **Total Functions:** {total_functions}
- **Total Classes:** {total_classes}
- **Average Complexity:** {avg_complexity}
- **Tech Debt Score:** {tech_debt_hours} hours
- **Tech Debt Grade:** {debt_grade}
- **Total Issues:** {total_issues}
  - Critical: {critical}
  - High: {high}
  - Moderate: {moderate}
  - Low: {low}

Write the executive health summary now.
"""


class AIService:
    """Service for AI-powered code analysis via OpenAI-compatible endpoints."""

    _client: Optional[AsyncOpenAI] = None

    @classmethod
    def _get_client(cls) -> AsyncOpenAI:
        """Lazily initialise and return the OpenAI client singleton."""
        if cls._client is None:
            api_key = settings.AI_API_KEY
            if not api_key:
                raise RuntimeError(
                    "AI_API_KEY is not configured. "
                    "Set it in your .env file to enable AI features."
                )
            cls._client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.AI_BASE_URL,
            )
            logger.info("openai_client_initialized", model=settings.AI_MODEL, base_url=settings.AI_BASE_URL)
        return cls._client

    # ── Public API ────────────────────────────────────────────────────────

    @classmethod
    async def enrich_insight(cls, issue: TechDebtIssue) -> str:
        """
        Send a single TechDebtIssue to the LLM and return an AI-generated
        refactoring recommendation.
        """
        client = cls._get_client()

        # Build the metrics block
        metrics_lines = [
            f"- **{key}:** {value}" for key, value in issue.related_metrics.items()
        ]
        metrics_block = "\n".join(metrics_lines) if metrics_lines else "_No extra metrics._"

        user_prompt = INSIGHT_PROMPT_TEMPLATE.format(
            rule_name=issue.rule_name,
            severity=issue.severity,
            file_path=issue.file_path,
            start_line=issue.start_line or "?",
            end_line=issue.end_line or "?",
            description=issue.description,
            metrics_block=metrics_block,
        )

        try:
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": REFACTORING_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            advice = response.choices[0].message.content or ""
            logger.info(
                "insight_enriched",
                rule=issue.rule_name,
                file=issue.file_path,
                response_len=len(advice),
            )
            return advice.strip()

        except Exception as exc:
            logger.error("insight_enrichment_failed", error=str(exc), rule=issue.rule_name)
            return f"AI analysis unavailable: {exc}"

    @classmethod
    async def generate_repo_summary(
        cls,
        total_files: int,
        total_lines: int,
        total_functions: int,
        total_classes: int,
        avg_complexity: float,
        tech_debt_report: TechDebtReport,
    ) -> str:
        """
        Generate a natural-language executive summary of repository health.
        """
        client = cls._get_client()

        user_prompt = REPO_SUMMARY_PROMPT_TEMPLATE.format(
            total_files=total_files,
            total_lines=total_lines,
            total_functions=total_functions,
            total_classes=total_classes,
            avg_complexity=round(avg_complexity, 2),
            tech_debt_hours=tech_debt_report.total_remediation_hours,
            debt_grade=tech_debt_report.debt_grade,
            total_issues=tech_debt_report.total_issues,
            critical=tech_debt_report.critical_issues,
            high=tech_debt_report.high_issues,
            moderate=tech_debt_report.moderate_issues,
            low=tech_debt_report.low_issues,
        )

        try:
            response = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": REPO_SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=512,
            )
            summary = response.choices[0].message.content or ""
            logger.info("repo_summary_generated", length=len(summary))
            return summary.strip()

        except Exception as exc:
            logger.error("repo_summary_failed", error=str(exc))
            return f"AI summary unavailable: {exc}"

    @classmethod
    async def enrich_all_insights(cls, report: TechDebtReport) -> dict[str, str]:
        """
        Enrich every issue in a TechDebtReport.
        Returns a mapping of issue_id → AI recommendation string.

        Only enriches high and critical issues to conserve API quota.
        """
        results: dict[str, str] = {}
        enrichable = [
            issue for issue in report.issues
            if issue.severity in ("critical", "high")
        ]

        logger.info(
            "enriching_insights",
            total=len(report.issues),
            enrichable=len(enrichable),
        )

        for issue in enrichable:
            advice = await cls.enrich_insight(issue)
            results[issue.issue_id] = advice

        return results
