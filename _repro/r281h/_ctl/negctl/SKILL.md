---
name: ui-ux-pro-max
description: UI/UX design intelligence and implementation guidance for building polished interfaces. Use when the user asks for UI design, UX flows, information architecture, visual style direction, design systems/tokens, component specs, copy/microcopy, accessibility, or to generate/critique/refine frontend UI (HTML/CSS/JS, React, Next.js, Vue, Svelte, Tailwind). Includes workflows for (1) generating new UI layouts and styling, (2) improving existing UI/UX, (3) producing design-system tokens and component guidelines, and (4) turning UX recommendations into concrete code changes.
last_updated: 2026-10-26
version: 1.2.0
---

Follow these steps to deliver high-quality UI/UX output with minimal back-and-forth.

## When NOT to use this skill (路由消歧)
- **Use frontend-skill** when you need to BUILD actual production frontend CODE (not just design guidance)
- **Not for**: 写前端代码、做落地页、实现UI组件 — 那些是 frontend-skill 的职责
- This skill provides design THINKING and GUIDANCE (design systems, UX flows, critique)
- If the user says "帮我做/写/实现一个页面" → use frontend-skill

## 1) Triage
Ask only what you must to avoid wrong work:
- Target platform: web / iOS / Android / desktop
- Stack (if code changes): React/Next/Vue/Svelte, CSS/Tailwind, component library
- Goal and constraints: conversion, speed, brand vibe, accessibility level (WCAG AA?)
- What you have: screenshot, Figma, repo, URL, user journey

If the user says "全部都要" (design + UX + code + design system), treat it as four deliverables and ship in that order.

## 2) Produce Deliverables (pick what fits)
Always be concrete: name components, states, spacing, typography, and interactions.

- **UI concept + layout**: Provide a clear visual direction, grid, typography, color system, key screens/sections.
- **UX flow**: Map the user journey, critical paths, error/empty/loading states, edge cases.
- **Design system**: Tokens (color/typography/spacing/radius/shadow), component rules, accessibility notes.
- **Implementation plan**: Exact file-level edits, component breakdown, and acceptance criteria.

## 3) Use Bundled Assets
This skill bundles data you can cite for inspiration/standards.

- **Design intelligence data**: Read from `skills/ui-ux-pro-max/assets/data/` when you need palettes, patterns, or UI/UX heuristics.
- **Upstream reference**: If you need more phrasing/examples, consult `skills/ui-ux-pro-max/references/upstream-skill-content.md`.

## 4) Optional Script (Design System Generator)
If you need to quickly generate tokens and page-specific overrides, use the bundled script:

```bash
python3 skills/ui-ux-pro-max/scripts/design_system.py --help
```

Prefer running it when the user wants a structured token output (ASCII-friendly).

## Output Standards
- Default to ASCII-only tokens/variables unless the project already uses Unicode.
- Include: spacing scale, type scale, 2-3 font pair options, color tokens, component states.
- Always cover: empty/loading/error, keyboard navigation, focus states, contrast.

## Version history

- **1.2.0**（2026-10-26）— P1-3 续补：上游 `CSV_CONFIG` 有 `gsap`、`google-fonts` 两域而本件缺，已补 `data/motion.csv`（14679B）与 `data/google-fonts.csv`（747241B）各双副本（`data/` 与 `assets/data/`，SHA256 一致），并在 `scripts/core.py` 的 `CSV_CONFIG` 登记两域。接入机制实测（`search.py` 的 `--domain choices=list(CSV_CONFIG.keys())`）：未注册域 `--domain prompt` → rc=2 `invalid choice`（证明选项集确实由 CSV_CONFIG 决定 ⇒ 补域即自动进选项）；补后 `--domain gsap` rc=0 且结果 `Source: motion.csv`、`--domain google-fonts` rc=0 且 `Source: google-fonts.csv`，各 Found 3。注：这是**门机制 + 补后**的实测，**未取「补前的 gsap」基线**（该域补前不存在，无从跑同查询），故不作「补前 rc=2 ⇒ 补后生效」的前后对比断言。**未动 `web` 域**：本地 `web-interface.csv`（31 行）与上游 `app-interface.csv`（33 行）是双向分叉（本地独有 Accessibility/Keyboard Handlers、Focus/Visible Focus States 等，上游独有 Touch Target Size、Back Behavior 等），以本地为准不覆盖。上游 `scripts/tests/fixtures/catalogs/*`（480/495B）是测试夹具不是数据资产，不纳入。
- **1.1.0**（2026-10-25）— P1-3 补上游数据资产：`data/stacks/` 与 `assets/data/stacks/` 各新增 9 个技术栈 CSV（angular / avalonia / javafx / laravel / threejs / uno / uwp / winui / wpf，上游 MIT 件一手 `gh api` 取回），并在 `scripts/core.py` 的 `STACK_CONFIG` 登记同名条目。关键：**只补 CSV 不生效** —— 一手实测 `search.py --stack wpf` 补前 rc=2（`invalid choice`，`AVAILABLE_STACKS`=13），补后 rc=0 且检索出真实条目（`AVAILABLE_STACKS`=22）；上游 CSV 多出的 `Applies To / Status / Verified At` 三列由 `_search_csv` 的 `output_cols` 白名单忽略，输出形状不变。本件既有「`data/` 与 `assets/data/` 两份逐字节重复」结构（`core.py` 读前者、SKILL.md 文本指后者），本轮按现状同步两处，不擅自合并（合并属结构变更，需另行裁决）。
- **1.0.0** — 初版（上游 ui-ux-pro-max 骨架 + 13 个技术栈）。
