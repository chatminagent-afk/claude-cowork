// ============================================================
// RATE LIMITER LID — PATCH Sesi 2 (T2)
// Batas spam dibaca dari tab CONFIG: rate_limit_max + rate_limit_window_sec.
// Fallback ke perilaku lama (5 pesan / 60 detik) kalau config kosong/invalid.
// ============================================================
const input = $input.first().json;
const userWa = $('Resolve User Row').first().json.resolved_key;
const now = Date.now();

// Baca CONFIG; kalau node Parse Config tak terjangkau, pakai default lama.
const cfg = (() => {
  try { return $('Parse Config').first().json.config || {}; } catch (e) { return {}; }
})();

// Hanya terima angka finite > 0. 0 / negatif / NaN / '' -> default lama.
const posNum = (v, def) => {
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? n : def;
};

const maxMessages = posNum(cfg.rate_limit_max, 5);           // default lama: 5
const windowSec   = posNum(cfg.rate_limit_window_sec, 60);   // default lama: 60 detik
const windowMs    = windowSec * 1000;                        // default lama: 60000 ms

// Global store menggunakan $workflow static data
const staticData = $getWorkflowStaticData('global');
const rateLimits = staticData.rateLimits || {};

const userKey = `rl_${userWa}`;

if (!rateLimits[userKey]) {
  rateLimits[userKey] = { count: 1, windowStart: now };
} else {
  const elapsed = now - rateLimits[userKey].windowStart;
  if (elapsed > windowMs) {
    // Reset window baru
    rateLimits[userKey] = { count: 1, windowStart: now };
  } else {
    rateLimits[userKey].count++;
  }
}

staticData.rateLimits = rateLimits;

const isRateLimited = rateLimits[userKey].count > maxMessages;

if (isRateLimited) {
  console.log(`⛔ RATE LIMITED: ${userWa} sudah ${rateLimits[userKey].count} pesan dalam ${windowSec}s (maks ${maxMessages})`);
  return [];
}

console.log(`✅ RATE OK: ${userWa} pesan ke-${rateLimits[userKey].count}/${maxMessages} dalam window ${windowSec}s`);
return [$input.first()];
