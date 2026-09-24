# Panduan Build Flow — Weekly Reminder Ci Lenny (Adaptive Card UAT Status)

Tanggal dibuat: 11 Juni 2026 · Update terakhir: 12 Juni 2026
Tujuan: Flow Power Automate yang setiap **Jumat 08:00 WIB** memposting **Adaptive Card** status UAT mingguan ke **group chat Teams (Ci Lenny)**, data dari `Tracking Project MBI.xlsx` di SharePoint Ateam786.

Dokumen ini punya 3 bagian:
- **BAGIAN A** — Import package siap-pakai (`2026-06-11-WeeklyReminderCiLenny-Package.zip`). Coba ini dulu.
- **BAGIAN B** — Build manual node-per-node (kalau import gagal). Semua field & expression ada di sini.
- **BAGIAN C** — Uji coba, verifikasi & solusi error yang sudah pernah muncul.

---

## 0. Fakta penting hasil pengecekan file Excel

| Hal | Nilai aktual |
|---|---|
| Nama sheet status | `Project-Testing ` (ADA SPASI di belakang) |
| Tabel di sheet Project-Testing | **`TableProjectTesting`** (A1:BS415) |
| Nama sheet timeline | `Timeline Implementation` |
| Tabel di sheet Timeline | **`Table5`** (A1:Q19) |
| Kolom track | `Track1` (angka 1–18) |
| Kolom PIC | `Team Member1` |
| Kolom nama project | `Project Name (per slicing)` |
| Kolom status | `Status Project` |
| Kolom bulan implementasi | `Estimated Implementation` (format `Jun 2026`) |
| Kolom % UAT / Regresi / Pilot / Prod | `% UAT Overall` / `% Regresi Overall` / `% Pilot Overall` / `% Prod Overall` |
| Timeline: bulan / tanggal | `Year-Month` · `Imple Pilot` · `Imple Prod` · `Rollout` |

**Isi yang dibuat (final):**

**Section 1 — per status (4 status saja), tiap baris: project — Track — PIC:**
1. `ON GOING PREP UAT`
2. `ON GOING UAT` (+ `% UAT Overall`)
3. `ON HOLD`
4. `ON GOING ODR` (judul section ditampilkan sebagai **"Next Project"**)

> ⚠️ Section **ON GOING REGRESSION SUDAH DIHAPUS** dari Section 1.

**Section 2 — info bulan berjalan:**
- Daftar fitur: filter `Estimated Implementation` = bulan ini.
- 3 angka rata-rata dari project bulan ini: **Avg % Pilot Overall**, **Avg % Prod Overall**, **Avg % Regresi Overall** (dijumlahkan lalu dibagi jumlah project yang punya nilai angka).
- Tanggal dari sheet Timeline (bulan ini): `Imple Pilot`, `Imple Prod`, `Rollout`.
- Tombol link ke Tracking Sheet.

**Catatan angka %:** disimpan sebagai pecahan (`1`=100%, `0.77`=77%). Expression sudah `×100`. Banyak sel `% Pilot/Prod/Regresi` **kosong (null)** atau berisi **teks** (mis. `Diluar Paketan myBCA`) — makanya rata-rata pakai **guard angka** (lihat B.4) supaya `float()` tidak error.

---

## BAGIAN A — Import Package Siap Pakai

### A.1 Import
1. https://make.powerautomate.com → pilih environment yang benar.
2. **My flows → Import → Import Package (Legacy)** → upload `2026-06-11-WeeklyReminderCiLenny-Package.zip`.
3. Di Review Package Content:
   - Flow → **Create as new**.
   - **Excel Online (Business)** & **Microsoft Teams** connection → pilih koneksi akun BCA kamu.
4. **Import**. Kalau muncul "save it as a new flow first", klik link draft-nya — isinya lengkap.

### A.2 Lengkapi isian environment-specific
Buka flow → **Edit**:

1. **List_rows_Project_Testing**: Location `https://bcaoffice365.sharepoint.com/sites/Ateam786` · Library `Documents` · File `Tracking Project MBI.xlsx` · **Table `TableProjectTesting`**.
2. **List_rows_Timeline**: sama, **Table `Table5`**.
3. **Post_Adaptive_Card**: Post as `Flow bot` · Post in `Group chat` · pilih group chat **Ci Lenny**.
   - ⚠️ Kalau field **"Adaptive Card"** ditandai *required* dan kartunya malah ada di field `body/messageContent`: **kosongkan `body/messageContent`**, lalu **paste JSON dari B.6 ke field "Adaptive Card"**.

4. **Save → Test → Manually → Run flow**.

---

## BAGIAN B — Build Manual (Node per Node)

### B.1 Trigger — Recurrence
Repeat every `1` `Week` · Time zone `(UTC+07:00) Bangkok, Hanoi, Jakarta` · On these days **Friday** · At these hours `8` · At these minutes `0`.

### B.2 List rows present in a table (×2)
Connector **Excel Online (Business) → List rows present in a table**.

**`List_rows_Project_Testing`**: Location `https://bcaoffice365.sharepoint.com/sites/Ateam786` · Document Library `Documents` · File `Tracking Project MBI.xlsx` · Table `TableProjectTesting`.
**`List_rows_Timeline`**: sama, Table `Table5`.

> Keduanya: **... → Settings → Pagination → On**, Threshold `5000`.

### B.3 Initialize variable (14 buah, semua di level atas)

| # | Name | Type | Value |
|---|---|---|---|
| 1 | `varBulan` | String | `formatDateTime(utcNow(),'MMM yyyy')` |
| 2 | `varTanggal` | String | `convertTimeZone(utcNow(),'UTC','SE Asia Standard Time','dd MMMM yyyy')` |
| 3 | `varPrepUAT` | String | *(kosong)* |
| 4 | `varUAT` | String | *(kosong)* |
| 5 | `varOnHold` | String | *(kosong)* |
| 6 | `varODR` | String | *(kosong)* |
| 7 | `varFitur` | String | *(kosong)* |
| 8 | `varTimeline` | String | *(kosong)* |
| 9 | `sumPilot` | Float | `0` |
| 10 | `cntPilot` | Integer | `0` |
| 11 | `sumProd` | Float | `0` |
| 12 | `cntProd` | Integer | `0` |
| 13 | `sumRegresi` | Float | `0` |
| 14 | `cntRegresi` | Integer | `0` |

### B.4 Apply to each — looping Project-Testing
Output: **value** dari `List_rows_Project_Testing`. **... → Settings → Concurrency = On, Degree 1.**

**Switch (Control → Switch)** — On (expression): `item()?['Status Project']`. 4 case:

| Case | Append ke | Value (Expression) |
|---|---|---|
| `ON GOING PREP UAT` | `varPrepUAT` | **Expr-Plain** |
| `ON GOING UAT` | `varUAT` | **Expr-UAT** |
| `ON HOLD` | `varOnHold` | **Expr-Plain** |
| `ON GOING ODR` | `varODR` | **Expr-Plain** |

**Expr-Plain:**
```
concat('• ', item()?['Project Name (per slicing)'], '  —  Track ', string(item()?['Track1']), ' · PIC: ', item()?['Team Member1'], decodeUriComponent('%0A%0A'))
```
**Expr-UAT:**
```
concat('• ', item()?['Project Name (per slicing)'], '  —  Track ', string(item()?['Track1']), ' · PIC: ', item()?['Team Member1'], ' · Progress: ', if(empty(item()?['% UAT Overall']),'-',concat(formatNumber(mul(float(item()?['% UAT Overall']),100),'0'),'%')), decodeUriComponent('%0A%0A'))
```

**SETELAH Switch, tambah Condition Section 2:** `item()?['Estimated Implementation']` **is equal to** `variables('varBulan')` → **If yes**:

1. **Append to string variable** `varFitur`:
   ```
   concat('• ', item()?['Project Name (per slicing)'], decodeUriComponent('%0A%0A'))
   ```
2. **Condition (numeric guard) % Pilot** → gunakan 2 baris di-AND:
   - Baris 1 (Expression): `empty(item()?['% Pilot Overall'])` — **is equal to** — `false`
   - Baris 2 (Expression): `empty(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(string(item()?['% Pilot Overall']),'0',''),'1',''),'2',''),'3',''),'4',''),'5',''),'6',''),'7',''),'8',''),'9',''),'.',''),'-',''))` — **is equal to** — `true`
   - **If yes**: **Increment variable** `sumPilot` value `float(item()?['% Pilot Overall'])` ; **Increment variable** `cntPilot` by `1`.
3. **Condition % Prod** (sama pola, ganti `% Pilot Overall` → `% Prod Overall`, var → `sumProd`/`cntProd`).
4. **Condition % Regresi** (ganti → `% Regresi Overall`, var → `sumRegresi`/`cntRegresi`).

> Guard angka ini WAJIB: kolom %  banyak yang null/teks; tanpa guard, `float()` error (`Action 'If_Pilot_NotEmpty' failed`). Untuk `sumPilot/Prod/Regresi` WAJIB pakai **Increment variable**, BUKAN Set variable (Set variable yang merujuk dirinya sendiri ditolak: `Self reference is not supported`).

### B.5 Apply to each — looping Timeline
Output: **value** dari `List_rows_Timeline` (Concurrency 1). Di dalam **Condition** `item()?['Year-Month']` **is equal to** `variables('varBulan')` → **If yes** → **Set variable** `varTimeline`:
```
concat('Pilot Imple : ', string(item()?['Imple Pilot']), decodeUriComponent('%0A%0A'), 'Prod Imple : ', string(item()?['Imple Prod']), decodeUriComponent('%0A%0A'), 'Rollout : ', string(item()?['Rollout']))
```

### B.6 Post adaptive card in a chat or channel
Post as `Flow bot` · Post in `Group chat` · Group chat **Ci Lenny**. Paste JSON ini ke field **Adaptive Card**:

```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.4",
  "body": [
    { "type": "TextBlock", "text": "📋 Weekly UAT Status Report — @{variables('varTanggal')}", "wrap": true, "weight": "Bolder", "size": "Large" },
    { "type": "TextBlock", "text": "────────────", "wrap": true, "spacing": "Small" },
    { "type": "TextBlock", "text": "🟡 ON GOING PREP UAT", "wrap": true, "weight": "Bolder", "color": "Warning", "spacing": "Medium" },
    { "type": "TextBlock", "text": "@{if(empty(variables('varPrepUAT')),'— (tidak ada)',variables('varPrepUAT'))}", "wrap": true },
    { "type": "TextBlock", "text": "🔵 ON GOING UAT", "wrap": true, "weight": "Bolder", "color": "Accent", "spacing": "Medium" },
    { "type": "TextBlock", "text": "@{if(empty(variables('varUAT')),'— (tidak ada)',variables('varUAT'))}", "wrap": true },
    { "type": "TextBlock", "text": "⏸️ ON HOLD", "wrap": true, "weight": "Bolder", "color": "Attention", "spacing": "Medium" },
    { "type": "TextBlock", "text": "@{if(empty(variables('varOnHold')),'— (tidak ada)',variables('varOnHold'))}", "wrap": true },
    { "type": "TextBlock", "text": "📦 Next Project", "wrap": true, "weight": "Bolder", "color": "Good", "spacing": "Medium" },
    { "type": "TextBlock", "text": "@{if(empty(variables('varODR')),'— (tidak ada)',variables('varODR'))}", "wrap": true },
    { "type": "TextBlock", "text": "────────────", "wrap": true, "spacing": "Medium" },
    { "type": "TextBlock", "text": "📅 INFO BULAN BERJALAN — @{variables('varBulan')}", "wrap": true, "weight": "Bolder", "size": "Medium", "spacing": "Medium" },
    { "type": "TextBlock", "text": "Paketan / Fitur:", "wrap": true, "weight": "Bolder" },
    { "type": "TextBlock", "text": "@{if(empty(variables('varFitur')),'— (tidak ada)',variables('varFitur'))}", "wrap": true },
    { "type": "TextBlock", "text": "Progress Summary:", "wrap": true, "weight": "Bolder", "spacing": "Small" },
    { "type": "TextBlock", "text": "• Avg % Pilot Overall : @{if(equals(variables('cntPilot'),0),'-',concat(formatNumber(mul(div(variables('sumPilot'),variables('cntPilot')),100),'0'),'%'))}\n\n• Avg % Prod Overall : @{if(equals(variables('cntProd'),0),'-',concat(formatNumber(mul(div(variables('sumProd'),variables('cntProd')),100),'0'),'%'))}\n\n• Avg % Regresi Overall : @{if(equals(variables('cntRegresi'),0),'-',concat(formatNumber(mul(div(variables('sumRegresi'),variables('cntRegresi')),100),'0'),'%'))}", "wrap": true },
    { "type": "TextBlock", "text": "Timeline Implementation:", "wrap": true, "weight": "Bolder", "spacing": "Small" },
    { "type": "TextBlock", "text": "@{if(empty(variables('varTimeline')),'— (tidak ada)',variables('varTimeline'))}", "wrap": true }
  ],
  "actions": [
    { "type": "Action.OpenUrl", "title": "📎 Buka Tracking Sheet (Excel)", "url": "https://bcaoffice365.sharepoint.com/:x:/r/sites/Ateam786/_layouts/15/Doc.aspx?sourcedoc=%7B50F3C17B-9E4A-4C1B-AB30-911DFAE76E39%7D&file=Tracking%20Project%20MBI.xlsx&nav=MTVfezU0MDA5NkIwLUM2REEtNDY1Ri1CODA4LUM3ODYyMzYzN0VGQ30&action=default&mobileredirect=true" }
  ]
}
```

### B.7 Urutan akhir
```
Recurrence → List_rows_Project_Testing → List_rows_Timeline →
Initialize 14 variable →
Apply to each Project (Switch 4 status + Condition bulan berjalan → fitur + 3 guard numeric Pilot/Prod/Regresi) →
Apply to each Timeline (Condition Year-Month → Set varTimeline) →
Post Adaptive Card (Group chat Ci Lenny)
```

---

## BAGIAN C — Uji Coba, Verifikasi & Error yang Pernah Muncul

**Test → Manually → Run flow**, lalu cek group chat Ci Lenny.

Error yang sudah ditemui & solusinya:

| Error | Sebab | Solusi |
|---|---|---|
| `Self reference is not supported ... 'sumPilot'` (saat Save) | `Set variable sumPilot = sumPilot + ...` | Pakai **Increment variable**, bukan Set variable (B.4) |
| `Action 'If_Pilot_NotEmpty' failed` (saat Run) | `float()` kena sel kosong/teks (`Diluar Paketan myBCA`) | Pakai **guard angka** 2-baris AND (B.4) |
| Field **"Adaptive Card" is required** | Connector menaruh kartu di `body/messageContent`, field wajibnya `Adaptive Card` | Kosongkan `body/messageContent`, paste JSON ke field **Adaptive Card** (B.6) |
| Import legacy "failed / save as new flow" | Package legacy hand-built | Klik link **Save as a new flow** → lanjut isi config |
| Tampilan designer beda (kotak ungu vertikal) | Classic Designer | Toggle **New designer** di bar atas |

### Checklist Go-Live
- [ ] Koneksi Excel & Teams tersambung
- [ ] Table `TableProjectTesting` & `Table5`, Pagination On (5000)
- [ ] Concurrency = 1 di kedua Apply to each
- [ ] Switch hanya 4 status (regression sudah dihapus)
- [ ] 3 guard numeric (Pilot/Prod/Regresi) pakai Increment variable
- [ ] Card di field "Adaptive Card", group chat Ci Lenny terpilih
- [ ] Trigger Jumat 08:00 WIB
- [ ] Test run sukses & card tampil benar
