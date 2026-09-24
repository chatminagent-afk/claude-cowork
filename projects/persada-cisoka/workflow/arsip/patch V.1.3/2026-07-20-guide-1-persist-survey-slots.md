# Guide Register #1 — Persist Slot Survey (`pending_survey_*`) di STATS

Basis: **VIRA-PCR Main V1.2**. Prinsip: kepemilikan slot pindah dari memory LLM ke sistem — slot disodorkan ke AI tiap giliran lewat `[SYSTEM_DATA]`, AI tinggal menyebut ulang di tag.

> **Deviasi kecil dari plan register (disengaja, lebih aman):** node `Preprocess - Context Detection` TIDAK disentuh. Plan lama menyuruh Preprocess re-parse teks `PENDING_SURVEY` dari fullMessage; tidak perlu — `Process All` membaca nilai terstruktur langsung dari `$('Cek_user_status')`, persis pola `nama_lengkap_db` yang sudah ada. Node berubah: 4 (bukan 5) + prompt. AI tetap tahu slot tersimpan karena baris `PENDING_SURVEY` ada di `[SYSTEM_DATA]` yang dia baca langsung.

**Urutan pengerjaan WAJIB seperti di bawah** (kolom sheet dulu — node Google Sheets gagal kalau mapping menunjuk kolom yang belum ada).

---

## Step 0 — Google Sheets live, tab STATS

Tambah 4 kolom di PALING KANAN (setelah `domisili_ts`), nama persis:

```
pending_survey_tanggal | pending_survey_jam | pending_survey_unit | pending_survey_ts
```

Tanpa spasi ekstra, huruf kecil semua.

## Step 1 — Node `Resolve User Row`

Ganti seluruh isi jsCode dengan file: **`2026-07-20-code-1-Resolve-User-Row.js`**
(Perubahan: 4 field `pending_survey_*` ikut dibaca dari row STATS, di bawah `domisili_ts`.)

## Step 2 — Node `Cek_user_status`

Ganti seluruh isi jsCode dengan file: **`2026-07-20-code-1-Cek_user_status.js`**
Perubahan:
- Blok baru `PENDING SURVEY` (setelah blok PROFIL USER): baca slot dari `debounceRow`/`resolve`, **TTL 48 jam** — slot lebih tua dianggap hangus dan tidak diteruskan ke mana pun (otomatis bersih di giliran berikutnya).
- Baris baru di `[SYSTEM_DATA]` (di bawah `BUDGET_RANGE`): `PENDING_SURVEY: tanggal=... | jam=... | unit=...` atau `-` kalau kosong.
- Return membawa `pending_survey_tanggal_db` / `_jam_db` / `_unit_db` (sudah lolos TTL) untuk dibaca Process All.

## Step 3 — Node `Process All`

Ganti seluruh isi jsCode dengan file: **`2026-07-20-code-1-Process-All.js`**
Perubahan (3 titik):
1. Setelah blok merge unit/budget: baca `pendingSv` dari `$('Cek_user_status')` (try/catch, default kosong).
2. Di awal gate `if (svTagFound)`: backfill — `svTgl`/`svJam`/`svUnit` yang kosong diisi dari `pendingSv` (**tag AI menang, pending cadangan**). Semua logika downstream (missingSlots, validasi, pesan reject) otomatis memakai nilai hasil backfill.
3. Sebelum return: hitung `surveyPendingWrite` — survey **sukses tercatat → dikosongkan semua**; selain itu slot terbaru dibawa maju dengan `ts` sekarang. Field masuk ke return object.

## Step 4 — Node `Update to STATS`

Buka node, di bagian mapping kolom klik refresh/`Add Column` (kolom baru muncul setelah Step 0), lalu isi 4 mapping baru:

```
pending_survey_tanggal = {{ $('Process All').first().json.surveyPendingWrite.tanggal }}
pending_survey_jam     = {{ $('Process All').first().json.surveyPendingWrite.jam }}
pending_survey_unit    = {{ $('Process All').first().json.surveyPendingWrite.unit }}
pending_survey_ts      = {{ $('Process All').first().json.surveyPendingWrite.ts }}
```

## Step 5 — Node `AI Agent` (system prompt)

Di blok `# SURVEY`, tambah 1 bullet (mis. setelah bullet "Slot belum lengkap ..."):

```
- PENDING_SURVEY di [SYSTEM_DATA] adalah slot yang SUDAH dikonfirmasi user di giliran sebelumnya. Anggap benar, JANGAN tanya ulang slot itu, dan sertakan lagi nilainya saat memasang [SCHEDULE_SURVEY]. Tanda "-" artinya belum ada.
```

---

## Verifikasi (wajib, `Update to STATS` jalan di SETIAP pesan)

1. **Alur 3 giliran**: "mau survey dong" → "senin aja" → "jam 10 pagi bs". Cek tab STATS: kolom pending terisi bertahap tiap giliran, lalu **kosong lagi** begitu baris SURVEY berhasil tertulis.
2. **Chat non-survey biasa** ("harga 36/72 berapa?"): reply normal, kolom pending tetap kosong, kolom STATS lain tetap terisi benar.
3. **TTL**: isi manual `pending_survey_ts` dengan epoch 3 hari lalu → chat lagi → `[SYSTEM_DATA]` harus menunjukkan `PENDING_SURVEY: -` dan kolom terhapus/terganti di giliran itu.
4. Cek execution log: tidak ada error `column not found` di `Update to STATS`.

## Catatan perilaku

- `ts` di-refresh tiap giliran selama percakapan aktif — TTL 48 jam efektif = "48 jam sejak interaksi terakhir yang membawa slot", itu memang yang diinginkan.
- STATS selalu menang atas ingatan LLM hanya dalam arti *cadangan*: kalau AI menyebut slot baru di tag, nilai tag yang dipakai dan yang dipersist.
- File kode dibangun dari export V1.2 dengan insersi ter-verifikasi (anchor unik + syntax check) — bukan tulis ulang manual.
