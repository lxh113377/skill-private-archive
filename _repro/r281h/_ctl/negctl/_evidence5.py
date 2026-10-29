# -*- coding: ascii -*-
"""Arm-A evidence round 5: closes every remaining numeric claim made in TOKENS.md.
Nothing may be tagged [MEAS] before it is computed here. Includes the alpha-blend case:
MASTER.md:130 emits the focus halo as 8-digit hex `#1E40AF20` over the page background,
which is NOT a solid color - we composite it (a = 0x20/255 = 12.55%) before measuring,
because a halo's job is a visible edge and that edge has to clear 3:1.
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

def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i+2], 16) for i in (0, 2, 4)]

def over(fg_hex, alpha, bg_hex):
    f, b = rgb(fg_hex), rgb(bg_hex)
    m = [round(f[i] * alpha + b[i] * (1 - alpha)) for i in range(3)]
    return "#%02X%02X%02X" % tuple(m), 0x20 / 255.0,

def blend(fg_hex, alpha, bg_hex):
    f, b = rgb(fg_hex), rgb(bg_hex)
    return "#%02X%02X%02X" % tuple(round(f[i] * alpha + b[i] * (1 - alpha)) for i in range(3))

print("=== ROUND 5 (computed by _evidence5.py) ===")
PAIRS = [
    ("waterfall increase #4CAF50 vs white (UI 3:1)", "#4CAF50", "#FFFFFF"),
    ("waterfall decrease #F44336 vs white (UI 3:1)", "#F44336", "#FFFFFF"),
    ("waterfall start #2196F3 vs white (UI 3:1)", "#2196F3", "#FFFFFF"),
    ("waterfall end #0D47A1 vs white", "#0D47A1", "#FFFFFF"),
    ("heatmap cool #0080FF vs white (UI 3:1)", "#0080FF", "#FFFFFF"),
    ("heatmap hot #FF0000 vs white (UI 3:1)", "#FF0000", "#FFFFFF"),
    ("alert red #EF4444 vs white (text duty?)", "#EF4444", "#FFFFFF"),
    ("accent #F59E0B vs white (UI 3:1)", "#F59E0B", "#FFFFFF"),
    ("secondary #3B82F6 vs white (UI 3:1)", "#3B82F6", "#FFFFFF"),
    ("violet #8B5CF6 vs #F8FAFC (UI 3:1)", "#8B5CF6", "#F8FAFC"),
    ("link #1E40AF vs hover tint #EFF6FF", "#1E40AF", "#EFF6FF"),
    ("heading #1E3A8A vs hover tint #EFF6FF", "#1E3A8A", "#EFF6FF"),
    ("body #0F172A vs skeleton #F1F5F9", "#0F172A", "#F1F5F9"),
    ("white vs danger #B91C1C (fill text)", "#FFFFFF", "#B91C1C"),
    ("dark primary #60A5FA vs page #F8FAFC (should fail on light)", "#60A5FA", "#F8FAFC"),
    ("#93C5FD vs dark page #0F172A", "#93C5FD", "#0F172A"),
    ("muted #94A3B8 vs dark surface #1E293B", "#94A3B8", "#1E293B"),
    ("#22C55E vs dark bg #0F172A", "#22C55E", "#0F172A"),
]
for name, fg, bg in PAIRS:
    r = ratio(fg, bg)
    v = "AAA" if r >= 7 else ("AA" if r >= 4.5 else ("AA-UI(>=3:1)" if r >= 3 else "FAIL"))
    print("%-52s ratio=%6.2f  %s" % (name, r, v))
print("")
print("=== focus halo alpha compositing (MASTER.md:130 emits #1E40AF20) ===")
A = 0x20 / 255.0
for bg in ("#F8FAFC", "#FFFFFF"):
    mix = blend("#1E40AF", A, bg)
    print("halo composite: #1E40AF a=%.3f over %s -> %s ; vs bg ratio=%.2f" % (A, bg, mix, ratio(mix, bg)))
B = 0x60 / 255.0
mix2 = blend("#93C5FD", B, "#F8FAFC")
print("shipped halo alt #93C5FD a=%.3f over #F8FAFC -> %s ratio=%.2f" % (B, mix2, ratio(mix2, "#F8FAFC")))
mix3 = blend("#1D4ED8", 1.0, "#F8FAFC")
print("shipped solid ring #1D4ED8 (a=1.0) over #F8FAFC -> %s ratio=%.2f" % (mix3, ratio(mix3, "#F8FAFC")))
