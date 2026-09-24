// ====================================================================
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
    nama_lengkap: row ? String(row['nama_lengkap'] || '').trim() : '',
    nama_lengkap_ts: Number(row ? (row['nama_lengkap_ts'] || 0) : 0) || 0,
    domisili: row ? String(row['domisili'] || '').trim() : '',
    domisili_ts: Number(row ? (row['domisili_ts'] || 0) : 0) || 0,
    pending_survey_tanggal: row ? String(row['pending_survey_tanggal'] || '').trim() : '',
    pending_survey_jam: row ? String(row['pending_survey_jam'] || '').trim() : '',
    pending_survey_unit: row ? String(row['pending_survey_unit'] || '').trim() : '',
    pending_survey_ts: Number(row ? (row['pending_survey_ts'] || 0) : 0) || 0,
    lead_source_db: row ? String(row['lead_source'] || '').trim() : '',
    counter_db: Number(row ? (row['Counter'] || 0) : 0) || 0
  }
}];
