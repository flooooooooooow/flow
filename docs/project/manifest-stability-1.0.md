# Flow 1.0 project manifest stability contract

`flow.toml` is an extensible project manifest. Flow 1.0 freezes only the compiler/project fields already required by ordinary Stable source resolution. Package-registry, native-link and development-policy extensions remain Experimental until their installation, integrity and portability contracts are separately qualified.

## Stable core schema

The Stable 1.x reader recognises the following fields.

| TOML location | Type | Meaning |
| --- | --- | --- |
| `[package].name` | string | Project/package name. |
| `[package].version` | string | Project/package version. Flow's own release tooling uses semantic versions; project-specific validation may become stricter only through an additive validation/versioning mechanism. |
| `[package].entry` | string | Project entry Flow source path when a command needs a default entry point. |
| `[paths].<alias>` | string | Maps a logical module-root alias to a directory relative to the project root. |

The `[paths].stdlib` alias may select a project-local standard-library root when that directory exists; otherwise the installed compiler's standard library remains the fallback. Ordinary module resolution may also consult `[dependencies]`, but dependency acquisition/source specifications are not part of the Stable 1.0 manifest core until the package-security and reproducibility work is qualified.

All Stable path values are interpreted relative to the directory containing `flow.toml` unless a separately documented field says otherwise. A compiler finding a project manifest by walking upward from a source path is part of the Stable project-discovery behaviour.

## Forward compatibility

Readers must ignore top-level tables and fields they do not consume rather than treating their mere presence as invalid Stable Flow. This permits 1.x to add optional metadata or Experimental extensions without changing the core schema. A future manifest-format version field may introduce stricter validation additively; 1.0 does not manufacture an implicit schema version that current files do not contain.

Stable fields may gain additional validation only when existing valid 1.x projects remain accepted or the change follows the compatibility/deprecation policy in `STABILITY.md`. Their meaning cannot be silently reassigned during 1.x.

## Experimental extensions

The current package tooling understands more than the Stable compiler/project core. These surfaces remain Experimental for 1.0 unless separately promoted: `[package].description`, `author` and `license` as package-publication metadata; dependency version/source forms in `[dependencies]`; `[dev-dependencies]`; `[native]` sources/frameworks/libs/cflags/ldflags; `[build]`; `[conventions]`; `[patterns]`; registry publication metadata; git/path dependency acquisition; lockfile/install semantics; and native build/package commands.

Some of these fields are already useful and may be widely exercised. Experimental classification here is about the 1.x compatibility and security promise, not whether the implementation exists. In particular, dependency acquisition and archive/extraction behaviour must satisfy #650/#652 before Flow 1.0 treats it as a Stable supply-chain interface.

## Minimal Stable example

```toml
[package]
name = "example"
version = "1.0.0"
entry = "src/main.flow"

[paths]
app = "src"
```

A tool may preserve additional unknown/Experimental tables when rewriting a manifest, but the Stable compiler must not require those extensions in order to compile an otherwise self-contained Stable project.
