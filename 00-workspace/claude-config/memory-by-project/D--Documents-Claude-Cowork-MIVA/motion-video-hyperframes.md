---
name: motion-video-hyperframes
description: "Pipeline motion video dari kode (HyperFrames + edge-tts + kirim WA via Kirimi) — POC 2026-09-29, lokasi, gotcha, dan kenapa HyperFrames dipilih"
metadata:
  node_type: memory
  type: project
  originSessionId: efaf27f4-007e-459f-b8aa-2d72024f6de6
  modified: 2026-09-29T07:13:31.096Z
---

POC 2026-09-29 di `MIVA\reels\2026-09-29-motion-video-hyperframes\` (README berisi pipeline lengkap). Video 9:16 25 dtk "admin yang nggak pernah tidur" terkirim ke WA Steven via Kirimi.

- Pilihan tool: HyperFrames (HeyGen, Apache-2.0, HTML+GSAP, skill resmi Claude Code) > Remotion (cadangan; lisensi berbayar kalau 4+ orang) > Motion Canvas (mandek) / Revideo (kecil).
- Node tidak terinstall di sistem; pakai Node portable di folder `node/` proyek itu (Steven pilih portable, bukan winget).
- TTS: edge-tts `id-ID-ArdiNeural` (gratis, pilihan Steven); Gemini Flash-Lite TTS jadi opsi berbayar murah, butuh key yang Steven set sendiri.
- Gotcha: `<audio>` tanpa `id` = bisu di render; `hyperframes check` menangkapnya.
- "19:6" dari Steven = maksudnya 9:16 vertikal.
- Feedback v1: Steven TIDAK suka voiceover edge-tts. v2 (29/09) = tanpa VO, SFX sintetis ffmpeg, musik ditambahkan di IG. Arah desain yang dia mau: transisi bentuk/teks halus mengalir, palet minimalis landing MIVA, tempo cepat tapi terbaca (referensi: 2 video Klickpin di D:\Download). Feedback v2 (29/09): "gerakannya masih tidak natural, teksnya aneh bergerak". Steven mau rebuild (v3) di sesi baru. Dugaan penyebab (BELUM diverifikasi): pan kamera linear terus-menerus saat teks dibaca, tween keluar x:-120 bertabrakan dengan pan, overshoot back.out di gelembung/chip, kata di kotak yang bertumpuk saat berganti.
- Gotcha: encoder MP4 HyperFrames di Windows menghitamkan 8px kanan → render lewat `render-final.ps1` (PNG sequence + ffmpeg sendiri).
- Skill motion-graphics disepakati dibuat SETELAH 1–2 revisi desain disetujui, bukan sebelumnya. ⚠ Nama `motion-graphics` sudah dipakai skill resmi HyperFrames (terpasang global 29/09 di ~\.claude\skills) → skill kita pakai nama lain, mis. `miva-motion`.
- v3 (29/09, `v3/`): diagnosis v2 terbukti (pan linear saat dibaca, tween keluar bentrok dengan pan, back.out, kata bertumpuk di kotak). Steven minta: teks **typing** dan **diam setelah muncul** (geser kiri/kanan "aneh sekali"); sound ala pesan chat, bunyi WA asli tidak dipakai (milik Meta) → blip sintetis. Aturan gerak lengkap di README bagian v3. Menunggu penilaian Steven; kalau cocok → kunci jadi skill.
- v4 (29/09, `v4/`): brief gelap 3-act "Incoming → MIVA → Outcome", 22 dtk, pakai aturan v3 (Steven: "okelah pakai dulu v3"). Menunggu penilaian.
- Gotcha render: png-sequence bikin html/body/#root transparan → latar hitam + gradient jadi cincin bergaris; snapshot tidak menunjukkannya. Latar solid wajib di div layer sendiri; cek frame dari MP4, bukan snapshot.
- v4 dinilai "much better"; feedback: sound "sedikit kaku" → v4.1 (sound dari `make_sound.py`), menunggu penilaian sound.
- **Skill `miva-motion` DIBUAT 29/09** (`MIVA/skills/miva-motion`, junction ke ~/.claude/skills): naskah → MP4 tanpa checkpoint storyboard (pilihan Steven), pad ambient default ada. Feedback berikutnya → perbaiki file skill + `references/changelog.md`.
- Rename folder VIRA→MIVA: Steven menjalankan bat rename SETELAH ada satu motion graphic yang benar (v3 dibangun di path VIRA lama).
- v5 (29/09, `v5/`): v4.1 + Act "Sampai beres." (kartu owner berganti: handover, follow up, lead→Sheets, di luar FAQ) + strip kecil premium & add-on. Steven minta v2/v3/v4 dihapus (bukan _snap-v4), sisakan v4.1 — sudah dipindah ke Recycle Bin 29/09.
- Feedback v5 → v6 (36 dtk): fitur harus DITUNJUKKAN terjadi (follow up: MIVA mengetik + pelanggan membalas), premium = bento mock UI (bukan chip), banjir chat 100+ dengan auto-scroll list. Sudah dimasukkan ke skill miva-motion (motion-rules 7a & §Fitur).
- Feedback v6 → v7: angka naik = count-up terus (bukan 3/27/100+), jam pembuka = jam digital 7-segmen, konten di x 140–940 (Reels di HP 19,5:9 memotong sisi). Masuk skill (design.md, components, changelog). v7 DISETUJUI 29/09 → jadi `template/index.html` skill miva-motion (v4.1 dicadangkan di `_cadangan-2026-09-29-template-v4.1/`).
- Junction `~/.claude/skills/miva-motion` sudah diarahkan ulang ke `MIVA\skills\miva-motion` (29/09); sebelumnya rusak karena masih menunjuk path MIVA.
- Motion #3 "fresh" (29/09, `reels/2026-09-29-motion-miva-fresh/`): gabungan v7 + launch v2, palet lime `#cbf24b` + kertas + tinta, 24,9 dtk, musik 100 bpm per 1/8 + pulse. Dikirim, menunggu penilaian Steven. Palet & tempo sudah dicatat di skill (design/motion-rules/sound/components/changelog).
- Motion #4 "keynote" (29/09, `reels/2026-09-29-motion-miva-keynote/`): hook kata per layar di latar hitam → cut putih saat "MIVA nggak.", ponsel pahlawan + headline gradien hijau, 24/7, end card putih; 23,3 dtk, 110 bpm. Steven: "aku suka" (29/09). ⚠ headline "Dibalas instan." overclaim (bot sengaja delay 5–10 dtk) — belum diganti.
- Motion #5 "listicle" (29/09, `reels/2026-09-29-motion-miva-listicle/`, dibangkitkan `build.py`): 11 kerjaan MIVA + progress bar Stories, gaya keynote, 30,9 dtk. Menunggu penilaian.
- **Dirapikan 29/09 (permintaan Steven):** semua video motion sekarang di `MIVA
eels\motion\` — `1-poc`, `2-inbox/v4.1–v7`, `3-launch/v1–v2`, `4-fresh`, `5-keynote`, `6-listicle`; MP4 final di `motion\hasil\<nama>.mp4`; Node portable & `kirim_video_wa.py` di `motion\_tools\`; daftar + status di `motion\README.md`. Path lama `reels6-09-29-motion-*` di catatan atas sudah TIDAK ada. `_snap-v4` & folder snapshots dibuang ke Recycle Bin.

- Motion #7 "jam 2" (30/09, `reels/motion/7-jam2/`, `build.py`): adaptasi iklan Notion "You at 2 a.m." — tidur (jam digital, lullaby) ↔ MIVA kerja (cut putih + beat 808 drop), 11 fitur, 31,5 dtk, CTA "DM @povstevens". Steven: "bagus" (30/09). Palet sound "drop" + alur video referensi masuk skill.

**How to apply:** untuk video/reel berikutnya, pakai skill `/miva-motion` (proyek baru = `reels\motion\<n>-<nama>\`), jangan setup ulang. Tetap jalankan [[privacy-check]] sebelum posting; ilustrasi chat harus dummy ([[miva-fakta-konten]]).
