# Troubleshooting

<!-- step: trouble-01 -->
## trouble-01 - `claude` not found
Install Claude Code from https://code.claude.com/docs/en/overview, open a **new** terminal and run the plan again.

<!-- step: trouble-02 -->
## trouble-02 - Python is not found, or the Microsoft Store opens
On Windows `python` can be a Store stub (exit code 9009). Try `py -3 --version`. Install Python 3.12 from python.org or `winget install --id Python.Python.3.12 -e --source winget`, then open a new terminal.

<!-- step: trouble-03 -->
## trouble-03 - Playwright is blocked: Node is missing
Install Node LTS (`winget install --id OpenJS.NodeJS.LTS -e --source winget` on Windows, `brew install node` on macOS), open a **new** terminal and run `apply` again. The installer never installs Node for you.

<!-- step: trouble-04 -->
## trouble-04 - Superpowers is blocked or fails
Git must be installed (plugins are fetched from GitHub). If the failure line mentions the network, check the connection and run `apply` again. You can also add it by hand inside Claude Code: `/plugin install superpowers@claude-plugins-official`.

<!-- step: trouble-05 -->
## trouble-05 - The plugin or the server does not show up
Restart Claude Code (close it and run `claude` again): plugins and servers are read at start. Then `claude plugin list` and `claude mcp get playwright`. Run `python install/setup.py verify`.

<!-- step: trouble-06 -->
## trouble-06 - I want the browser to have a window
Run `claude mcp remove playwright --scope user`, then `claude mcp add --scope user --transport stdio playwright -- npx @playwright/mcp@0.0.83 --isolated` (Windows: `cmd /c npx ...`). Note that `uninstall` will then no longer treat the server as one it added.

<!-- step: trouble-07 -->
## trouble-07 - My CLAUDE.md looks different
The block is between `<!-- avc-claude-code-setup:begin v1 -->` and `<!-- avc-claude-code-setup:end -->`. Everything outside the markers is yours. A backup of the file from before the first change is in `~/.avc/claude-code-setup/backups/`.
