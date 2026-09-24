# Panduan deploy VIRA Personal v3 — siap iklan

Berkas: `workflow/2026-09-05-VIRA-Personal-Main-v3.json`
Patch : `workflow/_patch_2026-09-05.py` → UAT: `workflow/_uat_2026-09-05.py` (154 skenario, semua lolos)
Prompt: `workflow/2026-09-05-system-prompt-VIRA-Personal-v3.md`

Versi lama (`2026-09-04-...-patched-v2.json`) tidak disentuh sama sekali. Kalau ada apa-apa,
tinggal aktifkan lagi yang itu — satu-satunya yang perlu diurungkan cuma dua kolom sheet
di bawah, dan itu pun tidak merusak versi lama kalau dibiarkan.

---

## 1. Sheet — WAJIB, kerjakan sebelum import

Tambahkan **dua kolom baru di tab `STATS`**, di paling kanan, persis dengan nama ini:

```
last_bot_reply
last_bot_reply_ts
```

Isi kolomnya biarkan kosong. Workflow yang mengisi sendiri mulai chat berikutnya.

Kalau langkah ini terlewat, bot tetap jalan normal — jaring pengaman ingatannya saja yang
tidak aktif (sudah diuji, skenario E5). Jadi ini tidak bisa membuat bot mati, tapi jangan
dilewat: kolom inilah inti perbaikan bug 5 September.

## 2. CONFIG — periksa tiga baris

| key | isi | kalau kosong |
|-----|-----|--------------|
| `whitelist_enabled` | **kosongkan atau isi `false`** | aman, default false = semua orang boleh chat |
| `bot_wa_number` | nomor VIRA sendiri (mis. `6285155202354`) | proteksi anti-loop tidak aktif |
| `rate_limit_max` | kosongkan | default 15 pesan/menit |

Kalau suatu saat mau balik ke mode uji terbatas: isi `whitelist_enabled = true` dan
`whitelist_numbers = ["628...","628..."]` (format JSON array). Tidak perlu menyentuh workflow lagi.

## 3. Import & aktifkan

1. Import `2026-09-05-VIRA-Personal-Main-v3.json` ke n8n.
2. Pastikan credential DeepSeek & Google service account ikut terpasang.
3. **Nonaktifkan workflow versi lama** sebelum mengaktifkan yang baru — dua workflow aktif
   di path webhook yang sama (`wa-inbound-steven`) akan membalas dobel.

## 4. UAT manual di nomor asli

Urutan ini yang harus dijalankan sebelum iklan menyala. Nomor 4 dan 5 yang paling penting.

1. **Chat dari nomor ketiga** (bukan dua nomor uji lama) → harus dibalas.
   Ini bukti gerbang whitelist sudah lepas. Sebelum patch, 100% prospek iklan dibuang diam-diam.
2. Ulang persis alur 5 September:
   tanya soal AI CS → sebut bidang usaha → tanya harga → `udah itu aja sih` →
   terima tawaran deck dengan `boleh` → jawab nama bisnisnya.
   VIRA harus **mengenali nama bisnis itu** (bukan "aku belum paham maksudnya"),
   dan **Steven harus menerima notifikasi brief**.
3. Kirim `boleh minta brosurnya` saat tab LINKS tidak punya brosur →
   balasan tidak boleh menjanjikan file apa pun.
4. Kirim `chat paling ramai hari senin` → VIRA harus tetap membalas di giliran berikutnya.
5. Kirim `mau ngobrol langsung sama Steven` → notif handover masuk **dan** bot berhenti.
6. Buka STATS, pastikan `last_bot_reply` terisi teks balasan terakhir.

## 5. Kalau harus mundur

Aktifkan lagi workflow versi 4 September, nonaktifkan v3. Dua kolom baru di STATS boleh
ditinggal — versi lama tidak membacanya dan tidak menulisnya.
