"""High-level plotting primitives tailored for Robotic Manipulation publications."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from .palettes import PALETTES, PHASE_COLORS, SEMANTIC_COLORS, XYZ_COLORS


def add_task_phases(
    axes: Union[mpl.axes.Axes, Sequence[mpl.axes.Axes], np.ndarray],
    phases: Sequence[Tuple[float, float, str]],
    colors: Optional[Sequence[str]] = None,
    alpha: float = 0.42,
    show_labels: bool = True,
    label_y: float = 0.94,
    divider_color: str = "#64748B",
) -> None:
    """Shade manipulation task phases (e.g. Approach -> Contact -> Insert -> Release) across time-series subplots.

    Parameters
    ----------
    axes : Axes or sequence of Axes
        Single axes or vertically stacked shared-x axes.
    phases : sequence of `(t_start, t_end, label)`
        Time intervals and human-readable phase names.
    """
    if isinstance(axes, mpl.axes.Axes):
        ax_list = [axes]
    elif hasattr(axes, "flat"):
        ax_list = list(axes.flat)
    else:
        ax_list = list(axes)

    phase_palette = list(colors) if colors is not None else PHASE_COLORS

    for idx, (t0, t1, name) in enumerate(phases):
        fill_color = phase_palette[idx % len(phase_palette)]
        for ax_i, ax in enumerate(ax_list):
            ax.axvspan(t0, t1, color=fill_color, alpha=alpha, zorder=0, lw=0)
            if idx > 0:
                ax.axvline(
                    t0,
                    color=divider_color,
                    linestyle=":",
                    linewidth=0.75,
                    alpha=0.75,
                    zorder=1,
                )
            if show_labels and ax_i == 0 and name:
                trans = mpl.transforms.blended_transform_factory(
                    ax.transData, ax.transAxes
                )
                ax.text(
                    0.5 * (t0 + t1),
                    label_y,
                    name,
                    transform=trans,
                    ha="center",
                    va="top",
                    fontsize=float(mpl.rcParams["xtick.labelsize"]),
                    fontweight="bold",
                    color="#1E293B",
                    bbox=dict(
                        boxstyle="round,pad=0.18",
                        facecolor="white",
                        edgecolor="none",
                        alpha=0.78,
                    ),
                    zorder=5,
                )


def plot_ci_curves(
    ax: mpl.axes.Axes,
    x: np.ndarray,
    series_dict: Dict[str, np.ndarray],
    colors: Optional[Sequence[str]] = None,
    ci_mode: str = "std",
    alpha_band: float = 0.18,
    smooth_window: int = 1,
    highlight: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> mpl.axes.Axes:
    """Plot multi-seed RL / Imitation Learning / convergence curves with Mean and shaded Std / 95% CI.

    Parameters
    ----------
    ax : Axes
        Target matplotlib Axes.
    x : 1D array of shape (T,)
        Horizontal axis (e.g. training steps, episodes, or time).
    series_dict : dict mapping `method_name -> 2D array of shape (n_seeds, T)` or 1D array `(T,)`
        Evaluation series across random seeds or rollouts.
    ci_mode : str
        `'std'` (Mean ± 1 SD), `'sem'` (Mean ± 1 SEM), or `'ci95'` (Mean ± 1.96 SEM).
    smooth_window : int
        Moving-average smoothing window size (1 = no smoothing).
    highlight : str, optional
        Method name (e.g. `'Ours'`) to emphasize with thicker line weight and top z-order.
    """
    palette = list(colors) if colors is not None else list(
        plt.rcParams["axes.prop_cycle"].by_key().get("color", PALETTES["ieee"])
    )

    def _smooth(arr: np.ndarray, win: int) -> np.ndarray:
        if win <= 1:
            return arr
        kernel = np.ones(win, dtype=float) / win
        pad_left = win // 2
        pad_right = win - 1 - pad_left
        padded = np.pad(arr, (pad_left, pad_right), mode="edge")
        return np.convolve(padded, kernel, mode="valid")

    for idx, (label, raw) in enumerate(series_dict.items()):
        arr = np.asarray(raw, dtype=float)
        if arr.ndim == 1:
            mean = _smooth(arr, smooth_window)
            spread = np.zeros_like(mean)
        else:
            smoothed = np.vstack([_smooth(seed_row, smooth_window) for seed_row in arr])
            mean = np.nanmean(smoothed, axis=0)
            std = np.nanstd(smoothed, axis=0)
            n = max(1, smoothed.shape[0])
            if ci_mode == "ci95":
                spread = 1.96 * std / np.sqrt(n)
            elif ci_mode == "sem":
                spread = std / np.sqrt(n)
            else:
                spread = std

        color = palette[idx % len(palette)]
        is_highlight = highlight is not None and label == highlight
        lw = float(mpl.rcParams["lines.linewidth"]) * (1.35 if is_highlight else 1.0)
        zorder = 4 if is_highlight else 2

        ax.plot(x, mean, label=label, color=color, linewidth=lw, zorder=zorder)
        if np.any(spread > 0):
            ax.fill_between(
                x,
                mean - spread,
                mean + spread,
                color=color,
                alpha=alpha_band * (1.25 if is_highlight else 1.0),
                linewidth=0,
                zorder=zorder - 1,
            )

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.margins(x=0.01)
    return ax


def plot_benchmark_bars(
    ax: mpl.axes.Axes,
    tasks: Sequence[str],
    method_scores: Dict[str, Sequence[float]],
    method_errors: Optional[Dict[str, Sequence[float]]] = None,
    highlight_method: Optional[str] = None,
    colors: Optional[Sequence[str]] = None,
    ylabel: str = "Success Rate (%)",
    ylim: Optional[Tuple[float, float]] = (0, 112),
    annotate_values: bool = True,
    value_fmt: str = "{:.0f}",
) -> mpl.axes.Axes:
    """Plot grouped manipulation benchmark bar chart with error bars and top annotations.

    Parameters
    ----------
    tasks : sequence of str
        Task names on the x-axis (e.g., `['Peg-in-Hole', 'Bimanual Handover', 'Drawer Open']`).
    method_scores : dict mapping `method_name -> sequence of scores`
        Mean scores per task for each method.
    method_errors : dict mapping `method_name -> sequence of error bar half-widths`, optional
        Standard deviation or confidence interval per task.
    highlight_method : str, optional
        Name of the proposed method (e.g. `'Ours'`) to highlight with bold text and crisp edge.
    """
    palette = list(colors) if colors is not None else list(
        plt.rcParams["axes.prop_cycle"].by_key().get("color", PALETTES["ieee"])
    )
    methods = list(method_scores.keys())
    n_tasks = len(tasks)
    n_methods = len(methods)
    x = np.arange(n_tasks, dtype=float)
    total_group_width = 0.76
    bar_width = total_group_width / max(1, n_methods)

    for idx, method in enumerate(methods):
        scores = np.asarray(method_scores[method], dtype=float)
        errs = (
            np.asarray(method_errors[method], dtype=float)
            if (method_errors and method in method_errors)
            else None
        )
        offset = (idx - (n_methods - 1) / 2.0) * bar_width
        color = palette[idx % len(palette)]
        is_ours = highlight_method is not None and method == highlight_method

        bars = ax.bar(
            x + offset,
            scores,
            width=bar_width * 0.90,
            label=method,
            color=color,
            alpha=0.95 if is_ours else 0.80,
            edgecolor="#111827" if is_ours else "#334155",
            linewidth=0.9 if is_ours else 0.55,
            yerr=errs,
            capsize=2.2 if errs is not None else 0,
            error_kw=dict(lw=0.75, capthick=0.75, ecolor="#1E293B"),
            zorder=3 if is_ours else 2,
        )

        if annotate_values:
            for b_i, rect in enumerate(bars):
                val = scores[b_i]
                err_offset = errs[b_i] if errs is not None else 0.0
                ax.text(
                    rect.get_x() + rect.get_width() / 2.0,
                    val + err_offset + (ylim[1] * 0.015 if ylim else 1.2),
                    value_fmt.format(val),
                    ha="center",
                    va="bottom",
                    fontsize=float(mpl.rcParams["xtick.labelsize"]) - 0.8,
                    fontweight="bold" if is_ours else "normal",
                    color="#111827" if is_ours else "#475569",
                )

    ax.set_xticks(x)
    ax.set_xticklabels(tasks)
    ax.set_ylabel(ylabel)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.grid(axis="x", visible=False)
    return ax


def plot_3d_trajectory(
    ax: mpl.axes.Axes,
    trajectories: Dict[str, np.ndarray],
    reference: Optional[np.ndarray] = None,
    rotation_matrices: Optional[np.ndarray] = None,
    triad_step: int = 25,
    triad_scale: float = 0.025,
    project_xy_z: Optional[float] = None,
    start_label: str = "Start",
    goal_label: str = "Goal",
    colors: Optional[Sequence[str]] = None,
) -> mpl.axes.Axes:
    """Plot 3D End-Effector trajectories with optional 6-DoF orientation triads and XY floor shadow projection.

    Parameters
    ----------
    ax : 3D Axes (`projection='3d'`)
        Target 3D matplotlib Axes.
    trajectories : dict mapping `name -> (N, 3) array`
        3D Cartesian trajectories `[x, y, z]`.
    reference : (M, 3) array, optional
        Desired/reference trajectory plotted as a black dashed curve.
    rotation_matrices : (N, 3, 3) array, optional
        End-effector rotation matrices along the primary trajectory for drawing RGB orientation frames.
    project_xy_z : float, optional
        If provided, projects a subtle 2D shadow of each trajectory onto the plane `z = project_xy_z`.
    """
    palette = list(colors) if colors is not None else list(
        plt.rcParams["axes.prop_cycle"].by_key().get("color", PALETTES["ieee"])
    )

    if reference is not None:
        ref = np.asarray(reference, dtype=float)
        ax.plot(
            ref[:, 0],
            ref[:, 1],
            ref[:, 2],
            color=SEMANTIC_COLORS["reference"],
            linestyle="--",
            linewidth=1.2,
            label="Reference",
            zorder=2,
        )
        if project_xy_z is not None:
            ax.plot(
                ref[:, 0],
                ref[:, 1],
                np.full_like(ref[:, 2], project_xy_z),
                color="#94A3B8",
                linestyle="--",
                linewidth=0.7,
                alpha=0.55,
            )

    first_traj = None
    for idx, (label, pts) in enumerate(trajectories.items()):
        arr = np.asarray(pts, dtype=float)
        if first_traj is None:
            first_traj = arr
        color = palette[idx % len(palette)]
        ax.plot(
            arr[:, 0],
            arr[:, 1],
            arr[:, 2],
            color=color,
            linewidth=1.5 if idx == 0 else 1.15,
            label=label,
            zorder=4 if idx == 0 else 3,
        )
        if project_xy_z is not None:
            ax.plot(
                arr[:, 0],
                arr[:, 1],
                np.full_like(arr[:, 2], project_xy_z),
                color=color,
                linewidth=0.75,
                alpha=0.30,
            )

    # Mark Start and Goal on the primary trajectory (or reference)
    anchor = np.asarray(reference if reference is not None else first_traj, dtype=float)
    if anchor is not None and len(anchor) > 0:
        ax.scatter(
            [anchor[0, 0]],
            [anchor[0, 1]],
            [anchor[0, 2]],
            color="#009E73",
            s=36,
            marker="o",
            edgecolors="white",
            linewidths=0.7,
            label=start_label,
            zorder=6,
        )
        ax.scatter(
            [anchor[-1, 0]],
            [anchor[-1, 1]],
            [anchor[-1, 2]],
            color="#D55E00",
            s=58,
            marker="*",
            edgecolors="#111827",
            linewidths=0.5,
            label=goal_label,
            zorder=6,
        )

    # Draw 6-DoF End-Effector orientation triads (RGB coordinate axes) along primary trajectory
    if rotation_matrices is not None and first_traj is not None:
        rots = np.asarray(rotation_matrices, dtype=float)
        axis_colors = [XYZ_COLORS["x"], XYZ_COLORS["y"], XYZ_COLORS["z"]]
        for k in range(0, len(first_traj), max(1, triad_step)):
            origin = first_traj[k]
            R = rots[k]
            for axis_idx in range(3):
                vec = R[:, axis_idx] * triad_scale
                ax.plot(
                    [origin[0], origin[0] + vec[0]],
                    [origin[1], origin[1] + vec[1]],
                    [origin[2], origin[2] + vec[2]],
                    color=axis_colors[axis_idx],
                    linewidth=1.0,
                    alpha=0.85,
                )

    # Clean 3D pane styling (pure white panes with subtle gridlines)
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("#CBD5E1")
    ax.tick_params(pad=1)
    return ax
