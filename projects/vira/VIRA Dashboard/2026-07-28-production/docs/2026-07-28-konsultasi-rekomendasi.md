# Konsultasi & Rekomendasi — VIRA Dashboard dan Sekitarnya

2026-07-28

Selama membangun dashboard, saya membaca lengkap `VIRA V4.json`,
`VIRA-PCR Main V1.3.json` beserta workflow pendukungnya, kedua spreadsheet
produksi, dan seluruh draft dashboard lama. Dokumen ini berisi temuan yang
**bukan bagian dari dashboard** tapi menurut saya kamu perlu tahu, plus saran
arah ke depan.

Diurutkan dari yang paling perlu ditindak. Tidak ada satu pun file produksi yang
saya ubah.

---

## 🔴 T1 — Private key service account Google tersimpan plaintext di sheet CONFIG Persada

**Di mana.** `PCR_Database` → tab `CONFIG` → baris dengan key
`google service email` dan `google service private key`. Kolom `value` berisi
private key RSA lengkap dalam bentuk PEM.

**Kenapa serius.** Itu kunci yang sama dengan credential `Google Service Account
- Persada` di n8n. Siapa pun yang punya akses **baca** ke spreadsheet itu bisa
menyalin kuncinya dan mengautentikasi sebagai service account tersebut — termasuk
ke spreadsheet lain yang dibagikan ke akun itu. Spreadsheet ini kemungkinan besar
dibagikan ke beberapa orang tim Persada, dan sekali bocor tidak ada jejak siapa
yang mengambilnya.

**Yang perlu dilakukan.**
1. Hapus dua baris itu dari CONFIG.
2. **Rotate** key service account di Google Cloud (anggap yang lama sudah bocor —
   kunci itu sudah cukup lama berada di sheet yang dipakai banyak orang).
3. Simpan kunci baru hanya di credential store n8n, yang terenkripsi.
4. Cek apakah ada baris serupa di `The_Scholars_Database`.

Ini juga alasan dashboard **tidak pernah membaca tab CONFIG sama sekali** —
`qa/validate_workflow.py` menolak build kalau ada tenant yang mencantumkan
`CONFIG` di daftar tabnya. Kalau tidak, private key itu akan ikut terkirim ke
browser owner.

---

## 🔴 T2 — Kredensial Kirimi hardcoded di puluhan node, ikut terbawa setiap export

**Di mana.** VIRA V4: 8 node HTTP Request + workflow Error Notifier.
VIRA-PCR: 13 node. Semuanya mengirim `user_code`, `secret`, dan `device_id`
sebagai parameter body biasa — bukan lewat credential store n8n. Di Persada
nilainya dibaca dari sheet CONFIG saat runtime; di The Scholars ditulis langsung
di dalam node (`user_code: KM40LI0426`, `device_id: D-4ZV1F`, `secret: 4efe37…`).

**Kenapa penting.** Setiap kali kamu meng-export workflow JSON — untuk backup,
untuk dikirim ke saya, untuk dipindah instance — token kirim-WhatsApp penuh ikut
di dalamnya. Folder proyek ini sendiri sudah memuat beberapa salinan. Siapa pun
yang memegang file itu bisa mengirim WhatsApp atas nama nomor bisnis klien.

Ada komentar di kode `Parse Config` Persada yang menyebut *"Node teks (JSON body)
tetap pakai credential httpCustomAuth"* — itu **tidak sesuai kenyataan**, tidak
ada satu pun node yang memakai credential tersebut. Komentar yang menyesatkan
seperti ini berbahaya karena membuat orang berikutnya mengira sudah aman.

**Saran.** Pindahkan ke n8n credential (Header Auth / Custom Auth). Kalau terlalu
memakan waktu sekarang, minimal: jangan simpan export workflow di folder yang
tersinkron ke cloud, dan rotate secret Kirimi kalau pernah terkirim lewat chat.

---

## 🟠 T3 — Webhook bot terbuka tanpa autentikasi

`POST /wa-inbound` dan `POST /wa-inbound-pcr` tidak punya autentikasi apa pun.
Keamanannya bergantung sepenuhnya pada kerahasiaan path.

Siapa pun yang tahu URL-nya bisa menyuntik pesan palsu: membuat baris STATS
palsu, memicu balasan AI (yang berbiaya token Anthropic), atau memicu notifikasi
ke tim lapangan. Path-nya sendiri sudah tertulis di beberapa dokumen di folder ini.

**Saran.** Tambahkan header rahasia yang dikirim Kirimi dan diperiksa di node
pertama, atau minimal IP allowlist kalau Kirimi punya IP tetap. Prioritas di
bawah T1/T2 karena dampaknya gangguan, bukan pengambilalihan akun.

---

## 🟠 T4 — Dua workflow pendukung The Scholars tidak aktif

`VIRA - MSG_BUFFER Cleanup (harian 03:00 WIB)` dan `VIRA Error Notifier`
keduanya `active: false`.

- **Cleanup tidak aktif = MSG_BUFFER tumbuh selamanya.** Saat snapshot ada 34
  baris. Setiap `Read MSG_BUFFER` membaca seluruh tab, jadi tab yang membesar
  memperlambat setiap giliran percakapan — pelan-pelan, tanpa gejala jelas,
  sampai terasa lambat tanpa sebab.
- **Error Notifier** masih bisa terpanggil sebagai errorWorkflow meski inactive,
  tapi lebih baik dipastikan.

Bandingkan dengan Persada: ketiga workflow pendukungnya `active: true`. The
Scholars tertinggal di sini.

**Terkait:** node `IF (Whitelist)` di VIRA V4 dalam keadaan `disabled`, sehingga
filter 5 nomor itu tidak berlaku dan semua nomor diproses. Kalau itu memang
disengaja saat go-live, tidak apa-apa — tapi sebaiknya node matinya dihapus
supaya tidak ada yang mengira filter itu masih bekerja.

---

## 🟡 T5 — Tiga kolom Persada punya spasi di ujung nama, dan kodenya membaca tanpa spasi

Header di STATS `PCR_Database`: `pending_survey_tanggal `,
`pending_survey_jam `, `pending_survey_unit ` — ketiganya berakhir spasi.

Node `Update to STATS` **menulis** dengan nama yang benar (ikut spasinya), tapi
`Resolve User Row` dan `Cek_user_status` **membaca** `row['pending_survey_tanggal']`
tanpa spasi. Karena node Google Sheets n8n memakai header apa adanya sebagai key
JSON, pembacaan itu kemungkinan besar selalu `undefined`.

**Artinya fitur "pending survey lintas giliran" kemungkinan tidak pernah
bekerja** — data ditulis, tidak pernah dibaca balik. Perlu diverifikasi dengan
satu percakapan uji, tapi dari kode saja gejalanya jelas.

**Perbaikan.** Rapikan header di spreadsheet (hapus spasinya) **atau** ubah
pembacaan supaya toleran. Dashboard sendiri sudah dibuat toleran — fungsi
`vdRowGet` mencocokkan nama kolom setelah di-trim, jadi dashboard tetap membaca
kolom seperti ini dengan benar. Bot belum.

---

## 🟡 T6 — Kolom `EVENTS.ts` bercampur satuan

`Log EVENTS Delegated` menulis `Math.floor(Date.now()/1000)` (detik).
`Log Call Request` menulis `Date.now()` (milidetik). Ke kolom yang sama.

Akibatnya urutan waktu di tab EVENTS salah — semua baris `REQUEST_CALL` akan
selalu tampak "lebih baru" dari `DELEGATED` mana pun, karena angkanya 1000× lebih
besar. Dashboard menormalkannya (`vdEpochAuto` menebak dari besaran angka), tapi
itu tambalan; sumbernya sebaiknya diseragamkan ke milidetik.

---

## 🟡 T7 — Tidak ada metrik konversi yang jujur, dan itu disengaja

Kolom `gform_filled` di STATS The Scholars **tidak pernah ditulis oleh node mana
pun**. Nilainya kosong di seluruh 382 baris.

Draft dashboard lama menampilkan KPI "GForm Conversion" dari kolom ini —
angkanya **akan selalu 0%**. KPI yang selalu nol lebih buruk daripada tidak ada
KPI: owner akan menyimpulkan kampanyenya gagal total, padahal yang gagal adalah
pengukurannya.

Dashboard baru **tidak menampilkannya**. Yang ditampilkan adalah "GForm
Terkirim" (dari `gform_sent_ts`, yang memang ditulis) — jujur mengukur pengiriman,
bukan pengisian.

**Kalau kamu mau konversi sungguhan**, perlu sumber data submission form: Google
Form → Sheet respons → workflow yang mencocokkan nomor WA dan menulis
`gform_filled`. Itu pekerjaan tersendiri; bilang saja kalau mau dikerjakan.

Hal yang sama berlaku di Persada: `flag_survey` dan `survey_status` ditulis, jadi
funnel survey bisa diukur — dan memang ditampilkan.

---

## 🟡 T8 — Toggle global belum berfungsi (sesuai keputusanmu, ditunda)

`CONFIG.VIRA_STATUS` yang ditulis dashboard lama **tidak dibaca oleh satu node
pun** di VIRA V4 maupun VIRA-PCR. Tombolnya menyala, tapi bot tetap jalan.

Sesuai keputusanmu, tombol itu **saya hilangkan dari UI** — lebih baik tidak ada
tombol daripada ada tombol yang berbohong. Toggle per-user berfungsi penuh karena
`bot_mode` memang dibaca di tiga titik oleh kedua workflow.

Kalau nanti mau diadakan, yang dibutuhkan: satu node `Read CONFIG` + satu `IF
VIRA Active` di awal alur kedua workflow, plus baris `VIRA_STATUS` di CONFIG.
Bilang saja, saya buatkan patch-nya.

---

## ⚪ T9–T11 — Catatan kecil

**T9. `Counter` tidak akurat secara struktural.** Pola `baca → +1 → tulis` tanpa
penguncian; dua pesan bersamaan menghilangkan satu increment. Google Sheets tidak
punya transaksi, jadi tidak ada perbaikan yang bersih. Saran saya sama dengan
dokumen sesi 4 milikmu: **terima saja dan dokumentasikan**. Dashboard sudah
menandainya di tooltip KPI "Total Chat" sebagai perkiraan.

**T10. `Bootstrap Config` Persada menyuntik Sheet ID yang salah**
(`1dJWq7iq…`, sementara 23 node lain memakai `1pzGuRZ…`). Nilai itu tidak dibaca
siapa pun hari ini, jadi belum meledak — tapi ini ranjau untuk orang berikutnya.
Patch-nya sudah kamu siapkan di `2026-07-25-sesi2-kode-patch/`, tinggal dipasang.

**T11. Folder draft dashboard lama membingungkan.**
`VIRA-DASHBOARD/2026-07-07-patch-V4-compat/` mengklaim `index-LID-badge.html`
adalah "pengganti index.html", padahal arsitekturnya sudah divergen total (PIN +
Apps Script vs n8n + JSON). Kalau file itu di-deploy, dashboard justru **mundur**
ke versi tanpa tab CRM, Mock Interview, dan Insights.

Saran: arsipkan seluruh isi `VIRA-DASHBOARD/` yang lama ke `_arsip/` dan sisakan
`2026-07-28-production/` sebagai satu-satunya sumber. Saya tidak memindahkan
apa-apa — itu keputusanmu, dan aturanmu sendiri bilang konfirmasi dulu sebelum
memindahkan file.

---

## Arah ke depan

### Kuota Google Sheets adalah langit-langit yang sebenarnya

Dokumen sesi 4-mu sudah menghitungnya dengan benar: plafon keras 2 read/pesan
membuat batas teoretis ~30 pesan/menit, realistis ~12 giliran/menit setelah
optimasi. Dashboard tidak memperburuk ini (service account terpisah, cache 60
detik, tanpa polling), **tapi juga tidak menaikkannya**.

Kalau target Persada benar-benar di atas ~10.000 pesan/hari, migrasi STATS ke
Postgres/Supabase bukan pilihan tapi keharusan — dan kalau itu memang akan
dikerjakan, sebagian pekerjaan optimasi R1/R3/R4 akan terbuang. Pertanyaan
"berapa target traffic sebenarnya" sudah tiga kali muncul di dokumenmu dan belum
terjawab; itu satu-satunya angka yang menentukan urutan kerja berikutnya.

**Kabar baiknya untuk dashboard:** kalau STATS pindah ke Postgres, yang berubah
hanya node pembaca di dalam workflow API. Kontrak ke frontend tidak berubah sama
sekali, karena normalisasi sudah terpisah di `build-payload.js`.

### Yang menurut saya paling berharga ditambahkan berikutnya

1. **Notifikasi ke owner saat bot menyerahkan percakapan.** Saat AI mengeluarkan
   `[TALK_TO_SAM]` / `[TALK_TO_ADMIN]`, `bot_mode` langsung jadi OFF dan
   percakapan menunggu manusia. Kalau owner tidak sedang membuka dashboard, lead
   itu menganggur tanpa ada yang tahu. Notifikasi WhatsApp sudah ada di workflow;
   yang belum ada adalah cara melihat **berapa lama** sudah menunggu.
   Saran konkret: KPI "menunggu dibalas manusia > 1 jam" di dashboard.
2. **Kolom "terakhir dibalas manusia"** di direktori lead, supaya owner tahu mana
   yang sudah ditangani dan mana yang belum. Datanya belum ada — perlu satu kolom
   baru yang ditulis saat admin membalas.
3. **Ekspor CSV** dari direktori lead. Murah dibuat, dan owner biasanya ingin
   mengolah sendiri di Excel.
4. **Login dua akun per klien** (owner + staf) kalau nanti ada tim. Struktur
   `VIRA_USERS` sudah mendukungnya, tinggal ditambah entri.

### Satu hal yang saya sarankan JANGAN dilakukan

Jangan menambahkan auto-refresh berkala di dashboard. Godaannya besar (terasa
lebih "hidup"), tapi setiap polling memakan kuota Sheets yang sama dengan yang
dipakai bot untuk membalas customer. Tiga owner dengan tab terbuka dan polling
30 detik = beban tetap yang tidak menghasilkan apa-apa. Tombol Segarkan sudah
cukup, dan itu sebabnya ganti rentang 7/30/90 hari sengaja diproses di browser.

---

## Yang saya butuhkan darimu

1. **Keputusan T1** — kapan rotate service account Persada. Ini yang paling
   mendesak dan tidak bisa saya kerjakan sendiri.
2. **Konfirmasi T5** — apakah fitur pending survey memang terasa tidak jalan?
   Kalau iya, temuannya terkonfirmasi dan perbaikannya sederhana.
3. **Angka target traffic** untuk Persada — menentukan apakah migrasi database
   perlu dijadwalkan sekarang atau tahun depan.
4. **Izin untuk mengarsipkan** draft dashboard lama (T11).
