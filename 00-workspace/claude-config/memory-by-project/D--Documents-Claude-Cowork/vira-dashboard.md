---
name: vira-dashboard
description: "Dashboard multi-tenant VIRA — keputusan arsitektur, status deploy, dan hal yang masih menunggu keputusan Steven"
metadata: 
  node_type: memory
  type: project
  originSessionId: c210a9ba-75c6-44ea-854d-aaab95614c81
  modified: 2026-08-28T10:10:20.996Z
---

Dashboard performa + direktori lead untuk bot VIRA, melayani **The Scholars** dan **Persada Cisoka Residence** dari satu kode. Selesai dibangun 2026-07-28 di `D:\Documents\Claude Cowork\VIRA\VIRA-DASHBOARD\2026-07-28-production\`. Draft lama di `VIRA-DASHBOARD/` (index.html + folder `2026-07-07-patch-V4-compat/`) **usang** — patch itu kalau di-deploy justru meregresi ke arsitektur PIN+Apps Script tanpa tab CRM/Mock/Insights.

Keputusan arsitektur (dipilih Steven 2026-07-28):
- Frontend statis zero-build (mesin Steven **tidak punya Node/npm**) + satu workflow n8n `VIRA Dashboard API` (webhook `/vira-dash`, 30 node) sebagai backend. n8n instance bersama untuk kedua klien: `https://n8n.srv1270416.hstgr.cloud`
- Isolasi tenant: token HMAC-SHA256 (node Crypto n8n) berisi `tenant|role|exp`; **spreadsheet ID tidak pernah keluar dari n8n**; hak akses diperiksa ulang ke registry server tiap request, bukan sekadar percaya isi token
- Genericity: server mengirim *deskriptor* (label kolom, judul chart, tipe), frontend buta terhadap tenant → tambah klien ke-3 = 1 entri di `n8n/src/tenants.js`, nol perubahan frontend. Dijaga oleh `qa/validate_workflow.py` yang menolak build kalau nama klien/kolom spesifik muncul di `app/`
- **Service account Google terpisah** khusus dashboard (kuota Sheets dihitung per-user; bot Persada sudah dekat plafon 60 read/menit)
- **Toggle global dihilangkan dari UI** — `CONFIG.VIRA_STATUS` tidak dibaca node mana pun di V4 maupun PCR, jadi tombolnya akan berbohong. Toggle per-user berfungsi penuh
- Hosting: Cloudflare Pages/Netlify. Chart digambar sendiri sebagai SVG (nol dependensi eksternal)
- Kode Code node n8n **di-generate** dari `n8n/src/*.js` oleh `build_workflow.py` — jangan edit lewat UI n8n

Menunggu keputusan Steven (ditulis di `docs/2026-07-28-konsultasi-rekomendasi.md`):
1. **Rotate service account Persada** — private key RSA plaintext tersimpan di tab CONFIG `PCR_Database` (T1, kritis)
2. Konfirmasi apakah fitur pending-survey PCR terasa tidak jalan — 3 kolom `pending_survey_*` di STATS punya trailing space, kodenya membaca tanpa spasi (T5)
3. Angka target traffic Persada — menentukan jadwal migrasi STATS ke Postgres
4. Izin mengarsipkan draft dashboard lama

Bahasa visual (redesain 2026-08-28, folder `app revamp/`): **monokrom**. Ramp netral 5 langkah `--n-1`…`--n-5` (n-1 = paling kontras di kedua tema) jadi tulang punggung; hanya tiga warna berkroma yang boleh hidup — `--tone-blue` (aksen merek/tenant: tombol, border aktif, dot status, seri chart pertama), `--tone-red` (galat/destruktif), `--warn` (spanduk mode uji saja). Jangan menambah tone dekoratif baru. Chart mengikuti bklit UI: kurva monotone Fritsch–Carlson, gradasi area 0.32→0, grid horizontal putus-putus 4,4, reveal clip-path 1100ms, crosshair memudar di ujung + date pill. Semua 10 warna seri sudah diverifikasi lolos kontras 3:1. `charts.js` sengaja MENGABAIKAN nama warna dari payload n8n.

Path `app/` sudah tidak ada — semua tooling menunjuk `app revamp/`. Empat berkas dulu masih menunjuk `app/` sehingga diam-diam tidak menguji apa pun (selftest, uitest, build_demo, validate_workflow); sudah diperbaiki 2026-08-28. Harness chart tanpa login: `qa/preview-charts.html`.

Belum diuji terhadap n8n sungguhan: node Crypto, `Loop Over Tabs`, `documentId` dinamis, ketepatan baris saat menulis `bot_mode`. Checklist smoke test wajib ada di §8 `docs/2026-07-28-UAT-report.md`.

Terkait: [[persada-cisoka-residence]]
