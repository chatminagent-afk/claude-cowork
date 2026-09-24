/*
 * admin.js — Logika Halaman Admin Lapangan (Metro Logistik Tracking)
 * (Redesain & Mode Uji Dummy oleh Antigravity)
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
  const loadingOverlay = $('loadingOverlay');
  const loadingOverlayText = $('loadingOverlayText');
  const successModal = $('successModal');
  const successModalText = $('successModalText');
  const btnSuccessModalClose = $('btnSuccessModalClose');

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

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function buatId() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'id-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
  }

  let toastTimer = null;
  function tampilToast(pesan, tipe) {
    const warna = tipe === 'error' ? 'bg-rose-600' : tipe === 'success' ? 'bg-emerald-600' : 'bg-slate-900';
    toast.className = `fixed left-1/2 -translate-x-1/2 bottom-6 z-50 max-w-[92%] w-max px-5 py-3.5 rounded-xl shadow-xl text-sm font-medium text-white transition-all duration-300 scale-95 opacity-0 ${warna}`;
    toast.textContent = pesan;
    toast.classList.remove('hidden');
    
    void toast.offsetWidth;
    toast.classList.add('scale-100', 'opacity-100');

    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove('scale-100', 'opacity-100');
      toast.classList.add('scale-95', 'opacity-0');
      setTimeout(() => toast.classList.add('hidden'), 300);
    }, 4000);
  }

  function tidur(ms) { return new Promise((r) => setTimeout(r, ms)); }

  // ══════════════════════════════════════════════════════════════════════
  // OVERLAY LOADING (blur layar) & MODAL POP-UP BERHASIL
  // ══════════════════════════════════════════════════════════════════════

  function tampilLoadingOverlay(pesan) {
    loadingOverlayText.textContent = pesan || 'Mengirim pembaruan...';
    loadingOverlay.classList.remove('hidden');
    loadingOverlay.classList.add('flex');
  }

  function tutupLoadingOverlay() {
    loadingOverlay.classList.add('hidden');
    loadingOverlay.classList.remove('flex');
  }

  function tampilSuccessModal(pesan) {
    successModalText.textContent = pesan;
    successModal.classList.remove('hidden');
    successModal.classList.add('flex');
  }

  function tutupSuccessModal() {
    successModal.classList.add('hidden');
    successModal.classList.remove('flex');
  }

  if (btnSuccessModalClose) {
    btnSuccessModalClose.addEventListener('click', () => {
      tutupSuccessModal();
      noResi.focus();
    });
  }

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

  const DB_NAME = 'metro_admin_queue_db_redesign';
  const STORE = 'pending_updates_redesign';
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

  function lsBaca() {
    try {
      const raw = localStorage.getItem(CONFIG.OFFLINE_QUEUE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) { return []; }
  }
  function lsTulis(arr) {
    try { localStorage.setItem(CONFIG.OFFLINE_QUEUE_KEY, JSON.stringify(arr)); } catch (e) {}
  }

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
      } catch (e) {}
    }
    const arr = lsBaca();
    if (!arr.some((x) => x.client_id === entri.client_id)) arr.push(entri);
    lsTulis(arr);
  }

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

  async function perbaruiBadgeAntrean() {
    const n = await antreanJumlah();
    if (n > 0) {
      antreanBadge.classList.remove('hidden');
      antreanBadge.classList.add('flex');
      antreanText.textContent = `${n} update tertunda menunggu jaringan.`;
    } else {
      antreanBadge.classList.add('hidden');
      antreanBadge.classList.remove('flex');
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  // KIRIM ke server (dipakai submit langsung & flushQueue)
  // ══════════════════════════════════════════════════════════════════════

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

    // Error server (5xx) dianggap SEMENTARA → lempar error supaya data masuk
    // antrean offline dan dicoba ulang, BUKAN dihapus seperti error validasi.
    if (resp.status >= 500) {
      throw new Error(CONFIG.ERROR_MESSAGES.SERVER_ERROR);
    }

    if (!resp.ok && !data) {
      return { ok: false, validasi: true, pesan: CONFIG.ERROR_MESSAGES.RESPON_TIDAK_VALID };
    }
    // n8n dapat mengirim field `message` ataupun `error` — terima keduanya.
    return {
      ok: false,
      validasi: true,
      pesan: (data && (data.message || data.error)) ? (data.message || data.error) : CONFIG.ERROR_MESSAGES.SERVER_ERROR
    };
  }

  let sedangFlush = false;
  async function flushQueue() {
    if (CONFIG.TEST_DUMMY) return; // Tidak flushing antrean jika sedang uji dummy
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
            await antreanHapus(entri.client_id);
          }
        } catch (e) {
          break;
        }
      }
      await perbaruiBadgeAntrean();
      if (terkirim > 0) {
        tampilToast(`${terkirim} update tertunda berhasil disinkronkan.`, 'success');
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
    inputEl[field].classList.add('border-rose-400', 'ring-2', 'ring-rose-100');
    inputEl[field].classList.remove('border-slate-200');
  }
  function bersihkanError(field) {
    errEl[field].classList.add('hidden');
    inputEl[field].classList.remove('border-rose-400', 'ring-2', 'ring-rose-100');
    inputEl[field].classList.add('border-slate-200');
  }
  function bersihkanSemuaError() {
    Object.keys(errEl).forEach(bersihkanError);
  }

  function validasi() {
    bersihkanSemuaError();
    let valid = true;
    let fieldPertama = null;

    const vResi = (noResi.value || '').trim().toUpperCase();
    const vNama = (namaAdmin.value || '').trim();
    const vStatus = statusResi.value || '';
    const vLokasi = (lokasi.value || '').trim();

    if (vResi.length === 0) {
      setError('noResi', CONFIG.ERROR_MESSAGES.ADMIN_RESI_KOSONG);
      valid = false; fieldPertama = fieldPertama || 'noResi';
    }
    if (vNama.length === 0) {
      setError('namaAdmin', CONFIG.ERROR_MESSAGES.ADMIN_NAMA_KOSONG);
      valid = false; fieldPertama = fieldPertama || 'namaAdmin';
    }
    if (vStatus.length === 0 || CONFIG.ENUM_STATUS.indexOf(vStatus) === -1) {
      setError('statusResi', CONFIG.ERROR_MESSAGES.ADMIN_STATUS_KOSONG);
      valid = false; fieldPertama = fieldPertama || 'statusResi';
    }
    if (vLokasi.length === 0) {
      setError('lokasi', CONFIG.ERROR_MESSAGES.ADMIN_LOKASI_KOSONG);
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
    btnSubmitText.textContent = sedang ? 'Mengirim data...' : 'Submit Update';
    if (sedang) {
      btnSubmit.classList.add('opacity-75', 'cursor-not-allowed');
    } else {
      btnSubmit.classList.remove('opacity-75', 'cursor-not-allowed');
    }
  }

  function resetForm() {
    noResi.value = '';
    statusResi.value = '';
    lokasi.value = '';
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
      tampilToast(CONFIG.ERROR_MESSAGES.ADMIN_FORM_TIDAK_VALID, 'error');
      return;
    }

    try { localStorage.setItem(CONFIG.ADMIN_NAME_KEY, v.payload.nama_admin); } catch (err) {}

    // ── INTERCEPTOR DUMMY MODE ──
    if (CONFIG.TEST_DUMMY) {
      setSubmitting(true);
      tampilLoadingOverlay('Menyimpan pembaruan (Mode Uji)...');
      await tidur(800); // Simulasi delay loading

      try {
        let localUpdates = [];
        try {
          const raw = localStorage.getItem(CONFIG.DUMMY_STORAGE_KEY);
          if (raw) localUpdates = JSON.parse(raw);
        } catch (e) {}

        localUpdates.push({
          no_resi: v.payload.no_resi.toUpperCase(),
          status: v.payload.status,
          lokasi: v.payload.lokasi,
          nama_admin: v.payload.nama_admin,
          waktu: new Date().toISOString()
        });

        localStorage.setItem(CONFIG.DUMMY_STORAGE_KEY, JSON.stringify(localUpdates));

        resetForm();
        tampilSuccessModal(`(Mode Uji) Status ${v.payload.no_resi} berhasil diperbarui menjadi "${v.payload.status}".`);
      } catch (err) {
        tampilToast(CONFIG.ERROR_MESSAGES.PENYIMPANAN_LOKAL_GAGAL, 'error');
      } finally {
        tutupLoadingOverlay();
        setSubmitting(false);
      }
      return;
    }

    // ── Endpoint belum dikonfigurasi → beri tahu jelas, jangan pura-pura sukses ──
    if (CONFIG.ENDPOINT_BELUM_DIKONFIGURASI) {
      tampilToast(CONFIG.ERROR_MESSAGES.ENDPOINT_BELUM_DIKONFIGURASI, 'error');
      return;
    }

    const entri = { client_id: buatId(), payload: v.payload, dibuat: new Date().toISOString(), status: 'pending' };
    const payloadKirim = Object.assign({ client_id: entri.client_id }, v.payload);

    setSubmitting(true);
    tampilLoadingOverlay('Mengirim pembaruan...');

    if (!navigator.onLine) {
      await antreanSimpan(entri);
      await perbaruiBadgeAntrean();
      tutupLoadingOverlay();
      setSubmitting(false);
      resetForm();
      tampilSuccessModal(CONFIG.ERROR_MESSAGES.GAGAL_KIRIM_OFFLINE);
      return;
    }

    try {
      const hasil = await kirimKeServer(payloadKirim);
      if (hasil.ok) {
        const d = hasil.data || {};
        const total = (d.total_riwayat !== undefined && d.total_riwayat !== null)
          ? d.total_riwayat
          : (d.data && d.data.total_riwayat);
        let pesan = `Status ${v.payload.no_resi} berhasil diperbarui menjadi "${v.payload.status}" dan tersimpan ke Google Sheet.`;
        if (total !== undefined && total !== null) pesan += ` Total ${total} riwayat.`;
        resetForm();
        tampilSuccessModal(pesan);
        flushQueue();
      } else {
        tampilToast(hasil.pesan || CONFIG.ERROR_MESSAGES.SERVER_ERROR, 'error');
      }
    } catch (err) {
      await antreanSimpan(entri);
      await perbaruiBadgeAntrean();
      resetForm();
      tampilSuccessModal(CONFIG.ERROR_MESSAGES.GAGAL_KIRIM_ANTRE);
    } finally {
      tutupLoadingOverlay();
      setSubmitting(false);
    }
  });

  Object.keys(inputEl).forEach((f) => {
    inputEl[f].addEventListener('input', () => bersihkanError(f));
    inputEl[f].addEventListener('change', () => bersihkanError(f));
  });

  // ══════════════════════════════════════════════════════════════════════
  // STATUS KONEKSI
  // ══════════════════════════════════════════════════════════════════════

  function perbaruiBannerOffline() {
    if (CONFIG.TEST_DUMMY) return; // Abaikan banner jika mode dummy aktif
    if (navigator.onLine) {
      offlineBanner.classList.add('hidden');
      offlineBanner.classList.remove('flex');
    } else {
      offlineBanner.classList.remove('hidden');
      offlineBanner.classList.add('flex');
    }
  }

  window.addEventListener('online', () => {
    perbaruiBannerOffline();
    if (!CONFIG.TEST_DUMMY) {
      tampilToast('Terhubung kembali ke internet. Sinkronisasi antrean...', 'info');
      flushQueue();
    }
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
  // INISIALISASI
  // ══════════════════════════════════════════════════════════════════════

  try {
    const namaTersimpan = localStorage.getItem(CONFIG.ADMIN_NAME_KEY);
    if (namaTersimpan) namaAdmin.value = namaTersimpan;
  } catch (e) {}

  perbaruiBannerOffline();
  perbaruiBadgeAntrean();
  
  if (!CONFIG.TEST_DUMMY) {
    flushQueue();
  }
})();
