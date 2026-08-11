"""Flow Discord welcome bot.

Greets every new member who joins the Flow Discord server with a rotating
message posted to the configured welcome channel. Reads its token and welcome
channel id from environment variables (see .env.example).

Run:
    python3 bot.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import discord

from welcome import load_messages, pick_welcome

LOG = logging.getLogger("discord-welcome")

HERE = Path(__file__).resolve().parent
MESSAGES_FILE = HERE / "messages.json"


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        LOG.error("Missing required env var %s", name)
        sys.exit(1)
    return value


class WelcomeBot(discord.Client):
    def __init__(self, welcome_channel_id: int, messages: list[str]) -> None:
        intents = discord.Intents.default()
        intents.members = True  # privileged, must be enabled in the dev portal
        super().__init__(intents=intents)
        self.welcome_channel_id = welcome_channel_id
        self.messages = messages

    async def on_ready(self) -> None:
        LOG.info("Logged in as %s (id=%s)", self.user, self.user.id)
        LOG.info("Watching guilds: %s", [g.name for g in self.guilds])
        LOG.info("Welcome channel id: %s", self.welcome_channel_id)

    async def on_member_join(self, member: discord.Member) -> None:
        channel = self.get_channel(self.welcome_channel_id)
        if channel is None:
            LOG.warning(
                "Welcome channel %s not visible to the bot; skipping greet for %s",
                self.welcome_channel_id,
                member,
            )
            return
        text = pick_welcome(
            member_name=member.mention,
            guild_name=member.guild.name,
            templates=self.messages,
        )
        try:
            await channel.send(text)
        except discord.DiscordException as exc:
            LOG.error("Failed to send welcome message for %s: %s", member, exc)
        else:
            LOG.info("Welcomed %s in %s", member, member.guild.name)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    token = _required_env("DISCORD_TOKEN")
    channel_id_raw = _required_env("WELCOME_CHANNEL_ID")
    try:
        channel_id = int(channel_id_raw)
    except ValueError:
        LOG.error("WELCOME_CHANNEL_ID must be an integer, got %r", channel_id_raw)
        sys.exit(1)

    messages = load_messages(MESSAGES_FILE)
    client = WelcomeBot(welcome_channel_id=channel_id, messages=messages)

    try:
        client.run(token, log_handler=None)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
