from __future__ import annotations

import json

import pytest


def test_missing_file_exits_two_with_action(run_summarize, tmp_path):
    result = run_summarize(config_path=tmp_path / "missing.json")
    assert result.returncode == 2
    payload = json.loads(result.stderr)
    assert "error" in payload
    assert payload["action"]


def test_invalid_json_exits_two_with_action(run_summarize):
    result = run_summarize("{ not valid json")
    assert result.returncode == 2
    payload = json.loads(result.stderr)
    assert payload["action"]


INVALID_CONFIGS = [
    pytest.param({"records": [], "surprise": 1}, id="unknown_key"),
    pytest.param({"records": {}}, id="records_not_array"),
    pytest.param({}, id="records_missing"),
    pytest.param({"records": [{"category": "a"}]}, id="record_missing_value"),
    pytest.param({"records": [{"category": "a", "value": "x"}]}, id="value_not_number"),
    pytest.param({"records": [{"category": "a", "value": True}]}, id="value_is_bool"),
    pytest.param({"records": [{"category": 1, "value": 2}]}, id="category_not_string"),
    pytest.param({"records": [{"category": "a", "value": 2, "extra": 1}]}, id="record_unknown_key"),
    pytest.param({"records": [], "category": 5}, id="category_filter_not_string"),
    pytest.param([], id="not_an_object"),
]


@pytest.mark.parametrize("config", INVALID_CONFIGS)
def test_invalid_config_exits_two_with_action(run_summarize, config):
    result = run_summarize(config)
    assert result.returncode == 2
    payload = json.loads(result.stderr)
    assert "error" in payload
    assert payload["action"]
