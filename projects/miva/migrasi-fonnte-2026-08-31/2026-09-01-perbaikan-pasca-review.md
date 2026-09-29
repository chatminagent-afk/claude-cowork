# Perbaikan pasca-review — 2026-09-01

Review ulang atas 14 workflow hasil konversi 2026-08-31. Semua file di folder ini diperbarui **di tempat**; produksi tetap tidak tersentuh.

---

## 1. Guard respons di tiga error notifier — **cacat sungguhan**

**File:** `VIRA TS Error Notifier`, `VIRA-PCR Error Notifier`, `GLOBAL - VIRA Error Notifier`

Kemarin aku hanya mengonversi `Check Kirimi Response` di *VIRA Personal*. Tiga notifier lain punya node yang sama dan terlewat. Isinya:

```js
const isSuccess = r.status === true || r.success === true ||
                  (r.data && r.data.id) || (r.message && r.message !== 'error');
```

Baris terakhir itu masalahnya. Respons **gagal** dari Fonnte bisa membawa field `message`; kalau itu terjadi, kegagalan lolos sebagai sukses, error tidak dilempar, jalur email fallback tidak jalan, dan notifikasi hilang tanpa jejak — persis pola yang jadi alasan node ini dibuat.

Bukan berarti selalu rusak: untuk respons sukses biasa (`status: true`) dan respons gagal berbentuk array, logika lama kebetulan tetap benar. Yang berbahaya adalah bentuk gagal yang membawa `message`.

Sekarang: hanya `status === true` yang diterima, respons array maupun objek ditangani, dan alasan kegagalan ikut dicetak di pesan error. Node di-rename jadi `Check Fonnte Response`.

## 2. `filename` pada node kirim media — **cacat sungguhan**

**File:** `VIRA PCR AI Powered`, `VIRA Personal — Main` (2 node masing-masing)

Fonnte menentukan cara WhatsApp merender lampiran dari **ekstensi `filename`** — tanpa ekstensi, media gagal render. Kirimi tidak butuh itu, jadi konversi kemarin tidak membawanya. Sekarang tiap node media punya parameter `filename`:

```
{{ $binary.data.fileName && $binary.data.fileName.includes('.')
   ? $binary.data.fileName
   : 'media' + ($binary.data.fileExtension ? '.' + $binary.data.fileExtension : '') }}
```

Kalau biner hasil `Download Media` tidak membawa nama maupun ekstensi, hasilnya sama seperti sebelumnya (tanpa ekstensi) — tidak lebih buruk, tapi kasus umum jadi benar. **Uji kirim brosur PDF dan satu gambar** setelah migrasi.

## 3. Notifikasi tes bisa nyasar ke Sam — **risiko nyata**

**File:** `VIRA TS Fonnte v2`

`Notify Admin Unknown` dan `Notify Talk to Sam` masih memakai nilai produksi `6596110395`, sementara panduan menyuruh menggantinya untuk produksi — panduannya salah, karena file-nya memang sudah berisi nomor Sam. Artinya menguji alur "UNKNOWN" akan mengirim notifikasi tes ke klien.

Sekarang diarahkan ke `6285171701168` dengan `notes` pengingat di node, dan panduan TS dikoreksi.

## 4. Whitelist TS

`6285171701168` — nomor yang kamu pakai tes kemarin — tidak ada di `IF (Whitelist)`, jadi pesanmu akan berhenti di node itu. Ditambahkan sebagai kondisi ke-6.

## 5. Tabrakan device ↔ target notifikasi

Tujuh node notifikasi menargetkan `6285155202354`. Itu nilai warisan produksi dan **benar** selama tiap klien memakai device Fonnte sendiri. Tapi nomor itu juga device Fonnte "Work" milikmu — kalau credential sebuah workflow menunjuk ke device itu, notifikasinya jadi kirim-ke-diri-sendiri.

Nomornya **tidak** kuubah: menebak nomor tujuan notifikasimu bukan keputusan yang pantas kuambil sendiri. Sebagai gantinya ketujuh node diberi `notes` yang tampil di kanvas n8n, berisi peringatan dan alternatifnya.

Node terdampak: `Notify Admin Error` (TS/PCR/GLOBAL notifier), `Notify Maintenance` (GLOBAL Sheet Cleanup, PCR STATS Purge), `Notify Steven` (TS STATS Cleanup), `Notify Admin FU Summary` (PCR Follow-up).

## 6. Kebersihan yang berdampak

- **Nama node**: `Send Media Kirimi` → `Send Media (Fonnte)` (+ `2`). Tidak ada lagi nama node yang menyebut gateway lama.
- **Sticky note pemasangan** di tiga error notifier masih memuat instruksi menyambungkan `Check Kirimi Response` — node yang sudah tidak ada. Sudah ditulis ulang sesuai keadaan sekarang.
- **`Siapkan Notif Deck`** (VIRA Personal Main) masih menyusun `user_code`/`secret`/`device_id` dari config yang sudah dihapus. Tiga field mati itu dibuang.
- **17 komentar & sticky** yang menyebut gateway atau node lama diperbarui, termasuk `Sticky Note Skala` (PCR Follow-up) dan `V2 Vision - Area Baru`. Yang terakhir kini menyuruh **menguji lebih dulu apakah URL media Fonnte publik** — host-nya berubah, dan alur Vision mengandalkan Anthropic bisa mengambil URL itu.
- **Email fallback** dibuat netral gateway di teks dan pesan e-mailnya.

Yang **sengaja dibiarkan**: konstanta `source: 'kirimi_fallback'`. Itu protokol antar-workflow yang dibaca `GLOBAL - Email Fallback Notifier`, bukan referensi ke API Kirimi. Sudah diberi komentar penjelas, dan versi Fonnte email fallback menerima `kirimi_fallback` maupun `fonnte_fallback`.

---

## Yang masih terbuka, dan kenapa belum kukerjakan

**Konfirmasi pengiriman (`status: true` ≠ terkirim).** Fonnte punya webhook *update message status* dengan field `device`, `id`, `stateid`, `status`, `state`. Tapi dokumentasinya **tidak mencantumkan nilai yang mungkin** untuk `status`/`state` — tidak ada daftar `delivered`/`read`/`failed`.

Membangun alerting di atas nilai yang kutebak berarti menaruh tebakan tepat di tempat yang menentukan apakah "pesan gagal" terdeteksi. Itu bertentangan dengan seluruh tujuan pekerjaan ini.

Yang bisa dikerjakan tanpa menebak: workflow kecil yang menerima webhook status dan mencatat payload apa adanya ke satu tab Sheets. Setelah beberapa hari kamu punya daftar nilai sungguhan, dan aturan alert ditulis dari data. Bilang saja kalau mau kubuatkan.
