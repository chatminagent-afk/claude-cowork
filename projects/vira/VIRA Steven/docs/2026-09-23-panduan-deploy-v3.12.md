# Deploy v3.12 — balasan to the point (2026-09-23)

**Berubah:** balasan VIRA biasanya cukup satu pertanyaan. Dia tidak lagi merangkum ucapan prospek, tidak promosi VIRA kalau tidak ditanya, dan tidak menanyakan lagi yang sudah disebut. Tidak ada kolom sheet baru.

**Sudah lolos:** UAT **732/0** · eval model DeepSeek asli, 15 percakapan dibandingkan dengan v3.11 live:

| | v3.11 | v3.12 |
|---|---|---|
| Median kata per balasan | 26 | **13** |
| Membuka dengan merangkum | 7 | **0** |
| Promosi VIRA tanpa ditanya | 5 | **0** |
| Perkenalan (median kata) | 54 | **37** |
| Nama usaha tercatat benar | 4/4 | **12/12** |

## Langkah

1. n8n → **Import from File** → `workflow/2026-09-23-VIRA-Personal-Main-v3.12.json`.
2. Cek node yang pakai credential (Google Sheets, DeepSeek). Kalau ada yang merah, pilih lagi credential yang sama.
3. **Nonaktifkan "VIRA Personal — Main" yang lama**, baru **aktifkan v3.12**. Jangan dua-duanya aktif karena path webhook-nya sama.
4. Settings v3.12 → pastikan **Available in MCP** menyala, supaya aku bisa cek live.

## Uji (±5 menit, nomor uji)

1. Hapus baris STATS nomor uji → kirim `Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku.` → perkenalan ±3 kalimat, satu pertanyaan (nama + nama usaha).
2. Balas 4 baris: `abdul` / `aku owner humanizer` / `jualan parfum` / `kdg ribet balesin org ty 1 1` → VIRA **tidak** menanyakan nama usaha lagi. STATS: nama_lengkap, nama_bisnis, industri, masalah_utama terisi.
3. Lanjut 2–3 giliran → tiap balasan 1–2 kalimat pendek.
4. Tanya `harganya berapa?` → jawabannya tetap lengkap.
5. Kalau ada balasan yang dipangkas pengaman, tab **EVENTS** mendapat baris `RINGKAS` (teks asli model + teks yang terkirim).

## Kalau bermasalah

Nonaktifkan v3.12 → aktifkan lagi Main lama (v3.11). Tidak ada data yang perlu dikembalikan.

## Sesudah uji

Hapus workflow **VIRA Eval — Balasan (sementara, hapus sesudah uji)**.
