// Rate Limiter (ENGINE) — batas & window dari CONFIG (default 5/menit)
const cfg = $('Parse Config').first().json.config || {};
const userWa = $('Chat Counter').first().json.user_lid || $('Chat Counter').first().json.user_wa;
const now = Date.now();
const staticData = $getWorkflowStaticData('global');
const rateLimits = staticData.rateLimits || {};
const userKey = `rl_${userWa}`;
const windowMs = (Number(cfg.rate_limit_window_sec) || 60) * 1000;
const maxMessages = Number(cfg.rate_limit_max) || 5;
if (!rateLimits[userKey]) {
  rateLimits[userKey] = { count: 1, windowStart: now };
} else {
  const elapsed = now - rateLimits[userKey].windowStart;
  if (elapsed > windowMs) rateLimits[userKey] = { count: 1, windowStart: now };
  else rateLimits[userKey].count++;
}
staticData.rateLimits = rateLimits;
if (rateLimits[userKey].count > maxMessages) {
  console.log(`⛔ RATE LIMITED: ${userWa} (${rateLimits[userKey].count}/${maxMessages})`);
  return [];
}
console.log(`✅ RATE OK: ${userWa} pesan ke-${rateLimits[userKey].count}`);
return [$input.first()];

