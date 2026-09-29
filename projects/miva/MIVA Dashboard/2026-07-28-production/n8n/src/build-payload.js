/* ============================================================================
 * build-payload.js — NORMALISASI DATA SHEET -> KONTRAK DASHBOARD
 *
 * Fungsi murni. Tidak menyentuh jaringan, tidak baca global selain argumen.
 * Inilah alasan UI bisa identik untuk produk yang berbeda: semua perbedaan
 * skema diserap di sini, frontend hanya merender deskriptor.
 *
 * Dipakai oleh:
 *   - n8n Code node "Build Payload" (di-inline oleh build_workflow.py)
 *   - qa/selftest.html              (di-load langsung, diuji unit)
 *
 * KONTRAK KELUARAN — lihat docs/2026-07-28-API-CONTRACT.md
 * ========================================================================== */
'use strict';

/* ---------------------------------------------------------------- helpers */

/** Ambil digit saja. Dipakai untuk mencocokkan identitas WA/LID. */
function vdDigits(v) {
  return String(v === null || v === undefined ? '' : v).replace(/\D/g, '');
}

/**
 * vdNormalizeWa — merapikan nomor yang diketik manusia menjadi bentuk yang
 * dipakai bot di kolom "No WA" (digit saja, berawalan kode negara).
 *
 * Aturan Indonesia: `08xx` dan `8xx` sama-sama berarti `628xx`. Nomor yang
 * sudah diawali `62` dibiarkan. Awalan internasional `00` dibuang lebih dulu
 * supaya `00628…` tidak berubah jadi `620628…`.
 *
 * Aturan "8 di depan" sengaja DIBATASI pada panjang 9–12 digit, yaitu rentang
 * nomor seluler Indonesia tanpa kode negara. Tanpa batas itu, nomor luar
 * negeri yang kebetulan diawali 8 (mis. +86 Tiongkok, 13 digit) akan diberi
 * awalan 62 dan tersimpan sebagai nomor yang salah total.
 *
 * Mengembalikan '' kalau hasilnya tidak masuk akal sebagai nomor telepon —
 * pemanggil harus menolak, bukan menulis sampah ke sheet.
 */
function vdNormalizeWa(raw) {
  var d = vdDigits(raw);
  if (d === '') return '';
  if (d.length > 2 && d.substring(0, 2) === '00') d = d.substring(2);
  if (d.charAt(0) === '0') {
    d = '62' + d.substring(1);
  } else if (d.charAt(0) === '8' && d.length >= 9 && d.length <= 12) {
    d = '62' + d;
  }
  if (d.length < 9 || d.length > 15) return '';
  return d;
}

/** Trim aman untuk nilai sel yang bisa berupa angka/null/undefined. */
function vdStr(v) {
  if (v === null || v === undefined) return '';
  return String(v).trim();
}

function vdIsBlank(v) { return vdStr(v) === ''; }

/** Parse angka toleran ("12,5" / "12" / 12 / ""). Gagal -> 0. */
function vdNum(v) {
  if (typeof v === 'number' && isFinite(v)) return v;
  var s = vdStr(v).replace(/[^0-9.\-]/g, '');
  var n = parseFloat(s);
  return isFinite(n) ? n : 0;
}

/**
 * Parse bilangan bulat (Counter, follow_up_count, dsb).
 *
 * Semua non-digit dibuang, TERMASUK titik — karena sel yang diformat gaya
 * Indonesia mengirim "1.234" yang berarti seribu dua ratus tiga puluh empat,
 * bukan 1,234. Kolom-kolom ini secara definisi tidak punya pecahan, jadi
 * membuang titik selalu benar di sini (dan salah kalau dipakai untuk harga —
 * karena itu fungsinya dipisah dari vdNum).
 */
function vdInt(v) {
  if (typeof v === 'number' && isFinite(v)) return Math.round(v);
  var s = vdStr(v);
  var neg = s.charAt(0) === '-';
  s = s.replace(/[^0-9]/g, '');
  if (s === '') return 0;
  var n = parseInt(s, 10);
  return neg ? -n : n;
}

/**
 * Parse tanggal dari berbagai format yang benar-benar dipakai kedua workflow:
 *   - "21/07/2026"  (en-GB, dipakai Tanggal Chat Pertama/Terakhir)
 *   - "2026-07-21"  / ISO penuh
 *   - epoch detik (10 digit) atau milidetik (13 digit) — kolom *_ts
 * Return { ms, key:"YYYY-MM-DD" } atau null.
 *
 * Semua perhitungan hari memakai UTC supaya tidak bergeser oleh timezone
 * server n8n vs browser. Nilai yang masuk sudah dicatat dalam WIB oleh bot,
 * jadi yang dibandingkan adalah label harinya, bukan instant absolutnya.
 */
function vdParseDate(v) {
  if (v === null || v === undefined) return null;
  if (v instanceof Date && !isNaN(v.getTime())) return vdFromMs(v.getTime());

  var s = vdStr(v);
  if (s === '') return null;

  // epoch murni
  if (/^\d{10}$/.test(s)) return vdFromMs(parseInt(s, 10) * 1000);
  if (/^\d{13}$/.test(s)) return vdFromMs(parseInt(s, 10));

  // dd/mm/yyyy atau d/m/yyyy  (juga menerima pemisah "-" dan ".")
  var m = s.match(/^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})/);
  if (m) {
    var dd = parseInt(m[1], 10), mm = parseInt(m[2], 10), yy = parseInt(m[3], 10);
    if (mm >= 1 && mm <= 12 && dd >= 1 && dd <= 31) {
      return vdFromMs(Date.UTC(yy, mm - 1, dd));
    }
    return null;
  }

  // yyyy-mm-dd (opsional diikuti waktu)
  m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) {
    return vdFromMs(Date.UTC(parseInt(m[1], 10), parseInt(m[2], 10) - 1, parseInt(m[3], 10)));
  }

  var t = Date.parse(s);
  if (!isNaN(t)) return vdFromMs(t);
  return null;
}

function vdFromMs(ms) {
  var dt = new Date(ms);
  if (isNaN(dt.getTime())) return null;
  return { ms: ms, key: vdDayKey(ms) };
}

function vdDayKey(ms) {
  var dt = new Date(ms);
  var y = dt.getUTCFullYear();
  var m = dt.getUTCMonth() + 1;
  var d = dt.getUTCDate();
  return y + '-' + (m < 10 ? '0' : '') + m + '-' + (d < 10 ? '0' : '') + d;
}

/**
 * Epoch dengan satuan campur — tab EVENTS di Persada menulis detik di satu node
 * dan milidetik di node lain (lihat konsultasi T3). Dinormalisasi ke ms.
 */
function vdEpochAuto(v) {
  var n = vdNum(v);
  if (n <= 0) return null;
  if (n < 1e11) return n * 1000;   // detik
  return n;                         // milidetik
}

/** "14:32:05" / "14.32" / "14" -> 14. Di luar 0..23 -> null. */
function vdParseHour(v) {
  var s = vdStr(v);
  if (s === '') return null;
  var m = s.match(/^(\d{1,2})\s*[:.]/);
  var h = m ? parseInt(m[1], 10) : parseInt(s, 10);
  if (!isFinite(h) || h < 0 || h > 23) return null;
  return h;
}

/** bot_mode aktif kecuali persis "OFF". Kosong = aktif (sesuai logika kedua workflow). */
function vdBotOn(v) {
  return vdStr(v).toUpperCase() !== 'OFF';
}

/** Ambil nilai kolom pertama yang tidak kosong (map bisa string atau array). */
function vdPick(row, spec) {
  if (!spec) return '';
  var list = Object.prototype.toString.call(spec) === '[object Array]' ? spec : [spec];
  for (var i = 0; i < list.length; i++) {
    var v = row ? row[list[i]] : '';
    if (!vdIsBlank(v)) return vdStr(v);
  }
  return '';
}

/**
 * Baris di Google Sheets kadang punya header ber-trailing-space
 * (dikonfirmasi di STATS Persada: "pending_survey_tanggal "). Lookup toleran
 * supaya kolom seperti itu tetap terbaca dan tidak diam-diam kosong.
 */
function vdRowGet(row, col) {
  if (!row) return '';
  if (Object.prototype.hasOwnProperty.call(row, col)) return vdStr(row[col]);
  var want = String(col).trim().toLowerCase();
  for (var k in row) {
    if (!Object.prototype.hasOwnProperty.call(row, k)) continue;
    if (String(k).trim().toLowerCase() === want) return vdStr(row[k]);
  }
  return '';
}

function vdRows(tabs, name) {
  var r = tabs ? tabs[name] : null;
  return Object.prototype.toString.call(r) === '[object Array]' ? r : [];
}

/** Buang baris kosong total (Sheets sering mengembalikan baris hantu). */
function vdNonEmptyRows(rows) {
  var out = [];
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    if (!r || typeof r !== 'object') continue;
    var any = false;
    for (var k in r) {
      if (!Object.prototype.hasOwnProperty.call(r, k)) continue;
      if (k === 'row_number') continue;
      if (!vdIsBlank(r[k])) { any = true; break; }
    }
    if (any) out.push(r);
  }
  return out;
}

/* ------------------------------------------------------------ agregator */

var VD_RANGES = [7, 30, 90];

function vdCountInRange(dayKeys, nowMs, days) {
  var floor = nowMs - (days * 86400000);
  var n = 0;
  for (var i = 0; i < dayKeys.length; i++) {
    if (dayKeys[i] !== null && dayKeys[i] >= floor) n++;
  }
  return n;
}

function vdRangeValues(msList, nowMs) {
  var out = {};
  for (var i = 0; i < VD_RANGES.length; i++) {
    out[String(VD_RANGES[i])] = vdCountInRange(msList, nowMs, VD_RANGES[i]);
  }
  return out;
}

/** Distribusi nilai -> {labels, data}. Top N, sisanya digabung "Lainnya". */
function vdDistribution(values, topN) {
  var counts = {};
  for (var i = 0; i < values.length; i++) {
    var v = vdStr(values[i]);
    if (v === '') continue;
    // Nilai multi-value dipisah koma (mis. kelas_anak "SMP 1, SMA 12").
    var parts = v.split(',');
    for (var j = 0; j < parts.length; j++) {
      var p = parts[j].trim();
      if (p === '') continue;
      counts[p] = (counts[p] || 0) + 1;
    }
  }
  var pairs = [];
  for (var k in counts) {
    if (Object.prototype.hasOwnProperty.call(counts, k)) pairs.push([k, counts[k]]);
  }
  pairs.sort(function (a, b) { return b[1] - a[1] || (a[0] < b[0] ? -1 : 1); });

  var n = topN || 6;
  var labels = [], data = [];
  for (var x = 0; x < pairs.length && x < n; x++) { labels.push(pairs[x][0]); data.push(pairs[x][1]); }
  if (pairs.length > n) {
    var rest = 0;
    for (var y = n; y < pairs.length; y++) rest += pairs[y][1];
    labels.push('Lainnya'); data.push(rest);
  }
  return { labels: labels, data: data };
}

/* --------------------------------------------------- pembangun tabel umum */

function vdSortRows(rows, sort) {
  if (!sort || !sort.col) return rows;
  var dir = sort.dir === 'asc' ? 1 : -1;
  var copy = rows.slice();
  copy.sort(function (a, b) {
    var av = vdRowGet(a, sort.col), bv = vdRowGet(b, sort.col);
    var ad = vdParseDate(av), bd = vdParseDate(bv);
    if (ad && bd) return (ad.ms - bd.ms) * dir;
    var an = parseFloat(av), bn = parseFloat(bv);
    if (isFinite(an) && isFinite(bn)) return (an - bn) * dir;
    if (av === bv) return 0;
    return (av < bv ? -1 : 1) * dir;
  });
  return copy;
}

function vdBuildTable(spec, tabs) {
  var raw = vdNonEmptyRows(vdRows(tabs, spec.tab));
  var sorted = vdSortRows(raw, spec.sort);
  var limit = spec.limit || 200;
  var rows = [];
  for (var i = 0; i < sorted.length && i < limit; i++) {
    var src = sorted[i];
    var out = {};
    for (var c = 0; c < spec.columns.length; c++) {
      var col = spec.columns[c];
      var val = vdRowGet(src, col.col);
      if (col.type === 'epoch_auto') {
        var ms = vdEpochAuto(val);
        out[col.col] = ms ? vdDayKey(ms) : '';
      } else {
        out[col.col] = val;
      }
    }
    rows.push(out);
  }
  return {
    id: spec.id,
    title: spec.title,
    // Penjelasan asal data. Opsional: tabel tanpa `hint` tetap sah, frontend
    // hanya tidak menampilkan tombol "i" untuknya.
    hint: spec.hint || '',
    empty: spec.empty || 'Belum ada data.',
    truncated: sorted.length > limit,
    total: sorted.length,
    columns: spec.columns.map(function (c) {
      return { key: c.col, label: c.label, type: c.type === 'epoch_auto' ? 'text' : c.type };
    }),
    rows: rows
  };
}

/* ------------------------------------------ ringkasan bulanan (generik) */

var VD_BULAN_ID = ['Januari','Februari','Maret','April','Mei','Juni',
                   'Juli','Agustus','September','Oktober','November','Desember'];

/** "2026-09" -> "September 2026". Kalau bukan format bulan, kembalikan apa adanya. */
function vdMonthLabel(key) {
  var m = /^(\d{4})-(\d{2})$/.exec(vdStr(key));
  if (!m) return vdStr(key);
  var idx = parseInt(m[2], 10) - 1;
  if (idx < 0 || idx > 11) return vdStr(key);
  return VD_BULAN_ID[idx] + ' ' + m[1];
}

/** id snake_case -> label enak dibaca. labelMap dari tenant menang duluan. */
function vdPrettyLabel(id, labelMap) {
  var s = vdStr(id);
  if (s === '') return '';
  if (labelMap && Object.prototype.hasOwnProperty.call(labelMap, s)) return labelMap[s];
  if (s.indexOf('NEW:') === 0) return 'Baru: ' + vdPrettyLabel(s.slice(4), labelMap);
  s = s.replace(/_/g, ' ');
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** Ambil baris bulan terbaru (kunci YYYY-MM, urut leksikografis = urut waktu). */
function vdLatestMonthRow(rows, monthCol) {
  var best = null, bestKey = '';
  for (var i = 0; i < rows.length; i++) {
    var k = vdStr(vdRowGet(rows[i], monthCol));
    if (!/^\d{4}-\d{2}$/.test(k)) continue;
    if (k > bestKey) { bestKey = k; best = rows[i]; }
  }
  return best;
}

function vdSafeJsonArray(raw) {
  var v = vdStr(raw);
  if (v === '') return [];
  try {
    var parsed = JSON.parse(v);
    return Object.prototype.toString.call(parsed) === '[object Array]' ? parsed : [];
  } catch (e) { return []; }
}

/**
 * Ubah satu baris ringkasan bulanan jadi KPI + doughnut + tabel.
 * Semua nama kolom datang dari spec tenant -- tidak ada yang spesifik klien.
 * Chart SENGAJA tanpa `rangeAware`: granularitasnya bulan, bukan hari, jadi
 * selektor 7/30/90 hari harus mengabaikannya (lihat API contract).
 */
/**
 * Penjelasan untuk kartu ringkasan bulanan.
 *
 * Peringatan soal kebasian sengaja ikut ditulis: `vdLatestMonthRow` mengambil
 * baris bulan TERBARU yang ada di tab, bukan "bulan lalu" yang dihitung dari
 * tanggal hari ini. Kalau tab ringkasan berhenti diisi, kartunya akan terus
 * menampilkan bulan lama tanpa tanda apa pun — dan pembacanya tidak punya cara
 * tahu selain dari label bulan di judul. Kalimat ini yang memberi tahu.
 */
function vdMonthlyHint(spec, monthTxt) {
  return 'Dari tab ' + vdStr(spec.tab) + ', baris bulan terbaru yang ada di sheet' +
         (monthTxt ? ' (' + monthTxt + ')' : '') + '. ' +
         'Angka ini TIDAK mengikuti filter 7/30/90 hari, dan tidak berubah sampai ' +
         'baris bulan berikutnya ditambahkan ke tab itu.';
}

function vdBuildMonthly(spec, tabs, labelMap) {
  var out = { kpis: [], charts: [], tables: [], insights: [] };
  if (!spec || !spec.tab) return out;

  var row = vdLatestMonthRow(vdNonEmptyRows(vdRows(tabs, spec.tab)), spec.monthCol || 'bulan');
  var monthKey = row ? vdStr(vdRowGet(row, spec.monthCol || 'bulan')) : '';
  var monthTxt = monthKey ? vdMonthLabel(monthKey) : 'belum ada data';
  var note = row ? vdStr(vdRowGet(row, spec.noteCol)) : '';

  for (var k = 0; k < (spec.kpis || []).length; k++) {
    var kp = spec.kpis[k];
    out.kpis.push({
      id: kp.id, label: kp.label, tone: kp.tone || 'blue',
      value: row ? vdInt(vdRowGet(row, kp.col)) : 0,
      hint: (kp.hint || '') + (monthKey ? ' (' + monthTxt + ')' : '')
    });
  }

  var top = row ? vdSafeJsonArray(vdRowGet(row, spec.topCol || 'top_json')) : [];
  var labelKey = spec.labelKey || 'topic';
  var valueKey = spec.valueKey || 'users';

  var chartN = spec.chartTop || 5;
  var cLabels = [], cData = [];
  for (var c = 0; c < top.length && c < chartN; c++) {
    cLabels.push(vdPrettyLabel(top[c][labelKey], labelMap));
    cData.push(vdInt(top[c][valueKey]));
  }
  out.charts.push({
    id: spec.id + '_chart',
    // Penanda mesin, bukan label. Node rekomendasi memakainya untuk menemukan
    // blok topik tanpa menebak-nebak id atau judul yang bisa diubah per tenant.
    source: 'monthly_topics',
    type: 'doughnut',
    title: (spec.chartTitle || 'Topik Terbanyak') + ' — ' + monthTxt,
    hint: vdMonthlyHint(spec, monthTxt),
    labels: cLabels,
    series: [{ name: 'User', data: cData, color: 'palette' }],
    empty: cLabels.length === 0
  });

  var tRows = [];
  for (var t = 0; t < top.length; t++) {
    tRows.push({
      topik: vdPrettyLabel(top[t][labelKey], labelMap),
      user: vdInt(top[t][valueKey]),
      persen: vdStr(top[t].pct) === '' ? '' : top[t].pct + '%',
      pesan: vdInt(top[t].messages)
    });
  }
  /* Rekomendasi AI: dibaca dari sel, tidak pernah dihitung di sini. */
  var insight = vdInsightFromMonthly(spec, row, monthTxt);
  if (insight) out.insights.push(insight);

  out.tables.push({
    id: spec.id + '_table',
    source: 'monthly_topics',
    month: monthTxt,
    title: (spec.tableTitle || 'Peringkat Topik') + ' — ' + monthTxt,
    hint: vdMonthlyHint(spec, monthTxt),
    empty: note || 'Belum ada ringkasan bulanan.',
    note: note,
    truncated: false,
    total: tRows.length,
    columns: [
      { key: 'topik',  label: 'Topik',      type: 'text' },
      { key: 'user',   label: 'User',       type: 'int'  },
      { key: 'persen', label: '% User',     type: 'text' },
      { key: 'pesan',  label: 'Pesan',      type: 'int'  }
    ],
    rows: tRows
  });

  return out;
}

/**
 * vdLeadRow — mengubah SATU baris mentah tab STATS menjadi objek lead yang
 * dikirim ke frontend.
 *
 * Dipisah jadi fungsi sendiri karena dipakai dua kali: oleh vdBuildPayload
 * (seluruh direktori lead) dan oleh jalur `add_lead` (satu baris yang baru
 * saja ditulis, dikembalikan ke frontend supaya tabel bisa diperbarui tanpa
 * refetch). Kalau bentuknya dibangun dua kali di dua tempat, cepat atau
 * lambat keduanya akan berbeda — dan bedanya baru ketahuan sebagai baris
 * yang tampil aneh setelah user menambah nomor.
 *
 * Mengembalikan null kalau baris tidak punya identitas sama sekali
 * (wa maupun lid kosong) — baris seperti itu tidak bisa di-toggle dan tidak
 * boleh muncul di direktori.
 *
 * Selain `lead`, ikut dikembalikan hasil parse yang mahal (tanggal & jam)
 * supaya pemanggil tidak perlu menghitungnya ulang untuk agregat.
 */
function vdLeadRow(profile, r) {
  var wa = vdPick(r, profile.map.wa);
  var lid = vdPick(r, profile.map.lid);
  if (wa === '' && lid === '') return null;

  var key = wa !== '' ? wa : lid;
  var digits = vdDigits(key);
  var on = vdBotOn(vdPick(r, profile.map.bot_mode));
  var cnt = vdInt(vdPick(r, profile.map.counter));
  var fd = vdParseDate(vdPick(r, profile.map.first_chat));
  var ld = vdParseDate(vdPick(r, profile.map.last_chat));
  var hh = vdParseHour(vdPick(r, profile.map.last_hour));
  var segment = vdPick(r, profile.map.segment);
  var stage = vdPick(r, profile.map.stage);

  // detail drawer
  var detail = [];
  for (var f = 0; f < (profile.detailFields || []).length; f++) {
    var df = profile.detailFields[f];
    var dv = vdRowGet(r, df.col);
    if (dv !== '') detail.push({ label: df.label, value: dv });
  }

  return {
    lead: {
      // `key` adalah nilai yang dipakai untuk mencocokkan baris saat toggle.
      key: key,
      wa: wa,
      lid: lid,
      // LID = identitas WhatsApp tanpa nomor asli; ditandai supaya owner tahu
      // nomor itu tidak bisa dihubungi manual.
      is_lid: digits.length >= 15 || (wa === '' && lid !== ''),
      nama: vdPick(r, profile.map.nama),
      segment: segment,
      stage: stage,
      counter: cnt,
      first_chat: fd ? fd.key : '',
      last_chat: ld ? ld.key : '',
      bot_mode: on ? 'ON' : 'OFF',
      detail: detail
    },
    on: on,
    cnt: cnt,
    fd: fd,
    ld: ld,
    hh: hh,
    segment: segment,
    stage: stage
  };
}

/* ================================================== TAMBAH LEAD (add_lead) ==
 *
 * Tiga fungsi di bawah memuat SELURUH keputusan jalur add_lead. Sengaja murni
 * (tidak menyentuh $input, Google Sheets, maupun jam) supaya bisa dijalankan
 * apa adanya oleh qa/selftest.html. Code node di n8n hanya membungkus: ambil
 * input, panggil fungsi ini, kembalikan hasilnya.
 *
 * Kalau logikanya ditulis langsung di dalam Code node, ia tidak akan pernah
 * bisa diuji — dan jalur ini adalah satu-satunya jalur yang MEMBUAT baris
 * baru di sheet produksi.
 */

/**
 * Kolom yang wajib ada PERSIS di tab STATS supaya baris baru bisa ditulis.
 * Pemeriksaannya sengaja tidak toleran spasi seperti vdRowGet: node Sheets
 * menulis ke nama kolom apa adanya, jadi header "Nama " (dengan spasi di
 * ujung) akan melahirkan kolom kedua yang tidak pernah dibaca bot.
 */
var VD_ADD_LEAD_COLUMNS = ['No WA', 'Nama', 'bot_mode', 'Counter'];

/**
 * vdPrepareAddLead — validasi & normalisasi permintaan tambah lead.
 * @param {object} profile entri VIRA_TENANTS
 * @param {object} req     { key, nama, mode } apa adanya dari client
 * @returns {object} { ok:true, key, nama, mode } atau { ok:false, error, message }
 */
function vdPrepareAddLead(profile, req) {
  req = req || {};
  var mode = vdStr(req.mode).toUpperCase();
  var rawKey = vdStr(req.key);
  var nama = vdStr(req.nama);

  if (!profile) {
    return { ok: false, error: 'TENANT_UNKNOWN', message: 'Tenant tidak dikenal.' };
  }
  if (mode !== 'ON' && mode !== 'OFF') {
    return { ok: false, error: 'BAD_REQUEST', message: 'Mode harus ON atau OFF.' };
  }
  if (rawKey === '') {
    return { ok: false, error: 'BAD_REQUEST', message: 'Nomor WhatsApp wajib diisi.' };
  }
  if (nama.length > 80) {
    return { ok: false, error: 'BAD_REQUEST', message: 'Nama maksimal 80 karakter.' };
  }

  var wa = vdNormalizeWa(rawKey);
  if (wa === '') {
    return { ok: false, error: 'BAD_NUMBER',
      message: 'Nomor "' + rawKey + '" tidak terbaca sebagai nomor WhatsApp. ' +
               'Contoh yang benar: 081234567890 atau 6281234567890.' };
  }

  return { ok: true, key: wa, nama: nama, mode: mode };
}

/**
 * vdCheckAddLead — pagar terakhir sebelum menulis. Menolak tiga keadaan,
 * semuanya lebih baik gagal keras daripada terlanjur menulis:
 *
 *   SHEET_UNREADABLE  tab tidak terbaca -> jangan append buta
 *   DUPLICATE         nomor sudah ada   -> "No WA" ganda membuat Update Bot
 *                     Mode dan Follow-up (yang mencocokkan "No WA") ambigu
 *   SHEET_SCHEMA      header tidak persis -> data mendarat di kolom baru
 *                     yang tidak dibaca siapa pun
 *
 * Pencocokan identitas memakai prinsip yang sama dengan Find Row: No WA
 * primer, lid cadangan, dan tidak pernah jatuh ke rows[0].
 *
 * @param {object} profile entri VIRA_TENANTS
 * @param {array}  rows    baris mentah tab STATS
 * @param {string} key     nomor yang sudah dinormalkan
 * @param {string} tabName nama tab, hanya untuk pesan error
 */
function vdCheckAddLead(profile, rows, key, tabName) {
  var tab = vdStr(tabName) || 'STATS';
  var list = Object.prototype.toString.call(rows) === '[object Array]' ? rows : [];
  var i;

  // Baris hantu dari Sheets hanya membawa row_number; butuh baris asli untuk
  // membaca header. Sheet yang benar-benar kosong bukan keadaan normal untuk
  // tenant mana pun, jadi diperlakukan sebagai gagal baca.
  //
  // Item BERTANDA _claims/_cors juga dibuang. Node pembaca memakai
  // onError:continueRegularOutput, jadi kalau pembacaan gagal (credential
  // belum dipilih, kuota habis, jaringan) n8n meneruskan item kendali kita
  // sendiri ke sini. Tanpa penyaringan ini item itu dikira baris sheet, lalu
  // pemeriksaan header menuduh SHEET_SCHEMA — menunjuk ke sheet padahal yang
  // rusak adalah pembacaannya. Pesan yang salah arah lebih mahal daripada
  // tidak ada pesan: yang membaca akan mengutak-atik header yang sudah benar.
  var usable = [];
  for (i = 0; i < list.length; i++) {
    var r = list[i];
    if (!r || typeof r !== 'object') continue;
    if (Object.prototype.hasOwnProperty.call(r, '_claims') ||
        Object.prototype.hasOwnProperty.call(r, '_cors') ||
        Object.prototype.hasOwnProperty.call(r, '_route')) continue;
    var keys = [];
    for (var k in r) {
      if (Object.prototype.hasOwnProperty.call(r, k) && k !== 'row_number') keys.push(k);
    }
    if (keys.length > 0) usable.push(r);
  }
  if (usable.length === 0) {
    return { ok: false, error: 'SHEET_UNREADABLE',
      message: 'Tab ' + tab + ' tidak terbaca, jadi nomor belum ditambahkan. ' +
               'Periksa credential Google Sheets di node Read STATS for Add, ' +
               'lalu coba lagi.' };
  }

  var want = vdDigits(key);
  var dup = null;
  if (want !== '') {
    for (i = 0; i < usable.length; i++) {
      if (vdDigits(vdPick(usable[i], profile.map.wa)) === want) { dup = usable[i]; break; }
    }
    if (!dup) {
      for (i = 0; i < usable.length; i++) {
        if (vdDigits(vdPick(usable[i], profile.map.lid)) === want) { dup = usable[i]; break; }
      }
    }
  }
  if (dup) {
    var dupNama = vdPick(dup, profile.map.nama);
    return { ok: false, error: 'DUPLICATE',
      message: 'Nomor ' + key + ' sudah ada di data' +
               (dupNama ? ' atas nama ' + dupNama : '') +
               '. Cari nomornya di daftar lead untuk mengubah status botnya.' };
  }

  var header = {};
  for (var h in usable[0]) {
    if (Object.prototype.hasOwnProperty.call(usable[0], h)) header[h] = true;
  }
  var missing = [];
  for (i = 0; i < VD_ADD_LEAD_COLUMNS.length; i++) {
    if (!header[VD_ADD_LEAD_COLUMNS[i]]) missing.push(VD_ADD_LEAD_COLUMNS[i]);
  }
  if (missing.length > 0) {
    // Header yang benar-benar ada ikut disebut. Tanpa ini, kolom yang salah
    // hanya karena spasi di ujung terlihat "sudah ada" bagi yang membaca
    // pesannya, dan ia akan mencari masalah di tempat yang salah.
    var found = [];
    for (var f in header) {
      if (Object.prototype.hasOwnProperty.call(header, f) && f !== 'row_number') {
        found.push('"' + f + '"');
      }
    }
    return { ok: false, error: 'SHEET_SCHEMA',
      message: 'Kolom ' + missing.join(', ') + ' tidak ditemukan persis di tab ' + tab +
               '. Header yang terbaca: ' + found.slice(0, 12).join(', ') +
               (found.length > 12 ? ', …' : '') +
               '. Perhatikan spasi di ujung nama kolom.' };
  }

  return { ok: true };
}

/**
 * vdAddLeadCells — nilai yang benar-benar ditulis ke sheet.
 * Nama kosong diisi nomornya sendiri, mengikuti perilaku yang sudah ada untuk
 * lead yang belum pernah menyebutkan namanya.
 */
function vdAddLeadCells(prep) {
  return {
    'No WA': prep.key,
    'Nama': prep.nama !== '' ? prep.nama : prep.key,
    'bot_mode': prep.mode,
    'Counter': 0
  };
}

/**
 * vdAddLeadRow — baris lead untuk dikirim balik ke frontend, dibangun lewat
 * vdLeadRow() yaitu jalur yang sama dengan `stats`. Kalau dibentuk manual,
 * baris hasil tambah akan pelan-pelan berbeda dari baris hasil muat ulang.
 */
function vdAddLeadRow(profile, cells) {
  var sheetRow = {
    'No WA': cells['No WA'],
    'Nama': cells['Nama'],
    'bot_mode': cells['bot_mode'],
    'Counter': cells['Counter'],
    'lid': ''
  };
  var built = vdLeadRow(profile, sheetRow);
  return built ? built.lead : null;
}

/* ------------------------------------------- sebaran hari & jam --------- */

/**
 * Label tetap. Senin lebih dulu karena itu cara orang membaca minggu kerja;
 * getUTCDay() menaruh Minggu di indeks 0, jadi indeksnya digeser saat dihitung.
 */
var VD_DOW_LABELS = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];

/** vdDowCounts — 7 angka, dari daftar epoch ms. null diabaikan. */
function vdDowCounts(msList) {
  var out = [0, 0, 0, 0, 0, 0, 0];
  var list = Object.prototype.toString.call(msList) === '[object Array]' ? msList : [];
  for (var i = 0; i < list.length; i++) {
    if (list[i] === null || list[i] === undefined) continue;
    var wd = new Date(list[i]).getUTCDay();
    if (isNaN(wd)) continue;
    out[(wd + 6) % 7]++;
  }
  return out;
}

/**
 * Selisih WIB terhadap UTC. Dipakai untuk epoch mentah dari TOPIC_LOG
 * (first_ts/last_ts berupa milidetik). Tanpa pergeseran ini, "jam tersibuk"
 * meleset tujuh jam — dan tidak ada yang akan sadar dari melihat angkanya.
 */
var VD_WIB_OFFSET_MS = 7 * 3600 * 1000;

/** Geser daftar epoch ke WIB, supaya bagian UTC-nya bisa dibaca sebagai WIB. */
function vdWibShift(msList) {
  var list = Object.prototype.toString.call(msList) === '[object Array]' ? msList : [];
  var out = [];
  for (var i = 0; i < list.length; i++) {
    var v = vdNum(list[i]);
    if (v > 0) out.push(v + VD_WIB_OFFSET_MS);
  }
  return out;
}

/** Jam WIB (0..23) dari daftar epoch milidetik. */
function vdWibHours(msList) {
  var shifted = vdWibShift(msList);
  var out = [];
  for (var i = 0; i < shifted.length; i++) {
    var h = new Date(shifted[i]).getUTCHours();
    if (!isNaN(h)) out.push(h);
  }
  return out;
}

/** vdHourLabels — "00".."23". */
function vdHourLabels() {
  var out = [];
  for (var h = 0; h < 24; h++) out.push((h < 10 ? '0' : '') + h);
  return out;
}

/** vdHourCounts — 24 angka, dari daftar jam 0..23. Di luar rentang diabaikan. */
function vdHourCounts(hours) {
  var out = [];
  for (var i = 0; i < 24; i++) out.push(0);
  var list = Object.prototype.toString.call(hours) === '[object Array]' ? hours : [];
  for (var j = 0; j < list.length; j++) {
    var h = list[j];
    if (typeof h !== 'number' || h < 0 || h > 23) continue;
    out[h]++;
  }
  return out;
}

/**
 * vdStatsTimes — tarik tanggal & jam chat terakhir dari baris STATS mentah.
 *
 * Ada supaya WF-B bisa menghitung sebaran hari/jam dengan kode yang SAMA
 * dengan dashboard. Kalau keduanya menghitung sendiri-sendiri, angka di kartu
 * dan angka yang dipakai AI pelan-pelan akan berbeda — dan sarannya jadi
 * tidak bisa dicek balik ke layar.
 */
function vdStatsTimes(profile, rows) {
  var lastMs = [], hours = [];
  var list = Object.prototype.toString.call(rows) === '[object Array]' ? rows : [];
  for (var i = 0; i < list.length; i++) {
    var r = list[i];
    if (!r || typeof r !== 'object') continue;
    var ld = vdParseDate(vdPick(r, profile.map.last_chat));
    if (ld) lastMs.push(ld.ms);
    var hh = vdParseHour(vdPick(r, profile.map.last_hour));
    if (hh !== null) hours.push(hh);
  }
  return { lastMs: lastMs, hours: hours };
}

/* ============================================ REKOMENDASI AI (insights) ==
 *
 * Dashboard TIDAK memanggil AI. Ia hanya membaca kolom `ai_insight_json` di
 * tab MONTHLY_SUMMARY, yang diisi WF-B (Monthly Rollup) sekali sebulan.
 *
 * Ini bukan pilihan gaya. Versi pertama menaruh panggilan Anthropic di dalam
 * jalur permintaan dashboard; panggilan LLM melampaui batas tunggu frontend
 * dan halaman jadi GAGAL DIMUAT — bukan sekadar kartunya hilang. Dengan
 * membaca kolom, tidak ada lagi jalan bagi kegagalan atau kelambatan AI untuk
 * menyentuh pemuatan dashboard.
 *
 * Bentuk isi sel yang diharapkan:
 *   {"model":"…","generated_at":1756…,"items":[ {judul,alasan,aksi,dampak,dasar} ]}
 * Array telanjang juga diterima, supaya sel yang diisi tangan tetap terbaca.
 */

/** Nilai `dampak` yang sah. Di luar ini dipaksa jadi 'sedang'. */
var VD_INSIGHT_TONE = { tinggi: 1, sedang: 1, rendah: 1 };

/**
 * vdInsightItems — bersihkan dan batasi daftar rekomendasi.
 *
 * Butir tanpa `judul` atau `aksi` DIBUANG, bukan ditampilkan separuh: saran
 * yang terpotong akan dibaca sebagai saran utuh oleh yang melihatnya.
 * Isinya berasal dari keluaran model, jadi panjangnya dipangkas di sini —
 * bukan di CSS — supaya satu balasan yang meleset tidak merusak tata letak.
 */
function vdInsightItems(raw) {
  var list = Object.prototype.toString.call(raw) === '[object Array]' ? raw : [];
  var out = [];
  for (var i = 0; i < list.length && out.length < 4; i++) {
    var it = list[i] || {};
    var judul = vdStr(it.judul);
    var aksi = vdStr(it.aksi);
    if (judul === '' || aksi === '') continue;

    var dasar = [];
    var src = Object.prototype.toString.call(it.dasar) === '[object Array]' ? it.dasar : [];
    for (var d = 0; d < src.length && dasar.length < 4; d++) {
      var v = vdStr(src[d]);
      if (v !== '') dasar.push(v.slice(0, 80));
    }

    var tone = vdStr(it.dampak).toLowerCase();
    out.push({
      judul: judul.slice(0, 120),
      alasan: vdStr(it.alasan).slice(0, 400),
      aksi: aksi.slice(0, 400),
      dampak: VD_INSIGHT_TONE[tone] ? tone : 'sedang',
      dasar: dasar
    });
  }
  return out;
}

/**
 * vdInsightFromMonthly — susun blok `insights` dari sel MONTHLY_SUMMARY.
 *
 * Mengembalikan null untuk APA PUN yang tidak beres: kolom belum ada, sel
 * kosong, JSON rusak, atau tidak ada butir yang lolos pembersihan. Blok yang
 * hilang berarti kartunya tidak tampil dan sisa dashboard normal — jauh lebih
 * baik daripada kartu setengah jadi.
 */
function vdInsightFromMonthly(spec, row, monthTxt) {
  if (!spec || !row) return null;
  var cell = vdRowGet(row, spec.insightCol || 'ai_insight_json');
  if (cell === '') return null;

  var parsed;
  try { parsed = JSON.parse(cell); } catch (e) { return null; }
  if (!parsed) return null;

  var isArray = Object.prototype.toString.call(parsed) === '[object Array]';
  var items = vdInsightItems(isArray ? parsed : parsed.items);
  if (items.length === 0) return null;

  var bulan = vdStr(monthTxt);
  return {
    id: 'ai_insight',
    title: (vdStr(spec.insightTitle) || 'AI Insight dari Topik') +
           (bulan ? ' — ' + bulan : ''),
    hint: 'Disusun otomatis oleh AI dari ringkasan topik bulan' +
          (bulan ? ' ' + bulan : ' itu') + '. Ini SARAN, bukan fakta — angka ' +
          'pendukungnya sengaja ditampilkan supaya bisa dicek balik ke kartu ' +
          'di atas. Dihitung sekali saat rekap bulanan dibuat, bukan setiap ' +
          'kali dashboard dibuka.',
    generated_at: isArray ? 0 : vdInt(parsed.generated_at),
    model: isArray ? '' : vdStr(parsed.model),
    items: items
  };
}

/* ================================================================ MAIN ==== */

/**
 * @param {object} profile  entri dari VIRA_TENANTS
 * @param {object} tabs     { NAMA_TAB: [ {kolom: nilai}, ... ] }
 * @param {object} opts     { nowMs, cached, generatedAt }
 * @returns {object} payload sesuai API contract (tanpa blok `session`)
 */
function vdBuildPayload(profile, tabs, opts) {
  opts = opts || {};
  var nowMs = opts.nowMs || Date.now();

  var statsRows = vdNonEmptyRows(vdRows(tabs, profile.statsTab || 'STATS'));

  /* ---- normalisasi baris lead ---- */
  var leads = [];
  var firstMs = [], lastMs = [], hours = [];
  var botOn = 0, botOff = 0, chatVolume = 0;
  var segVals = [], stageVals = [];
  var extraColVals = {};   // untuk distribution berbasis kolom mentah

  for (var i = 0; i < statsRows.length; i++) {
    var r = statsRows[i];
    var built = vdLeadRow(profile, r);
    if (!built) continue;   // baris tanpa identitas -> abaikan

    if (built.on) botOn++; else botOff++;
    chatVolume += built.cnt;

    firstMs.push(built.fd ? built.fd.ms : null);
    lastMs.push(built.ld ? built.ld.ms : null);
    if (built.hh !== null) hours.push(built.hh);

    segVals.push(built.segment);
    stageVals.push(built.stage);

    // kumpulkan kolom mentah yang dibutuhkan distribution
    for (var dIdx = 0; dIdx < (profile.distributions || []).length; dIdx++) {
      var dsp = profile.distributions[dIdx];
      if (dsp.col) {
        if (!extraColVals[dsp.col]) extraColVals[dsp.col] = [];
        extraColVals[dsp.col].push(vdRowGet(r, dsp.col));
      }
    }

    leads.push(built.lead);
  }

  /* ---- UNKNOWN (pertanyaan tak terjawab) ---- */
  var unkSpec = profile.unknownTable;
  var unkRows = vdNonEmptyRows(vdRows(tabs, unkSpec ? unkSpec.tab : 'UNKNOWN'));
  var unkMs = [];
  for (var u = 0; u < unkRows.length; u++) {
    var ud = vdParseDate(vdRowGet(unkRows[u], 'Tanggal'));
    unkMs.push(ud ? ud.ms : null);
  }

  /* ---- KPI ---- */
  var total = leads.length;
  var kpis = [
    { id: 'total_leads', label: 'Total Lead', tone: 'blue', value: total,
      hint: 'Nomor unik yang pernah chat (baris STATS dengan identitas terisi)' },
    { id: 'new_leads', label: 'Lead Baru', tone: 'teal', rangeAware: true,
      values: vdRangeValues(firstMs, nowMs), value: vdCountInRange(firstMs, nowMs, 30),
      hint: 'Lead dengan tanggal chat pertama di dalam rentang' },
    { id: 'active_leads', label: 'Lead Aktif', tone: 'green', rangeAware: true,
      values: vdRangeValues(lastMs, nowMs), value: vdCountInRange(lastMs, nowMs, 30),
      hint: 'Lead yang chat terakhirnya di dalam rentang' },
    { id: 'chat_volume', label: 'Total Chat', tone: 'purple', value: chatVolume,
      hint: 'Jumlah kolom Counter seluruh lead. Perkiraan — increment bisa hilang saat pesan bersamaan.' },
    { id: 'bot_on', label: 'Bot Aktif', tone: 'green', value: botOn,
      sub: total ? Math.round(botOn * 100 / total) + '% dari total' : '',
      hint: 'bot_mode bukan OFF' },
    { id: 'bot_off', label: 'Diambil Alih Manual', tone: 'orange', value: botOff,
      sub: total ? Math.round(botOff * 100 / total) + '% dari total' : '',
      hint: 'bot_mode = OFF, percakapan dipegang manusia' },
    { id: 'unanswered', label: 'Pertanyaan Tak Terjawab', tone: 'red', rangeAware: true,
      values: vdRangeValues(unkMs, nowMs), value: vdCountInRange(unkMs, nowMs, 30),
      hint: 'Baris di tab UNKNOWN dalam rentang' }
  ];

  for (var e = 0; e < (profile.extraKpis || []).length; e++) {
    var ek = profile.extraKpis[e];
    var val = 0;
    if (ek.agg === 'count_rows') {
      val = vdNonEmptyRows(vdRows(tabs, ek.tab)).length;
    } else if (ek.agg === 'count_nonempty') {
      var src = vdNonEmptyRows(vdRows(tabs, ek.tab));
      for (var s2 = 0; s2 < src.length; s2++) {
        if (vdRowGet(src[s2], ek.col) !== '') val++;
      }
    } else if (ek.agg === 'sum') {
      var src2 = vdNonEmptyRows(vdRows(tabs, ek.tab));
      for (var s3 = 0; s3 < src2.length; s3++) val += vdNum(vdRowGet(src2[s3], ek.col));
    }
    kpis.push({ id: ek.id, label: ek.label, tone: ek.tone || 'blue', value: val, hint: ek.hint || '' });
  }

  /* ---- Chart universal ---- */
  // Tren harian 90 hari; frontend memotong sesuai rentang aktif.
  var dayLabels = [], newSeries = [], activeSeries = [];
  var todayMs = Date.UTC(new Date(nowMs).getUTCFullYear(), new Date(nowMs).getUTCMonth(), new Date(nowMs).getUTCDate());
  var newByDay = {}, actByDay = {};
  for (var a = 0; a < firstMs.length; a++) {
    if (firstMs[a] !== null) { var k1 = vdDayKey(firstMs[a]); newByDay[k1] = (newByDay[k1] || 0) + 1; }
    if (lastMs[a] !== null) { var k2 = vdDayKey(lastMs[a]); actByDay[k2] = (actByDay[k2] || 0) + 1; }
  }
  for (var back = 89; back >= 0; back--) {
    var dk = vdDayKey(todayMs - back * 86400000);
    dayLabels.push(dk);
    newSeries.push(newByDay[dk] || 0);
    activeSeries.push(actByDay[dk] || 0);
  }

  var hourCounts = vdHourCounts(hours);
  var hourLabels = vdHourLabels();

  /* Sebaran hari dalam seminggu, dari tanggal chat terakhir tiap lead —
   * sumber yang sama dengan seri "Lead aktif" di chart harian, jadi tidak ada
   * pembacaan sheet tambahan. Tanpa ini tidak ada dasar apa pun untuk saran
   * yang menyebut hari tertentu. */
  var dowLabels = VD_DOW_LABELS;
  var dowCounts = vdDowCounts(lastMs);

  var charts = [
    {
      id: 'daily', type: 'line', title: 'Tren Harian', rangeAware: true,
      hint: 'Dari tab STATS. "Lead baru" dihitung dari tanggal chat pertama, ' +
            '"Lead aktif" dari tanggal chat terakhir. Satu titik = satu hari, ' +
            'dan grafik ini mengikuti filter 7/30/90 hari.',
      labels: dayLabels,
      series: [
        { name: 'Lead baru', data: newSeries, color: 'blue' },
        { name: 'Lead aktif', data: activeSeries, color: 'teal' }
      ]
    },
    {
      id: 'hourly', type: 'bar', title: 'Jam Chat Tersibuk (WIB)',
      hint: 'Dari kolom jam chat terakhir tiap lead di tab STATS. Yang dihitung ' +
            'JUMLAH LEAD per jam, bukan jumlah pesan — satu lead menyumbang satu ' +
            'angka, di jam terakhir ia chat. Tidak mengikuti filter rentang.',
      labels: hourLabels,
      series: [{ name: 'Lead', data: hourCounts, color: 'purple' }],
      note: 'Berdasarkan jam chat terakhir tiap lead.'
    },
    {
      id: 'weekday', type: 'bar', title: 'Hari Tersibuk',
      hint: 'Dari tanggal chat terakhir tiap lead di tab STATS, dikelompokkan ' +
            'per hari dalam seminggu. Yang dihitung JUMLAH LEAD, bukan jumlah ' +
            'pesan. Ini dasar yang dipakai untuk saran yang menyebut hari ' +
            'tertentu — kalau angkanya rata, sarannya tidak boleh menyebut hari.',
      labels: dowLabels,
      series: [{ name: 'Lead', data: dowCounts, color: 'blue' }],
      note: 'Berdasarkan tanggal chat terakhir tiap lead.'
    },
    {
      id: 'botmode', type: 'doughnut', title: 'Status Bot',
      hint: 'Perbandingan seluruh lead di tab STATS berdasarkan kolom bot_mode. ' +
            '"Diambil alih manual" berarti bot_mode = OFF, jadi VIRA berhenti ' +
            'membalas dan percakapannya menunggu dijawab manusia.',
      labels: ['Bot aktif', 'Diambil alih manual'],
      series: [{ name: 'Lead', data: [botOn, botOff], color: ['green', 'orange'] }]
    }
  ];

  for (var dd2 = 0; dd2 < (profile.distributions || []).length; dd2++) {
    var ds = profile.distributions[dd2];
    var vals;
    if (ds.col) vals = extraColVals[ds.col] || [];
    else if (ds.key === 'segment') vals = segVals;
    else if (ds.key === 'stage') vals = stageVals;
    else vals = [];
    var dist = vdDistribution(vals, 6);
    charts.push({
      id: ds.id, type: 'doughnut', title: ds.title,
      hint: ds.hint || '',
      labels: dist.labels,
      series: [{ name: 'Lead', data: dist.data, color: 'palette' }],
      empty: dist.labels.length === 0
    });
  }

  /* ---- Tabel ---- */
  var tables = [];
  if (unkSpec) tables.push(vdBuildTable(unkSpec, tabs));
  for (var t = 0; t < (profile.tables || []).length; t++) {
    tables.push(vdBuildTable(profile.tables[t], tabs));
  }

  /* ---- Ringkasan bulanan (topik) ---- */
  var insights = [];
  if (profile.monthlySummary) {
    var mon = vdBuildMonthly(profile.monthlySummary, tabs, profile.topicLabels);
    for (var mk = 0; mk < mon.kpis.length; mk++) kpis.push(mon.kpis[mk]);
    for (var mc = 0; mc < mon.charts.length; mc++) charts.push(mon.charts[mc]);
    for (var mt = 0; mt < mon.tables.length; mt++) tables.push(mon.tables[mt]);
    for (var mi = 0; mi < mon.insights.length; mi++) insights.push(mon.insights[mi]);
  }

  return {
    ok: true,
    action: 'stats',
    tenant: {
      id: profile.id,
      name: profile.name,
      product: profile.product,
      accent: profile.accent,
      logo: profile.logo || ''
    },
    generated_at: opts.generatedAt || nowMs,
    cached: !!opts.cached,
    kpis: kpis,
    charts: charts,
    leads: {
      title: 'Direktori Lead',
      hint: 'Satu baris per identitas di tab STATS — nomor WhatsApp, atau LID ' +
            'kalau nomornya tidak terekspos. Switch di kolom Bot menulis balik ' +
            'kolom bot_mode ke sheet, jadi mematikannya benar-benar menghentikan ' +
            'VIRA membalas orang itu.',
      columns: profile.leadColumns,
      rows: leads
    },
    tables: tables,
    // Kunci ini SENGAJA hilang kalau kosong. Frontend memperlakukan ketiadaan
    // `insights` sebagai keadaan normal — tidak ada kartu, tidak ada kotak
    // "belum ada data" yang tidak memberi tahu apa pun.
    insights: insights
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    vdBuildPayload: vdBuildPayload,
    vdParseDate: vdParseDate, vdParseHour: vdParseHour, vdBotOn: vdBotOn,
    vdDigits: vdDigits, vdPick: vdPick, vdRowGet: vdRowGet,
    vdDistribution: vdDistribution, vdEpochAuto: vdEpochAuto,
    vdNonEmptyRows: vdNonEmptyRows, vdDayKey: vdDayKey,
    vdNum: vdNum, vdInt: vdInt,
    vdBuildTable: vdBuildTable, vdSortRows: vdSortRows,
    vdLeadRow: vdLeadRow, vdStr: vdStr, vdIsBlank: vdIsBlank,
    vdNormalizeWa: vdNormalizeWa,
    vdPrepareAddLead: vdPrepareAddLead, vdCheckAddLead: vdCheckAddLead,
    vdAddLeadCells: vdAddLeadCells, vdAddLeadRow: vdAddLeadRow,
    vdInsightItems: vdInsightItems, vdInsightFromMonthly: vdInsightFromMonthly,
    vdDowCounts: vdDowCounts, vdHourCounts: vdHourCounts,
    vdWibShift: vdWibShift, vdWibHours: vdWibHours,
    vdHourLabels: vdHourLabels, vdStatsTimes: vdStatsTimes,
    VD_DOW_LABELS: VD_DOW_LABELS
  };
}
