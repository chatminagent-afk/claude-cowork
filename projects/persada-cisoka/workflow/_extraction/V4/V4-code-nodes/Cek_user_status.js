// ====================================================================
// NODE: Cek_user_status (V4)
// Peran: gate HITL post-debounce + gabung pesan MSG_BUFFER +
//        siapkan SYSTEM_DATA (intro user baru, kelas tersimpan).
// Alur status PARENT/STUDENT sudah DIHAPUS (register netral).
// ====================================================================
const cc = $('Chat Counter').first().json;
const resolve = $('Resolve User Row').first().json;
const resolvedKey = resolve.resolved_key;

// bot_mode dicek ulang SETELAH debounce (Wait 60 detik) —
// Sam bisa set OFF kapan saja selama bot menunggu.
const debounceItem = $('Re-Read STATS Debounce').first();
const debounceRow = (debounceItem && debounceItem.json) ? debounceItem.json : {};
const botModeNow = String(debounceRow['bot_mode'] || '').trim().toUpperCase();
if (botModeNow === 'OFF') {
  console.log('👨‍💼 HITL (post-debounce): bot_mode OFF — berhenti, Sam handle manual.');
  return [];
}

// ── Gabung pesan dari MSG_BUFFER (append-only, anti lost-update) ──
// Konsumsi: ts > buffer_done_ts (watermark) dan ts <= process_start_ts saya.
const doneTs = Number(debounceRow['buffer_done_ts'] || 0) || 0;
const myTs = Number(cc.process_start_ts) || 0;
let bufRows = [];
try {
  bufRows = $('Read MSG_BUFFER').all()
    .map(i => i.json)
    .filter(r => r && r.message !== undefined && r.message !== null);
} catch (e) {
  console.warn('⚠️ Read MSG_BUFFER tidak terbaca:', e.message);
}
// Batas kedaluwarsa: pesan lebih tua dari 30 menit tidak ikut digabung
// (mis. pesan yang sempat ter-buffer lalu ditangani manual oleh Sam saat bot OFF).
const MAX_AGE_MS = 30 * 60 * 1000;
const msgs = bufRows
  .map(r => ({ ts: Number(r.ts) || 0, message: String(r.message ?? '').trim() }))
  .filter(r => r.ts > doneTs && r.ts <= myTs && (myTs - r.ts) < MAX_AGE_MS && r.message !== '')
  .sort((a, b) => a.ts - b.ts)
  .map(r => r.message);

// Fallback aman: kalau buffer kosong (mis. append gagal), pakai pesan asli.
const userMessage = msgs.length ? msgs.join('\n') : (cc.original_message || '');
console.log(`📨 userMessage final ke AI (${msgs.length} pesan digabung):\n${userMessage}`);

// ── User baru? (greeting_sent belum Y) ──
const greetingSent = String(debounceRow['greeting_sent'] || resolve.greeting_sent || '').trim().toUpperCase();
const isNewUser = greetingSent !== 'Y';

// ── Fakta persisten (tahan restart n8n / reset memory) ──
// TTL 60 hari: kelas berubah tiap tahun ajaran, jangan injeksi data basi.
const KELAS_TTL_S = 60 * 86400;
const kelasTs = Number(debounceRow['kelas_anak_ts'] || resolve.kelas_anak_ts || 0) || 0;
const kelasFresh = kelasTs > 0 && (Math.floor(Date.now() / 1000) - kelasTs) <= KELAS_TTL_S;
const kelasAnak = kelasFresh ? String(debounceRow['kelas_anak'] || resolve.kelas_anak || '').trim() : '';
const programInterest = kelasFresh ? String(debounceRow['program_interest'] || resolve.program_interest || '').trim() : '';
if (kelasTs && !kelasFresh) console.log('⏳ kelas_anak kedaluwarsa (>60 hari) — tidak diinjeksi.');

const INTRO = 'Haloo thank you sudah contact TheScholars.id yaa. Saya Sam versi AI yaa, saya siap bantu untuk jawab pertanyaan yang ada mengenai program kita dan scholarships ke Singapore.';

const aiSystemData = `[SYSTEM_DATA]
USER_WA: ${resolvedKey}
IS_NEW_USER: ${isNewUser}
KELAS_ANAK: ${kelasAnak || 'UNKNOWN'}
PROGRAM_INTEREST: ${programInterest || 'UNKNOWN'}

CRITICAL INSTRUCTION:
${isNewUser
  ? `USER BARU. Baris pertama balasan WAJIB intro ini PERSIS (jangan diubah/diringkas): "${INTRO}" Setelah intro, di pesan yang sama langsung jawab pertanyaan user kalau ada. Kalau user hanya menyapa, cukup intro saja.`
  : 'User lama. JANGAN kirim intro/perkenalan lagi, lanjutkan percakapan secara natural. Jangan reset percakapan dari awal.'}

[USER QUERY]
${userMessage}`;

return [{
  json: {
    ...cc,
    resolved_key: resolvedKey,
    ai_input_text: aiSystemData,
    user_message_final: userMessage,
    is_new_user: isNewUser,
    kelas_anak_db: kelasAnak,
    program_interest_db: programInterest,
    buffer_done_ts_old: doneTs
  }
}];

