#!/usr/bin/env python3
"""Copy the agent-swarm skill into an explicit destination directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKIP_DIR_NAMES = {".git", "__pycache__", ".swarm", ".swarm-log"}


def skill_source(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def should_skip(path: Path, source: Path) -> bool:
    rel_parts = path.relative_to(source).parts
    if any(part in SKIP_DIR_NAMES for part in rel_parts):
        return True
    name = path.name
    return name.endswith(".pyc") or name == ".DS_Store"


def install_skill(source: Path, target: Path, force: bool) -> Path:
    if not source.is_dir():
        raise SystemExit(f"INSTALL_SOURCE_MISSING: {source}")
    skill_file = source / "SKILL.md"
    if not skill_file.is_file():
        raise SystemExit(f"INSTALL_SOURCE_INVALID: SKILL.md is missing from {source}")
    if target.exists():
        if target.is_file():
            raise SystemExit(f"INSTALL_TARGET_INVALID: {target} is a file")
        occupied = any(target.iterdir())
        if occupied and not force:
            raise SystemExit(
                "INSTALL_TARGET_EXISTS: destination is not empty; pass --force to replace files"
            )
    else:
        target.mkdir(parents=True, exist_ok=True)

    copied = 0
    for item in source.rglob("*"):
        if not item.is_file() or should_skip(item, source):
            continue
        dest = target / item.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
        copied += 1
    if copied == 0:
        raise SystemExit("INSTALL_SOURCE_EMPTY: no skill files were copied")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install agent-swarm into an explicit skill directory."
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Destination directory. The installer never guesses a host path.",
    )
    parser.add_argument(
        "--source",
        help="Skill directory containing SKILL.md. Defaults to the parent of this script.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace files in an existing destination.",
    )
    args = parser.parse_args(argv)
    source = skill_source(args.source)
    target = Path(args.target).expanduser()
    if not target.is_absolute():
        target = Path.cwd() / target
    installed = install_skill(source, target.resolve(), args.force)
    print(f"Installed agent-swarm to {installed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
