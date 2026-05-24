"""Rule-based static checks for SQL text (no database connection)."""

from __future__ import annotations

import re
from collections.abc import Callable

from dqgate.models import Finding, Severity

RuleFn = Callable[[str], list[Finding]]


def _line_number(sql: str, position: int) -> int:
    return sql[:position].count("\n") + 1


def _strip_comments(sql: str) -> str:
    """Remove line and block comments so rules match executable SQL."""
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql


def check_select_star(sql: str) -> list[Finding]:
    findings: list[Finding] = []
    patterns = [
        (re.compile(r"\bSELECT\s+(?:DISTINCT\s+)?\*", re.IGNORECASE), "SELECT *"),
        (re.compile(r",\s*\*(?=\s*(?:,|FROM\b))", re.IGNORECASE), "column list includes *"),
    ]
    for pattern, detail in patterns:
        for match in pattern.finditer(sql):
            findings.append(
                Finding(
                    rule_id="select_star",
                    severity=Severity.WARNING,
                    message=f"Avoid {detail}; prefer explicit column lists.",
                    line=_line_number(sql, match.start()),
                )
            )
    return findings


def _keyword_line(sql: str, segment: str, segment_offset: int, keyword: str) -> int:
    match = re.search(rf"\b{keyword}\b", segment, re.IGNORECASE)
    if match is None:
        return _line_number(sql, segment_offset)
    return _line_number(sql, segment_offset + match.start())


def check_delete_without_where(sql: str) -> list[Finding]:
    findings: list[Finding] = []
    offset = 0
    for part in sql.split(";"):
        stmt = _strip_comments(part).strip()
        if not stmt:
            offset += len(part) + 1
            continue
        if not re.search(r"\bDELETE\b", stmt, re.IGNORECASE):
            offset += len(part) + 1
            continue
        if re.search(r"\bWHERE\b", stmt, re.IGNORECASE):
            offset += len(part) + 1
            continue
        findings.append(
            Finding(
                rule_id="delete_without_where",
                severity=Severity.ERROR,
                message="DELETE without WHERE can remove all rows.",
                line=_keyword_line(sql, part, offset, "DELETE"),
            )
        )
        offset += len(part) + 1
    return findings


def check_update_without_where(sql: str) -> list[Finding]:
    findings: list[Finding] = []
    offset = 0
    for part in sql.split(";"):
        stmt = _strip_comments(part).strip()
        if not stmt:
            offset += len(part) + 1
            continue
        if not re.search(r"\bUPDATE\b", stmt, re.IGNORECASE):
            offset += len(part) + 1
            continue
        if re.search(r"\bWHERE\b", stmt, re.IGNORECASE):
            offset += len(part) + 1
            continue
        findings.append(
            Finding(
                rule_id="update_without_where",
                severity=Severity.ERROR,
                message="UPDATE without WHERE can modify all rows.",
                line=_keyword_line(sql, part, offset, "UPDATE"),
            )
        )
        offset += len(part) + 1
    return findings


def check_window_function(sql: str) -> list[Finding]:
    findings: list[Finding] = []
    pattern = re.compile(r"\bOVER\s*\(", re.IGNORECASE)
    for match in pattern.finditer(sql):
        findings.append(
            Finding(
                rule_id="window_function",
                severity=Severity.INFO,
                message="Window function detected; verify PARTITION BY and ORDER BY.",
                line=_line_number(sql, match.start()),
            )
        )
    return findings


def check_truncate(sql: str) -> list[Finding]:
    findings: list[Finding] = []
    pattern = re.compile(r"\bTRUNCATE\s+(?:TABLE\s+)?\w+", re.IGNORECASE)
    for match in pattern.finditer(sql):
        findings.append(
            Finding(
                rule_id="truncate_table",
                severity=Severity.WARNING,
                message="TRUNCATE removes all rows; confirm this is intentional.",
                line=_line_number(sql, match.start()),
            )
        )
    return findings


DEFAULT_RULES: list[RuleFn] = [
    check_select_star,
    check_delete_without_where,
    check_update_without_where,
    check_window_function,
    check_truncate,
]


def run_rules(sql: str, rules: list[RuleFn] | None = None) -> list[Finding]:
    """Run all registered rules and return combined findings."""
    rule_set = DEFAULT_RULES if rules is None else rules
    findings: list[Finding] = []
    for rule in rule_set:
        findings.extend(rule(sql))
    return findings
