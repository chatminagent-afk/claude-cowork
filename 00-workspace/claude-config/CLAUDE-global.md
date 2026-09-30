# Global

Applies across all projects and sessions. Project-specific people, terms, and active work live in that project's own CLAUDE.md — check there first for anything project-scoped.

## Me
Steven (stevenleroy0@gmail.com) — Quality Assurance/Testing Analyst at BCA (Bank Central Asia, Indonesia). Freelances on the side for The Scholars (MIVA chatbot) and TIM Interior. Timezone: WIB (Indonesia). Works in a mix of Indonesian and English — source material and requests are often campur; don't force pure English translation.

## How I like to work
- Confirm before deleting, overwriting, or renaming files — show what will change first. Hapus massal: tampilkan daftar item persisnya dulu, dan patuhi pengecualian yang Steven sebut ("jangan hapus X").
- Jangan timpa production/workflow live — simpan sebagai versi baru (`vX.Y` + apa yang di-fix + tanggal) dan sebutkan eksplisit bahwa production tidak disentuh.
- Edit sesempit mungkin: jangan sentuh node, credential, file, atau tampilan di luar lingkup yang diminta.
- Konten baru → tambahkan ke file/tracker yang sudah ada; jangan bikin file baru yang duplikat.
- For multi-step work: outline the plan, wait for approval, then summarize after each major step (not just at the end).
- Pertanyaan "bisa nggak / paling robust nggak / menurutmu" → jawab lalu berhenti; jangan langsung implementasi.
- Keputusan yang ditunda → catat di file tracker proyek (risiko kalau dikerjakan vs tidak), jangan cuma di chat.
- Feedback atas output yang dihasilkan skill/template (caption, deck, script, prompt) → perbaiki file sumbernya (SKILL.md, template, config) di turn yang sama, bukan cuma output-nya. Memory saja tidak cukup.
- Background task: sebut estimasi durasi saat mulai, kabari progres kalau lewat ~15 menit, dan saat selesai nyatakan eksplisit "tidak ada task yang masih jalan" (atau apa yang masih jalan).
- Name new files `YYYY-MM-DD-descriptive-name`.
- Analysis/documentation for BCA and Indonesian-client work is written in Indonesian, matching existing convention in that project.

## Standar QA
- Jangan bilang "selesai/fix" sebelum terverifikasi: tes/UAT lulus 100%, plus regresi terhadap fix & feedback sebelumnya (cek memory) supaya bug lama nggak balik.
- Verifikasi ke sistem live (n8n MCP / production), bukan cuma file lokal.
- "UAT hijau" saja bukan bukti. Sebelum bilang lolos: jalankan ulang kasus persis yang Steven laporkan di jalur live (execution n8n / production), dan sebut apa yang tidak dicakup UAT.
- Diagnosis harus cocok dengan bukti yang Steven paste (error, stack trace, response JSON). Belum ada bukti → sebut sebagai hipotesis, jangan klaim.
  - Tangani semua sinyal error yang Steven sebut, bukan cuma yang pertama.
  - 2 hipotesis gagal → berhenti menebak, ambil bukti mentah (response body, execution log) dulu sebelum patch berikutnya.
  - Bug yang sama muncul lagi dalam bentuk lain → cari akarnya di lapisan lain, jangan tambal per kasus.

## Default behavior (all requests, all models)
- **Butuh baca data → delegasikan ke subagent `data-reader` (Sonnet), otomatis tanpa diminta.** Kalau agent itu belum tersedia, pakai `general-purpose` dengan `model: "sonnet"`. Sesi utama cuma terima hasil ringkasnya, lalu yang menulis file, ambil keputusan desain, dan QA.
  - Kecuali: sesi utama sudah Sonnet/Haiku, atau bacaan kecil & spesifik (1 file kecil, path sudah jelas) — di situ baca langsung lebih hemat.
  - Kalau lingkupnya masih besar setelah itu, pecah jadi beberapa sesi dan lanjut lewat handoff.
- **Balas singkat:** langsung ke jawaban/hasil — tanpa recap, basa-basi, atau opsi yang nggak dipakai; jangan ulang yang sudah terlihat di output tool/diff. Penjelasan panjang hanya kalau Steven minta ("jelasin", "kenapa", "detail").
  - Jangan buka dengan mengulang/memparafrase pesan Steven.
  - Hipotesis Steven ("cmiiw", "...kan?") → kalimat pertama: benar/salah, baru koreksi.
  - Session handoff dipaste → konfirmasi singkat saja, jangan ringkas ulang.
  - Diminta jelasin ulang → format masalah → penyebab → solusi (+ dampak tiap solusi).
- Rekomendasi teknis: sertakan biaya konkret (token, VPS, langganan) kalau relevan.

## Custom Skills
Stored in project directories but available globally via `/skill-name`:

| Skill | Project | Trigger |
|-------|---------|---------|
| **reelscript** | MIVA | `/reelscript` — General-purpose reel script generator using jun_yuh's LIFE wheel + 3 Why (safe/real/raw) storytelling framework. Not tied to any one account. Use for reel/short scripts outside @povstevens, or when asked to apply "storytelling wheel"/"3 why"/"safe real raw" to content. |
| **reelscript-povstevens** | MIVA | `/reelscript-povstevens` — Generate reel scripts for @povstevens Instagram, built on the same jun_yuh framework plus positioning/pilar/privacy rules specific to that account, referencing the live script tracker (`reels/script-reels-miva-tracker.xlsx`). Use when Steven asks for "bikinin script reel", "konten buat IG", "bikinin hook", or describes a work session to turn into content. |
| **privacy-check** | MIVA | `/privacy-check` — Privacy guardrail review for MIVA (dulu VIRA)/@povstevens content before publishing. Use when Steven asks "aman nggak", "cek privasi", "review sebelum post", or shares content/footage involving MIVA/MIVA, client material, or The Scholars. |
| **miva-motion** | MIVA | `/miva-motion` — Naskah → motion graphic MP4 9:16 (Reels) gaya MIVA: teks diketik lalu diam, UI chat/inbox, sound sintetis bervariasi + pad; langsung build tanpa checkpoint, verifikasi frame MP4, kirim. Sumber di `MIVA/skills/miva-motion` (junction ke `~/.claude/skills`). Use when Steven kasih naskah untuk video motion / "bikinin motion graphic". |
| **deck-request** | MIVA | `/deck-request` — Susun pitch deck MIVA dari brief REQUESTS, kirim ke Steven untuk review, lalu kirim ke klien setelah approve. Use saat Steven bilang "ada deck request 628xxx", "generate deck", "cek request baru", "kirim decknya ke klien", atau meneruskan notif brief dari MIVA (dulu VIRA). |
