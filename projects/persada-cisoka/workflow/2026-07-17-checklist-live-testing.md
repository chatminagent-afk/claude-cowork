# Checklist Live Testing — VIRA Persada Cisoka Residence (2026-07-17)

Urutan kerja dari nol sampai bot bisa dites langsung via WhatsApp. Referensi detail: `2026-07-15-README-deploy.md` (arsip 07-15). File aktif yang dipakai semuanya versi **2026-07-17**.

---

## A. Excel → Google Sheets

1. **Upload** `2026-07-17-Persada-Cisoka-Database.xlsx` ke Google Drive.
2. **Konversi ke Google Sheet native**: buka file → File → *Save as Google Sheets*. (Node n8n tidak bisa baca .xlsx langsung — harus Sheet native.) Beri nama `Persada_Cisoka_Database`.
3. **Salin Sheet ID** dari URL: `https://docs.google.com/spreadsheets/d/`**`<SHEET_ID>`**`/edit`.
4. **Share** sheet ke email service account Google (role **Editor**) — service account yang sama dengan yang dipakai credential n8n.
5. **Isi 3 key CONFIG** yang masih `(ISI: ...)`:
   - `kirimi_user_code`, `kirimi_secret`, `kirimi_device_id` → nilai asli Kirimi PCR.
   - ⚠️ `kirimi_secret` SENSITIF — jangan share sheet ini ke orang di luar tim inti.
6. **Cek tab LINKS**: baris `video` + `foto` sudah AKTIF dengan URL `uc?export=download&id=...` (sudah terverifikasi bisa diunduh publik). Pastikan file Drive-nya tetap "Anyone with the link".
7. (Opsional tapi disarankan sebelum demo ke klien) Isi sel `(ISI:)` di PRODUK — paling kritis **harga resmi subsidi 30/60**. Sel yang masih placeholder akan ikut terkirim ke konteks AI apa adanya.

## B. Import & Setup n8n

1. **Import 3 workflow** (Workflows → ⋯ → *Import from File*):
   - `2026-07-17-VIRA-PCR-main.json` (75 node)
   - `2026-07-17-VIRA-PCR-buffer-cleanup.json`
   - `2026-07-17-VIRA-PCR-error-notifier.json`
2. **Buat 3 credentials**:
   - **Kirimi Custom Auth** (Generic → Custom Auth): JSON body berisi `user_code`, `secret`, `device_id`. Assign ke semua node HTTP Kirimi **teks/notifikasi** (Reply Chat Kirimi, Notify Talk to Admin, Notify Field Team, Notify Admin Unknown, Notify Admin API Error, Notify Admin Media Error, Notify User Error, Reply Error, + Notify Admin Error di Error Notifier).
   - **Anthropic account PCR**: assign ke `Anthropic Chat Model` + `Anthropic Model Summarize`.
   - **Google Service Account PCR**: assign ke semua node Google Sheets (di Main + 2 node di Buffer Cleanup).
   - Semua node ber-placeholder `REPLACE_WITH_...` → klik node, pilih credential asli.
3. **PENTING — node `Send Media Kirimi`: JANGAN pasang credential** (authentication = None). Node ini kirim multipart `send-message-file` dan ambil kredensial dari tab CONFIG via Parse Config (custom-auth n8n tidak reliabel untuk multipart). Node `Download Media` juga tanpa credential.
4. **Isi Sheet ID**:
   - Main: buka node **Bootstrap Config** (Code) → ganti `PASTE_PCR_GOOGLE_SHEET_ID_HERE` dengan Sheet ID asli (satu-satunya titik edit di Main).
   - Buffer Cleanup: ganti `PASTE_PCR_GOOGLE_SHEET_ID_HERE` manual di 2 node Sheets (documentId).
5. **Set Error Workflow**: di VIRA-PCR Main → Settings → *Error Workflow* → pilih **VIRA-PCR Error Notifier**.
6. **Aktifkan** Main + Buffer Cleanup (cron). Salin **Production URL** node `Webhook` (path `/wa-inbound-pcr`).
7. **Daftarkan webhook di dashboard Kirimi**: tempel Production URL sebagai webhook incoming message device PCR (`D-...`).

## C. UAT Live via WhatsApp

Kirim dari nomor WA lain (bukan nomor device bot):

| # | Tes | Ekspektasi |
|---|-----|-----------|
| 1 | Kirim "halo" | Bot balas sebagai telemarketer Persada Cisoka |
| 2 | Tanya harga/spek (mis. "harga tipe 36/72?") | Jawaban sesuai data PRODUK, tidak mengarang |
| 3 | Minta "foto rumahnya dong" | **Foto tampil natural** (bukan dokumen dengan nama aneh) |
| 4 | Minta "ada video?" | Video terkirim playable |
| 5 | Tanya kavling/blok mana yang kosong | Bot arahkan survey dulu, TIDAK menjawab ketersediaan kavling |
| 6 | Kirim 2–3 pesan beruntun cepat | Satu balasan gabungan (debounce jalan, tidak dobel) |
| 7 | Minta media yang belum ada (mis. "denah") | Notifikasi manual masuk ke Aar + Aqsa (media_team_phone) |
| 8 | Minta bicara dengan orang / jadwalkan survey | Notif ke Om Sulianto (field_team_phone) / jalur HITL |
| 9 | (Negatif) Ubah URL `foto` di LINKS jadi URL mati → minta foto | Admin dapat **Notify Admin Media Error**; user dapat pesan fallback |
| 10 | Cek n8n → Executions | Tidak ada eksekusi merah; STATS/MSG_BUFFER/UNKNOWN terisi wajar |

Setelah tes #9, kembalikan URL `foto` ke URL asli.

## Catatan sisa

- Video dummy (`Video tipe 36 72 atau tipe 36 81.mp4`) perlu review isi + izin tim sebelum go-live.
- Jalur media belum ada cek `success:false` pada HTTP 200 (parity gap yang disengaja) — kalau Kirimi balas 200 tapi gagal, tidak masuk error branch. Pantau manual saat UAT.
- Gap data form zoom (stok, promo Juli 2026, dimensi 36/81, rekening resmi PT) masih menunggu jawaban tim.
