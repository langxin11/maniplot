#!/usr/bin/env python3
"""Cross-platform (Windows & Linux & macOS) and Multi-Agent installer for maniplot.

Automatically registers:
1. Python package path (`maniplot.pth`) across system/user/conda site-packages.
2. Global AI Agent Skill (`skills/maniplot/SKILL.md`) across ALL mainstream coding agents:
   - Google Antigravity / Gemini CLI (`~/.gemini/config/skills/maniplot`)
   - OpenAI Codex (`~/.codex/skills/maniplot`)
   - Anthropic Claude Code (`~/.claude/skills/maniplot`)
   - Universal Agent Skills Standard (`~/.agents/skills/maniplot` for Cursor / Windsurf / OpenCode)
"""

from __future__ import annotations

import os
import platform
import shutil
import site
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILL_SRC = REPO_ROOT / "skills" / "maniplot"

AGENT_SKILL_TARGETS = [
    ("Antigravity / Gemini", Path.home() / ".gemini" / "config" / "skills" / "maniplot"),
    ("OpenAI Codex", Path.home() / ".codex" / "skills" / "maniplot"),
    ("Claude Code", Path.home() / ".claude" / "skills" / "maniplot"),
    ("Universal (.agents)", Path.home() / ".agents" / "skills" / "maniplot"),
]


def register_python_pth() -> None:
    """Write maniplot.pth into site-packages so `import maniplot` works everywhere on Windows & Linux."""
    target_dirs = []
    try:
        user_site = site.getusersitepackages()
        if user_site:
            target_dirs.append(Path(user_site))
    except Exception:
        pass

    try:
        for sp in site.getsitepackages():
            target_dirs.append(Path(sp))
    except Exception:
        pass

    installed_any = False
    for sp_dir in target_dirs:
        try:
            sp_dir.mkdir(parents=True, exist_ok=True)
            pth_file = sp_dir / "maniplot.pth"
            pth_file.write_text(f"{REPO_ROOT}\n", encoding="utf-8")
            print(f"[OK] Registered Python path in: {pth_file}")
            installed_any = True
        except PermissionError:
            continue

    if not installed_any:
        print("[WARN] Could not write .pth file due to permissions. Try: pip install -e .")


def _link_or_copy_skill(agent_name: str, dst: Path) -> None:
    """Link or copy `skills/maniplot` to a target agent's global skill directory."""
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.is_symlink() or dst.exists():
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            try:
                os.rmdir(dst)
            except OSError:
                shutil.rmtree(dst)

    # 1. Try native symlink (Linux / macOS / Windows with Developer Mode)
    try:
        os.symlink(SKILL_SRC, dst, target_is_directory=True)
        print(f"[OK] [{agent_name}] Symlinked skill: {dst} -> {SKILL_SRC}")
        return
    except OSError:
        pass

    # 2. On Windows without admin/Developer Mode, use NTFS Directory Junction (`mklink /J`)
    if platform.system().lower().startswith("win"):
        res = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst), str(SKILL_SRC)],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            print(f"[OK] [{agent_name}] Created Windows Junction: {dst} -> {SKILL_SRC}")
            return

    # 3. Fallback: copy directory tree
    shutil.copytree(SKILL_SRC, dst)
    print(f"[OK] [{agent_name}] Copied skill to: {dst}")


def install_all_agent_skills() -> None:
    """Install the maniplot skill into all mainstream AI coding agent global directories."""
    for agent_name, target_path in AGENT_SKILL_TARGETS:
        _link_or_copy_skill(agent_name, target_path)


if __name__ == "__main__":
    print(f"=== Setting up maniplot on {platform.system()} ({sys.executable}) ===")
    register_python_pth()
    install_all_agent_skills()
    print("=== Setup complete! All AI Agents & Python environments are ready. ===")
