# frozen_string_literal: true

# Homebrew formula for the self-hosted Flow compiler (Stage-A / flowc).
#   brew install --formula ./Formula/flowc.rb
#   brew install --HEAD --formula ./Formula/flowc.rb
#
# Stable archives come from flowc-release.yml (tag flowc-v*). #154

class Flowc < Formula
  desc "Self-hosted Flow language compiler (Stage-A)"
  homepage "https://github.com/flooooooooooow/flow"
  license "MIT"
  url "https://github.com/flooooooooooow/flow/releases/download/flowc-v0.10.0/flowc-flowc-v0.10.0-darwin-arm64.tar.gz"
  version "0.10.0"
  # sha256 filled per-platform via on_macos / on_linux blocks below; head builds from git.
  head "https://github.com/flooooooooooow/flow.git", branch: "main"

  livecheck do
    url :stable
    regex(/flowc-v?(\d+(?:\.\d+)+)/i)
  end

  on_macos do
    on_arm do
      url "https://github.com/flooooooooooow/flow/releases/download/flowc-v0.10.0/flowc-flowc-v0.10.0-darwin-arm64.tar.gz"
      sha256 :no_check # release CI publishes .sha256 alongside; brew audit can pin later
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/flooooooooooow/flow/releases/download/flowc-v0.10.0/flowc-flowc-v0.10.0-linux-x86_64.tar.gz"
      sha256 :no_check
    end
  end

  def install
    if build.head?
      cc = ENV.cc || "cc"
      system cc, "-O2", "compiler/bootstrap/flowc_stage_a.c", "-o", "flowc"
      bin.install "flowc"
    else
      bin.install "bin/flowc"
    end
  end

  test do
    system "#{bin}/flowc", "--help"
  end
end
