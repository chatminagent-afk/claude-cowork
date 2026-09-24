# DASH_AUDIT Cleanup — VIRA Dashboard

Tanggal: 2026-08-26
File workflow: `2026-08-26-VIRA-Dashboard-DASH_AUDIT-Cleanup.json` (12 node)
Builder (rerunnable): `build_audit_cleanup.py`

---

## 1. Jawaban: cukup **1 workflow**, bukan 2

Tiga alasan teknis, semuanya sudah terverifikasi di file yang ada:

| Alasan | Bukti |
|---|---|
| Kedua spreadsheet dibuka pakai **credential yang sama** | node `Append Audit` di `n8n/VIRA-Dashboard-API.json` menulis ke DASH_AUDIT kedua tenant hanya dengan `Google Service Account - VIRA Dashboard` (id `5KD9A3Tef1H8UQKk`) |
| Nama tab & skema kolom **identik** | `n8n/src/tenants.js:400` → `auditTab: 'DASH_AUDIT'` dipakai global (bukan per-tenant); header sama: `ts \| actor \| role \| no_wa \| from \| to` |
| Pola multi-target **sudah terbukti** di workflow yang sama | `Fan Out Tabs` → `Loop Over Tabs` → node Sheets dengan `documentId = {{ $json.doc_id }}`. Workflow ini memakai pola persis itu, hanya di-fan-out per *tenant* bukan per *tab* |

Yang biasanya memaksa 2 workflow — credential berbeda, skema berbeda, jadwal berbeda per klien — tidak ada satu pun di sini.

Satu-satunya kerugian 1 workflow adalah *blast radius*: satu error bisa menghentikan tenant lain.
Itu sudah ditutup: node `Read DASH_AUDIT` dan `Delete Rows` di-set `onError: continueRegularOutput`, jadi kalau tab The Scholars belum dibuat / gagal, Persada tetap dibersihkan (dan sebaliknya).

**Kalau nanti klien ke-3 pakai service account sendiri** → baru pecah jadi 2 workflow (atau tambah node Sheets kedua dengan credential lain). Selama credential-nya satu, jangan digandakan.

---

## 2. Cara kerja

```
Tiap 3 bulan 02:00 WIB ─┐
Test manual ────────────┴─► Fan Out Tenants ─► Loop Over Tenants ─(done)─► Ringkasan
                                                    │
                                                  (loop)
                                                    ▼
                                          Read DASH_AUDIT (per tenant)
                                                    ▼
                                          Hitung Baris Dihapus
                                                    ▼
                                              Ada Baris?
                                            ┌──true──┴──false──┐
                                     Delete Rows          Lewati (kosong)
                                            ▼                  │
                                      Catat Hasil ─────────────┴─► kembali ke Loop
```

- **Header tidak pernah tersentuh.** Node `Hitung Baris Dihapus` menyaring `row_number >= 2`, jadi baris 1 mustahil masuk range hapus.
- Menghapus **baris**, bukan cuma isinya — sheet benar-benar menyusut (hemat kuota sel), bukan menyisakan ribuan baris kosong.
- Satu `delete range` per tenant (bukan per baris) → hemat kuota Sheets API.
- Kalau tab kosong / belum dibuat → `count = 0` → cabang `Lewati`, tidak error.

---

## 3. Konfigurasi — hanya node `Fan Out Tenants`

```js
const RETENTION_DAYS = 0;          // 0 = wipe total, sisakan header (default, sesuai permintaan)
                                   // 90 = simpan 90 hari terakhir, buang yang lebih tua
const AUDIT_TAB      = 'DASH_AUDIT';

const TENANTS = [
  { tenant: 'thescholars', nama: 'The Scholars',             doc_id: '1tEJ...' },
  { tenant: 'persada',     nama: 'Persada Cisoka Residence', doc_id: '1pzG...' },
];
```

Tambah klien ke-3 = **tambah 1 baris di array ini**. Nol perubahan di node lain.

### Ganti jadwal

Node `Tiap 3 bulan 02:00 WIB` → field Cron Expression:

| Frekuensi | Cron |
|---|---|
| Tiap 3 bulan (default) — 1 Jan/Apr/Jul/Okt 02:00 | `0 2 1 1,4,7,10 *` |
| Tiap bulan — tanggal 1, 02:00 | `0 2 1 * *` |

Timezone sudah `Asia/Jakarta` di `settings` workflow, jadi jam di atas = WIB.

**Rekomendasi: tiap 3 bulan.** DASH_AUDIT hanya bertambah 1 baris per klik toggle `bot_mode` — volumenya sangat kecil, cleanup bulanan tidak perlu dan cuma menghapus jejak yang masih berguna saat troubleshooting.

---

## 4. Deploy

1. n8n → **Workflows → Import from File** → pilih `2026-08-26-VIRA-Dashboard-DASH_AUDIT-Cleanup.json`
2. Buka node `Read DASH_AUDIT` dan `Delete Rows (header aman)` → pastikan credential ter-resolve ke **Google Service Account - VIRA Dashboard**. Kalau id `5KD9A3Tef1H8UQKk` tidak cocok di instance, pilih ulang dari dropdown.
3. Pastikan tab `DASH_AUDIT` sudah ada di **kedua** spreadsheet dengan header baris 1: `ts | actor | role | no_wa | from | to` (lihat `docs/2026-07-28-DEPLOY-README.md:76`). Kalau belum ada, workflow ini tetap aman — cuma me-skip tenant itu.
4. (Opsional) Settings → **Error Workflow** → arahkan ke error notifier, seperti workflow PCR lain.
5. Activate.

### Smoke test — WAJIB sebelum diaktifkan

Jangan langsung jalan dengan `RETENTION_DAYS = 0`.

1. Set `RETENTION_DAYS = 3650` (10 tahun) → praktis tidak ada yang dihapus.
2. Klik **Test manual**. Cek output node `Ringkasan`: harus muncul 2 entri tenant dengan `dihapus: 0` dan `status` sesuai.
3. Cek `Hitung Baris Dihapus` untuk masing-masing iterasi: `startRow` harus **2** (atau nomor baris data pertama), tidak pernah 1.
4. Turunkan ke `RETENTION_DAYS = 1`, jalankan manual sekali, lalu **buka spreadsheet dan pastikan baris header masih utuh**.
5. Baru set ke `0` dan Activate.

Kenapa langkah 3–4 penting: parameter `startIndex` node Google Sheets bersifat 1-based (baris pertama = 1) — pola yang sama dipakai workflow production `VIRA-PCR - MSG_BUFFER Cleanup`. Kalau ternyata instance ini berperilaku 0-based, gejalanya adalah **error grid limit** atau satu baris data tersisa, bukan header ikut terhapus — tapi tetap lebih baik dilihat langsung sekali.

---

## 5. Catatan / risiko

- **DASH_AUDIT tidak dibaca siapa pun.** Sudah dicek: tidak masuk `tabs[]` tenant manapun di `tenants.js`, dan tidak ada referensi `audit` di `app revamp/js/*.js`. Sheet ini murni write-only, dibaca manual lewat spreadsheet. Jadi menghapus isinya **tidak merusak fitur dashboard apa pun** — yang hilang hanya jejak siapa mematikan bot_mode siapa dan kapan.
- Kalau jejak itu masih dibutuhkan untuk akuntabilitas ke klien, pakai `RETENTION_DAYS = 90` (rolling) daripada `0`. Kode sudah mendukung, tinggal ganti angka.
- Workflow ini **berdiri sendiri**, tidak digenerate oleh `n8n/build_workflow.py` (script itu hardcoded khusus `VIRA Dashboard API`). Edit lewat `build_audit_cleanup.py` lalu rerun, atau langsung di UI n8n — pilih satu, jangan dua-duanya.
- Node Sheets di sini pakai `typeVersion 4.7` (sama dengan workflow PCR production), sedangkan `VIRA Dashboard API` masih `4.5`. Tidak masalah, keduanya jalan berdampingan di instance yang sama.
