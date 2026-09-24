# -*- coding: utf-8 -*-
"""
_uat_2026-09-06.py — UAT perilaku untuk 2026-09-06-VIRA-Personal-Main-v3.1.json.

Berbeda dari _qa_*.py yang hanya memeriksa struktur, berkas ini MENJALANKAN kode
JavaScript asli dari node-node workflow di dalam mesin V8 (py-mini-racer), dengan
$(), $input, $getWorkflowStaticData, $vars, dan console yang dipalsukan persis
seperti yang disediakan n8n. Jadi yang diuji adalah kode yang benar-benar akan
jalan di produksi, bukan tiruannya.

Yang TETAP tidak bisa diuji di sini: apakah Google Sheets menulis baris yang benar,
apakah Kirimi mengirim, dan apakah model DeepSeek benar-benar mengeluarkan tag.
Tiga itu butuh nomor aktif — lihat daftar UAT manual di akhir keluaran.

Jalankan: python _uat_2026-09-06.py
Keluar dengan kode 1 kalau ada satu saja skenario GAGAL.
"""
import json
import os
import sys

from py_mini_racer import MiniRacer

DIR = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.1.json")

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
  const $vars = ctx.pakaiVars ? ctx.vars : undefined;
  const logs = [];
  const tulis = (lvl) => function () {
    logs.push(lvl + ": " + Array.prototype.slice.call(arguments).join(" "));
  };
  const konsol = { log: tulis("log"), warn: tulis("warn"), error: tulis("error"), info: tulis("info") };

  let out = null, err = null;
  try {
    const fn = new Function("$", "$input", "$json", "$getWorkflowStaticData", "$vars", "console", code);
    const hasil = fn($, $input, $input.item ? $input.item.json : {}, $getWorkflowStaticData, $vars, konsol);
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


def jalan(nama_node, nodes=None, inp=None, static=None, pakai_vars=True, vars_=None):
    """Jalankan jsCode sebuah node dengan konteks palsu. Kembalikan dict hasil."""
    kode = NODES[nama_node]["parameters"]["jsCode"]
    ctx = {
        "nodes": nodes or {},
        "input": inp if inp is not None else [],
        "staticData": static if static is not None else {},
        "vars": vars_ if vars_ is not None else {},
        "pakaiVars": pakai_vars,
    }
    return CTX.call("__run", kode, ctx)


def item(**kw):
    return {"json": kw}


def items(*ds):
    return [{"json": d} for d in ds]


def keluar_json(r):
    """Ambil daftar json dari keluaran node (bentuk [{json}] atau objek polos)."""
    if r["err"]:
        return None
    o = r["out"]
    if o is None:
        return []
    if isinstance(o, list):
        return [(x or {}).get("json", x) for x in o]
    if isinstance(o, dict) and "json" in o:
        return [o["json"]]
    return [o]


def satu(r):
    d = keluar_json(r)
    return d[0] if d else None


# ── ekspresi n8n dievaluasi apa adanya untuk menguji node IF ────────────────
def eval_ekspresi(ekspr, konteks_json):
    """Evaluasi '={{ ... }}' sederhana dengan $json yang diberikan."""
    isi = ekspr
    if isi.startswith("="):
        isi = isi[1:]
    isi = isi.strip()
    if isi.startswith("{{") and isi.endswith("}}"):
        isi = isi[2:-2].strip()
    return CTX.call("__run", "return (" + isi + ");",
                    {"nodes": {}, "input": [{"json": konteks_json}], "staticData": {},
                     "vars": {}, "pakaiVars": True})


print("=" * 72)
print("UAT PERILAKU — VIRA Personal v3.1 (2026-09-06)")
print("berkas: %s" % os.path.basename(WF))
print("=" * 72)


def cfg(**over):
    c = {
        "sheet_id": "SHEET", "client_name": "Steven", "bot_name": "Vira",
        "admin_phone": "6285171701168", "whitelist_enabled": False, "whitelist_numbers": [],
        "blocklist_numbers": [], "bot_wa_number": "6285155202354", "ignore_self_number": True,
        "rate_limit_max": 15, "rate_limit_window_sec": 60, "debounce_seconds": 60,
        "vision_mode": "full", "vision_max_images": 3,
        "vision_model": "deepseek-v4-flash-vision-exp", "vision_max_tokens": 700,
        "katalog_cache_minutes": 10, "fact_ttl_days": 60,
        "kirimi_user_code": "UC", "kirimi_secret": "SEC", "kirimi_device_id": "DEV",
        "lead_source_map": [],
    }
    c.update(over)
    return c


def payload(frm="6289900112233", pesan="halo", **over):
    b = {"from": frm, "message": pesan, "messageType": "text",
         "isFromGroup": False, "isFromMe": False, "name": "Prospek"}
    b.update(over)
    return b


# ===========================================================================
bagian("A. GERBANG MASUK — siapa yang boleh dibalas (P0-1, P1-7, P2-12)")
# ===========================================================================
wl = NODES["IF (Whitelist)"]
cek("A0  IF (Whitelist) tidak lagi punya kabel keluar",
    "IF (Whitelist)" not in CONNS, "node masih menyambung ke sesuatu")
cek("A0b IF (Whitelist) disabled", wl.get("disabled") is True)
cek("A0c IF From Me menyambung langsung ke Bootstrap Config",
    CONNS["IF From Me"]["main"][0][0]["node"] == "Bootstrap Config",
    str(CONNS["IF From Me"]["main"][0]))
cek("A0d tidak ada node lain yang menyambung ke IF (Whitelist)",
    all(t["node"] != "IF (Whitelist)"
        for v in CONNS.values() for br in v.get("main", []) for t in (br or [])))


def gate(frm, konfig, lid=""):
    inp = [item(body=payload(frm=frm, originLid=lid), sheet_id="SHEET", config=konfig)]
    return jalan("Blocklist Gate", nodes={"Parse Config": [item(config=konfig)]}, inp=inp)


r = gate("6289900112233", cfg())
cek("A1  prospek iklan (nomor acak) LOLOS", r["err"] is None and len(keluar_json(r)) == 1,
    r["err"] or "dibuang")

r = gate("6289900112233", cfg(whitelist_enabled=True, whitelist_numbers=["6285171701168"]))
cek("A2  whitelist aktif + nomor asing ditolak", keluar_json(r) == [])

r = gate("6285171701168", cfg(whitelist_enabled=True, whitelist_numbers=["6285171701168"]))
cek("A3  whitelist aktif + nomor terdaftar lolos", len(keluar_json(r)) == 1)

r = gate("6289900112233", cfg(whitelist_enabled=True, whitelist_numbers=[]))
cek("A4  whitelist aktif tapi daftar KOSONG -> tetap lolos (fail-open)",
    len(keluar_json(r)) == 1, "bot mati total kalau Steven lupa isi daftarnya")

r = gate("6289900112233", cfg(blocklist_numbers=["6289900112233"]))
cek("A5  nomor di blocklist ditolak", keluar_json(r) == [],
    "blocklist tidak pernah aktif sebelum patch")

r = gate("6285155202354", cfg())
cek("A6  nomor bot sendiri ditolak (anti-loop)", keluar_json(r) == [])

r = gate("", cfg(blocklist_numbers=["6289900112233"]), lid="778899001122")
cek("A7  pengirim @lid tetap dievaluasi lewat originLid", len(keluar_json(r)) == 1)

r = gate("", cfg(blocklist_numbers=["778899001122"]), lid="778899001122")
cek("A8  blocklist mengenali lid", keluar_json(r) == [])

# node IF: payload tanpa field isFromGroup / isFromMe
for nm, fld in (("If From Group", "isFromGroup"), ("IF From Me", "isFromMe")):
    ekspr = NODES[nm]["parameters"]["conditions"]["conditions"][0]["leftValue"]
    hasil = eval_ekspresi(ekspr, {"body": {"from": "628999"}})
    cek("A9  %s: payload tanpa field -> false (bukan error)" % nm,
        hasil["err"] is None and hasil["out"] is False, hasil["err"] or str(hasil["out"]))
    hasil = eval_ekspresi(ekspr, {"body": {"from": "628999", fld: True}})
    cek("A10 %s: field true tetap terdeteksi" % nm, hasil["out"] is True)


# ===========================================================================
bagian("B. CHAT COUNTER — gerbang tipe pesan (P2-9b)")
# ===========================================================================
def chat_counter(body, konfig=None, pakai_vars=True):
    konfig = konfig or cfg()
    return jalan("Chat Counter",
                 nodes={"Parse Config": [item(config=konfig)]},
                 inp=[item(body=body)], pakai_vars=pakai_vars)


r = chat_counter(payload(pesan="halo mau tanya"))
d = satu(r)
cek("B1  pesan teks diteruskan", d is not None and d["original_message"] == "halo mau tanya",
    r["err"] or str(d))
cek("B2  user_phone & media_kind benar",
    d and d["user_phone"] == "6289900112233" and d["media_kind"] == "none")

r = chat_counter(payload(pesan="ok", messageType="reaction"))
cek("B3  reaction dibuang", keluar_json(r) == [], r["err"] or "tidak dibuang")

r = chat_counter(payload(pesan="", messageType="image", mediaUrl="https://x/y.jpg", mimetype="image/jpeg"))
d = satu(r)
cek("B4  gambar diteruskan sebagai media_kind=image", d and d["media_kind"] == "image")

r = chat_counter(payload(pesan="", messageType="sticker"))
d = satu(r)
cek("B5  stiker jadi media_kind=other (tidak dikirim ke Vision)", d and d["media_kind"] == "other")

r = chat_counter(payload(pesan="", messageType="image", mediaUrl="https://x/y.jpg"),
                 konfig=cfg(vision_mode="off"))
cek("B6  vision_mode=off membuang media", keluar_json(r) == [])

r = chat_counter(payload(pesan="halo"), pakai_vars=False)
cek("B7  $vars tidak tersedia -> TIDAK error (P2-9b)",
    r["err"] is None and satu(r) is not None, r["err"] or "kosong")

r = chat_counter(payload(pesan="", messageType="text"))
cek("B8  pesan kosong tanpa media dibuang", keluar_json(r) == [])


# ===========================================================================
bagian("C. RATE LIMITER (P2-9)")
# ===========================================================================
static = {}
lolos_n = 0
for i in range(20):
    r = jalan("Rate Limiter LID",
              nodes={"Parse Config": [item(config=cfg())],
                     "Resolve User Row": [item(resolved_key="6289900112233")]},
              inp=[item(msg=i)], static=static)
    static = r["staticData"]
    if keluar_json(r):
        lolos_n += 1
cek("C1  batas 15/menit dipatuhi (bukan 5)", lolos_n == 15, "lolos=%d" % lolos_n)

static = {}
lolos_n = 0
for i in range(8):
    r = jalan("Rate Limiter LID",
              nodes={"Parse Config": [item(config=cfg(rate_limit_max=3))],
                     "Resolve User Row": [item(resolved_key="628")]},
              inp=[item(msg=i)], static=static)
    static = r["staticData"]
    if keluar_json(r):
        lolos_n += 1
cek("C2  batas mengikuti CONFIG.rate_limit_max", lolos_n == 3, "lolos=%d" % lolos_n)


# ===========================================================================
bagian("D. RESOLVE USER ROW — identitas & balasan terakhir (P0-2a)")
# ===========================================================================
BARIS = {"No WA": "6289900112233", "lid": "778899001122", "greeting_sent": "Y",
         "bot_mode": "ON", "industri": "konsultan sipil", "nama_bisnis": "",
         "Counter": 4, "last_bot_reply": "Boleh tahu nama bisnisnya dulu kak?",
         "last_bot_reply_ts": 1757000000}


def resolve(cc, baris=None):
    return jalan("Resolve User Row",
                 nodes={"Chat Counter": [item(**cc)],
                        "Read User STATS": items(*(baris if baris is not None else [BARIS]))},
                 inp=[item()])


d = satu(resolve({"user_phone": "6289900112233", "user_lid": ""}))
cek("D1  cocok lewat No WA", d and d["resolved_key"] == "6289900112233" and d["row_found"])
cek("D2  last_bot_reply ikut terbawa (P0-2a)",
    d and d["last_bot_reply"] == "Boleh tahu nama bisnisnya dulu kak?"
      and d["last_bot_reply_ts"] == 1757000000, str(d and d.get("last_bot_reply")))

d = satu(resolve({"user_phone": "", "user_lid": "778899001122"}))
cek("D3  cocok lewat lid, kunci tetap No WA", d and d["resolved_key"] == "6289900112233")

d = satu(resolve({"user_phone": "6280000000000", "user_lid": ""}))
cek("D4  user baru -> kunci = nomor, row_found false",
    d and d["resolved_key"] == "6280000000000" and d["row_found"] is False)
cek("D5  user baru tidak mewarisi last_bot_reply orang lain",
    d and d["last_bot_reply"] == "")

r = resolve({"user_phone": "", "user_lid": ""})
cek("D6  identitas kosong -> error keras (bukan diam-diam rows[0])",
    r["err"] is not None and "Identitas user kosong" in r["err"], str(r["err"]))

d = satu(resolve({"user_phone": "6280000000000", "user_lid": ""}, baris=[]))
cek("D7  STATS kosong tidak menjatuhkan node", d and d["resolved_key"] == "6280000000000")


# ===========================================================================
bagian("I. DETECT LEAD SOURCE (P2-10)")
# ===========================================================================
def lead(pesan, lead_db=""):
    return satu(jalan("Detect Lead Source",
                      nodes={"Resolve User Row": [item(lead_source_db=lead_db)],
                             "Parse Config": [item(config=cfg())]},
                      inp=[item(user_message_final=pesan)]))


cek("I1  'chat masuk tinggi banget' BUKAN Instagram",
    lead("chat masuk tinggi banget")["lead_source_final"] == "Organik",
    lead("chat masuk tinggi banget")["lead_source_final"])
cek("I2  'bagi info dong' BUKAN Instagram",
    lead("bagi info dong")["lead_source_final"] == "Organik")
cek("I3  'aku lihat di IG' -> Instagram",
    lead("aku lihat di IG")["lead_source_final"] == "Instagram")
cek("I4  'dari instagram' -> Instagram",
    lead("dari instagram")["lead_source_final"] == "Instagram")
cek("I5  'nemu di gmaps' -> Google",
    lead("nemu di gmaps")["lead_source_final"] == "Google")
cek("I6  sumber pertama dipertahankan",
    lead("aku lihat di IG", lead_db="Google")["lead_source_final"] == "Google")


import time
NOW_S = int(time.time())
NOW_MS = NOW_S * 1000


# ===========================================================================
bagian("E. CEK_USER_STATUS — buffer + jaring pengaman ingatan (P0-2b)")
# ===========================================================================
def cek_user(buffer_rows, debounce_row, cc=None, konfig=None, resolve_row=None):
    cc = cc or {"user_phone": "6289900112233", "user_lid": "", "process_start_ts": NOW_MS,
                "original_message": "terakhir", "media_url": "", "media_kind": "none"}
    resolve_row = resolve_row or {"resolved_key": "6289900112233", "greeting_sent": "Y",
                                  "last_bot_reply": "", "last_bot_reply_ts": 0}
    return jalan("Cek_user_status", nodes={
        "Chat Counter": [item(**cc)],
        "Resolve User Row": [item(**resolve_row)],
        "Parse Config": [item(config=konfig or cfg())],
        "Re-Read STATS Debounce": [item(**debounce_row)],
        "Read MSG_BUFFER": items(*buffer_rows),
    }, inp=[item()])


BUF = [
    {"ts": NOW_MS - 8000, "message": "di bidang konsultan ya", "media_url": "", "media_type": ""},
    {"ts": NOW_MS - 5000, "message": "konsultan sipil", "media_url": "", "media_type": ""},
    {"ts": NOW_MS, "message": "mau tau ai cs ini bs bantu apa aja", "media_url": "", "media_type": ""},
]

d = satu(cek_user(BUF, {"bot_mode": "ON", "buffer_done_ts": NOW_MS - 60000, "greeting_sent": "Y"}))
cek("E1  tiga pesan dalam window debounce digabung",
    d and d["user_message_final"].count("\n") == 2
      and "konsultan sipil" in d["user_message_final"], str(d and d.get("user_message_final")))

r = cek_user(BUF, {"bot_mode": "OFF", "buffer_done_ts": 0, "greeting_sent": "Y"})
cek("E2  bot_mode OFF setelah debounce -> berhenti", keluar_json(r) == [])

d = satu(cek_user(BUF, {"bot_mode": "ON", "buffer_done_ts": 0, "greeting_sent": "Y",
                        "last_bot_reply": "Boleh tahu nama bisnisnya dulu kak?",
                        "last_bot_reply_ts": NOW_S - 120}))
cek("E3  blok BALASAN TERAKHIRMU disuntikkan saat segar",
    d and "BALASAN TERAKHIRMU" in d["ai_input_text"]
      and "Boleh tahu nama bisnisnya dulu kak?" in d["ai_input_text"],
    (d or {}).get("ai_input_text", "")[:200])
cek("E3b blok berdiri SEBELUM CRITICAL INSTRUCTION",
    d and d["ai_input_text"].index("BALASAN TERAKHIRMU") < d["ai_input_text"].index("CRITICAL INSTRUCTION"))
cek("E3c blok tidak mengganggu pemisah [USER QUERY]",
    d and d["ai_input_text"].count("[USER QUERY]") == 1)

d = satu(cek_user(BUF, {"bot_mode": "ON", "buffer_done_ts": 0, "greeting_sent": "Y",
                        "last_bot_reply": "pesan lama sekali",
                        "last_bot_reply_ts": NOW_S - 40 * 3600}))
cek("E4  balasan lebih tua dari 24 jam TIDAK disuntikkan",
    d and "BALASAN TERAKHIRMU" not in d["ai_input_text"])

d = satu(cek_user(BUF, {"bot_mode": "ON", "buffer_done_ts": 0, "greeting_sent": "Y"}))
cek("E5  kolom kosong (sheet belum ditambah) tetap jalan normal",
    d is not None and "BALASAN TERAKHIRMU" not in d["ai_input_text"], str(r["err"]))

d = satu(cek_user(BUF, {"bot_mode": "ON", "buffer_done_ts": 0, "greeting_sent": ""},
                  resolve_row={"resolved_key": "6289900112233", "greeting_sent": "",
                               "last_bot_reply": "", "last_bot_reply_ts": 0}))
cek("E6  greeting_sent kosong -> IS_NEW_USER true", d and d["is_new_user"] is True)

d = satu(cek_user(BUF, {"bot_mode": "ON", "buffer_done_ts": 0},
                  resolve_row={"resolved_key": "6289900112233", "greeting_sent": "Y",
                               "last_bot_reply": "", "last_bot_reply_ts": 0}))
cek("E6b kolom greeting_sent hilang dari hasil debounce -> jatuh ke Resolve User Row",
    d and d["is_new_user"] is False)

d = satu(cek_user([], {"bot_mode": "ON", "buffer_done_ts": 0, "greeting_sent": "Y"}))
cek("E7  MSG_BUFFER kosong -> jatuh ke pesan terakhir, tidak kosong",
    d and d["user_message_final"] == "terakhir")

d = satu(cek_user(
    [{"ts": NOW_MS, "message": "", "media_url": "https://x/a.jpg", "media_type": "image"}],
    {"bot_mode": "ON", "buffer_done_ts": 0, "greeting_sent": "Y"}))
cek("E8  gambar tanpa caption -> teks netral, vision_on true",
    d and d["has_image"] is True and d["vision_on"] is True
      and "gambar" not in d["user_query_text"].lower(),
    str(d and d.get("user_query_text")))


# ===========================================================================
bagian("F. PREPROCESS — tidak lagi mendorong bot bunuh diri (P1-5)")
# ===========================================================================
def pre(pesan):
    teks = ("[SYSTEM_DATA]\nUSER_WA: 628\nIS_NEW_USER: false\n\nCRITICAL INSTRUCTION:\nlanjut\n\n"
            "[USER QUERY]\n" + pesan)
    return satu(jalan("Preprocess - Context Detection",
                      nodes={"Parse Config": [item(config=cfg())]},
                      inp=[item(ai_input_text=teks, user_wa="628")]))


for pesan in ["chat paling ramai hari senin", "besok jam 10 gimana", "mau mulai minggu depan",
              "biasanya sore sih ramenya", "tanggal 1 bulan depan bisa?"]:
    d = pre(pesan)
    cek("F1  '%s' TIDAK mendorong [TALK_TO_ADMIN]" % pesan,
        "TALK_TO_ADMIN" not in d["ai_input_text"], d["aiContext"])

for pesan in ["aku kirim foto ya", "ini gambar dashboard aku", "fotonya udah aku kirim"]:
    d = pre(pesan)
    cek("F2  '%s' TIDAK dianggap minta file" % pesan, d["wantsMedia"] is False, d["aiContext"])

for pesan in ["boleh minta brosurnya?", "ada contoh decknya ga", "mau lihat portfolio dong"]:
    d = pre(pesan)
    cek("F3  '%s' dianggap minta file" % pesan, d["wantsMedia"] is True)

for pesan in ["20an chat per hari", "kira kira berapa ya orangnya", "ada berapa admin"]:
    d = pre(pesan)
    cek("F4  '%s' TIDAK memicu konteks harga" % pesan, d["askingPrice"] is False, d["aiContext"])

for pesan in ["harganya berapa ya", "biaya bulanannya gimana", "paket premium berapa harganya"]:
    d = pre(pesan)
    cek("F5  '%s' memicu konteks harga" % pesan, d["askingPrice"] is True)

for pesan in ["mau ngobrol langsung sama steven dong", "boleh minta nomor stevennya",
              "bisa ditelpon ga", "mau meeting bisa?"]:
    d = pre(pesan)
    cek("F6  '%s' terdeteksi niat bicara" % pesan, d["wantsHuman"] is True)

d = pre("halo mau tanya soal ai customer service")
cek("F7  SYSTEM_DATA dipertahankan utuh", "CRITICAL INSTRUCTION" in d["ai_input_text"])
cek("F8  [USER QUERY] tepat satu", d["ai_input_text"].count("[USER QUERY]") == 1)
cek("F9  actualUserMessage bersih dari blok sistem",
    d["actualUserMessage"] == "halo mau tanya soal ai customer service")


# ===========================================================================
bagian("G. PROCESS ALL — inti insiden 2026-09-05 (P0-2, P0-3, P1-4, P1-6)")
# ===========================================================================
LINKS = [
    {"Nama Link": "instagram", "URL": "https://instagram.com/povstevens", "Caption": "IG-ku",
     "Status": "Aktif", "Keyword": "instagram ig", "Tipe": "website"},
    {"Nama Link": "brosur vira", "URL": "https://drive.google.com/file/d/1AAAAAAAAAAAAAA/view",
     "Caption": "Brosur VIRA", "Status": "Aktif", "Keyword": "brosur", "Tipe": "file"},
    {"Nama Link": "deck contoh", "URL": "https://drive.google.com/file/d/1BBBBBBBBBBBBBB/view",
     "Caption": "Contoh deck", "Status": "Aktif", "Keyword": "deck contoh", "Tipe": "file"},
]


def proses(ai_output, pesan_user="halo", prev_row=None, links=None):
    prev = {"resolved_key": "6289900112233", "nama_lengkap": "", "nama_bisnis": "",
            "industri": "", "masalah_utama": "", "volume_chat": "", "budget_range": "",
            "minat_paket": "", "bahasa": "", "deck_requested": "", "brief_terisi": "",
            "last_bot_reply": "", "last_bot_reply_ts": 0}
    prev.update(prev_row or {})
    return jalan("Process All", nodes={
        "Chat Counter": [item(original_message=pesan_user, user_wa="6289900112233",
                              user_name="Prospek")],
        "Preprocess - Context Detection": [item(actualUserMessage=pesan_user, isNewUser=False,
                                                wantsMedia=False, askingPrice=False,
                                                wantsHuman=False)],
        "Parse Config": [item(config=cfg())],
        "Resolve User Row": [item(**prev)],
        "Rakit Konteks": [item(katalog={"links": links if links is not None else LINKS})],
    }, inp=[item(output=ai_output)])


DECK_BLOK = ("[DECK_REQUEST]\nnama: belum disebut\njabatan: belum disebut\n"
             "nama_bisnis: belum disebut\nindustri: konsultan sipil\n"
             "deskripsi_bisnis: belum disebut\ntarget_pelanggan: belum disebut\n"
             "channel: WhatsApp\nsumber_leads: mulut ke mulut dan Google Maps\n"
             "volume_chat_harian: belum disebut\njam_operasional: belum disebut\n"
             "siapa_balas_chat: ownernya sendiri\nbiaya_admin_bulanan: belum disebut\n"
             "sistem_sekarang: belum disebut\nmasalah_utama: tenggelam membalas chat satu per satu\n"
             "pain_points: belum disebut\naksi_utama: belum disebut\n"
             "alur_setelah_chat: belum disebut\npertanyaan_tersering: harga proyek\n"
             "fitur_diminati: belum disebut\nnilai_transaksi: belum disebut\n"
             "prospek_per_bulan: belum disebut\nminat_paket: belum disebut\n"
             "budget_range: belum disebut\ndeadline: belum disebut\nurgensi: belum disebut\n"
             "bahasa_deck: ID\ncatatan: belum disebut\nkota: belum disebut\n"
             "jumlah_admin: belum disebut\nsudah_pakai_chatbot: belum disebut\n"
             "integrasi_dibutuhkan: belum disebut\ndata_tersedia: belum disebut\n"
             "kutipan_asli: tenggelem balesin chat 1 1 | paling sering tanya harga si\n"
             "[/DECK_REQUEST]\n")

# --- G1: REGRESI PERSIS INSIDEN 14:34-14:35 -------------------------------
BALASAN_ASLI = ("Sudah aku teruskan briefnya ke Steven, dia sendiri yang akan menyusun "
                "decknya dan menghubungi kakak langsung. Sambil menunggu, kakak bebas "
                "tanya apa aja ke aku.")
r = proses(DECK_BLOK + BALASAN_ASLI, pesan_user="boleh",
           prev_row={"last_bot_reply": "Kalau nanti mau lihat gambaran lengkapnya, ada landing "
                                       "page-nya, atau bisa juga aku mintakan Steven buatkan deck "
                                       "khusus buat bisnis kakak, gratis. Mau?",
                     "last_bot_reply_ts": NOW_S - 90,
                     "industri": "konsultan sipil",
                     "masalah_utama": "tenggelam membalas chat satu per satu"})
d = satu(r)
cek("G0  node tidak error", r["err"] is None, str(r["err"]))
cek("G1  balasan TIDAK diganti pertanyaan kaleng (akar insiden)",
    d and "Boleh tahu nama bisnisnya" not in d["cleanOutput"], str(d and d["cleanOutput"])[:160])
cek("G1b balasan yang dikirim = tulisan AI",
    d and "teruskan briefnya ke steven" in d["cleanOutput"].lower(),
    str(d and d["cleanOutput"])[:160])
cek("G1c deckRejected tetap terdeteksi (brief tetap disimpan)",
    d and d["deckRejected"] is True and d["deckMissing"] == ["nama_bisnis"])
cek("G2  'boleh' setelah tawaran deck dikenali sebagai permintaan (P1-4)",
    d and d["deckDiminta"] is True, "deckDiminta=%s" % (d and d.get("deckDiminta")))
cek("G2b deckNotify true -> Steven pasti dinotifikasi", d and d["deckNotify"] is True)
cek("G2c last_bot_reply = teks final yang dikirim",
    d and d["last_bot_reply"] == d["cleanOutput"])
cek("G2d replyOverridden false (tidak ada penggantian teks)", d and d["replyOverridden"] is False)
cek("G2e tag tidak bocor ke prospek",
    d and "[DECK_REQUEST]" not in d["cleanOutput"] and "[/DECK_REQUEST]" not in d["cleanOutput"])

# --- G3: 'boleh' TANPA tawaran deck sebelumnya ----------------------------
d = satu(proses("Oke kak, aku catat yaa.", pesan_user="boleh",
                prev_row={"last_bot_reply": "Kira-kira chat masuknya berapa per hari kak?",
                          "last_bot_reply_ts": NOW_S - 60}))
cek("G3  'boleh' tanpa tawaran deck TIDAK dianggap minta deck", d and d["deckDiminta"] is False)

# --- G4/G5: gerbang mematikan bot ----------------------------------------
d = satu(proses("[TALK_TO_ADMIN]\nSiap kak, Steven yang akan menghubungi kakak langsung yaa.",
                pesan_user="boleh minta ditelpon aja bisa?"))
cek("G4  prospek minta ditelepon -> bot dimatikan",
    d and d["isTalkToAdmin"] is True and d["matikanBot"] is True)

d = satu(proses("[TALK_TO_ADMIN]\nSiap kak, nanti Steven kabari yaa.",
                pesan_user="oke makasih infonya"))
cek("G5  tag TALK_TO_ADMIN tanpa permintaan bicara -> bot TETAP HIDUP (P1-6)",
    d and d["isTalkToAdmin"] is True and d["matikanBot"] is False,
    "matikanBot=%s" % (d and d.get("matikanBot")))
cek("G5b Steven tetap dinotifikasi (isTalkToAdmin true)", d and d["isTalkToAdmin"] is True)

for pesan in ["mau ngobrol langsung sama steven dong", "boleh minta kontak stevennya",
              "bisa meeting minggu ini?", "ada cp yang bisa dihubungi?"]:
    d = satu(proses("[TALK_TO_ADMIN]\nOke kak.", pesan_user=pesan))
    cek("G4b '%s' -> bot dimatikan" % pesan, d and d["matikanBot"] is True)

# --- G6: dua SEND_MEDIA (P0-3 ReferenceError) -----------------------------
r = proses("[SEND_MEDIA: brosur vira] [SEND_MEDIA: deck contoh]\nIni dua-duanya yaa kak.",
           pesan_user="boleh minta brosur sama contoh decknya")
d = satu(r)
cek("G6  dua tag SEND_MEDIA tidak lagi melempar ReferenceError (P0-3)",
    r["err"] is None, str(r["err"]))
cek("G6b media pertama & kedua sama-sama terisi",
    d and d["isSendMedia"] is True and d["isSendMedia2"] is True
      and d["mediaUrl"] != d["mediaUrl2"], str(d and (d.get("mediaUrl"), d.get("mediaUrl2"))))
cek("G6c URL Drive dirapikan ke bentuk direct download",
    d and d["mediaUrl"].startswith("https://drive.usercontent.google.com/download?id=")
      and d["mediaUrl2"].startswith("https://drive.usercontent.google.com/download?id="))

# --- G7: file tidak ada di katalog ---------------------------------------
d = satu(proses("[SEND_MEDIA: video demo]\nAku kirim video demonya yaa kak.",
                pesan_user="ada video demo?"))
cek("G7  key tidak ada -> eskalasi manual", d and d["isMediaManual"] is True)
cek("G7b balasan diganti supaya tidak menjanjikan file",
    d and "belum ada di katalogku" in d["cleanOutput"])
cek("G7c penggantian ditandai replyOverridden (P0-2d)", d and d["replyOverridden"] is True)
cek("G7d last_bot_reply mengikuti teks pengganti, bukan tulisan AI",
    d and d["last_bot_reply"] == d["cleanOutput"] and "video demonya" not in d["last_bot_reply"])

# --- G8: media ambigu ----------------------------------------------------
AMBIGU = LINKS + [{"Nama Link": "brosur vira lama", "URL": "https://drive.google.com/file/d/1CCCCCCCCCCCCCC/view",
                   "Caption": "Brosur lama", "Status": "Aktif", "Keyword": "brosur", "Tipe": "file"}]
d = satu(proses("[SEND_MEDIA: brosur]\nIni brosurnya kak.",
                pesan_user="minta brosur dong", links=AMBIGU))
cek("G8  dua kandidat -> sistem bertanya balik, media tidak dikirim",
    d and d["isMediaAmbiguous"] is True and d["isSendMedia"] is False
      and "mau yang mana" in d["cleanOutput"], str(d and d.get("cleanOutput"))[:120])
cek("G8b ditandai replyOverridden", d and d["replyOverridden"] is True)

# --- G9: FACTS ------------------------------------------------------------
d = satu(proses('Siap kak, aku catat yaa.\n'
                '[FACTS nama="Budi" nama_bisnis="Teamsultan" industri="konsultan sipil"]',
                pesan_user="teamsultan, konsultan sipil",
                prev_row={"masalah_utama": "tenggelam balas chat"}))
cek("G9  FACTS terparse", d and d["nama_bisnis_merged"] == "Teamsultan"
    and d["nama_lengkap_merged"] == "Budi" and d["industri_merged"] == "konsultan sipil")
cek("G9b fakta lama yang tidak disebut tetap dipertahankan",
    d and d["masalah_utama_merged"] == "tenggelam balas chat")
cek("G9c tag FACTS tidak bocor ke prospek", d and "[FACTS" not in d["cleanOutput"])
cek("G9d penanda perubahan benar", d and d["nama_bisnis_changed"] is True
    and d["masalah_utama_changed"] is False)

# --- G10..G12: ketahanan output ------------------------------------------
d = satu(proses(""))
cek("G10 output AI kosong -> ada kalimat cadangan, bukan pesan kosong",
    d and len(d["cleanOutput"]) > 10)

d = satu(proses("[UNKNOWN]\nAku belum tahu soal itu kak, nanti aku tanyakan ke Steven."))
cek("G11 [UNKNOWN] terdeteksi & tag dibuang",
    d and d["isUnknown"] is True and "[UNKNOWN]" not in d["cleanOutput"])

d = satu(proses("Oke kak.\n[DECK_REQUEST]\nnama: Budi\nnama_bisnis: Teamsultan\nindustri: sipil",
                pesan_user="boleh dibuatkan decknya"))
cek("G12 blok DECK_REQUEST terpotong -> tag tidak bocor ke prospek",
    d and "DECK_REQUEST" not in d["cleanOutput"], str(d and d.get("cleanOutput")))
cek("G12b brief yang sempat tertangkap tetap tersimpan",
    d and d["deckRequest"]["nama_bisnis"] == "Teamsultan")

d = satu(proses("Siap kak, briefnya aku teruskan ke Steven yaa.\n"
                + DECK_BLOK.split("[/DECK_REQUEST]")[0][:600],
                pesan_user="boleh dibuatkan decknya"))
cek("G12c keluaran terpotong di tengah blok -> brief yang sempat tertulis tetap terbaca (P1-8b)",
    d and d["deckRequest"]["industri"] == "konsultan sipil",
    str(d and d.get("deckRequest", {}).get("industri")))
cek("G12d prospek tetap menerima kalimat yang masuk akal",
    d and "DECK_REQUEST" not in d["cleanOutput"] and len(d["cleanOutput"]) > 10,
    str(d and d.get("cleanOutput"))[:120])

d = satu(proses("**Halo** kak, ini _penting_ ya.\n- poin satu"))
cek("G13 markdown dibersihkan untuk WhatsApp",
    d and "**" not in d["cleanOutput"] and "_penting_" not in d["cleanOutput"])

d = satu(proses("[SEND_MEDIA: instagram]\nIni IG-ku kak."))
cek("G14 link tipe website ditempel sebagai teks, bukan diunduh",
    d and d["isSendMedia"] is False and "instagram.com/povstevens" in d["cleanOutput"])


# ===========================================================================
bagian("H. MERGE BRIEF — gerbang notifikasi ke Steven (P1-4b)")
# ===========================================================================
def merge(pa_over, requests_lama=None):
    pa = {"deckRequest": {}, "deckLayak": False, "deckDiminta": False, "isDeckRequest": True,
          "nama_lengkap_merged": "", "nama_bisnis_merged": "", "industri_merged": "",
          "masalah_utama_merged": "", "minat_paket_merged": "", "budget_range_merged": "",
          "volume_chat_merged": ""}
    pa.update(pa_over)
    return satu(jalan("Merge Brief", nodes={
        "Process All": [item(**pa)],
        "Resolve User Row": [item(resolved_key="6289900112233", lead_source_db="Organik")],
        "Read REQUESTS": items(*(requests_lama or [])),
    }, inp=[item()]))


BRIEF1 = {"nama_bisnis": "", "industri": "konsultan sipil",
          "masalah_utama": "tenggelam balas chat", "channel": "WhatsApp"}
d = merge({"deckRequest": BRIEF1})
cek("H1  brief PERTAMA selalu dinotifikasi walau tingkat 1 belum lengkap",
    d and d["deck_layak"] is True, "deck_layak=%s" % (d and d.get("deck_layak")))
cek("H1b kelengkapan dihitung", d and d["brief_jumlah"] == 3)

LAMA = {"no_wa": "6289900112233", "ts": "2026-09-05 14:35:00", "brief_jumlah": 3,
        "nama_bisnis": "", "industri": "konsultan sipil",
        "masalah_utama": "tenggelam balas chat", "channel": "WhatsApp"}
d = merge({"deckRequest": BRIEF1}, requests_lama=[LAMA])
cek("H2  brief yang isinya sama TIDAK dinotifikasi lagi (anti spam)",
    d and d["deck_layak"] is False, "deck_layak=%s" % (d and d.get("deck_layak")))

BRIEF2 = dict(BRIEF1, nama_bisnis="Teamsultan", volume_chat_harian="20an")
d = merge({"deckRequest": BRIEF2}, requests_lama=[LAMA])
cek("H3  brief bertambah isi -> dinotifikasi lagi", d and d["deck_layak"] is True)
cek("H3b isian lama tidak hilang", d and d["masalah_utama"] == "tenggelam balas chat")

d = merge({"deckRequest": BRIEF1, "deckDiminta": True}, requests_lama=[LAMA])
cek("H4  prospek meminta eksplisit -> selalu dinotifikasi", d and d["deck_layak"] is True)

LAMA_LAIN = dict(LAMA, nama_bisnis="Sekolah Alpha", industri="edukasi",
                 target_pelanggan="calon murid")
d = merge({"deckRequest": BRIEF2}, requests_lama=[LAMA_LAIN])
cek("H5  identitas bisnis berubah -> brief lama dibuang, tidak menyeret field asing",
    d and d.get("target_pelanggan", "") == "", str(d and d.get("target_pelanggan")))

d = merge({"deckRequest": {}, "isDeckRequest": False})
cek("H6  tidak ada brief sama sekali -> tidak ada notifikasi", d and d["deck_layak"] is False)
cek("H7  perintah generate deck memakai nomor yang benar",
    d and "--wa 6289900112233" in d["notif_text"])


# ===========================================================================
bagian("J. RAKIT KONTEKS — data prospek & kebocoran catatan internal (P2-11)")
# ===========================================================================
def rakit(user_row, katalog=None, faq=""):
    kat = katalog or {
        "faq": [], "program": [{"Nama": "Basic", "Harga": "Rp3.000.000/bln",
                                "Status": "Aktif", "Catatan Internal": "margin 60%"}],
        "links": LINKS,
        "about": [{"Aspek": "Pengalaman", "Detail": "QA di bank swasta nasional",
                   "Boleh Dibagikan": "Ya"},
                  {"Aspek": "Tarif dasar", "Detail": "jangan pernah turun dari 3jt",
                   "Boleh Dibagikan": "Tidak"}]}
    return satu(jalan("Rakit Konteks", nodes={
        "Parse Config": [item(config=cfg())],
        "Resolve User Row": [item(userRow=user_row, lead_source_db="Organik")],
    }, inp=[item(katalog=kat, faq_context=faq)]))


d = rakit({"greeting_sent": "Y", "industri": "konsultan sipil", "nama_bisnis": "Teamsultan"})
cek("J1  greeting_sent='Y' -> IS_NEW_USER false", "IS_NEW_USER: false" in d["prospect_context"])
cek("J1b fakta tersimpan muncul di DATA PROSPEK",
    "industri: konsultan sipil" in d["prospect_context"]
    and "nama_bisnis: Teamsultan" in d["prospect_context"])

d = rakit({"greeting_sent": ""})
cek("J2  greeting_sent kosong -> IS_NEW_USER true", "IS_NEW_USER: true" in d["prospect_context"])

d = rakit({"greeting_sent": "N"})
cek("J3  greeting_sent='N' -> IS_NEW_USER true (konsisten dgn Cek_user_status, P2-11)",
    "IS_NEW_USER: true" in d["prospect_context"], d["prospect_context"])

d = rakit({"greeting_sent": "Y"})
cek("J4  catatan internal PROGRAM tidak dikirim ke AI",
    "margin 60%" not in d["program_context"])
cek("J5  baris ABOUT 'Boleh Dibagikan=Tidak' masuk aturan internal, bukan fakta",
    "jangan pernah turun" in d["about_context"]
    and "ATURAN INTERNAL" in d["about_context"])

d = rakit({"greeting_sent": "Y", "deck_requested": "Y"})
cek("J6  deck_requested=Y muncul sebagai sudah_minta_pitch_deck",
    "sudah_minta_pitch_deck: ya" in d["prospect_context"])

d = rakit({"greeting_sent": "Y", "masalah_utama": "basi banget",
           "masalah_utama_ts": str(NOW_S - 200 * 86400)})
cek("J7  fakta lebih tua dari TTL dibuang", "masalah_utama" not in d["prospect_context"])


# ===========================================================================
bagian("K. KONSISTENSI WORKFLOW (statis)")
# ===========================================================================
import re as _re

def _tanpa_komentar(kode):
    """Buang komentar // dan /* */ supaya nama node yang cuma DISEBUT di komentar
    (mis. node lama yang sudah dihapus) tidak dihitung sebagai rujukan hidup."""
    kode = _re.sub(r"/\*[\s\S]*?\*/", "", kode)
    return "\n".join(_re.sub(r"//.*$", "", b) for b in kode.split("\n"))


_rujukan_hilang = []
for _n in wf["nodes"]:
    _p = _n.get("parameters", {})
    _teks = _tanpa_komentar(_p.get("jsCode", "")) + "\n" + json.dumps(
        {k: v for k, v in _p.items() if k != "jsCode"}, ensure_ascii=False)
    for _ref in set(_re.findall(r"\$\('([^']+)'\)", _teks)):
        if _ref not in NODES:
            _rujukan_hilang.append("%s -> $('%s')" % (_n["name"], _ref))
cek("K1  semua rujukan $('NodeLain') menunjuk node yang ada",
    not _rujukan_hilang, "; ".join(_rujukan_hilang))

# jangkauan dari webhook aktif
_aktif = {n["name"] for n in wf["nodes"] if not n.get("disabled")}
_mulai = [n["name"] for n in wf["nodes"]
          if n["type"].endswith(".webhook") and not n.get("disabled")]
_terjangkau, _antre = set(_mulai), list(_mulai)
while _antre:
    _n = _antre.pop()
    for _br in CONNS.get(_n, {}).get("main", []):
        for _t in (_br or []):
            if _t["node"] not in _terjangkau:
                _terjangkau.add(_t["node"])
                _antre.append(_t["node"])
cek("K2  jalur utama tersambung dari Webhook sampai pengiriman WA",
    {"Bootstrap Config", "Chat Counter", "AI Agent", "Process All",
     "Send WA + Verify (Kirimi)"} <= _terjangkau,
    str(sorted({"Bootstrap Config", "Chat Counter", "AI Agent", "Process All",
                "Send WA + Verify (Kirimi)"} - _terjangkau)))
cek("K2b IF (Whitelist) TIDAK terjangkau lagi", "IF (Whitelist)" not in _terjangkau)

_yatim = sorted(n["name"] for n in wf["nodes"]
                if not n.get("disabled")
                and not n["type"].endswith(".webhook")
                and n["name"] not in _terjangkau
                and n["type"].split(".")[-1] not in
                ("memoryBufferWindow", "lmChatDeepSeekThinking"))
cek("K3  tidak ada node aktif yang menggantung di luar jalur",
    not _yatim, "yatim: " + ", ".join(_yatim))

# model & parameter LLM
_chat = NODES["DeepSeek Personal Chat"]["parameters"]
_sum = NODES["DeepSeek Personal Summary"]["parameters"]
cek("K4  model chat prospek = deepseek-v4-pro", _chat.get("model") == "deepseek-v4-pro",
    str(_chat.get("model")))
cek("K5  model ringkasan ke Steven = deepseek-v4-flash",
    _sum.get("model") == "deepseek-v4-flash", str(_sum.get("model")))
cek("K6  temperature chat tetap 0.7 (keputusan Steven, jangan diturunkan)",
    _chat["options"].get("temperature") == 0.7, str(_chat["options"].get("temperature")))
cek("K7  maxTokens chat cukup untuk brief 33 baris + [FACTS]",
    _chat["options"].get("maxTokens", 0) >= 2500, str(_chat["options"].get("maxTokens")))

# rantai teks: apa yang dikirim = apa yang disimpan
_kirim = NODES["Send WA + Verify (Kirimi)"]["parameters"]["jsCode"]
cek("K8  Kirimi mengirim Process All.cleanOutput",
    "$('Process All').first().json.cleanOutput" in _kirim)
_stats = NODES["Update to STATS"]["parameters"]["columns"]["value"]
cek("K9  STATS.last_bot_reply diisi dari cleanOutput yang sama",
    _stats.get("last_bot_reply") == "={{ $('Process All').first().json.cleanOutput }}",
    str(_stats.get("last_bot_reply")))
cek("K10 STATS.last_bot_reply_ts ikut ditulis", "last_bot_reply_ts" in _stats)
cek("K11 bot_mode hanya OFF lewat matikanBot",
    "matikanBot" in _stats.get("bot_mode", "")
    and "matikanBot" in NODES["Update row in sheet"]["parameters"]["columns"]["value"].get("bot_mode", ""),
    str(_stats.get("bot_mode")))
cek("K12 deck_requested konsisten di dua node penulis STATS",
    "deckNotify" in _stats.get("deck_requested", "")
    and "deckNotify" in NODES["Update STATS Brief"]["parameters"]["columns"]["value"].get("deck_requested", ""))

# system message
_sm = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]
cek("K13 system message memuat aturan BALASAN TERAKHIRKU", "BALASAN TERAKHIRMU" in _sm)
cek("K14 system message memuat aturan 'satu kata = jawaban'",
    "adalah JAWABAN atas pertanyaan itu" in _sm)
for _ph in ("prospect_context", "brief_context", "about_context",
            "program_context", "links_context", "faq_context"):
    cek("K15 placeholder {{ $json.%s }} terpasang" % _ph, "$json." + _ph in _sm)

# kolom STATS baru harus konsisten antara penulis dan pembaca
_baca = NODES["Cek_user_status"]["parameters"]["jsCode"] + NODES["Resolve User Row"]["parameters"]["jsCode"]
cek("K16 kolom last_bot_reply ditulis DAN dibaca",
    "last_bot_reply" in json.dumps(_stats) and "last_bot_reply" in _baca)

# tidak ada sisa override yang menciptakan desinkronisasi ingatan
_pa = NODES["Process All"]["parameters"]["jsCode"]
cek("K17 override 'Boleh tahu nama bisnisnya' sudah tidak ada di kode",
    "Boleh tahu nama bisnisnya dulu kak" not in _pa)
cek("K18 setiap penggantian teks yang tersisa menandai replyOverridden",
    _pa.count("replyOverridden = true") == 2, str(_pa.count("replyOverridden = true")))
cek("K19 rapikanUrl berada di lingkup atas (bukan di dalam if)",
    _re.search(r"^const rapikanUrl = ", _pa, _re.M) is not None)


# ===========================================================================
bagian("L. PENGERASAN 2026-09-06 — dua error produksi (H1, H2)")
# ===========================================================================
# H1 — Resolve User Row tidak boleh memerahkan execution untuk pesan yang
# memang sudah dibuang Chat Counter. `Read User STATS` bersetel
# alwaysOutputData:true, jadi item kosong tetap mengalir ke sini.

r = jalan("Resolve User Row",
          nodes={"Chat Counter": [item()], "Read User STATS": items(BARIS)},
          inp=[item()])
cek("L1  input Chat Counter kosong ({}) -> berhenti tanpa error",
    r["err"] is None and keluar_json(r) == [], r["err"] or str(keluar_json(r)))
cek("L2  alasannya dicatat di log, bukan didiamkan total",
    any("Chat Counter membuang pesan ini di hulu" in s for s in r["logs"]), str(r["logs"]))

# payload asing yang sungguhan tetap harus berisik
r = jalan("Resolve User Row",
          nodes={"Chat Counter": [item(user_phone="", user_lid="", body={"aneh": 1})],
                 "Read User STATS": items(BARIS)},
          inp=[item()])
cek("L3  payload berisi tapi tanpa identitas -> TETAP throw",
    r["err"] is not None and "Identitas user kosong" in r["err"], str(r["err"]))

# regresi: pesan normal tidak terpengaruh
d = satu(resolve({"user_phone": "6289900112233", "user_lid": ""}))
cek("L4  pesan normal tetap resolve seperti biasa",
    d is not None and d["resolved_key"] == "6289900112233" and d["row_found"] is True)

# rantai nyata: reaction dibuang Chat Counter, lalu Resolve User Row diam
r = chat_counter(payload(pesan="", messageType="reaction"))
cek("L5  Chat Counter membuang reaction", keluar_json(r) == [])


# H2 — Parse Config berhenti di tempat penyebabnya, bukan enam node kemudian.
def baris_cfg(**over):
    d = {"bot_name": "VIRA", "admin_phone": "6285171701168",
         "kirimi_user_code": "KM40LI0426",
         "kirimi_secret": "REDACTED",
         "kirimi_device_id": "D-BTUYM", "vision_mode": "full",
         "rate_limit_max": "15", "debounce_seconds": "60"}
    d.update(over)
    return [{"key": k, "value": v} for k, v in d.items() if v is not None]


def parse_cfg(rows_cfg, sheet_id="SHEET"):
    return jalan("Parse Config",
                 nodes={"Read CONFIG": items(*rows_cfg) if rows_cfg else [],
                        "Bootstrap Config": [item(sheet_id=sheet_id)]},
                 inp=[item()])


r = parse_cfg(baris_cfg())
d = satu(r)
cek("L6  CONFIG lengkap -> tidak throw", r["err"] is None, str(r["err"]))
cek("L7  nilai kirimi terbaca utuh",
    d and d["config"]["kirimi_user_code"] == "KM40LI0426"
      and d["config"]["kirimi_device_id"] == "D-BTUYM")

r = parse_cfg([])
cek("L8  tab CONFIG 0 baris -> throw menyebut tab CONFIG",
    r["err"] is not None and "Tab CONFIG terbaca kosong" in r["err"], str(r["err"]))

# bentuk yang sebenarnya terjadi: alwaysOutputData mengeluarkan SATU item kosong
r = parse_cfg([{}])
cek("L9  satu item kosong (efek alwaysOutputData) -> throw juga",
    r["err"] is not None and "Tab CONFIG terbaca kosong" in r["err"], str(r["err"]))
cek("L10 pesannya menyebut sheet_id supaya bisa dicek aksesnya",
    r["err"] is not None and "SHEET" in r["err"], str(r["err"]))

# insiden 2026-09-06 persis: nilai masih ada, NAMA KUNCINYA yang tertimpa jadi 'f'
rows = [x for x in baris_cfg() if x["key"] != "kirimi_user_code"]
rows.insert(2, {"key": "f", "value": "KM40LI0426"})
r = parse_cfg(rows)
cek("L11 kunci kirimi_user_code hilang -> throw menyebut kunci itu",
    r["err"] is not None and "kirimi_user_code" in r["err"], str(r["err"]))
cek("L12 pesannya membedakan 'barisnya ketemu' dari 'nilainya kosong'",
    r["err"] is not None and "nama kuncinya" in r["err"], str(r["err"]))
cek("L13 dua kunci lain dilaporkan ADA barisnya",
    r["err"] is not None and "kirimi_secret, kirimi_device_id" in r["err"], str(r["err"]))

r = parse_cfg(baris_cfg(kirimi_secret=""))
cek("L14 nilai ada barisnya tapi kosong -> tetap throw",
    r["err"] is not None and "kirimi_secret" in r["err"], str(r["err"]))

# kunci non-kritis boleh kosong: itu bukan alasan mematikan bot
r = parse_cfg(baris_cfg(survey_slots=None, media_catalog=None, client_name=None))
cek("L15 kunci non-kritis kosong -> TIDAK throw", r["err"] is None, str(r["err"]))

d = satu(parse_cfg(baris_cfg()))
cek("L16 whitelist_enabled default false (mode iklan)",
    d and d["config"]["whitelist_enabled"] is False)


# ===========================================================================
print()
print("=" * 72)
print("RINGKASAN UAT")
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
print("UAT MANUAL — wajib dijalankan di nomor asli sebelum iklan menyala")
print("-" * 72)
for i, langkah in enumerate([
    "SUDAH: kolom last_bot_reply + last_bot_reply_ts ada di tab STATS (terverifikasi 2026-09-06).",
    "SUDAH: whitelist_enabled=false, bot_wa_number=6285155202354 (terverifikasi 2026-09-06).",
    "CONFIG: pastikan sel A10 berbunyi kirimi_user_code (sempat tertimpa huruf f), dan naikkan rate_limit_max 5 -> 15.",
    "Import 2026-09-06-VIRA-Personal-Main-v3.1.json, aktifkan, matikan versi lama. Tunggu ~2 menit sebelum menguji: execution yang masih menggantung di node Wait akan bangun memakai definisi baru dan bisa error sekali.",
    "Chat dari nomor KETIGA (bukan 2 nomor uji lama) - harus dibalas. Ini bukti P0-1 beres.",
    "Ulang persis alur 2026-09-05: tanya AI CS -> sebut bidang -> tanya harga -> "
    "'udah itu aja' -> terima tawaran deck dengan 'boleh' -> jawab nama bisnis. "
    "VIRA harus mengenali nama bisnis itu, dan Steven harus menerima notif brief.",
    "Kirim 'boleh minta brosurnya' saat LINKS tidak punya brosur - balasan tidak boleh menjanjikan file.",
    "Kirim 'chat paling ramai hari senin' - VIRA harus tetap membalas (bot tidak mati).",
    "Kirim 'mau ngobrol langsung sama Steven' - notif handover masuk DAN bot berhenti.",
    "Cek kolom STATS.last_bot_reply terisi teks balasan terakhir.",
], 1):
    print("  %d. %s" % (i, langkah))

sys.exit(1 if gagal else 0)
