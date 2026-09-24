# Patch kalimat `wantsMedia` di node Preprocess - Context Detection — VIRA PCR

**Tanggal:** 2026-07-18
**Kenapa:** planning §Langkah 6 (konsistensi silang). Kalimat lama yang di-inject ke `[CONTEXT]` menekan AI untuk **langsung** pasang `[SEND_MEDIA]` begitu user minta media. Ini bertabrakan dengan aturan klarifikasi baru (ambigu -> tanya balik dulu, jangan tag). Patch **1 baris saja**; bagian lain node Preprocess JANGAN diubah.

**Lokasi:** `workflow/Preprocess___Context_Detection.js` baris 100 (blok perakitan `aiContext`).

---

### CARI (verbatim, 1 baris):

```js
if (wantsMedia) aiContext += `User minta brosur/denah/siteplan. Kalau tersedia di katalog, pasang [SEND_MEDIA: <key>]. `;
```

### GANTI DENGAN:

```js
if (wantsMedia) aiContext += `User minta media (brosur/foto/video/denah). Kalau tipe unit sudah jelas atau cuma 1 yang cocok di katalog, pasang [SEND_MEDIA: <key>] dengan key kanonik. Kalau ambigu (belum sebut tipe & ada >1 pilihan), tanya dulu tipe mana yang dimaksud, JANGAN pasang tag. `;
```

Perubahan menjaga backtick template literal & spasi penutup (` `) seperti baris-baris `aiContext` lain, jadi perakitan `[CONTEXT: ...]` tidak berubah strukturnya.
