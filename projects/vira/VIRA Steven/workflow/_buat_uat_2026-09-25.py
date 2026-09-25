# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-25.py - turunkan _uat_2026-09-25.py dari harness _uat_2026-09-23b.py (v3.13).

Harness v3.13 diarahkan ulang ke v3.14. Seksi A-Q, S-W ikut jalan sebagai regresi tanpa diubah.
Seksi baru:
  X. INSIDEN LIVE 2026-09-25 - "Brp" sesudah sapaan (Reza, iklan IG). Input & keluaran model PERSIS
     dari output Process All live. Tiap cek utama dijalankan dua kali: kode v3.13 harus
     MEREPRODUKSI insidennya (kalau tidak, ujinya tidak membuktikan apa-apa), kode v3.14 harus lolos.
Seksi R ditulis ulang: membedah v3.14 terhadap v3.13 (= live).

Jalankan: python _buat_uat_2026-09-25.py   (lalu: python _uat_2026-09-25.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-23b.py")
DST = os.path.join(DIR, "_uat_2026-09-25.py")

with io.open(SRC, encoding="utf-8") as f:
    teks = f.read()


def ganti(lama, baru):
    global teks
    assert teks.count(lama) == 1, "anchor tidak tunggal (%d): %r" % (teks.count(lama), lama[:90])
    teks = teks.replace(lama, baru, 1)


ganti("""_uat_2026-09-23b.py — UAT perilaku untuk 2026-09-23-VIRA-Personal-Main-v3.13.json.

Diturunkan dari _uat_2026-09-23.py (jangan diedit manual — ubah generatornya,
_buat_uat_2026-09-23b.py, lalu jalankan ulang). Seksi A-Q, S, T, U dan V ikut jalan sebagai
regresi (hanya V5 'menyebut harga' yang disesuaikan); seksi W baru untuk uji live Steven
2026-09-23 13:22-13:45 (Rehan); seksi R membedah v3.13 terhadap v3.12.
""", """_uat_2026-09-25.py — UAT perilaku untuk 2026-09-25-VIRA-Personal-Main-v3.14.json.

Diturunkan dari _uat_2026-09-23b.py (jangan diedit manual — ubah generatornya,
_buat_uat_2026-09-25.py, lalu jalankan ulang). Seksi A-Q, S-W ikut jalan sebagai regresi;
seksi X baru untuk insiden live 2026-09-25 ("Brp", Reza); seksi R membedah v3.14 terhadap v3.13.
""")
ganti('Jalankan: python _uat_2026-09-23b.py\n', 'Jalankan: python _uat_2026-09-25.py\n')
ganti('WF = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json")\n',
      'WF = os.path.join(DIR, "2026-09-25-VIRA-Personal-Main-v3.14.json")\n')
ganti('print("UAT PERILAKU — VIRA Personal v3.13 (2026-09-23)")\n',
      'print("UAT PERILAKU — VIRA Personal v3.14 (2026-09-25)")\n')

# ---- seksi X + R baru menggantikan R lama (sampai sebelum RINGKASAN) -----------------------------
AWAL_R = '# ===========================================================================\nbagian("R. BEDAH REGRESI v3.13 vs v3.12'
AKHIR_R = '\n\n\n# ===========================================================================\nprint()\nprint("=" * 72)\nprint("RINGKASAN UAT")'
assert teks.count(AWAL_R) == 1 and teks.count(AKHIR_R) == 1
i = teks.index(AWAL_R)
j = teks.index(AKHIR_R, i)

SEKSI_BARU = r'''# ===========================================================================
bagian("X. INSIDEN LIVE 2026-09-25 — 'Brp' sesudah sapaan (Reza, iklan IG, 6285199701359)")
# ===========================================================================
# Data PERSIS dari output Process All live 2026-09-25 12:19-12:20 (ditempel Steven):
SAPAAN_REZA = ("Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia buat untuk "
               "kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw, boleh tau nama kakak siapa "
               "dan nama usahanya apa?")
AI_INPUT_REZA = ("[SYSTEM_DATA]\nUSER_WA: 6285199701359\nIS_NEW_USER: false\nNAMA_LENGKAP: UNKNOWN\n"
                 "TANGGAL_SEKARANG: 2026-09-25 (Jumat) 12:20 WIB\n\n"
                 "BALASAN TERAKHIRMU YANG BENAR-BENAR DITERIMA PROSPEK:\n\"" + SAPAAN_REZA + "\"\n"
                 "Pesan prospek di bawah adalah tanggapan atas kalimat itu. Kalau ingatanmu berbeda, kalimat di "
                 "atas yang benar.\n\nCRITICAL INSTRUCTION:\nUser lama. JANGAN memperkenalkan diri lagi, lanjutkan "
                 "percakapan secara natural.\n\n[USER QUERY]\nBrp")
MODEL_REZA = "Salam kenal kak. Nama usahanya apa ya?"          # keluaran AI Agent live
BARIS_REZA = {"greeting_sent": "Y", "Counter": "1", "last_bot_reply": SAPAAN_REZA}
HARGA_REZA = ("Untuk VIRA ada dua paket kak: Basic mulai Rp3.000.000 per bulan dan Premium Rp5.000.000 per bulan, "
              "angka finalnya dibicarakan langsung sama Steven. Btw, nama usahanya apa kak?")

with open(os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json"), encoding="utf-8") as _f:
    _V313 = {n["name"]: n for n in json.load(_f)["nodes"]}


def di_v313(fn):
    """Jalankan fn dengan kode node v3.13 (= live saat insiden)."""
    simpan = dict(NODES)
    NODES.update(_V313)
    try:
        return fn()
    finally:
        NODES.clear()
        NODES.update(simpan)


def pre_live(teks, lalu):
    """Preprocess ASLI dengan ai_input_text live dan balasan terakhir dari Resolve User Row."""
    return satu(jalan("Preprocess - Context Detection",
                      nodes={"Parse Config": [item(config=cfg())],
                             "Resolve User Row": [item(last_bot_reply=lalu)]},
                      inp=[item(ai_input_text=teks, user_wa="6285199701359")]))


def replay_reza(ai_output, pesan="Brp", teks_input=None):
    """Rantai live: Preprocess asli -> Rakit Konteks asli (galian_kolom) -> Process All asli."""
    pr = pre_live(teks_input or AI_INPUT_REZA.replace("[USER QUERY]\nBrp", "[USER QUERY]\n" + pesan), SAPAAN_REZA)
    _g, rk = galian2(BARIS_REZA, pesan)
    prev = {"resolved_key": "6285199701359", "nama_lengkap": "", "nama_bisnis": "", "industri": "",
            "masalah_utama": "", "volume_chat": "", "budget_range": "", "minat_paket": "", "bahasa": "",
            "deck_requested": "", "brief_terisi": "", "last_bot_reply": SAPAAN_REZA, "last_bot_reply_ts": 0}
    return satu(jalan("Process All", nodes={
        "Chat Counter": [item(original_message=pesan, user_wa="6285199701359", user_name="Reza")],
        "Preprocess - Context Detection": [item(**pr)],
        "Parse Config": [item(config=cfg())],
        "Resolve User Row": [item(**prev)],
        "Rakit Konteks": [item(katalog={"links": LINKS}, galian_kolom=(rk or {}).get("galian_kolom", ""))],
    }, inp=[item(output=ai_output)]))


# ---- X0 sapaan live terbaca dua slot (jalur ambilNamaDanUsaha) ----------------------------------
cek("X0  sapaan live terbaca detektor sebagai nama + nama usaha",
    detek(SAPAAN_REZA) == ["nama_bisnis", "nama_lengkap"], str(detek(SAPAAN_REZA)))

# ---- X1 reproduksi: kode v3.13 menghasilkan PERSIS output live -----------------------------------
_p0 = di_v313(lambda: pre_live(AI_INPUT_REZA, SAPAAN_REZA))
cek("X1  v3.13 mereproduksi: 'Brp' -> askingPrice=false, hargaBukanTanya=false (= live)",
    _p0 and _p0["askingPrice"] is False and _p0["hargaBukanTanya"] is False, str(_p0 and _p0["aiContext"]))
_d0 = di_v313(lambda: replay_reza(MODEL_REZA))
cek("X1b v3.13 mereproduksi: terkirim 'Salam kenal kak.', nama_lengkap 'Brp', ringkas tanya-ulang (= live)",
    _d0 and _d0["cleanOutput"] == "Salam kenal kak." and _d0["nama_lengkap_merged"] == "Brp"
    and _d0["slotTertangkap"] == "nama_lengkap" and _d0["ringkas"] == "tanya-ulang"
    and _d0["slotDitanyaLalu"] == ["nama_bisnis", "nama_lengkap"],
    str(_d0 and (_d0["cleanOutput"], _d0["nama_lengkap_merged"], _d0["slotTertangkap"], _d0["ringkas"])))

# ---- X2 v3.14 Preprocess: konteks harga menyala -------------------------------------------------
_p = pre_live(AI_INPUT_REZA, SAPAAN_REZA)
cek("X2  v3.14: 'Brp' (input live persis) -> askingPrice=true", _p and _p["askingPrice"] is True, str(_p))
cek("X2b ... catatan harga TEGAS masuk ke input model, SYSTEM_DATA & [USER QUERY] utuh",
    _p and '[CONTEXT: Pesannya singkatan dari "berapa harganya?": dia menanyakan harga VIRA - BUKAN menjawab pertanyaanmu dan bukan namanya.' in _p["ai_input_text"]
    and "Sepertinya" not in _p["aiContext"] and "jangan dikutip" in _p["aiContext"]
    and "BALASAN TERAKHIRMU YANG BENAR-BENAR DITERIMA PROSPEK" in _p["ai_input_text"]
    and _p["ai_input_text"].endswith("[USER QUERY]\nBrp") and _p["actualUserMessage"] == "Brp",
    _p and _p["ai_input_text"][-200:])
cek("X2c ... hargaBukanTanya=false (jaring HARGA tidak memotong jawaban harga)", _p and _p["hargaBukanTanya"] is False)
for _pesan in ["harganya berapa ya", "paket premium berapa harganya", "info pricelist dong kak"]:
    _q = pre2(_pesan, SAPAAN_REZA)
    cek("X2d '%s' -> catatan harga lama ('Sepertinya ... Periksa dulu') tidak berubah" % _pesan,
        _q["askingPrice"] is True and _q["aiContext"].startswith("Sepertinya dia menanyakan harga. Periksa dulu pesannya"),
        _q["aiContext"][:60])

# ---- X3 Rakit Konteks (tidak diubah): dia bertanya, tanpa galian -------------------------------
_g, _rk = galian2(BARIS_REZA, "Brp")
cek("X3  Rakit Konteks: 'Brp' = bertanya -> tanpa galian, format_balasan BERTANYA (sama dengan live)",
    _g is None and "format_balasan: dia sedang BERTANYA" in _rk["prospect_context"]
    and _rk.get("galian_kolom", "") == "", str(_g))

# ---- X4 replay keluaran model live lewat v3.14 --------------------------------------------------
_d = replay_reza(MODEL_REZA)
cek("X4  replay output model live: 'Brp' TIDAK disimpan sebagai nama",
    _d and _d["nama_lengkap_merged"] == "" and _d["nama_lengkap_changed"] is False and _d["slotTertangkap"] == "",
    str(_d and (_d["nama_lengkap_merged"], _d["slotTertangkap"])))
cek("X4b ... nama usaha juga tidak terisi 'Brp'", _d and _d["nama_bisnis_merged"] == "", str(_d and _d["nama_bisnis_merged"]))
cek("X4c ... balasan TIDAK buntu: pertanyaannya tidak dibuang (dulu: 'Salam kenal kak.' saja)",
    _d and _d["cleanOutput"] == MODEL_REZA and "?" in _d["cleanOutput"], str(_d and (_d["cleanOutput"], _d["ringkas"])))
cek("X4d ... last_bot_reply = teks yang benar-benar terkirim", _d and _d["last_bot_reply"] == _d["cleanOutput"])

# ---- X5 balasan yang diharapkan (jawab harga) tidak dipotong -----------------------------------
_d = replay_reza(HARGA_REZA)
cek("X5  balasan harga atas 'Brp': kalimat harga utuh (Basic & Premium, Rp, Steven)",
    _d and "Basic mulai Rp3.000.000 per bulan dan Premium Rp5.000.000 per bulan" in _d["cleanOutput"]
    and "dibicarakan langsung sama Steven" in _d["cleanOutput"], str(_d and _d["cleanOutput"]))
cek("X5b ... tanpa nama tersimpan", _d and _d["nama_lengkap_merged"] == "")

# ---- X6 [FACTS nama] dari model --------------------------------------------------------------
for ai, harap, judul in [
        ('Salam kenal kak.\n[FACTS nama="Brp"]', "", "[FACTS nama=\"Brp\"] ditolak"),
        ('Salam kenal kak.\n[FACTS nama="berapa"]', "", "[FACTS nama=\"berapa\"] ditolak"),
        ('Salam kenal kak.\n[FACTS nama="Knp"]', "", "[FACTS nama=\"Knp\"] ditolak"),
        ('Salam kenal kak.\n[FACTS nama="Reza"]', "Reza", "[FACTS nama=\"Reza\"] tetap disimpan"),
        ('Salam kenal kak.\n[FACTS nama="Kak Rina"]', "Kak Rina", "[FACTS nama=\"Kak Rina\"] tetap disimpan (ada kata nama)")]:
    _d = replay_reza(ai)
    cek("X6  %s" % judul, _d and _d["nama_lengkap_merged"] == harap, str(_d and _d["nama_lengkap_merged"]))
_d0 = di_v313(lambda: replay_reza('Salam kenal kak.\n[FACTS nama="Brp"]'))
cek("X6b v3.13 mereproduksi celah [FACTS]: nama 'Brp' tersimpan", _d0 and _d0["nama_lengkap_merged"] == "Brp",
    str(_d0 and _d0["nama_lengkap_merged"]))
_d = replay_reza('Salam kenal kak.\n[FACTS nama="Brp"]')
cek("X6c [FACTS nama] ditolak -> penangkap juga tidak menyimpan 'Brp'",
    _d and _d["nama_lengkap_merged"] == "" and _d["nama_lengkap_changed"] is False and _d["slotTertangkap"] == "")

# ---- X7 kata tanya polos sesudah sapaan dua slot & sapaan nama saja --------------------------------
for pesan in ["Brp", "brp", "Brp?", "brp kak", "berapa?", "Berapa ya kak", "brapa", "brpa kak", "knp",
              "gmn?", "apa?", "kapan", "kpn", "mana"]:
    d = tangkap(pesan, SAPAAN_REZA, ai="Oke kak.")
    cek("X7  '%s' sesudah sapaan nama+usaha -> tidak disimpan sebagai nama / nama usaha" % pesan,
        d and d["nama_lengkap_merged"] == "" and d["nama_bisnis_merged"] == "" and d["slotTertangkap"] == "",
        str(d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"])))
for pesan in ["brp", "knp", "gmn", "berapa kak"]:
    d = tangkap(pesan, PERKENALAN, ai="Oke kak.")
    cek("X7b '%s' sesudah 'boleh tau namanya siapa kak?' -> tidak disimpan" % pesan,
        d and d["nama_lengkap_merged"] == "" and d["slotTertangkap"] == "", str(d and d["nama_lengkap_merged"]))

# ---- X8 regresi: nama asli tetap tertangkap ------------------------------------------------------
for pesan, harap in [("Reza", ("Reza", "")), ("reza kak", ("Reza", "")), ("Reza, brp harganya?", ("Reza", "")),
                     ("Reza\nbrp", ("Reza", "")), ("aku Reza dari Kopi Senja", ("Reza", "Kopi Senja")),
                     ("Reza, Kopi Senja", ("Reza", "Kopi Senja")), ("Apriyanto", ("Apriyanto", "")),
                     ("Dimas, Bengkel Jaya", ("Dimas", "Bengkel Jaya"))]:
    d = tangkap(pesan, SAPAAN_REZA, ai="Oke kak.")
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"])
    cek("X8  '%s' -> %s" % (pesan.replace("\n", " / "), harap), got == harap, str(got))

# ---- X9 Preprocess: pertanyaan harga polos vs bukan ----------------------------------------------
for pesan in ["Brp", "brp", "brp?", "Brp??", "brp kak", "brp kak?", "berapa?", "Berapa ya kak", "brapa kak",
              "brpa", "brp sih", "brp itu kak", "Reza\nbrp"]:
    d = pre2(pesan, SAPAAN_REZA)
    cek("X9  '%s' -> tanya harga" % pesan.replace("\n", " / "), d["askingPrice"] is True, d["aiContext"][:60])
for pesan, lalu in [("brp lama setupnya", SAPAAN_REZA), ("berapa ya, 50an", TANYA_VOLUME),
                    ("brp ya.. 50an kayaknya", TANYA_VOLUME), ("ada berapa admin", SAPAAN_REZA),
                    ("kira kira berapa ya orangnya", SAPAAN_REZA), ("Reza", SAPAAN_REZA), ("berapapun oke", SAPAAN_REZA)]:
    d = pre2(pesan, lalu)
    cek("X9b '%s' -> BUKAN tanya harga" % pesan, d["askingPrice"] is False, d["aiContext"][:60])

# ---- X10 jaring tanya-ulang ------------------------------------------------------------------
d = proses3("Oke kak. Nama usahanya apa ya?", "gmn tuh?", {"last_bot_reply": SAPAAN_REZA}, galian_kolom="")
cek("X10  prospek bertanya + balasan cuma basa-basi & tanya ulang -> pertanyaannya DIBIARKAN (tidak buntu)",
    d and d["cleanOutput"] == "Oke kak. Nama usahanya apa ya?", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3("Bisa kak, VIRA bisa jawab pertanyaan jadwal dan booking otomatis. Nama usahanya apa ya?",
            "bisa buat klinik?", {"last_bot_reply": SAPAAN_REZA}, galian_kolom="")
cek("X10b prospek bertanya + balasan MENJAWAB + tanya ulang -> tanya ulangnya tetap dibuang (desain v3.12)",
    d and d["cleanOutput"] == "Bisa kak, VIRA bisa jawab pertanyaan jadwal dan booking otomatis."
    and "tanya-ulang" in d["ringkas"], str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3("Siap kak, ditunggu ya. Nama usahanya apa ya?", "oke nanti aku kabari", {"last_bot_reply": SAPAAN_REZA},
            galian_kolom="")
cek("X10c balasan bukan basa-basi murni ('ditunggu ya') -> tanya ulang tetap dibuang",
    d and d["cleanOutput"] == "Siap kak, ditunggu ya.", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3("Salam kenal kak. Nama usahanya apa ya?", "Reza", {"last_bot_reply": SAPAAN_REZA}, galian_kolom="")
cek("X10d prospek MENJAWAB (tidak bertanya) -> tanya ulang tetap dibuang walau sisanya basa-basi (desain v3.13)",
    d and d["cleanOutput"] == "Salam kenal kak." and d["ringkas"] == "tanya-ulang", str(d and (d["cleanOutput"], d["ringkas"])))
for pesan in ["knp?", "apa?", "gmn tuh", "brp kak"]:
    d = proses3("Maaf kak. Nama usahanya apa ya?", pesan, {"last_bot_reply": SAPAAN_REZA}, galian_kolom="")
    cek("X10e prospek bertanya '%s' + balasan 'Maaf kak.' + tanya ulang -> tidak buntu" % pesan,
        d and "?" in d["cleanOutput"], str(d and (d["cleanOutput"], d["ringkas"])))

# ---- X11 prompt ------------------------------------------------------------------------------
_spx = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]
cek("X11  prompt BALASAN TERAKHIR: satu kata = jawaban, KECUALI kata tanya",
    "kata itu adalah jawaban pertanyaanku —\nkecuali kata tanya (“brp”, “berapa”, “knp”, “gmn”): itu pertanyaan dia, jawab dulu." in _spx)
cek("X11b prompt [FACTS]: satu kata tak dikenal (bukan kata tanya) = jawaban",
    "Satu kata atau nama yang tidak kukenal (bukan kata tanya seperti “brp”), dikirim tepat setelah" in _spx)


# ===========================================================================
bagian("R. BEDAH REGRESI v3.14 vs v3.13 (= live, dibuktikan output Process All 2026-09-25)")
# ===========================================================================
with open(os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Preprocess - Context Detection", "Process All", "Rakit Konteks"}

cek("R1  node sama dengan v3.13: 91, tanpa node baru/hilang", set(NODES) == set(_NL) and len(wf["nodes"]) == 91,
    str(sorted(set(NODES) ^ set(_NL))))
cek("R2  koneksi identik dengan v3.13", json.dumps(_lama["connections"], sort_keys=True) == json.dumps(CONNS, sort_keys=True))
cek("R2b settings identik (errorWorkflow = GLOBAL notifier)", _lama["settings"] == wf["settings"]
    and wf["settings"].get("errorWorkflow") == "0mp_AdLtInm68RxQUwLqV")
cek("R2c ID & nama workflow tetap", wf.get("id") == _lama.get("id") == "AC65HeFegHFCFc5aY609u" and wf.get("name") == _lama.get("name"))
_beda = sorted(n for n in _NL if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  87 node lain identik byte per byte dengan v3.13", not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))


def _hapus_satu(s, awal, akhir, sisip=""):
    """Hapus dari `awal` (tunggal) sampai SEBELUM `akhir` berikutnya, lalu sisipkan `sisip`."""
    assert s.count(awal) == 1, ("awal", s.count(awal), awal[:60])
    a = s.index(awal)
    b = s.index(akhir, a)
    return s[:a] + sisip + s[b:]


_pre1 = NODES["Preprocess - Context Detection"]["parameters"]["jsCode"]
_pre0 = _NL["Preprocess - Context Detection"]["parameters"]["jsCode"]
_pre_balik = _hapus_satu(_pre1, '// ── "BRP" POLOS (2026-09-25, v3.14) ──', "const askingPrice = ").replace(
    "const askingPrice = TANYA_HARGA_POLOS\n  || (TANYA_HARGA_KITA", "const askingPrice = (TANYA_HARGA_KITA", 1)
_pre_balik = _hapus_satu(_pre_balik, '// v3.14: "brp"/"berapa" polos tidak ambigu',
                         "else if (askingPrice) aiContext += 'Sepertinya", "")
_pre_balik = _pre_balik.replace("else if (askingPrice) aiContext += 'Sepertinya", "if (askingPrice) aiContext += 'Sepertinya", 1)
cek("R5  Preprocess: selain TANYA_HARGA_POLOS & catatan harganya - identik dengan v3.13", _pre_balik == _pre0)

_BARIS_NAMA_V313 = ("    if (/^(aku|saya|kak|kakak|mau|mo|tanya|harga|terima|makasih|thanks|thank|sama|ama|dengan|dgn|ini|"
                    "itu|nama|lagi|lg|siapa|udah|sudah|bisa|oke|ok|iya|ya|bot|admin)$/i.test(kata[0])) return '';\n")
_BARIS_NAMA_V314 = "    if (BUKAN_NAMA_ORANG.test(kata[0])) return '';\n"


def _balik_blok(s):
    s = _hapus_satu(s, "// Kata yang tidak mungkin nama orang. v3.14", "// SEMUA kata ekor di ujung")
    assert s.count(_BARIS_NAMA_V314) == 1
    return s.replace(_BARIS_NAMA_V314, _BARIS_NAMA_V313, 1)


_pa1 = NODES["Process All"]["parameters"]["jsCode"]
_pa0 = _NL["Process All"]["parameters"]["jsCode"]
_rk1 = NODES["Rakit Konteks"]["parameters"]["jsCode"]
_rk0 = _NL["Rakit Konteks"]["parameters"]["jsCode"]
_pa_balik = _balik_blok(_pa1)
_pa_balik = _hapus_satu(_pa_balik, "// ── Nama orang dari model yang bukan nama (2026-09-25, v3.14) ──", "const slotDitanyaLalu = ")
_pa_balik = _hapus_satu(_pa_balik, '  // v3.14 (live 2026-09-25 "Reza"): "Brp" dibalas',
                        "    cleanOutput = sisa.join(' ');\n    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+tanya-ulang'",
                        "  if (sisa.length && sisa.length < kal.length) {\n")
cek("R6  Process All: selain BUKAN_NAMA_ORANG, cek [FACTS nama] & jaring buntu - identik dengan v3.13", _pa_balik == _pa0)
cek("R7  Rakit Konteks: selain BUKAN_NAMA_ORANG - identik dengan v3.13", _balik_blok(_rk1) == _rk0)
_M, _S = "// ── PENANGKAP JAWABAN — MULAI ──", "// ── PENANGKAP JAWABAN — SELESAI ──"
cek("R7b blok PENANGKAP identik di Process All & Rakit Konteks",
    _pa1[_pa1.index(_M):_pa1.index(_S)] == _rk1[_rk1.index(_M):_rk1.index(_S)])
cek("R7c BUKAN_NAMA_ORANG = daftar v3.13 + kata tanya saja (tidak ada kata lama yang hilang)",
    "|".join(["aku", "saya", "kak", "kakak", "mau", "mo", "tanya", "harga", "terima", "makasih", "thanks", "thank",
              "sama", "ama", "dengan", "dgn", "ini", "itu", "nama", "lagi", "lg", "siapa", "udah", "sudah", "bisa",
              "oke", "ok", "iya", "ya", "bot", "admin"]) + "|berapa|brp|brapa|brpa|apa|apakah|gimana|gmn|bagaimana|kenapa|knp|kapan|kpn|mana|dimana)$/i;" in _pa1)

_sp = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]
_sp0 = _NL["AI Agent"]["parameters"]["options"]["systemMessage"]
_sp_balik = _sp.replace(
    "kata itu adalah jawaban pertanyaanku —\nkecuali kata tanya (“brp”, “berapa”, “knp”, “gmn”): itu pertanyaan dia, jawab dulu.\n",
    "kata itu adalah jawaban pertanyaanku.\n", 1).replace(
    "Satu kata atau nama yang tidak kukenal (bukan kata tanya seperti “brp”), dikirim",
    "Satu kata atau nama yang tidak kukenal, dikirim", 1)
cek("R8  prompt: selain dua pengecualian kata tanya - identik dengan v3.13", _sp_balik == _sp0)
cek("R8b angka harga di prompt tidak berubah", _re.findall(r"\d[\d.]*", _sp) == _re.findall(r"\d[\d.]*", _sp0))
cek("R8c tujuh ekspresi {{ }} tetap utuh", len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 7)
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R9  AI Agent: selain systemMessage identik", _pl == _pb)
cek("R10 DeepSeek Personal Chat & Simple Memory tidak disentuh (temperature 0.7)",
    NODES["DeepSeek Personal Chat"] == _NL["DeepSeek Personal Chat"] and NODES["Simple Memory"] == _NL["Simple Memory"]
    and NODES["DeepSeek Personal Chat"]["parameters"]["options"].get("temperature") == 0.7)
cek("R11 cermin prompt .md sama persis dengan systemMessage",
    io.open(os.path.join(DIR, "2026-09-25-system-prompt-VIRA-Personal-v3.14.md"),
            encoding="utf-8").read() == (_sp[1:] if _sp.startswith("=") else _sp))'''

teks = teks[:i] + SEKSI_BARU + teks[j:]

# ---- UAT manual -----------------------------------------------------------------------------------
AWAL_M = '    "DEPLOY — di workflow \'VIRA Personal — Main\' yang live, ganti isinya dengan 2026-09-23-VIRA-Personal-Main-v3.13.json'
AKHIR_M = '    "Hapus workflow \'VIRA Eval — Balasan (sementara)\' sesudah uji selesai.",\n'
assert teks.count(AWAL_M) == 1 and teks.count(AKHIR_M) == 1
i = teks.index(AWAL_M)
j = teks.index(AKHIR_M, i) + len(AKHIR_M)
teks = teks[:i] + '''    "DEPLOY — di workflow 'VIRA Personal — Main' yang live, ganti isinya dengan 2026-09-25-VIRA-Personal-Main-v3.14.json (ID tetap). Tidak ada kolom/node baru.",
    "DATA — STATS baris 6285199701359 (Reza): kosongkan nama_lengkap 'Brp'.",
    "RESET — hapus baris STATS nomor uji dulu.",
    "ULANG KASUS REZA — 'Halo VIRA, aku lihat iklannya di IG, mau ngobrol soal AI customer service.' lalu, sesudah sapaan yang menanyakan nama + nama usaha, kirim 'Brp'. VIRA menjawab kisaran harga (Basic/Premium, angka final ke Steven), TIDAK 'Salam kenal kak'. STATS nama_lengkap tetap KOSONG.",
    "Lalu kirim 'Reza' -> STATS nama_lengkap = Reza.",
    "Regresi: 'harganya berapa kak?' -> kisaran tetap lengkap; jawaban alur 'harga dulu, trs ...' -> tanpa Basic/Premium (kasus Rehan v3.13).",
    "Tab EVENTS: balasan yang dipangkas tetap tercatat sebagai RINGKAS.",
    "Hapus workflow 'VIRA Eval — Balasan (sementara)' sesudah uji selesai.",
''' + teks[j:]

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(teks)
print("OK ->", os.path.basename(DST))
