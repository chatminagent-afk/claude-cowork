# -*- coding: utf-8 -*-
"""Rakit workflow n8n: VIRA Dashboard - DASH_AUDIT Cleanup (multi-tenant, 1 workflow)."""
import json, os

OUT = r"D:\Documents\Claude Cowork\VIRA Dashboard\2026-08-26-dash-audit-cleanup\2026-08-26-VIRA-Dashboard-DASH_AUDIT-Cleanup.json"

CRED = {"googleApi": {"id": "5KD9A3Tef1H8UQKk", "name": "Google Service Account - VIRA Dashboard"}}

JS_FANOUT = r"""// ====================================================================
// KONFIGURASI  -- HANYA NODE INI YANG PERLU DIEDIT
// --------------------------------------------------------------------
// Tambah klien ke-3 = tambah 1 baris di array TENANTS. Nol perubahan
// di node lain (pola sama dengan 'Fan Out Tabs' di VIRA Dashboard API).
//
// RETENTION_DAYS = 0   -> hapus SEMUA baris data, sisakan header saja
//                         (ini yang diminta: wipe, sisakan header)
// RETENTION_DAYS = 90  -> simpan 90 hari terakhir, buang yang lebih tua
//                         (kalau nanti mau tetap punya jejak audit)
// ====================================================================
const RETENTION_DAYS = 0;
const AUDIT_TAB      = 'DASH_AUDIT';

const TENANTS = [
  { tenant: 'thescholars', nama: 'The Scholars',             doc_id: '1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE' },
  { tenant: 'persada',     nama: 'Persada Cisoka Residence', doc_id: '1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o' },
];

// Satu item per tenant -> diproses satu-satu oleh 'Loop Over Tenants'.
return TENANTS.map(t => ({
  json: { ...t, tab: AUDIT_TAB, retention_days: RETENTION_DAYS }
}));
"""

JS_HITUNG = r"""// ====================================================================
// HITUNG BLOK BARIS YANG DIHAPUS  (1 tenant per iterasi)
// --------------------------------------------------------------------
// DASH_AUDIT ditulis append-only oleh node 'Append Audit' di workflow
// VIRA Dashboard API, jadi urutan baris = urutan waktu. Baris terlama
// selalu blok kontigu di atas => cukup 1x delete range (hemat kuota).
//
// Header (baris 1) TIDAK PERNAH ikut: filter row_number >= 2.
// Kalau tab DASH_AUDIT belum dibuat, node Read di-set
// onError=continueRegularOutput sehingga item yang masuk ke sini tidak
// punya row_number -> tersaring jadi 0 baris -> lewat, bukan error.
// ====================================================================
const ctx  = $('Loop Over Tenants').first().json;
const RET  = Number(ctx.retention_days || 0);
const base = { tenant: ctx.tenant, nama: ctx.nama, doc_id: ctx.doc_id, tab: ctx.tab };

const rows = $input.all()
  .map(i => i.json)
  .filter(r => r && r.row_number !== undefined && Number(r.row_number) >= 2)
  .sort((a, b) => Number(a.row_number) - Number(b.row_number)); // atas -> bawah

if (!rows.length) {
  return [{ json: { ...base, startRow: 0, count: 0, alasan: 'tidak ada baris data (tab kosong / belum dibuat)' } }];
}

const startRow = Number(rows[0].row_number);

if (RET <= 0) {
  return [{ json: { ...base, startRow, count: rows.length, alasan: 'wipe penuh, header dipertahankan' } }];
}

const cutoff = Date.now() - RET * 24 * 60 * 60 * 1000;
let n = 0;
for (const r of rows) {
  const t = Date.parse(r.ts);
  // ts tak terbaca dianggap sampah lama -> ikut dihapus, tapi hanya
  // selama masih di blok kontigu paling atas.
  if (isNaN(t) || t < cutoff) n++; else break;
}
return [{ json: { ...base, startRow, count: n, alasan: 'retensi ' + RET + ' hari' } }];
"""

JS_CATAT = r"""// Node googleSheets 'delete' membuang konteks di output-nya.
// Ambil lagi dari node hitung supaya ringkasan akhir tetap informatif.
const ctx = $('Hitung Baris Dihapus').first().json;
return [{ json: { ...ctx, status: 'deleted' } }];
"""

JS_LEWATI = r"""const ctx = $('Hitung Baris Dihapus').first().json;
return [{ json: { ...ctx, status: 'skipped' } }];
"""

JS_RINGKASAN = r"""// Output SplitInBatches cabang 'done' = semua item yang kembali ke loop.
const detail = $input.all().map(i => i.json).map(r => ({
  tenant:      r.tenant || '?',
  tab:         r.tab || 'DASH_AUDIT',
  status:      r.status || 'unknown',
  mulai_baris: Number(r.startRow || 0),
  dihapus:     Number(r.count || 0),
  alasan:      r.alasan || '',
}));
return [{ json: {
  ok: true,
  workflow: 'VIRA Dashboard - DASH_AUDIT Cleanup',
  total_baris_dihapus: detail.reduce((a, b) => a + b.dihapus, 0),
  detail,
} }];
"""

STICKY = """## DASH_AUDIT Cleanup - 1 workflow untuk SEMUA tenant

Kenapa cukup satu, bukan satu per klien:
- kedua spreadsheet dibuka pakai credential yang SAMA (Google Service Account - VIRA Dashboard)
- nama tab & skema kolom identik: ts | actor | role | no_wa | from | to
- documentId di-set dinamis lewat expression, persis pola Fan Out Tabs -> Loop Over Tabs di workflow VIRA Dashboard API

Tambah klien ke-3 = tambah 1 baris di node Fan Out Tenants. Node lain tidak perlu disentuh.

Isolasi kegagalan: node Read & Delete pakai onError=continueRegularOutput, jadi kalau tab satu tenant belum ada / gagal, tenant lain tetap dibersihkan."""

nodes = [
    {
        "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 2 1 1,4,7,10 *"}]}},
        "id": "sched-quarterly", "name": "Tiap 3 bulan 02:00 WIB",
        "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2, "position": [-40, 0],
        "notes": "0 2 1 1,4,7,10 * = 1 Jan / 1 Apr / 1 Jul / 1 Okt pukul 02:00 WIB.\nKalau mau BULANAN, ganti jadi: 0 2 1 * *",
    },
    {
        "parameters": {}, "id": "manual-trigger", "name": "Test manual",
        "type": "n8n-nodes-base.manualTrigger", "typeVersion": 1, "position": [-40, 200],
        "notes": "Untuk smoke test. Set RETENTION_DAYS besar dulu supaya dry-run aman.",
    },
    {
        "parameters": {"jsCode": JS_FANOUT}, "id": "fan-out-tenants", "name": "Fan Out Tenants",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [200, 100],
    },
    {
        "parameters": {"options": {"reset": False}}, "id": "loop-tenants", "name": "Loop Over Tenants",
        "type": "n8n-nodes-base.splitInBatches", "typeVersion": 3, "position": [420, 100],
    },
    {
        "parameters": {
            "authentication": "serviceAccount",
            "documentId": {"__rl": True, "value": "={{ $json.doc_id }}", "mode": "id"},
            "sheetName": {"__rl": True, "value": "={{ $json.tab }}", "mode": "name"},
            "options": {},
        },
        "id": "read-audit", "name": "Read DASH_AUDIT",
        "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7, "position": [660, 220],
        "alwaysOutputData": True, "onError": "continueRegularOutput",
        "retryOnFail": True, "waitBetweenTries": 3000,
        "credentials": CRED,
        "notes": "Baca semua baris DASH_AUDIT milik tenant yang sedang diproses.\nonError=continue supaya tab yang belum dibuat tidak menggagalkan tenant lain.",
    },
    {
        "parameters": {"jsCode": JS_HITUNG}, "id": "hitung-baris", "name": "Hitung Baris Dihapus",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [880, 220],
    },
    {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                "conditions": [{
                    "id": "ada-baris",
                    "leftValue": "={{ $json.count }}",
                    "rightValue": 0,
                    "operator": {"type": "number", "operation": "gt"},
                }],
                "combinator": "and",
            },
            "looseTypeValidation": True,
            "options": {},
        },
        "id": "if-ada-baris", "name": "Ada Baris?",
        "type": "n8n-nodes-base.if", "typeVersion": 2, "position": [1100, 220],
    },
    {
        "parameters": {
            "authentication": "serviceAccount",
            "operation": "delete",
            "documentId": {"__rl": True, "value": "={{ $json.doc_id }}", "mode": "id"},
            "sheetName": {"__rl": True, "value": "={{ $json.tab }}", "mode": "name"},
            "startIndex": "={{ $json.startRow }}",
            "numberToDelete": "={{ $json.count }}",
        },
        "id": "delete-rows", "name": "Delete Rows (header aman)",
        "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7, "position": [1340, 120],
        "onError": "continueRegularOutput", "retryOnFail": True, "waitBetweenTries": 3000,
        "credentials": CRED,
        "notes": "startIndex = nomor baris 1-based (baris pertama = 1).\nSelalu >= 2 karena header disaring di node hitung.",
    },
    {
        "parameters": {"jsCode": JS_CATAT}, "id": "catat-hasil", "name": "Catat Hasil",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1560, 120],
    },
    {
        "parameters": {"jsCode": JS_LEWATI}, "id": "lewati", "name": "Lewati (kosong)",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [1340, 340],
    },
    {
        "parameters": {"jsCode": JS_RINGKASAN}, "id": "ringkasan", "name": "Ringkasan",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [660, -80],
    },
    {
        "parameters": {"width": 540, "height": 320, "content": STICKY},
        "id": "sticky-doc", "name": "Sticky Note",
        "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": [-40, -420],
    },
]


def c(name, idx=0):
    return {"node": name, "type": "main", "index": idx}


connections = {
    "Tiap 3 bulan 02:00 WIB": {"main": [[c("Fan Out Tenants")]]},
    "Test manual": {"main": [[c("Fan Out Tenants")]]},
    "Fan Out Tenants": {"main": [[c("Loop Over Tenants")]]},
    # output 0 = selesai (done), output 1 = tiap batch
    "Loop Over Tenants": {"main": [[c("Ringkasan")], [c("Read DASH_AUDIT")]]},
    "Read DASH_AUDIT": {"main": [[c("Hitung Baris Dihapus")]]},
    "Hitung Baris Dihapus": {"main": [[c("Ada Baris?")]]},
    # output 0 = true, output 1 = false
    "Ada Baris?": {"main": [[c("Delete Rows (header aman)")], [c("Lewati (kosong)")]]},
    "Delete Rows (header aman)": {"main": [[c("Catat Hasil")]]},
    "Catat Hasil": {"main": [[c("Loop Over Tenants")]]},
    "Lewati (kosong)": {"main": [[c("Loop Over Tenants")]]},
}

workflow = {
    "name": "VIRA Dashboard - DASH_AUDIT Cleanup (tiap 3 bulan, 02:00 WIB)",
    "nodes": nodes,
    "connections": connections,
    "settings": {
        "executionOrder": "v1",
        "timezone": "Asia/Jakarta",
        "saveManualExecutions": True,
        "saveDataSuccessExecution": "all",
        "saveDataErrorExecution": "all",
    },
    "pinData": {},
}

names = {n["name"] for n in nodes}
for src, spec in connections.items():
    assert src in names, "source hilang: " + src
    for branch in spec["main"]:
        for conn in branch:
            assert conn["node"] in names, "target hilang: " + conn["node"]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)
print("OK ->", OUT, os.path.getsize(OUT), "bytes,", len(nodes), "node")
