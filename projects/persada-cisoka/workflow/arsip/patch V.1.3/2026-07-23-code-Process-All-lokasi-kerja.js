const item = $input.first();
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

// ── HELPER TANGGAL WIB ──
const DAY_ID = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
const BULAN_ID = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
const pad = n => String(n).padStart(2, '0');
const nowWIB = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta' }));
const tglDisplay = iso => { const m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})$/); if (!m) return String(iso); const d = new Date(+m[1], +m[2]-1, +m[3]); return `${DAY_ID[d.getDay()]} ${+m[3]} ${BULAN_ID[+m[2]-1]}`; };
const contohTanggal = (() => { const d = new Date(nowWIB.getFullYear(), nowWIB.getMonth(), nowWIB.getDate() + 1); return `${DAY_ID[d.getDay()]} ${d.getDate()} ${BULAN_ID[d.getMonth()]}`; })();

// ── VALIDASI SLOT SURVEY (deterministik di Code node) ──
const openH = Number(cfg.survey_open_hour ?? 8);
const closeH = Number(cfg.survey_close_hour ?? 17);
// 🔶 harus SAMA dengan closedDays di node Preprocess
const closedDays = Array.isArray(cfg.survey_closed_days) ? cfg.survey_closed_days.map(Number) : [];

function validateSurveySlot(tglRaw, jamRaw) {
  let d = null;
  const iso = String(tglRaw).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  const dmy = String(tglRaw).match(/^(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?$/);
  if (iso) d = new Date(+iso[1], +iso[2] - 1, +iso[3]);
  else if (dmy) d = new Date(dmy[3] ? (dmy[3].length === 2 ? 2000 + +dmy[3] : +dmy[3]) : nowWIB.getFullYear(), +dmy[2] - 1, +dmy[1]);
  if (!d || isNaN(d)) return { ok: false, reason: 'tanggal tidak terbaca' };

  const jm = String(jamRaw).match(/(\d{1,2})[:.](\d{2})/);
  if (!jm) return { ok: false, reason: 'jam tidak terbaca' };
  const hh = +jm[1], mm = +jm[2];
  if (hh > 23 || mm > 59) return { ok: false, reason: 'jam tidak valid' };
  d.setHours(hh, mm, 0, 0);

  // bandingkan ke WAKTU SEKARANG WIB, bukan tengah malam.
  // (bug lama: jam yang sudah lewat hari ini tetap lolos)
  if (d.getTime() <= nowWIB.getTime()) return { ok: false, reason: 'tanggal/jam sudah lewat' };
  // jaga-jaga halusinasi tahun (mis. AI keluarkan 2025 padahal 2026)
  if (d.getFullYear() < nowWIB.getFullYear()) return { ok: false, reason: 'tahun tidak valid' };
  if (closedDays.includes(d.getDay())) return { ok: false, reason: 'hari ' + DAY_ID[d.getDay()] + ' tutup' };
  if (hh < openH || hh >= closeH) return { ok: false, reason: 'di luar jam operasional' };

  return { ok: true, tanggal: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`, jam: `${pad(hh)}:${pad(mm)}` };
}

// ── TAG: [SCHEDULE_SURVEY] (parse dulu, validasi setelah unit di-merge) ──
let isScheduleSurvey = false, surveyData = {};
let isSurveyIncomplete = false, missingSlots = [], surveyRejectReason = '';
let svTagFound = false, svTgl = '', svJam = '', svUnit = '';
const svMatch = aiOutput.match(/\[\s*SCHEDULE_SURVEY\b([^\]]*)\]/i);
if (svMatch && svMatch[1]) {
  svTagFound = true;
  const c = svMatch[1];
  svTgl = ((c.match(/tanggal\s*=\s*"([^"]*)"/i) || [])[1] || '').trim();
  svJam = ((c.match(/jam\s*=\s*"([^"]*)"/i) || [])[1] || '').trim();
  svUnit = ((c.match(/unit\s*=\s*"([^"]*)"/i) || [])[1] || '').trim();
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
let factNama = '', factLokasiKerja = '';
if (factsMatch && factsMatch[1]) {
  factNama        = (factsMatch[1].match(/nama\s*=\s*"([^"]*)"/i) || [])[1] || '';
  factLokasiKerja = (factsMatch[1].match(/lokasi_kerja\s*=\s*"([^"]*)"/i) || [])[1] || '';
}
let existingUnit = ''; try { existingUnit = String($('Cek_user_status').first().json.unit_interest_db || ''); } catch (e) {}
let existingBudget = ''; try { existingBudget = String($('Cek_user_status').first().json.budget_range_db || ''); } catch (e) {}
let existingNama = '';     try { existingNama = String($('Cek_user_status').first().json.nama_lengkap_db || ''); } catch (e) {}
let existingLokasiKerja = ''; try { existingLokasiKerja = String($('Cek_user_status').first().json.lokasi_kerja_db || ''); } catch (e) {}
// sanitasi ringan: buang karakter kontrol (charCode < 32) tanpa escape unicode, rapikan spasi, batasi panjang.
const cleanProfile = s => String(s || '').split('').filter(ch => ch.charCodeAt(0) >= 32).join('').replace(/\s+/g, ' ').trim().slice(0, 60);
const namaMerged        = cleanProfile(factNama)        || existingNama;
const lokasiKerjaMerged = cleanProfile(factLokasiKerja) || existingLokasiKerja;
const namaChanged        = namaMerged !== ''        && namaMerged !== existingNama;
const lokasiKerjaChanged = lokasiKerjaMerged !== '' && lokasiKerjaMerged !== existingLokasiKerja;
// kanonikalisasi tipe saat merge — buang entri tak valid (mis. "Tipe 36" tanpa slash).
// Ini yang membersihkan STATS yang sudah terlanjur korup: nilai bersih ditulis ulang,
// dan "Tipe 36" tidak pernah re-propagate dari existingUnit.
const canonType = (s) => { const t = String(s); const m = t.match(/(\d{2,3})\s*\/\s*(\d{2,3})/); if (m) return `Tipe ${m[1]}/${m[2]}`; if (/komersil|komersial/i.test(t)) return 'Komersial'; if (/subsidi/i.test(t)) return 'Subsidi'; return null; };
const regexUnits = Array.isArray(preprocess && preprocess.units) ? preprocess.units : [];
const unitSet = [];
for (const raw of [factUnit, ...regexUnits, existingUnit].join(',').split(',')) {
  const c = canonType(raw);
  if (c && !unitSet.includes(c)) unitSet.push(c);
}
const unitMerged = unitSet.join(', ');
const budgetMerged = (factBudget || (preprocess && preprocess.budgetMention) || existingBudget || '').trim();
const unitChanged = unitMerged !== '' && unitMerged !== existingUnit;
const budgetChanged = budgetMerged !== '' && budgetMerged !== existingBudget;

// PENDING SURVEY (register #1) — slot cadangan dari STATS.
// TTL sudah diterapkan di Cek_user_status; di sini tinggal pakai.
let pendingSv = { tanggal: '', jam: '', unit: '' };
try {
  const cus = $('Cek_user_status').first().json;
  pendingSv = {
    tanggal: String(cus.pending_survey_tanggal_db || '').trim(),
    jam: String(cus.pending_survey_jam_db || '').trim(),
    unit: String(cus.pending_survey_unit_db || '').trim()
  };
} catch (e) {}

// ── GUARD: TAG SURVEY HALUSINASI ──
// AI kadang memasang [SCHEDULE_SURVEY] padahal user tidak menyinggung survey/tanggal/jam
// sama sekali (mis. cuma minta foto taman). Tag setengah-isi begitu tidak boleh sampai
// masuk gate kelengkapan, karena FAIL LOUD di bawah akan menimpa balasan AI yang sudah benar.
// Sengaja TIDAK melihat pendingSv: slot nyangkut dari giliran sebelumnya justru yang
// bikin tag hantu ini berulang tiap turn.
let svHallucinated = false;
const svIntentTurn = !!(preprocess && (preprocess.wantsSurvey || preprocess.mentionsDateTime));
const svSlotsAI = [svTgl, svJam, svUnit].filter(Boolean).length;
if (svTagFound && !svIntentTurn && svSlotsAI < 3) {
  svHallucinated = true;
  svTagFound = false;
  svTgl = ''; svJam = ''; svUnit = '';
  console.warn('SCHEDULE_SURVEY diabaikan: tag hantu (user tidak minta survey, slot terisi=' + svSlotsAI + ')');
}

// ── GATE KELENGKAPAN SURVEY ──
// Write SURVEY hanya boleh jalan kalau tanggal + jam + unit LENGKAP dan valid.
if (svTagFound) {
  // register #1: slot giliran sebelumnya jadi cadangan kalau AI tidak menyebut ulang — tag AI menang
  if (!svTgl && pendingSv.tanggal) svTgl = pendingSv.tanggal;
  if (!svJam && pendingSv.jam) svJam = pendingSv.jam;
  if (!svUnit && pendingSv.unit) svUnit = pendingSv.unit;

  // unit: resolusi berjenjang, jangan tanya ulang kalau sudah diketahui sistem
  const unitResolved = svUnit || unitMerged || '';

  if (!svTgl) missingSlots.push('tanggal');
  if (!svJam) missingSlots.push('jam');
  if (!unitResolved) missingSlots.push('unit');

  if (missingSlots.length) {
    isSurveyIncomplete = true;
    surveyRejectReason = 'slot belum lengkap: ' + missingSlots.join(', ');
    console.warn('SCHEDULE_SURVEY ditolak:', surveyRejectReason);
  } else {
    const v = validateSurveySlot(svTgl, svJam);
    if (v.ok) {
      isScheduleSurvey = true;
      surveyData = { tanggal: v.tanggal, jam: v.jam, unit: unitResolved };
      console.log('SCHEDULE_SURVEY valid', JSON.stringify(surveyData));
    } else {
      isSurveyIncomplete = true;
      surveyRejectReason = v.reason;
      surveyData = { tanggal: svTgl, jam: svJam, unit: unitResolved };
      console.warn('SCHEDULE_SURVEY ditolak validasi:', v.reason);
    }
  }
}

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

// ── FAIL LOUD: tag survey ditolak -> JANGAN kirim konfirmasi palsu ──
// Setiap tag yang ditolak sistem harus MENGUBAH balasan, bukan cuma dibuang.
if (isSurveyIncomplete) {
  const tglOk = svTgl && !missingSlots.includes('tanggal');
  const jamOk = svJam && !missingSlots.includes('jam');
  if (missingSlots.includes('tanggal') && missingSlots.includes('jam')) {
    cleanOutput = `Boleh Kak, survey-nya enaknya kapan yaa? Misal ${contohTanggal} jam 10 pagi.`;
  } else if (missingSlots.includes('tanggal')) {
    cleanOutput = `Baik Kak, jam ${svJam} noted. Mau tanggal berapa yaa? Misal ${contohTanggal}.`;
  } else if (missingSlots.includes('jam')) {
    cleanOutput = `Baik Kak, untuk ${tglDisplay(svTgl)}. Jam berapa enaknya? Kami buka jam ${pad(openH)}.00 sampai ${pad(closeH)}.00 yaa.`;
  } else if (missingSlots.includes('unit')) {
    cleanOutput = `Baik Kak, untuk ${tglOk ? tglDisplay(svTgl) : 'jadwal itu'}${jamOk ? ' jam ' + svJam : ''}. Kira-kira mau lihat tipe unit yang mana yaa?`;
  } else if (/lewat|tahun/.test(surveyRejectReason)) {
    cleanOutput = `Boleh dikonfirmasi lagi tanggalnya Kak? Kalau ${contohTanggal} jam 10 pagi gimana?`;
  } else if (/tutup/.test(surveyRejectReason)) {
    cleanOutput = `Maaf Kak, di hari itu kami tutup. Boleh pilih hari lain? Misal ${contohTanggal} yaa.`;
  } else if (/jam operasional|jam tidak/.test(surveyRejectReason)) {
    cleanOutput = `Untuk jam segitu kami belum buka Kak. Survey bisa jam ${pad(openH)}.00 sampai ${pad(closeH)}.00 yaa, enaknya jam berapa?`;
  } else {
    cleanOutput = `Boleh dikonfirmasi lagi tanggal dan jamnya Kak? Misal ${contohTanggal} jam 10 pagi.`;
  }
  // survey belum jadi -> jangan biarkan aksi lain nyangkut di balasan yang sudah diganti
  isSendMedia = false;
  mediaKey = '';
}

// ── REQUEST_CALL: sisipkan admin_phone_display ──
if (isRequestCall) {
  const disp = (cfg.admin_phone_display) || '';
  if (disp && !cleanOutput.includes(disp)) cleanOutput = `${cleanOutput}\n\nBisa langsung telepon/WA ke ${disp} yaa.`;
}

// ── RESOLVE MEDIA URL + caption dari LINKS ──
// CHANGELOG 2026-07-18 (disambiguasi media, planning §Langkah 3):
//   Dulu: exact match -> substring .find() (ambil match PERTAMA) -> asal kirim baris teratas.
//   Sekarang: exact match tetap kirim; kalau exact gagal, kumpulkan SEMUA kandidat aktif
//   (substring Nama Link + kolom Keyword, lalu dipersempit kolom Tipe Unit bila key
//   mengandung pola tipe), dedup by URL, dan:
//     1 kandidat unik  -> kirim (seperti dulu)
//     >1 kandidat unik -> isMediaAmbiguous: override cleanOutput dengan pertanyaan pilihan
//                         (pola gate SURVEY — tag ditolak = balasan berubah), TIDAK kirim media,
//                         TIDAK notif tim (isSendMedia=false, isMediaManual=false)
//     0 kandidat       -> isMediaManual=true (jalur eskalasi existing, TIDAK berubah)
//   Field baru di return: isMediaAmbiguous, mediaCandidates. Field lama tidak diubah.
//   Konvensi: pakai $('Read LINKS Data').all() (Run Once for All Items), bukan .item.
// CHANGELOG 2026-07-22 (maps/website salah masuk jalur download+attach):
//   Row LINKS Tipe 'location'/'website' (mis. key "maps", "website") BUKAN file, cuma
//   URL. resolveRow() sekarang cek Tipe: kalau location/website -> JANGAN isi
//   mediaUrl/mediaCaption (supaya IF Send Media tidak trigger Download Media/Send Media
//   Kirimi), tempel URL-nya langsung sebagai teks ke cleanOutput, isSendMedia=false.
let mediaUrl = '', mediaCaption = '';
let isMediaManual = false, mediaRequestSummary = '';
let isMediaAmbiguous = false, mediaCandidates = [];
if (isSendMedia) {
  let linkRows = [];
  try { linkRows = $('Read LINKS Data').all().map(i => i.json); } catch (e) {}
  const norm = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const digitsOf = s => String(s || '').replace(/\D/g, '');
  const active = linkRows.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(String(r['Status'] || '')));

  const resolveRow = (row) => {
    const tipeRow = norm(row['Tipe']);
    if (tipeRow === 'location' || tipeRow === 'website') {
      // Bukan file media, cuma URL -> jangan lewat Download Media/Send Media Kirimi.
      // Tempel sebagai teks biasa ke balasan yang sudah ada.
      isSendMedia = false;
      const url = String(row['URL'] || '').trim();
      const label = String(row['Caption'] || row['Deskripsi'] || '').trim();
      if (url) {
        const line = label ? `${label} ${url}` : url;
        cleanOutput = cleanOutput.trim() ? `${cleanOutput}\n\n${line}` : line;
      }
      return;
    }
    mediaUrl = String(row['URL'] || '').trim();
    mediaCaption = String(row['Caption'] || row['Deskripsi'] || '').trim() || 'Ini file yang diminta yaa.';
  };

  // 1) EXACT match Nama Link == key -> kirim (perilaku existing dipertahankan)
  const exactRow = active.find(r => norm(r['Nama Link']) === mediaKey);
  if (exactRow && String(exactRow['URL'] || '').trim()) {
    resolveRow(exactRow);
  } else {
    // 2) FALLBACK: kumpulkan SEMUA kandidat aktif (Array.filter, bukan .find).
    //   (0) saring pool per jenis media (foto->image / video->video),
    //   (a) substring Nama Link + (b) Keyword (cocok PER-TOKEN),
    //   (c) persempit kolom Tipe Unit bila key mengandung pola tipe (3672/3681/3060).
    //   QUALIFIER GATE: kalau key punya kata pembeda yang TIDAK ada di kandidat mana pun
    //   (mis. "foto-interior" -> "interior" tak ada di katalog) -> kandidat dikosongkan
    //   supaya jatuh ke eskalasi manual, bukan salah tanya tipe.
    const tokensOf = s => norm(s).split(/[^a-z0-9]+/i).filter(Boolean);
    const GENERIC = new Set(['foto','gambar','photo','potret','video','klip','movie','denah','siteplan','brosur','katalog','price','pricelist','list','unit','rumah','tipe','type','file','media','minta','contoh']);
    const keyTokens = tokensOf(mediaKey);
    const keyDigits = digitsOf(mediaKey);            // "foto-36-72" -> "3672", "foto" -> ""
    const hasTypePattern = keyDigits.length >= 4;    // tipe PCR = 4 digit
    const qualifiers = keyTokens.filter(t => !GENERIC.has(t) && !/^\d+$/.test(t) && t.length >= 3);

    // jenis media yang diminta -> saring pool lewat kolom Tipe (image/video/document)
    let wantTipe = null;
    if (/\bvideo\b|klip|movie/.test(mediaKey)) wantTipe = 'video';
    else if (/foto|gambar|photo|potret|denah|siteplan|brosur|katalog|price/.test(mediaKey)) wantTipe = 'image';
    let pool = active;
    if (wantTipe) { const p = active.filter(r => norm(r['Tipe']) === wantTipe); if (p.length) pool = p; }

    const rowBag = (r) => [...tokensOf(r['Keyword']), ...tokensOf(r['Nama Link'])];
    const nameMatch = (r) => { const nl = norm(r['Nama Link']); return !!nl && (nl.includes(mediaKey) || mediaKey.includes(nl)); };
    const keywordMatch = (r) => tokensOf(r['Keyword']).some(kw => keyTokens.includes(kw));
    const typeUnitMatch = (r) => { const tuD = digitsOf(r['Tipe Unit']); return tuD.length >= 4 && (keyDigits === tuD || keyDigits.includes(tuD)); };

    // (a) substring Nama Link + (b) Keyword per-token + (c) Tipe Unit
    let candidates = pool.filter(r => nameMatch(r) || keywordMatch(r) || typeUnitMatch(r));
    // QUALIFIER GATE: kandidat wajib memenuhi minimal satu kata pembeda yang diminta
    if (qualifiers.length) {
      candidates = candidates.filter(r => { const bag = rowBag(r); return qualifiers.some(q => bag.includes(q)); });
    }
    // (c) Tipe Unit: bila key mengandung pola tipe, PERSEMPIT ke tipe itu
    if (hasTypePattern) {
      const typedIn = candidates.filter(typeUnitMatch);
      if (typedIn.length) candidates = typedIn;
    }

    // dedup by URL — baris beda tipe tapi URL sama (video 36/72 & 36/81) = 1 kandidat.
    // Simpan tipe unit yang ter-group per URL untuk menyusun pertanyaan pilihan.
    const byUrl = new Map();
    for (const r of candidates) {
      const u = String(r['URL'] || '').trim();
      if (!u) continue;
      if (!byUrl.has(u)) byUrl.set(u, { row: r, tipes: [] });
      const g = byUrl.get(u);
      const tu = String(r['Tipe Unit'] || '').trim();
      if (tu && !g.tipes.includes(tu)) g.tipes.push(tu);
    }
    const unique = [...byUrl.values()];

    if (unique.length === 1) {
      // 1 kandidat unik (termasuk kasus "semua kandidat share 1 URL") -> kirim
      resolveRow(unique[0].row);
    } else if (unique.length > 1) {
      // >1 kandidat unik -> AMBIGU: sistem yang bertanya, media TIDAK dikirim, tim TIDAK dinotif
      isMediaAmbiguous = true;
      isSendMedia = false;
      isMediaManual = false;
      mediaUrl = '';
      mediaCaption = '';

      mediaCandidates = unique.map(g => ({
        key: String(g.row['Nama Link'] || '').trim(),
        tipeUnit: g.tipes.join(' / ')
      }));

      // label human-readable per kandidat, mis. "tipe 36/72", "tipe 30/60 subsidi"
      const labelFor = (g) => {
        const nl = norm(g.row['Nama Link']);
        const kw = norm(g.row['Keyword']);
        const isSub = /subsidi/.test(nl) || /subsidi/.test(kw) || g.tipes.includes('30/60');
        const tp = g.tipes.length ? g.tipes.join(', ') : String(g.row['Tipe Unit'] || '').trim();
        if (!tp) return nl;
        return 'tipe ' + tp + (isSub ? ' subsidi' : '');
      };
      // kata benda media (foto/video) — dari Tipe kandidat atau dari key
      const isVideo = /video/.test(mediaKey) || unique.every(g => /video/i.test(String(g.row['Tipe'] || '')));
      const noun = isVideo ? 'video' : 'foto';

      const opts = unique.map(labelFor);
      let optText;
      if (opts.length <= 1) optText = opts.join('');
      else if (opts.length === 2) optText = `${opts[0]} atau ${opts[1]}`;
      else optText = `${opts.slice(0, -1).join(', ')}, atau ${opts[opts.length - 1]}`;

      // OVERRIDE balasan (pola gate SURVEY). Satu pertanyaan saja, gaya konsisten bot.
      cleanOutput = `Boleh Kak 😊 Mau ${noun} unit tipe yang mana yaa, ${optText}?`;
      console.log('SEND_MEDIA ambigu, tanya balik:', JSON.stringify(mediaCandidates));
    } else {
      // 0 kandidat -> fallback NOTIFIKASI MANUAL ke tim telemarketer (jalur existing)
      console.warn('SEND_MEDIA key tidak ada di LINKS, fallback manual:', mediaKey);
      isSendMedia = false;
      isMediaManual = true;
      const userMsg = (preprocess && preprocess.actualUserMessage) || originalMessage || '';
      mediaRequestSummary = (mediaKey ? ('key="' + mediaKey + '" ') : '') + (userMsg ? ('| pesan user: ' + String(userMsg).slice(0, 300)) : '');
    }
  }
}

// ── NOTIF ADMIN: hanya untuk survey reject kategori AI-FAULT ──
// Kasus normal (slot belum lengkap / di luar jam operasional / hari tutup) TIDAK dinotif,
// supaya admin tidak banjir alarm dari perilaku yang memang benar. Hanya kegagalan
// prompt (halusinasi tanggal/jam/tahun, format tag salah) yang di-flag.
const AI_FAULT_REASONS = ['tanggal tidak terbaca', 'jam tidak terbaca', 'jam tidak valid', 'tahun tidak valid', 'tanggal/jam sudah lewat'];
const surveyNeedsAdminAlert = isSurveyIncomplete && AI_FAULT_REASONS.some(r => surveyRejectReason.includes(r));

// register #1: slot yang dipersist ke STATS.
// Survey sukses tercatat -> kosongkan. Selain itu bawa maju slot terbaru (tag menang, pending cadangan).
const pendTglOut = svTgl || pendingSv.tanggal || '';
const pendJamOut = svJam || pendingSv.jam || '';
const pendUnitOut = svUnit || pendingSv.unit || '';
const surveyPendingWrite = (isScheduleSurvey || svHallucinated || !(pendTglOut || pendJamOut || pendUnitOut))
  ? { tanggal: '', jam: '', unit: '', ts: '' }
  : { tanggal: pendTglOut, jam: pendJamOut, unit: pendUnitOut, ts: Math.floor(Date.now() / 1000) };

return [{
  json: {
    ...chatCounter, ...preprocess, ...item.json,
    cleanOutput,
    isScheduleSurvey, surveyData,
    isSurveyIncomplete, missingSlots, surveyRejectReason,
    surveyNeedsAdminAlert,
    surveyPendingWrite,
    aiOutputRaw: aiOutput,
    isRequestCall,
    isTalkToAdmin,
    isSendMedia, mediaUrl, mediaCaption, mediaKey,
    isMediaManual, mediaRequestSummary,
    isMediaAmbiguous, mediaCandidates,
    isUnknown,
    needs_unknown: isUnknown ? 'true' : 'false',
    original_message: originalMessage,
    is_new_user: isNewUser,
    unit_interest_merged: unitMerged,
    budget_range_merged: budgetMerged,
    unit_changed: unitChanged,
    budget_changed: budgetChanged,
    nama_lengkap_merged: namaMerged,
    lokasi_kerja_merged: lokasiKerjaMerged,
    nama_changed: namaChanged,
    lokasi_kerja_changed: lokasiKerjaChanged
  }
}];