# Deploy VIRA Personal v3.8: kolom STATS terisi + tanya nama

> **KEDALUWARSA 2026-09-15:** diganti `2026-09-15-panduan-deploy-v3.9.md` (nama tidak dipakai menyapa, jendela galian berubah).

| | Berkas (folder `workflow/`) |
|---|---|
| Workflow | `2026-09-14-VIRA-Personal-Main-v3.8.json` |
| Prompt | `2026-09-14-system-prompt-VIRA-Personal-v3.8.md` |
| Patch / UAT | `_patch_2026-09-14.py` → `_uat_2026-09-14.py`, **371 lolos, 0 gagal** (`2026-09-14-hasil-uat-v3.8.log`) |

**Tidak ada kolom baru.** Sheet dan CONFIG tidak perlu diubah. 82 dari 89 node identik dengan v3.6.

---

## 1. Sebelum import
Workflow Main tidak bisa kubaca dari n8n (`Available in MCP` mati). Karena itu:
- **Download** workflow Main yang live sekarang sebagai cadangan.
- Kalau sesudah 7 Sep kamu pernah mengedit langsung di n8n, **kabari aku dulu**. Import v3.8 akan menimpa editan itu.

## 2. Import
1. Import v3.8, lalu pasang lagi credential DeepSeek dan Google service account.
2. **Nonaktifkan v3.6 dulu**, baru aktifkan v3.8 (path webhook sama, `wa-inbound-steven`).

## 3. UAT manual (nomor baru)
1. Kirim `halo` → perkenalan seperti biasa + "namanya siapa kak?".
2. Jawab `Budi` → VIRA memanggil "kak Budi". Cek STATS: `nama_lengkap = Budi`.
3. Ngobrol biasa → satu pertanyaan per balasan: bidang usaha → masalah → jumlah chat per hari. Tiap jawaban muncul di STATS.
4. Abaikan satu pertanyaan → balasan berikutnya **tidak** mengulangnya.
5. Terima tawaran deck + sebut nama usaha → `nama_bisnis` terisi, REQUESTS dapat baris, notif ke Steven berbaris `WA: 62xxx · Budi`.
6. Sepanjang uji, VIRA **tidak pernah** menanyakan anggaran atau Basic/Premium.

## 4. Kalau harus mundur
Aktifkan lagi v3.6. Tidak ada yang perlu dikembalikan di sheet.

---

## Kapan tiap kolom STATS terisi

| Kolom | Diisi oleh | Kondisi |
|---|---|---|
| nama_lengkap | VIRA bertanya | **Sekali**, di pesan perkenalan |
| industri | VIRA bertanya | Giliran 2–4, kalau masih kosong |
| masalah_utama | VIRA bertanya | Giliran 2–6, sesudah bidang usaha ada (atau giliran 5+) |
| volume_chat | VIRA bertanya | Giliran 3–8, sesudah masalah ada |
| nama_bisnis | VIRA bertanya | Di kalimat tawaran deck (aturan lama) |
| budget_range, minat_paket | Dicatat saja | Hanya kalau prospek menyebut sendiri (keputusanmu) |
| bahasa | Kode | Dideteksi dari setiap pesan prospek |
| brief_terisi | Kode | Saat brief deck terbentuk |
| kolom `_ts` | Kode | Ikut terisi saat kolom faktanya berubah |
| No WA … last_bot_reply_ts | Kode | Setiap giliran (sudah jalan) |
| follow_up_count, last_follow_up_ts | Workflow Follow-up | Kosong sampai `followup_enabled=true` |
| Tanggal/Jam Chat Terakhir | Kode | Terisi, tapi hanya untuk kamu baca (tidak dibaca workflow) |

Pertanyaan yang tidak dijawab tidak diulang di balasan tepat sesudahnya. Di luar jendela gilirannya, VIRA berhenti bertanya.
Kalau AI lupa menulis tag `[FACTS]`, jawaban prospek atas pertanyaan VIRA tetap disimpan langsung oleh kode. Isi blok brief deck juga ikut mengisi STATS.

Di luar cakupan: workflow Follow-up mengisi `{nama}` dari nama akun WA. Perbaiki sebelum `followup_enabled` dinyalakan.
