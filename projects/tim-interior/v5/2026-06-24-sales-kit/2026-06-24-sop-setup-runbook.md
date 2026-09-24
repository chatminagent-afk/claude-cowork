# SOP Setup Klien Baru — Runbook
### Jasa Setup + Retainer Sistem Manajemen Proyek (basis v5)

> Tujuan: tiap klien baru bisa di-setup **cepat, konsisten, dan tanpa lupa langkah**. Ikuti urut. Target waktu: **2–3 hari kerja** dari DP masuk sampai go-live.

---

## ⚠️ Konsep penting sebelum mulai

v5 saat ini **menunjuk ke satu backend** (instance v4: satu Google Sheet, satu device WA, endpoint `/v4/...`). Untuk **klien berbayar**, tiap klien WAJIB punya instance sendiri agar datanya terpisah:

1. **Google Sheet sendiri** (salinan template 7-tab).
2. **Workflow n8n sendiri** (atau path endpoint unik per klien, mis. `/c-namaklien/...`) yang menunjuk ke Sheet klien itu.
3. **Device WhatsApp sendiri** (kirimi.id) untuk recap.
4. **Webform klien** yang `BASE_URL` / endpoint-nya diarahkan ke instance klien tersebut, dan `TEST_MODE = false`.

Jangan pernah memasang klien berbayar di backend v4 milik TIM Interior — datanya akan tercampur.

---

## FASE 0 — Pra-syarat (sebelum kerja teknis)

- [ ] Setup fee / DP minimal 50% sudah masuk.
- [ ] Dapat dari klien: nama studio, logo (jika paket Studio/Skala), daftar proyek aktif, daftar pekerja/PIC, nomor WA penerima recap.
- [ ] Tentukan kode klien singkat (mis. `studioaura`) untuk penamaan resource.

---

## FASE 1 — Google Sheet (±20 menit)

- [ ] Duplikat template Sheet 7-tab: `Tiket`, `RAB_Items`, `StatusLog`, `RAB_Budget`, `Pekerja`, `Project`, `Recipients`.
- [ ] Beri nama: `[KodeKlien] - Manajemen Proyek`.
- [ ] Isi tab `Project` dengan proyek aktif klien.
- [ ] Isi tab `Pekerja` dengan pekerja/PIC.
- [ ] Isi tab `Recipients` dengan nomor WA penerima recap (format `628xxxx`).
- [ ] Catat **Spreadsheet ID** (dari URL).
- [ ] Pastikan akun Google service (`Google Sheets account 2` atau kredensial khusus) punya akses edit ke Sheet ini.

---

## FASE 2 — Workflow n8n (±40 menit)

- [ ] Import workflow template (basis `2026-06-13-TIM-Interior-v4-n8n-HEMAT-READ-v2.json`).
- [ ] Ganti **docId / Spreadsheet ID** ke milik klien di semua node Google Sheets / HTTP batchGet/batchUpdate.
- [ ] Ubah path endpoint ke namespace klien (mis. `/c-studioaura/...`) **atau** pakai instance/folder terpisah — yang penting unik per klien.
- [ ] **GOTCHA wajib cek:** setiap webhook node yang menerima POST harus di-set `httpMethod: POST` eksplisit. Default n8n = GET → endpoint diam-diam ditolak ("no hit").
- [ ] **GOTCHA wajib cek:** tiap node Google Sheets set `retryOnFail` + `maxTries` + `waitBetweenTries` (kuota baca 60/menit/user → error 429 kalau tidak).
- [ ] Sesuaikan jadwal recap (08/13/19 WIB) jika klien minta jam lain.
- [ ] Aktifkan workflow.

---

## FASE 3 — WhatsApp (kirimi.id) (±15 menit)

- [ ] Siapkan device WA untuk klien ini (scan/registrasi di kirimi.id).
- [ ] Masukkan device ID ke node pengirim WA di workflow.
- [ ] Uji kirim 1 pesan tes ke nomor sendiri.

---

## FASE 4 — Webform (PWA) (±30 menit)

- [ ] Ambil salinan `v5/webform/`.
- [ ] Set **`const TEST_MODE = false;`** (sekitar baris ~1717 di `index.html`). **Ini langkah paling sering terlupa — wajib dicek.**
- [ ] Arahkan `BASE_URL` / endpoint ke instance n8n klien (path namespace klien).
- [ ] Paket Studio/Skala: ganti nama app di `manifest.json`, judul header, dan `logo.png` sesuai branding klien. Regenerate ikon PWA (72–512 + apple-touch + maskable) bila logo diganti.
- [ ] **GOTCHA editing:** `index.html` besar (~2900 baris) — Edit tool memotong file kalau banyak Edit beruntun (kehilangan `</script></body></html>`). Lebih aman edit via script string-replace Python, lalu verifikasi.
- [ ] Deploy seluruh isi folder ke hosting statis (Netlify / Vercel / cPanel / GitHub Pages) — semua file satu folder.

---

## FASE 5 — Uji end-to-end (±30 menit)

Dengan `TEST_MODE = false` (data nyata klien):

- [ ] **Dashboard** memuat 3 angka KPI & proyek klien benar.
- [ ] **Catat Pekerjaan** → Simpan → muncul di Cek & RAB.
- [ ] **Catat Komplain** → Kirim → tersimpan.
- [ ] **Cek Pekerjaan** → ubah status → Simpan → status tetap saat dicari ulang.
- [ ] **Generate RAB / Checklist** → jendela cetak muncul, bisa Save PDF.
- [ ] **+ Tambah Proyek / + Tambah Pekerja** → masuk ke dropdown & ke Sheet.
- [ ] **Recap WA**: jalankan manual sekali → pesan masuk ke penerima yang benar.
- [ ] Verifikasi setiap submit benar-benar menulis ke Sheet klien (bukan sheet lain).

---

## FASE 6 — Handover & training

- [ ] Kirim link webform + instruksi "Add to Home Screen".
- [ ] Paket Mulai: kirim video panduan. Paket Studio/Skala: sesi training live sesuai paket.
- [ ] Jelaskan alur harian: catat → cek status → recap WA otomatis.
- [ ] Serahkan kredensial yang relevan ke klien (akses Sheet sebagai pemilik data).
- [ ] Tagih pelunasan (jika DP) + aktifkan tagihan retainer pertama.

---

## FASE 7 — Aktifkan retainer & dokumentasi

- [ ] Catat klien di daftar internal: kode klien, Spreadsheet ID, namespace endpoint, device WA, tanggal go-live, paket, tanggal tagih retainer.
- [ ] Set pengingat tagihan retainer (bulanan/3-bulanan).
- [ ] Minta izin jadikan studi kasus/testimoni (terutama klien awal).

---

## Checklist MAINTENANCE bulanan (per klien)

- [ ] Cek workflow n8n aktif & tidak ada eksekusi gagal menumpuk.
- [ ] Cek recap WA tetap terkirim (device tidak logout).
- [ ] Cek tidak ada error 429 Google Sheets berulang.
- [ ] Tinjau permintaan/penyesuaian kecil dari klien.
- [ ] Pastikan tagihan retainer terkirim & terbayar.

---

## Daftar masalah umum & solusi cepat

| Gejala | Kemungkinan sebab | Aksi |
|---|---|---|
| Endpoint POST "no hit" | webhook node masih GET | set `httpMethod: POST` eksplisit |
| Error 429 saat recap/dashboard | kuota baca Google Sheets | pastikan `retryOnFail`/`maxTries`/`waitBetweenTries` aktif; pakai batchGet |
| Webform blank / JS error | `index.html` terpotong saat edit | rebuild via script, verifikasi `</script>`==1 & `node --check` |
| Recap WA tidak terkirim | device kirimi.id logout | scan ulang device, uji kirim |
| Data masuk ke sheet salah | docId belum diganti | cek semua node menunjuk Spreadsheet ID klien |
| Aplikasi pakai data demo | `TEST_MODE` masih true | set `TEST_MODE = false`, re-deploy |
