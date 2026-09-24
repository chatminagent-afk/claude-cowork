# WeeklyMBIProjectsReportV.6.0 — Catatan Rilis

**Package:** `2026-08-19-WeeklyMBIProjectsReportV.6.0.zip`
**Flow:** Weekly Reminder Ci Lenny - MBI Projects Report V6.0
**Basis:** `2026-07-25-WeeklyMBIProjectsReportV.5.0`
**Flow ID baru:** `8b3f4c17-6e29-4d05-a1b8-93c7f2ad6e41` (v5.0 **tidak** tertimpa saat import)

---

## Ringkas

Tiga section baru disisipkan di **Kartu 1**, tepat setelah RECAP RELEASE THIS MONTH:

1. 📈 **Coverage UAT (On Going)** — 🟢 / 🟡 / 🔴, dihitung atas project On Going UAT
2. 🎯 **Go-Live Readiness (UAT + Regression)** — 🟢 Ready / 🟡 Conditional / 🔴 Not Ready
3. ⚠️ **Attention** — detail dari Coverage UAT 🟡 dan 🔴

Blok ⚠️ Attention yang lama di Kartu 3 **dihapus** dan isinya digabung ke Attention baru di Kartu 1 (termasuk entri bulan depan, supaya tidak ada informasi yang hilang).

Selain itu **tidak ada** yang diubah. Kartu 2 byte-identik dengan v5.0.

---

## Perubahan label RECAP

| v5.0 | V6.0 | Logika filter |
|---|---|---|
| Done UAT | **Completed UAT** | tidak diubah |
| Done Regresi | **Completed Regresi** | tidak diubah |
| Exclude Implementation Package | **Out-of-Package Implementation** | tidak diubah (`Diluar Paketan?` = `Y`) |

10 baris recap lainnya tidak berubah sama sekali, begitu juga rumus di belakangnya.

> Catatan: "Out-of-Package Implementation" di recap = kolom `Diluar Paketan?` = `Y`.
> Ini **berbeda** dari section "🛠️ Out-of-Package Project Implementation" di Kartu 2/3
> yang sumbernya sheet `Support Project`.

---

## Formula Coverage UAT

Populasi: `Filter_OnGoingUAT` — Status UAT = `ON GOING UAT`, `Estimated Implementation` = bulan berjalan, `Diluar Paketan?` ≠ `Y`.
Karena itu **🟢 + 🟡 + 🔴 selalu = angka "On Going UAT" di recap** — bisa dicek silang langsung.

Dievaluasi **berurutan (worst-wins)** supaya tiap project masuk tepat satu bucket:

```
1. 🔴 <70%   bila  coverage < 70   ATAU  critical open > 1   ATAU  delay > 20 poin
2. 🟡 70-90% bila  bukan 🔴  DAN ( coverage < 90  ATAU  critical open ≥ 1  ATAU  ada delay )
3. 🟢 >90%   sisanya ( coverage ≥ 90  DAN  critical open = 0  DAN  tidak delay )
```

**Definisi delay** (dipakai juga untuk "progress sesuai timeline"):

```
varN       = jumlah hari kerja (Sen–Jum) Start UAT Plan .. End UAT Plan
varD       = jumlah hari kerja Start UAT Plan .. hari ini
expected%  = min(varD, varN) / varN × 100
delay      = expected% − (% UAT Overall × 100)      ← satuan poin persen
```

Mesin hari-kerja ini **diambil verbatim dari v5.0**, jadi identik dengan indikator 🟢 On Target / 🟡 Warning yang sudah tampil di Kartu 2. Toleransi 0,01 poin juga disamakan.
Kalau `Start UAT Plan` / `End UAT Plan` kosong atau bukan tanggal → delay dianggap **0** (project tidak dihukum karena tanggalnya belum diisi).

---

## Formula Go-Live Readiness

Populasi: `Filter_Total` — **semua** project bulan berjalan, `Diluar Paketan?` ≠ `Y`.
Karena itu **🟢 + 🟡 + 🔴 selalu = Total Project**.
(Populasi harus mencakup semua project, karena klausa 🔴 berbunyi "UAT Completion <100%" — klausa itu hanya hidup kalau project ber-UAT belum 100% ikut dihitung.)

```
1. 🔴 Not Ready   bila  UAT < 100  ATAU  Regresi < 80  ATAU  critical open > 1
2. 🟡 Conditional bila  bukan 🔴  DAN ( Regresi < 100  ATAU  critical open ≥ 1 )
3. 🟢 Ready       sisanya ( UAT = 100  DAN  Regresi = 100  DAN  critical open = 0 )
```

`% UAT Overall` (kolom AO) dan `% Regresi Overall` (kolom BC) tersimpan sebagai pecahan 0–1 di Excel, dikali 100 di flow. Sel kosong / teks / `#VALUE!` dihitung **0**.

---

## Critical Defect Open — kolom Q

Dibaca dari kolom **Q** sheet `Project-Testing` (nama header tabel saat ini: `Column32`).

**Selama kolom Q masih kosong, kriteria critical defect otomatis NONAKTIF** dan bucket ditentukan murni oleh coverage + progress terhadap timeline. Ini bukan penanganan khusus — kalau nilainya kosong, `critical open` = 0, sehingga klausa `> 1` dan `≥ 1` dua-duanya tidak pernah menyala.

Di section Attention, nilainya tampil `—` (bukan `0`) selama data belum tersedia, supaya tidak salah dibaca sebagai "sudah dicek, nol defect". Begitu kolom Q terisi angka, kriterianya langsung aktif tanpa perlu ubah flow.

**Dijamin tidak error** untuk semua keadaan berikut (sudah diuji satu per satu): kolom tidak ada sama sekali, string kosong, `null`, spasi, teks (`TBD`, `-`), angka `0`/`1`/`2`/`3`, dan desimal `2.0`.

Power Automate mengikat kolom lewat **nama header**, bukan huruf kolom. Kalau nanti header Q1 diganti dari `Column32` jadi nama sungguhan, flow tetap menemukannya — dipasang rantai `coalesce` ke: `Column32` → `Critical Defect Open` → `Critical Defect` → `Open Critical Defect` → `Critical`. Kalau dinamai di luar daftar itu, cukup ubah satu ekspresi di `Select_Cov_Metrics` dan `Select_GL_Metrics`.

Kalau kolom Q mau diisi dari data yang sudah ada di workbook:

```
=IFERROR(TableMasterSuperfile[[#This Row],[Critical]],"")
```

(`TableMasterSuperfile` kolom `Critical` ada di sheet `LookupSheetSuperfileMyBCA`, berisi angka 0–13.)

---

## Section Attention

Menggantikan blok Attention lama di Kartu 3. Urutan: **🔴 dulu, baru 🟡**, lalu sub-blok NEXT MONTH.

```
🔴 Track 14 — [ADHOC] Enhancement Validasi Data CIS BO ...
• Progress : 67%
• Critical Defect : 3
• PIC : Jesslyn, Verine
• Target Done : 21 Aug 2026
```

Sub-blok `── NEXT MONTH: <bulan> ──` hanya muncul kalau memang ada isinya. Ini menggantikan `Append_Attention_NM` yang dulu ikut mengisi Attention lama.

**Batas aman:** maksimal 12 entri 🔴, 12 entri 🟡, dan 8 entri NEXT MONTH. Kelebihannya tidak dibuang diam-diam — muncul baris `… +N project lainnya, lihat Tracking Sheet`. Tanpa batas ini, bulan dengan puluhan project bermasalah bisa membuat kartu melewati batas ±28 KB Teams dan gagal terkirim.

---

## Cara kerja teknis

15 action baru disisipkan antara `For_each_Support` dan `Compose_Card1`:

| Action | Fungsi |
|---|---|
| `Select_Cov_Metrics` | hitung `uat` / `crit` / `critav` / `delay` / `pic` / `target` sekali per project |
| `Filter_Cov_Red` / `_Yellow` / `_Green` | ladder Coverage UAT |
| `Select_GL_Metrics` | hitung `uat` / `reg` / `crit` untuk semua project bulan berjalan |
| `Filter_GL_NotReady` / `_Conditional` / `_Ready` | ladder Go-Live |
| `Filter_NM_OnGoingUAT`, `Select_NM_Metrics`, `Filter_NM_Attn` | Attention bulan depan |
| `Select_Attn_Red` / `_Yellow` / `_NM` | rakit teks per entri |
| `Compose_Attention` | gabungkan + terapkan batas aman |

Ekspresi berat (hari kerja / delay) dihitung **sekali per baris di action `Select`**, lalu `Filter array` tinggal membaca hasilnya. Ini membuat kondisi filter tetap pendek dan terbaca, dan tidak ada perhitungan yang diulang. Tidak ada counter di dalam loop — sama seperti prinsip v5.0.

`For_each_Project` dan `For_each_Support` **tidak disentuh sama sekali**. `varAttention` masih terisi seperti dulu tapi tidak lagi dirender — sengaja dibiarkan supaya logika lama gampang dikembalikan kalau perlu.

---

## Hasil verifikasi

Diuji pakai simulator Workflow Definition Language yang dibangun khusus, dijalankan atas **data Excel asli** (`Tracking Project MBI (di luar paketan).xlsx`, 414 baris).

| Uji | Hasil |
|---|---|
| Struktur, runAfter, variabel, referensi antar-action | 50/50 lolos |
| Ketahanan kolom Q & tanggal & persen bermasalah | 43/43 lolos |
| Skenario (rollover bulan, Q terisi, nama kotor, beban besar) | 11/11 lolos |
| Verifikasi artefak zip final | 17/17 lolos |
| Semua ekspresi `@` ter-parse | 79/79 |
| Kartu 2 dibanding v5.0 | **byte-identik** |
| Kartu 3 dibanding v5.0 | berkurang tepat 3 block (blok Attention), sisanya identik |
| Angka recap dibanding v5.0 | ke-13 angka sama persis |
| Invarian 🟢+🟡+🔴 | selalu = On Going UAT (Coverage) dan = Total Project (Go-Live) |
| Ukuran kartu | 3,1 KB / 5,7 KB / 9,8 KB (batas Teams ±28 KB) |

Diuji pada 5 tanggal jalan berbeda (05 Aug, 19 Aug, 30 Jun, 02 Jan, 28 Des termasuk lintas tahun ke Jan 2027) — logika rollover bulan v5.0 tetap utuh.

### Simulasi atas data nyata

Jalan **05 Aug 2026** (sebelum Rollout 11 Aug → THIS MONTH = Aug 2026, Ver 2.20.0):

```
Total Project 17 | On Going UAT 4 | Completed UAT 6 | Done Implement 1
📈 Coverage UAT  : 🟢 3  🟡 0  🔴 1     (= 4 = On Going UAT ✔)
🎯 Go-Live       : 🟢 0  🟡 0  🔴 17    (= 17 = Total Project ✔)
⚠️ Attention     : 🔴 Track 14 (67%), NEXT MONTH 🟡 Track 10 (99%)
```

Jalan **19 Aug 2026** (sesudah Rollout → THIS MONTH = Sep 2026, Ver 2.21.0):

```
Total Project 15 | On Going UAT 4 | Completed UAT 4
📈 Coverage UAT  : 🟢 3  🟡 1  🔴 0
🎯 Go-Live       : 🟢 0  🟡 0  🔴 15
```

---

## ⚠️ Perlu diperhatikan

**1. `% Regresi Overall` hampir seluruhnya kosong.**
Akibatnya Go-Live Readiness menampilkan 🔴 Not Ready = seluruh project, 🟢 Ready = 0. Secara formula ini **benar** (belum ada angka regresi = belum siap go-live), tapi angkanya baru akan informatif setelah kolom `% Regresi Overall` diisi. Kalau nanti mau blank Regresi diperlakukan berbeda, cukup ubah satu ekspresi.

**2. Baris 141 dan 147 `% UAT Overall` rumusnya rusak.**
Keduanya hardcoded `=AO114`, jadi ikut nilai baris 114 (99,46%) alih-alih progres sendiri. Ini masalah di Excel, bukan di flow — perlu diperbaiki di sheet.

**3. Kolom K (`Estimated Implementation`) masih rusak sebagian.**
Warisan v5.0: dari 414 baris, 132 baris bernilai `#VALUE!` karena lookup ke `TableMasterSuperfile` gagal (tabel itu cuma punya 282 baris, dan lookup-nya posisional bukan by-key). Baris tersebut ter-skip otomatis.

**4. Backslash di nama project bisa merusak Kartu 2 (bug bawaan v5.0).**
v5.0 meng-escape kutip ganda, tab, CR, dan LF — tapi **tidak** backslash. Satu saja nama project yang mengandung `\` akan membuat Adaptive Card gagal di-parse dan flow error. Sudah diperbaiki di section baru Kartu 1 (dan Kartu 3 ikut aman karena blok Attention-nya pindah), tapi **Kartu 2 masih rentan** karena tidak boleh disentuh di rilis ini. Saat ini tidak ada nama project yang mengandung backslash, jadi belum menggigit. Bilang saja kalau mau sekalian ditambal.

---

## Checklist sebelum go live

- [ ] Import package → pilih **Create as new** (jangan Update, biar v5.0 tetap ada)
- [ ] Pasang koneksi Excel Online (Business) dan Microsoft Teams
- [ ] Cek trigger: Jumat 20:00 SE Asia Standard Time (warisan v5.0)
- [ ] Test run manual, pastikan 3 kartu masuk berurutan ke group chat
- [ ] Cek silang: 🟢+🟡+🔴 Coverage UAT harus sama dengan angka "On Going UAT"
- [ ] Cek silang: 🟢+🟡+🔴 Go-Live harus sama dengan "Total Project"
- [ ] Setelah kolom Q terisi, pastikan angka Critical Defect muncul menggantikan `—`
- [ ] Matikan v5.0 setelah V6.0 dikonfirmasi jalan
