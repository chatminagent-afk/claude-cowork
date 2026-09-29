# Plan — Membuat Kegagalan VIRA Terlihat & Bisa Di-retry dari HP

**Tanggal:** 2026-08-08
**Cakupan:** VIRA V4 (The Scholars) · VIRA-PCR Main V1.3 + V2.1-Vision (Persada) · VIRA Error Notifier · VIRA-PCR Error Notifier · n8n Mobile Dashboard
**Status:** menunggu persetujuan Steven — **belum dieksekusi**, JSON belum dibuat

---

## 1. Ringkasan keputusan

> **Bukan cuma hapus node "Notify Admin Error".** Yang jadi akar masalah adalah setelan `onError` di node sumbernya. Node notify cuma penumpang di cabang error — kalau dia dihapus duluan tanpa mengubah `onError`, hasilnya lebih buruk: execution tetap `success` (tidak bisa di-retry) **dan** tidak ada notifikasi sama sekali.

Urutan yang benar: **ubah `onError` → default (Stop Workflow)** dulu, node notify jadi yatim, baru dihapus.

Sasaran akhir: setiap kegagalan yang membuat user tidak terbalas → execution **merah** → notifikasi WA/email otomatis (Error Notifier yang sudah ada) → Steven buka execution ID di mobile dashboard → **Retry** → alur lanjut dari node yang gagal dan user akhirnya terbalas.

---

## 2. Rantai sebab (kenapa retry sekarang tidak berguna)

```
onError: "Continue (using error output)"
   ↓
n8n menandai execution finished = true, status = "success"
   ↓
├─ Dashboard mobile: list pakai includeData=false → badge SUCCESS (buta)
├─ Error Trigger TIDAK jalan → Error Notifier diam → tidak ada notif WA/email
└─ n8n MENOLAK retry di sisi server:
      if (execution.finished) throw "The execution succeeded, so it cannot be retried."
```

Tiga konsekuensi itu semuanya berasal dari satu setelan. Memperbaiki guard `canRetry` di dashboard **tidak akan menolong** — penolakannya terjadi di server n8n, bukan di UI.

### Fakta n8n yang jadi dasar (terverifikasi dari source & docs)

| # | Fakta | Sumber |
|---|---|---|
| 1 | `onError: continue` / `continue using error output` → execution ditandai **success** | perilaku n8n, dikonfirmasi PSA komunitas |
| 2 | Error Trigger **hanya** jalan saat execution benar-benar `error` | docs Error Trigger |
| 3 | Execution `finished=true` **tidak bisa** di-retry: `"The execution succeeded, so it cannot be retried."` | `packages/cli/src/executions/execution.service.ts` |
| 4 | Retry **melanjutkan dari node yang gagal**, `runData` node yang sudah sukses dipertahankan | `execution.service.ts` — `nodeRunData.pop(); // Stack will determine what to run next` |
| 5 | `loadWorkflow: true` melempar `WorkflowOperationError` kalau ada node yang **dihapus/di-rename** | `execution.service.ts` |

**Fakta #4 adalah kabar baik terbesar:** retry tidak mengulang dari webhook. Tidak ada duplikasi append MSG_BUFFER, tidak ada dobel biaya AI, tidak ada dobel kirim WA untuk node yang sudah sukses.

**Fakta #5 adalah jebakan operasional:** setelah node dihapus, me-retry execution **lama** dengan centang "pakai versi workflow terbaru" akan error. Lihat §4.

---

## 3. Prinsip desain

> **Node yang throw harus node yang juga mengulang aksinya saat di-retry.**

Konsekuensi langsung: validator terpisah (`Check API Response`) yang throw membuat execution merah — bagus untuk visibilitas — tapi retry-nya percuma, karena mengulang validator tidak mengirim ulang apa pun. Ini yang ditangani Fase 2.

---

## 4. Fase 0 — Prasyarat (wajib, sebelum menyentuh apa pun)

| # | Langkah | Alasan |
|---|---|---|
| 0.1 | Export JSON: `VIRA V4`, `VIRA-PCR Main V1.3`, `VIRA-PCR Main V2.1-Vision`, `VIRA Error Notifier`, `VIRA-PCR Error Notifier`. Simpan sebagai `2026-08-08-pre-retry-patch/` | rollback |
| 0.2 | **Habiskan backlog execution lama.** Retry semua execution merah yang masih mau di-retry **sekarang**, sebelum node dihapus | fakta #5 — setelah node hilang, retry lama dengan `loadWorkflow:true` akan error |
| 0.3 | Catat: untuk execution yang dibuat **sebelum** patch, retry harus dengan checkbox "pakai versi workflow terbaru" **OFF** | idem |
| 0.4 | Pastikan `errorWorkflow` masih terpasang: V4 → `ZKsINjA7ZC8c9yRHWp3ud`, PCR → `rBsq-mGgHfqfwbz3YmwxI` (sudah terpasang per audit) | jalur notifikasi |
| 0.5 | Pastikan email fallback (Bagian A+B di `fallback_error_VIRA_shared-n8n/README.md`) sudah aktif | kalau Kirimi mati, notifnya juga mati |

---

## 5. Fase 1 — Ubah `onError`, lalu hapus node yatim

### 5.1 The Scholars — `VIRA V4` (59 node)

**Ubah setelan (tab Settings di dalam node):**

| Node | `On Error` sekarang | → Jadi | Setelan lain |
|---|---|---|---|
| `Reply Chat Kirimi` | Continue (using error output) | **Stop Workflow** | Retry On Fail: on, Max Tries **3**, Wait **5000** |
| `Check API Response` | Continue (using error output) | **Stop Workflow** | — |
| `AI Agent` | Continue (using error output) | **Stop Workflow** | Retry On Fail: **on** (sekarang OFF!), Max Tries **3**, Wait **5000** |
| `Append MSG_BUFFER` | Continue (using error output) | **Stop Workflow** | Retry On Fail: on, Max Tries **3**, Wait 2000 |

> Catatan: keempat node ini juga menyimpan field lama `continueOnFail: true` di JSON. Mengubah dropdown ke *Stop Workflow* di UI sudah membereskannya; kalau mengedit JSON langsung, hapus juga key `continueOnFail`.

**Hapus node (semuanya jadi yatim setelah perubahan di atas):**

| Node dihapus | Kenapa aman |
|---|---|
| `Notify Admin API Error` | Digantikan Error Notifier yang informasinya lebih lengkap (nama workflow, nama node, pesan error, execution ID, URL) |
| `Delete_Pending_Msg_Error` | Hanya dijangkau dari `Notify Admin API Error`. **Menghapusnya memperbaiki bug** — lihat §7 |
| `Reply Error` | Fallback WA "Maaf, saya belum bisa membantu" ke user — dibuang sesuai keputusan Steven |
| `Delete_Pending_Msg_Bot_Off1` | Hanya dijangkau dari `Reply Error`. Sama, memperbaiki bug watermark |
| `Notify User Error` | Fallback WA "Maaf sedang ada kendala teknis" — dibuang, dan node ini memang sudah buntu (tidak punya koneksi keluar) |

**JANGAN disentuh — namanya mirip tapi bukan error handler:**

| Node | Perannya |
|---|---|
| `Notify Admin Unknown` | Notifikasi bisnis di jalur sukses (pertanyaan tak terjawab) |
| `Notify Talk to Sam` | Notifikasi bisnis di jalur sukses (user minta bicara dengan Sam) |
| `Delete_Pending_Msg`, `Delete_Pending_Msg_Bot_Off` | Watermark di jalur normal — **wajib tetap ada** |
| `FAQ Retrieve` (`continueRegularOutput`) | Degradasi anggun: FAQ kosong bukan kegagalan mengirim |
| `Send GForm Link`, `Send GForm Clarify` | Sudah `disabled` di produksi |

---

### 5.2 Persada — `VIRA-PCR Main V1.3` (88 node)

**Ubah setelan:**

| Node | → Jadi | Setelan lain |
|---|---|---|
| `Reply Chat Kirimi` | **Stop Workflow** | Retry On Fail: on, Max Tries 3, Wait 5000 |
| `Check API Response` | **Stop Workflow** | — |
| `AI Agent` | **Stop Workflow** | Retry On Fail: **on** (sekarang OFF), Max Tries 3, Wait 5000 |
| `Append MSG_BUFFER` | **Stop Workflow** | Retry On Fail: on, Max Tries 3, Wait 2000 |
| `Download Media` | **Stop Workflow** | Retry On Fail: on, Wait 2000 |
| `Send Media Kirimi` | **Stop Workflow** | Retry On Fail: on, Wait 2000 |
| `Download Media 2` | **Stop Workflow** | Retry On Fail: on |
| `Send Media Kirimi 2` | **Stop Workflow** | Retry On Fail: on |

> **Kenapa node media ikut diubah, dan kenapa itu aman:** keempatnya berjalan **setelah** `Check API Response` sukses — artinya balasan teks ke user **sudah terkirim**. Karena retry melanjutkan dari node yang gagal (fakta #4), retry hanya mengulang unduh/kirim media, **tidak** mengirim ulang teksnya. Kegagalan media jadi terlihat dan bisa diperbaiki dari HP tanpa efek samping.

**Hapus node:**

| Node dihapus | Kenapa aman |
|---|---|
| `Notify Admin API Error` | Digantikan Error Notifier |
| `Mark Buffer Consumed (Kirimi Error)` | Hanya dijangkau dari node di atas; memperbaiki bug watermark (§7) |
| `Reply Error` | Fallback WA ke user — dibuang |
| `Mark Buffer Consumed (AI Agent)` | Hanya dijangkau dari `Reply Error`; idem |
| `Notify User Error` | Fallback WA ke user; sudah buntu |
| `Notify Admin Media Error` | Yatim setelah keempat node media diubah |

**JANGAN disentuh:**

| Node | Perannya |
|---|---|
| `Notify Media Team` | Notifikasi bisnis (jalur `IF Media Manual`) |
| `Notify Field Team` | Notifikasi bisnis (handover ke tim lapangan) |
| `Notify Admin Unknown` | Notifikasi bisnis |
| `Notify Talk to Admin` | Notifikasi bisnis |
| `Mark Buffer Consumed (Regular)`, `Mark Buffer Consumed (Bot_Off)` | Watermark jalur normal — **wajib tetap ada** |
| `Summarize Handover` (`continueRegularOutput`) | Degradasi anggun |

---

### 5.3 ⚠️ Persada — `VIRA-PCR Main V2.1-Vision` (98 node) — **jangan dilupakan**

V2.1 masih menunggu deploy dan struktur error-handling-nya **identik** dengan V1.3 (audit: node notify error sama persis, nama/`onError`/koneksi tidak berubah; `settings.errorWorkflow` juga sama).

**Kalau V2.1 di-deploy tanpa patch yang sama, seluruh pekerjaan ini ter-revert diam-diam.**

Terapkan §5.2 apa adanya ke V2.1. Satu node tambahan yang khas V2.1:

| Node | `onError` | Keputusan |
|---|---|---|
| `Analisa Gambar (Claude Haiku)` | `continueRegularOutput` | **Biarkan.** Gagal analisa gambar = degradasi anggun (alur tetap ke `Rakit Konteks Gambar`), bukan pesan user yang hilang. Catat sebagai *known blind spot*. |

---

## 6. Fase 2 — Kegagalan senyap Kirimi (HTTP 200 + `status:false`)

**Masalah:** `Check API Response` throw → execution merah ✅ → tapi retry mengulang **validator** dengan respons Kirimi lama → throw lagi → WA tidak pernah terkirim ulang ❌.

Kode pemicunya (identik di kedua bot, versi PCR sedikit lebih ketat):

```js
const explicitFail = responseData.success === false || responseData.status === false;
const isSuccess = !explicitFail && ( ... );
if (!isSuccess) { throw new Error('Kirimi API gagal: ' + JSON.stringify(responseData)); }
```

### Opsi A — Gabung kirim + validasi jadi satu node (direkomendasikan)

Ganti pasangan `Reply Chat Kirimi` + `Check API Response` dengan **satu Code node** (usul nama: `Send WA + Verify (Kirimi)`).

**Spesifikasi (bukan implementasi):**

- Lakukan POST ke `https://api.kirimi.id/v1/send-message` lewat `this.helpers.httpRequest`, body sama persis dengan node HTTP Request sekarang (`user_code`, `secret`, `device_id`, `receiver`, `message`).
- Terapkan logika `isSuccess` yang sudah ada; `throw` kalau gagal.
- **Kembalikan respons Kirimi apa adanya sebagai item** — persis seperti `Check API Response` yang sekarang `return [input]`.
- Settings: `On Error` = Stop Workflow, Retry On Fail = on, Max Tries 2, Wait 5000.

**Koneksi yang harus dipindahkan** (jumlah target berbeda antar bot — jangan sampai ada yang tertinggal):

| Workflow | Masuk dari | Keluar ke |
|---|---|---|
| V4 | `Wait1` | `Extract & Prepare Data`, `Delete_Pending_Msg`, `Update STATS - Greeting Flag` (3 target) |
| PCR V1.3 / V2.1 | `Wait1` | `Extract & Prepare Data`, `Mark Buffer Consumed (Regular)`, `Update STATS - Greeting Flag`, **`IF Send Media`** (4 target) |

**Kenapa aman (sudah diverifikasi):**
- Tidak ada node mana pun yang mereferensikan `Reply Chat Kirimi` atau `Check API Response` lewat `$('nama')` — dicek di V4, PCR V1.3, dan PCR V2.1. Nol ekspresi yang pecah.
- Kontrak output tidak berubah, jadi seluruh hilir tidak perlu disentuh.
- **Hanya pengiriman teks** yang digabung. `Send Media Kirimi` (multipart) tidak disentuh.

**Yang dikorbankan:**
- Node HTTP Request hasil import curl berubah jadi ±20 baris JS. Kalau Kirimi mengubah API, edit di kode, bukan di form.
- Kredensial tetap plaintext di node — **sama seperti sekarang**, tidak lebih buruk.

### Opsi B — Biarkan terpisah

Execution tetap merah dan notif tetap datang, tapi untuk kelas kegagalan ini tombol retry di HP akan gagal lagi di validator dan kamu tetap harus buka UI n8n.

**Rekomendasi:** jalankan Fase 1 dulu, pantau 3–7 hari, baru kerjakan Opsi A. Kalau di periode itu ternyata mayoritas kegagalan adalah HTTP-level (bukan `status:false`), Fase 2 boleh ditunda tanpa rugi.

---

## 7. Efek samping yang justru **membaik**: watermark `buffer_done_ts`

`Cek_user_status` mengonsumsi pesan dengan aturan:

```js
const doneTs = Number(debounceRow['buffer_done_ts'] || 0) || 0;
.filter(r => r.ts > doneTs && r.ts <= myTs && (myTs - r.ts) < 30*60*1000 && r.message !== '')
```

Perilaku **sekarang** (bug): saat `Reply Chat Kirimi` gagal, cabang error tetap menjalankan `Delete_Pending_Msg_Error` / `Mark Buffer Consumed (Kirimi Error)` yang **menaikkan watermark**. Pesan user ditandai sudah dikonsumsi padahal user tidak pernah dibalas → konteksnya hilang permanen.

Perilaku **setelah patch**: execution gagal sebelum sempat menaikkan watermark. Pesan tetap *unconsumed*. Dua jalan pemulihan, keduanya benar:
1. Steven retry → alur lanjut → `Delete_Pending_Msg` / `Mark Buffer Consumed (Regular)` di jalur normal menaikkan watermark sebagaimana mestinya.
2. Steven tidak sempat retry, tapi user mengirim pesan lagi dalam **30 menit** → pesan lama + baru digabung dan dijawab sekaligus oleh AI.

Batasnya: kalau tidak di-retry **dan** user diam >30 menit, `MAX_AGE_MS` membuang pesan lama. Sama seperti sekarang, tapi tidak lebih buruk.

---

## 8. Fase 3 — Notifier: tambahkan deep link ke dashboard

`Compose Notif` di kedua Error Notifier sudah memuat `execution.id` dan `execution.url` (URL UI n8n — justru yang susah dibuka dari HP). Tambahkan satu baris berisi link dashboard mobile:

```
https://n8n.chatminagent.workers.dev/#/e/{execution.id}
```

Terapkan di **tiga** tempat:
1. `Compose Notif` — VIRA Error Notifier (The Scholars)
2. `Compose Notif` — VIRA-PCR Error Notifier (Persada)
3. `Normalize & Compose Email` — GLOBAL Email Fallback Notifier (tombol link di email)

Sekalian rapikan (temuan audit, bukan blocker): `Notify Admin Error` di VIRA-PCR Error Notifier punya key `device_id` **dobel** di `bodyParameters`, dan kredensial Kirimi-nya literal hardcoded sementara workflow Main mengambilnya via `$('Parse Config')`.

---

## 9. Fase 4 — n8n Mobile Dashboard

File tunggal: `mobile dashboard/production/upload/index.html`. Deploy ulang sesuai README (worker `n8n`, lalu hard refresh; `sw.js` tidak berubah).

| # | Perubahan | Kenapa | Perkiraan |
|---|---|---|---|
| 4.1 | **Input "Buka execution #___"** di tab Executions → panggil `openExecution(id)` yang sudah ada | Alurmu adalah "dapat notif → cari nomor execution". Sekarang list-nya 20/halaman **tanpa pencarian sama sekali** — ini gap terbesar di dashboard | ~20 baris |
| 4.2 | **Hash route `#/e/<id>`** → saat halaman dibuka dengan hash itu, langsung buka drawer execution tersebut | Bikin link di WA/email jadi satu-ketukan. Ini pasangan dari Fase 3 | ~15 baris |
| 4.3 | Tampilkan `retryOf` / `retrySuccessId` di drawer, mis. badge "sudah di-retry → #12345" | Setelah retry sukses, execution **lama tetap merah** (n8n bikin execution baru). Tanpa penanda ini kamu akan retry dua kali | ~10 baris |
| 4.4 | Tombol **"Deep scan 20 terakhir"** (opsional): ambil detail 20 execution terakhir dengan `includeData=true`, tandai yang status `success` tapi ada `run.error` di `runData` | Jaring pengaman untuk sisa `continueRegularOutput` yang sengaja dipertahankan (`FAQ Retrieve`, `Summarize Handover`, `Analisa Gambar`). Sengaja on-demand karena 20 request sekaligus | ~40 baris |

**Tidak perlu diubah:** guard `canRetry = ['error','crashed']` sudah benar — n8n juga menolak retry execution sukses di sisi server. Logika `extractError()` di drawer juga sudah memindai `runData` tanpa peduli status; tidak perlu disentuh.

---

## 10. Matriks QA

Uji di **kedua** bot. Untuk tiap baris, catat: status execution · notif WA masuk? · email fallback masuk? · execution ID terlihat di dashboard? · retry berhasil? · user akhirnya terbalas? · tidak ada duplikasi?

| # | Skenario | Cara memicu | Harapan |
|---|---|---|---|
| Q1 | Kirimi mati total | Ubah URL `Reply Chat Kirimi` → `.../send-message-ngasal` | Execution **error** · notif WA + email · retry (setelah URL dibalikkan) mengirim ulang WA dan alur lanjut sampai `Update to STATS` |
| Q2 | Kirimi 200 tapi `status:false` | Ubah `receiver` → `628000000000` | Fase 1: execution **error**, notif masuk, retry **gagal lagi di validator** (ekspektasi benar). Fase 2 (Opsi A): retry **berhasil kirim ulang** |
| Q3 | Google Sheets tidak terjangkau | Rename tab `STATS` sebentar, kirim WA, lalu balikkan | Execution **error** di node GS · retry lanjut dari node itu · **tidak ada** duplikat baris MSG_BUFFER |
| Q4 | AI Agent gagal | Kosongkan/rusak kredensial Anthropic sementara | 3x retry otomatis dulu · lalu execution **error** · user tidak dapat pesan apa pun · retry menghasilkan jawaban asli |
| Q5 | `Append MSG_BUFFER` gagal | Rename tab `MSG_BUFFER` sebentar | Execution **error** · retry lanjut · pesan tetap terjawab |
| Q6 | Media gagal (PCR saja) | Rusak `mediaUrl` di sheet PRODUK/LINKS | Execution **error** di `Download Media` · **teks tetap terkirim sekali** dan tidak dikirim ulang saat retry |
| Q7 | Watermark | Picu Q1, jangan retry, lalu suruh user kirim pesan lagi dalam <30 menit | Pesan lama + baru **digabung** dan dijawab sekaligus |
| Q8 | Non-regresi notifikasi bisnis | Kirim pertanyaan di luar FAQ (`IF Unknown`); minta bicara dengan Sam/admin | `Notify Admin Unknown` & `Notify Talk to Sam`/`Notify Talk to Admin` **tetap jalan**, execution tetap hijau |
| Q9 | Non-regresi happy path | Chat normal | Hijau · user terbalas · `Counter`, `greeting_sent`, `buffer_done_ts` terisi benar |
| Q10 | Alur ops utuh (end-to-end) | Picu Q1 dari HP saja | Notif WA masuk → ketuk link → dashboard membuka execution itu langsung → Retry → hijau · **tanpa membuka UI n8n sama sekali** |
| Q11 | Retry ganda | Retry execution yang sudah pernah sukses di-retry | Dashboard menampilkan penanda "sudah di-retry" (4.3); n8n menolak dengan `"...cannot be retried"` |
| Q12 | Execution lama | Retry execution dari **sebelum** patch, centang "pakai versi workflow terbaru" **ON** | Gagal dengan `WorkflowOperationError` — **ekspektasi benar** (fakta #5). Ulangi dengan centang **OFF** → berhasil |

---

## 11. Risiko & rollback

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Volume execution merah melonjak setelah patch | Notifikasi WA/email membanjir | Ini memang kegagalan yang selama ini tersembunyi, bukan kegagalan baru. Pantau hari pertama; kalau bising, naikkan `Max Tries` supaya lebih banyak yang sembuh sendiri |
| User tidak dapat balasan apa pun saat AI Agent gagal | UX turun | Keputusan Steven, sudah diambil. Diredam `retryOnFail` 3× dan self-healing watermark (§7) |
| Retry execution lama gagal | Backlog macet | Fase 0.2 — habiskan backlog dulu; setelah patch pakai centang OFF |
| Salah hapus node notifikasi bisnis | Lead hilang diam-diam | Daftar "JANGAN disentuh" di §5.1/§5.2; Q8 di matriks QA |
| V2.1-Vision di-deploy tanpa patch | Semua pekerjaan ini ter-revert | §5.3 — patch V2.1 di sesi yang sama |
| Fase 2 Opsi A merusak hilir | Balasan berhenti total | Kontrak output dipertahankan; nol referensi `$('nama')`; uji di workflow duplikat sebelum menyentuh produksi |

**Rollback:** import ulang JSON dari `2026-08-08-pre-retry-patch/`. Perubahan dashboard: deploy ulang `index.html` versi sebelumnya (arsip di `mobile dashboard/archive/` **usang** — pakai salinan dari Fase 0, bukan arsip itu).

---

## 12. Yang sengaja **tidak** diubah

| Hal | Alasan |
|---|---|
| `FAQ Retrieve` (V4), `Summarize Handover`, `Notify Media Team`, `Notify Field Team` (PCR) — `continueRegularOutput` | Degradasi anggun, bukan pesan user yang hilang. Tercakup jaring pengaman 4.4 |
| `Analisa Gambar (Claude Haiku)` (V2.1) | Idem — *known blind spot*, dicatat sengaja |
| Guard `canRetry` di dashboard | Sudah benar; server n8n juga menolak retry execution sukses |
| Workflow Follow-up & MSG_BUFFER Cleanup | Di luar cakupan permintaan ("workflow utama"). Layak diaudit terpisah |
| Kredensial Kirimi plaintext di body node | Temuan nyata tapi isu keamanan terpisah, jangan dicampur ke patch ini |

---

## 13. Urutan eksekusi & titik henti

```
Fase 0  Backup + habiskan backlog                            ~20 mnt   ← wajib duluan
Fase 1  V4 (4 setelan, 5 node dihapus)                       ~30 mnt
        PCR V1.3 (8 setelan, 6 node dihapus)                 ~40 mnt
        PCR V2.1 (patch identik)                             ~40 mnt
        ▸ QA Q1, Q3, Q4, Q5, Q8, Q9  ─── HENTI: validasi produksi 3–7 hari
Fase 3  Deep link di 3 notifier                              ~20 mnt
Fase 4  Dashboard 4.1–4.3 (4.4 opsional)                     ~1,5 jam
        ▸ QA Q10, Q11, Q12
Fase 2  Gabung kirim+validasi (Opsi A) — setelah data 3–7 hari  ~1 jam
        ▸ QA Q2, Q6, Q9
```

**Yang masih menunggu keputusan Steven:**
1. Setujui plan ini secara keseluruhan?
2. Fase 2 Opsi A (gabung) atau Opsi B (biarkan terpisah)? — boleh diputuskan nanti setelah data 3–7 hari
3. Node media PCR ikut diubah (§5.2)? Direkomendasikan ya, argumennya di §5.2
4. Item 4.4 (deep scan) dikerjakan atau dilewati?
