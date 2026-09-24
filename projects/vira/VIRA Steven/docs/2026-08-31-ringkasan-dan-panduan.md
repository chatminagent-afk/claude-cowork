# Ringkasan & panduan — mulai dari sini

**Per 2026-08-31.** Dokumen ini pintu masuk. Yang lain dibuka kalau butuh detail.

---

## Kesimpulan

Berangkat dari satu pertanyaan — *apakah sheet VIRA sudah cukup untuk mengumpulkan informasi
buat bikin pitch deck?* — jawabannya waktu itu: **belum**, karena tiga jalur diam-diam membuang
data, dan dua angka paling penting untuk deck justru tidak pernah ditanyakan.

Sekarang: **jalur itu sudah tertutup, dan decknya bisa digenerate sendiri.**

| | Sebelum | Sekarang |
|---|---|---|
| Brief belum lengkap | dibuang **utuh** | tetap tersimpan, notifikasi saja yang ditahan |
| Kolom REQUESTS | 32 | 43 |
| Field yang diisi AI | 27 | 33 |
| Kutipan asli prospek | tidak pernah disimpan | tersimpan, dipakai di deck |
| Outcome (menang/kalah) | tidak ada | 3 kolom, tidak akan tertimpa workflow |
| Bikin deck | manual dari nol | `python buat_deck.py --wa 628xxx` → PDF 29 slide |
| Konsistensi antar deck | bergantung ingatan | struktur terkunci, terbukti byte-identik |

**Semua sudah lolos uji statis: workflow 64/64, generator deck 14/14.**
Yang **belum** teruji sama sekali: perilakunya saat benar-benar jalan — itu butuh nomor byU.

---

## 1 · Yang perlu kamu adjust

### Bisa dikerjakan sekarang, tidak menunggu byU

**Google Sheet**

- [ ] Tab REQUESTS → klik sel **AG1** (tepat di kanan `status_followup`), ketik 11 header ini berurut:
      `kota` · `jumlah_admin` · `sudah_pakai_chatbot` · `integrasi_dibutuhkan` · `data_tersedia` ·
      `kutipan_asli` · `sumber_prospek` · `brief_jumlah` · `deck_dikirim_ts` · `hasil` · `alasan_kalah`
      **Jangan import ulang tab REQUESTS** — cukup ketik headernya
- [ ] Buat tab kosong `_KAMUS_BRIEF` → import `sheet/2026-08-30-import/_KAMUS_BRIEF.csv` (Replace current sheet)
- [ ] Format kolom `no_wa` (REQUESTS) dan `No WA` (STATS) → **Plain text**
- [ ] Hapus baris uji 16–21 Agu di REQUESTS / STATS / EVENTS (format `ts`-nya lama, mengacaukan sortir)

**n8n**

- [ ] Import `workflow/2026-08-30-VIRA-Personal-Main.json`
- [ ] Settings → Error Workflow = `VIRA Personal — Error Notifier`
- [ ] Set kredensial Google Sheets di semua node
- [ ] **JANGAN aktifkan** sampai 4 langkah Sheet di atas selesai

> ⚠️ Urutannya mengikat. `Write REQUESTS` memetakan 8 dari 11 kolom baru itu — node Google Sheets
> akan **error** kalau headernya belum ada.

### Menunggu nomor byU

- [ ] Isi 5 nilai `ISI MANUAL` di CONFIG (4 kredensial Kirimi + `bot_wa_number`)
- [ ] Nonaktifkan Main lama → aktifkan Main baru. **Jangan dua-duanya aktif**
- [ ] Jalankan UAT **V1–V4** (detail di `2026-08-30-perbaikan-brief-deck.md`)

### Belum mendesak, tapi nyata

- [ ] **VIRA belum bisa mengirim file apa pun.** Tab LINKS cuma 2 baris (landing page + IG),
      padahal `media/` sudah punya deck PDF, company profile, dan harga-ringkas. Perlu diupload
      ke Drive lalu URL-nya ditempel ke LINKS
- [ ] **Belum ada jawaban FAQ untuk “kenapa kamu nanya omzet saya?”** — VIRA sekarang memang
      menanyakan itu (Tingkat 2B). Dari 48 baris FAQ, tidak satu pun menyentuhnya

---

## 2 · Yang butuh keputusanmu

| | Pertanyaan | Asumsiku sekarang |
|---|---|---|
| 1 | Nilai sah kolom `hasil` | `DEAL` / `KALAH` / `NO_RESPONSE` / `MASIH_JALAN` |
| 2 | Kosakata `sumber_prospek` | sekarang cuma ada `Organik`. Perlu daftar lengkap (IG / landing / referral / iklan?) |
| 3 | Harga add-on | **deck menyebut** IDR 999.000, **bot tetap tidak** (`"Diskusikan dengan Steven"`). Sengaja dipisah — deck itu dokumen yang sudah dipikirkan, chat itu langsung |
| 4 | Font deck | pakai Montserrat, jatuh ke Segoe UI. Kemungkinan bukan font asli deckmu — kalau tahu namanya, ganti satu baris di `template.html` |
| 5 | Prioritas berikutnya | pilih: FAQ objection · isi LINKS · naskah mockup per klien · auto-generate penuh |

Nomor 1–2 memblokir pemakaian kolom outcome. Nomor 3–4 kosmetik. Nomor 5 menentukan sesi berikutnya.

---

## 3 · Workflow kita

```
prospek chat → VIRA gali → brief masuk sheet → notif WA ke kamu
                                                      ↓
                        PDF siap kirim ← generate ← keputusanmu
```

| # | Langkah | Siapa |
|---|---|---|
| 1 | Prospek chat ke nomor VIRA | otomatis |
| 2 | VIRA menggali berjenjang — Tingkat 1 dikejar, 2 pelan-pelan, **2B hanya setelah setuju dibuatkan deck**, 3 tidak pernah ditanya | otomatis |
| 3 | `[DECK_REQUEST]` → digabung ke baris lama (`no_wa` kunci). Satu prospek = satu baris yang makin kaya | otomatis |
| 4 | Notif WA masuk **hanya kalau Tingkat 1 lengkap** | otomatis |
| 5 | Kamu baca baris **“Slide khusus siap: n/6”** lalu putuskan | **kamu** |
| 6 | Unduh ulang sheet → `python buat_deck.py --wa 628xxx` | kamu (1 perintah) |
| 7 | Review PDF → kalau perlu tulis `deck/naskah/<klien>.json` → jalankan ulang → kirim | kamu |

**Notifikasi WA-nya sekarang berisi ini:**

```
📋 [VIRA Personal] BRIEF DECK
Akademi Arsi — Edukasi software arsitek
Kelengkapan: 28/33
Slide khusus siap: 6/6  → DECK SIAP DIGENERATE
  ✓ Konteks bisnis   ✓ Pain Points   ✓ The Flow (mockup)
  ✓ #1 Time Freedom  ✓ #2 Zero Leaking Profit  ✓ #3 Scalability
  …
Generate deck:
python buat_deck.py --wa 628xxxxxxxxxx
```

**Cara membaca “Slide khusus siap”:** 23 dari 29 slide berdiri tanpa data klien sama sekali.
Enam sisanya butuh field tertentu — kalau kosong, slide itu **dibuang**, tidak pernah ditebak.

| Angka | Artinya |
|---|---|
| `6/6` | deck penuh, generate sekarang |
| `4–5/6` | deck 27 slide, tetap layak kirim — atau telepon dulu untuk melengkapi |
| `≤3/6` | jangan digenerate. Notifnya sekaligus daftar pertanyaan buat telepon |

**Kenapa langkah 6 bukan otomatis:** deck itu aset jualanmu. Deck lemah yang terkirim cepat lebih
merugikan daripada deck bagus yang telat sehari. Kalau nanti mau penuh otomatis, tinggal satu node
n8n di mesin yang menyala terus + syarat “hanya jalan kalau 6/6”.

---

## 4 · Perintah yang sering dipakai

Bikin deck dari sheet:
```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/deck" && python buat_deck.py --wa 628xxxxxxxxxx
```

Cek workflow n8n masih konsisten (64 pemeriksaan):
```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/workflow" && python _qa_2026-08-30.py
```

Cek generator deck masih deterministik (14 pemeriksaan):
```bash
cd "D:/Documents/Claude Cowork/VIRA/VIRA Steven/deck" && python uji_konsistensi.py
```

Setiap render deck menutup dengan `PERIKSA : 29 halaman, 1440x810 pt, semua teks wajib ada`.
**Kalau baris itu tidak muncul atau tertulis GAGAL — jangan dikirim**, ada yang terpotong.

---

## 5 · Buka dokumen yang mana

| Butuh apa | Buka |
|---|---|
| Langkah deploy patch brief-deck | `2026-08-30-panduan-deploy-brief-deck.md` |
| Alasan teknis tiap perubahan + checklist UAT V1–V4 | `2026-08-30-perbaikan-brief-deck.md` |
| Alur ujung-ke-ujung, lengkap | `2026-08-31-alur-brief-ke-pitchdeck.md` |
| Peta 29 slide, mana tetap / custom | `2026-08-30-peta-slide-deck-vira.md` |
| Cara pakai & ubah generator deck | `../deck/README.md` |
| Deploy VIRA Personal secara umum (kredensial, Kirimi, dashboard) | `2026-08-28-panduan-deploy-VIRA-Personal.md` |
| Arti tiap kolom REQUESTS | tab `_KAMUS_BRIEF` di sheet |

---

## 6 · Yang masih terasa template — jujur

**Balasan VIRA di mockup masih bahasa proses** (“aku butuh beberapa data singkat”), belum menyebut
hal spesifik bisnis mereka — karena menyebut jadwal atau harga berarti mengarang. Untuk klien yang
serius, tulis 4 gelembung yang benar-benar pas di `deck/naskah/<klien>.json` sekali; setelah itu
tersimpan dan render berikutnya tetap identik.

**Pain Points terkunci 1 slide** (maksimal 6 poin), belum bisa pecah otomatis ke 2 slide seperti
deck Scholars.

**`nilai_transaksi` dan `prospek_per_bulan` tidak dipakai di deck** — sesuai keputusanmu, keduanya
hanya dikirim ke HP-mu lewat notif.
