import sys
import os
import subprocess
import hashlib
import re

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

res = subprocess.run(
    ["./compiler/build/flowc_bootstrap", "compiler/fixtures/mlir/test_only_guard.flow"],
    env=dict(os.environ, FLOWC_EMIT="mlir", FLOWC_OUT="raw.mlir"),
    capture_output=True,
    text=True
)

with open("raw.mlir", "r") as f:
    out_text = f.read()

start_idx = out_text.find("module {")
if start_idx != -1:
    out_text = out_text[start_idx:]
else:
    print("Could not find 'module {'")
    sys.exit(1)

lines = out_text.split('\n')
vals = {}
labels = {}
nv = 0
nl = 0
out = []

for line in lines:
    line = line.strip()
    if not line:
        continue

    if line.startswith("llvm.mlir.global "):
        out.append(line)
        continue

    if line.startswith("gpu.func "):
        vals = {}

    i = 0
    n = len(line)
    start = 0
    new_line = ""
    while i < n:
        if line[i] == '%' and i + 1 < n and line[i+1].isdigit():
            j = i + 1
            while j < n and line[j].isdigit():
                j += 1
            tok = line[i:j]
            if tok not in vals:
                nv += 1
                vals[tok] = f"%v{nv}"
            new_line += line[start:i] + vals[tok]
            start = j
            i = j
        elif line[i] == '^' and i + 1 < n and line[i+1] == 'b' and i + 2 < n and line[i+2] == 'b' and i + 3 < n and line[i+3].isdigit():
            j = i + 3
            while j < n and line[j].isdigit():
                j += 1
            tok = line[i:j]
            if tok not in labels:
                nl += 1
                labels[tok] = f"^b{nl}"
            new_line += line[start:i] + labels[tok]
            start = j
            i = j
        else:
            i += 1
    new_line += line[start:]

    # fix func paths
    new_line = re.sub(r'\"<ROOT>/(.*?)\"', r'"\1"', new_line)

    out.append(new_line)

norm_text = '\n'.join(out) + '\n'

with open("compiler/fixtures/mlir/test_only_guard.mlir", "w") as f:
    f.write(norm_text)

h = sha256(norm_text)

with open("compiler/fixtures/mlir/corpus.txt", "r") as f:
    lines = f.read().splitlines()

with open("compiler/fixtures/mlir/corpus.txt", "w") as f:
    for line in lines:
        if "test_only_guard.flow" in line:
            f.write(f"{h} compiler/fixtures/mlir/test_only_guard.flow\n")
        else:
            f.write(line + "\n")
