// ============================================
// PREPROCESS - CONTEXT DETECTION (V4)
// - Deteksi status PARENT/STUDENT DIHAPUS (register netral).
// - Deteksi kelas MULTI-VALUE: bisa menangkap >1 kelas dalam satu
//   pesan (kasus orang tua dengan beberapa anak). Disimpan sebagai
//   daftar "SMP 1, SD 6".
// - Dukung jenjang Singapura/internasional (Primary/Sec) & angka
//   Romawi; fallback kelas tersimpan dari DB (kelas_anak, TTL di
//   Cek_user_status).
// ============================================

const json = $input.item.json;

// Get the full message (includes SYSTEM_DATA + user query)
const fullMessage = json.message || json.ai_input_text || json.text || json.body || '';

// ============================================
// 1. EXTRACT USER QUERY
// ============================================
let actualUserMessage = '';
if (fullMessage.includes('[USER QUERY]')) {
  const parts = fullMessage.split('[USER QUERY]');
  actualUserMessage = parts[1] ? parts[1].trim() : '';
} else {
  actualUserMessage = fullMessage.trim();
}

// ============================================
// 2. PARSE SYSTEM_DATA
// ============================================
let isNewUser = false;
let kelasAnakDB = '';
let programInterestDB = '';

if (fullMessage.includes('[SYSTEM_DATA]')) {
  const newUserMatch = fullMessage.match(/IS_NEW_USER:\s*(\w+)/i);
  if (newUserMatch) isNewUser = newUserMatch[1].toLowerCase() === 'true';

  const kelasMatch = fullMessage.match(/KELAS_ANAK:\s*([^\n]+)/i);
  if (kelasMatch) {
    const v = kelasMatch[1].trim();
    if (v && v.toUpperCase() !== 'UNKNOWN') kelasAnakDB = v;
  }
  const progMatch = fullMessage.match(/PROGRAM_INTEREST:\s*([^\n]+)/i);
  if (progMatch) {
    const v = progMatch[1].trim();
    if (v && v.toUpperCase() !== 'UNKNOWN') programInterestDB = v;
  }
}

// ============================================
// 3. PROCESS MESSAGE
// ============================================
const message = actualUserMessage.toLowerCase().replace(/\bkls\b/g, 'kelas').replace(/\bklas\b/g, 'kelas');
const userPhone = json.userPhone || json.from || json.phone || json.user_wa || 'unknown';

// ============================================
// 4. DETECT GRADE(S) & PROGRAM(S) — MULTI-VALUE
//    Semua pola discan (bukan berhenti di match pertama) supaya
//    ">1 anak" dalam satu pesan tertangkap semua.
//    Seniors KHUSUS kelas 12. SMA 10/11 -> belum ada program.
// ============================================
const GRADE_PATTERNS = [
  // Jenjang internasional/Singapura (intl=true)
  [/\b(?:primary|pri)\s*\.?\s*6\b|\bp6\b/i,        'SD 6',      'Junior',       true],
  [/\b(?:sec|secondary)\s*\.?\s*1\b/i,             'SMP 1',     'Junior',       true],
  [/\b(?:sec|secondary)\s*\.?\s*2\b/i,             'SMP 2',     'Intermediate', true],
  [/\b(?:sec|secondary)\s*\.?\s*3\b/i,             'SMP 3',     'Intermediate', true],
  [/\b(?:sec|secondary)\s*\.?\s*4\b/i,             'SMA 10/11', '',             true],
  // Angka Romawi (\b menjaga 'kelas x' tidak match di 'kelas xii')
  [/kelas\s*xii\b/i,                               'SMA 12',    'Seniors',      false],
  [/kelas\s*xi\b/i,                                'SMA 10/11', '',             false],
  [/kelas\s*x\b/i,                                 'SMA 10/11', '',             false],
  [/kelas\s*ix\b/i,                               'SMP 3',     'Intermediate', false],
  [/kelas\s*viii\b/i,                             'SMP 2',     'Intermediate', false],
  [/kelas\s*vii\b/i,                              'SMP 1',     'Junior',       false],
  [/kelas\s*vi\b/i,                               'SD 6',      'Junior',       false],
  // Pola Indonesia
  [/sd 6|kelas 6 sd|kelas 6(?!\s*smp)/i,           'SD 6',      'Junior',       false],
  [/smp 1|kelas 1 smp|kelas 7\b/i,                 'SMP 1',     'Junior',       false],
  [/smp 2|kelas 2 smp|kelas 8\b/i,                 'SMP 2',     'Intermediate', false],
  [/smp 3|kelas 3 smp|kelas 9\b/i,                 'SMP 3',     'Intermediate', false],
  [/sma 3|kelas 3 sma|kelas 12\b/i,                'SMA 12',    'Seniors',      false],
  [/sma 1|sma 2|kelas 1 sma|kelas 2 sma|kelas 10\b|kelas 11\b/i, 'SMA 10/11', '', false],
];

const PROGRAM_OF = { 'SD 6': 'Junior', 'SMP 1': 'Junior', 'SMP 2': 'Intermediate', 'SMP 3': 'Intermediate', 'SMA 12': 'Seniors', 'SMA 10/11': '' };

let grades = [];
let intlSystemDetected = false;
for (const [re, label, prog, intl] of GRADE_PATTERNS) {
  if (re.test(message) && !grades.includes(label)) {
    grades.push(label);
    if (intl) intlSystemDetected = true;
  }
}
// Fallback generik SMA (kelas belum jelas) hanya kalau tidak ada match lain
let smaUnclear = false;
if (!grades.length && message.match(/sma|kelas.*sma/i)) {
  smaUnclear = true;
}

// Fallback: kelas tersimpan dari percakapan sebelumnya (DB, sudah lolos TTL)
let gradeFromDB = false;
if (!grades.length && !smaUnclear && kelasAnakDB) {
  grades = kelasAnakDB.split(',').map(s => s.trim()).filter(Boolean);
  gradeFromDB = true;
}

const programs = [...new Set(grades.map(g => PROGRAM_OF[g] || '').filter(Boolean))];
const noProgramGrades = grades.filter(g => !(PROGRAM_OF[g] || ''));

// String gabungan (dipakai untuk penyimpanan kelas_anak & kompatibilitas)
const grade = grades.join(', ');
const recommendedProgram = gradeFromDB && programInterestDB ? programInterestDB : programs.join(', ');

// ============================================
// 5. DETECT REGISTRATION INTENT
// ============================================
const wantsToRegister = message.match(/daftar|mau ikut|tertarik|mau coba|mau daftar|link pendaftaran|link form|minta link/i) !== null;

// ============================================
// 5b. DETECT OUT-OF-SCOPE USER (di luar jenjang SMP-SMA)
// ============================================
let outOfScope = false;
if (message.match(/\b(mahasiswa|semester\s*\d+|lagi kuliah|sudah kuliah|udah kuliah|sarjana|magister|fresh graduate|gap year|karyawan|pegawai|sudah lulus|udah lulus|sudah kerja|udah kerja)\b/i)) {
  outOfScope = true;
}

// ============================================
// 5c. DETECT UNCLEAR / AMBIGUOUS SHORT REPLY (anti-loop)
// ============================================
const isGreetingLike = message.match(/^(hai|halo|hi|pagi|siang|sore|malam|makasih|thanks|terima kasih|ok|oke|sip|baik|👍|🙏)/i) !== null;
const unclearReply = (actualUserMessage.trim().length <= 4) && !grades.length && !isGreetingLike && !wantsToRegister;

// ============================================
// 6. DETECT PERSUASION TRIGGERS
// ============================================
let persuasionMode = '';
// PAYMENT dicek PALING DULU: intent transfer harus menang atas 'oke deh' (INTERESTED)
// dan 'nanti' (DEFER), spt pesan "oke deh mau transfer" / "udah tf, nanti kabarin yaa".
// Catatan: kata 'bayar'/'pembayaran' telanjang SENGAJA tidak dipakai sebagai pemicu -
// itu biasanya pertanyaan harga/cicilan yang MASIH BOLEH dijawab.
if (message.match(/\b(tf|trf|transfer|mau bayar|sudah bayar|udah bayar|sdh bayar|kirim bukti|bukti transfer|bukti bayar|bukti pembayaran|rekening|no rek|norek|nomor rekening|bayar ke ?mana|kirim ke ?mana|bayarnya ke ?mana)\b/i)) {
  persuasionMode = 'PAYMENT';
} else if (message.match(/mau daftar|tertarik|boleh deh|mau coba|mau ikut|oke deh/i)) {
  persuasionMode = 'INTERESTED';
} else if (message.match(/nanti (dulu|aja|saja|lah)|nanti deh|pikir dulu|pikir-?2? dulu|pikirkan dulu|dipikir dulu|setelah ujian|belum sekarang|belum kepikiran|masih ragu|\bragu\b|mikir (dulu|lagi)|lagi mikir|dipikir-?pikir|lihat dulu|liat dulu|tunggu dulu|nunggu dulu/i)) {
  // 'nanti' TELANJANG sengaja tidak dipakai: "nanti tolong kabarin", "nanti saya tanya lagi",
  // "nanti daftar" bukan penundaan, tapi dulu semuanya terbaca DEFER lalu AI diminta
  // 'singkat & jangan menekan' sehingga pertanyaan user malah tidak terjawab.
  persuasionMode = 'DEFER';
}

// ============================================
// 7. DETECT TOPICS
// ============================================
const discussingProgram = message.match(/program|junior|intermediate|senior|batch/i) !== null;
const askingPrice = message.match(/berapa|biaya|harga|bayar|mahal|murah/i) !== null;
const askingBatch = message.match(/batch|kapan|mulai|jadwal|pendaftaran/i) !== null;

// ============================================
// 8. BUILD AI CONTEXT
//    HANYA fakta deteksi + pointer, selaras system message.
// ============================================
let aiContext = '';

if (outOfScope) {
  aiContext += `User kemungkinan di luar jenjang SMP-SMA (mahasiswa/kuliah/kerja). Sampaikan jujur program khusus siswa SMP-SMA, jadi belum ada yang cocok. JANGAN tanya kelas SMP/SMA. `;
}

if (unclearReply) {
  aiContext += `Balasan user terlalu singkat/ambigu. JANGAN ulang pertanyaan yang sama. Kalau sebelumnya sudah bertanya hal yang sama, tawarkan bantuan langsung dari Sam: [TALK_TO_SAM]. `;
}

if (intlSystemDetected) {
  aiContext += `User menyebut jenjang sistem Singapura/internasional (Primary/Sec). Ini TIDAK berarti calon murid sudah bersekolah di Singapura, banyak sekolah kurikulum internasional di Indonesia. Jangan asumsikan lokasi sekolah, dan JANGAN tanya lokasi kecuali menentukan jawaban. `;
}

if (!outOfScope && grades.length) {
  const src = gradeFromDB ? 'SUDAH DIKETAHUI dari percakapan sebelumnya' : 'disebut di pesan ini';
  if (grades.length === 1) {
    const g = grades[0];
    const p = PROGRAM_OF[g] || '';
    if (p) {
      aiContext += `Kelas calon murid ${src}: ${g} -> arahkan ke program ${p}. ${gradeFromDB ? 'JANGAN tanya kelas lagi. ' : ''}Catatan: SMP 2 = Intermediate (BUKAN Junior). Sebut HANYA program ${p}, jangan tawarkan tier program lain kecuali user tanya. `;
    } else if (g === 'SMA 10/11') {
      aiContext += `Calon murid di SMA kelas 10/11 -> belum ada program yang cocok untuk sekarang (Seniors khusus kelas 12). Sampaikan jujur dan arahkan ke opsi yang ada.${gradeFromDB ? ' Kelas sudah diketahui, JANGAN tanya kelas lagi.' : ''} `;
    }
  } else {
    // Multi-anak: sebutkan pemetaan per kelas
    const mapText = grades.map(g => `${g} -> ${PROGRAM_OF[g] || 'belum ada program yang cocok (Seniors khusus kelas 12)'}`).join('; ');
    aiContext += `User menyebut LEBIH DARI SATU kelas calon murid (kemungkinan beberapa anak), ${src}: ${mapText}. JANGAN tanya ulang kelas. Bahas program sesuai kelas masing-masing, ringkas, tanpa membandingkan tier lain di luar itu. Catatan: SMP 2 = Intermediate (BUKAN Junior). `;
  }
} else if (smaUnclear) {
  aiContext += `Calon murid SMA tapi kelas belum jelas -> tanya dulu kelas berapa (Seniors hanya untuk kelas 12). `;
}

if (wantsToRegister) {
  aiContext += `User ingin daftar -> siapkan [SEND_GFORM] HANYA jika diizinkan ATURAN BATCH (batch reguler DIBUKA, atau Mock Interview, atau Seniors). Kalau batch belum dibuka, arahkan user menunggu kabar pendaftaran. `;
}

if (persuasionMode) {
  if (persuasionMode === 'INTERESTED') {
    aiContext += `User tertarik daftar. Ikuti ATURAN BATCH. Nada tenang dan netral, langsung ke langkah daftar tanpa berlebihan. `;
  } else if (persuasionMode === 'DEFER') {
    aiContext += `User menunda. Validasi singkat dan santai, beri ruang tanpa menekan waktu. `;
  } else if (persuasionMode === 'PAYMENT') {
    aiContext += `User menyinggung pembayaran/transfer. PEMBAYARAN DITANGANI SAM MANUAL, bukan kamu. Balas PERSIS: "Baik, nanti akan dibantu cek dengan Sam yaa." lalu berhenti. DILARANG menyebut transfer/tf/rekening/bukti bayar, dilarang minta bukti, dilarang konfirmasi pembayaran diterima, dilarang pasang tag [TALK_TO_SAM]. `;
  }
}

// ============================================
// 9. BUILD ENHANCED INPUT FOR AI
// ============================================
// FIX C1: preserve the [SYSTEM_DATA] block from Cek_user_status so
// IS_NEW_USER + intro instruction survive to the AI Agent. Detection
// facts are added as an extra [CONTEXT: ...] block.
let systemDataBlock = '';
if (fullMessage.includes('[USER QUERY]')) {
  systemDataBlock = fullMessage.split('[USER QUERY]')[0].trim();
}
let enhancedInput = '';
if (systemDataBlock) enhancedInput += systemDataBlock + `\n\n`;
if (aiContext.trim()) enhancedInput += `[CONTEXT: ${aiContext.trim()}]\n\n`;
enhancedInput += `[USER QUERY]\n${actualUserMessage}`;

// ============================================
// OUTPUT
// ============================================
return {
  userPhone,
  actualUserMessage,
  fullMessage,
  messageLower: message,
  isNewUser,
  kelasAnakDB,
  programInterestDB,
  grade,
  grades,
  gradeFromDB,
  intlSystemDetected,
  recommendedProgram,
  wantsToRegister,
  discussingProgram,
  askingPrice,
  askingBatch,
  persuasionMode,
  outOfScope,
  unclearReply,
  aiContext: aiContext.trim(),
  ai_input_text: enhancedInput
};
