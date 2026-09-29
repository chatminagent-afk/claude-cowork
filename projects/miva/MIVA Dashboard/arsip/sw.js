/* VIRA Performance & CRM Dashboard — Service Worker (PWA)
 * Caches app shell, database engine, and database.json for instant offline access.
 * API network calls bypass cache for real-time live data.
 */
const CACHE_NAME = "vira-dashboard-v2";
const SHELL_ASSETS = [
  "./",
  "./index.html",
  "./db-store.js",
  "./database.json",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).catch(() => caches.match("./index.html"));
    })
  );
});
