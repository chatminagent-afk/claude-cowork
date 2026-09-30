---
name: laptop-tanpa-runtime-js
description: "Tidak ada node/deno/bun di laptop ini, TAPI py_mini_racer (V8) terpasang — node Code n8n bisa dieksekusi sungguhan, bukan cuma dicek sintaks; tree-sitter untuk sintaks, esprima terlalu tua"
metadata:
  node_type: memory
  type: reference
  originSessionId: c8117eff-be65-4842-aa66-da4a292d6f00
  modified: 2026-09-16T07:05:25.945Z
---

Di laptop Steven **tidak ada runtime JavaScript CLI**: `node`, `deno`, `bun`, `qjs` semuanya tidak
terpasang. Tapi **koreksi penting (2026-09-10): itu bukan berarti JS tidak bisa dijalankan.**

**`py_mini_racer` terpasang di Python dan itu V8 sungguhan.** Node Code n8n bisa **dieksekusi utuh**,
bukan sekadar dicek sintaks. Ini jauh lebih kuat daripada validasi statis dan sudah terbukti
menangkap bug yang tree-sitter lolos begitu saja.

```python
from py_mini_racer import MiniRacer
ctx = MiniRacer()
ctx.eval(SHELL)   # definisikan runNode() yang membungkus jsCode dgn new Function
```

Pola harness yang bekerja: bungkus `jsCode` dengan `new Function('$','$input','console', code)`,
lalu suntik stub. `$ = name => ({first, all, last})` yang mengambil dari dict `DATA` dan
**melempar error kalau nama node tidak ada di dict** — itu yang membuat stub salah nama langsung
kelihatan. Init MiniRacer lambat (~2 menit), jadi jalankan seluruh suite dalam **satu** proses
background, jangan sekali per kasus.

**Koreksi 2026-09-16 soal kecepatan:** yang lambat (~1–2 menit) cuma **`import py_mini_racer`
pertama kali di sesi** (cold load V8). Sesudah itu `MiniRacer()` praktis instan — satu suite yang
membuat **372 instance** (satu per kasus uji) selesai dalam hitungan detik. Jadi tidak perlu
memaksakan satu instance dipakai ulang; yang wajib dihindari cuma import berulang di proses baru.

**Jebakan exit (2026-09-16):** kalau instance `MiniRacer` masih dipegang variabel level modul saat
skrip selesai, **prosesnya tidak pernah keluar** — thread V8 menahannya. Gejalanya menipu: semua
`print` sudah keluar dan kerjanya selesai dalam 0,1 detik, tapi perintahnya kena timeout (dan kalau
di-pipe ke `tail`, output-nya tidak terlihat sama sekali sehingga terbaca seperti hang di awal).
Tutup dengan `sys.stdout.flush(); os._exit(kode)` di akhir skrip.

**Dua jebakan harness yang sudah memakan waktu** (gejalanya: kegagalan palsu, bukan error):
1. Stub `FAQ Retrieve` tanpa field `_diag` → canary `dataOutage` di `Process All` menyala dan
   `batalkanAksi()` mematikan `isScheduleSurvey`. Semua kasus tampak gagal padahal patch benar.
2. Stub pakai nama node yang salah (`Read STATS` padahal kodenya `$('Read User STATS')`) — dan
   pemanggilan itu dibungkus try/catch, jadi `rows = []` secara senyap. Lihat
   [[n8n-referensi-node-mati]].
Sebelum menyimpulkan "patch rusak", cek dulu apakah stub-nya yang memicu jalur degradasi.

Untuk cek **sintaks** saja (cepat, tanpa init V8), pakai **tree-sitter**: parse tiap `jsCode`, lalu
telusuri pohonnya untuk node bertipe `ERROR` atau `is_missing`.

```bash
python -m pip install tree-sitter tree-sitter-javascript
```

**Jangan pakai `esprima`** (pip): terlalu tua untuk JS modern — gagal pada optional chaining `?.`,
object spread `{...x}`, regex unicode `\p{L}` + flag `u`, dan `return` di top level (normal di node
Code n8n). Pada workflow VIRA PCR, esprima gagal di **19 dari 19** node Code termasuk yang tidak
disentuh.

Tambahan checker yang wajib sejak 2026-09-10: **scan karakter kontrol liar** (U+0000/07/08/0B/0C)
di semua `jsCode`. Tree-sitter menerima karakter itu tanpa keluhan, padahal `\b` yang tanpa sengaja
jadi BACKSPACE membuat regex gagal senyap. Lihat [[heredoc-makan-backslash]].

**Why:** tanpa kontrol, "parser gagal" gampang disalahartikan sebagai "patch-ku rusak" dan memicu
perbaikan atas bug yang tidak ada. Dan tanpa eksekusi, bug logika lolos ke produksi.

**How to apply:** cek sintaks + karakter kontrol pada file **sebelum** dan **sesudah** patch (file
sebelum patch = kelompok kontrol). Lalu **eksekusi node utuh di MiniRacer** dengan data replay dari
execution n8n yang nyata — jangan cuma menguji blok yang kamu ubah secara terisolasi, karena guard
dan canary di bagian lain node bisa membatalkan hasilnya. Sampaikan ke Steven mana yang terverifikasi
lewat eksekusi dan mana yang statis saja.

Terkait: [[n8n-referensi-node-mati]], [[n8n-json-gaya-byte]], [[store-python-appdata-redirect]],
[[heredoc-makan-backslash]], [[stats-kolom-berspasi]]
