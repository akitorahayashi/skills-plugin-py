# skills-plugin

A minimal template for packaging Agent Skills as a plugin that installs natively on Claude Code, Codex CLI, and Antigravity CLI. One repository is one plugin holding one or more related skills, distributed from a single shared `skills/` directory with one small manifest per client.

## Structure

```text
skills-plugin/
├── skills/
│   └── example-skill/
│       └── SKILL.md         # one directory per skill; name comes from SKILL.md frontmatter
├── .claude-plugin/
│   ├── plugin.json          # Claude Code manifest
│   └── marketplace.json     # distribution catalog (marketplace)
├── .codex-plugin/
│   └── plugin.json          # Codex manifest
└── plugin.json              # Antigravity CLI manifest
```

`skills/` is shared across all three clients. Each manifest carries only that client's identity; the skill body is never duplicated.

Component files (`skills/`, and later `hooks/`, `agents/`, `commands/`, `.mcp.json`) live at the repository root. Only `plugin.json` belongs inside `.claude-plugin/` and `.codex-plugin/`.

## What each manifest requires

- Claude Code — skills under `skills/` are auto-discovered, so `.claude-plugin/plugin.json` needs no `skills` field. Metadata like `author`, `homepage`, `repository`, `license`, and `keywords` is optional.
- Codex — `.codex-plugin/plugin.json` declares `"skills": "./skills/"` and accepts the same optional metadata plus an `interface` block for install-surface presentation.
- Antigravity CLI — the root `plugin.json` is a closed schema: only `name` (required, `^[a-zA-Z0-9-_]+$`) and `description` are valid. Skills are discovered from `skills/`; do not add other fields.

## Customize

1. Rename `skills/example-skill/` to your skill's name and rewrite its `SKILL.md`. The `name` frontmatter sets the invocation name; the `description` frontmatter is the sentence the agent reads to decide when to use the skill, so make it a specific trigger.
2. Replace `example-plugin` with your plugin name (kebab-case) in all three manifests, and `example-marketplace` / `your-name` in `.claude-plugin/marketplace.json`.
3. Add more skills as sibling directories under `skills/`. Group related skills in one plugin rather than splitting one plugin per skill.
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

Public repositories can use the HTTPS URL instead of the SSH one.

### Codex

```bash
codex plugin marketplace add git@github.com:your-org/your-repo.git
codex plugin install example-plugin@example-marketplace
```

Alternatively, run `/plugins` in the Codex TUI to browse the registered marketplaces and install interactively.

### Antigravity CLI

```bash
agy plugin install https://github.com/your-org/your-repo.git
```

For a private repository, clone first and install from the local path.

```bash
git clone git@github.com:your-org/your-repo.git
agy plugin install ./your-repo
```
