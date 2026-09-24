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
const isNewUser = preprocess?.isNewUser || false;

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

// ── TAG: [FACTS kelas="..."] + MERGE kelas_anak (union, anti-overwrite) ──
// AI (yang paham "kls 12"/"kls vii") mengekstrak kelas; digabung dgn deteksi
// regex (cadangan) + nilai lama DB (TTL-aware dari Cek_user_status). Union +
// dedup -> tidak menimpa anak lain. Program DITURUNKAN dari kelas (bukan AI).
const KELAS_WL   = ['SD 1','SD 2','SD 3','SD 4','SD 5','SD 6','SMP 1','SMP 2','SMP 3','SMA 10/11','SMA 12'];
const KELAS_PROG = { 'SD 1':'','SD 2':'','SD 3':'','SD 4':'','SD 5':'','SD 6':'Junior','SMP 1':'Junior','SMP 2':'Intermediate','SMP 3':'Intermediate','SMA 12':'Seniors','SMA 10/11':'' };
const PROG_ORDER = ['Junior','Intermediate','Seniors'];
const toLabel = (s) => {
  const t = String(s || '').toUpperCase().replace(/\s+/g, ' ').trim();
  return KELAS_WL.find(w => w.toUpperCase() === t) || null;
};

let aiFactsKelas = [];
const factsMatch = aiOutput.match(/\[\s*FACTS\b[^\]]*\bkelas\s*=\s*"([^"]*)"[^\]]*\]/i);
if (factsMatch && factsMatch[1]) {
  aiFactsKelas = factsMatch[1].split(',').map(s => s.trim()).filter(Boolean);
  console.log('🏷️ FACTS kelas dari AI:', aiFactsKelas);
}

const regexGrades = Array.isArray(preprocess && preprocess.grades) ? preprocess.grades : [];
let existingFreshRaw = '';
try { existingFreshRaw = String($('Cek_user_status').first().json.kelas_anak_db || ''); } catch (e) {}
const existingFresh = existingFreshRaw.split(',').map(s => s.trim()).filter(Boolean);

const mergedSet = [];
for (const c of [...aiFactsKelas, ...regexGrades, ...existingFresh]) {
  const lab = toLabel(c);
  if (lab && !mergedSet.includes(lab)) mergedSet.push(lab);
}
const mergedArr     = KELAS_WL.filter(w => mergedSet.includes(w)); // urut kanonik
const mergedKelas   = mergedArr.join(', ');
const progSet       = [...new Set(mergedArr.map(g => KELAS_PROG[g]).filter(Boolean))];
const mergedProgram = PROG_ORDER.filter(p => progSet.includes(p)).join(', ');
const existingCanon = KELAS_WL.filter(w => existingFresh.map(toLabel).includes(w)).join(', ');
const kelasChanged  = mergedKelas !== '' && mergedKelas !== existingCanon;
if (kelasChanged) console.log(`📝 kelas_anak: "${existingCanon}" -> "${mergedKelas}" | program: "${mergedProgram}"`);


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

// ── CLEAN OUTPUT (hapus semua tag sistem) ──────────────────────
let cleanOutput = aiOutput
  .replace(/\[\s*SEND_GFORM\s*(?::[^\]]*)?\]/gi, '')
  .replace(/\[MOCK_INTERVIEW_BOOKING\].*?\[\/MOCK_INTERVIEW_BOOKING\]/gs, '')
  .replace(/\[PENDAFTARAN\].*?\[\/PENDAFTARAN\]/gs, '')
  .replace(/\[DATA_COMPLETE\].*?\[\/DATA_COMPLETE\]/gs, '')
  .replace(/\[UNKNOWN\]/g, '')
  .replace(/\[\s*USER[_\s]?STATUS\s*:\s*[^\]]*\]/gi, '')
  .replace(/\[\s*FACTS\b[^\]]*\]/gi, '')
  .replace(/\[TALK_TO_SAM\]/g, '');

// ── SIMPAN VERSI SEBELUM FILTER INTERNAL (guard anti-kosong) ──
const preInternalStrip = cleanOutput;

// ── HAPUS KALIMAT PROSES INTERNAL ───────────────────────────
// V4 FIX: daftar keyword DIPERSEMPIT ke frasa yang benar-benar
// membocorkan proses internal (selalu menyebut sumber data).
// Frasa percakapan normal ("saya cek", "saya lihat", "dari data")
// DIHAPUS dari daftar — dulu menyebabkan balasan valid 1 kalimat
// terhapus habis dan user menerima "Maaf, terjadi kesalahan".
const internalKeywords = [
  'berdasarkan faq',
  'berdasarkan data',
  'menurut data',
  'dari faq',
  'dari sheet',
  'dari referensi',
  'data terverifikasi',
  'faq relevan',
  'faq yang tersedia',
  'data yang tersedia',
  'saya cek data',
  'saya cek faq',
  'saya cek sheet',
  'saya cek di',
  'cek di sheet',
  'cek di database',
  'ambil data dari',
];
const keywordPattern = internalKeywords.join('|');
const internalRegex = new RegExp(`^\\s*([^.!?]*?(${keywordPattern})[^.!?]*[.!?]\\s*)`, 'i');
cleanOutput = cleanOutput.replace(internalRegex, '');

// Hapus juga kalimat yang diawali dengan kata-kata tersebut (tanpa titik)
const startPattern = new RegExp(`^\\s*(${keywordPattern}).*?(\\n|\\.|$)`, 'i');
cleanOutput = cleanOutput.replace(startPattern, '');

// Jaga-jaga: buang baris pertama jika terindikasi
const lines = cleanOutput.split('\n');
if (lines.length > 1) {
  const firstLine = lines[0].toLowerCase();
  if (internalKeywords.some(kw => firstLine.includes(kw))) {
    lines.shift();
    cleanOutput = lines.join('\n');
  }
}

// Kalimat pembuka "Berdasarkan/Menurut/Dari + data/faq/sheet/referensi ..."
cleanOutput = cleanOutput.replace(/^\s*(Berdasarkan|Menurut|Dari)\s+(data|faq|sheet|referensi)[^.!?]*[.!?]\s*/i, '');

// Potong teks sebelum ": " — hanya jika kalimat DIAWALI frasa proses internal
const colonMatch = cleanOutput.match(/^\s*(Berdasarkan|Menurut|Dari)\s+(data|faq|sheet|referensi)[^:]*:\s*(.+)/is);
if (colonMatch && colonMatch[3] && colonMatch[3].trim().length > 0) {
  cleanOutput = colonMatch[3].trim();
}

// ── V4 GUARD ANTI-KOSONG ──────────────────────────────────────
// Kalau filter internal menghapus SEMUA teks padahal AI punya
// jawaban, kembalikan versi sebelum filter. Pesan error hanya
// untuk kasus AI benar-benar tidak menghasilkan output.
if (!cleanOutput.trim() && preInternalStrip.trim()) {
  // Coba selamatkan isi setelah titik dua ("Berdasarkan FAQ ...: <isi>")
  const rescue = preInternalStrip.match(/^\s*[^:.!?\n]{0,80}(?:data|faq|sheet|referensi)[^:.!?\n]{0,80}:\s*(.+)/is);
  if (rescue && rescue[1] && rescue[1].trim()) {
    console.warn('🛡️ GUARD: ambil isi setelah frasa internal.');
    cleanOutput = rescue[1].trim();
  } else {
    console.warn('🛡️ GUARD: filter internal mengosongkan output — pakai versi asli.');
    cleanOutput = preInternalStrip;
  }
}

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

// Safety net register netral: buang vokatif yang lolos dari prompt
cleanOutput = cleanOutput
  .replace(/(^|\n)\s*(Om\s*\/?\s*Tante|Bapak\s*\/?\s*Ibu|Pak\s*\/?\s*Bu|Ayah\s*\/?\s*Bunda)\s*,\s*/gi, '$1')
  .replace(/\s*\b(Om\s*\/?\s*Tante|Bapak\s*\/?\s*Ibu|Pak\s*\/?\s*Bu|Ayah\s*\/?\s*Bunda)\b\s*/gi, ' ')
  .replace(/\s{2,}/g, ' ')
  .replace(/\s+,/g, ',')
  .replace(/,\s*,/g, ',')
  .replace(/(^|\n)\s*,\s*/g, '$1')
  .trim();

cleanOutput = cleanOutput.replace(/(^|\n)([a-z])/g, (m, p1, p2) => p1 + p2.toUpperCase());

// ── FALLBACK: jika cleanOutput tetap kosong (AI tidak menghasilkan output) ──
if (!cleanOutput || cleanOutput.trim() === '') {
  console.warn('⚠️ cleanOutput kosong! Menggunakan fallback.');
  if (isUnknown) {
    cleanOutput = 'Maaf yaa, untuk pertanyaan ini saya belum punya jawabannya. Nanti saya cari tahu dan kabari lewat sini ya!';
  } else {
    cleanOutput = 'Maaf, terjadi kesalahan. Coba tanyakan ulang yaa.';
  }
}

// ── RESOLVE & INJECT GFORM LINK (inline, data-driven) ───────────
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
    console.warn('⚠️ SEND_GFORM aktif tapi link tidak ditemukan di LINKS. linkName=', gformLinkName || '(kosong)');
  }
}

// ── LOGGING ───────────────────────────────────────────────────
if (isSendGForm)   console.log('📋 SEND_GFORM tag detected');
if (isMockBooking) console.log('📅 MOCK_INTERVIEW_BOOKING detected:', JSON.stringify(mockBookingData));
if (isUnknown)     console.log('❓ UNKNOWN tag detected');

// ── RETURN ──────────────────────────────────────────────────
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
    isTalkToSam,
    nama:    pendaftaranData.nama    || dataComplete.nama    || mockBookingData.nama || '',
    program: pendaftaranData.program || dataComplete.program || 'Mock Interview',
    needs_unknown: isUnknown ? 'true' : 'false',
    can_record_to_sheet: isMockBooking || isPendaftaran || isDataComplete,
    original_message: originalMessage,
    is_new_user: isNewUser,
    kelas_anak_merged: mergedKelas,
    program_interest_merged: mergedProgram,
    kelas_changed: kelasChanged,
  }
}];

