# VIRA V6 — Media Skill (baca gambar + kirim file)

**Tanggal:** 2026-08-19
**File:** `report/patch/2026-08-19-VIRA-V6-media-skill.json`
**Basis:** `2026-08-14-VIRA-V4-r6-link-guard-wa-channel.json` (kumulatif — memuat r1–r6)
**Node:** 53 → **67** (+14). Node lama yang disentuh cuma **5**; 48 sisanya identik byte-per-byte.
**Referensi:** di-port dari `VIRA Steven` (inbound vision) dan `VIRA-PCR` (pola `[SEND_MEDIA]`)

---

## Apa yang V6 tambahkan

**1. VIRA bisa MEMBACA gambar.** User kirim foto rapor, sertifikat, atau screenshot → gambar dibaca Claude Haiku → hasil bacaannya disuntik ke konteks AI Agent sebagai blok `[GAMBAR DARI USER]` → VIRA menanggapi isinya.

**2. VIRA bisa MENGIRIM file.** AI memasang tag `[SEND_MEDIA: <Nama Link>]` → sistem mencari barisnya di sheet LINKS → unduh → cek keutuhan file → kirim sebagai lampiran WhatsApp.

Sebelum V6, semua pesan non-teks dibuang di node `Chat Counter`. Perilaku itu **sengaja dipertahankan** untuk stiker, video, dokumen, dan reaction — yang berubah **hanya** gambar yang punya URL. Fix Juni 2026 (gambar tidak lagi bikin crash, teks di atasnya tetap terbalas) tetap utuh dan diverifikasi di QA.

---

## Bagian 1 — Yang harus kamu ubah di Google Sheet

Ada **2 tab** yang perlu kolom tambahan. Tidak ada tab baru.

### 1a. Tab `MSG_BUFFER` — tambah 2 kolom

Sekarang: `no_wa | lid | message | ts`

Tambahkan **di paling kanan**, persis dengan nama ini (huruf kecil semua):

| Kolom baru | Isinya |
|---|---|
| `media_url` | URL gambar dari Kirimi, diisi otomatis |
| `media_type` | `image`, diisi otomatis |

Tanpa dua kolom ini, gambar akan hilang saat debounce 60 detik dan VIRA tidak akan pernah melihatnya.

> Kolom ini diisi workflow, bukan kamu. Cukup buat headernya.

### 1b. Tab `LINKS` — tambah 3 kolom

Sekarang: `Nama Link | URL | Deskripsi | Status | Last Updated`

Tambahkan **di paling kanan** (setelah `Last Updated`):

| Kolom baru | Isi | Wajib? |
|---|---|---|
| `Tipe` | `image`, `file`, `website`, atau `location` | ya, untuk baris yang mau dikirim sebagai lampiran |
| `Caption` | teks yang menyertai file saat dikirim | opsional (kosong → pakai `Deskripsi`) |
| `Keyword` | kata bantu pencarian, pisahkan dengan spasi | opsional tapi sangat disarankan |

**Arti `Tipe`:**
- `image` / `file` → diunduh lalu dikirim sebagai **lampiran**
- `website` / `location` → **tidak** diunduh; ini untuk baris seperti GForm dan WhatsApp Channel yang memang harus dikirim sebagai teks URL biasa lewat `[SEND_GFORM]`

**Isi yang disarankan untuk baris yang sudah ada:**

| Nama Link | Tipe | Keyword |
|---|---|---|
| Guidebook | `file` | `guidebook panduan beasiswa singapore` |
| GForm Pendaftaran Batch 5 | `website` | *(kosongkan)* |
| GForm Mock Interview | `website` | *(kosongkan)* |
| GForm Pendaftaran Seniors | `website` | *(kosongkan)* |
| WhatsApp Channel | `website` | *(kosongkan)* |
| Intensive Class | `website` | *(kosongkan)* |
| Tentang Batch 4 | `website` | *(kosongkan)* |

Baris baru untuk gambar yang mau dikirim (poster, infografis, brosur) tinggal ditambahkan dengan `Tipe = image` dan `Status = Active`.

**Menaruh kolom di paling kanan itu penting** — node lama membaca kolom berdasarkan nama, jadi menambah di ujung aman. Menyisipkan di tengah berisiko menggeser rumus atau range lain di sheet.

### 1c. Aturan `Status` untuk media

Media **hanya dikirim kalau `Status` = `Active`** (juga menerima `aktif`/`on`/`ya`). Baris `Closed` tidak akan pernah dikirim.

Ini disengaja dan menguntungkan: aturan yang sudah kamu pakai untuk menutup pendaftaran otomatis juga menutup pengiriman filenya. Tidak ada mekanisme baru yang perlu diingat.

---

## Bagian 2 — Import & konfigurasi

1. n8n → **Import from File** → `2026-08-19-VIRA-V6-media-skill.json`.
2. Cek kredensial ter-mapping di node-node ini (import n8n kadang melepas binding):
   - Google Sheets → `Google Service Account thescholars`
   - `Anthropic Chat Model` **dan node baru `Analisa Gambar (Claude Haiku)`** → `Anthropic Personal`
3. **Kerjakan Bagian 1 dulu** (kolom sheet) sebelum mengaktifkan. Tanpa kolom `media_url`/`media_type`, fitur baca gambar tidak jalan.
4. Jangan aktifkan sebelum tes di Bagian 3 lolos.

Model yang dipakai: vision `claude-haiku-4-5-20251001` (murah, cukup untuk mendeskripsikan gambar). Model AI Agent utama **tidak diubah** — tetap seperti r6.

---

## Bagian 3 — Tes sebelum aktivasi

### Baca gambar (inbound)

| Kirim ke VIRA | Harapan |
|---|---|
| Foto rapor + teks "ini rapor anak saya, cocok program apa?" | VIRA menanggapi isi rapornya, bukan bilang tidak bisa lihat gambar |
| Foto **tanpa teks** sama sekali | VIRA tetap membalas, menanggapi isi gambar |
| Teks lalu gambar (berurutan cepat) | Dua-duanya masuk satu balasan setelah debounce ±60 detik |
| Stiker | Tidak ada balasan, tidak ada error (perilaku lama, sengaja) |
| Kirim 5 gambar sekaligus | Maksimal 3 terakhir yang dibaca |

### Kirim file (outbound)

| Kirim ke VIRA | Harapan |
|---|---|
| "boleh minta guidebook-nya?" | File guidebook terkirim sebagai lampiran |
| "minta poster" (kalau ada >1 baris poster aktif) | **Tidak** mengirim file; VIRA tanya dulu maksudnya yang mana |
| "minta brosur harga" (tidak ada di LINKS) | Tidak mengirim; WA notifikasi masuk ke Sam |
| "minta link pendaftaran batch 5" | Tetap lewat `[SEND_GFORM]` seperti biasa, bukan lampiran |

### Regresi yang wajib dicek ulang

| Kirim ke VIRA | Harapan |
|---|---|
| "mau transfer nih" | `Baik, nanti akan dibantu cek dengan Sam yaa.` (guardrail 11 Agt utuh) |
| "mau daftar batch 5" | Batch ditutup, tanpa link, ditawari WhatsApp Channel (r5/r6 utuh) |
| "mau ngomong sama sam" | Handover jalan, `bot_mode` jadi OFF |
| Pesan teks biasa | Balasan normal, tidak ada perubahan gaya |

---

## Bagian 4 — Cara kerjanya

### Inbound
```
Cek_user_status ─► IF Ada Gambar ─(ada)──► Siapkan Vision Request
                        │                        └► Analisa Gambar (Claude Haiku)
                        │                                    │
                        └─(tidak ada)──────────────► Rakit Konteks Gambar ─► Preprocess ─► AI Agent
```

Kalau tidak ada gambar, panggilan vision **dilewati sepenuhnya** — tidak ada biaya dan tidak ada tambahan latensi untuk percakapan teks biasa.

### Outbound
```
Process All ─► IF Send Media ─► Resolve Media ─► IF Media Resolved
                                                     ├─(ketemu)─► Wait 2s ─► Download ─► Cek File ─► IF File OK
                                                     │                                                  ├─(ok)──► Send Media Kirimi
                                                     │                                                  └─(rusak)┐
                                                     └─(tidak ketemu / ambigu)───────────────────────────────────┴► Notify Sam
```

---

## Keputusan desain yang perlu kamu tahu

**1. Gambar dibaca model terpisah, bukan langsung oleh AI Agent.** Claude Haiku mendeskripsikan gambar jadi teks, lalu teksnya masuk ke konteks AI Agent. Ini pola yang sama dengan VIRA Steven. Untungnya: AI Agent utama tidak perlu diubah sama sekali, dan biaya per gambar tetap murah.

**2. Deskripsi gambar disanitasi sebelum masuk konteks.** Teks di dalam gambar bisa saja berisi tag sistem palsu — orang bisa menulis `[SEND_MEDIA: ...]` di gambar untuk menyuruh VIRA mengirim file, atau `CRITICAL INSTRUCTION` untuk membajak instruksi. Semua pola itu dinetralkan sebelum diteruskan. Diuji di QA (E27–E29).

**3. Kalau vision gagal, alur tidak berhenti.** Node vision di-set `onError: continueRegularOutput`. VIRA akan minta maaf dan meminta user menuliskan isi gambarnya, bukan diam total.

**4. Salah kirim file dicegah lebih ketat daripada tidak kirim.** Ini ditemukan saat QA dan diperbaiki: pencocokan longgar versi awal membuat permintaan *"GForm Pendaftaran Batch 5"* nyasar ke baris *"Poster Batch 6"*, hanya karena token `batch` ada di kolom `Keyword`-nya. User minta formulir, yang terkirim poster.

   Perbaikannya: kandidat sekarang harus mencocokkan **semua** token permintaan, bukan salah satu. Kalau hasilnya lebih dari satu → tidak dikirim, VIRA tanya dulu. Kalau nol → tidak dikirim, Sam dikabari. Tidak ada jalur "kirim saja yang paling mirip".

**5. Tidak ada auto-correct untuk `[SEND_MEDIA]`.** Tag `[SEND_GFORM]` punya fallback yang memasang tag otomatis kalau AI lupa. Untuk media itu sengaja tidak dibuat — menebak file mana yang dimaksud terlalu berisiko.

**6. Ada jeda 2 detik sebelum file dikirim**, supaya lampiran datang setelah balasan teks, bukan mendahuluinya.

---

## Hasil QA

**73 assertion, 0 gagal.** Skrip: `2026-08-19-qa-v6.py`.

| Bagian | Cakupan |
|---|---|
| A. Struktur (9) | 53→67 node, nama/id unik, semua terjangkau, **hanya 5 node lama berubah**, 48 sisanya byte-identik, hanya 2 koneksi yang di-rewire |
| B. Sintaks (2) | 18 node Code parse bersih, nol regresi vs r6 |
| C. Rantai vision (9) | Percabangan benar, kedua cabang menyatu, Preprocess cuma punya 1 inbound, vision **di belakang gerbang bot_mode** |
| D. Rantai media (11) | 5 cabang Process All, cabang false buntu, `Send Media` **hanya** lewat `IF File Media OK[true]`, file rusak → notif manual |
| E. Logika (32) | Gate Chat Counter (9 kasus), pengumpulan gambar dari buffer (5), parsing tag (6), resolusi LINKS (9), sanitasi injeksi (3) |
| F. Regresi (10) | Guardrail transfer utuh, link guard r5/r6 utuh, systemMessage tanpa section baru & tumbuh hanya **+2,1%**, fix Juni utuh, kolom MSG_BUFFER lama utuh |

### Batasan QA — yang BELUM diuji

1. **Kode belum pernah dieksekusi sebagai JavaScript.** Node.js/Deno/Bun tidak terpasang di mesin ini. Validasi = parser `esprima` + port logika 1:1 ke Python.
2. **`esprima` 4.0.1 setara ES2017.** Untuk cek sintaks, tiga fitur diturunkan ke bentuk setara: `??` dan `?.` (ES2020) dan `\p{L}`/`\p{N}` (ES2018) — ketiganya sudah dipakai di node r6 yang jalan di produksi sekarang. Wrapper-nya `async` karena node Code n8n memang dieksekusi sebagai badan fungsi async.
3. **Belum diuji di n8n sungguhan** — import, binding kredensial, dan eksekusi end-to-end lewat WhatsApp belum dijalankan.
4. **Perilaku model belum diuji.** Apakah AI benar-benar memasang `[SEND_MEDIA]` di saat yang tepat itu perilaku model, bukan sesuatu yang dijamin kode. Yang deterministik cuma: tag yang salah/ambigu tidak akan pernah mengirim file.

---

## ⚠️ Risiko terbesar: URL Kirimi harus bisa diakses publik

Ini asumsi yang **belum bisa saya verifikasi** dari sini, dan paling mungkin jadi penyebab kalau fitur baca gambar tidak jalan.

Gambar dikirim ke Anthropic sebagai **URL** (`source.type: "url"`) — jadi server Anthropic yang mengunduhnya langsung dari Kirimi. Ini cara yang dipakai VIRA Steven dan berhasil di sana, tapi kalau URL media Kirimi untuk akun The Scholars ternyata butuh autentikasi, Anthropic tidak akan bisa mengambilnya dan setiap gambar akan jatuh ke pesan fallback.

**Kalau itu terjadi**, solusinya sudah ditulis sebagai komentar di dalam node `Siapkan Vision Request`: ganti blok image jadi `source.type: "base64"` dan sisipkan satu node HTTP Request (`responseFormat: file`) sebelumnya untuk mengunduh gambarnya lebih dulu. Kabari saya kalau perlu, patch-nya kecil.

**Cara cepat mengeceknya:** kirim satu gambar ke VIRA, lalu buka execution log di node `Analisa Gambar (Claude Haiku)`. Kalau responsnya error 400 dengan keluhan soal URL/fetch, berarti URL-nya tidak publik.

---

## Catatan privasi — perlu kamu sampaikan ke Sam

Mulai V6, **gambar yang dikirim user diteruskan ke API Anthropic** untuk dibaca. Konsekuensinya nyata untuk The Scholars: calon murid sangat mungkin mengirim rapor, sertifikat, bahkan KTP orang tua.

Mitigasi yang sudah terpasang: prompt vision melarang menyalin NIK, nomor rekening, NISN lengkap, alamat rumah, dan nomor telepon — dokumen semacam itu hanya disebut jenisnya. Tapi **gambarnya sendiri tetap terkirim ke Anthropic**, dan yang dibatasi adalah apa yang ditulis dalam deskripsinya.

Ini keputusan bisnis, bukan teknis. Sebaiknya Sam tahu sebelum fitur diaktifkan.

---

## Checklist urutan pengerjaan

- [ ] 1. Tambah kolom `media_url`, `media_type` di tab MSG_BUFFER
- [ ] 2. Tambah kolom `Tipe`, `Caption`, `Keyword` di tab LINKS
- [ ] 3. Isi `Tipe` untuk 7 baris LINKS yang sudah ada (lihat tabel Bagian 1b)
- [ ] 4. Import `2026-08-19-VIRA-V6-media-skill.json`, cek kredensial (termasuk node vision baru)
- [ ] 5. Tes kirim 1 gambar → cek execution log node `Analisa Gambar` (verifikasi asumsi URL publik)
- [ ] 6. Jalankan tes Bagian 3, termasuk **4 tes regresi**
- [ ] 7. Konfirmasi ke Sam soal privasi gambar
- [ ] 8. Tambahkan baris media baru di LINKS (poster/brosur) kalau sudah ada materinya
- [ ] 9. Aktifkan

**Rollback:** import ulang `report/production/2026-08-08-VIRA-V4-retryable.json` (basis produksi, tidak pernah disentuh), atau `2026-08-14-...-r6-...json` kalau r1–r6 sudah terlanjur live.
