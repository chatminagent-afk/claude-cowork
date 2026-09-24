// ====================================================================
// NODE: Cek_user_status
// Type: Code (JavaScript)
// ====================================================================

const chatCounter = $('Chat Counter').first().json;
const statsRows = $('Read User STATS').all();
const userWa  = chatCounter.user_wa;
const userLid = chatCounter.user_lid;

// Cari user di STATS by LID (kunci stabil)
const userRow = statsRows.find(r => {
  const lid = String(r.json['lid'] || '').trim();
  return lid === String(userLid).trim();
});

const userStatus = userRow ? String(userRow.json['user_status'] || '').trim() : '';
const greetingSent = userRow ? String(userRow.json['greeting_sent'] || '').trim() : '';

// Ambil pending_msg dari Re-Read STATS Debounce — bukan Read User STATS
// Re-Read jalan SETELAH Wait 8 detik, jadi sudah punya semua bubble termasuk yang terakhir
const debounceRow = $('Re-Read STATS Debounce').first().json;
const botModeNow = String(debounceRow['bot_mode'] || '').trim().toUpperCase();
if (botModeNow === 'OFF') {
  console.log('👨‍💼 HITL (post-debounce): bot_mode OFF — berhenti, Sam handle manual.');
  return [];
}
const pendingMsg = (debounceRow['pending_msg'] || '').trim();
const userMessage = pendingMsg || chatCounter.original_message;

console.log(`📨 userMessage final ke AI:\n${userMessage}`);

// ============ SIMPLE BOOLEAN LOGIC ============
// Kirim greeting HANYA jika:
// 1. User belum punya status DAN
// 2. Greeting belum pernah dikirim (flag ≠ Y)
const counter = Number(userRow ? (userRow.json['Counter'] || 0) : 0) || 0;
const shouldAskStatus = (!userStatus && greetingSent !== 'Y' && counter <= 1);

if (shouldAskStatus) {
  console.log('🆕 New user - will send greeting');
} else if (userStatus) {
  console.log(`✅ User status: ${userStatus}`);
} else if (greetingSent === 'Y') {
  console.log('⛔ Greeting already sent - skip');
}

let aiSystemData = `[SYSTEM_DATA]
USER_WA: ${userWa}
USER_STATUS_IN_DB: ${userStatus || 'EMPTY'}
IS_NEW_USER: ${shouldAskStatus}
GREETING_SENT: ${greetingSent === 'Y' ? 'YES' : 'NO'}

CRITICAL INSTRUCTION:
${shouldAskStatus ? 
  `This is a NEW USER. You MUST ask: "${($('Parse Config').first().json.config||{}).status_question || 'Sebelumnya, boleh tahu yang sedang chat sekarang orang tua murid atau calon muridnya langsung?'}"` : 
  userStatus ? 
    `This user's status is: ${userStatus}. Use appropriate language.` :
    `Greeting already sent but user hasn't responded. Continue conversation naturally WITHOUT repeating the greeting.`
}

[USER QUERY]
${userMessage}`;

return [{
  json: {
    ...chatCounter,
    ai_input_text: aiSystemData,
    user_message_final: userMessage,
    user_status_from_db: userStatus,
    is_new_user: !userStatus,
    should_ask_status: shouldAskStatus
  }
}];
