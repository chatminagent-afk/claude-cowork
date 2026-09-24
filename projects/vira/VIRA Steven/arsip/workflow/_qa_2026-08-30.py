# -*- coding: utf-8 -*-
"""
_qa_2026-08-30.py — QA statis untuk semua berkas hasil Paket A+B+C+D+E.

Yang BISA diperiksa di sini: konsistensi struktur, keselarasan daftar field lintas
4 tempat, kabel workflow, dan selisih header sheet.

Yang TIDAK BISA diperiksa di sini: perilaku runtime — apakah AI benar-benar
mengeluarkan tag, apakah Google Sheets menulis baris yang benar, apakah notifikasi
WA terkirim. Itu UAT, butuh nomor aktif. Lihat checklist V1-V4 di
docs/2026-08-30-perbaikan-brief-deck.md.

Jalankan: python _qa_2026-08-30.py
Keluar dengan kode 1 kalau ada yang GAGAL.
"""
import csv
import io
import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)
WF = os.path.join(DIR, "2026-08-30-VIRA-Personal-Main.json")
PROMPT_MD = os.path.join(DIR, "2026-08-30-system-prompt-VIRA-Personal.md")
IMPORT_DIR = os.path.join(ROOT, "sheet", "2026-08-30-import")
HEADER_TSV = os.path.join(IMPORT_DIR, "REQUESTS-header.tsv")
KAMUS_CSV = os.path.join(IMPORT_DIR, "_KAMUS_BRIEF.csv")
XLSX = os.path.join(ROOT, "sheet", "VIRA Database.xlsx")
DOC = os.path.join(ROOT, "docs", "2026-08-30-perbaikan-brief-deck.md")

lolos, gagal, catatan = [], [], []


def ok(judul, detail=""):
    lolos.append(judul)
    print("  LOLOS  %s%s" % (judul, (" — " + detail) if detail else ""))


def no(judul, detail):
    gagal.append((judul, detail))
    print("  GAGAL  %s — %s" % (judul, detail))


def info(judul, detail):
    catatan.append((judul, detail))
    print("  CATAT  %s — %s" % (judul, detail))


def cek(judul, syarat, detail_gagal, detail_lolos=""):
    if syarat:
        ok(judul, detail_lolos)
    else:
        no(judul, detail_gagal)


print("=" * 72)
print("QA STATIS — VIRA Personal, patch 2026-08-30")
print("=" * 72)

# ─── 0. Semua berkas ada ───
print("\n[0] Keberadaan berkas")
for p in (WF, PROMPT_MD, HEADER_TSV, KAMUS_CSV, DOC):
    cek("ada: %s" % os.path.basename(p), os.path.exists(p), "tidak ditemukan di %s" % p)
if gagal:
    print("\nBerkas inti hilang, QA dihentikan.")
    sys.exit(1)

d = json.load(io.open(WF, encoding="utf-8"))
N = {n["name"]: n for n in d["nodes"]}
C = d["connections"]
pa_kode = N["Process All"]["parameters"]["jsCode"]
mb_kode = N["Merge Brief"]["parameters"]["jsCode"]
sm = N["AI Agent"]["parameters"]["options"]["systemMessage"]

# ─── 1. Integritas workflow ───
print("\n[1] Integritas workflow")
nama_node = [n["name"] for n in d["nodes"]]
cek("nama node unik", len(nama_node) == len(set(nama_node)),
    "ada nama dobel", "%d node" % len(nama_node))

putus = []
for asal, spec in C.items():
    if asal not in N:
        putus.append("sumber '%s' tidak ada" % asal)
    for cabang in spec.get("main", []):
        for t in cabang:
            if t["node"] not in N:
                putus.append("%s -> '%s' tidak ada" % (asal, t["node"]))
cek("semua koneksi menunjuk node nyata", not putus, "; ".join(putus))

punya_masuk = {t["node"] for s in C.values() for br in s.get("main", []) for t in br}
yatim = [n for n in nama_node if n not in punya_masuk and n not in C
         and N[n]["type"] not in ("n8n-nodes-base.stickyNote",)]
cek("tidak ada node yatim (tanpa kabel masuk & keluar)", not yatim, "yatim: %s" % yatim)

# ─── 2. Keseimbangan JS ───
print("\n[2] Sintaks code node")
sys.path.insert(0, DIR)
try:
    import importlib.util

    spec_js = importlib.util.spec_from_file_location("cekjs", os.path.join(DIR, "_cek_js.py"))
    # _cek_js.py mengeksekusi argv[1] saat diimpor, jadi disuntik dulu
    sys.argv = ["_cek_js.py", WF]
    mod = importlib.util.module_from_spec(spec_js)
    spec_js.loader.exec_module(mod)
    ok("_cek_js.py dijalankan", "lihat baris di atas")
except SystemExit:
    ok("_cek_js.py dijalankan")
except Exception as e:
    no("_cek_js.py", str(e))

# ─── 3. Urutan cabang deck ───
print("\n[3] Kabel cabang deck")
RANTAI = [
    "IF Deck Request", "Read REQUESTS", "Merge Brief", "Write REQUESTS",
    "Update STATS Brief", "Siapkan Notif Deck", "Wait Deck", "IF Brief Layak",
    "Notify Admin Deck",
]
for a, b in zip(RANTAI, RANTAI[1:]):
    tuj = [t["node"] for t in C.get(a, {}).get("main", [[]])[0]]
    cek("%s -> %s" % (a, b), tuj == [b], "ternyata menuju %s" % tuj)

cabang_if = C.get("IF Brief Layak", {}).get("main", [])
cek("IF Brief Layak cabang false berhenti (brief mentah tetap tersimpan)",
    len(cabang_if) == 2 and cabang_if[1] == [],
    "cabang false: %s" % (cabang_if[1] if len(cabang_if) > 1 else "tidak ada"))

# ─── 4. Tidak ada ekspresi lintas Wait ───
print("\n[4] Ekspresi setelah node Wait")
for nm in ("IF Brief Layak", "Notify Admin Deck"):
    teks = json.dumps(N[nm]["parameters"], ensure_ascii=False)
    ref = re.findall(r"\$\('([^']+)'\)", teks)
    cek("%s tidak memanggil $('NodeLain')" % nm, not ref, "masih memanggil: %s" % set(ref))

wait_pos = RANTAI.index("Wait Deck")
sebelum = RANTAI[:wait_pos]
cek("Update STATS Brief berjalan sebelum Wait Deck",
    "Update STATS Brief" in sebelum, "masih di hilir Wait")

# ─── 5. Daftar field selaras di 4 tempat ───
print("\n[5] Keselarasan daftar field")
f_proc = re.findall(r"'([a-z_]+)'",
                    re.search(r"const DECK_FIELDS = \[(.*?)\];", pa_kode, re.S).group(1))
f_merge = re.findall(r'"([a-z_]+)"',
                     re.search(r"const FIELDS = \[(.*?)\];", mb_kode, re.S).group(1))
f_label = re.findall(r'"([a-z_]+)":',
                     re.search(r"const LABEL = \{(.*?)\};", mb_kode, re.S).group(1))
i = sm.rfind("  [DECK_REQUEST]")
j = sm.find("[/DECK_REQUEST]", i)
f_tag = re.findall(r"^\s+([a-z_]+): \.\.\.$", sm[i:j], re.M)

cek("DECK_FIELDS (Process All) = 33 field", len(f_proc) == 33, "ternyata %d" % len(f_proc))
cek("Process All == Merge Brief FIELDS (urut sama)", f_proc == f_merge,
    "selisih: %s" % (set(f_proc) ^ set(f_merge)))
cek("Merge Brief LABEL menutup semua field", set(f_label) == set(f_merge),
    "tanpa label: %s" % (set(f_merge) - set(f_label)))
cek("blok tag di prompt == DECK_FIELDS (urut sama)", f_tag == f_proc,
    "selisih: %s | tag=%d proc=%d" % (set(f_tag) ^ set(f_proc), len(f_tag), len(f_proc)))

# ─── 6. Header REQUESTS vs pemetaan vs kamus ───
print("\n[6] Kolom REQUESTS")
header = io.open(HEADER_TSV, encoding="utf-8").read().strip().split("\t")
wr = list(N["Write REQUESTS"]["parameters"]["columns"]["value"].keys())
MANUAL = ["deck_dikirim_ts", "hasil", "alasan_kalah"]

cek("header REQUESTS = 43 kolom", len(header) == 43, "ternyata %d" % len(header))
cek("nama kolom header unik", len(header) == len(set(header)), "ada yang dobel")
cek("semua kolom yang dipetakan ada di header", set(wr) <= set(header),
    "dipetakan tapi tidak ada di header: %s" % (set(wr) - set(header)))
cek("kolom manual TIDAK dipetakan (tidak akan ditimpa workflow)",
    not (set(MANUAL) & set(wr)), "ikut dipetakan: %s" % (set(MANUAL) & set(wr)))
cek("semua field AI ikut ditulis ke sheet", set(f_proc) <= set(wr),
    "field AI tidak dipetakan: %s" % (set(f_proc) - set(wr)))

with io.open(KAMUS_CSV, encoding="utf-8") as f:
    baris = list(csv.reader(f))
kamus_head, kamus_rows = baris[0], baris[1:]
kamus_f = [r[0] for r in kamus_rows]
cek("_KAMUS_BRIEF punya 7 kolom", len(kamus_head) == 7, "ternyata %d" % len(kamus_head))
cek("_KAMUS_BRIEF mendokumentasikan semua kolom REQUESTS (urut sama)",
    kamus_f == header, "selisih: %s" % (set(kamus_f) ^ set(header)))
kosong = [r[0] for r in kamus_rows if not all(x.strip() for x in r)]
cek("tidak ada sel kosong di _KAMUS_BRIEF", not kosong, "baris kurang isi: %s" % kosong)

tingkat_sah = {"1", "2", "2B", "3", "selalu", "sistem", "manual"}
salah = [(r[0], r[1]) for r in kamus_rows if r[1] not in tingkat_sah]
cek("nilai kolom 'tingkat' sah semua", not salah, "tidak dikenal: %s" % salah)

# ─── 7. Gerbang & flag ───
print("\n[7] Gerbang tingkat 1 & flag deckLayak")
cek("Process All memaparkan deckLayak", "deckLayak: isDeckRequest && !deckRejected" in pa_kode,
    "flag tidak ditemukan")
cek("isDeckRequest tidak lagi dipaksa false saat tingkat 1 kurang",
    "isDeckRequest = DECK_FIELDS.some(f => deckRequest[f]);" in pa_kode,
    "gerbang lama masih ada")
cek("Merge Brief membaca deckLayak", "deck_layak: pa.deckLayak === true" in mb_kode,
    "tidak ditemukan")

for nm in ("Update to STATS", "Update STATS Brief"):
    ekspr = N[nm]["parameters"]["columns"]["value"].get("deck_requested", "")
    cek("%s.deck_requested pakai deckLayak" % nm,
        "deckLayak" in ekspr and "isDeckRequest" not in ekspr,
        "ekspresi: %s" % ekspr[:90])
    cek("%s.deck_requested mempertahankan nilai lama" % nm,
        "Resolve User Row" in ekspr, "tidak ada fallback nilai lama")

cek("brief_terisi ditulis dari Merge Brief",
    "Merge Brief" in N["Update STATS Brief"]["parameters"]["columns"]["value"]["brief_terisi"],
    "sumbernya bukan Merge Brief")

# ─── 8. Isi system prompt ───
print("\n[8] System prompt")
cek("TINGKAT 2B ada", "TINGKAT 2B" in sm, "tidak ditemukan")
cek("2B bergerbang 'setelah setuju dibuatkan pitch deck'",
    "SETELAH\ndia setuju dibuatkan pitch deck" in sm or "SETELAH dia setuju" in sm,
    "gerbang waktu tidak eksplisit")
blok_t3 = sm[sm.find("TINGKAT 3"):sm.find("TINGKAT 3") + 700]
# Empat hal ini pindah ke 2B (boleh ditanya) — tidak boleh tersisa di TINGKAT 3
for f in ("nilai rata-rata satu", "jumlah prospek per bulan",
          "biaya admin sekarang", "berapa orang yang membalas chat"):
    cek("'%s' sudah keluar dari TINGKAT 3" % f, f not in blok_t3, "masih ada di TINGKAT 3")
# Lima field Paket B tetap di TINGKAT 3
for f in ("kotanya", "pernah", "price list, katalog"):
    cek("TINGKAT 3 masih memuat '%s'" % f, f in blok_t3, "hilang dari TINGKAT 3")
cek("2B menanyakan admin hanya kalau memang pakai admin",
    "LEWATI dua ini" in sm, "syarat 'kalau ownernya balas sendiri' tidak ada")
cek("2B menanyakan biaya admin per bulan",
    "biaya admin per bulan" in sm, "tidak ditemukan di 2B")
cek("jumlah tingkat sudah 'empat'", "Ada empat tingkat informasi" in sm, "masih tertulis tiga")
cek("TINGKAT 1 bukan lagi gerbang emisi tag",
    "tidak menunda `[DECK_REQUEST]`" in sm, "kalimat gerbang lama masih ada")
cek("ada rem emisi tag berulang",
    "tidak ada satu pun informasi baru sejak tag terakhir" in sm, "rem tidak ditemukan")
cek("aturan kutipan_asli ada", "kutipan_asli` justru diisi kutipan MENTAH" in sm,
    "tidak ditemukan")
cek("kutipan_asli dilarang memuat data pribadi",
    "Jangan pernah memasukkan nomor telepon" in sm, "peringatan privasi tidak ada")

md = io.open(PROMPT_MD, encoding="utf-8").read()
cek("prompt .md sinkron dengan JSON", sm in md, "isi .md berbeda dari node AI Agent")

# ─── 9. Selisih terhadap sheet live ───
print("\n[9] Selisih terhadap sheet live (VIRA Database.xlsx)")
try:
    import openpyxl

    wb = openpyxl.load_workbook(XLSX, read_only=True)
    tabs = {ws.title: [c.value for c in next(ws.iter_rows(min_row=1, max_row=1)) if c.value]
            for ws in wb.worksheets}

    cek("tab STATS punya kolom brief_terisi", "brief_terisi" in tabs.get("STATS", []),
        "TIDAK ADA — ini kandidat penyebab brief_terisi kosong di data 16 Agu")
    cek("tab REQUESTS ada", "REQUESTS" in tabs, "tidak ada")
    cek("_KAMUS_BRIEF belum ada (memang harus dibuat manual)",
        "_KAMUS_BRIEF" not in tabs, "sudah ada — pastikan isinya sama dengan CSV")

    live = tabs.get("REQUESTS", [])
    tambah = [c for c in header if c not in live]
    geser = live != header[:len(live)]
    info("kolom REQUESTS yang harus ditambahkan manual (%d)" % len(tambah),
         ", ".join(tambah) if tambah else "tidak ada")
    cek("32 kolom lama tidak bergeser", not geser,
        "urutan kolom lama berubah — akan merusak baris yang sudah ada")

    for t in ("CONFIG", "LINKS", "ABOUT_STEVEN", "FAQ", "PROGRAM", "EVENTS", "MSG_BUFFER",
              "UNKNOWN", "DASH_AUDIT"):
        if t not in tabs:
            no("tab %s ada di sheet" % t, "hilang")
except ImportError:
    info("openpyxl tidak terpasang", "pemeriksaan sheet dilewati")

# ─── 10. Node Sheets menunjuk tab yang ada ───
print("\n[10] Node Google Sheets")
try:
    tak_dikenal = []
    for n in d["nodes"]:
        if n["type"] == "n8n-nodes-base.googleSheets":
            t = n["parameters"].get("sheetName", {})
            nama_tab = t.get("value") if isinstance(t, dict) else t
            if isinstance(nama_tab, str) and nama_tab and nama_tab not in tabs:
                tak_dikenal.append((n["name"], nama_tab))
    cek("semua node Sheets menunjuk tab yang ada", not tak_dikenal, "%s" % tak_dikenal)
except NameError:
    info("pemeriksaan tab dilewati", "sheet tidak terbaca")

# ─── Ringkasan ───
print("\n" + "=" * 72)
print("LOLOS : %d" % len(lolos))
print("CATAT : %d  (perlu tindakan manual, bukan kegagalan)" % len(catatan))
print("GAGAL : %d" % len(gagal))
for j, dt in gagal:
    print("   !! %s — %s" % (j, dt))
print("=" * 72)
print("CATATAN: ini QA STATIS. UAT perilaku (V1-V4) belum bisa dijalankan")
print("         selama nomor WA belum aktif.")
sys.exit(1 if gagal else 0)
