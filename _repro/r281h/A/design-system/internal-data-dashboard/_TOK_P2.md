---

## 3. Typography

### 3.1 Font families

The pair is the CSV row the generator selected: `typography.csv:43` (row `No 42`,
`Font Pairing Name = Dashboard Data`, Category `Mono + Sans`) `[CSV]`; `MASTER.md:31-32`
carries the same pair `[GEN]`.

| Token | Family | Role | Provenance |
|-------|--------|------|-----------|
| `--font-heading` | `Fira Code` | KPI numerals, table figures, code, metric labels | `[CSV]` typography.csv:43 col `Heading Font` |
| `--font-body` | `Fira Sans` | nav, labels, prose, table text | `[CSV]` typography.csv:43 col `Body Font` |
| `--font-mono` | `Fira Code` | query / SQL / JSON cells | `[CSV]` typography.csv:43 col `Tailwind Config` (`mono: ['Fira Code', 'monospace']`) |
| `--font-fallback` | `ui-monospace, SFMono-Regular, Menlo, monospace` / `system-ui, -apple-system, Segoe UI, Roboto, sans-serif` | load failure + FOIT guard | `[J]` 设计判断（无本地出处）; the `display=swap` requirement is `[CSV]` typography.csv:43 CSS Import + `[CSV]` ux-guidelines.csv:51 |
| `--font-weight-light` | 300 | large KPI numerals only | `[CSV]` typography.csv:43 Google Fonts URL (`Fira+Sans:wght@300;...`) |
| `--font-weight-regular` | 400 | body | `[CSV]` typography.csv:43 URL |
| `--font-weight-medium` | 500 | labels, filter chips | `[CSV]` typography.csv:43 URL |
| `--font-weight-semibold` | 600 | buttons, card titles | `[CSV]` typography.csv:43 URL + `[GEN]` MASTER.md:75 (`font-weight: 600`) |
| `--font-weight-bold` | 700 | table header, delta badges | `[CSV]` typography.csv:43 URL |

CSS import verbatim from typography.csv:43 col `CSS Import` (echoed at MASTER.md:38) `[CSV]`:

```css
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');
```

Tailwind config verbatim from the same row `[CSV]` typography.csv:43:
`fontFamily: { mono: ['Fira Code', 'monospace'], sans: ['Fira Sans', 'sans-serif'] }`

Alternative pairs (SKILL.md line 50 asks for 2-3 options; each option below is a real CSV row):

| Option | Heading / Body | Switch to it when | Provenance |
|--------|----------------|-------------------|-----------|
| B | `Exo` / `Roboto Mono` | research / ML-flavoured analytics | `[CSV]` typography.csv:48 (row No 47 Science/Tech; keywords `research, data, precise`) |
| C | `Share Tech Mono` / `Fira Code` | NOC / live-monitoring wall | `[CSV]` typography.csv:52 (row No 51 Tech/HUD Mono; Best For includes `dashboards`) |
| D | `Atkinson Hyperlegible` / `Atkinson Hyperlegible` | low-vision accessibility override | `[CSV]` typography.csv:49 (row No 48 Accessibility First; Notes: `Designed for maximum legibility`) |

### 3.2 Type scale

Anchor set is verbatim from `ux-guidelines.csv:75` col Do: `Type scale (12 14 16 18 24 32)` `[CSV]`;
48px comes from `styles.csv:31` (`--kpi-font-size: 48px`, `large font-size (24-48px) for metrics`) `[CSV]`;
the 12-14px dense band from `styles.csv:29` (`font-size: 12-14px`) `[CSV]`; root 16px from
`ux-guidelines.csv:68` (`Minimum 16px body text on mobile`) `[CSV]`. rem values and step ratios are
arithmetic on those anchors, printed in `_evidence2_out.txt` `[MEAS]`. The ladder is deliberately
NOT a constant modular ratio (steps run 1.167 / 1.143 / 1.125 / 1.333 / 1.333 / 1.500 `[MEAS]`):
keeping the CSV anchor set verbatim was chosen over forcing a 1.25 scale `[J]` 设计判断（无本地出处，选择理由）.

| Token | px | rem (root 16) | line-height | weight | Use | Provenance |
|-------|----|---------------|-------------|--------|-----|-----------|
| `--text-micro` | 12px | 0.75rem | 18px (1.5) | 400 | axis labels, badges, timestamps | `[CSV]` ux-guidelines.csv:75 + styles.csv:29 |
| `--text-dense` | 13px | 0.8125rem | 20px (1.5) | 400 | data table cells | `[J]` 设计判断（无本地出处） - midpoint of the 12-14px band in styles.csv:29 |
| `--text-sm` | 14px | 0.875rem | 21px (1.5) | 400 | secondary UI text, chips | `[CSV]` ux-guidelines.csv:75 |
| `--text-base` | 16px | 1rem | 24px (1.5) | 400 | body, form controls | `[CSV]` ux-guidelines.csv:75 + :68 + `[GEN]` MASTER.md:123 |
| `--text-lg` | 18px | 1.125rem | 27px (1.5) | 500 | card titles, section heads | `[CSV]` ux-guidelines.csv:75 |
| `--text-xl` | 24px | 1.5rem | 32px (1.33) | 600 | page title, secondary KPI | `[CSV]` ux-guidelines.csv:75 + styles.csv:31 |
| `--text-2xl` | 32px | 2rem | 40px (1.25) | 600 | hero KPI number | `[CSV]` ux-guidelines.csv:75 |
| `--text-kpi` | 48px | 3rem | 56px (1.17) | 700 | primary KPI value, max 6 per row | `[CSV]` styles.csv:31 (`--kpi-font-size: 48px`, checklist `☐ KPIs 4-6 maximum`) |
| `--leading-body` | 1.5 | - | - | - | body copy floor | `[CSV]` ux-guidelines.csv:73 (Use 1.5-1.75 for body text) |
| `--leading-relaxed` | 1.625 | - | - | - | tooltips, help text | `[CSV]` ux-guidelines.csv:73 Code Example (`leading-relaxed (1.625)`) |
| `--tracking-micro` | 0.02em | - | - | - | uppercase 12px labels | `[J]` 设计判断（无本地出处） |
| `--font-variant-numeric` | `tabular-nums` | - | - | - | every numeric column so digits align | `[J]` 设计判断（无本地出处） |
| `--decimal-places` | 2 | - | - | - | currency / ratio formatting | `[CSV]` styles.csv:37 (`--decimal-places: 2`) |
| `--variance-threshold` | 10% | - | - | - | when a delta turns warning/danger colour | `[CSV]` styles.csv:37 (`--variance-threshold: 10%`) |
| `--table-header-bg` | `#F3F4F6` | - | - | 600 | sticky table header fill | `[CSV]` styles.csv:37 (`--table-header-bg: #F3F4F6`) |
| `--currency-symbol` | `$` | - | - | - | default locale for money columns | `[CSV]` styles.csv:37 |

Line-heights at 16px and below apply the CSV 1.5 rule arithmetically; the tightened 1.33 /
1.25 / 1.17 leading for 24/32/48px numerals is `[J]` 设计判断（无本地出处）.

---

## 4. Component states

SKILL.md line 50-51 requires component states and mandates empty/loading/error, keyboard
navigation, focus states and contrast coverage. Six states per interactive control
(default / hover / focus / disabled / loading / error) plus empty for containers.

### 4.0 Timing and motion tokens

| Token | Value | Provenance |
|-------|-------|-----------|
| `--duration-fast` | 150ms | `[GEN]` MASTER.md:197 checklist band 150-300ms (lower bound) |
| `--duration-base` | 200ms | `[GEN]` MASTER.md:76/93/106/124 (`transition: all 200ms ease`) + `[CSV]` motion.csv:3 (200-300ms, power2.out) |
| `--duration-slow` | 300ms | `[GEN]` MASTER.md:197 band upper bound + `[CSV]` styles.csv:33 (`--expand-duration: 300ms`) |
| `--ease-standard` | `ease` | `[GEN]` MASTER.md:76 |
| `--ease-gsap` | `power2.out` | `[CSV]` motion.csv:3 col Easing |
| `--drill-transition` | `300ms ease` | `[CSV]` styles.csv:33 |
| `--pulse-animation` | `pulse 2s infinite` | `[CSV]` styles.csv:32 |
| `--toast-duration` | `5s` | `[CSV]` styles.csv:32 |
| `--update-interval` | `5s` | `[CSV]` styles.csv:32 |
| `--loading-threshold` | 300ms | `[CSV]` ux-guidelines.csv:79 (spinner/skeleton for operations > 300ms) |
| `--reduced-motion` | durations -> 0ms, transforms -> none | `[CSV]` ux-guidelines.csv:10 (`@media (prefers-reduced-motion: reduce)`) + `[GEN]` MASTER.md:200 |
| `--hover-transform` | card `translateY(-2px)`, button `translateY(-1px)`; never scale on tables | `[GEN]` MASTER.md:82 / MASTER.md:112; no-layout-shift rule `[GEN]` MASTER.md:183 |

### 4.1 Button - primary

| State | Fill | Text | Ring / other | Measured or provenance |
|-------|------|------|--------------|------------------------|
| default | `#1E40AF` | `#FFFFFF` | radius 8px, padding `12px 24px`, weight 600, min-height 44px (touch surfaces) | fill/text 8.72 `[MEAS]` AAA; geometry `[GEN]` MASTER.md:71-78 (MASTER.md:71-73 emitted `#F59E0B` + `white` = 2.15 `[MEAS]` FAIL -> overridden, CONTRAST-AUDIT finding #1); 44px `[CSV]` ux-guidelines.csv:23 |
| hover | `#1E3A8A` | `#FFFFFF` | `--duration-base` colour transition, no layout shift | white on `#1E3A8A` 10.36 `[MEAS]` AAA; the shade itself `[J]` 设计判断（无本地出处） (CSV carries no hover ramp); hover-transition duty `[CSV]` html-tailwind.csv:5 |
| active | `#172554` | `#FFFFFF` | none | 14.69 `[MEAS]` AAA; hex `[J]` 设计判断（无本地出处） |
| focus-visible | unchanged | unchanged | 2px solid `#93C5FD`, offset 2px, on top of a 2px `#1D4ED8` base ring | `#93C5FD` vs `#1E40AF` = 4.84 `[MEAS]` AA; `#1D4ED8` vs `#F8FAFC` = 6.41 `[MEAS]` AA. Necessity: the generator halo `#1E40AF20` composites to 1.23 vs bg `[MEAS]` and `#1D4ED8` on a filled primary is 1.30 `[MEAS]` - both invisible (finding #2). Ring requirement `[CSV]` ux-guidelines.csv:29 |
| disabled | `#F1F5F9` | `#94A3B8` | border `#E2E8F0`, `cursor: not-allowed`, `aria-disabled="true"` | opacity + cursor rule `[CSV]` ux-guidelines.csv:32 (`opacity-50 cursor-not-allowed`) + `[CSV]` html-tailwind.csv:29; disabled contrast 2.34 `[MEAS]` reported and treated as exempt (WCAG 2.1 inactive-components exemption) `[J]` |
| loading | unchanged | label swapped for 16px spinner + `aria-busy="true"` | control disabled while in flight | double-submit block `[CSV]` ux-guidelines.csv:33 (`disabled={loading} spinner`); spinner 16px `[J]` 设计判断（无本地出处） |
| error | `#B91C1C` | `#FFFFFF` | inline message under the control, not toast-only | 6.47 `[MEAS]` AA on fill; inline-error rule `[CSV]` web-interface.csv:16 |

### 4.2 Button - secondary / ghost

| State | Spec | Provenance |
|-------|------|-----------|
| default | transparent, text `#1E40AF`, 2px solid `#1E40AF`, radius 8px, `12px 24px`, weight 600 | `[GEN]` MASTER.md:86-94 |
| hover | bg `#EFF6FF`, text `#1E3A8A` | tint `[CSV]` colors.csv:52 / :59 / :70; text on tint 9.52 `[MEAS]` AAA; link on tint 8.01 `[MEAS]` `[MEAS]` from `_evidence5_out.txt` |
| focus-visible | 2px `#1D4ED8` ring, offset 2px | 6.41 vs `#F8FAFC` `[MEAS]` and 6.70 vs `#FFFFFF` `[MEAS]` - passes because the control is unfilled |
| disabled | text `#94A3B8`, border `#E2E8F0`, `pointer-events: none` | `[CSV]` ux-guidelines.csv:32 |
| loading | border kept, spinner replaces label, control disabled | `[CSV]` ux-guidelines.csv:33 |
| error | border + text `#B91C1C` | `[CSV]` colors.csv:69 |

### 4.3 Input / select / filter

| State | Spec | Provenance |
|-------|------|-----------|
| default | bg `#FFFFFF`, border 1px `#64748B`, radius 8px, padding `12px 16px`, font-size 16px, min-height 44px on touch | geometry `[GEN]` MASTER.md:119-123 - but that rule ships border `#E2E8F0` which measures 1.23 vs white `[MEAS]`, replaced by border-strong (finding #3); border-strong hex `[CSV]` colors.csv:33; 44px `[CSV]` ux-guidelines.csv:23 |
| hover | border `#1E40AF` | `[J]` 设计判断（无本地出处） for the colour; the requirement for a hover state `[CSV]` html-tailwind.csv:5 |
| focus | border `#1E40AF` + ring 2px `#1D4ED8` offset 1px; never `outline: none` alone | `[CSV]` ux-guidelines.csv:29 (Don't: remove focus outline without replacement); `[GEN]` MASTER.md:129-130 is the banned pattern (halo 1.23 `[MEAS]`) |
| disabled | bg `#F1F5F9`, text `#94A3B8`, `cursor: not-allowed` | `[CSV]` ux-guidelines.csv:32 + html-tailwind.csv:29 |
| loading | 16px trailing spinner, control read-only while the option list fetches | `[J]` 设计判断（无本地出处）; async-feedback duty `[CSV]` ux-guidelines.csv:11 |
| error | border `#B91C1C`, inline message below the field, focus jumps to first invalid field, `aria-invalid`, `aria-describedby` | `[CSV]` web-interface.csv:16 (Do: inline error with focus on first error; Don't: single error at top) |
| empty | placeholder copy + one helper line, never a blank box | `[CSV]` ux-guidelines.csv:80 |

### 4.4 Data table

| Aspect | Spec | Provenance |
|--------|------|-----------|
| row height | 36px | `[CSV]` styles.csv:29 (`--table-row-height: 36px`) |
| cell type | 13px / 12px micro, text `#0F172A` on `#FFFFFF` = 17.85 `[MEAS]` | `[CSV]` styles.csv:29 (`font-size: 12-14px`); hex `[CSV]` colors.csv:7 |
| header | sticky, bg `#F3F4F6`, weight 600, sort affordance | `[CSV]` styles.csv:29 (`overflow: auto for tables, sticky headers`, checklist `☐ Tables sortable`) + styles.csv:37 (`--table-header-bg`) |
| row default | border-bottom 1px `#E2E8F0` (decorative) + zebra `#F1F5F9` on even rows | `[CSV]` styles.csv:34 (`comparison table zebra striping`) + `[J]` for the exact tint |
| row hover | bg `#F1F5F9` only, no transform (1.10 vs white `[MEAS]`, decorative) | `[CSV]` styles.csv:29 Effects (`row highlighting on hover`); `[GEN]` MASTER.md:183 (no layout-shifting hovers) |
| row selected | bg `#DBEAFE` + 3px left bar `#1E40AF`, text `#1E3A8A` (8.49 `[MEAS]` AAA) | `[CSV]` colors.csv:9; left-bar idiom `[CSV]` styles.csv:31 (`status indicators (border-left color)`) |
| focus (keyboard row/cell nav) | 2px inset ring `#1D4ED8` on the cell; arrows move cells, Enter opens the row | `[CSV]` web-interface.csv:4 (keyboard handlers) + `[CSV]` ux-guidelines.csv:29; 6.41 `[MEAS]` |
| loading | 8 skeleton rows at 36px, `--color-surface-sunken`, pulse | `[CSV]` ux-guidelines.csv:11 (`animate-pulse skeleton`) + styles.csv:29 checklist (`☐ Loading states for data`) |
| empty | full-width panel: icon + `No rows match these filters` + primary action `Reset filters` | `[CSV]` ux-guidelines.csv:80 (Do: helpful message and action; Don't: blank empty screens) |
| error | in-body banner + `Retry` button + last successful load time | `[CSV]` ux-guidelines.csv:62 (Loading -> success/error state); timestamp detail `[J]` 设计判断（无本地出处） |
| density toggle | 36px dense (default) / 44px comfortable (touch) | 36px `[CSV]` styles.csv:29; 44px `[CSV]` ux-guidelines.csv:23; the toggle `[J]` |
| bulk actions | always available for a multi-row selection, never row-action-only | `[CSV]` pages/dashboard.md:35 (`Avoid: Single row actions only`) + :50 (`Allow multi-select and bulk edit`) |

### 4.5 KPI card

| Aspect | Spec | Provenance |
|--------|------|-----------|
| geometry | radius 12px, padding 12px (dense) / 24px (comfortable), min-width 280px, `--shadow-md` | `[GEN]` MASTER.md:103-105; `[CSV]` styles.csv:29 (`--card-padding: 12px`); `[CSV]` styles.csv:31 (`--card-min-width: 280px`) |
| value | `--font-heading` 48px 700 `#1E3A8A`, tabular-nums, count-up 200-300ms | `[CSV]` styles.csv:31 (`--kpi-font-size: 48px`, `KPI value animations (count-up)`); hex `[CSV]` colors.csv:9; timing `[CSV]` motion.csv:3 |
| label | 12px `#475569` (7.24 `[MEAS]` AAA on page bg) | `[CSV]` colors.csv:27 |
| delta up / down | text `#15803D` / `#B91C1C` + arrow glyph, colour never alone | `[CSV]` styles.csv:34 (`--positive-color: #22C55E`, `--negative-color: #EF4444`) measured 2.18 / 3.60 `[MEAS]` on light -> text uses the darker pair (finding #5) |
| status bar | 3px left border: `#22C55E` / `#F59E0B` / `#EF4444`, always paired with a text status label | `[CSV]` styles.csv:31 (`--status-green: #22C55E, --status-yellow: #F59E0B, --status-red: #EF4444`, `status indicators (border-left color)`) - decorative bar, exempt from text contrast |
| hover | `--shadow-lg` + `translateY(-2px)` | `[GEN]` MASTER.md:110-112; card-hover duty `[CSV]` html-tailwind.csv:39 |
| focus | 2px ring `#1D4ED8` when the card is a link | 6.41 `[MEAS]` |
| loading | 3 stacked skeleton bars in the value slot, dashed sparkline placeholder | `[CSV]` ux-guidelines.csv:11 |
| empty | value shows `--`, sub-line `No data in selected range`, action opens the range picker | `[J]` 设计判断（无本地出处）; duty `[CSV]` ux-guidelines.csv:80 |
| error | value shows `Unavailable` in `#B91C1C` (6.18 `[MEAS]` AA) + retry icon button | `[CSV]` colors.csv:69 |
| sparkline height | 32px | `[CSV]` styles.csv:31 |

### 4.6 Chart card

| Aspect | Spec | Provenance |
|--------|------|-----------|
| default | axis 12px `#64748B`, gridlines `#E2E8F0`, series from `--chart-series-*` | `[CSV]` charts.csv:25 (`#94A3B8` family) + `[J]` for the gridline choice |
| hover | tooltip `rgba(0,0,0,0.9)` bg + series highlight; chart zoom on click | `[CSV]` styles.csv:29 Effects; tooltip bg `[CSV]` styles.csv:30 |
| focus | chart container is tabbable, 2px `#1D4ED8` ring, data table alternative | `[CSV]` charts.csv:5 (Do: provide data table alternative) + `[CSV]` web-interface.csv:4 |
| loading | skeleton in the plot area, axes stay fixed so nothing jumps | `[CSV]` ux-guidelines.csv:11 + `[CSV]` ux-guidelines.csv:77 (reserve space with fallback) |
| empty | centred `No data` + the active filter chips so the cause is visible | `[CSV]` ux-guidelines.csv:80 |
| error | `Chart failed to load` + retry, never a blank plot | `[J]` 设计判断（无本地出处）; duty `[CSV]` ux-guidelines.csv:11 |
| live update | pulse dot `#22C55E` on dark, refresh every 5s, critical alerts in `#DC2626` | `[CSV]` styles.csv:32 (`--pulse-animation: pulse 2s infinite`, `--live-indicator: #22C55E`, `--critical-color: #DC2626`, `--update-interval: 5s`) |

### 4.7 Modal / drawer / toast

| Aspect | Spec | Provenance |
|--------|------|-----------|
| overlay | `rgba(0, 0, 0, 0.5)` + `backdrop-filter: blur(4px)` | `[GEN]` MASTER.md:137-139 |
| modal | radius 16px, padding 32px, `--shadow-xl`, max-width 500px, width 90% | `[GEN]` MASTER.md:142-148 |
| focus | moved into the dialog on open, trapped while open, returned to the trigger on close, Esc closes | `[J]` 设计判断（无本地出处）; keyboard duty `[CSV]` web-interface.csv:4 |
| loading | primary button enters its loading state, body unaffected | `[CSV]` ux-guidelines.csv:33 |
| error | inline validation area, no toast-only | `[CSV]` web-interface.csv:16 |
| empty n/a | a modal has no empty state by definition | `[J]` |
| toast | `z-index: 1000`, auto-dismiss 5s, slide disabled under reduced motion | `[CSV]` styles.csv:32 |

### 4.8 Sidebar / header / filter panel

| Aspect | Spec | Provenance |
|--------|------|-----------|
| sidebar | docked 240px >=1024px, collapsed rail 64px, sheet <768px | 240px `[CSV]` styles.csv:29; rail and mapping `[J]` 设计判断（无本地出处） |
| header | 56px, sticky, no content hidden underneath it | `[CSV]` styles.csv:29 (`--header-height: 56px`); no-hidden-behind-navbar duty `[GEN]` MASTER.md:202 |
| active nav item | text `#1E40AF` + 2px bottom border, never grey alone | `[CSV]` ux-guidelines.csv:4 (Do: `text-primary border-b-2`) |
| breadcrumb | separator `/`, sticky, 24px indent per level, back control 40px, expand 300ms | `[CSV]` styles.csv:33 |
| filter panel | chips 12px, badge padding `4px 8px`, comparison gap 2rem, arrow 16px | `[CSV]` styles.csv:34 + styles.csv:29 (`☐ Filters functional`) |
| empty panel | panel-shaped skeleton, never a blank rail | `[CSV]` ux-guidelines.csv:80 |

---

## 5. Breakpoints

Two local sources disagree, so the union ships and every value is cited. No breakpoint here
is invented:

- `ux-guidelines.csv:66` col Do = `Test at 320 375 414 768 1024 1440` `[CSV]`
- `stacks/html-tailwind.csv:32` col Do = `320 375 768 1024 1280 1536` `[CSV]`
- `MASTER.md:201` (generator checklist) = `375px, 768px, 1024px, 1440px` `[GEN]`
- mobile-first method (default mobile, then `md: lg: xl:`) = `[CSV]` ux-guidelines.csv:65 + html-tailwind.csv:31

Shipped ladder = union (8 values). Required test set = intersection (320/375/768/1024),
because those four appear in both CSVs `[J]` 设计判断（无本地出处）（选择理由：交集是两份本地数据
的最低共识；1440 与 1536 都保留，因为内部分析后台的主战场是 27" 与 4K 大屏）.

| Token | min-width | Cols | Layout contract | Provenance |
|-------|-----------|------|-----------------|-----------|
| `--bp-xs` | 320px | 1 | floor; no horizontal page scroll | `[CSV]` ux-guidelines.csv:66 + html-tailwind.csv:32; no-hscroll `[GEN]` MASTER.md:203 |
| `--bp-sm` | 375px | 1 | KPI cards stack, table -> record cards, touch >=44px | `[CSV]` both + `[GEN]` MASTER.md:201 |
| `--bp-sm-plus` | 414px | 1 | 1 col, density stays 36px rows | `[CSV]` ux-guidelines.csv:66 only |
| `--bp-md` | 768px | 2 | filter sheet opens, sidebar still hidden, 2-up KPI grid | `[CSV]` both |
| `--bp-lg` | 1024px | 3 | sidebar docks at 240px, 12-col grid gap 8px | `[CSV]` both + `[CSV]` styles.csv:29 |
| `--bp-xl` | 1280px | 4 | right rail appears, content max 1200px | `[CSV]` html-tailwind.csv:32; 1200px = the generator's fallback Max Width (`design_system.py:1003` writes `1200px (standard)`) `[GEN]` |
| `--bp-2xl` | 1440px | 4 | primary design target for an internal analyst | `[CSV]` ux-guidelines.csv:66 + `[GEN]` MASTER.md:201 |
| `--bp-3xl` | 1536px | 4 + rail | full width up to `--content-max-width` | `[CSV]` html-tailwind.csv:32 |

Layout tokens that hang off the ladder:

| Token | Value | Provenance |
|-------|-------|-----------|
| `--content-max-width` | 1400px or full-width at >=1536px | `[CSV]` pages/dashboard.md:16 (`Max Width: 1400px or full-width`) |
| `--content-max-width` | 1200px at 1280-1535px | `[GEN]` design_system.py:1003 (fallback branch writes `1200px (standard)`) |
| `--grid-columns` | 12 at every stop | `[CSV]` pages/dashboard.md:17 + styles.csv:51 |
| `--grid-gap` | 8px at every stop | `[CSV]` styles.csv:29 |
| `--table-behavior` | below 768px the table renders as stacked record cards; wide tables never break the layout | `[CSV]` pages/dashboard.md:34 (`Avoid: Wide tables breaking layout`) + pages/dashboard.md:49 (`Use horizontal scroll or card layout`) |
| `--touch-targets` | >=44px with >=8px gaps below 1024px | `[CSV]` ux-guidelines.csv:23 / :24 |
| `--sidebar-behavior` | docked >=1024 / drawer 768-1023 / sheet <768 | `[J]` 设计判断（无本地出处）（组合方式自定，宽度与断点集均来自上面两处） |
| `--print` | executive views get a print-friendly single-page layout | `[CSV]` styles.csv:31 checklist (`☐ Print-friendly layout`) |

---

## 6. Coverage self-check (the five required classes)

| Required class | Where | Concrete numbers present |
|----------------|-------|--------------------------|
| color tokens | sections 1.1-1.4 | 46 hexes with role, source line, measured ratio |
| spacing scale | section 2 | 8 steps (4/8/12/16/24/32/48/64px) + 18 component dimensions |
| typography (family + scale) | section 3 | 2 primary families + 3 alternates, 8-step size scale, 4 weights, leading tokens |
| component states | section 4 | default/hover/focus/disabled/loading/error on buttons + inputs, empty/loading/error on table, card, chart, modal |
| breakpoints | section 5 | 8 named stops with column and layout contracts |
