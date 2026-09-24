# The Scholars — checklist migrasi ke Fonnte

## Jawaban singkat atas asumsimu

**Tidak.** Bukan hanya `VIRA TS` yang menyentuh API WhatsApp. Ada **3**:

| Workflow | Node pemanggil WA |
|---|---|
| VIRA TS | 5 (1 Code + 4 HTTP) |
| VIRA TS Error Notifier | 1 — `Notify Admin Error` |
| STATS Cleanup v3 | 1 — `Notify Steven` |

Yang **tidak** menyentuh WA dan tidak perlu diapa-apakan: Topic Harvester (WF-A), Monthly Rollup (WF-B), MSG_BUFFER Cleanup.

Kalau hanya `VIRA TS` yang dimigrasi, dua workflow di atas tetap memanggil Kirimi — dan karena IP n8n diblokir, notifikasi error TS akan gagal diam-diam. Justru notifier-nya yang paling tidak boleh mati.

---

## File di folder ini

| File | Isi |
|---|---|
| `2026-08-31-VIRA-TS-Fonnte-v2.json` | 57 node. Pengganti `VIRA TS`. |
| `2026-08-31-VIRA-TS-Error-Notifier-Fonnte.json` | 7 node. |
| `2026-08-31-TS-STATS-Cleanup-v3-Fonnte.json` | 8 node. |

`v2` berbeda dari versi yang kukirim lebih dulu: token pindah ke n8n Credential (kecuali 1 Code node), dan `countryCode` dibuang.

## Checklist

**1. Langganan & device**
- [ ] Upgrade paket Fonnte (minimal yang menghilangkan watermark) — wajib sebelum menyentuh nomor klien.
- [ ] Siapkan device Fonnte untuk nomor TS, scan QR, pastikan status `connect`.
- [ ] Salin token device.

**2. Credential**
- [ ] n8n → Credentials → Generic → **Header Auth**. Name `Authorization`, Value = token, **tanpa `Bearer`**.
- [ ] Beri nama persis: **`Fonnte - The Scholars`**.

**3. Import**
- [ ] Import ketiga file. Jangan diaktifkan dulu.
- [ ] Di tiap node HTTP yang credential-nya merah, pilih `Fonnte - The Scholars`.
- [ ] Buka node **`Send WA + Verify (Fonnte)`** di `VIRA TS Fonnte v2` → ganti `const TOKEN = 'txUT5...'` dengan token device TS. Ini satu-satunya token literal yang tersisa; Code node n8n tidak bisa membaca credential.

**4. Nomor**
- [x] `IF (Whitelist)` sudah berisi nomormu `6285171701168` (ditambahkan 2026-09-01). Isi lengkap: `6285155202354`, `6281510624599`, `6596110395`, `6589200455`, `628176480658`, `6285171701168`.
- [x] `Notify Admin Unknown` dan `Notify Talk to Sam` diarahkan ke `6285171701168` untuk masa pengujian. **Ini penting**: nilai aslinya `6596110395` — kalau dibiarkan, uji coba "UNKNOWN" dan "mau ngomong sama Sam" akan mengirim notifikasi tes ke Sam sungguhan.
- [ ] **Sebelum produksi**, kembalikan `target` kedua node itu ke **`6596110395`** (Sam). Dua node, satu baris masing-masing; sudah ada `notes` pengingat di node-nya.
- [ ] Jangan arahkan credential `Fonnte - The Scholars` ke device `6285155202354`. Nomor itu jadi target notifikasi di `VIRA TS Error Notifier` dan `STATS Cleanup v3` — kalau ia juga jadi pengirim, notifikasi jadi kirim-ke-diri-sendiri.

**5. Webhook**
- [ ] Dashboard Fonnte → device TS → webhook URL = `https://<host-n8n>/webhook/wa-inbound-fonnte`.
- [ ] Selama workflow belum aktif, hanya URL `/webhook-test/` yang jalan.

**6. Uji sebelum ganti**
- [ ] Aktifkan `VIRA TS Fonnte`, kirim WA dari nomor whitelist. Harapan: balasan masuk, execution hijau.
- [ ] Uji notifier: matikan sementara sebuah node agar error → cek WA notifikasi masuk.
- [ ] `STATS Cleanup v3` jalankan manual (aslinya `active: false`) → cek laporan masuk.

**7. Pindah**
- [ ] Nonaktifkan `VIRA TS` (Kirimi) dan `VIRA TS Error Notifier` lama.
- [ ] Pastikan `settings → Error Workflow` di workflow utama menunjuk notifier **versi Fonnte**, bukan yang lama.

## Rollback

Aktifkan kembali workflow Kirimi lama, kembalikan webhook Fonnte ke kosong. Tidak ada data yang berubah — Google Sheets, STATS, MSG_BUFFER, credential Anthropic dan Sheets tidak tersentuh sama sekali.

## Catatan

- Watermark "sent via fonnte" bukan dari workflow. Disuntikkan Fonnte di sisi server pada paket Free, tidak bisa dimatikan lewat API.
- `countryCode` dibuang. Nomor dari webhook selalu format internasional lengkap, dan memaksa `62` berisiko merusak nomor Singapura — dan whitelist TS berisi dua nomor +65.
