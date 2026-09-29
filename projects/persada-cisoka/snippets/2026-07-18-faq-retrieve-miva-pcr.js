// ===== CONTEXT RETRIEVE (PCR) =====
// data_context dari PRODUK (unit/harga/KPR) + LINKS. FAQ lexical.
// CHANGELOG 2026-07-18 (disambiguasi media):
//   - HAPUS blok $('Read LINGKUNGAN Data') (referensi mati; data lingkungan sudah
//     dipindah ke FAQ). Node itu tidak ada di workflow live -> grab() selalu [].
//   - Serialisasi LINK/MEDIA AKTIF kini menyertakan Tipe, Tipe Unit, dan Keyword
//     (kolom baru sheet LINKS) supaya AI bisa menyebut opsi per tipe dengan akurat
//     saat permintaan media ambigu.
try {
  const pre = $('Preprocess - Context Detection').first().json;
  const query = pre.actualUserMessage || '';
  const flags = {
    askingPrice: !!pre.askingPrice, askingKPR: !!pre.askingKPR, askingLokasi: !!pre.askingLokasi,
    askingFasilitas: !!pre.askingFasilitas, askingLegalitas: !!pre.askingLegalitas,
    discussingUnit: !!pre.discussingUnit, wantsSurvey: !!pre.wantsSurvey,
  };
  const grab = (node) => { try { return $(node).all().map(i => i.json).filter(Boolean); } catch (e) { return []; } };
  const val = (row, ...keys) => { for (const k of keys) { for (const rk of Object.keys(row)) { if (rk.toLowerCase().trim() === k.toLowerCase().trim() || rk.toLowerCase().startsWith(k.toLowerCase())) { const v = row[rk]; if (v !== undefined && v !== null && String(v).trim() !== '') return String(v).trim(); } } } return ''; };
  const clip = (s, n) => { s = (s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n - 1) + '…' : s; };

  const parts = [];
  const prod = grab('Read PRODUK Data');
  if (prod.length) {
    // Serialisasi GENERIK: loop semua kolom PRODUK apa adanya (label = nama header).
    // Robust terhadap restrukturisasi skema (kolom baru/rename/nambah otomatis ikut,
    // tanpa hardcode 'Harga'/'Skema KPR'/dst). Kolom index/timestamp di-skip.
    const SKIP = new Set(['no', 'row_number', 'last update', 'last_update', 'tipe unit', 'tipe']);
    const lines = prod.map(r => {
      const name = val(r, 'Tipe Unit', 'Tipe') || '(unit tanpa nama)';
      const fields = [];
      for (const k of Object.keys(r)) {
        const kl = String(k).toLowerCase().trim();
        if (SKIP.has(kl)) continue;
        const raw = r[k];
        if (raw === undefined || raw === null || String(raw).trim() === '') continue;
        fields.push(`${k}=${clip(String(raw), 220)}`);
      }
      return `${name} → ${fields.join(' | ')}`;
    });
    parts.push('UNIT / HARGA / KPR / SPESIFIKASI (data resmi; tipe, harga, cicilan, skema, atau promo yang TIDAK tertulis di sini = jangan dikarang):\n' + lines.join('\n'));
  }
  const links = grab('Read LINKS Data');
  if (links.length) {
    const activeRows = links.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(val(r, 'Status')));
    const active = activeRows.map(r => {
      const nm = val(r, 'Nama Link');
      if (!nm) return '';
      const tipe = val(r, 'Tipe');
      const tu = val(r, 'Tipe Unit');
      const kw = val(r, 'Keyword');
      const ds = clip(val(r, 'Deskripsi'), 60);
      const meta = [];
      if (tipe) meta.push(tipe);
      if (tu) meta.push('tipe ' + tu);
      if (kw) meta.push('kata kunci: ' + kw);
      let line = nm;
      if (meta.length) line += ' [' + meta.join(', ') + ']';
      if (ds) line += ' - ' + ds;
      return line;
    }).filter(Boolean);
    if (active.length) {
      const sample = val(activeRows[0], 'Nama Link') || 'brosur';
      parts.push('LINK/MEDIA AKTIF (saat [SEND_MEDIA] sebut key PERSIS dari kolom pertama, mis. [SEND_MEDIA: ' + sample + ']; kalau user minta foto/video tanpa sebut tipe dan ada >1 pilihan, tanya dulu tipe mana):\n- ' + active.join('\n- '));
    }
  }
  const data_context = parts.join('\n\n');

  // FAQ lexical retrieval
  const faq = grab('Read FAQ').filter(r => r.Pertanyaan && r.Jawaban);
  const STOP = new Set(['yang','untuk','dan','di','ke','dari','itu','ini','apa','apakah','bisa','kah','ya','yaa','kak','min','dong','sih','kok','aja','ada','gimana','bagaimana','saya','aku','nya','kalau','atau','juga','sudah','belum','mau','dengan','pada','adalah','tolong','mohon','halo','hai','permisi','terima','kasih','sama','buat','soal','tentang','nih','ga','gak','engga','tidak','dll','yg','utk']);
  const GROUPS = [
    ['harga','biaya','bayar','cicil','cicilan','angsuran','dp','kpr','tenor','bunga','subsidi','promo','murah','mahal'],
    ['unit','tipe','rumah','kavling','cluster','hook','bangunan'],
    ['luas','tanah','bangunan','ukuran'],
    ['survey','survei','kunjungan','datang'],
    ['lokasi','alamat','maps','akses','tol','jalan','stasiun','dekat'],
    ['legalitas','shm','hgb','sertifikat','imb','pbb','akad','notaris'],
    ['fasilitas','keamanan','cctv','masjid','taman','kolam','security','gate'],
    ['ready','indent','stok','tersedia','sisa'],
    ['bank','kredit','approve','pengajuan','simulasi'],
    ['brosur','siteplan','denah','katalog','gambar','foto'],
  ];
  const SYN = {}; for (const g of GROUPS) for (const w of g) SYN[w] = g[0];
  const stem = (t) => { let w = t; for (const s of ['nya','kah','lah','kan','an','i']) if (w.length - s.length >= 4 && w.endsWith(s)) { w = w.slice(0, -s.length); break; } for (const p of ['meng','meny','mem','men','peng','peny','pem','pen','ber','ter','di','se','ke','me','pe']) if (w.length - p.length >= 4 && w.startsWith(p)) { w = w.slice(p.length); break; } return w; };
  const tok = (s) => (s || '').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, ' ').split(/\s+/).filter(Boolean).filter(t => !STOP.has(t)).map(t => { const a = SYN[t]; if (a) return a; const st = stem(t); return SYN[st] || st; }).filter(t => t.length >= 2 && !STOP.has(t));
  const docs = faq.map(r => ({ row: r, toks: tok(r.Pertanyaan) }));
  const Nn = docs.length, df = {};
  for (const dd of docs) for (const t of new Set(dd.toks)) df[t] = (df[t] || 0) + 1;
  const idf = (t) => Math.log((Nn + 1) / ((df[t] || 0) + 1)) + 1;
  const boost = {};
  if (flags.askingPrice || flags.askingKPR) boost['Harga & KPR'] = 1.25;
  if (flags.askingLokasi) boost['Lokasi'] = 1.2;
  if (flags.wantsSurvey) boost['Survey'] = 1.2;
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
