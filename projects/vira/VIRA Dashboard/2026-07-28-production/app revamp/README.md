# `app revamp/` — VIRA Dashboard, front-end baru

Redesain tampilan penuh dari `app/`. **Folder `app/` tidak disentuh sama sekali** —
versi produksi lama tetap utuh dan bisa dipakai kapan saja.

Kontrak ke server tidak berubah satu byte pun: endpoint, bentuk request,
bentuk respons, dan model token persis sama. Yang berubah hanya lapisan
tampilan dan interaksi.

---

## Yang berubah

| | `app/` | `app revamp/` |
|---|---|---|
| Tema | gelap saja | **gelap + terang**, ada tombol pindah, tersimpan di `localStorage` |
| Bahasa visual | glass gelap datar | glassmorphism ala iOS/macOS: latar ambient bergerak, kilau tepi kartu, kurva animasi khas Apple |
| Login | kartu polos | kartu melayang, emblem beremanasi cahaya, tombol lihat kata sandi, tombol tema |
| Logo tenant | huruf awal nama | **foto `thescholars.jpg`** untuk The Scholars, huruf awal untuk tenant lain |
| Daftar lead di ponsel | tabel 7 kolom yang harus digeser ke samping | **kartu** — nama, nomor, angka penting, dan switch bot dalam satu pandangan |
| Urutkan di ponsel | hanya lewat kepala kolom (harus digeser) | pemilih urutan muncul otomatis di tampilan kartu |
| Tombol header di layar sempit | berdesakan | dilipat ke menu ringkas |
| Pencarian | tanpa tombol hapus | ada tombol hapus |
| Target sentuh | sebagian < 44px | semua ≥ 44px |
| Bulatan "i" pada KPI | hanya `title` — tak pernah muncul di layar sentuh | **tombol sungguhan**, membuka lembar penjelasan |
| Section card | selalu terbuka | **bisa dilipat**, status diingat per klien |
| Section kosong | kotak "belum ada data" setinggi 80px | otomatis terlipat jadi satu baris |
| Kartu yang tak dipakai | selalu tampil | **"Atur tampilan"** — pilih sendiri kartu mana yang muncul |

Fungsi yang **tidak** berubah: login/me/switch_tenant/stats/toggle_user, konfirmasi
sebelum mematikan bot, optimistic update + rollback, rentang 7/30/90 hari tanpa
request server, banner mode uji `?api=`, token per-origin, PWA + service worker,
dan aturan "tidak ada nama tenant/kolom yang di-hardcode di frontend".

---

## Cara deploy

Sama seperti `app/`: folder statis, tanpa build step.

1. Edit `js/config.js` → `DEFAULT_API_URL` kalau alamat webhook berubah.
2. Unggah **isi folder ini** ke hosting statis (Cloudflare Pages / Netlify).
3. Pastikan domainnya ada di `corsOrigins` (`n8n/src/tenants.js`), lalu rebuild
   + import ulang workflow n8n. Kalau domainnya sama dengan yang lama, tidak
   ada yang perlu diubah di sisi server.

Setiap kali berkas di folder ini berubah, naikkan `CACHE_VERSION` di `sw.js`
supaya klien lama tidak menyajikan berkas basi.

### Kalau `app/` dan `app revamp/` disajikan dari domain yang sama

Awalan nama cache sengaja dibedakan (`vira-revamp-` vs `vira-dash-`). Kalau
disamakan, service worker versi lama akan menghapus cache versi ini setiap kali
halaman lamanya dibuka.

---

## Menambah logo tenant baru

Satu tempat saja, di `js/config.js`:

```js
TENANT_LOGOS: {
  thescholars: 'icons/thescholars.jpg'
}
```

Kuncinya id tenant dari server (`stats.tenant.id`); pencocokan juga menerima
variasi penulisan nama ("The Scholars", "the-scholars"). Tenant yang tidak
terdaftar tetap tampil normal dengan emblem huruf awal — tidak ada yang rusak.
Kalau berkas gambarnya hilang saat deploy, header otomatis jatuh kembali ke
emblem huruf.

---

## Tema

- Urutan penentuan: pilihan tersimpan → preferensi sistem → `DEFAULT_THEME`.
- Tema dipasang di `<head>` sebelum CSS melukis, jadi tidak ada kedipan gelap
  saat pengguna mode terang membuka halaman.
- Selama pengguna belum menekan tombol tema, perubahan tema sistem tetap
  diikuti. Begitu ia memilih sendiri, pilihannya yang menang.
- Warna garis/bar chart adalah atribut SVG, bukan CSS — `app.js` menggambar
  ulang chart setiap kali tema diganti. Gridline, sumbu, dan garis panduan
  ikut CSS jadi berganti sendiri.

---

## Hasil pengujian

Dijalankan dengan `python qa/serve.py`, dibuka di
`http://localhost:8099/app%20revamp/index.html`.

| Uji | Hasil |
|---|---|
| `qa/uitest.html` diarahkan ke `app revamp/js/` | **94/94 lolos** |
| `qa/selftest.html` diarahkan ke `app revamp/js/` | **184/184 lolos** |
| Alur penuh dengan fixture kedua tenant | login → stats → ganti tenant → toggle → drawer → keluar, semua jalan |
| Regresi toggle bolak-balik | switch bisa dibalik berkali-kali di tabel maupun kartu |
| Ponsel 375px | tanpa gulir horizontal (`scrollWidth` = 375), KPI dua kolom, kartu lead aktif |
| Tema terang & gelap | semua token terdefinisi di kedua tema, chart digambar ulang, teks kecil ≥ 4.5:1 |
| Empty state | chart, tabel lead, tabel tambahan, dan drawer semuanya punya pesan sendiri |
| XSS | nilai server tetap masuk lewat `textContent`; `<img onerror>` tidak pernah jadi elemen |
| Switch di kartu lead | 50×30 dengan knob 24px — geometri benar di tabel maupun kartu |
| Lipat seksi | 11 seksi bisa dilipat; status tersimpan dan bertahan setelah reload |
| Atur tampilan | 22 baris (1 direktori + 11 KPI + 6 grafik + 4 tabel), sembunyikan/tampilkan jalan |
| Isolasi antar klien | pengaturan The Scholars tidak ikut terbawa saat pindah ke Persada |

Belum diuji terhadap n8n produksi yang sebenarnya — sama seperti `app/`,
perlu smoke test setelah deploy.

---

## Atur tampilan (kurasi kartu)

Menu tiga titik → **Atur tampilan**. Panelnya mendaftar SETIAP kartu yang
dikirim server untuk klien yang sedang dibuka — direktori lead, tiap KPI, tiap
grafik, tiap tabel — masing-masing dengan switch.

Isinya dibangun 100% dari payload server; tidak ada satu pun judul kartu yang
ditulis di kode frontend. Konsekuensinya: klien ketiga yang ditambahkan nanti
langsung punya panel yang benar tanpa frontend disentuh sama sekali.

Baris yang isinya kosong pada data saat ini ditandai "Kosong pada data saat
ini" — itu petunjuk kandidat kartu yang bisa dimatikan.

Pengaturan disimpan di `localStorage`, **per perangkat dan per klien**
(`vd.hidden::<id tenant>`). Artinya Sam dan Om Sulianto bisa punya susunan
sendiri-sendiri, dan tidak ada perubahan apa pun di sisi server. Tombol
"Tampilkan semua lagi" mengembalikan semuanya.

### Melipat seksi

Setiap kepala seksi bisa ditekan untuk buka/tutup. Statusnya diingat
(`vd.sections::<id tenant>`). Seksi yang isinya kosong terlipat sendiri saat
pertama kali dibuka — kotak "belum ada data" setinggi 80px tidak memberi tahu
apa pun yang belum terbaca dari judulnya.

### Penjelasan kartu

Bulatan "i" pada KPI kini tombol sungguhan yang membuka lembar penjelasan
(di ponsel muncul sebagai sheet dari bawah). Isinya `kpi.hint` dari server.

Kepala seksi juga punya "i" yang sama, isinya field `hint` pada
`leads` / `charts[]` / `tables[]`. Field itu **sudah ditambahkan** di
`n8n/src/tenants.js` dan `n8n/src/build-payload.js`, dan `VIRA-Dashboard-API.json`
sudah di-rebuild — tinggal **import ulang workflow-nya ke n8n** supaya hint-nya
sampai ke produksi. Sebelum di-import, seksi tetap jalan, hanya tanpa tombol "i".

Hint bersifat opsional dan aditif: `app/` versi lama mengabaikannya dan tetap
berjalan normal dengan payload baru (sudah diuji).
