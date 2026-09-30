---
name: n8n-error-code-node-dipotong-titik-dua
description: "Pesan error yang di-throw node Code n8n dipotong formatter (titik dua, baris baru; tergantung versi) sebelum sampai ke error output — penanda/alasan wajib satu baris tanpa ':'"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 42e8cf04-5640-4495-ae07-179864fd0550
  modified: 2026-09-13T13:57:52.107Z
---

`throw new Error(msg)` di node Code n8n TIDAK sampai utuh ke error output (`$json.error`). n8n
membungkusnya dengan `ExecutionError` yang menyusun ulang pesan dari baris stack yang memuat `Error:`,
lalu menambah ` [line N]`. Aturannya beda per versi (dicek dari kode sumber n8n, 2026-09-13):

- nodes-base Code s/d 2025-06 dan task-runner s/d 2026-08-26: `split(':').reverse()`, jadi yang
  tersisa hanya teks **setelah titik dua terakhir** di baris pertama. **Ini perilaku n8n live PCR.**
- nodes-base Code 2025-06+: dipotong di `': '` pertama setelah `Error: `.
- task-runner 2026-08-26+ (master): pesan baris pertama utuh.
- Semua versi: hanya **baris pertama** yang terbawa.

Kejadian nyata: `FU_AI_INVALID: tenor :: <pesan>` di workflow Follow-up AI Powered sampai ke notif
admin sebagai `<pesan> [line 60]`, jadi alasan penolakannya hilang. Buktinya: potongan di notif
tepat 160 char (= `pesan.slice(0,160)`).

**Why:** logika hilir yang membaca penanda di teks error (rollback, laporan) gagal diam-diam, dan
hasilnya berubah begitu n8n di-upgrade.

**How to apply:** kalau node hilir perlu membaca penanda dari error node Code, tulis pesannya
**satu baris tanpa `:`** (`.replace(/[:\r\n]+/g,' ')`), letakkan penanda di depan, dan batasi
panjangnya sebelum dipotong node lain. Uji dengan port 4 formatter di
`scratchpad/harness.js` (`fmtF1`–`fmtF4`) dari sesi 2026-09-13. Rancang supaya kalau penanda
hilang, sistem jatuh ke perilaku lama (fail-safe).

Terkait: [[laptop-tanpa-runtime-js]], [[n8n-referensi-node-mati]], [[persada-cisoka-status]]
