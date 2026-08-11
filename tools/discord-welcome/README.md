# Flow Discord welcome bot

A small bot that greets every new member who joins the Flow Discord server.
Picks one of a rotating set of welcome messages from `messages.json` and posts
it to the `#welcome` channel, mentioning the joining user.

The Flow Discord server already uses webhooks for CI and release notifications
(see `docs/discord-webhooks.md`). Those webhooks are outbound only. Greeting a
joining member by name needs an inbound event, which is why this bot exists.

## What it does

- Listens to the `guildMemberAdd` event via the privileged `GUILD_MEMBERS`
  intent.
- On each join, picks a random template from `messages.json`, substitutes
  `{user}` with the member's mention and `{guild}` with the server name, and
  posts it to the configured welcome channel.
- Logs every greet and every failure.

## Files

| File | Purpose |
|------|---------|
| `bot.py` | The bot itself. |
| `messages.json` | Welcome message templates. Edit to change the copy. |
| `requirements.txt` | Pins `discord.py`. |
| `.env.example` | Template for the env file the bot reads. |
| `systemd/discord-welcome.service` | systemd unit for the VPS host. |

## Create the bot account

1. Go to the Discord Developer Portal -> Applications -> New Application.
   Name it something like `Flow Welcome`.
2. Open the application -> Bot -> Reset Token. Copy the token. This is the
   only time Discord shows it.
3. Under Bot -> Privileged Gateway Intents, enable **Server Members Intent**.
   The bot will not receive `on_member_join` without it.
4. Open OAuth2 -> URL Generator. Select scopes `bot`. Select bot permissions
   `View Channels` and `Send Messages`. Open the generated URL and invite the
   bot to the Flow server.

## Get the welcome channel id

In Discord, Settings -> Advanced -> Developer Mode on. Right-click the
`#welcome` channel -> Copy ID. This is `WELCOME_CHANNEL_ID`.

## Run locally

```bash
cd tools/discord-welcome
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in DISCORD_TOKEN and WELCOME_CHANNEL_ID
python3 bot.py
```

The bot logs `Logged in as ...` and `Watching guilds: [...]`. Join the server
with a test account to confirm a welcome message lands in `#welcome`.

## Host on the VPS

The systemd unit assumes the bot lives at `/opt/discord-welcome` and reads its
secrets from `/etc/discord-welcome.env`.

```bash
# on the VPS, as root
useradd --system --home /opt/discord-welcome --shell /usr/sbin/nologin discord-welcome
mkdir -p /opt/discord-welcome
chown discord-welcome:discord-welcome /opt/discord-welcome

# copy these files to /opt/discord-welcome
cd /opt/discord-welcome
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

cat > /etc/discord-welcome.env <<'EOF'
DISCORD_TOKEN=...
WELCOME_CHANNEL_ID=...
EOF
chmod 600 /etc/discord-welcome.env
chown root:discord-welcome /etc/discord-welcome.env

cp systemd/discord-welcome.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now discord-welcome
journalctl -u discord-welcome -f
```

## Edit the welcome copy

Open `messages.json`. Each entry is a template string. `{user}` becomes the
joining member's mention (renders as `@name`), `{guild}` becomes the server
name. Add, remove, or rewrite entries freely. The bot reloads the file on
restart.

## Notes

- The `GUILD_MEMBERS` intent is privileged. Discord may ask you to verify the
  bot if the server crosses 100 members. Verification is free.
- The bot only needs `View Channels` and `Send Messages`. Do not give it
  administrator. Least privilege.
- If `#welcome` is ever renamed or the bot loses access to it, the bot logs
  `Welcome channel ... not visible` and skips the greet instead of crashing.
