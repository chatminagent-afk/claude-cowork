---
name: motion-video-hyperframes
description: "Pipeline motion video dari kode (HyperFrames + edge-tts + kirim WA via Kirimi) — POC 2026-09-29, lokasi, gotcha, dan kenapa HyperFrames dipilih"
metadata:
  node_type: memory
  type: project
  originSessionId: efaf27f4-007e-459f-b8aa-2d72024f6de6
  modified: 2026-09-29T05:20:18.467Z
---

POC 2026-09-29 di `VIRA\reels\2026-09-29-motion-video-hyperframes\` (README berisi pipeline lengkap). Video 9:16 25 dtk "admin yang nggak pernah tidur" terkirim ke WA Steven via Kirimi.

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
- **Skill `miva-motion` DIBUAT 29/09** (`VIRA/skills/miva-motion`, junction ke ~/.claude/skills): naskah → MP4 tanpa checkpoint storyboard (pilihan Steven), pad ambient default ada. Feedback berikutnya → perbaiki file skill + `references/changelog.md`.
- Rename folder VIRA→MIVA: Steven menjalankan bat rename SETELAH ada satu motion graphic yang benar (v3 dibangun di path VIRA).

**How to apply:** untuk video/reel berikutnya, lanjutkan dari folder ini (copy `poc/` jadi project baru), jangan setup ulang. Tetap jalankan [[privacy-check]] sebelum posting; ilustrasi chat harus dummy ([[vira-fakta-konten]]).
