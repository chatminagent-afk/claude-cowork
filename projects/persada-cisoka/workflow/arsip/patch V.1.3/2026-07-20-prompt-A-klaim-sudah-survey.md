# Rute A — Prompt patch: user mengklaim SUDAH survey / booking / diproses tim

Basis: **VIRA-PCR Main V1.2**, node `AI Agent` → `options.systemMessage`.
Perubahan: **prompt saja**, 0 node baru, 0 kolom sheet baru. `flag_survey` / `survey_status` TIDAK disentuh sama sekali.

Kasus pemicu: chat Cost. Herawati — dijapri follow-up "bagaimana dengan surveinya waktu itu?", user jawab *"Udah booking ka, lagi prosess sama pak dadang"*. Lead sudah dipegang manusia dan masuk proses KPR, tapi VIRA tidak punya cara mengenalinya.

---

## Prinsip yang dipegang patch ini

1. **Klaim user ≠ fakta sistem.** `flag_survey=Y` hanya boleh ditulis sistem lewat jalur `IF Schedule Survey` (VIRA benar-benar menjadwalkan). Klaim lisan tidak pernah jadi Y.
2. **Beda derajat, beda aksi.** "Pernah ke lokasi" ≠ "sudah booking, lagi diproses Pak Dadang". Yang pertama masih layak dilayani VIRA; yang kedua harus dilepas ke manusia.
3. **Lever penghenti follow-up adalah `bot_mode`, bukan `flag_survey`.** `Filter Kandidat` di workflow Follow-up skip baris kalau `bot_mode == off`. `[TALK_TO_ADMIN]` sudah men-set itu. Jadi eskalasi = follow-up berhenti, gratis.

---

## Step 1 — Blok `# SURVEY`

Tambah 3 bullet di **paling bawah** blok `# SURVEY`, setelah bullet terakhir
`- Jangan menjanjikan kehadiran orang tertentu; cukup "tim kami".`

```
- USER MENGKLAIM SUDAH SURVEY / SUDAH KE LOKASI ("udah survey kok", "kemarin udah ke sana", "udah lihat unitnya") -> PERCAYA dan akui dengan hangat, JANGAN tanya "kapan?" untuk mengetes, JANGAN ajak survey lagi. Lanjutkan melayani pertanyaannya seperti biasa dan bantu ke langkah berikutnya. Contoh: "Wah sudah pernah ke lokasi yaa Kak, makasih sudah mampir 😊 Ada yang mau ditanyakan lagi soal unit atau proses KPR-nya?"
- USER MENGKLAIM SUDAH BOOKING / SUDAH BAYAR / SEDANG DIPROSES TIM, apalagi menyebut nama orang ("udah booking ka", "lagi proses sama Pak Dadang", "udah DP", "berkasnya udah masuk") -> ini BUKAN lead baru, dia SUDAH dipegang tim kami. JANGAN menjual, JANGAN ajak survey, JANGAN menebak status prosesnya (kamu tidak punya datanya). Akui + pasang [TALK_TO_ADMIN]. Contoh: "[TALK_TO_ADMIN] Alhamdulillah Kak, semoga lancar sampai akad yaa 🙏 Untuk progres prosesnya saya sambungkan ke tim kami yaa biar lebih pasti."
- Kalau klaimnya AMBIGU dan kamu ragu ini survey ke lokasi kami atau ke perumahan lain -> JANGAN eskalasi, JANGAN pasang tag. Tanya ringan sekali saja: "Oh sudah pernah ke Persada Cisoka-nya langsung yaa Kak?" lalu ikuti jawabannya.
```

## Step 2 — Blok `# TAG`, baris `[TALK_TO_ADMIN]`

Ganti baris `[TALK_TO_ADMIN]` yang sekarang berbunyi:

```
[TALK_TO_ADMIN] -> user minta bicara langsung dengan tim marketing manusia, ATAU user mengiyakan tawaranmu untuk dibantu tim (lihat # KALAU RAGU ATAU DIBANTAH). JANGAN dipasang saat kamu baru menawarkan — tunggu user menyatakan mau. Contoh: "[TALK_TO_ADMIN] Baik Kak, akan saya sambungkan ke tim marketing kami yaa, mohon ditunggu." (sistem set mode manual).
```

menjadi (tambahan hanya kalimat ke-2):

```
[TALK_TO_ADMIN] -> user minta bicara langsung dengan tim marketing manusia, ATAU user mengiyakan tawaranmu untuk dibantu tim (lihat # KALAU RAGU ATAU DIBANTAH), ATAU user menyatakan dirinya SUDAH booking/bayar/sedang diproses tim kami (lihat # SURVEY). JANGAN dipasang saat kamu baru menawarkan — tunggu user menyatakan mau. Contoh: "[TALK_TO_ADMIN] Baik Kak, akan saya sambungkan ke tim marketing kami yaa, mohon ditunggu." (sistem set mode manual).
```

---

## Efek yang diharapkan (sudah ada plumbing-nya, tidak perlu node baru)

| Klaim user | Tag | Efek sistem |
|---|---|---|
| "udah pernah ke lokasi" | — | VIRA lanjut melayani, berhenti mengajak survey. Tidak ada tulisan ke sheet. |
| "udah booking / lagi proses sama Pak Dadang" | `[TALK_TO_ADMIN]` | `Notify Talk to Admin` → admin dapat notif; `Update row in sheet` → `bot_mode=off`; `Filter Kandidat` follow-up men-skip baris ini selamanya sampai bot dinyalakan lagi. |
| ambigu | — | 1 pertanyaan klarifikasi, tidak ada aksi sistem. |

`flag_survey`, `survey_status`, tab SURVEY, dan notif Om Sulianto **tidak tersentuh** — antrian kerja tim lapangan tetap bersih dan KPI "survey hasil VIRA" tetap jujur.

## Verifikasi (4 skenario, semua lewat chat testing)

1. **"udah booking ka lagi proses sama pak dadang"** → balasan mengakui + tidak menjual; cek STATS: `bot_mode` jadi `off`, `flag_survey` TETAP kosong/nilai lama; admin menerima notif Talk to Admin.
2. **"aku udah pernah ke lokasi kemarin, harga 36/72 berapa ya?"** → VIRA menjawab harga normal, TIDAK mengajak survey, TIDAK pasang `[TALK_TO_ADMIN]`, `bot_mode` tetap `on`.
3. **Regresi jalur survey normal**: "mau survey senin depan jam 10" → tag `[SCHEDULE_SURVEY]` tetap jalan, baris masuk tab SURVEY, `flag_survey=Y`, Om Sulianto dapat notif. Patch ini tidak boleh mengganggu jalur ini.
4. **Regresi `[TALK_TO_ADMIN]` lama**: "mau ngobrol sama marketingnya dong" → tetap berfungsi seperti sebelumnya.

## Batas patch ini (sadar, disengaja)

- Klaim user **tidak tercatat** di mana pun kecuali sebagai `bot_mode=off` + notif admin. Kalau nanti butuh datanya untuk laporan (berapa lead yang ternyata sudah dipegang telemarketer), itu Rute B: kolom `klaim_status` + tag `[LEAD_STATUS: ...]` di STATS.
- `bot_mode=off` bersifat permanen sampai di-on-kan manual. Untuk kasus "sudah booking" itu memang perilaku yang diinginkan — tapi berarti admin harus punya kebiasaan mengecek baris `off` di STATS.
