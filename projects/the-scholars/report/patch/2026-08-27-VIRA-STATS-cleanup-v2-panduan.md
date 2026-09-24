# VIRA — STATS Cleanup v2: filter "whitelist baris OFF"

**Tanggal:** 2026-08-27
**File workflow:** `2026-08-27-VIRA-STATS-cleanup-3bulan-v2.json`
**QA:** `2026-08-27-qa-cleanup-v2.py` — 80 PASS / 0 FAIL
**Menggantikan:** `2026-08-19-VIRA-STATS-cleanup-3bulan.json` (v1, **belum pernah diaktifkan**)

---

## 1. Aturan baru

Hapus **semua** baris data di tab STATS, **kecuali**:

1. **Header** (baris 1) — tidak pernah disentuh.
2. Baris dengan `bot_mode == "OFF"` yang `off_reason`-nya **BUKAN** `"VIRA"`.

Jadi dari kelompok baris OFF, satu-satunya yang ikut dihapus adalah yang eksplisit
dilabeli `off_reason = VIRA`. Perbandingan case-insensitive + trim (`"off"`, `" Off "`,
`"OFF"` sama; `"vira"`, `" Vira "` sama).

### Tabel keputusan

| `bot_mode` | `off_reason` | v1 (lama) | v2 (baru) |
|---|---|---|---|
| `ON` / kosong | apa pun | HAPUS | **HAPUS** |
| `OFF` | `VIRA` | HAPUS | **HAPUS** |
| `OFF` | `SAM` | simpan | **SIMPAN** |
| `OFF` | kosong (Sam lupa isi) | HAPUS ← *bahaya* | **SIMPAN** |
| `OFF` | kosong (di-OFF lewat Dashboard) | HAPUS ← *bahaya* | **SIMPAN** |
| `OFF` | label lain (`CEK`, typo, dll) | HAPUS ← *bahaya* | **SIMPAN** |

v2 adalah **superset** dari v1 — tidak ada satu pun baris yang dulu selamat lalu jadi
terhapus. Diuji eksplisit di QA bagian E.

## 2. Kenapa dibalik

v1 memakai **whitelist label**: hanya `off_reason == "SAM"` yang selamat. Masalahnya
label itu harus **diisi manual** Sam lewat dropdown di sheet, sementara ada dua jalur
yang mematikan bot **tanpa pernah menulis `off_reason`**:

- Sam mengubah `bot_mode` langsung di Google Sheets dan lupa isi dropdown-nya.
- **VIRA Dashboard** — node `Update Bot Mode` di `VIRA-Dashboard-API.json` hanya menulis
  `row_number` (match key) + `bot_mode`. Grep `off_reason` di seluruh file itu = 0 hasil.
  Histori toggle-nya masuk ke tab `DASH_AUDIT`, bukan ke kolom `off_reason` di STATS.

Di v1 kedua kasus itu terbaca sebagai "OFF tanpa label" dan **ikut terhapus** — padahal
justru itu murid/parent yang harus ditangani manual selamanya. v2 membalik arahnya jadi
**blacklist label**: lupa-label = baris tetap aman, yang hilang hanya yang sudah jelas
ditandai VIRA. Fail-safe, bukan fail-open.

## 3. Perubahan node

| Node | Perubahan |
|---|---|
| `Plan cleanup` | jsCode diganti total (aturan + guard + counter baru) |
| `Split kept rows` | jsCode: komentar & log disesuaikan; logika sama |
| `Prepare delete` | jsCode: log menyebut jumlah baris OFF; logika sama |
| `IF Ada Baris SAM` | **rename** → `IF Ada Baris Dipertahankan` (kondisi `keptCount > 0` tetap) |
| `Append SAM rows` | **rename** → `Append Baris Dipertahankan` (parameter tetap) |
| `Notify Steven` | pesan WA dirombak: rincian dipertahankan vs dihapus |

Tidak berubah: cron `1 0 1 */3 *`, timezone `Asia/Jakarta`, errorWorkflow, documentId,
gid `56867128`, credential, `retryOnFail`, dan **urutan append → delete**.

Nama node `Plan cleanup` **wajib tetap** — direferensikan `$('Plan cleanup')` oleh
`Split kept rows` dan `Prepare delete`. Dua node yang di-rename tidak direferensikan
node lain, jadi aman.

## 4. Guard

| # | Kondisi | Aksi | Alasan |
|---|---|---|---|
| 1 | Kolom `No WA` tak ada | **throw** | Tab yang terbaca kemungkinan bukan STATS |
| 2 | Kolom `bot_mode` tak ada | **throw** | **Kritis di v2.** Tanpa kolom ini semua baris terbaca non-OFF → seluruh STATS terhapus |
| 3 | Kolom `off_reason` tak ada | **warning + flag** | Di v2 kolom ini hanya mempersempit yang dihapus; kalau hilang, semua OFF selamat (aman, cuma kurang bersih) |
| 4 | `deleteCount <= 0` | **skip** (return kosong) | Jangan jalankan siklus append+delete kalau tidak ada yang perlu dihapus |

**Perhatikan pergeseran guard kritis**: di v1 kolom pengunci adalah `off_reason`; di v2
adalah `bot_mode`. Guard 2 baru; guard 3 turun status dari throw jadi warning; guard 4 baru.

## 5. Yang harus dicek sebelum aktivasi

1. **Kolom `off_reason` belum ada di file export manapun.** Panduan 2026-08-19 bilang
   kolomnya ditambahkan manual sebagai kolom **X** (setelah `last_reply_ts`), dan field
   `off_reason: "VIRA"` ditambahkan manual di node `Update row in sheet` workflow utama.
   Grep `off_reason` di `r6`, `V6-media-skill`, `r7`, `r8` = **0 hasil** — jadi tidak ada
   bukti di repo bahwa perubahan itu benar-benar sudah dipasang di n8n.
   **Cek langsung di editor n8n** apakah `Update row in sheet` sudah menulis `off_reason`.
   Kalau belum: v2 tetap aman jalan (guard 3 → semua OFF disimpan, nol yang dihapus dari
   kelompok OFF), tapi tab tidak akan pernah benar-benar bersih dari baris OFF-by-VIRA.
2. **`ISI_NOMOR_WA_STEVEN`** di node `Notify Steven` masih placeholder — ganti dulu.
3. Workflow di-import dalam keadaan **non-aktif** (`active: false`). Disarankan sekali
   **Execute Workflow manual** dulu sambil lihat output `Plan cleanup` sebelum diaktifkan.

## 6. Sisa risiko

- Baris yang di-OFF lewat Dashboard sekarang **tidak akan pernah terhapus** oleh cleanup,
  karena `off_reason`-nya selamanya kosong. Ini konsekuensi yang disengaja dari aturan v2.
  Kalau nanti tab jadi menumpuk, opsinya: Dashboard ikut menulis `off_reason` (mis. `DASH`),
  lalu putuskan apakah `DASH` masuk daftar yang boleh dihapus.
- Baris berlabel di luar `SAM`/`VIRA` disimpan dan dihitung sebagai `keptOffOther`;
  notifikasi WA memberi tanda `CEK:` kalau jumlahnya > 0.
