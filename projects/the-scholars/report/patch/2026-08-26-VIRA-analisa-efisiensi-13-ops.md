# Analisis Efisiensi 13 Operasi Sheets — Workflow VIRA Utama

**Tanggal:** 2026-08-26
**Baseline:** r6 (`2026-08-14-VIRA-V4-r6-link-guard-wa-channel.json`)
**Status:** r7 sudah dibuat & lulus QA. Sisanya **usulan, belum dibangun.**

---

## Ringkasan

Kamu bertanya: bisa tidak 13 operasi Sheets per pesan dikurangi, dan mana yang
tidak relevan.

Jawabannya: **bisa, 13 → 9**, tapi **bukan lewat cara yang saya sarankan
sebelumnya.** Setelah menelusuri lebih dalam, saya menarik rekomendasi
penggabungan write — alasannya di bawah, dan menurut saya alasannya penting.

| Usulan | Hemat | Status |
|---|---|---|
| Buang `Query LINKS for GForm` | −1 (jalur GForm) | ✅ **Dibangun, 21/21 QA lulus** — r7 |
| Cache 4 tab statis | **−4 / pesan** | 📋 Dirancang, belum dibangun — butuh keputusanmu |
| ~~Gabung 3 write STATS~~ | ~~−2~~ | ❌ **Ditarik** — lihat bagian 3 |
| ~~Buang `Read STATS` terakhir~~ | ~~−1~~ | ⚠️ Tidak disarankan — lihat bagian 4 |
| Paralelkan 4 read statis | 0 ops, −3 round-trip | ⚠️ Butuh node Merge — lihat bagian 5 |

---

## 1. r7 — buang pembacaan LINKS yang dobel ✅

`Query LINKS for GForm` membaca **tab yang sama** dengan `Read LINKS Data` yang
sudah dibaca lebih dulu di rantai FAQ Retrieve, dalam eksekusi yang sama.

Kenapa aman:
- **Tidak ada satu pun node di workflow ini yang menulis ke LINKS** (diverifikasi
  dengan memindai seluruh 18 node Sheets). Jadi tidak ada jendela basi.
- `Read LINKS Data` selalu jalan sebelum `IF Send GForm` (diverifikasi dengan
  penelusuran graf, bukan asumsi).

**Berkas:** `2026-08-26-VIRA-r7-drop-duplicate-links-read.json`
**QA:** `2026-08-26-qa-r7-selftest.html` — **21/21 lulus**

Diff terhadap r6, tepat sebanyak ini dan tidak lebih:
```
node dibuang : ['Query LINKS for GForm']
node baru    : []
node berubah : ['Pick GForm Link']
connection   : IF Send GForm -> Pick GForm Link (langsung)
```

### Satu detail yang hampir terlewat

`Read LINKS Data` ber-**`executeOnce: true`**. Artinya pada run kedua (jalur
debounce/buffer), referensi run saat ini **kosong** walau datanya sudah terambil
di run pertama. Kalau `Pick GForm Link` cuma diganti nama nodenya, link GForm
akan gagal terkirim **persis pada user yang mengirim pesan beruntun**.

Node `FAQ Retrieve` sudah menemui masalah ini dan memasang penawar `.all(0, 0)`
di helper `grab`. Pola yang sama saya salin ke `Pick GForm Link`. Ada tes khusus
untuk skenario run-kedua ini, plus tes pembanding yang membuktikan tanpa penawar
itu memang gagal.

**Tapi jujur:** sendirian, r7 hanya menghemat 1 operasi di jalur GForm saja.
Menurut saya **tidak sepadan** dengan satu siklus import + QA produksi. Simpan
saja, gabungkan saat kamu mengerjakan caching di bawah.

---

## 2. Caching 4 tab statis — ini kemenangan sesungguhnya 📋

`Read FAQ`, `Read PROGRAM Data`, `Read ABOUT Data`, `Read LINKS Data` dibaca
**setiap pesan masuk**, padahal isinya nyaris tidak pernah berubah.

| Tab | Baris | Dipakai bagaimana |
|---|---|---|
| FAQ | 112 | Seluruh tab ditarik, lalu dicari lokal (TF-IDF) |
| PROGRAM | 4 | Seluruh baris selalu masuk `data_context` |
| ABOUT_SAM | 10 | **Hanya dipakai kalau regex `askingAboutSam` cocok** — selebihnya ditarik lalu dibuang |
| LINKS | 7 | Difilter status aktif, selalu dipakai |

**−4 operasi di mayoritas pesan. 13 → 9, potong 31%** tepat di bottleneck yang
dulu bikin pesan hilang.

Polanya sudah terbukti di workflow ini: `Rate Limiter LID` sudah memakai
`getWorkflowStaticData` untuk hitungan rate limit.

### Kenapa belum saya bangun

Tiga alasan, dan menurut saya sebaiknya memang menunggu:

1. **Butuh percabangan IF** — node bacanya harus benar-benar dilewati, bukan
   sekadar hasilnya diabaikan. Kalau tetap jalan, ops-nya tidak berkurang.
2. **Menyentuh `FAQ Retrieve`** — Code node 571 baris, node paling kritis di
   jalur balasan, dan **sudah berjaringan parut** (penawar `.all(0, 0)` itu
   bukti ada masalah halus yang pernah menggigit di sana).
3. **Butuh keputusanmu soal basi.** Kalau Sam mengubah harga atau menutup batch,
   bot masih akan mengutip data lama selama TTL. Itu keputusan bisnis, bukan teknis.

Saya tidak nyaman mengubah jalur balasan produksi tanpa kamu bisa mengujinya di
n8n asli — logika JS-nya bisa saya uji di browser, tapi perilaku percabangan n8n
dan persistensi `staticData` tidak bisa.

### Rancangannya, kalau kamu setuju

```
Preprocess -> Cache Check (Code) -> IF Cache Hit
                                     ├ true  -> FAQ Retrieve          (0 read)
                                     └ false -> Read FAQ -> PROGRAM
                                                -> ABOUT -> LINKS
                                                -> Cache Store -> FAQ Retrieve
```

Perubahan di `FAQ Retrieve` cuma satu tempat: helper `grab(node)` dibuat
mengecek `$json._cache[node]` dulu sebelum jatuh ke `$(node)`. Sisa 571 baris
tidak disentuh.

**TTL saran: 120 detik.** Dengan volume sekarang, itu sudah memotong hampir
semua pembacaan berulang, dan jendela basinya masih pendek untuk ukuran
percakapan WhatsApp. Set `0` untuk mematikan cache tanpa perlu ubah topologi.

Tinggal bilang mau, dan sebutkan TTL-nya.

---

## 3. Penggabungan 3 write STATS — saya tarik rekomendasinya ❌

Sebelumnya saya bilang ini "kemenangan terbaik, risiko nol". **Itu keliru**, dan
alasannya baru terlihat setelah memeriksa topologi kegagalannya, bukan cuma
urutan baca-tulisnya.

Sekarang ketiganya bercabang **paralel** dari `Send WA + Verify (Kirimi)`:

```
Send WA + Verify ├─> Extract & Prepare Data -> Read STATS -> Process Counter -> Update to STATS
                 ├─> Delete_Pending_Msg                    (buffer_done_ts)
                 └─> Update STATS - Greeting Flag -> IF -> Update Greeting
```

Menggabungkan `Delete_Pending_Msg` ke `Update to STATS` memindahkannya **ke ujung
rantai analitik** — di belakang `Read STATS`.

Masalahnya: `buffer_done_ts` itu **watermark** yang menandai pesan buffer sudah
terjawab. Kalau `Read STATS` gagal — **dan 429 adalah persis mode gagal yang
terdokumentasi di sini** — maka watermark tidak pernah maju, dan pesan berikutnya
akan memproses ulang isi buffer lama.

Jadi penggabungan itu menukar **1 panggilan API** dengan **mengikat watermark ke
rantai yang paling rentan 429**. Untuk workflow dengan riwayat pesan hilang,
itu pertukaran yang buruk.

Cabang paralel yang sekarang justru fitur, bukan pemborosan: `Delete_Pending_Msg`
tetap jalan walaupun cabang analitik gagal.

`Update Greeting` bisa digabung dengan lebih aman (ia idempoten), tapi hanya
menghemat 1 ops di pesan pertama user saja — tidak sepadan dengan risikonya.

**Kesimpulan: biarkan ketiganya apa adanya.**

---

## 4. Membuang `Read STATS` terakhir ⚠️

Menghemat −1 ops di **setiap** pesan, dan pembenarannya memang paling lemah di
antara 4 read STATS — ia cuma melindungi `Counter` dan `Pesan Pertama`, bukan
field kontrol seperti `bot_mode`.

Tapi konsekuensinya: eksekusi bersamaan selama jendela latensi AI bisa membuat
`Counter` kurang hitung, dan `Counter` tampil di Direktori Lead dashboard yang
dilihat Sam.

Menukar akurasi angka yang dilihat klien dengan 1 panggilan API — menurut saya
tidak sepadan. **Tidak disarankan.**

---

## 5. Memparalelkan 4 read statis ⚠️

Sekarang mereka **berantai sekuensial**:
`Read FAQ → Read PROGRAM → Read ABOUT → Read LINKS → FAQ Retrieve`

Tiap pesan menunggu 4 round-trip Sheets berurutan. Ini bukan penghematan ops,
tapi **latensi yang dirasakan user** — kira-kira −3 round-trip per pesan.

Kendalanya: kalau keempatnya langsung disambung ke `FAQ Retrieve`, node itu akan
jalan **empat kali**. Perlu node Merge 4-input. Menambah node tanpa mengurangi
ops, dan mengubah topologi jalur kritis.

Kalau caching jadi dikerjakan, ini otomatis jadi tidak relevan — mayoritas pesan
tidak akan membaca sama sekali. **Saran: lewati, kerjakan caching saja.**

---

## 6. Temuan sampingan — ranjau laten di filter status LINKS 🟡

Ketemu tidak sengaja saat menulis tes r7.

`Pick GForm Link` menyaring link aktif dengan:

```js
/aktif|active|on|ya/i.test(String(r['Status'] || ''))
```

Regex ini **tidak berjangkar**. String `"nonaktif"` **mengandung** `"aktif"` —
jadi link yang ditandai nonaktif akan lolos sebagai aktif dan **tetap dikirim ke
customer**. (`"nonaktif"` juga mengandung `"on"`.)

**Belum menggigit hari ini.** Tab LINKS produksi memakai `Active` / `Closed`,
dan keduanya berperilaku benar — sudah saya verifikasi ke snapshot produksi:

| Status di produksi | Lolos filter aktif? | Benar? |
|---|---|---|
| `Active` (4 baris) | ya | ✅ |
| `Closed` (3 baris) | tidak | ✅ |
| `Nonaktif` (hipotetis) | **ya** | ❌ |

Tapi `"Nonaktif"` adalah kata yang sangat wajar diketik orang Indonesia di kolom
itu — termasuk oleh Sam. Sekali diketik, link yang sudah ditutup akan dikirim ke
calon murid tanpa ada yang sadar.

**Perbaikannya satu baris**, setelah trim + lowercase:

```js
const isActive = s => ['aktif', 'active', 'on', 'ya'].includes(
  String(s || '').trim().toLowerCase()
);
```

`Active` tetap lolos, `Closed` tetap ditolak, `Nonaktif` jadi ditolak dengan benar.

**Sengaja TIDAK saya masukkan ke r7.** Ini urusan yang berbeda dari pengurangan
ops, dan mencampur perubahan yang tidak berhubungan ke dalam satu patch produksi
justru menyulitkan review. Suite QA r7 mengunci perilaku sekarang apa adanya
(ditandai `[ranjau laten]`) supaya perubahannya nanti terlihat jelas.

Bilang saja kalau mau ini dikerjakan — bisa berdiri sendiri, atau ikut caching.

---

## Yang saya sarankan

1. **Jangan import r7 sendirian** — hematnya terlalu kecil untuk satu siklus QA produksi.
2. **Putuskan soal caching + TTL.** Itu 31% pemotongan di bottleneck yang sudah
   terbukti memakan korban. Kalau setuju, r8 = caching + r7 + perbaikan filter
   status, satu patch, satu QA.
3. **Biarkan write STATS dan 4 read STATS apa adanya.** Cabang paralelnya itu
   yang menjaga watermark tetap maju saat 429 menyerang.
