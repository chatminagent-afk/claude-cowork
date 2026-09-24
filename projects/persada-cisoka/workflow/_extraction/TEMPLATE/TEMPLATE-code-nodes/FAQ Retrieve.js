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

  const grab = (node) => { try { return $(node).all().map(i => i.json).filter(Boolean); } catch (e) { return []; } };
  const val = (row, ...keys) => { for (const k of keys) { for (const rk of Object.keys(row)) { if (rk.toLowerCase().trim() === k.toLowerCase().trim() || rk.toLowerCase().startsWith(k.toLowerCase())) { const v = row[rk]; if (v !== undefined && v !== null && String(v).trim() !== '') return String(v).trim(); } } } return ''; };
  const clip = (s, n) => { s = (s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n - 1) + '…' : s; };

  const parts = [];
  const prog = grab('Read PROGRAM Data');

  // STATUS & BATCH (selalu; gating harga & pendaftaran) -- diturunkan dari PROGRAM
  if (prog.length) {
    const lines = prog.map(r => {
      const nm = val(r, 'Nama Program'), st = val(r, 'Status'), batch = val(r, 'Nama Batch');
      const mulai = val(r, 'Tanggal Mulai'), dl = val(r, 'Deadline Daftar'), kuota = val(r, 'Kuota');
      const hasBatch = batch && batch !== '-';
      return `${nm}: Status=${st || 'tidak tertulis'}${hasBatch ? ', ' + batch : ''}${mulai ? ', Mulai ' + mulai : ''}${dl ? ', Deadline daftar ' + dl : ''}${kuota ? ', Kuota ' + kuota : ''}`;
    });
    parts.push('STATUS & BATCH (sumber resmi; program/batch yang tidak ada di sini = tidak ada, jangan dikarang):\n' + lines.join('\n'));
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

  return [{ json: { ...pre, faq_context, data_context }, pairedItem: { item: 0 } }];
} catch (e) {
  const pre = ($('Preprocess - Context Detection').first() || { json: {} }).json || {};
  return [{ json: { ...pre, faq_context: '', data_context: '', faq_error: String(e) }, pairedItem: { item: 0 } }];
}

