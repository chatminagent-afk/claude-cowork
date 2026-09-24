/*
 * admin.js — Logika Halaman Admin Lapangan (Metro Logistik Tracking)
 * ------------------------------------------------------------------
 * Tanggung jawab:
 *  - Validasi client-side per-field (wajib, tolak spasi-saja).
 *  - Submit POST JSON ke N8N_UPDATE_URL (timeout + retry).
 *  - Persist Nama Admin di localStorage (bukan data sensitif lain).
 *  - Antrean offline via IndexedDB (fallback localStorage): simpan saat
 *    gagal jaringan, badge jumlah antrean, kirim ulang otomatis saat online
 *    & saat halaman dibuka, dengan client_id unik anti-duplikat.
 *  - Registrasi service worker + banner offline.
 *
 * Catatan: POST ke N8N_UPDATE_URL sengaja TIDAK di-cache oleh service worker;
 * ketahanan tulis ditangani di sini via antrean IndexedDB.
 */

'use strict';

(function () {
  const $ = (id) => document.getElementById(id);

  const form = $('formAdmin');
  const noResi = $('noResi');
  const namaAdmin = $('namaAdmin');
  const statusResi = $('statusResi');
  const lokasi = $('lokasi');
  const btnSubmit = $('btnSubmit');
  const btnSubmitText = $('btnSubmitText');
  const spinner = $('spinner');
  const toast = $('toast');
  const offlineBanner = $('offlineBanner');
  const antreanBadge = $('antreanBadge');
  const antreanText = $('antreanText');

  const errEl = {
    noResi: $('errNoResi'),
    namaAdmin: $('errNamaAdmin'),
    statusResi: $('errStatus'),
    lokasi: $('errLokasi')
  };
  const inputEl = { noResi, namaAdmin, statusResi, lokasi };

  // ══════════════════════════════════════════════════════════════════════
  // UTILITAS
  // ══════════════════════════════════════════════════════════════════════

  /** Escape HTML (dipakai bila membangun pesan dinamis ke DOM). */
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /** UUID sederhana untuk client_id (idempotensi antrean). */
  function buatId() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'id-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
  }

  let toastTimer = null;
  function tampilToast(pesan, tipe) {
    const warna = tipe === 'error' ? 'bg-danger' : tipe === 'success' ? 'bg-success' : 'bg-primary';
    toast.className = `fixed left-1/2 -translate-x-1/2 bottom-5 z-50 max-w-[92%] w-max px-4 py-3 rounded-lg shadow-lg text-sm font-medium text-white text-center ${warna}`;
    toast.textContent = pesan;
    toast.classList.remove('hidden');
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.add('hidden'), 4000);
  }

  function tidur(ms) { return new Promise((r) => setTimeout(r, ms)); }

  // ══════════════════════════════════════════════════════════════════════
  // FETCH dengan TIMEOUT + RETRY
  // ══════════════════════════════════════════════════════════════════════

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

  // ══════════════════════════════════════════════════════════════════════
  // ANTREAN OFFLINE — IndexedDB (fallback localStorage)
  // ══════════════════════════════════════════════════════════════════════

  const DB_NAME = 'metro_admin_queue_db';
  const STORE = 'pending_updates';
  let dbPromise = null;
  const punyaIDB = typeof indexedDB !== 'undefined';

  function bukaDB() {
    if (dbPromise) return dbPromise;
    dbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(STORE)) {
          db.createObjectStore(STORE, { keyPath: 'client_id' });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
    return dbPromise;
  }

  // ── Fallback localStorage ──
  function lsBaca() {
    try {
      const raw = localStorage.getItem(CONFIG.OFFLINE_QUEUE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) { return []; }
  }
  function lsTulis(arr) {
    try { localStorage.setItem(CONFIG.OFFLINE_QUEUE_KEY, JSON.stringify(arr)); } catch (e) {}
  }

  /** Simpan entri ke antrean. */
  async function antreanSimpan(entri) {
    if (punyaIDB) {
      try {
        const db = await bukaDB();
        await new Promise((resolve, reject) => {
          const tx = db.transaction(STORE, 'readwrite');
          tx.objectStore(STORE).put(entri);
          tx.oncomplete = resolve;
          tx.onerror = () => reject(tx.error);
        });
        return;
      } catch (e) {
        // Jatuh ke localStorage bila IndexedDB gagal.
      }
    }
    const arr = lsBaca();
    if (!arr.some((x) => x.client_id === entri.client_id)) arr.push(entri);
    lsTulis(arr);
  }

  /** Ambil semua entri antrean. */
  async function antreanSemua() {
    if (punyaIDB) {
      try {
        const db = await bukaDB();
        return await new Promise((resolve, reject) => {
          const tx = db.transaction(STORE, 'readonly');
          const req = tx.objectStore(STORE).getAll();
          req.onsuccess = () => resolve(req.result || []);
          req.onerror = () => reject(req.error);
        });
      } catch (e) {}
    }
    return lsBaca();
  }

  /** Hapus satu entri berdasarkan client_id. */
  async function antreanHapus(clientId) {
    if (punyaIDB) {
      try {
        const db = await bukaDB();
        await new Promise((resolve, reject) => {
          const tx = db.transaction(STORE, 'readwrite');
          tx.objectStore(STORE).delete(clientId);
          tx.oncomplete = resolve;
          tx.onerror = () => reject(tx.error);
        });
        return;
      } catch (e) {}
    }
    lsTulis(lsBaca().filter((x) => x.client_id !== clientId));
  }

  async function antreanJumlah() {
    const semua = await antreanSemua();
    return semua.length;
  }

  /** Perbarui badge indikator jumlah antrean. */
  async function perbaruiBadgeAntrean() {
    const n = await antreanJumlah();
    if (n > 0) {
      antreanBadge.classList.remove('hidden');
      antreanText.textContent = `${n} update menunggu dikirim.`;
    } else {
      antreanBadge.classList.add('hidden');
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  // KIRIM ke server (dipakai submit langsung & flushQueue)
  // ══════════════════════════════════════════════════════════════════════

  /**
   * Kirim satu payload ke WF2.
   * Return { ok:true } | { ok:false, validasi:true, pesan } | throw (jaringan).
   */
  async function kirimKeServer(payload) {
    const resp = await fetchWithRetry(CONFIG.N8N_UPDATE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(payload)
    });

    let data = null;
    try { data = await resp.json(); } catch (e) { data = null; }

    if (data && data.success === true) {
      return { ok: true, data: data };
    }
    // Gagal validasi/server (bukan jaringan) — jangan diantrekan ulang.
    return {
      ok: false,
      validasi: true,
      pesan: (data && data.message) ? data.message : 'Gagal memproses update.'
    };
  }

  /**
   * flushQueue — kirim ulang semua entri pending.
   * Dipanggil saat online & saat halaman dibuka.
   */
  let sedangFlush = false;
  async function flushQueue() {
    if (sedangFlush) return;
    if (!navigator.onLine) return;
    sedangFlush = true;
    try {
      const semua = await antreanSemua();
      let terkirim = 0;
      for (const entri of semua) {
        try {
          const hasil = await kirimKeServer(entri.payload);
          if (hasil.ok) {
            await antreanHapus(entri.client_id);
            terkirim++;
          } else if (hasil.validasi) {
            // Ditolak server karena validasi → hapus agar tidak nyangkut selamanya.
            await antreanHapus(entri.client_id);
          }
          // Jika throw (jaringan) → biarkan tetap di antrean, coba lagi nanti.
        } catch (e) {
          break; // jaringan bermasalah lagi; hentikan, sisa tetap pending.
        }
      }
      await perbaruiBadgeAntrean();
      if (terkirim > 0) {
        tampilToast(`${terkirim} update tertunda berhasil dikirim.`, 'success');
      }
    } finally {
      sedangFlush = false;
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  // VALIDASI FORM
  // ══════════════════════════════════════════════════════════════════════

  function setError(field, pesan) {
    errEl[field].textContent = pesan;
    errEl[field].classList.remove('hidden');
    inputEl[field].classList.add('border-danger', 'ring-2', 'ring-danger');
    inputEl[field].classList.remove('border-netral-300');
  }
  function bersihkanError(field) {
    errEl[field].classList.add('hidden');
    inputEl[field].classList.remove('border-danger', 'ring-2', 'ring-danger');
    inputEl[field].classList.add('border-netral-300');
  }
  function bersihkanSemuaError() {
    Object.keys(errEl).forEach(bersihkanError);
  }

  /** Return { valid, payload, fieldPertamaGagal }. */
  function validasi() {
    bersihkanSemuaError();
    let valid = true;
    let fieldPertama = null;

    const vResi = (noResi.value || '').trim().toUpperCase();
    const vNama = (namaAdmin.value || '').trim();
    const vStatus = statusResi.value || '';
    const vLokasi = (lokasi.value || '').trim();

    if (vResi.length === 0) {
      setError('noResi', 'No. Resi wajib diisi.');
      valid = false; fieldPertama = fieldPertama || 'noResi';
    }
    if (vNama.length === 0) {
      setError('namaAdmin', 'Nama admin wajib diisi (tidak boleh hanya spasi).');
      valid = false; fieldPertama = fieldPertama || 'namaAdmin';
    }
    if (vStatus.length === 0 || CONFIG.ENUM_STATUS.indexOf(vStatus) === -1) {
      setError('statusResi', 'Silakan pilih status yang valid.');
      valid = false; fieldPertama = fieldPertama || 'statusResi';
    }
    if (vLokasi.length === 0) {
      setError('lokasi', 'Catatan lokasi wajib diisi.');
      valid = false; fieldPertama = fieldPertama || 'lokasi';
    }

    return {
      valid: valid,
      fieldPertama: fieldPertama,
      payload: { no_resi: vResi, nama_admin: vNama, status: vStatus, lokasi: vLokasi }
    };
  }

  // ══════════════════════════════════════════════════════════════════════
  // SUBMIT
  // ══════════════════════════════════════════════════════════════════════

  function setSubmitting(sedang) {
    btnSubmit.disabled = sedang;
    spinner.classList.toggle('hidden', !sedang);
    btnSubmitText.textContent = sedang ? 'Mengirim...' : 'Submit Update';
  }

  function resetForm() {
    noResi.value = '';
    statusResi.value = '';
    lokasi.value = '';
    // Nama admin dipertahankan untuk mempercepat entri berikutnya.
    bersihkanSemuaError();
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const v = validasi();
    if (!v.valid) {
      const el = inputEl[v.fieldPertama];
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.focus();
      }
      tampilToast('Periksa kembali isian formulir.', 'error');
      return;
    }

    // Persist nama admin (bukan data sensitif).
    try { localStorage.setItem(CONFIG.ADMIN_NAME_KEY, v.payload.nama_admin); } catch (err) {}

    // Sertakan client_id untuk idempotensi (dipakai bila masuk antrean).
    const entri = { client_id: buatId(), payload: v.payload, dibuat: new Date().toISOString(), status: 'pending' };
    const payloadKirim = Object.assign({ client_id: entri.client_id }, v.payload);

    setSubmitting(true);

    // Jika sudah jelas offline → langsung antre, jangan buang waktu retry.
    if (!navigator.onLine) {
      await antreanSimpan(entri);
      await perbaruiBadgeAntrean();
      setSubmitting(false);
      tampilToast('Tersimpan di perangkat. Akan dikirim otomatis saat koneksi tersedia.', 'info');
      resetForm();
      return;
    }

    try {
      const hasil = await kirimKeServer(payloadKirim);
      if (hasil.ok) {
        const total = hasil.data && hasil.data.data && hasil.data.data.total_riwayat;
        let pesan = `Berhasil! Status ${v.payload.no_resi} diperbarui menjadi "${v.payload.status}".`;
        if (total !== undefined && total !== null) pesan += ` Total ${total} riwayat.`;
        tampilToast(pesan, 'success');
        resetForm();
        // Coba flush entri lama yang mungkin masih pending.
        flushQueue();
      } else {
        // Gagal validasi server — tampilkan pesan, JANGAN diantrekan.
        tampilToast(hasil.pesan, 'error');
      }
    } catch (err) {
      // Gagal jaringan/timeout → simpan ke antrean offline.
      await antreanSimpan(entri);
      await perbaruiBadgeAntrean();
      tampilToast('Gagal terkirim (jaringan). Data tersimpan di HP ini dan akan dikirim otomatis saat koneksi tersedia.', 'error');
      resetForm();
    } finally {
      setSubmitting(false);
    }
  });

  // Bersihkan error saat pengguna mulai memperbaiki field.
  Object.keys(inputEl).forEach((f) => {
    inputEl[f].addEventListener('input', () => bersihkanError(f));
    inputEl[f].addEventListener('change', () => bersihkanError(f));
  });

  // ══════════════════════════════════════════════════════════════════════
  // STATUS KONEKSI
  // ══════════════════════════════════════════════════════════════════════

  function perbaruiBannerOffline() {
    offlineBanner.classList.toggle('hidden', navigator.onLine);
  }

  window.addEventListener('online', () => {
    perbaruiBannerOffline();
    tampilToast('Koneksi kembali. Mengirim antrean...', 'info');
    flushQueue();
  });
  window.addEventListener('offline', perbaruiBannerOffline);

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
  // INISIALISASI SAAT HALAMAN DIBUKA
  // ══════════════════════════════════════════════════════════════════════

  // Muat nama admin tersimpan.
  try {
    const namaTersimpan = localStorage.getItem(CONFIG.ADMIN_NAME_KEY);
    if (namaTersimpan) namaAdmin.value = namaTersimpan;
  } catch (e) {}

  perbaruiBannerOffline();
  perbaruiBadgeAntrean();
  // Kirim ulang antrean tertunda saat halaman dibuka (penting untuk iOS
  // yang tidak punya Background Sync API).
  flushQueue();
})();
