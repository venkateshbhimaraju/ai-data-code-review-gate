# ai-data-code-review-gate (dqgate)

Local-first CLI that reviews SQL files before commit. V1 uses rule-based static checks only—no database connection, no cloud deployment, and no AI API calls.

The installable Python package is named **dqgate** (data quality gate). The repository name describes the broader project goal; the CLI and imports use `dqgate`.

## Quick start

From the repository root:

```bash
python3 -m dqgate.cli review examples/sample_query.sql
```

Exit code `0` when there are no errors; `1` when any error-level finding is present.

Try `examples/sample_query.sql` first—it intentionally includes issues so you can see a non-empty report.

## Architecture

Request flow is linear and small on purpose:

```
dqgate/cli.py          → parse args, exit codes
    ↓
dqgate/reviewer.py     → read file, orchestrate review
    ↓
dqgate/rules.py        → run each check, return findings
    ↓
dqgate/models.py       → Finding, ReviewReport, Severity
    ↓
dqgate/report.py       → format and print terminal output
```

- **`cli.py`** — User-facing entry (`python3 -m dqgate.cli review <file>`).
- **`reviewer.py`** — `RuleBasedReviewer` loads SQL and calls `run_rules()`. Future LLM reviewers can plug in here without changing the CLI.
- **`rules.py`** — One function per rule; each returns a list of `Finding`.
- **`models.py`** — Shared types; `ReviewReport.passed` is true when there are no errors.
- **`report.py`** — Turns a `ReviewReport` into human-readable terminal output.

V1 does **not** parse SQL into an AST. Rules use regex and simple heuristics (see `dqgate/rules.py` module docstring). That keeps dependencies at zero but means edge cases (semicolons in strings, nested statements) are not handled perfectly.

## Adding a rule

1. Add a function in `dqgate/rules.py`:

   ```python
   def check_my_rule(sql: str) -> list[Finding]:
       """One-line description of what this rule catches."""
       ...
   ```

2. Register it in `DEFAULT_RULES` (order affects stable output when sorting is equal).

3. Add a test in `tests/test_rules.py` with a minimal SQL string that should trigger the rule.

4. Document the rule ID and severity in the table below.

Each rule function takes the full SQL text and returns zero or more `Finding` objects (`rule_id`, `severity`, `message`, optional `line`).

## V1 rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `select_star` | warning | `SELECT *` or `, *` in column list |
| `delete_without_where` | error | `DELETE` with no `WHERE` |
| `update_without_where` | error | `UPDATE` with no `WHERE` |
| `window_function` | info | `OVER (...)` window functions |
| `truncate_table` | warning | `TRUNCATE` statements |

## Development

```bash
python3 -m pytest
```

## Future

`RuleBasedReviewer` is the V1 engine. The layout leaves room for an LLM-backed reviewer without changing the CLI surface.
