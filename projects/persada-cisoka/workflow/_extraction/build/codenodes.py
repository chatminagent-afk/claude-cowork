# -*- coding: utf-8 -*-
# Semua jsCode untuk code node PCR (modifikasi + baru). Dipakai oleh assemble.py.
# Raw strings supaya backslash regex JS tidak diinterpretasi Python.

BOOTSTRAP_CONFIG = r'''// ============================================================
// BOOTSTRAP CONFIG (satu-satunya titik edit manual per klien)
// Ganti SHEET_ID ke Sheet ID spreadsheet "Persada_Cisoka_Database".
// ============================================================
const SHEET_ID = 'PASTE_PCR_GOOGLE_SHEET_ID_HERE';   // <-- EDIT INI
const wh = $input.first() ? $input.first().json : {};
return [{ json: { ...wh, sheet_id: SHEET_ID } }];
'''

PARSE_CONFIG = r'''// ============================================================
// PARSE CONFIG (ENGINE) — baca tab CONFIG (key|value) jadi objek config.
// Nilai list/JSON ditulis sbg JSON string di sel value.
// ============================================================
const rows = $('Read CONFIG').all().map(i => i.json);
const sheetId = $('Bootstrap Config').first().json.sheet_id || '';
const raw = {};
for (const r of rows) {
  const k = String(r.key ?? r.Key ?? r.KEY ?? '').trim();
  if (!k) continue;
  raw[k] = (r.value ?? r.Value ?? r.VALUE ?? '');
}
const str = (k, def='') => { const v = raw[k]; return (v===undefined||v===null||String(v).trim()==='') ? def : String(v).trim(); };
const num = (k, def) => { const s = str(k,''); if (s==='') return def; const n = Number(s); return Number.isFinite(n)?n:def; };
const bool = (k, def=false) => { const v = str(k,'').toLowerCase(); if (v==='') return def; return ['true','yes','y','on','1','aktif','ya'].includes(v); };
const jsonArr = (k) => { try { const v = str(k,''); if (!v) return []; const p = JSON.parse(v); return Array.isArray(p) ? p : []; } catch(e){ return []; } };

const config = {
  sheet_id: sheetId,
  client_name: str('client_name', 'Persada Cisoka Residence'),
  bot_name: str('bot_name', 'VIRA'),
  bot_language: str('bot_language', 'id'),
  system_prompt: str('system_prompt', ''),
  admin_phone: str('admin_phone', ''),
  admin_phone_display: str('admin_phone_display', ''),
  field_team_phone: (() => {
    const a = jsonArr('field_team_phone');
    if (a.length) return a.map(x => String(x).replace(/\D/g,'')).filter(Boolean);
    const s = str('field_team_phone','');
    return s ? [s.replace(/\D/g,'')].filter(Boolean) : [];
  })(),
  media_team_phone: (() => {
    const a = jsonArr('media_team_phone');
    if (a.length) return a.map(x => String(x).replace(/\D/g,'')).filter(Boolean);
    const s = str('media_team_phone','');
    return s ? [s.replace(/\D/g,'')].filter(Boolean) : [];
  })(),
  brochure_url: str('brochure_url', ''),
  media_catalog: jsonArr('media_catalog'),
  survey_slots: jsonArr('survey_slots'),
  survey_open_hour: num('survey_open_hour', 8),
  survey_close_hour: num('survey_close_hour', 17),
  followup_max: num('followup_max', 3),
  followup_interval_hours: num('followup_interval_hours', 24),
  followup_open_hour: num('followup_open_hour', 9),
  followup_close_hour: num('followup_close_hour', 18),
  followup_templates: jsonArr('followup_templates'),
  lead_source_map: jsonArr('lead_source_map'),
  whitelist_enabled: bool('whitelist_enabled', false),
  whitelist_numbers: jsonArr('whitelist_numbers').map(x => String(x).replace(/\D/g,'')),
  rate_limit_max: num('rate_limit_max', 5),
  rate_limit_window_sec: num('rate_limit_window_sec', 60),
  debounce_seconds: num('debounce_seconds', 60),
  // Kredensial Kirimi utk endpoint multipart send-message-file (upload binary).
  // Custom-auth n8n TIDAK reliabel meng-inject body ke multipart/form-data,
  // jadi user_code/secret/device_id di-supply sbg field form via CONFIG sheet.
  // Node teks (JSON body) tetap pakai credential httpCustomAuth.
  kirimi_user_code: str('kirimi_user_code', ''),
  kirimi_secret: str('kirimi_secret', ''),
  kirimi_device_id: str('kirimi_device_id', ''),
};
const passthrough = $('Bootstrap Config').first() ? $('Bootstrap Config').first().json : {};
return [{ json: { ...passthrough, config } }];
'''

RESOLVE_USER_ROW = r'''// ====================================================================
// RESOLVE USER ROW (fondasi identitas)
// No WA = kunci PRIMER, lid = backup. TIDAK PERNAH fallback rows[0].
// ====================================================================
const cc = $('Chat Counter').first().json;
const digits = v => String(v ?? '').replace(/\D/g, '');
const phone = digits(cc.user_phone);
const lid = digits(cc.user_lid);

if (!phone && !lid) {
  throw new Error('Identitas user kosong (phone & lid tidak ada) - payload webhook tidak dikenal: ' + JSON.stringify(cc.body?.from ?? null));
}

let rows = [];
try {
  rows = $('Read User STATS').all().map(i => i.json).filter(r => r && Object.keys(r).length > 0);
} catch (e) { console.warn('Read User STATS tidak terbaca:', e.message); }

let row = null;
if (phone) row = rows.find(r => digits(r['No WA']) === phone) || null;
if (!row && lid) {
  row = rows.find(r => digits(r['lid']) === lid) || rows.find(r => digits(r['No WA']) === lid) || null;
}

const resolvedKey = row ? String(row['No WA']).trim() : (phone || lid);
const greetingSent = row ? String(row['greeting_sent'] || '').trim().toUpperCase() : '';
console.log('resolved_key=' + resolvedKey + ' | row_found=' + (!!row));

return [{
  json: {
    ...cc,
    resolved_key: resolvedKey,
    row_found: !!row,
    bot_mode: row ? String(row['bot_mode'] || '').trim().toUpperCase() : '',
    greeting_sent: greetingSent,
    is_new_user: !row || greetingSent !== 'Y',
    buffer_done_ts: Number(row ? (row['buffer_done_ts'] || 0) : 0) || 0,
    unit_interest: row ? String(row['unit_interest'] || '').trim() : '',
    unit_interest_ts: Number(row ? (row['unit_interest_ts'] || 0) : 0) || 0,
    budget_range: row ? String(row['budget_range'] || '').trim() : '',
    budget_range_ts: Number(row ? (row['budget_range_ts'] || 0) : 0) || 0,
    lead_source_db: row ? String(row['lead_source'] || '').trim() : '',
    counter_db: Number(row ? (row['Counter'] || 0) : 0) || 0
  }
}];
'''

CEK_USER_STATUS = r'''// ====================================================================
// CEK_USER_STATUS — gate HITL post-debounce + gabung MSG_BUFFER +
// siapkan SYSTEM_DATA (intro user baru, unit/budget tersimpan).
// ====================================================================
const cc = $('Chat Counter').first().json;
const resolve = $('Resolve User Row').first().json;
const resolvedKey = resolve.resolved_key;

const debounceItem = $('Re-Read STATS Debounce').first();
const debounceRow = (debounceItem && debounceItem.json) ? debounceItem.json : {};
const botModeNow = String(debounceRow['bot_mode'] || '').trim().toUpperCase();
if (botModeNow === 'OFF') {
  console.log('HITL (post-debounce): bot_mode OFF — berhenti, admin handle manual.');
  return [];
}

const doneTs = Number(debounceRow['buffer_done_ts'] || 0) || 0;
const myTs = Number(cc.process_start_ts) || 0;
let bufRows = [];
try {
  bufRows = $('Read MSG_BUFFER').all().map(i => i.json).filter(r => r && r.message !== undefined && r.message !== null);
} catch (e) { console.warn('Read MSG_BUFFER tidak terbaca:', e.message); }

const MAX_AGE_MS = 30 * 60 * 1000;
const msgs = bufRows
  .map(r => ({ ts: Number(r.ts) || 0, message: String(r.message ?? '').trim() }))
  .filter(r => r.ts > doneTs && r.ts <= myTs && (myTs - r.ts) < MAX_AGE_MS && r.message !== '')
  .sort((a, b) => a.ts - b.ts)
  .map(r => r.message);

const userMessage = msgs.length ? msgs.join('\n') : (cc.original_message || '');

const greetingSent = String(debounceRow['greeting_sent'] || resolve.greeting_sent || '').trim().toUpperCase();
const isNewUser = greetingSent !== 'Y';

const TTL_S = 60 * 86400;
const nowS = Math.floor(Date.now() / 1000);
const uiTs = Number(debounceRow['unit_interest_ts'] || resolve.unit_interest_ts || 0) || 0;
const uiFresh = uiTs > 0 && (nowS - uiTs) <= TTL_S;
const unitInterest = uiFresh ? String(debounceRow['unit_interest'] || resolve.unit_interest || '').trim() : '';
const brTs = Number(debounceRow['budget_range_ts'] || resolve.budget_range_ts || 0) || 0;
const brFresh = brTs > 0 && (nowS - brTs) <= TTL_S;
const budgetRange = brFresh ? String(debounceRow['budget_range'] || resolve.budget_range || '').trim() : '';

const INTRO = 'Haloo, terima kasih sudah menghubungi Persada Cisoka Residence yaa. Saya VIRA, siap bantu info seputar unit, harga, KPR, sampai jadwal survey ke lokasi.';

const aiSystemData = `[SYSTEM_DATA]
USER_WA: ${resolvedKey}
IS_NEW_USER: ${isNewUser}
UNIT_INTEREST: ${unitInterest || 'UNKNOWN'}
BUDGET_RANGE: ${budgetRange || 'UNKNOWN'}

CRITICAL INSTRUCTION:
${isNewUser
  ? `USER BARU. Baris pertama balasan WAJIB intro ini PERSIS (jangan diubah/diringkas): "${INTRO}" Setelah intro, di pesan yang sama langsung jawab pertanyaan user kalau ada. Kalau user hanya menyapa, cukup intro saja.`
  : 'User lama. JANGAN kirim intro/perkenalan lagi, lanjutkan percakapan secara natural.'}

[USER QUERY]
${userMessage}`;

return [{
  json: {
    ...cc,
    resolved_key: resolvedKey,
    ai_input_text: aiSystemData,
    user_message_final: userMessage,
    is_new_user: isNewUser,
    unit_interest_db: unitInterest,
    budget_range_db: budgetRange,
    buffer_done_ts_old: doneTs
  }
}];
'''

DETECT_LEAD_SOURCE = r'''// ====================================================================
// DETECT LEAD SOURCE (BARU) — deteksi sumber traffic dari pesan pertama.
// Rule-based murah; default "Organik". Tulis sekali (preserve first-touch).
// ====================================================================
const pre = $('Cek_user_status').first().json;
const resolve = $('Resolve User Row').first().json;
const cfg = (() => { try { return $('Parse Config').first().json.config || {}; } catch(e){ return {}; } })();
const firstMsg = String(pre.user_message_final || pre.original_message || '').toLowerCase();

const DEFAULT_MAP = [
  { source:'Instagram', keywords:['instagram','ig','insta','dari ig','lihat di ig','story ig'] },
  { source:'Facebook',  keywords:['facebook','fb','dari fb','lihat di fb','marketplace'] },
  { source:'Google',    keywords:['google','search','nyari di google','gmaps','maps'] },
  { source:'TikTok',    keywords:['tiktok','tt','dari tiktok'] },
  { source:'WhatsApp',  keywords:['broadcast','wa blast','katalog wa'] },
];
const MAP = (Array.isArray(cfg.lead_source_map) && cfg.lead_source_map.length) ? cfg.lead_source_map : DEFAULT_MAP;

let detected = '';
for (const m of MAP) {
  const kws = (m.keywords || []);
  if (kws.some(k => firstMsg.includes(String(k).toLowerCase()))) { detected = m.source; break; }
}
if (!detected) detected = 'Organik';

const existing = String(resolve.lead_source_db || '').trim();
const finalSource = existing || detected;   // preserve sumber pertama

return [{ json: { ...pre, lead_source_detected: detected, lead_source_final: finalSource } }];
'''

PREPROCESS = r'''// ============================================
// PREPROCESS - CONTEXT DETECTION (domain properti PCR)
// Deteksi tipe unit, budget, dan intent (harga/KPR/lokasi/legalitas/survey/media).
// Pertahankan mekanisme: [SYSTEM_DATA] + [CONTEXT] + [USER QUERY] utk AI Agent.
// ============================================
const json = $input.item.json;
const fullMessage = json.ai_input_text || json.message || json.text || '';

let actualUserMessage = '';
if (fullMessage.includes('[USER QUERY]')) {
  actualUserMessage = (fullMessage.split('[USER QUERY]')[1] || '').trim();
} else {
  actualUserMessage = String(fullMessage).trim();
}

let isNewUser = false, unitInterestDB = '', budgetRangeDB = '';
if (fullMessage.includes('[SYSTEM_DATA]')) {
  const m = fullMessage.match(/IS_NEW_USER:\s*(\w+)/i); if (m) isNewUser = m[1].toLowerCase() === 'true';
  const u = fullMessage.match(/UNIT_INTEREST:\s*([^\n]+)/i); if (u) { const v = u[1].trim(); if (v && v.toUpperCase() !== 'UNKNOWN') unitInterestDB = v; }
  const b = fullMessage.match(/BUDGET_RANGE:\s*([^\n]+)/i); if (b) { const v = b[1].trim(); if (v && v.toUpperCase() !== 'UNKNOWN') budgetRangeDB = v; }
}

const message = actualUserMessage.toLowerCase();
const userPhone = json.user_wa || json.from || 'unknown';

// deteksi tipe unit (mis. "tipe 36", "tipe 36/72")
let units = [];
const typeRe = /tipe\s*(\d{2,3})(?:\s*\/\s*(\d{2,3}))?/gi;
let tm;
while ((tm = typeRe.exec(message)) !== null) {
  const lbl = 'Tipe ' + tm[1] + (tm[2] ? '/' + tm[2] : '');
  if (!units.includes(lbl)) units.push(lbl);
}
if (!units.length && unitInterestDB) units = unitInterestDB.split(',').map(s => s.trim()).filter(Boolean);

// budget mention (mis. "500 juta", "1.2 M")
let budgetMention = '';
const bmatch = message.match(/(\d+(?:[.,]\d+)?)\s*(jt|juta|m\b|miliar|milyar)/i);
if (bmatch) budgetMention = bmatch[0].trim();

const askingPrice = /harga|biaya|berapa|nyicil|cicil|angsuran|\bdp\b|kpr|bayar|murah|mahal|promo/i.test(message);
const askingKPR = /kpr|cicil|angsuran|\bdp\b|tenor|bunga|bank|simulasi|subsidi/i.test(message);
const askingLokasi = /lokasi|alamat|dimana|di mana|maps|arah|jalan|akses|tol|dekat|deket|stasiun/i.test(message);
const askingLegalitas = /shm|hgb|sertifikat|legalitas|imb|pbb|surat|akad|notaris|balik nama/i.test(message);
const askingFasilitas = /fasilitas|keamanan|cctv|masjid|taman|kolam|security|one gate|cluster/i.test(message);
const wantsSurvey = /survey|survei|kunjungan|lihat lokasi|liat lokasi|liat unit|lihat unit|ke lokasi|datang|show ?unit|kunjung/i.test(message);
const wantsMedia = /brosur|siteplan|site plan|denah|katalog|gambar|foto|price ?list/i.test(message);
const discussingUnit = /unit|tipe|rumah|cluster|kavling|hook|ready|indent/i.test(message) || units.length > 0;

let aiContext = '';
if (units.length) aiContext += `Unit yang diminati user: ${units.join(', ')}. Fokus rekomendasi ke tipe itu. `;
else if (budgetMention) aiContext += `User menyebut kisaran budget ${budgetMention}. Arahkan ke tipe yang sesuai budget dari DATA. `;
if (askingKPR) aiContext += `User menanyakan KPR/cicilan. Jawab dari DATA (Skema KPR), jangan mengarang nominal/bank. `;
if (wantsSurvey) aiContext += `User berminat survey ke lokasi. Kalau sudah jelas tanggal & jam, pasang tag [SCHEDULE_SURVEY]. Kalau belum, tawarkan slot dari DATA/CONFIG. `;
if (wantsMedia) aiContext += `User minta brosur/denah/siteplan. Kalau tersedia di katalog, pasang [SEND_MEDIA: <key>]. `;
if (askingLegalitas) aiContext += `Pertanyaan legalitas: jawab hanya yang tertulis di DATA, selebihnya eskalasi atau [UNKNOWN]. `;

let systemDataBlock = '';
if (fullMessage.includes('[USER QUERY]')) systemDataBlock = fullMessage.split('[USER QUERY]')[0].trim();
let enhancedInput = '';
if (systemDataBlock) enhancedInput += systemDataBlock + `\n\n`;
if (aiContext.trim()) enhancedInput += `[CONTEXT: ${aiContext.trim()}]\n\n`;
enhancedInput += `[USER QUERY]\n${actualUserMessage}`;

return {
  userPhone,
  actualUserMessage,
  fullMessage,
  messageLower: message,
  isNewUser,
  unitInterestDB,
  budgetRangeDB,
  units,
  budgetMention,
  askingPrice,
  askingKPR,
  askingLokasi,
  askingLegalitas,
  askingFasilitas,
  wantsSurvey,
  wantsMedia,
  discussingUnit,
  aiContext: aiContext.trim(),
  ai_input_text: enhancedInput
};
'''

FAQ_RETRIEVE = r'''// ===== CONTEXT RETRIEVE (PCR) =====
// data_context dari PRODUK (unit/harga/KPR) + LINGKUNGAN + LINKS. FAQ lexical.
try {
  const pre = $('Preprocess - Context Detection').first().json;
  const query = pre.actualUserMessage || '';
  const flags = {
    askingPrice: !!pre.askingPrice, askingKPR: !!pre.askingKPR, askingLokasi: !!pre.askingLokasi,
    askingFasilitas: !!pre.askingFasilitas, askingLegalitas: !!pre.askingLegalitas,
    discussingUnit: !!pre.discussingUnit, wantsSurvey: !!pre.wantsSurvey,
  };
  const grab = (node) => { try { return $(node).all().map(i => i.json).filter(Boolean); } catch (e) { return []; } };
  const val = (row, ...keys) => { for (const k of keys) { for (const rk of Object.keys(row)) { if (rk.toLowerCase().trim() === k.toLowerCase().trim() || rk.toLowerCase().startsWith(k.toLowerCase())) { const v = row[rk]; if (v !== undefined && v !== null && String(v).trim() !== '') return String(v).trim(); } } } return ''; };
  const clip = (s, n) => { s = (s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n - 1) + '…' : s; };

  const parts = [];
  const prod = grab('Read PRODUK Data');
  if (prod.length) {
    // Serialisasi GENERIK: loop semua kolom PRODUK apa adanya (label = nama header).
    // Robust terhadap restrukturisasi skema (kolom baru/rename/nambah otomatis ikut,
    // tanpa hardcode 'Harga'/'Skema KPR'/dst). Kolom index/timestamp di-skip.
    const SKIP = new Set(['no', 'row_number', 'last update', 'last_update', 'tipe unit', 'tipe']);
    const lines = prod.map(r => {
      const name = val(r, 'Tipe Unit', 'Tipe') || '(unit tanpa nama)';
      const fields = [];
      for (const k of Object.keys(r)) {
        const kl = String(k).toLowerCase().trim();
        if (SKIP.has(kl)) continue;
        const raw = r[k];
        if (raw === undefined || raw === null || String(raw).trim() === '') continue;
        fields.push(`${k}=${clip(String(raw), 220)}`);
      }
      return `${name} → ${fields.join(' | ')}`;
    });
    parts.push('UNIT / HARGA / KPR / SPESIFIKASI (data resmi; tipe, harga, cicilan, skema, atau promo yang TIDAK tertulis di sini = jangan dikarang):\n' + lines.join('\n'));
  }
  if (flags.askingLokasi || flags.askingFasilitas || flags.askingLegalitas) {
    const ling = grab('Read LINGKUNGAN Data');
    if (ling.length) parts.push('LINGKUNGAN & LEGALITAS:\n' + ling.map(r => `${val(r, 'Aspek')}: ${clip(val(r, 'Detail'), 160)}`).join('\n'));
  }
  const links = grab('Read LINKS Data');
  if (links.length) {
    const activeRows = links.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(val(r, 'Status')));
    const active = activeRows.map(r => { const nm = val(r, 'Nama Link'); const ds = clip(val(r, 'Deskripsi'), 80); return nm ? (ds ? `${nm} — ${ds}` : nm) : ''; }).filter(Boolean);
    if (active.length) {
      const sample = val(activeRows[0], 'Nama Link') || 'brosur';
      parts.push('LINK/MEDIA AKTIF (saat [SEND_MEDIA] sebut key PERSIS, mis. [SEND_MEDIA: ' + sample + ']):\n- ' + active.join('\n- '));
    }
  }
  const data_context = parts.join('\n\n');

  // FAQ lexical retrieval
  const faq = grab('Read FAQ').filter(r => r.Pertanyaan && r.Jawaban);
  const STOP = new Set(['yang','untuk','dan','di','ke','dari','itu','ini','apa','apakah','bisa','kah','ya','yaa','kak','min','dong','sih','kok','aja','ada','gimana','bagaimana','saya','aku','nya','kalau','atau','juga','sudah','belum','mau','dengan','pada','adalah','tolong','mohon','halo','hai','permisi','terima','kasih','sama','buat','soal','tentang','nih','ga','gak','engga','tidak','dll','yg','utk']);
  const GROUPS = [
    ['harga','biaya','bayar','cicil','cicilan','angsuran','dp','kpr','tenor','bunga','subsidi','promo','murah','mahal'],
    ['unit','tipe','rumah','kavling','cluster','hook','bangunan'],
    ['luas','tanah','bangunan','ukuran'],
    ['survey','survei','kunjungan','datang'],
    ['lokasi','alamat','maps','akses','tol','jalan','stasiun','dekat'],
    ['legalitas','shm','hgb','sertifikat','imb','pbb','akad','notaris'],
    ['fasilitas','keamanan','cctv','masjid','taman','kolam','security','gate'],
    ['ready','indent','stok','tersedia','sisa'],
    ['bank','kredit','approve','pengajuan','simulasi'],
    ['brosur','siteplan','denah','katalog','gambar','foto'],
  ];
  const SYN = {}; for (const g of GROUPS) for (const w of g) SYN[w] = g[0];
  const stem = (t) => { let w = t; for (const s of ['nya','kah','lah','kan','an','i']) if (w.length - s.length >= 4 && w.endsWith(s)) { w = w.slice(0, -s.length); break; } for (const p of ['meng','meny','mem','men','peng','peny','pem','pen','ber','ter','di','se','ke','me','pe']) if (w.length - p.length >= 4 && w.startsWith(p)) { w = w.slice(p.length); break; } return w; };
  const tok = (s) => (s || '').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, ' ').split(/\s+/).filter(Boolean).filter(t => !STOP.has(t)).map(t => { const a = SYN[t]; if (a) return a; const st = stem(t); return SYN[st] || st; }).filter(t => t.length >= 2 && !STOP.has(t));
  const docs = faq.map(r => ({ row: r, toks: tok(r.Pertanyaan) }));
  const Nn = docs.length, df = {};
  for (const dd of docs) for (const t of new Set(dd.toks)) df[t] = (df[t] || 0) + 1;
  const idf = (t) => Math.log((Nn + 1) / ((df[t] || 0) + 1)) + 1;
  const boost = {};
  if (flags.askingPrice || flags.askingKPR) boost['Harga & KPR'] = 1.25;
  if (flags.askingLokasi) boost['Lokasi'] = 1.2;
  if (flags.wantsSurvey) boost['Survey'] = 1.2;
  const qToks = [...new Set(tok(query))];
  let faq_context = '';
  if (qToks.length && docs.length) {
    const scored = docs.map(dd => { const dset = new Set(dd.toks); let s = 0, m = 0; for (const t of qToks) if (dset.has(t)) { s += idf(t); m++; } s *= (boost[dd.row.Kategori] || 1.0); return { row: dd.row, score: s, matched: m }; }).sort((a, b) => b.score - a.score);
    const top = scored[0];
    const FLOOR = 2.5, needCov = qToks.length >= 3 ? 2 : 1;
    if (top.score >= FLOOR && top.matched >= needCov) {
      const kept = scored.filter(x => x.score >= 0.45 * top.score && x.matched >= 1).slice(0, 4);
      faq_context = kept.map(x => `Q: ${x.row.Pertanyaan}\nA: ${x.row.Jawaban}`).join('\n\n');
    }
  }

  return [{ json: { ...pre, faq_context, data_context }, pairedItem: { item: 0 } }];
} catch (e) {
  const pre = ($('Preprocess - Context Detection').first() || { json: {} }).json || {};
  return [{ json: { ...pre, faq_context: '', data_context: '', faq_error: String(e) }, pairedItem: { item: 0 } }];
}
'''

PROCESS_ALL = r'''const item = $input.first();
let aiOutput = '';
if (item?.json?.content && Array.isArray(item.json.content) && item.json.content.length > 0) {
  aiOutput = item.json.content[0].text || '';
} else {
  aiOutput = item?.json?.output || item?.json?.text || '';
}
console.log('AI Output preview:', aiOutput.substring(0, 300));

const chatCounter = $('Chat Counter').first().json;
const preprocess = $('Preprocess - Context Detection').first().json;
const cfg = (() => { try { return $('Parse Config').first().json.config || {}; } catch(e){ return {}; } })();
const originalMessage = chatCounter.original_message || '';
const isNewUser = preprocess?.isNewUser || false;

// ── VALIDASI SLOT SURVEY (deterministik di Code node) ──
function validateSurveySlot(tglRaw, jamRaw) {
  const now = new Date();
  const openH = Number(cfg.survey_open_hour ?? 8);
  const closeH = Number(cfg.survey_close_hour ?? 17);
  let d = null;
  const iso = String(tglRaw).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  const dmy = String(tglRaw).match(/^(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?$/);
  if (iso) d = new Date(+iso[1], +iso[2] - 1, +iso[3]);
  else if (dmy) d = new Date(dmy[3] ? (dmy[3].length === 2 ? 2000 + +dmy[3] : +dmy[3]) : now.getFullYear(), +dmy[2] - 1, +dmy[1]);
  if (!d || isNaN(d)) return { ok: false, reason: 'tanggal tidak terbaca' };
  const jm = String(jamRaw).match(/(\d{1,2})[:.](\d{2})/);
  if (!jm) return { ok: false, reason: 'jam tidak terbaca' };
  const hh = +jm[1], mm = +jm[2];
  d.setHours(hh, mm, 0, 0);
  const todayWIB = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Jakarta' })); todayWIB.setHours(0, 0, 0, 0);
  if (d < todayWIB) return { ok: false, reason: 'tanggal sudah lewat' };
  if (hh < openH || hh >= closeH) return { ok: false, reason: 'di luar jam operasional' };
  const pad = n => String(n).padStart(2, '0');
  return { ok: true, tanggal: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`, jam: `${pad(hh)}:${pad(mm)}` };
}

// ── TAG: [SCHEDULE_SURVEY] ──
let isScheduleSurvey = false, surveyData = {};
const svMatch = aiOutput.match(/\[\s*SCHEDULE_SURVEY\b([^\]]*)\]/i);
if (svMatch && svMatch[1]) {
  const c = svMatch[1];
  const tgl = (c.match(/tanggal\s*=\s*"([^"]*)"/i) || [])[1] || '';
  const jam = (c.match(/jam\s*=\s*"([^"]*)"/i) || [])[1] || '';
  const unit = (c.match(/unit\s*=\s*"([^"]*)"/i) || [])[1] || '';
  const v = validateSurveySlot(tgl, jam);
  if (v.ok) { isScheduleSurvey = true; surveyData = { tanggal: v.tanggal, jam: v.jam, unit: String(unit).trim() }; console.log('SCHEDULE_SURVEY valid', JSON.stringify(surveyData)); }
  else console.warn('SCHEDULE_SURVEY ditolak validasi:', v.reason);
}

// ── TAG: [REQUEST_CALL] ──
let isRequestCall = aiOutput.includes('[REQUEST_CALL]');
if (!isRequestCall) {
  const low = aiOutput.toLowerCase();
  const callPatterns = ['nomor yang bisa dihubungi','bisa ditelpon','bisa ditelepon','nomor telepon admin','hubungi langsung','minta nomornya','nomor cs','nomor marketing'];
  if (callPatterns.some(p => low.includes(p))) isRequestCall = true;
}

// ── TAG: [TALK_TO_ADMIN] ──
let isTalkToAdmin = aiOutput.includes('[TALK_TO_ADMIN]');
if (!isTalkToAdmin) {
  const low = aiOutput.toLowerCase();
  const p = ['sambungkan ke tim marketing','saya sambungkan ke tim','biar tim marketing','ke tim marketing kami'];
  if (p.some(x => low.includes(x))) isTalkToAdmin = true;
}

// ── TAG: [SEND_MEDIA: key] ──
let isSendMedia = false, mediaKey = '';
const mediaMatch = aiOutput.match(/\[\s*SEND_MEDIA\s*(?::\s*([^\]]*))?\]/i);
if (mediaMatch) { isSendMedia = true; mediaKey = (mediaMatch[1] || 'brosur').trim().toLowerCase(); }
if (!isSendMedia) {
  const low = aiOutput.toLowerCase();
  const patt = ['kirim brosur','saya kirimkan brosur','ini brosurnya','brosurnya saya kirim','saya kirim siteplan','denahnya saya kirim','saya kirim denah','ini siteplannya'];
  if (patt.some(p => low.includes(p))) { isSendMedia = true; mediaKey = 'brosur'; }
}

// ── TAG: [UNKNOWN] ──
let isUnknown = aiOutput.includes('[UNKNOWN]');

// ── TAG: [FACTS unit="..." budget="..."] + merge persist ──
let factUnit = '', factBudget = '';
const factsMatch = aiOutput.match(/\[\s*FACTS\b([^\]]*)\]/i);
if (factsMatch && factsMatch[1]) {
  factUnit = (factsMatch[1].match(/unit\s*=\s*"([^"]*)"/i) || [])[1] || '';
  factBudget = (factsMatch[1].match(/budget\s*=\s*"([^"]*)"/i) || [])[1] || '';
}
let existingUnit = ''; try { existingUnit = String($('Cek_user_status').first().json.unit_interest_db || ''); } catch (e) {}
let existingBudget = ''; try { existingBudget = String($('Cek_user_status').first().json.budget_range_db || ''); } catch (e) {}
const regexUnits = Array.isArray(preprocess && preprocess.units) ? preprocess.units : [];
const unitSet = [];
for (const u of [factUnit, ...regexUnits, existingUnit].join(',').split(',').map(s => s.trim()).filter(Boolean)) { if (!unitSet.includes(u)) unitSet.push(u); }
const unitMerged = unitSet.join(', ');
const budgetMerged = (factBudget || (preprocess && preprocess.budgetMention) || existingBudget || '').trim();
const unitChanged = unitMerged !== '' && unitMerged !== existingUnit;
const budgetChanged = budgetMerged !== '' && budgetMerged !== existingBudget;

// ── CLEAN OUTPUT (buang semua tag) ──
let cleanOutput = aiOutput
  .replace(/\[\s*SEND_MEDIA\s*(?::[^\]]*)?\]/gi, '')
  .replace(/\[\s*SCHEDULE_SURVEY\b[^\]]*\]/gi, '')
  .replace(/\[REQUEST_CALL\]/gi, '')
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

// clean markdown (mask url dulu)
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
    ? 'Maaf yaa, untuk yang ini saya belum ada infonya. Nanti saya cek dulu dan kabari lagi yaa.'
    : 'Maaf, ada kendala sebentar. Boleh diketik ulang yaa.';
}

// ── REQUEST_CALL: sisipkan admin_phone_display ──
if (isRequestCall) {
  const disp = (cfg.admin_phone_display) || '';
  if (disp && !cleanOutput.includes(disp)) cleanOutput = `${cleanOutput}\n\nBisa langsung telepon/WA ke ${disp} yaa.`;
}

// ── RESOLVE MEDIA URL + caption dari LINKS ──
// Native send bila key ada di katalog LINKS (URL publik). Bila TIDAK ada
// (katalog belum diisi / key tak dikenal) -> fallback NOTIFIKASI MANUAL ke
// tim telemarketer (Aar & Aqsa) supaya mereka kirim file-nya manual.
let mediaUrl = '', mediaCaption = '';
let isMediaManual = false, mediaRequestSummary = '';
if (isSendMedia) {
  let linkRows = [];
  try { linkRows = $('Read LINKS Data').all().map(i => i.json); } catch (e) {}
  const norm = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const active = linkRows.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(String(r['Status'] || '')));
  const row = active.find(r => norm(r['Nama Link']) === mediaKey) || active.find(r => norm(r['Nama Link']).includes(mediaKey));
  if (row && row['URL']) {
    // Katalog terisi -> kirim native lewat Kirimi send-message-file (download binary dulu)
    mediaUrl = String(row['URL']).trim();
    mediaCaption = String(row['Caption'] || row['Deskripsi'] || '').trim() || 'Ini file yang diminta yaa.';
  } else {
    // Katalog kosong / key tak dikenal -> jalur manual ke tim
    console.warn('SEND_MEDIA key tidak ada di LINKS, fallback manual:', mediaKey);
    isSendMedia = false;
    isMediaManual = true;
    const userMsg = (preprocess && preprocess.actualUserMessage) || originalMessage || '';
    mediaRequestSummary = (mediaKey ? ('key="' + mediaKey + '" ') : '') + (userMsg ? ('| pesan user: ' + String(userMsg).slice(0, 300)) : '');
  }
}

return [{
  json: {
    ...chatCounter, ...preprocess, ...item.json,
    cleanOutput,
    isScheduleSurvey, surveyData,
    isRequestCall,
    isTalkToAdmin,
    isSendMedia, mediaUrl, mediaCaption, mediaKey,
    isMediaManual, mediaRequestSummary,
    isUnknown,
    needs_unknown: isUnknown ? 'true' : 'false',
    original_message: originalMessage,
    is_new_user: isNewUser,
    unit_interest_merged: unitMerged,
    budget_range_merged: budgetMerged,
    unit_changed: unitChanged,
    budget_changed: budgetChanged
  }
}];
'''

COLLECT_HANDOVER = r'''// COLLECT HANDOVER CONTEXT — STATS (fakta persisten) + MSG_BUFFER (transkrip sesi).
const digits = v => String(v ?? '').replace(/\D/g, '');
const key = $('Resolve User Row').first().json.resolved_key;

let statsRow = {};
try { statsRow = $('Read User STATS').all().map(i => i.json).find(r => digits(r['No WA']) === digits(key)) || {}; } catch (e) {}

let transcript = '';
try {
  const buf = $('Read MSG_BUFFER').all().map(i => i.json)
    .filter(r => digits(r['no_wa']) === digits(key))
    .sort((a, b) => Number(a.ts) - Number(b.ts));
  transcript = buf.map(r => `User: ${r.message}`).join('\n');
} catch (e) {}

const pa = $('Process All').item.json;
const sd = pa.surveyData || {};
const profil = {
  nama: statsRow['Nama'] || $('Chat Counter').first().json.user_name || '',
  no_wa: key,
  pesan_pertama: statsRow['Pesan Pertama'] || '',
  unit_interest: pa.unit_interest_merged || statsRow['unit_interest'] || '',
  budget_range: pa.budget_range_merged || statsRow['budget_range'] || '',
  survey: [sd.tanggal, sd.jam, 'SCHEDULED'].filter(Boolean).join(' '),
  lead_source: $('Detect Lead Source').first().json.lead_source_final || statsRow['lead_source'] || '',
  jumlah_chat: statsRow['Counter'] || '',
};

return [{ json: {
  handover_profil: profil,
  handover_transcript: transcript || '(transkrip sesi tidak tersedia)',
  handover_trigger: 'DELEGATION'
}}];
'''

FORMAT_HANDOVER = r'''// FORMAT HANDOVER MESSAGE — bungkus ringkasan LLM (atau fallback deterministik).
let summary = '';
try { const s = $('Summarize Handover').first().json; summary = (s.content && s.content[0] && s.content[0].text) || s.text || ''; } catch (e) {}

const ctx = $('Collect Handover Context').first().json;
const p = ctx.handover_profil || {};
const trigger = ctx.handover_trigger || 'DELEGATION';

if (!summary || !summary.trim()) {
  summary = `PROFIL KLIEN: ${p.nama || '-'}, ${p.no_wa || '-'}, sumber ${p.lead_source || 'belum diketahui'}
TIPE UNIT DIMINATI: ${p.unit_interest || 'belum diketahui'}
BUDGET/KPR: ${p.budget_range || 'belum dibahas'}
STATUS SURVEY: ${p.survey || 'belum dijadwalkan'}`;
}

const header = {
  DELEGATION: '🏠 [PCR] SURVEY BARU — HANDOVER KE TIM LAPANGAN',
  HITL: '🙋 [PCR] AMBIL ALIH CHAT',
  CALL: '📞 [PCR] MINTA DITELEPON',
}[trigger] || '📋 [PCR] HANDOVER';

const message = `${header}

${summary}

— Chat: wa.me/${p.no_wa}`;

const cfg = $('Parse Config').first().json.config;
let tujuan = (trigger === 'DELEGATION')
  ? (Array.isArray(cfg.field_team_phone) ? cfg.field_team_phone : [cfg.field_team_phone])
  : [cfg.admin_phone];
tujuan = (tujuan || []).filter(Boolean);
if (!tujuan.length) { console.warn('Tidak ada nomor tujuan handover (field_team_phone kosong).'); return []; }

return tujuan.map(no => ({ json: { phone: String(no), message } }));
'''

SUMMARIZE_PROMPT = r'''=Kamu asisten internal yang merangkum percakapan calon pembeli properti untuk tim telemarketer/admin Persada Cisoka Residence. Buat ringkasan SINGKAT, PADAT, FAKTUAL dalam Bahasa Indonesia. Hanya gunakan DATA PROFIL dan TRANSKRIP di bawah. JANGAN mengarang, tulis "belum diketahui" bila kosong. Tanpa basa-basi.

Keluarkan PERSIS format berikut:
PROFIL KLIEN: <nama, no WA, sumber>
KEBUTUHAN: <apa yang dicari, 1-2 kalimat>
TIPE UNIT DIMINATI: <tipe, atau belum diketahui>
BUDGET/KPR: <kisaran/skema, atau belum dibahas>
STATUS SURVEY: <SCHEDULED tgl jam / belum dijadwalkan>
POIN PENTING: <objections/kendala/urgensi, maks 3 poin>
NEXT ACTION: <1 kalimat konkret>

DATA PROFIL:
Nama: {{ $json.handover_profil.nama }}
No WA: {{ $json.handover_profil.no_wa }}
Sumber: {{ $json.handover_profil.lead_source }}
Unit diminati (sistem): {{ $json.handover_profil.unit_interest }}
Budget (sistem): {{ $json.handover_profil.budget_range }}
Status survey (sistem): {{ $json.handover_profil.survey }}
Jumlah chat: {{ $json.handover_profil.jumlah_chat }}

TRANSKRIP SESI:
{{ $json.handover_transcript }}'''

FORMAT_MEDIA_NOTIF = r'''// FORMAT MEDIA NOTIF — notifikasi manual ke tim telemarketer (Aar & Aqsa).
// Dipakai saat user minta gambar/video/brosur TAPI file belum ada di katalog
// LINKS (native send tak bisa). Tim kirim file-nya manual ke user.
// Mengembalikan 1 item per nomor tim (loop kirim di Notify Media Team).
const pa = $('Process All').item.json;
const cc = $('Chat Counter').first().json;
const key = $('Resolve User Row').first().json.resolved_key || cc.user_wa || '';
const nama = cc.user_name || '';
const mediaKey = pa.mediaKey || '';
const summary = pa.mediaRequestSummary || '';

const message = `📸 [PCR] PERMINTAAN MEDIA - KIRIM MANUAL
User: ${key}
Nama: ${nama || '(belum ada nama)'}
Diminta: ${mediaKey || 'foto/video'}
Detail: ${summary || '(tidak ada detail)'}

User menunggu file dikirim. Balas langsung ke user yaa.
Chat: wa.me/${String(key).replace(/\D/g, '')}`;

const cfg = $('Parse Config').first().json.config;
let tujuan = Array.isArray(cfg.media_team_phone) ? cfg.media_team_phone : [cfg.media_team_phone];
tujuan = (tujuan || []).filter(Boolean);
if (!tujuan.length) { console.warn('media_team_phone kosong — tidak ada tujuan notif media manual.'); return []; }

return tujuan.map(no => ({ json: { phone: String(no), message } }));
'''

# QA hardening 2026-07-16: Kirimi bisa balas HTTP 200 dengan success:false (dibuktikan
# live test). Flag eksplisit false wajib dianggap gagal; klausa lama
# (message && message !== 'error') meloloskan {success:false, message:"duplicate"}.
CHECK_API_RESPONSE = r"""// Cek apakah Kirimi API sukses
const input = $input.first();
const responseData = input.json;

// Flag eksplisit false = gagal, apapun isi field lain (Kirimi bisa HTTP 200 + success:false)
const explicitFail = responseData.success === false || responseData.status === false;

const isSuccess = !explicitFail && (
  responseData.status === true ||
  responseData.success === true ||
  (responseData.data && responseData.data.id) ||
  (responseData.message && responseData.message !== 'error')
);

if (!isSuccess) {
  console.log('X Kirimi API Response Error:', JSON.stringify(responseData));
  throw new Error('Kirimi API gagal: ' + JSON.stringify(responseData));
}

return [input];
"""
