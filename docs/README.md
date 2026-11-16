# Flow documentation

Flow's documentation is organised by task. Start with one path below; use the language specification when you need precise syntax or a statement of supported behaviour.

This index is a guide to the documentation, **not** a competing language specification or a list of release promises.

## Choose your path

| Your goal | Start here | Then continue with |
| --- | --- | --- |
| Learn programming with Flow | [Start here](start-here.md) | [The Flow Book](book/README.md) |
| Install Flow and run a native program | [Getting started](getting-started.md) | [Development and CLI](DEVELOPMENT.md) |
| Learn the language systematically | [The Flow Book](book/README.md) | [Tutorial tracks](tutorials/README.md) |
| Try Flow before installing anything | [Browser playground](playground/index.html) | [Interactive tutorials](https://flooooooooooow.github.io/flow/tutorials/) |
| Run a compiled example in the browser | [Live WebAssembly gallery](https://flooooooooooow.github.io/flow/wasm/index.html) | [WebAssembly target guide](language/wasm.md) |
| Look up a language rule | [Language reference index](language/spec-index.md) | [Full language specification](LANGUAGE_SPEC.md) |
| Find a standard-library function | [Standard-library reference](library/stdlib-reference.md) | [Generated API signatures](library/stdlib-api.md) |
| Build graphics or simulations | [Graphics](language/graphics.md) and [dynamics](language/dynamics-dsl.md) | [Demo showcase](demos/overview.md) |
| Use Flow from another language | [FFI buffer ABI](language/ffi-buffer.md) | [Export ABI](language/export-abi.md) |
| Contribute to the compiler or docs | [Development](DEVELOPMENT.md) | [Contribution guide](project/CONTRIBUTING.md) |

## Live examples: three different execution environments

The browser experiences are useful, but they do **not** all execute the same engine. The distinction matters when investigating a parser, numerical, graphics, or backend issue.

| Experience | What it runs | Use it for |
| --- | --- | --- |
| [Playground](playground/index.html) | A **browser-side Flow interpreter and syntax explorer** supporting a subset of native Flow | Exploring syntax, experimenting with examples and inspecting available representations |
| [Interactive tutorials](https://flooooooooooow.github.io/flow/tutorials/) | An in-browser lesson runner; individual lessons may have target-specific limitations | Guided experiments and practising concepts |
| [Live WebAssembly gallery](https://flooooooooooow.github.io/flow/wasm/index.html) | Flow programs **precompiled** to WebAssembly | Running and comparing the published, browser-compatible demos |
| Native Flow | Flow's self-hosted compiler and the selected C or MLIR toolchain | Authoritative compilation, cross-target investigation and full regression tests |

**A browser interpreter result is not proof that the native compiler accepts the same program.** A compiled WASM demo is likewise not an in-browser Flow compiler. If behaviour differs, record the specific target and reproduce it with the native CLI before reporting a language regression. See the [WASM target guide](language/wasm.md) and [language specification](LANGUAGE_SPEC.md) for the relevant boundaries.

## Learn, reference, and explore

### Learn

[Start here](start-here.md) is the shortest first-run walkthrough. [Getting started](getting-started.md) focuses on installing and running Flow. [The Flow Book](book/README.md) is the ordered curriculum. [Interactive and written tutorials](tutorials/README.md) provide short, focused exercises after that.

Do not treat the book, tutorials and specification as parallel authorities: the book teaches, tutorials exercise, and the specification defines.

### Reference

Use [the focused language reference](language/README.md) to browse by feature, [the specification index](language/spec-index.md) to find the canonical section, and [the formal grammar](grammar.ebnf) when syntax details matter. [The standard-library reference](library/stdlib-reference.md) is the human-oriented entry point; [generated API documentation](library/stdlib-api.md) is the signature-level index.

For runtime and performance-sensitive work, continue with [memory management](library/memory.md), [real-time safety](library/rt-safety.md), [C SIMD lowering](language/c-simd-loops.md) and [debugging](language/debugging.md).

### Explore examples

The [demo showcase](demos/overview.md) is a curated directory of graphics, games, numerical methods, audio and simulations, not a promise that every demo runs on every target. Each collection distinguishes live browser output, recorded output and source where possible. The [WASM gallery](https://flooooooooooow.github.io/flow/wasm/index.html) is the entry point for browser-executable compiled programs.

## Documentation status and authority

Flow evolves quickly. Pages describing proposed designs, research, roadmaps or experimental features should not be interpreted as evidence of shipping compiler behaviour.

| Question | Authoritative source |
| --- | --- |
| Supported syntax and semantics | [Full specification](LANGUAGE_SPEC.md), tests and compiler behaviour |
| Implemented language features | [Language reference](language/README.md) and tests |
| Recent shipped changes | [Changelog](project/CHANGELOG.md) |
| Planned language work | [Roadmap](../ROADMAP.md) and linked GitHub issues |
| Open design questions | [Questions](project/Questions.md) |
| Release and compatibility commitments | [Stability policy](../STABILITY.md) |
| Source and contribution rules | [Contributing](project/CONTRIBUTING.md) and [repository structure](project/repository-structure.md) |

## Maintaining the documentation

The custom documentation site is generated from content in this directory and the shell in the repository's site directory. **[docs/nav.json](nav.json) is the canonical sidebar and content map**; the demo navigation portions are generated from the demo catalog. Edit source material rather than generated site output.

After changing documentation, verify the generated website, internal links and any relevant live example interactions with the repository's documented toolchain:

    ./flow tool build_wiki
    ./flow tool wiki_links
    node scripts/check_live_demos.mjs --wiki build/wiki

For playground, tutorial, or browser-runner changes, also run the documentation-specific Chromium checks where available; the GitHub Actions live-demos workflow supplies browser-level coverage. Report whether the verification was run locally or in CI, and never describe an untested example as working.

Broken examples and misleading pages should be reported through [GitHub issues](https://github.com/flooooooooooow/flow/issues) with the URL, target, reproduction steps and actual output. Documentation changes should link to a working example or a verification step whenever they make an executable claim.
