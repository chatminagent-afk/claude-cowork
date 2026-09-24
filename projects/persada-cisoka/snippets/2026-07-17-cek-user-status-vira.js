// ====================================================================
// CEK_USER_STATUS — gate HITL post-debounce + gabung MSG_BUFFER +
// siapkan SYSTEM_DATA (intro user baru, unit/budget tersimpan).
// Perubahan 2026-07-17: (1) INTRO "Saya VIRA" -> "Saya Vira",
// (2) inject TANGGAL_SEKARANG (WIB) ke [SYSTEM_DATA] — system prompt
//     # SURVEY versi baru merujuk field ini utk hitung tanggal survey,
//     mencegah halusinasi tanggal ("senin depan" tanpa tahu hari ini).
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

// Tanggal & jam sekarang dlm WIB — sumber kebenaran tanggal utk AI.
// Format sama dgn yang divalidasi Process All (validateSurveySlot).
const nowWIB = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta' }));
const pad2 = n => String(n).padStart(2, '0');
const HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
const tanggalSekarang = `${nowWIB.getFullYear()}-${pad2(nowWIB.getMonth() + 1)}-${pad2(nowWIB.getDate())}`;
const hariSekarang = HARI[nowWIB.getDay()];
const jamSekarang = `${pad2(nowWIB.getHours())}:${pad2(nowWIB.getMinutes())}`;

const INTRO = 'Haloo, terima kasih sudah menghubungi Persada Cisoka Residence yaa. Saya Vira, siap bantu info seputar unit, harga, KPR, sampai jadwal survey ke lokasi.';

const aiSystemData = `[SYSTEM_DATA]
USER_WA: ${resolvedKey}
IS_NEW_USER: ${isNewUser}
UNIT_INTEREST: ${unitInterest || 'UNKNOWN'}
BUDGET_RANGE: ${budgetRange || 'UNKNOWN'}
TANGGAL_SEKARANG: ${tanggalSekarang} (${hariSekarang}) ${jamSekarang} WIB

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
