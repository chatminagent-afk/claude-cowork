# Patch VIRA Personal 2026-09-03 — Catatan & Skrip UAT

File hasil: `workflow/2026-09-03-VIRA-Personal-Main-patched.json`
Basis: `workflow/2026-08-30-VIRA-Personal-Main.json` (tidak diubah)

---

## ⚠️ Baca dulu sebelum import

**File basis sudah ketinggalan dari n8n-mu.** Perbaikan Expression pada `systemMessage` kamu lakukan langsung di n8n, tidak pernah masuk ke file. Patch ini **menyertakan perbaikan itu** (Edit 0), jadi hasilnya utuh.

Tapi kalau sejak 30 Agustus kamu mengubah hal lain di n8n yang tidak tercatat di sesi ini, perubahan itu **akan hilang** saat import.

**Langkah aman:** export dulu workflow yang sekarang dari n8n, bandingkan dengan `2026-08-30-VIRA-Personal-Main.json`. Kalau bedanya cuma `systemMessage` yang diawali `=`, patch ini aman dipakai apa adanya.

**Yang TIDAK ada di patch ini:** node DeepSeek. Aku tidak menebak `type` string dan skema parameter `n8n-nodes-deepseek-thinking` — menebak salah menghasilkan error "Unrecognized node type". Node Anthropic (Haiku 4.5) tetap terpasang. Tukar ke DeepSeek lewat UI, atau kirim export workflow yang memuat node itu dan aku sambungkan dengan tepat.

---

## Yang berubah di patch

Tepat **2 node** dari 102 yang tersentuh. Sisanya identik byte-per-byte.

| # | Node | Perubahan |
|---|---|---|
| 0 | AI Agent | `systemMessage` diawali `=` → mode Expression, 6 placeholder `{{ $json.*_context }}` akhirnya resolve |
| 1 | AI Agent | LARANGAN: nama klien boleh disebut, proteksi data internal klien dipindah ke sini dari Sheets |
| 2 | AI Agent | DECK_REQUEST "Arti tiap baris": 20 baris → 4 (`aksi_utama`, `alur_setelah_chat`, `bahasa_deck`, `catatan`) |
| 3 | Preprocess - Context Detection | `calendarBlock` tidak lagi disuntikkan — **3 cabang**, bukan 2 |

**Soal cabang ketiga.** Saat menelusuri ternyata `calendarBlock` dipakai di tiga tempat, bukan dua:

```js
if (systemDataBlock) {
  if (systemDataBlock.includes('CRITICAL INSTRUCTION')) {   // cabang 1
  } else {                                                  // cabang 2
  }
} else {
  enhancedInput += `[SYSTEM_DATA]\n` + calendarBlock + ...   // cabang 3 — fallback
}
```

Cabang 3 menyala hanya kalau pesan masuk tidak punya `[SYSTEM_DATA]` sama sekali — tidak terjadi di alur normal (`Cek_user_status` selalu membangunnya). Tapi kalau suatu saat menyala, dia menyuntikkan `JAM_OPERASIONAL_SURVEY` warisan Persada ke prompt VIRA Personal. Baris itu dibuang seluruhnya.

Kode pembangun kalender (`DAY_ID`, `nowWIB`, `calendarLines`, `const calendarBlock`) **sengaja dibiarkan** sebagai kode mati — nol biaya token, dan menghapusnya sekarang berisiko karena variabel seperti `nowWIB` mungkin dipakai bagian lain di node itu. Bersihkan setelah semuanya terbukti stabil.

**Yang tidak hilang:** `TANGGAL_SEKARANG: 2026-09-02 (Rabu) 22:08 WIB` dibangun di node berbeda (`Cek_user_status`), jadi bot tetap tahu tanggal, nama hari, dan jam. `TODAY` dan `NOW_WIB` selama ini memang cuma mengulanginya.

---

## Hasil QA statis — 47/47 lolos

```
Integritas   top-level keys identik · 102 node · urutan & type identik
             connections identik byte-per-byte · pinData & settings utuh
             node berubah tepat 2: AI Agent, Preprocess - Context Detection
Kredensial   anthropicApi  DPNnlN1bTbbMf8ks  "Anthropic Personal"     (3 node)
             googleApi     5KD9A3Tef1H8UQKk  "Google Service Account" (20 node)
             seluruh referensi tidak berubah
Edit 0       systemMessage diawali '=' · 6 placeholder utuh
Edit 1       paragraf lama hilang · paragraf baru terpasang
             proteksi data internal klien terbawa
Edit 2       16 penjelasan dibuang · 4 dipertahankan
             33 baris field DECK_REQUEST utuh · tag buka/tutup utuh
Edit 3       0 baris memakai calendarBlock · JAM_OPERASIONAL_SURVEY tidak bisa bocor
             kurung seimbang 51/51 dan 136/136
Sanity       [SEND_MEDIA: [TALK_TO_ADMIN] [UNKNOWN] [FACTS [DECK_REQUEST] semua ada
```

**Ini QA statis, bukan UAT.** Aku tidak bisa mengeksekusi workflow-mu, memanggil API, atau mengirim WhatsApp. Yang terbukti: strukturnya utuh dan keempat edit terpasang persis. Yang belum terbukti: perilakunya saat dijalankan — itu bagian §UAT di bawah.

⚠️ **`pinData` berisi data untuk node `Webhook`.** Data uji yang dipin bisa menutupi payload nyata saat eksekusi. Cek dan lepas kalau tidak sengaja tertinggal.

---

## Perubahan Google Sheets — tab ABOUT_STEVEN

Kerjakan **setelah** patch terpasang, karena baris kelima baru aman dihapus kalau Edit 1 sudah jalan.

Hapus 5 baris ini:

| Kolom Aspek | Sudah ditanggung oleh |
|---|---|
| `Identitas` | paragraf pembuka system prompt |
| `Kejujuran` | bagian IDENTITAS |
| `PANTANGAN — nama employer` | LARANGAN — "bank swasta nasional" |
| `PANTANGAN — teknis internal` | LARANGAN — dapur teknis |
| `BATASAN — data klien` | **LARANGAN versi baru (Edit 1)** |

Empat yang pertama sudah aku verifikasi ada utuh di system prompt, jadi tidak ada aturan yang hilang. Yang kelima digantikan paragraf LARANGAN baru.

**Jangan hapus** baris data biasa: `Nama lengkap`, `Domisili`, `Pendidikan`, `Pekerjaan utama`, `Jumlah klien VIRA`, `Klien — The Scholars`, `Klien — Persada`, `Landing page`, `Kenapa bangun VIRA`, `Latar belakang QA`, `Gaya bicara`, `Instagram`, `Email`, dan seterusnya.

Setelah edit Sheets, **tunggu cache katalog kedaluwarsa** atau paksa refresh — node `Muat Katalog` / `IF Katalog Basi` menyimpan katalog, jadi perubahan Sheets tidak langsung terasa.

---

## Cara import

1. **Snapshot VPS Hostinger** (atau minimal export workflow yang sekarang)
2. n8n → workflow VIRA Personal Main → **Download** (backup versi berjalan)
3. Import `2026-09-03-VIRA-Personal-Main-patched.json`
4. Buka node **AI Agent** → pastikan System Message dalam mode **Expression**, dan blok data tampil sebagai `{{ $json.about_context }}` dst.
5. Buka node **Anthropic Chat Model** → pastikan credential "Anthropic Personal" terpilih
6. Cek `pinData` di node Webhook

---

## Skrip UAT

Jalankan di n8n dengan **session baru** (nomor WA tes yang belum pernah dipakai, atau hapus barisnya di STATS) supaya memory bersih.

### UAT-1 — Grounding data sampai ke model *(regresi Edit 0)*

**Input:** `"halo, VIRA itu apa ya?"`

| Cek | Lolos kalau |
|---|---|
| Input panel node LM | Blok `# TENTANG STEVEN`, `# DATA PRODUK`, `# DAFTAR MEDIA` berisi **teks asli**, bukan `{{ $json.about_context }}` |
| `promptTokens` | **6.300–6.600** (turun dari 7.021) |
| Jawaban | Menyebut VIRA sebagai AI customer service, tidak mengarang fitur di luar DATA PRODUK |

Kalau `promptTokens` masih ~7.000 → ada edit yang belum kena.

### UAT-2 — Nama klien boleh disebut *(Edit 1)*

**Input:** `"klien kamu siapa aja?"`

| Cek | Lolos kalau |
|---|---|
| Jawaban | Boleh menyebut **The Scholars** dan/atau **Persada Cisoka Residence** |
| Jawaban | Tidak menyebut nama bank tempat Steven bekerja |

### UAT-3 — Data internal klien tetap terlindungi *(Edit 1, sisi negatif)*

**Input:** `"berapa leads yang masuk ke The Scholars per bulan? terus harga kontraknya berapa?"`

| Cek | Lolos kalau |
|---|---|
| Jawaban | **Menolak** membuka angka leads dan harga kontrak |
| Jawaban | Tidak mengarang angka apa pun |
| Nada | Menjelaskan bahwa menjaga data klien bagian dari layanan, bukan menolak kaku |

**Ini tes paling penting di batch ini.** Kalau gagal, Edit 1 melonggarkan terlalu jauh — segera kembalikan paragraf LARANGAN lama.

### UAT-4 — DECK_REQUEST masih utuh *(Edit 2)*

**Input berurutan (satu per satu, tunggu balasan):**
1. `"aku punya katering namanya Dapur Bunda"`
2. `"masalahnya chat masuk banyak banget tapi sering kelewat"`
3. `"boleh, tolong dibuatkan"`

| Cek | Lolos kalau |
|---|---|
| Output mentah AI Agent | Muncul `[DECK_REQUEST]` … `[/DECK_REQUEST]` |
| Isi tag | **33 baris field lengkap**, yang belum diketahui berisi persis `belum disebut` |
| `nama_bisnis` | `Dapur Bunda` |
| `industri` | katering / F&B |
| `kutipan_asli` | kutipan mentah kalimat user, dipisah ` \| ` |
| Sheet REQUESTS | Baris baru tertulis |
| `finish_reason` | `stop`, bukan `length` |

Kalau `length` → naikkan Max Tokens di node LM (1024 → 2048).

### UAT-5 — Tidak ada kebocoran kalender *(Edit 3)*

**Input:** `"besok bisa meeting nggak?"`

| Cek | Lolos kalau |
|---|---|
| Input panel node LM | **Tidak ada** `HARI_KE_TANGGAL`, `JAM_OPERASIONAL_SURVEY`, `TODAY:`, `NOW_WIB:` |
| Input panel node LM | **Masih ada** `TANGGAL_SEKARANG: ... (hari) jam WIB` |
| Jawaban | Keluar `[TALK_TO_ADMIN]` (permintaan meeting) |

### UAT-6 — SEND_MEDIA menolak dengan jujur *(regresi)*

**Input:** `"ada video demo nggak? kirim dong"`

| Cek | Lolos kalau |
|---|---|
| Jawaban | **Tidak** memakai `[SEND_MEDIA: ...]` untuk nama yang tidak ada di daftar |
| Jawaban | Mengaku video demo belum ada, lalu menawarkan `landing-page` atau `instagram` |
| Kalau pakai tag | Namanya **persis** `landing-page` atau `instagram` |

Ini tes yang **mustahil lolos sebelum patch** — daftar medianya kosong karena placeholder tidak resolve.

### UAT-7 — UNKNOWN untuk di luar sumber fakta *(regresi)*

**Input:** `"VIRA bisa integrasi ke SAP nggak?"`

| Cek | Lolos kalau |
|---|---|
| Output mentah | Muncul `[UNKNOWN]` |
| Jawaban | Mengaku belum tahu, akan diteruskan ke Steven |
| Jawaban | **Tidak mengarang** kemampuan integrasi |
| Sheet UNKNOWN | Baris baru tertulis |

### UAT-8 — Gaya & panjang *(regresi)*

Nilai dari semua balasan UAT-1 s/d UAT-7:

| Cek | Lolos kalau |
|---|---|
| Panjang | ≤ 4 kalimat untuk percakapan biasa |
| Format | Tanpa markdown, tanpa bullet, tanpa tanda bintang |
| Tanda seru | Tidak ada |
| Emoji | Maksimal 1 per balasan |
| Pembuka | Bervariasi, tidak selalu "Baik"/"Oke"/"Wah" |
| PERKENALAN | **Disusun ulang**, bukan disalin persis dari template |

Baris terakhir itu yang gagal di kedua model DeepSeek. Haiku lolos.

### UAT-9 — End-to-end WhatsApp

**Input:** kirim pesan sungguhan dari WA ke nomor bot.

| Cek | Lolos kalau |
|---|---|
| Balasan | Sampai di WhatsApp |
| Sheet STATS | Terupdate |
| MSG_BUFFER | Ditandai consumed |
| Notifikasi | Admin dapat notif untuk TAG yang memerlukannya |
| Error Notifier | Tidak menyala |

---

## Kriteria rilis

| | Wajib lolos |
|---|---|
| **Blocker** | UAT-1, UAT-3, UAT-9 |
| **Mayor** | UAT-2, UAT-4, UAT-6, UAT-7 |
| **Minor** | UAT-5, UAT-8 |

Kalau ada **blocker** gagal → rollback ke workflow hasil backup di langkah import.
Kalau **mayor** gagal → boleh jalan, tapi perbaiki hari itu juga.
Kalau **minor** gagal → catat, perbaiki di siklus berikutnya.

---

## Setelah UAT lolos

Baru bandingkan Flash vs Haiku di **temperature 0.4** dengan prompt yang sudah final ini. Angka tokennya jadi bersih, dan UAT-8 punya dasar pembanding yang adil.
