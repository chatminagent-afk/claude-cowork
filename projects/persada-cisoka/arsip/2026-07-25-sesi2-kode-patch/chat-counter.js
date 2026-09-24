// ============================================================
// CHAT COUNTER — PATCH Sesi 2 (T3)
// Dihapus: counter berbasis $vars (READ-ONLY di n8n, assignment tak persist)
//   -> nilai selalu 1, menyesatkan. Field chat_counter tidak dikonsumsi node
//   mana pun, dan baris CHAT_COUNTER di ai_input_text ditimpa total oleh
//   Cek_user_status sebelum sampai ke AI Agent. Jadi murni dead code.
// ============================================================
const webhookData = $input.first();
const body = webhookData.json.body || {};

// Ambil data dari Kirimi
const userMessage = body.message || "";
const messageType = body.messageType || "";
const userNumber = body.from || "unknown";  // ← TIDAK strip @lid, passthrough as-is
const _isLid    = String(userNumber).toLowerCase().includes('@lid');
const userLid   = String(body.originLid || (_isLid ? userNumber : '')).replace(/\D/g, '');// kunci cocok
const userPhone = _isLid ? '' : String(userNumber).replace(/\D/g, '');// utk kolom No WA
const userName = body.name || body.pushName || body.notifyName || "User";
const isFromMe = body.isFromMe === true;
const eventType = body.event || "";

// Filter: hanya pesan teks yang tidak kosong
if (messageType !== "text" || !userMessage || userMessage.trim() === "") {
    console.log('⛔ STOP: Bukan pesan teks valid');
    return [];
}

console.log('✅ LANJUT: Pesan teks valid dari user');
console.log('📱 No WA:', userNumber);

// Format tanggal & jam WIB
const now = new Date();
const formattedDate = now.toLocaleDateString('en-GB', {
    timeZone: 'Asia/Jakarta',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
});
const formattedTime = now.toLocaleTimeString('id-ID', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: 'Asia/Jakarta'
}).replace(/\./g, ':');

const processStartTs = Date.now();

const aiInputText = `[SYSTEM_DATA]
USER_NAME: ${userName}
USER_MESSAGE: "${userMessage}"

[USER QUERY]
${userMessage}`;

return [{
    json: {
        user_wa: userNumber,
        user_lid: userLid,
        user_phone: userPhone,
        user_name: userName,
        formatted_date: formattedDate,
        formatted_time: formattedTime,
        ai_input_text: aiInputText,
        original_message: userMessage,
        body: body,
        message_type: messageType,
        process_start_ts: processStartTs
    }
}];
