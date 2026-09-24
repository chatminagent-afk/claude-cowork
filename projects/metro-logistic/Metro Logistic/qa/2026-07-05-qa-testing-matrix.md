# QA Testing Matrix — Metro Logistik Tracking PWA
**Disusun oleh:** Fable (QA Lead) · **Tanggal:** 5 Juli 2026
**Benchmark:** Shopee Express, JNE, J&T — timeline harus akurat, terbaru di atas, tiap step menampilkan waktu, status, lokasi, dan petugas.

Format hasil: PASS / FAIL / BLOCKED. Jalankan di staging setelah `config.js` diisi URL webhook asli.

## A. Halaman Publik — Cek Resi & Timeline
| ID | Skenario | Langkah | Hasil Diharapkan |
|----|----------|---------|------------------|
| PUB-01 | Cek 1 resi valid | Masukkan 1 resi, Lacak | Kartu tampil: pengirim, penerima, status terakhir, timeline lengkap |
| PUB-02 | Multi-resi (koma) | `RESI1, RESI2, RESI3` | 3 kartu, data tidak tertukar antar-resi |
| PUB-03 | Multi-resi (baris baru) | 3 resi dipisah Enter | Sama seperti PUB-02 |
| PUB-04 | Campuran valid + tak dikenal | 1 valid + 1 ngawur | Kartu valid normal; kartu lain "resi tidak ditemukan", tanpa error JS |
| PUB-05 | Resi huruf kecil / spasi tepi | ` mli-001 ` | Ternormalisasi (trim + uppercase), tetap ditemukan |
| PUB-06 | **Akurasi urutan timeline** | Resi dengan ≥5 riwayat (Manifest→Delivered) | Terbaru DI ATAS; urutan = kebalikan array backend; waktu format Indonesia + WIB; step teratas ter-highlight; Delivered hijau + centang |
| PUB-07 | Riwayat 1 entri | Resi baru (baru Manifest) | Timeline 1 step, tanpa garis menggantung |
| PUB-08 | Filter tanggal | Set rentang yang memotong riwayat | Step di luar rentang tersembunyi + hitungan step tersembunyi tampil |
| PUB-09 | Filter status | Pilih "Transit" | Hanya step Transit tampil per kartu |
| PUB-10 | Filter tanpa hasil | Rentang tanggal kosong riwayat | Pesan/state kosong yang jelas, bukan kartu blank |
| PUB-11 | Status di luar enum (mis. CATATAN_SISTEM) | Injeksi data uji | Badge netral fallback, tidak crash |
| PUB-12 | Riwayat_Posisi_JSON korup | Rusak manual di sheet uji | WF1 kirim `riwayat_error:true`; UI tampilkan pesan sopan |
| PUB-13 | Anti-XSS | Lokasi berisi `<img src=x onerror=alert(1)>` | Tampil sebagai teks, tidak dieksekusi |

## B. Halaman Admin Lapangan
| ID | Skenario | Langkah | Hasil Diharapkan |
|----|----------|---------|------------------|
| ADM-01 | Update resi eksisting | Isi lengkap, submit | Sukses + total_riwayat; entri baru muncul paling atas di halaman publik |
| ADM-02 | Resi baru | No resi belum ada di sheet | Baris baru dibuat, riwayat 1 entri |
| ADM-03 | **Nama admin kosong** | Kosongkan nama, submit | Ditolak client-side, error inline; server juga menolak (uji via curl langsung) |
| ADM-04 | Nama admin spasi-saja | `"   "` | Sama dengan ADM-03 (trim → kosong) |
| ADM-05 | Field lain kosong | Uji tiap field satu per satu | Error inline per field, fokus/scroll ke field bermasalah |
| ADM-06 | Status di luar enum via curl | POST status "Terbang" | HTTP 400 `{success:false}` |
| ADM-07 | Nama admin dipersist | Submit sukses, reload halaman | Nama terisi otomatis dari localStorage |
| ADM-08 | Double-submit | Klik submit 2x cepat | Tombol disabled saat mengirim; tidak ada entri ganda |
| ADM-09 | 2 admin update resi sama hampir bersamaan | 2 device, jeda <5 dtk | Kedua entri masuk; verifikasi tidak ada yang tertimpa (risiko race — lihat catatan QC) |

## C. Offline / Low-Signal (target: HP low-end pekerja lapangan)
| ID | Skenario | Langkah | Hasil Diharapkan |
|----|----------|---------|------------------|
| OFF-01 | Publik offline, ada cache | Lacak resi → matikan jaringan → lacak lagi | Banner offline + hasil cache terakhir tampil |
| OFF-02 | Publik offline, tanpa cache | Fresh install, offline, lacak | Pesan error jaringan yang jelas, bukan spinner abadi |
| OFF-03 | **Admin submit saat offline** | Airplane mode, submit update | Masuk antrean, badge antrean +1, feedback jelas |
| OFF-04 | Auto-flush saat online | Nyalakan jaringan kembali | Antrean terkirim otomatis, badge kembali 0, data masuk sheet |
| OFF-05 | Flush saat buka halaman | Antre offline → tutup app → online → buka app | Antrean terkirim saat halaman dibuka |
| OFF-06 | Anti-duplikat antrean | Submit sama saat offline berkali-kali dgn app restart | client_id unik; tidak ada duplikat entri di antrean |
| OFF-07 | Sinyal lambat (throttle 2G di DevTools) | Lacak resi | Timeout 8 dtk + retry backoff; UI tidak freeze |
| OFF-08 | Install PWA Android | Chrome → prompt install | Terpasang, buka standalone, ikon benar |
| OFF-09 | Install PWA iOS | Safari → Bagikan → Add to Home Screen | Terpasang; petunjuk manual iOS tampil di banner |
| OFF-10 | Update versi SW | Deploy versi baru | Cache lama terhapus (versioned), shell terupdate |

## D. Simulasi Workflow 3 — Housekeeping (WAJIB sebelum aktif di produksi)
**Prinsip: tidak boleh ada data aktif yang terhapus/terarsip.** Gunakan spreadsheet DUMMY (copy struktur produksi) + Archive dummy. Jalankan WF3 manual (Execute Workflow), bukan menunggu cron.

Seed data uji (8 baris):
| Baris | Status_Terakhir | Waktu Delivered di riwayat | Harus diarsip? |
|-------|-----------------|---------------------------|----------------|
| HK-1 | Delivered | 45 hari lalu | ✅ YA |
| HK-2 | Delivered | 31 hari lalu | ✅ YA |
| HK-3 | Delivered | 29 hari lalu | ❌ TIDAK (belum 30 hari) |
| HK-4 | Delivered | 30 hari lalu tepat (batas) | ❌ TIDAK (aturan: > 30 hari) |
| HK-5 | Transit | update terakhir 90 hari lalu | ❌ TIDAK (bukan Delivered — data aktif!) |
| HK-6 | Delivered | riwayat JSON korup | ❌ TIDAK (korup dilewati demi keamanan) |
| HK-7 | Delivered | riwayat tanpa entri Delivered, Timestamp_Update 40 hari lalu | ✅ YA (fallback Timestamp_Update) |
| HK-8 | Delivered, No_Resi kosong | 45 hari lalu | ❌ TIDAK (guard QC-FIX No_Resi kosong) |

Verifikasi pasca-run:
1. Archive berisi PERSIS HK-1, HK-2, HK-7 + kolom Tanggal_Diarsipkan terisi.
2. Sheet Utama tersisa PERSIS HK-3, HK-4, HK-5, HK-6, HK-8 — hitung baris sebelum/sesudah: 8 → 5.
3. Baris yang dihapus dari Utama = baris yang ada di Archive, cocok 1:1 per No_Resi (tidak ada yang hilang tanpa arsip, tidak ada yang terarsip ganda).
4. Uji gagal-aman: run kedua kalinya → tidak ada aksi (kandidat sudah kosong).
5. Uji putus di tengah: nonaktifkan sementara akses ke Archive (ganti ID jadi salah) → workflow error di node Append → PASTIKAN tidak ada baris yang terhapus dari Utama.
6. Setelah semua PASS di dummy → baru pasang ID produksi & aktifkan schedule.
