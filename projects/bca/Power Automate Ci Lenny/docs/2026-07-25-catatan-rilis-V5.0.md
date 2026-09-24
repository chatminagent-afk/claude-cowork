# WeeklyMBIProjectsReportV.5.0 — Catatan Rilis

**Package:** `2026-07-25-WeeklyMBIProjectsReportV.5.0.zip`
**Flow:** Weekly Reminder Ci Lenny - MBI Projects Report V5.0
**Basis:** WeeklyMBIProjectsReportV.4.9_20260717095244
**Flow ID baru:** `5c1e0a92-7d44-4b1e-9f3a-2ab6d8e15f70` (v4.9 **tidak** tertimpa saat import)

---

## Perubahan Besar

Report dipecah dari **1 kartu** menjadi **3 kartu berurutan** ke group chat yang sama:

| Kartu | Isi |
|---|---|
| **1/3** | 📊 Header + tanggal + 📋 RECAP RELEASE THIS MONTH (12 angka + Exclude Implementation Package) |
| **2/3** | 🚀 DETAIL RELEASE THIS MONTH — timeline, 9 section project, Out-of-Package |
| **3/3** | 🚀 DETAIL RELEASE NEXT MONTH — blok identik, lalu Support Project, ON HOLD, NEXT PROJECT, Attention |

Tiap kartu punya judul + label `Bagian X dari 3` sendiri, jadi tidak ada informasi yang terpotong di tengah. Kartu 2 ditutup dengan penunjuk `Bersambung ke Bagian 3`.

---

## Resolusi Bulan

```
varBulanCal  = bulan kalender saat flow jalan
             ↓ cek Rollout bulan tsb di Table5
varOffset    = 1 kalau Rollout sudah lewat, 0 kalau belum
varBulan     = bulan kalender + varOffset          ← THIS MONTH
varBulanNext = bulan kalender + varOffset + 1      ← NEXT MONTH
```

Logika rollover v4.9 dipertahankan. Timeline (Pilot / Prod / Rollout), Regresi, dan Version diambil dari `Table5` untuk **kedua** bulan sekaligus dalam satu loop.

**Contoh** (jalan 25 Jul 2026): Rollout Jul = 14 Jul → sudah lewat → THIS = **Aug 2026 / Ver 2.20.0**, NEXT = **Sep 2026 / Ver 2.21.0**.

---

## Mapping Recap (kolom M `Status UAT`, difilter kolom K = bulan berjalan)

| Baris Recap | Status sumber |
|---|---|
| Total Project | semua baris bulan berjalan |
| Waiting Prep UAT | `NEXT PROJECT` |
| Prep UAT | `ON GOING SKENARIO`, `ON GOING PREP UAT` |
| Ready To UAT | `READY TO UAT` |
| On Going UAT | `ON GOING UAT` |
| Done UAT | `DONE UAT` |
| On Going Regresi | `ON GOING REGRESI` |
| Done Regresi | `DONE REGRESI` |
| Ready to Implement | `READY TO IMPLEMENT` |
| On Going Pilot | `ON GOING PILOT` |
| On Going Prod | `ON GOING PROD` |
| Done Implement | `DONE IMPLEMENT`, `SERTIFIKASI`, `LHI`, `CLOSED` |
| Exclude Implementation Package | COUNTIF kolom N = `Y` |

Angka dihitung pakai action **Filter array** + `length()`, bukan increment di dalam loop — lebih cepat dan tidak bisa salah hitung.

Baris kolom N = `Y` **di-exclude** dari Total Project dan semua status count, supaya tidak dobel dengan baris Exclude.

---

## Section Detail (per bulan)

Urutan di kartu 2 dan 3 identik:

1. 📅 Implementation Package Timeline + Regresi
2. 📋 Prep UAT — *include On Going Skenario, On Going Prep UAT, Ready to UAT*
3. 🔵 On Going UAT — dengan indikator 🟢 On Target / 🟡 Warning
4. ✅ Completed UAT
5. 🔁 On Going Regresi
6. ✅ Completed Regresi
7. 📦 Ready to Implement
8. 🚀 On Going PILOT
9. 🏭 On Going PROD
10. ✅ Done Implement — *include Done Implement, Sertifikasi, LHI, Closed*
11. 🛠️ Out-of-Package Project Implementation — dari sheet **Support Project**, difilter `Estimated Implementation` = bulan bersangkutan

Section kosong tampil `—`.

**Format tiap entry diambil verbatim dari v4.9** (parsing tanggal Excel-serial, emoji progres 🟢/🟡/🔵, escaping tanda kutip, logika Track2) — jadi tampilan per project persis sama, hanya penempatannya yang pindah.

---

## Section Bawah (global, di kartu 3)

Berurutan sesuai permintaan: 🛠️ Support Project → ⏸️ ON HOLD → 📦 NEXT PROJECT → ⚠️ Attention → tombol 📎 Buka Tracking Sheet.

Ketiganya tidak difilter bulan (sama seperti v4.9).

---

## Perbaikan Teknis

| Hal | v4.9 | v5.0 |
|---|---|---|
| Deteksi Rollout lewat | `ticks()` langsung ke nilai mentah — gagal kalau selnya serial number | nilai dinormalisasi ke `MM/dd/yyyy` dulu, baru `ticks()` |
| Tab / newline di nama project | tidak ditangani → bisa merusak JSON kartu | dibersihkan di 94 titik (`%09`, `%0D`, `%0A`) |
| Baris kolom K error | ikut diproses | `#VALUE!` / kosong otomatis ter-skip (tidak cocok bulan mana pun) |
| Hitungan recap | belum ada | 13 Filter array |
| Variabel tanpa nilai awal | 10 variabel `InitializeVariable` tanpa `value` | semua diberi nilai awal eksplisit |

---

## Hasil Verifikasi

- ✅ 179 action, tidak ada nama duplikat, semua `runAfter` valid
- ✅ 39 variabel — semua ter-inisialisasi, tidak ada yang menganggur
- ✅ Ketiga Compose disimulasikan → menghasilkan Adaptive Card JSON yang **valid & ter-parse**
- ✅ Ukuran kartu: 1,9 KB / 4,4 KB / 5,7 KB (batas Teams ±28 KB — aman)
- ✅ Struktur zip cocok dengan format package v4.9

**Simulasi terhadap data Excel nyata (per 25 Jul 2026, THIS = Aug 2026):**

```
Total Project 17 | Waiting Prep UAT 3 | Prep UAT 1 | Ready To UAT 2
On Going UAT 4 | Done UAT 6 | Done Implement 1 | Exclude 0
NEXT MONTH (Sep 2026): Done UAT 4, Next Project 5, On Going UAT 4,
                       On Going Prep UAT 1, Ready To UAT 1
ON HOLD 2 | NEXT PROJECT 49 | Support Project on-going 2
```

---

## ⚠️ Perlu Diperhatikan

**Kolom K (`Estimated Implementation`) rusak sebagian.** Kolom itu formula `=TableMasterSuperfile[[#This Row],[Estimated Implementation]]`. Dari 414 baris, **259 baris** nilainya `#VALUE!` atau kosong karena lookup ke sheet `LookupSheetSuperfileMyBCA` gagal. Baris-baris itu di-skip (sesuai keputusan), tapi artinya **hanya ~155 baris yang benar-benar masuk report**. Kalau ada project yang "hilang" dari report, penyebabnya hampir pasti di sini — bukan di flow.

**Out-of-Package saat ini kosong** untuk Aug dan Sep 2026, karena tidak ada baris di sheet Support Project yang `Estimated Implementation`-nya jatuh di bulan tersebut.

---

## Checklist Sebelum Go Live

- [ ] Import package → pilih **Create as new** (jangan Update, biar v4.9 tetap ada)
- [ ] Pasang koneksi Excel Online (Business) dan Microsoft Teams
- [ ] Cek trigger: Jumat 20:00 SE Asia Standard Time (warisan v4.9 — kalau mau 08:00 pagi, ubah `hours` dari `20` ke `8`)
- [ ] Test run manual, pastikan 3 kartu masuk berurutan ke group chat
- [ ] Bandingkan angka recap dengan hitungan manual di Excel
- [ ] Perbaiki lookup kolom K kalau angka Total Project terasa kekecilan
- [ ] Matikan v4.9 setelah v5.0 dikonfirmasi jalan
