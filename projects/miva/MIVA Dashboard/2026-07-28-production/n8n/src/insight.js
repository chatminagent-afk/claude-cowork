/* ============================================================================
 * insight.js — REKOMENDASI AI DARI RINGKASAN BULANAN
 *
 * Fungsi murni untuk MENYUSUN PERMINTAAN dan MEMBACA BALASAN Anthropic.
 *
 * File ini SENGAJA tidak ikut di-inline ke VIRA Dashboard API. Dashboard tidak
 * pernah memanggil AI — ia hanya membaca kolom `ai_insight_json` di tab
 * MONTHLY_SUMMARY. Alasannya konkret dan mahal: versi pertama menaruh panggilan
 * Anthropic di dalam jalur permintaan dashboard, dan halaman jadi gagal dimuat
 * karena panggilan LLM melampaui batas tunggu frontend.
 *
 * Yang memakai file ini adalah WF-B (VIRA Monthly Rollup), cron bulanan.
 * Karena ia jalan sebulan sekali, "satu panggilan per tenant per bulan" jadi
 * sifat bawaan jadwalnya — bukan sesuatu yang perlu dijaga dengan cache.
 *
 * Dipakai oleh:
 *   - Code node WF-B
 *   - qa/selftest.html (di-load langsung, diuji unit)
 * ========================================================================== */
'use strict';

/** Cari elemen pertama yang cocok predikat. Array.find belum tentu ada. */
function vdFind(list, fn) {
  var l = Object.prototype.toString.call(list) === '[object Array]' ? list : [];
  for (var i = 0; i < l.length; i++) { if (fn(l[i])) return l[i]; }
  return null;
}

/** Hash string pendek & stabil (djb2). Dipakai sebagai kunci cache. */
function vdHash(str) {
  var h = 5381;
  var s = String(str === null || str === undefined ? '' : str);
  for (var i = 0; i < s.length; i++) {
    h = ((h << 5) + h + s.charCodeAt(i)) | 0;
  }
  return (h >>> 0).toString(36);
}

/**
 * vdInsightFacts — kumpulkan fakta bulan sasaran menjadi bahan prompt.
 *
 * SEMUA angka di sini dibatasi ke SATU bulan. Versi pertama mencampur topik
 * bulanan dengan sebaran hari sepanjang masa, dan hasilnya menyesatkan: "21
 * user bulan Agustus" berdiri di sebelah "Rabu 104", padahal 104 itu akumulasi
 * berbulan-bulan. Yang membacanya pasti mengira keduanya Agustus.
 *
 * Setiap blok angka membawa `satuan`. Tanpa itu model menebak sendiri — pada
 * percobaan pertama ia menyebut jumlah lead sebagai "pesan".
 *
 * @param {object} o {
 *   bulan, bulanKey, bisnis, klien, catatan_cakupan,
 *   total_user, total_pesan,
 *   topik: [{topic, users, messages, pct}], labelMap,
 *   topicLogRows, programRows, unknownRows, faqRows
 * }
 * @returns {object|null} null kalau bulan itu tidak punya topik sama sekali —
 *          tidak ada gunanya bertanya (dan membayar) untuk bulan kosong.
 */
function vdInsightFacts(o) {
  o = o || {};
  var arr = function (v) {
    return Object.prototype.toString.call(v) === '[object Array]' ? v : [];
  };
  var src = arr(o.topik);
  if (src.length === 0) return null;

  var bulanKey = vdStr(o.bulanKey);
  var i;

  /* ---- topik ---- */
  var topik = [];
  for (i = 0; i < src.length; i++) {
    topik.push({
      topik: vdPrettyLabel(src[i].topic, o.labelMap),
      user: vdInt(src[i].users),
      persen: vdStr(src[i].pct) === '' ? '' : src[i].pct + '%',
      pesan: vdInt(src[i].messages)
    });
  }

  /* ---- sebaran hari & jam, dari TOPIC_LOG bulan sasaran ----
   * Sumbernya last_ts: epoch milidetik. Jam dibaca dalam WIB, bukan UTC —
   * tanpa pergeseran itu "jam tersibuk" meleset tujuh jam. */
  var hari = null, jam = null;
  var logRows = arr(o.topicLogRows);
  if (logRows.length) {
    var msList = [];
    for (i = 0; i < logRows.length; i++) {
      var r = logRows[i];
      if (!r || typeof r !== 'object') continue;
      if (bulanKey !== '' && vdStr(r.bulan).slice(0, 7) !== bulanKey) continue;
      var ms = vdNum(r.last_ts);
      if (ms > 0) msList.push(ms);
    }
    if (msList.length) {
      var shifted = vdWibShift(msList);
      var dow = vdDowCounts(shifted);
      var hrs = vdHourCounts(vdWibHours(msList));
      var dv = [], jv = [], k;
      for (k = 0; k < VD_DOW_LABELS.length; k++) {
        dv.push({ label: VD_DOW_LABELS[k], n: dow[k] });
      }
      var hl = vdHourLabels();
      for (k = 0; k < hl.length; k++) jv.push({ label: hl[k], n: hrs[k] });
      hari = { satuan: 'percakapan topik', nilai: dv };
      jam = { satuan: 'percakapan topik', zona: 'WIB', nilai: jv };
    }
  }

  /* ---- katalog program ----
   * Ini yang mengubah "IELTS banyak ditanya" menjadi keputusan: batch mana
   * yang masih buka, kuotanya berapa, deadline-nya kapan. */
  var program = [];
  var progRows = arr(o.programRows);
  for (i = 0; i < progRows.length && program.length < 40; i++) {
    var p = progRows[i];
    if (!p || typeof p !== 'object') continue;
    var nama = vdRowGet(p, 'Nama Program');
    if (nama === '') continue;
    program.push({
      program: nama,
      target: vdRowGet(p, 'Target Peserta').slice(0, 120),
      harga: vdRowGet(p, 'Harga'),
      batch: vdRowGet(p, 'Nama Batch'),
      mulai: vdRowGet(p, 'Tanggal Mulai'),
      kuota: vdRowGet(p, 'Kuota'),
      deadline: vdRowGet(p, 'Deadline Daftar'),
      status: vdRowGet(p, 'Status')
    });
  }

  /* ---- pertanyaan yang belum terjawab, bulan sasaran ---- */
  var belum = [];
  var unkRows = arr(o.unknownRows);
  for (i = 0; i < unkRows.length && belum.length < 40; i++) {
    var u = unkRows[i];
    if (!u || typeof u !== 'object') continue;
    var q = vdRowGet(u, 'Pertanyaan');
    if (q === '') continue;
    if (bulanKey !== '') {
      var d = vdParseDate(vdRowGet(u, 'Tanggal'));
      if (!d || d.key.slice(0, 7) !== bulanKey) continue;
    }
    belum.push(q.slice(0, 160));
  }

  /* ---- FAQ yang SUDAH ada ----
   * Dikirim supaya model berhenti menyarankan membuat jawaban yang sudah
   * tersedia. Hanya pertanyaannya; jawabannya tidak perlu dan hanya
   * memperpanjang prompt. */
  var faq = [];
  var faqRows = arr(o.faqRows);
  for (i = 0; i < faqRows.length && faq.length < 60; i++) {
    var f = faqRows[i];
    if (!f || typeof f !== 'object') continue;
    var fq = vdRowGet(f, 'Pertanyaan');
    // Wajib punya Jawaban. Tab UNKNOWN juga berkolom "Pertanyaan", dan node
    // pembacanya memakai onError yang meneruskan input saat gagal — tanpa
    // syarat ini, pertanyaan yang BELUM terjawab bisa masuk ke daftar
    // "sudah ada jawabannya" dan model berhenti menyarankannya.
    if (fq !== '' && vdRowGet(f, 'Jawaban') !== '') faq.push(fq.slice(0, 120));
  }

  return {
    periode: vdStr(o.bulan),
    catatan_periode: 'SEMUA angka di bawah ini hanya mencakup ' + vdStr(o.bulan) +
                     '. Jangan membandingkannya dengan bulan lain.',
    bisnis: vdStr(o.bisnis),
    klien: vdStr(o.klien),
    catatan_cakupan: vdStr(o.catatan_cakupan),
    ringkasan: {
      user_unik: vdInt(o.total_user),
      total_pesan: vdInt(o.total_pesan)
    },
    topik: topik,
    hari: hari,
    jam: jam,
    program: program,
    belum_terjawab: belum,
    faq_sudah_ada: faq
  };
}

/** Instruksi sistem. Pagarnya ada di sini, bukan di pesan pengguna. */
function vdInsightSystem() {
  return [
    'Kamu analis yang membantu PEMILIK USAHA membaca hasil percakapan asisten',
    'WhatsApp-nya. Pembacanya adalah pemiliknya sendiri — bukan orang yang',
    'mengoperasikan bot, bukan tim teknis.',
    '',
    'Tugasmu: mengubah angka menjadi 2-4 KEPUTUSAN USAHA yang bisa dia ambil.',
    '',
    'YANG BOLEH DISARANKAN — hal yang diputuskan pemilik usaha:',
    '  - membuka, menutup, menjadwalkan ulang, atau menambah kuota kelas/batch',
    '  - mengejar segmen tertentu (jenjang, kota, minat program)',
    '  - menghubungi kembali kelompok orang tertentu yang sudah bertanya',
    '  - harga, promo, atau cara pembayaran',
    '  - menyiapkan materi/kapasitas untuk permintaan yang terlihat menumpuk',
    '',
    'YANG DILARANG — bukan wilayah pemilik usaha, jangan pernah disarankan:',
    '  - mengubah, menyetel, atau memperbaiki asisten WhatsApp-nya',
    '  - menulis FAQ, skrip jawaban, atau pesan sambutan',
    '  - jadwal jaga, standby, shift, atau siapa memantau jam berapa',
    '  - memantau, memeriksa, atau menganalisis sesuatu lebih lanjut',
    '"Perbaiki botnya" bukan keputusan usaha. Kalau sebuah temuan hanya bisa',
    'ditindaklanjuti dengan menyetel bot, JANGAN dijadikan rekomendasi.',
    '',
    'ATURAN KERAS soal angka:',
    '1. Hanya boleh memakai angka yang ada di data. Dilarang mengarang angka,',
    '   tren, rata-rata hasil hitungan sendiri, atau perbandingan antar bulan.',
    '2. Setiap angka punya SATUAN yang tertulis di data. Pakai satuan itu',
    '   apa adanya. Jangan menyebut "pesan" untuk angka bersatuan lain.',
    '3. Seluruh data hanya mencakup satu bulan. Jangan menyiratkan tren.',
    '4. Setiap rekomendasi WAJIB menyebut angka pendukungnya di "dasar",',
    '   lengkap dengan satuannya.',
    '5. Kalau sebuah pola tidak terlihat di data, jangan menyebutkannya.',
    '   Jangan menyarankan hari tertentu kalau sebaran harinya rata.',
    '',
    'ATURAN lain:',
    '6. Perhatikan daftar program: sebut batch, kuota, atau deadline yang',
    '   relevan kalau ada. Rekomendasi yang menyebut program nyata jauh lebih',
    '   berguna daripada yang umum.',
    '7. Jangan menyarankan sesuatu yang sudah terjawab di faq_sudah_ada.',
    '8. Bahasa Indonesia yang wajar, bukan bahasa laporan.',
    '9. "aksi" harus bisa dikerjakan minggu ini oleh pemilik usaha sendiri.',
    '10. RINGKAS. "alasan" dan "aksi" masing-masing maksimal dua kalimat,',
    '    "dasar" maksimal empat butir pendek. Jawaban yang kepanjangan akan',
    '    terpotong di tengah dan seluruh isinya jadi tidak terpakai.',
    '11. Kalau datanya terlalu tipis untuk menyimpulkan apa pun, kembalikan',
    '    items berisi array kosong. Itu jawaban yang sah.',
    '',
    'Jawab HANYA dengan JSON, tanpa teks pembuka, tanpa blok kode:',
    '{"items":[{"judul":"...","alasan":"...","aksi":"...",',
    '"dampak":"tinggi|sedang|rendah","dasar":["..."]}]}'
  ].join('\n');
}

/** Pesan pengguna: fakta apa adanya, tanpa interpretasi. */
function vdInsightPrompt(facts) {
  return 'Data percakapan ' + facts.periode +
         (facts.bisnis ? '. Bidang usaha: ' + facts.bisnis : '') + '.\n\n' +
         JSON.stringify(facts, null, 1);
}

/** Badan permintaan Messages API. */
function vdInsightBody(facts, model) {
  return {
    model: vdStr(model) || 'claude-sonnet-5',
    max_tokens: 4000,
    temperature: 0.2,
    system: vdInsightSystem(),
    messages: [{ role: 'user', content: vdInsightPrompt(facts) }]
  };
}

/**
 * vdSalvageItems — pungut butir yang UTUH dari teks JSON yang terpotong.
 *
 * Balasan bisa terpotong di tengah kalau model kehabisan jatah token. Kalau
 * seluruh balasan dibuang, satu butir yang tidak selesai membatalkan tiga
 * butir yang sudah sempurna — dan bulan itu tidak dapat rekomendasi sama
 * sekali sampai bulan berikutnya.
 *
 * Objek dipungut satu per satu dengan menghitung kurung, sambil menghormati
 * tanda kutip dan escape. Objek terakhir yang belum tertutup ditinggalkan.
 */
function vdSalvageItems(text) {
  var key = text.indexOf('"items"');
  var start = key === -1 ? text.indexOf('[') : text.indexOf('[', key);
  if (start === -1) return [];

  var out = [];
  var i = start + 1;
  while (i < text.length) {
    while (i < text.length && text.charAt(i) !== '{') {
      if (text.charAt(i) === ']') return out;
      i++;
    }
    if (i >= text.length) break;

    var depth = 0, inStr = false, esc = false, closed = -1;
    for (var j = i; j < text.length; j++) {
      var c = text.charAt(j);
      if (esc) { esc = false; continue; }
      if (c === '\\') { esc = true; continue; }
      if (c === '"') { inStr = !inStr; continue; }
      if (inStr) continue;
      if (c === '{') depth++;
      else if (c === '}') { depth--; if (depth === 0) { closed = j; break; } }
    }
    if (closed === -1) break;   // objek terakhir terpotong -> ditinggalkan

    try { out.push(JSON.parse(text.substring(i, closed + 1))); } catch (e) {}
    i = closed + 1;
  }
  return out;
}

/**
 * vdInsightParse — ubah balasan Anthropic menjadi isi kolom `ai_insight_json`.
 *
 * Mengembalikan null untuk APA PUN yang tidak sesuai bentuk. Kolom yang tidak
 * jadi ditulis berarti kartunya tidak tampil bulan itu; kolom berisi separuh
 * jawaban berarti Sam membaca saran terpotong dan mengira itu utuh.
 *
 * Pembersihan butir memakai vdInsightItems() dari build-payload.js — fungsi
 * yang sama yang dipakai dashboard saat membaca kolomnya kembali. Kalau
 * keduanya dibersihkan dengan aturan berbeda, WF-B bisa menulis butir yang
 * kemudian dibuang diam-diam saat dibaca.
 */
function vdInsightParse(raw, model) {
  var text = '', stop = '';
  try {
    if (raw && raw.content && raw.content.length) {
      text = vdStr(raw.content[0].text);
      stop = vdStr(raw.stop_reason);
    } else if (typeof raw === 'string') { text = raw; }
  } catch (e) { return null; }
  if (text === '') return null;

  // Model kadang tetap membungkus dengan pagar kode meski diminta tidak.
  text = text.replace(/^\s*```(?:json)?\s*/i, '').replace(/\s*```\s*$/, '');
  var rawItems = null;
  var first = text.indexOf('{');
  var last = text.lastIndexOf('}');
  if (first !== -1 && last > first) {
    try {
      var parsed = JSON.parse(text.substring(first, last + 1));
      if (parsed) rawItems = parsed.items;
    } catch (e) { rawItems = null; }
  }

  // Balasan terpotong: pungut butir yang sudah utuh daripada membuang semua.
  var truncated = false;
  if (!rawItems) {
    rawItems = vdSalvageItems(text);
    truncated = rawItems.length > 0;
  }

  var items = vdInsightItems(rawItems);
  if (items.length === 0) return null;

  return {
    model: vdStr(model),
    generated_at: Date.now(),
    truncated: truncated || stop === 'max_tokens',
    items: items
  };
}


if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    vdHash: vdHash, vdFind: vdFind,
    vdInsightFacts: vdInsightFacts, vdInsightSystem: vdInsightSystem,
    vdInsightPrompt: vdInsightPrompt, vdInsightBody: vdInsightBody,
    vdInsightParse: vdInsightParse
  };
}
