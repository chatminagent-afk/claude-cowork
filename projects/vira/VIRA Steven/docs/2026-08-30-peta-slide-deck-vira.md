# Peta slide deck VIRA — basis untuk template otomatis

**Sumber:**
- `Persada Cisoka Residence/arsip/2026-07-16/VIRA for Persada Cisoka Residence.pdf` — 31 slide, **acuan utama** (info & harga terbaru)
- `the scholars/client-materials/VIRA.pdf` — 31 slide, dipakai sebagai pembanding untuk tahu apa yang berubah antar klien

Keduanya dibaca lewat lapisan teks PDF (pypdf), bukan tebakan. Mockup gambar tidak punya lapisan
teks — isinya diketahui dari caption di sekitarnya.

---

## Ringkasan

| Sifat | Jumlah | Porsi |
|---|---|---|
| **Tetap** — sama persis di kedua deck | 16 slide | 52% |
| **Variabel teks** — ganti kalimat, layout sama | 9 slide | 29% |
| **Variabel berat** — mockup percakapan, harus dibuat ulang | 5 slide | 16% |
| **Kondisional** — muncul/hilang tergantung klien | 3 slide | — |

**Artinya: lebih dari separuh deck bisa dicetak apa adanya.** Yang benar-benar mahal cuma 5 slide
mockup. Ini yang bikin otomasi masuk akal.

---

## Peta 31 slide (nomor mengikuti deck Persada)

| # | Slide | Sifat | Diisi field |
|---|---|---|---|
| 1 | Cover — "The Future of Customer Service" + tagline | var. ringan | `nama_bisnis`, `industri` |
| 2 | Agenda | var. ringan | jumlah bagian ikut slide kondisional |
| 3 | Kutipan Wani Sabu (BCA) | **tetap** | — |
| 4 | Pain Points | **variabel** | `masalah_utama`, `pain_points`, `sumber_leads`, `jam_operasional`, `siapa_balas_chat`, `channel` |
| 5 | "VIRA — A Premium 24/7 AI WhatsApp Assistant System" | **tetap** | — |
| 6 | WHY? — pembatas | **tetap** | — |
| 7 | Core Features (9 fitur) | **variabel** | `aksi_utama`, `fitur_diminati`, `alur_setelah_chat` |
| 8 | The Flow — Start! | tetap (rangka) | — |
| 9 | Mockup: FAQ + awal alur | **mockup** | `kutipan_asli`, `pertanyaan_tersering`, `target_pelanggan` |
| 10 | Mockup: aksi utama tercatat + notify | **mockup** | `aksi_utama`, `alur_setelah_chat` |
| 11 | Mockup: Basic Analytics (+ Traffic Source) | **mockup** | `sumber_leads`, `channel` |
| 12 | Mockup: Unknown FAQ | mockup (hampir tetap) | — |
| 13 | Mockup: Automated Follow Up (+ Call Redirection) | **mockup** | `aksi_utama`, `fitur_diminati` |
| 14 | Scale Beyond Limits — pembatas | **tetap** | — |
| 15 | Premium Features | **tetap** | — |
| 16 | Advanced Insights | **tetap** | — |
| 17 | 3 fitur premium | **tetap** | — |
| 18 | Comparison Basic vs Premium | var. ringan | `aksi_utama`, `fitur_diminati` (nama baris ikut berubah) |
| 19 | Investment — pembatas | **tetap** | — |
| 20 | Tabel harga | **tetap** | dari CONFIG — 3jt / 5jt / setup gratis |
| 21 | WHY? — pembatas | **tetap** | — |
| 22 | Advantages & ROI — pembatas | **tetap** | — |
| 23 | #1 Time Freedom | **variabel** | `jumlah_admin`, `volume_chat_harian` |
| 24 | #2 Zero Leaking Profit | **variabel** | `industri`, `target_pelanggan`, `aksi_utama` |
| 25 | #3 Scalability | **variabel** | `volume_chat_harian`, `biaya_admin_bulanan` |
| 26 | #4 Brand Trust | **variabel** | `industri`, `aksi_utama` |
| 27 | Disclaimer — pembatas | kondisional | ada di Persada, tidak ada di Scholars |
| 28 | Risiko teknis & cara menanganinya | kondisional | ada di Persada, tidak ada di Scholars |
| 29 | Implementation Day 1/15/30/31 | var. ringan | `data_tersedia`, `integrasi_dibutuhkan`, `deadline` |
| 30 | 100% Satisfaction Guarantee | **tetap** | dari `CONFIG.guarantee_text` |
| 31 | Let's Start + kontak | **tetap** | — |

### Slide kondisional yang terbukti

| Slide | Scholars | Persada | Pemicu |
|---|---|---|---|
| Pain Points | **2 slide** (7 poin) | 1 slide (4 poin) | jumlah `pain_points` |
| Mockup Invoicing | ada | **dibuang** | `fitur_diminati` / `aksi_utama` |
| Disclaimer + Risiko Teknis | tidak ada | **2 slide baru** | selalu sertakan (lebih jujur) |

---

## Yang berubah antar klien — bukti dari diff dua deck

| Hal | Scholars | Persada |
|---|---|---|
| Tagline cover | "Respon instan, konversi maksimal." | "Respon cepat, konversi maksimal" |
| Aksi utama | Automated **Booking** | Automated **Survey Scheduling** |
| Fitur khas | Automated Invoicing, Order Form | Call Redirection, Traffic Source Recognition |
| Harga Basic / Premium | 2.499.000 / 4.499.000 | **3.000.000 / 5.000.000** |
| Setup fee | 1.999.000 (Free) | 3.000.000 (Free) |
| Add-on Global Language | tidak dicantumkan | **IDR 999.000/month** |
| #1 Time Freedom | 2 jam chat + 1 jam invoice → 60 jam/bulan | 1 orang × 3 jam → 90 jam/bulan |
| #3 Scalability | chat 100 → 1000/hari | chat 50 → 100/hari |
| Garansi | dibatasi "first 30 days" | tanpa batas waktu |

---

## Temuan yang butuh keputusanmu

### 1. ⚠️ Baris setup fee di slide harga Persada kemungkinan rusak

Scholars:
```
One-Time System Setup & Integration   IDR 1.999.000 (Free)
WhatsApp Auto-Reply                   ✅  ✅
FAQ                                   ✅  ✅
```
Persada:
```
WhatsApp Auto-Reply                   IDR 3.000.000 (Free)
FAQ                                   ✅  ✅
```

Label "One-Time System Setup & Integration" **hilang**, dan baris fitur WhatsApp Auto-Reply ikut
lenyap — nama fiturnya kepakai untuk baris setup. Terbaca seperti "WhatsApp Auto-Reply harganya
3 juta, digratiskan". Ini di slide harga, slide yang paling lama dipandangi orang. Perlu dicek
di file aslinya apakah memang begitu tampilannya, atau cuma artefak urutan ekstraksi teks.

### 2. ⚠️ Add-on IDR 999.000 di deck vs "jangan sebut angka add-on" di bot

Deck Persada mencantumkan Global Language Capability **IDR 999.000/month**. Tapi `CONFIG` menulis
harga add-on `"Diskusikan dengan Steven"`, dan system prompt melarang: *"Untuk add-on: sebutkan
add-on-nya ada dan apa gunanya, tapi jangan pernah menyebut angka"*.

Jadi bot menolak menyebut angka, deck menyebutkan. Salah satu harus mengalah — mana yang benar?

### 3. ⚠️ Nomor telepon di slide penutup perlu diverifikasi

Kedua deck menutup dengan `+628155202354` (12 digit). Catatan proyek menulis nomor Steven
`6285155202354` (13 digit). Dua-duanya format nomor Indonesia yang masuk akal, jadi aku tidak bisa
memastikan mana yang benar dari sini — tapi selisihnya nyata dan ini nomor di slide penutup deck
jualan. Tolong dicek. (Terpisah dari itu: nomor VIRA Personal yang baru nanti mungkin harus
menggantikannya.)

### 4. Kutipan BCA di slide 3 vs pantangan menyebut employer

Slide 3 mengutip **"Wani Sabu — Head of Contact Center & Digital Services at BCA"**. Sementara
`ABOUT_STEVEN` menulis PANTANGAN: *"JANGAN PERNAH menyebut nama bank tempat Steven bekerja"*.
Bot menutupi, deck membuka. Kutipannya sendiri kemungkinan publik, jadi ini soal positioning,
bukan kebocoran — tapi tidak konsisten. Keputusanmu.

### 5. Klaim angka di deck Scholars sudah dibuang di Persada — pertahankan

Scholars slide 26 menulis *"Potensi kenaikan omzet 20–30%"* dan contoh perhitungan
*"50 prospek/bulan..."*. System prompt sekarang melarang keras: *"Jangan menjanjikan hasil dalam
angka (kenaikan penjualan, jumlah leads, persentase apa pun)."* Persada sudah membuangnya.
Template harus ikut Persada. **Tidak ada yang perlu diubah — cukup jangan mundur ke versi Scholars.**

---

## Implikasi ke Paket C — perlu ditinjau ulang

Paket C kemarin menaikkan `nilai_transaksi` + `prospek_per_bulan` ke TINGKAT 2B, dengan alasan
dokumen desain menyebut keduanya sebagai bahan slide ROI.

**Deck Persada — versi terbaru — tidak memakai dua angka itu sama sekali.** Slide 23–26 dibangun
dari waktu dan biaya kepala, bukan nilai transaksi:

- slide 23 butuh `jumlah_admin` + `volume_chat_harian`
- slide 25 butuh `volume_chat_harian` + `biaya_admin_bulanan`

Yang memakai `nilai_transaksi` × `prospek_per_bulan` justru deck **Scholars**, di bagian yang sudah
sengaja dibuang karena melanggar aturan "jangan janji angka".

**Tiga pilihan:**

| | Pilihan | Konsekuensi |
|---|---|---|
| **a** | Biarkan 2B seperti sekarang, lalu bikin slide ROI baru yang memakai dua angka itu — dibingkai sebagai *hitungan potensi milik klien*, bukan janji Steven | Deck lebih kuat, tapi harus hati-hati agar tidak jadi klaim |
| **b** | Ganti isi 2B: yang ditanya `jumlah_admin` + `biaya_admin_bulanan`, karena itu yang benar-benar dipakai slide 23 & 25 | Paling setia pada deck yang ada. Perubahan kecil di system prompt |
| **c** | Gabung: 2B menanyakan `jumlah_admin` + `biaya_admin_bulanan` dulu (dipakai pasti), dua angka transaksi hanya kalau prospek menyebut sendiri | Aman, dan angka yang ditanya semuanya terpakai |

Saranku **c**. Sekarang slide 25 memakai angka generik "4-6jt/orang" untuk semua klien; menanyakan
`biaya_admin_bulanan` membuat slide itu memakai angka mereka sendiri — jauh lebih menusuk daripada
rentang umum.

---

## Rekomendasi rute build

Rakit ulang di **HTML + CSS paged media**, render lewat Chrome headless yang sudah terpasang.

- 16 slide tetap: tulis sekali, tidak pernah disentuh lagi
- 9 slide variabel teks: substitusi placeholder langsung dari baris REQUESTS
- 5 slide mockup: LLM menyusun percakapannya dari `kutipan_asli` + `pertanyaan_tersering` +
  `aksi_utama`, dirender jadi gelembung chat HTML — bukan screenshot tempel
- 3 slide kondisional: aturan sertakan/buang berdasarkan `fitur_diminati` dan jumlah `pain_points`

**Gerbang wajib:** jangan pernah render kalau field yang dibutuhkan sebuah slide kosong — lewati
slide itu atau hentikan generate. Angka yang tidak diketahui tidak boleh ditebak.
