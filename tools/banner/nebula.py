"""Textura de fundo do banner: nebulosas do PlanetarySystem com ruido fractal + poeira estelar."""
import numpy as np
from PIL import Image

W, H = 1280, 480
SS = 2  # supersampling
w, h = W * SS, H * SS
rng = np.random.default_rng(42)

yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) / SS


def fbm(octaves=6, base=3, persist=0.55, seed=0):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gx, gy = base * 2 ** o + 1, int(base * 2 ** o * H / W) + 2
        g = r.random((gy, gx)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += amp * (np.asarray(im, np.float32) / 255)
        tot += amp
        amp *= persist
    return acc / tot


def elipse(cx, cy, rx, ry, ang=0.0, p=2.0):
    c, s = np.cos(ang), np.sin(ang)
    dx, dy = xx - cx, yy - cy
    u = (dx * c + dy * s) / rx
    v = (-dx * s + dy * c) / ry
    return np.exp(-((u * u + v * v) ** (p / 2)) * 2.2)


# distorcao de dominio: desloca a amostragem por outro ruido -> filamentos de gas
wx = (fbm(seed=11, base=4) - 0.5) * 2
wy = (fbm(seed=12, base=4) - 0.5) * 2
def warp(field, k):
    iy = np.clip((yy * SS + wy * k * SS).astype(np.int32), 0, h - 1)
    ix = np.clip((xx * SS + wx * k * SS).astype(np.int32), 0, w - 1)
    return field[iy, ix]
n1 = warp(fbm(seed=1, base=6, octaves=7, persist=0.58), 140)
n2 = warp(fbm(seed=2, base=8, octaves=7, persist=0.6), 90)
r3 = warp(fbm(seed=3, base=7, octaves=6, persist=0.55), 120)
ridge = (1 - np.abs(r3 * 2 - 1)) ** 6           # veios finos e brilhantes
textura = np.clip((n1 - 0.30) * 2.6, 0, 1) ** 1.6
filamento = np.clip((n2 - 0.42) * 3.2, 0, 1) ** 1.3 + ridge * 0.9
d = warp(fbm(seed=4, base=9, octaves=6), 60)
poeira = 1 - 0.75 * np.clip((d - 0.5) * 3.5, 0, 1)  # faixas escuras de poeira

img = np.zeros((h, w, 3), np.float32)
img[:] = np.array([6, 4, 13], np.float32)

def soma(mask, cor, k):
    global img
    img += mask[..., None] * np.array(cor, np.float32)[None, None, :] * k

# roxa (canto superior esquerdo) + realce lilas
m = elipse(64, 48, 470, 190, 0.2) * (0.25 + 0.95 * textura) * poeira
soma(m, (120, 40, 180), 0.75)
soma(elipse(64, 48, 470, 190, 0.2) * filamento * poeira, (170, 90, 255), 0.42)
soma(elipse(102, 34, 170, 70, -0.3) * (0.4 + 0.8 * filamento), (180, 100, 255), 0.30)
# ciano (canto superior direito) + nucleo
m = elipse(1178, 72, 330, 200, 0.6) * (0.25 + 0.95 * textura) * poeira
soma(m, (0, 160, 190), 0.7)
soma(elipse(1178, 72, 330, 200, 0.6) * filamento * poeira, (90, 220, 255), 0.4)
soma(elipse(1152, 86, 120, 80, 0.8) * (0.45 + 0.7 * filamento), (100, 220, 240), 0.28)
# laranja (base central) + ponto ambar
m = elipse(640, 470, 300, 150, 0.1) * (0.25 + 0.95 * textura) * poeira
soma(m, (200, 60, 20), 0.72)
soma(elipse(640, 470, 300, 150, 0.1) * filamento * poeira, (255, 120, 40), 0.38)
soma(elipse(653, 440, 110, 60, -0.2) * (0.5 + 0.6 * filamento), (255, 150, 0), 0.24)
# faixa difusa (via lactea) cruzando em diagonal
band = elipse(640, 240, 900, 120, -0.18, p=1.6) * (0.2 + 0.8 * textura) * poeira
soma(band, (70, 60, 140), 0.26)
soma(elipse(640, 240, 900, 120, -0.18, p=1.6) * ridge * poeira, (120, 110, 200), 0.18)

# vinheta suave
vig = elipse(640, 240, 980, 520, 0, p=2.0)
img *= (0.55 + 0.45 * vig)[..., None]

# poeira estelar
cores = np.array([(255, 255, 255), (180, 255, 250), (255, 244, 110), (224, 129, 255), (248, 158, 255), (79, 195, 247)], np.float32)
N = 3800
sx = rng.random(N) * w
sy = rng.random(N) * h
br = rng.pareto(2.4, N) * 0.22 + 0.06
br = np.clip(br, 0, 1.0)
ci = np.where(rng.random(N) < 0.72, 0, rng.integers(1, 6, N))
for x, y, b, c in zip(sx, sy, br, ci):
    xi, yi = int(x), int(y)
    col = cores[c] * 0.35 + 255 * 0.65 if c else cores[0]
    r = 1 if b < 0.5 else 2
    y0, y1, x0, x1 = max(yi - r, 0), min(yi + r + 1, h), max(xi - r, 0), min(xi + r + 1, w)
    gy, gx = np.mgrid[y0:y1, x0:x1]
    fall = np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / (0.9 if r == 1 else 1.6))
    img[y0:y1, x0:x1] += fall[..., None] * col[None, None, :] * b

img = np.clip(img, 0, 255)
out = Image.fromarray(img.astype(np.uint8)).resize((W, H), Image.LANCZOS)
# grao
g = rng.normal(0, 2.2, (H, W, 1))
out = Image.fromarray(np.clip(np.asarray(out, np.float32) + g, 0, 255).astype(np.uint8))
out.save("nebula.webp", "WEBP", quality=82, method=6)
out.save("nebula_preview.png")
import os
print(os.path.getsize("nebula.webp"))
