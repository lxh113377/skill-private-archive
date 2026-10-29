# -*- coding: ascii -*-
"""Arm-A evidence harness round 2: remediation tokens chosen AFTER measuring.

Round 1 (_evidence.py) proved two defects in the generator output: white text on
CTA #F59E0B = 2.15 (FAIL) and --border #DBEAFE vs #F8FAFC = 1.17 (fails the 3:1
UI-component rule). Round 2 measures the replacement candidates, and every hover/
active/disabled shade we ship, so the token table only carries numbers with a
recomputable verdict. Same WCAG 2.x formula as round 1 (chan() takes 0..1).
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
    ("on-cta #451A03 on CTA #F59E0B", "#451A03", "#F59E0B"),
    ("on-cta #78350F on CTA #F59E0B", "#78350F", "#F59E0B"),
    ("white on CTA-strong #B45309", "#FFFFFF", "#B45309"),
    ("white on CTA-strong #92400E", "#FFFFFF", "#92400E"),
    ("CTA-strong #B45309 on bg #F8FAFC (UI 3:1)", "#B45309", "#F8FAFC"),
    ("primary on tint #1E40AF on #DBEAFE", "#1E40AF", "#DBEAFE"),
    ("primary-hover #1E3A8A on bg #F8FAFC", "#1E3A8A", "#F8FAFC"),
    ("primary-active #172554 on bg #F8FAFC", "#172554", "#F8FAFC"),
    ("white on primary-hover #1E3A8A", "#FFFFFF", "#1E3A8A"),
    ("white on primary-active #172554", "#FFFFFF", "#172554"),
    ("focus ring #1D4ED8 on surface #FFFFFF (3:1)", "#1D4ED8", "#FFFFFF"),
    ("focus ring #1D4ED8 on primary #1E40AF (3:1)", "#1D4ED8", "#1E40AF"),
    ("body #0F172A on surface #FFFFFF", "#0F172A", "#FFFFFF"),
    ("muted #475569 on surface #FFFFFF", "#475569", "#FFFFFF"),
    ("muted #64748B on surface #FFFFFF", "#64748B", "#FFFFFF"),
    ("border-meaning #64748B on bg #F8FAFC (UI 3:1)", "#64748B", "#F8FAFC"),
    ("border-meaning #64748B on surface #FFFFFF (UI 3:1)", "#64748B", "#FFFFFF"),
    ("disabled label #94A3B8 on surface #FFFFFF (UI 3:1)", "#94A3B8", "#FFFFFF"),
    ("success #15803D on surface #FFFFFF", "#15803D", "#FFFFFF"),
    ("success #16A34A on bg #F8FAFC (UI 3:1)", "#16A34A", "#F8FAFC"),
    ("danger #DC2626 on bg #F8FAFC (UI 3:1)", "#DC2626", "#F8FAFC"),
    ("danger #B91C1C on surface #FFFFFF", "#B91C1C", "#FFFFFF"),
    ("warning #B45309 on #FEF3C7 (alert bg)", "#B45309", "#FEF3C7"),
    ("danger #B91C1C on #FEF2F2 (alert bg)", "#B91C1C", "#FEF2F2"),
    ("success #15803D on #F0FDF4 (alert bg)", "#15803D", "#F0FDF4"),
    ("info #1E40AF on #DBEAFE (alert bg)", "#1E40AF", "#DBEAFE"),
    ("dark: body #E2E8F0 on surface #1E293B", "#E2E8F0", "#1E293B"),
    ("dark: muted #94A3B8 on surface #1E293B", "#94A3B8", "#1E293B"),
    ("dark: primary #60A5FA on surface #1E293B", "#60A5FA", "#1E293B"),
    ("dark: surface #1E293B vs bg #0F172A (UI 3:1)", "#1E293B", "#0F172A"),
    ("chart s2 #3B82F6 on surface #FFFFFF (UI 3:1)", "#3B82F6", "#FFFFFF"),
    ("chart s4 #F59E0B on surface #FFFFFF (UI 3:1)", "#F59E0B", "#FFFFFF"),
    ("chart s3 #22C55E on surface #FFFFFF (UI 3:1)", "#22C55E", "#FFFFFF"),
    ("chart s7 #06B6D4 on surface #FFFFFF (UI 3:1)", "#06B6D4", "#FFFFFF"),
    ("chart s6 #8B5CF6 on surface #FFFFFF (UI 3:1)", "#8B5CF6", "#FFFFFF"),
    ("chart s1 #1E40AF on surface #FFFFFF (UI 3:1)", "#1E40AF", "#FFFFFF"),
]
print("=== WCAG CONTRAST ROUND 2 (computed by _evidence2.py) ===")
for name, fg, bg in PAIRS:
    r = ratio(fg, bg)
    v = "AAA" if r >= 7 else ("AA" if r >= 4.5 else ("AA-UI(>=3:1)" if r >= 3 else "FAIL"))
    print("%-52s ratio=%6.2f  verdict=%s" % (name, r, v))
print("")
print("=== type-scale derived from CSV-cited anchors ===")
# ux-guidelines.csv:75 cites the scale anchors 12 14 16 18 24 32; styles.csv:29 cites 12-14px
# dense body and 36px row height; styles.csv:31 cites 24-48px KPI. Everything below is
# arithmetic on those anchors (ratio printed for the record), not new invented numbers.
anchors = [12, 14, 16, 18, 24, 32, 48]
for i in range(1, len(anchors)):
    print("%d -> %d  step ratio = %.3f" % (anchors[i-1], anchors[i], anchors[i] / anchors[i-1]))
base = 16
for px in anchors:
    print("size.%d = %.2frem (base %d) ; line 1.5 -> %.1fpx" % (px, px / base, base, px * 1.5))
# 36px row height from styles.csv:29 Design System Variables column, expressed in the 8px grid
print("table-row 36px = 4.5 x 8px base unit (styles.csv:29 --table-row-height: 36px)")
print("sidebar 240px = 30 x 8px (styles.csv:29 --sidebar-width: 240px) ; header 56px (same row)")
