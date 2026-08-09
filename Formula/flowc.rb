# frozen_string_literal: true

# Homebrew formula for the self-hosted Flow compiler (Stage-A / flowc).
# Install:  brew install --formula ./Formula/flowc.rb
# Or after a tap: brew install flowc
#
# Builds from the checked-in bootstrap C — no Python on the compile path (#154).

class Flowc < Formula
  desc "Self-hosted Flow language compiler (Stage-A)"
  homepage "https://github.com/flooooooooooow/flow"
  license "MIT"
  head "https://github.com/flooooooooooow/flow.git", branch: "main"

  # Stable installs track GitHub release archives produced by flowc-release.yml
  # (tags flowc-v*). Until the first tagged release, use --HEAD.
  livecheck do
    url :stable
    regex(/^flowc[._-]v?(\d+(?:\.\d+)+)$/i)
  end

  depends_on "gcc" => :build if OS.linux?

  def install
    cc = ENV.cc || "cc"
    cflags = %w[-O2]
    system cc, *cflags, "compiler/bootstrap/flowc_stage_a.c", "-o", "flowc"
    bin.install "flowc"
  end

  test do
    (testpath/"hi.flow").write <<~FLOW
      function main() -> i32 {
          return 0
      }
    FLOW
    # Stage-A driver: compile to C then run via system cc when available.
    system "#{bin}/flowc", "--help"
  end
end
