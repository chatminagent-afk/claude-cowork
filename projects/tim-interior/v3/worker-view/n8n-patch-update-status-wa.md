# Patch n8n: WA Notifikasi saat Worker Update Status

## Konteks
Setelah Worker View live, setiap kali tukang mengubah status pekerjaan,
kita ingin owner/mandor dapat notif WA otomatis.

Endpoint yang dimodifikasi: `POST /v3/update-status`

---

## Yang perlu ditambahkan di n8n

Buka workflow v3 di n8n, cari flow `Webhook - Update Status`.
Setelah node **"GS - Write Status"** (yang terakhir sebelum Respond),
tambahkan 2 node baru:

---

### Node 1 — Code: Build WA Notif

**Type:** Code  
**Name:** `Code - Build WA Update Notif`  
**Execute once:** No  

```javascript
// Ambil data dari upstream
const body    = $('Webhook - Update Status').first().json.body || $('Webhook - Update Status').first().json;
const updates = body.updates || [];
const pekerja = (body.pekerja || '').toString().trim();

// Nomor mandor/owner — ganti dengan nomor HP aktual (format: 628xxxxxxx)
const MANDOR_PHONE = '628xxxxxxxxxx';   // ← GANTI INI

if (!updates.length || !pekerja) return [];

// Pisahkan hanya item yang baru selesai (done)
const doneItems = updates.filter(u => u.status === 'done');
const progItems = updates.filter(u => u.status === 'inprogress');

if (!doneItems.length && !progItems.length) return [];

const statusLabel = { done: '✅ Selesai', inprogress: '🔨 On Progress', pending: '⏳ Belum' };

let msg = `🔔 *Update Pekerjaan — TIM Interior*\n\n`;
msg += `*${pekerja}* update status:\n`;

[...doneItems, ...progItems].forEach(u => {
  const label = statusLabel[u.status] || u.status;
  // batch_id sebagai referensi ringkas
  const ref = (u.batch_id || '').replace('PKJ-','#');
  msg += `${label} ${ref} item ${u.no_item}\n`;
});

msg += `\n_TIM Interior_`;

return [{ json: { phone: MANDOR_PHONE, waMessage: msg } }];
```

---

### Node 2 — HTTP: Kirim ke kirimi.id

**Type:** HTTP Request  
**Name:** `HTTP - Kirim WA Update Notif`  
**Method:** POST  
**URL:** `https://api.kirimi.id/v1/send-message`  

**Body (JSON):**
```json
{
  "token": "REDACTED",
  "phone": "={{ $json.phone }}",
  "message": "={{ $json.waMessage }}"
}
```

> Salin token dari node kirimi.id yang sudah ada di workflow
> (cek node "HTTP - Kirim WA Pekerjaan Baru", ambil token yang sama).

---

## Wiring

```
Webhook - Update Status
  → Code - Validate
  → (existing nodes...)
  → GS - Write Status
  → Code - Build WA Update Notif    ← tambahkan di sini
  → HTTP - Kirim WA Update Notif    ← dan ini
  → Respond to Webhook              ← sudah ada
```

**Catatan:** Jika GS Write gagal / 0 item → node Code otomatis skip
dan WA tidak dikirim (behavior yang diinginkan).

---

## Catatan pengembangan berikutnya

Idealnya message bisa lebih deskriptif (nama pekerjaan, proyek).
Untuk itu perlu tambahan step:
`GS - Baca Pekerjaan by BatchID` setelah validate,
lalu `Code - Enrich + Build WA` yang mengambil nama proyek & pekerjaan dari sheet.

Untuk sekarang, versi ringkas ini sudah cukup fungsional.
