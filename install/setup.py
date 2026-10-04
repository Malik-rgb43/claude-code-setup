#!/usr/bin/env python3
"""claude-code-setup - prepares Claude Code for a student (Python stdlib only). Three things, nothing about video editing:

  1. a working-defaults block (context/credit saving, verification, safety) in ~/.claude/CLAUDE.md (marked, backed up, removable)
  2. the Playwright MCP server (pinned, isolated, headless)
  3. the Superpowers plugin (from Anthropic's official plugin marketplace)

Usage: python install/setup.py [plan|apply|verify|status|uninstall] [options]

Default command is `plan` (read-only). Nothing is changed without `apply --yes`.
No telemetry. No secrets are read, asked for or written. Windows, macOS, Linux.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent
VERSION = "0.4.0"
BLOCK_BEGIN = "<!-- avc-claude-code-setup:begin v1 -->"
BLOCK_END = "<!-- avc-claude-code-setup:end -->"
TEMPLATE = Path("templates") / "claude-md" / "working-defaults.md"
PLAYWRIGHT_PIN = "@playwright/mcp@0.0.83"  # verified on npm 2026-10-03; node >= 18
MARKETPLACE_NAME = "claude-plugins-official"
MARKETPLACE_SOURCE = "anthropics/claude-plugins-official"
PLUGIN_ID = "superpowers@" + MARKETPLACE_NAME
EDITING_REPO_URL = "https://github.com/Malik-rgb43/editing-workflow"
STEPS = ("claude_md", "playwright", "superpowers")
EXIT_OK, EXIT_USAGE, EXIT_REFUSED, EXIT_VERIFY, EXIT_PARTIAL = 0, 1, 2, 3, 4

MSG = {
    "en": {
        "title": "Claude Code setup - plan (read-only, nothing has been changed)",
        "host": "This computer", "steps": "What will be set up", "what": "What it is", "downloads": "Downloads", "changes": "Changes on your computer",
        "answer": "Do you answer anything?", "status": "Status", "cost": "Cost: none. No account, no key, no payment.",
        "undo": "Undo: python install/setup.py uninstall --yes  (removes exactly what was added)",
        "confirm": "Ask the student ONE question: shall I go ahead with all three, or which of them to skip? Then run: python install/setup.py apply --yes",
        "next": "Next: when this is done, paste the editing toolkit link into Claude Code and say \"install this\": " + EDITING_REPO_URL,
        "s_new": "will be added", "s_update": "will be updated", "s_present": "already there", "s_skip": "skipped by you", "s_blocked": "blocked",
        "claude_md.what": "A short block of general rules in ~/.claude/CLAUDE.md for every project: small context and targeted reads (fewer credits), explore-plan-build for big work, a real check before saying done, and safe defaults (no commit/delete/secrets unless you ask; answers in your language).",
        "claude_md.downloads": "Nothing.",
        "claude_md.changes": "Adds one marked block to ~/.claude/CLAUDE.md (a backup of the file is saved first). Your own text in that file is never touched.",
        "playwright.what": "The Playwright MCP server: a browser Claude Code can drive to look at pages (isolated and headless, version pinned).",
        "playwright.downloads": "The package " + PLAYWRIGHT_PIN + " from npm the first time it runs; a Chromium browser may be downloaded on first use (size not measured here).",
        "playwright.changes": "Registers one MCP server called `playwright` for your user (via `claude mcp add`).",
        "superpowers.what": "The Superpowers plugin: a set of skills for planning, debugging and reviewing work in Claude Code.",
        "superpowers.downloads": "The plugin files from Anthropic's official plugin marketplace on GitHub (" + MARKETPLACE_SOURCE + ").",
        "superpowers.changes": "Adds the official marketplace if it is missing and installs the plugin for your user (via `claude plugin install`). It loads the next time Claude Code starts.",
        "answer_none": "No. One yes before it starts; you may skip any of the three.",
        "present_note": "Nothing: it is already on this computer and stays exactly as it is.",
    },
    "he": {
        "title": "הכנת Claude Code - תוכנית (קריאה בלבד, שום דבר לא שונה)",
        "host": "המחשב הזה", "steps": "מה יוגדר", "what": "מה זה", "downloads": "הורדות", "changes": "שינויים במחשב שלך",
        "answer": "האם צריך לענות על משהו?", "status": "מצב", "cost": "עלות: אפס. בלי חשבון, בלי מפתח ובלי תשלום.",
        "undo": "ביטול: python install/setup.py uninstall --yes  (מסיר בדיוק מה שנוסף)",
        "confirm": "שואלים את התלמיד שאלה אחת: להמשיך עם שלושתם, או מה לדלג? ואז מריצים: python install/setup.py apply --yes",
        "next": "השלב הבא: כשזה נגמר, מדביקים ב-Claude Code את הלינק של ארגז הכלים לעריכה ואומרים \"תתקין את זה\": " + EDITING_REPO_URL,
        "s_new": "יתווסף", "s_update": "יתעדכן", "s_present": "כבר קיים", "s_skip": "דילגת", "s_blocked": "חסום",
        "claude_md.what": "בלוק קצר של כללים כלליים בקובץ ~/.claude/CLAUDE.md לכל פרויקט: הקשר קטן וקריאות ממוקדות (פחות קרדיטים), חקירה-תוכנית-בנייה לעבודה גדולה, בדיקה אמיתית לפני \"סיימתי\", וברירות מחדל בטוחות (בלי commit/מחיקה/סודות אלא אם ביקשת; תשובות בשפה שלך).",
        "claude_md.downloads": "כלום.",
        "claude_md.changes": "מוסיף בלוק מסומן אחד ל-~/.claude/CLAUDE.md (קודם נשמר גיבוי של הקובץ). הטקסט שלך בקובץ הזה אף פעם לא נוגעים בו.",
        "playwright.what": "שרת Playwright MCP: דפדפן ש-Claude Code יכול להפעיל כדי לראות דפים (מבודד, בלי חלון, בגרסה נעוצה).",
        "playwright.downloads": "החבילה " + PLAYWRIGHT_PIN + " מ-npm בהרצה הראשונה; ייתכן שדפדפן Chromium יורד בשימוש הראשון (הגודל לא נמדד כאן).",
        "playwright.changes": "רושם שרת MCP אחד בשם `playwright` למשתמש שלך (דרך `claude mcp add`).",
        "superpowers.what": "התוסף Superpowers: אוסף סקילים לתכנון, דיבוג וסקירה של עבודה ב-Claude Code.",
        "superpowers.downloads": "קבצי התוסף מחנות התוספים הרשמית של Anthropic ב-GitHub (" + MARKETPLACE_SOURCE + ").",
        "superpowers.changes": "מוסיף את החנות הרשמית אם היא חסרה ומתקין את התוסף למשתמש שלך (דרך `claude plugin install`). הוא נטען בפעם הבאה ש-Claude Code מופעל.",
        "answer_none": "לא. כן אחד לפני שמתחילים; אפשר לדלג על כל אחד משלושתם.",
        "present_note": "כלום: זה כבר קיים במחשב הזה ונשאר בדיוק כמו שהוא.",
    },
}


def tr(lang: str, key: str) -> str:
    return MSG.get(lang, MSG["en"]).get(key, MSG["en"].get(key, key))


def emit(text: str = "", file=None) -> None:
    out = file or sys.stdout
    try:
        print(text, file=out)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"), file=out)


# ----------------------------------------------------------------------------- environment
def user_home() -> Path:
    return Path(os.environ.get("AVC_USER_HOME") or Path.home())


def os_name() -> str:
    return {"Windows": "windows", "Darwin": "macos"}.get(platform.system(), "linux")


def which(name: str):
    return shutil.which(name)


def run_cmd(argv, timeout=180, cwd=None):
    """Run a command, never raise. Replaced in tests (no real `claude` call may happen in a unit test)."""
    if os.environ.get("AVC_NO_REAL_EXEC") == "1":
        raise RuntimeError("AVC_NO_REAL_EXEC=1: refusing to start a real process: %r" % (argv,))
    try:
        exe = which(argv[0]) or argv[0]
        p = subprocess.run([exe] + [str(a) for a in argv[1:]], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, cwd=cwd)
        return SimpleNamespace(ok=p.returncode == 0, rc=p.returncode, out=p.stdout or "", err=p.stderr or "", error="")
    except (OSError, subprocess.TimeoutExpired) as e:
        return SimpleNamespace(ok=False, rc=-1, out="", err="", error=str(e))


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Layout:
    def __init__(self, args):
        self.home = user_home()
        self.claude_dir = Path(args.claude_dir) if getattr(args, "claude_dir", None) else self.home / ".claude"
        self.claude_md = self.claude_dir / "CLAUDE.md"
        self.state_dir = Path(args.state_dir) if getattr(args, "state_dir", None) else self.home / ".avc" / "claude-code-setup"
        self.manifest = self.state_dir / "manifest.json"
        self.backups = self.state_dir / "backups"


def load_manifest(lay: Layout) -> dict:
    try:
        return json.loads(lay.manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_manifest(lay: Layout, data: dict) -> None:
    lay.state_dir.mkdir(parents=True, exist_ok=True)
    tmp = lay.manifest.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, lay.manifest)


# ----------------------------------------------------------------------------- the CLAUDE.md block
def block_body(repo: Path = None) -> str:
    text = ((repo or REPO) / TEMPLATE).read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").strip("\n")


def render_block(repo: Path = None, eol: str = "\n") -> str:
    return eol.join([BLOCK_BEGIN] + block_body(repo).split("\n") + [BLOCK_END])


def read_bytes_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace") if path.is_file() else ""


def claude_md_status(lay: Layout) -> str:
    existing = read_bytes_text(lay.claude_md)
    if BLOCK_BEGIN in existing and BLOCK_END in existing:
        pre, rest = existing.split(BLOCK_BEGIN, 1)
        cur = rest.split(BLOCK_END, 1)[0]
        want = "\n" + block_body() + "\n"
        return "present" if cur.replace("\r\n", "\n") == want else "update"
    return "new"


def upsert_block(lay: Layout, repo: Path = None) -> None:
    existing = read_bytes_text(lay.claude_md)
    eol = "\r\n" if "\r\n" in existing else "\n"
    block = render_block(repo, eol)
    if BLOCK_BEGIN in existing and BLOCK_END in existing:
        pre, rest = existing.split(BLOCK_BEGIN, 1)
        post = rest.split(BLOCK_END, 1)[1]
        new = pre + block + post
    else:
        new = existing + ((eol + eol) if existing and not existing.endswith(eol + eol) else "") + block + eol
    lay.claude_dir.mkdir(parents=True, exist_ok=True)
    tmp = lay.claude_md.with_name(lay.claude_md.name + ".tmp")
    tmp.write_bytes(new.encode("utf-8"))
    os.replace(tmp, lay.claude_md)


def strip_block(lay: Layout) -> bool:
    existing = read_bytes_text(lay.claude_md)
    if BLOCK_BEGIN not in existing or BLOCK_END not in existing:
        return False
    pre, rest = existing.split(BLOCK_BEGIN, 1)
    post = rest.split(BLOCK_END, 1)[1]
    new = (pre.rstrip("\r\n") + post.lstrip("\r\n")) if pre.strip() and post.strip() else (pre + post).strip("\r\n")
    if new.strip():
        new = new.rstrip("\r\n") + ("\r\n" if "\r\n" in existing else "\n")
    tmp = lay.claude_md.with_name(lay.claude_md.name + ".tmp")
    tmp.write_bytes(new.encode("utf-8"))
    os.replace(tmp, lay.claude_md)
    return True


# ----------------------------------------------------------------------------- probes of the other two steps
def playwright_present() -> bool:
    p = run_cmd(["claude", "mcp", "get", "playwright"], timeout=90)
    return p.ok and "No MCP server named" not in (p.out + p.err)


def plugin_present() -> bool:
    p = run_cmd(["claude", "plugin", "list"], timeout=90)
    return p.ok and ("superpowers@" in p.out)


def marketplace_present() -> bool:
    p = run_cmd(["claude", "plugin", "marketplace", "list"], timeout=90)
    return p.ok and (MARKETPLACE_NAME in p.out)


def playwright_argv() -> list:
    cmd = ["cmd", "/c", "npx"] if os_name() == "windows" else ["npx"]
    return ["claude", "mcp", "add", "--scope", "user", "--transport", "stdio", "playwright", "--"] + cmd + [PLAYWRIGHT_PIN, "--isolated", "--headless"]


# ----------------------------------------------------------------------------- plan
def detect_host() -> dict:
    claude = which("claude")
    ver = ""
    if claude:
        p = run_cmd(["claude", "--version"], timeout=60)
        ver = (p.out or "").strip().splitlines()[0] if p.ok and p.out.strip() else ""
    return {"os": os_name(), "arch": platform.machine(), "python": sys.version.split()[0], "claude": bool(claude), "claude_version": ver,
            "node": bool(which("node")), "npx": bool(which("npx")), "git": bool(which("git"))}


def build_plan(args) -> dict:
    lay = Layout(args)
    host = detect_host()
    skip = {"claude_md": args.skip_claude_md, "playwright": args.skip_playwright, "superpowers": args.skip_superpowers}
    steps, blockers = [], []
    if not host["claude"]:
        blockers.append("Claude Code (`claude`) was not found on PATH. Install it from https://code.claude.com/docs/en/overview, open a NEW terminal, then run this again.")
    for sid in STEPS:
        row = {"id": sid, "status": "new", "reason": ""}
        if skip[sid]:
            row["status"] = "skip"
        elif sid == "claude_md":
            row["status"] = claude_md_status(lay)
        elif not host["claude"]:
            row["status"], row["reason"] = "blocked", "needs Claude Code"
        elif sid == "playwright":
            if not host["npx"]:
                row["status"], row["reason"] = "blocked", "needs Node.js (npx). Install Node LTS (Windows: winget install --id OpenJS.NodeJS.LTS -e --source winget | macOS: brew install node), open a NEW terminal, run again. Nothing was installed for you."
            elif playwright_present():
                row["status"] = "present"
            else:
                row["argv"] = playwright_argv()
        elif sid == "superpowers":
            if not host["git"]:
                row["status"], row["reason"] = "blocked", "needs Git (plugins are fetched from GitHub). Install Git (Windows: winget install --id Git.Git -e --source winget | macOS: xcode-select --install), open a NEW terminal, run again."
            elif plugin_present():
                row["status"] = "present"
            else:
                row["add_marketplace"] = not marketplace_present()
                row["argv"] = ["claude", "plugin", "install", PLUGIN_ID, "--scope", "user"]
        steps.append(row)
    return {"command": "plan", "version": VERSION, "host": host, "steps": steps, "blockers": blockers,
            "paths": {"claude_md": str(lay.claude_md), "state": str(lay.state_dir)}, "cost": "none"}


def render_plan(plan: dict, lang: str) -> str:
    L = lambda k: tr(lang, k)  # noqa: E731
    h = plan["host"]
    o = ["=" * 72, L("title"), "=" * 72, "", "## " + L("host"),
         "  OS: %s (%s) | Claude Code: %s | Node/npx: %s | Git: %s" % (h["os"], h["arch"], h["claude_version"] or ("yes" if h["claude"] else "NOT FOUND"), "yes" if h["npx"] else "no", "yes" if h["git"] else "no"),
         "", "## " + L("steps")]
    for i, r in enumerate(plan["steps"], 1):
        o += ["", "%d. [%s] %s" % (i, L("s_" + r["status"]), r["id"]),
              "   %s: %s" % (L("what"), L(r["id"] + ".what")),
              "   %s: %s" % (L("downloads"), L("present_note") if r["status"] == "present" else L(r["id"] + ".downloads")),
              "   %s: %s" % (L("changes"), L("present_note") if r["status"] == "present" else L(r["id"] + ".changes")),
              "   %s: %s" % (L("answer"), L("answer_none"))]
        if r.get("reason"):
            o.append("   !! " + r["reason"])
    if plan["blockers"]:
        o += ["", "## BLOCKERS"] + ["  - " + b for b in plan["blockers"]]
    o += ["", L("cost"), L("undo"), "", L("confirm"), "", L("next")]
    return "\n".join(o)


# ----------------------------------------------------------------------------- apply / verify / uninstall
def cmd_plan(args) -> int:
    plan = build_plan(args)
    emit(json.dumps(plan, ensure_ascii=False, indent=2) if args.json else render_plan(plan, args.lang))
    return EXIT_REFUSED if plan["blockers"] else EXIT_OK


def cmd_apply(args) -> int:
    if not args.yes:
        emit("apply changes your computer. Review `plan`, get the student's ONE confirmation, then re-run with --yes.", file=sys.stderr)
        return EXIT_USAGE
    plan = build_plan(args)
    if plan["blockers"]:
        emit("blocked: " + "; ".join(plan["blockers"]), file=sys.stderr)
        return EXIT_REFUSED
    lay = Layout(args)
    man = load_manifest(lay) or {"schema": 1, "installed_at": now_utc(), "steps": {}}
    man["version"], man["updated_at"] = VERSION, now_utc()
    partial, lines = False, []
    for row in plan["steps"]:
        sid, st = row["id"], row["status"]
        if st in ("skip", "present") or (st == "blocked"):
            lines.append("%-12s %s%s" % (sid, {"skip": "skipped (you chose)", "present": "already there, untouched", "blocked": "BLOCKED"}[st], (": " + row["reason"]) if row.get("reason") else ""))
            partial = partial or st == "blocked"
            continue
        if sid == "claude_md":
            existed = lay.claude_md.is_file()
            backup = ""
            if existed:
                stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                bdir = lay.backups / stamp
                bdir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(lay.claude_md, bdir / "CLAUDE.md")
                backup = str(bdir / "CLAUDE.md")
            upsert_block(lay)
            man["steps"]["claude_md"] = {"ours": True, "existed_before": existed, "backup": backup, "at": now_utc()}
            lines.append("%-12s ok -> %s%s" % (sid, lay.claude_md, (" (backup: %s)" % backup) if backup else ""))
        elif sid == "playwright":
            p = run_cmd(row["argv"], timeout=180)
            dup = (not p.ok) and "already exists" in (p.out + p.err).lower()
            if p.ok or dup:
                man["steps"]["playwright"] = {"ours": p.ok, "at": now_utc()}
                lines.append("%-12s %s" % (sid, "ok (registered; the first use downloads what it needs)" if p.ok else "already registered"))
            else:
                partial = True
                lines.append("%-12s FAILED rc=%s: %s (safe to re-run)" % (sid, p.rc, (p.err or p.out or p.error).strip()[-300:]))
        elif sid == "superpowers":
            ok = True
            if row.get("add_marketplace"):
                m = run_cmd(["claude", "plugin", "marketplace", "add", MARKETPLACE_SOURCE], timeout=300)
                if not m.ok and "already" not in (m.out + m.err).lower():
                    ok = False
                    partial = True
                    lines.append("%-12s FAILED to add the marketplace rc=%s: %s (safe to re-run)" % (sid, m.rc, (m.err or m.out or m.error).strip()[-300:]))
            if ok:
                p = run_cmd(row["argv"], timeout=600)
                if p.ok:
                    man["steps"]["superpowers"] = {"ours": True, "at": now_utc()}
                    lines.append("%-12s ok (loads the next time Claude Code starts)" % sid)
                else:
                    partial = True
                    lines.append("%-12s FAILED rc=%s: %s (safe to re-run)" % (sid, p.rc, (p.err or p.out or p.error).strip()[-300:]))
    save_manifest(lay, man)
    for ln in lines:
        emit("  " + ln)
    emit("")
    emit("Next: python install/setup.py verify    (then restart Claude Code so it loads the plugin and the server)")
    emit(tr(args.lang, "next"))
    return EXIT_PARTIAL if partial else EXIT_OK


def verify_state(args) -> dict:
    lay = Layout(args)
    host = detect_host()
    res = {}
    res["claude_md"] = "pass" if claude_md_status(lay) == "present" else "fail"
    if not host["claude"]:
        res["playwright"] = res["superpowers"] = "not_run"
    else:
        res["playwright"] = "pass" if playwright_present() else "fail"
        res["superpowers"] = "pass" if plugin_present() else "fail"
    return res


def cmd_verify(args) -> int:
    res = verify_state(args)
    skipped = {"claude_md": args.skip_claude_md, "playwright": args.skip_playwright, "superpowers": args.skip_superpowers}
    for k, v in list(res.items()):
        if skipped[k]:
            res[k] = "skipped"
    if args.json:
        emit(json.dumps({"command": "verify", "results": res}, ensure_ascii=False, indent=2))
    else:
        for k, v in res.items():
            emit("  %-12s %s" % (k, v))
        emit("`claude doctor` only diagnoses the Claude Code installation. Restart Claude Code after setup so the plugin and the browser server are loaded.")
    return EXIT_VERIFY if any(v in ("fail", "not_run") for v in res.values()) else EXIT_OK


def cmd_status(args) -> int:
    lay = Layout(args)
    man = load_manifest(lay)
    emit(json.dumps(man or {"installed": False}, ensure_ascii=False, indent=2))
    return EXIT_OK


def cmd_uninstall(args) -> int:
    lay = Layout(args)
    man = load_manifest(lay)
    steps = man.get("steps", {}) if man else {}
    plan = ["remove the marked block from %s" % lay.claude_md] if (steps.get("claude_md") or claude_md_status(lay) != "new") else []
    if steps.get("playwright", {}).get("ours"):
        plan.append("claude mcp remove playwright --scope user")
    if steps.get("superpowers", {}).get("ours"):
        plan.append("claude plugin uninstall %s --scope user" % PLUGIN_ID)
    if not args.yes:
        emit("uninstall would: " + ("; ".join(plan) if plan else "nothing (nothing was installed by this tool)") + "\nre-run with --yes to do it")
        return EXIT_OK
    for item in plan:
        emit("  " + item)
    if steps.get("claude_md") or claude_md_status(lay) != "new":
        strip_block(lay)
        if not steps.get("claude_md", {}).get("existed_before", True) and lay.claude_md.is_file() and not read_bytes_text(lay.claude_md).strip():
            lay.claude_md.unlink()  # a file this tool created and nothing else lives in
    failed = False
    if steps.get("playwright", {}).get("ours"):
        failed |= not run_cmd(["claude", "mcp", "remove", "playwright", "--scope", "user"], timeout=90).ok
    if steps.get("superpowers", {}).get("ours"):
        failed |= not run_cmd(["claude", "plugin", "uninstall", PLUGIN_ID, "--scope", "user"], timeout=120).ok
    if not failed and lay.manifest.is_file():
        lay.manifest.unlink()
    emit("Done. Your other settings, servers and plugins were not touched." if not failed else "Some removals failed; see the lines above (safe to re-run).")
    return EXIT_PARTIAL if failed else EXIT_OK


# ----------------------------------------------------------------------------- cli
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="setup.py", description=__doc__.split("\n\n")[0],
                                epilog="Docs: INSTALL.md. Nothing is changed without `apply --yes`. No telemetry; no secrets are read or written.")
    p.add_argument("command", nargs="?", default="plan", choices=["plan", "apply", "verify", "status", "uninstall"])
    p.add_argument("--yes", action="store_true", help="the student's single confirmation was given")
    p.add_argument("--lang", choices=["en", "he"], default="en")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--skip-claude-md", action="store_true", help="do not add the working-defaults block")
    p.add_argument("--skip-playwright", action="store_true", help="do not register the Playwright MCP server")
    p.add_argument("--skip-superpowers", action="store_true", help="do not install the Superpowers plugin")
    p.add_argument("--claude-dir", help="Claude Code user folder. Default ~/.claude")
    p.add_argument("--state-dir", help="where the manifest and backups go. Default ~/.avc/claude-code-setup")
    p.add_argument("--repo", help=argparse.SUPPRESS)
    return p


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    args = build_parser().parse_args(argv)
    if args.repo:
        global REPO
        REPO = Path(args.repo).resolve()
    return {"plan": cmd_plan, "apply": cmd_apply, "verify": cmd_verify, "status": cmd_status, "uninstall": cmd_uninstall}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
