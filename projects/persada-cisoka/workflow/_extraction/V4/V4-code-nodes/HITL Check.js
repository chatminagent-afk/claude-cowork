// ============================================================
// HUMAN-IN-THE-LOOP CHECK (V4: No WA primer, lid backup)
// bot_mode = 'OFF' -> Sam handle manual -> stop.
// ============================================================
const cc = $('Chat Counter').first().json;
const digits = v => String(v ?? '').replace(/\D/g, '');
const phone = digits(cc.user_phone);
const lid = digits(cc.user_lid);

const statsRows = $('Read STATS for HITL').all()
  .map(r => r.json)
  .filter(r => r && Object.keys(r).length > 0);

let userRow = null;
if (phone) userRow = statsRows.find(r => digits(r['No WA']) === phone) || null;
if (!userRow && lid) {
  userRow = statsRows.find(r => digits(r['lid']) === lid)
         || statsRows.find(r => digits(r['No WA']) === lid)
         || null;
}

const botMode = userRow ? String(userRow['bot_mode'] || '').trim().toUpperCase() : '';

if (botMode === 'OFF') {
  console.log(`👨‍💼 HITL AKTIF — Sam sedang handle manual, bot berhenti.`);
  return [];
}

console.log(`🤖 Bot mode AKTIF (bot_mode="${botMode}") — lanjut.`);
return [$input.first()];

