/*
 * Service Worker — Metro Logistik Tracking PWA
 * (Redesain & Mode Uji Dummy oleh Antigravity)
 */

'use strict';

const CACHE_VERSION = 'v1.1.0-redesign';
const SHELL_CACHE = `metrotrack-shell-${CACHE_VERSION}`;
const API_CACHE = `metrotrack-api-${CACHE_VERSION}`;

const NETWORK_TIMEOUT_MS = 5000;

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

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(SHELL_CACHE);
      await Promise.all(
        APP_SHELL.map(async (url) => {
          try {
            await cache.add(new Request(url, { cache: 'reload' }));
          } catch (err) {
            console.warn('[SW] Gagal precache (dilewati):', url, err);
          }
        })
      );
      await self.skipWaiting();
    })()
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.map((key) => {
          const milikApp = key.startsWith('metrotrack-');
          const versiSaatIni = key === SHELL_CACHE || key === API_CACHE;
          if (milikApp && !versiSaatIni) {
            console.log('[SW] Menghapus cache lama:', key);
            return caches.delete(key);
          }
          return Promise.resolve();
        })
      );
      await self.clients.claim();
    })()
  );
});

function isApiRequest(url) {
  return (
    url.pathname.includes('/webhook/tracking-get') ||
    url.pathname.includes('/webhook/tracking-update') ||
    url.pathname.includes('/webhook-test/tracking-get') ||
    url.pathname.includes('/webhook-test/tracking-update')
  );
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  if (req.method !== 'GET') {
    return;
  }

  if (isApiRequest(url)) {
    event.respondWith(networkFirstDenganTimeout(req));
    return;
  }

  if (url.origin === self.location.origin) {
    event.respondWith(cacheFirst(req));
    return;
  }
});

async function cacheFirst(req) {
  const cache = await caches.open(SHELL_CACHE);
  const cached = await cache.match(req, { ignoreSearch: false });
  if (cached) {
    return cached;
  }
  try {
    const resp = await fetch(req);
    if (resp && resp.status === 200 && resp.type === 'basic') {
      cache.put(req, resp.clone());
    }
    return resp;
  } catch (err) {
    if (req.mode === 'navigate') {
      const fallback = await cache.match('./index.html');
      if (fallback) return fallback;
    }
    throw err;
  }
}

async function networkFirstDenganTimeout(req) {
  const cache = await caches.open(API_CACHE);

  try {
    const networkResp = await fetchDenganTimeout(req, NETWORK_TIMEOUT_MS);
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
