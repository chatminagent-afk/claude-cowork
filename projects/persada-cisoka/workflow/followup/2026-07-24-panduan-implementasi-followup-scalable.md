# Panduan Implementasi — VIRA-PCR Follow-up (versi scalable/konservatif)

**Tanggal:** 2026-07-24
**File workflow:** `workflow/production/VIRA-PCR Follow-up.json`
**Backup versi lama:** `workflow/production/2026-07-24-VIRA-PCR Follow-up.backup.json`
**Gateway:** tetap Kirimi (tidak resmi) — setting default sengaja konservatif untuk menekan risiko banned.

Panduan ini urut. Kerjakan dari atas ke bawah. Jangan lompat ke "Aktifkan produksi" sebelum uji terbatas (Step 5) lulus.

---

## 0. Prasyarat (cek dulu, 2 menit)

- [ ] Punya akses editor n8n tempat workflow PCR jalan.
- [ ] Punya akses tab **CONFIG** dan **STATS** di Google Sheet PCR (`1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o`).
- [ ] Nomor device Kirimi sudah "warm" (nomor lama yang biasa dipakai, bukan nomor baru).
- [ ] Credential n8n `Google Service Account - Persada` (`QC5aF1HyvTElhC0M`) masih aktif — dipakai semua node Sheets di workflow ini.

> Setting bawaan file: **20 nomor/jam**, jeda acak **20–45 dtk**, jam kirim **08–21 WIB**, interval follow-up **72 jam**. Dengan ini 1000 nomor tuntas ~4 hari. Semua bisa diubah lewat CONFIG tanpa sentuh workflow (lihat Step 2).

---

## 1. Import workflow baru ke n8n (ganti yang lama)

Tujuan: mengganti workflow Follow-up live dengan versi baru **tanpa menduplikat** (dua workflow follow-up aktif = kirim dobel).

1. Buka n8n → menu **Workflows**.
2. **Non-aktifkan dulu** workflow follow-up lama: buka workflow "VIRA-PCR Follow-up" yang sekarang → toggle **Active → OFF** (pojok kanan atas). Ini mencegah trigger jam berjalan saat kamu utak-atik.
3. Import versi baru: menu **⋮ (titik tiga) → Import from File** → pilih `workflow/production/VIRA-PCR Follow-up.json`.
   - Karena `id` di file sama (`Ey5WRO8pnOKCVjTHMLq9I`), n8n biasanya menimpa workflow yang sama. **Kalau n8n malah membuat workflow BARU (jadi ada 2)**: hapus/nonaktifkan yang lama, sisakan yang baru saja diimport. **Wajib hanya 1 yang Active.**
4. Setelah import, cek credential tiap node Sheets tidak "unbound":
   - `Read CONFIG FU`, `Read STATS FU`, `Claim STATS FU`, `Rollback STATS FU` → semua harus menunjuk **Google Service Account - Persada**. Kalau ada yang kosong, pilih ulang dari dropdown credential.
5. **Jangan aktifkan dulu.** Lanjut Step 2–4 selagi OFF.

### Cek visual canvas (harus seperti ini)

```
Schedule Trigger FU → Read CONFIG FU → Parse Config FU → Read STATS FU → Filter Kandidat → Loop Kandidat
                                                                                                    │
                                                          (output "loop") ──► Claim STATS FU → Wait FU → Kirim Follow-up
                                                                                                              │  ├─(sukses)─► balik ke Loop Kandidat
                                                                                                              │  └─(error)──► Rollback STATS FU → Notify Admin FU Error → balik ke Loop Kandidat
```

Poin yang WAJIB benar (kalau salah, logikanya rusak):
- **Claim STATS FU ada SEBELUM Wait/Kirim** (bukan sesudah). Ini kunci anti-dobel.
- **Loop Kandidat** output ke-2 ("loop") → Claim STATS FU. Output ke-1 ("done") dibiarkan kosong.
- **Kirim Follow-up** punya 2 output: sukses → Loop Kandidat; error → Rollback STATS FU.

---

## 2. Isi CONFIG keys (tab CONFIG, format key/value)

Semua key ini **opsional** — kalau tidak diisi, workflow pakai default konservatif. Isi hanya kalau mau override.

| key | default (kalau kosong) | isi kalau mau ubah |
|-----|------------------------|--------------------|
| `followup_max_per_run` | **20** (nomor per jam) | naikkan pelan-pelan setelah stabil (mis. 30) |
| `followup_min_delay_sec` | **20** (jeda min antar pesan) | min 3, jangan di bawah itu |
| `followup_max_delay_sec` | **45** (jeda maks antar pesan) | harus ≥ min |
| `followup_open_hour` | 8 | jam buka kirim |
| `followup_close_hour` | 21 | jam tutup kirim |
| `followup_interval_hours` | 72 | jarak minimal antar follow-up per nomor |
| `followup_max` | 0 (tanpa batas) | maks berapa kali 1 nomor di-follow-up |
| `followup_templates` | — (WAJIB ada) | JSON array string, mis. `["Halo {nama}, ...", "Hai {nama}, ..."]` |

Cara isi (kalau key belum ada): tambah baris baru di tab CONFIG, kolom `key` = nama key, kolom `value` = nilainya.

### Personalisasi (opsional tapi disarankan untuk anti-spam)
Di `followup_templates`, sisipkan `{nama}` — otomatis diganti nama depan user. Kalau nama kosong → jadi "Kak". Contoh isi value:
```json
["Halo {nama}, masih tertarik dengan unit di Persada Cisoka? Kalau ada yang mau ditanyakan, saya bantu ya 😊","Hai {nama}, sekadar mengingatkan promo unit PCR masih berlaku. Mau saya kirimkan detailnya?"]
```
Template tanpa `{nama}` tetap jalan (perilaku lama) — tapi pesan jadi identik semua = lebih gampang kena flag.

---

## 3. Cek parameter delay & cap sudah terbaca

1. Buka node **Parse Config FU** → tab **Code**. Pastikan baris default berbunyi `num('followup_min_delay_sec', 20)`, `num('followup_max_delay_sec', 45)`, `num('followup_max_per_run', 20)`. (Ini sudah di file — cukup pastikan tidak ada yang keubah saat import.)
2. Buka node **Wait FU** → field **Wait Amount** harus berupa expression jitter (`{{ Math.floor( ... min_delay + random ... ) }}`) dengan **Unit = Seconds**.

---

## 4. Siapkan data uji terbatas (2–3 nomor milikmu sendiri)

Jangan uji langsung ke 1000 nomor. Buat 2–3 baris kandidat "buatan" di tab **STATS** pakai nomor yang kamu pegang (nomor pribadi/nomor tim), supaya bisa lihat pesan benar-benar masuk.

Untuk tiap baris uji, set kolom STATS begini (mengikuti Sticky Note di workflow):
- `No WA` = nomor kamu (format sama seperti baris lain, mis. `628xxxx`)
- `Counter` = `1` (atau lebih) — tanda sudah pernah chat
- `last_reply_ts` = **epoch sekarang dikurangi 350000** (≈ 4 hari lalu), supaya lolos syarat "sudah lewat interval". Ambil epoch sekarang dari mana saja (mis. ketik `=INT((NOW()-DATE(1970,1,1))*86400)-25200` di sel kosong Sheet lalu kurangi 350000), tempel angkanya.
- `bot_mode` = kosong (atau `on`)
- `survey_status` = kosong
- `follow_up_count` = kosong (0)
- `last_follow_up_ts` = kosong
- `Nama` = isi nama, buat nguji `{nama}`

Pastikan nomor uji **bukan** yang terdaftar sebagai admin/field/media team di CONFIG (nomor itu sengaja di-skip).

---

## 5. Uji manual (WAJIB lulus sebelum produksi)

### 5a. Uji kirim + personalisasi
1. Pastikan **jam WIB sekarang antara 08–21** (kalau di luar itu, workflow sengaja tidak kirim apa-apa — bukan bug).
2. Di editor n8n, buka workflow, klik **Execute Workflow** (manual run).
3. Harapan:
   - Node `Filter Kandidat` output = jumlah baris uji kamu (maks 20).
   - Tiap nomor uji **menerima 1 pesan WA**, dengan nama tersisip kalau template pakai `{nama}`.
   - Jeda antar pesan terlihat **20–45 dtk** (bukan serempak).
4. Cek tab STATS baris uji: `follow_up_count` naik jadi 1, `last_follow_up_ts` terisi epoch sekarang.

### 5b. Uji anti-dobel (paling penting)
1. **Segera** setelah run 5a selesai, klik **Execute Workflow** lagi (masih dalam interval 72 jam).
2. Harapan: `Filter Kandidat` output = **0** (semua nomor uji sudah ditandai `last_follow_up_ts` barusan → di-skip). **Tidak ada pesan kedua yang terkirim.** Ini bukti claim-before-send bekerja.

### 5c. Uji rollback (opsional, kalau mau yakin)
1. Sementara rusak kredensial Kirimi (mis. ubah `kirimi_secret` di CONFIG jadi salah) lalu jalankan dengan 1 nomor uji yang belum di-follow-up.
2. Harapan: kirim gagal → `Notify Admin FU Error` kirim notif ke admin → di STATS, `last_follow_up_ts` nomor itu **kembali kosong / ke nilai semula** dan `follow_up_count` tidak naik (state dipulihkan). Artinya nomor itu akan dicoba lagi run berikutnya, tidak hangus.
3. **Kembalikan `kirimi_secret` ke nilai benar** setelah tes.

### 5d. Bersihkan
Hapus baris uji dari STATS setelah semua lulus (biar tidak ikut ke-follow-up saat live).

---

## 6. Aktifkan produksi

1. Pastikan CONFIG production benar (`kirimi_user_code`/`kirimi_secret`/`kirimi_device_id` = milik PCR, bukan The Scholars).
2. Toggle workflow **Active → ON**.
3. Trigger jadwal jalan tiap 1 jam otomatis. Tiap jam operasional ambil ≤20 nomor.
4. **Pantau hari pertama:**
   - Menu **Executions** n8n → lihat tiap run selesai cepat (beberapa menit), tidak ada yang error beruntun.
   - Cek beberapa nomor benar-benar terima pesan (tanya sampel).
   - Cek HP device Kirimi tidak muncul warning WhatsApp / tidak logout tiba-tiba.

---

## 7. Tuning (setelah stabil beberapa hari)

Semua lewat CONFIG, tanpa import ulang:
- Kalau aman & mau lebih cepat: naikkan `followup_max_per_run` bertahap (20 → 30 → 40). Jangan langsung besar.
- Kalau ada tanda-tanda bahaya (device kena warning, banyak user block): turunkan cap + lebarkan delay (`min 30 / max 60`).

| Skenario | max_per_run | delay | ~selesai 1000 nomor |
|----------|-------------|-------|---------------------|
| Sangat aman (default) | 20 | 20–45 dtk | ~4 hari |
| Sedang | 30 | 15–30 dtk | ~3 hari |
| Agresif (hati-hati) | 40 | 10–20 dtk | ~2 hari |

---

## 8. Rollback (kalau ada masalah)

1. Toggle workflow **Active → OFF**.
2. Import ulang `workflow/production/2026-07-24-VIRA-PCR Follow-up.backup.json` (versi lama) kalau perlu balik total.
3. Catatan: baris STATS yang sudah ter-follow-up tetap tercatat — tidak perlu di-reset.

---

## Batas yang tetap ada (jujur)

Fix ini menyelesaikan **overload teknis** (workflow, Sheets, dobel-kirim, kegagalan) dan **menekan** risiko banned lewat drip pelan + jitter + personalisasi. Tapi Kirimi tetap gateway **tidak resmi** — risiko banned dari sisi pola akun **tidak nol**. Pemicu ban terbesar bukan volume, tapi **user klik Block/Report**. Jaga isi pesan tetap relevan & sopan, dan hindari nomor yang tidak pernah benar-benar berinteraksi. Untuk kebutuhan rutin volume tinggi jangka panjang, WhatsApp Business API resmi tetap opsi paling aman.
