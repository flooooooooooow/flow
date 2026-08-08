#!/usr/bin/env python3
"""CLI for FIR-G: graphify + CPU/MLX analyses + routing + opt candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Optional, Set

from .fir_analysis import analyse
from .fir_graphify import graphify
from .module_resolver import resolve_modules
from .monomorphize import monomorphize
from .transpiler import _filter_declarations


def build_fir_g(program: str, *, active_modes: Optional[Set[str]] = None):
    modes = active_modes or {"compile", "c"}
    declarations = resolve_modules(program)
    declarations = _filter_declarations(declarations, modes)
    declarations = monomorphize(declarations)
    declarations = _filter_declarations(declarations, modes)
    return graphify(declarations)


def dump_text(report: dict) -> str:
    lines = [
        report["summary"],
        f"call ops: {report['num_call_ops']}",
        f"reachable: {', '.join(report['reachable']) or '(none)'}",
        f"dead: {', '.join(report['dead']) or '(none)'}",
        "call graph:",
    ]
    for caller, callee, site in report["call_edges"]:
        lines.append(f"  {caller} -> {callee}  (op {site})")
    lines.append("effects / pure:")
    for name, bits in report["effects"].items():
        pure = report["pure"].get(name, False)
        lines.append(f"  {name}: effects=0x{bits:04x} pure={pure}")
    if report.get("device_chosen") is not None:
        lines.append(
            f"device: requested={report.get('device_requested')} "
            f"chosen={report['device_chosen']}"
        )
    if report.get("bulk_backend"):
        lines.append(
            f"bulk check ({report['bulk_backend']}): "
            f"effects_match={report['bulk_effects_match']} "
            f"reach_match={report['bulk_reach_match']} "
            f"({report['bulk_ms']:.3f} ms)"
        )
    opts = report.get("opt_candidates")
    if opts:
        lines.append(
            f"opt candidates: total={opts['total']} by_kind={opts['by_kind']}"
        )
        for c in opts["top"][:12]:
            extra = ""
            if c.get("caller"):
                extra = f" caller={c['caller']}"
            lines.append(
                f"  [{c['kind']}] {c['target']} score={c['score']} "
                f"({c['reason']}){extra}"
            )
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flow FIR-G: program graph + CPU/MLX analyses"
    )
    parser.add_argument(
        "program",
        nargs="?",
        help=".flow source file (optional with --calibrate alone)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "numpy", "mlx", "auto"],
        help="analysis device (default: cpu). auto uses measured thresholds "
        "(uncalibrated → cpu)",
    )
    parser.add_argument(
        "--bench",
        action="store_true",
        help="print rough CPU vs bulk wall times for this program",
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="sweep synthetic graph sizes, measure break-even, save thresholds",
    )
    parser.add_argument(
        "--thresholds",
        type=str,
        default=None,
        help="path to fir_g_route.json (default: $FLOW_FIR_G_THRESHOLDS or "
        "~/.cache/flow/fir_g_route.json)",
    )
    parser.add_argument(
        "--opts",
        action="store_true",
        help="list deterministic optimisation candidates (dead_elim / inline)",
    )
    args = parser.parse_args(argv)

    thresh_path = Path(args.thresholds) if args.thresholds else None

    if args.calibrate:
        from .fir_route import calibrate_routing, default_thresholds_path, save_thresholds

        th = calibrate_routing()
        out = save_thresholds(th, thresh_path)
        payload = th.to_json()
        payload["saved_to"] = str(out)
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"calibrated routing → {out}")
            print(
                f"  bulk_backend={th.bulk_backend} "
                f"min_funcs={th.min_funcs} min_edges={th.min_edges}"
            )
            for s in th.samples:
                print(
                    f"  F={s['n_funcs']} E={s['n_edges']}: "
                    f"cpu={s['cpu_ms']:.3f} ms  "
                    f"{s['bulk_backend']}={s['bulk_ms']:.3f} ms"
                )
            if th.min_funcs >= 10**9:
                print("  (bulk never beat CPU in sweep — auto stays on cpu)")
        if not args.program:
            return 0

    if not args.program:
        parser.error("program is required unless using --calibrate alone")

    path = Path(args.program)
    if not path.exists():
        print(f"error: no such file: {path}", file=sys.stderr)
        return 1

    g = build_fir_g(str(path))
    report: dict[str, Any] = analyse(g)
    report["device_requested"] = args.device

    from .fir_route import choose_analysis_backend

    chosen = choose_analysis_backend(
        g, args.device, thresholds_path=thresh_path
    )
    report["device_chosen"] = chosen

    if chosen != "cpu":
        from .fir_mlx import analyse_bulk

        bulk = analyse_bulk(g, backend=chosen)
        cpu_effects = [report["effects"][g.func_name[i]] for i in range(g.num_funcs())]
        cpu_reach = {
            g._func_by_name[n] for n in report["reachable"] if n in g._func_by_name
        }
        report["bulk_backend"] = bulk.backend
        report["bulk_ms"] = bulk.elapsed_ms
        report["bulk_effects_match"] = list(bulk.effects) == cpu_effects
        report["bulk_reach_match"] = bulk.reachable == cpu_reach
        if not report["bulk_effects_match"] or not report["bulk_reach_match"]:
            print(
                "error: bulk analysis diverged from CPU oracle "
                f"(effects_match={report['bulk_effects_match']}, "
                f"reach_match={report['bulk_reach_match']})",
                file=sys.stderr,
            )
            return 2

    if args.opts:
        from .fir_opts import discover_candidates, summarise_candidates

        cands = discover_candidates(g)
        report["opt_candidates"] = summarise_candidates(cands)

    if args.bench:
        from .fir_mlx import break_even_hint

        cpu_ms, bulk_ms, bulk_name = break_even_hint(g)
        report["bench_cpu_ms"] = cpu_ms
        report["bench_bulk_ms"] = bulk_ms
        report["bench_bulk_name"] = bulk_name

    if args.json:
        payload = dict(report)
        payload["call_edges"] = [
            {"caller": a, "callee": b, "op": c} for a, b, c in report["call_edges"]
        ]
        payload["reachable"] = list(report["reachable"])
        print(json.dumps(payload, indent=2))
    else:
        print(dump_text(report))
        if args.bench:
            bn = report.get("bench_bulk_name")
            print(
                f"bench: cpu={report['bench_cpu_ms']:.3f} ms"
                + (
                    f", {bn}={report['bench_bulk_ms']:.3f} ms"
                    if bn is not None
                    else ", bulk=n/a"
                )
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
