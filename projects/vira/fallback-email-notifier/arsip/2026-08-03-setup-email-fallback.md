# Email Fallback Notifier — Setup

**Masalah yang diselesaikan:** kalau API WhatsApp Kirimi mati, error notifier (`VIRA-PCR Error Notifier` dan `VIRA Error Notifier` / The Scholars) ikut gagal kirim — errornya hilang, tidak ada yang tahu.

**Solusi:** satu workflow email global sebagai jalur cadangan. Provider-nya beda (SMTP Gmail vs Kirimi), jadi kegagalan keduanya tidak berkorelasi.

---

## Arsitektur

```
Workflow error (Main / Follow-up / Cleanup)
        │ gagal
        ▼
  Error Notifier (per klien)
        │
   Compose Notif ──► Notify Admin Error (Kirimi)
                          │ sukses          │ error ◄── output error
                          ▼                 │
              Check Kirimi Response ────────┤  (throw kalau status != sukses)
                          │ sukses          │
                        selesai             ▼
                                   Build Fallback Payload
                                            │
                                            ▼
                          ┌─────────────────────────────────┐
                          │ GLOBAL - Email Fallback Notifier│──► email ke stevenleroy0@
                          └─────────────────────────────────┘
                                            ▲
                          Error Trigger (lapis 2) ─── kalau notifier crash
                                                       sebelum sempat memanggil
```

**Dua lapis, sengaja:**

| Lapis | Pemicu | Kualitas data |
|-------|--------|---------------|
| 1 — Execute Workflow (utama) | Node Kirimi gagal, atau balas 200 tapi isinya gagal | Lengkap: isi WA yang gagal + error asli + link execution asli |
| 2 — Error Workflow n8n | Notifier crash di node lain (mis. `Compose Notif`) | Tipis: hanya info notifier + link execution notifier |

Lapis 1 dibikin eksplisit karena **fitur "Error Workflow" n8n tidak bisa diandalkan untuk kasus ini** — beberapa versi n8n punya loop-guard yang tidak menjalankan error workflow kalau eksekusi yang gagal modenya sudah `error`. Lapis 2 tetap dipasang sebagai bonus, bukan andalan.

---

## Keputusan: satu sender saja

- **Sender:** `chatminagent@gmail.com` (SMTP, app password)
- **Penerima:** `stevenleroy0@gmail.com`
- **Pembeda klien:** tag di subject — `🚨 [VIRA-PCR] ...` / `🚨 [VIRA-SCHOLARS] ...`

Tidak perlu login `hiduppersada@gmail.com` maupun `thescholarsid@gmail.com`. Alasannya:

1. Ini alert internal untuk Steven, bukan email ke klien — tidak ada yang melihat sender-nya.
2. Tiap sender tambahan = satu kredensial lagi yang bisa expired / di-revoke, menambah titik gagal justru di jalur yang harus paling andal.
3. Tag di subject sudah cukup untuk memisahkan, dan lebih mudah di-filter di Gmail.

Kapan baru perlu sender terpisah: kalau nanti alert dikirim langsung ke pihak klien (Om Sulianto / Sam) dan sender "chatminagent" jadi tidak pantas.

---

## Langkah pasang

### 1. Import workflow global

Import `2026-08-03-GLOBAL-email-fallback-notifier.json`.

### 2. Buat kredensial SMTP

Credentials → New → **SMTP**:

| Field | Nilai |
|-------|-------|
| Host | `smtp.gmail.com` |
| Port | `465` |
| SSL/TLS | on |
| User | `chatminagent@gmail.com` |
| Password | **App Password** Gmail |

App Password dibuat di myaccount.google.com → Security → 2-Step Verification → App passwords. 2FA harus aktif dulu di akun itu. Password Gmail biasa **tidak akan** bekerja.

Lalu pilih credential ini di node **Kirim Email Alert**.

#### Kalau SMTP gagal

| Error | Sebab | Perbaikan |
|-------|-------|-----------|
| `535-5.7.8 Username and Password not accepted` | Pakai password Gmail biasa | Harus App Password 16 karakter |
| Menu App Password tidak muncul | 2FA belum aktif | Aktifkan 2-Step Verification dulu |
| `ETIMEDOUT` / connection timeout | Port 465 diblok hosting | Coba port `587`, SSL/TLS **off** |
| `self signed certificate` | Sertifikat proxy | Aktifkan *Ignore SSL Issues* di credential |
| Test gagal tapi setting benar | n8n hanya gagal saat verifikasi | Save paksa, lalu tes lewat Execute Workflow |

Kalau tetap tidak bisa, ganti node pengirimnya — lihat `2026-08-03-email-node-alternatives.json` (Gmail node OAuth2 / Resend / Brevo). Code node tidak perlu diubah sama sekali; semua alternatif memakai output yang sama (`subject`, `html`, `text`).

### 3. Ganti `N8N_BASE`

Buka node **Normalize & Compose Email**, baris paling atas:

```js
const N8N_BASE = 'https://GANTI-DENGAN-URL-N8N-KAMU';
```

Isi URL instance n8n, tanpa `/` di akhir. Ini yang bikin tombol "Buka execution yang error" di email bisa diklik.

### 4. Save & catat workflow ID

Save workflow. Ambil ID dari URL browser: `.../workflow/<ID-INI>`.

Workflow global ini **tidak perlu di-Activate** — dipanggil sebagai sub-workflow / error workflow.

### 5. Pasang patch di kedua notifier

Untuk **masing-masing** notifier (`VIRA-PCR Error Notifier` dan `VIRA Error Notifier`):

1. Buka workflow → copy isi `2026-08-03-patch-notifier-fallback-nodes.json` → paste ke canvas (Ctrl+V).
2. Ikuti sticky note kuning yang ikut ter-paste. Ringkasnya:
   - Node **Notify Admin Error** → Settings → **On Error** = `Continue (using error output)`
   - Output **success** → `Check Kirimi Response`
   - Output **error** (merah) → `Build Fallback Payload`
   - `Check Kirimi Response` output **error** (merah) → `Build Fallback Payload`
3. Di **Build Fallback Payload**, set `TENANT`:
   - `'VIRA-PCR'` untuk workflow PCR
   - `'VIRA-SCHOLARS'` untuk The Scholars
4. Di **Call Global Email Fallback**, pilih workflow **GLOBAL - Email Fallback Notifier**.
5. Workflow Settings → **Error Workflow** = `GLOBAL - Email Fallback Notifier`.
6. Node **Notify Admin Error** → Settings → **Retry On Fail** on, Max Tries 2, Wait 2000ms. Supaya gangguan sesaat 1–2 detik tidak langsung memicu email.
7. Save.

---

## Cara tes

**Tes A — jalur utama (Kirimi mati):**
Di notifier, ubah sementara URL node Kirimi jadi `https://api.kirimi.id/v1/send-message-ngasal`. Lalu bikin error di workflow Main (mis. rename sheet sebentar) sampai notifier terpicu. Harusnya masuk email dengan isi WA lengkap + link execution. Kembalikan URL setelah selesai.

**Tes B — Kirimi balas 200 tapi gagal:**
Ubah sementara `phone` di node Kirimi jadi nomor ngawur (`628000000000`). Kirimi biasanya tetap balas 200 dengan status gagal → `Check Kirimi Response` harus throw dan memicu email.

**Tes C — lapis 2 (Error Workflow):**
Di notifier, tambahkan `throw new Error('tes lapis 2')` di baris pertama node `Compose Notif`, lalu picu error. Kalau email masuk, berarti versi n8n-mu memang menjalankan error workflow untuk workflow error — bonus. Kalau tidak masuk, itu wajar (loop-guard) dan lapis 1 tetap aman. Hapus baris tes setelahnya.

---

## Yang masih belum tertutup

Kalau **instance n8n-nya sendiri mati**, tidak ada yang jalan — baik WA maupun email. Untuk itu perlu monitor dari luar (uptime ping ke n8n, mis. UptimeRobot/BetterStack ke healthcheck endpoint). Di luar scope patch ini, tapi ini satu-satunya lubang yang tersisa.

Sekunder: `Notify Admin Error` di kedua notifier masih menyimpan `user_code` dan `secret` Kirimi sebagai plaintext di body parameter. Sebaiknya dipindah ke n8n Credentials / environment variable saat ada waktu.
