# Getting Started with FLOW

Welcome to FLOW! This guide will help you get up and running with the FLOW programming language, from installation to your first program.

## 🚀 Installation

### Prerequisites

Before installing FLOW, make sure you have the following dependencies:

- **LLVM 15+** - Required for the compiler backend
- **MLIR** - Multi-Level Intermediate Representation framework
- **CMake 3.20+** - Build system
- **Python 3.8+** - For build scripts and tools
- **Git** - For version control

### Installing Dependencies

#### macOS (Homebrew)
```bash
brew install llvm cmake python3 git
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install llvm-15-dev cmake python3 git
```

#### Fedora/CentOS
```bash
sudo dnf install llvm-devel cmake python3 git
```

### Building FLOW from Source

1. **Clone the Repository**
```bash
git clone https://github.com/flow-lang/flow.git
cd flow
```

2. **Configure the Build**
```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
```

3. **Compile**
```bash
make -j$(nproc)
```

4. **Install (Optional)**
```bash
sudo make install
```

5. **Add to PATH**
```bash
# Add this to your ~/.bashrc or ~/.zshrc
export PATH=$PWD/bin:$PATH
```

### Verifying Installation

Check that FLOW is properly installed:

```bash
flow --version
```

You should see something like:
```
FLOW compiler version 1.0.0
Built with LLVM 15.0.0
```

## 📝 Your First FLOW Program

Let's create your first FLOW program - the classic "Hello, World!"

### Create the Program

Create a new file called `hello.flow`:

```flow
// hello.flow
extern "C" fn printf(s: string, ...);

fn main() {
    printf("Hello, FLOW!\n");
}
```

### Run the Program

Execute your program using the FLOW compiler:

```bash
flow run hello.flow
```

You should see:
```
Hello, FLOW!
```

### Compile and Run Separately

You can also compile to an executable and run it:

```bash
# Compile
flow build hello.flow

# Run
./hello
```

## 🛠️ Development Environment

### Recommended Editors

#### Visual Studio Code
Install the FLOW extension for syntax highlighting and IntelliSense:
```bash
code --install-extension flow-lang.flow
```

#### Vim/Neovim
Add this to your `.vimrc` for FLOW syntax highlighting:
```vim
Plug 'flow-lang/flow-vim'
```

#### Emacs
Use the FLOW mode for Emacs:
```elisp
(require 'flow-mode)
```

### IDE Configuration

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "flow.compilerPath": "/path/to/flow/bin/flow",
    "flow.enableLinting": true,
    "flow.formatOnSave": true
}
```

#### Build Tasks
Create `.vscode/tasks.json` for easy building:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build FLOW",
            "type": "shell",
            "command": "flow",
            "args": ["build", "${file}"],
            "group": "build"
        },
        {
            "label": "Run FLOW",
            "type": "shell",
            "command": "flow",
            "args": ["run", "${file}"],
            "group": "test"
        }
    ]
}
```

## 📚 Basic FLOW Concepts

### Variables and Types

FLOW is statically typed with type inference:

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    // Type inference
    let x = 42;        // i32
    let y = 3.14;      // f32
    let name = "FLOW"; // string
    
    // Explicit types
    let count: i32 = 100;
    let pi: f64 = 3.14159;
    
    printf("x = %d, y = %f, name = %s\n", x, y, name);
}
```

### Functions

Define functions with clear parameter and return types:

```flow
extern "C" fn printf(s: string, ...);

fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

fn greet(name: string) -> string {
    return "Hello, " + name + "!";
}

fn main() {
    let sum = add(10, 20);
    let greeting = greet("World");
    
    printf("Sum: %d\n", sum);
    printf("%s\n", greeting);
}
```

### Control Flow

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    // If-else
    let x = 10;
    if x > 5 {
        printf("x is greater than 5\n");
    } else {
        printf("x is not greater than 5\n");
    }
    
    // Loops
    for i in range(0, 5) {
        printf("Iteration: %d\n", i);
    }
    
    // While loop
    let mut i = 0;
    while i < 3 {
        printf("While iteration: %d\n", i);
        i = i + 1;
    }
}
```

## 🏗️ Project Structure

### Simple Project

For small projects, a single file is sufficient:

```
my_project/
├── main.flow
└── README.md
```

### Medium Project

For larger projects, organize files by functionality:

```
my_project/
├── src/
│   ├── main.flow
│   ├── utils.flow
│   └── graphics.flow
├── tests/
│   ├── test_utils.flow
│   └── test_graphics.flow
├── examples/
│   └── demo.flow
├── build/
└── README.md
```

### Module System

Use FLOW's module system for code organization:

```flow
// utils.flow
export fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

export fn multiply(a: i32, b: i32) -> i32 {
    return a * b;
}
```

```flow
// main.flow
import utils;

extern "C" fn printf(s: string, ...);

fn main() {
    let result = utils.add(10, 20);
    printf("Result: %d\n", result);
}
```

## 🔧 Common Commands

### Building and Running

```bash
# Run directly
flow run program.flow

# Build to executable
flow build program.flow

# Build with optimizations
flow build program.flow -O3

# Build for debugging
flow build program.flow -g
```

### Testing

```bash
# Run all tests
flow test

# Run specific test
flow test test_program.flow

# Run tests with verbose output
flow test --verbose
```

### Documentation

```bash
# Generate documentation
flow docs

# Check for documentation coverage
flow docs --check-coverage
```

### Linting and Formatting

```bash
# Lint code
flow lint program.flow

# Format code
flow format program.flow

# Format entire project
flow format --recursive src/
```

## 🐛 Debugging

### Debug Mode

Compile with debug symbols:

```bash
flow build program.flow -g
```

### Debug Prints

Use printf for debugging:

```flow
extern "C" fn printf(s: string, ...);

fn debug_print(value: i32, location: string) {
    printf("DEBUG [%s]: %d\n", location, value);
}

fn main() {
    let x = 42;
    debug_print(x, "main");
    // ... rest of code
}
```

### Common Issues

#### "printf not found"
Make sure to declare external functions:
```flow
extern "C" fn printf(s: string, ...);
```

#### "Type mismatch"
Check that your variable types match:
```flow
let x: i32 = 42;  // Correct
// let x: i32 = 3.14;  // Error: type mismatch
```

#### "Undefined variable"
Ensure variables are declared before use:
```flow
let x = 10;
printf("%d\n", x);  // OK

// printf("%d\n", y);  // Error: y not defined
```

## 📚 Next Steps

Now that you have FLOW installed and running, here's what to explore next:

1. **[Beginner Tutorial](tutorials/beginner.md)** - Learn the basics
2. **[Language Reference](language/overview.md)** - Detailed language features
3. **[Standard Library](library/overview.md)** - Available functions and modules
4. **[Examples Gallery](examples/README.md)** - See FLOW in action

## 🔗 Resources

- **Official Website**: https://flow-lang.org
- **GitHub Repository**: https://github.com/flow-lang/flow
- **Discord Community**: https://discord.gg/flow-lang
- **Documentation**: https://docs.flow-lang.org

## 💡 Tips for Success

1. **Start Small** - Begin with simple programs and gradually add complexity
2. **Use Type Inference** - Let FLOW infer types when possible, but be explicit when needed
3. **Test Frequently** - Use the built-in testing framework to verify your code
4. **Read Examples** - Study the examples to understand best practices
5. **Join the Community** - Ask questions and share your experiences

---

*Welcome to the FLOW community! Happy coding! 🚀*
