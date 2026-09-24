# Persada Cisoka — panduan migrasi ke Fonnte

## File di folder ini

| File | Node | Titik kirim WA |
|---|---|---|
| `2026-08-31-VIRA-PCR-AI-Powered-Fonnte.json` | 85 | 7 |
| `2026-08-31-PCR-Follow-up-AI-Powered-Fonnte.json` | 23 | 3 |
| `2026-08-31-VIRA-PCR-Error-Notifier-Fonnte.json` | 8 | 1 |
| `2026-08-31-VIRA-PCR-STATS-Purge-Fonnte.json` | 12 | 1 |

`MSG_BUFFER Cleanup PCR` tidak menyentuh WA — biarkan.

---

## Yang harus dibenahi di CONFIG sheet

Tab **CONFIG** di `PCR_Database`. Hanya tiga baris yang perlu diurus:

| Baris | Tindakan |
|---|---|
| `kirimi_user_code` = `KM40LI0426` | hapus (atau biarkan, sudah tidak dibaca) |
| `kirimi_secret` = `4efe3780…` | **hapus** — ini rahasia yang tidak terpakai lagi |
| `kirimi_device_id` = `D-LM6WE` | hapus |
| **`fonnte_token`** | **tambah baru**, isi token device Fonnte PCR |

`fonnte_token` dibaca oleh node `Parse Config` dan dipakai node Code `Send WA + Verify (Fonnte)`. Node HTTP tidak memakainya — mereka pakai n8n Credential.

**Tidak ada baris lain yang perlu diubah.** `admin_phone` (`6282281811212`), `field_team_phone` (`6287888542255`), `media_team_phone` (`6282281811212`), `whitelist_enabled` (`0` = publik, semua user lewat) semuanya tetap.

Dua hal yang sekalian layak dirapikan saat sheet dibuka:

- **Format kolom `value` sebaiknya Plain text.** Nomor telepon panjang tersimpan sebagai angka; kalau Sheets mengubahnya ke notasi ilmiah, `admin_phone` jadi rusak dan notifikasi salah alamat tanpa error.
- **`google service private key` ada di dalam CONFIG sheet.** Di luar cakupan migrasi ini, tapi itu kunci privat service account yang duduk di spreadsheet.

---

## Checklist

**1. Device & credential**
- [ ] Device Fonnte untuk nomor PCR, scan QR, status `connect`.
- [ ] n8n → Credentials → Generic → Header Auth. Name `Authorization`, Value = token **tanpa `Bearer`**.
- [ ] Nama credential persis: **`Fonnte - Persada Cisoka`**.
- [ ] Isi `fonnte_token` di tab CONFIG (lihat bagian di atas).

**2. Import**
- [ ] Import keempat file, jangan aktifkan.
- [ ] Pilih credential `Fonnte - Persada Cisoka` di tiap node HTTP yang merah.

**3. Webhook**
- [ ] Dashboard Fonnte → device PCR → webhook = `https://<host-n8n>/webhook/wa-inbound-pcr-fonnte`.

**4. Paket — perhatikan yang ini**
- [ ] PCR punya **dua node kirim media** (`Send Media Kirimi`, `Send Media Kirimi 2`) untuk brosur dan katalog. Attachment butuh paket Fonnte yang mendukungnya. Paket text-only akan membuat kedua node gagal, dan brosur adalah bagian inti alur telemarketer.
- [ ] Volume PCR ±1.889 pesan/7 hari di Kirimi. Kuota 1.000/bulan tidak cukup — pilih tier dari angka ini.

**5. Uji**
- [ ] Set `whitelist_enabled` = `1` sementara, isi `whitelist_numbers` dengan nomormu saja. Uji percakapan penuh termasuk permintaan brosur.
- [ ] Kembalikan `whitelist_enabled` = `0` setelah lolos.
- [ ] Follow-up: `followup_ai_dry_run` = `Y` untuk uji tanpa benar-benar mengirim, lalu balik ke `N`.
- [ ] Uji error notifier dengan memicu error sengaja.

**6. Pindah**
- [ ] Nonaktifkan 4 workflow Kirimi lama, aktifkan versi Fonnte.
- [ ] Pastikan `Error Workflow` di tiap workflow menunjuk notifier versi Fonnte.

## Catatan konversi

- Node media tetap multipart, field `file` tetap binary dari field `data`. Hanya URL, autentikasi, dan `phone` → `target` yang berubah.
- Node `Normalize Fonnte Inbound` disisipkan setelah Webhook. `If From Group` dan `IF From Me` memakai strict boolean pada field yang tidak dikirim Fonnte — tanpa node ini alur berhenti di node ketiga.
- `Whitelist Gate` tetap bekerja: ia membandingkan digit `from` maupun `originLid`, dan Fonnte selalu mengirim nomor asli.
