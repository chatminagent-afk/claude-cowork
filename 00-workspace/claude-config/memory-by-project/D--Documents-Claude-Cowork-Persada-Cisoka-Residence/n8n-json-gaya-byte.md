---
name: n8n-json-gaya-byte
description: "Saat generate/patch workflow n8n JSON, samakan gaya byte-nya dengan file export asli (LF, tanpa BOM, key order, id/versionId) — kalau tidak, n8n menolak import"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 66585a38-5f2f-43b8-a2ca-fcce27e8a78c
  modified: 2026-08-07T05:11:59.547Z
---

Kalau membuat atau mem-patch file workflow n8n secara terprogram, **jangan cuma pastikan JSON-nya valid** — samakan gaya byte-nya dengan file export n8n yang terbukti bisa di-import:

- **Tulis binary (`open(path,"wb")`), bukan text mode.** Di Windows, `io.open(...,"w")` mengubah setiap `\n` jadi `\r\n`. Export asli n8n pakai **LF murni**. Ini pernah bikin import gagal dengan pesan *"Could not import file — The file does not contain valid JSON data"* padahal Python & PowerShell sama-sama bisa parse file itu.
- **Jangan hapus key `id` dan `versionId`.** Isi dengan nilai BARU (bukan milik workflow sumber) supaya workflow lama tidak tertimpa, tapi key-nya tetap ada.
- **Pertahankan urutan key top-level** seperti aslinya: `name, nodes, pinData, connections, active, settings, versionId, meta, id, tags`.
- Tanpa BOM, `ensure_ascii=False`, `indent=2`.

**Cara verifikasi writer sudah setia:** parse file export asli lalu tulis ulang dengan writer yang sama — hasilnya harus **byte-identik** dengan aslinya. `json.dumps(obj, ensure_ascii=False, indent=2)` terbukti mereproduksi `VIRA-PCR Main V1.3.json` persis.

**Why:** JSON yang valid belum tentu diterima importer n8n; validasi `json.loads` saja memberi rasa aman yang salah dan menghabiskan satu siklus bolak-balik dengan Steven.

**How to apply:** sebelum menyerahkan file workflow, jalankan cek byte: 0 CRLF, tanpa BOM, urutan key sama, dan round-trip file referensi byte-identik. Kalau import tetap gagal, suruh coba import file asli yang belum disentuh dulu (memisahkan masalah file vs masalah n8n/browser); jalur cadangan = copy isi JSON lalu `Ctrl+V` di canvas n8n.

Terkait: [[persada-cisoka-status]], [[pending-changes-register]]
