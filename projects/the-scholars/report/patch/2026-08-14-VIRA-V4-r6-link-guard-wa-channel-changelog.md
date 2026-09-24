# VIRA V4 — r6: balasan link-ditutup mengarahkan ke WhatsApp Channel

**File:** `2026-08-14-VIRA-V4-r6-link-guard-wa-channel.json`
**Basis:** `2026-08-13-VIRA-V4-r5-link-guard.json` (kumulatif — memuat r1–r5)
**Node yang berubah:** `Process All` saja (549 → 571 baris). Sejak r4, **hanya node ini** yang pernah disentuh; 52 node lain dan seluruh `connections` identik byte-per-byte.
**systemMessage: TIDAK diubah sama sekali** — identik byte-per-byte dengan r4, diverifikasi di QA.

---

## Kasus pemicu

Catatan Sam ke Steven, 13 Agustus 2026:

> Iya betul, untuk sekarang, Batch 5 sudah tutup. Terus Seniors juga sudah tutup ya. Mungkin bisa di-redirect untuk join channel WA ku saja.

Balasan penolakan link di r5 mengarahkan user ke Sam, bukan ke WhatsApp Channel:

> Untuk linknya saya belum bisa kasih yaa, pendaftarannya lagi tidak dibuka. Kalau mau tanya-tanya lebih lanjut, bisa ngobrol langsung sama Sam yaa, tinggal ketik "mau ngomong sama Sam".

Keputusan Steven: tawarkan **WhatsApp Channel + tetap sediakan opsi ngomong sama Sam**. Menutup total jalur ke Sam berisiko kehilangan calon murid yang niatnya sudah serius.

---

## Isi perubahan

### Balasan dibangun dari data, bukan dihardcode

`LINK_CLOSED_REPLY` (const statis) diganti `buildClosedReply(txt)`. URL channel dicari dari tab LINKS — baris aktif yang URL-nya `whatsapp.com/channel/` atau `chat.whatsapp.com/`, atau yang `Nama Link`-nya mengandung "channel".

Konsekuensinya: kalau Sam mengganti channel atau menonaktifkan barisnya di LINKS, balasan ini ikut menyesuaikan tanpa perlu mengubah kode. URL channel tidak pernah muncul sebagai literal di dalam kode — diverifikasi di QA.

**Balasan penuh** (WhatsApp Channel aktif di LINKS):

```
Untuk sekarang pendaftarannya lagi ditutup yaa. Boleh join WhatsApp Channel-nya
dulu, nanti info batch berikutnya saya share di sana:

👉 https://whatsapp.com/channel/0029Vb7vhDZ9MF9Anr7LcT1P

Kalau mau tanya-tanya lebih lanjut, tinggal ketik "mau ngomong sama Sam".
```

**Balasan pendek** — dipakai kalau baris WhatsApp Channel tidak ada / tidak aktif, **atau** kalau link channel-nya kebetulan sudah disebut di balasan itu (supaya user tidak menerima URL yang sama dua kali):

```
Untuk sekarang pendaftarannya lagi ditutup yaa. Kalau mau tanya-tanya lebih
lanjut, tinggal ketik "mau ngomong sama Sam".
```

**Balasan saat tab LINKS gagal terbaca** — tidak berubah dari r5. Guard tetap *fail closed*, tapi tidak boleh memakai kalimat "lagi ditutup" karena itu jadi kebohongan padahal penyebabnya gangguan teknis:

```
Untuk linknya saya cek dulu yaa. Kalau mau lebih cepat, bisa ngobrol langsung
sama Sam, tinggal ketik "mau ngomong sama Sam".
```

### Kenapa tidak lewat systemMessage

Steven: systemMessage sudah bloated, jangan ditambah. Perubahan ini murni di `Process All` dan tidak menambah satu baris pun di prompt. Aturan yang dibutuhkan sebenarnya sudah ada di systemMessage r4 untuk kasus `PENDAFTARAN SUDAH DITUTUP`:

> Boleh tawarkan guidebook atau WhatsApp Channel untuk info batch berikutnya.

Jadi r6 hanya menyelaraskan balasan deterministik dengan aturan yang sudah tertulis — bukan menambah aturan baru.

---

## Hasil QA

`qa_r6.py` — **34 assertion, TOTAL GAGAL: 0**

| Bagian | Cakupan |
|---|---|
| A. Struktur | 53 node utuh, `connections` byte-identik r4, hanya `Process All` berubah, **systemMessage identik byte-per-byte dengan r4** |
| B. Sintaks | `Process All` parse bersih, tidak ada error baru vs r4, tidak ada sisa referensi const lama, URL channel tidak dihardcode |
| C. Port logika | Kasus asli tinyurl, skenario Sam (Batch 5 + Seniors di-`Closed`), link aktif tetap lolos, anti-URL-dobel, WA Channel dinonaktifkan, LINKS gagal baca, output tanpa URL, IG post |

Skenario Sam diuji dengan menyalin data LINKS asli lalu men-set semua baris `pendaftaran` jadi `Closed` — persis kondisi setelah adjustment B1–B2 dikerjakan.

**Batasan yang sama seperti sebelumnya:** tidak ada Node.js/Deno/Bun di mesin ini. Kode belum pernah dieksekusi sebagai JavaScript. Validasi = parser `esprima` + port logika 1:1 ke Python terhadap data LINKS asli.

---

## Uji setelah import ke n8n

Jalankan **setelah** adjustment A1–A3 dan B1–B2 dikerjakan di Google Sheet.

| Kirim ke VIRA | Harapan |
|---|---|
| `mau daftar batch 5` | Batch 5 sudah ditutup, tanpa link pendaftaran, ditawari join WhatsApp Channel |
| `anak saya kelas 12 mau daftar seniors` | Seniors sudah ditutup, tanpa link, ditawari WhatsApp Channel |
| `mau yg intensive class` | Tanpa URL tinyurl, ditawari WhatsApp Channel |
| `boleh minta link whatsapp channel?` | Link channel terkirim sekali, **tidak dobel** |
| `info beasiswa` | Link Guidebook tetap terkirim (status `Active`) |

---

## Rollback

`report/production/2026-08-08-VIRA-V4-retryable.json` — basis produksi, tidak pernah disentuh.
