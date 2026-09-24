// ---- PENGGANTI blok `const prod = grab('Read PRODUK Data'); if (prod.length) {...}` ----
// Serialisasi PRODUK KONDISIONAL (pola V4). Kolom dibagi 3 ember:
//   CORE  = selalu dikirim (identitas unit + harga dasar + stok)
//   MONEY = hanya saat user bicara harga/KPR/promo/survey
//   SPEK  = hanya saat user bicara unit/fasilitas/legalitas
// Kolom yang TIDAK dikenal masuk SPEK (bukan dibuang) -> tetap robust kalau
// sheet PRODUK nambah kolom baru; cuma tidak ikut di turn basa-basi.
const prod = grab('Read PRODUK Data');
if (prod.length) {
  const norm = (k) => String(k).toLowerCase().trim();
  const DROP  = new Set(['no', 'row_number', 'last update', 'last_update', 'catatan']);
  const CORE  = new Set(['tipe unit', 'tipe', 'kategori', 'harga normal', 'status stok']);
  const MONEY = new Set(['harga promo', 'batas tanggal promo', 'booking fee / dp', 'booking fee/dp',
                         'skema cicilan', 'bank / skema kpr', 'bank/skema kpr', 'promo berlaku']);

  const wantMoney = flags.askingPrice || flags.askingKPR || flags.wantsSurvey || flags.discussingUnit;
  const wantSpek  = flags.discussingUnit || flags.askingFasilitas || flags.askingLegalitas;

  const lines = prod.map(r => {
    const name = val(r, 'Tipe Unit', 'Tipe') || '(unit tanpa nama)';
    const fields = [];
    for (const k of Object.keys(r)) {
      const kl = norm(k);
      if (DROP.has(kl)) continue;
      if (kl === 'tipe unit' || kl === 'tipe') continue;      // sudah jadi label
      const raw = r[k];
      if (raw === undefined || raw === null || String(raw).trim() === '') continue;
      const bucket = CORE.has(kl) ? 'core' : (MONEY.has(kl) ? 'money' : 'spek');
      if (bucket === 'money' && !wantMoney) continue;
      if (bucket === 'spek'  && !wantSpek)  continue;
      fields.push(`${k}=${clip(String(raw), 220)}`);
    }
    return `${name} → ${fields.join(' | ')}`;
  });
  parts.push('UNIT / HARGA / KPR / SPESIFIKASI (data resmi; tipe, harga, cicilan, skema, atau promo yang TIDAK tertulis di sini = jangan dikarang):\n' + lines.join('\n'));
}

// ---- PENGGANTI blok LINKS ----
// Metadata (Keyword, Deskripsi) cuma perlu saat user memang minta media.
// Nama key + Tipe + Tipe Unit tetap selalu ada supaya AI tahu katalognya.
const links = grab('Read LINKS Data');
if (links.length) {
  const wantMediaMeta = !!pre.wantsMedia;
  const activeRows = links.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(val(r, 'Status')));
  const active = activeRows.map(r => {
    const nm = val(r, 'Nama Link');
    if (!nm) return '';
    const meta = [];
    const tipe = val(r, 'Tipe');   if (tipe) meta.push(tipe);
    const tu   = val(r, 'Tipe Unit'); if (tu) meta.push('tipe ' + tu);
    if (wantMediaMeta) {
      const kw = val(r, 'Keyword'); if (kw) meta.push('kata kunci: ' + kw);
    }
    let line = nm;
    if (meta.length) line += ' [' + meta.join(', ') + ']';
    if (wantMediaMeta) {
      const ds = clip(val(r, 'Deskripsi'), 60);
      if (ds) line += ' - ' + ds;
    }
    return line;
  }).filter(Boolean);
  if (active.length) {
    const sample = val(activeRows[0], 'Nama Link') || 'brosur';
    parts.push('LINK/MEDIA AKTIF (saat [SEND_MEDIA] sebut key PERSIS dari kolom pertama, mis. [SEND_MEDIA: ' + sample + ']; kalau user minta foto/video tanpa sebut tipe dan ada >1 pilihan, tanya dulu tipe mana):\n- ' + active.join('\n- '));
  }
}
