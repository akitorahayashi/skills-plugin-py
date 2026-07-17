#!/usr/bin/env python3
"""
Summarize numeric records described by a JSON config, printing one JSON document.

This is the example skill CLI for the skills-plugin-py template. It demonstrates
the conventions every script in this template follows: standard library only,
one JSON document on stdout, argparse arguments, explicit validation with an
actionable error, and meaningful exit codes.

Exit codes:
- 0: the summary covers at least one record
- 1: the config is valid but no record matched
- 2: config or runtime error; stderr carries JSON with an "action"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIG_KEYS = frozenset({"records", "category", "label"})
RECORD_KEYS = frozenset({"category", "value"})


class ConfigError(Exception):
    """A configuration or runtime error carrying an action for the user to fix."""

    def __init__(self, message: str, action: str) -> None:
        super().__init__(message)
        self.action = action


def load_config(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}", "Pass an existing JSON config path with --config.")
    except json.JSONDecodeError as error:
        raise ConfigError(f"Config file is not valid JSON: {error}", "Fix the JSON syntax in the config file.")
    except OSError as error:
        raise ConfigError(f"Config file cannot be read: {path}: {error}", "Check the path and file permissions.")

    if not isinstance(data, dict):
        raise ConfigError("Config must be a JSON object.", "Wrap the config in an object with a 'records' array.")

    unknown = sorted(set(data) - CONFIG_KEYS)
    if unknown:
        raise ConfigError(
            f"Unsupported config keys: {', '.join(unknown)}",
            f"Use only these keys: {', '.join(sorted(CONFIG_KEYS))}.",
        )

    if "records" not in data:
        raise ConfigError("Config is missing 'records'.", "Add a 'records' array of {category, value} objects.")
    records = data["records"]
    if not isinstance(records, list):
        raise ConfigError("'records' must be an array.", "Provide 'records' as a JSON array.")

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ConfigError(
                f"records[{index}] must be an object.", "Each record is an object with category and value."
            )
        unknown_record = sorted(set(record) - RECORD_KEYS)
        if unknown_record:
            raise ConfigError(
                f"records[{index}] has unsupported keys: {', '.join(unknown_record)}",
                f"Each record uses only: {', '.join(sorted(RECORD_KEYS))}.",
            )
        if not isinstance(record.get("category"), str):
            raise ConfigError(
                f"records[{index}].category must be a string.", "Set each record's 'category' to a string."
            )
        value = record.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ConfigError(f"records[{index}].value must be a number.", "Set each record's 'value' to a number.")

    if "category" in data and not isinstance(data["category"], str):
        raise ConfigError("'category' must be a string.", "Set the top-level 'category' filter to a string.")
    if "label" in data and not isinstance(data["label"], str):
        raise ConfigError("'label' must be a string.", "Set 'label' to a string.")

    return data


def summarize(records: List[Dict[str, Any]], category_filter: Optional[str]) -> Dict[str, Any]:
    selected = [r for r in records if category_filter is None or r["category"] == category_filter]
    by_category: Dict[str, Dict[str, Any]] = {}
    for record in selected:
        bucket = by_category.setdefault(str(record["category"]), {"count": 0, "total": 0})
        bucket["count"] += 1
        bucket["total"] += record["value"]
    return {
        "count": len(selected),
        "total": sum(record["value"] for record in selected),
        "by_category": dict(sorted(by_category.items())),
    }


def run(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config).expanduser())
    category_filter = config.get("category")
    summary = summarize(config["records"], category_filter)
    result: Dict[str, Any] = {
        "label": config.get("label", "unnamed summary"),
        "category_filter": category_filter,
        **summary,
    }
    if summary["count"] == 0:
        result["hint"] = "No records matched. Check the 'category' filter or that 'records' is non-empty."
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if summary["count"] > 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize numeric records from a JSON config.")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the JSON config describing the records to summarize.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except ConfigError as error:
        payload = {"error": str(error), "action": error.action}
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
