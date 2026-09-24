
// Rate Limiter: cegah spam (maks 5 pesan per menit per user)
const input = $input.first().json;
const userWa = $('Resolve User Row').first().json.resolved_key;
const now = Date.now();

// Global store menggunakan $workflow static data
const staticData = $getWorkflowStaticData('global');
const rateLimits = staticData.rateLimits || {};

const userKey = `rl_${userWa}`;
const windowMs = 60000; // 1 menit
const maxMessages = 5;

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
  console.log(`⛔ RATE LIMITED: ${userWa} sudah ${rateLimits[userKey].count} pesan dalam 1 menit`);
  return [];
}

console.log(`✅ RATE OK: ${userWa} pesan ke-${rateLimits[userKey].count}`);
return [$input.first()];
