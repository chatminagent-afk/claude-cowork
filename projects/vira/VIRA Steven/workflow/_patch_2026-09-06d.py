# -*- coding: utf-8 -*-
"""
_patch_2026-09-06d.py \u2014 pindahkan dorongan nama_bisnis ke bagian yang benar.

Masukan : 2026-09-06-VIRA-Personal-Main-v3.3.json    (tidak diubah)
Keluaran: 2026-09-06-VIRA-Personal-Main-v3.4.json    (berkas baru)
          2026-09-06-system-prompt-VIRA-Personal-v3.4.md

Kenapa: dua transkrip 2026-09-06 (konter game & konveksi) menunjukkan VIRA tidak pernah
menanyakan nama usaha. Polanya identik \u2014 empat giliran, empat pertanyaan, semuanya
TINGKAT 2, lalu langsung menawarkan deck dan menutup.

Tiga sebab yang saling menguatkan:
  1. TINGKAT 1 tidak punya contoh kalimat; TINGKAT 2 punya dua yang harfiah. Contoh konkret
     jauh lebih dipatuhi daripada label prioritas, jadi jatah "satu pertanyaan per balasan"
     selalu habis di TINGKAT 2.
  2. Dua dari tiga item TINGKAT 1 datang gratis \u2014 `industri` terpancing pertanyaan
     pembuka, `masalah_utama` diceritakan sendiri. Hanya `nama_bisnis` yang butuh pertanyaan
     tersendiri, dan itu yang tidak ada skripnya.
  3. Balasan penutup ("sudah aku teruskan ke Steven") tidak memeriksa apa pun.

v3.3 menaruh dorongannya di blok `[DECK_REQUEST]` \u2014 blok itu mengatur KAPAN TAG KELUAR,
bukan perilaku bertanya. Salah tempat, jadi dicabut di sini dan ditulis ulang di MENGGALI
lengkap dengan contoh kalimat, plus satu perkecualian aturan di balasan penutup.

Yang TIDAK diubah: syarat `[DECK_REQUEST]` tetap longgar (A1 2026-08-30). Prospek yang tidak
mau menyebut nama usahanya tetap tercatat.

Catatan teknis: prefix "=" pada systemMessage adalah penanda expression mode n8n \u2014
dipertahankan, lihat _patch_2026-09-06c.py.

Jalankan: python _patch_2026-09-06d.py
"""
import io
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.3.json")
DST = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.4.json")
MD = os.path.join(DIR, "2026-09-06-system-prompt-VIRA-Personal-v3.4.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

agent = [n for n in wf["nodes"] if n["name"] == "AI Agent"]
assert len(agent) == 1, "node 'AI Agent' tidak tunggal: %d" % len(agent)
sp = agent[0]["parameters"]["options"]["systemMessage"]
assert sp.startswith("="), "systemMessage tidak lagi expression mode \u2014 jangan ditimpa"
ekspresi = re.findall(r"\{\{[^}]+\}\}", sp)
assert len(ekspresi) == 6, "jumlah ekspresi konteks berubah: %s" % ekspresi

# ── A. TINGKAT 1 dapat contoh kalimat, setara TINGKAT 2
A_LAMA = """cuma karena salah satunya belum keluar.
"""
A_BARU = """cuma karena salah satunya belum keluar.

Dari ketiganya, industri dan masalahnya hampir selalu keluar sendiri sambil dia cerita.
Nama usahanya tidak \u2014 itu satu-satunya yang harus kutanyakan sengaja, dan tanpa itu cover
decknya jadi generik. Momen paling wajar: saat menawarkan decknya, karena memang di situ
namanya dipakai. Contoh: "biar Steven tulis di decknya, usahanya namanya apa kak?"
"""

# ── B. balasan penutup jadi perkecualian aturan satu pertanyaan
B_LAMA = """baru gali. Kalau dia terlihat buru-buru atau cuma ingin tahu harga, berhenti menggali dan jawab saja.
"""
B_BARU = """baru gali. Kalau dia terlihat buru-buru atau cuma ingin tahu harga, berhenti menggali dan jawab saja.

Satu perkecualian pada "satu pertanyaan per balasan": balasan yang menutup obrolan brief
("sudah aku teruskan ke Steven"). Kalau nama usahanya belum keluar sampai titik itu,
tanyakan di balasan penutup yang sama \u2014 jangan menutup dulu lalu menanyakannya belakangan.
"""

# ── C. cabut tambahan v3.3 yang salah tempat, rapikan rujukannya
C_LAMA = """
  Satu baris berdiri sendiri: `nama_bisnis`. Tanpa itu cover decknya jadi generik \u2014 hilang
  satu-satunya slide yang menyebut nama dia. Kejar itu duluan, sebelum menutup obrolan brief.
"""
C_BARU = ""

# ── D. harga paket digerbang, setara add-on & biaya token
# VIRA menyebut Rp3jt/Rp5jt tanpa diminta di dua transkrip 2026-09-06, dua kali per
# percakapan, salah satunya menempel di tawaran deck. Sebabnya kalimat ini imperatif tanpa
# syarat, padahal add-on (baris 179) dan biaya token (182) di bagian yang sama sudah
# bersyarat "kalau ditanya". Harga yang datang sebelum nilainya terbangun membuat prospek
# menilai angka, bukan hasil.
D_LAMA = "Sebutkan kisaran, lalu arahkan ke Steven untuk angka final:"
D_BARU = """Sebutkan kisaran HANYA kalau dia menanyakan harga, biaya, atau paket. Jangan pernah
menyebut angkanya lebih dulu — termasuk saat menawarkan deck atau menutup obrolan.
Kalau memang ditanya, sebutkan kisarannya lalu arahkan ke Steven untuk angka final:"""

SUNTING = [(A_LAMA, A_BARU), (B_LAMA, B_BARU), (C_LAMA, C_BARU),
           ("kecuali `nama_bisnis`, lihat di atas.", "kecuali `nama_bisnis`, lihat TINGKAT 1."),
           (D_LAMA, D_BARU)]

baru = sp
for lama, ganti in SUNTING:
    assert baru.count(lama) == 1, "pola tidak tunggal (%d): %r" % (baru.count(lama), lama[:60])
    baru = baru.replace(lama, ganti)

assert baru != sp
assert re.findall(r"\{\{[^}]+\}\}", baru) == ekspresi, "ekspresi konteks ikut berubah"
assert baru.startswith("="), "prefix expression mode hilang"
assert "Kejar itu duluan" not in baru, "tambahan v3.3 belum tercabut"
assert "lihat di atas" not in baru, "rujukan menggantung masih ada"
assert "HANYA kalau dia menanyakan harga" in baru, "gerbang harga tidak terpasang"

agent[0]["parameters"]["options"]["systemMessage"] = baru
with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8") as f:
    f.write(baru[1:])          # tanpa "=" \u2014 itu penanda n8n, bukan isi prompt

print("SRC   : %s" % os.path.basename(SRC))
print("DST   : %s" % os.path.basename(DST))
print("MD    : %s" % os.path.basename(MD))
print("prompt: %d -> %d karakter | baris %d -> %d"
      % (len(sp), len(baru), sp.count(chr(10)) + 1, baru.count(chr(10)) + 1))
print("node  : %d (tidak berubah)" % len(wf["nodes"]))
