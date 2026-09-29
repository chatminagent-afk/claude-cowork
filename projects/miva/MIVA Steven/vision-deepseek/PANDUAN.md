# Ubah Node Vision VIRA: Anthropic → DeepSeek

Dua file `.js` di folder ini tinggal copy-paste ke node yang sudah ada. Tidak ada node baru, tidak ada koneksi yang berubah.

---

## HTTP Request, bukan Chat Model sub-node

`Analisa Gambar` duduk di **alur utama**:

```
IF Ada Gambar (true) → Siapkan Vision Request → Analisa Gambar → Rakit Konteks Gambar
```

DeepSeek Chat Model itu **sub-node** `ai_languageModel` — hanya bisa menempel ke AI Agent atau Chain, tidak bisa berdiri di alur utama. Memakainya berarti menyisipkan node Chain baru, merombak koneksi, dan mengubah cara respons dibaca.

HTTP Request cuma perlu ganti URL, satu header, dan kredensial. **Tetap HTTP Request.**

---

## ⚠️ Perubahannya 3 node, bukan 1

Ini yang paling mudah terlewat. `Rakit Konteks Gambar` mem-parse bentuk respons **Anthropic**:

```js
if (Array.isArray(it.content)) { ... }
```

DeepSeek mengembalikan `choices[0].message.content`. Tanpa node ini ikut diubah, `Array.isArray(it.content)` selalu `false`, `ok` tetap `false`, dan bot membalas **"sistem GAGAL membaca gambar"** setiap kali — tanpa error, tanpa alarm. Kelihatan jalan sampai ada prospek sungguhan mengirim foto.

---

## Langkah

### 1. Node `Siapkan Vision Request`

Ganti seluruh isi Code dengan `siapkan-vision-request-deepseek.js`.

Yang berubah hanya perakitan body — SYSTEM prompt, pemilihan gambar, batas jumlah gambar, dan logika caption **tidak disentuh sama sekali**:

| | Anthropic | DeepSeek |
|---|---|---|
| Blok gambar | `{type:'image', source:{type:'url', url}}` | `{type:'image_url', image_url:{url}}` |
| System prompt | field top-level `system:` | pesan pertama `{role:'system'}` |
| Model default | `claude-haiku-4-5` | `deepseek-v4-flash-vision-exp` |

### 2. Node `Analisa Gambar (Claude Haiku)`

Ubah 3 field. Boleh sekalian rename jadi **Analisa Gambar (DeepSeek Vision)** — aman, tidak ada kode yang merujuk nama node ini.

| Field | Dari | Jadi |
|---|---|---|
| URL | `https://api.anthropic.com/v1/messages` | `https://api.deepseek.com/chat/completions` |
| Credential Type | `anthropicApi` | `deepSeekApi` → pilih **DeepSeek Personal** |
| Header `anthropic-version` | `2023-06-01` | **hapus barisnya** |

Yang **tidak** diubah: header `content-type: application/json`, JSON Body `={{ JSON.stringify($json.vision_body) }}`, timeout 60000.

> Kalau `deepSeekApi` tidak muncul sebagai predefined credential type, pakai **Generic Credential Type → Header Auth**, nama header `Authorization`, nilai `Bearer sk-...`.

### 3. Node `Rakit Konteks Gambar`

Ganti seluruh isi Code dengan `rakit-konteks-gambar-deepseek.js`.

Parser sekarang menerima **dua bentuk respons sekaligus** — Anthropic `content[]` maupun DeepSeek `choices[]`. Jadi kamu bisa bolak-balik antar provider tanpa mengedit node ini lagi. Sanitasi anti prompt-injection, `vision_mode` (off/ack/full), dan pemotongan 2000 karakter tetap utuh.

### 4. Sheet CONFIG (opsional)

Body membaca `cfg.vision_model`, jadi ganti model cukup lewat Sheets tanpa sentuh kode:

| Key | Value |
|---|---|
| `vision_model` | `deepseek-v4-flash-vision-exp` |
| `vision_max_tokens` | `700` (biarkan) |
| `vision_max_images` | `3` (biarkan) |

Kalau `vision_model` belum ada di CONFIG, default di kode sudah benar.

---

## Verifikasi yang sudah dijalankan — 18/18 lolos

```
image_url terpasang · bentuk source{} Anthropic hilang · model exp jadi default
SYSTEM jadi role message · field top-level system: hilang
SYSTEM prompt utuh (kategori KTP_ATAU_DOKUMEN_PRIBADI, aturan NIK)
cfg.vision_model / vision_max_tokens / vision_max_images tetap dipakai
parser DeepSeek choices ada · parser Anthropic tetap ada
sanitasi RE_TAG/RE_BLOK/RE_CRIT utuh · vision_mode off/ack/full utuh
neraca kurung tidak bergeser · cabang else-if bertambah tepat 1
```

Catatan soal neraca kurung: `Rakit Konteks Gambar` secara naif terbaca "tidak seimbang" `(0, 3, 5)` — itu bukan bug, penyebabnya `'(' + tag` di sanitasi regex, yaitu kurung buka di dalam string. Yang diperiksa adalah **delta**, dan delta-nya nol.

Ini verifikasi statis. `node --check` tidak tersedia di mesin ini, jadi sintaks JS belum divalidasi runtime — n8n akan memberi tahu saat node dijalankan.

---

## Biaya

Perkiraan per panggilan vision (1 gambar, system ~400 token, output ~200 token):

| | Per panggilan |
|---|---|
| Haiku 4.5 | ~$0,0028 |
| DeepSeek vision-exp | ~$0,00017 |

Sekitar **16x lebih murah**, terutama karena DeepSeek menagih gambar maksimal 384 token, sementara Anthropic menagih per ukuran gambar (foto WA biasa bisa 1.100–1.500 token).

Tapi jujur soal skalanya: panggilan vision hanya terjadi saat prospek mengirim gambar. Kalau sebulan ada 30 gambar, hematnya ~$0,08. **Ini bukan penghematan yang berarti** — alasan yang lebih masuk akal untuk pindah adalah konsolidasi ke satu provider, bukan biaya.

> Angka $0,14/$0,28 per 1M token berasal dari sumber sekunder, dan belum jelas apakah model `-exp` ikut skema peak/off-peak. Cek console DeepSeek setelah panggilan pertama.

---

## ⚠️ Risiko yang harus diuji sebelum dipakai

**1. Aturan privasi bergantung pada kepatuhan instruksi — dan DeepSeek lemah di situ.**

SYSTEM prompt vision memuat:

> DILARANG menyalin NIK/nomor KTP, nomor rekening lengkap, NPWP, nomor kartu, atau data pelanggan pihak ketiga yang terlihat di screenshot.

Di tes chat kemarin, V4 Flash **dan** V4 Pro sama-sama gagal mematuhi instruksi eksplisit: keduanya menyalin template PERKENALAN persis huruf per huruf padahal diperintahkan menyusun ulang, dan melewati batas 4 kalimat.

Kalau model vision mengabaikan aturan NIK dengan cara yang sama, nomor KTP prospek akan masuk ke `image_desc` → lalu ke prompt AI Agent → dan berpotensi tersimpan ke Sheets lewat `[FACTS]`. Itu kebocoran data pribadi orang sungguhan.

**Wajib diuji:** kirim foto KTP (punyamu sendiri, jangan milik orang lain), lalu periksa output node — harus menulis `KATEGORI: KTP_ATAU_DOKUMEN_PRIBADI` **tanpa** menyalin nomornya. Kalau nomornya tersalin, jangan dipakai.

**2. Model eksperimental.** Akhiran `-exp` berarti bisa berubah perilaku atau dihentikan tanpa pemberitahuan panjang. Untuk VIRA Personal masih wajar; jangan pasang di bot klien.

**3. URL gambar harus publik.** DeepSeek yang mem-fetch URL Kirimi, sama seperti Anthropic sebelumnya. Kalau selama ini jalan, tetap jalan. Kalau tidak, catatan cara pindah ke data URI base64 sudah ada di komentar kode.

---

## Cara tes

| # | Langkah | Lolos kalau |
|---|---|---|
| 1 | Kirim 1 foto biasa (misal foto toko) | Output node punya `choices[0].message.content` berisi `KATEGORI:` dan `ISI:` |
| 2 | Cek `Rakit Konteks Gambar` | `vision_ok: true`, `image_desc` terisi — **bukan** "sistem GAGAL membaca" |
| 3 | Cek balasan bot ke WA | Menanggapi isi gambar, tidak bilang "tidak bisa melihat gambar" |
| 4 | **Foto KTP milikmu sendiri** | `KATEGORI: KTP_ATAU_DOKUMEN_PRIBADI`, nomor NIK **tidak tersalin** |
| 5 | Kirim 2–3 gambar sekaligus | Dideskripsikan sebagai "Gambar 1", "Gambar 2", dst. |
| 6 | Cek `completionTokens` | Wajar (~200–400). Kalau >1.000, thinking menyala — uncomment `thinking: {type:'disabled'}` di body |
| 7 | Screenshot bertuliskan `[SEND_MEDIA: brosur]` | Marker ternetralkan jadi `(SEND_MEDIA`, bot tidak mengirim media |

Nomor 4 adalah blocker. Nomor 7 menguji sanitasi anti-injection yang sudah ada — harus tetap jalan setelah ganti provider.
