# Pending Changes — Skalabilitas 100x Load (VIRA-PCR)

**Dibuat:** 2026-07-25
**Sumber:** QA menyeluruh `workflow/production/` — 4 workflow n8n + PCR_Database.xlsx
**Laporan detail:** [2026-07-25-QA-skalabilitas-VIRA-PCR.md](2026-07-25-QA-skalabilitas-VIRA-PCR.md) · [Sesi 2 patch](2026-07-25-sesi2-patch-keamanan-VIRA-PCR.md) · [Sesi 4 desain](2026-07-25-sesi4-desain-beban-sheets-VIRA-PCR.md)

> Register ini **terpisah** dari `Pending Waiting Changes.md`. File itu melacak pekerjaan go-live (item #1–#21). File ini khusus skalabilitas/beban. Penomoran pakai prefiks `L` supaya tidak bentrok.
>
> **Overlap yang perlu diketahui:** item **L1** di bawah adalah perluasan dari item **#21** di register lama (private key di CONFIG, dicatat 2026-07-19). Yang baru bukan keberadaan key-nya — tapi temuan bahwa `Read CONFIG` menariknya ke execution log n8n **setiap pesan masuk**, jauh lebih luas dari "siapa pun yang pegang sheet".

---

## Ringkasan (urut prioritas)

| # | Masalah | Effort | Dampak | Status |
|---|---|---|---|---|
| **L1** | Private key Google plaintext di CONFIG | 30 menit | Tutup akses tulis penuh ke data pelanggan | 🔴 Belum |
| **L2** | Cleanup MSG_BUFFER bisa macet permanen | Kecil | Cegah buffer tumbuh selamanya | 🟠 Belum |
| **L3** | Pesan menggantung saat admin ambil alih | Kecil | Cegah AI jawab ulang yang sudah dijawab admin | 🟠 Belum |
| **L4** | Hitungan `Counter` bisa meleset | — | Tidak ada fix bersih di Sheets; dokumentasikan | 🟠 Terima |
| **L5** | Secret Kirimi hardcode di Error Notifier | Kecil | Rotate secret jadi 1 tempat | 🟠 Belum |
| **L6** | `data_context`/`faq_context` di dalam system prompt | Kecil | Prasyarat caching; benar terlepas dari itu | 🟡 Belum |
| **L7** | Sistem mentok ~6,6 giliran chat/menit | Sedang | 6,6 → 12 giliran/menit (1,8×) | 🟡 Belum |
| **L8** | 100× mustahil selama STATS di Google Sheets | Besar | Plafon hilang + L4 selesai gratis | 🟡 Keputusan |
| **L9** | Biaya AI ~Rp 30 jt/bln di 3.000 pesan/hari | Sedang | Rp 30 jt → Rp 16 jt/bln | 🟡 Tunda |
| **L10** | WhatsApp gateway satu perangkat | Besar | Hilangkan titik mati tunggal | 🟡 Keputusan |
| **L11** | Follow-up backlog tidak pernah habis | Besar | Butuh desain ulang | 🟡 Keputusan |
| **L12** | Config diabaikan + dead code + Sheet ID salah | Kecil | Kebersihan; cegah jebakan berikutnya | 🟢 Patch siap |

**Keputusan yang menunggu Steven** (menentukan mana yang layak dikerjakan): lihat bagian akhir.

---

# 🔴 Prioritas 1 — Keamanan

## L1. Private key Google service account plaintext di tab CONFIG

**Masalah**
Private key service account (PEM lengkap, 1.732 karakter) dan `kirimi_secret` tersimpan sebagai teks biasa di tab CONFIG.

**Penyebab**
Dua baris residu setup (`google service email`, `google service private key`) yang **tidak dipakai node manapun** — `Parse Config` tidak memasukkannya ke objek `config`, dan kredensial n8n yang benar sudah ada dan berfungsi. Yang memperparah: node `Read CONFIG` membaca **seluruh tab tanpa filter**, jadi private key ikut masuk ke *execution data* n8n setiap pesan masuk, dan tersimpan di database eksekusi. Key itu juga ada di snapshot `PCR_Database.xlsx` di disk.

**Kenapa serius:** key ini adalah kredensial untuk mengakses spreadsheet itu sendiri — bocornya = akses tulis penuh ke STATS (nama, no WA, lokasi kerja, budget seluruh pelanggan).

**Solusi** — urutkan begini supaya sistem tidak mati di tengah:
1. Buat key baru di Google Cloud Console: IAM & Admin → Service Accounts → `persada@vira-persada.iam.gserviceaccount.com` → Keys → Add Key
2. Pasang key baru di credential n8n `Google Service Account - Persada`, tes 1 eksekusi
3. Hapus key lama di GCP
4. Hapus 2 baris dari tab CONFIG di Google Sheets
5. Bersihkan execution history n8n
6. Pertimbangkan rotate `kirimi_secret` juga

**Dampak**
Menutup jalur bocor terbesar. Nol efek ke performa maupun perilaku bot. **Effort ~30 menit.**

---

# 🟠 Prioritas 2 — Bug yang merusak diam-diam

Tiga ini tetap valid walau nanti pindah database — mengerjakannya bukan usaha terbuang.

## L2. Cleanup MSG_BUFFER bisa macet permanen

**Masalah**
Workflow `MSG_BUFFER Cleanup` (harian 03:00 WIB) bisa berhenti membersihkan selamanya.

**Penyebab**
Node `Pick expired block (>2h)` menghapus blok kontigu mulai baris 2, dan melakukan `break` saat ketemu baris pertama dengan `ts` tidak valid (bukan angka/kosong/negatif). Satu baris rusak = **seluruh baris kadaluarsa di belakangnya tidak pernah terhapus**.

**Solusi**
Jangan `break` pada `ts` invalid. Perlakukan baris tanpa timestamp valid sebagai kadaluarsa (baris tanpa `ts` yang bisa dipercaya tidak mungkin masih relevan), atau lewati dan lanjutkan scan lalu hapus dalam beberapa range terpisah. Tambahkan log jumlah baris yang dilewati supaya kerusakan data terlihat, bukan senyap.

**Dampak**
Mencegah MSG_BUFFER tumbuh tanpa batas. Kalau dibiarkan, setiap `Read MSG_BUFFER` (jalan tiap giliran chat) makin lambat **selamanya** — degradasi permanen, bukan sesaat.

---

## L3. Pesan menggantung di buffer saat admin ambil alih

**Masalah**
Setelah admin menonaktifkan bot (`bot_mode = OFF`) dan menjawab manual, pesan lama bisa terkirim ulang ke AI saat bot dinyalakan lagi.

**Penyebab**
Ada 3 lapis gate `bot_mode`. Gate pertama (`IF Bot Mode Active`) jalan **sebelum** pesan masuk MSG_BUFFER — aman. Tapi gate kedua (`HITL Check`) dan ketiga (`Cek_user_status`) jalan **setelah** `Append MSG_BUFFER`, dan tidak ada node `Mark Buffer Consumed` yang jalan saat mereka menghentikan alur. Pesan menggantung di buffer sampai ada pesan baru yang memicu pembacaan ulang — dan `Cek_user_status` menerima pesan sampai umur 30 menit.

**Solusi**
Sambungkan cabang stop `HITL Check` dan `Cek_user_status` ke node `Mark Buffer Consumed` (update `buffer_done_ts`).

**Dampak**
Mencegah AI menjawab ulang pertanyaan yang **sudah dijawab admin manual** — pengalaman user yang buruk dan membingungkan.

---

## L4. Hitungan `Counter` / `Intensitas Chat` bisa meleset

**Masalah**
Dua pesan yang diproses hampir bersamaan bikin satu increment hilang.

**Penyebab**
Pola `Read STATS` → `+1` → `Update to STATS` tanpa lock. Keduanya baca `Counter = N`, keduanya hitung `N+1`, keduanya tulis `N+1` — bukan `N+2`. Google Sheets tidak punya transaksi. `executeOnce: true` tidak membantu — itu hanya berlaku dalam satu eksekusi, bukan lintas eksekusi.

**Solusi**
**Tidak ada perbaikan bersih di atas Google Sheets.** Rekomendasi: terima ketidakakuratannya, dokumentasikan bahwa `Counter` adalah perkiraan bukan hitungan eksak. **Jangan bangun locking di atas Sheets** — kompleksitasnya tidak sepadan untuk kolom statistik.

**Dampak**
Perbaikan sungguhan datang **gratis** bersama L8 (migrasi database): `UPDATE ... SET counter = counter + 1` bersifat atomik.

---

## L5. Kredensial Kirimi hardcode di Error Notifier

**Masalah**
`VIRA-PCR Error Notifier.json` → node `Notify Admin Error` menyimpan `user_code`, `secret`, `device_id` langsung di `bodyParameters`. `device_id` bahkan tertulis dua kali.

**Penyebab**
Workflow ini pakai `errorTrigger` dan tidak punya node `Read CONFIG`, jadi tidak bisa ambil dari CONFIG tanpa menambah node.

**Solusi**
Pindahkan ke credential n8n (Custom Auth). ⚠️ **Butuh smoke test** — Sesi 2 menemukan **nol dari 16 node httpRequest** di seluruh workflow punya credential; semuanya kirim kredensial via body parameter. Jadi dukungan Custom Auth belum pernah terbukti jalan di instance ini.

Minimal yang bisa dideploy hari ini tanpa risiko: hapus `device_id` duplikat, tambah `retryOnFail: true` + `maxTries: 3` + `waitBetweenTries: 5000`.

**Catatan:** Node ini juga **tidak punya retry maupun onError**. Kalau Kirimi sedang jadi penyebab error, notifikasinya sendiri gagal tanpa fallback — kamu tidak tahu sistem mati tepat saat paling butuh tahu.

**Dampak**
Rotate secret cukup di satu tempat, bukan edit workflow. Plus alert error tidak hilang karena satu timeout jaringan.

Patch siap: [2026-07-25-sesi2-patch-keamanan-VIRA-PCR.md](2026-07-25-sesi2-patch-keamanan-VIRA-PCR.md)

---

# 🟡 Prioritas 3 — Kapasitas & biaya

## L6. `data_context` / `faq_context` di dalam system prompt

**Masalah**
Struktur prompt sekarang membuat prompt caching **mustahil kena**, dan bikin system prompt membengkak tak terduga.

**Penyebab**
System prompt AI Agent berakhir dengan `# DATA TERVERIFIKASI {{ $json.data_context }}` dan `# FAQ RELEVAN {{ $json.faq_context }}` — keduanya hasil retrieval yang **berubah tiap pesan**. Prompt caching itu cocok-prefix: satu byte berubah, semua setelahnya invalid. Konten volatil di dalam blok yang sama = tiap request menulis entry cache baru, nol yang pernah dibaca.

Terpisah: isi `Jawaban` FAQ **tidak di-clip** (berbeda dari PRODUK yang di-clip 220 char/field), jadi FAQ panjang masuk penuh ke prompt.

**Solusi**
Pindahkan `data_context` + `faq_context` keluar dari system prompt ke **user message**. Clip isi `Jawaban` FAQ.

**Dampak**
Gratis, tidak mengubah perilaku bot (isi yang sampai ke model sama, cuma posisinya beda). Prasyarat wajib untuk L9. **Benar dikerjakan terlepas dari caching** — bikin prompt lebih bersih dan ukurannya terprediksi.

---

## L7. Sistem mentok ~6,6 giliran chat/menit

**Masalah**
Plafon throughput sekarang sekitar 6,6 giliran/menit — dan turun ke ~3,5 kalau user mengetik beberapa bubble beruntun.

**Penyebab**
Setiap giliran chat menembak Google Sheets **9 kali baca**; 7 di antaranya membaca **seluruh tab tanpa filter**. Kuota Google Sheets API = **60 baca/menit per user** (service account = 1 user). `60 ÷ 9 ≈ 6,6`.

Diperparah: pesan yang kalah race debounce tetap membakar **4 baca + 2 tulis** sebelum dibuang. User yang mengetik 3 bubble = 17 baca untuk 1 giliran percakapan.

**Solusi** — 3 perubahan:

| | Perubahan | Hemat |
|---|---|---|
| R1 | Gabung `Read User STATS` + `Read STATS for HITL` (keduanya baca seluruh STATS, dipisah hitungan milidetik) | 1 baca **per pesan** — termasuk pecundang debounce, jadi pengali terbesar |
| R2 | Gabung `Read FAQ` + `Read PRODUK Data` + `Read LINKS Data` jadi 1 panggilan `values:batchGet` | 2 baca per giliran |
| R3 | Hapus `Read STATS` yang telat, pakai ulang `Re-Read STATS Debounce` yang sudah difilter ke baris user | 1 baca per giliran |

R1 aman karena gate `bot_mode` yang benar-benar berarti adalah pemeriksaan ketiga di `Cek_user_status` — jalan setelah jeda 60 detik, di situlah admin realistis sempat menekan tombol.

R3 paling aman: `Read STATS` satu-satunya dari 9 node read yang **nol referensi by-name** — dikonsumsi murni via `$input.all()`.

⚠️ **R2 butuh uji coba terpisah.** Autentikasi Predefined Credential Type Google Service Account di HTTP Request node belum pernah terbukti jalan di instance n8n ini. Uji di workflow kosong dulu.

**Dampak**
9 → 5 baca per giliran. **6,6 → 12 giliran/menit (1,8×).**

Desain lengkap: [2026-07-25-sesi4-desain-beban-sheets-VIRA-PCR.md](2026-07-25-sesi4-desain-beban-sheets-VIRA-PCR.md)

---

## L8. 100× mustahil selama STATS di Google Sheets

**Masalah**
Bahkan setelah L7 selesai, target 100× tidak tercapai.

**Penyebab** — struktural, bukan soal implementasi. Setiap pesan **wajib** baca STATS dua kali:
1. **Sebelum buffer** — kenali user (No WA/lid) + cek `bot_mode`. Harus terjadi sebelum pesan masuk MSG_BUFFER.
2. **Sesudah `Wait3`** — baca ulang `debounce_ts` untuk tahu siapa pemenang race. Nilainya baru valid setelah jeda 60 detik, jadi tidak bisa digabung dengan yang pertama.

```
60 baca/menit ÷ 2 baca/pesan = 30 pesan/menit   ← plafon absolut
```

Itu sebelum menghitung satu pun operasi tulis.

**Solusi**
Pindahkan tab **STATS** ke database sungguhan (Postgres/Supabase). Sheets tetap dipakai untuk PRODUK/FAQ/LINKS yang jarang berubah dan enak diedit tim non-teknis.

**Dampak**
Plafon hilang (ribuan/menit). **Bonus: L4 (lost update) selesai gratis** — `UPDATE ... SET counter = counter + 1` atomik. Juga menyelesaikan masalah `Simple Memory` yang sekarang disimpan in-memory di proses n8n dan akan korup begitu n8n di-scale horizontal.

**Effort besar.** Layak atau tidak tergantung jawaban pertanyaan baseline di bawah.

---

## L9. Biaya AI ~Rp 30 juta/bulan di 3.000 pesan/hari

**Masalah**
System prompt 17.731 karakter (~4.400 token) dikirim utuh dan ditagih penuh **setiap pesan**.

**Penyebab**
Tidak ada prompt caching. **Dan tombolnya memang tidak ada** — node `Anthropic Chat Model` (`lmChatAnthropic`) di n8n tidak punya opsi ini sama sekali:
- [PR #22318](https://github.com/n8n-io/n8n/pull/22318) (menambah toggle) — **closed, tidak di-merge**
- [Issue #13231](https://github.com/n8n-io/n8n/issues/13231) — **closed as not planned**
- [PR #20484](https://github.com/n8n-io/n8n/pull/20484) yang merged hanya menyentuh `@n8n/ai-workflow-builder.ee` — fitur AI Builder internal n8n, **nol efek** ke AI Agent

**Solusi** — 2 langkah:
1. **Sekarang, gratis:** L6 (pindahkan data keluar dari system prompt)
2. **Nanti:** ganti `AI Agent` + `Anthropic Chat Model` dengan HTTP Request langsung ke `https://api.anthropic.com/v1/messages`, dengan `cache_control: {"type":"ephemeral"}` pada blok system.

Langkah 2 feasible justru karena **AI Agent VIRA tidak punya tool sama sekali** — nol koneksi `ai_tool`, system promptnya sendiri bilang *"Kamu TIDAK punya tool"*. Tidak ada agent loop yang hilang. Yang perlu diganti hanya `Simple Memory` (riwayat 10-turn harus dibangun manual jadi array `messages`) — dan itu sekalian membereskan masalah memory in-memory di L8.

**Dampak**
Rp 30 jt → Rp 16 jt/bulan (~46%) di 3.000 pesan/hari.

⚠️ **JANGAN kerjakan langkah 2 sekarang.** TTL cache 5 menit, break-even ≥2 request dalam window itu. Selama `whitelist_enabled = TRUE` dengan 3 nomor, jeda antar pesan hampir pasti >5 menit → tiap request bayar biaya tulis cache 1,25× **tanpa pernah dibaca**. Malah rugi 25%. Tunggu sampai traffic >1 pesan per 5 menit di jam aktif, atau pakai `ttl: "1h"` kalau polanya bursty.

---

## L10. WhatsApp gateway satu perangkat

**Masalah**
Satu device Kirimi (`D-GHK1A`) melayani semua: balasan user, kirim media, notif admin, notif tim lapangan, notif tim media, follow-up, notif error.

**Penyebab**
Gateway WhatsApp tidak resmi. Sticky note di workflow Follow-up sendiri sudah menandai **>500 pesan/hari berisiko ban**. 100× traffic melewati batas itu jauh.

**Solusi**
Multi-device, atau pindah ke WhatsApp Cloud API resmi.

**Dampak**
Menghilangkan titik mati tunggal. Kalau device kena ban sekarang, **seluruh sistem mati — termasuk kemampuan mengabari kamu bahwa sistem mati**, karena notif error lewat device yang sama.

---

## L11. Follow-up backlog tidak akan pernah habis

**Masalah**
Sistem menjanjikan follow-up tiap 72 jam, tapi kapasitasnya jauh di bawah itu begitu lead bertambah.

**Penyebab**
- `followup_max_per_run` tidak ada di CONFIG → default kode **20/run**
- `followup_min/max_delay_sec` tidak ada di CONFIG → default **20–45 detik** (rata-rata ~34,5 dtk)
- `Loop Kandidat` batchSize = 1 → **serial murni**, tidak paralel
- Jendela aktif 08:00–20:00 = 13 run/hari

```
Kapasitas    = 20 × 13 = 260 kandidat/hari
Batas jenuh  = 20 × 13 × 3 hari = 780 kandidat
```

Di atas ±780 kandidat eligible, antrian bertambah terus tiap siklus. 10.000 kandidat = **±39 hari** untuk satu putaran, padahal dijanjikan 3 hari.

**Solusi**
Butuh desain ulang (queue worker / paralelisasi), **bukan tuning angka**. Menaikkan `max_per_run` ke clamp maksimum 300 bikin satu run berdurasi ~172 menit — melebihi interval trigger 1 jam, sehingga run saling tumpang tindih. Jalan buntu.

**Catatan:** `followup_max = 0` di CONFIG berarti follow-up **tak terbatas** per user. Digabung interval 72 jam: user yang tidak pernah balas akan di-follow-up selamanya.

---

# 🟢 Prioritas 4 — Kebersihan (patch sudah siap)

## L12. Config diabaikan, dead code, Sheet ID salah

| Temuan | Penyebab | Solusi |
|---|---|---|
| `Bootstrap Config` hardcode Sheet ID **`1dJWq7iq...`** | Salinan/typo — semua 23 node Sheets pakai `1pzGuRZ...` | Ganti ke ID benar. Dampak fungsional nol (`config.sheet_id` nol konsumen), tapi jebakan untuk perubahan berikutnya |
| `Rate Limiter LID` hardcode 5 pesan/60 detik | CONFIG punya `rate_limit_max=10` + `rate_limit_window_sec=60` tapi diabaikan | Baca dari config dengan fallback. ⚠️ **Butuh keputusan** — lihat bawah |
| `Wait3` hardcode 60 detik | CONFIG punya `debounce_seconds=60` tapi diabaikan | Ganti ke ekspresi. Terbukti aman: `Wait1`/`Wait2` di workflow yang sama, typeVersion sama, sudah pakai ekspresi di produksi |
| `$vars.chatCounter = counter` di `Chat Counter` | `$vars` di n8n **read-only** — assignment tidak persist | Hapus. `chat_counter` nol konsumen (verified). Catatan: ada juga `CHAT_COUNTER: ${counter}` di `aiInputText` yang harus ikut dihapus, kalau tidak node langsung error |

Kode patch siap paste: [2026-07-25-sesi2-kode-patch/](2026-07-25-sesi2-kode-patch/)

---

# Urutan yang disarankan

1. **L1** — hapus private key + rotate → 30 menit, risiko tertinggi hilang
2. **L2, L3** — fix 2 bug senyap → aman, bisa deploy satu-satu
3. **L6** — pindahkan data keluar dari system prompt → gratis, benar terlepas dari caching
4. **L12** — patch kebersihan → kode sudah siap
5. **L7** — optimasi 9→5 baca → 1,8× kapasitas
6. *Baru putuskan:* **L8** (Postgres), **L10** (multi-device), **L11** (redesign follow-up)

---

# ⛔ Keputusan yang menunggu Steven

Tiga ini memblokir keputusan besar — tanpa jawabannya, sebagian pekerjaan di atas berisiko sia-sia.

### 1. Target realistis berapa pesan/hari?
Produksi masih `whitelist_enabled = TRUE` dengan 3 nomor, jadi tidak ada data observasi untuk menebak.

- **~3.000/hari** → L7 cukup, L8 (Postgres) bisa ditunda
- **~30.000/hari** → L7 sebagian **sia-sia** (R1/R3 akan dibuang saat migrasi). Kerjakan hanya R2 + bug fix, lalu langsung L8

### 2. Rate limit 5 atau 10 pesan/menit per user?
Kode hardcode `5`, CONFIG bilang `10`. Patch L12 bikin kode nurut CONFIG → batas efektif **naik dua kali lipat**. Kalau `5` yang benar, ubah CONFIG-nya, jangan kodenya.

### 3. Nomor penerima alert error tetap `6285155202354`?
Berbeda dari `admin_phone` di CONFIG (`6282321298930`). Nomor itu ada di `whitelist_numbers` — kemungkinan besar nomormu sendiri dan **memang sengaja** jadi penerima alert teknis (bukan admin klien). Kalau begitu, biarkan.
