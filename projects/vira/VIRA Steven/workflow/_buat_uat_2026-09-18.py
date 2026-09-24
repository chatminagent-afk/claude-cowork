# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-18.py - turunkan _uat_2026-09-18.py dari harness _uat_2026-09-15.py.

Harness v3.9 diarahkan ulang ke v3.10. Seksi A-Q dan S ikut jalan sebagai regresi, dengan
penyesuaian yang memang disengaja patch 2026-09-18:
  - O1  : tabel jendela giliran diganti (nama usaha di perkenalan + tanya ulang di pesan 2,
          bidang 2-6, masalah 2-8, jumlah chat 3-10)
  - Q4/Q5/Q7/Q13/Q15 : kalimat prompt yang memang diganti
  - S9  : baris uji diberi nama_bisnis supaya tetap menguji bidang usaha
Seksi baru:
  T. UJI 2026-09-17 - nama usaha di perkenalan, jawaban gabungan, nama bocor, balasan ringkas
  R. BEDAH REGRESI v3.10 vs export live - 86 node identik; di 3 node hanya wilayah sasaran

Jalankan: python _buat_uat_2026-09-18.py   (lalu: python _uat_2026-09-18.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-15.py")
DST = os.path.join(DIR, "_uat_2026-09-18.py")

with io.open(SRC, encoding="utf-8") as f:
    teks = f.read()


def ganti(lama, baru):
    global teks
    assert teks.count(lama) == 1, "anchor tidak tunggal (%d): %r" % (teks.count(lama), lama[:90])
    teks = teks.replace(lama, baru, 1)


def ganti_blok(awal, akhir, baru):
    """Ganti teks dari `awal` sampai dan termasuk `akhir` (keduanya harus tunggal)."""
    global teks
    assert teks.count(awal) == 1 and teks.count(akhir) == 1, (teks.count(awal), teks.count(akhir), awal[:60])
    i = teks.index(awal)
    j = teks.index(akhir, i) + len(akhir)
    teks = teks[:i] + baru + teks[j:]


# --- 1. arahkan ke v3.10 -------------------------------------------------
ganti('WF = os.path.join(DIR, "2026-09-15-VIRA-Personal-Main-v3.9.json")',
      'WF = os.path.join(DIR, "2026-09-18-VIRA-Personal-Main-v3.10.json")')
ganti("_uat_2026-09-15.py — UAT perilaku untuk 2026-09-15-VIRA-Personal-Main-v3.9.json.\n\n"
      "Diturunkan dari _uat_2026-09-14.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-15.py, lalu jalankan ulang). Seksi A-Q ikut jalan sebagai regresi;\n"
      "seksi S baru untuk insiden 2026-09-15, seksi R membedah v3.9 terhadap v3.8.",
      "_uat_2026-09-18.py — UAT perilaku untuk 2026-09-18-VIRA-Personal-Main-v3.10.json.\n\n"
      "Diturunkan dari _uat_2026-09-15.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-18.py, lalu jalankan ulang). Seksi A-Q dan S ikut jalan sebagai regresi;\n"
      "seksi T baru untuk uji Steven 2026-09-17, seksi R membedah v3.10 terhadap export live.")
ganti("Jalankan: python _uat_2026-09-15.py", "Jalankan: python _uat_2026-09-18.py")

# --- 2. detektor: kalimat gabungan nama + nama usaha ----------------------
ganti('        ("Usahanya di bidang apa kak? Sehari ada berapa chat masuk?", ["industri", "volume_chat"])]:',
      '        ("Usahanya di bidang apa kak? Sehari ada berapa chat masuk?", ["industri", "volume_chat"]),\n'
      '        ("Btw boleh tau nama kakak siapa, dan nama usahanya apa?", ["nama_bisnis", "nama_lengkap"]),\n'
      '        ("Nama adminnya siapa, dan nama brandnya apa?", ["nama_bisnis"])]:')

# --- 3. O1: tabel jendela giliran v3.10 -----------------------------------
ganti_blok(
    'for baris, harap, judul in [\n        ({"greeting_sent": ""}, "namanya", "pesan perkenalan -> tanya nama"),',
    '    cek("O1  %s" % judul, ok, str(g))\n',
    r'''_NB = {"nama_bisnis": "Kopi Senja"}   # nama usaha sudah ada -> jalur galian biasa
for baris, harap, judul in [
        ({"greeting_sent": ""}, "namanya dan nama usahanya", "pesan perkenalan -> tanya nama DAN nama usaha"),
        ({"greeting_sent": "", "nama_lengkap": "Budi"}, "nama usahanya — tanyakan di",
         "perkenalan, nama sudah ada -> tanya nama usaha saja"),
        ({"greeting_sent": "", "nama_lengkap": "Budi", "nama_bisnis": "Kopi Senja"}, None,
         "perkenalan, keduanya sudah ada -> tidak menggali apa pun"),
        ({"greeting_sent": "Y", "Counter": "1"}, "nama usahanya — tanya ulang", "giliran 2, nama usaha kosong -> tanya ulang"),
        (dict({"greeting_sent": "Y", "Counter": "1"}, **_NB), "bidang usahanya", "giliran 2, nama usaha ada -> bidang usaha"),
        (dict({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": "Usahanya di bidang apa kak?"}, **_NB), None,
         "bidang usaha baru ditanyakan & belum dijawab -> jeda satu balasan"),
        ({"greeting_sent": "Y", "Counter": "3"}, "bidang usahanya", "giliran 4 -> jendela tanya ulang habis, bidang usaha"),
        ({"greeting_sent": "Y", "Counter": "5"}, "bidang usahanya", "giliran 6 -> bidang usaha masih dalam jendela (v3.10: 2-6)"),
        ({"greeting_sent": "Y", "Counter": "6"}, "masalah terbesarnya", "giliran 7 -> jendela bidang usaha habis, lanjut masalah"),
        (dict({"greeting_sent": "Y", "Counter": "2", "industri": "sipil"}, **_NB), "masalah terbesarnya", "bidang usaha ada -> masalah"),
        (dict({"greeting_sent": "Y", "Counter": "1", "industri": "sipil"}, **_NB), "masalah terbesarnya",
         "giliran 2, nama usaha & bidang sudah ada -> langsung masalah"),
        ({"greeting_sent": "Y", "Counter": "4", "industri": "sipil",
          "last_bot_reply": "Soal chat, yang paling bikin repot sekarang apa kak?"}, None, "masalah baru ditanyakan -> jeda"),
        ({"greeting_sent": "Y", "Counter": "7", "industri": "sipil"}, "masalah terbesarnya",
         "giliran 8 -> masalah masih dalam jendela (v3.10: 2-8)"),
        ({"greeting_sent": "Y", "Counter": "8", "industri": "sipil"}, None, "giliran 9 -> jendela masalah habis"),
        ({"greeting_sent": "Y", "Counter": "3", "industri": "sipil", "masalah_utama": "x"}, "kira-kira berapa chat",
         "masalah ada -> jumlah chat"),
        ({"greeting_sent": "Y", "Counter": "9", "industri": "sipil", "masalah_utama": "x"}, "kira-kira berapa chat",
         "giliran 10 -> jumlah chat masih dalam jendela (v3.10: 3-10)"),
        ({"greeting_sent": "Y", "Counter": "10", "industri": "sipil", "masalah_utama": "x"}, None,
         "giliran 11 -> jendela jumlah chat habis"),
        ({"greeting_sent": "Y", "Counter": "3", "industri": "sipil", "masalah_utama": "x", "volume_chat": "20"}, None,
         "semua terisi -> tidak menggali"),
        (dict({"greeting_sent": "Y", "Counter": "1", "nama_lengkap": ""}, **_NB), "bidang usahanya",
         "nama tidak ditanya lagi di luar perkenalan"),
        ({"greeting_sent": "Y", "Counter": ""}, None, "Counter kosong (kontak import) + sudah disapa -> tidak menggali")]:
    g, d = galian(**baris)
    ok = (g is None) if harap is None else (g is not None and g.startswith(harap))
    cek("O1  %s" % judul, ok, str(g))
''')

# --- 4. Q: kalimat prompt yang memang diganti -----------------------------
ganti('cek("Q4  nama ditanya SEKALI di perkenalan, tidak diulang", "Namanya kutanyakan SEKALI, di pesan perkenalan" in _sp\n'
      '    and "jangan ditanyakan lagi" in _sp)',
      'cek("Q4  nama ditanya SEKALI di perkenalan, tidak diulang", "Namanya kutanyakan SEKALI: kalau dia tidak menjawab" in _sp\n'
      '    and "jangan ditanyakan lagi" in _sp)')
ganti('cek("Q5  PERKENALAN tetap intro biasa + tanya nama", "tutup dengan menanyakan namanya" in _sp\n'
      '    and "perkenalan seperti di atas, jawaban singkat kalau dia bertanya, lalu pertanyaan nama" in _sp)',
      'cek("Q5  PERKENALAN tetap intro biasa + tanya nama & nama usaha",\n'
      '    "tutup dengan SATU kalimat pendek yang menanyakan namanya" in _sp\n'
      '    and "jawaban singkat kalau dia bertanya, lalu pertanyaan nama dan nama usaha" in _sp.replace("\\n", " "))')
ganti('    "Nama, bidang usaha, masalah utama, dan jumlah chat per hari hanya kutanyakan lewat baris itu" in _sp)',
      '    "Nama, nama usaha, bidang usaha, masalah utama, dan jumlah chat per hari hanya kutanyakan lewat baris itu" in _sp)')
ganti('_harap = [["industri"], ["masalah_utama"], ["volume_chat"]]\n'
      'cek("Q13 tiga contoh kalimat galian ditemukan", len(_cth) == 3, str(_cth))',
      '_harap = [["nama_bisnis"], ["industri"], ["masalah_utama"], ["volume_chat"]]\n'
      'cek("Q13 empat contoh kalimat galian ditemukan", len(_cth) == 4, str(_cth))')
ganti('for _k in [k for k in _re.findall(r\'"([^"]*siapa[^"]*)"\', _bag) if len(k.split()) >= 3]:\n'
      '    cek("Q15 contoh tanya nama \'%s\' terbaca sebagai nama_lengkap" % _k, detek(_k) == ["nama_lengkap"])',
      '_q15 = [k for k in _re.findall(r\'"([^"]*siapa[^"]*)"\', _bag) if len(k.split()) >= 3]\n'
      'cek("Q15 bagian NAMA punya contoh kalimat tanya nama", len(_q15) >= 1, str(_q15))\n'
      'for _k in _q15:\n'
      '    _hq = ["nama_bisnis", "nama_lengkap"] if "nama usaha" in _k else ["nama_lengkap"]\n'
      '    cek("Q15 contoh tanya nama \'%s\' terbaca sebagai %s" % (_k, _hq), detek(_k) == _hq, str(detek(_k)))')

# --- 5. S9: tetap menguji bidang usaha (nama usaha sudah ada) --------------
ganti('    g, _ = galian2({"greeting_sent": "Y", "Counter": "1"}, pesan)\n'
      '    cek("S9  \'%s\' (tidak bertanya) -> galian bidang usaha jalan" % pesan,',
      '    g, _ = galian2({"greeting_sent": "Y", "Counter": "1", "nama_bisnis": "Kopi Senja"}, pesan)\n'
      '    cek("S9  \'%s\' (tidak bertanya) -> galian bidang usaha jalan" % pesan,')

# --- 5b. K5: n8n tidak mengekspor parameter yang bernilai default ----------
# Export live 2026-09-16 tidak memuat "model" di DeepSeek Personal Summary karena nilainya
# sama dengan default paket n8n-nodes-deepseek-thinking 0.3.1 (deepseek-v4-flash).
ganti('cek("K5  model ringkasan ke Steven = deepseek-v4-flash",\n'
      '    _sum.get("model") == "deepseek-v4-flash", str(_sum.get("model")))',
      '# n8n tidak mengekspor parameter bernilai default; default paket = deepseek-v4-flash\n'
      'cek("K5  model ringkasan ke Steven = deepseek-v4-flash (eksplisit atau default node)",\n'
      '    _sum.get("model", "deepseek-v4-flash") == "deepseek-v4-flash", str(_sum.get("model")))')

# --- 6. seksi T baru + R baru, menggantikan R lama ------------------------
BARU = r'''# ===========================================================================
bagian("T. UJI 2026-09-17 — nama usaha di perkenalan, jawaban gabungan, balasan ringkas")
# ===========================================================================
_sp = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]
_sp1 = _sp.replace("\n", " ")
PERKENALAN_BARU = ("Halo kak, aku Steven versi AI. Aku dibangun sama Steven pakai sistem yang sama yang dia "
                   "bikin untuk kliennya, namanya VIRA. Jadi kalau kakak penasaran hasilnya kayak apa, kakak "
                   "lagi ngobrol sama contohnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa?")
INTRO_1709 = ("Halo kak, salam kenal. Aku Steven versi AI, asisten yang dibangun Steven pakai sistem yang sama "
              "dengan yang dia tawarkan untuk kliennya, namanya VIRA. Jadi kalau kakak penasaran hasilnya seperti "
              "apa, kakak lagi ngobrol sama contohnya sekarang. Senang kakak sudah lihat website-nya. Boleh cerita "
              "dulu bisnis kakak di bidang apa, dan apa yang bikin kakak tertarik cari AI customer service? Btw, "
              "boleh tau namanya siapa kak?")
JAWAB_1709 = "Nadia kak, bisnis aku katering, chat suka numpuk pas malem"
BALAS_1709 = ("Salam kenal Nadia. Chat katering memang paling ramai pas malam hari, apalagi kalau orang baru "
              "pulang kerja dan mulai mikir pesanan. Kalau lagi numpuk gitu, biasanya yang paling bikin repot "
              "bagian mananya kak?")

# --- T1 prompt: perkenalan ---
_perk = _sp.split("# PERKENALAN")[1].split("\n# NAMA LAWAN BICARA")[0]
_m = _re.search(r'"(btw boleh tau nama kakak siapa, dan nama usahanya apa\?)"', _perk)
cek("T1  PERKENALAN memberi contoh SATU kalimat nama + nama usaha", _m is not None)
cek("T1b contoh itu terbaca detektor sebagai dua slot", _m and detek(_m.group(1)) == ["nama_bisnis", "nama_lengkap"],
    str(_m and detek(_m.group(1))))
cek("T2  'apa yang bikin dia tertarik' dibuang dari prompt", "apa yang bikin dia tertarik" not in _sp)
cek("T2b pesan perkenalan dilarang menanyakan hal lain (bidang, masalah, alasan tertarik)",
    "JANGAN menanyakan apa pun di pesan ini — bukan bidang usahanya, bukan masalahnya" in _sp1)
cek("T3  larangan lama menggabung nama + nama usaha sudah dihapus",
    "Jangan digabung dengan pertanyaan nama usaha" not in _sp and "Jangan dipecah" in _sp)
cek("T3b cara membaca jawaban gabungan dijelaskan (jenis usaha -> industri)",
    "Cara membaca jawabannya" in _sp and "itu `industri` — nama usahanya berarti belum dia sebut" in _sp1)
cek("T4  TINGKAT 1: nama usaha tidak lagi 'saat menawarkan decknya'",
    "Momen paling wajar: saat menawarkan decknya" not in _sp
    and "nama usahanya kutanyakan di pesan perkenalan bersama namanya" in _sp1)
cek("T4b kalimat tawaran deck tetap jadi jaring terakhir", "kalau boleh tau nama usahanya apa ya kak?." in _sp)
cek("T4c [FACTS] menjelaskan pertanyaan gabungan", "nama dan nama usahanya sekaligus → dua-duanya" in _sp)

# --- T5 prompt: balasan ringkas ---
_gaya = _sp.split("\n# GAYA\n")[1].split("\n# MENGGALI")[0]
cek("T5  target panjang: DUA kalimat, 20-35 kata", "Panjang yang kuincar: DUA kalimat, kira-kira 20 sampai 35 kata" in _gaya.replace("\n", " "))
cek("T5b batas keras 3 kalimat tetap ada", "Maksimal 3 kalimat;" in _gaya and "itu batas keras" in _gaya)
cek("T5c larangan mengulang ucapan prospek", "JANGAN MENGULANG UCAPANNYA" in _gaya)
cek("T5d ALUR 10 menyuruh membuang kalimat yang mengulang sebelum mengirim",
    "buang kalimat yang cuma mengulang atau merangkum ucapannya" in _sp)
_pas = [k.replace("\n", " ") for k in _re.findall(r'(?:Pas: |— )"([^"]+)"', _gaya)]
cek("T5e dua contoh balasan 'pas' ditemukan", len(_pas) == 2, str(_pas))
for _k in _pas:
    _kal = len(_re.findall(r"[.?!](?:\s|$)", _k))
    _kata = len(_k.split())
    cek("T5f contoh pas '%s...' <= 2 kalimat & <= 35 kata (%d kal, %d kata)" % (_k[:30], _kal, _kata),
        _kal <= 2 and _kata <= 35)
_buruk = _re.search(r'Terlalu panjang[^"]*"([^"]+)"', _gaya)
cek("T5g contoh buruk memuat pembuka terlarang 'Jadi alurnya ada dua'",
    _buruk is not None and _buruk.group(1).startswith("Jadi alurnya ada dua"))
cek("T5h tidak ada nama prospek uji di prompt", "Nadia" not in _sp)
cek("T5i tidak ada tanda seru di contoh 'pas'", all("!" not in k for k in _pas))

# --- T6 detektor gabungan ---
for kal, harap in [
        (PERKENALAN_BARU, ["nama_bisnis", "nama_lengkap"]),
        ("Boleh tau nama kakak siapa dan nama usahanya apa kak?", ["nama_bisnis", "nama_lengkap"]),
        ("Namanya siapa kak, usahanya namanya apa?", ["nama_bisnis", "nama_lengkap"]),
        ("Boleh kenalan kak, namanya siapa dan usahanya namanya apa?", ["nama_bisnis", "nama_lengkap"]),
        ("Kalau boleh tau dengan kak siapa, dan nama tokonya apa?", ["nama_bisnis", "nama_lengkap"]),
        (INTRO_1709, ["industri", "nama_lengkap"]),
        ("Nama usahanya apa, dan yang balas chat siapa?", ["nama_bisnis"]),
        ("Nama pelanggannya siapa aja kak?", []),
        ("Oh iya, nama usahanya apa kak?", ["nama_bisnis"]),
        ("Usahanya bergerak di bidang apa kak, boleh cerita sedikit?", ["industri"])]:
    got = detek(kal)
    cek("T6  detektor '%s' -> %s" % (kal[-55:], harap), got == harap, str(got))

# --- T7 penangkap jawaban gabungan (model TIDAK menulis [FACTS]) ---
for pesan, nama, usaha, bidang in [
        ("Rina, Dapur Mama", "Rina", "Dapur Mama", ""),
        ("Rina kak, usahaku namanya Dapur Mama", "Rina", "Dapur Mama", ""),
        ("aku Rina dari Dapur Mama", "Rina", "Dapur Mama", ""),
        ("aku Rina, usahaku Dapur Mama", "Rina", "Dapur Mama", ""),
        ("Rina owner Kopi Senja", "Rina", "Kopi Senja", ""),
        ("Nama saya Rina, usaha saya Kopi Senja", "Rina", "Kopi Senja", ""),
        ("Rina\nKopi Senja", "Rina", "Kopi Senja", ""),
        ("Rina - Kopi Senja kak", "Rina", "Kopi Senja", ""),
        ("usahaku Kopi Senja, aku Rina", "Rina", "Kopi Senja", ""),
        ("Kopi Senja, aku Rina", "Rina", "Kopi Senja", ""),
        ("oke kak, aku Rina dari Toko Berkah Jaya", "Rina", "Berkah Jaya", ""),
        (JAWAB_1709, "Nadia", "", "katering"),
        ("Rina, katering rumahan", "Rina", "", "katering rumahan"),
        ("Rina, usahaku katering", "Rina", "", "katering"),
        ("aku Rina, jualan skincare", "Rina", "", "jualan skincare"),
        ("Rina", "Rina", "", ""),
        ("Rina kak", "Rina", "", ""),
        ("Rina dari Surabaya", "Rina", "", ""),
        ("Rina\nmau tanya harganya dong", "Rina", "", ""),
        ("Rina, belum ada nama usahanya kak", "Rina", "", ""),
        ("dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?", "Aldi", "", ""),
        ("harganya berapa kak?", "", "", ""),
        ("rahasia hehe", "", "", "")]:
    d = tangkap(pesan, PERKENALAN_BARU, ai="Salam kenal kak.")
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"])
    cek("T7  '%s' -> nama=%r usaha=%r bidang=%r" % (pesan.replace("\n", " / "), nama, usaha, bidang),
        got == (nama, usaha, bidang), str(got))

d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU, ai='Salam kenal kak.\n[FACTS nama="Rina Wati" nama_bisnis="Dapur Mama Rina"]')
cek("T8  [FACTS] dari model menang atas penangkap gabungan",
    d and d["nama_lengkap_merged"] == "Rina Wati" and d["nama_bisnis_merged"] == "Dapur Mama Rina" and d["slotTertangkap"] == "",
    str(d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["slotTertangkap"])))
d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU, ai='Salam kenal kak.\n[FACTS nama="Rina"]')
cek("T8b [FACTS] hanya nama -> nama usaha tetap ditangkap penangkap",
    d and d["nama_bisnis_merged"] == "Dapur Mama" and d["slotTertangkap"] == "nama_bisnis", str(d and d["slotTertangkap"]))
d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU, prev={"nama_bisnis": "Kopi Senja"})
cek("T8c nama usaha lama tidak pernah ditimpa", d and d["nama_bisnis_merged"] == "Kopi Senja" and d["nama_lengkap_merged"] == "Rina")
d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU)
cek("T8d slotTertangkap mencatat dua kolom", d and d["slotTertangkap"] == "nama_lengkap,nama_bisnis", str(d and d["slotTertangkap"]))
d = tangkap("Dapur Mama", "Oh iya, nama usahanya apa kak?")
cek("T9  jawaban tanya ulang nama usaha ditangkap (jalur satu slot)",
    d and d["nama_bisnis_merged"] == "Dapur Mama" and d["slotTertangkap"] == "nama_bisnis", str(d and d["nama_bisnis_merged"]))
d = tangkap("Rina, Dapur Mama", "Nama usahanya apa, dan yang balas chat siapa?")
cek("T9b tanpa pertanyaan nama orang -> penangkap gabungan tidak jalan",
    d and d["nama_lengkap_merged"] == "", str(d and d["nama_lengkap_merged"]))

# --- T10 nama bocor: ulang persis uji 2026-09-17 ---
d = satu(proses(BALAS_1709, pesan_user=JAWAB_1709, prev_row={"last_bot_reply": INTRO_1709}))
cek("T10 uji 17/09: 'Salam kenal Nadia' -> 'Salam kenal kak' walau nama tidak tersimpan",
    d and d["cleanOutput"].startswith("Salam kenal kak.") and "nadia" not in d["cleanOutput"].lower()
    and d["namaDihapus"] is True, str(d and d["cleanOutput"][:60]))
cek("T10b kata 'katering' di balasan tidak tersentuh", d and "Chat katering memang paling ramai" in d["cleanOutput"])
cek("T10c perkenalan lama (bidang + nama) tetap tidak ditebak: nama tidak disimpan",
    d and d["nama_lengkap_merged"] == "", str(d and d["nama_lengkap_merged"]))
d = satu(proses("Halo Nadia, oke. Jadi Nadia mau tanya soal chat?", pesan_user=JAWAB_1709,
                prev_row={"last_bot_reply": INTRO_1709}))
cek("T10d nama tebakan hanya dihapus sesudah sapaan, tidak di tengah kalimat",
    d and d["cleanOutput"] == "Halo kak, oke. Jadi Nadia mau tanya soal chat?", str(d and d["cleanOutput"]))
d = satu(proses("Chat katering memang ramai kak. Biasanya pesan H berapa?", pesan_user="katering kak, aku Nadia",
                prev_row={"last_bot_reply": INTRO_1709}))
cek("T10e tebakan yang ternyata bukan nama ('katering') tidak merusak balasan",
    d and d["cleanOutput"] == "Chat katering memang ramai kak. Biasanya pesan H berapa?", str(d and d["cleanOutput"]))
d = satu(proses("Salam kenal Budi.", pesan_user="Budi", prev_row={"last_bot_reply": "Usahanya di bidang apa kak?"}))
cek("T10f tanpa pertanyaan nama sebelumnya -> tidak ada tebakan", d and d["cleanOutput"] == "Salam kenal Budi.")

# --- T11 alur baru, giliran demi giliran ---
PESAN1 = "Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku."
g, d = galian2({"greeting_sent": ""}, PESAN1)
cek("T11 pesan 1: galian = nama DAN nama usaha, satu kalimat",
    g is not None and g.startswith("namanya dan nama usahanya") and "SATU kalimat" in g, str(g))
g, _ = galian2({"greeting_sent": "", "nama_lengkap": "Rina"}, PESAN1)
cek("T11b pesan 1, nama sudah disebut -> nama usaha saja", g is not None and g.startswith("nama usahanya — tanyakan di"), str(g))
_bocor = [c for c in range(0, 13) for gs in ("",) for g, _ in [galian2({"greeting_sent": gs, "Counter": str(c)}, "oke")]
          if g and _re.search(r"bidang|masalah|chat masuk", g)]
cek("T11c perkenalan tidak pernah menggali bidang/masalah/jumlah chat", not _bocor, str(_bocor[:3]))

d = satu(proses("Salam kenal kak Nadia. Pas malam justru jam orang mikir pesanan, jadi yang telat dibalas "
                "biasanya pindah ke katering lain.", pesan_user=JAWAB_1709,
                prev_row={"last_bot_reply": PERKENALAN_BARU}))
cek("T12 pesan 2 (jawaban uji 17/09 atas perkenalan baru): nama & bidang tersimpan, nama usaha kosong",
    d and (d["nama_lengkap_merged"], d["industri_merged"], d["nama_bisnis_merged"]) == ("Nadia", "katering", ""),
    str(d and (d["nama_lengkap_merged"], d["industri_merged"], d["nama_bisnis_merged"])))
cek("T12b nama tidak dipakai menyapa", d and d["cleanOutput"].startswith("Salam kenal kak.") and "Nadia" not in d["cleanOutput"])

g, _ = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": PERKENALAN_BARU}, JAWAB_1709)
cek("T13 giliran 2, nama usaha belum tercatat -> tanya ulang (walau perkenalan baru saja menanyakannya)",
    g is not None and g.startswith("nama usahanya — tanya ulang SEKALI"), str(g))
cek("T13b baris tanya ulang memberi jalan keluar kalau nama usahanya ternyata sudah disebut",
    g is not None and "sudah menyebut nama usahanya, jangan ditanyakan" in g and "tanyakan bidang usahanya" in g, str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": PERKENALAN_BARU}, "Rina, harganya berapa kak?")
cek("T13c giliran 2 tapi prospek bertanya -> galian ditunda (pertanyaan dijawab dulu)", g is None, str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "last_bot_reply": "Basic mulai Rp3.000.000 per bulan kak."}, "oke")
cek("T13d tanya ulang yang tertunda jalan di giliran 3", g is not None and g.startswith("nama usahanya — tanya ulang"), str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "last_bot_reply": "Oh iya, nama usahanya apa kak?"}, "hmm nanti aja")
cek("T13e tanya ulang sudah dilakukan & tidak dijawab -> lanjut bidang usaha, TIDAK diulang lagi",
    g is not None and g.startswith("bidang usahanya"), str(g))
_ulang = []
for c in range(3, 13):
    for lalu in ("", "Oh iya, nama usahanya apa kak?", PERKENALAN_BARU):
        g, _ = galian2({"greeting_sent": "Y", "Counter": str(c), "last_bot_reply": lalu}, "oke")
        if g and g.startswith("nama usahanya"):
            _ulang.append((c, lalu[:20]))
cek("T13f nama usaha tidak pernah ditanya ulang sesudah giliran 3 (30 kombinasi)", not _ulang, str(_ulang[:3]))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "nama_lengkap": "Nadia", "nama_bisnis": "Dapur Nadia",
                "last_bot_reply": "Oh iya, nama usahanya apa kak?"}, "Dapur Nadia")
cek("T14 giliran 3, nama usaha sudah ada -> bidang usaha + cerita singkat",
    g is not None and g.startswith("bidang usahanya, sekaligus minta dia cerita singkat"), str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "nama_lengkap": "Nadia", "nama_bisnis": "Dapur Nadia",
                "industri": "katering", "last_bot_reply": "Oh iya, nama usahanya apa kak?"}, "Dapur Nadia")
cek("T14b giliran 3, bidang sudah ada -> masalah", g is not None and g.startswith("masalah terbesarnya"), str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "3", "nama_bisnis": "Dapur Nadia", "industri": "katering",
                "last_bot_reply": "Usahanya bergerak di bidang apa kak, boleh cerita sedikit?"}, "katering rumahan kak")
cek("T14c contoh galian bidang di prompt ikut kena jeda satu balasan", g is None or not g.startswith("bidang"), str(g))


# ===========================================================================
bagian("R. BEDAH REGRESI v3.10 vs export live — yang tidak disebut patch tidak tersentuh")
# ===========================================================================
import difflib as _dl
with open(os.path.join(DIR, "VIRA Personal — Main.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Process All", "Rakit Konteks"}

cek("R1  jumlah & nama node sama dengan export live", set(_NL) == set(NODES) and len(wf["nodes"]) == 89)
cek("R2  koneksi identik", json.dumps(_lama["connections"], sort_keys=True) == json.dumps(CONNS, sort_keys=True))
_beda = sorted(n for n in NODES if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  86 node lain identik byte per byte dengan export live", not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))
cek("R4b settings workflow tetap", _lama.get("settings") == wf.get("settings"))


def _baris_diganti(a, b):
    la, lb = a.split("\n"), b.split("\n")
    return [i for t, i1, i2, j1, j2 in _dl.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes()
            if t != "equal" for i in range(i1, i2)]


def _wilayah(teks_, awal, akhir):
    la = teks_.split("\n")
    i = next(k for k, x in enumerate(la) if awal in x)
    j = next(k for k in range(i, len(la)) if akhir in la[k])
    return set(range(i, j + 1))


def _di_luar(teks_lama, teks_baru, wilayah):
    boleh = set()
    for aw, ak in wilayah:
        boleh |= _wilayah(teks_lama, aw, ak)
    la = teks_lama.split("\n")
    return [la[i].strip()[:60] for i in _baris_diganti(teks_lama, teks_baru) if i not in boleh]


_pa0, _pa1 = _NL["Process All"]["parameters"]["jsCode"], NODES["Process All"]["parameters"]["jsCode"]
_x = _di_luar(_pa0, _pa1, [("const namaMilikLain =", "hasil.add('nama_lengkap');"),
                           ("let namaDihapus = false;", "return [{")])
cek("R5  Process All: baris lama yang diganti hanya di detektor nama & jaring nama", not _x, str(_x))
_rk0, _rk1 = _NL["Rakit Konteks"]["parameters"]["jsCode"], NODES["Rakit Konteks"]["parameters"]["jsCode"]
_x = _di_luar(_rk0, _rk1, [("const namaMilikLain =", "hasil.add('nama_lengkap');"),
                           ("// - nama_bisnis: tidak di sini", "// - nama_bisnis: tidak di sini"),
                           ("const GALIAN = [", "if (galian) barisProspek.push")])
cek("R6  Rakit Konteks: baris lama yang diganti hanya di detektor, komentar, dan GALIAN", not _x, str(_x))
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
cek("R7  detektor galian tetap IDENTIK di Process All dan Rakit Konteks", _det(_pa1) == _det(_rk1))
cek("R7b detektor memang berubah dari export live (pertanyaan gabungan)", _det(_pa1) != _det(_pa0))

_sp0 = _NL["AI Agent"]["parameters"]["options"]["systemMessage"]
_x = _di_luar(_sp0, _sp, [
    ("Pesan perkenalan itu juga menanyakan namanya", "Pesan perkenalan itu juga menanyakan namanya"),
    ("   Nama, bidang usaha, masalah utama", "   Nama, bidang usaha, masalah utama"),
    ("10. Sebelum mengirim", "ikut dihitung dan tidak pernah dipotong"),
    ("Lalu langsung jawab pertanyaannya, dan tutup", "Kalau dia sudah menyebut namanya di pesan pertama"),
    ("Aku ingin tahu sedang bicara dengan siapa", "jawaban satu kata jadi tidak bisa kubedakan"),
    ("Maksimal 3 kalimat per balasan", "tanya di giliran berikutnya. Menjawab pendek"),
    ("kususun sendiri: satu kalimat, ringan", "bidang apa kak?\"; untuk masalah"),
    ("decknya jadi generik. Momen paling wajar", "namanya dipakai. Contoh"),
    ("menanyakan namanya → `nama`; nama usahanya", "menanyakan namanya → `nama`; nama usahanya")])
cek("R8  system prompt: baris lama yang diganti hanya di 9 wilayah sasaran patch", not _x, str(_x))
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R9  AI Agent: selain systemMessage identik", _pl == _pb)
cek("R10 DeepSeek Personal Chat: temperature tetap 0.7 (panjang diatur lewat prompt, bukan parameter)",
    NODES["DeepSeek Personal Chat"]["parameters"]["options"].get("temperature") == 0.7)


'''

AWAL_R = ('# ===========================================================================\n'
          'bagian("R. BEDAH REGRESI v3.9 vs v3.8 — yang tidak disebut patch tidak tersentuh")')
ANCHOR = ('# ===========================================================================\n'
          'print()\n'
          'print("=" * 72)\n'
          'print("RINGKASAN UAT")')
assert teks.count(AWAL_R) == 1 and teks.count(ANCHOR) == 1
i, j = teks.index(AWAL_R), teks.index(ANCHOR)
teks = teks[:i] + BARU + teks[j:]

# --- 7. checklist UAT manual ---------------------------------------------
ganti('    "Import 2026-09-15-VIRA-Personal-Main-v3.9.json, matikan v3.8 dulu, lalu aktifkan v3.9. Tidak ada kolom baru.",\n',
      '    "Import 2026-09-18-VIRA-Personal-Main-v3.10.json, matikan v3.9 dulu, lalu aktifkan v3.10. Tidak ada kolom baru.",\n')
ganti('    "NAMA — nomor baru kirim \'halo\': perkenalan seperti biasa + \'namanya siapa kak?\'.",\n',
      '    "PERKENALAN — nomor uji (baris STATS-nya dihapus dulu) kirim \'Halo VIRA, aku lihat website-nya dan mau coba '
      'ngobrol soal AI customer service buat bisnisku.\': perkenalan + SATU kalimat \'nama kakak siapa, dan nama usahanya '
      'apa?\'. TIDAK ada pertanyaan bidang usaha atau alasan tertarik.",\n'
      '    "NAMA + USAHA — ulang uji 17/09: jawab \'Nadia kak, bisnis aku katering, chat suka numpuk pas malem\'. '
      'Balasan menyapa \'kak\' TANPA nama dan menanyakan ulang nama usaha (sekali). STATS: nama_lengkap = Nadia, '
      'industri = katering, nama_bisnis kosong.",\n'
      '    "NAMA USAHA — jawab \'Dapur Nadia\': STATS.nama_bisnis = Dapur Nadia. Balasan berikutnya tidak menanyakan '
      'nama usaha lagi, lanjut masalah (bidang sudah ada) atau bidang usaha + cerita singkat.",\n'
      '    "NAMA + USAHA SEKALIGUS — nomor uji baru, jawab perkenalan dengan \'Rina, Kopi Senja\': balasan TIDAK menanyakan '
      'nama usaha lagi. STATS: nama_lengkap = Rina, nama_bisnis = Kopi Senja.",\n'
      '    "RINGKAS — sepanjang uji, balasan galian umumnya 2 kalimat (maks 3) dan TIDAK membuka dengan merangkum jawaban '
      '(\'Jadi...\', \'Berarti...\', \'Paham, berarti...\', \'Nah itu...\'). Bandingkan dengan transkrip 17/09.",\n')
ganti('    "DECK — terima tawaran deck + sebut nama usaha: STATS.nama_bisnis terisi, REQUESTS mendapat baris, "\n'
      '    "notif brief ke Steven berbaris \'WA: 62xxx · Budi\'.",\n',
      '    "DECK — sampai tawaran deck: REQUESTS.nama_bisnis SUDAH terisi dari awal, notif brief ke Steven berbaris "\n'
      '    "\'WA: 62xxx · Nadia\', dan deck yang digenerate tidak lagi bernama \'tanpa-nama.pdf\'.",\n')

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(teks)

print("DST : %s  (%d baris)" % (os.path.basename(DST), teks.count("\n") + 1))
