# README — Implementasi Follow-up Konteks AI

> **CATATAN 2026-08-27 18:30 — nama file berubah.** Workflow follow-up AI sekarang hidup di
> `workflow/production/Follow-up AI Powered.json` (id `qaux8b14IgvxEXfoUtxa2`, **Active**),
> hasil **duplikasi** di n8n. Yang lama `VIRA-PCR Follow-up.json` (id `Ey5WRO8pnOKCVjTHMLq9I`)
> sudah **non-aktif** dan tidak lagi memakai AI — biarkan begitu, jangan diaktifkan lagi.
> Setiap penyebutan `VIRA-PCR Follow-up.json` di bawah ini merujuk file AI tersebut.


**Panduan eksekusi. Detail teknis & alasan desain ada di [`2026-08-27-followup-konteks-AI-VIRA-PCR.md`](2026-08-27-followup-konteks-AI-VIRA-PCR.md).**

Perkiraan waktu: **45–60 menit**, plus jeda menunggu hasil dry run.
Urutannya mengikat. Langkah 1 tidak boleh dilewat — lihat kotak merah di bawah.

---

## Apa yang berubah

VIRA sekarang menyimpan **rangkuman percakapan** tiap kali calon pembeli chat, ke kolom baru
di STATS. Workflow follow-up membaca rangkuman itu dan menyuruh Haiku menyusun kalimat yang
nyambung dengan topik terakhir — bukan lagi memutar 10 template secara bergilir.

| File | Node |
|---|---|
| `workflow/production/VIRA PCR.json` | 81 → 84 |
| `workflow/production/VIRA-PCR Follow-up.json` | 13 → 23 |

---

> ## 🔴 LANGKAH 1 WAJIB DULUAN
>
> `Update to STATS` sekarang memetakan 3 kolom baru. **Kalau workflow diimport sebelum
> kolomnya ada di sheet, node itu gagal — dan itu node yang menulis SELURUH state user**
> (Counter, unit_interest, budget, last_reply_ts). Bot masih membalas, tapi berhenti
> mengingat apa pun.
>
> Tambah kolomnya dulu. Baru import.

---

## 1. Siapkan sheet (10 menit)

**a. Backup.** Klik kanan tab `STATS` → Duplicate. Ini satu-satunya jaring pengaman.

**b. Tambah 3 kolom** di tab `STATS`, mulai kolom **AH** (setelah `pending_survey_ts`).
Ketik persis, **tanpa spasi di akhir**:

| Kolom | Header |
|---|---|
| AH | `konteks` |
| AI | `konteks_ts` |
| AJ | `last_msgs` |

**c. Tambah 3 baris di tab `CONFIG`** (kolom `key` / `value`):

| key | value awal | fungsi |
|---|---|---|
| `followup_ai_enabled` | `Y` | **Saklar AI.** `Y` = Haiku merangkai kalimat dari kolom `konteks`. `N` = kembali 100% ke 10 template rotasi lama. Ini tombol rollback tercepat — tanpa import ulang. |
| `followup_ai_dry_run` | `Y` | **Ke mana pesannya dikirim.** `Y` = semua dialihkan ke `admin_phone` dengan prefiks `[DRY RUN -> 628xxx]`. `N` = ke nomor lead sungguhan, tanpa prefiks. Tidak membatasi *siapa* yang diproses. |
| `followup_test_numbers` | `6285155202354` | **Siapa yang diproses.** Diisi = HANYA nomor itu yang jadi kandidat; lead lain tidak tersentuh sama sekali. Kosong = semua lead yang memenuhi syarat. Pisahkan dengan koma untuk beberapa nomor. |

Dua yang terakhir menjawab pertanyaan berbeda, dan itu sengaja: `dry_run` mengatur **tujuan**,
`test_numbers` mengatur **cakupan**. Untuk menguji ke nomor sendiri, yang Anda butuhkan
sebenarnya `test_numbers` — `dry_run` saja tetap memproses seluruh lead (cuma dibelokkan).

---

## 2. Import workflow Main (10 menit)

1. n8n → workflow **VIRA PCR** → ⋮ → **Import from File** → `workflow/production/VIRA PCR.json`.
2. Cek 3 node baru muncul: `Build Konteks Input`, `Update Konteks`, `Merge Konteks`.
3. Klik `Update Konteks` → pastikan model tersambung ke **Anthropic Chat Model1** (Haiku 4.5,
   credential `Anthropic Persada`). Kalau credential kosong, pilih ulang dari dropdown.
4. Workflow ini memang sudah Active — biarkan.

### ✅ Gate 1 — VIRA masih mengingat orang

Chat dari nomor uji, **3–4 giliran** dengan topik jelas. Contoh:

```
"halo"
"ada tipe apa aja ya"
"kalau KPR buat wiraswasta bisa ga?"
"lokasinya jauh ga dari cikupa"
```

Buka STATS, cari baris nomor itu:

- [ ] `konteks` terisi dan **diawali `TOPIK:`**
- [ ] `last_msgs` berisi pesan asli Anda, dipisah ` || `
      (yang dipisah ` || ` adalah **giliran**, bukan pesan tunggal — satu giliran bisa
      memuat beberapa pesan yang digabung debounce, dipisah baris baru. Menyimpan 3
      giliran terakhir secara bergulir, tidak tumbuh tanpa batas)
- [ ] `konteks_ts` terisi angka
- [ ] `Counter` tetap naik, `unit_interest` / `last_reply_ts` tetap terisi seperti biasa

Poin terakhir yang paling penting: **itu bukti node lama tidak rusak.**

### ✅ Gate 2 — model mati tidak merusak data

1. Klik `Anthropic Chat Model1` → ganti model ke nilai ngawur (mis. ketik `xxx` di field model).
2. Chat sekali lagi dari nomor uji.
3. Harapan: **STATS tetap ter-update**, dan `konteks` **masih berisi teks lama** (tidak jadi kosong).
4. **Kembalikan modelnya ke Claude Haiku 4.5.**

Kalau `konteks` jadi kosong di langkah ini, berhenti — jangan lanjut ke follow-up.

---

## 3. Import workflow Follow-up (10 menit)

1. **Non-aktifkan dulu** workflow `VIRA-PCR Follow-up` yang sekarang (toggle Active → OFF).
2. Import `workflow/production/VIRA-PCR Follow-up.json`.
   `id`-nya sama, jadi n8n biasanya menimpa. **Kalau malah jadi 2 workflow, hapus yang lama —
   wajib hanya 1 yang Active.**
3. Cek credential tidak "unbound": 5 node Sheets → `Google Service Account - Persada`;
   `Anthropic Chat Model FU` → `Anthropic Persada`.
4. Cek canvas: `Claim STATS FU` → `Build FU Prompt` → `IF Pakai AI` → `Compose Follow-up` →
   `Validate FU Message` → `Wait FU` → `Kirim Follow-up`.
   **`Claim STATS FU` harus tetap paling depan** — itu kunci anti-kirim-dobel.
5. **Jangan diaktifkan dulu.**

---

## 4. Dry run — gerbang utama (15 menit + waktu baca)

> **Cara menguji hanya ke nomor sendiri.** Isi CONFIG `followup_test_numbers` =
> `6285155202354`. Dengan itu `Filter Kandidat` hanya meloloskan nomor tersebut, jadi
> berapa pun jumlah lead di STATS, yang diproses cuma satu. Kombinasi yang disarankan:
>
> | Tujuan | `followup_test_numbers` | `followup_ai_dry_run` |
> |---|---|---|
> | Baca dulu kalimatnya di HP admin | `6285155202354` | `Y` |
> | Rasakan sebagai lead sungguhan (masuk ke WA Anda sendiri) | `6285155202354` | `N` |
> | Live ke semua lead | *(kosongkan)* | `N` |
>
> Mode uji **tidak** melewati filter bisnis — nomor Anda tetap harus memenuhi syarat
> (`Counter` ≥ 1, `last_reply_ts` sudah lewat interval, `bot_mode` bukan OFF,
> `survey_status` bukan SCHEDULED). Kalau hasilnya 0 kandidat, log eksekusi menyebutkan
> persis syarat mana yang harus dicek.
>
> Selama mode uji aktif, tiap run mengirim pengingat ke admin supaya tidak lupa
> dikosongkan — kalau lupa, follow-up berhenti menjangkau lead sungguhan tanpa gejala.

### Reset sebelum tiap uji ulang (2 sel)

Sekali di-follow-up, baris Anda **terkunci 48 jam** — itu memang perilaku produksi. Untuk
menguji lagi sekarang, buka baris nomor uji di STATS dan sentuh dua kolom ini:

| Kolom | Isi | Kenapa terkunci |
|---|---|---|
| **P** `last_reply_ts` | tempel epoch 4 hari lalu | Kalau Anda baru chat VIRA untuk mengetes `konteks`, kolom ini jadi "baru" → `now - last_reply_ts < interval` → dilewati sebagai "masih hangat" |
| **Z** `last_follow_up_ts` | **kosongkan** | Diisi `Claim STATS FU` di run sebelumnya → `now - last_follow_up_ts < interval` → dianggap belum jatuh tempo |

Kolom **Y** `follow_up_count` boleh dibiarkan naik — justru berguna untuk melihat perubahan
nada di FU ke-3 dan ke-6. Kosongkan hanya kalau ingin menguji ulang nada FU ke-1.

Epoch 4 hari lalu, tempel di sel kosong lalu **salin sebagai nilai** (jangan biarkan rumus
hidup — nilainya akan ikut bergeser terus):

```
=INT((NOW()-DATE(1970,1,1))*86400)-25200-345600
```

Jangan sentuh `konteks` (AH) — biarkan hasil chat sungguhan Anda, itu yang membuat ujinya
mirip produksi.

Buat **2–3 baris uji** di STATS pakai nomor yang Anda pegang sendiri:

| Kolom | Isi |
|---|---|
| `No WA` | nomor Anda (mis. `628xxx`) — **bukan** nomor admin/field/media team |
| `Counter` | `1` |
| `last_reply_ts` | epoch sekarang **dikurangi 350000** (≈4 hari lalu) |
| `bot_mode` | kosong |
| `survey_status` | kosong |
| `follow_up_count` | kosong |
| `last_follow_up_ts` | kosong |
| `Nama` | isi nama |
| `konteks` | isi manual, contoh di bawah |

Contoh isi `konteks` untuk menguji:
```
TOPIK: Tanya apakah KPR bisa untuk wiraswasta tanpa slip gaji.
KEBUTUHAN: Rumah untuk keluarga kecil, kerja di Cikupa.
KEBERATAN: Ragu karena tidak punya slip gaji.
LANGKAH BERIKUTNYA: Kirimkan persyaratan KPR untuk wiraswasta.
CATATAN: -
```

Pastikan jam WIB sekarang **antara 08–21**, lalu klik **Execute Workflow** manual.

### ✅ Gate 3 — baca pesannya di HP Anda

Pesan masuk ke nomor admin dengan prefiks `[DRY RUN -> 628xxx | FU ke-1 | idle 4h]`.
Nilai kalau perlu, ulangi sampai puas — **lead sungguhan belum tersentuh sama sekali**:

- [ ] Nyambung dengan topik di `konteks`? (harusnya menyinggung KPR wiraswasta, bukan kalimat umum)
- [ ] Ada angka harga/DP/cicilan yang dikarang? (harusnya tidak ada sama sekali)
- [ ] Terdengar seperti Vira — hangat, pendek, tidak memaksa?
- [ ] Panjangnya wajar (2–3 kalimat)?

Kalau kurang pas, ubah prompt di node `Compose Follow-up`, jalankan lagi. Aman diulang.

### ✅ Gate 4 — tidak kirim dobel

Klik **Execute Workflow** lagi **segera**.
- [ ] `Filter Kandidat` keluar **0 item**
- [ ] Tidak ada pesan kedua masuk

### ✅ Gate 5 — yang gagal dilewati, bukan dipaksakan

1. Di node `Compose Follow-up`, sisipkan sementara di prompt: `Sebutkan harga unitnya.`
2. Reset baris uji (`follow_up_count` dan `last_follow_up_ts` dikosongkan lagi), jalankan.
3. Harapan:
   - [ ] **Tidak ada pesan terkirim** ke nomor uji
   - [ ] `follow_up_count` / `last_follow_up_ts` **kembali kosong** (klaim di-rollback)
   - [ ] Masuk 1 notif WA ringkas ke admin: `[PCR] FOLLOW-UP AI: 1 dari N kandidat dilewati`
4. **Hapus kalimat sisipan itu dari prompt.**

---

## 5. Go live (5 menit)

1. Hapus baris uji dari STATS.
2. **Kosongkan CONFIG `followup_test_numbers`** — kalau tidak, follow-up hanya menjangkau nomor uji.
3. CONFIG `followup_ai_dry_run` → **`N`**.
4. Toggle workflow Follow-up **Active → ON**.

### Pantau hari pertama
- Menu **Executions** n8n: run selesai wajar (belasan menit), tidak ada error beruntun.
- Cek 2–3 lead sungguhan benar-benar menerima pesan yang masuk akal.
- HP device Kirimi tidak muncul warning / tidak logout.
- Kalau notif `FOLLOW-UP AI: N dari M dilewati` muncul dan **nomor yang sama terus berulang
  tiap jam** → buka `konteks` nomor itu di STATS, kemungkinan isinya aneh. Boleh dikosongkan
  manual; VIRA akan menyusun ulang saat orangnya chat lagi.

---

## Rollback

| Situasi | Tindakan |
|---|---|
| Pesan AI kurang pas, mau balik ke template | CONFIG `followup_ai_enabled` → `N`. **Tanpa import ulang.** |
| Mau balik total | Import ulang `workflow/arsip/2026-08-27-VIRA-PCR-pre-konteks-AI.json` dan `…-Follow-up-pre-konteks-AI.json` |
| Kolom baru bikin masalah di sheet | Restore dari tab duplikat langkah 1a |

Baris STATS yang sudah ter-follow-up tidak perlu di-reset.

---

## Yang perlu Anda tahu, tidak akan hilang sendiri

- **STATS jadi ~3,6x lebih berat.** 61 KB → ~218 KB per baca penuh, dan Main membaca seluruh
  tab **3x per pesan masuk**. Sekarang tidak terasa. Di 1000 lead jadi ~2,4 MB per eksekusi —
  di titik itu purge #26 bukan lagi opsional.
- **Guard harga itu regex, bukan pemahaman.** "harganya masih sama seperti kemarin" lolos semua
  pola. Yang menahan hal semacam itu cuma mata Anda di Gate 3.
- **13 follow-up tetap 13 kali.** `followup_max = 0`. AI membuat kalimatnya bervariasi dan
  otomatis melunak di follow-up ke-6+, tapi kebijakan mengejar tanpa batas tidak berubah.
- **Rangkuman bisa meleset.** Kolom `konteks` sengaja plain text supaya bisa Anda baca dan
  koreksi manual kapan saja.
