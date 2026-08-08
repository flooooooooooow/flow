class Flow < Formula
  include Language::Python::Virtualenv

  desc "Statically typed language with algebraic effects, autodiff, and a C backend"
  homepage "https://flooooooooooow.github.io/flow/"
  license "MIT"
  url "https://github.com/flooooooooooow/flow/releases/download/v0.10.0/flow-v0.10.0.tar.gz"
  sha256 "05dc81ee33089724977cf1e6dfac00e9bfd8bbd81da8649570ea8c21669da486"
  version "0.10.0"
  head "https://github.com/flooooooooooow/flow.git", branch: "main"

  depends_on "python@3.12"

  def install
    # Keep the repo layout intact — the `flow` driver resolves SCRIPT_DIR via
    # realpath and expects src/, lib/, runtime/ next to itself.
    libexec.install "flow", "flow-lsp"
    libexec.install "src", "lib", "runtime", "compiler"
    libexec.install "tools" if (buildpath/"tools").exist?
    libexec.install "wasm" if (buildpath/"wasm").exist?
    libexec.install "examples" if (buildpath/"examples").exist?
    libexec.install "pyproject.toml" if (buildpath/"pyproject.toml").exist?
    libexec.install "requirements.txt" if (buildpath/"requirements.txt").exist?

    chmod 0755, libexec/"flow"
    chmod 0755, libexec/"flow-lsp" if (libexec/"flow-lsp").exist?

    python = Formula["python@3.12"].opt_bin/"python3.12"
    venv = virtualenv_create(libexec/"venv", python)
    venv.pip_install "numpy"

    env = {
      PATH: "#{libexec}/venv/bin:#{Formula["python@3.12"].opt_libexec}/bin:$PATH",
    }
    (bin/"flow").write_env_script libexec/"flow", env
    (bin/"flow-lsp").write_env_script libexec/"flow-lsp", env if (libexec/"flow-lsp").exist?
  end

  def caveats
    <<~EOS
      Flow compiles programs to C and shells out to clang at run time.
      On macOS, install the Xcode Command Line Tools if needed:
        xcode-select --install

      For MLIR / JIT support, also install LLVM and put it on PATH:
        brew install llvm
        export PATH="$(brew --prefix llvm)/bin:$PATH"

      Installed Flow #{version}. Use `brew install --HEAD flow` for main.
    EOS
  end

  test do
    (testpath/"hello.flow").write <<~EOS
      function main() -> i32 {
        return 0
      }
    EOS
    # `flow compile` should exit 0 for a trivial program.
    system bin/"flow", "compile", "hello.flow"
  end
end
