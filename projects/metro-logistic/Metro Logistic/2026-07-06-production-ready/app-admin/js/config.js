/*
 * config.js — Konfigurasi APP ADMIN LAPANGAN — Metro Logistik Tracking.
 * (Redesain & Mode Uji Dummy oleh Antigravity — QA & production-fix 2026-07-06)
 */

'use strict';

// ── URL Webhook n8n (GANTI dengan domain n8n Anda saat deploy) ──────────────
// APP ADMIN: hanya endpoint UPDATE. Endpoint GET tidak diperlukan di sini.
const N8N_UPDATE_URL = 'https://n8n.srv1270416.hstgr.cloud/webhook/tracking-update';

const CONFIG = {
  // ── Mode Uji Dummy ────────────────────────────────────────────────────────
  // PRODUKSI: false (terhubung ke webhook n8n asli).
  // Ubah ke true HANYA untuk demo/uji offline dengan data dummy interaktif.
  TEST_DUMMY: true,

  N8N_UPDATE_URL: N8N_UPDATE_URL,
  API_UPDATE_URL: N8N_UPDATE_URL,

  // Deteksi apakah URL n8n masih placeholder (belum dikonfigurasi ke server asli).
  // Dipakai untuk menampilkan pesan error yang jelas alih-alih retry percuma.
  ENDPOINT_BELUM_DIKONFIGURASI: N8N_UPDATE_URL.indexOf('DOMAIN-N8N-ANDA') !== -1,

  // ── Parameter Jaringan (Sinyal Lemah) ─────────────────────────────────────
  FETCH_TIMEOUT_MS: 8000,
  MAX_RETRY: 2,
  RETRY_BACKOFF_MS: 1500,

  // ── Penyimpanan Lokal ──────────────────────────────────────────────────────
  OFFLINE_QUEUE_KEY: 'metro_admin_queue_redesign',
  ADMIN_NAME_KEY: 'metro_admin_name_redesign',
  DUMMY_STORAGE_KEY: 'metro_dummy_data_storage', // Untuk menyimpan status dummy yang diupdate

  APP_NAME: 'Metro Logistik Indonesia',

  // ── Kamus Pesan Error Terpusat (Bahasa Indonesia) ─────────────────────────
  // Pesan seragam & mudah dipelihara dari satu tempat.
  ERROR_MESSAGES: {
    // ── Validasi input umum ──
    RESI_KOSONG: 'Masukkan minimal satu nomor resi.',
    RESI_FORMAT_TIDAK_VALID: 'Format nomor resi tidak valid. Gunakan huruf/angka tanpa spasi.',

    // ── Form admin ──
    ADMIN_RESI_KOSONG: 'Nomor Resi harus diisi.',
    ADMIN_NAMA_KOSONG: 'Nama admin harus diisi.',
    ADMIN_STATUS_KOSONG: 'Pilih salah satu status yang valid.',
    ADMIN_LOKASI_KOSONG: 'Detail posisi/lokasi saat ini wajib dicatat.',
    ADMIN_FORM_TIDAK_VALID: 'Periksa kembali isian formulir sebelum mengirim.',

    // ── Jaringan & server ──
    TIDAK_ADA_KONEKSI: 'Tidak ada koneksi internet. Periksa jaringan Wi-Fi/seluler Anda.',
    TIMEOUT_SERVER: 'Server tidak merespons (timeout). Coba lagi dalam beberapa saat.',
    SERVER_ERROR: 'Terjadi kesalahan pada server. Coba lagi nanti atau hubungi admin.',
    RESPON_TIDAK_VALID: 'Menerima respons yang tidak dapat dibaca dari server.',
    ENDPOINT_BELUM_DIKONFIGURASI: 'Sistem belum terhubung ke server (endpoint belum dikonfigurasi). Hubungi tim teknis.',
    GAGAL_KIRIM_ANTRE: 'Gagal terkirim karena kendala jaringan. Data disimpan di perangkat ini dan akan dikirim otomatis saat koneksi tersedia.',
    GAGAL_KIRIM_OFFLINE: 'Sedang offline. Data disimpan di perangkat ini dan akan dikirim otomatis saat internet aktif.',

    // ── Filter tanpa pencarian ──
    FILTER_PERLU_PENCARIAN: 'Belum ada resi yang dicari. Masukkan nomor resi dan klik "Mulai Lacak" terlebih dahulu, baru terapkan filter.',

    // ── Data / hasil pelacakan ──
    RESI_TIDAK_DITEMUKAN: 'Nomor resi tidak terdaftar. Periksa kembali atau hubungi CS.',
    RIWAYAT_BERMASALAH: 'Data riwayat bermasalah. Mohon maaf, kami tidak dapat menampilkan detail perjalanan untuk resi ini.',
    TIDAK_ADA_RIWAYAT: 'Belum ada riwayat pengiriman.',
    FILTER_TIDAK_COCOK: 'Tidak ada riwayat yang cocok dengan filter.',
    FILTER_CARD_TIDAK_COCOK: 'Tidak ada riwayat pengiriman yang cocok dengan filter tanggal atau status Anda.',

    // ── Penyimpanan lokal ──
    PENYIMPANAN_LOKAL_GAGAL: 'Penyimpanan lokal perangkat tidak tersedia (mode privat/penuh). Sebagian fitur offline mungkin terbatas.',

    // ── Fallback umum ──
    ERROR_TIDAK_DIKETAHUI: 'Terjadi kesalahan yang tidak diketahui. Silakan coba lagi.'
  },

  ENUM_STATUS: [
    'Manifest',
    'On Process',
    'Transit',
    'Out for Delivery',
    'Delivered',
    'Failed/Return'
  ]
};

// Ekspor ke lingkungan browser
if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
}
