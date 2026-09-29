/**
 * n8n CORS Proxy — Worker berdiri sendiri.
 *
 * Dipakai karena Worker static-assets tidak bisa punya variables/secrets,
 * jadi proxy-nya dipisah ke Worker yang benar-benar punya kode.
 *
 * Alur:
 *   HP  --X-N8N-API-KEY: DASH_TOKEN-->  Worker ini  --API key asli-->  n8n
 *
 * Beda origin dengan dashboard, tapi CORS di sini milik kita sendiri —
 * jadi tinggal dikirim, tidak seperti n8n yang tidak mau mengirimnya.
 *
 * API key n8n asli hanya hidup sebagai secret di Cloudflare, tidak pernah
 * sampai ke HP. Yang disimpan di localStorage HP cuma DASH_TOKEN, yang bisa
 * dicabut dari Cloudflare tanpa menyentuh n8n.
 */

const ALLOWED_PREFIX = '/api/v1/';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = corsHeaders(env, request.headers.get('Origin') || '');

    // Preflight. Header X-N8N-API-KEY itu custom, jadi browser selalu
    // kirim OPTIONS dulu sebelum request aslinya.
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }

    // Health check — supaya bisa dicek dari browser tanpa token.
    if (url.pathname === '/' || url.pathname === '/health') {
      return json({
        ok: true,
        service: 'n8n-cors-proxy',
        configured: Boolean(env.N8N_BASE && env.N8N_API_KEY && env.DASH_TOKEN)
      }, 200, cors);
    }

    // Public API saja. /rest/* diblokir — itu internal API yang butuh
    // session cookie, dan meneruskannya cuma bikin bocor tanpa hasil.
    if (!url.pathname.startsWith(ALLOWED_PREFIX)) {
      return json({ message: 'Hanya /api/v1/* yang di-proxy.' }, 403, cors);
    }

    if (!env.DASH_TOKEN) {
      return json({ message: 'Worker belum dikonfigurasi: DASH_TOKEN kosong.' }, 500, cors);
    }
    if (!safeEqual(request.headers.get('X-N8N-API-KEY') || '', env.DASH_TOKEN)) {
      return json({ message: 'Dashboard token salah.' }, 401, cors);
    }
    if (!env.N8N_API_KEY || !env.N8N_BASE) {
      return json({ message: 'Worker belum dikonfigurasi: N8N_BASE / N8N_API_KEY kosong.' }, 500, cors);
    }

    const target = env.N8N_BASE.replace(/\/+$/, '') + url.pathname + url.search;

    const headers = new Headers({
      'X-N8N-API-KEY': env.N8N_API_KEY,
      'Accept': 'application/json'
    });
    const ct = request.headers.get('Content-Type');
    if (ct) headers.set('Content-Type', ct);

    const init = { method: request.method, headers, redirect: 'manual' };
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      init.body = await request.arrayBuffer();
    }

    let res;
    try {
      res = await fetch(target, init);
    } catch (err) {
      return json({ message: 'n8n tidak bisa dihubungi: ' + err.message }, 502, cors);
    }

    // Bangun header balasan dari nol — jangan teruskan Set-Cookie dari n8n.
    const out = new Headers(cors);
    out.set('Content-Type', res.headers.get('Content-Type') || 'application/json');
    out.set('Cache-Control', 'no-store');
    return new Response(res.body, { status: res.status, headers: out });
  }
};

/**
 * ALLOW_ORIGIN kosong -> '*'. Isi dengan origin dashboard (boleh
 * dipisah koma) untuk mempersempit. Gate sebenarnya tetap DASH_TOKEN;
 * ini lapisan tambahan supaya tab acak tidak ikut bisa memanggil.
 */
function corsHeaders(env, origin) {
  const raw = (env.ALLOW_ORIGIN || '').trim();
  let allow = '*';
  if (raw) {
    const list = raw.split(',').map(s => s.trim()).filter(Boolean);
    allow = list.includes(origin) ? origin : list[0];
  }
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'X-N8N-API-KEY,Content-Type,Accept',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  };
}

/** Perbandingan waktu-konstan supaya token tidak bisa ditebak lewat timing. */
function safeEqual(a, b) {
  const ea = new TextEncoder().encode(a);
  const eb = new TextEncoder().encode(b);
  if (ea.length !== eb.length) return false;
  let diff = 0;
  for (let i = 0; i < ea.length; i++) diff |= ea[i] ^ eb[i];
  return diff === 0;
}

function json(obj, status, extra) {
  const h = new Headers(extra || {});
  h.set('Content-Type', 'application/json');
  h.set('Cache-Control', 'no-store');
  return new Response(JSON.stringify(obj), { status, headers: h });
}
