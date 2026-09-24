# VIRA V4 r2 — 3 Verdict Pendaftaran + Jaring Pengaman Tanggal + DATA Menang atas FAQ

**Tanggal:** 2026-08-12
**Basis:** `2026-08-12-VIRA-V4-r1-status-batch.json`
**Hasil:** `2026-08-12-VIRA-V4-r2-status-batch.json` — **kumulatif** (transfer + batch + r2). Ini yang di-import.
**Pemicu:** dropdown 4 status di sheet PROGRAM + log produksi yang membuktikan kontaminasi FAQ.

---

## Bukti dari log produksi

Pertanyaan `"kapan batch berikutnya dimulai?"` dijawab:

> "Batch 5 **rencananya** mulai **15 Agustus 2026** yaa, pendaftarannya sudah dibuka sekarang."

Model mencampur dua sumber yang bertentangan:

| Sumber | Isi |
|---|---|
| DATA TERVERIFIKASI | `Junior: PENDAFTARAN DIBUKA ... Program mulai 15 Agustus 2026` |
| FAQ RELEVAN | `Q: Kapan batch berikutnya mulai? A: Batch 5 **rencananya** mulai **akhir Agustus 2026**. **Stay tuned** untuk info resminya ya!` |

Tanggalnya diambil dari DATA (benar), tapi kata ragu `"rencananya"` dicomot dari FAQ. Penyebabnya: system message menaruh kedua sumber **sejajar** —

```
L8 : Semua fakta HANYA boleh dari dua sumber di bawah pesan ini: DATA TERVERIFIKASI dan FAQ RELEVAN.
L21: JAWAB: ambil fakta dari DATA TERVERIFIKASI / FAQ RELEVAN.
```

Tidak ada aturan siapa menang, jadi model bebas memilih atau mencampur.

---

## Perubahan (2 node, 7 titik)

Jumlah node tetap 53, `connections` identik.

### 1. `FAQ Retrieve` — 3 verdict, selaras dropdown Sam

Dropdown di sheet PROGRAM: **`Active` · `Coming Soon` · `Closed` · `Always Active`**.

```js
const ALWAYS_RE = /always|selalu/i;
const SOON_RE   = /(coming\s*soon|belum\s*dibuka|belum\s*buka|akan\s*datang)/i;
const CLOSED_RE = /(closed|close|tutup|ditutup|penuh|full|selesai|inactive|tidak\s*aktif|non\s*-?\s*aktif)/i;
const OPEN_RE   = /(active|aktif|open|buka|dibuka|berjalan|ongoing)/i;
```

Urutan pemeriksaan **ALWAYS → SOON → CLOSED → OPEN** wajib: `Always Active` mengandung kata `Active`, dan `Coming Soon`/`Belum dibuka` mengandung `belum`/`dibuka`. Kalau OPEN dicek duluan, ketiganya salah terbaca.

Verdict lama hanya 2 nilai (DIBUKA/DITUTUP). Sekarang 3, plus satu keadaan gagal:

| Verdict | Kapan |
|---|---|
| `PENDAFTARAN DIBUKA` | `Active` (tanggal masih berlaku) atau `Always Active` |
| `PENDAFTARAN BELUM DIBUKA` | `Coming Soon` |
| `PENDAFTARAN SUDAH DITUTUP` | `Closed`, atau jaring pengaman tanggal di bawah |
| `STATUS PENDAFTARAN TIDAK JELAS` | isi kolom di luar dropdown / kosong → AI diminta `[UNKNOWN]` |

### 2. Jaring pengaman tanggal — untuk kasus Sam lupa update Status

Kolom `Status` tetap yang utama. Tanggal **hanya** dipakai saat Status jelas-jelas sudah basi:

| Status | Kondisi tanggal | Hasil |
|---|---|---|
| `Active` | `Deadline Daftar` sudah lewat | → **SUDAH DITUTUP** + `console.warn` |
| `Active` | tanpa deadline, `Tanggal Mulai` sudah lewat | → **SUDAH DITUTUP** + warn |
| `Coming Soon` | `Tanggal Mulai` sudah lewat | → **SUDAH DITUTUP** + warn |
| `Closed` | apa pun | → **SUDAH DITUTUP** (final) |
| `Always Active` | apa pun | → **DIBUKA** (tanggal diabaikan) |

Alasan penutupan ikut dikirim ke AI supaya balasannya bisa spesifik:

```
Junior: PENDAFTARAN SUDAH DITUTUP (deadline daftar 8 Agustus 2026 sudah lewat), Batch 5,
Program mulai 15 Agustus 2026, Deadline daftar 8 Agustus 2026, Kuota 15 per kelas
```

Setiap kali jaring pengaman aktif, muncul `STATUS BASI: ...` di execution log — itu penanda kolom Status di sheet perlu diperbarui.

Catatan: patch sebelumnya **menyembunyikan** deadline yang sudah lewat. Sekarang tidak perlu lagi — verdict-nya sudah cocok dengan tanggalnya, jadi datanya konsisten dan boleh ditampilkan penuh.

### 3. `systemMessage` — DATA menang atas FAQ

```
- PRIORITAS SUMBER: untuk status pendaftaran, nama batch, tanggal, harga, dan kuota ->
  DATA TERVERIFIKASI SELALU MENANG atas FAQ RELEVAN. FAQ hanya untuk penjelasan/kebijakan.
- Kalau FAQ bertentangan dengan DATA TERVERIFIKASI: IKUTI DATA, ABAIKAN FAQ. Jangan
  menggabungkan keduanya, dan jangan memakai kata ragu dari FAQ ("rencananya", "stay tuned",
  "kemungkinan") kalau DATA sudah menyatakan pasti.
```

Kata `"rencananya"` dan `"stay tuned"` disebut eksplisit karena itu persis yang bocor di log.

### 4. `systemMessage` — 3 balasan berbeda

Sebelumnya `SUDAH DITUTUP` dan `BELUM DIBUKA` dijawab dengan kalimat yang sama — *"pendaftarannya belum dibuka yaa"* — padahal artinya berlawanan.

```
* PENDAFTARAN DIBUKA -> boleh kirim link, boleh sebut kuota/deadline apa adanya dari DATA.
* PENDAFTARAN BELUM DIBUKA -> "Untuk Batch berikutnya pendaftarannya belum dibuka yaa,
  nanti saya kabari kalau sudah buka."
* PENDAFTARAN SUDAH DITUTUP -> "Untuk Batch <nama dari DATA> pendaftarannya sudah ditutup yaa."
  DILARANG bilang "belum dibuka" untuk kasus ini - itu dua hal berbeda.
```

### 5. `systemMessage` — "tidak ada di DATA" bukan lagi "belum dibuka"

Aturan lama menyamakan **data kosong** dengan **belum dibuka**. Log run pertama membuktikan ini berbahaya: pada eksekusi itu SELURUH blok dari sheet kosong (`STATUS & BATCH`, `HARGA`, `PROGRAM`, `LINK AKTIF`, dan `faq_context`) — hanya `PEMETAAN PROGRAM` yang tersisa. Dengan aturan lama, kegagalan baca sheet membuat VIRA **yakin** menyatakan pendaftaran belum dibuka.

```
- STATUS PENDAFTARAN TIDAK JELAS, atau program/batch tidak ada barisnya di DATA -> JANGAN
  menebak dan JANGAN bilang "belum dibuka". Jawab [UNKNOWN] khusus untuk status itu.
```

### 6. `[SEND_GFORM]` diperketat

Syaratnya diperjelas: `BELUM DIBUKA`, `SUDAH DITUTUP`, atau `TIDAK JELAS` → dilarang memasang tag, jadi link pendaftaran tidak akan terkirim saat pendaftaran tutup.

---

## ⚠️ Efek langsung yang harus Sam tahu

Dengan jaring pengaman tanggal aktif, **hari ini Batch 5 jadi `SUDAH DITUTUP`** — karena `Deadline Daftar = 8 Agustus 2026` sudah lewat, meskipun `Status` masih `Active`.

```diff
- Junior: PENDAFTARAN DIBUKA (kolom Status=Active), Batch 5, Program mulai 15 Agustus 2026
+ Junior: PENDAFTARAN SUDAH DITUTUP (deadline daftar 8 Agustus 2026 sudah lewat), Batch 5, ...
```

Kalau pendaftaran Batch 5 **sebenarnya masih dibuka**, Sam harus **menggeser `Deadline Daftar`** di sheet. Mengubah `Status` saja tidak cukup — sesuai permintaan, tanggal memang dijadikan acuan saat Status berpotensi basi.

Status per program hari ini:

| Program | Verdict |
|---|---|
| Junior | `SUDAH DITUTUP` (deadline lewat) |
| Intermediate | `SUDAH DITUTUP` (deadline lewat) |
| Seniors | `DIBUKA` (Active, tanpa tanggal) |
| Mock Interview | `DIBUKA` (Always Active) |

---

## Yang harus Sam perbaiki di sheet FAQ

**Prinsip: FAQ tidak boleh memuat fakta yang sudah ada di sheet PROGRAM** (tanggal, harga, status, kuota). Duplikasi = sumber kontradiksi. FAQ untuk penjelasan & kebijakan yang jarang berubah.

| Baris FAQ | Masalah | Tindakan |
|---|---|---|
| `Kapan batch berikutnya mulai?` | tanggal duplikat & sudah salah ("akhir Agustus" vs "15 Agustus") | **hapus** |
| `Berapa kuota per batch?` | duplikat kolom `Kuota` | hapus, atau buang angkanya |
| `Batch 5 ada libur di tengah program gak?` | hardcode "Batch 5", basi tiap ganti batch | ganti jadi "batch reguler" |
| `Kalau batch penuh, ada waiting list?` | mendorong `"langsung daftar aja"` — bentrok saat pendaftaran tutup | netralkan |
| `Intensive Class` (deskripsi di LINKS) | hardcode `"tanggal 11 July"` | perbarui atau buang tanggalnya |

**Jangan** mengganti jawaban FAQ jadi *"lihat sheet PROGRAM"*. Teks jawaban FAQ disisipkan apa adanya ke prompt, dan system message melarang VIRA membocorkan proses internal — ada risiko kalimat itu ikut terucap ke orang tua murid.

VIRA tetap bisa menjawab "kapan batch mulai" tanpa baris FAQ itu, karena `Program mulai <tanggal>` sudah ada di blok `STATUS & BATCH`.

---

## Hasil QA

Logika verdict di-port 1:1 dari file hasil patch, dijalankan atas data asli sheet PROGRAM.
**23 assertion lolos, 0 regresi sintaks** (13 node Code di-parse `esprima`).

Matriks Status × tanggal — 10 kombinasi, semua sesuai harapan:

| Status | Deadline | Tanggal Mulai | Hasil |
|---|---|---|---|
| `Active` | 8 Agu (lewat) | 15 Agu | SUDAH DITUTUP |
| `Active` | 20 Agu | 15 Agu | DIBUKA |
| `Active` | — | 15 Agu | DIBUKA |
| `Active` | — | 1 Agu (lewat) | SUDAH DITUTUP |
| `Coming Soon` | — | 1 Sep | BELUM DIBUKA |
| `Coming Soon` | — | 1 Agu (lewat) | SUDAH DITUTUP |
| `Closed` | 20 Agu | 15 Agu | SUDAH DITUTUP |
| `Always Active` | 8 Agu (lewat) | 1 Agu (lewat) | DIBUKA |
| kosong | 20 Agu | 15 Agu | TIDAK JELAS |
| di luar dropdown | 20 Agu | 15 Agu | TIDAK JELAS |

Guardrail transfer dari patch sebelumnya dicek masih utuh.

**Batasan:** tidak ada Node.js di mesin ini — kode belum dieksekusi sebagai JavaScript; validasi sebatas parser + port logika. Belum diuji di n8n sungguhan.

---

## Deploy

1. n8n → **Import from File** → `2026-08-12-VIRA-V4-r2-status-batch.json`
2. Cek binding kredensial (Anthropic Personal, Google Sheets, Kirimi)
3. Uji:
   - `"batch 5 udah buka pendaftarannya?"` → **sudah ditutup** (selama deadline belum digeser), tanpa link
   - `"kapan batch berikutnya dimulai?"` → tanggal dari DATA, **tanpa** kata "rencananya"/"stay tuned"
   - `"mock interview masih bisa?"` → dibuka
   - `"mau transfer nih"` → `Baik, nanti akan dibantu cek dengan Sam yaa.`
4. Pantau execution log: `STATUS BASI` dan `STATUS TIDAK DIKENALI` = kolom Status di sheet perlu diperbaiki

**Rollback:** import ulang `report/production/2026-08-08-VIRA-V4-retryable.json`.

---

## Masih terbuka

- **Pembacaan sheet kosong total** (terlihat di log run pertama) — masalah keandalan, dampaknya lebih luas dari bug batch. Belum diinvestigasi.
- **Janji "nanti saya kabari"** — workflow hanya punya trigger webhook, tidak ada cron/broadcast, jadi janji itu tidak bisa ditepati. Belum diputuskan.
