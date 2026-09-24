# Follow-up berbasis konteks AI — VIRA PCR

> **CATATAN 2026-08-27 18:30 — nama file berubah.** Workflow follow-up AI sekarang hidup di
> `workflow/production/Follow-up AI Powered.json` (id `qaux8b14IgvxEXfoUtxa2`, **Active**),
> hasil **duplikasi** di n8n. Yang lama `VIRA-PCR Follow-up.json` (id `Ey5WRO8pnOKCVjTHMLq9I`)
> sudah **non-aktif** dan tidak lagi memakai AI — biarkan begitu, jangan diaktifkan lagi.
> Setiap penyebutan `VIRA-PCR Follow-up.json` di bawah ini merujuk file AI tersebut.


**Dibuat:** 2026-08-27
**File yang diubah:** `workflow/production/VIRA PCR.json`, `workflow/production/VIRA-PCR Follow-up.json`
**Backup pre-patch:** `workflow/arsip/2026-08-27-VIRA-PCR-pre-konteks-AI.json`, `workflow/arsip/2026-08-27-VIRA-PCR-Follow-up-pre-konteks-AI.json`
**Panduan eksekusi ringkas:** [`2026-08-27-README-implementasi-followup-konteks-AI.md`](2026-08-27-README-implementasi-followup-konteks-AI.md)
**Status:** file siap-import, **belum diimport, belum diaktifkan**. Baca §6 sebelum menyalakan.

---

## 1. Masalahnya

Follow-up lama buta konteks. `Filter Kandidat` memilih kalimat lewat rotasi modulo:

```js
let msg = String(cfg.templates[fuCount % cfg.templates.length] || '');
msg = msg.replace(/\{\s*(nama|name)\s*\}/gi, namaFirst || 'Kak');
```

Nama depan adalah satu-satunya personalisasi yang ada. Tidak ada node AI sama sekali di workflow itu. Lead yang menanyakan KPR untuk wiraswasta dan lead yang menanyakan jarak ke stasiun menerima kalimat yang sama persis.

**Akar masalahnya di data, bukan di workflow follow-up.** STATS punya 33 kolom dan tidak satu pun menyimpan *apa yang dibicarakan* — hanya `unit_interest`, `budget_range`, `lokasi_kerja`, `Pesan Pertama`. Transkrip hidup di `MSG_BUFFER` yang dibersihkan tiap 03:00 WIB untuk baris berumur >2 jam, dan memory AI Agent (`Simple Memory`, window 10) cuma ada di RAM n8n. Saat follow-up jalan 48 jam kemudian, jejak percakapan nol.

---

## 2. Bentuk solusinya

Satu kolom ringkasan yang di-update AI tiap turn — plus tiga penguatan supaya tidak hanyut:

1. **Jangkar teks mentah** (`last_msgs`). Ditulis kode, bukan AI, jadi gratis dan tidak bisa dikarang. Tiap turn ringkasan disusun ulang dari *(ringkasan lama + pesan asli terbaru)*, sehingga detail yang terkikis punya kesempatan dikoreksi ke teks sungguhan. Tanpa ini, turn ke-20 hanyalah ringkasan dari ringkasan ke-19 dan seterusnya — kesalahan menumpuk tanpa ada yang mengoreksi.
2. **Format berlabel tetap**, bukan prosa bebas. Struktur jauh lebih tahan drift, gampang divalidasi, gampang dipotong.
3. **Tidak pernah menimpa dengan hasil buruk.** Panggilan gagal/kosong/tak berformat → `konteks` lama dipertahankan apa adanya.

Yang **tidak** dipilih: tab `CHAT_LOG` append-only berisi transkrip penuh. Lebih robust secara teori, tapi proyek ini sedang melawan pertumbuhan Sheets (workflow purge #26 lahir karena `Read STATS (all)` sudah berat). Menambah tab yang tumbuh tiap turn melawan arus itu.

---

## 3. Kolom baru di tab STATS

Tambah manual, setelah kolom AG. **Header tanpa spasi di akhir** — jangan ulangi bug `pending_survey_tanggal ` yang sudah ada di sheet.

| Kol | Header | Ditulis | Isi |
|---|---|---|---|
| AH | `konteks` | AI (Haiku), tiap turn | 5 baris berlabel, maks 500 karakter |
| AI | `konteks_ts` | kode | epoch **detik**, hanya bergerak kalau isinya benar-benar berubah |
| AJ | `last_msgs` | kode | **3 giliran** terakhir, maks 150 char/giliran, total maks 450 |

### `last_msgs` menyimpan GILIRAN, bukan pesan tunggal

Yang dipisah ` || ` adalah **giliran percakapan**, dan satu giliran bisa berisi beberapa
pesan sekaligus — karena debounce 60 detik menggabungkan pesan beruntun jadi satu
`user_message_final` (dipisah newline). Contoh isi sel nyata:

```
apakah kpr bisa untuk wiraswsta tanpa slip gaji?
kalo subsidi dpt apa aja? || sy bkeluarga anak 3, pasny unit ap y?
bs muat mobil brp?
```

Itu **2 giliran berisi 4 pesan**, bukan 4 entri. Jendelanya bergulir: giliran ke-4 masuk,
giliran ke-1 gugur. Selnya tidak tumbuh tanpa batas.

**Kenapa 3 giliran, bukan 1?** Kolom ini adalah jangkar untuk mengoreksi ringkasan yang
mulai hanyut. Kalau hanya menyimpan giliran terakhir, orang yang membalas "oke" atau
"brp?" tidak meninggalkan bahan apa pun untuk dikoreksi, dan drift kembali. Tiga giliran
cukup untuk menangkap benang topik, masih terbatas.

Perakitannya dimulai dari giliran **terbaru** mundur ke belakang, bukan memotong string
gabungan dari depan. Sebabnya: 3 x 150 + 2 pemisah = 458 > 450, jadi pemotongan dari depan
akan memakan ujung giliran terbaru — justru bagian paling berguna. Dengan cara ini giliran
terbaru selalu utuh; yang tertua yang gugur duluan.

Isi `konteks` selalu berbentuk:

```
TOPIK: <yang sedang dibahas, 1 kalimat>
KEBUTUHAN: <yang dia cari>
KEBERATAN: <hambatan yang dia sebut sendiri, atau ->
LANGKAH BERIKUTNYA: <yang paling masuk akal ditawarkan berikutnya>
CATATAN: <maks 1 kalimat penting lain, atau ->
```

---

## 4. Perubahan di `VIRA PCR.json` (Main)

Seluruhnya di jalur **sesudah balasan terkirim ke user** — tidak menambah latensi yang dirasakan calon pembeli.

```
Send WA + Verify (Kirimi) → Extract & Prepare Data → Read STATS
  → Process Counter & Merge Data   [EDIT]
  → Build Konteks Input            [BARU]
  → Update Konteks                 [BARU]   ← ai_languageModel dari Anthropic Chat Model1
  → Merge Konteks                  [BARU]
  → Update to STATS                [EDIT]
```

| Node | Yang berubah |
|---|---|
| `Process Counter & Merge Data` | Mengeluarkan `last_msgs` (rolling 3 pesan, cap 150/450), `konteks_lama`, `konteks_ts_lama` — dibaca dari `existingRow` yang sudah dicari node ini |
| `Build Konteks Input` | Merakit bahan prompt. Semua akses lintas-node dibungkus `try/catch`: satu field gagal dibaca tidak boleh menggagalkan penulisan state user |
| `Update Konteks` | `chainLlm` tv 1.5, meniru pola `Summarize Handover`. `onError: continueRegularOutput` |
| `Merge Konteks` | **Wajib, bukan hiasan** — lihat catatan di bawah |
| `Update to STATS` | +3 mapping kolom, +3 entri `columns.schema`. Tidak ada write tambahan ke Sheets |

**Kenapa `Merge Konteks` wajib:** `Update to STATS` membaca `"lid": "={{ $json.lid }}"` dari item yang masuk. Output `chainLlm` bentuknya `{text: ...}` — kalau disambung langsung ke `Update to STATS`, kolom `lid` di sheet tertimpa kosong. Node ini mengembalikan item asli apa adanya plus `konteks_final`.

**Model dipakai bersama:** `Anthropic Chat Model1` (Haiku 4.5, `maxTokensToSample: 512`, credential `Anthropic Persada`) sekarang melayani dua chain — `Summarize Handover` dan `Update Konteks`. Sengaja tidak dibuat node model baru: satu tempat saja untuk mengganti model atau credential. Konsekuensinya garis koneksi di canvas jadi panjang; itu kosmetik.

---

## 5. Perubahan di `VIRA-PCR Follow-up.json`

```
Loop Kandidat (loop) → Claim STATS FU  [tidak diubah — anti-dobel tetap utuh]
  → Build FU Prompt        [BARU]
  → IF Pakai AI            [BARU]
      true  → Compose Follow-up  [BARU] ← Anthropic Chat Model FU [BARU]
      false → (langsung ke Validate, pakai template lama)
  → Validate FU Message    [BARU]
      ok    → Wait FU → Kirim Follow-up  [EDIT: tujuan & isi]
      tolak → Catat Kegagalan AI [BARU] → Rollback STATS FU (AI) [BARU] → Loop
Loop Kandidat (done, dulu menganggur)
  → Report FU Run [BARU] → IF Ada Kegagalan [BARU] → Notify Admin FU Summary [BARU]
```

`Claim STATS FU` **tetap berada sebelum compose** — nomor sudah diklaim sebelum satu token pun dibakar, jadi jaminan anti-dobel yang lama tidak bergeser sedikit pun.

### Node yang diedit

| Node | Yang berubah |
|---|---|
| `Parse Config FU` | +`ai_enabled`, +`ai_dry_run`; reset penghitung kegagalan run di static data. **Perbaikan bug:** `if (!templates.length) return [];` dulu mematikan seluruh run kalau `followup_templates` kosong — sekarang template hanya wajib saat AI mati |
| `Filter Kandidat` | Kandidat membawa `konteks`, `last_msgs`, `unit_interest`, `budget_range`, `lokasi_kerja`, `nama_lengkap`, `lead_source`, `pesan_pertama`, `days_idle`. Semua dari baris STATS yang sudah di tangan — **tidak ada pembacaan Sheets tambahan** |
| `Kirim Follow-up` | `phone` → `{{ $json.target_phone }}`, `message` → `{{ $json.final_message }}`. Ini yang membuat dry run bekerja tanpa cabang node terpisah |

### Guard di `Validate FU Message`

Prompt boleh melarang; yang **menjamin** adalah kode. Pesan ditolak kalau:

| Cek | Pola |
|---|---|
| terlalu pendek / kosong | `< 20 char` |
| terlalu panjang | `> 400 char` |
| nominal berformat ribuan | `\d{1,3}([.,]\d{3})+` |
| nominal singkat | `\b\d+([.,]\d+)?\s*(jt\|juta\|rb\|ribu\|m\|miliar\|milyar)\b` |
| menyebut Rp | `\bRp\s*\.?\s*\d` |
| persentase | `\d+\s*%` |
| tenor | `\b\d+\s*tahun\b` |
| URL | `(https?:\|www\.\|wa\.me\|\.com\b\|\.id\b)` |
| nomor telepon | `\b0\d{8,}\b\|\b62\d{8,}\b` |

Tag `[...]` dan markdown dibuang lebih dulu, jadi `[SEND_MEDIA: brosur]` yang bocor tidak ikut terkirim.

Melanggar → `throw` → error output → `Catat Kegagalan AI` → `Rollback STATS FU (AI)` → kembali ke loop. **Nomor itu dilewati, bukan dikirimi template** (keputusan Steven 2026-08-27): `follow_up_count` dan `last_follow_up_ts` dikembalikan ke nilai semula, jadi dia otomatis masuk antrian run berikutnya.

### Nada menyesuaikan tahap

`followup_max = 0` berarti tanpa batas, dan sudah ada lead dengan `follow_up_count: 13`. `Build FU Prompt` menyuntikkan tahap:

| FU ke- | Nada |
|---|---|
| 1–2 | Hangat, lanjutkan pembicaraan, wajar menawarkan langkah konkret |
| 3–5 | Lebih ringan, jangan mengulang ajakan yang sudah dilewatkan |
| 6+ | Soft. Beri ruang, jangan mendesak, jangan mengajak survey lagi kecuali ada minat baru |

Ini **meredam**, bukan menyembuhkan. Lihat §8.

### Laporan run

Output `done` `Loop Kandidat` yang selama ini menganggur sekarang dipakai. `Report FU Run` membaca daftar kegagalan dari static data dan **diam total kalau kosong** — ini alarm, bukan laporan rutin. Tanpanya, satu lead yang konteksnya selalu bikin AI melanggar akan dicoba ulang tiap jam selamanya tanpa ada yang tahu.

---

## 6. CONFIG baru

| key | default | fungsi |
|---|---|---|
| `followup_ai_enabled` | `Y` | `N` = kembali 100% ke template rotasi lama, **tanpa import ulang**. Ini tombol rollback tercepat |
| `followup_ai_dry_run` | `N` | `Y` = pesan tetap disusun sungguhan, tapi **dikirim ke `admin_phone`** dengan prefiks `[DRY RUN -> 628xxx | FU ke-N | idle Nh]` |

Dua-duanya opsional; kalau key-nya tidak ada, dipakai default. Menerima `Y`/`YES`/`TRUE`/`1`.

⚠️ Perhatikan: CONFIG production punya `followup_interval_hours = 48`, bukan 72 seperti tertulis di panduan lama `workflow/followup/2026-07-24-panduan-implementasi-followup-scalable.md`.

---

## 7. Checklist sebelum diaktifkan

1. **Duplicate tab STATS** sebagai backup. Lalu tambah 3 kolom §3.
2. Import `VIRA PCR.json`. Konfirmasi credential `Google Service Account - Persada` dan `Anthropic Persada` tidak "unbound".
3. Chat dari nomor uji, 3–4 giliran dengan topik jelas (mis. "KPR buat wiraswasta bisa?"). Cek di STATS: `konteks` terisi diawali `TOPIK:`, `last_msgs` berisi pesan asli, `konteks_ts` bergerak.
4. **Uji tahan gagal:** sementara ganti model di `Anthropic Chat Model1` ke nilai ngawur → chat lagi → pastikan STATS **tetap ter-update** dan `konteks` **tidak terhapus**. Kembalikan modelnya.
5. Isi CONFIG `followup_ai_dry_run` = `Y`.
6. **Non-aktifkan workflow follow-up lama dulu**, baru import yang baru (`id` sama jadi biasanya menimpa — pastikan hanya **1** yang Active).
7. Siapkan 2–3 baris uji di STATS: `Counter` ≥ 1, `last_reply_ts` = epoch sekarang − 350000, `survey_status` kosong, `bot_mode` kosong, `konteks` diisi manual. Nomor uji **bukan** admin/field/media team. Jalankan *Execute Workflow* manual pada jam 08–21 WIB.
8. **Baca hasil dry run di WA admin.** Ini gerbang utamanya: kalimatnya nyambung dengan topik? ada angka yang dikarang? terdengar seperti Vira? Ulangi sampai puas — lead sungguhan belum tersentuh sama sekali.
9. **Uji anti-dobel:** jalankan lagi segera → `Filter Kandidat` harus keluar **0**.
10. **Uji skip:** paksa gagal (sisipkan sementara aturan "sebut harga" di prompt `Compose Follow-up`) → pastikan pesan **tidak terkirim**, `follow_up_count`/`last_follow_up_ts` **kembali ke nilai semula**, dan laporan run menyebut kegagalan itu. Kembalikan prompt.
11. Hapus baris uji. `followup_ai_dry_run` → `N`. Aktifkan. Pantau hari pertama lewat menu Executions.

**Rollback:** CONFIG `followup_ai_enabled` = `N` → template lama, tanpa import ulang. Untuk balik total, import ulang dari `workflow/arsip/2026-08-27-*-pre-konteks-AI.json`.

---

## 8. Yang TIDAK dilindungi — baca ini

- **13 follow-up ke satu orang tetap 13 kali.** `followup_max = 0`. AI membuat kalimatnya bervariasi dan aturan nada meredam di FU ke-6+, tapi kebijakannya tidak berubah. Menetapkan `followup_max` adalah keputusan bisnis.
- **Guard nominal itu regex, bukan pemahaman.** "harganya masih sama seperti yang saya sebut kemarin" lolos semua pola. Yang menahan hal semacam itu cuma prompt dan mata Anda di tahap dry run.
- **Kirimi tetap gateway tidak resmi.** Pesan yang relevan menurunkan kemungkinan user menekan Block (pemicu ban terbesar), tapi risikonya tidak nol.
- **`konteks` ikut hilang** kalau workflow purge (#26) diaktifkan — barisnya terhapus seluruhnya. Konsisten dengan keputusan 2026-08-27.
- **Loop kegagalan.** Lead yang konteksnya selalu bikin AI melanggar dicoba tiap jam selamanya. Laporan run §5 satu-satunya yang membuatnya terlihat.
- **Penghitung kegagalan pakai `$getWorkflowStaticData('global')`** (pola sama dengan `Rate Limiter LID`). Reliabel dalam satu eksekusi, yang memang cukup di sini — tapi bukan penyimpanan tahan restart.
- **STATS jadi ~3,6x lebih berat per baca.** Diukur 2026-08-27: baseline 269 baris = **61 KB**
  per baca penuh; dengan 2 kolom teks baru jadi **~218 KB** (worst case cap penuh ~310 KB).
  Main membaca SELURUH tab **3x per pesan masuk** (`Read User STATS`, `Read STATS for HITL`,
  `Read STATS`) → ~0,6 MB per eksekusi, dari ~0,18 MB. Tidak terasa di skala sekarang.
  Proyeksi di 1000 baris: ~812 KB per baca, ~2,4 MB per eksekusi — di titik itu purge #26
  bukan lagi opsional. Cap sel sudah diperketat (konteks 800→500, last_msgs 600→450) untuk
  menahan laju ini; mitigasi berikutnya kalau perlu adalah membatasi range kolom pada dua
  node baca yang sebenarnya tidak butuh kolom baru — sengaja TIDAK dilakukan sekarang supaya
  tidak menyentuh node yang di luar cakupan.
- **Ringkasan tetap bisa meleset.** Jangkar `last_msgs` mengurangi drift, tidak menghapusnya. Kalau ada follow-up yang terasa salah paham, `konteks` di STATS bisa dibaca dan dikoreksi manual — kolomnya sengaja plain text.

---

## 9. Biaya

Haiku 4.5: **$1,00 / 1M token input, $5,00 / 1M output**.

| Panggilan | Perkiraan | Per panggilan |
|---|---|---|
| `Update Konteks` (tiap pesan masuk) | ~1.050 in / ~200 out | ~$0,0021 |
| `Compose Follow-up` (tiap follow-up) | ~800 in / ~120 out | ~$0,0014 |

Pada 269 lead dengan interval 48 jam, steady state ≈ 135 follow-up/hari ≈ **$0,19/hari**. Termasuk update konteks, realistis **di bawah $10/bulan**.

Prompt caching tidak dipasang dan memang tidak akan membantu: prefiks minimum yang bisa di-cache ~1.024 token, sedangkan blok instruksi statis di sini di bawah itu dan sisanya berubah per user.

---

## 10. Verifikasi yang sudah dijalankan (statis)

Belum diuji terhadap sheet dan n8n sungguhan. Dry run di §7 langkah 8 adalah tes pertamanya.

- JSON valid; urutan key root = export live n8n; `id`/`versionId`/`meta.instanceId` terisi.
- **0 byte CR** — LF murni, tanpa BOM, kedua file.
- **0 referensi node mati** yang hidup. (Satu kemunculan `$('Read LINGKUNGAN Data')` tersisa di **baris komentar** changelog `FAQ Retrieve` — bawaan sejak sebelum patch ini, bukan kode aktif.)
- 0 koneksi dangling; nama node unik.
- **Tree-sitter: 21/21 node Code Main dan 6/6 node Code Follow-up bebas syntax error.**
- 0 pemakaian `$(...).item` (konvensi proyek: `.first()`); 0 kredensial Kirimi plaintext.
- 35 cek struktural (rantai koneksi, mapping kolom, urutan claim-sebelum-compose, credential) — semua lolos.
- **Simulasi guard: 16/16** — 5 pesan wajar lolos, 11 pelanggaran (harga penuh, `15jt`, `2.500.000`, `5%`, `20 tahun`, URL, nomor telepon, kosong, terlalu pendek, tag bocor, "500 juta") semuanya tertolak dengan alasan yang benar.
- **Uji regresi terhadap file pre-patch: 22/22 lolos** — 0 node lama hilang, isi node lama
  berubah HANYA pada yang disengaja (Main: `Process Counter & Merge Data`, `Update to STATS`;
  FU: `Parse Config FU`, `Filter Kandidat`, `Kirim Follow-up`), **tepat 1 koneksi lama
  terputus per workflow** (titik sisip), `id`/`name`/`active`/`settings`/`meta`/`tags` dan
  seluruh credential node lama tidak berubah, `versionId` diperbarui.
- **Simulasi rolling `last_msgs`: 4/4** — menyimpan tepat 3 pesan terakhir, potong 200 char/pesan, batas sel 600, pesan kosong tidak menambah entri.

---

## 11. Perbaikan hasil review QA (2026-08-27, setelah patch awal)

Tiga hal ditemukan saat menguji "apakah yang lama tetap jalan", dan sudah diperbaiki:

| # | Temuan | Perbaikan |
|---|---|---|
| QA-1 | STATS dibaca **seluruh tab 3x per pesan masuk**; 2 kolom teks baru menaikkan payload 7,1x dengan cap awal | Cap diperketat: `konteks` 800→500, `last_msgs` 200/600→150/450. Turun ke 3,6x. Sisanya dilaporkan di §8, bukan disembunyikan |
| QA-2 | `Catat Kegagalan AI` memakai `String(e.error)`. Item error n8n sering berbentuk objek → laporan berisi `[object Object]`, tidak berguna | Ditangani per bentuk: objek diambil `.message`/`.description`, fallback `JSON.stringify` |
| QA-3 | `Filter Kandidat` menghitung `capByTime` dengan estimasi latency +2 dtk/kandidat, padahal kini ada 1 panggilan Haiku tambahan | Estimasi dinaikkan ke +4 dtk. Efeknya `cap` sedikit lebih konservatif — arah yang aman |

Efek samping yang disengaja dari urutan node baru: `Wait FU` sekarang berada **sesudah**
compose, jadi jarak antar pesan = jitter + latensi LLM (~1–2 dtk). Jaraknya jadi sedikit lebih
lebar dari yang dikonfigurasi — arah yang aman untuk risiko banned, bukan sebaliknya.

Satu batas yang tetap ada: penghitung kegagalan memakai `$getWorkflowStaticData('global')`.
Andal dalam satu eksekusi (yang memang cukup di sini, karena reset dan baca ada di eksekusi yang
sama), tapi kalau dua run sampai tumpang tindih daftarnya bisa bercampur. Dengan default 20
nomor/run (~11 menit) dan trigger tiap jam, itu tidak akan terjadi.

---

## 12. Perbaikan dari data live pertama (2026-08-27)

Steven menjalankan Gate 1 dan mengirim isi sel sungguhan. Dua hal muncul:

| # | Temuan | Perbaikan |
|---|---|---|
| L-1 | `last_msgs` dirakit dengan `slice(-3).join(SEP).slice(0, 450)`. Karena 3 x 150 + 8 pemisah = **458 > 450**, pemotongan memakan **sampai 8 karakter dari ujung giliran TERBARU** — bagian paling berharga sebagai jangkar | Dirakit dari giliran terbaru mundur ke belakang. Giliran terbaru dijamin utuh; yang tertua gugur duluan. Diverifikasi: cara lama 450 char/terbaru terpotong, cara baru 304 char/terbaru utuh |
| L-2 | Model konsisten menulis `LANGKAH BERIKUTNYA:` padahal prompt meminta `LANGKAH BERIKUT:`. Validasi hanya mengecek `TOPIK:` jadi lolos, tapi label jadi tidak seragam | Prompt diselaraskan ke `LANGKAH BERIKUTNYA:` — bahasa Indonesia yang lebih wajar dan memang itu yang dihasilkan model. Tidak ada yang mem-parse label ini, jadi baris lama tidak perlu diperbaiki |

**Dampak L-1 kecil** (maksimal 8 karakter, dan hanya saat ketiga giliran mentok cap) — tapi
cap-nya jadi tidak konsisten dengan dirinya sendiri, dan cara baru kebal terhadap perubahan cap
di kemudian hari.

Penilaian isi `konteks` dari data live itu: **bekerja seperti yang dirancang.** `LANGKAH
BERIKUTNYA` masih menyebut pengumpulan dokumen KPR wiraswasta padahal giliran terakhir sudah
pindah ke soal kapasitas parkir — persis perilaku yang diinginkan: informasi lama tidak hilang
saat topik bergeser.
