// ============================================================
// GLOBAL - Send WA (failover)
// Satu-satunya pintu keluar WhatsApp untuk seluruh workflow VIRA.
//
// LATAR BELAKANG (2026-08-31):
// Kirimi memblokir IP server n8n (76.13.18.214) dengan respons
//   {"success":false,"data":null,"message":"Access denied. Your IP has been blocked..."}
// Enam node menembak Kirimi langsung, hardcoded, tanpa cadangan -> seluruh bot mati,
// termasuk notifikasi errornya sendiri. Node lama juga membuang body respons,
// sehingga penyebabnya baru ketahuan setelah berjam-jam menebak.
//
// YANG DIPERBAIKI DI SINI:
//  1. Rantai provider. Gagal di satu provider -> lanjut ke berikutnya, otomatis.
//  2. Circuit breaker. Provider yang membalas 401/403 diistirahatkan 10 menit,
//     supaya kita tidak menghantam layanan yang sedang memblokir kita -- itu
//     persis yang memicu blokir kemarin.
//  3. Retry hanya untuk kegagalan transient (5xx/408/429/jaringan). 4xx TIDAK
//     di-retry karena permanen; mengulanginya cuma menambah jejak abuse.
//  4. Body respons SELALU ikut dilaporkan. Ini yang kemarin hilang.
//  5. Kredensial semua provider terkumpul di satu tempat (blok PROVIDERS di bawah).
//
// KONTRAK:
//   input  : { phone, message, context }
//   sukses : [{ json: { ok:true, provider, response, attempts, context } }]
//   gagal  : throw berisi ringkasan SEMUA percobaan -> execution merah ->
//            Error Notifier jalan -> bisa di-retry dari dashboard mobile.
//
// CATATAN RETRY n8n: node pemanggil (Execute Workflow) harus dibiarkan
// On Error = Stop Workflow. Karena kirim + verifikasi ada di dalam satu
// sub-workflow, satu klik Retry benar-benar mengirim ulang -- bukan sekadar
// memvalidasi ulang respons lama.
// ============================================================

const input   = $input.first().json || {};
const phone   = String(input.phone == null ? '' : input.phone).trim();
const message = String(input.message == null ? '' : input.message);
const context = String(input.context || 'tanpa-konteks');

if (!phone)          { throw new Error('Send WA: nomor tujuan kosong (context: ' + context + ')'); }
if (!message.trim()) { throw new Error('Send WA: pesan kosong (context: ' + context + ')'); }

// ============================================================
// KONFIGURASI PROVIDER -- urut prioritas, atas duluan.
// Untuk mengganti provider utama, cukup pindahkan urutannya di array ini.
// Ini SATU-SATUNYA tempat kredensial WhatsApp disimpan sekarang.
// ============================================================
const enc = (o) => Object.keys(o)
  .map((k) => encodeURIComponent(k) + '=' + encodeURIComponent(o[k]))
  .join('&');

const PROVIDERS = [
  {
    name: 'kirimi',
    enabled: true,
    maxChars: 60000,
    build: () => ({
      method: 'POST',
      url: 'https://api.kirimi.id/v1/send-message',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        user_code: 'KM40LI0426',
        secret: 'REDACTED',
        device_id: 'D-4ZV1F',
        receiver: phone, // nama field sesuai docs Kirimi per Agustus 2026
        phone: phone,    // dipertahankan kalau-kalau Kirimi rollback
        message: message,
      }),
    }),
    ok: (r) => {
      if (!r || typeof r !== 'object') { return false; }
      if (r.success === false || r.status === false) { return false; }
      return r.status === true || r.success === true ||
             !!(r.data && r.data.id) || !!(r.message && r.message !== 'error');
    },
  },
  {
    // ISI TOKEN LALU UBAH enabled MENJADI true.
    // Token: dashboard Fonnte -> Device -> Token.
    name: 'fonnte',
    enabled: false,
    maxChars: 60000,
    build: () => ({
      method: 'POST',
      url: 'https://api.fonnte.com/send',
      headers: {
        'Authorization': 'ISI_TOKEN_FONNTE_DI_SINI',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
      },
      body: enc({ target: phone, message: message, countryCode: '62' }),
    }),
    ok: (r) => !!(r && r.status === true),
  },
];

// ============================================================
// Circuit breaker -- state bertahan antar eksekusi lewat static data.
// Kalau static data tidak tersedia, sistem tetap jalan tanpa breaker
// (degradasi lunak, bukan error).
// ============================================================
const COOLDOWN_MS = 10 * 60 * 1000;
const now = Date.now();

let store = null;
try { store = $getWorkflowStaticData('global'); } catch (e) { store = null; }
if (store && !store.cb) { store.cb = {}; }

const cooldownUntil = (name) => (store && store.cb && store.cb[name]) ? store.cb[name].until : 0;
const inCooldown    = (name) => cooldownUntil(name) > now;
const tripBreaker   = (name, why) => {
  if (store && store.cb) { store.cb[name] = { until: now + COOLDOWN_MS, why: String(why).slice(0, 120) }; }
};
const resetBreaker  = (name) => { if (store && store.cb) { delete store.cb[name]; } };

// ============================================================
// Helper HTTP
// ============================================================
const MAX_TRIES = 2;   // hanya untuk kegagalan transient
const WAIT_MS   = 4000;
const TIMEOUT   = 60000;

const sleep = (ms) => new Promise((r) => {
  if (typeof setTimeout === 'function') { setTimeout(r, ms); } else { r(); }
});

// Bentuk objek error httpRequest berbeda-beda antar versi n8n/axios.
// Semua jalur yang mungkin dicoba supaya body aslinya tidak pernah hilang lagi.
const digErr = (e) => {
  const st = (e && (e.httpCode
    || (e.response && (e.response.status || e.response.statusCode))
    || (e.cause && e.cause.response && e.cause.response.status))) || null;
  const raw = (e && (
    (e.response && (e.response.body || e.response.data))
    || (e.cause && e.cause.response && e.cause.response.data)
    || e.errorResponse)) || null;
  let body = '';
  try { body = (typeof raw === 'string') ? raw : JSON.stringify(raw); }
  catch (_) { body = String(raw); }
  return { status: st === null ? null : Number(st), body: String(body || '').slice(0, 400) };
};

const parseBody = (raw) => {
  if (raw && typeof raw === 'object') { return raw; }
  if (typeof raw === 'string') {
    try { return JSON.parse(raw); } catch (_) { return { raw: raw.slice(0, 400) }; }
  }
  return {};
};

// 5xx / 408 / 429 / gangguan jaringan = layak diulang.
// 401 / 403 / 404 / 400 = permanen, jangan diulang.
const isTransient = (s) => s === null || s >= 500 || s === 408 || s === 429;
const isHardBlock = (s) => s === 401 || s === 403;

const trySend = async (p) => {
  let info = { status: null, body: '' };
  let lastMsg = '';

  for (let i = 1; i <= MAX_TRIES; i++) {
    try {
      const opts = p.build();
      opts.json = false;          // parsing respons ditangani manual
      opts.timeout = TIMEOUT;
      const raw  = await this.helpers.httpRequest(opts);
      const resp = parseBody(raw);

      if (p.ok(resp)) {
        return { provider: p.name, ok: true, status: 200, response: resp, tries: i };
      }
      // HTTP 200 tapi isi respons menolak -> jangan diulang otomatis,
      // risiko pesan dobel. Lanjut ke provider berikutnya saja.
      return {
        provider: p.name, ok: false, status: 200, hardBlock: false,
        body: JSON.stringify(resp).slice(0, 300),
        error: 'HTTP 200 tapi respons menolak', tries: i,
      };
    } catch (e) {
      info = digErr(e);
      lastMsg = (e && e.message) ? e.message : String(e);
      console.log('[' + p.name + '] percobaan ' + i + '/' + MAX_TRIES +
        ' gagal | HTTP ' + (info.status === null ? '?' : info.status) + ' | ' + lastMsg);
      console.log('[' + p.name + '] respons mentah: ' + (info.body || '(kosong)'));

      if (!isTransient(info.status)) { break; }
      if (i < MAX_TRIES) { await sleep(WAIT_MS); }
    }
  }

  return {
    provider: p.name, ok: false, status: info.status,
    hardBlock: isHardBlock(info.status),
    body: info.body, error: lastMsg, tries: MAX_TRIES,
  };
};

// ============================================================
// Rantai failover
// ============================================================
const attempts = [];
let sent = null;

for (const p of PROVIDERS) {
  if (!p.enabled) {
    attempts.push({ provider: p.name, skipped: 'dinonaktifkan di konfigurasi' });
    continue;
  }
  if (inCooldown(p.name)) {
    const sisa = Math.ceil((cooldownUntil(p.name) - now) / 1000);
    attempts.push({ provider: p.name, skipped: 'circuit breaker aktif, sisa ' + sisa + ' detik' });
    continue;
  }
  if (message.length > p.maxChars) {
    attempts.push({ provider: p.name, skipped: 'pesan ' + message.length + ' char melebihi batas ' + p.maxChars });
    continue;
  }

  const res = await trySend(p);
  attempts.push(res);

  if (res.ok) { sent = res; resetBreaker(p.name); break; }
  if (res.hardBlock) {
    tripBreaker(p.name, 'HTTP ' + res.status + ': ' + (res.body || res.error));
    console.log('[' + p.name + '] diistirahatkan 10 menit (HTTP ' + res.status + ')');
  }
}

if (!sent) {
  const rincian = attempts.map((a) => {
    if (a.skipped) { return '  - ' + a.provider + ': DILEWATI (' + a.skipped + ')'; }
    return '  - ' + a.provider + ': HTTP ' + (a.status === null ? '?' : a.status) +
           ' | ' + (a.body || a.error || '(tanpa detail)');
  }).join('\n');

  throw new Error(
    'Send WA GAGAL di SEMUA provider\n' +
    'context : ' + context + '\n' +
    'tujuan  : ' + phone + '\n' +
    'panjang : ' + message.length + ' karakter\n' +
    'percobaan:\n' + rincian
  );
}

console.log('Send WA sukses via ' + sent.provider + ' (context: ' + context + ')');

return [{
  json: {
    ok: true,
    provider: sent.provider,
    response: sent.response,
    attempts: attempts,
    context: context,
  },
}];
