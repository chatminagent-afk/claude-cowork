---
name: vira-steven-aksi-lewat-tag-bukan-tool
description: AI Agent VIRA Steven tidak punya tool sama sekali; semua aksi dipicu tag teks yang ditulis LLM lalu di-regex node Process All
metadata: 
  node_type: memory
  type: project
  originSessionId: 226a5d21-ea40-40ff-b33c-3d5aecf14bc0
  modified: 2026-08-16T17:28:42.162Z
---

Node `AI Agent` di workflow VIRA Steven **tidak punya satu pun koneksi `ai_tool`** — hanya
`ai_memory` (Simple Memory) dan `ai_languageModel` (Anthropic). Jadi LLM murni
chat-completion. Semua "aksi" dijalankan dengan cara LLM **menulis tag teks** di dalam
balasannya (`[SEND_MEDIA: ...]`, `[TALK_TO_ADMIN]`, `[UNKNOWN]`, `[DECK_REQUEST]...[/DECK_REQUEST]`,
`[FACTS]`), yang lalu di-regex oleh Code node `Process All` dan mencabangkan alur.

**Why:** ini menciptakan satu kelas bug yang tidak ada di arsitektur function-calling —
**LLM bisa mengklaim sudah melakukan sesuatu tanpa tag apa pun, dan tidak ada yang
membantah.** Contoh nyata (16 Agt 2026): VIRA menjawab "Aku sudah kirim video demonya tadi
kak" tanpa menulis `[SEND_MEDIA]`, sehingga `isSendMedia` tetap `false`, tidak ada file yang
dikirim, dan kalimat bohong itu lolos utuh ke prospek. Guard FAIL LOUD yang ada di
`Process All` hanya menyala kalau tag SUDAH muncul tapi key-nya tidak ketemu di tab LINKS —
bukan saat tag tidak pernah ada.

**How to apply:** saat mendiagnosis "VIRA bilang X tapi X tidak terjadi", cek dua hal
berurutan: (1) apakah tag-nya benar-benar keluar di output LLM, (2) baru cabang eksekusinya.
Jangan pernah mengandalkan instruksi bahasa alami di system prompt sebagai jaminan — model
murah (Haiku) tidak patuh 100%. Setiap kemampuan baru butuh **guard di kode**: kalau teks
balasan menjanjikan aksi (regex kata kerja "kirim/share/lampirkan" + objek "video/file/deck")
sementara tag terkait tidak ada, timpa balasannya. Alternatif struktural: pindah ke tool
call sungguhan. Terkait: [[vira-steven-jalan-di-nomor-pribadi-campuran]].
