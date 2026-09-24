# Panduan import — The Scholars & Persada Cisoka

Urutan kerja langsung. Kerjakan A sampai tuntas, baru B.

**Yang tidak perlu diimport:** `GLOBAL - Email Fallback Notifier (Fonnte-ready)`. Notifier baru tetap mengirim `kirimi_fallback` + `kirimi_response`, jadi email fallback yang sudah jalan di n8n tetap terbaca. Mengimportnya justru bikin kerjaan: ID-nya baru, dan 4 notifier harus di-repoint. Lewati.

**Prasyarat:** paket Fonnte berbayar (watermark "sent via fonnte" hanya hilang di paket berbayar; paket Persada juga harus mendukung attachment), dan **dua device terpisah** — satu TS, satu PCR.

> Jangan pakai nomor `6285155202354` sebagai device untuk workflow mana pun di sini. Nomor itu jadi *tujuan* notifikasi di beberapa node; kalau ia juga jadi pengirim, notifikasi jadi kirim-ke-diri-sendiri.

---

# A. The Scholars

**A1. Device** — buat device Fonnte nomor TS, scan QR, pastikan `connect`. Salin tokennya.

**A2. Credential** — n8n → Credentials → New → *Header Auth*
- Name (field di dalam credential): `Authorization`
- Value: token, **polos tanpa `Bearer`**
- Nama credential: **`Fonnte - The Scholars`**

**A3. Import** 3 file dari `the-scholars/`:
- `2026-08-31-VIRA-TS-Fonnte-v2.json`
- `2026-08-31-VIRA-TS-Error-Notifier-Fonnte.json`
- `2026-08-31-TS-STATS-Cleanup-v3-Fonnte.json`

Semua masuk sebagai workflow baru dan **tidak aktif**. Yang lama tidak tersentuh.

**A4. Isi token di satu Code node** — buka `VIRA TS Fonnte` → node **`Send WA + Verify (Fonnte)`** → ganti:
```js
const TOKEN = 'REDACTED';
```
dengan token device TS. Ini satu-satunya token literal yang tersisa (Code node n8n tidak bisa membaca credential). Token lama itu sudah terpapar di chat — **regenerate di dashboard Fonnte**.

**A5. Pilih credential** di setiap node HTTP yang tandanya merah → `Fonnte - The Scholars`. Ada 4 di workflow utama, 1 di Error Notifier, 1 di STATS Cleanup.

**A6. Error Workflow** — buka `VIRA TS Fonnte` → Settings → **Error Workflow** = `VIRA TS Error Notifier (Fonnte)`.
File-nya masih menunjuk notifier Kirimi lama; ID workflow baru baru lahir saat import, jadi tidak bisa diisi dari file. Ada sticky merah di kanvas sebagai pengingat.

**A7. Webhook** — dashboard Fonnte → device TS → webhook:
```
https://<host-n8n>/webhook/wa-inbound-fonnte
```

**A8. Uji** (workflow lama masih hidup — path webhook beda, jadi aman berdampingan)
- Aktifkan `VIRA TS Fonnte`, kirim WA dari `6285171701168`. Harus dibalas, execution hijau.
- Notifikasi tes sudah diarahkan ke nomormu, **bukan ke Sam**. Jangan lupa langkah A10.
- Picu error sengaja (mis. rename sementara sebuah node) → cek WA notifikasi masuk.
- `STATS Cleanup v3` → Execute Workflow manual → cek laporan masuk. (Aslinya memang tidak aktif; biarkan tidak aktif.)

**A9. Pindah** — nonaktifkan `VIRA TS` dan `VIRA TS Error Notifier` yang lama. Aktifkan yang baru.

**A10. Sebelum benar-benar produksi** — kembalikan `target` di `Notify Admin Unknown` dan `Notify Talk to Sam` ke **`6596110395`** (Sam). Sekarang keduanya ke nomormu untuk keperluan tes; ada `notes` pengingat di node.

---

# B. Persada Cisoka

**B1. CONFIG sheet dulu** — tab `CONFIG` di `PCR_Database`:

| Baris | Aksi |
|---|---|
| `fonnte_token` | **tambah**, isi token device Fonnte PCR |
| `kirimi_secret` | **hapus** — rahasia yang sudah tidak terpakai |
| `kirimi_user_code`, `kirimi_device_id` | hapus (sudah tidak dibaca) |

Selesai. Baris lain tidak berubah.

**B2. Device & credential** — device Fonnte nomor PCR, scan QR, `connect`. Credential *Header Auth*, Name `Authorization`, Value token tanpa `Bearer`, nama credential **`Fonnte - Persada Cisoka`**.

**B3. Rem tangan dulu, sebelum import** — di CONFIG set:
```
followup_ai_dry_run = Y
```
`followup_max` saat ini `0`, dan di kode `0` berarti **tanpa batas**, bukan mati. `followup_ai_dry_run` saat ini `N` = kirim sungguhan, dan trigger-nya tiap jam. Tanpa langkah ini, begitu follow-up diaktifkan ia langsung mengirim ke lead nyata lewat gateway yang belum teruji.

**B4. Import** 4 file dari `persada-cisoka/`:
- `2026-08-31-VIRA-PCR-AI-Powered-Fonnte.json`
- `2026-08-31-PCR-Follow-up-AI-Powered-Fonnte.json`
- `2026-08-31-VIRA-PCR-Error-Notifier-Fonnte.json`
- `2026-08-31-VIRA-PCR-STATS-Purge-Fonnte.json`

**B5. Pilih credential** `Fonnte - Persada Cisoka` di semua node HTTP merah: 6 di workflow utama, 3 di follow-up, 1 di error notifier, 1 di STATS purge.

**B6. Error Workflow** → `VIRA-PCR Error Notifier (Fonnte)`, pada **dua** workflow: `VIRA PCR AI Powered` dan `Follow-up AI Powered`. Sticky merah ada di kanvas keduanya.

**B7. Webhook** — dashboard Fonnte → device PCR:
```
https://<host-n8n>/webhook/wa-inbound-pcr-fonnte
```

**B8. Uji percakapan**
- CONFIG: `whitelist_enabled = 1`, `whitelist_numbers = ["6285171701168"]`.
- Aktifkan `VIRA PCR AI Powered`, chat dari nomormu.
- **Wajib diuji: minta brosur.** Node media berubah paling banyak (endpoint, autentikasi, plus parameter `filename` baru yang menentukan apakah WhatsApp merender PDF sebagai dokumen atau gagal). Pastikan brosur benar-benar terbuka di WA, bukan sekadar terkirim.
- Kembalikan `whitelist_enabled = 0` setelah lolos.

**B9. Uji follow-up** — Execute Workflow manual sekali dengan `dry_run` masih `Y`, cek log: kandidat terpilih, pesan tersusun, tidak ada yang terkirim. Baru set `followup_ai_dry_run = N` dan aktifkan.

**B10. Pindah** — nonaktifkan 4 workflow PCR lama, aktifkan yang baru. `STATS Purge` aslinya tidak aktif; biarkan.

---

# Verifikasi akhir

| Cek | Lolos kalau |
|---|---|
| Balasan chat | Execution hijau, WA sampai |
| Respons node kirim | `status: true` |
| Brosur PCR | Terbuka sebagai PDF/gambar di WA, bukan file rusak |
| Notifikasi error | WA masuk saat error dipicu sengaja |
| Error Workflow | Menunjuk notifier **(Fonnte)**, bukan yang lama |
| Watermark | Tidak ada "sent via fonnte" di akhir pesan |

# Rollback

Aktifkan kembali workflow Kirimi lama, kosongkan webhook di dashboard Fonnte. Tidak ada data yang berubah — Google Sheets, STATS, MSG_BUFFER, credential Anthropic dan Sheets tidak pernah tersentuh. CONFIG PCR cukup dikembalikan tiga barisnya kalau memang mau kembali penuh.

# Ringkasan isian

| Tempat | TS | PCR |
|---|---|---|
| Nama credential | `Fonnte - The Scholars` | `Fonnte - Persada Cisoka` |
| Token literal di Code node | ya, 1 tempat | tidak |
| Token di CONFIG sheet | tidak ada CONFIG gateway | `fonnte_token` |
| Path webhook | `wa-inbound-fonnte` | `wa-inbound-pcr-fonnte` |
| Node HTTP butuh credential | 6 (3 workflow) | 11 (4 workflow) |
| Kirim media | tidak ada | 2 node, wajib diuji |
