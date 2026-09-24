// ============================================================
// WHITELIST GATE  (ENGINE) — config-driven, anti-bug LID
// whitelist_enabled=false -> semua user lewat (mode produksi publik).
// whitelist_enabled=true  -> hanya nomor di whitelist_numbers (uji).
// Pencocokan tahan format: bandingkan digit dari `from` DAN `originLid`.
// ============================================================
const cfg = $('Parse Config').first().json.config || {};
const body = ($input.first().json.body) || ($('Parse Config').first().json.body) || {};

if (!cfg.whitelist_enabled) {
  return [$input.first()];
}

const list = (cfg.whitelist_numbers || []).map(x => String(x).replace(/\D/g, '')).filter(Boolean);
const fromDigits = String(body.from || '').replace(/\D/g, '');
const lidDigits  = String(body.originLid || '').replace(/\D/g, '');

const allowed = list.some(w => w && (w === fromDigits || w === lidDigits ||
  (fromDigits && fromDigits.endsWith(w)) || (w.endsWith(fromDigits) && fromDigits.length >= 6)));

if (!allowed) {
  console.log(`⛔ WHITELIST: ${fromDigits || lidDigits || 'unknown'} tidak di whitelist — stop.`);
  return [];
}
console.log(`✅ WHITELIST OK: ${fromDigits || lidDigits}`);
return [$input.first()];

