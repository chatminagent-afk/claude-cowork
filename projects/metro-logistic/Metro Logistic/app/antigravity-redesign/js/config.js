/*
 * config.js — Konfigurasi endpoint API untuk PWA Metro Logistik Tracking.
 * (Redesain & Mode Uji Dummy oleh Antigravity)
 */

'use strict';

// ── URL Webhook n8n (Placeholder Default) ───────────────────────────────────
const N8N_GET_URL = 'https://DOMAIN-N8N-ANDA/webhook/tracking-get';
const N8N_UPDATE_URL = 'https://DOMAIN-N8N-ANDA/webhook/tracking-update';

// Fungsi untuk menjana waktu dummy dinamis relatif terhadap tanggal saat ini
const relativeDate = (offsetDays, hours, minutes) => {
  const d = new Date();
  d.setDate(d.getDate() - offsetDays);
  d.setHours(hours, minutes, 0, 0);
  
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  
  // Format timezone offset secara otomatis agar kompatibel dengan filter tanggal browser lokal
  const tzOffset = -d.getTimezoneOffset();
  const diffSign = tzOffset >= 0 ? '+' : '-';
  const pad = (num) => String(Math.floor(Math.abs(num))).padStart(2, '0');
  const tzFormatted = diffSign + pad(tzOffset / 60) + ':' + pad(tzOffset % 60);
  
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}:00${tzFormatted}`;
};

const CONFIG = {
  // ── Mode Uji Dummy ────────────────────────────────────────────────────────
  // Set ke true untuk menguji aplikasi secara offline dengan data dummy interaktif.
  // Set ke false untuk menggunakan koneksi webhook n8n asli.
  TEST_DUMMY: true,

  N8N_GET_URL: N8N_GET_URL,
  N8N_UPDATE_URL: N8N_UPDATE_URL,
  API_GET_URL: N8N_GET_URL,
  API_UPDATE_URL: N8N_UPDATE_URL,

  // Deteksi apakah URL n8n masih placeholder (belum dikonfigurasi ke server asli).
  // Dipakai untuk menampilkan pesan error yang jelas alih-alih retry percuma.
  ENDPOINT_BELUM_DIKONFIGURASI: N8N_GET_URL.indexOf('DOMAIN-N8N-ANDA') !== -1 || N8N_UPDATE_URL.indexOf('DOMAIN-N8N-ANDA') !== -1,

  // ── Parameter Jaringan (Sinyal Lemah) ─────────────────────────────────────
  FETCH_TIMEOUT_MS: 8000,
  MAX_RETRY: 2,
  RETRY_BACKOFF_MS: 1500,

  // ── Penyimpanan Lokal ──────────────────────────────────────────────────────
  CACHE_KEY_PREFIX: 'metro_track_redesign_',
  OFFLINE_QUEUE_KEY: 'metro_admin_queue_redesign',
  ADMIN_NAME_KEY: 'metro_admin_name_redesign',
  DUMMY_STORAGE_KEY: 'metro_dummy_data_storage', // Untuk menyimpan status dummy yang diupdate

  APP_NAME: 'Metro Logistik Indonesia',

  // ── Kamus Pesan Error Terpusat (Bahasa Indonesia) ─────────────────────────
  // Dipakai konsisten di tracking.js & admin.js agar pesan yang dilihat
  // pengguna seragam dan mudah dipelihara dari satu tempat.
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
  ],

  // ── Data Dummy Awal untuk Simulasi Uji Coba (Dinamis Relatif) ──────────────
  DUMMY_DATA: [
    {
      no_resi: 'JX12345678',
      found: true,
      pengirim: 'Budi Setiawan (Jakarta)',
      penerima: 'Siti Aminah (Surabaya)',
      status_terakhir: 'Delivered',
      timestamp_update: relativeDate(0, 9, 0), // Hari ini jam 09:00
      riwayat: [
        {
          status: 'Manifest',
          waktu: relativeDate(2, 10, 0), // 2 hari lalu jam 10:00
          lokasi: 'Gudang Pengirim - Jakarta Pusat',
          admin: 'Rian Hidayat'
        },
        {
          status: 'On Process',
          waktu: relativeDate(2, 14, 30), // 2 hari lalu jam 14:30
          lokasi: 'Sorting Center - Jakarta Barat',
          admin: 'Bambang Kusuma'
        },
        {
          status: 'Transit',
          waktu: relativeDate(1, 3, 15), // Kemarin jam 03:15
          lokasi: 'Hub Utama - Semarang',
          admin: 'Agus Salim'
        },
        {
          status: 'Transit',
          waktu: relativeDate(1, 19, 45), // Kemarin jam 19:45
          lokasi: 'Gateway Utama - Surabaya',
          admin: 'Heri Prasetyo'
        },
        {
          status: 'Out for Delivery',
          waktu: relativeDate(0, 7, 30), // Hari ini jam 07:30
          lokasi: 'Kurir Sedang Menuju ke Lokasi Penerima',
          admin: 'Joko Susilo'
        },
        {
          status: 'Delivered',
          waktu: relativeDate(0, 9, 0), // Hari ini jam 09:00
          lokasi: 'Diterima oleh Ibu Siti Aminah (Ybs)',
          admin: 'Joko Susilo'
        }
      ]
    },
    {
      no_resi: 'JX87654321',
      found: true,
      pengirim: 'Toko Elektronik Makmur (Bandung)',
      penerima: 'Andi Wijaya (Yogyakarta)',
      status_terakhir: 'Out for Delivery',
      timestamp_update: relativeDate(0, 8, 15), // Hari ini jam 08:15
      riwayat: [
        {
          status: 'Manifest',
          waktu: relativeDate(1, 9, 0), // Kemarin jam 09:00
          lokasi: 'Drop Point - Bandung Timur',
          admin: 'Soni Sanjaya'
        },
        {
          status: 'On Process',
          waktu: relativeDate(1, 12, 0), // Kemarin jam 12:00
          lokasi: 'Sorting Center - Bandung Utara',
          admin: 'Dewi Lestari'
        },
        {
          status: 'Transit',
          waktu: relativeDate(0, 1, 30), // Hari ini jam 01:30
          lokasi: 'Hub Transit - Yogyakarta Sleman',
          admin: 'Hadi Wibowo'
        },
        {
          status: 'Out for Delivery',
          waktu: relativeDate(0, 8, 15), // Hari ini jam 08:15
          lokasi: 'Dalam pengantaran kurir area Sleman-Condongcatur',
          admin: 'Guntur Pamungkas'
        }
      ]
    },
    {
      no_resi: 'JX55556666',
      found: true,
      pengirim: 'Hijab Chic Official (Bandung)',
      penerima: 'Diana Putri (Medan)',
      status_terakhir: 'Transit',
      timestamp_update: relativeDate(0, 5, 40), // Hari ini jam 05:40
      riwayat: [
        {
          status: 'Manifest',
          waktu: relativeDate(1, 15, 0), // Kemarin jam 15:00
          lokasi: 'Drop Point - Bandung Central',
          admin: 'Novi Fitriani'
        },
        {
          status: 'On Process',
          waktu: relativeDate(1, 18, 0), // Kemarin jam 18:00
          lokasi: 'Sorting Hub - Jakarta Soekarno Hatta',
          admin: 'Hendra Setiawan'
        },
        {
          status: 'Transit',
          waktu: relativeDate(0, 5, 40), // Hari ini jam 05:40
          lokasi: 'Bandara Kualanamu - Medan (Transit Udara)',
          admin: 'Ucok Siregar'
        }
      ]
    },
    {
      no_resi: 'JX11112222',
      found: true,
      pengirim: 'PT Global Trading (Semarang)',
      penerima: 'CV Karya Utama (Balikpapan)',
      status_terakhir: 'Manifest',
      timestamp_update: relativeDate(0, 6, 30), // Hari ini jam 06:30
      riwayat: [
        {
          status: 'Manifest',
          waktu: relativeDate(0, 6, 30), // Hari ini jam 06:30
          lokasi: 'Kantor Cabang - Semarang Mangkang',
          admin: 'Taufik Hidayat'
        }
      ]
    }
  ]
};

// Ekspor ke lingkungan browser
if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
}
