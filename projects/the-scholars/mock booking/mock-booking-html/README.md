# Mock Interview Booking — The Scholars
## Versi: Single HTML File

Tidak perlu Node.js, npm, atau build step apapun.
Buka `index.html` langsung di browser untuk test.

---

## Setup (2 langkah saja)

### Langkah 1 — Isi webhook URL
Buka `index.html` dengan text editor, cari bagian CONFIG di atas:

```js
const CONFIG = {
  WEBHOOK_URL: 'https://YOUR_N8N_HOST/webhook/mock-booking',
  MOCK_MODE: true,
}
```

Ganti `YOUR_N8N_HOST` dengan domain/IP n8n kamu.
Contoh: `https://n8n.thescholars.id/webhook/mock-booking`

### Langkah 2 — Aktifkan live data (setelah n8n siap)
Di bagian yang sama, ganti:
```js
MOCK_MODE: false
```

---

## Deploy ke Hostinger

Upload file `index.html` ke folder web root di Hostinger.
Selesai. Tidak ada langkah lain.

Via cPanel File Manager atau FTP ke: `/public_html/` atau subfolder sesuai domain kamu.

---

## Payload yang dikirim ke n8n (POST JSON)

```json
{
  "idBooking"  : "MI-20260614-483",
  "tanggal"    : "Sabtu, 14 Jun 2026",
  "noWa"       : "6281234567890",
  "nama"       : "Budi Santoso",
  "jamMulai"   : "10:00",
  "jamSelesai" : "12:00",
  "slotId"     : "1",
  "status"     : "Pending",
  "timestamp"  : 1749859200
}
```

## Response yang diharapkan dari n8n

**Sukses** → HTTP 200, body apapun

**Slot sudah penuh (race condition):**
```json
{ "error": "SLOT_TAKEN" }
```
HTTP 409 — website otomatis tampilkan pesan error dan reset dropdown.

---

## Cara Sam kelola jadwal (sheet MOCK_SLOTS)

| Aksi | Cara |
|------|------|
| Tambah slot baru | Tambah row baru di sheet MOCK_SLOTS |
| Cancel booking / buka lagi | Kosongkan kolom `booked` di row yang bersangkutan |
| Tutup semua slot | Isi `booked=Y` di semua row |
