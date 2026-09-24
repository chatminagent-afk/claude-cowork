// ====================================================================
// BUILD FU PROMPT (2026-08-27)
// Dijalankan SESUDAH Claim STATS FU - anti-dobel tetap utuh: nomornya sudah
// diklaim sebelum satu token pun dibakar.
// ====================================================================
const cfg = $('Parse Config FU').first().json.config;
const c = $('Loop Kandidat').first().json;

// Nama SENGAJA tidak dipakai. Kolom STATS 'Nama' berisi push name akun WA yang
// sering bukan nama orang ('dawwonnu24', nama toko, nama pasangan). Menyapa dengan
// nama yang salah lebih merusak kepercayaan daripada sekadar 'Kak'.
const fuKe = Number(c.follow_up_count || 0) + 1;

// Nada menyesuaikan berapa kali orang ini sudah dikejar. followup_max = 0
// (tanpa batas) berarti angka ini bisa jadi belasan - makin tinggi, makin
// pelan, supaya AI tidak jadi mesin desak.
let tahap;
if (fuKe <= 2) {
  tahap = 'AWAL - lanjutkan pembicaraan dengan hangat, wajar kalau menawarkan langkah konkret.';
} else if (fuKe <= 5) {
  tahap = 'MENENGAH - lebih ringan. Jangan mengulang ajakan yang sudah pernah dia lewatkan.';
} else {
  tahap = 'LANJUT - SOFT. Beri ruang, akui dia mungkin sedang sibuk atau belum tertarik, JANGAN mendesak, dan JANGAN mengajak survey lagi kecuali konteks menunjukkan minat baru.';
}

// -- SAMARKAN BAHAN PROMPT (2026-09-13) --------------------------------------
// Guard "Validate FU Message" menolak pesan yang memuat angka harga/DP/cicilan/
// tenor, URL, nomor telepon, atau nama lead. Kalau bahan prompt SENDIRI memuat pola
// itu (mis. konteks "tenor 3 tahun"), AI ikut menulisnya, pesan ditolak, dan lead
// yang sama gagal di SETIAP run karena konteksnya tidak berubah sampai dia chat lagi
// (kejadian nyata: 6289635089520, 12-13 Sep 2026). Angka disamarkan di sini supaya
// AI tidak punya angka untuk disalin. Hanya bahan prompt - tidak ada yang ditulis
// balik ke STATS.
// WAJIB tetap SUPERSET dari pola guard di "Validate FU Message": jaring terakhir
// di bawah memakai pola guard persis, jadi kalau guard diubah, ubah juga di sini.
const GUARD_SAMAR = [
  { re: /\d{1,3}([.,]\d{3})+/g, ganti: '[angka]' },
  { re: /\b\d+([.,]\d+)?\s*(jt|juta|rb|ribu|m|miliar|milyar)\b/gi, ganti: '[angka]' },
  { re: /\bRp\s*\.?\s*\d/gi, ganti: '[angka]' },
  { re: /\d+\s*%/g, ganti: '[angka]' },
  { re: /\b\d+\s*tahun\b/gi, ganti: '[angka]' },
  { re: /(https?:|www\.|wa\.me|\.com\b|\.id\b)/gi, ganti: '[link]' },
  { re: /\b0\d{8,}\b|\b62\d{8,}\b/g, ganti: '[nomor]' }
];
// Sama dengan daftar UMUM di guard nama "Validate FU Message".
const UMUM_NAMA = ['persada','cisoka','residence','rumah','unit','tipe','subsidi','komersil',
  'komersial','info','admin','marketing','property','properti','sales','survey','kpr',
  'pak','bapak','ibu','kak','mas','mbak','bu','yang','saya','kami','anda']
  // (2026-09-16) WAJIB identik dengan daftar di "Validate FU Message" - lihat catatan
  // di sana. Efek di node ini hanya satu: kata sapaan tidak lagi disamarkan jadi [nama]
  // di bahan prompt, yang memang tidak pernah perlu disamarkan.
  .concat(['halo','hallo','helo','hai','hei','hey','salam','assalamualaikum',
    'assalamualaykum','waalaikumsalam','selamat','pagi','siang','sore','malam','permisi',
    'maaf','mohon','tolong','terima','kasih','test','tes','coba','oke','okay','sip',
    'siap','iya','mau','ingin','minta','boleh','bisa','ada','apa','berapa','gimana',
    'bagaimana','harga','cicilan','angsuran','lokasi','alamat','masih','sudah','belum',
    'nanti','besok','hari','kabar','chat','whatsapp','nomor','dan','atau','untuk','dari',
    'dengan','kalau','saja','juga','lagi','dulu','punya','ini','itu','nya']);
const namaLead = String((c.nama_lengkap || '') + ' ' + (c.nama || ''))
  .split(/[^A-Za-z]+/)
  .filter(w => w.length >= 3 && UMUM_NAMA.indexOf(w.toLowerCase()) === -1)
  .map(w => w.toLowerCase());

const samarkan = s => {
  let t = String(s || '');
  if (!t) return t;
  // Bentuk utuh dulu (termasuk rentang "15-30 tahun", "10, 15, 20 tahun"),
  // supaya yang tersisa tidak berupa potongan seperti "15-[angka]".
  t = t
    .replace(/\S*(https?:|www\.|wa\.me|\.com\b|\.id\b)\S*/gi, '[link]')
    .replace(/\+?\b(0|62)\d{8,}\b/g, '[nomor]')
    .replace(/\bRp\s*\.?\s*\d+([.,]\d+)*(\s*(jt|juta|rb|ribu|k|m|miliar|milyar)\b)?/gi, '[angka]')
    .replace(/\b\d+([.,]\d+)?(\s*(-|–|—|\/|,|s\.?\s*d\.?|sampai|hingga|atau|dan)\s*\d+([.,]\d+)?)*\s*(tahun|thn|th)\b/gi, '[angka]')
    .replace(/\b\d+([.,]\d+)?(\s*(-|–|—|\/|s\.?\s*d\.?|sampai|hingga|atau|dan)\s*\d+([.,]\d+)?)*\s*(jt|juta|rb|ribu|k|m|miliar|milyar)\b/gi, '[angka]')
    .replace(/\d{1,3}([.,]\d{3})+([.,]\d+)?/g, '[angka]')
    .replace(/\d+([.,]\d+)?(\s*(-|–|—|\/|s\.?\s*d\.?|sampai|hingga|atau|dan)\s*\d+([.,]\d+)?)*\s*%/g, '[angka]');
  if (namaLead.length) {
    t = t.split(/([^A-Za-z]+)/)
      .map(tok => (namaLead.indexOf(tok.toLowerCase()) !== -1 ? '[nama]' : tok))
      .join('');
  }
  // Jaring terakhir: apa pun yang masih cocok dengan pola guard persis ikut disamarkan.
  for (let i = 0; i < 3; i++) {
    let sisa = false;
    for (const g of GUARD_SAMAR) {
      if (t.search(g.re) !== -1) { sisa = true; t = t.replace(g.re, g.ganti); }
    }
    if (!sisa) break;
  }
  return t;
};

// "LANGKAH BERIKUT" di konteks adalah RENCANA untuk VIRA di chat, belum dikerjakan.
// Diberikan ke composer follow-up, AI menulisnya seolah sudah terjadi ("saya sudah
// cek ke tim kami ..."), padahal tidak ada yang mengecek. Baris itu tidak dikirim ke AI.
const buangLangkahBerikut = s => {
  let buang = false;
  return String(s || '').split('\n').filter(line => {
    const m = line.match(/^\s*([A-Za-z][A-Za-z _\/]{2,30}?)\s*:/);
    if (m) buang = /^langkah\s+berikut/i.test(m[1]);
    return !buang;
  }).join('\n').trim();
};

return [{ json: {
  ai_enabled: !!cfg.ai_enabled,
  ai_dry_run: !!cfg.ai_dry_run,
  fu_ke: fuKe,
  fu_tahap: tahap,
  fu_hari: Number(c.days_idle || 0),
  fu_konteks: samarkan(buangLangkahBerikut(c.konteks)),
  fu_last_msgs: samarkan(c.last_msgs),
  fu_unit: samarkan(c.unit_interest),
  fu_budget: samarkan(c.budget_range),
  fu_lokasi: samarkan(c.lokasi_kerja),
  fu_sumber: samarkan(c.lead_source),
  fu_pesan_pertama: samarkan(c.pesan_pertama)
}}];
