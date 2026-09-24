# FAQ Booking Fee — Fixes (#1 & #2)

**Dibuat**: 2026-07-23
**Sumber**: temuan QA `test chat vira.txt` (#1 "rugi", #2 "bayar 1jt lagi untuk saudara")
**Target**: tab **FAQ** di Google Sheet live (spreadsheet `1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o`).
**Catatan**: file `PCR_Database.xlsx` lokal **tidak ditimpa** (menghindari kerusakan format/gambar sheet lain). Terapkan perubahan berikut langsung di Google Sheet.

> ⚠️ Bug laten #17F: `FAQ Retrieve` mem-boost kategori yang tidak match nama riil → boost tidak aktif. Jadi retrieval bergantung pada **teks Pertanyaan**, bukan Kategori. Pertanyaan di bawah sudah dibuat kaya keyword ("BI Checking", "hangus", "saudara").

> 🔒 **JANGAN** memasukkan disclaimer internal (BI Checking sebenarnya gratis / Rp1jt = pengikat keseriusan) ke sheet manapun. Semua isi FAQ diinject mentah ke prompt dan bisa keluar verbatim ke calon pembeli. Teks di bawah sudah versi customer-facing saja.

---

## Perubahan 1 — EDIT cell B82 (ganti isi lama)

**Cell B82 (Jawaban)** — ganti dengan:

> Iya betul kak, untuk komersial DP-nya nol rupiah, jadi tidak perlu bayar uang muka di awal. Yang dibayar di awal hanya Rp1 juta untuk BI Checking. Kalau BI Checking tidak lolos, Rp1 juta itu dikembalikan penuh — tidak ada yang hangus. Kalau lolos, lanjut pelunasan Rp1,5 juta sebagai booking fee (total Rp2,5 juta).

**Cell C82 (Kategori)** — isi: `Booking` (sebelumnya kosong)

*Alasan: versi lama hanya menyebut "apabila lolos lanjut pelunasan 1,5 juta" tanpa klausa refund → memperkuat sisi ambigu yang bikin Vira ngomong "rugi".*

---

## Perubahan 2 — APPEND row 83 & 84 (baris baru)

Paste 2 baris berikut ke bawah row 82 (kolom A / B / C). TSV siap-paste:

```tsv
Kalau BI Checking saya jelek atau tidak lolos, uang Rp1 juta hangus?	Tenang kak, kalau BI Checking tidak lolos, uang Rp1 juta untuk BI Checking dikembalikan penuh — jadi tidak ada yang hangus. Uang Rp1,5 juta untuk booking fee baru dibayar kalau BI Checking lolos. Jadi di awal Kakak tidak menanggung risiko kehilangan uang.	Penanganan Keberatan
Kalau mau pakai data saudara untuk BI Checking, bayar Rp1 juta lagi?	Tidak perlu bayar lagi kak. Uang Rp1 juta yang sudah dibayar tidak hangus dan tetap di-hold untuk melanjutkan proses cek data dengan data pemohon lain (misalnya saudara atau beda KK). Jadi tidak ada biaya tambahan, tinggal lanjut prosesnya. Kalau lolos, tinggal tambah Rp1,5 juta untuk booking fee (total Rp2,5 juta).	Booking
```

- **Row 83** → menjawab langsung objection #1 ("jelek/tidak lolos → hangus?").
- **Row 84** → menutup data gap #2 (pakai data saudara → tidak bayar lagi, dana di-hold).

---

## Verifikasi setelah apply

Uji di WA (atau simulasi):
1. "Kalau BI Checking saya jelek, uang saya hilang?" → Vira jawab **dikembalikan penuh, tidak hangus** (bukan "rugi").
2. "Bayar 1 juta lagi kalau pakai data saudara?" → Vira jawab **tidak bayar lagi, dana di-hold**.

Kedua fix ini melengkapi editan H2/H3 di sheet PRODUK yang sudah benar.
