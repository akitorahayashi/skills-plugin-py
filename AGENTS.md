# AGENTS.md

Orientation for an agent working on this repository. For the development
workflow in full, see [CONTRIBUTING.md](CONTRIBUTING.md); for user-facing
behavior, see [README.md](README.md).

## What this is

A template for a multi-client Agent Skills plugin whose skills are backed by
Python scripts. One repository is one plugin, installable on Claude Code, Codex
CLI, and Antigravity CLI from a shared `skills/` directory. Each skill drives a
standalone standard-library Python CLI that prints one JSON document. The plugin
lives in the `plugin/example-plugin/` subtree; development assets live at the
repository root and never ship.

## Map

- `plugin/example-plugin/skills/<name>/SKILL.md` — how the agent-facing skill
  drives its CLI.
- `plugin/example-plugin/skills/<name>/scripts/` — the CLI. One per skill by
  default.
- `plugin/example-plugin/skills/<name>/references/` — strict specs such as JSON
  Schema (optional).
- `plugin/example-plugin/skills/<name>/assets/` — example configs and sample
  inputs (optional).
- `plugin/example-plugin/skills/example-skill/scripts/summarize.py` — the example
  CLI. Takes numbers as arguments and prints count/sum/min/max/mean. Exit 0 a
  result, exit 1 no numbers given, exit 2 a non-numeric argument (stderr JSON with
  an `action`).
- `plugin/example-plugin/.claude-plugin/plugin.json`,
  `plugin/example-plugin/.codex-plugin/plugin.json`,
  `plugin/example-plugin/plugin.json` — the per-client manifests.
- `.claude-plugin/marketplace.json` — the distribution catalog at the repository
  root; its `git-subdir` source points at `plugin/example-plugin`.
- `tests/` — pytest process-boundary tests, one directory per skill;
  `tests/conftest.py` holds fixtures and a subprocess CLI runner.

## Invariants to preserve

- Runtime is standard-library only, Python 3.10+. No third-party import enters
  `plugin/**/skills/**/scripts/`. `pyproject.toml` dependencies are development
  tools that never ship.
- Each CLI prints exactly one JSON document on stdout and uses exit codes 0
  (affirmative), 1 (negative), 2 (error). Errors are JSON on stderr carrying an
  actionable `action`.
- No silent fallbacks. Invalid input fails before work begins rather than
  degrading the result.
- Skills are auto-discovered from `skills/`. Manifests carry only per-client
  identity and never duplicate a skill body.

## Working here

- `make fix` applies formatting and autofixes first. Verify changes with
  `make lint` and `make test` (see CONTRIBUTING.md).
- Tests assert observable CLI behavior, not internal composition. Add coverage
  at the same process boundary.

## Distribution boundary

The distributed plugin is whatever `source` in
`.claude-plugin/marketplace.json` points to. It is a `git-subdir` source scoped
to `plugin/example-plugin`, which holds only the three manifests and `skills/`.
Claude Code and Codex both read this marketplace and sparse-clone that subtree,
so the development-only assets at the repository root — `tests/`, `Makefile`,
`pyproject.toml`, `uv.lock`, `.python-version` — are excluded from the installed
plugin. Antigravity CLI treats the path you install from as the plugin
root and does not fetch a remote subdirectory, so it installs from a local
checkout pointed at the subtree (see README.md). Component directories such as `skills/` live at the subtree
root, not inside its `.claude-plugin/`, or the clients would not load them. When
adding development assets, keep them at the repository root and leave only the
manifests and `skills/` inside `plugin/example-plugin/`.
