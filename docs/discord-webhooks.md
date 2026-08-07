# Discord webhook strategy

Flow's CI and release pipelines notify the Flow Discord server. Join at
`https://discord.gg/YK7VaHy24T` (points to `#welcome`, never expires).
This document is the single source of truth for how webhooks work.

## Channels

| Channel | Purpose | Webhook | GitHub secret |
|---|---|---|---|
| `#announcements` | Releases and docs deploys | `release-notifier` | `DISCORD_RELEASE_WEBHOOK` |
| `#ci-releases` | Per-run CI status | `ci-releases` | `DISCORD_CI_WEBHOOK` |
| `#changelog` | Release changelog notes | `flow-changelog` | `DISCORD_CHANGELOG_WEBHOOK` |

Server categories: `engagement` (welcome, announcements, introductions,
showcase), `help`, `dev` (tooling, contribute, ci-releases), `projects`
(project-showcase, project-work), `changelog`.

The webhooks themselves are created in the Discord server under each channel's
channel settings. Only the server owner/`MANAGE_WEBHOOKS` role can create or
rotate them.

## The notify action

All payloads use one composite action so the embed shape lives in one place:

- `.github/actions/discord-notify/action.yml`

Every sending workflow just calls it. If the embed format ever changes, edit
that one file. The action builds the payload with a small Python builder
instead of string concatenation, so multi-line descriptions and embedded
quotes survive intact. It supports the full Discord embed schema.

```yaml
- uses: ./.github/actions/discord-notify
  with:
    webhook: ${{ secrets.DISCORD_RELEASE_WEBHOOK }}
    botname: Flow Release Bot
    avatar_url: ${{ github.server_url }}/${{ github.repository_owner }}.png
    title: Flow v0.9.0 released
    url: https://github.com/OWNER/flow/releases/tag/v0.9.0
    color: '5763719'
    description: Release published for commit ...
    author_name: Flow
    author_icon: ${{ github.server_url }}/${{ github.repository_owner }}.png
    fields: >-
      [{"name":"Version","value":"v0.9.0","inline":true}]
    footer_text: Flow Releases · v0.9.0
```

### Inputs

| Input | Description |
|---|---|
| `webhook` | Webhook URL. Empty skips the step. |
| `content` | Top-level message above the embed (markdown, role pings via `<@&id>`). |
| `botname` | Webhook username override. Default `Flow Bot`. |
| `avatar_url` | Webhook avatar image URL. |
| `title` / `url` | Embed title and its link. |
| `color` | Embed color as decimal. Green `3066993`, red `15158332`, amber `14440101`, purple `5763719`, default `0`. |
| `description` | Embed description (Discord markdown, multi-line). |
| `fields` | JSON array of up to 4 field objects: `[{"name","value","inline"}]`. |
| `author_name` / `author_icon` | Embed author line. |
| `thumbnail` / `image` | Right-top thumbnail and bottom large image URLs. |
| `footer_text` / `footer_icon` | Bottom footer line. |
| `timestamp` | ISO8601 time; defaults to now. |

The org avatar URL pattern `https://github.com/<owner>.png` is used as the
webhook/author/footer icon across all three workflows.

## Add a new notification

1. Pick a channel. If it does not exist yet, create it and a webhook for it.
2. Put the webhook URL in a GitHub secret (Settings -> Secrets).
   `gh secret set <NAME> --body "<url>"`
3. Add a `discord-notify` step to the workflow. Use `if: always()` and guard
   on the secret being set so the step is skipped when the secret is absent.

## Workflows wired

| Workflow | Trigger | Notifies |
|---|---|---|
| `.github/workflows/release.yml` | tag created | `#announcements` release, `#changelog` notes |
| `.github/workflows/ci.yml` | push, PR, nightly | `#ci-releases` pass/fail |
| `.github/workflows/wiki.yml` | docs deploy | `#announcements` docs |

`flowc-release.yml` publishes compiler binaries but does not notify Discord yet.

## Rotating a secret

1. Delete the webhook from the Discord channel settings and create a fresh one.
2. `gh secret set DISCORD_RELEASE_WEBHOOK --body "<new url>"`
3. Confirm with `gh secret list`.