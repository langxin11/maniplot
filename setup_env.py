#!/usr/bin/env python3
"""Cross-platform (Windows & Linux & macOS) one-click installer for maniplot & AI Agent Skill."""

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
SKILL_DST = Path.home() / ".gemini" / "config" / "skills" / "maniplot"


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


def install_global_skill() -> None:
    """Link or copy `skills/maniplot` into `~/.gemini/config/skills/maniplot` across Windows & Linux."""
    SKILL_DST.parent.mkdir(parents=True, exist_ok=True)

    if SKILL_DST.is_symlink() or SKILL_DST.exists():
        if SKILL_DST.is_symlink() or SKILL_DST.is_file():
            SKILL_DST.unlink()
        else:
            # On Windows, a directory junction can be unlinked with os.rmdir; normal dir with rmtree
            try:
                os.rmdir(SKILL_DST)
            except OSError:
                shutil.rmtree(SKILL_DST)

    # 1. Try native symlink (Linux / macOS / Windows with Developer Mode)
    try:
        os.symlink(SKILL_SRC, SKILL_DST, target_is_directory=True)
        print(f"[OK] Symlinked global Agent Skill: {SKILL_DST} -> {SKILL_SRC}")
        return
    except OSError:
        pass

    # 2. On Windows without admin/Developer Mode, use NTFS Directory Junction (`mklink /J`)
    if platform.system().lower().startswith("win"):
        res = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(SKILL_DST), str(SKILL_SRC)],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            print(f"[OK] Created Windows Directory Junction for Agent Skill: {SKILL_DST} -> {SKILL_SRC}")
            return

    # 3. Fallback: copy directory tree
    shutil.copytree(SKILL_SRC, SKILL_DST)
    print(f"[OK] Copied global Agent Skill to: {SKILL_DST}")


if __name__ == "__main__":
    print(f"=== Setting up maniplot on {platform.system()} ({sys.executable}) ===")
    register_python_pth()
    install_global_skill()
    print("=== Setup complete! You can now `import maniplot as mplt` in any project. ===")
