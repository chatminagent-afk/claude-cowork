# SPEC: Tambah Tanya Nama Lengkap + Domisili di Awal Chat (VIRA-PCR)

Status: RANCANGAN — menunggu approval Steven, belum ada file/node yang diubah.
Tanggal: 2026-07-19
Referensi: auto-reply telemarketer eksisting ("Nama Lengkap: / Domisili saat ini:"), pola chat telemarketer manusia (Aar/Aca) di folder `data dari telemarketer/`, dan pola greeting VIRA V4 The Scholars.

---

## 1. Rekomendasi Arsitektur

**Rekomendasi tegas: PERTAHANKAN pola prompt-injection (seperti sekarang / seperti V4). JANGAN bikin jalur hardcode terpisah yang bypass AI Agent.**

Alasan:

1. **Chat pertama user hampir selalu berisi pertanyaan** ("info harga dong", "tipe 36 ready?"). Hardcode murni akan mengirim sapaan + minta data tapi mengabaikan pertanyaan itu → user harus tanya ulang, terasa robotik, drop-off naik. Pola prompt-injection bisa: intro + jawab pertanyaan + minta nama/domisili dalam SATU pesan — persis yang dilakukan telemarketer manusia (pola Aar: sapa → tanya "dengan kak siapa dan domisili" → sambil bantu).
2. **Jalur hardcode terpisah akan menabrak 4 mekanisme yang sudah stabil**: debounce (`Wait3` + `Re-Read STATS Debounce`), penggabungan `MSG_BUFFER` (user sering kirim 2-3 bubble beruntun), greeting flag (`Update STATS - Greeting Flag`), dan single-message guarantee. Semua itu harus di-fork ulang → risiko regresi tinggi di bot yang sudah live.
3. **Infrastruktur persist-fact SUDAH ADA**: tag `[FACTS unit budget]` → `Process All` → `Update to STATS`. Nama/domisili tinggal ikut rel yang sama (tambah 2 atribut), bukan bikin pipeline baru.

Catatan: greeting saat ini **sudah** semi-hardcode (teks `INTRO` konstan diwajibkan persis via CRITICAL INSTRUCTION di `Cek_user_status`). Itu pola yang tepat dan cukup — tidak perlu dinaikkan jadi hardcode penuh (bypass AI). Cukup menambah instruksi minta-data ke pola yang sama.

**Keputusan Steven (2026-07-19): TANPA kolom counter `profile_asked`.** Permintaan data hanya ditumpangkan di pesan intro (saat `isNewUser` true), sehingga `greeting_sent` sekaligus menjadi penanda "sudah pernah diminta". Konsekuensi yang diterima: tidak ada re-ask otomatis kalau user tidak menjawab, dan user lama eksisting tidak di-backfill — nama masih bisa terkumpul natural saat user menjadwalkan survey (diatur di prompt `# PROFIL USER`).

---

## 2. Daftar Node yang Di-adjust (VIRA-PCR Main.json)

Aliran data: `Resolve User Row` (baca) → `Cek_user_status` (susun instruksi) → `AI Agent` → `Process All` (parse tag) → `Update to STATS` / `Write SURVEY` (tulis).

### 2.1. `Resolve User Row` (Code) — BACA kolom baru

Di dalam objek `return [{ json: { ... } }]`, tepat setelah blok `budget_range_ts`, sisipkan:

```js
    nama_lengkap: row ? String(row['nama_lengkap'] || '').trim() : '',
    nama_lengkap_ts: Number(row ? (row['nama_lengkap_ts'] || 0) : 0) || 0,
    domisili: row ? String(row['domisili'] || '').trim() : '',
    domisili_ts: Number(row ? (row['domisili_ts'] || 0) : 0) || 0,
```

### 2.2. `Cek_user_status` (Code) — state pengumpulan data di `[SYSTEM_DATA]`

**(a)** Setelah baris `const budgetRange = brFresh ? ... : '';`, tambah blok status profil (sumber baca: `debounceRow` primer, `resolve` fallback — konsisten pola unit/budget eksisting):

```js
// ── PROFIL USER (nama lengkap + domisili) ──
const namaLengkap = String(debounceRow['nama_lengkap'] || resolve.nama_lengkap || '').trim();
const domisili     = String(debounceRow['domisili']     || resolve.domisili     || '').trim();
const needName     = !namaLengkap;
const needDomicile = !domisili;
// diminta HANYA di pesan intro (user baru) — greeting_sent otomatis jadi penanda "sudah pernah diminta"
const askProfileNow = isNewUser && (needName || needDomicile);
const askProfileTarget = !askProfileNow ? 'NO'
  : (needName && needDomicile) ? 'nama+domisili'
  : (needName ? 'nama' : 'domisili');
```

Catatan: blok ini harus diletakkan SETELAH `isNewUser` dihitung (variabel eksisting di node ini).

**(b)** Konstanta `INTRO` TIDAK diubah teksnya (harus tetap sinkron dengan system prompt). Ganti blok template `aiSystemData` menjadi:

```js
const aiSystemData = `[SYSTEM_DATA]
USER_WA: ${resolvedKey}
IS_NEW_USER: ${isNewUser}
NAMA_LENGKAP: ${namaLengkap || 'UNKNOWN'}
DOMISILI: ${domisili || 'UNKNOWN'}
ASK_PROFILE: ${askProfileTarget}
UNIT_INTEREST: ${unitInterest || 'UNKNOWN'}
BUDGET_RANGE: ${budgetRange || 'UNKNOWN'}
TANGGAL_SEKARANG: ${tanggalSekarang} (${hariSekarang}) ${jamSekarang} WIB

CRITICAL INSTRUCTION:
${isNewUser
  ? `USER BARU. Baris pertama balasan WAJIB intro ini PERSIS (jangan diubah/diringkas): "${INTRO}" Setelah intro, di pesan yang sama langsung jawab pertanyaan user kalau ada. Kalau user hanya menyapa, cukup intro saja.`
  : 'User lama. JANGAN kirim intro/perkenalan lagi, lanjutkan percakapan secara natural.'}${
  askProfileNow
  ? `\nMINTA DATA: user ini belum melengkapi ${askProfileTarget === 'nama+domisili' ? 'nama lengkap dan domisili' : (askProfileTarget === 'nama' ? 'nama lengkap' : 'domisili')}. Di pesan yang SAMA, minta data itu sekali secara natural dan ramah (lihat # PROFIL USER). JANGAN memaksa, JANGAN menahan jawaban atas pertanyaan user, dan minta HANYA yang belum ada. Begitu user menyebutkannya, catat lewat tag [FACTS ...].`
  : ''}

[USER QUERY]
${userMessage}`;
```

**(c)** Pada objek `return`, tambah field hilir (setelah `budget_range_db`):

```js
    nama_lengkap_db: namaLengkap,
    domisili_db: domisili,
    ask_profile: askProfileTarget,
```

Catatan: `Preprocess - Context Detection` **tidak perlu diubah** — ia meneruskan seluruh blok `[SYSTEM_DATA]` apa adanya, jadi field baru otomatis sampai ke AI.

### 2.3. `Process All` (Code) — parse nama/domisili dari `[FACTS]`

Perluas `[FACTS]` yang sudah di-parse (jangan bikin tag baru — reuse jalur persist). Di blok parsing FACTS, setelah `factBudget = ...`:

```js
let factNama = '', factDomisili = '';
if (factsMatch && factsMatch[1]) {
  factNama     = (factsMatch[1].match(/nama\s*=\s*"([^"]*)"/i) || [])[1] || '';
  factDomisili = (factsMatch[1].match(/domisili\s*=\s*"([^"]*)"/i) || [])[1] || '';
}
```

Setelah blok `existingUnit`/`existingBudget`:

```js
let existingNama = '';     try { existingNama = String($('Cek_user_status').first().json.nama_lengkap_db || ''); } catch (e) {}
let existingDomisili = ''; try { existingDomisili = String($('Cek_user_status').first().json.domisili_db || ''); } catch (e) {}
// sanitasi ringan: buang kontrol char, rapikan spasi, batasi panjang. Sekali terisi jangan ditimpa kecuali AI kirim nilai baru.
const cleanProfile = s => String(s || '').replace(/[\u0000-\u001F\u007F]/g, '').replace(/\s+/g, ' ').trim().slice(0, 60);
const namaMerged     = cleanProfile(factNama)     || existingNama;
const domisiliMerged = cleanProfile(factDomisili) || existingDomisili;
const namaChanged     = namaMerged !== ''     && namaMerged !== existingNama;
const domisiliChanged = domisiliMerged !== '' && domisiliMerged !== existingDomisili;
```

Di objek `return` akhir, tambah (dekat `unit_interest_merged`):

```js
    nama_lengkap_merged: namaMerged,
    domisili_merged: domisiliMerged,
    nama_changed: namaChanged,
    domisili_changed: domisiliChanged,
```

Regex pembersih tag `/\[\s*FACTS\b[^\]]*\]/gi` di `cleanOutput` sudah menyapu atribut baru — tidak perlu diubah.

### 2.4. `Update to STATS` (Google Sheets, appendOrUpdate) — tulis kolom baru

Di `parameters.columns.value`, tambah 4 mapping (setelah `budget_range_ts`):

```
"nama_lengkap": "={{ $('Process All').first().json.nama_lengkap_merged || '' }}",
"nama_lengkap_ts": "={{ $('Process All').first().json.nama_changed ? Math.floor(Date.now()/1000) : ($('Resolve User Row').first().json.nama_lengkap_ts || '') }}",
"domisili": "={{ $('Process All').first().json.domisili_merged || '' }}",
"domisili_ts": "={{ $('Process All').first().json.domisili_changed ? Math.floor(Date.now()/1000) : ($('Resolve User Row').first().json.domisili_ts || '') }}"
```

Lalu di `parameters.columns.schema` tambah entri schema untuk tiap kolom baru (pola sama seperti `unit_interest`, `canBeUsedToMatch: true`, tanpa `removed`): `nama_lengkap`, `nama_lengkap_ts`, `domisili`, `domisili_ts`. **Tanpa entri schema, mapping value tidak dieksekusi node Sheets.**

### 2.5. `Write SURVEY` (Google Sheets, tab SURVEY)

Kolom `nama` sekarang: `={{ $('Chat Counter').first().json.user_name }}` (WA profile name). Ganti jadi:

```
"nama": "={{ $('Process All').first().json.nama_lengkap_merged || $('Chat Counter').first().json.user_name }}"
```

### 2.6. TIDAK berubah (konfirmasi eksplisit)

- `Update STATS - Greeting Flag` / `IF Update Greeting` / `Update Greeting` — tidak diubah; `greeting_sent` kini merangkap dua peran: penanda intro terkirim sekaligus penanda "permintaan nama/domisili sudah pernah disampaikan" (karena permintaan selalu nempel di pesan intro).
- Kolom `Nama` (WA pushname) di STATS & `Process Counter & Merge Data` — jangan timpa; `Nama` = pushname WA, `nama_lengkap` = hasil tanya. Dua kolom berbeda.
- `Preprocess - Context Detection`, `Detect Lead Source`, debounce, buffer, rate limiter — tidak tersentuh.

---

## 3. Perubahan System Prompt (node `AI Agent`, `options.systemMessage`)

⚠️ Sumber kebenaran system prompt = `parameters.options.systemMessage` di **Main.json**. File `workflow/ai_agent_node.json` adalah draft basi — jangan dipakai.

### 3.1. `# ALUR` — ubah langkah 3

> 3. USER BARU / MINTA DATA: kalau IS_NEW_USER true -> ikuti # INTRO USER BARU. Kalau ASK_PROFILE di [SYSTEM_DATA] bukan "NO" -> di pesan yang sama minta data profil sesuai # PROFIL USER (nama lengkap/domisili), tanpa menahan jawaban atas pertanyaan user.

### 3.2. `# INTRO USER BARU` — ganti seluruh section

```
# INTRO USER BARU
Kalau IS_NEW_USER: true -> baris PERTAMA balasan WAJIB intro ini (boleh sedikit variasi, jangan diterjemahkan):
"Haloo, terima kasih sudah menghubungi Persada Cisoka Residence yaa. Saya Vira, siap bantu info seputar unit, harga, KPR, sampai jadwal survey ke lokasi."
- Kalau user sudah bertanya di pesan pertamanya -> setelah intro, di pesan yang SAMA langsung jawab pertanyaannya.
- Kalau user cuma menyapa -> cukup intro + tawaran bantuan singkat.
- Kalau ASK_PROFILE bukan "NO" -> di pesan yang sama, minta data profil sesuai # PROFIL USER. Jangan menahan jawaban user demi data ini; boleh jawab dulu lalu minta datanya, atau sebaliknya, yang paling luwes.
- IS_NEW_USER: false -> JANGAN PERNAH ulangi intro ini.
```

### 3.3. Section BARU `# PROFIL USER` (setelah `# INTRO USER BARU`)

```
# PROFIL USER (nama lengkap + domisili)
Tim marketing perlu tahu nama lengkap dan kota/kecamatan domisili calon pembeli untuk follow-up dan proses berikutnya. Field NAMA_LENGKAP, DOMISILI, dan ASK_PROFILE ada di [SYSTEM_DATA].
- ASK_PROFILE = "nama+domisili" / "nama" / "domisili" -> minta HANYA yang disebut itu, di pesan intro ini. ASK_PROFILE = "NO" -> JANGAN memulai permintaan data baru; lanjut natural.
- Pengecualian saat ASK_PROFILE = "NO" (dua-duanya andalkan konteks percakapan, jangan berulang):
  1. Kalau di pesan terakhirnya user baru menyebut SEBAGIAN datanya (mis. nama saja), boleh tanyakan sisanya SEKALI secara ringan ("domisilinya di mana yaa Kak?").
  2. Saat user mau menjadwalkan survey dan NAMA_LENGKAP masih UNKNOWN -> minta nama lengkap dulu untuk pencatatan survey ("boleh saya catat surveynya atas nama siapa Kak?").
- Minta secara ramah dan mengalir seperti telemarketer, BUKAN seperti formulir. JANGAN tulis "Nama Lengkap: ___ / Domisili: ___".
  Contoh nada: "Oh iya, boleh sekalian saya catat, ini dengan Kak siapa dan domisilinya di mana yaa? 😊" atau "Sebelumnya, boleh tahu nama lengkap dan sekarang domisili di mana Kak?"
- Kalau user tidak menjawab atau menolak -> hormati, JANGAN ulangi permintaan di pesan-pesan berikutnya. JANGAN pernah memblokir atau menunda menjawab pertanyaan user hanya karena data belum diberikan.
- Begitu user menyebut namanya dan/atau domisilinya, catat di baris PALING AKHIR dengan tag [FACTS] (lihat # TAG), isi yang diketahui saja.
- Domisili yang dicatat cukup kota/kecamatan (mis. "Tangerang", "Cisoka", "Jakarta Barat"). Jawaban ambigu yang bukan nama tempat ("di rumah", "deket sini") -> JANGAN dicatat; klarifikasi ringan sekali ("maksudnya daerah mana yaa Kak?"). Kalau user menolak/mengabaikan, hormati dan lanjutkan membantu.
```

### 3.4. `# TAG` — perluas `[FACTS]`

```
[FACTS unit="<tipe>" budget="<kisaran>" nama="<nama lengkap>" domisili="<kota/kecamatan>"] -> WAJIB di baris PALING AKHIR setiap kali percakapan mengungkap salah satu dari: tipe unit yang diminati, budget user, nama lengkap user, atau domisili user. Isi HANYA atribut yang diketahui, kosongkan/hilangkan yang belum. Contoh: [FACTS nama="Budi Santoso" domisili="Tangerang"] atau [FACTS unit="Tipe 36/72" budget="500jt-600jt"]. Kalau belum ada info sama sekali, JANGAN pasang tag. Tag ini dibuang sistem, user tidak melihatnya, TIDAK menggantikan jawaban biasa.
```

### 3.5. `# LARANGAN` — hilangkan kontradiksi domisili

Ganti baris "Probing data pribadi yang tidak perlu (KTP, penghasilan detail, alamat) ..." menjadi:

> - Probing data pribadi sensitif yang belum perlu (nomor KTP, penghasilan detail, alamat lengkap/RT-RW) kecuali user sendiri mengarah ke proses KPR dan tim yang memintanya. (Nama lengkap dan domisili tingkat kota/kecamatan BOLEH diminta di awal sesuai # PROFIL USER — itu bukan data sensitif.)

---

## 4. Perubahan Google Sheet PCR_Database (manual oleh Steven di sheet asli)

xlsx lokal hanyalah snapshot; perubahan wajib di Google Sheet live (documentId `1dJWq7iq5PRGRguW6GRAgtclgvhSqppa-D6tSNrAo1PU`).

**Tab STATS — tambah 4 kolom baru DI PALING KANAN** (setelah `last_follow_up_ts`, mulai kolom `Z`). Node Sheets mencocokkan by header-name, jadi menaruh di ujung paling aman (tidak menggeser kolom lama):

| Kolom baru | Isi | Analog konvensi |
|---|---|---|
| `nama_lengkap` | nama hasil tanya (bukan pushname WA) | `unit_interest` |
| `nama_lengkap_ts` | epoch detik saat pertama dicatat | `unit_interest_ts` |
| `domisili` | kota/kecamatan | `unit_interest` |
| `domisili_ts` | epoch detik | `unit_interest_ts` |

(Kolom `profile_asked` DIHAPUS dari rancangan atas keputusan Steven — penanda "sudah pernah diminta" cukup `greeting_sent`.)

Header ditulis persis (case-sensitive) supaya mapping node cocok.

**Tab SURVEY** — tidak perlu kolom baru (kolom `nama` eksisting kini diisi nama lengkap, fallback pushname). Opsional: tambah kolom `domisili` di SURVEY, map dari `domisili_merged` — bukan blocker.

**Tab lain** (CONFIG, PRODUK, FAQ, LINKS, MSG_BUFFER, EVENTS, UNKNOWN): tidak kena.

---

## 5. Edge Cases

| # | Kasus | Perilaku diinginkan | Ditangani di |
|---|---|---|---|
| 1 | User jawab salah satu (nama saja / domisili saja) | Yang terisi disimpan; sisanya boleh ditanyakan SEKALI secara ringan berdasarkan konteks percakapan (bukan state sheet) | Code (`Process All` merge terpisah) + Prompt (`# PROFIL USER` pengecualian 1) |
| 2 | User menolak jawab ("gak usah", "nanti aja") | Hormati, tidak pernah diminta lagi — setelah reply pertama `greeting_sent='Y'` → `ASK_PROFILE=NO` di semua giliran berikutnya | Code (`askProfileNow = isNewUser && ...`) + Prompt |
| 3 | User langsung tanya harga tanpa jawab | Jawab pertanyaan normal; permintaan data ditumpangkan, tidak memblokir | Prompt (CRITICAL INSTRUCTION) |
| 4 | User lama (`greeting_sent='Y'`) belum pernah kasih data | TIDAK di-backfill otomatis (konsekuensi hapus `profile_asked`); nama tetap diminta natural saat user mau jadwal survey, domisili user lama mungkin tidak terkumpul — trade-off diterima | Prompt (`# PROFIL USER` pengecualian 2) |
| 5 | Nama mengandung emoji / karakter aneh | Kontrol char dibuang, spasi dirapikan, potong 60 char | Code (`cleanProfile`) |
| 6 | Domisili ambigu ("saya di rumah", "deket sini") | Jangan simpan junk; klarifikasi ringan sekali | Prompt (`# PROFIL USER`) |
| 7 | Nama di bubble 2, domisili di bubble 3 | Sudah aman — MSG_BUFFER digabung sebelum ke AI | Mekanisme eksisting |
| 8 | User koreksi nama ("eh salah, Budi Santoso") | `[FACTS nama]` baru menang → overwrite + ts diperbarui | Code (merge: nilai baru menang) |

---

## 6. Urutan Implementasi (aman untuk workflow live)

1. **Sheet dulu, kode belakangan.** Tambah 4 kolom di ujung kanan STATS (§4). Kolom kosong tidak mengganggu flow lama. Verifikasi ejaan header.
2. **`Resolve User Row`** (§2.1) — hanya menambah pembacaan; aman.
3. **`Cek_user_status`** (§2.2) — sampai di sini AI belum diminta apa-apa (ASK_PROFILE cuma data mentah). Aman.
4. **System prompt `AI Agent`** (§3) — mulai titik ini bot menanyakan nama/domisili.
5. **`Process All`** (§2.3) — parse `[FACTS nama/domisili]`.
6. **`Update to STATS`** (§2.4) — data mulai tersimpan.
7. **`Write SURVEY`** (§2.5).
8. **Uji end-to-end** (basis `2026-07-17-checklist-live-testing.md`): (a) user baru + tanya harga → intro+jawaban+minta data dalam 1 pesan; (b) jawab nama saja → AI tanya domisili sekali (dari konteks percakapan), lalu berhenti; (c) menolak → giliran berikutnya tidak diminta lagi (`ASK_PROFILE=NO`); (d) user lama tanpa data → TIDAK diminta, kecuali saat mau jadwal survey (nama); (e) jadwalkan survey → kolom `nama` SURVEY = nama lengkap.

**Sinkronisasi INTRO:** teks INTRO ada di 2 tempat (`Cek_user_status` const + `# INTRO USER BARU`) dan harus tetap identik. Spec ini tidak mengubah teks INTRO, jadi aman.

**Rollback:** kolom sheet hanya ditambah, semua field baru punya fallback string kosong → mengembalikan node ke versi lama tidak merusak data.

---

## Keputusan

- ✅ 2026-07-19 — `profile_asked` DIHAPUS dari rancangan (keputusan Steven): permintaan data hanya di pesan intro, `greeting_sent` jadi penanda "sudah pernah diminta"; follow-up parsial & momen survey ditangani prompt.
- ✅ 2026-07-19 — Nama+domisili di awal = SOFT / tidak mandatory (keputusan Steven): user cuek dan langsung tanya hal lain → jawab saja, jangan tanya ulang.
- ✅ 2026-07-19 — Saat user mau survey: minta nama lengkap DAN domisili yang masih UNKNOWN sebelum konfirmasi jadwal (perluasan dari "nama saja"). Kalau user menolak tapi tanggal+jam jelas → tetap pasang [SCHEDULE_SURVEY], jangan korbankan lead.
- ✅ 2026-07-19 — **PATCH V1.2 DIBUAT**: `workflow/2026-07-19-VIRA-PCR-main-v1.2.json` (copy dari production terbaru + patch 6 node: Resolve User Row, Cek_user_status, Process All, Update to STATS, Write SURVEY, AI Agent). File production asli tidak disentuh. Tervalidasi: JSON parse OK, hanya 6 node target berubah, bebas karakter kontrol liar.

## Menunggu Steven (untuk go-live V1.2)

1. Tambah 4 kolom di tab STATS Google Sheet LIVE (paling kanan): `nama_lengkap`, `nama_lengkap_ts`, `domisili`, `domisili_ts` — tanpa ini mapping tidak tereksekusi.
2. Import/replace workflow di n8n dengan `2026-07-19-VIRA-PCR-main-v1.2.json`.
3. Uji end-to-end sesuai §6 langkah 8.
4. Opsional (belum diputuskan): kolom `domisili` di tab SURVEY.
