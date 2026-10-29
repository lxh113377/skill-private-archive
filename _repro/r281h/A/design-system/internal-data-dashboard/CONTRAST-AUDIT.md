# CONTRAST-AUDIT.md - every contrast claim in TOKENS.md, measured (arm A)

Reproduce (from the arm dir):

```bash
PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
for f in _evidence.py _evidence2.py _evidence3.py _evidence4.py _evidence5.py; do "$PY" "$f"; done
```

Formula: WCAG 2.x sRGB relative luminance (per-channel linearization, L = 0.2126R + 0.7152G + 0.0722B,
ratio = (Lmax + 0.05) / (Lmin + 0.05)). Verdict bands: >=7 AAA, >=4.5 AA, >=3 AA-UI (graphics and
control edges per SC 1.4.11), otherwise FAIL.

Method note kept on purpose: the first version of `_evidence.py` divided each channel by 255 a second
time inside `chan()` after `lum()` had already normalized it, which printed ratio=1.00 for all 20 pairs.
That output was NOT used for any conclusion; the bug and the fix are recorded in the script docstring
and in _exec_log.md rows 18-20.

## Defects found in the generator output, and the replacements (6)

| # | Where the bad value came from | Value as shipped by the script | Measured | Why it fails | Replacement | Replacement measured |
|---|------------------------------|--------------------------------|----------|--------------|-------------|----------------------|
| 1 | `MASTER.md:71-73` (`.btn-primary`) | `background: #F59E0B` + `color: white` | 2.15 | text needs 4.5:1 | fill `#1E40AF` + white; when an accent fill is required, text becomes `--color-on-cta #451A03` | 8.72 / 6.97 `[MEAS]` |
| 2 | `MASTER.md:130` (`.input:focus`) | `box-shadow: 0 0 0 3px #1E40AF20` | 1.23 after compositing the 8-digit alpha (a = 0x20/255 = 0.1255, blends to `#DDE3F2`) | a focus indicator is a control edge: 3:1 | two-layer ring: 2px `#1D4ED8` on light surfaces, 2px `#93C5FD` where the control is filled (`#1D4ED8` on `#1E40AF` measured only 1.30 `[MEAS]`) | 6.41 vs `#F8FAFC`, 6.70 vs `#FFFFFF`, 4.84 on the filled primary `[MEAS]` |
| 3 | `MASTER.md:121` (`.input` border) | `border: 1px solid #E2E8F0` | 1.23 vs `#FFFFFF` | a focusable control edge must clear 3:1 | `--color-border-strong #64748B` | 4.76 `[MEAS]` |
| 4 | `MASTER.md:22` (`--color-secondary`) | `#3B82F6` used as text | 3.52 vs `#F8FAFC`, 3.68 vs `#FFFFFF` `[MEAS]` | over the 3:1 graphic bar, under the 4.5:1 text bar | restricted to graphics/outlines; text uses `--color-primary` | 8.34 `[MEAS]` |
| 5 | `styles.csv:34` recommends `#22C55E` / `#EF4444` for deltas | same | 2.18 / 3.60 vs `#F8FAFC` `[MEAS]` | the green is under 3:1 and both are under 4.5:1 as text | delta TEXT uses `#15803D` / `#B91C1C`; the bright pair survives only as fills | 4.79 / 6.18 `[MEAS]` |
| 6 | `charts.csv:14` waterfall increase `#4CAF50` | same | 2.78 vs `#FFFFFF` `[MEAS]` | essential graphic under 3:1 | keep the CSV ramp for the fill but require a numeric label in the same visual field; text deltas as row 5 | decrease 3.68, start 3.12, end 8.63 `[MEAS]` |

Two further measurements that are not defects but change how a token may be used:
- `#F59E0B` measures 2.15 on white `[MEAS]` but 6.81 on the dark surface `#1E293B` `[MEAS]` - the same hex
  is unusable in one theme and text-grade in the other, so the accent ramp is theme-split in TOKENS.md 1.3.
- `--color-dark-surface #1E293B` against `--color-dark-page-bg #0F172A` measures 1.22 `[MEAS]`, so dark
  layer separation is carried by border + shadow, not by luminance (TOKENS.md 1.4).

## Decorative values that are deliberately kept below 3:1

| Token | Ratio | Justification |
|-------|-------|---------------|
| `--color-border-hairline #E2E8F0` | 1.18-1.23 `[MEAS]` | inner row rules only; every control edge uses `--color-border-strong` instead |
| `--color-border #CBD5E1` | 1.42-1.48 `[MEAS]` | card frame paired with `--shadow-sm`, and the card also has a heading with AA text |
| `--color-surface-sunken #F1F5F9` | 1.10 `[MEAS]` | zebra / skeleton tint, no affordance duty |
| `--color-row-selected-bg #DBEAFE` | 1.22 `[MEAS]` vs white | selection is also signalled by a 3px left bar `#1E40AF` (8.72 `[MEAS]`) so colour is not the only cue |
| skeleton pulse | 1.23 `[MEAS]` | transient placeholder; text never rendered on it |
| disabled label `#94A3B8` | 2.34-2.56 `[MEAS]` | WCAG 2.1 exempts inactive components from 1.4.3/1.4.11; reported, not hidden `[J]` for the exemption reading |

## Full measurement inventory

| Script | Pairs measured | What it settled |
|--------|----------------|-----------------|
| `_evidence_out.txt` | 20 | the palette the generator chose |
| `_evidence2_out.txt` | 37 + type-scale arithmetic | replacement candidates, dark theme, focus-on-fill |
| `_evidence3_out.txt` | 26 + 8px-grid multipliers + breakpoint union | strong chart ramp (10 slots), light chart ramp (6 slots), row states |
| `_evidence4_out.txt` | 18 + 44px arithmetic | borders, row hover, dark hairlines |
| `_evidence5_out.txt` | 18 + 3 alpha-composite lines | 8-digit halo compositing, waterfall pair, dark primary on light |

Total ratio computations available on disk: **139**, across 5 scripts, all rc=0.

## Keyboard and focus coverage (SKILL.md:51 mandates it)

| Requirement | Source | Where it lands in the design system |
|-------------|--------|-------------------------------------|
| visible focus ring; never remove outline without a replacement | `ux-guidelines.csv:29` `[CSV]` | TOKENS.md 4.1/4.2 focus-visible rows |
| keyboard handlers alongside click (`onKeyDown`, `tabIndex`) | `web-interface.csv:4` `[CSV]` | TOKENS.md 4.4 table focus row |
| inline error + move focus to first invalid field | `web-interface.csv:16` `[CSV]` | TOKENS.md 4.3 error row |
| data-table alternative for every chart | `charts.csv:5` `[CSV]` | TOKENS.md 4.6 focus row |
| `prefers-reduced-motion` respected | `ux-guidelines.csv:10` `[CSV]` + `MASTER.md:200` `[GEN]` | TOKENS.md 4.0 `--reduced-motion` |
| body text never under 16px on mobile | `ux-guidelines.csv:68` `[CSV]` | TOKENS.md 3.2 `--text-base` |
