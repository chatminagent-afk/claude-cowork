/*
 * config.js — Konfigurasi endpoint API untuk PWA Metro Logistik Tracking.
 * -----------------------------------------------------------------------
 * ISI URL di bawah dengan URL webhook n8n Anda (lihat n8n/README setup).
 * File ini di-precache oleh service worker sebagai bagian dari app shell.
 *
 * PENYELARASAN FASE B: nama konstanta diselaraskan dengan rancangan arsitektur
 * Sonnet (N8N_GET_URL / N8N_UPDATE_URL + parameter jaringan). Nama lama Fase A
 * (API_GET_URL / API_UPDATE_URL) tetap dipertahankan sebagai alias agar tidak
 * memecah referensi apa pun yang mungkin sudah ada.
 *
 * CATATAN: nilai URL di bawah masih placeholder. Ganti dengan URL production
 * n8n Anda sebelum deploy.
 */

'use strict';

// ── URL Webhook n8n (SATU-SATUNYA tempat URL disimpan) ──────────────────────
// WF1 (GET) — endpoint pencarian data resi.
const N8N_GET_URL = 'https://DOMAIN-N8N-ANDA/webhook/tracking-get';
// WF2 (POST) — endpoint update status resi.
const N8N_UPDATE_URL = 'https://DOMAIN-N8N-ANDA/webhook/tracking-update';

const CONFIG = {
  // Nama sesuai rancangan Sonnet (dipakai tracking.js & admin.js).
  N8N_GET_URL: N8N_GET_URL,
  N8N_UPDATE_URL: N8N_UPDATE_URL,

  // Alias nama lama Fase A (kompatibilitas mundur).
  API_GET_URL: N8N_GET_URL,
  API_UPDATE_URL: N8N_UPDATE_URL,

  // ── Parameter ketahanan jaringan (sinyal lemah) ──────────────────────────
  FETCH_TIMEOUT_MS: 8000,     // batas waktu tunggu 1 request (2G/3G lemah)
  MAX_RETRY: 2,               // percobaan ulang otomatis saat gagal/timeout
  RETRY_BACKOFF_MS: 1500,     // jeda dasar antar-retry (bertahap: 1.5s, 3s)

  // ── Kunci penyimpanan lokal ──────────────────────────────────────────────
  CACHE_KEY_PREFIX: 'metro_track_',        // prefix key cache hasil lacak (localStorage)
  OFFLINE_QUEUE_KEY: 'metro_admin_queue',  // key cadangan antrean update (localStorage)
  ADMIN_NAME_KEY: 'metro_admin_name',      // key nama admin yang dipersist

  APP_NAME: 'Metro Logistik Indonesia',

  // Daftar enum status resmi (dipakai UI untuk validasi & dropdown admin).
  // Harus identik persis (kapitalisasi & spasi) dengan skema database.
  ENUM_STATUS: [
    'Manifest',
    'On Process',
    'Transit',
    'Out for Delivery',
    'Delivered',
    'Failed/Return'
  ]
};

// Ekspor ke lingkungan browser (window) & module (jika ada).
if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
}
