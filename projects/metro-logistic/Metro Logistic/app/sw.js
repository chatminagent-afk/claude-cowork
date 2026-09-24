/*
 * Service Worker — Metro Logistik Tracking PWA
 * ---------------------------------------------
 * Strategi:
 *  - App shell (HTML, JS, ikon, manifest): cache-first (cepat, offline-ready).
 *  - Request GET ke API n8n (webhook tracking-get): network-first dengan
 *    timeout, fallback ke cache bila jaringan lambat/putus.
 *  - Request POST (mis. tracking-update): TIDAK di-cache, selalu ke jaringan.
 *  - Cache versioned: saat versi dinaikkan, cache lama dihapus di 'activate'.
 *
 * CATATAN: Naikkan CACHE_VERSION setiap kali app shell berubah agar
 * service worker memicu update dan membersihkan cache lama.
 */

'use strict';

// Versi cache — ubah nilai ini untuk memaksa pembaruan cache di klien.
const CACHE_VERSION = 'v1.0.0';
const SHELL_CACHE = `metrotrack-shell-${CACHE_VERSION}`;
const API_CACHE = `metrotrack-api-${CACHE_VERSION}`;

// Batas waktu (ms) menunggu jaringan sebelum jatuh ke cache untuk API GET.
const NETWORK_TIMEOUT_MS = 5000;

// Daftar aset app shell yang di-precache saat instalasi.
// Path relatif terhadap scope service worker (folder /app/).
const APP_SHELL = [
  './',
  './index.html',
  './admin.html',
  './manifest.json',
  './js/config.js',
  './js/tracking.js',
  './js/admin.js',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-192.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png'
];

/* =========================================================
 * INSTALL — precache app shell.
 * ========================================================= */
self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(SHELL_CACHE);
      // addAll gagal-atomik; agar 1 file hilang tidak menggagalkan seluruh
      // instalasi, kita cache satu per satu dan abaikan yang gagal (mis. file
      // HTML belum dibuat pada Fase A). Aset inti tetap tercache bila ada.
      await Promise.all(
        APP_SHELL.map(async (url) => {
          try {
            await cache.add(new Request(url, { cache: 'reload' }));
          } catch (err) {
            console.warn('[SW] Gagal precache (dilewati):', url, err);
          }
        })
      );
      // Aktifkan service worker baru segera tanpa menunggu tab lama tertutup.
      await self.skipWaiting();
    })()
  );
});

/* =========================================================
 * ACTIVATE — hapus cache versi lama & klaim klien.
 * ========================================================= */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.map((key) => {
          // Hapus cache milik app ini yang bukan versi saat ini.
          const milikApp = key.startsWith('metrotrack-');
          const versiSaatIni = key === SHELL_CACHE || key === API_CACHE;
          if (milikApp && !versiSaatIni) {
            console.log('[SW] Menghapus cache lama:', key);
            return caches.delete(key);
          }
          return Promise.resolve();
        })
      );
      // Ambil kendali atas semua klien yang sedang terbuka.
      await self.clients.claim();
    })()
  );
});

/* =========================================================
 * Deteksi apakah sebuah request adalah panggilan API n8n.
 * Disesuaikan dengan path webhook n8n (tracking-get / tracking-update).
 * ========================================================= */
function isApiRequest(url) {
  return (
    url.pathname.includes('/webhook/tracking-get') ||
    url.pathname.includes('/webhook/tracking-update') ||
    url.pathname.includes('/webhook-test/tracking-get') ||
    url.pathname.includes('/webhook-test/tracking-update')
  );
}

/* =========================================================
 * FETCH — router strategi caching.
 * ========================================================= */
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // 1. JANGAN cache request non-GET (POST update, dsb). Selalu ke jaringan.
  if (req.method !== 'GET') {
    return; // biarkan browser menangani request seperti biasa.
  }

  // 2. API GET n8n → network-first dengan timeout, fallback ke cache.
  if (isApiRequest(url)) {
    event.respondWith(networkFirstDenganTimeout(req));
    return;
  }

  // 3. Hanya tangani request same-origin untuk app shell.
  if (url.origin === self.location.origin) {
    event.respondWith(cacheFirst(req));
    return;
  }

  // 4. Lainnya (cross-origin non-API): biarkan default.
});

/* =========================================================
 * Strategi CACHE-FIRST untuk app shell.
 * ========================================================= */
async function cacheFirst(req) {
  const cache = await caches.open(SHELL_CACHE);
  const cached = await cache.match(req, { ignoreSearch: false });
  if (cached) {
    return cached;
  }
  try {
    const resp = await fetch(req);
    // Simpan salinan bila respons valid & same-origin.
    if (resp && resp.status === 200 && resp.type === 'basic') {
      cache.put(req, resp.clone());
    }
    return resp;
  } catch (err) {
    // Offline & tidak ada di cache. Coba fallback ke index.html untuk
    // navigasi (SPA-style), jika tersedia.
    if (req.mode === 'navigate') {
      const fallback = await cache.match('./index.html');
      if (fallback) return fallback;
    }
    throw err;
  }
}

/* =========================================================
 * Strategi NETWORK-FIRST dengan timeout untuk API GET.
 * Bila jaringan gagal / lewat batas waktu → pakai cache terakhir.
 * ========================================================= */
async function networkFirstDenganTimeout(req) {
  const cache = await caches.open(API_CACHE);

  try {
    const networkResp = await fetchDenganTimeout(req, NETWORK_TIMEOUT_MS);
    // Simpan salinan respons segar untuk fallback offline berikutnya.
    if (networkResp && networkResp.status === 200) {
      cache.put(req, networkResp.clone());
    }
    return networkResp;
  } catch (err) {
    console.warn('[SW] API network gagal/timeout, coba cache:', err);
    const cached = await cache.match(req);
    if (cached) {
      return cached;
    }
    // Tidak ada jaringan & tidak ada cache → kembalikan JSON error terstruktur.
    return new Response(
      JSON.stringify({
        error: true,
        offline: true,
        message: 'Tidak ada koneksi dan data belum tersimpan di cache.'
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

/* =========================================================
 * fetch() dengan batas waktu via AbortController.
 * ========================================================= */
function fetchDenganTimeout(req, timeoutMs) {
  return new Promise((resolve, reject) => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      controller.abort();
      reject(new Error('Batas waktu jaringan tercapai'));
    }, timeoutMs);

    fetch(req, { signal: controller.signal })
      .then((resp) => {
        clearTimeout(timer);
        resolve(resp);
      })
      .catch((err) => {
        clearTimeout(timer);
        reject(err);
      });
  });
}
