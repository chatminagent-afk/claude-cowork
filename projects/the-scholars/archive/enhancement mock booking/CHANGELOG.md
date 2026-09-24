# Enhancement Log

---

## v3 — Write-First Submission + Graceful Booking Not Found
**File:** `VIRA_MockBooking_Generator_Payment_v3.json`  
**Tanggal:** 2026-06-09

### Problem yang Diselesaikan (v3)

**Skenario bug:** Dua peserta submit booking slot yang sama secara bersamaan. Hanya satu yang berhasil tertulis di sheet. Peserta yang datanya hilang tetap mendapat notif WA ke Sam (karena WA sudah dikirim sebelum data ter-write). Ketika Sam membuka link confirm peserta tersebut, halaman **kosong/blank** dan flow n8n berhenti di `Check Booking Exists`.

### Perubahan di v3

#### Submission Flow — Write-First

Node urutan baru setelah `Validate Payload`:

| Urutan lama | Urutan baru (v3) |
|---|---|
| Validate Payload → Read Slot → Check Slot → (taken) Return 409 | Validate Payload → **Append** → Read Slot → Check Slot → (taken) **Mark Booking Failed** → Return 409 |
| Flag Slot → **Append** → Notify Sam | Flag Slot → Notify Sam *(Append sudah dilakukan sebelumnya)* |

**Alasan:** Dengan write-first, SEMUA submit tercatat di `MOCK_INTERVIEW_BOOKING` terlebih dahulu — tidak ada data yang hilang. Jika slot ternyata sudah diambil, row tersebut di-update ke status `Gagal - Slot Penuh`.

**Node baru:**
- **`Mark Booking Failed`** *(Google Sheets update)*: di-trigger ketika `Slot Taken? = TRUE`. Update status booking (match by `ID Booking`) ke `"Gagal - Slot Penuh"`. Sam **tidak** menerima notif untuk booking yang gagal ini.

**Node dimodifikasi:**
- **`Append to MOCK_INTERVIEW_BOOKING`**: dipindah ke sebelum slot check. Referensi kolom diubah dari `$('Check Slot Availability')` → `$('Validate Payload')`.
- **`Flag Slot Booked`**: sekarang langsung terhubung ke `Notify Sam` (Append sudah terjadi lebih awal).

#### Confirm Flow — Graceful "Booking Not Found"

**Node dimodifikasi:**
- **`Check Booking Exists`**: tidak lagi `throw new Error`. Sekarang mengembalikan `{ bookingFound: false, id }` jika booking tidak ditemukan.

**Node baru:**
- **`Booking Found?`** *(IF)*: branch setelah `Check Booking Exists`.
  - TRUE → lanjut ke `Read CONFIG` (flow normal)
  - FALSE → `Build Not Found HTML` → `Return HTML Not Found`
- **`Build Not Found HTML`** *(Code)*: render halaman HTML informatif untuk Sam, berisi penjelasan bahwa booking tidak terdaftar dan saran untuk minta peserta daftar ulang.
- **`Return HTML Not Found`** *(Respond to Webhook)*: kirim halaman ke Sam.

### Koneksi yang Diubah (v3)

| Dari | Output | Dulu | Sekarang |
|------|--------|------|----------|
| `Validate Payload` | main[0] | `Read Slot by ID` | `Append to MOCK_INTERVIEW_BOOKING` |
| `Append to MOCK_INTERVIEW_BOOKING` | main[0] | `Notify Sam` | `Read Slot by ID` |
| `Slot Taken?` | TRUE | `Return 409 Slot Taken` | `Mark Booking Failed` |
| `Mark Booking Failed` | main[0] | *(baru)* | `Return 409 Slot Taken` |
| `Flag Slot Booked` | main[0] | `Append to MOCK_INTERVIEW_BOOKING` | `Notify Sam` |
| `Check Booking Exists` | main[0] | `Read CONFIG` | `Booking Found?` |
| `Booking Found?` | TRUE | *(baru)* | `Read CONFIG` |
| `Booking Found?` | FALSE | *(baru)* | `Build Not Found HTML` |

### Skenario & Hasilnya (v3)

**Skenario: Ferdy & Sherlyn submit bersamaan**
1. Kedua execution start → kedua booking **di-append ke sheet** terlebih dahulu ✅
2. Kedua check slot → satu (misal Sherlyn) lebih dulu lolos, flagging slot sebagai Booked=Y
3. Ferdy's execution: slot sudah Booked=Y → `Mark Booking Failed` → Ferdy's row di-update ke `Gagal - Slot Penuh` → Return 409 ke browser Ferdy ✅
4. Sam hanya menerima satu notif (Sherlyn) ✅
5. Tidak ada stale confirm link untuk Ferdy ✅

**Skenario: Sam membuka link booking yang tidak ada di sheet (kasus lama)**
- Flow berhenti di `Booking Found? = FALSE` → Sam melihat halaman informatif: *"Booking ini tidak ditemukan — minta peserta daftar ulang"* ✅ (tidak lagi blank)

### Cara Import

1. Buka n8n → Import from File
2. Pilih `VIRA_MockBooking_Generator_Payment_v3.json`
3. Aktifkan workflow
4. **Nonaktifkan** v2 dan workflow lama (`VIRA_MockBooking_Generator_Payment.json`)
5. Pastikan hanya **satu** workflow yang aktif untuk webhook path `mock-booking-submit`

> **Penting:** `maxConcurrency: 1` sudah diset di semua versi workflow. Write-first adalah lapisan perlindungan tambahan untuk edge case di mana dua execution sempat overlap sebelum lock teraplikasi.

---

## v2 — Slot Conflict Detection (Race Condition Fix — Confirm Flow)
**File:** `VIRA_MockBooking_Generator_Payment_v2.json`  
**Tanggal:** 2026-06-09

---

## Problem yang Diselesaikan

Jika 2 orang submit booking untuk slot yang sama secara bersamaan, keduanya bisa masuk ke sheet `MOCK_INTERVIEW_BOOKING` dengan status Pending. Workflow lama tidak punya mekanisme untuk mencegah Sam mengkonfirmasi keduanya — atau lebih buruk, me-reject booking kedua yang secara tidak sengaja membebaskan slot milik booking pertama yang sudah dikonfirmasi.

---

## Perubahan di Workflow

### Node yang dimodifikasi

**1. `Parse Confirm Request`**
- Tambah parsing parameter `skip_free` dari query string
- Output baru: `{ id, action, skipFree }`

**2. `Build Confirm Data`**
- Ambil `skipFree` dari `Parse Confirm Request` dan teruskan ke downstream
- Output baru: `{ ..., skipFree: boolean }`

### Node baru (6 node)

**3. `Read Bookings Same Slot`** *(Google Sheets)*
- Baca semua baris di `MOCK_INTERVIEW_BOOKING` yang punya `Slot ID` = slot yang sedang diproses

**4. `Check Slot Conflict`** *(Code)*
- Filter hasil read untuk mencari booking lain (bukan booking saat ini) yang sudah `Status = Confirmed`
- Hitung dua flag:
  - `hasConflict` — apakah ada konflik
  - `showConflictPage` — apakah harus tampilkan halaman konflik (true jika ada konflik DAN ini bukan force-reject)
- Jika ada konflik, ambil info peserta pemenang (nama, ortu, sekolah, kelas, no WA, ID booking)

**5. `Slot Conflict?`** *(IF)*
- TRUE (showConflictPage = true) → tampilkan halaman konflik
- FALSE → lanjut ke `Confirm or Reject?` seperti biasa

**6. `Build Slot Conflict HTML`** *(Code)*
- Render halaman HTML `🚫 Jadwal Sudah Di-book Peserta Lain`
- Tampilkan info lengkap peserta yang sudah dikonfirmasi
- Sertakan tombol **"Tolak Booking Duplikat"** yang mengarah ke `?id=[id]&action=reject&skip_free=1`

**7. `Return HTML Slot Conflict`** *(Respond to Webhook)*
- Kirim halaman HTML konflik ke Sam

**8. `Should Free Slot?`** *(IF)*
- Disisipkan di antara `Update Status Rejected` dan `Free Slot`
- TRUE (skipFree = false) → jalankan `Free Slot` seperti biasa
- FALSE (skipFree = true) → langsung ke `Send WA Rejection`, lewati `Free Slot`
- Mencegah slot milik booking yang sudah dikonfirmasi ter-free secara tidak sengaja

### Koneksi yang diubah

| Dari | Output | Dulu menuju | Sekarang menuju |
|------|--------|-------------|-----------------|
| `Already Processed?` | FALSE | `Confirm or Reject?` | `Read Bookings Same Slot` |
| `Update Status Rejected` | main | `Free Slot` | `Should Free Slot?` |

---

## Skenario & Hasilnya

### Skenario 1: Sam konfirmasi A, lalu buka link B (slot sama)
1. Sam buka link confirm untuk booking A → dikonfirmasi, slot Booked=Y
2. Sam buka link confirm/reject untuk booking B (slot sama, masih Pending)
3. `Check Slot Conflict` menemukan A sudah Confirmed untuk slot yang sama
4. Sam melihat halaman **"🚫 Jadwal Sudah Di-book Peserta Lain"** dengan info lengkap peserta A
5. Sam bisa klik **"Tolak Booking Duplikat (B)"** → B di-reject, slot TIDAK dibebaskan ✅

### Skenario 2: Sam tolak A, lalu buka link B (slot sama)
1. Sam buka link reject untuk booking A → A di-reject, slot dibebaskan (Booked="")
2. Sam buka link confirm/reject untuk booking B
3. `Check Slot Conflict` → tidak ada booking lain dengan Status=Confirmed untuk slot ini
4. Sam bisa confirm/reject B secara normal ✅

### Skenario 3: Submit tunggal (normal)
- Tidak ada perubahan behavior — `showConflictPage = false` → flow lama berjalan normal ✅

---

## Cara Import

1. Buka n8n → Import from File
2. Pilih `VIRA_MockBooking_Generator_Payment_v2.json`
3. Aktifkan workflow
4. Nonaktifkan/hapus workflow lama (`VIRA_MockBooking_Generator_Payment.json`)

> **Catatan:** Tidak ada perubahan di Google Sheet schema, HTML booking form, atau workflow generator slot.
