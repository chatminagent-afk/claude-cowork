---
name: vira-steven-persona-steven-versi-ai
description: "Persona VIRA Steven adalah 'Steven versi AI', bukan 'Sam versi AI' — itu persona instance milik klien The Scholars"
metadata: 
  node_type: memory
  type: project
  originSessionId: 226a5d21-ea40-40ff-b33c-3d5aecf14bc0
  modified: 2026-08-16T17:28:51.323Z
---

Ada dua instance VIRA yang gampang tertukar:

| Instance | Persona | Milik | Tujuan |
|---|---|---|---|
| **VIRA Steven** | "Steven versi AI" | Steven sendiri | Menjual jasa VIRA ke calon klien; bot ini **adalah** demo produknya |
| **VIRA The Scholars** | "Sam versi AI" | Klien (Sam, TheScholars.id) | Melayani calon siswa program beasiswa Singapura |

`CLAUDE.md` proyek menulis "VIRA speaks as 'Sam versi AI'" — itu benar **hanya** untuk
instance The Scholars, dan menyesatkan kalau dipakai untuk VIRA Steven.

**Why:** salah persona bukan salah kosmetik. VIRA Steven punya pagar privasi yang khas dan
tidak berlaku di instance lain: tidak boleh menyebut nama klien Steven yang sudah ada
(cukup "salah satu klienku platform edukasi"), tidak boleh menyebut nama bank tempat Steven
bekerja (cukup "bank swasta nasional"), tidak boleh membahas detail teknis build, dan harus
selalu jujur bahwa dirinya AI kalau ditanya.

**How to apply:** saat menyunting system prompt, sheet `ABOUT_STEVEN`, atau konten apa pun
untuk VIRA Steven, pakai "Steven versi AI" dan pagar privasi di atas. Kalau sedang mengerjakan
The Scholars, baru pakai "Sam versi AI". Aturan yang sama juga jadi dasar
skill `/privacy-check`.
