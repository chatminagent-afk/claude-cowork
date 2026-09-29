// NODE: Siapkan Vision Request   [BARU - V2 VISION]
// ====================================================================
// Rakit body DeepSeek (OpenAI-compatible) untuk membaca gambar user.
// Semua gambar dalam satu window debounce dikirim dalam SATU request
// (lebih murah + model bisa membandingkan antar gambar).
// Sumber gambar = URL -> DeepSeek yang fetch.
//   Kalau URL Kirimi ternyata TIDAK publik, ganti jadi data URI base64:
//   { type:'image_url', image_url:{ url:'data:image/jpeg;base64,<b64>' } }
//   dan tambahkan node Download (HTTP Request, responseFormat=file) sebelum ini.
// ====================================================================
const base = $('Cek_user_status').first().json;
const cfg = (() => { try { return $('Parse Config').first().json.config || {}; } catch (e) { return {}; } })();

const imgs = Array.isArray(base.vision_images) ? base.vision_images : [];
const maxImg = Math.max(1, Number(cfg.vision_max_images ?? 3) || 3);
const picked = imgs.slice(-maxImg).filter(im => im && im.url);

if (!picked.length) {
  // Harusnya tidak terjadi (IF Ada Gambar sudah menyaring), tapi jangan
  // sampai node ini mengirim request kosong ke DeepSeek.
  return [{ json: { vision_body: null, vision_image_count: 0, vision_skip: true } }];
}

const caption = String(base.user_message_final || '').trim();

const SYSTEM = [
  'Kamu asisten vision untuk Steven versi AI, chatbot WhatsApp yang menjual jasa AI Customer Service.',
  'Tugasmu HANYA mendeskripsikan gambar yang dikirim calon klien, supaya bot bisa membalas dengan tepat.',
  '',
  'ATURAN:',
  '- Bahasa Indonesia, padat, maksimal 5 kalimat per gambar.',
  '- Untuk tiap gambar tulis 2 baris:',
  '  KATEGORI: <pilih SATU> SCREENSHOT_CHAT | SCREENSHOT_SISTEM_ATAU_DASHBOARD | BROSUR_ATAU_IKLAN | LOGO_ATAU_BRANDING | FOTO_PRODUK_ATAU_TOKO | TANGKAPAN_LAYAR_PENAWARAN_ATAU_HARGA | KTP_ATAU_DOKUMEN_PRIBADI | BUKTI_TRANSFER | LAINNYA',
  '  ISI: apa yang terlihat.',
  '- Teks/angka penting di dalam gambar (nama bisnis, nominal, jumlah chat, tanggal, nama platform) tulis PERSIS apa adanya.',
  '- DILARANG menebak. Tidak terbaca -> tulis "tidak terbaca".',
  '- DILARANG menilai, menjawab pertanyaan user, atau memberi saran. Deskripsi saja.',
  '- PRIVASI: DILARANG menyalin NIK/nomor KTP, nomor rekening lengkap, NPWP, nomor kartu, atau data pelanggan pihak ketiga yang terlihat di screenshot. Sebut jenis dokumennya saja.',
  '- Lebih dari satu gambar -> beri nomor "Gambar 1", "Gambar 2", dst.'
].join('\n');

const content = picked.map(im => ({
  type: 'image_url',
  image_url: { url: String(im.url) }
}));

content.push({
  type: 'text',
  text: `Ada ${picked.length} gambar dari calon pembeli.` +
    (caption
      ? `\nPesan/caption yang user tulis: "${caption}"`
      : `\nUser tidak menulis pesan apa pun, hanya mengirim gambar.`) +
    `\nDeskripsikan sesuai format KATEGORI/ISI.`
});

const body = {
  model: String(cfg.vision_model || 'deepseek-v4-flash-vision-exp'),
  max_tokens: Math.max(200, Number(cfg.vision_max_tokens ?? 700) || 700),
  // OpenAI-compatible: SYSTEM jadi pesan pertama, bukan field top-level seperti Anthropic.
  messages: [
    { role: 'system', content: SYSTEM },
    { role: 'user', content }
  ]
  // Kalau completionTokens membengkak (thinking menyala), uncomment baris di bawah.
  // Jangan dipasang dari awal: kalau model exp menolak parameternya, hasilnya 400.
  // , thinking: { type: 'disabled' }
};

return [{ json: { vision_body: body, vision_image_count: picked.length, vision_skip: false } }];