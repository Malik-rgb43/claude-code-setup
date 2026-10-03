@AGENTS.md

Claude Code only: this repository changes your Claude Code setup (the marked block in `~/.claude/CLAUDE.md`, one MCP server, one plugin) through `install/setup.py` and the clients' own commands (`claude mcp add`, `claude plugin install`). Never edit those files by hand to "fix" a step; re-run `python install/setup.py apply --yes` or `uninstall --yes`.
