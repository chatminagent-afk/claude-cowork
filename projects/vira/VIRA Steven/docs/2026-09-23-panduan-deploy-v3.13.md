# Deploy v3.13 — harga hanya kalau ditanya, handover langsung (2026-09-23)

**Berubah** (semuanya dari uji "Rehan" tadi siang):
- Jawaban alur seperti "harga dulu, trs klo udah aman baru ke payment" tidak lagi dianggap menanyakan harga. VIRA tidak menyebut Basic/Premium kalau tidak ditanya, dan tidak mengomentari "bukan nanya harga".
- "usahaku sewa raket padel" masuk ke **industri**, jadi nama usahanya ditanya ulang. "persewaan aja sih" tersimpan sebagai "persewaan".
- "kpn bs ngmng sm steven?" langsung disambungkan: bot OFF, notif ke admin, balasan "Siap kak, sudah aku sambungkan ke Steven…". VIRA tidak bertanya "mau aku sambungkan?".
- Sesudah deck terkirim, info baru dari prospek ("basic deh") dikirim sebagai notif singkat **UPDATE PROSPEK**, bukan brief lengkap. Kalau tidak ada yang baru, tidak ada notif.
- Tidak ada kolom sheet atau node baru.

**Sudah lolos:** UAT **885/0** · eval model DeepSeek asli, 7 skenario (v3.12 ×1, v3.13 ×3). Keluaran modelnya juga diputar ulang lewat kode final, dan hasilnya 0 balasan yang berubah.

| | v3.12 (live) | v3.13 |
|---|---|---|
| Harga VIRA disebut tanpa diminta | 1 (persis kasus Rehan) | **0** |
| "kpn bs ngmng sm steven?" → disambungkan (bot OFF) | 0/1 | **3/3** |
| Balasan handover mengonfirmasi (tanpa "mau aku sambungkan?") | – | **3/3** |
| Nama usaha tercatat benar | 5/6 | **18/18** |
| STATS Rehan (nama_bisnis · industri) | sewa raket padel · persewaan aja | **kosong · sewa raket padel** (3/3) |
| Median kata per balasan | 12 | 12 |

## Langkah

1. Buka workflow live **VIRA Personal — Main** (ID `AC65HeFegHFCFc5aY609u`). Ganti isinya dengan `workflow/2026-09-23-VIRA-Personal-Main-v3.13.json` dengan cara yang sama seperti v3.12 kemarin, supaya ID dan settings tetap.
2. Save, lalu pastikan tidak ada node ganda berakhiran angka (mis. `Process All1`). Jumlah node harus 91.
3. Cek node yang memakai credential (Google Sheets, DeepSeek). Kalau ada yang merah, pilih lagi credential yang sama.
4. Pastikan workflow tetap **Active**. Setelah itu kabari aku, nanti aku cocokkan lewat MCP.

## Uji (±10 menit, nomor uji)

1. Hapus baris STATS nomor uji. Kirim `Halo VIRA, aku lihat website-nya...`, lalu `rehan` dan `usahaku sewa raket padel`. VIRA harus menanyakan **nama usaha**. Di STATS, industri = sewa raket padel dan nama_bisnis kosong.
2. Sampai VIRA menanyakan langkah dari chat sampai jadi sewa, jawab `harga dulu, trs klo udah aman baru ke payment`. Balasannya **tanpa** Basic/Premium/Rp.
3. Tanya `harganya berapa kak?`. Kisaran Basic/Premium **tetap** disebut lengkap.
4. Minta deck, kirim decknya (kirim_deck.py), lalu jawab `basic deh`. WA admin menerima notif singkat **UPDATE PROSPEK — deck sudah terkirim** (Minat paket: Basic).
5. Kirim `kpn bs ngmng sm steven?`. VIRA membalas "Siap kak, sudah aku sambungkan ke Steven…", WA admin menerima **PROSPEK MINTA DISAMBUNGKAN**, dan STATS bot_mode = OFF. Kembalikan bot_mode = ON sesudah uji.

## Kalau bermasalah

Ganti lagi isi workflow dengan `2026-09-23-VIRA-Personal-Main-v3.12.json`. Tidak ada data yang perlu dikembalikan.

## Sesudah uji

Hapus workflow **VIRA Eval — Balasan (sementara, hapus sesudah uji)**.
