# -*- coding: ascii -*-
"""Arm-A evidence round 4: the remaining shipped values (borders, row hover, dark hairlines).
Purpose: no contrast verdict in TOKENS.md without a measured number. Same WCAG 2.x
formula as rounds 1-3. Decorative-only surfaces are reported as non-normative so a
reader does not mistake 1.2:1 for a pass.
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
    ("border.subtle #E2E8F0 vs page #F8FAFC", "#E2E8F0", "#F8FAFC"),
    ("border.subtle #E2E8F0 vs surface #FFFFFF", "#E2E8F0", "#FFFFFF"),
    ("border.default #CBD5E1 vs page #F8FAFC", "#CBD5E1", "#F8FAFC"),
    ("border.default #CBD5E1 vs surface #FFFFFF", "#CBD5E1", "#FFFFFF"),
    ("border.strong #64748B vs surface #FFFFFF", "#64748B", "#FFFFFF"),
    ("dark border.default #334155 vs dark surface #1E293B", "#334155", "#1E293B"),
    ("dark border.default #334155 vs dark bg #0F172A", "#334155", "#0F172A"),
    ("dark body #E2E8F0 vs dark surface #1E293B", "#E2E8F0", "#1E293B"),
    ("dark on-primary #0F172A vs primary #60A5FA", "#0F172A", "#60A5FA"),
    ("row hover #F1F5F9 vs surface #FFFFFF (non-normative)", "#F1F5F9", "#FFFFFF"),
    ("row selected #DBEAFE vs surface #FFFFFF (non-normative)", "#DBEAFE", "#FFFFFF"),
    ("row selected text #1E3A8A on #DBEAFE", "#1E3A8A", "#DBEAFE"),
    ("focus halo #93C5FD vs surface #FFFFFF", "#93C5FD", "#FFFFFF"),
    ("focus #1D4ED8 vs surface #FFFFFF", "#1D4ED8", "#FFFFFF"),
    ("link #1E40AF vs surface #FFFFFF", "#1E40AF", "#FFFFFF"),
    ("muted #64748B vs row-hover #F1F5F9", "#64748B", "#F1F5F9"),
    ("body #1E3A8A vs surface #FFFFFF", "#1E3A8A", "#FFFFFF"),
    ("white on CTA-strong #B45309 (recheck)", "#FFFFFF", "#B45309"),
]
print("=== WCAG CONTRAST ROUND 4 (computed by _evidence4.py) ===")
for name, fg, bg in PAIRS:
    r = ratio(fg, bg)
    v = "AAA" if r >= 7 else ("AA" if r >= 4.5 else ("AA-UI(>=3:1)" if r >= 3 else "FAIL/non-normative"))
    print("%-52s ratio=%6.2f  %s" % (name, r, v))
print("")
print("=== 44px and 8px-grid arithmetic (CSV-cited numbers only) ===")
print("touch min 44x44 px  (ux-guidelines.csv:23 Do)")
print("touch gap min 8 px  (ux-guidelines.csv:24 Do)")
print("button 12px 24px padding (MASTER.md:72-73, generator design_system.py:651)")
print("44px = 5.5 x 8px grid step; control heights 32/36/40/44 all multiples of 4px half-step")
for h in (28, 32, 36, 40, 44, 56):
    print("  height %dpx = %g x 8px-grid base(styles.csv:50 --base-unit: 8px)" % (h, h / 8))
