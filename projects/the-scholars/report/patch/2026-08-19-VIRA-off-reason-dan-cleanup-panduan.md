# VIRA — Pembeda OFF by SAM vs by VIRA + Cleanup STATS Berkala

**Tanggal:** 2026-08-19
**Pemicu:** Diskusi Sam–Steven 14 Agustus 2026 (nomor yang di-OFF perlu dibedakan; STATS perlu dibersihkan berkala)
**File baru:** `report/patch/2026-08-19-VIRA-STATS-cleanup-3bulan.json`
**Workflow utama:** TIDAK dibuatkan file baru — perubahannya cuma 1 field di 1 node, lebih hemat dikerjakan manual (lihat Bagian 2)

---

## Ringkasan keputusan

| Hal | Keputusan |
|---|---|
| Nilai `off_reason` | `SAM` (Sam yang matikan) / `VIRA` (VIRA matikan atas permintaan user) |
| Pencocokan | **Case-insensitive + trim** — `SAM`, `Sam`, `sam`, ` SAM ` semuanya aman |
| Interval cleanup | Tiap 3 bulan, 00:01 WIB (1 Jan / 1 Apr / 1 Jul / 1 Okt) |
| Yang dipertahankan | **Hanya** `off_reason = SAM` |
| Yang dihapus | Semua sisanya — termasuk `bot_mode = ON`, termasuk OFF tanpa label |
| Archive | Tidak ada (Sam konfirmasi tidak pernah pakai data STATS) |
| Notifikasi | WA ke Steven setelah cleanup selesai |

---

## Bagian 1 — Kolom yang harus ditambah di STATS

**Jawaban singkat: ya, cukup satu kolom `off_reason`.** Tidak perlu kolom timestamp atau kolom bantu lain.

Langkah:

1. Buka Google Sheet `The_Scholars_Database` → tab **STATS**.
2. Tambahkan kolom baru **di paling kanan** (setelah `last_reply_ts`, jadi kolom **X**). Nama header persis: `off_reason` — huruf kecil semua, tanpa spasi.
3. Pasang dropdown supaya Sam tidak bisa salah ketik: blok kolom X → **Data → Data validation** → *Dropdown* → isi dua opsi: `SAM` dan `VIRA`.

> **Kenapa ditaruh paling kanan:** node n8n memetakan kolom by nama, bukan posisi, jadi menaruhnya di tengah juga jalan. Tapi paling kanan menghindari risiko formula/range lain di sheet ikut bergeser.

---

## Bagian 2 — Perubahan di workflow utama VIRA (kerjakan manual, 1 field saja)

Ini bagian yang tidak perlu file JSON baru. Cukup **satu field di satu node**.

### Yang diubah: node `Update row in sheet`

Node ini satu-satunya yang jalan saat VIRA mematikan bot atas permintaan user (jalurnya: `Process All` → `IF Talk To Sam` → `Notify Talk to Sam` → `Update row in sheet`).

Buka node itu, di bagian **Values to Send**, tambahkan satu field:

| Column | Value |
|---|---|
| `off_reason` | `VIRA` |

Ketik literal `VIRA` — bukan expression, tidak pakai `{{ }}`.

Setelah ini, tiap kali VIRA mematikan bot sendiri, kolomnya otomatis terisi `VIRA`. Sisanya (yang Sam matikan manual) tinggal diisi `SAM` lewat dropdown.

### ⚠️ Yang JANGAN diubah: node `Update to STATS`

Node ini jalan di **setiap pesan** dan menulis `bot_mode`. **Jangan tambahkan `off_reason` ke node ini.**

Alasannya penting: node ini pakai mapping mode *defineBelow*, yang artinya kolom yang **tidak** didaftarkan **tidak ikut ditulis** — nilainya di sheet aman apa adanya. Kalau `off_reason` didaftarkan di sini, tiap pesan masuk akan menimpa label yang Sam ketik, dan cleanup berikutnya akan menghapus baris murid/parent dia.

**Jebakan yang harus kamu waspadai:** setelah kolom `off_reason` ditambah di sheet, saat kamu membuka node `Update to STATS` di editor n8n, n8n akan me-refresh daftar kolom dan **bisa otomatis menambahkan `off_reason` ke mapping dengan nilai kosong**. Kalau itu terjadi, hapus field-nya (ikon tempat sampah di sebelah kanan field), jangan dibiarkan kosong. Cek ini setiap kali kamu membuka node itu.

Aturan gampangnya: di seluruh workflow utama, `off_reason` **hanya** boleh muncul di node `Update row in sheet`.

### Kenapa cukup segitu

Sudah saya telusuri graph koneksinya: `Update to STATS` dan `Update row in sheet` dua-duanya berada **di belakang** gerbang `IF Bot Mode Active` (cabang true) dan `HITL Check`, plus satu gerbang ketiga `Cek_user_status` yang cek ulang setelah debounce 60 detik. Tidak ada jalur yang bisa menulis ke baris user yang `bot_mode`-nya sudah OFF. Jadi baris ber-label `SAM` tidak akan pernah disentuh workflow utama.

---

## Bagian 3 — Melabeli 384 baris yang sudah OFF sekarang

Ini bagian yang paling makan waktu, dan angkanya lebih besar dari perkiraan awal. Dari data STATS terakhir (`The_Scholars_Database.xlsx`, 664 baris):

| Kelompok | Jumlah | Artinya |
|---|---:|---|
| `bot_mode = OFF` total | **384** | semuanya perlu label |
| — tanpa jejak chat sama sekali | **179** | `Pesan Pertama`, `Counter`, `Nama`, `greeting_sent`, `last_reply_ts` semua kosong → nomor yang **diketik manual Sam**, VIRA belum pernah menyentuhnya → hampir pasti `SAM` |
| — ada jejak chat dengan VIRA | **205** | pernah ngobrol sama VIRA → perlu penilaian Sam |
| `bot_mode` bukan OFF | 280 | tidak perlu label, akan terhapus |

Yang 179 itu bisa diisi otomatis dengan tingkat keyakinan tinggi — kalau VIRA tidak pernah membalas, tidak pernah menyapa, dan tidak ada pesan pertama, satu-satunya cara baris itu ada di sheet adalah Sam mengetiknya sendiri.

**Cara mengisinya:**

1. Di kolom kosong sementara (misal kolom Z), baris 2, tempel formula ini lalu tarik ke bawah:

   ```
   =IF(EXACT(UPPER(TRIM(B2)),"OFF"), IF(AND(F2="",G2=""),"SAM","CEK"), "")
   ```

   (B = `bot_mode`, F = `Pesan Pertama`, G = `Counter`)

2. Blok kolom Z → Copy → klik kolom X (`off_reason`) → **Paste special → Values only**. Jangan paste formula-nya; kolom `off_reason` harus berisi teks statis, bukan rumus.
3. Hapus kolom Z.
4. Kirim ke Sam: minta dia sisir baris yang isinya `CEK` (205 baris, kolom `Nama` terisi jadi dia bisa mengenali) dan ganti jadi `SAM` atau `VIRA` lewat dropdown.

**Yang penting disampaikan ke Sam:** baris yang masih `CEK` atau kosong saat cron jalan **akan terhapus**. Deadline realistisnya **sebelum 1 Oktober 2026** (jadwal cron pertama). Masih ada ~6 minggu.

> Catatan terpisah yang mungkin menarik buatmu: 159 baris punya jejak chat lengkap **dan** ber-`bot_mode` OFF. Kalau sebagian besar itu hasil deteksi `[TALK_TO_SAM]`, artinya sekitar 24% user berakhir di-handover ke Sam. Angka itu terasa tinggi — mungkin layak dicek terpisah apakah deteksi talk-to-Sam terlalu longgar. Di luar scope perbaikan ini.

---

## Bagian 4 — Import workflow cleanup

**File:** `report/patch/2026-08-19-VIRA-STATS-cleanup-3bulan.json`
**Nama workflow:** `VIRA - STATS Cleanup (tiap 3 bulan, 00:01 WIB)`

Langkah:

1. n8n → **Import from File** → pilih file di atas. Workflow masuk dalam keadaan **non-aktif** (disengaja).
2. Cek kredensial Google Sheets ter-mapping (`Google Service Account thescholars`) di 3 node: `Read STATS (all)`, `Append SAM rows`, `Delete original block`. Import n8n kadang melepas binding.
3. **Buka node `Notify Steven`** → ganti nilai field `phone` dari `ISI_NOMOR_WA_STEVEN` jadi nomor WA-mu (format `62xxx`, tanpa `+`, tanpa spasi). Sengaja saya isi placeholder yang tidak valid supaya kalau kelupaan, notifikasinya gagal terang-terangan — bukan diam-diam terkirim ke nomor asing.
4. **Jangan diaktifkan dulu** sampai kolom `off_reason` sudah ada dan pelabelan Bagian 3 selesai.

### Uji sebelum aktivasi

Jalankan manual (**Execute Workflow**) dan cek hasilnya:

| Kondisi | Harapan |
|---|---|
| Kolom `off_reason` belum ada | Workflow **gagal dengan error** di node `Plan cleanup` dan **tidak menghapus apa pun**. Ini benar — guard-nya bekerja. |
| Kolom sudah ada + sudah dilabeli | Sisa baris di STATS = persis baris ber-`off_reason` SAM, rapi mulai baris 2 tanpa celah |
| Setelah selesai | Kamu terima WA berisi jumlah dipertahankan / dihapus |

Saran: sebelum eksekusi manual pertama, **duplikat dulu tab STATS** (klik kanan tab → Duplicate) sebagai jaring pengaman. Setelah hasilnya kamu verifikasi benar, tab duplikat boleh dihapus. Google Sheets juga punya **File → Version history** kalau perlu mundur.

### Cara kerja workflow

```
Every 3 months 00:01 WIB
  └→ Read STATS (all)
       └→ Plan cleanup ............ pisahkan baris SAM vs sisanya + guard
            └→ IF Ada Baris SAM
                 ├─ true  → Split kept rows → Append SAM rows ─┐
                 └─ false ────────────────────────────────────┤
                                                              ↓
                                                     Prepare delete
                                                       └→ Delete original block
                                                            └→ Notify Steven
```

**Kenapa salin dulu baru hapus, bukan sebaliknya.** Ini keputusan desain yang paling menentukan keamanan workflow ini. Baris SAM disalin ke bawah sheet dulu, baru blok baris lama di atasnya dihapus sekaligus. Konsekuensinya:

- Kalau **Append gagal** → belum ada yang dihapus → **nol kehilangan data**, tinggal jalankan ulang.
- Kalau **Delete gagal** → yang terjadi cuma baris duplikat → masih **nol kehilangan data**, tinggal dirapikan.

Kalau urutannya dibalik (hapus dulu, tulis ulang belakangan), satu kegagalan tulis = baris murid dan parent Sam hilang permanen. Karena itu urutan ini jangan diubah.

Hanya butuh **2 operasi tulis** ke Google Sheets, jadi jauh dari batas kuota API.

### Guard yang terpasang

| Guard | Perilaku |
|---|---|
| Kolom `off_reason` belum ada | Error, batal total — bukan "anggap semua non-SAM lalu hapus" |
| Kolom `No WA` tidak ada | Error, batal total (indikasi salah tab) |
| Sheet kosong / cuma header | Berhenti tanpa menghapus |
| Baris kosong nyempil di tengah | Ikut terhapus — rentang hapus dihitung dari nomor baris terbesar, bukan jumlah baris terbaca |
| Node Append gagal | Retry 3x, jeda 5 detik |
| Kirimi error saat notif | Workflow tetap dianggap sukses (cleanup-nya sudah selesai) |
| Workflow error | Diteruskan ke error workflow yang sudah ada (`ZKsINjA7ZC8c9yRHWp3ud`) |

---

## Hasil QA

**67 assertion, 0 gagal.** Skrip: `qa_cleanup.py`.

| Bagian | Cakupan |
|---|---|
| A. Struktur (30) | 9 node, semua terjangkau dari trigger, cron `1 0 1 */3 *`, timezone Asia/Jakarta, kredensial identik dengan workflow utama, **Append terbukti berada sebelum Delete**, Delete hanya punya 1 sumber inbound, kedua cabang IF bertemu di `Prepare delete`, nomor notif masih placeholder |
| B. Sintaks (8) | 3 node Code parse bersih, `row_number` dibuang dari salinan, normalisasi case-insensitive ada, `Prepare delete` mengembalikan tepat 1 item |
| C. Logika (13) | Sheet kosong, tab salah, kolom belum ada, 5 variasi ketikan SAM, VIRA/kosong/ON ikut terhapus, hitungan laporan, semua-SAM, tanpa-SAM, baris berlubang, nilai null |
| D. Simulasi (10) | Transformasi sheet penuh (append→delete): hasil akhir persis baris SAM, urutan terjaga, tidak ada yang hilang, tidak ada duplikat, **idempoten**, plus simulasi kegagalan Append dan Delete |
| E. Data asli (6) | Dijalankan atas 664 baris STATS sungguhan; guard terbukti menolak jalan selama kolom belum ada; pemisahan 179 / 205 terverifikasi konsisten |

### Batasan QA — yang BELUM diuji

Supaya jelas sampai mana jaminannya:

1. **Kode belum pernah dieksekusi sebagai JavaScript.** Node.js/Deno/Bun tidak terpasang di mesin ini (sama seperti patch-patch sebelumnya). Sintaks divalidasi parser `esprima` dan logikanya diuji lewat port 1:1 ke Python.
2. **`esprima` 4.0.1 setara ES2017**, tidak mengenal operator `??` (ES2020). Untuk cek sintaks, `??` disubstitusi jadi `||`. Idiom `String(v ?? '')` yang saya pakai **identik dengan yang sudah jalan di node produksi** `HITL Check` — jadi ini keterbatasan parser, bukan risiko runtime.
3. **Belum diuji di n8n sungguhan.** Import, binding kredensial, dan perilaku node Google Sheets `append`/`delete` yang sebenarnya belum dijalankan. Parameter node (`toDelete`, `startIndex`, `numberToDelete`, `typeVersion 4.7`) **disalin dari workflow produksi `2026-07-03-VIRA_MSG_BUFFER-cleanup.json`** yang sudah terbukti jalan — bukan tebakan — tapi tetap wajib dites manual sebelum aktivasi.
4. **Perilaku `autoMapInputData` pada node Append belum diverifikasi live.** Secara desain dia memetakan key JSON ke header sheet yang sama namanya, dan datanya memang dibaca dari sheet yang sama, jadi key-nya pasti cocok. `row_number` sudah dibuang supaya tidak ikut ditulis. Tetap perlu dicek di eksekusi manual pertama.

---

## Workflow `VIRA_Follow_Up` — tidak dipakai, tidak terdampak

Ada workflow `VIRA_Follow_Up` (Schedule Trigger harian jam 10:00) yang membaca tab STATS dan bersandar pada kolom `timestamp`, `last follow up`, `follow_up_count`, `gform_sent_ts`, `gform_filled`.

**Steven mengonfirmasi sistem follow-up tidak dipakai di VIRA The Scholars**, jadi cleanup ini tidak berdampak apa pun padanya.

Konfirmasi itu juga menjelaskan pola data yang sempat terlihat janggal: `gform_sent_ts` terisi di 248 baris (ditulis workflow utama lewat node `Update GForm Sent TS1`) sementara `gform_filled = Y` ada di **0** baris. Itu bukan bug — memang tidak ada yang pernah menandainya karena fiturnya tidak jalan. Sama halnya `follow_up_count` yang bernilai 0 di seluruh 280 baris aktif.

Satu hal yang tetap layak dipastikan sekali: buka daftar workflow di n8n dan **pastikan `VIRA_Follow_Up` memang berstatus non-aktif**. File arsipnya (`archive/vira/VIRA/VIRA_Follow_Up.json`) tercatat `active: true`, tapi field itu hanya merekam status saat file di-export dulu, bukan kondisi sekarang. Kalau ternyata masih aktif, dia mengirim WA ke user tiap hari — dan itu masalah yang jauh lebih besar daripada cleanup ini.

Kalau suatu saat follow-up diaktifkan lagi, tidak perlu perubahan apa pun untuk `off_reason`: filternya sudah `if (botMode === 'OFF' || botMode === 'N') continue;`, jadi baris berlabel SAM otomatis dilewati.

---

## Hal kecil lain yang perlu diperhatikan

| Hal | Catatan |
|---|---|
| Sapaan ulang | Baris yang terhapus jadi "user baru" lagi. Kalau mereka chat lagi, VIRA menyapa dengan intro lengkap ("Saya Sam versi AI yaa..."). Ini memang konsekuensi yang Sam sendiri sudah setujui ("kalau udah 2 bulan, kita lupain semua konteksnya kan gappa"), tapi sebaiknya dikonfirmasi ulang supaya tidak kaget. |
| Sam harus isi **dua** kolom | `bot_mode` = `OFF` **dan** `off_reason` = `SAM`. Kalau cuma `off_reason` yang diisi, barisnya selamat dari cleanup tapi VIRA tetap membalas. Dropdown tidak bisa memaksa keduanya. |
| Tes langkah 5 memicu WA ke Sam | Mengirim `"mau ngomong sama sam"` untuk tes akan menjalankan node `Notify Talk to Sam` → WA masuk ke nomor Sam. Kabari dia dulu supaya tidak dikira ada customer beneran. |
| Secret Kirimi | `user_code`, `secret`, dan `device_id` masih plaintext di dalam file workflow — pola yang sama dengan workflow utama, dan sekarang bertambah satu file lagi. Ini sudah pernah dicatat sebagai Paket 8 (rotasi + pindah ke n8n Credentials) dan masih belum dikerjakan. |
| Kolom mati | `user_status` dan `pending_msg` sudah dipensiunkan oleh patch-patch sebelumnya tapi masih ada di sheet. Momen cleanup ini waktu yang pas untuk menghapusnya sekalian. |

---

## Temuan sampingan (tidak diperbaiki, hanya dilaporkan)

Ada celah waktu sempit di workflow utama yang sudah ada sejak sebelum perubahan ini: setelah `Cek_user_status` lolos, tidak ada lagi pengecekan `bot_mode`. Sisa jalurnya (generate AI Agent + `Wait1` 5–10 detik) tidak terjaga. Kalau Sam menekan OFF **tepat** di jendela itu, node `Update to STATS` masih akan menulis `bot_mode = ON` dan menimpa OFF-nya.

Kabar baiknya: desain `off_reason` ini **tahan terhadap masalah tersebut**. Karena `Update to STATS` tidak menyentuh kolom `off_reason`, label `SAM` tetap utuh, sehingga baris murid/parent Sam **tetap aman dari penghapusan** meski `bot_mode`-nya sempat terbalik jadi ON. Dampaknya cuma VIRA sempat membalas sampai Sam mematikannya lagi.

Tidak saya patch karena di luar scope dan menyentuh node yang sedang berjalan normal. Kalau nanti mau ditutup, caranya menambah pengecekan `bot_mode` sekali lagi tepat sebelum `Update to STATS`.

---

## Checklist urutan pengerjaan

- [ ] 1. Tambah kolom `off_reason` di STATS + pasang dropdown `SAM`/`VIRA`
- [ ] 2. Isi otomatis 179 baris tanpa jejak chat jadi `SAM` (formula di Bagian 3)
- [ ] 3. Edit node `Update row in sheet` → tambah field `off_reason` = `VIRA`
- [ ] 4. Pastikan `off_reason` **tidak** ikut ter-mapping di node `Update to STATS`
- [ ] 5. Save workflow utama, tes: kirim `"mau ngomong sama sam"` → cek kolom `off_reason` terisi `VIRA`
- [ ] 6. Minta Sam sisir 205 baris ber-label `CEK` (deadline sebelum 1 Okt 2026)
- [ ] 7. Import workflow cleanup, isi nomor WA di node `Notify Steven`
- [ ] 8. Duplikat tab STATS sebagai backup, lalu Execute Workflow manual, verifikasi hasil
- [ ] 9. Konfirmasi ke Sam: user lama yang terhapus akan disapa ulang seperti user baru
- [ ] 10. Aktifkan workflow cleanup

**Rollback:** workflow cleanup berdiri sendiri — cukup non-aktifkan. Workflow utama tidak dibuatkan file baru, jadi perubahan Bagian 2 tinggal dibatalkan dengan menghapus field `off_reason` dari node `Update row in sheet`.
