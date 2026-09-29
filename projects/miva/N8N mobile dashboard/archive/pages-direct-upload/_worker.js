/**
 * n8n Ops — static host + authenticated edge proxy.
 *
 * Dua tugas:
 *   1. Melayani dashboard (public/index.html) di semua path biasa.
 *   2. Mem-proxy /n8n/api/v1/* ke instance n8n, sambil menyuntikkan
 *      X-N8N-API-KEY di sisi server.
 *
 * Karena dashboard dan proxy berada di origin yang sama, browser tidak
 * pernah melakukan request cross-origin — jadi tidak ada CORS sama sekali.
 *
 * Browser mengirim DASH_TOKEN (bukan API key n8n) lewat header X-N8N-API-KEY.
 * Worker memvalidasinya, lalu menukarnya dengan N8N_API_KEY yang asli.
 * Konsekuensinya: kalau HP hilang, yang bocor cuma token dashboard yang bisa
 * kamu cabut dari Cloudflare tanpa menyentuh n8n.
 */

const API_PREFIX = '/n8n';
const UPSTREAM_ALLOWED = '/api/v1/';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // --- 1. bukan request proxy -> layani file statis ---
    if (!url.pathname.startsWith(API_PREFIX + '/')) {
      return env.ASSETS.fetch(request);
    }

    // --- 2. batasi ke Public API saja ---
    const upstreamPath = url.pathname.slice(API_PREFIX.length);
    if (!upstreamPath.startsWith(UPSTREAM_ALLOWED)) {
      return json({ message: 'Hanya /api/v1/* yang di-proxy.' }, 403);
    }

    // --- 3. auth: token dashboard, bukan API key n8n ---
    if (!env.DASH_TOKEN) {
      return json({ message: 'Worker belum dikonfigurasi: DASH_TOKEN kosong.' }, 500);
    }
    if (!safeEqual(request.headers.get('X-N8N-API-KEY') || '', env.DASH_TOKEN)) {
      return json({ message: 'Dashboard token salah.' }, 401);
    }
    if (!env.N8N_API_KEY || !env.N8N_BASE) {
      return json({ message: 'Worker belum dikonfigurasi: N8N_BASE / N8N_API_KEY kosong.' }, 500);
    }

    // --- 4. teruskan ke n8n dengan kredensial asli ---
    const target = env.N8N_BASE.replace(/\/+$/, '') + upstreamPath + url.search;

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
      return json({ message: 'n8n tidak bisa dihubungi: ' + err.message }, 502);
    }

    // Salin hanya header yang aman — jangan teruskan Set-Cookie dari n8n.
    const out = new Headers({
      'Content-Type': res.headers.get('Content-Type') || 'application/json',
      'Cache-Control': 'no-store'
    });
    return new Response(res.body, { status: res.status, headers: out });
  }
};

/** Perbandingan waktu-konstan supaya token tidak bisa ditebak lewat timing. */
function safeEqual(a, b) {
  const ea = new TextEncoder().encode(a);
  const eb = new TextEncoder().encode(b);
  if (ea.length !== eb.length) return false;
  let diff = 0;
  for (let i = 0; i < ea.length; i++) diff |= ea[i] ^ eb[i];
  return diff === 0;
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
  });
}
