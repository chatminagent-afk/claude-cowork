# Migrasi Kirimi → Fonnte — indeks

Dibuat 2026-08-31. Semua file di folder ini **baru**; tidak ada file produksi yang diubah atau ditimpa.

> **Direview ulang 2026-09-01** — dua cacat sungguhan ditemukan dan diperbaiki (guard respons di tiga error notifier, dan `filename` yang hilang di node kirim media), plus satu risiko notifikasi tes nyasar ke klien. Baca [`2026-09-01-perbaikan-pasca-review.md`](2026-09-01-perbaikan-pasca-review.md) sebelum import. File JSON di folder ini sudah versi terbaru.

## Yang ditemukan

14 workflow produksi menyentuh API WhatsApp — bukan hanya workflow utama.

| Klien | Workflow menyentuh WA | Tidak menyentuh WA (abaikan) |
|---|---|---|
| The Scholars | 3 | Topic Harvester (WF-A), Monthly Rollup (WF-B), MSG_BUFFER Cleanup |
| Persada Cisoka | 4 | MSG_BUFFER Cleanup PCR |
| VIRA Personal | 4 | Buffer Cleanup |
| GLOBAL | 3 (1 di antaranya tidak memanggil API, hanya rantai fallback) | Dashboard API, DASH_AUDIT Cleanup |

## Urutan pengerjaan yang disarankan

1. **GLOBAL** dulu — notifier error adalah jaring pengaman. Kalau ia rusak saat klien dimigrasi, kegagalan jadi senyap.
2. **VIRA Personal** — punyamu sendiri, risiko paling rendah, sekaligus uji nyata.
3. **The Scholars** — klien aktif.
4. **Persada Cisoka** — volume paling besar, kerjakan terakhir setelah pola terbukti.

## Berlaku untuk semua klien

- **Buat credential dulu, sebelum import.** n8n → Credentials → *Generic Credential Type* → **Header Auth**. Name: `Authorization`. Value: token device Fonnte, **polos tanpa `Bearer`**. Beri nama credential persis seperti yang tertulis di panduan tiap klien.
- **Import tanpa mengaktifkan.** Semua file sudah `active: false` dan `id` dibuang, jadi n8n membuat workflow baru, bukan menimpa yang lama.
- **Path webhook sengaja dibedakan** dari versi Kirimi, jadi versi lama dan baru bisa hidup berdampingan selama pengujian. Matikan yang lama baru aktifkan yang baru.
- **Atur webhook di dashboard Fonnte per device** — ini di luar file JSON dan paling sering terlewat. Gejalanya: kirim jalan, terima diam total.
- **Paket Fonnte.** Paket Free menempelkan watermark "sent via fonnte" di tiap pesan dan tidak bisa dimatikan lewat API. Hilang mulai paket berbayar. Untuk klien, ini bukan kosmetik — VIRA bicara atas nama Sam / developer. Kuota 1.000/bulan juga terlalu kecil untuk produksi; pilih tier dari volume, bukan dari watermark.
- **Attachment** butuh paket yang mendukung. PCR dan VIRA Personal punya node kirim media; TS tidak.
- **Jangan pakai satu nomor sebagai device pengirim sekaligus tujuan notifikasi.** Tujuh node notifikasi menargetkan `6285155202354`, yang juga terdaftar sebagai device Fonnte "Work". Kalau credential sebuah workflow menunjuk device itu, notifikasinya jadi kirim-ke-diri-sendiri. Node-node itu sudah diberi catatan yang tampil di kanvas n8n.

## Yang berubah secara teknis di semua workflow

| Kirimi | Fonnte |
|---|---|
| `POST api.kirimi.id/v1/send-message`, body JSON | `POST api.fonnte.com/send`, body **form-urlencoded** |
| `POST api.kirimi.id/v1/send-message-file`, multipart | `POST api.fonnte.com/send`, multipart, field `file` tetap binary |
| `user_code` + `secret` + `device_id` di body | header `Authorization: <token>` lewat n8n Credential |
| `phone` | `target` |
| `message` | `message` (tidak berubah) |

Nilai ekspresi `phone` dan `message` dipindahkan **utuh**, tidak ditulis ulang.

## Dua hal yang belum tertutup

1. **`status: true` belum berarti terkirim.** Fonnte membalas `"process": "pending"` — pesan baru masuk antrean. Guard yang terpasang membuktikan Fonnte *menerima* permintaan, bukan bahwa WA *sampai*. Penutupnya webhook *update message status* dari Fonnte. Belum dikerjakan.
2. **Token device TS masih literal** di satu Code node (`Send WA + Verify (Fonnte)`), karena Code node n8n tidak bisa membaca credential. PCR dan VIRA Personal membacanya dari tab CONFIG. Token yang sekarang tertulis sudah terpapar di chat — regenerate sebelum dipakai produksi.
