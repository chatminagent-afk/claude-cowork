---
name: persada-cisoka-residence
description: "Proyek remake VIRA untuk Persada Cisoka Residence (developer perumahan) — status, klien, dan keputusan arsitektur kunci"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9362e112-bdef-4832-96bf-9fedf6504f2e
---

Proyek baru (mulai 2026-07-15): remake chatbot VIRA (The Scholars) menjadi chatbot telemarketer WhatsApp untuk **Persada Cisoka Residence**, developer perumahan (area Cisoka/Tangerang). Kontak klien: **Om Sulianto**. Folder: `D:\Documents\Claude Cowork\Persada Cisoka Residence`.

6 fungsi inti: survey scheduling, follow-up otomatis (flag_survey ≠ Y), call redirection ke nomor admin, deteksi sumber traffic (Google/FB/IG dari template teks awal), persona telemarketer (unit/KPR/lingkungan), delegasi klien terjadwal ke tim lapangan.

Keputusan arsitektur kunci (fase eksplorasi 2026-07-15, 7 dokumen sudah ditulis di folder proyek):
- Basis remake = **logika node VIRA V4 production + lapisan config multi-tenant dari VIRA_TEMPLATE_v1** — template saja TIDAK cukup karena belum mewarisi fix kritikal V4 (identitas No WA/lid, MSG_BUFFER, debounce 2-lapis)
- `VIRA_Follow_Up.json` lama rusak diam-diam (baca kolom `STATS.timestamp` yang sudah tak ditulis V4) — follow-up baru dirancang terhadap skema STATS V4 (`last_reply_ts`)
- Kirim media terverifikasi dari docs Kirimi: field opsional `media_url` di `POST /v1/send-message` yang sama (PDF/gambar, maks 64MB) — tidak butuh endpoint baru; brosur di-host di URL publik
- Pola tag output AI dipertahankan: `[SCHEDULE_SURVEY]`, `[SEND_MEDIA: key]` meniru pola `[SEND_GFORM]`/`Talk To Sam` dari V4

Fase drafting (2026-07-15, folder `draft workflow\`): Google Sheet database 11 tab (xlsx) + 3 workflow n8n dirakit terprogram dari ekstraksi V4 (script rerunnable di `_extraction\build\`): VIRA-PCR-main (71 node, sampai notify tim lapangan), buffer-cleanup, error-notifier + README deploy. Semua tervalidasi (parse, connections, no leftover Sam/scholars, no secrets). Fakta penting: field penerima Kirimi = `phone` (BUKAN `receiver` seperti docs publik); kolom `debounce_ts` di STATS = baton debounce, wajib ada. **Workflow Follow-Up belum dirakit** (kolom flag_survey/follow_up_count/last_follow_up_ts belum ada penulisnya) — itu langkah berikutnya bersama pengisian data klien.

Menunggu dari klien: hasil sesi Zoom dengan tim telemarketer (daftar pertanyaan sudah dibuat), export chat WA yang berhasil sampai survey (template request sudah dibuat), data produk (harga, tipe unit, bank KPR, brosur, nomor admin & tim lapangan).

Terkait: [[vira-the-scholars]]
