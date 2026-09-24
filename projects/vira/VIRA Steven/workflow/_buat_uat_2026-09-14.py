# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-14.py - turunkan _uat_2026-09-14.py dari harness _uat_2026-09-07.py.

Harness lama diarahkan ulang ke v3.8 (232 assertion lamanya ikut jalan sebagai regresi),
lalu seksi baru disisipkan sebelum ringkasan:

  N. PROCESS ALL   - detektor pertanyaan galian, penangkap jawaban, isi dari blok deck, bahasa
  O. RAKIT KONTEKS - galian_berikutnya: urutan, jendela giliran, jeda, budget/paket tidak pernah
  P. NOTIF         - nama asli sampai ke Steven
  Q. PROMPT v3.8   - statis, plus contoh kalimat di prompt terbaca benar oleh detektor kode
  R. BEDAH REGRESI - 82 node lain identik byte per byte dengan v3.6; node yang diubah hanya
                     berubah di tempat yang disebut patch

Jalankan: python _buat_uat_2026-09-14.py   (lalu: python _uat_2026-09-14.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-07.py")
DST = os.path.join(DIR, "_uat_2026-09-14.py")

with io.open(SRC, encoding="utf-8") as f:
    teks = f.read()


def ganti(lama, baru):
    global teks
    assert teks.count(lama) == 1, "anchor tidak tunggal: %r" % lama[:80]
    teks = teks.replace(lama, baru, 1)


# --- 1. arahkan ke v3.8 --------------------------------------------------
ganti('WF = os.path.join(DIR, "2026-09-07-VIRA-Personal-Main-v3.6.json")',
      'WF = os.path.join(DIR, "2026-09-14-VIRA-Personal-Main-v3.8.json")')
ganti("_uat_2026-09-07.py — UAT perilaku untuk 2026-09-07-VIRA-Personal-Main-v3.6.json.\n\n"
      "Diturunkan dari _uat_2026-09-06b.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-07.py, lalu jalankan ulang). Seluruh assertion lama ikut jalan\n"
      "sebagai regresi; seksi L dan M baru untuk insiden harga 2026-09-07.",
      "_uat_2026-09-14.py — UAT perilaku untuk 2026-09-14-VIRA-Personal-Main-v3.8.json.\n\n"
      "Diturunkan dari _uat_2026-09-07.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-14.py, lalu jalankan ulang). Seluruh assertion lama ikut jalan\n"
      "sebagai regresi; seksi N-R baru untuk pengisian kolom STATS 2026-09-14.")
ganti("Jalankan: python _uat_2026-09-07.py", "Jalankan: python _uat_2026-09-14.py")

# --- 2. seksi baru -------------------------------------------------------
BARU = r'''
# ===========================================================================
bagian("N. PROCESS ALL — detektor galian & penangkap jawaban (2026-09-14)")
# ===========================================================================
PERKENALAN = ("Halo kak, aku Steven versi AI. Aku dibangun sama Steven pakai sistem yang sama yang dia "
              "bikin untuk kliennya, namanya VIRA. Jadi kalau kakak penasaran hasilnya kayak apa, kakak "
              "lagi ngobrol sama contohnya sekarang. Btw boleh tau namanya siapa kak?")
TAWARAN_LIVE = ("mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? "
                "kalau boleh tau nama usahanya apa ya kak?.")


def detek(kalimat):
    d = satu(proses("Oke kak.", pesan_user="hmm", prev_row={"last_bot_reply": kalimat}))
    return sorted(d["slotDitanyaLalu"]) if d else None


r = proses("Oke kak.", prev_row={"last_bot_reply": PERKENALAN})
cek("N0  node tidak error", r["err"] is None, str(r["err"]))

for kal, harap in [
        (PERKENALAN, ["nama_lengkap"]),
        ("Aku panggilnya siapa nih kak?", ["nama_lengkap"]),
        ("Boleh kenalan dulu kak?", ["nama_lengkap"]),
        ("Ini dengan kak siapa ya?", ["nama_lengkap"]),
        (TAWARAN_LIVE, ["nama_bisnis"]),
        ("Biar Steven tulis di decknya, usahanya namanya apa kak?", ["nama_bisnis"]),
        ("Nama brandnya apa kak?", ["nama_bisnis"]),
        ("Usahanya di bidang apa kak?", ["industri"]),
        ("Bisnisnya apa kak?", ["industri"]),
        ("Kakak jualan apa?", ["industri"]),
        ("Soal chat, yang paling bikin repot sekarang apa kak?", ["masalah_utama"]),
        ("Kendalanya apa sekarang kak?", ["masalah_utama"]),
        ("Kira-kira sehari ada berapa chat masuk kak?", ["volume_chat"]),
        ("Chatnya berapa per hari kak?", ["volume_chat"]),
        ("Kalau sekarang siapa yang balas chatnya kak?", []),
        ("Ada kendala lain kak?", []),
        ("Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak?", []),
        ("VIRA bisa dipakai buat bisnis apa aja kak.", []),
        ("Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan.", []),
        ("Biaya satu kelas kira-kira berapa kak?", []),
        ("Steven sendiri yang akan menghubungi kakak langsung.", []),
        ("mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?", []),
        ("Usahanya di bidang apa kak? Sehari ada berapa chat masuk?", ["industri", "volume_chat"])]:
    got = detek(kal)
    cek("N1  detektor '%s' -> %s" % (kal[:55], harap), got == harap, str(got))


def tangkap(pesan, lalu, ai="Oke kak.", prev=None):
    pr = {"last_bot_reply": lalu}
    pr.update(prev or {})
    return satu(proses(ai, pesan_user=pesan, prev_row=pr))


for pesan, harap in [("Budi", "Budi"), ("aku Callista", "Callista"), ("panggil aja Rina kak", "Rina"),
                     ("nama saya Dewi", "Dewi"), ("saya Andi, owner Andi Bakery", "Andi"),
                     ("halo kak, budi santoso", "Budi Santoso"), ("Budi 😊", "Budi"),
                     ("Budi\nmau tanya harga vira", "Budi"), ("ehm, Budi kak", "Budi")]:
    d = tangkap(pesan, PERKENALAN)
    cek("N2  nama dari '%s' -> %s" % (pesan.replace("\n", " / "), harap),
        d and d["nama_lengkap_merged"] == harap and d["nama_lengkap_changed"] is True
        and d["slotTertangkap"] == "nama_lengkap", str(d and d.get("nama_lengkap_merged")))

for pesan in ["oke", "kenapa emang?", "rahasia hehe", "nanti aja", "mau tanya harga dulu",
              "berapa harganya?", "saya mau tanya soal VIRA dong", "hmm", "ehm", "wah", "hmm kak"]:
    d = tangkap(pesan, PERKENALAN)
    cek("N3  '%s' BUKAN nama -> tidak disimpan" % pesan,
        d and d["nama_lengkap_merged"] == "" and d["slotTertangkap"] == "", str(d and d.get("nama_lengkap_merged")))

d = tangkap("budi", PERKENALAN, ai='Salam kenal kak Budi.\n[FACTS nama="Budi Santoso"]')
cek("N4  [FACTS] dari model menang atas penangkap", d and d["nama_lengkap_merged"] == "Budi Santoso"
    and d["slotTertangkap"] == "")
d = tangkap("Andi", PERKENALAN, prev={"nama_lengkap": "Budi"})
cek("N5  nilai lama tidak pernah ditimpa", d and d["nama_lengkap_merged"] == "Budi" and d["slotTertangkap"] == "")
d = tangkap("Budi", "Halo kak, aku Steven versi AI.")
cek("N6  balasan lalu tidak bertanya -> tidak ada yang ditangkap", d and d["slotTertangkap"] == "")

for pesan, harap in [("boleh kak, namanya Teamsultan", "Teamsultan"), ("Teamsultan", "Teamsultan"),
                     ("usahaku namanya Kopi Senja kak", "Kopi Senja"), ("belum ada nama kak", "")]:
    d = tangkap(pesan, TAWARAN_LIVE)
    cek("N7  nama usaha dari '%s' -> %r" % (pesan, harap), d and d["nama_bisnis_merged"] == harap,
        str(d and d.get("nama_bisnis_merged")))

for pesan, harap in [("konsultan sipil", "konsultan sipil"), ("aku jualan skincare kak", "jualan skincare"),
                     ("bergerak di bidang pendidikan", "pendidikan"), ("gimana ya", "")]:
    d = tangkap(pesan, "Usahanya di bidang apa kak?")
    cek("N8  bidang usaha dari '%s' -> %r" % (pesan, harap), d and d["industri_merged"] == harap,
        str(d and d.get("industri_merged")))

for pesan, harap in [("tenggelam balesin chat satu satu pas promo", "tenggelam balesin chat satu satu pas promo"),
                     ("aman aja", ""), ("nggak ada sih", "")]:
    d = tangkap(pesan, "Soal chat, yang paling bikin repot sekarang apa kak?")
    cek("N9  masalah dari '%s' -> %r" % (pesan, harap), d and d["masalah_utama_merged"] == harap,
        str(d and d.get("masalah_utama_merged")))

for pesan, harap in [("20an kak", "20an"), ("puluhan lah", "puluhan lah"), ("boleh", ""), ("belum tau", "")]:
    d = tangkap(pesan, "Kira-kira sehari ada berapa chat masuk kak?")
    cek("N10 jumlah chat dari '%s' -> %r" % (pesan, harap), d and d["volume_chat_merged"] == harap,
        str(d and d.get("volume_chat_merged")))

d = tangkap("konsultan sipil", "Usahanya di bidang apa kak? Sehari ada berapa chat masuk?")
cek("N11 dua pertanyaan sekaligus -> tidak ditebak", d and d["slotTertangkap"] == ""
    and d["industri_merged"] == "" and d["volume_chat_merged"] == "")

d = tangkap("boleh kak, namanya Teamsultan", TAWARAN_LIVE, ai="Siap kak, sudah aku teruskan ke Steven.",
            prev={"industri": "konsultan sipil", "masalah_utama": "tenggelam balas chat"})
cek("N12 nama usaha yang ditangkap ikut masuk brief deck (tanpa blok dari model)",
    d and d["deckDiminta"] is True and d["isDeckRequest"] is True
    and d["deckRequest"]["nama_bisnis"] == "Teamsultan" and d["deckRejected"] is False,
    str(d and (d.get("deckRequest", {}).get("nama_bisnis"), d.get("deckMissing"))))

BLOK = ("Oke kak.\n[DECK_REQUEST]\nnama: Budi\nindustri: konsultan sipil\n"
        "masalah_utama: tenggelam balas chat\nvolume_chat_harian: 20an\nbudget_range: belum disebut\n"
        "[/DECK_REQUEST]")
d = satu(proses(BLOK, pesan_user="boleh"))
cek("N13 isi blok [DECK_REQUEST] mengisi kolom STATS yang kosong",
    d and d["nama_lengkap_merged"] == "Budi" and d["industri_merged"] == "konsultan sipil"
    and d["masalah_utama_merged"] == "tenggelam balas chat" and d["volume_chat_merged"] == "20an"
    and d["industri_changed"] is True and d["volume_chat_changed"] is True,
    str(d and (d.get("industri_merged"), d.get("volume_chat_merged"))))
cek("N13b 'belum disebut' di blok tidak mengisi apa pun", d and d["budget_range_merged"] == "")
d = satu(proses(BLOK, pesan_user="boleh", prev_row={"industri": "edukasi"}))
cek("N14 blok deck tidak menimpa kolom STATS yang sudah terisi", d and d["industri_merged"] == "edukasi")

for pesan, prev_b, harap in [("halo mau tanya harganya berapa ya kak", "", "ID"),
                             ("hi, how much is the price for your service?", "", "EN"),
                             ("mau tanya dong, how does it work for my business?", "", "campur"),
                             ("Budi", "EN", "EN"),
                             ("ok", "", "")]:
    d = satu(proses("Oke kak.", pesan_user=pesan, prev_row={"bahasa": prev_b}))
    cek("N15 bahasa '%s' -> %r" % (pesan, harap), d and d["bahasa_merged"] == harap,
        str(d and d.get("bahasa_merged")))
d = satu(proses("Oke.\n[DECK_REQUEST]\nbahasa_deck: EN\nindustri: sipil\n[/DECK_REQUEST]",
                pesan_user="halo mau tanya harganya berapa ya kak"))
cek("N15b bahasa_deck dari blok tetap diutamakan", d and d["bahasa_merged"] == "EN")

d = satu(proses(DECK_BLOK + BALASAN_ASLI, pesan_user="boleh",
                prev_row={"last_bot_reply": "Kalau nanti mau lihat gambaran lengkapnya, ada landing page-nya, "
                                            "atau bisa juga aku mintakan Steven buatkan deck khusus buat bisnis "
                                            "kakak, gratis. Mau?"}))
cek("N16 regresi insiden 2026-09-05: 'boleh' tidak ditangkap sebagai isian apa pun",
    d and d["slotTertangkap"] == "" and d["deckDiminta"] is True)


# ===========================================================================
bagian("O. RAKIT KONTEKS — galian_berikutnya (2026-09-14)")
# ===========================================================================
def galian(**baris):
    d = rakit(baris)
    m = _re.search(r"^galian_berikutnya: (.*)$", d["prospect_context"], _re.M) if d else None
    return (m.group(1) if m else None), d


for baris, harap, judul in [
        ({"greeting_sent": ""}, "namanya", "pesan perkenalan -> tanya nama"),
        ({"greeting_sent": "", "nama_lengkap": "Budi"}, None, "perkenalan, nama sudah ada -> tidak menggali apa pun"),
        ({"greeting_sent": "Y", "Counter": "1"}, "bidang usahanya", "giliran 2 -> bidang usaha"),
        ({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": "Usahanya di bidang apa kak?"}, None,
         "bidang usaha baru ditanyakan & belum dijawab -> jeda satu balasan"),
        ({"greeting_sent": "Y", "Counter": "3"}, "bidang usahanya", "giliran 4 -> bidang usaha lagi (kesempatan kedua)"),
        ({"greeting_sent": "Y", "Counter": "4"}, "masalah terbesarnya", "giliran 5 -> jendela bidang usaha habis, lanjut masalah"),
        ({"greeting_sent": "Y", "Counter": "2", "industri": "sipil"}, "masalah terbesarnya", "bidang usaha ada -> masalah"),
        ({"greeting_sent": "Y", "Counter": "4", "industri": "sipil",
          "last_bot_reply": "Soal chat, yang paling bikin repot sekarang apa kak?"}, None, "masalah baru ditanyakan -> jeda"),
        ({"greeting_sent": "Y", "Counter": "6", "industri": "sipil"}, None, "giliran 7 -> jendela masalah habis"),
        ({"greeting_sent": "Y", "Counter": "3", "industri": "sipil", "masalah_utama": "x"}, "kira-kira berapa chat",
         "masalah ada -> jumlah chat"),
        ({"greeting_sent": "Y", "Counter": "8", "industri": "sipil", "masalah_utama": "x"}, None,
         "giliran 9 -> jendela jumlah chat habis"),
        ({"greeting_sent": "Y", "Counter": "3", "industri": "sipil", "masalah_utama": "x", "volume_chat": "20"}, None,
         "semua terisi -> tidak menggali"),
        ({"greeting_sent": "Y", "Counter": "1", "nama_lengkap": ""}, "bidang usahanya",
         "nama tidak ditanya lagi di luar perkenalan"),
        ({"greeting_sent": "Y", "Counter": ""}, None, "Counter kosong (kontak import) + sudah disapa -> tidak menggali")]:
    g, d = galian(**baris)
    ok = (g is None) if harap is None else (g is not None and g.startswith(harap))
    cek("O1  %s" % judul, ok, str(g))

_bocor = []
for c in range(0, 13):
    for isi in ({}, {"industri": "a"}, {"industri": "a", "masalah_utama": "b"},
                {"industri": "a", "masalah_utama": "b", "volume_chat": "c"}):
        for gs in ("", "Y"):
            g, _ = galian(greeting_sent=gs, Counter=str(c), **isi)
            if g and _re.search(r"budget|anggaran|paket|basic|premium|harga", g, _re.I):
                _bocor.append((c, isi, g))
cek("O2  budget & minat paket TIDAK PERNAH digali (408 kombinasi)", not _bocor, str(_bocor[:3]))

g, d = galian(greeting_sent="", Nama="Snowville Sentul")
cek("O3  nama akun WA tidak menggugurkan pertanyaan nama", g is not None and g.startswith("namanya"))
cek("O4  IS_NEW_USER tetap baris terakhir", d["prospect_context"].rstrip().endswith("IS_NEW_USER: true"))
g, d = galian(greeting_sent="Y", Counter="abc")
cek("O5  Counter rusak tidak menjatuhkan node", d is not None)


# ===========================================================================
bagian("P. NOTIF — nama asli sampai ke Steven (2026-09-14)")
# ===========================================================================
def ekspr_node(ekspr, nodes):
    isi = ekspr[1:] if ekspr.startswith("=") else ekspr
    isi = isi.strip()
    assert isi.startswith("{{") and isi.endswith("}}"), isi[:40]
    return CTX.call("__run", "return (" + isi[2:-2].strip() + ");",
                    {"nodes": nodes, "input": [], "staticData": {}, "vars": {}, "pakaiVars": True})


d = merge({"deckRequest": dict(BRIEF1, nama="Budi")})
cek("P1  notif brief deck: baris WA memuat nama asli",
    d and "WA: 6289900112233 · Budi" in d["notif_text"], str(d and d["notif_text"][:200]))
d = merge({"deckRequest": BRIEF1})
cek("P1b tanpa nama -> 'nama belum disebut'", d and "WA: 6289900112233 · nama belum disebut" in d["notif_text"])
cek("P1c perintah generate deck tetap memakai nomor", d and "--wa 6289900112233" in d["notif_text"])


def media_notif(nama_asli, nama_wa):
    return satu(jalan("Format Media Notif", nodes={
        "Process All": [item(nama_lengkap_merged=nama_asli, mediaKey="brosur",
                             mediaRequestSummary="minta brosur", mediaUrl="")],
        "Chat Counter": [item(user_name=nama_wa, user_wa="6289900112233")],
        "Resolve User Row": [item(resolved_key="6289900112233")],
        "Parse Config": [item(config=cfg())],
    }, inp=[item()]))


d = media_notif("Budi", "Snowville Sentul")
cek("P2  notif media: nama asli + akun WA", d and "Nama: Budi (akun WA: Snowville Sentul)" in d["message"],
    str(d and d.get("message")))
d = media_notif("", "Snowville Sentul")
cek("P2b tanpa nama asli: akun WA ditandai", d and "Nama: Snowville Sentul (nama akun WA)" in d["message"])
d = media_notif("Budi", "Budi")
cek("P2c nama asli = akun WA -> tidak diulang", d and "Nama: Budi\n" in d["message"])
d = media_notif("", "")
cek("P2d dua-duanya kosong -> '(belum ada nama)'", d and "(belum ada nama)" in d["message"])

_un = [p for p in NODES["Notify Admin Unknown"]["parameters"]["bodyParameters"]["parameters"]
       if p.get("name") == "message"][0]["value"]
_cc = [item(user_wa="6289900112233", user_name="Snowville Sentul", original_message="bisa integrasi SAP?")]
r = ekspr_node(_un, {"Process All": [item(nama_lengkap_merged="Budi")], "Chat Counter": _cc})
cek("P3  notif UNKNOWN: nama asli + akun WA", r["err"] is None and "Budi (akun WA: Snowville Sentul)" in r["out"]
    and "Pertanyaan: bisa integrasi SAP?" in r["out"], str(r))
r = ekspr_node(_un, {"Process All": [item(nama_lengkap_merged="")], "Chat Counter": _cc})
cek("P3b notif UNKNOWN tanpa nama asli", r["err"] is None and "Snowville Sentul (nama akun WA)" in r["out"], str(r))

_ev = NODES["Log EVENTS Delegated"]["parameters"]["columns"]["value"]["nama"]
r = ekspr_node(_ev, {"Process All": [item(nama_lengkap_merged="Budi")], "Chat Counter": _cc})
cek("P4  EVENTS handover mencatat nama asli", r["err"] is None and r["out"] == "Budi", str(r))
r = ekspr_node(_ev, {"Process All": [item(nama_lengkap_merged="")], "Chat Counter": _cc})
cek("P4b EVENTS tanpa nama asli -> akun WA", r["out"] == "Snowville Sentul", str(r))


# ===========================================================================
bagian("Q. PROMPT v3.8 — nama, galian, [FACTS]")
# ===========================================================================
_sp = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]
cek("Q1  prefix '=' dipertahankan", _sp.startswith("="))
cek("Q2  enam ekspresi {{ }} tetap utuh", len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 6)
cek("Q3  bagian # NAMA LAWAN BICARA tepat satu, sebelum # GAYA",
    _sp.count("# NAMA LAWAN BICARA\n") == 1 and _sp.index("# NAMA LAWAN BICARA") < _sp.index("\n# GAYA\n"))
cek("Q4  nama ditanya SEKALI di perkenalan, tidak diulang", "Namanya kutanyakan SEKALI, di pesan perkenalan" in _sp
    and "jangan ditanyakan lagi" in _sp)
cek("Q5  PERKENALAN tetap intro biasa + tanya nama", "tutup dengan menanyakan namanya" in _sp
    and "perkenalan seperti di atas, jawaban singkat kalau dia bertanya, lalu pertanyaan nama" in _sp)
cek("Q6  ALUR 7 mengikuti galian_berikutnya", "itu SATU-SATUNYA pertanyaan galian di balasan ini" in _sp)
cek("Q7  empat galian hanya lewat baris itu",
    "Nama, bidang usaha, masalah utama, dan jumlah chat per hari hanya kutanyakan lewat baris itu" in _sp)
cek("Q8  nama_wa BUKAN nama asli", "Itu BUKAN nama yang dia sebutkan" in _sp)
cek("Q9  [FACTS] wajib saat menjawab galian", "Setiap kali dia menjawab pertanyaan galianku, tulis `[FACTS]`" in _sp)
cek("Q10 budget tetap Tingkat 3 (tidak pernah ditanya)", "leadsnya datang, anggarannya" in _sp)
cek("Q11 prompt tidak menyuruh menanyakan minat paket",
    not _re.search(r"(tanya|tanyakan)[^.\n]{0,40}(basic atau premium|minat paket|paket mana)", _sp, _re.I))
cek("Q12 prompt merujuk baris galian_berikutnya yang benar-benar dibuat Rakit Konteks",
    "`galian_berikutnya`" in _sp and "galian_berikutnya: " in NODES["Rakit Konteks"]["parameters"]["jsCode"])

_par = _sp.split("Baris `galian_berikutnya`")[1].split("\n\n")[0]
_cth = [k.replace("\n", " ") for k in _re.findall(r'"([^"]+)"', _par)]
_harap = [["industri"], ["masalah_utama"], ["volume_chat"]]
cek("Q13 tiga contoh kalimat galian ditemukan", len(_cth) == 3, str(_cth))
for _k, _h in zip(_cth, _harap):
    cek("Q14 contoh prompt '%s' terbaca detektor sebagai %s" % (_k, _h), detek(_k) == _h, str(detek(_k)))
_bag = _sp.split("# NAMA LAWAN BICARA")[1].split("\n# GAYA")[0]
for _k in [k for k in _re.findall(r'"([^"]*siapa[^"]*)"', _bag) if len(k.split()) >= 3]:
    cek("Q15 contoh tanya nama '%s' terbaca sebagai nama_lengkap" % _k, detek(_k) == ["nama_lengkap"])
_m = _re.search(r'"(mau aku mintakan Steven[^"]*nama usahanya[^"]*)"', _sp)
cek("Q16 kalimat tawaran deck (suntingan live) terbaca sebagai nama_bisnis",
    _m is not None and detek(_m.group(1)) == ["nama_bisnis"])
for _k in ["biasanya mereka paling sering nanya apa kak?",
           "dari chat sampai akhirnya beli, biasanya lewat langkah apa aja kak?",
           "biaya satu kelas kira-kira berapa kak?"]:
    # prompt membungkus contoh ke baris baru; bandingkan dengan spasi
    cek("Q17 contoh Tingkat 2/2B '%s' tidak dikira galian STATS" % _k[:40],
        _k in _sp.replace("\n", " ") and detek(_k) == [])


# ===========================================================================
bagian("R. BEDAH REGRESI — yang tidak disebut patch tidak tersentuh")
# ===========================================================================
import difflib as _dl
with open(os.path.join(DIR, "2026-09-07-VIRA-Personal-Main-v3.6.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Process All", "Rakit Konteks", "Merge Brief",
          "Notify Admin Unknown", "Format Media Notif", "Log EVENTS Delegated"}

cek("R1  jumlah & nama node sama dengan v3.6", set(_NL) == set(NODES) and len(wf["nodes"]) == 89)
cek("R2  koneksi identik dengan v3.6",
    json.dumps(_lama["connections"], sort_keys=True) == json.dumps(CONNS, sort_keys=True))
_beda = sorted(n for n in NODES if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  82 node lain identik byte per byte (termasuk Update to STATS & Cek_user_status)",
    not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))
cek("R4b settings workflow tetap", _lama.get("settings") == wf.get("settings"))
cek("R4c tidak ada sisa kolom v3.7 (nama_ditanya)", "nama_ditanya" not in json.dumps(wf, ensure_ascii=False))


def _hunk(a, b):
    la, lb = a.split("\n"), b.split("\n")
    return [(t, la[i1:i2], lb[j1:j2]) for t, i1, i2, j1, j2
            in _dl.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes() if t != "equal"]


_h = _hunk(_NL["Process All"]["parameters"]["jsCode"], NODES["Process All"]["parameters"]["jsCode"])
_ganti = [x for t, o, _ in _h if t != "insert" for x in o]
cek("R5  Process All: selain sisipan, hanya baris bahasa yang diganti",
    _ganti == ["                     || BERSIH(prev.bahasa, 20);"], str(_ganti))
_h = _hunk(_NL["Rakit Konteks"]["parameters"]["jsCode"], NODES["Rakit Konteks"]["parameters"]["jsCode"])
cek("R6  Rakit Konteks: hanya SISIPAN", _h and all(t == "insert" for t, _, _ in _h), str([(t, o) for t, o, _ in _h]))
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
cek("R7  detektor galian IDENTIK di Process All dan Rakit Konteks",
    _det(NODES["Process All"]["parameters"]["jsCode"]) == _det(NODES["Rakit Konteks"]["parameters"]["jsCode"]))
_h = _hunk(_NL["Merge Brief"]["parameters"]["jsCode"], NODES["Merge Brief"]["parameters"]["jsCode"])
cek("R8  Merge Brief: tepat satu baris (baris WA)",
    len(_h) == 1 and len(_h[0][1]) == 1 and "WA: ${key}" in _h[0][1][0], str(_h))
_h = _hunk(_NL["Format Media Notif"]["parameters"]["jsCode"], NODES["Format Media Notif"]["parameters"]["jsCode"])
cek("R9  Format Media Notif: hanya baris `const nama`",
    len(_h) == 1 and _h[0][1] == ["const nama = cc.user_name || '';"], str(_h))

_pl = json.loads(json.dumps(_NL["Log EVENTS Delegated"]["parameters"]))
_pb = json.loads(json.dumps(NODES["Log EVENTS Delegated"]["parameters"]))
_pl["columns"]["value"].pop("nama"); _pb["columns"]["value"].pop("nama")
cek("R10 Log EVENTS Delegated: selain kolom nama identik", _pl == _pb)
_pl = json.loads(json.dumps(_NL["Notify Admin Unknown"]["parameters"]))
_pb = json.loads(json.dumps(NODES["Notify Admin Unknown"]["parameters"]))
for _p in (_pl, _pb):
    for _x in _p["bodyParameters"]["parameters"]:
        if _x.get("name") == "message":
            _x["value"] = ""
cek("R11 Notify Admin Unknown: selain isi pesan identik", _pl == _pb)

_h = _hunk(_NL["AI Agent"]["parameters"]["options"]["systemMessage"], _sp)
_dihapus = [x for _, o, _ in _h for x in o]
_boleh = {
    "7. Kalau ada peluang wajar, gali satu hal tentang bisnisnya (lihat MENGGALI). Satu saja, jangan menginterogasi.",
    "Lalu langsung jawab pertanyaannya. Kalau dia belum bertanya apa-apa, tanya balik apa yang bikin dia tertarik.",
    "Nama usahanya tidak — itu satu-satunya yang harus kutanyakan sengaja, dan tanpa itu cover",
    "  Satu kata atau nama yang tidak kukenal, dikirim tepat setelah aku menanyakan nama bisnis atau",
    "  bidang usahanya, adalah JAWABAN atas pertanyaan itu — bukan pertanyaan baru. Catat lewat tag ini,",
    "  jangan tanya balik apa maksudnya.",
}
cek("R12 system prompt: baris lama yang diganti hanya 6 baris sasaran patch",
    set(_dihapus) <= _boleh, str([x for x in _dihapus if x not in _boleh]))
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R13 AI Agent: selain systemMessage identik", _pl == _pb)


'''

ANCHOR = ('# ===========================================================================\n'
          'print()\n'
          'print("=" * 72)\n'
          'print("RINGKASAN UAT")')
ganti(ANCHOR, BARU.lstrip("\n") + ANCHOR)

# --- 3. checklist UAT manual ---------------------------------------------
ganti('    "Import 2026-09-07-VIRA-Personal-Main-v3.6.json, aktifkan, matikan versi lama.",\n',
      '    "Import 2026-09-14-VIRA-Personal-Main-v3.8.json, matikan v3.6 dulu, lalu aktifkan v3.8. Tidak ada kolom baru.",\n')
ganti('    "DECK — generate deck dari brief itu, pastikan slide Pain Points memuat 3+ poin.",\n',
      '    "DECK — generate deck dari brief itu, pastikan slide Pain Points memuat 3+ poin.",\n'
      '    "NAMA — nomor baru kirim \'halo\': perkenalan seperti biasa + \'namanya siapa kak?\'.",\n'
      '    "NAMA — jawab \'Budi\': VIRA memanggil \'kak Budi\'; STATS.nama_lengkap = Budi.",\n'
      '    "GALIAN — lanjut chat biasa: berikutnya VIRA menanyakan bidang usaha, lalu masalah, lalu jumlah chat per hari "\n'
      '    "(satu per balasan). Setiap jawaban muncul di STATS: industri, masalah_utama, volume_chat, bahasa.",\n'
      '    "GALIAN — abaikan satu pertanyaan: balasan berikutnya TIDAK mengulangnya.",\n'
      '    "DECK — terima tawaran deck + sebut nama usaha: STATS.nama_bisnis terisi, REQUESTS mendapat baris, "\n'
      '    "notif brief ke Steven berbaris \'WA: 62xxx · Budi\'.",\n'
      '    "BUDGET/PAKET — sepanjang uji, VIRA tidak pernah menanyakan anggaran atau Basic/Premium.",\n')

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(teks)

print("DST : %s  (%d baris)" % (os.path.basename(DST), teks.count("\n") + 1))
