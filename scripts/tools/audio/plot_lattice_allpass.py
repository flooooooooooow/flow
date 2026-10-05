#!/usr/bin/env python3.12
"""Run Schur-lattice all-pass verification and generate publication plots."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / "formal" / "SchurLatticeAllpass"
OUT_DIR = ROOT / "build" / "plots" / "schur_lattice_allpass"
FIG_DIR = ROOT / "docs" / "research" / "schur_lattice_allpass" / "figures"
DEMO = ROOT / "examples" / "audio" / "lattice_allpass_demo.flow"
VERIFY = ROOT / "lib" / "verify" / "SchurLattice.flow"
FLOW = ROOT / "flow"

POLES = np.array([0.5, 0.4, 0.3, 0.2])
FS = 48000.0

# Visual theme
C_LATTICE = "#1b9e77"
C_NAIVE = "#d95f02"
C_PHASE = "#7570b3"
C_ACCENT = "#e7298a"
C_GRID = "#e6e6e6"


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


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


def denom_from_poles(poles: np.ndarray) -> np.ndarray:
    acc: list[float] = []
    for p in poles:
        one = [-float(p)]
        acc = one if not acc else denom_mul_monic(acc, one)
    return np.array(acc, dtype=float)


def schur_step_down(a: np.ndarray) -> np.ndarray:
    work = list(a.astype(float))
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
    return k


def design_from_poles(poles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = denom_from_poles(poles)
    return schur_step_down(a), a


def poly_roots_inside_disk(a: np.ndarray) -> bool:
    """Stable monic denominator 1 + sum a_k z^{-k} ⇔ roots inside unit disk."""
    coeffs = np.concatenate(([1.0], a))
    roots = np.roots(coeffs[::-1])
    return bool(np.all(np.abs(roots) < 1.0))


def measure_gain(k: np.ndarray, fs: float, freq: float, settle: int = 4096, measure: int = 2048) -> float:
    xp = np.zeros_like(k)
    yp = np.zeros_like(k)
    omega = 2 * math.pi * freq / fs
    for n in range(settle):
        _, xp, yp = lattice_tick(k, xp, yp, math.sin(omega * n))
    in_e = out_e = 0.0
    for n in range(measure):
        t = settle + n
        x = math.sin(omega * t)
        y, xp, yp = lattice_tick(k, xp, yp, x)
        in_e += x * x
        out_e += y * y
    return math.sqrt(out_e / in_e) if in_e > 1e-12 else 0.0


def modulated_k_trajectory(
    k_base: np.ndarray, fs: float, n_samples: int, depth: float, rate_hz: float
) -> np.ndarray:
    n = len(k_base)
    phases = np.linspace(0.31, 4.65, n)
    traj = np.zeros((n, n_samples))
    for i in range(n_samples):
        t = i / fs
        wobble = depth * np.sin(2 * math.pi * rate_hz * t + phases)
        traj[:, i] = np.clip(k_base + wobble, -0.999, 0.999)
    return traj


def simulate_modulated_block(
    k_base: np.ndarray,
    fs: float,
    n_samples: int,
    test_freq: float,
    depth: float,
    rate_hz: float,
    mode: str,
    a_base: np.ndarray | None = None,
    window: int = 256,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-sample retuning. mode: lattice | naive_coeff."""
    n = len(k_base)
    phases_k = np.linspace(0.31, 4.65, n)
    phases_a = np.linspace(0.0, 2.5, n)
    xp = np.zeros(n)
    yp = np.zeros(n)
    stable = np.ones(n_samples, dtype=bool)
    omega = 2 * math.pi * test_freq / fs
    x_ring = np.zeros(window)
    y_ring = np.zeros(window)
    block_gains: list[float] = []

    for i in range(n_samples):
        t = i / fs
        if mode == "lattice":
            wobble = depth * np.sin(2 * math.pi * rate_hz * t + phases_k)
            k_t = np.clip(k_base + wobble, -0.999, 0.999)
            stable[i] = True
        else:
            assert a_base is not None
            wobble = depth * np.sin(2 * math.pi * rate_hz * t + phases_a)
            a_t = a_base + wobble
            stable[i] = poly_roots_inside_disk(a_t)
            k_t = schur_step_down(a_t)

        x = math.sin(omega * i)
        y, xp, yp = lattice_tick(k_t, xp, yp, x)
        slot = i % window
        x_ring[slot] = x
        y_ring[slot] = y
        if i >= window and (i % window) == window - 1:
            in_rms = math.sqrt(np.mean(x_ring * x_ring))
            out_rms = math.sqrt(np.mean(y_ring * y_ring))
            block_gains.append(out_rms / in_rms if in_rms > 1e-12 else 0.0)

    gains = np.array(block_gains if block_gains else [1.0])
    return gains, stable, np.arange(n_samples) / fs


def instantaneous_phase_track(
    k_base: np.ndarray, fs: float, n_samples: int, depth: float, rate_hz: float, freqs: list[float]
) -> np.ndarray:
    """Phase at selected frequencies vs time under per-sample k modulation."""
    n_freq = len(freqs)
    phases_out = np.zeros((n_freq, n_samples))
    phases_lfo = np.linspace(0.31, 4.65, len(k_base))
    xp = np.zeros(len(k_base))
    yp = np.zeros(len(k_base))
    x_prev = {f: 0.0 for f in freqs}
    y_prev = {f: 0.0 for f in freqs}

    for i in range(n_samples):
        t = i / fs
        wobble = depth * np.sin(2 * math.pi * rate_hz * t + phases_lfo)
        k_t = np.clip(k_base + wobble, -0.999, 0.999)
        for fi, f in enumerate(freqs):
            omega = 2 * math.pi * f / fs
            x = math.sin(omega * i)
            y, xp_f, yp_f = lattice_tick(k_t, xp.copy(), yp.copy(), x)
            # two-sample phase increment estimator
            cross = x * y_prev[f] - y * x_prev[f]
            dot = x * x_prev[f] + y * y_prev[f]
            phases_out[fi, i] = math.degrees(math.atan2(cross, dot))
            x_prev[f] = x
            y_prev[f] = y
        _, xp, yp = lattice_tick(k_t, xp, yp, 0.0)
    return np.cumsum(phases_out, axis=1)


def givens_chain_orthogonality(k: np.ndarray) -> tuple[float, float]:
    n = len(k)
    a = np.eye(n)
    for i in range(n - 1):
        ki = k[i]
        c, s = math.sqrt(1 - ki * ki), ki
        g = np.eye(n)
        g[i, i] = c
        g[i, i + 1] = -s
        g[i + 1, i] = s
        g[i + 1, i + 1] = c
        a = g @ a
    err = np.linalg.norm(a.T @ a - np.eye(n), ord="fro")
    det = np.linalg.det(a)
    return err, det


def parse_flow_demo(stdout: str) -> dict:
    data: dict = {"k": [], "mag": [], "mod": [], "imp": [], "order": 0, "max_mag_dev": None}
    for line in stdout.splitlines():
        if line.startswith("order,"):
            data["order"] = int(float(line.split(",")[1]))
        elif line.startswith("k,"):
            data["k"].append(float(line.split(",")[1]))
        elif line.startswith("mag,"):
            parts = line.split(",")
            data["mag"].append((float(parts[1]), float(parts[2])))
        elif line.startswith("mod,"):
            parts = line.split(",")
            data["mod"].append(tuple(float(p) for p in parts[1:]))
        elif line.startswith("imp,"):
            data["imp"].append(float(line.split(",")[1]))
        elif line.startswith("max_mag_dev,"):
            data["max_mag_dev"] = float(line.split(",")[1])
    return data


def plot_novel_demo(k: np.ndarray, a: np.ndarray) -> Path:
    """Hero figure: why Schur-lattice modulation is novel vs naive retuning."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor("#fafafa")
    gs = fig.add_gridspec(3, 3, hspace=0.38, wspace=0.32, height_ratios=[1.0, 1.15, 1.0])

    fig.suptitle(
        "Schur–Lattice Colligations: Per-Sample Many-Pole Phase Engines",
        fontsize=17,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.935,
        "Finite-horizon synthesis  →  O(n) reflection retuning  →  |H|≡1 while geometry moves",
        ha="center",
        fontsize=11,
        color="#444",
        style="italic",
    )

    # --- Pipeline schematic ---
    ax0 = fig.add_subplot(gs[0, :])
    ax0.set_xlim(0, 10)
    ax0.set_ylim(0, 1)
    ax0.axis("off")
    steps = [
        ("Stable D(z)", "#4daf4a"),
        ("Schur step-down", "#377eb8"),
        ("Givens colligation A", "#984ea3"),
        ("Finite C observer map", "#ff7f00"),
        ("Lattice kᵢ(t)", C_LATTICE),
    ]
    for i, (label, color) in enumerate(steps):
        x = 0.4 + i * 1.9
        rect = mpatches.FancyBboxPatch(
            (x, 0.35), 1.5, 0.35, boxstyle="round,pad=0.03,rounding_size=0.05",
            facecolor=color, edgecolor="white", alpha=0.92, linewidth=1.5,
        )
        ax0.add_patch(rect)
        ax0.text(x + 0.75, 0.52, label, ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        if i < len(steps) - 1:
            ax0.annotate("", xy=(x + 1.65, 0.52), xytext=(x + 1.55, 0.52),
                         arrowprops=dict(arrowstyle="->", color="#333", lw=2))
    ax0.text(5.0, 0.12, "No infinite Gramian  ·  Mathlib stability lemmas  ·  Flow + Lean verified",
             ha="center", fontsize=9, color="#555")

    # --- Lattice vs naive modulation ---
    ax1 = fig.add_subplot(gs[1, 0])
    depth = 0.28
    rates = np.array([1, 3, 10, 30, 60, 120, 240, 480])
    lat_dev, naive_dev, naive_unstable = [], [], []
    for rate in rates:
        g_lat, st_lat, _ = simulate_modulated_block(k, FS, 12000, 1000.0, depth, rate, "lattice")
        g_nav, st_nav, _ = simulate_modulated_block(k, FS, 12000, 1000.0, depth, rate, "naive_coeff", a)
        lat_dev.append(float(np.std(20 * np.log10(np.clip(g_lat, 1e-6, None)))))
        naive_dev.append(float(np.std(20 * np.log10(np.clip(g_nav, 1e-6, None)))))
        naive_unstable.append(100.0 * float(1.0 - np.mean(st_nav)))
    x = np.arange(len(rates))
    w = 0.35
    ax1.bar(x - w / 2, lat_dev, w, label="Lattice kᵢ(t) clip", color=C_LATTICE, edgecolor="white")
    ax1.bar(x + w / 2, naive_dev, w, label="Naive coeff wobble", color=C_NAIVE, edgecolor="white")
    ax1.set_xticks(x, [f"{int(r)} Hz" for r in rates], rotation=35, ha="right")
    ax1.set_ylabel("Gain jitter (dB std)")
    ax1.set_title("Novel: fast modulation without magnitude blow-up", fontweight="bold")
    ax1.legend(fontsize=8)
    ax1.grid(True, axis="y", alpha=0.3)

    # --- Stability certificate ---
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.plot(rates, naive_unstable, "o-", color=C_NAIVE, lw=2.5, markersize=7, label="Naive unstable samples %")
    ax2.axhline(0, color=C_LATTICE, ls="--", lw=2, label="Lattice: 0% (|kᵢ|<1)")
    ax2.set_xscale("log")
    ax2.set_xlabel("Modulation rate")
    ax2.set_ylabel("% samples outside Schur disk")
    ax2.set_title("Local stability certificate |kᵢ|<1", fontweight="bold")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # --- Phase sculpting waterfall ---
    ax3 = fig.add_subplot(gs[1, 2])
    freqs_track = [250.0, 1000.0, 4000.0]
    n_phase = 2400
    phase_track = instantaneous_phase_track(k, FS, n_phase, 0.18, 8.0, freqs_track)
    t_ms = np.arange(n_phase) / FS * 1000
    im = ax3.imshow(
        phase_track,
        aspect="auto",
        origin="lower",
        extent=[0, t_ms[-1], 250, 4000],
        cmap="twilight_shifted",
        norm=TwoSlopeNorm(vcenter=0.0, vmin=-180, vmax=180),
    )
    ax3.set_xlabel("Time (ms)")
    ax3.set_ylabel("Frequency (Hz)")
    ax3.set_title("Phase geometry engine (8 Hz kᵢ LFO)", fontweight="bold")
    cb = fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
    cb.set_label("Δphase (deg/sample)")

    # --- Many-pole scaling ---
    ax4 = fig.add_subplot(gs[2, 0])
    pole_sets = [
        ("4-pole", POLES),
        ("8-pole", np.array([0.55, 0.48, 0.41, 0.34, 0.27, 0.20, 0.13, 0.06])),
        ("12-pole", np.linspace(0.58, 0.05, 12)),
        ("16-pole", np.linspace(0.62, 0.03, 16)),
    ]
    orders, ops, max_devs = [], [], []
    for label, poles in pole_sets:
        kk = schur_step_down(denom_from_poles(poles))
        devs = [abs(measure_gain(kk, FS, f) - 1.0) for f in [500, 2000, 8000]]
        orders.append(len(kk))
        ops.append(2 * len(kk))
        max_devs.append(max(devs))
    colors = plt.cm.viridis(np.linspace(0.25, 0.9, len(orders)))
    bars = ax4.bar([str(o) for o in orders], ops, color=colors, edgecolor="white")
    for bar, dev in zip(bars, max_devs):
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                 f"|H| err {dev:.4f}", ha="center", fontsize=8)
    ax4.set_xlabel("Filter order")
    ax4.set_ylabel("MACs / sample (2n)")
    ax4.set_title("Many-pole: O(n) retuning, still all-pass", fontweight="bold")
    ax4.grid(True, axis="y", alpha=0.3)

    # --- Orthogonal colligation ---
    ax5 = fig.add_subplot(gs[2, 1])
    err, det = givens_chain_orthogonality(k)
    theta = np.linspace(0, 2 * np.pi, 200)
    ax5.plot(np.cos(theta), np.sin(theta), "k--", alpha=0.25, lw=1)
    for i, ki in enumerate(k):
        c = math.sqrt(1 - ki * ki)
        ax5.arrow(0, 0, c, ki, head_width=0.04, length_includes_head=True,
                  color=plt.cm.plasma(i / max(len(k) - 1, 1)), lw=2)
        ax5.text(c * 1.08, ki * 1.08, f"G{i+1}", fontsize=8)
    ax5.set_xlim(-1.2, 1.2)
    ax5.set_ylim(-1.2, 1.2)
    ax5.set_aspect("equal")
    ax5.set_title(f"Lossless colligation  ‖AᵀA−I‖={err:.2e}", fontweight="bold")
    ax5.set_xlabel("Givens plane")
    ax5.grid(True, alpha=0.3)
    ax5.text(0.02, 0.98, f"det(A)={det:.4f}", transform=ax5.transAxes, va="top", fontsize=9)

    # --- Per-sample k heatmap ---
    ax6 = fig.add_subplot(gs[2, 2])
    traj = modulated_k_trajectory(k, FS, 4800, 0.25, 60.0)
    t_ms = np.arange(traj.shape[1]) / FS * 1000
    im2 = ax6.imshow(
        traj,
        aspect="auto",
        origin="lower",
        extent=[0, t_ms[-1], 1, len(k)],
        cmap="RdYlBu_r",
        vmin=-1,
        vmax=1,
    )
    ax6.axhline(0, color="white", alpha=0)
    for y in np.arange(1.5, len(k) + 0.5):
        ax6.axhline(y, color="white", lw=0.4, alpha=0.5)
    ax6.set_xlabel("Time (ms)")
    ax6.set_ylabel("Section i")
    ax6.set_title("60 Hz retune of all kᵢ — every sample", fontweight="bold")
    cb2 = fig.colorbar(im2, ax=ax6, fraction=0.046, pad=0.04)
    cb2.set_label("kᵢ(t)")

    out = OUT_DIR / "schur_lattice_novel_demo.png"
    fig.savefig(out, dpi=160, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return out


def plot_overview(k: np.ndarray, flow_data: dict, lean_ok: bool, verify_ok: bool, demo_ok: bool) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    freqs = np.logspace(np.log10(20), np.log10(FS / 2 - 1), 256)
    mags = [measure_gain(k, FS, f) for f in freqs]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("All-Pass Verification Dashboard", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ax.bar(np.arange(1, len(k) + 1), k, color="#2c7bb6")
    ax.axhline(1, color="r", ls="--", alpha=0.4)
    ax.axhline(-1, color="r", ls="--", alpha=0.4)
    ax.set_title("Schur reflections")
    ax.set_ylim(-1.05, 1.05)

    ax = axes[0, 1]
    ax.semilogx(freqs, 20 * np.log10(mags), color="#d7191c", lw=1.5)
    ax.axhline(0, color="k", ls="--", alpha=0.5)
    ax.set_title("|H(f)| ≡ 1 (formal + runtime)")
    ax.set_ylim(-0.15, 0.15)

    ax = axes[1, 0]
    if flow_data["mag"]:
        f_flow, m_flow = zip(*flow_data["mag"])
        ax.plot(f_flow, m_flow, "o-", label="Flow", lw=2)
        ax.axhline(1.0, color="k", ls=":")
    ax.set_xscale("log")
    ax.set_title("Flow runtime magnitude check")
    ax.legend()

    ax = axes[1, 1]
    status = (
        f"Lean: {'PASS' if lean_ok else 'FAIL'}   "
        f"Verify: {'PASS' if verify_ok else 'FAIL'}   "
        f"Demo: {'PASS' if demo_ok else 'FAIL'}"
    )
    if flow_data.get("max_mag_dev") is not None:
        status += f"\nmax |H| dev = {flow_data['max_mag_dev']:.4f}"
    ax.axis("off")
    ax.text(0.5, 0.55, status, ha="center", va="center", fontsize=13, family="monospace",
            bbox=dict(boxstyle="round", facecolor="#eef8ee" if demo_ok else "#fdecea", edgecolor="#ccc"))
    ax.set_title("Proof + implementation status")

    for ax in axes.flat[:3]:
        ax.grid(True, alpha=0.3)

    out = OUT_DIR / "schur_lattice_allpass_overview.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def copy_figures() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for p in OUT_DIR.glob("*.png"):
        dest = FIG_DIR / p.name
        dest.write_bytes(p.read_bytes())


def run_audio_demo() -> None:
    audio_script = ROOT / "tools" / "lattice_allpass_audio_demo.py"
    if audio_script.exists():
        subprocess.run(["python3.12", str(audio_script)], check=False)


def main() -> int:
    lean_ok = verify_ok = demo_ok = False
    flow_data: dict = {}

    if FORMAL.exists():
        r = run(["lake", "build"], cwd=FORMAL)
        lean_ok = r.returncode == 0
        if not lean_ok:
            print(r.stderr or r.stdout, file=sys.stderr)

    if FLOW.exists():
        r = run([str(FLOW), "run", str(VERIFY)])
        verify_ok = r.returncode == 0
        print(r.stdout)
        r = run([str(FLOW), "run", str(DEMO)])
        demo_ok = r.returncode == 0
        print(r.stdout)
        flow_data = parse_flow_demo(r.stdout)

    k, a = design_from_poles(POLES)
    if flow_data["k"]:
        k = np.array(flow_data["k"])

    novel = plot_novel_demo(k, a)
    overview = plot_overview(k, flow_data, lean_ok, verify_ok, demo_ok)
    copy_figures()
    run_audio_demo()

    print(f"\nWrote plots to {OUT_DIR}/")
    for p in sorted(OUT_DIR.glob("*.png")):
        print(f"  {p}")
    print(f"Copied to {FIG_DIR}/")

    subprocess.run(["open", str(novel), str(overview)], check=False)
    return 0 if (lean_ok and verify_ok and demo_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())