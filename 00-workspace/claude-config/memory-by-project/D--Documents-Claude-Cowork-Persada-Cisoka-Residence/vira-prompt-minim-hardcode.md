---
name: vira-prompt-minim-hardcode
description: Steven mau system prompt VIRA minim hardcode fakta; data hidup di sheet PRODUK/FAQ
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1eb9314b-4cd8-4b37-929e-0ceaf7bfef0c
  modified: 2026-07-23T13:40:12.929Z
---

Untuk VIRA-PCR, Steven menolak menaruh fakta bisnis (nominal booking fee, aturan BI Checking, daftar dokumen, dll) sebagai teks hardcode di system prompt AI Agent. Dia hanya mau aturan **perilaku generik** di prompt (mis. "kalau user tanya syarat/dokumen, tampilkan daftar LENGKAP, jangan diringkas").

**Why:** User (tim PCR) harus bisa mengubah sheet PRODUK & FAQ sendiri dan VIRA otomatis menarik info dari sana. Fakta yang di-hardcode di prompt = tidak fleksibel + harus edit workflow tiap ada perubahan bisnis.

**How to apply:** Saat mengusulkan fix konten VIRA, arahkan perubahan fakta ke sheet (PRODUK/FAQ), bukan ke prompt. Prompt cukup diberi aturan framing/perilaku singkat. Jangan tawarkan blok prompt panjang berisi nominal/aturan spesifik. Lihat [[persada-cisoka-status]] dan [[pending-changes-register]].
