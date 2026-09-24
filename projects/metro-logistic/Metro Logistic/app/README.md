# Metro Logistik Indonesia — PWA Tracking & Admin

Progressive Web App (PWA) untuk pelacakan resi publik dan update status oleh admin lapangan.
Tanpa framework, tanpa build step — cukup file statis (HTML + Tailwind CDN + Vanilla JS).

## Struktur

```
app/
├── index.html        # Halaman publik: cek resi & timeline tracking
├── admin.html        # Halaman admin lapangan: form update status
├── manifest.json     # Web App Manifest (metadata PWA)
├── sw.js             # Service Worker (cache app-shell + strategi API)
├── README.md         # Dokumen ini
├── js/
│   ├── config.js     # URL webhook n8n + parameter jaringan (SATU-SATUNYA tempat URL)
│   ├── tracking.js   # Logika halaman publik
│   └── admin.js      # Logika halaman admin (form, validasi, antrean offline)
└── icons/            # Ikon PWA (192/512, maskable, apple-touch-icon)
```

## 1. Konfigurasi (WAJIB sebelum deploy)

Buka `js/config.js` dan ganti dua URL placeholder dengan URL webhook n8n produksi Anda:

```js
const N8N_GET_URL    = 'https://domain-n8n-anda/webhook/tracking-get';    // WF1 (GET)
const N8N_UPDATE_URL = 'https://domain-n8n-anda/webhook/tracking-update'; // WF2 (POST)
```

Tidak perlu mengubah file lain — seluruh logika membaca URL dari `config.js`.
Parameter lain (timeout, retry) juga ada di `config.js` jika ingin disesuaikan.

## 2. Deploy (hosting statis, HTTPS wajib)

Aplikasi ini hanya berisi file statis, jadi dapat di-host di mana saja:
Netlify, Vercel, GitHub Pages, Cloudflare Pages, atau Nginx/Apache di VPS.

**HTTPS wajib** — Service Worker dan fitur "install PWA" hanya aktif di `https://`
(pengecualian: `http://localhost` untuk pengembangan lokal).

Langkah umum:
1. Unggah seluruh isi folder `app/` ke root domain (mis. `https://metrologistikindonesia.com/`).
2. Pastikan `index.html`, `admin.html`, `manifest.json`, `sw.js`, folder `js/` dan `icons/` dapat diakses.
3. Buka `https://domain-anda/index.html` di browser.

Uji lokal cepat (opsional), dari dalam folder `app/`:
```bash
# Python 3
python -m http.server 8080
# lalu buka http://localhost:8080
```

## 3. Cara Install PWA

### Android (Chrome / Edge)
- Buka halaman di browser. Banner "Instal Aplikasi Metro Logistik" akan muncul.
- Ketuk tombol **Instal**, atau via menu browser (⋮) → **"Instal aplikasi"** / **"Tambahkan ke layar utama"**.

### iOS (Safari)
- iOS tidak mendukung prompt instal otomatis; instalasi dilakukan manual.
- Buka halaman di **Safari** → ketuk tombol **Bagikan** (kotak dengan panah ke atas) →
  gulir dan pilih **"Tambah ke Layar Utama"** → **Tambah**.
- Ikon aplikasi akan muncul di layar utama dan berjalan layar penuh (standalone).

## 4. Halaman

- **`index.html`** — Publik. Masukkan satu atau banyak nomor resi (dipisah koma / baris baru),
  tekan **Lacak**. Hasil tampil sebagai kartu dengan timeline vertikal (terbaru di atas),
  lengkap dengan filter rentang tanggal & status. Mendukung mode offline (menampilkan
  data tersimpan terakhir bila ada).
- **`admin.html`** — Admin lapangan. Form ringkas (No Resi, Nama Admin, Status, Catatan Lokasi).
  Nama admin diingat di perangkat. Bila offline/gagal jaringan, update disimpan ke antrean
  (IndexedDB) dan dikirim ulang otomatis saat koneksi kembali atau saat halaman dibuka lagi.

## 5. Catatan Teknis

- Update cache: naikkan `CACHE_VERSION` di `sw.js` setiap kali app shell berubah,
  agar klien menerima versi terbaru.
- Enum status resmi (harus identik dengan backend): `Manifest`, `On Process`, `Transit`,
  `Out for Delivery`, `Delivered`, `Failed/Return`.
- Ikon di `icons/` adalah placeholder brand (monogram "M" navy/oranye). Ganti dengan
  aset final Metro Logistik bila tersedia (pertahankan nama file & ukuran yang sama).
