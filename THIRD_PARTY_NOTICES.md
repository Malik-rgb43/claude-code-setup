# Third-party notices

Not legal advice. Dates and licence terms are perishable (research snapshot 2026-10-01; src: blueprint/SECURITY_AND_LICENSING.md
sections 2-3, derived from the T18 licence review; every row there is `[SOURCED-unverified]` unless marked otherwise).
Licence texts, NOTICE files and change markers are added here at the moment a component is actually bundled.

## Generated from the bill of materials

The block below is rewritten by `python scripts/gen_bom.py --update-notices` from the third-party entries of `licenses.toml`
(files actually in the tree). Do not edit inside the markers.

<!-- BEGIN GENERATED:bom -->
<!-- GENERATED from docs/BOM.json by scripts/gen_bom.py --update-notices - edit outside this block only. -->

No third-party files are bundled in this tree (nothing to attribute here).

<!-- END GENERATED:bom -->

## Hand-written section: components this repository installs but does NOT bundle

Installed by the student's own Claude Code from the upstream source. Nothing in this table is redistributed by this repository.

| Component | Licence observed | Handling in this repository |
|---|---|---|
| Playwright MCP (`@playwright/mcp@0.0.83`, Microsoft) | Apache-2.0 (npm registry, checked 2026-10-03) | downloaded from npm by `npx` on first use; not bundled |
| Superpowers plugin (`obra/superpowers`) | MIT (LICENSE and plugin.json of the installed copy, checked 2026-10-03) | installed by `claude plugin install` from Anthropic's official marketplace; not bundled |
| Claude Code | Anthropic's own terms | installed by the student; not touched except for the marked block in `~/.claude/CLAUDE.md` and the commands `claude mcp add` / `claude plugin install` |
