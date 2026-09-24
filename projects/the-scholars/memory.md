# memory.md — the scholars (VIRA chatbot)

## What it is
WhatsApp AI assistant for **TheScholars.id**, an education consultancy (Singapore
scholarship programs). Client contact: **Sam** — bot speaks as **"Sam versi AI"**.
Stack: n8n workflow + Google Sheets (STATS + FAQ/PROGRAM/ABOUT/LINKS tabs) + Kirimi WA
gateway + AI Agent node with Simple Memory.

This is the **original/production** VIRA instance — the logic other instances
(Persada Cisoka, VIRA Steven) were forked from.

## Workflow — how work moves here
1. Bug/change identified (often from a real chat transcript or client report).
2. Root-cause analysis doc written first — `report/patch/YYYY-MM-DD-VIRA-V*-changelog.md`
   + matching `-handoff.md`, paired with the actual patched `.json` workflow export.
   Version numbers bump per patch (V3 → V3.1 → V3.2 … currently at **V6**, see
   `report/patch/2026-08-19-VIRA-V6-media-skill-panduan.md`).
3. Once a patch is stable, the workflow JSON becomes the new baseline referenced by
   the next patch (patches are cumulative, not squashed).
4. `report/production/` holds full production exports + extracted reference dumps
   (node lists, connections, credentials map) used when auditing the live workflow.
5. QA/report docs for specific real incidents live in
   `report/report problem production/report <tanggal>/`.
6. Bigger initiatives (mock booking flow, invoicing) get their own top-level folder
   (`mock booking/`, `archive/invoice/`) once mature.
7. This instance's proven patterns get promoted into `mass production/VIRA_TEMPLATE_v1.json`
   — the config-layer template other client instances (Persada Cisoka) are built from.

## Current status
Live in production, public mode (whitelist disabled). **Last confirmed-working patch:
r6 — link-guard + WA-channel filter (2026-08-14).** V6 media-skill + STATS cleanup
(2026-08-19) exists as a patch but its media handling **hasn't been tried/validated
yet — on hold.** Don't assume V6 is live until Steven confirms it's been tested.

The July 2026-07-02 execution plan (Paket 1–6) and its companion bug report are done —
fully executed via the V3.x–r6 patch series since. Archived to `archive/`
(2026-08-21) rather than kept at root.

**Analytics topik bulanan (2026-08-26)** — WF-A harvester + WF-B monthly rollup +
blok dashboard, semua **dibangun & lulus QA otomatis tapi BELUM di-import ke n8n**.
Tidak menyentuh workflow utama sama sekali. Baca `2026-08-26-MULAI-DI-SINI.md` dulu.
Laporan penuh pertama = data September, tampil 1 Oktober.

**STATS Cleanup v3 (2026-08-27)** — `2026-08-27-VIRA-STATS-cleanup-3bulan-v3.json`
+ panduan, QA 72/72 PASS. **Sudah di-import & dieksekusi manual di n8n; belum diaktifkan.**
Output `Plan cleanup` cocok persis (10/10 metrik, selisih 0) dengan port Python di QA
terhadap export sheet live 27 Ags — jadi logikanya tervalidasi di data nyata, bukan cuma
sintetis. Sisa satu: nomor WA di node `Notify Steven` masih `ISI_NOMOR_WA_STEVEN`.
Run pertama yang benar-benar menghapus = **1 Okt 2026, ±76 baris**. Menggantikan v1
(2026-08-19) dan v2 (sama-sama belum pernah aktif). Aturan: simpan header; simpan `bot_mode == "OFF"` yang
`off_reason`-nya bukan `"VIRA"` (**permanen, tanpa kedaluwarsa**); simpan yang aktivitas
terakhirnya < 90 hari; simpan yang tanpa jejak waktu. Sisanya dihapus.

Dua hal yang gampang salah kalau di-derive ulang:
- **Patokan umur tidak boleh `last_reply_ts` saja.** Kolom itu hanya ditulis
  `Update to STATS` di cabang `IF Bot Mode Active = ON`, jadi kontak OFF tidak pernah
  memperbaruinya (cuma 41% baris OFF punya nilai). Yang mengisi jalur OFF adalah
  `buffer_done_ts` lewat `Delete_Pending_Msg_Bot_Off`. Umur = max dari `last_reply_ts`,
  `buffer_done_ts`, `timestamp`, `gform_sent_ts`, `kelas_anak_ts`, fallback parse
  `Tanggal Chat Terakhir`/`Pertama` (DD/MM/YYYY). Unit campur — `timestamp` berisi detik
  DAN milidetik antar-baris — jadi normalisasi per nilai, bukan per kolom.
- **Jangan tiru `KEEP_WHEN_EMPTY = false` dari Persada Purge.** Di data nyata 103 baris
  tanpa jejak waktu, 100%-nya `bot_mode = OFF`.

Strategi hapus ganti dari salin-lalu-hapus jadi **hapus per blok kontigu, urut menurun**
(ala Persada) — karena dengan filter umur mayoritas baris justru dipertahankan.

Kolom `off_reason` sudah live sebagai **kolom C** (bukan X seperti rencana panduan 19 Ags),
dan node `Update row in sheet` di r9 memang menulis `"off_reason": "VIRA"` — terkonfirmasi,
tidak perlu dicek ulang. `Plan cleanup` membaca kolom by nama header, bukan posisi.
Baris OFF tumbuh tanpa batas (55% sheet sudah OFF: 392 dari 721); filter umur memperlambat,
tidak membatasi.

## Key decisions (durable — don't re-derive)
- **User identity:** No WA primary, `lid` backup only when No WA is empty. Never fall
  back to `rows[0]`. (This is the project-wide VIRA identity principle — applies to all
  instances.)
- **Debounce:** `Wait3` = 60s intentional (a code comment saying 8s is a stale typo).
- **Register netral:** no vocatives (Pak/Bu/Kak), no parent/student-status flow — removed
  per client request.
- **Simple Memory resets on every workflow save/deploy** — persistent state lives in
  Sheets columns (`kelas_anak`, `program_interest`) as mitigation, not in AI memory.
- Kirimi's actual recipient field is `phone` (not `receiver` as public docs claim) —
  same fact holds for every VIRA instance.

## Open items
- Test/validate V6's media handling before treating it as live — it's untested, r6 is
  the real current baseline.
- Sheets API 429 mitigation — only pursue if reproduced, don't over-engineer speculatively.

## File map
- `2026-08-26-MULAI-DI-SINI.md` — **titik masuk analytics topik**: 4 langkah setup + keputusan terbuka
- `2026-08-26-rencana-analytics-topik-vira.md` — rencana induk analytics (keputusan terkunci, batasan, arsitektur)
- `2026-08-26-taksonomi-seed-topik.md` — 16 topik hasil analisis 483 pesan pembuka + 151 baris UNKNOWN.
  Temuan penting: **IELTS praktis tidak ada demand** (5 sebutan/634 pesan), dan hari yang
  ditanyakan orang **Sabtu/Minggu, bukan Rabu** — dua asumsi awal yang terbantah data.
- `2026-08-26-laporan-baseline-untuk-sam.md` — versi bahasa bisnis untuk Sam; **belum dikirim**, Steven review dulu
- `2026-08-12-audit-google-sheet-untuk-Sam.md` — root-level active doc (audit sheet)
- `client-materials/` — client reference docs (program info, WA export, phone
  exclusion list). Note: `Batch5_Info_TheScholars_1.docx` and `The Scholars Program
  Seniors.docx` also exist under `report/refrence history original reply from Sam/` —
  duplicate copies kept in both places rather than merged; verify which is canonical
  before editing either.
- `report/patch/` — dated changelog + handoff + JSON per patch, V2 → V6 (**r6,
  2026-08-14, is the last confirmed-working one** — treat V6 patch files as draft/hold).
  Per 2026-08-26 juga berisi: WF-A/WF-B analytics + QA selftest HTML (buka di browser,
  mesin ini tidak punya Node), `analisa-efisiensi-13-ops.md`, dan patch r7/r8 (draft).
- `report/refrence history original reply from Sam/` — client's original reply history
- `mass production/` — reusable template + onboarding docs for new client instances
- `mock booking/` — active booking demo/generator (current version at root; older v2/v3
  iterations already in `archive/enhancement mock booking/`)
- `archive/` — completed/superseded material: 2026-07-02 execution plan + bug report
  (done, folded into V3.x–r6 patches), `AI-systems-audit-2026-06-15/` (one-time),
  `report-production-V4-obsolete/` (frozen V4 export + extracted dumps, superseded once
  r6/V6 patches landed), `report-problem-production/` (closed-out incident investigations)

## Related
- Shared dashboard: `../VIRA Dashboard/memory.md` (serves this client + Persada Cisoka)
- Shared error notifier: `../Fallback VIRA Error Email Notifier/`
- Fork target: `../Persada Cisoka Residence/memory.md`
