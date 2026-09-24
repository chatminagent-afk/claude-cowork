const CACHE = 'tim-interior-v3';
const ASSETS = [
  './index.html',
  './manifest.json',
  './logo_tim.jpg',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png'
];

// Install: cache shell assets
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).catch(() => {})
  );
});

// Activate: drop old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => clients.claim())
  );
});

// Fetch: network-first for API calls, cache-first for assets
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);

  // Always go to network for n8n API calls
  if (url.hostname.includes('hstgr') || url.hostname.includes('n8n')) return;

  e.respondWith(
    fetch(e.request)
      .then(res => {
        // Cache successful responses for app assets
        if (res.ok && url.origin === self.location.origin) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
