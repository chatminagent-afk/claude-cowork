# Revisi Final (eps. 1–12)

*Disusun 2026-07-22, revisi total dari batch v1 (14 Jul) berdasarkan review Steven per episode. File lama (`2026-07-14-reels-minggu-1..4.md`) tidak ditimpa — ini versi baru yang jadi acuan produksi.*

## Perubahan global vs v1

- **Durasi:** semua episode ~60 detik (sebelumnya 15–30 dtk untuk pilar B/C/D).
- **Nama sistem:** eps. 1 masih boleh sebut "chatbot" (istilah awam), eps. 2 dan seterusnya selalu **"VIRA"** / **"VIRA AI"** — bukan "bot" generik lagi.
- **Positioning baru:** VIRA bukan chatbot ketik-angka-pilih-menu — VIRA dibikin bisa "ngobrol", ngerti goal owner dan kebutuhan client, dan **dibikin custom per owner** (ditegaskan di eps. 2 & 3).
- **Bahasa:** dijaga awam — hindari istilah teknis (race condition, debounce, filter, HITL) diganti analogi/kalimat sehari-hari.
- **CTA tiap episode** (bukan cuma pilar A lagi): "follow, next aku tunjukin/ceritain [teaser konkret]" + "kalau mau dibikinin sistem khusus buat bisnis kamu, komen atau DM aja". Episode jualan (3, 6, 12) boleh lebih tegas ("komen OTOMASI").
- **Tidak pernah sebut hari** ("Rabu", "Sabtu") di CTA — cukup "next episode".
- Angka diupdate: eps. 3 pakai **1100+ chat bulan pertama**, eps. 12 pakai **1000+ chat** (tanpa detail FAQ/username).
- Eps. 9: fitur yang dihapus tetap sama (auto-deteksi ortu/calon murid), tapi alasannya diperkaya — bukan cuma "kesan kurang profesional", tapi juga **boros token** dan bikin **percakapan mandek karena nanya ulang 2x** buat intro.
- Eps. 8: topik baru (request kamu) — VIRA yang tau kapan harus nanya balik ke owner dulu sebelum jawab, bukan asal jawab.

---

## Minggu 1 (eps. 1–3) — Kenalan

### Eps. 1 — Siang QA Bank, Malam Bangun Chatbot
- Pilar D · Durasi ~60 dtk

**Script**
- **Hook:** "Jam 9 pagi aku ngetes aplikasi bank. Jam 11 malem, aku bangun chatbot sendiri." *(on-screen: "Eps. 1" / "**QA bank** by day")*
- **Body:** "Awalnya simpel — leads dari iklan kelas onlineku sendiri kebanjiran, aku nggak sanggup bales satu-satu. Terus aku sadar satu hal: banyak calon murid itu sebenarnya bukan nggak tertarik. Mereka cuma lupa bales, atau lagi mikir-mikir dulu. Dan kalau nggak di-follow up, deal itu ilang gitu aja — bukan karena gagal, tapi karena nggak pernah ditindaklanjuti. Jujur, yang bikin aku tetep lanjut sampe subuh bukan cuma soal itu. Ketakutanku: udah lima tahun aku jalan, tapi aku ngerasa masih di sini-sini aja. Aku pengen bikin sesuatu yang impactful — buat orang lain, bukan cuma buat aku sendiri." *(on-screen: "deal ilang ≠ gagal — tapi **nggak di-follow up**" / "5 tahun jalan, masih **di sini-sini aja**")*
- **CTA:** "Jadi aku bangun chatbot ini. Follow — next aku ceritain kenapa justru karena aku bukan programmer, sistemnya malah lebih teliti. Kalau kamu juga ngerasa banyak calon klien ngilang gitu aja, komen atau DM aku aja." *(on-screen: "follow → next: **kenapa bukan programmer**")*

**Caption IG**
> Eps. 1 🌙
> Siang: QA di bank. Malam: bangun chatbot sendiri buat bisnis kelas onlineku.
> Awalnya cuma karena leads kebanjiran, aku nggak sanggup bales satu-satu. Terus aku sadar — banyak deal itu bukan gagal, tapi nggak pernah di-follow up.
> Ketakutan sebenarnya bukan soal duit. Udah 5 tahun jalan, aku masih ngerasa di sini-sini aja — aku pengen bikin sesuatu yang impactful buat orang lain.
> Follow — next aku ceritain kenapa justru karena aku bukan programmer, sistemnya jadi lebih teliti.
> #otomasibisnis #aiautomation #buildinpublic #umkmindonesia

**Checklist privasi**
- Layar/n8n yang kerekam wajib mock, bukan production
- Cukup sebut "QA di bank" — jangan nama divisi/proyek BCA spesifik

**Target produksi**
- Take video: Sabtu, 25 Jul
- Edit video: Minggu malam, 26 Jul
- Upload: Senin malam, 27 Jul

---

### Eps. 2 — Aku Bukan Programmer
- Pilar D/B · Durasi ~60 dtk

**Script**
- **Hook:** "Aku bukan programmer. Tapi VIRA AI ini udah bales ratusan chat buat bisnis orang." *(on-screen: "Eps. 2" / "**bukan programmer**")*
- **Body:** "Rahasianya nggak keren-keren amat — AI yang bantu aku nulis, aku yang ngerangkai jadi sistem pakai n8n. Tapi jujur, yang bikin aku khawatir bukan soal itu. Aku khawatir: bisa nggak ya, aku yang kerjaan sehari-harinya QA, develop sistem yang beneran berguna — bukan cuma buat aku, tapi buat orang yang makai. Makanya VIRA nggak aku desain sebagai chatbot yang nyuruh ketik angka 1-2-3 pilih menu. VIRA aku bikin bisa 'ngobrol' — ngerti maunya owner apa, ngerti kebutuhan calon client-nya juga. Dan tiap bisnis beda kebutuhan, jadi VIRA-nya juga aku bikin custom, bukan satu template buat semua." *(on-screen: "khawatir: bisa **berguna** nggak ya?" / "VIRA ≠ chatbot ketik angka" / "**custom** per bisnis")*
- **CTA:** "Follow — next aku tunjukin VIRA kerja pas aku lagi tidur jam 2 pagi. Kalau kamu penasaran gimana VIRA bisa custom buat bisnismu, komen atau DM aja." *(on-screen: "follow → next: **kerja jam 2 pagi**")*

**Caption IG**
> Eps. 2 🌙
> Aku bukan programmer. AI yang bantu nulis, aku yang merangkai pakai n8n.
> Yang bikin aku khawatir bukan soal ngodingnya — tapi bisa nggak ya, aku yang QA, develop sistem yang beneran berguna buat orang yang makai.
> VIRA bukan chatbot ketik-angka-pilih-menu. VIRA dibikin bisa ngerti maunya owner dan kebutuhan client-nya — dan dibikin custom, bukan satu template buat semua bisnis.
> Follow — next VIRA kerja pas aku lagi tidur jam 2 pagi.
> #otomasibisnis #aiautomation #vibecoding #belajarai

**Checklist privasi**
- Kode yang tampil di layar = contoh generik, bukan potongan workflow klien
- Angka "ratusan chat" = grounded ke data agregat, jangan dinaikkan sendiri

**Target produksi**
- Take video: Sabtu, 25 Jul
- Edit video: Selasa malam, 28 Jul
- Upload: Rabu malam, 29 Jul

---

### Eps. 3 — VIRA yang Bales Chat Pas Aku Tidur 🎯
- Pilar A (jualan) · Durasi ~60 dtk

**Script**
- **Hook:** "Semalem ada yang chat ke VIRA jam 2 pagi. Aku tidur. Klienku juga tidur. Tapi chat-nya kebales." *(on-screen: "Eps. 3" / "chat **jam 2 pagi**, kebales")*
- **Body:** "Ini demonya — VIRA nggak langsung nyaut kayak mesin, ada jeda, ngetiknya kayak orang beneran. Dia jawab soal program, urus booking, catet data, tanpa siapa pun pegang HP. Dan ini yang penting: VIRA-nya dibikin custom, ngikutin kebutuhan klien — mau goal-nya sampe closing, sampe booking, atau baru sekadar kasih info, itu diatur sesuai bisnisnya. Kalau calon customer-nya belum sampe goal itu, VIRA follow-up lagi — pelan-pelan, biar KPI-nya kecapai, bukan cuma sekali kirim terus diem. Di bulan pertama aja, VIRA udah bales lebih dari seribu seratus chat dari user — tanpa aku atau ownernya perlu begadang." *(on-screen: "custom sesuai **goal klien**" / "belum goal → **follow-up otomatis**" / "**1100+ chat** bulan pertama")*
- **CTA:** "Kalau bisnismu lagi tumbuh dan chat mulai keteteran — komen **OTOMASI**, atau DM aku. Nggak harus langsung pasang, ngobrol dulu aja." *(on-screen: "komen **OTOMASI**" / "DM @povstevens")*

**Caption IG**
> Eps. 3 🌙
> Chat masuk jam 2 pagi, kebales. Bukan karena ada yang begadang — tapi karena VIRA yang jaga.
> VIRA dibikin custom sesuai goal tiap klien — kalau calon customer-nya belum sampe goal itu, VIRA follow-up lagi biar KPI-nya kecapai.
> Di bulan pertama aja, VIRA udah bales lebih dari 1100 chat dari user — tanpa aku atau ownernya begadang.
> Bisnismu lagi tumbuh tapi chat mulai keteteran? Komen "OTOMASI" atau DM aku — ngobrol dulu aja, santai.
> #otomasibisnis #aiautomation #whatsappbusiness #ukmnaikkelas

**Checklist privasi**
- Semua screen-record dari bot demo "A Course" + data dummy — bukan environment production
- Angka 1100+ = agregat bulan pertama, jangan diklaim sebagai angka "sekarang"

**Target produksi**
- Take video: Sabtu, 25 Jul
- Edit video: Kamis–Jumat malam, 30–31 Jul
- Upload: Sabtu malam, 1 Agu

---

## Minggu 2 (eps. 4–6) — Bug Wars

### Eps. 4 — VIRA Sempet "Amnesia" Tiap Ganti Jam
- Pilar B · Durasi ~60 dtk

**Script**
- **Hook:** "VIRA sempet ngalamin 'amnesia'. Tiap ganti jam, dia lupa semua obrolan." *(on-screen: "Eps. 4" / "**amnesia** tiap jam")*
- **Body:** "Jadi user udah ngobrol panjang, udah dikasih rekomendasi. Eh, dua jam kemudian dia balik nanya — VIRA nyapa dari nol, kayak nggak kenal. Coba bayangin jadi customer-nya: cerita panjang, disuruh ngulang dari nol — kamu balik lagi, nggak? Ternyata ingatannya VIRA emang di-reset tiap jam berganti. Makanya kita enhance — sekarang VIRA punya semacam 'memori sementara', yang direset teratur sekali sehari, bukan tiap jam. Jadi obrolan sepanjang hari tetep nyambung, nggak keputus-putus lagi." *(on-screen: "jam 8: **ngobrol panjang**" / "jam 10: '**halo, ada yang bisa dibantu?**'" / "fix: memori **direset 1x sehari**")*
- **CTA:** "Follow — next aku cerita masalah lain yang sempet bikin pesan user ilang. Kalau kamu penasaran sistem kayak gini cocok buat bisnismu, komen atau DM aja." *(on-screen: "follow → next: **pesan yang sempet ilang**")*

**Caption IG**
> Eps. 4 🌙
> VIRA pernah "amnesia" tiap ganti jam — user yang udah ngobrol panjang tiba-tiba disapa dari nol lagi.
> Ternyata ingatannya kedesain reset tiap jam. Kita enhance jadi memori sementara yang direset 1x sehari — obrolannya jadi tetep nyambung.
> Follow — next masalah lain yang sempet bikin pesan user ilang.
> #otomasibisnis #aiautomation #debugging #buildinpublic

**Checklist privasi**
- Ilustrasi chat = buatan sendiri/dummy, bukan chat user asli
- Layar n8n = mock, jangan sampai node credentials kerekam

**Target produksi**
- Take video: Sabtu–Minggu, 1–2 Agu
- Edit video: Minggu malam, 2 Agu
- Upload: Senin malam, 3 Agu

---

### Eps. 5 — Bukan Bug-nya yang Bikin Aku Nggak Bisa Tidur
- Pilar B · Durasi ~60 dtk

**Script**
- **Hook:** "Yang bikin aku nggak bisa tidur bukan bug-nya — tapi mikirin udah berapa lama ini kejadian tanpa aku sadar, sementara aku pede-pede aja sistemnya baik-baik aja." *(on-screen: "Eps. 5" / "bukan bug-nya yang bikin **gak bisa tidur**")*
- **Body:** "Ceritanya: user ngetik beberapa pesan beruntun, tapi VIRA cuma nangkep sebagian. Aku sempet coba beberapa chatbot AI lain di bisnis lain buat bandingin — ternyata ini masalah umum. Ada yang balesnya patah-patah, satu-satu tiap bubble pesan yang masuk. Ada juga yang cuma nanggepin pesan pertama doang, sisanya diabaikan. Dua-duanya bikin jawabannya nyasar. Solusinya: VIRA sekarang nunggu dulu. Pesan-pesannya ditampung, kayak nungguin orang selesai ngetik — begitu orangnya udah berhenti kirim bubble baru, VIRA baru proses semuanya jadi satu jawaban yang nyambung." *(on-screen: "bot lain: **patah-patah** / cuma baca pesan pertama" / "VIRA: **nunggu dulu**, baru jawab")*
- **CTA:** "Berapa lama VIRA nunggu itu ternyata ada angkanya, dan itu keputusan sengaja — follow, next aku ceritain kenapa aku bikin dia 'lambat'. Kalau bisnismu juga pernah kena masalah kayak gini, komen atau DM aja." *(on-screen: "follow → next: kenapa sengaja **'lambat'**")*

**Caption IG**
> Eps. 5 🌙
> Yang bikin aku nggak bisa tidur bukan bug-nya — tapi mikirin udah berapa lama ini kejadian tanpa aku sadar, sementara aku pede semuanya aman-aman aja.
> Ternyata ini masalah umum di chatbot AI lain juga: ada yang jawabnya patah-patah per bubble pesan, ada yang cuma baca pesan pertama. Solusinya, VIRA sekarang nunggu dulu sampai orangnya selesai ngetik, baru jawab sekali — utuh.
> Follow — next aku ceritain kenapa aku sengaja bikin VIRA "lambat".
> #otomasibisnis #aiautomation #debugging #buildinpublic

**Checklist privasi**
- Jangan sebut nama bisnis/chatbot lain yang dibandingkan — cukup "beberapa chatbot AI lain"
- Ilustrasi bubble chat = dummy sepenuhnya, bukan chat user asli

**Target produksi**
- Take video: Sabtu–Minggu, 1–2 Agu
- Edit video: Selasa malam, 4 Agu
- Upload: Rabu malam, 5 Agu

---

### Eps. 6 — Sengaja Kubikin VIRA "Lambat" 60 Detik 🎯
- Pilar A (jualan) · Durasi ~60 dtk

**Script**
- **Hook:** "VIRA sengaja kubikin nunggu 60 detik sebelum jawab. Ada yang nanya: 'ini lemot ya?' Bukan — ini justru fiturnya." *(on-screen: "Eps. 6" / "**sengaja** nunggu 60 detik")*
- **Body:** "Coba inget cara kamu sendiri chat — jarang satu pesan lengkap, kan? Dicicil. Kalau VIRA langsung nyaut di pesan pertama, dia jawab sebelum orangnya selesai ngomong, hasilnya nyasar. Jadi VIRA nunggu, ngumpulin semua cicilan pesannya dulu, baru bales — satu jawaban yang nyambungin semuanya, plus jeda ngetik biar berasa manusiawi. Ada alasan lain juga: ini jaga-jaga biar nomor WhatsApp bisnisnya nggak rawan dianggap spam dan kena banned — soalnya balas kebanyakan atau secepat kilat itu salah satu yang bikin WhatsApp curiga." *(on-screen: "orang ngetik = **dicicil**" / "tunggu → gabung → jawab **sekali, utuh**" / "jaga nomor WA biar **gak rawan banned**")*
- **CTA:** "Kalau kamu penasaran gimana rasanya chat bisnismu diladenin kayak gini — komen atau DM aku aja, santai, ngobrol dulu." *(on-screen: "komen / DM **@povstevens**")*

**Caption IG**
> Eps. 6 🌙
> "Kok VIRA nggak langsung bales?" — karena manusia juga nggak.
> Orang ngetik itu dicicil. VIRA nunggu, ngumpulin dulu, baru jawab sekali — utuh. Bonusnya, ini juga jaga nomor WhatsApp bisnisnya biar nggak rawan dianggap spam.
> Penasaran gimana rasanya chat bisnismu diladenin kayak gini? Komen atau DM aku aja, ngobrol dulu, santai.
> #otomasibisnis #aiautomation #customerexperience #whatsappbusiness

**Checklist privasi**
- Demo hanya bot demo "A Course" + data dummy
- Jangan klaim angka respon absolut ("selalu 5 detik") — cukup "beberapa detik"

**Target produksi**
- Take video: Sabtu–Minggu, 1–2 Agu
- Edit video: Kamis–Jumat malam, 6–7 Agu
- Upload: Sabtu malam, 8 Agu

---

## Minggu 3 (eps. 7–9) — Realita Klien

### Eps. 7 — VIRA Versi Awal, Sejujurnya
- Pilar C · Durasi ~60 dtk

**Script**
- **Hook:** "Waktu VIRA pertama kali dipakai klien, aku PD banget bilang dia udah siap." *(on-screen: "Eps. 7" / "PD banget: '**udah siap**'")*
- **Body:** "Jujur, itu bukan karena aku mau overpromise — tapi waktu itu scope pengetesanku masih kecil banget, jadi aku pede VIRA udah oke. Begitu dipakai user beneran — dengan cara ngetik yang macem-macem — muncul kasus-kasus yang nggak pernah kebayang sebelumnya. Dari situ aku janji ke diri sendiri: aku bakal terus improve VIRA, sampai dia beneran bisa bantu orang yang butuh — bukan cuma keliatan bisa pas demo doang." *(on-screen: "scope tes kecil → **PD terlalu cepat**" / "janji: **terus improve VIRA**")*
- **CTA:** "Follow — next aku tunjukin sisi VIRA yang jarang aku omongin: dia tau kapan harus nanya balik ke aku dulu, bukan asal jawab. Kalau kamu penasaran gimana ini bisa diterapin ke bisnismu, komen atau DM aja." *(on-screen: "follow → next: **VIRA nanya balik dulu**")*

**Caption IG**
> Eps. 7 🌙
> Waktu VIRA pertama dipakai klien, aku PD banget bilang dia udah siap.
> Jujur, itu bukan overpromise — scope pengetesanku waktu itu emang masih kecil. Begitu ketemu user beneran, muncul kasus yang nggak pernah kebayang.
> Dari situ aku janji: terus improve VIRA, sampai dia beneran bisa bantu orang yang butuh — bukan cuma keliatan bisa di demo.
> Follow — next sisi VIRA yang jarang aku omongin.
> #otomasibisnis #aiautomation #umkmindonesia #realitastartup

**Checklist privasi**
- Jangan tampilkan dokumen onboarding asli — semua visual dibuat ulang generik
- Jangan sebut budget/fee klien

**Target produksi**
- Take video: Sabtu–Minggu, 8–9 Agu
- Edit video: Minggu malam, 9 Agu
- Upload: Senin malam, 10 Agu

---

### Eps. 8 — VIRA Tau Kapan Harus Nanya Balik
- Pilar B · Durasi ~60 dtk

**Script**
- **Hook:** "VIRA nggak selalu langsung jawab. Kadang dia mikir dulu — terus nanya ke aku." *(on-screen: "Eps. 8" / "kadang VIRA **nanya balik dulu**")*
- **Body:** "Jadi ada momen-momen tertentu di mana asal jawab itu berisiko — misalnya pertanyaan yang di luar kebiasaan, atau yang jawabannya bisa berpengaruh besar ke keputusan calon customer. Nah, di momen kayak gitu, VIRA nggak asal jawab. Dia notify dulu ke aku atau ke ownernya, minta konfirmasi, baru dia lanjut bales ke customernya. Ini bagian dari filosofi VIRA yang custom per bisnis — bukan cuma soal jawab cepat, tapi soal jawab yang bener dan aman buat reputasi bisnisnya." *(on-screen: "situasi berisiko → **VIRA notify owner dulu**" / "custom = jawab **bener**, bukan cuma cepet")*
- **CTA:** "Follow — next aku cerita fitur paling pinter di VIRA... yang akhirnya kuhapus sendiri. Kalau kamu mau sistem yang tau kapan harus hati-hati kayak gini, komen atau DM aja." *(on-screen: "follow → next: fitur **kuhapus sendiri**")*

**Caption IG**
> Eps. 8 🌙
> VIRA nggak selalu langsung jawab. Ada momen dia mikir dulu, terus nanya balik ke aku.
> Kalau situasinya berisiko — jawabannya bisa berpengaruh besar ke keputusan customer — VIRA notify owner dulu sebelum lanjut jawab. Bukan soal jawab cepat, tapi soal jawab yang bener.
> Follow — next fitur paling pinter di VIRA yang akhirnya kuhapus sendiri.
> #otomasibisnis #aiautomation #buildinpublic

**Checklist privasi**
- Contoh "situasi berisiko" pakai skenario generik/dummy, bukan kasus asli klien
- Jangan sebut detail rule/prompt asli yang menentukan kapan VIRA escalate

**Target produksi**
- Take video: Sabtu–Minggu, 8–9 Agu
- Edit video: Selasa malam, 11 Agu
- Upload: Rabu malam, 12 Agu

---

### Eps. 9 — Fitur Andalan yang Kuhapus Sendiri
- Pilar B/D · Durasi ~60 dtk

**Script**
- **Hook:** "Fitur paling pinter di VIRA... akhirnya kuhapus. Dan itu keputusan yang bener." *(on-screen: "Eps. 9" / "fitur andalan → **dihapus**")*
- **Body:** "Fiturnya: VIRA nebak siapa yang lagi chat — orang tua atau calon murid — terus nyesuaiin gaya bahasanya. Kedengeran pinter kan? Di demo, keren banget. Tapi di dunia nyata, ada tiga masalah. Satu, tebakannya kadang meleset — orang tua disapa kayak anak muda, kesan profesionalnya rusak. Dua, fitur ini bikin boros — tiap chat butuh proses tambahan buat nebak dulu. Tiga, yang paling nyebelin: kadang bikin percakapan mandek, karena VIRA nanya ulang buat intro sampai dua kali. Akhirnya dihapus, diganti bahasa netral — dan sistemnya justru makin dipercaya." *(on-screen: "tebakan **meleset**" / "boros proses" / "nanya intro **2x** → obrolan mandek" / "dihapus → bahasa **netral**")*
- **CTA:** "Follow — next aku cerita kenapa ganti AI model yang lebih murah justru bongkar lima bug sekaligus. Kalau kamu mau sistem yang simpel tapi konsisten kayak gini, komen atau DM aja." *(on-screen: "follow → next: **AI murah bongkar bug**")*

**Caption IG**
> Eps. 9 🌙
> "Kill your darling" — kupikir istilah itu cuma buat penulis. Ternyata kena juga ke aku.
> Fitur deteksi otomatis siapa-yang-chat itu keren pas demo. Tapi di dunia nyata: tebakannya kadang meleset, bikin boros proses, dan kadang bikin obrolan mandek karena nanya ulang intro sampai 2x.
> Dihapus, diganti bahasa netral — dan sistemnya justru makin dipercaya.
> Follow — next kenapa AI model yang lebih murah justru bongkar 5 bug sekaligus.
> #otomasibisnis #aiautomation #productdesign #buildinpublic

**Checklist privasi**
- Keputusan hapus fitur ini aman diceritakan — jangan sebut nama klien, cukup "diputusin bareng klien"
- Contoh salah sapa pakai ilustrasi buatan, bukan screenshot chat asli

**Target produksi**
- Take video: Sabtu–Minggu, 8–9 Agu
- Edit video: Kamis–Jumat malam, 13–14 Agu
- Upload: Sabtu malam, 15 Agu

---

## Minggu 4 (eps. 10–12) — Pelajaran & Hasil

### Eps. 10 — AI Model Murah Justru Bongkar Bug
- Pilar C · Durasi ~60 dtk

**Script**
- **Hook:** "Aku pernah ganti AI model VIRA ke yang lebih murah. Minggu itu juga: lima bug muncul barengan." *(on-screen: "Eps. 10" / "ganti **AI model murah** → 5 bug")*
- **Body:** "Ternyata bedanya AI model murah sama yang mahal itu bukan cuma soal harga doang. Kalau pakai yang murah, aku harus banyak kompromi — batasin instruksinya ketat banget biar dia tetep patuh sama system prompt, dan aku harus siapin banyak pengaman ekstra biar dia nggak ngarang jawaban sendiri. Kalau pakai AI model yang lebih mahal, dia jauh lebih patuh sama instruksi yang aku kasih — aku nggak perlu sebanyak itu pengaman tambahan. Jadi ini bukan soal mana yang lebih bagus — tinggal owner mau pilih yang mana, sesuai budget dan risiko yang mau ditanggung." *(on-screen: "AI murah = **banyak kompromi & pengaman**" / "AI mahal = **lebih patuh**, pengaman lebih sedikit" / "tinggal **pilih sesuai kebutuhan**")*
- **CTA:** "Kalau kamu penasaran AI model apa yang cocok buat bisnismu, komen atau DM aku aja. Follow — next aku cerita tiga kali aku yakin nemu penyebab bug, tiga kali salah." *(on-screen: "follow → next: **yakin 3x, salah 3x**")*

**Caption IG**
> Eps. 10 🌙
> Aku pernah ganti AI model VIRA ke yang lebih murah. Minggu itu juga, 5 bug muncul barengan.
> Bedanya bukan cuma harga: AI murah butuh banyak kompromi & pengaman ekstra biar tetep patuh dan nggak ngarang jawaban. AI yang lebih mahal jauh lebih patuh, pengamannya nggak sebanyak itu.
> Bukan soal mana yang lebih bagus — tinggal pilih sesuai kebutuhan dan budget bisnismu.
> Follow — next tiga kali aku yakin nemu penyebab bug, tiga kali salah.
> #otomasibisnis #aiautomation #umkmindonesia #belajarai

**Checklist privasi**
- Jangan sebut nama model/vendor AI spesifik dan angka biaya eksak
- Ilustrasi biaya/bug buatan sendiri, bukan dokumen root-cause asli

**Target produksi**
- Take video: Sabtu–Minggu, 15–16 Agu
- Edit video: Minggu malam, 16 Agu
- Upload: Senin malam, 17 Agu

---

### Eps. 11 — Yakin Bukan Bukti
- Pilar B · Durasi ~60 dtk

**Script**
- **Hook:** "Tiga kali aku yakin banget udah nemu penyebab bug VIRA. Tiga kali salah." *(on-screen: "Eps. 11" / "yakin 3x, **salah 3x**")*
- **Body:** "Awalnya aku pengen cepet — jadi aku nebak-nebak penyebabnya biar cepet kelar. Ternyata itu salah besar. Karena yang dipertaruhkan bukan cuma waktuku, tapi kepercayaan klien ke VIRA. Kalau aku asal nebak dan ternyata salah berkali-kali, kredibilitasnya yang taruhan. Sejak itu aku ganti caranya: nggak boleh lagi menebak-nebak. Begitu ada bug, aku harus langsung cari tau akar masalahnya beneran dulu, baru fix. Karena trust itu yang paling penting dijaga — bukan cuma soal kecepatan benerin." *(on-screen: "nebak-nebak → **kredibilitas taruhan**" / "sekarang: cari **akar masalah dulu**, baru fix")*
- **CTA:** "Follow — next episode penutup season ini: rekap dari satu video sampai VIRA versi 4. Kalau kamu mau sistem yang bener-bener dijagain kayak gini, komen atau DM aja." *(on-screen: "follow → next: **season finale**")*

**Caption IG**
> Eps. 11 🌙
> Tiga kali aku yakin udah ketemu penyebab bug-nya. Tiga kali salah.
> Awalnya aku nebak-nebak biar cepet — ternyata itu salah besar, karena yang dipertaruhkan bukan cuma waktu, tapi kepercayaan klien ke VIRA.
> Sekarang: nggak boleh lagi menebak-nebak. Cari akar masalah dulu, baru fix — karena trust itu yang paling penting dijaga.
> Follow — next episode penutup season ini.
> #otomasibisnis #aiautomation #debugging #qamindset

**Checklist privasi**
- Jangan tunjukkan link/form asli klien atau nama fitur internal spesifik
- Layar n8n = mock

**Target produksi**
- Take video: Sabtu–Minggu, 15–16 Agu
- Edit video: Selasa malam, 18 Agu
- Upload: Rabu malam, 19 Agu

---

### Eps. 12 — 1 Video → 1 Klien → VIRA Versi 4 (Season Finale) 🎯
- Pilar A (jualan) · Durasi ~60 dtk

**Script**
- **Hook:** "Season pertama series ini selesai. Video pertama itu kuposting tanpa ekspektasi — jujur, aku setengah berharap nggak ada yang notice, takut kelihatan 'belum ahli'." *(on-screen: "Eps. 12" / "takut kelihatan **'belum ahli'**")*
- **Body:** "Ternyata kejujuran itu yang bikin orang percaya. Satu bisnis DM aku — jadi klien pertamaku. Dari situ: begadang, salah tebak, hapus fitur sendiri, benerin pesan yang hilang, sampai sekarang VIRA versi 4. Sekarang VIRA udah handle lebih dari seribu chat, dan sistemnya udah di fase stabil. Tapi namanya sistem, tetep ada hal di luar kontrolku — kadang API WhatsApp atau API AI-nya sempet 'berkedip' sebentar. Tapi ini bukan alasan buat nggak pakai sistem AI — karena dibanding cost kecil itu, ownernya bisa fokus ke hal lain buat ngembangin bisnisnya, bukan sibuk bales chat sendiri. Sekarang aku lagi kembangin VIRA buat industri yang beda: developer properti." *(on-screen: "1 video → **1 klien** → VIRA **versi 4**" / "**1000+ chat**, fase **stabil**" / "next: VIRA buat **developer properti**")*
- **CTA:** "Kalau bisnismu lagi tumbuh dan kamu ngerasa jadi bottleneck-nya sendiri — bales chat sampai malem, follow-up kelewat — aku bisa bantu. Komen **OTOMASI** atau DM aku. Kita mulai dari ngobrol, bukan dari bayar." *(on-screen: "komen **OTOMASI**" / "DM @povstevens · WA 085155202354")*

**Caption IG**
> Eps. 12 🌙 SEASON FINALE
> Video pertama itu kuposting tanpa ekspektasi — takut kelihatan "belum ahli". Ternyata justru kejujuran itu yang bikin orang percaya.
> Satu video → satu klien → VIRA versi 4. Sekarang VIRA udah handle lebih dari 1000 chat, di fase stabil — meski tetap ada hal di luar kontrol (API WhatsApp/AI kadang "berkedip"). Tapi itu bukan alasan buat nggak pakai sistem AI — ownernya justru bisa fokus ke hal lain buat ngembangin bisnisnya.
> Sekarang aku lagi kembangin VIRA buat industri yang beda: developer properti.
> Kalau kamu owner yang masih jadi customer service dadakan buat bisnismu sendiri: komen "OTOMASI" atau DM aku. Mulai dari ngobrol dulu.
> Terima kasih udah nemenin season ini 🙏
> #otomasibisnis #aiautomation #whatsappbusiness #ukmnaikkelas

**Checklist privasi**
- Jangan sebut nama klien; "satu bisnis DM aku" cukup
- Angka "1000+ chat" = agregat, bukan angka per-user; jangan sebut FAQ count/username
- Teaser developer properti: pakai demo de-branded, jangan tunjukkan backend data klien asli

**Target produksi**
- Take video: Sabtu–Minggu, 15–16 Agu
- Edit video: Kamis–Jumat malam, 20–21 Agu
- Upload: Sabtu malam, 22 Agu
