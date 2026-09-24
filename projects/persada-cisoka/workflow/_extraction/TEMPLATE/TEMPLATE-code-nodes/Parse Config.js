// ============================================================
// PARSE CONFIG  (ENGINE — jangan edit per klien)
// Membaca tab CONFIG (kolom: key | value) jadi satu objek config.
// Nilai bertipe list/JSON ditulis sbg JSON string di sel value.
// Semua punya default aman -> kalau klien tidak isi, engine tetap jalan.
// ============================================================
const rows = $('Read CONFIG').all().map(i => i.json);
const sheetId = $('Bootstrap Config').first().json.sheet_id || '';

const raw = {};
for (const r of rows) {
  const k = String(r.key ?? r.Key ?? r.KEY ?? '').trim();
  if (!k) continue;
  raw[k] = (r.value ?? r.Value ?? r.VALUE ?? '');
}

const str = (k, def='') => {
  const v = raw[k];
  return (v === undefined || v === null || String(v).trim() === '') ? def : String(v).trim();
};
const num = (k, def) => { const raw = str(k, ''); if (raw === '') return def; const n = Number(raw); return Number.isFinite(n) ? n : def; };
const bool = (k, def=false) => { const v = str(k, '').toLowerCase(); if (v==='') return def; return ['true','yes','y','on','1','aktif','ya'].includes(v); };
const jsonArr = (k) => { try { const v = str(k,''); if (!v) return []; const p = JSON.parse(v); return Array.isArray(p) ? p : []; } catch(e){ return []; } };

const config = {
  sheet_id: sheetId,
  client_name: str('client_name', 'Client'),
  system_prompt: str('system_prompt', 'Kamu asisten AI yang ramah. Jawab hanya dari DATA TERVERIFIKASI & FAQ. Kalau tidak ada -> [UNKNOWN].'),
  status_question: str('status_question', 'Sebelumnya, boleh tahu yang sedang chat sekarang orang tua murid atau calon muridnya langsung?'),
  admin_phone: str('admin_phone', ''),
  bot_language: str('bot_language', 'id'),
  // whitelist
  whitelist_enabled: bool('whitelist_enabled', false),
  whitelist_numbers: jsonArr('whitelist_numbers').map(x => String(x).replace(/\D/g,'')),
  // rate limit & debounce
  rate_limit_max: num('rate_limit_max', 5),
  rate_limit_window_sec: num('rate_limit_window_sec', 60),
  debounce_seconds: num('debounce_seconds', 60),
  // NLU keyword lists (driver Preprocess) — semua opsional
  status_parent_keywords: jsonArr('status_parent_keywords'),
  status_student_keywords: jsonArr('status_student_keywords'),
  out_of_scope_keywords: jsonArr('out_of_scope_keywords'),
  register_keywords: jsonArr('register_keywords'),
  price_keywords: jsonArr('price_keywords'),
  batch_keywords: jsonArr('batch_keywords'),
  program_keywords: jsonArr('program_keywords'),
  grade_program_map: jsonArr('grade_program_map'), // [{keywords:[],grade,program,note}]
};

// pass-through input agar node berikutnya tetap punya body webhook
const passthrough = $('Bootstrap Config').first() ? $('Bootstrap Config').first().json : {};
return [{ json: { ...passthrough, config } }];

