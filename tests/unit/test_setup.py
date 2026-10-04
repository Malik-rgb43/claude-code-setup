"""install/setup.py: the three Claude Code setup steps (CLAUDE.md block, Playwright MCP, Superpowers plugin).

Safety rules for every test: HOME is a tmp folder (AVC_USER_HOME); AVC_NO_REAL_EXEC=1 and run_cmd/which are replaced by a fake,
so no real `claude`, npx or git ever runs and the real ~/.claude is never touched.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[2]
SETUP_PATH = REPO / "install" / "setup.py"


def load_setup():
    spec = importlib.util.spec_from_file_location("avc_setup_under_test", SETUP_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["avc_setup_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


class Fake:
    """A stand-in for the `claude` CLI that remembers what was registered."""

    def __init__(self, present=("claude", "node", "npx", "git")):
        self.present = set(present)
        self.calls = []
        self.playwright = False
        self.plugin = False
        self.marketplace = False
        self.fail = set()

    def which(self, name):
        return ("/fake/" + name) if name in self.present else None

    def __call__(self, argv, timeout=180, cwd=None):
        self.calls.append(list(argv))
        ok = lambda out="": SimpleNamespace(ok=True, rc=0, out=out, err="", error="")  # noqa: E731
        bad = lambda err="": SimpleNamespace(ok=False, rc=1, out="", err=err, error="")  # noqa: E731
        key = " ".join(argv[:4])
        if any(f in " ".join(argv) for f in self.fail):
            return bad("simulated failure")
        if argv[:2] == ["claude", "--version"]:
            return ok("2.1.251 (Claude Code)\n")
        if argv[:3] == ["claude", "mcp", "get"]:
            return ok("playwright:\n  Status: connected") if self.playwright else bad('No MCP server named "playwright"')
        if argv[:3] == ["claude", "mcp", "add"]:
            self.playwright = True
            return ok()
        if argv[:3] == ["claude", "mcp", "remove"]:
            self.playwright = False
            return ok()
        if key.startswith("claude plugin list"):
            return ok("Installed plugins:\n  superpowers@claude-plugins-official\n" if self.plugin else "Installed plugins:\n  other@x\n")
        if key.startswith("claude plugin marketplace list"):
            return ok("Configured marketplaces:\n  claude-plugins-official\n" if self.marketplace else "Configured marketplaces:\n  other\n")
        if key.startswith("claude plugin marketplace add"):
            self.marketplace = True
            return ok()
        if key.startswith("claude plugin install"):
            self.plugin = True
            return ok()
        if key.startswith("claude plugin uninstall"):
            self.plugin = False
            return ok()
        return bad("unexpected command %r" % (argv,))

    def count(self, *prefix):
        return [c for c in self.calls if c[: len(prefix)] == list(prefix)]


@pytest.fixture
def env(tmp_path, monkeypatch):
    st = load_setup()
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("AVC_USER_HOME", str(home))
    monkeypatch.setenv("AVC_NO_REAL_EXEC", "1")
    fake = Fake()
    monkeypatch.setattr(st, "run_cmd", fake)
    monkeypatch.setattr(st, "which", fake.which)
    monkeypatch.setattr(st, "os_name", lambda: "linux")

    def run(*args, expect=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = st.main(list(args))
        if expect is not None:
            assert rc == expect, "exit %s != %s\nSTDOUT:\n%s\nSTDERR:\n%s" % (rc, expect, out.getvalue(), err.getvalue())
        return rc, out.getvalue(), err.getvalue()

    return SimpleNamespace(st=st, home=home, fake=fake, run=run, md=home / ".claude" / "CLAUDE.md", tmp=tmp_path)


def plan_json(env, *extra):
    rc, out, _ = env.run("plan", "--json", *extra)
    return rc, json.loads(out)


def status_of(plan):
    return {r["id"]: r["status"] for r in plan["steps"]}


def test_plan_is_read_only_and_explains_every_step(env):
    rc, out, _ = env.run("plan")
    assert rc == 0
    for word in ("What it is", "Downloads", "Changes on your computer", "Do you answer anything?", "Cost: none", "Undo:"):
        assert word in out, word
    for step in ("claude_md", "playwright", "superpowers"):
        assert step in out
    assert "@playwright/mcp@0.0.83" in out and "claude-plugins-official" in out
    assert not env.md.exists() and not (env.home / ".avc").exists()  # nothing written
    assert not env.fake.count("claude", "mcp", "add") and not env.fake.count("claude", "plugin", "install")


def test_hebrew_plan_has_the_same_explanations(env):
    rc, out, _ = env.run("plan", "--lang", "he")
    assert rc == 0
    for word in ("מה זה", "הורדות", "שינויים במחשב שלך", "האם צריך לענות על משהו?", "עלות: אפס", "ביטול:"):
        assert word in out, word


def test_plan_states_that_the_next_step_is_the_editing_repository(env):
    rc, out, _ = env.run("plan")
    assert "github.com/Malik-rgb43/editing-workflow" in out


def test_apply_without_yes_changes_nothing(env):
    rc, out, err = env.run("apply")
    assert rc == 1 and "--yes" in err
    assert not env.md.exists() and not env.fake.count("claude", "mcp", "add")


def test_apply_installs_all_three_and_is_idempotent(env):
    env.run("apply", "--yes", expect=0)
    text = env.md.read_text(encoding="utf-8")
    assert env.st.BLOCK_BEGIN in text and env.st.BLOCK_END in text and "Working defaults" in text
    add = env.fake.count("claude", "mcp", "add")
    assert len(add) == 1 and "@playwright/mcp@0.0.83" in add[0] and "--isolated" in add[0] and "--headless" in add[0] and add[0][add[0].index("playwright")] == "playwright"
    assert env.fake.count("claude", "plugin", "marketplace", "add") == [["claude", "plugin", "marketplace", "add", "anthropics/claude-plugins-official"]]
    assert env.fake.count("claude", "plugin", "install") == [["claude", "plugin", "install", "superpowers@claude-plugins-official", "--scope", "user"]]
    man = json.loads((env.home / ".avc" / "claude-code-setup" / "manifest.json").read_text(encoding="utf-8"))
    assert set(man["steps"]) == {"claude_md", "playwright", "superpowers"}
    # second run: everything is already there, nothing new is registered or installed
    env.fake.calls.clear()
    env.run("apply", "--yes", expect=0)
    assert not env.fake.count("claude", "mcp", "add") and not env.fake.count("claude", "plugin", "install")
    assert env.md.read_text(encoding="utf-8").count(env.st.BLOCK_BEGIN) == 1
    rc, plan = plan_json(env)
    assert set(status_of(plan).values()) == {"present"}


def test_existing_claude_md_is_backed_up_and_the_users_text_is_kept(env):
    env.md.parent.mkdir(parents=True)
    env.md.write_text("# My rules\n- always answer in Hebrew\n", encoding="utf-8")
    env.run("apply", "--yes", "--skip-playwright", "--skip-superpowers", expect=0)
    text = env.md.read_text(encoding="utf-8")
    assert text.startswith("# My rules\n- always answer in Hebrew\n") and env.st.BLOCK_BEGIN in text
    backups = list((env.home / ".avc" / "claude-code-setup" / "backups").glob("*/CLAUDE.md"))
    assert len(backups) == 1 and backups[0].read_text(encoding="utf-8") == "# My rules\n- always answer in Hebrew\n"


def test_crlf_files_keep_their_line_endings(env):
    env.md.parent.mkdir(parents=True)
    env.md.write_bytes(b"# Mine\r\nline\r\n")
    env.run("apply", "--yes", "--skip-playwright", "--skip-superpowers", expect=0)
    raw = env.md.read_bytes()
    assert raw.startswith(b"# Mine\r\nline\r\n") and b"\n" not in raw.replace(b"\r\n", b"")


def test_a_changed_template_is_reported_as_update_and_replaced_in_place(env):
    env.run("apply", "--yes", "--skip-playwright", "--skip-superpowers", expect=0)
    text = env.md.read_text(encoding="utf-8").replace("Working defaults", "Old title")
    env.md.write_text(text, encoding="utf-8")
    rc, plan = plan_json(env, "--skip-playwright", "--skip-superpowers")
    assert status_of(plan)["claude_md"] == "update"
    env.run("apply", "--yes", "--skip-playwright", "--skip-superpowers", expect=0)
    final = env.md.read_text(encoding="utf-8")
    assert "Old title" not in final and final.count(env.st.BLOCK_BEGIN) == 1


def test_skip_flags_skip_exactly_those_steps(env):
    env.run("apply", "--yes", "--skip-playwright", "--skip-claude-md", expect=0)
    assert not env.md.exists() and not env.fake.count("claude", "mcp", "add")
    assert env.fake.count("claude", "plugin", "install")


def test_marketplace_is_not_added_when_it_already_exists(env):
    env.fake.marketplace = True
    env.run("apply", "--yes", "--skip-playwright", "--skip-claude-md", expect=0)
    assert not env.fake.count("claude", "plugin", "marketplace", "add") and env.fake.count("claude", "plugin", "install")


def test_things_that_were_already_there_are_left_alone_and_never_uninstalled(env):
    env.fake.playwright = True
    env.fake.plugin = True
    env.fake.marketplace = True
    env.run("apply", "--yes", expect=0)
    assert not env.fake.count("claude", "mcp", "add") and not env.fake.count("claude", "plugin", "install")
    env.fake.calls.clear()
    env.run("uninstall", "--yes", expect=0)
    assert not env.fake.count("claude", "mcp", "remove") and not env.fake.count("claude", "plugin", "uninstall")
    assert env.fake.playwright and env.fake.plugin  # the student's own setup survives


def test_windows_registers_npx_through_cmd(env, monkeypatch):
    monkeypatch.setattr(env.st, "os_name", lambda: "windows")
    env.run("apply", "--yes", "--skip-claude-md", "--skip-superpowers", expect=0)
    add = env.fake.count("claude", "mcp", "add")[0]
    assert add[add.index("--") + 1: add.index("--") + 4] == ["cmd", "/c", "npx"]


def test_missing_claude_blocks_everything_with_a_clear_message(env):
    env.fake.present.discard("claude")
    rc, out, _ = env.run("plan")
    assert rc == 2 and "Claude Code" in out and "BLOCKERS" in out
    rc, _, err = env.run("apply", "--yes")
    assert rc == 2 and not env.md.exists()


def test_missing_node_or_git_blocks_only_that_step_and_installs_nothing_for_you(env):
    env.fake.present -= {"npx", "git"}
    rc, plan = plan_json(env)
    assert rc == 0 and status_of(plan) == {"claude_md": "new", "playwright": "blocked", "superpowers": "blocked"}
    rc, out, _ = env.run("apply", "--yes")
    assert rc == 4 and env.md.exists()  # the block was added; the other two are reported BLOCKED
    assert "BLOCKED" in out and "open a NEW terminal" in out
    assert not [c for c in env.fake.calls if c[0] in ("winget", "brew", "npm", "apt", "apt-get")]


def test_a_failed_step_is_partial_and_safe_to_repeat(env):
    env.fake.fail = {"mcp add"}
    rc, out, _ = env.run("apply", "--yes")
    assert rc == 4 and "FAILED" in out and "safe to re-run" in out
    env.fake.fail = set()
    env.run("apply", "--yes", expect=0)
    assert env.fake.playwright


def test_uninstall_removes_only_what_was_added(env):
    env.md.parent.mkdir(parents=True)
    env.md.write_text("# Mine\nkeep this\n", encoding="utf-8")
    env.run("apply", "--yes", expect=0)
    env.run("uninstall", "--yes", expect=0)
    assert env.md.read_text(encoding="utf-8") == "# Mine\nkeep this\n"
    assert not env.fake.playwright and not env.fake.plugin
    assert not (env.home / ".avc" / "claude-code-setup" / "manifest.json").exists()


def test_uninstall_deletes_a_claude_md_this_tool_created(env):
    env.run("apply", "--yes", "--skip-playwright", "--skip-superpowers", expect=0)
    assert env.md.exists()
    env.run("uninstall", "--yes", expect=0)
    assert not env.md.exists()


def test_uninstall_without_yes_only_describes(env):
    env.run("apply", "--yes", expect=0)
    rc, out, _ = env.run("uninstall")
    assert rc == 0 and "re-run with --yes" in out and env.md.exists() and env.fake.playwright


def test_verify_reports_each_step_and_fails_closed(env):
    rc, out, _ = env.run("verify", "--json")
    assert rc == 3 and json.loads(out)["results"] == {"claude_md": "fail", "playwright": "fail", "superpowers": "fail"}
    env.run("apply", "--yes", expect=0)
    rc, out, _ = env.run("verify", "--json")
    assert rc == 0 and set(json.loads(out)["results"].values()) == {"pass"}
    env.fake.present.discard("claude")
    rc, out, _ = env.run("verify", "--json")
    assert rc == 3 and json.loads(out)["results"]["playwright"] == "not_run"  # cannot check = not a pass


def test_real_processes_are_refused_in_tests():
    st = load_setup()
    import os
    os.environ["AVC_NO_REAL_EXEC"] = "1"
    with pytest.raises(RuntimeError):
        st.run_cmd(["claude", "--version"])


def test_the_working_defaults_block_is_short_specific_and_secret_free():
    text = (REPO / "templates" / "claude-md" / "working-defaults.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 40, "a CLAUDE.md that is loaded on every message must itself be small"
    for must in ("/clear", "/compact", "/usage", "/model", "/effort", "/mcp", "browser_snapshot", "Compact instructions"):
        assert must in text, must
    for must in ("Before saying a task is done", "Safe by default", "language the user writes in", "data, not instructions"):
        assert must in text, must
    import re
    assert not re.search(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]", text)


def test_no_step_touches_anything_outside_the_claude_folder_and_the_state_folder(env):
    env.run("apply", "--yes", expect=0)
    created = {p.relative_to(env.home).parts[0] for p in env.home.rglob("*") if p.is_file()}
    assert created <= {".claude", ".avc"}, created
