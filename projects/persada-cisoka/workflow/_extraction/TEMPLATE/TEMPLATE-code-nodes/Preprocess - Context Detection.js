// ============================================================
// PREPROCESS - CONTEXT DETECTION  (ENGINE, config-driven)
// Keyword & mapping program diambil dari tab CONFIG (Parse Config),
// jadi BISA dipakai ulang lintas klien tanpa edit kode.
// Output shape dipertahankan agar FAQ Retrieve / Process All tetap jalan.
// ============================================================
const json = $input.item.json;
const cfg = ($('Parse Config').first().json.config) || {};

const fullMessage = json.message || json.ai_input_text || json.text || json.body || '';

// 1. EXTRACT USER QUERY
let actualUserMessage = '';
if (fullMessage.includes('[USER QUERY]')) {
  const parts = fullMessage.split('[USER QUERY]');
  actualUserMessage = parts[1] ? parts[1].trim() : '';
} else {
  actualUserMessage = String(fullMessage).trim();
}

// 2. PARSE SYSTEM_DATA
let userStatusInDB = '', isNewUser = false, greetingSent = false;
if (fullMessage.includes('[SYSTEM_DATA]')) {
  const s = fullMessage.match(/USER_STATUS_IN_DB:\s*(\w+)/i); if (s) userStatusInDB = s[1];
  const n = fullMessage.match(/IS_NEW_USER:\s*(\w+)/i); if (n) isNewUser = n[1].toLowerCase() === 'true';
  const g = fullMessage.match(/GREETING_SENT:\s*(\w+)/i); if (g) greetingSent = g[1].toUpperCase() === 'YES';
}

const message = actualUserMessage.toLowerCase();
const userPhone = json.userPhone || json.from || json.phone || json.user_wa || 'unknown';

// helper: cek apakah message mengandung salah satu keyword (string biasa, case-insensitive, word-ish)
const hasAny = (arr) => Array.isArray(arr) && arr.some(k => {
  k = String(k || '').trim().toLowerCase(); if (!k) return false;
  return message.includes(k);
});

// 3. STATUS detection (config keyword lists; default fallback generik)
const parentKw  = (cfg.status_parent_keywords && cfg.status_parent_keywords.length) ? cfg.status_parent_keywords
                  : ['orang tua','ortu','ayah','ibu','bapak','mama','papa','anak saya','anak kami'];
const studentKw = (cfg.status_student_keywords && cfg.status_student_keywords.length) ? cfg.status_student_keywords
                  : ['murid','saya sendiri','saya yang mau','calon murid','anaknya','aku yang','aku sendiri','saya aja','aku aja'];
let detectedStatusFromMessage = '';
if (hasAny(parentKw)) detectedStatusFromMessage = 'PARENT';
else if (hasAny(studentKw)) detectedStatusFromMessage = 'STUDENT';

// 4. GRADE & PROGRAM (data-driven dari grade_program_map)
let grade = '', recommendedProgram = '', gradeNote = '';
for (const m of (cfg.grade_program_map || [])) {
  if (hasAny(m.keywords || [])) { grade = m.grade || ''; recommendedProgram = m.program || ''; gradeNote = m.note || ''; break; }
}

// 5. REGISTRATION INTENT
const registerKw = (cfg.register_keywords && cfg.register_keywords.length) ? cfg.register_keywords
                   : ['daftar','mau ikut','tertarik','mau coba','link pendaftaran','link form','minta link'];
const wantsToRegister = hasAny(registerKw);

// 6. OUT-OF-SCOPE
const outScopeKw = cfg.out_of_scope_keywords || [];
const outOfScope = hasAny(outScopeKw);

// 7. ANTI-LOOP ambiguous short reply
const isGreetingLike = /^(hai|halo|hi|pagi|siang|sore|malam|makasih|thanks|terima kasih|ok|oke|sip|baik|👍|🙏)/i.test(message);
const unclearReply = (actualUserMessage.trim().length <= 4) && !grade && !detectedStatusFromMessage && !isGreetingLike && !wantsToRegister;

// 8. TOPIC FLAGS
const priceKw   = (cfg.price_keywords && cfg.price_keywords.length) ? cfg.price_keywords : ['berapa','biaya','harga','bayar','mahal','murah'];
const batchKw   = (cfg.batch_keywords && cfg.batch_keywords.length) ? cfg.batch_keywords : ['batch','kapan','mulai','jadwal','pendaftaran'];
const programKw = (cfg.program_keywords && cfg.program_keywords.length) ? cfg.program_keywords : ['program','batch'];
const askingPrice = hasAny(priceKw);
const askingBatch = hasAny(batchKw);
const discussingProgram = hasAny(programKw) || (cfg.grade_program_map||[]).some(m => hasAny([(m.program||'').toLowerCase()]));

// persuasion (generik)
let persuasionMode = '';
if (/mau daftar|tertarik|boleh deh|mau coba|mau ikut|oke deh/i.test(message)) persuasionMode = 'INTERESTED';
else if (/nanti|pikir dulu|setelah ujian|belum sekarang|ragu|mikir|lihat dulu/i.test(message)) persuasionMode = 'DEFER';
else if (/\b(tf|transfer|bayar|mau bayar|sudah bayar|kirim bukti)\b/i.test(message)) persuasionMode = 'PAYMENT';

// 9. BUILD AI CONTEXT
let aiContext = '';
if (userStatusInDB === 'EMPTY' && detectedStatusFromMessage) {
  aiContext += `CRITICAL: User baru mengungkap status (${detectedStatusFromMessage}). WAJIB pasang tag [USER_STATUS:${detectedStatusFromMessage}] di PALING AWAL output. `;
  aiContext += detectedStatusFromMessage === 'PARENT'
    ? `Ke orang tua: langsung ke isi tanpa vokatif, hangat tapi sopan. `
    : `Ke murid: boleh sapa 'kamu', nada suportif. `;
} else if (userStatusInDB && userStatusInDB !== 'EMPTY') {
  aiContext += `User status: ${userStatusInDB}. `;
} else {
  aiContext += `User status belum diketahui. Tanya dulu status user sebelum menjawab pertanyaan. `;
}
if (outOfScope) aiContext += `User kemungkinan di luar target program. Sampaikan jujur belum ada yang cocok, JANGAN paksa tanya detail jenjang. `;
if (unclearReply) aiContext += `Balasan user terlalu singkat/ambigu. JANGAN ulang pertanyaan yang sama. Kalau sudah pernah tanya hal sama, tawarkan handoff: [TALK_TO_SAM]. `;
if (!outOfScope && grade && recommendedProgram) aiContext += `User di ${grade} -> arahkan ke program ${recommendedProgram}. ${gradeNote ? gradeNote + ' ' : ''}Sebut HANYA program yang cocok, jangan tawarkan tier lain kecuali user tanya. `;
else if (!outOfScope && grade && !recommendedProgram) aiContext += `User di ${grade}, tapi belum ada program yang pas. Sampaikan jujur. ${gradeNote ? gradeNote + ' ' : ''}`;
if (wantsToRegister) aiContext += `User ingin daftar -> siapkan [SEND_GFORM] HANYA jika diizinkan aturan batch. `;
if (persuasionMode === 'INTERESTED') aiContext += `User tertarik. Nada tenang, langsung ke langkah daftar tanpa berlebihan. `;
else if (persuasionMode === 'DEFER') aiContext += `User menunda. Validasi singkat, beri ruang tanpa menekan. `;
else if (persuasionMode === 'PAYMENT') aiContext += `User konfirmasi pembayaran. Balas singkat & hangat. `;

let enhancedInput = actualUserMessage;
if (aiContext.trim()) enhancedInput = `[CONTEXT: ${aiContext.trim()}]\n\n${actualUserMessage}`;

return {
  userPhone, actualUserMessage, fullMessage, messageLower: message,
  userStatusInDB, isNewUser, greetingSent, detectedStatusFromMessage,
  grade, recommendedProgram, wantsToRegister, discussingProgram,
  askingPrice, askingBatch, persuasionMode, outOfScope, unclearReply,
  aiContext: aiContext.trim(), ai_input_text: enhancedInput
};

