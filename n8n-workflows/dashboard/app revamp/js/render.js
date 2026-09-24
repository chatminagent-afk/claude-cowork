/* ============================================================================
 * render.js — RENDERER GENERIK
 *
 * Tidak ada satu pun nama tenant, nama kolom, atau judul di file ini. Semua
 * label datang dari respons server. Kalau sebuah fitur butuh nama tenant untuk
 * bekerja, fitur itu salah desain.
 *
 * Satu-satunya penyebutan tenant di seluruh frontend ada di
 * `VDConfig.TENANT_LOGOS`, dan itu murni soal berkas gambar avatar: tenant
 * yang tidak terdaftar di sana tetap tampil normal dengan emblem huruf awal.
 *
 * Bagian 1: fungsi murni (tanpa DOM) — bisa diuji langsung.
 * Bagian 2: pembangun elemen.
 *
 * Nilai dari server SELALU masuk lewat textContent atau createElement.
 * Tidak ada innerHTML di file ini: nama lead dan isi pertanyaan berasal dari
 * pesan WhatsApp yang tidak terkontrol.
 * ========================================================================== */
'use strict';

var VDRender = (function (global) {

  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];

  /* ====================================================== FUNGSI MURNI ==== */

  function str(v) {
    return v === null || v === undefined ? '' : String(v);
  }

  function digits(v) { return str(v).replace(/\D/g, ''); }

  /** 12345 -> "12.345". Bukan angka -> "0". */
  function fmtInt(n) {
    var v = typeof n === 'number' ? n : parseFloat(str(n).replace(/[^0-9.\-]/g, ''));
    if (!isFinite(v)) return '0';
    var neg = v < 0;
    var s = String(Math.abs(Math.round(v)));
    s = s.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (neg ? '-' : '') + s;
  }

  /** "2026-07-21" -> "21 Jul 2026". Kosong / tidak terbaca -> "—". */
  function fmtDate(s) {
    var v = str(s).trim();
    if (v === '') return '—';
    var m = v.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (m) {
      var mo = parseInt(m[2], 10) - 1;
      if (mo < 0 || mo > 11) return v;
      return String(parseInt(m[3], 10)) + ' ' + MONTHS[mo] + ' ' + m[1];
    }
    var d = v.match(/^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})$/);
    if (d) {
      var mo2 = parseInt(d[2], 10) - 1;
      if (mo2 < 0 || mo2 > 11) return v;
      return String(parseInt(d[1], 10)) + ' ' + MONTHS[mo2] + ' ' + d[3];
    }
    return v;
  }

  /** epoch ms -> "21 Jul 2026, 14:32" (waktu lokal perangkat). */
  function fmtDateTime(ms) {
    var n = typeof ms === 'number' ? ms : parseInt(str(ms), 10);
    if (!isFinite(n) || n <= 0) return '—';
    var d = new Date(n);
    if (isNaN(d.getTime())) return '—';
    var hh = d.getHours(), mm = d.getMinutes();
    return d.getDate() + ' ' + MONTHS[d.getMonth()] + ' ' + d.getFullYear() +
           ', ' + (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
  }

  /**
   * Nilai KPI untuk rentang aktif.
   * KPI rangeAware memakai values[rentang]; sisanya memakai `value`.
   */
  function kpiValue(kpi, range) {
    if (!kpi) return 0;
    if (kpi.rangeAware && kpi.values) {
      var v = kpi.values[String(range)];
      if (v !== undefined && v !== null) return v;
    }
    return kpi.value === undefined || kpi.value === null ? 0 : kpi.value;
  }

  /**
   * Potong chart rangeAware ke N titik terakhir. Selalu mengembalikan objek
   * baru; `chart` asli tidak pernah diubah (payload dipakai ulang saat rentang
   * diganti, jadi mutasi akan merusak rentang berikutnya).
   */
  function sliceChart(chart, range) {
    if (!chart) return chart;
    var out = {}, k;
    for (k in chart) {
      if (Object.prototype.hasOwnProperty.call(chart, k)) out[k] = chart[k];
    }
    if (!chart.rangeAware) {
      out.series = (chart.series || []).slice();
      out.labels = (chart.labels || []).slice();
      return out;
    }
    var n = parseInt(range, 10);
    if (!isFinite(n) || n <= 0) n = (chart.labels || []).length;

    out.labels = (chart.labels || []).slice(-n);
    out.series = (chart.series || []).map(function (s) {
      var c = {}, kk;
      for (kk in s) { if (Object.prototype.hasOwnProperty.call(s, kk)) c[kk] = s[kk]; }
      c.data = (s.data || []).slice(-n);
      return c;
    });
    return out;
  }

  /**
   * Saring baris lead.
   *   q       — cocok ke nama, nomor, lid, atau key. Angka dibandingkan
   *             sebagai digit saja supaya "0812" tetap menemukan "62812…".
   *   botMode — 'all' | 'on' | 'off'
   */
  function filterLeads(rows, opts) {
    var list = rows || [];
    var o = opts || {};
    var mode = String(o.botMode || 'all').toLowerCase();
    var q = str(o.q).trim().toLowerCase();
    var qd = digits(q);

    var out = [];
    for (var i = 0; i < list.length; i++) {
      var r = list[i];
      if (!r) continue;

      if (mode === 'on' && !isBotOn(r)) continue;
      if (mode === 'off' && isBotOn(r)) continue;

      if (q !== '') {
        var hay = (str(r.nama) + ' ' + str(r.wa) + ' ' + str(r.lid) + ' ' + str(r.key)).toLowerCase();
        var hit = hay.indexOf(q) !== -1;
        if (!hit && qd !== '') {
          var nums = digits(r.wa) + ' ' + digits(r.lid) + ' ' + digits(r.key);
          hit = nums.indexOf(qd) !== -1;
          // Nomor tersimpan dalam bentuk internasional ("62812…") sementara
          // orang mengetiknya dengan nol di depan ("0812…"). Tanpa langkah
          // ini, mengetik nomor persis seperti yang dikenal penggunanya justru
          // tidak menemukan apa pun. Nol di depan dibuang, bukan diganti kode
          // negara, supaya tidak ada asumsi negara tertentu di file ini.
          if (!hit) {
            var qs = qd.replace(/^0+/, '');
            if (qs !== '' && qs !== qd) hit = nums.indexOf(qs) !== -1;
          }
        }
        if (!hit) continue;
      }
      out.push(r);
    }
    return out;
  }

  /**
   * Urut baris. Stabil (indeks asli jadi pemutus seri).
   * Angka diurut sebagai angka, tanggal "YYYY-MM-DD" sudah benar secara leksikal,
   * sisanya perbandingan string. Nilai kosong selalu di bawah.
   */
  function sortLeads(rows, key, dir) {
    var list = (rows || []).slice();
    if (!key) return list;
    var sign = String(dir).toLowerCase() === 'asc' ? 1 : -1;

    var decorated = list.map(function (r, i) { return { r: r, i: i }; });

    decorated.sort(function (a, b) {
      var av = a.r ? a.r[key] : undefined;
      var bv = b.r ? b.r[key] : undefined;
      var ae = av === undefined || av === null || av === '';
      var be = bv === undefined || bv === null || bv === '';
      if (ae && be) return a.i - b.i;
      if (ae) return 1;
      if (be) return -1;

      var an = typeof av === 'number' ? av : parseFloat(str(av).replace(',', '.'));
      var bn = typeof bv === 'number' ? bv : parseFloat(str(bv).replace(',', '.'));
      var bothNum = isFinite(an) && isFinite(bn) &&
                    /^-?[\d.,\s]+$/.test(str(av)) && /^-?[\d.,\s]+$/.test(str(bv));
      var cmp;
      if (bothNum) cmp = an - bn;
      else {
        var as = str(av).toLowerCase(), bs = str(bv).toLowerCase();
        cmp = as < bs ? -1 : as > bs ? 1 : 0;
      }
      if (cmp === 0) return a.i - b.i;
      return cmp * sign;
    });

    return decorated.map(function (d) { return d.r; });
  }

  /**
   * Potong per halaman. Halaman dijepit ke rentang sah supaya penghapusan
   * filter tidak pernah menghasilkan halaman kosong.
   */
  function paginate(rows, page, size) {
    var list = rows || [];
    var sz = parseInt(size, 10);
    if (!isFinite(sz) || sz <= 0) sz = 50;
    var total = list.length;
    var pages = Math.max(1, Math.ceil(total / sz));
    var p = parseInt(page, 10);
    if (!isFinite(p) || p < 1) p = 1;
    if (p > pages) p = pages;
    var start = (p - 1) * sz;
    var end = Math.min(total, start + sz);
    return {
      rows: list.slice(start, end),
      page: p, pages: pages, size: sz, total: total,
      start: total === 0 ? 0 : start + 1,
      end: end
    };
  }

  /** Warna badge yang stabil untuk sebuah teks (tanpa daftar nilai hardcoded). */
  function badgeTone(value) {
    var s = str(value);
    if (s === '') return 'gray';
    var h = 0;
    for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    var pal = (global.VDCharts && global.VDCharts.PALETTE) ||
              ['blue', 'teal', 'purple', 'orange', 'green', 'red'];
    return pal[h % pal.length];
  }

  /* ======================================================== DOM HELPERS === */

  function elem(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = String(text);
    return n;
  }

  function clear(node) {
    while (node && node.firstChild) node.removeChild(node.firstChild);
  }

  /* ------------------------------------------------------ reveal saat gulung */

  /*
   * Kartu muncul saat digulung ke dalam layar, bukan semuanya sekaligus saat
   * data datang. Dua alasan:
   *   - Dashboard ini lebih tinggi dari satu layar. Menganimasikan segalanya
   *     di awal berarti animasi untuk kartu di bawah lipatan sudah selesai
   *     sebelum ada yang menggulung ke sana — biayanya dibayar, hasilnya tidak
   *     pernah dilihat.
   *   - Muncul berurutan memberi arah baca; muncul serentak hanya jadi kedipan.
   *
   * Yang di-reveal HANYA kartu KPI dan kartu chart. Kartu lead sengaja tidak:
   * daftarnya digambar ulang setiap ketikan di kotak cari, jadi animasinya
   * akan berkedip terus saat mengetik.
   */
  var REVEAL_STEP_MS = 70;   /* jeda antar kartu dalam satu rombongan */
  var REVEAL_MAX_STEP = 7;   /* jeda berhenti bertambah setelah kartu ke-8 */

  /*
   * Jaring pengaman. Kartu yang menunggu reveal berada di `opacity: 0`, jadi
   * kalau observer-nya karena satu dan lain hal TIDAK PERNAH menyala, kartunya
   * tak kasat mata selamanya — dashboard tampak kosong dan tidak ada cara
   * pengguna memperbaikinya. Itu kegagalan yang jauh lebih buruk daripada
   * kehilangan animasi.
   *
   * Kejadian nyata yang memicunya: dokumen dirender di tab tersembunyi
   * (`visibilityState: 'hidden'`) — IntersectionObserver tidak pernah
   * memanggil balik di sana. Juga: elemen di dalam wadah yang tidak pernah
   * menghasilkan kotak layout.
   *
   * Enam detik dipilih supaya jauh lebih lama dari gulungan wajar, sehingga di
   * jalur normal timer ini selalu keburu dibatalkan dan tidak pernah terasa.
   */
  var REVEAL_FAILSAFE_MS = 6000;

  var revealIO = null;

  function prefersReducedMotion() {
    try {
      return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
    } catch (e) { return false; }
  }

  /**
   * Lepas kelas reveal. Ini SEKALIGUS jaminan kartu terlihat: begitu `reveal`
   * hilang, aturan `opacity: 0` ikut hilang — terlepas dari apakah animasinya
   * sempat berjalan.
   */
  function clearReveal(el) {
    el.classList.remove('reveal', 'is-in');
    el.style.animationDelay = '';
  }

  /** Jalankan animasi muncul untuk `el`, dengan jeda `delayMs`. Idempoten. */
  function fireReveal(el, delayMs) {
    if (!el || el._vdRevealed) return;
    el._vdRevealed = true;
    if (el._vdRevealTimer) { global.clearTimeout(el._vdRevealTimer); el._vdRevealTimer = 0; }
    if (revealIO) revealIO.unobserve(el);

    var d = delayMs || 0;
    el.style.animationDelay = d + 'ms';
    el.classList.add('is-in');

    /*
     * Pembersihan dijadwalkan dengan timer, BUKAN hanya menunggu `animationend`.
     * Animasi CSS tidak berjalan di dokumen yang tersembunyi, jadi di sana
     * `animationend` tidak pernah datang — dan karena `animation-fill-mode:
     * both` menahan bingkai pertama, kartunya akan bertahan di opacity 0.
     * Timer tetap jalan di tab tersembunyi, sehingga kartu dijamin terlihat.
     * `animationend` di reveal() tetap ada karena biasanya datang lebih dulu.
     */
    global.setTimeout(function () { clearReveal(el); }, d + 700);
  }

  function revealObserver() {
    if (revealIO) return revealIO;
    revealIO = new global.IntersectionObserver(function (entries) {
      /* Entri datang dalam satu rombongan tapi urutannya tidak dijamin.
       * Diurutkan menurut posisi vertikal supaya jeda bertingkatnya mengalir
       * dari atas ke bawah, bukan acak. */
      var hits = [], i;
      for (i = 0; i < entries.length; i++) if (entries[i].isIntersecting) hits.push(entries[i]);
      hits.sort(function (a, b) {
        return a.boundingClientRect.top - b.boundingClientRect.top;
      });
      for (i = 0; i < hits.length; i++) {
        fireReveal(hits[i].target, Math.min(i, REVEAL_MAX_STEP) * REVEAL_STEP_MS);
      }
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.1 });
    return revealIO;
  }

  /**
   * Daftarkan satu elemen untuk muncul saat tergulung ke layar.
   *
   * Kelasnya DILEPAS lagi setelah animasi selesai. Kalau dibiarkan, aturan
   * `animation-fill-mode: both` terus memaksa `transform: none` dan mengalahkan
   * efek angkat saat kursor lewat di atas kartu.
   */
  function reveal(el) {
    if (!el) return el;
    /* Tanpa IntersectionObserver, atau saat pengguna meminta gerak minimal,
     * kartu tampil apa adanya — jangan pernah menyembunyikannya lebih dulu. */
    if (prefersReducedMotion() || !global.IntersectionObserver) return el;

    el.classList.add('reveal');
    el.addEventListener('animationend', function onDone(ev) {
      if (ev.animationName !== 'vd-reveal') return;
      el.removeEventListener('animationend', onDone);
      clearReveal(el);
    });
    revealObserver().observe(el);
    el._vdRevealTimer = global.setTimeout(function () { fireReveal(el, 0); },
                                          REVEAL_FAILSAFE_MS);
    return el;
  }

  /* --------------------------------------------------------------- ikon -- */

  var SVG_NS = 'http://www.w3.org/2000/svg';

  /**
   * Ikon garis bergaya SF Symbols. Semuanya di kanvas 24x24, stroke 1.8,
   * mewarisi `currentColor` supaya otomatis benar di kedua tema.
   *
   * Path ditulis di sini (bukan sebagai berkas .svg terpisah) supaya tidak ada
   * request tambahan dan tidak ada aset yang bisa gagal dimuat saat offline.
   */
  var ICON_PATHS = {
    sun: ['M12 4.2V2.4', 'M12 21.6v-1.8', 'M19.5 12h1.8', 'M2.7 12h1.8',
          'M17.3 6.7l1.3-1.3', 'M5.4 18.6l1.3-1.3', 'M17.3 17.3l1.3 1.3',
          'M5.4 5.4l1.3 1.3', 'M12 8a4 4 0 100 8 4 4 0 000-8z'],
    moon: ['M20 13.4A8.2 8.2 0 1110.6 4a6.6 6.6 0 009.4 9.4z'],
    refresh: ['M20 12a8 8 0 11-2.6-5.9', 'M20 4.4V9h-4.6'],
    logout: ['M15.5 8.2V6.4A1.9 1.9 0 0013.6 4.5H6.4A1.9 1.9 0 004.5 6.4v11.2a1.9 1.9 0 001.9 1.9h7.2a1.9 1.9 0 001.9-1.9v-1.8',
             'M11 12h9.5', 'M17.6 8.8l3.4 3.2-3.4 3.2'],
    search: ['M11 4.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13z', 'M16 16l3.5 3.5'],
    close: ['M6.4 6.4l11.2 11.2', 'M17.6 6.4L6.4 17.6'],
    chevron: ['M9.5 5.5l6.5 6.5-6.5 6.5'],
    dots: ['M12 6.6h.01', 'M12 12h.01', 'M12 17.4h.01'],
    person: ['M12 4.6a3.7 3.7 0 100 7.4 3.7 3.7 0 000-7.4z',
             'M4.8 19.4a7.2 7.2 0 0114.4 0'],
    sliders: ['M4 7.5h10', 'M18 7.5h2', 'M4 16.5h4', 'M12 16.5h8',
              'M16 5.5v4', 'M10 14.5v4'],
    eye: ['M2.6 12S6.4 5.6 12 5.6 21.4 12 21.4 12 17.6 18.4 12 18.4 2.6 12 2.6 12z',
          'M12 9.2a2.8 2.8 0 100 5.6 2.8 2.8 0 000-5.6z'],
    eyeOff: ['M9.6 5.9A8.6 8.6 0 0112 5.6c5.6 0 9.4 6.4 9.4 6.4a16 16 0 01-3.2 3.8',
             'M6.1 7.5A16.3 16.3 0 002.6 12S6.4 18.4 12 18.4a8.9 8.9 0 003.6-.75',
             'M10 10.1a2.8 2.8 0 003.9 3.9', 'M4.5 4.5l15 15']
  };

  /** Bangun elemen <svg> untuk satu ikon. Nama tak dikenal -> null. */
  function icon(name) {
    var paths = ICON_PATHS[name];
    if (!paths) return null;
    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '1.8');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    for (var i = 0; i < paths.length; i++) {
      var p = document.createElementNS(SVG_NS, 'path');
      p.setAttribute('d', paths[i]);
      svg.appendChild(p);
    }
    return svg;
  }

  /** Tempelkan ikon ke sebuah tombol/elemen (kalau namanya dikenal). */
  function withIcon(host, name) {
    var ic = icon(name);
    if (ic && host) host.appendChild(ic);
    return host;
  }

  /* ------------------------------------------------------------- avatar -- */

  /**
   * Berkas gambar untuk sebuah tenant, diambil dari deskriptor yang dikirim
   * server (`stats.tenant.logo`). Tidak ada -> '' (pemanggil pakai emblem
   * huruf awal).
   *
   * Dulu ini mencocokkan id/nama tenant ke peta TENANT_LOGOS di config.js —
   * artinya menambah klien menuntut perubahan kode frontend, padahal
   * arsitekturnya menjanjikan sebaliknya. Sekarang frontend buta: yang tahu
   * klien mana punya logo apa hanyalah n8n/src/tenants.js.
   *
   * NILAINYA DISARING. Meski sumbernya adalah server kita sendiri di balik
   * token HMAC, nilai ini berakhir di `img.src`. Yang diterima hanya dua
   * bentuk, keduanya mustahil menghubungi pihak luar:
   *
   *   1. path relatif se-origin  -> 'icons/logo.jpg'
   *   2. data URI gambar         -> 'data:image/jpeg;base64,...'
   *
   * Bentuk kedua ada karena demo satu-berkas (demo/build_demo.py) menyisipkan
   * gambarnya langsung ke dalam payload; tanpa izin ini logo di demo selalu
   * jatuh ke emblem huruf. Aman: data URI tidak menimbulkan request, dan SVG
   * di dalam <img> tidak mengeksekusi skrip. Jangan pakai bentuk ini di
   * tenants.js produksi — isinya ikut terkirim di SETIAP respons `stats`.
   *
   * Yang ditolak: URL absolut ke host lain (membocorkan ke pihak ketiga bahwa
   * dashboard sedang dibuka, sekaligus melanggar jaminan "tanpa dependensi
   * eksternal"), path berawalan '/' atau '//', penelusuran '..', dan skema
   * lain apa pun seperti `javascript:`.
   */
  function tenantLogoSrc(tenant) {
    var v = str(tenant && tenant.logo).trim();
    if (v === '') return '';
    if (/^data:image\/[a-z0-9.+-]+[;,]/i.test(v)) return v;
    if (/^[a-z][a-z0-9+.-]*:/i.test(v)) return '';   // skema lain -> tolak
    if (v.charAt(0) === '/' || v.indexOf('//') === 0) return '';
    if (v.indexOf('..') !== -1) return '';
    return v;
  }

  /**
   * Isi kotak logo merek di header.
   * Kalau tenant punya foto, foto dipakai; kalau gambar gagal dimuat (berkas
   * hilang saat deploy), elemen otomatis jatuh kembali ke emblem huruf supaya
   * header tidak pernah tampil kosong.
   */
  function brandLogo(host, tenant) {
    if (!host) return host;
    clear(host);
    host.classList.remove('has-img');

    var initial = str(tenant && tenant.name).trim().charAt(0).toUpperCase() || 'V';
    var src = tenantLogoSrc(tenant);

    if (src) {
      var img = document.createElement('img');
      img.alt = '';
      img.decoding = 'async';
      img.addEventListener('error', function () {
        host.classList.remove('has-img');
        clear(host);
        host.appendChild(document.createTextNode(initial));
      });
      img.src = src;
      host.classList.add('has-img');
      host.appendChild(img);
      return host;
    }

    host.appendChild(document.createTextNode(initial));
    return host;
  }

  /* ----------------------------------------------------- kepala seksi -- */

  /**
   * Tombol bulat "i". Sengaja <button>, bukan <span> ber-`title`: tooltip
   * `title` tidak pernah muncul di layar sentuh, jadi versi lama membuat
   * penjelasan tidak bisa diakses sama sekali dari ponsel.
   *
   * `onHint(title, text)` dipanggil saat ditekan. `title` tetap dipasang
   * supaya pengguna mouse tetap dapat tooltip cepat tanpa harus mengklik.
   */
  function infoButton(cls, title, text, onHint) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = cls;
    b.textContent = 'i';
    b.title = str(text);
    b.setAttribute('aria-label', 'Penjelasan: ' + str(title));
    b.addEventListener('click', function (ev) {
      ev.stopPropagation();
      ev.preventDefault();
      if (onHint) onHint(str(title), str(text));
    });
    return b;
  }

  /**
   * Kepala seksi yang bisa dibuka/tutup.
   *
   * Mengembalikan { head, body, setCount } — pemanggil mengisi `body` dan
   * memasang keduanya ke dalam kartu. Status buka/tutup disimpan pemanggil
   * (app.js), bukan di sini, supaya renderer tetap bebas state.
   *
   * opts:
   *   id        — kunci stabil untuk mengingat status lipat
   *   title     — teks judul (dari server)
   *   count     — teks kecil di kanan judul (opsional)
   *   hint      — penjelasan; kalau ada, tombol "i" ikut dipasang
   *   expanded  — status awal
   *   onToggle(id, expanded) — dipanggil setiap kali ditekan
   *   onHint(title, text)
   */
  var sectionSeq = 0;

  function sectionHead(opts) {
    var o = opts || {};
    var head = elem('div', 'section-head');
    var body = elem('div', 'section-body');

    sectionSeq++;
    var bodyId = 'sec-body-' + sectionSeq;
    body.id = bodyId;

    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'section-toggle';
    toggle.setAttribute('aria-controls', bodyId);

    var caret = elem('span', 'section-caret');
    withIcon(caret, 'chevron');
    toggle.appendChild(caret);
    toggle.appendChild(elem('span', 'section-label', o.title || ''));

    var count = elem('span', 'section-count', o.count || '');
    toggle.appendChild(count);
    head.appendChild(toggle);

    if (str(o.hint) !== '') {
      head.appendChild(infoButton('section-info', o.title || '', o.hint, o.onHint));
    }

    var expanded = o.expanded !== false;

    function apply(next) {
      expanded = !!next;
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      body.hidden = !expanded;
      // Kartu induk baru ada setelah kepala ini dipasang, jadi kelasnya
      // ditelusuri saat dipakai — bukan disimpan saat dibuat.
      var card = head.parentNode && head.parentNode.closest
        ? head.parentNode.closest('.glass-card') : null;
      if (card) card.classList.toggle('is-collapsed', !expanded);
    }
    apply(expanded);

    toggle.addEventListener('click', function () {
      apply(!expanded);
      if (o.onToggle) o.onToggle(o.id, expanded);
    });

    return {
      head: head,
      body: body,
      isExpanded: function () { return expanded; },
      setCount: function (v) { count.textContent = str(v); }
    };
  }

  /* ------------------------------------------------------------------ KPI */

  /** Tone yang sah saja yang boleh masuk ke nama kelas / custom property. */
  function safeTone(v) {
    var pal = (global.VDCharts && global.VDCharts.PALETTE) ||
              ['blue', 'teal', 'purple', 'orange', 'green', 'red', 'pink', 'gray'];
    var t = String(v || '').toLowerCase();
    return pal.indexOf(t) !== -1 ? t : 'blue';
  }

  function kpiCard(kpi, range, onHint) {
    var card = elem('div', 'metric-card');

    var label = kpi.label || kpi.id || '';
    var head = elem('div', 'metric-head');
    head.appendChild(elem('span', 'metric-label', label));
    if (kpi.hint) head.appendChild(infoButton('metric-info', label, kpi.hint, onHint));
    card.appendChild(head);

    var tone = safeTone(kpi.tone);
    // Semburat warna di sudut kartu dibaca CSS dari --mc-tone.
    card.style.setProperty('--mc-tone', 'var(--tone-' + tone + ')');
    card.appendChild(elem('div', 'metric-val tone-' + tone, fmtInt(kpiValue(kpi, range))));

    if (kpi.sub) card.appendChild(elem('div', 'metric-sub', kpi.sub));
    if (kpi.rangeAware) card.appendChild(elem('div', 'metric-range', range + ' hari'));
    return card;
  }

  function kpiGrid(host, kpis, range, onHint) {
    clear(host);
    var list = kpis || [];
    for (var i = 0; i < list.length; i++) {
      host.appendChild(reveal(kpiCard(list[i], range, onHint)));
    }
  }

  /* ---------------------------------------------------------------- Chart */

  /**
   * Kartu chart. `sec` berisi kait lipat dari pemanggil (app.js):
   *   { expanded, onToggle, onHint }
   *
   * Chart yang sedang tertutup TIDAK digambar — lebarnya nol saat tersembunyi,
   * dan SVG yang digambar dengan lebar nol menghasilkan viewBox rusak. Jadi
   * penggambaran ditunda sampai seksinya benar-benar terbuka.
   */
  function chartCard(chart, range, sec) {
    var s = sec || {};
    var card = elem('section', 'glass-card chart-card');

    var host = elem('div', 'chart-host');
    var sliced = sliceChart(chart, range);
    var drawn = false;

    function draw() {
      if (global.VDCharts) global.VDCharts.render(sliced, host);
      drawn = true;
    }

    var head = sectionHead({
      id: 'chart:' + (chart.id || chart.title || ''),
      title: chart.title || '',
      hint: chart.hint || '',
      expanded: s.expanded !== false,
      onHint: s.onHint,
      onToggle: function (id, expanded) {
        // Gambar saat pertama kali dibuka, bukan saat dibuat.
        if (expanded && !drawn) draw();
        if (s.onToggle) s.onToggle(id, expanded);
      }
    });

    head.body.appendChild(host);
    if (chart.note) head.body.appendChild(elem('div', 'chart-note', chart.note));

    card.appendChild(head.head);
    card.appendChild(head.body);
    card.classList.toggle('is-collapsed', !head.isExpanded());

    card._vdDraw = function () { if (head.isExpanded()) draw(); };
    card._vdSection = head;
    return card;
  }

  function chartGrid(host, charts, range, sec) {
    clear(host);
    var list = charts || [];
    var cards = [];
    for (var i = 0; i < list.length; i++) {
      var c = chartCard(list[i], range, sec);
      host.appendChild(c);
      cards.push(c);
    }
    // Digambar setelah dilampirkan supaya clientWidth sudah nyata.
    for (var j = 0; j < cards.length; j++) cards[j]._vdDraw();
    return cards;
  }

  /* ----------------------------------------------------------------- Sel */

  /**
   * Isi satu sel sesuai `column.type`. Tidak tahu-menahu soal nama kolom.
   * `handlers.onToggle(row, nextMode, switchEl)` dipanggil untuk type toggle.
   */
  function cell(row, column, handlers) {
    var td = elem('td');
    var type = String(column.type || 'text').toLowerCase();
    var raw = row ? row[column.key] : '';

    if (type === 'toggle') {
      td.className = 'col-toggle';
      td.appendChild(toggleSwitch(row, handlers));
      return td;
    }

    if (type === 'wa') {
      td.className = 'col-wa';
      var shown = str(raw) !== '' ? str(raw) : (str(row && row.lid) !== '' ? str(row.lid) : str(row && row.key));
      td.appendChild(elem('span', 'mono', shown || '—'));
      if (row && row.is_lid) {
        var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
        var b = elem('span', 'badge badge-lid', txt.lidBadge || 'LID');
        b.title = txt.lidHint || '';
        td.appendChild(b);
      }
      return td;
    }

    if (type === 'int') {
      td.className = 'col-num';
      td.textContent = fmtInt(raw);
      return td;
    }

    if (type === 'date') {
      td.className = 'col-date';
      td.textContent = fmtDate(raw);
      return td;
    }

    if (type === 'badge') {
      var v = str(raw);
      if (v === '') { td.textContent = '—'; td.className = 'is-dim'; return td; }
      var parts = v.split(',');
      for (var i = 0; i < parts.length && i < 3; i++) {
        var p = parts[i].trim();
        if (p === '') continue;
        td.appendChild(elem('span', 'badge tone-bg-' + badgeTone(p), p));
      }
      if (parts.length > 3) td.appendChild(elem('span', 'badge tone-bg-gray', '+' + (parts.length - 3)));
      return td;
    }

    var s = str(raw);
    td.textContent = s === '' ? '—' : s;
    if (s === '') td.className = 'is-dim';
    return td;
  }

  /**
   * Bot dianggap aktif kecuali persis "OFF".
   *
   * `trim()` bukan hiasan: kedua workflow bot memakai
   * `String(v).trim().toUpperCase() === 'OFF'`. Tanpa trim di sini, sel berisi
   * `" off "` akan tampil ON di dashboard padahal bot sudah berhenti membalas —
   * beda persepsi antara apa yang dilihat owner dan apa yang dilakukan bot.
   */
  function isBotOn(row) {
    return String(row && row.bot_mode).trim().toUpperCase() !== 'OFF';
  }

  /**
   * Mode yang dituju kalau switch baris ini ditekan SEKARANG.
   *
   * Harus dihitung ulang saat diklik, bukan saat baris digambar. Versi awal
   * menyimpan statusnya di variabel closure; setelah satu kali toggle, nilai
   * itu basi sementara `row.bot_mode` sudah diperbarui — akibatnya klik kedua
   * mengirim mode yang sama dan bot tidak pernah bisa dinyalakan kembali
   * tanpa merender ulang tabel.
   */
  function nextMode(row) {
    return isBotOn(row) ? 'OFF' : 'ON';
  }

  function toggleSwitch(row, handlers) {
    var sw = document.createElement('button');
    sw.type = 'button';
    sw.className = 'ios-switch';
    sw.setAttribute('role', 'switch');
    sw.appendChild(elem('span', 'ios-knob'));
    setSwitch(sw, isBotOn(row) ? 'ON' : 'OFF');
    sw.addEventListener('click', function (ev) {
      ev.stopPropagation();
      if (sw.disabled) return;
      if (handlers && handlers.onToggle) {
        // Dibaca dari model saat diklik — bukan dari nilai saat render.
        handlers.onToggle(row, nextMode(row), sw);
      }
    });
    return sw;
  }

  /** Ubah tampilan switch tanpa merender ulang tabel (untuk optimistic update). */
  function setSwitch(sw, mode) {
    var on = isBotOn({ bot_mode: mode });
    sw.classList.toggle('on', on);
    sw.setAttribute('aria-checked', on ? 'true' : 'false');
    sw.setAttribute('aria-label', 'Bot ' + (on ? 'aktif' : 'nonaktif'));
  }

  /* ---------------------------------------------------------- Tabel lead */

  /**
   * Bangun <table> lead.
   * state: { sortKey, sortDir }
   * handlers: { onSort(key), onRow(row), onToggle(row, next, sw) }
   */
  function leadTable(columns, rows, state, handlers) {
    var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
    var table = elem('table', 'data-table');
    var thead = elem('thead');
    var htr = elem('tr');
    var cols = columns || [];

    for (var c = 0; c < cols.length; c++) {
      (function (col) {
        var th = elem('th');
        th.className = 'th-sortable' + (String(col.type) === 'toggle' ? ' col-toggle' : '');
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'th-btn';
        btn.appendChild(elem('span', null, col.label || col.key));
        var caret = elem('span', 'th-caret', state && state.sortKey === col.key
          ? (state.sortDir === 'asc' ? '▲' : '▼') : '');
        btn.appendChild(caret);
        if (state && state.sortKey === col.key) th.classList.add('is-sorted');
        btn.addEventListener('click', function () {
          if (handlers && handlers.onSort) handlers.onSort(col.key);
        });
        th.appendChild(btn);
        htr.appendChild(th);
      }(cols[c]));
    }
    thead.appendChild(htr);
    table.appendChild(thead);

    var tbody = elem('tbody');
    if (!rows || rows.length === 0) {
      var etr = elem('tr');
      var etd = elem('td', 'empty-cell', txt.emptyLeads || 'Tidak ada data.');
      etd.colSpan = Math.max(1, cols.length);
      etr.appendChild(etd);
      tbody.appendChild(etr);
    } else {
      for (var r = 0; r < rows.length; r++) {
        (function (row) {
          var tr = elem('tr', 'row-click' + (isHighlighted(row, handlers) ? ' is-new' : ''));
          tr.tabIndex = 0;
          for (var k = 0; k < cols.length; k++) tr.appendChild(cell(row, cols[k], handlers));
          tr.addEventListener('click', function () {
            if (handlers && handlers.onRow) handlers.onRow(row);
          });
          tr.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter' || ev.key === ' ') {
              ev.preventDefault();
              if (handlers && handlers.onRow) handlers.onRow(row);
            }
          });
          tbody.appendChild(tr);
        }(rows[r]));
      }
    }
    table.appendChild(tbody);
    return table;
  }

  /* --------------------------------------------- Daftar lead versi kartu */

  /**
   * Teks tampilan untuk sebuah sel, TANPA membuat elemen. Dipakai kartu untuk
   * menampilkan nilai kolom apa pun tanpa menduplikasi logika format.
   * Kolom bertipe toggle tidak punya bentuk teks — pemanggil menanganinya.
   */
  function cellText(row, column) {
    var type = String(column.type || 'text').toLowerCase();
    var raw = row ? row[column.key] : '';
    if (type === 'int') return fmtInt(raw);
    if (type === 'date') return fmtDate(raw);
    var s = str(raw);
    return s === '' ? '—' : s;
  }

  /**
   * Apakah baris ini sedang disorot.
   *
   * Pemanggil hanya mengoper `handlers.highlightKey` berupa string; file ini
   * tetap tidak tahu apa artinya sebuah baris "baru" — ia cuma membandingkan
   * `row.key`, yang memang sudah bagian dari kontrak baris (dipakai juga oleh
   * rowIdent dan jalur toggle).
   */
  function isHighlighted(row, handlers) {
    if (!handlers || !handlers.highlightKey) return false;
    return str(row && row.key) !== '' &&
           str(row.key) === str(handlers.highlightKey);
  }

  /** Identitas yang ditampilkan di baris kedua kartu: wa > lid > key. */
  function rowIdent(row) {
    if (!row) return '';
    if (str(row.wa) !== '') return str(row.wa);
    if (str(row.lid) !== '') return str(row.lid);
    return str(row.key);
  }

  /**
   * Satu kartu lead untuk layar sempit.
   *
   * Kenapa bentuk kartu, bukan tabel yang digulung ke samping: di 375px tabel
   * 7 kolom memaksa pengguna menggeser horizontal, dan kolom paling kanan —
   * yang justru switch bot — tidak pernah terlihat tanpa digeser. Kartu
   * menaruh nama, identitas, angka penting, dan switch dalam satu pandangan.
   *
   * Kolom tetap dibaca dari deskriptor server; tidak ada nama kolom yang
   * ditulis di sini. Aturannya murni berdasarkan `type`:
   *   toggle -> switch di sisi kanan
   *   wa     -> baris identitas (sudah tampil di bawah nama)
   *   badge  -> pill
   *   sisanya-> chip "label nilai"
   */
  function leadCard(columns, row, handlers) {
    var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
    var card = elem('div', 'lead-card row-click' +
                    (isHighlighted(row, handlers) ? ' is-new' : ''));
    card.tabIndex = 0;
    card.setAttribute('role', 'button');

    var name = str(row && row.nama).trim();
    var ident = rowIdent(row);

    /*
     * Di data nyata, banyak lead belum pernah menyebut namanya — kolom `nama`
     * berisi nomor WhatsApp itu sendiri. Menampilkannya dua kali (judul dan
     * baris identitas) hanya membuang baris dan membuat daftar sulit dipindai.
     * Jadi nama dianggap "nama sungguhan" hanya kalau ia berbeda dari
     * identitasnya setelah dibandingkan sebagai digit.
     */
    var hasRealName = name !== '' && !(digits(name) !== '' && digits(name) === digits(ident));
    var title = hasRealName ? name : (ident || '—');

    var avatar = elem('div', 'lead-card-avatar');
    if (hasRealName) {
      avatar.appendChild(document.createTextNode(name.charAt(0).toUpperCase()));
    } else {
      // Huruf awal dari sebuah nomor selalu "6" untuk semua orang — tidak
      // membedakan apa pun. Ikon orang lebih jujur: identitasnya belum dikenal.
      avatar.classList.add('is-anon');
      withIcon(avatar, 'person');
    }
    // Warna avatar stabil per lead supaya daftar mudah dipindai matanya.
    avatar.style.setProperty('--lc-tone', 'var(--tone-' + badgeTone(name || ident) + ')');
    card.appendChild(avatar);

    var main = elem('div', 'lead-card-main');
    main.appendChild(elem('div', 'lead-card-name', title));

    // Baris identitas hanya kalau ia menambah informasi.
    if (hasRealName || (row && row.is_lid)) {
      var idLine = elem('div', 'lead-card-id');
      idLine.appendChild(document.createTextNode(ident || '—'));
      if (row && row.is_lid) {
        var b = elem('span', 'badge badge-lid', txt.lidBadge || 'LID');
        b.title = txt.lidHint || '';
        idLine.appendChild(b);
      }
      main.appendChild(idLine);
    }

    var meta = elem('div', 'lead-card-meta');
    var cols = columns || [];
    var toggleCol = null;

    for (var i = 0; i < cols.length; i++) {
      var col = cols[i];
      var type = String(col.type || 'text').toLowerCase();

      if (type === 'toggle') { toggleCol = col; continue; }
      if (type === 'wa') continue;                       // sudah jadi baris identitas
      if (col.key === 'nama') continue;                  // sudah jadi judul kartu

      var raw = str(row ? row[col.key] : '');
      if (raw === '') continue;                          // kosong: jangan bikin gaduh

      if (type === 'badge') {
        var parts = raw.split(',');
        for (var p = 0; p < parts.length && p < 2; p++) {
          var v = parts[p].trim();
          if (v !== '') meta.appendChild(elem('span', 'badge tone-bg-' + badgeTone(v), v));
        }
        if (parts.length > 2) {
          meta.appendChild(elem('span', 'badge tone-bg-gray', '+' + (parts.length - 2)));
        }
        continue;
      }

      var chip = elem('span', 'lead-card-stat');
      chip.appendChild(elem('b', null, cellText(row, col)));
      chip.appendChild(document.createTextNode(col.label || col.key || ''));
      meta.appendChild(chip);
    }

    if (meta.firstChild) main.appendChild(meta);
    card.appendChild(main);

    var side = elem('div', 'lead-card-side');
    if (toggleCol) side.appendChild(toggleSwitch(row, handlers));
    var chev = elem('span', 'lead-card-chev');
    withIcon(chev, 'chevron');
    side.appendChild(chev);
    card.appendChild(side);

    function open() { if (handlers && handlers.onRow) handlers.onRow(row); }
    card.addEventListener('click', open);
    card.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); open(); }
    });

    return card;
  }

  /** Bungkus daftar kartu lead. Kosong -> empty state yang sama dengan tabel. */
  function leadCards(columns, rows, handlers) {
    var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
    var box = elem('div', 'lead-cards');
    if (!rows || !rows.length) {
      box.appendChild(elem('div', 'empty-box', txt.emptyLeads || 'Tidak ada data.'));
      return box;
    }
    for (var i = 0; i < rows.length; i++) box.appendChild(leadCard(columns, rows[i], handlers));
    return box;
  }

  /* ------------------------------------------------------- Tabel tambahan */

  /**
   * Kartu rekomendasi.
   *
   * Seperti seluruh file ini, tidak tahu apa pun soal isi: judul, alasan, aksi,
   * dan angka pendukung semuanya datang dari server. Yang ditentukan di sini
   * hanya susunannya.
   *
   * Dua hal sengaja dipaksa muncul, bukan opsional:
   *   - Penanda bahwa isinya dibuat AI. Saran yang tampil sama rapinya dengan
   *     angka hasil hitungan akan dibaca sebagai fakta kalau tidak ditandai.
   *   - Angka pendukung tiap butir ("dasar"). Rekomendasi tanpa angka tidak
   *     bisa dicek balik ke kartu di atasnya, dan yang tidak bisa dicek tidak
   *     pantas dipakai mengambil keputusan.
   *
   * spec = { id, title, hint, generated_at, model, items:[{judul, alasan,
   *          aksi, dampak, dasar:[...]}] }
   */
  function insightCard(spec, sec) {
    var s = sec || {};
    var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
    var section = elem('section', 'glass-card');
    var items = (spec && spec.items) || [];

    var head = sectionHead({
      id: 'insight:' + ((spec && spec.id) || ''),
      title: (spec && spec.title) || '',
      count: items.length ? fmtInt(items.length) + ' saran' : '',
      hint: (spec && spec.hint) || '',
      expanded: s.expanded !== false,
      onHint: s.onHint,
      onToggle: s.onToggle
    });
    section.appendChild(head.head);
    section.appendChild(head.body);
    section.classList.toggle('is-collapsed', !head.isExpanded());

    var badge = elem('div', 'insight-badge');
    badge.appendChild(elem('span', 'insight-dot'));
    badge.appendChild(document.createTextNode(
      (txt.insightBadge || 'Dibuat AI') +
      (str(spec && spec.model) !== '' ? ' · ' + str(spec.model) : '')));
    head.body.appendChild(badge);

    if (!items.length) {
      head.body.appendChild(elem('div', 'empty-box',
        txt.insightEmpty || 'Belum ada rekomendasi.'));
      return section;
    }

    var list = elem('div', 'insight-list');
    for (var i = 0; i < items.length; i++) {
      var it = items[i] || {};
      var card = elem('article', 'insight-item');

      var top = elem('div', 'insight-item-head');
      top.appendChild(elem('h3', 'insight-title', str(it.judul)));
      var dampak = str(it.dampak).toLowerCase();
      if (dampak !== '') {
        top.appendChild(elem('span', 'insight-impact tone-bg-' + safeTone(
          dampak === 'tinggi' ? 'green' : dampak === 'rendah' ? 'gray' : 'orange'),
          (txt.insightImpact || 'Dampak') + ' ' + dampak));
      }
      card.appendChild(top);

      if (str(it.alasan) !== '') card.appendChild(elem('p', 'insight-why', str(it.alasan)));

      if (str(it.aksi) !== '') {
        var act = elem('div', 'insight-action');
        act.appendChild(elem('span', 'insight-action-label', txt.insightAction || 'Lakukan'));
        act.appendChild(elem('span', 'insight-action-text', str(it.aksi)));
        card.appendChild(act);
      }

      var dasar = (it.dasar && it.dasar.length) ? it.dasar : [];
      if (dasar.length) {
        var chips = elem('div', 'insight-basis');
        for (var b = 0; b < dasar.length; b++) {
          chips.appendChild(elem('span', 'insight-chip', str(dasar[b])));
        }
        card.appendChild(chips);
      }

      list.appendChild(card);
    }
    head.body.appendChild(list);
    return section;
  }

  function simpleTable(spec, sec) {
    var s = sec || {};
    var section = elem('section', 'glass-card');

    var rows = spec.rows || [];
    var cols = spec.columns || [];

    var head = sectionHead({
      id: 'table:' + (spec.id || spec.title || ''),
      title: spec.title || '',
      count: typeof spec.total === 'number' ? fmtInt(spec.total) + ' baris' : '',
      hint: spec.hint || '',
      expanded: s.expanded !== false,
      onHint: s.onHint,
      onToggle: s.onToggle
    });
    section.appendChild(head.head);
    section.appendChild(head.body);
    section.classList.toggle('is-collapsed', !head.isExpanded());

    if (!rows.length) {
      head.body.appendChild(elem('div', 'empty-box', spec.empty || 'Belum ada data.'));
      return section;
    }

    var wrap = elem('div', 'table-wrap');
    var table = elem('table', 'data-table');
    var thead = elem('thead');
    var htr = elem('tr');
    for (var c = 0; c < cols.length; c++) htr.appendChild(elem('th', null, cols[c].label || cols[c].key));
    thead.appendChild(htr);
    table.appendChild(thead);

    var tbody = elem('tbody');
    for (var r = 0; r < rows.length; r++) {
      var tr = elem('tr');
      for (var k = 0; k < cols.length; k++) tr.appendChild(cell(rows[r], cols[k], null));
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    wrap.appendChild(table);
    head.body.appendChild(wrap);

    if (spec.truncated) {
      var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
      head.body.appendChild(elem('div', 'table-note',
        (txt.truncatedPrefix || 'Menampilkan') + ' ' + fmtInt(rows.length) + ' ' +
        (txt.truncatedMiddle || 'dari total') + ' ' + fmtInt(spec.total) + ' ' +
        (txt.truncatedSuffix || 'baris.')));
    }
    return section;
  }

  /* --------------------------------------------------------------- Drawer */

  /** Isi drawer dari `row.detail` — array {label,value}. */
  function detailList(row) {
    var txt = (global.VDConfig && global.VDConfig.TEXT) || {};
    var box = elem('div', 'detail-list');
    var list = (row && row.detail) || [];
    if (!list.length) {
      box.appendChild(elem('div', 'empty-box', txt.detailEmpty || 'Tidak ada detail.'));
      return box;
    }
    for (var i = 0; i < list.length; i++) {
      var item = elem('div', 'detail-item');
      item.appendChild(elem('div', 'detail-label', list[i].label || ''));
      item.appendChild(elem('div', 'detail-value', str(list[i].value) === '' ? '—' : str(list[i].value)));
      box.appendChild(item);
    }
    return box;
  }

  /* ============================================================= EKSPOR === */

  return {
    /* murni */
    kpiValue: kpiValue,
    sliceChart: sliceChart,
    filterLeads: filterLeads,
    sortLeads: sortLeads,
    paginate: paginate,
    fmtInt: fmtInt,
    fmtDate: fmtDate,
    fmtDateTime: fmtDateTime,
    badgeTone: badgeTone,
    safeTone: safeTone,
    cellText: cellText,
    rowIdent: rowIdent,
    isHighlighted: isHighlighted,
    tenantLogoSrc: tenantLogoSrc,
    /* DOM */
    elem: elem,
    clear: clear,
    icon: icon,
    withIcon: withIcon,
    brandLogo: brandLogo,
    reveal: reveal,
    infoButton: infoButton,
    sectionHead: sectionHead,
    kpiCard: kpiCard,
    kpiGrid: kpiGrid,
    chartCard: chartCard,
    chartGrid: chartGrid,
    cell: cell,
    leadTable: leadTable,
    leadCard: leadCard,
    leadCards: leadCards,
    insightCard: insightCard,
    simpleTable: simpleTable,
    detailList: detailList,
    setSwitch: setSwitch,
    toggleSwitch: toggleSwitch,
    isBotOn: isBotOn,
    nextMode: nextMode
  };

})(typeof window !== 'undefined' ? window : this);

if (typeof window !== 'undefined') window.VDRender = VDRender;
if (typeof module !== 'undefined' && module.exports) module.exports = VDRender;
