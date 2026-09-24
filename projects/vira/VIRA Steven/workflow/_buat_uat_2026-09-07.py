# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-07.py - turunkan _uat_2026-09-07.py dari harness _uat_2026-09-06b.py.

Harness lama diarahkan ulang ke v3.6 (jadi 186 assertion lamanya ikut jalan sebagai
regresi), lalu dua seksi baru disisipkan sebelum ringkasan:

  L. HARGA - insiden 2026-09-07 (perilaku, menjalankan JS asli node Preprocess)
  M. PROMPT v3.6 + PAIN POINT (statis pada systemMessage, plus pecah_pain asli
     dari buat_deck.py untuk membuktikan pemisah ";" benar-benar menghasilkan
     lebih dari dua poin)

Jalankan: python _buat_uat_2026-09-07.py   (lalu: python _uat_2026-09-07.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-06b.py")
DST = os.path.join(DIR, "_uat_2026-09-07.py")

with io.open(SRC, encoding="utf-8") as f:
    teks = f.read()

# --- 1. arahkan ke v3.6 --------------------------------------------------
LAMA_WF = 'WF = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.2.json")'
BARU_WF = 'WF = os.path.join(DIR, "2026-09-07-VIRA-Personal-Main-v3.6.json")'
assert teks.count(LAMA_WF) == 1
teks = teks.replace(LAMA_WF, BARU_WF)

teks = teks.replace(
    "_uat_2026-09-06b.py — UAT perilaku untuk 2026-09-06-VIRA-Personal-Main-v3.2.json.",
    "_uat_2026-09-07.py — UAT perilaku untuk 2026-09-07-VIRA-Personal-Main-v3.6.json.\n\n"
    "Diturunkan dari _uat_2026-09-06b.py (jangan diedit manual — ubah generatornya,\n"
    "_buat_uat_2026-09-07.py, lalu jalankan ulang). Seluruh assertion lama ikut jalan\n"
    "sebagai regresi; seksi L dan M baru untuk insiden harga 2026-09-07.",
    1,
)
teks = teks.replace("Jalankan: python _uat_2026-09-06b.py",
                    "Jalankan: python _uat_2026-09-07.py", 1)
teks = teks.replace("Import 2026-09-06-VIRA-Personal-Main-v3.2.json",
                    "Import 2026-09-07-VIRA-Personal-Main-v3.6.json", 1)

# --- 2. seksi baru -------------------------------------------------------
BARU = r'''
# ===========================================================================
bagian("L. HARGA — insiden studysipil 2026-09-07 (kebocoran angka ke lead dingin)")
# ===========================================================================
# Pesan asli prospek, empat baris yang digabung debounce 60 detik jadi satu
# giliran. Kata `promo` dan `harga` dua-duanya milik PELANGGAN DIA.
INSIDEN = ("biasanya pas lg promo buka kelas sih\n"
           "ads itu pasti pd tanya hal yg sama\n"
           "harga, kuota, apa aja yg didapet\n"
           "sama jadwalnya kapan")

d = pre(INSIDEN)
cek("L1  pesan insiden TIDAK memicu konteks harga",
    d["askingPrice"] is False, d["aiContext"])
cek("L1b pesan insiden tidak menyuntik blok [CONTEXT] harga",
    "menanyakan harga" not in d["ai_input_text"], d["ai_input_text"][-200:])

for pesan in ["pelanggan sering nanya harga sama ongkir",
              "customer pd nanyain harga terus",
              "mereka biasanya tanya harga, stok, sama ukuran",
              "yang ditanya itu itu aja sih, harga sama jadwal",
              "calon murid pasti nanya biaya dulu"]:
    d = pre(pesan)
    cek("L2  '%s' = cerita pelanggan, bukan tanya harga" % pesan,
        d["askingPrice"] is False, d["aiContext"])

for pesan in ["biaya adminku sebulan sekitar 3 juta",
              "harga kelasku 500rb per murid",
              "paket kelas aku ada 3 kak",
              "adminku ada 2 orang, biayanya 4 juta"]:
    d = pre(pesan)
    cek("L3  '%s' = angka miliknya (jawaban TINGKAT 2B)" % pesan,
        d["askingPrice"] is False, d["aiContext"])

for pesan in ["harganya berapa ya", "biaya bulanannya gimana",
              "paket premium berapa harganya", "harganya gabisa kurang ya?",
              "boleh minta pricelist?", "mahal ga sih?", "ada diskon ga kak?",
              "kalau paket basic dapat apa aja?", "berapa biaya setupnya?",
              "oh gitu, btw harga viranya berapa kak?"]:
    d = pre(pesan)
    cek("L4  '%s' TETAP memicu konteks harga" % pesan, d["askingPrice"] is True)

d = pre("pelanggan sering nanya harga. btw berapa harga paket basic?")
cek("L5  cerita + pertanyaan asli di satu giliran tetap memicu harga",
    d["askingPrice"] is True, d["aiContext"])

for pesan in ["lagi promo buka kelas nih", "pelanggan bayar lewat transfer",
              "abis promo biasanya sepi"]:
    d = pre(pesan)
    cek("L6  '%s' (promo/bayar dicabut) TIDAK memicu harga" % pesan,
        d["askingPrice"] is False, d["aiContext"])

d = pre("harganya berapa ya")
cek("L7  aiContext harga TIDAK lagi imperatif tanpa syarat",
    "User menanyakan harga. Sebut kisaran" not in d["aiContext"], d["aiContext"])
cek("L7b aiContext harga memuat syarat eksplisit",
    "Periksa dulu" in d["aiContext"] and "JANGAN sebut angka" in d["aiContext"],
    d["aiContext"])

d = pre("halo mau tanya soal ai customer service")
cek("L8  pesan netral tidak menyuntik [CONTEXT] apa pun",
    d["aiContext"] == "" and "[CONTEXT:" not in d["ai_input_text"], d["aiContext"])

_pre_src = NODES["Preprocess - Context Detection"]["parameters"]["jsCode"]
cek("L9  gerbang CERITA_ORANG_LAIN / MILIK_DIA / TANYA_HARGA_KITA terpasang",
    all(k in _pre_src for k in ("CERITA_ORANG_LAIN", "MILIK_DIA", "TANYA_HARGA_KITA")))
cek("L10 'promo' dan 'bayar' tidak lagi ada di KATA_HARGA",
    "promo" not in _pre_src.split("const KATA_HARGA")[1].split("\n")[0]
    and "bayar" not in _pre_src.split("const KATA_HARGA")[1].split("\n")[0])


# ===========================================================================
bagian("M. PROMPT v3.6 — aturan harga & pendalaman pain point")
# ===========================================================================
_sp = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]

cek("M1  prefix '=' (expression mode) dipertahankan", _sp.startswith("="))
cek("M2  enam ekspresi {{ }} tetap utuh",
    len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 6,
    str(len(_re.findall(r"\{\{[^}]+\}\}", _sp))))
cek("M3  # HARGA melarang angka saat kata harga milik orang lain",
    "milik orang lain bukan pertanyaan untukku" in _sp)
cek("M4  # HARGA menyuruh menahan angka saat ragu",
    "Kalau ragu, jangan sebut angka" in _sp)
cek("M5  MENGGALI punya pendalaman pain point sekali",
    "Sekali masalah utamanya keluar" in _sp and "sekali saja, jangan diulang" in _sp)
cek("M6  pendalaman menanyakan AKIBAT, bukan 'ada kendala lain?'",
    "AKIBATNYA" in _sp)
cek("M7  spek pain_points menyebut pemisah titik koma",
    "dipisah titik koma" in _sp)
cek("M8  spek pain_points melarang mengulang masalah_utama",
    "JANGAN mengulang isi masalah_utama" in _sp)
cek("M9  suntingan tangan di n8n live ikut tersalin (tidak tertimpa)",
    "kalau boleh tau nama usahanya apa ya kak?." in _sp)
cek("M10 larangan harga di kalimat tawaran deck (v3.5) tidak hilang",
    "JANGAN menempelkan harga pada tawaran ini" in _sp)
cek("M11 pain_points tetap ada di daftar field [DECK_REQUEST]",
    "\n  pain_points: ...\n" in _sp)

# --- pecah_pain ASLI dari buat_deck.py: buktikan ';' menghasilkan >2 poin ---
_bd = os.path.join(os.path.dirname(DIR), "deck", "buat_deck.py")
if os.path.exists(_bd):
    with open(_bd, encoding="utf-8") as _f:
        _src_bd = _f.read()
    _m = _re.search(r"^def pecah_pain\(d\):.*?(?=\n(?:def |# |@|\Z))",
                    _src_bd, _re.S | _re.M)
    cek("M12 fungsi pecah_pain ditemukan di buat_deck.py", _m is not None)
    if _m:
        _ns = {}
        exec(_m.group(0), _ns)
        _pecah = _ns["pecah_pain"]

        # perilaku LAMA: pain_points satu kalimat -> selalu tepat 2 poin
        _lama = _pecah({"masalah_utama": "kewalahan balas chat saat promo",
                        "pain_points": "chat numpuk saat fokus ke hal lain"})
        cek("M13 satu kalimat pain_points = hanya 2 poin (gejala lama)",
            len(_lama) == 2, str(len(_lama)))

        # perilaku BARU: dipisah ';' -> lebih dari 2 poin, sampai 6
        _baru = _pecah({"masalah_utama": "kewalahan balas chat saat promo",
                        "pain_points": "ada calon murid yang kelewat nggak dibalas; "
                                       "chat masuk tengah malam nggak keurus; "
                                       "jawaban beda-beda tiap kali ditanya"})
        cek("M14 pain_points dipisah ';' menghasilkan 4 poin", len(_baru) == 4,
            str(len(_baru)))
        cek("M15 masalah_utama tetap jadi poin pertama",
            _baru[0]["judul"].startswith("kewalahan balas chat"))
        _enam = _pecah({"masalah_utama": "a", "pain_points": ";".join("bcdefgh")})
        cek("M16 batas atas 6 poin dihormati", len(_enam) == 6, str(len(_enam)))
else:
    cek("M12 buat_deck.py ditemukan", False, _bd)


'''

ANCHOR = ('# ===========================================================================\n'
          'print()\n'
          'print("=" * 72)\n'
          'print("RINGKASAN UAT")')
assert teks.count(ANCHOR) == 1, "anchor ringkasan tidak tunggal"
teks = teks.replace(ANCHOR, BARU.lstrip("\n") + ANCHOR, 1)

# --- 3. perbarui checklist UAT manual ------------------------------------
LAMA_CL = '''    "Cek kolom STATS.last_bot_reply terisi teks balasan terakhir.",
'''
BARU_CL = '''    "Cek kolom STATS.last_bot_reply terisi teks balasan terakhir.",
    "HARGA (insiden 2026-09-07) — ulang persis: 'mau tanya soal AI customer service' -> "
    "sebut bidang usaha -> lalu kirim 'biasanya pas lg promo buka kelas, ads itu pasti pd "
    "tanya hal yg sama, harga kuota apa aja yg didapet, sama jadwalnya kapan'. "
    "VIRA TIDAK BOLEH menyebut Rp3.000.000 / Rp5.000.000 di balasan itu.",
    "HARGA (kontrol) — di percakapan yang sama, lanjut 'kalau paket basic berapa ya?'. "
    "Di sini VIRA HARUS menyebut kisaran dan mengarahkan ke Steven.",
    "PAIN POINT — setelah prospek menyebut masalah utamanya, VIRA harus menanyakan "
    "AKIBATNYA satu kali (mis. 'ada yang sampai kelewat nggak kak?'), tidak dua kali.",
    "PAIN POINT — cek notif brief: baris 'Keluhan lain' harus berisi lebih dari satu "
    "keluhan dipisah ';', dan tidak boleh mengulang kalimat 'Masalah utama'.",
    "DECK — generate deck dari brief itu, pastikan slide Pain Points memuat 3+ poin.",
'''
assert teks.count(LAMA_CL) == 1, "anchor checklist tidak tunggal"
teks = teks.replace(LAMA_CL, BARU_CL, 1)

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(teks)

print("DST : %s  (%d baris)" % (os.path.basename(DST), teks.count("\n") + 1))
