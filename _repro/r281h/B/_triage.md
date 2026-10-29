# Triage (SKILL.md step 1) - written answer for arm B

Task: UI/UX design system for an internal data-analysis admin dashboard.
Authority: `_temp/r281h/B/SKILL.md` (ui-ux-pro-max v1.6.0 local copy). Per instruction the deliverable is a
design system persisted as files, so step 1 questions are self-adjudicated here (no bounce-back).

## 1. Target platform
**Web (desktop-first responsive admin).** Ruling reason: an internal data-analysis dashboard is consumed on
analyst/desktop browsers; SKILL.md line 60-61 forbids fixed-px containers and demands responsive breakpoints,
line 97 of the generated checklist gives the web ladder 375/768/1024/1440. iOS/Android ruled out: no mobile
app request; native touch rules are still adopted as a floor (44x44 on touch, ux-guidelines.csv:23).

## 2. Stack
**Not supplied by the requester.** Ruling: tokens are emitted as neutral CSS custom properties (`--color-*`,
`--space-*`) because that shape is stack-agnostic, plus a documented Tailwind mapping because the local data
set is Tailwind-heavy (data/stacks/html-tailwind.csv:32 row 31 lists the test-breakpoint ladder; :35 row 34
gives `min-h-[44px] min-w-[44px]`). SKILL.md line 12 explicitly scopes this skill OUT of writing production
frontend code, so no framework is installed or assumed.

## 3. Goal and constraints
- Goal: **analyst speed and data legibility**, not conversion. Ruling reason: internal tool, no funnel.
  Therefore the marketing artifacts in the generator output (Hero / Pricing / CTA sections from landing.csv
  row 10 "Comparison Table + CTA", `_gen_stdout.txt` RUN 3 PATTERN block) are **declined as patterns** and
  only its token rows (Colors / Typography) are used. Recorded in MASTER.md Usage Notes.
- Style constraint: **Data-Dense Dashboard** (assets/data/styles.csv:29 row 28, BI/Analytics: "minimal
  padding, grid layout, space-efficient, maximum data visibility"), chosen over Executive Dashboard
  (styles.csv:31, built for C-suite at-a-glance) because the brief says *data analysis*.
- Constraint: must pass WCAG AA and be implementable with plain CSS variables; ASCII-only tokens
  (SKILL.md line 95).

## 4. WCAG level
**AA (EN 301 549 / WCAG 2.2 AA) as the shipping target, AAA adopted selectively.** Ruling reasons:
- assets/data/styles.csv:29 (Data-Dense Dashboard) declares "Accessibility: WCAG AA".
- The generator itself returns "Accessibility: WCAG AA" (_gen_stdout.txt RUN 3, STYLE block).
- The product type is an internal enterprise tool: SKILL.md priority row 1 requires contrast 4.5:1
  (references/quick-reference.md:104 `readable-font-size`, :122 line-height 1.5-1.75), and AAA-only numbers
  (styles.csv:9 row 8: 7:1, 44x44 everywhere, focus ring 3-4px) are adopted where they do not fight density:
  focus ring 2px minimum per web-interface.csv:8 row 7, upgraded to 3px for the table shell.

## 5. What we have (existing assets)
- No screenshot, no Figma, no repo, no URL supplied by the requester - stated as absent, not assumed.
- Local bundled data is the only material: D:/global_skills/ui-ux-pro-max/data/ (read-only) - colors.csv,
  typography.csv, styles.csv, charts.csv, ux-guidelines.csv, web-interface.csv, app-interface.csv,
  stacks/html-tailwind.csv, motion.csv - and references/quick-reference.md + pro-rules.md.
- Arm-local process authority: SKILL.md; arm-local generator output: _gen_stdout.txt and
  design-system/data-analytics-dashboard/MASTER.md + pages/.

## 6. Deliverable split (SKILL.md line 23 rule)
SKILL.md line 23: if the user wants design + UX + code + design system, treat as four deliverables. Here the
request is the **design-system** deliverable only (plus component-state rules inside it); implementation code
is out of scope per SKILL.md line 12. Order shipped: tokens -> component states -> breakpoints -> page overrides.
