---
name: heredoc-makan-backslash
description: "Heredoc shell di sesi ini memakan satu level backslash — script patch yang menyuntik JS ber-regex wajib ditulis sebagai file, bukan heredoc"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 448502b0-0538-4fb0-86dd-16c90e53394b
  modified: 2026-09-11T09:00:13.868Z
---

Di sesi Claude Code ini, **heredoc Bash memakan satu level backslash**, bahkan dengan delimiter
ber-kutip (`<<'PYEOF'`) yang seharusnya literal. Efeknya diam-diam merusak JS yang disuntik ke
workflow n8n.

Contoh nyata (2026-09-10). Ditulis di heredoc:

```
new RegExp('\\b(\\d{1,2})\\s*' + BLN[bi] + '\\b')
```

Yang sampai ke file: `new RegExp('\b(\d{1,2})\s*' ...)`. Di JS, `'\b'` **di dalam string literal**
adalah karakter BACKSPACE (U+0008), bukan word-boundary — jadi polanya tidak pernah cocok, dan 3
karakter U+0008 ikut tertulis ke `jsCode`. Tree-sitter menerimanya tanpa keluhan.

Aturan:

1. **Tulis script patch sebagai file** (pakai tool Write), lalu `python nama_script.py`. Ini yang
   paling aman dan juga lolos dari masalah quoting heredoc yang pernah bikin exit code 2.
2. Kalau terpaksa heredoc, pakai **Python raw string** (`r"""..."""`) — satu level hilang di shell,
   raw string menahan sisanya. Ini yang membuat patch pertama (dengan `r"""`) benar sementara patch
   kedua (string biasa) rusak.
3. **Hindari `new RegExp(string)` di JS yang disuntik.** Pakai **regex literal** `/.../` — di sana
   satu backslash memang yang benar, jadi tidak ada level yang bisa salah hitung.
4. Sesudah patch, **scan karakter kontrol** (U+0000/07/08/0B/0C) di semua `jsCode`.

**Why:** kerusakan ini tidak memunculkan error di mana pun — sintaks valid, import n8n berhasil,
regex cuma tidak pernah cocok. Tanpa scan karakter kontrol, bug seperti ini lolos ke produksi dan
gejalanya baru muncul sebagai "fitur X kadang tidak jalan".

**How to apply:** bandingkan `repr()` potongan kode di file hasil patch dengan yang kamu maksud
tulis, sebelum menyatakan patch selesai. Satu backslash di `repr()` (`'\\b'` tercetak) berarti JS
melihat BACKSPACE; yang kamu mau untuk `new RegExp` adalah dua.

Terkait: [[laptop-tanpa-runtime-js]], [[n8n-json-gaya-byte]], [[store-python-appdata-redirect]]
