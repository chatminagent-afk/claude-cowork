# Deploy VIRA Personal v3.9: nama tidak dipakai menyapa

| | Berkas (folder `workflow/`) |
|---|---|
| Workflow | `2026-09-15-VIRA-Personal-Main-v3.9.json` |
| Prompt | `2026-09-15-system-prompt-VIRA-Personal-v3.9.md` |
| Patch / UAT | `_patch_2026-09-15.py` → `_uat_2026-09-15.py`, **402 lolos, 0 gagal** (`2026-09-15-hasil-uat-v3.9.log`) |

Berbasis v3.8 yang sudah live. Hanya 3 node yang berubah (AI Agent, Process All, Rakit Konteks). Sheet dan CONFIG tidak perlu diubah.

## Yang diperbaiki (insiden 15/09 14:11)
1. **Nama tidak pernah dipakai di balasan.** Aturan "pakai namanya" dihapus dari prompt, dan "kamu" diganti "kakak". Kalau model tetap menulis nama, kode menghapusnya sebelum terkirim ("Halo Aldi" → "Halo kak").
2. **"Dengan Aldi" → "Aldi".** Kata "dengan / sama / ini" di depan nama dibuang.
3. **Pertanyaan prospek dijawab dulu.** Kalau pesannya berisi pertanyaan, galian (bidang usaha dll.) ditunda ke balasan berikutnya. Jendela giliran dilebarkan satu: bidang usaha 2–5, masalah 2–7, jumlah chat 3–9.

## Langkah
1. Import v3.9, pasang lagi credential, **nonaktifkan v3.8**, aktifkan v3.9.
2. Di STATS, baris nomor uji (No WA `6281548899671`, baris 532): hapus barisnya supaya perkenalan bisa diuji ulang, atau minimal ganti `nama_lengkap` "Dengan Aldi" → "Aldi".
3. Ulang insiden dari nomor uji. VIRA harus:
   - menyapa **"kak"** tanpa nama
   - **menjawab** "bisa apa aja / sama kayak chatbot biasa?"
   - **tidak** menanyakan bidang usaha di balasan itu

   Cek STATS: `nama_lengkap = Aldi`.
4. Kirim satu pesan yang tidak bertanya (mis. "oh gitu oke"). Baru di situ VIRA menanyakan bidang usaha.

Kalau harus mundur: aktifkan lagi v3.8.

Catatan: `CONFIG.followup_templates` masih berbunyi "Halo kak {nama}". Sebelum Follow-up dinyalakan, hapus `{nama}` supaya konsisten dengan aturan ini.
