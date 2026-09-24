# Panduan deploy — v3.11 + Follow-up v2 (2026-09-22)

Apa yang berubah: VIRA jadi tahu decknya sudah terkirim dan apa isinya, bisa mengarahkan ke
Steven kalau prospek mau diskusi, dan ada follow-up yang kalimatnya berbeda tergantung sejauh
mana prospek melangkah.

Dua bagian yang **bisa dipisah**. Bagian A boleh dipasang hari ini dan langsung dipakai.
Bagian B (follow-up) sengaja dikirim dalam keadaan mati — nyalakan kapan pun kamu siap.

Sudah lolos sebelum sampai di sini:

| Pemeriksaan | Hasil |
|---|---|
| UAT perilaku v3.11 (`_uat_2026-09-22.py`) | **551 lolos / 0 gagal** — 491 di antaranya uji lama yang jalan ulang sebagai regresi |
| UAT follow-up (`_uat_followup_2026-09-22.py`) | **204 lolos / 0 gagal** |
| Uji konsistensi deck (`uji_konsistensi.py`) | **87 lolos / 0 gagal** |
| Bedah regresi v3.11 vs v3.10 | 86 node identik byte per byte, koneksi identik, tidak ada satu baris pun kode lama yang hilang |

---

## A. v3.11 — VIRA tahu decknya terkirim

### A1. Tambah kolom di STATS

Buka tab **STATS**, tambahkan satu kolom di **paling kanan** (jadi kolom ke-33):

```
deck_terkirim_ts
```

Isinya epoch detik, diisi otomatis oleh `kirim_deck.py`. Kosong = deck belum dikirim.

> **Taruh di paling kanan, jangan disisipkan di tengah.** Node n8n memetakan kolom berdasarkan
> nama, jadi kolom baru di ujung tidak mengganggu apa pun. Menyisipkan di tengah bisa menggeser
> cache skema node-node lama.
>
> Namanya sengaja beda dari `REQUESTS.deck_dikirim_ts`. Yang di REQUESTS berformat teks WIB
> (catatan untuk kamu); yang di STATS epoch (dibaca mesin), mengikuti konvensi semua kolom
> `*_ts` lain di tab itu.

### A2. Import workflow

1. Import `workflow/2026-09-22-VIRA-Personal-Main-v3.11.json`
2. Pasang lagi credential-nya (import n8n tidak membawa credential)
3. **Nonaktifkan v3.10 dulu**, baru aktifkan v3.11 — jangan dua-duanya hidup, path webhook-nya sama

Tidak ada node baru, tidak ada kabel yang berubah. Cuma 3 node yang isinya diperbarui:
`Rakit Konteks`, `AI Agent`, `Process All`.

### A3. Skrip deck sudah diperbarui, tidak perlu kamu apa-apakan

Sudah dikerjakan di `VIRA Steven/deck/`:

- `vira_sheet.py` — fungsi baru `cari_stats()` (No WA dulu, `lid` cadangan, error kalau tidak
  ketemu — tidak pernah jatuh ke baris pertama)
- `kirim_deck.py` — menulis `STATS.deck_terkirim_ts` sesudah kiriman ke klien berhasil
- `caption-deck.txt` — isinya sekarang caption serah-terima (minta review → Basic/Premium →
  tawaran diskusi). Isi lama disimpan di `caption-deck.txt.lama-2026-09-22`
- perbaikan cacat: `susun_caption()` dulu menyisipkan karakter kontrol U+0001 ke caption saat
  kolom `nama` kosong, dan menghapus tanda bacanya. Sekarang `"Halo kak, ..."` seperti seharusnya

**Kalau caption diubah lagi nanti**, perbarui juga blok `deck_context` di node `Rakit Konteks` —
di situlah VIRA membaca apa yang kamu minta di pesan pengantar.

### A4. Uji sebelum dipakai ke prospek asli

```bash
cd "D:\Documents\Claude Cowork\VIRA\VIRA Steven\deck" && python vira_sheet.py 628xxxxxxxxxx
```

1. Isi manual `deck_terkirim_ts` satu nomor uji dengan epoch kemarin → di n8n, Execute node
   `Rakit Konteks` untuk baris itu → `deck_context` harus terbentuk. Untuk nomor lain harus
   berbunyi `(deck belum pernah dikirim ke orang ini)`.
2. `python kirim_deck.py --wa <uji> --ke-admin --kirim` → **STATS tidak boleh berubah**
   (itu kiriman review ke kamu, bukan ke klien).
3. `python kirim_deck.py --wa <nomor kamu sendiri> --kirim` → keluarannya memuat
   `SHEET : STATS.deck_terkirim_ts = <epoch>`, dan kolomnya benar-benar terisi **di baris yang benar**.
4. Chat dari nomor itu → VIRA **tidak boleh lagi** bilang decknya sedang disusun atau briefnya
   baru diteruskan. Dia harus bisa menyebut isi decknya garis besar.
5. Tanya `"basic sama premium bedanya apa?"` → boleh menyebut kisaran dan mengarahkan angka final
   ke kamu. **Harga add-on tetap tidak boleh disebut.**
6. Pancing VIRA menawarkan ngobrol langsung, balas `"boleh"` → notif handover masuk dan berbunyi
   **"VIRA sudah BERHENTI membalas"**, `STATS.bot_mode` jadi `OFF`.
7. Kontrolnya: di nomor lain, balas `"boleh"` atas tawaran **deck** → `bot_mode` harus tetap `ON`.

### A5. Kalau harus mundur

Nonaktifkan v3.11, aktifkan lagi v3.10. Kolom `deck_terkirim_ts` dan tulisan Python-nya tidak
mengganggu v3.10 — node lama tidak membacanya.

---

## B. Follow-up v2 — nyalakan kapan kamu siap

Dikirim **mati**: `active: false` dan `Schedule Trigger FU` disabled. Tidak akan jalan sendiri.

### B1. Isi CONFIG

Yang **diubah**:

| key | dari | jadi | kenapa |
|---|---|---|---|
| `followup_max` | `2` | `0` | semantiknya dibalik: **0 = tanpa batas**. Versi lama membuat `0` berarti nol orang di-follow-up — gagal diam. Batas sebenarnya sekarang per bucket. |
| `followup_interval_hours` | `24` | `48` | default global; per bucket menimpa |
| `followup_templates` | ada `{nama}` | hapus `{nama}` | melanggar aturan "selalu kak". Kode membuangnya paksa, tapi sheet jangan menyimpan pola yang salah |

Yang **baru**:

| key | nilai |
|---|---|
| `followup_ai_enabled` | `Y` |
| `followup_ai_dry_run` | `Y` ← biarkan Y sampai kamu puas baca hasilnya |
| `followup_test_numbers` | nomor kamu sendiri selama uji, lalu **kosongkan** |
| `followup_interval_hours_a` | `72` |
| `followup_interval_hours_c` | `48` |
| `followup_max_a` | `3` |
| `followup_max_c` | `3` |
| `followup_min_delay_sec` | `20` |
| `followup_max_delay_sec` | `45` |
| `followup_max_per_run` | `20` |
| `followup_backlog_hour` | `9` |
| `followup_backlog_days` | `3` |
| `followup_templates_a` | lihat bawah |
| `followup_templates_c` | lihat bawah |

`followup_templates_a` (prospek belum sampai tahap deck):
```json
["Halo kak, kita sempat bahas soal chat yang masuk ke usaha kakak. Masih ada yang mau ditanyain soal gimana AI bantu di bagian itu?","Hai kak, aku masih di sini kalau mau lanjut ngobrol soal chat yang numpuk itu. Mau aku ceritain contoh sistemnya jalan di bisnis lain?","Halo kak, kalau mau, aku bisa mintakan Steven buatkan deck khusus buat bisnis kakak. Tinggal bilang di sini aja ya."]
```

`followup_templates_c` (decknya sudah di tangan dia):
```json
["Halo kak, decknya sempat kebaca belum? Kalau ada bagian yang mau dibahas, aku bisa jelasin di sini.","Hai kak, antara Basic sama Premium, kira-kira yang mana yang lebih mendekati kebutuhan usaha kakak?","Halo kak, kalau lebih enak dibahas langsung sama Steven, bilang aja di sini ya. Nanti aku sambungkan."]
```

Template ini cuma jaring pengaman — dipakai kalau AI mati atau kalimat AI ditolak guard.
Normalnya AI yang menulis, bersandar pada `masalah_utama`, `industri`, dan `nama_bisnis` di STATS.

### B2. Import

1. Import `workflow/2026-09-22-VIRA-Personal-Followup-v2.json`
2. Pasang credential: **5 node Google Sheets** (service account) + **`DeepSeek FU`**
3. `followup_enabled = true` di CONFIG

### Tiga saklar yang berbeda — baca ini dulu

| Saklar | Mengatur apa |
|---|---|
| Toggle **Active** workflow (kanan atas) | apakah jadwalnya berdenyut **sendiri** tiap jam |
| Node `Schedule Trigger FU` enabled/disabled | apakah workflow bisa **dijalankan sama sekali**, termasuk manual |
| CONFIG `followup_enabled` | kill switch di dalam kode, berlaku siklus berikutnya |

Yang menahan follow-up jalan sendiri adalah **toggle Active**, bukan node trigger-nya.
Node trigger dikirim disabled cuma sebagai lapis kedua: kalau toggle Active kepencet tidak
sengaja, tetap tidak ada yang terkirim.

Konsekuensinya: **selama node trigger disabled, tombol Execute workflow tidak bisa dipakai** —
eksekusi manual pun berangkat dari trigger.

### B3. Uji kering

1. Buka workflow, klik kanan node `Schedule Trigger FU` → **Activate**
   (atau pilih node-nya lalu tekan `D`).
2. **Toggle Active workflow biarkan OFF.** Selama OFF, jadwalnya tidak pernah jalan sendiri —
   kamu yang memicu tiap kali.
3. Klik **Execute workflow**.

- Semua pesan harus mendarat di **WA kamu**, berawalan `[DRY RUN -> 628xxx | bucket A | ...]`.
  Tidak boleh ada satu pun yang sampai ke prospek.
- Baca kalimat bucket A dan C: tidak ada nama prospek, tidak ada angka harga, tidak ada janji
  tanggal, maksimal 3 kalimat.
- Cek STATS: `follow_up_count` naik 1, `last_follow_up_ts` terisi.
- **Uji rollback**: isi `kirimi_device_id` dengan nilai salah, jalankan lagi. `follow_up_count`
  harus **kembali** ke nilai semula, dan laporan run menyebut `FU_KIRIM_GAGAL`.
- **Uji backlog**: set `followup_backlog_hour` ke jam berjalan, pastikan ada baris
  `deck_requested=Y` tanpa `deck_terkirim_ts`. WA `BRIEF DECK MENGGANTUNG` harus masuk ke kamu.

### B4. Buka ke production

Baru setelah B3 beres. Enam hal, tidak ada yang lain:

| Di mana | Edit |
|---|---|
| CONFIG | `followup_test_numbers` → **kosongkan** |
| CONFIG | `followup_ai_dry_run` → **`N`** |
| CONFIG | `followup_interval_hours_c` → **`48`** (kalau sempat diturunkan ke `6` buat uji) |
| n8n Follow-up | node `Schedule Trigger FU` harus **enabled** — workflow tidak bisa diaktifkan tanpa trigger hidup |
| n8n Follow-up | nyalakan **toggle Active** |
| n8n Main | pastikan **v3.11 aktif**, v3.10 mati |

Hari pertama: pantau satu siklus penuh dan baca laporan run yang masuk.

Mundur sewaktu-waktu: `followup_enabled = false` di CONFIG. Berlaku siklus berikutnya,
tanpa menyentuh n8n.

Tiga tingkat mematikan, dari yang paling ringan:

- `followup_enabled = false` di CONFIG — berlaku siklus berikutnya, tanpa menyentuh n8n
- matikan **toggle Active** workflow — jadwalnya berhenti, tapi masih bisa kamu jalankan manual
- disable node `Schedule Trigger FU` — tidak bisa jalan sama sekali, bahkan manual

---

## Cara kerjanya, singkat

**Tiga bucket, ditentukan dari kolom — bukan tebakan AI:**

| Bucket | Syarat | Yang terjadi |
|---|---|---|
| **A** | `deck_requested` ≠ Y | buka lagi pelan, gali satu hal, boleh tawarkan deck sekali |
| **B** | `deck_requested`=Y, `deck_terkirim_ts` kosong | **prospeknya tidak dikirimi apa pun** — kamu yang ditegur lewat WA `BRIEF DECK MENGGANTUNG` |
| **C** | `deck_terkirim_ts` terisi | sempat dibaca belum / Basic atau Premium / tawarkan diskusi — pilih satu |

Bucket C juga tahu bedanya prospek yang diam total sejak deck datang dan yang sempat menanggapi
lalu hilang.

**Follow-up ikut mengisi `last_bot_reply`** (node `Catat Balasan FU`, hanya kalau bukan dry run).
Ini bukan sekadar supaya VIRA ingat kalimatnya sendiri: `Process All` membaca kolom itu untuk
dua gerbang persetujuan — `TAWARAN_DECK` dan `TAWARAN_DISKUSI`. Tanpa ini, prospek yang membalas
**"boleh"** atas tawaran di follow-up tidak memicu apa pun: brief tidak tercatat, handover tidak
jalan. `last_reply_ts` sengaja tidak disentuh, karena itu acuan jam diam di `Filter Kandidat`.

**Yang dijaga kode, bukan prompt.** Prompt boleh melarang; yang menjamin adalah `Validate FU
Message`. Dia menolak: angka harga (ditulis digit maupun huruf), `999` (add-on), URL, nomor
telepon, **menyapa pakai nama**, janji tanggal, dan klaim "sudah aku cek/kirim". Klaim "deck
sudah dikirim" dimaafkan khusus di bucket C — di situ memang benar.

Ditolak → **pakai template bucket itu**, bukan dilewati. Tanpa itu, prospek yang datanya selalu
memicu guard akan macet selamanya (persis bug Persada 16 Sept).

---

## Yang belum ada, supaya kamu tahu

- **Tidak ada opt-out.** Prospek yang mengetik "stop" tidak otomatis berhenti di-follow-up.
  Jalan keluarnya tetap `bot_mode = OFF` manual.
- **Tidak ada tanda sudah closing.** Kalau kamu closing lewat telepon dan lupa set
  `bot_mode = OFF`, bucket C akan terus menanyakan Basic/Premium ke orang yang sudah bayar,
  sampai `followup_max_c` habis. Perbaikan permanennya kolom status baru.
- **`deck_terkirim_ts` cuma mencatat Kirimi menerima file.** Terkirim ≠ terbaca.
- **Dashboard belum menampilkan `deck_terkirim_ts`** sampai ditambahkan ke `tenants.js`.
