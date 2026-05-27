"""Review orchestration: read SQL files and run static checks."""

from __future__ import annotations

from pathlib import Path

from dqgate.models import ReviewReport
from dqgate.rules import run_rules


class RuleBasedReviewer:
    """V1 reviewer: rule-based static analysis only (no DB, no LLM)."""

    def review_file(self, path: Path) -> ReviewReport:
        """Read SQL from ``path`` and return a rule-based review report."""
        sql = path.read_text(encoding="utf-8")
        return self.review_sql(sql, file_path=str(path))

    def review_sql(self, sql: str, *, file_path: str = "<string>") -> ReviewReport:
        """Run rule-based checks on in-memory SQL and return a review report."""
        findings = run_rules(sql)
        return ReviewReport(file_path=file_path, sql=sql, findings=findings)


# Future: LLMReviewer can implement the same interface and plug in here.
