"""flow check: lint .flow files against project conventions (#415).

Reads [conventions].avoid from flow.toml and warns when source
files match avoid patterns.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flow.conventions import check_file, load_conventions


import json
import argparse
from flow.parser import Parser, Lexer
from flow.idioms import IdiomAdvisor


def main(argv: list[str] | None = None) -> int:
    args_list = argv if argv is not None else sys.argv[1:]
    
    check_idioms = False
    output_format = "text"
    file_args = []
    
    for arg in args_list:
        if arg == "--idioms":
            check_idioms = True
        elif arg.startswith("--format="):
            output_format = arg.split("=")[1]
        elif arg == "--format":
            pass
        elif not arg.startswith("-"):
            file_args.append(arg)

    conv = load_conventions()
    if not conv.avoid and not check_idioms:
        print("No avoid patterns defined in flow.toml.")
        return 0

    if file_args:
        files = [Path(a) for a in file_args]
    else:
        files = list(Path.cwd().rglob("*.flow"))
        files = [f for f in files if "build/" not in str(f) and ".freebuff/" not in str(f)]

    if not files:
        print("No .flow files found.")
        return 0

    total_warnings = 0
    all_findings = []
    
    for f in files:
        if conv.avoid:
            warnings = check_file(f, conv)
            for w in warnings:
                if output_format == "text":
                    print(w, file=sys.stderr)
                total_warnings += 1
                
        if check_idioms:
            try:
                code = f.read_text()
                ast = Parser(Lexer(code)).parse()
                advisor = IdiomAdvisor()
                for node in ast:
                    from flow.parser import FunctionDecl
                    if isinstance(node, FunctionDecl):
                        advisor.analyze_function(node)
                
                lines = code.split('\n')
                for finding in advisor.findings:
                    # Check for suppressions in the file text
                    suppress_str = f"# flow-idiom: allow {finding.rule_id}"
                    
                    line_idx = finding.line - 1
                    is_suppressed = False
                    if 0 <= line_idx - 1 < len(lines):
                        if suppress_str in lines[line_idx - 1]:
                            is_suppressed = True
                    if 0 <= line_idx < len(lines):
                        if suppress_str in lines[line_idx]:
                            is_suppressed = True

                    if is_suppressed:
                        continue

                    if output_format == "json":
                        finding_dict = finding.to_dict()
                        finding_dict["file"] = str(f)
                        all_findings.append(finding_dict)
                    else:
                        print(f"{f}:{finding.line}:{finding.column}: {finding.severity}: [{finding.rule_id}] {finding.title} - {finding.rationale}")
                        if finding.replacement:
                            print(f"  Suggested fix: {finding.replacement}")
                    total_warnings += 1
            except Exception as e:
                pass

    if output_format == "json":
        print(json.dumps(all_findings, indent=2))
        return 1 if total_warnings > 0 else 0

    if total_warnings == 0:
        if conv.avoid and not check_idioms:
            print(f"Checked {len(files)} files. No convention violations found.")
        else:
            print(f"Checked {len(files)} files. No violations or idiom suggestions found.")
        return 0
    
    print(f"\n{total_warnings} warning(s)/suggestion(s) in {len(files)} files.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
