/* Kertas service worker — app shell cache so the app opens instantly and
   keeps working with no signal. Data lives in localStorage, never here. */
const CACHE = "kertas-v3";
const SHELL = ["./", "./index.html", "./manifest.json", "./icon.svg",
  "./icon-192.png", "./icon-512.png",
  "./icon-maskable-192.png", "./icon-maskable-512.png", "./apple-touch-icon.png"];

/* addAll() bersifat semua-atau-tidak: satu berkas 404 membuat SELURUH
   pemasangan service worker gagal — dan tanpa service worker, Chrome tidak
   pernah menawarkan "Install app". Karena itu tiap berkas di-cache sendiri
   dan kegagalan satu berkas tidak menjatuhkan yang lain. */
self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await Promise.all(SHELL.map((u) => c.add(u).catch(() => {})));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Fonts are cached so the app still looks like itself with no signal.
const FONT_HOSTS = ["fonts.googleapis.com", "fonts.gstatic.com"];
// These must never be served from cache — a stale token or a stale Drive
// response is worse than an honest failure.
const LIVE_HOSTS = ["www.googleapis.com", "accounts.google.com", "oauth2.googleapis.com"];

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (LIVE_HOSTS.includes(url.hostname)) return;
  if (e.request.method !== "GET") return;

  // Fonts: cache first, they never change.
  if (FONT_HOSTS.includes(url.hostname)) {
    e.respondWith(
      caches.match(e.request).then((hit) =>
        hit || fetch(e.request).then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
          return res;
        }).catch(() => hit)
      )
    );
    return;
  }

  // Network first for the shell, so a redeploy is picked up; cache is the fallback.
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(e.request).then((r) => r || caches.match("./index.html")))
  );
});
