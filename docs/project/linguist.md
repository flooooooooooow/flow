# GitHub Linguist — Flow language submission

Goal: teach [github-linguist/linguist](https://github.com/github-linguist/linguist)
about **Flow** (`.flow`, `source.flow`) so GitHub’s language bar / highlighting
stop treating this repo as “mostly Python”.

## Honest status (2026-08-05)

| Check | Result |
|-------|--------|
| `.flow` free in `languages.yml`? | Yes (not listed) |
| Grammar (MIT TextMate)? | Yes — publish as `flooooooooooow/flow-tmLanguage` |
| Real-world samples? | Ready under `docs/project/linguist/samples/Flow/` |
| Popularity bar (~2000 non-fork files / year)? | **Not yet** for *this* Flow |
| Collision with Facebook Flow? | Yes — many `*.js.flow` libdefs match extension `.flow` |

`extension:flow` on GitHub is dominated by Facebook’s **Flow type checker**
libdefs (`foo.js.flow`), not this language. Any Linguist PR **must** ship a
heuristic (and samples for both sides if they keep sharing `.flow`).

Search snippets to cite (re-run before opening the PR):

```text
# This language (org)
https://github.com/search?type=code&q=org%3Aflooooooooooow+extension%3Aflow+NOT+is%3Afork

# Distinctive tokens (broader)
https://github.com/search?type=code&q=extension%3Aflow+%22let+mut%22+NOT+is%3Afork
https://github.com/search?type=code&q=extension%3Aflow+%22evolves+as%22+NOT+is%3Afork

# Noise (Facebook libdefs) — do NOT claim these as Flow-the-language
https://github.com/search?type=code&q=extension%3Aflow+%22declare+module%22+NOT+is%3Afork
```

Until the bar clears outside `flooooooooooow/*`, prefer a **Linguist Discussion**
over a full PR (PRs for hobby languages get closed / parked as pending
popularity). Keep this kit ready so `script/add-grammar` + samples are one
afternoon of work when usage is real.

**Opened:** [linguist#8101](https://github.com/github-linguist/linguist/discussions/8101)
(Classification — popularity + naming check before PR).

## Grammar repo

Published: https://github.com/flooooooooooow/flow-tmLanguage

```bash
script/add-grammar https://github.com/flooooooooooow/flow-tmLanguage
```

Expected `tm_scope`: `source.flow`.

## `languages.yml` entry (draft)

Insert alphabetically under **F**. Omit `language_id` until `script/update-ids`.

```yaml
Flow:
  type: programming
  color: "#5B8DEF"
  extensions:
  - ".flow"
  tm_scope: source.flow
  ace_mode: text
  aliases:
  - flow-lang
```

Color rationale: blue used in Flow branding / docs accents (not Facebook’s pink).
Confirm with community before arguing branding in the PR.

> **Name clash:** Linguist language names must be unique. Facebook’s checker is
> not currently a separate Linguist language (files classify as JavaScript).
> If maintainers prefer disambiguation, use **`Flow Lang`** or **`Flow (systems)`**
> with alias `flow-lang` — decide in the Discussion before opening the PR.

## Heuristic draft (`heuristics.yml`)

Disambiguate `.flow` between this language and Facebook `*.js.flow` libdefs:

```yaml
- extensions: ['.flow']
  rules:
  - language: Flow
    pattern: '^\s*(?:export\s+)?(?:function|effect|capability|struct|extern|flow)\b|^\s*let\s+mut\b|\bevolves\s+as\b'
  - language: JavaScript
    pattern: '^\s*(?:declare\s+(?:module|export|var|function|class)\b|//\s*@flow\b)'
  # default: leave unclassified / classifier — do not steal JS libdefs
```

(Exact YAML shape must match current `lib/linguist/heuristics.yml` — copy a
nearby multi-rule extension block when applying.)

## Samples

| File | Source (MIT) |
|------|----------------|
| `effects_showcase.flow` | `examples/effects/showcase.flow` |
| `lu_decomposition.flow` | `examples/linalg/lu_decomposition.flow` |
| `channels.flow` | `examples/concurrency/channels.flow` |
| `lexer.flow` | `compiler/src/lexer.flow` |

Copies with provenance headers live in
[`samples/Flow/`](samples/Flow/).

## PR checklist (fill when opening)

See [`PR_TEMPLATE.md`](PR_TEMPLATE.md).

## Local repo until upstream lands

`.gitattributes` already has `*.flow linguist-detectable=true`. That only helps
*after* Linguist knows the language name; it cannot invent “Flow” on GitHub.com
by itself.
