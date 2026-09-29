# -*- coding: utf-8 -*-
"""
uji_konsistensi.py — membuktikan deck yang digenerate selalu sama.

Yang dijamin di sini:
  1. Deterministik      — brief yang sama menghasilkan HTML byte-per-byte identik, berapa kali pun
  2. Struktur terkunci  — urutan slide tidak bisa berubah diam-diam
  3. Gerbang data       — field kosong membuang slide, tidak pernah diisi tebakan
  4. Naskah tulisan tangan menang, dan tetap deterministik
  5. Penutur benar      — mockup diisi pertanyaan pelanggan, kutipan owner tidak bocor ke sana
  6. Slide UI flow ada  — dua slide The Flow tidak boleh hilang meski brief tipis
  7. Cover selalu ada   — brief tanpa nama_bisnis dapat cover generik, bukan kehilangan cover
  8. Nomor tidak bolong — slide bernomor ditulis ulang berurutan setelah penyaringan
  9. Slide wajib — kena aturan pembuangan = berhenti, bukan slidenya yang hilang

Jalankan: python uji_konsistensi.py   (keluar 1 kalau ada yang gagal)
"""
import hashlib
import io
import json
import os
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
import buat_deck as bd  # noqa: E402

BRIEF = os.path.join(DIR, "brief-contoh.json")
lolos, gagal = [], []


def cek(judul, syarat, detail=""):
    (lolos if syarat else gagal).append(judul)
    print("  %s  %s%s" % ("LOLOS" if syarat else "GAGAL", judul,
                          ("" if syarat else " — " + detail)))


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def jalankan(brief, tambahan=()):
    # Anak proses harus menulis UTF-8, bukan code page konsol Windows. Tanpa ini, satu
    # em dash di pesan generator membuat thread pembaca subprocess meledak
    # (UnicodeDecodeError) padahal generatornya sendiri berhasil. errors="replace" jadi
    # jaring terakhir supaya kegagalan encoding tidak pernah menyamar jadi kegagalan uji.
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "buat_deck.py", brief, "--html", *tambahan],
                       cwd=DIR, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r


print("=" * 68)
print("UJI KONSISTENSI GENERATOR DECK")
print("=" * 68)

# ── 1. Deterministik ──
print("\n[1] Hasil generate berulang")
r1 = jalankan(BRIEF)
h1 = sha(os.path.join(DIR, "keluaran", "akademi-arsi.html"))
r2 = jalankan(BRIEF)
h2 = sha(os.path.join(DIR, "keluaran", "akademi-arsi.html"))
cek("dua kali generate menghasilkan HTML identik", h1 == h2, "%s vs %s" % (h1[:12], h2[:12]))
cek("generate berhasil (exit 0)", r1.returncode == 0 and r2.returncode == 0,
    (r1.stderr or r2.stderr or "")[-300:])
print("       sha256 = %s" % h1[:32])

# ── 2. Struktur terkunci ──
print("\n[2] Kunci struktur")
tpl = io.open(os.path.join(DIR, "template.html"), encoding="utf-8").read()
kunci = json.load(io.open(os.path.join(DIR, "struktur.lock.json"), encoding="utf-8"))
try:
    bd.periksa_struktur(tpl)
    cek("template cocok dengan struktur.lock.json (%d slide)" % kunci["jumlah"], True)
except SystemExit as e:
    cek("template cocok dengan struktur.lock.json", False, str(e))

rusak = tpl.replace('data-id="comparison"', 'data-id="comparison-diubah"')
try:
    bd.periksa_struktur(rusak)
    cek("perubahan struktur TERDETEKSI dan dihentikan", False, "template rusak malah lolos")
except SystemExit:
    cek("perubahan struktur TERDETEKSI dan dihentikan", True)

# ── 3. Gerbang data ──
print("\n[3] Gerbang field kosong")
d = json.load(io.open(BRIEF, encoding="utf-8"))
d["nama_bisnis"] = "Uji Gerbang"
for f in ("masalah_utama", "pain_points", "pertanyaan_tersering", "aksi_utama",
          "volume_chat_harian", "deskripsi_bisnis"):
    d[f] = "belum disebut"
bolong = os.path.join(DIR, "_uji-gerbang.json")
json.dump(d, io.open(bolong, "w", encoding="utf-8"), ensure_ascii=False)
rb = jalankan("_uji-gerbang.json")
keluar_bolong = io.open(os.path.join(DIR, "keluaran", "uji-gerbang.html"), encoding="utf-8").read()
sisa = keluar_bolong.count('<section class="slide')
cek("brief kosong menyisakan 28 slide kerangka", sisa == 28, "ternyata %d" % sisa)

# Gambar disematkan sebagai data URI; blob base64-nya mengandung huruf apa saja
# ("Rp" ikut muncul di sana). Buang dulu, kalau tidak pemeriksaannya salah tuduh.
import re as _re  # noqa: E402

teks_terlihat = _re.sub(r'src="data:[^"]*"', 'src="[gambar]"', keluar_bolong)
for frasa in ("Rp", "jam per bulan", "chat per hari"):
    tidak_ada = frasa not in teks_terlihat.replace("IDR", "")
    cek("tidak ada angka tebakan ('%s') di deck kosong" % frasa, tidak_ada,
        (teks_terlihat[max(0, teks_terlihat.find(frasa) - 60):
                       teks_terlihat.find(frasa) + 60] if not tidak_ada else ""))

# ── 3b. Slide UI flow tidak boleh hilang ──
# Regresi 2026-09-04 (deck Sonic, brief 3/33): dua slide The Flow raib tanpa error.
# Slide 9 kena gerbang data-butuh="aksi_utama"; slide 12 kena aturan pembuangan yang
# mencari class="telepon", padahal percakapan slide itu bawaan template dan sama sekali
# tidak butuh data klien. Deck terkirim tanpa satu pun tampilan produk.
print("\n[3b] Slide UI flow di brief kosong")
SLIDE_FLOW = ("flow-ui", "flow-ui-aksi", "flow-ui-unknown", "flow-ui-followup",
              "flow-ui-premium-dashboard")
for sid in SLIDE_FLOW:
    cek("slide '%s' tetap ada" % sid, 'data-id="%s"' % sid in keluar_bolong)

for sid in SLIDE_FLOW[:4]:
    blok = _re.search(r'<section class="slide[^"]*" data-id="%s">.*?</section>' % sid,
                      keluar_bolong, _re.S)
    n = blok.group(0).count('class="gel ') if blok else -1
    cek("'%s' berisi gelembung percakapan contoh" % sid, n >= 2, "gelembung: %d" % n)

# ── 3c. Cover tanpa nama_bisnis ──
# Regresi 2026-09-06 (deck "tanpa-nama"): cover memakai data-butuh="nama_bisnis", jadi brief
# tanpa nama usaha kehilangan SELURUH cover — deck terkirim tanpa halaman pembuka dan tanpa
# satu pun penyebutan nama klien. Dua uji lama sama-sama menyetel nama_bisnis lebih dulu,
# jadi keadaan ini memang tidak pernah teruji.
print("\n[3c] Brief tanpa nama_bisnis")
d_nn = json.load(io.open(BRIEF, encoding="utf-8"))
d_nn["nama_bisnis"] = "belum disebut"
d_nn["volume_chat_harian"] = "belum disebut"   # tiru brief nyata: ikut mematikan #1 dan #3
json.dump(d_nn, io.open(bolong, "w", encoding="utf-8"), ensure_ascii=False)
r_nn = jalankan("_uji-gerbang.json")
h_nn = io.open(os.path.join(DIR, "keluaran", "tanpa-nama.html"), encoding="utf-8").read()
h_nn_terlihat = _re.sub(r'src="data:[^"]*"', 'src="[gambar]"', h_nn)

cek("generate tetap berhasil (exit 0)", r_nn.returncode == 0, (r_nn.stderr or "")[-300:])
cek("slide cover TETAP ADA", 'data-id="cover"' in h_nn)
cek("penanda cover 'The Future of' ada di keluaran", "The Future of" in h_nn_terlihat)
cek('blok "Disusun khusus untuk" dibuang, bukan diisi cadangan',
    "Disusun khusus untuk" not in h_nn_terlihat)
cek("peringatan COVER GENERIK tercetak", "COVER GENERIK" in (r_nn.stdout or ""),
    (r_nn.stdout or "")[-300:])

# Lima pemakaian nama_bisnis lain tidak boleh menyisakan kalimat menggantung / label kosong
cek("judul konteks tidak menggantung",
    "Yang aku tangkap soal bisnis kamu" in h_nn_terlihat,
    (_re.search(r'judul-bagian">(Yang aku tangkap[^<]*)', h_nn_terlihat) or ["(tidak ada)"])[0])
nama_wa = _re.findall(r'class="wa-nama">([^<]*)<', h_nn_terlihat)
inisial_wa = _re.findall(r'class="wa-foto">([^<]*)<', h_nn_terlihat)
cek("header WA mockup tidak kosong",
    len(nama_wa) == 6 and all(n.strip() for n in nama_wa), str(nama_wa))
cek("avatar WA mockup tidak kosong",
    len(inisial_wa) == 6 and all(i.strip() for i in inisial_wa), str(inisial_wa))
cek("label tenant dashboard tidak kosong",
    not _re.search(r'class="dash-tenant">\s*<', h_nn_terlihat),
    str(_re.findall(r'class="dash-tenant">([^<]*)<', h_nn_terlihat)))
cek("KPI dashboard tidak menampilkan strip kosong",
    "—/bln" not in h_nn_terlihat)

# ── 3d. Penomoran tidak boleh bolong ──
# Sebelumnya nomor #1..#4 statis di template; #1 dan #3 terbuang karena volume kosong,
# sehingga klien melihat "#2" lalu "#4" — terbaca seperti deck yang halamannya hilang.
print("\n[3d] Penomoran slide advantage")
nomor = _re.findall(r'<div class="adv-nomor">#(\d+)</div>', h_nn_terlihat)
cek("nomor advantage berurutan tanpa lompat",
    [int(x) for x in nomor] == list(range(1, len(nomor) + 1)),
    "yang muncul: %s" % nomor)
nomor_penuh = _re.findall(r'<div class="adv-nomor">#(\d+)</div>',
                          io.open(os.path.join(DIR, "keluaran", "akademi-arsi.html"),
                                  encoding="utf-8").read())
cek("brief lengkap tetap #1..#4", [int(x) for x in nomor_penuh] == [1, 2, 3, 4],
    "yang muncul: %s" % nomor_penuh)

# ── 3e. Slide wajib tidak bisa hilang diam-diam ──
print("\n[3e] Gerbang slide wajib")
kunci_lock = json.load(io.open(os.path.join(DIR, "struktur.lock.json"), encoding="utf-8"))
cek("cover terdaftar sebagai slide wajib", "cover" in kunci_lock.get("wajib", []),
    str(kunci_lock.get("wajib")))
cek("semua slide The Flow terdaftar wajib",
    set(SLIDE_FLOW) <= set(kunci_lock.get("wajib", [])),
    str(kunci_lock.get("wajib")))

# Template disabotase: cover diberi lagi data-butuh yang tidak terpenuhi.
# Yang benar bukan membuang covernya, tapi berhenti dan melapor.
tpl_sabotase = tpl.replace('<section class="slide terang" data-id="cover">',
                           '<section class="slide terang" data-id="cover" data-butuh="tidak_ada_field">')
data_uji = bd.turunan({k: bd.bersih(v) for k, v in
                       json.load(io.open(BRIEF, encoding="utf-8")).items()})
daftar_uji = {"pain_list": bd.pecah_pain(data_uji), "konteks": bd.pecah_konteks(data_uji)}
daftar_uji.update(bd.jendela_layar(bd.susun_adegan(data_uji, "tidak-ada-naskah")))
_h, _dibuang, diselamatkan = bd.render(tpl_sabotase, data_uji, daftar_uji,
                                       kunci_lock.get("wajib", []), kunci_lock.get("bernomor", []))
cek("slide wajib yang kena aturan pembuangan DILAPORKAN",
    [s for s, _ in diselamatkan] == ["cover"], str(diselamatkan))
cek("slide wajib TIDAK ikut terbuang", 'data-id="cover"' in _h)

# ── 4. Naskah tulisan tangan ──
print("\n[4] Naskah tulisan tangan")
os.makedirs(os.path.join(DIR, "naskah"), exist_ok=True)
uji_naskah = os.path.join(DIR, "naskah", "uji-gerbang.json")
json.dump({"gelembung": [
    {"arah": "masuk", "teks": "PENANDA NASKAH MANUAL"},
    {"arah": "keluar", "teks": "Balasan dari naskah."},
]}, io.open(uji_naskah, "w", encoding="utf-8"), ensure_ascii=False)
d["pertanyaan_tersering"] = "Ada slot minggu ini"
d["aksi_utama"] = "Booking"
json.dump(d, io.open(bolong, "w", encoding="utf-8"), ensure_ascii=False)
jalankan("_uji-gerbang.json")
isi = io.open(os.path.join(DIR, "keluaran", "uji-gerbang.html"), encoding="utf-8").read()
ha = sha(os.path.join(DIR, "keluaran", "uji-gerbang.html"))
jalankan("_uji-gerbang.json")
hb = sha(os.path.join(DIR, "keluaran", "uji-gerbang.html"))
cek("naskah tulisan tangan dipakai", "PENANDA NASKAH MANUAL" in isi)
cek("naskah tulisan tangan tetap deterministik", ha == hb)
os.remove(uji_naskah)

# ── 5. Penutur benar ──
print("\n[5] Penutur di mockup")
brief_asli = json.load(io.open(BRIEF, encoding="utf-8"))
data = bd.turunan({k: bd.bersih(v) for k, v in brief_asli.items()})
gel = bd.susun_adegan(data, "tidak-ada-naskah")["utama"]
kutipan_owner = [q.strip() for q in brief_asli["kutipan_asli"].split("|") if q.strip()]
masuk = [g["teks"] for g in gel if g["arah"] == "masuk"]
bocor = [k for k in kutipan_owner if any(k.lower() in m.lower() for m in masuk)]
cek("kutipan owner TIDAK muncul sebagai pesan pelanggan", not bocor, "bocor: %s" % bocor)
cek("pesan pelanggan berasal dari pertanyaan_tersering",
    any("kelas" in m.lower() or "daftar" in m.lower() for m in masuk), str(masuk))
cek("gelembung masuk terakhir bukan pertanyaan",
    not masuk[-1].strip().endswith("?") and len(masuk[-1]) < 40, masuk[-1])

# Brief tanpa pertanyaan_tersering: jatuh ke percakapan contoh, bukan daftar kosong.
# Contoh itu harus netral — tidak boleh membawa kutipan owner atau angka apa pun.
polos = dict(data)
polos["pertanyaan_tersering"] = ""
gel_polos = bd.susun_adegan(polos, "tidak-ada-naskah")["utama"]
masuk_polos = [g["teks"] for g in gel_polos if g["arah"] == "masuk"]
cek("brief tanpa pertanyaan_tersering tetap dapat gelembung", len(gel_polos) >= 4,
    "cuma %d" % len(gel_polos))
cek("percakapan contoh tidak membawa kutipan owner",
    not [k for k in kutipan_owner if any(k.lower() in m.lower() for m in masuk_polos)],
    str(masuk_polos))
cek("percakapan contoh tidak memuat angka",
    not _re.search(r"\d", " ".join(g["teks"] for g in gel_polos)),
    str([g["teks"] for g in gel_polos]))
# Kutipan mentah owner TIDAK boleh muncul di deck sama sekali — bukan di mockup
# pelanggan, bukan juga sebagai footer Pain Points seperti dulu.
_deck_penuh = io.open(os.path.join(DIR, "keluaran", "akademi-arsi.html"),
                      encoding="utf-8").read()
_bocor_deck = [k for k in kutipan_owner if k in _deck_penuh]
cek("kutipan mentah owner tidak dicetak di deck", not _bocor_deck, "bocor: %s" % _bocor_deck)
cek("penanda 'kata mereka sendiri' sudah tidak ada",
    "kata mereka sendiri" not in _deck_penuh)

# -- 5b. Kalimat tanya dari pertanyaan_tersering --
# `pertanyaan_tersering` isinya potongan kata, bukan kalimat. Ditempel apa adanya,
# gelembungnya berbunyi "Fee" - tidak ada pelanggan yang mengetik begitu.
print("\n[5b] Pembungkus kalimat tanya")
cek("potongan kata jadi kalimat tanya",
    bd.kalimat_tanya("Fee") == "Halo kak, mau tanya soal fee gimana ya?",
    bd.kalimat_tanya("Fee"))
cek("singkatan tetap kapital", bd.kalimat_tanya("KPR-nya").count("KPR") == 1,
    bd.kalimat_tanya("KPR-nya"))
cek("butir yang sudah kalimat tanya tidak dibungkus lagi",
    bd.kalimat_tanya("Apakah bisa dicicil?") == "Apakah bisa dicicil?",
    bd.kalimat_tanya("Apakah bisa dicicil?"))
cek("butir berawalan 'kalau' tidak jadi 'Kalau kalau'",
    "Kalau kalau" not in bd.kalimat_tanya("kalau slip gajinya belum ada", kedua=True),
    bd.kalimat_tanya("kalau slip gajinya belum ada", kedua=True))
cek("koma di dalam kurung tidak memecah butir",
    bd.pecah_pertanyaan("Fee, kesiapan tukang (all-in material, atau cari sendiri)") ==
    ["Fee", "kesiapan tukang (all-in material, atau cari sendiri)"],
    str(bd.pecah_pertanyaan("Fee, kesiapan tukang (all-in material, atau cari sendiri)")))

# Naskah tulisan tangan yang terlalu pendek: slide 10 jadi pengulangan slide 9, padahal
# kolom kanannya menyatakan datanya sudah tercatat. Slidenya tetap jadi, tapi harus berbunyi.
pendek = os.path.join(DIR, "naskah", "uji-gerbang.json")
json.dump({"gelembung": [{"arah": "masuk", "teks": "Halo kak?"},
                         {"arah": "keluar", "teks": "Halo kak."}]},
          io.open(pendek, "w", encoding="utf-8"), ensure_ascii=False)
d_pendek = json.load(io.open(BRIEF, encoding="utf-8"))
d_pendek["nama_bisnis"] = "Uji Gerbang"
json.dump(d_pendek, io.open(bolong, "w", encoding="utf-8"), ensure_ascii=False)
r_pendek = jalankan("_uji-gerbang.json")
cek("naskah terlalu pendek menghasilkan PERINGATAN",
    "PERINGATAN: naskah cuma 2 gelembung" in (r_pendek.stdout or ""),
    (r_pendek.stdout or "")[:400])
os.remove(pendek)


# -- 6. Render PDF sungguhan --
# Dua kegagalan 2026-09-04 sama-sama LOLOS di HTML dan baru kelihatan di PDF: slide UI flow
# terbuang, dan gelembung terakhir terpotong karena telepon kepenuhan. Uji HTML saja tidak
# cukup, jadi satu render PDF betulan ikut dijalankan memakai percakapan terpanjang yang
# didukung (8 gelembung, kalimat panjang).
print("")
print("[6] Render PDF sungguhan")
if bd.cari_chrome() is None:
    print("  (Chrome/Edge tidak ditemukan - dilewati)")
else:
    d_pdf = json.load(io.open(BRIEF, encoding="utf-8"))
    d_pdf["nama_bisnis"] = "Uji Pdf"
    json.dump(d_pdf, io.open(bolong, "w", encoding="utf-8"), ensure_ascii=False)

    EKOR = "lalu aku teruskan ke tim untuk dikonfirmasi jadwalnya."
    panjang = os.path.join(DIR, "naskah", "uji-pdf.json")
    json.dump({"gelembung": [
        {"arah": "masuk", "teks": "Halo, saya lihat iklannya di Instagram. Ada paket untuk keluarga?"},
        {"arah": "keluar", "teks": "Halo kak, ada. Biar aku carikan yang paling pas, ini untuk berapa orang ya?"},
        {"arah": "masuk", "teks": "berdua sama istri, umur 30an. kira-kira gimana ya?"},
        {"arah": "keluar", "teks": "Baik kak. Untuk usia 30-an berdua, pilihannya menyesuaikan manfaat yang diambil, jadi aku siapkan dulu daftarnya biar kakak bisa bandingkan."},
        {"arah": "masuk", "teks": "isinya apa aja?"},
        {"arah": "keluar", "teks": "Aku kirimkan ringkasan tiap pilihannya sekarang ya kak."},
        {"arah": "masuk", "teks": "oke, kalau mau tanya lebih detail gimana?"},
        {"arah": "keluar", "teks": "Paling enak dijelaskan langsung kak. Aku carikan waktu yang cocok, " + EKOR},
    ]}, io.open(panjang, "w", encoding="utf-8"), ensure_ascii=False)

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    rp = subprocess.run([sys.executable, "buat_deck.py", "_uji-gerbang.json"],
                        cwd=DIR, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", env=env)
    keluaran_pdf = rp.stdout or ""
    cek("render PDF berhasil (exit 0)", rp.returncode == 0, (rp.stderr or "")[-300:])
    cek("PERIKSA lolos - halaman, ukuran, dan semua teks wajib",
        "PERIKSA  : GAGAL" not in keluaran_pdf and "1440x810 pt" in keluaran_pdf,
        keluaran_pdf[-400:])
    cek("%d halaman untuk brief lengkap" % kunci_lock["jumlah"],
        "%d halaman" % kunci_lock["jumlah"] in keluaran_pdf, keluaran_pdf[-400:])

    # Gelembung terakhir naskah 8-baris harus benar-benar sampai ke PDF, bukan terpotong
    # diam-diam oleh overflow:hidden pada mockup telepon.
    try:
        from pypdf import PdfReader
        teks_pdf = _re.sub(r"\s+", " ", " ".join(
            (hal.extract_text() or "") for hal in PdfReader(
                os.path.join(DIR, "keluaran", "uji-pdf.pdf")).pages))
        cek("gelembung terakhir tidak terpotong di PDF", EKOR in teks_pdf,
            "ekor tidak ketemu")
    except ImportError:
        print("  (pypdf tidak ada - pemeriksaan ekor dilewati)")

    os.remove(panjang)
    for f in ("uji-pdf.pdf", "uji-pdf.html", "uji-pdf-pratinjau.html"):
        g = os.path.join(DIR, "keluaran", f)
        if os.path.exists(g):
            os.remove(g)

# -- bersih-bersih --
for f in (bolong, os.path.join(DIR, "keluaran", "uji-gerbang.html"),
          os.path.join(DIR, "keluaran", "uji-gerbang-pratinjau.html"),
          os.path.join(DIR, "keluaran", "tanpa-nama.html"),
          os.path.join(DIR, "keluaran", "tanpa-nama-pratinjau.html")):
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 68)
print("LOLOS : %d    GAGAL : %d" % (len(lolos), len(gagal)))
for g in gagal:
    print("   !! %s" % g)
print("=" * 68)
sys.exit(1 if gagal else 0)
