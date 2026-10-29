# -*- coding: ascii -*-
"""Arm-A evidence harness (read-only on D:/global_skills). Run: python _evidence.py.

Job 1: WCAG 2.x contrast ratios for every hex pair the token table ships, so each
       pass/fail claim is recomputable instead of asserted. Algorithm: per channel
       c8 = value/255, linearize (c8/12.92 if c8<=0.03928 else ((c8+0.055)/1.055)^2.4),
       L = 0.2126R + 0.7152G + 0.0722B, ratio = (Lmax+0.05)/(Lmin+0.05).
       v1 bug: chan() divided by 255 a second time after lum() already did it,
       which squeezed every channel toward 0 and printed ratio=1.00 for all pairs.
Job 2: dump 1-based line numbers + raw text of the CSV rows cited as provenance,
       so each numeric token traces to file:line (grep/read line numbers match).
"""
import io
D = "D:/global_skills/ui-ux-pro-max/data/"

def chan(c8):
    # c8 is already 0..1; linearize the sRGB component per WCAG definition
    return c8 / 12.92 if c8 <= 0.03928 else ((c8 + 0.055) / 1.055) ** 2.4

def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

PAIRS = [
    ("body #1E3A8A on bg #F8FAFC", "#1E3A8A", "#F8FAFC"),
    ("body #0F172A on bg #F8FAFC", "#0F172A", "#F8FAFC"),
    ("primary #1E40AF on bg #F8FAFC", "#1E40AF", "#F8FAFC"),
    ("primary #1E40AF on surface #FFFFFF", "#1E40AF", "#FFFFFF"),
    ("on-primary #FFFFFF on primary #1E40AF", "#FFFFFF", "#1E40AF"),
    ("on-cta #FFFFFF on CTA #F59E0B", "#FFFFFF", "#F59E0B"),
    ("on-cta #78350F on CTA #F59E0B", "#78350F", "#F59E0B"),
    ("CTA #F59E0B on bg #F8FAFC (icon/UI 3:1)", "#F59E0B", "#F8FAFC"),
    ("secondary #3B82F6 on bg #F8FAFC", "#3B82F6", "#F8FAFC"),
    ("muted #475569 on bg #F8FAFC", "#475569", "#F8FAFC"),
    ("muted #64748B on bg #F8FAFC", "#64748B", "#F8FAFC"),
    ("border #DBEAFE on bg #F8FAFC (UI 3:1)", "#DBEAFE", "#F8FAFC"),
    ("border #94A3B8 on bg #F8FAFC (UI 3:1)", "#94A3B8", "#F8FAFC"),
    ("success text #15803D on bg #F8FAFC", "#15803D", "#F8FAFC"),
    ("success #22C55E on bg #F8FAFC (UI 3:1)", "#22C55E", "#F8FAFC"),
    ("warning text #B45309 on bg #F8FAFC", "#B45309", "#F8FAFC"),
    ("danger text #B91C1C on bg #F8FAFC", "#B91C1C", "#F8FAFC"),
    ("danger #EF4444 on bg #F8FAFC (UI 3:1)", "#EF4444", "#F8FAFC"),
    ("focus ring #1D4ED8 on bg #F8FAFC (UI 3:1)", "#1D4ED8", "#F8FAFC"),
    ("on-danger #FFFFFF on danger #B91C1C", "#FFFFFF", "#B91C1C"),
    ("dark text #E2E8F0 on dark bg #0F172A", "#E2E8F0", "#0F172A"),
    ("dark muted #94A3B8 on dark bg #0F172A", "#94A3B8", "#0F172A"),
]
print("=== WCAG CONTRAST (computed by _evidence.py) ===")
for name, fg, bg in PAIRS:
    r = ratio(fg, bg)
    v = "AAA" if r >= 7 else ("AA" if r >= 4.5 else ("AA/UI(>=3:1)" if r >= 3 else "FAIL"))
    print("%-44s ratio=%5.2f  verdict=%s" % (name, r, v))

print("")
print("=== CITED CSV ROWS (file:line -> raw line) ===")
CITES = [("colors.csv", [1, 9, 15, 23]),
         ("typography.csv", [1, 43, 48, 52, 58]),
         ("styles.csv", [29, 30, 31, 34, 37, 47]),
         ("ux-guidelines.csv", [1, 11, 29, 32, 33, 37, 66, 68, 75, 79, 80]),
         ("charts.csv", [1, 2, 5, 8, 14]),
         ("web-interface.csv", [4, 16]),
         ("stacks/html-tailwind.csv", [5, 29, 31, 32, 39]),
         ("landing.csv", [1]),
         ("products.csv", [1])]
for fname, lns in CITES:
    with io.open(D + fname, "r", encoding="utf-8") as f:
        all_lines = f.read().splitlines()
    for n in lns:
        txt = all_lines[n - 1] if 0 < n <= len(all_lines) else "OUT OF RANGE (file has %d lines)" % len(all_lines)
        print("%s:%d | %s" % (fname, n, txt[:200]))
