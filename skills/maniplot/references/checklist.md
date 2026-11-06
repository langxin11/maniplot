# Robotic Manipulation Publication Figure Checklist

Always verify the following items before presenting a figure to the user:

1. **Typography & Fonts**
   - [ ] `pdf.fonttype == 42` and `ps.fonttype == 42` (No Type 3 fonts that fail IEEE PDF eXpress).
   - [ ] In `cn_thesis` mode, Chinese characters render in Serif/SimSun/Noto Serif CJK SC without `[?]` tofu boxes, and English/numbers render in Times/Liberation Serif.
   - [ ] Mathematical variables ($q_i, \dot{q}_i, \tau_i, F_ext, M(q), \mathcal{J}$) use `$...$` math mode.

2. **Dimensions & Aspect Ratio**
   - [ ] Single-column IEEE figures use `width = 3.50 in`; double-column IEEE figures use `width = 7.16 in`.
   - [ ] Chinese thesis full-width figures use `width = 5.80 in`.
   - [ ] Font sizes are 7.5–9.0 pt for IEEE and 9.0–10.5 pt for Chinese thesis so text matches the paper caption size at 100% scale.

3. **Visual Clarity & Aesthetics**
   - [ ] Pure white background (`#FFFFFF`) on both figure and axes.
   - [ ] Legend does not cover critical peaks, step transitions, or error bars (use `ncol=2` or top-outside legend if crowded).
   - [ ] Every axis has both quantity name and physical unit, e.g., `Force $F_z$ (N)`.
   - [ ] Visual inspection performed on the generated `.png` file via `read_file`.
