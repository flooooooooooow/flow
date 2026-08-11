"""Pure welcome-message logic, kept separate from the discord client so it
can be tested without the discord.py dependency.

Templates are format strings that may use {user} (the joining member's
mention) and {guild} (the server name).
"""

from __future__ import annotations

import json
import random
from pathlib import Path


def load_messages(path: Path) -> list[str]:
    """Load welcome templates from a messages.json file.

    Raises FileNotFoundError if the file is missing and ValueError if it has
    no usable entries.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    templates = data.get("messages", [])
    if not templates:
        raise ValueError(f"{path} contains no 'messages' entries")
    return templates


def pick_welcome(
    member_name: str,
    guild_name: str,
    templates: list[str],
    rng: random.Random | None = None,
) -> str:
    """Pick a random template and substitute {user} and {guild}.

    Accepts an optional rng for deterministic tests.
    """
    chooser = rng or random
    template = chooser.choice(templates)
    return template.format(user=member_name, guild=guild_name)
