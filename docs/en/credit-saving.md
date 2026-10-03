# Credit-saving rules - what they are and why

> Written 2026-10-03. Source: Anthropic's "Manage costs effectively" page for Claude Code (https://code.claude.com/docs/en/costs). The rules change how Claude Code behaves; they do not change your plan, and the saving is not measured here - check it yourself with `/usage`.

Claude Code sends the whole conversation with every message, so a smaller context costs less. The block added to `~/.claude/CLAUDE.md` (the text is in `templates/claude-md/credit-saver.md`) asks Claude Code to work in these ways:

<!-- step: saving-01 -->
## saving-01 - Keep the context small
Search first and read only the matching lines; do not paste long outputs; do not re-read what is already in the conversation; suggest `/clear` when the topic changes and `/compact` with what to keep when continuing. Use a subagent only for high-volume work, one at a time, on a smaller model.

<!-- step: saving-02 -->
## saving-02 - Do small things directly, big things with a short plan
A typo, a rename or a question is done directly, without planning workflows. Substantial or unclear work gets a short plan and your yes first, which avoids expensive re-work. The smallest change that satisfies the request; two to four lines at the end.

<!-- step: saving-03 -->
## saving-03 - Cheap tools and cheap proofs
A command-line tool instead of an extra MCP server when both can do the job; text snapshots instead of screenshots in the browser; the one relevant test instead of the whole suite.

<!-- step: saving-04 -->
## saving-04 - Things only you control
Claude Code will not change these by itself, but it will suggest them: `/usage` (see what you used), `/model` (a smaller model for routine work), `/effort` (lower for simple tasks), `/mcp` (turn off servers you do not use), Esc and `/rewind` (stop early and go back). The block also holds "compact instructions" so a compaction keeps the goal, decisions, files and errors.

The block itself is short on purpose: it is read on every message, and Anthropic advises keeping `CLAUDE.md` under about 200 lines. To remove it: `python install/setup.py uninstall --yes`, or delete the lines between the two marker comments.
