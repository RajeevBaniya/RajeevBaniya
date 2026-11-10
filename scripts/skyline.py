#!/usr/bin/env python3
"""Draw the last 26 weeks of contributions as an isometric 3D city into the right
half of assets/signals-{dark,light}.svg. Stdlib only.

    python scripts/skyline.py --user RajeevBaniya

Only the region between <!-- skyline --> and <!-- /skyline --> is rewritten
(first run: the old right-half block). The left radar and metadata are untouched.
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import re
import sys
from pathlib import Path

from cards import contribution_days, streaks

ASSETS = Path(__file__).resolve().parents[1] / "assets"
WEEKS = 26
K, ANGLE = 12.2, math.radians(27)            # cell size, isometric tilt
CX, SY = K * math.cos(ANGLE), K * math.sin(ANGLE)
GAP, MAX_H, FLOOR_H = 0.8, 70.0, 1.5
BOX = (452, 82, 868, 330)                    # city fits here (x0, y0, x1, y1)

THEMES = {
    "dark": {"levels": ["#21262D", "#0E4429", "#006D32", "#26A641", "#39D353"],
             "peak": "#A6F4B1", "accent": "#39D353", "text": "#E6EDF3", "muted": "#7D8590",
             "line": "#30363D", "plat": ("#161B22", "#1C2128", "#12161C"),
             "shadow": ("#000000", .55)},
    "light": {"levels": ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"],
              "peak": "#2DA44E", "accent": "#1A7F37", "text": "#1F2328", "muted": "#656D76",
              "line": "#D0D7DE", "plat": ("#FFFFFF", "#E6EAEF", "#D0D7DE"),
              "shadow": ("#1F2328", .16)},
}


def shade(hex_color: str, k: float) -> str:
    r, g, b = (min(255, round(int(hex_color[i:i + 2], 16) * k)) for i in (1, 3, 5))
    return "#%02X%02X%02X" % (r, g, b)


def level(count: int, peak: int) -> int:
    return 0 if count == 0 else min(4, 1 + int(4 * count / (peak + 1)))


def pt(w, d, lift=0.0):
    """Floor coords (week, weekday) -> raw screen coords; weeks run up-right, days down-right."""
    return ((w + d) * CX, (d - w) * SY - lift)


def poly(points, fill, extra="") -> str:
    return '<path d="M%s Z" fill="%s"%s/>' % (
        " L".join(f"{x:.1f} {y:.1f}" for x, y in points), fill, extra)


def prism(w0, d0, w1, d1, h, top, left, right, base=0.0, extra=""):
    """Visible faces of a box: left (w-start), right (d-end), top (last, so it can be patched)."""
    L, T, R, B = (w0, d0), (w1, d0), (w1, d1), (w0, d1)
    up = lambda p: pt(*p, base + h)
    dn = lambda p: pt(*p, base)
    return (poly([up(L), up(B), dn(B), dn(L)], left)
            + poly([up(B), up(R), dn(R), dn(B)], right)
            + poly([up(L), up(T), up(R), up(B)], top, extra))


def fade(delay, dur=.5):
    return (f'<animate attributeName="opacity" values="0;1" begin="{delay:.2f}s" dur="{dur}s" '
            f'fill="freeze"/>')


def render(grid, dates, theme: str, today: dt.date) -> str:
    """grid[w][d] = count (w = week, 0 oldest; d = weekday, 0 Sunday); dates[w][d] likewise."""
    t = THEMES[theme]
    acc = t["accent"]
    flat = [c for col in grid for c in col]
    peak = max(flat) or 1
    total, active = sum(flat), sum(c > 0 for c in flat)
    cells = [(w, d) for w in range(WEEKS) for d in range(7) if dates[w][d]]
    current, _ = streaks([(dates[w][d], grid[w][d]) for w, d in cells])
    lw, ld = cells[-1]                                       # today
    height = lambda c: FLOOR_H if c == 0 else FLOOR_H + MAX_H * math.sqrt(c / peak)

    # Fit: scale + translate the raw drawing into BOX.
    pw0, pd0, pw1, pd1 = -.5, -.5, WEEKS + .5, 8.4          # platform (front margin holds months)
    xs = [pt(w, d)[0] for w in (pw0, pw1) for d in (pd0, pd1)]
    ys = [pt(w, d)[1] for w in (pw0, pw1) for d in (pd0, pd1)] + [pt(pw0, pd1)[1] + 8]
    ys += [pt(w + .5, d + .5, height(grid[w][d]))[1] for w, d in cells]
    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    s = min((BOX[2] - BOX[0]) / bw, (BOX[3] - BOX[1]) / bh)
    tx = (BOX[0] + BOX[2]) / 2 - s * (min(xs) + max(xs)) / 2
    ty = (BOX[1] + BOX[3]) / 2 - s * (min(ys) + max(ys)) / 2

    a, b = (1 - GAP) / 2, (1 + GAP) / 2
    rise_end = .4 + (WEEKS + 3) * .035 + .7
    out = ['<!-- skyline -->',
           '<defs>'
           '<filter id="skBlur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>'
           f'<linearGradient id="skScan" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{acc}" stop-opacity=".45"/>'
           f'<stop offset=".35" stop-color="{acc}" stop-opacity=".12"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></linearGradient>'
           f'<linearGradient id="skBeam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{acc}" stop-opacity=".9"/>'
           f'<stop offset="1" stop-color="{acc}" stop-opacity="0"/></linearGradient>'
           '</defs>',
           f'<text x="660" y="46" text-anchor="middle" font-size="20" font-weight="700" '
           f'fill="{acc}">Activity Skyline{fade(0, .6)}</text>',
           f'<text x="660" y="68" text-anchor="middle" font-size="10.5" letter-spacing="1.4" fill="{t["muted"]}">'
           f'LAST {WEEKS} WEEKS  ·  UPDATED {today.strftime("%d %b").upper()}{fade(.2)}</text>',
           # LIVE pill
           f'<g opacity="0">{fade(.3)}<rect x="808" y="31" width="52" height="19" rx="9.5" fill="{acc}" '
           f'fill-opacity=".12" stroke="{acc}" stroke-opacity=".5"/>'
           f'<circle cx="820" cy="40.5" r="3" fill="{acc}"><animate attributeName="r" values="3;6;3" '
           f'dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0;1" dur="2s" '
           f'repeatCount="indefinite"/></circle><circle cx="820" cy="40.5" r="2.6" fill="{acc}"/>'
           f'<text x="828" y="44.5" font-size="10" font-weight="700" letter-spacing="1" fill="{acc}">LIVE</text></g>']

    # Ground shadow (stays put while the city floats).
    fp = [pt(pw0, pd0), pt(pw1, pd0), pt(pw1, pd1), pt(pw0, pd1)]
    so = t["shadow"][1]
    out.append(f'<g transform="translate({tx:.1f} {ty + 12:.1f}) scale({s:.4f})" opacity="{so}" '
               f'filter="url(#skBlur)">{poly(fp, t["shadow"][0])}'
               f'<animate attributeName="opacity" values="{so};{so * .6:.2f};{so}" '
               f'dur="6s" repeatCount="indefinite"/></g>')

    city = []
    p_top, p_left, p_right = t["plat"]
    city.append(prism(pw0, pd0, pw1, pd1, 7, p_top, p_left, p_right, base=-7,
                      extra=f' stroke="{t["line"]}" stroke-width=".8"'))

    # Month labels lying flat on the platform's front margin.
    m = f"matrix({CX / K:.4f} {-SY / K:.4f} {CX / K:.4f} {SY / K:.4f} {{x:.1f}} {{y:.1f}})"
    seen = set()
    for w in range(WEEKS - 1):
        first = next((x for x in dates[w] if x and x.day <= 7), None)
        if first and first.month not in seen:
            seen.add(first.month)
            x, y = pt(w + .15, 7.55)
            city.append(f'<text transform="{m.format(x=x, y=y)}" font-size="8.5" font-weight="600" '
                        f'letter-spacing=".6" fill="{t["muted"]}" opacity="0">'
                        f'{first.strftime("%b").upper()}{fade(.4)}</text>')

    # Towers, back to front.
    for w in range(WEEKS - 1, -1, -1):
        for d in range(7):
            if not dates[w][d]:
                continue
            c = grid[w][d]
            col = t["levels"][level(c, peak)]
            body = prism(w + a, d + a, w + b, d + b, height(c), col, shade(col, .78), shade(col, .58))
            if c == peak and c > 0:   # busiest day: roof twinkles
                body = (body[:-2] + f'><animate attributeName="fill" values="{col};{t["peak"]};{col}" '
                        f'begin="{rise_end:.1f}s" dur="2.4s" repeatCount="indefinite"/></path>')
            if c == 0:
                city.append(body)
                continue
            px, py = pt(w + a, d + b)
            begin = .4 + (w + (6 - d) * .5) * .035
            city.append(
                f'<g transform="translate({px:.1f} {py:.1f})"><g transform="scale(1 0)">'
                f'<animateTransform attributeName="transform" type="scale" values="1 0;1 1.12;1 1" '
                f'keyTimes="0;.7;1" calcMode="spline" keySplines=".3 0 .4 1;.4 0 .6 1" '
                f'begin="{begin:.2f}s" dur=".7s" fill="freeze"/>'
                f'<g transform="translate({-px:.1f} {-py:.1f})">{body}</g></g></g>')

    # Today: beacon beam + expanding ring on its roof.
    h = height(grid[lw][ld])
    cx, cy = pt(lw + .5, ld + .5, h)
    ring = [pt(lw + a, ld + a, h), pt(lw + b, ld + a, h), pt(lw + b, ld + b, h), pt(lw + a, ld + b, h)]
    ring = [(x - cx, y - cy) for x, y in ring]
    ring_attr = f' stroke="{acc}" stroke-width="1.2" vector-effect="non-scaling-stroke"'
    city.append(
        f'<g opacity="0">{fade(rise_end - .3)}'
        f'<rect x="{cx - 1.2:.1f}" y="{cy - 46:.1f}" width="2.4" height="46" fill="url(#skBeam)">'
        f'<animate attributeName="opacity" values=".35;1;.35" dur="2s" repeatCount="indefinite"/></rect>'
        f'<g transform="translate({cx:.1f} {cy:.1f})"><g>'
        f'<animateTransform attributeName="transform" type="scale" values="1;2.6" dur="2s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;0" dur="2s" repeatCount="indefinite"/>'
        f'{poly(ring, "none", ring_attr)}</g></g></g>')

    # Scanner: a translucent light wall sweeping along the weeks.
    hgt = MAX_H + 24
    wall = [pt(0, pd0), pt(0, 7.6), pt(0, 7.6, hgt), pt(0, pd0, hgt)]
    sx0, sy0 = pt(-.5, 0)
    sx1, sy1 = pt(WEEKS + .5, 0)
    city.append(
        f'<g opacity="0"><animateTransform attributeName="transform" type="translate" '
        f'values="{sx0:.1f} {sy0:.1f};{sx1:.1f} {sy1:.1f};{sx1:.1f} {sy1:.1f}" keyTimes="0;.75;1" '
        f'begin="{rise_end:.1f}s" dur="7s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.08;.67;.75;1" '
        f'begin="{rise_end:.1f}s" dur="7s" repeatCount="indefinite"/>'
        f'{poly(wall, "url(#skScan)")}'
        f'<path d="M{wall[0][0]:.1f} {wall[0][1]:.1f} L{wall[1][0]:.1f} {wall[1][1]:.1f}" '
        f'stroke="{acc}" stroke-width="1.6" stroke-linecap="round"/></g>')

    out.append(f'<g transform="translate({tx:.1f} {ty:.1f}) scale({s:.4f})"><g>'
               f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" '
               f'dur="6s" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1" '
               f'repeatCount="indefinite"/>\n' + "\n".join(city) + '\n</g></g>')

    # Stat chips.
    chips = [(f"{total:,}", "CONTRIBUTIONS"), (str(peak), "BEST DAY"),
             (str(current), "DAY STREAK"), (str(active), "ACTIVE DAYS")]
    cw, gap, y0 = 98, 8, 344
    x0 = 660 - (len(chips) * cw + (len(chips) - 1) * gap) / 2
    for i, (val, label) in enumerate(chips):
        x = x0 + i * (cw + gap)
        dl = 1.2 + i * .12
        out.append(
            f'<g opacity="0">{fade(dl)}<animateTransform attributeName="transform" type="translate" '
            f'values="0 8;0 0" begin="{dl:.2f}s" dur=".5s" calcMode="spline" keyTimes="0;1" '
            f'keySplines=".2 .8 .3 1" fill="freeze"/>'
            f'<rect x="{x:.1f}" y="{y0}" width="{cw}" height="42" rx="8" fill="{acc}" fill-opacity=".06" stroke="{acc}" stroke-opacity=".3"/>'
            f'<text x="{x + cw / 2:.1f}" y="{y0 + 20}" text-anchor="middle" font-size="16" font-weight="700" '
            f'fill="{acc if i else t["text"]}">{val}</text>'
            f'<text x="{x + cw / 2:.1f}" y="{y0 + 34}" text-anchor="middle" font-size="8.5" '
            f'letter-spacing="1" fill="{t["muted"]}">{label}</text></g>')

    out.append('<!-- /skyline -->')
    return "\n".join(out) + "\n"


def splice(svg: str, block: str) -> str:
    marked = re.compile(r"<!-- skyline -->.*?<!-- /skyline -->\n?", re.S)
    if marked.search(svg):
        return marked.sub(lambda _: block, svg, count=1)
    old = re.compile(r'<text x="660" y="46".*?(?=<rect x="1" y="1" width="878")', re.S)
    new, n = old.subn(lambda _: block, svg, count=1)
    if n != 1:
        sys.exit("could not find the right-half block to replace")
    return new


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--user", required=True)
    args = p.parse_args(argv)

    days = contribution_days(args.user, os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    if not days:
        sys.exit("no contribution data; leaving signals untouched")
    # Whole weeks, Sunday-first like GitHub; the current week is partial.
    last = days[-1][0]
    start_idx = len(days) - (WEEKS - 1) * 7 - ((last.weekday() + 1) % 7) - 1
    grid = [[0] * 7 for _ in range(WEEKS)]
    dates = [[None] * 7 for _ in range(WEEKS)]
    for i, (day, c) in enumerate(days[max(start_idx, 0):]):
        grid[i // 7][i % 7], dates[i // 7][i % 7] = c, day

    for theme in THEMES:
        f = ASSETS / f"signals-{theme}.svg"
        f.write_text(splice(f.read_text(encoding="utf-8"), render(grid, dates, theme, last)),
                     encoding="utf-8", newline="\n")
        print(f"wrote {f.name}  ({sum(map(sum, grid))} contributions, {WEEKS} weeks)")


if __name__ == "__main__":
    main()
