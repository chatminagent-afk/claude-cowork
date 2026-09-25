# Regresi eval balasan VIRA — v3.13 (×3, 23/09) vs v3.14 (×3, 25/09), model asli (2026-09-25 14:49)

DeepSeek `deepseek-v4-pro` asli, temperature 0.7, lewat workflow eval sementara. Kode node asli dari file workflow; katalog dari sheet live (baca saja). Pesan prospek sama persis untuk semua versi. Metrik dihitung dari teks yang TERKIRIM.

## Ringkasan

| Metrik | v3.13 | v3.14 |
|---|---|---|
| balasan (tanpa perkenalan) | 96 | 96 |
| median kata | 12.0 | 12.0 |
| maks kata | 45 | 62 |
| median kata saat prospek tidak bertanya | 12.0 | 12.0 |
| membuka dengan merangkum (gema) | 0 | 0 |
| promosi VIRA tanpa ditanya | 0 | 0 |
| HARGA VIRA disebut tanpa diminta | 0 | 1 |
| catatan konteks dikutip ke prospek | 0 | 0 |
| konteks harga menyala | 8 (dari 117 giliran) | 10 (dari 117 giliran) |
| > 2 kalimat saat prospek tidak bertanya | 4 | 3 |
| > 1 pertanyaan dalam satu balasan | 2 | 2 |
| jumlah chat ditanya padahal sudah disebut | 0 | 1 |
| pertanyaan kembar dengan balasan sebelumnya | 3 | 5 |
| pertanyaan kembar dalam 2 balasan terakhir | 5 | 7 |
| perkenalan: median kata | 36 | 38 |
| perkenalan: > 1 pertanyaan | 0 | 0 |
| dipangkas jaring (RINGKAS/HARGA) | 17 | 9 |
| dipangkas karena harga | 0 | 0 |
| minta deck dibalas tawaran deck lagi | 0 | 0 |
| balasan 'Maaf, ada kendala' | 0 | 0 |
| STATS nama usaha benar | 18/18 | 18/18 |
| STATS nama usaha kotor | 0 | 0 |
| S6 STATS (nama_bisnis | industri) | - | sewa raket padel; - | sewa raket padel; - | sewa raket padel | - | sewa raket padel; - | sewa raket padel; - | sewa raket padel |
| S7 'kpn bs ngmng sm steven?' -> bot dimatikan | 3/3 | 3/3 |
| handover: balasan mengonfirmasi | 3/3 | 2/3 |
| handover: balasan masih menawarkan 'sambungkan?' | 0 | 0 |


## Analisis selisih (2026-09-25)

- **Kode identik di kedua arah.** Rekaman model eval v3.13 (21 percakapan) diputar lewat kode v3.14, dan rekaman model regresi v3.14 (21 percakapan) diputar lewat kode v3.13. Hasilnya **0 balasan terkirim berbeda dan 0 STATS berbeda**. Semua selisih metrik di atas berasal dari output model, bukan dari kode.
- Beda input model v3.13 dan v3.14 di S1–S7 hanya dua kalimat pengecualian kata tanya di prompt. Catatan harga tegas untuk "brp" polos tidak menyala, karena tidak ada pesan S1–S7 yang berupa brp/berapa polos.
- **HARGA tanpa diminta 0 → 1** (S6 u2 #6, "gimana prosedurnya dan lain-lain"): diuji A/B dengan riwayat percakapan yang persis sama. Prompt v3.13 menyebut harga **0/6**, prompt v3.14 **0/6**. Kejadian ini variasi model (1 dari 117 giliran), bukan akibat prompt baru.
- **Handover mengonfirmasi 3/3 → 2/3:** balasan S7 u2 berbunyi "Siap kak, sudah aku teruskan ke Steven. Dia yang nanti menghubungi kakak langsung." Regex metrik hanya mengenali "sambungkan" atau "Steven akan/bakal menghubungi", jadi ini kelemahan metrik. Bot dimatikan 3/3.
- **Pertanyaan kembar 3 → 5 dan "jumlah chat ditanya padahal sudah disebut" 0 → 1:** kodenya identik (lihat poin pertama). Ini variasi model, termasuk pola lama yang sudah dicatat tertunda di v3.13 ("model kadang bertanya langkah sesudah prospek menjelaskan alur"). Dengan n=3, tidak ada bukti ini disebabkan v3.14. Tidak diuji A/B.

## v3.13

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 1)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin buat kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Dan btw, boleh tau nama kakak siapa, dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 47 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Soal chat yang ribet dibales satu-satu itu, yang paling bikin repot biasanya bagian mananya kak? | 18 |  |
| 3 | 100 an chat | Dari 100-an chat itu, yang paling sering ditanyain biasanya apa aja kak? | 12 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Dari chat pertama sampai akhirnya pesen, biasanya lewat langkah apa aja kak? | 12 |  |
| 5 | aroma, ketahanan, sama ready stok ga | Siap kak. Sekali closing di tempat kakak, masuknya kira-kira berapa rupiah? | 11 |  |
| 6 | iya kadang ada yg kelewat | Kalau chat lagi numpuk gitu, biasanya yang kelewat itu chat baru masuk atau yang udah nanya lama kak? | 18 |  |

### S2 Katering — ulang uji 17/09 (ulang 1)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=sekitar 20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Silakan, aku jawab semampuku. btw boleh tau nama kakak siapa, dan nama usahanya apa? | 40 | dipangkas jaring: perkenalan (model 48 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Halo kak, salam kenal. Kalau boleh tau, nama usahanya apa kak? | 11 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Noted kak. Kira-kira sehari ada berapa chat masuk kak? | 9 | galian: kira-kira berapa chat masuk per hari |
| 4 | sekitar 20-30 chat sehari | Kalau malam lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Pas lagi ramai gitu, yang paling bikin repot bagian mananya kak? | 11 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 1)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=chat masuk sehari 50an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA ini AI Customer Service WhatsApp yang balas chat pelanggan otomatis 24 jam, jadi pas kakak lagi sibuk atau di luar jam kerja, chat tetap kejawab. Dia bisa jawab pertanyaan yang berulang, bantu follow-up, sampai arahin pelanggan ke closing. btw boleh tau nama kakak siapa, dan nama usahanya apa? | 75 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan, setup saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis kakak, jadi lebih pas kalau dibicarakan langsung sama Steven. Sambil menunggu, kira-kira sehari ada berapa chat masuk kak? | 37 | konteks harga |
| 4 | bisa connect ke IG juga ga? | Bisa kak, chat yang masuk dari Instagram juga bisa ditangani VIRA. Aku belum tahu detail teknis integrasinya, tapi ini bisa aku teruskan ke Steven ya. Boleh tau kakak sekarang chat masuknya lewat mana aja? | 34 |  |
| 5 | oke, chat masuk sehari 50an | Dari chat pertama sampai jadi booking, biasanya lewat langkah apa aja kak? | 12 | galian: masalah terbesarnya soal chat sekarang |

### S4 Bimbel — prospek bercerita panjang (ulang 1)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 35 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat di bimbelnya, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Kalau lagi ramai, biasanya ada chat yang sampai kelewat nggak kak? | 11 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | 40 chat itu lumayan padat kak. Dari chat pertama sampai akhirnya daftar, biasanya lewat langkah apa aja? | 17 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Orang tua biasanya paling sering nanya apa aja kak? | 9 |  |

### S5 Kopi — sampai minta deck (ulang 1)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=coffee shop, masalah_utama=chat reservasi numpuk pas weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, salam kenal. Aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama usahanya apa ya kak? | 35 | dipangkas jaring: perkenalan (model 48 kata) |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Noted kak. Yang paling bikin repot soal chat reservasi itu bagian mananya kak? | 13 | galian: masalah terbesarnya soal chat sekarang |
| 3 | 100an chat pas weekend | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 4 | boleh dong dibuatin deck | Siap kak, brief-nya sudah aku teruskan ke Steven. Dia sendiri yang bakal nyusun deck-nya dan nanti langsung hubungin kakak. Sambil nunggu, kakak bebas tanya apa aja ke aku. | 28 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Btw reservasinya biasanya buat apa aja, meja biasa, private room, atau acara khusus? | 15 |  |

### S6 Padel — ulang uji live Steven 23/09 13:22 (Rehan, sewa raket padel) (ulang 1)

STATS akhir: nama_lengkap=Rehan, nama_bisnis=-, industri=sewa raket padel, masalah_utama=balesin chat satu-satu suka tenggelam, volume_chat=10-20 an, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 42 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | rehan / usahaku sewa raket padel | Salam kenal kak. Usahanya sewa raket padel ya, boleh tau nama usahanya apa? | 13 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | persewaan aja sih | Noted kak. Soal chat, yang paling bikin repot sekarang apa kak? | 11 | galian: masalah terbesarnya soal chat sekarang |
| 4 | balesin chat 1 1 sih / suka tenggelem | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 5 | 10-20 an | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 11 |  |
| 6 | gimana prosedurnya dan lain-lain | Maksud kakak prosedur penyewaan raketnya, atau prosedur pemasangan VIRA-nya? | 9 |  |
| 7 | harga dulu, trs klo udah aman baru ke payment | Itu alur penyewaannya ya kak. Dari chat pertama sampai jadi sewa, biasanya lewat langkah apa aja kak? | 17 | konteks harga |
| 8 | okee | Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? | 10 | brief/deck |

### S7 Laundry — minta ngobrol dengan Steven, bahasa singkat (uji live 14:05) (ulang 1)

STATS akhir: nama_lengkap=Dimas, nama_bisnis=Laundry Kilat, industri=laundry, masalah_utama=chat numpuk tiap pagi, sering telat bales, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun pakai VIRA, sistem yang sama yang Steven bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 34 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Dimas, Laundry Kilat | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | chat numpuk tiap pagi, sering telat bales | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 | galian: kira-kira berapa chat masuk per hari |
| 4 | kpn bs ngmng sm steven? | Steven akan menghubungi kakak langsung ya kak. | 7 | HANDOVER (bot OFF) |

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 2)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 35 | GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Soal chat yang bikin repot itu, biasanya bagian mana yang paling makan waktu? | 16 |  |
| 3 | 100 an chat | Dari chat pertama sampai jadi order, biasanya lewat langkah apa aja kak? | 12 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 5 | aroma, ketahanan, sama ready stok ga | Siap kak. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? | 12 | brief/deck |
| 6 | iya kadang ada yg kelewat | Kalau lagi numpuk gitu, biasanya yang kelewat itu chat apa aja kak? | 12 | brief/deck |

### S2 Katering — ulang uji 17/09 (ulang 2)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=-, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=sekitar 20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh juga sekalian tau nama kakak siapa, dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 45 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Kalau malam lagi numpuk gitu, biasanya yang paling bikin repot bagian mananya? | 15 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Noted kak. Oh iya, nama usahanya apa kak? | 8 | dipangkas jaring: tanya-ulang+galian (model 14 kata); galian: nama usahanya — tanya ulang SEKALI ini s |
| 4 | sekitar 20-30 chat sehari | Kalau malam lagi numpuk gitu, biasanya yang paling bikin repot bagian mananya? | 12 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Kalau lagi ramai gitu, biasanya yang kelewat paling sering di bagian mana kak? | 13 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 2)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=chat masuk sehari 50an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA ini AI customer service buat WhatsApp yang balas chat pelanggan 24 jam, paham bahasa natural, bisa follow-up otomatis, sampai jadwalin janji, semuanya dirancang sesuai alur bisnis kakak, bukan template. btw boleh tau nama kakak siapa, dan nama usahanya apa? | 66 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat di klinik, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Paket Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan, setup-nya saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis kakak, jadi lebih pas dibicarakan langsung sama Steven. Kira-kira sehari ada berapa chat masuk ke klinik kak? | 37 | konteks harga |
| 4 | bisa connect ke IG juga ga? | Bisa kak, VIRA bisa terhubung ke Instagram juga, chat dari IG masuk ke satu sistem yang sama, jadi balasannya tetap konsisten. Chat dari IG-nya juga rame kak? | 27 |  |
| 5 | oke, chat masuk sehari 50an | Dari chat pertama sampai jadi pasien datang, biasanya lewat langkah apa aja kak? | 13 | galian: masalah terbesarnya soal chat sekarang |

### S4 Bimbel — prospek bercerita panjang (ulang 2)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 47 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat di bimbelnya, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Siap kak. Kira-kira sehari ada berapa chat masuk? | 8 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 11 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Dari chat sampai akhirnya daftar, biasanya lewat langkah apa aja kak? | 11 | dipangkas jaring: gema (model 20 kata); konteks harga |

### S5 Kopi — sampai minta deck (ulang 2)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=chat reservasi numpuk pas weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Wah pas banget, Kopi Senja lagi cari AI buat bales chat. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 47 | dipangkas jaring: perkenalan (model 58 kata) |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Salam kenal kak. Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak? | 14 |  |
| 3 | 100an chat pas weekend | Dari chat pertama sampai jadi reservasi, biasanya lewat langkah apa aja kak? | 12 |  |
| 4 | boleh dong dibuatin deck | Siap kak, sudah aku teruskan ke Steven. Dia sendiri yang akan menyusun decknya dan menghubungi kakak langsung. | 17 | dipangkas jaring: deck (model 110 kata); brief/deck |
| 5 | makasih kak | Sama-sama kak. Sambil nunggu Steven, kalau ada yang mau ditanya soal VIRA, aku di sini. | 15 |  |

### S6 Padel — ulang uji live Steven 23/09 13:22 (Rehan, sewa raket padel) (ulang 2)

STATS akhir: nama_lengkap=Rehan, nama_bisnis=-, industri=sewa raket padel, masalah_utama=balesin chat 1 1 sih suka tenggelem, volume_chat=10-20 an, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin buat kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw, boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 45 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | rehan / usahaku sewa raket padel | Salam kenal kak. Sewa raket padel ya, boleh tau nama usahanya apa kak? | 13 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | persewaan aja sih | Oke kak. Soal chat, yang paling bikin repot sekarang apa kak? | 11 | galian: masalah terbesarnya soal chat sekarang |
| 4 | balesin chat 1 1 sih / suka tenggelem | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 5 | 10-20 an | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | gimana prosedurnya dan lain-lain | Dari chat pertama sampai akhirnya jadi sewa, biasanya lewat langkah apa aja kak? | 13 |  |
| 7 | harga dulu, trs klo udah aman baru ke payment | Noted kak. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? Kalau boleh tau nama usahanya apa ya kak? | 20 | brief/deck |
| 8 | okee | Siap kak. Briefnya sudah aku teruskan ke Steven, dia yang akan susun decknya dan hubungi kakak langsung. Sambil nunggu, kakak bebas tanya apa aja ke aku. | 26 | brief/deck |

### S7 Laundry — minta ngobrol dengan Steven, bahasa singkat (uji live 14:05) (ulang 2)

STATS akhir: nama_lengkap=Dimas, nama_bisnis=Laundry Kilat, industri=laundry, masalah_utama=chat numpuk tiap pagi, sering telat bales, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 48 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Dimas, Laundry Kilat | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | chat numpuk tiap pagi, sering telat bales | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 | galian: kira-kira berapa chat masuk per hari |
| 4 | kpn bs ngmng sm steven? | Siap kak, sudah aku sambungkan ke Steven. Dia bakal langsung menghubungi kakak ya. | 13 | HANDOVER (bot OFF) |

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 3)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Wah, boleh banget kak. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 40 | dipangkas jaring: perkenalan (model 49 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Soal chat, yang paling bikin repot sekarang bagian mananya kak? | 13 |  |
| 3 | 100 an chat | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 | konteks harga |
| 5 | aroma, ketahanan, sama ready stok ga | Dari chat sampai akhirnya pesen, biasanya lewat langkah apa aja kak? | 11 |  |
| 6 | iya kadang ada yg kelewat | Noted kak. Kalau lagi ramai gitu, yang paling bikin repot bagian mananya kak? | 13 |  |

### S2 Katering — ulang uji 17/09 (ulang 3)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=chat suka numpuk pas malam, volume_chat=20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 54 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Kalau pas malam lagi numpuk gitu, biasanya yang paling bikin repot bagian mananya? | 16 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Noted kak. Kalau chat lagi numpuk pas malam, biasanya ada yang sampai kelewat nggak kak? | 15 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 4 | sekitar 20-30 chat sehari | Siap kak. Kalau lagi ramai gitu, yang paling sering ditanyain biasanya apa aja? | 13 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Dari chat sampai akhirnya pesen, biasanya lewat langkah apa aja kak? | 11 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Itu yang paling bikin repot ya kak. Kalau lagi numpuk gitu, chat-nya masuk lewat mana aja biasanya? | 17 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 3)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=50an per hari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA ini AI customer service buat WhatsApp yang balas chat pelanggan 24 jam, paham bahasa natural, bisa follow-up otomatis, sampai jadwalin janji atau closing order, tergantung alur bisnis kakak. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 65 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Kisaran paketnya mulai Rp3.000.000 per bulan untuk Basic, dan Rp5.000.000 per bulan untuk Premium. Setup awalnya saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis kakak, jadi lebih pas kalau dibicarakan langsung dengan Steven. | 34 | konteks harga |
| 4 | bisa connect ke IG juga ga? | Bisa kak. Chat yang masuk dari Instagram juga bisa ditangani VIRA, jadi pelanggan yang komen atau DM di sana tetap kebalas otomatis. | 22 |  |
| 5 | oke, chat masuk sehari 50an | Kalau lagi ramai gitu, biasanya ada yang sampai kelewat nggak kak? | 11 | galian: masalah terbesarnya soal chat sekarang |

### S4 Bimbel — prospek bercerita panjang (ulang 3)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=Bimbel SD SMP, murid kebanyakan dari sekitar rumah, orang tua suka nanya jadwal dan biaya lewat WA, owner sendiri yang balas, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin buat kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 35 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Kalau lagi ramai gitu, yang paling bikin repot bagian mananya kak? | 11 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Ini jawaban atas pertanyaanku soal alurnya kak. Yang paling sering ditanyain orang tua biasanya apa aja kak? | 17 | konteks harga |

### S5 Kopi — sampai minta deck (ulang 3)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=dong dibuatin deck, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, salam kenal. Aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh cerita sedikit, chat di Kopi Senja biasanya seperti apa kak? | 39 |  |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Wah pas weekend itu biasanya yang paling ramai ya kak. Soal chat reservasi yang numpuk, kira-kira sehari bisa masuk berapa chat kak? | 22 | galian: masalah terbesarnya soal chat sekarang |
| 3 | 100an chat pas weekend | Pas lagi numpuk 100an chat gitu, yang paling bikin repot bagian mananya kak? | 13 | galian: masalah terbesarnya soal chat sekarang |
| 4 | boleh dong dibuatin deck | Siap kak, brief-nya sudah aku teruskan ke Steven. Dia sendiri yang akan menyusun deck-nya dan menghubungi kakak langsung. Sambil menunggu, kakak bebas tanya apa pun ke aku. | 27 | brief/deck |
| 5 | makasih kak | Sama-sama kak, semoga deck-nya nanti pas buat Kopi Senja. | 9 |  |

### S6 Padel — ulang uji live Steven 23/09 13:22 (Rehan, sewa raket padel) (ulang 3)

STATS akhir: nama_lengkap=Rehan, nama_bisnis=-, industri=sewa raket padel, masalah_utama=balesin chat satu-satu suka tenggelam, volume_chat=10-20 an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Dan btw, boleh tau nama kakak siapa, dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 47 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | rehan / usahaku sewa raket padel | Salam kenal kak. Usahanya sewa raket padel ya, nama usahanya apa kak? | 12 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | persewaan aja sih | Oke kak. Soal chat, yang paling bikin repot sekarang apa kak? | 11 | galian: masalah terbesarnya soal chat sekarang |
| 4 | balesin chat 1 1 sih / suka tenggelem | Siap kak. Kira-kira sehari ada berapa chat masuk kak? | 9 | galian: kira-kira berapa chat masuk per hari |
| 5 | 10-20 an | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 6 | gimana prosedurnya dan lain-lain | Maksudnya prosedur pemasangan VIRA-nya ya kak? Kalau iya, alurnya gini: kakak cerita soal bisnisnya, Steven yang rancang alurnya, terus dipasang di WhatsApp kakak, diuji dulu, baru jalan. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? Kalau boleh tau nama usahanya apa ya kak? | 45 |  |
| 7 | harga dulu, trs klo udah aman baru ke payment | Dari chat sampai akhirnya sewa, biasanya lewat langkah apa aja kak? | 11 | dipangkas jaring: gema (model 22 kata); konteks harga |
| 8 | okee | Noted kak. Biasanya mereka paling sering nanya apa aja kak? | 10 |  |

### S7 Laundry — minta ngobrol dengan Steven, bahasa singkat (uji live 14:05) (ulang 3)

STATS akhir: nama_lengkap=Dimas, nama_bisnis=Laundry Kilat, industri=laundry, masalah_utama=chat numpuk tiap pagi, sering telat bales, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 47 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Dimas, Laundry Kilat | Salam kenal kak. Soal chat di Laundry Kilat, yang paling bikin repot sekarang apa kak? | 15 | galian: masalah terbesarnya soal chat sekarang |
| 3 | chat numpuk tiap pagi, sering telat bales | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 11 | galian: kira-kira berapa chat masuk per hari |
| 4 | kpn bs ngmng sm steven? | Siap kak, aku sambungkan ke Steven ya, dia yang bakal langsung hubungin kakak. | 13 | HANDOVER (bot OFF) |

## v3.14

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 1)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Silakan cerita soal kebutuhan bisnis kakak, aku bantu jawab sebisanya. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 46 | GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Soal chat yang bikin ribet itu, biasanya yang paling sering ditanyain apa aja kak? | 17 |  |
| 3 | 100 an chat | Dari chat pertama sampai akhirnya beli, biasanya lewat langkah apa aja kak? | 12 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 5 | aroma, ketahanan, sama ready stok ga | Siap kak. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? | 12 |  |
| 6 | iya kadang ada yg kelewat | Briefnya sudah aku teruskan ke Steven kak, dia yang akan menyusun decknya dan menghubungi kakak langsung. Sambil nunggu, kakak bebas tanya apa aja ke aku. | 25 | brief/deck |

### S2 Katering — ulang uji 17/09 (ulang 1)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=sekitar 20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem AI customer service yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 39 | dipangkas jaring: perkenalan (model 48 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Nama usahanya apa ya kak? | 8 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Kira-kira sehari ada berapa chat masuk? | 6 | dipangkas jaring: gema (model 10 kata); galian: kira-kira berapa chat masuk per hari |
| 4 | sekitar 20-30 chat sehari | Siap kak. Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak? | 13 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Noted kak. Dari chat sampai akhirnya pesen, biasanya lewat langkah apa aja? | 12 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 1)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=50an per hari, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia buat untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA ini AI customer service buat WhatsApp, jadi dia bisa balas chat pelanggan 24 jam, jawab pertanyaan yang sering ditanya, bantu proses order atau booking, sampai follow-up otomatis ke orang yang belum deal. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 69 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat di klinik, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Kisaran paketnya mulai dari Rp3.000.000 per bulan untuk Basic, dan Rp5.000.000 per bulan untuk Premium kak. Setup dan integrasi awal saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis klinik kakak, jadi lebih enak dibicarakan langsung sama Steven biar pas. | 40 | konteks harga |
| 4 | bisa connect ke IG juga ga? | Bisa kak, chat yang masuk dari Instagram juga bisa ditangani VIRA. Mau aku mintakan Steven buatkan deck khusus buat Klinik Sehat Gigi? | 22 |  |
| 5 | oke, chat masuk sehari 50an | Siap kak, briefnya sudah aku teruskan ke Steven, dia yang akan menyusun decknya dan menghubungi kakak langsung. Sambil menunggu, kakak bebas tanya apa pun ke aku ya. | 27 | brief/deck |

### S4 Bimbel — prospek bercerita panjang (ulang 1)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 35 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Kalau lagi banyak yang nanya barengan, biasanya ada yang sampai kelewat nggak kak? | 13 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Kira-kira dari 40 chat itu, berapa yang biasanya lanjut daftar kak? | 11 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Kalau daftar lewat form, biasanya orang tua itu udah tau dari mana aja kak? | 14 | konteks harga |

### S5 Kopi — sampai minta deck (ulang 1)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=100an chat pas weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh cerita sedikit, chat di Kopi Senja biasanya seperti apa? Btw nama kakak ya, salam kenal. | 42 |  |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Noted kak. Yang paling bikin repot dari chat reservasi pas weekend itu apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | 100an chat pas weekend | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat atau lama kebales nggak kak? | 14 |  |
| 4 | boleh dong dibuatin deck | Siap kak, brief-nya sudah aku teruskan ke Steven. Dia yang akan menyusun deck-nya dan nanti menghubungi kakak langsung. Sambil menunggu, kakak bebas tanya apa pun ke aku. | 27 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Sambil nunggu Steven, pertanyaan yang paling sering masuk ke chat Kopi Senja biasanya apa aja kak? | 18 |  |

### S6 Padel — ulang uji live Steven 23/09 13:22 (Rehan, sewa raket padel) (ulang 1)

STATS akhir: nama_lengkap=Rehan, nama_bisnis=-, industri=sewa raket padel, masalah_utama=balesin chat satu-satu dan suka tenggelam, volume_chat=10-20 an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Silakan cerita soal bisnis kakak, nanti aku bantu arahkan. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 45 | GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | rehan / usahaku sewa raket padel | Salam kenal kak. Usahanya sewa raket padel ya, boleh tau nama usahanya apa? | 13 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | persewaan aja sih | Siap kak. Soal chat, yang paling bikin repot sekarang apa kak? | 11 | galian: masalah terbesarnya soal chat sekarang |
| 4 | balesin chat 1 1 sih / suka tenggelem | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 5 | 10-20 an | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 6 | gimana prosedurnya dan lain-lain | Maksud kakak prosedur pakai VIRA-nya, atau prosedur sewanya? | 8 |  |
| 7 | harga dulu, trs klo udah aman baru ke payment | Dari chat sampai akhirnya sewa, biasanya lewat langkah apa aja kak? | 11 | dipangkas jaring: gema (model 22 kata); konteks harga |
| 8 | okee | Oke kak, maksudku langkahnya gimana, dari orang chat pertama kali sampai akhirnya sewa raket, biasanya lewat proses apa aja? | 19 |  |

### S7 Laundry — minta ngobrol dengan Steven, bahasa singkat (uji live 14:05) (ulang 1)

STATS akhir: nama_lengkap=Dimas, nama_bisnis=Laundry Kilat, industri=laundry, masalah_utama=chat numpuk tiap pagi, sering telat bales, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Dimas, Laundry Kilat | Salam kenal kak. Soal chat di Laundry Kilat, yang paling bikin repot sekarang apa? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | chat numpuk tiap pagi, sering telat bales | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 11 | galian: kira-kira berapa chat masuk per hari |
| 4 | kpn bs ngmng sm steven? | Siap kak, sudah aku sambungkan ke Steven, dia yang akan menghubungi kakak langsung. | 13 | HANDOVER (bot OFF) |

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 2)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 35 | GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Kalau lagi ramai gitu, biasanya ada chat yang sampai kelewat nggak kak? | 15 |  |
| 3 | 100 an chat | Pertanyaan yang paling sering masuk biasanya apa aja kak? | 9 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Dari chat sampai akhirnya beli, biasanya lewat langkah apa aja kak? | 11 |  |
| 5 | aroma, ketahanan, sama ready stok ga | Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? | 10 |  |
| 6 | iya kadang ada yg kelewat | Sudah aku teruskan ke Steven kak, dia sendiri yang akan menyusun deck-nya dan menghubungi kakak langsung. Sambil menunggu, kakak bebas tanya apa pun ke aku. | 25 | brief/deck |

### S2 Katering — ulang uji 17/09 (ulang 2)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=20-30 chat per hari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 34 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Nama usahanya apa ya? | 7 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Kira-kira sehari berapa chat masuk kak? | 6 | galian: kira-kira berapa chat masuk per hari |
| 4 | sekitar 20-30 chat sehari | Chat yang numpuk pas malem itu biasanya nanya apa aja kak? | 11 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Dari chat pertama sampai jadi pesanan, biasanya lewat langkah apa aja kak? | 12 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Pas lagi numpuk gitu, yang paling bikin repot bagian mananya kak? | 11 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 2)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=50an chat per hari, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA itu AI Customer Service WhatsApp yang balas chat pelanggan 24 jam, paham bahasa natural, bisa follow-up otomatis, sampai alihkan ke manusia kalau perlu. Bisa dipakai buat bisnis yang chat-nya udah ramai dan pertanyaannya berulang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 71 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per bulan kak, setup-nya saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnisnya, jadi lebih pas kalau dibicarakan langsung sama Steven. | 28 | konteks harga |
| 4 | bisa connect ke IG juga ga? | Bisa kak, VIRA bisa menangani chat yang masuk lewat Instagram juga, bukan cuma WhatsApp. Jadi kalau kakak aktif di IG, leads dari sana juga ikut kebalas otomatis. Ini nanti detailnya dibahas sama Steven ya. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? | 44 |  |
| 5 | oke, chat masuk sehari 50an | Siap kak, sudah aku teruskan ke Steven. Dia sendiri yang akan menyusun deck-nya dan menghubungi kakak langsung. Sambil menunggu, kakak bebas tanya apa pun ke aku. | 26 | brief/deck |

### S4 Bimbel — prospek bercerita panjang (ulang 2)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=orang tua murid sering tanya jadwal dan biaya lewat WA, dibalas sendiri oleh Sari, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat di bimbelnya, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 11 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Noted kak. Dari chat sampai akhirnya daftar, biasanya lewat langkah apa aja kak? | 13 | konteks harga |

### S5 Kopi — sampai minta deck (ulang 2)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=chat reservasi numpuk saat weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Senang bisa bantu. Soal AI buat bales chat, Kopi Senja biasanya nerima chat kayak apa aja kak? | 43 |  |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Wah iya, weekend pasti rame banget. Yang paling bikin repot pas chat numpuk gitu apa kak? | 16 | galian: masalah terbesarnya soal chat sekarang |
| 3 | 100an chat pas weekend | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 4 | boleh dong dibuatin deck | Siap kak, briefnya sudah aku teruskan ke Steven, dia yang akan susun decknya dan langsung menghubungi kakak. Sambil nunggu, kakak bebas tanya apa aja ke aku ya. | 27 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Kalau ada yang mau ditanyain soal VIRA, tinggal chat aja ya. | 13 |  |

### S6 Padel — ulang uji live Steven 23/09 13:22 (Rehan, sewa raket padel) (ulang 2)

STATS akhir: nama_lengkap=Rehan, nama_bisnis=-, industri=sewa raket padel, masalah_utama=chat suka tenggelam, dibalas satu-satu, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin buat kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau nama kakak siapa, dan nama usahanya apa? | 35 | GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | rehan / usahaku sewa raket padel | Noted kak. Usahanya bernama apa? | 5 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | persewaan aja sih | Oh iya, nama usahanya apa kak? | 6 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 4 | balesin chat 1 1 sih / suka tenggelem | Soal chat, yang paling bikin repot sekarang apa kak? | 9 | galian: masalah terbesarnya soal chat sekarang |
| 5 | 10-20 an | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 6 | gimana prosedurnya dan lain-lain | Prosedurnya gini kak: Steven ngobrol dulu sama kakak buat paham alur bisnisnya, terus dia rancang VIRA-nya khusus buat sewa raket padel kakak, bukan template. Setelah jadi, VIRA balas chat 24 jam, catat booking, dan follow-up otomatis. Setup-nya gratis, biaya bulanannya mulai Rp3.000.000, angka finalnya tergantung kompleksitas alurnya. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? Nama usahanya apa ya kak? | 62 | HARGA TANPA DIMINTA |
| 7 | harga dulu, trs klo udah aman baru ke payment | Siap kak. Dari chat masuk sampai akhirnya orang sewa, biasanya lewat langkah apa aja? | 14 | konteks harga; galian: kira-kira berapa chat masuk per hari |
| 8 | okee | Jadi alurnya gimana kak, dari orang chat sampai akhirnya sewa raket? | 11 | galian: kira-kira berapa chat masuk per hari |

### S7 Laundry — minta ngobrol dengan Steven, bahasa singkat (uji live 14:05) (ulang 2)

STATS akhir: nama_lengkap=Dimas, nama_bisnis=Laundry Kilat, industri=laundry, masalah_utama=chat numpuk tiap pagi, sering telat bales, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, salam kenal. Aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin buat kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 38 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Dimas, Laundry Kilat | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | chat numpuk tiap pagi, sering telat bales | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 4 | kpn bs ngmng sm steven? | Siap kak, sudah aku teruskan ke Steven. Dia yang nanti menghubungi kakak langsung. | 13 | HANDOVER (bot OFF) |

### S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek) (ulang 3)

STATS akhir: nama_lengkap=Abdul, nama_bisnis=humanizer, industri=jualan parfum, masalah_utama=kdg ribet balesin org ty 1 1, volume_chat=100 an chat, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Oh iya, boleh tau nama kakak siapa dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 53 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1 | Salam kenal kak. Soal chat yang ribet dibales satu-satu itu, yang paling bikin repot biasanya di bagian mana? | 18 |  |
| 3 | 100 an chat | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 4 | tanya2 dlu, trs minta pricelist, dan pesen | Noted kak. Pertanyaan yang paling sering masuk ke chat biasanya soal apa aja kak? | 14 | konteks harga |
| 5 | aroma, ketahanan, sama ready stok ga | Siap kak. Mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? kalau boleh tau nama usahanya apa ya kak? | 20 | brief/deck |
| 6 | iya kadang ada yg kelewat | Paham kak. Kalau lagi ramai gitu, yang paling bikin repot bagian mananya? | 12 | brief/deck |

### S2 Katering — ulang uji 17/09 (ulang 3)

STATS akhir: nama_lengkap=Nadia, nama_bisnis=Dapur Nadia, industri=katering, masalah_utama=chat suka numpuk pas malem, volume_chat=sekitar 20-30 chat sehari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, mau tanya soal chatbot | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Silakan, aku jawab semampuku. btw boleh tau nama kakak siapa, dan nama usahanya apa? | 40 | dipangkas jaring: perkenalan (model 47 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Nadia kak, bisnis aku katering, chat suka numpuk pas malem | Salam kenal kak. Oh iya, nama usahanya apa ya kak? | 10 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | Dapur Nadia | Siap kak. Kira-kira sehari ada berapa chat masuk? | 8 | galian: kira-kira berapa chat masuk per hari |
| 4 | sekitar 20-30 chat sehari | Kalau lagi numpuk gitu, biasanya ada chat yang sampai kelewat nggak kak? | 12 |  |
| 5 | biasanya tanya menu dulu, trus harga, baru pesen | Yang paling sering ditanyain biasanya apa aja kak? | 8 |  |
| 6 | ada yg sampe kelewat sih kak kadang | Chat yang kelewat itu biasanya soal apa kak? | 8 |  |

### S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong) (ulang 3)

STATS akhir: nama_lengkap=Budi, nama_bisnis=Klinik Sehat Gigi, industri=klinik, masalah_utama=-, volume_chat=50an chat per hari, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo, ini bisa buat apa aja ya? | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. VIRA ini AI customer service WhatsApp yang balas chat pelanggan 24 jam, paham bahasa natural, bisa follow-up otomatis, sampai bantu closing, semuanya disesuaikan sama alur bisnis kakak, bukan template. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 65 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Budi, Klinik Sehat Gigi | Salam kenal kak. Soal chat, yang paling bikin repot sekarang apa kak? | 12 | galian: masalah terbesarnya soal chat sekarang |
| 3 | harganya berapa kak? | Kisaran paketnya mulai dari Rp3.000.000 per bulan untuk Basic, dan Rp5.000.000 per bulan untuk Premium kak. Setup awal saat ini gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis kakak, jadi lebih pas kalau dibicarakan langsung dengan Steven. | 36 | konteks harga |
| 4 | bisa connect ke IG juga ga? | Bisa kak, itu termasuk kebutuhan custom yang nanti ditinjau dulu bareng Steven, dia yang pastikan alurnya cocok sama sistem klinik kakak. Jadi sekarang chat masuk ke klinik paling banyak lewat mana kak? | 32 |  |
| 5 | oke, chat masuk sehari 50an | Siap kak. Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 14 | galian: masalah terbesarnya soal chat sekarang |

### S4 Bimbel — prospek bercerita panjang (ulang 3)

STATS akhir: nama_lengkap=Sari, nama_bisnis=Bimbel Cerdas Mandiri, industri=bimbel, masalah_utama=bimbel SD SMP, murid dari sekitar rumah, orang tua sering tanya jadwal dan biaya lewat WA, dibalas sendiri, volume_chat=sehari bisa 40 chat kalo lagi musim daftar, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | dipangkas jaring: perkenalan (model 41 kata); galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Sari dari Bimbel Cerdas Mandiri | Salam kenal kak. Soal chat di bimbel, yang paling bikin repot sekarang apa kak? | 14 | galian: masalah terbesarnya soal chat sekarang |
| 3 | bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales | Noted kak. Kira-kira sehari ada berapa chat masuk kak? | 9 | galian: kira-kira berapa chat masuk per hari |
| 4 | sehari bisa 40 chat kalo lagi musim daftar | Kalau lagi 40 chat gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 5 | tanya biaya, jadwal, trus daftar lewat form | Pertanyaan soal biaya dan jadwal itu yang paling sering masuk ya kak? | 12 | konteks harga |

### S5 Kopi — sampai minta deck (ulang 3)

STATS akhir: nama_lengkap=Rina, nama_bisnis=Kopi Senja, industri=kopi, masalah_utama=chat reservasi numpuk pas weekend, volume_chat=100an chat pas weekend, deck_requested=Y

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Boleh tau kakak lagi cari AI buat bales chat yang kayak gimana, dan btw boleh tau nama kakak siapa, dan nama usahanya apa? | 49 |  |
| 2 | coffee shop kak, chat reservasi numpuk pas weekend | Salam kenal kak. Pas weekend numpuknya biasanya berapa chat masuk kak? | 11 |  |
| 3 | 100an chat pas weekend | Kalau lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 11 |  |
| 4 | boleh dong dibuatin deck | Siap kak, briefnya sudah aku teruskan ke Steven. Dia sendiri yang akan nyusun deck khusus buat Kopi Senja dan bakal langsung hubungin kakak, sambil nunggu kakak bebas tanya apa aja ke aku. | 32 | brief/deck |
| 5 | makasih kak | Sama-sama kak. Btw pas weekend gitu, yang paling sering ditanyain biasanya apa aja? | 13 |  |

### S6 Padel — ulang uji live Steven 23/09 13:22 (Rehan, sewa raket padel) (ulang 3)

STATS akhir: nama_lengkap=Rehan, nama_bisnis=-, industri=sewa raket padel, masalah_utama=balesin chat 1 1 sih suka tenggelem, volume_chat=10-20 an, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku. | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya, jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Oh iya, boleh tau nama kakak siapa dan nama usahanya apa? | 37 | dipangkas jaring: perkenalan (model 46 kata); GEMA; galian: namanya dan nama usahanya — tanyakan ber |
| 2 | rehan / usahaku sewa raket padel | Salam kenal kak. Sewa raket padel, itu di lapangan padel, kakak punya venue-nya sendiri atau jasa rentalnya aja? | 18 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 3 | persewaan aja sih | Oke kak. Soal chat masuk, yang paling bikin repot sekarang apa? | 11 | galian: nama usahanya — tanya ulang SEKALI ini s |
| 4 | balesin chat 1 1 sih / suka tenggelem | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 5 | 10-20 an | Kalau chat lagi numpuk gitu, biasanya ada yang sampai kelewat nggak kak? | 12 |  |
| 6 | gimana prosedurnya dan lain-lain | Biasanya orang yang chat ke kakak paling sering nanya apa aja? | 11 |  |
| 7 | harga dulu, trs klo udah aman baru ke payment | Dari chat pertama sampai akhirnya sewa, biasanya lewat langkah apa aja kak? | 12 | dipangkas jaring: gema (model 26 kata); konteks harga |
| 8 | okee | Noted kak. Kalau begitu, mau aku mintakan Steven buatkan deck khusus buat bisnis kakak? | 14 |  |

### S7 Laundry — minta ngobrol dengan Steven, bahasa singkat (uji live 14:05) (ulang 3)

STATS akhir: nama_lengkap=Dimas, nama_bisnis=Laundry Kilat, industri=laundry, masalah_utama=chat numpuk tiap pagi, sering telat bales, volume_chat=-, deck_requested=-

| # | Prospek | VIRA (terkirim) | kata | catatan |
|---|---|---|---|---|
| 1 | halo | Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw boleh tau nama kakak siapa, dan nama usahanya apa? | 36 | galian: namanya dan nama usahanya — tanyakan ber |
| 2 | Dimas, Laundry Kilat | Salam kenal kak. Soal chat di Laundry Kilat, yang paling bikin repot sekarang apa kak? | 15 | galian: masalah terbesarnya soal chat sekarang |
| 3 | chat numpuk tiap pagi, sering telat bales | Kira-kira sehari ada berapa chat masuk kak? | 7 | galian: kira-kira berapa chat masuk per hari |
| 4 | kpn bs ngmng sm steven? | Siap kak, Steven akan langsung menghubungi kakak ya. | 8 | HANDOVER (bot OFF) |
