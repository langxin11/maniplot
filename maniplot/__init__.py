"""maniplot: Publication-ready plotting toolkit & AI Agent Skill for Robotic Manipulation."""

from __future__ import annotations

from .palettes import PALETTES, PHASE_COLORS, SEMANTIC_COLORS, XYZ_COLORS, get_palette
from .plots import (
    add_task_phases,
    plot_3d_trajectory,
    plot_benchmark_bars,
    plot_ci_curves,
)
from .style import (
    FIGURE_WIDTHS,
    add_panel_labels,
    get_figsize,
    load_csv,
    savefig,
    subplots,
    use_style,
)

__version__ = "0.1.0"

__all__ = [
    "FIGURE_WIDTHS",
    "PALETTES",
    "PHASE_COLORS",
    "SEMANTIC_COLORS",
    "XYZ_COLORS",
    "add_panel_labels",
    "add_task_phases",
    "get_figsize",
    "get_palette",
    "load_csv",
    "plot_3d_trajectory",
    "plot_benchmark_bars",
    "plot_ci_curves",
    "savefig",
    "subplots",
    "use_style",
]
