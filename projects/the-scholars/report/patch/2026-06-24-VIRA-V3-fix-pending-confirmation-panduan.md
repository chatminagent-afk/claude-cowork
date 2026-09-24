# Panduan Fix VIRA: Konfirmasi Tertunda (Pending Confirmation) — Deterministik

**Tanggal:** 2026-06-24
**Versi dasar:** `VIRA_V3 23 jun live.json`
**Tujuan:** VIRA menindaklanjuti jawaban afirmatif pendek ("Baik kak", "Yaa", "boleh") atas tawarannya sendiri ("boleh saya kirimkan formnya?" / "mau saya sambungkan ke Sam?") secara **deterministik** — tidak lagi bergantung tebakan LLM.

---

## 0. Latar belakang (kenapa ini terjadi)

Dari 2 eksekusi yang dianalisis (kontak `Irir_KafhayaCollection`, `lid 97805129535709`):

| Pesan user | Output AI Agent | Masalah |
|---|---|---|
| `Baik kak 😊` (jawab "boleh saya kirimkan formnya?") | `[UNKNOWN] Untuk detail harga Seniors saya belum ada infonya...` + tawar Sam | Form tidak dikirim, malah `[UNKNOWN]` |
| `Yaa` (jawab "mau saya sambungkan ke Sam?") | `Oke, ada yang bisa saya bantu lagi? 😊` | `[TALK_TO_SAM]` tidak terpasang, Notify Sam tidak jalan |

**Akar masalah (BUKAN LID/memory — `from` kedua pesan konsisten `6289519321948`, memory jalan):**

1. **Retrieval gated per-pesan.** `FAQ Retrieve` hanya membangun blok HARGA kalau pesan **saat ini** mengandung keyword harga/daftar. "Baik kak" tak punya keyword → harga Seniors (Rp 4.000.000, ada di sheet `HARGA` & `FAQ`) tidak diinjeksi → aturan keras system prompt memaksa `[UNKNOWN]`.
2. **Tidak ada state "tawaran tertunda".** Saat VIRA menawarkan sesuatu, tidak ada yang mencatatnya. Jawaban "ya" di pesan berikut 100% bergantung tebakan LLM — dan gagal di dua kasus.
3. `Preprocess` cuma **menyarankan** `[TALK_TO_SAM]` lewat teks (non-deterministik); AI bebas mengabaikan.

**Prinsip solusi:** simpan "tawaran terakhir VIRA" ke STATS (key `lid`, konsisten dengan migrasi LID). Saat user membalas afirmatif → **paksa** aksi yang sesuai di kode (`Process All`), bukan menunggu AI memasang tag. Satu kolom STATS, edit 3 code node, +1 node tulis. Deterministik = gampang di-QA.

> ⚠️ **Pre-check (flag terpisah):** node `FAQ Retrieve` mengambil harga via `val(r,'Harga')` dari tab **PROGRAM**, padahal di database tab PROGRAM tidak punya kolom `Harga` (harga ada di tab `HARGA` terpisah). Pastikan tab PROGRAM di Google Sheet live memang punya kolom `Harga`; kalau tidak, harga hanya bisa datang dari FAQ. Ini di luar scope fix ini tapi memperparah `[UNKNOWN]` — sebaiknya dicek.

---

## FASE 0 — Backup (jangan dilewat)

- [ ] n8n → workflow VIRA → menu (•••) → **Download** JSON (cadangan).
- [ ] Google Sheets → `The_Scholars_Database` → **File → Make a copy**.
- [ ] Kerjakan saat sepi chat. Edit SEMUA node dulu, **Save sekali** di akhir.

---

## FASE 1 — Tambah kolom `pending_offer` di STATS

- [ ] Buka sheet **STATS**. Tambah 1 header kolom baru `pending_offer` di kolom kosong paling kanan (setelah `pending_msg`).
- [ ] Biarkan isinya kosong — akan terisi otomatis oleh workflow.

---

## FASE 2 — Code node `Cek_user_status` (baca `pending_offer`)

Cari baris:
```js
const pendingMsg = (debounceRow['pending_msg'] || '').trim();
```
**Tambahkan tepat di bawahnya:**
```js
const pendingOffer = (debounceRow['pending_offer'] || '').trim(); // tawaran VIRA dari turn sebelumnya
```
Lalu di blok `return [{ json: { ... } }]`, **tambahkan 1 baris** di dalam objek `json` (mis. setelah `should_ask_status: shouldAskStatus`):
```js
    pending_offer: pendingOffer,
```

---

## FASE 3 — Code node `Preprocess - Context Detection` (deteksi afirmasi + konsumsi tawaran)

### 3.1 — Tambah deteksi afirmasi

Cari blok komentar `// 6c. DETECT UNCLEAR / AMBIGUOUS SHORT REPLY` (di atas perhitungan `unclearReply`). **Tepat di bawah baris** `const unclearReply = (...)`, tambahkan:

```js
// ============================================
// 6d. PENDING CONFIRMATION (deterministik)
//     Afirmasi pendek atas tawaran VIRA sebelumnya -> langsung eksekusi.
// ============================================
const pendingOffer = (json.pending_offer || '').trim(); // dari Cek_user_status (STATS)

const affNorm = actualUserMessage.toLowerCase().replace(/[^a-z\s]/g, '').replace(/\s+/g, ' ').trim();
const emojiOnlyYes = /^[\s👍🙏🙂😊✅👌]+$/.test(actualUserMessage.trim());
const isAffirmative = emojiOnlyYes ||
  /^(ya+|iya+|y|ok|oke+|okay|okai|baik|baik kak|baik kk|boleh|mau|sip|setuju|lanjut|gas|yes|yaudah|yauda|yowes|monggo)$/.test(affNorm);

let confirmedAction = '';
let confirmedLink = '';
if (isAffirmative && pendingOffer) {
  const [act, lnk] = pendingOffer.split('::');
  confirmedAction = (act || '').trim().toUpperCase(); // SEND_GFORM | TALK_TO_SAM
  confirmedLink = (lnk || '').trim();
}
```

### 3.2 — Suntik konteks + buka gate data saat konfirmasi

Cari bagian `// 9. BUILD AI CONTEXT`. **Di paling akhir blok pembentukan `aiContext`** (sebelum `// 10. BUILD ENHANCED INPUT FOR AI`), tambahkan:

```js
// Pending confirmation -> instruksi tegas + buka data
if (confirmedAction === 'SEND_GFORM') {
  aiContext += `User MENGKONFIRMASI mau dikirim form pendaftaran (jawaban afirmatif atas tawaran VIRA sebelumnya). Kirim link form yang sesuai: [SEND_GFORM${confirmedLink ? ': ' + confirmedLink : ''}]. DILARANG [UNKNOWN], jangan tanya ulang. `;
} else if (confirmedAction === 'TALK_TO_SAM') {
  aiContext += `User MENGKONFIRMASI mau dihubungkan langsung ke Sam. Pasang [TALK_TO_SAM] dan balas singkat: "Oke, akan saya sampaikan ke Sam yaa. Mohon ditunggu, terimakasih." `;
}
```

### 3.3 — Pastikan data harga ikut terinjeksi saat konfirmasi form

Masih di node yang sama, cari deklarasi:
```js
const wantsToRegister = message.match(/daftar|mau ikut|tertarik|mau coba|mau daftar|link pendaftaran|link form|minta link/i) !== null;
```
**Ganti** baris itu jadi (agar konfirmasi form ikut membuka gate retrieval HARGA/PROGRAM di `FAQ Retrieve`):
```js
let wantsToRegister = message.match(/daftar|mau ikut|tertarik|mau coba|mau daftar|link pendaftaran|link form|minta link/i) !== null;
if (typeof confirmedAction !== 'undefined' && confirmedAction === 'SEND_GFORM') wantsToRegister = true;
```
> Catatan: `confirmedAction` dihitung di blok 6d (di atas), jadi sudah terdefinisi saat baris ini dieksekusi.

### 3.4 — Keluarkan field baru di OUTPUT

Di blok `return { ... }` paling bawah node, **tambahkan** field-field ini di dalam objek:
```js
  isAffirmative,
  pendingOffer,
  confirmedAction,
  confirmedLink,
```

---

## FASE 4 — Code node `Process All` (paksa aksi + catat tawaran + clear)

### 4.1 — Paksa aksi saat konfirmasi (deterministik)

Cari blok `// ── TAG: [TALK_TO_SAM] ──`. **Tepat setelah** blok fallback `talkToSamPatterns` selesai (setelah baris yang menutup `if (talkToSamPatterns.some(...))`), tambahkan:

```js
// ── DETERMINISTIC: paksa aksi kalau ini konfirmasi atas tawaran VIRA sebelumnya ──
const confirmedAction = preprocess.confirmedAction || '';
const confirmedLink   = preprocess.confirmedLink || '';
if (confirmedAction === 'SEND_GFORM') {
  isSendGForm = true;
  if (!gformLinkName && confirmedLink) gformLinkName = confirmedLink;
  console.log('🔒 FORCED SEND_GFORM (konfirmasi user). link=', gformLinkName || '(default)');
}
if (confirmedAction === 'TALK_TO_SAM') {
  isTalkToSam = true;
  console.log('🔒 FORCED TALK_TO_SAM (konfirmasi user).');
}
```
> `isSendGForm`, `gformLinkName`, `isTalkToSam` semuanya dideklarasikan `let` di atas, jadi aman ditimpa di sini.

### 4.2 — Catat tawaran VIRA untuk turn berikutnya (+ auto-clear)

Cari komentar `// ── LOGGING ──` (dekat akhir, sebelum `// ── RETURN ──`). **Tepat sebelum** blok LOGGING, tambahkan:

```js
// ── DETERMINISTIC: catat / bersihkan "tawaran tertunda" untuk turn berikutnya ──
let pendingOfferToSet = '';
const outLow = (cleanOutput || '').toLowerCase();
const offeredForm = /kirim(kan)?\s+(link\s+)?form|saya\s+kirim.*form|mau\s+saya\s+kirim.*form|boleh\s+saya\s+kirim.*form|saya\s+kirimkan\s+formnya/i.test(outLow);
const offeredSam  = /sambungkan.*sam|mau saya sambungkan|ngomong.*sama sam|bilang aja yaa|sampaikan.*ke sam/i.test(outLow);

if (isSendGForm || isTalkToSam) {
  pendingOfferToSet = '';                 // aksi sudah dieksekusi turn ini -> clear
} else if (offeredForm) {
  const prog = (preprocess.recommendedProgram || '').toLowerCase();
  let lk = 'GForm Pendaftaran Batch 5';   // default
  if (prog === 'seniors') lk = 'GForm Pendaftaran Seniors';
  else if (/mock/i.test(outLow)) lk = 'GForm Mock Interview';
  pendingOfferToSet = 'SEND_GFORM::' + lk;
} else if (offeredSam) {
  pendingOfferToSet = 'TALK_TO_SAM';
}
// kalau VIRA tidak menawarkan apa-apa -> pendingOfferToSet tetap '' (otomatis bersihkan tawaran lama)
```
> **Penting (sesuaikan nama link):** ganti `'GForm Pendaftaran Seniors'`, `'GForm Pendaftaran Batch 5'`, `'GForm Mock Interview'` agar **PERSIS** sama dengan kolom `Nama Link` di sheet **LINKS** (status Active). Kalau nama tidak cocok, injeksi URL di Process All gagal mencocokkan.

### 4.3 — Keluarkan field baru di RETURN

Di objek `return [{ json: { ... } }]` (akhir node), **tambahkan**:
```js
    confirmedAction,
    pendingOfferToSet,
```

---

## FASE 5 — Node baru `Update Pending Offer` (tulis ke STATS)

Tambah **Google Sheets** node baru:

- [ ] **Name:** `Update Pending Offer`
- [ ] **Operation:** `Update Row`
- [ ] **Document:** `The_Scholars_Database` · **Sheet:** `STATS`
- [ ] **Mapping Mode:** Map Each Column Manually
- [ ] **Column to match on:** `lid`
- [ ] **Values:**
  - `lid` = `={{ $('Chat Counter').item.json.user_lid }}`
  - `pending_offer` = `={{ $('Process All').item.json.pendingOfferToSet }}`

**Wiring:** dari node **`Process All`**, tarik 1 output baru ke **`Update Pending Offer`** (paralel dengan cabang `Wait1` / `IF Send GForm` / `IF Talk To Sam` yang sudah ada). Node ini cukup berhenti di situ (tidak perlu node lanjutan).

> Node ini jalan tiap balasan: mengisi tawaran baru ATAU menulis string kosong untuk membersihkan tawaran lama. Itu yang membuat sistem "satu-tembak" (one-shot) dan tidak menumpuk state basi.

---

## FASE 6 — Save & QA (deterministik — wajib lolos semua)

Klik **Save** sekali. Lalu jalankan test berikut dari WhatsApp (atau Pin/replay execution):

| # | Skenario | Langkah | Hasil yang HARUS terjadi |
|---|---|---|---|
| 1 | Konfirmasi form (kasus asli) | Pancing VIRA menawarkan form (mis. tanya harga Seniors → VIRA tawarkan form) lalu balas **"Baik kak"** | VIRA **mengirim link form** (Seniors), bukan `[UNKNOWN]` |
| 2 | Konfirmasi Sam (kasus asli) | Buat VIRA menawarkan "mau saya sambungkan ke Sam?" lalu balas **"Yaa"** | `Notify Talk to Sam` **jalan** + balasan "akan saya sampaikan ke Sam" |
| 3 | Afirmasi varian | Ulangi #1 dengan balasan **"boleh"**, **"oke"**, **"iya kak"**, **"👍"** | Sama seperti #1 (form terkirim) |
| 4 | Bukan afirmasi | Setelah VIRA tawarkan form, user malah tanya hal lain (mis. "kelasnya berapa orang?") | VIRA jawab pertanyaan normal; `pending_offer` di STATS **kembali kosong** (tidak menumpuk) |
| 5 | Afirmasi tanpa tawaran | Tanpa tawaran sebelumnya, user kirim "ya" | Flow normal (tidak memaksa kirim form/Sam); `pending_offer` kosong |
| 6 | HITL tetap utuh | `bot_mode = OFF` lalu user balas "ya" | Bot **diam** (HITL menang, tidak terpengaruh fix ini) |

Cek kolom **STATS → `pending_offer`** saat test: terisi `SEND_GFORM::...` / `TALK_TO_SAM` setelah VIRA menawarkan, lalu **kosong lagi** setelah dikonfirmasi/ditinggal.

---

## Rollback

Kalau ada masalah: n8n → workflow VIRA → **History** (atau import ulang JSON cadangan dari FASE 0). Kolom `pending_offer` di STATS boleh dibiarkan (tidak mengganggu versi lama).

---

## Ringkasan perubahan

| Komponen | Perubahan |
|---|---|
| Sheet STATS | +1 kolom `pending_offer` |
| `Cek_user_status` | baca `pending_offer` → teruskan ke Preprocess |
| `Preprocess - Context Detection` | deteksi `isAffirmative` + `confirmedAction`; buka gate data saat konfirmasi form |
| `Process All` | paksa `isSendGForm`/`isTalkToSam` saat konfirmasi; catat/clear `pendingOfferToSet` |
| Node baru `Update Pending Offer` | tulis `pending_offer` ke STATS (key `lid`) |

**Sifat:** deterministik (aksi dipaksa di kode, bukan tag dari LLM), one-shot (otomatis clear), aman terhadap HITL & migrasi LID (pakai key `lid`).
