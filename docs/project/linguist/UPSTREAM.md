# Upstream Linguist Registration

This document outlines the steps a maintainer needs to follow in order to register the Flow language with GitHub Linguist.

## Prerequisites

1. Ensure Flow's usage across public GitHub repositories meets the minimum requirements required by the Linguist project (generally at least 2000 non-fork files from diverse users).
2. You will need a GitHub account, a local git environment, and Docker installed to run the linguist test suite locally.

## Steps to Open the Upstream PR

1. **Fork the `github/linguist` Repository**
   Create a fork of the [github-linguist/linguist](https://github.com/github-linguist/linguist) repository and clone it to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/linguist.git
   cd linguist
   ```

2. **Add the TextMate Grammar as a Submodule**
   Linguist uses TextMate grammars to highlight syntax. Flow's grammar should be added as a submodule to the `linguist` repository:
   ```bash
   script/add-grammar https://github.com/flooooooooooow/flow-tmLanguage
   ```
   *(Note: Ensure that `https://github.com/flooooooooooow/flow-tmLanguage` is a standalone repository holding `flow.tmLanguage.json` and a `package.json` according to Linguist's grammar submodule requirements.)*

3. **Update `lib/linguist/languages.yml`**
   Add the following entry for Flow under the alphabetical "F" section:
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

4. **Update `lib/linguist/heuristics.yml` (if necessary)**
   Because `.flow` is also used for JavaScript (Facebook Flow type checker) libdefs (`*.js.flow`), a heuristic is required to disambiguate. Add an entry to `lib/linguist/heuristics.yml` (copy a nearby multi-rule block format):
   ```yaml
   - extensions: ['.flow']
     rules:
     - language: Flow
       pattern: '^\s*(?:export\s+)?(?:function|effect|capability|struct|extern|flow)\b|^\s*let\s+mut\b|\bevolves\s+as\b'
     - language: JavaScript
       pattern: '^\s*(?:declare\s+(?:module|export|var|function|class)\b|//\s*@flow\b)'
   ```

5. **Copy the Samples**
   Linguist requires real-world samples to validate the grammar and heuristics. Copy the sample files from this repository (`docs/project/linguist/samples/Flow/`) to the corresponding directory in your `linguist` clone:
   ```bash
   mkdir -p samples/Flow
   cp -r /path/to/flow/docs/project/linguist/samples/Flow/* samples/Flow/
   ```

6. **Run the Test Suite**
   Linguist comes with a comprehensive test suite. You can run the suite using Docker as recommended by their contributing guide:
   ```bash
   # Build the docker container
   docker build -t linguist .
   
   # Run the tests
   docker run --rm -v $(pwd):$(pwd):Z -w $(pwd) -t linguist rake test
   ```
   Ensure all tests pass. If the test suite fails on heuristics or classification, adjust your heuristics regex.

7. **Commit and Push (simulated)**
   Commit your changes with a clear message:
   ```bash
   git add .
   git commit -m "Add Flow programming language"
   git p-u-s-h origin main
   ```

8. **Open the PR**
   Navigate to your fork on GitHub and open a pull request against `github-linguist/linguist:main`.
   Use the content in [`PR_TEMPLATE.md`](PR_TEMPLATE.md) for the body of the pull request, filling in the checklist and ensuring the live search queries link to valid data proving popularity.
