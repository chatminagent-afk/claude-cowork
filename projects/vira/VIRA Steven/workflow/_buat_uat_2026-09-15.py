# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-15.py - turunkan _uat_2026-09-15.py dari harness _uat_2026-09-14.py.

Harness v3.8 diarahkan ulang ke v3.9. Semua assertion A-Q ikut jalan sebagai regresi,
dengan tiga baris tabel O1 disesuaikan ke jendela giliran v3.9 (dilebarkan satu).
Seksi R lama (bedah v3.8 vs v3.6) diganti:

  S. INSIDEN 2026-09-15 - nama tidak dipakai menyapa, "Dengan Aldi", pertanyaan dijawab dulu
  R. BEDAH REGRESI v3.9 vs v3.8 - 86 node identik; di 3 node yang diubah hanya baris sasaran

Jalankan: python _buat_uat_2026-09-15.py   (lalu: python _uat_2026-09-15.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-14.py")
DST = os.path.join(DIR, "_uat_2026-09-15.py")

with io.open(SRC, encoding="utf-8") as f:
    teks = f.read()


def ganti(lama, baru):
    global teks
    assert teks.count(lama) == 1, "anchor tidak tunggal (%d): %r" % (teks.count(lama), lama[:90])
    teks = teks.replace(lama, baru, 1)


# --- 1. arahkan ke v3.9 --------------------------------------------------
ganti('WF = os.path.join(DIR, "2026-09-14-VIRA-Personal-Main-v3.8.json")',
      'WF = os.path.join(DIR, "2026-09-15-VIRA-Personal-Main-v3.9.json")')
ganti("_uat_2026-09-14.py — UAT perilaku untuk 2026-09-14-VIRA-Personal-Main-v3.8.json.\n\n"
      "Diturunkan dari _uat_2026-09-07.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-14.py, lalu jalankan ulang). Seluruh assertion lama ikut jalan\n"
      "sebagai regresi; seksi N-R baru untuk pengisian kolom STATS 2026-09-14.",
      "_uat_2026-09-15.py — UAT perilaku untuk 2026-09-15-VIRA-Personal-Main-v3.9.json.\n\n"
      "Diturunkan dari _uat_2026-09-14.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-15.py, lalu jalankan ulang). Seksi A-Q ikut jalan sebagai regresi;\n"
      "seksi S baru untuk insiden 2026-09-15, seksi R membedah v3.9 terhadap v3.8.")
ganti("Jalankan: python _uat_2026-09-14.py", "Jalankan: python _uat_2026-09-15.py")

# --- 2. jendela giliran v3.9 (dilebarkan satu) ---------------------------
ganti('({"greeting_sent": "Y", "Counter": "4"}, "masalah terbesarnya", "giliran 5 -> jendela bidang usaha habis, lanjut masalah"),',
      '({"greeting_sent": "Y", "Counter": "4"}, "bidang usahanya", "giliran 5 -> bidang usaha masih dalam jendela (v3.9: 2-5)"),\n'
      '        ({"greeting_sent": "Y", "Counter": "5"}, "masalah terbesarnya", "giliran 6 -> jendela bidang usaha habis, lanjut masalah"),')
ganti('({"greeting_sent": "Y", "Counter": "6", "industri": "sipil"}, None, "giliran 7 -> jendela masalah habis"),',
      '({"greeting_sent": "Y", "Counter": "7", "industri": "sipil"}, None, "giliran 8 -> jendela masalah habis (v3.9: 2-7)"),')
ganti('({"greeting_sent": "Y", "Counter": "8", "industri": "sipil", "masalah_utama": "x"}, None,\n'
      '         "giliran 9 -> jendela jumlah chat habis"),',
      '({"greeting_sent": "Y", "Counter": "9", "industri": "sipil", "masalah_utama": "x"}, None,\n'
      '         "giliran 10 -> jendela jumlah chat habis (v3.9: 3-9)"),')

# --- 3. kasus nama dari insiden ------------------------------------------
ganti(r'("Budi\nmau tanya harga vira", "Budi"), ("ehm, Budi kak", "Budi")]:',
      r'("Budi\nmau tanya harga vira", "Budi"), ("ehm, Budi kak", "Budi"),'
      '\n'
      r'                     ("dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?", "Aldi"),'
      '\n'
      r'                     ("ini dengan aldi", "Aldi"), ("saya dengan Rina", "Rina"), ("sama budi kak", "Budi")]:')

# --- 4. seksi S baru + R baru, menggantikan R lama ------------------------
BARU = r'''# ===========================================================================
bagian("S. INSIDEN 2026-09-15 — nama tidak dipakai menyapa, pertanyaan dijawab dulu")
# ===========================================================================
_sp = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]
cek("S1  GAYA tidak lagi menyuruh memakai nama", "setelah itu pakai namanya" not in _sp)
cek("S1b GAYA: nama TIDAK PERNAH dipakai di balasan",
    "Namanya hanya dicatat untuk Steven dan TIDAK PERNAH dipakai di balasan" in _sp)
cek("S2  bagian NAMA tidak lagi menyuruh 'panggil dia dengan nama itu'",
    "panggil dia dengan nama itu" not in _sp and "BUKAN untuk menyapa" in _sp)
cek("S3  spek [FACTS] tidak lagi 'memanggilnya dengan nama itu'",
    "memanggilnya dengan nama itu" not in _sp and "Nama itu tidak pernah dipakai di balasan" in _sp)
cek("S4  tidak ada 'kamu' di luar kutipan larangan",
    not _re.findall(r'(?<!")\bkamu\b(?!")', _sp), str(_re.findall(r'.{20}\bkamu\b.{20}', _sp)))

BALASAN_INSIDEN = ("Halo Aldi, senang kenal sama kamu. Jadi Aldi mau tanya soal AI customer service "
                   "buat bisnis, usahanya di bidang apa kak?")
d = satu(proses(BALASAN_INSIDEN, pesan_user="dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?",
                prev_row={"last_bot_reply": PERKENALAN}))
cek("S5  insiden: nama tersimpan 'Aldi', bukan 'Dengan Aldi'", d and d["nama_lengkap_merged"] == "Aldi",
    str(d and d.get("nama_lengkap_merged")))
cek("S5b insiden: 'Aldi' dihapus dari balasan yang terkirim",
    d and "aldi" not in d["cleanOutput"].lower() and d["namaDihapus"] is True, str(d and d.get("cleanOutput")))
cek("S5c insiden: sapaan jadi 'Halo kak', kalimat tetap utuh",
    d and d["cleanOutput"].startswith("Halo kak,") and "Jadi kakak mau tanya" in d["cleanOutput"],
    str(d and d.get("cleanOutput")))
cek("S5d last_bot_reply = teks yang sudah dibersihkan", d and d["last_bot_reply"] == d["cleanOutput"])
cek("S5e penghapusan nama bukan penggantian balasan (replyOverridden tetap false)",
    d and d["replyOverridden"] is False)

for ai, nama, prev_extra, harap, judul in [
        ("Salam kenal kak Aldi.", "Aldi", {}, "Salam kenal kak.", "'kak Aldi' -> 'kak'"),
        ("Makasih Aldi, nanti aku teruskan ke Steven.", "Aldi", {}, "Makasih kak, nanti aku teruskan ke Steven.",
         "'Makasih Aldi' -> 'Makasih kak'"),
        ('Salam kenal kak Budi Santoso.\n[FACTS nama="Budi Santoso"]', "", {}, "Salam kenal kak.",
         "nama dari [FACTS] giliran ini ikut dihapus"),
        ("Oke Pak Budi, siap.", "Budi", {}, "Oke Pak, siap.", "'Pak Budi' -> 'Pak'"),
        ("Deck buat Andi Bakery sudah aku teruskan ke Steven.", "Andi", {"nama_bisnis": "Andi Bakery"},
         "Deck buat Andi Bakery sudah aku teruskan ke Steven.", "nama yang juga bagian nama usaha TIDAK disentuh"),
        ("Tampilannya jadi indah dan rapi kak.", "Indah", {}, "Tampilannya jadi indah dan rapi kak.",
         "nama = kata umum ('Indah') TIDAK disentuh"),
        ("Oke kak Al, siap.", "Al", {}, "Oke kak Al, siap.", "nama < 3 huruf TIDAK disentuh"),
        ("Pak Aldianto sudah aku catat.", "Aldi", {}, "Pak Aldianto sudah aku catat.",
         "kata yang hanya MEMUAT nama tidak disentuh"),
        ("Halo kak, ada yang bisa aku bantu?", "", {}, "Halo kak, ada yang bisa aku bantu?", "tanpa nama -> tidak berubah")]:
    pr = {"nama_lengkap": nama}
    pr.update(prev_extra)
    d = satu(proses(ai, pesan_user="oke", prev_row=pr))
    cek("S6  %s" % judul, d and d["cleanOutput"] == harap, str(d and d.get("cleanOutput")))


def rakit2(user_row, pesan):
    kat = {"faq": [], "program": [], "links": LINKS, "about": []}
    return satu(jalan("Rakit Konteks", nodes={
        "Parse Config": [item(config=cfg())],
        "Resolve User Row": [item(userRow=user_row, lead_source_db="Organik")],
        "Preprocess - Context Detection": [item(actualUserMessage=pesan)],
    }, inp=[item(katalog=kat, faq_context="")]))


def galian2(baris, pesan):
    d = rakit2(baris, pesan)
    m = _re.search(r"^galian_berikutnya: (.*)$", d["prospect_context"], _re.M) if d else None
    return (m.group(1) if m else None), d


g, d = galian2({"greeting_sent": "Y", "Counter": "1", "nama_lengkap": "Aldi"},
               "dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?")
cek("S7  insiden: pesan berisi pertanyaan -> galian DITUNDA (pertanyaan dijawab dulu)", g is None, str(g))
cek("S7b baris panggilan: kak muncul begitu nama tersimpan",
    "panggilan: kak — nama_lengkap hanya catatan untuk Steven" in d["prospect_context"], d["prospect_context"])
for pesan in ["bisa integrasi ke IG?", "harganya berapa", "gimana cara kerjanya", "kapan bisa mulai"]:
    g, _ = galian2({"greeting_sent": "Y", "Counter": "1"}, pesan)
    cek("S8  '%s' (bertanya) -> galian ditunda" % pesan, g is None, str(g))
for pesan in ["dengan aldi", "oh gitu oke kak", "sip, masuk akal"]:
    g, _ = galian2({"greeting_sent": "Y", "Counter": "1"}, pesan)
    cek("S9  '%s' (tidak bertanya) -> galian bidang usaha jalan" % pesan,
        g is not None and g.startswith("bidang usahanya"), str(g))
g, _ = galian2({"greeting_sent": ""}, "halo, harganya berapa?")
cek("S10 pesan perkenalan yang bertanya tetap menanyakan nama", g is not None and g.startswith("namanya"), str(g))
g, d = galian2({"greeting_sent": "Y", "Counter": "1"}, "oke")
cek("S11 tanpa nama tersimpan -> tidak ada baris panggilan", "panggilan:" not in d["prospect_context"])
cek("S11b IS_NEW_USER tetap baris terakhir", d["prospect_context"].rstrip().endswith("IS_NEW_USER: false"))


# ===========================================================================
bagian("R. BEDAH REGRESI v3.9 vs v3.8 — yang tidak disebut patch tidak tersentuh")
# ===========================================================================
import difflib as _dl
with open(os.path.join(DIR, "2026-09-14-VIRA-Personal-Main-v3.8.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Process All", "Rakit Konteks"}

cek("R1  jumlah & nama node sama dengan v3.8", set(_NL) == set(NODES) and len(wf["nodes"]) == 89)
cek("R2  koneksi identik", json.dumps(_lama["connections"], sort_keys=True) == json.dumps(CONNS, sort_keys=True))
_beda = sorted(n for n in NODES if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  86 node lain identik byte per byte dengan v3.8", not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))
cek("R4b settings workflow tetap", _lama.get("settings") == wf.get("settings"))


def _hunk(a, b):
    la, lb = a.split("\n"), b.split("\n")
    return [(t, la[i1:i2], lb[j1:j2]) for t, i1, i2, j1, j2
            in _dl.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes() if t != "equal"]


_h = _hunk(_NL["Process All"]["parameters"]["jsCode"], NODES["Process All"]["parameters"]["jsCode"])
_ganti = sorted(x.strip()[:40] for t, o, _ in _h if t != "insert" for x in o)
cek("R5  Process All: selain sisipan, hanya 2 baris penangkap nama yang diganti",
    len(_ganti) == 2 and any(x.startswith("if (/^(aku|saya") for x in _ganti)
    and any(x.startswith(".replace(/^(nama") for x in _ganti),
    str(_ganti))
_h = _hunk(_NL["Rakit Konteks"]["parameters"]["jsCode"], NODES["Rakit Konteks"]["parameters"]["jsCode"])
_ganti = [x.strip() for t, o, _ in _h if t != "insert" for x in o]
cek("R6  Rakit Konteks: selain sisipan, hanya 3 baris jendela giliran yang diganti",
    len(_ganti) == 3 and all(x.startswith("boleh: () => !pesanPerkenalan") for x in _ganti), str(_ganti))
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
cek("R7  detektor galian tetap IDENTIK di Process All dan Rakit Konteks, dan tidak berubah dari v3.8",
    _det(NODES["Process All"]["parameters"]["jsCode"]) == _det(NODES["Rakit Konteks"]["parameters"]["jsCode"])
    == _det(_NL["Process All"]["parameters"]["jsCode"]))

_h = _hunk(_NL["AI Agent"]["parameters"]["options"]["systemMessage"], _sp)
_dihapus = [x for _, o, _ in _h for x in o]
_boleh = {
    'namanya VIRA. Jadi kalau kamu penasaran hasilnya kayak apa, kamu lagi ngobrol sama contohnya sekarang."',
    'Begitu dia menyebut namanya — di pesan mana pun, ditanya atau tidak — catat lewat `[FACTS nama="..."]`,',
    'panggil dia dengan nama itu, dan jangan pernah menanyakannya lagi.',
    'Panggil lawan bicara "kak", kecuali dia menyebutkan namanya — setelah itu pakai namanya.',
    'juga yang akan kujaga kalau kamu jadi klien.',
    '  `nama` adalah nama orangnya, bukan nama bisnisnya — pakai tag ini begitu dia menyebutkan namanya,',
    '  supaya aku bisa memanggilnya dengan nama itu di percakapan berikutnya.',
}
cek("R8  system prompt: baris lama yang diganti hanya 7 baris sasaran patch",
    set(_dihapus) <= _boleh, str([x for x in _dihapus if x not in _boleh]))
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R9  AI Agent: selain systemMessage identik", _pl == _pb)


'''

AWAL_R = ('# ===========================================================================\n'
          'bagian("R. BEDAH REGRESI — yang tidak disebut patch tidak tersentuh")')
ANCHOR = ('# ===========================================================================\n'
          'print()\n'
          'print("=" * 72)\n'
          'print("RINGKASAN UAT")')
assert teks.count(AWAL_R) == 1 and teks.count(ANCHOR) == 1
i, j = teks.index(AWAL_R), teks.index(ANCHOR)
teks = teks[:i] + BARU + teks[j:]

# --- 5. checklist UAT manual ---------------------------------------------
ganti('    "Import 2026-09-14-VIRA-Personal-Main-v3.8.json, matikan v3.6 dulu, lalu aktifkan v3.8. Tidak ada kolom baru.",\n',
      '    "Import 2026-09-15-VIRA-Personal-Main-v3.9.json, matikan v3.8 dulu, lalu aktifkan v3.9. Tidak ada kolom baru.",\n')
ganti('    "NAMA — jawab \'Budi\': VIRA memanggil \'kak Budi\'; STATS.nama_lengkap = Budi.",\n',
      '    "NAMA — ulang insiden 2026-09-15: jawab \'dengan aldi\' + \'mo ty ini bs apa aj\' + \'apa sm ky chatbot biasa?\'. "\n'
      '    "VIRA menyapa \'kak\' (TANPA nama), MENJAWAB pertanyaannya, dan tidak menanyakan bidang usaha di balasan itu. "\n'
      '    "STATS.nama_lengkap = Aldi.",\n')

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(teks)

print("DST : %s  (%d baris)" % (os.path.basename(DST), teks.count("\n") + 1))
