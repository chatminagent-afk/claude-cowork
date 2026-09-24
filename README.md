# Claude Cowork — backup workspace Steven

Repo **private**. Susunan folder di sini dirapikan dari `D:\Documents\Claude Cowork`
(folder aslinya di laptop tidak diubah).

```
00-workspace/          CLAUDE.md, TASKS.md, konteks proyek, memory
  claude-config/       CLAUDE.md global + memory Claude (untuk restore di laptop baru)
n8n-workflows/         SEMUA workflow n8n VIRA, disusun per project — mulai dari sini (lihat README di dalamnya)
projects/
  vira/                skill, deck, sheet, docs, reels (naskah/tracker), threads, landing, dashboard
  the-scholars/        klien The Scholars
  persada-cisoka/      klien Persada Cisoka Residence
  tim-interior/        klien TIM Interior (v1–v5, webform, n8n)
  metro-logistic/      klien Metro Logistic
  bca/                 BIC 2026 / LUNA, Power Automate Ci Lenny
tools/
  claude-token-monitor/  monitor pemakaian token (tray app)
  kertas/                PWA Kertas
EXCLUDED.md            daftar file yang sengaja TIDAK ada di repo + alasannya
```

## Yang disensor / tidak dimasukkan
- Secret, token, dan private key diganti `REDACTED`. Isi ulang setelah restore (simpan aslinya di password manager).
- Tidak dimasukkan: service account key Google, `KREDENSIAL-*`, video/media, file >15–25 MB,
  spreadsheet/zip berisi banyak nomor HP (data pelanggan/kontak), file setting lokal.
- Yang tidak ada di sini → lihat `EXCLUDED.md`, backup terpisah (Drive / harddisk eksternal).

## Restore di laptop baru
1. `git clone` repo ini ke `D:\Documents\Claude Cowork\`.
2. Salin `00-workspace/claude-config/CLAUDE-global.md` → `C:\Users\<user>\.claude\CLAUDE.md`, dan isi `memory/` ke folder memory project.
3. Pasang ulang skill dari `projects/vira/skills/`.
4. Isi ulang secret (Kirimi, service account Google, dst.) dari password manager.
5. Ambil media/file besar dari backup Drive/harddisk sesuai `EXCLUDED.md`.
