# Deploy v3.14 — "Brp" dijawab harga, bukan dianggap nama (2026-09-25)

**Kasus:** prospek iklan IG (Reza, 6285199701359) membalas sapaan VIRA dengan `Brp`. VIRA mengirim "Salam kenal kak." saja, lalu `Brp` tersimpan sebagai nama di STATS.

**Berubah:**
- `brp` / `berapa` / `brapa` yang dikirim sendirian (boleh ditambah "kak", "ya", "?") dibaca sebagai **tanya harga**. Model diberi catatan tegas: dia menanyakan harga VIRA, bukan menjawab pertanyaan nama.
- Kata tanya (brp, berapa, knp, gmn, apa, kapan, mana, …) **tidak pernah disimpan sebagai nama**, baik yang ditangkap kode maupun yang ditulis model lewat `[FACTS nama="..."]`.
- Kalau prospek bertanya dan balasan VIRA cuma basa-basi ("Salam kenal kak."), pertanyaan VIRA tidak dibuang lagi. Balasan tidak pernah buntu.
- Prompt: aturan "satu kata = jawaban pertanyaanku" dikecualikan untuk kata tanya.
- Tidak ada kolom sheet atau node baru. 87 dari 91 node identik dengan v3.13.

**Sudah lolos:** UAT **943/0**. Di dalamnya ada replay persis insiden Reza: kode v3.13 menghasilkan "Salam kenal kak." + nama "Brp" seperti di live, sedangkan v3.14 tidak. Juga lolos eval model DeepSeek asli (`workflow/2026-09-25-hasil-eval-brp-v3.14.md`). Di eval itu, giliran 1 dipaksa sama persis dengan sapaan yang diterima Reza, lalu giliran 2 dijawab model.

| Balasan atas "Brp" | v3.13 (live) ×10 | v3.14 ×10 | v3.14 "brp kak?" / "Berapa?" ×6 |
|---|---|---|---|
| Menjawab kisaran harga | 0/10 | **10/10** | **6/6** |
| "Salam kenal kak" | 9/10 | **0/10** | 0/6 |
| "Brp" tersimpan sebagai nama | 10/10 | **0/10** | 0/6 |
| Balasan buntu (tanpa jawaban & tanpa pertanyaan) | 8/10 | **0/10** | 0/6 |
| Model menulis `[FACTS nama="Brp"]` | 2/10 | 0/10 | 0/6 |
| Catatan konteks bocor ke prospek | 0/10 | 0/10 | 0/6 |
| Median kata | 3 | 27 | 28 |

**Regresi** (`workflow/2026-09-25-hasil-eval-regresi-v3.14.md`):
- 7 skenario lama (Abdul, Nadia, klinik, bimbel, Kopi Senja, Rehan, Dimas) dijalankan dengan model asli di v3.14 ×3, lalu dibandingkan dengan v3.13 ×3.
- Nama usaha benar 18/18, S6 Rehan benar 3/3, dan "kpn bs ngmng sm steven?" membuat bot OFF 3/3, semuanya sama dengan v3.13.
- Median kata tetap 12.
- Rekaman model diputar silang (v3.13 lewat kode v3.14 dan sebaliknya): **0 balasan berbeda**.
- Muncul satu kejadian harga disebut tanpa diminta. Sudah diuji A/B dengan riwayat yang sama: prompt v3.13 0/6, prompt v3.14 0/6. Artinya variasi model, bukan efek v3.14.

## Langkah

1. Buka workflow live **VIRA Personal — Main** (ID `AC65HeFegHFCFc5aY609u`). Ganti isinya dengan `workflow/2026-09-25-VIRA-Personal-Main-v3.14.json`, caranya sama seperti v3.13, supaya ID dan settings tetap.
2. Save, lalu pastikan tidak ada node ganda berakhiran angka (mis. `Process All1`). Jumlah node harus 91.
3. Cek node yang memakai credential (Google Sheets, DeepSeek). Kalau ada yang merah, pilih lagi credential yang sama.
4. Pastikan workflow tetap **Active**.
5. STATS baris **6285199701359** (Reza): kosongkan `nama_lengkap` yang berisi `Brp`.

## Uji (±5 menit, nomor uji)

1. Hapus baris STATS nomor uji. Kirim `Halo VIRA, aku lihat iklannya di IG, mau ngobrol soal AI customer service.`
2. Sesudah sapaan yang menanyakan nama + nama usaha, kirim `Brp`. VIRA menyebut kisaran Basic/Premium dan bilang angka finalnya lewat Steven. **Tidak** membalas "Salam kenal kak". Di STATS, `nama_lengkap` tetap kosong.
3. Kirim `Reza`. Di STATS, `nama_lengkap` = Reza.
4. Regresi: `harganya berapa kak?` tetap dijawab kisaran lengkap.

## Kalau bermasalah

Ganti lagi isi workflow dengan `2026-09-23-VIRA-Personal-Main-v3.13.json`. Tidak ada data yang perlu dikembalikan.

## Sesudah uji

Hapus workflow **VIRA Eval — Balasan (sementara, hapus sesudah uji)**.
