#!/usr/bin/env python3
"""Flow documentation tools — proof artifacts in English and LaTeX."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from flow.proof_document import (
    write_basic_proof_bundle_pdf,
    write_geometry_proof_bundle_pdf,
    write_proof_artifacts,
    write_proof_artifacts_tree,
    write_proof_book_pdf,
)
from flow.proof_kernel import (
    compile_file_kernel,
    plot_proof_kernel,
    write_kernel_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Flow proof documentation")
    sub = parser.add_subparsers(dest="command", required=True)

    proof = sub.add_parser(
        "proof",
        help="Generate .proof.md (English) and .proof.tex (numbered LaTeX)",
    )
    proof.add_argument("path", help=".flow file or directory")
    proof.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process directories recursively",
    )
    proof.add_argument(
        "-o",
        "--output-dir",
        help="Output directory (default: alongside each source file)",
    )

    bundle = sub.add_parser(
        "bundle",
        help="Generate unified Flow Proof Book PDF (algebra + geometry + analysis)",
    )
    bundle.add_argument(
        "-o",
        "--output-dir",
        help="Output directory (default: build/proofs)",
    )

    basic_bundle = sub.add_parser(
        "basic-bundle",
        help="Generate PDF of Part I only (logic and arithmetic)",
    )
    basic_bundle.add_argument(
        "-o",
        "--output-dir",
        help="Output directory (default: build/proofs)",
    )

    geo_bundle = sub.add_parser(
        "geometry-bundle",
        help="Generate side-by-side PDF of Euclidean geometry proofs with diagrams",
    )
    geo_bundle.add_argument(
        "-o",
        "--output-dir",
        help="Output directory (default: build/proofs)",
    )

    kernel = sub.add_parser(
        "kernel",
        help="Compile proof to parameterizable kernel JSON and plot DAG",
    )
    kernel.add_argument("path", help=".flow theorem file")
    kernel.add_argument(
        "-p",
        "--param",
        action="append",
        metavar="NAME=VALUE",
        help="Parameter instantiation (e.g. n=0, a=true)",
    )
    kernel.add_argument(
        "--plot",
        metavar="FILE",
        help="Plot kernel DAG to PNG/PDF (or .dot without matplotlib)",
    )
    kernel.add_argument(
        "-o",
        "--output",
        help="Kernel JSON output path (default: alongside source)",
    )

    args = parser.parse_args()
    if args.command == "kernel":
        inst: dict = {}
        for pair in args.param or []:
            if "=" in pair:
                k, v = pair.split("=", 1)
                inst[k.strip()] = v.strip()
        json_path = write_kernel_json(
            args.path,
            output=args.output,
            instantiation=inst or None,
        )
        print(f"Wrote {json_path}")
        if args.plot:
            k = compile_file_kernel(args.path, instantiation=inst or None)
            plot_path = plot_proof_kernel(k, args.plot)
            print(f"Wrote {plot_path}")
        return 0

    if args.command == "bundle":
        root = Path(__file__).resolve().parents[2]
        tex, pdf = write_proof_book_pdf(
            str(root),
            output_dir=args.output_dir,
        )
        print(f"Wrote {tex}")
        print(f"Wrote {pdf}")
        return 0

    if args.command == "basic-bundle":
        root = Path(__file__).resolve().parents[2]
        tex, pdf = write_basic_proof_bundle_pdf(
            str(root),
            output_dir=args.output_dir,
        )
        print(f"Wrote {tex}")
        print(f"Wrote {pdf}")
        return 0

    if args.command == "geometry-bundle":
        root = Path(__file__).resolve().parents[2]
        tex, pdf = write_geometry_proof_bundle_pdf(
            str(root),
            output_dir=args.output_dir,
        )
        print(f"Wrote {tex}")
        print(f"Wrote {pdf}")
        return 0

    path = Path(args.path)

    if not path.exists():
        print(f"Error: path not found: {path}", file=sys.stderr)
        return 1

    if path.is_file():
        md, tex, diagrams = write_proof_artifacts(
            str(path),
            output_dir=args.output_dir,
        )
        print(f"Wrote {md}")
        print(f"Wrote {tex}")
        for d in diagrams:
            print(f"Wrote {d}")
        return 0

    results = write_proof_artifacts_tree(str(path), recursive=args.recursive)
    if not results:
        print("No theorem files found.", file=sys.stderr)
        return 1

    for src, md, tex in results:
        print(f"{src}")
        print(f"  -> {md}")
        print(f"  -> {tex}")
        stem = Path(src).stem
        parent = Path(src).parent
        for extra in sorted(parent.glob(f"{stem}*.proof.svg")):
            print(f"  -> {extra}")
        for extra in sorted(parent.glob(f"{stem}*.proof-diagram.tex")):
            print(f"  -> {extra}")
    print(f"\nGenerated {len(results)} proof artifact pair(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())