/*
 * config.js — Konfigurasi APP PUBLIK (Pelacakan) — Metro Logistik Tracking.
 * (Redesain & Mode Uji Dummy oleh Antigravity — QA & production-fix 2026-07-06)
 * [ENHANCEMENT 2026-07-06] Kolom Pengirim/Penerima dihapus (tak ada input-nya).
 *   Data dummy dinaikkan ke 60 resi dengan status beragam untuk uji paginasi.
 */

'use strict';

// ── URL Webhook n8n (GANTI dengan domain n8n Anda saat deploy) ──────────────
// APP PUBLIK: hanya endpoint GET. URL update TIDAK ada di aplikasi ini (keamanan).
const N8N_GET_URL = 'https://n8n.srv1270416.hstgr.cloud/webhook/tracking-get';

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

// ── Generator Data Dummy (60 resi, gaya pelacakan JNE/Shopee) ───────────────
// Dipakai HANYA saat TEST_DUMMY=true. 60 resi > 50/halaman → paginasi "Halaman
// 1 dari 2" bisa diverifikasi. Perjalanan tiap resi REALISTIS: status akhir
// selalu melewati semua tahap sebelumnya (mis. Delivered = Manifest → On
// Process → Transit multi-hop → Out for Delivery → Delivered), dengan
// keterangan lokasi meniru sistem nyata (contoh: "tiba di Jakarta - Cakung DC").

// Nama hub sortir/DC nyata per kota (mirip penamaan JNE/J&T/SiCepat).
const HUB_KOTA = {
  'Jakarta': 'Jakarta - Cakung DC',
  'Bandung': 'Bandung - Gedebage Hub',
  'Surabaya': 'Surabaya - Margomulyo Hub',
  'Semarang': 'Semarang - Ngaliyan Hub',
  'Medan': 'Medan - Tanjung Morawa Hub',
  'Makassar': 'Makassar - Daya Hub',
  'Denpasar': 'Denpasar - Sanur DC',
  'Palembang': 'Palembang - Sukarami Hub',
  'Yogyakarta': 'Yogyakarta - Maguwoharjo DC',
  'Malang': 'Malang - Singosari Hub',
  'Balikpapan': 'Balikpapan - Batu Ampar Hub',
  'Pontianak': 'Pontianak - Sungai Raya Hub',
  'Manado': 'Manado - Mapanget Hub',
  'Padang': 'Padang - Lubuk Begalung Hub',
  'Pekanbaru': 'Pekanbaru - Marpoyan Hub',
  'Bogor': 'Bogor - Tanah Sareal DC'
};
function hubKota(kota) { return HUB_KOTA[kota] || (kota + ' Hub'); }

// Format objek Date → string ISO dengan offset zona waktu lokal (samakan dgn relativeDate).
function formatISOLokal(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  const tzOffset = -d.getTimezoneOffset();
  const sign = tzOffset >= 0 ? '+' : '-';
  const pad = (n) => String(Math.floor(Math.abs(n))).padStart(2, '0');
  const tz = sign + pad(tzOffset / 60) + ':' + pad(tzOffset % 60);
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}:00${tz}`;
}

function buatDummyData(jumlah) {
  const kotaAsal = ['Jakarta', 'Bandung', 'Surabaya', 'Semarang', 'Medan', 'Makassar', 'Denpasar', 'Palembang'];
  const kotaTujuan = ['Yogyakarta', 'Malang', 'Balikpapan', 'Pontianak', 'Manado', 'Padang', 'Pekanbaru', 'Bogor'];
  const admins = ['Rian Hidayat', 'Bambang Kusuma', 'Agus Salim', 'Dewi Lestari', 'Joko Susilo', 'Novi Fitriani', 'Hendra Setiawan', 'Guntur Pamungkas'];
  const kurirNama = ['Slamet R.', 'Dedi K.', 'Wawan S.', 'Yanto P.', 'Firman A.', 'Rudi H.'];
  const penerimaKet = ['Yang Bersangkutan (YBS)', 'Keluarga', 'Rekan kerja', 'Satpam/Resepsionis'];
  const alasanGagal = ['penerima tidak berada di alamat', 'alamat tidak ditemukan', 'penerima menolak paket', 'nomor penerima tidak dapat dihubungi'];

  const finalStatuses = ['Manifest', 'On Process', 'Transit', 'Out for Delivery', 'Delivered', 'Failed/Return'];

  const data = [];
  for (let i = 0; i < jumlah; i++) {
    const finalStatus = finalStatuses[i % finalStatuses.length];
    const asal = kotaAsal[i % kotaAsal.length];
    const tujuan = kotaTujuan[i % kotaTujuan.length];
    const noResi = 'JX' + String(10000000 + i * 137); // resi dummy unik & mudah ditebak (JX10000000, JX10000137, ...)
    const kurir = kurirNama[i % kurirNama.length];

    const hubAsal = hubKota(asal);
    const hubTujuan = hubKota(tujuan);
    // Hub transit nasional (silang pulau); hindari sama dengan asal.
    const hubAntara = asal === 'Jakarta' ? 'Surabaya - Margomulyo Hub' : 'Jakarta - Cakung DC';

    // Sequence perjalanan LENGKAP (kalau sampai Delivered). Tiap entri: status + keterangan.
    const penuh = [
      { status: 'Manifest', teks: `Pesanan telah dibuat, menunggu penjemputan oleh kurir di ${asal}` },
      { status: 'On Process', teks: `Paket telah diterima di ${hubAsal} dan sedang disortir` },
      { status: 'Transit', teks: `Paket berangkat dari ${hubAsal}` },
      { status: 'Transit', teks: `Paket transit di ${hubAntara}` },
      { status: 'Transit', teks: `Paket telah tiba di ${hubTujuan}` },
      { status: 'Out for Delivery', teks: `Paket sedang dalam pengantaran oleh kurir (${kurir}) di ${tujuan}` },
      { status: 'Delivered', teks: `Paket telah diterima di ${tujuan}. Diterima oleh: ${penerimaKet[i % penerimaKet.length]}. Terima kasih telah menggunakan Metro Logistik.` }
    ];

    // Potong sequence sesuai status akhir.
    let langkah;
    if (finalStatus === 'Failed/Return') {
      langkah = penuh.slice(0, 5).concat([{
        status: 'Failed/Return',
        teks: `Pengiriman gagal — ${alasanGagal[i % alasanGagal.length]}. Paket dikembalikan (retur) ke ${hubAsal}`
      }]);
    } else {
      const potongIdx = { 'Manifest': 1, 'On Process': 2, 'Transit': 5, 'Out for Delivery': 6, 'Delivered': 7 };
      langkah = penuh.slice(0, potongIdx[finalStatus]);
    }

    // Sebar waktu: entri terakhir = baseDaysAgo hari lalu; entri sebelumnya lebih tua.
    const baseDaysAgo = i % 16;                 // 0..15 hari (dalam rentang 30 hari)
    const stepGapJam = 8 + (i % 4) * 4;         // jarak antar-langkah 8..20 jam
    const len = langkah.length;
    const lastMs = Date.now() - (baseDaysAgo * 24 + (i % 12)) * 3600 * 1000;
    const riwayat = langkah.map((s, j) => {
      const jamSebelumTerakhir = (len - 1 - j) * stepGapJam;
      const d = new Date(lastMs - jamSebelumTerakhir * 3600 * 1000);
      return {
        status: s.status,
        waktu: formatISOLokal(d),
        lokasi: s.teks,
        admin: admins[(i + j) % admins.length]
      };
    });

    const terakhir = riwayat[riwayat.length - 1];
    data.push({
      no_resi: noResi,
      found: true,
      status_terakhir: finalStatus,
      timestamp_update: terakhir.waktu,
      riwayat: riwayat
    });
  }
  return data;
}

const CONFIG = {
  // ── Mode Uji Dummy ────────────────────────────────────────────────────────
  // PRODUKSI: false (terhubung ke webhook n8n asli).
  // Ubah ke true HANYA untuk demo/uji offline dengan data dummy interaktif.
  // Saat true: 60 resi dummy tersedia → klik "Terapkan Filter" (tanpa mengetik)
  // untuk memuat semuanya dan menguji paginasi "Halaman 1 dari 2".
  TEST_DUMMY: true,

  N8N_GET_URL: N8N_GET_URL,
  API_GET_URL: N8N_GET_URL,

  // Deteksi apakah URL n8n masih placeholder (belum dikonfigurasi ke server asli).
  ENDPOINT_BELUM_DIKONFIGURASI: N8N_GET_URL.indexOf('DOMAIN-N8N-ANDA') !== -1,

  // ── Parameter Jaringan (Sinyal Lemah) ─────────────────────────────────────
  FETCH_TIMEOUT_MS: 8000,
  MAX_RETRY: 2,
  RETRY_BACKOFF_MS: 1500,

  // ── Penyimpanan Lokal ──────────────────────────────────────────────────────
  CACHE_KEY_PREFIX: 'metro_track_redesign_',
  DUMMY_STORAGE_KEY: 'metro_dummy_data_storage', // Untuk menyimpan status dummy yang diupdate

  APP_NAME: 'Metro Logistik Indonesia',

  // ── Kamus Pesan Error Terpusat (Bahasa Indonesia) ─────────────────────────
  ERROR_MESSAGES: {
    // ── Validasi input umum ──
    RESI_KOSONG: 'Masukkan minimal satu nomor resi.',
    RESI_FORMAT_TIDAK_VALID: 'Format nomor resi tidak valid. Gunakan huruf/angka tanpa spasi.',

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

  // ── Data Dummy untuk Simulasi Uji Coba: 60 resi, status beragam ────────────
  DUMMY_DATA: buatDummyData(60)
};

// Ekspor ke lingkungan browser
if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
}
