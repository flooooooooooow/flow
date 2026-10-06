class Flow < Formula
  include Language::Python::Virtualenv

  desc "Statically typed language with algebraic effects, autodiff, and a C backend"
  homepage "https://flooooooooooow.github.io/flow/"
  url "https://github.com/flooooooooooow/flow/releases/download/v1.0.1/flow-v1.0.1.tar.gz"
  sha256 "deb4978f97cb5643c29fcb9d73ab72a8eb121e2e31c60df73ba6870d04f5229b"
  license "MIT"
  head "https://github.com/flooooooooooow/flow.git", branch: "main"

  depends_on "python@3.12"

  def install
    # Stable v1.0.1 uses the Python src/ tree, while HEAD uses the
    # self-hosted CLI plus VERSION/tools. Both keep their repo-relative layout.
    libexec.install "flow", "flow-lsp"
    libexec.install "lib", "runtime", "compiler"
    if build.head?
      libexec.install "VERSION", "tools"
    else
      libexec.install "src"
      libexec.install "tools" if (buildpath/"tools").exist?
    end
    libexec.install "wasm" if (buildpath/"wasm").exist?
    libexec.install "examples" if (buildpath/"examples").exist?
    libexec.install "pyproject.toml" if (buildpath/"pyproject.toml").exist?
    libexec.install "requirements.txt" if (buildpath/"requirements.txt").exist?

    chmod 0755, libexec/"flow"
    chmod 0755, libexec/"flow-lsp" if (libexec/"flow-lsp").exist?
    # HEAD builds its Flow-native CLI from checked-in bootstrap C.
    system libexec/"flow", "version" if build.head?

    python = formula_opt_bin("python@3.12")/"python3.12"
    virtualenv_create(libexec/"venv", python)

    env = {
      PATH: "#{libexec}/venv/bin:#{formula_opt_libexec("python@3.12")}/bin:$PATH",
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
    # `flow compile` writes into libexec/build, which is read-only in the
    # test sandbox, so check that the installed CLI runs and reports its version.
    output = shell_output("#{bin}/flow version")
    if version.head?
      assert_match(/^Flow \d+\.\d+\.\d+/, output)
    else
      assert_match "Flow #{version}", output
    end
  end
end
