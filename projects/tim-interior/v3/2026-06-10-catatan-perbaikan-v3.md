# Catatan Perbaikan — TIM Interior v3 (2026-06-10)

## Ringkasan
Perbaikan bug webform `webform_v3_final` + penyelarasan database ke workflow n8n.
Semua perubahan sudah melewati QA otomatis (18/18 tes lolos, headless jsdom + cek sintaks).

## Masalah yang diperbaiki

| # | Masalah | Akar masalah | Perbaikan |
|---|---------|--------------|-----------|
| 1 & 5 | Cek Pekerjaan error / tidak bisa dipakai | Fungsi `delay()` dipakai 4× tapi **tidak pernah didefinisikan** → setiap "Cari Pekerjaan" melempar ReferenceError | Menambahkan `function delay(ms)` |
| 6 | Generate RAB/Checklist tak menampilkan layar | Seluruh blok `<div id="screen-rab-checklist">` **terjebak di dalam string template `_printRAB`** → screen tidak ada di DOM, `goto('rab-checklist')` crash | Mengeluarkan screen ke `<body>`, memperbaiki penutup template `_printRAB` |
| 3 | Tidak ada layar loading saat submit | Overlay hanya transparan gelap tanpa indikator | Overlay kini menampilkan **spinner + teks** ("Menyimpan pekerjaan...", "Mengirim komplain...", dst). Diterapkan ke semua aksi: simpan pekerjaan, kirim komplain, update status, cari pekerjaan, generate RAB/checklist |
| 2 | Input tidak ter-reset tiap buka halaman | (sebelumnya screen crash sehingga init tak jalan) | Setiap `goto()` menjalankan `init*()` yang mengosongkan semua field secara default |
| 4 | Sheet database lama masih ada | DB baru tidak sinkron dengan workflow | Lihat bagian Database di bawah |

## Perbaikan tambahan saat QA
- `_fetchRABData` (menu RAB/Checklist) sebelumnya **tidak punya cabang TEST_MODE** sama sekali — selalu `fetch`, jadi tak bisa dipakai standalone. Ditambahkan dukungan TEST_MODE pakai data demo.
- Variabel CSS `--text-1` / `--text-2` dipakai tapi belum didefinisikan → ditambahkan ke `:root`.
- `TEST_MODE = true` agar webform bisa langsung diuji tanpa server. **Ganti ke `false`** setelah endpoint n8n v3 live (baris ~1493 di `index.html`).

## Database (Issue 4)
DB lama `TIM Interior.xlsx` (sisa v2: tab Database, Update_History, PIC_Mandor, PIC_Pengawas) **dihapus** — cadangan ada di `_arsip/`.

`TIM_Interior_V3.xlsx` dibangun ulang agar **persis cocok dengan skema workflow n8n** (header di baris 1, tanpa baris judul yang merusak deteksi header n8n):

| Tab | Kolom |
|-----|-------|
| Pekerja | Nama, No_HP, Keterangan |
| Pekerjaan | Batch_ID, Tanggal, Proyek, Pekerja, Catatan, No_Item, Pekerjaan, Vol, Sat, Harga_Satuan, Total_Item, Total_Keseluruhan, Timestamp_Submit |
| PekerjaanStatus *(baru — tadinya hilang)* | Batch_ID, No_Item, Status, Updated_At |
| Komplain *(kolom diluruskan)* | ID, Tanggal, Proyek, Pengaju, Komplain, Lokasi, Prioritas, Status, Timestamp |
| Project *(dari "Projects")* | Project, Keterangan |

> Catatan: data produksi sebenarnya ada di Google Sheets (lewat n8n). File `.xlsx` ini adalah template/acuan — pastikan **nama tab & kolom di Google Sheet hidup sama persis** dengan tabel di atas.

## File yang dibuat / diubah
- **Diubah:** `v3/webform_v3_final/webform v3/index.html` (semua perbaikan webform)
- **Diubah:** `v3/webform_v3_final.zip` (di-zip ulang dari folder yang sudah diperbaiki)
- **Dibangun ulang:** `v3/TIM_Interior_V3.xlsx`
- **Dihapus:** `v3/TIM Interior.xlsx` (cadangan di `_arsip/2026-06-10-TIM-Interior-v2-OLD.xlsx`)
- **Dibuat:** `v3/_arsip/` (cadangan DB lama & versi xlsx sebelum perbaikan)
- **Dibuat:** dokumen catatan ini

---

## Perbaikan workflow n8n (update 2 — setelah deploy live)

Gejala: `Cek Pekerjaan` dan `Generate RAB` error **"Unexpected end of JSON input"** (respons webhook kosong).

### Akar masalah
Semua webhook pakai `responseMode: responseNode` → wajib mencapai node *Respond to Webhook*. Di n8n, **node Code yang menerima 0 item akan di-skip**, sehingga node Respond tidak pernah menerima data dan webhook membalas **body kosong**. Ini terjadi saat:
- Tab **PekerjaanStatus kosong** (belum ada update status) → `GS - Baca Status Pekerjaan` keluarkan 0 item → `Code - Filter dan Group Pekerjaan` di-skip → `get-pekerjaan` balas kosong.
- Tab **Komplain kosong** → `Code - Filter Komplain` di-skip → `get-komplain` balas kosong.

### Perbaikan
1. **`alwaysOutputData = true`** pada semua node GS read yang memberi makan rantai Code→Respond: `GS - Baca Komplain`, `GS - Baca Semua Pekerjaan`, `GS - Baca Status Pekerjaan`, `GS - Baca Semua Pekerja`, `GS - Baca Projects`. → walau sheet 0 baris, tetap mengalirkan 1 item kosong sehingga Code node tetap jalan dan mengembalikan `{"success":true,"count":0,"data":[]}` (JSON valid).
2. **Node `Respond - Get Komplain Error` yang menggantung** kini tersambung: `GS - Baca Komplain` diberi error-output (`onError: continueErrorOutput`), output error → `Respond - Get Komplain Error` (balas HTTP 500 JSON bila baca Sheet benar-benar gagal).

### Hasil QA n8n (otomatis)
- JSON valid, 72 node.
- **9/9 webhook** mencapai node Respond di **setiap** cabang.
- **0 node Respond menggantung**, 0 dead-end.
- Simulasi Code node dengan input kosong → JSON valid (bukan body kosong).

> ⚠️ Setelah meng-impor ulang JSON ke n8n: **aktifkan workflow** dan pastikan kredensial Google Sheet + `documentId` benar. Untuk Google Sheet hidup, header harus di **baris 1** dan nama tab persis: `Pekerja, Pekerjaan, PekerjaanStatus, Komplain, Project`.

## Perbaikan workflow n8n (update 3 — TypeError .trim)

Gejala: `Code - Filter Komplain` error **`(r.Lokasi || "").trim is not a function`**.

Penyebab: sebagian sel Google Sheet terbaca sebagai **angka** (mis. Lokasi/Prioritas berisi angka), dan `.trim()` tidak ada pada number.

Perbaikan: semua pemanggilan `.trim()` atas data sheet/body kini dibungkus `String(...)` — **25 titik di 7 Code node** + 4 titik di `Code - Validate dan Expand` (total aman). Diverifikasi: 0 error sintaks di semua Code node, 0 `.trim()` rawan tersisa.

## Perbaikan UX cek pekerjaan & komplain (update 4)

1. **Filter komplain ikut nama pekerja** — sebelumnya semua komplain muncul. Kini komplain difilter `pengaju === pekerja` yang dicari.
2. **Kartu komplain dibuat mirip kartu pekerjaan** (layout sama, penanda halus: garis kiri oranye + tag "KOMPLAIN", **tidak merah pekat lagi**), dan **bisa update status** (Open / Proses / Selesai) seperti pekerjaan.
3. **Tombol "Generate RAB" dihapus** dari hasil cek pekerjaan (tinggal "Generate Checklist"). Menu RAB terpisah tetap ada.
4. **Checklist**: komplain kini punya **kotak centang ☐**, dan warnanya dibuat lembut (krem/emas), tidak merah.
5. **Endpoint n8n baru** `POST /v3/update-komplain-status` (additif) untuk menyimpan status komplain ke kolom Status di sheet Komplain (match by ID). Webform mengarahkan update pekerjaan ke `/v3/update-status` dan update komplain ke endpoint baru ini.

QA: webform 13/13 tes fitur baru lolos + 17/18 regresi (1 "fail" = tombol RAB yang memang sengaja dihapus). n8n: 10/10 webhook mencapai Respond, 0 orphan, JSON valid.

> Catatan teknis: file `index.html` sempat terpotong oleh tool edit (file besar), sudah dipulihkan utuh & diverifikasi (`</script>` + service worker + `</html>` lengkap). Arsip ZIP terbaru: **`webform_v3_final_2026-06-10.zip`** (ZIP lama `webform_v3_final.zip` tidak ter-refresh karena glitch mount — abaikan, pakai yang bertanggal).

## File yang dibuat / diubah (lengkap)
- `v3/webform_v3_final/webform v3/index.html` — perbaikan webform (diubah)
- `v3/webform_v3_final.zip` — di-zip ulang
- `v3/TIM_Interior_V3.xlsx` — dibangun ulang sesuai skema
- `v3/TIM_Interior_v3_n8n_Workflow.json` — **diperbaiki** (alwaysOutputData + wiring respond error)
- `v3/TIM Interior.xlsx` — dihapus (cadangan di `_arsip/`)
- `v3/_arsip/` — cadangan DB lama, xlsx & workflow sebelum perbaikan
