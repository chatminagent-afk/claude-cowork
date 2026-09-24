# -*- coding: utf-8 -*-
"""
_uat_2026-09-23b.py — UAT perilaku untuk 2026-09-23-VIRA-Personal-Main-v3.13.json.

Diturunkan dari _uat_2026-09-23.py (jangan diedit manual — ubah generatornya,
_buat_uat_2026-09-23b.py, lalu jalankan ulang). Seksi A-Q, S, T, U dan V ikut jalan sebagai
regresi (hanya V5 'menyebut harga' yang disesuaikan); seksi W baru untuk uji live Steven
2026-09-23 13:22-13:45 (Rehan); seksi R membedah v3.13 terhadap v3.12.

Berbeda dari _qa_*.py yang hanya memeriksa struktur, berkas ini MENJALANKAN kode
JavaScript asli dari node-node workflow di dalam mesin V8 (py-mini-racer), dengan
$(), $input, $getWorkflowStaticData, $vars, dan console yang dipalsukan persis
seperti yang disediakan n8n. Jadi yang diuji adalah kode yang benar-benar akan
jalan di produksi, bukan tiruannya.

Yang TETAP tidak bisa diuji di sini: apakah Google Sheets menulis baris yang benar,
apakah Kirimi mengirim, dan apakah model DeepSeek benar-benar mengeluarkan tag.
Tiga itu butuh nomor aktif — lihat daftar UAT manual di akhir keluaran.

Jalankan: python _uat_2026-09-23b.py
Keluar dengan kode 1 kalau ada satu saja skenario GAGAL.
"""
import io
import json
import os
import sys

from py_mini_racer import MiniRacer

DIR = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json")

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
print("UAT PERILAKU — VIRA Personal v3.13 (2026-09-23)")
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
cek("M2  tujuh ekspresi {{ }} tetap utuh (enam lama + deck_context)",
    len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 7,
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
cek("Q2  tujuh ekspresi {{ }} tetap utuh (enam lama + deck_context)",
    len(_re.findall(r"\{\{[^}]+\}\}", _sp)) == 7)
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
cek("T5  target (v3.12): SATU kalimat tanya + pengakuan <= 4 kata",
    "SATU kalimat tanya, boleh didahului pengakuan pendek maksimal empat kata" in _gaya.replace("\n", " "))
cek("T5b batas keras (v3.12): 2 kalimat, sekitar 25 kata", "Batas keras 2 kalimat, sekitar 25 kata." in _gaya)
cek("T5c larangan mengulang ucapan prospek", "JANGAN MENGULANG UCAPANNYA" in _gaya)
cek("T5d ALUR 10 menyuruh membuang kalimat yang mengulang sebelum mengirim",
    "buang kalimat yang cuma mengulang atau merangkum ucapannya" in _sp)
_pas = [k.replace("\n", " ") for k in _re.findall(r'(?:Pas: |— )"([^"]+)"', _gaya)]
cek("T5e dua contoh balasan 'pas' ditemukan", len(_pas) == 2, str(_pas))
for _k in _pas:
    _kal = len(_re.findall(r"[.?!](?:\s|$)", _k))
    _kata = len(_k.split())
    cek("T5f contoh pas '%s...' <= 2 kalimat & <= 20 kata (%d kal, %d kata)" % (_k[:30], _kal, _kata),
        _kal <= 2 and _kata <= 20)
_buruk = _re.search(r'Terlalu panjang[^"]*"([^"]+)"', _gaya)
cek("T5g contoh buruk (v3.12) = gema + promosi: '50 chat sehari itu' ... 'VIRA bisa pegang'",
    _buruk is not None and _buruk.group(1).startswith("50 chat sehari itu")
    and "VIRA bisa pegang" in _buruk.group(1).replace("\n", " "))
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
        ("Rina owner Kopi Senja", "Rina", "Kopi Senja", "kopi"),
        ("Nama saya Rina, usaha saya Kopi Senja", "Rina", "Kopi Senja", "kopi"),
        ("Rina\nKopi Senja", "Rina", "Kopi Senja", "kopi"),
        ("Rina - Kopi Senja kak", "Rina", "Kopi Senja", "kopi"),
        ("usahaku Kopi Senja, aku Rina", "Rina", "Kopi Senja", "kopi"),
        ("Kopi Senja, aku Rina", "Rina", "Kopi Senja", "kopi"),
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
cek("T10b (v3.12) balasan uji 17/09 kini juga dipangkas RINGKAS: kalimat gema dibuang",
    d and d["cleanOutput"] == "Salam kenal kak. Kalau lagi numpuk gitu, biasanya yang paling bikin repot bagian mananya kak?"
    and d["ringkas"] == "gema", str(d and (d["cleanOutput"], d["ringkas"])))
_d10 = satu(proses("Salam kenal Nadia. Chat katering memang paling ramai pas malam hari.", pesan_user=JAWAB_1709,
                   prev_row={"last_bot_reply": INTRO_1709}))
cek("T10b' kata 'katering' tidak tersentuh penghapus nama (balasan tanpa pertanyaan = tanpa RINGKAS)",
    _d10 and _d10["cleanOutput"] == "Salam kenal kak. Chat katering memang paling ramai pas malam hari.",
    str(_d10 and _d10["cleanOutput"]))
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
cek("T14 giliran 3, nama usaha sudah ada -> bidang usaha (v3.12: tanpa 'cerita singkat')",
    g == "bidang usahanya", str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "2", "nama_lengkap": "Nadia", "nama_bisnis": "Dapur Nadia",
                "industri": "katering", "last_bot_reply": "Oh iya, nama usahanya apa kak?"}, "Dapur Nadia")
cek("T14b giliran 3, bidang sudah ada -> masalah", g is not None and g.startswith("masalah terbesarnya"), str(g))
g, _ = galian2({"greeting_sent": "Y", "Counter": "3", "nama_bisnis": "Dapur Nadia", "industri": "katering",
                "last_bot_reply": "Usahanya bergerak di bidang apa kak, boleh cerita sedikit?"}, "katering rumahan kak")
cek("T14c contoh galian bidang di prompt ikut kena jeda satu balasan", g is None or not g.startswith("bidang"), str(g))


# ===========================================================================
bagian("U. DECK TERKIRIM — deck_context, persetujuan diskusi, bagian # DECK (2026-09-22)")
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
bagian("V. RINGKAS & PENANGKAP — ulang uji Steven 2026-09-23 (abdul, parfum)")
# ===========================================================================
INTRO_2309 = ("Halo kak, salam kenal! Aku Steven versi AI, dibangun sama Steven pakai sistem yang sama yang "
              "dia bikin untuk kliennya, namanya VIRA. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. "
              "Senang kakak tertarik setelah lihat website-nya. Kakak mau cerita dulu soal bisnisnya, atau "
              "langsung tanya hal yang paling bikin penasaran? Btw boleh tau nama kakak siapa, dan nama "
              "usahanya apa?")
ABDUL = "abdul\naku owner humanizer\njualan parfum\nkdg ribet balesin org ty 1 1"
# Transkrip asli 23/09: (pesan prospek, balasan VIRA sebelumnya, balasan VIRA giliran ini)
G2 = ("Salam kenal kak. Jadi Humanizer ini jualan parfum ya, wajar sih ribet, chat parfum biasanya banyak "
      "yang nanya aroma, ketahanan, sama rekomendasi. Nah itu justru yang bisa dipegang VIRA. Balesin yang "
      "nanya-nanya itu otomatis 24 jam, jadi kakak tinggal fokus ke yang udah siap order. Btw nama usahanya "
      "Humanizer itu sendiri ya kak, atau itu nama brand parfumnya?")
G3 = ("Oke, Humanizer itu nama brand sekaligus usahanya. Nah soal chat yang bikin ribet itu, yang paling "
      "sering bikin kakak kewalahan bagian mananya, yang nanya aroma, atau yang nanya harga dan stok?")
G4 = ("Semua jenis chat itu memang makan waktu kalau dibales satu-satu. VIRA bisa pegang itu semua sekaligus, "
      "jelasin aroma, jawab harga, cek stok, sampai kasih rekomendasi. Kira-kira sehari ada berapa chat masuk "
      "kak, biar aku kebayang bebannya?")
G5 = ("100 chat sehari itu lumayan berat buat dibales sendiri, apalagi sambil ngurus packing dan stok. Dari "
      "chat pertama sampai orangnya akhirnya beli, biasanya lewat langkah apa aja kak?")
G6 = ("Alurnya jelas, tanya dulu, minta pricelist, terus pesen. Nah bagian tanya-tanya dan kirim pricelist "
      "itu yang paling bisa diotomasi. VIRA bisa jawab pertanyaan umum dan kirim pricelist otomatis, jadi "
      "kakak tinggal terima order yang udah jadi. Biasanya mereka paling sering nanya apa aja kak, selain harga?")
_FAKTA4 = {"nama_lengkap": "Abdul", "nama_bisnis": "humanizer", "industri": "jualan parfum",
           "masalah_utama": "kdg ribet balesin org ty 1 1"}


def proses2(ai_output, pesan_user, prev_row=None, baru=False, galian_kolom=None):
    """proses() dengan isNewUser dan galian_kolom (keluaran Rakit Konteks) yang bisa diatur."""
    rk = {"katalog": {"links": LINKS}}
    if galian_kolom is not None:
        rk["galian_kolom"] = galian_kolom
    prev = {"resolved_key": "6289900112233", "nama_lengkap": "", "nama_bisnis": "", "industri": "",
            "masalah_utama": "", "volume_chat": "", "budget_range": "", "minat_paket": "", "bahasa": "",
            "deck_requested": "", "brief_terisi": "", "last_bot_reply": "", "last_bot_reply_ts": 0}
    prev.update(prev_row or {})
    return satu(jalan("Process All", nodes={
        "Chat Counter": [item(original_message=pesan_user, user_wa="6289900112233", user_name="Prospek")],
        "Preprocess - Context Detection": [item(actualUserMessage=pesan_user, isNewUser=baru, wantsMedia=False,
                                                askingPrice=False, wantsHuman=False)],
        "Parse Config": [item(config=cfg())],
        "Resolve User Row": [item(**prev)],
        "Rakit Konteks": [item(**rk)],
    }, inp=[item(output=ai_output)]))


# ---- V1 penangkap jawaban perkenalan -------------------------------------
cek("V1  perkenalan asli 23/09 terbaca detektor sebagai nama + nama usaha",
    detek(INTRO_2309) == ["nama_bisnis", "nama_lengkap"], str(detek(INTRO_2309)))
d = tangkap(ABDUL, INTRO_2309, ai="Salam kenal kak.")
cek("V1b pesan 4 baris uji 23/09 -> nama, nama usaha, industri, masalah tertangkap semua",
    d and {k: d[k + "_merged"] for k in _FAKTA4} == _FAKTA4, str(d and {k: d[k + "_merged"] for k in _FAKTA4}))
cek("V1c slotTertangkap mencatat keempatnya",
    d and sorted(d["slotTertangkap"].split(",")) == sorted(_FAKTA4), str(d and d["slotTertangkap"]))
for pesan, harap in [
        (ABDUL, ("Abdul", "humanizer", "jualan parfum", "kdg ribet balesin org ty 1 1")),
        ("aku owner humanizer", ("", "humanizer", "", "")),
        ("Rina\nkewalahan balesin customer", ("Rina", "", "", "kewalahan balesin customer")),
        ("kewalahan balesin customer\nRina", ("Rina", "", "", "kewalahan balesin customer")),
        ("jualan parfum\nabdul", ("Abdul", "", "jualan parfum", "")),
        ("Rina, parfum", ("Rina", "", "parfum", "")),
        ("saya owner Toko Wangi, jualan parfum", ("", "Wangi", "jualan parfum", "")),
        ("Nadia kak, bisnis aku katering, chat suka numpuk pas malem", ("Nadia", "", "katering", "chat suka numpuk pas malem")),
        ("Rina, Dapur Mama", ("Rina", "Dapur Mama", "", "")),
        ("aku Rina, jualan skincare", ("Rina", "", "jualan skincare", "")),
        ("Budi, Klinik Sehat Gigi", ("Budi", "Klinik Sehat Gigi", "klinik", "")),
        ("Sari dari Bimbel Cerdas Mandiri", ("Sari", "Bimbel Cerdas Mandiri", "bimbel", "")),
        ("Rina, Dapur Mama, jualan kue", ("Rina", "Dapur Mama", "jualan kue", "")),
        ("dengan aldi\nmo ty ini bs apa aj\napa sm ky chatbot biasa?", ("Aldi", "", "", ""))]:
    d = tangkap(pesan, PERKENALAN_BARU, ai="Salam kenal kak.")
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"], d["masalah_utama_merged"])
    cek("V2  '%s' -> %s" % (pesan.replace("\n", " / ")[:45], harap), got == harap, str(got))
d = tangkap(ABDUL, INTRO_2309, ai="Salam kenal kak.", prev={"masalah_utama": "chat numpuk"})
cek("V2b masalah lama tidak pernah ditimpa keluhan baru", d and d["masalah_utama_merged"] == "chat numpuk")
d = tangkap(ABDUL, INTRO_2309, ai='Salam kenal kak.\n[FACTS nama="Abdul Karim" industri="parfum"]')
cek("V2c [FACTS] dari model tetap menang", d and d["nama_lengkap_merged"] == "Abdul Karim" and d["industri_merged"] == "parfum",
    str(d and (d["nama_lengkap_merged"], d["industri_merged"])))
d = tangkap("kewalahan balesin customer", "Usahanya di bidang apa kak?")
cek("V2d di luar perkenalan, jalur satu slot tidak berubah (industri = jawaban mentah)",
    d and d["industri_merged"] == "kewalahan balesin customer" and d["masalah_utama_merged"] == "",
    str(d and (d["industri_merged"], d["masalah_utama_merged"])))

# ---- V3 Rakit Konteks: galian memakai fakta pesan giliran ini ---------------
g, d = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": INTRO_2309}, ABDUL)
cek("V3  giliran 2 uji 23/09: TIDAK menanyakan ulang nama usaha (v3.11: 'nama usahanya — tanya ulang')",
    g is None, str(g))
for k, v in _FAKTA4.items():
    cek("V3b DATA PROSPEK memuat %s dari pesan ini" % k,
        d and ("%s: %s (baru dia sebut di pesan ini)" % (k, v)) in d["prospect_context"], d and d["prospect_context"])
cek("V3c baris panggilan: kak muncul begitu nama tertangkap di pesan ini",
    d and "panggilan: kak — nama_lengkap hanya catatan untuk Steven" in d["prospect_context"])
cek("V3d format_balasan: prospek tidak bertanya -> SATU kalimat tanya",
    d and "format_balasan: dia tidak sedang bertanya — cukup SATU kalimat tanya" in d["prospect_context"])
cek("V3e IS_NEW_USER tetap baris terakhir", d and d["prospect_context"].rstrip().endswith("IS_NEW_USER: false"))
_S4 = dict({"greeting_sent": "Y", "Counter": "2"}, **_FAKTA4)
g, d = galian2(dict(_S4, last_bot_reply="Salam kenal kak. Sehari kira-kira ada berapa chat masuk?"), "100 an chat")
cek("V3f jawaban jumlah chat ikut dihitung -> tidak ada galian tersisa", g is None, str(g))
cek("V3g volume_chat dari pesan ini tampil", d and "volume_chat: 100 an chat (baru dia sebut di pesan ini)" in d["prospect_context"])
g, d = galian2(dict({"greeting_sent": "Y", "Counter": "2", "nama_bisnis": "Dapur Mama"},
                    last_bot_reply="Usahanya bergerak di bidang apa kak?"), "katering rumahan kak")
cek("V3h jawaban bidang usaha ditangkap -> langsung ke masalah (dulu: jeda satu balasan)",
    g is not None and g.startswith("masalah terbesarnya"), str(g))
g, d = galian2({"greeting_sent": "Y", "Counter": "2"}, "harganya berapa kak?")
cek("V3i prospek bertanya -> format_balasan BERTANYA, tanpa galian",
    g is None and "format_balasan: dia sedang BERTANYA — jawab langsung" in d["prospect_context"], str(g))
g, d = galian2({"greeting_sent": ""}, "Halo VIRA, aku lihat website-nya")
cek("V3j pesan perkenalan: tanpa format_balasan & tanpa fakta pesan ini (aturan perkenalan sendiri)",
    "format_balasan" not in d["prospect_context"] and "baru dia sebut" not in d["prospect_context"])
d = rakit({"greeting_sent": "Y", "Counter": "3"})
cek("V3k tanpa pesan prospek (node Preprocess tidak ada) -> node tetap jalan", d is not None)
for lalu, pesan in [("Oh iya, nama usahanya apa kak?", "Dapur Mama"),
                    ("Usahanya di bidang apa kak?", "katering rumahan kak"),
                    ("Soal chat, yang paling bikin repot sekarang apa kak?", "chat numpuk pas malem ga kebales"),
                    ("Kira-kira sehari ada berapa chat masuk kak?", "50an"),
                    (INTRO_2309, ABDUL), (PERKENALAN_BARU, "Rina, Dapur Mama"),
                    (PERKENALAN_BARU, "harganya berapa kak?"),
                    ("Yang paling bikin repot pas lagi rame, biasanya bagian mananya?", "100 an chat"),
                    ("Dari chat pertama sampai beli, biasanya lewat langkah apa aja kak?",
                     "tanya dulu, trus sehari bisa 40 chat kalo lagi rame")]:
    _, drk = galian2({"greeting_sent": "Y", "Counter": "2", "last_bot_reply": lalu}, pesan)
    rk_f = dict(_re.findall(r"^(\w+): (.*) \(baru dia sebut di pesan ini\)$", drk["prospect_context"], _re.M))
    dpa = tangkap(pesan, lalu)
    pa_f = {k: dpa[k + "_merged"] for k in ("nama_lengkap", "nama_bisnis", "industri", "masalah_utama", "volume_chat")
            if dpa[k + "_merged"]}
    cek("V3l Rakit Konteks & Process All sepakat soal fakta '%s'" % pesan.replace("\n", " / ")[:40],
        rk_f == pa_f, "RK=%s PA=%s" % (rk_f, pa_f))

# ---- V4 jaring RINGKAS: transkrip asli ------------------------------------
for judul, pesan, lalu, ai, harap, alasan in [
        ("G2", ABDUL, INTRO_2309, G2,
         "Salam kenal kak. Btw nama usahanya Humanizer itu sendiri ya kak, atau itu nama brand parfumnya?", "gema+panjang"),
        ("G3", "keduanya", G2, G3,
         "Soal chat yang bikin ribet itu, yang paling sering bikin kakak kewalahan bagian mananya, yang nanya aroma, "
         "atau yang nanya harga dan stok?", "panjang"),
        ("G4", "semua", G3, G4, "Kira-kira sehari ada berapa chat masuk kak?", "panjang+ekor"),
        ("G5", "100 an chat", G4, G5,
         "Dari chat pertama sampai orangnya akhirnya beli, biasanya lewat langkah apa aja kak?", "gema"),
        ("G6", "tanya2 dlu, trs minta pricelist, dan pesen", G5, G6,
         "Biasanya mereka paling sering nanya apa aja kak, selain harga?", "gema+panjang")]:
    d = proses2(ai, pesan, {"last_bot_reply": lalu})
    cek("V4  %s uji 23/09 -> '%s...' (%s)" % (judul, harap[:40], alasan),
        d and d["cleanOutput"] == harap and d["ringkas"] == alasan, str(d and (d["cleanOutput"], d["ringkas"])))
    cek("V4b %s ringkas_asli = balasan model utuh, needs_ringkas_log = 'true'" % judul,
        d and d["ringkas_asli"] == ai and d["needs_ringkas_log"] == "true")
    cek("V4c %s last_bot_reply = teks yang terkirim" % judul, d and d["last_bot_reply"] == d["cleanOutput"])
d = proses2(G2.replace("Salam kenal kak.", "Salam kenal Abdul."), ABDUL, {"last_bot_reply": INTRO_2309})
cek("V4d penghapus nama tetap jalan sesudah RINGKAS",
    d and d["cleanOutput"].startswith("Salam kenal kak. Btw nama usahanya") and "abdul" not in d["cleanOutput"].lower(),
    str(d and d["cleanOutput"]))
d = proses2("Siap kak. Terus biasanya yang paling sering ditanyain apa, biar Steven bisa siapin contohnya?", "oke", {})
cek("V4e ekor alasan dibuang walau balasan sudah pendek",
    d and d["cleanOutput"] == "Siap kak. Terus biasanya yang paling sering ditanyain apa?" and d["ringkas"] == "ekor",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Nah itu biasanya bikin repot banget. Apalagi kalau lagi rame. Oh iya, sehari ada berapa chat masuk kak?",
            "biasanya tanya harga", {})
cek("V4f penghubung di depan pertanyaan dibuang kalau tanpa pengakuan ('Oh iya, ...')",
    d and d["cleanOutput"] == "Sehari ada berapa chat masuk kak?" and d["ringkas"] == "panjang",
    str(d and (d["cleanOutput"], d["ringkas"])))

# ---- V5 jaring RINGKAS TIDAK boleh menyentuh --------------------------------
PANJANG_TANYA = ("VIRA bisa balas chat 24 jam, kirim katalog, dan catat pesanan. Bedanya dengan chatbot biasa, "
                 "dia paham maksud orang walau bahasanya campur. Semua jawabannya diambil dari data bisnis kakak "
                 "sendiri. Kakak jualan apa kak?")
for judul, ai, pesan, prev, baru in [
        ("prospek BERTANYA (jawaban tidak boleh terpotong)", PANJANG_TANYA, "ini bisa buat apa aja ya?", {}, False),
        ("prospek bertanya tanpa tanda tanya", PANJANG_TANYA, "bedanya sama chatbot biasa gmn", {}, False),
        # v3.13: "oke noted" dibalas daftar harga kini dipangkas jaring HARGA (seksi W2c). Yang dijaga cek ini
        # tetap sama: jawaban harga TIDAK dipotong kalau prospek memang meminta harganya.
        ("menyebut harga (prospek minta pricelist)", "Basic mulai Rp3.000.000 per bulan, sudah termasuk setup. "
         "Angka finalnya Steven yang tentukan setelah lihat kebutuhan kakak. Chat masuk sehari kira-kira ada berapa kak?",
         "info pricelist dong kak", {}, False),
        ("tawaran deck", "Itu yang paling sering bikin calon pembeli pindah ke toko lain. VIRA balas dalam hitungan "
         "detik, termasuk tengah malam. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?",
         "iya kadang ada yg kelewat", {}, False),
        ("persetujuan deck (brief)", DECK_BLOK + "Sudah aku teruskan ke Steven, dia sendiri yang akan menyusun "
         "decknya. Sambil nunggu, ada lagi yang mau ditanyain kak?", "boleh",
         {"last_bot_reply": "mau aku mintakan Steven buatkan deck khusus buat bisnis kakak?"}, False),
        ("handover", "[TALK_TO_ADMIN]\nSiap kak, aku sambungkan ke Steven ya. Dia biasanya balas di hari yang "
         "sama. Ada yang mau aku titipkan ke dia kak?", "mau ngobrol langsung sama steven", {}, False),
        ("[UNKNOWN]", "[UNKNOWN]\nYang itu aku belum tahu pasti kak, nanti aku tanyakan ke Steven dulu. Sambil "
         "nunggu, biasanya chat paling ramai jam berapa kak?", "oke", {}, False),
        ("kirim media", "[SEND_MEDIA:brosur vira]\nIni brosurnya kak, isinya lengkap soal fitur. Kalau sudah "
         "dibaca, bagian mana yang paling relevan buat bisnis kakak?", "oke", {}, False),
        ("pesan perkenalan", "Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia "
         "bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak "
         "siapa, dan nama usahanya apa?", "halo", {}, True),
        ("tanpa pertanyaan", "Siap kak, makasih ya. Nanti Steven kabari lagi soal decknya. Semoga lancar terus "
         "jualannya.", "oke makasih", {}, False),
        ("sudah pas (1 pengakuan + 1 tanya)", "Noted kak. Dari chat pertama sampai jadi pesan, biasanya lewat "
         "langkah apa aja?", "50an", {}, False),
        ("2 kalimat <= 30 kata, tanpa gema", "Lumayan ramai ya kak. Dari chat pertama sampai jadi pesan, "
         "biasanya lewat langkah apa aja?", "50an", {}, False)]:
    d = proses2(ai, pesan, prev, baru)
    bersih = _re.sub(r"\[[^\]]*\]\n?", "", ai.replace(DECK_BLOK, "")).strip()
    cek("V5  RINGKAS tidak menyentuh: %s" % judul,
        d is not None and d["ringkas"] == "" and d["needs_ringkas_log"] == "false"
        and d["ringkas_asli"] == "" and (d["cleanOutput"].startswith(bersih[:40]) and bersih[-25:] in d["cleanOutput"]),
        str(d and (d["ringkas"], d["cleanOutput"][:90])))

# ---- V6 node baru: IF Ringkas Dipangkas & Log EVENTS Ringkas -------------------
IFR, LOGR = NODES["IF Ringkas Dipangkas"], NODES["Log EVENTS Ringkas"]
_kond = IFR["parameters"]["conditions"]["conditions"]
cek("V6  IF Ringkas: satu kondisi, needs_ringkas_log equals 'true' (pola IF Unknown)",
    len(_kond) == 1 and _kond[0]["leftValue"] == "={{ $json.needs_ringkas_log }}"
    and _kond[0]["rightValue"] == "true" and _kond[0]["operator"]["operation"] == "equals"
    and IFR["type"] == NODES["IF Unknown"]["type"] and IFR["typeVersion"] == NODES["IF Unknown"]["typeVersion"])
_dp = proses2(G4, "semua", {"last_bot_reply": G3})
_dn = proses2("Noted kak. Dari chat pertama sampai jadi pesan, biasanya lewat langkah apa aja?", "50an", {})
cek("V6b ekspresi kondisi -> 'true' saat dipangkas, 'false' saat tidak",
    eval_ekspresi(_kond[0]["leftValue"], _dp)["out"] == "true" and eval_ekspresi(_kond[0]["leftValue"], _dn)["out"] == "false")
cek("V6c Log EVENTS Ringkas: append ke EVENTS di sheet & kredensial yang sama dengan Log EVENTS Delegated",
    LOGR["parameters"]["operation"] == "append"
    and LOGR["parameters"]["documentId"] == NODES["Log EVENTS Delegated"]["parameters"]["documentId"]
    and LOGR["parameters"]["sheetName"] == NODES["Log EVENTS Delegated"]["parameters"]["sheetName"]
    and LOGR.get("credentials") == NODES["Log EVENTS Delegated"].get("credentials")
    and LOGR["type"] == NODES["Log EVENTS Delegated"]["type"])
cek("V6d Log EVENTS Ringkas: gagal tulis tidak menghentikan workflow (onError lanjut, retry 2x)",
    LOGR.get("onError") == "continueRegularOutput" and LOGR.get("retryOnFail") is True and LOGR.get("maxTries") == 2)
_kol = LOGR["parameters"]["columns"]
cek("V6e kolom yang dipetakan = header EVENTS (ts, no_wa, nama, event, detail)",
    sorted(_kol["value"]) == ["detail", "event", "nama", "no_wa", "ts"]
    and [s["id"] for s in _kol["schema"]] == ["ts", "no_wa", "nama", "event", "detail"]
    and _kol["mappingMode"] == "defineBelow")
_ctx = {"Process All": [{"json": _dp}], "Resolve User Row": [{"json": {"resolved_key": "6285171701168"}}],
        "Chat Counter": [{"json": {"user_name": "Steven Leroy"}}]}
_ev = {k: (v if not str(v).startswith("=") else ekspr_node(v, _ctx)) for k, v in _kol["value"].items()}
_evo = {k: (v["out"] if isinstance(v, dict) else v) for k, v in _ev.items()}
cek("V6f ekspresi kolom terevaluasi tanpa error",
    all(not (isinstance(v, dict) and v.get("err")) for v in _ev.values()), str(_ev)[:300])
cek("V6g isi baris EVENTS: no_wa, event RINGKAS, ts epoch",
    _evo["no_wa"] == "6285171701168" and _evo["event"] == "RINGKAS" and isinstance(_evo["ts"], int)
    and abs(_evo["ts"] - NOW_S) < 3600, str({k: _evo[k] for k in ("no_wa", "event", "ts")}))
cek("V6h detail memuat alasan, teks terkirim, dan teks asli model",
    _evo["detail"].startswith("dipangkas: panjang+ekor | terkirim: Kira-kira sehari ada berapa chat masuk kak?")
    and "| asli: Semua jenis chat itu memang makan waktu" in _evo["detail"], _evo["detail"][:200])
cek("V6i nama jatuh ke nama akun WA kalau nama belum tercatat", _evo["nama"] == "Steven Leroy", str(_evo["nama"]))
_anak = [c["node"] for c in CONNS["Process All"]["main"][0]]
cek("V6j Process All -> IF Ringkas Dipangkas terpasang", "IF Ringkas Dipangkas" in _anak, str(_anak))
cek("V6k IF Ringkas (true) -> Log EVENTS Ringkas; cabang false kosong; Log tidak menyambung ke mana pun",
    CONNS["IF Ringkas Dipangkas"]["main"][0] == [{"node": "Log EVENTS Ringkas", "type": "main", "index": 0}]
    and len(CONNS["IF Ringkas Dipangkas"]["main"]) == 1 and "Log EVENTS Ringkas" not in CONNS)
cek("V6l cabang log paling bawah -> dijalankan TERAKHIR (sesudah Wait1 -> kirim WA), executionOrder v1",
    wf["settings"].get("executionOrder") == "v1"
    and all(NODES["IF Ringkas Dipangkas"]["position"][1] > NODES[n]["position"][1] for n in _anak if n != "IF Ringkas Dipangkas"),
    str([(n, NODES[n]["position"][1]) for n in _anak]))
cek("V6m id node baru unik", len({n["id"] for n in wf["nodes"]}) == len(wf["nodes"]))

# ---- V9 temuan eval model asli 2026-09-23 -------------------------------------
_TANYA_MASALAH = "Yang paling bikin repot pas lagi rame, biasanya bagian mananya?"
for pesan, harap in [("100 an chat", "100 an chat"),
                     ("sehari bisa 40 chat kalo lagi musim daftar", "sehari bisa 40 chat kalo lagi musim daftar"),
                     ("oke, chat masuk sehari 50an", "chat masuk sehari 50an"),
                     ("100an chat pas weekend", "100an chat pas weekend"),
                     ("sekitar 20-30 chat sehari", "sekitar 20-30 chat sehari"),
                     ("chatnya\n30an per hari kak", "30an per hari"),
                     ("tanya2 dlu, trs minta pricelist, dan pesen", ""),
                     ("paket 2 sebulan berapa?", ""), ("3 juta sebulan ya", ""), ("ada 2 admin yang bales", ""),
                     ("buka jam 8 sampai 21 tiap hari", ""), ("kdg ribet balesin org ty 1 1", "")]:
    d = tangkap(pesan, _TANYA_MASALAH, prev={"masalah_utama": "chat numpuk"})
    cek("V9  jumlah chat tanpa ditanya: '%s' -> %r" % (pesan.replace("\n", " / "), harap),
        d and d["volume_chat_merged"] == harap, str(d and d["volume_chat_merged"]))
d = tangkap("100 an chat", _TANYA_MASALAH, prev={"masalah_utama": "chat numpuk", "volume_chat": "20"})
cek("V9b jumlah chat lama tidak pernah ditimpa", d and d["volume_chat_merged"] == "20")
d = tangkap("tanya2 dlu, trs minta pricelist, dan pesen", "Kira-kira sehari ada berapa chat masuk kak?")
cek("V9c jawab jumlah chat: 'tanya2' bukan angka (dulu tersimpan sebagai volume_chat)",
    d and d["volume_chat_merged"] == "", str(d and d["volume_chat_merged"]))
d = tangkap("50an", "Kira-kira sehari ada berapa chat masuk kak?")
cek("V9d jawab jumlah chat '50an' tetap tertangkap", d and d["volume_chat_merged"] == "50an")
g, d = galian2(dict({"greeting_sent": "Y", "Counter": "2"}, **_FAKTA4, last_bot_reply=_TANYA_MASALAH), "100 an chat")
cek("V9e eval S1: '100 an chat' tanpa ditanya -> galian jumlah chat TIDAK muncul",
    g is None and "volume_chat: 100 an chat (baru dia sebut di pesan ini)" in d["prospect_context"], str(g))
g, d = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": INTRO_2309}, "Sari dari Bimbel Cerdas Mandiri")
cek("V9f eval S4: 'Bimbel Cerdas Mandiri' -> bidang tidak ditanya, langsung masalah",
    g is not None and g.startswith("masalah terbesarnya") and "industri: bimbel (baru dia sebut" in d["prospect_context"], str(g))
cek("V9g galian_kolom keluar dari Rakit Konteks", d and d.get("galian_kolom") == "masalah_utama", str(d and d.get("galian_kolom")))
g, d = galian2({"greeting_sent": ""}, "halo")
cek("V9h galian_kolom kosong di pesan perkenalan", d and d.get("galian_kolom") == "", str(d and d.get("galian_kolom")))

_DUA = "Oh iya, nama usahanya apa kak? Usahanya bergerak di bidang apa?"
d = proses2(_DUA, "oke", {}, galian_kolom="nama_bisnis")
cek("V9i dua pertanyaan -> sisakan yang menanyakan galian (nama usaha)",
    d and d["cleanOutput"] == "Oh iya, nama usahanya apa kak?" and d["ringkas"] == "satu-tanya",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2(_DUA, "oke", {})
cek("V9j dua pertanyaan tanpa galian -> sisakan yang terakhir",
    d and d["cleanOutput"] == "Usahanya bergerak di bidang apa?" and d["ringkas"] == "satu-tanya",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Siap kak. Chat malam biasanya soal apa? Terus sehari ada berapa chat masuk?", "oke", {},
            galian_kolom="volume_chat")
cek("V9k pengakuan tetap, pertanyaan galian yang disisakan",
    d and d["cleanOutput"] == "Siap kak. Terus sehari ada berapa chat masuk?" and d["ringkas"] == "satu-tanya",
    str(d and (d["cleanOutput"], d["ringkas"])))
_BRIEF_DIAM = DECK_BLOK + "Noted kak, 50 chat sehari itu lumayan ramai. Yang paling bikin repot soal chat sekarang apa kak?"
d = proses2(_BRIEF_DIAM, "oke, chat masuk sehari 50an", {})
cek("V9l eval S3: pembaruan brief diam-diam ([DECK_REQUEST] tanpa menyebut deck) tetap diringkas",
    d and d["cleanOutput"] == "Yang paling bikin repot soal chat sekarang apa kak?" and d["ringkas"] == "gema",
    str(d and (d["cleanOutput"], d["ringkas"])))
cek("V9m ... dan briefnya tetap terbaca", d and d["isDeckRequest"] is True and d["deckRequest"].get("industri") == "konsultan sipil")

_INTRO_ASLI = ("Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk "
               "kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang.")
for judul, ai, harap in [
        ("eval S2: 'mau tanya bagian mana?'",
         _INTRO_ASLI + " Soal chatbot, mau tanya yang bagian mana kak? Btw boleh tau nama kakak siapa, dan nama usahanya apa?",
         _INTRO_ASLI + " Btw boleh tau nama kakak siapa, dan nama usahanya apa?"),
        ("eval S1: 'bidang apa?'",
         _INTRO_ASLI + " Boleh cerita, bisnis kakak bergerak di bidang apa? Dan btw, boleh tau nama kakak siapa dan nama usahanya apa?",
         _INTRO_ASLI + " Dan btw, boleh tau nama kakak siapa dan nama usahanya apa?"),
        ("perkenalan asli 23/09", INTRO_2309,
         "Halo kak, salam kenal! Aku Steven versi AI, dibangun sama Steven pakai sistem yang sama yang dia bikin "
         "untuk kliennya, namanya VIRA. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Senang kakak "
         "tertarik setelah lihat website-nya. Btw boleh tau nama kakak siapa, dan nama usahanya apa?")]:
    d = proses2(ai, "Halo kak, mau tanya soal chatbot", {}, baru=True)
    cek("V9n perkenalan (%s) -> hanya pertanyaan nama + nama usaha" % judul,
        d and d["cleanOutput"] == harap and d["ringkas"] == "perkenalan", str(d and (d["cleanOutput"], d["ringkas"])))
_TANPA_NAMA = (_INTRO_ASLI + " VIRA ini intinya AI customer service WhatsApp: balas chat otomatis 24 jam. "
               "Kakak sendiri usahanya di bidang apa?")
d = proses2(_TANPA_NAMA, "Halo, ini bisa buat apa aja ya?", {}, baru=True)
cek("V9o perkenalan TANPA pertanyaan nama (eval S3) -> pertanyaan lain diganti pertanyaan baku nama + nama usaha",
    d and d["cleanOutput"] == _INTRO_ASLI + " VIRA ini intinya AI customer service WhatsApp: balas chat otomatis 24 jam. "
    "Btw boleh tau nama kakak siapa, dan nama usahanya apa?" and d["ringkas"] == "perkenalan",
    str(d and (d["cleanOutput"][-80:], d["ringkas"])))
cek("V9o' pertanyaan baku itu terbaca detektor sebagai nama + nama usaha (jadi jawabannya tertangkap)",
    detek("Btw boleh tau nama kakak siapa, dan nama usahanya apa?") == ["nama_bisnis", "nama_lengkap"]
    and detek("Btw boleh tau nama kakak siapa?") == ["nama_lengkap"] and detek("Btw nama usahanya apa kak?") == ["nama_bisnis"])
d = proses2(_INTRO_ASLI + " Btw boleh tau nama kakak siapa, dan nama usahanya apa?", "halo", {}, baru=True)
cek("V9p perkenalan yang sudah pas tidak disentuh", d and d["ringkas"] == "" and d["needs_ringkas_log"] == "false")

# ---- V10 temuan eval putaran 2 --------------------------------------------------
g, d = galian2({"greeting_sent": "Y", "Counter": "1", "last_bot_reply": PERKENALAN_BARU}, JAWAB_1709)
cek("V10  eval S2: ada galian -> format_balasan menunjuk galian itu sebagai SATU-SATUNYA pertanyaan",
    g is not None and "dan pertanyaan itu adalah galian_berikutnya di atas (bukan pertanyaan lain)" in d["prospect_context"],
    str(g)[:60])
g, d = galian2(dict({"greeting_sent": "Y", "Counter": "2"}, **_FAKTA4, last_bot_reply=_TANYA_MASALAH), "100 an chat")
cek("V10b tanpa galian -> format_balasan tanpa rujukan galian",
    g is None and "format_balasan: dia tidak sedang bertanya" in d["prospect_context"]
    and "adalah galian_berikutnya" not in d["prospect_context"])
_LALU_DECK = ("Siap kak, brief-nya sudah aku teruskan ke Steven. Dia sendiri yang bakal nyusun deck-nya dan langsung "
              "hubungin kakak. Sambil nunggu, dari chat pertama sampai jadi reservasi biasanya lewat langkah apa aja kak?")
d = proses2("Sama-sama kak. Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja?", "makasih kak",
            {"last_bot_reply": _LALU_DECK})
cek("V10c eval S5: pertanyaan yang sama dengan balasan sebelumnya tidak diulang",
    d and d["cleanOutput"] == "Sama-sama kak." and d["ringkas"] == "tanya-ulang", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja?", "oke", {"last_bot_reply": _LALU_DECK})
cek("V10d kalau yang tersisa cuma pertanyaan kembar itu -> dibiarkan (tidak mengirim teks kosong)",
    d and d["cleanOutput"] == "Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja?" and d["ringkas"] == "",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Sama-sama kak. Yang paling sering ditanyain biasanya apa aja?", "makasih kak", {"last_bot_reply": _LALU_DECK})
cek("V10e pertanyaan BERBEDA tidak tersentuh", d and d["ringkas"] == "" and d["cleanOutput"].endswith("apa aja?"))
_INTRO_S5 = ("Halo kak, salam kenal. Aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin "
             "buat kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh aku tau dulu, chat di Kopi "
             "Senja biasanya kayak gimana kak? Yang paling bikin repot sekarang apa?")
d = proses2(_INTRO_S5, "Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat", {}, baru=True)
cek("V10f eval S5: perkenalan tanpa pertanyaan nama tapi 2 pertanyaan -> sisakan yang terakhir",
    d and d["cleanOutput"].endswith("contoh hasilnya sekarang. Yang paling bikin repot sekarang apa?")
    and "kayak gimana" not in d["cleanOutput"] and d["ringkas"] == "perkenalan", str(d and (d["cleanOutput"][-90:], d["ringkas"])))
d = proses2("100 chat itu lumayan ya kak. Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja kak?",
            "100an chat pas weekend", {})
cek("V10g eval S5: '100an' dikenali sama dengan '100' -> kalimat gema dibuang",
    d and d["cleanOutput"] == "Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja kak?"
    and d["ringkas"] == "gema", str(d and (d["cleanOutput"], d["ringkas"])))

# ---- V11 temuan eval putaran 3 --------------------------------------------------
# (a) pertanyaan kembar: galian tanya ulang nama usaha dikecualikan
_KEMBAR = "Salam kenal kak. Nama usahanya apa ya kak?"
d = proses2(_KEMBAR, "coffee shop kak, chat reservasi numpuk pas weekend", {"last_bot_reply": PERKENALAN_BARU},
            galian_kolom="nama_bisnis")
cek("V11  eval S5/S2: galian tanya ulang nama usaha TIDAK dibuang walau mirip pertanyaan perkenalan",
    d and d["cleanOutput"] == _KEMBAR and d["ringkas"] == "", str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2(_KEMBAR, "coffee shop kak, chat reservasi numpuk pas weekend", {"last_bot_reply": PERKENALAN_BARU})
cek("V11b tanpa galian -> pertanyaan kembar itu dibuang", d and d["cleanOutput"] == "Salam kenal kak." and d["ringkas"] == "tanya-ulang",
    str(d and (d["cleanOutput"], d["ringkas"])))
_LALU_HARGA = ("Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan. Boleh aku tau, di klinik kakak "
               "sehari kira-kira berapa chat masuk?")
d = proses2("Bisa kak, VIRA bisa pegang chat dari Instagram juga. Kira-kira sehari ada berapa chat masuk ke klinik kakak?",
            "bisa connect ke IG juga ga?", {"last_bot_reply": _LALU_HARGA})
cek("V11c eval S3: prospek BERTANYA -> jawaban utuh, hanya pertanyaan kembarnya yang dibuang",
    d and d["cleanOutput"] == "Bisa kak, VIRA bisa pegang chat dari Instagram juga." and d["ringkas"] == "tanya-ulang",
    str(d and (d["cleanOutput"], d["ringkas"])))
# (b) nama usaha mustahil
for pesan, lalu in [("makasih kak", TAWARAN_LIVE), ("boleh dong dibuatin deck", TAWARAN_LIVE),
                    ("sekitar 20-30 chat sehari", "Oh iya, nama usahanya apa kak?"),
                    ("oke siap", "Oh iya, nama usahanya apa kak?")]:
    d = tangkap(pesan, lalu)
    cek("V11d eval S5/S2: '%s' BUKAN nama usaha" % pesan, d and d["nama_bisnis_merged"] == "", str(d and d["nama_bisnis_merged"]))
for pesan, harap in [("Kopi Senja", "Kopi Senja"), ("namanya Toko Wangi kak", "Wangi"), ("boleh kak, namanya Teamsultan", "Teamsultan")]:
    d = tangkap(pesan, "Oh iya, nama usahanya apa kak?")
    cek("V11e nama usaha asli tetap tertangkap: '%s'" % pesan, d and d["nama_bisnis_merged"] == harap, str(d and d["nama_bisnis_merged"]))
# (c) perkenalan diri di pesan pertama
_S5_1 = "Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat"
d = proses2("Halo kak, salam kenal. Aku Steven versi AI. Yang paling bikin repot soal chat sekarang apa kak?", _S5_1, {}, baru=True)
cek("V11f eval S5: pesan pertama 'aku Rina dari Kopi Senja' -> nama, nama usaha, industri tercatat",
    d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"]) == ("Rina", "Kopi Senja", "kopi"),
    str(d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"])))
cek("V11g ... dan karena keduanya sudah diketahui, balasan tanpa pertanyaan nama tidak diubah",
    d and d["ringkas"] == "" and d["cleanOutput"].endswith("Yang paling bikin repot soal chat sekarang apa kak?"))
for pesan, harap in [("Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku.", ("", "", "")),
                     ("Halo, saya owner toko kue, mau tanya", ("", "", "kue")),
                     ("halo kak saya mau tanya harga", ("", "", "")),
                     ("aku seorang ibu rumah tangga, jualan kue", ("", "", "jualan kue")),
                     ("Halo, ini bisa buat apa aja ya?", ("", "", ""))]:
    d = proses2("Halo kak, aku Steven versi AI. Btw boleh tau nama kakak siapa, dan nama usahanya apa?", pesan, {}, baru=True)
    got = d and (d["nama_lengkap_merged"], d["nama_bisnis_merged"], d["industri_merged"])
    cek("V11h pesan pertama '%s' -> %s" % (pesan[:40], harap), got == harap, str(got))
g, d = galian2({"greeting_sent": ""}, _S5_1)
cek("V11i Rakit Konteks: perkenalan diri lengkap -> perkenalan tidak menanyakan nama/usaha lagi",
    g is None and "nama_bisnis: Kopi Senja (baru dia sebut di pesan ini)" in d["prospect_context"], str(g))
g, d = galian2({"greeting_sent": ""}, "halo kak, aku Rina")
cek("V11j perkenalan diri tanpa nama usaha -> tanya nama usaha saja", g is not None and g.startswith("nama usahanya — tanyakan di"), str(g))
d = proses2("Halo kak, aku Steven versi AI. Senang kenalan. Kakak jualan apa?", "halo kak, aku Rina", {}, baru=True)
cek("V11k nama sudah disebut, nama usaha belum, model lupa -> pertanyaan diganti 'nama usahanya apa'",
    d and d["cleanOutput"] == "Halo kak, aku Steven versi AI. Senang kenalan. Btw nama usahanya apa kak?", str(d and d["cleanOutput"]))
# (d) model hanya menulis tag
_TAG_SAJA = '[FACTS nama="Sari" nama_bisnis="Bimbel Cerdas Mandiri" industri="bimbel"]'
d = proses2(_TAG_SAJA, "Sari dari Bimbel Cerdas Mandiri", {"last_bot_reply": PERKENALAN_BARU}, galian_kolom="masalah_utama")
cek("V11l eval S4: balasan cuma tag -> pertanyaan galian, bukan 'Maaf, ada kendala'",
    d and d["cleanOutput"] == "Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak?"
    and d["ringkas"] == "cadangan-galian" and d["needs_ringkas_log"] == "true", str(d and (d["cleanOutput"], d["ringkas"])))
cek("V11m ... fakta dari tag tetap tersimpan", d and d["nama_bisnis_merged"] == "Bimbel Cerdas Mandiri" and d["nama_lengkap_merged"] == "Sari")
d = proses2(_TAG_SAJA, "Sari dari Bimbel Cerdas Mandiri", {"last_bot_reply": PERKENALAN_BARU})
cek("V11n tanpa galian -> kalimat cadangan lama tetap", d and d["cleanOutput"] == "Maaf, ada kendala sebentar. Boleh diketik ulang yaa.")
d = proses2("[UNKNOWN]", "sistemnya pakai server mana?", {}, galian_kolom="masalah_utama")
cek("V11o [UNKNOWN] saja -> kalimat 'belum tahu' tetap (bukan pertanyaan galian)",
    d and d["cleanOutput"].startswith("Maaf yaa, untuk yang ini aku belum tahu"))
for kol, harap in [("nama_bisnis", ["nama_bisnis"]), ("industri", ["industri"]), ("masalah_utama", ["masalah_utama"]),
                   ("volume_chat", ["volume_chat"])]:
    d = proses2("[FACTS]", "oke", {}, galian_kolom=kol)
    cek("V11p kalimat cadangan untuk galian %s terbaca detektor sebagai %s" % (kol, harap),
        d and detek(d["cleanOutput"]) == harap, str(d and d["cleanOutput"]))

# ---- V12 temuan eval putaran 4 --------------------------------------------------
_BASIS = {"greeting_sent": "Y", "Counter": "4", "nama_lengkap": "Rina", "nama_bisnis": "Kopi Senja",
          "industri": "kopi", "masalah_utama": "chat numpuk"}
g, d = galian2(dict(_BASIS, last_bot_reply="Kalau lagi numpuk gitu, ada yang kelewat nggak kak?"), "boleh dong dibuatin deck")
cek("V12  eval S5: 'boleh dong dibuatin deck' -> format_balasan: kabari brief diteruskan, bukan tawaran",
    "format_balasan: dia MINTA / SETUJU dibuatkan deck" in d["prospect_context"] and g is None
    and d.get("galian_kolom") == "", d["prospect_context"][-200:])
g, d = galian2(dict(_BASIS, deck_requested="Y", last_bot_reply="Siap kak."), "boleh dong dibuatin deck")
cek("V12b sudah pernah minta deck -> tidak memaksa pengumuman kedua", "dia MINTA / SETUJU" not in d["prospect_context"])
for pesan, lalu in [("boleh dong dibuatin deck", "Kalau lagi numpuk gitu, ada yang kelewat nggak kak?"),
                    ("boleh", TAWARAN_LIVE), ("mau kak", TAWARAN_LIVE), ("boleh telepon aja", TAWARAN_LIVE),
                    ("oke", "Sehari berapa chat masuk kak?"), ("tolong bikinin proposal", "Siap kak."),
                    ("mau tanya harga dulu", TAWARAN_LIVE), ("boleh, tapi aku mau ngobrol langsung sama steven", TAWARAN_LIVE)]:
    _, drk = galian2(dict(_BASIS, last_bot_reply=lalu), pesan)
    dpa = proses2("Siap kak.", pesan, {"last_bot_reply": lalu})
    cek("V12c Rakit Konteks & Process All sepakat soal minta deck: '%s'" % pesan,
        ("dia MINTA / SETUJU dibuatkan deck" in drk["prospect_context"]) == bool(dpa["deckDiminta"]),
        "RK=%s PA=%s" % ("dia MINTA" in drk["prospect_context"], dpa["deckDiminta"]))
_rkc = NODES["Rakit Konteks"]["parameters"]["jsCode"]
_pac = NODES["Process All"]["parameters"]["jsCode"]
for _nama, _pola in [("NIAT_DECK", r"const NIAT_DECK   = (/.+?/);\n"), ("NIAT_BICARA", r"const NIAT_BICARA = (/.+?/);\n"),
                     ("TAWARAN_DECK", r"const TAWARAN_DECK  = (/.+?/)\.test"),
                     ("SETUJU_PENDEK", r"const SETUJU_PENDEK = PESAN_USER\.length <= 40\n  && (/.+?/)\.test")]:
    _lit = _re.search(_pola, _pac).group(1)
    cek("V12d regex %s di Rakit Konteks = salinan persis dari Process All" % _nama, _lit in _rkc)
d = proses2('Oh iya, nama usahanya Dapur Nadia ya kak? Usahanya bergerak di bidang apa kak?\n[FACTS nama_bisnis="Dapur Nadia"]',
            "Dapur Nadia",
            {"nama_lengkap": "Nadia", "industri": "katering"}, galian_kolom="nama_bisnis")
cek("V12e eval S2: pertanyaan bidang padahal bidang sudah diketahui -> dibuang",
    d and d["cleanOutput"] == "Oh iya, nama usahanya Dapur Nadia ya kak?" and d["ringkas"] == "sudah-tahu",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Kira-kira sehari ada berapa chat masuk kak?", "sekitar 20-30 chat sehari", {}, galian_kolom="masalah_utama")
cek("V12f eval S2: jumlah chat ditanya sesudah dia menyebutnya -> diganti pertanyaan galian",
    d and d["cleanOutput"] == "Soal chat, yang paling bikin repot sekarang apa kak?" and d["ringkas"] == "sudah-tahu",
    str(d and (d["cleanOutput"], d["ringkas"])))
d = proses2("Kira-kira sehari ada berapa chat masuk kak?", "sekitar 20-30 chat sehari", {})
cek("V12g ... tanpa galian -> dibiarkan (tidak mengirim teks kosong)",
    d and d["cleanOutput"] == "Kira-kira sehari ada berapa chat masuk kak?" and d["ringkas"] == "")
d = proses2("Siap kak. Pas lagi ramai gitu, yang paling bikin repot bagian mananya kak?", "oke", {"masalah_utama": "chat numpuk"})
cek("V12h pertanyaan lanjutan soal masalah (akibat) TIDAK dianggap 'sudah tahu'", d and d["ringkas"] == "")
d = proses2("Noted kak. Chat yang numpuk pas malem itu biasanya isinya apa aja kak?", "Dapur Nadia",
            {"last_bot_reply": "Chat yang numpuk pas malem itu biasanya isinya apa aja kak?"}, galian_kolom="nama_bisnis")
cek("V12i eval S2: pertanyaan kembar dibuang -> pertanyaan galian dikirim, bukan 'Noted kak.' saja",
    d and d["cleanOutput"] == "Noted kak. Oh iya, nama usahanya apa kak?" and d["ringkas"] == "tanya-ulang+galian",
    str(d and (d["cleanOutput"], d["ringkas"])))

# ---- V7 prompt & teks galian --------------------------------------------------
_sp1 = _sp.replace("\n", " ")
cek("V7  ALUR 10 membuang promosi yang tidak ditanya",
    "kalimat promosi VIRA yang tidak dia tanyakan (lihat GAYA)" in _sp1)
cek("V7b GAYA melarang promosi di setiap balasan + ekor alasan",
    "JANGAN BERJUALAN DI SETIAP BALASAN" in _sp and "ekor alasan di pertanyaan" in _sp)
cek("V7c promosi VIRA hanya kalau ditanya / satu kalimat di tawaran deck",
    "Kemampuan VIRA baru kujelaskan kalau dia menanyakannya, atau dalam SATU kalimat di balasan yang menawarkan deck" in _sp1)
cek("V7d aturan lama yang mendorong rangkuman/promosi sudah hilang",
    "satu yang menanggapi, satu yang" not in _sp1 and "harus MENAMBAH sesuatu" not in _sp1
    and "Lumayan buat dibalas sendiri" not in _sp1)
cek("V7e GAYA merujuk format_balasan, dan Rakit Konteks benar-benar menulisnya",
    "`format_balasan`" in _sp and "format_balasan: " in NODES["Rakit Konteks"]["parameters"]["jsCode"])
_perk = _sp.split("# PERKENALAN")[1].split("\n# NAMA LAWAN BICARA")[0]
_tpl = _re.search(r'\n"(Halo kak, aku Steven versi AI[^"]+)"', _perk)
cek("V7f contoh perkenalan <= 2 kalimat & <= 30 kata",
    _tpl is not None and len(_re.findall(r"[.?!](?:\s|$)", _tpl.group(1))) <= 2 and len(_tpl.group(1).split()) <= 30,
    str(_tpl and len(_tpl.group(1).split())))
cek("V7g perkenalan melarang basa-basi & menawarkan pilihan (pola asli 23/09)",
    '"senang kakak tertarik"' in _perk and '"mau cerita dulu atau langsung tanya?"' in _perk)
cek("V7h tidak ada 'cerita sedikit/cerita singkat' di prompt maupun Rakit Konteks",
    "cerita sedikit" not in _sp and not any(
        "cerita singkat" in l for l in NODES["Rakit Konteks"]["parameters"]["jsCode"].splitlines()
        if not l.strip().startswith("//")))
cek("V7i contoh prompt tidak memuat nama/usaha uji (abdul, humanizer)",
    "abdul" not in _sp.lower() and "humanizer" not in _sp.lower())

# ---- V8 kode bersama identik -------------------------------------------------
_PA = NODES["Process All"]["parameters"]["jsCode"]
_RK = NODES["Rakit Konteks"]["parameters"]["jsCode"]
_blok = lambda s: s[s.index("// ── PENANGKAP JAWABAN — MULAI ──"):s.index("// ── PENANGKAP JAWABAN — SELESAI ──")]
cek("V8  blok PENANGKAP JAWABAN identik di Process All dan Rakit Konteks", _blok(_PA) == _blok(_RK))
_bersih = lambda s: _re.search(r"const BERSIH = [^;]+;", s, _re.S).group(0)
cek("V8b fungsi BERSIH identik di dua node", _bersih(_PA) == _bersih(_RK))
_rx = lambda s, nama: _re.search(r"const " + nama + r" = (/.+?/i)\.test", s).group(1)
cek("V8c definisi 'prospek bertanya' sama di dua node", _rx(_PA, "PROSPEK_BERTANYA") == _rx(_RK, "pesanBertanya"))
cek("V8d Process All: penangkap satu slot tetap jalan SEBELUM penangkap perkenalan",
    _PA.index("if (slotDitanyaLalu.length === 1)") < _PA.index("if (slotDitanyaLalu.includes('nama_lengkap')"))
cek("V8e Process All: RINGKAS jalan sesudah tag dibuang & sebelum media/penghapus nama",
    _PA.index("let cleanOutput = aiOutput") < _PA.index("// ── RINGKAS (2026-09-23) ──")
    < _PA.index("// ── RESOLVE MEDIA URL") < _PA.index("const namaSimpan"))


# ===========================================================================
bagian("W. HARGA & PENANGKAP — ulang uji live Steven 2026-09-23 13:22-13:45 (Rehan, sewa raket padel)")
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
bagian("R. BEDAH REGRESI v3.13 vs v3.12 (= live, dicek MCP 2026-09-23 12:19 WIB)")
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
], 1):
    print("  %d. %s" % (i, langkah))

sys.exit(1 if gagal else 0)
