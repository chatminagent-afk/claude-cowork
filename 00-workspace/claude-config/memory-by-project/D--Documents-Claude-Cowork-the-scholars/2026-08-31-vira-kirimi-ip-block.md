---
name: vira-kirimi-ip-block
description: VIRA down 2026-08-31 karena Kirimi memblokir IP egress server n8n; IP egress dan cara diagnosanya
metadata:
  type: project
---

Server n8n VIRA (self-hosted, Hostinger VPS Jakarta, AS47583) punya **IP egress `76.13.18.214`** — sama untuk HTTP Request node maupun Code node (JsTaskRunner), sudah diverifikasi 2026-08-31.

Pada 2026-08-31 seluruh pengiriman WhatsApp VIRA mati dengan HTTP 403. Body responsnya:
`{"success":false,"data":null,"message":"Access denied. Your IP has been blocked due to suspicious activity."}`
Bukan kredensial, kuota, device, nama field, maupun content-type — murni blokir IP di sisi Kirimi. Hanya support@kirimi.id yang bisa mencabutnya.

**Why:** Diagnosanya makan 4 putaran karena node `Send WA + Verify (Kirimi)` (Code node) hanya menyimpan `lastErr.message` dan membuang body respons. Node HTTP Request biasa memunculkan `rawErrorMessage` — itu yang akhirnya membuka jawabannya.

**How to apply:** Kalau VIRA kena 403 lagi, jangan tebak-tebak kredensial/kuota: reproduksi sekali pakai **HTTP Request node polos** (bukan Code node) untuk melihat body aslinya. Ingat juga bahwa Error Notifier VIRA mengirim alert lewat Kirimi juga — saat Kirimi yang bermasalah, alert WA ikut mati dan yang tersisa hanya email fallback. Retry berlapis (`AI Agent` 3x × `Anthropic Chat Model` 3x; enam node Kirimi dengan `retryOnFail`) memperbesar risiko kena flag anti-abuse. Lihat [[vira-stats-archiving-plan]].
