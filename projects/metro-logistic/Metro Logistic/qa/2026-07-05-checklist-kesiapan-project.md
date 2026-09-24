# Checklist Kesiapan Project — Metro Logistik Tracking PWA
**Disusun oleh:** Fable (PM/QA Lead) · **Tanggal:** 5 Juli 2026 · **Referensi standar:** Shopee Express, JNE, J&T

Legenda: ✅ Siap · ⚠️ Siap dengan catatan · ⬜ Menunggu tindakan Steven

## 1. Dokumen & Rancangan (Sonnet)
| # | Item | Status |
|---|------|--------|
| 1.1 | Arsitektur komponen frontend PWA (`docs/2026-07-05-arsitektur-frontend-pwa.md`) | ✅ |
| 1.2 | Wireframe & design system publik + admin (`docs/2026-07-05-wireframe-uiux.md`) | ✅ |
| 1.3 | Skema Google Sheets + kontrak Riwayat_Posisi_JSON (`docs/2026-07-05-skema-database-google-sheets.md`) | ✅ |
| 1.4 | Kontrak API WF1/WF2 konsisten antara docs, frontend, dan n8n | ✅ diverifikasi QC |

## 2. Frontend PWA (Opus)
| # | Item | Status |
|---|------|--------|
| 2.1 | `app/index.html` — cek resi multi-item, filter tanggal/status | ✅ |
| 2.2 | Timeline vertikal berundak ala Shopee/JNE (terbaru di atas, waktu+status+lokasi+admin) | ✅ |
| 2.3 | `app/admin.html` — form resi/nama admin/dropdown status/lokasi | ✅ |
| 2.4 | Validasi field wajib + tolak spasi-saja (nama admin dll.) | ✅ |
| 2.5 | Anti-XSS: semua data API di-escape sebelum masuk DOM | ✅ diverifikasi QC |
| 2.6 | `manifest.json` (standalone, ikon 192/512 + maskable + apple-touch-icon) | ✅ |
| 2.7 | `sw.js` — cache-first shell, network-first API, precache versioned | ✅ |
| 2.8 | Antrean offline admin (IndexedDB + client_id anti-duplikat, auto-flush saat online) | ✅ |
| 2.9 | Ikon brand | ⚠️ placeholder "M" — ganti aset brand final |
| 2.10 | `app/js/config.js` — URL webhook n8n | ⬜ isi URL asli setelah deploy n8n |

## 3. Backend n8n
| # | Item | Status |
|---|------|--------|
| 3.1 | WF1 Get Data (multi-resi, parse riwayat aman, CORS) | ✅ |
| 3.2 | WF2 Update Data (validasi, append riwayat real-time by row) | ✅ setelah QC-fix respond node |
| 3.3 | WF3 Housekeeping (cron 60 hari, arsip >30 hari pasca-Delivered, archive-dulu-baru-hapus, delete descending) | ✅ setelah 2 QC-fix keamanan data |
| 3.4 | Semua JSON valid + semua jsCode lolos syntax check | ✅ |
| 3.5 | Spreadsheet Utama & Archive dibuat + placeholder ID diganti | ⬜ Steven |
| 3.6 | Credential Google Sheets di n8n | ⬜ Steven |

## 4. Deploy & Go-Live
| # | Item | Status |
|---|------|--------|
| 4.1 | Hosting statis HTTPS (wajib untuk service worker) | ⬜ |
| 4.2 | Uji install PWA di Android (Chrome) & iOS (Safari, Add to Home Screen) | ⬜ setelah deploy |
| 4.3 | Jalankan QA Testing Matrix (`qa/2026-07-05-qa-testing-matrix.md`) di staging | ⬜ |
| 4.4 | Simulasi housekeeping dengan sheet dummy SEBELUM mengaktifkan WF3 di produksi | ⬜ wajib |
| 4.5 | Proteksi halaman admin (minimal: URL tidak dipublikasikan; disarankan: token sederhana di WF2) | ⚠️ direkomendasikan sebelum go-live |
