# Hasil eval balasan VIRA — model asli (2026-09-23 11:21)

DeepSeek `deepseek-v4-pro` asli, temperature 0.7, lewat workflow eval sementara. Kode node asli dari file workflow; katalog dari sheet live (baca saja). Pesan prospek sama persis untuk semua versi.

## Ringkasan

| Metrik | v3.11 | v3.12 |
|---|---|---|
| balasan (tanpa perkenalan) | 22 | 66 |
| median kata | 26.0 | 13.0 |
| maks kata | 42 | 37 |
| median kata saat prospek tidak bertanya | 25.5 | 12.5 |
| membuka dengan merangkum (gema) | 7 | 0 |
| promosi VIRA tanpa ditanya | 5 | 0 |
| > 2 kalimat saat prospek tidak bertanya | 5 | 3 |
| > 1 pertanyaan dalam satu balasan | 0 | 0 |
| jumlah chat ditanya padahal sudah disebut | 0 | 1 |
| pertanyaan kembar dengan balasan sebelumnya | 1 | 4 |
| perkenalan: median kata | 54 | 37 |
| perkenalan: > 1 pertanyaan | 3 | 0 |
| dipangkas jaring RINGKAS | 0 | 9 |
| minta deck dibalas tawaran deck lagi | 0 | 0 |
| balasan 'Maaf, ada kendala' | 0 | 0 |
| STATS nama usaha benar | 4/4 | 12/12 |
| STATS nama usaha kotor | 0 | 0 |

## v3.11

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=Humanizer, industri=parfum, masalah_utama=kewalahan balas chat satu-satu, volume_chat=100an per hari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun sama Steven pakai sistem yang sama yang dia bikin untuk kliennya, namanya VIRA. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Mau coba ngobrol soal AI customer service ya? Boleh banget, cerita dulu aja kakak butuhnya seperti apa. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 55 | GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak, Humanizer jualan parfum ya. Ribet balasin orang satu-satu itu memang makan waktu, apalagi kalau chat-nya masuk terus. Kira-kira sehari ada berapa chat masuk kak? | 27 | GEMA; galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | 100 an chat | Wah 100an chat sehari itu lumayan padat buat dibales sendiri sambil ngurus pesanan. Dari chat pertama sampai orang beneran beli, biasanya lewat langkah apa aja kak? | 26 | galian: bidang usahanya, sekaligus minta dia cer |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Alurnya jelas ya: tanya-tanya, minta pricelist, terus pesen. Nah bagian tanya-tanya dan kirim pricelist itu yang bisa VIRA pegang otomatis, jadi kakak tinggal terima orderan yang udah siap. Biasanya mereka paling sering nanya apa aja kak? | 36 | GEMA; PROMOSI |
| 5 | aroma, ketahanan, sama ready stok ga | Tiga itu pertanyaan klasik parfum, dan jawabannya udah pasti ada di kepala kakak, tinggal diajarin ke VIRA sekali, dia yang jawabin berulang-ulang tanpa capek. Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 36 | PROMOSI |
| 6 | iya kadang ada yg kelewat | Nah itu yang bikin rugi pelan-pelan, karena tiap chat kelewat itu calon pembeli yang udah niat tanya tapi nggak kebales. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? | 30 |  |

### S2 Katering — ulang uji 17/09

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=-, volume_chat=20-30 chat per hari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI. Aku dibangun sama Steven pakai sistem yang sama yang dia bikin untuk kliennya, namanya VIRA, jadi kakak lagi ngobrol sama contohnya sekarang. Mau tanya soal chatbot yang mana kak? Kalau soal VIRA, boleh cerita dulu kebutuhannya seperti apa. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 54 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Nah itu justru celahnya, chat malam yang nggak kebalas biasanya keburu pindah ke katering lain. Boleh tau nama usahanya apa kak? | 24 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Siap kak, Dapur Nadia. Kalau boleh tau, dari chat yang numpuk itu yang paling bikin repot sekarang apa, yang nanya menu, harga, atau yang lain? | 25 | GEMA; galian: masalah terbesarnya soal chat sekarang |
| 4 | sekitar 20-30 chat sehari | Lumayan buat dibalas sendiri sambil ngurus masakan. Dari chat masuk sampai jadi pesanan, biasanya lewat langkah apa aja kak? | 19 | galian: masalah terbesarnya soal chat sekarang |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Itu alur yang bisa dipegang AI dari awal sampai pesanan masuk. Yang paling sering bikin mereka berhenti di tengah biasanya di bagian mana kak? | 24 | galian: masalah terbesarnya soal chat sekarang |
| 6 | ada yg sampe kelewat sih kak kadang | Nah itu yang paling mahal, chat yang kelewat itu pesanan yang pindah ke katering lain. Kalau lagi ramai gitu, yang paling bikin repot bagian mananya kak? | 26 | galian: masalah terbesarnya soal chat sekarang |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=-, masalah_utama=-, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI. Aku dibangun sama Steven pakai sistem yang sama yang dia bikin untuk kliennya, namanya VIRA, jadi kalau kakak penasaran hasilnya kayak apa, kakak lagi ngobrol sama contohnya sekarang. VIRA ini AI customer service WhatsApp yang balas chat pelanggan otomatis 24 jam, paham bahasa natural, bisa follow-up, jadwalin, sampai arahkan ke manusia kalau memang perlu. Cocok buat bisnis yang chat-nya ramai dan pertanyaannya berulang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 78 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Klinik gigi berarti chat-nya banyak yang nanya jadwal, harga perawatan, sama mau booking kan, itu semua bisa dipegang VIRA otomatis. Kira-kira sehari ada berapa chat masuk kak? | 30 | PROMOSI; galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | harganya berapa kak? | Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000, dan setup awalnya sekarang gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis kakak, jadi lebih pas kalau dibicarakan langsung sama Steven. Kalau boleh tau, dari chat masuk itu yang paling sering ditanyakan pelanggan apa aja kak? | 42 |  |
| 4 | bisa connect ke IG juga ga? | Bisa kak, chat dari Instagram bisa disambungkan ke sistem yang sama, jadi semua masuk ke satu tempat dan tetap kebalas otomatis. Kalau boleh tau, sekarang pelanggan lebih sering chat lewat WhatsApp atau Instagram? | 33 |  |
| 5 | oke, chat masuk sehari 50an | Lumayan ramai kak, 50 chat sehari itu berat kalau dibalas manual sambil ngurus pasien. VIRA bisa pegang yang tanya-tanya umum, kakak tinggal turun kalau ada yang butuh keputusan khusus. Dari chat sampai akhirnya booking, biasanya lewat langkah apa aja kak? | 40 | GEMA; PROMOSI; galian: bidang usahanya, sekaligus minta dia cer |

### S4 Bimbel — prospek bercerita panjang

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=Bimbel SD SMP, masalah_utama=-, volume_chat=40 chat per hari saat musim pendaftaran, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak! Aku Steven versi AI, dibangun sama Steven pakai sistem yang dia bikin untuk kliennya, namanya VIRA. Jadi kalau kakak penasaran hasilnya kayak apa, kakak lagi ngobrol sama contohnya sekarang. Ada yang bisa aku bantu soal VIRA atau otomasi chat untuk bisnis kakak? Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 54 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak! Bimbel Cerdas Mandiri itu bergerak di bidang apa persisnya, boleh cerita sedikit? | 15 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Nah itu yang bikin repot ya kak, nanya jadwal dan biaya itu kan berulang terus. Kalau lagi ngajar, chat dari orang tua suka numpuk nggak? | 25 | GEMA |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | 40 chat sehari itu lumayan banget buat dibalas sendiri sambil ngajar. Pas lagi numpuk gitu, biasanya ada yang kelewat atau telat dibales nggak kak? | 24 | GEMA; galian: masalah terbesarnya soal chat sekarang |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Jadi alurnya jelas ya kak: tanya biaya, tanya jadwal, lalu daftar lewat form. Yang tanya biaya dan jadwal itu sebenarnya bisa langsung dijawab otomatis, jadi kakak tinggal fokus ke yang sudah mau daftar. | 33 | GEMA; PROMOSI; galian: masalah terbesarnya soal chat sekarang |

### S5 Kopi — sampai minta deck

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=coffee shop, masalah_utama=chat reservasi numpuk saat weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, salam kenal. Aku Steven versi AI, dibangun sama Steven pakai sistem yang sama yang dia bikin untuk kliennya, namanya VIRA. Jadi kalau kakak penasaran hasilnya kayak apa, kakak lagi ngobrol sama contohnya sekarang. Boleh aku tau sedikit, chat di Kopi Senja biasanya soal apa aja kak? | 48 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Wah pas weekend memang paling ramai ya kak. Itu yang bikin repot biasanya bagian mananya, yang nunggu dibales lama atau ada yang sampai kelewat? | 24 | galian: bidang usahanya, sekaligus minta dia cer |
| 3 | 100an chat pas weekend | Itu lumayan berat kalau dibalas manual sambil ngurusin kedai. Dari chat masuk sampai akhirnya booking, biasanya lewat langkah apa aja kak? | 21 | galian: kira-kira berapa chat masuk per hari |
| 4 | boleh dong dibuatin deck | Boleh banget kak, sudah aku teruskan ke Steven. Dia sendiri yang bakal nyusun decknya dan nanti langsung hubungin kakak, sambil nunggu kakak bisa tanya apa aja ke aku. | 28 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Sambil nunggu Steven, boleh aku tau nggak, dari chat masuk sampai akhirnya booking, biasanya lewat langkah apa aja? | 20 |  |

## v3.12

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 1)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw, boleh tau nama kakak siapa dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 44 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Soal balas chat satu-satu itu, biasanya yang bikin paling repot bagian mananya? | 15 |  |
| 3 | 100 an chat | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Dari chat pertama sampai jadi pesanan, biasanya lewat langkah apa aja kak? | 12 |  |
| 5 | aroma, ketahanan, sama ready stok ga | Yang paling sering ditanyain dari tiga itu yang mana kak? | 10 |  |
| 6 | iya kadang ada yg kelewat | Noted kak. Dari chat pertama sampai jadi pesanan, biasanya lewat langkah apa aja? | 13 |  |

### S2 Katering — ulang uji 17/09 (ulang 1)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=-, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=sekitar 20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh juga sekalian kenalan, nama kakak siapa dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 45 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Kalau malam numpuk gitu, biasanya chat yang masuk paling banyak soal apa aja? | 16 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Oh iya, nama usahanya apa kak? | 6 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 4 | sekitar 20-30 chat sehari | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 11 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Kira-kira sehari ada berapa chat masuk kak? | 7 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 1)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=chat masuk sehari 50an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA itu AI customer service WhatsApp yang balas chat pelanggan 24 jam, jawab pertanyaan yang berulang, sampai bantu follow-up. Cocok buat bisnis yang chat-nya mulai ramai dan sering ditanyain hal yang sama. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 68 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat di kliniknya, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan, dan setup-nya lagi gratis kak. Angka finalnya tergantung kompleksitas alur bisnisnya, jadi lebih pas kalau dibicarakan langsung sama Steven. Kira-kira sehari ada berapa chat masuk ke kliniknya kak? | 37 |  |
| 4 | bisa connect ke IG juga ga? | Bisa kak, VIRA bisa pegang chat yang masuk dari Instagram juga. Jadi pertanyaan yang sama dari WhatsApp atau IG bisa kebalas otomatis. Kalau boleh tau, chat dari IG itu biasanya nanya apa aja kak? | 34 |  |
| 5 | oke, chat masuk sehari 50an | Dari chat pertama sampai jadi pasien, biasanya lewat langkah apa aja kak? | 12 | galian: masalah terbesarnya soal chat sekarang |

### S4 Bimbel — prospek bercerita panjang (ulang 1)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 49 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat di Bimbel Cerdas Mandiri, yang paling bikin repot sekarang apa kak? | 16 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Siap kak. Kira-kira sehari ada berapa chat masuk? | 8 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Itu pertanyaan tersering dari orang tua murid ya kak, bukan nanya harga VIRA, paham. Dari chat pertama sampai daftar, biasanya lewat langkah apa aja kak? | 25 |  |

### S5 Kopi — sampai minta deck (ulang 1)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=chat reservasi numpuk pas weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 35 |  |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Salam kenal kak. Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak? | 13 |  |
| 3 | 100an chat pas weekend | Itu lumayan banyak kak. Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja? | 15 |  |
| 4 | boleh dong dibuatin deck | Siap kak, briefnya sudah aku teruskan ke Steven. Dia yang akan susun deck-nya dan langsung hubungi kakak. Sambil nunggu, kakak bebas tanya apa aja ke aku. | 26 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Dari chat pertama sampai jadi reservasi di Kopi Senja, biasanya lewat langkah apa aja? | 16 |  |

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 2)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin buat kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Oh iya, boleh tau nama kakak siapa, dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 56 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Soal chat yang bikin ribet itu, biasanya yang paling sering ditanyain pembeli apa aja kak? | 18 |  |
| 3 | 100 an chat | Dari 100-an chat itu, yang paling sering ditanyain biasanya apa aja kak? | 12 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Noted kak. Kalau lagi numpuk gitu, biasanya ada chat yang sampai kelewat nggak kak? | 14 |  |
| 5 | aroma, ketahanan, sama ready stok ga | Chat masuknya lewat mana aja kak, WhatsApp doang atau ada dari Instagram juga? | 13 |  |
| 6 | iya kadang ada yg kelewat | Chat masuknya lewat mana aja kak, WhatsApp doang atau ada dari Instagram juga? | 13 |  |

### S2 Katering — ulang uji 17/09 (ulang 2)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=sekitar 20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh juga sekalian tau nama kakak siapa, dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 45 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Kalau malam numpuk gitu, yang paling bikin repot bagian mananya kak? | 14 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Noted kak. Usahanya katering, berarti yang masuk biasanya tanya menu atau order ya kak? | 14 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 4 | sekitar 20-30 chat sehari | Dari chat pertama sampai jadi pesanan, biasanya lewat langkah apa aja kak? | 12 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Kalau lagi numpuk gitu, biasanya yang kelewat tuh chat baru atau follow up pesanan kak? | 15 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 2)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=chat masuk sehari 50an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA ini AI customer service WhatsApp yang balas chat otomatis 24 jam: jawab pertanyaan yang berulang, follow-up calon pembeli, sampai bantu booking atau order, sesuai alur bisnisnya. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 63 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan, setup-nya saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnisnya, paling pas dibicarakan langsung sama Steven. | 25 |  |
| 4 | bisa connect ke IG juga ga? | Bisa kak, IG bisa jadi salah satu channel-nya. Chat masuk dari IG juga ditangani VIRA. | 15 |  |
| 5 | oke, chat masuk sehari 50an | Kalau lagi numpuk gitu, biasanya ada chat yang sampai kelewat nggak kak? | 12 | galian: masalah terbesarnya soal chat sekarang |

### S4 Bimbel — prospek bercerita panjang (ulang 2)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat di Bimbel Cerdas Mandiri, yang paling bikin repot sekarang apa kak? | 16 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Noted kak. Kalau lagi ramai gitu, biasanya ada chat yang sampai kelewat nggak kak? | 14 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Kalau 40 chat masuk sendiri, kira-kira berapa lama baru kebales semua kak? | 12 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Maksudku, kalau 40 chat masuk sendiri, kira-kira berapa lama baru kebales semua kak? | 13 |  |

### S5 Kopi — sampai minta deck (ulang 2)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=100an chat pas weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, aku Steven versi AI, dibangun pakai VIRA, sistem yang sama yang Steven bikin buat kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Senang kakak tertarik. Boleh tau Kopi Senja butuhnya buat balas chat seperti apa dulu kak? | 40 |  |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Siap kak. Kalau lagi numpuk gitu, yang paling bikin repot bagian mananya kak? | 13 | galian: masalah terbesarnya soal chat sekarang |
| 3 | 100an chat pas weekend | Dari chat masuk sampai akhirnya reservasi, biasanya lewat langkah apa aja kak? | 12 |  |
| 4 | boleh dong dibuatin deck | Siap kak, briefnya sudah aku teruskan ke Steven. Dia yang akan susun decknya dan hubungi kakak langsung. Sambil nunggu, kakak bebas tanya apa aja ke aku. | 26 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Dari chat masuk sampai akhirnya reservasi, biasanya lewat langkah apa aja kak? | 14 |  |

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 3)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Oh iya, boleh tau nama kakak siapa, dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 47 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Ribetnya paling kerasa di bagian mana kak, pas jelasin varian parfum atau pas follow-up yang nanya-nanya dulu? | 20 |  |
| 3 | 100 an chat | Dari chat pertama sampai orangnya beli, biasanya lewat langkah apa aja? | 11 | dipangkas jaring: gema (model 18 kata) |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Yang paling sering ditanyain sebelum minta pricelist, biasanya apa aja kak? | 11 |  |
| 5 | aroma, ketahanan, sama ready stok ga | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 6 | iya kadang ada yg kelewat | Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? Biar kakak lihat langsung VIRA-nya jalan pakai contoh chat parfum kakak sendiri. | 22 |  |

### S2 Katering — ulang uji 17/09 (ulang 3)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=sekitar 20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin buat klien-kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh aku bantu jelasin. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 40 | dipangkas jaring: perkenalan (model 47 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Kalau boleh tau, nama usahanya apa ya kak? | 11 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 4 | sekitar 20-30 chat sehari | Chat masuknya lewat mana aja kak? | 6 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Kalau chat lagi numpuk gitu, yang paling bikin repot bagian mananya kak? | 12 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 3)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=chat masuk sehari 50an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA ini AI customer service WhatsApp yang balas chat pelanggan 24 jam, paham bahasa natural, bisa follow-up otomatis, sampai jadwalin booking atau survey, disesuaikan sama alur bisnis kakak. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 64 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan, setup saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis kakak, Steven yang akan hitung pas. | 25 |  |
| 4 | bisa connect ke IG juga ga? | Bisa kak, itu bagian dari kebutuhan custom yang nanti dibahas sama Steven, dia yang tinjau dulu alurnya, baru disusun penawarannya. | 20 |  |
| 5 | oke, chat masuk sehari 50an | Kalau lagi ramai gitu, biasanya ada chat yang sampai kelewat nggak kak? | 12 | galian: masalah terbesarnya soal chat sekarang |

### S4 Bimbel — prospek bercerita panjang (ulang 3)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, dia sendiri yang bales, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 42 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat di bimbelnya, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Kalau lagi ramai gitu, biasanya ada chat yang sampai kelewat nggak kak? | 12 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Pas lagi musim daftar gitu, biasanya yang paling sering ditanyain orang tua apa aja kak? | 15 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Dari chat pertama sampai akhirnya daftar, biasanya lewat langkah apa aja kak? | 12 |  |

### S5 Kopi — sampai minta deck (ulang 3)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=chat reservasi numpuk pas weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Senang bisa bantu kak. Boleh tau nama kakak siapa, dan nama usahanya apa? | 39 |  |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Salam kenal kak. Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak? | 13 |  |
| 3 | 100an chat pas weekend | Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja kak? | 12 |  |
| 4 | boleh dong dibuatin deck | Siap kak, briefnya sudah aku teruskan ke Steven. Dia yang bakal nyusun decknya dan langsung hubungin kakak. Sambil nunggu, kakak bebas tanya apa aja ke aku ya. | 27 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Sambil nunggu, yang paling sering ditanyain customer di chat biasanya apa aja? | 14 |  |
