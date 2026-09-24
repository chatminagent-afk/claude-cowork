# VIRA Personal (Steven) — panduan migrasi ke Fonnte

## File di folder ini

| File | Node | Titik kirim WA | Sumber |
|---|---|---|---|
| `2026-08-31-VIRA-Personal-Main-Fonnte.json` | 103 | 7 | `2026-08-30-VIRA-Personal-Main.json` (versi terbaru) |
| `2026-08-31-VIRA-Personal-Followup-Fonnte.json` | 13 | 2 | `2026-08-28-…-Followup.json` |
| `2026-08-31-VIRA-Personal-Error-Notifier-Fonnte.json` | 8 | 1 | `2026-08-28-…-Error-Notifier.json` |
| `2026-08-31-VIRA-Personal-STATS-Cleanup-Fonnte.json` | 16 | 1 | `2026-08-28-…-STATS-Cleanup.json` |

Yang dipakai sebagai basis Main adalah **`2026-08-30`**, bukan `2026-08-28`. `Buffer Cleanup` tidak menyentuh WA — biarkan.

---

## CONFIG sheet

Tab CONFIG di sheet VIRA Personal (`1C5gF1TT…`):

| Baris | Tindakan |
|---|---|
| `kirimi_user_code` / `kirimi_secret` / `kirimi_device_id` | hapus ketiganya |
| **`fonnte_token`** | tambah, isi token device Fonnte VIRA Personal |
| `admin_phone` | pastikan terisi — sekarang jadi satu-satunya ketergantungan CONFIG di notifier |

---

## Checklist

**1. Device & credential**
- [ ] Device Fonnte untuk nomor VIRA Personal, scan QR, status `connect`.
- [ ] Credential Header Auth, Name `Authorization`, Value token tanpa `Bearer`.
- [ ] Nama persis: **`Fonnte - VIRA Personal`**.
- [ ] Isi `fonnte_token` di CONFIG.

**2. Import**
- [ ] Import keempat file, jangan aktifkan.
- [ ] Pilih credential di node HTTP yang merah.

**3. Webhook**
- [ ] Dashboard Fonnte → webhook = `https://<host-n8n>/webhook/wa-inbound-steven-fonnte`.

**4. Paket**
- [ ] Main punya dua node kirim media (`Send Media Kirimi`, `Send Media Kirimi 2`) untuk deck/portofolio. Butuh paket Fonnte yang mendukung attachment.

**5. Uji**
- [ ] Percakapan teks penuh, lalu satu permintaan yang memicu kirim media.
- [ ] Kirim gambar **ke** VIRA untuk menguji jalur Vision — normalizer memetakan `url` + `extension` Fonnte ke `mediaUrl`/`mimeType` yang dicari `Chat Counter`.
- [ ] Follow-up: jalankan manual sekali sebelum diaktifkan terjadwal.

**6. Pindah**
- [ ] Nonaktifkan 4 workflow Kirimi lama, aktifkan versi Fonnte.

---

## Yang ikut diperbaiki, bukan sekadar dipindah

**Error Notifier tidak lagi bisa bolong saat paling dibutuhkan.** Sebelumnya kredensial pengirim ikut dibaca dari CONFIG; kalau `Read CONFIG` gagal, `Compose Notif` jatuh ke kredensial `PLACEHOLDER_ISI_MANUAL` dan notifikasi hampir pasti gagal terkirim — jaring pengaman terakhir justru berlubang tepat ketika ada masalah. Sekarang autentikasi ada di n8n Credential yang tidak menyentuh sheet sama sekali. Kalau CONFIG gagal dibaca, notifikasi **tetap terkirim**; hanya `admin_phone` yang jatuh ke cadangan `6285171701168`, dan pesannya menyebutkan itu.

**`Check Kirimi Response` → `Check Fonnte Response`.** Kini mengenali respons Fonnte berbentuk objek maupun array, dan melempar error saat `status: false` walau HTTP 200 — sehingga jalur email fallback ikut jalan.

**`Build Fallback Payload` mengirim `fonnte_response` dan `kirimi_response` sekaligus**, jadi `GLOBAL - Email Fallback Notifier` versi lama maupun versi baru sama-sama bisa membacanya. Tidak ada urutan import yang wajib.

## Sisa yang sengaja dibiarkan

Node `Siapkan Notif Deck` masih menyusun field `user_code`/`secret`/`device_id` dari config. Field-field itu sudah tidak dibaca siapa pun (node `Notify Admin Deck` kini pakai credential) dan nilainya jadi kosong — tidak error, hanya sisa. Dibiarkan supaya node itu tetap byte-identik dengan produksi; rapikan kapan saja tanpa risiko.
