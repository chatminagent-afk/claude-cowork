---
name: reelscript-povstevens
description: Generate reel scripts, hooks, and captions for Steven's @povstevens Instagram (AI automation personal branding), built on jun_yuh's LIFE wheel + 3 Why storytelling framework, referencing the live script tracker. Use whenever Steven asks for a reel script, konten IG, script baru, hook, or caption — trigger on phrases like "bikinin script reel", "konten buat IG", "bikinin hook", "caption buat reel", or when he describes a work/debugging session and wants to turn it into content. Also use when revising or reviewing an existing reel script for @povstevens.
---

# Reel Script Generator (@povstevens)

Skill ini menghasilkan script reel Instagram untuk personal branding Steven di **@povstevens**. Tujuan akhirnya bukan views, tapi DM masuk → klien freelance. Formula dan formatnya sudah terbukti (video pertama menghasilkan klien tanpa ads), jadi konsistensi lebih penting daripada kreativitas format.

Skill ini **mewarisi seluruh isi skill umum `reelscript`** — bukan cuma LIFE wheel + 3 Why (ide & kedalaman cerita), tapi juga craft system-nya: hook system 6 tipe, struktur & prinsip menulis (But/Therefore, buang info mati, spesifik>generik, nulis buat diomongin), humor/progresi emosi/visual cues, daftar pola AI-writing yang dihindari, dan pacing (kata per durasi + read-aloud test). Baca `reelscript` dulu, baru tambahan khusus akun @povstevens di bawah — jangan duplikasi craft rules di sini. Kalau butuh script untuk akun lain (bukan @povstevens), pakai `reelscript` langsung.

> Series **NIGHT SHIFT** sudah tidak dipakai sejak 19 Agu 2026 — jangan pakai istilah "NIGHT SHIFT", "episode"/"eps. N", atau hashtag `#nightshift` lagi kecuali Steven eksplisit minta balik ke branding itu. Batch script lama dari era itu diarsipkan di folder `2026-07-14-reels-batch-1\` (di-rename dari `night-shift-batch-1` pada 2026-09-08) sebagai catatan historis saja — bukan referensi format aktif.

## Sumber kebenaran — satu-satunya: tracker xlsx

Baca dulu sebelum menulis apa pun — jangan mengandalkan ingatan atau file lama:

**`D:\Documents\Claude Cowork\VIRA\reels\script-reels-vira-tracker.xlsx`**, sheet **"Script Tracker"**. Kolomnya:

| Kolom | Isi |
|---|---|
| A — No. | Nomor urut script (bukan "episode") |
| B — Judul / Hook Singkat | Judul pendek buat identifikasi baris |
| C — Script (Hook, Isi, CTA) | Isi lengkap: `HOOK:` / `ISI:` / `REVEAL:` / `CTA:` sebagai paragraf teks biasa |
| D — Caption IG | Caption final + hashtag |
| E — Status | Dropdown: `Not Done` / `Done Take Video` / `Done Edit` / `Done Upload` |
| F/G/H | Tanggal Take Video / Edit Selesai / Upload |
| I — Link Video Final | Path lokal atau link setelah tayang |
| J — Catatan | Flag manual: privasi, alasan dibuat, hal yang perlu dicek sebelum syuting |

Sheet kedua **"Panduan"** berisi penjelasan dropdown status — cek kalau perlu, tapi jangan diedit.

**Cara pakai sebelum menulis script baru:**
1. Baca beberapa baris terakhir di tracker (bukan cuma baris 1) — itu kalibrasi gaya, panjang, dan konvensi *paling update*, karena gaya sudah berevolusi beberapa kali (lihat riwayat revisi di kolom Catatan tiap baris).
2. Nomor baru = nomor terakhir di kolom A + 1. Jangan menimpa baris yang sudah ada, jangan pakai penomoran "episode".
3. Kalau tracker tidak bisa diakses (file pindah/terkunci), lanjut pakai aturan di bawah — semuanya cukup untuk menulis script yang benar — tapi beri tahu Steven bahwa kalibrasi dari tracker dilewati.

## Fondasi — LIFE wheel & teknik 3 Why (jun_yuh)

Dipakai untuk njawab 2 pertanyaan yang paling sering bikin macet: **mau posting apa** (LIFE) dan **gimana bikin ceritanya kena** (3 Why → depth Raw). Jalankan ini di tahap ideation, sebelum masuk ke tabel script.

**LIFE — sumber ide cerita.** Hampir semua cerita hidup masuk salah satu dari 4 kategori:
- **L**ove — relasi, hobi
- **I**dentity — budaya, gender, usia, keyakinan
- **F**itness — pikiran, tubuh, spirit (termasuk burnout/grind)
- **E**arnings — karier, klien, skill

Konten @povstevens sumbernya paling sering **Earnings** (kerjaan/klien/skill) dan **Fitness** (begadang, capek, grind siang QA-malam ngoprek). Kalau lagi kehabisan ide, cek 4 kategori ini dulu sebelum brainstorm dari nol.

**3 Depth — safe / real / raw.** Cerita yang sama bisa diceritakan di 3 level kedalaman, dan cuma level terdalam yang bikin penonton connect:
1. **Safe** — fakta permukaan, aman, tapi boring
2. **Real** — udah personal, tapi masih nyaman diomongin
3. **Raw** — ketakutan/insecurity yang mendasari; ini yang bikin penonton ngerasa sesuatu tiap nonton

**Teknik: 3 Why.** Sebelum nulis beat *story* (ISI), tanya "kenapa ini penting?" tiga kali berturut-turut — tiap jawaban gali lebih dalam dari sebelumnya, bukan mengulang:
1. Kenapa ini penting? → jawaban pertama = **safe**
2. Kenapa lagi? → jawaban kedua = **real**
3. Tapi kenapa sebenarnya? → jawaban ketiga = **raw**, ini yang dipakai jadi inti hook/story — bukan jawaban pertama.

Contoh (adaptasi ke konteks Steven):
> Topik: begadang ngoprek n8n abis kerja QA seharian (kategori Fitness/Earnings)
> 1. Kenapa penting? → Aku mau punya penghasilan tambahan di luar gaji kantor (safe)
> 2. Kenapa lagi? → Aku capek ngerasa stuck di karier yang udah predictable (real)
> 3. Tapi kenapa sebenarnya? → Aku takut suatu hari kena PHK dan nggak punya apa-apa buat dipegang selain gaji bulanan — jadi tiap malem aku buktiin ke diri sendiri kalau aku bisa bangun sesuatu sendirian (raw)

**Cara pakai:** untuk beat *story* (ISI/REVEAL), jalankan 3 Why ini secara internal dulu, lalu tulis dari jawaban **raw** — bukan dari jawaban safe. Tampilkan progresi 3 Why sebagai catatan singkat sebelum tabel script (lihat format output), supaya Steven bisa lihat alasannya sebelum approve — terutama karena layer raw kadang menyentuh hal yang lebih personal, jadi dia yang putuskan apakah nyaman dipakai atau perlu ditumpulkan satu notch ke "real".

## Menulis hook — pola andalan akun ini

Hook adalah baris `HOOK:` di kolom C dan judul singkat di kolom B. Aturan bentuk umum (panjang 8-12 kata, SVO biasa, baca-keras-keras, dll.) ada di `reelscript` Bagian 4 — berlaku di sini juga. Dua pola di bawah ini **sudah terbukti buat @povstevens** (video pertama & beberapa episode berikutnya) — pakai duluan sebelum eksplorasi 6 tipe hook generik di `reelscript`:

**Pola 1 — WTF hook (konkret + ironis/kontradiktif).** Cocok buat cerita hasil/insiden konkret. Dua klausa yang tabrakan secara nilai/ekspektasi, atau angka spesifik yang bikin reaksi "lah kok bisa?" — bukan kategori umum/edukatif ("cara untung dari X" itu hook lemah). Contoh acuan: "hutang 2M lunas karena meme coin", "omset naik, suami dicerai istri".

**Pola 2 — Confession + urgency.** Cocok buat opini/insight personal Steven soal arah AI/automation. Opener "kalau boleh jujur..." (sinyal konfesi, insider truth bukan jualan) + klaim dikasih batas waktu/kuota konkret ("1-2 tahun", bukan "someday"). Contoh acuan: "kalau boleh jujur, kamu cuma punya 1-2 tahun dari sekarang buat manfaatin AI gold rush ini."

Klaim di hook (angka, kuota, urgency) tetap harus grounded — cek bagian Privasi & Fakta di bawah sebelum ditulis final.

## Positioning — wajib konsisten di tiap reel

- Payung identitas: **AI automation**, BUKAN "AI chatbot" sebagai label diri. Alasannya: Steven belum mengunci porsi AI vs automation murni di kerjaan freelance-nya, dan automation deterministik risikonya lebih kecil. Jadi jangan tulis "aku bikin AI chatbot" sebagai label diri — pakai "aku bikin sistem/otomasi buat bisnis kecil", lalu sebut chatbot sebagai contoh konkret produk (menyebut produknya sebagai "AI chatbot"/"AI Customer Service" tetap boleh).
- **VIRA** = nama produk flagship (asisten virtual WhatsApp), aman disebut bebas. Yang TIDAK aman: mengaitkannya ke nama klien asli tanpa izin (lihat bagian Privasi).
- Pembeda terkuat: **"aku yang bukan programmer"** + latar QA bank ("aku ngetes sampai ketemu bug-nya"). Relatable, bukan flexing. Jaga bahasa tetap awam, analogi sehari-hari (contoh yang sudah dipakai: race condition = "dua orang nulis di buku yang sama").
- Anchor identitas: "siang QA bank, malam ngoprek otomasi".
- Target penonton: owner bisnis muda yang bisnisnya lagi tumbuh & siap scale up — bukan "UMKM capek bales chat" semata.
- **Show, don't claim** (framework Pandji marketing vs branding): script yang cuma bilang "aku pegang prinsip X" itu masih level iklan/klaim, bukan branding. Proof-by-demo (ajak chat/coba sendiri ke nomor AI persona Steven `6285155202354`) jauh lebih kuat daripada narasi klaim. Benang merah REVEAL yang disukai: owner bisa tenang meski lagi tidur/sibuk, karena leads yang masuk WhatsApp tetap dihandle VIRA — fitur boleh disebut tapi harus nyambung ke perasaan ini, bukan berhenti di level listing fitur.

## Gaya: document the process (bukan presentasi produk)

Penonton diajak ikut proses building/belajar/debugging saat kejadian — bukan disuguhi hasil jadi. Ini keputusan sadar Steven: konten proses lebih relate, mengikat produk ke sosoknya, dan jualan terjadi implisit.

- Buka dengan **momen kerja**, bukan hasil: "jam 11 malem, klien chat…" bukan "ini fitur baruku".
- Selalu ada **beat gagal/belajar**: "aku sempet ngira X, ternyata salah" — imperfection membangun trust.
- Visual dari **footage bank** (klip asli sesi kerja: layar n8n mock, timestamp malam, meja, kopi) — raw > polished, jangan minta staging semua.
- Narasi iterasi boleh dipakai ("VIRA udah versi 4") — angka harus grounded, lihat bagian Privasi & Fakta.

## Formula & aturan per pilar

Struktur cerita: **HOOK → ISI (pain/story) → REVEAL (proof/prinsip) → CTA**, dengan beat *story* ditarik dari layer **raw** hasil 3 Why kalau relevan.

| Pilar | Isi | CTA |
|---|---|---|
| **A — Demo/Proof** | Demo VIRA, case study, fitur — diframe "ikut aku ngetes/bangun ini", bukan "ini produkku" | CTA eksplisit boleh (ajak chat/DM langsung) |
| **B — Build-in-public/debugging** | Cerita bug & proses fix dari kerjaan nyata | Follow/share/save saja — JANGAN hard-sell |
| **C — Edukasi/opini UMKM** | Pain-point, prinsip, atau opini — selalu di-ground di pengalaman nyata | Follow, atau CTA soft ("chat kalau penasaran") |
| **A/C hybrid** | Argumen/proof yang cukup kuat buat CTA eksplisit tapi framing-nya tetap edukasi/opini | CTA boleh eksplisit |

Kalau reel-nya murni personal/komedi tanpa pitch bisnis natural (nggak pas dipetakan ke A/C di atas), CTA-nya follow-only kayak Pilar B — dan **jangan dipaksa nyambung ke pitch VIRA di kalimat/napas yang sama dengan punchline** (lihat `reelscript` Bagian 6, "jangan sambung punchline ke CTA"). Grafting pitch ke ending komedi itu yang paling sering bikin script kerasa dipaksa iklan.

**Durasi target: 45–60 detik** — konvensi terbaru, berlaku lintas pilar (dulu pilar B/C/D ditarget lebih pendek 15-30 dtk, tapi praktik terkini konsisten pakai 45-60 dtk karena beat REVEAL butuh ruang). Per tabel kata/durasi di `reelscript` Bagian 8, itu setara **~100-150 kata VO** — pakai patokan itu buat cek draft kepanjangan/kependekan sebelum ngukur di kepala. Pilar B (bug story) boleh lebih ringkas 20-40 dtk (~45-90 kata) kalau ceritanya natural pendek — jangan dipaksa panjang. Kalau draft lewat target, pangkas beat penjelasan teknis yang bisa dipadatkan — jangan naikkan target durasinya. Selalu tutup dengan read-aloud test (`reelscript` Bagian 8) sebelum dianggap final.

## Format output — ikuti struktur ini, siap tempel ke tracker

```markdown
### Script [No.] — [Judul]
- **Pilar X** / Durasi target **XX–XX dtk**

**Analisis 3 Why** *(untuk beat story di ISI/REVEAL, kalau relevan)*
- Kategori LIFE: [L/I/F/E]
- Safe: ...
- Real: ...
- Raw: ... ← dipakai jadi inti hook/story

**Script (kolom C — tempel langsung)**

HOOK: ...

ISI: ...

REVEAL: ...

CTA: ...

**Caption IG (kolom D — tempel langsung)**

> [paragraf caption, 2-4 kalimat pendek]
> [CTA]
> #otomasibisnis #aiautomation #vira [+2-3 hashtag tema]

**Catatan (kolom J — tempel langsung)**
- [alasan/tanggal dibuat, pilar, durasi, hal yang perlu dicek manual sebelum syuting/upload — SPESIFIK ke script ini, bukan checklist generik]

**Persiapan aset**
- [footage bank / screen-record / talking head / b-roll yang dibutuhkan]
```

Aturan penulisan:
- Bahasa lisan Indonesia santai khas Steven: "aku", "nggak", "kayak", "beneran", "nih". Tulis persis seperti diucapkan — ini yang dia baca saat rekam.
- HOOK/ISI/REVEAL/CTA ditulis sebagai paragraf teks biasa (bukan tabel per-detik dengan kolom Visual/On-screen text) — itu format tracker saat ini. Kalau Steven minta breakdown timing per beat untuk kebutuhan syuting, tawarkan sebagai lapisan tambahan terpisah, bukan menggantikan format tracker.
- Caption bilingual boleh (Indo utama), santai, bukan bahasa marketing formal.
- Hashtag inti selalu `#otomasibisnis #aiautomation #vira`, ditambah 2-3 tag tema spesifik ke isi script.

## Privasi & fakta — jalankan sebelum menyerahkan script

Setiap script wajib ditutup dengan catatan privasi yang spesifik (bukan checklist generik). Aturan minimum (versi lengkap ada di skill `privacy-check` — pakai itu sebagai gate terakhir sebelum Steven post):

- Demo/screen-record selalu pakai bot demo + data dummy — jangan pernah environment production klien.
- Jangan tampilkan nama/nomor WA user asli, isi chat asli, Google Sheet ID/URL, kredensial Kirimi, atau layar n8n production.
- **Nama klien asli tidak boleh pernah disebut.** Default anonim: "klien yang platform edukasi" dan "klien yang developer properti" — dua tenant produksi VIRA saat ini. Jangan sebut nama tempat kerja Steven (bank) secara eksplisit — pakai "kantor"/"tempat aku kerja".
- **Cerita bug hanya untuk bug yang sudah difix DAN live di production.** Kalau Steven cerita bug tapi tidak bilang fixnya sudah deploy, tanyakan — jangan diasumsikan.
- Angka yang dipakai (jumlah klien, jumlah pesan, dll.) harus grounded ke fakta VIRA yang terverifikasi — kalau nggak yakin sumbernya, tanyakan ke Steven sebelum dipakai sebagai klaim, jangan taruh sebagai statistik pasti.
- **Klaim/janji publik** (kuota klien, garansi, batas waktu) yang keluar dari mulut Steven sendiri boleh dipakai persis, tapi flag di kolom Catatan bahwa begitu di-post ini jadi komitmen publik — minta Steven konfirmasi dulu kalau itu representasi akurat dari rencana bisnisnya, bukan cuma angle konten.
- Crop/blur kalau ada notifikasi atau nomor asli di status bar.
- Layer **raw** dari analisis 3 Why kadang menyentuh hal personal (relasi, keuangan, insecurity) — cek juga apakah detailnya nyaman dibagikan ke publik, bukan cuma soal data klien/VIRA.

## Setelah script jadi

Tawarkan (jangan langsung eksekusi): menambahkan baris baru ke tracker `script-reels-vira-tracker.xlsx` (kolom A-E, J diisi; F-I dikosongkan sampai produksi jalan; Status default `Not Done`), dengan style/formatting mengikuti baris sebelumnya persis (font Arial 10, border, wrap text).
