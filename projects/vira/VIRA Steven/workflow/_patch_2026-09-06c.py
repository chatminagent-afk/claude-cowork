# -*- coding: utf-8 -*-
"""
_patch_2026-09-06c.py — prioritas nama_bisnis di prompt AI Agent.

Masukan : 2026-09-06-VIRA-Personal-Main-v3.2.json    (tidak diubah)
Keluaran: 2026-09-06-VIRA-Personal-Main-v3.3.json    (berkas baru)
          2026-09-06-system-prompt-VIRA-Personal-v3.3.md  (bentuk bacanya)

Kenapa: deck "tanpa-nama" 2026-09-06 terbit tanpa cover karena `nama_bisnis` kosong di
REQUESTS. Sisi generator sudah diperbaiki (cover tidak lagi bisa hilang, tapi jadi generik).
Yang belum: promptnya sendiri menggolongkan `nama_bisnis` sebagai baris yang "tidak
menggagalkan slide" — padahal dia satu-satunya yang mengubah cover jadi generik. Jadi VIRA
tidak pernah punya alasan mengejarnya.

Yang TIDAK diubah: syarat mengeluarkan [DECK_REQUEST]. Pelonggaran A1 (2026-08-30) sengaja
dibuat supaya brief setengah jadi tidak hilang, dan itu tetap benar. Yang berubah hanya
prioritas menggali.

Catatan teknis: nilai systemMessage di n8n diawali "=" (penanda expression mode). Prefix itu
DIPERTAHANKAN — tanpa dia field pindah ke fixed mode dan enam injeksi konteks
({{ $json.prospect_context }} dst.) tercetak mentah sebagai teks.

Jalankan: python _patch_2026-09-06c.py
"""
import io
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.2.json")
DST = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.3.json")
MD = os.path.join(DIR, "2026-09-06-system-prompt-VIRA-Personal-v3.3.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

agent = [n for n in wf["nodes"] if n["name"] == "AI Agent"]
assert len(agent) == 1, "node 'AI Agent' tidak tunggal: %d" % len(agent)
sp = agent[0]["parameters"]["options"]["systemMessage"]
assert sp.startswith("="), "systemMessage tidak lagi expression mode — jangan ditimpa"
ekspresi = re.findall(r"\{\{[^}]+\}\}", sp)
assert len(ekspresi) == 6, "jumlah ekspresi konteks berubah: %s" % ekspresi

TAMBAHAN = (
    "  Satu baris berdiri sendiri: `nama_bisnis`. Tanpa itu cover decknya jadi generik "
    "\u2014 hilang\n"
    "  satu-satunya slide yang menyebut nama dia. Kejar itu duluan, sebelum menutup "
    "obrolan brief.\n"
)

SUNTING = [
    # 1. nama_bisnis diangkat jadi prioritas gali, tepat setelah alasan A1
    ("  Brief setengah jadi tetap berguna; yang hilang justru kalau tidak kucatat sama sekali.\n",
     "  Brief setengah jadi tetap berguna; yang hilang justru kalau tidak kucatat sama sekali.\n"
     "\n" + TAMBAHAN),
    # 2. ekor paragraf "tujuh penentu slide" tidak lagi menyesatkan
    ("berguna tapi tidak menggagalkan slide.",
     "berguna tapi tidak menggagalkan slide \u2014 kecuali `nama_bisnis`, lihat di atas."),
]

baru = sp
for lama, ganti in SUNTING:
    assert baru.count(lama) == 1, "pola tidak tunggal (%d): %r" % (baru.count(lama), lama[:50])
    baru = baru.replace(lama, ganti)

assert baru != sp
assert re.findall(r"\{\{[^}]+\}\}", baru) == ekspresi, "ekspresi konteks ikut berubah"
assert baru.startswith("="), "prefix expression mode hilang"

agent[0]["parameters"]["options"]["systemMessage"] = baru
with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8") as f:
    f.write(baru[1:])          # tanpa "=" — itu penanda n8n, bukan isi prompt

print("SRC   : %s" % os.path.basename(SRC))
print("DST   : %s" % os.path.basename(DST))
print("MD    : %s" % os.path.basename(MD))
print("prompt: %d -> %d karakter (+%d)" % (len(sp), len(baru), len(baru) - len(sp)))
print("node  : %d (tidak berubah)" % len(wf["nodes"]))
