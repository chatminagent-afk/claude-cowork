# Analisa Bug VIRA — Report Production 1 Juli

**Tanggal analisa:** 2 Juli 2026
**Sumber:** `production/VIRA.json` (56 node, live), `production/The_Scholars_Database.xlsx`, 7 chat export WA `report/report problem production/report 1 juli`
**Status:** MENUNGGU APPROVAL — belum ada perubahan apapun yang dieksekusi.

---

## Ringkasan Eksekutif

Keempat masalah yang dilaporkan berhasil direproduksi dan root cause-nya teridentifikasi di level node/kode. Ditemukan juga 7 temuan tambahan, termasuk satu yang cukup serius: **data nama user tertukar antar row di sheet STATS** (indikasi bug matching row by `lid`). Semua solusi yang diusulkan bersifat perbaikan minimal pada node existing — tidak ada penggantian framework/arsitektur.

| # | Masalah | Root Cause Singkat | Tingkat Keyakinan |
|---|---------|--------------------|--------------------|
| 1 | Balasan valid di-override jadi pesan error | Filter "kalimat proses internal" di node **Process All** menghapus seluruh kalimat yang mengandung frasa umum seperti "saya cek" | **Terbukti** (disimulasikan) |
| 2 | Context/memory hilang | **Simple Memory** = buffer in-RAM (hilang saat restart), window 10 pesan, session key rentan pecah, tidak ada fakta persisten di DB | Tinggi (perlu log n8n untuk konfirmasi final) |
| 3 | Belum ada intro "Sam versi AI" untuk user baru | Memang belum di-handle — instruksi user baru di **Cek_user_status** langsung tanya status tanpa intro | Terkonfirmasi |
| 4 | Baris pesan hilang di debounce | Append `pending_msg` di **Update Buffer** = read-modify-write **tidak atomik** → lost update saat pesan beruntun | Tinggi (perlu log eksekusi untuk konfirmasi final) |

---

## Konteks: Alur Live Saat Ini

```
Webhook → IF From Me → IF (Whitelist, DISABLED) → Chat Counter
→ Read User STATS → IF Bot Mode Active → Update Buffer (append pending_msg)
→ Rate Limiter LID → Read STATS for HITL → HITL Check
→ Wait3 (60 detik) → Re-Read STATS Debounce → IF_Chat_Debounce (last-writer wins)
→ Cek_user_status → Preprocess - Context Detection → Read FAQ/PROGRAM/ABOUT/LINKS
→ FAQ Retrieve → AI Agent (Sonnet 4.6, Simple Memory window 10)
→ Process All → Wait1 (5–10 dtk) → Reply Chat Kirimi → Delete_Pending_Msg
```

Catatan penting: `IF (Whitelist)` sekarang **disabled** (traffic publik lolos) — konsisten dengan bot membalas nomor publik. Jalur GForm terpisah (IF Send GForm dkk.) juga disabled karena link sudah di-inject inline di Process All.

---

## Masalah 1 — Node "Process All" Over-strict (TERBUKTI)

### Root cause

Di Process All ada blok "HAPUS KALIMAT PROSES INTERNAL (FORCE)" dengan daftar `internalKeywords` yang memuat frasa percakapan normal: `'saya cek'`, `'saya lihat'`, `'saya temukan'`, `'saya ambil'`, `'dari data'`, `'data yang ada'`, dll. Regex-nya menghapus **seluruh kalimat pertama** yang mengandung salah satu frasa itu:

```js
const internalRegex = new RegExp(`^\\s*([^.!?]*?(${keywordPattern})[^.!?]*[.!?]\\s*)`, 'i');
```

Jika balasan AI hanya 1 kalimat (dan gaya Sam memang diwajibkan 1–2 kalimat oleh system prompt!), seluruh output terhapus → `cleanOutput` kosong → jatuh ke fallback:

```js
if (!cleanOutput || cleanOutput.trim() === '') {
  ...
  cleanOutput = 'Maaf, terjadi kesalahan. Coba tanyakan ulang yaa.';
}
```

### Bukti (simulasi kode asli)

| Output AI asli | Hasil setelah filter |
|---|---|
| "Oke, ditunggu yaa, nanti **saya cek** dan akan saya hubungi lewat WA setelah proses seleksinya selesai." (kasus Maria 30/6 20:05) | `""` → **"Maaf, terjadi kesalahan…"** |
| "Untuk yang ini saya belum ada infonya yaa, nanti **saya cek** dan kabari." (balasan [UNKNOWN] yang DIWAJIBKAN system prompt sendiri) | `""` → fallback UNKNOWN hardcode |
| "Iya betul, nanti **saya lihat** dulu jadwalnya yaa." | `""` → **"Maaf, terjadi kesalahan…"** |
| "Boleh kok, batch 5 masih buka pendaftarannya." | utuh (aman) |

Ada kontradiksi internal: system prompt **mewajibkan** balasan UNKNOWN berbunyi "nanti saya cek dan kabari", tapi Process All **menghapus** setiap kalimat yang mengandung "saya cek". Ini juga menjelaskan kenapa Tri Agustina (1/7 09:08) selalu menerima teks fallback UNKNOWN hardcode, bukan kalimat racikan AI.

### Sub-temuan: `detectedStatusFromMessage` STUDENT vs PARENT

Di **Preprocess - Context Detection**, regex STUDENT memuat kata `anaknya`:

```js
else if (message.match(/\b(murid|saya\s*sendiri|...|anaknya|...)\b/i)) {
  detectedStatusFromMessage = 'STUDENT';
}
```

Pesan Maria "Saya sudah isi form batch 5 sam **anaknya** namanya angelo dewata" → terdeteksi STUDENT, padahal "anaknya" justru ucapan khas orang tua. Kata ini masuk daftar STUDENT karena saat menjawab greeting "orang tua atau anaknya?", jawaban "anaknya" berarti si murid — tapi di tengah percakapan artinya kebalikan. Dampak ke balasan Maria kebetulan nol (karena `userStatusInDB=PARENT` yang dipakai), tapi ini bug laten untuk user baru.

### Solusi yang diusulkan

Node yang diubah: **Process All** dan **Preprocess - Context Detection**.

1. **Persempit `internalKeywords`** hanya ke frasa yang benar-benar membocorkan proses internal (selalu menyebut sumber data): `'saya cek data'`, `'saya cek di sheet'`, `'berdasarkan faq'`, `'berdasarkan data'`, `'dari faq'`, `'dari sheet'`, `'menurut data'`, `'faq yang tersedia'`. Buang frasa percakapan normal: `'saya cek'`, `'saya lihat'`, `'saya temukan'`, `'saya ambil'`, `'dari data'`, `'data yang ada'`, `'referensi yang ada'`.
2. **Safety guard anti-kosong**: sebelum menghapus kalimat, simpan `aiOutput` asli; jika hasil akhir stripping kosong padahal `aiOutput` tidak kosong → **pakai aiOutput asli** (setelah pembersihan tag & markdown), BUKAN pesan error. Pesan "Maaf, terjadi kesalahan" hanya untuk kasus AI benar-benar tidak menghasilkan output.
3. **Perbaiki regex STUDENT** di Preprocess: keluarkan `anaknya` dari daftar umum; `anaknya` hanya dihitung sinyal STUDENT jika pesan pendek (≤ ~15 karakter) DAN status di DB masih kosong (konteks menjawab greeting). Selain itu, `anaknya` justru sinyal PARENT.
4. Terapkan perbaikan yang sama ke blok fallback status di Process All (duplikat logika serupa ada di sana — jangan sampai dua heuristik beda hasil).

---

## Masalah 2 — Context/Memory Hilang

### Root cause (berlapis)

Konfigurasi live: **Simple Memory** = `memoryBufferWindow`, `contextWindowLength: 10`, `sessionKey = user_wa` (nilai `body.from` mentah dari Kirimi).

1. **Memory volatil (penyebab utama yang paling mungkin)**: `memoryBufferWindow` disimpan di RAM proses n8n. Setiap restart/redeploy n8n = seluruh history percakapan semua user hilang. Jika n8n jalan queue mode multi-worker, memory bahkan tidak dibagi antar worker (tiap eksekusi bisa jatuh di worker berbeda dengan memory berbeda).
2. **Window hanya 10 pesan**: percakapan panjang mendorong fakta awal (kelas anak, program) keluar window.
3. **Session key rentan pecah**: `user_wa` dipakai mentah. Di sheet STATS nyatanya ada 7 row dengan identitas `@lid` (bukan nomor) — artinya Kirimi kadang mengirim `from` dalam format berbeda untuk user yang sama → memory user tersebut terpecah jadi 2 sesi.
4. **Tidak ada fakta persisten**: STATS tidak menyimpan kelas anak/program yang dibahas. Padahal Preprocess sudah mendeteksi `grade` dan `recommendedProgram` di tiap pesan — hasil deteksi itu dibuang begitu saja.

### Bukti dari chat

Marsella (0877-7283-0441): 30/6 12:24 bot sudah merekomendasikan program Junior untuk anak kelas 6; 30/6 14:25 (2 jam kemudian, masih hari yang sama) bot bertanya "Program apa yang ingin diketahui lebih lanjut, anaknya sekarang kelas berapa yaa?". Maria ditanya kelas anak 3 hari berturut-turut (28/6, 29/6, 30/6). Pola yang sama di Tri Agustina, EL, dan DSS.

### Data tambahan yang saya butuhkan (untuk konfirmasi final)

- Mode deployment n8n: single instance atau queue mode (berapa worker)?
- Apakah ada restart/redeploy n8n antara 30/6 12:24–14:25 WIB?

### Solusi yang diusulkan (sederhana, tanpa infra baru)

Node yang diubah: **Cek_user_status**, **Preprocess - Context Detection**, **Update to STATS** (atau node update baru), sheet **STATS**.

1. **Fakta persisten di STATS**: tambah kolom `kelas_anak` dan `program_interest` (atau satu kolom `context_note`). Diisi otomatis: saat Preprocess mendeteksi `grade`/`recommendedProgram`, tulis ke STATS pada siklus update yang sudah ada (Process Counter & Merge Data → Update to STATS — tidak perlu node Sheets baru).
2. **Inject ke SYSTEM_DATA**: di Cek_user_status, sertakan fakta tersimpan ke blok `[SYSTEM_DATA]`, mis. `KELAS_ANAK: SMP 2 / PROGRAM_DIBAHAS: Intermediate`, plus instruksi "JANGAN tanya ulang kelas kalau KELAS_ANAK sudah terisi". Ini membuat konteks inti tahan restart, tahan window overflow, dan tahan pecah session key.
3. **Naikkan `contextWindowLength` 10 → 20** (perubahan satu angka, biaya token masih kecil karena balasan pendek).
4. **Stabilkan session key**: pakai `user_lid || user_phone` (digit saja) sebagai sessionKey Simple Memory, bukan `body.from` mentah.

Migrasi memory ke storage persisten (Redis/Postgres) sengaja TIDAK diusulkan sekarang — over-engineered untuk skala ini; poin 1–2 sudah menutup gap paling menyakitkan.

---

## Masalah 3 — Intro "Sam versi AI" untuk User Baru

### Kondisi saat ini

Belum ada intro. Untuk user baru (`shouldAskStatus = true`), **Cek_user_status** menyuntik instruksi:

> "This is a NEW USER. You MUST ask: 'Sebelumnya, boleh tahu yang sedang chat sekarang orang tua murid atau calon muridnya langsung?'"

dan system prompt ALUR langkah 3 melarang menjawab pertanyaan sebelum status diketahui → pertanyaan pertama user baru efektif "ditelan" (lihat kasus Vivipoh di Temuan Tambahan C).

### Node/prompt yang perlu diubah

1. **Cek_user_status** — ubah CRITICAL INSTRUCTION untuk user baru: wajib buka dengan intro verbatim client:
   > "Haloo thank you sudah contact TheScholars.id yaa. Saya Sam versi AI yaa, saya siap bantu untuk jawab pertanyaan yang ada mengenai program kita dan scholarships ke Singapore."
2. **System prompt AI Agent** — sesuaikan bagian `# STATUS` dan `# ALUR` langkah 3 agar konsisten dengan intro + aturan "jawab pertanyaan pertama, jangan di-skip".
3. **Update STATS - Greeting Flag** — saat ini menandai `greeting_sent=Y` lewat pattern-matching teks balasan (`orang tua` + `anak` + tanda tanya). Dengan intro baru, pattern ini tidak match lagi → ganti dengan penanda sederhana: set `Y` jika `should_ask_status === true` dan reply sukses terkirim. Lebih robust, tidak tergantung susunan kalimat.

### Keputusan yang saya butuhkan dari kamu

Permintaan client: "jika user baru langsung bertanya, tetap tampilkan intro dulu, lalu lanjutkan menjawab". Tapi register bahasa (PARENT vs STUDENT) bergantung status yang belum diketahui di pesan pertama. Dua opsi:

- **Opsi A (rekomendasi, paling sesuai permintaan client):** 1 pesan = intro + jawaban pertanyaan (register netral, tanpa "kamu") + tutup dengan pertanyaan status ringan ("Ngomong-ngomong, ini saya ngobrol sama orang tuanya atau calon muridnya yaa?").
- **Opsi B:** intro + tanya status dulu; pertanyaan pertama user disimpan dan dijawab segera setelah status dijawab (perlu simpan pending question di STATS — sedikit lebih rumit).

---

## Masalah 4 — Baris Pesan Hilang di Debounce (Lost Update)

### Root cause

Debounce bekerja per-eksekusi: setiap pesan masuk memicu eksekusi sendiri yang meng-append pesannya ke kolom `pending_msg` di STATS (node **Update Buffer**), menunggu **Wait3 = 60 detik**, lalu hanya eksekusi dengan `timestamp` terakhir yang lanjut memproses gabungan pesan.

Masalahnya, append-nya **read-modify-write yang tidak atomik**:

```js
// Update Buffer — nilai "existing" diambil dari Read User STATS,
// yang dibaca di AWAL eksekusi (bisa stale beberapa detik):
const existing = userRow ? (userRow.json['pending_msg'] || '') : '';
return existing ? existing + '\n' + newMsg : newMsg;
```

Timeline kasus Adrian (+62 855-1070-070), pesan 28/6 11:27:38 / 11:27:54 / 11:28:09:

1. Eksekusi A tulis `pending_msg = "mau tanya"`.
2. Eksekusi B baca existing `"mau tanya"` → tulis `"mau tanya\nutk singapura itu rapor harus 90?"`.
3. Eksekusi C **membaca existing sebelum tulisan B ter-commit/terbaca** (latensi tulis+baca Google Sheets API bisa beberapa detik, ditambah antrean eksekusi n8n) → existing yang terbaca masih `"mau tanya"` → tulis `"mau tanya\nanak saya rata2x kelas x saat ini masih 85"` → **pesan B tertimpa dan hilang permanen**.

Persis sesuai log yang dilaporkan. Ini race condition klasik (lost update) — akan terus terjadi sporadis setiap user mengetik beruntun cepat.

### Bukti pendukung + data tambahan

Untuk konfirmasi 100%, saya butuh **log eksekusi n8n 28/6 11:27–11:30 WIB** (output node Read User STATS & Update Buffer di 3 eksekusi tsb). Tapi secara desain, bug ini pasti ada terlepas dari log.

### Solusi yang diusulkan: buffer append-only

Ganti mekanisme "edit satu sel" dengan "tambah baris" — operasi append di Google Sheets atomik per baris, tidak ada yang saling menimpa:

1. Buat sheet baru `MSG_BUFFER` dengan kolom: `lid`, `message`, `ts`.
2. **Update Buffer** → ubah jadi operasi **append** row baru (bukan appendOrUpdate sel pending_msg). Kolom `timestamp` di STATS tetap di-update seperti sekarang (tetap dipakai IF_Chat_Debounce untuk menentukan winner).
3. **Cek_user_status** → winner membaca semua row `MSG_BUFFER` untuk `lid` tsb, urutkan by `ts`, gabung dengan `\n` → jadi `userMessage` final.
4. **Delete_Pending_Msg** (dan variannya) → hapus row-row `MSG_BUFFER` milik `lid` tsb setelah terproses. Kolom `pending_msg` di STATS dipensiunkan.

Perubahan terlokalisir di 4 node yang memang sudah ada, tanpa tool/infra baru.

### Perlu konfirmasi: Wait3 = 60 detik

Komentar di Cek_user_status menyebut "Wait 8 detik", tapi node Wait3 live berisi **60 detik**. Artinya SEMUA balasan bot minimal tertunda ±65–70 detik (60 + Wait1 5–10 dtk + proses). Ini cocok dengan jeda balasan ~1,5 menit di chat export dan berkontribusi ke persepsi "bot lambat/tidak merespon". Apakah 60 detik ini disengaja? Rekomendasi: 15–20 detik cukup untuk menampung user yang mengetik beruntun.

---

## Temuan Tambahan (di luar 4 poin laporan)

### A. SERIUS — Nama user tertukar antar row STATS (bug matching `lid`)

Di sheet STATS: row `628121105026` bernama **"DSS"** dan row `6281393979477` bernama **"Vivipoh"** — padahal dari chat export justru kebalikannya (0812-1105-026 = Vivipoh yang tanya alamat; 0813-9397-9477 = DSS yang tanya SC1). Data user tertukar.

Penyebab yang paling mungkin: hampir semua node matching row memakai kolom `lid` sebagai kunci, dengan pola rawan:

```js
const userRow = rows.find(r => String(r.json['lid'] || '').trim() === userLid) || rows[0];
```

Jika `user_lid` kosong (Kirimi mengirim `from` sebagai nomor biasa dan `originLid` kosong), maka: (a) `find` mencocokkan **row pertama yang lid-nya juga kosong** — bisa row user lain; (b) fallback `|| rows[0]` mengambil row sembarang; (c) `appendOrUpdate` dengan `matchingColumns: [lid]` bernilai kosong bisa meng-update row orang lain. Dampak: nama/status/greeting flag/pending_msg bisa tertulis ke user yang salah — kategori bug yang bisa bocorkan konteks antar user.

**Solusi:** jadikan `No WA` (selalu ada) kunci matching primer dan `lid` sekunder; hapus semua fallback `|| rows[0]`; jika `user_lid` kosong → jangan pernah match by lid. Audit ke-4 node yang matching by lid (Update Buffer, Cek_user_status, HITL Check, Delete_Pending_Msg + varian).

### B. Istilah kelas Singapura/internasional tidak dikenali → bot salah asumsi

Preprocess hanya mengenali "kelas 6/SMP 1/SMA 3" dst. User dari sekolah kurikulum Singapura di Indonesia ("naik **Sec 3**", SIS Medan, BBS Kebon Jeruk) tidak terdeteksi → bot tanya ulang kelas berkali-kali dan berulang kali salah menyimpulkan "anaknya sudah sekolah di Singapura" (kasus EL 30/6 & 2/7, Tri Agustina 1/7 — dua-duanya sampai harus klarifikasi 3x).
**Solusi:** (1) tambah mapping di Preprocess: Primary 6 → SD 6, Sec 1 → SMP 1, Sec 2 → SMP 2, Sec 3 → SMP 3, Sec 4 → SMA 10; (2) tambah 1 paragraf di system prompt: "Banyak calon student bersekolah di sekolah kurikulum Singapura/internasional DI Indonesia (SIS, BBS, dll). Sebutan 'Sec 1–4' TIDAK berarti anaknya sudah di Singapura — jangan berasumsi; kalau ragu, tanya kota/negara sekolahnya."

### C. Pertanyaan user baru "ditelan" oleh alur status

Vivipoh (2/7): tanya alamat kantor → bot balas tanya status ortu/murid → user jawab "Iy" (ambigu) → anti-loop langsung eskalasi TALK_TO_SAM → pertanyaan alamat tidak pernah dijawab. Ini konsekuensi ALUR langkah 3 ("jangan jawab sebelum status") — akan ikut terselesaikan oleh solusi Masalah 3 (intro + jawab dulu).

### D. Janji "nanti saya cek dan kabari" tidak pernah ditepati (gap operasional)

Sheet UNKNOWN sudah berisi 31 pertanyaan tak terjawab dan admin memang dinotifikasi, tapi tidak ada mekanisme/SOP follow-up (kasus Tri Agustina 1/7: tanya jadwal buka ASEAN scholarship, dijanjikan dikabari, tidak pernah dikabari). **Usulan (ops, bukan node):** SOP harian singkat — Sam cek sheet UNKNOWN, jawab manual, tandai kolom `answered`. Opsional nanti: jawaban bagus dipromosikan jadi row FAQ.

### E. Keamanan (masih terbuka dari analisa 25 Juni)

Kredensial Kirimi (`user_code`, `secret`, `device_id`) masih plaintext di body beberapa node HTTP (terkonfirmasi masih ada di file live, mis. Reply Chat Kirimi). Webhook inbound juga masih tanpa auth. Bukan penyebab bug 1 Juli, tapi tetap perlu: rotasi secret + pindah ke n8n Credentials, dan validasi token sederhana di webhook.

### F. Higienitas data STATS

6 row punya `timestamp` milidetik (13 digit) tercampur dengan detik (10 digit) — row-row ini overlap dengan row beridentitas `@lid`; format `Tanggal Chat Pertama` campur (`dd/mm/yyyy` vs `yyyy-mm-dd`); ±929 row kosong di ekor sheet; mayoritas row tidak punya `user_status`/`bot_mode`. Rapikan sekalian saat menyentuh STATS (solusi M2 & A), terutama normalisasi timestamp — kolom ini dipakai IF_Chat_Debounce.

### G. Minor

- **Chat Counter:** `$vars.chatCounter = counter` — `$vars` di n8n read-only; counter internal ini kemungkinan selalu 1. Tidak berdampak (kolom Counter di sheet dihitung terpisah), tapi sebaiknya dibuang biar tidak menyesatkan.
- **Rate Limiter LID:** pakai `workflowStaticData` yang juga last-writer-wins antar eksekusi paralel — akurasi hitungan bisa meleset sedikit. Diterima saja untuk sekarang (fungsinya cuma anti-spam kasar).
- **Kasus "Iya ini saya Samm" (Adrian, 28/6 11:54):** itu Sam manusia (bot_mode row tsb OFF), bukan bug bot — tapi user jadi bingung identitas. Saran untuk client: saat takeover manual, konsisten mengakui "iya ini Sam asli yaa" supaya tidak merusak kepercayaan yang dibangun aturan # IDENTITAS.
- **Pesan pertama Adrian (21/6) tidak dibalas 7 hari** — konsisten dengan whitelist yang saat itu masih aktif (sekarang sudah disabled), bukan bug baru.

---

## Rencana Eksekusi (menunggu approval)

Urutan berdasarkan dampak × risiko (semua perubahan kecil dan terlokalisir):

| Prioritas | Perubahan | Node/aset | Risiko |
|---|---|---|---|
| 1 | Fix filter over-strict + guard anti-kosong | Process All | Rendah |
| 2 | Fix regex `anaknya` (STUDENT) | Preprocess, Process All | Rendah |
| 3 | Buffer append-only `MSG_BUFFER` | Update Buffer, Cek_user_status, Delete_Pending_Msg (+varian), sheet baru | Sedang (perlu test rapid-fire) |
| 4 | Fix matching row by No WA (temuan A) | Update Buffer, Cek_user_status, HITL Check, Delete_Pending_Msg | Sedang |
| 5 | Intro user baru (perlu keputusan Opsi A/B) | Cek_user_status, system prompt, Update STATS - Greeting Flag | Rendah |
| 6 | Konteks persisten (kelas/program) + window 20 + session key stabil | Cek_user_status, Preprocess, Update to STATS, Simple Memory, sheet STATS | Sedang |
| 7 | Mapping Sec 1–4 + catatan prompt | Preprocess, system prompt | Rendah |
| 8 | Turunkan Wait3 60→15-20 dtk (perlu konfirmasi) | Wait3 | Rendah |
| 9 | Keamanan: rotasi + n8n Credentials, auth webhook | 7 node HTTP, Webhook | Rendah |
| 10 | SOP follow-up UNKNOWN | Operasional | — |

**Testing yang diusulkan setelah eksekusi:** kirim 3 pesan beruntun <10 detik (verifikasi M4), pesan yang memancing "saya cek/saya lihat" (M1), chat dari nomor baru (M3 intro), tanya ulang setelah restart n8n (M2), dan user dengan istilah "Sec 3" (temuan B).

---

## Pertanyaan / Kebutuhan Sebelum & Saat Eksekusi

1. **Keputusan M3:** Opsi A (intro + jawab + tanya status di satu pesan — rekomendasi) atau Opsi B (intro + tanya status dulu, jawaban ditunda)?
2. **Konfirmasi Wait3:** 60 detik disengaja atau sisa eksperimen? Boleh diturunkan ke 15–20 dtk?
3. **Log n8n** (opsional, untuk konfirmasi final M2 & M4): mode deployment (single/queue), riwayat restart 30/6 siang, dan log eksekusi 28/6 11:27–11:30 WIB.
4. Konfirmasi bahwa `production/VIRA.json` memang export terbaru dari instance live (whitelist disabled, GForm path disabled — sudah cocok dengan perilaku yang diamati).
