# Memory Index

- [Status proyek Persada Cisoka](persada-cisoka-status.md) — klien Om Sulianto approve Paket Basic; kontak kunci, keputusan media/notifikasi, file kunci, gap data
- [Register perubahan tertunda](pending-changes-register.md) — setiap changes yang ditunda wajib dicatat ke "Pending Waiting Changes.md" lalu kabari Steven
- [Prompt VIRA minim hardcode](vira-prompt-minim-hardcode.md) — fakta bisnis hidup di sheet PRODUK/FAQ, prompt cukup aturan perilaku generik
- [SPARKLINE formula Intensitas Chat](sparkline-formula-intensitas-chat.md) — formula MAP/SPARKLINE untuk kolom G sheet STATS; harus pakai semicolon+backslash di Indonesian locale
- [Claude Token Monitor](claude-token-monitor.md) — tray app monitor token Claude Code real-time; lokasi, cara jalan, kenapa dedup & cache-adjusted gauge wajib
- [Store Python redirect %APPDATA%](store-python-appdata-redirect.md) — Python Store di laptop ini me-redirect tulisan AppData ke container MSIX; pakai path relatif home
- [Gaya byte JSON workflow n8n](n8n-json-gaya-byte.md) — generate/patch workflow n8n harus LF murni + key order + id/versionId, bukan cuma JSON valid; kalau tidak, import ditolak
- [Referensi node mati di n8n](n8n-referensi-node-mati.md) — duplikasi workflow menambah sufiks ke nama node tapi tidak ke `$('...')` di kode; gagal senyap kalau dibungkus try/catch
- [Laptop tanpa runtime JS](laptop-tanpa-runtime-js.md) — tidak ada node/deno/bun TAPI py_mini_racer (V8) ada; node Code n8n bisa dieksekusi sungguhan, plus jebakan harness
- [Sisip node memutus mapping $json](n8n-sisip-node-putus-mapping.md) — node baru di depan node Sheets bikin kolom `$json.*` tertimpa kosong tanpa error
- [STATS kolom berspasi](stats-kolom-berspasi.md) — 3 kolom pending_survey_* di STATS berakhir spasi; perbaiki sisi BACA, jangan ubah header
- [Heredoc makan backslash](heredoc-makan-backslash.md) — heredoc shell memakan 1 level backslash; tulis script patch sebagai file, hindari new RegExp(string)
- [Error node Code n8n dipotong](n8n-error-code-node-dipotong-titik-dua.md) — pesan throw dipotong di titik dua/baris baru (tergantung versi); penanda harus satu baris tanpa ':'
