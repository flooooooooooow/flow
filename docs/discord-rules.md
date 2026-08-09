# Discord server rules and channel guide

Flow's community Discord lives at `https://discord.gg/YK7VaHy24T`. It is
moderated lightly; the server is primarily a place to watch CI, ask for help,
and see releases land. This page states the rules, what each channel is for,
and where the important links live. The webhook mechanics are documented
separately in [discord-webhooks.md](discord-webhooks.md).

## Rules

1. Be civil. Disagreement about design is normal; personal attacks are not.
2. Help threads stay Help. If you open a question there, keep the thread alive
   until it is answered or closed.
3. No spam, no self-promotion outside `#showcase`.
4. Do not paste secrets, keys, or auth tokens. A webhook URL is a secret and
   grants write access to the channel it belongs to.
5. Public output differs from the sandbox. Flow compiles and runs arbitrary
   code; never paste a program that touches your filesystem into this server
   unless you have read it and understand it.
6. Unsolved compiler defects belong in GitHub issues, with the smallest
   reproducer you can make.
7. Bots may only post through the documented webhook strategy. If a bot
   double-posts, fix the sender, do not add another bot.

## Channels

| Channel | Purpose |
|---|---|
| `#welcome` | One post. Start here, read the rules, pick up important links. |
| `#announcements` | Release announcements and docs deploys. Read-only for everyone but bots. |
| `#changelog` | Machine-posted release changelog notes. Read-only. |
| `#ci-releases` | Live CI status and PR activity. High-traffic, intended to skim. |
| `#projects` | Forum: one thread per release or milestone announcement. |
| `#help` | Ask questions, paste compiler output, get unblocked. |
| `#showcase` | Show off programs, doodles, and experiments made with Flow. |

## Important links

| Thing | Where |
|---|---|
| Website and docs | https://flooooooooooow.github.io/flow/ |
| Changelog | https://flooooooooooow.github.io/flow/project/CHANGELOG.md |
| Releases | https://github.com/flooooooooooow/flow/releases |
| Issues | https://github.com/flooooooooooow/flow/issues |
| Source | https://github.com/flooooooooooow/flow |
| Homebrew | `brew install flow` |

## What lands where

- **Releases** announce in `#announcements`, post the changelog in
  `#changelog`, and open a thread in `#projects`.
- **CI runs** report to `#ci-releases`. PRs post lifecycle notices there
  too, so opening a PR produces one message.
- **Docs deploys** ping `#announcements` with a link to what changed.

A new post belongs in exactly one channel. If a notification lands twice,
one of the senders is posting to the wrong channel and should be fixed
rather than duplicated.

## Rotating webhooks

Deleting a webhook and creating a fresh one is the only way to invalidate a
leaked URL. Steps in [discord-webhooks.md](discord-webhooks.md).

## Fixing a broken notification

Check the warning in `docs/discord-webhooks.md` first, then the workflow
that posted it. Each workflow names its target channel in its header comment.