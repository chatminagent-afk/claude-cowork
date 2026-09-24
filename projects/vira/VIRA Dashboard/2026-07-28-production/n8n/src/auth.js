/* ============================================================================
 * auth.js — TOKEN SESI & PENJAGAAN LOGIN (fungsi murni)
 *
 * Kriptografinya sendiri (SHA-256 & HMAC-SHA256) dikerjakan oleh node Crypto
 * bawaan n8n, BUKAN di sini — supaya tidak bergantung pada `require('crypto')`
 * yang di banyak instance n8n diblokir (NODE_FUNCTION_ALLOW_BUILTIN).
 * File ini hanya mengurus encoding, klaim, dan perbandingan.
 *
 * Bentuk token:  base64url(JSON klaim) + "." + hmacSha256Hex(payload, SECRET)
 * Klaim:         { u: username, r: role, t: tenantAktif, ts: [tenant...], exp, n }
 *
 * Kenapa ditandatangani: token disimpan di localStorage browser. Tanpa tanda
 * tangan, siapa pun bisa mengubah "t" dari persada -> thescholars dan membaca
 * data tenant lain. Server memverifikasi tanda tangan pada SETIAP request.
 * ========================================================================== */
'use strict';

/* ------------------------------------------------------------- base64url */

function vaB64uEncode(str) {
  var b64;
  if (typeof Buffer !== 'undefined' && Buffer.from) {
    b64 = Buffer.from(str, 'utf8').toString('base64');
  } else {
    var bytes = new TextEncoder().encode(str);
    var bin = '';
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    b64 = btoa(bin);
  }
  return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function vaB64uDecode(s) {
  var b64 = String(s).replace(/-/g, '+').replace(/_/g, '/');
  while (b64.length % 4 !== 0) b64 += '=';
  if (typeof Buffer !== 'undefined' && Buffer.from) {
    return Buffer.from(b64, 'base64').toString('utf8');
  }
  var bin = atob(b64);
  var bytes = new Uint8Array(bin.length);
  for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}

/* ------------------------------------------------------------ token util */

/** Susun bagian payload token (yang akan di-HMAC oleh node Crypto). */
function vaBuildClaims(user, tenantId, nowSec, ttlSec, nonce) {
  return {
    u: user.username,
    d: user.display,
    r: user.role,
    t: tenantId,
    ts: user.tenants.slice(),
    iat: nowSec,
    exp: nowSec + ttlSec,
    n: nonce
  };
}

function vaEncodeClaims(claims) {
  return vaB64uEncode(JSON.stringify(claims));
}

/** Pisah "payload.sig". Return null kalau bentuknya bukan token. */
function vaSplitToken(token) {
  var s = String(token === null || token === undefined ? '' : token);
  if (s === '') return null;
  var i = s.lastIndexOf('.');
  if (i <= 0 || i === s.length - 1) return null;
  var payload = s.slice(0, i);
  var sig = s.slice(i + 1);
  if (!/^[A-Za-z0-9\-_]+$/.test(payload)) return null;
  if (!/^[a-f0-9]{64}$/i.test(sig)) return null;
  return { payload: payload, sig: sig.toLowerCase() };
}

function vaDecodeClaims(payload) {
  try {
    var obj = JSON.parse(vaB64uDecode(payload));
    if (!obj || typeof obj !== 'object') return null;
    return obj;
  } catch (e) {
    return null;
  }
}

/** Perbandingan waktu-konstan untuk hex digest. */
function vaSafeEqual(a, b) {
  var x = String(a || ''), y = String(b || '');
  if (x.length !== y.length) return false;
  var diff = 0;
  for (var i = 0; i < x.length; i++) diff |= (x.charCodeAt(i) ^ y.charCodeAt(i));
  return diff === 0;
}

/**
 * Validasi klaim SETELAH tanda tangan terbukti cocok.
 * Mengembalikan { ok, reason }.
 */
function vaCheckClaims(claims, nowSec, tenantsRegistry, usersRegistry) {
  if (!claims) return { ok: false, reason: 'TOKEN_MALFORMED' };
  if (typeof claims.exp !== 'number' || claims.exp <= nowSec) {
    return { ok: false, reason: 'TOKEN_EXPIRED' };
  }
  var user = usersRegistry ? usersRegistry[claims.u] : null;
  if (!user) return { ok: false, reason: 'USER_UNKNOWN' };

  // Akun yang perannya/aksesnya diubah setelah token terbit tidak boleh lolos
  // hanya karena tokennya masih berlaku.
  if (user.role !== claims.r) return { ok: false, reason: 'ROLE_CHANGED' };
  if (user.tenants.indexOf(claims.t) === -1) return { ok: false, reason: 'TENANT_FORBIDDEN' };
  if (tenantsRegistry && !tenantsRegistry[claims.t]) return { ok: false, reason: 'TENANT_UNKNOWN' };

  return { ok: true, reason: '' };
}

/**
 * Apakah user boleh berpindah ke tenant target.
 * Owner terkunci ke daftar tenant-nya; super boleh semua yang terdaftar.
 */
function vaCanUseTenant(user, tenantId) {
  if (!user || !tenantId) return false;
  return user.tenants.indexOf(tenantId) !== -1;
}

/* -------------------------------------------------------- penjaga login */

/**
 * Lockout sederhana berbasis workflow static data.
 *
 * CATATAN JUJUR: static data n8n di-persist saat eksekusi SELESAI, jadi dua
 * percobaan login yang benar-benar bersamaan bisa saling menimpa hitungannya.
 * Ini memperlambat brute force, bukan mencegahnya secara mutlak — pertahanan
 * utamanya tetap panjang & keacakan password (16 karakter alfanumerik).
 */
function vaLoginGate(state, username, nowSec, settings) {
  var rec = state[username];
  if (!rec) return { blocked: false, remain: 0 };
  if (rec.until && rec.until > nowSec) {
    return { blocked: true, remain: rec.until - nowSec };
  }
  return { blocked: false, remain: 0 };
}

function vaLoginFail(state, username, nowSec, settings) {
  var rec = state[username];
  if (!rec || !rec.first || (nowSec - rec.first) > settings.loginWindowSec) {
    rec = { first: nowSec, fails: 0, until: 0 };
  }
  rec.fails += 1;
  if (rec.fails >= settings.loginMaxFail) {
    rec.until = nowSec + settings.loginWindowSec;
  }
  state[username] = rec;
  return rec;
}

function vaLoginOk(state, username) {
  delete state[username];
  return state;
}

/* ------------------------------------------------------------------ CORS */

/**
 * Hanya origin yang terdaftar yang dipantulkan balik. Tidak pernah "*",
 * karena "*" akan membuat halaman mana pun di internet bisa memanggil API ini
 * dengan token yang dicuri dari localStorage lewat XSS di situs lain.
 */
function vaCorsOrigin(origin, allowlist) {
  var o = String(origin || '');
  for (var i = 0; i < allowlist.length; i++) {
    if (allowlist[i] === o) return o;
  }
  return allowlist.length ? allowlist[0] : '';
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    vaB64uEncode: vaB64uEncode, vaB64uDecode: vaB64uDecode,
    vaBuildClaims: vaBuildClaims, vaEncodeClaims: vaEncodeClaims,
    vaSplitToken: vaSplitToken, vaDecodeClaims: vaDecodeClaims,
    vaSafeEqual: vaSafeEqual, vaCheckClaims: vaCheckClaims,
    vaCanUseTenant: vaCanUseTenant,
    vaLoginGate: vaLoginGate, vaLoginFail: vaLoginFail, vaLoginOk: vaLoginOk,
    vaCorsOrigin: vaCorsOrigin
  };
}
