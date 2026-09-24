# VIRA — Ketahanan Pengiriman WhatsApp (failover multi-provider)

**Tanggal:** 2026-08-31
**Konteks:** Kirimi memblokir IP server n8n (`76.13.18.214`). Akun, kredensial, device, dan kuota semuanya sehat — hanya IP-nya yang ditolak. Dokumen ini merancang VIRA supaya **tetap hidup walau Kirimi tidak pernah membuka blokirnya.**

---

## 1. Kenapa arsitektur lama runtuh total

Satu blokir IP mematikan seluruh bot. Penyebabnya bukan Kirimi, melainkan tiga cacat desain:

| Cacat | Akibat |
|---|---|
| 6 node menembak Kirimi langsung, hardcoded | Tidak ada jalur cadangan. Satu provider tumbang = bot mati |
| Error Notifier mengirim alert **lewat Kirimi** | Saat Kirimi bermasalah, notifikasinya ikut mati. Buta total |
| Body respons dibuang, hanya `lastErr.message` disimpan | Penyebab asli baru ketahuan setelah berjam-jam menebak |

Ditambah pemicu awalnya: retry berlapis (`AI Agent` 3× × `Anthropic` 3×, enam node Kirimi ber-`retryOnFail`) memperbesar volume request saat gagal — persis pola yang dibaca sistem anti-abuse sebagai penyalahgunaan.

**Prinsip perbaikan:** jangan cuma ganti provider. Hilangkan ketergantungan pada provider mana pun, dan berhenti menghasilkan trafik yang memicu blokir.

---

## 2. Yang sudah disiapkan

| File | Isi |
|---|---|
| `2026-08-31-GLOBAL-Send-WA-failover.json` | Sub-workflow siap import — pintu keluar WhatsApp tunggal |
| `2026-08-31-snippet-send-wa-failover.js` | Kode node-nya terpisah, untuk dibaca/diedit tanpa membuka n8n |

Isi sub-workflow:

1. **Rantai provider** — gagal di satu provider, otomatis lanjut ke berikutnya
2. **Circuit breaker** — provider yang membalas 401/403 diistirahatkan 10 menit, supaya kita berhenti menghantam layanan yang sedang memblokir kita
3. **Retry disiplin** — hanya untuk 5xx/408/429/jaringan. 4xx tidak pernah diulang
4. **Body respons selalu dilaporkan** — kebutaan kemarin tidak terulang
5. **Kredensial terpusat** — satu tempat untuk semua provider

Provider kedua yang dipilih: **Fonnte**. Alasannya batas pesan 60.000 karakter, sedangkan Wablas hanya 1.024 — balasan VIRA dengan `maxTokensToSample: 512` bisa menembus batas itu dan terpotong diam-diam.

---

## 3. Urutan deploy

Dikerjakan bertahap. Tahap 1–3 sudah cukup membuat VIRA hidup kembali.

### Tahap 1 — Siapkan Fonnte (prasyarat)

1. Daftar di fonnte.com, ambil paket trial/termurah
2. Scan QR dengan nomor The Scholars
3. Salin token dari **Device → Token**

> WhatsApp mendukung sampai 4 linked device per nomor, dan gateway unofficial memakai satu slot. Secara teknis Kirimi dan Fonnte bisa terhubung bersamaan ke nomor yang sama. **Konfirmasi dulu ke Fonnte** sebelum scan, dan pastikan device Kirimi tidak terputus setelahnya.

### Tahap 2 — Import & uji terpisah (belum menyentuh produksi)

1. Import `2026-08-31-GLOBAL-Send-WA-failover.json`
2. Buka node **Kirim WA (failover)**, di blok `PROVIDERS`:
   - Ganti `ISI_TOKEN_FONNTE_DI_SINI` dengan token Fonnte
   - Ubah `enabled: false` → `enabled: true` pada blok fonnte
3. Uji manual: jalankan sub-workflow dengan input `phone` = nomormu, `message` = `tes failover`, `context` = `uji-coba`

Yang diharapkan: Kirimi gagal 403, breaker aktif, Fonnte mengambil alih, WA masuk. Cek output — `provider` harus berisi `fonnte`, dan `attempts` menampilkan alasan Kirimi gagal secara lengkap.

**Kalau tahap ini gagal, berhenti di sini.** Jangan lanjut menyentuh produksi.

### Tahap 3 — Ganti node balasan utama (ini yang menghidupkan VIRA)

Di workflow **VIRA TS**:

1. Hapus node `Send WA + Verify (Kirimi)`
2. Tambah node **Execute Workflow**, beri nama `Send WA (failover)`
3. Sambungkan ulang:
   - `Wait1` → `Send WA (failover)`
   - `Send WA (failover)` → `Extract & Prepare Data`, `Delete_Pending_Msg`, `Update STATS - Greeting Flag`
4. Parameter:
   - Workflow: **GLOBAL - Send WA (failover)**
   - Wait for Sub-Workflow Completion: **ON**
   - `phone` → `={{ $('Chat Counter').first().json.user_wa }}`
   - `message` → `={{ $('Process All').first().json.cleanOutput }}`
   - `context` → `reply-utama`
5. Settings node: **On Error = Stop Workflow**, **Retry on Fail = OFF**

Dua catatan penting:

- **Retry on Fail wajib OFF.** Sub-workflow sudah menangani retry. Menyalakannya di sini mengembalikan pelipatgandaan request yang memicu blokir.
- **Semantik Retry tetap utuh.** Kirim dan verifikasi ada di dalam satu sub-workflow, jadi satu klik Retry benar-benar mengirim ulang — bukan sekadar memvalidasi respons lama. Ini properti yang sengaja dibangun pada Agustus lalu dan tidak boleh hilang.

Sudah diverifikasi: **tidak ada node yang membaca output node lama** (`Extract & Prepare Data`, `Delete_Pending_Msg`, dan `Update STATS - Greeting Flag` semuanya memakai referensi silang `$('NodeName')`, bukan `$json`). Perubahan bentuk output aman.

### Tahap 4 — Empat node sisanya

Ganti masing-masing HTTP Request menjadi Execute Workflow ke sub-workflow yang sama, dengan pemetaan berikut:

| Node | `phone` | `message` | `context` |
|---|---|---|---|
| `Send GForm Link` | `={{ $json.phone }}` | `={{ $json.message }}` | `gform-link` |
| `Send GForm Clarify` | `={{ $json.phone }}` | `={{ $json.message }}` | `gform-clarify` |
| `Notify Admin Unknown` | `6596110395` | *(salin ekspresi lama apa adanya)* | `notif-unknown` |
| `Notify Talk to Sam` | `6596110395` | *(salin ekspresi lama apa adanya)* | `notif-talk-to-sam` |

- Dua node GForm: pertahankan **On Error = Continue (using error output)** seperti sekarang
- Dua node notifikasi: **Retry on Fail = OFF** (sebelumnya menyala 3×)

### Tahap 5 — Error Notifier tidak boleh buta lagi

Di workflow **VIRA TS Error Notifier**, ganti `Notify Admin Error` menjadi Execute Workflow:

- `phone` → `6285155202354`
- `message` → `={{ $json.notif_text }}`
- `context` → `alert-error`
- Settings: **On Error = Continue (using error output)**
- Output error → `Build Fallback Payload` (jalur email yang sudah ada)

Hasilnya: alert dicoba lewat Kirimi, lalu Fonnte, dan kalau dua-duanya tumbang barulah email. Node `Check Kirimi Response` menjadi tidak diperlukan lagi — verifikasi respons sudah ditangani di dalam sub-workflow.

> Kalau ingin kepastian maksimum, kirim email **selalu** (bukan hanya saat WA gagal). Konsekuensinya inbox lebih ramai. Rekomendasi saya: pakai konfigurasi di atas dulu, naikkan kalau ternyata masih ada alert yang lolos.

### Tahap 6 — Kecilkan pelipatgandaan retry

Ini pemicu awalnya, dan harus ikut diperbaiki. Tanpa ini, provider berikutnya akan bernasib sama.

| Node | Sekarang | Jadi |
|---|---|---|
| `AI Agent` | maxTries 3, jeda 5000 | maxTries **2**, jeda **8000** |
| `Anthropic Chat Model` | maxTries default 3, jeda 2000 | maxTries **2**, jeda **5000** |

Worst case turun dari 9 panggilan Anthropic per pesan menjadi 4. Jeda yang lebih panjang juga lebih efektif untuk `429 rate_limit` dan `529 overloaded` — jeda 2 detik terlalu pendek untuk keduanya.

---

## 4. Verifikasi

- [ ] Sub-workflow berjalan mandiri, WA masuk lewat Fonnte
- [ ] Output `attempts` menampilkan alasan kegagalan Kirimi **lengkap dengan body respons**
- [ ] Kirim pesan tes ke VIRA dari WhatsApp → balasan masuk
- [ ] Cek execution: node `Send WA (failover)` hijau, `provider` berisi `fonnte`
- [ ] Percobaan kedua dalam 10 menit: Kirimi **dilewati** oleh circuit breaker, bukan dicoba ulang
- [ ] Picu error sengaja → alert error tetap sampai (WA atau email)
- [ ] Jalur GForm masih mengirim link dengan benar

---

## 5. Rollback

Semua perubahan bersifat penggantian node, bukan penghapusan data.

- File produksi lama tersimpan di `report/patch/live production/VIRA TS.json` — import ulang untuk kembali ke kondisi semula
- Sub-workflow bisa dinonaktifkan tanpa menyentuh workflow utama
- Untuk mematikan satu provider: ubah `enabled` menjadi `false` di blok `PROVIDERS`

---

## 6. Yang tetap harus dikejar (di luar teknis)

1. **Email ke support@kirimi.id** minta pencabutan blokir `76.13.18.214`. Paket Basic masih 333 hari — jangan direlakan. Setelah dibuka, Kirimi otomatis kembali jadi jalur utama tanpa perubahan apa pun, karena urutannya sudah di posisi pertama.
2. **Audit device Persada** — 1.889 pesan dengan performa 86,55% (sekitar 255 gagal) adalah sumber api yang sebenarnya. Selama itu jalan, IP mana pun berisiko kena lagi.
3. **Pisahkan Persada ke akun Kirimi sendiri.** Sekarang satu proyek bisa mematikan proyek lain, dan slot device sudah 3/3. Lakukan terbuka sebagai pemisahan proyek, bukan untuk menghindari sanksi.
4. **Ganti field `phone` → `receiver`.** Docs Kirimi terbaru menandai `receiver` sebagai wajib. Sub-workflow sudah mengirim keduanya, jadi aman ke dua arah — tapi konfirmasikan sekali setelah blokir dibuka.
