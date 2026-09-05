#!/usr/bin/env python3
import os
import subprocess
import json
import sys

PYTHON_DEPLOYMENT_SIZE = 25 * 1024 * 1024 # 25MB

def get_binary_size(path):
    return os.stat(path).st_size

def get_binary_sections(path):
    result = subprocess.run(['size', path], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    if len(lines) >= 2:
        parts = lines[1].split()
        if len(parts) >= 3:
            return {
                'text': int(parts[0]),
                'data': int(parts[1]),
                'bss': int(parts[2])
            }
    return None

def strip_binary(path):
    subprocess.run(['strip', path])

def compile_flow(path):
    name = os.path.basename(path).replace('.flow', '')
    subprocess.run(['./flow', 'compile', path], env=dict(os.environ, FLOW_HOST='python'), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f'build/{name}'

def run_benchmarks(programs=None):
    if not programs:
        programs = [
            'examples/basics/hello_world.flow',
            'examples/basics/fibonacci.flow',
            'examples/basics/loops.flow'
        ]
    
    results = {}
    
    for prog in programs:
        name = os.path.basename(prog)
        bin_path = compile_flow(prog)
        
        sections = get_binary_sections(bin_path)
        unstripped_size = get_binary_size(bin_path)
        
        strip_binary(bin_path)
        stripped_size = get_binary_size(bin_path)
        
        results[name] = {
            'sections': sections,
            'unstripped_size': unstripped_size,
            'stripped_size': stripped_size,
            'python_ratio_percent': (stripped_size / PYTHON_DEPLOYMENT_SIZE) * 100
        }
        
    return results

def print_report(results, out_file=None):
    report = ["# Binary Size Report", ""]
    report.append(f"Comparison baseline: Python minimum footprint (~25MB)")
    report.append("")
    report.append("| Program | `.text` | `.data` | `.bss` | Unstripped | Stripped | % of Python |")
    report.append("|---------|---------|---------|--------|------------|----------|-------------|")
    
    for name, data in results.items():
        s = data['sections']
        pct = f"{data['python_ratio_percent']:.2f}%"
        report.append(f"| `{name}` | {s['text']} | {s['data']} | {s['bss']} | {data['unstripped_size']} | {data['stripped_size']} | {pct} |")
        
    report.append("")
    report_text = "\n".join(report)
    print(report_text)
    
    if out_file:
        with open(out_file, 'w') as f:
            f.write(report_text)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Measure FLOW binary sizes")
    parser.add_argument('--out', type=str, help="Output markdown report file")
    parser.add_argument('programs', nargs='*', help="FLOW programs to measure")
    args = parser.parse_args()
    
    results = run_benchmarks(args.programs if args.programs else None)
    print_report(results, args.out)
