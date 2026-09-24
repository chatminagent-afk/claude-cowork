const item = $input.first();

// Ambil AI output dari Anthropic Chat Model
let aiOutput = '';
if (item?.json?.content && Array.isArray(item.json.content) && item.json.content.length > 0) {
  aiOutput = item.json.content[0].text || '';
} else {
  aiOutput = item?.json?.output || item?.json?.text || '';
}

console.log('AI Output preview:', aiOutput.substring(0, 300));

// Ambil data konteks dari node Chat Counter dan Preprocess
const chatCounter = $('Chat Counter').first().json;
const preprocess = $('Preprocess - Context Detection').first().json;

// Context data
const originalMessage = chatCounter.original_message || '';
const isNewUser = preprocess?.isNewUser || chatCounter?.is_new_user || false;
const shouldAskStatus = preprocess?.should_ask_status || false;
const userWa = chatCounter.user_wa || '';
const userName = chatCounter.user_name || '';

// ── TAG: [USER_STATUS] ──────────────────────────────────────
let userStatus = '';
const statusMatch = aiOutput.match(/\[\s*USER[_\s]?STATUS\s*:\s*(PARENT|STUDENT)\s*\]/i);
if (statusMatch && statusMatch[1]) {
  userStatus = statusMatch[1];
  console.log('👤 USER_STATUS detected:', userStatus);
}

// ── FALLBACK: Detect from conversation if tag missing ────────
if (!userStatus && isNewUser) {
  const userMessage = originalMessage.toLowerCase() || '';
  const aiResponse = aiOutput.toLowerCase();
  
  const isStatusConversation = 
    aiResponse.includes('terima kasih sudah memberi tahu') ||
    aiResponse.includes('baik om/tante') ||
    aiResponse.includes('baik! terima kasih') ||
    (aiResponse.includes('om/tante') && userMessage.length < 50) ||
    (aiResponse.includes('kamu') && userMessage.length < 50);
  
  if (isStatusConversation) {
    if (userMessage.includes('orang tua') || 
        userMessage.includes('ortu') || 
        userMessage.includes('ayah') || 
        userMessage.includes('ibu') ||
        userMessage.includes('bapak') ||
        userMessage.includes('mama') ||
        userMessage.includes('papa') ||
        userMessage.includes('anak saya') ||
        userMessage.includes('anak kami')) {
      userStatus = 'PARENT';
      console.log('⚠️ FALLBACK: Detected PARENT from user message');
    }
    else if (userMessage.includes('murid') || 
             userMessage.includes('saya sendiri') ||
             userMessage.includes('saya yang') ||
             userMessage.includes('calon muridnya') ||
             (userMessage.includes('saya') && !userMessage.includes('anak'))) {
      userStatus = 'STUDENT';
      console.log('⚠️ FALLBACK: Detected STUDENT from user message');
    }
  }
}

// ── TAG: [SEND_GFORM: Nama Link] ──────────────────────────────
let gformLinkName = '';
let isSendGForm = false;
const gformMatch = aiOutput.match(/\[\s*SEND_GFORM\s*(?::\s*([^\]]*))?\]/i);
if (gformMatch) {
  isSendGForm = true;
  gformLinkName = (gformMatch[1] || '').trim();
  console.log('📋 SEND_GFORM tag detected. linkName=', gformLinkName || '(kosong)');
}

if (!isSendGForm) {
  const outputLower = aiOutput.toLowerCase();
  const hasFormsUrl = aiOutput.includes('forms.gle');
  const forgotTagPatterns = [
    'link pendaftaran sudah saya kirim',
    'link pendaftaran mock interview sudah saya kirim',
    'silakan isi formnya',
    'form sudah saya kirim',
    'link pendaftarannya',
    'link pendaftaran',
    'ini linknya',
    'silakan diisi',
    'link pendaftaran mock',
    'ini link mock',
  ];
  const mentionedSendingForm = forgotTagPatterns.some(pattern =>
    outputLower.includes(pattern)
  );
  if (hasFormsUrl || mentionedSendingForm) {
    isSendGForm = true;
    const reason = hasFormsUrl ? 'forms.gle URL detected' : 'phrase pattern matched';
    console.log(`⚠️ FALLBACK: AI forgot [SEND_GFORM] tag - auto-correcting (${reason})`);
  }
}

// ── TAG: [TALK_TO_SAM] ─────────────────────────────────────────
let isTalkToSam = aiOutput.includes('[TALK_TO_SAM]');

if (!isTalkToSam) {
  const outputLower = aiOutput.toLowerCase();
  const talkToSamPatterns = [
    'sampaikan ke sam',
    'saya sampaikan ke sam',
    'dibalas langsung sama dia',
    'dibales langsung sama dia',
    'kalau dia sudah ada waktu',
  ];
  if (talkToSamPatterns.some(p => outputLower.includes(p))) {
    isTalkToSam = true;
    console.log('⚠️ FALLBACK: AI forgot [TALK_TO_SAM] tag - auto-correcting');
  }
}

// ── TAG: [MOCK_INTERVIEW_BOOKING] ─────────────────────────────
let isMockBooking = false;
let mockBookingData = {};
const mockMatch = aiOutput.match(/\[MOCK_INTERVIEW_BOOKING\](.*?)\[\/MOCK_INTERVIEW_BOOKING\]/s);
if (mockMatch && mockMatch[1]) {
  isMockBooking = true;
  const c = mockMatch[1];
  const namaM    = c.match(/Nama:([^|]+)/);
  const sesiM    = c.match(/Sesi:([^|]+)/);
  const noWaM    = c.match(/NoWA:([^|\\]]+)/);
  mockBookingData = {
    nama:  namaM ? namaM[1].trim() : '',
    sesi:  sesiM ? sesiM[1].trim() : '',
    noWA:  noWaM ? noWaM[1].trim() : '',
  };
}

// ── TAG: [UNKNOWN] ────────────────────────────────────────────
let isUnknown = aiOutput.includes('[UNKNOWN]');

// ── TAG: [PENDAFTARAN] (backward compat) ──────────────────────
let isPendaftaran = false;
let pendaftaranData = {};
const pendMatch = aiOutput.match(/\[PENDAFTARAN\](.*?)\[\/PENDAFTARAN\]/s);
if (pendMatch && pendMatch[1]) {
  isPendaftaran = true;
  const c = pendMatch[1];
  const namaM    = c.match(/Nama:([^|]+)/);
  const programM = c.match(/Program:([^|]+)/);
  const batchM   = c.match(/Batch:([^|]+)/);
  const asalM    = c.match(/Asal:([^|\\]]+)/);
  pendaftaranData = {
    nama:    namaM    ? namaM[1].trim()    : '',
    program: programM ? programM[1].trim() : '',
    batch:   batchM   ? batchM[1].trim()   : '',
    asal:    asalM    ? asalM[1].trim()    : '',
  };
}

// ── DATA_COMPLETE ──────────────────────────────────────────────
let isDataComplete = false;
let dataComplete = {};
const dcMatch = aiOutput.match(/\[DATA_COMPLETE\](.*?)\[\/DATA_COMPLETE\]/s);
if (dcMatch && dcMatch[1]) {
  isDataComplete = true;
  const c = dcMatch[1];
  const namaM    = c.match(/Nama:([^|]+)/);
  const noWaM    = c.match(/NoWA:([^|]+)/);
  const programM = c.match(/Program:([^|\\]]+)/);
  dataComplete = {
    nama:    namaM    ? namaM[1].trim() : '',
    noWA:    noWaM    ? noWaM[1].trim() : '',
    program: programM ? programM[1].trim() : '',
  };
}

// ── CLEAN OUTPUT ──────────────────────────────────────────────
let cleanOutput = aiOutput
  .replace(/\[\s*SEND_GFORM\s*(?::[^\]]*)?\]/gi, '')
  .replace(/\[MOCK_INTERVIEW_BOOKING\].*?\[\/MOCK_INTERVIEW_BOOKING\]/gs, '')
  .replace(/\[PENDAFTARAN\].*?\[\/PENDAFTARAN\]/gs, '')
  .replace(/\[DATA_COMPLETE\].*?\[\/DATA_COMPLETE\]/gs, '')
  .replace(/\[UNKNOWN\]/g, '')
  .replace(/\[\s*USER[_\s]?STATUS\s*:\s*[^\]]*\]/gi, '')
  .replace(/\[TALK_TO_SAM\]/g, '');

// ── HAPUS KALIMAT PROSES INTERNAL (FORCE) ──────────────────
// Daftar kata kunci yang menandakan proses internal
const internalKeywords = [
  'ambil data',
  'berdasarkan faq',
  'berdasarkan data',
  'dari faq',
  'dari data',
  'dari sheet',
  'dari referensi',
  'saya cek',
  'saya temukan',
  'saya ambil',
  'saya lihat',
  'menurut data',
  'faq yang tersedia',
  'data yang ada',
  'referensi yang ada',
  'sheet yang ada',
];
// Buat regex untuk mencocokkan kalimat pembuka yang mengandung keyword tersebut
const keywordPattern = internalKeywords.join('|');
const internalRegex = new RegExp(`^\\s*([^.!?]*?(${keywordPattern})[^.!?]*[.!?]\\s*)`, 'i');
cleanOutput = cleanOutput.replace(internalRegex, '');

// Hapus juga kalimat yang diawali dengan kata-kata tersebut (tanpa titik)
const startPattern = new RegExp(`^\\s*(${keywordPattern}).*?(\\n|\\.|$)`, 'i');
cleanOutput = cleanOutput.replace(startPattern, '');

// Jaga-jaga: ambil kalimat setelah baris baru jika kalimat pertama terindikasi
const lines = cleanOutput.split('\n');
if (lines.length > 1) {
  const firstLine = lines[0].toLowerCase();
  if (internalKeywords.some(kw => firstLine.includes(kw))) {
    lines.shift(); // buang baris pertama
    cleanOutput = lines.join('\n');
  }
}

// ── TAMBAHAN: Jika masih ada kalimat yang diawali "Berdasarkan..." ──
cleanOutput = cleanOutput.replace(/^[^.!?]*?(Berdasarkan|Dari|Menurut|Saya cek|Saya temukan|Saya ambil|Data yang|FAQ yang).*?[.!?]\s*/i, '');

// ── POTONG TEKS SEBELUM ": " — hanya jika kalimat DIAWALI frasa proses internal ──
const colonMatch = cleanOutput.match(/^\s*(Berdasarkan|Menurut|Dari)\s+(data|faq|sheet|referensi)[^:]*:\s*(.+)/is);
if (colonMatch && colonMatch[3] && colonMatch[3].trim().length > 0) {
  cleanOutput = colonMatch[3].trim(); // hanya potong kalau hasilnya tidak kosong
}

// Trim akhir
cleanOutput = cleanOutput.trim();

// ── CLEAN MARKDOWN ──────────────────────────────────────────
const urlRegex = /https?:\/\/[^\s)]+/g;
const maskedUrls = [];
cleanOutput = cleanOutput.replace(urlRegex, (match) => {
  maskedUrls.push(match);
  return `\x00URL${maskedUrls.length - 1}\x00`;
});

cleanOutput = cleanOutput
  .replace(/\*\*([^*]+)\*\*/g, '$1')
  .replace(/\*([^*]+)\*/g, '$1')
  .replace(/_([^_]+)_/g, '$1')
  .replace(/~~([^~]+)~~/g, '$1')
  .replace(/`([^`]+)`/g, '$1')
  .replace(/[\*_~`]/g, '');

cleanOutput = cleanOutput
  .replace(/(\d)\s*[—–]\s*(\d)/g, '$1-$2')
  .replace(/\s*[—–]\s*/g, ', ')
  .replace(/\s*;\s*/g, ', ')
  .replace(/\s{2,}/g, ' ')
  .replace(/\s+([,.])/g, '$1')
  .replace(/,\s*,/g, ',')
  .trim();

cleanOutput = cleanOutput.replace(
  /\x00URL(\d+)\x00/g,
  (_, idx) => maskedUrls[parseInt(idx)]
);

cleanOutput = cleanOutput
  .replace(/(^|\n)\s*(Om\s*\/?\s*Tante|Bapak\s*\/?\s*Ibu|Pak\s*\/?\s*Bu|Ayah\s*\/?\s*Bunda)\s*,\s*/gi, '$1')
  .replace(/\s*\b(Om\s*\/?\s*Tante|Bapak\s*\/?\s*Ibu|Pak\s*\/?\s*Bu|Ayah\s*\/?\s*Bunda)\b\s*/gi, ' ')
  .replace(/\s{2,}/g, ' ')
  .replace(/\s+,/g, ',')
  .replace(/,\s*,/g, ',')
  .replace(/(^|\n)\s*,\s*/g, '$1')
  .trim();

cleanOutput = cleanOutput.replace(/(^|\n)([a-z])/g, (m, p1, p2) => p1 + p2.toUpperCase());

// ── FALLBACK: jika cleanOutput kosong ──
if (!cleanOutput || cleanOutput.trim() === '') {
  console.warn('⚠️ cleanOutput kosong! Menggunakan fallback.');
  if (isUnknown) {
    cleanOutput = 'Maaf yaa, untuk pertanyaan ini saya belum punya jawabannya. Nanti saya cek dan kabari lewat sini ya!';
  } else {
    cleanOutput = 'Maaf, terjadi kesalahan. Coba tanyakan ulang yaa.';
  }
}

// ── RESOLVE & INJECT GFORM LINK (inline, data-driven — pola V2) ───
// Jika ada tag [SEND_GFORM: Nama Link], cari URL asli di sheet LINKS lalu
// sisipkan ke cleanOutput supaya terkirim dalam 1 pesan (tanpa node terpisah).
if (isSendGForm) {
  let linkRows = [];
  try {
    linkRows = $('Read LINKS Data').all().map(i => i.json);
  } catch (e) {
    console.warn('⚠️ Tidak bisa baca node Read LINKS Data:', e.message);
  }

  const normL = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const activeRows = linkRows.filter(r => /aktif|active|on|ya/i.test(String(r['Status'] || '')));

  let match = null;
  const rq = normL(gformLinkName);
  if (rq) {
    match = activeRows.find(r => normL(r['Nama Link']) === rq)
         || activeRows.find(r => { const n = normL(r['Nama Link']); return n && (n.includes(rq) || rq.includes(n)); });
  }
  // AI tidak menyebut nama link -> default ke pendaftaran batch reguler
  if (!match && !rq) {
    match = activeRows.find(r => /pendaftaran batch/i.test(String(r['Nama Link'] || '')))
         || activeRows.find(r => /gform|pendaftaran/i.test(String(r['Nama Link'] || '')));
  }

 if (match && match['URL']) {
    gformLinkName = match['Nama Link'];
    const url = String(match['URL']).trim();

    // ── Deteksi link WhatsApp Channel/komunitas → cukup kirim URL, tanpa imbuhan "ngobrol sama Sam" ──
    const linkMeta = `${match['Nama Link'] || ''} ${match['Deskripsi'] || ''}`.toLowerCase();
    const isWaChannel =
      /whatsapp\.com\/channel\//i.test(url) ||
      /chat\.whatsapp\.com\//i.test(url) ||
      /channel|komunitas|wa\s*channel/i.test(linkMeta);

    if (!cleanOutput.includes(url)) {
      cleanOutput = isWaChannel
        ? `${cleanOutput}\n\n👉 ${url}`
        : `${cleanOutput}\n\n👉 ${url}\n\nKalau ada yang masih kurang jelas, bisa ngobrol langsung sama Sam yaa. tinggal ketik "mau ngomong sama Sam".`;
    }
    console.log('✅ Link injected inline:', match['Nama Link'], url, isWaChannel ? '(WA channel - tanpa imbuhan)' : '');
  } else {
    // Tidak ketemu: jangan kirim link asal-asalan; pertahankan teks AI, log utk audit.
    console.warn('⚠️ SEND_GFORM aktif tapi link tidak ditemukan di LINKS. linkName=', gformLinkName || '(kosong)');
  }
}

// ── LOGGING ───────────────────────────────────────────────────
if (isSendGForm)   console.log('📋 SEND_GFORM tag detected');
if (isMockBooking) console.log('📅 MOCK_INTERVIEW_BOOKING detected:', JSON.stringify(mockBookingData));
if (isUnknown)     console.log('❓ UNKNOWN tag detected');
if (userStatus)    console.log('👤 USER_STATUS detected:', userStatus);

// ── RETURN ──────────────────────────────────────────────────
// ── GUARD: jangan tandai UNKNOWN kalau turn ini bukan pertanyaan ──
   // Kasus: user hanya mengungkap status (mis. "saya org tuanya") -> output memuat [USER_STATUS]
   const isQuestionTurn = !!(preprocess?.askingPrice || preprocess?.askingBatch
     || preprocess?.wantsToRegister || preprocess?.discussingProgram);
   if (isUnknown && userStatus && !isQuestionTurn) {
     console.log('🛡️ GUARD: [UNKNOWN] dibatalkan — turn balasan status, bukan pertanyaan.');
     isUnknown = false;
   }
return [{
  json: {
    ...chatCounter,
    ...preprocess,
    ...item.json, // overwrite dengan data terbaru jika ada konflik
    cleanOutput,
    isSendGForm,
    gformLinkName,
    isMockBooking,
    mockBookingData,
    isUnknown,
    isPendaftaran,
    pendaftaranData,
    isDataComplete,
    dataComplete,
    userStatus,
    isTalkToSam,
    should_ask_status: shouldAskStatus,
    nama:    pendaftaranData.nama    || dataComplete.nama    || mockBookingData.nama || '',
    program: pendaftaranData.program || dataComplete.program || 'Mock Interview',
    needs_unknown: isUnknown ? 'true' : 'false',
    needs_status_update: userStatus !== '',
    can_record_to_sheet: isMockBooking || isPendaftaran || isDataComplete,
    original_message: originalMessage,
    is_new_user: isNewUser,
  }
}];
