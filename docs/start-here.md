# Start here

This page is for people who have never written a line of code, and for
programmers who want the shortest possible path to a working Flow setup.

You need a Mac or a Linux machine, a terminal window, and about fifteen
minutes. Everything below is copy and paste.

Flow is a language for describing how things change over time. You write down
the rule a system follows, and the compiler turns that rule into a fast
program. A bouncing ball, a savings account, a heart cell, a control loop: all
the same shape of description.

---

## 1. Open a terminal

On a Mac, press `Command` and `Space`, type `Terminal`, press `Return`.

On Linux, press `Ctrl` `Alt` `T`.

A window opens with a blinking cursor. Every command below gets typed into that
window, one line at a time, each followed by `Return`.

---

## 2. Install the build tools

Flow compiles your program into C and then into a real binary, so your computer
needs a C compiler. Most machines already have one.

On a Mac:

```bash
xcode-select --install
```

If it says the tools are already installed, you are done with this step.

On Ubuntu or Debian:

```bash
sudo apt install build-essential python3
```

---

## 3. Install Flow

On a Mac with [Homebrew](https://brew.sh):

```bash
brew tap flooooooooooow/flow
brew install flow
```

Check it worked:

```bash
flow version
```

You should see a version number such as `0.11.1`.

On Linux, or if you want the examples and the full source:

```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow version
```

When you install from source, the command is `./flow` and you run it from
inside the `flow` folder. Everywhere below that says `flow`, type `./flow`
instead.

---

## 4. Turn on the full language

Flow ships two compilers. A small fast one written in Flow itself, and a larger
one that supports the whole language, including printing text to the screen.
The small one is the default, which surprises people on their first program.

Turn on the full one, once, for good:

```bash
echo 'export FLOW_HOST=python' >> ~/.zshrc
source ~/.zshrc
```

If your terminal uses bash rather than zsh, replace `~/.zshrc` with
`~/.bashrc`.

Skip this step and your first program will fail with
`flowc emit failed (Stage-A subset?)`. That message means the small compiler
was asked for something it does not have yet.

---

## 5. Run your first program

Make a folder to work in:

```bash
mkdir ~/flow-play
cd ~/flow-play
```

Create a file called `hello.flow`. If you have no editor you like, this command
writes the file for you:

```bash
cat > hello.flow <<'EOF'
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
EOF
```

Run it:

```bash
flow run hello.flow
```

```
ℹ️  Compiling hello.flow...
✅ FLOW → C: hello.c
✅ C → Executable: hello
ℹ️  Running hello...
----------------------------------------
Hello, Flow!
----------------------------------------
✅ Program finished
Exit code: 0
```

The first run takes around twenty seconds. Flow is building a real native
program, the same kind of binary a C compiler produces. It is not interpreting
your file line by line.

---

## 6. Run something that moves

Here is the shape of Flow that no other language has. Write a `flow` block that
states how a system evolves, and the compiler builds the simulation for you.

```bash
cat > ball.flow <<'EOF'
flow Ball {
    state height      : f64 = 2.0
    state velocity    : f64 = 0.0
    param gravity     : f64 = 9.81
    param restitution : f64 = 0.8

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }
}

function main() -> i32 {
    let dt: f64 = 0.001
    let mut ball: Ball = Ball_new()

    for k in 0 to 3000 {
        Ball_step(&ball, dt)
        if k % 500 == 0 {
            println(ball.height)
        }
    }
    return 0
}
EOF

flow run ball.flow
```

Read the block out loud and it says what it does. Height changes at the rate of
velocity. Velocity changes at the rate of gravity, downward. When the height
reaches zero, the ball bounces and keeps eighty percent of its speed.

That is the whole program. There is no solver to write, no loop of physics
maths, no library to import.

---

## 7. Let an AI write Flow for you

Flow is young, so an AI assistant does much better when it has been told how the
language actually works today. There is a pack of skills and tools for exactly
this.

Install [Claude Code](https://claude.com/claude-code):

```bash
npm install -g @anthropic-ai/claude-code
```

Then install the Flow skills pack:

```bash
git clone https://github.com/flooooooooooow/flow-skills.git
cd flow-skills
./install.sh
```

The installer copies a set of skills into `~/.claude/skills/` and puts a few
helper commands on your path. It prints exactly what it did.

Now go back to your project folder and start the assistant:

```bash
cd ~/flow-play
claude
```

Paste this as your first message:

```text
I am new to Flow. Use the flow-setup skill to check my toolchain, then use
flow-basics to write and run a small program. Explain what you are doing in
plain language as you go.
```

From then on, ask for what you want in ordinary words:

```text
Write a Flow program that simulates a savings account earning 4% a year with
£200 paid in every month, and print the balance once a year for ten years.
Run it and show me the output.
```

```text
Simulate two populations, rabbits and foxes, using a flow block. Record it as
an animated GIF so I can see the cycles.
```

The assistant will write the file, run it, read the errors if there are any,
and fix them. You review the result. If the numbers look wrong, say so and it
will check them against a formula you can verify.

### Using a different assistant

The pack works with anything that reads project instructions. Copy
`AGENTS.md` from the skills repo into whatever folder you work in, and point
Cursor, Codex, or any other tool at it. The rules are plain Markdown.

---

## 8. Make a picture

Flow draws to a real window and can record what it draws.

```bash
flow examples
```

That lists the programs shipped with Flow. If you installed from source, pick
one of the graphical ones and record it:

```bash
flow record examples/games/snake_gfx.flow --frames 200 --gif snake.gif
```

Open `snake.gif` in any image viewer.

To watch it live in a window instead:

```bash
flow gfx examples/games/snake_gfx.flow
```

---

## When something goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `flowc emit failed (Stage-A subset?)` | The small compiler does not support this program | Do step 4, or put `FLOW_HOST=python` in front of the command |
| `command not found: flow` | Flow is not on your path | Use `./flow` from inside the `flow` folder, or reinstall with Homebrew |
| `clang: command not found` | No C compiler | Do step 2 |
| The program compiles but the numbers look wrong | Usually the model, rarely the compiler | Ask the assistant to check the result against a closed-form answer or a smaller time step |
| Nothing happens for a long time | Normal on a first run | Wait. Later runs of the same file are faster |

If you get stuck, the [Discord](https://discord.gg/YK7VaHy24T) is the fastest
place to ask, and questions from beginners are welcome there.

---

## Where to go next

- [Introduction to Flow](book/README.md) is a short book that starts from a
  complete program and builds up.
- [Interactive tutorials](tutorials/index.html) run in your browser with
  nothing installed.
- [Getting started](getting-started.md) is the same ground as this page, at a
  faster pace, for people who already program.
- [Working with AI on Flow](AI_FLOW_HANDBOOK.md) is the full operating manual
  behind the skills pack. Read it when you want to direct an assistant
  precisely rather than conversationally.
- [Vision](vision.md) explains why the language treats time the way it does.
