# Uninstall

<!-- step: uninstall-01 -->
## uninstall-01 - See what would be removed
```text
python install/setup.py uninstall
```
It only describes what it would remove.

<!-- step: uninstall-02 -->
## uninstall-02 - Remove it
```text
python install/setup.py uninstall --yes
```
It removes the marked block from `~/.claude/CLAUDE.md` (your own text stays; a `CLAUDE.md` that this tool created and that holds nothing else is deleted), the `playwright` server and the `superpowers` plugin **only if this tool added them**. A server or plugin that was already there before is left as it is. The backups in `~/.avc/claude-code-setup/backups/` are kept; delete that folder yourself when you no longer need it. The official plugin marketplace stays added (it is Claude Code's own).
