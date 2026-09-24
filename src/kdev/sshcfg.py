"""Manage the kdev block in ~/.ssh/config.

Marker-delimited rewrite rather than parsing Host stanzas: the old
launch_kaggle.py approach of scanning for the next `Host ` line silently ate
the final stanza in the file whenever ours was last.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from . import cloudflared

BEGIN = "# >>> kdev >>>"
END = "# <<< kdev <<<"
BLOCK_RE = re.compile(rf"\n?{re.escape(BEGIN)}.*?{re.escape(END)}\n?", re.DOTALL)

SSH_CONFIG = Path.home() / ".ssh" / "config"


def render_block(
    alias: str, hostname: str, user: str = "root", cloudflared_path: Path | None = None
) -> str:
    proxy = cloudflared.proxy_command(cloudflared_path)
    return (
        f"{BEGIN}\n"
        f"Host {alias}\n"
        f"    HostName {hostname}\n"
        f"    User {user}\n"
        f"    ProxyCommand {proxy}\n"
        # Every session is a new container with a new host key, so a key
        # remembered by one machine is wrong on the next box another machine
        # starts: VS Code and `ssh kaggle` there fail until someone resets it.
        # Only a box holding the workspace's tunnel credentials can answer on
        # this hostname, and whoever holds those can already edit the
        # notebook that builds the box, so a pinned key protects nothing.
        f"    UserKnownHostsFile {os.devnull}\n"
        f"    StrictHostKeyChecking no\n"
        f"    LogLevel ERROR\n"
        f"    ServerAliveInterval 30\n"
        f"    ServerAliveCountMax 10\n"
        # For `ssh kaggle htop`. kdev's own background ssh calls pass -T: a tty
        # there puts this terminal in raw mode and smears the live board.
        f"    RequestTTY yes\n"
        f"{END}\n"
    )


def write(
    alias: str, hostname: str, user: str = "root", cloudflared_path: Path | None = None
) -> Path:
    SSH_CONFIG.parent.mkdir(mode=0o700, exist_ok=True)
    existing = SSH_CONFIG.read_text() if SSH_CONFIG.exists() else ""
    stripped = BLOCK_RE.sub("\n", existing).strip()
    body = (stripped + "\n\n" if stripped else "") + render_block(
        alias, hostname, user, cloudflared_path
    )
    SSH_CONFIG.write_text(body)
    SSH_CONFIG.chmod(0o600)
    return SSH_CONFIG


def has_block() -> bool:
    """Whether ~/.ssh/config currently points the alias at a session."""
    return SSH_CONFIG.exists() and BEGIN in SSH_CONFIG.read_text()


def clear() -> None:
    if SSH_CONFIG.exists():
        SSH_CONFIG.write_text(BLOCK_RE.sub("\n", SSH_CONFIG.read_text()).strip() + "\n")
