---
name: example-skill
description: Use this skill when the user asks to summarize or tally numeric records grouped by category from a JSON file, for example totals and per-category counts. This is the template's example skill; replace it with your own.
---

# Example Skill

Summarize numeric records described by a JSON config and report the totals. This
is the example skill shipped with the template. Rename the directory, rewrite
this file, and replace the CLI with your own.

Files are referenced by path relative to this skill directory. Do not assume the
shell working directory is this directory.

- [scripts/summarize_records.py](scripts/summarize_records.py) — the CLI. Prints one JSON document.
- [references/records-spec.schema.json](references/records-spec.schema.json) — the strict config schema.
- [assets/records.example.json](assets/records.example.json) — an example config.

## Run

```bash
python3 <skill-dir>/scripts/summarize_records.py --config <path-to-config.json>
```

The config is a JSON object with a `records` array of `{category, value}`
objects, an optional `category` filter, and an optional `label`. See the schema
for the exact shape and the example asset for a working config.

## Read the result

The CLI prints one JSON document to stdout with `label`, `category_filter`,
`count`, `total`, and `by_category`. Exit codes:

- 0: the summary covers at least one record.
- 1: the config is valid but no record matched; the result carries a `hint`.
- 2: a config or runtime error. stderr carries JSON with an `error` and an
  actionable `action`. Relay the action to the user and stop.

## Report

Answer with the totals directly, then add per-category detail when useful. For an
empty result, relay the hint. For an error, relay the action.
