# -*- coding: utf-8 -*-
"""
_buat_uat_2026-09-22.py - turunkan _uat_2026-09-22.py dari harness _uat_2026-09-18.py.

Harness v3.10 diarahkan ulang ke v3.11. Seksi A-Q, S dan T ikut jalan sebagai regresi
tanpa satu pun penyesuaian: patch 2026-09-22 murni menambah, tidak mengubah perilaku lama.

Seksi baru:
  U. DECK TERKIRIM - blok deck_context di Rakit Konteks, gerbang persetujuan diskusi
     di Process All, dan bagian # DECK di system prompt.
Seksi R ditulis ulang: membedah v3.11 terhadap v3.10 (bukan lagi terhadap export live),
dan membuktikan patch ini murni sisipan - tidak ada baris v3.10 yang hilang atau diganti
di luar satu baris mintaBicara yang memang disengaja.

Jalankan: python _buat_uat_2026-09-22.py   (lalu: python _uat_2026-09-22.py)
"""
import io
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "_uat_2026-09-18.py")
DST = os.path.join(DIR, "_uat_2026-09-22.py")

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


# --- 1. arahkan ke v3.11 -------------------------------------------------
ganti('WF = os.path.join(DIR, "2026-09-18-VIRA-Personal-Main-v3.10.json")',
      'WF = os.path.join(DIR, "2026-09-22-VIRA-Personal-Main-v3.11.json")')
ganti("_uat_2026-09-18.py — UAT perilaku untuk 2026-09-18-VIRA-Personal-Main-v3.10.json.\n\n"
      "Diturunkan dari _uat_2026-09-15.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-18.py, lalu jalankan ulang). Seksi A-Q dan S ikut jalan sebagai regresi;\n"
      "seksi T baru untuk uji Steven 2026-09-17, seksi R membedah v3.10 terhadap export live.",
      "_uat_2026-09-22.py — UAT perilaku untuk 2026-09-22-VIRA-Personal-Main-v3.11.json.\n\n"
      "Diturunkan dari _uat_2026-09-18.py (jangan diedit manual — ubah generatornya,\n"
      "_buat_uat_2026-09-22.py, lalu jalankan ulang). Seksi A-Q, S dan T ikut jalan sebagai\n"
      "regresi tanpa penyesuaian; seksi U baru untuk patch deck terkirim; seksi R membedah\n"
      "v3.11 terhadap v3.10.")
ganti("Jalankan: python _uat_2026-09-18.py", "Jalankan: python _uat_2026-09-22.py")
ganti('print("UAT PERILAKU — VIRA Personal v3.2 (2026-09-06b)")',
      'print("UAT PERILAKU — VIRA Personal v3.11 (2026-09-22)")')

# --- 2. seksi U (baru), disisipkan sebelum seksi R ------------------------
SEKSI_U = r'''bagian("U. DECK TERKIRIM — deck_context, persetujuan diskusi, bagian # DECK (2026-09-22)")
# ===========================================================================
_HARI = 86400


def deckctx(**baris):
    """prospect/deck context untuk satu baris STATS."""
    b = {"greeting_sent": "Y", "Counter": "5", "industri": "katering",
         "masalah_utama": "chat numpuk", "volume_chat": "30", "nama_bisnis": "Dapur Mama"}
    b.update(baris)
    return rakit(b)


# ---- U1..U9: bentuk blok deck_context -----------------------------------
d = deckctx()
cek("U1  deck_terkirim_ts kosong -> satu baris '(belum pernah dikirim)'",
    d is not None and d["deck_context"] == "(deck belum pernah dikirim ke orang ini)",
    str(d and d.get("deck_context"))[:120])

d = deckctx(deck_terkirim_ts=str(NOW_S))
cek("U2  dikirim hari ini -> 'hari ini'",
    d and d["deck_context"].startswith("Deck-nya SUDAH dikirim") and "hari ini" in d["deck_context"],
    str(d and d["deck_context"].split("\n")[0])[:140])

d = deckctx(deck_terkirim_ts=str(NOW_S - _HARI))
cek("U3  dikirim kemarin -> 'kemarin'", d and "kemarin" in d["deck_context"].split("\n")[0],
    str(d and d["deck_context"].split("\n")[0])[:140])

d = deckctx(deck_terkirim_ts=str(NOW_S - 5 * _HARI))
cek("U4  dikirim 5 hari lalu -> '5 hari lalu'", d and "5 hari lalu" in d["deck_context"].split("\n")[0],
    str(d and d["deck_context"].split("\n")[0])[:140])

d = deckctx(deck_terkirim_ts="2026-09-20 14:30:00")
cek("U5  format WIB manual tetap terbaca sebagai sudah dikirim",
    d and d["deck_context"].startswith("Deck-nya SUDAH dikirim"),
    str(d and d["deck_context"].split("\n")[0])[:140])

for rusak in ("abc", "-", "0", "  ", "belum"):
    d = deckctx(deck_terkirim_ts=rusak)
    cek("U6  nilai tidak terbaca (%r) -> dianggap belum dikirim, node tidak jatuh" % rusak,
        d is not None and d["deck_context"] == "(deck belum pernah dikirim ke orang ini)",
        str(d and d.get("deck_context"))[:80])

d = deckctx(deck_terkirim_ts=str(NOW_S - 2 * _HARI))
_blok = d["deck_context"] if d else ""
cek("U7  blok melarang menyebut harga add-on",
    "add-on tetap TIDAK kusebut" in _blok or "Harga add-on tetap TIDAK" in _blok)
cek("U7b blok melarang mengulang 'decknya sedang disusun'",
    "JANGAN lagi bilang" in _blok and "disusun" in _blok)
cek("U8  blok menyuruh pakai [TALK_TO_ADMIN] kalau mau disambungkan",
    "[TALK_TO_ADMIN]" in _blok)
cek("U8b blok menyuruh pakai [UNKNOWN] untuk isi slide yang tidak diketahui",
    "[UNKNOWN]" in _blok)
cek("U8c blok menyuruh mencatat minat paket lewat [FACTS]",
    "[FACTS minat_paket=" in _blok)
cek("U9  blok TIDAK memuat satu pun angka harga",
    not _re.search(r"3\.000\.000|5\.000\.000|\b999\b|Rp\s*\d", _blok), _blok[:200])

# ---- U10..U12: tidak mengganggu blok lain -------------------------------
for kirim in ("", str(NOW_S - _HARI)):
    d = deckctx(deck_terkirim_ts=kirim)
    cek("U10 deck_context selalu ada di keluaran (deck_terkirim_ts=%r)" % kirim,
        d is not None and isinstance(d.get("deck_context"), str) and d["deck_context"] != "")
    cek("U10b enam blok lama tetap ada (deck_terkirim_ts=%r)" % kirim,
        d is not None and all(k in d for k in ("prospect_context", "brief_context", "about_context",
                                               "program_context", "links_context", "faq_context")))

d0 = deckctx(deck_terkirim_ts="")
d1 = deckctx(deck_terkirim_ts=str(NOW_S - _HARI))
cek("U11 prospect_context tidak berubah karena deck terkirim",
    d0 and d1 and d0["prospect_context"] == d1["prospect_context"])
cek("U11b deck_terkirim_ts tidak bocor ke DATA PROSPEK",
    d1 and "deck_terkirim_ts" not in d1["prospect_context"])

g0, _ = galian(greeting_sent="Y", Counter="1")
g1, _ = galian(greeting_sent="Y", Counter="1", deck_terkirim_ts=str(NOW_S - _HARI))
cek("U12 galian_berikutnya tidak terpengaruh deck_terkirim_ts", g0 == g1, "%r vs %r" % (g0, g1))

# ---- U13..U20: gerbang persetujuan diskusi di Process All ---------------
TAWAR_DISKUSI = ("Kalau mau, aku bisa atur supaya kakak ngobrol langsung sama Steven. Mau aku "
                 "sambungkan?")
TUTUP_DECK = ("Sudah aku teruskan briefnya ke Steven, dia sendiri yang akan menyusun decknya dan "
              "menghubungi kakak langsung. Sambil menunggu, kakak bebas tanya apa aja ke aku.")


def diskusi(ai_output, pesan_user, balasan_lalu):
    return satu(proses(ai_output, pesan_user=pesan_user,
                       prev_row={"last_bot_reply": balasan_lalu, "last_bot_reply_ts": NOW_S - 60,
                                 "deck_requested": "Y"}))


d = diskusi("[TALK_TO_ADMIN]\nSiap kak, Steven yang akan menghubungi kakak langsung.",
            "boleh", TAWAR_DISKUSI)
cek("U13 tawaran diskusi + 'boleh' + tag -> bot dimatikan", d and d["matikanBot"] is True,
    str(d and d.get("matikanBot")))

d = diskusi("Siap kak, nanti Steven yang menghubungi kakak langsung ya.", "boleh", TAWAR_DISKUSI)
cek("U14 tawaran diskusi + 'boleh' TANPA tag -> handover tetap nyala (promosi deterministik)",
    d and d["matikanBot"] is True, str(d and d.get("matikanBot")))

d = diskusi("Siap kak, ditunggu ya.", "boleh", TUTUP_DECK)
cek("U15 kalimat penutup deck + 'boleh' -> bot TIDAK dimatikan",
    d and d["matikanBot"] is False, str(d and d.get("matikanBot")))

d = diskusi(DECK_BLOK + "Sudah aku teruskan ke Steven ya kak.", "boleh",
            "Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?")
cek("U16 tawaran DECK + 'boleh' -> bot tetap hidup dan jalur deck jalan",
    d and d["matikanBot"] is False and d["isDeckRequest"] is True,
    str(d and (d.get("matikanBot"), d.get("isDeckRequest"))))

d = diskusi("Aku jelasin dulu ya kak.", "boleh tapi nanti dulu ya, aku mau baca decknya lagi "
            "sampai tuntas soalnya belum sempat kebuka semua", TAWAR_DISKUSI)
cek("U17 tawaran diskusi + kalimat panjang (bukan persetujuan pendek) -> bot tetap hidup",
    d and d["matikanBot"] is False, str(d and d.get("matikanBot")))

d = diskusi("Halo kak.", "boleh", "")
cek("U18 tanpa balasan terakhir -> perilaku lama, bot tetap hidup",
    d and d["matikanBot"] is False, str(d and d.get("matikanBot")))

d = diskusi("[TALK_TO_ADMIN]\nSiap kak.", "mau ngobrol langsung sama Steven dong", "")
cek("U19 REGRESI: NIAT_BICARA eksplisit tetap mematikan bot",
    d and d["matikanBot"] is True, str(d and d.get("matikanBot")))

for pesan, harap in [("boleh", True), ("mau", True), ("oke", True), ("iya", True),
                     ("silakan", True), ("gas", True),
                     ("hmm", False), ("nanti aja", False), ("kenapa emang?", False)]:
    d = diskusi("Siap kak.", pesan, TAWAR_DISKUSI)
    cek("U20 '%s' atas tawaran diskusi -> handover %s" % (pesan, "nyala" if harap else "mati"),
        d and d["matikanBot"] is harap, str(d and d.get("matikanBot")))

# ---- U21..U24: bagian # DECK di system prompt ---------------------------
cek("U21 system prompt punya bagian '# DECK'", "\n# DECK (status pitch deck untuk orang ini)\n" in _sp)
cek("U22 bagian itu memuat slot {{ $json.deck_context }}", "{{ $json.deck_context }}" in _sp)
cek("U23 '# DECK' berada tepat sebelum '# BRIEF TERISI'",
    _sp.index("# DECK (status pitch deck") < _sp.index("# BRIEF TERISI"))
_slot = _re.findall(r"\{\{ \$json\.(\w+) \}\}", _sp)
cek("U24 tujuh slot data, tanpa duplikat",
    len(_slot) == 7 and len(set(_slot)) == 7 and "deck_context" in _slot, str(_slot))


# ===========================================================================
'''

ganti('bagian("R. BEDAH REGRESI v3.10 vs export live', SEKSI_U
      + 'bagian("R. BEDAH REGRESI v3.10 vs export live')

# --- 3. seksi R ditulis ulang: v3.11 vs v3.10 ----------------------------
SEKSI_R = r'''bagian("R. BEDAH REGRESI v3.11 vs v3.10 — patch ini murni sisipan")
# ===========================================================================
import difflib as _dl
with open(os.path.join(DIR, "2026-09-18-VIRA-Personal-Main-v3.10.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Process All", "Rakit Konteks"}

cek("R1  jumlah & nama node sama dengan v3.10", set(_NL) == set(NODES) and len(wf["nodes"]) == 89)
cek("R2  koneksi identik", json.dumps(_lama["connections"], sort_keys=True) == json.dumps(CONNS, sort_keys=True))
_beda = sorted(n for n in NODES if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  86 node lain identik byte per byte dengan v3.10", not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))
cek("R4b settings workflow tetap", _lama.get("settings") == wf.get("settings"))
cek("R4c kredensial tiap node tetap",
    all(NODES[n].get("credentials") == _NL[n].get("credentials") for n in NODES))
cek("R4d webhookId tiap node tetap",
    all(NODES[n].get("webhookId") == _NL[n].get("webhookId") for n in NODES))


def _opcodes(a, b):
    return _dl.SequenceMatcher(None, a.split("\n"), b.split("\n"), autojunk=False).get_opcodes()


def _bukan_sisipan(a, b):
    """Opcode selain equal/insert = ada baris lama yang diganti atau dibuang."""
    return [t for t, i1, i2, j1, j2 in _opcodes(a, b) if t not in ("equal", "insert")]


def _sisipan(a, b):
    lb = b.split("\n")
    return ["\n".join(lb[j1:j2]) for t, i1, i2, j1, j2 in _opcodes(a, b) if t == "insert"]


# ---- Rakit Konteks: sisipan murni ---------------------------------------
_rk0, _rk1 = _NL["Rakit Konteks"]["parameters"]["jsCode"], NODES["Rakit Konteks"]["parameters"]["jsCode"]
_x = _bukan_sisipan(_rk0, _rk1)
cek("R5  Rakit Konteks: tidak ada baris v3.10 yang diganti/dibuang", not _x, str(_x))
_ins = _sisipan(_rk0, _rk1)
cek("R5b Rakit Konteks: tepat 2 sisipan (blok deck_context + baris return)", len(_ins) == 2, str(len(_ins)))
cek("R5c sisipan 1 = blok deck_context", _ins and "// ---------- 7. deck_context ----------" in _ins[0])
cek("R5d sisipan 2 = deck_context di objek return",
    len(_ins) > 1 and _ins[1].strip() == "deck_context,")
cek("R5e enam blok lama masih dirakit di node yang sama",
    all(("const " + k) in _rk1 or (k + " =") in _rk1 for k in
        ("prospect_context", "about_context", "program_context", "links_context",
         "faq_context", "brief_context")))

# ---- Process All: satu baris mintaBicara memang diganti -----------------
_pa0, _pa1 = _NL["Process All"]["parameters"]["jsCode"], NODES["Process All"]["parameters"]["jsCode"]
_pa0n = _pa0.replace(
    "const mintaBicara = (preprocess && preprocess.wantsHuman === true) || NIAT_BICARA.test(PESAN_USER);",
    "const mintaBicara = (preprocess && preprocess.wantsHuman === true)\n"
    "                  || NIAT_BICARA.test(PESAN_USER)\n"
    "                  || SETUJU_DISKUSI;")
cek("R6  Process All: baris mintaBicara lama ada tepat sekali di v3.10", _pa0n != _pa0)
_x = _bukan_sisipan(_pa0n, _pa1)
cek("R6b Process All: selain baris mintaBicara, tidak ada yang diganti/dibuang", not _x, str(_x))
_ins = _sisipan(_pa0n, _pa1)
cek("R6c Process All: tepat 1 sisipan", len(_ins) == 1, str(len(_ins)))
cek("R6d sisipan = gerbang TAWARAN_DISKUSI", _ins and "const TAWARAN_DISKUSI =" in _ins[0])
cek("R6e NIAT_BICARA tidak diubah",
    _re.search(r"const NIAT_BICARA = .*", _pa0).group(0) == _re.search(r"const NIAT_BICARA = .*", _pa1).group(0))
cek("R6f SETUJU_PENDEK dipakai ulang, bukan disalin",
    _pa1.count("const SETUJU_PENDEK") == 1)
cek("R6g matikanBot tetap butuh isTalkToAdmin",
    "const matikanBot = isTalkToAdmin && mintaBicara;" in _pa1)
cek("R6h persetujuan deck tetap membatalkan jalur diskusi", "&& !mintaDeck;" in _pa1)
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):
                   s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
cek("R7  detektor galian tetap IDENTIK di Process All dan Rakit Konteks", _det(_pa1) == _det(_rk1))
cek("R7b detektor galian tidak berubah dari v3.10", _det(_pa1) == _det(_pa0))

# ---- system prompt: sisipan murni ---------------------------------------
_sp0 = _NL["AI Agent"]["parameters"]["options"]["systemMessage"]
_x = _bukan_sisipan(_sp0, _sp)
cek("R8  system prompt: tidak ada baris v3.10 yang diganti/dibuang", not _x, str(_x))
_ins = _sisipan(_sp0, _sp)
cek("R8b system prompt: tepat 1 sisipan", len(_ins) == 1, str(len(_ins)))
cek("R8c sisipan = bagian # DECK", _ins and "# DECK (status pitch deck untuk orang ini)" in _ins[0])
cek("R8d sisipan tidak menambah aturan harga baru",
    _ins and not _re.search(r"3\.000\.000|5\.000\.000|\b999\b", _ins[0]))
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R9  AI Agent: selain systemMessage identik", _pl == _pb)
cek("R10 DeepSeek Personal Chat: temperature tetap 0.7 (panjang diatur lewat prompt, bukan parameter)",
    NODES["DeepSeek Personal Chat"]["parameters"]["options"].get("temperature") == 0.7)
cek("R11 cermin prompt .md sama persis dengan systemMessage",
    io.open(os.path.join(DIR, "2026-09-22-system-prompt-VIRA-Personal-v3.11.md"),
            encoding="utf-8").read() == (_sp[1:] if _sp.startswith("=") else _sp))
'''

ganti_blok('bagian("R. BEDAH REGRESI v3.10 vs export live',
           'NODES["DeepSeek Personal Chat"]["parameters"]["options"].get("temperature") == 0.7)',
           SEKSI_R)

# `io` dipakai seksi R11; harness aslinya tidak mengimpornya.
ganti("import json\nimport os\nimport sys\n", "import io\nimport json\nimport os\nimport sys\n")

# --- 4. tambah langkah UAT manual ----------------------------------------
ganti('    "BUDGET/PAKET — sepanjang uji, VIRA tidak pernah menanyakan anggaran atau Basic/Premium.",\n',
      '    "BUDGET/PAKET — sepanjang uji, VIRA tidak pernah menanyakan anggaran atau Basic/Premium.",\n'
      '    "KOLOM BARU — tambahkan kolom deck_terkirim_ts di tab STATS, PALING KANAN (jadi kolom ke-33). '
      'Jangan menyisipkannya di tengah.",\n'
      '    "SKRIP — jalankan `python vira_sheet.py 628xxx` di folder deck: harus menyebut REQUESTS terbaca. '
      'Lalu uji cari_stats untuk nomor yang TIDAK ada: harus error, bukan mengembalikan baris lain.",\n'
      '    "KIRIM KE STEVEN — `kirim_deck.py --wa <uji> --ke-admin --kirim`: STATS.deck_terkirim_ts harus TETAP KOSONG.",\n'
      '    "KIRIM KE KLIEN — `kirim_deck.py --wa <nomor Steven sendiri> --kirim`: keluaran memuat baris '
      '`SHEET : STATS.deck_terkirim_ts = <epoch>`, dan kolomnya benar-benar terisi di baris yang benar.",\n'
      '    "CAPTION — caption yang sampai di WhatsApp memuat permintaan review + Basic/Premium + tawaran diskusi, '
      'dan TIDAK memuat karakter aneh. Untuk baris REQUESTS yang kolom `nama`-nya kosong, caption harus berbunyi '
      '\\"Halo kak, salam kenal\\" — bukan \\"Halo kak salam kenal\\".",\n'
      '    "SESUDAH DECK — chat dari nomor itu: VIRA TIDAK BOLEH lagi bilang decknya sedang disusun atau briefnya '
      'baru diteruskan. Dia harus bisa menyebut isi decknya garis besar.",\n'
      '    "SESUDAH DECK (harga) — tanya \\"basic sama premium bedanya apa?\\": VIRA boleh menyebut kisaran dan '
      'mengarahkan angka final ke Steven. Harga ADD-ON tetap tidak boleh disebut.",\n'
      '    "DISKUSI — pancing VIRA menawarkan ngobrol langsung dengan Steven, lalu balas \\"boleh\\": notif handover '
      'masuk, isinya berbunyi \\"VIRA sudah BERHENTI membalas\\", dan STATS.bot_mode = OFF.",\n'
      '    "DISKUSI (kontrol) — di nomor lain, balas \\"boleh\\" atas tawaran DECK: STATS.bot_mode harus tetap ON.",\n')

# --- 5. dua assertion lama yang memang berubah: enam slot -> tujuh -------
# Bagian # DECK menambah satu slot {{ $json.deck_context }}. Enam slot lama tetap
# utuh, dan itu dijaga terpisah dan lebih ketat oleh U24 (tujuh slot tanpa duplikat)
# serta R8 (tidak ada satu baris pun prompt lama yang diganti atau dibuang).
ganti(r'''cek("M2  enam ekspresi {{ }} tetap utuh",
    len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 6,
    str(len(_re.findall(r"\{\{[^}]+\}\}", _sp))))''',
      r'''cek("M2  tujuh ekspresi {{ }} tetap utuh (enam lama + deck_context)",
    len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 7,
    str(len(_re.findall(r"\{\{[^}]+\}\}", _sp))))''')
ganti(r'''cek("Q2  enam ekspresi {{ }} tetap utuh", len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 6)''',
      r'''cek("Q2  tujuh ekspresi {{ }} tetap utuh (enam lama + deck_context)",
    len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 7)''')

with io.open(DST, "w", encoding="utf-8", newline="\n") as f:
    f.write(teks)
print("ditulis: %s (%d baris)" % (os.path.basename(DST), teks.count("\n") + 1))
