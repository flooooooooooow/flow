# Getting started with Flow

From zero to a running program in a few minutes.

## Installation

### Requirements

- Clang or GCC (Xcode Command Line Tools on macOS)
- Python 3.9+ (for `FLOW_HOST=python`, tests, MLIR/gfx, and first-time Gen0 bootstrap)

### Homebrew

```bash
brew tap flooooooooooow/flow
brew install flow
flow version
```

### From source

```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow version
```

`./flow run` and `./flow compile` default to Stage-A **flowc** (`FLOW_HOST=flowc`). Use `FLOW_HOST=python` for the full language surface (I/O helpers, DSLs, tests). See [self-hosting](project/self-hosting.md).

## Hello world

Create `hello.flow` (Stage-A subset; works with the default flowc host):

```flow
function main() -> i32 {
    return 0
}
```

Run it:

```bash
./flow run hello.flow
```

For `println` and other full-language features:

```bash
FLOW_HOST=python ./flow run hello.flow
```

## Language basics

### Variables

```flow
let x: i32 = 42              # Immutable
let mut count: i32 = 0       # Mutable
count = count + 1
```

### Functions

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function greet(name: string) -> void {
    println(name)
}
```

### Control flow

```flow
# If/else
if x > 0 {
    println("positive")
} elif x < 0 {
    println("negative")
} else {
    println("zero")
}

# While loop
let mut i: i32 = 0
while i < 10 {
    println(i)
    i = i + 1
}

# For loop
for i in 0 to 10 {
    println(i)
}
```

### Structs

```flow
struct Point {
    x: f32,
    y: f32
}

function main() -> i32 {
    let p: Point = Point { x: 3.0, y: 4.0 }
    println(p.x)
    return 0
}
```

## CLI commands

```bash
./flow run <file>       # Compile and run
./flow compile <file>   # Compile only
./flow test             # Run tests
./flow fmt <file>       # Format code
./flow repl             # Interactive mode
```

## Native graphics (macOS)

```bash
# Compile
./flow compile examples/games/tetris_gfx.flow

# Link with graphics runtime
clang -O2 build/tetris_gfx.c runtime/gfx_macos.m \
    -framework Cocoa -framework CoreGraphics -framework QuartzCore \
    -o build/tetris_gfx

# Run
./build/tetris_gfx
```

Or use `./flow gfx examples/games/tetris_gfx.flow` when the gfx host is available.

## Next steps

| Goal | Resource |
|------|----------|
| How to structure Flow code | [Coding best practices](language/best-practices.md) |
| Language reference | [docs/LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) |
| Examples | [examples/](../examples/) |
| Effects system | [examples/effects/](../examples/effects/) |
| Machine learning | [examples/ml/](../examples/ml/) |
| Galleries | [demos/overview.md](demos/overview.md) |

## Troubleshooting

**"command not found: flow"**: use `./flow` (with the leading `./`).

**"gcc/clang not found"**: install with `xcode-select --install` (macOS) or `apt install build-essential` (Ubuntu).
