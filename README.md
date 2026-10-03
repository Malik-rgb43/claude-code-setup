# claude-code-setup - prepare Claude Code (repository 1 of 2)

This repository prepares **Claude Code itself**, in three small steps. It is not about video editing: the editing toolkit is the second repository, [`editing-workflow`](https://github.com/Malik-rgb43/editing-workflow).

| Step | What | Downloads | Changes on your computer |
|---|---|---|---|
| 1 | **Credit-saving rules** (`templates/claude-md/credit-saver.md`) | nothing | one marked block in `~/.claude/CLAUDE.md`, backed up first, removable |
| 2 | **Playwright MCP** | `@playwright/mcp@0.0.83` from npm on first use (and possibly a Chromium browser) | one MCP server `playwright` for your user |
| 3 | **Superpowers plugin** | plugin files from Anthropic's official marketplace on GitHub | the plugin, installed for your user |

## How a student uses it
Open Claude Code, paste this repository's link and say **"install this"** / **"תתקין את זה"**. The agent follows [INSTALL.md](INSTALL.md): it shows what will be downloaded and changed, asks **one** question (all three, or skip some), sets it up, checks it, and tells you to restart Claude Code. Cost: none. No account, key or payment. Undo: `python install/setup.py uninstall --yes`.

Then paste the link of the editing repository and say "install this" again: that one asks how you want to work (local, connected or both) and which services to connect, and installs HyperFrames.

## What is inside
| Path | What |
|---|---|
| `install/setup.py` | the installer (Python standard library only): `plan`, `apply --yes`, `verify`, `status`, `uninstall --yes` |
| `templates/claude-md/credit-saver.md` | the credit-saving block |
| `INSTALL.md`, `AGENTS.md` | the agent runbook and the rules |
| `docs/en`, `docs/he` | install (what is downloaded, what you answer), credit-saving rules explained, uninstall, troubleshooting |
| `docs/decisions/` | ADR 0005 (who owns what), 0004 (public, Apache-2.0) |
| `scripts/`, `tests/unit/` | the repository's own gates and 22 unit tests (no real `claude` call) |

## Honest status (2026-10-03)
* Covered by mocked unit tests and CI on Windows, macOS and Ubuntu. **Not** run on a clean student computer yet.
* The saving from the credit-saving rules is **not measured**; the rules follow Anthropic's cost guidance (https://code.claude.com/docs/en/costs). Measure with `/usage`.
* Licence: Apache-2.0 (see `LICENSE`, `NOTICE`). Third-party software (Playwright MCP, Superpowers, Claude Code) is downloaded, never bundled; their own licences apply.
