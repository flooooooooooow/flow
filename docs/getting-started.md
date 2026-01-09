# Getting Started with FLOW

## Installation

```bash
git clone https://github.com/flow-lang/flow.git
cd flow
pip install -e .
```

## Hello World

```flow
function main() -> i32 {
    printf("Hello, FLOW!\n")
    return 0
}
```

Run it:
```bash
./flow run examples/hello_world.flow
```

## What Just Happened?

1. FLOW parsed your code into an AST
2. Generated portable C code
3. Compiled with your system's C compiler
4. Executed the binary

## Next Steps

| Goal | Resource |
|------|----------|
| Understand the language | [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) §1-5 |
| Learn systematically | [tutorials/beginner.md](tutorials/beginner.md) |
| See examples | [examples/](examples/) |
| Use effects | [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) §6 |

## Common Commands

```bash
# Compile and run
./flow run file.flow

# Compile to C only
./flow compile file.flow -o output.c

# Compile to executable
./flow compile file.flow && cc build/file.c -o file && ./file
```

## Project Structure

```
your_project/
├── main.flow        # Entry point
├── lib/             # Your modules
│   └── utils.flow
└── build/           # Generated output
```

## FAQ

**Q: What features are actually implemented?**
A: See [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) Appendix C for the complete feature matrix.

**Q: Why C as the backend?**
A: Portability. FLOW-generated C compiles anywhere with a C99 compiler.

**Q: What about performance?**
A: The C backend benefits from compiler optimizations (gcc -O3, clang -O3).
The MLIR backend (WIP) will enable more aggressive optimizations.
