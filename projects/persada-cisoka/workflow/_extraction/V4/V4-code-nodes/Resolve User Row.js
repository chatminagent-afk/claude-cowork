// ====================================================================
// NODE: Resolve User Row (BARU di V4)
// Identitas user: No WA (phone) = kunci PRIMER, lid = backup.
// Menghilangkan bug fallback rows[0] / match dengan kunci kosong
// yang menyebabkan data user tertukar antar row (kasus Vivipoh/DSS).
// ====================================================================
const cc = $('Chat Counter').first().json;
const digits = v => String(v ?? '').replace(/\D/g, '');
const phone = digits(cc.user_phone);
const lid = digits(cc.user_lid);

if (!phone && !lid) {
  // throw agar tertangkap Error Workflow (VIRA Error Notifier) -> admin dapat notif,
  // bukan silent drop.
  throw new Error('Identitas user kosong (phone & lid tidak ada) - payload webhook tidak dikenal: ' + JSON.stringify(cc.body?.from ?? null));
}

let rows = [];
try {
  rows = $('Read User STATS').all()
    .map(i => i.json)
    .filter(r => r && Object.keys(r).length > 0);
} catch (e) {
  console.warn('⚠️ Read User STATS tidak terbaca:', e.message);
}

// Primer: No WA == phone. Backup: kolom lid == lid.
// Terakhir: No WA == lid (row lama yang tersimpan pakai identitas lid).
let row = null;
if (phone) {
  row = rows.find(r => digits(r['No WA']) === phone) || null;
}
if (!row && lid) {
  row = rows.find(r => digits(r['lid']) === lid)
     || rows.find(r => digits(r['No WA']) === lid)
     || null;
}
// PENTING: tidak ada fallback rows[0]. Tidak ketemu = user baru.

const resolvedKey = row ? String(row['No WA']).trim() : (phone || lid);
const greetingSent = row ? String(row['greeting_sent'] || '').trim().toUpperCase() : '';

console.log(`🔑 resolved_key=${resolvedKey} | row_found=${!!row} | greeting=${greetingSent}`);

return [{
  json: {
    ...cc,
    resolved_key: resolvedKey,
    row_found: !!row,
    bot_mode: row ? String(row['bot_mode'] || '').trim().toUpperCase() : '',
    greeting_sent: greetingSent,
    is_new_user: !row || greetingSent !== 'Y',
    buffer_done_ts: Number(row ? (row['buffer_done_ts'] || 0) : 0) || 0,
    kelas_anak: row ? String(row['kelas_anak'] || '').trim() : '',
    kelas_anak_ts: Number(row ? (row['kelas_anak_ts'] || 0) : 0) || 0,
    program_interest: row ? String(row['program_interest'] || '').trim() : '',
    counter_db: Number(row ? (row['Counter'] || 0) : 0) || 0
  }
}];

