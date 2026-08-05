# Getting Started with Flow

Get from zero to productive in 5 minutes.

## Installation

### Requirements

- Python 3.9+
- Clang or GCC (Xcode Command Line Tools on macOS)

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

No pip install needed — Flow runs directly from the repo (or the Homebrew prefix).

## Hello World

Create `hello.flow`:

```flow
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
```

Run it:

```bash
./flow run hello.flow
```

## Language Basics

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

### Control Flow

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

## CLI Commands

```bash
./flow run <file>       # Compile and run
./flow compile <file>   # Compile only
./flow test             # Run tests
./flow fmt <file>       # Format code
./flow repl             # Interactive mode
```

## Native Graphics (macOS)

For graphical applications:

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

## Next Steps

| Goal | Resource |
|------|----------|
| Language reference | [docs/LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) |
| Examples | [examples/](../examples/) |
| Effects system | [examples/effects/](../examples/effects/) |
| Machine learning | [examples/ml/](../examples/ml/) |

## Troubleshooting

**"command not found: flow"** - Use `./flow` (with dot-slash)

**"gcc/clang not found"** - Install: `xcode-select --install` (macOS) or `apt install build-essential` (Ubuntu)
