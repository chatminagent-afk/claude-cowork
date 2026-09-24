# Patch V4 Compat — Changelog & Panduan Import (2026-07-07)

Basis: `report/production/VIRA V4.json` (59 node, tidak diubah — berfungsi sebagai backup).
Hasil: `2026-07-07-VIRA-V4-global-toggle-plus-race-fix.json` (62 node) + `2026-07-07-index-LID-badge.html`.

## Yang berubah di workflow (item 1 & 2 plan)

**Node baru (3):**

| Node | Fungsi | Setting penting |
|------|--------|-----------------|
| `Read VIRA Config` | Baca CONFIG, filter Key=VIRA_STATUS | alwaysOutputData, retryOnFail, credential Service Account thescholars |
| `IF VIRA Active` | Gate global ON/OFF | Kondisi: `Value ≠ OFF` (lihat catatan fail-open di bawah) |
| `Re-Read Bot Mode` | Re-read 1 baris STATS (filter No WA = resolved_key) sebelum tulis | alwaysOutputData (wajib — tanpa ini user baru tidak pernah tertulis), executeOnce, retryOnFail |

**Rewiring (2):**
- `IF (Whitelist) [true] → Read VIRA Config → IF VIRA Active [true] → Chat Counter`; branch false kosong (bot silent).
- `Process Counter & Merge Data → Re-Read Bot Mode → Update to STATS`.

**Node `Update to STATS` (2 formula):**
- `bot_mode`: `isTalkToSam ? 'OFF' : ($json.bot_mode terkini === 'OFF' ? 'OFF' : 'ON')` — OFF dari dashboard tidak lagi ter-overwrite balik jadi ON (Opsi A).
- `lid`: diubah dari `$json.lid` → referensi eksplisit `$('Process Counter & Merge Data').first().json.lid`, karena `$json` sekarang berisi baris hasil Re-Read Bot Mode.

Tidak ada node lain yang berubah (diverifikasi diff programatik: hanya `Update to STATS` + connections).

## Deviasi kecil dari plan (fail-open, disengaja)

Plan spesifikasi `Value === "ON"`. Saya pakai `Value ≠ "OFF"` + `alwaysOutputData`. Alasan: kalau baris `VIRA_STATUS` belum ada / terhapus / node read gagal filter, versi `=== ON` membuat bot **mati total secara diam-diam**. Versi `≠ OFF` hanya mematikan bot kalau eksplisit OFF. Perilaku toggle ON/OFF normal 100% sama. Kalau mau persis plan, ubah operator di `IF VIRA Active` jadi equals "ON".

## Langkah import (n8n)

1. Export workflow production aktif sebagai backup bertanggal (opsional — file asli di repo juga utuh).
2. Import `2026-07-07-VIRA-V4-global-toggle-plus-race-fix.json` sebagai workflow baru.
3. Buka `Read VIRA Config` → dropdown Sheet → pilih ulang **CONFIG** (bind gid). Cek credential.
4. Buka `Re-Read Bot Mode` → dropdown Sheet → pilih ulang **STATS** (bind gid). Cek credential.
5. Di sheet CONFIG tambah baris: `VIRA_STATUS | ON`.
6. Deactivate workflow lama → Activate workflow baru (webhook path sama, jangan aktif dua-duanya).

## Verifikasi (acceptance)

- [ ] Toggle global OFF di dashboard → pesan test tidak dibalas, execution berhenti di `IF VIRA Active`. ON → dibalas normal.
- [ ] Toggle per-user OFF → user chat → `bot_mode` di STATS **tetap OFF** setelah turn selesai (test race fix).
- [ ] `Talk to Sam` dari user tetap men-set OFF seperti sebelumnya.
- [ ] User baru (nomor belum ada di STATS) tetap tertulis ke STATS (test alwaysOutputData Re-Read Bot Mode).
- [ ] Badge kuning "LID" muncul di daftar user untuk No WA ≥15 digit.

## Dashboard (item 5)

`2026-07-07-index-LID-badge.html` = pengganti `index.html` (deploy: rename jadi `index.html` di hosting PWA). Perubahan: CSS `.lidtag` + fungsi `isLid()` (hitung digit ≥15, aman terhadap format `+62 ...`) + badge di `renderUsers`. Tidak ada perubahan Code.gs.

## ⚠️ Flag (di luar scope patch, perlu perhatian)

1. **`IF (Whitelist)` di V4 production ternyata DISABLED** — audit biaya 3 Juli mencatat whitelist ENABLED. Ada yang mematikannya antara 3–7 Juli? Node disabled bersifat pass-through jadi toggle global tetap jalan, tapi artinya **whitelist tidak menyaring apa-apa sekarang**. Konfirmasi ke Sam apakah disengaja.
2. **Kuota Sheets**: patch ini menambah **+2 read/pesan** (Read VIRA Config + Re-Read Bot Mode) di atas ~9 read/pesan yang sudah tercatat di audit 6 Juli → ~11 read/pesan. Masih di bawah limit 300 read/menit Google, tapi kalau traffic naik, pertimbangkan cache CONFIG (mis. workflow static data) sebelum scale.
3. **Item 3 plan (verifikasi `gform_sent_ts`)**: belum dikerjakan — butuh konfirmasi tertulis Sam apakah ada fix eksplisit yang deploy 6–7 Juli.
4. **Item 4 plan (`gform_filled`)**: belum dikerjakan — kartu "Konversi GForm" akan tetap 0% sampai sumber data form response ditentukan.

## Rollback

Deactivate workflow baru → activate workflow lama. Atau di workflow baru: sambungkan langsung `IF (Whitelist) [true] → Chat Counter` dan `Process Counter & Merge Data → Update to STATS`, lalu kembalikan formula `bot_mode` ke `isTalkToSam ? 'OFF' : 'ON'` dan `lid` ke `$json.lid`.
