# Deploy VIRA Personal v3.10: nama usaha di perkenalan, balasan lebih ringkas

| | Berkas (folder `workflow/`) |
|---|---|
| Workflow | `2026-09-18-VIRA-Personal-Main-v3.10.json` |
| Prompt | `2026-09-18-system-prompt-VIRA-Personal-v3.10.md` |
| Patch / UAT | `_patch_2026-09-18.py` → `_uat_2026-09-18.py`, **491 lolos, 0 gagal** (`2026-09-18-hasil-uat-v3.10.log`) |

Berbasis export live 16/09 (`VIRA Personal — Main.json`, = v3.9). Hanya 3 node yang berubah (AI Agent, Process All, Rakit Konteks); 86 node lain identik byte per byte. Sheet dan CONFIG tidak perlu diubah.

## Yang diperbaiki (uji 17/09 "Nadia", katering)
1. **Nama usaha ditanya di pesan pertama**, bersama nama orangnya, dalam satu kalimat: "btw boleh tau nama kakak siapa, dan nama usahanya apa?". Pesan pertama tidak lagi menanyakan bidang usaha atau alasan tertarik.
2. **Urutan galian baru:**
   - pesan 1: nama dan nama usaha
   - pesan 2: bidang usaha sambil minta cerita singkat
   - pesan 3: masalah
   - pesan 4: jumlah chat
   - setelah itu: tawaran deck

   Kalau nama usaha belum dijawab di pesan 1, pesan 2 menanyakannya ulang **sekali**, dan bidang usaha mundur ke pesan 3. Kalimat tawaran deck tetap jadi cadangan terakhir.
3. **Jawaban gabungan tersimpan otomatis walau model lupa `[FACTS]`**, misalnya "Rina, Kopi Senja", "aku Rina dari Kopi Senja", atau jawaban dua baris. Jenis usaha seperti "katering" masuk ke `industri`, bukan dianggap nama usaha.
4. **"Salam kenal Nadia" tidak lolos lagi.** Nama yang disebut prospek tetap dihapus sesudah sapaan, walaupun belum sempat tersimpan.
5. **Balasan lebih ringkas.** Target 2 kalimat, sekitar 20–35 kata, dengan batas keras 3 kalimat. Ini masih di atas VIRA TS, yang defaultnya 1 kalimat. VIRA dilarang membuka dengan merangkum atau mengulang jawaban prospek ("Jadi alurnya ada dua...", "Berarti...", "Paham, berarti..."). Temperature tetap 0.7.

## Langkah
1. Import v3.10, pasang lagi credential, **nonaktifkan v3.9**, lalu aktifkan v3.10.
2. Di STATS, **hapus baris nomor uji** (No WA `6285171701168`, sekarang baris 3) supaya perkenalan bisa diuji ulang. Kalau mau data briefnya bersih, hapus juga baris nomor itu di REQUESTS.
3. Ulang uji 17/09 dari nomor uji:
   - Kirim "Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku." VIRA harus membalas dengan perkenalan dan **satu** kalimat yang menanyakan nama dan nama usaha. Tidak boleh ada pertanyaan bidang usaha.
   - Jawab "Nadia kak, bisnis aku katering, chat suka numpuk pas malem". VIRA harus menyapa "kak" **tanpa nama** dan menanyakan ulang nama usaha. Cek STATS: `nama_lengkap = Nadia`, `industri = katering`.
   - Jawab "Dapur Nadia". Cek `STATS.nama_bisnis = Dapur Nadia`, dan pastikan VIRA tidak menanyakannya lagi.
   - Lanjutkan sampai tawaran deck. Nama usaha harus sudah terisi di REQUESTS **sebelum** tawaran, dan deck tidak lagi bernama `tanpa-nama.pdf`.
4. Uji kedua (baris STATS dihapus lagi): jawab perkenalan dengan "Rina, Kopi Senja". VIRA **tidak** boleh menanyakan nama usaha lagi.
5. Nilai panjang balasan dengan membandingkannya ke transkrip 17/09. Sebagian besar balasan galian harus 2 kalimat, dan tidak ada yang membuka dengan mengulang jawabanmu.

Kalau harus mundur: aktifkan lagi v3.9 (workflow lama yang sekarang live).

## Catatan
- Panjang balasan **tidak bisa diuji otomatis**, karena UAT hanya menjalankan kode, bukan model DeepSeek. Hasilnya baru terlihat di langkah 5. Kalau masih bertele-tele, tuasnya tetap di prompt (bagian GAYA), bukan temperature atau maxTokens.
- Kalau prospek menjawab nama dan nama usaha sekaligus di pesan 2, baris tanya ulang tetap muncul. Ini karena `Rakit Konteks` jalan sebelum jawabannya tersimpan. Baris itu sudah menyuruh model untuk tidak bertanya lagi kalau nama usahanya sudah disebut, dan memastikan ini yang jadi tujuan uji di langkah 4.
- Yang belum dikerjakan:
  - skill `deck-request` belum menahan generate kalau `nama_bisnis` kosong
  - jam `*_ts` di STATS sekitar 15 menit lebih lambat dari jam WA, dan belum ditelusuri
