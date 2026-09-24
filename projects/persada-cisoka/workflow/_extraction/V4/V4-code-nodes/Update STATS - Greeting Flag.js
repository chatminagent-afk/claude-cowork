// ====================================================================
// UPDATE GREETING FLAG (V4 - disederhanakan)
// Dulu: pattern-matching teks balasan (rapuh, tergantung susunan
// kalimat). Sekarang: cukup dari flag is_new_user — kalau eksekusi
// ini mengirim intro ke user baru (reply sudah SUKSES terkirim
// karena node ini jalan setelah Reply Chat Kirimi), tandai Y.
// ====================================================================
const isNewUser = $('Cek_user_status').first().json.is_new_user === true;

if (isNewUser) {
  console.log('📝 [GREETING] intro terkirim ke user baru -> greeting_sent = Y');
}

return [{
  json: {
    update_needed: isNewUser ? 'true' : 'false',
    greeting_sent: 'Y'
  }
}];

