# Token Sheet - Internal Data-Analysis Dashboard (arm B)

Companion to `MASTER.md` (script-generated, Do Not Hand-Edit That File). This sheet adds the five token
classes the task requires and gives **provenance for every number**. All paths are read-only sources under
`D:/global_skills/ui-ux-pro-max/`; `gen:*` means "produced by the bundled script, captured verbatim in
`_gen_stdout.txt` / the file this script wrote".

Provenance legend:
- `CSV file:line` = exact line of a bundled data file (line = physical file line, `sed -n '<line>p'` reproducible).
- `gen:<file>:<line>` = output of `scripts/search.py --design-system --persist` / `scripts/design_system.py` as written to disk in this arm.
- **[DJ]** = design judgement, no local provenance. Never presented as script or CSV output.

---

## 1. Color tokens

Core palette - source `gen:design-system/data-analytics-dashboard/MASTER.md:21-25` (script) and, identical,
`data/colors.csv:9` row `8,Analytics Dashboard`:

| Token | Value | Provenance |
|---|---|---|
| `--color-primary` | `#1E40AF` | `data/colors.csv:9` col Primary; `gen:MASTER.md:21` |
| `--color-secondary` | `#3B82F6` | `data/colors.csv:9` col Secondary; `gen:MASTER.md:22` |
| `--color-cta` | `#F59E0B` | `data/colors.csv:9` col CTA; `gen:MASTER.md:23` |
| `--color-background` | `#F8FAFC` | `data/colors.csv:9` col Background; `gen:MASTER.md:24` |
| `--color-text` | `#1E3A8A` | `data/colors.csv:9` col Text; `gen:MASTER.md:25` |
| `--color-border` | `#DBEAFE` | `data/colors.csv:9` col Border (script did not emit this column) |
| `--color-surface-neutral` | `#F5F5F5` | `data/styles.csv:29` Primary Colors: "light grey/white #F5F5F5" |
| `--color-text-strong` | `#333333` | `data/styles.csv:29` Primary Colors: "dark text #333333" |
| `--color-row-highlight` | `#FFFACD` | `gen:_gen_stdout.txt` RUN 2 Color Strategy (design_system.py) |

Semantic status colors - `data/styles.csv:29` "Chart colors" field:

| Token | Value | Provenance |
|---|---|---|
| `--color-success` | `#22C55E` | `data/styles.csv:29` Chart colors: success (green #22C55E) |
| `--color-warning` | `#F59E0B` | `data/styles.csv:29` Chart colors: warning (amber #F59E0B) |
| `--color-danger` | `#EF4444` | `data/styles.csv:29` Chart colors: alert (red #EF4444) |
| `--color-neutral` | `#6B7280` | **[DJ]** - "neutral (grey)" in `data/styles.csv:29` names no hex; this value is mine |
| `--color-alert-critical` | `#FF0000` | `data/styles.csv:32` Alert colors: critical (red #FF0000) |
| `--color-alert-warning2` | `#FFA500` | `data/styles.csv:32` warning (orange #FFA500) |
| `--color-alert-normal` | `#22C55E` | `data/styles.csv:32` normal (green #22C55E) |

Chart series (waterfall / cumulative deltas) - `data/charts.csv:14` row 13:

| Token | Value | Provenance |
|---|---|---|
| `--chart-increase` | `#4CAF50` | `data/charts.csv:14` "Increases: #4CAF50" |
| `--chart-decrease` | `#F44336` | `data/charts.csv:14` "Decreases: #F44336" |
| `--chart-start` | `#2196F3` | `data/charts.csv:14` "Start: #2196F3" |
| `--chart-end` | `#0D47A1` | `data/charts.csv:14` "End: #0D47A1" |
| `--chart-edge` | `#90A4AE` @ 60% | `data/charts.csv:17` "Edges: #90A4AE 60% opacity" |
| `--chart-line-default` | `#0080FF` @ 20% fill | `data/charts.csv:2` "Primary: #0080FF ... Fill: 20% opacity" |

Rules attached to the palette:
- Contrast floor 4.5:1 for body text - `data/ux-guidelines.csv:37`; `gen:MASTER.md:198`.
- Do not convey meaning by color alone (pattern overlay / legend) - `data/styles.csv:9` Secondary Colors and
  `data/charts.csv:2` Accessibility Notes; SKILL.md priority row 10 (`B/SKILL.md:65`).
- No raw hex inside components; every color consumed through a token - SKILL.md priority row 6 (`B/SKILL.md:61`).

## 2. Spacing scale

Emitted by the generator (`gen:MASTER.md:45-51`, physical lines 45-51):

| Token | px | rem | Provenance |
|---|---|---|---|
| `--space-xs` | 4 | 0.25 | `gen:MASTER.md:45` |
| `--space-sm` | 8 | 0.5 | `gen:MASTER.md:46` |
| `--space-md` | 16 | 1 | `gen:MASTER.md:47` |
| `--space-lg` | 24 | 1.5 | `gen:MASTER.md:48` |
| `--space-xl` | 32 | 2 | `gen:MASTER.md:49` |
| `--space-2xl` | 48 | 3 | `gen:MASTER.md:50` |
| `--space-3xl` | 64 | 4 | `gen:MASTER.md:51` |
| `--space-xxs` | 2 | 0.125 | **[DJ]** - extension step for icon/optical alignment; not in generator output |

Interaction minimums:
- Touch target 44x44 px (mobile) - `data/ux-guidelines.csv:23`; Tailwind form `min-h-[44px] min-w-[44px]` -
  `data/stacks/html-tailwind.csv:35`. Native floors 44pt iOS / 48dp Android / 24 CSS px WCAG 2.2 -
  `data/app-interface.csv:7`: **do not collapse these into one number.**
- 8 px gap between adjacent touch targets - `data/ux-guidelines.csv:24` (`gap-2`).
- Cell density for the main table **[DJ]**: 8 px vertical / 12 px horizontal per row, row height 36 px.
  Reasoning only: the style mandates "minimal padding / maximum data visibility" (`data/styles.csv:29`
  Keywords) - the CSV does not publish a numeric row height.
- Card padding 24 px, card radius 12 px - `gen:MASTER.md:103-104`.
- Shadow ramp `--shadow-sm/md/lg/xl` = `0 1px 2px .05` / `0 4px 6px .1` / `0 10px 15px .1` / `0 20px 25px .15`
  - `gen:MASTER.md:57-60`.

## 3. Typography

Family (generator choice, `gen:MASTER.md:31-34` = `data/typography.csv:43` row `42,Dashboard Data`):
- Heading: **Fira Code** (mono), Body: **Fira Sans** (sans).
- CSS import: `gen:MASTER.md:38`; Google Fonts selection `gen:MASTER.md:34`.
- Rationale in-file: "Code for data, Sans for labels" - `data/typography.csv:43` Notes field.

Two alternates, required by SKILL.md:96 ("2-3 font pair options"):
1. Minimal Swiss - Inter / Inter - `data/typography.csv:6` row 5, Best For "Dashboards, admin panels".
2. Friendly SaaS - Plus Jakarta Sans - `data/typography.csv:14` row 13, Best For "... dashboards, B2B".
3. (chosen) Dashboard Data - Fira Code / Fira Sans - `data/typography.csv:43` row 42.

Type scale (ladder is published in `references/quick-reference.md:125`: "e.g. 12 14 16 18 24 32"):

| Token | px | Provenance |
|---|---|---|
| `--font-size-display` | 48 | `data/styles.csv:31` "large font-size (24-48px) for metric" upper bound; **[DJ]** for use as KPI max |
| `--font-size-kpi` | 24 | `data/styles.csv:31` lower bound of same 24-48px range; also in the `quick-reference.md:125` ladder |
| `--font-size-h1` | 32 | `references/quick-reference.md:125` ladder top step |
| `--font-size-h2` | 24 | `references/quick-reference.md:125` |
| `--font-size-h3` | 18 | `references/quick-reference.md:125` |
| `--font-size-body` | 16 | `references/quick-reference.md:125`; min 16px body `references/quick-reference.md:104`; SKILL.md:61 "Base 16px"; `gen:MASTER.md:123` (input font-size 16px) |
| `--font-size-label` | 14 | `references/quick-reference.md:125` |
| `--font-size-micro` | 12 | `references/quick-reference.md:125`; floor only - body text below 12px is an anti-pattern (SKILL.md:61) |
| `--line-height-body` | 1.5 | `references/quick-reference.md:122` ("1.5-1.75"), SKILL.md:61 |
| `--line-height-tight` | 1.25 | **[DJ]** - within no published value; used for KPI numerals only |
| `--font-weight-*` | 400 / 500 / 600 / 700 | `data/typography.csv:43` Google Fonts URL weight list |

Tabular numerals for all metric columns **[DJ]** (no local numeric provenance; `font-variant-numeric: tabular-nums`).
Font loading: `font-display: swap` + metric-compatible fallback - `data/ux-guidelines.csv:51` and `:76`.

## 4. Component states

Applied to Button / Input / Table row / Card / Chart tile. Durations are shared motion tokens.

| State | Value(s) | Provenance |
|---|---|---|
| default | surface `#FFFFFF`  **[DJ]** hex; text 16px/1.5; radius 8px; `cursor:pointer` | radius 8px `gen:MASTER.md:74,91,122`; cursor rule `gen:MASTER.md:196` |
| hover | bg `gray-100` shift, 150-200ms micro / 200-300ms card, translate <= 2px, shadow sm->md | `data/ux-guidelines.csv:30`; `data/motion.csv:2` (150-200ms), `:3` (200-300ms, "Keep displacement under 2px"); `gen:MASTER.md:197` (150-300ms); table row highlight `data/styles.csv:29` |
| focus | `:focus-visible` ring 2px, never bare `outline:none`; control box-shadow `0 0 0 3px #1E40AF20` | `data/web-interface.csv:8` (`focus-visible:ring-2`), `:9`; `data/ux-guidelines.csv:29`; ring value `gen:MASTER.md:130`; AAA variant 3-4px `data/styles.csv:9` |
| disabled | `opacity:0.5` (range 0.38-0.5), `cursor:not-allowed`, `aria-disabled` kept in tab order | `data/ux-guidelines.csv:32` (`opacity-50 cursor-not-allowed`); `references/quick-reference.md:178` (0.38-0.5 + semantic attr) |
| loading | spinner for <=1s, skeleton for >1s, trigger at >300ms, exit 60-70% of enter, 30-50ms stagger | `data/ux-guidelines.csv:11`, `:79` (>300ms), `references/quick-reference.md:76` (>1s skeleton), `:152` exit-faster, `:153` stagger 30-50ms; `data/stacks/html-tailwind.csv:36` |
| error | border `#EF4444`, message inline next to field, `role=alert` / `aria-live`, focus first error | `data/ux-guidelines.csv:45`; `data/web-interface.csv:16`; `gen:MASTER.md:184` (low-contrast forbidden) |
| empty | "No data yet" + one action, never a blank chart, 24px+ icon | `references/quick-reference.md:174`, `:241`; `data/ux-guidelines.csv:80` ("No items yet. Create one!") |

Conflict on the loading-button state, recorded rather than averaged:
- `data/ux-guidelines.csv:33` says disable the button while submitting.
- `data/web-interface.csv:15` says keep it enabled and show a spinner.
- Ruling for this dashboard: **keep focus on the button, `aria-busy=true`, block duplicate submits in state, do
  not remove the element from the tab order** - this satisfies the a11y intent of both rows. **[DJ]** adjudication.

Other binding interaction numbers:
- Input latency budget ~100 ms, tap feedback within 100 ms - `references/quick-reference.md:77`, `:78`.
- Per-frame main-thread budget ~16 ms - `references/quick-reference.md:75`.
- Virtualize any list/table over 50 rows - `references/quick-reference.md:74`, `data/web-interface.csv:17`.
- `prefers-reduced-motion: reduce` honored everywhere (render final state immediately) - `data/ux-guidelines.csv:10`, `data/motion.csv:2`.
- Destructive actions (delete saved view / drop dataset) need confirm - `data/web-interface.csv:24`.

## 5. Breakpoints

| Token | min-width | Layout ruling | Provenance |
|---|---|---|---|
| `bp-xs` (test floor) | 320 | content must not clip | `data/stacks/html-tailwind.csv:32` |
| `bp-sm` | 375 | 1 column; KPI cards stacked; table -> card list | `references/quick-reference.md:103`; `gen:MASTER.md:201`; `references/pro-rules.md:71` |
| `bp-md` | 768 | 2 columns; filters in a sheet | `references/quick-reference.md:103` |
| `bp-lg` | 1024 | 3-4 columns; persistent sidebar | `references/quick-reference.md:103` |
| `bp-xl` | 1280 | table regains horizontal real estate | `data/stacks/html-tailwind.csv:32` |
| `bp-2xl` | 1440 | max data density; container cap below | `references/quick-reference.md:103`; `gen:MASTER.md:201` |
| `bp-3xl` | 1536 | test only | `data/stacks/html-tailwind.csv:32` |

- Mobile-first: author base styles at `bp-sm` and add up - `data/stacks/html-tailwind.csv:31`, SKILL.md:60.
- Viewport meta `width=device-width, initial-scale=1`, zoom never disabled - `references/quick-reference.md:101`, SKILL.md:60.
- Container max width 1400 px or full-bleed, 12-column grid - `gen:pages/overview.md:16-17`.
- No horizontal page scroll; wide tables scroll **inside** their own container - `references/quick-reference.md:106`, `gen:pages/overview.md:34`, `gen:MASTER.md:203`.
- Media query form for JS-driven layout state: `useMediaQuery('(max-width: 767px)')` - `data/react-performance.csv:22`.
- Charts must simplify on small screens (fewer ticks, bar instead of column) - `references/quick-reference.md:240`.
- `min-h-dvh` over `100vh` on mobile - `references/quick-reference.md:113`.

## Acceptance gate (run before shipping any page)

From `gen:MASTER.md:194-203` and SKILL.md:65 (row 10) - every item must be checkable:
1. No emoji as icon; SVG only (Heroicons/Lucide) - `gen:MASTER.md:194`.
2. `cursor:pointer` on every clickable element - `gen:MASTER.md:196`.
3. Hover states 150-300 ms - `gen:MASTER.md:197`.
4. Text contrast >= 4.5:1 - `gen:MASTER.md:198`.
5. Visible focus states - `gen:MASTER.md:199`.
6. `prefers-reduced-motion` respected - `gen:MASTER.md:200`.
7. Tested at 375 / 768 / 1024 / 1440 - `gen:MASTER.md:201`.
8. Nothing hidden behind a fixed navbar - `gen:MASTER.md:202`.
9. No horizontal scroll on mobile - `gen:MASTER.md:203`.
10. Legends + tooltips on every chart, color never alone - SKILL.md:65.
