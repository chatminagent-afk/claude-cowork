# Panduan Fix: VIRA Crash & Tidak Membalas Saat User Kirim Gambar/Stiker

**Tanggal:** 2026-06-27
**File live terdampak:** `enhancement boros v2 vira 18 juni/VIRA V3.1 fixing greeting Y & unknown.json`
**Status:** Belum di-patch. Panduan ini untuk dikerjakan manual di n8n oleh Sam/Steven.
**Sifat:** Step-by-step, dengan rencana QA & rollback.

---

## 1. Ringkasan & Root Cause (sudah terbukti dari data)

**Gejala:** VIRA tidak membalas user. Error tertangkap di node `Read User STATS`:
`Cannot read properties of undefined (reading 'toString')`.

**Pemicu:** user mengirim **gambar** (atau stiker) — bukan teks.

**Rantai kejadian (terbukti dari output node yang kamu kirim):**

1. Webhook menerima pesan gambar: `messageType: "image"`, `message: ""`, `from: 6282230300382`, `originLid: 117536108593389` (user Tri Agustina/Noah — sama dengan screenshot).
2. Node `Chat Counter` punya guard non-teks: `if (messageType !== "text" ...) return [];` → seharusnya **berhenti** (output kosong `[]`).
3. **MASALAH UTAMA:** node `Chat Counter` di-set **`Always Output Data = true`**. Setting ini memaksa n8n mengubah `[]` menjadi **satu item kosong `[{}]`** (persis output yang kamu lihat: `[{}]`). Jadi guard `return []` jadi sia-sia — aliran tetap jalan membawa item kosong.
4. Item kosong `{}` masuk ke `Read User STATS`. Parameter lookup-nya `lookupValue = {{ $json.user_wa }}`. Di item kosong, `user_wa` = **undefined**.
5. Node Google Sheets memanggil `.toString()` pada nilai undefined → **crash** → eksekusi mati → **VIRA tidak balas**.
   (Ditambah `Read User STATS` punya `retryOnFail = true`, jadi node sempat retry crash beberapa kali sebelum gagal total.)

**Yang TERBUKTI BUKAN penyebab:** kompilasi `pending_msg` tidak terlibat; sel `No WA` kosong juga bukan (di sheet live kolom `No WA` terisi semua). Pemicunya murni `user_wa` undefined dari item kosong.

---

## 2. Kenapa fix inti otomatis membalas "bubble teks di atas gambar"

Penting dipahami sebelum patch — ini mekanisme debounce yang sudah ada:

- Setiap pesan teks → ditulis ke kolom `pending_msg` + kolom `timestamp` (diisi `process_start_ts` pesan itu) lewat node `Update Buffer`.
- Lalu menunggu di `Wait3` = **60 detik**.
- Lalu `Re-Read STATS Debounce` membaca ulang baris, dan `IF_Chat_Debounce` membandingkan:
  `Re-Read.timestamp == Chat Counter.process_start_ts`.
  - **Sama** → pesan ini adalah yang **terakhir** ("the closer") → lanjut → VIRA membalas berisi **seluruh `pending_msg`** (semua bubble teks).
  - **Beda** → ada pesan lebih baru sesudahnya → eksekusi ini berhenti (tidak balas).

**Di insiden kemarin:** gambar adalah pesan terakhir, tetapi ia **crash di `Read User STATS` sebelum sempat menulis `timestamp`/jadi closer** → buffer teks tak pernah di-flush → tidak ada balasan sama sekali.

**Setelah Bagian A (gambar di-drop bersih, tidak crash):** karena gambar tidak menulis timestamp baru, **closer-nya otomatis jatuh ke pesan teks terakhir** (mis. "…join kelas sec3"). Setelah 60 detik, VIRA membalas seluruh teks di atas gambar. **Jadi tujuan "tetap balas bubble di atasnya" tercapai hanya dengan Bagian A — tanpa cabang tambahan.**

> Satu-satunya kasus yang tidak otomatis terbalas: **gambar berdiri sendiri** (tidak ada teks di atasnya). Untuk itu ada Bagian B (opsional).

---

## 3. SEBELUM MULAI — Backup (wajib)

1. Buka workflow VIRA live di n8n.
2. Menu titik-tiga (kanan atas) → **Download**. Simpan sebagai mis. `VIRA_backup_sebelum_fix_2026-06-27.json`.
3. Pastikan tahu cara import balik (menu → Import from File) untuk rollback.

---

## 4. BAGIAN A — Fix Inti (WAJIB, ±2 menit) — Hentikan Crash + Pulihkan Balasan Teks

1. Di canvas, **double-click** node **`Chat Counter`**.
2. Klik tab **Settings** (di header panel node, sebelah "Parameters").
3. Cari opsi **Always Output Data** → **matikan (toggle OFF)**.
4. Tutup node, lalu **Save** workflow.

**Efek:**
- Pesan gambar/stiker → `Chat Counter` mengembalikan `[]` → cabang berhenti rapi → tidak ada lagi crash `toString`.
- Bubble teks di atas gambar **otomatis terbalas** oleh mekanisme debounce (lihat bagian 2).

> Opsional kebersihan: node `Read User STATS` → tab Settings → matikan **Retry On Fail** (saat ini ON; hanya memperlambat kegagalan tanpa menolong).

**Untuk banyak kasus, Bagian A sudah cukup.** Lanjut ke Bagian B hanya bila kamu mau VIRA memberi catatan sopan saat user mengirim **gambar tanpa teks apa pun**.

---

## 5. BAGIAN B — (Opsional) Catatan Sopan untuk Gambar yang Berdiri Sendiri

Tujuan: kalau user kirim gambar/stiker **tanpa ada teks di buffer**, VIRA balas singkat agar user tidak bingung. Dirancang agar **TIDAK dobel-balas** saat ada teks di atasnya (kasus itu sudah ditangani Bagian A), dan tetap menghormati HITL (`bot_mode = OFF`). Mengikuti pola existing (`IF` + `Read STATS` + `HTTP Reply`).

### B.1 — Node `IF Is Text`

1. Arahkan kursor ke **garis koneksi** antara `IF (Whitelist)` dan `Chat Counter` → klik tombol **+**.
2. Tambah node **IF**, beri nama **`IF Is Text`**.
   - **Value 1:** `={{ $json.body.messageType }}`
   - **Operation:** String → **is equal to**
   - **Value 2:** `text`
3. Pastikan wiring: `IF (Whitelist)` → `IF Is Text`; output **TRUE** → `Chat Counter` (alur normal).

### B.2 — Node baca STATS (untuk cek buffer + bot_mode)

1. Duplikasi node **`Read STATS for HITL`** (read sheet STATS polos, tanpa filter). Beri nama **`Read STATS Non-Text`**.
2. Sambungkan `IF Is Text` (**output FALSE**) → `Read STATS Non-Text`.

### B.3 — Node Code `Cek Non-Text`

1. Tambah node **Code** sesudahnya, beri nama **`Cek Non-Text`**. Isi:
   ```javascript
   const body = $('Webhook').first().json.body || {};
   const userLid = String(body.originLid || '').replace(/\D/g, '');
   const rows = $('Read STATS Non-Text').all();
   const row = rows.find(r => String(r.json['lid'] || '').trim() === userLid);

   const botMode    = row ? String(row.json['bot_mode']    || '').trim().toUpperCase() : '';
   const pendingMsg = row ? String(row.json['pending_msg'] || '').trim()                : '';

   // 1) Sam handle manual → jangan kirim apa pun
   if (botMode === 'OFF') {
     console.log(`👨‍💼 HITL aktif (lid ${userLid}) — non-text diabaikan.`);
     return [];
   }
   // 2) Ada teks di buffer → biarkan debounce yang membalas teksnya (hindari dobel)
   if (pendingMsg !== '') {
     console.log(`📝 Ada teks di buffer (lid ${userLid}) — non-text diabaikan, debounce yang balas.`);
     return [];
   }
   // 3) Gambar/stiker berdiri sendiri → kirim catatan sopan
   return [{ json: { phone: body.from } }];
   ```
2. Sambungkan `Read STATS Non-Text` → `Cek Non-Text`.

### B.4 — Node `Reply Catatan Non-Text`

1. Duplikasi node **`Reply Chat Kirimi`** (Ctrl+C / Ctrl+V). Beri nama **`Reply Catatan Non-Text`**.
2. Biarkan `user_code`, `secret`, `device_id` apa adanya. Ubah dua field:
   - **phone:** `={{ $json.phone }}`
   - **message:**
     ```
     =Maaf kak 🙏 untuk saat ini aku belum bisa membaca gambar atau stiker. Boleh tolong ketik pertanyaannya dalam bentuk teks ya, nanti aku bantu jawab 😊
     ```
3. Sambungkan `Cek Non-Text` → `Reply Catatan Non-Text`.
4. **Save** workflow.

**Wiring akhir (dengan Bagian B):**
```
IF (Whitelist) ─► IF Is Text ─(TRUE: teks)─► Chat Counter ─► (alur normal + debounce balas teks)
                            └─(FALSE)─► Read STATS Non-Text ─► Cek Non-Text ─► Reply Catatan Non-Text
                                                                    │ (return [] jika HITL OFF
                                                                    │  atau ada teks di buffer)
```

---

## 6. Rencana QA (lakukan sebelum dianggap selesai)

Pakai satu nomor WA test. Setelah tiap test, cek **n8n → Executions** (tidak boleh ada error).

| # | Aksi | Ekspektasi |
|---|------|-----------|
| 1 | Kirim 1 pesan **teks** normal | VIRA balas seperti biasa (regression — alur teks tak berubah) |
| 2 | Kirim **teks lalu gambar** (urutan persis insiden) | Tidak ada error `toString`. Setelah debounce (±60 dtk), VIRA **membalas teksnya**. Bagian B: tidak ada catatan tambahan (karena ada teks di buffer) |
| 3 | Kirim **gambar berdiri sendiri** (tanpa teks) | Tidak ada error. Bagian A saja: tidak ada balasan. Bagian B: VIRA kirim catatan sopan |
| 4 | (Bagian B) set `bot_mode` = **OFF** lalu kirim gambar | Tidak ada catatan terkirim; tidak ada error |
| 5 | Buka Executions, filter error | Tidak ada lagi error `Cannot read properties of undefined (reading 'toString')` di `Read User STATS` |

> Catatan QA: `Wait3` = 60 detik, jadi balasan teks pada Test 2 muncul ±1 menit setelah pesan terakhir — itu normal (perilaku debounce existing), bukan bug.

---

## 7. Rollback

- **Bagian A:** nyalakan kembali `Always Output Data` di `Chat Counter`.
- **Bagian B:** hapus node `IF Is Text`, `Read STATS Non-Text`, `Cek Non-Text`, `Reply Catatan Non-Text`, lalu sambungkan kembali `IF (Whitelist)` → `Chat Counter` langsung.
- Atau import ulang backup dari Langkah 3.

---

## 8. Catatan & temuan tambahan (diflag, bukan bagian fix ini)

1. **Inkonsistensi lookup:** `Read User STATS` adalah satu-satunya node lookup user yang masih memakai kolom `No WA`; node lain sudah pindah ke `lid`. Sebaiknya diselaraskan ke `lid` agar konsisten dengan arsitektur pasca-migrasi LID. (Utang teknis, bukan penyebab kasus ini.)
2. **Kredensial Kirimi plaintext:** `user_code` & `secret` tertulis langsung di body node HTTP (termasuk node reply baru). Disarankan pindah ke n8n Credentials + rotasi secret. (Sudah diflag di analisa 2026-06-25.)
3. **Webhook `wa-inbound` tanpa auth** — relevan untuk hardening terpisah.

---

## Lampiran — Nilai field Kirimi (referensi node `Reply Chat Kirimi` live)

```
method   : POST
url      : https://api.kirimi.id/v1/send-message
body     : user_code = KM40LI0426
           secret    = (sama seperti node asli)
           device_id = D-4ZV1F
           phone     = {{ $json.phone }}     ← untuk Reply Catatan Non-Text (Bagian B)
           message   = (teks catatan di B.4)
```
