# Generator deck VIRA

Menyusun pitch deck dari satu baris `REQUESTS`, lalu merender PDF lewat Chrome headless.
Tanpa layanan luar, tanpa login, tanpa langganan.

```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/deck" && python buat_deck.py brief-contoh.json
```

| Perintah | Guna |
|---|---|
| `python buat_deck.py brief-contoh.json` | dari file JSON |
| `python buat_deck.py --wa 628xxxxxxxxxx` | ambil langsung baris REQUESTS dari `sheet/VIRA Database.xlsx` |
| `python buat_deck.py brief-contoh.json --html` | berhenti di HTML, tidak merender PDF |

Keluaran di `keluaran/`: `<nama>.pdf`, `<nama>.html`, `<nama>-pratinjau.html`.

**Sumber kebenaran isi deck: `VIRA for Persada Cisoka Residence.pdf`.** Harga, urutan slide,
kalimat fitur, disclaimer, timeline, dan teks garansi mengikuti deck itu — bukan deck Scholars,
yang beberapa bagiannya sudah usang (harga lama, klaim "kenaikan omzet 20–30%").

---

## Struktur slide — 32 slide, urutan dikunci

| # | Slide | Sifat |
|---|---|---|
| 1 | Cover — “ditujukan kepada” | **custom** |
| 2 | Agenda | tetap |
| 3 | Kutipan Wani Sabu | tetap |
| 4 | Yang aku tangkap soal &lt;bisnis&gt; | **custom** — tambahan, lihat catatan |
| 5 | Pain Points | **custom** |
| 6 | VIRA — A Premium 24/7 AI WhatsApp Assistant System | tetap |
| 7 | WHY? Kenapa memilih VIRA dibanding chatbot mainstream? | tetap |
| 8 | Core Features | tetap (nama fitur aksi menyesuaikan) |
| 9 | The Flow — layar 1: pembuka & FAQ | **custom** — lihat tiga sumber naskah |
| 10 | The Flow — layar 2: percakapan berlanjut sampai tercatat | **custom** |
| 11 | The Flow — Unknown FAQ | **custom** |
| 12 | The Flow — Follow Up & Call Redirection | **custom** |
| 13 | Scale Beyond Limits | tetap |
| 14 | Premium Features — termasuk Send Media & Analyze Photo | tetap |
| 15 | Premium — Send Media, Analyze Photo & Dashboard | semi-custom |
| 16 | Comparison | tetap |
| 17 | Investment (judul) | tetap |
| 18 | Investment table | tetap |
| 19 | Siapa saja yang sudah pakai VIRA? | tetap |
| 20 | The Scholars | tetap |
| 21 | Persada Cisoka Residence | tetap |
| 22 | WHY? Kenapa bisnis Anda harus menggunakan VIRA? | tetap |
| 23 | Advantages & ROI (judul) | tetap |
| 24 | #1 Time Freedom | **custom** |
| 25 | #2 Zero Leaking Profit | **custom** |
| 26 | #3 Scalability without Complexity | **custom** |
| 27 | #4 Brand Trust | tetap |
| 28 | Disclaimer (judul) | tetap |
| 29 | Risiko Teknis & Cara VIRA Menanganinya | tetap |
| 30 | Implementation | tetap (+ catatan dari brief) |
| 31 | 100% Satisfaction Guarantee | tetap |
| 32 | Let’s Start | tetap |

**28 slide berdiri tanpa data klien sama sekali** — terbukti: brief yang seluruh field
kliennya dikosongkan tetap menghasilkan 28 slide yang utuh dan layak kirim.

### The Flow itu empat slide, bukan satu

Deck Persada maupun Scholars memakai enam halaman untuk The Flow, dan percakapannya
BERLANJUT antar halaman — layar berikutnya menampilkan chat yang sama yang sudah
di-scroll, dengan pesan barunya dikotaki merah. Versi satu slide kehilangan justru
bagian yang paling meyakinkan: bahwa ini satu percakapan utuh dari sapaan sampai
tercatat, bukan potongan tanya-jawab.

Empat slidenya memakai satu percakapan yang sama, dipotong jadi layar-layar oleh
`jendela_layar()`. Layar kedua sengaja tumpang tindih empat gelembung dengan layar
pertama — itu yang membuatnya terbaca sebagai chat yang di-scroll, sekaligus mengisi
layar sampai penuh. Telepon yang separuh atasnya kosong langsung terlihat sebagai
gambar buatan.

Yang dikotaki merah **hanya gelembung terakhir**. Mengotaki semua pesan baru membuat
slidenya penuh kotak dan tidak ada yang menonjol.

### Dua slide yang aku tambahkan di luar daftarmu

- **Slide 2 Agenda** — ada di deck Scholars maupun Persada, jadi dikembalikan.
- **Slide 4 “Yang aku tangkap soal &lt;bisnis&gt;”** — kartu berisi apa yang VIRA tangkap dari
  obrolan WhatsApp: yang dijalankan, siapa yang chat, channel, volume, siapa yang membalas,
  yang dikejar dari chat. Ini slide paling murah sekaligus paling personal — datanya sudah ada
  di brief, dan efeknya menunjukkan bahwa kamu benar-benar mendengarkan. Buang saja kalau
  terasa berlebihan.

---

## Yang berubah per klien

| Field brief | Mengisi |
|---|---|
| `nama_bisnis`, `industri` | cover, dashboard, judul slide 4 |
| `deskripsi_bisnis`, `target_pelanggan`, `channel`, `siapa_balas_chat`, `sistem_sekarang`, `sudah_pakai_chatbot` | kartu slide 4 |
| `masalah_utama`, `pain_points` | Pain Points — `masalah_utama` selalu jadi poin pertama |
| `pertanyaan_tersering` | gelembung chat di The Flow — kosong pun slide tetap tampil, lihat di bawah |
| `aksi_utama` | nama fitur (Automated Booking / Survey Scheduling / Order Capture / Consultation) |
| `volume_chat_harian` | jam per bulan (#1), skala chat (#3), chat per bulan di dashboard |
| `biaya_admin_bulanan` | angka admin di #3 — kalau kosong, dipakai rentang umum |
| `data_tersedia`, `integrasi_dibutuhkan`, `deadline` | catatan di slide Implementation |

`nilai_transaksi` dan `prospek_per_bulan` **sengaja tidak dipakai di deck** — keduanya hanya
dikirim ke Steven lewat notifikasi WA saat brief masuk.

---

## Sintaks template

| Sintaks | Arti |
|---|---|
| `{{field}}` | diganti isi field dari brief |
| `{{field\|cadangan}}` | pakai cadangan kalau field kosong |
| `data-butuh="a,b"` | **slide dibuang** kalau salah satu field kosong |
| `<!--ULANG:nama-->…<!--/ULANG-->` | blok diulang per item |
| `<!--DEF:x-->…<!--/DEF-->` | simpan potongan markup |
| `<!--PAKAI:x-->` | sisipkan potongan itu |

`DEF`/`PAKAI` dipakai rangka telepon (bar status, header, bar input) yang muncul di enam
mockup. Disalin enam kali, perbaikan pada salah satunya pasti ada yang tertinggal — dan
satu mockup yang tampilannya beda sendiri merusak kesan "ini WhatsApp beneran".
`PAKAI` yang menunjuk potongan tidak ada = generator berhenti, bukan menyisipkan kosong.

---

## Aturan yang tidak boleh dilanggar

**Angka yang tidak diketahui tidak pernah ditebak.** Field kosong → slide yang membutuhkannya
dibuang, bukan diisi karangan.

**Tapi mockup bukan angka.** Gelembung The Flow punya tiga sumber, berurut:

1. `naskah/<slug>.json` — tulisan tangan untuk klien itu. Kalau ada, dia yang menang.
2. Susunan deterministik dari `pertanyaan_tersering`.
3. Percakapan contoh yang netral, kalau dua-duanya tidak ada.

Sumber 3 sengaja tidak menyebut harga, jadwal, stok, atau satu angka pun — hanya alur
prosesnya, dan slide sudah berlabel *"Ilustrasi tampilan"*. Ini bukan pelanggaran aturan
"jangan menebak": yang dilarang adalah mengarang **fakta klien**, sedangkan ini demo produk.
Generator mencetak `Naskah : contoh umum ...` supaya jelas mana yang perlu ditulis tangan.

**Asumsi selalu dicetak.** Perhitungan jam di slide #1 memakai ±5 menit per chat, dan angka itu
ditulis di slide dalam huruf kecil — bukan disembunyikan.

**Setiap render diperiksa otomatis** (`PERIKSA` di terminal): jumlah halaman harus sama dengan
jumlah slide, ukuran halaman harus 1440×810 pt, sembilan potongan teks wajib harus muncul, dan
**gelembung terakhir percakapan** harus ikut terbaca di PDF. Pemeriksaan itu penting karena slide
punya tinggi tetap dengan `overflow:hidden` — isi yang kepanjangan akan **terpotong diam-diam**.
Sudah dua kali terjadi: baris `Global Language Capability` di tabel harga, dan tiga gelembung
terakhir naskah Alianz.

**Render PDF tidak pernah menimpa berkas lama sebelum berhasil.** Chrome menulis ke
`<nama>-baru.pdf` dulu, baru berkasnya digeser ke nama yang benar. Kalau PDF lama masih terbuka
di penampil PDF, Windows menguncinya dan penggeseran gagal — generator bilang begitu apa adanya
dan menyimpan hasil barunya, bukan mengaku sukses. Versi lama kode ini cuma bertanya "berkasnya
ada?", jadi render yang gagal total dilaporkan sukses lengkap dengan ukurannya.

## Keputusan Steven — 2026-08-31

1. Baris setup fee: label **One-Time System Setup & Integration**, harga **3jt dicoret, Free**
   (deck Persada memang keliru di sini)
2. Add-on **IDR 999.000/month** boleh ditulis. Ditambah **Send Media** dan **Analyze Photo**
   — ❌ Basic, ✅ Premium
3. Nomor benar **+6285155202354** (kedua deck lama salah ketik)
4. Kutipan BCA di slide 3 tetap dipakai
5. Klaim “kenaikan omzet 20–30%” dibuang permanen
6. Slide klien The Scholars & Persada Cisoka, masing-masing dengan cerita + goal
7. `nilai_transaksi` & `prospek_per_bulan` tidak masuk deck — hanya ke notif WA Steven

Catatan butir 2: deck menyebut angka add-on, tapi **bot tetap tidak boleh** (`CONFIG` masih
`"Diskusikan dengan Steven"`). Pemisahan ini disengaja — deck itu dokumen yang sudah dipikirkan,
chat itu langsung.

## Yang belum

- **Balasan VIRA di mockup masih kalimat proses yang umum** — tidak pernah menjawab isi,
  karena isinya memang tidak ada di brief. Idealnya ditulis LLM mengikuti `alur_setelah_chat`.
  Sementara ini jalur `naskah/<slug>.json` yang dipakai kalau butuh kalimat yang benar-benar
  pas; naskah itu mengganti percakapan UTAMA, sedangkan adegan Unknown FAQ, Follow Up, dan
  Call Redirection tetap dari generator.
- **Percakapan lebih dari 10 gelembung belum diuji.** Sejak gelembung ditumpuk dari bawah,
  kelebihan isi terpotong di ATAS — terbaca sebagai chat yang di-scroll, dan gelembung
  terakhir tidak pernah hilang lagi. Kelas `.padat` masih dipasang otomatis supaya
  percakapan panjang mengecil lebih dulu sebelum sampai terpotong.
- **Nomor di Call Redirection masih `0812-xxxx-xxxx`** — sengaja, karena nomor tim klien
  tidak ada di brief. Kalau nomornya diketahui, tulis tangan di `naskah/<slug>.json`.
- **Font** memakai Montserrat kalau ada, jatuh ke Segoe UI kalau tidak. Deck asli kemungkinan
  memakai font lain — kalau tahu namanya, tinggal ganti satu baris di `template.html`.
- **Pain Points terbatas 1 slide** (maksimal 6 poin). Belum ada pemecahan otomatis ke 2 slide.

## Perbaikan 2026-09-04 — dua slide UI flow hilang dari deck Sonic

Brief Sonic hanya 3/33 field. Deck keluar 24 slide tanpa satu pun tampilan produk, tanpa error.

1. **Slide 9 `flow-ui`** kena `data-butuh="aksi_utama"`. Padahal dua field yang dipakai slide itu
   sudah punya cadangan di template, jadi gerbangnya membuang slide yang sebenarnya utuh.
   Gerbang dilepas; yang menentukan slide layak tampil sekarang gelembung percakapannya.
2. **Slide 12 `flow-ui-premium-dashboard`** kena aturan "buang mockup yang tidak punya gelembung",
   yang mencari `class="telepon"`. Slide 12 memang memakai kelas itu — tapi percakapannya bawaan
   template dan tidak butuh data klien sama sekali. Aturannya sekarang mencari penanda
   `<!--ULANG:chat-->`, jadi hanya slide yang benar-benar mengambil gelembung dari brief.
3. **Percakapan contoh** ditambahkan sebagai sumber ketiga, supaya brief tipis tetap punya
   The Flow tanpa mengarang fakta klien.
4. **`ke_pdf` tidak bisa lagi melaporkan sukses palsu.** Ditemukan saat memverifikasi perbaikan
   ini: `sonic.pdf` sedang terbuka di penampil PDF, Chrome gagal menulis, dan generator tetap
   mencetak `PDF : ... (418 KB)` — ukuran berkas LAMA.
5. **Mockup telepon tidak lagi memotong diam-diam.** Tinggi telepon slide 9 dinaikkan ke 576px,
   kelas `.padat` dipasang otomatis untuk percakapan panjang, dan gelembung terakhir ikut
   diperiksa di PDF. Deck Alianz yang lama kehilangan tiga gelembung terakhirnya karena ini —
   **perlu digenerate ulang.**

Uji: `python uji_konsistensi.py` — 24 pemeriksaan, termasuk satu render PDF sungguhan.

## Perbaikan 2026-09-07 — mockup WhatsApp dan The Flow multi-layar

Keluhannya: mockup chat-nya cuma satu layar, dan tampilannya tidak seperti WhatsApp.

1. **Mockup WhatsApp ditulis ulang** mengikuti mockup di `VIRA for Persada Cisoka
   Residence.pdf`: tema gelap, bar status (jam, sinyal, baterai), header ber-avatar dengan
   status "online", latar doodle, keping tanggal dan pemberitahuan enkripsi, gelembung
   berwaktu dengan centang ganda, dan bar input lengkap dengan tombol mic. Versi lama —
   header hijau polos dengan latar krem — tidak menyerupai WhatsApp versi mana pun.
2. **Sisi gelembung dibalik.** Teleponnya milik PELANGGAN (header memuat nama bisnis klien),
   jadi pesan pelanggan ada di kanan dan balasan VIRA di kiri. Sebelumnya terbalik.
3. **Gelembung ditumpuk dari bawah**, seperti WhatsApp sungguhan. Efek sampingnya
   menyelesaikan bug lama: yang terpotong sekarang bagian ATAS, jadi gelembung terakhir
   tidak bisa lagi raib diam-diam seperti pada naskah Alianz.
4. **The Flow jadi empat slide** — lihat bagian di atas.
5. **Kalimat pelanggan dibentuk jadi kalimat tanya.** `pertanyaan_tersering` isinya potongan
   kata ("Fee", "termin pembayaran"); ditempel apa adanya, gelembungnya berbunyi "Fee".
   `kalimat_tanya()` membungkusnya jadi "Halo kak, mau tanya soal fee gimana ya?" — yang
   dibungkus hanya cara bertanyanya, kata-katanya tetap dari brief.

Diuji ke tujuh bentuk brief (0/1/5 pertanyaan, satu pertanyaan sangat panjang, naskah
tulisan tangan, tanpa `aksi_utama`). Semuanya 32 slide dengan kelima slide mockup utuh.
Dua cacat ketemu dari situ dan sudah ditutup:

- Butir yang sudah diawali "kalau" jadi **"Kalau kalau saya baru pindah kerja..."**.
- Singkatan berimbuhan jadi **"kPR-nya"** — penjaganya menguji kata utuh dengan
  `isupper()`, padahal "KPR-nya" memang bukan `isupper()`. Sekarang diuji dari dua huruf
  pertama.

**Naskah tulisan tangan sekarang perlu minimal 8 gelembung.** Kurang dari itu, layar 2
tidak punya kelanjutan — slide 10 mengulang isi slide 9 sambil kolom kanannya menyatakan
datanya sudah tercatat. Generator tidak menolak, tapi mencetak `PERINGATAN`.

Uji: `python uji_konsistensi.py` — 53 pemeriksaan, termasuk satu render PDF sungguhan.

## Gerbang kelengkapan — 2026-09-18

Deck uji 17/09 (katering, "Nadia") terkirim sebagai `tanpa-nama.pdf`: nama bisnis kosong, slide
Konteks Bisnis ikut dibuang, dan satu-satunya tanda adalah baris `COVER GENERIK` di akhir
keluaran. **Keputusan 2026-09-06 "cover generik masih layak kirim" diganti:**

| Tingkat | Field | Kalau kosong |
|---|---|---|
| **BLOKIR** | `nama_bisnis`, `industri`, `masalah_utama` | generator berhenti (exit 2) **sebelum menulis berkas apa pun**. Lanjut hanya kalau Steven mengizinkan per field: `--lanjut-tanpa nama_bisnis` |
| PERINGATAN | `deskripsi_bisnis`, `aksi_utama`, `volume_chat_harian` (harus ada angkanya), `pertanyaan_tersering`, `alur_setelah_chat` | deck tetap jadi; dampaknya dicetak (slide dibuang / isi umum) + pertanyaan siap kirim ke prospek |
| CATATAN | `target_pelanggan`, `sumber_prospek`, `channel`, `biaya_admin_bulanan`, `pertanyaan_tersering` cuma 1 butir | template memakai kalimat umum |

- Tabelnya satu: `KELENGKAPAN` di `buat_deck.py`. `cek_request.py` dan `kirim_deck.py` memakai
  tabel yang sama.
- `kirim_deck.py` menolak kirim **ke klien** selama ada field BLOKIR yang kosong tanpa
  `--lanjut-tanpa` yang sama. Kiriman review ke Steven (`--ke-admin`) tidak diblokir.
- `--lanjut-tanpa` hanya menerima tiga field BLOKIR; field lain ditolak. Tidak ada "paksa semua".
- Brief tanpa nama bisnis sekarang bernama `tanpa-nama-<4 digit akhir no_wa>.pdf` — dulu semua
  `tanpa-nama.pdf`, jadi dua klien tanpa nama saling menimpa.
- Isi field yang kosong boleh **diusulkan** Claude, hanya dari fakta yang sudah ada di brief
  atau STATS, dan baru ditulis ke REQUESTS setelah Steven setuju (lihat skill `deck-request`).

Uji: `python uji_konsistensi.py` — 87 pemeriksaan (bagian [7] untuk gerbang ini), termasuk
`kirim_deck.py` yang dijalankan dengan sheet palsu dan tanpa kredensial Kirimi.
