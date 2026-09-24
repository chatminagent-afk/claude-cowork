# n8n Ops — deploy ke Cloudflare Workers

Dashboard + proxy dalam satu Worker. Dashboard di-serve dari origin yang sama
dengan proxy, jadi **tidak ada CORS** dan **API key n8n tidak pernah masuk ke HP**.

```
Browser HP ──X-N8N-API-KEY: <DASH_TOKEN>──▶ Worker ──X-N8N-API-KEY: <key asli>──▶ n8n
                                            (secret disimpan di Cloudflare)
```

## Setup

```bash
cd "D:\Documents\Claude Cowork\2026-08-03-n8n-dashboard-worker"
npx wrangler login
```

Buat token dashboard (string acak bebas, ini yang nanti kamu ketik di HP):

```bash
npx wrangler secret put DASH_TOKEN
```

Masukkan API key n8n yang asli:

```bash
npx wrangler secret put N8N_API_KEY
```

Deploy:

```bash
npx wrangler deploy
```

## Isian di HP

Buka `https://n8n.chatminagent.workers.dev` → tab Settings:

| Field | Isi |
|---|---|
| N8N_BASE_URL | `https://n8n.chatminagent.workers.dev/n8n` |
| N8N_API_KEY | `DASH_TOKEN` yang kamu buat di atas — **bukan** API key n8n |
| CORS Proxy | biarkan **OFF** |

Save Credentials → Test.

## Kalau perlu ganti token

```bash
npx wrangler secret put DASH_TOKEN
npx wrangler deploy
```

Token lama langsung mati. API key n8n tidak perlu diganti.

## Batasan

- Hanya `/api/v1/*` yang di-proxy. Endpoint internal `/rest/*` diblokir,
  jadi tombol Retry tetap tidak berfungsi (memang tidak ada di Public API v1).
- Worker ini mengasumsikan dashboard dibuka dari origin yang sama.
  Membuka `index.html` dari `file://` tetap kena CORS.
