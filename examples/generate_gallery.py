#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "matplotlib>=3.5.0",
#     "numpy>=1.20.0",
# ]
# ///
"""Generate publication-ready showcase gallery for maniplot (IEEE & Chinese Master's Thesis)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import maniplot as mplt

GALLERY_DIR = Path(__file__).resolve().parent / "gallery"


def make_fig1_ieee_force_pose_phases() -> None:
    """Figure 1: IEEE Single-Column Contact-Rich Peg-in-Hole Pose & Force Tracking with Phases."""
    mplt.use_style("ieee")
    rng = np.random.default_rng(42)
    t = np.linspace(0.0, 6.0, 600)

    # Simulate 4-phase Peg-in-Hole compliant manipulation
    ex = 18.0 * np.exp(-1.4 * t) + 1.2 * np.exp(-0.5 * (t - 2.0) ** 2 / 0.08) * np.sin(9 * t)
    ey = -12.0 * np.exp(-1.6 * t) + 0.9 * np.exp(-0.5 * (t - 2.1) ** 2 / 0.08) * np.cos(8 * t)
    ez = np.piecewise(
        t,
        [t < 1.5, (t >= 1.5) & (t < 2.6), (t >= 2.6) & (t < 4.8), t >= 4.8],
        [
            lambda x: 45.0 * np.exp(-1.8 * x),
            lambda x: 3.0 + 0.5 * np.sin(6 * x),
            lambda x: 3.0 * np.exp(-1.5 * (x - 2.6)),
            lambda x: 0.12 * np.sin(4 * x),
        ],
    )

    # Contact force Fz (desired = 12 N during contact/insertion)
    fz_des = np.where((t >= 1.5) & (t < 4.8), 12.0, 0.0)
    fz_ours = np.zeros_like(t)
    fz_base = np.zeros_like(t)
    for i, ti in enumerate(t):
        if 1.5 <= ti < 4.8:
            tau = ti - 1.5
            fz_ours[i] = 12.0 * (1.0 - np.exp(-7.0 * tau)) + 2.2 * np.exp(-4.5 * tau) * np.sin(18 * tau)
            fz_base[i] = 12.0 * (1.0 - np.exp(-5.0 * tau)) + 8.8 * np.exp(-2.2 * tau) * np.sin(15 * tau)
        elif ti >= 4.8:
            tau = ti - 4.8
            fz_ours[i] = 12.0 * np.exp(-8.0 * tau)
            fz_base[i] = 12.0 * np.exp(-4.5 * tau)
    fz_ours += rng.normal(0, 0.18, size=t.shape)
    fz_base += rng.normal(0, 0.25, size=t.shape)

    fig, axes = mplt.subplots(nrows=2, ncols=1, layout="ieee_single", height=3.15, sharex=True)

    # Panel (a): 3D Cartesian Position Error
    axes[0].plot(t, ex, color=mplt.XYZ_COLORS["x"], label="$e_x$")
    axes[0].plot(t, ey, color=mplt.XYZ_COLORS["y"], label="$e_y$")
    axes[0].plot(t, ez, color=mplt.XYZ_COLORS["z"], label="$e_z$")
    axes[0].axhline(0.0, color="#64748B", linestyle=":", linewidth=0.6)
    axes[0].set_ylabel("Pos. Error (mm)")
    axes[0].set_ylim(-18, 54)
    axes[0].legend(loc="upper right", bbox_to_anchor=(0.99, 0.78), ncol=3, columnspacing=0.8)

    # Panel (b): Normal Contact Force Tracking
    axes[1].plot(t, fz_des, color=mplt.SEMANTIC_COLORS["reference"], linestyle="--", linewidth=1.0, label="Desired $F_d$")
    axes[1].plot(t, fz_base, color="#64748B", alpha=0.85, linewidth=1.05, label="PD Impedance")
    axes[1].plot(t, fz_ours, color=mplt.SEMANTIC_COLORS["ours"], linewidth=1.35, label="Ours (Adaptive)")
    axes[1].axhline(18.0, color=mplt.SEMANTIC_COLORS["limit"], linestyle="-.", linewidth=0.8, label="Safety Limit")
    axes[1].set_xlabel("Time $t$ (s)")
    axes[1].set_ylabel("Force $F_z$ (N)")
    axes[1].set_ylim(-2, 27)
    axes[1].legend(loc="upper right", ncol=2, columnspacing=0.7)

    phases = [
        (0.0, 1.5, "Approach"),
        (1.5, 2.6, "Contact"),
        (2.6, 4.8, "Insertion"),
        (4.8, 6.0, "Release"),
    ]
    mplt.add_task_phases(axes, phases, label_y=0.95)
    mplt.add_panel_labels(axes, loc=(-0.16, 1.03))

    mplt.savefig(fig, GALLERY_DIR / "fig1_ieee_force_pose_phases")
    plt.close(fig)


def make_fig2_ieee_double_overview() -> None:
    """Figure 2: IEEE Double-Column (7.16 in) 3-Panel Manipulation Benchmark & 3D Trajectory."""
    mplt.use_style("ieee")
    rng = np.random.default_rng(7)

    fig = plt.figure(figsize=mplt.get_figsize("ieee_double", height=2.35), constrained_layout=True)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.15, 1.05])
    ax_ci = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])
    ax_3d = fig.add_subplot(gs[0, 2], projection="3d")

    # (a) Multi-seed Policy / Controller Learning Curves
    steps = np.linspace(0, 100, 80)
    ours_seeds = 92.0 * (1.0 - np.exp(-steps / 18.0))[None, :] + rng.normal(0, 3.2, (8, len(steps)))
    dp_seeds = 78.0 * (1.0 - np.exp(-steps / 26.0))[None, :] + rng.normal(0, 4.5, (8, len(steps)))
    act_seeds = 68.0 * (1.0 - np.exp(-steps / 30.0))[None, :] + rng.normal(0, 5.0, (8, len(steps)))
    mplt.plot_ci_curves(
        ax_ci,
        steps,
        {
            "Ours": np.clip(ours_seeds, 0, 100),
            "Diffusion Policy": np.clip(dp_seeds, 0, 100),
            "ACT Baseline": np.clip(act_seeds, 0, 100),
        },
        ci_mode="std",
        smooth_window=3,
        highlight="Ours",
        xlabel="Training Rollouts",
        ylabel="Success Rate (%)",
    )
    ax_ci.set_ylim(0, 105)
    ax_ci.set_title("(a) Sample Efficiency", loc="left", pad=4)
    ax_ci.legend(loc="lower right")

    # (b) Multi-Task Manipulation Benchmark Bar Chart
    tasks = ["Peg-Insert", "Dual-Lift", "Wiping", "Drawer"]
    scores = {
        "ACT": [65, 70, 75, 80],
        "Diffusion": [75, 78, 82, 85],
        "Ours": [94, 92, 96, 95],
    }
    errors = {
        "ACT": [5.5, 6.0, 4.5, 4.0],
        "Diffusion": [4.5, 4.8, 3.8, 3.5],
        "Ours": [2.5, 3.0, 2.0, 2.2],
    }
    mplt.plot_benchmark_bars(
        ax_bar,
        tasks,
        scores,
        errors,
        highlight_method="Ours",
        ylabel="Success Rate (%)",
        ylim=(0, 126),
    )
    ax_bar.set_yticks([0, 20, 40, 60, 80, 100])
    ax_bar.set_title("(b) Real-World Task Benchmark", loc="left", pad=4)
    ax_bar.legend(loc="upper center", ncol=3, columnspacing=0.8)

    # (c) 3D End-Effector Trajectory with 6-DoF Triads
    s = np.linspace(0, 1, 100)
    ref_traj = np.column_stack([
        0.35 + 0.22 * s,
        -0.18 + 0.36 * s + 0.05 * np.sin(np.pi * s),
        0.12 + 0.18 * np.sin(np.pi * s),
    ])
    actual_traj = ref_traj + np.column_stack([
        0.008 * np.sin(3 * np.pi * s) * (1 - s),
        -0.010 * np.sin(2 * np.pi * s) * (1 - s),
        0.007 * np.cos(2 * np.pi * s) * (1 - s),
    ])
    rots = np.zeros((len(s), 3, 3))
    for k, si in enumerate(s):
        ang = 0.6 * si
        c, sn = np.cos(ang), np.sin(ang)
        rots[k] = np.array([[c, -sn, 0], [sn, c, 0], [0, 0, 1]])

    mplt.plot_3d_trajectory(
        ax_3d,
        {"Ours (Actual)": actual_traj},
        reference=ref_traj,
        rotation_matrices=rots,
        triad_step=22,
        triad_scale=0.032,
        project_xy_z=0.06,
    )
    ax_3d.set_xlabel("$X$ (m)", labelpad=-2)
    ax_3d.set_ylabel("$Y$ (m)", labelpad=-2)
    ax_3d.set_zlabel("$Z$ (m)", labelpad=-2)
    ax_3d.set_zlim(0.06, 0.34)
    ax_3d.view_init(elev=24, azim=-52)
    ax_3d.set_title("(c) 3D EE Trajectory & Frames", loc="left", pad=2)
    ax_3d.legend(loc="upper left", fontsize=6.5)

    mplt.savefig(fig, GALLERY_DIR / "fig2_ieee_double_overview")
    plt.close(fig)


def make_fig3_cn_thesis_bimanual() -> None:
    """Figure 3: Chinese Master's Thesis Standard (宋体 + Times New Roman + STIX 公式混排)."""
    mplt.use_style("cn_thesis")
    t = np.linspace(0.0, 5.0, 500)

    # Panel (a): Dual-arm relative synchronization error ||e_sync||_2 (mm)
    err_trad = 8.5 * np.exp(-0.9 * t) + 2.4 * np.exp(-0.5 * (t - 1.8) ** 2 / 0.06) + 0.35 * np.sin(10 * t)
    err_ours = 8.5 * np.exp(-2.1 * t) + 0.65 * np.exp(-0.5 * (t - 1.8) ** 2 / 0.05) + 0.10 * np.sin(10 * t)

    # Panel (b): Internal squeeze force F_int (N)
    f_ref = np.where(t >= 1.0, 15.0, 0.0)
    f_trad = np.where(t >= 1.0, 15.0 * (1 - np.exp(-4.0 * (t - 1.0))) + 4.8 * np.exp(-1.8 * (t - 1.0)) * np.sin(14 * t), 0.0)
    f_ours = np.where(t >= 1.0, 15.0 * (1 - np.exp(-6.5 * (t - 1.0))) + 0.9 * np.exp(-3.5 * (t - 1.0)) * np.sin(14 * t), 0.0)

    fig, axes = mplt.subplots(nrows=1, ncols=2, layout="thesis_full", height=2.45)

    axes[0].plot(t, err_trad, color="#64748B", linestyle="-.", label="传统主从阻抗控制")
    axes[0].plot(t, err_ours, color="#C0392B", linewidth=1.6, label="本文协同柔顺控制 (Ours)")
    axes[0].axvline(1.8, color="#D35400", linestyle=":", linewidth=0.9)
    axes[0].annotate(
        "外部扰动冲击",
        xy=(1.8, 2.8),
        xytext=(2.35, 5.2),
        arrowprops=dict(arrowstyle="->", color="#D35400", lw=0.8),
        fontsize=8.5,
        color="#D35400",
    )
    axes[0].set_xlabel("时间 $t$ (s)")
    axes[0].set_ylabel(r"双臂协同同步误差 $\|e_{\mathrm{sync}}\|_2$ (mm)")
    axes[0].set_title("(a) 末端相对位姿同步误差响应", pad=6)
    axes[0].legend(loc="upper right")

    axes[1].plot(t, f_ref, color="#111827", linestyle="--", linewidth=1.1, label="期望夹持内力 $F_d$")
    axes[1].plot(t, f_trad, color="#1F4E78", alpha=0.85, label="传统主从阻抗控制")
    axes[1].plot(t, f_ours, color="#C0392B", linewidth=1.6, label="本文协同柔顺控制 (Ours)")
    axes[1].set_xlabel("时间 $t$ (s)")
    axes[1].set_ylabel("协同夹持内力 $F_{\\mathrm{int}}$ (N)")
    axes[1].set_title("(b) 接触过渡阶段内力跟踪响应", pad=6)
    axes[1].set_ylim(-1.5, 22.5)
    axes[1].legend(loc="lower right", fontsize=8.0)

    mplt.add_task_phases(
        [axes[1]],
        [(0.0, 1.0, "自由接近"), (1.0, 2.3, "接触建力"), (2.3, 5.0, "稳态协同搬运")],
        label_y=0.95,
    )

    mplt.savefig(fig, GALLERY_DIR / "fig3_cn_thesis_bimanual")
    plt.close(fig)


if __name__ == "__main__":
    make_fig1_ieee_force_pose_phases()
    make_fig2_ieee_double_overview()
    make_fig3_cn_thesis_bimanual()
    print(f"Successfully generated showcase gallery in: {GALLERY_DIR}")
