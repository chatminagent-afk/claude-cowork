# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-23.py - turunkan _uat_2026-09-23.py dari harness _uat_2026-09-22.py.

Harness v3.11 diarahkan ulang ke v3.12. Seksi A-Q, S, T dan U ikut jalan sebagai regresi.
Yang disesuaikan HANYA cek yang mengunci teks lama yang memang diganti patch ini:
  T5/T5b/T5f/T5g  target panjang & contoh di # GAYA (sekarang: satu kalimat tanya, batas 2)
  T10b            balasan uji 17/09 kini dipangkas jaring RINGKAS -> tujuan cek aslinya
                  (penghapus nama tidak merusak kata lain) diuji di balasan tanpa pertanyaan
  T14             teks galian bidang usaha tanpa "cerita singkat"
Seksi baru:
  V. RINGKAS & PENANGKAP - ulang persis uji Steven 2026-09-23 (abdul, parfum).
Seksi R ditulis ulang: membedah v3.12 terhadap v3.11 (= live, dicek via MCP 2026-09-23).

Jalankan: python _buat_uat_2026-09-23.py   (lalu: python _uat_2026-09-23.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-22.py")
DST = os.path.join(DIR, "_uat_2026-09-23.py")

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


# --- 1. arahkan ke v3.12 -------------------------------------------------
ganti('WF = os.path.join(DIR, "2026-09-22-VIRA-Personal-Main-v3.11.json")',
      'WF = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.12.json")')
ganti("_uat_2026-09-22.py — UAT perilaku untuk 2026-09-22-VIRA-Personal-Main-v3.11.json.\n\n"
      "Diturunkan dari _uat_2026-09-18.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-22.py, lalu jalankan ulang). Seksi A-Q, S dan T ikut jalan sebagai\n"
      "regresi tanpa penyesuaian; seksi U baru untuk patch deck terkirim; seksi R membedah\n"
      "v3.11 terhadap v3.10.",
      "_uat_2026-09-23.py — UAT perilaku untuk 2026-09-23-VIRA-Personal-Main-v3.12.json.\n\n"
      "Diturunkan dari _uat_2026-09-22.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-23.py, lalu jalankan ulang). Seksi A-Q, S, T dan U ikut jalan sebagai\n"
      "regresi (hanya cek yang mengunci teks lama yang diganti yang disesuaikan); seksi V baru\n"
      "untuk uji Steven 2026-09-23; seksi R membedah v3.12 terhadap v3.11.")
ganti("Jalankan: python _uat_2026-09-22.py", "Jalankan: python _uat_2026-09-23.py")
ganti('print("UAT PERILAKU — VIRA Personal v3.11 (2026-09-22)")',
      'print("UAT PERILAKU — VIRA Personal v3.12 (2026-09-23)")')

# --- 2. cek lama yang mengunci teks yang memang diganti ------------------
ganti('''cek("T5  target panjang: DUA kalimat, 20-35 kata", "Panjang yang kuincar: DUA kalimat, kira-kira 20 sampai 35 kata" in _gaya.replace("\\n", " "))
cek("T5b batas keras 3 kalimat tetap ada", "Maksimal 3 kalimat;" in _gaya and "itu batas keras" in _gaya)''',
      '''cek("T5  target (v3.12): SATU kalimat tanya + pengakuan <= 4 kata",
    "SATU kalimat tanya, boleh didahului pengakuan pendek maksimal empat kata" in _gaya.replace("\\n", " "))
cek("T5b batas keras (v3.12): 2 kalimat, sekitar 25 kata", "Batas keras 2 kalimat, sekitar 25 kata." in _gaya)''')
ganti('''    cek("T5f contoh pas '%s...' <= 2 kalimat & <= 35 kata (%d kal, %d kata)" % (_k[:30], _kal, _kata),
        _kal <= 2 and _kata <= 35)''',
      '''    cek("T5f contoh pas '%s...' <= 2 kalimat & <= 20 kata (%d kal, %d kata)" % (_k[:30], _kal, _kata),
        _kal <= 2 and _kata <= 20)''')
ganti('''cek("T5g contoh buruk memuat pembuka terlarang 'Jadi alurnya ada dua'",
    _buruk is not None and _buruk.group(1).startswith("Jadi alurnya ada dua"))''',
      '''cek("T5g contoh buruk (v3.12) = gema + promosi: '50 chat sehari itu' ... 'VIRA bisa pegang'",
    _buruk is not None and _buruk.group(1).startswith("50 chat sehari itu")
    and "VIRA bisa pegang" in _buruk.group(1).replace("\\n", " "))''')
ganti('''cek("T10b kata 'katering' di balasan tidak tersentuh", d and "Chat katering memang paling ramai" in d["cleanOutput"])''',
      '''cek("T10b (v3.12) balasan uji 17/09 kini juga dipangkas RINGKAS: kalimat gema dibuang",
    d and d["cleanOutput"] == "Salam kenal kak. Kalau lagi numpuk gitu, biasanya yang paling bikin repot bagian mananya kak?"
    and d["ringkas"] == "gema", str(d and (d["cleanOutput"], d["ringkas"])))
_d10 = satu(proses("Salam kenal Nadia. Chat katering memang paling ramai pas malam hari.", pesan_user=JAWAB_1709,
                   prev_row={"last_bot_reply": INTRO_1709}))
cek("T10b' kata 'katering' tidak tersentuh penghapus nama (balasan tanpa pertanyaan = tanpa RINGKAS)",
    _d10 and _d10["cleanOutput"] == "Salam kenal kak. Chat katering memang paling ramai pas malam hari.",
    str(_d10 and _d10["cleanOutput"]))''')
for _uji in ('("Rina owner Kopi Senja", "Rina", "Kopi Senja", ""),',
             '("Nama saya Rina, usaha saya Kopi Senja", "Rina", "Kopi Senja", ""),',
             '("Rina\\nKopi Senja", "Rina", "Kopi Senja", ""),',
             '("Rina - Kopi Senja kak", "Rina", "Kopi Senja", ""),',
             '("usahaku Kopi Senja, aku Rina", "Rina", "Kopi Senja", ""),',
             '("Kopi Senja, aku Rina", "Rina", "Kopi Senja", ""),'):
    # v3.12: nama usaha yang menyebut jenisnya ("Kopi ...") ikut mengisi industri
    ganti(_uji, _uji.replace('"Kopi Senja", ""),', '"Kopi Senja", "kopi"),'))
ganti('''cek("T14 giliran 3, nama usaha sudah ada -> bidang usaha + cerita singkat",
    g is not None and g.startswith("bidang usahanya, sekaligus minta dia cerita singkat"), str(g))''',
      '''cek("T14 giliran 3, nama usaha sudah ada -> bidang usaha (v3.12: tanpa 'cerita singkat')",
    g == "bidang usahanya", str(g))''')

# --- 3. seksi V (baru), disisipkan sebelum seksi R ------------------------
SEKSI_V = r'''bagian("V. RINGKAS & PENANGKAP — ulang uji Steven 2026-09-23 (abdul, parfum)")
# ===========================================================================
INTRO_2309 = ("Halo kak, salam kenal! Aku Steven versi AI, dibangun sama Steven pakai sistem yang sama yang "
              "dia bikin untuk kliennya, namanya VIRA. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. "
              "Senang kakak tertarik setelah lihat website-nya. Kakak mau cerita dulu soal bisnisnya, atau "
              "langsung tanya hal yang paling bikin penasaran? Btw boleh tau nama kakak siapa, dan nama "
              "usahanya apa?")
ABDUL = "abdul\naku owner humanizer\njualan parfum\nkdg ribet balesin org ty 1 1"
# Transkrip asli 23/09: (pesan prospek, balasan VIRA sebelumnya, balasan VIRA giliran ini)
G2 = ("Salam kenal kak. Jadi Humanizer ini jualan parfum ya, wajar sih ribet, chat parfum biasanya banyak "
      "yang nanya aroma, ketahanan, sama rekomendasi. Nah itu justru yang bisa dipegang VIRA. Balesin yang "
      "nanya-nanya itu otomatis 24 jam, jadi kakak tinggal fokus ke yang udah siap order. Btw nama usahanya "
      "Humanizer itu sendiri ya kak, atau itu nama brand parfumnya?")
G3 = ("Oke, Humanizer itu nama brand sekaligus usahanya. Nah soal chat yang bikin ribet itu, yang paling "
      "sering bikin kakak kewalahan bagian mananya, yang nanya aroma, atau yang nanya harga dan stok?")
G4 = ("Semua jenis chat itu memang makan waktu kalau dibales satu-satu. VIRA bisa pegang itu semua sekaligus, "
      "jelasin aroma, jawab harga, cek stok, sampai kasih rekomendasi. Kira-kira sehari ada berapa chat masuk "
      "kak, biar aku kebayang bebannya?")
G5 = ("100 chat sehari itu lumayan berat buat dibales sendiri, apalagi sambil ngurus packing dan stok. Dari "
      "chat pertama sampai orangnya akhirnya beli, biasanya lewat langkah apa aja kak?")
G6 = ("Alurnya jelas, tanya dulu, minta pricelist, terus pesen. Nah bagian tanya-tanya dan kirim pricelist "
      "itu yang paling bisa diotomasi. VIRA bisa jawab pertanyaan umum dan kirim pricelist otomatis, jadi "
      "kakak tinggal terima order yang udah jadi. Biasanya mereka paling sering nanya apa aja kak, selain harga?")
_FAKTA4 = {"nama_lengkap": "Abdul", "nama_bisnis": "humanizer", "industri": "jualan parfum",
           "masalah_utama": "kdg ribet balesin org ty 1 1"}


def proses2(ai_output, pesan_user, prev_row=None, baru=False, galian_kolom=None):
    """proses() dengan isNewUser dan galian_kolom (keluaran Rakit Konteks) yang bisa diatur."""
    rk = {"katalog": {"links": LINKS}}
    if galian_kolom is not None:
        rk["galian_kolom"] = galian_kolom
    prev = {"resolved_key": "6289900112233", "nama_lengkap": "", "nama_bisnis": "", "industri": "",
            "masalah_utama": "", "volume_chat": "", "budget_range": "", "minat_paket": "", "bahasa": "",
            "deck_requested": "", "brief_terisi": "", "last_bot_reply": "", "last_bot_reply_ts": 0}
    prev.update(prev_row or {})
    return satu(jalan("Process All", nodes={
        "Chat Counter": [item(original_message=pesan_user, user_wa="6289900112233", user_name="Prospek")],
        "Preprocess - Context Detection": [item(actualUserMessage=pesan_user, isNewUser=baru, wantsMedia=False,
                                                askingPrice=False, wantsHuman=False)],
        "Parse Config": [item(config=cfg())],
        "Resolve User Row": [item(**prev)],
        "Rakit Konteks": [item(**rk)],
    }, inp=[item(output=ai_output)]))


# ---- V1 penangkap jawaban perkenalan -------------------------------------
cek("V1  perkenalan asli 23/09 terbaca detektor sebagai nama + nama usaha",
    detek(INTRO_2309) == ["nama_bisnis", "nama_lengkap"], str(detek(INTRO_2309)))
d = tangkap(ABDUL, INTRO_2309, ai="Salam kenal kak.")
cek("V1b pesan 4 baris uji 23/09 -> nama, nama usaha, industri, masalah tertangkap semua",
    d and {k: d[k + "_merged"] for k in _FAKTA4} == _FAKTA4, str(d and {k: d[k + "_merged"] for k in _FAKTA4}))
cek("V1c slotTertangkap mencatat keempatnya",
    d and sorted(d["slotTertangkap"].split(",")) == sorted(_FAKTA4), str(d and d["slotTertangkap"]))
for pesan, harap in [
        (ABDUL, ("Abdul", "humanizer", "jualan parfum", "kdg ribet balesin org ty 1 1")),
        ("aku owner humanizer", ("", "humanizer", "", "")),
        ("Rina\nkewalahan balesin customer", ("Rina", "", "", "kewalahan balesin customer")),
        ("kewalahan balesin customer\nRina", ("Rina", "", "", "kewalahan balesin customer")),
        ("jualan parfum\nabdul", ("Abdul", "", "jualan parfum", "")),
        ("Rina, parfum", ("Rina", "", "parfum", "")),
        ("saya owner Toko Wangi, jualan parfum", ("", "Wangi", "jualan parfum", "")),
        ("Nadia kak, bisnis aku katering, chat suka numpuk pas malem", ("Nadia", "", "katering", "chat suka numpuk pas malem")),
        ("Rina, Dapur Mama", ("Rina", "Dapur Mama", "", "")),
        ("aku Rina, jualan skincare", ("Rina", "", "jualan skincare", "")),
        ("Budi, Klinik Sehat Gigi", ("Budi", "Klinik Sehat Gigi", "klinik", "")),
        ("Sari dari Bimbel Cerdas Mandiri", ("Sari", "Bimbel Cerdas Mandiri", "bimbel", "")),
        ("Rina, Dapur Mama, jualan kue", ("Rina", "Dapur Mama", "jualan kue", "")),
        ("dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?", ("Aldi", "", "", ""))]:
    d = tangkap(pesan, PERKENALAN_BARU, ai="Salam kenal kak.")
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"], d["masalah_utama_merged"])
    cek("V2  '%s' -> %s" % (pesan.replace("\n", " / ")[:45], harap), got == harap, str(got))
d = tangkap(ABDUL, INTRO_2309, ai="Salam kenal kak.", prev={"masalah_utama": "chat numpuk"})
cek("V2b masalah lama tidak pernah ditimpa keluhan baru", d and d["masalah_utama_merged"] == "chat numpuk")
d = tangkap(ABDUL, INTRO_2309, ai='Salam kenal kak.\n[FACTS nama="Abdul Karim" industri="parfum"]')
cek("V2c [FACTS] dari model tetap menang", d and d["nama_lengkap_merged"] == "Abdul Karim" and d["industri_merged"] == "parfum",
    str(d and (d["nama_lengkap_merged"], d["industri_merged"])))
d = tangkap("kewalahan balesin customer", "Usahanya di bidang apa kak?")
cek("V2d di luar perkenalan, jalur satu slot tidak berubah (industri = jawaban mentah)",
    d and d["industri_merged"] == "kewalahan balesin customer" and d["masalah_utama_merged"] == "",
    str(d and (d["industri_merged"], d["masalah_utama_merged"])))

# ---- V3 Rakit Konteks: galian memakai fakta pesan giliran ini ---------------
g, d = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": INTRO_2309}, ABDUL)
cek("V3  giliran 2 uji 23/09: TIDAK menanyakan ulang nama usaha (v3.11: 'nama usahanya — tanya ulang')",
    g is None, str(g))
for k, v in _FAKTA4.items():
    cek("V3b DATA PROSPEK memuat %s dari pesan ini" % k,
        d and ("%s: %s (baru dia sebut di pesan ini)" % (k, v)) in d["prospect_context"], d and d["prospect_context"])
cek("V3c baris panggilan: kak muncul begitu nama tertangkap di pesan ini",
    d and "panggilan: kak — nama_lengkap hanya catatan untuk Steven" in d["prospect_context"])
cek("V3d format_balasan: prospek tidak bertanya -> SATU kalimat tanya",
    d and "format_balasan: dia tidak sedang bertanya — cukup SATU kalimat tanya" in d["prospect_context"])
cek("V3e IS_NEW_USER tetap baris terakhir", d and d["prospect_context"].rstrip().endswith("IS_NEW_USER: false"))
_S4 = dict({"greeting_sent": "Y", "Counter": "2"}, **_FAKTA4)
g, d = galian2(dict(_S4, last_bot_reply="Salam kenal kak. Sehari kira-kira ada berapa chat masuk?"), "100 an chat")
cek("V3f jawaban jumlah chat ikut dihitung -> tidak ada galian tersisa", g is None, str(g))
cek("V3g volume_chat dari pesan ini tampil", d and "volume_chat: 100 an chat (baru dia sebut di pesan ini)" in d["prospect_context"])
g, d = galian2(dict({"greeting_sent": "Y", "Counter": "2", "nama_bisnis": "Dapur Mama"},
                    last_bot_reply="Usahanya bergerak di bidang apa kak?"), "katering rumahan kak")
cek("V3h jawaban bidang usaha ditangkap -> langsung ke masalah (dulu: jeda satu balasan)",
    g is not None and g.startswith("masalah terbesarnya"), str(g))
g, d = galian2({"greeting_sent": "Y", "Counter": "2"}, "harganya berapa kak?")
cek("V3i prospek bertanya -> format_balasan BERTANYA, tanpa galian",
    g is None and "format_balasan: dia sedang BERTANYA — jawab langsung" in d["prospect_context"], str(g))
g, d = galian2({"greeting_sent": ""}, "Halo VIRA, aku lihat website-nya")
cek("V3j pesan perkenalan: tanpa format_balasan & tanpa fakta pesan ini (aturan perkenalan sendiri)",
    "format_balasan" not in d["prospect_context"] and "baru dia sebut" not in d["prospect_context"])
d = rakit({"greeting_sent": "Y", "Counter": "3"})
cek("V3k tanpa pesan prospek (node Preprocess tidak ada) -> node tetap jalan", d is not None)
for lalu, pesan in [("Oh iya, nama usahanya apa kak?", "Dapur Mama"),
                    ("Usahanya di bidang apa kak?", "katering rumahan kak"),
                    ("Soal chat, yang paling bikin repot sekarang apa kak?", "chat numpuk pas malem ga kebales"),
                    ("Kira-kira sehari ada berapa chat masuk kak?", "50an"),
                    (INTRO_2309, ABDUL), (PERKENALAN_BARU, "Rina, Dapur Mama"),
                    (PERKENALAN_BARU, "harganya berapa kak?"),
                    ("Yang paling bikin repot pas lagi rame, biasanya bagian mananya?", "100 an chat"),
                    ("Dari chat pertama sampai beli, biasanya lewat langkah apa aja kak?",
                     "tanya dulu, trus sehari bisa 40 chat kalo lagi rame")]:
    _, drk = galian2({"greeting_sent": "Y", "Counter": "2", "last_bot_reply": lalu}, pesan)
    rk_f = dict(_re.findall(r"^(\w+): (.*) \(baru dia sebut di pesan ini\)$", drk["prospect_context"], _re.M))
    dpa = tangkap(pesan, lalu)
    pa_f = {k: dpa[k + "_merged"] for k in ("nama_lengkap", "nama_bisnis", "industri", "masalah_utama", "volume_chat")
            if dpa[k + "_merged"]}
    cek("V3l Rakit Konteks & Process All sepakat soal fakta '%s'" % pesan.replace("\n", " / ")[:40],
        rk_f == pa_f, "RK=%s PA=%s" % (rk_f, pa_f))

# ---- V4 jaring RINGKAS: transkrip asli ------------------------------------
for judul, pesan, lalu, ai, harap, alasan in [
        ("G2", ABDUL, INTRO_2309, G2,
         "Salam kenal kak. Btw nama usahanya Humanizer itu sendiri ya kak, atau itu nama brand parfumnya?", "gema+panjang"),
        ("G3", "keduanya", G2, G3,
         "Soal chat yang bikin ribet itu, yang paling sering bikin kakak kewalahan bagian mananya, yang nanya aroma, "
         "atau yang nanya harga dan stok?", "panjang"),
        ("G4", "semua", G3, G4, "Kira-kira sehari ada berapa chat masuk kak?", "panjang+ekor"),
        ("G5", "100 an chat", G4, G5,
         "Dari chat pertama sampai orangnya akhirnya beli, biasanya lewat langkah apa aja kak?", "gema"),
        ("G6", "tanya2 dlu, trs minta pricelist, dan pesen", G5, G6,
         "Biasanya mereka paling sering nanya apa aja kak, selain harga?", "gema+panjang")]:
    d = proses2(ai, pesan, {"last_bot_reply": lalu})
    cek("V4  %s uji 23/09 -> '%s...' (%s)" % (judul, harap[:40], alasan),
        d and d["cleanOutput"] == harap and d["ringkas"] == alasan, str(d and (d["cleanOutput"], d["ringkas"])))
    cek("V4b %s ringkas_asli = balasan model utuh, needs_ringkas_log = 'true'" % judul,
        d and d["ringkas_asli"] == ai and d["needs_ringkas_log"] == "true")
    cek("V4c %s last_bot_reply = teks yang terkirim" % judul, d and d["last_bot_reply"] == d["cleanOutput"])
d = proses2(G2.replace("Salam kenal kak.", "Salam kenal Abdul."), ABDUL, {"last_bot_reply": INTRO_2309})
cek("V4d penghapus nama tetap jalan sesudah RINGKAS",
    d and d["cleanOutput"].startswith("Salam kenal kak. Btw nama usahanya") and "abdul" not in d["cleanOutput"].lower(),
    str(d and d["cleanOutput"]))
d = proses2("Siap kak. Terus biasanya yang paling sering ditanyain apa, biar Steven bisa siapin contohnya?", "oke", {})
cek("V4e ekor alasan dibuang walau balasan sudah pendek",
    d and d["cleanOutput"] == "Siap kak. Terus biasanya yang paling sering ditanyain apa?" and d["ringkas"] == "ekor",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Nah itu biasanya bikin repot banget. Apalagi kalau lagi rame. Oh iya, sehari ada berapa chat masuk kak?",
            "biasanya tanya harga", {})
cek("V4f penghubung di depan pertanyaan dibuang kalau tanpa pengakuan ('Oh iya, ...')",
    d and d["cleanOutput"] == "Sehari ada berapa chat masuk kak?" and d["ringkas"] == "panjang",
    str(d and (d["cleanOutput"], d["ringkas"])))

# ---- V5 jaring RINGKAS TIDAK boleh menyentuh --------------------------------
PANJANG_TANYA = ("VIRA bisa balas chat 24 jam, kirim katalog, dan catat pesanan. Bedanya dengan chatbot biasa, "
                 "dia paham maksud orang walau bahasanya campur. Semua jawabannya diambil dari data bisnis kakak "
                 "sendiri. Kakak jualan apa kak?")
for judul, ai, pesan, prev, baru in [
        ("prospek BERTANYA (jawaban tidak boleh terpotong)", PANJANG_TANYA, "ini bisa buat apa aja ya?", {}, False),
        ("prospek bertanya tanpa tanda tanya", PANJANG_TANYA, "bedanya sama chatbot biasa gmn", {}, False),
        ("menyebut harga", "Basic mulai Rp3.000.000 per bulan, sudah termasuk setup. Angka finalnya Steven yang "
         "tentukan setelah lihat kebutuhan kakak. Chat masuk sehari kira-kira ada berapa kak?", "oke noted", {}, False),
        ("tawaran deck", "Itu yang paling sering bikin calon pembeli pindah ke toko lain. VIRA balas dalam hitungan "
         "detik, termasuk tengah malam. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?",
         "iya kadang ada yg kelewat", {}, False),
        ("persetujuan deck (brief)", DECK_BLOK + "Sudah aku teruskan ke Steven, dia sendiri yang akan menyusun "
         "decknya. Sambil nunggu, ada lagi yang mau ditanyain kak?", "boleh",
         {"last_bot_reply": "mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?"}, False),
        ("handover", "[TALK_TO_ADMIN]\nSiap kak, aku sambungkan ke Steven ya. Dia biasanya balas di hari yang "
         "sama. Ada yang mau aku titipkan ke dia kak?", "mau ngobrol langsung sama steven", {}, False),
        ("[UNKNOWN]", "[UNKNOWN]\nYang itu aku belum tahu pasti kak, nanti aku tanyakan ke Steven dulu. Sambil "
         "nunggu, biasanya chat paling ramai jam berapa kak?", "oke", {}, False),
        ("kirim media", "[SEND_MEDIA:brosur vira]\nIni brosurnya kak, isinya lengkap soal fitur. Kalau sudah "
         "dibaca, bagian mana yang paling relevan buat bisnis kakak?", "oke", {}, False),
        ("pesan perkenalan", "Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia "
         "bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak "
         "siapa, dan nama usahanya apa?", "halo", {}, True),
        ("tanpa pertanyaan", "Siap kak, makasih ya. Nanti Steven kabari lagi soal decknya. Semoga lancar terus "
         "jualannya.", "oke makasih", {}, False),
        ("sudah pas (1 pengakuan + 1 tanya)", "Noted kak. Dari chat pertama sampai jadi pesan, biasanya lewat "
         "langkah apa aja?", "50an", {}, False),
        ("2 kalimat <= 30 kata, tanpa gema", "Lumayan ramai ya kak. Dari chat pertama sampai jadi pesan, "
         "biasanya lewat langkah apa aja?", "50an", {}, False)]:
    d = proses2(ai, pesan, prev, baru)
    bersih = _re.sub(r"\[[^\]]*\]\n?", "", ai.replace(DECK_BLOK, "")).strip()
    cek("V5  RINGKAS tidak menyentuh: %s" % judul,
        d is not None and d["ringkas"] == "" and d["needs_ringkas_log"] == "false"
        and d["ringkas_asli"] == "" and (d["cleanOutput"].startswith(bersih[:40]) and bersih[-25:] in d["cleanOutput"]),
        str(d and (d["ringkas"], d["cleanOutput"][:90])))

# ---- V6 node baru: IF Ringkas Dipangkas & Log EVENTS Ringkas -------------------
IFR, LOGR = NODES["IF Ringkas Dipangkas"], NODES["Log EVENTS Ringkas"]
_kond = IFR["parameters"]["conditions"]["conditions"]
cek("V6  IF Ringkas: satu kondisi, needs_ringkas_log equals 'true' (pola IF Unknown)",
    len(_kond) == 1 and _kond[0]["leftValue"] == "={{ $json.needs_ringkas_log }}"
    and _kond[0]["rightValue"] == "true" and _kond[0]["operator"]["operation"] == "equals"
    and IFR["type"] == NODES["IF Unknown"]["type"] and IFR["typeVersion"] == NODES["IF Unknown"]["typeVersion"])
_dp = proses2(G4, "semua", {"last_bot_reply": G3})
_dn = proses2("Noted kak. Dari chat pertama sampai jadi pesan, biasanya lewat langkah apa aja?", "50an", {})
cek("V6b ekspresi kondisi -> 'true' saat dipangkas, 'false' saat tidak",
    eval_ekspresi(_kond[0]["leftValue"], _dp)["out"] == "true" and eval_ekspresi(_kond[0]["leftValue"], _dn)["out"] == "false")
cek("V6c Log EVENTS Ringkas: append ke EVENTS di sheet & kredensial yang sama dengan Log EVENTS Delegated",
    LOGR["parameters"]["operation"] == "append"
    and LOGR["parameters"]["documentId"] == NODES["Log EVENTS Delegated"]["parameters"]["documentId"]
    and LOGR["parameters"]["sheetName"] == NODES["Log EVENTS Delegated"]["parameters"]["sheetName"]
    and LOGR.get("credentials") == NODES["Log EVENTS Delegated"].get("credentials")
    and LOGR["type"] == NODES["Log EVENTS Delegated"]["type"])
cek("V6d Log EVENTS Ringkas: gagal tulis tidak menghentikan workflow (onError lanjut, retry 2x)",
    LOGR.get("onError") == "continueRegularOutput" and LOGR.get("retryOnFail") is True and LOGR.get("maxTries") == 2)
_kol = LOGR["parameters"]["columns"]
cek("V6e kolom yang dipetakan = header EVENTS (ts, no_wa, nama, event, detail)",
    sorted(_kol["value"]) == ["detail", "event", "nama", "no_wa", "ts"]
    and [s["id"] for s in _kol["schema"]] == ["ts", "no_wa", "nama", "event", "detail"]
    and _kol["mappingMode"] == "defineBelow")
_ctx = {"Process All": [{"json": _dp}], "Resolve User Row": [{"json": {"resolved_key": "6285171701168"}}],
        "Chat Counter": [{"json": {"user_name": "Steven Leroy"}}]}
_ev = {k: (v if not str(v).startswith("=") else ekspr_node(v, _ctx)) for k, v in _kol["value"].items()}
_evo = {k: (v["out"] if isinstance(v, dict) else v) for k, v in _ev.items()}
cek("V6f ekspresi kolom terevaluasi tanpa error",
    all(not (isinstance(v, dict) and v.get("err")) for v in _ev.values()), str(_ev)[:300])
cek("V6g isi baris EVENTS: no_wa, event RINGKAS, ts epoch",
    _evo["no_wa"] == "6285171701168" and _evo["event"] == "RINGKAS" and isinstance(_evo["ts"], int)
    and abs(_evo["ts"] - NOW_S) < 3600, str({k: _evo[k] for k in ("no_wa", "event", "ts")}))
cek("V6h detail memuat alasan, teks terkirim, dan teks asli model",
    _evo["detail"].startswith("dipangkas: panjang+ekor | terkirim: Kira-kira sehari ada berapa chat masuk kak?")
    and "| asli: Semua jenis chat itu memang makan waktu" in _evo["detail"], _evo["detail"][:200])
cek("V6i nama jatuh ke nama akun WA kalau nama belum tercatat", _evo["nama"] == "Steven Leroy", str(_evo["nama"]))
_anak = [c["node"] for c in CONNS["Process All"]["main"][0]]
cek("V6j Process All -> IF Ringkas Dipangkas terpasang", "IF Ringkas Dipangkas" in _anak, str(_anak))
cek("V6k IF Ringkas (true) -> Log EVENTS Ringkas; cabang false kosong; Log tidak menyambung ke mana pun",
    CONNS["IF Ringkas Dipangkas"]["main"][0] == [{"node": "Log EVENTS Ringkas", "type": "main", "index": 0}]
    and len(CONNS["IF Ringkas Dipangkas"]["main"]) == 1 and "Log EVENTS Ringkas" not in CONNS)
cek("V6l cabang log paling bawah -> dijalankan TERAKHIR (sesudah Wait1 -> kirim WA), executionOrder v1",
    wf["settings"].get("executionOrder") == "v1"
    and all(NODES["IF Ringkas Dipangkas"]["position"][1] > NODES[n]["position"][1] for n in _anak if n != "IF Ringkas Dipangkas"),
    str([(n, NODES[n]["position"][1]) for n in _anak]))
cek("V6m id node baru unik", len({n["id"] for n in wf["nodes"]}) == len(wf["nodes"]))

# ---- V9 temuan eval model asli 2026-09-23 -------------------------------------
_TANYA_MASALAH = "Yang paling bikin repot pas lagi rame, biasanya bagian mananya?"
for pesan, harap in [("100 an chat", "100 an chat"),
                     ("sehari bisa 40 chat kalo lagi musim daftar", "sehari bisa 40 chat kalo lagi musim daftar"),
                     ("oke, chat masuk sehari 50an", "chat masuk sehari 50an"),
                     ("100an chat pas weekend", "100an chat pas weekend"),
                     ("sekitar 20-30 chat sehari", "sekitar 20-30 chat sehari"),
                     ("chatnya\n30an per hari kak", "30an per hari"),
                     ("tanya2 dlu, trs minta pricelist, dan pesen", ""),
                     ("paket 2 sebulan berapa?", ""), ("3 juta sebulan ya", ""), ("ada 2 admin yang bales", ""),
                     ("buka jam 8 sampai 21 tiap hari", ""), ("kdg ribet balesin org ty 1 1", "")]:
    d = tangkap(pesan, _TANYA_MASALAH, prev={"masalah_utama": "chat numpuk"})
    cek("V9  jumlah chat tanpa ditanya: '%s' -> %r" % (pesan.replace("\n", " / "), harap),
        d and d["volume_chat_merged"] == harap, str(d and d["volume_chat_merged"]))
d = tangkap("100 an chat", _TANYA_MASALAH, prev={"masalah_utama": "chat numpuk", "volume_chat": "20"})
cek("V9b jumlah chat lama tidak pernah ditimpa", d and d["volume_chat_merged"] == "20")
d = tangkap("tanya2 dlu, trs minta pricelist, dan pesen", "Kira-kira sehari ada berapa chat masuk kak?")
cek("V9c jawab jumlah chat: 'tanya2' bukan angka (dulu tersimpan sebagai volume_chat)",
    d and d["volume_chat_merged"] == "", str(d and d["volume_chat_merged"]))
d = tangkap("50an", "Kira-kira sehari ada berapa chat masuk kak?")
cek("V9d jawab jumlah chat '50an' tetap tertangkap", d and d["volume_chat_merged"] == "50an")
g, d = galian2(dict({"greeting_sent": "Y", "Counter": "2"}, **_FAKTA4, last_bot_reply=_TANYA_MASALAH), "100 an chat")
cek("V9e eval S1: '100 an chat' tanpa ditanya -> galian jumlah chat TIDAK muncul",
    g is None and "volume_chat: 100 an chat (baru dia sebut di pesan ini)" in d["prospect_context"], str(g))
g, d = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": INTRO_2309}, "Sari dari Bimbel Cerdas Mandiri")
cek("V9f eval S4: 'Bimbel Cerdas Mandiri' -> bidang tidak ditanya, langsung masalah",
    g is not None and g.startswith("masalah terbesarnya") and "industri: bimbel (baru dia sebut" in d["prospect_context"], str(g))
cek("V9g galian_kolom keluar dari Rakit Konteks", d and d.get("galian_kolom") == "masalah_utama", str(d and d.get("galian_kolom")))
g, d = galian2({"greeting_sent": ""}, "halo")
cek("V9h galian_kolom kosong di pesan perkenalan", d and d.get("galian_kolom") == "", str(d and d.get("galian_kolom")))

_DUA = "Oh iya, nama usahanya apa kak? Usahanya bergerak di bidang apa?"
d = proses2(_DUA, "oke", {}, galian_kolom="nama_bisnis")
cek("V9i dua pertanyaan -> sisakan yang menanyakan galian (nama usaha)",
    d and d["cleanOutput"] == "Oh iya, nama usahanya apa kak?" and d["ringkas"] == "satu-tanya",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2(_DUA, "oke", {})
cek("V9j dua pertanyaan tanpa galian -> sisakan yang terakhir",
    d and d["cleanOutput"] == "Usahanya bergerak di bidang apa?" and d["ringkas"] == "satu-tanya",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Siap kak. Chat malam biasanya soal apa? Terus sehari ada berapa chat masuk?", "oke", {},
            galian_kolom="volume_chat")
cek("V9k pengakuan tetap, pertanyaan galian yang disisakan",
    d and d["cleanOutput"] == "Siap kak. Terus sehari ada berapa chat masuk?" and d["ringkas"] == "satu-tanya",
    str(d and (d["cleanOutput"], d["ringkas"])))
_BRIEF_DIAM = DECK_BLOK + "Noted kak, 50 chat sehari itu lumayan ramai. Yang paling bikin repot soal chat sekarang apa kak?"
d = proses2(_BRIEF_DIAM, "oke, chat masuk sehari 50an", {})
cek("V9l eval S3: pembaruan brief diam-diam ([DECK_REQUEST] tanpa menyebut deck) tetap diringkas",
    d and d["cleanOutput"] == "Yang paling bikin repot soal chat sekarang apa kak?" and d["ringkas"] == "gema",
    str(d and (d["cleanOutput"], d["ringkas"])))
cek("V9m ... dan briefnya tetap terbaca", d and d["isDeckRequest"] is True and d["deckRequest"].get("industri") == "konsultan sipil")

_INTRO_ASLI = ("Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk "
               "kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang.")
for judul, ai, harap in [
        ("eval S2: 'mau tanya bagian mana?'",
         _INTRO_ASLI + " Soal chatbot, mau tanya yang bagian mana kak? Btw boleh tau nama kakak siapa, dan nama usahanya apa?",
         _INTRO_ASLI + " Btw boleh tau nama kakak siapa, dan nama usahanya apa?"),
        ("eval S1: 'bidang apa?'",
         _INTRO_ASLI + " Boleh cerita, bisnis kakak bergerak di bidang apa? Dan btw, boleh tau nama kakak siapa dan nama usahanya apa?",
         _INTRO_ASLI + " Dan btw, boleh tau nama kakak siapa dan nama usahanya apa?"),
        ("perkenalan asli 23/09", INTRO_2309,
         "Halo kak, salam kenal! Aku Steven versi AI, dibangun sama Steven pakai sistem yang sama yang dia bikin "
         "untuk kliennya, namanya VIRA. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Senang kakak "
         "tertarik setelah lihat website-nya. Btw boleh tau nama kakak siapa, dan nama usahanya apa?")]:
    d = proses2(ai, "Halo kak, mau tanya soal chatbot", {}, baru=True)
    cek("V9n perkenalan (%s) -> hanya pertanyaan nama + nama usaha" % judul,
        d and d["cleanOutput"] == harap and d["ringkas"] == "perkenalan", str(d and (d["cleanOutput"], d["ringkas"])))
_TANPA_NAMA = (_INTRO_ASLI + " VIRA ini intinya AI customer service WhatsApp: balas chat otomatis 24 jam. "
               "Kakak sendiri usahanya di bidang apa?")
d = proses2(_TANPA_NAMA, "Halo, ini bisa buat apa aja ya?", {}, baru=True)
cek("V9o perkenalan TANPA pertanyaan nama (eval S3) -> pertanyaan lain diganti pertanyaan baku nama + nama usaha",
    d and d["cleanOutput"] == _INTRO_ASLI + " VIRA ini intinya AI customer service WhatsApp: balas chat otomatis 24 jam. "
    "Btw boleh tau nama kakak siapa, dan nama usahanya apa?" and d["ringkas"] == "perkenalan",
    str(d and (d["cleanOutput"][-80:], d["ringkas"])))
cek("V9o' pertanyaan baku itu terbaca detektor sebagai nama + nama usaha (jadi jawabannya tertangkap)",
    detek("Btw boleh tau nama kakak siapa, dan nama usahanya apa?") == ["nama_bisnis", "nama_lengkap"]
    and detek("Btw boleh tau nama kakak siapa?") == ["nama_lengkap"] and detek("Btw nama usahanya apa kak?") == ["nama_bisnis"])
d = proses2(_INTRO_ASLI + " Btw boleh tau nama kakak siapa, dan nama usahanya apa?", "halo", {}, baru=True)
cek("V9p perkenalan yang sudah pas tidak disentuh", d and d["ringkas"] == "" and d["needs_ringkas_log"] == "false")

# ---- V10 temuan eval putaran 2 --------------------------------------------------
g, d = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": PERKENALAN_BARU}, JAWAB_1709)
cek("V10  eval S2: ada galian -> format_balasan menunjuk galian itu sebagai SATU-SATUNYA pertanyaan",
    g is not None and "dan pertanyaan itu adalah galian_berikutnya di atas (bukan pertanyaan lain)" in d["prospect_context"],
    str(g)[:60])
g, d = galian2(dict({"greeting_sent": "Y", "Counter": "2"}, **_FAKTA4, last_bot_reply=_TANYA_MASALAH), "100 an chat")
cek("V10b tanpa galian -> format_balasan tanpa rujukan galian",
    g is None and "format_balasan: dia tidak sedang bertanya" in d["prospect_context"]
    and "adalah galian_berikutnya" not in d["prospect_context"])
_LALU_DECK = ("Siap kak, brief-nya sudah aku teruskan ke Steven. Dia sendiri yang bakal nyusun deck-nya dan langsung "
              "hubungin kakak. Sambil nunggu, dari chat pertama sampai jadi reservasi biasanya lewat langkah apa aja kak?")
d = proses2("Sama-sama kak. Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja?", "makasih kak",
            {"last_bot_reply": _LALU_DECK})
cek("V10c eval S5: pertanyaan yang sama dengan balasan sebelumnya tidak diulang",
    d and d["cleanOutput"] == "Sama-sama kak." and d["ringkas"] == "tanya-ulang", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja?", "oke", {"last_bot_reply": _LALU_DECK})
cek("V10d kalau yang tersisa cuma pertanyaan kembar itu -> dibiarkan (tidak mengirim teks kosong)",
    d and d["cleanOutput"] == "Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja?" and d["ringkas"] == "",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Sama-sama kak. Yang paling sering ditanyain biasanya apa aja?", "makasih kak", {"last_bot_reply": _LALU_DECK})
cek("V10e pertanyaan BERBEDA tidak tersentuh", d and d["ringkas"] == "" and d["cleanOutput"].endswith("apa aja?"))
_INTRO_S5 = ("Halo kak, salam kenal. Aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin "
             "buat kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh aku tau dulu, chat di Kopi "
             "Senja biasanya kayak gimana kak? Yang paling bikin repot sekarang apa?")
d = proses2(_INTRO_S5, "Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat", {}, baru=True)
cek("V10f eval S5: perkenalan tanpa pertanyaan nama tapi 2 pertanyaan -> sisakan yang terakhir",
    d and d["cleanOutput"].endswith("contoh hasilnya sekarang. Yang paling bikin repot sekarang apa?")
    and "kayak gimana" not in d["cleanOutput"] and d["ringkas"] == "perkenalan", str(d and (d["cleanOutput"][-90:], d["ringkas"])))
d = proses2("100 chat itu lumayan ya kak. Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja kak?",
            "100an chat pas weekend", {})
cek("V10g eval S5: '100an' dikenali sama dengan '100' -> kalimat gema dibuang",
    d and d["cleanOutput"] == "Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja kak?"
    and d["ringkas"] == "gema", str(d and (d["cleanOutput"], d["ringkas"])))

# ---- V11 temuan eval putaran 3 --------------------------------------------------
# (a) pertanyaan kembar: galian tanya ulang nama usaha dikecualikan
_KEMBAR = "Salam kenal kak. Nama usahanya apa ya kak?"
d = proses2(_KEMBAR, "coffee shop kak, chat reservasi numpuk pas weekend", {"last_bot_reply": PERKENALAN_BARU},
            galian_kolom="nama_bisnis")
cek("V11  eval S5/S2: galian tanya ulang nama usaha TIDAK dibuang walau mirip pertanyaan perkenalan",
    d and d["cleanOutput"] == _KEMBAR and d["ringkas"] == "", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2(_KEMBAR, "coffee shop kak, chat reservasi numpuk pas weekend", {"last_bot_reply": PERKENALAN_BARU})
cek("V11b tanpa galian -> pertanyaan kembar itu dibuang", d and d["cleanOutput"] == "Salam kenal kak." and d["ringkas"] == "tanya-ulang",
    str(d and (d["cleanOutput"], d["ringkas"])))
_LALU_HARGA = ("Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan. Boleh aku tau, di klinik kakak "
               "sehari kira-kira berapa chat masuk?")
d = proses2("Bisa kak, VIRA bisa pegang chat dari Instagram juga. Kira-kira sehari ada berapa chat masuk ke klinik kakak?",
            "bisa connect ke IG juga ga?", {"last_bot_reply": _LALU_HARGA})
cek("V11c eval S3: prospek BERTANYA -> jawaban utuh, hanya pertanyaan kembarnya yang dibuang",
    d and d["cleanOutput"] == "Bisa kak, VIRA bisa pegang chat dari Instagram juga." and d["ringkas"] == "tanya-ulang",
    str(d and (d["cleanOutput"], d["ringkas"])))
# (b) nama usaha mustahil
for pesan, lalu in [("makasih kak", TAWARAN_LIVE), ("boleh dong dibuatin deck", TAWARAN_LIVE),
                    ("sekitar 20-30 chat sehari", "Oh iya, nama usahanya apa kak?"),
                    ("oke siap", "Oh iya, nama usahanya apa kak?")]:
    d = tangkap(pesan, lalu)
    cek("V11d eval S5/S2: '%s' BUKAN nama usaha" % pesan, d and d["nama_bisnis_merged"] == "", str(d and d["nama_bisnis_merged"]))
for pesan, harap in [("Kopi Senja", "Kopi Senja"), ("namanya Toko Wangi kak", "Wangi"), ("boleh kak, namanya Teamsultan", "Teamsultan")]:
    d = tangkap(pesan, "Oh iya, nama usahanya apa kak?")
    cek("V11e nama usaha asli tetap tertangkap: '%s'" % pesan, d and d["nama_bisnis_merged"] == harap, str(d and d["nama_bisnis_merged"]))
# (c) perkenalan diri di pesan pertama
_S5_1 = "Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat"
d = proses2("Halo kak, salam kenal. Aku Steven versi AI. Yang paling bikin repot soal chat sekarang apa kak?", _S5_1, {}, baru=True)
cek("V11f eval S5: pesan pertama 'aku Rina dari Kopi Senja' -> nama, nama usaha, industri tercatat",
    d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"]) == ("Rina", "Kopi Senja", "kopi"),
    str(d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"])))
cek("V11g ... dan karena keduanya sudah diketahui, balasan tanpa pertanyaan nama tidak diubah",
    d and d["ringkas"] == "" and d["cleanOutput"].endswith("Yang paling bikin repot soal chat sekarang apa kak?"))
for pesan, harap in [("Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku.", ("", "", "")),
                     ("Halo, saya owner toko kue, mau tanya", ("", "", "kue")),
                     ("halo kak saya mau tanya harga", ("", "", "")),
                     ("aku seorang ibu rumah tangga, jualan kue", ("", "", "jualan kue")),
                     ("Halo, ini bisa buat apa aja ya?", ("", "", ""))]:
    d = proses2("Halo kak, aku Steven versi AI. Btw boleh tau nama kakak siapa, dan nama usahanya apa?", pesan, {}, baru=True)
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"])
    cek("V11h pesan pertama '%s' -> %s" % (pesan[:40], harap), got == harap, str(got))
g, d = galian2({"greeting_sent": ""}, _S5_1)
cek("V11i Rakit Konteks: perkenalan diri lengkap -> perkenalan tidak menanyakan nama/usaha lagi",
    g is None and "nama_bisnis: Kopi Senja (baru dia sebut di pesan ini)" in d["prospect_context"], str(g))
g, d = galian2({"greeting_sent": ""}, "halo kak, aku Rina")
cek("V11j perkenalan diri tanpa nama usaha -> tanya nama usaha saja", g is not None and g.startswith("nama usahanya — tanyakan di"), str(g))
d = proses2("Halo kak, aku Steven versi AI. Senang kenalan. Kakak jualan apa?", "halo kak, aku Rina", {}, baru=True)
cek("V11k nama sudah disebut, nama usaha belum, model lupa -> pertanyaan diganti 'nama usahanya apa'",
    d and d["cleanOutput"] == "Halo kak, aku Steven versi AI. Senang kenalan. Btw nama usahanya apa kak?", str(d and d["cleanOutput"]))
# (d) model hanya menulis tag
_TAG_SAJA = '[FACTS nama="Sari" nama_bisnis="Bimbel Cerdas Mandiri" industri="bimbel"]'
d = proses2(_TAG_SAJA, "Sari dari Bimbel Cerdas Mandiri", {"last_bot_reply": PERKENALAN_BARU}, galian_kolom="masalah_utama")
cek("V11l eval S4: balasan cuma tag -> pertanyaan galian, bukan 'Maaf, ada kendala'",
    d and d["cleanOutput"] == "Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak?"
    and d["ringkas"] == "cadangan-galian" and d["needs_ringkas_log"] == "true", str(d and (d["cleanOutput"], d["ringkas"])))
cek("V11m ... fakta dari tag tetap tersimpan", d and d["nama_bisnis_merged"] == "Bimbel Cerdas Mandiri" and d["nama_lengkap_merged"] == "Sari")
d = proses2(_TAG_SAJA, "Sari dari Bimbel Cerdas Mandiri", {"last_bot_reply": PERKENALAN_BARU})
cek("V11n tanpa galian -> kalimat cadangan lama tetap", d and d["cleanOutput"] == "Maaf, ada kendala sebentar. Boleh diketik ulang yaa.")
d = proses2("[UNKNOWN]", "sistemnya pakai server mana?", {}, galian_kolom="masalah_utama")
cek("V11o [UNKNOWN] saja -> kalimat 'belum tahu' tetap (bukan pertanyaan galian)",
    d and d["cleanOutput"].startswith("Maaf yaa, untuk yang ini aku belum tahu"))
for kol, harap in [("nama_bisnis", ["nama_bisnis"]), ("industri", ["industri"]), ("masalah_utama", ["masalah_utama"]),
                   ("volume_chat", ["volume_chat"])]:
    d = proses2("[FACTS]", "oke", {}, galian_kolom=kol)
    cek("V11p kalimat cadangan untuk galian %s terbaca detektor sebagai %s" % (kol, harap),
        d and detek(d["cleanOutput"]) == harap, str(d and d["cleanOutput"]))

# ---- V12 temuan eval putaran 4 --------------------------------------------------
_BASIS = {"greeting_sent": "Y", "Counter": "4", "nama_lengkap": "Rina", "nama_bisnis": "Kopi Senja",
          "industri": "kopi", "masalah_utama": "chat numpuk"}
g, d = galian2(dict(_BASIS, last_bot_reply="Kalau lagi numpuk gitu, ada yang kelewat nggak kak?"), "boleh dong dibuatin deck")
cek("V12  eval S5: 'boleh dong dibuatin deck' -> format_balasan: kabari brief diteruskan, bukan tawaran",
    "format_balasan: dia MINTA / SETUJU dibuatkan deck" in d["prospect_context"] and g is None
    and d.get("galian_kolom") == "", d["prospect_context"][-200:])
g, d = galian2(dict(_BASIS, deck_requested="Y", last_bot_reply="Siap kak."), "boleh dong dibuatin deck")
cek("V12b sudah pernah minta deck -> tidak memaksa pengumuman kedua", "dia MINTA / SETUJU" not in d["prospect_context"])
for pesan, lalu in [("boleh dong dibuatin deck", "Kalau lagi numpuk gitu, ada yang kelewat nggak kak?"),
                    ("boleh", TAWARAN_LIVE), ("mau kak", TAWARAN_LIVE), ("boleh telepon aja", TAWARAN_LIVE),
                    ("oke", "Sehari berapa chat masuk kak?"), ("tolong bikinin proposal", "Siap kak."),
                    ("mau tanya harga dulu", TAWARAN_LIVE), ("boleh, tapi aku mau ngobrol langsung sama steven", TAWARAN_LIVE)]:
    _, drk = galian2(dict(_BASIS, last_bot_reply=lalu), pesan)
    dpa = proses2("Siap kak.", pesan, {"last_bot_reply": lalu})
    cek("V12c Rakit Konteks & Process All sepakat soal minta deck: '%s'" % pesan,
        ("dia MINTA / SETUJU dibuatkan deck" in drk["prospect_context"]) == bool(dpa["deckDiminta"]),
        "RK=%s PA=%s" % ("dia MINTA" in drk["prospect_context"], dpa["deckDiminta"]))
_rkc = NODES["Rakit Konteks"]["parameters"]["jsCode"]
_pac = NODES["Process All"]["parameters"]["jsCode"]
for _nama, _pola in [("NIAT_DECK", r"const NIAT_DECK   = (/.+?/);\n"), ("NIAT_BICARA", r"const NIAT_BICARA = (/.+?/);\n"),
                     ("TAWARAN_DECK", r"const TAWARAN_DECK  = (/.+?/)\.test"),
                     ("SETUJU_PENDEK", r"const SETUJU_PENDEK = PESAN_USER\.length <= 40\n  && (/.+?/)\.test")]:
    _lit = _re.search(_pola, _pac).group(1)
    cek("V12d regex %s di Rakit Konteks = salinan persis dari Process All" % _nama, _lit in _rkc)
d = proses2('Oh iya, nama usahanya Dapur Nadia ya kak? Usahanya bergerak di bidang apa kak?\n[FACTS nama_bisnis="Dapur Nadia"]',
            "Dapur Nadia",
            {"nama_lengkap": "Nadia", "industri": "katering"}, galian_kolom="nama_bisnis")
cek("V12e eval S2: pertanyaan bidang padahal bidang sudah diketahui -> dibuang",
    d and d["cleanOutput"] == "Oh iya, nama usahanya Dapur Nadia ya kak?" and d["ringkas"] == "sudah-tahu",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Kira-kira sehari ada berapa chat masuk kak?", "sekitar 20-30 chat sehari", {}, galian_kolom="masalah_utama")
cek("V12f eval S2: jumlah chat ditanya sesudah dia menyebutnya -> diganti pertanyaan galian",
    d and d["cleanOutput"] == "Soal chat, yang paling bikin repot sekarang apa kak?" and d["ringkas"] == "sudah-tahu",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Kira-kira sehari ada berapa chat masuk kak?", "sekitar 20-30 chat sehari", {})
cek("V12g ... tanpa galian -> dibiarkan (tidak mengirim teks kosong)",
    d and d["cleanOutput"] == "Kira-kira sehari ada berapa chat masuk kak?" and d["ringkas"] == "")
d = proses2("Siap kak. Pas lagi ramai gitu, yang paling bikin repot bagian mananya kak?", "oke", {"masalah_utama": "chat numpuk"})
cek("V12h pertanyaan lanjutan soal masalah (akibat) TIDAK dianggap 'sudah tahu'", d and d["ringkas"] == "")
d = proses2("Noted kak. Chat yang numpuk pas malem itu biasanya isinya apa aja kak?", "Dapur Nadia",
            {"last_bot_reply": "Chat yang numpuk pas malem itu biasanya isinya apa aja kak?"}, galian_kolom="nama_bisnis")
cek("V12i eval S2: pertanyaan kembar dibuang -> pertanyaan galian dikirim, bukan 'Noted kak.' saja",
    d and d["cleanOutput"] == "Noted kak. Oh iya, nama usahanya apa kak?" and d["ringkas"] == "tanya-ulang+galian",
    str(d and (d["cleanOutput"], d["ringkas"])))

# ---- V7 prompt & teks galian --------------------------------------------------
_sp1 = _sp.replace("\n", " ")
cek("V7  ALUR 10 membuang promosi yang tidak ditanya",
    "kalimat promosi VIRA yang tidak dia tanyakan (lihat GAYA)" in _sp1)
cek("V7b GAYA melarang promosi di setiap balasan + ekor alasan",
    "JANGAN BERJUALAN DI SETIAP BALASAN" in _sp and "ekor alasan di pertanyaan" in _sp)
cek("V7c promosi VIRA hanya kalau ditanya / satu kalimat di tawaran deck",
    "Kemampuan VIRA baru kujelaskan kalau dia menanyakannya, atau dalam SATU kalimat di balasan yang menawarkan deck" in _sp1)
cek("V7d aturan lama yang mendorong rangkuman/promosi sudah hilang",
    "satu yang menanggapi, satu yang" not in _sp1 and "harus MENAMBAH sesuatu" not in _sp1
    and "Lumayan buat dibalas sendiri" not in _sp1)
cek("V7e GAYA merujuk format_balasan, dan Rakit Konteks benar-benar menulisnya",
    "`format_balasan`" in _sp and "format_balasan: " in NODES["Rakit Konteks"]["parameters"]["jsCode"])
_perk = _sp.split("# PERKENALAN")[1].split("\n# NAMA LAWAN BICARA")[0]
_tpl = _re.search(r'\n"(Halo kak, aku Steven versi AI[^"]+)"', _perk)
cek("V7f contoh perkenalan <= 2 kalimat & <= 30 kata",
    _tpl is not None and len(_re.findall(r"[.?!](?:\s|$)", _tpl.group(1))) <= 2 and len(_tpl.group(1).split()) <= 30,
    str(_tpl and len(_tpl.group(1).split())))
cek("V7g perkenalan melarang basa-basi & menawarkan pilihan (pola asli 23/09)",
    '"senang kakak tertarik"' in _perk and '"mau cerita dulu atau langsung tanya?"' in _perk)
cek("V7h tidak ada 'cerita sedikit/cerita singkat' di prompt maupun Rakit Konteks",
    "cerita sedikit" not in _sp and not any(
        "cerita singkat" in l for l in NODES["Rakit Konteks"]["parameters"]["jsCode"].splitlines()
        if not l.strip().startswith("//")))
cek("V7i contoh prompt tidak memuat nama/usaha uji (abdul, humanizer)",
    "abdul" not in _sp.lower() and "humanizer" not in _sp.lower())

# ---- V8 kode bersama identik -------------------------------------------------
_PA = NODES["Process All"]["parameters"]["jsCode"]
_RK = NODES["Rakit Konteks"]["parameters"]["jsCode"]
_blok = lambda s: s[s.index("// ── PENANGKAP JAWABAN — MULAI ──"):s.index("// ── PENANGKAP JAWABAN — SELESAI ──")]
cek("V8  blok PENANGKAP JAWABAN identik di Process All dan Rakit Konteks", _blok(_PA) == _blok(_RK))
_bersih = lambda s: _re.search(r"const BERSIH = [^;]+;", s, _re.S).group(0)
cek("V8b fungsi BERSIH identik di dua node", _bersih(_PA) == _bersih(_RK))
_rx = lambda s, nama: _re.search(r"const " + nama + r" = (/.+?/i)\.test", s).group(1)
cek("V8c definisi 'prospek bertanya' sama di dua node", _rx(_PA, "PROSPEK_BERTANYA") == _rx(_RK, "pesanBertanya"))
cek("V8d Process All: penangkap satu slot tetap jalan SEBELUM penangkap perkenalan",
    _PA.index("if (slotDitanyaLalu.length === 1)") < _PA.index("if (slotDitanyaLalu.includes('nama_lengkap')"))
cek("V8e Process All: RINGKAS jalan sesudah tag dibuang & sebelum media/penghapus nama",
    _PA.index("let cleanOutput = aiOutput") < _PA.index("// ── RINGKAS (2026-09-23) ──")
    < _PA.index("// ── RESOLVE MEDIA URL") < _PA.index("const namaSimpan"))


# ===========================================================================
'''
ganti('bagian("R. BEDAH REGRESI v3.11 vs v3.10', SEKSI_V + 'bagian("R. BEDAH REGRESI v3.11 vs v3.10')

# --- 4. seksi R ditulis ulang: v3.12 vs v3.11 ----------------------------
SEKSI_R = r'''bagian("R. BEDAH REGRESI v3.12 vs v3.11 (= live 2026-09-23)")
# ===========================================================================
import collections as _col
import copy as _copy
with open(os.path.join(DIR, "2026-09-22-VIRA-Personal-Main-v3.11.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Process All", "Rakit Konteks"}
BARU = {"IF Ringkas Dipangkas", "Log EVENTS Ringkas"}

cek("R1  node = 89 node v3.11 + 2 node baru", set(NODES) == set(_NL) | BARU and len(wf["nodes"]) == 91,
    str(sorted(set(NODES) ^ (set(_NL) | BARU))))
_harap = _copy.deepcopy(_lama["connections"])
_harap["Process All"]["main"][0].append({"node": "IF Ringkas Dipangkas", "type": "main", "index": 0})
_harap["IF Ringkas Dipangkas"] = {"main": [[{"node": "Log EVENTS Ringkas", "type": "main", "index": 0}]]}
cek("R2  koneksi = koneksi v3.11 + tepat 2 kabel baru",
    json.dumps(_harap, sort_keys=True) == json.dumps(CONNS, sort_keys=True))
_beda = sorted(n for n in _NL if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  86 node lain identik byte per byte dengan v3.11", not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))
_s0, _s1 = dict(_lama["settings"]), dict(wf["settings"])
cek("R4b settings: hanya availableInMCP yang berubah (false -> true, sama dengan live)",
    _s1.pop("availableInMCP") is True and _s0.pop("availableInMCP") is False and _s0 == _s1)
cek("R4c kredensial tiap node lama tetap", all(NODES[n].get("credentials") == _NL[n].get("credentials") for n in _NL))
cek("R4d webhookId tiap node lama tetap", all(NODES[n].get("webhookId") == _NL[n].get("webhookId") for n in _NL))


def _hilang(lama, baru):
    """Baris lama (tanpa baris kosong) yang tidak ada lagi di kode baru, dihitung sebagai multiset."""
    sisa = _col.Counter(l for l in baru.split("\n"))
    keluar = []
    for l in lama.split("\n"):
        if not l.strip():
            continue
        if sisa[l] > 0:
            sisa[l] -= 1
        else:
            keluar.append(l.strip())
    return keluar


# ---- Process All ---------------------------------------------------------------
_pa0, _pa1 = _NL["Process All"]["parameters"]["jsCode"], NODES["Process All"]["parameters"]["jsCode"]
_IZIN_PA = {
    "const JENIS_USAHA = ",                                     # + parfum, aksesoris, ...
    ".flatMap(pecahDiPenanda).map(s => s.trim()).filter(Boolean).slice(0, 4);",
    "const diri  = bagian.filter(s => PENANDA_DIRI.test(s));",
    "const usaha = bagian.filter(s => !PENANDA_DIRI.test(s) && PENANDA_USAHA.test(s));",
    "const polos = bagian.filter(s => !PENANDA_DIRI.test(s) && !PENANDA_USAHA.test(s));",
    "const calonNama = diri[0] || polos.shift() || '';",
    "const nama = calonNama ? ambilJawaban('nama_lengkap', calonNama) : '';",
    "if (JENIS_USAHA.test(isi)) { if (!hasil.industri) hasil.industri = isi; continue; }",
    "if (!/\\d|\\b(puluhan|belasan|ratusan|ribuan|seratus|sepuluh|sedikit|dikit|banyak|lumayan)\\b/i.test(baris1)) return '';",
}
_x = [l for l in _hilang(_pa0, _pa1) if not any(l.startswith(i) for i in _IZIN_PA)]
cek("R5  Process All: tidak ada baris v3.11 yang hilang selain 9 baris penangkap yang memang diganti", not _x, str(_x))
cek("R5b Process All: 9 baris itu memang tidak ada lagi",
    len([l for l in _hilang(_pa0, _pa1) if any(l.startswith(i) for i in _IZIN_PA)]) == 9)
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):
                   s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
_rk0, _rk1 = _NL["Rakit Konteks"]["parameters"]["jsCode"], NODES["Rakit Konteks"]["parameters"]["jsCode"]
cek("R6  detektor galian IDENTIK di dua node dan tidak berubah dari v3.11",
    _det(_pa1) == _det(_rk1) == _det(_pa0) == _det(_rk0))
for _k in ("const matikanBot = isTalkToAdmin && mintaBicara;", "const TAWARAN_DISKUSI =", "const NIAT_BICARA =",
           "const mintaDeck =", "last_bot_reply: cleanOutput,"):
    cek("R6b baris kunci v3.11 utuh: %s" % _k[:40], _pa1.count(_k) == 1)

# ---- Rakit Konteks ---------------------------------------------------------------
_IZIN_RK = {
    "+ 'lalu tanyakan bidang usahanya sekaligus minta cerita singkat',",
    "{ kolom: 'industri',      teks: 'bidang usahanya, sekaligus minta dia cerita singkat tentang usahanya',",
    "boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 8 && (!!txt(stats['industri']) || giliran > 6) },",
    "boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 3 && giliran <= 10 && !!txt(stats['masalah_utama']) },",
    "if (txt(stats[g.kolom]) || !g.boleh()) continue;",
    "if (txt(stats['nama_lengkap'])) {",
    "const kurang = GALIAN.filter(g => g.boleh() && !txt(stats[g.kolom])).map(g => g.teks);",
}
_x = [l for l in _hilang(_rk0, _rk1) if l not in _IZIN_RK]
cek("R7  Rakit Konteks: tidak ada baris v3.11 yang hilang selain 7 baris galian yang memang diganti", not _x, str(_x))
cek("R7b Rakit Konteks: galian perkenalan memakai STATS + perkenalan diri di pesan pertama",
    "const kurang = GALIAN.filter(g => g.boleh() && !txt(statsGalian[g.kolom])).map(g => g.teks);" in _rk1)
cek("R7c tujuh blok konteks masih dirakit",
    all(("const " + k) in _rk1 or (k + " =") in _rk1 for k in
        ("prospect_context", "about_context", "program_context", "links_context", "faq_context",
         "brief_context", "deck_context")))

# ---- system prompt ---------------------------------------------------------------
_sp0 = _NL["AI Agent"]["parameters"]["options"]["systemMessage"]
_bag = lambda s: {b.split("\n", 1)[0]: b for b in ("\n" + s).split("\n# ")[1:]}
_b0, _b1 = _bag(_sp0), _bag(_sp)
cek("R8  urutan & nama heading prompt tetap", list(_b0) == list(_b1), str(list(_b1)))
_ubah = sorted(h for h in _b0 if _b0[h] != _b1.get(h))
cek("R8b hanya ALUR, PERKENALAN, GAYA, MENGGALI yang berubah",
    _ubah == ["ALUR", "GAYA", "MENGGALI", "PERKENALAN"], str(_ubah))
cek("R8c tujuh ekspresi {{ }} tetap utuh", len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 7)
cek("R8d prompt tidak menambah angka harga",
    not _re.search(r"3\.000\.000|5\.000\.000|\b999\b", "\n".join(_b1[h] for h in _ubah)))
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R9  AI Agent: selain systemMessage identik", _pl == _pb)
cek("R10 DeepSeek Personal Chat & Simple Memory tidak disentuh (temperature 0.7, maxTokens, window)",
    NODES["DeepSeek Personal Chat"] == _NL["DeepSeek Personal Chat"] and NODES["Simple Memory"] == _NL["Simple Memory"]
    and NODES["DeepSeek Personal Chat"]["parameters"]["options"].get("temperature") == 0.7)
cek("R11 cermin prompt .md sama persis dengan systemMessage",
    io.open(os.path.join(DIR, "2026-09-23-system-prompt-VIRA-Personal-v3.12.md"),
            encoding="utf-8").read() == (_sp[1:] if _sp.startswith("=") else _sp))



# ===========================================================================
print()
print("=" * 72)
print("RINGKASAN UAT")'''
ganti_blok('bagian("R. BEDAH REGRESI v3.11 vs v3.10', 'print("RINGKASAN UAT")', SEKSI_R)

# --- 5. daftar UAT manual untuk v3.12 --------------------------------------
_i = teks.index("for i, langkah in enumerate([")
_j = teks.index("], 1):", _i)
teks = teks[:_i] + r'''for i, langkah in enumerate([
    "DEPLOY — import 2026-09-23-VIRA-Personal-Main-v3.12.json, nonaktifkan Main lama, aktifkan v3.12. Tidak ada kolom baru.",
    "ULANG UJI 23/09 — hapus baris STATS nomor uji dulu, lalu kirim persis: 'Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku.' Perkenalan <= 3 kalimat, TANPA 'senang kakak tertarik' dan TANPA 'mau cerita dulu atau langsung tanya'.",
    "Balas 4 baris: 'abdul' / 'aku owner humanizer' / 'jualan parfum' / 'kdg ribet balesin org ty 1 1'. VIRA TIDAK menanyakan nama usaha/brand lagi. STATS: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama terisi.",
    "Lanjut beberapa giliran (100 an chat / tanya2 dlu, trs minta pricelist, dan pesen / ...): tiap balasan 1-2 kalimat, tidak membuka dengan merangkum, tidak menjelaskan VIRA kalau tidak ditanya.",
    "Tanya 'bisa buat apa aja?' atau 'harganya berapa?': jawabannya TETAP lengkap (tidak terpotong jadi satu pertanyaan).",
    "Tab EVENTS: kalau ada balasan yang dipangkas, muncul baris event RINGKAS berisi teks asli model dan teks yang terkirim.",
    "Sampai tawaran deck lalu jawab 'boleh': notif brief tetap masuk ke Steven dan REQUESTS terisi (tag tidak terganggu).",
    "Hapus workflow 'VIRA Eval — Balasan (sementara)' sesudah uji selesai.",
''' + teks[_j:]

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(teks)
print("OK ->", os.path.basename(DST))
