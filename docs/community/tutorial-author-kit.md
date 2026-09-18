# Independent Flow tutorial author kit

Flow needs third-party explanations, not more first-party claims. This page exists to make independent tutorials easy to write without requiring an author to reverse-engineer the language.

## What counts

A tutorial is independent when the author is not presenting it as official Flow documentation and publishes it under their own identity, site, channel, repository, newsletter, blog, or community account.

Independent does not mean unverified. Authors should link to the exact Flow version they used and include commands readers can reproduce.

## Recommended tutorial shape

A useful first tutorial can be short:

1. What Flow is.
2. Installation.
3. Hello World.
4. Variables and functions.
5. One conventional algorithm.
6. One example that demonstrates Flow's evolution model.
7. What surprised the author.
8. What did not work or still feels experimental.
9. Exact Flow version and platform.
10. Links to source and reproduction commands.

Critical or mixed tutorials are welcome. Independent coverage is valuable because it gives potential users information that does not come from the project itself.

## Reproduction block

Authors can start with:

```bash
brew tap flooooooooooow/flow
brew install flow
flow version

git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow run examples/basics/fibonacci.flow
./flow gfx examples/morphogenesis/gray_scott.flow
```

For a tutorial tied to a release, check out that release tag and report it explicitly.

## Suggested article ideas

- "I learned Flow in an hour: what is actually different?"
- "Flow versus C for a small numerical program"
- "Writing a dynamical system directly in Flow"
- "Building a tiny DSP program in Flow"
- "Trying Flow as a C/C++ programmer"
- "Trying Flow as a Python scientific-computing user"
- "What Flow's self-hosted compiler actually supports"
- "Flow's evolution syntax versus a hand-written integration loop"
- "A weekend project in Flow"
- "Where Flow 1.x still feels experimental"

## Verification

Every code sample with a `main` function should be run before publication:

```bash
./flow run path/to/sample.flow
```

Formatting can be normalized with:

```bash
./flow fmt path/to/sample.flow
```

For repository examples, consult `examples/STATUS.md` rather than assuming every experimental surface has identical host support.

## Disclosure

If the Flow project helped debug code or reviewed a draft, say so. Do not present project-written copy as independent reporting.

If an AI assistant was heavily used, authors should disclose that according to the norms of the publication or community they are using.

## Getting listed

Open a pull request adding the tutorial to a `Community tutorials` section in this page with the title, author, publication date, URL, Flow version, and platform tested.

The project should list qualifying independent tutorials regardless of whether they are positive, negative, or mixed, as long as they are technically substantive and not spam.

## Community tutorials

No qualifying third-party tutorials have been submitted here yet.
