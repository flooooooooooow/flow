# Discord webhook strategy

Flow's CI and release pipelines notify the Flow Discord server. This document
is the single source of truth for how that works.

## Channels

| Channel | Purpose | Webhook | GitHub secret |
|---|---|---|---|
| `#announcements` | Releases and docs deploys | `release-notifier` | `DISCORD_RELEASE_WEBHOOK` |
| `#ci-releases` | Per-run CI status | `ci-releases` | `DISCORD_CI_WEBHOOK` |

The webhooks themselves are created in the Discord server under each channel's
channel settings. Only the server owner/`MANAGE_WEBHOOKS` role can create or
rotate them.

## The notify action

All payloads use one composite action so the embed shape lives in one place:

- `.github/actions/discord-notify/action.yml`

Every sending workflow just calls it. If the embed format ever changes, edit
that one file.

```yaml
- uses: ./.github/actions/discord-notify
  with:
    webhook: ${{ secrets.DISCORD_RELEASE_WEBHOOK }}
    title: Flow v0.9.0 released
    color: '5763719'
    url: https://github.com/OWNER/flow/releases/tag/v0.9.0
```

## Add a new notification

1. Pick a channel. If it does not exist yet, create it and a webhook for it.
2. Put the webhook URL in a GitHub secret (Settings -> Secrets).
   `gh secret set <NAME> --body "<url>"`
3. Add a `discord-notify` step to the workflow. Use `if: always()` and guard
   on the secret being set so the step is skipped when the secret is absent.

## Workflows wired

| Workflow | Trigger | Notifies |
|---|---|---|
| `.github/workflows/release.yml` | tag created | `#announcements` release |
| `.github/workflows/ci.yml` | push, PR, nightly | `#ci-releases` pass/fail |
| `.github/workflows/wiki.yml` | docs deploy | `#announcements` docs |

## Rotating a secret

1. Delete the webhook from the Discord channel settings and create a fresh one.
2. `gh secret set DISCORD_RELEASE_WEBHOOK --body "<new url>"`
3. Confirm with `gh secret list`.