---
name: maniplot
description: >-
  Publication-ready scientific plotting skill for Robotic Manipulation (IEEE ICRA/IROS/RA-L/T-RO,
  CoRL/RSS, and Chinese Master's Thesis). Activate this skill whenever the user asks to plot data,
  visualize experimental CSV/JSON/NPZ/ROS logs, analyze controller or learning performance, or
  create/refine figures.
---

# maniplot: Robotic Manipulation Publication Plotting Skill

Whenever the user asks to plot data, generate figures, or visualize experimental results, you **MUST** follow the `maniplot` publication standards below instead of writing ad-hoc Matplotlib styling boilerplate.

## 1. Quick Setup & Cross-Platform Library Import (Windows & Linux)

`maniplot` is registered across Python environments and supports both **Windows** and **Linux**. Always import it at the top of your plotting script (with a cross-platform `Path.home() / "maniplot"` fallback in case a fresh virtualenv is used):

```python
import sys
from pathlib import Path

for _candidate in (Path.home() / "maniplot", Path(__file__).resolve().parent):
    if (_candidate / "maniplot" / "__init__.py").exists() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

import maniplot as mplt
import matplotlib.pyplot as plt
import numpy as np
```

When loading CSV logs exported from either Windows (Excel/MATLAB `utf-8-sig` BOM or `gbk`) or Linux (ROS 2 / Franka FCI `utf-8`), prefer `mplt.load_csv(path)` to avoid cross-platform encoding or header whitespace errors:
```python
headers, data = mplt.load_csv("experiment_log.csv")
```

## 2. Selecting the Style Preset

Choose the preset matching the user's language or target venue:

1. **IEEE Robotics Standard (`preset="ieee"`)** — *Default for English labels / ICRA / IROS / RA-L / T-RO*:
   ```python
   mplt.use_style("ieee")  # Times/Liberation Serif + STIX math, inward ticks, Type 42 PDF fonts
   ```
   - Single-column width: `layout="ieee_single"` (`3.50 in`)
   - Double-column width: `layout="ieee_double"` (`7.16 in`)

2. **Chinese Master's Thesis Standard (`preset="cn_thesis"`)** — *Default whenever Chinese labels/titles are requested or for 硕士学位论文*:
   ```python
   mplt.use_style("cn_thesis")  # 中文宋体 (SimSun/Noto Serif CJK SC) + 英文数字 Times New Roman + STIX 公式
   ```
   - Full A4 text width: `layout="thesis_full"` (`5.80 in`)
   - Half-width side-by-side: `layout="thesis_half"` (`2.85 in`)

3. **Modern CoRL / RSS / Science Robotics (`preset="corl"`)**:
   ```python
   mplt.use_style("corl")  # Sans-serif Arial/Liberation Sans, despined top/right, NPG palette
   ```

## 3. Ironclad Publication Rules (Mandatory)

1. **Pure White Background Only**: Figure and axes backgrounds MUST be pure white (`#FFFFFF`). **NEVER** use beige (`#f6f1e8`), gray, or dark dashboard backgrounds.
2. **Always Include Physical Units**: Every axis label must state the symbol and unit in parentheses, e.g.:
   - English: `Time $t$ (s)`, `Contact Force $F_z$ (N)`, `Joint Torque $\tau_i$ (N$\cdot$m)`, `Position Error $\|e_p\|_2$ (mm)`, `Loop Latency ($\mu$s)`
   - Chinese: `时间 $t$ (s)`, `末端接触力 $F_z$ (N)`, `关节力矩 $\tau_i$ (N$\cdot$m)`, `位置跟踪误差 $\|e_p\|_2$ (mm)`
3. **Dual Vector + High-DPI Raster Export**: Always use `mplt.savefig(fig, output_path)` which automatically exports both `.pdf` (vector, Type 42 fonts for IEEE PDF eXpress) and `600 DPI .png` (for quick preview and Word/Markdown insertion).
4. **Consistent Robotics Channel Colors**:
   - When plotting 3D Cartesian channels ($X, Y, Z$ or Roll, Pitch, Yaw), use `mplt.XYZ_COLORS` (`"x": "#D55E00"`, `"y": "#009E73"`, `"z": "#005596"`).
   - Reference / desired trajectories (`$x_d, F_d$`): use black/charcoal dashed lines (`color="#111827", linestyle="--"`).
   - Safety / contact force limits: use red dashed lines (`color="#DC2626", linestyle="--"`).
5. **Multi-Panel Subfigure Labels**: When creating multi-panel subplots (`ncols > 1` or `nrows > 1`), call `mplt.add_panel_labels(axes)` to add bold `(a)`, `(b)`, `(c)` labels.

## 4. High-Level Robotic Manipulation Plot Helpers

Prefer `maniplot`'s built-in primitives over writing raw matplotlib loops:

- **Time-Series Force/Pose Tracking with Manipulation Phases**:
  ```python
  fig, axes = mplt.subplots(nrows=2, ncols=1, layout="ieee_single", aspect=0.48, sharex=True)
  # Plot tracking curves on axes[0], axes[1]...
  mplt.add_task_phases(axes, [
      (0.0, 1.5, "Approach"),
      (1.5, 2.8, "Align & Contact"),
      (2.8, 5.2, "Insertion"),
      (5.2, 6.5, "Stabilize"),
  ])
  ```
- **Multi-Seed Convergence / Learning Curves (Mean ± Std / 95% CI)**:
  ```python
  mplt.plot_ci_curves(ax, steps, {"Ours": ours_seeds, "Baseline": base_seeds},
                      ci_mode="ci95", smooth_window=5, highlight="Ours",
                      xlabel="Training Steps ($\\times 10^3$)", ylabel="Success Rate (%)")
  ```
- **Multi-Task Manipulation Benchmark Bar Charts**:
  ```python
  mplt.plot_benchmark_bars(ax, tasks, scores_dict, errors_dict,
                           highlight_method="Ours", ylabel="Success Rate (%)")
  ```
- **3D End-Effector Trajectories with 6-DoF Orientation Triads & Floor Projection**:
  ```python
  fig = plt.figure(figsize=mplt.get_figsize("ieee_single", aspect=0.88))
  ax = fig.add_subplot(111, projection="3d")
  mplt.plot_3d_trajectory(ax, {"Actual": ee_pos}, reference=ref_pos,
                          rotation_matrices=ee_rot, triad_step=25, project_xy_z=z_floor)
  ```

## 5. Pre-Delivery Verification Checklist

Before finishing any plotting task, consult [checklist.md](./references/checklist.md) and visually inspect the generated `.png` image using your file/image viewing tool (e.g., `read_file`, `Read`, or `view_image`) to verify there are no overlapping legends, clipped labels, or missing font glyphs.
