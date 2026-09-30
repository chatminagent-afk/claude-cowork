---
name: sparkline-intensitas-chat-pcr
description: Formula SPARKLINE untuk kolom G Intensitas Chat di sheet STATS PCR — harus pakai syntax Indonesian locale
metadata: 
  node_type: memory
  type: reference
  project: Persada Cisoka Residence
  date_discovered: 2026-07-24
  originSessionId: ea9f3dca-1b5e-4e94-99e7-bee5a30e11a1
  modified: 2026-07-24T07:31:51.627Z
---

## Formula SPARKLINE untuk Intensitas Chat

**Lokasi:** Sheet STATS, kolom G (Intensitas Chat), reference data dari kolom F (Counter)

**Formula yang benar** (Indonesian region setting):
```
=MAP(F2:F; LAMBDA(x; IF(x=""; ""; SPARKLINE(x; {"charttype"\"bar";"max"\MAX($F$2:$F)}))))
```

## Perbedaan syntax: Indonesian vs English locale

| Setting | Separator argument | Separator property | Contoh |
|---------|---|---|---|
| **English** | `,` (comma) | `;` (semicolon) | `=MAP(F2:F, LAMBDA(x, IF(...; {"charttype", "bar"; ...})))` |
| **Indonesian** | `;` (semicolon) | `\` (backslash) | `=MAP(F2:F; LAMBDA(x; IF(x=""; ""; SPARKLINE(x; {"charttype"\"bar"; ...}))))` |

## Cara cek/ubah regional setting

Google Sheets → `Tools` → `Spreadsheet settings` → "Calculation" atau "Locale" → pilih "Indonesian (Indonesia)" atau sesuai region.

## Notes

- Formula ini MAP + SPARKLINE berhasil tested 2026-07-24 di sheet STATS live PCR
- Cukup paste 1x di G2, akan auto-iterate untuk semua baris di kolom F
- Kolom F (Counter) harus berisi angka untuk SPARKLINE bekerja
- Jika F kosong, cell G akan kosong (IF condition)
