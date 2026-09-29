# Catatan Build — Workflow VIRA Steven

> ⛔ **KEDALUWARSA (2026-08-16).** Isinya menggambarkan build 88 node sebelum rantai `[DECK_REQUEST]`
> dan sebelum lima bug ditemukan. Beberapa klaim di dalamnya sudah tidak benar.
> **Baca `2026-08-16-catatan-build-workflow.md`.** File ini disimpan hanya sebagai riwayat.

Dibangun dengan **mentransformasi** `2026-08-08-VIRA-PCR-Main-V2.1` (91 node), bukan ditulis dari nol.
Skripnya ada di `_transform.py` dan **idempoten** — aman dijalankan ulang kapan saja; dia selalu
membaca ulang file Persada asli dan menghasilkan output yang sama.

```bash
python _transform.py
```

Hasil: **88 node**, tanpa koneksi menggantung, tanpa node yatim.

---

## Yang sudah selesai dan terverifikasi

| # | Perubahan | Verifikasi |
|---|---|---|
| 1 | 5 node alur survei & request-call dihapus, alurnya dijembatani ulang | ✅ tidak ada node yatim |
| 2 | `Whitelist Gate` → **`Blocklist Gate`** (kode ditulis ulang total) | ✅ bot publik, blocklist dari CONFIG, anti-loop diri sendiri |
| 3 | `Read PRODUK Data` → **`Read PROGRAM Data`** | ✅ tab `PROGRAM` |
| 4 | Node **`Read ABOUT_STEVEN`** ditambahkan | ✅ tersisip di rantai baca |
| 5 | Notifikasi tim lapangan & media dialihkan ke HP Steven | ✅ 15 referensi diganti ke `admin_phone` |
| 6 | Sheet ID diganti | ✅ hanya `1C5gF...O_Yxk` |
| 7 | Model: balasan `claude-sonnet-5` (thinking **dimatikan**), utilitas `claude-haiku-4-5` | ✅ tidak ada model lain |
| 8 | Kredensial jadi placeholder | ✅ `Anthropic Personal Steven`, `Google Service Account VIRA Steven` |
| 9 | `meta.instanceId`, `id`, `versionId` dibersihkan | ✅ tidak ada sidik jari instance lama |
| 10 | System prompt disuntik (9.601 karakter) | ✅ ke node `AI Agent` |
| 11 | Node **`Rakit Konteks`** ditambahkan sebelum AI Agent | ✅ 5 variabel tersambung ujung ke ujung |
| 12 | Pemetaan kolom `Update to STATS` diperbaiki | ✅ 9 kolom Persada dibuang, 10 kolom VIRA Steven ditambah |
| 13 | **Bug trailing-space `pending_survey_*` hilang** | ✅ tidak ada nama kolom dengan spasi di ujung |
| 14 | `active: false`, webhook path `wa-inbound-steven` | ✅ |

**Yang paling menentukan adalah nomor 11.** System prompt merujuk `prospect_context`, `about_context`,
`program_context`, `links_context`, dan `faq_context`. Di workflow Persada tidak ada satu pun node yang
memproduksi empat yang pertama — tanpa `Rakit Konteks`, VIRA akan menjawab tanpa data sama sekali.

Node itu juga menegakkan dua aturan privasi di level kode: kolom `Catatan Internal` (PROGRAM & LINKS)
tidak pernah ikut terkirim ke AI, dan baris `Boleh Dibagikan = Tidak` (ABOUT_STEVEN) dikirim sebagai
**aturan**, bukan sebagai fakta yang boleh dibacakan.

---

## ⚠️ Yang BELUM selesai — baca sebelum go-live

Workflow ini **sudah bisa di-import dan mengobrol dengan grounding penuh**, tapi mesin penangkap
lead-nya belum tersambung. Jangan nyalakan iklan sebelum bagian ini beres.

### 1. `[DECK_REQUEST]` belum diparsing — PRIORITAS TERTINGGI
`Process All` (27KB) masih memakai set tag Persada. Yang **sudah jalan** karena memang ada di Persada:
`[SEND_MEDIA]`, `[TALK_TO_ADMIN]`, `[UNKNOWN]`, `[FACTS]`.

Yang **belum ada**: parsing blok `[DECK_REQUEST]...[/DECK_REQUEST]`, penulisan ke tab `REQUESTS`,
notifikasi rangkuman ke HP Steven, dan penandaan `deck_requested=Y`.

**Akibatnya:** VIRA akan tetap mengumpulkan brief dan mengatakan "Steven akan menghubungimu",
tapi **tidak ada baris yang masuk ke tab REQUESTS dan tidak ada notifikasi yang terkirim.**
Ini persis tujuan utama bot, jadi ini yang harus dikerjakan lebih dulu.

### 2. Kolom fakta baru belum benar-benar terisi
`Update to STATS` sudah menulis ke `nama_bisnis`, `industri`, `masalah_utama`, `volume_chat`,
`minat_paket`, `bahasa` — tapi ekspresinya menunggu field `*_merged` dari `Process All`, yang
untuk field-field baru ini belum diproduksi.

Sudah diamankan: ekspresinya jatuh ke nilai lama (`Resolve User Row`), **bukan** ke string kosong —
jadi tidak akan menimpa data yang sudah ada dengan kosong. Efeknya kolom-kolom itu tetap kosong
sampai `Process All` diperbarui.

### 3. Daily Cap Guard belum ada
Rem biaya yang aktif saat ini tinggal `Rate Limiter LID` (5 pesan/menit/nomor).
`daily_message_cap` dan `daily_vision_cap` sudah ada di CONFIG tapi belum dibaca node manapun.
**Sampai ini dibangun, pengaman biaya yang sesungguhnya adalah spend limit di Anthropic Console.**
Set itu dulu — lihat checklist bagian F.

### 4. Vision masih memakai `source.type: "url"`
Perbaikan download→base64 belum diterapkan. Artinya kemampuan baca gambar bergantung pada
apakah Anthropic bisa mengunduh URL Kirimi secara langsung — dan itu **belum pernah diverifikasi
dengan data live**. Uji E5 di checklist akan langsung menjawabnya.

### 5. Referensi mati bawaan Persada
- `FAQ Retrieve` memanggil `$('Read LINGKUNGAN Data')` — node itu **tidak ada** di workflow.
  Sudah begitu sejak V2.1 Persada. Kemungkinan besar tertangkap `try/catch`, tapi perlu dicek.
- Masih ada referensi `pending_survey`, `unit_interest`, `survey_status`, `flag_survey` di dalam
  `jsCode` beberapa node. Semuanya kode mati — kolomnya sudah tidak ditulis lagi — tapi bikin
  bingung saat dibaca orang.

---

## Urutan pengerjaan yang kusarankan

1. `[DECK_REQUEST]` + rantai REQUESTS + notifikasi ← **tanpa ini bot tidak menghasilkan lead**
2. Update `[FACTS]` di `Process All` untuk field baru
3. Daily Cap Guard
4. Vision base64
5. Bersih-bersih kode mati

Nomor 1 dan 2 sama-sama menyentuh `Process All`, jadi paling efisien dikerjakan sekaligus.
