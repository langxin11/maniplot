"""Style management, IEEE / Thesis figure dimensions, and vector export helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

from .palettes import PALETTES

STYLES_DIR = Path(__file__).resolve().parent / "styles"

# Exact physical dimensions in inches for robotics venues and theses
FIGURE_WIDTHS: Dict[str, float] = {
    "ieee_single": 3.50,      # IEEE ICRA / IROS / RA-L / T-RO single-column width (8.89 cm)
    "ieee_double": 7.16,      # IEEE ICRA / IROS / RA-L / T-RO double-column width (18.19 cm)
    "corl_single": 3.25,      # CoRL / RSS / NeurIPS single-column or half-page width
    "corl_double": 6.75,      # CoRL / RSS / NeurIPS full text width
    "thesis_full": 5.80,      # Chinese Master's Thesis A4 full text width (~14.7 cm)
    "thesis_half": 2.85,      # Chinese Master's Thesis side-by-side half width (~7.2 cm)
}

GOLDEN_RATIO = 0.61803398875


def get_figsize(
    layout: str = "ieee_single",
    aspect: float = 0.66,
    nrows: int = 1,
    ncols: int = 1,
    height: Optional[float] = None,
) -> Tuple[float, float]:
    """Compute exact publication figure size `(width_in, height_in)` in inches.

    Parameters
    ----------
    layout : str
        One of `'ieee_single'` (3.5 in), `'ieee_double'` (7.16 in),
        `'thesis_full'` (5.8 in), `'thesis_half'` (2.85 in), `'corl_single'`, `'corl_double'`.
    aspect : float
        Height-to-width ratio per subplot panel (default 0.66).
    nrows, ncols : int
        Subplot grid dimensions used to scale total figure height automatically.
    height : float, optional
        Explicit height in inches (overrides aspect calculation).
    """
    if layout not in FIGURE_WIDTHS:
        valid = ", ".join(sorted(FIGURE_WIDTHS.keys()))
        raise ValueError(f"Unknown layout '{layout}'. Valid options: {valid}")
    width = FIGURE_WIDTHS[layout]
    if height is not None:
        return (width, float(height))
    panel_width = width / max(1, ncols)
    computed_height = panel_width * aspect * max(1, nrows)
    # Clamp minimum height so labels never clip
    computed_height = max(1.65, min(computed_height, 9.0))
    return (round(width, 2), round(computed_height, 2))


def use_style(
    preset: str = "ieee",
    palette: Optional[str] = None,
    layout: Optional[str] = None,
    font_scale: float = 1.0,
) -> None:
    """Activate a publication plotting style preset globally.

    Parameters
    ----------
    preset : str
        `'ieee'` (ICRA/IROS/RA-L/T-RO), `'cn_thesis'` (国内硕博学位论文 宋体+Times New Roman混排),
        or `'corl'` (CoRL/RSS/Science Robotics modern sans-serif).
    palette : str, optional
        Override color palette (`'ieee'`, `'cn_thesis'`, `'npg'`, `'aaas'`).
    layout : str, optional
        Override default figure width layout (`'ieee_single'`, `'ieee_double'`, `'thesis_full'`, etc.).
    font_scale : float
        Multiplier for all font sizes (default 1.0).
    """
    style_map = {
        "ieee": STYLES_DIR / "ieee.mplstyle",
        "icra": STYLES_DIR / "ieee.mplstyle",
        "iros": STYLES_DIR / "ieee.mplstyle",
        "ral": STYLES_DIR / "ieee.mplstyle",
        "tro": STYLES_DIR / "ieee.mplstyle",
        "cn_thesis": STYLES_DIR / "cn_thesis.mplstyle",
        "thesis": STYLES_DIR / "cn_thesis.mplstyle",
        "corl": STYLES_DIR / "corl.mplstyle",
        "rss": STYLES_DIR / "corl.mplstyle",
        "nature": STYLES_DIR / "corl.mplstyle",
    }
    key = preset.lower().strip()
    if key not in style_map:
        valid = ", ".join(sorted(style_map.keys()))
        raise ValueError(f"Unknown preset '{preset}'. Choose from: {valid}")

    plt.style.use(str(style_map[key]))

    # Apply palette override if specified
    if palette is not None:
        colors = PALETTES[palette]
        mpl.rcParams["axes.prop_cycle"] = cycler(color=colors)

    # Apply default layout size if specified
    if layout is not None:
        mpl.rcParams["figure.figsize"] = list(get_figsize(layout=layout))

    # Scale font sizes if requested
    if abs(font_scale - 1.0) > 1e-3:
        for param in (
            "font.size",
            "axes.titlesize",
            "axes.labelsize",
            "xtick.labelsize",
            "ytick.labelsize",
            "legend.fontsize",
            "figure.titlesize",
        ):
            base = float(mpl.rcParams[param])
            mpl.rcParams[param] = round(base * font_scale, 2)


def subplots(
    nrows: int = 1,
    ncols: int = 1,
    layout: Optional[str] = None,
    aspect: float = 0.62,
    height: Optional[float] = None,
    sharex: Union[bool, str] = False,
    sharey: Union[bool, str] = False,
    constrained_layout: bool = True,
    **kwargs,
):
    """Wrapper around `plt.subplots` that automatically computes publication `figsize`."""
    if "figsize" not in kwargs:
        if layout is None:
            # Infer default layout from current font size (cn_thesis uses 10pt, ieee uses 8.5pt)
            is_thesis = float(mpl.rcParams.get("font.size", 8.5)) >= 9.5
            if ncols > 1:
                layout = "thesis_full" if is_thesis else "ieee_double"
            else:
                layout = "thesis_full" if is_thesis else "ieee_single"
        kwargs["figsize"] = get_figsize(
            layout=layout, aspect=aspect, nrows=nrows, ncols=ncols, height=height
        )
    return plt.subplots(
        nrows=nrows,
        ncols=ncols,
        sharex=sharex,
        sharey=sharey,
        constrained_layout=constrained_layout,
        **kwargs,
    )


def add_panel_labels(
    axes: Iterable[mpl.axes.Axes],
    labels: Optional[Sequence[str]] = None,
    loc: Tuple[float, float] = (-0.14, 1.05),
    fontsize: Optional[float] = None,
    fontweight: str = "bold",
) -> None:
    """Add standardized `(a)`, `(b)`, `(c)` subfigure labels to an array of axes."""
    ax_list = list(axes.flat) if hasattr(axes, "flat") else list(axes)
    if labels is None:
        labels = [f"({chr(ord('a') + i)})" for i in range(len(ax_list))]
    size = fontsize or (float(mpl.rcParams["axes.titlesize"]) + 0.5)
    for ax, label in zip(ax_list, labels):
        ax.text(
            loc[0],
            loc[1],
            label,
            transform=ax.transAxes,
            fontsize=size,
            fontweight=fontweight,
            va="bottom",
            ha="right",
        )


def savefig(
    fig: mpl.figure.Figure,
    path: Union[str, Path],
    formats: Sequence[str] = ("pdf", "png"),
    dpi: int = 600,
) -> Sequence[Path]:
    """Save a figure in both vector (`pdf`) and high-res raster (`png`) formats.

    Ensures white background, tight bounding box, and IEEE PDF eXpress Type 42 font compliance.
    """
    base = Path(path)
    if base.suffix.lower() in (".png", ".pdf", ".svg", ".eps"):
        base = base.with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for fmt in formats:
        ext = fmt.lstrip(".").lower()
        out_path = base.with_suffix(f".{ext}")
        fig.savefig(
            out_path,
            format=ext,
            dpi=dpi if ext in ("png", "jpg", "jpeg", "tif", "tiff") else None,
            bbox_inches="tight",
            pad_inches=0.06,
            facecolor="white",
            edgecolor="none",
        )
        saved_paths.append(out_path)
    return saved_paths
