# GitHub Linguist — Flow language submission

Goal: teach [github-linguist/linguist](https://github.com/github-linguist/linguist)
about **Flow** (`.flow`, `source.flow`) so GitHub’s language bar / highlighting
stop treating this repo as “mostly Python”.

## Honest status (2026-09-18)

| Check | Result |
|-------|--------|
| `.flow` free in `languages.yml`? | Yes (not listed) |
| Grammar (MIT TextMate)? | Yes — publish as `flooooooooooow/flow-tmLanguage` |
| Real-world samples? | Ready under `docs/project/linguist/samples/Flow/` |
| Popularity bar (2,000 indexed files / year for this extension class)? | **Not yet** for independently used *this* Flow |
| Collision with JavaScript Flow libdefs? | Yes — many `*.js.flow` files match `extension:flow` |
| Collision with Area9 Flow? | Yes — Area9 Flow uses plain `.flow` files with different syntax |
| `.flow` currently assigned in Linguist? | No |

`extension:flow` on GitHub is not evidence for this language by itself. A search on 2026-09-18 returned about 138,752 files, with top results dominated by JavaScript Flow libdefs such as `foo.js.flow`; Area9's established Flow language also uses ordinary `.flow` files.

Distinctive searches show the real adoption problem. `"function main() ->"` returned 1,716 files after excluding the `flooooooooooow` organization, but all visible results were under the project maintainer's own account; excluding that account as well returned zero. `"evolves as"` returned one file outside the organization, also under the maintainer's account. These figures must be re-run before any upstream submission.

Any Linguist proposal therefore needs both independent-usage evidence and a collision strategy. Do not treat unrelated `.flow`, Area9 Flow, or JavaScript Flow libdefs as adoption of this language.

## Decision (2026-08-05): wait, prepare, then one PR

Linguist closes PRs below the usage threshold: for a shared extension, at
least 2,000 indexed files in the last year, excluding forks, with spread
across unrelated users; results dominated by the owner org are filtered out.
Flow does not clear that bar yet, so no PR now.

While usage grows, keep ready in `docs/project/linguist/`:

1. Two or more representative, licensed Flow samples.
2. Representative `.js.flow` JavaScript libdefs as the competing corpus.
3. Representative Area9 Flow samples as a second plain-`.flow` corpus.
4. Heuristic rules keyed to stable syntax (`function ... ->`, `let mut`, `evolves as`) rather than repository paths or owner names.
5. A local cross-validation breakdown showing Flow, Area9 Flow, and JavaScript Flow libdefs do not steal one another's files.
6. Agreement with Linguist maintainers on naming and how the Area9 collision should be represented before opening a PR.

Do not assume the Linguist display name can simply be **Flow**. There is no current `Flow` entry or `.flow` extension in `languages.yml`, but Area9 already has an established language named Flow outside Linguist. Resolve the naming question in the existing Linguist discussion before proposing an entry.

When owner-filtered searches clear the current 2,000-file rule with real repository diversity, open a PR only after the collision plan is accepted.

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

The previous two-way heuristic is insufficient because Area9 Flow also owns plain `.flow` in the wild. A safe upstream rule cannot map unmatched `.flow` files to this Flow by default. The distinctive signatures for this language are:

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
[`samples/Flow/`](linguist/samples/Flow/).

## PR checklist (fill when opening)

See [`PR_TEMPLATE.md`](linguist/PR_TEMPLATE.md).

## Local repo until upstream lands

`.gitattributes` already has `*.flow linguist-detectable=true`. That only helps
*after* Linguist knows the language name; it cannot invent “Flow” on GitHub.com
by itself.
