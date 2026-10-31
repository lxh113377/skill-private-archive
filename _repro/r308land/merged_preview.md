---
name: frontend-skill
description: Use when the task asks for a visually strong landing page, website, app, prototype, demo, or game UI. This skill enforces restrained composition, image-led hierarchy, cohesive content structure, and tasteful motion while avoiding generic cards, weak branding, and UI clutter.
last_updated: 2026-10-31
version: 1.1.0
---

# Frontend Skill

Use this skill when the quality of the work depends on art direction, hierarchy, restraint, imagery, and motion rather than component count.

Goal: ship interfaces that feel deliberate, premium, and current. Default toward award-level composition: one big idea, strong imagery, sparse copy, rigorous spacing, and a small number of memorable motions.

## Working Model

Before building, write three things:

- visual thesis: one sentence describing mood, material, and energy
- content plan: hero, support, detail, final CTA
- interaction thesis: 2-3 motion ideas that change the feel of the page

Each section gets one job, one dominant visual idea, and one primary takeaway or action.
<!-- r307b 逐字钉定（加法式并入 · 本地行零删除）| 增量 I3 · 发牌器与方向库 | 上游 L24-32 | Leonxlnx/taste-skill · branch main · commit 12af471f627f866411b4bd785b19646d3672784c · blob_sha d8444f13b76be100b3b088dfdae738e85288d6b6 · content_sha256 3435ed963b15a1b6447746ec8844ab2cd38d8d2e8ead3451937f42df01e408c4 · license MIT | 证据 r303b swap_pack increments[frontend-skill] · 准入 r305b merge_plan skills[slug=frontend-skill].files[src=SKILL.md,action=land] -->
1. **A script deals the directions, you choose among them.** Asked to invent a look, a model picks
   the category default every time. `scripts/draw.mjs` deals three of twenty researched directions;
   you choose the one that carries the subject's idea, and the script then deals its type system,
   palette, hero and section compositions from a library distilled from 247 real sites.
2. **The idea comes from the subject.** In the study, what separated the best sites from the forgettable
   ones was a concept taken from the thing itself, not the styling.
3. **A house style with no ornaments,** measured in a real browser by `scripts/inspect.mjs`, so the
   rules are checked rather than hoped for.
4. **You look at what you made.** Screenshots at three widths, a juror's rubric, fix, look again.


## Beautiful Defaults

- Start with composition, not components.
- Prefer a full-bleed hero or full-canvas visual anchor.
- Make the brand or product name the loudest text.
- Keep copy short enough to scan in seconds.
- Use whitespace, alignment, scale, cropping, and contrast before adding chrome.
- Limit the system: two typefaces max, one accent color by default.
- Default to cardless layouts. Use sections, columns, dividers, lists, and media blocks instead.
- Treat the first viewport as a poster, not a document.

## Landing Pages

Default sequence:

1. Hero: brand or product, promise, CTA, and one dominant visual
2. Support: one concrete feature, offer, or proof point
3. Detail: atmosphere, workflow, product depth, or story
4. Final CTA: convert, start, visit, or contact

Hero rules:

- One composition only.
- Full-bleed image or dominant visual plane.
- Canonical full-bleed rule: on branded landing pages, the hero itself must run edge-to-edge with no inherited page gutters, framed container, or shared max-width; constrain only the inner text/action column.
- Brand first, headline second, body third, CTA fourth.
- No hero cards, stat strips, logo clouds, pill soup, or floating dashboards by default.
- Keep headlines to roughly 2-3 lines on desktop and readable in one glance on mobile.
- Keep the text column narrow and anchored to a calm area of the image.
- All text over imagery must maintain strong contrast and clear tap targets.

If the first viewport still works after removing the image, the image is too weak. If the brand disappears after hiding the nav, the hierarchy is too weak.

Viewport budget:

- If the first screen includes a sticky/fixed header, that header counts against the hero. The combined header + hero content must fit within the initial viewport at common desktop and mobile sizes.
- When using `100vh`/`100svh` heroes, subtract persistent UI chrome (`calc(100svh - header-height)`) or overlay the header instead of stacking it in normal flow.

## Apps

Default to Linear-style restraint:

- calm surface hierarchy
- strong typography and spacing
- few colors
- dense but readable information
- minimal chrome
- cards only when the card is the interaction

For app UI, organize around:

- primary workspace
- navigation
- secondary context or inspector
- one clear accent for action or state

Avoid:

- dashboard-card mosaics
- thick borders on every region
- decorative gradients behind routine product UI
- multiple competing accent colors
- ornamental icons that do not improve scanning

If a panel can become plain layout without losing meaning, remove the card treatment.
<!-- r307b 逐字钉定（加法式并入 · 本地行零删除）| 增量 I4 · app 屏专线 | 上游 L48-55 + L64-66 | Leonxlnx/taste-skill · branch main · commit 12af471f627f866411b4bd785b19646d3672784c · blob_sha d8444f13b76be100b3b088dfdae738e85288d6b6 · content_sha256 3435ed963b15a1b6447746ec8844ab2cd38d8d2e8ead3451937f42df01e408c4 · license MIT | 证据 r303b swap_pack increments[frontend-skill] · 准入 r305b merge_plan skills[slug=frontend-skill].files[src=SKILL.md,action=land] -->
- **A page** is read and scrolled: a landing page, a marketing or product site, a portfolio, an
  event, a restaurant, a one-pager. It follows **the run** below.
- **An app screen** is worked in: a dashboard, an admin or analytics view, settings, billing, an inbox
  or queue to work through, a wallet, a list with filters, an editor or builder. It follows
  **`references/app-screens.md`**: its own run, its own draw (`draw.mjs --app`), its own house rules
  (quiet borders, small labels and repeated panels are normal there; gradients, glows, icons in tinted
  squares, rainbow charts and invented vanity numbers are not) and `inspect.mjs --app`. Read that file
  whole before you start; the page run below does not apply.

App fragments reuse the landed sidecars named above (a neutral app shell for panels, tables and controls, plus small charts drawn to the app rules):


and build every fragment the page shows (the hero's live screen, a feature's crop, a chart) as a real
piece of that app: `assets/app.css` for its panels, tables and controls, `assets/charts.js` for its


## Imagery

Imagery must do narrative work.

- Use at least one strong, real-looking image for brands, venues, editorial pages, and lifestyle products.
- Prefer in-situ photography over abstract gradients or fake 3D objects.
- Choose or crop images with a stable tonal area for text.
- Do not use images with embedded signage, logos, or typographic clutter fighting the UI.
- Do not generate images with built-in UI frames, splits, cards, or panels.
- If multiple moments are needed, use multiple images, not one collage.

The first viewport needs a real visual anchor. Decorative texture is not enough.

## Copy

- Write in product language, not design commentary.
- Let the headline carry the meaning.
- Supporting copy should usually be one short sentence.
- Cut repetition between sections.
- Do not include prompt language or design commentary into the UI.
- Give every section one responsibility: explain, prove, deepen, or convert.

If deleting 30 percent of the copy improves the page, keep deleting.

## Utility Copy For Product UI

When the work is a dashboard, app surface, admin tool, or operational workspace, default to utility copy over marketing copy.

- Prioritize orientation, status, and action over promise, mood, or brand voice.
- Start with the working surface itself: KPIs, charts, filters, tables, status, or task context. Do not introduce a hero section unless the user explicitly asks for one.
- Section headings should say what the area is or what the user can do there.
- Good: "Selected KPIs", "Plan status", "Search metrics", "Top segments", "Last sync".
- Avoid aspirational hero lines, metaphors, campaign-style language, and executive-summary banners on product surfaces unless specifically requested.
- Supporting text should explain scope, behavior, freshness, or decision value in one sentence.
- If a sentence could appear in a homepage hero or ad, rewrite it until it sounds like product UI.
- If a section does not help someone operate, monitor, or decide, remove it.
- Litmus check: if an operator scans only headings, labels, and numbers, can they understand the page immediately?

## Motion

Use motion to create presence and hierarchy, not noise.

Ship at least 2-3 intentional motions for visually led work:

- one entrance sequence in the hero
- one scroll-linked, sticky, or depth effect
- one hover, reveal, or layout transition that sharpens affordance

Prefer Framer Motion when available for:

- section reveals
- shared layout transitions
- scroll-linked opacity, translate, or scale shifts
- sticky storytelling
- carousels that advance narrative, not just fill space
- menus, drawers, and modal presence effects

Motion rules:

- noticeable in a quick recording
- smooth on mobile
- fast and restrained
- consistent across the page
- removed if ornamental only

<!-- r307b 逐字钉定（加法式并入 · 本地行零删除）| 增量 I1 · 可执行审美门禁 | 上游 L307-331 | Leonxlnx/taste-skill · branch main · commit 12af471f627f866411b4bd785b19646d3672784c · blob_sha d8444f13b76be100b3b088dfdae738e85288d6b6 · content_sha256 3435ed963b15a1b6447746ec8844ab2cd38d8d2e8ead3451937f42df01e408c4 · license MIT | 证据 r303b swap_pack increments[frontend-skill] · 准入 r305b merge_plan skills[slug=frontend-skill].files[src=SKILL.md,action=land] -->
### 7. Gate

```bash
node <skill>/scripts/lint.mjs <source files or folder>
node <skill>/scripts/inspect.mjs <url or path/to/index.html>
node <skill>/scripts/scenes.mjs <url or path/to/index.html>     # when the page has scroll scenes
```

`scenes.mjs` photographs every scroll scene at 0, 10 … 100% of its hold, on desktop and on a phone,
and the reduced-motion page; with scenes on the sheet, `inspect.mjs` also films the whole scroll
(`desktop-film-NN.jpg`). A scene that never started or rests on desktop is a `FAIL`.

`lint.mjs` scans source for banned patterns and stock phrases. `inspect.mjs` opens the page in a real
browser at 1440, 768 and 390 pixels, measures it (headline line counts, type sizes, fonts actually
loaded, colours, rules, shadows, gradients, contrast, overflow, and the frame: equal margins, sections
huddled on one side, blank stretches, the title, untitled sections, text against the screen edge) and
saves screenshots to `.taste-skill/inspect/`. Fix every `FAIL`. Treat each `WARN` as wrong unless you can defend it to a
designer in one sentence. Re-run until there are no `FAIL`s. Do not argue with the meter and do not
hide things from it. The inspector serves local files over a throwaway local server; if the page must
also open straight from the file system, open `index.html` that way once before you finish.

Inspect what the visitor receives. With a build step, run the last gate on the production build
(`vite build && vite preview`, `next build && next start`, or the built `index.html`), not only on the
dev server: minifiers and bundlers change what ships (one dropped a `backdrop-filter` that the dev
server showed). The inspector warns when it is looking at a dev server.
## Hard Rules

- No cards by default.
- No hero cards by default.
- No boxed or center-column hero when the brief calls for full bleed.
- No more than one dominant idea per section.
- No section should need many tiny UI devices to explain itself.
- No headline should overpower the brand on branded pages.
- No filler copy.
- No split-screen hero unless text sits on a calm, unified side.
- No more than two typefaces without a clear reason.
- No more than one accent color unless the product already has a strong system.

## Reject These Failures

- Generic SaaS card grid as the first impression
- Beautiful image with weak brand presence
- Strong headline with no clear action
- Busy imagery behind text
- Sections that repeat the same mood statement
- Carousel with no narrative purpose
- App UI made of stacked cards instead of layout

<!-- r307b 逐字钉定（加法式并入 · 本地行零删除）| 增量 I2 · 交付判据 0 FAIL | 上游 L363-373 | Leonxlnx/taste-skill · branch main · commit 12af471f627f866411b4bd785b19646d3672784c · blob_sha d8444f13b76be100b3b088dfdae738e85288d6b6 · content_sha256 3435ed963b15a1b6447746ec8844ab2cd38d8d2e8ead3451937f42df01e408c4 · license MIT | 证据 r303b swap_pack increments[frontend-skill] · 准入 r305b merge_plan skills[slug=frontend-skill].files[src=SKILL.md,action=land] -->
### 10. Report

Do not report until all of these are true; each one was skipped in a test run that came out badly:

- `inspect.mjs` shows **0 FAIL** at 1440, 768 and 390, on the final version of the page.
- You opened every screenshot it listed after the last change, not only the first screen.
- With scroll scenes: `scenes.mjs` ran on the final page with no problems, and you read every sheet
  (desktop, phone, reduced motion).
- A stranger reading the first screen for five seconds can say what this is and what to do.
- Every section has a heading; the margins match on both sides; no stretch of the page is empty.
- The critique of your last round is written down in the shape of `references/critique.md` §4.
## Litmus Checks

- Is the brand or product unmistakable in the first screen?
- Is there one strong visual anchor?
- Can the page be understood by scanning headlines only?
- Does each section have one job?
- Are cards actually necessary?
- Does motion improve hierarchy or atmosphere?
- Would the design still feel premium if all decorative shadows were removed?
## Version history

- **1.1.0** (2026-10-31) 换装增量并入（Leonxlnx/taste-skill @ commit 12af471f、MIT；F2-F6 五条逐字钉定 + 37 件 payload 落盘（含 r307 解锁的 charts.js/base.js/assets.mjs/inspect.mjs））；本地独有 3 项守住（Canonical full-bleed、Viewport budget、agents 平台配置）。r308 Lead 落地并追加本节。<!-- r307b 逐字钉定（加法式并入 · 本地行零删除）| 卡点解锁 B3 与 B4 · 补取件指针对账 | 上游 L539-541 | Leonxlnx/taste-skill · branch main · commit 12af471f627f866411b4bd785b19646d3672784c · blob_sha d8444f13b76be100b3b088dfdae738e85288d6b6 · content_sha256 3435ed963b15a1b6447746ec8844ab2cd38d8d2e8ead3451937f42df01e408c4 · license MIT | 证据 r303b swap_pack increments[frontend-skill] · 准入 r305b merge_plan skills[slug=frontend-skill].files[src=SKILL.md,action=land] -->
## Bundled Foundation and Chart Sidecars

The two files that r305b blocked as candidate gaps were re-fetched and pinned in r307b; the pointers below are upstream verbatim.

| File | Read it when |
| --- | --- |
| `assets/base.css` · `assets/base.js` | An optional neutral foundation to build on. |
| `assets/scenes/` | The scroll scenes: the shared stage (`stage.js`, `stage.css`) and, for each scene in the library, its `.js`, `.css` and a working demo page in `demo/`. |
| `assets/app.css` · `assets/charts.js` | For app screens: a neutral shell, panels, tables and controls, and small SVG charts drawn to the app rules. |

