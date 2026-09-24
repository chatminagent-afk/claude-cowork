# -*- coding: utf-8 -*-
"""
_uat_2026-09-18.py — UAT perilaku untuk 2026-09-18-VIRA-Personal-Main-v3.10.json.

Diturunkan dari _uat_2026-09-15.py (jangan diedit manual — ubah generatornya,
_buat_uat_2026-09-18.py, lalu jalankan ulang). Seksi A-Q dan S ikut jalan sebagai regresi;
seksi T baru untuk uji Steven 2026-09-17, seksi R membedah v3.10 terhadap export live.

Berbeda dari _qa_*.py yang hanya memeriksa struktur, berkas ini MENJALANKAN kode
JavaScript asli dari node-node workflow di dalam mesin V8 (py-mini-racer), dengan
$(), $input, $getWorkflowStaticData, $vars, dan console yang dipalsukan persis
seperti yang disediakan n8n. Jadi yang diuji adalah kode yang benar-benar akan
jalan di produksi, bukan tiruannya.

Yang TETAP tidak bisa diuji di sini: apakah Google Sheets menulis baris yang benar,
apakah Kirimi mengirim, dan apakah model DeepSeek benar-benar mengeluarkan tag.
Tiga itu butuh nomor aktif — lihat daftar UAT manual di akhir keluaran.

Jalankan: python _uat_2026-09-18.py
Keluar dengan kode 1 kalau ada satu saja skenario GAGAL.
"""
import json
import os
import sys

from py_mini_racer import MiniRacer

DIR = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(DIR, "2026-09-18-VIRA-Personal-Main-v3.10.json")

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
print("UAT PERILAKU — VIRA Personal v3.2 (2026-09-06b)")
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
# n8n tidak mengekspor parameter bernilai default; default paket = deepseek-v4-flash
cek("K5  model ringkasan ke Steven = deepseek-v4-flash (eksplisit atau default node)",
    _sum.get("model", "deepseek-v4-flash") == "deepseek-v4-flash", str(_sum.get("model")))
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
bagian("M. GERBANG IDENTITAS — event perangkat Kirimi (H3)")
# ===========================================================================
# Payload asli yang memerahkan produksi 2026-09-06 11:25 WIB.
DEVICE_EVENT = {"event": "device.last_active", "deviceId": "D-BTUYM",
                "timestamp": 1788668758, "message": "Device last active updated",
                "datetime_wib": "2026-09-06 11:25:59"}

r = chat_counter(DEVICE_EVENT)
cek("M1  device.last_active dibuang di Chat Counter", keluar_json(r) == [],
    str(keluar_json(r)))
cek("M2  alasannya terekam beserta nama event",
    any("payload tanpa pengenal" in s and "device.last_active" in s for s in r["logs"]),
    str(r["logs"]))
cek("M3  daftar field payload ikut dicatat untuk forensik",
    any("deviceId" in s and "field=" in s for s in r["logs"]), str(r["logs"]))

# rantai penuh: sesudah Chat Counter membuang, Resolve User Row tidak boleh throw
r2 = jalan("Resolve User Row",
           nodes={"Chat Counter": [item()], "Read User STATS": items(BARIS)},
           inp=[item()])
cek("M4  Resolve User Row diam saat Chat Counter sudah membuang",
    r2["err"] is None and keluar_json(r2) == [], r2["err"] or str(keluar_json(r2)))

# bentuk event perangkat lain yang belum pernah kita lihat -> tetap terbuang
for ev in ("session.status", "device.disconnected", "qr.updated", "ack"):
    r = chat_counter({"event": ev, "deviceId": "D-BTUYM", "message": "sesuatu"})
    cek("M5  event '%s' tanpa pengenal ikut terbuang" % ev, keluar_json(r) == [])

# event perangkat TANPA field message pun tetap aman (dulu lolos ke gerbang lain)
r = chat_counter({"event": "device.last_active", "deviceId": "D-BTUYM"})
cek("M6  event perangkat tanpa teks juga dibuang", keluar_json(r) == [])

# ── yang TIDAK boleh ikut terbuang ─────────────────────────────────────────
r = chat_counter(payload(frm="6289900112233", pesan="halo mau tanya"))
d = satu(r)
cek("M7  pesan normal tetap lolos", d is not None and d["user_phone"] == "6289900112233",
    str(r["err"] or keluar_json(r)))

r = chat_counter(payload(frm="79255182508173@lid", pesan="halo", originLid="79255182508173"))
d = satu(r)
cek("M8  pengirim @lid tetap lolos", d is not None and d["user_lid"] == "79255182508173")

# nomor hanya ada di senderAlt: sebelum patch ini chatnya hilang diam-diam
r = chat_counter({"message": "halo", "messageType": "text", "senderAlt": "6289900112233",
                  "isFromGroup": False, "isFromMe": False})
cek("M9  pesan yang pengenalnya cuma di senderAlt TIDAK dibuang",
    len(keluar_json(r)) == 1, str(r["logs"]))

# gambar tanpa caption: hasText false, tapi pengenal ada -> harus lolos
r = chat_counter(payload(frm="6289900112233", pesan="", messageType="image",
                         mediaUrl="https://x/y.jpg", mimetype="image/jpeg"))
d = satu(r)
cek("M10 gambar tanpa caption tetap lolos", d is not None and d["media_kind"] == "image",
    str(r["err"] or keluar_json(r)))

# gerbang lama tidak boleh tergeser: reaction dari nomor SAH tetap dibuang
r = chat_counter(payload(frm="6289900112233", pesan="", messageType="reaction"))
cek("M11 reaction dari nomor sah tetap dibuang (gerbang 1 utuh)", keluar_json(r) == [])

# urutan gerbang: identitas diperiksa SEBELUM gerbang tipe pesan
_cc = NODES["Chat Counter"]["parameters"]["jsCode"]
cek("M12 gerbang identitas berada sebelum gerbang DROP_TYPES",
    _cc.find("_adaPengenal") < _cc.find("DROP_TYPES.includes(messageType)"))
cek("M13 gerbang identitas memakai warn, bukan throw",
    "console.warn('STOP: payload tanpa pengenal" in _cc)


# ===========================================================================
bagian("L. HARGA — insiden studysipil 2026-09-07 (kebocoran angka ke lead dingin)")
# ===========================================================================
# Pesan asli prospek, empat baris yang digabung debounce 60 detik jadi satu
# giliran. Kata `promo` dan `harga` dua-duanya milik PELANGGAN DIA.
INSIDEN = ("biasanya pas lg promo buka kelas sih\n"
           "ads itu pasti pd tanya hal yg sama\n"
           "harga, kuota, apa aja yg didapet\n"
           "sama jadwalnya kapan")

d = pre(INSIDEN)
cek("L1  pesan insiden TIDAK memicu konteks harga",
    d["askingPrice"] is False, d["aiContext"])
cek("L1b pesan insiden tidak menyuntik blok [CONTEXT] harga",
    "menanyakan harga" not in d["ai_input_text"], d["ai_input_text"][-200:])

for pesan in ["pelanggan sering nanya harga sama ongkir",
              "customer pd nanyain harga terus",
              "mereka biasanya tanya harga, stok, sama ukuran",
              "yang ditanya itu itu aja sih, harga sama jadwal",
              "calon murid pasti nanya biaya dulu"]:
    d = pre(pesan)
    cek("L2  '%s' = cerita pelanggan, bukan tanya harga" % pesan,
        d["askingPrice"] is False, d["aiContext"])

for pesan in ["biaya adminku sebulan sekitar 3 juta",
              "harga kelasku 500rb per murid",
              "paket kelas aku ada 3 kak",
              "adminku ada 2 orang, biayanya 4 juta"]:
    d = pre(pesan)
    cek("L3  '%s' = angka miliknya (jawaban TINGKAT 2B)" % pesan,
        d["askingPrice"] is False, d["aiContext"])

for pesan in ["harganya berapa ya", "biaya bulanannya gimana",
              "paket premium berapa harganya", "harganya gabisa kurang ya?",
              "boleh minta pricelist?", "mahal ga sih?", "ada diskon ga kak?",
              "kalau paket basic dapat apa aja?", "berapa biaya setupnya?",
              "oh gitu, btw harga viranya berapa kak?"]:
    d = pre(pesan)
    cek("L4  '%s' TETAP memicu konteks harga" % pesan, d["askingPrice"] is True)

d = pre("pelanggan sering nanya harga. btw berapa harga paket basic?")
cek("L5  cerita + pertanyaan asli di satu giliran tetap memicu harga",
    d["askingPrice"] is True, d["aiContext"])

for pesan in ["lagi promo buka kelas nih", "pelanggan bayar lewat transfer",
              "abis promo biasanya sepi"]:
    d = pre(pesan)
    cek("L6  '%s' (promo/bayar dicabut) TIDAK memicu harga" % pesan,
        d["askingPrice"] is False, d["aiContext"])

d = pre("harganya berapa ya")
cek("L7  aiContext harga TIDAK lagi imperatif tanpa syarat",
    "User menanyakan harga. Sebut kisaran" not in d["aiContext"], d["aiContext"])
cek("L7b aiContext harga memuat syarat eksplisit",
    "Periksa dulu" in d["aiContext"] and "JANGAN sebut angka" in d["aiContext"],
    d["aiContext"])

d = pre("halo mau tanya soal ai customer service")
cek("L8  pesan netral tidak menyuntik [CONTEXT] apa pun",
    d["aiContext"] == "" and "[CONTEXT:" not in d["ai_input_text"], d["aiContext"])

_pre_src = NODES["Preprocess - Context Detection"]["parameters"]["jsCode"]
cek("L9  gerbang CERITA_ORANG_LAIN / MILIK_DIA / TANYA_HARGA_KITA terpasang",
    all(k in _pre_src for k in ("CERITA_ORANG_LAIN", "MILIK_DIA", "TANYA_HARGA_KITA")))
cek("L10 'promo' dan 'bayar' tidak lagi ada di KATA_HARGA",
    "promo" not in _pre_src.split("const KATA_HARGA")[1].split("\n")[0]
    and "bayar" not in _pre_src.split("const KATA_HARGA")[1].split("\n")[0])


# ===========================================================================
bagian("M. PROMPT v3.6 — aturan harga & pendalaman pain point")
# ===========================================================================
_sp = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]

cek("M1  prefix '=' (expression mode) dipertahankan", _sp.startswith("="))
cek("M2  enam ekspresi {{ }} tetap utuh",
    len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 6,
    str(len(_re.findall(r"\{\{[^}]+\}\}", _sp))))
cek("M3  # HARGA melarang angka saat kata harga milik orang lain",
    "milik orang lain bukan pertanyaan untukku" in _sp)
cek("M4  # HARGA menyuruh menahan angka saat ragu",
    "Kalau ragu, jangan sebut angka" in _sp)
cek("M5  MENGGALI punya pendalaman pain point sekali",
    "Sekali masalah utamanya keluar" in _sp and "sekali saja, jangan diulang" in _sp)
cek("M6  pendalaman menanyakan AKIBAT, bukan 'ada kendala lain?'",
    "AKIBATNYA" in _sp)
cek("M7  spek pain_points menyebut pemisah titik koma",
    "dipisah titik koma" in _sp)
cek("M8  spek pain_points melarang mengulang masalah_utama",
    "JANGAN mengulang isi masalah_utama" in _sp)
cek("M9  suntingan tangan di n8n live ikut tersalin (tidak tertimpa)",
    "kalau boleh tau nama usahanya apa ya kak?." in _sp)
cek("M10 larangan harga di kalimat tawaran deck (v3.5) tidak hilang",
    "JANGAN menempelkan harga pada tawaran ini" in _sp)
cek("M11 pain_points tetap ada di daftar field [DECK_REQUEST]",
    "\n  pain_points: ...\n" in _sp)

# --- pecah_pain ASLI dari buat_deck.py: buktikan ';' menghasilkan >2 poin ---
_bd = os.path.join(os.path.dirname(DIR), "deck", "buat_deck.py")
if os.path.exists(_bd):
    with open(_bd, encoding="utf-8") as _f:
        _src_bd = _f.read()
    _m = _re.search(r"^def pecah_pain\(d\):.*?(?=\n(?:def |# |@|\Z))",
                    _src_bd, _re.S | _re.M)
    cek("M12 fungsi pecah_pain ditemukan di buat_deck.py", _m is not None)
    if _m:
        _ns = {}
        exec(_m.group(0), _ns)
        _pecah = _ns["pecah_pain"]

        # perilaku LAMA: pain_points satu kalimat -> selalu tepat 2 poin
        _lama = _pecah({"masalah_utama": "kewalahan balas chat saat promo",
                        "pain_points": "chat numpuk saat fokus ke hal lain"})
        cek("M13 satu kalimat pain_points = hanya 2 poin (gejala lama)",
            len(_lama) == 2, str(len(_lama)))

        # perilaku BARU: dipisah ';' -> lebih dari 2 poin, sampai 6
        _baru = _pecah({"masalah_utama": "kewalahan balas chat saat promo",
                        "pain_points": "ada calon murid yang kelewat nggak dibalas; "
                                       "chat masuk tengah malam nggak keurus; "
                                       "jawaban beda-beda tiap kali ditanya"})
        cek("M14 pain_points dipisah ';' menghasilkan 4 poin", len(_baru) == 4,
            str(len(_baru)))
        cek("M15 masalah_utama tetap jadi poin pertama",
            _baru[0]["judul"].startswith("kewalahan balas chat"))
        _enam = _pecah({"masalah_utama": "a", "pain_points": ";".join("bcdefgh")})
        cek("M16 batas atas 6 poin dihormati", len(_enam) == 6, str(len(_enam)))
else:
    cek("M12 buat_deck.py ditemukan", False, _bd)


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
        ("Usahanya di bidang apa kak? Sehari ada berapa chat masuk?", ["industri", "volume_chat"]),
        ("Btw boleh tau nama kakak siapa, dan nama usahanya apa?", ["nama_bisnis", "nama_lengkap"]),
        ("Nama adminnya siapa, dan nama brandnya apa?", ["nama_bisnis"])]:
    got = detek(kal)
    cek("N1  detektor '%s' -> %s" % (kal[:55], harap), got == harap, str(got))


def tangkap(pesan, lalu, ai="Oke kak.", prev=None):
    pr = {"last_bot_reply": lalu}
    pr.update(prev or {})
    return satu(proses(ai, pesan_user=pesan, prev_row=pr))


for pesan, harap in [("Budi", "Budi"), ("aku Callista", "Callista"), ("panggil aja Rina kak", "Rina"),
                     ("nama saya Dewi", "Dewi"), ("saya Andi, owner Andi Bakery", "Andi"),
                     ("halo kak, budi santoso", "Budi Santoso"), ("Budi 😊", "Budi"),
                     ("Budi\nmau tanya harga vira", "Budi"), ("ehm, Budi kak", "Budi"),
                     ("dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?", "Aldi"),
                     ("ini dengan aldi", "Aldi"), ("saya dengan Rina", "Rina"), ("sama budi kak", "Budi")]:
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


_NB = {"nama_bisnis": "Kopi Senja"}   # nama usaha sudah ada -> jalur galian biasa
for baris, harap, judul in [
        ({"greeting_sent": ""}, "namanya dan nama usahanya", "pesan perkenalan -> tanya nama DAN nama usaha"),
        ({"greeting_sent": "", "nama_lengkap": "Budi"}, "nama usahanya — tanyakan di",
         "perkenalan, nama sudah ada -> tanya nama usaha saja"),
        ({"greeting_sent": "", "nama_lengkap": "Budi", "nama_bisnis": "Kopi Senja"}, None,
         "perkenalan, keduanya sudah ada -> tidak menggali apa pun"),
        ({"greeting_sent": "Y", "Counter": "1"}, "nama usahanya — tanya ulang", "giliran 2, nama usaha kosong -> tanya ulang"),
        (dict({"greeting_sent": "Y", "Counter": "1"}, **_NB), "bidang usahanya", "giliran 2, nama usaha ada -> bidang usaha"),
        (dict({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": "Usahanya di bidang apa kak?"}, **_NB), None,
         "bidang usaha baru ditanyakan & belum dijawab -> jeda satu balasan"),
        ({"greeting_sent": "Y", "Counter": "3"}, "bidang usahanya", "giliran 4 -> jendela tanya ulang habis, bidang usaha"),
        ({"greeting_sent": "Y", "Counter": "5"}, "bidang usahanya", "giliran 6 -> bidang usaha masih dalam jendela (v3.10: 2-6)"),
        ({"greeting_sent": "Y", "Counter": "6"}, "masalah terbesarnya", "giliran 7 -> jendela bidang usaha habis, lanjut masalah"),
        (dict({"greeting_sent": "Y", "Counter": "2", "industri": "sipil"}, **_NB), "masalah terbesarnya", "bidang usaha ada -> masalah"),
        (dict({"greeting_sent": "Y", "Counter": "1", "industri": "sipil"}, **_NB), "masalah terbesarnya",
         "giliran 2, nama usaha & bidang sudah ada -> langsung masalah"),
        ({"greeting_sent": "Y", "Counter": "4", "industri": "sipil",
          "last_bot_reply": "Soal chat, yang paling bikin repot sekarang apa kak?"}, None, "masalah baru ditanyakan -> jeda"),
        ({"greeting_sent": "Y", "Counter": "7", "industri": "sipil"}, "masalah terbesarnya",
         "giliran 8 -> masalah masih dalam jendela (v3.10: 2-8)"),
        ({"greeting_sent": "Y", "Counter": "8", "industri": "sipil"}, None, "giliran 9 -> jendela masalah habis"),
        ({"greeting_sent": "Y", "Counter": "3", "industri": "sipil", "masalah_utama": "x"}, "kira-kira berapa chat",
         "masalah ada -> jumlah chat"),
        ({"greeting_sent": "Y", "Counter": "9", "industri": "sipil", "masalah_utama": "x"}, "kira-kira berapa chat",
         "giliran 10 -> jumlah chat masih dalam jendela (v3.10: 3-10)"),
        ({"greeting_sent": "Y", "Counter": "10", "industri": "sipil", "masalah_utama": "x"}, None,
         "giliran 11 -> jendela jumlah chat habis"),
        ({"greeting_sent": "Y", "Counter": "3", "industri": "sipil", "masalah_utama": "x", "volume_chat": "20"}, None,
         "semua terisi -> tidak menggali"),
        (dict({"greeting_sent": "Y", "Counter": "1", "nama_lengkap": ""}, **_NB), "bidang usahanya",
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
cek("Q4  nama ditanya SEKALI di perkenalan, tidak diulang", "Namanya kutanyakan SEKALI: kalau dia tidak menjawab" in _sp
    and "jangan ditanyakan lagi" in _sp)
cek("Q5  PERKENALAN tetap intro biasa + tanya nama & nama usaha",
    "tutup dengan SATU kalimat pendek yang menanyakan namanya" in _sp
    and "jawaban singkat kalau dia bertanya, lalu pertanyaan nama dan nama usaha" in _sp.replace("\n", " "))
cek("Q6  ALUR 7 mengikuti galian_berikutnya", "itu SATU-SATUNYA pertanyaan galian di balasan ini" in _sp)
cek("Q7  empat galian hanya lewat baris itu",
    "Nama, nama usaha, bidang usaha, masalah utama, dan jumlah chat per hari hanya kutanyakan lewat baris itu" in _sp)
cek("Q8  nama_wa BUKAN nama asli", "Itu BUKAN nama yang dia sebutkan" in _sp)
cek("Q9  [FACTS] wajib saat menjawab galian", "Setiap kali dia menjawab pertanyaan galianku, tulis `[FACTS]`" in _sp)
cek("Q10 budget tetap Tingkat 3 (tidak pernah ditanya)", "leadsnya datang, anggarannya" in _sp)
cek("Q11 prompt tidak menyuruh menanyakan minat paket",
    not _re.search(r"(tanya|tanyakan)[^.\n]{0,40}(basic atau premium|minat paket|paket mana)", _sp, _re.I))
cek("Q12 prompt merujuk baris galian_berikutnya yang benar-benar dibuat Rakit Konteks",
    "`galian_berikutnya`" in _sp and "galian_berikutnya: " in NODES["Rakit Konteks"]["parameters"]["jsCode"])

_par = _sp.split("Baris `galian_berikutnya`")[1].split("\n\n")[0]
_cth = [k.replace("\n", " ") for k in _re.findall(r'"([^"]+)"', _par)]
_harap = [["nama_bisnis"], ["industri"], ["masalah_utama"], ["volume_chat"]]
cek("Q13 empat contoh kalimat galian ditemukan", len(_cth) == 4, str(_cth))
for _k, _h in zip(_cth, _harap):
    cek("Q14 contoh prompt '%s' terbaca detektor sebagai %s" % (_k, _h), detek(_k) == _h, str(detek(_k)))
_bag = _sp.split("# NAMA LAWAN BICARA")[1].split("\n# GAYA")[0]
_q15 = [k for k in _re.findall(r'"([^"]*siapa[^"]*)"', _bag) if len(k.split()) >= 3]
cek("Q15 bagian NAMA punya contoh kalimat tanya nama", len(_q15) >= 1, str(_q15))
for _k in _q15:
    _hq = ["nama_bisnis", "nama_lengkap"] if "nama usaha" in _k else ["nama_lengkap"]
    cek("Q15 contoh tanya nama '%s' terbaca sebagai %s" % (_k, _hq), detek(_k) == _hq, str(detek(_k)))
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
    g, _ = galian2({"greeting_sent": "Y", "Counter": "1", "nama_bisnis": "Kopi Senja"}, pesan)
    cek("S9  '%s' (tidak bertanya) -> galian bidang usaha jalan" % pesan,
        g is not None and g.startswith("bidang usahanya"), str(g))
g, _ = galian2({"greeting_sent": ""}, "halo, harganya berapa?")
cek("S10 pesan perkenalan yang bertanya tetap menanyakan nama", g is not None and g.startswith("namanya"), str(g))
g, d = galian2({"greeting_sent": "Y", "Counter": "1"}, "oke")
cek("S11 tanpa nama tersimpan -> tidak ada baris panggilan", "panggilan:" not in d["prospect_context"])
cek("S11b IS_NEW_USER tetap baris terakhir", d["prospect_context"].rstrip().endswith("IS_NEW_USER: false"))


# ===========================================================================
bagian("T. UJI 2026-09-17 — nama usaha di perkenalan, jawaban gabungan, balasan ringkas")
# ===========================================================================
_sp = NODES["AI Agent"]["parameters"]["options"]["systemMessage"]
_sp1 = _sp.replace("\n", " ")
PERKENALAN_BARU = ("Halo kak, aku Steven versi AI. Aku dibangun sama Steven pakai sistem yang sama yang dia "
                   "bikin untuk kliennya, namanya VIRA. Jadi kalau kakak penasaran hasilnya kayak apa, kakak "
                   "lagi ngobrol sama contohnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa?")
INTRO_1709 = ("Halo kak, salam kenal. Aku Steven versi AI, asisten yang dibangun Steven pakai sistem yang sama "
              "dengan yang dia tawarkan untuk kliennya, namanya VIRA. Jadi kalau kakak penasaran hasilnya seperti "
              "apa, kakak lagi ngobrol sama contohnya sekarang. Senang kakak sudah lihat website-nya. Boleh cerita "
              "dulu bisnis kakak di bidang apa, dan apa yang bikin kakak tertarik cari AI customer service? Btw, "
              "boleh tau namanya siapa kak?")
JAWAB_1709 = "Nadia kak, bisnis aku katering, chat suka numpuk pas malem"
BALAS_1709 = ("Salam kenal Nadia. Chat katering memang paling ramai pas malam hari, apalagi kalau orang baru "
              "pulang kerja dan mulai mikir pesanan. Kalau lagi numpuk gitu, biasanya yang paling bikin repot "
              "bagian mananya kak?")

# --- T1 prompt: perkenalan ---
_perk = _sp.split("# PERKENALAN")[1].split("\n# NAMA LAWAN BICARA")[0]
_m = _re.search(r'"(btw boleh tau nama kakak siapa, dan nama usahanya apa\?)"', _perk)
cek("T1  PERKENALAN memberi contoh SATU kalimat nama + nama usaha", _m is not None)
cek("T1b contoh itu terbaca detektor sebagai dua slot", _m and detek(_m.group(1)) == ["nama_bisnis", "nama_lengkap"],
    str(_m and detek(_m.group(1))))
cek("T2  'apa yang bikin dia tertarik' dibuang dari prompt", "apa yang bikin dia tertarik" not in _sp)
cek("T2b pesan perkenalan dilarang menanyakan hal lain (bidang, masalah, alasan tertarik)",
    "JANGAN menanyakan apa pun di pesan ini — bukan bidang usahanya, bukan masalahnya" in _sp1)
cek("T3  larangan lama menggabung nama + nama usaha sudah dihapus",
    "Jangan digabung dengan pertanyaan nama usaha" not in _sp and "Jangan dipecah" in _sp)
cek("T3b cara membaca jawaban gabungan dijelaskan (jenis usaha -> industri)",
    "Cara membaca jawabannya" in _sp and "itu `industri` — nama usahanya berarti belum dia sebut" in _sp1)
cek("T4  TINGKAT 1: nama usaha tidak lagi 'saat menawarkan decknya'",
    "Momen paling wajar: saat menawarkan decknya" not in _sp
    and "nama usahanya kutanyakan di pesan perkenalan bersama namanya" in _sp1)
cek("T4b kalimat tawaran deck tetap jadi jaring terakhir", "kalau boleh tau nama usahanya apa ya kak?." in _sp)
cek("T4c [FACTS] menjelaskan pertanyaan gabungan", "nama dan nama usahanya sekaligus → dua-duanya" in _sp)

# --- T5 prompt: balasan ringkas ---
_gaya = _sp.split("\n# GAYA\n")[1].split("\n# MENGGALI")[0]
cek("T5  target panjang: DUA kalimat, 20-35 kata", "Panjang yang kuincar: DUA kalimat, kira-kira 20 sampai 35 kata" in _gaya.replace("\n", " "))
cek("T5b batas keras 3 kalimat tetap ada", "Maksimal 3 kalimat;" in _gaya and "itu batas keras" in _gaya)
cek("T5c larangan mengulang ucapan prospek", "JANGAN MENGULANG UCAPANNYA" in _gaya)
cek("T5d ALUR 10 menyuruh membuang kalimat yang mengulang sebelum mengirim",
    "buang kalimat yang cuma mengulang atau merangkum ucapannya" in _sp)
_pas = [k.replace("\n", " ") for k in _re.findall(r'(?:Pas: |— )"([^"]+)"', _gaya)]
cek("T5e dua contoh balasan 'pas' ditemukan", len(_pas) == 2, str(_pas))
for _k in _pas:
    _kal = len(_re.findall(r"[.?!](?:\s|$)", _k))
    _kata = len(_k.split())
    cek("T5f contoh pas '%s...' <= 2 kalimat & <= 35 kata (%d kal, %d kata)" % (_k[:30], _kal, _kata),
        _kal <= 2 and _kata <= 35)
_buruk = _re.search(r'Terlalu panjang[^"]*"([^"]+)"', _gaya)
cek("T5g contoh buruk memuat pembuka terlarang 'Jadi alurnya ada dua'",
    _buruk is not None and _buruk.group(1).startswith("Jadi alurnya ada dua"))
cek("T5h tidak ada nama prospek uji di prompt", "Nadia" not in _sp)
cek("T5i tidak ada tanda seru di contoh 'pas'", all("!" not in k for k in _pas))

# --- T6 detektor gabungan ---
for kal, harap in [
        (PERKENALAN_BARU, ["nama_bisnis", "nama_lengkap"]),
        ("Boleh tau nama kakak siapa dan nama usahanya apa kak?", ["nama_bisnis", "nama_lengkap"]),
        ("Namanya siapa kak, usahanya namanya apa?", ["nama_bisnis", "nama_lengkap"]),
        ("Boleh kenalan kak, namanya siapa dan usahanya namanya apa?", ["nama_bisnis", "nama_lengkap"]),
        ("Kalau boleh tau dengan kak siapa, dan nama tokonya apa?", ["nama_bisnis", "nama_lengkap"]),
        (INTRO_1709, ["industri", "nama_lengkap"]),
        ("Nama usahanya apa, dan yang balas chat siapa?", ["nama_bisnis"]),
        ("Nama pelanggannya siapa aja kak?", []),
        ("Oh iya, nama usahanya apa kak?", ["nama_bisnis"]),
        ("Usahanya bergerak di bidang apa kak, boleh cerita sedikit?", ["industri"])]:
    got = detek(kal)
    cek("T6  detektor '%s' -> %s" % (kal[-55:], harap), got == harap, str(got))

# --- T7 penangkap jawaban gabungan (model TIDAK menulis [FACTS]) ---
for pesan, nama, usaha, bidang in [
        ("Rina, Dapur Mama", "Rina", "Dapur Mama", ""),
        ("Rina kak, usahaku namanya Dapur Mama", "Rina", "Dapur Mama", ""),
        ("aku Rina dari Dapur Mama", "Rina", "Dapur Mama", ""),
        ("aku Rina, usahaku Dapur Mama", "Rina", "Dapur Mama", ""),
        ("Rina owner Kopi Senja", "Rina", "Kopi Senja", ""),
        ("Nama saya Rina, usaha saya Kopi Senja", "Rina", "Kopi Senja", ""),
        ("Rina\nKopi Senja", "Rina", "Kopi Senja", ""),
        ("Rina - Kopi Senja kak", "Rina", "Kopi Senja", ""),
        ("usahaku Kopi Senja, aku Rina", "Rina", "Kopi Senja", ""),
        ("Kopi Senja, aku Rina", "Rina", "Kopi Senja", ""),
        ("oke kak, aku Rina dari Toko Berkah Jaya", "Rina", "Berkah Jaya", ""),
        (JAWAB_1709, "Nadia", "", "katering"),
        ("Rina, katering rumahan", "Rina", "", "katering rumahan"),
        ("Rina, usahaku katering", "Rina", "", "katering"),
        ("aku Rina, jualan skincare", "Rina", "", "jualan skincare"),
        ("Rina", "Rina", "", ""),
        ("Rina kak", "Rina", "", ""),
        ("Rina dari Surabaya", "Rina", "", ""),
        ("Rina\nmau tanya harganya dong", "Rina", "", ""),
        ("Rina, belum ada nama usahanya kak", "Rina", "", ""),
        ("dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?", "Aldi", "", ""),
        ("harganya berapa kak?", "", "", ""),
        ("rahasia hehe", "", "", "")]:
    d = tangkap(pesan, PERKENALAN_BARU, ai="Salam kenal kak.")
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"])
    cek("T7  '%s' -> nama=%r usaha=%r bidang=%r" % (pesan.replace("\n", " / "), nama, usaha, bidang),
        got == (nama, usaha, bidang), str(got))

d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU, ai='Salam kenal kak.\n[FACTS nama="Rina Wati" nama_bisnis="Dapur Mama Rina"]')
cek("T8  [FACTS] dari model menang atas penangkap gabungan",
    d and d["nama_lengkap_merged"] == "Rina Wati" and d["nama_bisnis_merged"] == "Dapur Mama Rina" and d["slotTertangkap"] == "",
    str(d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["slotTertangkap"])))
d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU, ai='Salam kenal kak.\n[FACTS nama="Rina"]')
cek("T8b [FACTS] hanya nama -> nama usaha tetap ditangkap penangkap",
    d and d["nama_bisnis_merged"] == "Dapur Mama" and d["slotTertangkap"] == "nama_bisnis", str(d and d["slotTertangkap"]))
d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU, prev={"nama_bisnis": "Kopi Senja"})
cek("T8c nama usaha lama tidak pernah ditimpa", d and d["nama_bisnis_merged"] == "Kopi Senja" and d["nama_lengkap_merged"] == "Rina")
d = tangkap("Rina, Dapur Mama", PERKENALAN_BARU)
cek("T8d slotTertangkap mencatat dua kolom", d and d["slotTertangkap"] == "nama_lengkap,nama_bisnis", str(d and d["slotTertangkap"]))
d = tangkap("Dapur Mama", "Oh iya, nama usahanya apa kak?")
cek("T9  jawaban tanya ulang nama usaha ditangkap (jalur satu slot)",
    d and d["nama_bisnis_merged"] == "Dapur Mama" and d["slotTertangkap"] == "nama_bisnis", str(d and d["nama_bisnis_merged"]))
d = tangkap("Rina, Dapur Mama", "Nama usahanya apa, dan yang balas chat siapa?")
cek("T9b tanpa pertanyaan nama orang -> penangkap gabungan tidak jalan",
    d and d["nama_lengkap_merged"] == "", str(d and d["nama_lengkap_merged"]))

# --- T10 nama bocor: ulang persis uji 2026-09-17 ---
d = satu(proses(BALAS_1709, pesan_user=JAWAB_1709, prev_row={"last_bot_reply": INTRO_1709}))
cek("T10 uji 17/09: 'Salam kenal Nadia' -> 'Salam kenal kak' walau nama tidak tersimpan",
    d and d["cleanOutput"].startswith("Salam kenal kak.") and "nadia" not in d["cleanOutput"].lower()
    and d["namaDihapus"] is True, str(d and d["cleanOutput"][:60]))
cek("T10b kata 'katering' di balasan tidak tersentuh", d and "Chat katering memang paling ramai" in d["cleanOutput"])
cek("T10c perkenalan lama (bidang + nama) tetap tidak ditebak: nama tidak disimpan",
    d and d["nama_lengkap_merged"] == "", str(d and d["nama_lengkap_merged"]))
d = satu(proses("Halo Nadia, oke. Jadi Nadia mau tanya soal chat?", pesan_user=JAWAB_1709,
                prev_row={"last_bot_reply": INTRO_1709}))
cek("T10d nama tebakan hanya dihapus sesudah sapaan, tidak di tengah kalimat",
    d and d["cleanOutput"] == "Halo kak, oke. Jadi Nadia mau tanya soal chat?", str(d and d["cleanOutput"]))
d = satu(proses("Chat katering memang ramai kak. Biasanya pesan H berapa?", pesan_user="katering kak, aku Nadia",
                prev_row={"last_bot_reply": INTRO_1709}))
cek("T10e tebakan yang ternyata bukan nama ('katering') tidak merusak balasan",
    d and d["cleanOutput"] == "Chat katering memang ramai kak. Biasanya pesan H berapa?", str(d and d["cleanOutput"]))
d = satu(proses("Salam kenal Budi.", pesan_user="Budi", prev_row={"last_bot_reply": "Usahanya di bidang apa kak?"}))
cek("T10f tanpa pertanyaan nama sebelumnya -> tidak ada tebakan", d and d["cleanOutput"] == "Salam kenal Budi.")

# --- T11 alur baru, giliran demi giliran ---
PESAN1 = "Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku."
g, d = galian2({"greeting_sent": ""}, PESAN1)
cek("T11 pesan 1: galian = nama DAN nama usaha, satu kalimat",
    g is not None and g.startswith("namanya dan nama usahanya") and "SATU kalimat" in g, str(g))
g, _ = galian2({"greeting_sent": "", "nama_lengkap": "Rina"}, PESAN1)
cek("T11b pesan 1, nama sudah disebut -> nama usaha saja", g is not None and g.startswith("nama usahanya — tanyakan di"), str(g))
_bocor = [c for c in range(0, 13) for gs in ("",) for g, _ in [galian2({"greeting_sent": gs, "Counter": str(c)}, "oke")]
          if g and _re.search(r"bidang|masalah|chat masuk", g)]
cek("T11c perkenalan tidak pernah menggali bidang/masalah/jumlah chat", not _bocor, str(_bocor[:3]))

d = satu(proses("Salam kenal kak Nadia. Pas malam justru jam orang mikir pesanan, jadi yang telat dibalas "
                "biasanya pindah ke katering lain.", pesan_user=JAWAB_1709,
                prev_row={"last_bot_reply": PERKENALAN_BARU}))
cek("T12 pesan 2 (jawaban uji 17/09 atas perkenalan baru): nama & bidang tersimpan, nama usaha kosong",
    d and (d["nama_lengkap_merged"], d["industri_merged"], d["nama_bisnis_merged"]) == ("Nadia", "katering", ""),
    str(d and (d["nama_lengkap_merged"], d["industri_merged"], d["nama_bisnis_merged"])))
cek("T12b nama tidak dipakai menyapa", d and d["cleanOutput"].startswith("Salam kenal kak.") and "Nadia" not in d["cleanOutput"])

g, _ = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": PERKENALAN_BARU}, JAWAB_1709)
cek("T13 giliran 2, nama usaha belum tercatat -> tanya ulang (walau perkenalan baru saja menanyakannya)",
    g is not None and g.startswith("nama usahanya — tanya ulang SEKALI"), str(g))
cek("T13b baris tanya ulang memberi jalan keluar kalau nama usahanya ternyata sudah disebut",
    g is not None and "sudah menyebut nama usahanya, jangan ditanyakan" in g and "tanyakan bidang usahanya" in g, str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": PERKENALAN_BARU}, "Rina, harganya berapa kak?")
cek("T13c giliran 2 tapi prospek bertanya -> galian ditunda (pertanyaan dijawab dulu)", g is None, str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "last_bot_reply": "Basic mulai Rp3.000.000 per bulan kak."}, "oke")
cek("T13d tanya ulang yang tertunda jalan di giliran 3", g is not None and g.startswith("nama usahanya — tanya ulang"), str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "last_bot_reply": "Oh iya, nama usahanya apa kak?"}, "hmm nanti aja")
cek("T13e tanya ulang sudah dilakukan & tidak dijawab -> lanjut bidang usaha, TIDAK diulang lagi",
    g is not None and g.startswith("bidang usahanya"), str(g))
_ulang = []
for c in range(3, 13):
    for lalu in ("", "Oh iya, nama usahanya apa kak?", PERKENALAN_BARU):
        g, _ = galian2({"greeting_sent": "Y", "Counter": str(c), "last_bot_reply": lalu}, "oke")
        if g and g.startswith("nama usahanya"):
            _ulang.append((c, lalu[:20]))
cek("T13f nama usaha tidak pernah ditanya ulang sesudah giliran 3 (30 kombinasi)", not _ulang, str(_ulang[:3]))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "nama_lengkap": "Nadia", "nama_bisnis": "Dapur Nadia",
                "last_bot_reply": "Oh iya, nama usahanya apa kak?"}, "Dapur Nadia")
cek("T14 giliran 3, nama usaha sudah ada -> bidang usaha + cerita singkat",
    g is not None and g.startswith("bidang usahanya, sekaligus minta dia cerita singkat"), str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "nama_lengkap": "Nadia", "nama_bisnis": "Dapur Nadia",
                "industri": "katering", "last_bot_reply": "Oh iya, nama usahanya apa kak?"}, "Dapur Nadia")
cek("T14b giliran 3, bidang sudah ada -> masalah", g is not None and g.startswith("masalah terbesarnya"), str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "3", "nama_bisnis": "Dapur Nadia", "industri": "katering",
                "last_bot_reply": "Usahanya bergerak di bidang apa kak, boleh cerita sedikit?"}, "katering rumahan kak")
cek("T14c contoh galian bidang di prompt ikut kena jeda satu balasan", g is None or not g.startswith("bidang"), str(g))


# ===========================================================================
bagian("R. BEDAH REGRESI v3.10 vs export live — yang tidak disebut patch tidak tersentuh")
# ===========================================================================
import difflib as _dl
with open(os.path.join(DIR, "VIRA Personal — Main.json"), encoding="utf-8") as _f:
    _lama = json.load(_f)
_NL = {n["name"]: n for n in _lama["nodes"]}
DIUBAH = {"AI Agent", "Process All", "Rakit Konteks"}

cek("R1  jumlah & nama node sama dengan export live", set(_NL) == set(NODES) and len(wf["nodes"]) == 89)
cek("R2  koneksi identik", json.dumps(_lama["connections"], sort_keys=True) == json.dumps(CONNS, sort_keys=True))
_beda = sorted(n for n in NODES if n not in DIUBAH
               and json.dumps(NODES[n], sort_keys=True, ensure_ascii=False)
               != json.dumps(_NL[n], sort_keys=True, ensure_ascii=False))
cek("R3  86 node lain identik byte per byte dengan export live", not _beda, ", ".join(_beda))
_meta = [n for n in DIUBAH if {k: v for k, v in NODES[n].items() if k != "parameters"}
         != {k: v for k, v in _NL[n].items() if k != "parameters"}]
cek("R4  node yang diubah: tipe/versi/posisi/kredensial tetap", not _meta, str(_meta))
cek("R4b settings workflow tetap", _lama.get("settings") == wf.get("settings"))


def _baris_diganti(a, b):
    la, lb = a.split("\n"), b.split("\n")
    return [i for t, i1, i2, j1, j2 in _dl.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes()
            if t != "equal" for i in range(i1, i2)]


def _wilayah(teks_, awal, akhir):
    la = teks_.split("\n")
    i = next(k for k, x in enumerate(la) if awal in x)
    j = next(k for k in range(i, len(la)) if akhir in la[k])
    return set(range(i, j + 1))


def _di_luar(teks_lama, teks_baru, wilayah):
    boleh = set()
    for aw, ak in wilayah:
        boleh |= _wilayah(teks_lama, aw, ak)
    la = teks_lama.split("\n")
    return [la[i].strip()[:60] for i in _baris_diganti(teks_lama, teks_baru) if i not in boleh]


_pa0, _pa1 = _NL["Process All"]["parameters"]["jsCode"], NODES["Process All"]["parameters"]["jsCode"]
_x = _di_luar(_pa0, _pa1, [("const namaMilikLain =", "hasil.add('nama_lengkap');"),
                           ("let namaDihapus = false;", "return [{")])
cek("R5  Process All: baris lama yang diganti hanya di detektor nama & jaring nama", not _x, str(_x))
_rk0, _rk1 = _NL["Rakit Konteks"]["parameters"]["jsCode"], NODES["Rakit Konteks"]["parameters"]["jsCode"]
_x = _di_luar(_rk0, _rk1, [("const namaMilikLain =", "hasil.add('nama_lengkap');"),
                           ("// - nama_bisnis: tidak di sini", "// - nama_bisnis: tidak di sini"),
                           ("const GALIAN = [", "if (galian) barisProspek.push")])
cek("R6  Rakit Konteks: baris lama yang diganti hanya di detektor, komentar, dan GALIAN", not _x, str(_x))
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
cek("R7  detektor galian tetap IDENTIK di Process All dan Rakit Konteks", _det(_pa1) == _det(_rk1))
cek("R7b detektor memang berubah dari export live (pertanyaan gabungan)", _det(_pa1) != _det(_pa0))

_sp0 = _NL["AI Agent"]["parameters"]["options"]["systemMessage"]
_x = _di_luar(_sp0, _sp, [
    ("Pesan perkenalan itu juga menanyakan namanya", "Pesan perkenalan itu juga menanyakan namanya"),
    ("   Nama, bidang usaha, masalah utama", "   Nama, bidang usaha, masalah utama"),
    ("10. Sebelum mengirim", "ikut dihitung dan tidak pernah dipotong"),
    ("Lalu langsung jawab pertanyaannya, dan tutup", "Kalau dia sudah menyebut namanya di pesan pertama"),
    ("Aku ingin tahu sedang bicara dengan siapa", "jawaban satu kata jadi tidak bisa kubedakan"),
    ("Maksimal 3 kalimat per balasan", "tanya di giliran berikutnya. Menjawab pendek"),
    ("kususun sendiri: satu kalimat, ringan", "bidang apa kak?\"; untuk masalah"),
    ("decknya jadi generik. Momen paling wajar", "namanya dipakai. Contoh"),
    ("menanyakan namanya → `nama`; nama usahanya", "menanyakan namanya → `nama`; nama usahanya")])
cek("R8  system prompt: baris lama yang diganti hanya di 9 wilayah sasaran patch", not _x, str(_x))
_pl = json.loads(json.dumps(_NL["AI Agent"]["parameters"]))
_pb = json.loads(json.dumps(NODES["AI Agent"]["parameters"]))
_pl["options"].pop("systemMessage"); _pb["options"].pop("systemMessage")
cek("R9  AI Agent: selain systemMessage identik", _pl == _pb)
cek("R10 DeepSeek Personal Chat: temperature tetap 0.7 (panjang diatur lewat prompt, bukan parameter)",
    NODES["DeepSeek Personal Chat"]["parameters"]["options"].get("temperature") == 0.7)


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
    "Import 2026-09-18-VIRA-Personal-Main-v3.10.json, matikan v3.9 dulu, lalu aktifkan v3.10. Tidak ada kolom baru.",
    "Diamkan ~15 menit tanpa chat apa pun. Kirimi mengirim device.last_active berkala; sesudah v3.2 tidak boleh ada execution merah dari denyut itu lagi.",
    "Chat dari nomor KETIGA (bukan 2 nomor uji lama) - harus dibalas. Ini bukti P0-1 beres.",
    "Ulang persis alur 2026-09-05: tanya AI CS -> sebut bidang -> tanya harga -> "
    "'udah itu aja' -> terima tawaran deck dengan 'boleh' -> jawab nama bisnis. "
    "VIRA harus mengenali nama bisnis itu, dan Steven harus menerima notif brief.",
    "Kirim 'boleh minta brosurnya' saat LINKS tidak punya brosur - balasan tidak boleh menjanjikan file.",
    "Kirim 'chat paling ramai hari senin' - VIRA harus tetap membalas (bot tidak mati).",
    "Kirim 'mau ngobrol langsung sama Steven' - notif handover masuk DAN bot berhenti.",
    "Cek kolom STATS.last_bot_reply terisi teks balasan terakhir.",
    "HARGA (insiden 2026-09-07) — ulang persis: 'mau tanya soal AI customer service' -> "
    "sebut bidang usaha -> lalu kirim 'biasanya pas lg promo buka kelas, ads itu pasti pd "
    "tanya hal yg sama, harga kuota apa aja yg didapet, sama jadwalnya kapan'. "
    "VIRA TIDAK BOLEH menyebut Rp3.000.000 / Rp5.000.000 di balasan itu.",
    "HARGA (kontrol) — di percakapan yang sama, lanjut 'kalau paket basic berapa ya?'. "
    "Di sini VIRA HARUS menyebut kisaran dan mengarahkan ke Steven.",
    "PAIN POINT — setelah prospek menyebut masalah utamanya, VIRA harus menanyakan "
    "AKIBATNYA satu kali (mis. 'ada yang sampai kelewat nggak kak?'), tidak dua kali.",
    "PAIN POINT — cek notif brief: baris 'Keluhan lain' harus berisi lebih dari satu "
    "keluhan dipisah ';', dan tidak boleh mengulang kalimat 'Masalah utama'.",
    "DECK — generate deck dari brief itu, pastikan slide Pain Points memuat 3+ poin.",
    "PERKENALAN — nomor uji (baris STATS-nya dihapus dulu) kirim 'Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku.': perkenalan + SATU kalimat 'nama kakak siapa, dan nama usahanya apa?'. TIDAK ada pertanyaan bidang usaha atau alasan tertarik.",
    "NAMA + USAHA — ulang uji 17/09: jawab 'Nadia kak, bisnis aku katering, chat suka numpuk pas malem'. Balasan menyapa 'kak' TANPA nama dan menanyakan ulang nama usaha (sekali). STATS: nama_lengkap = Nadia, industri = katering, nama_bisnis kosong.",
    "NAMA USAHA — jawab 'Dapur Nadia': STATS.nama_bisnis = Dapur Nadia. Balasan berikutnya tidak menanyakan nama usaha lagi, lanjut masalah (bidang sudah ada) atau bidang usaha + cerita singkat.",
    "NAMA + USAHA SEKALIGUS — nomor uji baru, jawab perkenalan dengan 'Rina, Kopi Senja': balasan TIDAK menanyakan nama usaha lagi. STATS: nama_lengkap = Rina, nama_bisnis = Kopi Senja.",
    "RINGKAS — sepanjang uji, balasan galian umumnya 2 kalimat (maks 3) dan TIDAK membuka dengan merangkum jawaban ('Jadi...', 'Berarti...', 'Paham, berarti...', 'Nah itu...'). Bandingkan dengan transkrip 17/09.",
    "NAMA — ulang insiden 2026-09-15: jawab 'dengan aldi' + 'mo ty ini bs apa aj' + 'apa sm ky chatbot biasa?'. "
    "VIRA menyapa 'kak' (TANPA nama), MENJAWAB pertanyaannya, dan tidak menanyakan bidang usaha di balasan itu. "
    "STATS.nama_lengkap = Aldi.",
    "GALIAN — lanjut chat biasa: berikutnya VIRA menanyakan bidang usaha, lalu masalah, lalu jumlah chat per hari "
    "(satu per balasan). Setiap jawaban muncul di STATS: industri, masalah_utama, volume_chat, bahasa.",
    "GALIAN — abaikan satu pertanyaan: balasan berikutnya TIDAK mengulangnya.",
    "DECK — sampai tawaran deck: REQUESTS.nama_bisnis SUDAH terisi dari awal, notif brief ke Steven berbaris "
    "'WA: 62xxx · Nadia', dan deck yang digenerate tidak lagi bernama 'tanpa-nama.pdf'.",
    "BUDGET/PAKET — sepanjang uji, VIRA tidak pernah menanyakan anggaran atau Basic/Premium.",
], 1):
    print("  %d. %s" % (i, langkah))

sys.exit(1 if gagal else 0)
