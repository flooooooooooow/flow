# FLOW Documentation

## 📖 Single Source of Truth

**[LANGUAGE_SPEC.md](LANGUAGE_SPEC.md)** — The authoritative language specification.
Everything else references this. If there's a conflict, the spec wins.

---

## Documentation Hierarchy

```
LANGUAGE_SPEC.md          ← AUTHORITATIVE (what IS implemented)
│
├── getting-started.md    ← How to start (practical, links to spec)
│
├── tutorials/            ← Learning paths (teach concepts, link spec for details)
│   ├── beginner.md
│   ├── intermediate.md  
│   └── advanced.md
│
├── examples/             ← Working code (demonstrates spec features)
│   ├── basic/
│   ├── algorithms/
│   ├── data-structures/
│   ├── effects/
│   ├── graphics/
│   └── gpu/
│
├── library/              ← Stdlib reference (links to spec for types)
│   └── *.md
│
└── reference/            ← Quick lookups (derived from spec)
    └── api.md
```

## Principles

1. **No Redundancy**: Don't repeat type tables, syntax definitions, or feature lists.
   Link to the spec section instead.

2. **Maximum Variance**: Each doc serves ONE purpose:
   - Spec → What exists
   - Tutorial → How to learn
   - Example → Working code
   - Reference → Quick lookup

3. **Status Tracking**: The spec uses ✅ ⚠️ ❌ for implementation status.
   All other docs should match or link to the spec's status.

---

## Quick Links

| I want to... | Go to |
|--------------|-------|
| Know what's implemented | [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) |
| Start coding | [getting-started.md](getting-started.md) |
| Learn step-by-step | [tutorials/](tutorials/) |
| See working examples | [examples/](examples/) |
| Look up stdlib | [library/](library/) |
| Understand the compiler | [project/](project/) |

---

## Status

| Component | Spec | Impl | Tests |
|-----------|------|------|-------|
| Lexer | ✅ | ✅ | ⚠️ |
| Parser | ✅ | ✅ | ⚠️ |
| C Backend | ✅ | ✅ | ⚠️ |
| MLIR Backend | ⚠️ | ⚠️ | ⚠️ |
| Effect System | ✅ | ✅ | ✅ |
| Module System | ✅ | ✅ | ⚠️ |
| WASM | ⚠️ | ⚠️ | ⚠️ |
