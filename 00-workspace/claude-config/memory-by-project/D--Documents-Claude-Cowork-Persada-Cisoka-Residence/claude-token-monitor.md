---
name: claude-token-monitor
description: "Tray app Windows buatan sendiri untuk monitor pemakaian token Claude Code real-time — lokasi, cara jalan, dan dua keputusan desain non-obvious"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3dbf5139-5c87-4392-877a-9d112e42f08f
  modified: 2026-07-31T04:46:18.348Z
---

Tray indicator Windows untuk pemakaian token + biaya Claude Code secara real-time. Dibuat 2026-07-31.

- **Lokasi:** `D:\Documents\Claude Cowork\claude-token-monitor\` (sengaja di root Claude Cowork, bukan di dalam folder klien)
- **Jalan:** double-click `Claude Token Monitor.vbs`, atau `python -m claude_token_monitor` (`--report`, `--calibrate`, `--window` untuk mode headless)
- **Config:** `C:\Users\Steven\.claude-token-monitor\config.json` — lihat [[store-python-appdata-redirect]] kenapa bukan `%APPDATA%`
- **Sumber data:** transkrip JSONL yang sudah ditulis Claude Code di `~/.claude/projects` — tanpa API key, tanpa koneksi keluar
- **Tampilan:** ring 5 jam + bar 7 hari, 4 kartu ringkasan, chart aktivitas 24 jam, tabel breakdown. Tema light/dark ikut Windows (laptop Steven set ke dark)

**Dua keputusan desain yang tidak obvious:**

1. **Dedup wajib.** Session yang di-resume/fork menulis ulang turn lama ke file baru — di data Steven ada **lebih banyak baris duplikat (4.755) daripada yang unik (3.761)**. Tanpa dedup pakai key `message.id` + `requestId`, total membengkak ~2x.

2. **Gauge pakai "cache-adjusted tokens", bukan token mentah.** ~96% token yang tersentuh adalah cache read, yang ditagih 0,1x. Kalau gauge pakai total mentah, yang terukur sebenarnya cache-hit rate, bukan konsumsi.

3. **Chrome digambar pakai Pillow, bukan Tk canvas.** Canvas Tk tidak punya antialiasing — arc dan sudut membulat kelihatan jagged. Semua elemen dekoratif di-render PIL pada 4x lalu di-downsample LANCZOS, teks tetap digambar Tk. Ada di `graphics.py`.

**Limit bukan angka resmi — tapi bisa disamakan dengan panel Claude.** Claude Code tidak menyimpan rate limit akun di disk. Cara paling akurat: baca persentase di Claude > Settings > Usage, lalu `--sync-limit <pct> --apply` untuk back-solve penyebutnya.

⚠️ Persentase dan angka pemakaian **harus dari momen yang sama**. Pemakaian naik terus saat kerja, jadi memasangkan hitungan baru dengan persentase 20 menit lalu bikin limit terlalu besar. Pakai `--used <angka>` untuk memasangkan dengan pembacaan lama (mis. dari screenshot).

Terverifikasi 2026-07-31: window rolling 5 jam app **cocok** dengan session Claude (mulai 09:54:38, reset sama-sama ~3h10m). Yang beda cuma penyebutnya — heuristik peak x1.35 meleset ~5% ketinggian (8.920.840 vs nilai sebenarnya **8.467.242** cache-adjusted tokens dari pembacaan 88% Claude). Plan Steven: **Pro**.

Catatan: sinkronisasi ini mengasumsikan metrik weighted app proporsional dengan akuntansi internal Claude — satu titik data tidak membuktikan itu, jadi re-sync sesekali.

**Why:** angka persen di gauge hanya bermakna kalau penyebutnya diturunkan dari data nyata, bukan ditebak.
