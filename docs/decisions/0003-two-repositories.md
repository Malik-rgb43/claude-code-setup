# ADR 0003 - Two repositories: Claude Code setup and the editing toolkit

> **Superseded by [ADR 0005](0005-repository-split-revised.md) (2026-10-03):** the installer, the integrations catalogue and the install questions moved to `editing-workflow`; this repository now only prepares Claude Code. Kept for history.

- Status: accepted (owner directive, 2026-10-02: "split it into 2 repos: one for the Claude Code setup, one for the editing setup")
- Date: 2026-10-02

## Decision
| | `claude-code-setup` | `editing-workflow` (editing) |
|---|---|---|
| Purpose | prepare the machine and the agent | what the agent uses to edit |
| Contains | `install/` (bootstrap.py), `integrations/` (MCP / CLI / API catalogue), Standard-profile templates, install docs (EN/HE), generic hygiene scripts | `agent-content/` (17 skills, playbooks, techniques, benchmarks, dated references), `tools/` + `src/core/`, `fixtures/`, `contracts/`, `profiles/`, `templates/`, `scripts/`, tests, legal/privacy guides |
| Student entry | pastes THIS link: "install this" | never needs to open it; the installer fetches it |
| Coupling | `bootstrap.py fetch` clones the editing repo (URL + pinned tag in `install/toolkit-source.toml`), or `--toolkit-src <checkout>` / a sibling folder; the skills are installed from it | none on the setup repo; the toolkit's own `tools/doctor.py` verifies the machine after install |

## Consequences
- Releases are independent: the setup repo changes when a CLI, MCP server or API changes; the editing repo changes when a skill or tool changes. The setup repo pins the editing repo by tag.
- The installer merges both into one managed toolkit home (`~/.avc/toolkit`) so skill paths such as `agent-content/...` and `tools/...` resolve.
- `toolkit-source.toml` has an empty `url` until the editing repo is published (decision default Q12, resolved by ADR 0004); the agent asks the student for the link meanwhile.

## Known limits
The cross-repo flow was verified with a local checkout (`--toolkit-src`), not with a `git clone` of a published repo.
