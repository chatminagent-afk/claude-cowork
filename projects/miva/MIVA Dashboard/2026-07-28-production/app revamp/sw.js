/* ============================================================================
 * sw.js — SERVICE WORKER
 *
 * Aturan yang mengikat:
 *   - Aset statis (isi folder ini): cache-first, lalu diperbarui diam-diam di
 *     latar belakang supaya deploy berikutnya tidak tertahan cache lama.
 *   - Request API: network-only. Tidak pernah dibaca dari cache dan tidak
 *     pernah ditulis ke cache. Respons `stats` memuat direktori lead lengkap;
 *     menyimpannya di Cache Storage berarti data lead tertinggal di perangkat
 *     setelah pengguna keluar.
 *   - Nama cache berversi. Naikkan CACHE_VERSION setiap kali berkas di folder
 *     ini berubah, supaya klien lama tidak menyajikan berkas basi.
 *
 * Awalan nama cache SENGAJA berbeda dari versi `app/` ('vira-dash-').
 * Kalau keduanya memakai awalan yang sama dan disajikan dari origin yang sama,
 * service worker versi lama akan menghapus cache versi ini setiap kali
 * halaman lamanya dibuka — aturan pembersihannya menyapu seluruh awalan.
 * ========================================================================== */
'use strict';

var CACHE_VERSION = 'v1.4.0';
var CACHE_PREFIX = 'vira-revamp-';
var CACHE_NAME = CACHE_PREFIX + CACHE_VERSION;

/*
 * Hanya kerangka aplikasi. Logo tenant SENGAJA tidak ada di sini: berkas mana
 * yang dipakai baru diketahui setelah server mengirim deskriptor tenant, dan
 * mencantumkannya berarti service worker harus tahu daftar klien — persis
 * kopling yang mau dihindari. Tidak ada yang hilang: handler `fetch` di bawah
 * sudah cache-first untuk semua GET se-origin, jadi logo ikut tersimpan
 * sendiri setelah sekali tampil.
 *
 * Konsekuensinya, kunjungan PERTAMA dalam keadaan offline penuh menampilkan
 * emblem huruf alih-alih logo. Itu keadaan yang mustahil dalam praktik —
 * deskriptor tenant sendiri baru datang dari jaringan.
 */
var PRECACHE = [
  './',
  './manifest.webmanifest',
  './css/app.css',
  './js/config.js',
  './js/api.js',
  './js/charts.js',
  './js/render.js',
  './js/app.js',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

self.addEventListener('install', function (ev) {
  ev.waitUntil(
    caches.open(CACHE_NAME)
      .then(function (c) { return c.addAll(PRECACHE); })
      .then(function () { return self.skipWaiting(); })
      .catch(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (ev) {
  ev.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        // Hanya cache milik versi ini yang boleh disentuh.
        if (k !== CACHE_NAME && k.indexOf(CACHE_PREFIX) === 0) return caches.delete(k);
        return null;
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

/**
 * Sebuah request dianggap API kalau bukan GET, atau kalau bukan berasal dari
 * origin halaman ini. Kedua syarat itu menutup panggilan webhook (POST, lintas
 * origin) tanpa perlu tahu URL-nya — yang penting, alamat API bisa diganti
 * lewat konfigurasi dan service worker tetap benar.
 */
function isApiRequest(req) {
  if (req.method !== 'GET') return true;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return true;
  return false;
}

self.addEventListener('fetch', function (ev) {
  var req = ev.request;

  if (isApiRequest(req)) return;              // network-only, tanpa campur tangan

  var url = new URL(req.url);
  // Query string (mis. ?api=) tidak boleh membuat entri cache terpisah.
  var keyReq = new Request(url.origin + url.pathname, { method: 'GET' });

  ev.respondWith(
    caches.match(keyReq).then(function (hit) {
      var net = fetch(req).then(function (res) {
        if (res && res.ok && res.type === 'basic') {
          var copy = res.clone();
          caches.open(CACHE_NAME).then(function (c) { c.put(keyReq, copy); });
        }
        return res;
      }).catch(function () { return hit; });

      // Cache-first: kalau ada salinan, pakai; pembaruan jalan di belakang.
      return hit || net;
    })
  );
});
