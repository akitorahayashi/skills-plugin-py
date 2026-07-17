from __future__ import annotations

import json


def test_summary_reports_totals_and_exits_zero(run_summarize):
    result = run_summarize(
        {
            "label": "sample",
            "records": [
                {"category": "a", "value": 10},
                {"category": "a", "value": 5},
                {"category": "b", "value": 2},
            ],
        }
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["label"] == "sample"
    assert payload["count"] == 3
    assert payload["total"] == 17
    assert payload["by_category"]["a"] == {"count": 2, "total": 15}
    assert payload["by_category"]["b"] == {"count": 1, "total": 2}


def test_category_filter_selects_matching_records(run_summarize):
    result = run_summarize(
        {
            "category": "a",
            "records": [
                {"category": "a", "value": 10},
                {"category": "b", "value": 2},
            ],
        }
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["category_filter"] == "a"
    assert payload["count"] == 1
    assert payload["total"] == 10


def test_filter_matching_nothing_exits_one_with_hint(run_summarize):
    result = run_summarize(
        {
            "category": "missing",
            "records": [{"category": "a", "value": 10}],
        }
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["count"] == 0
    assert payload["total"] == 0
    assert "hint" in payload


def test_empty_records_exits_one(run_summarize):
    result = run_summarize({"records": []})
    assert result.returncode == 1
    assert json.loads(result.stdout)["count"] == 0
