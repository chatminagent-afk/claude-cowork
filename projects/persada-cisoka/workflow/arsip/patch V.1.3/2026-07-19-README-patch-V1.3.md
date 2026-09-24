# Patch V1.3 — VIRA PCR (2026-07-19)

> ⚠️ **UPDATE 2026-07-20:** 3 file 2026-07-19 di bawah (Main V1.3, Cleanup V1.3, systemprompt draft) **SUPERSEDED — TIDAK DIPAKAI**. Steven memperbaiki #17/#18/#12/#20 sendiri di file terbaru; draft prompt di-skip (hemat 1,8% tidak impactful). Yang AKTIF di folder ini = file **2026-07-20-*** untuk register #4, #2, #1 (lihat `2026-07-20-guide-1-persist-survey-slots.md` + sticky note di masing-masing JSON import).

Hasil QA menyeluruh folder `workflow/production` (Main V1 & V1.2, Error Notifier, Follow-up, MSG_BUFFER Cleanup, PCR_Database.xlsx). Isi folder ini = file siap-import yang memperbaiki defect temuan QA. **Basis = V1.2** (fitur nama+domisili sudah termasuk).

## Isi folder

| File | Isi | Cara pakai |
|------|-----|-----------|
| `2026-07-19-VIRA-PCR-Main-V1.3.json` | V1.2 + **settings dipulihkan** (`errorWorkflow: rBsq-mGgHfqfwbz3YmwxI`, `timezone: Asia/Jakarta`, callerPolicy, timeSavedMode) + **pinData test dihapus** (payload webhook berisi 6285155202354). Node & connections 100% identik dengan V1.2 (terverifikasi diff otomatis). | Import ke n8n menggantikan Main live. Jangan lupa: kolom STATS baru (`nama_lengkap`, `nama_lengkap_ts`, `domisili`, `domisili_ts`) sudah ada di Sheets live sebelum aktifkan. |
| `2026-07-19-VIRA-PCR-MSG-BUFFER-Cleanup-V1.3.json` | Cleanup dengan **Document ID diganti ke sheet PCR live** (`1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o` — sebelumnya menunjuk `1dJWq7iq...`, spreadsheet LAIN yang kebetulan juga bernama "PCR_Database") + **credential diganti** ke `Google Service Account - Persada` (serviceAccount, id QC5aF1HyvTElhC0M) — sebelumnya OAuth "Google Sheets account". | Verifikasi dulu di n8n bahwa dugaan ini benar (1dJWq = copy lama), lalu import menggantikan cleanup lama. Tes manual-run 1x: harus baca MSG_BUFFER sheet live & tidak menghapus baris segar. |
| `2026-07-19-systemprompt-V1.3-draft.md` | Draft system prompt hasil efisiensi — **hanya membuang teks yang bukan instruksi runtime** (marker draft 🔶/🚧, instruksi untuk developer, referensi dokumen analis) + **1 perbaikan faktual**: contoh slot survey "Sabtu 9-13" diselaraskan dengan CONFIG `survey_slots` (setiap hari 09-16). Hemat ±94 token (~1,8%). Perilaku Vira TIDAK berubah. | Review, lalu paste ke field systemMessage node `AI Agent` (baris pertama `=` wajib ikut). File ini = konten murni, aman copy-paste utuh. |

## Yang TIDAK diubah (sengaja)

- Model tetap OpenAI gpt-4.1-mini (checklist go-live §7/§8B — swap ke Claude saat setup production).
- Error Notifier: kredensial Kirimi plaintext di body DIBIARKAN — jalur error harus bebas dependensi (tidak boleh bergantung Parse Config/Sheets yang mungkin justru penyebab crash). Konsekuensi: file JSON-nya mengandung secret, jangan dishare; rotate secret Kirimi kalau file pernah bocor.
- Entri register yang sengaja PENDING (#1, #2, #4) tidak disentuh.
