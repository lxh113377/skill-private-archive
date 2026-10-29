# -*- coding: ascii -*-
"""Arm-A evidence harness round 3: fixes for defects round 2 exposed.
Round 2 findings driving this run: focus ring #1D4ED8 on primary fill #1E40AF = 1.30
(invisible ring on filled buttons); chart amber/green/cyan on white = 2.15/2.28/2.43
(below the 3:1 graphical-object bar for essential data marks). Round 3 measures the
replacement values we actually ship, on both light and dark surfaces. Same WCAG 2.x
formula as rounds 1-2. Disabled-state contrast is reported but NOT treated as a
failure: WCAG 2.1 SC 1.4.3 / 1.4.11 exempt inactive components.
"""
def chan(c8):
    return c8 / 12.92 if c8 <= 0.03928 else ((c8 + 0.055) / 1.055) ** 2.4

def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

PAIRS = [
    ("[fix] focus on-dark ring #93C5FD vs primary fill #1E40AF", "#93C5FD", "#1E40AF"),
    ("[fix] focus on-dark ring #BFDBFE vs primary fill #1E40AF", "#BFDBFE", "#1E40AF"),
    ("[fix] focus ring #1D4ED8 vs bg #F8FAFC", "#1D4ED8", "#F8FAFC"),
    ("[fix] focus halo #93C5FD vs bg #F8FAFC (2nd layer)", "#93C5FD", "#F8FAFC"),
    ("chart strong amber #B45309 vs white", "#B45309", "#FFFFFF"),
    ("chart strong green #15803D vs white", "#15803D", "#FFFFFF"),
    ("chart strong cyan #0E7490 vs white", "#0E7490", "#FFFFFF"),
    ("chart strong red #B91C1C vs white", "#B91C1C", "#FFFFFF"),
    ("chart strong violet #6D28D9 vs white", "#6D28D9", "#FFFFFF"),
    ("chart strong pink #BE185D vs white", "#BE185D", "#FFFFFF"),
    ("chart strong blue #1E40AF vs white", "#1E40AF", "#FFFFFF"),
    ("chart strong teal #0F766E vs white", "#0F766E", "#FFFFFF"),
    ("chart strong slate #334155 vs white", "#334155", "#FFFFFF"),
    ("chart light amber #F59E0B vs dark surface #1E293B", "#F59E0B", "#1E293B"),
    ("chart light green #22C55E vs dark surface #1E293B", "#22C55E", "#1E293B"),
    ("chart light cyan #22D3EE vs dark surface #1E293B", "#22D3EE", "#1E293B"),
    ("chart light blue #60A5FA vs dark surface #1E293B", "#60A5FA", "#1E293B"),
    ("chart light violet #A78BFA vs dark surface #1E293B", "#A78BFA", "#1E293B"),
    ("chart light red #F87171 vs dark surface #1E293B", "#F87171", "#1E293B"),
    ("row-hover tint #EFF6FF vs surface #FFFFFF (UI, non-normative)", "#EFF6FF", "#FFFFFF"),
    ("selected tint #DBEAFE text #1E3A8A", "#1E3A8A", "#DBEAFE"),
    ("skeleton #E2E8F0 vs surface #FFFFFF (decorative)", "#E2E8F0", "#FFFFFF"),
    ("disabled label #94A3B8 vs #F1F5F9 (exempt, reported)", "#94A3B8", "#F1F5F9"),
    ("dark: body #E2E8F0 vs bg #0F172A", "#E2E8F0", "#0F172A"),
    ("dark: focus #93C5FD vs bg #0F172A", "#93C5FD", "#0F172A"),
]
print("=== WCAG CONTRAST ROUND 3 (computed by _evidence3.py) ===")
for name, fg, bg in PAIRS:
    r = ratio(fg, bg)
    v = "AAA" if r >= 7 else ("AA" if r >= 4.5 else ("AA-UI(>=3:1)" if r >= 3 else "FAIL"))
    print("%-58s ratio=%6.2f  %s" % (name, r, v))

print("")
print("=== 8-px spacing grid: CSV anchors vs our scale ===")
# base unit 8px from styles.csv:50 (--base-unit: 8px) and styles.csv:29 (--grid-gap: 8px,
# --card-padding: 12px). Scale multipliers themselves are our judgment, recorded here so
# the arithmetic is visible.
for n, m in [(4, 0.5), (8, 1), (12, 1.5), (16, 2), (24, 3), (32, 4), (48, 6), (64, 8)]:
    print("space %2dpx = %3.1f x 8px base" % (n, m))
print("MASTER.md generator block (lines 45-51) already lists 4/8/16/24/32/48/64 -> kept")
print("12px inserted from styles.csv:29 --card-padding: 12px (dense dashboard padding)")
print("")
print("=== breakpoint ladder: two CSV sets, union chosen ===")
# ux-guidelines.csv:66 Do = "Test at 320 375 414 768 1024 1440"
# stacks/html-tailwind.csv:32 Do = "320 375 768 1024 1280 1536"
# MASTER.md checklist line 202 area = 375/768/1024/1440 (design_system.py:459,801)
a = [320, 375, 414, 768, 1024, 1440]
b = [320, 375, 768, 1024, 1280, 1536]
print("set A (ux-guidelines.csv:66)      :", a)
print("set B (html-tailwind.csv:32)      :", b)
print("union (shipped)                   :", sorted(set(a) | set(b)))
print("intersection                      :", sorted(set(a) & set(b)))
