# Laporan QC Kode — Review oleh Fable (QA Lead)
**Tanggal:** 5 Juli 2026 · **Objek review:** seluruh output Opus (Fase A & B) + konsistensi dengan rancangan Sonnet

## Ringkasan
Kode dinyatakan **LAYAK diserahkan** setelah 3 perbaikan QC diterapkan. Verifikasi otomatis: semua JSON valid (`json.tool`), semua JS lolos `node --check` (termasuk jsCode di dalam node n8n yang saya ekstrak dan cek terpisah), ikon PNG terverifikasi ukuran & mode via PIL.

## Temuan & Perbaikan yang SUDAH diterapkan
| ID | Tingkat | Lokasi | Temuan | Perbaikan |
|----|---------|--------|--------|-----------|
| QC-01 | **Kritis** | WF3 `Code Susun Daftar Hapus` | Daftar baris untuk dihapus diambil dari output `Code Filter Kandidat Arsip`, padahal node `Filter Ada Kandidat` di tengah bisa menyaring item. Item yang tersaring akan DIHAPUS dari sheet Utama tanpa pernah ter-append ke Archive → potensi kehilangan data permanen. | Referensi diubah ke `$items('Filter Ada Kandidat')` sehingga daftar hapus = persis item yang di-append ke Archive. |
| QC-02 | Tinggi | WF3 `Code Filter Kandidat Arsip` | Baris dengan No_Resi kosong bisa lolos jadi kandidat lalu tersaring di node Filter → skenario pemicu QC-01. | Guard ditambahkan: baris tanpa No_Resi tidak pernah jadi kandidat arsip. |
| QC-03 | Sedang | WF2 `Respond Sukses` | responseBody membaca `$json.total_riwayat` dari output node Google Sheets (update/append), yang tidak menjamin field itu ada → respons bisa `undefined`. | Diubah membaca eksplisit dari `$('Code Proses Update/Append').first().json`. |
| QC-04 | Rendah | Struktur folder | Fase A menulis sebagian file ke folder bersarang salah (`Metro Logistic\Metro Logistic\`): WF2 & WF3 hanya ada di sana. | WF2 & WF3 (dengan patch QC-01–03) disalin ke `n8n/` yang benar. Folder bersarang menunggu konfirmasi hapus dari Steven. |

## Hasil review per area (LOLOS)
- **Kontrak data konsisten** — nama kolom sheet, bentuk elemen riwayat `{waktu, status, lokasi, admin}`, enum 6 status, dan bentuk response WF1/WF2 identik di docs Sonnet, frontend, dan ketiga workflow.
- **Timeline publik** — riwayat kronologis dibalik di frontend (`.reverse()`, terbaru di atas); waktu diformat Indonesia; step teratas di-highlight; Delivered hijau; status di luar enum jatuh ke badge netral (aman untuk entri `CATATAN_SISTEM` dari WF2).
- **Anti-XSS** — `escapeHtml()` diterapkan pada semua data API sebelum `innerHTML` (status, lokasi, admin, resi, pengirim/penerima, waktu fallback). Ikon memakai HTML entity statis.
- **Validasi berlapis** — client-side (wajib + tolak spasi-saja + error inline) dan server-side di WF2 (field wajib + enum, HTTP 400). Nama admin kosong tidak bisa lolos dari dua sisi.
- **Offline admin** — antrean IndexedDB dengan fallback localStorage, `client_id` unik untuk idempotensi, flush saat event `online` dan saat halaman dibuka, badge jumlah antrean.
- **Service worker** — cache versioned, cache-first shell / network-first API + timeout, POST tidak di-cache, pembersihan cache lama saat activate.
- **WF3 fail-safe** — urutan archive-dulu-baru-hapus (gagal append = workflow berhenti sebelum delete), JSON korup & non-Delivered dilewati, delete descending by row_number.

## Risiko tersisa & rekomendasi (belum diperbaiki — keputusan Steven)
| ID | Tingkat | Risiko | Rekomendasi |
|----|---------|--------|-------------|
| R-01 | Sedang | **Race condition WF2**: dua admin meng-update resi yang sama dalam hitungan detik → read-modify-write bisa saling menimpa (satu entri riwayat hilang). Probabilitas rendah pada skala tim kecil. | Jangka pendek: SOP satu resi dipegang satu kurir. Jangka panjang: aktifkan queue mode di n8n (concurrency 1) untuk WF2. |
| R-02 | Sedang | Halaman admin & webhook WF2 tanpa autentikasi — siapa pun yang tahu URL bisa memasukkan update. | Tambahkan token statis sederhana (header/field rahasia yang divalidasi di WF2) sebelum go-live. |
| R-03 | Rendah | `startIndex` node delete Google Sheets: perilaku indeks perlu dikonfirmasi di versi n8n yang dipakai (kesesuaian dengan `row_number`). | Tercakup di uji simulasi housekeeping (bagian D testing matrix) — wajib dijalankan di sheet dummy. |
| R-04 | Rendah | Ikon masih placeholder "M". | Ganti dengan aset brand Metro Logistik (nama & ukuran file dipertahankan). |

## Menunggu konfirmasi Steven (sesuai aturan: tidak menghapus tanpa persetujuan)
1. Hapus folder bersarang `Metro Logistic\Metro Logistic\` (duplikat Fase A yang sudah disalin/tergantikan: manifest lama, 2 ikon lama, 3 workflow yang sudah dipindah+dipatch).
2. Hapus `app\_check_config.js` (file bantu verifikasi milik Opus, tidak direferensikan aplikasi).
