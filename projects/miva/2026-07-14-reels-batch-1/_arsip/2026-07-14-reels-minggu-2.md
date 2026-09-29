# Minggu 2 (eps. 4–6): Bug Wars

Tema minggu ini: transparansi. Dua cerita bug yang sudah difix (trust), ditutup satu episode trade-off desain yang sekaligus jualan halus. Semua bug di minggu ini sudah diverifikasi fixed & live di V4 — **cek sekali lagi di n8n sebelum rekam.**

*Revisi 2026-07-21: script disesuaikan dengan framework jun_yuh (LIFE wheel + 3 Why) — tiap beat story digali sampai layer raw. Struktur, durasi, pilar, dan aturan privasi tetap sama seperti versi awal.*

---

### Reel — Bot-ku Amnesia Tiap Ganti Jam (eps. 4)
- **Pilar B** / Durasi target **15–30 dtk** / Jadwal: **Senin 3 Agu, malam**

**Analisis 3 Why**
- Kategori LIFE: **E** (kualitas kerja) + **I** (identitas sebagai "yang teliti")
- Safe: Bug bikin bot lupa obrolan tiap ganti jam.
- Real: Ini salahku sendiri, bukan AI-nya.
- Raw: Aku takut banget kalau klien nemuin bug ini duluan sebelum aku — karena itu ngebuktiin ketelitian yang aku jual ("aku bukan programmer, tapi teliti") ternyata nggak beneran. Kalau hal sedasar ini lolos, seluruh alasan orang harus percaya sama aku ikut goyah. ← dipakai jadi inti VO closing

**Script**

| Waktu | Visual | VO (persis diucapkan) | On-screen text |
|---|---|---|---|
| 0:00–0:03 | Talking head, ekspresi "capek tapi geli" | Bot-ku pernah ngalamin amnesia. Beneran lupa semua obrolan — tiap ganti jam. | "Eps. 4" / "bot **amnesia** tiap jam" |
| 0:03–0:11 | Ilustrasi/animasi teks: chat jam 8 nyambung, jam 9 bot nanya dari nol | Jadi user udah ngobrol panjang, udah dikasih rekomendasi. Eh, dua jam kemudian dia balik nanya — bot-nya nyapa dari nol, kayak nggak kenal. Coba bayangin jadi customer-nya: cerita panjang, disuruh ngulang dari nol — kamu balik lagi, nggak? | "jam 8: **ngobrol panjang**" / "jam 10: '**halo, ada yang bisa dibantu?**'" / "kamu balik lagi, **nggak**?" |
| 0:11–0:19 | Screen-record n8n mock, zoom ke satu setting | Ternyata salahku sendiri: 'ingatan' bot-nya kudesain reset tiap jam berganti. Ibaratnya resepsionis yang mejanya dibersihin paksa tiap pergantian jam, padahal tamunya masih berdiri di depannya. | "**memory key** ke-reset tiap jam" / "salahku **sendiri**" |
| 0:19–0:28 | Talking head | Yang bikin aku paling takut bukan bug-nya — tapi mikir kalau klien nemuin ini duluan sebelum aku. Ketelitian itu satu-satunya alasan orang harus percaya sama aku yang bukan programmer. Udah difix. Follow — eps. 5 lebih serem. | "takut **klien nemu duluan**" / "udah **difix** ✓ · follow → eps. 5" |

**Caption IG**

> Eps. 4 🌙
> Bot-ku pernah "amnesia" tiap ganti jam — user yang udah ngobrol panjang tiba-tiba disapa dari nol lagi.
> Coba bayangin kamu jadi customer-nya: udah cerita panjang, disuruh ngulang dari nol. Balik lagi nggak?
> Yang bikin aku paling takut bukan bug-nya — tapi mikir kalau klien nemuin ini duluan sebelum aku. Ketelitian itu satu-satunya alasan orang harus percaya sama aku yang bukan programmer.
> Follow — episode berikutnya bug yang lebih serem: pesan user hilang tanpa jejak.
> #otomasibisnis #aiautomation #debugging #buildinpublic

**Persiapan aset**
- Talking head
- Ilustrasi chat buatan sendiri (teks animasi) — JANGAN screenshot chat asli
- Screen-record n8n MOCK yang menirukan setting memory (bukan workflow production)

**Checklist privasi sebelum post**
- Ilustrasi chat = buatan sendiri/dummy, bukan chat user asli
- Layar n8n = mock; jangan sampai node credentials atau nama workflow production kerekam
- Bug ini fixed sejak V3 dan live — aman diceritakan; jangan sebut detail teknis key/format ID yang bisa jadi peta serangan
- Beat raw ("takut klien nemu duluan") itu personal soal insecurity profesional, bukan data klien — aman dibagikan, tapi tetap keputusan Steven

---

### Reel — Pesan User Hilang Tanpa Jejak (eps. 5)
- **Pilar B** / Durasi target **15–30 dtk** / Jadwal: **Rabu 5 Agu, malam**

**Analisis 3 Why**
- Kategori LIFE: **E** (tanggung jawab ke bisnis klien) + **F** (kecemasan/ketenangan pikiran)
- Safe: Bug bikin 1 pesan hilang tanpa error.
- Real: Race condition ini bisa bikin calon customer ilang tanpa siapa pun sadar.
- Raw: Yang bikin aku nggak bisa tidur bukan bug-nya — tapi mikirin udah berapa lama ini kejadian sebelum aku sadar, dan berapa banyak calon customer klien yang udah ilang diam-diam sementara aku pede sistemnya baik-baik aja. Ketakutan terbesarku megang sistem orang lain bukan sistem down (itu keliatan) — tapi sistem yang KELIHATAN baik-baik aja padahal diam-diam ngerugiin orang. ← dipakai jadi inti VO closing

**Script**

| Waktu | Visual | VO (persis diucapkan) | On-screen text |
|---|---|---|---|
| 0:00–0:04 | Talking head, serius | User ngetik tiga pesan. Yang kebaca sistem cuma dua. Satu pesan hilang — tanpa jejak, tanpa error. | "Eps. 5" / "1 pesan **hilang tanpa jejak**" |
| 0:04–0:12 | Ilustrasi: tiga bubble chat, bubble tengah memudar | Ini tipe bug paling nyebelin: nggak ada alarm, nggak ada log merah — sistemnya ngerasa baik-baik aja. Pernah ada calon customer yang tiba-tiba diem? Kadang bukan mereka yang ninggalin kamu, kadang pesannya yang nggak pernah nyampe. | "sistem: **aman** ✓" / "kadang pesannya yang **nggak nyampe**" |
| 0:12–0:20 | Ilustrasi whiteboard: dua tangan nulis bersamaan, satu tulisan ketimpa | Akar masalahnya: pas pesan masuk beruntun, dua proses nyatet ke tempat yang sama — bersamaan. Kayak dua orang nulis di whiteboard yang sama, salah satu tulisannya ketimpa. | "2 proses, **1 whiteboard**" / "tulisan **ketimpa**" |
| 0:20–0:30 | Screen-record n8n mock: alur buffer sederhana | Yang bikin aku nggak bisa tidur bukan bug-nya — tapi mikirin udah berapa lama ini kejadian tanpa aku sadar, sementara aku pede sistemnya baik-baik aja. Fixnya: semua pesan antri dulu, nggak ada yang nimpa. Udah live. Follow — Sabtu, kenapa aku sengaja bikin bot lambat. | "takut sistem **kelihatan aman**, padahal enggak" / "fix: **antri dulu** · follow → eps. 6" |

**Caption IG**

> Eps. 5 🌙
> Bug paling serem itu bukan yang bikin sistem mati — tapi yang diem-diem. Pesan user hilang, sistem ngerasa baik-baik aja, dan yang nanggung malunya: bisnis klien-ku.
> Yang bikin aku nggak bisa tidur bukan bug-nya sendiri — tapi mikirin udah berapa lama itu kejadian tanpa aku sadar, sementara aku pede semuanya aman-aman aja.
> Akarnya klasik: dua proses nulis ke tempat yang sama bersamaan. Fixnya sederhana di konsep, tapi nyarinya yang lama.
> Follow — Sabtu aku cerita keputusan desain yang paling sering disalahpahami orang.
> #otomasibisnis #aiautomation #debugging #racecondition

**Persiapan aset**
- Talking head
- Ilustrasi bubble chat dummy (animasi teks) + ilustrasi whiteboard
- Screen-record n8n mock alur buffer yang disederhanakan

**Checklist privasi sebelum post**
- JANGAN sebut nama user yang dulu kena bug ini atau tunjukkan chat aslinya — pakai ilustrasi dummy sepenuhnya
- Fix debounce 60 dtk + buffer append-only sudah live di V4 (per export 14 Jul) — verifikasi di n8n sebelum rekam
- "Pesan yang hilang: nol" = klaim sejak fix live; kalau ragu, ganti "sejauh ini nggak kejadian lagi"
- Layar n8n = mock, tanpa credentials/nama workflow production
- Beat raw (takut sistem "kelihatan aman" padahal enggak) itu personal soal kecemasan megang sistem orang — aman untuk publik, tapi tetap keputusan Steven

---

### Reel — Sengaja Kubikin "Lambat" 60 Detik (eps. 6) 🎯
- **Pilar A (jualan)** / Durasi target **30–60 dtk** / Jadwal: **Sabtu 8 Agu, malam**

**Analisis 3 Why**
- Kategori LIFE: **F** (pengalaman/perasaan pribadi) + **E** (filosofi kerja)
- Safe: Bot sengaja nunggu biar nggak motong omongan user.
- Real: Bikin klien ngerasa didengerin, bukan diburu-buru sistem otomatis.
- Raw: Aku sendiri paling nggak suka ngerasa "diproses" bukan "didengerin" — kerja di sistem besar yang serba SOP dan cepat kadang bikin orang ngerasa cuma nomor antrian. Detail 60 detik ini caraku nolak bikin sistem yang bikin orang lain ngerasa kayak yang kadang aku rasain sendiri: diproses, bukan didengerin. ← dipakai jadi inti VO sebelum CTA

**Script**

| Waktu | Visual | VO (persis diucapkan) | On-screen text |
|---|---|---|---|
| 0:00–0:04 | Talking head | Bot-ku sengaja kubikin nunggu enam puluh detik sebelum jawab. Klien-ku sempet nanya: "ini lemot ya?" Nggak — ini justru fiturnya. | "Eps. 6" / "**sengaja** nunggu 60 detik" |
| 0:04–0:14 | Ilustrasi: orang ngetik pesan dicicil ("halo kak" / "mau tanya" / "kursusnya ada apa aja?") | Coba inget cara kamu sendiri chat: jarang satu pesan lengkap, kan? Dicicil. Kalau bot langsung nyaut di pesan pertama, dia jawab sebelum orangnya selesai ngomong — hasilnya jawaban nyasar. | "orang ngetik = **dicicil**" / "bot buru-buru = **jawaban nyasar**" |
| 0:14–0:26 | Screen-record demo A Course: user kirim 3 pesan beruntun, bot diam, lalu balas SATU jawaban utuh yang nyambung semua | Jadi bot-ku nunggu. Ngumpulin semua cicilan pesannya dulu, baru mikir, baru bales — satu jawaban yang nyambungin semuanya. Ditambah jeda ngetik beberapa detik biar kerasa manusiawi. | "tunggu → **gabung** → jawab **sekali, utuh**" |
| 0:26–0:44 | Talking head, nada lebih personal, jeda sebelum ngomong | Aku sendiri paling nggak suka ngerasa 'diproses', bukan 'didengerin' — kerjaanku sendiri kadang di sistem yang serba cepat, dan itu bisa bikin orang berasa cuma nomor antrian. Detail-detail kayak gini caraku nolak bikin sistem yang begitu ke orang lain. | "diproses ≠ **didengerin**" |
| 0:44–0:56 | Talking head, CTA | Kalau kamu pengen chat bisnismu diladenin kayak gini — komen **OTOMASI** atau DM aku. Ngobrol dulu, gratis. | "komen **OTOMASI**" / "DM @povstevens" |

**Caption IG**

> Eps. 6 🌙
> "Kok bot-nya nggak langsung bales?" — karena manusia juga nggak.
> Orang ngetik itu dicicil. Bot yang buru-buru jawab di pesan pertama bakal jawab hal yang salah. Jadi bot-ku nunggu, ngumpulin dulu, baru jawab sekali — utuh.
> Aku sendiri paling nggak suka ngerasa "diproses", bukan "didengerin" — kerjaanku sendiri kadang di sistem serba cepat yang bikin orang berasa nomor antrian. Detail kayak gini caraku nolak bikin sistem yang begitu ke orang lain.
> Pengen sistem yang mikirin detail kayak gini buat bisnismu? Komen "OTOMASI" atau DM aku.
> Follow — episode berikutnya.
> #otomasibisnis #aiautomation #customerexperience #whatsappbusiness

**Persiapan aset**
- Screen-record demo "A Course": skenario 3 pesan dicicil → 1 jawaban utuh (latih dulu skenarionya biar sekali take)
- Talking head buka/tengah/tutup + beat personal (0:26–0:44, nada lebih pelan)
- Ilustrasi teks pesan dicicil

**Checklist privasi sebelum post**
- Demo HANYA "A Course" + data dummy
- Jangan klaim angka respon absolut ("selalu 5 detik") — jeda natural disebut "beberapa detik" saja
- Percakapan klien soal "ini lemot ya?" diceritakan tanpa nama dan tanpa screenshot chat asli dengan klien
- Layar HP demo: crop status bar kalau ada notifikasi masuk
- Beat raw ("diproses vs didengerin") harus tetap generik — jangan sebut nama sistem/divisi BCA spesifik, cukup "sistem besar yang serba cepat"
