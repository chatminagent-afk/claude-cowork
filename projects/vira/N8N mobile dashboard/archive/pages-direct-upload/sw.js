/**
 * Service worker n8n Ops.
 *
 * Tugasnya cuma bikin shell app (HTML, ikon, CDN) tetap kebuka saat sinyal
 * jelek. Data n8n TIDAK PERNAH di-cache — dashboard monitoring yang
 * menampilkan angka basi lebih berbahaya daripada yang jujur bilang offline.
 */

const CACHE = 'n8n-ops-v1';
const SHELL = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/icon-192.png',
  '/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(SHELL))
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Request ke proxy n8n: selalu jaringan, jangan disentuh cache.
  if (url.origin === self.location.origin && url.pathname.startsWith('/n8n/')) return;

  // Navigasi: jaringan dulu, jatuh ke shell kalau offline.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() => caches.match('/index.html').then(r => r || Response.error()))
    );
    return;
  }

  // Aset (ikon, Vue/Tailwind dari CDN): cache dulu, lalu isi diam-diam.
  event.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    try {
      const res = await fetch(req);
      if (res && res.ok && (url.origin === self.location.origin || res.type === 'cors')) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
      }
      return res;
    } catch (err) {
      return cached || Response.error();
    }
  })());
});
