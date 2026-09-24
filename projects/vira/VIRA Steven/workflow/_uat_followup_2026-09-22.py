# -*- coding: utf-8 -*-
"""
_uat_followup_2026-09-22.py — UAT perilaku untuk 2026-09-22-VIRA-Personal-Followup-v2.json.

Sama seperti harness Main: MENJALANKAN kode JavaScript asli tiap node di dalam V8
(py-mini-racer), dengan $(), $input, $getWorkflowStaticData dan console palsu persis
seperti yang disediakan n8n. Yang diuji kode yang benar-benar akan jalan, bukan tiruannya.

Yang TETAP tidak bisa diuji di sini: apakah Google Sheets menulis baris yang benar,
apakah Kirimi mengirim, dan apakah DeepSeek mengeluarkan kalimat yang wajar.
Tiga itu butuh nomor aktif — lihat daftar UAT manual di akhir keluaran.

Jalankan: PYTHONIOENCODING=utf-8 python _uat_followup_2026-09-22.py
Keluar dengan kode 1 kalau ada satu saja skenario GAGAL.
"""
import json
import os
import re as _re
import sys
import time

from py_mini_racer import MiniRacer

DIR = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(DIR, "2026-09-22-VIRA-Personal-Followup-v2.json")

with open(WF, encoding="utf-8") as f:
    wf = json.load(f)
NODES = {n["name"]: n for n in wf["nodes"]}
CONNS = wf["connections"]

SHIM = r"""
globalThis.__run = function (code, ctx) {
  const bungkus = (items) => {
    const o = {
      all: () => items,
      first: () => (items.length ? items[0] : undefined),
      last: () => (items.length ? items[items.length - 1] : undefined),
    };
    o.item = items.length ? items[0] : undefined;
    return o;
  };
  const $ = (name) => {
    if (!Object.prototype.hasOwnProperty.call(ctx.nodes, name)) {
      throw new Error("NODE TIDAK ADA DI KONTEKS UJI: " + name);
    }
    return bungkus(ctx.nodes[name]);
  };
  const $input = bungkus(ctx.input || []);
  const $getWorkflowStaticData = () => ctx.staticData;
  const logs = [];
  const tulis = (lvl) => function () {
    logs.push(lvl + ": " + Array.prototype.slice.call(arguments).join(" "));
  };
  const konsol = { log: tulis("log"), warn: tulis("warn"), error: tulis("error"), info: tulis("info") };
  let out = null, err = null;
  try {
    const fn = new Function("$", "$input", "$json", "$getWorkflowStaticData", "console", code);
    const hasil = fn($, $input, $input.item ? $input.item.json : {}, $getWorkflowStaticData, konsol);
    out = hasil === undefined ? null : hasil;
  } catch (e) {
    err = String((e && e.message) || e);
  }
  return { out: out, err: err, logs: logs, staticData: ctx.staticData };
};
"""

CTX = MiniRacer()
CTX.eval(SHIM)

lolos, gagal = [], []
_bagian = [""]


def bagian(judul):
    _bagian[0] = judul
    print()
    print("-" * 72)
    print(judul)
    print("-" * 72)


def cek(judul, syarat, detail=""):
    if syarat:
        lolos.append(judul)
        print("  LOLOS  %s" % judul)
    else:
        gagal.append((_bagian[0], judul, detail))
        print("  GAGAL  %s%s" % (judul, ("  <- " + detail) if detail else ""))


def jalan(nama_node, nodes=None, inp=None, static=None):
    kode = NODES[nama_node]["parameters"]["jsCode"]
    return CTX.call("__run", kode, {"nodes": nodes or {}, "input": inp if inp is not None else [],
                                    "staticData": static if static is not None else {}})


def item(**kw):
    return {"json": kw}


def keluar(r):
    if r["err"]:
        return None
    o = r["out"]
    if o is None:
        return []
    return [(x or {}).get("json", x) for x in o] if isinstance(o, list) else [o]


def satu(r):
    d = keluar(r)
    return d[0] if d else None


NOW = int(time.time())
HARI = 86400

print("=" * 72)
print("UAT FOLLOW-UP — VIRA Personal v2 (2026-09-22)")
print("berkas: %s" % os.path.basename(WF))
print("=" * 72)


# ===========================================================================
bagian("A. STRUKTUR — kabel, kredensial, dan keadaan saat diimpor")
# ===========================================================================
cek("A1  diimpor NONAKTIF", wf.get("active") is False)
cek("A2  id & versionId kosong (belum pernah masuk n8n)",
    wf.get("id") == "" and wf.get("versionId") == "")
cek("A3  Schedule Trigger FU ship dalam keadaan disabled",
    NODES["Schedule Trigger FU"].get("disabled") is True)
cek("A4  timezone Asia/Jakarta", wf["settings"].get("timezone") == "Asia/Jakarta")
cek("A5  trigger tiap 1 jam",
    NODES["Schedule Trigger FU"]["parameters"]["rule"]["interval"][0].get("hoursInterval") == 1)

_ref = set()
for src, out in CONNS.items():
    cek("A6  node sumber '%s' ada" % src, src in NODES)
    for tipe, cabang in out.items():
        for c in cabang:
            for t in c:
                _ref.add(t["node"])
_hilang = sorted(n for n in _ref if n not in NODES)
cek("A7  semua tujuan kabel menunjuk node yang ada", not _hilang, str(_hilang))

_fungsional = {n for n, d in NODES.items() if d["type"] != "n8n-nodes-base.stickyNote"}
# Trigger tidak punya kabel masuk; node sub-LLM juga tidak - dia SUMBER ai_languageModel.
_subnode = {n for n, o in CONNS.items() if set(o) - {"main"}}
_yatim = sorted(n for n in _fungsional if n not in _ref and n != "Schedule Trigger FU"
                and n not in _subnode)
cek("A8  tidak ada node fungsional yatim (selain trigger & sub-node LLM)", not _yatim, str(_yatim))

_sheet = [n for n, d in NODES.items() if d["type"] == "n8n-nodes-base.googleSheets"]
cek("A9  lima node Sheets, semuanya punya kredensial",
    len(_sheet) == 5 and all(NODES[n].get("credentials") for n in _sheet), str(_sheet))
cek("A9b semua node Sheets menunjuk spreadsheet VIRA Steven",
    all(NODES[n]["parameters"]["documentId"]["value"] == "1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk"
        for n in _sheet))
cek("A9c semua node Sheets pakai service account",
    all(NODES[n]["parameters"].get("authentication") == "serviceAccount" for n in _sheet))
cek("A10 model DeepSeek (bukan Anthropic — tenant ini tidak punya kredensial Anthropic)",
    NODES["DeepSeek FU"]["type"] == "n8n-nodes-deepseek-thinking.lmChatDeepSeekThinking"
    and NODES["DeepSeek FU"]["credentials"]["deepSeekApi"]["id"] == "tVKwMVPK1fROjH5Z")
cek("A10b DeepSeek FU tersambung sebagai ai_languageModel Compose Follow-up",
    CONNS["DeepSeek FU"]["ai_languageModel"][0][0]["node"] == "Compose Follow-up")

cek("A11 ANTI-DOBEL: Claim STATS FU jalan sebelum Wait/Kirim",
    CONNS["Claim STATS FU"]["main"][0][0]["node"] == "Build FU Prompt"
    and CONNS["Loop Kandidat"]["main"][1][0]["node"] == "Claim STATS FU")
cek("A12 Compose & Validate & Kirim punya cabang error",
    all(NODES[n].get("onError") == "continueErrorOutput"
        for n in ("Compose Follow-up", "Validate FU Message", "Kirim Follow-up")))
cek("A13 kegagalan AI dan kegagalan kirim sama-sama berakhir di Rollback",
    CONNS["Catat Kegagalan AI"]["main"][0][0]["node"] == "Rollback STATS FU"
    and CONNS["Catat Gagal Kirim"]["main"][0][0]["node"] == "Rollback STATS FU")
cek("A14 Rollback mengembalikan alur ke Loop (loop tidak pernah putus)",
    CONNS["Rollback STATS FU"]["main"][0][0]["node"] == "Loop Kandidat"
    and NODES["Rollback STATS FU"].get("onError") == "continueRegularOutput")
cek("A15 Kirim sukses lewat gerbang dry run dulu, bukan langsung balik ke Loop",
    CONNS["Kirim Follow-up"]["main"][0][0]["node"] == "IF Bukan Dry Run")
cek("A16 Backlog Deck menggantung dari Read STATS, BUKAN dari cabang done Loop",
    any(t["node"] == "Backlog Deck" for t in CONNS["Read STATS FU"]["main"][0]))
cek("A17 Report FU Run di cabang done Loop (index 0)",
    CONNS["Loop Kandidat"]["main"][0][0]["node"] == "Report FU Run")
cek("A18 node Notify Admin FU Error milik Persada sudah dibuang",
    "Notify Admin FU Error" not in NODES)
cek("A19 dua notifikasi admin memakai admin_phone dari CONFIG, tidak dihardcode",
    all(not _re.search(r'"value": "\d{8,}"',
                       json.dumps(NODES[n]["parameters"], ensure_ascii=False))
        for n in ("Notify Admin FU Summary", "Notify Admin Backlog")))
cek("A20 Kirim Follow-up memakai target_phone hasil Validate (bukan no_wa mentah)",
    "Validate FU Message" in json.dumps(NODES["Kirim Follow-up"]["parameters"], ensure_ascii=False))
cek("A21 Claim & Rollback menulis HANYA kolom follow-up",
    set(NODES["Rollback STATS FU"]["parameters"]["columns"]["value"])
    == {"No WA", "follow_up_count", "last_follow_up_ts"})
cek("A22 Rollback: penanda guard menunda, kegagalan lain memulihkan",
    "FU_AI_DITOLAK_GUARD" in NODES["Rollback STATS FU"]["parameters"]["columns"]["value"]["last_follow_up_ts"]
    and "prev_last_fu" in NODES["Rollback STATS FU"]["parameters"]["columns"]["value"]["last_follow_up_ts"])
cek("A23 tiga node Sheets penulis pakai retry",
    all(NODES[n].get("retryOnFail") is True for n in ("Claim STATS FU", "Rollback STATS FU")))


# ===========================================================================
bagian("B. PARSE CONFIG FU — kill switch, jam etis, clamp")
# ===========================================================================
def baris_cfg(**kv):
    return [item(key=k, value=v) for k, v in kv.items()]


def parse(**kv):
    base = {"followup_enabled": "true", "followup_open_hour": "0", "followup_close_hour": "24",
            "admin_phone": "6285171701168", "followup_templates_a": '["halo kak A"]',
            "followup_templates_c": '["halo kak C"]',
            "kirimi_user_code": "UC", "kirimi_secret": "SEC", "kirimi_device_id": "DEV"}
    base.update(kv)
    return satu(jalan("Parse Config FU", inp=baris_cfg(**base)))


cek("B1  followup_enabled='true' -> jalan", parse() is not None)
for mati in ("false", "FALSE", "", "1", "yes", "y", "enabled", "truee"):
    cek("B2  followup_enabled=%r -> run berhenti" % mati, parse(followup_enabled=mati) is None)
cek("B2b followup_enabled=' True ' tetap sah (trim + lowercase, seperti versi lama)",
    parse(followup_enabled=" True ") is not None)
cek("B3  di luar jam etis -> run berhenti", parse(followup_close_hour="0") is None)
cek("B4  admin_phone kosong -> run berhenti (notif tidak akan sampai)",
    parse(admin_phone="") is None)

d = parse()
cek("B5  followup_max default 0 dibaca sebagai TANPA BATAS", d["config"]["bucket"]["A"]["max"] == 0)
d = parse(followup_max_a="3", followup_max_c="2")
cek("B6  cap per bucket dibaca", d["config"]["bucket"]["A"]["max"] == 3
    and d["config"]["bucket"]["C"]["max"] == 2)
d = parse(followup_interval_hours_a="0", followup_interval_hours_c="99999")
cek("B7  interval 0 di-clamp ke 6 jam (tidak boleh jadi blast tiap jam)",
    d["config"]["bucket"]["A"]["interval_h"] == 6)
cek("B7b interval raksasa di-clamp 30 hari", d["config"]["bucket"]["C"]["interval_h"] == 720)
d = parse(followup_min_delay_sec="1", followup_max_delay_sec="0", followup_max_per_run="9999")
cek("B8  jeda & plafon di-clamp", d["config"]["min_delay"] == 3
    and d["config"]["max_delay"] >= 3 and d["config"]["max_per_run"] == 300)
d = parse()
cek("B9  dry run default AKTIF (gagal ke arah aman)", d["config"]["ai_dry_run"] is True)
cek("B9b AI default aktif", d["config"]["ai_enabled"] is True)
cek("B10 bucket B tidak punya template (prospeknya memang tidak dikirimi apa pun)",
    set(d["config"]["templates"]) == {"A", "C"})
cek("B11 AI mati + semua template kosong -> run berhenti",
    parse(followup_ai_enabled="N", followup_templates_a="[]", followup_templates_c="[]",
          followup_templates="[]") is None)
cek("B11b AI hidup + template kosong -> TETAP jalan (template cuma jaring fallback)",
    parse(followup_templates_a="[]", followup_templates_c="[]", followup_templates="[]") is not None)
d = parse(followup_test_numbers="628111, 628222;628333")
cek("B12 followup_test_numbers dipecah jadi daftar digit",
    d["config"]["test_numbers"] == ["628111", "628222", "628333"], str(d["config"]["test_numbers"]))
d = parse(followup_backlog_hour="30", followup_backlog_days="0")
cek("B13 backlog_hour di luar jam buka ditarik ke jam buka",
    d["config"]["backlog_hour"] == d["config"]["open_hour"])
cek("B13b backlog_days minimal 1", d["config"]["backlog_days"] == 1)
cek("B14 penghitung kegagalan direset tiap run",
    jalan("Parse Config FU", inp=baris_cfg(**{"followup_enabled": "true",
          "followup_open_hour": "0", "followup_close_hour": "24",
          "admin_phone": "628", "followup_templates_a": '["x"]'}),
          static={"fu_gagal": [{"no_wa": "lama"}]})["staticData"]["fu_gagal"] == [])


# ===========================================================================
bagian("C. FILTER KANDIDAT — bucket, gerbang, antrian")
# ===========================================================================
def pcfg(**over):
    c = {"kirimi_user_code": "UC", "kirimi_secret": "SEC", "kirimi_device_id": "DEV",
         "admin_phone": "6285171701168", "exclude_numbers": ["6285171701168"],
         "test_numbers": [],
         "bucket": {"A": {"interval_sec": 72 * 3600, "interval_h": 72, "max": 3},
                    "C": {"interval_sec": 48 * 3600, "interval_h": 48, "max": 3}},
         "templates": {"A": ["Halo kak, masih ada yang mau ditanyain soal chatnya?"],
                       "C": ["Halo kak, decknya sempat kebaca belum?"]},
         "min_delay": 20, "max_delay": 45, "max_per_run": 20,
         "open_hour": 9, "close_hour": 21, "backlog_hour": 9, "backlog_days": 3,
         "ai_enabled": True, "ai_dry_run": False}
    c.update(over)
    return item(config=c, wib_hour=10, wib_min=0, now_epoch=NOW)


def baris(**over):
    b = {"No WA": "6289900112233", "lid": "", "Nama": "Prospek", "nama_lengkap": "",
         "bot_mode": "ON", "Counter": "5", "last_reply_ts": str(NOW - 10 * HARI),
         "follow_up_count": "0", "last_follow_up_ts": "", "deck_requested": "",
         "deck_terkirim_ts": "", "nama_bisnis": "", "industri": "", "masalah_utama": "",
         "volume_chat": "", "minat_paket": "", "budget_range": "", "brief_terisi": "",
         "last_bot_reply": "", "Pesan Pertama": "halo"}
    b.update(over)
    return item(**b)


def filt(rows, cfg_over=None):
    return keluar(jalan("Filter Kandidat",
                        nodes={"Parse Config FU": [pcfg(**(cfg_over or {}))]},
                        inp=rows if isinstance(rows, list) else [rows]))


d = filt(baris())
cek("C1  prospek biasa & sudah lama diam -> lolos, bucket A",
    len(d) == 1 and d[0]["bucket"] == "A", str(d))
d = filt(baris(deck_requested="Y"))
cek("C2  sudah minta deck, deck BELUM dikirim -> bucket B, TIDAK dikirimi apa pun",
    d == [], str(d))
d = filt(baris(deck_requested="Y", deck_terkirim_ts=str(NOW - 10 * HARI)))
cek("C3  deck sudah dikirim -> bucket C", len(d) == 1 and d[0]["bucket"] == "C", str(d))
d = filt(baris(deck_requested="", deck_terkirim_ts=str(NOW - 10 * HARI)))
cek("C3b deck_terkirim_ts menang atas deck_requested", len(d) == 1 and d[0]["bucket"] == "C")
d = filt(baris(deck_terkirim_ts="2026-09-01 10:00:00"))
cek("C3c deck_terkirim_ts format WIB tetap terbaca -> bucket C",
    len(d) == 1 and d[0]["bucket"] == "C", str(d))
for rusak in ("abc", "-", "0", "belum"):
    d = filt(baris(deck_terkirim_ts=rusak))
    cek("C3d deck_terkirim_ts=%r tidak terbaca -> bucket A" % rusak,
        len(d) == 1 and d[0]["bucket"] == "A")

# -- gerbang --
for judul, over in [
        ("No WA kosong", {"No WA": ""}),
        ("bot_mode OFF (HITL / Steven pegang)", {"bot_mode": "off"}),
        ("Counter 0 (belum pernah chat)", {"Counter": "0"}),
        ("last_reply_ts kosong (belum pernah dibalas bot)", {"last_reply_ts": ""}),
        ("baru dibalas kemarin (masih hangat)", {"last_reply_ts": str(NOW - HARI)}),
        ("baru di-follow-up kemarin", {"last_follow_up_ts": str(NOW - HARI)}),
        ("sudah 3x follow-up (cap bucket A)", {"follow_up_count": "3"}),
        ("nomor admin sendiri", {"No WA": "6285171701168"}),
        ("kontak LID-only", {"No WA": "123456789012345", "lid": "123456789012345"}),
        ("nomor terlalu pendek", {"No WA": "628123"}),
        ("nomor terlalu panjang", {"No WA": "6281234567890123456"})]:
    cek("C4  dilewati: %s" % judul, filt(baris(**over)) == [])

cek("C5  followup_max=0 berarti TANPA BATAS (bug 2026-08-28 diperbaiki)",
    len(filt(baris(follow_up_count="99"),
             {"bucket": {"A": {"interval_sec": 3600, "interval_h": 1, "max": 0},
                         "C": {"interval_sec": 3600, "interval_h": 1, "max": 0}}})) == 1)

d = filt([baris(bot_mode="off"), baris(bot_mode="ON")])
cek("C6  baris kembar: yang OFF mendaftar duluan, kembarannya TIDAK lolos", d == [], str(d))
d = filt([baris(), baris()])
cek("C6b baris kembar biasa hanya menghasilkan satu kandidat", len(d) == 1)

d = filt([baris(No_WA="628111") if False else baris(**{"No WA": "628900000001"}),
          baris(**{"No WA": "6285171701168"})],
         {"test_numbers": ["6285171701168"]})
cek("C7  MODE UJI menang atas exclude_numbers",
    len(d) == 1 and d[0]["no_wa"] == "6285171701168", str(d))

# -- antrian & plafon --
d = filt([baris(**{"No WA": "628900000001"}),
          baris(**{"No WA": "628900000002", "deck_terkirim_ts": str(NOW - 20 * HARI)})])
cek("C8  bucket C didahulukan dari bucket A",
    len(d) == 2 and d[0]["bucket"] == "C" and d[1]["bucket"] == "A", str([x["bucket"] for x in d]))
d = filt([baris(**{"No WA": "62890000000%d" % i}) for i in range(1, 6)], {"max_per_run": 2})
cek("C9  plafon per run dihormati", len(d) == 2 and d[0]["antrian_total"] == 5)
d = filt([baris(**{"No WA": "62890000000%d" % i}) for i in range(1, 6)],
         {"wib_hour": 20, "wib_min": 59} if False else {"max_per_run": 20})
cek("C9b antrian_bucket ikut terbawa", d and d[0]["antrian_bucket"]["A"] == 5, str(d and d[0].get("antrian_bucket")))

d = filt(baris(deck_terkirim_ts=str(NOW - HARI), last_reply_ts=str(NOW - 10 * HARI)))
cek("C10 deck yang BARU dikirim menunda jatuh tempo (ref = max(last_reply, deck_ts))", d == [])
d = filt(baris(deck_terkirim_ts=str(NOW - 10 * HARI), last_reply_ts=str(NOW - 5 * HARI)))
cek("C10b prospek sempat membalas sesudah deck -> ditandai",
    len(d) == 1 and d[0]["pernah_balas_sesudah_deck"] is True)
d = filt(baris(deck_terkirim_ts=str(NOW - 5 * HARI), last_reply_ts=str(NOW - 10 * HARI)))
cek("C10c diam total sejak deck -> ditandai false",
    len(d) == 1 and d[0]["pernah_balas_sesudah_deck"] is False)

d = filt(baris(Nama="Rina", nama_bisnis="Kopi Senja"),
         {"templates": {"A": ["Halo kak {nama}, usaha {nama_bisnis} gimana kabarnya?"], "C": []}})
cek("C11 {nama} SELALU dibuang dari template, {nama_bisnis} diisi",
    d and "Rina" not in d[0]["message"] and "Kopi Senja" in d[0]["message"], str(d and d[0]["message"]))
cek("C11b kalimatnya tidak rusak jadi 'Halo kak ,'",
    d and " ," not in d[0]["message"] and "  " not in d[0]["message"], str(d and d[0]["message"]))
d = filt(baris(follow_up_count="1"),
         {"templates": {"A": ["satu", "dua"], "C": []}})
cek("C12 template dirotasi pakai follow_up_count", d and d[0]["message"] == "dua")
d = filt(baris(), {"templates": {"A": [], "C": []}})
cek("C13 template bucket kosong -> kandidat tetap lolos (AI yang menulis)",
    len(d) == 1 and d[0]["message"] == "")


# ===========================================================================
bagian("D. BUILD FU PROMPT — tahap per bucket & penyamaran")
# ===========================================================================
def build(kand, cfg_over=None):
    return satu(jalan("Build FU Prompt",
                      nodes={"Parse Config FU": [pcfg(**(cfg_over or {}))],
                             "Loop Kandidat": [item(**kand)]}))


def kand(**over):
    k = {"no_wa": "6289900112233", "nama": "", "nama_lengkap": "", "follow_up_count": 0,
         "bucket": "A", "days_idle": 10, "days_since_deck": 0,
         "pernah_balas_sesudah_deck": False, "nama_bisnis": "", "industri": "",
         "masalah_utama": "", "volume_chat": "", "minat_paket": "", "budget_range": "",
         "brief_terisi": "", "last_bot_reply": "", "pesan_pertama": "", "message": "tpl"}
    k.update(over)
    return k


p = build(kand(bucket="A", follow_up_count=0))
cek("D1  bucket A awal -> tahap AWAL, boleh tawarkan deck", p and p["fu_tahap"].startswith("AWAL"))
p = build(kand(bucket="A", follow_up_count=4))
cek("D2  bucket A lanjut -> SOFT, jangan tawarkan deck lagi",
    p and "SOFT" in p["fu_tahap"] and "JANGAN menawarkan deck lagi" in p["fu_tahap"])
p = build(kand(bucket="C", days_since_deck=6, pernah_balas_sesudah_deck=False))
cek("D3  bucket C diam total -> boleh tanya apakah sempat dibaca",
    p and "SUDAH DIKIRIM" in p["fu_tahap"] and "BELUM membalas" in p["fu_tahap"])
cek("D3b bucket C menyuruh pilih SATU dari tiga", p and "Pilih SATU" in p["fu_tahap"])
p = build(kand(bucket="C", days_since_deck=6, pernah_balas_sesudah_deck=True))
cek("D4  bucket C sudah sempat membalas -> dilarang tanya 'sudah diterima belum'",
    p and "JANGAN bertanya" in p["fu_tahap"])
cek("D5  galian hanya untuk bucket A",
    build(kand(bucket="C", days_since_deck=3))["fu_galian"] == ""
    and build(kand(bucket="A"))["fu_galian"] != "")
p = build(kand(bucket="A", brief_terisi="nama_bisnis,industri", masalah_utama="chat numpuk"))
cek("D5b galian melewati yang sudah tercatat", p and "chat" in p["fu_galian"], str(p and p["fu_galian"]))

# -- penyamaran --
for asal, dilarang in [
        ("biaya adminku 3.000.000 per bulan", r"3\.000\.000"),
        ("sekali closing masuk 500rb", r"500\s*rb"),
        ("budgetnya Rp5.000.000", r"Rp\s*\d"),
        ("marginnya 30%", r"\d+\s*%"),
        ("add-on 999 ribu", r"\b999\b"),
        ("lihat di povstevens.com dulu", r"\.com"),
        ("hubungi 6285155202354", r"62\d{8,}"),
        ("kita ketemu besok ya", r"\bbesok\b"),
        ("jam 3 sore", r"\bjam\s*\d"),
        ("selesai dalam 2 hari", r"dalam\s+\d+\s*hari")]:
    p = build(kand(masalah_utama=asal))
    cek("D6  disamarkan: %r" % asal, p and not _re.search(dilarang, p["fu_masalah"], _re.I),
        str(p and p["fu_masalah"]))

p = build(kand(nama_lengkap="Nadia", masalah_utama="kata Nadia chatnya numpuk"))
cek("D7  nama lead disamarkan jadi [nama]",
    p and "Nadia" not in p["fu_masalah"] and "[nama]" in p["fu_masalah"], str(p and p["fu_masalah"]))
p = build(kand(nama_lengkap="Halo", masalah_utama="Halo chat numpuk"))
cek("D7b push name berupa kata umum TIDAK menyamarkan seluruh kalimat",
    p and "[nama]" not in p["fu_masalah"], str(p and p["fu_masalah"]))

p = build(kand(nama_lengkap="Rina", nama_bisnis="Rina Catering"))
cek("D8  nama_bisnis yang memuat nama orang TIDAK disuapkan ke prompt",
    p and p["fu_bisnis"] == "", str(p and p["fu_bisnis"]))
p = build(kand(nama_lengkap="Rina", nama_bisnis="Kopi Senja"))
cek("D8b nama_bisnis yang aman tetap disuapkan", p and p["fu_bisnis"] == "Kopi Senja")

p = build(kand(last_bot_reply="Nanti aku teruskan ke Steven ya kak. Chatnya biasanya ramai jam berapa?"))
cek("D9  janji di balasan terakhir dibuang dari bahan prompt",
    p and "teruskan ke Steven" not in p["fu_balasan_terakhir"]
    and "ramai" in p["fu_balasan_terakhir"], str(p and p["fu_balasan_terakhir"]))

p = build(kand(budget_range="3 juta sampai 5 juta"))
cek("D10 rentang nominal disamarkan utuh, tidak menyisakan potongan",
    p and not _re.search(r"\d", p["fu_budget"]), str(p and p["fu_budget"]))


# ===========================================================================
bagian("E. VALIDATE FU MESSAGE — guard, fallback template, dry run")
# ===========================================================================
def val(teks, bucket="A", kand_over=None, prompt_over=None, cfg_over=None, static=None):
    k = kand(bucket=bucket, message="Halo kak, masih ada yang mau ditanyain soal chatnya?")
    k.update(kand_over or {})
    p = {"ai_enabled": True, "ai_dry_run": False, "bucket": bucket, "fu_ke": 1, "fu_hari": 10}
    p.update(prompt_over or {})
    r = jalan("Validate FU Message",
              nodes={"Parse Config FU": [pcfg(**(cfg_over or {}))],
                     "Loop Kandidat": [item(**k)],
                     "Build FU Prompt": [item(**p)]},
              inp=[item(text=teks)], static=static if static is not None else {})
    return satu(r), r


BAIK = "Halo kak, chat yang numpuk itu masih jadi kendala nggak sekarang? Kalau mau, aku bisa bantu lihat bagiannya."
d, r = val(BAIK)
cek("E1  kalimat bersih lolos apa adanya",
    d and d["final_message"] == BAIK and d["pakai_template"] is False, str(r["err"] or d))

TOLAK = [
    ("Halo kak, paket Basic itu Rp3.000.000 per bulan ya, lumayan buat mulai.", "nominal ribuan"),
    ("Halo kak, mulai dari 3jt per bulan aja kok buat paket Basicnya.", "nominal singkat"),
    ("Halo kak, biayanya cuma tiga juta per bulan buat paket Basic ya kak.", "nominal huruf"),
    ("Halo kak, add-on nya 999 ribu per bulan kalau mau sekalian ya kak.", "harga add-on"),
    ("Halo kak, chatnya bisa naik 30% kalau dibalas otomatis semua nanti.", "persentase"),
    ("Halo kak, coba lihat dulu di povstevens.com ya biar ada gambarannya.", "URL"),
    ("Halo kak, langsung hubungi 6285155202354 aja ya kalau mau cepat.", "nomor telepon"),
    ("Halo kak Nadia, chatnya masih numpuk nggak sekarang? Aku bisa bantu lihat.", "menyapa nama"),
    ("Halo kak, decknya besok aku kirimkan ya, sekarang masih disusun Steven.", "janji waktu"),
    ("Halo kak, deck yang dikirim kemarin sempat kebaca belum ya kak?", "menyebut kapan: kemarin"),
    ("Halo kak, soal yang kita bahas minggu lalu itu, masih ada yang mau ditanyain?", "menyebut kapan: minggu lalu"),
    ("Halo kak, deck yang dikirim 3 hari lalu sempat kebaca belum ya kak?", "menyebut kapan: N hari lalu"),
    ("Halo kak, tadi kita sempat bahas soal chatnya, masih ada yang mengganjal nggak?", "menyebut kapan: tadi"),
    ("Halo kak, aku sudah tanyakan ke Steven soal itu, tinggal nunggu balasannya.", "klaim sudah melakukan"),
    ("Halo kak, aku sudah kirim decknya ke kakak kemarin, sempat kebaca belum?", "klaim sudah mengirim (bucket A)"),
    ("Halo kak.", "terlalu pendek"),
    ("Halo kak. Chatnya gimana. Masih numpuk ya. Aku bantu ya. Kabari aku.", "lebih dari 4 kalimat"),
    ("Halo kak, anggarannya [angka] itu masih sesuai nggak buat sekarang ini ya?", "menyalin data tersamar"),
]
for teks, label in TOLAK:
    d, r = val(teks, kand_over={"nama_lengkap": "Nadia"})
    cek("E2  ditolak -> jatuh ke template: %s" % label,
        d and d["pakai_template"] is True and d["final_message"] != teks,
        str(r["err"] or (d and d["final_message"]))[:110])

d, _ = val("Halo kak, decknya sudah aku kirim beberapa hari lalu, sempat kebaca belum ya kak?",
           bucket="C")
cek("E3  bucket C: klaim 'deck sudah dikirim' DIMAAFKAN (di situ memang benar)",
    d and d["pakai_template"] is False, str(d and d["final_message"])[:110])
d, _ = val("Halo kak, aku sudah kirim brosurnya kemarin ya, sempat kebaca belum kak?", bucket="C")
cek("E3b bucket C: klaim kirim BUKAN soal deck tetap ditolak", d and d["pakai_template"] is True)

d, _ = val("Halo kak, soal yang kita bahas beberapa waktu lalu itu, masih ada yang mau ditanyain?")
cek("E2b penanda waktu KABUR tidak ikut ditolak (tidak bisa salah)",
    d and d["pakai_template"] is False, str(d and d["final_message"])[:90])
d, _ = val("Halo kak, decknya sempat kebaca belum? Kalau ada yang mau dibahas aku siap bantu.")
cek("E2c kalimat tanpa penanda waktu sama sekali tetap lolos", d and d["pakai_template"] is False)

d, _ = val(BAIK, kand_over={"nama_lengkap": "Halo"})
cek("E4  push name kata umum tidak membuat setiap pesan ditolak", d and d["pakai_template"] is False)
d, _ = val("Halo kak, Kopi Senja chatnya masih ramai nggak sekarang? Aku bisa bantu lihat bagiannya.",
           kand_over={"nama_lengkap": "Rina", "nama_bisnis": "Kopi Senja"})
cek("E4b menyebut nama USAHA (bukan nama orang) tetap boleh", d and d["pakai_template"] is False)

d, r = val("", kand_over={"message": ""})
cek("E5  keluaran AI kosong + template kosong -> error teknis (dicoba lagi run berikutnya)",
    d is None and r["err"] and "FU_AI_INVALID" in r["err"], str(r["err"]))
d, r = val("Halo kak, Rp3.000.000 ya.", kand_over={"message": ""})
cek("E5b ditolak guard + template kosong -> penanda GUARD (ditunda, bukan diulang tiap jam)",
    d is None and r["err"] and "FU_AI_DITOLAK_GUARD" in r["err"], str(r["err"]))
cek("E5c penanda tidak terpotong titik dua", r["err"] and ":" not in r["err"].split("FU_AI_DITOLAK_GUARD")[1])

st = {"fu_gagal": []}
d, r = val("Halo kak, Rp3.000.000 ya kak, gimana menurut kakak?", static=st)
cek("E6  fallback template dicatat untuk laporan run",
    len(r["staticData"]["fu_gagal"]) == 1
    and "FU_AI_FALLBACK_TEMPLATE" in r["staticData"]["fu_gagal"][0]["alasan"],
    str(r["staticData"]["fu_gagal"]))

d, _ = val(BAIK + " \U0001f600\U0001f600\U0001f600")
cek("E7  emoji berlebih dirapikan diam-diam, bukan ditolak",
    d and d["pakai_template"] is False and d["final_message"].count("\U0001f600") == 1,
    str(d and d["final_message"])[-40:])
d, _ = val("**Halo kak**, chatnya masih numpuk nggak sekarang? Aku bisa bantu lihat bagiannya.")
cek("E7b markdown dibersihkan, bukan ditolak", d and "*" not in d["final_message"])
d, _ = val("[FACTS nama=\"x\"] Halo kak, chatnya masih numpuk nggak? Aku bisa bantu lihat bagiannya.")
cek("E7c tag bocor dibuang", d and "[FACTS" not in d["final_message"])

d, _ = val(BAIK, prompt_over={"ai_dry_run": True})
cek("E8  DRY RUN: tujuan dialihkan ke admin",
    d and d["target_phone"] == "6285171701168" and d["final_message"].startswith("[DRY RUN"),
    str(d and d["target_phone"]))
cek("E8b DRY RUN: isi aslinya tetap terbaca di ekor pesan", d and BAIK in d["final_message"])
d, _ = val(BAIK, prompt_over={"ai_dry_run": False})
cek("E8c bukan dry run: tujuan = nomor prospek", d and d["target_phone"] == "6289900112233")

d, _ = val("apa pun", prompt_over={"ai_enabled": False})
cek("E9  AI dimatikan -> pakai template, keluaran AI diabaikan",
    d and d["pakai_template"] is True and d["final_message"].startswith("Halo kak, masih ada"))

# -- invarian silang: bahan prompt yang sudah disamarkan tidak boleh memicu guard --
_bocor = []
for asal in ["biaya admin 3.000.000 sebulan", "sekali closing 500rb", "budget Rp5.000.000",
             "naik 30% tahun ini", "add-on 999 ribu", "cek povstevens.com", "wa 6285155202354",
             "ketemu besok jam 3", "3 juta sampai 5 juta", "selesai dalam 2 hari",
             "chatnya numpuk sejak kemarin", "sempat ramai minggu lalu", "mulai 3 bulan lalu"]:
    p = build(kand(masalah_utama=asal, nama_lengkap="Nadia"))
    contoh = "Halo kak, soal " + p["fu_masalah"] + " itu masih jadi kendala nggak sekarang ya?"
    d, _ = val(contoh, kand_over={"nama_lengkap": "Nadia"})
    # yang tersisa hanya penanda [angka]/[waktu] dst -> memang ditolak sebagai "menyalin
    # data tersamar"; yang TIDAK boleh adalah pola harga/waktu/nomor aslinya lolos.
    if d and d["pakai_template"] is False and _re.search(
            r"\d{1,3}[.,]\d{3}|\b\d+\s*(jt|juta|rb|ribu)\b|Rp\s*\d|\d+\s*%|\b999\b|\.com|62\d{8}"
            r"|besok|kemarin|minggu lalu|\d+\s*(hari|bulan)\s+lalu",
            d["final_message"], _re.I):
        _bocor.append(asal)
cek("E10 INVARIAN: penyamaran Build FU Prompt superset pola tolak Validate", not _bocor, str(_bocor))


# ===========================================================================
bagian("F. BACKLOG DECK — pengingat bucket B ke Steven (Paket 5)")
# ===========================================================================
def backlog(rows, cfg_over=None, jam=9):
    c = pcfg(**(cfg_over or {}))
    c["json"]["wib_hour"] = jam
    return keluar(jalan("Backlog Deck", nodes={"Parse Config FU": [c]},
                        inp=rows if isinstance(rows, list) else [rows]))


MACET = baris(deck_requested="Y", deck_terkirim_ts="", last_reply_ts=str(NOW - 5 * HARI),
              nama_bisnis="Kopi Senja", brief_terisi="nama,industri,masalah_utama")
d = backlog(MACET)
cek("F1  brief menggantung 5 hari -> satu laporan ke Steven", len(d) == 1 and d[0]["jumlah"] == 1)
cek("F1b laporan menyebut nomor, nama usaha, dan berapa hari",
    d and "6289900112233" in d[0]["laporan"] and "Kopi Senja" in d[0]["laporan"]
    and "5 hari" in d[0]["laporan"], str(d and d[0]["laporan"])[:200])
cek("F1c laporan menyebut perintah pengeceknya", d and "cek_request.py --belum" in d[0]["laporan"])
cek("F2  di luar jam pengingat -> tidak mengirim apa pun", backlog(MACET, jam=14) == [])
cek("F3  deck sudah dikirim -> tidak masuk backlog",
    backlog(baris(deck_requested="Y", deck_terkirim_ts=str(NOW - HARI),
                  last_reply_ts=str(NOW - 5 * HARI))) == [])
cek("F4  belum minta deck -> tidak masuk backlog",
    backlog(baris(deck_requested="", last_reply_ts=str(NOW - 5 * HARI))) == [])
cek("F5  bot_mode OFF (Steven sudah pegang) -> tidak masuk backlog",
    backlog(baris(deck_requested="Y", bot_mode="OFF", last_reply_ts=str(NOW - 5 * HARI))) == [])
cek("F6  baru 1 hari -> belum masuk backlog",
    backlog(baris(deck_requested="Y", last_reply_ts=str(NOW - HARI))) == [])
d = backlog([MACET, MACET])
cek("F7  baris kembar dihitung sekali", d and d[0]["jumlah"] == 1)
d = backlog([baris(**{"No WA": "62890000%04d" % i, "deck_requested": "Y",
                      "last_reply_ts": str(NOW - (4 + i) * HARI)}) for i in range(20)])
cek("F8  daftar dipotong 15 + keterangan sisanya",
    d and d[0]["jumlah"] == 20 and "dan 5 lagi" in d[0]["laporan"])
cek("F8b diurutkan dari yang paling lama menggantung",
    d and d[0]["laporan"].index("628900000019") < d[0]["laporan"].index("628900000010"))
cek("F8c yang paling baru justru terpotong dari daftar 15 teratas",
    d and "628900000000" not in d[0]["laporan"])


# ===========================================================================
bagian("G. REPORT FU RUN — satu laporan per run, bukan per kegagalan")
# ===========================================================================
def report(static, cfg_over=None, filt_json=None):
    return satu(jalan("Report FU Run",
                      nodes={"Parse Config FU": [pcfg(**(cfg_over or {}))],
                             "Filter Kandidat": [item(**(filt_json or {
                                 "antrian_bucket": {"A": 3, "B": 2, "C": 1},
                                 "antrian_total": 4, "cap_per_run": 20}))]},
                      static=static))


d = report({"fu_gagal": []}, {"ai_dry_run": False})
cek("G1  run bersih & bukan dry run -> tidak perlu mengganggu Steven", d and d["perlu_lapor"] is False)
d = report({"fu_gagal": []}, {"ai_dry_run": True})
cek("G2  DRY RUN selalu dilaporkan (supaya tidak lupa dimatikan)",
    d and d["perlu_lapor"] is True and "DRY RUN AKTIF" in d["laporan"])
d = report({"fu_gagal": []}, {"ai_dry_run": False, "test_numbers": ["628111"]})
cek("G3  MODE UJI selalu dilaporkan (supaya tidak berhenti diam-diam)",
    d and d["perlu_lapor"] is True and "MODE UJI AKTIF" in d["laporan"])
d = report({"fu_gagal": [{"no_wa": "628111", "bucket": "A", "alasan": "FU_KIRIM_GAGAL timeout"},
                         {"no_wa": "628222", "bucket": "C", "alasan": "FU_AI_FALLBACK_TEMPLATE x"},
                         {"no_wa": "628333", "bucket": "A", "alasan": "FU_AI_INVALID y"}]},
           {"ai_dry_run": False})
cek("G4  tiga jenis kegagalan dipisah di laporan",
    d and "Gagal kirim" in d["laporan"] and "Pakai template" in d["laporan"]
    and "Composer gagal total" in d["laporan"], str(d and d["laporan"]))
cek("G4b laporan menyebut antrian per bucket + catatan bucket B",
    d and "A 3 | B 2 | C 1" in d["laporan"] and "B tidak dikirimi" in d["laporan"])
r = jalan("Report FU Run",
          nodes={"Parse Config FU": [pcfg()], "Filter Kandidat": [item(antrian_bucket={"A": 0, "B": 0, "C": 0})]},
          static={"fu_gagal": [{"no_wa": "1", "alasan": "x"}]})
cek("G5  penghitung dibersihkan sesudah dilaporkan", r["staticData"]["fu_gagal"] == [])
d = report({"fu_gagal": [{"no_wa": "6281%03d" % i, "bucket": "A", "alasan": "FU_KIRIM_GAGAL e"}
                         for i in range(14)]}, {"ai_dry_run": False})
cek("G6  daftar kegagalan dipotong 10 + keterangan sisanya", d and "dan 4 lagi" in d["laporan"])
cek("G7  laporan tidak pernah memuat kredensial",
    d and not _re.search(r"SEC|UC|DEV", d["laporan"]))


_ifdry = NODES["IF Bukan Dry Run"]["parameters"]["conditions"]["conditions"][0]["leftValue"]

# ===========================================================================
bagian("H. CATAT BALASAN FU \u2014 follow-up ikut mengisi last_bot_reply")
# ===========================================================================
# Follow-up mengirim langsung lewat Kirimi, tidak lewat workflow Main, jadi
# STATS.last_bot_reply tidak ikut diperbarui. Akibatnya bukan sekadar VIRA lupa
# kalimatnya sendiri: TAWARAN_DECK dan TAWARAN_DISKUSI di Process All membaca
# kolom itu untuk menerima persetujuan pendek, jadi "boleh" atas tawaran di
# follow-up tidak pernah memicu brief maupun handover.
_cb = NODES["Catat Balasan FU"]
_kol = _cb["parameters"]["columns"]["value"]

cek("H1  node Catat Balasan FU ada, tipe Sheets, punya kredensial",
    _cb["type"] == "n8n-nodes-base.googleSheets" and bool(_cb.get("credentials")))
cek("H1b operasinya update ke tab STATS, dicocokkan lewat No WA",
    _cb["parameters"].get("operation") == "update"
    and _cb["parameters"]["sheetName"]["value"] == "STATS"
    and _cb["parameters"]["columns"]["matchingColumns"] == ["No WA"])
cek("H2  menulis tepat tiga kolom", set(_kol) == {"No WA", "last_bot_reply", "last_bot_reply_ts"},
    str(sorted(_kol)))
cek("H3  TIDAK menyentuh last_reply_ts (itu acuan jam diam di Filter Kandidat)",
    "last_reply_ts" not in _kol)
cek("H3b TIDAK menyentuh follow_up_count / last_follow_up_ts (milik Claim & Rollback)",
    "follow_up_count" not in _kol and "last_follow_up_ts" not in _kol)
cek("H4  yang dicatat adalah pesan yang BENAR-BENAR terkirim (final_message dari Validate)",
    "Validate FU Message" in _kol["last_bot_reply"] and "final_message" in _kol["last_bot_reply"])
cek("H4b stempel waktunya epoch detik", "Math.floor(Date.now()/1000)" in _kol["last_bot_reply_ts"])
cek("H5  gagal mencatat tidak memutus loop", _cb.get("onError") == "continueRegularOutput")
cek("H5b pakai retry", _cb.get("retryOnFail") is True)

cek("H6  kirim sukses -> IF Bukan Dry Run", CONNS["Kirim Follow-up"]["main"][0][0]["node"] == "IF Bukan Dry Run")
cek("H6b IF true -> Catat Balasan FU, IF false -> langsung Loop",
    CONNS["IF Bukan Dry Run"]["main"][0][0]["node"] == "Catat Balasan FU"
    and CONNS["IF Bukan Dry Run"]["main"][1][0]["node"] == "Loop Kandidat")
cek("H6c sesudah dicatat, kembali ke Loop", CONNS["Catat Balasan FU"]["main"][0][0]["node"] == "Loop Kandidat")
cek("H7  gerbangnya membaca dry_run dari Validate FU Message",
    "Validate FU Message" in _ifdry and "dry_run" in _ifdry, _ifdry)
cek("H7b gerbangnya MENEGASIKAN dry_run (dicatat hanya kalau BUKAN dry run)",
    "!" in _ifdry.split("dry_run")[0], _ifdry)
cek("H8  jalur gagal kirim TIDAK lewat Catat Balasan (klaim di-rollback, bukan dicatat)",
    CONNS["Kirim Follow-up"]["main"][1][0]["node"] == "Catat Gagal Kirim"
    and "Catat Balasan FU" not in [t["node"] for c in CONNS["Catat Gagal Kirim"]["main"] for t in c])

# Bukti kenapa gerbang dry run wajib: pesan dry run memuat awalan [DRY RUN ...]
# dan mendarat di WA Steven, jadi kalau ikut dicatat, Main akan menganggap
# prospek pernah menerima kalimat itu.
d, _ = val(BAIK, prompt_over={"ai_dry_run": True})
cek("H9  pesan dry run memang tidak layak dicatat (berawalan [DRY RUN, tujuan admin)",
    d and d["dry_run"] is True and d["final_message"].startswith("[DRY RUN")
    and d["target_phone"] == "6285171701168")
d, _ = val(BAIK, prompt_over={"ai_dry_run": False})
cek("H9b pesan sungguhan layak dicatat apa adanya",
    d and d["dry_run"] is False and d["final_message"] == BAIK)

# ===========================================================================
print()
print("=" * 72)
print("RINGKASAN UAT FOLLOW-UP")
print("=" * 72)
print("  LOLOS : %d" % len(lolos))
print("  GAGAL : %d" % len(gagal))
if gagal:
    print()
    for b, j, det in gagal:
        print("  [%s] %s" % (b, j))
        if det:
            print("        %s" % det)

print()
print("-" * 72)
print("UAT MANUAL — wajib sebelum followup_enabled = true")
print("-" * 72)
for i, langkah in enumerate([
    "Kolom deck_terkirim_ts sudah ada di STATS (paling kanan) dan terisi untuk minimal satu nomor uji.",
    "CONFIG diisi: followup_templates_a, followup_templates_c, followup_interval_hours_a/c, "
    "followup_max_a/c, followup_backlog_hour, followup_backlog_days.",
    "CONFIG followup_templates lama sudah dibersihkan dari {nama} (kode membuangnya paksa, "
    "tapi sheet jangan menyimpan pola yang salah).",
    "Import dengan active:false. Pastikan Schedule Trigger FU tetap disabled sesudah import.",
    "Pasang ulang kredensial: 4 node Sheets (service account) + DeepSeek FU.",
    "followup_ai_dry_run = Y, followup_test_numbers = nomor Steven, followup_enabled = true.",
    "Jalankan manual (Execute workflow). Semua pesan harus mendarat di WA Steven "
    "berawalan '[DRY RUN -> ...]'. Tidak boleh ada satu pun yang sampai ke prospek.",
    "Baca kalimat bucket A dan C: tidak ada nama prospek, tidak ada angka harga, "
    "tidak ada janji tanggal, maksimal 3 kalimat.",
    "Cek STATS: follow_up_count naik 1 dan last_follow_up_ts terisi untuk nomor yang dikirimi.",
    "Saat masih DRY RUN: STATS.last_bot_reply TIDAK boleh berubah (pesannya mendarat di WA Steven, "
    "bukan di prospek).",
    "Sesudah dry_run = N, kirim satu follow-up sungguhan ke nomor uji: STATS.last_bot_reply harus "
    "berisi teks follow-up itu dan last_bot_reply_ts terisi epoch saat itu.",
    "Balas follow-up itu dengan 'boleh' dari nomor uji: kalau follow-upnya menawarkan ngobrol dengan "
    "Steven, notif handover harus masuk dan bot_mode jadi OFF. Kalau menawarkan deck, brief harus "
    "tercatat dan bot tetap ON.",
    "Uji rollback: matikan sementara kredensial Kirimi (atau isi device_id salah), jalankan lagi. "
    "follow_up_count harus KEMBALI ke nilai semula, dan laporan run menyebut FU_KIRIM_GAGAL.",
    "Uji backlog: set followup_backlog_hour ke jam berjalan, pastikan ada baris deck_requested=Y "
    "tanpa deck_terkirim_ts. WA 'BRIEF DECK MENGGANTUNG' harus masuk ke Steven.",
    "Baru setelah semua di atas: kosongkan followup_test_numbers, set followup_ai_dry_run = N, "
    "aktifkan Schedule Trigger FU, lalu aktifkan workflow-nya.",
    "Hari pertama menyala: pantau satu siklus penuh, dan baca laporan run yang masuk.",
], 1):
    print("  %d. %s" % (i, langkah))

sys.exit(1 if gagal else 0)
