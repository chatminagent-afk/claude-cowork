# -*- coding: utf-8 -*-
"""
buat_deck.py — susun pitch deck VIRA dari satu baris REQUESTS, render jadi PDF.

Pakai:
    python buat_deck.py brief-contoh.json
    python buat_deck.py --wa 628xxxxxxxxxx          (baca dari VIRA Database.xlsx)
    python buat_deck.py brief-contoh.json --html    (berhenti di HTML, tidak render PDF)
    python buat_deck.py --wa 628xxx --lanjut-tanpa nama_bisnis
                                                    (field wajib kosong, SUDAH diizinkan Steven)

Prinsip yang tidak boleh dilanggar:
  * Angka yang tidak diketahui TIDAK PERNAH ditebak. Field kosong -> slide yang
    membutuhkannya dibuang, bukan diisi karangan.
  * Slide dibuang lewat atribut data-butuh di template, bukan lewat logika di sini.
  * nama_bisnis / industri / masalah_utama kosong -> generator BERHENTI sebelum menulis
    apa pun, kecuali Steven mengizinkan lewat --lanjut-tanpa (lihat KELENGKAPAN).
  * Skrip ini hanya menyusun & merender. Kalimat yang perlu ditulis (mockup
    percakapan, narasi pain point) datang dari brief atau dari LLM — bukan dikarang
    di sini.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(DIR, "template.html")
KELUARAN = os.path.join(DIR, "keluaran")
XLSX = os.path.join(os.path.dirname(DIR), "sheet", "VIRA Database.xlsx")

CHROME_KANDIDAT = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

KOSONG = {"", "-", "belum disebut", "belum diketahui", "none", "null"}


def bersih(v):
    s = str(v if v is not None else "").strip()
    return "" if s.lower() in KOSONG else s


# ─────────────────────────────────────────────────────────────
# Sumber data
# ─────────────────────────────────────────────────────────────
def dari_json(path):
    with open(path, encoding="utf-8") as f:
        return {k: bersih(v) for k, v in json.load(f).items()}


def dari_live(no_wa):
    """Baris REQUESTS langsung dari Google Sheets — tanpa mengunduh apa pun dulu."""
    import vira_sheet
    _, d = vira_sheet.cari_request(no_wa)
    d.pop("_baris", None)
    return {k: bersih(v) for k, v in d.items()}


def dari_xlsx(no_wa):
    import datetime
    import openpyxl

    # Berkas ini UNDUHAN, bukan sheet live. Kalau lupa diunduh ulang, deck disusun dari
    # data basi dan hasilnya beda dengan isi sheet — persis inkonsistensi yang mau dihindari.
    umur = (datetime.datetime.now()
            - datetime.datetime.fromtimestamp(os.path.getmtime(XLSX))).days
    if umur >= 1:
        print("PERINGATAN: 'VIRA Database.xlsx' terakhir diperbarui %d hari lalu." % umur)
        print("            Unduh ulang sheet-nya dulu kalau brief ini baru masuk.")

    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["REQUESTS"]
    baris = list(ws.iter_rows(values_only=True))
    header = [str(c).strip() if c else "" for c in baris[0]]
    def digits(s):
        # Sheets menyimpan no_wa sebagai angka, jadi openpyxl mengembalikan float:
        # 6285171701168.0 -> tanpa penanganan ini, ".0" ikut jadi digit "0" di ujung.
        if isinstance(s, float) and s.is_integer():
            s = int(s)
        return re.sub(r"\D", "", str(s or ""))
    for r in baris[1:]:
        row = dict(zip(header, r))
        if digits(row.get("no_wa")) == digits(no_wa):
            return {k: bersih(v) for k, v in row.items()}
    raise SystemExit("Tidak ada baris REQUESTS dengan no_wa %s" % no_wa)


# ─────────────────────────────────────────────────────────────
# Field turunan — dihitung, bukan dikarang
# ─────────────────────────────────────────────────────────────
FITUR_AKSI = [
    (("survey", "kunjungan", "viewing"), "Automated Survey Scheduling"),
    (("booking", "daftar", "pendaftaran", "reservasi", "les", "kelas"), "Automated Booking"),
    (("order", "pesan", "beli", "checkout"), "Automated Order Capture"),
    (("konsultasi", "assessment", "konsul"), "Automated Consultation Booking"),
]


MENIT_PER_CHAT = 5  # asumsi yang DICETAK di slide, bukan disembunyikan


def angka_pertama(teks):
    """Ambil bilangan pertama dari teks bebas ('10 chat per hari' -> 10, 'Rp4-6 juta' -> 4)."""
    m = re.search(r"\d[\d.,]*", str(teks or ""))
    if not m:
        return None
    try:
        return int(re.sub(r"[.,]", "", m.group(0)))
    except ValueError:
        return None


def turunan(d):
    aksi = d.get("aksi_utama", "").lower()
    nama_fitur = ""
    for kunci, label in FITUR_AKSI:
        if any(k in aksi for k in kunci):
            nama_fitur = label
            break
    d["nama_fitur_aksi"] = nama_fitur                 # kosong -> template pakai cadangan
    ind = d.get("industri", "")
    d["industri_frasa"] = (" — " + ind) if ind else ""

    # ── angka ROI. Kalau volume tidak bisa dibaca, SEMUA turunannya dikosongkan
    #    supaya slide yang memakainya dibuang, bukan diisi tebakan.
    vol = angka_pertama(d.get("volume_chat_harian"))
    if vol:
        jam = max(1, round(vol * MENIT_PER_CHAT / 60))
        d["volume_angka"] = str(vol)
        d["volume_x2"] = str(vol * 2)
        d["volume_bulanan"] = "{:,}".format(vol * 30).replace(",", ".")
        d["jam_harian"] = str(jam)
        d["jam_bulanan"] = str(jam * 30)
    else:
        for f in ("volume_angka", "volume_x2", "volume_bulanan", "jam_harian", "jam_bulanan"):
            d[f] = ""

    # biaya admin: pakai angka klien kalau ada, kalau tidak biarkan template pakai rentang umum
    biaya = d.get("biaya_admin_bulanan", "")
    d["biaya_admin_frasa"] = (
        "Di tempat kamu, satu admin ada di kisaran %s per bulan." % biaya if biaya else ""
    )

    ch = [c.strip() for c in re.split(r"[;,/]", d.get("channel", "")) if c.strip()]
    d["channel_utama"] = ch[0] if ch else ""

    # catatan implementasi — hanya dari fakta yang memang tertangkap
    catatan = []
    if d.get("data_tersedia"):
        catatan.append("Bahan pengetahuan: %s." % d["data_tersedia"])
    if d.get("integrasi_dibutuhkan"):
        catatan.append("Integrasi: %s." % d["integrasi_dibutuhkan"])
    if d.get("deadline"):
        catatan.append("Target mulai jalan: %s." % d["deadline"])
    d["catatan_implementasi"] = " ".join(catatan)

    # ── isian mockup WhatsApp
    bisnis = d.get("nama_bisnis", "").strip()
    d["inisial_bisnis"] = bisnis[0].upper() if bisnis else ""
    aksi_bersih = (d.get("aksi_utama") or "").strip().rstrip(".")
    d["aksi_besar"] = aksi_bersih.upper() if aksi_bersih else ""
    d["kolom_aksi"] = kolom_dari_aksi(aksi_bersih)

    # `kutipan_asli` TIDAK pernah dicetak di deck. Dulu kalimat mentah owner tampil
    # sebagai footer slide Pain Points ("... — kata mereka sendiri"); hasilnya
    # mengutip balik ketikan WhatsApp calon klien apa adanya, lengkap dengan singkatan
    # dan tanda kutip ganda. Tidak pantas untuk deck penawaran. Kutipan itu tetap
    # berguna di sheet — sebagai bahan Steven menulis naskah/<klien>.json.
    return d


def kolom_dari_aksi(aksi):
    """Nama kolom di mockup Google Sheets, diturunkan dari aksi_utama.

    Cuma label kolom pada gambar contoh — bukan skema sheet yang sebenarnya.
    """
    a = (aksi or "").lower()
    if "survey" in a or "kunjung" in a:
        return "unit_diminati"
    if "booking" in a or "konsultasi" in a or "jadwal" in a:
        return "keperluan"
    if "order" in a or "pesan" in a or "beli" in a:
        return "pesanan"
    return "kebutuhan"


LABEL_KONTEKS = [
    ("deskripsi_bisnis", "Yang dijalankan"),
    ("target_pelanggan", "Siapa yang chat"),
    ("channel", "Chat masuk lewat"),
    ("volume_chat_harian", "Volume chat"),
    ("siapa_balas_chat", "Yang membalas sekarang"),
    ("aksi_utama", "Yang dikejar dari chat"),
    ("sistem_sekarang", "Sistem sekarang"),
    ("sudah_pakai_chatbot", "Pernah pakai chatbot"),
]


def pecah_konteks(d):
    """Kartu 'yang aku tangkap' — hanya field yang benar-benar terisi, maksimal 6."""
    return [{"label": lab, "isi": d[f]} for f, lab in LABEL_KONTEKS if d.get(f)][:6]


def pecah_pain(d):
    """pain_points ';' -> daftar {judul, isi}. masalah_utama selalu jadi poin pertama."""
    item = []
    utama = d.get("masalah_utama", "")
    if utama:
        item.append(utama)
    item += [p.strip() for p in d.get("pain_points", "").split(";") if p.strip()]
    hasil = []
    for t in item[:6]:
        for pisah in ("—", " - ", ":"):
            if pisah in t:
                a, b = t.split(pisah, 1)
                hasil.append({"judul": a.strip(), "isi": b.strip()})
                break
        else:
            hasil.append({"judul": t.strip(), "isi": ""})
    return hasil



TANYA_AWAL = ("apakah", "berapa", "bagaimana", "gimana", "kapan", "dimana", "di mana",
              "kenapa", "bisakah", "bisa ", "ada ", "apa ", "boleh ")


def kalimat_tanya(frasa, kedua=False):
    """Ubah satu butir `pertanyaan_tersering` jadi kalimat tanya yang wajar.

    Brief menyimpan pertanyaan tersering sebagai POTONGAN KATA ("Fee",
    "termin pembayaran"), bukan kalimat utuh. Ditempel apa adanya ke gelembung chat,
    hasilnya balon berbunyi "Fee" — tidak ada pelanggan yang mengetik begitu, dan
    mockupnya langsung terbaca sebagai tempelan.

    Yang dibungkus di sini HANYA cara bertanyanya. Isinya tetap kata-kata dari brief;
    tidak ada fakta, angka, atau istilah baru yang ditambahkan.
    """
    t = re.sub(r"\s+", " ", str(frasa or "")).strip().rstrip(".")
    if not t:
        return ""
    if t.endswith("?"):
        return t[0].upper() + t[1:]
    if t.lower().startswith(TANYA_AWAL):
        return t[0].upper() + t[1:] + "?"
    # huruf pertama dikecilkan supaya menyatu di tengah kalimat — kecuali kalau
    # kata pertamanya singkatan (NPWP, KPR, DP), yang harus tetap kapital.
    # Huruf pertama dikecilkan supaya menyatu di tengah kalimat — kecuali kalau
    # diawali singkatan, yang harus tetap kapital. Diuji dari dua huruf pertama, bukan
    # dari kata utuh: "KPR-nya" bukan isupper() karena ada "-nya", jadi uji kata utuh
    # meloloskannya jadi "kPR-nya".
    if not re.match(r"[A-Z]{2}", t):
        t = t[0].lower() + t[1:]
    # Butir yang sudah diawali "kalau" tidak dibungkus lagi — kalau tidak, hasilnya
    # "Kalau kalau saya baru pindah kerja...". Terjadi pada butir yang memang sudah
    # berbentuk anak kalimat, dan itu wajar ditulis begitu di brief.
    if kedua:
        return (t[0].upper() + t[1:] + " gimana kak?") if t.lower().startswith(("kalau", "kalo")) \
               else "Kalau %s gimana kak?" % t
    return "Halo kak, mau tanya soal %s gimana ya?" % t


def pecah_pertanyaan(teks):
    """Pisah `pertanyaan_tersering` jadi butir-butir, koma di dalam kurung diabaikan.

    Perlu karena butir seperti "kesiapan tukang (all-in material, atau cari sendiri)"
    akan terbelah di tengah kalau dipisah dengan split biasa.
    """
    butir, kini, dalam = [], "", 0
    for c in str(teks or ""):
        if c in "([":
            dalam += 1
        elif c in ")]":
            dalam = max(0, dalam - 1)
        if c in ";,|" and dalam == 0:
            butir.append(kini)
            kini = ""
        else:
            kini += c
    butir.append(kini)
    return [b.strip() for b in butir if b.strip()]


# Jam tiap gelembung percakapan utama. Dicocokkan dengan jam di bar status tiap
# slide (13.52 dan 14.06 di template) supaya layar keduanya terbaca sebagai
# kelanjutan beberapa menit kemudian, bukan percakapan lain.
JAM_UTAMA = ["13.46", "13.46", "13.47", "13.48", "13.50", "13.51",
             "14.02", "14.03", "14.05", "14.05"]


def susun_adegan(d, slug_nama):
    """Semua gelembung untuk empat slide The Flow.

    Kembaliannya dict berisi percakapan `utama` plus tiga adegan pendek
    (`unknown`, `followup`, `call`). Yang dipotong jadi layar-layar telepon
    dikerjakan `jendela_layar`.

    Balasan VIRA sengaja hanya berbicara soal PROSES — tidak pernah menyebut harga,
    jadwal, stok, atau fakta apa pun yang tidak ada di brief. Yang boleh datang dari
    brief cuma pertanyaan PELANGGAN (`pertanyaan_tersering`) dan nama aksinya.
    """
    aksi = (d.get("aksi_utama") or "langkah berikutnya").strip().rstrip(".")
    aksi_kecil = aksi[0].lower() + aksi[1:] if aksi else aksi
    bisnis = (d.get("nama_bisnis") or "").strip()
    tim = ("Tim %s" % bisnis) if bisnis else "Tim kami"
    tim_kecil = ("tim %s" % bisnis) if bisnis else "tim kami"
    sumber = (d.get("sumber_prospek") or "").strip()

    umpan = pecah_pertanyaan(d.get("pertanyaan_tersering"))
    manual = os.path.join(DIR, "naskah", slug_nama + ".json")

    if os.path.exists(manual):
        with open(manual, encoding="utf-8") as f:
            isi = json.load(f)
        gel = isi.get("gelembung", isi) if isinstance(isi, dict) else isi
        utama = [dict(g) for g in gel
                 if g.get("arah") in ("masuk", "keluar") and bersih(g.get("teks"))]
        if not utama:
            raise SystemExit("naskah/%s.json ada tapi tidak berisi gelembung yang sah." % slug_nama)
        print("Naskah   : naskah/%s.json (tulisan tangan)" % slug_nama)
        # The Flow butuh percakapan yang cukup panjang untuk mengisi DUA layar: enam
        # gelembung di layar 1, lalu setidaknya dua gelembung baru di layar 2. Naskah
        # yang lebih pendek membuat slide 10 mengulang isi slide 9 dan tidak punya
        # gelembung "sudah aku catat" — padahal kolom kanannya menyatakan datanya sudah
        # tercatat. Slidenya tetap jadi, tapi keadaan itu harus berbunyi.
        if len(utama) < 8:
            print("PERINGATAN: naskah cuma %d gelembung. The Flow perlu minimal 8 supaya "
                  "layar 2" % len(utama))
            print("            benar-benar menjadi kelanjutan, bukan pengulangan layar 1.")
        utama = utama[:10]
    else:
        if umpan:
            print("Naskah   : disusun dari pertanyaan_tersering (%d pertanyaan)" % len(umpan))
        else:
            print("Naskah   : contoh umum — brief belum menyebut pertanyaan_tersering.")
            print("           Tulis naskah/%s.json kalau kalimatnya mau spesifik." % slug_nama)

        pembuka = ("Halo, saya lihat dari %s, mau tanya-tanya soal %s boleh kak?"
                   % (sumber, bisnis)) if (sumber and bisnis) else (
                  ("Halo kak, saya mau tanya-tanya soal %s boleh?" % bisnis) if bisnis
                  else "Halo kak, saya mau tanya-tanya dulu boleh?")

        utama = [
            {"arah": "masuk", "teks": pembuka},
            {"arah": "keluar",
             "teks": "Halo kak 😊 Boleh banget. Ada yang bisa aku bantu hari ini? "
                     "Kalau ada pertanyaan atau mau %s, tinggal tanya aja ya." % aksi_kecil},
            {"arah": "masuk",
             "teks": kalimat_tanya(umpan[0]) if umpan
                     else "Yang paling cocok buat kebutuhan saya yang mana ya kak?"},
            {"arah": "keluar",
             "teks": "Boleh kak, aku bantu jelasin. Biar jawabannya pas sama kebutuhan "
                     "kakak, aku perlu tahu sedikit soal rencananya dulu ya."},
        ]
        if len(umpan) > 1:
            utama += [
                {"arah": "masuk", "teks": kalimat_tanya(umpan[1], kedua=True)},
                {"arah": "keluar",
                 "teks": "Siap, itu aku catat. Kalau kakak sudah sreg, aku bisa langsung "
                         "bantu %s — mau sekarang kak?" % aksi_kecil},
            ]
        else:
            utama += [
                {"arah": "masuk", "teks": "Oke kak, kalau gitu gimana lanjutannya?"},
                {"arah": "keluar",
                 "teks": "Kalau kakak sudah sreg, aku bisa langsung bantu %s — "
                         "mau sekarang kak?" % aksi_kecil},
            ]
        utama += [
            {"arah": "masuk", "teks": "Boleh kak, sekalian aja sekarang."},
            {"arah": "keluar",
             "teks": "Siap 🙌 Aku minta beberapa data singkat ya kak — aku tanya "
                     "satu-satu biar nggak ribet."},
            {"arah": "masuk", "teks": "Oke kak."},
            {"arah": "keluar",
             "teks": "Sudah aku catat ya kak ✅ %s langsung dapat notifikasinya, "
                     "nanti dikonfirmasi lewat nomor ini." % tim},
        ]

    for i, g in enumerate(utama):
        g.setdefault("jam", JAM_UTAMA[i] if i < len(JAM_UTAMA) else JAM_UTAMA[-1])

    # Adegan pendek. Sengaja TIDAK memakai fakta klien — hanya bentuk percakapannya,
    # dan slidenya sudah berlabel "Ilustrasi tampilan".
    tanya_unknown = ("Kak, kalau kasus saya agak beda dari yang biasa, "
                     "itu tetap bisa dibantu nggak ya?")
    unknown = [
        {"arah": "masuk", "teks": tanya_unknown, "jam": "14.12", "sorot": "sorot"},
        {"arah": "keluar", "sorot": "sorot", "jam": "14.13",
         "teks": "Untuk yang ini aku perlu konfirmasi ke %s dulu ya kak, biar jawabannya "
                 "akurat dan nggak salah info. Mohon ditunggu sebentar, nanti kami kabari 🙏"
                 % tim_kecil},
    ]
    ringkas = tanya_unknown.replace("Kak, ", "")
    d["unknown_ringkas"] = ringkas[0].upper() + ringkas[1:]

    followup = [
        {"arah": "keluar", "jam": "09.20",
         "teks": "Halo Kak, masih berminat soal %s? Kalau mau, aku bantu lanjutin ya 😊"
                 % aksi_kecil},
        {"arah": "keluar", "jam": "09.21",
         "teks": "Halo Kak, sekadar mengingatkan aja. Kalau butuh info lagi, "
                 "tinggal kabari aku di sini ya."},
    ]
    call = [
        {"arah": "masuk", "jam": "15.37",
         "teks": "Ada nomor yang bisa saya hubungi langsung kak?"},
        {"arah": "keluar", "jam": "15.38", "sorot": "sorot",
         "teks": "Bisa banget kak, langsung telepon atau WA aja ke "
                 "0812-xxxx-xxxx ya 😊"},
    ]
    return {"utama": utama, "unknown": unknown, "followup": followup, "call": call}


def jendela_layar(adegan):
    """Potong percakapan jadi layar-layar telepon.

    Layar kedua sengaja TUMPANG TINDIH beberapa gelembung dengan layar pertama. Itu yang
    membuatnya terbaca sebagai chat yang sama yang di-scroll, bukan percakapan baru —
    persis cara deck Persada menampilkannya. Tumpang tindihnya juga mengisi layar sampai
    penuh; kalau cuma gelembung baru yang tampil, separuh atas telepon kosong dan
    mockupnya langsung terlihat sebagai gambar buatan.

    Yang ditandai `sorot` (kotak merah) HANYA gelembung terakhir — hasil akhirnya.
    Mengotaki semua gelembung baru membuat slidenya penuh kotak dan tidak ada yang
    menonjol, yang justru kebalikan dari gunanya.
    """
    utama = adegan["utama"]
    potong = 6 if len(utama) > 6 else len(utama)
    layar1 = [dict(g) for g in utama[:potong]]

    layar2 = [dict(g) for g in utama[max(0, potong - 4):]]
    if len(utama) > potong:
        layar2[-1]["sorot"] = "sorot"

    unknown = [dict(g) for g in adegan["unknown"]]
    for g in unknown[:-1]:
        g.pop("sorot", None)
    unknown = [dict(g) for g in utama[max(0, potong - 4):potong]] + unknown

    return {
        "chat1": layar1,
        "chat2": layar2,
        "chat_unknown": unknown,
        "chat_followup_awal": [dict(g) for g in utama[max(0, potong - 4):potong]],
        "chat_followup": adegan["followup"],
        # dua gelembung pembuka ikut ditampilkan supaya layarnya tidak melompong
        "chat_call": [dict(g) for g in utama[:2]] + adegan["call"],
    }


def kepadatan(*jendela):
    """Kelas CSS untuk mockup telepon: "padat" kalau layar terpadatnya panjang.

    Telepon punya tinggi tetap dengan overflow:hidden. Sejak gelembung ditumpuk dari
    bawah, yang terpotong adalah bagian ATAS — jadi kelebihan isi tidak lagi
    menghilangkan gelembung terakhir seperti pada naskah Alianz. Kelas ini tetap ada
    supaya percakapan panjang mengecil lebih dulu sebelum sampai terpotong.
    """
    skor = 0
    for gel in jendela:
        if gel:
            skor = max(skor, sum(len(g.get("teks", "")) for g in gel) + 55 * len(gel))
    return "padat" if skor > 780 else ""


def ekor_teks(s, n=30):
    """Potongan akhir kalimat, dinormalkan supaya bisa dicocokkan dengan ekstraksi PDF."""
    return re.sub(r"\s+", " ", str(s or "")).strip()[-n:]


# ─────────────────────────────────────────────────────────────
# Kunci struktur — urutan slide tidak boleh berubah diam-diam
# ─────────────────────────────────────────────────────────────
LOCK = os.path.join(DIR, "struktur.lock.json")


def muat_kunci():
    if not os.path.exists(LOCK):
        raise SystemExit("struktur.lock.json tidak ada — struktur deck tidak terkunci.")
    with open(LOCK, encoding="utf-8") as f:
        return json.load(f)


def periksa_struktur(tpl):
    kunci = muat_kunci()["urutan"]
    ada = re.findall(r'<section class="slide[^"]*" data-id="([^"]+)"', tpl)
    if ada == kunci:
        return
    hilang = [x for x in kunci if x not in ada]
    baru = [x for x in ada if x not in kunci]
    print("STRUKTUR : GAGAL — template menyimpang dari struktur.lock.json")
    if hilang:
        print("  hilang dari template : %s" % ", ".join(hilang))
    if baru:
        print("  tidak ada di kunci   : %s" % ", ".join(baru))
    if not hilang and not baru:
        print("  urutannya berubah:")
        for i, (a, b) in enumerate(zip(kunci, ada), 1):
            if a != b:
                print("    slide %d: kunci '%s' vs template '%s'" % (i, a, b))
    raise SystemExit(
        "Dihentikan. Kalau perubahan ini memang disengaja, perbarui struktur.lock.json."
    )


# ─────────────────────────────────────────────────────────────
# Mesin template
# ─────────────────────────────────────────────────────────────
RX_ULANG = re.compile(r"<!--ULANG:(\w+)-->(.*?)<!--/ULANG-->", re.S)
RX_JIKA = re.compile(r"<!--JIKA:(\w+)-->(.*?)<!--/JIKA-->", re.S)
RX_FIELD = re.compile(r"\{\{([\w.]+)(?:\|([^}]*))?\}\}")
RX_SLIDE = re.compile(r"<section class=\"slide[^\"]*\"[^>]*>.*?</section>", re.S)
RX_DEF = re.compile(r"<!--DEF:(\w+)-->(.*?)<!--/DEF-->", re.S)
RX_PAKAI = re.compile(r"<!--PAKAI:(\w+)-->")


def potongan(tpl):
    """<!--DEF:x-->…<!--/DEF--> menyimpan potongan, <!--PAKAI:x--> menyisipkannya.

    Rangka telepon (bar status, header, bar input) muncul di enam mockup. Disalin
    enam kali, perbaikan pada salah satunya pasti ada yang tertinggal — dan mockup
    yang tampilannya beda sendiri justru merusak kesan "ini WhatsApp beneran".
    """
    simpanan = {}

    def simpan(m):
        simpanan[m.group(1)] = m.group(2)
        return ""

    tpl = RX_DEF.sub(simpan, tpl)
    kurang = sorted(set(RX_PAKAI.findall(tpl)) - set(simpanan))
    if kurang:
        raise SystemExit("PAKAI menunjuk potongan yang tidak ada: %s" % ", ".join(kurang))
    return RX_PAKAI.sub(lambda m: simpanan[m.group(1)], tpl)


def isi_jika(teks, data):
    """<!--JIKA:f-->A<!--LAIN-->B<!--/JIKA-->  -> A kalau f terisi, B kalau tidak.

    Perlu karena {{f|cadangan}} hanya bisa mengganti NILAI, tidak bisa membuang kalimat
    di sekitarnya. Cover memakainya: tanpa nama_bisnis, seluruh blok "Disusun khusus untuk"
    hilang — bukan diganti "Disusun khusus untuk Bisnis Kamu", yang justru lebih buruk
    daripada tidak ada.
    """
    def ganti(m):
        nama, isi = m.group(1), m.group(2)
        ya, _, tidak = isi.partition("<!--LAIN-->")
        return ya if data.get(nama) else tidak

    return RX_JIKA.sub(ganti, teks)


def nomori_ulang(tpl, bernomor):
    """Tulis ulang #1..#n pada slide bernomor yang SELAMAT dari penyaringan.

    Nomornya statis di template. Waktu #1 dan #3 terbuang karena volume_chat_harian kosong,
    klien melihat "#2" lalu "#4" — terbaca seperti deck yang halamannya hilang.
    """
    urut = []
    for potongan in RX_SLIDE.findall(tpl):
        m = re.search(r'data-id="([^"]+)"', potongan)
        if m and m.group(1) in bernomor:
            urut.append(m.group(1))
    nomor = {sid: i for i, sid in enumerate(urut, 1)}
    if not nomor:
        return tpl

    def ganti(m):
        s = m.group(0)
        sid = re.search(r'data-id="([^"]+)"', s)
        if not sid or sid.group(1) not in nomor:
            return s
        return re.sub(r'(<div class="adv-nomor">)#\d+(</div>)',
                      lambda x: x.group(1) + "#%d" % nomor[sid.group(1)] + x.group(2),
                      s, count=1)

    return RX_SLIDE.sub(ganti, tpl)


def isi_field(teks, data, awalan=""):
    def ganti(m):
        nama, cadangan = m.group(1), m.group(2)
        if awalan and nama.startswith("."):
            nilai = data.get(nama[1:], "")
        elif nama.startswith("."):
            nilai = ""
        else:
            nilai = data.get(nama, "")
        return html.escape(str(nilai)) if nilai else (cadangan or "")

    return RX_FIELD.sub(ganti, teks)


def render(tpl, data, daftar, wajib=(), bernomor=()):
    # Slide mana yang BENAR-BENAR memakai gelembung dari brief. Dihitung di sini, sebelum
    # blok ULANG disubstitusi, karena setelah itu penandanya hilang.
    # Dulu penandanya dicari lewat class="telepon" — padahal slide Premium juga memakai
    # kelas itu dengan percakapan bawaan template yang tidak butuh data klien, jadi slide
    # Premium ikut terbuang tiap kali brief tidak punya gelembung.
    pakai_chat = {}
    for blok in RX_SLIDE.findall(tpl):
        butuh = RX_ULANG.findall(blok)
        butuh = [n for n, _ in butuh if n.startswith("chat")]
        m = re.search(r'data-id="([^"]+)"', blok)
        if butuh and m:
            pakai_chat[m.group(1)] = butuh

    def ulang(m):
        nama, blok = m.group(1), m.group(2)
        return "".join(isi_field(blok, it, awalan=".") for it in daftar.get(nama, []))

    tpl = RX_ULANG.sub(ulang, tpl)
    tpl = isi_jika(tpl, data)

    # buang slide yang fieldnya belum lengkap
    dibuang = []
    diselamatkan = []

    def saring(m):
        s = m.group(0)
        sid = re.search(r'data-id="([^"]+)"', s)
        sid = sid.group(1) if sid else ""
        alasan = []
        butuh = re.search(r'data-butuh="([^"]*)"', s)
        if butuh:
            alasan += [f.strip() for f in butuh.group(1).split(",") if not data.get(f.strip())]
        # slide yang memakai gelembung dari brief tidak layak tampil kalau gelembungnya
        # kosong — sekarang hanya bisa terjadi kalau naskah tulisan tangan dikosongkan
        if sid in pakai_chat and not any(daftar.get(n) for n in pakai_chat[sid]):
            alasan.append("gelembung percakapan")
        if not alasan:
            return s
        # Slide wajib TIDAK PERNAH dibuang diam-diam. Kalau salah satunya sampai ke sini,
        # yang salah briefnya atau templatenya — dan itu harus berbunyi, bukan
        # menghilangkan slidenya. Persis begini cover raib di deck 2026-09-06.
        if sid in wajib:
            diselamatkan.append((sid, alasan))
            return s
        dibuang.append((sid, alasan))
        return ""

    tpl = RX_SLIDE.sub(saring, tpl)
    tpl = nomori_ulang(tpl, bernomor)
    return sematkan_aset(isi_field(tpl, data)), dibuang, diselamatkan


def sematkan_aset(teks):
    """
    Ubah src="aset/x.jpg" jadi data URI. Perlu karena HTML keluar di keluaran/,
    sehingga path relatif ke aset/ tidak lagi benar — dan supaya PDF-nya mandiri,
    tidak bergantung file di sekitarnya.
    """
    import base64
    import mimetypes

    def ganti(m):
        nama = m.group(1)
        path = os.path.join(DIR, "aset", nama)
        if not os.path.exists(path):
            print("! aset tidak ada, dilewati: %s" % nama)
            return m.group(0)
        tipe = mimetypes.guess_type(path)[0] or "image/jpeg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return 'src="data:%s;base64,%s"' % (tipe, b64)

    return re.sub(r'src="aset/([^"]+)"', ganti, teks)


# ─────────────────────────────────────────────────────────────
def cari_chrome():
    for p in CHROME_KANDIDAT:
        if os.path.exists(p):
            return p
    p = shutil.which("chrome") or shutil.which("msedge")
    if p:
        return p
    return None


def ke_pdf(html_path, pdf_path):
    """Render ke berkas sementara lalu ganti. Mengembalikan path PDF baru, atau None.

    Kenapa lewat berkas sementara, bukan langsung ke pdf_path:
    kalau PDF lama masih terbuka di penampil PDF, Windows mengunci berkasnya dan Chrome
    tidak bisa menulis apa-apa. Versi lama kode ini hanya bertanya "berkasnya ada?" —
    dan berkas LAMA memang ada, jadi render yang gagal total dilaporkan sukses lengkap
    dengan ukurannya. Deck basi terkirim tanpa satu pun peringatan. Persis itu yang
    terjadi pada deck Sonic 2026-09-04.
    """
    chrome = cari_chrome()
    if not chrome:
        print("! Chrome/Edge tidak ditemukan — PDF dilewati. HTML tetap dibuat.")
        return None

    sementara = (pdf_path[:-4] if pdf_path.lower().endswith(".pdf") else pdf_path) + "-baru.pdf"
    if os.path.exists(sementara):
        try:
            os.remove(sementara)
        except OSError:
            pass
    cmd = [
        chrome, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",
        "--print-to-pdf=" + sementara, html_path,
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if r.returncode != 0 or not os.path.exists(sementara):
        print("! Render gagal (exit %d):" % r.returncode,
              (r.stderr or b"").decode("utf-8", "replace")[-600:])
        return None

    # PDF lama TIDAK pernah dihapus lebih dulu — kalau penggantian gagal, hasil render
    # baru tetap tersimpan dan Steven tinggal menutup penampil PDF lalu mengulang.
    try:
        os.replace(sementara, pdf_path)
        return pdf_path
    except OSError:
        print("! %s tidak bisa ditimpa — kemungkinan masih terbuka di penampil PDF."
              % os.path.basename(pdf_path))
        print("  Tutup PDF-nya lalu ulangi. Hasil render baru sementara ada di:")
        print("  %s" % sementara)
        return sementara


# ─────────────────────────────────────────────────────────────
# Gerbang kelengkapan brief (2026-09-18)
# ─────────────────────────────────────────────────────────────
# Keputusan Steven 2026-09-18, menggantikan keputusan 2026-09-06 ("cover generik masih
# layak kirim"): deck 17/09 terkirim sebagai tanpa-nama.pdf tanpa ada yang menghentikan.
#   BLOKIR     - generator berhenti SEBELUM menulis file apa pun. Lanjut hanya kalau Steven
#                mengizinkan field itu kosong, satu per satu: --lanjut-tanpa nama_bisnis,industri
#   PERINGATAN - field penentu slide lainnya. Tidak menghentikan, tapi dampaknya dilaporkan.
#   CATATAN    - pelengkap; template memakai kalimat umum sebagai gantinya.
# Dampak di bawah harus sesuai template (data-butuh / cadangan {{field|...}}) - diuji di
# uji_konsistensi.py bagian [7].
KELENGKAPAN = [
    # (field, tingkat, dampak ke deck, pertanyaan siap kirim ke prospek)
    ("nama_bisnis", "BLOKIR",
     "cover tanpa nama klien, mockup menulis 'Tim kami', berkas bernama tanpa-nama",
     "Nama usahanya apa kak? Biar Steven tulis di cover decknya."),
    ("industri", "BLOKIR",
     "cover tanpa bidang usaha, slide '#2 zero leaking profit' dibuang",
     "Usahanya bergerak di bidang apa kak?"),
    ("masalah_utama", "BLOKIR",
     "slide Pain Points dibuang",
     "Soal chat, yang paling bikin repot sekarang apa kak?"),
    ("deskripsi_bisnis", "PERINGATAN",
     "slide Konteks Bisnis dibuang",
     "Boleh cerita sedikit usahanya jualan apa saja, dan biasanya siapa yang pesan kak?"),
    ("aksi_utama", "PERINGATAN",
     "fitur & mockup memakai kata umum 'Booking' / 'langkah berikutnya'",
     "Dari chat yang masuk, yang paling dikejar apa kak: order, booking, atau konsultasi?"),
    ("volume_chat_harian", "PERINGATAN",
     "slide '#1 time freedom' & '#3 scalability' dibuang, dashboard tanpa angka",
     "Kira-kira sehari ada berapa chat masuk kak?"),
    ("pertanyaan_tersering", "PERINGATAN",
     "mockup percakapan memakai contoh umum, bukan pertanyaan pelanggannya",
     "Biasanya pelanggan paling sering nanya apa kak?"),
    ("alur_setelah_chat", "PERINGATAN",
     "slide The Flow memakai alur umum 'Chat masuk sampai ...'",
     "Dari chat pertama sampai jadi order, biasanya lewat langkah apa aja kak?"),
    ("target_pelanggan", "CATATAN", "slide #2 memakai 'Calon pelanggan' umum", ""),
    ("sumber_prospek", "CATATAN", "mockup memakai 'Instagram/Facebook' umum", ""),
    ("channel", "CATATAN", "dashboard memakai 'WhatsApp' umum", ""),
    ("biaya_admin_bulanan", "CATATAN", "slide #3 memakai kisaran biaya admin umum", ""),
]
FIELD_BLOKIR = tuple(f for f, t, _, _ in KELENGKAPAN if t == "BLOKIR")


def slug_berkas(data):
    """Nama berkas keluaran (tanpa ekstensi) — juga nama naskah/<slug>.json.

    Brief tanpa nama bisnis diberi 4 digit akhir no_wa: dulu semuanya 'tanpa-nama.pdf',
    jadi dua klien tanpa nama bisnis saling menimpa PDF-nya.
    """
    nama = bersih(data.get("nama_bisnis"))
    if nama:
        return re.sub(r"[^\w-]+", "-", nama).strip("-").lower()
    wa = re.sub(r"\D", "", str(data.get("no_wa") or ""))
    return ("tanpa-nama-" + wa[-4:]) if wa else "tanpa-nama"


def cek_kelengkapan(data, slug=None):
    """Daftar kekurangan brief: [{field, tingkat, dampak, tanya, isi}], urut BLOKIR dulu.

    Membaca brief mentah (dari sheet atau JSON), jadi nilainya dibersihkan di sini.
    volume_chat_harian dihitung kosong kalau tidak ada angkanya ('puluhan') — slide ROI
    tetap dibuang dalam keadaan itu.
    """
    hasil = []
    ada_naskah = bool(slug) and os.path.exists(os.path.join(DIR, "naskah", slug + ".json"))
    for field, tingkat, dampak, tanya in KELENGKAPAN:
        isi = bersih(data.get(field))
        if field == "volume_chat_harian" and isi and angka_pertama(isi) is None:
            hasil.append(dict(field=field, tingkat=tingkat, dampak=dampak, tanya=tanya,
                              isi="tidak ada angkanya: %r" % isi))
            continue
        if field == "pertanyaan_tersering" and ada_naskah:
            continue   # naskah tulisan tangan menang atas pertanyaan_tersering
        if field == "pertanyaan_tersering" and isi and len(pecah_pertanyaan(isi)) < 2:
            hasil.append(dict(field=field, tingkat="CATATAN", tanya="",
                              dampak="cuma 1 pertanyaan, mockup percakapan tipis", isi=isi))
            continue
        if not isi:
            hasil.append(dict(field=field, tingkat=tingkat, dampak=dampak, tanya=tanya, isi=""))
    urut = {"BLOKIR": 0, "PERINGATAN": 1, "CATATAN": 2}
    return sorted(hasil, key=lambda k: urut[k["tingkat"]])


def cetak_kelengkapan(kurang, izin=()):
    """Cetak laporan kelengkapan. Kembalikan field BLOKIR yang belum diizinkan Steven."""
    tahan = [k["field"] for k in kurang if k["tingkat"] == "BLOKIR" and k["field"] not in izin]
    n = {t: sum(1 for k in kurang if k["tingkat"] == t) for t in ("BLOKIR", "PERINGATAN", "CATATAN")}
    if not kurang:
        print("LENGKAP  : semua field penentu slide terisi")
        return tahan
    print("LENGKAP  : %d wajib kosong, %d peringatan, %d catatan"
          % (n["BLOKIR"], n["PERINGATAN"], n["CATATAN"]))
    for k in kurang:
        label = k["tingkat"]
        if label == "BLOKIR" and k["field"] in izin:
            label = "DIIZINKAN"
        print("  %-10s %-20s %s%s" % (label, k["field"], k["dampak"],
                                      (" (%s)" % k["isi"]) if k["isi"] else ""))
        if k["tanya"] and label != "DIIZINKAN":
            print("  %-10s %-20s tanya: \"%s\"" % ("", "", k["tanya"]))
    return tahan


def baca_izin(teks):
    """--lanjut-tanpa 'a,b' -> {'a','b'}. Hanya field BLOKIR yang boleh disebut."""
    izin = {f.strip() for f in str(teks or "").split(",") if f.strip()}
    salah = sorted(izin - set(FIELD_BLOKIR))
    if salah:
        raise SystemExit("--lanjut-tanpa hanya untuk field yang menghentikan build (%s), bukan: %s"
                         % (", ".join(FIELD_BLOKIR), ", ".join(salah)))
    return izin


def peringatan_cover(data, no_wa=None):
    """Deck tanpa nama bisnis — hanya bisa sampai sini dengan --lanjut-tanpa nama_bisnis.

    Dicetak PALING AKHIR supaya ini yang terbaca di layar sebelum generate-deck.bat
    berhenti di 'pause'. Sejak 2026-09-18 nama_bisnis kosong menghentikan generator
    (lihat KELENGKAPAN); peringatan ini tinggal pengingat bahwa Steven memang sengaja
    mengizinkan cover generik.
    """
    if data.get("nama_bisnis"):
        return
    print("")
    print("!! COVER GENERIK — nama_bisnis kosong%s."
          % (" (brief no_wa %s)" % no_wa if no_wa else ""))
    print('   Deck jadi, tapi tanpa baris "Disusun khusus untuk ...".')
    print("   Tanya nama bisnisnya, isi kolom nama_bisnis di REQUESTS, lalu ulangi.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief", nargs="?", help="file JSON berisi brief")
    ap.add_argument("--wa", help="ambil baris REQUESTS dengan no_wa ini")
    ap.add_argument("--xlsx", action="store_true",
                    help="paksa baca dari VIRA Database.xlsx, bukan sheet live")
    ap.add_argument("--html", action="store_true", help="berhenti di HTML")
    ap.add_argument("--bersih", action="store_true",
                    help="hapus HTML antara setelah PDF jadi, sisakan PDF saja")
    ap.add_argument("--lanjut-tanpa", default="",
                    help="field wajib yang SUDAH DIIZINKAN Steven untuk kosong, dipisah koma "
                         "(hanya: %s)" % ", ".join(FIELD_BLOKIR))
    a = ap.parse_args()
    izin = baca_izin(a.lanjut_tanpa)

    if a.wa:
        # Sheet live dulu; xlsx cuma cadangan. Sumber yang dipakai SELALU dicetak,
        # supaya tidak pernah ada deck yang diam-diam disusun dari data basi.
        if a.xlsx:
            print("SUMBER   : VIRA Database.xlsx (dipaksa --xlsx)")
            data = dari_xlsx(a.wa)
        else:
            try:
                data = dari_live(a.wa)
                print("SUMBER   : Google Sheets live (REQUESTS)")
            except SystemExit:
                raise
            except Exception as e:
                print("SUMBER   : sheet live GAGAL (%s: %s)" % (type(e).__name__, e))
                print("           jatuh ke VIRA Database.xlsx — periksa isinya sebelum kirim.")
                data = dari_xlsx(a.wa)
    elif a.brief:
        data = dari_json(a.brief)
    else:
        raise SystemExit("Beri file brief JSON atau --wa <nomor>")

    if a.wa and not data.get("no_wa"):
        data["no_wa"] = a.wa
    nama = slug_berkas(data)

    # gerbang nol: brief cukup lengkap? Dijalankan sebelum file apa pun ditulis.
    tahan = cetak_kelengkapan(cek_kelengkapan(data, nama), izin)
    if tahan:
        print("")
        print("DIHENTIKAN: %s kosong — deck tidak disusun." % ", ".join(tahan))
        print("  Lengkapi dulu di REQUESTS (tanyakan ke prospek, atau Steven yang mengisi), lalu ulangi.")
        print("  Kalau Steven sudah mengizinkan deck tanpa field itu: --lanjut-tanpa %s" % ",".join(tahan))
        sys.exit(2)

    data = turunan(data)

    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = potongan(f.read())   # rangka telepon disisipkan dulu
    periksa_struktur(tpl)          # gerbang pertama: urutan slide belum berubah
    kunci = muat_kunci()

    adegan = susun_adegan(data, nama)     # menulis juga data["unknown_ringkas"]
    daftar = {"pain_list": pecah_pain(data), "konteks": pecah_konteks(data)}
    daftar.update(jendela_layar(adegan))
    data["kelas_telepon"] = kepadatan(daftar["chat1"], daftar["chat2"])
    keluar, dibuang, diselamatkan = render(tpl, data, daftar,
                                           kunci.get("wajib", []), kunci.get("bernomor", []))

    # gerbang kedua: slide wajib tidak boleh sampai kena aturan pembuangan
    if diselamatkan:
        print("WAJIB    : GAGAL — slide wajib kena aturan pembuangan")
        for sid, alasan in diselamatkan:
            print("  !! %-30s butuh: %s" % (sid, ", ".join(alasan)))
        raise SystemExit(
            "Dihentikan. Isi field itu di briefnya, atau keluarkan slidenya dari "
            '"wajib" di struktur.lock.json kalau memang boleh hilang.')

    os.makedirs(KELUARAN, exist_ok=True)
    html_path = os.path.join(KELUARAN, nama + ".html")
    pdf_path = os.path.join(KELUARAN, nama + ".pdf")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(keluar)

    # lembar kontak: semua slide dikecilkan dalam satu halaman, untuk review cepat
    pratinjau = os.path.join(KELUARAN, nama + "-pratinjau.html")
    with open(pratinjau, "w", encoding="utf-8") as f:
        f.write(keluar + "\n<style>\n"
                " body{background:#555;display:flex;flex-wrap:wrap;gap:8px;"
                "align-content:flex-start;padding:8px}\n"
                " .slide{zoom:1 !important;transform:scale(.235);"
                "transform-origin:top left;margin:0 -1102px -620px 0;"
                "outline:1px solid #888}\n"
                "</style>\n")

    total = len(RX_SLIDE.findall(tpl))
    print("Brief    : %s (%s)" % (data.get("nama_bisnis") or "-", data.get("industri") or "-"))
    print("Slide    : %d dari %d" % (total - len(dibuang), total))
    for sid, alasan in dibuang:
        print("  dibuang: %-34s <- kosong: %s" % (sid, ", ".join(alasan)))
    print("HTML     : %s" % html_path)
    print("Pratinjau: %s" % pratinjau)

    if a.html:
        peringatan_cover(data, a.wa)
        if izin:
            print("DIIZINKAN KOSONG oleh Steven: %s" % ", ".join(sorted(izin)))
        return
    hasil = ke_pdf(html_path, pdf_path)
    lolos = True
    if hasil:
        print("PDF      : %s (%.0f KB)" % (hasil, os.path.getsize(hasil) / 1024))
        # Gelembung TERAKHIR tiap layar telepon ikut diperiksa. Dia yang paling bawah,
        # jadi dia yang pertama hilang kalau teleponnya kepenuhan — dan isinya beda tiap
        # klien, sehingga tidak bisa dititipkan ke daftar WAJIB_ADA yang statis.
        ekor = [ekor_teks(daftar[n][-1]["teks"])
                for n in ("chat1", "chat2", "chat_unknown", "chat_followup", "chat_call")
                if daftar.get(n)]
        # Nama bisnis ikut jadi teks wajib HANYA kalau briefnya memang punya. Ini yang
        # menangkap keadaan "cover ada tapi namanya raib" tanpa ikut memerahkan deck
        # yang sengaja bercover generik.
        if data.get("nama_bisnis"):
            ekor.append(data["nama_bisnis"])
        lolos = periksa_pdf(hasil, total - len(dibuang), ekor)
        # --bersih: hanya menghapus dua berkas yang DIBUAT RUN INI, tidak pernah
        # menyentuh keluaran klien lain. PDF-nya sudah jadi dan sudah diperiksa.
        # HTML dipertahankan kalau PDF belum berhasil menempati namanya yang benar.
        if a.bersih and hasil == pdf_path:
            for f in (html_path, pratinjau):
                try:
                    os.remove(f)
                except OSError:
                    pass
            print("BERSIH   : HTML antara dihapus, sisa PDF saja")

    peringatan_cover(data, a.wa)
    if izin:
        print("DIIZINKAN KOSONG oleh Steven: %s" % ", ".join(sorted(izin)))
    if not lolos:
        raise SystemExit(1)


# Slide punya tinggi tetap dan overflow:hidden, jadi isi yang kepanjangan akan
# TERPOTONG DIAM-DIAM — pernah terjadi: baris terakhir tabel harga hilang.
# Kalimat-kalimat ini wajib muncul di PDF akhir.
WAJIB_ADA = [
    "The Future of",         # slide 1 — cover. Muncul tepat sekali di seluruh template.
                             # BUKAN "Disusun khusus untuk": blok itu memang hilang kalau
                             # nama_bisnis kosong, jadi tidak bisa jadi bukti cover ada.
    "The Flow",              # slide 9 — sempat hilang diam-diam untuk brief tipis
    "Notify Tim (Human)",    # slide 10 — layar kedua percakapan
    "MENUNGGU JAWABAN",      # slide 11 — Unknown FAQ
    "2 PESAN BELUM DIBACA",  # slide 12 — Follow Up & Call Redirection
    "VIRA Dashboard",        # slide 13 — ikut terbuang karena aturan class="telepon"
    "Aku jelaskan ya.",      # gelembung terbawah slide 13 — penanda telepon tidak terpotong
    "One-Time System Setup & Integration",
    "Global Language Capability",
    "Send Media",
    "Analyze Photo",
    "IDR 999.000/month",
    "100% Satisfaction",
]


def periksa_pdf(path, jumlah_slide, wajib_tambahan=()):
    try:
        from pypdf import PdfReader
    except ImportError:
        print("  (pypdf tidak ada — pemeriksaan PDF dilewati)")
        return True
    r = PdfReader(path)
    # Dirapikan dulu: pemenggalan baris hasil ekstraksi berbeda dengan yang ada di
    # HTML, jadi mencari kalimat pada teks mentah bisa salah lapor "hilang".
    teks = re.sub(r"\s+", " ",
                  "\n".join((p.extract_text() or "") for p in r.pages))
    kotak = r.pages[0].mediabox
    ukuran = (round(float(kotak.width)), round(float(kotak.height)))

    masalah = []
    if len(r.pages) != jumlah_slide:
        masalah.append("halaman PDF %d, slide %d" % (len(r.pages), jumlah_slide))
    if ukuran != (1440, 810):
        masalah.append("ukuran halaman %sx%s pt, seharusnya 1440x810" % ukuran)
    hilang = [k for k in list(WAJIB_ADA) + list(wajib_tambahan) if k not in teks]
    if hilang:
        masalah.append("teks wajib tidak muncul (kemungkinan terpotong): " + "; ".join(hilang))

    if masalah:
        print("PERIKSA  : GAGAL")
        for m in masalah:
            print("  !! %s" % m)
        return False
    print("PERIKSA  : %d halaman, %sx%s pt, semua teks wajib ada"
          % ((len(r.pages),) + ukuran))
    return True


if __name__ == "__main__":
    main()
