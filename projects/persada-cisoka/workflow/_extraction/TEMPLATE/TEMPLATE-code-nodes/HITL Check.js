
// ============================================================
// HUMAN-IN-THE-LOOP CHECK
// Baca kolom 'bot_mode' dari STATS sheet untuk user ini.
// Jika bot_mode = 'OFF' → Sam sedang handle manual → stop, jangan reply.
// Jika kosong / 'ON' / apapun selain 'OFF' → bot aktif, lanjut.
// ============================================================

const cc = $('Chat Counter').first().json;
const userWa = cc.user_wa;
const userLid = cc.user_lid;

// Ambil data STATS dari node Read STATS (dijalankan sebelum node ini)
// Node Read STATS membaca seluruh sheet, kita filter by No WA
const statsRows = $('Read STATS for HITL').all();
const userRow = statsRows.find(r => {
  const lid = String(r.json['lid'] || '').trim();
  return lid === String(userLid).trim();
});

const botMode = userRow ? String(userRow.json['bot_mode'] || '').trim().toUpperCase() : '';

if (botMode === 'OFF') {
  console.log(`👨‍💼 HITL AKTIF untuk ${userWa} — Sam sedang handle manual, bot berhenti.`);
  return [];
}

console.log(`🤖 Bot mode AKTIF untuk ${userWa} (bot_mode="${botMode}") — lanjut ke AI.`);
return [$input.first()];

