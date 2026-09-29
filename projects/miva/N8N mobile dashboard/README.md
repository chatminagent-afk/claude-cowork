# n8n Mobile Dashboard

Dashboard PWA untuk memantau n8n self-hosted dari HP: daftar execution, detail
per node, toggle workflow, dan retry execution yang gagal.

> ⚠️ **File ini memuat DASH_TOKEN.** Cloudflare tidak bisa menampilkan ulang
> nilai secret setelah disimpan, jadi token dicatat di sini supaya tidak hilang.
> Jangan ikut disalin ke tempat yang dibagikan.

---

## Arsitektur

```
HP  ──X-N8N-API-KEY: DASH_TOKEN──▶  Worker proxy  ──API key asli──▶  n8n
     (localStorage)                 (Cloudflare)                     (VPS Hostinger)
```

n8n tidak mengirim header CORS, jadi browser tidak bisa memanggil `/api/v1/*`
secara langsung. Proxy-nya yang mengirim header itu, karena kodenya milik kita
sendiri. Efek sampingnya: API key n8n asli tidak pernah sampai ke HP — yang
disimpan di sana cuma DASH_TOKEN, dan itu bisa dicabut dari Cloudflare tanpa
menyentuh n8n.

## Yang live sekarang

| Komponen | Alamat | Isi |
|---|---|---|
| Dashboard | `https://n8n.chatminagent.workers.dev` | Worker **static-assets** — melayani `production/` |
| Proxy | `https://n8n-proxy.chatminagent.workers.dev` | Worker **kode** — isi `production/worker-proxy.js` |
| n8n | `https://n8n.srv1270416.hstgr.cloud` | Tidak disentuh sama sekali |

Dua worker terpisah karena worker static-assets **tidak bisa punya variables /
secrets** — Cloudflare memblokirnya. Proxy harus jadi worker yang benar-benar
punya kode.

### Variables di worker `n8n-proxy`

| Nama | Tipe | Nilai |
|---|---|---|
| `N8N_BASE` | Text | `https://n8n.srv1270416.hstgr.cloud` |
| `DASH_TOKEN` | Secret | `Xtp0WrHvAiseswi6UgITnDFgsO6E_kK4` |
| `N8N_API_KEY` | Secret | API key dari n8n → Settings → n8n API |
| `ALLOW_ORIGIN` | Text | `https://n8n.chatminagent.workers.dev` |

### Setting di HP

- **N8N_BASE_URL**: `https://n8n-proxy.chatminagent.workers.dev` — tanpa slash di akhir
- **N8N_API_KEY**: isi dengan **DASH_TOKEN**, bukan API key n8n
- **CORS Proxy**: harus **off**. Kalau dinyalakan, kredensial lewat server pihak ketiga.

---

## Isi folder

```
production/
  upload/              ← INI yang di-upload ke worker `n8n`. Isinya persis 5 file, nol file lain.
    index.html           satu-satunya sumber HTML; edit di sini
    manifest.webmanifest
    sw.js                service worker; sengaja bypass /n8n/* supaya angka basi tidak ter-cache
    icon-192.png
    icon-512.png
  upload-assets.zip    isi upload/ dalam bentuk zip, kalau UI Cloudflare minta zip
  worker-proxy.js      kode worker `n8n-proxy` — TIDAK ikut di-upload ke worker `n8n`

archive/             ← jalur deploy yang dicoba lalu ditinggalkan
  pages-direct-upload/    Cloudflare Pages Direct Upload; gagal karena upload zip
  pages-direct-upload.zip lewat dashboard menghasilkan worker assets-only
  wrangler-worker/        jalur `npx wrangler deploy`; butuh Node.js, tidak terpasang
```

Arsip disimpan karena berisi varian `wrangler.toml` dan `_worker.js` yang masih
berguna kalau suatu saat Node.js dipasang. HTML di dalam arsip **versi lama**
(65 KB, sebelum QA 03 Agustus) — jangan dipakai.

---

## Cara deploy ulang

### Dashboard (kalau isi `production/upload/` berubah)

1. Cloudflare → Workers & Pages → worker **`n8n`** → **New deployment**
2. Upload salah satu, isinya sama:
   - isi folder `production/upload/` — pilih kelima filenya, atau drag foldernya
   - atau `production/upload-assets.zip` — jangan di-extract dulu
3. Di HP: hard refresh. Service worker bisa menyajikan HTML lama.
4. Kalau yang berubah `sw.js`: hard refresh **tidak cukup** — lihat catatan
   service worker di bawah.

Kalau ada file di `upload/` yang diedit, bikin ulang zip-nya supaya tidak ketinggalan:

```powershell
$p = "D:\Documents\Claude Cowork\mobile dashboard\production"
Compress-Archive -Path "$p\upload\*" -DestinationPath "$p\upload-assets.zip" -Force
```

Yang **tidak** ikut: `worker-proxy.js`. Worker `n8n` itu assets-only — file kode
di situ diabaikan diam-diam, dan itu yang bikin bingung waktu percobaan pertama.

### Proxy (kalau `worker-proxy.js` berubah)

Cloudflare → worker **`n8n-proxy`** → **Edit code** → ganti seluruh isi → **Deploy**.
Variables tidak perlu diisi ulang.

---

## Verifikasi

```bash
curl https://n8n-proxy.chatminagent.workers.dev/
```

| Cek | Harapan |
|---|---|
| `GET /` di proxy | `{"ok":true,...,"configured":true}` |
| `GET /api/v1/workflows` tanpa header token | `401` |
| `GET /rest/executions` dengan token | `403` — internal API sengaja diblokir |
| `OPTIONS /api/v1/executions` + Origin | `204` + `Access-Control-Allow-*` |
| Root dashboard | `200`, dashboard render |
| Tombol Test di HP | jadi **Connected** |

---

## Catatan yang gampang terlupa

- **Retry ternyata didukung** di build n8n ini. Dibuktikan lewat probe:
  `GET /api/v1/executions/{id}/retry` balas `405` (route terdaftar, method salah),
  sementara path karangan balas `404`. Dokumentasi umum bilang Public API v1 tidak
  punya retry — untuk instance ini itu tidak berlaku.
- Tombol Retry hanya aktif untuk execution berstatus `error`/`crashed`.
- **Belum pernah dijalankan sungguhan.** Retry men-trigger workflow beneran —
  bisa mengirim WhatsApp atau email. Untuk VIRA, jangan dipakai sampai ada guard
  idempotensi, karena re-run jalan dari awal dan bisa dobel kirim.
- **Service worker adalah tersangka pertama kalau angka tidak mau berubah.**
  Gejalanya khas: hard refresh menampilkan data terbaru, tombol refresh biasa
  tidak. SW duduk di antara halaman dan jaringan, dan Cache Storage API
  **mengabaikan** header `Cache-Control` — jadi `no-store` dari proxy tidak
  menolong sama sekali. 07 Agustus 2026: aturan bypass di `sw.js` masih
  mencocokkan `/n8n/*` pada origin sendiri, sisa dari waktu proxy belum pindah
  ke worker terpisah. Kondisi itu tidak pernah true, semua respons `/api/v1/*`
  ikut masuk cabang cache-first, dan URL-nya fixed tanpa cache-buster — jadi
  respons pertama membeku selamanya. Sekarang pemisahnya `req.destination === ''`
  (semua panggilan `fetch()`), bukan path.
- **SW tidak ikut ter-update waktu halaman di-refresh.** Kalau `sw.js` diubah,
  file di server sudah benar tapi HP masih menjalankan yang lama. Naikkan nama
  `CACHE` (`n8n-ops-v2`, dst) — handler `activate` cuma menghapus cache yang
  namanya beda, tanpa itu entri lama yang teracuni tetap tinggal. Di HP:
  Settings situs → Storage → **Clear & reset**, lalu buka ulang.
- Auto-refresh membatasi diri: daftar workflow paling sering tiap 5 menit,
  quick stats tiap 2 menit. Refresh manual dan pull-to-refresh selalu penuh.
- `ALLOW_ORIGIN` cuma pertahanan tingkat browser. Gerbang sebenarnya `DASH_TOKEN`.
- Kalau API key n8n dirotasi, cukup ubah secret `N8N_API_KEY` di Cloudflare.
  HP tidak perlu disentuh.
