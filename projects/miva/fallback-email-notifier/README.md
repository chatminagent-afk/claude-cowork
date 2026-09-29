# Email Fallback untuk Error Notifier VIRA

Kalau API WhatsApp Kirimi mati, error notifier ikut gagal kirim — errornya hilang tanpa jejak. Folder ini menambahkan jalur cadangan lewat email, provider berbeda, supaya kegagalan keduanya tidak berkorelasi.

Berlaku untuk 2 workflow: **VIRA-PCR Error Notifier** (Persada) dan **VIRA Error Notifier** (The Scholars).

| File | Fungsi |
|---|---|
| `2026-08-03-email-fallback-workflow.json` | Bagian A — import sebagai workflow baru |
| `2026-08-03-email-fallback-patch-notifier.json` | Bagian B — paste ke canvas kedua notifier |
| `arsip/` | Versi lama, abaikan |

Total waktu ±25 menit. Bagian A sekali saja, Bagian B diulang 2x (PCR dan Scholars).

---

# BAGIAN A — Workflow email (sekali saja)

Node pengirim defaultnya **Gmail**. Kalau OAuth-nya terasa ribet, ada 3 alternatif di bagian [Ganti pengirim](#ganti-pengirim) — paling cepat SMTP App Password (5 menit, akun yang sama, tanpa Google Cloud).

## A1. Bikin OAuth client di Google Cloud

Login ke Google Cloud Console **sebagai `chatminagent@gmail.com`**.

1. **console.cloud.google.com** → dropdown project kiri atas → **New Project**
   - Name: `n8n VIRA Alert` → Create
2. Pastikan project itu terpilih. Search bar → **Gmail API** → **Enable**
3. Menu kiri → **APIs & Services → OAuth consent screen**
   - User Type: **External** → Create
   - App name: `n8n VIRA Alert`
   - User support email: `chatminagent@gmail.com`
   - Developer contact: `chatminagent@gmail.com`
   - Save and Continue → Scopes: **Save and Continue** (lewati, n8n minta scope sendiri)
   - Test users: **Add Users** → `chatminagent@gmail.com` → Save and Continue
4. Menu kiri → **Credentials** → **Create Credentials** → **OAuth client ID**
   - Application type: **Web application**
   - Name: `n8n`
   - **Authorized redirect URIs** → Add URI → *(diisi di langkah A2, jangan ditutup dulu)*

## A2. Sambungkan ke n8n

1. Di n8n: menu kiri **Credentials** → **Add credential** → cari **Gmail OAuth2 API**
2. Di halaman kredensial itu ada baris **OAuth Redirect URL** — klik ikon copy.
   Bentuknya `https://n8n-mu.com/rest/oauth2-credential/callback`
3. Balik ke tab Google Cloud → paste ke **Authorized redirect URIs** → **Create**
4. Muncul popup berisi **Client ID** dan **Client Secret** → copy keduanya ke field yang sama di n8n
5. Klik **Sign in with Google** → login sebagai `chatminagent@gmail.com`
6. Muncul layar **"Google hasn't verified this app"** → **Advanced** → **Go to n8n VIRA Alert (unsafe)** → **Allow**

   Warning ini normal untuk app yang tidak diverifikasi Google. Aman karena app-nya kamu sendiri dan cuma dipakai akunmu sendiri.
7. Kredensial berubah jadi **Connected** → beri nama `Gmail chatminagent` → **Save**
8. Balik ke workflow → **double-click** node **Kirim Email (Gmail)** → field **Credential to connect with** → pilih `Gmail chatminagent` → **Back to canvas**

## A2b. ⚠️ PUBLISH APP — jangan dilewati

Ini satu-satunya jebakan serius di jalur Gmail.

1. Google Cloud → **APIs & Services → OAuth consent screen**
2. Status sekarang **Testing** → klik **PUBLISH APP** → **Confirm**
3. Status berubah jadi **In production**

**Kenapa wajib:** selama statusnya *Testing*, Google mematikan refresh token tiap **7 hari**. Artinya seminggu setelah setup, jalur alert ini mati — dan karena ini jalur cadangan yang jarang dipakai, kamu baru sadar justru pada saat paling butuh. Setelah *In production*, token tidak kedaluwarsa sendiri.

Tidak perlu proses verifikasi Google. Layar warning "unverified app" tetap muncul kalau nanti connect ulang, dan itu tidak masalah.

## A3. Isi URL n8n

1. **Double-click** node **Normalize & Compose Email**
2. Di baris ke-11 ada:
   ```js
   const N8N_BASE = 'https://GANTI-DENGAN-URL-N8N-KAMU';
   ```
3. Ganti dengan URL n8n kamu — ambil dari address bar browser, bagian **sebelum** `/workflow/`.
   Contoh kalau address bar-mu `https://n8n.contoh.com/workflow/abc123`, maka isinya:
   ```js
   const N8N_BASE = 'https://n8n.contoh.com';
   ```
   **Tanpa garis miring di akhir.** Ini yang bikin tombol link di email bisa diklik.
4. **Back to canvas**

## A4. Save & catat workflow ID

1. Tekan **Ctrl+S** (atau tombol **Save** kanan atas)
2. Lihat address bar: `https://n8n-mu.com/workflow/`**`Xk9mPqR2sT4vW7yZ`**
3. **Catat bagian tebal itu** — dipakai di Bagian B

Workflow ini **tidak perlu di-Activate**. Toggle Active biarkan mati.

## A5. Tes sekarang

Klik tombol oranye **Execute workflow from Error Trigger (lapis 2)** di bawah.

Cek inbox `stevenleroy0@gmail.com` (termasuk folder Spam untuk email pertama). Harus masuk email berjudul:

```
🚨 [VIRA-?] WA ALERT GAGAL TERKIRIM - ...
```

Isinya akan banyak tanda `-` dan `(tidak tersedia)`. **Itu normal** — Error Trigger yang dijalankan manual tidak punya data error asli. Yang penting emailnya sampai; artinya jalur email sudah hidup.

**Kalau gagal:**

| Yang terlihat | Sebab | Perbaikan |
|---|---|---|
| `invalid_client` saat Sign in with Google | Client ID/Secret salah copy | Ulangi A2 langkah 4 |
| `redirect_uri_mismatch` | URI di Google Cloud beda dengan punya n8n | Copy ulang persis dari halaman kredensial n8n, termasuk `https://` |
| `Gmail API has not been used in project...` | Gmail API belum di-enable | A1 langkah 2 |
| `invalid_grant` / `Token has been expired or revoked` | Status OAuth masih *Testing*, token mati 7 hari | Kerjakan **A2b**, lalu connect ulang kredensialnya |
| Node hijau tapi email tidak masuk | Nyangkut spam | Cek Spam, tandai Not Spam |
| Error `No item to return` | — | Lewati saja, tes beneran ada di Bagian B |

---

# BAGIAN B — Patch notifier (ulangi 2x)

Lakukan untuk **VIRA-PCR Error Notifier** dulu, lalu ulangi persis sama untuk **VIRA Error Notifier** (The Scholars).

## B1. Paste node-nya

1. Buka file `2026-08-03-email-fallback-patch-notifier.json` pakai Notepad
2. **Ctrl+A** lalu **Ctrl+C** (copy seluruh isi file)
3. Buka workflow **VIRA-PCR Error Notifier** di n8n
4. **Klik area kosong** di canvas, lalu **Ctrl+V**

Muncul 3 node baru + 1 sticky note kuning. Belum tersambung ke apa-apa — itu memang sengaja.

## B2. Aktifkan error output di node Kirimi

1. **Double-click** node **Notify Admin Error**
2. Tab **Settings** (di dalam node, sebelah tab Parameters)
3. **On Error** → pilih **Continue (using error output)**
4. Sekalian di tab Settings yang sama: **Retry On Fail** → **on**, Max Tries `2`, Wait Between Tries `2000`
5. **Back to canvas**

Sekarang node **Notify Admin Error** punya **2 titik output** di sisi kanan — atas (abu-abu, sukses) dan bawah (merah, error).

## B3. Sambungkan 3 garis

Tarik garis dengan cara **klik-tahan titik output**, lalu **lepas di titik input** (sisi kiri) node tujuan.

| Dari | Ke |
|---|---|
| `Notify Admin Error` output **atas** (abu-abu) | `Check Kirimi Response` |
| `Notify Admin Error` output **bawah** (merah) | `Build Fallback Payload` |
| `Check Kirimi Response` output **bawah** (merah) | `Build Fallback Payload` |

Output **atas** milik `Check Kirimi Response` sengaja **dibiarkan kosong** — itu jalur "WA berhasil terkirim, selesai".

Kalau benar, hasilnya:

```
Compose Notif ──► Notify Admin Error ──┬─(abu)──► Check Kirimi Response ──┬─(abu)──► (kosong)
                                       │                                  │
                                       └─(merah)──────┐    ┌───(merah)────┘
                                                      ▼    ▼
                                            Build Fallback Payload ──► Call Global Email Fallback
```

## B4. Set TENANT

1. **Double-click** node **Build Fallback Payload**
2. Baris ke-8:
   ```js
   const TENANT = 'VIRA-PCR';
   ```
   - Workflow PCR → biarkan `'VIRA-PCR'`
   - Workflow The Scholars → ganti jadi `'VIRA-SCHOLARS'`
3. **Back to canvas**

## B5. Sambungkan ke workflow email

1. **Double-click** node **Call Global Email Fallback**
2. Field **Workflow** → klik dropdown kecil di sebelah kiri field (tulisannya `By ID`) → ganti ke **From list**
3. Pilih **GLOBAL - Email Fallback Notifier**

   Kalau tidak muncul di list, balik ke **By ID** dan paste workflow ID dari langkah A4.
4. **Back to canvas**

## B6. Set Error Workflow (lapis kedua)

1. Klik **titik tiga (⋯)** di kanan atas, sebelah tombol Save
2. Pilih **Settings**
3. **Error Workflow** → pilih **GLOBAL - Email Fallback Notifier**
4. **Save**

## B7. Save & ulangi

**Ctrl+S**. Lalu ulangi B1–B7 untuk **VIRA Error Notifier** (The Scholars), dengan `TENANT = 'VIRA-SCHOLARS'` di langkah B4.

---

# Tes beneran

Setelah kedua notifier dipatch:

**Tes 1 — Kirimi mati total**
1. Buka `VIRA-PCR Error Notifier` → node **Notify Admin Error**
2. Ubah URL jadi `https://api.kirimi.id/v1/send-message-ngasal` → Save
3. Picu error di workflow Main (cara paling gampang: rename tab Google Sheet `STATS` sebentar, kirim pesan WA ke bot, lalu balikin namanya)
4. Email harus masuk — kali ini **isinya lengkap**: teks WA yang gagal terkirim, error aslinya, dan tombol link ke execution
5. **Kembalikan URL node Kirimi**

**Tes 2 — Kirimi balas 200 tapi gagal**
Ubah `phone` di node Kirimi jadi `628000000000` → picu error → email harus tetap masuk, lewat `Check Kirimi Response`. Kembalikan nomornya setelah selesai.

**Tes 3 — lapis 2 (opsional)**
Tambah `throw new Error('tes');` di baris pertama node `Compose Notif` → picu error.
Email masuk = versi n8n-mu tidak kena loop-guard, lapis 2 aktif (bonus).
Email tidak masuk = wajar dan sudah diperkirakan, lapis 1 tetap jalan.
Hapus baris tes setelahnya.

---

# Kenapa notifier WA ikut diubah?

Mengandalkan fitur "Error Workflow" n8n saja meninggalkan 2 lubang:

**1. Kirimi bisa gagal tanpa terlihat gagal.** Kalau Kirimi balas HTTP 200 tapi isinya `status: false` (device disconnect, nomor salah, kuota habis), n8n menganggap eksekusinya **sukses**. Tidak ada error → Error Workflow tidak jalan → tidak ada email sama sekali. Ini mode kegagalan paling sunyi, dan yang menangkapnya cuma node `Check Kirimi Response` di Bagian B.

**2. Error Workflow belum tentu jalan untuk workflow yang statusnya sendiri `error`.** Sebagian versi n8n punya loop-guard. Kalau instance-mu kena, seluruh jalur cadangan mati diam-diam.

Bonus: lewat Bagian B, email membawa konteks lengkap — teks WA yang gagal, error aslinya, link execution. Tanpa itu, email cuma bilang "notifier gagal".

Versi paling minimal kalau mau cepat: Bagian A + langkah B6 saja. Menutup kasus Kirimi mati total, tapi lubang nomor 1 tetap terbuka.

---

# Keputusan: satu sender saja

Pengirim `chatminagent@gmail.com` → penerima `stevenleroy0@gmail.com`. Pembeda klien lewat tag di subject: `🚨 [VIRA-PCR]` / `🚨 [VIRA-SCHOLARS]`.

Tidak perlu login `hiduppersada@gmail.com` maupun `thescholarsid@gmail.com`. Ini alert internal, tidak ada yang melihat sender-nya, dan tiap kredensial tambahan cuma menambah titik gagal di jalur yang justru harus paling andal.

<a id="ganti-pengirim"></a>

## Ganti pengirim

Di workflow email ada 3 node cadangan yang nonaktif. Semua memakai output yang sama (`subject`, `html`, `text`), jadi cara tukarnya: sambungkan `Normalize & Compose Email` → node pilihan, enable node itu (klik kanan → **Activate**), lalu matikan node Gmail.

| Node | Setup | Kelebihan | Kekurangan |
|---|---|---|---|
| **Gmail** (aktif) | OAuth2 via Google Cloud, ±20 menit | Akun sendiri, tanpa pihak ketiga | Wajib Publish App, kalau lupa token mati tiap 7 hari |
| **SMTP** | App Password Gmail, ±5 menit | Paling cepat, akun sama, tanpa Google Cloud | 2FA harus aktif; sebagian hosting blokir port 465 |
| **Resend** | Daftar + copy API key, ±5 menit | API key tidak pernah expired | Pihak ketiga; tanpa domain hanya bisa kirim ke email pemilik akun |
| **Brevo** | Verifikasi sender lewat klik link | Sender tetap `chatminagent@`, bebas penerima | Pihak ketiga; batas 300 email/hari |

Kalau OAuth Gmail bermasalah, **SMTP adalah jalan tercepat** dan tetap memakai akun `chatminagent@gmail.com` yang sama:
Host `smtp.gmail.com`, port `465`, SSL on, user `chatminagent@gmail.com`, password = **App Password** 16 karakter (bukan password Gmail biasa; butuh 2FA aktif dulu di akun itu). Kalau timeout, coba port `587` dengan SSL off.

---

# Yang masih belum tertutup

Kalau **instance n8n-nya sendiri mati**, tidak ada jalur ini yang jalan — WA maupun email. Perlu monitor dari luar (UptimeRobot / BetterStack ping ke n8n). Belum dikerjakan.

Sekunder: `user_code` dan `secret` Kirimi masih plaintext di body parameter kedua notifier. Sebaiknya dipindah ke n8n Credentials kapan-kapan.
