# VIRA V4 — Manual Deploy

Urutannya penting: **Google Sheet dulu, baru import n8n, baru aktivasi.** Estimasi total ±20 menit + testing.

## Langkah 1 — Penyesuaian Google Sheet (SEBELUM import)

Di spreadsheet `The_Scholars_Database` (`1tEJ…CwE`):

1. **Buat tab baru bernama persis `MSG_BUFFER`** dengan header di baris 1 (kolom A–D):
   `no_wa` | `lid` | `message` | `ts`
2. **Tab STATS — tambah 5 kolom baru** di kanan kolom `lid` (nama header harus persis):
   `kelas_anak` | `kelas_anak_ts` | `program_interest` | `buffer_done_ts` | `last_reply_ts`
3. **JANGAN hapus kolom `pending_msg` dan `user_status` dulu** — sudah tidak dipakai V4, tapi biarkan 1–2 minggu sebagai arsip/rollback. Hapus nanti setelah stabil.
4. Opsional (dianjurkan, bersih-bersih data lama): ±7 row yang kolom `No WA`-nya berformat `1234…@lid` → pindahkan angkanya ke kolom `lid` dan isi `No WA` dengan digit saja (tanpa `@lid`). Ini mencegah row duplikat untuk user lama tersebut.

## Langkah 2 — Import di n8n

1. Import `2026-07-02-VIRA_V4.json` sebagai **workflow baru** (jangan menimpa workflow lama — biarkan yang lama sebagai rollback). V4 ter-export dalam kondisi **inactive**.
2. Buka node **Append MSG_BUFFER** dan **Read MSG_BUFFER**: pastikan Document & Sheet ter-resolve. Kalau field Sheet merah/kosong, pilih ulang `MSG_BUFFER` dari dropdown (tab harus sudah dibuat di Langkah 1). Jangan rename tab ini di kemudian hari — node mereferensi by name.
3. Scan cepat: tidak ada node merah; credential `Google Service Account thescholars` ter-attach di semua node Sheets (harusnya otomatis karena ID credential sama).
4. Import `2026-07-02-VIRA_V4-error-workflow.json` ("VIRA Error Notifier") → **aktifkan**.
5. Di workflow **VIRA V4** → Settings (⚙) → **Error Workflow** → pilih "VIRA Error Notifier".

## Langkah 3 — Aktivasi mode testing

PENTING: VIRA lama dan V4 memakai path webhook yang sama (`wa-inbound`) — **jangan pernah dua-duanya aktif bersamaan**.

1. Di VIRA V4: **enable node `IF (Whitelist)`** (klik kanan → Activate) supaya hanya nomor tim yang diproses selama testing.
2. **Nonaktifkan workflow VIRA lama**, lalu **aktifkan VIRA V4**.

## Langkah 4 — Test checklist (pakai nomor whitelist)

| # | Test | Ekspektasi |
|---|------|------------|
| 1 | Chat dari nomor yang belum ada di STATS: "halo, program untuk anak kelas 8 apa?" | Intro "Sam versi AI" verbatim + jawaban Intermediate di pesan yang sama; tanpa "kamu"/vokatif; `greeting_sent=Y`, row STATS baru terbentuk dengan `kelas_anak=SMP 2` |
| 2 | Kirim pesan kedua dari nomor sama | TIDAK ada intro lagi |
| 3 | Kirim 3 pesan beruntun (<10 detik antar pesan) | 3 row muncul di MSG_BUFFER; SATU balasan yang menjawab ketiganya; `buffer_done_ts` terisi |
| 4 | Pancing frasa dulu-bermasalah: "oke ditunggu ya kabari kalau sudah dicek" | Balasan normal, BUKAN "Maaf, terjadi kesalahan" |
| 5 | Tanya lanjutan tanpa sebut kelas (setelah test 1): "kalau biayanya?" | Bot tidak tanya kelas lagi (pakai kelas_anak tersimpan); aturan harga batch tetap berlaku |
| 6 | "anak saya mau naik sec 3" | Diarahkan ke Intermediate, TANPA asumsi "sudah sekolah di Singapura" |
| 7 | Set `bot_mode=OFF` di STATS (cari via No WA) lalu chat | Bot diam total |
| 8 | Set `bot_mode=ON` lagi, chat baru | Bot balas normal; pesan era OFF tidak ikut kebawa |
| 9 | Ketik "mau ngomong sama Sam" | Balasan handoff + notif WA ke admin + `bot_mode` jadi OFF |
| 10 | Simulasi error (opsional): ubah sementara URL node Reply Chat Kirimi jadi salah, kirim pesan | Admin dapat WA dari "VIRA Error Notifier"; kembalikan URL setelahnya |

Cek juga sheet STATS setelah test 1–5: `Tanggal Chat Pertama` TIDAK berubah-ubah lagi di pesan berikutnya, `last_reply_ts` terisi, kolom `timestamp` berisi angka milidetik (13 digit — normal, itu kunci debounce).

## Langkah 5 — Go publik

Semua lolos → **disable kembali node `IF (Whitelist)`** di VIRA V4. Selesai.

## Rollback

Ada masalah → nonaktifkan VIRA V4, aktifkan kembali workflow lama. (Kolom/tab baru di sheet tidak mengganggu workflow lama.) Kirim laporan masalahnya ke saya untuk dianalisa.

## Catatan operasional

- **Setiap save/edit workflow di editor n8n me-reset Simple Memory** (konteks percakapan berjalan). Kolom `kelas_anak`/`program_interest` adalah pengaman-nya — fakta inti tetap ada. Usahakan deploy patch di jam sepi.
- **MSG_BUFFER menumpuk** ±1 row per pesan masuk. Bersihkan manual sebulan sekali (hapus row-row lama, sisakan header). Ini aman kapan pun.
- **Follow-up workflow** (jika ada yang membaca kolom `timestamp` STATS untuk deteksi inaktivitas): arahkan ke `last_reply_ts` — kolom `timestamp` kini eksklusif milik mekanisme debounce.
- **Kirimi**: kasus pesan ke-2 Adrian (28/6) terbukti tidak pernah sampai ke n8n. Kalau keluhan "pesan tidak dibalas" masih muncul setelah V4, cek riwayat delivery di dashboard Kirimi / tanyakan ke support Kirimi soal pesan beruntun cepat — itu di luar jangkauan workflow.
- **Keamanan (jadwalkan segera):** secret Kirimi masih plaintext di node HTTP (termasuk di error workflow baru). Rotasi secret di dashboard Kirimi → simpan sebagai n8n Credential → update node. Webhook `wa-inbound` juga masih tanpa auth.
