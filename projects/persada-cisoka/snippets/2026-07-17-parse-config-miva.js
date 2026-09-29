// ============================================================
// PARSE CONFIG (ENGINE) — baca tab CONFIG (key|value) jadi objek config.
// Nilai list/JSON ditulis sbg JSON string di sel value.
// Perubahan 2026-07-17: default bot_name 'VIRA' -> 'Vira'.
// ============================================================
const rows = $('Read CONFIG').all().map(i => i.json);
const sheetId = $('Bootstrap Config').first().json.sheet_id || '';
const raw = {};
for (const r of rows) {
  const k = String(r.key ?? r.Key ?? r.KEY ?? '').trim();
  if (!k) continue;
  raw[k] = (r.value ?? r.Value ?? r.VALUE ?? '');
}
const str = (k, def='') => { const v = raw[k]; return (v===undefined||v===null||String(v).trim()==='') ? def : String(v).trim(); };
const num = (k, def) => { const s = str(k,''); if (s==='') return def; const n = Number(s); return Number.isFinite(n)?n:def; };
const bool = (k, def=false) => { const v = str(k,'').toLowerCase(); if (v==='') return def; return ['true','yes','y','on','1','aktif','ya'].includes(v); };
const jsonArr = (k) => { try { const v = str(k,''); if (!v) return []; const p = JSON.parse(v); return Array.isArray(p) ? p : []; } catch(e){ return []; } };

const config = {
  sheet_id: sheetId,
  client_name: str('client_name', 'Persada Cisoka Residence'),
  bot_name: str('bot_name', 'Vira'),
  bot_language: str('bot_language', 'id'),
  system_prompt: str('system_prompt', ''),
  admin_phone: str('admin_phone', ''),
  admin_phone_display: str('admin_phone_display', ''),
  field_team_phone: (() => {
    const a = jsonArr('field_team_phone');
    if (a.length) return a.map(x => String(x).replace(/\D/g,'')).filter(Boolean);
    const s = str('field_team_phone','');
    return s ? [s.replace(/\D/g,'')].filter(Boolean) : [];
  })(),
  media_team_phone: (() => {
    const a = jsonArr('media_team_phone');
    if (a.length) return a.map(x => String(x).replace(/\D/g,'')).filter(Boolean);
    const s = str('media_team_phone','');
    return s ? [s.replace(/\D/g,'')].filter(Boolean) : [];
  })(),
  brochure_url: str('brochure_url', ''),
  media_catalog: jsonArr('media_catalog'),
  survey_slots: jsonArr('survey_slots'),
  survey_open_hour: num('survey_open_hour', 8),
  survey_close_hour: num('survey_close_hour', 17),
  followup_max: num('followup_max', 3),
  followup_interval_hours: num('followup_interval_hours', 24),
  followup_open_hour: num('followup_open_hour', 9),
  followup_close_hour: num('followup_close_hour', 18),
  followup_templates: jsonArr('followup_templates'),
  lead_source_map: jsonArr('lead_source_map'),
  whitelist_enabled: bool('whitelist_enabled', false),
  whitelist_numbers: jsonArr('whitelist_numbers').map(x => String(x).replace(/\D/g,'')),
  rate_limit_max: num('rate_limit_max', 5),
  rate_limit_window_sec: num('rate_limit_window_sec', 60),
  debounce_seconds: num('debounce_seconds', 60),
  // Kredensial Kirimi utk endpoint multipart send-message-file (upload binary).
  // Custom-auth n8n TIDAK reliabel meng-inject body ke multipart/form-data,
  // jadi user_code/secret/device_id di-supply sbg field form via CONFIG sheet.
  // Node teks (JSON body) tetap pakai credential httpCustomAuth.
  kirimi_user_code: str('kirimi_user_code', ''),
  kirimi_secret: str('kirimi_secret', ''),
  kirimi_device_id: str('kirimi_device_id', ''),
};
const passthrough = $('Bootstrap Config').first() ? $('Bootstrap Config').first().json : {};
return [{ json: { ...passthrough, config } }];
