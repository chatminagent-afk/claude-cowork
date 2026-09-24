# Audit Google Sheet VIRA — Daftar Perbaikan untuk Sam

**Tanggal:** 2026-08-12
**Sumber:** `report/production/The_Scholars_Database.xlsx` (snapshot **22 Juli 2026**)
**Cakupan:** tab `FAQ` (113 baris), `PROGRAM`, `LINKS`, `CONFIG`

> ⚠️ **Nomor baris mengacu ke snapshot 22 Juli.** Sheet live kemungkinan sudah berubah. Cocokkan lewat **teks pertanyaannya**, jangan lewat nomor baris saja.

---

## Kenapa ini perlu

VIRA punya dua sumber fakta: **DATA TERVERIFIKASI** (dari tab PROGRAM/LINKS) dan **FAQ RELEVAN** (dari tab FAQ). Patch r2 sudah menetapkan DATA menang kalau bertentangan — tapi itu instruksi ke AI, bukan jaminan. Selama FAQ masih menyimpan fakta yang duplikat atau basi, kontradiksinya tetap ada dan sewaktu-waktu bocor.

Sudah terbukti di produksi: baris FAQ R33 membuat VIRA menjawab *"Batch 5 **rencananya** mulai 15 Agustus"* — tanggalnya benar dari PROGRAM, tapi kata ragunya dicomot dari FAQ.

**Aturan main ke depan: FAQ tidak boleh memuat tanggal, harga, kuota, status pendaftaran, atau nomor batch.** Semua itu tempatnya di tab PROGRAM. FAQ untuk penjelasan & kebijakan yang jarang berubah.

---

## PRIORITAS 1 — Bertentangan langsung dengan permintaan Sam soal transfer

### R69 — **HAPUS**

| | |
|---|---|
| Pertanyaan | `Pembayarannya bisa pakai kartu kredit atau harus transfer?` |
| Jawaban | `Untuk sekarang pembayarannya lewat transfer bank yaa, belum bisa pakai kartu kredit. Nanti nomor rekeningnya saya kirim pas konfirmasi slot 🙂` |

Ini **persis** yang Sam minta VIRA jangan pernah ucapkan — menyebut transfer **dan** menjanjikan pengiriman nomor rekening. Safety net di `Process All` akan memotongnya sebelum sampai ke customer, tapi akibatnya jawaban VIRA jadi terpotong aneh. Hapus di sumbernya.

Penggantinya sudah ada di **R99**, yang jawabannya justru sudah tepat:
> `Metode pembayarannya nanti saya infoin langsung lewat WA begitu proses seleksinya selesai yaa.`

---

## PRIORITAS 2 — Fakta yang bertabrakan dengan tab PROGRAM

### Hapus

| Baris | Pertanyaan | Masalah |
|---|---|---|
| **R33** | `Kapan batch berikutnya mulai?` | Jawabannya `"Batch 5 rencananya mulai akhir Agustus 2026"` — **salah**, PROGRAM bilang 15 Agustus. Ini biang kontaminasi yang terbukti di log. |
| **R16** | `Berapa biaya batch 5 nya?` | Harga duplikat kolom `Harga` + hardcode nomor batch |
| **R18** | `Bisa bayar cicilan untuk batch 5?` | Skema bayar duplikat kolom `Pembayaran` + hardcode nomor batch |
| **R34** | `Berapa kuota per batch?` | `"Total sekitar 60 anak, dibagi jadi 4 kelas"` — angka 60 dan jumlah kelas **tidak ada** di PROGRAM (yang ada cuma `Kuota = 15 per kelas`). Berubah tiap batch. |
| **R47** | `Batch 4 isinya apa?` | Batch lama, tanggal `18 April`, link IG lama |
| **R48** | `Batch 4 masih buka pendaftaran?` | Batch lama |
| **R114** | `Kak, utk open asean schoolarshipnya sendiri di bulan apa ya kak?` | **Kolom Jawaban KOSONG.** Baris tanpa jawaban tetap ikut retrieval dan bisa membuat VIRA bingung. Isi jawabannya atau hapus barisnya. |

### Buang satu kalimat saja (sisanya bagus)

**R8, R9, R10, R11** — empat baris rekomendasi program per kelas (SD 6 / SMP 1 / SMP 2 / SMP 3). Semuanya diakhiri kalimat yang sama:

> ~~`Batch 5 rencananya mulai akhir Agustus.`~~

Buang kalimat terakhir itu saja. Isi rekomendasi programnya sudah benar dan tidak perlu diubah. Tanggal batch akan diambil VIRA dari PROGRAM.

### Duplikat tapi masih konsisten — pantau, jangan lupa update dua tempat

| Baris | Isi duplikat | Sumber aslinya |
|---|---|---|
| R17 | `Seniors Rp 4.000.000` | kolom `Harga` |
| R20, R110 | durasi `4 bulan / 16 sesi`, `~2 jam` | kolom `Durasi` |
| R27 | skema bayar 2x | kolom `Pembayaran` |
| R91 | `Rp 750.000 per sesi` | kolom `Harga` (Mock Interview) |
| R100 | `promo Rp 9.000.000, normal Rp 12.000.000` | kolom `Catatan` |

Paling aman: buang angkanya dari FAQ, biarkan VIRA mengambil dari PROGRAM.

---

## PRIORITAS 3 — Hardcode nomor batch (akan basi tiap ganti batch)

Sudah dibersihkan dari system message. Yang tersisa ada di sheet:

| Baris | Ganti jadi |
|---|---|
| R96 | `Batch 5 ada libur di tengah program gak?` → `Ada libur di tengah program gak?` (jawaban: buang kata "Batch 5") |
| R97 | `Berapa banyak siswa per kelas di Batch 5?` → `Berapa banyak siswa per kelas?` |
| R98 | `Ada PR atau tugas gak di Batch 5?` → `Ada PR atau tugas gak?` |
| R99 | `Metode pembayaran Batch 5 gimana Sam?` → `Metode pembayarannya gimana Sam?` |

(R8–R11, R16, R18, R33, R47, R48 sudah tercakup di Prioritas 2.)

---

## PRIORITAS 4 — URL mentah di FAQ (membobol guardrail link)

Ini **bukan** sekadar duplikasi. VIRA punya aturan: link pendaftaran hanya boleh dikirim lewat tag `[SEND_GFORM]`, dan tag itu **dilarang** saat pendaftaran `BELUM DIBUKA` / `SUDAH DITUTUP`. Kalau URL-nya sudah tertulis di dalam teks jawaban FAQ, model bisa menempelkannya langsung — **melewati gerbang itu sepenuhnya**, termasuk saat pendaftaran sedang tutup.

| Baris | URL di dalam jawaban | Sudah ada di LINKS sebagai |
|---|---|---|
| R14 | `forms.gle/mKZpg7t68qHNFnML6` | `GForm Pendaftaran Seniors` |
| R15 | `drive.google.com/file/d/1fFPyo...` | `Guidebook` |
| R46 | `drive.google.com/file/d/1fFPyo...` | `Guidebook` |
| R102 | `whatsapp.com/channel/0029Vb7...` | `WhatsApp Channel` |
| R106 | `tinyurl.com/UOBCLIntensiveClass` | `Intensive Class` |
| R47 | `instagram.com/p/DWLCeFhga8x` | — (post lama) |

**Tindakan:** buang URL-nya dari teks jawaban FAQ. Biarkan kalimat penjelasnya. VIRA akan menyisipkan link yang benar dari tab LINKS lewat mekanisme `[SEND_GFORM]`.

---

## PRIORITAS 5 — Janji yang tidak bisa ditepati

Workflow VIRA **hanya punya satu pemicu: webhook** (pesan masuk). Tidak ada cron, tidak ada broadcast. **VIRA secara teknis tidak bisa mengirim pesan lebih dulu.** Setiap janji "nanti saya kabari" lewat chat tidak akan pernah terjadi.

| Baris | Kalimat bermasalah | Saran |
|---|---|---|
| R57 | `Saya juga akan kabari kalau ada info resminya.` | ganti → `Info resminya bisa dipantau di website MOE yaa.` |
| R73 | `Nanti kalau ada yang bagus pasti saya kabari yaa 🙏` | ganti → arahkan ke IG / WhatsApp Channel |
| R51 | `Kalau ada info beasiswa baru pasti saya update juga nantinya.` | ganti → arahkan ke IG / WhatsApp Channel |
| R35 | `Untuk sekarang belum ada waiting list. Jadi kalau kamu minat, langsung daftar aja sebelum penuh!` | dorongan daftar ini bentrok saat pendaftaran `SUDAH DITUTUP` → netralkan |

**Aman, tidak perlu diubah:** R78 dan R103 menjanjikan kabar lewat **IG**, bukan lewat chat — itu kanal yang memang Sam pegang sendiri.

---

## PRIORITAS 6 — Kadaluwarsa & inkonsisten

| Baris | Masalah |
|---|---|
| R103 | `CLI yang akan diadakan tanggal 11 Juli ini` — sudah lewat |
| R84 | `UOB dan CLI bisa apply sekarang yaa, kalau ASEAN apply-nya tahun depan sekitar Januari` — pakai waktu relatif ("sekarang", "tahun depan"), pasti basi. Ganti ke bulan absolut. |
| **R6 vs R105** | **Saling bertentangan.** R6: `sekitar 13 alumni yang berhasil dapet Sec 1 dan Sec 3`. R105: `sukses antarkan 30+ murid dapat ASEAN Scholarship`. Angka mana yang benar? Ini menyangkut kredibilitas — kalau customer menanyakan dua kali dengan cara berbeda, VIRA bisa menyebut dua angka berbeda. |
| R22 | `Di 9 bulan ke belakang ini, saya sudah mentoring 100+ murid` — waktu relatif, akan basi |

---

## Tab PROGRAM

| Kolom | Masalah | Tindakan |
|---|---|---|
| `Deadline Daftar` (Junior & Intermediate) | `8 Agustus 2026` — **sudah lewat**, padahal `Status` masih `Active`. Dengan patch r2, tanggal jadi acuan penyeimbang → **Batch 5 dibaca `SUDAH DITUTUP`**. | Kalau pendaftaran masih dibuka: **geser tanggalnya**. Kalau memang sudah tutup: biarkan, dan ubah `Status` jadi `Closed` supaya niatnya eksplisit. |
| `Status` | Dropdown 4 nilai sudah benar dan seluruhnya dikenali kode: `Active` · `Coming Soon` · `Closed` · `Always Active` | tidak ada yang perlu diubah |
| `Pembayaran` | `"...metode pembayaran dikonfirmasi setelah seleksi"` — **bagus**, tidak menyebut transfer sama sekali | pertahankan |

---

## Tab LINKS

| Baris | Masalah | Tindakan |
|---|---|---|
| R7 `Intensive Class` | Deskripsi `"...yang diadakan tanggal 11 July"` — sudah lewat, tapi `Status` masih `Active`. Deskripsi ini ikut dikirim ke VIRA. | perbarui tanggalnya, atau ubah `Status` jadi non-aktif |
| R2 `GForm Pendaftaran Batch 5` | Nama link memuat nomor batch | Tidak masalah secara teknis — VIRA membacanya dinamis dari sheet. Tapi tiap ganti batch, **nama link ini harus ikut di-rename**, kalau tidak VIRA akan menyebut "Batch 5" terus. |
| semua | `Last Updated` masih Mei–Juni 2026 | tinjau ulang semua URL masih hidup |

---

## Tab CONFIG — aman sekarang, tapi jangan disentuh

Tab ini berisi `NAMA_BANK`, `NOMOR_REKENING`, dan `ATAS_NAMA`.

**Sudah diverifikasi: tidak ada satu pun node di workflow yang membaca tab CONFIG.** Node Google Sheets hanya menyentuh `STATS`, `PROGRAM`, `FAQ`, `LINKS`, `ABOUT_SAM`, `MSG_BUFFER`, `UNKNOWN`. Jadi nomor rekening **tidak mungkin** sampai ke VIRA hari ini.

Dua catatan:
1. **Jangan pernah menambahkan node yang membaca CONFIG** tanpa menyaring kolom rekening lebih dulu. Itu akan mengalirkan nomor rekening langsung ke prompt AI — persis yang Sam ingin cegah.
2. `NOMINAL_BIAYA = 1.000.000` tidak cocok dengan harga mana pun yang aktif (Rp 9jt / 4jt / 750rb). Kemungkinan sisa uji coba lama. Karena tidak dibaca, tidak berbahaya — tapi lebih baik dibersihkan supaya tidak menyesatkan orang yang membaca sheet.

---

## Ringkasan tindakan

| Tindakan | Baris |
|---|---|
| **Hapus** | R16, R18, R33, R34, R47, R48, R69, R114 |
| **Buang 1 kalimat** | R8, R9, R10, R11 |
| **Buang nomor batch dari pertanyaan** | R96, R97, R98, R99 |
| **Buang URL dari jawaban** | R14, R15, R46, R47, R102, R106 |
| **Ubah janji "saya kabari"** | R35, R51, R57, R73 |
| **Perbarui / samakan angka** | R6 vs R105, R22, R84, R103 |
| **Pantau duplikat** | R17, R20, R27, R91, R100, R110 |
| **PROGRAM** | geser `Deadline Daftar` atau ubah `Status` jadi `Closed` |
| **LINKS** | perbarui deskripsi `Intensive Class` |
| **CONFIG** | jangan dibaca workflow; bersihkan `NOMINAL_BIAYA` |

**Paling mendesak:** R69 (transfer + nomor rekening) dan `Deadline Daftar` di PROGRAM — keduanya berdampak langsung ke apa yang dibaca customer hari ini.
