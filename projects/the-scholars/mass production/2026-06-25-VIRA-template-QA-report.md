# VIRA Template v1 — Laporan QA & UAT

**Tanggal:** 2026-06-25
**Artefak diuji:** `VIRA_TEMPLATE_v1.json`, `VIRA_DATABASE_TEMPLATE.xlsx`
**Basis:** transformasi dari file live `VIRA V3.1 fixing greeting Y & unknown.json`

## Hasil ringkas

**62 dari 62 pengujian LULUS (100%).**

| Kategori | Cek | Lolos |
|---|---|---|
| UAT logika (simulasi code node) | 39 | 39 ✅ |
| Validasi struktur workflow | 14 | 14 ✅ |
| Integrasi Excel ↔ template | 9 | 9 ✅ |

> Catatan cakupan (disepakati): saya tidak bisa menjalankan instance n8n live + API Anthropic/Kirimi Anda dari sini. "100% lolos" di sini = seluruh **logika deterministik** (code nodes), **struktur/importability** JSON, dan **konsistensi Excel↔kode** lolos pada harness simulasi. Smoke test live tetap dijalankan saat onboarding (checklist ada di panduan onboarding).

---

## 1. UAT logika (39 cek) — simulasi node dengan runtime n8n di-mock

- **Parse Config (9):** parsing key/value dari tab CONFIG; tipe string/number/boolean; array JSON; **default aman** saat sel kosong (mis. `debounce_seconds`→60, bukan 0); passthrough body & sheet_id. *(Termasuk perbaikan bug `Number('')→0`.)*
- **Whitelist Gate (4):** disabled→loloskan semua; enabled+cocok nomor→lolos; **enabled+`from` format `@lid` tapi `originLid` cocok→lolos** (menutup bug whitelist-LID dari sistem live); tidak cocok→berhenti.
- **Preprocess (8):** deteksi PARENT/STUDENT dari keyword config; grade→program dari `grade_program_map`; out-of-scope; balasan ambigu (anti-loop); intent daftar; **config kosong tetap jalan tanpa error & tanpa false-positive**.
- **Rate Limiter (1):** batas dari config (uji 3/menit → 3 lolos, sisanya diblok).
- **Cek_user_status (4):** user baru→ajukan status (pertanyaan dari config); user lama→tidak tanya ulang; **HITL `bot_mode=OFF` post-debounce→berhenti**.
- **Process All (4):** deteksi & pembersihan tag `[SEND_GFORM]`, `[UNKNOWN]`, `[TALK_TO_SAM]`.
- **Pick GForm Link (2):** resolve link dari tab LINKS; fallback tanya ulang saat nama link tak cocok.
- **Chat Counter (3):** ekstraksi LID vs nomor telepon; pesan non-teks dibuang.

## 2. Validasi struktur workflow (14 cek)

JSON valid & importable · template `active:false` · `pinData` kosong · tepat 1 trigger webhook · **semua 12 code node lolos `node --check`** · **20 node Google Sheets** config-driven (documentId via ekspresi Bootstrap, sheetName by name agar portabel antar-copy) · **7 node HTTP Kirimi** pakai credential Custom Auth tanpa secret inline · tidak ada node yatim (selain sub-node AI yang memang feed ke Agent) · systemMessage Agent = persona dari config + footer DATA/FAQ engine · 4 node baru hadir (Bootstrap Config, Read CONFIG, Parse Config, Whitelist Gate).

**Cek kebocoran kredensial:** string secret Kirimi (`KM40LI0426`, `4efe37…`, `D-4ZV1F`) dan Sheet ID The Scholars **TIDAK ada** di template. ✅

## 3. Integrasi Excel ↔ template (9 cek)

CONFIG dari `VIRA_DATABASE_TEMPLATE.xlsx` yang sebenarnya → di-feed ke `Parse Config` lalu `Preprocess` yang sebenarnya:
- Semua 9 sel CONFIG bertipe JSON valid (parse tanpa error).
- 8 tab wajib ada dengan nama persis.
- "anak saya kelas 9" → **Intermediate**; "kelas 12" → **Seniors** (mapping dibaca dari Excel, bukan hardcode).
- Deteksi PARENT & out-of-scope dari keyword Excel berfungsi.

---

## Perubahan dari file live → template (ringkas)

| Aspek | Live | Template |
|---|---|---|
| Secret Kirimi | plaintext di 7 node | n8n Custom Auth credential |
| Sheet ID | hardcode di 20 node | 1 node Bootstrap (ekspresi ke semua) |
| sheetName | by gid (pecah saat copy) | by name (portabel) |
| Whitelist | 5 nomor hardcode (mengunci produksi) | toggle config + anti-bug LID |
| Persona | hardcode di systemMessage | dari tab CONFIG |
| Mapping kelas→program | hardcode regex Indonesia | data-driven `grade_program_map` |
| Keyword status/scope/intent | hardcode | dari tab CONFIG (ada default) |
| Greeting question, admin phone, rate limit, debounce | hardcode | dari tab CONFIG |
| Node | 56 | 59 (−1 IF Whitelist, +4 config) |

## Cara menjalankan ulang QA

Harness ada di lingkungan build (`harness.js`, `integ.js`). Bila template diubah, jalankan kembali ketiga set (39+14+9) — semua harus tetap 100% sebelum rilis.

## Sisa risiko (bukan kegagalan QA)

- **Tidak diuji live** terhadap Anthropic/Kirimi/n8n nyata → jalankan checklist UAT live saat onboarding.
- **Sheets sebagai DB** → batas concurrency untuk skala sangat besar (lihat panduan onboarding).
- **Layer Bahasa** pada `Process All` dioptimalkan untuk Indonesia.
- Credential placeholder pada node Sheets/HTTP harus dipilih ulang saat import (langkah onboarding).
