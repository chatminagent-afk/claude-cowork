# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-23b.py - turunkan _uat_2026-09-23b.py dari harness _uat_2026-09-23.py (v3.12).

Harness v3.12 diarahkan ulang ke v3.13. Seksi A-Q, S, T, U dan V ikut jalan sebagai regresi.
Yang disesuaikan HANYA cek yang mengunci perilaku yang memang diganti patch ini:
  V5 "menyebut harga"  prospek "oke noted" dibalas daftar harga = persis cacat 13:42 yang kini
                       dipangkas jaring HARGA. Tujuan cek aslinya (jawaban harga TIDAK dipotong)
                       diuji dengan prospek yang memang meminta harganya ("info pricelist dong kak").
Seksi baru:
  W. HARGA, PENANGKAP, HANDOVER & NOTIF - ulang uji live Steven 2026-09-23 13:22-14:06 ("Rehan",
     sewa raket padel): W1-W4 harga & penangkap, W5 handover langsung, W6 notif sesudah deck.
Seksi R ditulis ulang: membedah v3.13 terhadap v3.12 (= live, dicek via MCP 2026-09-23 12:19 WIB).

Jalankan: python _buat_uat_2026-09-23b.py   (lalu: python _uat_2026-09-23b.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-23.py")
DST = os.path.join(DIR, "_uat_2026-09-23b.py")

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


# --- 1. arahkan ke v3.13 -------------------------------------------------
ganti('WF = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.12.json")',
      'WF = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json")')
ganti("_uat_2026-09-23.py — UAT perilaku untuk 2026-09-23-VIRA-Personal-Main-v3.12.json.\n\n"
      "Diturunkan dari _uat_2026-09-22.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-23.py, lalu jalankan ulang). Seksi A-Q, S, T dan U ikut jalan sebagai\n"
      "regresi (hanya cek yang mengunci teks lama yang diganti yang disesuaikan); seksi V baru\n"
      "untuk uji Steven 2026-09-23; seksi R membedah v3.12 terhadap v3.11.",
      "_uat_2026-09-23b.py — UAT perilaku untuk 2026-09-23-VIRA-Personal-Main-v3.13.json.\n\n"
      "Diturunkan dari _uat_2026-09-23.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-23b.py, lalu jalankan ulang). Seksi A-Q, S, T, U dan V ikut jalan sebagai\n"
      "regresi (hanya V5 'menyebut harga' yang disesuaikan); seksi W baru untuk uji live Steven\n"
      "2026-09-23 13:22-13:45 (Rehan); seksi R membedah v3.13 terhadap v3.12.")
ganti("Jalankan: python _uat_2026-09-23.py", "Jalankan: python _uat_2026-09-23b.py")
ganti('print("UAT PERILAKU — VIRA Personal v3.12 (2026-09-23)")',
      'print("UAT PERILAKU — VIRA Personal v3.13 (2026-09-23)")')

# --- 2. cek lama yang mengunci perilaku yang memang diganti --------------
ganti('''        ("menyebut harga", "Basic mulai Rp3.000.000 per bulan, sudah termasuk setup. Angka finalnya Steven yang "
         "tentukan setelah lihat kebutuhan kakak. Chat masuk sehari kira-kira ada berapa kak?", "oke noted", {}, False),''',
      '''        # v3.13: "oke noted" dibalas daftar harga kini dipangkas jaring HARGA (seksi W2c). Yang dijaga cek ini
        # tetap sama: jawaban harga TIDAK dipotong kalau prospek memang meminta harganya.
        ("menyebut harga (prospek minta pricelist)", "Basic mulai Rp3.000.000 per bulan, sudah termasuk setup. "
         "Angka finalnya Steven yang tentukan setelah lihat kebutuhan kakak. Chat masuk sehari kira-kira ada berapa kak?",
         "info pricelist dong kak", {}, False),''')

# --- 3. seksi W (baru), disisipkan sebelum seksi R ------------------------
SEKSI_W = r'''bagian("W. HARGA & PENANGKAP — ulang uji live Steven 2026-09-23 13:22-13:45 (Rehan, sewa raket padel)")
# ===========================================================================
# Transkrip live (MSG_BUFFER / EVENTS / STATS, dibaca 2026-09-23):
#   rehan / usahaku sewa raket padel            -> STATS nama_bisnis "sewa raket padel" (salah)
#   persewaan aja sih                           -> STATS industri "persewaan aja" (ekor tersisa)
#   harga dulu, trs klo udah aman baru ke payment (jawaban pertanyaan langkah 13:40)
#       -> 13:42 EVENTS RINGKAS: model menyebut Basic/Premium + mengutip catatan konteks harga
#   okee -> 13:44 VIRA menanyakan lagi pertanyaan langkah yang sudah dijawab
Q_REHAN = "Dari chat sampai akhirnya jadi sewa, biasanya lewat langkah apa aja kak?"
# Balasan 13:40: yang diketahui hanya kalimat tanyanya (= last_bot_reply 13:44); pengakuan di depannya rekonstruksi.
LALU_1340 = "Noted kak. " + Q_REHAN
ALUR_REHAN = "harga dulu, trs klo udah aman baru ke payment"
ASLI_1342 = ("Oh itu alur bisnis kakak yang dia ceritakan kak, bukan nanya harga VIRA. Noted. Kalau kakak nanya "
             "harga VIRA, kisarannya: Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan, setup-nya "
             "sekarang gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis kakak, jadi nanti dibicarakan "
             "langsung sama Steven. " + Q_REHAN)
HARGA_TAK_DIMINTA = ("Basic mulai Rp3.000.000 per bulan, sudah termasuk setup. Angka finalnya Steven yang tentukan "
                     "setelah lihat kebutuhan kakak. Chat masuk sehari kira-kira ada berapa kak?")
TANYA_NAMA_USAHA = "Oh iya, nama usahanya apa kak?"
TANYA_BIDANG = "Usahanya bergerak di bidang apa kak?"
TANYA_VOLUME = "Kira-kira sehari ada berapa chat masuk kak?"


def pre2(pesan, lalu, baru=False):
    """Preprocess ASLI dengan balasan terakhir (Resolve User Row) - sama dengan jalur live."""
    teks = ("[SYSTEM_DATA]\nUSER_WA: 628\nIS_NEW_USER: %s\n\nCRITICAL INSTRUCTION:\nlanjut\n\n"
            "[USER QUERY]\n" % ("true" if baru else "false")) + pesan
    return satu(jalan("Preprocess - Context Detection",
                      nodes={"Parse Config": [item(config=cfg())],
                             "Resolve User Row": [item(last_bot_reply=lalu)]},
                      inp=[item(ai_input_text=teks, user_wa="628")]))


def proses3(ai_output, pesan_user, prev_row=None, galian_kolom=None, baru=False):
    """Process All dengan keluaran Preprocess ASLI (bukan tiruan askingPrice=False)."""
    rk = {"katalog": {"links": LINKS}}
    if galian_kolom is not None:
        rk["galian_kolom"] = galian_kolom
    prev = {"resolved_key": "6289900112233", "nama_lengkap": "", "nama_bisnis": "", "industri": "",
            "masalah_utama": "", "volume_chat": "", "budget_range": "", "minat_paket": "", "bahasa": "",
            "deck_requested": "", "brief_terisi": "", "last_bot_reply": "", "last_bot_reply_ts": 0}
    prev.update(prev_row or {})
    pr = pre2(pesan_user, prev["last_bot_reply"], baru)
    return satu(jalan("Process All", nodes={
        "Chat Counter": [item(original_message=pesan_user, user_wa="6289900112233", user_name="Prospek")],
        "Preprocess - Context Detection": [item(**pr)],
        "Parse Config": [item(config=cfg())],
        "Resolve User Row": [item(**prev)],
        "Rakit Konteks": [item(**rk)],
    }, inp=[item(output=ai_output)]))


# ---- W1 Preprocess: jawaban atas pertanyaanku bukan pertanyaan harga ------------
d = pre2(ALUR_REHAN, LALU_1340)
cek("W1  uji 13:41: jawaban langkah 'harga dulu, trs ...' -> TIDAK memicu konteks harga",
    d["askingPrice"] is False and d["hargaBukanTanya"] is True, d["aiContext"])
cek("W1b ... dan tidak ada blok [CONTEXT] yang bisa dikutip model", d["aiContext"] == "" and "[CONTEXT:" not in d["ai_input_text"],
    d["ai_input_text"][-160:])
d = pre(ALUR_REHAN)
cek("W1c tanpa balasan terakhir (node tidak ada) -> perilaku v3.12, node tidak error",
    d is not None and d["askingPrice"] is True and d["hargaBukanTanya"] is False)
cek("W1d catatan harga (v3.13): + alur penjualan, + larangan mengutip",
    'alur penjualannya ("harga dulu, terus transfer")' in d["aiContext"]
    and "Catatan ini hanya untukmu: jangan dikutip, jangan dikomentari di balasan." in d["aiContext"]
    and "Periksa dulu" in d["aiContext"] and "JANGAN sebut angka" in d["aiContext"], d["aiContext"])
for pesan, lalu, judul in [
        ("tanya2 dlu, trs minta pricelist, dan pesen", G5, "uji 23/09 Abdul, jawaban langkah"),
        ("Harga sewa, cara sewa, ongkir berapa", "Yang paling sering ditanyain calon penyewa biasanya apa aja kak?",
         "uji 21/09 Jacob, jawaban pertanyaan tersering (ada 'berapa')"),
        ("harga, ongkir, sama stok", "Biasanya mereka paling sering nanya apa aja kak, selain harga?", "pertanyaan pelanggan"),
        ("tanya harga dulu, kalau cocok baru transfer", "Dari chat pertama sampai jadi pesan, biasanya gimana alurnya kak?",
         "'alur' + 'dari chat'"),
        ("biasanya nanya harga", "Pertanyaan yang paling sering masuk apa aja kak?", "'pertanyaan ... paling sering'")]:
    d = pre2(pesan, lalu)
    cek("W1e '%s' (%s) -> bukan pertanyaan harga" % (pesan[:38], judul),
        d["askingPrice"] is False and d["hargaBukanTanya"] is True and "menanyakan harga" not in d["aiContext"], d["aiContext"])
d = pre("Harga sewa, cara sewa, ongkir berapa")
cek("W1f pembanding: jawaban Jacob TANPA konteks tetap terbaca bertanya (perilaku lama)", d["askingPrice"] is True)
for pesan, lalu, judul in [
        ("harganya berapa kak?", Q_REHAN, "ada tanda tanya"),
        ("harga dulu?", Q_REHAN, "ada tanda tanya"),
        ("harga vira berapa", Q_REHAN, "ditujukan ke VIRA"),
        ("paket kalian berapa", Q_REHAN, "ditujukan ke kalian"),
        ("harga dulu dong", "Mau tanya soal fitur atau harga dulu kak?", "pertanyaanku bukan soal alur/pelanggan"),
        ("boleh minta pricelist", TANYA_VOLUME, "pertanyaanku soal jumlah chat"),
        (ALUR_REHAN, "Mau aku jelasin alur kerja VIRA dulu kak?", "menawarkan penjelasan alur VIRA"),
        (ALUR_REHAN, "Kakak paling pengen tanya soal apa?", "'tanya' milik prospek, bukan pelanggan"),
        (ALUR_REHAN, "Noted kak. Alurnya sudah jelas.", "balasan terakhir tanpa pertanyaan")]:
    d = pre2(pesan, lalu)
    cek("W1g '%s' sesudah '%s' (%s) -> TETAP memicu konteks harga" % (pesan[:22], lalu[:30], judul),
        d["askingPrice"] is True and d["hargaBukanTanya"] is False, d["aiContext"])
for pesan, harap in [("pelanggan sering nanya harga sama ongkir", (False, True)),
                     ("biaya adminku sebulan sekitar 3 juta", (False, True)),
                     ("halo mau tanya soal ai customer service", (False, False)),
                     ("harganya berapa ya", (True, False))]:
    d = pre(pesan)
    cek("W1h hargaBukanTanya '%s' -> askingPrice=%s hargaBukanTanya=%s" % (pesan[:32], harap[0], harap[1]),
        (d["askingPrice"], d["hargaBukanTanya"]) == harap, str((d["askingPrice"], d["hargaBukanTanya"])))
_pre = NODES["Preprocess - Context Detection"]["parameters"]["jsCode"]
cek("W1i Preprocess membaca balasan terakhir di dalam try/catch (jalur tanpa Resolve User Row tidak error)",
    "try { return String($('Resolve User Row').first().json.last_bot_reply || '').toLowerCase(); }" in _pre
    and "catch (e) { return ''; }" in _pre)
cek("W1j hargaBukanTanya hanya ditulis Preprocess dan dibaca Process All",
    sorted(n["name"] for n in wf["nodes"] if "hargaBukanTanya" in n["parameters"].get("jsCode", ""))
    == ["Preprocess - Context Detection", "Process All"])
d = pre2("tanya harga dulu, kalau cocok baru transfer", "Dari chat pertama sampai jadi pesan, biasanya alurnya gimana kak?")
cek("W1k 'alurnya' (berakhiran -nya) tetap dikenali sebagai pertanyaan alur", d["askingPrice"] is False, d["aiContext"])

# ---- W2 Process All: jaring HARGA TANPA DITANYA ------------------------------------
d = proses3(ASLI_1342, ALUR_REHAN, {"last_bot_reply": LALU_1340})
cek("W2  uji 13:42 persis -> harga & kutipan catatan dibuang, pertanyaan kembar dibuang: 'Noted.'",
    d and d["cleanOutput"] == "Noted." and d["ringkas"] == "harga+tanya-ulang", str(d and (d["cleanOutput"], d["ringkas"])))
cek("W2b ... ringkas_asli = balasan model utuh, needs_ringkas_log = 'true', last_bot_reply = terkirim",
    d and d["ringkas_asli"] == ASLI_1342 and d["needs_ringkas_log"] == "true" and d["last_bot_reply"] == "Noted.")
_ctx = {"Process All": [{"json": d}], "Resolve User Row": [{"json": {"resolved_key": "6285171701168"}}],
        "Chat Counter": [{"json": {"user_name": "Steven Leroy"}}]}
_evd = ekspr_node(NODES["Log EVENTS Ringkas"]["parameters"]["columns"]["value"]["detail"], _ctx)
cek("W2c baris EVENTS: 'dipangkas: harga+tanya-ulang | terkirim: Noted. | asli: Oh itu alur ...'",
    not _evd.get("err") and str(_evd["out"]).startswith("dipangkas: harga+tanya-ulang | terkirim: Noted. | asli: Oh itu alur bisnis"),
    str(_evd)[:200])
d = proses3(ASLI_1342, ALUR_REHAN, {"last_bot_reply": "Yang paling sering ditanyain pelanggan biasanya apa aja kak?"})
cek("W2d balasan sama tanpa pertanyaan kembar -> 'Noted.' + pertanyaan langkah (hanya harga yang dibuang)",
    d and d["cleanOutput"] == "Noted. " + Q_REHAN and d["ringkas"] == "harga", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3(HARGA_TAK_DIMINTA, "oke noted")
cek("W2e 'oke noted' dibalas daftar harga (dulu V5, lolos) -> tinggal pertanyaannya",
    d and d["cleanOutput"] == "Chat masuk sehari kira-kira ada berapa kak?" and d["ringkas"] == "harga",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3("Basic mulai Rp3.000.000 per bulan. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?",
            "iya kadang ada yg kelewat")
cek("W2f tawaran deck yang menyebut harga tanpa ditanya -> harganya dibuang, tawarannya tetap (prompt # HARGA)",
    d and d["cleanOutput"] == "Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?" and d["ringkas"] == "harga",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3("Harga dulu, terus kalau aman baru payment. Basic mulai Rp3.000.000 per bulan. Yang paling sering "
            "ditanyain pelanggan biasanya apa aja kak?", ALUR_REHAN, {"last_bot_reply": LALU_1340})
cek("W2g harga + gema sekaligus -> alasan 'harga+gema' (gema tidak lagi menimpa alasan sebelumnya)",
    d and d["cleanOutput"] == "Yang paling sering ditanyain pelanggan biasanya apa aja kak?" and d["ringkas"] == "harga+gema",
    str(d and (d["cleanOutput"], d["ringkas"])))
for judul, ai, pesan, prev, baru in [
        ("prospek BERTANYA harga", HARGA_TAK_DIMINTA, "harganya berapa kak?", {}, False),
        ("prospek minta pricelist tanpa kata tanya (askingPrice)", HARGA_TAK_DIMINTA, "info pricelist dong kak", {}, False),
        ("menyinggung uang tanpa terbaca bertanya", HARGA_TAK_DIMINTA, "budgetku 2jt cukup ga", {}, False),
        ("prospek bertanya soal lain", HARGA_TAK_DIMINTA, "bisa connect ke IG juga ga?", {}, False),
        ("semua kalimatnya pernyataan harga (tidak pernah kosong)", "Basic mulai Rp3.000.000 per bulan.", "oke", {}, False),
        ("pertanyaan soal harga MILIK DIA", "Noted kak. Harga sewa raketnya per jam kisaran berapa kak?", "oke", {}, False),
        ("persetujuan deck (brief)", DECK_BLOK + "Basic mulai Rp3.000.000 per bulan. Sudah aku teruskan ke Steven, dia "
         "sendiri yang akan menyusun decknya.", "boleh", {"last_bot_reply": TAWARAN_LIVE}, False),
        ("handover", "[TALK_TO_ADMIN]\nSiap kak, aku sambungkan ke Steven ya. Paket Basic mulai Rp3.000.000 per bulan.",
         "mau ngobrol langsung sama steven", {}, False),
        ("[UNKNOWN]", "[UNKNOWN]\nYang itu aku belum tahu pasti kak. Basic mulai Rp3.000.000 per bulan.", "oke", {}, False),
        ("pesan perkenalan", "Halo kak, aku Steven versi AI. Paket Basic mulai Rp3.000.000 per bulan. Btw boleh tau "
         "nama kakak siapa, dan nama usahanya apa?", "halo", {}, True)]:
    d = proses3(ai, pesan, prev, baru=baru)
    cek("W2h jaring HARGA tidak menyentuh: %s" % judul,
        d is not None and "harga" not in d["ringkas"].split("+")
        and ("Rp3.000.000" not in ai.replace(DECK_BLOK, "") or "Rp3.000.000" in d["cleanOutput"]),
        str(d and (d["ringkas"], d["cleanOutput"][:90])))
_pa = NODES["Process All"]["parameters"]["jsCode"]
cek("W2i jaring HARGA jalan SESUDAH alasan cadangan disiapkan & SEBELUM RINGKAS memutuskan (bolehRingkas)",
    _pa.index("let ringkasAlasan = cadangan;") < _pa.index("// ── HARGA TANPA DITANYA (2026-09-23, v3.13) ──")
    < _pa.index("const bolehRingkas = "))
cek("W2j Process All membaca askingPrice & hargaBukanTanya dari Preprocess",
    "preprocess.askingPrice === true" in _pa and "preprocess.hargaBukanTanya === true" in _pa)

# ---- W3 penangkap: sewa/persewaan, ekor, nama usaha ------------------------------------
d = tangkap("rehan\nusahaku sewa raket padel", PERKENALAN_BARU, ai="Salam kenal kak.")
cek("W3  uji 13:23 persis: 'rehan / usahaku sewa raket padel' -> nama Rehan, industri 'sewa raket padel', nama usaha KOSONG",
    d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"]) == ("Rehan", "", "sewa raket padel"),
    str(d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"])))
g, d = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": PERKENALAN_BARU}, "rehan\nusahaku sewa raket padel")
cek("W3b ... galian berikutnya: tanya ulang nama usaha (v3.12: 'bidang usahanya' -> 'persewaan aja sih')",
    g is not None and g.startswith("nama usahanya — tanya ulang")
    and "industri: sewa raket padel (baru dia sebut di pesan ini)" in d["prospect_context"], str(g))
for pesan, harap in [
        ("usahaku persewaan tenda", ("", "", "persewaan tenda", "")),
        ("Rina, sewa kamera", ("Rina", "", "sewa kamera", "")),
        ("aku Dewi, usahaku nyewain PS", ("Dewi", "", "nyewain PS", "")),
        ("Budi, usahaku sewa", ("Budi", "", "sewa", "")),
        ("Rehan, usahaku Sewa Raket Padel", ("Rehan", "Sewa Raket Padel", "", "")),
        ("Sari, Persewaan Tenda Berkah", ("Sari", "Persewaan Tenda Berkah", "", "")),
        ("Rina, Rental Mobil Jaya", ("Rina", "Rental Mobil Jaya", "rental", "")),
        ("Rina, jualan kue", ("Rina", "", "jualan kue", ""))]:
    d = tangkap(pesan, PERKENALAN_BARU, ai="Salam kenal kak.")
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"], d["masalah_utama_merged"])
    cek("W3c perkenalan '%s' -> %s" % (pesan[:34], harap), got == harap, str(got))
for pesan, lalu, kolom, harap in [
        ("persewaan aja sih", TANYA_BIDANG, "industri", "persewaan"),
        ("jualan kue aja kak", TANYA_BIDANG, "industri", "jualan kue"),
        ("katering rumahan kak", TANYA_BIDANG, "industri", "katering rumahan"),
        ("10-20 an aja sih", TANYA_VOLUME, "volume_chat", "10-20 an"),
        ("10-20 an", TANYA_VOLUME, "volume_chat", "10-20 an")]:
    d = tangkap(pesan, lalu)
    cek("W3d semua kata ekor dibuang: '%s' -> %s=%r" % (pesan, kolom, harap), d and d[kolom + "_merged"] == harap,
        str(d and d[kolom + "_merged"]))
d = tangkap("50 chat sehari aja kak", "Yang paling bikin repot pas lagi rame, biasanya bagian mananya?", prev={"masalah_utama": "chat numpuk"})
cek("W3e jumlah chat tanpa ditanya: ekor dibuang semua", d and d["volume_chat_merged"] == "50 chat sehari", str(d and d["volume_chat_merged"]))
for pesan in ["sewa raket padel aja", "sewa raket padel", "Sewa raket padel", "jualan kue aja kak", "persewaan aja sih",
              "gaada kak", "ngga ada nama", "blm ada", "tanpa nama kak", "belum ada nama kak"]:
    d = tangkap(pesan, TANYA_NAMA_USAHA)
    cek("W3f jawab nama usaha '%s' -> BUKAN nama usaha" % pesan, d and d["nama_bisnis_merged"] == "", str(d and d["nama_bisnis_merged"]))
for pesan, harap in [("Sewa Raket Padel", "Sewa Raket Padel"), ("Persewaan Tenda Berkah", "Persewaan Tenda Berkah"),
                     ("PadelKu", "PadelKu"), ("Rental Mobil Jaya", "Rental Mobil Jaya"), ("namanya Padel Pro kak", "Padel Pro"),
                     ("Kopi Senja kak", "Kopi Senja"), ("boleh kak, namanya Teamsultan", "Teamsultan")]:
    d = tangkap(pesan, TANYA_NAMA_USAHA)
    cek("W3g nama usaha asli tetap tertangkap: '%s' -> %r" % (pesan, harap), d and d["nama_bisnis_merged"] == harap,
        str(d and d["nama_bisnis_merged"]))
for lalu, pesan in [(PERKENALAN_BARU, "rehan\nusahaku sewa raket padel"), (TANYA_NAMA_USAHA, "sewa raket padel aja"),
                    (TANYA_NAMA_USAHA, "Sewa Raket Padel"), (TANYA_NAMA_USAHA, "gaada kak"),
                    (TANYA_BIDANG, "persewaan aja sih"), (TANYA_VOLUME, "10-20 an aja sih")]:
    _, drk = galian2({"greeting_sent": "Y", "Counter": "2", "last_bot_reply": lalu}, pesan)
    rk_f = dict(_re.findall(r"^(\w+): (.*) \(baru dia sebut di pesan ini\)$", drk["prospect_context"], _re.M))
    dpa = tangkap(pesan, lalu)
    pa_f = {k: dpa[k + "_merged"] for k in ("nama_lengkap", "nama_bisnis", "industri", "masalah_utama", "volume_chat")
            if dpa[k + "_merged"]}
    cek("W3h Rakit Konteks & Process All sepakat soal fakta '%s'" % pesan.replace("\n", " / ")[:40],
        rk_f == pa_f, "RK=%s PA=%s" % (rk_f, pa_f))

# ---- W4 prompt -----------------------------------------------------------------------
_sp1 = _sp.replace("\n", " ")
_harga = _sp.split("\n# HARGA\n")[1].split("\n# ")[0].replace("\n", " ")
cek("W4  # HARGA: alur penjualan bukan pertanyaan harga, dan jangan mengomentarinya",
    "Sama halnya waktu dia menceritakan alur penjualannya (“harga dulu, terus kalau cocok baru transfer”): itu jawaban "
    "soal alurnya — jangan menyinggung harga VIRA sama sekali, dan jangan mengomentari bahwa itu bukan pertanyaan harga."
    in _harga, _harga[:120])
cek("W4b contoh prompt tidak memuat nama/usaha uji (rehan, padel)", "rehan" not in _sp.lower() and "padel" not in _sp.lower())
_tag = _sp.split("\n# TAG\n")[1].split("\n# ")[0]
cek("W4c # TAG: tag handover = SUDAH disambungkan, jangan tanya 'mau aku sambungkan?', singkatan sama artinya",
    '  Dia sudah minta, jadi langsung sambungkan — jangan bertanya lagi "mau aku sambungkan?".\n'
    '  Permintaan yang ditulis singkat ("kpn bs ngmng sm steven?") sama artinya.\n' in _tag)

# ---- W5 handover: permintaan bicara dengan Steven langsung disambungkan ----------------------
# Lanjutan uji live 13:58-14:06 (masih v3.12), sesudah deck dikirim 13:53.
LALU_1359 = "Noted kak, condongnya ke Basic. Nanti Steven yang bantu bahas detailnya langsung."
LALU_1402 = "Siap kak. Kalau ada yang mau ditanyakan soal VIRA, aku di sini."
KIRIM_1406 = "Steven biasanya balas begitu sedang online kak. Mau aku sambungkan supaya dia langsung menghubungi kakak?"
KALIMAT_HANDOVER = "Siap kak, sudah aku sambungkan ke Steven. Dia yang akan menghubungi kakak langsung di nomor ini ya."
_BOT = NODES["Update row in sheet"]["parameters"]["columns"]["value"]["bot_mode"]


def bot_mode(d):
    return ekspr_node(_BOT, {"Process All": [{"json": d}]}).get("out")


d = proses3("[TALK_TO_ADMIN]\n" + KIRIM_1406, "kpn bs ngmng sm steven?", {"last_bot_reply": LALU_1402})
cek("W5  uji 14:06 persis: 'kpn bs ngmng sm steven?' + tag -> bot DIMATIKAN (v3.12: tetap ON)",
    d and d["isTalkToAdmin"] is True and d["matikanBot"] is True and bot_mode(d) == "OFF",
    str(d and (d["isTalkToAdmin"], d["matikanBot"], bot_mode(d))))
cek("W5b ... balasan mengonfirmasi, tawaran 'Mau aku sambungkan...?' dibuang",
    d and d["cleanOutput"] == KALIMAT_HANDOVER + " Steven biasanya balas begitu sedang online kak."
    and d["ringkas"] == "handover" and d["needs_ringkas_log"] == "true", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3(KIRIM_1406, "kpn bs ngmng sm steven?", {"last_bot_reply": LALU_1402})
cek("W5c model LUPA menulis tag -> handover dinyalakan kode, balasan = kalimat konfirmasi utuh",
    d and d["isTalkToAdmin"] is True and d["matikanBot"] is True and d["cleanOutput"] == KALIMAT_HANDOVER,
    str(d and (d["isTalkToAdmin"], d["matikanBot"], d["cleanOutput"])))
d = proses3(LALU_1402, "kpn y bs ngmngnya?", {"last_bot_reply": LALU_1359})
cek("W5d uji 14:00 'kpn y bs ngmngnya?' sesudah 'Nanti Steven yang bantu bahas...' -> disambungkan",
    d and d["isTalkToAdmin"] is True and d["matikanBot"] is True and d["cleanOutput"] == KALIMAT_HANDOVER,
    str(d and (d["isTalkToAdmin"], d["matikanBot"], d["cleanOutput"])))
for pesan in ["mau ngobrol langsung sama steven", "bisa telpon steven ga?", "tolong hubungi steven ya",
              "boleh chat stevennya langsung?", "kapan steven bisa dihubungi?", "gmn cara ngobrol sm stev?"]:
    d = proses3("Siap kak.", pesan)
    cek("W5e '%s' -> disambungkan walau model lupa tag" % pesan,
        d and d["isTalkToAdmin"] is True and d["matikanBot"] is True and d["cleanOutput"] == KALIMAT_HANDOVER,
        str(d and (d["isTalkToAdmin"], d["matikanBot"])))
for pesan, lalu, judul in [
        ("ini lagi chat sama steven?", "", "pertanyaan identitas"),
        ("bisa chat sama steven beneran ga?", "", "identitas (beneran)"),
        ("ga usah ngobrol sama steven, aku tanya kamu aja", "", "menolak"),
        ("kapan bisa ketemu?", "Yang paling bikin repot soal chat sekarang apa kak?", "'kapan' tanpa Steven di pesan/balasan"),
        ("kapan bisa mulai?", LALU_1359, "'kapan' tanpa kata bicara"),
        ("steven itu siapa?", "", "bertanya tentang Steven"),
        ("pelanggan suka nanya bisa ngobrol sama admin ga", "", "cerita pelanggan, bukan Steven")]:
    d = proses3("Siap kak, ada lagi yang mau ditanyakan?", pesan, {"last_bot_reply": lalu})
    cek("W5f '%s' (%s) -> TIDAK disambungkan oleh kode" % (pesan[:34], judul),
        d and d["isTalkToAdmin"] is False and d["matikanBot"] is False and "handover" not in d["ringkas"],
        str(d and (d["isTalkToAdmin"], d["matikanBot"], d["ringkas"])))
d = proses3("[TALK_TO_ADMIN]\nSiap kak, aku sambungkan ke Steven ya. Dia biasanya balas di hari yang sama. Ada yang mau "
            "aku titipkan ke dia kak?", "mau ngobrol langsung sama steven")
cek("W5g balasan tag yang SUDAH mengonfirmasi tidak diubah (pertanyaan lain tidak dibuang)",
    d and d["matikanBot"] is True and d["ringkas"] == "" and d["cleanOutput"].endswith("Ada yang mau aku titipkan ke dia kak?"),
    str(d and (d["ringkas"], d["cleanOutput"])))
d = proses3("[TALK_TO_ADMIN]\nMau aku sambungkan ke Steven kak?", "oke")
cek("W5h tag tanpa permintaan eksplisit -> bot tetap hidup, balasan tidak diubah (perilaku lama)",
    d and d["isTalkToAdmin"] is True and d["matikanBot"] is False and d["cleanOutput"] == "Mau aku sambungkan ke Steven kak?",
    str(d and (d["matikanBot"], d["cleanOutput"])))
d = proses3("Siap kak.", "iya", {"last_bot_reply": KIRIM_1406})
cek("W5i 'iya' atas tawaran 'Mau aku sambungkan...?' -> disambungkan (v3.12: tidak dikenali)",
    d and d["isTalkToAdmin"] is True and d["matikanBot"] is True and d["cleanOutput"] == KALIMAT_HANDOVER,
    str(d and (d["isTalkToAdmin"], d["matikanBot"], d["cleanOutput"])))
d = proses3("Siap kak.", "boleh dibuatin deck, trs kpn bs ngmng sm steven?")
cek("W5j minta deck + minta bicara di satu pesan -> bicara menang (aturan lama NIAT_BICARA)",
    d and d["deckDiminta"] is False and d["isTalkToAdmin"] is True and d["matikanBot"] is True,
    str(d and (d["deckDiminta"], d["isTalkToAdmin"], d["matikanBot"])))
d = proses3(DECK_BLOK + "Sudah aku teruskan ke Steven, dia sendiri yang akan menyusun decknya.", "boleh",
            {"last_bot_reply": TAWARAN_LIVE})
cek("W5k persetujuan deck TIDAK jadi handover (tawaran deck bukan tawaran menyambungkan)",
    d and d["deckDiminta"] is True and d["isTalkToAdmin"] is False and d["matikanBot"] is False,
    str(d and (d["deckDiminta"], d["isTalkToAdmin"], d["matikanBot"])))
for kalimat in ["Nanti Steven sendiri yang akan menyusun decknya dan menghubungi kakak langsung.",
                "Deck kakak sudah dikirim Steven ya kak."]:
    d = proses3("Siap kak.", "oke", {"last_bot_reply": kalimat})
    cek("W5l 'oke' sesudah '%s...' -> BUKAN persetujuan diskusi" % kalimat[:32],
        d and d["isTalkToAdmin"] is False, str(d and d["isTalkToAdmin"]))
_pa = NODES["Process All"]["parameters"]["jsCode"]
cek("W5m blok HANDOVER jalan sesudah semua jaring RINGKAS & sebelum media/penghapus nama",
    _pa.index("// ── RINGKAS (2026-09-23) ──") < _pa.index("// ── HANDOVER: balasan wajib mengonfirmasi (2026-09-23, v3.13) ──")
    < _pa.index("// ── RESOLVE MEDIA URL") < _pa.index("const namaSimpan"))
cek("W5n gerbang mintaSteven jalan SESUDAH mintaDeck & pembatalan handover-oleh-deck, SEBELUM matikanBot",
    _pa.index("const mintaDeck =") < _pa.index("if (isTalkToAdmin && mintaDeck && isDeckRequest)")
    < _pa.index("const mintaSteven =") < _pa.index("const matikanBot ="))

# ---- W6 Merge Brief: sesudah deck terkirim cukup notif singkat UPDATE PROSPEK ----------------
LAMA_REHAN = {"no_wa": "6289900112233", "ts": "2026-09-23 13:51:26", "brief_jumlah": 13, "nama": "Rehan",
              "nama_bisnis": "sewa raket padel", "industri": "persewaan", "deskripsi_bisnis": "penyewaan raket padel",
              "channel": "WhatsApp dan platform lain", "volume_chat_harian": "10-20 an",
              "masalah_utama": "balesin chat satu-satu suka tenggelam", "aksi_utama": "sewa raket",
              "alur_setelah_chat": "harga dulu, kalau aman baru payment", "pertanyaan_tersering": "prosedur dan lain-lain",
              "bahasa_deck": "ID", "kutipan_asli": "balesin chat 1 1 sih | suka tenggelem",
              "deck_dikirim_ts": "2026-09-23 13:53:51"}
BRIEF_1359 = {k: v for k, v in LAMA_REHAN.items() if k not in ("no_wa", "ts", "brief_jumlah", "deck_dikirim_ts")}
BRIEF_1359.update(minat_paket="Basic", catatan="condong ke paket Basic", deskripsi_bisnis="jasa persewaan raket padel",
                  kutipan_asli="balesin chat 1 1 sih | suka tenggelem | basic deh")
_PA_1359 = {"deckRequest": BRIEF_1359, "deckLayak": True, "isDeckRequest": True}
d = merge(_PA_1359, requests_lama=[LAMA_REHAN])
cek("W6  uji 13:58 'basic deh' sesudah deck terkirim -> notif SINGKAT 'UPDATE PROSPEK'",
    d and d["deck_layak"] is True and d["notif_text"].startswith("🔄 [VIRA Personal] UPDATE PROSPEK — deck sudah terkirim")
    and "DECK SIAP" not in d["notif_text"] and "Generate deck" not in d["notif_text"], str(d and d["notif_text"][:120]))
cek("W6b ... isinya hanya yang baru: minat paket & catatan (deskripsi yang ditulis ulang & kutipan tidak)",
    d and d["notif_text"].split("\n\n", 1)[1].split("\n") == ["Minat paket: Basic", "Catatan: condong ke paket Basic"]
    and "sewa raket padel · Rehan · WA: 6289900112233" in d["notif_text"], str(d and d["notif_text"]))
cek("W6c ... REQUESTS tetap diperbarui seperti biasa (nilai baru menang, deck_dikirim_ts tidak disentuh)",
    d and d["minat_paket"] == "Basic" and d["deskripsi_bisnis"] == "jasa persewaan raket padel"
    and "deck_dikirim_ts" not in d, str(d and (d["minat_paket"], d["deskripsi_bisnis"])))
d = merge(_PA_1359, requests_lama=[dict(LAMA_REHAN, minat_paket="Basic", catatan="condong ke paket Basic")])
cek("W6d brief ditulis ulang tanpa isi baru sesudah deck -> TIDAK ada notif (v3.12: notif lengkap lagi)",
    d and d["deck_layak"] is False, str(d and d["deck_layak"]))
d = merge(dict(_PA_1359, deckRequest=dict(BRIEF_1359, minat_paket="Premium")),
          requests_lama=[dict(LAMA_REHAN, minat_paket="Basic", catatan="condong ke paket Basic")])
cek("W6e paket berubah Basic -> Premium -> notif singkat berisi perubahan itu",
    d and d["deck_layak"] is True and d["notif_text"].split("\n\n", 1)[1] == "Minat paket: Premium", str(d and d["notif_text"]))
d = merge(_PA_1359, requests_lama=[{k: v for k, v in LAMA_REHAN.items() if k != "deck_dikirim_ts"}])
cek("W6f SEBELUM deck terkirim -> notif lengkap seperti biasa",
    d and d["deck_layak"] is True and d["notif_text"].startswith("📋 [VIRA Personal] BRIEF DECK (diperbarui)"))
d = merge(dict(_PA_1359, deckDiminta=True), requests_lama=[LAMA_REHAN])
cek("W6g minta deck lagi sesudah deck terkirim -> notif lengkap (permintaan, bukan update)",
    d and d["deck_layak"] is True and d["notif_text"].startswith("📋 [VIRA Personal] BRIEF DECK"))
d = merge(dict(_PA_1359, deckRequest=dict(BRIEF_1359, nama_bisnis="Kopi Senja", industri="kopi")), requests_lama=[LAMA_REHAN])
cek("W6h bisnis LAIN di nomor yang sama sesudah deck -> brief baru, notif lengkap (gerbang identitas lama)",
    d and d["deck_layak"] is True and d["notif_text"].startswith("📋 [VIRA Personal] BRIEF DECK\n"), str(d and d["notif_text"][:60]))
d = satu(jalan("Merge Brief", nodes={
    "Process All": [item(**dict({"nama_lengkap_merged": "", "nama_bisnis_merged": "", "industri_merged": "",
                                  "masalah_utama_merged": "", "minat_paket_merged": "", "budget_range_merged": "",
                                  "volume_chat_merged": "", "deckDiminta": False}, **_PA_1359))],
    "Resolve User Row": [item(resolved_key="6289900112233", lead_source_db="Organik",
                              userRow={"deck_terkirim_ts": "1790146431"})],
    "Read REQUESTS": items({k: v for k, v in LAMA_REHAN.items() if k != "deck_dikirim_ts"}),
}, inp=[item()]))
cek("W6i REQUESTS belum mencatat deck_dikirim_ts tapi STATS.deck_terkirim_ts ada -> tetap mode update",
    d and d["notif_text"].startswith("🔄 [VIRA Personal] UPDATE PROSPEK"), str(d and d["notif_text"][:60]))
# ---- W7 temuan eval model asli v3.13 putaran 1 -------------------------------------------------
_S2_LALU = "Salam kenal kak. Kalau chat numpuk pas malem, biasanya yang paling sering ditanyain apa aja kak?"
_S2_PREV = {"last_bot_reply": _S2_LALU, "nama_lengkap": "Nadia", "industri": "katering",
            "masalah_utama": "chat suka numpuk pas malem"}
d = proses3('Noted kak. Yang paling sering ditanyain di chat biasanya apa aja kak?\n\n'
            '[FACTS nama="Nadia" nama_bisnis="Dapur Nadia" industri="katering"]', "Dapur Nadia", _S2_PREV,
            galian_kolom="nama_bisnis")
cek("W7  eval S2: nama usaha disebut tanpa ditanya & dicatat model -> galian nama usaha TIDAK ditempel",
    d and d["cleanOutput"] == "Noted kak." and d["ringkas"] == "tanya-ulang" and d["nama_bisnis_merged"] == "Dapur Nadia",
    str(d and (d["cleanOutput"], d["ringkas"], d["nama_bisnis_merged"])))
d = proses3('Noted kak. Yang paling sering ditanyain di chat biasanya apa aja kak?', "oke", _S2_PREV, galian_kolom="nama_bisnis")
cek("W7b ... kalau nama usaha MASIH kosong, galiannya tetap ditempel (perilaku v3.12)",
    d and d["cleanOutput"] == "Noted kak. Oh iya, nama usahanya apa kak?" and d["ringkas"] == "tanya-ulang+galian",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3('Oke kak. Usahanya bergerak di bidang apa kak?\n[FACTS industri="katering"]', "katering kak", {},
            galian_kolom="industri")
cek("W7c pertanyaan 'sudah tahu' dibuang, dan galian untuk kolom yang BARU terisi tidak ditempel",
    d and d["cleanOutput"] == "Oke kak." and d["ringkas"] == "sudah-tahu", str(d and (d["cleanOutput"], d["ringkas"])))
_S5_MENTAH = ('[FACTS volume_chat="100an chat pas weekend"]\n\nBoleh banget kak. Mau aku mintakan Steven buatkan deck '
              'khusus buat Kopi Senja? Nanti Steven sendiri yang susun dan hubungi kakak langsung.\n\n' + DECK_BLOK)
d = proses3(_S5_MENTAH, "boleh dong dibuatin deck", {"nama_lengkap": "Rina", "nama_bisnis": "Kopi Senja", "industri": "kopi"})
cek("W7d eval S5: minta deck dibalas tawaran deck -> tawarannya dibuang, kabar Steven akan menyusun tetap",
    d and d["cleanOutput"] == "Boleh banget kak. Nanti Steven sendiri yang susun dan hubungi kakak langsung."
    and d["ringkas"] == "deck" and d["deckNotify"] is True, str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3(DECK_BLOK + "Boleh kak. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?", "boleh dong dibuatin deck")
cek("W7e ... tanpa kalimat kabar -> kalimat kabar baku ditambahkan, sapaan pendek dibuang",
    d and d["cleanOutput"] == "Siap kak, sudah aku teruskan ke Steven. Dia sendiri yang akan menyusun decknya dan menghubungi "
    "kakak langsung." and d["ringkas"] == "deck", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses3("Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?", "iya kadang ada yg kelewat")
cek("W7f tawaran deck BIASA (prospek belum minta) tidak disentuh", d and d["ringkas"] == ""
    and d["cleanOutput"] == "Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?", str(d and d["ringkas"]))
d = proses3("[TALK_TO_ADMIN]\nSiap kak. Mau aku sambungkan ke Steven sekarang?", "bisa ngobrol langsung sama steven?")
cek("W7g handover + sapaan pendek -> konfirmasi baku saja (tanpa 'Siap kak.' ganda)",
    d and d["matikanBot"] is True and d["cleanOutput"] == KALIMAT_HANDOVER, str(d and d["cleanOutput"]))
# ---- W8 temuan eval putaran 2: nama usaha dari model yang cuma jenis usaha -------------------------
_S6_LALU = "Salam kenal kak. Usahanya sewa raket padel ya, boleh tau nama usahanya apa?"
_S6_PREV = {"last_bot_reply": _S6_LALU, "nama_lengkap": "Rehan", "industri": "sewa raket padel"}
d = proses3('Noted kak. Soal chat, yang paling bikin repot sekarang apa kak?\n\n[FACTS nama_bisnis="persewaan"]',
            "persewaan aja sih", _S6_PREV)
cek("W8  eval S6: [FACTS nama_bisnis=\"persewaan\"] -> TIDAK jadi nama usaha, industri lama tetap",
    d and d["nama_bisnis_merged"] == "" and d["nama_bisnis_changed"] is False and d["industri_merged"] == "sewa raket padel",
    str(d and (d["nama_bisnis_merged"], d["industri_merged"])))
for fakta, harap in [('nama_bisnis="Padel Pro"', ("Padel Pro", "sewa raket padel")),
                     ('nama_bisnis="Sewa Raket Padel"', ("Sewa Raket Padel", "sewa raket padel")),
                     ('nama_bisnis="sewa raket padel"', ("", "sewa raket padel")),
                     ('nama_bisnis="Kopi Senja"', ("Kopi Senja", "sewa raket padel"))]:
    d = proses3("Noted kak.\n[FACTS %s]" % fakta, "oke", _S6_PREV)
    got = d and (d["nama_bisnis_merged"], d["industri_merged"])
    cek("W8b [FACTS %s] -> nama_bisnis=%r" % (fakta, harap[0]), got == harap, str(got))
d = proses3('Noted kak.\n[FACTS nama_bisnis="katering"]', "katering kak", {})
cek("W8c [FACTS nama_bisnis=jenis usaha] & bidang usaha masih kosong -> pindah ke industri",
    d and d["nama_bisnis_merged"] == "" and d["industri_merged"] == "katering" and d["industri_changed"] is True,
    str(d and (d["nama_bisnis_merged"], d["industri_merged"])))
d = proses3('Noted kak.\n[FACTS nama_bisnis="persewaan"]', "persewaan aja sih", dict(_S6_PREV, nama_bisnis="Padel Pro"))
cek("W8d nama usaha lama di STATS tidak ditimpa/dihapus", d and d["nama_bisnis_merged"] == "Padel Pro")
_BRIEF_LIVE = ("Siap kak.\n[DECK_REQUEST]\nnama: Rehan\nnama_bisnis: sewa raket padel\nindustri: persewaan\n"
               "masalah_utama: balesin chat satu-satu suka tenggelam\n[/DECK_REQUEST]")
d = proses3(_BRIEF_LIVE, "okee", {"nama_lengkap": "Rehan"})
cek("W8e brief live 13:51 (nama_bisnis: sewa raket padel) -> nama usaha kosong, industri tetap 'persewaan'",
    d and d["deckRequest"]["nama_bisnis"] == "" and d["deckRequest"]["industri"] == "persewaan"
    and "nama_bisnis" in d["deckMissing"], str(d and (d["deckRequest"]["nama_bisnis"], d["deckRequest"]["industri"])))
d = proses3(_BRIEF_LIVE.replace("industri: persewaan\n", ""), "okee", {"nama_lengkap": "Rehan"})
cek("W8f ... bidang usaha di brief kosong -> diisi dari nilai itu", d and d["deckRequest"]["industri"] == "sewa raket padel"
    and d["deckRequest"]["nama_bisnis"] == "", str(d and d["deckRequest"]["industri"]))
d = proses3(_BRIEF_LIVE.replace("nama_bisnis: sewa raket padel", "nama_bisnis: Padel Pro"), "okee", {"nama_lengkap": "Rehan"})
cek("W8g nama usaha asli di brief tetap", d and d["deckRequest"]["nama_bisnis"] == "Padel Pro")
_notif = NODES["Siapkan Notif Deck"]["parameters"]["jsCode"]
cek("W6j Siapkan Notif Deck meneruskan deck_layak & notif_text apa adanya (node tidak diubah)",
    "deck_layak:  mb.deck_layak === true," in _notif and "notif_text:  String(mb.notif_text || '')," in _notif)


# ===========================================================================
'''
ganti('bagian("R. BEDAH REGRESI v3.12 vs v3.11', SEKSI_W + 'bagian("R. BEDAH REGRESI v3.12 vs v3.11')

# --- 4. seksi R ditulis ulang: v3.13 vs v3.12 ----------------------------
SEKSI_R = r'''bagian("R. BEDAH REGRESI v3.13 vs v3.12 (= live, dicek MCP 2026-09-23 12:19 WIB)")
# ===========================================================================
import collections as _col
with open(os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.12.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Preprocess - Context Detection", "Process All", "Rakit Konteks", "Merge Brief"}

cek("R1  node sama dengan v3.12: 91, tanpa node baru/hilang", set(NODES) == set(_NL) and len(wf["nodes"]) == 91,
    str(sorted(set(NODES) ^ set(_NL))))
cek("R2  koneksi identik dengan v3.12", json.dumps(_lama["connections"], sort_keys=True) == json.dumps(CONNS, sort_keys=True))
_beda = sorted(n for n in _NL if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  86 node lain identik byte per byte dengan v3.12", not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))
_pk = [n for n in DIUBAH - {"AI Agent"} if {k: v for k, v in NODES[n]["parameters"].items() if k != "jsCode"}
       != {k: v for k, v in _NL[n]["parameters"].items() if k != "jsCode"}]
cek("R4a node kode yang diubah: hanya jsCode yang berubah (mode dll tetap)", not _pk, str(_pk))
_s0, _s1 = dict(_lama["settings"]), dict(wf["settings"])
cek("R4b settings: hanya errorWorkflow yang berubah (P_ECOT... -> 0mp_..., notifier GLOBAL = live)",
    _s0.pop("errorWorkflow") == "P_ECOTzcz99B1siU-BcDW" and _s1.pop("errorWorkflow") == "0mp_AdLtInm68RxQUwLqV"
    and _s0 == _s1 and _s1.get("availableInMCP") is True)
cek("R4c kredensial tiap node tetap", all(NODES[n].get("credentials") == _NL[n].get("credentials") for n in _NL))
cek("R4d webhookId tiap node tetap", all(NODES[n].get("webhookId") == _NL[n].get("webhookId") for n in _NL))


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


def _cek_hilang(kode, nama, lama, baru, izin):
    keluar = _hilang(lama, baru)
    liar = [l for l in keluar if not any(l.startswith(i) for i in izin)]
    cek("%s  %s: tidak ada baris v3.12 yang hilang selain %d baris yang memang diganti" % (kode, nama, len(izin)),
        not liar, str(liar))
    cek("%sb %s: %d baris itu masing-masing hilang tepat sekali" % (kode, nama, len(izin)),
        len(keluar) == len(izin) and all(sum(1 for l in keluar if l.startswith(i)) == 1 for i in izin), str(keluar))


_IZIN_BLOK = [
    "const ambilJawaban = (kolom, pesan) => {",
    "if (/^(belum|masih|rahasia|nanti|gak|nggak|tidak|kok)\\b/i.test(s)) return '';",
    ".replace(EKOR, '').trim();",                                  # bidang usaha -> EKOR_SEMUA
    "const s = baris1.replace(EKOR, '').trim();",                  # jumlah chat -> EKOR_SEMUA
    "return baris ? BERSIH(baris.replace(LEPAS_AWAL, '').replace(EKOR, ''), 120) : '';",
    "const JENIS_USAHA = ",                                        # + sewa|persewaan|penyewaan
    "const DAGANGAN = /^(jualan|jual)\\s+\\S/i;",
    "if (JENIS_USAHA.test(isi) || DAGANGAN.test(isi)) { if (!hasil.industri) hasil.industri = isi; continue; }",
    "const isi = ambilJawaban('nama_bisnis', bersih);",
]
_pa0, _pa1 = _NL["Process All"]["parameters"]["jsCode"], NODES["Process All"]["parameters"]["jsCode"]
_cek_hilang("R5 ", "Process All", _pa0, _pa1, _IZIN_BLOK + [
    "if (kal.length < jumlahAwal) ringkasAlasan = 'gema';",
    "const NIAT_BICARA = ",                                         # + bahasa chat ke Steven
    "const TAWARAN_DISKUSI = ",                                     # + tawaran menyambungkan
    "|| SETUJU_DISKUSI;",                                           # mintaBicara + mintaSteven
    "if (kalBaru.length < kal.length && (kalBaru.length || TANYA_GALIAN[GALIAN_KOLOM])) {",   # -> GALIAN_TERBUKA
    "kal = kalBaru.length ? kalBaru : [TANYA_GALIAN[GALIAN_KOLOM]];",
    "if (ringkasAlasan && !cadangan && !isNewUser && !PROSPEK_BERTANYA && TANYA_GALIAN[GALIAN_KOLOM]",
    "cleanOutput = cleanOutput.trim() + ' ' + TANYA_GALIAN[GALIAN_KOLOM];",
])
_rk0, _rk1 = _NL["Rakit Konteks"]["parameters"]["jsCode"], NODES["Rakit Konteks"]["parameters"]["jsCode"]
_cek_hilang("R7 ", "Rakit Konteks", _rk0, _rk1, _IZIN_BLOK + ["&& !/telp|telepon|telfon|call|ditelpon"])
_mb0, _mb1 = _NL["Merge Brief"]["parameters"]["jsCode"], NODES["Merge Brief"]["parameters"]["jsCode"]
_cek_hilang("R13", "Merge Brief", _mb0, _mb1, [
    "deck_layak: pa.deckLayak === true || pa.deckDiminta === true",
    "|| (pa.isDeckRequest === true && (pertamaKali || bertambah)),",
    "notif_text,",
])
_pr0 = _NL["Preprocess - Context Detection"]["parameters"]["jsCode"]
_pr1 = NODES["Preprocess - Context Detection"]["parameters"]["jsCode"]
_cek_hilang("R12", "Preprocess", _pr0, _pr1, [
    "const askingPrice = TANYA_HARGA_KITA",
    "|| (KATA_HARGA.test(message) && !CERITA_ORANG_LAIN && !MILIK_DIA)",
    "&& !CERITA_ORANG_LAIN && !MILIK_DIA);",
    "if (askingPrice) aiContext += 'Sepertinya dia menanyakan harga.",
])
_blok = lambda s: s[s.index("// ── PENANGKAP JAWABAN — MULAI ──"):s.index("// ── PENANGKAP JAWABAN — SELESAI ──")]
_luar = lambda s: s.replace(_blok(s), "")
def _hapus_antara(s, awal, akhir):
    """Buang teks dari `awal` (harus tunggal) sampai tepat sebelum `akhir` berikutnya."""
    assert s.count(awal) == 1 and akhir in s[s.index(awal):], (awal[:50], akhir[:50])
    i = s.index(awal)
    return s[:i] + s[s.index(akhir, i):]


_n0 = _re.search(r"const NIAT_BICARA = (/.+?/);\n", _pa0).group(1)
_n1 = _re.search(r"const NIAT_BICARA = (/.+?/);\n", _pa1).group(1)
_t0 = _re.search(r"const TAWARAN_DISKUSI = .+\n", _pa0).group(0)
_t1 = _re.search(r"const TAWARAN_DISKUSI = .+\n", _pa1).group(0)


def _pulihkan_pa(s):
    """Balikkan SEMUA perubahan v3.13 yang disengaja di luar blok penangkap -> harus = v3.12."""
    s = _luar(s)
    s = _hapus_antara(s, "// ── HARGA TANPA DITANYA (2026-09-23, v3.13) ──", "const bolehRingkas = ")
    s = _hapus_antara(s, "// ── DECK SUDAH DITERUSKAN (2026-09-23, v3.13) ──", "// ── RESOLVE MEDIA URL")
    s = _hapus_antara(s, "// ── HANDOVER: balasan wajib mengonfirmasi (2026-09-23, v3.13) ──", "// ── RESOLVE MEDIA URL")
    s = _hapus_antara(s, "// Galian yang kolomnya MASIH kosong", "// Balasan model yang isinya CUMA tag")
    s = _hapus_antara(s, "// ── Nama usaha dari model yang cuma jenis usaha (2026-09-23, v3.13) ──", "const slotDitanyaLalu = ")
    s = _hapus_antara(s, "  // v3.13: nama usaha di blok brief yang cuma jenis usaha", "  // GATE TINGKAT 1")
    s = s.replace("TANYA_GALIAN[GALIAN_TERBUKA]", "TANYA_GALIAN[GALIAN_KOLOM]")
    s = _hapus_antara(s, "// ── Minta bicara dengan Steven dalam bahasa chat (2026-09-23, v3.13) ──", "const mintaBicara = ")
    s = _hapus_antara(s, "// v3.13 (uji live 2026-09-23 14:05)", "const NIAT_BICARA = ")
    s = _hapus_antara(s, "// v3.13: + tawaran menyambungkan", "const TAWARAN_DISKUSI = ")
    s = s.replace(_n1, _n0, 1).replace(_t1, _t0, 1)
    s = s.replace("                  || SETUJU_DISKUSI\n                  || mintaSteven;\n", "                  || SETUJU_DISKUSI;\n", 1)
    return s.replace("ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+gema' : 'gema';", "ringkasAlasan = 'gema';", 1)


cek("R5c Process All di luar blok penangkap: selain jaring HARGA, gerbang bicara, HANDOVER, NIAT/TAWARAN & alasan "
    "gema - identik dengan v3.12", _pulihkan_pa(_pa1) == _luar(_pa0))
cek("R5d NIAT_BICARA v3.13 = v3.12 + satu alternatif di belakang (tidak ada yang dihapus)",
    _n1.startswith(_n0[:-1] + "|") and _n1.endswith("stev/"))
cek("R7c Rakit Konteks di luar blok penangkap: hanya salinan NIAT_BICARA yang berubah",
    _luar(_rk1).replace(_n1, _n0, 1) == _luar(_rk0) and _rk1.count(_n1) == 1)
_MB_BARU = ("    // v3.13: sesudah deck terkirim, notif hanya kalau ada yang baru (lihat updateSesudahDeck).\n"
            "    deck_layak: updateSesudahDeck ? berubah.length > 0\n"
            "      : (pa.deckLayak === true || pa.deckDiminta === true\n"
            "         || (pa.isDeckRequest === true && (pertamaKali || bertambah))),\n"
            "    notif_text: updateSesudahDeck ? notif_update : notif_text,\n")
_MB_LAMA = ("    deck_layak: pa.deckLayak === true || pa.deckDiminta === true\n"
            "                || (pa.isDeckRequest === true && (pertamaKali || bertambah)),\n"
            "    notif_text,\n")
cek("R13c Merge Brief: selain blok 'sesudah deck terkirim' + gerbang notif - identik dengan v3.12",
    _hapus_antara(_mb1, "// ── Sesudah deck terkirim (2026-09-23, v3.13) ──", "// ── Kesiapan deck ──")
    .replace(_MB_BARU, _MB_LAMA, 1) == _mb0)
_i0, _i1 = _pr0.index("const askingPrice"), _pr1.index("// ── JAWABAN ATAS PERTANYAANKU")
cek("R12c Preprocess: bagian sebelum gerbang harga tidak berubah (deteksi CERITA/MILIK/TANYA_HARGA_KITA utuh)",
    _pr0[:_i0] == _pr1[:_i1])
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):
                   s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
cek("R6  detektor galian IDENTIK di dua node dan tidak berubah dari v3.12",
    _det(_pa1) == _det(_rk1) == _det(_pa0) == _det(_rk0))
for _k in ("const matikanBot = isTalkToAdmin && mintaBicara;", "const TAWARAN_DISKUSI =", "const NIAT_BICARA =",
           "const mintaDeck =", "last_bot_reply: cleanOutput,", "const LEWATI_RINGKAS =", "const PROSPEK_BERTANYA ="):
    cek("R6b baris kunci v3.12 utuh: %s" % _k[:40], _pa1.count(_k) == 1 and _pa0.count(_k) == 1)

# ---- system prompt ---------------------------------------------------------------
_sp0 = _NL["AI Agent"]["parameters"]["options"]["systemMessage"]
_bag = lambda s: {b.split("\n", 1)[0]: b for b in ("\n" + s).split("\n# ")[1:]}
_b0, _b1 = _bag(_sp0), _bag(_sp)
cek("R8  urutan & nama heading prompt tetap", list(_b0) == list(_b1), str(list(_b1)))
_ubah = sorted(h for h in _b0 if _b0[h] != _b1.get(h))
cek("R8b hanya # HARGA dan # TAG yang berubah", _ubah == ["HARGA", "TAG"], str(_ubah))
_TAMBAH_TAG = ('  Dia sudah minta, jadi langsung sambungkan — jangan bertanya lagi "mau aku sambungkan?".\n'
               '  Permintaan yang ditulis singkat ("kpn bs ngmng sm steven?") sama artinya.\n')
cek("R8f # TAG = versi v3.12 + tepat dua baris itu", _b1["TAG"].replace(_TAMBAH_TAG, "", 1) == _b0["TAG"]
    and _b1["TAG"].count(_TAMBAH_TAG) == 1)
_TAMBAH = ("Sama halnya waktu dia menceritakan alur penjualannya (“harga dulu, terus kalau cocok baru\n"
           "transfer”): itu jawaban soal alurnya — jangan menyinggung harga VIRA sama sekali, dan jangan\n"
           "mengomentari bahwa itu bukan pertanyaan harga.\n")
cek("R8c # HARGA = versi v3.12 + tepat tiga baris itu", _b1["HARGA"].replace(_TAMBAH, "", 1) == _b0["HARGA"]
    and _b1["HARGA"].count(_TAMBAH) == 1)
cek("R8d angka harga di prompt tidak berubah",
    _re.findall(r"\d[\d.]*", _sp) == _re.findall(r"\d[\d.]*", _sp0))
cek("R8e tujuh ekspresi {{ }} tetap utuh", len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 7)
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R9  AI Agent: selain systemMessage identik", _pl == _pb)
cek("R10 DeepSeek Personal Chat & Simple Memory tidak disentuh (temperature 0.7, maxTokens, window)",
    NODES["DeepSeek Personal Chat"] == _NL["DeepSeek Personal Chat"] and NODES["Simple Memory"] == _NL["Simple Memory"]
    and NODES["DeepSeek Personal Chat"]["parameters"]["options"].get("temperature") == 0.7)
cek("R11 cermin prompt .md sama persis dengan systemMessage",
    io.open(os.path.join(DIR, "2026-09-23-system-prompt-VIRA-Personal-v3.13.md"),
            encoding="utf-8").read() == (_sp[1:] if _sp.startswith("=") else _sp))



# ===========================================================================
print()
print("=" * 72)
print("RINGKASAN UAT")'''
ganti_blok('bagian("R. BEDAH REGRESI v3.12 vs v3.11', 'print("RINGKASAN UAT")', SEKSI_R)

# --- 5. daftar UAT manual untuk v3.13 --------------------------------------
_i = teks.index("for i, langkah in enumerate([")
_j = teks.index("], 1):", _i)
teks = teks[:_i] + r'''for i, langkah in enumerate([
    "DEPLOY — di workflow 'VIRA Personal — Main' yang live, ganti isinya dengan 2026-09-23-VIRA-Personal-Main-v3.13.json (ID tetap). Tidak ada kolom/node baru.",
    "RESET — hapus baris STATS nomor uji dulu.",
    "ULANG UJI REHAN — 'Halo VIRA, aku lihat website-nya...' lalu 'rehan' + 'usahaku sewa raket padel'. VIRA menanyakan NAMA usahanya (bukan bidangnya). STATS: nama_lengkap=Rehan, industri=sewa raket padel, nama_bisnis KOSONG.",
    "Jawab 'persewaan aja sih' -> nama_bisnis tetap kosong.",
    "Sampai VIRA menanyakan langkah dari chat sampai jadi sewa, jawab 'harga dulu, trs klo udah aman baru ke payment'. Balasan TANPA Basic/Premium/Rp dan TANPA 'bukan nanya harga'. Lalu 'okee' -> VIRA TIDAK menanyakan langkah itu lagi.",
    "Tanya 'harganya berapa kak?' -> kisaran Basic/Premium TETAP disebut lengkap.",
    "Tab EVENTS: balasan yang dipangkas tercatat sebagai RINGKAS (alasan 'harga' kalau harga yang dibuang).",
    "Sampai tawaran deck lalu jawab 'boleh': notif brief LENGKAP tetap masuk ke Steven dan REQUESTS terisi.",
    "Kirim decknya (kirim_deck.py), lalu dari nomor uji jawab 'basic deh': WA admin menerima notif SINGKAT 'UPDATE PROSPEK — deck sudah terkirim' (Minat paket: Basic), BUKAN 'BRIEF DECK ... DECK SIAP DIGENERATE'.",
    "Kirim 'kpn bs ngmng sm steven?': VIRA membalas 'Siap kak, sudah aku sambungkan ke Steven...' (TANPA 'mau aku sambungkan?'), WA admin menerima notif PROSPEK MINTA DISAMBUNGKAN, STATS bot_mode = OFF, pesan berikutnya tidak dibalas VIRA. Kembalikan bot_mode = ON sesudahnya.",
    "Hapus workflow 'VIRA Eval — Balasan (sementara)' sesudah uji selesai.",
''' + teks[_j:]

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(teks)
print("OK ->", os.path.basename(DST))
