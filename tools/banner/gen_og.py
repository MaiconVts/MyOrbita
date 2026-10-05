"""Imagem Open Graph (1200x630) e apple-touch-icon (180x180) do MyOrbita.
Mesmo ceu do banner do README: nebulosas, estrelas, orbitas e a marca com o anel no O."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2  # supersampling
W, H = 1200, 630
CEU = (11, 7, 24)
TECH = (79, 195, 247)
ADV = (255, 183, 3)
TINTA = (242, 237, 227)
PUBLIC = "../../myorbita-web/public/"
R = random.Random(11)


def fonte(path, wght, size):
    f = ImageFont.truetype(path, size * S)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def mistura(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def nebulosa(img, cx, cy, rx, ry, cor, alfa):
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=cor + (alfa,))
    camada = camada.filter(ImageFilter.GaussianBlur(max(rx, ry) * S * 0.45))
    img.alpha_composite(camada)


def estrelas(img, n):
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = R.uniform(0, W) * S, R.uniform(0, H) * S
        r = R.choice([0.5, 0.6, 0.8, 1.0, 1.4]) * S
        a = R.randint(70, 230)
        cor = R.choice([TINTA, TINTA, TINTA, TECH, ADV])
        d.ellipse([x - r, y - r, x + r, y + r], fill=cor + (a,))


def anel(cx, cy, rx, ry, rot, t0, t1, passos=720):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = []
    for i in range(passos + 1):
        t = t0 + (t1 - t0) * i / passos
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append(((cx + x * c - y * s) * S, (cy + x * s + y * c) * S, i / passos))
    return pts


def traco(img, pts, largura, cor_de, alfa):
    d = ImageDraw.Draw(img)
    r = largura * S / 2
    for (x0, y0, t0), (x1, y1, _) in zip(pts, pts[1:]):
        d.line([x0, y0, x1, y1], fill=cor_de(t0) + (alfa,), width=int(largura * S))
        if largura > 2:
            d.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=cor_de(t0) + (alfa,))


def glow(img, desenhar, raio):
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    desenhar(camada)
    img.alpha_composite(camada.filter(ImageFilter.GaussianBlur(raio * S)))
    img.alpha_composite(camada)


def ceu(w, h):
    img = Image.new("RGBA", (w * S, h * S), CEU + (255,))
    return img


# ---------------- OG ----------------
img = ceu(W, H)
nebulosa(img, 960, 160, 420, 260, (58, 28, 110), 150)
nebulosa(img, 1080, 520, 300, 200, (20, 70, 120), 120)
nebulosa(img, 180, 600, 380, 180, (90, 40, 20), 70)
estrelas(img, 520)

# sistema orbital a direita
PX, PY = 930, 330
for i, (rx, ry, a) in enumerate([(170, 54, 70), (250, 80, 55), (335, 108, 40)]):
    pts = anel(PX, PY, rx, ry, -16, 0, 2 * math.pi)
    traco(img, pts, 1.3, lambda t: mistura(TECH, ADV, t), a)

def planeta(camada):
    d = ImageDraw.Draw(camada)
    for k in range(60, 0, -1):
        t = k / 60
        cor = mistura((255, 226, 160), (122, 52, 120), t ** 1.6)
        r = 62 * t
        ox, oy = -20 * (1 - t), -20 * (1 - t)
        d.ellipse([(PX + ox - r) * S, (PY + oy - r) * S, (PX + ox + r) * S, (PY + oy + r) * S], fill=cor + (255,))
glow(img, planeta, 26)

# satelites nos aneis
for rx, ry, ang, cor, r in [(170, 54, 0.6, TECH, 7), (250, 80, 2.4, ADV, 9), (335, 108, 5.4, TINTA, 5)]:
    x, y, _ = anel(PX, PY, rx, ry, -16, ang, ang, 1)[0]
    def sat(c, x=x, y=y, cor=cor, r=r):
        ImageDraw.Draw(c).ellipse([x - r * S, y - r * S, x + r * S, y + r * S], fill=cor + (255,))
    glow(img, sat, r * 1.6)

# cometa
cometa = Image.new("RGBA", img.size, (0, 0, 0, 0))
dc = ImageDraw.Draw(cometa)
for i in range(80):
    t = i / 80
    x, y = (560 + 260 * t) * S, (70 + 70 * t) * S
    dc.ellipse([x - 2 * t * S, y - 2 * t * S, x + 2 * t * S, y + 2 * t * S], fill=TINTA + (int(220 * t),))
img.alpha_composite(cometa.filter(ImageFilter.GaussianBlur(1.2 * S)))

# escurece a esquerda para o texto
veu = Image.new("L", (W * S, H * S))
arr = np.clip(1 - np.linspace(0, 1.4, W * S), 0, 1) ** 1.5 * 200
veu = Image.fromarray(np.tile(arr.astype(np.uint8), (H * S, 1)))
img.alpha_composite(Image.merge("RGBA", [Image.new("L", veu.size, c) for c in CEU] + [veu]))

# marca
UNB, MAN = "fonts/Unbounded.ttf", "fonts/Manrope.ttf"
fm = fonte(UNB, 800, 104)
x0, base = 72, 300
d = ImageDraw.Draw(img)
w_my = d.textlength("My", font=fm)
o_box = d.textbbox((0, 0), "O", font=fm)
ocx = (x0 * S + w_my + (o_box[0] + o_box[2]) / 2) / S
ocy = (base * S + (o_box[1] + o_box[3]) / 2 - fm.getmetrics()[0]) / S
o_r = (o_box[3] - o_box[1]) / 2 / S
ring = lambda t0, t1: anel(ocx, ocy, o_r * 1.62, o_r * 0.42, -16, t0, t1)
cor_anel = lambda t: mistura(TECH, ADV, t)
traco(img, ring(math.pi, 2 * math.pi), 4.2, lambda t: mistura(TECH, ADV, 1 - t), 150)
d = ImageDraw.Draw(img)
d.text((x0 * S, base * S), "My", font=fm, fill=TINTA, anchor="ls")
d.text((x0 * S + w_my, base * S), "Orbita", font=fm, fill=TINTA, anchor="ls")
glow(img, lambda c: traco(c, ring(0, math.pi), 4.2, lambda t: mistura(ADV, TECH, t), 255), 6)
sx, sy, _ = ring(0.9, 0.9)[0]
glow(img, lambda c: ImageDraw.Draw(c).ellipse([sx - 9 * S, sy - 9 * S, sx + 9 * S, sy + 9 * S], fill=ADV + (255,)), 12)
ImageDraw.Draw(img).ellipse([sx - 3.2 * S, sy - 3.2 * S, sx + 3.2 * S, sy + 3.2 * S], fill=(255, 255, 255, 255))

d = ImageDraw.Draw(img)
ft = fonte(MAN, 600, 34)
d.text((x0 * S, 372 * S), "Vagas remotas em tecnologia e direito,", font=ft, fill=TINTA + (235,))
d.text((x0 * S, 416 * S), "atualizadas todos os dias.", font=ft, fill=TINTA + (235,))
fs = fonte(MAN, 700, 21)
y = 520
x = x0
for rotulo, cor in [("Gupy", TECH), ("LinkedIn", ADV), ("Sem cadastro", TINTA)]:
    d.ellipse([(x) * S, (y - 5) * S, (x + 10) * S, (y + 5) * S], fill=cor + (255,))
    d.text(((x + 20) * S, y * S), rotulo, font=fs, fill=TINTA + (210,), anchor="lm")
    x += 20 + d.textlength(rotulo, font=fs) / S + 34
fu = fonte(MAN, 500, 19)
d.text((x0 * S, 572 * S), "my-orbita.vercel.app", font=fu, fill=TINTA + (150,), anchor="lm")

img.resize((W, H), Image.LANCZOS).convert("RGB").save(PUBLIC + "og-myorbita.png", optimize=True)

# ---------------- apple-touch-icon ----------------
T = 180
ic = ceu(T, T)
nebulosa(ic, 120, 50, 90, 70, (58, 28, 110), 140)
R.seed(3)
d = ImageDraw.Draw(ic)
for _ in range(40):
    x, y, r = R.uniform(0, T) * S, R.uniform(0, T) * S, R.choice([0.5, 0.8, 1.1]) * S
    d.ellipse([x - r, y - r, x + r, y + r], fill=TINTA + (R.randint(60, 180),))
c = T / 2
traco(ic, anel(c, c, 74, 19.4, -16, math.pi, 2 * math.pi), 7, lambda t: mistura(TECH, ADV, 1 - t), 150)
ImageDraw.Draw(ic).ellipse([(c - 38) * S, (c - 38) * S, (c + 38) * S, (c + 38) * S], outline=TINTA + (255,), width=int(14.5 * S))
glow(ic, lambda k: traco(k, anel(c, c, 74, 19.4, -16, 0, math.pi), 7, lambda t: mistura(ADV, TECH, t), 255), 5)
sx, sy, _ = anel(c, c, 74, 19.4, -16, 0.9, 0.9)[0]
glow(ic, lambda k: ImageDraw.Draw(k).ellipse([sx - 12 * S, sy - 12 * S, sx + 12 * S, sy + 12 * S], fill=ADV + (255,)), 10)
ImageDraw.Draw(ic).ellipse([sx - 4 * S, sy - 4 * S, sx + 4 * S, sy + 4 * S], fill=(255, 255, 255, 255))
ic.resize((T, T), Image.LANCZOS).convert("RGB").save(PUBLIC + "apple-touch-icon.png", optimize=True)
print("ok")
