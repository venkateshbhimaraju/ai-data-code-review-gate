"""Tests for rule-based SQL checks."""

from dqgate.rules import (
    check_delete_without_where,
    check_select_star,
    check_update_without_where,
    check_window_function,
    run_rules,
)


def test_select_star_detected():
    sql = "SELECT * FROM t;"
    findings = check_select_star(sql)
    assert len(findings) == 1
    assert findings[0].rule_id == "select_star"


def test_delete_without_where_is_error():
    sql = "DELETE FROM staging_events;"
    findings = check_delete_without_where(sql)
    assert len(findings) == 1
    assert findings[0].rule_id == "delete_without_where"


def test_delete_with_where_passes():
    sql = "DELETE FROM staging_events WHERE id = 1;"
    assert check_delete_without_where(sql) == []


def test_update_without_where_is_error():
    sql = "UPDATE users SET active = false;"
    findings = check_update_without_where(sql)
    assert len(findings) == 1
    assert findings[0].rule_id == "update_without_where"


def test_window_function_info():
    sql = "SELECT ROW_NUMBER() OVER (ORDER BY x) AS rn FROM t;"
    findings = check_window_function(sql)
    assert len(findings) == 1
    assert findings[0].rule_id == "window_function"


def test_sample_query_has_expected_findings():
    sql = """
SELECT * FROM raw_events;
DELETE FROM staging_events;
SELECT ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS rn FROM users;
"""
    findings = run_rules(sql)
    rule_ids = {f.rule_id for f in findings}
    assert "select_star" in rule_ids
    assert "delete_without_where" in rule_ids
    assert "window_function" in rule_ids
