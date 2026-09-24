const chatCounter = $('Chat Counter').first().json;

// DATA LANGSUNG DARI CHAT COUNTER NODE
const userNumber = chatCounter.user_wa;
const userName = chatCounter.user_name;
const userMessage = chatCounter.original_message;   // ← perbaikan utama

// VALIDASI SEDERHANA
if (!userNumber) {
  throw new Error("user_wa tidak ditemukan di input!");
}

console.log("✅ Data berhasil di-extract:");
console.log("- No WA:", userNumber);
console.log("- Nama:", userName);
console.log("- Pesan:", userMessage);

return [{
  json: {
    search_no_wa: userNumber,
    user_name: userName,
    user_message: userMessage,
    timestamp: chatCounter.formatted_date + ' ' + chatCounter.formatted_time + ' WIB',
    source: "chat_counter_node",
    is_valid: userNumber !== "unknown"
  }
}];
