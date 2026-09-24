/*
 * tracking.js — Logika Halaman Publik (Metro Logistik Tracking)
 * (Redesain & Mode Uji Dummy oleh Antigravity)
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
  let hasilTerakhir = [];       // array objek result dari API / Dummy
  let sumberCache = false;      // true bila hasil berasal dari cache offline
  let waktuCache = null;        // waktu penyimpanan cache (ISO), bila ada
  let sumberSemuaResi = false;  // true bila hasilTerakhir dimuat otomatis (semua resi) tanpa pencarian spesifik

  // ── Mapping warna badge & ikon status (Premium Sleek Palette) ───────────
  const STATUS_STYLE = {
    'Manifest': {
      badge: 'bg-slate-100 text-slate-700 border border-slate-200',
      dot: 'bg-slate-400 ring-4 ring-slate-100',
      ikon: '📋'
    },
    'On Process': {
      badge: 'bg-slate-100 text-slate-700 border border-slate-200',
      dot: 'bg-slate-500 ring-4 ring-slate-100',
      ikon: '⚙️'
    },
    'Transit': {
      badge: 'bg-slate-100 text-slate-800 border border-slate-200',
      dot: 'bg-slate-600 ring-4 ring-slate-100',
      ikon: '🚚'
    },
    'Out for Delivery': {
      badge: 'bg-amber-50 text-amber-700 border border-amber-200',
      dot: 'bg-amber-500 ring-4 ring-amber-100 pulse-dot',
      ikon: '🛵'
    },
    'Delivered': {
      badge: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
      dot: 'bg-emerald-500 ring-4 ring-emerald-100',
      ikon: '✅'
    },
    'Failed/Return': {
      badge: 'bg-rose-50 text-rose-700 border border-rose-100',
      dot: 'bg-rose-500 ring-4 ring-rose-100',
      ikon: '⚠️'
    }
  };

  function styleStatus(status) {
    return STATUS_STYLE[status] || {
      badge: 'bg-slate-100 text-slate-700 border border-slate-200',
      dot: 'bg-slate-400 ring-4 ring-slate-100',
      ikon: '📦'
    };
  }

  // ══════════════════════════════════════════════════════════════════════
  // UTILITAS & DUMMY INTERCEPTOR
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

  /** Format waktu ISO menjadi teks Indonesia */
  const BULAN_ID = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  function formatWaktu(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return escapeHtml(iso);
    const dd = String(d.getDate()).padStart(2, '0');
    const mmm = BULAN_ID[d.getMonth()];
    const yyyy = d.getFullYear();
    const hh = String(d.getHours()).padStart(2, '0');
    const mi = String(d.getMinutes()).padStart(2, '0');
    return `${dd} ${mmm} ${yyyy}, ${hh}:${mi} WIB`;
  }

  /** Tampilkan toast transient. */
  let toastTimer = null;
  function tampilToast(pesan, tipe) {
    const warna = tipe === 'error' ? 'bg-rose-600' : tipe === 'success' ? 'bg-emerald-600' : 'bg-slate-900';
    toast.className = `fixed left-1/2 -translate-x-1/2 bottom-6 z-50 max-w-[92%] w-max px-5 py-3.5 rounded-xl shadow-xl text-sm font-medium text-white transition-all duration-300 scale-95 opacity-0 ${warna}`;
    toast.textContent = pesan;
    toast.classList.remove('hidden');
    
    // Trigger reflow untuk animasi fade-in
    void toast.offsetWidth;
    toast.classList.add('scale-100', 'opacity-100');

    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove('scale-100', 'opacity-100');
      toast.classList.add('scale-95', 'opacity-0');
      setTimeout(() => toast.classList.add('hidden'), 300);
    }, 3500);
  }

  function tidur(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /** Fetch dengan Retry */
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
        const percobaan = CONFIG.MAX_RETRY - retriesLeft + 1;
        await tidur(CONFIG.RETRY_BACKOFF_MS * percobaan);
        return fetchWithRetry(url, options, retriesLeft - 1);
      }
      throw err;
    }
  }

  /** Penggabungan Data Dummy dengan Update di LocalStorage */
  function dapatkanDataDummyTerupdate() {
    let localUpdates = [];
    try {
      const raw = localStorage.getItem(CONFIG.DUMMY_STORAGE_KEY);
      if (raw) localUpdates = JSON.parse(raw);
    } catch (e) {}

    // Clone CONFIG.DUMMY_DATA
    const data = JSON.parse(JSON.stringify(CONFIG.DUMMY_DATA));

    for (const update of localUpdates) {
      const resiObj = data.find(r => r.no_resi.toUpperCase() === update.no_resi.toUpperCase());
      if (resiObj) {
        // Cek apakah step ini sudah ada di riwayat
        const exists = resiObj.riwayat.some(step => 
          step.status === update.status && 
          step.lokasi === update.lokasi && 
          step.admin === update.nama_admin
        );
        if (!exists) {
          resiObj.riwayat.push({
            status: update.status,
            waktu: update.waktu,
            lokasi: update.lokasi,
            admin: update.nama_admin
          });
          resiObj.status_terakhir = update.status;
          resiObj.timestamp_update = update.waktu;
        }
      } else {
        // Buat resi baru
        data.push({
          no_resi: update.no_resi.toUpperCase(),
          found: true,
          pengirim: 'Pengirim Baru (Simulasi)',
          penerima: 'Penerima Baru (Simulasi)',
          status_terakhir: update.status,
          timestamp_update: update.waktu,
          riwayat: [
            {
              status: update.status,
              waktu: update.waktu,
              lokasi: update.lokasi,
              admin: update.nama_admin
            }
          ]
        });
      }
    }
    return data;
  }

  // ══════════════════════════════════════════════════════════════════════
  // CACHE localStorage (per resi)
  // ══════════════════════════════════════════════════════════════════════

  let sudahPeringatkanPenyimpanan = false;
  function simpanCache(result) {
    try {
      const key = CONFIG.CACHE_KEY_PREFIX + result.no_resi;
      const paket = { waktu: new Date().toISOString(), data: result };
      localStorage.setItem(key, JSON.stringify(paket));
    } catch (e) {
      if (!sudahPeringatkanPenyimpanan) {
        sudahPeringatkanPenyimpanan = true;
        tampilToast(CONFIG.ERROR_MESSAGES.PENYIMPANAN_LOKAL_GAGAL, 'info');
      }
    }
  }

  function ambilCache(resi) {
    try {
      const raw = localStorage.getItem(CONFIG.CACHE_KEY_PREFIX + resi);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  // NORMALISASI & RENDER
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

    let riwayatMentah = item.riwayat;

    if (!Array.isArray(riwayatMentah) && item.Riwayat_Posisi_JSON !== undefined) {
      if (typeof item.Riwayat_Posisi_JSON === 'string') {
        const s = item.Riwayat_Posisi_JSON.trim();
        if (s.length === 0) {
          riwayatMentah = [];
        } else {
          try {
            riwayatMentah = JSON.parse(s);
          } catch (e) {
            out.riwayat_error = true;
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
      out.riwayat_error = true;
    }

    return out;
  }

  /** Skeleton Card */
  function skeletonCard() {
    return `
      <div class="card-glass dark:bg-slate-900/85 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm animate-pulse">
        <div class="h-5 w-1/2 bg-slate-200 dark:bg-slate-800 rounded mb-4"></div>
        <div class="h-6 w-24 bg-slate-200 dark:bg-slate-800 rounded-full mb-6"></div>
        <div class="space-y-3 mb-6">
          <div class="h-3.5 w-full bg-slate-200 dark:bg-slate-800 rounded"></div>
          <div class="h-3.5 w-3/4 bg-slate-200 dark:bg-slate-800 rounded"></div>
        </div>
        <div class="border-t border-slate-100 dark:border-slate-800/60 pt-5 space-y-4">
          <div class="flex gap-3">
            <div class="w-5 h-5 rounded-full bg-slate-200 dark:bg-slate-800 shrink-0"></div>
            <div class="space-y-2 w-full">
              <div class="h-3.5 w-1/3 bg-slate-200 dark:bg-slate-800 rounded"></div>
              <div class="h-3.5 w-5/6 bg-slate-200 dark:bg-slate-800 rounded"></div>
            </div>
          </div>
        </div>
      </div>`;
  }

  function renderSkeleton(jumlah) {
    let html = '';
    for (let i = 0; i < jumlah; i++) html += skeletonCard();
    hasilContainer.innerHTML = html;
  }

  /** renderStep */
  function renderStep(step, aktif) {
    const status = step && step.status ? step.status : '-';
    const st = styleStatus(status);
    const dotColor = aktif ? st.dot : 'bg-slate-300 dark:bg-slate-700 ring-4 ring-slate-100/50 dark:ring-slate-800/40';
    const textColor = aktif ? 'text-slate-900 dark:text-slate-100 font-semibold' : 'text-slate-500 dark:text-slate-400';

    return `
      <li class="timeline-step relative pl-8 pb-5 last:pb-0">
        <span class="timeline-line"></span>
        <span class="absolute left-0 top-0.5 w-5 h-5 ${dotColor} rounded-full transition-all duration-300 z-10"></span>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="inline-block text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${st.badge}">${escapeHtml(status)}</span>
            <span class="text-[11px] text-slate-400 dark:text-slate-500 font-medium">${escapeHtml(formatWaktu(step && step.waktu))}</span>
          </div>
          <p class="text-sm text-slate-700 dark:text-slate-300 mt-1 flex items-start gap-1.5">
            <span class="text-slate-400 dark:text-slate-500 select-none shrink-0 mt-0.5 text-xs">📍</span>
            <span class="${textColor}">${escapeHtml(step && step.lokasi ? step.lokasi : '-')}</span>
          </p>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5 flex items-center gap-1.5">
            <span class="select-none">👤</span>
            <span>${escapeHtml(step && step.admin ? step.admin : '-')}</span>
          </p>
        </div>
      </li>`;
  }

  /**
   * Baca rentang filter yang SEDANG AKTIF langsung dari input DOM.
   * Dipakai sebagai satu-satunya sumber kebenaran (single source of truth)
   * baik untuk penyaringan level-card (hasilTersaring) maupun penyaringan
   * step riwayat di dalam tiap card (filterRiwayat) — supaya keduanya
   * selalu konsisten dan tidak pernah menyimpang.
   */
  function bacaFilterEfektif() {
    return {
      dari: filterDari.value ? new Date(filterDari.value + 'T00:00:00') : null,
      sampai: filterSampai.value ? new Date(filterSampai.value + 'T23:59:59') : null,
      status: filterStatus.value || ''
    };
  }

  /**
   * Status TERAKHIR sebuah resi — sumber kebenaran untuk filter status
   * level-card. Pakai status_terakhir dari API; bila kosong, fallback ke
   * status entri riwayat paling akhir (paling baru).
   */
  function statusTerakhirResult(result) {
    if (result && result.status_terakhir) return result.status_terakhir;
    const r = result && Array.isArray(result.riwayat) ? result.riwayat : [];
    for (let i = r.length - 1; i >= 0; i--) {
      if (r[i] && r[i].status) return r[i].status;
    }
    return null;
  }

  /** Format objek Date menjadi string "YYYY-MM-DD" sesuai zona waktu LOKAL (bukan UTC),
   *  supaya cocok dengan format yang dipakai oleh <input type="date">. */
  function formatTanggalUntukInput(d) {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  /**
   * Filter Riwayat — menerima rentang efektif eksplisit (dari/sampai).
   * CATATAN: filter STATUS sengaja TIDAK diterapkan di level step — status
   * hanya menyaring kartu (berdasarkan status terakhir resi). Timeline
   * selalu menampilkan SEMUA status yang pernah dilalui, misalnya resi
   * Delivered tetap memperlihatkan Manifest → On Process → Transit → dst.
   */
  function filterRiwayat(riwayat, efektif) {
    const dari = efektif.dari;
    const sampai = efektif.sampai;

    const tampil = [];
    let tersembunyi = 0;
    for (const step of riwayat) {
      let lolos = true;
      const w = step && step.waktu ? new Date(step.waktu) : null;
      if (dari && (!w || isNaN(w) || w < dari)) lolos = false;
      if (sampai && (!w || isNaN(w) || w > sampai)) lolos = false;
      if (lolos) tampil.push(step);
      else tersembunyi++;
    }
    return { tampil, tersembunyi };
  }

  // ID unik per card untuk toggle expand
  let cardIdCounter = 0;

  /** renderCard — efektif: { dari, sampai, status } dipakai untuk menyaring step riwayat. */
  function renderCard(result, efektif) {
    const cardId = 'card-timeline-' + (cardIdCounter++);

    if (!result.found) {
      return `
        <div class="card-glass dark:bg-slate-900/85 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5 shadow-sm animate-fade-in">
          <div class="flex items-center justify-between gap-2 mb-1">
            <h4 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider font-mono">${escapeHtml(result.no_resi)}</h4>
            <span class="shrink-0 px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-900/50">Tidak Ditemukan</span>
          </div>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-2">${escapeHtml(CONFIG.ERROR_MESSAGES.RESI_TIDAK_DITEMUKAN)}</p>
        </div>`;
    }

    const st = styleStatus(result.status_terakhir);
    const badgeStatus = result.status_terakhir
      ? `<span class="shrink-0 inline-block text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full ${st.badge}">${escapeHtml(result.status_terakhir)}</span>`
      : '';

    // Bangun konten timeline
    let timelineHtml = '';
    if (result.riwayat_error) {
      timelineHtml = `
        <div class="text-center py-4 bg-rose-50/30 dark:bg-rose-950/10 border border-rose-100/50 dark:border-rose-900/30 rounded-xl mt-4">
          <p class="text-xs text-rose-600 dark:text-rose-400 font-semibold">${escapeHtml(CONFIG.ERROR_MESSAGES.RIWAYAT_BERMASALAH)}</p>
        </div>`;
    } else if (!result.riwayat || result.riwayat.length === 0) {
      timelineHtml = `
        <div class="text-center py-4 mt-4">
          <p class="text-xs text-slate-400 dark:text-slate-500">${escapeHtml(CONFIG.ERROR_MESSAGES.TIDAK_ADA_RIWAYAT)}</p>
        </div>`;
    } else {
      const terbaruDiAtas = result.riwayat.slice().reverse();
      const { tampil, tersembunyi } = filterRiwayat(terbaruDiAtas, efektif);
      if (tampil.length === 0) {
        timelineHtml = `
          <div class="text-center py-4 mt-4">
            <p class="text-xs text-slate-400 dark:text-slate-500">${escapeHtml(CONFIG.ERROR_MESSAGES.FILTER_TIDAK_COCOK)}</p>
          </div>`;
      } else {
        timelineHtml = `<ul class="mt-4 relative">${tampil.map((step, idx) => renderStep(step, idx === 0)).join('')}</ul>`;
        if (tersembunyi > 0) {
          timelineHtml += `<p class="text-[10px] text-slate-400 italic mt-2 text-right">${tersembunyi} langkah disembunyikan oleh filter</p>`;
        }
      }
    }

    return `
      <div class="card-glass dark:bg-slate-900/85 border border-slate-100 dark:border-slate-800/80 rounded-2xl shadow-sm hover:shadow-md dark:shadow-none transition-all duration-300 animate-fade-in overflow-hidden">
        
        <!-- Header Ringkas (selalu tampil) -->
        <div class="p-5">
          <div class="flex items-start justify-between gap-3 mb-3">
            <div class="min-w-0">
              <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-0.5">No. Resi</p>
              <h4 class="text-base font-extrabold text-primary dark:text-primary-light font-mono tracking-tight truncate">${escapeHtml(result.no_resi)}</h4>
            </div>
            ${badgeStatus}
          </div>

          <div class="flex items-center justify-between gap-2">
            <p class="text-[11px] text-slate-400 dark:text-slate-500 flex items-center gap-1">
              <span>🕒</span> ${escapeHtml(formatWaktu(result.timestamp_update))}
            </p>
            <button
              type="button"
              onclick="(function(btn){
                var panel = document.getElementById('${cardId}');
                var icon = btn.querySelector('.expand-icon');
                var isOpen = panel.style.maxHeight && panel.style.maxHeight !== '0px';
                if (isOpen) {
                  panel.style.maxHeight = '0px';
                  panel.style.opacity = '0';
                  btn.querySelector('.expand-label').textContent = 'Lihat Detail';
                  icon.style.transform = 'rotate(0deg)';
                } else {
                  panel.style.maxHeight = panel.scrollHeight + 'px';
                  panel.style.opacity = '1';
                  btn.querySelector('.expand-label').textContent = 'Tutup';
                  icon.style.transform = 'rotate(180deg)';
                }
              })(this)"
              class="flex items-center gap-1.5 text-[11px] font-bold text-primary dark:text-primary-light hover:text-primary-dark dark:hover:text-white px-3 py-1.5 rounded-lg bg-primary/5 dark:bg-primary-light/10 hover:bg-primary/10 dark:hover:bg-primary-light/20 transition-all duration-200 shrink-0">
              <span class="expand-label">Lihat Detail</span>
              <svg class="expand-icon w-3.5 h-3.5 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Panel Detail Timeline (collapsible) -->
        <div
          id="${cardId}"
          style="max-height: 0px; opacity: 0; overflow: hidden; transition: max-height 0.4s cubic-bezier(0.16,1,0.3,1), opacity 0.3s ease;">
          <div class="px-5 pb-5 border-t border-slate-100 dark:border-slate-800/60 pt-4">
            <h5 class="text-[10px] font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
              Timeline Perjalanan
              <span class="w-1.5 h-1.5 rounded-full bg-primary dark:bg-primary-light inline-block"></span>
            </h5>
            ${timelineHtml}
          </div>
        </div>
      </div>`;
  }

  /**
   * renderHasil — labelAuto30: true bila rentang yang sedang aktif berasal
   * dari auto-default 30 hari (murni untuk label teks, bukan untuk logika
   * penyaringan — nilai filter SELALU dibaca langsung dari input via
   * bacaFilterEfektif() supaya level-card & level-step konsisten).
   */
  function renderHasil(labelAuto30) {
    if (!hasilTerakhir || hasilTerakhir.length === 0) {
      hasilContainer.innerHTML = '';
      judulHasil.classList.add('hidden');
      if (!CONFIG.TEST_DUMMY) {
        filterSection.classList.add('hidden');
      }
      return;
    }

    const efektif = bacaFilterEfektif();
    const { dari, sampai, status } = efektif;

    const hasilTersaring = hasilTerakhir.filter(result => {
      // Resi "tidak ditemukan": tampil hanya bila TIDAK ada filter status
      // (resi tanpa status tidak mungkin cocok dengan status apa pun).
      if (!result.found) return !status;
      if (!dari && !sampai && !status) return true;

      // ── Filter STATUS: berdasarkan status TERAKHIR resi, BUKAN status
      //    yang pernah dilalui. Contoh: resi yang sudah Delivered tidak
      //    muncul saat filter "Manifest", tapi muncul saat filter "Delivered".
      if (status) {
        const stAkhir = statusTerakhirResult(result);
        if (!stAkhir || String(stAkhir).trim().toLowerCase() !== status.trim().toLowerCase()) {
          return false;
        }
      }

      // ── Filter TANGGAL: cukup ada minimal satu langkah riwayat dalam rentang.
      if (dari || sampai) {
        const adaDalamRentang = (result.riwayat || []).some(step => {
          const w = step && step.waktu ? new Date(step.waktu) : null;
          if (!w || isNaN(w)) return false;
          if (dari && w < dari) return false;
          if (sampai && w > sampai) return false;
          return true;
        });
        if (!adaDalamRentang) return false;
      }

      return true;
    });

    filterSection.classList.remove('hidden');
    judulHasil.classList.remove('hidden');

    let labelFilter = labelAuto30 ? ' · 30 hari terakhir' : '';
    if (sumberSemuaResi) labelFilter += ' · seluruh resi (belum ada pencarian spesifik)';
    let labelSumber = '';
    if (CONFIG.TEST_DUMMY) {
      labelSumber = ` · ⚠️ Mode Uji Dummy`;
    } else if (sumberCache) {
      labelSumber = ` · data tersimpan${waktuCache ? ' ' + formatWaktu(waktuCache) : ''}`;
    }

    judulHasil.textContent = `Hasil Pelacakan (${hasilTersaring.length} dari ${hasilTerakhir.length} resi)${labelFilter}${labelSumber}`;

    if (hasilTersaring.length === 0) {
      hasilContainer.innerHTML = `
        <div class="card-glass dark:bg-slate-900/85 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-8 text-center animate-fade-in max-w-md mx-auto w-full">
          <div class="text-4xl mb-3">📅</div>
          <p class="font-bold text-slate-800 dark:text-slate-100">Tidak Ada Data Cocok</p>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">${escapeHtml(CONFIG.ERROR_MESSAGES.FILTER_CARD_TIDAK_COCOK)}</p>
        </div>`;
    } else {
      hasilContainer.innerHTML = hasilTersaring.map(result => renderCard(result, efektif)).join('');
    }
  }

  /** Render Error Jaringan — pesan opsional (default: tidak ada koneksi). */
  function renderErrorJaringan(pesan) {
    filterSection.classList.add('hidden');
    judulHasil.classList.add('hidden');
    hasilContainer.innerHTML = `
      <div class="card-glass border border-slate-100 rounded-2xl p-8 text-center animate-fade-in max-w-md mx-auto">
        <div class="text-4xl mb-3 animate-pulse">📡</div>
        <p class="font-bold text-slate-800">Koneksi Bermasalah</p>
        <p class="text-xs text-slate-400 mt-1 mb-5">${escapeHtml(pesan || CONFIG.ERROR_MESSAGES.TIDAK_ADA_KONEKSI)}</p>
        <button id="btnCobaLagi" type="button"
          class="min-h-[44px] px-6 rounded-xl bg-primary text-white font-semibold text-sm shadow-sm shadow-slate-100 hover:bg-primary-light active:scale-95 transition-all duration-200">
          Coba Lagi
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
    btnLacakText.textContent = loading ? 'Memproses...' : 'Lacak';
    if (loading) {
      btnLacak.classList.add('opacity-75', 'cursor-not-allowed');
    } else {
      btnLacak.classList.remove('opacity-75', 'cursor-not-allowed');
    }
  }

  async function lakukanLacak() {
    const daftarResi = parseResi(inputResi.value);
    if (daftarResi.length === 0) {
      tampilToast(CONFIG.ERROR_MESSAGES.RESI_KOSONG, 'error');
      inputResi.focus();
      return;
    }

    setLoading(true);
    sumberCache = false;
    waktuCache = null;
    sumberSemuaResi = false; // pencarian spesifik → bukan lagi "seluruh resi"
    filterSection.classList.remove('hidden');
    judulHasil.classList.remove('hidden');
    judulHasil.textContent = 'Memuat data...';
    renderSkeleton(Math.min(daftarResi.length, 3));

    // ── INTERCEPTOR DUMMY MODE ──
    if (CONFIG.TEST_DUMMY) {
      await tidur(800); // Beri simulasi delay loading agar terasa realistis
      const dummyDatabase = dapatkanDataDummyTerupdate();
      hasilTerakhir = daftarResi.map((resi) => {
        const cocok = dummyDatabase.find((r) => r.no_resi.toUpperCase() === resi);
        return normalisasiResult(cocok, resi);
      });
      renderHasil();
      setLoading(false);
      tampilToast('Menampilkan data simulasi uji dummy.', 'success');
      return;
    }

    // ── Endpoint belum dikonfigurasi → jangan buang waktu retry, langsung info jelas ──
    if (CONFIG.ENDPOINT_BELUM_DIKONFIGURASI) {
      if (!pakaiCache(daftarResi)) {
        renderErrorJaringan(CONFIG.ERROR_MESSAGES.ENDPOINT_BELUM_DIKONFIGURASI);
      }
      setLoading(false);
      return;
    }

    const url = CONFIG.N8N_GET_URL + '?resi=' + encodeURIComponent(daftarResi.join(','));

    try {
      const resp = await fetchWithRetry(url, { method: 'GET', headers: { 'Accept': 'application/json' } });

      let data = null;
      try {
        data = await resp.json();
      } catch (parseErr) {
        throw new Error(CONFIG.ERROR_MESSAGES.RESPON_TIDAK_VALID);
      }

      if (data && data.error) {
        if (data.offline) {
          if (pakaiCache(daftarResi)) return;
        }
        throw new Error(data.message || CONFIG.ERROR_MESSAGES.SERVER_ERROR);
      }

      if (!resp.ok) {
        throw new Error((data && data.message) || CONFIG.ERROR_MESSAGES.SERVER_ERROR);
      }

      const results = data && Array.isArray(data.results) ? data.results : [];

      hasilTerakhir = daftarResi.map((resi) => {
        const cocok = results.find((r) => r && (r.no_resi || '').toUpperCase() === resi);
        const norm = normalisasiResult(cocok, resi);
        if (norm.found) simpanCache(norm);
        return norm;
      });

      renderHasil();
    } catch (err) {
      if (!pakaiCache(daftarResi)) {
        const pesan = err && err.name === 'AbortError'
          ? CONFIG.ERROR_MESSAGES.TIMEOUT_SERVER
          : (err && err.message) || CONFIG.ERROR_MESSAGES.TIDAK_ADA_KONEKSI;
        renderErrorJaringan(pesan);
      }
    } finally {
      setLoading(false);
    }
  }

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
      return normalisasiResult(null, resi);
    });

    if (!adaCache) return false;

    hasilTerakhir = hasil;
    sumberCache = true;
    waktuCache = waktuTerlama;
    tampilkanBannerOffline(true);
    renderHasil();
    tampilToast('Offline. Menampilkan data dari cache lokal.', 'info');
    return true;
  }

  // ══════════════════════════════════════════════════════════════════════
  // STATUS KONEKSI (banner offline)
  // ══════════════════════════════════════════════════════════════════════

  function tampilkanBannerOffline(paksa) {
    const offline = paksa === true || !navigator.onLine;
    if (offline) {
      offlineBanner.classList.remove('hidden');
      offlineBanner.classList.add('flex');
      offlineBannerText.textContent = sumberCache
        ? 'Menampilkan data tersimpan terakhir di memori.'
        : 'Mode offline aktif. Beberapa fitur mungkin terbatas.';
    } else {
      offlineBanner.classList.add('hidden');
      offlineBanner.classList.remove('flex');
    }
  }

  window.addEventListener('online', () => {
    tampilkanBannerOffline(false);
    tampilToast('Koneksi internet terhubung kembali.', 'success');
  });
  window.addEventListener('offline', () => tampilkanBannerOffline(true));

  // ══════════════════════════════════════════════════════════════════════
  // PROMPT INSTAL PWA
  // ══════════════════════════════════════════════════════════════════════

  let deferredPrompt = null;
  const installBanner = $('installBanner');
  const installBtn = $('installBtn');
  const installDismiss = $('installDismiss');
  const installBannerText = $('installBannerText');
  const DISMISS_KEY = 'metro_install_dismissed';

  function sudahTerinstal() {
    return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  }

  function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  }

  function bolehTampilInstall() {
    return !sudahTerinstal() && localStorage.getItem(DISMISS_KEY) !== '1';
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (bolehTampilInstall()) {
      installBanner.classList.remove('hidden');
      installBanner.classList.add('flex');
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
      installBanner.classList.remove('flex');
    });
  }

  if (installDismiss) {
    installDismiss.addEventListener('click', () => {
      installBanner.classList.add('hidden');
      installBanner.classList.remove('flex');
      try { localStorage.setItem(DISMISS_KEY, '1'); } catch (e) {}
    });
  }

  if (isIOS() && bolehTampilInstall()) {
    installBanner.classList.remove('hidden');
    installBanner.classList.add('flex');
    installBtn.classList.add('hidden');
    installBannerText.innerHTML = 'Ketuk tombol Bagikan 📤 lalu pilih <b>"Tambah ke Layar Utama"</b>.';
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

  inputResi.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      lakukanLacak();
    }
  });

  /**
   * Pastikan ada data untuk difilter. Bila belum pernah melakukan pencarian
   * (hasilTerakhir kosong): pada Mode Uji Dummy kita muat SELURUH resi yang
   * pernah diupdate dari portal admin (sesuai spesifikasi: filter kosong
   * menampilkan maksimal 30 hari dari invoice yang diupdate admin — bukan
   * hanya menyaring resi yang kebetulan sudah dicari manual). Pada mode
   * produksi (API n8n asli), API saat ini hanya menerima query per no. resi,
   * jadi kita tampilkan pesan panduan yang jelas alih-alih diam saja.
   * Return true bila ada data untuk dirender, false bila tidak.
   */
  function pastikanAdaDataUntukFilter() {
    if (hasilTerakhir && hasilTerakhir.length > 0) return true;

    if (CONFIG.TEST_DUMMY) {
      hasilTerakhir = dapatkanDataDummyTerupdate();
      sumberSemuaResi = true;
      return true;
    }

    tampilToast(CONFIG.ERROR_MESSAGES.FILTER_PERLU_PENCARIAN, 'error');
    return false;
  }

  btnTerapkanFilter.addEventListener('click', () => {
    const kosong = !filterDari.value && !filterSampai.value && !filterStatus.value;

    if (!pastikanAdaDataUntukFilter()) return;

    if (kosong) {
      // Tidak ada field yang diisi → isi field tanggal dengan rentang 30 hari
      // terakhir SECARA NYATA (bukan hanya rentang "bayangan" di memori),
      // supaya penyaringan level-card & level-step di dalam tiap card
      // sama-sama membaca rentang yang identik lewat bacaFilterEfektif().
      const sekarang = new Date();
      const tigaPuluhHariLalu = new Date(sekarang);
      tigaPuluhHariLalu.setDate(sekarang.getDate() - 30);

      filterDari.value = formatTanggalUntukInput(tigaPuluhHariLalu);
      filterSampai.value = formatTanggalUntukInput(sekarang);

      renderHasil(true);
      tampilToast('Menampilkan data 30 hari terakhir (berdasarkan tanggal update tiap resi).', 'info');
    } else {
      renderHasil(false);
      tampilToast('Filter diterapkan.', 'info');
    }
  });

  btnResetFilter.addEventListener('click', () => {
    filterDari.value = '';
    filterSampai.value = '';
    filterStatus.value = '';
    renderHasil(false);
    tampilToast('Filter dibersihkan.', 'info');
  });

  tampilkanBannerOffline();

  // ── Tampilkan filterSection sejak awal (selalu, termasuk mode dummy) ──
  filterSection.classList.remove('hidden');
})();
