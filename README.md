# skills-plugin-py

A template for packaging Agent Skills that are backed by Python scripts, as a
plugin that installs natively on Claude Code, Codex CLI, and Antigravity CLI.
One repository is one plugin holding one or more related skills, distributed from
a single shared `skills/` directory with one small manifest per client. Each
skill drives a standard-library Python CLI that prints one JSON document.

The plugin lives in the `plugin/example-plugin/` subtree so that development
assets at the repository root stay out of what gets installed.

## Structure

```text
skills-plugin-py/
├── plugin/
│   └── example-plugin/                       # the distributed plugin (only this subtree installs)
│       ├── .claude-plugin/plugin.json        # Claude Code manifest
│       ├── .codex-plugin/plugin.json         # Codex manifest
│       ├── plugin.json                        # Antigravity CLI manifest
│       └── skills/
│           └── example-skill/
│               ├── SKILL.md                   # name comes from frontmatter
│               ├── scripts/summarize_records.py   # stdlib-only CLI, one JSON document, exit codes 0/1/2
│               ├── references/records-spec.schema.json  # strict spec the CLI validates against
│               └── assets/records.example.json         # example config
├── .claude-plugin/
│   └── marketplace.json                       # distribution catalog; git-subdir source -> plugin/example-plugin
├── tests/
│   ├── conftest.py                            # fixtures and a subprocess CLI runner
│   └── example_skill/                         # process-boundary tests, split by concern
├── pyproject.toml                             # development tools only (pytest / ruff / mypy)
├── Makefile                                   # make test / fix / lint
├── uv.lock                                    # development dependency lock
├── .python-version                            # development interpreter (uv)
├── README.md
├── AGENTS.md
└── CONTRIBUTING.md
```

`skills/` is shared across all three clients. Each manifest carries only that
client's identity; the skill body is never duplicated. Component directories
(`skills/`, and later `hooks/`, `agents/`, `commands/`, `.mcp.json`) live at the
plugin-subtree root. Only `plugin.json` belongs inside `.claude-plugin/` and
`.codex-plugin/`.

## What each manifest requires

Each manifest lives inside `plugin/example-plugin/`.

- Claude Code — skills under `skills/` are auto-discovered, so `plugin.json`
  needs no `skills` field. Metadata like `author`, `homepage`, `repository`,
  `license`, and `keywords` is optional.
- Codex — `.codex-plugin/plugin.json` declares `"skills": "./skills/"` and
  accepts the same optional metadata plus an `interface` block for install-surface
  presentation.
- Antigravity CLI — the `plugin.json` is a closed schema: only `name` (required,
  `^[a-zA-Z0-9-_]+$`) and `description` are valid. Skills are discovered from
  `skills/`; do not add other fields.

## The example skill

`plugin/example-plugin/skills/example-skill` demonstrates the conventions every
skill in this template follows. Its CLI reads a JSON config, validates it against
`references/records-spec.schema.json`, summarizes the records, and prints one
JSON document. It shows the whole contract: argparse arguments, standard-library
imports only, explicit validation with an actionable error, and exit codes 0
(a non-empty result), 1 (a valid config with no matching record), and 2 (a config
or runtime error, reported as JSON on stderr with an `action`). Rename the
directory and replace the skill with your own.

## Runtime and development separation

The skill CLIs run on the plugin user's own `python3` with no runtime
dependency. Every script under `skills/**/scripts/` imports only the standard
library, and the supported floor is Python 3.10. The dependencies in
`pyproject.toml` are development tools (pytest, ruff, mypy) synced by uv into a
local `.venv`; they are never installed into the runtime and never ship as a
plugin requirement.

## Distribution boundary

The distributed plugin is the `plugin/example-plugin/` subtree, selected by the
`git-subdir` source in `.claude-plugin/marketplace.json`. Claude Code and Codex
both read this marketplace and sparse-clone only that subtree, so the development
assets at the repository root (`tests/`, `pyproject.toml`, `Makefile`,
`uv.lock`, `.python-version`) are never part of the installed plugin. Component
directories such as `skills/` live at the subtree root, not inside its
`.claude-plugin/`, or the clients would not load them.

Antigravity CLI treats the path you install from as the plugin root and does not
fetch a subdirectory from a remote URL, so it installs from a local checkout
pointed at the subtree (see Install). This keeps the installed plugin clean on
every client at the cost of Antigravity's one-line remote install.

## Develop

Development uses [uv](https://docs.astral.sh/uv/). `make fix` applies formatting
and autofixes; `make lint` runs ruff and mypy; `make test` runs pytest. Run
`make fix` before `make lint`. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
full workflow and the CLI contract.

## Customize

1. Rename `plugin/example-plugin/` to your plugin name, and update the `path` in
   `.claude-plugin/marketplace.json` to match. Rename
   `plugin/<name>/skills/example-skill/` to your skill's name and rewrite its
   `SKILL.md`. The `name` frontmatter sets the invocation name; the `description`
   frontmatter is the sentence the agent reads to decide when to use the skill,
   so make it a specific trigger. Replace the CLI under `scripts/`, and the
   `references/` and `assets/` files, with your own.
2. Replace `example-plugin` with your plugin name (kebab-case) in the three
   manifests, and `example-marketplace` / `your-name` / the git-subdir `url` in
   `.claude-plugin/marketplace.json`.
3. Add more skills as sibling directories under `plugin/<name>/skills/`, and add
   tests under `tests/`. Group related skills in one plugin rather than splitting
   one plugin per skill.
4. Validate before distributing:

   ```bash
   claude plugin validate .
   ```

## Install

Replace the repository URL and the `plugin@marketplace` names with your own.

### Claude Code

```bash
claude plugin marketplace add git@github.com:your-org/your-repo.git
claude plugin install example-plugin@example-marketplace
```

Public repositories can use the HTTPS URL instead of the SSH one. The `git-subdir`
source sparse-clones only `plugin/example-plugin`.

### Codex

```bash
codex plugin marketplace add git@github.com:your-org/your-repo.git
codex plugin install example-plugin@example-marketplace
```

Alternatively, run `/plugins` in the Codex TUI to browse the registered
marketplaces and install interactively.

### Antigravity CLI

Antigravity stages the plugin from the path you give it, and that path must hold
`plugin.json` and `skills/`. The subtree does, so clone first and install from the
subtree path. A one-line remote install from the repository URL is not available,
because it would look for the plugin at the repository root.

```bash
git clone git@github.com:your-org/your-repo.git
agy plugin install ./your-repo/plugin/example-plugin
```
