"""Command-line interface for dqgate SQL review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dqgate import __version__
from dqgate.report import print_report
from dqgate.reviewer import RuleBasedReviewer


def _build_parser() -> argparse.ArgumentParser:
    """Configure the top-level CLI parser and subcommands."""
    parser = argparse.ArgumentParser(
        prog="dqgate",
        description="Local-first SQL quality gate for data engineering.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    review_parser = subparsers.add_parser(
        "review",
        help="Run rule-based static review on a SQL file.",
    )
    review_parser.add_argument(
        "sql_file",
        type=Path,
        help="Path to the .sql file to review.",
    )
    return parser


def _cmd_review(sql_file: Path) -> int:
    """Run static review on ``sql_file`` and print the report; return an exit code."""
    if not sql_file.exists():
        print(f"error: file not found: {sql_file}", file=sys.stderr)
        return 2
    if sql_file.suffix.lower() != ".sql":
        print(f"warning: expected a .sql file, got: {sql_file}", file=sys.stderr)

    reviewer = RuleBasedReviewer()
    report = reviewer.review_file(sql_file)
    print_report(report)
    return 0 if report.passed else 1


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and dispatch to the requested subcommand."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "review":
        return _cmd_review(args.sql_file)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
