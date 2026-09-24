# Ikon Kertas — selembar kertas beresudut lipat, dua baris tulisan, satu centang.
# Digambar 4x lalu dikecilkan (LANCZOS) supaya tepinya halus tanpa perlu SVG saat runtime.

import os
from PIL import Image, ImageDraw, ImageFilter

OUT = r"D:\Documents\Claude Cowork\Kertas\pwa"
SS = 4  # supersample

PINE_HI   = (14, 122, 90)     # kiri-atas, sedikit lebih terang
PINE_LO   = (7, 74, 53)       # kanan-bawah, lebih dalam
PAPER     = (248, 251, 249)
FOLD      = (206, 224, 214)
FOLD_EDGE = (176, 202, 189)
RULE      = (172, 205, 190)
INK       = (12, 107, 79)


def gradient(size):
    """Gradien diagonal halus. Dibuat kecil lalu diperbesar — cukup mulus,
    dan tidak butuh numpy."""
    g = Image.new("RGB", (48, 48))
    px = g.load()
    for y in range(48):
        for x in range(48):
            t = (x / 47 * 0.45 + y / 47 * 0.55)
            px[x, y] = tuple(round(PINE_HI[i] + (PINE_LO[i] - PINE_HI[i]) * t) for i in range(3))
    return g.resize((size, size), Image.BICUBIC)


def sheet_mask(size, cx, cy, w, h, r, ear):
    """Bentuk kertas: persegi membulat yang sudut kanan-atasnya dipotong miring.
    Dipakai sebagai mask supaya potongannya ikut mulus, bukan ditimpa warna."""
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=255)
    # buang segitiga di sudut kanan-atas
    d.polygon([(x2 - ear, y1 - 2), (x2 + 2, y1 - 2), (x2 + 2, y1 + ear)], fill=0)
    return m, (x1, y1, x2, y2)


def draw_icon(size, content=0.53, pad_shadow=True):
    S = size * SS
    img = gradient(S).convert("RGBA")

    cx = cy = S / 2
    w = S * content
    h = w * 1.22
    # Semua ukuran diikat ke lebar kertas, bukan ke kanvas. Kalau diikat ke
    # kanvas, versi maskable yang kertasnya lebih kecil akan punya sudut lipat
    # yang terlalu besar sampai memakan baris tulisan pertama.
    r = w * 0.085
    ear = w * 0.28

    mask, (x1, y1, x2, y2) = sheet_mask(S, cx, cy, w, h, r, ear)

    # bayangan lembut: bikin kertas terasa terangkat, bukan stiker tempel
    if pad_shadow:
        sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        sh.paste((4, 30, 22, 105), (0, 0, S, S), mask)
        sh = sh.filter(ImageFilter.GaussianBlur(S * 0.030))
        img.alpha_composite(sh, (0, int(S * 0.020)))

    # lembar kertas
    paper = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    paper.paste(PAPER + (255,), (0, 0, S, S), mask)
    img.alpha_composite(paper)

    d = ImageDraw.Draw(img)

    # sudut terlipat: segitiga bawah lipatan + garis tepinya
    d.polygon([(x2 - ear, y1), (x2, y1 + ear), (x2 - ear, y1 + ear)], fill=FOLD + (255,))
    d.line([(x2 - ear, y1), (x2 - ear, y1 + ear), (x2, y1 + ear)],
           fill=FOLD_EDGE + (255,), width=max(1, int(w * 0.010)))

    # dua baris tulisan — yang pertama berhenti tepat sebelum lipatan
    bar_h = w * 0.055
    left = x1 + w * 0.155
    for i, frac in enumerate((0.55, 0.37)):
        yy = y1 + h * (0.255 + i * 0.140)
        d.rounded_rectangle([left, yy, left + w * frac, yy + bar_h],
                            radius=bar_h / 2, fill=RULE + (255,))

    # centang: tugas yang beres — bagian yang bikin ikonnya tidak generik
    sw = w * 0.105
    ay = y1 + h * 0.685
    d.line([(left, ay), (left + w * 0.175, ay + w * 0.175), (left + w * 0.60, ay - w * 0.230)],
           fill=INK + (255,), width=int(sw), joint="curve")
    # ujung membulat — ImageDraw.line tidak punya round cap
    r2 = sw / 2
    for pt in ((left, ay), (left + w * 0.60, ay - w * 0.230)):
        d.ellipse([pt[0] - r2, pt[1] - r2, pt[0] + r2, pt[1] + r2], fill=INK + (255,))

    return img.resize((size, size), Image.LANCZOS).convert("RGB")


jobs = [
    # nama, ukuran, seberapa besar kertasnya relatif kanvas
    ("icon-192.png",          192, 0.53),
    ("icon-512.png",          512, 0.53),
    ("apple-touch-icon.png",  180, 0.53),
    # maskable: Android memotong jadi lingkaran/squircle, isinya harus muat
    # di lingkaran aman 80% — jadi kertasnya sengaja dikecilkan.
    ("icon-maskable-512.png", 512, 0.44),
    ("icon-maskable-192.png", 192, 0.44),
]

for name, size, content in jobs:
    im = draw_icon(size, content)
    im.save(os.path.join(OUT, name), "PNG", optimize=True)
    print(f"{name:26s} {size}x{size}  {os.path.getsize(os.path.join(OUT, name)):>6d} B")

# cek zona aman maskable: seluruh piksel kertas harus di dalam radius 40%
im = Image.open(os.path.join(OUT, "icon-maskable-512.png")).convert("RGB")
px = im.load()
worst = 0
for y in range(512):
    for x in range(512):
        r, g, b = px[x, y]
        if r > 150 and g > 170:  # warna kertas / lipatan
            worst = max(worst, ((x - 255.5) ** 2 + (y - 255.5) ** 2) ** 0.5)
print(f"\nmaskable: isi terjauh {worst:.1f}px dari pusat, batas aman 204.8px -> "
      f"{'AMAN' if worst <= 204.8 else 'MELEWATI BATAS'}")
