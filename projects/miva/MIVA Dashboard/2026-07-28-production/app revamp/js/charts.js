/* ============================================================================
 * charts.js — CHART SVG BUATAN SENDIRI (bahasa visual bklit UI)
 *
 * Tanpa pustaka. Empat bentuk: line, area, bar, ring (donut).
 *
 * Bagian atas file = fungsi murni (geometri). Tidak menyentuh DOM, bisa diuji
 * langsung. Bagian bawah = renderer yang menempelkan SVG ke elemen.
 *
 * ---------------------------------------------------------------------------
 * KENAPA TAMPILANNYA SEPERTI INI
 *
 * Mengikuti bahasa desain bklit UI (bklit.com/docs/components). Lima keputusan
 * yang membedakannya dari versi lama:
 *
 *  1. KURVA MONOTONE, bukan garis patah. Interpolasi Fritsch–Carlson: mulus
 *     tapi TIDAK PERNAH melewati nilai data (overshoot). Ini penting untuk
 *     dashboard — kurva Catmull-Rom biasa bisa menukik di bawah nol dan
 *     membuat pembaca mengira ada hari dengan lead negatif.
 *  2. ISIAN GRADASI 0.32 → 0 dari atas ke bawah, bukan blok satu opasitas.
 *  3. GRID HORIZONTAL SAJA, putus-putus 4,4. Garis vertikal dihapus; tugas
 *     menandai posisi-x diambil alih crosshair yang muncul saat hover.
 *  4. ANIMASI CLIP-REVEAL 1100ms cubic-bezier(.85,0,.15,1) — chart tersingkap
 *     dari kiri ke kanan. Dijalankan lewat requestAnimationFrame, bukan CSS,
 *     karena properti geometri SVG (width/x) tidak animatable lewat CSS di
 *     semua mesin. Dimatikan otomatis kalau prefers-reduced-motion menyala.
 *  5. LABEL SUMBU-X MEMUDAR saat crosshair lewat (radius 50px), digantikan
 *     "date pill" yang mengikuti crosshair. Jadi tidak ada dua tulisan tanggal
 *     yang bertabrakan di titik yang sama.
 *
 * ---------------------------------------------------------------------------
 * WARNA
 *
 * Sistemnya monokrom. Renderer TIDAK LAGI menerima nama warna dari server —
 * kalau payload n8n mengirim `color: 'purple'`, itu diabaikan. Warna seri
 * selalu diambil berurutan dari --chart-1..--chart-5 di CSS, dan --chart-1
 * adalah --accent (biru VIRA). Konsekuensinya: seri PERTAMA selalu yang
 * berwarna, sisanya ramp abu-abu makin redup. Ini disengaja — satu warna
 * berarti satu penanda; kalau semua seri berwarna, tidak ada yang menonjol.
 *
 * Gridline, sumbu, dan crosshair diwarnai lewat CSS (kelas `.chart-grid`,
 * `.chart-axis`, `.chart-guide`) sehingga ikut berganti sendiri saat tema
 * berpindah. Warna seri TIDAK bisa lewat CSS (itu atribut fill/stroke per
 * elemen), maka dibaca dari custom property saat menggambar — dan app.js
 * menggambar ulang chart setiap kali tema diganti.
 *
 * toneHex() sengaja DIPERTAHANKAN memakai warna asli (biru/hijau/ungu/…)
 * karena satu-satunya pemakainya kini applyAccent() di app.js: itu warna merek
 * tenant, satu-satunya warna berkroma yang diizinkan hidup di halaman.
 * ========================================================================== */
'use strict';

var VDCharts = (function (global) {

  var SVG_NS = 'http://www.w3.org/2000/svg';

  /* Nama tone dipertahankan untuk safeTone()/badgeTone() di render.js. Semua
   * sudah dipetakan ke ramp netral di CSS, jadi urutannya tidak lagi berarti
   * "warna apa" melainkan "seberapa terang". 'blue' dan 'red' sengaja TIDAK
   * ada di sini supaya hash badge tidak pernah mencuri warna aksen atau warna
   * galat. */
  var PALETTE = ['gray', 'teal', 'purple', 'pink', 'green', 'orange'];

  /* Palet merek untuk --accent (BUKAN untuk seri chart). Varian gelap. */
  var TONE_HEX = {
    blue:   '#0a84ff',
    green:  '#30d158',
    teal:   '#40c8e0',
    purple: '#bf5af2',
    orange: '#ff9f0a',
    red:    '#ff453a',
    pink:   '#ff375f',
    gray:   '#98989d'
  };

  /* Varian terang. Nama kunci identik supaya data server tidak perlu tahu tema. */
  var TONE_HEX_LIGHT = {
    blue:   '#007aff',
    green:  '#248a3d',
    teal:   '#0f7f95',
    purple: '#9430c7',
    orange: '#b35c00',
    red:    '#d70015',
    pink:   '#c90f3e',
    gray:   '#6c727f'
  };

  /* Cadangan ramp seri kalau custom property belum terbaca (mis. dipanggil
   * sebelum stylesheet selesai dimuat, atau di lingkungan uji tanpa CSS). */
  var RAMP_FALLBACK_DARK  = ['#0a84ff', '#c3cbd9', '#98a2b3', '#6f7a8d', '#4e5769'];
  var RAMP_FALLBACK_LIGHT = ['#007aff', '#3c4557', '#626c80', '#8d96a8', '#b6bdc9'];

  /* Tetapan bentuk — angka-angka ini menyalin default bklit. */
  var REVEAL_MS      = 1100;   /* animationDuration */
  var GRID_ROWS      = 5;      /* Grid numTicksRows */
  var GRID_DASH      = '4,4';  /* Grid strokeDasharray */
  var AREA_OPACITY   = 0.32;   /* Area fillOpacity (bklit 0.4, diredam sedikit
                                * karena kartu kita sudah bertumpuk di atas
                                * latar kaca — 0.4 membuatnya terlihat keruh) */
  var STROKE_W       = 2;      /* Area/Line strokeWidth */
  var TICKER_HALF    = 50;     /* XAxis tickerHalfWidth — radius pudar label */
  var CROSS_FADE_PCT = 10;     /* ChartTooltip indicatorFadeLength (% tinggi) */
  var RING_STROKE    = 14;     /* RingChart strokeWidth */
  var RING_GAP_DEG   = 2.6;    /* jeda antarsegmen, derajat */
  var MARKER_MAX_PTS = 12;     /* di atas ini penanda titik disembunyikan */

  var uidSeq = 0;

  /* ====================================================== FUNGSI MURNI ==== */

  /** Tema aktif dibaca dari atribut di <html> — satu sumber kebenaran. */
  function currentTheme() {
    try {
      var t = document.documentElement.getAttribute('data-theme');
      return t === 'light' ? 'light' : 'dark';
    } catch (e) { return 'dark'; }
  }

  /** Nilai CSS custom property, dengan cadangan kalau belum terdefinisi. */
  function cssVar(name, fallback) {
    try {
      var v = getComputedStyle(document.documentElement).getPropertyValue(name);
      v = String(v || '').trim();
      return v !== '' ? v : fallback;
    } catch (e) { return fallback; }
  }

  /**
   * Hex untuk sebuah nama tone, mengikuti tema aktif.
   * Dipakai HANYA untuk warna merek tenant (--accent), bukan untuk seri chart.
   */
  function toneHex(name, theme) {
    var table = (theme || currentTheme()) === 'light' ? TONE_HEX_LIGHT : TONE_HEX;
    return table[String(name || '').toLowerCase()] || table.blue;
  }

  /**
   * Warna seri ke-i dari ramp monokrom. i=0 -> --chart-1 (= aksen merek).
   * Melingkar setelah lima langkah.
   */
  function rampColor(i) {
    var k = ((i % 5) + 5) % 5;
    var fb = currentTheme() === 'light' ? RAMP_FALLBACK_LIGHT : RAMP_FALLBACK_DARK;
    return cssVar('--chart-' + (k + 1), fb[k]);
  }

  /** Kompatibilitas: dulu mengembalikan warna kategorikal, kini ramp netral. */
  function paletteHex(i) { return rampColor(i); }

  function num(v) {
    var n = typeof v === 'number' ? v : parseFloat(v);
    return isFinite(n) ? n : 0;
  }

  function round(n) { return Math.round(n * 100) / 100; }

  /**
   * Skala sumbu yang "bulat".
   * niceScale(7)  -> { max:8,  step:2,  ticks:[0,2,4,6,8] }
   * niceScale(0)  -> { max:1,  step:1,  ticks:[0,1] }
   * Selalu dimulai dari 0 karena semua metrik di dashboard ini adalah hitungan.
   */
  function niceScale(max, targetTicks) {
    var t = targetTicks && targetTicks > 0 ? targetTicks : 4;
    var m = num(max);
    if (!(m > 0)) return { max: 1, step: 1, ticks: [0, 1] };

    var raw = m / t;
    var mag = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10));
    var norm = raw / mag;
    var mult = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 2.5 ? 2.5 : norm <= 5 ? 5 : 10;
    var step = mult * mag;

    // Hitungan selalu bilangan bulat; langkah pecahan hanya membingungkan.
    if (m >= 1 && step < 1) step = 1;

    var top = Math.ceil(m / step) * step;
    var ticks = [];
    for (var v = 0; v <= top + step * 1e-9; v += step) {
      ticks.push(Math.round(v * 1e6) / 1e6);
    }
    return { max: top, step: step, ticks: ticks };
  }

  /** Nilai terbesar di seluruh series sebuah chart. */
  function seriesMax(series) {
    var m = 0, i, j, d;
    for (i = 0; i < (series || []).length; i++) {
      d = (series[i] && series[i].data) || [];
      for (j = 0; j < d.length; j++) { var v = num(d[j]); if (v > m) m = v; }
    }
    return m;
  }

  /** true kalau seluruh angka di semua series bernilai 0 (atau tidak ada data). */
  function isEmptyData(series) {
    var i, j, d;
    for (i = 0; i < (series || []).length; i++) {
      d = (series[i] && series[i].data) || [];
      for (j = 0; j < d.length; j++) { if (num(d[j]) !== 0) return false; }
    }
    return true;
  }

  /** Posisi x titik ke-i dari n titik di dalam lebar w. */
  function xAt(i, n, w) {
    if (n <= 1) return w / 2;
    return (i * w) / (n - 1);
  }

  function sign(x) { return x < 0 ? -1 : 1; }

  /**
   * Kurva monotone kubik (setara d3.curveMonotoneX) untuk deret titik [x,y].
   *
   * Kenapa bukan Catmull-Rom / cardinal: kurva itu boleh melampaui titik data.
   * Pada grafik hitungan yang menyentuh nol, lengkungnya bisa menukik ke
   * bawah sumbu dan menampilkan lembah yang tidak pernah ada di data. Metode
   * Fritsch–Carlson membatasi tangen tiap simpul sehingga kurva mustahil
   * melewati nilai tetangganya — mulus tapi tetap jujur.
   */
  function monotoneD(pts) {
    var n = pts.length, i;
    if (n === 0) return '';
    if (n === 1) return 'M' + round(pts[0][0]) + ',' + round(pts[0][1]);
    if (n === 2) {
      return 'M' + round(pts[0][0]) + ',' + round(pts[0][1]) +
             ' L' + round(pts[1][0]) + ',' + round(pts[1][1]);
    }

    /* Kemiringan tiap ruas. */
    var d = new Array(n - 1);
    for (i = 0; i < n - 1; i++) {
      var dx = pts[i + 1][0] - pts[i][0];
      d[i] = (pts[i + 1][1] - pts[i][1]) / (dx || 1e-9);
    }

    /* Tangen simpul dalam, dibatasi supaya monoton. */
    var t = new Array(n);
    for (i = 1; i < n - 1; i++) {
      var s0 = d[i - 1], s1 = d[i];
      if (s0 * s1 <= 0) {
        t[i] = 0;                       /* titik balik: tangen datar */
      } else {
        var h0 = pts[i][0] - pts[i - 1][0];
        var h1 = pts[i + 1][0] - pts[i][0];
        var p = (s0 * h1 + s1 * h0) / (h0 + h1);
        t[i] = (sign(s0) + sign(s1)) *
               Math.min(Math.abs(s0), Math.abs(s1), 0.5 * Math.abs(p));
      }
    }

    /* Tangen ujung — rumus tiga titik satu sisi. */
    t[0]     = endTangent(pts[1][0] - pts[0][0], d[0], t[1]);
    t[n - 1] = endTangent(pts[n - 1][0] - pts[n - 2][0], d[n - 2], t[n - 2]);

    var out = 'M' + round(pts[0][0]) + ',' + round(pts[0][1]);
    for (i = 0; i < n - 1; i++) {
      var w = (pts[i + 1][0] - pts[i][0]) / 3;
      out += ' C' + round(pts[i][0] + w) + ',' + round(pts[i][1] + w * t[i]) +
             ' '  + round(pts[i + 1][0] - w) + ',' + round(pts[i + 1][1] - w * t[i + 1]) +
             ' '  + round(pts[i + 1][0]) + ',' + round(pts[i + 1][1]);
    }
    return out;
  }

  function endTangent(h, s, tNext) {
    if (!h) return tNext;
    var v = (3 * s - tNext) / 2;
    return isFinite(v) ? v : 0;
  }

  /** Titik-titik [x,y] untuk `data` di dalam kotak w x h. */
  function pointsFor(data, w, h, scaleMax) {
    var d = data || [], out = [], i;
    var top = scaleMax && scaleMax > 0 ? scaleMax : niceScale(seriesMax([{ data: d }])).max;
    for (i = 0; i < d.length; i++) {
      out.push([xAt(i, d.length, w), h - (num(d[i]) / top) * h]);
    }
    return out;
  }

  /**
   * Path garis monotone untuk `data` di dalam kotak w x h.
   * y = h untuk nilai 0, y = 0 untuk nilai maksimum skala.
   * Mengembalikan '' kalau tidak ada data.
   */
  function linePath(data, w, h, scaleMax) {
    if (!(data || []).length) return '';
    return monotoneD(pointsFor(data, w, h, scaleMax));
  }

  /** Path area (kurva + turun ke dasar) untuk gradasi di bawah garis. */
  function areaPath(data, w, h, scaleMax) {
    var line = linePath(data, w, h, scaleMax);
    if (!line) return '';
    var n = (data || []).length;
    var lastX = round(xAt(n - 1, n, w));
    var firstX = round(xAt(0, n, w));
    return line + ' L' + lastX + ',' + round(h) + ' L' + firstX + ',' + round(h) + ' Z';
  }

  /**
   * Path batang dengan HANYA dua sudut atas yang membulat.
   * rect + rx membulatkan keempat sudut sehingga batang tampak melayang,
   * tidak menempel ke garis dasar.
   */
  function barPath(x, y, w, h, r) {
    var rad = Math.min(r, w / 2, h);
    if (rad <= 0.5) {
      return 'M' + round(x) + ',' + round(y) + ' h' + round(w) +
             ' v' + round(h) + ' h' + round(-w) + ' Z';
    }
    return 'M' + round(x) + ',' + round(y + h) +
           ' L' + round(x) + ',' + round(y + rad) +
           ' A' + round(rad) + ',' + round(rad) + ' 0 0 1 ' + round(x + rad) + ',' + round(y) +
           ' L' + round(x + w - rad) + ',' + round(y) +
           ' A' + round(rad) + ',' + round(rad) + ' 0 0 1 ' + round(x + w) + ',' + round(y + rad) +
           ' L' + round(x + w) + ',' + round(y + h) + ' Z';
  }

  /**
   * Geometri donut dalam kotak 100x100 (cx=50, cy=50).
   * Mengembalikan array { value, pct, start, end, d, index }.
   * total 0 -> array kosong (pemanggil menampilkan empty state).
   *
   * Dipertahankan apa adanya untuk qa/selftest.html; renderer ring memakai
   * ringSegments() yang menggambar busur bergaris, bukan juring terisi.
   */
  function donutArcs(data, opts) {
    var o = opts || {};
    var r = o.r > 0 ? o.r : 42;
    var inner = o.inner > 0 ? o.inner : 26;
    var cx = o.cx === undefined ? 50 : o.cx;
    var cy = o.cy === undefined ? 50 : o.cy;

    var d = data || [];
    var total = 0, i;
    for (i = 0; i < d.length; i++) total += Math.max(0, num(d[i]));
    if (total <= 0) return [];

    var arcs = [];
    var angle = -Math.PI / 2;           // mulai dari jam 12
    for (i = 0; i < d.length; i++) {
      var v = Math.max(0, num(d[i]));
      if (v === 0) continue;
      var frac = v / total;
      var sweep = frac * Math.PI * 2;
      // Lingkaran penuh tidak bisa digambar satu arc; sisakan celah tak kasat mata.
      if (sweep >= Math.PI * 2) sweep = Math.PI * 2 - 0.0001;
      var start = angle;
      var end = angle + sweep;
      arcs.push({
        index: i,
        value: v,
        pct: Math.round(frac * 1000) / 10,
        start: start,
        end: end,
        d: arcPath(cx, cy, r, inner, start, end)
      });
      angle = end;
    }
    return arcs;
  }

  function arcPath(cx, cy, r, inner, start, end) {
    var large = (end - start) > Math.PI ? 1 : 0;
    var x0 = cx + r * Math.cos(start), y0 = cy + r * Math.sin(start);
    var x1 = cx + r * Math.cos(end),   y1 = cy + r * Math.sin(end);
    var x2 = cx + inner * Math.cos(end),   y2 = cy + inner * Math.sin(end);
    var x3 = cx + inner * Math.cos(start), y3 = cy + inner * Math.sin(start);
    return 'M' + round(x0) + ',' + round(y0) +
           ' A' + r + ',' + r + ' 0 ' + large + ' 1 ' + round(x1) + ',' + round(y1) +
           ' L' + round(x2) + ',' + round(y2) +
           ' A' + inner + ',' + inner + ' 0 ' + large + ' 0 ' + round(x3) + ',' + round(y3) +
           ' Z';
  }

  /**
   * Segmen ring bergaris (bukan juring terisi) dalam kotak 100x100.
   * Tiap segmen dipisah jeda RING_GAP_DEG derajat supaya ujung bulatnya tidak
   * saling menindih. Segmen yang lebih kecil dari jeda dilewati — kalau tidak,
   * busurnya berbalik arah dan menggambar lingkaran hampir penuh.
   */
  function ringSegments(data, radius) {
    var r = radius > 0 ? radius : 38;
    var d = data || [];
    var total = 0, i;
    for (i = 0; i < d.length; i++) total += Math.max(0, num(d[i]));
    if (total <= 0) return [];

    var gap = (RING_GAP_DEG * Math.PI) / 180;
    var only = countPositive(d) === 1;
    var out = [];
    var angle = -Math.PI / 2;                 /* mulai jam 12 */
    for (i = 0; i < d.length; i++) {
      var v = Math.max(0, num(d[i]));
      if (v === 0) continue;
      var frac = v / total;
      var sweep = frac * Math.PI * 2;
      var inset = only ? 0 : gap / 2;
      var start = angle + inset;
      var end = angle + sweep - inset;
      if (end > start) {
        out.push({
          index: i,
          value: v,
          pct: Math.round(frac * 1000) / 10,
          start: start,
          end: end,
          d: strokeArc(50, 50, r, start, end)
        });
      }
      angle += sweep;
    }
    return out;
  }

  function countPositive(d) {
    var c = 0;
    for (var i = 0; i < (d || []).length; i++) if (num(d[i]) > 0) c++;
    return c;
  }

  /** Busur terbuka (untuk digambar dengan stroke, bukan fill). */
  function strokeArc(cx, cy, r, start, end) {
    var sweep = end - start;
    /* Busur nyaris penuh tidak bisa satu perintah A; potong sedikit. */
    if (sweep >= Math.PI * 2) { end = start + Math.PI * 2 - 0.001; sweep = end - start; }
    var large = sweep > Math.PI ? 1 : 0;
    var x0 = cx + r * Math.cos(start), y0 = cy + r * Math.sin(start);
    var x1 = cx + r * Math.cos(end),   y1 = cy + r * Math.sin(end);
    return 'M' + round(x0) + ',' + round(y0) +
           ' A' + r + ',' + r + ' 0 ' + large + ' 1 ' + round(x1) + ',' + round(y1);
  }

  /**
   * Pilih indeks label sumbu-x supaya tidak tumpang tindih.
   * Selalu menyertakan indeks pertama dan terakhir.
   */
  function labelTicks(count, maxLabels) {
    var m = maxLabels && maxLabels > 1 ? maxLabels : 6;
    if (count <= 0) return [];
    if (count <= m) {
      var all = [];
      for (var i = 0; i < count; i++) all.push(i);
      return all;
    }
    var stepF = (count - 1) / (m - 1);
    var out = [], seen = {};
    for (var k = 0; k < m; k++) {
      var idx = Math.round(k * stepF);
      if (idx > count - 1) idx = count - 1;
      if (!seen[idx]) { seen[idx] = 1; out.push(idx); }
    }
    return out;
  }

  /* --------------------------------------------------------------- easing */

  /**
   * Penyelesai cubic-bezier(x1,y1,x2,y2) — kurva easing CSS, tapi dijalankan
   * sendiri karena animasi kita menggerakkan atribut geometri SVG yang tidak
   * bisa ditransisikan lewat CSS di semua mesin.
   */
  function cubicBezier(x1, y1, x2, y2) {
    function cx(t) { return ((1 - t) * (1 - t) * 3 * t * x1) + ((1 - t) * 3 * t * t * x2) + (t * t * t); }
    function cy(t) { return ((1 - t) * (1 - t) * 3 * t * y1) + ((1 - t) * 3 * t * t * y2) + (t * t * t); }
    function dx(t) {
      return 3 * (1 - t) * (1 - t) * x1 + 6 * (1 - t) * t * (x2 - x1) + 3 * t * t * (1 - x2);
    }
    return function (p) {
      if (p <= 0) return 0;
      if (p >= 1) return 1;
      var t = p, i, d;
      for (i = 0; i < 6; i++) {                 /* Newton–Raphson */
        var e = cx(t) - p;
        if (Math.abs(e) < 1e-5) return cy(t);
        d = dx(t);
        if (Math.abs(d) < 1e-6) break;
        t -= e / d;
      }
      var lo = 0, hi = 1;                        /* cadangan: bagi dua */
      t = p;
      for (i = 0; i < 20; i++) {
        var v = cx(t);
        if (Math.abs(v - p) < 1e-5) break;
        if (v < p) lo = t; else hi = t;
        t = (lo + hi) / 2;
      }
      return cy(t);
    };
  }

  /* Kurva reveal bklit: cubic-bezier(0.85, 0, 0.15, 1) — berangkat pelan,
   * menyapu cepat di tengah, mendarat pelan. */
  var easeReveal = cubicBezier(0.85, 0, 0.15, 1);

  function reducedMotion() {
    try {
      return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
    } catch (e) { return false; }
  }

  /**
   * Tunda `run()` sampai `el` benar-benar masuk layar.
   *
   * Tanpa ini seluruh chart di halaman menganimasi bersamaan saat data datang —
   * termasuk yang berada jauh di bawah lipatan. Animasinya sudah selesai
   * sebelum pengguna sempat menggulung ke sana, jadi biayanya dibayar tanpa
   * ada yang melihat hasilnya.
   *
   * Sekali jalan saja: observer diputus begitu terpicu, supaya menggulung
   * bolak-balik tidak membuat chart berkedip menganimasi ulang terus-menerus.
   *
   * Dua keadaan langsung dijalankan tanpa menunggu: mesin tanpa
   * IntersectionObserver, dan pengguna yang meminta gerak minimal (buat mereka
   * tween() toh langsung melompat ke keadaan akhir — menundanya hanya akan
   * membuat chart tampak kosong sampai digulung).
   */
  function whenVisible(el, run) {
    if (reducedMotion() || !global.IntersectionObserver || !el) { run(); return; }

    var fired = false;
    var timer = 0;
    function go() {
      if (fired) return;
      fired = true;
      if (timer) global.clearTimeout(timer);
      io.disconnect();
      run();
    }

    var io = new global.IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) { go(); return; }
      }
    }, {
      /* Menyusutkan tepi bawah viewport: animasi mulai saat chart sudah cukup
       * masuk, bukan tepat saat piksel pertamanya menyentuh layar. */
      rootMargin: '0px 0px -10% 0px',
      threshold: 0.12
    });
    io.observe(el);

    /*
     * Jaring pengaman — WAJIB, bukan kemewahan. Sebelum animasinya jalan,
     * chart berada di keadaan p=0: tirai reveal selebar nol, batang setinggi
     * nol, busur ring sepanjang nol. Artinya chart yang observernya tidak
     * pernah menyala bukan sekadar kehilangan animasi, melainkan tampil
     * KOSONG selamanya, seolah datanya tidak ada.
     *
     * Yang paling sering memicunya: dokumen yang dirender di tab tersembunyi —
     * di sana IntersectionObserver memang tidak pernah memanggil balik.
     */
    timer = global.setTimeout(go, 6000);
  }

  /**
   * Jalankan `step(p)` dengan p 0→1 selama `ms`, lalu `step(1)` sekali lagi.
   * Kalau pengguna meminta gerak minimal, langsung lompat ke keadaan akhir.
   */
  function tween(ms, ease, step) {
    if (reducedMotion() || !global.requestAnimationFrame) { step(1); return; }

    var t0 = null, done = false, guard = 0;

    function finish() {
      if (done) return;
      done = true;
      if (guard) global.clearTimeout(guard);
      step(1);
    }

    function frame(ts) {
      if (done) return;
      if (t0 === null) t0 = ts;
      var p = (ts - t0) / ms;
      if (p >= 1) { finish(); return; }
      step(ease(p));
      global.requestAnimationFrame(frame);
    }
    global.requestAnimationFrame(frame);

    /*
     * Penjaga terakhir. requestAnimationFrame TIDAK BERJALAN di dokumen yang
     * tersembunyi, sementara setTimeout tetap jalan (walau dikasari). Tanpa
     * ini, chart yang animasinya dimulai saat tab tidak tampak akan mandek di
     * p=0 — dan p=0 untuk chart ini berarti tirai selebar nol alias KOSONG,
     * bukan sekadar "belum bergerak".
     *
     * Kalaupun ikut memotong animasi yang sah karena tab sempat disembunyikan
     * di tengah jalan, yang terjadi hanya melompat ke keadaan akhir yang benar.
     */
    guard = global.setTimeout(finish, ms + 2000);
  }

  /* ========================================================= RENDERER ===== */

  function el(name, attrs) {
    var n = document.createElementNS(SVG_NS, name);
    if (attrs) for (var k in attrs) {
      if (Object.prototype.hasOwnProperty.call(attrs, k)) n.setAttribute(k, attrs[k]);
    }
    return n;
  }

  function div(cls) {
    var d = document.createElement('div');
    if (cls) d.className = cls;
    return d;
  }

  function cfgNum(key, fallback) {
    var c = global.VDConfig || {};
    return typeof c[key] === 'number' ? c[key] : fallback;
  }

  function chartHeight() {
    var bp = cfgNum('MOBILE_BREAKPOINT', 640);
    return (global.innerWidth || 1024) < bp
      ? cfgNum('CHART_HEIGHT_MOBILE', 200)
      : cfgNum('CHART_HEIGHT', 240);
  }

  /**
   * Warna efektif untuk seri ke-i.
   *
   * Nama warna dari server SENGAJA DIABAIKAN — lihat catatan WARNA di kepala
   * file. Satu-satunya yang masih dihormati adalah `color: 'palette'`, yang
   * berarti "warnai per-titik, bukan per-seri" (dipakai bar chart kategori).
   */
  function colorFor(series, i, pointIndex) {
    var perPoint = series && series.color === 'palette';
    if (perPoint && pointIndex !== undefined) return rampColor(pointIndex);
    return rampColor(i);
  }

  function emptyState(host, message) {
    var box = div('chart-empty');
    box.textContent = message;
    host.appendChild(box);
  }

  /**
   * Gambar `chart` ke dalam `host` (elemen kosong, position:relative).
   * `host` dikosongkan lebih dulu.
   */
  function render(chart, host, opts) {
    opts = opts || {};
    while (host.firstChild) host.removeChild(host.firstChild);
    if (!chart) return;

    var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
    var series = chart.series || [];

    if (chart.empty === true || !series.length || isEmptyData(series)) {
      emptyState(host, opts.emptyText || txt.emptyChart || 'Belum ada data.');
      return;
    }

    var type = String(chart.type || 'line').toLowerCase();
    if (type === 'doughnut' || type === 'donut' || type === 'ring') return renderRing(chart, host);
    if (type === 'bar') return renderCartesian(chart, host, 'bar');
    return renderCartesian(chart, host, 'line');
  }

  /* ---------------------------------------------------------- line & bar */

  function renderCartesian(chart, host, kind) {
    var W = Math.max(240, Math.round(host.clientWidth || host.offsetWidth || 320));
    var H = chartHeight();
    var uid = 'vdc' + (++uidSeq);

    var series = chart.series || [];
    var labels = chart.labels || [];
    var n = labels.length || (series[0] && series[0].data ? series[0].data.length : 0);

    /* Skala sumbu-y pakai GRID_ROWS langkah, mengikuti Grid numTicksRows=5. */
    var scale = niceScale(seriesMax(series), GRID_ROWS - 1);

    /* Margin lebih lapang dari versi lama (bklit memakai 40 di keempat sisi).
     * padB dibesarkan karena date pill hidup di bawah sumbu-x. */
    var padL = 44, padR = 14, padT = 16, padB = 30;
    var plotW = W - padL - padR;
    var plotH = H - padT - padB;

    var svg = el('svg', {
      viewBox: '0 0 ' + W + ' ' + H,
      preserveAspectRatio: 'xMidYMid meet',
      width: '100%',
      height: String(H),
      role: 'img',
      'aria-label': chart.title || ''
    });
    svg.classList.add('chart-svg');

    var defs = el('defs');
    svg.appendChild(defs);

    /* Gradasi crosshair: pekat di tengah, hilang di kedua ujung.
     *
     * Dua hal yang mudah salah di sini:
     *  - gradientUnits WAJIB userSpaceOnUse. Kotak pembatas sebuah garis
     *    vertikal lebarnya nol, jadi gradasi objectBoundingBox (bawaan)
     *    menjadi degenerate dan garisnya hilang sama sekali.
     *  - warna stop dibaca sekarang dari custom property, bukan currentColor.
     *    currentColor pada <stop> mewarisi dari <stop> itu sendiri, bukan dari
     *    elemen yang memakai gradasinya — hasilnya hitam di kedua tema.
     *    app.js sudah menggambar ulang chart tiap kali tema berganti, jadi
     *    membaca nilai sekali di sini aman. */
    var crossCol = cssVar('--chart-crosshair', 'rgba(255,255,255,.34)');
    var cg = el('linearGradient', {
      id: uid + '-cross', gradientUnits: 'userSpaceOnUse',
      x1: 0, y1: 0, x2: 0, y2: plotH
    });
    cg.appendChild(el('stop', { offset: '0%', 'stop-color': crossCol, 'stop-opacity': '0' }));
    cg.appendChild(el('stop', { offset: CROSS_FADE_PCT + '%', 'stop-color': crossCol, 'stop-opacity': '1' }));
    cg.appendChild(el('stop', { offset: (100 - CROSS_FADE_PCT) + '%', 'stop-color': crossCol, 'stop-opacity': '1' }));
    cg.appendChild(el('stop', { offset: '100%', 'stop-color': crossCol, 'stop-opacity': '0' }));
    defs.appendChild(cg);

    /* Tirai reveal — lebarnya dianimasikan dari 0 ke plotW. */
    var clip = el('clipPath', { id: uid + '-reveal' });
    var clipRect = el('rect', { x: -2, y: -10, width: 0, height: plotH + 20 });
    clip.appendChild(clipRect);
    defs.appendChild(clip);

    var g = el('g', { transform: 'translate(' + padL + ',' + padT + ')' });

    /* --- gridline horizontal (putus-putus) + label sumbu y --- */
    var ti;
    for (ti = 0; ti < scale.ticks.length; ti++) {
      var val = scale.ticks[ti];
      var y = plotH - (val / scale.max) * plotH;
      g.appendChild(el('line', {
        x1: 0, y1: round(y), x2: plotW, y2: round(y),
        class: 'chart-grid' + (val === 0 ? ' chart-grid-base' : ''),
        'stroke-dasharray': val === 0 ? 'none' : GRID_DASH
      }));
      var yl = el('text', { x: -10, y: round(y) + 4, class: 'chart-axis', 'text-anchor': 'end' });
      yl.textContent = fmtTick(val);
      g.appendChild(yl);
    }

    /* --- data (di dalam tirai reveal) --- */
    var plot = el('g', { 'clip-path': 'url(#' + uid + '-reveal)' });
    var i, s, si;
    var barRects = [];

    if (kind === 'bar') {
      var groups = series.length;
      var slot = n > 0 ? plotW / n : plotW;
      /* barGap 0.2 = seperlima slot dibiarkan kosong di kiri-kanan kelompok. */
      var groupW = slot * (1 - 0.2);
      var barW = Math.max(2, groupW / Math.max(1, groups));
      for (si = 0; si < groups; si++) {
        s = series[si];
        var data = s.data || [];
        for (i = 0; i < data.length; i++) {
          var v = num(data[i]);
          var bh = (v / scale.max) * plotH;
          if (v > 0 && bh < 2) bh = 2;         /* nilai kecil tetap terlihat */
          var cx0 = slot * i + slot / 2;
          var bx = cx0 - groupW / 2 + barW * si;
          var path = el('path', {
            d: barPath(bx, plotH - bh, barW, bh, Math.min(4, barW / 2)),
            fill: colorFor(s, si, s.color === 'palette' ? i : undefined),
            class: 'chart-bar'
          });
          plot.appendChild(path);
          barRects.push({ node: path, x: bx, w: barW, h: bh });
        }
      }
    } else {
      for (si = 0; si < series.length; si++) {
        s = series[si];
        var col = colorFor(s, si);
        var pts = pointsFor(s.data || [], plotW, plotH, scale.max);

        /* Gradasi isian: AREA_OPACITY di puncak, lenyap di garis dasar. */
        var gid = uid + '-fill' + si;
        var lg = el('linearGradient', {
          id: gid, gradientUnits: 'userSpaceOnUse', x1: 0, y1: 0, x2: 0, y2: plotH
        });
        lg.appendChild(el('stop', { offset: '0%', 'stop-color': col, 'stop-opacity': String(AREA_OPACITY) }));
        lg.appendChild(el('stop', { offset: '100%', 'stop-color': col, 'stop-opacity': '0' }));
        defs.appendChild(lg);

        var ap = areaPath(s.data || [], plotW, plotH, scale.max);
        if (ap) plot.appendChild(el('path', { d: ap, fill: 'url(#' + gid + ')', stroke: 'none' }));

        var lp = linePath(s.data || [], plotW, plotH, scale.max);
        if (lp) {
          plot.appendChild(el('path', {
            d: lp, fill: 'none', stroke: col, 'stroke-width': String(STROKE_W),
            'stroke-linejoin': 'round', 'stroke-linecap': 'round'
          }));
        }

        /* Penanda titik hanya kalau datanya jarang — di 30 titik, lingkaran
         * di tiap simpul menutupi garisnya sendiri. */
        if (pts.length <= MARKER_MAX_PTS) {
          for (i = 0; i < pts.length; i++) {
            plot.appendChild(el('circle', {
              cx: round(pts[i][0]), cy: round(pts[i][1]), r: 3,
              fill: cssVar('--chart-marker-halo', '#0b0f19'),
              stroke: col, 'stroke-width': '2', class: 'chart-marker'
            }));
          }
        }
      }
    }
    g.appendChild(plot);

    /* --- label sumbu x --- */
    var axisLabels = [];
    var ticks = labelTicks(n, W < 420 ? 4 : 7);
    for (i = 0; i < ticks.length; i++) {
      var idx = ticks[i];
      var lx = kind === 'bar'
        ? (n > 0 ? (plotW / n) * idx + (plotW / n) / 2 : plotW / 2)
        : xAt(idx, n, plotW);
      var anchor = 'middle';
      if (idx === 0 && lx < 16) anchor = 'start';
      if (idx === n - 1 && lx > plotW - 16) anchor = 'end';
      var t = el('text', {
        x: round(lx), y: plotH + 20, class: 'chart-axis', 'text-anchor': anchor
      });
      t.textContent = shortLabel(labels[idx]);
      g.appendChild(t);
      axisLabels.push({ node: t, x: lx });
    }

    /* --- lapisan interaksi --- */
    var guide = el('line', {
      x1: 0, y1: 0, x2: 0, y2: plotH,
      class: 'chart-guide', stroke: 'url(#' + uid + '-cross)', opacity: '0'
    });
    g.appendChild(guide);
    var dots = el('g', { class: 'chart-dots' });
    g.appendChild(dots);

    svg.appendChild(g);
    host.appendChild(svg);

    var tip = div('chart-tip');
    tip.setAttribute('aria-hidden', 'true');
    host.appendChild(tip);

    /* Date pill: menggantikan label sumbu yang dipudarkan crosshair. */
    var pill = div('chart-datepill');
    pill.setAttribute('aria-hidden', 'true');
    host.appendChild(pill);

    if (series.length > 1) host.appendChild(legendFor(series));

    /* --- animasi masuk ---
     * Keadaan awal dipasang SEKARANG (p = 0) supaya chart yang masih di bawah
     * lipatan tidak sempat terlihat utuh lalu tiba-tiba mengulang dari nol.
     * Gerakannya sendiri baru mulai saat kartunya masuk layar. */
    var step;
    if (kind === 'bar') {
      clipRect.setAttribute('width', plotW + 4);        /* bar tumbuh sendiri */
      step = function (p) {
        for (var b = 0; b < barRects.length; b++) {
          var it = barRects[b];
          /* Setiap batang berangkat sedikit lebih lambat dari batang di
           * kirinya — "stagger" bklit, tapi diturunkan dari satu kemajuan
           * global supaya hanya ada SATU rAF untuk seluruh chart. */
          var lag = barRects.length > 1 ? (b / barRects.length) * 0.35 : 0;
          var q = Math.max(0, Math.min(1, (p - lag) / (1 - lag || 1)));
          var hh = it.h * q;
          it.node.setAttribute('d', barPath(it.x, plotH - hh, it.w, hh, Math.min(4, it.w / 2)));
        }
      };
    } else {
      step = function (p) { clipRect.setAttribute('width', round(plotW * p + 2)); };
    }
    step(0);
    whenVisible(host, function () { tween(REVEAL_MS, easeReveal, step); });

    attachCartesianTip(host, svg, tip, pill, guide, dots, {
      chart: chart, kind: kind, n: n, padL: padL, padT: padT,
      plotW: plotW, plotH: plotH, plotTop: padT, scaleMax: scale.max,
      W: W, H: H,
      axisLabels: axisLabels
    });
  }

  function fmtTick(v) {
    if (v >= 1000000) return (Math.round(v / 100000) / 10) + 'jt';
    if (v >= 1000) return (Math.round(v / 100) / 10) + 'rb';
    return String(v);
  }

  /** "2026-07-21" -> "21/07". Label lain dipakai apa adanya (dipotong). */
  function shortLabel(v) {
    var s = v === undefined || v === null ? '' : String(v);
    var m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (m) return m[3] + '/' + m[2];
    return s.length > 8 ? s.slice(0, 8) + '…' : s;
  }

  function legendFor(series) {
    var box = div('chart-legend');
    for (var i = 0; i < series.length; i++) {
      var item = div('chart-legend-item');
      var sw = div('chart-swatch');
      sw.style.background = colorFor(series[i], i);
      var lab = document.createElement('span');
      lab.textContent = series[i].name || ('Seri ' + (i + 1));
      item.appendChild(sw);
      item.appendChild(lab);
      box.appendChild(item);
    }
    return box;
  }

  /**
   * Faktor skala dan pergeseran dari satuan viewBox ke piksel layar.
   *
   * Tidak bisa disederhanakan jadi `box.width / W`. Dengan
   * preserveAspectRatio="xMidYMid meet", gambar diskalakan dengan faktor
   * TERKECIL dari kedua sumbu lalu DITENGAHKAN — jadi kalau elemennya lebih
   * lebar dari rasio viewBox, isinya tidak melar, ia hanya bergeser ke tengah
   * dan menyisakan pias di kiri-kanan. Memakai box.width/W di kondisi itu
   * membuat crosshair salah menunjuk hari dan date pill melayang di bawah
   * kartu. Selisihnya baru muncul kalau lebar host berubah setelah chart
   * digambar (mis. scrollbar hilang), yang persis terjadi di halaman
   * qa/preview-charts.html.
   */
  function viewportOf(svg, ctx) {
    var box = svg.getBoundingClientRect();
    var k = Math.min(box.width / ctx.W, box.height / ctx.H);
    if (!isFinite(k) || k <= 0) k = 1;
    return {
      box: box,
      k: k,
      ox: (box.width - ctx.W * k) / 2,
      oy: (box.height - ctx.H * k) / 2
    };
  }

  function attachCartesianTip(host, svg, tip, pill, guide, dots, ctx) {
    var series = ctx.chart.series || [];
    var labels = ctx.chart.labels || [];
    var active = -1;

    function indexFromClientX(clientX) {
      var vp = viewportOf(svg, ctx);
      if (!vp.box.width || ctx.n <= 0) return -1;
      var x = (clientX - vp.box.left - vp.ox) / vp.k - ctx.padL;
      if (x < -8 || x > ctx.plotW + 8) return -1;
      if (ctx.kind === 'bar') {
        var slot = ctx.plotW / ctx.n;
        var i = Math.floor(x / slot);
        return i < 0 ? 0 : i > ctx.n - 1 ? ctx.n - 1 : i;
      }
      var stepW = ctx.n > 1 ? ctx.plotW / (ctx.n - 1) : ctx.plotW;
      var j = Math.round(x / stepW);
      return j < 0 ? 0 : j > ctx.n - 1 ? ctx.n - 1 : j;
    }

    /**
     * Label sumbu yang berada dalam radius TICKER_HALF dari crosshair
     * dipudarkan. Tanpa ini, date pill dan label sumbu menumpuk persis di
     * titik yang sama dan keduanya jadi tidak terbaca.
     */
    function fadeAxis(gx) {
      for (var i = 0; i < ctx.axisLabels.length; i++) {
        var it = ctx.axisLabels[i];
        if (gx === null) { it.node.style.opacity = ''; continue; }
        var dist = Math.abs(it.x - gx);
        it.node.style.opacity = dist >= TICKER_HALF ? '1'
          : String(Math.max(0, dist / TICKER_HALF));
      }
    }

    function show(i, clientX) {
      if (i < 0) return hide();
      active = i;

      var gx = ctx.kind === 'bar'
        ? (ctx.plotW / ctx.n) * i + (ctx.plotW / ctx.n) / 2
        : xAt(i, ctx.n, ctx.plotW);

      guide.setAttribute('x1', round(gx));
      guide.setAttribute('x2', round(gx));
      guide.setAttribute('opacity', '1');
      fadeAxis(gx);

      while (dots.firstChild) dots.removeChild(dots.firstChild);
      while (tip.firstChild) tip.removeChild(tip.firstChild);

      var head = div('chart-tip-head');
      head.textContent = labels[i] !== undefined ? String(labels[i]) : '';
      tip.appendChild(head);

      for (var si = 0; si < series.length; si++) {
        var s = series[si];
        var v = num((s.data || [])[i]);
        var col = colorFor(s, si, s.color === 'palette' ? i : undefined);

        if (ctx.kind !== 'bar') {
          var dy = ctx.plotH - (v / ctx.scaleMax) * ctx.plotH;
          // Lingkaran halo mengambil warna permukaan tema aktif; kalau dipatok
          // gelap, di mode terang titiknya terlihat berlubang hitam.
          dots.appendChild(el('circle', {
            cx: round(gx), cy: round(dy), r: 4.5, fill: col,
            stroke: cssVar('--dot-halo', 'rgba(11,15,25,0.9)'), 'stroke-width': '2.5'
          }));
        }

        var row = div('chart-tip-row');
        var sw = div('chart-swatch');
        sw.style.background = col;
        var nm = document.createElement('span');
        nm.className = 'chart-tip-name';
        nm.textContent = s.name || '';
        var val = document.createElement('strong');
        val.textContent = String(v);
        row.appendChild(sw); row.appendChild(nm); row.appendChild(val);
        tip.appendChild(row);
      }

      tip.classList.add('show');
      positionTip(host, tip, clientX);

      pill.textContent = labels[i] !== undefined ? shortLabel(labels[i]) : '';
      pill.classList.add('show');
      positionPill(host, svg, pill, gx, ctx);
    }

    function hide() {
      active = -1;
      guide.setAttribute('opacity', '0');
      fadeAxis(null);
      while (dots.firstChild) dots.removeChild(dots.firstChild);
      tip.classList.remove('show');
      pill.classList.remove('show');
    }

    function onMove(ev) {
      var cx = ev.clientX !== undefined ? ev.clientX
             : (ev.touches && ev.touches[0] ? ev.touches[0].clientX : 0);
      var i = indexFromClientX(cx);
      if (i !== active || tip.classList.contains('show') === false) show(i, cx);
      else positionTip(host, tip, cx);
    }

    svg.addEventListener('pointermove', onMove);
    svg.addEventListener('pointerdown', onMove);
    svg.addEventListener('pointerleave', hide);
    svg.addEventListener('pointercancel', hide);
  }

  function positionTip(host, tip, clientX) {
    var hb = host.getBoundingClientRect();
    var w = tip.offsetWidth || 120;
    var x = clientX - hb.left - w / 2;
    if (x < 4) x = 4;
    if (x > hb.width - w - 4) x = Math.max(4, hb.width - w - 4);
    tip.style.left = Math.round(x) + 'px';
  }

  /**
   * Date pill duduk tepat di bawah garis dasar plot, sejajar crosshair.
   * Koordinat viewBox diterjemahkan ke piksel host lewat viewportOf(), karena
   * pill adalah elemen HTML biasa yang hidup di luar sistem koordinat SVG.
   */
  function positionPill(host, svg, pill, gx, ctx) {
    var vp = viewportOf(svg, ctx);
    var hb = host.getBoundingClientRect();
    var w = pill.offsetWidth || 44;
    var x = (vp.box.left - hb.left) + vp.ox + (ctx.padL + gx) * vp.k - w / 2;
    if (x < 0) x = 0;
    if (x > hb.width - w) x = Math.max(0, hb.width - w);
    pill.style.left = Math.round(x) + 'px';
    pill.style.top = Math.round(
      (vp.box.top - hb.top) + vp.oy + (ctx.plotTop + ctx.plotH + 8) * vp.k
    ) + 'px';
  }

  /* ----------------------------------------------------------------- ring */

  /**
   * Ring chart (dulu doughnut). Bedanya dengan versi lama: segmennya digambar
   * sebagai GARIS BUSUR berujung bulat dengan jeda antarsegmen, bukan juring
   * terisi yang saling menempel. Lebih ringan dan sesuai gaya bklit.
   *
   * Urutan warna mengikuti BESAR NILAI, bukan urutan data: segmen terbesar
   * mendapat --chart-1 (warna merek), sisanya makin redup. Jadi mata langsung
   * jatuh ke kategori dominan tanpa perlu membaca legenda.
   */
  function renderRing(chart, host) {
    var series = (chart.series || [])[0] || { data: [] };
    var labels = chart.labels || [];
    var data = series.data || [];

    var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
    var radius = 50 - RING_STROKE / 2 - 1;
    var segs = ringSegments(data, radius);
    if (!segs.length) return emptyState(host, txt.emptyChart || 'Belum ada data.');

    /* Peringkat nilai -> langkah ramp. */
    var order = segs.slice().sort(function (a, b) { return b.value - a.value; });
    var rankOf = {};
    for (var q = 0; q < order.length; q++) rankOf[order[q].index] = q;

    var wrap = div('donut-wrap');
    var size = Math.min(200, Math.max(140, chartHeight() - 20));
    var svg = el('svg', {
      viewBox: '0 0 100 100',
      preserveAspectRatio: 'xMidYMid meet',
      width: String(size), height: String(size),
      role: 'img', 'aria-label': chart.title || ''
    });
    svg.classList.add('chart-svg', 'donut-svg');

    /* Rel latar — memberi tahu bahwa lingkarannya utuh 100%, dan menahan
     * bentuk ring saat animasi masih di awal. */
    svg.appendChild(el('circle', {
      cx: 50, cy: 50, r: radius, fill: 'none',
      'stroke-width': String(RING_STROKE), class: 'ring-track'
    }));

    var total = 0, i;
    for (i = 0; i < data.length; i++) total += Math.max(0, num(data[i]));

    var tip = div('chart-tip');
    var center = div('donut-center');
    var cNum = div('donut-center-num');
    cNum.textContent = String(Math.round(total));
    var cLab = div('donut-center-lab');
    cLab.textContent = series.name || 'Total';
    center.appendChild(cNum); center.appendChild(cLab);

    var legend = div('donut-legend');
    var arcNodes = [];

    function highlight(idx) {
      for (var p = 0; p < arcNodes.length; p++) {
        arcNodes[p].node.style.opacity =
          (idx === null || arcNodes[p].index === idx) ? '1' : '0.28';
      }
      if (idx === null) {
        cNum.textContent = String(Math.round(total));
        cLab.textContent = series.name || 'Total';
      }
    }

    for (i = 0; i < segs.length; i++) {
      (function (a) {
        var col = rampColor(rankOf[a.index]);
        var p = el('path', {
          d: a.d, fill: 'none', stroke: col,
          'stroke-width': String(RING_STROKE), 'stroke-linecap': 'round',
          'data-i': String(a.index), class: 'donut-arc'
        });
        p.addEventListener('pointerenter', function () {
          highlight(a.index);
          cNum.textContent = String(a.value);
          cLab.textContent = labels[a.index] !== undefined ? String(labels[a.index]) : '';
          while (tip.firstChild) tip.removeChild(tip.firstChild);
          var head = div('chart-tip-head');
          head.textContent = labels[a.index] !== undefined ? String(labels[a.index]) : '';
          var row = div('chart-tip-row');
          var sw = div('chart-swatch'); sw.style.background = col;
          var val = document.createElement('strong');
          val.textContent = a.value + ' · ' + a.pct + '%';
          row.appendChild(sw); row.appendChild(val);
          tip.appendChild(head); tip.appendChild(row);
          tip.classList.add('show');
          tip.style.left = '50%';
          tip.style.transform = 'translateX(-50%)';
        });
        p.addEventListener('pointerleave', function () {
          highlight(null);
          tip.classList.remove('show');
        });
        svg.appendChild(p);
        arcNodes.push({ node: p, index: a.index, start: a.start, end: a.end });

        var item = document.createElement('button');
        item.type = 'button';
        item.className = 'donut-legend-item';
        var sw2 = div('chart-swatch'); sw2.style.background = col;
        var nm = document.createElement('span');
        nm.className = 'donut-legend-label';
        nm.textContent = labels[a.index] !== undefined ? String(labels[a.index]) : '—';
        var vl = document.createElement('span');
        vl.className = 'donut-legend-val';
        vl.textContent = a.value + ' (' + a.pct + '%)';
        item.appendChild(sw2); item.appendChild(nm); item.appendChild(vl);
        item.addEventListener('pointerenter', function () { highlight(a.index); });
        item.addEventListener('pointerleave', function () { highlight(null); });
        item.addEventListener('click', function () { highlight(a.index); });
        legend.appendChild(item);
      }(segs[i]));
    }

    /* Busur tumbuh searah jarum jam dari jam 12. Sama seperti chart kartesian:
     * keadaan nol dipasang segera, gerakannya menunggu ring masuk layar. */
    function step(prog) {
      for (var k = 0; k < arcNodes.length; k++) {
        var a = arcNodes[k];
        var end = a.start + (a.end - a.start) * prog;
        a.node.setAttribute('d', strokeArc(50, 50, radius, a.start,
          end > a.start ? end : a.start + 0.0001));
      }
    }
    step(0);

    var ring = div('donut-ring');
    ring.appendChild(svg);
    ring.appendChild(center);
    ring.appendChild(tip);

    wrap.appendChild(ring);
    wrap.appendChild(legend);
    host.appendChild(wrap);

    whenVisible(host, function () { tween(REVEAL_MS, easeReveal, step); });
  }

  /* ============================================================= EKSPOR === */

  return {
    /* murni */
    niceScale: niceScale,
    linePath: linePath,
    areaPath: areaPath,
    monotoneD: monotoneD,
    barPath: barPath,
    donutArcs: donutArcs,
    ringSegments: ringSegments,
    labelTicks: labelTicks,
    seriesMax: seriesMax,
    isEmptyData: isEmptyData,
    xAt: xAt,
    toneHex: toneHex,
    rampColor: rampColor,
    paletteHex: paletteHex,
    cubicBezier: cubicBezier,
    whenVisible: whenVisible,
    currentTheme: currentTheme,
    PALETTE: PALETTE,
    TONE_HEX: TONE_HEX,
    TONE_HEX_LIGHT: TONE_HEX_LIGHT,
    /* render */
    render: render
  };

})(typeof window !== 'undefined' ? window : this);

if (typeof window !== 'undefined') window.VDCharts = VDCharts;
if (typeof module !== 'undefined' && module.exports) module.exports = VDCharts;
