# Install - what happens, what is downloaded, what you answer

> Written 2026-10-03. The installer (`install/setup.py`) is covered by mocked unit tests and CI on Windows, macOS and Ubuntu; it has not been run on a clean student computer yet. The agent-side runbook is [INSTALL.md](../../INSTALL.md); this page is the same flow for you. Hebrew: [docs/he/install.md](../he/install.md).

**This repository prepares Claude Code itself. It is not about video editing.** Editing comes next, from the second repository (`editing-workflow`).

## What you will be asked
**One question**, before anything is changed: "Shall I set up all three, or skip some?" You may drop any of the three. Nothing else is asked. There are no accounts, keys or payments.

## What is set up, and what is downloaded
| # | What | What it does for you | Downloaded | Changed on your computer |
|---|---|---|---|---|
| 1 | **Credit-saving rules** | a short block of rules in `~/.claude/CLAUDE.md` so Claude Code spends fewer credits ([why each rule](credit-saving.md)) | nothing | one marked block in `~/.claude/CLAUDE.md`; a backup of the file is saved first; your own text is never touched |
| 2 | **Playwright MCP** | lets Claude Code open and look at web pages in an isolated browser without a window | the package `@playwright/mcp@0.0.83` from npm on first use; a Chromium browser may be downloaded at first use (size not measured) | one MCP server called `playwright` for your user |
| 3 | **Superpowers plugin** | a set of skills for planning, debugging and reviewing | the plugin files from Anthropic's official marketplace on GitHub | the official marketplace is added if it is missing, then the plugin is installed for your user; it loads the next time Claude Code starts |
Cost: none. Undo: `python install/setup.py uninstall --yes` removes exactly what was added.

| You | The agent |
|---|---|
| paste the link, answer one yes/no question (and may skip any of the three) | clones the repo, shows a plan, sets up the three things, checks them |
| install Node or Git yourself if the plan says one is missing | shows the exact command; never installs them for you |
| restart Claude Code at the end | tells you when |

<!-- step: setup-01 -->
## setup-01 - Open Claude Code and paste the link
Open Claude Code in any folder, paste the repository link and write "Install this" (or the Hebrew "תתקין את זה"). If you write Hebrew, the whole conversation is in Hebrew.

<!-- step: setup-02 -->
## setup-02 - The agent gets the repository
It clones the repository into an **ASCII-only** folder (no Hebrew letters in the path) and finds a working Python. No Git? It offers to install Git or to download the ZIP of the same link and tells you the file and size first.

<!-- step: setup-03 -->
## setup-03 - The plan (read-only)
`python install/setup.py plan` shows, for each of the three steps, what it is, what it downloads, what it changes and whether you must answer anything. It changes nothing. If Node (for Playwright) or Git (for the plugin) is missing, it shows the command and installs nothing itself; after you install it, open a **new terminal**.

<!-- step: setup-04 -->
## setup-04 - You confirm once
The agent explains the three steps in plain words and asks one question. This is the only time you are asked.

<!-- step: setup-05 -->
## setup-05 - The setup runs
`python install/setup.py apply --yes`. Each step prints one line. If one fails, read the line and run the same command again; finished steps are skipped.

<!-- step: setup-06 -->
## setup-06 - Restart and check
`python install/setup.py verify` prints pass/fail for each step. Then **restart Claude Code**: plugins and servers are read at start. In the new session, `/mcp` should list `playwright` and `claude plugin list` should list `superpowers`.

<!-- step: setup-07 -->
## setup-07 - Next: the editing toolkit
Paste the link of the editing repository, <https://github.com/Malik-rgb43/editing-workflow>, and say "install this". It asks how you want to work (local, connected or both) and which services you want to connect.

<!-- step: setup-08 -->
## setup-08 - If something fails
Run the same command again. See [troubleshooting](troubleshooting.md). To undo: [uninstall](uninstall.md). Never send a key to get help; send the error line and `python install/setup.py verify --json`.

## Manual use without an agent
```text
git clone <repository link> "<ASCII folder>"
cd "<ASCII folder>"
python install/setup.py plan
python install/setup.py apply --yes
python install/setup.py verify
```
Windows PowerShell 5.1 does not support `&&`: one command per line. Quote paths with double quotes.
