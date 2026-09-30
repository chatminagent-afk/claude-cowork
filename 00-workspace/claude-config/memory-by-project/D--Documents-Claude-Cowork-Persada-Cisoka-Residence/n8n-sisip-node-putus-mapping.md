---
name: n8n-sisip-node-putus-mapping
description: Menyisipkan node di depan node Google Sheets n8n memutus mapping kolom yang memakai $json.* — kolomnya tertimpa kosong tanpa error
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0e1c69b0-ba5f-4639-8bd0-ebdaf3c774d1
  modified: 2026-08-27T09:36:52.932Z
---

Node Google Sheets di n8n memetakan kolom dengan dua gaya yang terlihat mirip tapi berperilaku
sangat berbeda saat rantai node diubah:

- `={{ $('Nama Node').first().json.x }}` — **tahan** disisipi node baru di depannya.
- `={{ $json.x }}` — **membaca item yang persis masuk ke node itu**. Begitu ada node baru
  disisipkan di depannya, `$json` berganti jadi output node baru itu.

Kalau field-nya tidak ada di item baru, ekspresi jadi kosong dan Sheets **menimpa kolom itu
dengan string kosong**. Tidak ada error, node hijau, run sukses.

**Kejadian nyata (2026-08-27, VIRA PCR):** `Update to STATS` memetakan `"lid": "={{ $json.lid }}"`
sementara ~21 mapping lain memakai `$('...')`. Rencananya menyisipkan `Build Konteks Input` →
`Update Konteks` (chainLlm) → `Update to STATS`. Output chainLlm bentuknya `{text: ...}`, jadi
kalau disambung langsung, kolom `lid` seluruh lead tertimpa kosong — dan `lid` adalah kunci
identitas cadangan (No WA primer, lid backup). Solusinya node `Merge Konteks` yang mengembalikan
item asli (`...base`) plus field baru, jadi bentuk item yang masuk ke Sheets tidak berubah.

**Why:** kerusakannya senyap dan mengenai data identitas, bukan cuma data tampilan. Audit
"referensi node mati" ([[n8n-referensi-node-mati]]) tidak menangkapnya sama sekali — `$json.lid`
bukan referensi ke node mana pun, jadi lolos semua pengecekan `$('...')`.

**How to apply:**
1. Sebelum menyisipkan node apa pun ke tengah rantai, grep dulu node-node **di hilirnya** untuk
   `$json.` — daftar field itulah kontrak yang wajib dipertahankan.
2. Kalau node sisipan mengubah bentuk item (chainLlm, HTTP Request, Sheets), tutup dengan Code
   node yang menyebar item asli: `return [{ json: { ...base, field_baru } }]`.
3. Verifikasi otomatis: kumpulkan `$json.(\w+)` dari mapping node hilir, lalu pastikan tiap nama
   benar-benar diproduksi oleh salah satu node di rantai baru. Murah, dan menangkap kelas bug ini
   sebelum menyentuh sheet.
4. Node Sheets `appendOrUpdate`/`update` paling berbahaya — kolom yang tidak sengaja kosong bukan
   sekadar hilang di output, tapi **menghapus nilai lama di sheet**.

Terkait: [[n8n-referensi-node-mati]], [[n8n-json-gaya-byte]], [[persada-cisoka-status]],
[[pending-changes-register]]
