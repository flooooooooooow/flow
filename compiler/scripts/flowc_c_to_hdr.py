#!/usr/bin/env python3
"""Derive a C header from Stage-A flowc emit output (multi-module dogfood).

Keeps includes + typedef structs, turns consts into extern, functions into prototypes.
"""
from __future__ import annotations

import re
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} in.c out.h", file=sys.stderr)
        return 2
    src = open(sys.argv[1], encoding="utf-8").read()
    out: list[str] = []
    for line in src.splitlines():
        if line.startswith("#include"):
            out.append(line)
    out.append("")
    for m in re.finditer(r"typedef struct \w+ \{.*?\n\} \w+;", src, re.S):
        out.append(m.group(0))
        out.append("")
    for m in re.finditer(r"^(?:static )?const int32_t (\w+) = [^;]+;", src, re.M):
        out.append(f"extern const int32_t {m.group(1)};")
    out.append("")
    for line in src.splitlines():
        if not line.endswith(") {"):
            continue
        s = line.lstrip()
        if s.startswith(("if ", "while ", "for ", "else ", "switch ")):
            continue
        if re.match(r"^[A-Za-z_].*\(.*\) \{$", line):
            out.append(line[:-2].rstrip() + ";")
    open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
