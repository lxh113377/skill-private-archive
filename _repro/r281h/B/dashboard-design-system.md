# Dashboard Design System - Internal Data-Analysis Admin (arm B deliverable)

Project slug: `data-analytics-dashboard` | Master: `design-system/data-analytics-dashboard/MASTER.md`
Detail sheet: `design-system/data-analytics-dashboard/TOKENS.md` | Page overrides: `.../pages/*.md`
Process authority: `_temp/r281h/B/SKILL.md` (ui-ux-pro-max v1.6.0 arm copy). Triage: `_triage.md`.
Every command + rc: `_exec_log.md`. Raw generator stdout: `_gen_stdout.txt`.

Provenance markers used below:
- `src:` = a line of a bundled local file (`D:/global_skills/ui-ux-pro-max/...`) or a script output written by
  this arm. Reproducible with `sed -n '<line>p' <file>`.
- `DJ:` = design judgement, **no local provenance**. Never to be quoted as script/CSV output.

---

## 0. Scope, platform, a11y level (from _triage.md)
Web, desktop-first responsive. Style = Data-Dense Dashboard (src: data/styles.csv:29 row 28, BI/Analytics).
Accessibility target = **WCAG 2.x AA** (src: data/styles.csv:29 Accessibility field; the generator returns the
same, src: _gen_stdout.txt RUN 3 STYLE block). AAA numbers are adopted only where they do not fight density.
Marketing-page pattern rows (Hero/Pricing/CTA) returned by the generator are **declined** for an internal
tool; only its token rows were used (DJ: adjudication, logged in _triage.md section 3).

## 1. Color tokens

```css
:root {
  /* core - src: data/colors.csv:9 (row 8,Analytics Dashboard) == src: gen MASTER.md:21-25 */
  --color-primary:      #1E40AF;   /* src colors.csv:9 Primary */
  --color-secondary:    #3B82F6;   /* src colors.csv:9 Secondary */
  --color-cta:          #F59E0B;   /* src colors.csv:9 CTA */
  --color-background:   #F8FAFC;   /* src colors.csv:9 Background */
  --color-text:         #1E3A8A;   /* src colors.csv:9 Text */
  --color-border:       #DBEAFE;   /* src colors.csv:9 Border (column the script never emitted) */
  /* surfaces - src: data/styles.csv:29 Primary Colors field */
  --color-surface:         #FFFFFF;   /* DJ: hex not published; standard card white under a #F8FAFC page */
  --color-surface-neutral: #F5F5F5;   /* src styles.csv:29 "light grey/white #F5F5F5" */
  --color-text-strong:     #333333;   /* src styles.csv:29 "dark text #333333" */
  --color-row-alt:         #F1F5F9;   /* DJ: zebra tint; src only says "Alternating rows (white/light grey)" (_gen_stdout.txt RUN 2) */
  --color-row-highlight:   #FFFACD;   /* src _gen_stdout.txt RUN 2 Color Strategy */
  /* semantic status - src: data/styles.csv:29 "Chart colors" */
  --color-success: #22C55E;   /* src styles.csv:29 */
  --color-warning: #F59E0B;   /* src styles.csv:29 */
  --color-danger:  #EF4444;   /* src styles.csv:29 */
  --color-neutral: #6B7280;   /* DJ: src says "neutral (grey)", no hex published */
  /* live-monitor alert ramp - src: data/styles.csv:32 (row 31 Real-Time Monitoring) */
  --alert-critical: #FF0000;  /* src styles.csv:32 */
  --alert-warning:  #FFA500;  /* src styles.csv:32 */
  --alert-normal:   #22C55E;  /* src styles.csv:32 */
  /* chart series - src: data/charts.csv:14 (row 13 waterfall), :2 (row 1 line) */
  --chart-increase: #4CAF50;  /* src charts.csv:14 */
  --chart-decrease: #F44336;  /* src charts.csv:14 */
  --chart-start:    #2196F3;  /* src charts.csv:14 */
  --chart-end:      #0D47A1;  /* src charts.csv:14 */
  --chart-line:     #0080FF;  /* src charts.csv:2, series fill 20% */
  --chart-edge:     #90A4AE;  /* src charts.csv:17, applied at 60% opacity */
}
```

Measured contrast for these pairs (WCAG relative-luminance formula, computed by this arm - see
`design-system/data-analytics-dashboard/_contrast_calc.txt`; the **hexes** are src-cited, the **ratios** are
arm-computed, not from any CSV):

| Pair | Ratio | Ruling |
|---|---|---|
| `#1E3A8A` on `#F8FAFC` | 9.90:1 | AA pass - default body text |
| `#1E40AF` on `#FFFFFF` | 8.72:1 | AA pass - links, primary text on card |
| `#FFFFFF` on `#F59E0B` | 2.15:1 | **FAIL** -> CTA label must be `#1E3A8A` |
| `#1E3A8A` on `#F59E0B` | 4.82:1 | AA pass - the CTA pair actually shipped |
| `#333333` on `#F5F5F5` | 11.59:1 | AA pass - dense table text |
| `#EF4444` on `#FFFFFF` | 3.76:1 | AA large/UI only -> danger text uses `#B91C1C` (DJ: darkened tint) or 18px+/bold |
| `#22C55E` on `#FFFFFF` | 2.28:1 | **FAIL** -> success is never bare colored text; icon + label required |
| `#6B7280` on `#FFFFFF` | 4.83:1 | AA pass - secondary/metadata |

Rules: contrast >= 4.5:1 (src: data/ux-guidelines.csv:37; MASTER.md:198); never color alone - pair with icon
or pattern (src: data/charts.csv:2 Accessibility Notes; B/SKILL.md:65 priority 10); no raw hex in components
(src: B/SKILL.md:61 priority 6 anti-pattern "Raw hex in components").

## 2. Spacing scale

| Token | px | rem | src / note |
|---|---|---|---|
| `--space-xxs` | 2 | 0.125 | DJ: extension step, not in generator output |
| `--space-xs` | 4 | 0.25 | src: MASTER.md:45 |
| `--space-sm` | 8 | 0.5 | src: MASTER.md:46 |
| `--space-md` | 16 | 1 | src: MASTER.md:47 |
| `--space-lg` | 24 | 1.5 | src: MASTER.md:48 |
| `--space-xl` | 32 | 2 | src: MASTER.md:49 |
| `--space-2xl` | 48 | 3 | src: MASTER.md:50 |
| `--space-3xl` | 64 | 4 | src: MASTER.md:51 |
| `--radius-md` | 8 | - | src: MASTER.md:74 / :91 / :122 (buttons, inputs) |
| `--radius-lg` | 12 | - | src: MASTER.md:103 (card) |
| `--shadow-md` | 0 4px 6px rgba(0,0,0,0.1) | - | src: MASTER.md:58 |
| touch target | 44x44 | - | src: data/ux-guidelines.csv:23; Tailwind `min-h-[44px] min-w-[44px]` src: data/stacks/html-tailwind.csv:35 |
| touch spacing | 8 | - | src: data/ux-guidelines.csv:24 |
| table row height | 36 | - | DJ: density call, backed only by the qualitative "minimal padding" in src: data/styles.csv:29 |
| table cell padding | 8 v / 12 h | - | DJ: same qualitative backing only |
| sidebar width | 240 collapsed 56 | - | DJ: no local numeric source |
| content max width | 1400 | - | src: pages/overview.md:16 |
| grid columns | 12 | - | src: pages/overview.md:17 |

Native floors kept separate, not merged: iOS 44pt / Android 48dp / web WCAG 2.2 24 CSS px
(src: data/app-interface.csv:7 - its Don't column explicitly forbids collapsing them into one number).

## 3. Typography

Family: Heading **Fira Code**, Body **Fira Sans** (src: MASTER.md:31-32 == data/typography.csv:43 row
`42,Dashboard Data`; rationale "Code for data, Sans for labels" same line).
Import: src: MASTER.md:38.
Alternates (src: B/SKILL.md:96 requires 2-3 pairs): Minimal Swiss Inter/Inter (src: data/typography.csv:6,
Best For "Dashboards, admin panels") and Friendly SaaS Plus Jakarta Sans (src: data/typography.csv:14).

Type scale (src: references/quick-reference.md:125 publishes the ladder "12 14 16 18 24 32"):

| Token | px | rem | Weight | src |
|---|---|---|---|---|
| `--font-size-display` | 48 | 3.0 | 600 | src: data/styles.csv:31 upper bound of "24-48px for metric" (DJ: assigning it to display) |
| `--font-size-h1` | 32 | 2.0 | 600 | src: quick-reference.md:125 |
| `--font-size-kpi` | 24 | 1.5 | 600 | src: data/styles.csv:31 lower bound; also ladder step |
| `--font-size-h2` | 24 | 1.5 | 600 | src: quick-reference.md:125 |
| `--font-size-h3` | 18 | 1.125 | 600 | src: quick-reference.md:125 |
| `--font-size-body` | 16 | 1.0 | 400 | src: quick-reference.md:125 + :104 (min 16px body); B/SKILL.md:61 "Base 16px"; MASTER.md:123 |
| `--font-size-label` | 14 | 0.875 | 500 | src: quick-reference.md:125 |
| `--font-size-micro` | 12 | 0.75 | 500 | src: quick-reference.md:125; floor - nothing below 12 for body (B/SKILL.md:61) |
| `--line-height-body` | 1.5 | - | - | src: quick-reference.md:122 (range 1.5-1.75); B/SKILL.md:61 |
| `--line-height-tight` | 1.25 | - | - | DJ: for KPI numerals only, no published value |
| weights | 300-700 | - | - | src: data/typography.csv:43 Google Fonts weight list |
| tabular numerals | `font-variant-numeric: tabular-nums` | - | - | DJ: alignment need for numeric columns |
| font loading | `font-display: swap` + metric fallback | - | - | src: data/ux-guidelines.csv:51 and :76 |

## 4. Component states (default / hover / focus / disabled / loading / error / empty)

Applies to Button, Input, Table row, Card/KPI tile, Chart panel. src for the state list itself:
B/SKILL.md:97 ("Always cover: empty/loading/error, keyboard navigation, focus states").

| State | Token values | src |
|---|---|---|
| default | bg `--color-surface`, text 16px/1.5, radius 8px, `cursor: pointer` | radius src: MASTER.md:74/:91/:122; cursor src: MASTER.md:196 |
| hover | bg -> `--color-row-alt` or shadow md->lg, translate <= 2px, duration 150-200ms (control) / 200-300ms (card) | src: data/ux-guidelines.csv:30; data/motion.csv:2 (150-200ms, "Keep displacement under 2px") and :3 (200-300ms); MASTER.md:197 |
| hover (table row) | row highlight, no layout shift | src: data/styles.csv:29 "row highlighting on hover"; MASTER.md:183 forbids layout-shifting hovers |
| focus | `:focus-visible` ring 2px `--color-primary` offset 2px; input box-shadow `0 0 0 3px #1E40AF20`; **never** bare `outline:none` | src: data/web-interface.csv:8 (`focus-visible:ring-2`), :9; data/ux-guidelines.csv:29; box-shadow src: MASTER.md:130; AAA 3-4px variant src: data/styles.csv:9 |
| disabled | `opacity: 0.5` (published range 0.38-0.5), `cursor: not-allowed`, keep `aria-disabled`, stay reachable | src: data/ux-guidelines.csv:32 (`opacity-50 cursor-not-allowed`); references/quick-reference.md:178 |
| loading | trigger > 300ms; spinner <= 1s, skeleton > 1s; exit duration 60-70% of enter; list stagger 30-50ms; `aria-busy` | src: data/ux-guidelines.csv:11 (skeleton/spinner) + :79 (">300ms") + :33 (loading button); references/quick-reference.md:76 (>1s skeleton), :152 (exit 60-70%), :153 (stagger 30-50ms); data/stacks/html-tailwind.csv:36 |
| error | border + icon + inline message next to the field, `role=alert`/`aria-live`, focus moves to first error, never color alone | src: data/web-interface.csv:16 (inline errors); data/ux-guidelines.csv:45 (must be announced); danger hex src: data/styles.csv:29 |
| empty | heading + one primary action, never a blank chart, 24px+ icon | src: references/quick-reference.md:174 and :241 ("No data yet" + guidance); data/ux-guidelines.csv:80 ("No items yet. Create one!") |

Recorded conflict (not averaged): data/ux-guidelines.csv:33 says disable the submit button while loading;
data/web-interface.csv:15 says keep it enabled with a spinner. Ruling = **hold focus, `aria-busy=true`,
block re-submit in state, do not remove from tab order** (DJ: adjudication; satisfies both intents).

Cross-cutting interaction budgets: input latency ~100ms and tap feedback within 100ms
(src: references/quick-reference.md:77, :78); per-frame main-thread budget ~16ms (:75); virtualize > 50 rows
(src: references/quick-reference.md:74; data/web-interface.csv:17); `prefers-reduced-motion: reduce` renders
final state immediately (src: data/ux-guidelines.csv:10; data/motion.csv:2); destructive actions confirm
(src: data/web-interface.csv:24).

## 5. Breakpoints

| Name | min-width | Dashboard ruling | src |
|---|---|---|---|
| `xs` | 320 | test floor, no clipping | src: data/stacks/html-tailwind.csv:32 |
| `sm` | 375 | 1 column, KPI stack, table -> card list | src: references/quick-reference.md:103; MASTER.md:201; references/pro-rules.md:71 |
| `md` | 768 | 2 columns, filters as sheet | src: references/quick-reference.md:103 |
| `lg` | 1024 | 3-4 columns, persistent sidebar | src: references/quick-reference.md:103 |
| `xl` | 1280 | table regains width | src: data/stacks/html-tailwind.csv:32 |
| `2xl` | 1440 | max density, container cap 1400px | src: references/quick-reference.md:103; MASTER.md:201; pages/overview.md:16 |
| `3xl` | 1536 | test only | src: data/stacks/html-tailwind.csv:32 |

Mobile-first authoring (src: data/stacks/html-tailwind.csv:31; B/SKILL.md:60); viewport meta
`width=device-width, initial-scale=1`, zoom never disabled (src: references/quick-reference.md:101);
no horizontal page scroll - wide tables scroll inside their own container (src:
references/quick-reference.md:106; pages/overview.md:34; MASTER.md:203); prefer `min-h-dvh` over `100vh`
(src: references/quick-reference.md:113); charts simplify below `md` - fewer ticks, bars over columns
(src: references/quick-reference.md:240); JS media-state via `useMediaQuery('(max-width: 767px)')`
(src: data/react-performance.csv:22); gutters step up at larger widths (src: references/pro-rules.md:59).

## 6. Retrieval contract across sessions (B/SKILL.md:85-88)
1. Read `design-system/data-analytics-dashboard/MASTER.md`.
2. Check `design-system/data-analytics-dashboard/pages/<page>.md` - if present it **overrides** MASTER.
3. Otherwise use MASTER exclusively.
Persisted page overrides in this arm: `overview.md`, `data-table.md`, `filters.md`, `metrics-detail.md`
(all written by `scripts/search.py --page` under the package-form invocation - see _exec_log.md E14-E17).

## 7. Known generator defects found on this host (honest record)
- `--page` through the documented `python <path>/search.py` form fails with ImportError
  (scripts/design_system.py:925 relative import) - rc=1, four attempts, logged E08-E11. Workaround = package
  form `PYTHONPATH=D:/global_skills/ui-ux-pro-max python -m scripts.search ...` (rc=0).
- The generator returns a landing-page PATTERN (Hero / Pricing / CTA sections) for a dashboard query
  (src: _gen_stdout.txt RUN 3). It is kept verbatim in the generated files for reproducibility but is
  overridden by `pages/*.md` intent and by _triage.md section 3 for actual use.
- The generator emits no Border color, no type scale, no component-state matrix, and no breakpoint ladder;
  those four gaps are what TOKENS.md and this file add, each value carrying either a src: or a DJ: marker.

## 8. Pre-delivery gate (all 10 must be checkable)
src: MASTER.md:194-203 + B/SKILL.md:65. 1) no emoji icons 2) cursor:pointer everywhere clickable
3) hover 150-300ms 4) contrast >= 4.5:1 5) visible focus 6) prefers-reduced-motion 7) tested at
375/768/1024/1440 8) nothing under a fixed navbar 9) no horizontal mobile scroll 10) legends + tooltips on
every chart, color never alone.
