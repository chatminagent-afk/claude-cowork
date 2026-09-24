# VIRA V4 — Changelog

**Tanggal:** 2 Juli 2026 · **Basis:** `production/VIRA.json` (export live 2 Juli) · **File:** `2026-07-02-VIRA_V4.json` (57 node) + `2026-07-02-VIRA_V4-error-workflow.json`
**QA:** simulasi fungsional (Process All, Preprocess, merge buffer, resolusi identitas) + syntax check 13 code node + review independen sub-agent (temuan MAJOR sudah di-fix). Workflow di-export dengan `active: false`.

## Ringkasan

V4 menyelesaikan seluruh temuan report production 1 Juli: pesan error palsu (filter over-strict), pesan user hilang (buffer non-atomik + timestamp debounce tertimpa), data user tertukar (matching lid), context hilang (memory volatil), plus permintaan client: alur tanya status orang tua/murid DIHAPUS TOTAL — semua balasan kini register netral, dan user baru menerima intro "Sam versi AI".

## 1. Alur status PARENT/STUDENT dihapus (permintaan client)

- **Node dihapus:** `IF Status Update Needed`, `Update User Status`.
- **System prompt:** bagian `# REGISTER`, `# STATUS`, ALUR langkah status, dan tag `[USER_STATUS]` dihapus. Diganti `# REGISTER NETRAL` (dilarang "kamu"/"Anda"/vokatif; merujuk calon murid dengan frasa netral; boleh ikut framing user, mis. user bilang "anak saya" → boleh balas "anaknya") dan `# INTRO USER BARU`.
- **Preprocess:** blok deteksi status dari pesan dihapus (sekaligus menghilangkan bug regex `anaknya` → STUDENT).
- **Process All:** parsing/fallback USER_STATUS dihapus; regex pembersih tag `[USER_STATUS:...]` dipertahankan sebagai safety net, begitu juga penghapus vokatif.
- **Sheet:** kolom `user_status` tidak lagi ditulis/dibaca (kolom dibiarkan sebagai arsip).

## 2. Intro user baru

- User baru = `greeting_sent ≠ Y` (bukan lagi berbasis status).
- `Cek_user_status` menyuntik instruksi intro verbatim client + "jawab pertanyaan user di pesan yang sama".
- `Update STATS - Greeting Flag` disederhanakan: set `greeting_sent=Y` dari flag `is_new_user` setelah reply sukses (bukan pattern-matching teks balasan yang rapuh).

## 3. Fix "Maaf, terjadi kesalahan" palsu (Process All)

- `internalKeywords` dipersempit ke frasa yang benar-benar menyebut sumber data (`berdasarkan faq`, `dari sheet`, `data terverifikasi`, `saya cek data`, dst.). Frasa percakapan normal (`saya cek`, `saya lihat`, `saya temukan`, `dari data`, `data yang ada`) DIBUANG dari daftar — dulu menghapus balasan valid 1 kalimat sampai kosong.
- Guard anti-kosong: jika filter mengosongkan output padahal AI punya jawaban → pakai versi sebelum filter (dengan penyelamatan isi setelah titik dua bila ada). Pesan error hanya untuk output AI yang benar-benar kosong.
- Balasan wajib [UNKNOWN] di prompt diubah ke "nanti saya cari tahu dan kabari" (menghindari frasa "saya cek").

## 4. Anti pesan hilang: MSG_BUFFER append-only + fix timestamp

- **Node baru `Append MSG_BUFFER`:** setiap pesan masuk = 1 row baru di tab `MSG_BUFFER` (append atomik — tidak ada lagi read-modify-write `pending_msg` yang bisa saling menimpa).
- **Node baru `Read MSG_BUFFER`:** pemenang debounce membaca semua row user, gabung urut `ts` dengan aturan: `ts > buffer_done_ts` (watermark) dan `ts ≤ process_start_ts` dan umur < 30 menit (pesan basi era bot-OFF tidak bocor ke konteks).
- **4 node `Delete_Pending_Msg*`** direpurpose: bukan mengosongkan `pending_msg`, tapi memajukan watermark `buffer_done_ts`.
- **FIX KRITIS `Update to STATS`:** berhenti menulis kolom `timestamp` (dulu menimpa kunci debounce milidetik dengan detik → pesan yang masuk saat post-processing bisa gagal debounce dan tidak dibalas siapa pun). Waktu balasan kini dicatat di kolom baru `last_reply_ts`. *Catatan: jika ada workflow follow-up yang membaca `timestamp`, arahkan ke `last_reply_ts`.*
- `Wait3` tetap 60 detik (komentar "8 detik" yang typo dibetulkan).
- Catatan: kasus pesan ke-2 Adrian terbukti tidak pernah sampai ke n8n (tanpa eksekusi) — itu isu delivery Kirimi, di luar workflow; mitigasi visibilitas via Error Workflow di bawah.

## 5. Fix identitas user (data tertukar Vivipoh/DSS)

- **Node baru `Resolve User Row`:** resolusi satu kali per eksekusi — No WA (phone) primer, kolom `lid` backup, terakhir No WA==lid untuk row lama; TANPA fallback `rows[0]`, TANPA match dengan kunci kosong. Identitas kosong → throw (tertangkap Error Workflow → notif admin).
- Semua node Sheets update/appendOrUpdate kini matching by `No WA` dengan `resolved_key` (dulu by `lid` — sumber data tertukar): Update Buffer, Update to STATS, Update Greeting, Update GForm Sent TS1, Update row in sheet, 4× Delete_Pending_Msg*.
- `HITL Check` & `Process Counter & Merge Data` pakai resolusi yang sama; `Re-Read STATS Debounce` filter by No WA; `Rate Limiter LID` pakai resolved_key.

## 6. Context/memory

- Kolom STATS baru `kelas_anak`, `kelas_anak_ts` & `program_interest`, ditulis otomatis oleh `Update to STATS` dari deteksi Preprocess (dengan fallback nilai lama — tidak menimpa dengan kosong), diinjeksi ke `[SYSTEM_DATA]` tiap pesan → kelas tidak ditanya ulang walau memory n8n ter-reset (restart/save workflow).
- **Multi-anak**: deteksi kelas kini menangkap SEMUA kelas dalam satu pesan (bukan berhenti di match pertama). Orang tua dengan >1 anak (kasus Venn, 3 Juli) tersimpan sebagai daftar (mis. "SMP 1, SD 6") dan konteks AI memetakan program per kelas — tanpa tanya ulang.
- **TTL 60 hari**: kelas tersimpan hanya diinjeksi jika tercatat ≤60 hari terakhir (`kelas_anak_ts`). Lewat itu dianggap kedaluwarsa (naik kelas/tahun ajaran baru) dan bot bertanya lagi — data basi tidak pernah bocor sebagai fakta.
- `Simple Memory`: sessionKey → `resolved_key` (stabil walau Kirimi kadang kirim lid, kadang nomor), window 10 → 20.

## 7. Pemahaman jenjang Singapura/internasional

- Preprocess: mapping baru Primary 6/P6→SD 6, Sec 1→SMP 1, Sec 2→SMP 2, Sec 3→SMP 3, Sec 4→SMA 10, plus angka Romawi (kelas x/xi/xii).
- Prompt: "Sec 1–4" TIDAK berarti sudah sekolah di Singapura (SIS/BBS dll. ada di Indonesia) — jangan asumsikan lokasi.

## 7b. Anti-probing (kasus Venn, report 3 Juli)

- Prompt: lokasi/nama sekolah HANYA boleh ditanya kalau jawaban bergantung padanya; istilah kelas Indonesia = lokasi tidak relevan, JANGAN ditanya.
- Larangan baru: dilarang probing data yang tidak dibutuhkan (lokasi/nama sekolah, kota, usia); user sudah bilang mau lanjut/daftar -> langsung ke langkah berikutnya tanpa menyela dengan pertanyaan baru.

## 8. Fix minor

- `Process Counter & Merge Data`: `Tanggal Chat Pertama` dibaca dari kolom yang benar (dulu selalu ter-reset jadi hari ini); error tidak lagi menulis row "ERROR" ke sheet.
- `Record to UNKNOWN` & notifikasi admin memakai pesan gabungan (`user_message_final`), bukan hanya bubble terakhir.
- `Update GForm Sent TS1`: mapping `row_number: 0` yang salah dihapus.

## 9. Workflow baru: VIRA Error Notifier

`Error Trigger → Compose Notif → Notify Admin Error` (WA ke 6285155202354). Eksekusi VIRA yang mati diam-diam kini terlihat. Harus di-set sebagai Error Workflow di settings VIRA V4 (lihat manual).

## Masih terbuka (di luar scope V4)

Rotasi kredensial Kirimi + pindah ke n8n Credentials (secret masih plaintext di node HTTP, termasuk di error workflow), auth webhook, SOP follow-up sheet UNKNOWN, investigasi delivery Kirimi untuk pesan beruntun cepat.
