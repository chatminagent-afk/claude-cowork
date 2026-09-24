# Minggu 4 (eps. 10–12): Pelajaran & Hasil

Tema minggu ini: naik altitude — pelajaran soal biaya, mindset QA, lalu tutup season dengan rekap perjalanan + CTA terkuat batch ini.

*Revisi 2026-07-21: script disesuaikan dengan framework jun_yuh (LIFE wheel + 3 Why) — tiap beat story digali sampai layer raw. Struktur, durasi, pilar, dan aturan privasi tetap sama seperti versi awal.*

---

### Reel — AI Murah Justru Bongkar Bug (eps. 10)
- **Pilar C** / Durasi target **15–30 dtk** / Jadwal: **Senin 17 Agu, malam**

**Analisis 3 Why**
- Kategori LIFE: **E** (kompetensi kerja solo) + **F** (rasa aman/parno)
- Safe: Ganti AI murah, lima bug muncul barengan.
- Real: Bug bukan bawaan AI murahnya — bug-nya udah ada dari dulu di arsitektur buatanku.
- Raw: Ini bikin aku ngerasa nggak aman — berapa lama aku "untung" karena ditutupin komponen yang lebih pinter, bukan karena kerjaanku sendiri udah bener? Ini ketakutan siapa pun yang kerja sendirian tanpa tim buat ngecek: kamu nggak pernah beneran tau separah apa fondasimu sampai penyangganya dicabut. ← dipakai jadi inti VO closing

**Script**

| Waktu | Visual | VO (persis diucapkan) | On-screen text |
|---|---|---|---|
| 0:00–0:04 | Talking head | Aku ganti otak bot-ku ke versi yang lebih murah, biar hemat. Seminggu kemudian: lima bug muncul barengan. | "Eps. 10" / "ganti **AI murah** → 5 bug" |
| 0:04–0:13 | Ilustrasi mobil: mesin gede vs rem aus | Yang menarik: bug-nya bukan bawaan si AI murah. Bug-nya udah ada dari dulu — di arsitektur buatanku. AI yang mahal itu cukup pinter buat **nutupin** kesalahan desainku. Kayak mesin gede yang nutupin rem aus: kerasa aman, padahal enggak. | "AI mahal = **nutupin** bug" / "bug-nya **punyaku**, bukan punya AI" |
| 0:13–0:21 | Ilustrasi angka: biaya per balasan normal vs pas error | Dan bug itu ada harganya. Pas lagi error, satu balasan bisa makan biaya berkali-kali lipat dari normal — karena bot-nya muter-muter manggil fungsi yang nggak ada. Hemat di depan, boncos di belakang. | "1 balasan error = **berkali-kali lipat** biaya normal" |
| 0:21–0:30 | Talking head | Ini yang bikin aku parno: kerja sendirian tanpa tim ngecek, aku nggak pernah beneran tau separah apa fondasiku — sampai penyangganya dicabut. Sejak itu: arsitektur bener dulu, baru mainin biaya. Besok: tiga kali aku yakin, tiga kali salah. | "kerja **sendirian** = nggak ada yang ngecek" / "besok: **yakin 3x, salah 3x**" |

**Caption IG**

> Eps. 10 🌙
> Plot twist terbesar di proyekku: AI yang mahal ternyata diam-diam nutupin bug arsitektur buatanku sendiri. Begitu diganti yang murah, semua retakannya keliatan — lima bug sekaligus.
> Yang bikin aku parno: kerja sendirian tanpa tim buat ngecek, aku nggak pernah beneran tau separah apa fondasiku — sampai penyangganya dicabut.
> Pelajarannya bukan "jangan pakai AI murah". Pelajarannya: kalau sistemmu cuma jalan di komponen termahal, yang bermasalah bukan komponennya.
> #otomasibisnis #aiautomation #umkmindonesia #belajarai

**Persiapan aset**
- Talking head
- Ilustrasi mobil (mesin vs rem) — bisa animasi teks sederhana
- Ilustrasi perbandingan biaya (bar sederhana, tanpa angka dolar spesifik di layar)

**Checklist privasi sebelum post**
- Semua 5 bug era V2 sudah difix sejak V3 — aman diceritakan
- Jangan sebut nama model/vendor AI spesifik & angka biaya dolar eksak di layar (internal klien) — cukup "berkali-kali lipat"
- Jangan sebut budget bulanan klien
- Ilustrasi buatan sendiri, bukan dokumen root-cause asli
- Beat raw ("parno kerja sendirian") itu personal soal rasa aman profesional, bukan data klien — aman dibagikan

---

### Reel — Salah Tebak 3x (eps. 11)
- **Pilar B** / Durasi target **15–30 dtk** / Jadwal: **Rabu 19 Agu, malam**

**Analisis 3 Why**
- Kategori LIFE: **E** (kepercayaan diri profesional) + **I** (identitas sebagai orang yang teliti)
- Safe: Tiga kali yakin nemu penyebab bug, tiga kali salah.
- Real: Pelajaran QA — yakin bukan bukti.
- Raw: Tiap salah tebak itu bukan cuma buang waktu — itu momen aku ngaku ke diri sendiri kalau rasa yakinku, modal utamaku buat pede megang sistem orang, ternyata nggak bisa dipegang. Kalau intuisiku aja salah 3x berturut-turut, gimana klien harus percaya sama aku? Jawabannya bukan dari yakinnya aku — tapi dari disiplin proses yang nggak butuh aku "yakin". ← dipakai jadi inti VO closing

**Script**

| Waktu | Visual | VO (persis diucapkan) | On-screen text |
|---|---|---|---|
| 0:00–0:04 | Talking head, ngaku | Tiga kali aku yakin banget udah nemu penyebab bug-nya. Tiga kali salah. | "Eps. 11" / "yakin 3x, **salah 3x**" |
| 0:04–0:12 | Ilustrasi: link nggak sampai ke user | Kasusnya: link pendaftaran kadang nggak kekirim ke user. Tebakan pertamaku: perangkat pengirimnya yang salah. Kufix, pede. Tes lagi — masih gagal. | "tebakan 1: **device** ❌" |
| 0:12–0:20 | Ilustrasi lapisan: tebakan 2 salah lagi, lapisan makin dalam | Tebakan kedua, masih salah juga. Baru di percobaan ketiga ketemu akar aslinya: jalur pengirim link-nya ternyata memang **dimatiin** dari desain versi lama. Bukan rusak — tapi nggak pernah dinyalain lagi. | "tebakan 2 ❌" / "akar: jalurnya **sengaja mati** dari versi lama" |
| 0:20–0:30 | Talking head | Tiap salah tebak itu bukan cuma buang waktu — itu aku ngaku ke diri sendiri kalau rasa yakinku nggak bisa dipegang. Kalau intuisiku aja salah 3x, gimana klien harus percaya sama aku? Makanya sekarang: reproduksi dulu, buktiin, baru fix. Follow — Sabtu, episode penutup. | "yakin ≠ **bukti**" / "final: **1 video → versi 4**" |

**Caption IG**

> Eps. 11 🌙
> Debugging itu pelajaran rendah hati: tiga kali aku yakin udah ketemu penyebabnya, tiga kali salah. Akar masalahnya ternyata bukan yang rusak — tapi jalur yang diam-diam dimatikan dari desain versi lama.
> Tiap salah tebak itu bukan cuma buang waktu — itu aku ngaku ke diri sendiri kalau rasa yakinku nggak bisa dipegang. Kalau intuisiku aja bisa salah 3x, gimana klien harus percaya sama aku?
> Prinsip yang selalu nyelametin aku sekarang: jangan percaya rasa yakin, percaya hasil tes. Karena yang dipertaruhkan bisnis mereka, bukan eksperimen.
> Follow — Sabtu ini episode penutup season: rekap dari satu video sampai bot versi 4.
> #otomasibisnis #aiautomation #debugging #qamindset

**Persiapan aset**
- Talking head
- Ilustrasi tebakan berlapis (teks animasi ❌❌✓)
- Opsional b-roll layar n8n mock sedang menelusuri node

**Checklist privasi sebelum post**
- Rangkaian fix ini (V3.2→V3.4) sudah lama live — aman
- Jangan tunjukkan link pendaftaran asli klien atau nama form-nya
- Layar n8n = mock
- Jangan sebut nama fitur internal spesifik yang mengarah ke identitas klien
- Beat raw (yakin ≠ bukti, soal kepercayaan diri sendiri) itu personal, bukan data klien — aman dibagikan

---

### Reel — 1 Video → 1 Klien → Versi 4 (eps. 12 — Season Finale) 🎯
- **Pilar A (jualan)** / Durasi target **30–60 dtk** / Jadwal: **Sabtu 22 Agu, malam**

**Analisis 3 Why**
- Kategori LIFE: **I** (identitas: dari QA jadi builder) + **E** (career risk)
- Safe: Satu video jadi satu klien, sistem sekarang versi 4.
- Real: Perjalanan dari nol ke sistem yang dipercaya butuh proses panjang.
- Raw: Video pertama itu kuposting tanpa ekspektasi — jujur, aku setengah berharap nggak ada yang notice, karena aku takut kelihatan "belum ahli" di depan followers yang kenal aku sebagai QA, bukan builder. Ternyata kejujuran soal belum-ahlinya itu yang bikin orang percaya. Season ini ngebuktiin: aku nggak perlu nunggu jadi ahli buat mulai dipercaya. ← dipakai jadi inti VO pembuka

**Script**

| Waktu | Visual | VO (persis diucapkan) | On-screen text |
|---|---|---|---|
| 0:00–0:07 | Talking head, tenang | Season pertama series ini selesai. Video pertama itu kuposting tanpa ekspektasi — jujur, aku setengah berharap nggak ada yang notice, takut kelihatan 'belum ahli'. | "Eps. 12" / "takut kelihatan **'belum ahli'**" |
| 0:07–0:17 | Flashback: cuplikan video perdana + b-roll proses | Ternyata kejujuran itu yang bikin orang percaya. Satu bisnis DM aku. Jadi klien pertamaku — dan dari situ, begadang, salah tebak, hapus fitur sendiri, benerin pesan yang hilang, sampai sistemnya sekarang versi empat. | "1 video → **1 klien** → versi **4**" |
| 0:17–0:30 | Screen-record demo A Course + sheets dummy berjalan | Hari ini sistem itu megang seratus enam puluhan percakapan — delapan ratusan pesan udah lewat situ. Ada FAQ seratus lima entri yang dia kuasain, dan booking yang kecatet otomatis tanpa ada yang pegang HP. | "**164** percakapan · **834** pesan" / "**105** FAQ · booking **otomatis**" |
| 0:30–0:42 | Talking head | Aku nggak akan bilang ini gampang — kalian udah nonton sebelas episode buktinya. Sistem yang udah ngelewatin kasus nyata lebih layak dipercaya daripada demo yang mulus. Dan aku nggak jual template — sistem yang kubangun ngikutin cara bisnismu jalan, dan aku sendiri yang jagain. | "**teruji** kasus nyata" / "bukan template — aku yang **jagain**" |
| 0:42–0:54 | Talking head, CTA utama | Kalau bisnismu lagi tumbuh dan kamu ngerasa jadi bottleneck-nya sendiri — bales chat sampai malem, follow-up kelewat — aku bisa bantu. Komen **OTOMASI** atau DM aku. Kita mulai dari ngobrol, bukan dari bayar. | "komen **OTOMASI**" / "DM @povstevens · WA 085155202354" |
| 0:54–1:00 | Talking head, teaser | Dan season dua? Aku lagi nyiapin sistem kedua — beda industri, masalah yang sama: kerjaan manual yang nyita hidup owner-nya. Sampai ketemu di season 2. | "**season 2**: coming soon" |

**Caption IG**

> Eps. 12 🌙 SEASON FINALE
> Video pertama itu kuposting tanpa ekspektasi — jujur, aku setengah berharap nggak ada yang notice, karena takut kelihatan "belum ahli". Ternyata justru kejujuran itu yang bikin orang percaya.
> Satu video → satu klien → bot versi 4. Di antaranya: pesan hilang, bot amnesia, fitur andalan yang kuhapus sendiri, dan banyak malam yang panjang.
> Sekarang: 164 percakapan, 834 pesan, 105 FAQ, booking yang jalan sendiri. Bukan karena sistemnya sempurna — tapi karena tiap rusak, dibenerin, dan tiap versi makin kuat.
> Aku nggak jual template. Sistem yang kubangun ngikutin cara bisnismu jalan sendiri — dan aku sendiri yang jagain.
> Kalau kamu owner yang masih jadi customer service dadakan buat bisnismu sendiri: komen "OTOMASI" atau DM aku. Mulai dari ngobrol dulu.
> Season 2 segera. Terima kasih udah nemenin season ini 🙏
> #otomasibisnis #aiautomation #whatsappbusiness #ukmnaikkelas

**Persiapan aset**
- Cuplikan video perdana (flashback 2–3 dtk)
- Kompilasi b-roll dari eps 1–11 (proses, malam, layar mock)
- Screen-record demo A Course + Google Sheets dummy
- Talking head dengan energi paling hidup di batch ini — kecuali beat pembuka (0:00–0:07) yang lebih pelan/jujur
- Setelah tayang: pin reel ini menggantikan/mendampingi eps 3

**Checklist privasi sebelum post**
- Angka 164/834 = counter per 7 Jul 2026; kalau tayang 15 Agu, cek angka terbaru di STATS dan update VO-nya (atau tetap sebut "seratus enam puluhan" bila belum sempat cek — jangan mengklaim angka yang lebih tinggi tanpa data)
- Booking "5 booking, 4 confirmed" tidak disebut angka eksaknya di VO — aman; kalau mau disebut, pakai angka dari sheet terbaru
- Screen-record = demo A Course + sheets DUMMY, bukan STATS production
- Flashback video perdana: pastikan tidak ada frame chat asli Akademi Arsi dengan nomor user terlihat (blur seperti aslinya)
- Jangan sebut nama klien; "satu bisnis DM aku" cukup
- Teaser season 2 (RAPI): jangan tunjukkan backend v4 TIM Interior — kalau mau tease visual, pakai demo v5 de-branded
- Beat raw (takut kelihatan "belum ahli") itu personal soal identitas dan rasa percaya diri — aman dibagikan, dan justru ini yang bikin finale-nya kuat
