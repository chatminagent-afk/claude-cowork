// ====================================================================
// VALIDATE FU MESSAGE (2026-08-27)
// Guard deterministik, meniru semangat PRICE GUARD di node "Process All"
// workflow Main: prompt boleh melarang, tapi yang MENJAMIN adalah kode.
// Melanggar -> throw -> error output -> Catat Kegagalan AI -> rollback klaim.
// Sesuai keputusan: nomor yang gagal DILEWATI, bukan dikirimi template.
// ====================================================================
const cfg = $('Parse Config FU').first().json.config;
const c = $('Loop Kandidat').first().json;
const p = $('Build FU Prompt').first().json;

const bersihkan = s => String(s || '')
  .replace(/\[[^\]]*\]/g, ' ')     // buang tag [SEND_MEDIA] dsb kalau bocor
  .replace(/[*`#]/g, '')
  .replace(/[ \t]{2,}/g, ' ')
  .replace(/\n{3,}/g, '\n\n')
  .trim();

let pesan = '';
// (2026-09-16) true kalau kalimat AI dibuang dan diganti template rotasi CONFIG.
let pakai_template = false;

if (p.ai_enabled) {
  try {
    const s = $input.first().json;
    pesan = (s.content && s.content[0] && s.content[0].text) || s.text || '';
  } catch (e) {}
  pesan = bersihkan(pesan);

  const tolak = [];
  if (pesan.length < 20) tolak.push('terlalu pendek atau kosong');
  if (pesan.length > 400) tolak.push('terlalu panjang (' + pesan.length + ' char)');
  if (/\d{1,3}([.,]\d{3})+/.test(pesan)) tolak.push('nominal berformat ribuan');
  if (/\b\d+([.,]\d+)?\s*(jt|juta|rb|ribu|m|miliar|milyar)\b/i.test(pesan)) tolak.push('nominal singkat');
  if (/\bRp\s*\.?\s*\d/i.test(pesan)) tolak.push('menyebut Rp');
  if (/\d+\s*%/.test(pesan)) tolak.push('persentase');
  if (/\b\d+\s*tahun\b/i.test(pesan)) tolak.push('tenor');
  if (/(https?:|www\.|wa\.me|\.com\b|\.id\b)/i.test(pesan)) tolak.push('URL');
  if (/\b0\d{8,}\b|\b62\d{8,}\b/.test(pesan)) tolak.push('nomor telepon');

  // Guard nama. Prompt sudah melarang, tapi yang menjamin adalah kode.
  // (a) pola sapaan bernama: "Kak Novi", "Kak Kris".
  if (/\bKak\s+[A-Z][a-z]{2,}/.test(pesan)) tolak.push('menyapa pakai nama');
  // (b) nama yang benar-benar tersimpan untuk lead ini, di mana pun ia muncul.
  //     Kata umum/merek dikecualikan supaya push name seperti "Cisoka Property"
  //     tidak membuat SEMUA pesan ditolak.
  const UMUM = ['persada','cisoka','residence','rumah','unit','tipe','subsidi','komersil',
    'komersial','info','admin','marketing','property','properti','sales','survey','kpr',
    'pak','bapak','ibu','kak','mas','mbak','bu','yang','saya','kami','anda']
    // (2026-09-16) Kata sapaan/kata umum yang lazim nyangkut di push name WA. Tanpa ini,
    // lead dengan Nama 'halo' (62895413911026) menolak SETIAP pesan follow-up: pembuka
    // paling wajar dalam bahasa Indonesia adalah 'Halo Kak', dan konteks lead tidak
    // berubah sampai dia chat lagi - jadi penolakannya berulang tiap jatuh tempo,
    // selamanya. Ini hanya melemahkan cek (b); sapaan bernama tetap dijaga cek (a).
    .concat(['halo','hallo','helo','hai','hei','hey','salam','assalamualaikum',
      'assalamualaykum','waalaikumsalam','selamat','pagi','siang','sore','malam','permisi',
      'maaf','mohon','tolong','terima','kasih','test','tes','coba','oke','okay','sip',
      'siap','iya','mau','ingin','minta','boleh','bisa','ada','apa','berapa','gimana',
      'bagaimana','harga','cicilan','angsuran','lokasi','alamat','masih','sudah','belum',
      'nanti','besok','hari','kabar','chat','whatsapp','nomor','dan','atau','untuk','dari',
      'dengan','kalau','saja','juga','lagi','dulu','punya','ini','itu','nya']);
  const kandidatNama = String((c.nama_lengkap || '') + ' ' + (c.nama || ''))
    .split(/[^A-Za-z]+/)
    .filter(w => w.length >= 3 && UMUM.indexOf(w.toLowerCase()) === -1);
  for (const w of kandidatNama) {
    const aman = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (new RegExp('\\b' + aman + '\\b', 'i').test(pesan)) {
      tolak.push('menyebut nama lead (' + w + ')');
      break;
    }
  }

  // (2026-09-13) Klaim sudah mengecek/menanyakan/mengonfirmasi ke TIM atau pihak lain,
  // atau sudah menelepon - hal yang tidak pernah dilakukan siapa pun. Prompt melarang, tapi
  // terbukti tetap ditulis AI ("saya sudah cek ke tim kami", "sudah saya tanyakan ke tim";
  // lead 6289635089520, 7 run berturut-turut, 12-13 Sep).
  // SENGAJA sempit: "saya sudah kirimkan daftar persyaratannya" atau "seperti yang sudah
  // saya sampaikan" sering BENAR (konteks STATS mencatat "Vira sudah kirim ...") dan
  // tidak boleh ikut ditolak. Subjek wajib saya/kami/tim supaya "Kakak sudah cek?" lolos.
  if (/\b(saya|aku|kami|vira)\s+(juga\s+|pun\s+|tadi\s+|kemarin\s+)?(sudah|udah|telah|barusan)\s+(sempat\s+|coba\s+|juga\s+|langsung\s+)?(cek|cekin|cekkan|mengecek|ngecek|periksa|memeriksa|tanya|tanyakan|menanyakan|nanya|nanyain|konfirmasi|konfirmasikan|mengonfirmasi|mengonfirmasikan|mengkonfirmasi|koordinasi|koordinasikan|berkoordinasi|mengoordinasikan|diskusi|diskusikan|berdiskusi|mendiskusikan|hubungi|menghubungi|kontak|mengontak|pastikan|memastikan|minta|meminta|mintakan|carikan|mencarikan)\b((\s+[^\s.?!,]+){0,4}?\s+(ke|kepada|dengan|sama|pada|oleh)\s+|\s+)(tim|marketing|admin|atasan|kantor|developer|pihak|bagian|manajemen|management|bank)\b/i.test(pesan)
    || /\b(sudah|udah|telah|barusan)\s+(saya|aku|kami)\s+(cek|cekkan|periksa|tanya|tanyakan|konfirmasi|konfirmasikan|koordinasikan|diskusikan|hubungi|kontak|pastikan|mintakan|carikan)\b((\s+[^\s.?!,]+){0,4}?\s+(ke|kepada|dengan|sama|pada)\s+|\s+)(tim|marketing|admin|atasan|kantor|developer|pihak|bagian|manajemen|management|bank)\b/i.test(pesan)
    || /\b(tim|marketing|admin|atasan|developer|pihak|bagian|manajemen)\b(\s+[A-Za-z]+){0,2}\s+(juga\s+)?(sudah|udah|telah|barusan)\s+(sempat\s+|coba\s+|juga\s+|langsung\s+)?(cek|mengecek|periksa|memeriksa|konfirmasi|mengonfirmasi|mengkonfirmasi|koordinasi|berkoordinasi|diskusi|berdiskusi|mendiskusikan|pastikan|memastikan|siapkan|menyiapkan|hitung|menghitung|hubungi|menghubungi|carikan|mencarikan|setujui|menyetujui)\b/i.test(pesan)
    || /\b(sudah|udah|telah)\s+di(cek|periksa|tanyakan|konfirmasi|konfirmasikan|koordinasikan|diskusikan|pastikan|setujui)\s+(oleh|dari|ke|dengan|sama|bersama)\s+(pihak\s+|bagian\s+)?(tim|kami|marketing|admin|atasan|developer|manajemen)\b/i.test(pesan)
    || /\b(saya|aku|kami|tim|vira)\s+(juga\s+|pun\s+|tadi\s+|kemarin\s+)?(sudah|udah|telah|barusan)\s+(sempat\s+|coba\s+)?(telepon|menelepon|telpon|nelpon|menelpon)\b/i.test(pesan)) {
    tolak.push('klaim sudah melakukan');
  }

  // (2026-09-13) Keluaran AI KOSONG = anomali model/API, bukan soal isi konteks: tetap
  // pakai pesan error lama persis, supaya perilakunya juga tetap lama (klaim di-rollback,
  // dicoba lagi run berikutnya) dan tidak menunda lead 48 jam karena gangguan sesaat.
  if (tolak.length && !pesan) {
    throw new Error('FU_AI_INVALID: ' + tolak.join(', ') + ' :: ' + pesan.slice(0, 160));
  }
  if (tolak.length) {
    // (2026-09-13) Satu baris, TANPA titik dua. Formatter error node Code n8n hanya
    // membawa baris pertama dan memotong di titik dua (versi live: hanya menyisakan teks
    // SETELAH titik dua terakhir - itu sebabnya notif lama berisi potongan pesan tanpa
    // alasan). Penanda FU_AI_DITOLAK_GUARD wajib sampai utuh ke "Rollback STATS FU (AI)"
    // (nomor DITUNDA ke jadwal berikutnya, bukan diulang tiap jam) dan "Report FU Run".
    // Maks 150 char: "Catat Kegagalan AI" memotong 180 SESUDAH n8n menambah "[line N]".
    const info = ('FU_AI_DITOLAK_GUARD (' + tolak.join(', ') + ') >> ' + pesan)
      .replace(/[:\r\n]+/g, ' ')
      .replace(/\s{2,}/g, ' ')
      .slice(0, 150);
    // (2026-09-16) FALLBACK TEMPLATE. Dulu lead-nya DILEWATI dan ditunda ke jadwal
    // berikutnya. Kalau penyebab penolakan melekat pada baris STATS-nya - mis. push name
    // 'halo' bikin setiap pembuka "Halo Kak" kena guard nama - konteksnya tidak berubah
    // sampai lead chat lagi, jadi lead itu ditolak lagi di jatuh tempo berikutnya,
    // selamanya, dan tidak pernah benar-benar di-follow-up. Sekarang kalimat AI dibuang
    // dan diganti template rotasi CONFIG: tulisan manusia, persis yang dipakai saat
    // followup_ai_enabled = N, jadi TIDAK divalidasi ulang (template memang memuat angka).
    // Klaim "Claim STATS FU" DIPERTAHANKAN karena pesannya benar-benar terkirim.
    const tpl = String(c.message || '').trim();
    // Template kosong -> tidak ada yang bisa dikirim. Perilaku lama PERSIS: dilewati,
    // klaim dikembalikan, dan ditunda ke jadwal berikutnya lewat penanda di 'info'.
    if (!tpl) throw new Error(info);
    // Dicatat ke static data yang sama dengan "Catat Kegagalan AI" supaya "Report FU Run"
    // melapor SEKALI di ujung run. Penanda beda: nomor ini TERKIRIM, bukan dilewati.
    try {
      const sd = $getWorkflowStaticData('global');
      if (!Array.isArray(sd.fu_ai_fail)) sd.fu_ai_fail = [];
      sd.fu_ai_fail.push({
        no_wa: c.no_wa,
        alasan: info.replace('FU_AI_DITOLAK_GUARD', 'FU_AI_FALLBACK_TEMPLATE').slice(0, 150)
      });
    } catch (e) {}
    console.warn('Follow-up pakai template (' + c.no_wa + '): ' + info);
    pesan = tpl;
    pakai_template = true;
  }
} else {
  // followup_ai_enabled = N -> kembali ke template rotasi lama.
  pesan = String(c.message || '').trim();
  if (!pesan) throw new Error('FU_AI_INVALID: AI dimatikan tapi template kosong');
}

// Dry run: pesan tetap disusun sungguhan, tapi dikirim ke admin - bukan lead.
const dry = !!p.ai_dry_run;
const target = dry ? String(cfg.admin_phone || '').trim() : String(c.no_wa || '').trim();
if (!target) throw new Error('FU_AI_INVALID: nomor tujuan kosong');

const teks = dry
  ? ('[DRY RUN -> ' + c.no_wa + ' | FU ke-' + p.fu_ke + ' | idle ' + p.fu_hari + 'h]\n\n' + pesan)
  : pesan;

return [{ json: {
  target_phone: target,
  final_message: teks,
  dry_run: dry,
  pakai_template: pakai_template,
  no_wa: c.no_wa
}}];
