---
name: repo-claude-cowork-public-bocor
description: "29/09 ditemukan repo GitHub chatminagent-afk/claude-cowork PUBLIC berisi private key SA Google, secret Kirimi, Sheet ID, nomor WA asli; rename VIRA→MIVA ditunda menunggu approval"
metadata:
  node_type: memory
  type: project
  originSessionId: efaf27f4-007e-459f-b8aa-2d72024f6de6
  modified: 2026-09-29T02:25:00.506Z
---

2026-09-29: repo `chatminagent-afk/claude-cowork` bisa diakses publik sejak commit ac37c01 (24/09). Isinya: private key service account asli (`projects/persada-cisoka/config_section.txt`), ±19 nilai secret, 104 file dengan Sheet ID, 220 file dengan nomor WA 628…. Claude tidak mengubah GitHub (gh CLI tidak terpasang, dan ini aksi keluar). Langkah yang disarankan (private → rotasi key → bersihkan history → gitleaks) dicatat di `MIVA Steven\docs\2026-09-28-panduan-rebrand-MIVA-ringkas.md` langkah 10.

Rename VIRA→MIVA DIEKSEKUSI 29/09 ("rename semua"): 638/640 nama, referensi di 474 file, git 3653a08 + ba2cec0 sudah di-push. Sisa: folder `MIVA` dan `VIRA\VIRA Steven` (terkunci sesi Claude) → Steven jalankan `D:\Documents\Claude Cowork\2026-09-29-selesaikan-rename-miva.bat`, yang juga menyalin memory ke `D--Documents-Claude-Cowork-MIVA`. Rename repo `vira-workflows` dilakukan manual lewat web. Per 29/09 repo claude-cowork MASIH public (langkah 10 belum). Status lengkap: panduan rebrand langkah 11.

**How to apply:** di sesi berikutnya, tanyakan dulu status langkah 10 (sudah private/rotasi?) sebelum push apa pun ke repo itu. Jangan eksekusi rename sebelum Steven menjawab keputusan di langkah 11. Terkait [[rebrand-vira-ke-sapa-ai]].
