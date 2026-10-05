#!/usr/bin/env python3
"""Compose the two radar SVGs into one navy SIGNALS panel (assets/signals-*.svg).

GitHub tables cannot take a background colour, so the panel, the two charts and
the centre divider are drawn as a single image. Run after radar.py:
    python scripts/signals.py
"""
import re
from pathlib import Path

A = Path(__file__).resolve().parents[1] / "assets"
CHART_W, PAD, GAP = 400, 24, 40  # each chart drawn 400 wide, as in the README table
THEME = {"dark": ("#050B1A", "#142038"), "light": ("#EEF3FB", "#C3D0E6")}


def load(name):
    s = (A / name).read_text(encoding="utf-8")
    w, h = map(float, re.search(r'viewBox="0 0 (\S+) (\S+)"', s).groups())
    return s, w, h


for theme, (bg, line) in THEME.items():
    charts = [load(f"radar-{theme}.svg"), load(f"radar-langs-{theme}.svg")]
    sizes = [(CHART_W, CHART_W * h / w) for _, w, h in charts]
    half = CHART_W + GAP
    W, H = 2 * half, round(max(h for _, h in sizes) + 2 * PAD)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
           f'height="{H}" role="img" aria-label="Signals"><rect width="100%" height="100%" fill="{bg}"/>']
    for i, ((s, w, h), (cw, ch)) in enumerate(zip(charts, sizes)):
        x, y = i * half + GAP / 2, (H - ch) / 2
        font = re.search(r'font-family="([^"]*)"', s).group(1)  # lives on the root tag
        s = re.sub(r"<svg [^>]*>", f'<svg x="{x:.1f}" y="{y:.1f}" width="{cw}" height="{ch:.1f}" '
                   f'viewBox="0 0 {w:g} {h:g}" font-family="{font}">', s, count=1)
        out.append(s.rstrip().removesuffix("</svg>") + "</svg>")
    out.append(f'<path d="M{half} {PAD}V{H - PAD}" stroke="{line}"/></svg>')
    (A / f"signals-{theme}.svg").write_text("".join(out), encoding="utf-8")
    print(f"wrote signals-{theme}.svg ({W}x{H})")
