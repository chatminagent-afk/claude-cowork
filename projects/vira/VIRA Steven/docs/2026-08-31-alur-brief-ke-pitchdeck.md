# Alur: dari obrolan WhatsApp sampai pitch deck jadi

Satu jalur, tujuh langkah. Tiga otomatis, satu keputusanmu, tiga menyusul.

```
prospek chat  →  VIRA gali  →  brief masuk sheet  →  notif WA ke Steven
                                                            ↓
                              PDF siap review  ←  generate  ←  keputusan Steven
```

---

## 1 · Prospek chat ke VIRA — otomatis

Masuk lewat nomor VIRA Personal. VIRA membalas sebagai “Steven versi AI”, menjawab
pertanyaan, dan mulai memahami bisnisnya.

## 2 · VIRA menggali — otomatis, berjenjang

| Tingkat | Isi | Kapan ditanya |
|---|---|---|
| **1** | nama bisnis, industri, masalah utama | dikejar duluan |
| **2** | aksi utama, volume chat, channel, siapa balas chat, deadline | pelan-pelan, satu per balasan |
| **2B** | nilai closing, prospek/bulan · jumlah admin & biaya admin *(hanya kalau pakai admin)* | **hanya setelah setuju dibuatkan deck** |
| **3** | 20 field sisanya | tidak pernah ditanya, dicatat kalau disebut sendiri |

Aturan tetap: satu pertanyaan per balasan, tidak pernah mengirim daftar pertanyaan.

## 3 · Brief masuk sheet — otomatis

Tag `[DECK_REQUEST]` keluar setiap ada informasi baru yang berarti. Workflow menggabungkannya
dengan baris lama (`no_wa` sebagai kunci), jadi **satu prospek = satu baris yang makin kaya**.
Nilai lama tidak pernah terhapus oleh emisi berikutnya.

Brief setengah jadi **tetap tersimpan** — sejak patch 30 Agu, gerbang Tingkat 1 hanya menahan
notifikasi, bukan penyimpanan.

## 4 · Notifikasi masuk ke HP-mu — otomatis

Hanya dikirim kalau Tingkat 1 sudah lengkap. Isinya sekarang:

```
📋 [VIRA Personal] BRIEF DECK
Akademi Arsi — Edukasi software arsitek
WA: 628xxxxxxxxxx
Kelengkapan: 28/33
Slide khusus siap: 6/6  → DECK SIAP DIGENERATE

  ✓ Konteks bisnis
  ✓ Pain Points
  ✓ The Flow (mockup)
  ✓ #1 Time Freedom
  ✓ #2 Zero Leaking Profit
  ✓ #3 Scalability

  (daftar field terisi)

Belum tergali: Jabatan, Budget, …

Generate deck:
python buat_deck.py --wa 628xxxxxxxxxx
```

**Baris yang menentukan: “Slide khusus siap”.** 23 dari 29 slide berdiri tanpa data klien sama
sekali. Enam sisanya butuh field tertentu — kalau kosong, slide itu **dibuang**, tidak pernah
diisi tebakan. Jadi `6/6` berarti deck penuh; `4/6` berarti deck 27 slide yang tetap layak
kirim, tinggal kamu putuskan mau menunggu atau jalan duluan.

## 5 · Keputusanmu

| Kondisi | Tindakan |
|---|---|
| `6/6` | generate sekarang |
| `4–5/6` | generate juga boleh — atau telepon dulu untuk melengkapi, lalu VIRA memperkaya barisnya sendiri |
| `≤3/6` | jangan digenerate. Notifikasi sudah menyebut field mana yang kurang; itu daftar pertanyaan untuk telepon |

## 6 · Generate

```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/deck" && python buat_deck.py --wa 628xxxxxxxxxx
```

Sebelum itu **unduh ulang** `sheet/VIRA Database.xlsx`. Generator membaca berkas unduhan, bukan
sheet live — kalau berkasnya berumur ≥1 hari, dia memperingatkan sendiri di terminal.

Keluarannya `deck/keluaran/<nama-bisnis>.pdf`. Terminal menutup dengan:

```
PERIKSA  : 29 halaman, 1440x810 pt, semua teks wajib ada
```

Kalau baris itu tidak muncul atau tertulis GAGAL, **jangan dikirim** — ada yang terpotong.

## 7 · Review, perbaiki bila perlu, kirim

Buka PDF-nya. Yang paling perlu dibaca ulang: **Pain Points** dan **The Flow**, dua slide yang
isinya datang dari obrolan.

Kalau kalimat di mockup kurang pas, tulis naskahnya sendiri:

`deck/naskah/<nama-bisnis>.json`

```json
{ "gelembung": [
  { "arah": "masuk",  "teks": "Kapan buka kelas lagi ya kak?" },
  { "arah": "keluar", "teks": "Batch berikutnya awal Oktober kak. Mau aku daftarkan sekalian?" }
]}
```

Jalankan ulang perintah yang sama. Naskah tulisan tangan menang atas susunan otomatis, **dan
tetap tersimpan** — jadi render berikutnya menghasilkan PDF yang sama persis.

Setelah dikirim, isi kolom `deck_dikirim_ts`, lalu `hasil` dan `alasan_kalah` saat sudah ketahuan.
Tiga kolom itu sengaja tidak dipetakan di workflow, jadi tidak akan pernah tertimpa.

---

## Kenapa hasilnya tidak akan berubah-ubah

Empat pengunci, semuanya diuji oleh `deck/uji_konsistensi.py` (14 pemeriksaan, semua lolos):

| Pengunci | Cara kerja |
|---|---|
| **Struktur terkunci** | `struktur.lock.json` mencatat urutan 29 slide. Generator **menolak jalan** kalau template menyimpang — sudah diuji dengan sengaja merusak template |
| **Tidak ada keacakan** | tidak ada timestamp, tidak ada random, tidak ada panggilan LLM saat render. Brief sama → HTML **byte-per-byte identik** |
| **Naskah tersimpan** | perbaikan kalimat masuk ke berkas, bukan ke prompt sekali pakai |
| **Verifikasi tiap render** | jumlah halaman, ukuran halaman, dan enam potongan teks wajib dicek di PDF akhir |

Yang terakhir bukan teori: baris `Global Language Capability` pernah **terpotong diam-diam**
karena tabel melebihi tinggi slide, tanpa error apa pun. Sekarang ketahuan sebelum terkirim.

---

## Yang harus kamu ubah

### Di Google Sheet — bisa sekarang, tidak menunggu nomor

Tambah **11 kolom** di tab REQUESTS mulai sel **AG1**, urut:
`kota`, `jumlah_admin`, `sudah_pakai_chatbot`, `integrasi_dibutuhkan`, `data_tersedia`,
`kutipan_asli`, `sumber_prospek`, `brief_jumlah`, `deck_dikirim_ts`, `hasil`, `alasan_kalah`

Lalu buat tab `_KAMUS_BRIEF` dan import `sheet/2026-08-30-import/_KAMUS_BRIEF.csv`.

⚠️ **Wajib sebelum workflow baru diaktifkan** — `Write REQUESTS` memetakan 8 dari kolom itu; node
Google Sheets akan error kalau headernya belum ada.

### Di n8n — bisa sekarang

Import `workflow/2026-08-30-VIRA-Personal-Main.json`, set Error Workflow, set kredensial Sheets.
**Jangan aktifkan** sampai 11 kolom di atas sudah ada.

Langkah lengkap + checklist: `docs/2026-08-30-panduan-deploy-brief-deck.md`.

### Menunggu nomor byU

Isi 5 nilai `ISI MANUAL` di CONFIG, aktifkan workflow, lalu jalankan UAT V1–V4.

---

## Belum otomatis penuh — sengaja

Generate deck **tidak** dipicu sendiri oleh `[DECK_REQUEST]`. Alasannya: deck adalah aset
jualanmu, dan deck lemah yang terkirim cepat lebih merugikan daripada deck bagus yang telat
sehari. Bot memberi tahu, kamu yang memutuskan.

Kalau nanti mau otomatis penuh, yang perlu ditambah cuma dua hal — node n8n yang menjalankan
`buat_deck.py` di mesin yang menyala terus, dan aturan “hanya jalan kalau slide khusus 6/6”.
Struktur sekarang sudah siap untuk itu.
