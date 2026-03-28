"""Git hook installation and management."""
from __future__ import annotations

import stat
from pathlib import Path

POST_COMMIT_HOOK = """\
#!/bin/sh
# AKUP evidence auto-capture — do not edit this block
# Records evidence for each commit automatically
akup record --auto 2>/dev/null || true
"""

HOOK_MARKER = "# AKUP evidence auto-capture"


def hooks_dir(repo: Path) -> Path:
    return repo / ".git" / "hooks"


def post_commit_path(repo: Path) -> Path:
    return hooks_dir(repo) / "post-commit"


def is_hook_installed(repo: Path) -> bool:
    hook = post_commit_path(repo)
    if not hook.exists():
        return False
    return HOOK_MARKER in hook.read_text()


def install_hook(repo: Path) -> Path:
    hook = post_commit_path(repo)
    hook.parent.mkdir(parents=True, exist_ok=True)

    if hook.exists():
        content = hook.read_text()
        if HOOK_MARKER in content:
            return hook  # already installed
        # Append to existing hook
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + POST_COMMIT_HOOK
        hook.write_text(content)
    else:
        hook.write_text(POST_COMMIT_HOOK)

    # Make executable
    hook.chmod(hook.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return hook


def uninstall_hook(repo: Path) -> bool:
    hook = post_commit_path(repo)
    if not hook.exists():
        return False

    content = hook.read_text()
    if HOOK_MARKER not in content:
        return False

    # Remove the AKUP block
    lines = content.split("\n")
    new_lines: list[str] = []
    skip = False
    for line in lines:
        if HOOK_MARKER in line:
            skip = True
            continue
        if skip and (line.startswith("#") or line.startswith("akup ") or line == ""):
            continue
        skip = False
        new_lines.append(line)

    remaining = "\n".join(new_lines).strip()
    if remaining and remaining != "#!/bin/sh":
        hook.write_text(remaining + "\n")
    else:
        hook.unlink()
    return True
