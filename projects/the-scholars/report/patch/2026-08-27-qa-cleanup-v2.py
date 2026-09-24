# -*- coding: utf-8 -*-
"""QA for 2026-08-27-VIRA-STATS-cleanup-3bulan-v2.json

Aturan v2 yang diuji:
  HAPUS semua baris data KECUALI header dan baris bot_mode == "OFF"
  yang off_reason-nya BUKAN "VIRA".

Sections:
  A. Structure / graph
  B. JS syntax of the Code nodes
  C. Logic port of "Plan cleanup v2" + edge cases
  D. Full sheet-transformation simulation (append-then-delete)
  E. Regression vs aturan lama (off_reason == SAM only)
"""
import json
import re
import sys

WF = r"D:\Documents\Claude Cowork\the scholars\report\patch\2026-08-27-VIRA-STATS-cleanup-3bulan-v2.json"

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    mark = "PASS" if cond else "FAIL"
    line = f"  [{mark}] {name}"
    if detail:
        line += f"  -- {detail}"
    print(line)
    return cond


# ====================================================================
print("=" * 68)
print("A. STRUKTUR & GRAPH")
print("=" * 68)

with open(WF, encoding="utf-8") as f:
    wf = json.load(f)

nodes = wf["nodes"]
conns = wf["connections"]
names = [n["name"] for n in nodes]
by_name = {n["name"]: n for n in nodes}

check("A1 JSON valid & punya nodes/connections", "nodes" in wf and "connections" in wf)
check("A2 jumlah node = 9", len(nodes) == 9, f"{len(nodes)}")
check("A3 nama node unik", len(set(names)) == len(names))
check("A4 semua node punya id unik", len({n["id"] for n in nodes}) == len(nodes))

bad_src = [s for s in conns if s not in by_name]
targets = []
for src, spec in conns.items():
    for branch in spec.get("main", []):
        for c in branch:
            targets.append(c["node"])
bad_tgt = [t for t in targets if t not in by_name]
check("A5 semua source connection ada sbg node", not bad_src, str(bad_src))
check("A6 semua target connection ada sbg node", not bad_tgt, str(bad_tgt))

EXPECTED_EDGES = {
    ("Every 3 months 00:01 WIB", "Read STATS (all)"),
    ("Read STATS (all)", "Plan cleanup"),
    ("Plan cleanup", "IF Ada Baris Dipertahankan"),
    ("IF Ada Baris Dipertahankan", "Split kept rows"),
    ("IF Ada Baris Dipertahankan", "Prepare delete"),
    ("Split kept rows", "Append Baris Dipertahankan"),
    ("Append Baris Dipertahankan", "Prepare delete"),
    ("Prepare delete", "Delete original block"),
    ("Delete original block", "Notify Steven"),
}
actual_edges = set()
for src, spec in conns.items():
    for branch in spec.get("main", []):
        for c in branch:
            actual_edges.add((src, c["node"]))
check("A7 graph sama persis dengan desain v1 (urutan append->delete utuh)",
      actual_edges == EXPECTED_EDGES,
      str(actual_edges ^ EXPECTED_EDGES))

# urutan aman: append berada SEBELUM delete di jalur true
if_node = by_name["IF Ada Baris Dipertahankan"]
true_branch = [c["node"] for c in conns["IF Ada Baris Dipertahankan"]["main"][0]]
false_branch = [c["node"] for c in conns["IF Ada Baris Dipertahankan"]["main"][1]]
check("A8 IF true -> Split kept rows (bukan langsung delete)", true_branch == ["Split kept rows"], str(true_branch))
check("A9 IF false -> Prepare delete", false_branch == ["Prepare delete"], str(false_branch))

trig = by_name["Every 3 months 00:01 WIB"]["parameters"]
cron = json.dumps(trig)
check("A10 cron tetap '1 0 1 */3 *'", "1 0 1 */3 *" in cron, cron[:120])
check("A11 timezone workflow Asia/Jakarta", wf.get("settings", {}).get("timezone") == "Asia/Jakarta")
check("A12 workflow di-import dalam keadaan non-aktif", wf.get("active") is False)

dele = by_name["Delete original block"]["parameters"]
check("A13 Delete pakai startRow/totalDataRows dari plan",
      dele.get("startIndex") == "={{ $json.startRow }}"
      and dele.get("numberToDelete") == "={{ $json.totalDataRows }}",
      json.dumps(dele.get("startIndex")) + " / " + json.dumps(dele.get("numberToDelete")))

gs = [n for n in nodes if n["type"] == "n8n-nodes-base.googleSheets"]
gids = {json.dumps(n["parameters"]["sheetName"]["value"]) for n in gs}
docs = {json.dumps(n["parameters"]["documentId"]["value"]) for n in gs}
check("A14 semua node Sheets menunjuk gid yang sama", len(gids) == 1, str(gids))
check("A15 semua node Sheets menunjuk spreadsheet yang sama", len(docs) == 1, str(docs))

# ====================================================================
print()
print("=" * 68)
print("B. SYNTAX CODE NODE")
print("=" * 68)

code_nodes = {n["name"]: n["parameters"]["jsCode"] for n in nodes if n["type"] == "n8n-nodes-base.code"}
check("B1 3 node Code hadir", set(code_nodes) == {"Plan cleanup", "Split kept rows", "Prepare delete"}, str(set(code_nodes)))

for nm, src in code_nodes.items():
    bal = src.count("{") - src.count("}")
    check(f"B2 kurung kurawal balance - {nm}", bal == 0, f"selisih {bal}")
    bal = src.count("(") - src.count(")")
    check(f"B3 kurung bulat balance - {nm}", bal == 0, f"selisih {bal}")

plan_src = code_nodes["Plan cleanup"]
check("B4 Plan cleanup tidak lagi memakai KEEP_VALUE='SAM' sebagai satu-satunya syarat simpan",
      "const KEEP_VALUE = 'SAM'" not in plan_src)
check("B5 Plan cleanup memakai OFF_VALUE + DELETE_LABEL",
      "OFF_VALUE" in plan_src and "DELETE_LABEL" in plan_src)
check("B6 guard bot_mode hard-fail ada", "Kolom \"bot_mode\" tidak ditemukan" in plan_src)
check("B7 guard No WA hard-fail ada", "Kolom \"No WA\" tidak ditemukan" in plan_src)
throw_lines = [ln for ln in plan_src.splitlines() if "throw new Error" in ln]
check("B8a tidak ada throw yang dipicu kolom off_reason",
      not any("off_reason" in ln for ln in throw_lines), str(throw_lines))
check("B8b off_reason absen ditangani sbg console.log + flag hasOffReason",
      "hasOffReason" in plan_src
      and re.search(r"if \(!hasOffReason\) \{\s*\n\s*console\.log", plan_src) is not None)
check("B8c tepat 2 throw (No WA + bot_mode)", len(throw_lines) == 2, str(len(throw_lines)))
check("B9 row_number dibuang sebelum di-append", "delete copy.row_number" in plan_src)

for nm in ("Split kept rows", "Prepare delete"):
    check(f"B10 {nm} mereferensi node 'Plan cleanup'", "$('Plan cleanup')" in code_nodes[nm])

msg = [p["value"] for p in by_name["Notify Steven"]["parameters"]["bodyParameters"]["parameters"] if p["name"] == "message"][0]
for fld in ("totalDataRows", "keptCount", "deleteCount", "keptOffSam", "keptOffBlank",
            "keptOffOther", "delOffVira", "delNotOff", "delBlankGap", "hasOffReason"):
    check(f"B11 notif memakai field {fld}", fld in msg)
emitted = set(re.findall(r"^\s{4}(\w+)[,:]", plan_src, re.M))
used = set(re.findall(r"first\(\)\.json\.(\w+)", msg))
check("B12 semua field di notif diemit Plan cleanup", used <= emitted | {"totalDataRows"}, str(used - emitted))

# ====================================================================
print()
print("=" * 68)
print("C. PORT LOGIKA 'Plan cleanup v2' + EDGE CASE")
print("=" * 68)


def norm(v):
    return str("" if v is None else v).strip().upper()


def plan_cleanup(rows):
    """Port 1:1 dari jsCode Plan cleanup v2. Mengembalikan dict atau None (return [])."""
    rows = [r for r in rows if isinstance(r, dict)
            and r.get("row_number") is not None and int(r["row_number"]) >= 2]
    if not rows:
        return None
    if not any("No WA" in r for r in rows):
        raise ValueError("GUARD_NO_WA")
    if not any("bot_mode" in r for r in rows):
        raise ValueError("GUARD_BOT_MODE")
    has_off_reason = any("off_reason" in r for r in rows)

    kept, k_sam, k_blank, k_other, d_vira, d_notoff = [], 0, 0, 0, 0, 0
    for r in rows:
        mode, reason = norm(r.get("bot_mode")), norm(r.get("off_reason"))
        if mode != "OFF":
            d_notoff += 1
            continue
        if reason == "VIRA":
            d_vira += 1
            continue
        c = dict(r)
        c.pop("row_number", None)
        kept.append(c)
        if reason == "SAM":
            k_sam += 1
        elif reason == "":
            k_blank += 1
        else:
            k_other += 1

    max_row = max(int(r["row_number"]) for r in rows)
    total = max_row - 1
    if total < 1:
        return None
    delete_count = total - len(kept)
    if delete_count <= 0:
        return None
    return dict(startRow=2, totalDataRows=total, keptCount=len(kept), deleteCount=delete_count,
                keptOffSam=k_sam, keptOffBlank=k_blank, keptOffOther=k_other,
                delOffVira=d_vira, delNotOff=d_notoff,
                delBlankGap=max(0, delete_count - d_vira - d_notoff),
                hasOffReason=has_off_reason, keptRows=kept)


def row(n, wa, mode, reason=None):
    r = {"row_number": n, "No WA": wa, "bot_mode": mode}
    if reason is not None:
        r["off_reason"] = reason
    return r


# --- C1: kasus utama dari spesifikasi Steven
data = [
    row(2, "6281000000001", "ON", ""),            # aktif           -> HAPUS
    row(3, "6281000000002", "OFF", "VIRA"),       # OFF by VIRA     -> HAPUS
    row(4, "6281000000003", "OFF", "SAM"),        # OFF by Sam      -> SIMPAN
    row(5, "6281000000004", "OFF", ""),           # OFF lupa label  -> SIMPAN
    row(6, "6281000000005", "OFF", None),         # kolom tak terisi-> SIMPAN
    row(7, "6281000000006", "ON", "VIRA"),        # aktif tp berlabel-> HAPUS
]
p = plan_cleanup(data)
check("C1a kept = 3 (semua OFF non-VIRA)", p["keptCount"] == 3, str(p["keptCount"]))
check("C1b deleted = 3", p["deleteCount"] == 3, str(p["deleteCount"]))
kept_wa = {r["No WA"] for r in p["keptRows"]}
check("C1c yang disimpan tepat 03/04/05",
      kept_wa == {"6281000000003", "6281000000004", "6281000000005"}, str(sorted(kept_wa)))
check("C1d OFF+VIRA masuk hitungan delOffVira", p["delOffVira"] == 1, str(p["delOffVira"]))
check("C1e baris ON dengan label VIRA tetap dihapus (bot_mode menang)", p["delNotOff"] == 2, str(p["delNotOff"]))
check("C1f rincian kept konsisten",
      p["keptOffSam"] == 1 and p["keptOffBlank"] == 2 and p["keptOffOther"] == 0,
      f"sam={p['keptOffSam']} blank={p['keptOffBlank']} other={p['keptOffOther']}")

# --- C2: case-insensitive + trim
data = [
    row(2, "a", " off ", " vira "),   # HAPUS
    row(3, "b", "Off", "Vira"),       # HAPUS
    row(4, "c", "oFF", " sam "),      # SIMPAN
    row(5, "d", "OFF", "  "),         # SIMPAN (whitespace = kosong)
    row(6, "e", "on", "vira"),        # HAPUS
]
p = plan_cleanup(data)
check("C2a normalisasi case+trim bekerja untuk OFF & VIRA", p["deleteCount"] == 3, str(p["deleteCount"]))
check("C2b kept = c, d", {r["No WA"] for r in p["keptRows"]} == {"c", "d"}, str(p["keptRows"]))
check("C2c off_reason ' sam ' -> keptOffSam", p["keptOffSam"] == 1, str(p["keptOffSam"]))
check("C2d off_reason '  ' -> keptOffBlank", p["keptOffBlank"] == 1, str(p["keptOffBlank"]))

# --- C3: label di luar SAM/VIRA
data = [row(2, "a", "OFF", "CEK"), row(3, "b", "OFF", "manual"), row(4, "c", "ON", "")]
p = plan_cleanup(data)
check("C3a label asing tetap DISIMPAN (fail-safe)", p["keptCount"] == 2, str(p["keptCount"]))
check("C3b masuk keptOffOther untuk ditandai di notif", p["keptOffOther"] == 2, str(p["keptOffOther"]))

# --- C4: guard
try:
    plan_cleanup([{"row_number": 2, "bot_mode": "OFF"}])
    check("C4a guard 'No WA' throw", False, "tidak throw")
except ValueError as e:
    check("C4a guard 'No WA' throw", str(e) == "GUARD_NO_WA", str(e))

try:
    plan_cleanup([{"row_number": 2, "No WA": "a", "off_reason": "VIRA"}])
    check("C4b guard 'bot_mode' throw (KRITIS v2)", False, "tidak throw")
except ValueError as e:
    check("C4b guard 'bot_mode' throw (KRITIS v2)", str(e) == "GUARD_BOT_MODE", str(e))

# off_reason belum ada -> jalan terus, semua OFF selamat
data = [row(2, "a", "OFF"), row(3, "b", "OFF"), row(4, "c", "ON")]
p = plan_cleanup(data)
check("C4c off_reason absen -> tidak throw", p is not None)
check("C4d off_reason absen -> semua OFF disimpan", p["keptCount"] == 2, str(p["keptCount"]))
check("C4e off_reason absen -> flag hasOffReason False", p["hasOffReason"] is False)
check("C4f off_reason absen -> nol baris OFF dihapus", p["delOffVira"] == 0, str(p["delOffVira"]))

# --- C5: sheet kosong / hanya header
check("C5a input kosong -> no-op", plan_cleanup([]) is None)
check("C5b hanya header -> no-op", plan_cleanup([{"row_number": 1, "No WA": "hdr", "bot_mode": "x"}]) is None)

# --- C6: guard 4 - tidak ada yang perlu dihapus
data = [row(2, "a", "OFF", "SAM"), row(3, "b", "OFF", "")]
check("C6 semua baris disimpan & tanpa celah -> cleanup dilewati", plan_cleanup(data) is None)

# --- C7: baris kosong di tengah ikut dirapikan
data = [row(2, "a", "OFF", "SAM"), row(5, "b", "ON", "")]   # baris 3-4 kosong
p = plan_cleanup(data)
check("C7a totalDataRows dari row_number terbesar", p["totalDataRows"] == 4, str(p["totalDataRows"]))
check("C7b delBlankGap menghitung celah", p["delBlankGap"] == 2, str(p["delBlankGap"]))
check("C7c deleteCount = 3", p["deleteCount"] == 3, str(p["deleteCount"]))

# ====================================================================
print()
print("=" * 68)
print("D. SIMULASI TRANSFORMASI SHEET (append -> delete)")
print("=" * 68)


def simulate(sheet_rows):
    """sheet_rows = list dict (baris 2..N). Kembalikan isi sheet setelah workflow."""
    rows = [dict(r, row_number=i + 2) for i, r in enumerate(sheet_rows)]
    p = plan_cleanup(rows)
    if p is None:
        return [dict((k, v) for k, v in r.items() if k != "row_number") for r in rows]
    body = [dict((k, v) for k, v in r.items() if k != "row_number") for r in rows]
    if p["keptCount"] > 0:                       # jalur IF true
        body = body + [dict(r) for r in p["keptRows"]]
    start_idx = p["startRow"] - 2                # 0-based dalam body
    del body[start_idx:start_idx + p["totalDataRows"]]
    return body


sheet = [
    {"No WA": "w1", "bot_mode": "ON",  "off_reason": "",     "Nama": "Ana"},
    {"No WA": "w2", "bot_mode": "OFF", "off_reason": "VIRA", "Nama": "Budi"},
    {"No WA": "w3", "bot_mode": "OFF", "off_reason": "SAM",  "Nama": "Citra"},
    {"No WA": "w4", "bot_mode": "OFF", "off_reason": "",     "Nama": "Dedi"},
    {"No WA": "w5", "bot_mode": "ON",  "off_reason": "",     "Nama": "Eka"},
]
out = simulate(sheet)
check("D1a sisa 2 baris", len(out) == 2, str(len(out)))
check("D1b sisa = w3 & w4, urutan terjaga", [r["No WA"] for r in out] == ["w3", "w4"], str([r["No WA"] for r in out]))
check("D1c kolom lain ikut terbawa utuh", out[0]["Nama"] == "Citra" and out[1]["Nama"] == "Dedi")
check("D1d tidak ada duplikat tersisa", len({r["No WA"] for r in out}) == len(out))

# semua ON -> jalur IF false, tidak ada append
sheet = [{"No WA": f"x{i}", "bot_mode": "ON", "off_reason": ""} for i in range(5)]
out = simulate(sheet)
check("D2 semua bot aktif -> sheet bersih total (header saja)", out == [], str(out))

# semua OFF non-VIRA -> guard 4, sheet tak tersentuh
sheet = [{"No WA": f"y{i}", "bot_mode": "OFF", "off_reason": "SAM"} for i in range(4)]
out = simulate(sheet)
check("D3 semua OFF non-VIRA -> sheet tidak berubah sama sekali",
      [r["No WA"] for r in out] == ["y0", "y1", "y2", "y3"], str(out))

# skala 300 baris
sheet = []
for i in range(300):
    if i % 10 == 0:
        sheet.append({"No WA": f"z{i}", "bot_mode": "OFF", "off_reason": "SAM"})
    elif i % 10 == 1:
        sheet.append({"No WA": f"z{i}", "bot_mode": "OFF", "off_reason": ""})
    elif i % 10 == 2:
        sheet.append({"No WA": f"z{i}", "bot_mode": "OFF", "off_reason": "VIRA"})
    else:
        sheet.append({"No WA": f"z{i}", "bot_mode": "ON", "off_reason": ""})
out = simulate(sheet)
expect = [r["No WA"] for r in sheet if r["bot_mode"] == "OFF" and r["off_reason"] != "VIRA"]
check("D4a 300 baris -> 60 tersisa", len(out) == 60, str(len(out)))
check("D4b isi & urutan persis sesuai aturan", [r["No WA"] for r in out] == expect)

# ====================================================================
print()
print("=" * 68)
print("E. REGRESI vs ATURAN LAMA (v1: simpan hanya off_reason == SAM)")
print("=" * 68)


def plan_v1(rows):
    kept = [r for r in rows if norm(r.get("off_reason")) == "SAM"]
    return {r["No WA"] for r in kept}


sheet = [
    row(2, "sam-labeled", "OFF", "SAM"),
    row(3, "dashboard-off", "OFF", ""),        # di-OFF lewat VIRA Dashboard
    row(4, "sam-lupa-label", "OFF", None),     # Sam lupa isi dropdown
    row(5, "vira-off", "OFF", "VIRA"),
    row(6, "aktif", "ON", ""),
]
v1 = plan_v1(sheet)
v2 = {r["No WA"] for r in plan_cleanup(sheet)["keptRows"]}
check("E1 v1 hanya menyelamatkan baris berlabel SAM", v1 == {"sam-labeled"}, str(sorted(v1)))
check("E2 v2 juga menyelamatkan baris dashboard & lupa-label",
      v2 == {"sam-labeled", "dashboard-off", "sam-lupa-label"}, str(sorted(v2)))
check("E3 v2 superset dari v1 (tidak ada baris yang dulu selamat jadi terhapus)", v1 <= v2, str(sorted(v1 - v2)))
check("E4 baris OFF by VIRA tetap dihapus di v2", "vira-off" not in v2)
check("E5 baris aktif tetap dihapus di v2", "aktif" not in v2)

# ====================================================================
print()
print("=" * 68)
print(f"HASIL: {len(PASS)} PASS, {len(FAIL)} FAIL")
if FAIL:
    for f in FAIL:
        print("  FAIL:", f)
print("=" * 68)
sys.exit(1 if FAIL else 0)
