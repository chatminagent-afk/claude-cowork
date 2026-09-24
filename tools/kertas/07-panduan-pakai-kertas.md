# Panduan Kertas — dari nol sampai jalan di HP

Ditulis untuk orang yang belum pernah membuka Google Cloud Console seumur hidup. Tidak ada istilah teknis yang dibiarkan tanpa penjelasan.

---

## Baca dua hal ini dulu

### 1. Kertas jalan penuh TANPA akun Google

Ini penting dan sering disalahpahami. Kertas **bukan** aplikasi yang mogok kalau tidak login.

Tanpa menyambungkan Google sama sekali, kamu sudah bisa:

- menulis catatan, checklist, blok kode, semuanya
- membuat tugas dengan tanggal dan jam
- mencari isi catatan
- memakai mode gelap
- menyimpan semuanya permanen di HP — tutup app, matikan HP, besok masih ada

Menyambungkan Google **hanya** dibutuhkan untuk dua hal:

| Kebutuhan | Perlu Google? |
|---|---|
| Menulis dan menyimpan di satu HP | ❌ Tidak |
| Membaca catatan yang sama di HP lain / laptop | ✅ Ya |
| Punya cadangan otomatis kalau HP hilang atau rusak | ✅ Ya |
| Membuka catatan lewat Google Docs di komputer | ✅ Ya |
| Pengingat yang bunyi walau Kertas tertutup | ✅ Ya |

Jadi kalau kamu cuma butuh app catatan di satu HP: **kerjakan Langkah 1 dan 2, lalu berhenti.** Selesai dalam 10 menit. Langkah 3 dan seterusnya boleh dikerjakan kapan-kapan, bahkan setahun lagi — catatan yang sudah kamu tulis akan ikut naik ke Drive saat itu juga.

### 2. Penyiapan Google makan waktu ±15 menit, tapi privasimu justru lebih aman

Jujur saja: menyambungkan Google butuh sekitar 15 menit menyiapkan izin, dan itu terasa merepotkan dibanding app biasa yang tinggal tekan "Login dengan Google".

Kenapa begitu, dan kenapa justru itu yang bagus:

App catatan biasa terasa mudah karena **perusahaan pembuatnya** yang menyiapkan izin, sekali, untuk semua orang. Konsekuensinya, perusahaan itulah yang memegang kunci ke Drive setiap penggunanya, dan catatanmu lewat server mereka.

Di Kertas, **kamu sendiri yang memegang kunci itu.** Tidak ada server Kertas — HP-mu bicara langsung ke Google, tidak ada perantara. Yang kamu kerjakan 15 menit itu adalah membuatkan izin atas namamu sendiri.

Tambahan penting: izin yang diminta namanya `drive.file`, artinya Kertas **hanya bisa melihat file yang dibuatnya sendiri**. Foto, dokumen kerja, dan semua isi Drive-mu yang lain benar-benar tidak terlihat olehnya. Ini bukan janji — memang begitu batasan teknisnya dari Google.

Dan 15 menit itu **cuma sekali seumur hidup**. Setelah selesai, HP kedua cukup buka satu tautan.

---

# LANGKAH 1 — Taruh Kertas di internet

**Waktu: 5 menit · Butuh: komputer atau HP, akun GitHub gratis**

Kertas berbentuk berkas web. Supaya bisa dipasang di HP dan bisa login ke Google, ia harus punya alamat `https://` sendiri. Kita pakai GitHub Pages karena gratis dan permanen.

### 1.1 Siapkan berkasnya

Unggah **seluruh isi folder `pwa/`** — 10 berkas, semuanya sudah ada:

```
index.html                ← seluruh aplikasi ada di sini
sw.js                     ← supaya app tetap jalan tanpa sinyal
manifest.json             ← supaya bisa dipasang ke layar utama
manifest.webmanifest      ← cadangan dari berkas di atas
icon.svg                  ← ikon versi vektor, dipakai tab browser
icon-192.png              ← ikon app
icon-512.png              ← ikon app ukuran besar
icon-maskable-192.png     ← ikon untuk Android, yang dipotong bulat
icon-maskable-512.png     ← sama, ukuran besar
apple-touch-icon.png      ← ikon untuk layar utama iPhone
```

⚠️ **Semuanya harus terunggah dan harus sejajar** — bukan di dalam folder. Kalau satu saja tertinggal, app tetap bisa dibuka di browser tapi **tidak bisa dipasang ke layar utama**. Tab Sync → **Periksa kenapa belum bisa dipasang** akan menyebutkan persis berkas mana yang hilang.

### 1.2 Buat akun dan gudang berkas

1. Buka [github.com](https://github.com) → daftar kalau belum punya (gratis).
2. Setelah masuk, klik tanda **+** di kanan atas → **New repository**.
3. Isi **Repository name** dengan: `kertas`
4. Pilih **Public**. *(Jangan khawatir: yang publik hanya program aplikasinya, bukan catatanmu. Catatanmu tersimpan di HP dan Drive pribadimu, tidak pernah masuk ke sini.)*
5. Klik **Create repository**.

### 1.3 Unggah berkasnya

1. Di halaman yang muncul, klik **uploading an existing file**.
2. Seret kelima berkas tadi ke kotak yang tersedia. Pastikan **kelimanya** masuk.
3. Gulir ke bawah, klik **Commit changes**.

### 1.4 Nyalakan alamat webnya

1. Klik tab **Settings** (di bagian atas halaman repo).
2. Di menu kiri, klik **Pages**.
3. Bagian **Source**: pilih **Deploy from a branch**.
4. Bagian **Branch**: pilih `main`, folder `/ (root)`. Klik **Save**.
5. Tunggu 1–2 menit, lalu segarkan halaman itu.

Di atas akan muncul alamatmu, bentuknya:

```
https://namamu.github.io/kertas/
```

**Catat alamat ini.** Nanti dipakai dua kali.

### ✅ Cek sebelum lanjut

Buka alamat itu di browser. Kertas harus muncul, dan ada tulisan **"Belum tersambung ke Google"** di atas. Itu **normal dan benar** — memang belum kita sambungkan.

Kalau yang muncul halaman kosong atau tulisan "404": tunggu 2 menit lagi, GitHub kadang butuh waktu. Kalau tetap, periksa apakah kelima berkas benar-benar terunggah dan `index.html` ada di lapisan paling luar (bukan di dalam folder).

---

# LANGKAH 2 — Pasang di HP

**Waktu: 2 menit**

### Kalau HP-mu Android

1. Buka alamat tadi di **Chrome**.
2. Ketuk menu titik tiga di kanan atas.
3. Pilih **Install app** / **Pasang aplikasi**.
4. Konfirmasi.

Kertas juga menyediakan tombolnya sendiri: tab **Sync** → **Pasang Kertas di layar utama**.

> **Kalau pilihan "Install app" tidak muncul**, jangan tebak-tebak: tab **Sync** → **Periksa kenapa belum bisa dipasang**. Kertas akan memeriksa satu per satu (alamat https, service worker, manifest, ikon) dan menyebutkan persis apa yang kurang beserta cara membetulkannya.
>
> Penyebab paling sering: ada berkas yang tertinggal saat mengunggah, atau alamatnya masih `http://` bukan `https://`.

⚠️ **"Add to Home screen" ≠ "Install app".** Kalau Chrome cuma menawarkan *Tambahkan ke layar utama*, yang terpasang hanyalah pintasan browser biasa — masih ada bilah alamat di atas. Kalau ini yang terjadi, berarti ada syarat yang belum terpenuhi; jalankan pemeriksaan di atas.

Sekarang Kertas punya ikon sendiri dan terbuka layar penuh seperti app biasa. **Bonus:** tekan-lama ikonnya, muncul pintasan *Catatan baru* dan *Tugas baru*.

### Kalau HP-mu iPhone

⚠️ **Wajib pakai Safari.** Chrome di iPhone tidak bisa memasang app.

1. Buka alamat tadi di **Safari**.
2. Ketuk tombol **Bagikan** (kotak dengan panah ke atas, di bawah layar).
3. Gulir ke bawah, pilih **Add to Home Screen** / **Tambahkan ke Layar Utama**.
4. Ketuk **Add**.

**Dua hal yang paling sering bikin gagal di iPhone:**

- **Chrome di iPhone tidak bisa memasang app.** Kelihatannya browser biasa, tapi Apple tidak memberi kemampuan itu ke browser selain Safari. Kalau kamu terlanjur membuka lewat Chrome, Kertas akan memberi tahu dan menyediakan tombol **Salin alamat app** — tempel di Safari, ulangi.
- **Pilihan "Add to Home Screen" tidak muncul di mode Penjelajahan Pribadi.** Keluar dari mode itu dulu.

### ✅ Cek sebelum lanjut

Buka Kertas **lewat ikon barunya**, bukan lewat browser. Tulis satu catatan, tutup app sepenuhnya, buka lagi. Catatannya harus masih ada.

## 🎉 Kalau kamu cuma butuh app catatan di satu HP, kamu sudah selesai

Semua fitur menulis sudah aktif. Lompat ke bagian **[Cara memakai Kertas sehari-hari](#cara-memakai-kertas-sehari-hari)** di bawah.

Lanjutkan ke Langkah 3 hanya kalau kamu mau catatanmu bisa dibuka dari HP lain atau laptop, dan punya cadangan otomatis.

---

# LANGKAH 3 — Buat izin Google

**Waktu: ±15 menit · Sekali seumur hidup**

Di sini kita membuatkan Kertas sebuah "kartu izin" atas namamu, supaya ia boleh menyimpan ke Drive-mu. Lakukan di **komputer** kalau ada — jauh lebih nyaman daripada di HP.

> **Sebelum mulai:** Kertas punya penuntun bawaan. Buka Kertas → tab **Sync** (ikon jam di kanan bawah) → **Buka panduan penyiapan**. Di sana ada tombol yang langsung membuka halaman Google yang tepat, plus alamat app-mu yang tinggal disalin. Ikuti sambil membaca panduan ini.

### 3.1 Buat "proyek" di Google

1. Buka [console.cloud.google.com](https://console.cloud.google.com). Masuk dengan akun Google yang catatanmu mau disimpan di situ.
2. Di bagian atas ada tombol pemilih proyek (tulisannya mungkin *Select a project*). Klik → **New project**.
3. **Project name**: ketik `kertas`. Klik **Create**.
4. Tunggu beberapa detik, lalu **pastikan proyek `kertas` yang terpilih** di pemilih atas itu. Ini sering terlewat dan bikin langkah berikutnya salah tempat.

*"Proyek" di sini cuma wadah pengaturan. Tidak ada biaya, tidak diminta kartu kredit.*

### 3.2 Nyalakan Google Drive API

1. Menu kiri (garis tiga) → **APIs & Services** → **Library**.
2. Ketik `Drive` di kotak pencarian.
3. Klik **Google Drive API** → klik tombol biru **Enable**.

*Ini seperti menyalakan sakelar: memberi tahu Google bahwa proyekmu boleh berbicara dengan Drive.*

> **Lebih enak dikerjakan sambil dituntun.** Buka Kertas → tab **Sync** → **Buka panduan penyiapan**. Isinya tujuh langkah yang sama persis dengan di bawah ini, tapi tiap langkah punya tombol yang langsung membuka halaman Google-nya, alamat app-mu sudah tertulis siap salin, dan nomor langkahnya bisa diketuk untuk ditandai selesai. Bagian di bawah ini gunanya kalau kamu lebih suka membaca dulu sebelum menekan apa pun.

### 3.3 Daftarkan aplikasinya (Google Auth Platform)

Ini halaman yang nanti muncul saat kamu menekan tombol login.

1. Menu kiri → **Google Auth Platform** → **Overview**. Tekan **Get started**.
   *(Kalau menu kirinya sudah menampilkan Branding / Audience / Clients / Data Access, berarti bagian ini sudah pernah selesai — lompat ke 3.4.)*
2. **App Information** — App name: `Kertas`. User support email: pilih emailmu. **Next**
3. **Audience** — pilih **External**. **Next**
4. **Contact Information** — emailmu lagi. **Next**
5. **Finish** — centang persetujuannya, **Continue**, lalu **CREATE**.

### 3.4 Tambahkan izin `drive.file`

1. Menu kiri → **Data Access**. Klik **ADD OR REMOVE SCOPES** — panel geser muncul dari kanan.
2. Di kotak **Filter** ketik `drive.file`. Centang baris yang kolom Scope-nya persis berbunyi:
   ```
   .../auth/drive.file
   ```
3. Klik **UPDATE** di bawah panel, lalu **SAVE** di halaman utamanya.

   **Dua-duanya harus ditekan.** Kalau cuma UPDATE, izinnya tidak tersimpan dan nanti loginnya ditolak.

⚠️ **Jangan mencentang yang lain.** Ada pilihan bernama `.../auth/drive` tanpa `.file` — itu akses ke SELURUH Drive-mu. Kertas tidak membutuhkannya, dan mencentangnya justru membuka pintu yang tidak perlu.

### 3.5 Tekan Publish — jangan sampai terlewat

Menu kiri → **Audience**. Di bagian **Publishing status** masih tertulis *Testing*. Tekan **PUBLISH APP**, lalu **CONFIRM**.

**Kenapa ini penting:** selama statusnya masih *Testing*, izin yang kamu berikan **hangus setiap 7 hari** dan kamu harus login ulang tiap minggu. Menekan Publish menghilangkan masalah itu.

**Apakah Publish berarti app-ku dipakai orang lain?** Tidak. Alamatnya cuma kamu yang punya. "Publish" di sini hanya status internal Google. Dan karena izin yang kamu minta tergolong ringan (`drive.file`), tidak ada proses pemeriksaan apa pun — langsung jadi.

### 3.6 Buat Client ID

Ini "kartu izin" yang tadi disebut.

1. Menu kiri → **Clients**. Klik **CREATE CLIENT**.
2. **Application type**: pilih **Web application**. Bukan Android, bukan Desktop.
3. **Name**: `Kertas`
4. Cari bagian **Authorized JavaScript origins** → klik **+ ADD URI**.
5. Tempel alamat app-mu, **tapi domainnya saja**:

   ✅ Benar: `https://namamu.github.io`
   ❌ Salah: `https://namamu.github.io/kertas/`
   ❌ Salah: `https://namamu.github.io/`

   **Ini penyebab kegagalan nomor satu.** Domain saja — tanpa nama folder, tanpa garis miring di ujung.

   *Cara paling aman: buka Kertas → tab Sync → Buka panduan penyiapan → tombol **Salin** di langkah 6. Alamatnya sudah dalam bentuk yang benar, tinggal tempel.*

6. Bagian **Authorized redirect URIs** biarkan **kosong**.
7. Klik **CREATE**.

Muncul kotak berisi **Client ID**, bentuknya seperti:

```
812345678901-a1b2c3d4e5f6g7.apps.googleusercontent.com
```

Salin. Kalau kotaknya terlanjur ditutup, Client ID tetap bisa dilihat lagi di daftar **Credentials**.

> **Apakah Client ID rahasia?** Bukan. Ia memang dirancang untuk terlihat publik — fungsinya cuma menandai "app mana yang minta izin". Yang rahasia namanya *client secret*, dan Kertas sama sekali tidak memakainya. Jadi aman ditempel di HP.

---

# LANGKAH 4 — Sambungkan

**Waktu: 1 menit**

1. Buka Kertas di HP → tab **Sync** → **Buka panduan penyiapan**.
2. Gulir ke langkah 4, tempel **Client ID** di kotaknya.
3. Tulisan di bawahnya berubah hijau: *"Formatnya benar."* Kalau masih merah, berarti ada bagian yang terpotong saat menyalin — ulangi.
4. Ketuk tombol putih **Sambungkan dengan Google**.
5. Pilih akun Google-mu → **Allow** / **Izinkan**.

Kertas otomatis membuat folder `Kertas` dan `Kertas/Notes` di Drive-mu.

---

# LANGKAH 5 — Pastikan benar-benar jalan

**Waktu: 5 menit. Jangan dilewati** — lebih baik ketahuan sekarang daripada saat kamu sudah punya 200 catatan.

### Tes 1 — catatan sampai ke Drive

1. Buat satu catatan, tulis apa saja.
2. Tunggu 5 detik. Tulisan di kanan atas berubah jadi **Tersinkron**.
3. Tab **Sync** → ketuk **Buka folder Kertas di Drive →**.
4. Catatanmu ada di sana sebagai **Google Doc asli**. Buka — isinya terbaca rapi.

### Tes 2 — perubahan dari laptop turun ke HP

1. Edit dokumen itu dari Google Docs di komputer, simpan.
2. Kembali ke Kertas di HP, tutup lalu buka lagi.
3. Perubahannya ikut turun.

### Tes 3 — offline benar-benar aman

1. Tab **Sync** → nyalakan **Mode offline (uji coba)**.
2. Tulis dua catatan baru dan centang satu tugas.
3. Spanduk kuning muncul: *"3 perubahan tersimpan di HP"*.
4. **Tutup app sepenuhnya**, buka lagi. Angkanya masih 3 — tidak ada yang hilang.
5. Matikan sakelarnya. Semua naik, spanduk hilang.

### Tes 4 — pemeriksaan bawaan

Tab **Sync** → **Jalankan tes internal**. Harus muncul **29/29 lolos**. Kalau ada yang merah, ada yang tidak beres dengan berkasnya — unggah ulang `index.html`.

---

# HP kedua — tidak perlu mengulang apa pun

Kamu **tidak** perlu mengerjakan Langkah 3 lagi. Pilih salah satu:

### Cara cepat — tautan penyiapan

1. Di HP yang sudah jalan: tab **Sync** → **Salin tautan penyiapan untuk HP lain**.
2. Kirim tautan itu ke HP satunya (WhatsApp ke diri sendiri juga bisa).
3. Buka di HP kedua → pasang ke layar utama (Langkah 2) → ketuk **Sambungkan dengan Google**.

Client ID-nya sudah terisi otomatis.

### Cara permanen — tanam di berkasnya

Buka `index.html`, cari baris di dekat awal (sekitar baris 710) — atau cari kata `CONFIG`:

```js
const CONFIG={ clientId:"" };
```

Isi dengan Client ID-mu:

```js
const CONFIG={ clientId:"812345678901-a1b2c3d4e5f6g7.apps.googleusercontent.com" };
```

Unggah ulang ke GitHub. Setelah ini layar penyiapan **tidak pernah muncul lagi** di perangkat mana pun — yang tampil cuma tombol **Sambungkan dengan Google**, persis app biasa.

---

# Cara memakai Kertas sehari-hari

## Menulis catatan

Setiap baris adalah blok tersendiri. **Kamu tidak perlu menghafal apa pun — ketik saja awalannya:**

| Ketik di awal baris | Langsung berubah jadi |
|---|---|
| `[] ` | ☐ Checklist yang bisa dicentang |
| `- ` | • Poin |
| `1. ` | Daftar bernomor, lanjut sendiri 2, 3, 4… |
| `## ` | Judul |
| `> ` | Kutipan |
| ` ``` ` | Blok kode (huruf mesin tik, autocorrect mati, ada tombol salin) |
| `---` | Garis pemisah |

Semua itu juga ada sebagai tombol di bawah keyboard, kalau lebih suka menekan.

**Yang bikin terasa alami:**

- **Enter** melanjutkan daftar. **Enter dua kali** keluar dari daftar.
- **Hapus** (backspace) di awal baris mengembalikan ke teks biasa dulu, baru kalau ditekan lagi menggabung ke atas. Tidak ada yang hilang gara-gara salah pencet.
- Di blok kode, Enter menambah baris seperti mestinya. Dua Enter di ujung untuk keluar.

## Section catatan

Chip di atas daftar catatan — **Semua / BCA / Klien / Personal** — adalah section. Bawaannya tiga, tapi jumlahnya tidak dikunci.

**Menambah:** tab Catatan → chip putus-putus **+ Section** di ujung kanan → ketik namanya → **Tambah section**. Maksimal 20 huruf. Kertas langsung pindah ke section baru itu, jadi catatan berikutnya yang kamu buat masuk ke sana.

**Memindahkan catatan:** buka catatannya, ketuk **tag hijau** di bawah judul (atau ikon folder di kanan atas) → pilih section tujuannya.

**Menghapus section:** di lembar yang sama, tekan **Hapus** di baris section-nya. Catatannya **tidak ikut terhapus** — semuanya dipindahkan ke section pertama yang tersisa, dan perpindahan itu ikut naik ke Drive. Section terakhir tidak bisa dihapus.

Section-nya sekarang **ikut tersinkron**. Kalau kamu bikin section "Riset" di HP, HP keduamu akan punya chip yang sama begitu selesai sinkron. Penandanya disimpan sebagai properti berkas di Drive, bukan diselipkan ke dalam isi catatan — jadi kalau catatan itu kamu buka langsung di Google Docs, tidak ada baris aneh yang ikut kelihatan.

> **Catatan:** section cuma pengelompokan di dalam Kertas. Di Drive semua catatan tetap berada di satu folder `Kertas/Notes`. Ini disengaja — memindah-mindahkan berkas antar folder Drive akan membuat sinkronisasi jauh lebih rapuh tanpa manfaat yang sepadan.

Tiap thumbnail catatan sekarang menampilkan **tag section**-nya di baris paling depan, jadi saat kamu sedang di chip **Semua** kamu tetap tahu tiap catatan berasal dari mana.

## Tugas dan pengingat

Ketuk tugas mana pun untuk mengatur **tanggal, jam, pengingat, daftar, prioritas, dan catatan tambahan**.

### Mencentang tugas

Ketuk kotaknya. Yang terjadi berurutan, persis seperti Google Tasks:

1. Kotaknya terisi hijau dan tanda centangnya **menggambar dirinya sendiri**
2. Judulnya **tercoret** dari kiri ke kanan
3. Baru setelah itu barisnya menyusut dan **pindah ke bagian Selesai** di bawah daftar

Jedanya disengaja. Kalau tugasnya langsung hilang begitu ditekan, kamu tidak pernah yakin tekanannya masuk atau kamu salah pencet baris lain.

**Salah centang?** Ketuk lagi kotaknya sebelum jedanya habis — baris itu tidak jadi pindah ke mana-mana. Kalau sudah terlanjur pindah, ketuk kotaknya di bagian Selesai dan ia naik lagi ke daftar aktif.

Bagian **Selesai** bisa dilipat lewat tanda panah di judulnya, dan pilihan lipat/buka itu diingat. Di tab **Hari ini** yang ditampilkan hanya yang selesai hari itu; di tab **Tugas** semuanya. Kalau sudah lebih dari 25, yang lama tidak ditampilkan lagi tapi tetap tersimpan di sheet `Kertas Tasks`.

Soal pengingat, ini harus disampaikan apa adanya: **browser tidak bisa membunyikan alarm saat app-nya tertutup.** Itu batasan semua aplikasi web, bukan kekurangan Kertas. Jadi ada dua lapis:

| Lapis | Bunyinya kapan |
|---|---|
| Notifikasi HP | Selama Kertas terbuka |
| **Google Calendar** | **Selalu — walau Kertas tertutup dan HP di saku** |

Lapis kedua itu jawabannya. Nyalakan **Kirim pengingat ke Google Calendar** di tab Sync. Tugas berpengingat akan muncul sebagai acara di Kalender, dan yang membunyikan adalah HP-mu sendiri lewat app Kalender bawaan — sama andalnya dengan alarm biasa.

Fitur ini butuh izin tambahan (`calendar.events`) dan menyalakan **Google Calendar API** di Cloud Console, dengan cara yang sama seperti Langkah 3.2.

## Mode gelap

Tombolnya ada di **kanan atas**, di antara pil status sinkron dan ikon gerigi — bukan di dalam pengaturan. Satu ketukan, langsung berganti, dari layar mana pun.

Ikonnya menunjukkan ke mana ia akan pergi, bukan di mana ia sedang berada: **bulan** berarti "tekan untuk gelap", **matahari** berarti "tekan untuk terang".

Sebelum kamu pernah menekannya, Kertas ikut pengaturan HP — termasuk kalau HP-mu terjadwal gelap saat malam. Begitu ditekan sekali, pilihanmu yang dipakai dan tidak ikut HP lagi. Mau balik ikut HP: tab **Sync** → bagian **Tampilan** → **Ikut pengaturan HP lagi**.

Mode gelapnya bukan sekadar warna dibalik: hijau khas Kertas dicerahkan supaya tetap terbaca, dan setiap tingkat permukaan dibedakan. Kalender dan pemilih jam bawaan HP ikut menggelap.

## Pindah HP tanpa Google

Kalau kamu memilih tidak menyambungkan Google sama sekali, catatanmu hidup di satu HP saja. Untuk memindahkannya, ada jalur berkas:

**Di HP lama:** tab Sync → **Unduh cadangan (.json)**. Satu berkas berisi seluruh catatan, tugas, daftar section, dan Client ID-mu.

**Kirim berkasnya** ke HP baru — WhatsApp ke diri sendiri, email, kabel, bebas.

**Di HP baru:** tab Sync → **Pulihkan dari cadangan (.json)** → pilih berkasnya.

Sebelum apa pun berubah, muncul pratinjau yang menyebutkan **berapa yang baru, berapa yang menggantikan versi lebih lama, dan berapa yang dilewati**. Baru setelah itu ada dua pilihan:

| Pilihan | Artinya |
|---|---|
| **Gabungkan** | Tidak membuang apa pun. Yang lebih baru menang; kalau tanggalnya seri, **yang sudah ada di HP ini yang dipertahankan** — jadi mengimpor cadangan lama tidak akan memundurkan catatan yang baru saja kamu ketik |
| **Ganti semua** | Buang isi HP ini, pakai isi cadangan. Butuh konfirmasi kedua. Berkas di Drive tidak ikut terhapus |

Untuk pindah HP, **Gabungkan** yang kamu mau — nyaris selalu.

Kalau kamu memang memakai Google, cara ini tidak perlu: pasang app di HP baru, tekan Sambungkan, semuanya turun sendiri dari Drive. Cadangan .json gunanya untuk yang offline, atau sebagai jaring pengaman sebelum melakukan sesuatu yang berisiko.

> Berkas cadangannya berisi Client ID-mu supaya HP baru tidak perlu mengulang urusan Cloud Console. Client ID bukan rahasia — tapi isi catatanmu iya, jadi berkas ini tetap perlakukan seperti isi HP-mu sendiri.

## Kalau sedang tanpa sinyal

Tidak ada yang perlu kamu lakukan. Tulis seperti biasa. Spanduk kuning akan menyebutkan berapa perubahan yang menunggu, dan semuanya naik sendiri begitu ada koneksi — bahkan kalau app-nya sempat kamu tutup.

Kalau sebuah catatan ternyata juga berubah di tempat lain selagi kamu offline, Kertas **tidak menimpanya diam-diam**. Muncul pilihan, dan pilihan bawaannya menyimpan dua-duanya.

---

# Kalau macet

| Yang muncul di layar | Artinya | Yang harus dilakukan |
|---|---|---|
| `Error 400: origin_mismatch` | Alamat di Cloud Console tidak sama persis | Kembali ke **Langkah 3.6 poin 5**. Domain saja, tanpa folder, tanpa garis miring di ujung. Tunggu 5 menit setelah menyimpan — Google butuh waktu. |
| `Error 401: invalid_client` | Client ID terpotong saat ditempel, atau tipenya bukan Web application | Ulangi **Langkah 3.6**, lalu tempel ulang Client ID-nya utuh. |
| Jendela login langsung tertutup | Popup diblokir | Tekan tombol **Sambungkan** secara langsung. Di iPhone: Settings → Safari → matikan *Block Pop-ups*. |
| Harus login ulang tiap minggu | Layar persetujuan masih *Testing* | Kembali ke **Langkah 3.5** dan tekan **PUBLISH APP**. |
| "Google hasn't verified this app" | **Wajar, bukan error.** App ini memang cuma milikmu dan tidak pernah didaftarkan untuk publik | Tekan **Advanced** di kiri bawah → **Go to Kertas (unsafe)** → centang izin Drive → **Continue**. Muncul sekali saja per perangkat. |
| `Access blocked` / app tidak dikenal | Izin `drive.file` belum tersimpan, atau Publish terlewat | Cek **Langkah 3.4** (harus sampai ditekan SAVE) dan **Langkah 3.5**. |
| `HTTP 403 ... has not been used` | Drive API belum dinyalakan | Ulangi **Langkah 3.2**. |
| Tombol Sambungkan tidak bisa ditekan | Client ID belum lengkap | Salin ulang seluruhnya, sampai `.apps.googleusercontent.com`. |
| Sudah unggah berkas baru tapi app lama terus | Versi lama masih tersimpan di HP | Tutup app, buka lagi. Kalau bengal: tab Sync → **Hapus data lokal**. Data di Drive tidak tersentuh. |
| App kosong di HP baru | Wajar — data tersimpan per perangkat | Sambungkan Google, tunggu sinkron. Semua turun dari Drive. |
| Tidak ada pilihan **Install app** di Chrome | Ada syarat pemasangan yang belum terpenuhi | Tab Sync → **Periksa kenapa belum bisa dipasang**. Ikuti perbaikan yang disebutkan. |
| Di iPhone tidak ada **Add to Home Screen** | Bukan Safari, atau sedang mode Pribadi | Buka di Safari, dan keluar dari Penjelajahan Pribadi. |
| Terpasang tapi masih ada bilah alamat | Yang terpasang cuma pintasan, bukan app | Hapus ikonnya, jalankan pemeriksaan di tab Sync, betulkan, lalu pasang ulang. |
| Spanduk merah "Penyimpanan HP penuh" | Catatan lokal sudah terlalu banyak | Ketuk **Sinkronkan**, pastikan semua sudah di Drive, lalu hapus catatan lama dari app. |

---

# Pertanyaan yang sering muncul

**Apakah catatanku bisa dibaca orang lain karena repo GitHub-nya publik?**
Tidak. Yang ada di GitHub cuma program aplikasinya — kerangka kosong. Catatanmu tersimpan di HP dan di Drive pribadimu, tidak pernah menyentuh GitHub.

**Apakah pembuat Kertas bisa melihat catatanku?**
Tidak ada server Kertas sama sekali. HP-mu bicara langsung ke Google. Tidak ada tempat lain yang dilewati datamu.

**Kenapa penyiapannya tidak bisa otomatis saja?**
Untuk membuat izin Google secara otomatis, dibutuhkan izin Google yang sudah ada lebih dulu — ayam dan telur. Kalau sebuah halaman web bisa membuatkan izin atas namamu, aplikasi jahat mana pun juga bisa. Batasan ini justru yang melindungimu.

**Kalau saya berhenti pakai Kertas, catatan saya bagaimana?**
Tetap ada, sebagai Google Docs biasa di folder `Kertas` di Drive-mu. Bisa dibuka, dibagikan, diunduh, tanpa Kertas sama sekali. Tidak ada yang terkunci.

**Bagaimana mencabut aksesnya?**
[myaccount.google.com/permissions](https://myaccount.google.com/permissions) → pilih Kertas → **Remove access**. Selesai.

**Ada biayanya?**
Tidak ada. GitHub Pages gratis, Google Cloud tidak menagih apa pun untuk pemakaian sebesar ini, dan tidak diminta kartu kredit.

**Bisa dipakai di komputer juga?**
Bisa — buka alamat yang sama di browser mana pun. Fitur lengkap, kecuali ikon di layar utama.

---

## Berkas lain di paket ini

| Berkas | Isinya |
|---|---|
| `pwa/index.html` | Seluruh aplikasi — tampilan, logika, dan tes internalnya jadi satu berkas |
| `pwa/sw.js` | Service worker: bikin app tetap terbuka saat offline |
| `pwa/manifest.json` | Keterangan app untuk layar utama HP |
| `pwa/icon*.png`, `pwa/icon.svg` | Ikon app — lihat bagian di bawah |
| `make-icons.py` | Skrip yang membuat semua ikon itu, kalau nanti mau diubah |
| `08-bikin-apk-android.md` | Cara membungkus Kertas jadi APK Android, supaya pengingat tetap bunyi saat app tertutup |
| `capacitor.config.json`, `package.json` | Konfigurasi untuk pembungkusan APK di atas |

Tiga berkas terakhir tidak berpengaruh sama sekali kalau kamu cuma memakai versi PWA — abaikan saja.

## Ikon app

Ikonnya selembar kertas beresudut lipat dengan dua baris tulisan dan satu centang, di atas hijau pine — catatan dan tugas dalam satu gambar.

Ada dua bentuk, dan bedanya penting:

| Berkas | Dipakai siapa |
|---|---|
| `icon-192/512.png` | Browser desktop, daftar app, tab. Kertasnya digambar lebih besar |
| `icon-maskable-192/512.png` | **Android**, yang memotong tiap ikon jadi bulat atau squircle. Kertasnya sengaja dikecilkan supaya tidak ada bagian yang terpotong |
| `apple-touch-icon.png` | Layar utama iPhone (180×180) |
| `icon.svg` | Tab browser — versi vektor, tetap tajam di layar sebesar apa pun |

Kalau kamu memakai satu ikon untuk dua-duanya, hasilnya salah satu: entah terpotong di Android, atau kekecilan dan mengambang di tempat lain. Karena itu dibedakan.

**Mau ganti warna atau bentuknya?** Ubah `make-icons.py` di folder induk, lalu jalankan:

```bash
python make-icons.py
```

Butuh Pillow (`pip install Pillow`). Skripnya menggambar 4× lebih besar lalu mengecilkan, jadi tepinya halus, dan di akhir ia memeriksa sendiri apakah isi versi maskable masih muat di lingkaran aman 80%. Kalau kamu mengubah `icon.svg`, ubah juga skripnya supaya keduanya tidak berbeda.
