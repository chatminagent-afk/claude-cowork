# VIRA Control Panel — Panduan Deploy

Dibuat 2026-06-29. Panel kontrol VIRA (chatbot WA The Scholars): toggle on/off global, toggle per-user, dan dashboard analitik. Backend = Google Apps Script (akses Sheet aman, gratis). Frontend = PWA di Cloudflare Pages (bisa di-install di HP).

Arsitektur singkat:

```
HP / Browser (PWA, Cloudflare Pages)
        │   POST text/plain (anti-CORS)
        ▼
Google Apps Script Web App  ──►  Google Sheet The_Scholars_Database
        (cek PIN, baca/tulis)      ├─ CONFIG  (VIRA_STATUS = ON/OFF)  ← toggle global
                                    ├─ STATS   (kolom bot_mode)        ← toggle per-user
                                    └─ AUDIT_LOG (dibuat otomatis)     ← catatan aksi
n8n (VIRA workflow) baca CONFIG.VIRA_STATUS & STATS.bot_mode (sudah ada)
```

Total waktu setup ± 20 menit. Ikuti urut.

---

## BAGIAN A — Backend (Google Apps Script) ± 8 menit

1. Buka spreadsheet **The_Scholars_Database** di Google Sheets.
2. Menu **Extensions → Apps Script**.
3. Hapus isi `Code.gs` bawaan, lalu **paste seluruh isi** file `2026-06-29-vira-dashboard-Code.gs`.
4. Di bagian atas `CONFIG_APP`, ganti:
   - `PIN: '123456'` → **PIN rahasiamu** (mis. `'7421'`). Ini yang dimasukkan Sam saat buka panel.
   - `SPREADSHEET_ID` sudah terisi (`1tEJ…CwE`) — biarkan.
5. **Save** (ikon disket).
6. Jalankan tes: pilih fungsi `selfTest` di dropdown → **Run**. Pertama kali akan minta **Authorize** → izinkan akun Google pemilik sheet. Lihat **Execution log** harus muncul `getStatus -> {"ok":true,...}`. (Kalau muncul, akses Sheet sudah benar.)
7. **Deploy → New deployment**:
   - Klik gerigi → **Web app**.
   - Description: `VIRA Control`.
   - Execute as: **Me**.
   - Who has access: **Anyone**.  *(Wajib — supaya frontend bisa memanggil. Keamanan tetap dijaga oleh PIN.)*
   - **Deploy** → **Authorize** → salin **Web app URL** (akhirannya `/exec`).

> Setiap kali kamu ubah `Code.gs`, lakukan **Deploy → Manage deployments → Edit → Version: New version → Deploy** (jangan buat deployment baru, supaya URL tetap sama).

---

## BAGIAN B — Frontend (Cloudflare Pages) ± 7 menit

1. Buka file **`index.html`**, cari baris:
   ```js
   const API_URL = "PASTE_APPS_SCRIPT_WEB_APP_URL_HERE";
   ```
   Ganti dengan **Web app URL** dari Bagian A langkah 7. Save.
2. Login **dash.cloudflare.com → Workers & Pages → Create → Pages → Upload assets**.
3. Beri nama projek (mis. `vira-control`), lalu **upload semua file** di folder ini KECUALI file dokumentasi/JSON n8n. Yang di-upload cukup:
   - `index.html`
   - `manifest.webmanifest`
   - `sw.js`
   - `icon-192.png`
   - `icon-512.png`
4. **Deploy**. Cloudflare kasih URL `https://vira-control.pages.dev`.
5. Buka URL itu di browser → muncul layar PIN. Masukkan PIN → dashboard terbuka. ✅

> Update frontend nanti: tinggal upload ulang file yang berubah di project Pages yang sama.

---

## BAGIAN C — Install di smartphone (PWA)

**Android (Chrome):** buka URL Pages → menu ⋮ → **Add to Home screen / Install app**.
**iPhone (Safari):** buka URL → tombol **Share** → **Add to Home Screen**.

Ikon VIRA muncul di layar HP dan terbuka layar penuh seperti aplikasi.

---

## BAGIAN D — Patch n8n (toggle global) ± 5 menit

Ini yang membuat tombol global ON/OFF benar-benar menghentikan VIRA. Hanya **2 node baru**, disisipkan **setelah `IF (Whitelist)`** dan sebelum `Chat Counter`.

**Langkah:**
1. Di Google Sheet, buka sheet **CONFIG**, tambah 1 baris baru:
   | Key | Value |
   |-----|-------|
   | `VIRA_STATUS` | `ON` |
   *(Apps Script juga membuat baris ini otomatis saat pertama dipanggil, tapi lebih aman buat manual.)*

2. **Cara cepat (rekomendasi):** import workflow versi sudah-dipatch:
   - File `2026-06-29-VIRA-with-global-toggle.json` = salinan workflow LIVE + 2 node baru. **Tidak menimpa** VIRA.json asli.
   - n8n → **Import from File** ke workflow baru untuk uji, atau timpa setelah yakin.
   - Buka node **Read VIRA Config** → klik dropdown **Sheet** → pilih **CONFIG** (supaya gid ter-bind). Pastikan credential Google = *Google Service Account thescholars*.

3. **Cara manual** (kalau tak mau import ulang): pakai `2026-06-29-VIRA-toggle-nodes-snippet.json` — salin 2 node, paste ke canvas, lalu sambungkan:
   `IF (Whitelist) [true] → Read VIRA Config → IF VIRA Active`
   `IF VIRA Active [true] → Chat Counter`
   `IF VIRA Active [false] → (biarkan kosong = flow berhenti)`

4. **Save & Activate** workflow.

**Cara kerja:** tiap pesan masuk yang lolos whitelist, n8n baca CONFIG.VIRA_STATUS.
- `ON` → lanjut normal.
- `OFF` → flow berhenti di `IF VIRA Active`, VIRA tidak membalas siapa pun.

**Soal kuota Sheets:** hanya +1 read per pesan saat ON; saat **OFF flow berhenti lebih awal** sehingga 8–9 read downstream tidak terjadi (net lebih hemat). Karena whitelist sudah membatasi volume, aman. (Optimasi lanjutan: cache pakai `$getWorkflowStaticData` bila trafik naik — tanya aku kalau perlu.)

---

## Apa yang dipakai bersama (satu sumber kebenaran)

| State | Lokasi | Ditulis oleh | Dibaca oleh |
|-------|--------|--------------|-------------|
| Global ON/OFF | `CONFIG!VIRA_STATUS` | Dashboard | n8n + Dashboard |
| Per-user | `STATS!bot_mode` | Dashboard + n8n | n8n + Dashboard |
| Audit | `AUDIT_LOG` | Apps Script | (manual) |

---

## Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| Popup "API_URL belum diisi" | Lupa ganti API_URL | Edit index.html Bagian B-1 |
| Selalu "PIN salah" | PIN beda dgn Code.gs | Samakan `CONFIG_APP.PIN` |
| "Tidak bisa terhubung" | URL salah / deployment lama | Cek URL `/exec`, redeploy versi baru |
| Toggle sukses tapi VIRA tetap balas | Patch n8n belum dipasang/aktif | Pasang Bagian D, Activate |
| Dashboard kosong | Sheet STATS belum ada data | Normal kalau belum ada chat |
| Konversi GForm 0% | Kolom `gform_filled` belum diisi workflow (lihat catatan QA) | Cek node yang harusnya menandai gform terisi |
