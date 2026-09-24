# VIRA Dashboard — Rencana Implementasi Kompatibilitas dengan V4 Production

Dibuat: 2026-07-07 | Untuk: Fable (dev) | Referensi: `report/production/VIRA V4.json`, `report/production/The_Scholars_Database.xlsx`, `VIRA-DASHBOARD/2026-06-29-*`

## Konteks

Dashboard VIRA (Apps Script + PWA) dibuat 29 Juni 2026 di atas versi workflow n8n yang saat itu live. Sejak itu workflow production sudah naik ke V4 (59 node, per 7 Juli). Analisa perbandingan menunjukkan fitur toggle per-user & analitik sudah kompatibel langsung, tapi ada 5 item yang perlu dikerjakan sebelum dashboard dianggap siap pakai penuh di V4. Urutan di bawah berdasarkan prioritas (P0 = blocking, P1 = perlu untuk fungsi penuh, P2 = kualitas data/nice-to-have).

---

## Ringkasan Prioritas

| # | Item | Prioritas | Status sekarang |
|---|------|-----------|------------------|
| 1 | Pasang toggle global `VIRA_STATUS` ke workflow V4 production | P0 | Belum terpasang |
| 2 | Fix race condition `bot_mode` OFF→ON ter-overwrite | P1 | Belum difix |
| 3 | Konfirmasi status fix `gform_sent_ts` pass-through | P0 (verifikasi) | Perlu konfirmasi Sam |
| 4 | Implementasi penulisan `gform_filled` | P1 | Belum ada node yang menulis |
| 5 | Mitigasi rasio LID 66% di kolom No WA | P2 | Belum ditangani |

---

## 1. Pasang Toggle Global VIRA_STATUS (P0)

**Masalah:** Sheet `CONFIG` di production saat ini cuma berisi 5 key biaya (NOMINAL_BIAYA, NAMA_BANK, dst) — tidak ada baris `VIRA_STATUS`. Node `Read VIRA Config` dan `IF VIRA Active` tidak ada di 59 node V4 production sekarang. Tombol toggle global di dashboard (`setGlobalStatus_` di Code.gs) akan menulis ke CONFIG, tapi workflow tidak membacanya sama sekali — toggle global saat ini tidak berefek ke bot.

**JANGAN** import `2026-06-29-VIRA-with-global-toggle.json` langsung — file itu masih versi 58 node (sebelum penambahan `If From Group`, `Resolve User Row`, `Append MSG_BUFFER`, `Read MSG_BUFFER`, `Notify User Error`). Import akan memundurkan production ke versi lama.

**Langkah implementasi:**
1. Buka `report/production/VIRA V4.json` di editor n8n (workflow production yang sekarang, bukan file dashboard).
2. Ambil 2 node dari `VIRA-DASHBOARD/2026-06-29-VIRA-toggle-nodes-snippet.json`: `Read VIRA Config` (googleSheets, baca sheet CONFIG filter Key=VIRA_STATUS) dan `IF VIRA Active` (cek Value === "ON").
3. Copy-paste kedua node ke canvas V4 production.
4. Putus koneksi existing `IF (Whitelist) → Chat Counter`, sambungkan ulang:
   `IF (Whitelist) [true] → Read VIRA Config → IF VIRA Active [true] → Chat Counter`
   `IF VIRA Active [false] → (biarkan kosong, flow berhenti = bot silent)`
5. Di node `Read VIRA Config`, buka dropdown Sheet → pilih ulang **CONFIG** supaya gid ter-bind ke spreadsheet yang benar, dan pastikan credential = *Google Service Account thescholars*.
6. Di sheet CONFIG, tambah baris manual: `VIRA_STATUS | ON` (fail-safe: Apps Script juga auto-create baris ini kalau belum ada, tapi lebih aman ditambah manual dulu).
7. Save & Activate workflow.

**Verifikasi:** toggle dashboard ke OFF → kirim pesan test dari nomor test → pastikan tidak ada balasan & flow berhenti di `IF VIRA Active`. Toggle kembali ON → pesan test dibalas normal.

**Catatan biaya:** +1 read Sheets/pesan saat ON; saat OFF net lebih hemat karena flow berhenti lebih awal (sudah dianalisa di DEPLOY-README, tidak berubah).

---

## 2. Fix Race Condition `bot_mode` Ter-overwrite (P1)

**Masalah:** Node `Update to STATS` menulis `bot_mode = isTalkToSam ? 'OFF' : 'ON'` di akhir SETIAP turn yang lolos gate `IF Bot Mode Active`. Kalau Sam toggle OFF via dashboard tepat saat pesan user tersebut sedang mid-flight (sudah lewat gate di awal turn), turn itu akan tetap selesai dan menimpa balik `bot_mode` jadi ON — toggle Sam seolah tidak ngefek.

**Rekomendasi fix (pilih salah satu, didiskusikan dengan Fable):**
- **Opsi A (minimal):** sebelum `Update to STATS`, tambah 1 node re-read cepat nilai `bot_mode` terkini dari STATS untuk baris user tsb. Formula `bot_mode` di `Update to STATS` diubah jadi: kalau nilai terkini sudah `OFF` (dan bukan karena `isTalkToSam` turn ini), pertahankan `OFF`; kalau `isTalkToSam` true → set `OFF`; selain itu → `ON`.
- **Opsi B (terima risiko):** dokumentasikan sebagai known limitation — window race-nya kecil (hanya kalau toggle terjadi persis saat 1 pesan sedang diproses AI, biasanya beberapa detik). Sam tinggal toggle ulang kalau ketahuan ke-overwrite.

**Rekomendasi saya:** Opsi A kalau frekuensi HITL manual Sam cukup sering; Opsi B kalau jarang terjadi. Minta Fable estimasi effort Opsi A sebelum diputuskan.

---

## 3. Konfirmasi Status Fix `gform_sent_ts` Pass-through (P0 — verifikasi saja)

**Konteks:** Audit 6 Juli menandai bug kritikal — `gform_sent_ts` tertulis di TIAP pesan semua user karena rantai GForm yang disabled tetap pass-through, padahal entry gate-nya (`IF Send GForm`) di-disable juga saat itu. Di file production sekarang, gate `IF Send GForm` (`isSendGForm === true`) enabled dan tervalidasi benar secara kode, dan data aktual di sheet cuma 125 dari 239 user riil yang punya `gform_sent_ts` terisi (bukan 100%) — indikasi sudah difix.

**Yang perlu dikerjakan:** bukan coding, tapi konfirmasi ke Sam/tim: apakah memang ada fix eksplisit yang di-deploy antara 6-7 Juli untuk item ini? Kalau belum ada yang sengaja mem-fix, perlu digali kenapa datanya sudah tidak menunjukkan pola "every message" — supaya tidak salah asumsi sebelum dashboard mulai dipakai untuk metrik follow-up GForm.

---

## 4. Implementasi Penulisan `gform_filled` (P1)

**Masalah:** Kolom `gform_filled` di STATS 100% kosong (1159/1159 baris) — bukan bug baru, memang belum ada node manapun di V4 yang menulis kolom ini. Kartu "Konversi GForm" di dashboard akan selalu tampil 0%.

**Langkah implementasi (perlu didiskusikan dulu sumber datanya):**
1. Tentukan sumber sinyal "GForm sudah diisi" — apakah dari Google Form response sheet terpisah (via trigger/polling), atau webhook dari Google Forms.
2. Tambah node baru (trigger terjadwal atau webhook Form submit) yang mencocokkan submission ke baris STATS via No WA, lalu update `gform_filled = TRUE`.
3. Kalau sumber data form response belum ada/diakses, ini jadi item terpisah di luar scope dashboard — beri tahu Steven supaya expektasi metrik konversi disesuaikan dulu.

---

## 5. Mitigasi Rasio LID 66% (P2)

**Masalah:** Dari 239 baris user riil di STATS, 158 (~66%) punya `No WA` berformat LID/grup (15-22 digit), bukan nomor HP yang bisa dihubungi manual. Saat QA 29 Juni baru 7 dari 143 baris (~5%). Fitur cari/toggle per-user di dashboard tetap jalan untuk baris ini, tapi Sam tidak bisa menghubungi user tsb secara manual di luar bot.

**Opsi mitigasi:**
- Tambah badge/label visual di dashboard untuk baris dengan `No WA` panjang (≥15 digit) → tandai "LID, tidak bisa dihubungi manual".
- Investigasi di level n8n (`Resolve User Row` / `Chat Counter`) kenapa proporsi LID naik drastis — apakah ada perubahan di WhatsApp Business API/Kirimi yang membuat lebih banyak percakapan datang sebagai LID daripada nomor.

Ini tidak menghalangi dashboard dipakai, tapi sebaiknya Sam diberi tahu supaya tidak bingung kenapa banyak "user" yang tidak bisa ditelepon langsung.

---

## Urutan Eksekusi yang Disarankan

1. Item 3 (konfirmasi, tidak perlu coding) — bisa jalan paralel, tidak blocking.
2. Item 1 (toggle global) — prasyarat sebelum dashboard diklaim "full-featured".
3. Item 2 (race condition bot_mode) — penting sebelum toggle per-user dipakai intensif untuk HITL.
4. Item 4 (gform_filled) — tergantung ketersediaan sumber data form response.
5. Item 5 (LID) — bisa dikerjakan kapan saja, tidak blocking.

## Kriteria Selesai (Acceptance)

- Toggle global ON/OFF dari dashboard benar-benar menghentikan/menjalankan balasan bot (test end-to-end).
- Toggle per-user OFF bertahan minimal 1 turn penuh meski user tsb baru saja chat (test race condition).
- Konfirmasi tertulis dari Sam soal status fix `gform_sent_ts`.
- Kartu "Konversi GForm" menunjukkan angka non-nol setelah `gform_filled` diimplementasi (atau expektasi didokumentasikan kalau ditunda).
- Dashboard menandai baris LID secara visual (kalau opsi mitigasi dipilih).

## Rollback

Semua perubahan di atas dilakukan di workflow n8n `report/production/VIRA V4.json` — sebelum edit, export/duplicate workflow dulu sebagai backup bertanggal (mis. `VIRA V4 - backup sebelum patch dashboard.json`). Kalau toggle global menyebabkan masalah, cukup putuskan kembali koneksi `IF (Whitelist) → Chat Counter` langsung (skip 2 node baru) dan set `CONFIG.VIRA_STATUS = ON`.
