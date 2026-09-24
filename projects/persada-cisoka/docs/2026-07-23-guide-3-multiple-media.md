# Guide #3 — Multiple Media (foto + video dalam satu balasan)

**Dibuat**: 2026-07-23
**Temuan**: `test chat vira.txt` #3 — user minta "video dan foto", Vira hanya kirim foto.
**Akar masalah**: regex penangkap tag di `Process All` tanpa flag `/g` → hanya tag PERTAMA yang diproses; tag ke-2 dibersihkan dari teks tapi medianya tidak pernah terkirim.
**Keputusan desain (07-23)**: "hanya yang diminta" (foto+video → dua-duanya; salah satu → satu saja) + **2 pesan WA terpisah**, urutan foto → video. Pricelist dikecualikan (tidak auto-bundle).

**Pendekatan**: ADDITIVE — jalur media-1 existing (exact/fallback/ambigu/manual/location) **tidak disentuh**. Ditambahkan pass ke-2 untuk tag kedua (key kanonik, exact-match) + 1 branch node ke-2 setelah `Send Media Kirimi`.

**Prompt**: TIDAK perlu diubah. System prompt sudah memerintahkan Vira memasang DUA tag terpisah kalau menjanjikan foto DAN video ("Kalau kamu menjanjikan foto DAN video, pasang DUA tag terpisah"). Kode-lah yang tadinya membuang tag ke-2.

---

## BAGIAN 1 — Edit kode node `Process All` (3 edit)

Buka node **Process All** → field **JavaScript**. Lakukan 3 find-replace berikut.

### Edit 1 — tangkap SEMUA tag (bukan cuma pertama)

**CARI** (sekitar baris 84–87):
```js
let isSendMedia = false, mediaKey = '';
const mediaMatch = aiOutput.match(/\[\s*SEND_MEDIA\s*(?::\s*([^\]]*))?\]/i);
if (mediaMatch) { isSendMedia = true; mediaKey = (mediaMatch[1] || 'brosur').trim().toLowerCase(); }
```

**GANTI JADI**:
```js
let isSendMedia = false, mediaKey = '';
// #3 multi-media: tangkap SEMUA tag SEND_MEDIA (bukan cuma pertama). matchAll + flag /g.
const mediaKeysAll = [...new Set(
  [...aiOutput.matchAll(/\[\s*SEND_MEDIA\s*(?::\s*([^\]]*))?\]/gi)]
    .map(m => (m[1] || 'brosur').trim().toLowerCase())
    .filter(Boolean)
)];
if (mediaKeysAll.length) { isSendMedia = true; mediaKey = mediaKeysAll[0]; }
```
> `mediaKey` tetap = tag pertama, jadi seluruh blok resolusi media-1 di bawahnya berjalan sama persis seperti sekarang. `mediaKeysAll` menyimpan semua key untuk dipakai media-2.

### Edit 2 — tambah resolusi MEDIA KE-2

**CARI** baris komentar ini (tepat setelah blok `if (isSendMedia) { ... }` resolusi media, sekitar baris 417):
```js
// ── NOTIF ADMIN: hanya untuk survey reject kategori AI-FAULT ──
```

**SISIPKAN blok berikut TEPAT DI ATAS baris komentar itu**:
```js
// ── #3: MEDIA KE-2 (foto + video dalam satu balasan) ──
// Kirim media kedua HANYA jika media-1 sukses (bukan ambigu/manual/location) DAN ada tag
// kedua dengan KEY KANONIK yang exact-match di LINKS. Kalau tidak memenuhi -> dilewati
// diam-diam (tidak tanya balik, tidak notif). Jalur media-1 di atas tidak diubah.
let isSendMedia2 = false, mediaUrl2 = '', mediaCaption2 = '';
if (isSendMedia && mediaUrl && !isMediaAmbiguous && mediaKeysAll.length >= 2) {
  let linkRows2 = [];
  try { linkRows2 = $('Read LINKS Data').all().map(i => i.json); } catch (e) {}
  const norm2 = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const active2 = linkRows2.filter(r => /^\s*(aktif|active|on|ya)\s*$/i.test(String(r['Status'] || '')));
  const key2 = mediaKeysAll.find(k => k && k !== mediaKey) || '';
  const row2 = key2 ? active2.find(r => norm2(r['Nama Link']) === key2) : null;
  if (row2) {
    const tipe2 = norm2(row2['Tipe']);
    const url2 = String(row2['URL'] || '').trim();
    if (url2 && url2 !== mediaUrl && tipe2 !== 'location' && tipe2 !== 'website') {
      isSendMedia2 = true;
      mediaUrl2 = url2;
      mediaCaption2 = String(row2['Caption'] || row2['Deskripsi'] || '').trim() || 'Ini file berikutnya yaa.';
      // urutan foto -> video: kalau media-1 video & media-2 image, tukar posisi.
      const row1 = active2.find(r => norm2(r['Nama Link']) === mediaKey);
      const tipe1 = row1 ? norm2(row1['Tipe']) : '';
      if (tipe1 === 'video' && tipe2 === 'image') {
        const tU = mediaUrl, tC = mediaCaption;
        mediaUrl = mediaUrl2; mediaCaption = mediaCaption2;
        mediaUrl2 = tU; mediaCaption2 = tC;
      }
    }
  }
}
```

### Edit 3 — ekspor field baru ke output

**CARI** (di dalam `return [{ json: { ... } }]`, sekitar baris 444):
```js
    isSendMedia, mediaUrl, mediaCaption, mediaKey,
```

**GANTI JADI**:
```js
    isSendMedia, mediaUrl, mediaCaption, mediaKey,
    isSendMedia2, mediaUrl2, mediaCaption2,
```

---

## BAGIAN 2 — Tambah branch node ke-2 + wiring

### 2a. Import 4 node baru
File: **`2026-07-23-import-nodes-3-media2.json`** (folder root project).
- Di n8n: buka workflow **VIRA-PCR Main V1.2** → **Import from File** (atau buka file, copy isinya, lalu Ctrl+V di canvas).
- Muncul 4 node: `IF Send Media 2` → `Wait Media 2` → `Download Media 2` → `Send Media Kirimi 2` (sudah tersambung internal).

### 2b. Wiring WAJIB (1 koneksi)
Sambungkan output **sukses** `Send Media Kirimi` (media-1) ke branch baru:

> **`Send Media Kirimi`** — output **main #0 (atas / sukses)** → input **`IF Send Media 2`**

*(Saat ini output sukses `Send Media Kirimi` belum tersambung ke mana-mana, jadi aman.)*

### 2c. Wiring error (opsional tapi disarankan)
Kalau saat import koneksi ke `Notify Admin Media Error` tidak ikut terbawa, sambungkan manual:
- `Download Media 2` output **#1 (error, bawah)** → `Notify Admin Media Error`
- `Send Media Kirimi 2` output **#1 (error, bawah)** → `Notify Admin Media Error`

### Skema akhir
```
... Reply Chat Kirimi (teks) → Check API Response → IF Send Media
      → Wait Media → Download Media → Send Media Kirimi (foto)
            └─(sukses #0)→ IF Send Media 2
                  → Wait Media 2 → Download Media 2 → Send Media Kirimi 2 (video)
```

---

## BAGIAN 3 — Test setelah apply

| Skenario user | Harapan |
|---------------|---------|
| "minta foto dan video 36/81" | 2 file masuk: **foto dulu, lalu video** (2 pesan) |
| "minta foto 36/81" saja | 1 file (foto) |
| "minta video 36/81" saja | 1 file (video) |
| "minta foto" (tanpa tipe) | Vira tanya balik tipe mana (jalur ambigu existing, tidak berubah) |
| minta brosur | 1 file brosur (tidak berubah) |

---

## Batasan (by design)
- Media ke-2 hanya jalan kalau Vira memasang **tag kedua dengan key kanonik** (mis. `video-36-81`) yang **exact-match** di kolom `Nama Link` sheet LINKS. Ini sesuai instruksi prompt (Vira memakai key kanonik). Kalau tag ke-2 tidak kanonik / tidak ketemu → hanya media-1 yang terkirim (tidak ada regresi, tidak error).
- Maksimal 2 media per balasan (foto + video). Cukup untuk kebutuhan unit PCR. Kalau nanti perlu >2, branch bisa diperpanjang dengan pola yang sama.
- Kalau saat test Vira ternyata **tidak** memasang tag ke-2 (lupa), itu isu reliabilitas prompt, bukan kode ini — kabari aku, cukup nudge kecil di prompt (tanpa hardcode fakta).
