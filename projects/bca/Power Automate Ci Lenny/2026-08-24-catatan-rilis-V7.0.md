# WeeklyMBIProjectsReportV.7.0 — Catatan Rilis

**Package:** `2026-08-24-WeeklyMBIProjectsReportV.7.0.zip`
**Flow:** Weekly Reminder Ci Lenny - MBI Projects Report V7.0
**Basis:** `2026-08-19-WeeklyMBIProjectsReportV.6.0`
**Flow ID baru:** `571df2ca-0369-4985-821f-c2279e92d442` (V6.0 **tidak** tertimpa saat import)

---

## Ringkas

Empat perubahan, hanya 4 action yang disentuh. Kartu 2 dan Kartu 3 **byte-identik** dengan V6.0. Trigger, variabel, dan seluruh graph `runAfter` tidak berubah.

| # | Perubahan | Action |
|---|---|---|
| 1 | Header recap: `📋 RECAP RELEASE THIS MONTH` → `📋 RECAP RUNNING FOR` | `Compose_Card1` |
| 2 | Disclaimer baru (italic) di bawah "Bagian 1 dari 3" | `Compose_Card1` |
| 3 | Sub-blok `── NEXT MONTH ──` dihapus dari section Attention | `Compose_Attention` |
| 4 | **Bugfix: Pagination dinyalakan** (threshold 5000) | `List_rows_Project_Testing`, `List_rows_SupportProject` |

---

## 1–2. Perubahan Kartu 1

Urutan tampilan baru:

```
📊 Weekly MBI Projects Report
<tanggal>
Bagian 1 dari 3
❗Disclaimer: recap project ini hanya menampilkan project yang akan
implementasi di 2 bulan terdekat            ← italic, ukuran normal, abu-abu
————————————
📋 RECAP RUNNING FOR — Sep 2026 — Ver 2.21.0
```

Disclaimer dirender italic via markdown `_..._`. Kalau di klien Teams tertentu italic tidak ke-render (tampil underscore literal), ganti pengapitnya jadi `*...*` di `Compose_Card1`.

Nomor bulan/versi di header tetap dinamis (kolom `Version` sheet Timeline), tidak ada yang di-hardcode.

## 3. Attention = bulan berjalan saja

Aturan yang diinginkan: Attention berisi project bulan berjalan, dan "bulan berjalan" otomatis maju ke bulan berikutnya begitu tanggal implementasi (kolom `Rollout` di sheet Timeline) terlewati. Mekanisme rollover itu **sudah ada** di flow (`Condition_RolloutPassed` → `varOffset` → `varBulan`) — yang membuat entri bulan depan ikut tampil adalah sub-blok `── NEXT MONTH: <bulan> ──` warisan penggabungan Attention V6.0. Sub-blok itu dihapus dari `Compose_Attention`.

Action rantai NM (`Filter_NM_OnGoingUAT`, `Select_NM_Metrics`, `Filter_NM_Attn`, `Select_Attn_NM`) **dibiarkan utuh tapi tidak dirender** — sama seperti perlakuan `varAttention` di V6.0 — supaya gampang dikembalikan kalau kebijakan berubah.

Konsekuensi yang disadari: project bulan depan yang bermasalah tidak lagi ter-surface di kartu mana pun sampai bulannya menjadi bulan berjalan.

## 4. Bugfix pagination — akar masalah P-258 hilang

**Gejala:** run 21 Aug 2026 — P-258 (QR CB Hongkong, Sep 2026, ON GOING SKENARIO) tidak muncul di Kartu 1 maupun Kartu 2; Total Project tampil 16.

**Akar masalah:** konektor Excel Online `List rows present in a table` berhenti di **256 baris** bila setting Pagination mati, berapa pun nilai `$top` (di flow ini `$top: 5000`, tapi tanpa pagination hanya halaman pertama yang diambil). Tabel `TableProjectTesting` sudah 414 baris — semua baris ≥257 (P-257 ke atas) tidak pernah terbaca. Data P-258 sendiri diverifikasi bersih: `Sep 2026` 8 karakter persis, status match, `Diluar Paketan?` kosong, baris di dalam range table.

**Perbaikan:** `"runtimeConfiguration": {"paginationPolicy": {"minimumItemCount": 5000}}` dipasang di `List_rows_Project_Testing` dan `List_rows_SupportProject`. `List_rows_Timeline` tidak perlu (18 baris).

**Dampak angka (data 24 Aug):** Total Project 16 → **22**, Prep UAT 1 → **4**, On Going UAT 0 → **1**, Completed UAT 14 → **16**. Kenaikan ini **koreksi**, bukan anomali data — sampaikan ke Ci Lenny sebelum run pertama V7.0.

Catatan: simulator verifikasi V6.0 membaca xlsx langsung (414 baris penuh), sehingga batas 256 konektor tidak pernah tersimulasi — karena itu bug ini lolos sampai production.

---

## Verifikasi package (22/22 lolos)

- GUID flow baru di folder, `definition.json` (`name`, `id`), `manifest.json`, dan `flows/manifest.json` — tidak ada sisa GUID lama
- displayName V7.0 di 3 lokasi
- Hanya 4 action berbeda dari V6.0; set action & graph `runAfter` identik
- `Compose_Attention` bersih dari `NEXT MONTH` / `Select_Attn_NM` / `varBulanNext`; bagian 🔴/🟡 verbatim dari V6.0 (termasuk batas 12+12 entri)
- Kartu 2 & Kartu 3 byte-identik dengan V6.0; trigger identik
- Kartu 1 hasil build disimulasikan render → Adaptive Card valid, disclaimer di posisi & format yang benar
- 227 ekspresi `@` ter-parse

## Checklist import

- [ ] Import package → **Create as new** (jangan Update, biar V6.0 tetap ada)
- [ ] Pasang koneksi Excel Online (Business) dan Microsoft Teams
- [ ] Cek trigger: Jumat 20:00 SE Asia Standard Time (warisan, tidak diubah)
- [ ] Test run manual — pastikan:
  - [ ] Total Project = jumlah sebenarnya (per 24 Aug: **22**, bukan 16)
  - [ ] P-257 & P-258 muncul (P-258 di list Prep UAT Kartu 2)
  - [ ] Disclaimer italic muncul di bawah "Bagian 1 dari 3"
  - [ ] Header: `📋 RECAP RUNNING FOR — <bulan> — Ver <x>`
  - [ ] Attention **tanpa** blok NEXT MONTH (untuk Sep saat ini tampil `—` — benar, satu-satunya project UAT Sep sudah 100%)
- [ ] Info ke Ci Lenny: angka naik karena koreksi pagination
- [ ] Matikan V6.0 setelah V7.0 dikonfirmasi jalan

## Ditunda (dicatat, belum dikerjakan)

- Penyeragaman label "THIS MONTH" di Kartu 2/3 — menunggu keputusan wording (Steven ajukan take-out "THIS MONTH")
- Bug bawaan V5.0: backslash `\` di nama project bisa merusak Kartu 2 (belum pernah kejadian; nama project saat ini bersih)
