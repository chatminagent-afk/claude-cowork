# GLOBAL — panduan migrasi rantai "WA error"

Kerjakan folder ini **lebih dulu** dari klien mana pun. Notifier error adalah yang memberitahumu kalau migrasi klien gagal; kalau ia sendiri masih memanggil Kirimi lewat IP yang diblokir, kegagalan jadi senyap.

## File di folder ini

| File | Node | Peran |
|---|---|---|
| `2026-08-31-GLOBAL-VIRA-Error-Notifier-Fonnte.json` | 7 | Lapis 1 — notifikasi WA saat workflow mana pun gagal |
| `2026-08-31-GLOBAL-Email-Fallback-Notifier-Fonnte.json` | 10 | Lapis 2 — email saat WA gagal. Tidak memanggil API WA |
| `2026-08-31-GLOBAL-Sheet-Cleanup-Fonnte.json` | 18 | Laporan maintenance harian/kuartalan |

`VIRA Dashboard API` dan `DASH_AUDIT Cleanup` tidak menyentuh WA — biarkan.

## Checklist

- [ ] Device Fonnte untuk notifikasi (boleh device yang sama dengan salah satu klien).
- [ ] Credential Header Auth, Name `Authorization`, Value token tanpa `Bearer`. Nama persis: **`Fonnte - GLOBAL Notif`**.
- [ ] Import ketiga file, pilih credential di node yang merah.
- [ ] `GLOBAL - Sheet Cleanup` punya trigger `Test manual` (mode dry run) — pakai itu untuk uji tanpa efek samping.
- [ ] Uji notifier: picu error sengaja di salah satu workflow, pastikan WA masuk **dan** label klien benar.
- [ ] Setelah lolos, arahkan `settings → Error Workflow` tiap workflow klien ke notifier versi Fonnte.
- [ ] Nonaktifkan notifier versi Kirimi.

## Satu perubahan perilaku yang perlu kamu tahu

Notifier lama memilih **perangkat WA pengirim per tenant**: error TS dikirim dari device `D-4ZV1F`, error PCR dari `D-LM6WE`. Dengan Fonnte, autentikasi pindah ke n8n Credential, jadi **satu device mengirim semua notifikasi error**.

Yang hilang hanya *dari nomor mana* notifikasi datang. Yang tidak hilang: label klien (`The Scholars` / `Persada Cisoka Residence` / `Global`) tetap tercetak di baris pertama pesan, dan pemetaan `WF_MAP` workflow-id → tenant tetap utuh. Jadi kamu tetap tahu klien mana yang bermasalah, hanya tidak lagi bisa membedakannya dari warna chat.

Kalau kamu ingin pemisahan itu kembali, butuh satu credential Fonnte per tenant plus node Switch di depan `Notify Admin Error`. Menurutku tidak sepadan — tujuan notifikasi selalu nomormu sendiri.

## Email fallback

`GLOBAL - Email Fallback Notifier` tidak memanggil API WhatsApp, jadi sebetulnya tidak wajib dimigrasi. Yang diubah hanya dua baris supaya ia menerima payload dari notifier versi Fonnte **maupun** versi Kirimi:

- `d.source === 'kirimi_fallback' || d.source === 'fonnte_fallback'`
- `d.fonnte_response || d.kirimi_response`

Artinya tidak ada urutan import yang wajib, dan selama masa transisi kedua versi notifier tetap terlayani.

## Yang belum tertutup

Rantai ini menangkap kegagalan *pengiriman*. Ia tidak menangkap pesan yang diterima Fonnte lalu mati di antrean — Fonnte membalas `status: true` dengan `process: pending`, dan itu dianggap sukses. Penutupnya webhook *update message status* Fonnte, belum dikerjakan. Selama itu belum ada, celah "pesan hilang diam-diam" masih ada, hanya berpindah dari n8n ke antrean Fonnte.
