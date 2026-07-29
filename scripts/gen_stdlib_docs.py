#!/usr/bin/env python3
"""Generate docs/library/stdlib-api.md from lib/stdlib/*.flow export signatures."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STDLIB = ROOT / "lib" / "stdlib"
OUT = ROOT / "docs" / "library" / "stdlib-api.md"

SKIP = {".DS_Store"}

STRUCT_RE = re.compile(
    r"^export\s+struct\s+(\w+)\s*\{",
    re.MULTILINE,
)
FN_RE = re.compile(
    r"^export\s+function\s+(\w+)\s*(\([^;{]*\))\s*(?:->\s*([^{\n]+))?",
    re.MULTILINE,
)
CONST_RE = re.compile(
    r"^export\s+const\s+(\w+)\s*:\s*([^=]+)=",
    re.MULTILINE,
)
TRAIT_RE = re.compile(
    r"^export\s+trait\s+(\w+)",
    re.MULTILINE,
)


def module_title(path: Path) -> str:
    return path.relative_to(STDLIB).as_posix()


def leading_doc(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("#"):
            lines.append(line.lstrip("# ").strip())
        elif not line.strip():
            if lines:
                break
        else:
            break
    return " ".join(lines[:3]).strip()


def extract(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "doc": leading_doc(text),
        "structs": STRUCT_RE.findall(text),
        "traits": TRAIT_RE.findall(text),
        "consts": [(m.group(1), m.group(2).strip()) for m in CONST_RE.finditer(text)],
        "fns": [
            (m.group(1), m.group(2).strip(), (m.group(3) or "void").strip())
            for m in FN_RE.finditer(text)
        ],
    }


def main() -> int:
    files = sorted(
        p
        for p in STDLIB.rglob("*.flow")
        if p.name not in SKIP and "test" not in p.parts
    )
    lines = [
        "# Standard Library API (generated)",
        "",
        f"> Auto-generated from `lib/stdlib/` on {date.today().isoformat()} by "
        "`scripts/gen_stdlib_docs.py`. Hand-written guides live alongside this page.",
        "",
        f"**{len(files)}** modules scanned.",
        "",
        "## Modules",
        "",
    ]

    for path in files:
        info = extract(path)
        rel = module_title(path)
        lines.append(f"### `{rel}`")
        lines.append("")
        if info["doc"]:
            lines.append(info["doc"])
            lines.append("")
        if info["traits"]:
            lines.append("**Traits:** " + ", ".join(f"`{t}`" for t in info["traits"]))
            lines.append("")
        if info["structs"]:
            lines.append("**Structs:** " + ", ".join(f"`{s}`" for s in info["structs"]))
            lines.append("")
        if info["consts"]:
            lines.append("**Constants:**")
            lines.append("")
            for name, ty in info["consts"][:40]:
                lines.append(f"- `{name}: {ty}`")
            lines.append("")
        if info["fns"]:
            lines.append("**Functions:**")
            lines.append("")
            lines.append("| Name | Signature |")
            lines.append("|------|-----------|")
            for name, params, ret in info["fns"][:80]:
                sig = f"{params} -> {ret}".replace("|", "\\|")
                lines.append(f"| `{name}` | `{sig}` |")
            if len(info["fns"]) > 80:
                lines.append(f"| … | {len(info['fns']) - 80} more |")
            lines.append("")
        if not any((info["structs"], info["fns"], info["traits"], info["consts"])):
            lines.append("*No `export` items found (internal / extern-only module).*")
            lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(files)} modules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
