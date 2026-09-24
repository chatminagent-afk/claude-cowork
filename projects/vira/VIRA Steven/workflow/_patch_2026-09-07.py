# -*- coding: utf-8 -*-
"""
_patch_2026-09-07.py - tutup kebocoran harga di LAPISAN YANG BENAR, plus perdalam pain point.

Masukan : 2026-09-06-VIRA-Personal-Main-v3.5.json   (tidak diubah)
Keluaran: 2026-09-07-VIRA-Personal-Main-v3.6.json
          2026-09-07-system-prompt-VIRA-Personal-v3.6.md

LATAR - insiden studysipil, 2026-09-07 15:04.
VIRA menyebut Rp3.000.000 / Rp5.000.000 ke prospek yang belum menanyakan harga,
dan balasan prospek berikutnya langsung "harganya gabisa kurang ya?".

Patch d (v3.4) dan e (v3.5) dua-duanya menambal SYSTEM PROMPT. Dua-duanya benar,
dan dua-duanya tidak menolong, karena kebocorannya satu lapis di bawah: node
"Preprocess - Context Detection". Debounce 60 detik menggabungkan empat pesan
jadi satu teks yang memuat kata `promo` dan `harga` - dua-duanya milik PELANGGAN
prospek, bukan pertanyaan untuk kita. Regex askingPrice menyala, lalu menyuntik
ini tepat di atas [USER QUERY]:

    [CONTEXT: User menanyakan harga. Sebut kisaran dari DATA PRODUK lalu arahkan
    ke Steven untuk angka final. Jangan menawar, jangan memberi diskon.]

Jadi model membaca dua hal yang TIDAK saling bertentangan: prompt bilang "sebut
kisaran HANYA kalau dia menanyakan harga", konteks bilang "user menanyakan harga".
Dia patuh pada keduanya. Aturannya tidak pernah dilanggar - premisnya yang palsu.

ISI PATCH
  A. Preprocess: askingPrice tidak lagi percaya pada kata harga telanjang.
     Ditambah gerbang CERITA_ORANG_LAIN (dia menceritakan pertanyaan pelanggannya)
     dan MILIK_DIA (dia menyebut angka bisnisnya sendiri - jawaban TINGKAT 2B),
     plus pengaman balik TANYA_HARGA_KITA supaya pertanyaan asli tidak ikut dibungkam.
     `promo` dan `bayar` dicabut dari daftar kata harga.
  B. Preprocess: aiContext harga dari IMPERATIF jadi BERSYARAT. Ini yang penting -
     regex tidak akan pernah sempurna, jadi keputusan akhirnya dikembalikan ke model
     alih-alih diperintahkan.
  C. Prompt # HARGA: aturan eksplisit bahwa kata "harga" milik orang lain bukan
     pertanyaan untuk kita, dan kalau ragu jangan sebut angka.
  D. Prompt # MENGGALI TINGKAT 1: satu pertanyaan pendalaman setelah masalah utama
     keluar - menanyakan AKIBAT, bukan "ada kendala lain?".
  E. Prompt spek [DECK_REQUEST]: pain_points dipisah titik koma dan dilarang
     mengulang masalah_utama. Tanpa ini deck SELALU tepat 2 poin, karena
     buat_deck.py memecah pain_points dengan ";" (mendukung 6) tapi VIRA tidak
     pernah diberi tahu soal pemisah itu.

SINKRONISASI DRIFT
n8n live (ditarik 2026-09-07) berbeda satu baris dari file lokal v3.5: kalimat
tawaran deck sudah diedit manual langsung di n8n. Langkah 0 menyalin kalimat live
itu ke v3.6 supaya import v3.6 tidak menghapus suntingan tangan tersebut.

Catatan teknis: prefix "=" systemMessage dipertahankan (expression mode n8n),
dan keenam ekspresi {{ }} harus tetap utuh.

Jalankan: python _patch_2026-09-07.py
"""
import io
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.5.json")
DST = os.path.join(DIR, "2026-09-07-VIRA-Personal-Main-v3.6.json")
MD = os.path.join(DIR, "2026-09-07-system-prompt-VIRA-Personal-v3.6.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

NODES = {n["name"]: n for n in wf["nodes"]}
agent = NODES["AI Agent"]
prenode = NODES["Preprocess - Context Detection"]

sp0 = agent["parameters"]["options"]["systemMessage"]
pre0 = prenode["parameters"]["jsCode"]
assert sp0.startswith("="), "systemMessage harus expression mode"
EKSPRESI = re.findall(r"\{\{[^}]+\}\}", sp0)
assert len(EKSPRESI) == 6, "ekspresi {{ }} berubah: %d" % len(EKSPRESI)


def ganti(teks, lama, baru, label):
    n = teks.count(lama)
    assert n == 1, "%s: pola ditemukan %d kali (harus 1)" % (label, n)
    return teks.replace(lama, baru)


# =========================================================================
# 0. SINKRONKAN DRIFT DARI n8n LIVE
# =========================================================================
DRIFT_LAMA = (
    '  "mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? usahanya namanya apa kak,\n'
    '  biar Steven tulis di covernya."\n'
)
DRIFT_BARU = (
    '  "mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? '
    'kalau boleh tau nama usahanya apa ya kak?."\n'
)
sp = ganti(sp0, DRIFT_LAMA, DRIFT_BARU, "0-drift")


# =========================================================================
# A + B. NODE PREPROCESS - CONTEXT DETECTION
# =========================================================================
PRE_A_LAMA = r"""// -- INTENT (domain jasa AI customer service) --
// Harus ada kata yang benar-benar soal uang/paket, bukan sekadar "berapa".
// Akhiran -nya/-ku/-mu WAJIB ditoleransi: \b di ujung kata membuat "harganya",
// "brosurnya", "biayanya" tidak pernah cocok - padahal itu bentuk yang paling
// sering dipakai orang Indonesia saat bertanya.
const askingPrice = /\b(harga|hrg|biaya|tarif|bayar|langganan|paket|basic|premium|mahal|murah|promo|diskon|setup ?fee|budget|nego)(nya|ku|mu)?\b/i.test(message)
  || /\bberapa\b[^?]{0,20}\b(harga|biaya|duit|rupiah|bulan|bulanan)/i.test(message);
"""

PRE_A_BARU = r"""// -- INTENT (domain jasa AI customer service) --
// Harus ada kata yang benar-benar soal uang/paket, bukan sekadar "berapa".
// Akhiran -nya/-ku/-mu WAJIB ditoleransi: \b di ujung kata membuat "harganya",
// "brosurnya", "biayanya" tidak pernah cocok - padahal itu bentuk yang paling
// sering dipakai orang Indonesia saat bertanya.
//
// 2026-09-07 - insiden studysipil. Kata harga TELANJANG tidak cukup lagi.
// Debounce menggabungkan empat pesan jadi satu: "biasanya pas lg promo buka
// kelas sih / ads itu pasti pd tanya hal yg sama / harga, kuota, apa aja yg
// didapet / sama jadwalnya kapan". Dua kata kena (`promo` dan `harga`) padahal
// dua-duanya milik PELANGGAN DIA. Flag menyala -> aiContext menyuntik "User
// menanyakan harga. Sebut kisaran..." tepat di atas [USER QUERY] -> VIRA
// menyebut Rp3jt/Rp5jt ke lead yang belum bertanya, dan balasan berikutnya
// minta diskon. Aturan di system prompt tidak menolong: dari sudut pandang
// model, konteks ini MEMBERI TAHU bahwa syarat "kalau ditanya" sudah terpenuhi.
//
// `promo` dan `bayar` dicabut dari daftar: dua-duanya jauh lebih sering muncul
// saat prospek bercerita soal bisnisnya sendiri ("lagi promo buka kelas",
// "pelanggan bayar transfer") daripada saat dia menanyakan harga kita.
const KATA_HARGA = /\b(harga|hrg|biaya|tarif|langganan|paket|basic|premium|mahal|murah|diskon|setup ?fee|nego|price ?list|pricelist)(nya|ku|mu)?\b/i;

// Dia sedang MENCERITAKAN pertanyaan pelanggannya, bukan bertanya ke kita.
const CERITA_ORANG_LAIN =
     /\b(pd|pada|mereka|orang|customer|pelanggan|calon|murid|klien|konsumen|pembeli|user|tamu|pasien)\b[^.?!]{0,30}\b(tanya|nanya|nanyain|bertanya|tanyain)\b/i.test(message)
  || /\b(tanya|nanya|ditanya|ditanyain|nanyain|pertanyaan|pertanyaannya)\b[^.?!]{0,30}\b(sama|hal|berulang|melulu|itu.?itu|terus)\b/i.test(message)
  || /\b(sering|selalu|biasanya|pasti|kebanyakan|rata.?rata)\b[^.?!]{0,25}\b(tanya|nanya|nanyain|ditanya|ditanyain)\b/i.test(message);

// Angka itu MILIK DIA - jawaban atas pertanyaan TINGKAT 2B, bukan pertanyaan
// harga. Tanpa gerbang ini, tiap kali prospek menjawab "biaya adminku 3 juta"
// atau "sekali closing 500rb" konteks harga ikut menyala di giliran itu.
const MILIK_DIA =
     /\b(paket|harga|biaya|tarif|admin)\w*\b[^.?!]{0,20}\b(aku|gue|gw|saya|kami|kita|sendiri)\b/i.test(message)
  || /\b(paket|harga|biaya|tarif|kelas|admin)\w*ku\b/i.test(message)
  || /\b(biaya|harga|tarif)\b[^.?!]{0,15}\b\w+ku\b/i.test(message);

// Pengaman balik: kalau di pesan yang sama dia JELAS menanyakan harga KITA,
// cerita soal pelanggannya tidak boleh membungkam. Debounce sering menggabung
// dua-duanya dalam satu giliran.
const TANYA_HARGA_KITA =
     /\b(berapa|brp)\b[^.?!]{0,25}\b(harga|biaya|tarif|paket|basic|premium|langganan)/i.test(message)
  || /\b(harga|biaya|tarif|paket|basic|premium|langganan)(nya|ku|mu)?\b[^.?!]{0,25}\b(berapa|brp|gimana|bagaimana)\b/i.test(message)
  || /\b(harga|biaya|tarif|paket|price ?list|pricelist)(nya|mu)?\b[^.?!]{0,20}\b(vira|kamu|kalian|lo|situ|steven)\b/i.test(message)
  || /\b(vira|kamu|kalian|paket)\w*\b[^.?!]{0,20}\b(harga|biaya|tarif)(nya|mu)?\b/i.test(message);

const askingPrice = TANYA_HARGA_KITA
  || (KATA_HARGA.test(message) && !CERITA_ORANG_LAIN && !MILIK_DIA)
  || (/\bberapa\b[^?]{0,20}\b(harga|biaya|duit|rupiah|bulan|bulanan)/i.test(message)
      && !CERITA_ORANG_LAIN && !MILIK_DIA);
"""

PRE_B_LAMA = (
    "if (askingPrice) aiContext += 'User menanyakan harga. Sebut kisaran dari "
    "DATA PRODUK lalu arahkan ke Steven untuk angka final. Jangan menawar, "
    "jangan memberi diskon. ';\n"
)

# Regex tidak akan pernah sempurna. Kalimat ini sengaja BERSYARAT, bukan perintah:
# keputusan akhirnya dikembalikan ke model, yang bisa membaca kalimat utuhnya.
PRE_B_BARU = (
    "if (askingPrice) aiContext += 'Sepertinya dia menanyakan harga. Periksa dulu "
    "pesannya: kalau dia memang menanyakan harga VIRA, sebut kisaran dari DATA PRODUK "
    "lalu arahkan ke Steven untuk angka final. Kalau kata harga muncul karena dia sedang "
    "menceritakan pertanyaan pelanggannya sendiri atau menyebut angka bisnisnya sendiri, "
    "JANGAN sebut angka apa pun. Jangan menawar, jangan memberi diskon. ';\n"
)

pre = ganti(pre0, PRE_A_LAMA, PRE_A_BARU, "A-askingPrice")
pre = ganti(pre, PRE_B_LAMA, PRE_B_BARU, "B-aiContext")


# =========================================================================
# C. PROMPT # HARGA
# =========================================================================
C_LAMA = (
    "Selalu tambahkan bahwa angka finalnya menyesuaikan kompleksitas alur bisnisnya.\n\n"
)
C_BARU = (
    "Selalu tambahkan bahwa angka finalnya menyesuaikan kompleksitas alur bisnisnya.\n"
    "\n"
    "Kata “harga” milik orang lain bukan pertanyaan untukku. Kalau dia bercerita bahwa\n"
    "pelanggannya sering menanyakan harga, kuota, atau jadwal, dia sedang menjelaskan\n"
    "masalahnya — bukan meminta angka. Balas dengan mengakui masalahnya. Begitu juga\n"
    "waktu dia menyebut angka bisnisnya sendiri (“biaya adminku 3 juta”, “sekali closing\n"
    "500rb”): itu jawaban atas pertanyaanku, bukan pertanyaan tentang paket.\n"
    "Kalau ragu, jangan sebut angka. Menahan angka satu giliran tidak pernah merugikan;\n"
    "menyebut angka ke orang yang belum bertanya membuat dia menawar sebelum dia\n"
    "mengerti apa yang dia beli.\n\n"
)
sp = ganti(sp, C_LAMA, C_BARU, "C-harga")


# =========================================================================
# D. PROMPT # MENGGALI - PENDALAMAN PAIN POINT
# =========================================================================
D_LAMA = (
    "Momen paling wajar: saat menawarkan decknya, karena memang di situ\n"
    "namanya dipakai. Contoh: \"biar Steven tulis di decknya, usahanya namanya apa kak?\"\n\n"
)
D_BARU = (
    "Momen paling wajar: saat menawarkan decknya, karena memang di situ\n"
    "namanya dipakai. Contoh: \"biar Steven tulis di decknya, usahanya namanya apa kak?\"\n"
    "\n"
    "Sekali masalah utamanya keluar, gali SATU kali lagi — sekali saja, jangan diulang.\n"
    "Bukan “ada kendala lain?”, karena itu hampir selalu dijawab “nggak ada”. Tanyakan\n"
    "AKIBATNYA, karena di situ keluhan keduanya keluar sendiri dan bentuknya lebih konkret.\n"
    "Contoh: \"kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak?\"\n"
    "atau \"pas lagi ramai gitu, yang paling bikin repot bagian mananya kak?\"\n"
    "Jawabannya masuk ke `pain_points`. Kalau dia jawab pendek atau ganti topik,\n"
    "tinggalkan — jangan dikejar.\n\n"
)
sp = ganti(sp, D_LAMA, D_BARU, "D-pain-gali")


# =========================================================================
# E. PROMPT - SPEK FIELD pain_points
# =========================================================================
E_LAMA = (
    "  - catatan — hal penting yang tidak masuk baris mana pun\n\n"
)
E_BARU = (
    "  - catatan — hal penting yang tidak masuk baris mana pun\n"
    "  - pain_points — keluhan LAIN di luar masalah_utama, dipisah titik koma \";\".\n"
    "    Tiap keluhan jadi satu poin terpisah di deck, jadi tulis dua sampai empat kalau\n"
    "    memang ada, bukan satu kalimat panjang. JANGAN mengulang isi masalah_utama dengan\n"
    "    kata lain: dua poin kembar di deck terbaca seperti tidak ada yang benar-benar digali.\n\n"
)
sp = ganti(sp, E_LAMA, E_BARU, "E-pain-spek")


# =========================================================================
# PEMERIKSAAN AKHIR
# =========================================================================
assert sp.startswith("="), "prefix = hilang"
assert re.findall(r"\{\{[^}]+\}\}", sp) == EKSPRESI, "ekspresi {{ }} berubah"
assert "kalau boleh tau nama usahanya apa ya kak?." in sp, "drift live tidak tersalin"
assert "milik orang lain bukan pertanyaan untukku" in sp
assert "Sekali masalah utamanya keluar" in sp
assert "dipisah titik koma" in sp
assert "promo" not in pre.split("const KATA_HARGA")[1].split("\n")[0], "promo masih di KATA_HARGA"
assert "CERITA_ORANG_LAIN" in pre and "MILIK_DIA" in pre and "TANYA_HARGA_KITA" in pre
assert "User menanyakan harga. Sebut kisaran" not in pre, "aiContext lama masih ada"
assert pre.count("const askingPrice") == 1

agent["parameters"]["options"]["systemMessage"] = sp
prenode["parameters"]["jsCode"] = pre

with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8") as f:
    f.write(sp[1:])

print("DST    : %s" % os.path.basename(DST))
print("MD     : %s" % os.path.basename(MD))
print("prompt : %d -> %d karakter | baris %d -> %d"
      % (len(sp0), len(sp), sp0.count(chr(10)) + 1, sp.count(chr(10)) + 1))
print("pre    : %d -> %d karakter | baris %d -> %d"
      % (len(pre0), len(pre), pre0.count(chr(10)) + 1, pre.count(chr(10)) + 1))
print("node   : %d" % len(wf["nodes"]))
