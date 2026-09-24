# -*- coding: utf-8 -*-
"""QA for 2026-08-27-VIRA-STATS-cleanup-3bulan-v3.json

Aturan v3 = aturan v2 (lindungi baris OFF non-VIRA) + filter umur.
Baris DIHAPUS hanya kalau: tidak dilindungi DAN punya jejak waktu DAN
jejaknya sudah lewat RETENTION_DAYS.

Sections:
  A. Structure / graph
  B. JS syntax + konstanta node Code
  C. Port logika "Plan cleanup v3" + edge case
  D. Blok penghapusan (kontigu, menurun) + simulasi hapus sungguhan
  E. Regresi vs v2 (skenario "chat 30 Sept, cleanup 1 Okt")
  F. Data STATS nyata
"""
import json
import re
import sys
import datetime

WF = r"D:\Documents\Claude Cowork\the scholars\report\patch\2026-08-27-VIRA-STATS-cleanup-3bulan-v3.json"
XLSX = r"D:\Documents\Claude Cowork\the scholars\archive\report-production-V4-obsolete\The_Scholars_Database.xlsx"

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    line = f"  [{'PASS' if cond else 'FAIL'}] {name}"
    if detail:
        line += f"  -- {detail}"
    print(line)
    return cond


# ====================================================================
print("=" * 70)
print("A. STRUKTUR & GRAPH")
print("=" * 70)

with open(WF, encoding="utf-8") as f:
    wf = json.load(f)

nodes = wf["nodes"]
conns = wf["connections"]
by_name = {n["name"]: n for n in nodes}
names = [n["name"] for n in nodes]

check("A1 nama node unik", len(set(names)) == len(names))
check("A2 jumlah node = 8", len(nodes) == 8, str(len(nodes)))
check("A3 node append sudah dibuang (tidak ada salin-lalu-hapus)",
      not any("Append" in n for n in names), str([n for n in names if "Append" in n]))

EXPECTED = {
    ("Every 3 months 00:01 WIB", "Read STATS (all)"),
    ("Read STATS (all)", "Plan cleanup"),
    ("Plan cleanup", "IF Ada Yang Dihapus"),
    ("IF Ada Yang Dihapus", "Split delete blocks"),
    ("IF Ada Yang Dihapus", "Collapse to one"),
    ("Split delete blocks", "Delete STATS rows"),
    ("Delete STATS rows", "Collapse to one"),
    ("Collapse to one", "Notify Steven"),
}
actual = {(s, c["node"]) for s, sp in conns.items() for br in sp["main"] for c in br}
check("A4 graph sesuai desain v3", actual == EXPECTED, str(actual ^ EXPECTED))

t = [c["node"] for c in conns["IF Ada Yang Dihapus"]["main"][0]]
f_ = [c["node"] for c in conns["IF Ada Yang Dihapus"]["main"][1]]
check("A5 IF true -> Split delete blocks", t == ["Split delete blocks"], str(t))
check("A6 IF false -> Collapse (notifikasi tetap terkirim)", f_ == ["Collapse to one"], str(f_))

cond = by_name["IF Ada Yang Dihapus"]["parameters"]["conditions"]["conditions"][0]
check("A7 kondisi IF = deleteCount > 0",
      cond["leftValue"] == "={{ $json.deleteCount }}" and cond["rightValue"] == 0
      and cond["operator"]["operation"] == "gt",
      json.dumps(cond["leftValue"]) + " " + cond["operator"]["operation"] + " " + str(cond["rightValue"]))

dele = by_name["Delete STATS rows"]["parameters"]
check("A8 Delete pakai startRow/count per blok",
      dele["startIndex"] == "={{ $json.startRow }}" and dele["numberToDelete"] == "={{ $json.count }}",
      json.dumps(dele["startIndex"]) + " / " + json.dumps(dele["numberToDelete"]))
check("A9 Delete operation = delete", dele.get("operation") == "delete", str(dele.get("operation")))
check("A10 Delete retryOnFail aktif", by_name["Delete STATS rows"].get("retryOnFail") is True)

gs = [n for n in nodes if n["type"] == "n8n-nodes-base.googleSheets"]
check("A11 tinggal 2 node Sheets (read + delete)", len(gs) == 2, str([n["name"] for n in gs]))
check("A12 keduanya menunjuk gid & spreadsheet yang sama",
      len({n["parameters"]["sheetName"]["value"] for n in gs}) == 1
      and len({json.dumps(n["parameters"]["documentId"]["value"]) for n in gs}) == 1)

check("A13 cron tetap '1 0 1 */3 *'",
      "1 0 1 */3 *" in json.dumps(by_name["Every 3 months 00:01 WIB"]["parameters"]))
check("A14 timezone Asia/Jakarta", wf["settings"]["timezone"] == "Asia/Jakarta")
check("A15 errorWorkflow dipertahankan", bool(wf["settings"].get("errorWorkflow")))
check("A16 import dalam keadaan non-aktif", wf.get("active") is False)

msg = [p["value"] for p in by_name["Notify Steven"]["parameters"]["bodyParameters"]["parameters"]
       if p["name"] == "message"][0]
check("A17 notif memakai report siap-pakai dari Plan cleanup",
      msg == "={{ $('Plan cleanup').first().json.report }}", msg[:80])

# ====================================================================
print()
print("=" * 70)
print("B. SYNTAX & KONSTANTA CODE NODE")
print("=" * 70)

code = {n["name"]: n["parameters"]["jsCode"] for n in nodes if n["type"] == "n8n-nodes-base.code"}
check("B1 3 node Code", set(code) == {"Plan cleanup", "Split delete blocks", "Collapse to one"}, str(set(code)))
for nm, src in code.items():
    check(f"B2 kurung balance - {nm}",
          src.count("{") == src.count("}") and src.count("(") == src.count(")"))

plan = code["Plan cleanup"]
m = re.search(r"const RETENTION_DAYS\s*=\s*(\d+)", plan)
check("B3 RETENTION_DAYS terdefinisi", m is not None)
RET = int(m.group(1)) if m else 0
check("B4 RETENTION_DAYS = 90 (3 bulan)", RET == 90, str(RET))

m = re.search(r"const TS_COLS = \[([^\]]+)\]", plan, re.S)
ts_cols = re.findall(r"'([^']+)'", m.group(1)) if m else []
check("B5 TS_COLS mencakup buffer_done_ts (satu-satunya yang terisi di jalur OFF)",
      "buffer_done_ts" in ts_cols, str(ts_cols))
check("B6 TS_COLS mencakup last_reply_ts", "last_reply_ts" in ts_cols)
check("B7 normalisasi milidetik per-nilai ada", "1e12" in plan and "/ 1000" in plan)
check("B8 fallback ke kolom tanggal manusia ada",
      "Tanggal Chat Terakhir" in plan and "Tanggal Chat Pertama" in plan)

throws = [ln for ln in plan.splitlines() if "throw new Error" in ln]
check("B9 3 guard hard-fail (No WA, bot_mode, kolom umur)", len(throws) == 3, str(len(throws)))
check("B10 off_reason TIDAK memicu throw", not any("off_reason" in ln for ln in throws))
check("B11 blok diurutkan menurun sebelum dikirim", "blocks.reverse()" in plan)
check("B12 Split delete blocks tidak mengurutkan ulang",
      "sort" not in code["Split delete blocks"])
check("B13 Collapse mengembalikan tepat 1 item",
      "return [{ json: plan }]" in code["Collapse to one"])

# ====================================================================
print()
print("=" * 70)
print("C. PORT LOGIKA 'Plan cleanup v3' + EDGE CASE")
print("=" * 70)

TS_COLS = ts_cols
DAY = 86400


def norm(v):
    return str("" if v is None else v).strip().upper()


def to_sec(v):
    s = str("" if v is None else v).strip()
    try:
        n = float(s)
    except ValueError:
        return 0
    if n <= 0:
        return 0
    return int(n / 1000) if n > 1e12 else int(n)


def parse_tanggal(v):
    s = str("" if v is None else v).strip()
    if not s:
        return 0
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})", s)
    if m:
        return int(datetime.datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)),
                                     tzinfo=datetime.timezone.utc).timestamp())
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return int(datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                     tzinfo=datetime.timezone.utc).timestamp())
    return 0


def last_activity(r):
    best = 0
    for c in TS_COLS:
        n = to_sec(r.get(c))
        if n > best:
            best = n
    if not best:
        best = parse_tanggal(r.get("Tanggal Chat Terakhir")) or parse_tanggal(r.get("Tanggal Chat Pertama"))
    return best


def plan_cleanup(rows, now):
    rows = [r for r in rows if isinstance(r, dict)
            and r.get("row_number") is not None and int(r["row_number"]) >= 2]
    if not rows:
        return None
    if not any("No WA" in r for r in rows):
        raise ValueError("GUARD_NO_WA")
    if not any("bot_mode" in r for r in rows):
        raise ValueError("GUARD_BOT_MODE")
    age_cols = TS_COLS + ["Tanggal Chat Terakhir", "Tanggal Chat Pertama"]
    if not any(c in r for c in age_cols for r in rows):
        raise ValueError("GUARD_AGE_COLS")

    cutoff = now - 90 * DAY
    dels, no_ts = [], []
    st = dict(protSam=0, protBlank=0, protOther=0, keepHangat=0,
              keepTanpaJejak=0, delOffVira=0, delNotOff=0)
    for r in rows:
        mode, reason = norm(r.get("bot_mode")), norm(r.get("off_reason"))
        if mode == "OFF" and reason != "VIRA":
            st["protSam" if reason == "SAM" else ("protBlank" if reason == "" else "protOther")] += 1
            continue
        act = last_activity(r)
        if not act:
            st["keepTanpaJejak"] += 1
            no_ts.append(int(r["row_number"]))
            continue
        if act >= cutoff:
            st["keepHangat"] += 1
            continue
        st["delOffVira" if mode == "OFF" else "delNotOff"] += 1
        dels.append(int(r["row_number"]))

    dels.sort()
    blocks = []
    for n in dels:
        if blocks and n == blocks[-1]["startRow"] + blocks[-1]["count"]:
            blocks[-1]["count"] += 1
        else:
            blocks.append({"startRow": n, "count": 1})
    blocks.reverse()
    st.update(totalDataRows=len(rows), deleteCount=len(dels), keepCount=len(rows) - len(dels),
              blocks=blocks, blockCount=len(blocks), noTsRows=no_ts,
              hasOffReason=any("off_reason" in r for r in rows))
    return st


NOW = 1788000000          # 2026-08-29-ish
OLD = NOW - 200 * DAY     # jauh lewat ambang
FRESH = NOW - 5 * DAY     # baru saja


def row(n, wa, mode, reason=None, **ts):
    r = {"row_number": n, "No WA": wa, "bot_mode": mode}
    if reason is not None:
        r["off_reason"] = reason
    r.update(ts)
    return r


# --- C1 aturan inti
data = [
    row(2, "aktif-lama",   "ON",  "",     last_reply_ts=OLD),      # HAPUS
    row(3, "aktif-baru",   "ON",  "",     last_reply_ts=FRESH),    # SIMPAN (hangat)
    row(4, "vira-lama",    "OFF", "VIRA", last_reply_ts=OLD),      # HAPUS
    row(5, "vira-baru",    "OFF", "VIRA", last_reply_ts=FRESH),    # SIMPAN (hangat)
    row(6, "sam-lama",     "OFF", "SAM",  last_reply_ts=OLD),      # SIMPAN (dilindungi)
    row(7, "blank-lama",   "OFF", "",     last_reply_ts=OLD),      # SIMPAN (dilindungi)
    row(8, "tanpa-jejak",  "ON",  ""),                             # SIMPAN (tak diketahui)
]
p = plan_cleanup(data, NOW)
check("C1a hapus = 2", p["deleteCount"] == 2, str(p["deleteCount"]))
check("C1b yang dihapus tepat baris 2 & 4",
      sorted(sum(([b["startRow"] + i for i in range(b["count"])] for b in p["blocks"]), [])) == [2, 4])
check("C1c OFF+SAM lama TETAP selamat (dilindungi, tanpa kedaluwarsa)", p["protSam"] == 1)
check("C1d OFF+kosong lama TETAP selamat", p["protBlank"] == 1)
check("C1e OFF+VIRA yang masih hangat selamat", p["keepHangat"] == 2, str(p["keepHangat"]))
check("C1f tanpa jejak waktu -> disimpan & dilaporkan",
      p["keepTanpaJejak"] == 1 and p["noTsRows"] == [8])

# --- C2 skenario yang jadi pemicu v3
data = [row(2, "chat-30-sept", "ON", "", last_reply_ts=NOW - 1 * DAY)]
check("C2 baris yang chat kemarin TIDAK dihapus", plan_cleanup(data, NOW)["deleteCount"] == 0)

# --- C3 sumber umur alternatif (jalur OFF hanya punya buffer_done_ts)
data = [
    row(2, "off-vira-aktif", "OFF", "VIRA", buffer_done_ts=(NOW - 2 * DAY) * 1000),   # ms
    row(3, "off-vira-mati",  "OFF", "VIRA", buffer_done_ts=(NOW - 200 * DAY) * 1000),
]
p = plan_cleanup(data, NOW)
check("C3a buffer_done_ts (milidetik) dinormalkan benar", p["deleteCount"] == 1, str(p["deleteCount"]))
check("C3b yang dihapus baris 3", p["blocks"] == [{"startRow": 3, "count": 1}], str(p["blocks"]))

# --- C4 nilai terbesar yang menang
data = [row(2, "x", "ON", "", last_reply_ts=OLD, kelas_anak_ts=FRESH)]
check("C4 kolom ts terbaru menyelamatkan baris", plan_cleanup(data, NOW)["deleteCount"] == 0)

# --- C5 fallback tanggal manusia
old_str = datetime.datetime.fromtimestamp(OLD, datetime.timezone.utc).strftime("%d/%m/%Y")
new_str = datetime.datetime.fromtimestamp(FRESH, datetime.timezone.utc).strftime("%d/%m/%Y")
data = [row(2, "a", "ON", ""), row(3, "b", "ON", "")]
data[0]["Tanggal Chat Terakhir"] = old_str
data[1]["Tanggal Chat Terakhir"] = new_str
p = plan_cleanup(data, NOW)
check("C5a DD/MM/YYYY lama -> dihapus", p["blocks"] == [{"startRow": 2, "count": 1}], str(p["blocks"]))
check("C5b DD/MM/YYYY baru -> disimpan", p["keepHangat"] == 1)

# --- C6 batas ambang persis
data = [row(2, "tepat", "ON", "", last_reply_ts=NOW - 90 * DAY),
        row(3, "lewat", "ON", "", last_reply_ts=NOW - 90 * DAY - 1)]
p = plan_cleanup(data, NOW)
check("C6 tepat 90 hari = masih disimpan, lewat 1 detik = dihapus",
      p["blocks"] == [{"startRow": 3, "count": 1}], str(p["blocks"]))

# --- C7 guard
for bad, tag in [
    ([{"row_number": 2, "bot_mode": "ON", "last_reply_ts": OLD}], "GUARD_NO_WA"),
    ([{"row_number": 2, "No WA": "a", "last_reply_ts": OLD}], "GUARD_BOT_MODE"),
    ([{"row_number": 2, "No WA": "a", "bot_mode": "ON"}], "GUARD_AGE_COLS"),
]:
    try:
        plan_cleanup(bad, NOW)
        check(f"C7 {tag} throw", False, "tidak throw")
    except ValueError as e:
        check(f"C7 {tag} throw", str(e) == tag, str(e))

check("C8 input kosong -> no-op", plan_cleanup([], NOW) is None)

# --- C9 off_reason belum ada
data = [row(2, "a", "OFF", last_reply_ts=OLD), row(3, "b", "ON", last_reply_ts=OLD)]
p = plan_cleanup(data, NOW)
check("C9a tidak throw", p is not None)
check("C9b semua OFF dilindungi", p["protBlank"] == 1 and p["hasOffReason"] is False)
check("C9c baris ON lama tetap dihapus", p["deleteCount"] == 1)

# ====================================================================
print()
print("=" * 70)
print("D. BLOK PENGHAPUSAN + SIMULASI HAPUS SUNGGUHAN")
print("=" * 70)


def blocks_for(rownums):
    rownums = sorted(rownums)
    bl = []
    for n in rownums:
        if bl and n == bl[-1]["startRow"] + bl[-1]["count"]:
            bl[-1]["count"] += 1
        else:
            bl.append({"startRow": n, "count": 1})
    bl.reverse()
    return bl


check("D1a baris berurutan digabung jadi 1 blok",
      blocks_for([2, 3, 4]) == [{"startRow": 2, "count": 3}], str(blocks_for([2, 3, 4])))
check("D1b baris terpisah jadi blok terpisah, urut MENURUN",
      blocks_for([2, 5, 6, 9]) == [{"startRow": 9, "count": 1}, {"startRow": 5, "count": 2},
                                   {"startRow": 2, "count": 1}], str(blocks_for([2, 5, 6, 9])))
check("D1c semua blok urut menurun",
      all(blocks_for([2, 4, 6, 7, 10])[i]["startRow"] > blocks_for([2, 4, 6, 7, 10])[i + 1]["startRow"]
          for i in range(len(blocks_for([2, 4, 6, 7, 10])) - 1)))


def apply_delete(sheet_labels, blocks):
    """sheet_labels[i] = baris nomor i+2. Terapkan delete per blok, urut apa adanya."""
    body = list(sheet_labels)
    for b in blocks:
        i = b["startRow"] - 2
        del body[i:i + b["count"]]
    return body


def simulate(rows, now):
    p = plan_cleanup(rows, now)
    labels = [r["No WA"] for r in rows]
    if p is None or not p["blocks"]:
        return labels
    return apply_delete(labels, p["blocks"])


rows = [
    row(2,  "keep-hangat", "ON",  "",     last_reply_ts=FRESH),
    row(3,  "del-a",       "ON",  "",     last_reply_ts=OLD),
    row(4,  "del-b",       "ON",  "",     last_reply_ts=OLD),
    row(5,  "prot-sam",    "OFF", "SAM",  last_reply_ts=OLD),
    row(6,  "del-c",       "OFF", "VIRA", last_reply_ts=OLD),
    row(7,  "prot-blank",  "OFF", "",     last_reply_ts=OLD),
    row(8,  "del-d",       "ON",  "",     last_reply_ts=OLD),
    row(9,  "del-e",       "ON",  "",     last_reply_ts=OLD),
    row(10, "keep-nojejak", "ON", ""),
]
out = simulate(rows, NOW)
expect = ["keep-hangat", "prot-sam", "prot-blank", "keep-nojejak"]
check("D2a hasil akhir persis sesuai aturan", out == expect, str(out))
check("D2b urutan baris yang selamat terjaga", out == expect)
check("D2c tidak ada duplikat (tidak ada tahap salin)", len(set(out)) == len(out))

# stress: pola acak, bandingkan dengan hasil yang diharapkan
import random
random.seed(7)
rows = []
for i in range(300):
    mode = random.choice(["ON", "OFF", "OFF", ""])
    reason = random.choice(["", "SAM", "VIRA", "CEK"])
    r = row(i + 2, f"n{i}", mode, reason)
    if random.random() > 0.15:
        r["last_reply_ts"] = NOW - random.randint(1, 300) * DAY
    rows.append(r)
p = plan_cleanup(rows, NOW)
expect = []
for r in rows:
    mode, reason = norm(r["bot_mode"]), norm(r.get("off_reason"))
    if mode == "OFF" and reason != "VIRA":
        expect.append(r["No WA"]); continue
    act = last_activity(r)
    if not act or act >= NOW - 90 * DAY:
        expect.append(r["No WA"])
out = simulate(rows, NOW)
check("D3a 300 baris acak: hasil persis sesuai aturan", out == expect,
      f"len {len(out)} vs {len(expect)}")
check("D3b jumlah blok masuk akal", p["blockCount"] <= p["deleteCount"],
      f"{p['blockCount']} blok untuk {p['deleteCount']} baris")
check("D3c total kekal: sisa + dihapus = total",
      len(out) + p["deleteCount"] == p["totalDataRows"])

# ====================================================================
print()
print("=" * 70)
print("E. REGRESI vs v2")
print("=" * 70)


def plan_v2_keep(rows):
    return {r["No WA"] for r in rows
            if norm(r["bot_mode"]) == "OFF" and norm(r.get("off_reason")) != "VIRA"}


rows = [
    row(2, "chat-30-sept", "ON",  "",     last_reply_ts=NOW - 1 * DAY),
    row(3, "sam",          "OFF", "SAM",  last_reply_ts=OLD),
    row(4, "usang",        "ON",  "",     last_reply_ts=OLD),
    row(5, "vira-baru",    "OFF", "VIRA", last_reply_ts=NOW - 2 * DAY),
]
v2 = plan_v2_keep(rows)
v3 = set(simulate(rows, NOW))
check("E1 v2 menghapus baris yang baru chat kemarin", "chat-30-sept" not in v2)
check("E2 v3 menyelamatkannya", "chat-30-sept" in v3)
check("E3 v3 superset dari v2", v2 <= v3, str(sorted(v2 - v3)))
check("E4 baris usang tetap dihapus di v3", "usang" not in v3)
check("E5 OFF+VIRA yang masih hangat selamat di v3 (beda dari v2)",
      "vira-baru" in v3 and "vira-baru" not in v2)

# ====================================================================
print()
print("=" * 70)
print("F. DATA STATS NYATA")
print("=" * 70)

try:
    import openpyxl
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["STATS"]
    it = ws.iter_rows(values_only=True)
    hdr = [str(h).strip() if h is not None else "" for h in next(it)]
    real = []
    rn = 2
    for r in it:
        if any(c is not None and str(c).strip() != "" for c in r):
            d = {hdr[i]: r[i] for i in range(min(len(hdr), len(r)))}
            d["row_number"] = rn
            real.append(d)
        rn += 1

    check("F1 snapshot terbaca", len(real) > 0, f"{len(real)} baris data")
    check("F2 kolom off_reason memang belum ada di snapshot ini",
          "off_reason" not in hdr)

    now_real = max((last_activity(r) for r in real), default=0)
    p = plan_cleanup(real, now_real)
    print(f"\n  (now = aktivitas termuda di snapshot = "
          f"{datetime.datetime.fromtimestamp(now_real, datetime.timezone.utc):%Y-%m-%d})")
    print(f"  total {p['totalDataRows']} | simpan {p['keepCount']} | hapus {p['deleteCount']} "
          f"dalam {p['blockCount']} blok")
    print(f"  dilindungi: SAM {p['protSam']}, kosong {p['protBlank']}, lain {p['protOther']}")
    print(f"  hangat {p['keepHangat']} | tanpa jejak {p['keepTanpaJejak']}")

    check("F3 tidak ada baris OFF yang ikut terhapus",
          all(norm(r["bot_mode"]) != "OFF"
              for r in real
              if r["row_number"] in {b["startRow"] + i for b in p["blocks"] for i in range(b["count"])}))
    check("F4 baris tanpa jejak waktu semuanya selamat",
          p["keepTanpaJejak"] == sum(1 for r in real
                                     if norm(r["bot_mode"]) != "OFF" and not last_activity(r)))
    labels = [str(r.get("No WA")) for r in real]
    out = apply_delete(labels, p["blocks"]) if p["blocks"] else labels
    check("F5 simulasi hapus: sisa = keepCount", len(out) == p["keepCount"],
          f"{len(out)} vs {p['keepCount']}")
    check("F6 blok tidak keluar rentang sheet",
          all(b["startRow"] >= 2 and b["startRow"] + b["count"] - 1 <= real[-1]["row_number"]
              for b in p["blocks"]))
except ImportError:
    print("  (openpyxl tidak ada - bagian F dilewati)")
except FileNotFoundError:
    print("  (snapshot xlsx tidak ditemukan - bagian F dilewati)")

# ====================================================================
print()
print("=" * 70)
print(f"HASIL: {len(PASS)} PASS, {len(FAIL)} FAIL")
for f in FAIL:
    print("  FAIL:", f)
print("=" * 70)
sys.exit(1 if FAIL else 0)
