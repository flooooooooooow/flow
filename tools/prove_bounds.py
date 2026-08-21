#!/usr/bin/env python3
"""Report what the bounds prover concludes about each span access in a file."""
import sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from flow.parser import Parser, Lexer, FunctionDecl
from flow.bounds_proof import BoundsProver, PROVEN, HOIST, REFUTED, UNKNOWN

def fmt(form):
    parts = [f"{c:+d}*{s.key.replace('v:','')}" for s, c in sorted(form.terms.items(), key=lambda x: x[0].key)]
    return " ".join(parts) + (f" {form.const:+d}" if form.const else "") + " >= 0"

def functions(path):
    src = pathlib.Path(path).read_text()
    for d in Parser(Lexer(src), src).parse():
        if isinstance(d, FunctionDecl) and getattr(d, "body", None):
            yield d

def main():
    verbose = "-v" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    total = collections.Counter(); why = collections.Counter(); guards = 0
    for path in paths:
        try:
            fns = list(functions(path))
        except Exception as e:
            print(f"  !! {pathlib.Path(path).name}: {type(e).__name__}: {str(e)[:70]}")
            continue
        for d in fns:
            p = BoundsProver()
            try:
                p.run(d)
            except Exception as e:
                print(f"  !! {pathlib.Path(path).name}:{d.name}: {type(e).__name__}: {str(e)[:60]}")
                continue
            if not p.verdicts: continue
            for v in p.verdicts.values():
                total[v.kind] += 1
                if v.detail: why[v.detail] += 1
            guards += sum(1 for g in p.loop_guards.values() if not g.is_empty())
            if verbose:
                kinds = collections.Counter(v.kind for v in p.verdicts.values())
                print(f"{pathlib.Path(path).name}:{d.name:22s} {dict(kinds)}")
                for g in p.loop_guards.values():
                    for f in g.ascending:  print(f"      guard(asc)  {fmt(f)}")
                    for f in g.descending: print(f"      guard(desc) {fmt(f)}")
    n = sum(total.values())
    if not n: print("no accesses analysed"); return 1
    print(f"\n{n} span accesses, {guards} hoisted loop guards\n")
    for kind in (PROVEN, HOIST, UNKNOWN, REFUTED):
        print(f"  {total[kind]:5d}  {100*total[kind]/n:5.1f}%  {kind}")
    freed = total[PROVEN] + total[HOIST]
    print(f"\n  {freed}/{n} = {100*freed/n:.1f}% of accesses lose their per-access check")
    if why:
        print("\n  why the rest stayed:")
        for d, c in why.most_common(6): print(f"    {c:5d}  {d}")
    return 0

sys.exit(main())
