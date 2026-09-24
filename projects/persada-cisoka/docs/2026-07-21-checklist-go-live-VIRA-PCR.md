---
Checklist Go-Live VIRA-PCR — versi ringkas untuk Zoom & pilot testing
Update: 2026-07-21 (re-QA setelah CONFIG diedit) | Sumber: audit ulang folder `workflow/production/` (Main V1.2 + 3 workflow pendukung + PCR_Database.xlsx)
---

# Checklist Go-Live VIRA-PCR — versi ringkas

## 🚨 P0 — WAJIB sebelum go-live

- [ ] **whitelist_enabled = TRUE** (CONFIG) → **ubah ke FALSE**. Kalau lupa, semua customer asli diabaikan diam-diam (bot cuma balas 3 nomor test).
- [ ] **API Claude billing** — credential jalan (`Anthropic account`, id `DPNnlN1bTbbMf8ks`, model Haiku 4.5), tapi kemungkinan masih key pribadi Steven (tab Cost lacak Rupiah). Konfirmasi/pindah ke akun Anthropic milik Persada.
- [ ] **media_team_phone salah format** — sekarang `6282321298930` (nomor tunggal), padahal node baca sebagai JSON array & Aqsa hilang. Ganti ke `["6282321298930","628988585871"]` (Aar+Aqsa). Kalau tidak, notif lead media senyap.
- [ ] **Error Notifier — hardcode & divergen dari CONFIG** — `phone=6285155202354` (nomor test Steven, bukan admin_phone terbaru), Kirimi secret plaintext, param `device_id` duplikat. Putuskan alarm error mau ke siapa, lalu samakan dengan CONFIG (ekspresi, bukan hardcode).
- [ ] **Data test di sheet** — STATS (2 baris: Steven Leroy, S U L I A N T O) & MSG_BUFFER (5 baris) masih data test. Kosongkan sebelum go-live. SURVEY/EVENTS/UNKNOWN sudah bersih ✓.

## 📋 Sheet yang perlu direcheck / masih TBC

| Sheet.Field | Status | Yang perlu dipastikan |
|---|---|---|
| CONFIG.whitelist_enabled | 🔴 TRUE | ubah FALSE (lihat P0) |
| CONFIG.media_team_phone | 🔴 salah format | ubah ke array Aar+Aqsa (lihat P0) |
| CONFIG.admin_phone / admin_phone_display | 🟡 TBC | keduanya = nomor HP Om Sulianto. Hotline resmi ke user pakai ini atau `0822-8181-1212` dari brosur? |
| CONFIG.field_team_phone | 🟡 TBC | Om Sulianto tetap, atau Pak Dadang jadi kandidat alternatif? |
| CONFIG.survey_slots | 🟡 TBC | konfirmasi ulang slot & jam tutup resmi |
| CONFIG.lead_source_map | 🟡 TBC | kalibrasi ulang dengan template iklan asli klien |
| CONFIG.system_prompt | 🟡 verifikasi | sel cuma tulis "di sistem" — pastikan prompt final memang sudah live di node AI Agent |
| PRODUK 36/72 & 36/81 | 🔶 DITAHAN | uang muka, plafon KPR, bunga, cashback 20jt belum diputuskan tim → bot diarahkan lempar ke marketing. OK untuk launch? |
| FAQ row 43 | 🟡 placeholder | jawaban spesifikasi rangka atap/dinding belum ada, isi dari brosur fisik |
| FAQ row 60 | 🟡 typo? | jawaban sebut bank "BSN" — bukan nama bank lazim, cek ulang |
| FAQ row 29 & 31 | 🧹 rapikan | jawaban campur alamat+jam+nomor staf dalam 1 sel |
| LINKS video-36-81 | 🔴 bug | pakai file ID sama dengan video-36-72 — upload video benar & ganti ID |
| KONTAK.Putri | 🟡 TBC | format nomor beda dari sumber chat (089541290429 vs 0895-4129-04291), cek digit |
| KONTAK.Hotline resmi | 🟡 cross-check | `0822-8181-1212` beda format dari nomor lain — dipakai di mana saja? |

## 🔑 API Claude & Kirimi

- [ ] **API Claude**: pindahkan ke akun Anthropic milik Persada (lihat P0). Setelah pindah, cek ulang rate limit & siapa yang pegang key.
- [ ] **Kirimi**: `device_id=D-GHK1A` (beda dari draft lama `D-R91JY`, tanda device baru sudah disetup) tapi `user_code` sama seperti draft lama The Scholars — **konfirmasi ke akun Kirimi**: device ini login di nomor WA PCR yang benar?

## 🧹 Cleanup (tidak blocking, kerjakan kalau sempat)

- [ ] Hapus 2 node mati di Main: `AI Agent boros sonnet 19/7/26` & `FAQ Retrieve belum baca konteks 19/7/26...`
- [ ] `Bootstrap Config` SHEET_ID nyasar (`1dJWq7iq...`) beda dari Document ID asli (`1pzGuRZ...`) — dead value, samakan/hapus, pastikan bukan sheet lama yang masih dipakai.
- [ ] Private key service account Google tersimpan plaintext di CONFIG — pindahkan ke password manager.
- [ ] Sticky notes semua isi default "DONE" — tidak informatif.

## Urutan eksekusi disarankan

1. Kirimi (konfirmasi device/nomor) — fondasi, kalau salah semua WA salah kirim.
2. whitelist_enabled → FALSE + media_team_phone + Error Notifier — supaya notif & broadcast nyampe ke orang benar.
3. API Claude → pindah ke akun Persada.
4. Bersihkan STATS/MSG_BUFFER — tepat sebelum go-live, setelah UAT terakhir.
5. FAQ gaps + keputusan harga komersil — bisa paralel dengan tim marketing.
6. UAT final: chat dari nomor asing → cek balasan AI + semua notif (admin/media/field) masuk ke nomor yang benar.
