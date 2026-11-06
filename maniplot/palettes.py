"""Publication-grade colorblind-safe palettes and robotics semantic colors."""

from __future__ import annotations

from typing import Dict, List

PALETTES: Dict[str, List[str]] = {
    # IEEE / Okabe-Ito hybrid: high contrast in both color and grayscale print
    "ieee": [
        "#005596",  # Deep IEEE Blue (Primary / Ours)
        "#D55E00",  # Vermilion / Orange-Red (Comparison / Ours Highlight)
        "#009E73",  # Bluish Green
        "#CC79A7",  # Reddish Purple
        "#E69F00",  # Amber / Orange
        "#56B4E9",  # Sky Blue
        "#332288",  # Indigo
    ],
    # Chinese Master's / Doctoral Thesis: authoritative deep tones
    "cn_thesis": [
        "#1F4E78",  # 深海蓝 (Deep Academic Blue)
        "#C0392B",  # 朱砂红 (Crimson Red)
        "#27AE60",  # 翡翠绿 (Emerald Green)
        "#8E44AD",  # 皇家紫 (Royal Purple)
        "#D35400",  # 琥珀橙 (Amber Orange)
        "#2980B9",  # 晴空蓝 (Steel Blue)
        "#2C3E50",  # 石墨灰 (Slate Gray)
    ],
    # Nature Publishing Group (NPG) - popular in CoRL / RSS / Science Robotics
    "npg": [
        "#E64B35",  # Cinnabar Red
        "#4DBBD5",  # Cerulean Blue
        "#00A087",  # Persian Green
        "#3C5488",  # Chambray Navy
        "#F39B7F",  # Apricot
        "#8491B4",  # Wild Blue Yonder
        "#91D1C2",  # Monte Carlo Mint
        "#DC0000",  # Monza Red
    ],
    # Science (AAAS)
    "aaas": [
        "#3B4992",
        "#EE0000",
        "#008B45",
        "#631879",
        "#008280",
        "#BB0021",
        "#5F559B",
    ],
}

# Standard robotics X-Y-Z axis / 3D channel colors (colorblind-safe R-G-B equivalents)
XYZ_COLORS: Dict[str, str] = {
    "x": "#D55E00",  # X-axis: Vermilion Red
    "y": "#009E73",  # Y-axis: Emerald Teal
    "z": "#005596",  # Z-axis: Deep Blue
}

# Semantic colors for control & manipulation plots
SEMANTIC_COLORS: Dict[str, str] = {
    "ours": "#C0392B",
    "ours_alt": "#005596",
    "reference": "#111827",
    "limit": "#DC2626",
    "baseline_muted": "#64748B",
}

# Subtle pastel fills for manipulation task phases (Approach -> Grasp -> Contact/Insert -> Release)
PHASE_COLORS: List[str] = [
    "#E0F2FE",  # Phase 1: Soft Sky Blue (e.g., Approach / Free-space Motion)
    "#FEF3C7",  # Phase 2: Soft Amber (e.g., Alignment / Pre-grasp)
    "#FCE7F3",  # Phase 3: Soft Rose (e.g., Contact / Peg-in-Hole Insertion)
    "#DCFCE7",  # Phase 4: Soft Mint (e.g., Stabilize / Complete)
    "#F3E8FF",  # Phase 5: Soft Lavender (e.g., Retract / Release)
]


def get_palette(name: str = "ieee") -> List[str]:
    """Return a copy of a named color palette."""
    if name not in PALETTES:
        valid = ", ".join(sorted(PALETTES.keys()))
        raise ValueError(f"Unknown palette '{name}'. Available palettes: {valid}")
    return list(PALETTES[name])
