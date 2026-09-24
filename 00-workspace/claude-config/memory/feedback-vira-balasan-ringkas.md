---
name: feedback-vira-balasan-ringkas
description: "Balasan VIRA Personal harus ringkas & tidak mengulang ucapan prospek — tapi tidak sependek VIRA TS milik Sam"
metadata:
  type: feedback
---

Balasan VIRA Personal (Steven versi AI) jangan bertele-tele dan jangan membuka dengan merangkum/memparafrasekan jawaban prospek ("Jadi alurnya ada dua...", "Berarti...", "Paham, berarti..."). Tapi juga **tidak sependek VIRA TS** (Sam versi AI: default 1 kalimat, maks 2, ±10–17 kata).

**Why:** Steven 2026-09-18 setelah uji 17/09 — kesannya VIRA "sering mengulang jawaban yang diberikan user". Balasan waktu itu 3–4 kalimat, 40–70 kata.

**How to apply:** patokan v3.10 = 2 kalimat, ±20–35 kata (satu menanggapi dengan menambah hal baru, satu bertanya), batas keras 3. Atur lewat prompt (bagian GAYA + ALUR 10), bukan temperature/maxTokens — lihat [[vira-temperature-jangan-diturunkan]]. Panjang tidak bisa diuji UAT; nilai di uji manual nomor asli.

Terkait: [[vira-v3-10-nama-usaha-ringkas]]
