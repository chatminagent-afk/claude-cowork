# Changes: "Domisili" → "Lokasi Kerja" — VIRA-PCR Main V1.2

**Tanggal:** 2026-07-23
**Sumber:** `workflow/production/VIRA-PCR Main V1.2.json` (download terbaru)
**Requested by:** Owner (Om Sulianto) — intro ganti tanya "domisili" jadi "lokasi kerja", termasuk kolom sheet.
**Eksekutor:** Steven (manual)

---

## 0. Hasil target (intro yang diinginkan)

> Haloo, terima kasih sudah menghubungi Persada Cisoka Residence yaa. Saya Vira, siap bantu info seputar unit, harga, dan syarat KPR. Oh iya, boleh sekalian saya catat, ini dengan Kak siapa dan **lokasi kerjanya di mana** yaa? 😊

---

## 1. Keputusan penamaan (WAJIB konsisten)

| Konteks | Lama | Baru |
|---|---|---|
| Kolom sheet STATS | `domisili` / `domisili_ts` | `lokasi_kerja` / `lokasi_kerja_ts` |
| Label di [SYSTEM_DATA] | `DOMISILI:` | `LOKASI_KERJA:` |
| Atribut tag [FACTS] | `domisili="..."` | `lokasi_kerja="..."` |
| Token askProfileTarget | `'domisili'`, `'nama+domisili'` | `'lokasi_kerja'`, `'nama+lokasi_kerja'` |
| Teks ke user | "domisili" / "domisilinya" | "lokasi kerja" / "lokasi kerjanya" |
| Variabel JS internal | `factDomisili`, `domisiliMerged`, dst | opsional rename (lihat §4) |

⚠️ **JANGAN pakai token `lokasi` saja.** Sudah ada konsep lain di workflow: variabel `askingLokasi` dan kategori FAQ `Lokasi` (= lokasi fisik proyek). Selalu pakai token penuh `lokasi_kerja` biar tidak tabrakan.

⚠️ **Aturan kontrak n8n:** 3 pasangan ini harus diganti BERBARENGAN atau pipeline putus diam-diam (node Google Sheets nge-*no-op* tanpa error kalau nama kolom/schema tidak cocok):
1. Header kolom sheet ↔ kode yang baca/tulis kolom itu
2. Atribut `[FACTS]` di system prompt ↔ regex di node `Process All`
3. Label `LOKASI_KERJA:` yang di-emit `Cek_user_status` ↔ yang dibaca system prompt

---

## 2. Peta dampak — 8 node + 1 sheet

Semua node di bawah ada di `VIRA-PCR Main V1.2`. Nama node ditulis persis (cari di editor n8n).

| # | Node | Tipe | Bagian yang diubah |
|---|------|------|--------------------|
| A | **STATS** (Google Sheet) | spreadsheet | header kolom AB1, AC1 |
| B | `Resolve User Row` | Code | baca kolom + 2 output key |
| C | `Cek_user_status` | Code | variabel, label SYSTEM_DATA, token askProfile, output key |
| D | `AI Agent` | LangChain Agent (systemMessage) | 12 titik teks prompt (termasuk kalimat greeting) |
| E | `Process All` | Code | regex FACTS + variabel + 2 output key |
| F | `Update to STATS` | Google Sheets (appendOrUpdate) | value mapping + schema 2 kolom |
| G | `Collect Handover Context` | Code | 2 referensi |
| H | `Summarize Handover` | LangChain chainLlm (text) | label + ekspresi |
| I | `Format Handover Message` | Code | 1 baris fallback |

---

## 3. Langkah eksekusi (URUT — jangan diacak)

### Persiapan
1. **Backup workflow:** di n8n, duplicate `VIRA-PCR Main V1.2` → simpan copy (mis. `...V1.2-backup-pre-lokasikerja`).
2. **Backup sheet:** duplicate tab `STATS` (klik kanan tab → Duplicate) sebagai `STATS_backup_20260723`.
3. **Matikan sementara (opsional tapi disarankan):** kerjakan di jam sepi. Kalau bisa, non-aktifkan workflow selama edit supaya tidak ada request masuk di tengah rename.

### STEP A — Google Sheet STATS (lakukan DULUAN sebelum edit node F)
Di spreadsheet (docId `1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o`), tab **STATS**:
- Sel **AB1**: `domisili` → `lokasi_kerja`
- Sel **AC1**: `domisili_ts` → `lokasi_kerja_ts`
- Data lama di kolom itu tetap ada (nilainya dulu = domisili). Untuk lead lama boleh dibiarkan; kalau mau bersih, kosongkan isi AB2:AC (jangan hapus header).

### STEP B — Node `Resolve User Row` (Code)
Ganti 4 baris:
```js
// LAMA
domisili: row ? String(row['domisili'] || '').trim() : '',
domisili_ts: Number(row ? (row['domisili_ts'] || 0) : 0) || 0,
// BARU
lokasi_kerja: row ? String(row['lokasi_kerja'] || '').trim() : '',
lokasi_kerja_ts: Number(row ? (row['lokasi_kerja_ts'] || 0) : 0) || 0,
```

### STEP C — Node `Cek_user_status` (Code)
Find/replace di dalam node ini (14 titik). Amannya replace-all string berikut secara berurutan:
- `debounceRow['domisili']` → `debounceRow['lokasi_kerja']`
- `resolve.domisili` → `resolve.lokasi_kerja`
- `const domisili =` → `const lokasi_kerja =`  (dan semua pemakaian variabel `domisili` di node ini → `lokasi_kerja`)
- `needDomicile` → `needLokasiKerja` (nama variabel bebas, ganti konsisten)
- `!domisili` → `!lokasi_kerja`
- Literal `'nama+domisili'` → `'nama+lokasi_kerja'`
- Literal `'domisili'` → `'lokasi_kerja'`
- Label template `` `DOMISILI: ${...}` `` → `` `LOKASI_KERJA: ${...}` ``
- Teks instruksi `'nama lengkap dan domisili'` → `'nama lengkap dan lokasi kerja'`, dan `'domisili'` (versi teks natural) → `'lokasi kerja'`
- Output key `domisili_db: domisili,` → `lokasi_kerja_db: lokasi_kerja,`

> Catatan: nama variabel JS boleh tetap `domisili` kalau mau minim edit, TAPI label `DOMISILI:`, token `'domisili'`/`'nama+domisili'`, dan output key `domisili_db` **wajib** ikut aturan §1 karena dipakai lintas-node.

### STEP D — Node `AI Agent` → `parameters.options.systemMessage`
Ini teks prompt. Ganti 12 titik (nomor baris relatif dalam prompt):
- **Line 33** header: `# PROFIL USER (nama lengkap + domisili)` → `# PROFIL USER (nama lengkap + lokasi kerja)`
- **Line 34:** `Tim perlu nama lengkap + kota/kecamatan domisili untuk follow-up. Field NAMA_LENGKAP, DOMISILI, ASK_PROFILE ...` → `... kota/kecamatan lokasi kerja untuk follow-up. Field NAMA_LENGKAP, LOKASI_KERJA, ASK_PROFILE ...`
- **Line 36 (kalimat greeting):** `"...ini dengan Kak siapa dan domisilinya di mana yaa? 😊"` → `"...ini dengan Kak siapa dan lokasi kerjanya di mana yaa? 😊"`
- **Line 37:** `NAMA_LENGKAP/DOMISILI masih UNKNOWN` → `NAMA_LENGKAP/LOKASI_KERJA masih UNKNOWN`
- **Line 38:** `Domisili cukup kota/kecamatan ("Tangerang", "Cisoka"). Jawaban ambigu ("di rumah", "deket sini") ...` → `Lokasi kerja cukup kota/kecamatan ("Tangerang", "Cisoka"). Jawaban ambigu ("di kantor", "deket sini") ...`
- **Line 39:** `Begitu user menyebut nama/domisili` → `Begitu user menyebut nama/lokasi kerja`
- **Line 43 (combined-ask):** `"...ini dengan Kak siapa, domisilinya di mana, dan lagi cari unit ...` → `"...ini dengan Kak siapa, lokasi kerjanya di mana, dan lagi cari unit ...`
- **Line 78 (# SURVEY):** `kalau NAMA_LENGKAP/DOMISILI masih UNKNOWN` → `.../LOKASI_KERJA masih UNKNOWN`
- **Line 109 (# TAG, spec [FACTS]):** `[FACTS unit="..." budget="..." nama="..." domisili="<kota/kecamatan>"] ... Contoh: [FACTS nama="Budi Santoso" domisili="Tangerang"]` → ganti atribut `domisili=` jadi `lokasi_kerja=` (dan contohnya)
- **Line 117 (# LARANGAN):** `Nama lengkap dan domisili kota/kecamatan BOLEH` → `Nama lengkap dan lokasi kerja kota/kecamatan BOLEH`

### STEP E — Node `Process All` (Code)
- Regex FACTS: `/domisili\s*=\s*"([^"]*)"/i` → `/lokasi_kerja\s*=\s*"([^"]*)"/i` (harus cocok dgn atribut baru di STEP D)
- `let factNama = '', factDomisili = '';` → `... factLokasiKerja = '';`
- `factDomisili = (factsMatch[1].match(/domisili.../))...` → `factLokasiKerja = (factsMatch[1].match(/lokasi_kerja.../))...`
- `$('Cek_user_status').first().json.domisili_db` → `...json.lokasi_kerja_db`
- Variabel: `existingDomisili` → `existingLokasiKerja`, `domisiliMerged` → `lokasiKerjaMerged`, `domisiliChanged` → `lokasiKerjaChanged`
- Output key: `domisili_merged: domisiliMerged,` → `lokasi_kerja_merged: lokasiKerjaMerged,` dan `domisili_changed: domisiliChanged` → `lokasi_kerja_changed: lokasiKerjaChanged`

### STEP F — Node `Update to STATS` (Google Sheets, appendOrUpdate)
Karena header sheet sudah diganti di STEP A:
1. Buka node → di `Columns` klik refresh/re-fetch daftar kolom supaya `lokasi_kerja` & `lokasi_kerja_ts` muncul (kolom `domisili` lama hilang).
2. Map nilai kolom baru:
```
lokasi_kerja      = {{ $('Process All').first().json.lokasi_kerja_merged || '' }}
lokasi_kerja_ts   = {{ $('Process All').first().json.lokasi_kerja_changed ? Math.floor(Date.now()/1000) : ($('Resolve User Row').first().json.lokasi_kerja_ts || '') }}
```
3. Pastikan schema entry `lokasi_kerja` & `lokasi_kerja_ts` ada (kalau edit JSON manual: ganti `"id":"domisili"`→`"id":"lokasi_kerja"` dst, jangan sampai ada flag `removed`). Kalau lewat UI, refresh kolom sudah beres otomatis.

### STEP G — Node `Collect Handover Context` (Code)
```js
// LAMA
domisili: pa.domisili_merged || statsRow['domisili'] || '',
// BARU
lokasi_kerja: pa.lokasi_kerja_merged || statsRow['lokasi_kerja'] || '',
```
(update juga komentar changelog di atas objek `profil` kalau ada, biar konsisten)

### STEP H — Node `Summarize Handover` (chainLlm → `parameters.text`)
- Template output: `Profil Klien: <nama, domisili, no WA, sumber>` → `<nama, lokasi kerja, no WA, sumber>`
- Label: `Domisili: {{ $json.handover_profil.domisili }}` → `Lokasi Kerja: {{ $json.handover_profil.lokasi_kerja }}`

### STEP I — Node `Format Handover Message` (Code)
```js
// LAMA
${p.domisili ? ', ' + p.domisili : ''}
// BARU
${p.lokasi_kerja ? ', ' + p.lokasi_kerja : ''}
```

### Simpan & aktifkan
- Save workflow. Aktifkan kembali kalau tadi dinonaktifkan.

---

## 4. Catatan variabel JS internal
Nama variabel murni-internal (`factDomisili`, `domisiliMerged`, `needDomicile`, `existingDomisili`) secara teknis TIDAK wajib diganti untuk correctness — asal konsisten dalam satu node. Tapi disarankan rename (§ langkah di atas sudah termasuk) supaya maintenance ke depan tidak bingung karena konsep sudah "lokasi kerja". Yang **wajib** lintas-node cuma: nama kolom sheet, label `LOKASI_KERJA:`, atribut `[FACTS] lokasi_kerja=`, token askProfile, dan semua output key (`lokasi_kerja`, `lokasi_kerja_ts`, `lokasi_kerja_db`, `lokasi_kerja_merged`, `lokasi_kerja_changed`).

---

## 5. Testing setelah selesai
1. Chat dari **nomor WA baru** (yang belum ada di STATS) → cek Vira menanyakan "lokasi kerjanya di mana".
2. Jawab mis. "Budi, kerja di Tangerang".
3. Cek tab STATS: baris user baru terisi `nama_lengkap` = Budi, `lokasi_kerja` = Tangerang, `lokasi_kerja_ts` terisi epoch.
4. Trigger jalur survey/handover → cek pesan handover memuat "Lokasi Kerja: Tangerang".
5. Cek execution n8n: tidak ada node error, `Update to STATS` benar-benar menulis kolom (bukan no-op).

---

## 6. File dokumentasi ikut diupdate (opsional, biar konsisten)
- `2026-07-19-spec-nama-domisili-greeting-VIRA-PCR.md`
- `workflow/patch V.1.3/2026-07-20-fix-handover-nama-domisili.md`

---

## 7. Catatan penting SURVEY tab
Tab **SURVEY** TIDAK punya kolom domisili (memang belum pernah diimplementasi). Jadi tidak ada yang perlu diubah di node `Write SURVEY`. Cukup STATS saja.
