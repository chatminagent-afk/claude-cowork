---
name: thescholars-monthly-invoice
description: Generate invoice bulanan Persada Cisoka Residence setiap tanggal 27
---

Kamu adalah assistant yang bertugas generate invoice bulanan Persada Cisoka Residence (VIRA AI Chatbot).

Setiap tanggal 27, lakukan langkah berikut:

**LANGKAH 1 — Tanya item tambahan**
Gunakan tool AskUserQuestion untuk bertanya kepada user:
- Pertanyaan: "Ada item tambahan yang ingin dimasukkan ke invoice bulan ini (selain VIRA Basic Plan IDR 3,000,000 dan Add On Send Media IDR 300,000)?"
- Pilihan: "Tidak ada, langsung generate" dan "Ya, saya ingin tambah item"

**LANGKAH 2A — Jika tidak ada item tambahan:**
Jalankan script dengan mode silent:
```
python "D:\Documents\Claude Cowork\Persada Cisoka Residence\invoice\generate_invoice.py" --silent
```

**LANGKAH 2B — Jika ada item tambahan:**
Tanya user untuk setiap item:
- Nama item
- Qty (boleh angka atau teks, mis. "$5 USD")
- Harga/Subtotal (IDR)
- Diskon (jika ada)

Kemudian tulis item-item tersebut ke file JSON sementara di:
`D:\Documents\Claude Cowork\Persada Cisoka Residence\invoice\extra_items_temp.json`

Format JSON:
```json
[{"name": "Nama Item", "qty": 1, "price": 500000, "discount": null}]
```

Lalu jalankan script dengan:
```
python "D:\Documents\Claude Cowork\Persada Cisoka Residence\invoice\generate_invoice.py" --extra-items "D:\Documents\Claude Cowork\Persada Cisoka Residence\invoice\extra_items_temp.json"
```

Setelah selesai, hapus file temp extra_items_temp.json.

**LANGKAH 3 — Selesai**
Gunakan mcp__cowork__present_files untuk menampilkan file invoice PDF yang baru dibuat kepada user.
Berikan pesan singkat: nomor invoice, tanggal, dan grand total.

**Catatan penting:**
- Invoice tersimpan di: D:\Documents\Claude Cowork\Persada Cisoka Residence\invoice\
- State file (untuk tracking nomor invoice): D:\Documents\Claude Cowork\Persada Cisoka Residence\invoice\invoice_state.json
- Nama file format: PCR_{NNN}.pdf (contoh: PCR_002.pdf), nomor invoice di dalam PDF ditampilkan sebagai INV-{NNN}
- Invoice terakhir yang sudah terbit: PCR_001.pdf (27 Juli 2026). Invoice berikutnya otomatis jadi #002.
- Selalu generate invoice meskipun user tidak merespons dalam 10 menit (gunakan --silent mode)