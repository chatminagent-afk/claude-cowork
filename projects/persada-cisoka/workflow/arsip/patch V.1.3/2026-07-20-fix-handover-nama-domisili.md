# Fix bug handover: nama salah + domisili hilang

Tanggal: 2026-07-20
Gejala: handover 20 Juli menulis `PROFIL KLIEN: Steven Leroy` padahal user memperkenalkan diri sebagai **Hera**, dan domisili "Bukit Gading Cisoka" tidak muncul sama sekali.

---

## Akar masalah

Sheet STATS punya **dua kolom nama yang berbeda**:

| Kolom | Diisi oleh | Isinya |
|---|---|---|
| `Nama` (idx 3) | `Chat Counter` → `user_name` | **push name WhatsApp** — nama akun pengirim |
| `nama_lengkap` (idx 25) | `Process All` → tag `[FACTS nama="..."]` | **nama yang user sebut sendiri** |

`Collect Handover Context` baris 12 membaca kolom yang salah:

```js
nama: statsRow['Nama'] || $('Chat Counter').first().json.user_name || '',
```

`statsRow['Nama']` hampir selalu terisi (push name WA jarang kosong), jadi fallback-nya tidak pernah tercapai — nama hasil `[FACTS]` tidak pernah dipakai.

`domisili` tidak diambil sama sekali, padahal sudah tersimpan di `statsRow['domisili']` dan tersedia sebagai `pa.domisili_merged`.

**LLM `Summarize Handover` tidak bersalah.** Node itu menerima `handover_profil.nama` dan menuliskannya apa adanya — persis yang seharusnya dilakukan. Datanya yang salah sejak hulu.

### Inkonsistensi yang menjelaskan kenapa ini lolos

Di file yang sama, `unit_interest` dan `budget_range` sudah memakai pola prioritas yang benar:

```js
unit_interest: pa.unit_interest_merged || statsRow['unit_interest'] || '',
budget_range:  pa.budget_range_merged  || statsRow['budget_range']  || '',
```

Pola `pa.<x>_merged || statsRow[<x>]` itu benar. Fitur nama+domisili ditambahkan belakangan (spec `2026-07-19-spec-nama-domisili-greeting`) dan polanya tidak ikut diterapkan ke node handover.

---

## Fix 1 — `Collect Handover Context` (WAJIB)

Ganti blok `const profil = {...}` dengan:

```js
const profil = {
  // PRIORITAS: [FACTS] turn ini > nama_lengkap tersimpan > push name WA.
  // JANGAN pakai statsRow['Nama'] duluan — itu nama akun WhatsApp, bukan nama
  // yang user sebutkan. (Bug 2026-07-20: user bilang "Hera", handover kirim
  // "Steven Leroy" karena kolom 'Nama' selalu terisi push name.)
  nama: pa.nama_lengkap_merged || statsRow['nama_lengkap'] || statsRow['Nama'] || $('Chat Counter').first().json.user_name || '',
  // Simpan push name terpisah: kalau beda dengan nama asli, itu info berguna
  // untuk tim lapangan (mis. yang chat istri, akun WA atas nama suami).
  nama_akun_wa: statsRow['Nama'] || $('Chat Counter').first().json.user_name || '',
  domisili: pa.domisili_merged || statsRow['domisili'] || '',
  no_wa: key,
  pesan_pertama: statsRow['Pesan Pertama'] || '',
  unit_interest: pa.unit_interest_merged || statsRow['unit_interest'] || '',
  budget_range: pa.budget_range_merged || statsRow['budget_range'] || '',
  survey: [sd.tanggal, sd.jam, 'SCHEDULED'].filter(Boolean).join(' '),
  lead_source: $('Detect Lead Source').first().json.lead_source_final || statsRow['lead_source'] || '',
  jumlah_chat: statsRow['Counter'] || '',
};
```

Sisa file tidak berubah.

---

## Fix 2 — prompt `Summarize Handover` (WAJIB, kalau tidak domisili tetap tidak muncul)

Di bagian `DATA PROFIL:`, ganti baris `Nama:` dan tambahkan dua baris:

```
Nama: {{ $json.handover_profil.nama }}
Nama akun WA: {{ $json.handover_profil.nama_akun_wa }}
Domisili: {{ $json.handover_profil.domisili }}
No WA: {{ $json.handover_profil.no_wa }}
```

Lalu di blok format output, ganti baris `PROFIL KLIEN` jadi:

```
PROFIL KLIEN: <nama, domisili, no WA, sumber>
```

Dan tambahkan satu instruksi di paragraf pembuka:

> Kalau "Nama akun WA" berbeda dari "Nama", pakai "Nama" dan sebutkan akun WA-nya dalam kurung. Kalau sama, sebut sekali saja.

---

## Fix 3 — fallback deterministik di `Format Handover Message` (opsional tapi murah)

Fallback dipakai kalau LLM gagal. Sekarang ikut salah karena mewarisi `p.nama` yang sama — setelah Fix 1 otomatis benar, tinggal tambahkan domisili:

```js
  summary = `PROFIL KLIEN: ${p.nama || '-'}${p.domisili ? ', ' + p.domisili : ''}, ${p.no_wa || '-'}, sumber ${p.lead_source || 'belum diketahui'}
TIPE UNIT DIMINATI: ${p.unit_interest || 'belum diketahui'}
BUDGET/KPR: ${p.budget_range || 'belum dibahas'}
STATUS SURVEY: ${p.survey || 'belum dijadwalkan'}`;
```

---

## Cara verifikasi

Chat dari nomor tes dengan push name WhatsApp yang **berbeda** dari nama yang diketik. Sebut nama + domisili, jadwalkan survey, lalu cek pesan yang masuk ke `field_team_phone`:

- `PROFIL KLIEN:` harus memakai nama yang **diketik**, bukan push name
- Domisili harus muncul
- Cek juga kolom `nama_lengkap` dan `domisili` di sheet STATS memang terisi — kalau kosong, masalahnya bukan di handover tapi di parsing `[FACTS]` di `Process All`

---

## Dua temuan lain (belum diperbaiki, prioritas lebih rendah)

**1. Transkrip handover hanya berisi pesan user.**

```js
transcript = buf.map(r => `User: ${r.message}`).join('\n');
```

MSG_BUFFER memang hanya menyimpan pesan masuk, jadi balasan Vira tidak pernah masuk transkrip. Akibatnya baris `SUDAH DILAKUKAN:` adalah **inferensi LLM dari pesan user saja**, bukan fakta. Di tes 20 Juli hasilnya kebetulan benar ("Brosur unit telah dikirim") karena bisa disimpulkan dari alur pertanyaan user — tapi ini akan salah suatu saat, dan tim lapangan tidak punya cara tahu.

Perbaikan butuh menyimpan balasan Vira (mis. tambah kolom `role` di MSG_BUFFER, atau tarik dari Simple Memory). Bukan pekerjaan sepele — sebaiknya dijadwalkan terpisah.

**2. `Read MSG_BUFFER` di handover tidak difilter jendela waktu.**

`Cek_user_status` memfilter ketat (`ts > doneTs && ts <= myTs && umur < 30 menit`). `Collect Handover Context` hanya memfilter `no_wa`, jadi kalau user pernah chat beberapa jam sebelumnya dan cleanup harian 03:00 belum jalan, transkrip bisa membawa sisa sesi lama dan membuat ringkasan mencampur dua percakapan.

Perbaikan cepat kalau mau: tambahkan filter umur di baris `.filter(...)`, misalnya
`&& (Date.now() - Number(r.ts)) < 6 * 60 * 60 * 1000`.
