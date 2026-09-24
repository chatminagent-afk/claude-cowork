# Memory — VIRA Content (Reels @povstevens)

*Referensi strategi konten untuk penulisan script reels VIRA ke depannya. Diringkas dari brief Steven + dokumen produksi yang sudah ada per 2026-08-14 — CATATAN: skill `reelscript-povstevens` sudah migrasi ke sistem tracker xlsx sejak 19 Agu 2026 (lihat SKILL.md untuk aturan aktif), jadi bagian Workflow/Format di bawah ini sebagian sudah usang.*

## Apa ini
Proyek konten/personal branding Steven di Instagram (@povstevens) — **bukan** chatbot
VIRA itu sendiri. Materi cerita bersumber dari pengalaman build/debug chatbot VIRA
(the scholars, Persada Cisoka, VIRA Steven), tapi output di sini adalah script reel/thread,
bukan kode.

## Workflow — alur kerja proyek ini
1. Ide episode digali dari sesi kerja/debugging nyata (proyek chatbot lain) via skill
   `/reelscript-povstevens` — pakai jun_yuh LIFE wheel + teknik 3 Why (safe/real/raw).
2. Draft naskah masuk batch bernomor (`2026-07-14-reels-batch-1/`,
   `reels/9 ags/`, `reels/18 ags/`) — tiap batch punya file revisi final sendiri, versi
   lama dipindah ke `_arsip/` dalam batch itu, bukan ditimpa.
3. **Wajib privacy-check** (skill `/privacy-check`) sebelum syuting/posting — cek nama
   klien, kredensial, data user asli, angka biaya/kapasitas. Lihat bagian "Privacy" di
   bawah untuk aturan lengkap.
4. Status produksi (naskah → syuting → posting) dilacak di
   `reels/2026-08-14-script-reels-vira-tracker.xlsx`.
5. Footage b-roll reusable (screen recording, mock chat, ilustrasi) dikumpulkan di
   `reels/b-roll/` — dipakai lintas episode, bukan sekali pakai per naskah.
6. Konten format thread (non-reel) punya bank ide sendiri di `threads/`.

## Positioning & Brand
- Target audiens: **owner bisnis muda yang bisnisnya sedang tumbuh/scale up** — bukan sekadar "UMKM capek bales chat".
- Angle kepercayaan: solo builder — "masih aku sendiri yang pegang, tiap proyek dikerjain serius".
- CTA payung = **AI automation**, VIRA cuma salah satu produk (produk lain: RAPI, sistem manajemen proyek — demo selalu de-branded di kamera).
- Positioning VIRA: **"AI Customer Service yang dibangun sesuai tujuan tiap bisnis"** — bukan chatbot template, bukan ketik-angka-pilih-menu.
- Gaya storytelling: ala Nate Herk/Nick Saraev — hook first-person result-first + angka konkret; fail/blooper transparency; CTA soft & back-loaded; audience loop ("komen: proses apa yang paling makan waktu?"); narasi iterasi ("VIRA udah versi 4") — realita bolak-balik fixing, bukan langsung sempurna.
- Framework naskah: **jun_yuh LIFE wheel + teknik 3 Why (safe/real/raw)** — dipakai skill `reelscript-povstevens`, gali tiap beat cerita sampai layer "raw", bukan berhenti di permukaan.

## Format & Struktur Naskah
- Durasi standar: ~60 detik.
- Struktur: **Hook → Isi/Body → (Reveal VIRA) → CTA**.
- Bahasa awam — hindari istilah teknis (debounce, race condition, HITL, token, dsb), ganti analogi sehari-hari.
- CTA tiap episode: "follow, next [teaser konkret]" + "komen/DM kalau mau sistem serupa buat bisnismu". Episode jualan boleh lebih tegas ("komen OTOMASI").
- Jangan pernah sebut hari spesifik ("Rabu", "Sabtu") di CTA — cukup "next episode".
- Hashtag standar: **#otomasibisnis #aiautomation** + 2-3 tag relevan tema episode (`#buildinpublic`, `#whatsappbusiness`, `#debugging`, `#umkmindonesia`, dst).

## Privacy — WAJIB dicek tiap script baru
- **Jangan pernah sebut nama klien** — termasuk dua klien nyata yang jadi bahan cerita ("edukasi beasiswa" dan "developer properti" dalam script). Cukup pakai deskripsi generik: "salah satu klien", "platform edukasi", "developer properti".
- Jangan tampilkan/sebut: kredensial apa pun, system prompt penuh, Sheet ID, data user asli (nama+nomor WA), rekening, private key, angka biaya/budget operasional, angka kapasitas/skalabilitas sistem spesifik.
- Demo/screen-record wajib pakai environment mock/dummy — bukan production.
- Ilustrasi chat di visual = buatan sendiri/dummy, bukan chat user asli.
- Angka yang dipakai harus grounded ke data agregat yang sudah diverifikasi (bukan klaim absolut spekulatif seperti "selalu 5 detik") — cek memory `vira-v4-fix-status` di auto-memory Claude untuk fakta yang sudah aman dipakai.
- Kalau cerita bug/insiden berasal dari kejadian nyata klien, generic-kan konteksnya (skenario dummy) sebelum masuk script — jangan copy transkrip asli.

## Referensi Naskah yang Sudah Ada
- **Batch arsip no. 1–12** (`2026-07-14-reels-batch-1\2026-07-22-reels-revisi-final.md` — format lama, sebelum migrasi ke tracker) — cerita: leads follow-up, bukan programmer, demo kerja 24 jam, bug "amnesia" TTL, bug message buffering, delay sengaja anti-spam, versi awal jujur, fitur nanya-balik-ke-owner, fitur auto-detect yang dihapus, ganti AI model murah, yakin-vs-bukti debugging, season finale.
- **Batch "script reels" 1–10** (`reels/9 ags/1-5` untuk 1-5, sisanya baru) — cerita: telat bales chat bikin kehilangan pelanggan, chatbot gampang tapi ngerti bisnis susah (2 contoh klien), bukan butuh admin tambahan tapi butuh AI, 5 tahun di BCA & customer focus, BTS bikin AI pertama, salah paham kata "boleh", privacy-by-design, nanya-dulu-daripada-nebak, nervous sebelum go-live, mindset security.
- **Tracker status produksi:** `reels\2026-08-14-script-reels-vira-tracker.xlsx` — kolom nomor/script/caption/status/tanggal.

## Ide Cerita yang Belum Dipakai (stok untuk script berikutnya)
- Sistem yang harus disiapkan buat lonjakan traffic besar (generic-kan total, jangan sebut angka kapasitas/biaya asli).
- Proses testing skenario "orang iseng nyoba ngetes AI-nya" (edge case aneh yang pernah ketemu).
- Cerita soal gimana VIRA belajar "nada bicara" tiap owner biar kerasa konsisten sama brand kliennya.
- Momen serah terima ke klien — pertama kali owner lihat sistemnya jalan sendiri.

## Related
- Sumber cerita: `../the scholars/memory.md`, `../Persada Cisoka Residence/memory.md`,
  `../VIRA Steven/memory.md`
- Dashboard VIRA (bukan bagian proyek konten ini, jangan tertukar): `../VIRA Dashboard/memory.md`
