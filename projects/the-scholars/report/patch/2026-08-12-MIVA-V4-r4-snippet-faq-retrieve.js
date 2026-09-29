// ===== CONTEXT RETRIEVE V3 (KONSOLIDASI) =====
// Single source of truth = tab PROGRAM (superset: harga, batch, status, syarat).
// + ABOUT_SAM (bio) + LINKS (url) + FAQ. Token-efisien, anti-halu, tanpa tool agent.
try {
  const pre = $('Preprocess - Context Detection').first().json;
  const query = pre.actualUserMessage || '';
  const flags = {
    askingPrice: !!pre.askingPrice,
    askingBatch: !!pre.askingBatch,
    discussingProgram: !!pre.discussingProgram,
    wantsToRegister: !!pre.wantsToRegister,
  };
  const askingSyarat = /syarat|persyaratan|kriteria|ketentuan|dokumen|rapor|raport|portofolio|portfolio|requirement|nilai|esai|essay/i.test(query);
  const askingAboutSam = /\bsam\b|founder|pendiri|pengajar|mentor|tutor|guru|ngajar|siapa kak|siapa ini|admin|alumni|lulus|sekolah.*(mana|sg|singap)|kuliah|background|pengalaman|kerja/i.test(query);
  const askingProgramDetail = flags.discussingProgram || !!pre.grade || /durasi|berapa kali|seminggu|format|online|sesi|materi|isi program|belajar apa/i.test(query);

  // Kegagalan baca sheet dicatat, TIDAK ditelan diam-diam. Versi lama mengembalikan []
  // tanpa log, sehingga "sheet gagal dibaca" tidak bisa dibedakan dari "sheet memang
  // kosong" - VIRA lalu melayani customer seolah The Scholars tidak punya program.
  const sheetIssues = [];
  // Ringkasan per node ikut ke OUTPUT node (bukan cuma console), supaya bisa
  // dibaca langsung dari execution data tanpa membuka panel Logs n8n.
  const sheetDebug = {};
  const grab = (node) => {
    // pull(true) memaksa baca hasil run pertama. Perlu karena Read PROGRAM/ABOUT/LINKS
    // ber-executeOnce: kalau node ini jalan di run kedua (debounce/buffer), referensi
    // run saat ini kosong walau datanya sebenarnya sudah terambil di run pertama.
    const pull = (useFirstRun) => {
      try {
        const ref = $(node);
        const items = useFirstRun ? ref.all(0, 0) : ref.all();
        return (items || []).map(i => i.json).filter(Boolean);
      } catch (e) {
        return { err: (e && e.message) ? e.message : String(e) };
      }
    };

    const rows = pull(false);

    if (rows && rows.err !== undefined) {
      const first = pull(true);
      if (first && first.err === undefined && first.length) {
        console.warn('SHEET PULIH: "' + node + '" gagal di run saat ini (' + rows.err + '), diambil dari run pertama. ' + first.length + ' baris.');
        sheetDebug[node] = first.length + ' baris — FALLBACK run pertama (run saat ini error: ' + rows.err + ')';
        return first;
      }
      console.error('SHEET GAGAL DIBACA: "' + node + '" -> ' + rows.err);
      sheetIssues.push(node + ' (error: ' + rows.err + ')');
      sheetDebug[node] = 'GAGAL — ' + rows.err;
      return [];
    }

    if (!rows.length) {
      const first = pull(true);
      if (first && first.err === undefined && first.length) {
        console.warn('SHEET PULIH: "' + node + '" kosong di run saat ini, diambil dari run pertama. ' + first.length + ' baris.');
        sheetDebug[node] = first.length + ' baris — FALLBACK run pertama (run saat ini 0 baris)';
        return first;
      }
      console.error('SHEET KOSONG: "' + node + '" tidak mengembalikan baris apa pun.');
      sheetIssues.push(node + ' (0 baris)');
      sheetDebug[node] = '0 baris — KOSONG';
      return [];
    }

    sheetDebug[node] = rows.length + ' baris — normal';
    return rows;
  };
  const val = (row, ...keys) => { for (const k of keys) { for (const rk of Object.keys(row)) { if (rk.toLowerCase().trim() === k.toLowerCase().trim() || rk.toLowerCase().startsWith(k.toLowerCase())) { const v = row[rk]; if (v !== undefined && v !== null && String(v).trim() !== '') return String(v).trim(); } } } return ''; };
  const clip = (s, n) => { s = (s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n - 1) + '…' : s; };

  const parts = [];
  const prog = grab('Read PROGRAM Data');

  // Database tidak terbaca = GANGGUAN SISTEM, bukan "programnya tidak ada".
  // Tanpa penanda ini AI menyimpulkan The Scholars tidak punya program apa pun dan
  // menjawab dengan yakin - persis kegagalan yang terlihat di produksi.
  if (!prog.length) {
    parts.push('PERINGATAN SISTEM: DATABASE PROGRAM TIDAK TERBACA untuk pesan ini. Ini gangguan teknis, BUKAN berarti programnya tidak ada. DILARANG menyatakan program/batch tidak ada, dan DILARANG menyebut status pendaftaran, harga, jadwal, atau kuota. Untuk semua pertanyaan soal program, batch, harga, jadwal, dan pendaftaran -> jawab [UNKNOWN]. Jangan sebut adanya gangguan sistem ke user.');
  }

  // STATUS & BATCH (selalu; gating harga & pendaftaran) -- diturunkan dari PROGRAM
  // Kolom "Status" adalah SATU-SATUNYA penentu pendaftaran buka/tutup. Verdict dihitung
  // di sini (deterministik) supaya AI tidak menyimpulkannya sendiri dari tanggal.
  if (prog.length) {
    // Dropdown kolom Status di sheet PROGRAM: Active | Coming Soon | Closed | Always Active.
    // Dicocokkan per KATA supaya varian ejaan tetap kena. Urutan pemeriksaan penting:
    // ALWAYS dulu (mengandung "Active"), lalu SOON/CLOSED (mengandung "belum"/"tutup"),
    // baru OPEN. Kalau OPEN dicek duluan, "Coming Soon"/"Belum dibuka" salah terbaca.
    const ALWAYS_RE = /always|selalu/i;
    const SOON_RE = /(coming\s*soon|belum\s*dibuka|belum\s*buka|akan\s*datang)/i;
    const CLOSED_RE = /(closed|close|tutup|ditutup|penuh|full|selesai|inactive|tidak\s*aktif|non\s*-?\s*aktif)/i;
    const OPEN_RE = /(active|aktif|open|buka|dibuka|berjalan|ongoing)/i;

    // "hari ini" WIB, dinormalkan ke tengah malam supaya deadline hari-H tetap dihitung berlaku
    const _nowWib = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Jakarta' }));
    const todayWib = new Date(_nowWib.getFullYear(), _nowWib.getMonth(), _nowWib.getDate());
    const BLN_ID = ['januari','februari','maret','april','mei','juni','juli','agustus','september','oktober','november','desember'];
    const parseTglID = (s) => {
      const m = String(s || '').match(/(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/);
      if (!m) return null;
      const bi = BLN_ID.indexOf(m[2].toLowerCase());
      return bi === -1 ? null : new Date(Number(m[3]), bi, Number(m[1]));
    };

    const lines = prog.map(r => {
      const nm = val(r, 'Nama Program'), st = val(r, 'Status'), batch = val(r, 'Nama Batch');
      const mulai = val(r, 'Tanggal Mulai'), dl = val(r, 'Deadline Daftar'), kuota = val(r, 'Kuota');
      const hasBatch = batch && batch !== '-';
      const stRaw = String(st || '').trim();
      const dlDate = parseTglID(dl);
      const mulaiDate = parseTglID(mulai);
      const dlLewat = !!(dlDate && dlDate < todayWib);
      const mulaiLewat = !!(mulaiDate && mulaiDate < todayWib);

      // ── Verdict: kolom Status yang utama; tanggal cuma JARING PENGAMAN
      //    untuk kasus Sam lupa mengubah Status setelah tanggal terlewat.
      let verdict, alasan = '';
      if (ALWAYS_RE.test(stRaw)) {
        verdict = 'DIBUKA';                       // Always Active -> abaikan tanggal
      } else if (SOON_RE.test(stRaw)) {
        verdict = 'BELUM DIBUKA';
        if (mulaiLewat) {                          // Sam lupa: program sudah jalan
          verdict = 'SUDAH DITUTUP';
          alasan = 'program sudah mulai ' + mulai;
          console.warn('STATUS BASI: ' + nm + ' Status="' + stRaw + '" tapi Tanggal Mulai ' + mulai + ' sudah lewat -> dianggap SUDAH DITUTUP. Perbaiki kolom Status di sheet PROGRAM.');
        }
      } else if (CLOSED_RE.test(stRaw)) {
        verdict = 'SUDAH DITUTUP';
      } else if (OPEN_RE.test(stRaw)) {
        verdict = 'DIBUKA';
        if (dlLewat) {                             // Sam lupa: deadline sudah terlewat
          verdict = 'SUDAH DITUTUP';
          alasan = 'deadline daftar ' + dl + ' sudah lewat';
          console.warn('STATUS BASI: ' + nm + ' Status="' + stRaw + '" tapi Deadline Daftar ' + dl + ' sudah lewat -> dianggap SUDAH DITUTUP. Perbaiki kolom Status/Deadline di sheet PROGRAM.');
        } else if (!dlDate && mulaiLewat) {         // tanpa deadline: pakai tanggal mulai
          verdict = 'SUDAH DITUTUP';
          alasan = 'program sudah mulai ' + mulai;
          console.warn('STATUS BASI: ' + nm + ' Status="' + stRaw + '" tanpa Deadline, tapi Tanggal Mulai ' + mulai + ' sudah lewat -> dianggap SUDAH DITUTUP.');
        }
      } else {
        verdict = 'TIDAK JELAS';                   // di luar dropdown -> jangan menebak
        console.warn('STATUS TIDAK DIKENALI: ' + nm + ' Status="' + stRaw + '". Isi kolom Status dengan salah satu: Active / Coming Soon / Closed / Always Active.');
      }

      let out = verdict === 'TIDAK JELAS'
        ? `${nm}: STATUS PENDAFTARAN TIDAK JELAS - jangan menyatakan buka/tutup, jawab [UNKNOWN] untuk status`
        : `${nm}: PENDAFTARAN ${verdict}${alasan ? ' (' + alasan + ')' : ''}`;

      if (hasBatch) out += `, ${batch}`;
      if (mulai) out += `, Program mulai ${mulai}`;
      if (dl) out += `, Deadline daftar ${dl}`;
      if (kuota) out += `, Kuota ${kuota}`;
      return out;
    });
    parts.push('STATUS & BATCH (sumber resmi & PALING TINGGI - menang atas FAQ. PENDAFTARAN DIBUKA / BELUM DIBUKA / SUDAH DITUTUP di sini FINAL, jangan disimpulkan ulang dari tanggal; program/batch yang tidak ada di sini = tidak ada, jangan dikarang):\n' + lines.join('\n'));
  }

  // Pemetaan program -> kelas (selalu, kecil)
  parts.push('PEMETAAN PROGRAM: Junior=SD6/SMP1 | Intermediate=SMP2/SMP3 | Seniors=SMA kelas 12 | Mock Interview=semua siswa. SMA 10/11 belum ada program.');

  // HARGA (kondisional) -- dari PROGRAM
  if ((flags.askingPrice || flags.wantsToRegister || askingProgramDetail) && prog.length) {
    const lines = prog.map(r => `${val(r, 'Nama Program')}: ${val(r, 'Harga') || 'tidak tertulis'}${val(r, 'Pembayaran') ? ' (' + clip(val(r, 'Pembayaran'), 90) + ')' : ''}${val(r, 'Catatan') ? ' - ' + clip(val(r, 'Catatan'), 70) : ''}`);
    parts.push('HARGA (sebut hanya sesuai ATURAN HARGA di system; ikut status batch):\n' + lines.join('\n'));
  }

  // SYARAT (kondisional) -- dari PROGRAM
  if (askingSyarat && prog.length) {
    const lines = prog.map(r => `${val(r, 'Nama Program')}: Syarat: ${clip(val(r, 'Syarat Umum'), 180)}${val(r, 'Dokumen yang Perlu Disiapkan', 'Dokumen') ? ' | Dokumen: ' + clip(val(r, 'Dokumen yang Perlu Disiapkan', 'Dokumen'), 150) : ''}`);
    parts.push('SYARAT:\n' + lines.join('\n'));
  }

  // PROGRAM detail (kondisional)
  if (askingProgramDetail && prog.length) {
    const lines = prog.map(r => `${val(r, 'Nama Program')}: ${clip(val(r, 'Deskripsi'), 170)} | Target: ${clip(val(r, 'Target Peserta'), 90)} | Durasi: ${clip(val(r, 'Durasi'), 60)} | Format: ${clip(val(r, 'Format'), 60)}`);
    parts.push('PROGRAM (detail):\n' + lines.join('\n'));
  }

  // TENTANG SAM (kondisional) -- dari ABOUT_SAM
  if (askingAboutSam) {
    const about = grab('Read ABOUT Data');
    if (about.length) parts.push('TENTANG SAM & THE SCHOLARS:\n' + about.map(r => `${val(r, 'Aspek')}: ${clip(val(r, 'Detail'), 160)}`).join('\n'));
  }

  // LINK AKTIF (selalu) -- nama saja; URL disisipkan sistem saat [SEND_GFORM]
  const links = grab('Read LINKS Data');
  if (links.length) {
    const activeRows = links.filter(r => /aktif|active|on|ya/i.test(val(r, 'Status')));
    const active = activeRows.map(r => {
      const nm = val(r, 'Nama Link');
      const ds = clip(val(r, 'Deskripsi'), 80);
      return nm ? (ds ? `${nm} \u2014 ${ds}` : nm) : '';
    }).filter(Boolean);
    if (active.length) {
      const sample = val(activeRows[0], 'Nama Link') || 'Nama Link';
      parts.push('LINK AKTIF (saat [SEND_GFORM] WAJIB sebut Nama Link PERSIS, mis. [SEND_GFORM: ' + sample + ']):\n- ' + active.join('\n- '));
    }
  }

  const data_context = parts.join('\n\n');

  // ---------- FAQ lexical retrieval ----------
  const faq = grab('Read FAQ').filter(r => r.Pertanyaan && r.Jawaban);
  const STOP = new Set(['yang','untuk','dan','di','ke','dari','itu','ini','apa','apakah','bisa','kah','ya','yaa','kak','min','dong','sih','kok','aja','ada','gimana','bagaimana','saya','aku','nya','kalau','atau','juga','sudah','belum','mau','dengan','pada','adalah','kira','tolong','mohon','halo','hai','permisi','terima','kasih','sama','buat','soal','tentang','nih','ngga','gak','engga','tidak','dll','dsb','ga','ikut','harus','nanti','dimana','banget','seperti','pakai','punya','lagi','deh','yg','utk','sm','jd','udah','blm']);
  const GROUPS = [
    ['biaya','harga','bayar','tarif','pembayaran','cicil','cicilan','nyicil','nyicilnya','dicicil','ngecicil','dp','mahal','murah','fee','uang','dibayar','bayarnya','investasi','gratis'],
    ['daftar','pendaftaran','registrasi','enroll','gabung','join','mendaftar','ndaftar','apply'],
    ['jadwal','kapan','mulai','periode','angkatan','dibuka'],
    ['syarat','persyaratan','kriteria','ketentuan','requirement'],
    ['beasiswa','scholarship','asean','uob','cli','capitaland','moe','funded'],
    ['program','kelas','junior','intermediate','senior','seniors','jenjang'],
    ['interview','wawancara','mock'],
    ['essay','esai','karangan'],
    ['alumni','lulus','berhasil','diterima','keterima','sukses'],
    ['anak','anaku','anakku','putra','putri','murid','siswa'],
    ['singapura','singapore','sg'],
    ['tinggal','kehidupan','asrama','akomodasi','hidup'],
    ['kuota','slot','penuh','kursi','sisa'],
    ['mengajar','pengajar','guru','mentor','tutor','ngajar'],
  ];
  const SYN = {}; for (const g of GROUPS) for (const w of g) SYN[w] = g[0];
  const stem = (t) => { let w = t; for (const s of ['nya','kah','lah','kan','an','i']) if (w.length - s.length >= 4 && w.endsWith(s)) { w = w.slice(0, -s.length); break; } for (const p of ['meng','meny','mem','men','peng','peny','pem','pen','ber','ter','di','se','ke','me','pe']) if (w.length - p.length >= 4 && w.startsWith(p)) { w = w.slice(p.length); break; } return w; };
  const tok = (s) => (s || '').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, ' ').split(/\s+/).filter(Boolean).filter(t => !STOP.has(t)).map(t => { const a = SYN[t]; if (a) return a; const st = stem(t); return SYN[st] || st; }).filter(t => t.length >= 2 && !STOP.has(t));
  const docs = faq.map(r => ({ row: r, toks: tok(r.Pertanyaan) }));
  const Nn = docs.length, df = {};
  for (const dd of docs) for (const t of new Set(dd.toks)) df[t] = (df[t] || 0) + 1;
  const idf = (t) => Math.log((Nn + 1) / ((df[t] || 0) + 1)) + 1;
  const boost = {};
  if (flags.askingPrice || flags.discussingProgram) boost['Program & Biaya'] = 1.25;
  if (flags.askingBatch) boost['Batch & Jadwal'] = 1.30;
  if (flags.wantsToRegister) boost['Seleksi & Proses Daftar'] = 1.20;
  const qToks = [...new Set(tok(query))];
  let faq_context = '';
  if (qToks.length && docs.length) {
    const scored = docs.map(dd => { const dset = new Set(dd.toks); let s = 0, m = 0; for (const t of qToks) if (dset.has(t)) { s += idf(t); m++; } s *= (boost[dd.row.Kategori] || 1.0); return { row: dd.row, score: s, matched: m }; }).sort((a, b) => b.score - a.score);
    const top = scored[0];
    const FLOOR = 2.5, needCov = qToks.length >= 3 ? 2 : 1;
    if (top.score >= FLOOR && top.matched >= needCov) {
      const kept = scored.filter(x => x.score >= 0.45 * top.score && x.matched >= 1).slice(0, 4);
      faq_context = kept.map(x => `Q: ${x.row.Pertanyaan}\nA: ${x.row.Jawaban}`).join('\n\n');
    }
  }

  if (sheetIssues.length) {
    console.error('RINGKASAN MASALAH SHEET pesan ini: ' + sheetIssues.join(' | '));
  }

  return [{ json: { ...pre, faq_context, data_context, sheet_issues: sheetIssues, sheet_debug: sheetDebug }, pairedItem: { item: 0 } }];
} catch (e) {
  const msg = (e && e.message) ? e.message : String(e);
  console.error('FAQ RETRIEVE GAGAL TOTAL: ' + msg);
  const pre = ($('Preprocess - Context Detection').first() || { json: {} }).json || {};
  return [{ json: { ...pre, faq_context: '', data_context: 'PERINGATAN SISTEM: DATABASE TIDAK TERBACA untuk pesan ini. Ini gangguan teknis, BUKAN berarti datanya tidak ada. DILARANG menyatakan program/batch/harga/jadwal tidak ada -> jawab [UNKNOWN] untuk semua pertanyaan fakta. Jangan sebut adanya gangguan sistem ke user.', sheet_issues: ['FAQ Retrieve gagal total: ' + msg], sheet_debug: { 'FAQ Retrieve': 'GAGAL TOTAL — ' + msg }, faq_error: String(e) }, pairedItem: { item: 0 } }];
}
