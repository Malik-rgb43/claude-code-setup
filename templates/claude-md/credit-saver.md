## Credit-saving defaults (added by claude-code-setup; remove this block with `python install/setup.py uninstall --yes`)
Every message re-sends the whole conversation, so a smaller context is cheaper. Work in a way that keeps it small.

### Context
- Search first (`grep`/file search), then read only the matching line ranges. Do not read whole large files, and do not paste or print long outputs: filter with `head`, `tail` or `grep` and show the relevant lines.
- Do not re-read files or re-run commands whose result is already in this conversation.
- When the topic changes, tell the user to run `/clear`. To continue the same task with a smaller context, suggest `/compact` with what to keep. After a long break in a big session, prefer `/clear`.
- Use a subagent only for high-volume work (long test output, a wide search), one at a time, on a smaller model. Never start agent teams or parallel subagents for a small task.

### How to work
- A small, clear request (typo, rename, one command, a question): do it directly. Skip planning workflows and process skills; they are for substantial or unclear work.
- Substantial or unclear work: propose a short plan first, wait for a yes, then build. If the direction is unclear, ask one question instead of guessing.
- Make the smallest change that satisfies the request: no unrequested refactors, no extra files, no long explanation afterwards. Finish with 2-4 lines: what changed and how it was checked.
- Check with the cheapest proof (the one relevant test or command, not the whole suite) and say what was not checked.

### Tools and models
- Prefer a command-line tool (`git`, `gh`, `ffmpeg`) to an MCP server when both can do the job. Use the Playwright browser tools only when you need to look at a rendered page, and prefer a text snapshot (`browser_snapshot`) to a screenshot.
- If the user mentions cost, suggest `/usage` to see it, `/model` to use a smaller model for routine work, `/effort` lower for simple tasks, and `/mcp` to turn off servers they no longer use. Do not change the model or effort yourself.
- If the user is heading the wrong way, say so early; Esc stops a run and `/rewind` goes back to a checkpoint.

### Compact instructions
When compacting, keep: the goal, decisions made, files changed, open problems and exact error messages. Drop exploration output and file contents that can be re-read.
