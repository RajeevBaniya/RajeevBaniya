"""Write assets/toolkit.svg: idea -> plan -> build -> ship -> learn as glass tiles with a
travelling spark and a return arc closing the loop. Icons only, no text. Run once by hand."""
from pathlib import Path

CYCLE, N = 10, 5                       # seconds per loop, steps
XS = [102, 276, 450, 624, 798]         # tile centres
CY, H = 66, 46                         # tile centre y, half size
ICONS = [  # 64x64 line icons
    '<path d="M32 6a17 17 0 0 0-10 31c2 2 3 4 3 7v2h14v-2c0-3 1-5 3-7A17 17 0 0 0 32 6zM25 51h14M28 57h8"/><path d="M32 16a8 8 0 0 0-6 7"/>',
    '<rect x="12" y="10" width="40" height="46" rx="5"/><rect x="24" y="5" width="16" height="9" rx="3"/><path d="M19 28l3 3 5-6M19 40l3 3 5-6M34 28h11M34 40h11M34 50h11"/><rect x="19" y="47" width="7" height="7" rx="1.5"/>',
    '<path d="M22 20 8 32l14 12M42 20l14 12-14 12M36 13 28 51"/>',
    '<path d="M32 4c11 8 13 22 9 36H23C19 26 21 12 32 4z"/><circle cx="32" cy="22" r="4"/><path d="M23 32 13 44l10-3M41 32l10 12-10-3M28 46q4 12 8 0"/>',
    '<path d="M32 17C26 11 16 11 7 13v36c9-2 19-2 25 4 6-6 16-6 25-4V13c-9-2-19-2-25 4zM32 17v36"/>',
]
STEP = 100 / N


def kf(name, off, on, s, e, ramp=2.0):
    """Keyframes: `off` outside [s, e], `on` inside, short ramps at both ends."""
    pts = sorted({0: off, s: off if s else on, min(s + ramp, e): on, max(e - ramp, s): on, e: off, 100: off}.items())
    if s == 0:
        pts = [(p, on if p < e else v) for p, v in pts]
    return f"@keyframes {name}{{" + "".join(f"{p:g}%{{{v}}}" for p, v in pts) + "}"


css, body = [], []
css.append(""":root{--ac:#116329;--ed:#1A7F37;--mu:#656D76;--gl0:#FFFFFF;--gla:.55;--glb:.05;--glow:.28;--rail:#D0D7DE}
@media (prefers-color-scheme:dark){:root{--ac:#7EE787;--ed:#39D353;--mu:#7D8590;--gl0:#FFFFFF;--gla:.07;--glb:.035;--glow:.5;--rail:#30363D}}
.ic{fill:none;stroke:currentColor;stroke-width:2.1;stroke-linecap:round;stroke-linejoin:round}
.ic circle{fill:currentColor;stroke:none}
.rail{stroke:var(--rail);stroke-width:1.5;stroke-linecap:round;stroke-dasharray:1 7;fill:none}
.lit{stroke:var(--ed);stroke-width:2;stroke-linecap:round;fill:none;opacity:.55}
.s0{stop-color:var(--gl0);stop-opacity:var(--gla)}.s1{stop-color:var(--ed);stop-opacity:var(--glb)}.s2{stop-color:var(--ed);stop-opacity:.015}
.e0{stop-color:var(--ed);stop-opacity:.5}.e1{stop-color:var(--ed);stop-opacity:.1}.e2{stop-color:var(--ed);stop-opacity:.35}
.ac{stop-color:var(--ed)}
.glass{fill:url(#gf);stroke:url(#ge);stroke-width:1.3}
.ring{fill:none;stroke:var(--ed);stroke-width:2;stroke-linecap:round;stroke-dasharray:100}
.halo{fill:var(--ed)}.rip{fill:none;stroke:var(--ed);stroke-width:1.5}
@keyframes bob{50%{transform:translateY(-3px)}}.bob{animation:bob 5s ease-in-out infinite}""")

for i, x in enumerate(XS):
    s, e = i * STEP, (i + 1) * STEP
    a = f"{CYCLE}s linear infinite"
    css += [
        kf(f"k{i}", "color:var(--mu)", "color:var(--ac)", s, e),
        kf(f"h{i}", "opacity:0", "opacity:var(--glow)", s, e),
        kf(f"l{i}", "transform:translateY(0)", "transform:translateY(-5px)", s, e, 3),
        # progress ring draws itself around the active tile, then fades as the spark leaves
        f"@keyframes r{i}{{0%,{s:g}%{{stroke-dashoffset:100;opacity:0}}{s + .5:g}%{{stroke-dashoffset:100;opacity:.9}}"
        f"{e - 4:g}%{{stroke-dashoffset:0;opacity:.9}}{e:g}%,100%{{stroke-dashoffset:0;opacity:0}}}}",
        f"@keyframes p{i}{{0%,{s:g}%{{transform:scale(1);opacity:0}}{s + .3:g}%{{transform:scale(1);opacity:.7}}"
        f"{s + 7:g}%{{transform:scale(1.45);opacity:0}}{s + 7.1:g}%,100%{{opacity:0}}}}",
        f".k{i}{{animation:k{i} {a}}}.h{i}{{animation:h{i} {a}}}.l{i}{{animation:l{i} {a}}}"
        f".r{i}{{animation:r{i} {a}}}.p{i}{{transform-box:fill-box;transform-origin:center;animation:p{i} {a}}}"
        f".b{i}{{animation-delay:-{i * .9:g}s}}",
    ]
    r = H - 2
    body.append(
        f'<g transform="translate({x} {CY})"><g class="bob b{i}"><g class="l{i}">'
        f'<circle class="halo h{i}" r="40" filter="url(#bl)"/>'
        f'<rect class="rip p{i}" x="-{H}" y="-{H}" width="{2 * H}" height="{2 * H}" rx="26"/>'
        f'<rect class="glass" x="-{H}" y="-{H}" width="{2 * H}" height="{2 * H}" rx="26"/>'
        f'<path d="M-{H - 18} -{H - .8}H{H - 18}" stroke="#FFFFFF" stroke-opacity=".22" stroke-linecap="round"/>'
        f'<rect class="ring r{i}" x="-{r}" y="-{r}" width="{2 * r}" height="{2 * r}" rx="24" pathLength="100"/>'
        f'<g class="k{i}"><g class="ic" transform="translate(-28.8 -28.8) scale(.9)">{ICONS[i]}</g></g>'
        f'</g></g></g>')

# Rails, lit rails and travelling sparks: step i's spark leaves in its last 40% and lands as i+1 lights up.
rails, sparks = [], []
gap = H + 12
for i in range(N):
    s, e = i * STEP, (i + 1) * STEP
    t0, t1 = (e - STEP * .4) / 100, e / 100
    if i < N - 1:
        d = f"M{XS[i] + gap} {CY}H{XS[i + 1] - gap}"
        L = XS[i + 1] - XS[i] - 2 * gap
        rails.append(f'<path class="rail" d="{d}"/>')
        rails.append(
            f'<path class="lit" d="{d}" stroke-dasharray="{L}" stroke-dashoffset="{L}">'
            f'<animate attributeName="stroke-dashoffset" dur="{CYCLE}s" repeatCount="indefinite" '
            f'keyTimes="0;{t0:.3f};{t1:.3f};.97;1" values="{L};{L};0;0;{L}"/>'
            f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
            f'keyTimes="0;{t0:.3f};.9;.98;1" values="0;.55;.55;0;0"/></path>')
    else:  # learn -> idea: close the loop underneath
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
<linearGradient id="gf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" class="s0"/><stop offset=".5" class="s1"/><stop offset="1" class="s2"/></linearGradient>
<linearGradient id="ge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" class="e0"/><stop offset=".5" class="e1"/><stop offset="1" class="e2"/></linearGradient>
<radialGradient id="rg"><stop offset="0" class="ac" stop-opacity=".7"/><stop offset="1" class="ac" stop-opacity="0"/></radialGradient></defs>
{"".join(rails)}{"".join(body)}{"".join(sparks)}
</svg>
'''
Path(__file__).resolve().parents[1].joinpath("assets/toolkit.svg").write_text(svg, encoding="utf-8", newline="\n")
print("wrote assets/toolkit.svg", len(svg), "bytes")
