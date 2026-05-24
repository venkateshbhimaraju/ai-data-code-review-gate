# ai-data-code-review-gate (dqgate)

Local-first CLI that reviews SQL files before commit. V1 uses rule-based static checks only—no database connection, no cloud deployment, and no AI API calls.

## Quick start

From the repository root:

```bash
python3 -m dqgate.cli review examples/sample_query.sql
```

Exit code `0` when there are no errors; `1` when any error-level finding is present.

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
