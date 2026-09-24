# VIRA V4 — r5: SAFETY NET LINK

**File:** `2026-08-13-VIRA-V4-r5-link-guard.json`
**Basis:** `2026-08-12-VIRA-V4-r4-status-batch.json` (kumulatif — semua perbaikan r1–r4 ikut di dalamnya)
**Node yang berubah:** `Process All` saja (420 → 549 baris). 52 node lain dan seluruh `connections` identik byte-per-byte dengan r4.

---

## Kasus pemicu

Chat produksi 12 Agustus 2026, 22:22–22:24 WIB:

> **Steven:** mau yg intensive class
> **VIRA:** Untuk intensive class UOB/CLI, bisa daftar di sini yaa: https://tinyurl.com/UOBCLIntensiveClass

Padahal di tab `LINKS` baris 7, link Intensive Class sudah di-`Closed` oleh Steven.

### Kenapa lolos

Ada **dua jalur link** di VIRA, dan hanya satu yang dijaga:

| Jalur | Sumber URL | Penjagaan sebelum r5 |
|---|---|---|
| `[SEND_GFORM: <Nama Link>]` | tab LINKS | ✅ difilter kolom `Status` |
| URL mentah di teks jawaban AI | teks FAQ | ❌ tidak ada sama sekali |

URL yang terkirim (`tinyurl.com/UOBCLIntensiveClass`) **tidak ada di tab LINKS**. Asalnya dari teks jawaban FAQ baris 104. Di LINKS, Intensive Class URL-nya `forms.gle/3qoC6vWVkS39Hskr7` — URL yang berbeda. Jadi status `Closed` yang diset Steven memang bekerja, tapi tidak pernah kebagian giliran memeriksa.

Lebih buruk lagi: `Process All` justru **melindungi** URL. Sebelum pembersihan markdown, semua `https?://...` di-mask jadi placeholder, lalu dikembalikan utuh — tidak pernah divalidasi.

Total ada **7 baris FAQ** yang menyimpan URL mentah: 14, 15, 45, 46, 48, 100, 104.

---

## Isi perubahan

### 1. Blok `SAFETY NET LINK` (baru)

Ditempatkan **sesudah** safety net transfer dan **sebelum** injeksi `[SEND_GFORM]`, supaya link sah yang disisipkan sistem tidak ikut tersaring.

Aturannya: sebuah URL boleh keluar **hanya kalau** URL itu ada di tab LINKS **dan** statusnya aktif. Selain itu dibuang.

- `isLinkActive(status)` — memeriksa CLOSED dulu baru ACTIVE. Urutan ini wajib: `"Nonaktif"` mengandung kata `"aktif"`, kalau ACTIVE dicek duluan baris nonaktif salah terbaca sebagai aktif.
- `normUrl()` — menyamakan bentuk URL sebelum dibandingkan (huruf kecil, buang tanda baca penutup dan slash akhir), supaya `…FnML6.` dan `…FnML6/` tetap dikenali sama dengan yang di sheet.
- Pembuangan bersifat **per kalimat**, mengikuti pola safety net transfer yang sudah terbukti: kalimat yang memuat URL terlarang dibuang, kalimat informatif lain dipertahankan.
- Baris pengantar yang menggantung (`"…daftar di sini yaa:"` tanpa link di bawahnya) ikut dibuang.
- Fallback run pertama (`ref.all(0, 0)`) dipakai saat membaca `Read LINKS Data`, sama seperti `grab()` di `FAQ Retrieve`. Tanpa ini, node ber-`executeOnce` yang kosong di run kedua (debounce) akan membuat guard memblokir link yang sebenarnya sah.

### 2. Balasan pengganti

Keputusan Steven: kalau link ditolak, VIRA jujur bilang belum bisa memberi link karena pendaftarannya sedang tidak dibuka, lalu mengarahkan ke Sam.

```
Untuk linknya saya belum bisa kasih yaa, pendaftarannya lagi tidak dibuka.
Kalau mau tanya-tanya lebih lanjut, bisa ngobrol langsung sama Sam yaa,
tinggal ketik "mau ngomong sama Sam".
```

Ada balasan kedua khusus saat **tab LINKS gagal terbaca**. Guard sengaja *fail closed* — semua URL diblokir — tapi tidak boleh memakai kalimat di atas, karena "pendaftarannya tidak dibuka" akan jadi kebohongan padahal penyebabnya gangguan teknis:

```
Untuk linknya saya cek dulu yaa. Kalau mau lebih cepat, bisa ngobrol
langsung sama Sam, tinggal ketik "mau ngomong sama Sam".
```

### 3. Supresi fallback `[SEND_GFORM]`

Teks FAQ baris 104 memuat frasa `"link pendaftarannya"`, yang memicu deteksi cadangan di `Process All` baris 31–54 → `isSendGForm = true` tanpa nama link. Tanpa perbaikan ini, alurnya jadi: URL intensive class diblokir, lalu sistem menyisipkan link **pendaftaran Batch 5** sebagai default — mengganti link yang ditolak dengan link lain yang sama sekali tidak diminta user.

Sekarang: kalau ada URL yang diblokir **dan** AI tidak menyebut nama link secara eksplisit, fallback dimatikan. Kalau AI menyebut nama link eksplisit (mis. `[SEND_GFORM: GForm Pendaftaran Seniors]`), resolusi normal tetap jalan dan tetap disaring status aktif.

### 4. Balasan saat link diminta tapi tidak aktif

Cabang `else` pada resolusi `[SEND_GFORM]` dulu hanya menulis `console.warn` lalu diam. Akibatnya user yang minta link Intensive Class tidak dapat link **dan** tidak dapat penjelasan. Sekarang balasan penolakan ikut ditambahkan.

### 5. Filter status disamakan

Filter lama `/aktif|active|on|ya/i` di resolusi `[SEND_GFORM]` diganti `isLinkActive()` supaya konsisten dengan gerbang baru. Filter lama meloloskan `"Nonaktif"`.

### 6. Field diagnostik

`linkBlocked` dan `blockedUrls` ikut dikembalikan di output node, supaya kalau ada link yang salah terblokir penyebabnya kelihatan tanpa menebak.

---

## Hasil QA

`qa_r5.py` — **54 assertion, TOTAL GAGAL: 0**

| Bagian | Cakupan |
|---|---|
| A. Struktur | 53 node utuh, nama identik, `connections` byte-per-byte sama, hanya `Process All` yang berubah |
| B. Sintaks | `Process All` parse bersih; tidak ada error sintaks baru dibanding r4 |
| C. Port logika | Kasus asli tinyurl, link `Closed`, 3 link aktif harus lolos, URL tak terdaftar, normalisasi tanda baca, pengantar menggantung, output tanpa URL, LINKS gagal baca, nama link eksplisit |

**Batasan yang harus diketahui:**

- Tidak ada Node.js/Deno/Bun di mesin ini. Kode belum pernah dieksekusi sebagai JavaScript. Validasi = parser `esprima` + port logika 1:1 ke Python.
- `FAQ Retrieve` tidak bisa diparse esprima karena memakai `\p{L}`/`\p{N}` (Unicode property escape, ES2018) yang tidak didukung esprima 4. Kode itu warisan produksi, tidak disentuh r5, dan sudah berjalan di n8n.

---

## Uji setelah import ke n8n

| Kirim ke VIRA | Harapan |
|---|---|
| `mau yg intensive class` | Tidak ada URL. Balasan "belum bisa kasih link, pendaftarannya lagi tidak dibuka" + arahan ke Sam |
| `boleh minta link whatsapp channel?` | Link WA Channel tetap terkirim (status `Active`) |
| `anak saya kelas 12, mau daftar` | Link GForm Seniors tetap terkirim |
| `info beasiswa` | Link Guidebook tetap terkirim |
| `batch 4 isinya apa?` | Link IG post **hilang** (tidak terdaftar di LINKS) — lihat catatan di bawah |

---

## Yang masih perlu dikerjakan Sam di Google Sheet

r5 menutup jalur keluarnya, tapi sumbernya masih kotor. Prioritas:

| Row FAQ | URL | Status di LINKS | Tindakan |
|---|---|---|---|
| **104** | `tinyurl.com/UOBCLIntensiveClass` | tidak terdaftar | **Hapus URL + kalimat pengantarnya** |
| **46** | `instagram.com/p/DWLCeFhga8x/…` | tidak terdaftar | Hapus URL, **atau** daftarkan ke LINKS kalau memang mau dipakai. Isinya juga sudah basi (Batch 4, mulai 18 April) |
| 14 | `forms.gle/mKZ…` | GForm Pendaftaran Seniors (`Active`) | Ganti jadi `[SEND_GFORM: GForm Pendaftaran Seniors]` |
| 48 | `forms.gle/mKZ…` | sama | Ganti jadi `[SEND_GFORM: GForm Pendaftaran Seniors]` |
| 15 | `drive.google.com/file/d/1fFP…` | Guidebook (`Active`) | Ganti jadi `[SEND_GFORM: Guidebook]` |
| 45 | `drive.google.com/file/d/1fFP…` | Guidebook (`Active`) | Ganti jadi `[SEND_GFORM: Guidebook]` |
| 100 | `whatsapp.com/channel/0029…` | WhatsApp Channel (`Active`) | Ganti jadi `[SEND_GFORM: WhatsApp Channel]` |

Baris 14, 15, 45, 48, 100 aman dilewatkan r5 karena URL-nya cocok dengan LINKS yang aktif — tapi selama URL-nya dihardcode di FAQ, setiap kali Sam mengganti URL di LINKS, FAQ harus diedit juga. Mengganti dengan tag membuat tab LINKS benar-benar jadi satu-satunya tempat mengatur link.

---

## Rollback

`report/production/2026-08-08-VIRA-V4-retryable.json` — basis produksi, tidak pernah disentuh.
