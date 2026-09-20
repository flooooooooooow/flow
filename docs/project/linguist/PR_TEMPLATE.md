<!--
Paste into a github-linguist/linguist PR (use their official template —
this file mirrors the checklist so we don't forget fields).
Do NOT open until search evidence clears the popularity bar outside flooooooooooow.
-->

## Description

Add the [Flow](https://github.com/flooooooooooow/flow) programming language
(statically typed, algebraic effects, C backend; extension `.flow`).

## Checklist

- [ ] **I am adding a new language.**
  - [ ] The extension meets Linguist's current usage requirement after excluding forks, project-owner concentration, JavaScript Flow libdefs, Area9 Flow, and other unrelated `.flow` files.
    - Search results for each extension:
      - https://github.com/search?type=code&q=NOT+is%3Afork+extension%3Aflow+%22let+mut%22
      - https://github.com/search?type=code&q=NOT+is%3Afork+extension%3Aflow+%22evolves+as%22
      - (exclude Facebook libdefs) https://github.com/search?type=code&q=NOT+is%3Afork+extension%3Aflow+NOT+%22declare+module%22+NOT+%22.js.flow%22
  - [x] I have included a real-world usage sample for all extensions added in this PR:
    - Sample source(s):
      - https://github.com/flooooooooooow/flow/blob/main/examples/effects/showcase.flow
      - https://github.com/flooooooooooow/flow/blob/main/examples/linalg/lu_decomposition.flow
      - https://github.com/flooooooooooow/flow/blob/main/examples/concurrency/channels.flow
      - https://github.com/flooooooooooow/flow/blob/main/compiler/src/lexer.flow
    - Sample license(s): MIT — https://github.com/flooooooooooow/flow/blob/main/LICENSE
  - [x] I have included a syntax highlighting grammar: https://github.com/flooooooooooow/flow-tmLanguage
  - [x] I have added a color
    - Hex value: `#5B8DEF`
    - Rationale: blue accent used in Flow documentation / branding; chosen to avoid collision with Facebook Flow’s pink branding and with nearby Linguist blues where possible.
  - [ ] I have resolved the shared-extension classification problem with maintainers.
    - `.flow` is also used by JavaScript Flow libdefs (`*.js.flow`) and Area9 Flow. The final heuristic/naming strategy must demonstrate that all three corpora classify safely.

## Notes for maintainers

- Language name **Flow** collides conceptually with both Facebook's Flow type checker and Area9 Flow. Use the name agreed in the prior Linguist discussion rather than assuming the canonical project brand can be the Linguist display name.
- Popularity: please assess with queries that exclude `*.js.flow` / `declare module` noise and, if needed, `-org:flooooooooooow` to measure third-party adoption.
