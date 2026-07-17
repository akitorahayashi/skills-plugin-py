"""Shared fixtures for the example skill CLI tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SUMMARIZE_CLI = ROOT / "plugin/example-plugin/skills/example-skill/scripts/summarize_records.py"


@pytest.fixture
def run_summarize(tmp_path):
    """Run the CLI as a subprocess. Pass a config object or string, or an explicit config_path."""

    def _run(config=None, *, config_path=None):
        if config_path is None:
            config_path = tmp_path / "config.json"
            payload = config if isinstance(config, str) else json.dumps(config, ensure_ascii=False)
            config_path.write_text(payload, encoding="utf-8")
        argv = [sys.executable, str(SUMMARIZE_CLI), "--config", str(config_path)]
        return subprocess.run(argv, capture_output=True, text=True, timeout=30)

    return _run
