"""Banner animado do README: o ceu do PlanetarySystem (nebulosas, galaxia, buraco negro,
cinturao, 7 planetas, cometas, dobra/warp com salto de entrada) + marca vetorial."""
import base64, math, random
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

W, H = 1280, 480
CX, CY = 640, 240
R = random.Random(7)
OUT = "../../docs/assets/banner.svg"
UNB = "fonts/Unbounded.ttf"
MAN = "fonts/Manrope.ttf"

defs, css, body = [], [], []
f = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")


# ---------- texto -> caminhos vetoriais ----------
_faces = {}
def _font(path, wght):
    if path not in _faces:
        _faces[path] = hb.Face(hb.Blob.from_file_path(path))
    font = hb.Font(_faces[path])
    font.set_variations({"wght": wght})
    return font

def shape(path, text, wght, size, track=0.0):
    font = _font(path, wght)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    s = size / _faces[path].upem
    glyphs, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append((info.codepoint, x + pos.x_offset * s, pos.y_offset * s))
        x += pos.x_advance * s + track * size
    return font, s, glyphs, x - track * size

def text_d(path, text, wght, size, x0, base, track=0.0):
    font, s, glyphs, width = shape(path, text, wght, size, track)
    pen = SVGPathPen(None, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
    boxes = []
    for gid, gx, gy in glyphs:
        font.draw_glyph_with_pen(gid, TransformPen(pen, (s, 0, 0, -s, x0 + gx, base - gy)))
        e = font.get_glyph_extents(gid)
        boxes.append((x0 + gx + e.x_bearing * s, base - e.y_bearing * s, e.width * s, -e.height * s))
    return pen.getCommands(), width, boxes

def width_of(path, text, wght, size, track=0.0):
    return shape(path, text, wght, size, track)[3]


# ---------- utilidades ----------
def rgba(c, a=None):
    return c if a is None else f"rgba({c[0]},{c[1]},{c[2]},{a})"

def radial(id_, stops, cx=".5", cy=".5", r=".5", fx=None, fy=None):
    fxy = f' fx="{fx}" fy="{fy}"' if fx else ""
    st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    defs.append(f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}"{fxy}>{st}</radialGradient>')

def orbit_keyframes(name, rx, ry):
    # elipse via dois eixos senoidais (cubic-bezier = easeInOutSine), sem SMIL
    css.append(f"@keyframes {name}x{{from{{transform:translateX({f(rx)}px)}}to{{transform:translateX({f(-rx)}px)}}}}"
               f"@keyframes {name}y{{from{{transform:translateY({f(-ry)}px)}}to{{transform:translateY({f(ry)}px)}}}}")

def orbit(name, T, phase, inner, delay=0.0):
    """Envolve `inner` num movimento eliptico de periodo T (s); phase em [0,1)."""
    t0 = -phase * T + delay
    sx = f"animation:{name}x {f(T/2)}s {f(t0)}s infinite alternate var(--sen) both"
    sy = f"animation:{name}y {f(T/2)}s {f(t0 - T/4)}s infinite alternate var(--sen) both"
    return f'<g style="{sx}"><g style="{sy}">{inner}</g></g>'


# ---------- CSS base ----------
css.append(""":root{--sen:cubic-bezier(.37,0,.63,1)}
@keyframes pisca{0%,100%{opacity:var(--lo,.1)}50%{opacity:var(--hi,.82)}}
@keyframes deriva{to{transform:translateX(-1280px)}}
@keyframes gira{to{transform:rotate(360deg)}}
@keyframes vv{0%{transform:scaleX(1);opacity:0}18%{opacity:var(--a,.3)}100%{transform:scaleX(9);opacity:0}}
@keyframes vs{0%{transform:scaleX(1);opacity:0}25%{opacity:.85}100%{transform:scaleX(14);opacity:0}}
@keyframes surto{0%{opacity:0}2%{opacity:1}9%{opacity:1}14%{opacity:0}100%{opacity:0}}
@keyframes avanco{0%{transform:scale(1.07)}12%{transform:scale(1)}100%{transform:scale(1)}}
@keyframes clarao{0%,4%{opacity:0}8%{opacity:.5}16%{opacity:0}100%{opacity:0}}
@keyframes cometa{0%{transform:translateX(0);opacity:0}2%{opacity:1}16%{opacity:.9}20%{transform:translateX(var(--L));opacity:0}100%{transform:translateX(var(--L));opacity:0}}
@keyframes revela{from{transform:translateX(-1150px)}to{transform:none}}
@keyframes sobe{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes surge{from{opacity:0}to{opacity:1}}
@keyframes traca{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}
@keyframes brilho{0%,62%{transform:translateX(-520px)}100%{transform:translateX(900px)}}
@keyframes pulso{0%,100%{opacity:.75}50%{opacity:1}}
@keyframes onda{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}
@keyframes faixa{from{transform:translateX(-1.5px)}to{transform:translateX(1.5px)}}
.tw{animation:pisca 4s ease-in-out infinite both}
.surto{animation:surto 24s cubic-bezier(.2,.7,.3,1) infinite both;opacity:0}
.cena{transform-origin:640px 240px;animation:avanco 24s cubic-bezier(.16,1,.3,1) infinite both}
.clarao{animation:clarao 24s ease-out infinite both;opacity:0}
.marca{animation:sobe 1.4s 1s cubic-bezier(.16,1,.3,1) backwards}
.varre{animation:revela 1.6s .9s cubic-bezier(.65,0,.35,1) backwards}
.traco{stroke-dasharray:var(--len);animation:traca 1.5s 1.8s cubic-bezier(.65,0,.35,1) backwards}
.sat{animation:surge .8s 3.1s ease-out backwards}
.l1{animation:sobe 1s 2.2s cubic-bezier(.16,1,.3,1) backwards}
.l2{animation:sobe 1s 2.55s cubic-bezier(.16,1,.3,1) backwards}
.reflexo{animation:brilho 9s 3.6s cubic-bezier(.45,0,.2,1) infinite backwards}
.vivo{animation:pulso 2.4s ease-in-out infinite}
.onda{transform-box:fill-box;transform-origin:center;animation:onda 2.4s ease-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.surto,.clarao{opacity:0}}""")


# ---------- 1. nebulosa (raster) ----------
body.append(f'<rect width="{W}" height="{H}" fill="#06040d"/>')
body.append("@@NEBULA@@")

STAR = ["#FFFFFF", "#B4FFFA", "#FFF46E", "#E081FF", "#F89EFF", "#4FC3F7"]

# ---------- 3. estrelas em parallax (2 camadas em laco continuo) ----------
def star_layer(n, rmin, rmax, dur, twinkle_frac, spikes=0):
    items = []
    for i in range(n):
        x, y = R.uniform(0, W), R.uniform(0, H)
        r = R.uniform(rmin, rmax)
        c = STAR[0] if R.random() < .55 else R.choice(STAR)
        if R.random() < twinkle_frac:
            d, dl = R.uniform(2.2, 6.5), R.uniform(0, 6)
            items.append(f'<circle class="tw" cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c}" style="animation-duration:{f(d)}s;animation-delay:-{f(dl)}s"/>')
        else:
            items.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c}" opacity="{f(R.uniform(.2,.75))}"/>')
    for i in range(spikes):
        x, y = R.uniform(40, W - 40), R.uniform(20, H - 20)
        if 300 < x < 980 and 150 < y < 360:
            continue
        c = R.choice(["#FFFFFF", "#B4FFFA", "#E081FF"])
        L = R.uniform(7, 13)
        d, dl = R.uniform(3, 6), R.uniform(0, 6)
        items.append(f'<g class="tw" style="--lo:.25;--hi:1;animation-duration:{f(d)}s;animation-delay:-{f(dl)}s" transform="translate({f(x)} {f(y)})">'
                     f'<circle r="3.2" fill="url(#g-estrela)"/>'
                     f'<path d="M-{f(L)} 0H{f(L)}M0-{f(L)}V{f(L)}" stroke="{c}" stroke-width=".7" opacity=".7"/>'
                     f'<circle r="1.2" fill="#fff"/></g>')
    layer = "".join(items)
    return (f'<g style="animation:deriva {dur}s linear infinite">{layer}'
            f'<g transform="translate({W} 0)">{layer}</g></g>')

radial("g-estrela", [(0, "#FFFFFF", .9), (.4, "#B4FFFA", .25), (1, "#B4FFFA", 0)])
body.append(star_layer(46, .6, 1.5, 120, .6, spikes=14))


# ---------- 4. dobra: campo de riscos (constante + salto na entrada) ----------
def streaks(n, color_fn, anim, dmin, dmax, wmin, wmax, a_rng=None):
    out = []
    for _ in range(n):
        th = R.uniform(0, 360)
        r0 = R.uniform(14, 110)
        ln = r0 * R.uniform(.05, .12)
        d = R.uniform(dmin, dmax)
        extra = f";--a:{f(R.uniform(*a_rng))}" if a_rng else ""
        out.append(f'<g transform="rotate({f(th)})"><line x1="{f(r0)}" x2="{f(r0+ln)}" stroke="{color_fn()}" stroke-width="{f(R.uniform(wmin,wmax))}" '
                   f'style="animation:{anim} {f(d)}s {f(-R.uniform(0,d))}s cubic-bezier(.55,0,1,.45) infinite both{extra}"/></g>')
    return "".join(out)

def azul():
    z = R.random()
    return f"rgb({int(100+(1-z)*80)},{int(180+(1-z)*60)},255)"

body.append(f'<g transform="translate({CX} {CY})">'
            + streaks(42, lambda: "#E8E4FF", "vv", 6, 13, .5, 1.1, (.12, .4))
            + f'<g class="surto">{streaks(76, azul, "vs", .7, 1.5, .6, 1.6)}</g></g>')
radial("g-clarao", [(0, "#DDF6FF", .9), (.3, "#7FD8FF", .35), (1, "#4FC3F7", 0)])
body.append(f'<ellipse class="clarao" cx="{CX}" cy="{CY}" rx="520" ry="260" fill="url(#g-clarao)"/>')


# ---------- 5. cena (avanco da camera sincronizado com o salto) ----------
cena = []

# buraco negro (w*.08, h*.82) -> (102, 400)
BX, BY, BR = 102, 400, 18
radial("g-bn-lente", [(0, "#000000", .95), (.55, "#000000", .7), (1, "#000000", 0)])
radial("g-bn-disco", [(0, "#FF8C00", 0), (.24, "#FF8C00", 0), (.3, "#FFB040", .42), (.55, "#FF8C00", .26), (.8, "#FF4600", .12), (1, "#FF4600", 0)])
radial("g-bn-anel", [(0, "#FFB432", 0), (.5, "#FFB432", 0), (.7, "#FFB432", .3), (1, "#FFB432", 0)])
defs.append('<filter id="f-suave" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6"/></filter>')
defs.append('<filter id="f-halo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>')
defs.append(f'<clipPath id="c-frente"><rect x="-90" y="0" width="180" height="90"/></clipPath>')

def arcos():
    grupos = []
    for per, rlo, rhi, n in ((5, 1.25, 2.0, 6), (9, 1.9, 2.9, 6), (15, 2.7, 3.8, 6)):
        arcs = []
        for _ in range(n):
            rr = BR * R.uniform(rlo, rhi)
            a0 = R.uniform(0, 6.283); span = R.uniform(.8, 2.6)
            x0, y0 = math.cos(a0) * rr, math.sin(a0) * rr
            x1, y1 = math.cos(a0 + span) * rr, math.sin(a0 + span) * rr
            col = R.choice(["#FFC060", "#FF9A20", "#FF7A10", "#FFD890"])
            arcs.append(f'<path d="M{f(x0)} {f(y0)}A{f(rr)} {f(rr)} 0 0 1 {f(x1)} {f(y1)}" fill="none" stroke="{col}" '
                        f'stroke-width="{f(R.uniform(1.2,3.2))}" stroke-linecap="round" opacity="{f(R.uniform(.25,.7))}"/>')
        grupos.append(f'<g style="animation:gira {per}s linear infinite">{"".join(arcs)}</g>')
    return "".join(grupos)

disco = f'<circle r="{BR*3.8}" fill="url(#g-bn-disco)"/>' + arcos()
cena.append(f'<g transform="translate({BX} {BY})">'
            f'<circle r="{BR*2.6}" fill="url(#g-bn-lente)"/>'
            f'<g class="vivo" style="animation-duration:5.2s"><circle r="{BR*1.7}" fill="url(#g-bn-anel)"/></g>'
            f'<g transform="rotate(-10)">'
            f'<path d="M-{BR*1.5} 0A{BR*1.5} {BR*1.38} 0 0 1 {BR*1.5} 0" fill="none" stroke="#FFB850" stroke-width="6" opacity=".16"/>'
            f'<path d="M-{BR*1.5} 0A{BR*1.5} {BR*1.38} 0 0 1 {BR*1.5} 0" fill="none" stroke="#FFC870" stroke-width="2" opacity=".5"/>'
            f'<g transform="scale(1 .28)">{disco}</g>'
            f'<circle r="{BR}" fill="#000"/>'
            f'<circle r="{BR+1}" fill="none" stroke="#FFD8A0" stroke-width=".8" opacity=".6"/>'
            f'<g clip-path="url(#c-frente)"><g transform="scale(1 .28)">{disco}</g></g>'
            f'</g></g>')

# cinturao de asteroides (w*.15, h*.5) rx w*.12 ry h*.06
orbit_keyframes("cint", 154, 29)
ast = []
for i in range(28):
    jx, jy = R.uniform(-9, 9), R.uniform(-4, 4)
    r = R.uniform(.6, 1.7)
    pts = " ".join(f"{f(math.cos(k*1.2566+R.uniform(-.3,.3))*r*R.uniform(.7,1.3))},{f(math.sin(k*1.2566)*r*R.uniform(.7,1.3))}" for k in range(5))
    inner = f'<polygon points="{pts}" fill="rgb(180,160,140)" opacity="{f(R.uniform(.12,.45))}"/>'
    ast.append(f'<g transform="translate({f(192+jx)} {f(240+jy)})">{orbit("cint", 150, i/28 + R.uniform(0,.02), inner)}</g>')
cena.append("".join(ast))

# planetas (ancora, rx, ry, periodo, raio, anel, centro, realce, sombra, glow)
PL = [
    ("p1", .14, .5, 65, 22, 25, 28, .35, "#2D1B69", (147, 112, 219, .85), "#0A0015", (88, 28, 135, .35)),
    ("p2", .85, .42, 45, 15, 18, 20, None, "#0D2137", (79, 195, 247, .65), "#020810", (14, 116, 144, .3)),
    ("p3", .52, .1, 30, 10, 35, 11, None, "#3D1010", (200, 80, 50, .6), "#100505", (150, 40, 20, .2)),
    ("p4", .77, .78, 25, 8, 22, 8, None, "#0A1F35", (150, 230, 255, .7), "#020810", (100, 200, 240, .2)),
    ("p5", .22, .18, 35, 12, 30, 15, None, "#3D2800", (255, 183, 3, .65), "#1A1000", (200, 140, 0, .25)),
    ("p6", .93, .64, 18, 7, 40, 10, None, "#0A2010", (80, 200, 100, .6), "#020A05", (40, 150, 60, .2)),
    ("p7", .5, .89, 55, 10, 45, 22, -.25, "#1A0D35", (120, 80, 220, .7), "#08040F", (70, 30, 150, .3)),
]
SC = 1.12
for nome, ax, ay, rx, ry, T, rad, anel, c0, hi, sh, gl in PL:
    r = rad * SC
    radial(f"g-{nome}-glow", [(0, rgba(gl[:3]), gl[3]), (.4, rgba(gl[:3]), gl[3]), (1, rgba(gl[:3]), 0)])
    radial(f"g-{nome}-corpo", [(0, rgba(hi[:3]), hi[3]), (.45, c0, 1), (1, sh, 1)], cx=".5", cy=".5", r=".62", fx=".33", fy=".3")
    radial(f"g-{nome}-borda", [(0, "#000", 0), (.78, "#000", 0), (1, rgba(hi[:3]), .35)], cx=".5", cy=".5", r=".5", fx=".42", fy=".38")
    defs.append(f'<clipPath id="c-{nome}"><circle r="{f(r)}"/></clipPath>')
    faixas = "".join(
        f'<ellipse cy="{f(r*k)}" rx="{f(r*1.2)}" ry="{f(r*.07)}" fill="#fff" opacity=".055" '
        f'style="animation:faixa {f(R.uniform(3,6))}s {f(-R.uniform(0,6))}s ease-in-out infinite alternate"/>'
        for k in (-.38, -.05, .3))
    corpo = (f'<circle r="{f(r*2)}" fill="url(#g-{nome}-glow)"/>'
             f'<circle r="{f(r)}" fill="url(#g-{nome}-corpo)"/>'
             f'<g clip-path="url(#c-{nome})">{faixas}</g>'
             f'<circle r="{f(r)}" fill="url(#g-{nome}-borda)"/>')
    if anel is not None:
        ar, w = r * 1.8, r * .4
        tras = f'M{f(-ar)} 0A{f(ar)} {f(ar*.22)} 0 0 1 {f(ar)} 0'
        frente = f'M{f(ar)} 0A{f(ar)} {f(ar*.22)} 0 0 1 {f(-ar)} 0'
        anel_s = lambda d, op: (f'<path d="{d}" fill="none" stroke="rgb(180,150,255)" stroke-width="{f(w)}" opacity="{op}"/>'
                                f'<path d="{d}" fill="none" stroke="rgb(220,205,255)" stroke-width="{f(w*.18)}" opacity="{op*1.6}" transform="scale(.92)"/>')
        corpo = (f'<g transform="rotate({f(math.degrees(anel))})">{anel_s(tras, .13)}</g>' + corpo +
                 f'<g transform="rotate({f(math.degrees(anel))})">{anel_s(frente, .28)}</g>')
    orbit_keyframes(nome, rx, ry)
    cena.append(f'<g transform="translate({f(ax*W)} {f(ay*H)})">{orbit(nome, T, R.random(), corpo)}</g>')

body.append(f'<g class="cena">{"".join(cena)}</g>')


# ---------- 6. cometas ----------
defs.append('<linearGradient id="g-cauda" x1="0" x2="1"><stop offset="0" stop-color="#9FE6FF" stop-opacity="0"/>'
            '<stop offset=".75" stop-color="#CFF3FF" stop-opacity=".35"/><stop offset="1" stop-color="#FFFFFF" stop-opacity=".95"/></linearGradient>')
radial("g-cabeca", [(0, "#FFFFFF", 1), (.25, "#BDEFFF", .6), (1, "#4FC3F7", 0)])
def cometa(x0, y0, ang, L, T, delay, esc=1.0):
    cauda = f'M0 -1.4 L-{170*esc} -.2 L-{170*esc} .2 L0 1.4 Z'
    halo = f'M0 -4 L-{90*esc} -.5 L-{90*esc} .5 L0 4 Z'
    fag = "".join(f'<circle cx="{f(-R.uniform(10,120)*esc)}" cy="{f(R.uniform(-3,3))}" r="{f(R.uniform(.4,.9))}" fill="#DDF6FF" opacity="{f(R.uniform(.3,.8))}"/>' for _ in range(7))
    return (f'<g transform="translate({x0} {y0}) rotate({ang})"><g style="--L:{L}px;animation:cometa {T}s {delay}s linear infinite both">'
            f'<path d="{halo}" fill="url(#g-cauda)" opacity=".22"/>'
            f'<path d="{cauda}" fill="url(#g-cauda)"/>{fag}'
            f'<circle r="{9*esc}" fill="url(#g-cabeca)"/><circle r="{1.6*esc}" fill="#fff"/></g></g>')
body.append(cometa(-60, 40, 17, 980, 14, 3.5))
body.append(cometa(1340, 70, 158, 760, 23, 9, .8))
body.append(cometa(420, -40, 62, 420, 31, 18, .65))


# ---------- 7. marca ----------
# veu de contraste atras do texto
radial("g-veu", [(0, "#05030B", .78), (.55, "#05030B", .55), (1, "#05030B", 0)])
body.append(f'<ellipse cx="{CX}" cy="262" rx="470" ry="150" fill="url(#g-veu)"/>')

SIZE = 104
w_my = width_of(UNB, "My", 300, SIZE, -.01)
w_orb = width_of(UNB, "Orbita", 700, SIZE, -.015)
gap = SIZE * .06
x0 = CX - (w_my + gap + w_orb) / 2
BASE = 246
d_my, _, _ = text_d(UNB, "My", 300, SIZE, x0, BASE, -.01)
d_orb, _, bx = text_d(UNB, "Orbita", 700, SIZE, x0 + w_my + gap, BASE, -.015)
ox, oy, ow, oh = bx[0]
OCX, OCY, OR = ox + ow / 2, oy + oh / 2, oh / 2

# brilho atras do emblema e da palavra (camada desfocada, nao text-shadow)
radial("g-emblema", [(0, "#4FC3F7", .55), (.45, "#7B5CFF", .22), (1, "#7B5CFF", 0)])
body.append(f'<g class="marca"><ellipse cx="{f(OCX)}" cy="{f(OCY)}" rx="{f(OR*3.2)}" ry="{f(OR*2.2)}" fill="url(#g-emblema)" class="vivo" style="animation-duration:6s"/>'
            f'</g>')

# anel orbital do "O": metade de tras atras das letras, metade da frente por cima
ARX, ARY, AROT = OR * 1.62, OR * .42, -16
def meia(sweep_from_left):
    if sweep_from_left:
        return f"M{f(-ARX)} 0A{f(ARX)} {f(ARY)} 0 0 1 {f(ARX)} 0"
    return f"M{f(ARX)} 0A{f(ARX)} {f(ARY)} 0 0 1 {f(-ARX)} 0"
hlen = math.pi * (3 * (ARX + ARY) - math.sqrt((3 * ARX + ARY) * (ARX + 3 * ARY))) / 2 + 2
defs.append(f'<linearGradient id="g-anel" gradientUnits="userSpaceOnUse" x1="{f(-ARX)}" x2="{f(ARX)}">'
            f'<stop offset="0" stop-color="#7B5CFF" stop-opacity=".15"/><stop offset=".5" stop-color="#B4FFFA" stop-opacity=".95"/>'
            f'<stop offset="1" stop-color="#4FC3F7" stop-opacity=".25"/></linearGradient>')
anel_tr = f'<g transform="translate({f(OCX)} {f(OCY)}) rotate({AROT})">'
body.append(anel_tr + f'<path class="traco" style="--len:{f(hlen)}" d="{meia(True)}" fill="none" stroke="url(#g-anel)" stroke-width="1.6" opacity=".55"/></g>')

# letras, com revelacao por mascara e reflexo periodico
defs.append('<linearGradient id="g-varre" gradientUnits="userSpaceOnUse" x1="1080" x2="1320">'
            '<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>')
defs.append(f'<mask id="m-revela" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<rect class="varre" x="-1400" y="0" width="2800" height="{H}" fill="url(#g-varre)"/></mask>')
defs.append(f'<clipPath id="c-letras"><path d="{d_my}{d_orb}"/></clipPath>')
defs.append('<linearGradient id="g-reflexo" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
body.append(f'<g mask="url(#m-revela)"><g class="marca">'
            f'<path d="{d_my}" fill="#C9C1E8"/><path d="{d_orb}" fill="#F4F1FF"/>'
            f'<g clip-path="url(#c-letras)"><rect class="reflexo" x="{f(x0)}" y="140" width="120" height="160" fill="url(#g-reflexo)" transform="skewX(-18)"/></g>'
            f'</g></g>')

# metade da frente + satelite com troca de profundidade
T_SAT, D_SAT = 7.0, 3.1
orbit_keyframes("sat", ARX, ARY)
css.append("@keyframes sfrente{0%{opacity:1}50%{opacity:0}100%{opacity:0}}@keyframes stras{0%{opacity:0}50%{opacity:1}100%{opacity:1}}")
radial("g-sat", [(0, "#FFFFFF", 1), (.3, "#B4FFFA", .7), (1, "#4FC3F7", 0)])
def satelite(kf):
    dot = f'<g style="animation:{kf} {T_SAT}s {D_SAT}s step-end infinite both"><circle r="9" fill="url(#g-sat)"/><circle r="2.6" fill="#F2FEFF"/></g>'
    return orbit("sat", T_SAT, 0, dot, D_SAT)
# a fase 0 parte de (+rx, 0) indo para y>0 (frente) durante a primeira metade
body.insert(len(body) - 1, anel_tr + f'<g class="sat">{satelite("stras")}</g></g>')
body.append(anel_tr + f'<path class="traco" style="--len:{f(hlen)}" d="{meia(False)}" fill="none" stroke="url(#g-anel)" stroke-width="2.2"/>'
            f'<g class="sat">{satelite("sfrente")}</g></g>')

# linha de apoio e linha de estado
TAG = "Vagas de tecnologia e direito do Gupy e do LinkedIn, reunidas todos os dias"
tw = width_of(MAN, TAG, 500, 19.5)
d_tag, _, _ = text_d(MAN, TAG, 500, 19.5, CX - tw / 2, 306)
body.append(f'<path class="l1" d="{d_tag}" fill="#D4CDEA"/>')

ST = "4 ROTINAS AUTOMÁTICAS POR DIA  ·  GITHUB ACTIONS  ·  FIREBASE"
sw = width_of(MAN, ST, 650, 12.5, .16)
sx = CX - sw / 2 + 10
d_st, _, _ = text_d(MAN, ST, 650, 12.5, sx, 346, .16)
body.append(f'<g class="l2"><circle cx="{f(sx-16)}" cy="341.6" r="3.4" fill="#5BE49B"/>'
            f'<circle class="onda" cx="{f(sx-16)}" cy="341.6" r="3.4" fill="none" stroke="#5BE49B" stroke-width="1"/>'
            f'<path d="{d_st}" fill="#9F96C2"/></g>')

# vinheta final nas bordas
radial("g-vinheta", [(0, "#000", 0), (.7, "#000", 0), (1, "#000", .55)], r=".75")
body.append(f'<rect width="{W}" height="{H}" fill="url(#g-vinheta)" pointer-events="none"/>')

# ---------- raster: nebula + galaxy + wordmark glow ----------
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
base = np.asarray(Image.open("nebula_preview.png").convert("RGB"), np.float32)
SSG = 3
lay = Image.new("RGB", (W * SSG, H * SSG)); dr = ImageDraw.Draw(lay)
gx, gy, rot, sq = 1126, 54, math.radians(-22), .38
def pg(px, py, r, col, a):
    X = (px * math.cos(rot) - py * sq * math.sin(rot) + gx) * SSG
    Y = (px * math.sin(rot) + py * sq * math.cos(rot) + gy) * SSG
    rr = r * SSG
    dr.ellipse((X - rr, Y - rr, X + rr, Y + rr), fill=tuple(int(c * a) for c in col))
RG = random.Random(3)
for arm in range(2):
    for i in range(170):
        t = i / 170; th = arm * math.pi + t * 3 * math.pi + RG.uniform(-.2, .2); rr = t * 96 + RG.uniform(-4, 4)
        pg(math.cos(th) * rr, math.sin(th) * rr, RG.uniform(.6, 1.5), (210, 195, 255), (1 - t) * .55 * RG.uniform(.4, 1))
for _ in range(160):
    th, rr = RG.uniform(0, 6.283), abs(RG.gauss(0, 30))
    pg(math.cos(th) * rr, math.sin(th) * rr, RG.uniform(.5, 1.1), (235, 225, 255), RG.uniform(.1, .45))
gal = np.asarray(lay.resize((W, H), Image.LANCZOS), np.float32)
yy, xx = np.mgrid[0:H, 0:W]
u = ((xx - gx) * math.cos(rot) + (yy - gy) * math.sin(rot)); v = (-(xx - gx) * math.sin(rot) + (yy - gy) * math.cos(rot)) / sq
nuc = np.exp(-(u * u + v * v) / (2 * 16 ** 2))
gal += nuc[..., None] * np.array([255, 235, 200]) * .55 + np.exp(-(u*u+v*v)/(2*45**2))[..., None] * np.array([150, 130, 230]) * .18
# glow of the name: blurred layer of the letters themselves
m = Image.new("L", (W, H)); dm = ImageDraw.Draw(m)
fm = ImageFont.truetype(UNB, SIZE); fm.set_variation_by_axes([300])
fo = ImageFont.truetype(UNB, SIZE); fo.set_variation_by_axes([700])
dm.text((x0, BASE), "My", font=fm, fill=200, anchor="ls")
dm.text((x0 + w_my + gap, BASE), "Orbita", font=fo, fill=255, anchor="ls")
g1 = np.asarray(m.filter(ImageFilter.GaussianBlur(18)), np.float32) / 255
g2 = np.asarray(m.filter(ImageFilter.GaussianBlur(48)), np.float32) / 255
glow = g1[..., None] * np.array([143, 116, 255]) * .75 + g2[..., None] * np.array([79, 150, 247]) * .55
out = Image.fromarray(np.clip(base + gal + glow, 0, 255).astype(np.uint8))
import io; bio = io.BytesIO(); out.save(bio, "WEBP", quality=84, method=6); out.save("banner_raster.png")
neb = base64.b64encode(bio.getvalue()).decode()
body[body.index("@@NEBULA@@")] = f'<image href="data:image/webp;base64,{neb}" width="{W}" height="{H}" preserveAspectRatio="none"/>'

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="MyOrbita: vagas de tecnologia e direito do Gupy e do LinkedIn">'
       f'<title>MyOrbita</title><style>{"".join(css)}</style><defs>{"".join(defs)}</defs>{"".join(body)}</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print(len(svg.encode()), "bytes; O:", round(OCX), round(OCY), round(OR))
