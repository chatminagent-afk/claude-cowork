# -*- coding: utf-8 -*-
"""
Transformasi VIRA-PCR Main V2.1 -> VIRA Steven Main.
Deterministik & idempoten: aman dijalankan ulang berkali-kali.
Jalankan:  python _transform.py
"""
import json, re, os, io, sys

BASE = r"D:\Documents\Claude Cowork\Persada Cisoka Residence\workflow\production\2026-08-08-VIRA-PCR-Main-V2.1 (not used).json"
PROMPT_MD = r"D:\Documents\Claude Cowork\VIRA Steven\workflow\2026-08-15-system-prompt-VIRA-Steven.md"
OUT = r"D:\Documents\Claude Cowork\VIRA Steven\workflow\2026-08-15-VIRA-Steven-Main.json"

SHEET_ID = "1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk"
BOT_WA = "6285155202354"
ADMIN_WA = "6285171701168"
MODEL_REPLY = "claude-sonnet-5"
MODEL_UTIL = "claude-haiku-4-5"

# 5 node alur survei / request-call yang benar-benar dihapus
DROP = ["IF Schedule Survey", "Write SURVEY", "Update STATS Survey",
        "IF Request Call", "Log Call Request"]

# rename: lama -> baru
RENAME = {
    "Whitelist Gate":   "Blocklist Gate",
    "Read PRODUK Data": "Read PROGRAM Data",
    "Notify Media Team": "Notify Admin Media",
    "Notify Field Team": "Notify Admin Handover",
}

d = json.load(io.open(BASE, encoding="utf-8"))
nodes = d["nodes"]
conns = d["connections"]
log = []


# ───────────────── 1. buang node, sambung ulang alurnya ─────────────────
def out_targets(name, branch=0):
    """target dari output ke-`branch` sebuah node"""
    b = conns.get(name, {}).get("main", [])
    if len(b) > branch and b[branch]:
        return [c["node"] for c in b[branch]]
    return []


# simpan siapa penerus dari tiap node yang dibuang, untuk menjembatani
bridge = {n: out_targets(n) for n in DROP}
nodes[:] = [n for n in nodes if n["name"] not in DROP]
for n in DROP:
    conns.pop(n, None)
log.append(f"hapus {len(DROP)} node: {', '.join(DROP)}")

# lepaskan referensi ke node yang dibuang; khusus survei, jembatani ke penerusnya
for src, ch in conns.items():
    for key, branches in ch.items():
        for bi, br in enumerate(branches or []):
            if not br:
                continue
            baru = []
            for c in br:
                if c["node"] not in DROP:
                    baru.append(c)
                    continue
                # IF Schedule Survey -> Update STATS Survey -> Collect Handover Context
                # jembatani supaya Collect Handover Context tidak yatim
                hop, seen = c["node"], set()
                while hop in DROP and hop not in seen:
                    seen.add(hop)
                    nxt = bridge.get(hop, [])
                    hop = nxt[0] if nxt else None
                if hop and hop not in DROP:
                    if not any(x["node"] == hop for x in baru):
                        baru.append({"node": hop, "type": c["type"], "index": c["index"]})
                        log.append(f"jembatani {src} -> {hop} (menggantikan {c['node']})")
            branches[bi] = baru


# ───────────────── 2. rename node + perbarui semua referensi ─────────────────
for n in nodes:
    if n["name"] in RENAME:
        n["name"] = RENAME[n["name"]]
for lama, baru in RENAME.items():
    if lama in conns:
        conns[baru] = conns.pop(lama)
for src, ch in conns.items():
    for branches in ch.values():
        for br in branches or []:
            for c in br or []:
                if c["node"] in RENAME:
                    c["node"] = RENAME[c["node"]]
log.append("rename: " + ", ".join(f"{k} -> {v}" for k, v in RENAME.items()))


# ───────────────── 3. sisipkan Read ABOUT_STEVEN setelah Read LINKS Data ─────────────────
if not any(n["name"] == "Read ABOUT_STEVEN" for n in nodes):
    src = next(n for n in nodes if n["name"] == "Read LINKS Data")
    baru = json.loads(json.dumps(src))          # salin struktur node Sheets yang sudah benar
    baru["name"] = "Read ABOUT_STEVEN"
    baru["id"] = "about-steven-read-0001"
    baru["position"] = [src["position"][0], src["position"][1] + 180]
    nodes.append(baru)
    # sisipkan di rantai: LINKS -> ABOUT_STEVEN -> (tujuan lama LINKS)
    lama = conns.get("Read LINKS Data", {}).get("main", [[]])[0]
    conns["Read ABOUT_STEVEN"] = {"main": [list(lama)]}
    conns["Read LINKS Data"] = {"main": [[{"node": "Read ABOUT_STEVEN", "type": "main", "index": 0}]]}
    log.append("tambah node Read ABOUT_STEVEN, disisipkan setelah Read LINKS Data")


# ───────────────── 4. nama tab Google Sheets ─────────────────
TAB = {"PRODUK": "PROGRAM", "SURVEY": "REQUESTS"}
for n in nodes:
    p = n.get("parameters", {})
    if n["name"] == "Read PROGRAM Data":
        for k in ("sheetName", "documentId"):
            pass
    for key in ("sheetName",):
        v = p.get(key)
        if isinstance(v, dict):
            for f in ("value", "cachedResultName"):
                if isinstance(v.get(f), str):
                    for a, b in TAB.items():
                        if v[f] == a or v[f].endswith("/" + a):
                            v[f] = b
        elif isinstance(v, str):
            for a, b in TAB.items():
                if v == a:
                    p[key] = b
    if n["name"] == "Read ABOUT_STEVEN":
        sn = p.get("sheetName")
        if isinstance(sn, dict):
            sn["value"] = "ABOUT_STEVEN"
            sn["cachedResultName"] = "ABOUT_STEVEN"
            sn.pop("cachedResultUrl", None)
        else:
            p["sheetName"] = "ABOUT_STEVEN"


# ───────────────── 5. Sheet ID, model, kredensial, metadata ─────────────────
raw = json.dumps(d, ensure_ascii=False)
raw = raw.replace("claude-haiku-4-5-20251001", MODEL_UTIL)
d = json.loads(raw)

# documentId ditulis ulang secara EKSPLISIT, bukan lewat str.replace.
# Versi sebelumnya mengumpulkan nilai documentId ke dalam set lalu me-replace satu per satu;
# karena bentuk URL memuat bentuk ID polos sebagai substring, hasil akhirnya bergantung pada
# urutan iterasi set — yang diacak Python tiap proses. Dua run berturut-turut menghasilkan
# file yang berbeda, jadi skripnya sebenarnya tidak idempoten.
n_doc = 0
for n in d["nodes"]:
    doc = n.get("parameters", {}).get("documentId")
    if not isinstance(doc, dict):
        continue
    doc.clear()
    doc.update({"__rl": True, "value": SHEET_ID, "mode": "id",
                "cachedResultName": "VIRA Steven Database"})
    n_doc += 1
log.append(f"{n_doc} node: documentId -> {SHEET_ID} (mode id)")

for n in d["nodes"]:
    t = n.get("type", "")
    p = n.setdefault("parameters", {})
    # model: AI Agent pakai sonnet-5 (thinking dimatikan), sisanya haiku
    if t.endswith("lmChatAnthropic"):
        is_agent = n["name"] == "Anthropic Chat Model"
        mdl = MODEL_REPLY if is_agent else MODEL_UTIL
        m = p.get("model")
        if isinstance(m, dict):
            m["value"] = mdl
            m["cachedResultName"] = mdl
        else:
            p["model"] = mdl
        if is_agent:
            p.setdefault("options", {})["thinking"] = False
    # kredensial jadi placeholder
    for cred, val in (n.get("credentials") or {}).items():
        if "anthropic" in cred.lower():
            val["id"], val["name"] = "", "Anthropic Personal Steven"
        elif "google" in cred.lower():
            val["id"], val["name"] = "", "Google Service Account VIRA Steven"

d["name"] = "VIRA Steven — Main"
d["active"] = False
d["id"] = ""
d["versionId"] = ""
d.pop("meta", None)
d.pop("tags", None)
d.setdefault("settings", {})["errorWorkflow"] = "<<ISI_ID_ERROR_WORKFLOW>>"
for n in d["nodes"]:
    if n.get("type", "").endswith(".webhook"):
        n["parameters"]["path"] = "wa-inbound-steven"
        n.pop("webhookId", None)
log.append("nama/aktif/webhook/meta diset; kredensial jadi placeholder")


# ───────────────── 6. suntik system prompt ─────────────────
md = io.open(PROMPT_MD, encoding="utf-8").read()
blok = re.search(r"```\n(# STEVEN VERSI AI.*?)\n```", md, re.S)
if not blok:
    print("!! blok system prompt tidak ditemukan di file .md"); sys.exit(1)
sp = blok.group(1)
for n in d["nodes"]:
    if n.get("type", "").endswith(".agent"):
        opt = n["parameters"].setdefault("options", {})
        opt["systemMessage"] = sp
        log.append(f"system prompt disuntik ke '{n['name']}' ({len(sp)} char)")


# ───────────────── 7. Blocklist Gate: ganti isi kodenya ─────────────────
BLOCKLIST_JS = r"""
// Blocklist Gate — VIRA Steven
// Menggantikan Whitelist Gate milik Persada. Bot ini publik, jadi default-nya
// semua orang boleh masuk; yang disaring hanya nomor di blocklist dan nomor bot sendiri.
const cfg = $('Parse Config').first().json.config || {};
const item = $input.first().json;

const digits = (s) => String(s || '').replace(/\D/g, '');
const from = digits(item.from || item.no_wa || '');
const lid  = digits(item.originLid || item.lid || '');

// 1) jangan pernah membalas diri sendiri (bisa memicu loop tak berujung)
const ignoreSelf = String(cfg.ignore_self_number ?? 'true').toLowerCase() === 'true';
const botNumber = digits(cfg.bot_wa_number || '');
if (ignoreSelf && botNumber && (from === botNumber || lid === botNumber)) {
  return [];
}

// 2) blocklist manual dari CONFIG
let blocked = [];
try {
  const rawList = cfg.blocklist_numbers;
  blocked = Array.isArray(rawList) ? rawList : JSON.parse(rawList || '[]');
} catch (e) {
  blocked = [];   // CONFIG salah format -> jangan sampai memblokir semua orang
}
const blockedDigits = blocked.map(digits).filter(Boolean);
if (blockedDigits.length && (blockedDigits.includes(from) || blockedDigits.includes(lid))) {
  return [];
}

return $input.all();
""".strip()

for n in d["nodes"]:
    if n["name"] == "Blocklist Gate":
        n["parameters"]["jsCode"] = BLOCKLIST_JS
        log.append("kode Blocklist Gate ditulis ulang")


# ───────────────── 8. notifikasi diarahkan ke HP Steven ─────────────────
raw = json.dumps(d, ensure_ascii=False)
n_field = raw.count("field_team_phone") + raw.count("media_team_phone")
raw = raw.replace("config.field_team_phone[0]", "config.admin_phone") \
         .replace("config.media_team_phone[0]", "config.admin_phone") \
         .replace("config.field_team_phone", "config.admin_phone") \
         .replace("config.media_team_phone", "config.admin_phone")
d = json.loads(raw)
log.append(f"{n_field} referensi nomor tim lapangan/media dialihkan ke admin_phone")


# ───────────────── 9. perbaiki pemetaan kolom Update to STATS ─────────────────
# Node ini menulis 9 kolom milik Persada yang tidak ada di sheet VIRA Steven —
# tiga di antaranya bahkan punya trailing space (bug lama yang terdokumentasi).
# Menulis ke kolom yang tidak ada = error saat runtime, jadi wajib dibersihkan.
BUANG_KOLOM = [
    "unit_interest", "unit_interest_ts", "nama_lengkap_ts",
    "pending_survey_tanggal ", "pending_survey_jam ", "pending_survey_unit ",
    "pending_survey_ts", "lokasi_kerja", "lokasi_kerja_ts",
]

PA = "$('Process All').first().json"
RU = "$('Resolve User Row').first().json"


def nilai(f):
    # pakai hasil merge kalau Process All menyediakannya, kalau tidak pertahankan nilai lama.
    # JANGAN jatuh ke '' langsung — itu akan menimpa data yang sudah ada dengan kosong.
    return "={{ %s.%s_merged || %s.%s || '' }}" % (PA, f, RU, f)


def stempel(f):
    return "={{ %s.%s_changed ? Math.floor(Date.now()/1000) : (%s.%s_ts || '') }}" % (PA, f, RU, f)


TAMBAH_KOLOM = {
    "nama_bisnis":      nilai("nama_bisnis"),
    "industri":         nilai("industri"),
    "masalah_utama":    nilai("masalah_utama"),
    "masalah_utama_ts": stempel("masalah_utama"),
    "volume_chat":      nilai("volume_chat"),
    "volume_chat_ts":   stempel("volume_chat"),
    "budget_range_ts":  stempel("budget_range"),
    "minat_paket":      nilai("minat_paket"),
    "minat_paket_ts":   stempel("minat_paket"),
    "deck_requested":   "={{ %s.isDeckRequest ? 'Y' : (%s.deck_requested || '') }}" % (PA, RU),
    "bahasa":           nilai("bahasa"),
}

for n in d["nodes"]:
    if n["name"] != "Update to STATS":
        continue
    v = n["parameters"]["columns"]["value"]
    dibuang = [k for k in BUANG_KOLOM if k in v]
    for k in dibuang:
        v.pop(k)
    ditambah = [k for k in TAMBAH_KOLOM if k not in v]
    v.update({k: TAMBAH_KOLOM[k] for k in ditambah})
    # skema kolom juga harus ikut, kalau node menyimpannya
    sk = n["parameters"]["columns"].get("schema")
    if isinstance(sk, list):
        sk[:] = [c for c in sk if c.get("id") not in BUANG_KOLOM]
        adaid = {c.get("id") for c in sk}
        for k in TAMBAH_KOLOM:
            if k not in adaid:
                sk.append({"id": k, "displayName": k, "required": False,
                           "defaultMatch": False, "display": True,
                           "type": "string", "canBeUsedToMatch": True})
    log.append(f"Update to STATS: buang {len(dibuang)} kolom Persada, tambah {len(ditambah)} kolom VIRA Steven")


# ───────────────── 10. sisipkan node Rakit Konteks sebelum AI Agent ─────────────────
# System prompt VIRA Steven merujuk 5 variabel yang tidak diproduksi node manapun
# di workflow Persada. Tanpa node ini, AI Agent jalan tanpa data grounding sama sekali.
RAKIT_JS = r"""
// Rakit Konteks — VIRA Steven
// Membangun 5 blok data yang disisipkan ke system prompt.
// Aturan penting: kolom "Catatan Internal" (PROGRAM & LINKS) dan baris
// "Boleh Dibagikan = Tidak" (ABOUT_STEVEN) TIDAK BOLEH dikirim sebagai fakta.
const item = $input.first().json;
const cfg  = $('Parse Config').first().json.config || {};

const rows = (nodeName) => {
  try { return $(nodeName).all().map(r => r.json).filter(Boolean); }
  catch (e) { return []; }               // node tidak ada / belum jalan -> jangan gagalkan giliran
};
const txt = (v) => String(v ?? '').trim();
const aktif = (v) => /^(aktif|active|on|ya|yes)$/i.test(txt(v));

// ---------- 1. prospect_context ----------
let stats = {};
try { stats = $('Resolve User Row').first().json.userRow || $('Resolve User Row').first().json || {}; }
catch (e) { stats = {}; }

const TTL_HARI = parseInt(cfg.fact_ttl_days || '60', 10);
const sekarang = Math.floor(Date.now() / 1000);
const masihSegar = (ts) => {
  const t = parseInt(ts || '0', 10);
  if (!t) return true;                    // tidak ada stempel waktu -> anggap masih berlaku
  return (sekarang - t) < TTL_HARI * 86400;
};

const FAKTA = ['nama_lengkap', 'nama_bisnis', 'industri', 'masalah_utama',
               'volume_chat', 'budget_range', 'minat_paket'];
const barisProspek = [];
for (const f of FAKTA) {
  const nilai = txt(stats[f]);
  if (!nilai) continue;
  if (!masihSegar(stats[f + '_ts'])) continue;   // fakta basi dibuang, jangan dipakai menyapa
  barisProspek.push(`${f}: ${nilai}`);
}
if (txt(stats['Nama']))  barisProspek.push(`nama_wa: ${txt(stats['Nama'])}`);
if (txt(stats['bahasa'])) barisProspek.push(`bahasa_terakhir: ${txt(stats['bahasa'])}`);
if (txt(stats['deck_requested']) === 'Y') barisProspek.push('sudah_minta_pitch_deck: ya');

const baru = !txt(stats['greeting_sent']);
const prospect_context = (barisProspek.length ? barisProspek.join('\n') : '(belum ada data)')
  + `\nIS_NEW_USER: ${baru}`;

// ---------- 2. about_context ----------
const about = rows('Read ABOUT_STEVEN');
const fakta = [], aturan = [];
for (const r of about) {
  const aspek = txt(r['Aspek']), detail = txt(r['Detail']);
  if (!aspek || !detail) continue;
  (aktif(r['Boleh Dibagikan']) ? fakta : aturan).push(`${aspek}: ${detail}`);
}
let about_context = fakta.join('\n') || '(kosong)';
if (aturan.length) {
  about_context += '\n\nATURAN INTERNAL (jangan dibacakan ke prospek, tapi wajib dipatuhi):\n'
                 + aturan.join('\n');
}

// ---------- 3. program_context ----------
const program = rows('Read PROGRAM Data');
const program_context = program
  .filter(r => aktif(r['Status']))
  .map(r => {
    const bagian = [];
    for (const [k, v] of Object.entries(r)) {
      if (k === 'Catatan Internal' || k === 'row_number' || k === 'Status') continue;  // catatan internal TIDAK dikirim
      if (txt(v)) bagian.push(`${k}: ${txt(v)}`);
    }
    return bagian.join(' | ');
  })
  .filter(Boolean).join('\n') || '(kosong)';

// ---------- 4. links_context ----------
const links = rows('Read LINKS Data');
const links_context = links
  .filter(r => aktif(r['Status']) && txt(r['URL']))
  .map(r => `${txt(r['Nama Link'])} — ${txt(r['Caption']) || 'file pendukung'}`)
  .join('\n') || '(tidak ada media aktif — jangan pakai tag SEND_MEDIA)';

// ---------- 5. faq_context ----------
const faq_context = txt(item.faq_context) || '(tidak ada FAQ relevan untuk pesan ini)';

return [{
  json: {
    ...item,
    prospect_context,
    about_context,
    program_context,
    links_context,
    faq_context,
  }
}];
""".strip()

if not any(n["name"] == "Rakit Konteks" for n in d["nodes"]):
    ag = next(n for n in d["nodes"] if n["name"] == "AI Agent")
    d["nodes"].append({
        "parameters": {"jsCode": RAKIT_JS},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [ag["position"][0] - 200, ag["position"][1] + 200],
        "id": "rakit-konteks-steven-01",
        "name": "Rakit Konteks",
    })
    # sisipkan di antara FAQ Retrieve dan AI Agent
    for src, ch in d["connections"].items():
        for br in ch.get("main", []) or []:
            for c in (br or []):
                if c["node"] == "AI Agent" and src != "Rakit Konteks":
                    c["node"] = "Rakit Konteks"
    d["connections"]["Rakit Konteks"] = {
        "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
    }
    log.append("tambah node Rakit Konteks (5 variabel konteks), disisipkan sebelum AI Agent")


# ───────────────── 11. sheetName: gid Persada -> nama tab ─────────────────
# Sheet ID sudah diganti di langkah 5, tapi sheetName-nya masih mode "list" berisi
# ANGKA GID milik spreadsheet Persada. Gid itu tidak ada di spreadsheet VIRA Steven,
# jadi setiap node baca/tulis yang memakainya akan gagal saat runtime.
n_gid = 0
for n in d["nodes"]:
    if not n.get("type", "").endswith("googleSheets"):
        continue
    sn = n["parameters"].get("sheetName")
    if not isinstance(sn, dict) or sn.get("mode") != "list":
        continue
    nama_tab = sn.get("cachedResultName")
    if not nama_tab:
        print(f"!! {n['name']}: sheetName mode=list tanpa cachedResultName"); sys.exit(1)
    sn["mode"], sn["value"] = "name", nama_tab
    sn.pop("cachedResultUrl", None)
    n_gid += 1
    # documentId juga masih menyimpan nama file lama
    doc = n["parameters"].get("documentId")
    if isinstance(doc, dict) and isinstance(doc.get("cachedResultName"), str):
        doc["cachedResultName"] = "VIRA Steven Database"
log.append(f"{n_gid} node Sheets: sheetName gid Persada -> mode name")


# ───────────────── 12. Resolve User Row: ekspos baris STATS penuh ─────────────────
# Update to STATS & Rakit Konteks memanggil field-field ini; sebelumnya tidak ada satu pun
# yang diproduksi, jadi fallback "pertahankan nilai lama" sebenarnya jatuh ke string kosong
# dan prospect_context kehilangan 5 dari 7 fakta.
RESOLVE_TAMBAHAN = """    userRow: row ? { ...row } : {},
    nama_bisnis: row ? String(row['nama_bisnis'] || '').trim() : '',
    industri: row ? String(row['industri'] || '').trim() : '',
    masalah_utama: row ? String(row['masalah_utama'] || '').trim() : '',
    masalah_utama_ts: Number(row ? (row['masalah_utama_ts'] || 0) : 0) || 0,
    volume_chat: row ? String(row['volume_chat'] || '').trim() : '',
    volume_chat_ts: Number(row ? (row['volume_chat_ts'] || 0) : 0) || 0,
    minat_paket: row ? String(row['minat_paket'] || '').trim() : '',
    minat_paket_ts: Number(row ? (row['minat_paket_ts'] || 0) : 0) || 0,
    deck_requested: row ? String(row['deck_requested'] || '').trim() : '',
    brief_terisi: row ? String(row['brief_terisi'] || '').trim() : '',
    bahasa: row ? String(row['bahasa'] || '').trim() : '',
    counter_db:"""

for n in d["nodes"]:
    if n["name"] != "Resolve User Row":
        continue
    js = n["parameters"]["jsCode"]
    if "userRow:" in js:
        break
    if "    counter_db:" not in js:
        print("!! Resolve User Row: anchor 'counter_db:' tidak ditemukan"); sys.exit(1)
    n["parameters"]["jsCode"] = js.replace("    counter_db:", RESOLVE_TAMBAHAN, 1)
    log.append("Resolve User Row: ekspos userRow + 11 field STATS VIRA Steven")


# ───────────────── 13. Process All: parser tag ditulis ulang ─────────────────
# Versi Persada dibuang seluruhnya. Yang hilang beserta alasannya:
#   - SCHEDULE_SURVEY + validasi slot + FAIL LOUD  -> alurnya sudah tidak ada
#   - REQUEST_CALL                                 -> fallback frasanya menempelkan
#     admin_phone_display ke balasan; itu nomor HP pribadi Steven, tidak boleh bocor
#     ke prospek hanya karena bot menulis "bisa hubungi langsung"
#   - canonType / kolom 'Tipe Unit'                -> kolom itu tidak ada di sheet ini
#   - fallback frasa SEND_MEDIA ("kirim brosur")   -> memicu media manual palsu
PROCESS_ALL_JS = r"""
// ── Process All — VIRA Steven ──
// Ditulis ulang dari versi Persada oleh _transform.py. Jangan diedit langsung di n8n.
const item = $input.first();
let aiOutput = '';
if (item?.json?.content && Array.isArray(item.json.content) && item.json.content.length > 0) {
  aiOutput = item.json.content[0].text || '';
} else {
  aiOutput = item?.json?.output || item?.json?.text || '';
}
console.log('AI Output preview:', aiOutput.substring(0, 300));

const chatCounter = $('Chat Counter').first().json;
const preprocess  = $('Preprocess - Context Detection').first().json;
const cfg  = (() => { try { return $('Parse Config').first().json.config || {}; } catch (e) { return {}; } })();
const prev = (() => { try { return $('Resolve User Row').first().json || {}; } catch (e) { return {}; } })();
const originalMessage = chatCounter.original_message || '';
const isNewUser = preprocess?.isNewUser || false;

// ── util ──
// buang karakter kontrol, rapikan spasi, batasi panjang
const BERSIH = (s, max) => String(s ?? '')
  .split('').filter(ch => ch.charCodeAt(0) >= 32).join('')
  .replace(/\s+/g, ' ').trim().slice(0, max || 200);
// nilai yang artinya "tidak ada isi" — termasuk placeholder yang diminta ke AI
const KOSONG = (s) => {
  const t = BERSIH(s).toLowerCase().replace(/[.\s]+$/, '');
  return !t || t === '-' || t === '...' || t === 'belum disebut' || t === 'belum tahu'
      || t === 'tidak disebut' || t === 'n/a' || t === 'na' || t === 'null' || t === 'undefined';
};

// ── TAG sederhana ──
const isTalkToAdmin = aiOutput.includes('[TALK_TO_ADMIN]');
const isUnknown     = aiOutput.includes('[UNKNOWN]');

// ── TAG: [SEND_MEDIA: key] — maksimal 2, tanpa fallback frasa ──
let isSendMedia = false, mediaKey = '';
const mediaKeysAll = [...new Set(
  [...aiOutput.matchAll(/\[\s*SEND_MEDIA\s*(?::\s*([^\]]*))?\]/gi)]
    .map(m => (m[1] || '').trim().toLowerCase())
    .filter(Boolean)
)].slice(0, 2);
if (mediaKeysAll.length) { isSendMedia = true; mediaKey = mediaKeysAll[0]; }

// ── TAG: [FACTS ...] + merge persist ──
const FACT_FIELDS = ['nama_lengkap', 'nama_bisnis', 'industri', 'masalah_utama',
                     'volume_chat', 'budget_range', 'minat_paket'];
const PANJANG = { masalah_utama: 300, nama_lengkap: 60 };
const factsMatch = aiOutput.match(/\[\s*FACTS\b([^\]]*)\]/i);
const facts = {};
if (factsMatch && factsMatch[1]) {
  const isi = factsMatch[1];
  for (const f of FACT_FIELDS) {
    const m = isi.match(new RegExp(f + '\\s*=\\s*"([^"]*)"', 'i'));
    if (m) facts[f] = m[1];
  }
  // alias: prompt versi awal memakai nama="..." untuk nama_lengkap
  const mn = isi.match(/(^|[\s\[])nama\s*=\s*"([^"]*)"/i);
  if (mn && facts.nama_lengkap === undefined) facts.nama_lengkap = mn[2];
}
const merged = {}, changed = {};
for (const f of FACT_FIELDS) {
  const max  = PANJANG[f] || 120;
  const baru = KOSONG(facts[f]) ? '' : BERSIH(facts[f], max);
  const lama = BERSIH(prev[f], max);
  merged[f]  = baru || lama;
  changed[f] = merged[f] !== '' && merged[f] !== lama;
}

// ── TAG: [DECK_REQUEST] ... [/DECK_REQUEST] ──
const DECK_FIELDS = ['nama', 'jabatan', 'nama_bisnis', 'industri', 'deskripsi_bisnis',
  'target_pelanggan', 'channel', 'sumber_leads', 'volume_chat_harian', 'jam_operasional',
  'siapa_balas_chat', 'biaya_admin_bulanan', 'sistem_sekarang', 'masalah_utama', 'pain_points',
  'aksi_utama', 'alur_setelah_chat', 'pertanyaan_tersering', 'fitur_diminati', 'nilai_transaksi',
  'prospek_per_bulan', 'minat_paket', 'budget_range', 'deadline', 'urgensi', 'bahasa_deck', 'catatan'];

let isDeckRequest = false, deckRejected = false, deckMissing = [];
const deckRequest = {};
for (const f of DECK_FIELDS) deckRequest[f] = '';

const deckBlock = aiOutput.match(/\[\s*DECK_REQUEST\s*\]([\s\S]*?)\[\s*\/\s*DECK_REQUEST\s*\]/i);
if (deckBlock) {
  isDeckRequest = true;
  const dikenal = new Set(DECK_FIELDS);
  for (const baris of deckBlock[1].split('\n')) {
    const m = baris.match(/^\s*([A-Za-z_]+)\s*:\s*(.*)$/);
    if (!m) continue;                                  // baris kosong / bukan pasangan key:value
    const k = m[1].toLowerCase();
    if (!dikenal.has(k)) continue;                     // key asing diabaikan, bukan digagalkan
    deckRequest[k] = KOSONG(m[2]) ? '' : BERSIH(m[2], 500);
  }
  // fakta yang sudah dipastikan sistem menang atas tulisan AI di blok ini
  if (!deckRequest.nama && merged.nama_lengkap) deckRequest.nama = merged.nama_lengkap;
  const DARI_FACTS = [['nama_bisnis', 'nama_bisnis'], ['industri', 'industri'],
                      ['masalah_utama', 'masalah_utama'], ['minat_paket', 'minat_paket'],
                      ['budget_range', 'budget_range'], ['volume_chat_harian', 'volume_chat']];
  for (const [dk, fk] of DARI_FACTS) {
    if (!deckRequest[dk] && merged[fk]) deckRequest[dk] = merged[fk];
  }
  // GATE TINGKAT 1 — brief tanpa ketiganya tidak cukup untuk menyusun deck
  deckMissing = ['nama_bisnis', 'industri', 'masalah_utama'].filter(f => !deckRequest[f]);
  if (deckMissing.length) {
    isDeckRequest = false;
    deckRejected = true;
    console.warn('DECK_REQUEST ditolak, tingkat 1 belum lengkap: ' + deckMissing.join(', '));
  }
}
const bahasaMerged = (KOSONG(deckRequest.bahasa_deck) ? '' : BERSIH(deckRequest.bahasa_deck, 20))
                     || BERSIH(prev.bahasa, 20);

// ── CLEAN OUTPUT (buang semua tag) ──
let cleanOutput = aiOutput
  .replace(/\[\s*DECK_REQUEST\s*\][\s\S]*?\[\s*\/\s*DECK_REQUEST\s*\]/gi, '')
  .replace(/\[\s*\/?\s*DECK_REQUEST\s*\][\s\S]*$/gi, '')   // blok tak tertutup (output terpotong)
  .replace(/\[\s*SEND_MEDIA\s*(?::[^\]]*)?\]/gi, '')
  .replace(/\[TALK_TO_ADMIN\]/gi, '')
  .replace(/\[UNKNOWN\]/gi, '')
  .replace(/\[\s*FACTS\b[^\]]*\]/gi, '');

const preInternalStrip = cleanOutput;
const internalKeywords = ['berdasarkan faq','berdasarkan data','menurut data','dari faq','dari sheet','data terverifikasi','faq relevan','data yang tersedia','saya cek data','saya cek faq','saya cek sheet','cek di sheet','cek di database'];
const keywordPattern = internalKeywords.join('|');
cleanOutput = cleanOutput.replace(new RegExp(`^\\s*([^.!?]*?(${keywordPattern})[^.!?]*[.!?]\\s*)`, 'i'), '');
cleanOutput = cleanOutput.replace(new RegExp(`^\\s*(${keywordPattern}).*?(\\n|\\.|$)`, 'i'), '');
cleanOutput = cleanOutput.replace(/^\s*(Berdasarkan|Menurut|Dari)\s+(data|faq|sheet|referensi)[^.!?]*[.!?]\s*/i, '');
if (!cleanOutput.trim() && preInternalStrip.trim()) cleanOutput = preInternalStrip;
cleanOutput = cleanOutput.trim();

// bersihkan markdown (URL di-mask dulu supaya tidak ikut terpotong)
const urlRegex = /https?:\/\/[^\s)]+/g;
const maskedUrls = [];
cleanOutput = cleanOutput.replace(urlRegex, (m) => { maskedUrls.push(m); return `\x00URL${maskedUrls.length - 1}\x00`; });
cleanOutput = cleanOutput
  .replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1').replace(/_([^_]+)_/g, '$1')
  .replace(/~~([^~]+)~~/g, '$1').replace(/`([^`]+)`/g, '$1').replace(/[\*_~`]/g, '');
cleanOutput = cleanOutput
  .replace(/(\d)\s*[—–]\s*(\d)/g, '$1-$2').replace(/\s*[—–]\s*/g, ', ').replace(/\s*;\s*/g, ', ')
  .replace(/\s{2,}/g, ' ').replace(/\s+([,.])/g, '$1').replace(/,\s*,/g, ',').trim();
cleanOutput = cleanOutput.replace(/\x00URL(\d+)\x00/g, (_, idx) => maskedUrls[parseInt(idx)]);
cleanOutput = cleanOutput.replace(/(^|\n)([a-z])/g, (m, p1, p2) => p1 + p2.toUpperCase());

if (!cleanOutput || cleanOutput.trim() === '') {
  cleanOutput = isUnknown
    ? 'Maaf yaa, untuk yang ini aku belum tahu. Nanti aku cek dulu dan kabari lagi.'
    : 'Maaf, ada kendala sebentar. Boleh diketik ulang yaa.';
}

// ── FAIL LOUD: brief ditolak tapi balasan terlanjur menjanjikan deck ──
// Tag ditolak harus MENGUBAH balasan, bukan cuma dibuang — kalau tidak, prospek
// diberi janji yang tidak ada catatannya di mana pun. Override hanya dilakukan
// kalau balasannya memang menjanjikan; kalau tidak, tag cukup didiamkan.
if (deckRejected) {
  const low = cleanOutput.toLowerCase();
  const menjanjikan = /(deck|proposal|penawaran)/.test(low)
                   && /(susun|siapkan|buatkan|kirim|hubungi|kabari)/.test(low);
  if (menjanjikan) {
    const TANYA = {
      nama_bisnis:   'Boleh tahu nama bisnisnya dulu kak? Biar aku catat dengan benar.',
      industri:      'Bisnisnya bergerak di bidang apa kak?',
      masalah_utama: 'Sekarang yang paling bikin repot soal chat masuk itu apa kak?',
    };
    cleanOutput = TANYA[deckMissing[0]] || 'Boleh cerita sedikit soal bisnisnya kak?';
    console.warn('Balasan diganti: janji deck tanpa brief tingkat 1.');
  }
}

// ── RESOLVE MEDIA URL + caption dari LINKS ──
// Disederhanakan dari Persada: kolom 'Tipe Unit' tidak ada di sheet VIRA Steven,
// jadi seluruh penyempitan berbasis tipe unit dibuang. Gate ambigu & eskalasi
// manual dipertahankan apa adanya.
let mediaUrl = '', mediaCaption = '';
let isMediaManual = false, mediaRequestSummary = '';
let isMediaAmbiguous = false, mediaCandidates = [];
if (isSendMedia) {
  let linkRows = [];
  try { linkRows = $('Read LINKS Data').all().map(i => i.json); } catch (e) {}
  const norm = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const active = linkRows.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(String(r['Status'] || '')));

  const resolveRow = (row) => {
    const tipeRow = norm(row['Tipe']);
    if (tipeRow === 'location' || tipeRow === 'website') {
      // bukan file: jangan lewat Download Media / Send Media Kirimi, tempel sebagai teks
      isSendMedia = false;
      const url = String(row['URL'] || '').trim();
      const label = String(row['Caption'] || '').trim();
      if (url) {
        const line = label ? `${label} ${url}` : url;
        cleanOutput = cleanOutput.trim() ? `${cleanOutput}\n\n${line}` : line;
      }
      return;
    }
    mediaUrl = String(row['URL'] || '').trim();
    mediaCaption = String(row['Caption'] || '').trim() || 'Ini file yang diminta yaa.';
  };

  const exactRow = active.find(r => norm(r['Nama Link']) === mediaKey);
  if (exactRow && String(exactRow['URL'] || '').trim()) {
    resolveRow(exactRow);
  } else {
    const tokensOf = s => norm(s).split(/[^a-z0-9]+/i).filter(Boolean);
    const GENERIC = new Set(['foto','gambar','photo','video','klip','file','media','minta','contoh','link','dokumen']);
    const keyTokens = tokensOf(mediaKey);
    const qualifiers = keyTokens.filter(t => !GENERIC.has(t) && t.length >= 3);

    const rowBag  = (r) => [...tokensOf(r['Keyword']), ...tokensOf(r['Nama Link'])];
    const nameMatch    = (r) => { const nl = norm(r['Nama Link']); return !!nl && (nl.includes(mediaKey) || mediaKey.includes(nl)); };
    const keywordMatch = (r) => tokensOf(r['Keyword']).some(kw => keyTokens.includes(kw));

    let candidates = active.filter(r => nameMatch(r) || keywordMatch(r));
    // kandidat wajib memenuhi minimal satu kata pembeda yang diminta
    if (qualifiers.length) {
      candidates = candidates.filter(r => { const bag = rowBag(r); return qualifiers.some(q => bag.includes(q)); });
    }

    const byUrl = new Map();
    for (const r of candidates) {
      const u = String(r['URL'] || '').trim();
      if (!u || u.startsWith('<<')) continue;          // placeholder '<<ISI MANUAL>>' bukan URL
      if (!byUrl.has(u)) byUrl.set(u, r);
    }
    const unique = [...byUrl.values()];

    if (unique.length === 1) {
      resolveRow(unique[0]);
    } else if (unique.length > 1) {
      // sistem yang bertanya: media TIDAK dikirim, Steven TIDAK dinotif
      isMediaAmbiguous = true;
      isSendMedia = false;
      isMediaManual = false;
      mediaUrl = ''; mediaCaption = '';
      mediaCandidates = unique.map(r => ({ key: String(r['Nama Link'] || '').trim() }));
      const opts = mediaCandidates.map(c => c.key).filter(Boolean);
      const optText = opts.length === 2 ? `${opts[0]} atau ${opts[1]}`
                    : `${opts.slice(0, -1).join(', ')}, atau ${opts[opts.length - 1]}`;
      cleanOutput = `Ada beberapa yang cocok kak, mau yang mana yaa, ${optText}?`;
      console.log('SEND_MEDIA ambigu, tanya balik:', JSON.stringify(mediaCandidates));
    } else {
      console.warn('SEND_MEDIA key tidak ada di LINKS, fallback manual:', mediaKey);
      isSendMedia = false;
      isMediaManual = true;
      const userMsg = (preprocess && preprocess.actualUserMessage) || originalMessage || '';
      mediaRequestSummary = (mediaKey ? ('key="' + mediaKey + '" ') : '') + (userMsg ? ('| pesan user: ' + String(userMsg).slice(0, 300)) : '');
    }
  }
}

// ── MEDIA KE-2 (mis. foto + dokumen dalam satu balasan) ──
let isSendMedia2 = false, mediaUrl2 = '', mediaCaption2 = '';
if (isSendMedia && mediaUrl && !isMediaAmbiguous && mediaKeysAll.length >= 2) {
  let linkRows2 = [];
  try { linkRows2 = $('Read LINKS Data').all().map(i => i.json); } catch (e) {}
  const norm2 = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const active2 = linkRows2.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(String(r['Status'] || '')));
  const key2 = mediaKeysAll.find(k => k && k !== mediaKey) || '';
  const row2 = key2 ? active2.find(r => norm2(r['Nama Link']) === key2) : null;
  if (row2) {
    const tipe2 = norm2(row2['Tipe']);
    const url2 = String(row2['URL'] || '').trim();
    if (url2 && !url2.startsWith('<<') && url2 !== mediaUrl && tipe2 !== 'location' && tipe2 !== 'website') {
      isSendMedia2 = true;
      mediaUrl2 = url2;
      mediaCaption2 = String(row2['Caption'] || '').trim() || 'Ini file berikutnya yaa.';
    }
  }
}

return [{
  json: {
    ...chatCounter, ...preprocess, ...item.json,
    cleanOutput,
    aiOutputRaw: aiOutput,
    isTalkToAdmin,
    isUnknown,
    needs_unknown: isUnknown ? 'true' : 'false',
    isSendMedia, mediaUrl, mediaCaption, mediaKey,
    isSendMedia2, mediaUrl2, mediaCaption2,
    isMediaManual, mediaRequestSummary,
    isMediaAmbiguous, mediaCandidates,
    isDeckRequest, deckRequest, deckRejected, deckMissing,
    original_message: originalMessage,
    is_new_user: isNewUser,
    nama_lengkap_merged: merged.nama_lengkap,
    nama_changed:        changed.nama_lengkap,
    nama_lengkap_changed: changed.nama_lengkap,
    nama_bisnis_merged:  merged.nama_bisnis,
    nama_bisnis_changed: changed.nama_bisnis,
    industri_merged:     merged.industri,
    industri_changed:    changed.industri,
    masalah_utama_merged:  merged.masalah_utama,
    masalah_utama_changed: changed.masalah_utama,
    volume_chat_merged:  merged.volume_chat,
    volume_chat_changed: changed.volume_chat,
    budget_range_merged:  merged.budget_range,
    budget_changed:       changed.budget_range,
    budget_range_changed: changed.budget_range,
    minat_paket_merged:  merged.minat_paket,
    minat_paket_changed: changed.minat_paket,
    bahasa_merged: bahasaMerged,
  }
}];
""".strip()

for n in d["nodes"]:
    if n["name"] == "Process All":
        n["parameters"]["jsCode"] = PROCESS_ALL_JS
        log.append(f"Process All ditulis ulang ({len(PROCESS_ALL_JS)} char, dari 27.045)")


# ───────────────── 14. Rakit Konteks: tambah brief_context ─────────────────
RAKIT_BRIEF = """
// ---------- 6. brief_context ----------
const briefRaw = txt(stats['brief_terisi']);
const brief_context = briefRaw
  ? ('Isian brief yang sudah tertangkap untuk orang ini: ' + briefRaw
     + '\\nJangan menanyakan ulang isian di atas.')
  : '(belum ada brief yang terkirim untuk orang ini)';

return [{
  json: {
    ...item,
    prospect_context,
    about_context,
    program_context,
    links_context,
    faq_context,
    brief_context,
  }
}];
""".strip()

for n in d["nodes"]:
    if n["name"] != "Rakit Konteks":
        continue
    js = n["parameters"]["jsCode"]
    if "brief_context" in js:
        break
    potong = js.index("return [{")
    n["parameters"]["jsCode"] = js[:potong] + RAKIT_BRIEF
    log.append("Rakit Konteks: tambah brief_context (variabel konteks ke-6)")


# ───────────────── 15. rantai DECK_REQUEST: 7 node baru ─────────────────
DECK_FIELDS = ['nama', 'jabatan', 'nama_bisnis', 'industri', 'deskripsi_bisnis',
    'target_pelanggan', 'channel', 'sumber_leads', 'volume_chat_harian', 'jam_operasional',
    'siapa_balas_chat', 'biaya_admin_bulanan', 'sistem_sekarang', 'masalah_utama', 'pain_points',
    'aksi_utama', 'alur_setelah_chat', 'pertanyaan_tersering', 'fitur_diminati', 'nilai_transaksi',
    'prospek_per_bulan', 'minat_paket', 'budget_range', 'deadline', 'urgensi', 'bahasa_deck', 'catatan']
REQ_COLS = ['ts', 'update_terakhir', 'no_wa'] + DECK_FIELDS + ['kelengkapan', 'status_followup']

MERGE_BRIEF_JS = r"""
// ── Merge Brief — VIRA Steven ──
// Tag [DECK_REQUEST] selalu dikirim lengkap 27 baris, tapi sebagian isinya "belum disebut"
// (sudah dinormalkan jadi '' di Process All). Penggabungan dengan baris REQUESTS lama
// dilakukan DI SINI, bukan diserahkan ke AI — supaya emisi kedua tidak menghapus isian
// yang sudah pernah tertangkap di emisi pertama.
const FIELDS = __FIELDS__;
const LABEL = __LABEL__;

const pa  = $('Process All').first().json;
const key = $('Resolve User Row').first().json.resolved_key;
const digits = v => String(v ?? '').replace(/\D/g, '');

let lama = {};
try {
  const baris = $('Read REQUESTS').all().map(i => i.json)
    .filter(r => r && digits(r['no_wa']) === digits(key));
  lama = baris.length ? baris[baris.length - 1] : {};
} catch (e) { console.warn('Read REQUESTS tidak terbaca:', e.message); }

const baru = pa.deckRequest || {};
const hasil = {};
for (const f of FIELDS) {
  const v = String(baru[f] ?? '').trim();
  const l = String(lama[f] ?? '').trim();
  hasil[f] = v || l;                       // nilai baru menang hanya kalau ada isinya
}

const terisi = FIELDS.filter(f => hasil[f]);
const kosong = FIELDS.filter(f => !hasil[f]);
const nowS = Math.floor(Date.now() / 1000);
const stamp = new Date().toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' });
const tsLama = String(lama['ts'] || '').trim();
const revisi = tsLama ? ' (diperbarui)' : '';

const notif_text =
  `📋 [VIRA Steven] BRIEF DECK${revisi}\n` +
  `${hasil.nama_bisnis || '(nama bisnis belum disebut)'} — ${hasil.industri || '-'}\n` +
  `WA: ${key}\n` +
  `Kelengkapan: ${terisi.length}/${FIELDS.length}\n\n` +
  terisi.map(f => `${LABEL[f] || f}: ${hasil[f]}`).join('\n') +
  `\n\nBelum tergali: ${kosong.map(f => LABEL[f] || f).join(', ') || '(lengkap)'}`;

return [{
  json: {
    ...hasil,
    ts: tsLama || stamp,
    update_terakhir: stamp,
    no_wa: key,
    kelengkapan: `${terisi.length}/${FIELDS.length}`,
    status_followup: String(lama['status_followup'] || '').trim() || 'BARU',
    brief_terisi: terisi.join(','),
    brief_jumlah: terisi.length,
    notif_text,
  }
}];
""".strip()

LABEL = {
    'nama': 'Nama', 'jabatan': 'Jabatan', 'nama_bisnis': 'Bisnis', 'industri': 'Industri',
    'deskripsi_bisnis': 'Deskripsi', 'target_pelanggan': 'Target pelanggan', 'channel': 'Channel',
    'sumber_leads': 'Sumber leads', 'volume_chat_harian': 'Chat/hari', 'jam_operasional': 'Jam operasional',
    'siapa_balas_chat': 'Yang balas chat', 'biaya_admin_bulanan': 'Biaya admin', 'sistem_sekarang': 'Sistem sekarang',
    'masalah_utama': 'Masalah utama', 'pain_points': 'Keluhan lain', 'aksi_utama': 'Aksi utama',
    'alur_setelah_chat': 'Alur setelah chat', 'pertanyaan_tersering': 'Pertanyaan tersering',
    'fitur_diminati': 'Fitur diminati', 'nilai_transaksi': 'Nilai transaksi', 'prospek_per_bulan': 'Prospek/bulan',
    'minat_paket': 'Minat paket', 'budget_range': 'Budget', 'deadline': 'Deadline', 'urgensi': 'Urgensi',
    'bahasa_deck': 'Bahasa', 'catatan': 'Catatan',
}
MERGE_BRIEF_JS = MERGE_BRIEF_JS \
    .replace("__FIELDS__", json.dumps(DECK_FIELDS, ensure_ascii=False)) \
    .replace("__LABEL__", json.dumps(LABEL, ensure_ascii=False))


def skema(cols):
    return [{"id": c, "displayName": c, "required": False, "defaultMatch": False,
             "display": True, "type": "string", "canBeUsedToMatch": True} for c in cols]


DOC_RL = {"__rl": True, "value": SHEET_ID, "mode": "id", "cachedResultName": "VIRA Steven Database"}
GCRED = {"googleApi": {"id": "", "name": "Google Service Account VIRA Steven"}}
KIRIMI = "https://api.kirimi.id/v1/send-message"
CFG = "$('Parse Config').first().json.config"

if not any(n["name"] == "IF Deck Request" for n in d["nodes"]):
    pa_node = next(n for n in d["nodes"] if n["name"] == "Process All")
    x0, y0 = pa_node["position"][0], pa_node["position"][1] + 1200

    baru_nodes = [
        {"parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "",
                                                   "typeValidation": "strict", "version": 3},
                                       "conditions": [{"id": "deck-req-cond-0001",
                                                       "leftValue": "={{ $json.isDeckRequest }}",
                                                       "rightValue": "",
                                                       "operator": {"type": "boolean", "operation": "true",
                                                                    "singleValue": True}}],
                                       "combinator": "and"},
                        "options": {}},
         "type": "n8n-nodes-base.if", "typeVersion": 2.3, "position": [x0, y0],
         "id": "deck-if-0001", "name": "IF Deck Request"},

        {"parameters": {"authentication": "serviceAccount", "documentId": dict(DOC_RL),
                        "sheetName": {"__rl": True, "value": "REQUESTS", "mode": "name"},
                        "options": {}},
         "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7, "position": [x0 + 224, y0],
         "id": "deck-read-0001", "name": "Read REQUESTS",
         "alwaysOutputData": True, "onError": "continueRegularOutput",
         "retryOnFail": True, "waitBetweenTries": 2000, "credentials": json.loads(json.dumps(GCRED))},

        {"parameters": {"jsCode": MERGE_BRIEF_JS},
         "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [x0 + 448, y0],
         "id": "deck-merge-0001", "name": "Merge Brief"},

        {"parameters": {"authentication": "serviceAccount", "operation": "appendOrUpdate",
                        "documentId": dict(DOC_RL),
                        "sheetName": {"__rl": True, "value": "REQUESTS", "mode": "name"},
                        "columns": {"mappingMode": "defineBelow",
                                    "value": {c: "={{ $json['%s'] }}" % c for c in REQ_COLS},
                                    "matchingColumns": ["no_wa"], "schema": skema(REQ_COLS),
                                    "attemptToConvertTypes": False, "convertFieldsToString": True},
                        "options": {}},
         "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7, "position": [x0 + 672, y0],
         "id": "deck-write-0001", "name": "Write REQUESTS",
         "retryOnFail": True, "waitBetweenTries": 2000, "credentials": json.loads(json.dumps(GCRED))},

        # Jeda sebelum menyentuh STATS. Jalur utama menulis baris STATS yang sama lewat
        # appendOrUpdate, dan jendelanya: Wait1 (5-10 dtk acak) + kirim WA + baca STATS
        # + hitung counter -> kira-kira T+10..20 dtk. Dua appendOrUpdate yang beririsan pada
        # kunci yang sama bisa sama-sama membaca "baris belum ada" lalu sama-sama append =
        # baris ganda untuk satu nomor. 20 detik menaruh cabang ini jelas SETELAH jendela itu.
        # Prospek tidak menunggu apa pun di sini — yang tertunda cuma notifikasi ke Steven.
        {"parameters": {"amount": 20},
         "type": "n8n-nodes-base.wait", "typeVersion": 1.1, "position": [x0 + 896, y0],
         # tanpa webhookId — node Wait memakainya sebagai URL resume; string kosong lebih
         # berisiko daripada tidak ada, n8n membuatkan sendiri saat import.
         "id": "deck-wait-0001", "name": "Wait Deck"},

        {"parameters": {"authentication": "serviceAccount", "operation": "appendOrUpdate",
                        "documentId": dict(DOC_RL),
                        "sheetName": {"__rl": True, "value": "STATS", "mode": "name"},
                        "columns": {"mappingMode": "defineBelow",
                                    "value": {
                                        "No WA": "={{ $('Resolve User Row').first().json.resolved_key }}",
                                        "deck_requested": "Y",
                                        "brief_terisi": "={{ $('Merge Brief').first().json.brief_terisi }}",
                                    },
                                    "matchingColumns": ["No WA"],
                                    "schema": skema(["No WA", "deck_requested", "brief_terisi"]),
                                    "attemptToConvertTypes": False, "convertFieldsToString": True},
                        "options": {}},
         "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7, "position": [x0 + 1120, y0],
         "id": "deck-stats-0001", "name": "Update STATS Brief",
         "retryOnFail": True, "waitBetweenTries": 2000, "credentials": json.loads(json.dumps(GCRED))},

        {"parameters": {"method": "POST", "url": KIRIMI, "sendBody": True,
                        "bodyParameters": {"parameters": [
                            {"name": "user_code", "value": "={{ %s.kirimi_user_code }}" % CFG},
                            {"name": "secret", "value": "={{ %s.kirimi_secret }}" % CFG},
                            {"name": "device_id", "value": "={{ %s.kirimi_device_id }}" % CFG},
                            {"name": "phone", "value": "={{ %s.admin_phone }}" % CFG},
                            {"name": "message", "value": "={{ $('Merge Brief').first().json.notif_text }}"},
                        ]}, "options": {}},
         "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.3, "position": [x0 + 1344, y0],
         "id": "deck-notif-0001", "name": "Notify Admin Deck", "onError": "continueRegularOutput"},
    ]
    d["nodes"].extend(baru_nodes)

    rantai = ["IF Deck Request", "Read REQUESTS", "Merge Brief", "Write REQUESTS",
              "Wait Deck", "Update STATS Brief", "Notify Admin Deck"]
    for a, b in zip(rantai, rantai[1:]):
        d["connections"][a] = {"main": [[{"node": b, "type": "main", "index": 0}]]}
    d["connections"]["Process All"]["main"][0].append(
        {"node": "IF Deck Request", "type": "main", "index": 0})
    log.append("tambah 7 node rantai DECK_REQUEST (IF -> Read -> Merge -> Write -> Wait -> STATS -> Notif)")


# ───────────────── 16. Collect Handover Context: profil VIRA Steven ─────────────────
# Node ini satu-satunya pemakai surveyData / unit_interest_merged / lokasi_kerja_merged,
# yang sudah tidak diproduksi Process All setelah langkah 13.
HANDOVER_PROFIL = r"""const pa = $('Process All').first().json;
const profil = {
  // PRIORITAS: [FACTS] turn ini > nama_lengkap tersimpan > push name WA.
  // JANGAN pakai statsRow['Nama'] duluan — itu nama akun WhatsApp, bukan nama
  // yang user sebutkan sendiri.
  nama: pa.nama_lengkap_merged || statsRow['nama_lengkap'] || statsRow['Nama'] || $('Chat Counter').first().json.user_name || '',
  nama_akun_wa: statsRow['Nama'] || $('Chat Counter').first().json.user_name || '',
  no_wa: key,
  pesan_pertama: statsRow['Pesan Pertama'] || '',
  nama_bisnis: pa.nama_bisnis_merged || statsRow['nama_bisnis'] || '',
  industri: pa.industri_merged || statsRow['industri'] || '',
  masalah_utama: pa.masalah_utama_merged || statsRow['masalah_utama'] || '',
  volume_chat: pa.volume_chat_merged || statsRow['volume_chat'] || '',
  minat_paket: pa.minat_paket_merged || statsRow['minat_paket'] || '',
  budget_range: pa.budget_range_merged || statsRow['budget_range'] || '',
  brief_terisi: statsRow['brief_terisi'] || '(belum ada brief)',
  sudah_minta_deck: String(statsRow['deck_requested'] || '').trim().toUpperCase() === 'Y' ? 'ya' : 'belum',
  lead_source: $('Detect Lead Source').first().json.lead_source_final || statsRow['lead_source'] || '',
  jumlah_chat: statsRow['Counter'] || '',
};"""

for n in d["nodes"]:
    if n["name"] != "Collect Handover Context":
        continue
    js = n["parameters"]["jsCode"]
    awal = js.index("const pa = $('Process All')")
    akhir = js.index("return [{ json: {")
    n["parameters"]["jsCode"] = js[:awal] + HANDOVER_PROFIL + "\n\n" + js[akhir:]
    log.append("Collect Handover Context: profil survei/unit -> profil brief VIRA Steven")


# ───────────────── 17. sisa jejak Persada di teks yang dilihat Steven ─────────────────
raw = json.dumps(d, ensure_ascii=False)
n_pcr = raw.count("[PCR]")
raw = raw.replace("🏠 [PCR] SURVEY BARU — HANDOVER KE TIM LAPANGAN",
                  "🤝 [VIRA Steven] PROSPEK MINTA DISAMBUNGKAN") \
         .replace("[PCR]", "[VIRA Steven]") \
         .replace("PCR_Database", "VIRA Steven Database")
d = json.loads(raw)
log.append(f"{n_pcr} penanda [PCR] di teks notifikasi -> [VIRA Steven]")

# Record to UNKNOWN menulis kolom 'message' yang tidak ada di tab UNKNOWN -> append gagal
for n in d["nodes"]:
    if n["name"] != "Record to UNKNOWN":
        continue
    kol = n["parameters"]["columns"]
    v = kol["value"]
    if "message" in v:
        v["Jawaban VIRA"] = v.pop("message")
        sk = kol.get("schema")
        if isinstance(sk, list):
            for c in sk:
                if c.get("id") == "message":
                    c["id"] = c["displayName"] = "Jawaban VIRA"
        log.append("Record to UNKNOWN: kolom 'message' -> 'Jawaban VIRA'")


# ───────────────── 18. rantai handover masih berdomain properti ─────────────────
def ganti(js, lama, baru, ket):
    if lama not in js:
        print(f"!! anchor tidak ditemukan: {ket}"); sys.exit(1)
    return js.replace(lama, baru, 1)


for n in d["nodes"]:
    # (a) Format Handover Message — dua masalah dalam satu node
    if n["name"] == "Format Handover Message":
        js = n["parameters"]["jsCode"]
        if "cfg.field_team_phone" in js:
            # BUG: langkah 8 hanya mengganti pola "config.field_team_phone"; di node ini
            # variabelnya bernama `cfg`, jadi luput. Akibatnya `tujuan` kosong dan node
            # return [] — SELURUH notifikasi handover tidak pernah terkirim ke Steven.
            js = ganti(js, """let tujuan = (trigger === 'DELEGATION')
  ? (Array.isArray(cfg.field_team_phone) ? cfg.field_team_phone : [cfg.field_team_phone])
  : [cfg.admin_phone];""",
                       """let tujuan = [cfg.admin_phone];""", "tujuan handover")
            js = ganti(js, """  summary = `PROFIL KLIEN: ${p.nama || '-'}${p.lokasi_kerja ? ', ' + p.lokasi_kerja : ''}, ${p.no_wa || '-'}, sumber ${p.lead_source || 'belum diketahui'}
TIPE UNIT DIMINATI: ${p.unit_interest || 'belum diketahui'}
BUDGET/KPR: ${p.budget_range || 'belum dibahas'}
STATUS SURVEY: ${p.survey || 'belum dijadwalkan'}`;""",
                       """  summary = `PROSPEK: ${p.nama || '-'}, ${p.no_wa || '-'}, sumber ${p.lead_source || 'belum diketahui'}
BISNIS: ${p.nama_bisnis || 'belum diketahui'}${p.industri ? ' (' + p.industri + ')' : ''}
MASALAH UTAMA: ${p.masalah_utama || 'belum dibahas'}
SKALA: ${p.volume_chat || 'belum diketahui'} chat/hari
MINAT: ${p.minat_paket || 'belum disebut'}, budget ${p.budget_range || 'belum dibahas'}
BRIEF DECK: ${p.sudah_minta_deck === 'ya' ? 'sudah — ' + p.brief_terisi : 'belum'}`;""",
                       "fallback ringkasan handover")
            n["parameters"]["jsCode"] = js
            log.append("Format Handover Message: cfg.field_team_phone -> admin_phone (notif handover sebelumnya tidak pernah terkirim)")

    # (b) Summarize Handover — prompt masih merangkum calon pembeli properti
    if n["name"] == "Summarize Handover":
        t = n["parameters"].get("text", "")
        if "Persada Cisoka Residence" in t:
            n["parameters"]["text"] = (
                "=Kamu asisten internal yang merangkum percakapan calon klien jasa AI Customer Service "
                "untuk Steven. Buat ringkasan SINGKAT, PADAT, FAKTUAL dalam Bahasa Indonesia. Hanya gunakan "
                "DATA PROFIL dan TRANSKRIP di bawah. JANGAN mengarang, tulis \"belum diketahui\" bila kosong. "
                "Tanpa basa-basi. Kalau \"Nama akun WA\" berbeda dari \"Nama\", pakai \"Nama\" dan sebutkan "
                "akun WA-nya dalam kurung. Kalau sama, sebut sekali saja.\n\n"
                "ATURAN FORMAT (WAJIB): keluarkan PLAIN TEXT murni. DILARANG memakai markdown — tanpa tanda "
                "bintang (* atau **), tanpa underscore, tanpa backtick, tanpa heading (#), tanpa bullet simbol. "
                "Tulis label apa adanya, contoh: Profil Prospek: ...\n\n"
                "Keluarkan PERSIS format berikut:\n"
                "Profil Prospek: <nama, no WA, sumber>\n"
                "Bisnisnya: <nama bisnis, industri, apa yang dijual>\n"
                "Masalah Utama: <masalah yang dia keluhkan, atau belum dibahas>\n"
                "Skala: <chat per hari, siapa yang balas sekarang>\n"
                "Minat: <paket yang disebut, budget, deadline>\n"
                "Status Brief: <isian brief yang sudah tertangkap, atau belum ada brief>\n"
                "Poin Penting: <keberatan/kendala/urgensi, maks 3 poin>\n"
                "Ringkasan: <1 kalimat konkret>\n\n"
                "DATA PROFIL:\n"
                "Nama: {{ $json.handover_profil.nama }}\n"
                "Nama akun WA: {{ $json.handover_profil.nama_akun_wa }}\n"
                "No WA: {{ $json.handover_profil.no_wa }}\n"
                "Sumber: {{ $json.handover_profil.lead_source }}\n"
                "Nama bisnis: {{ $json.handover_profil.nama_bisnis }}\n"
                "Industri: {{ $json.handover_profil.industri }}\n"
                "Masalah utama (sistem): {{ $json.handover_profil.masalah_utama }}\n"
                "Volume chat (sistem): {{ $json.handover_profil.volume_chat }}\n"
                "Minat paket (sistem): {{ $json.handover_profil.minat_paket }}\n"
                "Budget (sistem): {{ $json.handover_profil.budget_range }}\n"
                "Sudah minta deck: {{ $json.handover_profil.sudah_minta_deck }}\n"
                "Brief terisi: {{ $json.handover_profil.brief_terisi }}\n"
                "Jumlah chat: {{ $json.handover_profil.jumlah_chat }}\n\n"
                "TRANSKRIP SESI:\n{{ $json.handover_transcript }}")
            log.append("Summarize Handover: prompt properti -> prospek jasa AI CS")

    # (c) Log EVENTS Delegated — detail masih merangkai surveyData yang sudah tidak ada
    if n["name"] == "Log EVENTS Delegated":
        v = n["parameters"]["columns"]["value"]
        if "surveyData" in str(v.get("detail", "")):
            v["detail"] = ("={{ 'Handover | bisnis: ' + ($('Process All').first().json.nama_bisnis_merged || '-')"
                           " + ' | industri: ' + ($('Process All').first().json.industri_merged || '-')"
                           " + ' | brief: ' + ($('Resolve User Row').first().json.brief_terisi || 'belum ada') }}")
            log.append("Log EVENTS Delegated: detail survey -> ringkasan handover VIRA Steven")


# ───────────────── 19. domain Persada di teks yang dibaca AI & prospek ─────────────────
# Ini yang paling menentukan apakah bot terdengar seperti VIRA Steven atau seperti
# chatbot perumahan. Semuanya masuk ke prompt runtime, bukan sekadar komentar.
for n in d["nodes"]:

    # (a) Cek_user_status — INTRO hardcoded "Persada Cisoka Residence" + blok SYSTEM_DATA
    #     berisi slot properti (LOKASI_KERJA, ASK_UNIT, PENDING_SURVEY). Blok ini dikirim
    #     sebagai pesan user ke AI setiap giliran.
    if n["name"] == "Cek_user_status":
        js = n["parameters"]["jsCode"]
        if "Persada Cisoka Residence" in js:
            awal, akhir = js.index("const INTRO ="), js.index("return [{")
            js = js[:awal] + r"""const aiSystemData = `[SYSTEM_DATA]
USER_WA: ${resolvedKey}
IS_NEW_USER: ${isNewUser}
NAMA_LENGKAP: ${namaLengkap || 'UNKNOWN'}
TANGGAL_SEKARANG: ${tanggalSekarang} (${hariSekarang}) ${jamSekarang} WIB

CRITICAL INSTRUCTION:
${isNewUser
  ? 'USER BARU. Buka dengan perkenalan sesuai bagian PERKENALAN di instruksimu — susun dengan kalimatmu sendiri, jangan disalin persis, lalu gabungkan dengan jawaban atas pertanyaannya dalam SATU pesan.'
  : 'User lama. JANGAN memperkenalkan diri lagi, lanjutkan percakapan secara natural.'}

[USER QUERY]
${userQueryText}`;

""" + js[akhir:]
            n["parameters"]["jsCode"] = js
            log.append("Cek_user_status: INTRO & blok SYSTEM_DATA properti -> VIRA Steven")

    # (b) Preprocess - Context Detection — menyuntikkan perintah memasang [SCHEDULE_SURVEY].
    #     Tag itu sudah tidak diparsing MAUPUN dibersihkan Process All, jadi kalau AI
    #     menurutinya, tag mentah ikut terkirim ke layar prospek.
    if n["name"] == "Preprocess - Context Detection":
        js = n["parameters"]["jsCode"]
        if "SCHEDULE_SURVEY" in js:
            awal = js.index("let aiContext = '';")
            akhir = js.index("// ── RAKIT INPUT AI ──")
            js = js[:awal] + r"""let aiContext = '';
if (askingPrice) aiContext += `User menanyakan harga. Sebut kisaran dari DATA PRODUK lalu arahkan ke Steven untuk angka final. Jangan menawar, jangan memberi diskon. `;
else if (budgetMention) aiContext += `User menyebut kisaran anggaran ${budgetMention}. Kaitkan ke paket yang paling masuk akal, tetap pakai kisaran resmi. `;
if (wantsMedia) aiContext += `User meminta file. Kalau ada yang cocok di DAFTAR MEDIA, pasang [SEND_MEDIA: <nama-link>] persis seperti tertulis di daftar. Kalau tidak ada yang cocok, jangan pasang tag apa pun dan jangan mengarang nama link. `;
if (wantsSurvey || mentionsDateTime) aiContext += `User menyinggung waktu atau jadwal. Kamu tidak bisa menjadwalkan apa pun sendiri — kalau dia ingin bicara langsung dengan Steven, pakai [TALK_TO_ADMIN]. Jangan menjanjikan jam atau tanggal. `;

""" + js[akhir:]
            n["parameters"]["jsCode"] = js
            log.append("Preprocess: instruksi [SCHEDULE_SURVEY] dibuang, konteks diarahkan ke harga/media/TALK_TO_ADMIN")

    # (c) Siapkan Vision Request — system prompt vision masih menyebut perumahan Persada,
    #     dan kategorinya (denah, siteplan, simulasi KPR) tidak ada padanannya di sini.
    if n["name"] == "Siapkan Vision Request":
        js = n["parameters"]["jsCode"]
        if "Persada Cisoka Residence" in js:
            awal = js.index("const SYSTEM = [")
            akhir = js.index("].join", awal) + len("].join('\\n');")
            js = js[:awal] + r"""const SYSTEM = [
  'Kamu asisten vision untuk Steven versi AI, chatbot WhatsApp yang menjual jasa AI Customer Service.',
  'Tugasmu HANYA mendeskripsikan gambar yang dikirim calon klien, supaya bot bisa membalas dengan tepat.',
  '',
  'ATURAN:',
  '- Bahasa Indonesia, padat, maksimal 5 kalimat per gambar.',
  '- Untuk tiap gambar tulis 2 baris:',
  '  KATEGORI: <pilih SATU> SCREENSHOT_CHAT | SCREENSHOT_SISTEM_ATAU_DASHBOARD | BROSUR_ATAU_IKLAN | LOGO_ATAU_BRANDING | FOTO_PRODUK_ATAU_TOKO | TANGKAPAN_LAYAR_PENAWARAN_ATAU_HARGA | KTP_ATAU_DOKUMEN_PRIBADI | BUKTI_TRANSFER | LAINNYA',
  '  ISI: apa yang terlihat.',
  '- Teks/angka penting di dalam gambar (nama bisnis, nominal, jumlah chat, tanggal, nama platform) tulis PERSIS apa adanya.',
  '- DILARANG menebak. Tidak terbaca -> tulis "tidak terbaca".',
  '- DILARANG menilai, menjawab pertanyaan user, atau memberi saran. Deskripsi saja.',
  '- PRIVASI: DILARANG menyalin NIK/nomor KTP, nomor rekening lengkap, NPWP, nomor kartu, atau data pelanggan pihak ketiga yang terlihat di screenshot. Sebut jenis dokumennya saja.',
  '- Lebih dari satu gambar -> beri nomor "Gambar 1", "Gambar 2", dst.'
].join('\n');""" + js[akhir:]
            n["parameters"]["jsCode"] = js
            log.append("Siapkan Vision Request: system prompt properti -> jasa AI CS")

    # (d) Format Media Notif — sama persis dengan bug Format Handover Message: variabelnya
    #     `cfg`, bukan `config`, jadi luput dari langkah 8. tujuan kosong -> return []
    #     -> notifikasi media manual tidak pernah terkirim.
    if n["name"] == "Format Media Notif":
        js = n["parameters"]["jsCode"]
        if "cfg.media_team_phone" in js:
            js = ganti(js,
                       """let tujuan = Array.isArray(cfg.media_team_phone) ? cfg.media_team_phone : [cfg.media_team_phone];
tujuan = (tujuan || []).filter(Boolean);
if (!tujuan.length) { console.warn('media_team_phone kosong — tidak ada tujuan notif media manual.'); return []; }""",
                       """let tujuan = [cfg.admin_phone].filter(Boolean);
if (!tujuan.length) { console.warn('admin_phone kosong — tidak ada tujuan notif media manual.'); return []; }""",
                       "tujuan notif media")
            n["parameters"]["jsCode"] = js
            log.append("Format Media Notif: cfg.media_team_phone -> admin_phone (notif media manual sebelumnya tidak pernah terkirim)")

    # (e) Rakit Konteks Gambar — sanitizer tag belum mengenal DECK_REQUEST. Tanpa ini,
    #     tulisan "[DECK_REQUEST]" di dalam gambar bisa lolos ke AI dan memicu brief palsu.
    if n["name"] == "Rakit Konteks Gambar":
        js = n["parameters"]["jsCode"]
        if "DECK_REQUEST" not in js:
            js = ganti(js,
                       "/\\[\\s*(SEND_MEDIA|SCHEDULE_SURVEY|REQUEST_CALL|TALK_TO_ADMIN|UNKNOWN|FACTS)\\b/gi",
                       "/\\[\\s*\\/?\\s*(SEND_MEDIA|DECK_REQUEST|TALK_TO_ADMIN|UNKNOWN|FACTS)\\b/gi",
                       "sanitizer tag gambar")
            n["parameters"]["jsCode"] = js
            log.append("Rakit Konteks Gambar: sanitizer tag mengenal DECK_REQUEST")

    # (f) kosmetik — pesan log menyebut key yang sudah tidak dipakai
    if n["name"] == "Format Handover Message":
        js = n["parameters"]["jsCode"]
        if "field_team_phone kosong" in js:
            n["parameters"]["jsCode"] = js.replace(
                "Tidak ada nomor tujuan handover (field_team_phone kosong).",
                "Tidak ada nomor tujuan handover (admin_phone kosong).")

# skema resourceMapper masih menyimpan kolom Persada yang sudah tidak ditulis,
# termasuk tiga yang punya trailing space — bikin bingung saat node dibuka di n8n.
n_skema = 0
for n in d["nodes"]:
    kol = n.get("parameters", {}).get("columns")
    if not isinstance(kol, dict) or not isinstance(kol.get("schema"), list):
        continue
    ditulis = set(kol.get("value") or {}) | set(kol.get("matchingColumns") or []) | {"row_number"}
    sebelum = len(kol["schema"])
    kol["schema"] = [c for c in kol["schema"]
                     if c.get("id") in ditulis or (c.get("id") or "").strip() == c.get("id")]
    kol["schema"] = [c for c in kol["schema"]
                     if c.get("id") in ditulis or not str(c.get("id", "")).startswith("pending_survey")]
    n_skema += sebelum - len(kol["schema"])
log.append(f"{n_skema} entri skema kolom Persada dibuang dari resourceMapper")


# ═════════════════════════════════════════════════════════════════════════════
# Langkah 20-25 ditambahkan 2026-08-16 setelah uji chat live pertama.
# Tiga gejala yang dilaporkan Steven, plus akar yang ditemukan saat menelusurinya.
# ═════════════════════════════════════════════════════════════════════════════

def cari(nama):
    return next((n for n in d["nodes"] if n["name"] == nama), None)


def wajib(nama):
    n = cari(nama)
    if n is None:
        print(f"!! node hilang, tidak bisa lanjut: {nama}"); sys.exit(1)
    return n


def putus(src, target, branch=0):
    """buang satu edge src -> target, sisanya dibiarkan"""
    br = d["connections"].get(src, {}).get("main", [])
    if len(br) > branch and br[branch]:
        br[branch] = [c for c in br[branch] if c["node"] != target]


def sambung(src, targets, branch=0):
    """set ulang isi satu cabang output src"""
    ch = d["connections"].setdefault(src, {}).setdefault("main", [])
    while len(ch) <= branch:
        ch.append([])
    ch[branch] = [{"node": t, "type": "main", "index": 0} for t in targets]


def buang_node(nama):
    d["nodes"][:] = [n for n in d["nodes"] if n["name"] != nama]
    d["connections"].pop(nama, None)
    for ch in d["connections"].values():
        for branches in ch.values():
            for bi, br in enumerate(branches or []):
                if br:
                    branches[bi] = [c for c in br if c["node"] != nama]


def ganti_js(nama, lama, baru, ket):
    n = wajib(nama)
    js = n["parameters"]["jsCode"]
    if lama not in js:
        print(f"!! anchor tidak ditemukan di {nama}: {ket}"); sys.exit(1)
    n["parameters"]["jsCode"] = js.replace(lama, baru, 1)


# ───────────────── 20. kredensial live + preferensi runtime Steven ─────────────────
# Kenapa langkah ini ada: output transform dulu memakai placeholder kredensial kosong,
# jadi tiap regenerate Steven harus memasang ulang kredensial satu per satu di n8n.
# Itulah yang memaksanya mengedit JSON hasil unduhan langsung — dan sejak itu file live
# menyimpang dari skrip ini. Dengan ID asli ditulis di sini, hasil regenerate bisa
# langsung diimpor dan skrip ini kembali jadi satu-satunya sumber kebenaran.
GCRED_LIVE = {"googleSheetsOAuth2Api": {"id": "8TSFDcV58PfhioCB",
                                        "name": "Google Sheets account"}}
ACRED_LIVE = {"anthropicApi": {"id": "DPNnlN1bTbbMf8ks", "name": "Anthropic Personal"}}

# Keputusan Steven 2026-08-16: model balasan tetap Haiku 4.5 demi hemat token.
# (Sonnet 5 ditolak node lmChatAnthropic 1.3 dengan set parameter yang dipakai di sini —
# dugaan terkuat: opsi `thinking`. Kalau nanti mau naik, uji dulu tanpa opsi itu.)
MODEL_REPLY_LIVE = {"__rl": True, "value": "claude-haiku-4-5-20251001",
                    "mode": "list", "cachedResultName": "Claude Haiku 4.5"}

# Node yang SENGAJA dimatikan Steven supaya uji chat pribadi tidak perlu menunggu.
# Ditulis di sini supaya regenerate tidak diam-diam menyalakannya kembali.
# Wait3 = debounce 60 dtk, Wait1 = jeda ketik 5-10 dtk. Nyalakan lagi sebelum live.
SENGAJA_MATI = ["Wait1", "Wait3"]

n_gc = n_ac = 0
for n in d["nodes"]:
    if n["type"] == "n8n-nodes-base.googleSheets":
        n["parameters"].pop("authentication", None)      # OAuth2 = default, bukan serviceAccount
        n["credentials"] = json.loads(json.dumps(GCRED_LIVE))
        n_gc += 1
    if "anthropicApi" in (n.get("credentials") or {}):
        n["credentials"] = json.loads(json.dumps(ACRED_LIVE))
        n_ac += 1
    if n["name"] == "Anthropic Chat Model":
        n["parameters"]["model"] = json.loads(json.dumps(MODEL_REPLY_LIVE))

for nama in SENGAJA_MATI:
    wajib(nama)["disabled"] = True

log.append(f"kredensial live dipasang ({n_gc} node Sheets OAuth2, {n_ac} node Anthropic); "
           f"model balasan {MODEL_REPLY_LIVE['value']}; {len(SENGAJA_MATI)} node Wait tetap mati")


# ───────────────── 21. handover: pasang gerbangnya ─────────────────
# GEJALA: tiap pesan yang masuk menghasilkan notifikasi "PROSPEK MINTA DISAMBUNGKAN"
# ke HP Steven, bahkan untuk sapaan pertama.
#
# AKAR: langkah 1 skrip ini sendiri. Di Persada rantainya
#     Process All -> IF Schedule Survey -> Update STATS Survey -> Collect Handover Context
# Dua node tengah masuk daftar DROP, lalu logika penjembatanan di baris 60-75 menyambung
# Process All langsung ke Collect Handover Context supaya node itu tidak jadi yatim.
# Penjembatanan itu menyelamatkan node-nya, tapi ikut membuang IF yang jadi gerbangnya.
# Process All selalu `return` satu item, jadi handover jalan tanpa syarat.
#
# PERBAIKAN: sambungkan ke gerbang yang memang sudah ada dan sudah benar —
# IF Talk To Admin (tag [TALK_TO_ADMIN]). Prospek yang minta dibuatkan pitch deck
# tidak lewat sini; dia punya jalurnya sendiri (IF Deck Request -> Notify Admin Deck),
# jadi menyambungkan keduanya cuma akan bikin notifikasi ganda.
#
# 'Notify Talk to Admin' dibuang: pesannya cuma nomor + nama + pesan mentah, sementara
# rantai handover menghasilkan ringkasan profil lengkap untuk hal yang sama persis.
putus("Process All", "Collect Handover Context")
sambung("IF Talk To Admin", ["Collect Handover Context"])
sambung("Collect Handover Context", ["Summarize Handover"])
sambung("Summarize Handover", ["Format Handover Message"])
sambung("Format Handover Message", ["Notify Admin Handover"])
# bot_mode -> OFF ikut di ujung rantai: sesuai janji system prompt bahwa setelah
# [TALK_TO_ADMIN] bot berhenti membalas orang itu sampai Steven menyalakannya lagi.
sambung("Notify Admin Handover", ["Update row in sheet", "Log EVENTS Delegated"])
buang_node("Notify Talk to Admin")

for nama in ["Collect Handover Context", "Summarize Handover", "Format Handover Message",
             "Notify Admin Handover", "Log EVENTS Delegated", "Anthropic Chat Model1"]:
    wajib(nama).pop("disabled", None)

# rapikan kanvas: rantai handover pindah ke jalur TALK_TO_ADMIN
ttad = wajib("IF Talk To Admin")["position"]
for i, nama in enumerate(["Collect Handover Context", "Summarize Handover",
                          "Format Handover Message", "Notify Admin Handover"]):
    wajib(nama)["position"] = [ttad[0] + 224 * (i + 1), ttad[1]]
wajib("Anthropic Chat Model1")["position"] = [ttad[0] + 448, ttad[1] + 224]
wajib("Update row in sheet")["position"] = [ttad[0] + 1120, ttad[1]]
wajib("Log EVENTS Delegated")["position"] = [ttad[0] + 1120, ttad[1] + 176]
log.append("handover digerbangi IF Talk To Admin (dulu tersambung langsung ke Process All "
           "tanpa syarat); 'Notify Talk to Admin' dibuang, 6 node handover diaktifkan")


# ───────────────── 22. media: guard file + FAIL LOUD + urutan output ─────────────────
# GEJALA: "ada video demonya?" -> notif "KIRIM MANUAL" ke Steven, tapi ke prospek
# bot tetap menjawab "Aku bisa kirim video demo VIRA" — janji yang tidak pernah ditepati.
#
# Tiga hal berbeda yang menumpuk, diperbaiki satu per satu di bawah.

# (a) URL Google Drive. 'uc?export=download' membalas HTTP 200 berisi HALAMAN HTML
#     konfirmasi virus-scan untuk file di atas ~100 MB. Node Download Media memakai
#     responseFormat "file", jadi HTML itu ditelan sebagai biner tanpa error dan Kirimi
#     menerima file rusak. Bentuk drive.usercontent + confirm=t melewati halaman itu.
ganti_js("Process All",
         "  const resolveRow = (row) => {",
         """  // Drive 'uc?export=download' membalas halaman konfirmasi virus-scan (HTML) untuk
  // file besar, bukan byte filenya. Bentuk usercontent + confirm=t melewati halaman itu.
  const rapikanUrl = (u) => {
    const s = String(u || '').trim();
    const m = s.match(/^https?:\\/\\/(?:drive|docs)\\.google\\.com\\/(?:uc\\?(?:[^#]*&)?id=|file\\/d\\/)([A-Za-z0-9_-]{10,})/);
    return m ? ('https://drive.usercontent.google.com/download?id=' + m[1] + '&export=download&confirm=t') : s;
  };

  const resolveRow = (row) => {""",
         "rapikanUrl disisipkan")
ganti_js("Process All",
         "    mediaUrl = String(row['URL'] || '').trim();",
         "    mediaUrl = rapikanUrl(row['URL']);",
         "mediaUrl lewat rapikanUrl")
ganti_js("Process All",
         "    const url2 = String(row2['URL'] || '').trim();",
         "    const url2 = rapikanUrl(row2['URL']);",
         "mediaUrl2 lewat rapikanUrl")

# (b) Daftar nama link aktif dikumpulkan supaya balasan pengganti bisa menawarkan
#     yang memang ada, bukan sekadar minta maaf.
ganti_js("Process All",
         "let isMediaAmbiguous = false, mediaCandidates = [];",
         "let isMediaAmbiguous = false, mediaCandidates = [], linkAktifNama = [];",
         "deklarasi linkAktifNama")
ganti_js("Process All",
         "  const active = linkRows.filter(r => /^\\s*(aktif|active|on|ya)\\s*$/i.test(String(r['Status'] || '')));",
         """  const active = linkRows.filter(r => /^\\s*(aktif|active|on|ya)\\s*$/i.test(String(r['Status'] || '')));
  linkAktifNama = active.map(r => String(r['Nama Link'] || '').trim()).filter(Boolean);""",
         "isi linkAktifNama")

# (c) FAIL LOUD. Pola yang sama sudah dipakai untuk deckRejected di langkah 13: tag yang
#     ditolak harus MENGUBAH balasan, bukan cuma dibuang. Kalau tidak, prospek menunggu
#     file yang tidak akan datang dan satu-satunya yang tahu cuma Steven.
ganti_js("Process All",
         "return [{\n  json: {\n    ...chatCounter, ...preprocess, ...item.json,",
         """// ── FAIL LOUD: file diminta tapi tidak ada di katalog ──
// Notifikasi ke Steven saja tidak cukup. Selama balasannya masih berbunyi seperti
// janji, prospek menunggu sesuatu yang tidak pernah dikirim.
if (isMediaManual) {
  const low = cleanOutput.toLowerCase();
  const menjanjikan = /\\b(kirim|kirimin|share|bagikan|lampirkan)\\b/.test(low)
                   || /\\b(ini|berikut)\\s+(video|foto|file|dokumen|brosur|deck)/.test(low);
  if (menjanjikan) {
    const alt = linkAktifNama.length
      ? ' Yang sudah siap sekarang: ' + linkAktifNama.join(', ') + '.'
      : '';
    cleanOutput = 'Maaf kak, file itu belum ada di katalogku jadi belum bisa aku kirim '
                + 'langsung. Sudah aku teruskan ke Steven yaa, biar dia yang kirim.' + alt;
    console.warn('Balasan diganti: menjanjikan file yang tidak ada di LINKS. key=' + mediaKey);
  }
}

return [{
  json: {
    ...chatCounter, ...preprocess, ...item.json,""",
         "FAIL LOUD media")

# (d) Urutan cabang keluar Process All. n8n mengeksekusi cabang sesuai urutan array ini,
#     dan sebelumnya notifikasi ke Steven berada di urutan pertama — itu sebabnya di log
#     chat 10:02 notif "KIRIM MANUAL" muncul lebih dulu daripada balasan ke prospek.
URUT = ["Wait1", "IF Media Manual", "IF Unknown", "IF Talk To Admin", "IF Deck Request"]
ada = [c["node"] for c in d["connections"]["Process All"]["main"][0]]
sisa = [x for x in ada if x not in URUT]
sambung("Process All", [x for x in URUT if x in ada] + sisa)

# (e) Guard file untuk kedua rantai kirim media. Download yang gagal atau mengembalikan
#     HTML sekarang jatuh ke notifikasi manual (memakai node yang sudah ada), bukan
#     mengirim file rusak atau mematikan eksekusi.
CEK_FILE_JS = r"""// Guard: pastikan yang terunduh benar-benar file, bukan halaman HTML.
// Drive/Dropbox membalas HTTP 200 + HTML (konfirmasi virus-scan, halaman login) kalau
// link-nya tidak benar-benar direct. responseFormat "file" menelannya sebagai biner
// tanpa error, lalu Kirimi mengirim file rusak — gagal diam-diam.
const it = $input.first();
const bin = (it && it.binary && it.binary.data) ? it.binary.data : null;
const mime = String((bin && bin.mimeType) || '').toLowerCase();
const rusak = !bin || mime.startsWith('text/html') || mime.includes('xhtml');
if (rusak) {
  console.warn('Download media gagal / bukan file. mime=' + (mime || '(tidak ada biner)'));
}
return [{ json: { ...(it.json || {}), file_ok: !rusak, file_mime: mime }, binary: it.binary }];
"""


def if_bool(node_id, nama, field, pos):
    return {"parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "",
                                                      "typeValidation": "loose", "version": 2},
                                          "conditions": [{"id": node_id + "-c",
                                                          "leftValue": "={{ $json.%s }}" % field,
                                                          "rightValue": "",
                                                          "operator": {"type": "boolean",
                                                                       "operation": "true",
                                                                       "singleValue": True}}],
                                          "combinator": "and"},
                           "looseTypeValidation": True, "options": {}},
            "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": pos,
            "id": node_id, "name": nama}


for suffix, unduh, kirim in [("", "Download Media", "Send Media Kirimi"),
                             (" 2", "Download Media 2", "Send Media Kirimi 2")]:
    nu, nk = wajib(unduh), wajib(kirim)
    # 404 / timeout tidak lagi mematikan eksekusi; guard di bawah yang memutuskan
    nu["onError"] = "continueRegularOutput"
    nu["alwaysOutputData"] = True
    px, py = nu["position"]
    cek, gate = "Cek File Media" + suffix, "IF File Media OK" + suffix
    d["nodes"].extend([
        {"parameters": {"jsCode": CEK_FILE_JS}, "type": "n8n-nodes-base.code",
         "typeVersion": 2, "position": [px + 112, py + 176],
         "id": "media-cek" + suffix.strip().rjust(1, "1"), "name": cek},
        if_bool("media-gate" + suffix.strip().rjust(1, "1"), gate, "file_ok",
                [px + 112, py + 352]),
    ])
    nk["position"] = [px + 336, py]
    sambung(unduh, [cek])
    sambung(gate, [kirim], branch=0)
    sambung(gate, ["Format Media Notif"], branch=1)
    sambung(cek, [gate])

# (f) Notif manual kini punya dua sebab yang sangat berbeda: file memang tidak ada di
#     katalog, atau file ADA tapi gagal diunduh. Tanpa dibedakan, Steven tidak tahu
#     apakah yang perlu dia perbaiki itu isi sheet atau link-nya.
ganti_js("Format Media Notif",
         "// FORMAT MEDIA NOTIF — notifikasi manual ke tim telemarketer (Aar & Aqsa).\n"
         "// Dipakai saat user minta gambar/video/brosur TAPI file belum ada di katalog\n"
         "// LINKS (native send tak bisa). Tim kirim file-nya manual ke user.\n"
         "// Mengembalikan 1 item per nomor tim (loop kirim di Notify Media Team).",
         "// FORMAT MEDIA NOTIF — notifikasi manual ke Steven.\n"
         "// Dua jalur masuk ke sini: (1) key tidak ada di katalog LINKS, (2) key ada\n"
         "// tapi unduhannya gagal / bukan file. Keduanya dibedakan di baris 'Sebab'\n"
         "// supaya jelas yang perlu dibetulkan isi sheet-nya atau link-nya.",
         "Format Media Notif: komentar Persada")
ganti_js("Format Media Notif",
         "const summary = pa.mediaRequestSummary || '';",
         """const summary = pa.mediaRequestSummary || '';
const urlKatalog = String(pa.mediaUrl || '').trim();
const sebab = urlKatalog
  ? ('file ADA di katalog tapi gagal diunduh -> ' + urlKatalog)
  : 'key tidak ada di katalog LINKS (atau statusnya belum Aktif)';""",
         "Format Media Notif: deklarasi sebab")
ganti_js("Format Media Notif",
         "Detail: ${summary || '(tidak ada detail)'}",
         "Detail: ${summary || '(tidak ada detail)'}\nSebab: ${sebab}",
         "Format Media Notif: baris Sebab")
log.append("media: URL Drive dinormalkan, FAIL LOUD saat file tidak ada di katalog, "
           "balasan prospek didahulukan sebelum notif, guard HTML/unduhan gagal di 2 rantai kirim")


# ───────────────── 23. cache katalog: 4 pembacaan Sheets per pesan -> 0 ─────────────────
# GEJALA: kena batas kuota Google 60 detik di klien lain saat trafik naik.
#
# HITUNGAN: satu pesan yang dibalas memakai 14 read + 5 write (appendOrUpdate/update
# masing-masing = 1 read lookup + 1 write). Kuota Google 60 read/menit PER USER per
# project — dibagi bersama semua workflow di akun yang sama. Artinya ~4 pesan/menit.
#
# Empat tab ini (FAQ, PROGRAM, LINKS, ABOUT_STEVEN) isinya nyaris statis tapi dibaca
# ulang setiap pesan. Sekarang disimpan di static data workflow dengan TTL.
# CONFIG.katalog_cache_minutes mengatur umurnya (default 10); isi 0 untuk mematikan.
# Read CONFIG SENGAJA tidak ikut di-cache — di situ nanti kill switch global dibaca,
# dan perubahannya harus langsung terasa.
MUAT_KATALOG_JS = r"""// Cache katalog: FAQ + PROGRAM + LINKS + ABOUT_STEVEN.
// Empat tab nyaris statis yang dulu dibaca ulang tiap pesan = 4 dari 14 request Sheets
// per giliran. Kuota Google 60 read/menit per user per project, dipakai bareng semua
// workflow di akun yang sama, jadi ini rem yang paling terasa.
// CONFIG.katalog_cache_minutes mengatur umur cache; isi 0 untuk mematikan.
const cfg = (() => { try { return $('Parse Config').first().json.config || {}; } catch (e) { return {}; } })();
const menit = parseInt(cfg.katalog_cache_minutes ?? '10', 10);
const TTL = (isNaN(menit) ? 10 : menit) * 60000;

const sd = $getWorkflowStaticData('global');
const k = sd.katalog;
const umur = (k && k.ts) ? (Date.now() - k.ts) : Infinity;
const segar = TTL > 0 && !!k && Array.isArray(k.faq) && umur < TTL;

console.log('katalog cache: ' + (segar ? 'HIT (umur ' + Math.round(umur / 1000) + ' dtk)' : 'MISS'));
return [{ json: { ...$input.first().json, katalog_segar: segar } }];
"""

SIMPAN_KATALOG_JS = r"""// Simpan hasil 4 pembacaan tadi ke static data, lalu bawa juga sebagai field
// supaya node hilir tidak perlu memanggil $('Read ...') — node itu tidak jalan
// saat cache HIT, dan pemanggilannya akan mengembalikan kosong tanpa error.
const ambil = (nm) => { try { return $(nm).all().map(i => i.json).filter(Boolean); } catch (e) { return []; } };
const katalog = {
  ts: Date.now(),
  faq:     ambil('Read FAQ'),
  program: ambil('Read PROGRAM Data'),
  links:   ambil('Read LINKS Data'),
  about:   ambil('Read ABOUT_STEVEN'),
};
const sd = $getWorkflowStaticData('global');
sd.katalog = katalog;
console.log(`katalog disimpan: faq=${katalog.faq.length} program=${katalog.program.length} links=${katalog.links.length} about=${katalog.about.length}`);
return [{ json: { ...$('Muat Katalog').first().json, katalog } }];
"""

AMBIL_KATALOG_JS = r"""// Cache masih segar: pakai isi static data, tidak menyentuh Google sama sekali.
const sd = $getWorkflowStaticData('global');
const k = sd.katalog || {};
const katalog = {
  ts: k.ts || 0,
  faq: k.faq || [], program: k.program || [], links: k.links || [], about: k.about || [],
};
return [{ json: { ...$input.first().json, katalog } }];
"""

pre_pos = wajib("Preprocess - Context Detection")["position"]
d["nodes"].extend([
    {"parameters": {"jsCode": MUAT_KATALOG_JS}, "type": "n8n-nodes-base.code",
     "typeVersion": 2, "position": [pre_pos[0] + 112, pre_pos[1]],
     "id": "katalog-muat-01", "name": "Muat Katalog"},
    # true = katalog BASI -> baca sheet. false = masih segar -> ambil dari cache.
    {"parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "",
                                               "typeValidation": "loose", "version": 2},
                                   "conditions": [{"id": "katalog-basi-c",
                                                   "leftValue": "={{ $json.katalog_segar }}",
                                                   "rightValue": "",
                                                   "operator": {"type": "boolean",
                                                                "operation": "false",
                                                                "singleValue": True}}],
                                   "combinator": "and"},
                    "looseTypeValidation": True, "options": {}},
     "type": "n8n-nodes-base.if", "typeVersion": 2.2,
     "position": [pre_pos[0] + 224, pre_pos[1]],
     "id": "katalog-basi-01", "name": "IF Katalog Basi"},
    {"parameters": {"jsCode": SIMPAN_KATALOG_JS}, "type": "n8n-nodes-base.code",
     "typeVersion": 2, "position": [pre_pos[0] + 1120, pre_pos[1] + 160],
     "id": "katalog-simpan-01", "name": "Simpan Katalog"},
    {"parameters": {"jsCode": AMBIL_KATALOG_JS}, "type": "n8n-nodes-base.code",
     "typeVersion": 2, "position": [pre_pos[0] + 448, pre_pos[1] - 160],
     "id": "katalog-ambil-01", "name": "Ambil Katalog"},
])
for i, nama in enumerate(["Read FAQ", "Read PROGRAM Data", "Read LINKS Data", "Read ABOUT_STEVEN"]):
    wajib(nama)["position"] = [pre_pos[0] + 448 + 168 * i, pre_pos[1] + 160]

sambung("Preprocess - Context Detection", ["Muat Katalog"])
sambung("Muat Katalog", ["IF Katalog Basi"])
sambung("IF Katalog Basi", ["Read FAQ"], branch=0)
sambung("IF Katalog Basi", ["Ambil Katalog"], branch=1)
sambung("Read ABOUT_STEVEN", ["Simpan Katalog"])
sambung("Simpan Katalog", ["FAQ Retrieve"])
sambung("Ambil Katalog", ["FAQ Retrieve"])

# FAQ Retrieve ditulis ulang. Selain pindah ke katalog cache, isinya memang masih
# Persada seluruhnya: dia memanggil $('Read PRODUK Data') — node yang sudah direname
# jadi 'Read PROGRAM Data' di langkah 2, jadi blok itu SELALU kosong. Hasilnya
# `data_context` yang tidak pernah dipakai siapa pun (Rakit Konteks membangun
# program_context & links_context sendiri). Kelompok sinonim & boost kategorinya juga
# masih KPR/unit/survey/legalitas — tidak cocok dengan kategori FAQ VIRA Steven.
FAQ_RETRIEVE_JS = r"""// ===== FAQ RETRIEVE — VIRA Steven =====
// Pencarian FAQ leksikal (TF-IDF sederhana + sinonim domain).
// Sumber datanya `katalog` dari cache, bukan $('Read FAQ') langsung: saat cache HIT
// node Sheets-nya tidak dijalankan sama sekali.
// Blok `data_context` warisan Persada dibuang — isinya dibangun dari $('Read PRODUK Data')
// yang sudah tidak ada sejak node itu direname, jadi selalu kosong, dan tidak ada satu
// node pun yang membacanya (Rakit Konteks menyusun program_context & links_context sendiri).
try {
  const inp = $input.first().json;
  const pre = $('Preprocess - Context Detection').first().json;
  const query = pre.actualUserMessage || '';
  const katalog = inp.katalog || { faq: [] };

  const STOP = new Set(['yang','untuk','dan','di','ke','dari','itu','ini','apa','apakah','bisa','kah','ya','yaa','kak','min','dong','sih','kok','aja','ada','gimana','bagaimana','saya','aku','nya','kalau','atau','juga','sudah','belum','mau','dengan','pada','adalah','tolong','mohon','halo','hai','permisi','terima','kasih','sama','buat','soal','tentang','nih','ga','gak','engga','tidak','dll','yg','utk','kamu','kita','gitu','banget','emang','memang']);

  // Kelompok sinonim domain VIRA Steven (jasa AI customer service), bukan properti.
  // Kata pertama tiap grup jadi wakilnya.
  const GROUPS = [
    ['harga','biaya','tarif','bayar','paket','basic','premium','langganan','bulanan','mahal','murah','budget','nego','setup','token','kontrak','berhenti'],
    ['fitur','kemampuan','fungsi','follow','followup','laporan','analitik','invoice','jadwal','multibahasa','inggris','mandarin'],
    ['media','foto','gambar','video','brosur','katalog','file','dokumen','demo','contoh','bukti','portfolio','tangkapan'],
    ['aman','keamanan','privasi','bocor','rahasia','akses','data'],
    ['proses','lama','durasi','waktu','golive','mulai','siapkan','persiapan','maintenance'],
    ['deck','pitch','proposal','penawaran','presentasi'],
    ['steven','klien','pengalaman','siapa','background','qa'],
    ['whatsapp','wa','nomor','device','aplikasi','install','internet','server','sheets','spreadsheet'],
    ['error','gangguan','down','mati','rusak','gagal','ramai','lonjakan','kuat'],
    ['bot','ai','robot','manusia','admin','chatbot','template','persona','gaya'],
  ];
  const SYN = {}; for (const g of GROUPS) for (const w of g) SYN[w] = g[0];

  const stem = (t) => { let w = t; for (const s of ['nya','kah','lah','kan','an','i']) if (w.length - s.length >= 4 && w.endsWith(s)) { w = w.slice(0, -s.length); break; } for (const p of ['meng','meny','mem','men','peng','peny','pem','pen','ber','ter','di','se','ke','me','pe']) if (w.length - p.length >= 4 && w.startsWith(p)) { w = w.slice(p.length); break; } return w; };
  const tok = (s) => (s || '').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, ' ').split(/\s+/).filter(Boolean).filter(t => !STOP.has(t)).map(t => { const a = SYN[t]; if (a) return a; const st = stem(t); return SYN[st] || st; }).filter(t => t.length >= 2 && !STOP.has(t));

  const faq = (katalog.faq || []).filter(r => r && r.Pertanyaan && r.Jawaban
    && /^\s*(aktif|active|on|ya)\s*$/i.test(String(r.Status || 'Aktif')));
  const docs = faq.map(r => ({ row: r, toks: tok(r.Pertanyaan) }));
  const Nn = docs.length, df = {};
  for (const dd of docs) for (const t of new Set(dd.toks)) df[t] = (df[t] || 0) + 1;
  const idf = (t) => Math.log((Nn + 1) / ((df[t] || 0) + 1)) + 1;

  // Boost mengikuti nama Kategori yang benar-benar ada di tab FAQ VIRA Steven.
  const boost = {};
  if (pre.askingPrice) boost['Harga'] = 1.25;
  if (pre.wantsMedia)  boost['Fitur'] = 1.15;

  const qToks = [...new Set(tok(query))];
  let faq_context = '';
  if (qToks.length && docs.length) {
    const scored = docs.map(dd => {
      const dset = new Set(dd.toks);
      let s = 0, m = 0;
      for (const t of qToks) if (dset.has(t)) { s += idf(t); m++; }
      s *= (boost[dd.row.Kategori] || 1.0);
      return { row: dd.row, score: s, matched: m };
    }).sort((a, b) => b.score - a.score);
    const top = scored[0];
    const FLOOR = 2.5, needCov = qToks.length >= 3 ? 2 : 1;
    if (top.score >= FLOOR && top.matched >= needCov) {
      const kept = scored.filter(x => x.score >= 0.45 * top.score && x.matched >= 1).slice(0, 4);
      faq_context = kept.map(x => `Q: ${x.row.Pertanyaan}\nA: ${x.row.Jawaban}`).join('\n\n');
    }
  }

  return [{ json: { ...pre, katalog, faq_context }, pairedItem: { item: 0 } }];
} catch (e) {
  const pre = ($('Preprocess - Context Detection').first() || { json: {} }).json || {};
  const katalog = ($input.first().json || {}).katalog || { faq: [], program: [], links: [], about: [] };
  return [{ json: { ...pre, katalog, faq_context: '', faq_error: String(e) }, pairedItem: { item: 0 } }];
}
"""
wajib("FAQ Retrieve")["parameters"]["jsCode"] = FAQ_RETRIEVE_JS

# Rakit Konteks & Process All: sumber baris sheet pindah dari $('Read ...') ke katalog.
ganti_js("Rakit Konteks",
         """const rows = (nodeName) => {
  try { return $(nodeName).all().map(r => r.json).filter(Boolean); }
  catch (e) { return []; }               // node tidak ada / belum jalan -> jangan gagalkan giliran
};""",
         """// Baris sheet datang dari katalog cache (lihat node 'Muat Katalog'), bukan dari
// $('Read ...') langsung — saat cache HIT node Sheets-nya memang tidak dijalankan.
const KATALOG = item.katalog || { faq: [], program: [], links: [], about: [] };
const rows = (kunci) => (Array.isArray(KATALOG[kunci]) ? KATALOG[kunci] : []);""",
         "Rakit Konteks: rows() -> katalog")
for lama, baru in [("rows('Read ABOUT_STEVEN')", "rows('about')"),
                   ("rows('Read PROGRAM Data')", "rows('program')"),
                   ("rows('Read LINKS Data')", "rows('links')")]:
    ganti_js("Rakit Konteks", lama, baru, f"Rakit Konteks: {lama}")

for lama, baru in [
    ("  try { linkRows = $('Read LINKS Data').all().map(i => i.json); } catch (e) {}",
     "  try { linkRows = $('Rakit Konteks').first().json.katalog.links || []; } catch (e) {}"),
    ("  try { linkRows2 = $('Read LINKS Data').all().map(i => i.json); } catch (e) {}",
     "  try { linkRows2 = $('Rakit Konteks').first().json.katalog.links || []; } catch (e) {}"),
]:
    ganti_js("Process All", lama, baru, "Process All: LINKS -> katalog")

log.append("cache katalog: 4 node Sheets (FAQ/PROGRAM/LINKS/ABOUT_STEVEN) di balik TTL static data; "
           "FAQ Retrieve ditulis ulang (blok data_context Persada yang selalu kosong dibuang, "
           "sinonim & boost diarahkan ke domain VIRA Steven)")


# ───────────────── 24. buang 2 pembacaan STATS yang mubazir ─────────────────
# 'Read STATS for HITL' membaca ULANG seluruh tab STATS ~2 detik setelah 'Read User STATS'
# membacanya, untuk memeriksa bot_mode yang sudah diperiksa 'IF Bot Mode Active'.
# Pemeriksaan ulang yang benar-benar berarti terjadi setelah debounce, di
# 'Re-Read STATS Debounce' — dan node itu tetap ada.
#
# 'Read STATS' pasca-AI membaca seluruh tab lagi hanya untuk mencari baris user yang
# sudah dibawa 'Resolve User Row' sebagai userRow sejak awal giliran.
sambung("Update Buffer", ["HITL Check"])
buang_node("Read STATS for HITL")
wajib("HITL Check")["parameters"]["jsCode"] = r"""// ============================================================
// HUMAN-IN-THE-LOOP CHECK — bot_mode 'OFF' = admin pegang manual, bot berhenti.
// Sumbernya Resolve User Row, bukan pembacaan STATS tersendiri: node lama
// 'Read STATS for HITL' membaca ulang seluruh tab ~2 detik setelah
// 'Read User STATS', untuk nilai yang tidak berubah di antara keduanya.
// Pemeriksaan ulang yang berarti tetap ada, setelah debounce, di
// 'Re-Read STATS Debounce'.
// ============================================================
const r = $('Resolve User Row').first().json;
const botMode = String(r.bot_mode || '').trim().toUpperCase();

if (botMode === 'OFF') {
  console.log('👨‍💼 HITL AKTIF — admin sedang handle manual, bot berhenti.');
  return [];
}

console.log(`🤖 Bot mode AKTIF (bot_mode="${botMode}") — lanjut.`);
return [$input.first()];
"""

sambung("Extract & Prepare Data", ["Process Counter & Merge Data"])
buang_node("Read STATS")
wajib("Process Counter & Merge Data")["parameters"]["jsCode"] = r"""// ====================================================================
// PROCESS COUNTER & MERGE DATA — VIRA Steven
// Baris STATS lama diambil dari Resolve User Row (userRow), bukan dari
// pembacaan ulang seluruh tab. Node 'Read STATS' dibuang: barisnya sudah
// dibawa sejak awal giliran, dan satu-satunya penulis STATS di antara
// keduanya (Update Buffer) tidak menyentuh Counter.
// Dipertahankan dari V4: No WA primer / lid backup, 'Tanggal Chat Pertama'
// dibaca dari kolom yang benar, error -> stop (bukan menulis baris "ERROR").
// ====================================================================
try {
    const chatCounter = $('Chat Counter').first().json;
    const resolve = $('Resolve User Row').first().json;
    const resolvedKey = resolve.resolved_key;

    if (!resolvedKey) {
        console.warn('resolved_key kosong - skip update STATS');
        return [];
    }

    const digits = v => String(v ?? '').replace(/\D/g, '');
    const userName = chatCounter.user_name || 'User';
    const userMessage = chatCounter.stats_message || chatCounter.original_message || '';
    const lid = digits(chatCounter.user_lid);

    const row = resolve.userRow || {};
    const existingRow = Object.keys(row).length ? row : null;
    console.log('Baris STATS: ' + (existingRow ? 'SUDAH ADA' : 'USER BARU'));

    let counter, pesanPertama, tanggalPertama, intensitasChat;
    if (existingRow) {
        counter = parseInt(existingRow.Counter || existingRow.counter || 0) + 1;
        intensitasChat = parseInt(existingRow['Intensitas Chat'] || existingRow.intensitas_chat || 0) + 1;
        const pesanLama = existingRow['Pesan Pertama'] || existingRow.pesan_pertama;
        pesanPertama = (pesanLama && String(pesanLama).trim() !== '') ? pesanLama : userMessage;
        const tglLama = existingRow['Tanggal Chat Pertama'];
        tanggalPertama = (tglLama && String(tglLama).trim() !== '') ? tglLama : null;
    } else {
        counter = 1;
        intensitasChat = 1;
        pesanPertama = userMessage;
        tanggalPertama = null;
    }

    const hariIni = () => new Date().toLocaleDateString('en-GB', {
        timeZone: 'Asia/Jakarta', day: '2-digit', month: '2-digit', year: 'numeric'
    });
    if (!tanggalPertama) tanggalPertama = hariIni();

    return [{ json: {
        'No WA': resolvedKey,
        'lid': lid,
        'Tanggal': tanggalPertama,
        'TanggalSekarang': hariIni(),
        'Nama': userName,
        'Pesan Pertama': pesanPertama,
        'Counter': counter,
        'Intensitas Chat': intensitasChat
    }}];

} catch (error) {
    // jangan menulis baris "ERROR" ke sheet - cukup log & stop.
    console.error('Process Counter ERROR: ' + error.message);
    return [];
}
"""
log.append("buang 'Read STATS for HITL' & 'Read STATS' (2 pembacaan penuh tab STATS per pesan); "
           "HITL Check & Process Counter dialihkan ke Resolve User Row")


# ───────────────── 25. retry seragam di semua node Sheets ─────────────────
# Saat kuota Google terlampaui jawabannya HTTP 429 dan jendelanya 60 detik.
# waitBetweenTries 2000 ms x 3 percobaan = 6 detik, masih di dalam jendela yang sama —
# retry-nya habis sebelum kuotanya pulih. 'Read MSG_BUFFER' malah tidak punya retry
# sama sekali, jadi satu 429 di situ mematikan seluruh eksekusi.
n_retry = 0
for n in d["nodes"]:
    if n["type"] == "n8n-nodes-base.googleSheets":
        n["retryOnFail"] = True
        n["maxTries"] = 4
        n["waitBetweenTries"] = 5000
        n_retry += 1
log.append(f"{n_retry} node Sheets: retryOnFail 4x jeda 5 dtk (menjangkau lewat jendela kuota 60 dtk)")


# ───────────────── simpan + validasi struktur ─────────────────
json.dump(d, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

names = {n["name"] for n in d["nodes"]}
dangling = sorted({c["node"] for ch in d["connections"].values()
                   for br in ch.values() for b in (br or []) for c in (b or [])
                   if c["node"] not in names})
punya_masuk = {c["node"] for ch in d["connections"].values()
               for br in ch.values() for b in (br or []) for c in (b or [])}
yatim = sorted(n["name"] for n in d["nodes"]
               if n["name"] not in punya_masuk
               and n["name"] not in d["connections"]
               and not n["type"].endswith("stickyNote"))

print("=== LANGKAH TRANSFORMASI ===")
for l in log:
    print("  -", l)
print()
print("=== HASIL ===")
print(f"  node       : {len(d['nodes'])}")
print(f"  menggantung: {dangling or 'tidak ada'}")
print(f"  yatim      : {yatim or 'tidak ada'}")
print(f"  file       : {OUT}")
