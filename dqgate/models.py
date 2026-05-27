"""Data models for SQL review findings and reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """Finding severity levels used in review output and exit-code logic."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Finding:
    """A single rule violation or informational note from a SQL review."""

    rule_id: str
    severity: Severity
    message: str
    line: int | None = None


@dataclass
class ReviewReport:
    """Aggregated results of reviewing one SQL file or SQL string."""

    file_path: str
    sql: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        """Findings with ``Severity.ERROR``."""
        return [f for f in self.findings if f.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Finding]:
        """Findings with ``Severity.WARNING``."""
        return [f for f in self.findings if f.severity == Severity.WARNING]

    @property
    def infos(self) -> list[Finding]:
        """Findings with ``Severity.INFO``."""
        return [f for f in self.findings if f.severity == Severity.INFO]

    @property
    def passed(self) -> bool:
        """True when the review has no error-level findings."""
        return len(self.errors) == 0
