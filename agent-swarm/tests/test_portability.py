#!/usr/bin/env python3
"""Deterministic checks for host-neutral installer, scripts, and wording."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parent
SCRIPTS = SKILL_ROOT / "scripts"
FORBIDDEN_TERMS = (
    "kimi",
    "kimi code",
    "kimi cli",
    "moonshot",
    "k2.5",
    "k2.6",
    ".kimi",
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    files = []
    for line in result.stdout.splitlines():
        path = REPO_ROOT / line
        if path.is_file():
            files.append(path)
    # include newly added untracked files that will be committed
    extra = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    for line in extra.stdout.splitlines():
        path = REPO_ROOT / line
        if path.is_file():
            files.append(path)
    return files


class SkillPortabilityTests(unittest.TestCase):
    def test_frontmatter_is_host_neutral(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: agent-swarm", text)
        self.assertNotIn("Kimi", text)
        self.assertNotIn("kimi", text)

    def test_installer_requires_explicit_target(self) -> None:
        completed = subprocess.run(
            ["python3", str(SCRIPTS / "installer.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--target", completed.stderr)

    def test_installer_copies_skill_into_isolated_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills" / "agent-swarm"
            completed = subprocess.run(
                [
                    "python3",
                    str(SCRIPTS / "installer.py"),
                    "--target",
                    str(dest),
                    "--source",
                    str(SKILL_ROOT),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertTrue((dest / "scripts" / "installer.py").is_file())
            self.assertFalse((dest / ".git").exists())

    def test_installer_does_not_probe_vendor_home_paths(self) -> None:
        source = (SCRIPTS / "installer.py").read_text(encoding="utf-8")
        for needle in ("~/.kimi", ".kimi/", "~/.claude", "~/.cursor", "detect_installed_tools"):
            self.assertNotIn(needle, source)

    def test_scripts_do_not_use_shell_subprocess(self) -> None:
        for script in SCRIPTS.glob("*.py"):
            tree = ast.parse(script.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    name = None
                    if isinstance(func, ast.Attribute) and func.attr == "run":
                        if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                            name = "subprocess.run"
                    if name == "subprocess.run":
                        for kw in node.keywords:
                            if kw.arg == "shell":
                                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                    self.fail(f"{script.name} invokes subprocess.run(shell=True)")

    def test_dispatch_writes_host_neutral_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            swarm = Path(tmp) / "swarm"
            (swarm / "agent-01").mkdir(parents=True)
            (swarm / "SPEC.md").write_text(
                "# SPEC\n\n### Agent 1\n\n- Scope: parser\n- Files: src/parser.py\n- Interfaces: parse()\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["python3", str(SCRIPTS / "dispatch.py"), "--swarm-dir", str(swarm)],
                capture_output=True,
                text=True,
                check=False,
                cwd=tmp,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            prompt = (swarm / "agent-01" / "PROMPT.md").read_text(encoding="utf-8")
            self.assertIn("Implement: parser", prompt)
            self.assertNotIn("Agent()", prompt)
            self.assertNotIn("run_in_background", completed.stdout)

    def test_dispatch_updates_metadata_for_selected_swarm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected = root / ".swarm" / "output" / "20260917-010000"
            newer = root / ".swarm" / "output" / "20260917-020000"
            (selected / "agent-01").mkdir(parents=True)
            (newer / "agent-01").mkdir(parents=True)
            (selected / "SPEC.md").write_text(
                "# SPEC\n\n### Agent 1\n\n- Scope: parser\n- Files: src/parser.py\n- Interfaces: parse()\n",
                encoding="utf-8",
            )
            log_dir = root / ".swarm-log"
            log_dir.mkdir()
            selected_meta = log_dir / "swarm-20260917-010000.json"
            newer_meta = log_dir / "swarm-20260917-020000.json"
            selected_meta.write_text(
                json.dumps({"swarm_dir": ".swarm/output/20260917-010000", "status": "initialized"}),
                encoding="utf-8",
            )
            newer_meta.write_text(
                json.dumps({"swarm_dir": ".swarm/output/20260917-020000", "status": "initialized"}),
                encoding="utf-8",
            )
            os.utime(selected_meta, (1, 1))
            os.utime(newer_meta, (2, 2))

            completed = subprocess.run(
                ["python3", str(SCRIPTS / "dispatch.py"), "--swarm-dir", str(selected)],
                capture_output=True,
                text=True,
                check=False,
                cwd=root,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            selected_state = json.loads(selected_meta.read_text(encoding="utf-8"))
            newer_state = json.loads(newer_meta.read_text(encoding="utf-8"))
            self.assertEqual(selected_state["status"], "dispatched")
            self.assertEqual(selected_state["agents_dispatched"], 1)
            self.assertEqual(newer_state["status"], "initialized")
            self.assertNotIn("agents_dispatched", newer_state)

    def test_init_and_merge_copy_are_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    "python3",
                    str(SCRIPTS / "init_swarm.py"),
                    "--agents",
                    "2",
                    "--project",
                    "portable-check",
                    "--no-git",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=tmp,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            swarm_dirs = list((Path(tmp) / ".swarm" / "output").iterdir())
            self.assertEqual(len(swarm_dirs), 1)
            (swarm_dirs[0] / "agent-01" / "note.txt").write_text("ok\n", encoding="utf-8")
            merge = subprocess.run(
                [
                    "python3",
                    str(SCRIPTS / "merge.py"),
                    "--swarm-dir",
                    str(swarm_dirs[0]),
                    "--strategy",
                    "copy",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=tmp,
            )
            self.assertEqual(merge.returncode, 0, merge.stderr)
            self.assertTrue((swarm_dirs[0] / "integration" / "note.txt").is_file())

    def test_tracked_sources_have_no_active_kimi_coupling(self) -> None:
        hits = []
        for path in tracked_files():
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel.startswith("agent-swarm/tests/"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            lowered = text.lower()
            for term in FORBIDDEN_TERMS:
                if term in lowered:
                    hits.append(f"{rel}: {term}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
