"""Terminal formatting for structured review reports."""

from __future__ import annotations

import sys
from typing import TextIO

from dqgate.models import Finding, ReviewReport, Severity


def _severity_label(severity: Severity) -> str:
    """Format a severity enum value for display (e.g. ``ERROR``)."""
    return severity.value.upper()


def format_finding(finding: Finding) -> str:
    """Format a single finding as an indented terminal line."""
    location = f" (line {finding.line})" if finding.line is not None else ""
    return (
        f"  [{_severity_label(finding.severity)}] "
        f"{finding.rule_id}{location}: {finding.message}"
    )


def format_report(report: ReviewReport) -> str:
    """Build the full structured review report as a multi-line string."""
    lines = [
        "SQL Review Report",
        "=" * 40,
        f"File: {report.file_path}",
        "",
    ]

    if not report.findings:
        lines.append("Findings: none")
        lines.append("")
        lines.append("Summary: PASSED (no issues)")
        return "\n".join(lines)

    lines.append(f"Findings ({len(report.findings)}):")
    for finding in sorted(
        report.findings,
        key=lambda f: (
            {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}[f.severity],
            f.line or 0,
            f.rule_id,
        ),
    ):
        lines.append(format_finding(finding))

    lines.append("")
    status = "PASSED" if report.passed else "FAILED"
    lines.append(
        "Summary: "
        f"{status} "
        f"({len(report.errors)} error(s), "
        f"{len(report.warnings)} warning(s), "
        f"{len(report.infos)} info)"
    )
    return "\n".join(lines)


def print_report(report: ReviewReport, stream: TextIO | None = None) -> None:
    """Print a formatted review report to ``stream`` (stdout by default)."""
    out = sys.stdout if stream is None else stream
    print(format_report(report), file=out)
