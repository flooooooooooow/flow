# Contributing to Flow

## Agentic Pair Programming Guidelines

Flow is developed through **human-AI collaboration**. This document defines how that works.

---

## The Collaboration Model

```
┌─────────────────────────────────────────────────────────────┐
│                      HUMAN (Abhishek)                       │
│  • Vision & Direction    • Final Authority                  │
│  • Design Decisions      • Quality Judgment                 │
│  • User Empathy          • Social Context                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Intent & Feedback
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        AI AGENT                             │
│  • Implementation        • Pattern Recognition              │
│  • Code Generation       • Consistency Checking             │
│  • Documentation         • Refactoring                      │
│  • Testing               • Research & Options               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Artifacts & Proposals
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       CODEBASE                              │
│  • Source Code           • Tests                            │
│  • Documentation         • Examples                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Decision Authority Matrix

| Domain | Human Authority | AI Role |
|--------|-----------------|---------|
| **Language Design** | Final | Propose options, explain tradeoffs |
| **Syntax Choices** | Final | Implement, ensure consistency |
| **Feature Priority** | Final | Suggest based on dependencies |
| **Architecture** | Final | Implement, identify risks |
| **Code Style** | Set standards | Enforce consistently |
| **Bug Fixes** | Approve | Identify, propose, implement |
| **Documentation** | Review | Write, maintain accuracy |
| **Examples** | Approve direction | Generate, test |
| **Refactoring** | Approve scope | Execute, verify |

### The Rule
> **Human sets the "what" and "why". AI handles the "how".**

---

## Communication Protocols

### How to Express Intent

**Good (clear intent):**
```
"Add a `match` expression that works like Rust's"
"Make the parser support ptr[0].field syntax"
"Clean up the examples directory"
```

**Better (intent + context):**
```
"Add a `match` expression like Rust's - we need this for 
the Option<T> type to be ergonomic"
```

**Best (intent + context + constraints):**
```
"Add a `match` expression like Rust's for Option<T>. 
Keep it simple - no guards or complex patterns yet. 
Should compile to C switch statements where possible."
```

### AI Response Patterns

1. **Before major changes**: State plan, get approval
2. **During implementation**: Update todos, show progress
3. **After completion**: Summarize what changed, verify it works
4. **When stuck**: Explain the blocker, propose alternatives

---

## Quality Gates

### Code Changes Must:

- [ ] Compile without errors (`./flow compile`)
- [ ] Pass existing tests (`./flow test`)
- [ ] Include new tests for new features
- [ ] Follow existing code style
- [ ] Update documentation if behavior changes
- [ ] Not break working examples

### Documentation Must:

- [ ] Be accurate to current implementation
- [ ] Include runnable examples
- [ ] Explain the "why" not just the "what"
- [ ] Stay DRY (link, don't duplicate)

### Examples Must:

- [ ] Actually compile and run
- [ ] Demonstrate one concept clearly
- [ ] Use current syntax (not deprecated patterns)

### Code Blocks in Documentation

CI compiles every ` ```flow ` block in every tracked markdown file
(`scripts/check_doc_examples.py`). A block that neither compiles nor carries a
reason is a build failure, and the unverified count can only go down.

A block does not need a `main`. The checker wraps a bare fragment in one and
records which wrapping it needed, so a two-line snippet is fine.

Four words go after `flow` on the opening fence:

| Word | Use it when |
|---|---|
| `expect-error` | The block is there to show a rejection. It must fail on meaning, so a syntax error the harness caused does not count. |
| `ignore="reason"` | The block cannot be checked. The reason is required and is read by a human. |
| `preamble=path` | The block needs declarations from a file to make sense on its own. |
| `no-harness` | The block must compile exactly as written, with no wrapping. |
| `from=path` | The block is a copy of that `.flow` file. CI fails if the two drift apart. |

An unknown word is an error rather than a silent pass, so `expect_error` fails
loudly instead of being verified as ordinary code.

Use `from=` whenever a page inlines a program and also links the real file.
Without it there are two copies and only the file is covered by the test
suite, so the page drifts: one such copy renamed a variable to `test`, which
is a keyword, while the linked file kept the name that parses.

---

## Session Workflow

### Starting a Session

1. **Context Recovery**
   - AI reads ROADMAP.md, recent changes
   - Human states current goal
   
2. **Scope Agreement**
   - Define what "done" looks like
   - Identify dependencies and risks

3. **Work Execution**
   - AI uses todos for complex tasks
   - Human reviews at checkpoints

4. **Session Close**
   - Commit working state
   - Update ROADMAP.md if needed
   - Note any open issues

### Session Types

| Type | Duration | Example |
|------|----------|---------|
| **Quick Fix** | 5-15 min | "Fix this error", "Add this test" |
| **Feature** | 30-120 min | "Add match expressions" |
| **Refactor** | 60-180 min | "Reorganize the examples" |
| **Design** | Variable | "Plan the package system" |
| **Exploration** | Variable | "What would X look like?" |

---

## Knowledge Persistence

### What AI Should Remember (via files)

| Information | Location |
|-------------|----------|
| Project vision | VISION.md / README.md |
| Current priorities | ROADMAP.md |
| Open questions | docs/project/Questions.md |
| Issue checklist | docs/project/issues-checklist.md |
| Next actions | docs/NEXT.md |
| Language rules | docs/LANGUAGE_SPEC.md |
| Code patterns | Existing codebase |
| What works | tests/, examples/ |

### Session Handoff

When ending a session, ensure:
1. All changes are committed
2. ROADMAP.md reflects current state
3. Any open issues are documented
4. Examples still compile

---

## Social Incentive Alignment

### AI Optimization Targets

**Optimize for:**
- ✅ Working code over perfect code
- ✅ Consistency with existing patterns
- ✅ Human understanding of changes
- ✅ Incremental progress
- ✅ Reversible decisions

**Avoid:**
- ❌ Over-engineering
- ❌ Adding unrequested features
- ❌ Breaking working functionality
- ❌ Massive uncommitted changes
- ❌ Assuming instead of asking

### The "Good Collaborator" Test

Before making a change, AI should ask:
1. Would a thoughtful human collaborator do this?
2. Is this what was actually requested?
3. Will this be easy to review and understand?
4. Does this respect existing design decisions?

---

## Conflict Resolution

### When AI and Human Disagree

1. **AI presents options** with tradeoffs
2. **Human decides** (may ask for more info)
3. **AI implements** the decision faithfully
4. **Learn for next time** (update guidelines if needed)

### When AI is Uncertain

```
"I see two approaches here:

Option A: [description]
  + Pro
  - Con

Option B: [description]  
  + Pro
  - Con

Which direction do you prefer?"
```

---

## Anti-Patterns to Avoid

### AI Anti-Patterns

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Huge changes without checkpoints | Incremental commits |
| Guessing requirements | Ask for clarification |
| Ignoring existing patterns | Study codebase first |
| Over-documenting trivial changes | Match importance to effort |
| Deleting without asking | Confirm before removing |

### Session Anti-Patterns

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Vague goals | Define "done" upfront |
| No verification | Test after changes |
| Context loss | Update docs continuously |
| Scope creep | Finish before expanding |

---

## Extending the Roadmap

### Adding New Items

New roadmap items should include:

```markdown
## [Feature Name]

**Goal:** One sentence description

**Why:** Why this matters for Flow

**Scope:**
- [ ] Specific deliverable 1
- [ ] Specific deliverable 2

**Dependencies:** What must exist first

**Not in scope:** Explicit exclusions
```

### Prioritization Criteria

| Factor | Weight |
|--------|--------|
| Unblocks other work | High |
| Fixes broken functionality | High |
| Improves user experience | Medium |
| Nice to have | Low |
| Speculative/experimental | Lowest |

---

## Roadmap Sync

Open items in `ROADMAP.md` mirror to GitHub issues (label `roadmap`) so the
tracker stays visible on GitHub. Two scripts handle it:

- `scripts/sync_roadmap.py` — creates a GitHub issue for every open item
  (🔲 status, `partial` status, unchecked `- [ ]` checkboxes, numbered 🔲
  items, and the curated `KNOWN_GAPS` list). When an item is marked done in
  `ROADMAP.md`, it closes the issue and checks the `docs/project/issues-checklist.md` line.
  Rewording an item updates the existing issue instead of creating a duplicate.
- `scripts/sync_issues.sh` — rounds trip state between `docs/project/issues-checklist.md`
  and GitHub (closes issues checked locally, checks items closed on GitHub).

Run it after editing `ROADMAP.md`:

```bash
make sync-roadmap-dry   # preview only
make sync-roadmap       # apply
```

Each issue body carries a `ROADMAP-SYNC: <slug>` marker that keeps the binding
stable across title edits. `docs/project/issues-checklist.md` lines use the format
`- [ ] #NNN [roadmap:<slug>] <title> <url>`.

---

## The Meta-Goal

Flow is an experiment in **human-AI collaborative language design**.

The process is as important as the product. We're learning:
- How to express programming language intent to AI
- How to maintain coherent vision across sessions
- How to build complex systems incrementally
- How AI can amplify (not replace) human creativity

Every session should leave the codebase better AND teach us something about the collaboration itself.

---

## Quick Reference

```
Before starting:  What's the goal? What's "done"?
During work:      Todos, checkpoints, verify
Before stopping:  Commit, update docs, handoff notes
When stuck:       Explain, propose options, ask
When done:        Summarize, celebrate 🦔
```
