# Catatan Build — Workflow VIRA Steven

> Menggantikan `2026-08-15-catatan-build-workflow.md`. Baca file ini, bukan yang lama.

Dibangun dengan **mentransformasi** `2026-08-08-VIRA-PCR-Main-V2.1` (91 node), bukan ditulis dari nol.
Skripnya `_transform.py`, **idempoten** — dia selalu membaca ulang file Persada asli dan
menghasilkan output yang sama, jadi aman dijalankan ulang kapan saja.

```bash
cd "D:\Documents\Claude Cowork\VIRA Steven\workflow" && python -X utf8 _transform.py
```

Hasil: **100 node**, tanpa koneksi menggantung, tanpa node yatim.

**Jangan pernah mengedit `2026-08-15-VIRA-Steven-Main.json` langsung.** Semua perubahan
ditambahkan sebagai langkah di `_transform.py`, lalu regenerate. File JSON-nya keluaran, bukan sumber.

> **Sejak langkah 20 (2026-08-16), regenerate aman diimpor langsung.** Dulu output transform
> memakai kredensial placeholder kosong, jadi tiap regenerate harus memasang ulang kredensial
> satu per satu di n8n — itu yang memaksa mengedit JSON hasil unduhan, dan sejak itu file live
> menyimpang dari skrip. Sekarang ID kredensial asli ditulis di langkah 20, begitu juga model
> balasan dan daftar node yang sengaja dimatikan. Kalau kamu mengubah salah satunya di n8n,
> ubah juga konstanta di langkah 20 — kalau tidak, regenerate berikutnya akan mengembalikannya.

---

## Cara memverifikasi

Empat pemeriksa, jalankan berurutan. Semuanya harus lolos.

```bash
cd "D:\Documents\Claude Cowork\VIRA Steven\workflow" && python -X utf8 _transform.py && python -X utf8 _cek_js.py 2026-08-15-VIRA-Steven-Main.json && python -X utf8 _validasi.py && python -X utf8 _uji_parser.py
```

| Skrip | Yang diperiksa |
|---|---|
| `_transform.py` | 100 node, `menggantung: tidak ada`, `yatim: tidak ada` |
| `_cek_js.py` | keseimbangan token di 28 code node (string, template literal, komentar, regex) |
| `_validasi.py` | kolom tulis vs skema sheet, `documentId` seragam, 6 variabel konteks tersambung, tiap `$('Node')` menunjuk node yang ada, rantai DECK_REQUEST utuh, sisa jejak Persada |
| `_uji_parser.py` | 20 asersi logika parser `[DECK_REQUEST]` & `[FACTS]` |

**Batas `_uji_parser.py`:** dia menjalankan padanan Python dari regex yang dipakai node, jadi dia
membuktikan *logikanya* benar — bukan bahwa n8n mengeksekusi JS-nya tanpa error. Node.js tidak
terpasang di mesin ini. Verifikasi runtime tetap harus lewat uji chat sungguhan (checklist bagian E).

Cek idempotensi kalau `_transform.py` diubah:

```bash
cd "D:\Documents\Claude Cowork\VIRA Steven\workflow" && python -X utf8 -c "import hashlib,io,subprocess,sys;hs=[(subprocess.run([sys.executable,'-X','utf8','_transform.py'],capture_output=True),hashlib.sha256(io.open('2026-08-15-VIRA-Steven-Main.json','rb').read()).hexdigest())[1] for _ in range(3)];print('idempoten:',len(set(hs))==1)"
```

---

## 25 langkah transformasi

| # | Langkah |
|---|---|
| 1 | 5 node alur survei & request-call dihapus, alurnya dijembatani ulang |
| 2 | `Whitelist Gate` → **`Blocklist Gate`** (kode ditulis ulang total) |
| 3 | `Read PRODUK Data` → `Read PROGRAM Data` |
| 4 | Node `Read ABOUT_STEVEN` ditambahkan |
| 5 | `documentId` semua node → sheet VIRA Steven; model utilitas → `claude-haiku-4-5` |
| 6 | Model balasan `claude-sonnet-5` (thinking **dimatikan**), kredensial jadi placeholder — **keduanya ditimpa langkah 20** |
| 7 | System prompt disuntik ke `AI Agent` (13.724 karakter) |
| 8 | Notifikasi tim lapangan & media dialihkan ke HP Steven |
| 9 | Pemetaan kolom `Update to STATS` diperbaiki (buang 9 kolom Persada, tambah 10 kolom VIRA Steven) |
| 10 | Node `Rakit Konteks` disisipkan sebelum AI Agent |
| 11 | `sheetName` gid Persada → mode nama tab (9 node) |
| 12 | `Resolve User Row` mengekspos `userRow` + 11 field STATS |
| 13 | `Process All` ditulis ulang (27.045 → 14.739 karakter) |
| 14 | `Rakit Konteks` menambah `brief_context` (variabel konteks ke-6) |
| 15 | 7 node baru: rantai `[DECK_REQUEST]` |
| 16 | `Collect Handover Context` diarahkan ke profil brief VIRA Steven |
| 17 | Penanda `[PCR]` di teks notifikasi → `[VIRA Steven]`; `Record to UNKNOWN` kolom diperbaiki |
| 18 | Rantai handover (`Summarize`, `Format`, `Log EVENTS`) dilepas dari domain properti |
| 19 | Domain Persada di prompt runtime dibersihkan (`Cek_user_status`, `Preprocess`, vision, notif media) |
| 20 | Kredensial live, model balasan Haiku 4.5, dan node Wait yang sengaja dimatikan ditulis eksplisit |
| 21 | Handover digerbangi `IF Talk To Admin`; `Notify Talk to Admin` dibuang |
| 22 | Media: URL Drive dinormalkan, FAIL LOUD, urutan cabang, guard file di 2 rantai kirim |
| 23 | Cache katalog (FAQ/PROGRAM/LINKS/ABOUT_STEVEN) + `FAQ Retrieve` ditulis ulang |
| 24 | `Read STATS for HITL` & `Read STATS` dibuang, sumbernya pindah ke `Resolve User Row` |
| 25 | Semua node Sheets `retryOnFail` 4x jeda 5 detik |

---

## Tiga gejala dari uji chat live pertama (2026-08-16) dan akarnya

### 1. Handover jalan di setiap pesan

Akarnya **langkah 1 skrip ini sendiri**. Di Persada rantainya:

```
Process All → IF Schedule Survey → Update STATS Survey → Collect Handover Context
```

Dua node tengah masuk `DROP`, lalu logika penjembatanan menyambung `Process All` langsung
ke `Collect Handover Context` supaya node itu tidak jadi yatim. Penjembatanan menyelamatkan
node-nya — dan ikut membuang IF yang jadi gerbangnya. `Process All` selalu `return` satu item,
jadi handover jalan tanpa syarat. Tab `EVENTS` mencatat 2 baris `DELEGATED` dari satu sesi uji.

Mematikan node-nya bukan perbaikan: di n8n node disabled itu *pass-through*, jadi item tetap
mengalir ke `Summarize Handover` — satu panggilan LLM per pesan untuk data yang tidak pernah
dibentuk. Sekarang rantainya digantung di `IF Talk To Admin`, dan ujungnya menulis `bot_mode=OFF`
sesuai janji system prompt.

Prospek yang minta pitch deck **tidak** lewat sini — dia punya `IF Deck Request → Notify Admin Deck`.
Menyambungkan keduanya cuma bikin notifikasi ganda.

### 2. Link media tidak pernah terkirim

Lima hal menumpuk:

| Lapis | Temuan |
|---|---|
| Data | 5 dari 6 baris `LINKS` berstatus `Nonaktif`, 4 di antaranya URL `<<ISI MANUAL>>`. Yang aktif cuma `instagram` |
| Model | AI mengeluarkan `[SEND_MEDIA:demo-vira]`; key yang ada `demo-video`. Tidak ketemu → jalur manual |
| Balasan | `Process All` benar memilih jalur manual, tapi balasannya tetap menjanjikan video — tidak ada FAIL LOUD |
| URL | `uc?export=download` membalas HTML konfirmasi virus-scan untuk file besar. `responseFormat: file` menelannya sebagai biner tanpa error → Kirimi kirim file rusak |
| Urutan | Cabang `IF Media Manual` ada di urutan pertama output `Process All`, jadi notif ke Steven keluar sebelum balasan ke prospek |

### 3. Sheets nyaris kena kuota

Satu pesan yang dibalas = **14 read + 5 write** (`appendOrUpdate`/`update` masing-masing
1 read lookup + 1 write). Kuota Google **60 read/menit per user per project**, dipakai bareng
semua workflow di akun yang sama → **~4 pesan/menit**. Setelah langkah 23–24: **8 read**.

Yang paling menentukan justru di luar workflow: kalau VIRA Steven, The Scholars, dan Persada
memakai akun Google yang sama, ketiganya berebut jatah 60 yang sama. Service account terpisah
per klien memberi tiap-tiap 60/menit sendiri, tanpa mengubah satu baris kode pun.

---

## Rantai `[DECK_REQUEST]` — mesin lead-nya

```
Process All → IF Deck Request → Read REQUESTS → Merge Brief → Write REQUESTS
            → Wait Deck (20 dtk) → Update STATS Brief → Notify Admin Deck
```

| Node | Tugas |
|---|---|
| `IF Deck Request` | lolos hanya kalau `isDeckRequest` true (tingkat 1 lengkap) |
| `Read REQUESTS` | ambil baris lama prospek ini. `alwaysOutputData: true` supaya tab kosong tidak menghentikan cabang |
| `Merge Brief` | gabungkan 27 field; nilai baru menang **hanya kalau ada isinya**. Hitung `kelengkapan` & `brief_terisi`, susun teks notifikasi |
| `Write REQUESTS` | `appendOrUpdate` cocokkan `no_wa` — satu prospek satu baris yang makin kaya |
| `Wait Deck` | jeda 20 detik supaya jalur utama (`Update to STATS`) selesai menulis baris STATS lebih dulu |
| `Update STATS Brief` | tulis `deck_requested=Y` + `brief_terisi` |
| `Notify Admin Deck` | rangkuman lengkap ke `6285171701168` |

`brief_terisi` inilah yang bikin bot sadar diri: giliran berikutnya `Resolve User Row` membacanya,
`Rakit Konteks` menyisipkannya sebagai `brief_context`, dan bot berhenti menanyakan hal yang sudah dijawab.

Desain lengkap 27 field dan pemetaannya ke slide deck: `docs/2026-08-16-desain-brief-deck-request.md`.

---

## Lima bug yang ditemukan saat build ini

Empat di antaranya **senyap** — tidak menghasilkan error, hanya diam tidak melakukan apa-apa.

### 1. `_transform.py` sendiri tidak deterministik
Langkah 5 versi lama mengumpulkan nilai `documentId` ke sebuah `set`, lalu `str.replace` satu per satu.
Salah satu nilainya adalah URL utuh yang memuat ID lain sebagai substring, jadi hasil akhirnya
bergantung pada urutan iterasi set — yang diacak Python tiap proses. **Dua run berturut-turut
menghasilkan file berbeda.** Sekarang `documentId` ditulis eksplisit per node.

### 2. Sembilan node Sheets menunjuk gid milik Persada
`documentId` sudah diganti, `sheetName`-nya belum: masih `mode: "list"` berisi angka gid
(`1863977253`, `824508993`, …) dari spreadsheet Persada. Gid itu tidak ada di spreadsheet VIRA Steven.
**Semua node baca/tulis itu gagal saat runtime — bot tidak akan jalan sama sekali.**

### 3. Notifikasi handover & media manual tidak pernah terkirim
Langkah 8 mengganti pola `config.field_team_phone`. Tapi `Format Handover Message` dan
`Format Media Notif` memakai variabel bernama `cfg`, bukan `config`, jadi keduanya luput.
Akibatnya `tujuan` kosong → node `return []` → **notifikasi berhenti diam-diam.**
Ini bug bawaan dari Persada, bukan bawaan transformasi.

### 4. `Cek_user_status` menyuntikkan intro Persada ke AI
String hardcoded `'Haloo, terima kasih sudah menghubungi Persada Cisoka Residence yaa. Saya Vira,
siap bantu info seputar unit, harga, dan syarat KPR.'` dikirim sebagai `CRITICAL INSTRUCTION`
dengan perintah menulisnya **persis**. Prospek pertama akan disambut sebagai calon pembeli rumah.
Blok `[SYSTEM_DATA]`-nya juga penuh slot properti (`LOKASI_KERJA`, `ASK_UNIT`, `PENDING_SURVEY`).

### 5. `Preprocess` menyuruh AI memasang `[SCHEDULE_SURVEY]`
Setelah `Process All` ditulis ulang, tag itu tidak diparsing **maupun** dibersihkan — jadi kalau AI
menurutinya, tag mentah ikut terkirim ke layar prospek. Sekarang deteksi tanggal/jam diarahkan
ke `[TALK_TO_ADMIN]`.

Ditambah tiga temuan kecil: vision prompt masih "chatbot perumahan Persada Cisoka" dengan kategori
KPR/siteplan; `Record to UNKNOWN` menulis kolom `message` yang tidak ada di tabnya (append gagal);
sanitizer tag pada deskripsi gambar belum mengenal `DECK_REQUEST` (celah injeksi lewat gambar).

---

## Kenapa `Process All` ditulis ulang, bukan ditambal

Tiga blok warisan Persada bukan sekadar kode mati:

- **`[REQUEST_CALL]` punya fallback frasa.** Kalimat seperti "bisa hubungi langsung" memicu
  penempelan `admin_phone_display` ke balasan. Itu **nomor HP pribadi Steven**, bocor ke prospek
  hanya karena bot memakai frasa biasa.
- **`[SCHEDULE_SURVEY]` + FAIL LOUD** bisa **menimpa balasan yang sudah benar** dengan pertanyaan
  jadwal survey.
- **Fallback frasa `[SEND_MEDIA]`** ("kirim brosur", "saya kirim siteplan") memicu notifikasi
  media manual palsu ke HP Steven.

Ditambah kanonikalisasi tipe unit dan pencocokan kolom `Tipe Unit` — kolom itu tidak ada di sheet
VIRA Steven, jadi seluruh cabangnya mati.

---

## Sisa jejak Persada yang sengaja dibiarkan

Sudah dipastikan tidak sampai ke AI maupun ke prospek:

| Lokasi | Apa | Kenapa aman |
|---|---|---|
| `FAQ Retrieve` | `$('Read LINGKUNGAN Data')` | hanya di dalam komentar changelog; bloknya sudah dihapus sejak V2.1 Persada |
| `Parse Config` | `client_name` default `'Persada Cisoka Residence'` | **tidak dibaca node manapun**. Kalau nanti ada node yang memakainya, isi dulu key `client_name` di CONFIG |
| `Parse Config` | pembaca `field_team_phone` / `media_team_phone` | opsional, default `[]`, tidak ada pemakai |
| `Cek_user_status` | pembacaan `pending_survey_*` | kolomnya tidak ada di STATS → selalu `''` |
| `Rakit Konteks Gambar` | kata `SCHEDULE_SURVEY` | hanya di komentar; regex sanitizernya sudah diganti |

---

## Yang BELUM selesai

### 1. Daily Cap Guard belum ada — bukan cuma "belum disetel"
`daily_message_cap` (500) dan `daily_vision_cap` (100) ada di CONFIG tapi **tidak dibaca node manapun.**
Tidak ada node yang menghitung, tidak ada baris `CAP_REACHED` yang akan pernah muncul di `EVENTS`.

Rem biaya yang benar-benar aktif saat ini hanya dua:
- `Rate Limiter LID` — 5 pesan/menit/nomor
- **Spend limit di Anthropic Console** ← ini satu-satunya pengaman keras. Wajib disetel sebelum iklan.

### 2. Vision masih `source.type: "url"`
Perbaikan download→base64 belum diterapkan. Kemampuan baca gambar bergantung pada apakah Anthropic
bisa mengunduh URL Kirimi langsung — belum pernah diverifikasi dengan data live. Uji E6 menjawabnya.

### 3. Tidak ada kill switch global
Dashboard VIRA lama punya key `VIRA_STATUS`. CONFIG VIRA Steven tidak punya key itu dan tidak ada
node yang memeriksanya. Untuk bot yang di-ads, ini celah nyata: kalau ada yang salah, satu-satunya
cara menghentikan adalah menonaktifkan workflow dari n8n.

### 4. PWA dashboard belum diadaptasi
`D:\Documents\Claude Cowork\VIRA\VIRA-DASHBOARD` (webhook `vira-getdata` / `vira-toggle-user` /
`vira-toggle-global`) — butuh ganti Sheet ID, buang tab `MOCK Booking`, tambah `REQUESTS`.

### 5. Biaya system prompt
System prompt 13.724 karakter (~3.500 token) dikirim tiap giliran. Isinya statis, jadi sebagian besar
tertutup prompt caching — tapi kalau volume iklan tinggi dan biayanya terasa, bagian yang paling
mudah dipangkas adalah penjelasan per-baris di tag `[DECK_REQUEST]`.

---

### 6. Dua kolom sheet yang belum ada — `_validasi.py` masih melaporkannya

Ini satu-satunya masalah tersisa di validator, dan keduanya di sisi Google Sheets, bukan workflow:

- **`REQUESTS` masih 12 kolom**, `Write REQUESTS` menulis 32. Terapkan
  `sheet/2026-08-16-header-baru-untuk-sheet-live.tsv` sebagai baris 1. Tab-nya masih kosong,
  jadi aman ditimpa. **Tanpa ini rantai deck — inti funnel-nya — gagal menulis.**
- **`STATS` belum punya kolom `brief_terisi`.** Tambahkan sebagai kolom AD (sesudah
  `last_follow_up_ts`). Tanpa ini `brief_context` tidak pernah terisi dan bot terus
  menanyakan hal yang sudah dijawab.

### 7. Katalog LINKS masih kosong

`demo-video` sudah punya URL tapi statusnya `Nonaktif`; empat baris lain URL-nya
`<<ISI MANUAL>>`. Selama begini, satu-satunya media yang bisa disebut bot cuma `instagram`.
`rapikanUrl` di `Preprocess`-nya `Process All` sudah menangani bentuk link Drive, jadi URL
`drive.google.com/uc?...` atau `drive.google.com/file/d/...` boleh ditempel apa adanya.

---

## Urutan pengerjaan yang kusarankan

1. **Dua kolom sheet di atas** (`REQUESTS` 32 kolom, `STATS.brief_terisi`) — tanpa ini rantai deck mati
2. Aktifkan baris `LINKS` yang filenya sudah siap; sisanya biarkan `Nonaktif` (bot sekarang jujur soal itu)
3. Import ulang workflow & jalankan uji di checklist bagian E — kredensial tidak perlu dipasang ulang lagi
4. Service account Google terpisah untuk VIRA Steven (lepas dari jatah kuota The Scholars & Persada)
5. Spend limit Anthropic Console
6. Nyalakan lagi `Wait3` (debounce) & `Wait1` (jeda ketik) sebelum live — keduanya dimatikan untuk uji cepat
7. Kill switch global
8. Daily Cap Guard
9. Vision base64 (kalau E6 gagal)
10. PWA dashboard

### Opsional: `katalog_cache_minutes` di CONFIG

Langkah 23 membaca key ini; kalau tidak ada, defaultnya 10 menit. Isi `0` untuk mematikan cache
(mis. saat sedang sering mengedit isi FAQ/PROGRAM dan mau perubahannya langsung terasa).
`Read CONFIG` sengaja **tidak** ikut di-cache — di situ nanti kill switch global dibaca.
