# Changelog

All notable changes to the public contract of this toolkit are recorded here, newest first.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html).
Releases are immutable: a correction is a new release. Public since 2026-10-03 under Apache-2.0 (the `LICENSE` file is authoritative; older notes below about an undecided licence are historical).

Dates and facts here are perishable; each entry states its source where it relies on research
(src: blueprint/REPO_ARCHITECTURE.md section 10, 2026-10-02).

## [0.3.1] - 2026-10-03

### Changed
- **Privacy:** no details of the author's computer remain in the current files (hardware specs replaced by "one reference machine"; the private research repository name and a local lab path were removed from the scan rules). Earlier commits and tags still contain the old text.

## [0.3.0] - 2026-10-03

### Changed
- **Repository split revised (ADR 0005).** This repository now only prepares Claude Code: a credit-saving block in `~/.claude/CLAUDE.md`, the Playwright MCP server (pinned `@playwright/mcp@0.0.83`) and the Superpowers plugin, through the new small installer `install/setup.py`. The old installer (`install/bootstrap.py`), the integrations catalogue with sign-up links, the editing install questions and their docs moved to `editing-workflow`. `fetch` and the cross-repository pin no longer exist.

### Added
- `templates/claude-md/credit-saver.md`, `install/setup.py` (`plan`, `apply --yes`, `verify`, `status`, `uninstall --yes`), `docs/{en,he}/credit-saving.md`, 22 unit tests.

## [0.2.1] - 2026-10-03

### Added
- `integrations/referrals.toml`: sign-up links for paid services (Higgsfield, ElevenLabs, 21st.dev, 3D generation via Tripo). `bootstrap.py add <id>` prints them; a referral link is always labelled and disclosed ("supports this project, no extra cost to you"), the plain link is always shown beside it, nothing is opened without the student's yes, `--plain-links` hides referrals. The `referral_url` fields are empty until the maintainer fills them. Tests guard that every paid integration is covered.
- AGENTS.md rule 6 and INSTALL.md wording: disclose referral links, never answer "no" when asked, never add referral parameters to MCP / API / CLI calls.

### Changed
- The editing toolkit pin is now `v0.2.1` (the phone-style Seedance preset was removed there).

## [Unreleased]

### Added
- Repository hygiene: `.gitignore`, `.gitattributes` (LF everywhere, binary and generated markers), `.editorconfig`.
- `LICENSE` placeholder (licence undecided, decision default Q12: private until chosen), `THIRD_PARTY_NOTICES.md`
  (generated block + hand-written section), `licenses.toml` (declared licence per path, fail-closed).
- `release-manifest.json` template (schema, support matrix with unmeasured/untested labels, hash fields filled at build time).
- Deterministic gates in `scripts/`: skill checks, secret scan, private-path/client-name scan, bill of materials with
  blocked-component gating, agent-adapter generation with package parity, SYSTEM.md / TOOLS.md generators, link and
  step-id checks, workflow policy check, dry-run release builder with update/rollback plan, and `run_all_checks.py`.
- `tests/evals/run_trigger_evals.py`: deterministic dry run of every skill's trigger evals; reports `model_eval: not_run`;
  the model lane is a stub that refuses to run without `--approved-by-owner` and a budget cap (default 60).
- GitHub Actions: deterministic CPU lane on Windows, macOS and Ubuntu with least-privilege permissions; a disabled,
  manual, approval-gated model-eval workflow. Action pins are placeholders marked `TODO pin to reviewed commit`
  (they could not be verified offline) and a release build refuses to proceed until they are real commit SHAs.

### Known limits
- No skill has been evaluated with a model (decision default Q4); only deterministic checks exist.
- CI has not run on a hosted runner yet; only the local Windows run of the unit tests is evidenced.
