/* ============================================================================
 * config.js — SATU-SATUNYA FILE YANG PERLU DIEDIT SAAT DEPLOY
 *
 * Tidak ada logika bisnis di sini. Hanya alamat, kunci penyimpanan, angka
 * ambang, dan teks. Semua label bisnis (nama kolom, judul chart, nama tenant)
 * datang dari server — jangan pernah menaruhnya di sini.
 *
 * Bedanya dengan versi `app/`:
 *   - STORAGE_THEME  : menyimpan pilihan terang/gelap.
 *   - DEFAULT_THEME  : tema saat belum ada pilihan tersimpan.
 *   - TENANT_LOGOS   : peta id tenant -> berkas gambar untuk avatar merek.
 *     Ini SATU-SATUNYA tempat di seluruh frontend yang menyebut sebuah tenant,
 *     dan hanya untuk urusan gambar. Tenant yang tidak terdaftar di sini tetap
 *     tampil normal dengan emblem huruf awal — tidak ada fitur yang rusak.
 * ========================================================================== */
'use strict';

var VDConfig = {

  /* ---- Transport -------------------------------------------------------- */

  /**
   * Endpoint produksi. Ini nilai yang diedit saat deploy.
   * API_URL di bawah adalah hasil resolusi (query string > localStorage > ini)
   * dan diisi oleh blok di bagian bawah file.
   */
  DEFAULT_API_URL: 'https://n8n.srv1270416.hstgr.cloud/webhook/vira-dash',

  /** Kunci localStorage untuk override alamat API (staging / harness QA). */
  STORAGE_API_URL: 'vd_api_url',

  /** Diisi saat file dimuat. Jangan diedit di sini. */
  API_URL: '',

  /**
   * Content-Type sengaja text/plain: itu membuat request masuk kategori
   * "CORS simple request" sehingga browser tidak mengirim preflight OPTIONS
   * (webhook n8n tidak menangani OPTIONS). Jangan tambah header lain — satu
   * header kustom saja membatalkan ini dan seluruh request akan gagal.
   */
  CONTENT_TYPE: 'text/plain;charset=UTF-8',

  /** Batas waktu satu request sebelum dianggap gagal jaringan. */
  REQUEST_TIMEOUT_MS: 25000,

  /* ---- Penyimpanan lokal ------------------------------------------------ */

  STORAGE_TOKEN: 'vd.token',
  STORAGE_RANGE: 'vd.range',
  STORAGE_THEME: 'vd.theme',

  /**
   * Status lipat seksi dan daftar seksi yang disembunyikan. Keduanya
   * di-namespace per tenant (`<kunci>::<id tenant>`) karena tiap klien punya
   * susunan KPI, chart, dan tabel yang berbeda — pengaturan satu klien tidak
   * boleh bocor ke klien lain saat berpindah.
   */
  STORAGE_SECTIONS: 'vd.sections',
  STORAGE_HIDDEN: 'vd.hidden',

  /* ---- Perilaku UI ------------------------------------------------------ */

  /** 'dark' | 'light'. Dipakai kalau pengguna belum pernah memilih dan sistem
   *  tidak menyatakan preferensi. */
  DEFAULT_THEME: 'dark',

  /** Pilihan rentang hari. Harus cocok dengan kunci di KPI `values`. */
  RANGES: [7, 30, 90],
  DEFAULT_RANGE: 30,

  /** Baris per halaman di tabel lead. */
  PAGE_SIZE: 50,

  /** Tinggi area gambar chart (piksel). Dipakai charts.js. */
  CHART_HEIGHT: 240,
  CHART_HEIGHT_MOBILE: 200,

  /** Lebar viewport di bawah nilai ini diperlakukan sebagai ponsel. */
  MOBILE_BREAKPOINT: 640,

  /**
   * Di bawah lebar ini, daftar lead digambar sebagai kartu, bukan tabel.
   * Tabel yang harus digeser ke samping menyembunyikan kolom terakhir —
   * dan kolom terakhir itu justru switch bot.
   */
  CARD_BREAKPOINT: 720,

  /* ---- Error ------------------------------------------------------------ */

  /**
   * Kode error yang berarti sesi tidak lagi sah. Frontend keluar otomatis
   * dan menampilkan alasannya. Dicocokkan ke `error`, bukan ke `message`.
   */
  AUTH_ERRORS: /^TOKEN_|^TENANT_|^ROLE_CHANGED$/,

  /** Kode buatan klien (server tidak pernah mengirim ini). */
  CLIENT_ERRORS: {
    NETWORK: 'NETWORK',
    BAD_RESPONSE: 'BAD_RESPONSE'
  },

  /* ---- Teks -------------------------------------------------------------
   * Server selalu mengirim `message` dalam Bahasa Indonesia. Teks di bawah
   * hanya cadangan kalau `message` tidak ada atau kalau kegagalan terjadi
   * sebelum server sempat menjawab.
   * ---------------------------------------------------------------------- */
  TEXT: {
    appName: 'VIRA Dashboard',

    network: 'Tidak bisa menghubungi server. Periksa koneksi lalu coba lagi.',
    badResponse: 'Respons server tidak bisa dibaca.',
    unknown: 'Terjadi kesalahan yang tidak dikenali.',
    sessionEnded: 'Sesi berakhir. Silakan masuk kembali.',
    loggedOut: 'Anda sudah keluar.',

    loginTitle: 'Masuk',
    loginBusy: 'Memeriksa…',
    loginEmpty: 'Isi nama pengguna dan kata sandi.',
    loginSubmit: 'Masuk',
    showPass: 'Tampilkan kata sandi',
    hidePass: 'Sembunyikan kata sandi',

    loading: 'Memuat data…',
    refreshing: 'Mengambil data terbaru…',
    refreshed: 'Data diperbarui.',

    emptyChart: 'Belum ada data pada rentang ini.',
    emptyLeads: 'Tidak ada baris yang cocok.',
    noColumns: 'Server tidak mengirim definisi kolom.',

    lidBadge: 'LID',
    lidHint: 'Identitas LID. Nomor WhatsApp asli tidak terekspos, jadi kontak ini tidak bisa dihubungi manual dari nomor di layar.',

    toggleConfirmTitle: 'Ubah status bot',
    toggleOff: 'Bot akan berhenti membalas otomatis. Percakapan harus dilanjutkan manual.',
    toggleOn: 'Bot akan kembali membalas otomatis.',
    toggleCancel: 'Batal',
    toggleOk: 'Ya, ubah',

    /* ---- Tambah lead ----
     * addWarnOn sengaja berbunyi keras. Menambah nomor dengan bot ON membuat
     * nomor itu masuk jangkauan alur follow-up otomatis, yang bisa mengirim
     * WhatsApp ke orang yang belum pernah menghubungi sama sekali. Salah ketik
     * satu digit berarti pesan mendarat di nomor orang asing. */
    addOpen: 'Tambah',
    addTitle: 'Tambah nomor',
    addSub: 'Menambahkan satu baris baru ke data lead. Nomor yang sudah ada tidak bisa ditambahkan dua kali.',
    addWaLabel: 'Nomor WhatsApp',
    addWaPlaceholder: '081234567890',
    addWaHelp: 'Boleh diketik 08…, 62…, atau +62…',
    addNamaLabel: 'Nama (opsional)',
    addNamaPlaceholder: 'Kosongkan kalau belum tahu',
    addNamaHelp: 'Kalau dikosongkan, kolom nama diisi nomornya sendiri.',
    addBotLabel: 'Bot langsung aktif',
    addWarnOn: 'Hati-hati: dengan bot aktif, VIRA bisa mengirim WhatsApp lebih dulu ke nomor ini walaupun orangnya belum pernah chat. Pastikan nomornya benar.',
    addSubmit: 'Tambahkan',
    addBusy: 'Menambahkan…',
    addCancel: 'Batal',
    addInvalid: 'Nomor belum benar. Minimal 9 digit, contoh 081234567890.',
    addDone: 'Nomor ditambahkan.',

    /* ---- Rekomendasi AI ----
     * insightBadge WAJIB tampil di kartunya. Saran yang dirender serapi angka
     * hasil hitungan akan dibaca sebagai fakta kalau tidak ditandai. */
    insightBadge: 'Dibuat AI',
    insightEmpty: 'Belum ada rekomendasi untuk data bulan ini.',
    insightAction: 'Lakukan',
    insightImpact: 'Dampak',
    viewGroupInsight: 'Rekomendasi',

    cached: 'dari cache',
    truncatedPrefix: 'Menampilkan',
    truncatedMiddle: 'dari total',
    truncatedSuffix: 'baris.',

    detailTitle: 'Detail Lead',
    detailEmpty: 'Tidak ada detail tambahan.',

    hintClose: 'Mengerti',
    viewTitle: 'Atur tampilan',
    viewOpen: 'Atur tampilan',
    viewReset: 'Tampilkan semua lagi',
    viewGroupKpi: 'Kartu angka',
    viewGroupChart: 'Grafik',
    viewGroupTable: 'Tabel',
    viewGroupLeads: 'Direktori',
    viewHidden: 'Disembunyikan',
    viewEmptyNote: 'Kosong pada data saat ini',
    viewSaved: 'Tampilan diperbarui.',
    sectionExpand: 'Buka bagian',
    sectionCollapse: 'Tutup bagian',

    themeToDark: 'Beralih ke mode gelap',
    themeToLight: 'Beralih ke mode terang',
    menuLabel: 'Menu lainnya',
    refreshLabel: 'Segarkan',
    logoutLabel: 'Keluar',
    searchClear: 'Hapus pencarian',
    sortLabel: 'Urutkan',
    botOn: 'Bot aktif',
    botOff: 'Manual',
    prevPage: 'Sebelumnya',
    nextPage: 'Berikutnya',

    testModePrefix: 'Mode uji — terhubung ke',
    testModeReset: 'Kembali ke produksi',
    apiConfirmTitle: 'Alihkan alamat server?',
    apiConfirmBody: 'Halaman ini diminta memakai alamat server di luar alamat produksi. Data yang tampil bukan data produksi, dan Anda harus masuk ulang di alamat tersebut. Lanjutkan hanya kalau Anda sendiri yang menyiapkan alamat ini.',
    apiConfirmOk: 'Ya, pakai alamat itu',
    apiConfirmCancel: 'Pakai alamat produksi'
  },

  /**
   * Cadangan pesan per kode error. Dipakai hanya kalau server tidak
   * menyertakan `message`.
   */
  ERROR_TEXT: {
    BAD_REQUEST: 'Permintaan ditolak server.',
    BAD_CREDENTIALS: 'Nama pengguna atau kata sandi salah.',
    LOCKED_OUT: 'Terlalu banyak percobaan gagal. Coba lagi nanti.',
    TOKEN_MISSING: 'Sesi tidak ditemukan. Silakan masuk kembali.',
    TOKEN_MALFORMED: 'Sesi tidak sah. Silakan masuk kembali.',
    TOKEN_BAD_SIGNATURE: 'Sesi tidak sah. Silakan masuk kembali.',
    TOKEN_EXPIRED: 'Sesi sudah berakhir. Silakan masuk kembali.',
    TENANT_FORBIDDEN: 'Akun ini tidak berhak atas data tersebut.',
    TENANT_UNKNOWN: 'Tujuan data tidak dikenali.',
    ROLE_CHANGED: 'Peran akun berubah. Silakan masuk kembali.',
    ROW_NOT_FOUND: 'Baris tidak ditemukan. Data mungkin sudah berubah.',
    SHEET_ERROR: 'Sumber data gagal dibaca. Coba lagi sebentar lagi.'
  }
};

/* ============================================================================
 * RESOLUSI ALAMAT API
 *
 * Urutan: ?api=<url> di query string  >  localStorage  >  DEFAULT_API_URL.
 *
 * Kenapa ini butuh penjagaan: `?api=` bisa diisi siapa saja lewat tautan.
 * Dua pengaman dipasang.
 *
 *   a) Token disimpan per-origin API. Kunci penyimpanan ikut host tujuan, jadi
 *      token produksi secara fisik tidak bisa terkirim ke alamat lain — kalau
 *      alamat berganti, tidak ada token untuk dikirim dan pengguna harus masuk
 *      ulang di alamat itu. Ini yang membuat tautan `?api=` jahat tidak bisa
 *      memanen sesi yang sudah ada.
 *
 *   b) Alamat non-default di luar localhost/origin halaman sendiri tidak
 *      langsung dipakai — app.js meminta konfirmasi eksplisit lebih dulu, dan
 *      selama alamat aktif bukan default, header menampilkan banner mode uji
 *      berikut tombol "Kembali ke produksi".
 * ========================================================================== */
(function (cfg, global) {
  'use strict';

  function store() {
    try { return global.localStorage; } catch (e) { return null; }
  }

  function readStore(k) {
    var s = store();
    if (!s) return '';
    try { return s.getItem(k) || ''; } catch (e) { return ''; }
  }

  function writeStore(k, v) {
    var s = store();
    if (!s) return;
    try { v ? s.setItem(k, v) : s.removeItem(k); } catch (e) {}
  }

  /** Hanya http/https absolut yang diterima. Sisanya diabaikan diam-diam. */
  function parseUrl(raw) {
    if (!raw) return null;
    try {
      var u = new global.URL(String(raw), global.location ? global.location.href : undefined);
      if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
      return u;
    } catch (e) { return null; }
  }

  function originOf(raw) {
    var u = parseUrl(raw);
    return u ? u.origin : String(raw || '');
  }

  function hostOf(raw) {
    var u = parseUrl(raw);
    return u ? u.host : String(raw || '');
  }

  function isLocal(u) {
    if (!u) return false;
    var h = u.hostname;
    return h === 'localhost' || h === '127.0.0.1' || h === '::1' || h === '[::1]' ||
           /\.localhost$/.test(h);
  }

  function sameAsPage(u) {
    if (!u || !global.location) return false;
    return u.origin === global.location.origin;
  }

  function queryApi() {
    if (!global.location || !global.location.search) return '';
    try {
      return new global.URLSearchParams(global.location.search).get('api') || '';
    } catch (e) { return ''; }
  }

  var defaultUrl = cfg.DEFAULT_API_URL;
  var fromQuery = queryApi();
  var fromStore = readStore(cfg.STORAGE_API_URL);

  var resolution = { url: defaultUrl, source: 'default', pending: '', needsConfirm: false };

  if (fromQuery) {
    var qu = parseUrl(fromQuery);
    if (qu) {
      if (qu.href === defaultUrl || isLocal(qu) || sameAsPage(qu)) {
        resolution = { url: qu.href, source: 'query', pending: '', needsConfirm: false };
        writeStore(cfg.STORAGE_API_URL, qu.href === defaultUrl ? '' : qu.href);
      } else {
        // Origin asing: jangan dipakai sebelum pengguna menyetujui.
        resolution = {
          url: fromStore || defaultUrl,
          source: fromStore ? 'storage' : 'default',
          pending: qu.href,
          needsConfirm: true
        };
      }
    }
  } else if (fromStore) {
    var su = parseUrl(fromStore);
    if (su) resolution = { url: su.href, source: 'storage', pending: '', needsConfirm: false };
  }

  cfg.API_URL = resolution.url;
  cfg.API_RESOLUTION = resolution;

  /** true kalau alamat aktif bukan alamat produksi -> banner mode uji. */
  cfg.isTestEndpoint = function (url) {
    var u = url === undefined ? cfg.API_URL : url;
    return originOf(u) !== originOf(defaultUrl) || String(u) !== String(defaultUrl);
  };

  cfg.apiHost = function (url) {
    return hostOf(url === undefined ? cfg.API_URL : url);
  };

  /** Simpan & aktifkan alamat baru. Kosong = kembali ke produksi. */
  cfg.setApiUrl = function (url) {
    var u = url ? parseUrl(url) : null;
    var next = u ? u.href : defaultUrl;
    cfg.API_URL = next;
    writeStore(cfg.STORAGE_API_URL, next === defaultUrl ? '' : next);
    return next;
  };

  /**
   * Kunci token, di-namespace per origin API. Inilah pengaman utama terhadap
   * tautan `?api=` yang mencoba memanen token.
   */
  cfg.tokenKey = function (url) {
    var base = cfg.STORAGE_TOKEN;
    var o = originOf(url === undefined ? cfg.API_URL : url);
    if (o === originOf(defaultUrl)) return base;
    return base + '::' + o;
  };

}(VDConfig, typeof window !== 'undefined' ? window : this));

if (typeof module !== 'undefined' && module.exports) module.exports = VDConfig;
