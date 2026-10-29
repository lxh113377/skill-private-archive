# TOKENS.md - internal-data-dashboard design system (Arm A)

Project slug: `internal-data-dashboard`  |  Arm: A  |  Date: 2026-10-29
Process authority: `_temp/r281h/A/SKILL.md` (ui-ux-pro-max v1.2.0, arm-local copy, 57 lines).
Retrieval order for any later session: `MASTER.md` -> `pages/dashboard.md` (page overrides beat
MASTER) -> `TOKENS.md` (this file: the full numeric token set) -> `CONTRAST-AUDIT.md` (the
measurements behind every contrast claim) -> `README.md` (persist / regenerate).

## Provenance legend (honesty rule)

| Tag | Meaning |
|-----|---------|
| `[CSV]` | value copied from a local CSV row, cited as file:line |
| `[GEN]` | value emitted by the bundled generator script, cited as generated-file:line |
| `[MEAS]` | ratio computed by `_evidence*.py` in this arm dir; outputs in `_evidence*_out.txt` (recomputable) |
| `[J]` | 设计判断（无本地出处） - this arm's own judgment, no local source |

CSV base path (read-only): `D:/global_skills/ui-ux-pro-max/data/`. Line numbers are 1-based
physical lines; CSV line 1 is the header, so row `No 8` sits at physical line 9.
No number below is presented as script output unless a script actually printed it.

---

## 1. Color tokens

Base palette = the Analytics Dashboard row of the bundled color data:
`colors.csv:9` = `8,Analytics Dashboard,#1E40AF,#3B82F6,#F59E0B,#F8FAFC,#1E3A8A,#DBEAFE,Blue data + amber highlights` `[CSV]`.
The generator wrote those same five hexes into `MASTER.md:21-25` `[GEN]`.

### 1.1 Core semantic roles (light theme)

| Token | Value | Role | Provenance | Contrast measured on its real background |
|-------|-------|------|-----------|------------------------------------------|
| `--color-primary` | `#1E40AF` | brand + interactive | `[CSV]` colors.csv:9 | 8.34 vs `#F8FAFC` `[MEAS]` AAA; 8.72 vs `#FFFFFF` `[MEAS]` AAA |
| `--color-secondary` | `#3B82F6` | support / selected outline | `[CSV]` colors.csv:9 | 3.52 vs `#F8FAFC` `[MEAS]`, 3.68 vs `#FFFFFF` `[MEAS]` - graphics only, not text |
| `--color-cta` | `#F59E0B` | accent FILL only (bars, badges, glow) | `[CSV]` colors.csv:9 | 2.05 vs `#F8FAFC` `[MEAS]` and 2.15 vs `#FFFFFF` `[MEAS]` - fails the 3:1 graphic bar; see CONTRAST-AUDIT finding #1 |
| `--color-on-cta` | `#451A03` | text on an accent fill | `[CSV]` colors.csv:68 | 6.97 vs `#F59E0B` `[MEAS]` AA (replaces white, which measured 2.15 `[MEAS]` FAIL) |
| `--color-cta-strong` | `#B45309` | accent where text-level contrast is required | `[CSV]` colors.csv:43 / :67 | white on it 5.02 `[MEAS]` AA; itself vs `#F8FAFC` 4.80 `[MEAS]` AA |
| `--color-page-bg` | `#F8FAFC` | app background | `[CSV]` colors.csv:9 | base layer |
| `--color-surface` | `#FFFFFF` | card / panel / table background | `[CSV]` styles.csv:40 (`--card-bg: #FFFFFF`) | base layer |
| `--color-surface-sunken` | `#F1F5F9` | zebra row, skeleton, row hover | `[J]` 设计判断（无本地出处） | 1.10 vs `#FFFFFF` `[MEAS]` - decorative surface, carries no text duty by itself |
| `--color-text` | `#1E3A8A` | headings, KPI values | `[CSV]` colors.csv:9 | 9.90 vs `#F8FAFC` `[MEAS]` AAA; 10.36 vs `#FFFFFF` `[MEAS]` AAA |
| `--color-text-body` | `#0F172A` | dense table body text | `[CSV]` colors.csv:7 / :8 / :15 | 17.06 vs `#F8FAFC` `[MEAS]` AAA; 17.85 vs `#FFFFFF` `[MEAS]` AAA; 16.30 vs `#F1F5F9` `[MEAS]` AAA |
| `--color-text-muted` | `#475569` | field labels, captions | `[CSV]` colors.csv:27 / :33 | 7.24 vs `#F8FAFC` `[MEAS]` AAA; 7.58 vs `#FFFFFF` `[MEAS]` AAA |
| `--color-text-subtle` | `#64748B` | metadata only (AA, not AAA) | `[CSV]` colors.csv:33 / :54 | 4.55 vs `#F8FAFC` `[MEAS]` AA; 4.76 vs `#FFFFFF` `[MEAS]` AA; 4.34 vs `#F1F5F9` `[MEAS]` AA |
| `--color-border-hairline` | `#E2E8F0` | inner separators, row rules (decorative) | `[CSV]` colors.csv:2 / :7 / :14 | 1.18 vs `#F8FAFC` `[MEAS]`, 1.23 vs `#FFFFFF` `[MEAS]` - must not be the only affordance cue |
| `--color-border` | `#CBD5E1` | default card/table border, paired with `--shadow-sm` | `[CSV]` colors.csv:43 | 1.42 vs `#F8FAFC` `[MEAS]`, 1.48 vs `#FFFFFF` `[MEAS]` decorative |
| `--color-border-strong` | `#64748B` | input/control edge that must clear 3:1 | `[CSV]` colors.csv:33 / :54 | 4.76 vs `#FFFFFF` `[MEAS]` AA; 4.55 vs `#F8FAFC` `[MEAS]` AA |
| `--color-row-selected-bg` | `#DBEAFE` | selection tint | `[CSV]` colors.csv:9 (Border col) | `#1E3A8A` on it 8.49 `[MEAS]` AAA; vs `#FFFFFF` 1.22 `[MEAS]` (tint, not an outline) |

### 1.2 Status colors (light theme)

| Token | Value | As text | As graphic | Provenance |
|-------|-------|---------|------------|-----------|
| `--color-success` | `#15803D` | 4.79 vs `#F8FAFC` `[MEAS]`, 5.02 vs `#FFFFFF` `[MEAS]` AA | >=3:1 OK at the same ratios | `[CSV]` colors.csv:53 / :63 / :66 |
| `--color-warning` | `#B45309` | 4.80 vs `#F8FAFC` `[MEAS]` AA | 4.80 `[MEAS]` OK | `[CSV]` colors.csv:43 / :67 |
| `--color-danger` | `#B91C1C` | 6.18 vs `#F8FAFC` `[MEAS]` AA; 6.47 vs `#FFFFFF` `[MEAS]` AA | 6.18 `[MEAS]` OK | `[CSV]` colors.csv:69 |
| `--color-danger-graphic` | `#EF4444` | not for text: 3.76 vs `#FFFFFF` `[MEAS]` is under the 4.5:1 text bar | 3.60 vs `#F8FAFC` `[MEAS]`, 3.76 vs `#FFFFFF` `[MEAS]` -> >=3:1 OK | `[CSV]` styles.csv:29 (alert red) / colors.csv:71 |
| `--color-success-graphic` | `#22C55E` | text FAIL on light (2.18 vs `#F8FAFC` `[MEAS]`) | light mode: fill only; on dark it is text-grade (6.42 vs `#1E293B` `[MEAS]`, 7.83 vs `#0F172A` `[MEAS]`) | `[CSV]` styles.csv:29 (success green) |
| `--color-info-bg` | `#DBEAFE` | - | info callout container | `[CSV]` colors.csv:9 |
| `--color-success-bg` | `#F0FDF4` | `#15803D` on it 4.79 `[MEAS]` AA | callout container | `[CSV]` colors.csv:53 / :63 / :66 |
| `--color-warning-bg` | `#FEF3C7` | `#B45309` on it 4.51 `[MEAS]` AA | callout container | `[CSV]` colors.csv:67 / :68 |
| `--color-danger-bg` | `#FEF2F2` | `#B91C1C` on it 5.91 `[MEAS]` AA | callout container | `[CSV]` colors.csv:69 |

### 1.3 Chart categorical ramp

Every essential data mark must clear 3:1 against the plot surface (WCAG 1.4.11).
Measured ramps below; assign `series-*` in order.

Light plot surface `#FFFFFF`:

| Slot | Hex | ratio vs white `[MEAS]` | Provenance |
|------|-----|------------------------|-----------|
| series-1 | `#1E40AF` | 8.72 | `[CSV]` colors.csv:9 |
| series-2 | `#334155` | 10.35 | `[CSV]` colors.csv:7 / :8 |
| series-3 | `#0F766E` | 5.47 | `[CSV]` colors.csv:39 |
| series-4 | `#15803D` | 5.02 | `[CSV]` colors.csv:53 |
| series-5 | `#B45309` | 5.02 | `[CSV]` colors.csv:43 / :67 |
| series-6 | `#B91C1C` | 6.47 | `[CSV]` colors.csv:69 |
| series-7 | `#8B5CF6` | 4.23 | `[CSV]` styles.csv:35 / colors.csv:16 (4.05 vs `#F8FAFC` `[MEAS]`) |
| series-8 | `#6D28D9` | 7.10 | `[J]` 设计判断（无本地出处） |
| series-9 | `#BE185D` | 6.04 | `[J]` 设计判断（无本地出处） |
| series-10 | `#0E7490` | 5.36 | `[J]` 设计判断（无本地出处） |

Excluded from the LIGHT ramp because they measure under 3:1 on white - `#F59E0B` 2.15,
`#22C55E` 2.28, `#06B6D4` 2.43 `[MEAS]` - although all three come from the CSV data
(styles.csv:29 lists success `#22C55E` and warning `#F59E0B` as the BI chart colors).
They stay in the dark ramp, where they pass. Past 10 series, reuse slots and add a
pattern/shape shift per series `[J]` 设计判断（无本地出处）; the data itself only says
"Multiple series: use distinct colors" with no numeric cap `[CSV]` charts.csv:2.

Dark plot surface `#1E293B`:

| Slot | Hex | ratio vs `#1E293B` `[MEAS]` | Provenance |
|------|-----|------------------------------|-----------|
| series-1 | `#60A5FA` | 5.75 | `[J]` 设计判断（无本地出处） |
| series-2 | `#22D3EE` | 8.09 | `[CSV]` colors.csv:10 |
| series-3 | `#22C55E` | 6.42 | `[CSV]` styles.csv:29 |
| series-4 | `#F59E0B` | 6.81 | `[CSV]` colors.csv:9 |
| series-5 | `#F87171` | 5.29 | `[CSV]` colors.csv:37 |
| series-6 | `#A78BFA` | 5.38 | `[CSV]` colors.csv:14 / :20 / :21 |

Heatmap diverging scale, verbatim from the BI heatmap row `[CSV]` styles.csv:30:
`--heatmap-cool: #0080FF` (3.80 vs white `[MEAS]`), `--heatmap-neutral: #FFFFFF`,
`--heatmap-hot: #FF0000` (4.00 vs white `[MEAS]`), `--cell-size: 24px`,
`--legend-width: 200px`, `--tooltip-bg: rgba(0,0,0,0.9)`.
That same row's Accessibility column states `⚠ Colorblind considerations` `[CSV]` styles.csv:30,
so the shipped rule adds a numeric label inside every cell `[J]` 设计判断（无本地出处）.

Waterfall / cumulative-delta colors verbatim from the CSV `[CSV]` charts.csv:14:
increases `#4CAF50`, decreases `#F44336`, start `#2196F3`, end `#0D47A1`.
Measured on white: increase 2.78 `[MEAS]` (under 3:1), decrease 3.68 `[MEAS]`, start 3.12 `[MEAS]`,
end 8.63 `[MEAS]`. Because the pair is asymmetric in contrast, delta TEXT uses
`--color-success` `#15803D` / `--color-danger` `#B91C1C` instead (5.02 / 6.47 `[MEAS]`) `[J]`
for the substitution decision.

### 1.4 Dark theme

| Token | Value | Measured | Provenance |
|-------|-------|---------|-----------|
| `--color-dark-page-bg` | `#0F172A` | base | `[CSV]` colors.csv:15 (Government/Public Service, Notes: `High contrast navy + blue`) |
| `--color-dark-surface` | `#1E293B` | 1.22 vs page bg `[MEAS]` - separation carried by border + shadow, not luminance | `[CSV]` colors.csv:2 / :8 / :27 |
| `--color-dark-text` | `#E2E8F0` | 14.48 vs `#0F172A` `[MEAS]` AAA; 11.87 vs `#1E293B` `[MEAS]` AAA | `[CSV]` colors.csv:15 (Border col) |
| `--color-dark-muted` | `#94A3B8` | 6.96 vs `#0F172A` `[MEAS]` AA; 5.71 vs `#1E293B` `[MEAS]` AA | `[CSV]` charts.csv:25 / colors.csv:54 |
| `--color-dark-border` | `#334155` | 1.41 vs `#1E293B` `[MEAS]`, 1.72 vs `#0F172A` `[MEAS]` decorative | `[CSV]` colors.csv:7 / :8 |
| `--color-dark-primary` | `#60A5FA` | 5.75 vs `#1E293B` `[MEAS]`; 2.43 vs `#F8FAFC` `[MEAS]` (dark theme only) | `[J]` 设计判断（无本地出处） |
| `--color-dark-on-primary` | `#0F172A` | 7.02 vs `#60A5FA` `[MEAS]` AAA | `[CSV]` colors.csv:15 |

---

## 2. Spacing scale

Base unit: `styles.csv:51` (Swiss Modernism 2.0) Design System Variables = `--base-unit: 8px` `[CSV]`;
the BI dashboard row ships `--grid-gap: 8px` + `--card-padding: 12px` `[CSV]` styles.csv:29.
Steps 1,4,5,6,7,8 are exactly the generator's block at `MASTER.md:45-51` `[GEN]`;
`--space-3` (12px) is inserted from the CSV card padding. Multipliers are arithmetic on the
8px base, printed in `_evidence3_out.txt` `[MEAS]`.

| Token | px | rem | x base(8px) | Usage | Provenance |
|-------|----|-----|-------------|-------|-----------|
| `--space-1` | 4px | 0.25rem | 0.5 | tight gaps, badge padding | `[GEN]` MASTER.md:45 |
| `--space-2` | 8px | 0.5rem | 1.0 | icon gap, grid gap, minimum touch spacing | `[GEN]` MASTER.md:46 + `[CSV]` styles.csv:29 |
| `--space-3` | 12px | 0.75rem | 1.5 | dense card padding, control vertical padding | `[CSV]` styles.csv:29 (`--card-padding: 12px`) |
| `--space-4` | 16px | 1rem | 2.0 | standard padding | `[GEN]` MASTER.md:47 |
| `--space-5` | 24px | 1.5rem | 3.0 | section padding, drill indent | `[GEN]` MASTER.md:48 + `[CSV]` styles.csv:33 (`--level-indent: 24px`) |
| `--space-6` | 32px | 2rem | 4.0 | large gaps, modal padding | `[GEN]` MASTER.md:49 + `[GEN]` MASTER.md:145 |
| `--space-7` | 48px | 3rem | 6.0 | section margins, context bar | `[GEN]` MASTER.md:50 + `[CSV]` styles.csv:33 (`--context-bar-height: 48px`) |
| `--space-8` | 64px | 4rem | 8.0 | page top padding; collapsed rail width | `[GEN]` MASTER.md:51; 64px rail `[J]` 设计判断（无本地出处） |
| `--space-dense-band` | 8-12px | - | - | dashboard card padding band, never above 12px | `[CSV]` styles.csv:29 AI Prompt Keywords: `minimal padding (8-12px)` |

Component geometry (verbatim from CSV Design System Variables columns):

| Token | Value | Provenance |
|-------|-------|-----------|
| `--grid-columns` | 12 | `[CSV]` styles.csv:51 (`--grid-columns: 12`) + styles.csv:29 checklist `☐ Grid layout 12 columns` |
| `--grid-gap` | 8px | `[CSV]` styles.csv:29 |
| `--card-padding` | 12px | `[CSV]` styles.csv:29 |
| `--table-row-height` | 36px (4.5 x base) | `[CSV]` styles.csv:29 |
| `--sidebar-width` | 240px (30 x base) | `[CSV]` styles.csv:29 |
| `--header-height` | 56px (7 x base) | `[CSV]` styles.csv:29 |
| `--card-min-width` | 280px | `[CSV]` styles.csv:31 |
| `--sparkline-height` | 32px | `[CSV]` styles.csv:31 |
| `--back-button-size` | 40px | `[CSV]` styles.csv:33 |
| `--level-indent` | 24px | `[CSV]` styles.csv:33 |
| `--context-bar-height` | 48px | `[CSV]` styles.csv:33 |
| `--cohort-cell-size` | 40px | `[CSV]` styles.csv:36 |
| `--heatmap-cell-size` | 24px | `[CSV]` styles.csv:30 |
| `--legend-width` | 200px | `[CSV]` styles.csv:30 |
| `--arrow-size` | 16px | `[CSV]` styles.csv:34 |
| `--badge-padding` | 4px 8px | `[CSV]` styles.csv:34 |
| `--comparison-gap` | 2rem | `[CSV]` styles.csv:34 |
| `--scenario-toggle-width` | 48px | `[CSV]` styles.csv:35 |
| `--touch-target-min` | 44px x 44px | `[CSV]` ux-guidelines.csv:23 (Do: `Minimum 44x44px touch targets`) |
| `--touch-target-gap` | 8px | `[CSV]` ux-guidelines.csv:24 (Do: `Minimum 8px gap between touch targets`) |
| `--radius-control` | 8px | `[GEN]` MASTER.md:74 (buttons) / MASTER.md:122 (inputs) |
| `--radius-card` | 12px | `[GEN]` MASTER.md:103 |
| `--radius-modal` | 16px | `[GEN]` MASTER.md:144 |

Elevation:

| Token | Value | Provenance |
|-------|-------|-----------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | `[GEN]` MASTER.md:57 |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.1)` | `[GEN]` MASTER.md:58 |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | `[GEN]` MASTER.md:59 |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | `[GEN]` MASTER.md:60 |
| `--elevation-1..4` | `0 1px 3px .1` / `0 4px 6px .1` / `0 10px 20px .1` / `0 20px 40px .15` | `[CSV]` styles.csv:47 |
| `--alert-z-index` | 1000 | `[CSV]` styles.csv:32 |
| `--tooltip-bg` | `rgba(0,0,0,0.9)` | `[CSV]` styles.csv:30 |
