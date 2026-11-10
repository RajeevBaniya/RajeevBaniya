"""Write assets/toolkit.svg: idea -> plan -> build -> ship -> learn as glass tiles. Each icon acts
out its step while active (bulb lights, checklist ticks, code compiles, rocket launches, pages
flip); a spark carries the work to the next tile and a return arc closes the loop. Icons only.
Run by hand: python scripts/toolkit.py"""
from pathlib import Path

CYCLE, N = 12.5, 5                     # seconds per loop, steps
STEP = 100 / N                         # % of the cycle per step
XS = [102, 276, 450, 624, 798]         # tile centres
CY, H = 66, 46                         # tile centre y, half size

css, defs = [], []


def act(name, i, off, pts, extra=""):
    """Keyframes for step i: `off` outside the step, `pts` = [(fraction of step, css)] inside it."""
    s, e = i * STEP, (i + 1) * STEP
    d = {0: off, s: off}
    for f, v in pts:
        d[round(s + f * STEP, 2)] = v
    d.setdefault(round(e, 2), off)
    d.setdefault(100, off)
    frames = "".join(f"{p:g}%{{{v}}}" for p, v in sorted(d.items()))
    css.append(f"@keyframes {name}{{{frames}}}.{name}{{animation:{name} {CYCLE}s linear infinite;{extra}}}")
    return name


def loop(name, dur, frames, extra=""):
    """Short endlessly repeating motion (flicker, twinkle); parents gate when it shows."""
    css.append(f"@keyframes {name}{{{frames}}}.{name}{{animation:{name} {dur}s ease-in-out infinite alternate;{extra}}}")
    return name


FILL = "transform-box:fill-box;transform-origin:center"


# ---- icons (64x64 box, line style) -------------------------------------------------------
def idea(i):
    glow = act("bg", i, "opacity:0", [(.04, "opacity:0"), (.08, "opacity:.5"), (.11, "opacity:.08"),
                                      (.15, "opacity:.6"), (.9, "opacity:.6"), (1, "opacity:0")])
    rays = act("ry", i, "opacity:0;transform:scale(.6)", [(.12, "opacity:0;transform:scale(.6)"),
                                                          (.24, "opacity:1;transform:scale(1)"),
                                                          (.9, "opacity:1;transform:scale(1)"),
                                                          (1, "opacity:0;transform:scale(1.1)")])
    pulse = loop("rp", .7, "from{transform:scale(1)}to{transform:scale(1.12)}")
    lines = "".join(f'<path d="M0 -20V-25" transform="rotate({a})"/>' for a in (-90, -55, -20, 20, 55, 90))
    return (f'<circle class="{glow} acc" cx="32" cy="23" r="12" stroke="none"/>'
            f'<g transform="translate(32 23)"><g class="{rays}"><g class="{pulse}">{lines}</g></g></g>'
            '<path d="M32 6a17 17 0 0 0-10 31c2 2 3 4 3 7v2h14v-2c0-3 1-5 3-7A17 17 0 0 0 32 6zM25 51h14M28 57h8"/>'
            '<path d="M27 32l2.5-6 2.5 4 2.5-4 2.5 6"/>')


def plan(i):
    out = '<rect x="12" y="10" width="40" height="46" rx="5"/><rect x="24" y="5" width="16" height="9" rx="3"/>'
    for r, (y, t) in enumerate(zip((24, 36, 48), (.12, .34, .56))):
        ck = act(f"pc{r}", i, "stroke-dashoffset:0", [(0, "stroke-dashoffset:1"), (t, "stroke-dashoffset:1"),
                                                      (t + .1, "stroke-dashoffset:0")])
        ln = act(f"pl{r}", i, "stroke-dashoffset:0", [(0, "stroke-dashoffset:1"), (t + .06, "stroke-dashoffset:1"),
                                                      (t + .2, "stroke-dashoffset:0")])
        out += (f'<rect x="18" y="{y - 4}" width="7" height="7" rx="1.5" stroke-width="1.6"/>'
                f'<path class="{ck} acs" d="M17.5 {y - 1}l3 3 6-7" pathLength="1" stroke-dasharray="1"/>'
                f'<path class="{ln}" d="M31 {y}h14" pathLength="1" stroke-dasharray="1"/>')
    return out


def build(i):
    lb = act("bl0", i, "transform:none", [(.06, "transform:none"), (.14, "transform:translateX(-3px)"),
                                          (.24, "transform:none"), (.32, "transform:translateX(-3px)"),
                                          (.42, "transform:none")])
    rb = act("bl1", i, "transform:none", [(.06, "transform:none"), (.14, "transform:translateX(3px)"),
                                          (.24, "transform:none"), (.32, "transform:translateX(3px)"),
                                          (.42, "transform:none")])
    sl = act("bsl", i, "transform:none", [(.08, "transform:rotate(0)"), (.55, "transform:rotate(360deg)")])
    bar = act("bbr", i, "stroke-dashoffset:1;opacity:0", [(.06, "stroke-dashoffset:1;opacity:1"),
                                                          (.78, "stroke-dashoffset:0;opacity:1"),
                                                          (.84, "stroke-dashoffset:0;opacity:.35"),
                                                          (.9, "stroke-dashoffset:0;opacity:1"),
                                                          (1, "stroke-dashoffset:0;opacity:0")])
    return (f'<g class="{lb}"><path d="M22 20 8 32l14 12"/></g><g class="{rb}"><path d="M42 20l14 12-14 12"/></g>'
            f'<g transform="translate(32 32)"><g class="{sl}"><path d="M4 -19-4 19"/></g></g>'
            '<path d="M14 60H50" opacity=".25"/>'
            f'<path class="{bar} acs" d="M14 60H50" pathLength="1" stroke-dasharray="1"/>')


def ship(i):
    shake = [(.06 + k * .035, f"transform:translate({.9 if k % 2 else -.9}px,0)") for k in range(8)]
    fly = act("sr", i, "transform:none", [(.04, "transform:none"), *shake,
                                          (.36, "transform:none;animation-timing-function:cubic-bezier(.55,0,1,.45)"),
                                          (.66, "transform:translateY(-70px)"),
                                          (.661, "transform:translateY(70px);animation-timing-function:cubic-bezier(0,.55,.45,1)"),
                                          (.92, "transform:none")])
    flame = act("sf", i, "opacity:0", [(.05, "opacity:0"), (.1, "opacity:1"), (.66, "opacity:1"),
                                       (.7, "opacity:0"), (.8, "opacity:0"), (.86, "opacity:.6"), (.95, "opacity:0")])
    flick = loop("fl", .09, "from{transform:scaleY(.7)}to{transform:scaleY(1.3)}")
    speed = act("ss", i, "opacity:0", [(.38, "opacity:0"), (.45, "opacity:.8"), (.62, "opacity:.8"), (.68, "opacity:0")])
    zoom = loop("sz", .18, "from{transform:translateY(-8px)}to{transform:translateY(10px)}")
    puffs = ""
    for k, (x, y) in enumerate(((24, 50), (32, 54), (40, 50))):
        p = act(f"sp{k}", i, "opacity:0;transform:scale(.4)",
                [(.1 + k * .04, "opacity:0;transform:scale(.4)"), (.3 + k * .04, "opacity:.45;transform:scale(1)"),
                 (.62, "opacity:0;transform:scale(2)")], FILL)
        puffs += f'<circle class="{p}" cx="{x}" cy="{y}" r="3.2" fill="currentColor" stroke="none"/>'
    return (f'<g clip-path="url(#tc)">{puffs}'
            f'<g class="{speed}"><g class="{zoom}"><path d="M16 6v12M48 14v10M24 0v8M42 -2v8" opacity=".6"/></g></g>'
            f'<g class="{fly}"><g transform="translate(32 41)"><g class="{flame}"><g class="{flick}">'
            '<path class="acc" d="M-5 0Q0 18 5 0z" stroke="none"/></g></g></g>'
            '<path d="M32 4c11 8 13 22 9 36H23C19 26 21 12 32 4z"/><circle cx="32" cy="22" r="4"/>'
            '<path d="M23 32 13 44l10-3M41 32l10 12-10-3M28 46q4 12 8 0"/></g></g>')


def learn(i):
    flip = act("lf", i, "opacity:0;transform:scaleX(1)",
               [(.1, "opacity:0;transform:scaleX(1)"), (.12, "opacity:1;transform:scaleX(1)"),
                (.36, "opacity:1;transform:scaleX(-1)"), (.38, "opacity:0;transform:scaleX(-1)"),
                (.42, "opacity:0;transform:scaleX(1)"), (.44, "opacity:1;transform:scaleX(1)"),
                (.68, "opacity:1;transform:scaleX(-1)"), (.7, "opacity:0;transform:scaleX(-1)")])
    spark = act("lk", i, "opacity:0", [(.4, "opacity:0"), (.5, "opacity:1"), (.92, "opacity:1"), (1, "opacity:0")])
    stars = ""
    for k, (x, y, s) in enumerate(((10, 4, .8), (54, 2, 1), (44, -6, .6))):
        tw = loop(f"tw{k}", .5 + k * .17, "from{transform:scale(.3)}to{transform:scale(1)}", FILL)
        stars += (f'<g transform="translate({x} {y}) scale({s})"><path class="{tw} acc" stroke="none" '
                  'd="M0-6Q1-1 6 0Q1 1 0 6Q-1 1-6 0Q-1-1 0-6z"/></g>')
    return (f'<g class="{spark}">{stars}</g>'
            '<path d="M32 17C26 11 16 11 7 13v36c9-2 19-2 25 4 6-6 16-6 25-4V13c-9-2-19-2-25 4zM32 17v36"/>'
            f'<g transform="translate(32 0)"><g class="{flip}">'
            '<path class="pg" d="M0 17c6-6 16-6 25-4v36c-9-2-19-2-25 4z"/>'
            '<path d="M5 22c4-2 9-3 15-2M5 29c4-2 9-3 15-2M5 36c4-2 9-3 15-2" stroke-width="1.4" opacity=".7"/></g></g>')


ICONS = [idea, plan, build, ship, learn]

# ---- shared look -------------------------------------------------------------------------
css.append(""":root{--ac:#116329;--ed:#1A7F37;--mu:#656D76;--gla:.55;--glb:.05;--glow:.28;--rail:#D0D7DE;--pg:#F6FBF7}
@media (prefers-color-scheme:dark){:root{--ac:#7EE787;--ed:#39D353;--mu:#7D8590;--gla:.07;--glb:.035;--glow:.5;--rail:#30363D;--pg:#14231A}}
.ic{fill:none;stroke:currentColor;stroke-width:2.1;stroke-linecap:round;stroke-linejoin:round}
.ic circle{fill:currentColor;stroke:none}
.acc{fill:var(--ed)}.acs{stroke:var(--ac)}.pg{fill:var(--pg)}
.rail{stroke:var(--rail);stroke-width:1.5;stroke-linecap:round;stroke-dasharray:1 7;fill:none}
.lit{stroke:var(--ed);stroke-width:2;stroke-linecap:round;fill:none}
.s0{stop-color:#FFFFFF;stop-opacity:var(--gla)}.s1{stop-color:var(--ed);stop-opacity:var(--glb)}.s2{stop-color:var(--ed);stop-opacity:.015}
.e0{stop-color:var(--ed);stop-opacity:.5}.e1{stop-color:var(--ed);stop-opacity:.1}.e2{stop-color:var(--ed);stop-opacity:.35}
.ac{stop-color:var(--ed)}
.glass{fill:url(#gf);stroke:url(#ge);stroke-width:1.3}
.ring{fill:none;stroke:var(--ed);stroke-width:2;stroke-linecap:round;stroke-dasharray:100}
.halo{fill:var(--ed)}
@keyframes bob{50%{transform:translateY(-3px)}}.bob{animation:bob 5s ease-in-out infinite}""")

body = []
for i, x in enumerate(XS):
    s, e = i * STEP, (i + 1) * STEP
    k = act(f"k{i}", i, "color:var(--mu)", [(.03, "color:var(--ac)"), (.97, "color:var(--ac)")])
    h = act(f"h{i}", i, "opacity:0", [(.04, "opacity:var(--glow)"), (.96, "opacity:var(--glow)")])
    lift = act(f"l{i}", i, "transform:none", [(.08, "transform:translateY(-5px)"), (.92, "transform:translateY(-5px)")])
    ring = act(f"r{i}", i, "stroke-dashoffset:100;opacity:0",
               [(.02, "stroke-dashoffset:100;opacity:.9"), (.8, "stroke-dashoffset:0;opacity:.9"),
                (1, "stroke-dashoffset:0;opacity:0")])
    css.append(f".b{i}{{animation-delay:-{i * .9:g}s}}")
    r = H - 2
    body.append(
        f'<g transform="translate({x} {CY})"><g class="bob b{i}"><g class="{lift}">'
        f'<circle class="halo {h}" r="40" filter="url(#bl)"/>'
        f'<rect class="glass" x="-{H}" y="-{H}" width="{2 * H}" height="{2 * H}" rx="26"/>'
        f'<path d="M-{H - 18} -{H - .8}H{H - 18}" stroke="#FFFFFF" stroke-opacity=".22" stroke-linecap="round"/>'
        f'<rect class="ring {ring}" x="-{r}" y="-{r}" width="{2 * r}" height="{2 * r}" rx="24" pathLength="100"/>'
        f'<g class="{k}"><g transform="translate(-28.8 -28.8) scale(.9)"><g class="ic">{ICONS[i](i)}</g></g></g>'
        f'</g></g></g>')

# Rails + sparks: the spark leaves in the last 35% of a step and lands as the next tile lights.
rails, sparks = [], []
gap = H + 12
for i in range(N):
    e = (i + 1) * STEP
    t0, t1 = (e - STEP * .35) / 100, e / 100
    if i < N - 1:
        d = f"M{XS[i] + gap} {CY}H{XS[i + 1] - gap}"
        L = XS[i + 1] - XS[i] - 2 * gap
        rails.append(f'<path class="rail" d="{d}"/>'
                     f'<path class="lit" d="{d}" stroke-dasharray="{L}" stroke-dashoffset="{L}" opacity="0">'
                     f'<animate attributeName="stroke-dashoffset" dur="{CYCLE}s" repeatCount="indefinite" '
                     f'keyTimes="0;{t0:.3f};{t1:.3f};1" values="{L};{L};0;0"/>'
                     f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
                     f'keyTimes="0;{t0:.3f};.9;.97;1" values="0;.55;.55;0;0"/></path>')
    else:  # learn -> idea underneath closes the loop
        d = f"M{XS[-1]} {CY + H + 8}C{XS[-1]} {CY + H + 52} {XS[0]} {CY + H + 52} {XS[0]} {CY + H + 8}"
        rails.append(f'<path class="rail" d="{d}" opacity=".7"/>')
    sparks.append(
        f'<g opacity="0"><animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
        f'keyTimes="0;{t0:.3f};{t0 + .01:.3f};{t1 - .01:.3f};{t1:.3f};1" values="0;0;1;1;0;0"/>'
        f'<animateMotion dur="{CYCLE}s" repeatCount="indefinite" path="{d}" calcMode="spline" '
        f'keyPoints="0;0;1;1" keyTimes="0;{t0:.3f};{t1 - .001:.3f};1" keySplines="0 0 1 1;.45 0 .55 1;0 0 1 1"/>'
        f'<circle r="15" fill="url(#rg)"/><circle r="3.6" class="halo"/><circle r="1.6" fill="#FFFFFF" opacity=".9"/></g>')

css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 175" width="900" height="175">
<title>Idea, plan, build, ship, learn</title>
<style>{"".join(css)}</style>
<defs><filter id="bl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="12"/></filter>
<clipPath id="tc"><rect x="-19" y="-19" width="102" height="102" rx="29"/></clipPath>
<linearGradient id="gf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" class="s0"/><stop offset=".5" class="s1"/><stop offset="1" class="s2"/></linearGradient>
<linearGradient id="ge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" class="e0"/><stop offset=".5" class="e1"/><stop offset="1" class="e2"/></linearGradient>
<radialGradient id="rg"><stop offset="0" class="ac" stop-opacity=".7"/><stop offset="1" class="ac" stop-opacity="0"/></radialGradient></defs>
{"".join(rails)}{"".join(body)}{"".join(sparks)}
</svg>
'''
Path(__file__).resolve().parents[1].joinpath("assets/toolkit.svg").write_text(svg, encoding="utf-8", newline="\n")
print("wrote assets/toolkit.svg", len(svg), "bytes")
