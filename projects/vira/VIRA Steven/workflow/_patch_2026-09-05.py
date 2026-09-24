# -*- coding: utf-8 -*-
"""
_patch_2026-09-05.py — Paket "SIAP IKLAN" untuk VIRA Personal Main.

Masukan : 2026-09-04-VIRA-Personal-Main-patched-v2.json   (tidak diubah)
Keluaran: 2026-09-05-VIRA-Personal-Main-v3.json           (file baru)
          2026-09-05-system-prompt-VIRA-Personal-v3.md    (salinan system message)

Latar: nomor ini dipakai untuk iklan mulai 2026-09-06. Audit 89 node menemukan
13 cacat; tiga di antaranya membuat kampanye iklan gagal total atau kehilangan lead.

P0-1  IF (Whitelist) mengunci bot ke 2 nomor. Semua prospek iklan akan di-drop diam-diam.
P0-2  Teks yang DIKIRIM ke prospek bisa berbeda dari teks yang DISIMPAN Simple Memory
      (override di Process All). Model lalu menyangkal pernah bertanya dan bertanya ulang.
      Insiden 2026-09-05 12:14-14:45 seluruhnya dijelaskan oleh ini.
P0-3  `rapikanUrl` dideklarasikan di dalam blok if tapi dipakai di luar -> ReferenceError
      saat AI mengirim dua tag SEND_MEDIA. Prospek tidak menerima balasan sama sekali.
P1-4  Persetujuan pendek ("boleh", "mau", "oke") tidak dikenali sebagai permintaan deck
      -> brief tersimpan tapi Steven TIDAK PERNAH dinotifikasi.
P1-5  Preprocess masih memakai regex domain properti. "senin"/"besok"/"jam 10"
      menyuntikkan dorongan [TALK_TO_ADMIN] -> bot mematikan dirinya untuk lead itu.
P1-6  [TALK_TO_ADMIN] selalu mematikan bot, walau prospek tidak memintanya.
P1-7  Blocklist Gate membaca item.from (selalu undefined) -> blocklist & anti-loop mati.
P1-8  maxTokens 1024 memotong output: blok DECK_REQUEST 33 baris + [FACTS] di paling
      akhir. Fakta yang terpotong tidak pernah tersimpan -> bot bertanya ulang.
P2-9  Rate limiter hardcode 5/menit; pesan ke-6 hilang permanen (dibuang sebelum buffer).
P2-10 Detect Lead Source memakai includes('ig') -> "tinggi"/"bagi" terbaca Instagram.
P2-11 IS_NEW_USER dihitung dua cara berbeda di satu prompt yang sama.
P2-12 If From Group / IF From Me typeValidation strict -> payload tanpa field = error.
P2-13 Parse Config default vision_model 'claude-haiku-4-5' dikirim ke api.deepseek.com.

Permintaan Steven 2026-09-05: model chat = deepseek-v4-pro, model ringkasan = deepseek-v4-flash.

Jalankan: python _patch_2026-09-05.py   (lalu python _qa_2026-09-05.py)
"""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-04-VIRA-Personal-Main-patched-v2.json")
DST = os.path.join(DIR, "2026-09-05-VIRA-Personal-Main-v3.json")
PROMPT_OUT = os.path.join(DIR, "2026-09-05-system-prompt-VIRA-Personal-v3.md")

with open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

nodes = {n["name"]: n for n in wf["nodes"]}
conns = wf["connections"]
jejak = []


def ganti(teks, lama, baru, label):
    """Ganti sekali. Gagal keras kalau pola tidak ketemu atau ambigu."""
    n = teks.count(lama)
    if n != 1:
        raise SystemExit("GAGAL [%s]: pola ditemukan %d kali (harus tepat 1)." % (label, n))
    jejak.append(label)
    return teks.replace(lama, baru)


def kode(nama):
    return nodes[nama]["parameters"]["jsCode"]


def set_kode(nama, isi, label):
    nodes[nama]["parameters"]["jsCode"] = isi
    jejak.append(label)


def sidik(nama, potongan, label):
    """Pastikan node sumber memang versi yang diharapkan sebelum ditimpa utuh."""
    if potongan not in kode(nama):
        raise SystemExit("GAGAL [%s]: sidik jari tidak cocok di node '%s'." % (label, nama))


# ====================================================================
# P0-1 — Gerbang whitelist hardcoded dilepas dari jalur
# ====================================================================
# `IF (Whitelist)` hanya meloloskan 6285171701168 dan 6281510624599. Node itu
# dipakai saat masa uji coba dan tidak pernah dilepas. Untuk nomor iklan, node
# ini berarti 100% prospek baru dibuang tanpa jejak.
# Nodenya TIDAK dihapus (Steven mungkin ingin memakainya lagi), tapi dilepas dari
# jalur dan dinonaktifkan. Fungsinya digantikan `Blocklist Gate` berbasis CONFIG.
if conns.get("IF From Me", {}).get("main", [[]])[0][0]["node"] != "IF (Whitelist)":
    raise SystemExit("GAGAL [P0-1]: kabel 'IF From Me' tidak seperti yang diharapkan.")
conns["IF From Me"]["main"][0] = [{"node": "Bootstrap Config", "type": "main", "index": 0}]
conns.pop("IF (Whitelist)", None)
nodes["IF (Whitelist)"]["disabled"] = True
jejak.append("P0-1 IF (Whitelist) dilepas dari jalur + disabled")


# ====================================================================
# P2-12 — Gerbang grup / pesan sendiri tahan payload tanpa field
# ====================================================================
# typeValidation 'strict' + boolean equals false: kalau Kirimi tidak mengirim
# field isFromGroup/isFromMe (payload versi lain, event baru), n8n melempar error
# dan prospek tidak dibalas. `=== true` mengubah undefined jadi false lebih dulu.
for _nm, _field in (("If From Group", "isFromGroup"), ("IF From Me", "isFromMe")):
    _cond = nodes[_nm]["parameters"]["conditions"]
    if _cond["conditions"][0]["leftValue"] != "={{ $json.body.%s }}" % _field:
        raise SystemExit("GAGAL [P2-12]: kondisi '%s' tidak seperti yang diharapkan." % _nm)
    _cond["conditions"][0]["leftValue"] = "={{ $json.body.%s === true }}" % _field
    _cond["options"]["typeValidation"] = "loose"
    nodes[_nm]["parameters"]["looseTypeValidation"] = True
jejak.append("P2-12 If From Group & IF From Me tahan field hilang")


# ====================================================================
# P1-7 — Blocklist Gate dibetulkan & diberi whitelist berbasis CONFIG
# ====================================================================
sidik("Blocklist Gate", "const from = digits(item.from || item.no_wa || '');", "P1-7")
set_kode("Blocklist Gate", r"""// Blocklist Gate - VIRA Steven (v3, 2026-09-05)
// Bot ini PUBLIK: defaultnya semua orang boleh masuk.
//
// Perbaikan 2026-09-05:
// (1) Node ini menerima item dari Parse Config, yang isinya hasil spread payload
//     webhook - nomor pengirim ada di `body.from`, BUKAN di `from` tingkat atas.
//     Versi lama membaca item.from (selalu undefined), jadi blocklist dan proteksi
//     anti-loop TIDAK PERNAH aktif satu kali pun.
// (2) Gerbang uji coba pindah ke sini dari node `IF (Whitelist)` yang mengunci bot
//     ke dua nomor. Sekarang dikendalikan CONFIG, bukan ditanam di kabel:
//       whitelist_enabled = false (default) -> semua orang masuk  = MODE IKLAN
//       whitelist_enabled = true            -> hanya whitelist_numbers = MODE UJI
const cfg  = $('Parse Config').first().json.config || {};
const item = $input.first().json || {};
const body = item.body || {};

const digits = (s) => String(s || '').replace(/\D/g, '');
const from = digits(body.from ?? item.from ?? item.no_wa ?? '');
const lid  = digits(body.originLid ?? item.originLid ?? item.lid ?? '');
const cocok = (daftar) => daftar.length > 0
  && ((from && daftar.includes(from)) || (lid && daftar.includes(lid)));

// 1) jangan pernah membalas diri sendiri (bisa memicu loop tak berujung)
const botNumber = digits(cfg.bot_wa_number || '');
if (cfg.ignore_self_number !== false && botNumber && (from === botNumber || lid === botNumber)) {
  console.log('STOP: pesan dari nomor bot sendiri.');
  return [];
}

// 2) blocklist manual dari CONFIG
if (cocok((cfg.blocklist_numbers || []).map(digits).filter(Boolean))) {
  console.log('STOP: nomor ada di blocklist. from=' + from + ' lid=' + lid);
  return [];
}

// 3) whitelist OPSIONAL - hanya aktif kalau CONFIG.whitelist_enabled = true.
//    Whitelist yang aktif tapi kosong TIDAK mematikan bot: itu kegagalan yang
//    paling mahal (semua prospek diam-diam dibuang), jadi sengaja diabaikan.
if (cfg.whitelist_enabled === true) {
  const putih = (cfg.whitelist_numbers || []).map(digits).filter(Boolean);
  if (!putih.length) {
    console.warn('whitelist_enabled=true tapi whitelist_numbers kosong - gerbang diabaikan.');
  } else if (!cocok(putih)) {
    console.log('STOP: whitelist aktif, nomor tidak terdaftar. from=' + from + ' lid=' + lid);
    return [];
  }
}

return $input.all();""", "P1-7 Blocklist Gate baca body.from + whitelist CONFIG")


# ====================================================================
# P1-7b + P2-13 — kunci CONFIG yang dibaca Blocklist Gate, dan model vision
# ====================================================================
_c = kode("Parse Config")
_c = ganti(_c,
  "  whitelist_enabled: bool('whitelist_enabled', false),",
  "  whitelist_enabled: bool('whitelist_enabled', false),\n"
  "  // Dibaca Blocklist Gate. Sebelum 2026-09-05 tiga kunci ini tidak pernah\n"
  "  // dirakit di sini, jadi blocklist & proteksi anti-loop selalu kosong.\n"
  "  blocklist_numbers: jsonArr('blocklist_numbers').map(x => String(x).replace(/\\D/g,'')).filter(Boolean),\n"
  "  bot_wa_number: str('bot_wa_number', '').replace(/\\D/g, ''),\n"
  "  ignore_self_number: bool('ignore_self_number', true),",
  "P1-7b kunci blocklist di Parse Config")
_c = ganti(_c,
  "  vision_model: str('vision_model', 'claude-haiku-4-5'),",
  "  // Default harus sama dengan fallback di `Siapkan Vision Request`. Sebelumnya\n"
  "  // 'claude-haiku-4-5' dikirim ke api.deepseek.com dan selalu ditolak 400,\n"
  "  // jadi setiap gambar berakhir di cabang 'sistem gagal membaca'.\n"
  "  vision_model: str('vision_model', 'deepseek-v4-flash-vision-exp'),",
  "P2-13 default vision_model diselaraskan")
nodes["Parse Config"]["parameters"]["jsCode"] = _c


# ====================================================================
# P2-9 — Rate limiter mengikuti CONFIG, batas dinaikkan
# ====================================================================
sidik("Rate Limiter LID", "const maxMessages = 5;", "P2-9")
set_kode("Rate Limiter LID", r"""// Rate Limiter - cegah spam, TAPI jangan menelan pesan prospek sungguhan.
// Node ini berdiri SEBELUM Append MSG_BUFFER: pesan yang ditolak di sini hilang
// permanen, tidak ikut debounce, tidak pernah dibaca AI. Batas lama (5/menit,
// hardcode) terlalu ketat untuk prospek iklan yang mengetik beruntun - pesan
// ke-6 lenyap tanpa jejak. Sekarang mengikuti CONFIG, default 15/menit.
const cfg = (() => { try { return $('Parse Config').first().json.config || {}; } catch (e) { return {}; } })();
const userWa = $('Resolve User Row').first().json.resolved_key;
const now = Date.now();

const maxMessages = Math.max(1, Number(cfg.rate_limit_max) || 15);
const windowMs    = Math.max(1000, (Number(cfg.rate_limit_window_sec) || 60) * 1000);

const staticData = $getWorkflowStaticData('global');
const rateLimits = staticData.rateLimits || {};
const userKey = 'rl_' + userWa;

if (!rateLimits[userKey] || (now - rateLimits[userKey].windowStart) > windowMs) {
  rateLimits[userKey] = { count: 1, windowStart: now };
} else {
  rateLimits[userKey].count++;
}

// Buang entri basi supaya static data tidak tumbuh tanpa batas seumur workflow.
for (const k of Object.keys(rateLimits)) {
  if ((now - rateLimits[k].windowStart) > windowMs * 60) delete rateLimits[k];
}
staticData.rateLimits = rateLimits;

if (rateLimits[userKey].count > maxMessages) {
  console.log('RATE LIMITED: ' + userWa + ' sudah ' + rateLimits[userKey].count
              + ' pesan dalam ' + (windowMs / 1000) + ' dtk');
  return [];
}

console.log('RATE OK: ' + userWa + ' pesan ke-' + rateLimits[userKey].count + '/' + maxMessages);
return [$input.first()];""", "P2-9 rate limiter dari CONFIG, default 15/menit")


# ====================================================================
# P2-9b — Chat Counter: $vars tidak boleh menjatuhkan seluruh alur
# ====================================================================
_c = kode("Chat Counter")
_c = ganti(_c,
  "// Counter sederhana\nlet counter = $vars.chatCounter || 0;\ncounter++;\n$vars.chatCounter = counter;",
  "// Counter sederhana. $vars adalah fitur berbayar n8n dan read-only di sebagian\n"
  "// instance; kalau tidak ada, akses langsung melempar TypeError dan SELURUH alur\n"
  "// mati di node paling awal. Angkanya cuma dipakai untuk log, jadi tidak layak\n"
  "// jadi titik gagal tunggal.\nlet counter = 0;\n"
  "try { counter = Number($vars && $vars.chatCounter) || 0; } catch (e) { counter = 0; }\n"
  "counter++;\ntry { if (typeof $vars !== 'undefined' && $vars) $vars.chatCounter = counter; } catch (e) {}",
  "P2-9b Chat Counter tahan $vars tidak tersedia")
nodes["Chat Counter"]["parameters"]["jsCode"] = _c


# ====================================================================
# P2-10 — Detect Lead Source: cocokkan kata, bukan potongan huruf
# ====================================================================
sidik("Detect Lead Source", "kws.some(k => firstMsg.includes(String(k).toLowerCase()))", "P2-10")
_c = kode("Detect Lead Source")
_c = ganti(_c,
  "let detected = '';\nfor (const m of MAP) {\n  const kws = (m.keywords || []);\n"
  "  if (kws.some(k => firstMsg.includes(String(k).toLowerCase()))) { detected = m.source; break; }\n}",
  "// 2026-09-05: dulu memakai includes() telanjang, jadi kata pendek mencocoki\n"
  "// bagian tengah kata lain - 'ig' kena di \"tinggi\"/\"bagi\"/\"ingin\", 'tt' kena di\n"
  "// \"watt\". Sumber lead jadi salah, dan angka itu yang dipakai menilai iklan.\n"
  "// Kata <= 3 huruf sekarang wajib berdiri sendiri; kata panjang tetap longgar.\n"
  "const esc = (s) => String(s).replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');\n"
  "const cocokKata = (teks, kw) => {\n"
  "  const k = String(kw).toLowerCase().trim();\n"
  "  if (!k) return false;\n"
  "  const pola = k.length <= 3\n"
  "    ? new RegExp('(^|[^a-z0-9])' + esc(k) + '([^a-z0-9]|$)', 'i')\n"
  "    : new RegExp(esc(k), 'i');\n"
  "  return pola.test(teks);\n"
  "};\n\n"
  "let detected = '';\nfor (const m of MAP) {\n  const kws = (m.keywords || []);\n"
  "  if (kws.some(k => cocokKata(firstMsg, k))) { detected = m.source; break; }\n}",
  "P2-10 Detect Lead Source pakai batas kata")
nodes["Detect Lead Source"]["parameters"]["jsCode"] = _c


# ====================================================================
# P1-5 — Preprocess: buang logika domain properti, hentikan dorongan
#        [TALK_TO_ADMIN] yang mematikan bot
# ====================================================================
sidik("Preprocess - Context Detection", "PREPROCESS - CONTEXT DETECTION (domain properti PCR)", "P1-5")
set_kode("Preprocess - Context Detection", r"""// ============================================
// PREPROCESS - CONTEXT DETECTION - VIRA Steven (v3, 2026-09-05)
//
// Versi lama masih memakai regex domain PROPERTI warisan Persada (tipe unit, KPR,
// survey lokasi, legalitas, fasilitas). Di bot jasa AI customer service tiga di
// antaranya aktif merusak:
//
//   1. `wantsSurvey || mentionsDateTime` menyuntikkan kalimat yang mendorong
//      [TALK_TO_ADMIN]. Tag itu MEMATIKAN bot untuk orang tersebut sampai
//      bot_mode dinyalakan manual. mentionsDateTime kena di "senin", "besok",
//      "jam 10", "minggu" - kata yang wajar muncul saat prospek menjawab
//      pertanyaan galian ("paling ramai hari Senin", "mau mulai bulan depan").
//      Untuk nomor iklan, itu artinya lead membunuh dirinya sendiri.
//   2. `wantsMedia` kena kata "gambar"/"foto" - termasuk saat PROSPEK yang
//      mengirim gambar - lalu Vira ikut mengirim brosur yang tidak diminta.
//   3. `askingPrice` kena kata "berapa" telanjang, termasuk saat prospek MENJAWAB
//      ("kira-kira berapa chat per hari?" -> "20an"), lalu konteks harga
//      disuntikkan di giliran yang tidak ada hubungannya dengan harga.
//
// Kode properti sisanya (units, budgetMention, KPR, lokasi, legalitas, fasilitas,
// kalender survey) dibuang - tidak ada satu node pun yang membacanya. Hanya
// askingPrice & wantsMedia yang dipakai di luar node ini (boost FAQ Retrieve).
// ============================================
const json = $input.item.json;
const fullMessage = json.ai_input_text || json.message || json.text || '';

// -- PARSE INPUT --
let actualUserMessage = '';
if (fullMessage.includes('[USER QUERY]')) {
  actualUserMessage = (fullMessage.split('[USER QUERY]')[1] || '').trim();
} else {
  actualUserMessage = String(fullMessage).trim();
}

let isNewUser = false;
if (fullMessage.includes('[SYSTEM_DATA]')) {
  const m = fullMessage.match(/IS_NEW_USER:\s*(\w+)/i);
  if (m) isNewUser = m[1].toLowerCase() === 'true';
}

const message = actualUserMessage.toLowerCase();
const userPhone = json.user_wa || json.from || 'unknown';

// -- INTENT (domain jasa AI customer service) --
// Harus ada kata yang benar-benar soal uang/paket, bukan sekadar "berapa".
// Akhiran -nya/-ku/-mu WAJIB ditoleransi: \b di ujung kata membuat "harganya",
// "brosurnya", "biayanya" tidak pernah cocok - padahal itu bentuk yang paling
// sering dipakai orang Indonesia saat bertanya.
const askingPrice = /\b(harga|hrg|biaya|tarif|bayar|langganan|paket|basic|premium|mahal|murah|promo|diskon|setup ?fee|budget|nego)(nya|ku|mu)?\b/i.test(message)
  || /\bberapa\b[^?]{0,20}\b(harga|biaya|duit|rupiah|bulan|bulanan)/i.test(message);

// File hanya dianggap DIMINTA kalau ada kata bendanya DAN kata memintanya.
// "aku kirim foto ya" -> BENDA tidak kena (foto sengaja tidak masuk daftar).
const BENDA_FILE = /\b(brosur|katalog|price ?list|portfolio|portofolio|deck|demo|dokumen|file|contoh)(nya|ku|mu)?\b/i;
const KATA_MINTA = /\b(minta|kirim|kirimin|share|bagi|boleh|ada|punya|lihat|liat|mau|pengen|bisa|dong)\b/i;
const wantsMedia = BENDA_FILE.test(message) && KATA_MINTA.test(message);

// Niat bicara langsung dengan Steven. SENGAJA TIDAK disuntikkan sebagai dorongan
// tag - hanya dicatat, supaya Process All yang memutuskan apakah bot dimatikan.
const wantsHuman = /\b(telp|telepon|telfon|call|ditelpon|ditelepon|ketemu|meeting|zoom|gmeet|disambungkan|sambungin)\b/i.test(message)
  || /\b(hubungi|kontak|nomor|no\.?|cp|wa)\b[^.?!]{0,25}steven/i.test(message)
  || /\bhubungi\b[^.?!]{0,20}\b(aku|saya|gue|gw)\b/i.test(message)
  || /\b(ngobrol|bicara|tanya|chat|ngomong)\b[^.?!]{0,20}(langsung|steven|orangnya|manusia|orang aslinya)/i.test(message);

let aiContext = '';
if (askingPrice) aiContext += 'User menanyakan harga. Sebut kisaran dari DATA PRODUK lalu arahkan ke Steven untuk angka final. Jangan menawar, jangan memberi diskon. ';
if (wantsMedia)  aiContext += 'User meminta file. Kalau ada yang cocok di DAFTAR MEDIA, pasang [SEND_MEDIA: <nama-link>] persis seperti tertulis di daftar. Kalau tidak ada yang cocok, jangan pasang tag apa pun dan jangan mengarang nama link. ';

// -- RAKIT INPUT AI --
let systemDataBlock = '';
if (fullMessage.includes('[USER QUERY]')) systemDataBlock = fullMessage.split('[USER QUERY]')[0].trim();

let enhancedInput = '';
if (systemDataBlock) enhancedInput += systemDataBlock + '\n\n';
if (aiContext.trim()) enhancedInput += '[CONTEXT: ' + aiContext.trim() + ']\n\n';
enhancedInput += '[USER QUERY]\n' + actualUserMessage;

return {
  userPhone,
  actualUserMessage,
  fullMessage,
  messageLower: message,
  isNewUser,
  askingPrice,
  wantsMedia,
  wantsHuman,
  aiContext: aiContext.trim(),
  ai_input_text: enhancedInput
};""", "P1-5 Preprocess disesuaikan domain jasa")


# ====================================================================
# P0-2a — Resolve User Row membawa balasan terakhir yang BENAR-BENAR terkirim
# ====================================================================
_c = kode("Resolve User Row")
_c = ganti(_c,
  "    counter_db: Number(row ? (row['Counter'] || 0) : 0) || 0\n  }",
  "    counter_db: Number(row ? (row['Counter'] || 0) : 0) || 0,\n"
  "    // Teks balasan terakhir yang benar-benar sampai ke prospek (lihat P0-2 di\n"
  "    // _patch_2026-09-05.py). Simple Memory menyimpan tulisan MENTAH AI Agent,\n"
  "    // yang bisa berbeda dari yang dikirim. Kolom ini sumber kebenarannya.\n"
  "    last_bot_reply: row ? String(row['last_bot_reply'] || '').trim() : '',\n"
  "    last_bot_reply_ts: Number(row ? (row['last_bot_reply_ts'] || 0) : 0) || 0\n  }",
  "P0-2a Resolve User Row expose last_bot_reply")
nodes["Resolve User Row"]["parameters"]["jsCode"] = _c


# ====================================================================
# P0-2b — Cek_user_status menyuntikkan balasan terakhir ke prompt
# ====================================================================
_c = kode("Cek_user_status")
_c = ganti(_c,
  "const aiSystemData = `[SYSTEM_DATA]\nUSER_WA: ${resolvedKey}\n"
  "IS_NEW_USER: ${isNewUser}\nNAMA_LENGKAP: ${namaLengkap || 'UNKNOWN'}\n"
  "TANGGAL_SEKARANG: ${tanggalSekarang} (${hariSekarang}) ${jamSekarang} WIB\n\n"
  "CRITICAL INSTRUCTION:",
  "// -- JARING PENGAMAN INGATAN (2026-09-05) --\n"
  "// Simple Memory menyimpan tulisan MENTAH AI Agent. Kalau Process All mengganti\n"
  "// teksnya (file tidak ada di katalog, pilihan media ambigu), atau kalau n8n\n"
  "// restart dan memory hilang, model tidak tahu apa yang sebenarnya dibaca\n"
  "// prospek - dia menyangkal pernah bertanya lalu bertanya ulang. Kolom STATS\n"
  "// last_bot_reply selalu berisi teks yang BENAR-BENAR terkirim, jadi kebenaran\n"
  "// itu selalu ada di prompt apa pun yang terjadi pada memory.\n"
  "const lastReply = String(debounceRow['last_bot_reply'] || resolve.last_bot_reply || '').trim();\n"
  "const lastReplyTs = Number(debounceRow['last_bot_reply_ts'] || resolve.last_bot_reply_ts || 0) || 0;\n"
  "const lastReplyFresh = lastReply !== '' && lastReplyTs > 0 && (nowS - lastReplyTs) <= 24 * 3600;\n"
  "const blokBalasanTerakhir = lastReplyFresh\n"
  "  ? `\\nBALASAN TERAKHIRMU YANG BENAR-BENAR DITERIMA PROSPEK:\\n\"${lastReply.replace(/\"/g, \"'\").slice(0, 700)}\"\\n`\n"
  "    + `Pesan prospek di bawah adalah tanggapan atas kalimat itu. Kalau ingatanmu berbeda, kalimat di atas yang benar.\\n`\n"
  "  : '';\n\n"
  "const aiSystemData = `[SYSTEM_DATA]\nUSER_WA: ${resolvedKey}\n"
  "IS_NEW_USER: ${isNewUser}\nNAMA_LENGKAP: ${namaLengkap || 'UNKNOWN'}\n"
  "TANGGAL_SEKARANG: ${tanggalSekarang} (${hariSekarang}) ${jamSekarang} WIB\n"
  "${blokBalasanTerakhir}\nCRITICAL INSTRUCTION:",
  "P0-2b Cek_user_status suntik BALASAN TERAKHIRMU")
_c = ganti(_c,
  "    buffer_done_ts_old: doneTs,",
  "    buffer_done_ts_old: doneTs,\n"
  "    last_bot_reply_prev: lastReply,\n"
  "    last_bot_reply_fresh: lastReplyFresh,",
  "P0-2b2 Cek_user_status expose last_bot_reply_prev")
nodes["Cek_user_status"]["parameters"]["jsCode"] = _c


# ====================================================================
# P2-11 — IS_NEW_USER dihitung satu cara saja
# ====================================================================
# Cek_user_status memakai greeting_sent !== 'Y'; Rakit Konteks memakai
# "kolom kosong". Nilai 'N' membuat dua blok di prompt yang SAMA saling
# bertentangan (SYSTEM_DATA bilang baru, DATA PROSPEK bilang lama).
_c = kode("Rakit Konteks")
_c = ganti(_c,
  "const baru = !txt(stats['greeting_sent']);",
  "// Definisi harus persis sama dengan Cek_user_status, kalau tidak SYSTEM_DATA\n"
  "// dan DATA PROSPEK bisa mengabarkan dua hal berbeda di prompt yang sama.\n"
  "const baru = txt(stats['greeting_sent']).toUpperCase() !== 'Y';",
  "P2-11 IS_NEW_USER konsisten")
nodes["Rakit Konteks"]["parameters"]["jsCode"] = _c


# ====================================================================
# P0-3 — `rapikanUrl` diangkat ke lingkup atas (ReferenceError)
# ====================================================================
# Dideklarasikan dengan const DI DALAM blok `if (isSendMedia) { ... }`, tapi
# dipakai lagi di blok "MEDIA KE-2" di luar blok itu. Begitu AI mengeluarkan dua
# tag [SEND_MEDIA] dan keduanya ketemu di LINKS, node ini melempar ReferenceError:
# eksekusi merah, prospek tidak menerima balasan apa pun.
_c = kode("Process All")
_blok_lama = (
"  // Drive 'uc?export=download' membalas halaman konfirmasi virus-scan (HTML) untuk\n"
"  // file besar, bukan byte filenya. Bentuk usercontent + confirm=t melewati halaman itu.\n"
"  const rapikanUrl = (u) => {\n"
"    const s = String(u || '').trim();\n"
"    const m = s.match(/^https?:\\/\\/(?:drive|docs)\\.google\\.com\\/(?:uc\\?(?:[^#]*&)?id=|file\\/d\\/)([A-Za-z0-9_-]{10,})/);\n"
"    return m ? ('https://drive.usercontent.google.com/download?id=' + m[1] + '&export=download&confirm=t') : s;\n"
"  };\n\n"
)
_c = ganti(_c, _blok_lama, "", "P0-3a rapikanUrl dilepas dari blok if")
_c = ganti(_c,
"      || t === 'tidak disebut' || t === 'n/a' || t === 'na' || t === 'null' || t === 'undefined';\n};",
"      || t === 'tidak disebut' || t === 'n/a' || t === 'na' || t === 'null' || t === 'undefined';\n};\n"
"// Drive 'uc?export=download' membalas halaman konfirmasi virus-scan (HTML) untuk\n"
"// file besar, bukan byte filenya. Bentuk usercontent + confirm=t melewati halaman itu.\n"
"// 2026-09-05: dipindah ke lingkup atas. Sebelumnya const ini hidup di dalam blok\n"
"// `if (isSendMedia)` tapi dipanggil lagi di blok MEDIA KE-2 di luar blok itu ->\n"
"// ReferenceError setiap kali balasan memuat dua tag [SEND_MEDIA] yang keduanya\n"
"// ketemu di LINKS. Akibatnya prospek tidak menerima balasan sama sekali.\n"
"const rapikanUrl = (u) => {\n"
"  const s = String(u || '').trim();\n"
"  const m = s.match(/^https?:\\/\\/(?:drive|docs)\\.google\\.com\\/(?:uc\\?(?:[^#]*&)?id=|file\\/d\\/)([A-Za-z0-9_-]{10,})/);\n"
"  return m ? ('https://drive.usercontent.google.com/download?id=' + m[1] + '&export=download&confirm=t') : s;\n"
"};",
"P0-3b rapikanUrl dipasang di lingkup atas")

# --------------------------------------------------------------------
# P1-8b — blok [DECK_REQUEST] yang tidak tertutup tetap dibaca
# --------------------------------------------------------------------
# Regex lama mewajibkan tag penutup. Kalau keluaran model terpotong batas token,
# SELURUH brief hilang di situ - padahal baris yang sudah tertulis tetap sah, dan
# justru brief terpanjang (33 baris) yang paling mungkin terpotong sekaligus
# paling berharga. Ditemukan lewat skenario UAT G12b.
_c = ganti(_c,
"const deckBlock = aiOutput.match(/\\[\\s*DECK_REQUEST\\s*\\]([\\s\\S]*?)\\[\\s*\\/\\s*DECK_REQUEST\\s*\\]/i);",
"let deckBlock = aiOutput.match(/\\[\\s*DECK_REQUEST\\s*\\]([\\s\\S]*?)\\[\\s*\\/\\s*DECK_REQUEST\\s*\\]/i);\n"
"// Keluaran yang terpotong batas token kehilangan tag penutupnya. Kalau tag\n"
"// pembuka ada tapi penutupnya tidak, baca sampai akhir keluaran: baris yang\n"
"// sempat tertulis tetap sah, dan Merge Brief memang dirancang menerima brief\n"
"// setengah jadi. Membuang semuanya adalah kerugian yang tidak perlu.\n"
"if (!deckBlock) {\n"
"  const buka = aiOutput.match(/\\[\\s*DECK_REQUEST\\s*\\]([\\s\\S]*)$/i);\n"
"  if (buka) {\n"
"    console.warn('Blok DECK_REQUEST tidak tertutup (keluaran terpotong?) - dibaca sampai akhir.');\n"
"    deckBlock = buka;\n"
"  }\n"
"}",
"P1-8b blok DECK_REQUEST tanpa penutup tetap dibaca")

# --------------------------------------------------------------------
# P1-4 + P1-6 — niat deck (termasuk persetujuan pendek) & gerbang mematikan bot
# --------------------------------------------------------------------
_c = ganti(_c,
"const PESAN_USER = String((preprocess && preprocess.actualUserMessage) || originalMessage || '')\n"
"                     .toLowerCase();\n"
"const NIAT_DECK   = /\\b(deck|pitch|penawaran|proposal)\\b|dibuat(in|kan)|dibikin(in|kan)?/;\n"
"const NIAT_BICARA = /telp|telepon|telfon|call|ketemu|meeting|zoom|disambungkan|sambungin|hubungi aku|hubungi saya|ngobrol (langsung|sama|dgn|dengan)|bicara (langsung|sama|dgn|dengan)/;\n"
"const mintaDeck   = NIAT_DECK.test(PESAN_USER) && !NIAT_BICARA.test(PESAN_USER);",
"const PESAN_USER = String((preprocess && preprocess.actualUserMessage) || originalMessage || '')\n"
"                     .toLowerCase().trim();\n"
"const NIAT_DECK   = /\\b(deck|pitch|penawaran|proposal)\\b|dibuat(in|kan)|dibikin(in|kan)?/;\n"
"// Diperluas 2026-09-05: versi lama tidak mengenali \"boleh minta kontaknya\",\n"
"// \"ada CP?\", \"mau tanya langsung ke orangnya\" - padahal ketiganya permintaan\n"
"// bicara yang sah, dan regex ini yang memutuskan bot boleh dimatikan atau tidak.\n"
"const NIAT_BICARA = /telp|telepon|telfon|call|ditelpon|ditelepon|ketemu|meeting|zoom|gmeet|disambungkan|sambungin|hubungi (aku|saya|gue|gw)|nomor(nya)? steven|kontak(nya)? (steven|orangnya|langsung)|minta kontak|\\bcp\\b|ngobrol (langsung|sama|dgn|dengan)|bicara (langsung|sama|dgn|dengan)|(tanya|chat|ngomong) (langsung|sama|dgn|dengan) (steven|orangnya|manusia|orang aslinya)/;\n"
"\n"
"// Persetujuan pendek atas tawaran deck: \"boleh\", \"mau\", \"oke\", \"ya\".\n"
"// Kalimat seperti ini tidak memuat kata \"deck\" sama sekali, jadi NIAT_DECK tidak\n"
"// kena - padahal justru inilah kalimat yang paling sering dipakai prospek untuk\n"
"// menyetujui tawaran. Kejadian 2026-09-05 14:34: prospek menjawab \"boleh\",\n"
"// briefnya tersimpan, tapi Steven tidak pernah dinotifikasi.\n"
"// Sumbernya `last_bot_reply` - teks yang BENAR-BENAR dikirim giliran sebelumnya,\n"
"// bukan ingatan model, jadi gerbang ini deterministik.\n"
"const BALASAN_LALU  = String(prev.last_bot_reply || '').toLowerCase();\n"
"const TAWARAN_DECK  = /\\b(deck|pitch|penawaran|proposal)\\b/.test(BALASAN_LALU);\n"
"const SETUJU_PENDEK = PESAN_USER.length <= 40\n"
"  && /^\\W*(boleh|mau|oke+|ok|ya+|iya+|yes|sip|siap|gas|silakan|silahkan|tolong|please|lanjut)\\b/.test(PESAN_USER);\n"
"const mintaDeck = (NIAT_DECK.test(PESAN_USER) || (TAWARAN_DECK && SETUJU_PENDEK))\n"
"                  && !NIAT_BICARA.test(PESAN_USER);\n"
"if (TAWARAN_DECK && SETUJU_PENDEK) {\n"
"  console.log('Persetujuan pendek atas tawaran deck terdeteksi: \"' + PESAN_USER + '\"');\n"
"}",
"P1-4 niat deck mengenali persetujuan pendek")

_c = ganti(_c,
"if (isTalkToAdmin && mintaDeck && isDeckRequest) {\n"
"  console.warn('Niat deck terdeteksi pada pesan yang ditandai TALK_TO_ADMIN. '\n"
"             + 'Handover dibatalkan supaya bot tidak dimatikan: ' + PESAN_USER.slice(0, 120));\n"
"  isTalkToAdmin = false;\n"
"}",
"if (isTalkToAdmin && mintaDeck && isDeckRequest) {\n"
"  console.warn('Niat deck terdeteksi pada pesan yang ditandai TALK_TO_ADMIN. '\n"
"             + 'Handover dibatalkan supaya bot tidak dimatikan: ' + PESAN_USER.slice(0, 120));\n"
"  isTalkToAdmin = false;\n"
"}\n"
"\n"
"// -- Gerbang mematikan bot (2026-09-05) --\n"
"// [TALK_TO_ADMIN] punya dua akibat yang bobotnya jauh berbeda: (a) Steven\n"
"// dinotifikasi, dan (b) bot BERHENTI membalas orang itu sampai bot_mode\n"
"// dinyalakan manual di sheet. Untuk nomor iklan, (b) adalah lead yang hilang\n"
"// permanen kalau modelnya salah memilih tag - dan model memang pernah memilih\n"
"// tag dari kalimat yang sedang dia tulis, bukan dari yang prospek minta.\n"
"// Mulai sekarang: notifikasi tetap dikirim setiap kali tag keluar, tapi bot\n"
"// hanya dimatikan kalau PROSPEK yang memang memintanya di pesan ini.\n"
"// Gagal ke arah \"bot tetap hidup\" jauh lebih murah daripada sebaliknya.\n"
"// Dua sumber niat bicara digabung supaya perbedaan kecil antara regex di sini\n"
"// dan di Preprocess tidak pernah menghasilkan keputusan yang berbeda.\n"
"const mintaBicara = (preprocess && preprocess.wantsHuman === true) || NIAT_BICARA.test(PESAN_USER);\n"
"const matikanBot = isTalkToAdmin && mintaBicara;\n"
"if (isTalkToAdmin && !matikanBot) {\n"
"  console.warn('TALK_TO_ADMIN tanpa permintaan bicara yang eksplisit di pesan user. '\n"
"             + 'Steven tetap dinotifikasi, bot DIBIARKAN HIDUP: ' + PESAN_USER.slice(0, 120));\n"
"}",
"P1-6 tag TALK_TO_ADMIN tidak lagi otomatis mematikan bot")

# --------------------------------------------------------------------
# P0-2c — hapus override balasan yang menciptakan desinkronisasi ingatan
# --------------------------------------------------------------------
_c = ganti(_c,
"// ── FAIL LOUD: brief ditolak tapi balasan terlanjur menjanjikan deck ──\n"
"// Tag ditolak harus MENGUBAH balasan, bukan cuma dibuang — kalau tidak, prospek\n"
"// diberi janji yang tidak ada catatannya di mana pun. Override hanya dilakukan\n"
"// kalau balasannya memang menjanjikan; kalau tidak, tag cukup didiamkan.\n"
"if (deckRejected) {\n"
"  const low = cleanOutput.toLowerCase();\n"
"  const menjanjikan = /(deck|proposal|penawaran)/.test(low)\n"
"                   && /(susun|siapkan|buatkan|kirim|hubungi|kabari)/.test(low);\n"
"  if (menjanjikan) {\n"
"    const TANYA = {\n"
"      nama_bisnis:   'Boleh tahu nama bisnisnya dulu kak? Biar aku catat dengan benar.',\n"
"      industri:      'Bisnisnya bergerak di bidang apa kak?',\n"
"      masalah_utama: 'Sekarang yang paling bikin repot soal chat masuk itu apa kak?',\n"
"    };\n"
"    cleanOutput = TANYA[deckMissing[0]] || 'Boleh cerita sedikit soal bisnisnya kak?';\n"
"    console.warn('Balasan diganti: janji deck tanpa brief tingkat 1.');\n"
"  }\n"
"}",
"// -- DIHAPUS 2026-09-05: override balasan saat brief tingkat 1 belum lengkap --\n"
"// Blok lama mengganti kalimat AI dengan pertanyaan kaleng ('Boleh tahu nama\n"
"// bisnisnya dulu kak?'). Yang DIKIRIM ke prospek adalah pertanyaan itu, tapi yang\n"
"// DISIMPAN Simple Memory adalah tulisan asli AI. Giliran berikutnya prospek\n"
"// menjawab pertanyaan yang - menurut ingatan model - tidak pernah dia ajukan.\n"
"// Persis inilah yang terjadi 2026-09-05 14:35-14:45: prospek menjawab nama\n"
"// bisnisnya, VIRA menjawab 'aku belum paham maksudnya', lalu 'aku belum nanya\n"
"// apa-apa barusan'. Nama bisnisnya pun tidak pernah tersimpan, jadi override\n"
"// yang sama siap terpicu lagi di giliran berikutnya - lingkaran tertutup.\n"
"//\n"
"// Alasan blok ini dulu ada sudah hilang sejak patch 2026-08-30: brief tingkat 1\n"
"// yang belum lengkap TETAP ditulis ke REQUESTS, dan notifikasi ke Steven punya\n"
"// gerbangnya sendiri (`deck_layak` di Merge Brief). Jadi balasannya tidak lagi\n"
"// menjanjikan sesuatu yang tidak tercatat. Menggali nama bisnis dikembalikan ke\n"
"// tugas prompt (bagian MENGGALI, TINGKAT 1), tempat yang benar untuk itu.\n"
"if (deckRejected) {\n"
"  console.log('Brief tingkat 1 belum lengkap (' + deckMissing.join(', ')\n"
"            + '). Tetap disimpan; balasan AI TIDAK diubah.');\n"
"}",
"P0-2c override deckRejected dihapus")

# --------------------------------------------------------------------
# P0-2d — override yang tersisa ditandai supaya bisa dilacak
# --------------------------------------------------------------------
_c = ganti(_c,
"let isTalkToAdmin   = aiOutput.includes('[TALK_TO_ADMIN]');",
"let isTalkToAdmin   = aiOutput.includes('[TALK_TO_ADMIN]');\n"
"// Ditandai true setiap kali teks yang dikirim ke prospek BUKAN tulisan AI.\n"
"// Dua kasus yang tersisa (media ambigu & file tidak ada di katalog) memang harus\n"
"// mengganti kalimat, karena AI menjanjikan file yang tidak bisa dikirim.\n"
"// Desinkronisasi ingatannya ditutup dari sisi lain: kolom STATS last_bot_reply\n"
"// selalu berisi teks final, dan Cek_user_status menyuntikkannya ke prompt.\n"
"let replyOverridden = false;",
"P0-2d penanda replyOverridden")
_c = ganti(_c,
"      cleanOutput = `Ada beberapa yang cocok kak, mau yang mana yaa, ${optText}?`;",
"      cleanOutput = `Ada beberapa yang cocok kak, mau yang mana yaa, ${optText}?`;\n"
"      replyOverridden = true;",
"P0-2d2 tandai override media ambigu")
_c = ganti(_c,
"    cleanOutput = 'Maaf kak, file itu belum ada di katalogku jadi belum bisa aku kirim '\n"
"                + 'langsung. Sudah aku teruskan ke Steven yaa, biar dia yang kirim.' + alt;",
"    cleanOutput = 'Maaf kak, file itu belum ada di katalogku jadi belum bisa aku kirim '\n"
"                + 'langsung. Sudah aku teruskan ke Steven yaa, biar dia yang kirim.' + alt;\n"
"    replyOverridden = true;",
"P0-2d3 tandai override file tidak ada")

# --------------------------------------------------------------------
# Keluaran baru Process All
# --------------------------------------------------------------------
_c = ganti(_c,
"    deckDiminta: mintaDeck,",
"    deckDiminta: mintaDeck,\n"
"    // deckNotify = ada blok brief berisi, ATAU prospek meminta deck. Dipakai\n"
"    // Merge Brief (gerbang notifikasi) dan kolom STATS.deck_requested supaya\n"
"    // keduanya tidak pernah berbeda pendapat.\n"
"    deckNotify: isDeckRequest || mintaDeck,\n"
"    // matikanBot = satu-satunya nilai yang boleh menulis bot_mode = OFF.\n"
"    matikanBot,\n"
"    replyOverridden,\n"
"    // Teks yang benar-benar dikirim ke prospek; ditulis ke STATS.last_bot_reply.\n"
"    last_bot_reply: cleanOutput,",
"P0-2e keluaran deckNotify/matikanBot/last_bot_reply")
nodes["Process All"]["parameters"]["jsCode"] = _c


# ====================================================================
# P1-4b — Merge Brief: gerbang notifikasi tidak lagi bergantung pada
#         kepatuhan model, tapi tetap tidak membanjiri Steven
# ====================================================================
_c = kode("Merge Brief")
_c = ganti(_c,
"    deck_layak: pa.deckLayak === true || pa.deckDiminta === true,",
"    // 2026-09-05 - tiga jalan menuju true, dan yang ketiga yang menutup lubangnya:\n"
"    //   1. tingkat 1 lengkap (deckLayak), ATAU\n"
"    //   2. prospek MEMINTA deck di pesan ini (deckDiminta), ATAU\n"
"    //   3. ada blok brief berisi yang belum pernah dilaporkan / isinya bertambah.\n"
"    // Tanpa (3), brief yang tersimpan bisa tidak pernah sampai ke Steven - persis\n"
"    // yang terjadi 2026-09-05 14:34. Syarat 'pertama kali atau bertambah' yang\n"
"    // mencegah notifikasi berulang untuk brief yang isinya sama.\n"
"    deck_layak: pa.deckLayak === true || pa.deckDiminta === true\n"
"                || (pa.isDeckRequest === true && (pertamaKali || bertambah)),",
"P1-4b Merge Brief gerbang notifikasi")
_c = ganti(_c,
"const tsLama = String(lama['ts'] || '').trim();\nconst revisi = tsLama ? ' (diperbarui)' : '';",
"const tsLama = String(lama['ts'] || '').trim();\nconst revisi = tsLama ? ' (diperbarui)' : '';\n"
"// Dipakai gerbang notifikasi di bawah: brief baru selalu dilaporkan, brief lama\n"
"// hanya dilaporkan lagi kalau benar-benar ada isian tambahan.\n"
"const jumlahLama  = Number(lama['brief_jumlah'] || 0) || 0;\n"
"const pertamaKali = !tsLama;\n"
"const bertambah   = terisi.length > jumlahLama;",
"P1-4b2 Merge Brief hitung pertamaKali/bertambah")
nodes["Merge Brief"]["parameters"]["jsCode"] = _c


# ====================================================================
# P0-2f — STATS menyimpan balasan yang benar-benar terkirim
#         + bot_mode & deck_requested memakai gerbang yang benar
# ====================================================================
_val = nodes["Update to STATS"]["parameters"]["columns"]["value"]
if _val.get("bot_mode") != "={{ $('Process All').first().json.isTalkToAdmin ? 'OFF' : 'ON' }}":
    raise SystemExit("GAGAL [P0-2f]: mapping bot_mode di 'Update to STATS' tidak seperti diharapkan.")
_val["bot_mode"] = "={{ $('Process All').first().json.matikanBot ? 'OFF' : 'ON' }}"
_val["deck_requested"] = ("={{ $('Process All').first().json.deckNotify ? 'Y' : "
                          "($('Resolve User Row').first().json.deck_requested || '') }}")
_val["last_bot_reply"] = "={{ $('Process All').first().json.cleanOutput }}"
_val["last_bot_reply_ts"] = "={{ Math.floor(Date.now()/1000) }}"

_schema = nodes["Update to STATS"]["parameters"]["columns"]["schema"]
_ada = {s["id"] for s in _schema}
for _kol in ("last_bot_reply", "last_bot_reply_ts"):
    if _kol not in _ada:
        _schema.append({
            "id": _kol, "displayName": _kol, "required": False, "defaultMatch": False,
            "display": True, "type": "string", "canBeUsedToMatch": True, "removed": False,
        })
jejak.append("P0-2f Update to STATS: last_bot_reply + bot_mode/deck_requested")

_valb = nodes["Update STATS Brief"]["parameters"]["columns"]["value"]
_valb["deck_requested"] = ("={{ $('Process All').first().json.deckNotify ? 'Y' : "
                           "($('Resolve User Row').first().json.deck_requested || '') }}")
jejak.append("P1-4c Update STATS Brief: deck_requested pakai deckNotify")

_valc = nodes["Update row in sheet"]["parameters"]["columns"]["value"]
if _valc.get("bot_mode") != "OFF":
    raise SystemExit("GAGAL [P1-6b]: mapping bot_mode di 'Update row in sheet' tidak seperti diharapkan.")
_valc["bot_mode"] = "={{ $('Process All').first().json.matikanBot ? 'OFF' : 'ON' }}"
jejak.append("P1-6b Update row in sheet: bot_mode hanya OFF kalau prospek memintanya")


# ====================================================================
# P1-6c — Steven perlu tahu bot masih hidup atau tidak saat handover masuk
# ====================================================================
_c = kode("Format Handover Message")
_c = ganti(_c,
"const message = `${header}\n\n${summary}\n\n— Chat: wa.me/${p.no_wa}`;",
"// Sejak 2026-09-05 tag [TALK_TO_ADMIN] tidak selalu mematikan bot (lihat P1-6).\n"
"// Steven harus tahu mana yang sedang dia terima, kalau tidak dia menunggu giliran\n"
"// membalas untuk chat yang sebenarnya masih dipegang VIRA - atau sebaliknya.\n"
"const botMati = (() => { try { return $('Process All').first().json.matikanBot === true; } catch (e) { return true; } })();\n"
"const statusBot = botMati\n"
"  ? 'STATUS: VIRA sudah BERHENTI membalas orang ini. Balas manual, lalu set bot_mode=ON di STATS kalau mau diserahkan lagi ke VIRA.'\n"
"  : 'STATUS: VIRA MASIH membalas orang ini (prospek tidak minta disambungkan secara eksplisit). Set bot_mode=OFF di STATS kalau mau ambil alih.';\n"
"\n"
"const message = `${header}\n\n${summary}\n\n${statusBot}\n\n— Chat: wa.me/${p.no_wa}`;",
"P1-6c status bot di notifikasi handover")
nodes["Format Handover Message"]["parameters"]["jsCode"] = _c


# ====================================================================
# Model DeepSeek (permintaan Steven, 2026-09-05)
#   chat balasan prospek -> deepseek-v4-pro
#   ringkasan handover ke Steven -> deepseek-v4-flash
# Node community ini defaultnya 'deepseek-v4-flash' saat parameter `model`
# tidak ditulis; sebelum patch kedua node berjalan di flash.
# ====================================================================
_chat = nodes["DeepSeek Personal Chat"]["parameters"]
_chat["model"] = "deepseek-v4-pro"
# P1-8: 1024 token memotong output. Blok [DECK_REQUEST] 33 baris + balasan +
# [FACTS] yang ditulis PALING AKHIR. Yang pertama hilang saat terpotong justru
# [FACTS] - fakta prospek tidak pernah tersimpan, lalu bot menanyakannya lagi.
_chat["options"]["maxTokens"] = 3000
if _chat["options"].get("temperature") != 0.7:
    raise SystemExit("GAGAL: temperature chat bukan 0.7 - jangan diubah tanpa keputusan Steven.")

_sum = nodes["DeepSeek Personal Summary"]["parameters"]
_sum["model"] = "deepseek-v4-flash"
jejak.append("Model: chat=deepseek-v4-pro (maxTokens 3000), summary=deepseek-v4-flash")


# ====================================================================
# System message — aturan baru + pemadatan
# ====================================================================
_sm = nodes["AI Agent"]["parameters"]["options"]["systemMessage"]
_panjang_awal = len(_sm)


def gsm(lama, baru, label):
    global _sm
    _sm = ganti(_sm, lama, baru, label)


# (1) Aturan BALASAN TERAKHIRMU — pasangan prompt dari P0-2.
gsm(
"# SUMBER FAKTA\n",
"# BALASAN TERAKHIRKU\n\n"
"Kadang di [SYSTEM_DATA] ada blok BALASAN TERAKHIRMU YANG BENAR-BENAR DITERIMA PROSPEK.\n"
"Itu teks yang sungguh-sungguh terkirim ke WhatsApp-nya. Kalau ingatanku berbeda dari kalimat itu,\n"
"kalimat itu yang benar dan pesan prospek berikutnya adalah tanggapan atasnya.\n"
"Aku tidak pernah bilang \"aku belum menanyakan apa pun\" atau \"aku tidak paham maksudmu\"\n"
"selama jawabannya masuk akal sebagai tanggapan atas kalimat itu. Kalau blok itu berisi\n"
"pertanyaan dan prospek menjawab dengan satu kata, kata itu adalah jawaban pertanyaanku.\n\n"
"# SUMBER FAKTA\n",
"SM-1 aturan BALASAN TERAKHIRKU")

# (2) Nama bisnis harus ditangkap begitu disebut. Ini yang dulu ditambal override
#     di Process All; sekarang jadi tugas prompt, tempat yang benar.
gsm(
"  `nama` adalah nama orangnya, bukan nama bisnisnya — pakai tag ini begitu dia menyebutkan namanya,\n"
"  supaya aku bisa memanggilnya dengan nama itu di percakapan berikutnya.",
"  `nama` adalah nama orangnya, bukan nama bisnisnya — pakai tag ini begitu dia menyebutkan namanya,\n"
"  supaya aku bisa memanggilnya dengan nama itu di percakapan berikutnya.\n"
"  Satu kata atau nama yang tidak kukenal, dikirim tepat setelah aku menanyakan nama bisnis atau\n"
"  bidang usahanya, adalah JAWABAN atas pertanyaan itu — bukan pertanyaan baru. Catat lewat tag ini,\n"
"  jangan tanya balik apa maksudnya.",
"SM-2 satu kata setelah pertanyaan = jawaban")

# (3) Pemadatan: langkah 10 mengulang seluruh aturan panjang yang sudah ada di GAYA.
gsm(
"10. Sebelum mengirim: hitung kalimat yang DIBACA PROSPEK saja. Lebih dari 3 — potong sampai 3.\n"
"    Perkenalan, tanggapan atas gambar, dan pertanyaan galian ikut terhitung.\n"
"    TAG TIDAK PERNAH ikut dihitung dan TIDAK PERNAH dipotong. Batas ini soal panjang balasan,\n"
"    bukan izin membuang `[DECK_REQUEST]` atau `[FACTS]` — kedua tag tetap ditulis utuh dengan\n"
"    semua barisnya walaupun balasan untuk prospeknya cuma satu kalimat.",
"10. Sebelum mengirim: hitung kalimat yang DIBACA PROSPEK saja (lihat GAYA). TAG tidak pernah\n"
"    ikut dihitung dan tidak pernah dipotong, walau balasannya cuma satu kalimat.",
"SM-3 padatkan langkah 10")

# (4) ALUR adalah ringkasan urutan kerja; aturan lengkap tiap tag sudah ada di
#     bagian TAG. Tiga langkah di bawah menuliskan ulang aturan itu kata per kata.
#     Yang dibuang hanya duplikatnya — tidak ada aturan yang hilang dari prompt.
gsm(
"2. Kalau dia minta bicara dengan Steven, minta ditelepon, minta meeting, atau sudah dua kali aku salah menangkap\n"
"   maksudnya — pakai `[TALK_TO_ADMIN]`.",
"2. Kalau dia ingin bicara langsung dengan Steven, atau aku sudah dua kali salah menangkap maksudnya —\n"
"   pakai `[TALK_TO_ADMIN]` (aturan lengkapnya di bagian TAG).",
"SM-4 padatkan langkah 2")

gsm(
"3. Kalau ini pesan pertamanya dan `IS_NEW_USER` bernilai true — buka dengan perkenalan (lihat PERKENALAN),\n"
"   digabung dengan jawaban atas pertanyaannya. Jangan jadi dua pesan terpisah.",
"3. Kalau `IS_NEW_USER` true — buka dengan PERKENALAN, digabung dengan jawaban dalam satu pesan.",
"SM-5 padatkan langkah 3")

gsm(
"8. Kalau syarat brief sudah terpenuhi, keluarkan `[DECK_REQUEST]` (lihat bagian TAG).\n"
"   Kalau dia baru saja menjawab \"ya\"/\"oke\"/\"boleh\" atas tawaran deck, tag ini WAJIB keluar di\n"
"   balasan itu juga — persetujuannya sendiri sudah dihitung sebagai informasi baru. Mengabari\n"
"   soal deck tanpa menulis tagnya berarti briefnya tidak pernah sampai ke Steven.\n"
"   Kalau tag ini keluar dan DATA PROSPEK belum memuat `sudah_minta_pitch_deck: ya`, balasan kali\n"
"   ini WAJIB menyinggung decknya — dan langkah 7 dilewati, jangan menggali di giliran yang sama.",
"8. Kalau syarat brief terpenuhi, keluarkan `[DECK_REQUEST]` (lihat TAG). Jawaban \"ya\"/\"oke\"/\"boleh\"\n"
"   atas tawaran deck WAJIB memunculkan tag itu di balasan yang sama — tanpa tagnya, briefnya tidak\n"
"   pernah sampai ke Steven. Kalau tag keluar dan DATA PROSPEK belum memuat `sudah_minta_pitch_deck: ya`,\n"
"   balasan ini WAJIB menyinggung decknya, dan langkah 7 dilewati.",
"SM-6 padatkan langkah 8")

nodes["AI Agent"]["parameters"]["options"]["systemMessage"] = _sm


# ====================================================================
# Simpan
# ====================================================================
with open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

with open(PROMPT_OUT, "w", encoding="utf-8") as f:
    f.write(_sm[1:] if _sm.startswith("=") else _sm)

print("=" * 72)
print("PATCH 2026-09-05 SELESAI")
print("=" * 72)
for i, j in enumerate(jejak, 1):
    print("  %2d. %s" % (i, j))
print()
print("  system message: %d -> %d karakter (%+d)" % (_panjang_awal, len(_sm), len(_sm) - _panjang_awal))
print("  keluaran: %s" % os.path.basename(DST))
print("  prompt  : %s" % os.path.basename(PROMPT_OUT))
