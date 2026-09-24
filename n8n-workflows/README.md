# VIRA Workflows

Backup & dokumentasi semua workflow n8n proyek VIRA (WhatsApp AI assistant).
Host n8n: `n8n.srv1270416.hstgr.cloud`. Repo ini **private**.

> Nilai rahasia (secret Kirimi, token) sudah diganti `REDACTED`, dan `pinData` (data uji eksekusi) dikosongkan.
> Setelah import ke n8n, isi ulang secret lewat CONFIG sheet / credential n8n.

## Workflow aktif (per 2026-09-24)

| Folder | File | ID n8n | Catatan |
|---|---|---|---|
| `personal/` | `VIRA-Personal-Main.json` | `AC65HeFegHFCFc5aY609u` | v3.13 (live). Prompt: `system-prompt-v3.13.md` |
| | `VIRA-Personal-Follow-up.json` | `THuHlao6hdnMtlL01vn_p` | v2, 3 bucket |
| | `VIRA-Personal-STATS-Cleanup.json` | `JwbvgIE_hPSG92oihZTyX` | cron 02:30, tgl 1 Jan/Apr/Jul/Okt |
| `thescholars/` | `VIRA-TS.json` | `27Nw6efKWq3Pq-J1T2Z2w` | 56 node |
| | `TS-STATS-Cleanup.json` | `flkj_TqYPs350gF3gp74K` | cron 00:01 |
| | `TS-Topic-Harvester-WF-A.json`, `TS-Monthly-Rollup-WF-B.json` | – | tidak terbaca MCP, status live belum diverifikasi |
| `persada/` | `VIRA-PCR-AI-Powered.json` | `oCQ315OHAjQEuG2vh14RR` | V1.5 (86 node) |
| | `PCR-Follow-up-AI-Powered.json` | `qaux8b14IgvxEXfoUtxa2` | |
| | `PCR-STATS-Cleanup.json` | `Uqt1M4Soj8gPbSdPBShBX` | |
| `dashboard/` | `VIRA-Dashboard-API.json` | – | 39 node; plus `app revamp/` (frontend), `n8n/` (builder), `docs/` |
| | `DASH_AUDIT-Cleanup.json` | `1PClsIt53I6Cn2CcpkCPg` | |
| `global/` | `GLOBAL-Sheet-Cleanup.json` | `U0Mqitn6RB520vNwxVGci` | harian 03:00 + kuartalan 02:00 |
| | `GLOBAL-VIRA-Error-Notifier.json` | `0mp_AdLtInm68RxQUwLqV` | |
| | `GLOBAL-Email-Fallback-Notifier.json` | – | |

## Archive
Versi lama dan workflow yang sudah tidak dipakai, dikelompokkan per project:
`archive/personal`, `archive/thescholars`, `archive/persada`, `archive/dashboard`, `archive/global`,
`archive/fonnte-migration` (versi migrasi Fonnte, belum dipakai), `archive/eval-sementara` (workflow uji, "hapus sesudah uji").

## Catatan
- Nomor WA admin/whitelist masih tertanam di sebagian workflow (fungsional). Jangan jadikan repo ini publik.
- Yang tidak dimasukkan: service account key Google, `KREDENSIAL-*`, CSV kontak, PDF deck klien.
- Beberapa workflow tidak terbaca lewat MCP n8n (`availableInMCP=false`); versi live-nya belum dibandingkan dengan file di sini.
