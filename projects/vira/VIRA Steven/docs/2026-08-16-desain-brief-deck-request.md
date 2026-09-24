# Desain Brief `[DECK_REQUEST]` — VIRA Steven

**Tujuan:** hasil tangkapan bot harus cukup lengkap untuk menyusun pitch deck khusus klien,
setara dengan yang sudah pernah dibuat untuk The Scholars (31 slide) dan Persada Cisoka (adaptasi).

**Sumber desain:**
- `scholars-vira-deck-text.txt` — isi 31 slide deck The Scholars
- `2026-07-16-outline-pitchdeck-VIRA-persada.md` — dokumen adaptasi deck yang sama untuk klien kedua

Dokumen kedua yang paling menentukan: dia mencatat **apa saja yang harus berubah** saat deck
dipakai ulang untuk klien lain. Itulah daftar yang wajib bot tangkap.

---

## Yang berubah tiap klien (dari outline Persada)

| Yang berubah | Contoh perbedaan Scholars → Persada | Field brief yang menutupinya |
|---|---|---|
| Pain points | "chat ortu murid di luar jam kerja" → "leads properti mahal, telat respon = pindah ke developer sebelah" | `masalah_utama`, `pain_points`, `sumber_leads` |
| Aksi konversi utama | booking les → jadwal survey unit | `aksi_utama` |
| Fitur yang tidak relevan | Automated Invoicing dibuang total untuk properti | `alur_setelah_chat`, `fitur_diminati` |
| Fitur ekstra yang justru jadi pembeda | call redirection, deteksi sumber leads, delegasi ke tim lapangan | `alur_setelah_chat`, `fitur_diminati` |
| Angka ROI | 50 prospek × Rp1jt → nilai transaksi properti jauh lebih besar | `nilai_transaksi`, `prospek_per_bulan`, `biaya_admin_bulanan` |
| Mockup percakapan | "booking les Mr. Andi" → "tanya harga unit, KPR, minta survey" | `pertanyaan_tersering`, `alur_setelah_chat` |
| Bahasa deck | Indonesia campur Inggris | `bahasa_deck` |

---

## 27 field brief

Dikelompokkan sesuai bagian deck yang dia isi.

### A. Identitas & konteks — slide 1 (cover), 31 (penutup)

| Field | Isi | Dipakai di slide |
|---|---|---|
| `nama` | Nama orang yang chat | Cover, sapaan |
| `jabatan` | Owner / manager / admin / marketing | Menentukan sudut pandang deck & siapa pengambil keputusan |
| `nama_bisnis` | Nama usaha | Cover, judul deck |
| `industri` | Kategori usaha | Menentukan seluruh konteks pain point |
| `deskripsi_bisnis` | Jualan/layanannya apa persis | Slide pembuka konteks |
| `target_pelanggan` | Siapa yang chat ke mereka | Pain point, mockup percakapan |

### B. Situasi sekarang — slide 4–5 (pain points), 27 (scalability)

| Field | Isi | Dipakai di slide |
|---|---|---|
| `channel` | WA / IG DM / marketplace / telepon | Pain point "multi-platform chaos" |
| `sumber_leads` | Iklan berbayar / organik / referral | Menentukan seberapa mahal satu leads hilang |
| `volume_chat_harian` | Perkiraan chat masuk per hari | Pain point + slide scalability |
| `jam_operasional` | Jam kerja mereka sekarang | Pain point "di luar jam kerja" |
| `siapa_balas_chat` | Owner sendiri / N admin | Pain point "owner overload" |
| `biaya_admin_bulanan` | Biaya CS/admin saat ini | Slide biaya & perbandingan |
| `sistem_sekarang` | Excel / CRM / catat manual / belum ada | Slide "human error" + integrasi |

### C. Masalah — slide 4–5

| Field | Isi |
|---|---|
| `masalah_utama` | Satu masalah terbesar menurut dia sendiri |
| `pain_points` | Keluhan lain, dipisah titik koma |

### D. Alur & fitur — slide 8–15 (fitur + flow), 20 (perbandingan paket)

| Field | Isi | Dipakai di slide |
|---|---|---|
| `aksi_utama` | Konversi yang dikejar: booking / survey / order / reservasi / konsultasi | Menggantikan slide "Automated Booking" |
| `alur_setelah_chat` | Chat masuk → apa saja sampai closing | Slide "The Flow" + menentukan fitur mana yang dibuang |
| `pertanyaan_tersering` | Pertanyaan yang paling sering masuk | Bahan FAQ + mockup percakapan |
| `fitur_diminati` | Follow-up / invoice / kirim media / multi-bahasa / laporan | Slide perbandingan Basic vs Premium |

### E. Angka ROI — slide 25–26

| Field | Isi |
|---|---|
| `nilai_transaksi` | Rata-rata nilai satu closing |
| `prospek_per_bulan` | Perkiraan jumlah prospek masuk per bulan |

Dua angka ini yang bikin slide ROI bisa dihitung spesifik, bukan template.

### F. Komersial & waktu — slide 21–22 (investment), 29 (implementation)

| Field | Isi |
|---|---|
| `minat_paket` | Basic / Premium / belum tahu |
| `budget_range` | Kisaran anggaran yang dia sebut |
| `deadline` | Kapan dia ingin jalan |
| `urgensi` | Kenapa sekarang, bukan nanti |

### G. Meta

| Field | Isi |
|---|---|
| `bahasa_deck` | ID / EN / campur — mengikuti bahasa yang dia pakai |
| `catatan` | Apa pun yang penting tapi tidak masuk field lain |

---

## Tingkat penggalian — supaya bot tidak menginterogasi

27 field tidak mungkin ditanyakan satu per satu di WhatsApp. Field dibagi tiga tingkat.
Aturan "satu pertanyaan per balasan" tetap berlaku dan tidak dilonggarkan.

| Tingkat | Field | Perlakuan |
|---|---|---|
| **1 — syarat minimum** | `nama_bisnis`, `industri`, `masalah_utama` | Tag `[DECK_REQUEST]` baru boleh keluar setelah tiga ini terisi |
| **2 — digali aktif** | `aksi_utama`, `volume_chat_harian`, `channel`, `siapa_balas_chat`, `deadline` | Ditanya satu per balasan, hanya kalau percakapan mengarah ke sana |
| **3 — oportunistik** | 19 field sisanya | Diisi **hanya** kalau dia menyebut sendiri. Tidak pernah ditanyakan langsung |

Field yang belum diketahui diisi `belum disebut`. Itu bukan kegagalan — kolom kosong justru
jadi daftar pertanyaan untuk Steven saat menelepon.

---

## Mekanisme merge — tag boleh keluar berkali-kali

Tag dikeluarkan ulang setiap kali ada informasi baru yang berarti, dan **selalu berisi 27 baris
lengkap**. Supaya emisi kedua tidak menghapus isi emisi pertama, penggabungan dilakukan di workflow,
bukan diserahkan ke AI:

1. `IF Deck Request` → `Read REQUESTS` — ambil baris lama prospek ini (kalau ada)
2. `Merge Brief` — per field: nilai baru menang **hanya** kalau bukan kosong dan bukan `belum disebut`;
   selain itu nilai lama dipertahankan
3. `Write REQUESTS` — `appendOrUpdate` dengan pencocokan `no_wa`, jadi satu prospek = satu baris yang makin kaya
4. `Update STATS Brief` — tulis `brief_terisi` (daftar key yang sudah terisi) ke STATS
5. `Notify Admin Deck` — rangkuman ke HP Steven

Langkah 4 yang membuat bot sadar diri: giliran berikutnya `Resolve User Row` membaca `brief_terisi`,
`Rakit Konteks` menyisipkannya ke `prospect_context`, dan bot tahu apa yang sudah dijawab —
jadi tidak menanyakan ulang hal yang sama.

---

## Perubahan skema sheet

### Tab `REQUESTS` — dari 12 kolom jadi 32

Kolom lama yang dipertahankan: `ts`, `no_wa`, `nama`, `nama_bisnis`, `industri`, `masalah_utama`,
`volume_chat_harian`, `channel`, `budget_range`, `deadline`, `catatan`, `status_followup`.

Urutan final:

```
ts | update_terakhir | no_wa | nama | jabatan | nama_bisnis | industri | deskripsi_bisnis |
target_pelanggan | channel | sumber_leads | volume_chat_harian | jam_operasional |
siapa_balas_chat | biaya_admin_bulanan | sistem_sekarang | masalah_utama | pain_points |
aksi_utama | alur_setelah_chat | pertanyaan_tersering | fitur_diminati | nilai_transaksi |
prospek_per_bulan | minat_paket | budget_range | deadline | urgensi | bahasa_deck | catatan |
kelengkapan | status_followup
```

- `ts` — kapan brief pertama masuk (tidak berubah setelah itu)
- `update_terakhir` — kapan terakhir diperkaya
- `kelengkapan` — `n/27`, biar terlihat brief mana yang sudah matang

### Tab `STATS` — tambah 1 kolom

`brief_terisi` — daftar key yang sudah terisi, dipisah koma. **Ditambahkan di ujung kanan**
(kolom AD, setelah `last_follow_up_ts`), bukan disisipkan di tengah — supaya di sheet live
cukup mengisi satu sel dan tidak ada kolom yang bergeser.

Urutan kolom tidak berpengaruh: node Google Sheets di n8n memetakan berdasarkan nama header.

Tidak ada kolom lama yang dihapus atau diganti nama.

### File arsip

Skema baru ada di `sheet/2026-08-16-VIRA-Steven-Database.xlsx`.
File lama `sheet/VIRA-Steven-Database.xlsx` tidak dihapus — masih ada sebagai cadangan.

---

## Format tag di system prompt

```
[DECK_REQUEST]
nama: ...
jabatan: ...
nama_bisnis: ...
industri: ...
deskripsi_bisnis: ...
target_pelanggan: ...
channel: ...
sumber_leads: ...
volume_chat_harian: ...
jam_operasional: ...
siapa_balas_chat: ...
biaya_admin_bulanan: ...
sistem_sekarang: ...
masalah_utama: ...
pain_points: ...
aksi_utama: ...
alur_setelah_chat: ...
pertanyaan_tersering: ...
fitur_diminati: ...
nilai_transaksi: ...
prospek_per_bulan: ...
minat_paket: ...
budget_range: ...
deadline: ...
urgensi: ...
bahasa_deck: ...
catatan: ...
[/DECK_REQUEST]
```

Parser di `Process All` menerima urutan baris apa pun, mengabaikan baris yang tidak dikenal,
dan memperlakukan `belum disebut` / `-` / kosong sebagai "tidak ada isi".
Nilai dipotong maksimal 500 karakter per field supaya satu baris sheet tidak meledak.
