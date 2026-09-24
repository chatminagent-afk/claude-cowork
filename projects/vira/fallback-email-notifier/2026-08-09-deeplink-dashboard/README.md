# Deep link dashboard di notifikasi error

**Tanggal:** 2026-08-09 · **QA:** 29/29 lolos · **Status:** siap tempel, belum dipasang

Tujuan: pesan alert WA/email membawa link yang langsung membuka execution yang gagal di n8n mobile dashboard, jadi tinggal tekan **Retry** tanpa mengetik nomor execution dan tanpa membuka UI n8n.

---

## Kenapa bentuknya "tempel kode", bukan import JSON

File export `VIRA Error Notifier` dan `VIRA-PCR Error Notifier` yang ada di repo ini **belum memuat node email-fallback** (`Build Fallback Payload`, `Check Kirimi Response`, `Call Global Email Fallback`).

Artinya salah satu dari dua ini benar:
- kamu belum memasang Bagian B di `../README.md`, atau
- kamu sudah memasangnya di n8n tapi belum export ulang.

Kalau yang kedua, **import JSON penuh akan menghapus jalur email cadanganmu.** Maka yang diberikan di sini cuma isi 1 Code node — aman untuk kedua kemungkinan.

---

## Yang berubah

| Workflow | Node | Perubahan |
|---|---|---|
| `VIRA Error Notifier` (The Scholars) | `Compose Notif` | + baris "📱 Retry dari HP" |
| `VIRA-PCR Error Notifier` (Persada) | `Compose Notif` | + baris "📱 Retry dari HP" |
| `GLOBAL - Email Fallback Notifier` | `Normalize & Compose Email` | + tombol "📱 Retry dari HP" · **+ isi `N8N_BASE` yang selama ini masih placeholder** |

> ⚠️ Temuan sampingan: `N8N_BASE` di `Normalize & Compose Email` masih berisi `https://GANTI-DENGAN-URL-N8N-KAMU`. Selama ini tombol "Buka execution" di email kemungkinan **rusak**. Kode baru sudah mengisinya dengan `https://n8n.srv1270416.hstgr.cloud`. Kalau kamu sudah membetulkannya langsung di n8n, nilainya sama saja.

---

## Hasil: bentuk pesan WA sesudahnya

```
🚨 [VIRA V4] EKSEKUSI GAGAL
Node: Send WA + Verify (Kirimi)
Error: Kirimi HTTP gagal setelah 3 percobaan: connect ETIMEDOUT
Execution: 23443

📱 Retry dari HP:
https://n8n.chatminagent.workers.dev/#/e/23443

🖥️ Buka di n8n:
https://n8n.srv1270416.hstgr.cloud/workflow/TW-E4ZbJgEzRSbsUcST5W/executions/23443

⚠️ Ada pesan user yang kemungkinan TIDAK terbalas. Cek & balas manual.
```

Tap link pertama → dashboard terbuka langsung di execution #23443 → tekan **Retry**. Selesai.

---

## Cara pasang (±10 menit, 3× langkah yang sama)

| # | Workflow | Node | File |
|---|---|---|---|
| 1 | `VIRA Error Notifier` | `Compose Notif` | `1-compose-notif-SCHOLARS.js` |
| 2 | `VIRA-PCR Error Notifier` | `Compose Notif` | `2-compose-notif-PCR.js` |
| 3 | `GLOBAL - Email Fallback Notifier` | `Normalize & Compose Email` | `3-normalize-compose-email.js` |

Untuk masing-masing:

1. Buka workflow-nya di n8n.
2. **Double-click** node yang disebut di tabel.
3. Klik di dalam kotak kode → **Ctrl+A** → **Delete**.
4. Buka file `.js` yang bersangkutan di Notepad → **Ctrl+A** → **Ctrl+C** → paste ke kotak kode n8n.
5. **Back to canvas** → **Ctrl+S**.

Tidak ada node yang ditambah/dihapus, tidak ada koneksi yang diubah, tidak ada Settings yang disentuh.

---

## Prasyarat

Deep link ini memakai fitur `#/e/<id>` yang baru ada di `index.html` hasil pekerjaan 2026-08-08. **Deploy dashboard-nya dulu** (lihat `mobile dashboard/2026-08-08-hasil-QA-dan-cara-deploy.md` §5.1), baru pasang kode ini — kalau tidak, link-nya akan membuka dashboard di halaman biasa, bukan langsung ke execution-nya.

---

## Uji setelah pasang

1. Di n8n, buka `VIRA Error Notifier` → tombol **Execute workflow** (jalankan manual dari Error Trigger).
   WA masuk dengan banyak tanda `-` — itu normal, karena eksekusi manual tidak punya data error asli. Yang dicek: **format pesannya benar dan tidak ada link `/#/e/-` yang rusak.**
2. Uji sungguhan: picu error di workflow Main (mis. ubah URL Kirimi di node `Send WA + Verify (Kirimi)` jadi ngawur), lalu:
   - WA masuk berisi link `📱 Retry dari HP`
   - tap dari HP → dashboard membuka execution itu
   - kembalikan URL Kirimi → tekan **Retry** → hijau, user terbalas

---

## Cakupan QA (29 cek, semua lolos)

- **Sintaks**: ketiga kode lolos parse sebagai `AsyncFunction` (cara n8n mengeksekusi Code node).
- **Jalur normal**: deep link benar · link UI n8n tetap ada · nama node, pesan error, dan nomor execution tetap ada · emoji tampil benar · peringatan "TIDAK terbalas" dipertahankan.
- **Kasus tepi — error di node trigger**: n8n tidak mengirim `execution.id`. Dijaga dengan `/^\d+$/`, jadi **tidak muncul link rusak** `.../#/e/-`; pesan tetap terkirim.
- **Email jalur direct** (Kirimi mati): tombol Retry ada di HTML dan di plain text · `N8N_BASE` terisi · tenant terdeteksi · subject dan isi alert lama tetap utuh.
- **Email jalur lapis-2** (notifier sendiri yang gagal): tidak ada `orig_exec_id`, jadi tombol dashboard tidak dibuat · email tetap terkirim.

Halaman QA-nya bisa dijalankan ulang: buka `mobile dashboard/production/2026-08-09-QA-deeplink-notifier.html` di browser.

---

## Temuan yang TIDAK kuubah (di luar cakupan)

Pada jalur email lapis-2, tenant untuk The Scholars terbaca **`VIRA-?`**, bukan `VIRA-SCHOLARS`. Sebabnya deteksi tenant mencari kata `scholar`/`v4`/`pcr` di nama workflow, sedangkan notifier Scholars bernama `VIRA Error Notifier` — tidak memuat satupun kata itu. Ini perilaku bawaan, bukan akibat perubahan hari ini, dan sudah tercatat sebagai keluaran normal di `../README.md`.

Dampaknya kecil: subject email jadi `🚨 [VIRA-?] ...`, tapi nama workflow tetap terbaca jelas di isi email. Kalau mau dirapikan, cara paling aman adalah **rename workflow-nya** jadi `VIRA-SCHOLARS Error Notifier` — bukan melonggarkan logika deteksi, karena itu akan salah melabeli klien ke-3 nanti.
