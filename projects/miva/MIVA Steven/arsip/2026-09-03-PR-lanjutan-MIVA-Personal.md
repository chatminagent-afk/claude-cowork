# PR Lanjutan — VIRA Personal

Hasil sesi 2026-09-02 (malam). Konteks: investigasi biaya API + eksperimen migrasi ke DeepSeek.

---

## 0. Yang sudah selesai — jangan diulang

| | Temuan |
|---|---|
| ✅ | **Placeholder `{{ $json.*_context }}` sudah diperbaiki.** Penyebabnya field `systemMessage` di node AI Agent ada di mode **Fixed**, bukan Expression. Sebelum ini VIRA jalan tanpa FAQ, DATA PRODUK, DAFTAR MEDIA, dan DATA PROSPEK — `[SEND_MEDIA]` mustahil benar karena daftarnya kosong. Ini perbaikan paling berharga dari sesi ini. |
| ✅ | **Model produksi VIRA Personal itu Haiku 4.5** (`claude-haiku-4-5-20251001`), bukan Sonnet. 4,7 juta token Sonnet 4.6 di console Agustus itu milik bot lain (The Scholars / Persada / Claude Code). |
| ✅ | **Output kosong DeepSeek = thinking mode.** Bukan bug konfigurasi. V4 Pro & Flash menyalakan thinking secara default; token habis untuk berpikir sebelum sempat menulis jawaban. |
| ✅ | **Node DeepSeek bawaan n8n tidak bisa mematikan thinking.** Tidak ada field-nya. Alias `deepseek-chat`/`deepseek-reasoner` juga sudah dipensiunkan 24 Juli 2026. |

---

## 1. Mendesak — korektif

### 1.1 Kembalikan Chat Model ke Anthropic Haiku 4.5
Port **Chat Model** di AI Agent harus tersambung ke node Anthropic, bukan DeepSeek. VIRA Personal saat ini tidak jalan.

### 1.2 Hapus node yatim di kanvas
Node bertipe `n8n-nodes-deepseek.deepSeek` — kemungkinan besar node **"Create chat completion"**. n8n menolak menjalankan workflow yang memuat node dengan tipe tidak dikenal, walaupun node itu tidak tersambung ke apa pun.

Tekan `1` di kanvas untuk zoom-to-fit; node tak dikenal muncul dengan ikon tanda tanya.

### 1.3 Bersihkan community node yang gagal
- `n8n-nodes-deepseek-v4-thinking-fix` (zeek_br) — **gagal di n8n 2.3.4**
- package adcom — sudah tidak dipakai
- `n8n-nodes-openrouter-cache-chat-model` — **sisakan**, masih kandidat (lihat §3.4)

### 1.4 ⚠️ Putuskan aturan nama klien — PALING MENDESAK

Dua aturan yang saling bertentangan sekarang **dikirim bersamaan** ke model. Ini baru muncul karena placeholder-nya sudah jalan; sebelumnya `about_context` tidak pernah sampai.

**Di system prompt (hardcoded), bagian LARANGAN:**
> Jangan menyebut nama klien Steven yang sudah ada... Cukup "salah satu klienku platform edukasi" dan "klien lainnya developer properti".

**Di `about_context` (dari Sheets), ATURAN INTERNAL:**
> Nama kedua klien (The Scholars dan Persada Cisoka Residence) BOLEH disebut... keduanya sudah tampil di landing page atas seizin mereka.

Model harus memilih sendiri → perilakunya tidak bisa diprediksi. Sementara blok TENTANG STEVEN di bawahnya sudah menyebut kedua nama itu terang-terangan berikut deskripsi bisnisnya.

**Dua pilihan:**
- **Nama boleh disebut** (sesuai izin landing page) → hapus paragraf klien di LARANGAN
- **Nama tidak boleh** → ubah ATURAN INTERNAL di Sheets, dan ganti nama klien di TENTANG STEVEN jadi deskripsi generik

Catatan: aturan untuk bot ini berbeda dari aturan konten @povstevens (di konten, nama klien tetap tidak disebut).

---

## 2. Optimasi prompt — tanpa upgrade, tanpa pihak ketiga

Total ± **690 token** per panggilan. Semua bisa dikerjakan hari ini.

### 2.1 Urutkan ulang blok di system prompt

Sekarang:
```
instruksi → DATA PROSPEK → BRIEF TERISI → TENTANG STEVEN → DATA PRODUK → DAFTAR MEDIA → FAQ RELEVAN
```

Jadi:
```
instruksi → TENTANG STEVEN → DATA PRODUK → DAFTAR MEDIA → DATA PROSPEK → BRIEF TERISI → FAQ RELEVAN
```

Alasan: `prospect_context` & `brief_context` berubah per user, `faq_context` berubah per pesan (hasil retrieval). Menaruhnya di depan membuat semua blok statis di belakangnya ikut batal cache.

Belum berguna sebelum caching aktif, **tapi jadi prasyarat** begitu aktif — bedanya caching yang hemat 35% vs 60% (prefix yang bisa di-cache: ~4.400 vs ~6.100 token).

### 2.2 Pangkas `calendarBlock` — warisan Persada

Node **`Preprocess - Context Detection`**, header aslinya masih:
```js
// PREPROCESS - CONTEXT DETECTION (domain properti PCR)
```

Isinya deteksi `Tipe 36/72`, `UNIT_INTEREST`, `BUDGET_RANGE`, dan tabel kalender 7 hari + `JAM_OPERASIONAL_SURVEY: 08:00-17:00`. VIRA Personal tidak menjadwalkan survey unit — itu alur Persada.

Pangkas jadi dua baris saja: `TODAY` + `NOW_WIB`. Tanggal masih berguna untuk field `deadline` di DECK_REQUEST.

Dampaknya berlipat: blok ini ikut di **setiap** giliran user dan tersimpan sampai **10 kali** di Simple Memory (`contextWindowLength: 10`).

### 2.3 Hapus 4 duplikasi aturan

Ditulis dua kali — sekali hardcoded, sekali dari Sheets:

| Aturan | Di system prompt | Di about_context |
|---|---|---|
| Identitas "Steven versi AI" | paragraf pembuka | `Identitas:` |
| Jujur soal AI | bagian IDENTITAS | `Kejujuran:` |
| Larangan nama bank | LARANGAN | `PANTANGAN — nama employer` |
| Larangan teknis internal | LARANGAN | `PANTANGAN — teknis internal` |

Bahaya sebenarnya bukan token, tapi maintenance: update satu lupa yang lain → kontradiksi baru seperti §1.4. **Pilih satu sumber — sebaiknya Sheets**, karena bisa diubah tanpa menyentuh workflow.

### 2.4 Pangkas "Arti tiap baris" di DECK_REQUEST

20 baris menjelaskan field yang sebagian besar sudah jelas dari namanya (`nama`, `kota`, `industri`, `deadline`, `pain_points`). Sisakan yang benar-benar ambigu: `aksi_utama`, `alur_setelah_chat`, `bahasa_deck`, `catatan`. ± 350 token.

---

## 3. Riset — 10 menit, nol risiko ke produksi

Semua dikerjakan di **container sekali pakai**, bukan di instance produksi:

```bash
docker run -it --rm -p 5679:5678 -v n8n_uji:/home/node/.n8n docker.n8n.io/n8nio/n8n:2.11.3
```

Akses lewat SSH tunnel (tidak perlu buka port di firewall):

```bash
ssh -L 5679:localhost:5679 root@IP_VPS
```

Lalu buka `http://localhost:5679`.

### 3.1 Apakah versi baru punya prompt caching di node Anthropic?
Bikin node **Anthropic Chat Model** → **Add Option** → cari opsi caching.

Di n8n 2.3.4 **tidak ada** — Add Option cuma berisi Top K & Top P. Kalau di versi baru ada, upgrade jadi layak (lihat §4).

### 3.2 Apakah node DeepSeek zeek_br jalan di versi itu?
Install `n8n-nodes-deepseek-v4-thinking-fix` di container uji. Kalau jalan, itu konfirmasi bahwa error `@n8n/ai-utilities` murni soal versi n8n.

### 3.3 Kandidat DeepSeek untuk n8n 2.3.4: `n8n-nodes-deepseek-fix` (raevon)

Satu-satunya kandidat yang **belum diuji**. v0.2.20, update 4 bulan lalu, 8.884 downloads, MIT, 0 dependensi. Deskripsinya sama persis: *"DeepSeek V4 models (deepseek-v4-flash, deepseek-v4-pro) with thinking mode control"*.

**Koreksi penilaian kemarin:** aku memilih zeek_br karena lebih baru — logikanya benar untuk kompatibilitas API DeepSeek, tapi salah untuk kompatibilitas n8n. Package yang lebih tua justru dibangun untuk n8n yang lebih tua, jadi **lebih mungkin cocok dengan 2.3.4**.

Cek kompatibilitas **sebelum** install — ini yang mencegah jebakan `@n8n/ai-utilities` terulang:

```bash
npm view n8n-nodes-deepseek-fix peerDependencies dependencies engines
```

### 3.4 Tes eksekusi node OpenRouter caching
`n8n-nodes-openrouter-cache-chat-model` sudah terpasang dan **UI-nya render normal** — tapi node DeepSeek juga begitu sebelum gagal saat dijalankan. Rendering bukan bukti. Harus dites eksekusi sungguhan.

Kalau dipakai: gunakan **BYOK** (masukkan API key Anthropic-mu di setting OpenRouter), jangan beli kredit OpenRouter.
- BYOK: **1 juta request/bulan pertama gratis** — kamu jauh di bawah itu. Tagihan tetap ke Anthropic, console Anthropic tetap mencatat usage.
- Beli kredit: fee 5,5% **dengan minimum $0,80** — untuk chatbot Haiku bervolume kecil ini bisa jadi ~20% lebih mahal.

### 3.5 Cari community node caching Anthropic langsung
Belum ketemu yang langsung ke Anthropic (tanpa OpenRouter). Coba cari di npm: `n8n-nodes-anthropic`, `claude cache`, `anthropic cache chat model`. Cek `peerDependencies` sebelum install.

---

## 4. Keputusan besar — jangan buru-buru

### Upgrade n8n 2.3.4 → versi baru?

**Untungnya bukan DeepSeek.** Kalau prompt caching native ada di versi baru, itu berlaku untuk **semua bot** — termasuk The Scholars & Persada. Console Agustus mencatat 4,7 juta token input Sonnet 4.6 ≈ $14/bulan; caching bisa memangkas ~60% → **hemat ~$8–9/bulan di seluruh estate**, plus latensi turun, plus tidak tertinggal patch keamanan.

Bandingkan dengan hadiah jalur DeepSeek: ~$0,006 per balas di bot pribadi saja.

**Risikonya nyata:**
- Instance ini menjalankan **dua bot klien yang hidup**. n8n down = pesan WhatsApp prospek tidak terbalas, dan tidak ada antrian yang menampungnya.
- **Migrasi database n8n satu arah.** Setelah skema ter-migrasi, turun balik ke 2.3.4 kemungkinan besar gagal.
- Ada laporan konflik dependensi di n8n 2.8.3+ ([#26714](https://github.com/n8n-io/n8n/issues/26714), [#26960](https://github.com/n8n-io/n8n/issues/26960)) — bentrokan versi `@langchain/core`.

**Prasyarat wajib sebelum mulai:**
1. **Snapshot VPS Hostinger** — satu-satunya jalan pulang
2. **Catat `N8N_ENCRYPTION_KEY`** — kalau hilang/berubah, **semua credential jadi tidak terbaca**. Ada di `.env` (Docker) atau `~/.n8n/config` (npm)
3. Backup folder `~/.n8n` / volume Docker
4. Kerjakan di jam sepi, sediakan waktu luang untuk menangani kalau ada yang pecah

**Cara upgrade (Docker Compose)** — pin ke versi pasti, jangan `:latest`:
```
image: docker.n8n.io/n8nio/n8n:2.11.3
```
```bash
docker compose pull && docker compose up -d
```

**Cek dulu cara install-mu yang mana:**
```bash
docker ps --format "{{.Names}}\t{{.Image}}"
```

---

## 5. Angka referensi

Basis: prompt produksi ± **6.700 token** (setelah placeholder benar, sebelum dipangkas), output ± 60 token.

| Konfigurasi | Per balas | Catatan |
|---|---|---|
| **Haiku 4.5 (sekarang)** | **$0,0070** | jalan, thinking off |
| Haiku 4.5 + caching | ~$0,0029 | butuh §3.1 atau §3.4 |
| V4 Flash thinking OFF | $0,0015 / $0,0030 peak | butuh community node yang jalan |
| V4 Pro thinking ON | $0,0087 / $0,0173 peak | **lebih mahal dari Haiku** |
| V4 Pro thinking OFF | $0,0050 / $0,0100 peak | |

**Kenapa V4 Pro tidak layak walau thinking bisa dimatikan:** beban kerja VIRA 99% input, jadi yang menentukan cuma harga input.

| Model | Input off-peak | Input peak | Rata-rata |
|---|---|---|---|
| Haiku 4.5 | $1,00 | $1,00 | **$1,00** |
| V4 Pro | $0,66 | $1,32 | **$0,99** |
| V4 Flash | $0,22 | $0,44 | **$0,33** |

Jam peak DeepSeek = **08:00–11:00 dan 13:00–17:00 WIB** — persis jam prospek chat. Dirata-rata, V4 Pro jadi **identik dengan Haiku**. Hanya Flash yang benar-benar lebih murah.

---

## 6. Urutan yang disarankan

1. §1.1–1.3 — kembalikan Haiku, bersihkan node yatim & package gagal *(15 menit)*
2. §1.4 — putuskan aturan nama klien *(keputusan, bukan teknis)*
3. §2.1–2.4 — pangkas prompt *(± 690 token, nol risiko)*
4. §3 — riset di container sekali pakai *(10 menit, nol risiko)*
5. §4 — kalau §3.1 hasilnya positif, rencanakan upgrade untuk hari lain

Kalau §3.1 negatif dan §3.3 juga gagal: berhenti di Haiku + prompt yang sudah dipangkas. Itu sudah hasil yang baik — bot yang akhirnya menerima seluruh data groundingnya, dengan prompt 10% lebih ramping.
