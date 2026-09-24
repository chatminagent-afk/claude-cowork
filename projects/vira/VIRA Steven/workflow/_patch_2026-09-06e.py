# -*- coding: utf-8 -*-
"""
_patch_2026-09-06e.py \u2014 tempelkan aturan ke KALIMAT CONTOH, bukan ke paragraf aturan.

Masukan : 2026-09-06-VIRA-Personal-Main-v3.4.json   (tidak diubah)
Keluaran: 2026-09-06-VIRA-Personal-Main-v3.5.json
          2026-09-06-system-prompt-VIRA-Personal-v3.5.md

Pelajaran dari empat transkrip: VIRA menyalin kalimat contoh KATA PER KATA, dan mengabaikan
aturan yang cuma dinarasikan. Tawaran deck di blok [DECK_REQUEST] punya kalimat contoh harfiah,
jadi kalimat itulah yang selalu keluar \u2014 lengkap dengan harga yang menempel di depannya dan
tanpa pertanyaan nama usaha, walaupun v3.4 sudah melarang yang pertama dan mencontohkan yang
kedua di bagian MENGGALI.

Perbaikannya: taruh dua-duanya DI TITIK KEJADIAN. Larangan harga ditulis di kalimat tawaran,
dan disediakan dua varian kalimat contoh \u2014 satu untuk saat nama usaha sudah diketahui,
satu untuk saat belum.

Catatan teknis: prefix "=" systemMessage dipertahankan (expression mode n8n).

Jalankan: python _patch_2026-09-06e.py
"""
import io
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.4.json")
DST = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.5.json")
MD = os.path.join(DIR, "2026-09-06-system-prompt-VIRA-Personal-v3.5.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)
agent = [n for n in wf["nodes"] if n["name"] == "AI Agent"]
assert len(agent) == 1
sp = agent[0]["parameters"]["options"]["systemMessage"]
assert sp.startswith("=")
ekspresi = re.findall(r"\{\{[^}]+\}\}", sp)
assert len(ekspresi) == 6

LAMA = """  dan mengabarkan deck yang tidak dia minta terdengar memaksa. Tawarkan saja, sekali:
  "mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?"
"""

BARU = """  dan mengabarkan deck yang tidak dia minta terdengar memaksa. Tawarkan saja, sekali, dan
  JANGAN menempelkan harga pada tawaran ini \u2014 kecuali dia memang sedang menanyakan harga.

  Kalau nama usahanya sudah kutahu:
  "mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?"

  Kalau belum \u2014 tanyakan di kalimat yang sama, karena nama itu yang dipakai di cover decknya:
  "mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? usahanya namanya apa kak,
  biar Steven tulis di covernya."
"""

assert sp.count(LAMA) == 1, "pola tawaran deck tidak tunggal: %d" % sp.count(LAMA)
baru = sp.replace(LAMA, BARU)
assert re.findall(r"\{\{[^}]+\}\}", baru) == ekspresi
assert baru.startswith("=")
assert "usahanya namanya apa kak" in baru
assert "JANGAN menempelkan harga" in baru

agent[0]["parameters"]["options"]["systemMessage"] = baru
with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8") as f:
    f.write(baru[1:])

print("DST   : %s" % os.path.basename(DST))
print("prompt: %d -> %d karakter | baris %d -> %d"
      % (len(sp), len(baru), sp.count(chr(10)) + 1, baru.count(chr(10)) + 1))
print("node  : %d" % len(wf["nodes"]))
