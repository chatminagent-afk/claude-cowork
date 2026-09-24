# Wireframe & Sistem UI/UX — Metro Logistik Indonesia

**Dokumen:** Wireframe & Design System PWA (Web Dashboard & Tracking)
**Proyek:** Web Dashboard & Tracking PWA — Metro Logistik Indonesia (metrologistikindonesia.com)
**Dibuat oleh:** Software Architect & UI/UX Designer (Claude)
**Tanggal:** 2026-07-05
**Audiens:** Programmer implementasi (Opus), Project Manager

Catatan: wireframe di bawah adalah blok ASCII/teks — merepresentasikan struktur & hierarki layout, bukan tampilan pixel-perfect. Referensi warna/ikon persis ada di §3 (Design System).

---

## A. Halaman Publik (`index.html`)

### A.1 Layout Mobile (utama, viewport ~360–420px)

```
┌───────────────────────────────────────┐
│ ▓▓▓  METRO LOGISTIK INDONESIA    ☰   │  ← Header brand, sticky top, warna primary
├───────────────────────────────────────┤
│ ⚠ Anda sedang offline. Menampilkan   │  ← OfflineBanner (kondisional, warna warning)
│   data tersimpan terakhir.            │
├───────────────────────────────────────┤
│  Lacak Kiriman Anda                   │
│  ┌─────────────────────────────────┐  │
│  │ Masukkan no. resi                │  │  ← SearchBar (textarea multi-line)
│  │ (pisahkan dengan koma atau       │  │
│  │ baris baru)                      │  │
│  │ JX12345678, JX87654321           │  │
│  │                                   │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │          🔍  LACAK               │  │  ← Tombol Lacak (full width, min-h 48px)
│  └─────────────────────────────────┘  │
├───────────────────────────────────────┤
│  Filter Hasil                     ▾   │  ← FilterBar (collapsible di mobile)
│  ┌───────────────┐ ┌───────────────┐  │
│  │ Dari: dd/mm/yy │ │ Sampai: dd/mm │  │
│  └───────────────┘ └───────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │ Status: [Semua Status      ▾]   │  │
│  └─────────────────────────────────┘  │
├───────────────────────────────────────┤
│  Hasil (2 resi)                       │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │ No. Resi: JX12345678       [▼]  │  │ ← ResultCard header
│  │ ● DELIVERED                      │  │   (badge status, warna sukses)
│  │ ───────────────────────────────  │  │
│  │ Pengirim : Toko Sinar Jaya       │  │
│  │ Penerima : Budi Santoso          │  │
│  │ Update   : 05 Jul 2026, 14:30    │  │
│  │ ───────────────────────────────  │  │
│  │ Riwayat Perjalanan:               │  │ ← TimelineStepper (lihat detail A.2)
│  │                                    │  │
│  │  ●━ Delivered                     │  │
│  │  ┃  05 Jul 2026, 14:30            │  │
│  │  ┃  Alamat Penerima, Surabaya     │  │
│  │  ┃  oleh: Rudi Hartono            │  │
│  │  ┃                                │  │
│  │  ○━ Out for Delivery              │  │
│  │  ┃  05 Jul 2026, 09:00            │  │
│  │  ┃  Gudang Transit Surabaya       │  │
│  │  ┃  oleh: Rudi Hartono            │  │
│  │  ┃                                │  │
│  │  ○━ Transit                       │  │
│  │  ┃  03 Jul 2026, 20:00            │  │
│  │  ┃  Hub Semarang                  │  │
│  │  ┃  oleh: Andi Wijaya             │  │
│  │  ┃                                │  │
│  │  ○━ Manifest                      │  │
│  │     01 Jul 2026, 09:00            │  │
│  │     Gudang Jakarta Pusat          │  │
│  │     oleh: Andi Wijaya             │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │ No. Resi: JX87654321       [▼]  │  │
│  │ ⚠ RESI TIDAK DITEMUKAN            │  │ ← Empty state per-card
│  │ Periksa kembali nomor resi Anda. │  │
│  └─────────────────────────────────┘  │
├───────────────────────────────────────┤
│  📲 Instal Aplikasi Metro Logistik    │  ← InstallPrompt (banner, dismissible)
│     untuk akses lebih cepat      [X]  │
└───────────────────────────────────────┘
```

### A.2 Detail Komponen: TimelineStepper (Vertikal Berundak — ala Shopee/JNE)

Prinsip visual:
- **Entri terbaru di atas** (hasil `.reverse()` dari array `riwayat` yang dikembalikan API secara kronologis).
- Titik (dot/ikon) di kiri setiap entri, dihubungkan garis vertikal solid ke entri berikutnya.
- Titik entri **paling atas** (status terkini) di-highlight: lebih besar, warna solid primary/success, dengan efek "aktif" (mis. ring/shadow).
- Titik entri lama: outline/lebih pudar (warna netral).
- Jika status terkini = `Delivered`, seluruh badge status & titik teratas menggunakan **warna sukses (hijau)**, bukan primary biru.

```
  ●━━━  ← titik besar, solid, warna sesuai status (highlight = status terkini)
  ┃     Delivered
  ┃     05 Jul 2026, 14:30 WIB
  ┃     📍 Alamat Penerima, Surabaya
  ┃     👤 Rudi Hartono
  ┃
  ○━━━  ← titik lebih kecil/outline, warna netral (riwayat lama)
  ┃     Out for Delivery
  ┃     05 Jul 2026, 09:00 WIB
  ┃     📍 Gudang Transit Surabaya
  ┃     👤 Rudi Hartono
  ┃
  ○━━━
  ┃     Transit
  ┃     03 Jul 2026, 20:00 WIB
  ┃     📍 Hub Semarang
  ┃     👤 Andi Wijaya
  ┃
  ○━━━
        Manifest
        01 Jul 2026, 09:00 WIB
        📍 Gudang Jakarta Pusat
        👤 Andi Wijaya
```

Struktur per-step (data-binding):
```
[dot+garis] [status label] [badge warna status]
            [waktu: tanggal + jam, format "dd Mmm yyyy, HH:mm WIB"]
            [ikon lokasi] [lokasi/posisi]
            [ikon admin]  [nama admin]
```

### A.3 State Halaman Publik

**1) Loading (Skeleton)**
```
┌─────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  [▓▓]  │  ← baris abu-abu animasi pulse
│ ▓▓▓▓▓▓▓▓▓▓                       │
│ ───────────────────────────────  │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓               │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                 │
│ ───────────────────────────────  │
│ ●━ ▓▓▓▓▓▓▓▓▓▓▓▓                 │
│ ┃  ▓▓▓▓▓▓▓▓▓                    │
│ ○━ ▓▓▓▓▓▓▓▓▓▓▓▓                 │
└─────────────────────────────────┘
Tampilkan 1-2 kartu skeleton sesuai jumlah resi yang sedang di-query.
```

**2) Resi Tidak Ditemukan** (per-card, lihat contoh JX87654321 di atas)
```
┌─────────────────────────────────┐
│ No. Resi: JX87654321             │
│                                    │
│         📭                        │
│  Resi Tidak Ditemukan             │
│  Periksa kembali nomor resi       │
│  Anda atau hubungi CS kami.       │
└─────────────────────────────────┘
```

**3) Error Jaringan (gagal total, semua resi)**
```
┌─────────────────────────────────┐
│            📡✕                    │
│   Gagal Memuat Data              │
│   Periksa koneksi internet Anda  │
│   dan coba lagi.                 │
│  ┌───────────────────────────┐   │
│  │      🔄  COBA LAGI         │   │
│  └───────────────────────────┘   │
└─────────────────────────────────┘
```

**4) Offline (ada cache)**
```
┌───────────────────────────────────────┐
│ ⚠ Anda sedang offline.                │
│   Menampilkan data tersimpan terakhir │
│   pada 05 Jul 2026, 14:30.            │
└───────────────────────────────────────┘
   (ResultCard tetap tampil dari cache di bawah banner ini)
```

### A.4 Catatan Layout Desktop (≥1024px)

```
┌──────────────────────────────────────────────────────────────────┐
│  ▓▓▓  METRO LOGISTIK INDONESIA                    [Beranda][CS]  │  ← header full width, nav horizontal
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│               Lacak Kiriman Anda dengan Mudah                    │
│   ┌────────────────────────────────────┐  ┌──────────────────┐   │
│   │ Textarea multi-resi (lebih lebar)   │  │   🔍 LACAK        │   │
│   └────────────────────────────────────┘  └──────────────────┘   │
│                                                                    │
│   [Filter: Dari][Sampai][Status ▾]   ← sejajar horizontal, inline │
│                                                                    │
│   ┌───────────────────┐  ┌───────────────────┐  ┌──────────────┐ │
│   │  ResultCard 1       │  │  ResultCard 2       │  │ ResultCard 3│ │  ← grid 2-3 kolom
│   │  (timeline penuh)   │  │  (timeline penuh)   │  │             │ │
│   └───────────────────┘  └───────────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```
Catatan: FilterBar berubah dari collapsible (mobile) menjadi inline horizontal (desktop). ResultCard disusun grid multi-kolom (Tailwind: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`), lebar maksimum konten `max-w-7xl mx-auto`.

---

## B. Halaman Admin Lapangan (`admin.html`)

Target pengguna: petugas lapangan dengan HP entry-level & sinyal lemah → prioritas: **form sesingkat mungkin, tombol besar, feedback sangat jelas, minim ketikan**.

### B.1 Layout Mobile (utama)

```
┌───────────────────────────────────────┐
│ ▓▓▓ METRO LOGISTIK   [ADMIN LAPANGAN] │  ← Header + badge peran
├───────────────────────────────────────┤
│ ⚠ Offline — update akan dikirim saat  │  ← OfflineBanner (kondisional)
│   koneksi tersedia.                    │
├───────────────────────────────────────┤
│                                        │
│  Update Status Kiriman                │
│                                        │
│  No. Resi *                           │
│  ┌─────────────────────────────────┐  │
│  │ JX12345678                       │  │  ← Input No Resi
│  └─────────────────────────────────┘  │
│                                        │
│  Nama Admin *                         │
│  ┌─────────────────────────────────┐  │
│  │ Rudi Hartono                     │  │  ← Input Nama Admin
│  └─────────────────────────────────┘  │
│                                        │
│  Status *                             │
│  ┌─────────────────────────────────┐  │
│  │ Out for Delivery            ▾    │  │  ← Dropdown Status
│  └─────────────────────────────────┘  │
│    • Manifest                          │
│    • On Process                        │
│    • Transit                           │
│    • Out for Delivery                  │
│    • Delivered                         │
│    • Failed/Return                     │
│                                        │
│  Catatan Lokasi/Posisi Saat Ini *     │
│  ┌─────────────────────────────────┐  │
│  │ Dalam perjalanan menuju alamat   │  │  ← Textarea Catatan Lokasi
│  │ penerima, area Rungkut Surabaya  │  │
│  │                                   │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │                                    │  │
│  │        ✅  SUBMIT UPDATE          │  │  ← Tombol Submit (besar, h-56px)
│  │                                    │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ⏳ 2 update menunggu dikirim          │  ← indikator antrean offline (kondisional)
└───────────────────────────────────────┘
```

### B.2 Feedback Sukses / Gagal

**Sukses (Toast, muncul dari bawah, auto-dismiss 4 detik, warna hijau):**
```
┌───────────────────────────────────────┐
│  ✅  Berhasil! Status JX12345678       │
│      diperbarui menjadi               │
│      "Out for Delivery".              │
└───────────────────────────────────────┘
```
Form otomatis reset (kecuali Nama Admin — dipertahankan untuk mempercepat entri berikutnya oleh admin yang sama).

**Gagal — validasi (Alert inline dekat field bermasalah, warna merah, border merah pada input):**
```
No. Resi *
┌─────────────────────────────────┐
│                                    │  ← border merah
└─────────────────────────────────┘
⚠ No. Resi wajib diisi.
```

**Gagal — jaringan/server (Toast merah + tersimpan ke antrean):**
```
┌───────────────────────────────────────┐
│  ⚠ Gagal terkirim (jaringan).         │
│    Data tersimpan di HP ini dan       │
│    akan dikirim otomatis saat         │
│    koneksi tersedia.                  │
└───────────────────────────────────────┘
```

### B.3 Validasi Form

| Field | Aturan |
|---|---|
| No Resi | Wajib diisi, tidak boleh kosong setelah trim |
| Nama Admin | Wajib diisi; ditolak jika kosong atau **hanya berisi spasi** (`value.trim().length === 0` → invalid) |
| Status | Wajib dipilih (tidak boleh pada opsi placeholder "-- Pilih Status --") |
| Catatan Lokasi | Wajib diisi, tidak boleh kosong setelah trim |

Perilaku validasi:
- Validasi dijalankan saat submit (bukan hanya `required` HTML, karena butuh pesan Bahasa Indonesia yang konsisten dan pengecekan trim/spasi).
- Field pertama yang gagal validasi otomatis di-scroll ke tampilan (`scrollIntoView`) dan diberi fokus — penting di layar kecil.
- Tombol Submit menampilkan state loading (`Mengirim...` + spinner kecil) selama proses submit, dan **disabled** untuk mencegah double-submit akibat koneksi lambat.

### B.4 Catatan Layout Desktop

```
┌──────────────────────────────────────────────────────────┐
│  ▓▓▓ METRO LOGISTIK        [ADMIN LAPANGAN]               │
├──────────────────────────────────────────────────────────┤
│              ┌──────────────────────────────┐             │
│              │  Update Status Kiriman         │             │
│              │  (form max-width 480px,        │             │
│              │   center-aligned)              │             │
│              │  [No Resi]                     │             │
│              │  [Nama Admin]                  │             │
│              │  [Dropdown Status]              │             │
│              │  [Catatan Lokasi]               │             │
│              │  [SUBMIT UPDATE]                │             │
│              └──────────────────────────────┘             │
└──────────────────────────────────────────────────────────┘
```
Form admin tetap single-column bahkan di desktop (form pendek, tidak butuh multi-kolom) — konsisten dengan prinsip "form sesingkat & sesederhana mungkin" karena tetap dipakai juga dari browser desktop oleh supervisor/gudang.

---

## C. Design System

### C.1 Palet Warna (Logistik Profesional)

Tema: biru navy (kepercayaan, korporat/logistik) + aksen oranye (energi, pergerakan/kurir) — umum dipakai identitas ekspedisi Indonesia.

| Token | Hex | Penggunaan |
|---|---|---|
| `primary` | `#0F3D5C` | Header, tombol utama, tema PWA, elemen brand |
| `primary-light` | `#1D6FA5` | Hover state primary, aksen link |
| `secondary/accent` | `#F2994A` | Aksen CTA sekunder (mis. tombol "Lacak"), highlight InstallPrompt |
| `success` | `#1E8E3E` | Status "Delivered", toast sukses, badge sukses |
| `warning` | `#F2B705` | OfflineBanner, status "Failed/Return" alternatif ringan, alert non-kritis |
| `danger` | `#D93025` | Toast gagal, validasi error, status "Failed/Return" |
| `netral-900` | `#1A1A1A` | Teks utama |
| `netral-600` | `#5F6B76` | Teks sekunder/caption |
| `netral-300` | `#D5DBE0` | Border, divider, garis timeline non-aktif |
| `netral-100` | `#F5F7F9` | Background halaman/card |
| `white` | `#FFFFFF` | Background card, teks di atas warna gelap |

Tailwind config (potongan, untuk `tailwind.config` di `<script>`):
```js
theme: {
  extend: {
    colors: {
      primary: { DEFAULT: '#0F3D5C', light: '#1D6FA5' },
      accent: '#F2994A',
      success: '#1E8E3E',
      warning: '#F2B705',
      danger: '#D93025',
    }
  }
}
```

### C.2 Tipografi

| Elemen | Ukuran (mobile) | Ukuran (desktop) | Bobot | Catatan |
|---|---|---|---|---|
| Judul Halaman (H1) | 20px (`text-xl`) | 28px (`text-3xl`) | 700 (bold) | "Lacak Kiriman Anda" |
| Judul Kartu (H2) | 16px (`text-base`) | 18px (`text-lg`) | 600 (semibold) | No. Resi di ResultCard |
| Label Status/Badge | 12px (`text-xs`) | 12px | 700, uppercase, letter-spacing | Badge status berwarna |
| Body/Teks Utama | 14px (`text-sm`) | 16px (`text-base`) | 400 | Info pengirim/penerima, catatan |
| Caption/Meta | 12px (`text-xs`) | 13px | 400 | Waktu, nama admin di timeline |
| Font family | `font-sans` (stack default Tailwind: system-ui, -apple-system, Segoe UI, Roboto) | | | Tanpa font kustom (hindari load lambat di sinyal buruk) |

### C.3 Spacing

- Basis skala Tailwind default (4px increment: `p-1`=4px ... `p-4`=16px ... `p-6`=24px).
- Padding kartu (ResultCard/AdminForm): `p-4` mobile, `p-6` desktop.
- Jarak antar kartu hasil: `space-y-4` (16px) mobile, `gap-4`/`gap-6` grid desktop.
- Jarak antar field form admin: `space-y-4` (16px), agar target sentuh tidak berdempetan.
- Margin section utama: `px-4` (16px) mobile, `px-8`/`max-w-7xl mx-auto` desktop.

### C.4 Touch Target

- **Minimum 44×44px** untuk semua elemen interaktif (tombol, input, dropdown, checkbox), sesuai standar aksesibilitas iOS/Android.
- Tombol Submit admin & tombol Lacak publik: tinggi minimum **48px** (`h-12`), full-width di mobile.
- Jarak antar elemen tap minimal 8px agar tidak salah tekan di layar kecil / jari besar (penting untuk pengguna sarung tangan kerja di lapangan).
- Dropdown Status memakai elemen `<select>` native (bukan custom dropdown JS) di mobile agar otomatis mendapat UI picker native OS yang besar & mudah disentuh.

### C.5 Mapping Warna & Ikon per Status

| Status | Warna Badge | Ikon (referensi, boleh emoji/SVG) | Deskripsi Singkat |
|---|---|---|---|
| **Manifest** | Netral (`bg-netral-300 text-netral-900`) | 📋 | Resi terdaftar, belum diproses fisik |
| **On Process** | Info/biru muda (`bg-primary-light/10 text-primary-light`) | ⚙️ | Barang sedang diproses di gudang asal |
| **Transit** | Aksen oranye (`bg-accent/10 text-accent`) | 🚚 | Dalam perjalanan antar hub/kota |
| **Out for Delivery** | Aksen oranye solid (`bg-accent text-white`) | 🛵 | Sedang diantar ke alamat penerima |
| **Delivered** | Sukses (`bg-success/10 text-success`, dot solid hijau) | ✅ | Barang sudah diterima |
| **Failed/Return** | Danger (`bg-danger/10 text-danger`) | ⚠️ / ↩️ | Gagal antar / dikembalikan |

Ikon di atas adalah referensi semantik minimal; programmer boleh menggunakan set ikon SVG konsisten (mis. Heroicons via CDN) selama mapping warna-status di atas dipatuhi persis, agar bahasa visual sama antara halaman publik dan admin.

### C.6 Komponen States (Interaction States)

Berlaku untuk semua elemen interaktif (tombol, input, dropdown):

| State | Perlakuan Visual |
|---|---|
| **Default** | Warna dasar sesuai token, border `netral-300` |
| **Hover** (desktop/mouse) | Tombol primary: `bg-primary-light`; border input: `border-primary-light`; sedikit shadow naik |
| **Focus** (keyboard/tap) | Ring fokus jelas: `ring-2 ring-primary-light ring-offset-2` — wajib untuk aksesibilitas & agar terlihat jelas field mana yang aktif diisi |
| **Disabled** | Opacity 50%, `cursor-not-allowed`, tombol submit disabled selama proses kirim berlangsung |
| **Error/Invalid** | Border `danger`, teks pesan error `text-danger text-xs` di bawah field, ikon peringatan di dalam input (opsional) |
| **Loading** | Tombol: teks berubah + spinner kecil putih, tetap mempertahankan lebar tombol (mencegah layout shift) |
| **Active/Pressed** | Sedikit scale-down (`active:scale-95`) untuk memberi umpan balik taktil di layar sentuh |

---

## Ringkasan Keputusan UI/UX

1. SearchBar publik menggunakan `<textarea>` (bukan `<input>` tunggal) agar jelas mendukung multi-resi, dengan placeholder yang mengedukasi format input (koma/baris baru).
2. TimelineStepper meniru pola familiar Shopee/JNE (vertikal, terbaru di atas, titik+garis, highlight status terkini) agar pengguna Indonesia tidak perlu belajar pola baru.
3. Form admin sengaja dibuat **single-column, field minimal, tombol besar** — dioptimalkan untuk kondisi lapangan nyata (HP murah, sinyal lemah, mungkin memakai sarung tangan/terburu-buru).
4. Palet warna navy + oranye dipilih untuk kesan profesional-logistik sekaligus familiar dengan identitas ekspedisi Indonesia, dengan status color-coding yang konsisten lintas halaman.
5. Semua state penting (loading, kosong, error, offline, sukses, gagal) didefinisikan eksplisit agar programmer tidak menebak-nebak perilaku UI di kondisi tepi (edge case).

---

**Daftar File Referensi Terkait:**
- `docs/2026-07-05-arsitektur-frontend-pwa.md` — struktur teknis & kontrak API
- `docs/2026-07-05-skema-database-google-sheets.md` — skema data sumber
