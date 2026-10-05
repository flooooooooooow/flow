#!/usr/bin/env python3.12
"""DSP plots + real audio through modulating Schur-lattice all-pass."""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "build" / "plots" / "schur_lattice_allpass"
AUDIO_DIR = ROOT / "build" / "audio" / "lattice_allpass"
FIG_DIR = ROOT / "docs" / "research" / "schur_lattice_allpass" / "figures"

FS = 48000.0
POLES = np.array([0.5, 0.4, 0.3, 0.2])


def denom_mul_monic(d1: list[float], d2: list[float]) -> list[float]:
    o1, o2 = len(d1), len(d2)
    out = [0.0] * (o1 + o2)
    for k in range(1, o1 + o2 + 1):
        s = 0.0
        if k <= o2:
            s += d2[k - 1]
        if k <= o1:
            s += d1[k - 1]
        for i in range(1, o1 + 1):
            j = k - i
            if 1 <= j <= o2:
                s += d1[i - 1] * d2[j - 1]
        out[k - 1] = s
    return out


def design_from_poles(poles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    acc: list[float] = []
    for p in poles:
        one = [-float(p)]
        acc = one if not acc else denom_mul_monic(acc, one)
    a = np.array(acc, dtype=float)
    work = list(a)
    n = len(work)
    k = np.zeros(n)
    stage = n
    while stage > 0:
        idx = stage - 1
        kn = float(np.clip(work[idx], -0.999, 0.999))
        k[idx] = kn
        denom = 1.0 - kn * kn
        if stage > 1:
            for m in range(stage - 1):
                rev = stage - 2 - m
                work[m] = (work[m] - kn * work[rev]) / denom
        stage -= 1
    return k, a


def lattice_tick(
    k: np.ndarray, x_prev: np.ndarray, y_prev: np.ndarray, x: float
) -> tuple[float, np.ndarray, np.ndarray]:
    xp = x_prev.copy()
    yp = y_prev.copy()
    inp = x
    for i, ki in enumerate(k):
        y = ki * inp + xp[i] - ki * yp[i]
        xp[i] = inp
        yp[i] = y
        inp = y
    return inp, xp, yp


def process_block(
    x: np.ndarray,
    k_base: np.ndarray,
    *,
    mod_depth: float = 0.0,
    mod_rate_hz: float = 0.0,
    fs: float = FS,
) -> np.ndarray:
    n = len(k_base)
    xp = np.zeros(n)
    yp = np.zeros(n)
    phases = np.linspace(0.31, 4.65, n)
    y = np.zeros_like(x, dtype=np.float64)
    for i, xi in enumerate(x):
        if mod_depth > 0.0 and mod_rate_hz > 0.0:
            t = i / fs
            wobble = mod_depth * np.sin(2 * math.pi * mod_rate_hz * t + phases)
            k_t = np.clip(k_base + wobble, -0.999, 0.999)
        else:
            k_t = k_base
        yi, xp, yp = lattice_tick(k_t, xp, yp, float(xi))
        y[i] = yi
    return y


def tf_cascade(k: np.ndarray, z: np.ndarray) -> np.ndarray:
    h = np.ones_like(z, dtype=np.complex128)
    for ki in k:
        h *= (ki + z ** -1) / (1.0 + ki * z ** -1)
    return h


def make_test_audio(duration: float = 3.0, fs: float = FS) -> np.ndarray:
    n = int(duration * fs)
    t = np.arange(n) / fs
    x = np.zeros(n, dtype=np.float64)

    # Kick-like transient every 0.5 s
    for hit in np.arange(0, duration, 0.5):
        idx = int(hit * fs)
        length = int(0.08 * fs)
        env = np.exp(-np.linspace(0, 8, length))
        tone = np.sin(2 * math.pi * 80 * np.linspace(0, length / fs, length))
        end = min(idx + length, n)
        seg = length - (end - idx - idx)
        x[idx:end] += 0.7 * env[: end - idx] * tone[: end - idx]

    # Chord pad
    for f in [220.0, 277.18, 329.63]:
        x += 0.12 * np.sin(2 * math.pi * f * t)

    # Noise bursts (hi-hat-ish)
    for hit in np.arange(0.25, duration, 0.5):
        idx = int(hit * fs)
        length = int(0.03 * fs)
        end = min(idx + length, n)
        rng = np.random.default_rng(int(hit * 1000))
        burst = rng.standard_normal(end - idx)
        env = np.linspace(1, 0, end - idx)
        x[idx:end] += 0.25 * burst * env

    # Sweep for phase audibility
    f0, f1 = 200.0, 4000.0
    phase = 2 * math.pi * (f0 * t + 0.5 * (f1 - f0) * t * t / duration)
    x += 0.18 * np.sin(phase)

    peak = np.max(np.abs(x))
    return (0.9 * x / peak).astype(np.float64)


def write_wav(path: Path, data: np.ndarray, fs: float = FS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(data, -1.0, 1.0)
    pcm16 = (pcm * 32767.0).astype(np.int16)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(int(fs))
        wf.writeframes(pcm16.tobytes())


def sliding_rms(x: np.ndarray, win: int) -> np.ndarray:
    kernel = np.ones(win) / win
    return np.sqrt(np.convolve(x * x, kernel, mode="same"))


def plot_dsp(k: np.ndarray, a: np.ndarray) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    w = np.linspace(0, math.pi, 2048)
    z = np.exp(1j * w)
    h = tf_cascade(k, z)
    freqs = w * FS / (2 * math.pi)
    mag_db = 20 * np.log10(np.abs(h) + 1e-15)
    phase = np.unwrap(np.angle(h))
    group_delay = -np.gradient(phase, w) / FS

    # Pole-zero
    zeros, poles = [], []
    for ki in k:
        zeros.append(-1.0 / ki)
        poles.append(-ki)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("DSP Characterization: Schur–Lattice All-Pass", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ax.semilogx(freqs[1:], mag_db[1:], color="#d62728", lw=1.8)
    ax.axhline(0, color="k", ls="--", alpha=0.5)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_title("Bode magnitude — |H(f)| ≡ 0 dB")
    ax.set_ylim(-0.2, 0.2)
    ax.grid(True, which="both", alpha=0.3)

    ax = axes[0, 1]
    ax.semilogx(freqs[1:], np.degrees(phase[1:]), color="#2ca02c", lw=1.8)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Phase (degrees)")
    ax.set_title("Bode phase — frequency-dependent delay")
    ax.grid(True, which="both", alpha=0.3)

    ax = axes[1, 0]
    ax.semilogx(freqs[1:], group_delay[1:] * 1000, color="#9467bd", lw=1.8)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Group delay (ms)")
    ax.set_title("Group delay τ_g(f)")
    ax.grid(True, which="both", alpha=0.3)

    ax = axes[1, 1]
    theta = np.linspace(0, 2 * np.pi, 256)
    ax.plot(np.cos(theta), np.sin(theta), "k--", alpha=0.25, lw=1)
    ax.scatter(np.real(zeros), np.imag(zeros), marker="o", s=80, c="#1f77b4", label="zeros", zorder=3)
    ax.scatter(np.real(poles), np.imag(poles), marker="x", s=80, c="#ff7f0e", label="poles", zorder=3)
    ax.set_aspect("equal")
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_title("Pole–zero map (cascade sections)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "dsp_bode_pz_groupdelay.png", dpi=150)
    plt.close(fig)

    # Impulse + step
    n_imp = 256
    xp = np.zeros(len(k))
    yp = np.zeros(len(k))
    imp = np.zeros(n_imp)
    for i in range(n_imp):
        x = 1.0 if i == 0 else 0.0
        yi, xp, yp = lattice_tick(k, xp, yp, x)
        imp[i] = yi
    step = np.cumsum(imp)

    fig2, axes2 = plt.subplots(1, 2, figsize=(12, 4))
    axes2[0].stem(range(n_imp), imp, linefmt="#7b3294", markerfmt="o", basefmt=" ")
    axes2[0].set_title("Impulse response h[n]")
    axes2[0].set_xlabel("n")
    axes2[0].grid(True, alpha=0.3)
    axes2[1].plot(step, color="#17becf", lw=1.5)
    axes2[1].axhline(1.0, color="k", ls=":", alpha=0.5)
    axes2[1].set_title("Step response (all-pass → unit magnitude)")
    axes2[1].set_xlabel("n")
    axes2[1].grid(True, alpha=0.3)
    fig2.suptitle("Time-domain DSP verification", fontweight="bold")
    fig2.tight_layout()
    fig2.savefig(OUT_DIR / "dsp_impulse_step.png", dpi=150)
    plt.close(fig2)


def plot_audio(
    x: np.ndarray,
    y_static: np.ndarray,
    y_mod: np.ndarray,
    k: np.ndarray,
    fs: float = FS,
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t = np.arange(len(x)) / fs
    win = int(0.02 * fs)

    # Waveforms (first 1.2 s)
    n_show = int(1.2 * fs)
    fig, axes = plt.subplots(3, 1, figsize=(13, 8), sharex=True)
    fig.suptitle("Audio Through All-Pass: Input vs Static vs Modulated", fontweight="bold")
    axes[0].plot(t[:n_show], x[:n_show], color="#333", lw=0.8)
    axes[0].set_ylabel("Input")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(t[:n_show], y_static[:n_show], color="#1b9e77", lw=0.8)
    axes[1].set_ylabel("Static AP")
    axes[1].grid(True, alpha=0.3)
    axes[2].plot(t[:n_show], y_mod[:n_show], color="#d95f02", lw=0.8)
    axes[2].set_ylabel("Modulated AP")
    axes[2].set_xlabel("Time (s)")
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "audio_waveforms.png", dpi=150)
    plt.close(fig)

    # RMS envelope — proves energy preserved
    rms_in = sliding_rms(x, win)
    rms_st = sliding_rms(y_static, win)
    rms_md = sliding_rms(y_mod, win)
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(t, rms_in, label="Input RMS", color="#333", lw=1.2)
    ax2.plot(t, rms_st, label="Static all-pass RMS", color="#1b9e77", lw=1.2, alpha=0.85)
    ax2.plot(t, rms_md, label="Modulated all-pass RMS", color="#d95f02", lw=1.2, alpha=0.85)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("RMS amplitude")
    ax2.set_title("All-pass preserves energy envelope (RMS tracks)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT_DIR / "audio_rms_envelope.png", dpi=150)
    plt.close(fig2)

    # Spectrograms
    n_fft = 1024
    hop = 256
    fig3, axes3 = plt.subplots(1, 3, figsize=(15, 4))
    for ax, sig, title in zip(
        axes3,
        [x, y_static, y_mod],
        ["Input spectrogram", "Static all-pass", "Modulated all-pass (2 Hz k LFO)"],
    ):
        ax.specgram(sig, NFFT=n_fft, Fs=fs, noverlap=n_fft - hop, cmap="magma")
        ax.set_title(title)
        ax.set_ylabel("Hz")
    axes3[-1].set_xlabel("Time (s)")
    fig3.suptitle("Spectral content preserved — phase sculpting under modulation", fontweight="bold")
    fig3.tight_layout()
    fig3.savefig(OUT_DIR / "audio_spectrograms.png", dpi=150)
    plt.close(fig3)

    # Modulation proof: lag between input and output vs time
    block = int(0.05 * fs)
    lags_ms = []
    times = []
    for start in range(0, len(x) - block, block):
        seg_x = x[start : start + block]
        seg_y = y_mod[start : start + block]
        c = np.correlate(seg_y, seg_x, mode="full")
        lag = np.argmax(c) - (block - 1)
        lags_ms.append(lag / fs * 1000)
        times.append(start / fs)
    fig4, axes4 = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    axes4[0].plot(times, lags_ms, color="#7570b3", lw=1.5)
    axes4[0].set_ylabel("Cross-corr lag (ms)")
    axes4[0].set_title("Modulation moves phase delay in real time")
    axes4[0].grid(True, alpha=0.3)
    # k trajectory during audio
    phases = np.linspace(0.31, 4.65, len(k))
    k1 = []
    for i in range(len(x)):
        tt = i / fs
        k1.append(np.clip(k[0] + 0.15 * math.sin(2 * math.pi * 2.0 * tt + phases[0]), -0.999, 0.999))
    # downsample for plot
    ds = int(fs / 200)
    axes4[1].plot(t[::ds], np.array(k1)[::ds], color="#e7298a", lw=1.2)
    axes4[1].set_xlabel("Time (s)")
    axes4[1].set_ylabel("k₁(t)")
    axes4[1].set_title("Reflection LFO (2 Hz) driving phase engine")
    axes4[1].grid(True, alpha=0.3)
    fig4.tight_layout()
    fig4.savefig(OUT_DIR / "audio_modulation_proof.png", dpi=150)
    plt.close(fig4)

    # Difference signals (should be phase-only, not amplitude loss)
    diff_st = y_static - x
    diff_md = y_mod - x
    fig5, axes5 = plt.subplots(2, 1, figsize=(12, 5), sharex=True)
    n_d = int(0.8 * fs)
    axes5[0].plot(t[:n_d], diff_st[:n_d], color="#1b9e77", lw=0.7)
    axes5[0].set_ylabel("y − x")
    axes5[0].set_title("Static: difference waveform (phase offset, not gain loss)")
    axes5[0].grid(True, alpha=0.3)
    axes5[1].plot(t[:n_d], diff_md[:n_d], color="#d95f02", lw=0.7)
    axes5[1].set_ylabel("y − x")
    axes5[1].set_xlabel("Time (s)")
    axes5[1].set_title("Modulated: difference evolves as k(t) moves")
    axes5[1].grid(True, alpha=0.3)
    fig5.tight_layout()
    fig5.savefig(OUT_DIR / "audio_phase_difference.png", dpi=150)
    plt.close(fig5)


def copy_outputs() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for p in OUT_DIR.glob("dsp_*.png"):
        (FIG_DIR / p.name).write_bytes(p.read_bytes())
    for p in OUT_DIR.glob("audio_*.png"):
        (FIG_DIR / p.name).write_bytes(p.read_bytes())


def main() -> int:
    k, a = design_from_poles(POLES)
    print(f"Schur reflections k = {k}")

    plot_dsp(k, a)

    x = make_test_audio(duration=3.0)
    y_static = process_block(x, k)
    y_mod = process_block(x, k, mod_depth=0.15, mod_rate_hz=2.0)

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    write_wav(AUDIO_DIR / "input.wav", x)
    write_wav(AUDIO_DIR / "output_static_allpass.wav", y_static)
    write_wav(AUDIO_DIR / "output_modulated_allpass.wav", y_mod)

    rms_in = float(np.sqrt(np.mean(x * x)))
    rms_st = float(np.sqrt(np.mean(y_static * y_static)))
    rms_md = float(np.sqrt(np.mean(y_mod * y_mod)))
    print(f"RMS  in={rms_in:.4f}  static={rms_st:.4f}  mod={rms_md:.4f}")
    print(f"RMS ratio static={rms_st/rms_in:.4f}  mod={rms_md/rms_in:.4f}")

    plot_audio(x, y_static, y_mod, k)
    copy_outputs()

    print(f"\nWAV files: {AUDIO_DIR}/")
    for w in sorted(AUDIO_DIR.glob("*.wav")):
        print(f"  {w}")

    print(f"\nDSP + audio plots: {OUT_DIR}/")
    for p in sorted(OUT_DIR.glob("dsp_*.png")) + sorted(OUT_DIR.glob("audio_*.png")):
        print(f"  {p}")

    # Open key outputs on macOS
    key_plots = [
        OUT_DIR / "dsp_bode_pz_groupdelay.png",
        OUT_DIR / "audio_waveforms.png",
        OUT_DIR / "audio_modulation_proof.png",
    ]
    subprocess.run(["open", *[str(p) for p in key_plots]], check=False)
    subprocess.run(["open", str(AUDIO_DIR / "output_modulated_allpass.wav")], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())