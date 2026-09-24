# Endpoint n8n yang Perlu Dibuat — v3

Base URL yang sama: `https://n8n.srv1270416.hstgr.cloud/webhook`

---

## ✅ Endpoint Lama (Tetap Dipakai)

| Endpoint | Digunakan untuk |
|---|---|
| `GET /get-projects` | Ambil list proyek |
| `POST /add-project` | Tambah proyek baru |
| `POST /tim-interior` | Submit komplain (sama persis v2) |

---

## 🆕 Endpoint Baru yang Perlu Dibuat

### 1. `GET /v3/get-workers`

Ambil daftar nama pekerja dari Google Sheet.

**Response:**
```json
{
  "data": ["Andi Santoso", "Budi Prasetyo", "Cahyo Wibowo"]
}
```

**Sheet:** Buat tab baru "Workers" dengan kolom: `Nama`

---

### 2. `POST /v3/add-worker`

Tambah nama pekerja baru ke sheet.

**Request body:**
```json
{ "nama": "Deni Kurniawan" }
```

**Action:** Append row ke tab "Workers"

---

### 3. `POST /v3/submit-pekerjaan`

Simpan catatan pekerjaan (bisa banyak item sekaligus).

**Request body:**
```json
{
  "project": "BTN",
  "pekerja": "Andi Santoso",
  "tanggal": "2026-06-09",
  "catatan": "Finishing area dapur",
  "items": [
    {
      "no": 1,
      "pekerjaan": "Pasang keramik lantai 60x60",
      "vol": 12,
      "sat": "m2",
      "harga_satuan": 85000,
      "total": 1020000
    },
    {
      "no": 2,
      "pekerjaan": "Pasang plint keramik",
      "vol": 20,
      "sat": "m'",
      "harga_satuan": 35000,
      "total": 700000
    }
  ],
  "total": 1720000
}
```

**Action:** Untuk setiap item di `items[]`, append 1 row ke tab "Pekerjaan" dengan format:

| Kolom | Isi |
|---|---|
| ID | Auto (timestamp + random) |
| Tanggal | tanggal |
| Proyek | project |
| Pekerja | pekerja |
| Catatan | catatan |
| No | item.no |
| Pekerjaan | item.pekerjaan |
| Vol | item.vol |
| Sat | item.sat |
| Harga/Sat | item.harga_satuan |
| Total | item.total |
| Total Keseluruhan | total (hanya di baris pertama) |

---

### 4. `GET /v3/get-pekerjaan`

Ambil catatan pekerjaan berdasarkan filter.

**Query params:**
- `pekerja` (required) — nama pekerja
- `project` (optional) — filter per proyek

**Response:**
```json
{
  "data": [
    {
      "id": "PKJ-001",
      "project": "BTN",
      "pekerja": "Andi Santoso",
      "tanggal": "2026-06-07",
      "catatan": "Area lantai 1",
      "items": [
        { "no": 1, "pekerjaan": "Pasang keramik", "vol": 12, "sat": "m2", "harga_satuan": 85000, "total": 1020000 }
      ],
      "total": 1020000
    }
  ]
}
```

**Action:** Query sheet "Pekerjaan", filter by Pekerja (+ Project jika ada), group by tanggal+catatan, return array.

---

## 📋 Struktur Google Sheet yang Diperlukan

### Tab: `Workers`
| Nama |
|---|
| Andi Santoso |
| Budi Prasetyo |

### Tab: `Pekerjaan`
| ID | Tanggal | Proyek | Pekerja | Catatan | No | Pekerjaan | Vol | Sat | Harga/Sat | Total Item | Total Keseluruhan |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Tab: `Komplain` (sudah ada dari v2, tidak perlu diubah)

---

## 🔧 Setup di index.html

Setelah semua endpoint siap, ubah baris ini di `index.html`:

```javascript
// Baris 240-an
const TEST_MODE = true;  // ← ganti ke: false
```

Semua endpoint sudah terhubung, tidak perlu ubah yang lain.
