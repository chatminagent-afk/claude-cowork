/* ============================================================================
 * app.js — CONTROLLER
 *
 * Menyimpan satu state, memanggil VDApi, meminta VDRender/VDCharts menggambar.
 * Tidak ada pengetahuan tentang tenant mana pun: setiap label, kolom, judul,
 * dan warna aksen dibaca dari respons server.
 *
 * Aturan rentang: ganti 7/30/90 TIDAK memanggil server. Payload `stats` sudah
 * memuat seluruh nilai untuk ketiga rentang, jadi pergantian hanya menghitung
 * ulang dari data yang sudah ada. Tidak ada polling, tidak ada auto-refresh —
 * kuota Google Sheets dipakai bersama bot produksi.
 *
 * Tambahan pada versi revamp:
 *   - Tema terang/gelap (blok `TEMA`), disimpan di localStorage.
 *   - Daftar lead berganti bentuk tabel <-> kartu mengikuti lebar layar.
 *   - Menu ringkas untuk tombol header di layar sempit.
 * ========================================================================== */
'use strict';

(function (global) {

  var cfg = global.VDConfig;
  var api = global.VDApi;
  var R = global.VDRender;
  var C = global.VDCharts;
  var T = cfg.TEXT;

  /* ------------------------------------------------------------- state -- */

  var state = {
    session: null,
    stats: null,
    range: cfg.DEFAULT_RANGE,
    q: '',
    botMode: 'all',
    sortKey: '',
    sortDir: 'desc',
    page: 1,
    busy: false,
    pendingToggles: 0,
    theme: 'dark',
    themeExplicit: false,   // true kalau pengguna sendiri yang memilih
    cardMode: false,        // true kalau daftar lead sedang berbentuk kartu
    sections: {},           // id -> true/false (terbuka/tertutup)
    hidden: {},             // id -> true berarti seksi disembunyikan
    addBusy: false,         // true selama permintaan add_lead berjalan
    highlightKey: '',       // key baris yang baru ditambahkan (sorotan sesaat)
    highlightTimer: null
  };

  /* ------------------------------------------------------------- shortcuts */

  function $(id) { return document.getElementById(id); }

  function on(el, ev, fn) { if (el) el.addEventListener(ev, fn); }

  function show(el, yes) { if (el) el.hidden = !yes; }

  /* =============================================================== TEMA === */

  /**
   * Urutan: pilihan tersimpan > preferensi sistem > DEFAULT_THEME.
   * Nilai `explicit` menandai apakah itu pilihan pengguna sendiri — hanya
   * pilihan eksplisit yang boleh mengunci tema dari perubahan sistem.
   */
  function readTheme() {
    try {
      var v = global.localStorage.getItem(cfg.STORAGE_THEME);
      if (v === 'light' || v === 'dark') return { theme: v, explicit: true };
    } catch (e) {}

    try {
      if (global.matchMedia) {
        if (global.matchMedia('(prefers-color-scheme: light)').matches) {
          return { theme: 'light', explicit: false };
        }
        if (global.matchMedia('(prefers-color-scheme: dark)').matches) {
          return { theme: 'dark', explicit: false };
        }
      }
    } catch (e) {}

    return { theme: cfg.DEFAULT_THEME === 'light' ? 'light' : 'dark', explicit: false };
  }

  /**
   * Terapkan tema.
   *
   * `persist` hanya true kalau pengguna menekan tombol — pemasangan awal dari
   * preferensi sistem tidak boleh ditulis, supaya sistem yang berubah nanti
   * (mis. jadwal gelap otomatis di ponsel) tetap diikuti.
   */
  function setTheme(theme, persist) {
    var t = theme === 'light' ? 'light' : 'dark';
    state.theme = t;
    document.documentElement.setAttribute('data-theme', t);

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', t === 'light' ? '#eef1f7' : '#05070e');

    paintThemeButtons();

    if (persist) {
      state.themeExplicit = true;
      try { global.localStorage.setItem(cfg.STORAGE_THEME, t); } catch (e) {}
    }

    // Warna garis/bar chart adalah atribut SVG, bukan CSS — harus digambar
    // ulang supaya ikut berganti. Gridline & sumbu sudah lewat CSS.
    if (state.stats) {
      paintCharts();
      applyAccent((state.stats.tenant || {}).accent);
    }
  }

  function toggleTheme() {
    setTheme(state.theme === 'light' ? 'dark' : 'light', true);
  }

  /** Isi kedua tombol tema dengan ikon matahari + bulan dan label yang benar. */
  function paintThemeButtons() {
    var label = state.theme === 'light' ? T.themeToDark : T.themeToLight;
    var ids = ['themeToggle', 'themeToggleLogin'];
    for (var i = 0; i < ids.length; i++) {
      var btn = $(ids[i]);
      if (!btn) continue;
      if (!btn.firstChild) {
        var sun = R.icon('sun');
        var moon = R.icon('moon');
        if (sun) { sun.setAttribute('class', 'ic-sun'); btn.appendChild(sun); }
        if (moon) { moon.setAttribute('class', 'ic-moon'); btn.appendChild(moon); }
      }
      btn.setAttribute('aria-label', label);
      btn.title = label;
    }
  }

  function watchSystemTheme() {
    if (!global.matchMedia) return;
    var mq;
    try { mq = global.matchMedia('(prefers-color-scheme: light)'); } catch (e) { return; }
    var handler = function (ev) {
      // Pilihan eksplisit pengguna selalu menang atas preferensi sistem.
      if (state.themeExplicit) return;
      setTheme(ev.matches ? 'light' : 'dark', false);
    };
    if (mq.addEventListener) mq.addEventListener('change', handler);
    else if (mq.addListener) mq.addListener(handler);
  }

  /* ====================================================== SEKSI & KURASI == */

  /**
   * Pengaturan seksi disimpan per tenant. Dua klien punya susunan KPI, chart,
   * dan tabel yang sama sekali berbeda; kalau kuncinya dipakai bersama,
   * menyembunyikan "Slot Mock Interview" di satu klien akan ikut mematikan
   * seksi lain yang kebetulan seindeks di klien berikutnya.
   */
  function tenantKey(base) {
    var id = (state.stats && state.stats.tenant && state.stats.tenant.id) ||
             (state.session && state.session.tenant) || '';
    return base + '::' + id;
  }

  function readMap(base) {
    try {
      var raw = global.localStorage.getItem(tenantKey(base));
      if (!raw) return {};
      var v = JSON.parse(raw);
      return v && typeof v === 'object' ? v : {};
    } catch (e) { return {}; }
  }

  function writeMap(base, map) {
    try {
      global.localStorage.setItem(tenantKey(base), JSON.stringify(map || {}));
    } catch (e) {}
  }

  function loadSectionPrefs() {
    state.sections = readMap(cfg.STORAGE_SECTIONS);
    state.hidden = readMap(cfg.STORAGE_HIDDEN);
  }

  /**
   * Terbuka atau tidak.
   *
   * Tanpa pilihan tersimpan, bawaannya terbuka — KECUALI seksi yang isinya
   * memang kosong. Kotak "belum ada data" setinggi 80px yang selalu terbuka
   * hanya memakan layar tanpa memberi tahu apa pun yang tidak sudah terbaca
   * dari judulnya.
   */
  function isExpanded(id, isEmpty) {
    if (Object.prototype.hasOwnProperty.call(state.sections, id)) return !!state.sections[id];
    return !isEmpty;
  }

  function setExpanded(id, expanded) {
    state.sections[id] = !!expanded;
    writeMap(cfg.STORAGE_SECTIONS, state.sections);
  }

  function isHidden(id) { return state.hidden[id] === true; }

  function setHidden(id, hidden) {
    if (hidden) state.hidden[id] = true;
    else delete state.hidden[id];
    writeMap(cfg.STORAGE_HIDDEN, state.hidden);
  }

  /** Kait yang dioper ke renderer supaya seksi tahu cara melapor balik. */
  function sectionHooks(id, isEmpty) {
    return {
      expanded: isExpanded(id, isEmpty),
      onToggle: setExpanded,
      onHint: showHint
    };
  }

  /* --------------------------------------------------- lembar penjelasan -- */

  /**
   * Bulatan "i" dulu hanya `title` — dan `title` tidak pernah muncul di layar
   * sentuh. Di ponsel, penjelasan KPI praktis tidak bisa dibaca sama sekali.
   * Sekarang setiap "i" membuka lembar ini.
   */
  function showHint(title, text) {
    var overlay = $('hintOverlay');
    if (!overlay) return;
    $('hintTitle').textContent = String(title || '');
    $('hintBody').textContent = String(text || '');
    overlay.classList.add('open');
    $('hintClose').focus();
  }

  function closeHint() {
    var overlay = $('hintOverlay');
    if (overlay) overlay.classList.remove('open');
  }

  /* ------------------------------------------------------------- overlay -- */

  function loader(yes, text) {
    var box = $('loader');
    if (text) $('loaderText').textContent = text;
    box.classList.toggle('open', !!yes);
  }

  function toast(message, kind) {
    var wrap = $('toasts');
    var t = document.createElement('div');
    t.className = 'toast ' + (kind || 'info');
    t.textContent = String(message || '');
    wrap.appendChild(t);
    global.setTimeout(function () {
      t.style.opacity = '0';
      t.style.transform = 'translateY(8px)';
      global.setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 220);
    }, kind === 'err' ? 5200 : 3200);
  }

  /** Modal konfirmasi generik. Mengembalikan Promise<boolean>. */
  function confirmBox(opts) {
    return new Promise(function (resolve) {
      var overlay = $('modalOverlay');
      $('modalTitle').textContent = opts.title || '';

      var body = $('modalBody');
      R.clear(body);
      body.appendChild(document.createTextNode(opts.body || ''));
      if (opts.target) {
        var t = R.elem('span', 'modal-target', opts.target);
        body.appendChild(t);
      }

      var ok = $('modalOk');
      var cancel = $('modalCancel');
      ok.textContent = opts.okText || 'Lanjutkan';
      cancel.textContent = opts.cancelText || 'Batal';
      ok.className = 'btn' + (opts.danger ? ' btn-danger' : '');

      function done(v) {
        overlay.classList.remove('open');
        ok.removeEventListener('click', onOk);
        cancel.removeEventListener('click', onCancel);
        overlay.removeEventListener('click', onBackdrop);
        document.removeEventListener('keydown', onKey);
        resolve(v);
      }
      function onOk() { done(true); }
      function onCancel() { done(false); }
      function onBackdrop(ev) { if (ev.target === overlay) done(false); }
      function onKey(ev) { if (ev.key === 'Escape') done(false); }

      ok.addEventListener('click', onOk);
      cancel.addEventListener('click', onCancel);
      overlay.addEventListener('click', onBackdrop);
      document.addEventListener('keydown', onKey);

      overlay.classList.add('open');
      ok.focus();
    });
  }

  /* --------------------------------------------------------- banner API -- */

  function paintApiBanner() {
    var banner = $('apiBanner');
    var isTest = cfg.isTestEndpoint();
    show(banner, isTest);
    document.body.classList.toggle('has-test-banner', isTest);
    if (isTest) {
      $('apiBannerText').textContent = T.testModePrefix + ' ' + cfg.apiHost();
      $('apiBannerReset').textContent = T.testModeReset;
      measureBanner();
    } else {
      document.body.style.removeProperty('--test-banner-h');
    }
  }

  /**
   * Beri tahu CSS setinggi apa banner sekarang, supaya header menempel tepat
   * di bawahnya. Teks banner membungkus jadi beberapa baris di layar sempit,
   * jadi tingginya tidak bisa dipatok di CSS.
   */
  function measureBanner() {
    var banner = $('apiBanner');
    if (!banner || banner.hidden) return;
    var h = banner.offsetHeight;
    if (h > 0) document.body.style.setProperty('--test-banner-h', h + 'px');
  }

  /**
   * Satu pengukuran saja tidak cukup: saat boot, lebar dan metrik font belum
   * tentu final, jadi tinggi yang tercatat bisa milik tata letak sementara —
   * dan header akan terdorong terlalu jauh ke bawah sampai ada resize.
   * ResizeObserver membuat nilai itu selalu mengikuti tinggi banner yang nyata.
   */
  function watchBannerHeight() {
    var banner = $('apiBanner');
    if (!banner) return;

    if (typeof global.ResizeObserver === 'function') {
      try {
        new global.ResizeObserver(measureBanner).observe(banner);
        return;
      } catch (e) { /* jatuh ke cadangan di bawah */ }
    }
    // Cadangan untuk mesin tanpa ResizeObserver.
    global.addEventListener('load', measureBanner);
    global.setTimeout(measureBanner, 300);
  }

  /**
   * `?api=` yang menunjuk origin asing tidak langsung dipakai. Tautan seperti
   * itu bisa dikirim siapa saja; menyetujuinya berarti memindahkan seluruh sesi
   * ke server orang lain.
   */
  function resolveEndpoint() {
    var res = cfg.API_RESOLUTION || {};
    api.setBaseUrl(cfg.API_URL);
    if (!res.needsConfirm || !res.pending) return Promise.resolve();

    return confirmBox({
      title: T.apiConfirmTitle,
      body: T.apiConfirmBody,
      target: res.pending,
      okText: T.apiConfirmOk,
      cancelText: T.apiConfirmCancel,
      danger: true
    }).then(function (yes) {
      if (yes) {
        cfg.setApiUrl(res.pending);
        api.setBaseUrl(cfg.API_URL);
      }
      paintApiBanner();
    });
  }

  /* ------------------------------------------------------------- layar --- */

  function showLogin(message) {
    state.session = null;
    state.stats = null;
    closeMenu();
    closeViewPanel();
    closeHint();
    closeDrawer();
    show($('screenApp'), false);
    show($('screenLogin'), true);
    var err = $('loginError');
    if (message) { err.textContent = message; show(err, true); }
    else { err.textContent = ''; show(err, false); }
    $('loginPass').value = '';
    setPassVisible(false);
    loader(false);
  }

  function showApp() {
    show($('screenLogin'), false);
    show($('screenApp'), true);
  }

  function logout(reason) {
    api.clearToken();
    showLogin(reason || '');
    if (reason) toast(reason, 'err');
  }

  /**
   * Titik tunggal penanganan respons gagal. Error sesi -> keluar otomatis.
   * Mengembalikan true kalau respons sehat.
   */
  function guard(res) {
    if (res && res.ok) return true;
    var code = res ? res.error : '';
    var msg = (res && res.message) || T.unknown;
    if (api.isAuthError(code)) { logout(msg); return false; }
    return false;
  }

  /* ------------------------------------------------------------- login --- */

  function setPassVisible(yes) {
    var input = $('loginPass');
    var btn = $('passToggle');
    if (!input || !btn) return;
    input.type = yes ? 'text' : 'password';
    R.clear(btn);
    R.withIcon(btn, yes ? 'eyeOff' : 'eye');
    var label = yes ? T.hidePass : T.showPass;
    btn.setAttribute('aria-label', label);
    btn.title = label;
  }

  function doLogin(ev) {
    if (ev) ev.preventDefault();
    if (state.busy) return;

    var u = $('loginUser').value.trim();
    var p = $('loginPass').value;
    var err = $('loginError');

    if (!u || !p) {
      err.textContent = T.loginEmpty;
      show(err, true);
      return;
    }

    var btn = $('loginBtn');
    state.busy = true;
    btn.disabled = true;
    btn.textContent = T.loginBusy;
    show(err, false);

    api.call('login', { username: u, password: p }).then(function (res) {
      state.busy = false;
      btn.disabled = false;
      btn.textContent = T.loginSubmit || 'Masuk';

      if (!res.ok) {
        err.textContent = res.message || T.unknown;
        show(err, true);
        return;
      }
      if (res.token) api.setToken(res.token);
      state.session = res.session || null;
      showApp();
      paintSession();
      loadStats(false);
    });
  }

  /* ------------------------------------------------------------- sesi ---- */

  function paintSession() {
    var s = state.session || {};
    $('metaUser').textContent = s.display || s.username || '';

    var sel = $('tenantSelect');
    var list = s.tenants || [];
    R.clear(sel);

    // Pemilih hanya muncul kalau akun benar-benar punya lebih dari satu tenant.
    if (list.length > 1) {
      for (var i = 0; i < list.length; i++) {
        var o = document.createElement('option');
        o.value = list[i].id;
        o.textContent = list[i].name || list[i].id;
        if (list[i].id === s.tenant) o.selected = true;
        sel.appendChild(o);
      }
      show(sel, true);
    } else {
      show(sel, false);
    }
  }

  function resetBotFilter() {
    state.botMode = 'all';
    var all = $('botFilter').querySelectorAll('.seg-btn');
    for (var i = 0; i < all.length; i++) {
      all[i].classList.toggle('active', all[i].getAttribute('data-mode') === 'all');
    }
  }

  function switchTenant(id) {
    if (!id || state.busy) return;
    loader(true, T.loading);
    state.busy = true;
    api.call('switch_tenant', { tenant: id }).then(function (res) {
      state.busy = false;
      if (!guard(res)) { loader(false); if (!api.isAuthError(res.error)) toast(res.message, 'err'); paintSession(); return; }
      if (res.token) api.setToken(res.token);
      state.session = res.session || state.session;
      // Tenant lain punya kolom lain: pencarian, urutan, dan saringan direset
      // supaya tidak mengurutkan berdasarkan kolom yang tidak ada di sana.
      state.page = 1;
      state.q = '';
      state.sortKey = '';
      state.sortDir = 'desc';
      resetBotFilter();
      $('leadSearch').value = '';
      syncSearchClear();
      paintSession();
      loadStats(false);
    });
  }

  /* ------------------------------------------------------------- stats --- */

  function loadStats(fresh) {
    if (state.busy) return;
    state.busy = true;
    loader(true, fresh ? T.refreshing : T.loading);
    setRefreshDisabled(true);

    api.call('stats', { fresh: !!fresh }).then(function (res) {
      state.busy = false;
      setRefreshDisabled(false);
      loader(false);

      if (!guard(res)) {
        if (!api.isAuthError(res.error)) toast(res.message || T.unknown, 'err');
        return;
      }
      state.stats = res;
      state.page = 1;
      // Preferensi seksi di-namespace per tenant, jadi baru bisa dibaca
      // setelah tahu tenant mana yang sedang dilihat.
      loadSectionPrefs();
      paintAll();
      if (fresh) toast(T.refreshed, 'ok');
    });
  }

  function setRefreshDisabled(yes) {
    var a = $('btnRefresh');
    var b = $('menuRefresh');
    if (a) a.disabled = !!yes;
    if (b) b.disabled = !!yes;
  }

  /* ---------------------------------------------------------- menggambar -- */

  function applyAccent(tone) {
    var hex = C.toneHex(tone);
    document.documentElement.style.setProperty('--accent', hex);
  }

  function paintAll() {
    var s = state.stats;
    if (!s) return;

    var tenant = s.tenant || {};
    applyAccent(tenant.accent);
    $('tenantName').textContent = tenant.name || '';
    $('tenantProduct').textContent = tenant.product || '';
    R.brandLogo($('brandLogo'), tenant);

    $('metaTime').textContent = R.fmtDateTime(s.generated_at);
    show($('metaCached'), !!s.cached);

    paintRangeBar();
    paintKpis();
    paintCharts();
    paintInsights();
    paintLeads();
    paintTables();
  }

  /* --------------------------------------------------------- kurasi kartu */

  /** Buang seksi yang disembunyikan pengguna. `prefix` menentukan ruang id. */
  function visible(list, prefix) {
    var out = [];
    var arr = list || [];
    for (var i = 0; i < arr.length; i++) {
      var id = prefix + (arr[i].id || arr[i].title || i);
      if (!isHidden(id)) out.push(arr[i]);
    }
    return out;
  }

  /** true kalau seluruh angka chart nol / tidak ada data sama sekali. */
  function chartIsEmpty(chart) {
    if (!chart) return true;
    if (chart.empty === true) return true;
    var sliced = R.sliceChart(chart, state.range);
    return C.isEmptyData(sliced.series || []);
  }

  function paintKpis() {
    var s = state.stats || {};
    R.kpiGrid($('kpiGrid'), visible(s.kpis, 'kpi:'), state.range, showHint);
  }

  function paintCharts() {
    var s = state.stats || {};
    var list = visible(s.charts, 'chart:');
    var host = $('chartGrid');
    R.clear(host);
    for (var i = 0; i < list.length; i++) {
      var chart = list[i];
      var id = 'chart:' + (chart.id || chart.title || i);
      var card = R.chartCard(chart, state.range, sectionHooks(id, chartIsEmpty(chart)));
      host.appendChild(R.reveal(card));
      // Digambar sekarang supaya lebarnya nyata; animasinya sendiri ditahan
      // charts.js sampai kartu tergulung ke dalam layar.
      card._vdDraw();
    }
  }

  function paintRangeBar() {
    var bar = $('rangeBar');
    R.clear(bar);
    bar.appendChild(R.elem('span', 'range-label', 'Rentang'));
    var ranges = cfg.RANGES || [7, 30, 90];
    for (var i = 0; i < ranges.length; i++) {
      (function (r) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'pill' + (r === state.range ? ' active' : '');
        b.textContent = r + ' hari';
        b.setAttribute('aria-pressed', r === state.range ? 'true' : 'false');
        b.addEventListener('click', function () { setRange(r); });
        bar.appendChild(b);
      }(ranges[i]));
    }
  }

  /** Ganti rentang: murni perhitungan ulang di klien. Tidak ada request. */
  function setRange(r) {
    if (r === state.range) return;
    state.range = r;
    try { global.localStorage.setItem(cfg.STORAGE_RANGE, String(r)); } catch (e) {}
    paintRangeBar();
    paintKpis();
    paintCharts();
  }

  /* -------------------------------------------------------------- leads -- */

  function leadView() {
    var leads = (state.stats && state.stats.leads) || {};
    var rows = leads.rows || [];
    var filtered = R.filterLeads(rows, { q: state.q, botMode: state.botMode });
    if (state.sortKey) filtered = R.sortLeads(filtered, state.sortKey, state.sortDir);
    return { leads: leads, filtered: filtered, page: R.paginate(filtered, state.page, cfg.PAGE_SIZE) };
  }

  /** true kalau viewport cukup sempit sehingga daftar lead lebih baik jadi kartu. */
  function wantsCards() {
    var bp = typeof cfg.CARD_BREAKPOINT === 'number' ? cfg.CARD_BREAKPOINT : 720;
    return (global.innerWidth || 1024) < bp;
  }

  /**
   * Isi pemilih urutan (hanya relevan di tampilan kartu — di tabel, kepala
   * kolom yang jadi kontrolnya). Dibangun dari definisi kolom server.
   */
  function paintSortSelect(columns) {
    var sel = $('sortSelect');
    if (!sel) return;
    R.clear(sel);

    var opt0 = document.createElement('option');
    opt0.value = '';
    opt0.textContent = (T.sortLabel || 'Urutkan') + ': bawaan';
    sel.appendChild(opt0);

    var cols = columns || [];
    for (var i = 0; i < cols.length; i++) {
      var c = cols[i];
      if (String(c.type || '').toLowerCase() === 'toggle') continue;
      var label = c.label || c.key;
      var dirs = [['asc', '↑'], ['desc', '↓']];
      for (var d = 0; d < dirs.length; d++) {
        var o = document.createElement('option');
        o.value = c.key + '|' + dirs[d][0];
        o.textContent = label + ' ' + dirs[d][1];
        if (state.sortKey === c.key && state.sortDir === dirs[d][0]) o.selected = true;
        sel.appendChild(o);
      }
    }
  }

  /**
   * Kepala seksi Direktori Lead. Markup-nya statis di index.html (isinya
   * punya toolbar dan pager sendiri, tidak dibangun ulang tiap render), jadi
   * pelipatannya dipasang di sini alih-alih lewat R.sectionHead.
   */
  function paintLeadsHead(leads) {
    var toggle = $('leadsToggle');
    var body = $('leadsBody');
    var card = $('leadsCard');
    var info = $('leadsInfo');
    if (!toggle || !body) return;

    var expanded = isExpanded('leads', !((leads.rows || []).length));

    function apply(next) {
      expanded = !!next;
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      body.hidden = !expanded;
      card.classList.toggle('is-collapsed', !expanded);
    }
    apply(expanded);

    if (!toggle._vdBound) {
      toggle._vdBound = true;
      toggle.addEventListener('click', function () {
        apply(!expanded);
        setExpanded('leads', expanded);
      });
    }

    // Penjelasan hanya muncul kalau server mengirimnya.
    var hint = String(leads.hint || '');
    show(info, hint !== '');
    if (hint !== '') {
      info.title = hint;
      info.setAttribute('aria-label', 'Penjelasan: ' + (leads.title || ''));
      if (!info._vdBound) {
        info._vdBound = true;
        info.addEventListener('click', function (ev) {
          ev.stopPropagation();
          showHint($('leadsTitle').textContent, info.title);
        });
      }
    }
  }

  function paintLeads() {
    var leads = (state.stats && state.stats.leads) || null;
    var card = $('leadsCard');
    if (!leads || !leads.columns || !leads.columns.length || isHidden('leads')) {
      show(card, false);
      return;
    }
    show(card, true);
    $('leadsTitle').textContent = leads.title || '';
    paintLeadsHead(leads);

    var view = leadView();
    state.page = view.page.page;

    $('leadsCount').textContent = R.fmtInt(view.filtered.length) + ' dari ' +
                                  R.fmtInt((leads.rows || []).length);

    state.cardMode = wantsCards();
    show($('sortWrap'), state.cardMode);
    if (state.cardMode) paintSortSelect(leads.columns);

    var handlers = {
      onSort: function (key) {
        if (state.sortKey === key) state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
        else { state.sortKey = key; state.sortDir = 'asc'; }
        state.page = 1;
        paintLeads();
      },
      onRow: openDrawer,
      onToggle: askToggle,
      highlightKey: state.highlightKey
    };

    var wrap = $('leadTableWrap');
    R.clear(wrap);
    wrap.classList.toggle('is-cards', state.cardMode);

    if (state.cardMode) {
      wrap.appendChild(R.leadCards(leads.columns, view.page.rows, handlers));
    } else {
      wrap.appendChild(R.leadTable(
        leads.columns,
        view.page.rows,
        { sortKey: state.sortKey, sortDir: state.sortDir },
        handlers
      ));
    }

    var p = view.page;
    $('pagerInfo').textContent = p.total === 0
      ? T.emptyLeads
      : 'Baris ' + R.fmtInt(p.start) + '–' + R.fmtInt(p.end) + ' dari ' + R.fmtInt(p.total) +
        ' · halaman ' + p.page + '/' + p.pages;
    $('pagePrev').disabled = p.page <= 1;
    $('pageNext').disabled = p.page >= p.pages;
  }

  /* ---------------------------------------------------------- rekomendasi -- */

  /**
   * Kartu rekomendasi AI.
   *
   * Server hanya mengirim blok `insights` kalau ada isinya — kalau panggilan
   * AI gagal, atau ringkasan bulanan belum ada, kuncinya tidak muncul sama
   * sekali dan bagian ini kosong tanpa kotak "belum ada data" yang percuma.
   */
  function paintInsights() {
    var host = $('insightsWrap');
    R.clear(host);
    var list = visible((state.stats && state.stats.insights) || [], 'insight:');
    for (var i = 0; i < list.length; i++) {
      var spec = list[i];
      var id = 'insight:' + (spec.id || spec.title || i);
      host.appendChild(R.insightCard(spec, sectionHooks(id, !(spec.items || []).length)));
    }
  }

  /* ------------------------------------------------------------- tables -- */

  function paintTables() {
    var host = $('tablesWrap');
    R.clear(host);
    var list = visible((state.stats && state.stats.tables) || [], 'table:');
    for (var i = 0; i < list.length; i++) {
      var spec = list[i];
      var id = 'table:' + (spec.id || spec.title || i);
      var empty = !(spec.rows || []).length;
      host.appendChild(R.simpleTable(spec, sectionHooks(id, empty)));
    }
  }

  /* ------------------------------------------------------------- drawer -- */

  function openDrawer(row) {
    var overlay = $('drawerOverlay');
    $('drawerTitle').textContent = (row && row.nama) || (row && row.key) || T.detailTitle;

    var sub = [];
    if (row && row.wa) sub.push(row.wa);
    else if (row && row.lid) sub.push(row.lid);
    if (row && row.is_lid) sub.push(T.lidBadge);
    $('drawerSub').textContent = sub.join(' · ');

    var body = $('drawerBody');
    R.clear(body);
    body.appendChild(R.detailList(row));

    overlay.classList.add('open');
    $('drawerClose').focus();
  }

  function closeDrawer() {
    $('drawerOverlay').classList.remove('open');
  }

  /* ------------------------------------------------------------- toggle -- */

  /**
   * Mematikan bot berarti percakapan produksi berhenti dibalas otomatis.
   * Karena itu konfirmasi datang lebih dulu, baru optimistic update.
   */
  function askToggle(row, next, sw) {
    if (sw.disabled) return;
    var name = (row && row.nama) || '';
    var id = (row && row.wa) || (row && row.lid) || (row && row.key) || '';

    confirmBox({
      title: T.toggleConfirmTitle,
      body: next === 'OFF' ? T.toggleOff : T.toggleOn,
      target: (name ? name + ' · ' : '') + id,
      okText: T.toggleOk,
      cancelText: T.toggleCancel,
      danger: next === 'OFF'
    }).then(function (yes) {
      if (yes) doToggle(row, next, sw);
    });
  }

  function doToggle(row, next, sw) {
    var previous = row.bot_mode;

    // Optimistic: switch langsung pindah, dikunci sampai server menjawab.
    R.setSwitch(sw, next);
    sw.disabled = true;
    row.bot_mode = next;
    state.pendingToggles++;

    api.call('toggle_user', { key: row.key, mode: next }).then(function (res) {
      state.pendingToggles--;
      sw.disabled = false;

      if (!res.ok) {
        // Kembalikan ke posisi semula — server yang memegang kebenaran.
        row.bot_mode = previous;
        R.setSwitch(sw, previous);
        if (!guard(res)) {
          if (!api.isAuthError(res.error)) toast(res.message || T.unknown, 'err');
        }
        return;
      }

      var confirmed = res.bot_mode || next;
      row.bot_mode = confirmed;
      R.setSwitch(sw, confirmed);
      toast(res.message || 'Status bot diperbarui.', 'ok');

      // Saring "bot aktif/manual" bisa jadi tidak lagi cocok dengan baris ini.
      if (state.botMode !== 'all') paintLeads();
    });
  }

  /* --------------------------------------------------------- tambah lead -- */

  /**
   * Normalisasi nomor sisi klien.
   *
   * Ini KEMBARAN dari vdNormalizeWa() di n8n/src/build-payload.js dan sengaja
   * dibuat sama persis, termasuk batas 9–12 digit untuk aturan "8 di depan".
   * Server tetap yang berwenang: nilai yang disimpan adalah hasil normalisasi
   * server, bukan hasil fungsi ini. Fungsi ini hanya supaya tombol Tambahkan
   * bisa mati/hidup saat diketik, alih-alih menunggu perjalanan ke server
   * untuk memberi tahu bahwa nomornya kurang satu digit.
   */
  function normalizeWa(raw) {
    var d = String(raw === null || raw === undefined ? '' : raw).replace(/\D/g, '');
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

  var addBotOn = false;

  function paintAddForm() {
    var sw = $('addBot');
    var warn = $('addWarn');
    sw.classList.toggle('on', addBotOn);
    sw.setAttribute('aria-checked', addBotOn ? 'true' : 'false');
    show(warn, addBotOn);

    var valid = normalizeWa($('addWa').value) !== '';
    $('addSubmit').disabled = !valid || state.addBusy === true;
  }

  function openAddLead() {
    if (!state.stats) return;
    closeMenu();

    $('addWa').value = '';
    $('addNama').value = '';
    // Selalu kembali ke OFF setiap kali dibuka. Nilai lengket akan membuat
    // penambahan berikutnya diam-diam mewarisi pilihan berisiko sebelumnya.
    addBotOn = false;
    state.addBusy = false;
    $('addSubmit').textContent = T.addSubmit;
    paintAddForm();

    $('addOverlay').classList.add('open');
    $('addWa').focus();
  }

  function closeAddLead() {
    if (state.addBusy) return;   // jangan tutup sementara tulis sedang berjalan
    $('addOverlay').classList.remove('open');
  }

  /**
   * Setelah baris masuk, pandangan direset supaya baris itu PASTI terlihat:
   * pencarian dikosongkan, saringan dikembalikan ke Semua, urutan ke bawaan,
   * halaman ke 1. Tanpa ini, menambah nomor dengan bot OFF sementara saringan
   * sedang di "Bot aktif" akan menampilkan notifikasi berhasil di atas tabel
   * yang tidak berubah sama sekali.
   */
  function revealNewLead(row) {
    state.q = '';
    $('leadSearch').value = '';
    syncSearchClear();   // tombol silang dikendalikan class .has-value, bukan [hidden]

    state.botMode = 'all';
    var segs = $('botFilter').querySelectorAll('.seg-btn');
    for (var i = 0; i < segs.length; i++) {
      segs[i].classList.toggle('active', segs[i].getAttribute('data-mode') === 'all');
    }

    state.sortKey = '';
    state.sortDir = 'desc';
    state.page = 1;
    state.highlightKey = row && row.key ? String(row.key) : '';

    paintLeads();

    // Sorotan dilepas setelah animasinya selesai supaya render berikutnya
    // (ganti halaman, cari, ubah ukuran layar) tidak menyalakannya lagi.
    if (state.highlightTimer) global.clearTimeout(state.highlightTimer);
    state.highlightTimer = global.setTimeout(function () {
      state.highlightKey = '';
    }, 2800);
  }

  function submitAddLead(ev) {
    if (ev) ev.preventDefault();
    if (state.addBusy) return;

    var wa = normalizeWa($('addWa').value);
    if (wa === '') { toast(T.addInvalid, 'err'); $('addWa').focus(); return; }

    var nama = String($('addNama').value || '').trim();
    var mode = addBotOn ? 'ON' : 'OFF';

    state.addBusy = true;
    $('addSubmit').disabled = true;
    $('addSubmit').textContent = T.addBusy;

    api.call('add_lead', { key: wa, nama: nama, mode: mode }).then(function (res) {
      state.addBusy = false;
      $('addSubmit').textContent = T.addSubmit;
      paintAddForm();

      if (!res.ok) {
        // Form sengaja dibiarkan terbuka dengan isian utuh: kegagalan di sini
        // hampir selalu bisa diperbaiki di tempat (nomor duplikat, salah ketik),
        // dan mengetik ulang nomor 13 digit adalah hukuman yang tidak perlu.
        if (!guard(res)) {
          if (!api.isAuthError(res.error)) toast(res.message || T.unknown, 'err');
        }
        return;
      }

      $('addOverlay').classList.remove('open');
      toast(res.message || T.addDone, 'ok');

      var row = res.row;
      if (row && state.stats && state.stats.leads) {
        var rows = state.stats.leads.rows || (state.stats.leads.rows = []);
        rows.unshift(row);
        revealNewLead(row);
      } else {
        // Server tidak mengirim barisnya — lebih baik muat ulang daripada
        // menampilkan tabel yang tidak memuat nomor yang barusan ditambahkan.
        loadStats(false);
      }
    });
  }

  /* ------------------------------------------------------- atur tampilan -- */

  /**
   * Panel kurasi.
   *
   * Isinya dibangun sepenuhnya dari apa yang dikirim server untuk tenant yang
   * sedang aktif — tidak ada satu pun judul KPI, chart, atau tabel yang
   * ditulis di kode. Konsekuensinya, klien ketiga yang ditambahkan nanti
   * langsung punya panel yang benar tanpa frontend disentuh.
   */
  function buildViewPanel() {
    var host = $('viewBody');
    var s = state.stats || {};
    R.clear(host);

    function group(title, items, prefix, emptyOf) {
      if (!items || !items.length) return;
      var box = R.elem('div', 'view-group');
      box.appendChild(R.elem('div', 'view-group-title', title));

      for (var i = 0; i < items.length; i++) {
        (function (item, idx) {
          var id = prefix + (item.id || item.title || item.label || idx);
          var row = R.elem('div', 'view-row');
          var text = R.elem('div', 'view-row-text');
          text.appendChild(R.elem('div', 'view-row-label',
                                  item.label || item.title || item.id || ''));

          var notes = [];
          if (emptyOf && emptyOf(item)) notes.push(T.viewEmptyNote);
          if (notes.length) text.appendChild(R.elem('div', 'view-row-note', notes.join(' · ')));
          row.appendChild(text);

          var sw = document.createElement('button');
          sw.type = 'button';
          sw.className = 'ios-switch';
          sw.setAttribute('role', 'switch');
          sw.appendChild(R.elem('span', 'ios-knob'));

          function paint() {
            var on = !isHidden(id);
            sw.classList.toggle('on', on);
            sw.setAttribute('aria-checked', on ? 'true' : 'false');
            sw.setAttribute('aria-label', (item.label || item.title || '') +
                                          (on ? ' ditampilkan' : ' disembunyikan'));
            row.classList.toggle('is-off', !on);
          }
          paint();

          sw.addEventListener('click', function () {
            setHidden(id, !isHidden(id));
            paint();
            paintAll();          // panel tetap terbuka; isi di belakangnya ikut berubah
          });

          row.appendChild(sw);
          box.appendChild(row);
        }(items[i], i));
      }
      host.appendChild(box);
    }

    var leads = s.leads;
    if (leads && leads.columns && leads.columns.length) {
      // Prefix kosong + id 'leads' supaya kuncinya persis sama dengan yang
      // dipakai paintLeads/isHidden. Kalau prefix dipakai, judul tenant ikut
      // masuk ke kunci dan pengaturannya hilang begitu judulnya berubah.
      group(T.viewGroupLeads, [{ id: 'leads', title: leads.title || 'Direktori' }], '',
            function () { return !((leads.rows || []).length); });
    }
    group(T.viewGroupKpi, s.kpis, 'kpi:', function (k) {
      return Number(R.kpiValue(k, state.range)) === 0;
    });
    group(T.viewGroupChart, s.charts, 'chart:', chartIsEmpty);
    group(T.viewGroupInsight, s.insights, 'insight:', function (b) {
      return !((b.items || []).length);
    });
    group(T.viewGroupTable, s.tables, 'table:', function (t) {
      return !((t.rows || []).length);
    });
  }

  function openViewPanel() {
    if (!state.stats) return;
    buildViewPanel();
    $('viewOverlay').classList.add('open');
    $('viewClose').focus();
  }

  function closeViewPanel() {
    $('viewOverlay').classList.remove('open');
  }

  function resetView() {
    state.hidden = {};
    writeMap(cfg.STORAGE_HIDDEN, state.hidden);
    buildViewPanel();
    paintAll();
    toast(T.viewSaved, 'ok');
  }

  /* --------------------------------------------------------------- menu -- */

  function openMenu() {
    var pop = $('menuPop');
    if (!pop) return;
    pop.classList.add('open');
    $('menuBtn').setAttribute('aria-expanded', 'true');
  }

  function closeMenu() {
    var pop = $('menuPop');
    if (!pop) return;
    pop.classList.remove('open');
    var btn = $('menuBtn');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }

  function toggleMenu() {
    var pop = $('menuPop');
    if (!pop) return;
    if (pop.classList.contains('open')) closeMenu(); else openMenu();
  }

  /* ------------------------------------------------------------ search -- */

  function syncSearchClear() {
    var wrap = $('searchWrap');
    var input = $('leadSearch');
    if (wrap && input) wrap.classList.toggle('has-value', input.value !== '');
  }

  /* ------------------------------------------------------------- ikon --- */

  /** Sisipkan ikon SEBELUM teks yang sudah ada di markup. */
  function prependIcon(id, name) {
    var el = $(id);
    if (!el) return;
    var ic = R.icon(name);
    if (ic) el.insertBefore(ic, el.firstChild);
  }

  /** Pasang ikon inline ke tombol-tombol statis sekali saat boot. */
  function paintIcons() {
    R.withIcon($('searchIcon'), 'search');
    R.withIcon($('drawerClose'), 'close');
    R.withIcon($('viewClose'), 'close');
    R.withIcon($('menuBtn'), 'dots');
    R.withIcon($('leadsCaret'), 'chevron');

    prependIcon('btnRefresh', 'refresh');
    prependIcon('btnLogout', 'logout');
    prependIcon('menuRefresh', 'refresh');
    prependIcon('menuView', 'sliders');
    prependIcon('menuLogout', 'logout');

    R.withIcon($('addClose'), 'close');

    // Teks drawer tambah lead diambil dari config, bukan ditulis di markup,
    // supaya semua kalimat produk tinggal di satu tempat.
    $('addTitle').textContent = T.addTitle;
    $('addSub').textContent = T.addSub;
    $('addWaLabel').textContent = T.addWaLabel;
    $('addWa').placeholder = T.addWaPlaceholder;
    $('addWaHelp').textContent = T.addWaHelp;
    $('addNamaLabel').textContent = T.addNamaLabel;
    $('addNama').placeholder = T.addNamaPlaceholder;
    $('addNamaHelp').textContent = T.addNamaHelp;
    $('addBotLabel').textContent = T.addBotLabel;
    $('addWarn').textContent = T.addWarnOn;
    $('addSubmit').textContent = T.addSubmit;
    $('addCancel').textContent = T.addCancel;
    $('addLeadBtn').lastChild.nodeValue = ' ' + T.addOpen;
    $('addLeadBtn').setAttribute('aria-label', T.addTitle);
    $('addBot').setAttribute('aria-label', T.addBotLabel);

    setPassVisible(false);
    paintThemeButtons();
  }

  /* --------------------------------------------------------------- init -- */

  function bind() {
    on($('loginForm'), 'submit', doLogin);

    on($('passToggle'), 'click', function () {
      setPassVisible($('loginPass').type === 'password');
      $('loginPass').focus();
    });

    on($('themeToggle'), 'click', toggleTheme);
    on($('themeToggleLogin'), 'click', toggleTheme);

    on($('btnLogout'), 'click', doLogoutClick);
    on($('menuLogout'), 'click', function () { closeMenu(); doLogoutClick(); });

    on($('btnRefresh'), 'click', function () { loadStats(true); });
    on($('menuRefresh'), 'click', function () { closeMenu(); loadStats(true); });

    on($('menuBtn'), 'click', function (ev) { ev.stopPropagation(); toggleMenu(); });
    document.addEventListener('click', function (ev) {
      var wrap = $('menuBtn') && $('menuBtn').parentNode;
      if (wrap && !wrap.contains(ev.target)) closeMenu();
    });

    on($('tenantSelect'), 'change', function (ev) { switchTenant(ev.target.value); });

    on($('sortSelect'), 'change', function (ev) {
      var v = String(ev.target.value || '');
      if (v === '') { state.sortKey = ''; state.sortDir = 'desc'; }
      else {
        var parts = v.split('|');
        state.sortKey = parts[0];
        state.sortDir = parts[1] === 'asc' ? 'asc' : 'desc';
      }
      state.page = 1;
      paintLeads();
    });

    var searchTimer = null;
    on($('leadSearch'), 'input', function (ev) {
      var v = ev.target.value;
      syncSearchClear();
      if (searchTimer) global.clearTimeout(searchTimer);
      searchTimer = global.setTimeout(function () {
        state.q = v;
        state.page = 1;
        paintLeads();
      }, 140);
    });

    on($('searchClear'), 'click', function () {
      var input = $('leadSearch');
      input.value = '';
      state.q = '';
      state.page = 1;
      syncSearchClear();
      paintLeads();
      input.focus();
    });

    on($('botFilter'), 'click', function (ev) {
      var btn = ev.target.closest ? ev.target.closest('.seg-btn') : null;
      if (!btn) return;
      var mode = btn.getAttribute('data-mode');
      if (!mode || mode === state.botMode) return;
      state.botMode = mode;
      state.page = 1;
      var all = $('botFilter').querySelectorAll('.seg-btn');
      for (var i = 0; i < all.length; i++) all[i].classList.toggle('active', all[i] === btn);
      paintLeads();
    });

    on($('pagePrev'), 'click', function () { state.page = Math.max(1, state.page - 1); paintLeads(); });
    on($('pageNext'), 'click', function () { state.page = state.page + 1; paintLeads(); });

    on($('drawerClose'), 'click', closeDrawer);
    on($('drawerOverlay'), 'click', function (ev) {
      if (ev.target === $('drawerOverlay')) closeDrawer();
    });

    on($('menuView'), 'click', function () { closeMenu(); openViewPanel(); });
    on($('viewClose'), 'click', closeViewPanel);
    on($('viewReset'), 'click', resetView);
    on($('viewOverlay'), 'click', function (ev) {
      if (ev.target === $('viewOverlay')) closeViewPanel();
    });

    on($('addLeadBtn'), 'click', openAddLead);
    on($('addClose'), 'click', closeAddLead);
    on($('addCancel'), 'click', closeAddLead);
    on($('addForm'), 'submit', submitAddLead);
    on($('addWa'), 'input', paintAddForm);
    on($('addBot'), 'click', function () { addBotOn = !addBotOn; paintAddForm(); });
    on($('addOverlay'), 'click', function (ev) {
      if (ev.target === $('addOverlay')) closeAddLead();
    });

    on($('hintClose'), 'click', closeHint);
    on($('hintOverlay'), 'click', function (ev) {
      if (ev.target === $('hintOverlay')) closeHint();
    });

    document.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Escape') return;
      // Tutup yang paling atas dulu; kalau semua ditutup sekaligus, satu
      // Escape akan menutup panel sekaligus drawer di belakangnya.
      if ($('hintOverlay').classList.contains('open')) { closeHint(); return; }
      if ($('addOverlay').classList.contains('open')) { closeAddLead(); return; }
      if ($('viewOverlay').classList.contains('open')) { closeViewPanel(); return; }
      closeDrawer();
      closeMenu();
    });

    on($('apiBannerReset'), 'click', function () {
      cfg.setApiUrl('');
      global.location.href = global.location.pathname;
    });

    // Chart digambar dengan lebar nyata; lebar berubah -> gambar ulang.
    var resizeTimer = null;
    global.addEventListener('resize', function () {
      // Banner bisa berganti jumlah baris saat lebar berubah — ukur langsung,
      // jangan tunggu debounce, supaya header tidak sempat menimpa banner.
      measureBanner();
      if (!state.stats) return;
      if (resizeTimer) global.clearTimeout(resizeTimer);
      resizeTimer = global.setTimeout(function () {
        paintCharts();
        // Melewati ambang lebar berarti daftar lead berganti bentuk.
        if (wantsCards() !== state.cardMode) paintLeads();
      }, 180);
    });
  }

  function doLogoutClick() {
    logout('');
    toast(T.loggedOut, 'info');
  }

  function restoreRange() {
    try {
      var v = parseInt(global.localStorage.getItem(cfg.STORAGE_RANGE), 10);
      if ((cfg.RANGES || []).indexOf(v) !== -1) state.range = v;
    } catch (e) {}
  }

  function registerSW() {
    if (!('serviceWorker' in navigator)) return;
    if (global.location.protocol === 'file:') return;
    // Service worker milik aplikasi yang berdiri sendiri. Di dalam iframe
    // (harness QA end-to-end) ia tidak berguna — dan `controllerchange` di
    // bawah akan memuat ulang frame di tengah pengujian.
    try { if (global.top !== global.self) return; } catch (e) { return; }
    try {
      // Begitu SW versi baru ambil alih (clients.claim di sw.js), reload
      // sekali supaya tab/app yang sedang terbuka langsung dapat berkas
      // baru — tanpa ini pengguna terjebak di versi lama sampai reload
      // manual dua kali (parah khusus di iOS Add to Home Screen, yang
      // jarang benar-benar reload sendiri).
      var refreshing = false;
      navigator.serviceWorker.addEventListener('controllerchange', function () {
        if (refreshing) return;
        refreshing = true;
        global.location.reload();
      });
      navigator.serviceWorker.register('sw.js').catch(function () { /* diabaikan */ });
    } catch (e) {}
  }

  function boot() {
    var t = readTheme();
    state.themeExplicit = t.explicit;
    setTheme(t.theme, false);
    watchSystemTheme();

    paintIcons();
    bind();
    restoreRange();
    syncSearchClear();
    paintApiBanner();
    watchBannerHeight();

    resolveEndpoint().then(function () {
      paintApiBanner();

      var token = api.getToken();
      if (!token) { showLogin(''); return; }

      // Token ada: validasi dulu ke server sebelum menampilkan apa pun.
      loader(true, T.loading);
      api.call('me', {}).then(function (res) {
        if (!res.ok) {
          api.clearToken();
          loader(false);
          showLogin(api.isAuthError(res.error) ? res.message : '');
          return;
        }
        state.session = res.session || null;
        showApp();
        paintSession();
        loadStats(false);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  /* Diekspos untuk pemeriksaan manual dari konsol; bukan API publik. */
  global.VDApp = {
    state: state,
    reload: loadStats,
    paint: paintAll,
    setTheme: setTheme
  };

  registerSW();

}(window));
