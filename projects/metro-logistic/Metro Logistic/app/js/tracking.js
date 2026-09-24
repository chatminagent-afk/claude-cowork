/*
 * tracking.js — Logika Halaman Publik (Metro Logistik Tracking)
 * -------------------------------------------------------------
 * Tanggung jawab:
 *  - Parse input multi-resi (koma / baris baru).
 *  - Fetch batch ke N8N_GET_URL dengan timeout + retry (sinyal lemah).
 *  - Render ResultCard + TimelineStepper (terbaru di atas / .reverse()).
 *  - Filter riwayat per kartu (rentang tanggal & status).
 *  - Tangani state: loading skeleton, found:false, riwayat_error,
 *    riwayat kosong, error jaringan, offline (cache terakhir).
 *  - Registrasi service worker + prompt instal PWA (Android/iOS).
 *
 * Semua data dari API di-escape sebelum masuk DOM (hindari XSS).
 */

'use strict';

(function () {
  // ── Referensi elemen DOM ───────────────────────────────────────────────
  const $ = (id) => document.getElementById(id);
  const inputResi = $('inputResi');
  const btnLacak = $('btnLacak');
  const btnLacakText = $('btnLacakText');
  const hasilContainer = $('hasilContainer');
  const judulHasil = $('judulHasil');
  const filterSection = $('filterSection');
  const filterDari = $('filterDari');
  const filterSampai = $('filterSampai');
  const filterStatus = $('filterStatus');
  const btnTerapkanFilter = $('btnTerapkanFilter');
  const btnResetFilter = $('btnResetFilter');
  const offlineBanner = $('offlineBanner');
  const offlineBannerText = $('offlineBannerText');
  const toast = $('toast');

  // Menyimpan hasil terakhir agar filter bisa re-render tanpa fetch ulang.
  let hasilTerakhir = [];       // array objek result dari API
  let sumberCache = false;      // true bila hasil berasal dari cache offline
  let waktuCache = null;        // waktu penyimpanan cache (ISO), bila ada

  // ── Mapping warna badge status (design system Sonnet) ───────────────────
  const STATUS_STYLE = {
    'Manifest':         { badge: 'bg-netral-300 text-netral-900', dot: 'bg-netral-600',   ring: '', ikon: '&#128203;' }, // 📋
    'On Process':       { badge: 'bg-primary-light/10 text-primary-light', dot: 'bg-primary-light', ring: 'dot-active', ikon: '&#9881;&#65039;' }, // ⚙️
    'Transit':          { badge: 'bg-accent/10 text-accent', dot: 'bg-accent', ring: 'dot-active', ikon: '&#128666;' }, // 🚚
    'Out for Delivery': { badge: 'bg-accent text-white', dot: 'bg-accent', ring: 'dot-active', ikon: '&#128676;' }, // 🛵
    'Delivered':        { badge: 'bg-success/10 text-success', dot: 'bg-success', ring: 'dot-active-success', ikon: '&#9989;' }, // ✅
    'Failed/Return':    { badge: 'bg-danger/10 text-danger', dot: 'bg-danger', ring: '', ikon: '&#9888;&#65039;' } // ⚠️
  };

  function styleStatus(status) {
    return STATUS_STYLE[status] || { badge: 'bg-netral-300 text-netral-900', dot: 'bg-netral-600', ring: '', ikon: '&#128230;' };
  }

  // ══════════════════════════════════════════════════════════════════════
  // UTILITAS
  // ══════════════════════════════════════════════════════════════════════

  /** Escape karakter HTML berbahaya sebelum masuk DOM (anti-XSS). */
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /** Parse input textarea menjadi array resi unik (dipisah koma / baris baru). */
  function parseResi(raw) {
    if (!raw) return [];
    const potongan = raw.split(/[\n,]+/);
    const bersih = [];
    const terlihat = new Set();
    for (let p of potongan) {
      const r = p.trim().toUpperCase();
      if (r.length > 0 && !terlihat.has(r)) {
        terlihat.add(r);
        bersih.push(r);
      }
    }
    return bersih;
  }

  /**
   * Format waktu ISO menjadi teks Indonesia, mis. "05 Jul 2026, 14:30 WIB".
   * Aman terhadap nilai kosong/invalid.
   */
  const BULAN_ID = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  function formatWaktu(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return escapeHtml(iso); // fallback tampilkan apa adanya (di-escape)
    const dd = String(d.getDate()).padStart(2, '0');
    const mmm = BULAN_ID[d.getMonth()];
    const yyyy = d.getFullYear();
    const hh = String(d.getHours()).padStart(2, '0');
    const mi = String(d.getMinutes()).padStart(2, '0');
    return `${dd} ${mmm} ${yyyy}, ${hh}:${mi} WIB`;
  }

  /** Tampilkan toast transient (auto-hilang). */
  let toastTimer = null;
  function tampilToast(pesan, tipe) {
    const warna = tipe === 'error' ? 'bg-danger' : tipe === 'success' ? 'bg-success' : 'bg-primary';
    toast.className = `fixed left-1/2 -translate-x-1/2 bottom-5 z-50 max-w-[92%] w-max px-4 py-3 rounded-lg shadow-lg text-sm font-medium text-white ${warna}`;
    toast.textContent = pesan;
    toast.classList.remove('hidden');
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.add('hidden'), 3500);
  }

  // ══════════════════════════════════════════════════════════════════════
  // FETCH dengan TIMEOUT + RETRY (AbortController)
  // ══════════════════════════════════════════════════════════════════════

  function tidur(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function fetchWithRetry(url, options, retriesLeft) {
    if (retriesLeft === undefined) retriesLeft = CONFIG.MAX_RETRY;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), CONFIG.FETCH_TIMEOUT_MS);
    try {
      const resp = await fetch(url, Object.assign({}, options, { signal: controller.signal }));
      clearTimeout(timer);
      return resp;
    } catch (err) {
      clearTimeout(timer);
      if (retriesLeft > 0) {
        // Backoff bertahap: percobaan ke-1 = 1.5s, ke-2 = 3s.
        const percobaan = CONFIG.MAX_RETRY - retriesLeft + 1;
        await tidur(CONFIG.RETRY_BACKOFF_MS * percobaan);
        return fetchWithRetry(url, options, retriesLeft - 1);
      }
      throw err;
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  // CACHE localStorage (per resi)
  // ══════════════════════════════════════════════════════════════════════

  function simpanCache(result) {
    try {
      const key = CONFIG.CACHE_KEY_PREFIX + result.no_resi;
      const paket = { waktu: new Date().toISOString(), data: result };
      localStorage.setItem(key, JSON.stringify(paket));
    } catch (e) {
      // localStorage penuh / diblokir — abaikan (bukan fatal).
    }
  }

  function ambilCache(resi) {
    try {
      const raw = localStorage.getItem(CONFIG.CACHE_KEY_PREFIX + resi);
      if (!raw) return null;
      return JSON.parse(raw); // { waktu, data }
    } catch (e) {
      return null;
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  // NORMALISASI: memetakan berbagai bentuk field API menjadi bentuk seragam.
  // Mendukung kontrak Sonnet (riwayat/found) + kemungkinan varian
  // (Riwayat_Posisi_JSON string, riwayat_error).
  // ══════════════════════════════════════════════════════════════════════

  function normalisasiResult(item, resiDiminta) {
    const out = {
      no_resi: item && item.no_resi ? item.no_resi : resiDiminta,
      found: item ? item.found !== false : false,
      pengirim: item ? item.pengirim : null,
      penerima: item ? item.penerima : null,
      status_terakhir: item ? item.status_terakhir : null,
      timestamp_update: item ? item.timestamp_update : null,
      riwayat: [],
      riwayat_error: item ? !!item.riwayat_error : false
    };

    if (!item) return out;

    // Ambil riwayat dari salah satu sumber yang mungkin.
    let riwayatMentah = item.riwayat;

    // Bila backend mengirim Riwayat_Posisi_JSON sebagai string mentah.
    if (!Array.isArray(riwayatMentah) && item.Riwayat_Posisi_JSON !== undefined) {
      if (typeof item.Riwayat_Posisi_JSON === 'string') {
        const s = item.Riwayat_Posisi_JSON.trim();
        if (s.length === 0) {
          riwayatMentah = [];
        } else {
          try {
            riwayatMentah = JSON.parse(s);
          } catch (e) {
            out.riwayat_error = true; // JSON riwayat bermasalah
            riwayatMentah = [];
          }
        }
      } else if (Array.isArray(item.Riwayat_Posisi_JSON)) {
        riwayatMentah = item.Riwayat_Posisi_JSON;
      }
    }

    if (Array.isArray(riwayatMentah)) {
      out.riwayat = riwayatMentah;
    } else if (riwayatMentah !== undefined && riwayatMentah !== null && out.found) {
      // Ada nilai riwayat tapi bukan array & bukan string valid → tandai error.
      out.riwayat_error = true;
    }

    return out;
  }

  // ══════════════════════════════════════════════════════════════════════
  // RENDER
  // ══════════════════════════════════════════════════════════════════════

  /** Kartu skeleton loading. */
  function skeletonCard() {
    return `
      <div class="bg-white rounded-xl border border-netral-300 p-4 animate-pulse">
        <div class="h-4 w-2/3 bg-netral-300 rounded mb-3"></div>
        <div class="h-6 w-28 bg-netral-300 rounded-full mb-4"></div>
        <div class="h-3 w-1/2 bg-netral-300 rounded mb-2"></div>
        <div class="h-3 w-2/5 bg-netral-300 rounded mb-4"></div>
        <div class="space-y-3">
          <div class="h-3 w-4/5 bg-netral-300 rounded"></div>
          <div class="h-3 w-3/5 bg-netral-300 rounded"></div>
          <div class="h-3 w-4/5 bg-netral-300 rounded"></div>
        </div>
      </div>`;
  }

  function renderSkeleton(jumlah) {
    let html = '';
    for (let i = 0; i < jumlah; i++) html += skeletonCard();
    hasilContainer.innerHTML = html;
  }

  /** Satu langkah timeline. `aktif` = entri teratas (status terkini). */
  function renderStep(step, aktif) {
    const status = step && step.status ? step.status : '-';
    const st = styleStatus(status);
    const dotSize = aktif ? 'w-6 h-6' : 'w-5 h-5';
    const dotRing = aktif ? st.ring : '';
    const dotOpacity = aktif ? '' : 'opacity-70';

    return `
      <li class="timeline-step relative pl-9 pb-5">
        <span class="timeline-line"></span>
        <span class="absolute left-0 top-0.5 ${dotSize} ${st.dot} ${dotRing} ${dotOpacity} rounded-full flex items-center justify-center text-white text-[10px]"
              aria-hidden="true">${aktif ? st.ikon : ''}</span>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="inline-block text-[11px] font-bold uppercase tracking-wide px-2 py-0.5 rounded ${st.badge}">${escapeHtml(status)}</span>
          </div>
          <p class="text-xs text-netral-600 mt-1">${escapeHtml(formatWaktu(step && step.waktu))}</p>
          <p class="text-sm mt-0.5"><span aria-hidden="true">&#128205;</span> ${escapeHtml(step && step.lokasi ? step.lokasi : '-')}</p>
          <p class="text-xs text-netral-600 mt-0.5"><span aria-hidden="true">&#128100;</span> ${escapeHtml(step && step.admin ? step.admin : '-')}</p>
        </div>
      </li>`;
  }

  /**
   * Filter entri riwayat sesuai rentang tanggal & status yang aktif.
   * Mengembalikan { tampil: [...], tersembunyi: n }.
   */
  function filterRiwayat(riwayat) {
    const dari = filterDari.value ? new Date(filterDari.value + 'T00:00:00') : null;
    const sampai = filterSampai.value ? new Date(filterSampai.value + 'T23:59:59') : null;
    const status = filterStatus.value || '';

    const tampil = [];
    let tersembunyi = 0;
    for (const step of riwayat) {
      let lolos = true;
      const w = step && step.waktu ? new Date(step.waktu) : null;
      if (dari && (!w || isNaN(w) || w < dari)) lolos = false;
      if (sampai && (!w || isNaN(w) || w > sampai)) lolos = false;
      if (status && (!step || step.status !== status)) lolos = false;
      if (lolos) tampil.push(step);
      else tersembunyi++;
    }
    return { tampil, tersembunyi };
  }

  /** Render satu ResultCard lengkap. */
  function renderCard(result) {
    // ── Kasus: resi tidak ditemukan ──
    if (!result.found) {
      return `
        <div class="bg-white rounded-xl border border-netral-300 p-4">
          <h4 class="text-base font-semibold">No. Resi: ${escapeHtml(result.no_resi)}</h4>
          <div class="mt-4 text-center py-4">
            <div class="text-4xl mb-2" aria-hidden="true">&#128235;</div>
            <p class="font-semibold text-netral-900">Resi Tidak Ditemukan</p>
            <p class="text-sm text-netral-600 mt-1">Periksa kembali nomor resi Anda atau hubungi CS kami.</p>
          </div>
        </div>`;
    }

    const st = styleStatus(result.status_terakhir);
    const badgeStatus = result.status_terakhir
      ? `<span class="inline-block text-[11px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-full ${st.badge}">${escapeHtml(result.status_terakhir)}</span>`
      : '';

    // ── Header + info pengirim/penerima ──
    let html = `
      <div class="bg-white rounded-xl border border-netral-300 p-4 flex flex-col">
        <div class="flex items-start justify-between gap-2">
          <h4 class="text-base font-semibold">No. Resi: ${escapeHtml(result.no_resi)}</h4>
        </div>
        <div class="mt-2">${badgeStatus}</div>
        <div class="mt-3 pt-3 border-t border-netral-300 text-sm space-y-1">
          <p><span class="text-netral-600">Pengirim</span> : ${escapeHtml(result.pengirim || '-')}</p>
          <p><span class="text-netral-600">Penerima</span> : ${escapeHtml(result.penerima || '-')}</p>
          <p><span class="text-netral-600">Update</span> : ${escapeHtml(formatWaktu(result.timestamp_update))}</p>
        </div>
        <div class="mt-4 pt-3 border-t border-netral-300">
          <p class="text-sm font-semibold mb-3">Riwayat Perjalanan</p>`;

    // ── Kasus: riwayat error ──
    if (result.riwayat_error) {
      html += `
        <div class="text-center py-3 bg-danger/5 rounded-lg">
          <p class="text-sm text-danger font-medium">Data riwayat sedang bermasalah.</p>
          <p class="text-xs text-netral-600 mt-1">Mohon maaf, kami tidak dapat menampilkan detail perjalanan untuk resi ini. Silakan coba lagi nanti.</p>
        </div>`;
    }
    // ── Kasus: riwayat kosong ──
    else if (!result.riwayat || result.riwayat.length === 0) {
      html += `
        <div class="text-center py-3">
          <p class="text-sm text-netral-600">Belum ada riwayat perjalanan untuk resi ini.</p>
        </div>`;
    }
    // ── Kasus normal: render timeline ──
    else {
      // Balik urutan → terbaru di atas.
      const kronologis = result.riwayat.slice();
      const terbaruDiAtas = kronologis.reverse();
      const { tampil, tersembunyi } = filterRiwayat(terbaruDiAtas);

      if (tampil.length === 0) {
        html += `
          <div class="text-center py-3">
            <p class="text-sm text-netral-600">Tidak ada riwayat yang cocok dengan filter.</p>
          </div>`;
      } else {
        html += '<ul class="mt-1">';
        tampil.forEach((step, idx) => {
          // Entri teraktif = step teratas (idx 0) HANYA bila tidak difilter
          // menyembunyikan status terkini asli. Kita highlight step teratas
          // yang tampil sebagai indikator posisi terkini yang lolos filter.
          html += renderStep(step, idx === 0);
        });
        html += '</ul>';
      }

      if (tersembunyi > 0) {
        html += `<p class="text-xs text-netral-600 italic mt-1">${tersembunyi} langkah disembunyikan oleh filter.</p>`;
      }
    }

    html += '</div></div>';
    return html;
  }

  /** Render seluruh hasil (dipanggil setelah fetch atau saat filter diubah). */
  function renderHasil() {
    if (!hasilTerakhir || hasilTerakhir.length === 0) {
      hasilContainer.innerHTML = '';
      judulHasil.classList.add('hidden');
      filterSection.classList.add('hidden');
      return;
    }
    filterSection.classList.remove('hidden');
    judulHasil.classList.remove('hidden');

    let labelSumber = '';
    if (sumberCache) {
      labelSumber = ` · data tersimpan${waktuCache ? ' pada ' + formatWaktu(waktuCache) : ''}`;
    }
    judulHasil.textContent = `Hasil (${hasilTerakhir.length} resi)${labelSumber}`;

    hasilContainer.innerHTML = hasilTerakhir.map(renderCard).join('');
  }

  /** State error jaringan total (tidak ada data & tidak ada cache). */
  function renderErrorJaringan() {
    filterSection.classList.add('hidden');
    judulHasil.classList.add('hidden');
    hasilContainer.innerHTML = `
      <div class="bg-white rounded-xl border border-netral-300 p-6 text-center md:col-span-2 lg:col-span-3">
        <div class="text-4xl mb-2" aria-hidden="true">&#128225;</div>
        <p class="font-semibold">Gagal Memuat Data</p>
        <p class="text-sm text-netral-600 mt-1 mb-4">Periksa koneksi internet Anda dan coba lagi.</p>
        <button id="btnCobaLagi" type="button"
          class="min-h-[48px] px-6 rounded-lg bg-primary text-white font-semibold
                 hover:bg-primary-light active:scale-[0.98] transition">
          <span aria-hidden="true">&#128260;</span> Coba Lagi
        </button>
      </div>`;
    const btn = document.getElementById('btnCobaLagi');
    if (btn) btn.addEventListener('click', lakukanLacak);
  }

  // ══════════════════════════════════════════════════════════════════════
  // ALUR UTAMA: LACAK
  // ══════════════════════════════════════════════════════════════════════

  function setLoading(loading) {
    btnLacak.disabled = loading;
    btnLacakText.textContent = loading ? 'Memuat...' : 'Lacak';
  }

  async function lakukanLacak() {
    const daftarResi = parseResi(inputResi.value);
    if (daftarResi.length === 0) {
      tampilToast('Masukkan minimal satu nomor resi.', 'error');
      inputResi.focus();
      return;
    }

    setLoading(true);
    sumberCache = false;
    waktuCache = null;
    filterSection.classList.remove('hidden');
    judulHasil.classList.remove('hidden');
    judulHasil.textContent = 'Memuat...';
    renderSkeleton(Math.min(daftarResi.length, 3));

    const url = CONFIG.N8N_GET_URL + '?resi=' + encodeURIComponent(daftarResi.join(','));

    try {
      const resp = await fetchWithRetry(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
      const data = await resp.json();

      // Respons error terstruktur dari server / service worker offline.
      if (data && data.error) {
        // Bila SW menandai offline, coba pakai cache lokal.
        if (data.offline) {
          if (pakaiCache(daftarResi)) return;
        }
        throw new Error(data.message || 'Server error');
      }

      const results = data && Array.isArray(data.results) ? data.results : [];

      // Cocokkan tiap resi yang diminta dengan hasil (jaga urutan input).
      hasilTerakhir = daftarResi.map((resi) => {
        const cocok = results.find((r) => r && (r.no_resi || '').toUpperCase() === resi);
        const norm = normalisasiResult(cocok, resi);
        if (norm.found) simpanCache(norm); // cache hanya yang ditemukan
        return norm;
      });

      renderHasil();
    } catch (err) {
      // Gagal jaringan → coba cache lokal terakhir per resi.
      if (!pakaiCache(daftarResi)) {
        renderErrorJaringan();
      }
    } finally {
      setLoading(false);
    }
  }

  /**
   * Coba tampilkan hasil dari cache localStorage untuk daftar resi.
   * Return true bila setidaknya satu resi punya cache; false bila kosong total.
   */
  function pakaiCache(daftarResi) {
    let adaCache = false;
    let waktuTerlama = null;
    const hasil = daftarResi.map((resi) => {
      const paket = ambilCache(resi);
      if (paket && paket.data) {
        adaCache = true;
        if (!waktuTerlama || new Date(paket.waktu) < new Date(waktuTerlama)) {
          waktuTerlama = paket.waktu;
        }
        return paket.data;
      }
      // Tidak ada cache → tampilkan sebagai tidak ditemukan/tak tersedia.
      return normalisasiResult(null, resi);
    });

    if (!adaCache) return false;

    hasilTerakhir = hasil;
    sumberCache = true;
    waktuCache = waktuTerlama;
    tampilkanBannerOffline(true);
    renderHasil();
    tampilToast('Menampilkan data tersimpan terakhir.', 'info');
    return true;
  }

  // ══════════════════════════════════════════════════════════════════════
  // STATUS KONEKSI (banner offline)
  // ══════════════════════════════════════════════════════════════════════

  function tampilkanBannerOffline(paksa) {
    const offline = paksa === true || !navigator.onLine;
    if (offline) {
      offlineBanner.classList.remove('hidden');
      offlineBannerText.textContent = sumberCache
        ? 'Menampilkan data tersimpan terakhir.'
        : 'Beberapa fitur mungkin tidak tersedia.';
    } else {
      offlineBanner.classList.add('hidden');
    }
  }

  window.addEventListener('online', () => {
    tampilkanBannerOffline(false);
    tampilToast('Koneksi kembali tersedia.', 'success');
  });
  window.addEventListener('offline', () => tampilkanBannerOffline(true));

  // ══════════════════════════════════════════════════════════════════════
  // PROMPT INSTAL PWA (Android beforeinstallprompt + petunjuk manual iOS)
  // ══════════════════════════════════════════════════════════════════════

  let deferredPrompt = null;
  const installBanner = $('installBanner');
  const installBtn = $('installBtn');
  const installDismiss = $('installDismiss');
  const installBannerText = $('installBannerText');
  const DISMISS_KEY = 'metro_install_dismissed';

  function sudahTerinstal() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }

  function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  }

  function bolehTampilInstall() {
    return !sudahTerinstal() && localStorage.getItem(DISMISS_KEY) !== '1';
  }

  // Android / Chrome: tangkap event, tampilkan tombol instal.
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (bolehTampilInstall()) {
      installBanner.classList.remove('hidden');
      installBtn.classList.remove('hidden');
    }
  });

  if (installBtn) {
    installBtn.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      try { await deferredPrompt.userChoice; } catch (e) {}
      deferredPrompt = null;
      installBanner.classList.add('hidden');
    });
  }

  if (installDismiss) {
    installDismiss.addEventListener('click', () => {
      installBanner.classList.add('hidden');
      try { localStorage.setItem(DISMISS_KEY, '1'); } catch (e) {}
    });
  }

  // iOS: tampilkan petunjuk manual (tidak ada beforeinstallprompt).
  if (isIOS() && bolehTampilInstall()) {
    installBanner.classList.remove('hidden');
    installBtn.classList.add('hidden');
    installBannerText.innerHTML = 'Ketuk tombol Bagikan &#8593;, lalu pilih "Tambah ke Layar Utama".';
  }

  // ══════════════════════════════════════════════════════════════════════
  // REGISTRASI SERVICE WORKER
  // ══════════════════════════════════════════════════════════════════════

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('sw.js').catch((err) => {
        console.warn('[PWA] Registrasi service worker gagal:', err);
      });
    });
  }

  // ══════════════════════════════════════════════════════════════════════
  // EVENT BINDING
  // ══════════════════════════════════════════════════════════════════════

  btnLacak.addEventListener('click', lakukanLacak);

  // Ctrl/Cmd+Enter di textarea untuk memicu lacak (kenyamanan desktop).
  inputResi.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      lakukanLacak();
    }
  });

  btnTerapkanFilter.addEventListener('click', () => {
    renderHasil();
    tampilToast('Filter diterapkan.', 'info');
  });

  btnResetFilter.addEventListener('click', () => {
    filterDari.value = '';
    filterSampai.value = '';
    filterStatus.value = '';
    renderHasil();
  });

  // Inisialisasi banner offline saat halaman dibuka.
  tampilkanBannerOffline();
})();
