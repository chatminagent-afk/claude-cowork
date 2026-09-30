---
name: vira-temperature-jangan-diturunkan
description: "Temperature node chat VIRA tetap 0.7 — menurunkannya merusak aturan \"variasikan pembuka\" di system message"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6622fa63-51d6-4cc7-bf17-f2e8ab534c41
  modified: 2026-09-03T07:49:44.352Z
---

Node `DeepSeek Personal Chat` di workflow VIRA Personal dipertahankan di `temperature: 0.7`.
Jangan diturunkan untuk memendekkan balasan.

**Why:** Temperature bukan tuas panjang kalimat — efeknya ke panjang cuma tidak langsung
(menaikkan variasi, bukan memperpendek). Sementara system message VIRA punya aturan
"Variasikan pembuka. Jangan setiap balasan dimulai dengan 'Baik', 'Oke', atau 'Wah'" yang
justru butuh keacakan. Temperature rendah bikin pembuka seragam dan terasa template —
kerugian mahal untuk bot sales yang nilai jualnya "kelihatan seperti manusia".

**How to apply:** Kalau balasan VIRA kepanjangan, perbaiki di system message (batas kalimat
sebagai langkah terakhir `# ALUR`, plus resolusi konflik dengan langkah "gali satu hal"),
bukan di parameter node. `maxTokens: 1024` juga bukan tuasnya — menurunkannya memotong
kalimat di tengah, bukan meringkas. Lihat [[vira-fakta-konten]].
