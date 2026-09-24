#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_workflow.py — merakit "VIRA Dashboard API.json" dari modul di src/.

Kenapa dirakit, bukan ditulis tangan:
  Kode di src/*.js dipakai DUA kali — di dalam Code node n8n dan di dalam
  qa/selftest.html. Kalau workflow ditulis tangan, dua salinan itu pasti
  akan berbeda pelan-pelan (dan bug yang lolos QA justru yang di produksi).
  Script ini menjadikan src/ satu-satunya sumber kebenaran.

Jalankan ulang setiap kali src/*.js berubah:
    python n8n/build_workflow.py
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.join(HERE, 'VIRA-Dashboard-API.json')

# ---------------------------------------------------------------- rahasia --
# Kunci HMAC penanda tangan token sesi. Bukan kredensial pihak ketiga —
# hanya dipakai workflow ini untuk menandatangani & memverifikasi tokennya
# sendiri. Menggantinya = semua sesi yang berjalan langsung tidak berlaku.
HMAC_SECRET = '3b5c294243318b3c0ef02604e00712d7a7b87d95b88b4d595db1876887f5db0f'

# Kredensial Google Sheets KHUSUS dashboard (service account terpisah dari bot,
# supaya kuota 60 read/menit dashboard tidak memakan jatah bot).
# Setelah import, buka tiap node Google Sheets dan pilih credential yang benar —
# id di bawah sengaja placeholder supaya kesalahan pilih tidak mungkin senyap.
GOOGLE_CRED_ID = '5KD9A3Tef1H8UQKk'
GOOGLE_CRED_NAME = 'Google Service Account - VIRA Dashboard'

WEBHOOK_PATH = 'vira-dash'
WEBHOOK_ID = 'a7c1f5e2-4b90-4d3a-9f61-2e8c0d7b45aa'


# ------------------------------------------------------------------ utils --

def read_src(name):
    """Baca modul src/ dan buang blok module.exports (tidak dipakai di n8n)."""
    with open(os.path.join(SRC, name), 'r', encoding='utf-8') as f:
        code = f.read()
    code = re.sub(
        r"\nif \(typeof module !== 'undefined'.*?\n\}\n?$",
        '\n', code, flags=re.S)
    return code.rstrip() + '\n'


LIB_TENANTS = read_src('tenants.js')
LIB_AUTH = read_src('auth.js')
LIB_PAYLOAD = read_src('build-payload.js')

# Daftar kolom hasil resolusi n8n dari spreadsheet sungguhan, diambil dari
# workflow yang sudah jalan oleh n8n/sync_sheets_schema.py.
#
# Tidak bisa ditebak dari kode: field Document/Sheet diisi ekspresi, jadi n8n
# tidak tahu spreadsheet mana yang dimaksud sampai node benar-benar dieksekusi.
# Tanpa berkas ini, setiap import menimpa hasil resolusi itu dengan kosong dan
# orang yang deploy harus mengulang ritual eksekusi-Retry-publish per node.
SHEETS_SCHEMA = {}
_schema_path = os.path.join(HERE, 'sheets-schema.json')
if os.path.exists(_schema_path):
    with open(_schema_path, 'r', encoding='utf-8') as _f:
        SHEETS_SCHEMA = json.load(_f)


BANNER = (
    "// === DI-GENERATE OLEH n8n/build_workflow.py — JANGAN EDIT DI UI n8n ===\n"
    "// Sumbernya ada di n8n/src/*.js. Edit di sana lalu jalankan ulang script.\n"
)


def code_node(name, js, position, always_output=False, on_error=None):
    node = {
        'parameters': {'jsCode': BANNER + js},
        'id': name.lower().replace(' ', '-'),
        'name': name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': position,
    }
    if always_output:
        node['alwaysOutputData'] = True
    if on_error:
        node['onError'] = on_error
    return node


def sheets_read(name, position):
    return {
        'parameters': {
            # WAJIB. Tanpa baris ini node memakai OAuth2 (bawaannya), padahal
            # credential yang dipasang bertipe service account — dan node tidak
            # pernah tersambung ke kredensial yang benar.
            'authentication': 'serviceAccount',
            'documentId': {'__rl': True, 'value': '={{ $json.doc_id }}', 'mode': 'id'},
            'sheetName': {'__rl': True, 'value': '={{ $json.tab }}', 'mode': 'name'},
            'options': {},
        },
        'id': name.lower().replace(' ', '-'),
        'name': name,
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.5,
        'position': position,
        'alwaysOutputData': True,
        'onError': 'continueRegularOutput',
        'credentials': {'googleApi': {'id': GOOGLE_CRED_ID, 'name': GOOGLE_CRED_NAME}},
    }


def sheets_append(name, position, doc_expr, tab_expr, mapping,
                  on_error=None, always_output=False):
    """Node Google Sheets `append` LENGKAP dengan blok `schema`.

    `schema` wajib ada. Node append tanpa blok itu adalah bentuk yang belum
    pernah terbukti bekerja di instalasi ini: satu-satunya contohnya di repo
    (`Append Audit` versi lama) memakai onError yang menelan kegagalan, jadi
    kalau selama ini gagal pun tidak ada yang tahu. Sebaliknya, SEMUA node
    append yang benar-benar jalan di produksi — termasuk `Append Audit` di
    `live production/VIRA Dashboard API.json` — membawa schema, matchingColumns,
    attemptToConvertTypes, dan convertFieldsToString.

    n8n mengisi blok ini sendiri kalau node dibuka lewat UI. Karena workflow ini
    di-generate dan tidak pernah disentuh UI, blok itu harus ikut ditulis di
    sini — kalau tidak, setiap import justru MENGGANTI node yang sudah bekerja
    dengan bentuk yang tidak bekerja.
    """
    # Blok schema nyata hasil resolusi n8n kalau sudah disinkronkan; kalau
    # belum, dilewati saja — node Update Bot Mode membuktikan operasi tulis
    # tetap bekerja tanpa blok itu.
    cols = SHEETS_SCHEMA.get(name)
    node = {
        'parameters': {
            'authentication': 'serviceAccount',
            'operation': 'append',
            'documentId': {'__rl': True, 'value': doc_expr, 'mode': 'id'},
            'sheetName': {'__rl': True, 'value': tab_expr, 'mode': 'name'},
            'columns': {
                'mappingMode': 'defineBelow',
                'value': mapping,
                'matchingColumns': [],
                'schema': cols if cols else [],
                'attemptToConvertTypes': False,
                'convertFieldsToString': False,
            },
            'options': {},
        },
        'id': name.lower().replace(' ', '-').replace('(', '').replace(')', ''),
        'name': name,
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.5,
        'position': position,
        'credentials': {'googleApi': {'id': GOOGLE_CRED_ID, 'name': GOOGLE_CRED_NAME}},
    }
    if always_output:
        node['alwaysOutputData'] = True
    if on_error:
        node['onError'] = on_error
    return node


# ------------------------------------------------------------ kode per node --

JS_PARSE_REQUEST = LIB_TENANTS + LIB_AUTH + r"""
/* -------------------------------------------------------------------------
 * Parse Request — pintu masuk. Menentukan action, CORS, dan (untuk login)
 * menyiapkan string yang akan di-hash node Crypto berikutnya.
 * Node ini TIDAK PERNAH mempercayai apa pun dari body selain bentuknya.
 * ---------------------------------------------------------------------- */
const item = $input.first().json || {};
const headers = item.headers || {};
const origin = headers.origin || headers.Origin || '';
const cors = vaCorsOrigin(origin, VIRA_SETTINGS.corsOrigins);
const nowSec = Math.floor(Date.now() / 1000);

function fail(code, message, action) {
  return [{ json: {
    _route: 'error', _cors: cors,
    _response: { ok: false, action: action || 'unknown', error: code, message: message }
  }}];
}

/* Body datang sebagai text/plain (lihat API contract §1). n8n bisa
 * menyerahkannya dalam beberapa bentuk tergantung versi & proxy, jadi
 * ketiganya ditangani daripada gagal misterius di produksi. */
let req = null;
const raw = item.body;
try {
  if (typeof raw === 'string') {
    req = JSON.parse(raw);
  } else if (raw && typeof raw === 'object') {
    if (typeof raw.data === 'string') {
      req = JSON.parse(raw.data);
    } else {
      const keys = Object.keys(raw);
      // form-urlencoded palsu: seluruh JSON jadi satu key kosong
      if (keys.length === 1 && raw[keys[0]] === '' && keys[0].charAt(0) === '{') {
        req = JSON.parse(keys[0]);
      } else {
        req = raw;
      }
    }
  }
} catch (e) { req = null; }

if (!req || typeof req !== 'object') {
  return fail('BAD_REQUEST', 'Permintaan tidak dapat dibaca.');
}

const action = String(req.action || '').trim();
const AUTHED = ['me', 'switch_tenant', 'stats', 'toggle_user', 'add_lead'];

if (action === 'login') {
  const username = String(req.username || '').trim().toLowerCase();
  const password = String(req.password || '');
  if (username === '' || password === '') {
    return fail('BAD_CREDENTIALS', 'Username dan password wajib diisi.', 'login');
  }

  const store = $getWorkflowStaticData('global');
  if (!store.loginState) store.loginState = {};
  const gate = vaLoginGate(store.loginState, username, nowSec, VIRA_SETTINGS);
  if (gate.blocked) {
    const menit = Math.ceil(gate.remain / 60);
    return fail('LOCKED_OUT',
      'Terlalu banyak percobaan gagal. Coba lagi dalam ' + menit + ' menit.', 'login');
  }

  const user = VIRA_USERS[username] || null;
  // Username tak dikenal tetap melewati jalur hash yang sama supaya waktu
  // responsnya tidak membocorkan username mana yang terdaftar.
  const salt = user ? user.salt : 'no-such-user';

  return [{ json: {
    _route: 'login', _cors: cors, _action: 'login',
    _username: username, _userKnown: !!user,
    _pwInput: salt + ':' + password,
    _nowSec: nowSec
  }}];
}

if (AUTHED.indexOf(action) !== -1) {
  const parts = vaSplitToken(req.token);
  if (!parts) {
    return fail(req.token ? 'TOKEN_MALFORMED' : 'TOKEN_MISSING',
      'Sesi tidak valid. Silakan login ulang.', action);
  }
  return [{ json: {
    _route: 'auth', _cors: cors, _action: action,
    _payloadPart: parts.payload, _sigGiven: parts.sig,
    _nowSec: nowSec,
    _req: {
      tenant: String(req.tenant || ''),
      key: String(req.key || ''),
      mode: String(req.mode || '').trim().toUpperCase(),
      // Dipakai action add_lead. Dipotong di sini juga, bukan hanya di node
      // berikutnya, supaya body raksasa tidak terbawa ke seluruh jalur.
      nama: String(req.nama || '').trim().slice(0, 120),
      fresh: req.fresh === true
    }
  }}];
}

return fail('BAD_REQUEST', 'Perintah tidak dikenal.', action || 'unknown');
"""

JS_VERIFY_LOGIN = LIB_TENANTS + LIB_AUTH + r"""
/* -------------------------------------------------------------------------
 * Verify Login — membandingkan hash yang dihitung node Crypto dengan hash
 * tersimpan, lalu menyiapkan klaim untuk ditandatangani.
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const cors = j._cors;
const nowSec = j._nowSec;
const store = $getWorkflowStaticData('global');
if (!store.loginState) store.loginState = {};

const user = j._userKnown ? VIRA_USERS[j._username] : null;
const okPw = !!user && vaSafeEqual(String(j._pwHash || '').toLowerCase(), user.hash);

if (!okPw) {
  vaLoginFail(store.loginState, j._username, nowSec, VIRA_SETTINGS);
  return [{ json: {
    _route: 'error', _cors: cors,
    _response: { ok: false, action: 'login', error: 'BAD_CREDENTIALS',
                 message: 'Username atau password salah.' }
  }}];
}

vaLoginOk(store.loginState, j._username);

// Tenant awal = tenant pertama yang boleh diakses akun ini.
const tenantId = user.tenants[0];
const nonce = String(nowSec) + '-' + Math.floor(Math.random() * 1e9).toString(36);
const claims = vaBuildClaims(user, tenantId, nowSec, VIRA_SETTINGS.tokenTtlSec, nonce);

return [{ json: {
  _route: 'sign', _cors: cors, _action: 'login',
  _claimsB64: vaEncodeClaims(claims), _claims: claims
}}];
"""

JS_CHECK_TOKEN = LIB_TENANTS + LIB_AUTH + r"""
/* -------------------------------------------------------------------------
 * Check Token — verifikasi tanda tangan HMAC lalu validasi klaim.
 * Inilah satu-satunya tempat yang memutuskan "tenant mana yang boleh dibaca".
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const cors = j._cors;
const action = j._action;

function deny(code, message) {
  return [{ json: {
    _route: 'error', _cors: cors,
    _response: { ok: false, action: action, error: code, message: message }
  }}];
}

if (!vaSafeEqual(String(j._sigCalc || '').toLowerCase(), j._sigGiven)) {
  // Tanda tangan tidak cocok = token dimodifikasi. Tidak ada alasan sah untuk ini.
  return deny('TOKEN_BAD_SIGNATURE', 'Sesi tidak valid. Silakan login ulang.');
}

const claims = vaDecodeClaims(j._payloadPart);
const check = vaCheckClaims(claims, j._nowSec, VIRA_TENANTS, VIRA_USERS);
if (!check.ok) {
  const msg = check.reason === 'TOKEN_EXPIRED'
    ? 'Sesi sudah berakhir. Silakan login ulang.'
    : 'Sesi tidak valid. Silakan login ulang.';
  return deny(check.reason, msg);
}

return [{ json: {
  _route: action, _cors: cors, _action: action,
  _claims: claims, _req: j._req, _nowSec: j._nowSec
}}];
"""

JS_BUILD_ME = LIB_TENANTS + r"""
/* Me — kembalikan identitas sesi tanpa menyentuh Google Sheets sama sekali. */
const j = $input.first().json;
const c = j._claims;
const list = c.ts.map(function (id) {
  return { id: id, name: VIRA_TENANTS[id] ? VIRA_TENANTS[id].name : id };
});
return [{ json: { _cors: j._cors, _response: {
  ok: true, action: 'me',
  session: { username: c.u, display: c.d, role: c.r, tenant: c.t, tenants: list, exp: c.exp }
}}}];
"""

JS_PREPARE_SWITCH = LIB_TENANTS + LIB_AUTH + r"""
/* -------------------------------------------------------------------------
 * Prepare Switch Tenant — hanya role `super`. Hak akses diambil dari registry
 * server (VIRA_USERS), BUKAN dari daftar tenant di dalam token, supaya
 * pencabutan akses langsung berlaku tanpa menunggu token kedaluwarsa.
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const c = j._claims;
const target = String(j._req.tenant || '').trim();
const user = VIRA_USERS[c.u];

function deny(code, message) {
  return [{ json: { _route: 'error', _cors: j._cors,
    _response: { ok: false, action: 'switch_tenant', error: code, message: message } }}];
}

if (!user) return deny('USER_UNKNOWN', 'Akun tidak dikenal.');
if (!VIRA_TENANTS[target]) return deny('TENANT_UNKNOWN', 'Klien tidak dikenal.');
if (!vaCanUseTenant(user, target)) {
  return deny('TENANT_FORBIDDEN', 'Akun ini tidak punya akses ke klien tersebut.');
}

const nonce = String(j._nowSec) + '-' + Math.floor(Math.random() * 1e9).toString(36);
const claims = vaBuildClaims(user, target, j._nowSec, VIRA_SETTINGS.tokenTtlSec, nonce);

return [{ json: {
  _route: 'sign', _cors: j._cors, _action: 'switch_tenant',
  _claimsB64: vaEncodeClaims(claims), _claims: claims
}}];
"""

JS_BUILD_AUTH_RESPONSE = LIB_TENANTS + r"""
/* Build Auth Response — merakit token final dari payload + tanda tangan. */
const j = $input.first().json;
const c = j._claims;
const token = j._claimsB64 + '.' + String(j._sig).toLowerCase();
const list = c.ts.map(function (id) {
  return { id: id, name: VIRA_TENANTS[id] ? VIRA_TENANTS[id].name : id };
});
return [{ json: { _cors: j._cors, _response: {
  ok: true, action: j._action, token: token,
  session: { username: c.u, display: c.d, role: c.r, tenant: c.t, tenants: list, exp: c.exp }
}}}];
"""

JS_CACHE_CHECK = LIB_TENANTS + r"""
/* -------------------------------------------------------------------------
 * Cache Check — pelindung kuota Google Sheets.
 *
 * Bot Persada sudah mendekati plafon 60 read/menit (lihat catatan sesi 4).
 * Dashboard memakai service account terpisah sehingga bucket kuotanya sendiri,
 * tapi cache ini tetap dipasang supaya beberapa owner yang membuka dashboard
 * bersamaan tidak menghasilkan pembacaan berulang yang sia-sia.
 *
 * Set VIRA_SETTINGS.statsCacheSec = 0 untuk mematikan cache.
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const c = j._claims;
const profile = VIRA_TENANTS[c.t];
const store = $getWorkflowStaticData('global');
if (!store.statsCache) store.statsCache = {};

const nowMs = Date.now();
const entry = store.statsCache[c.t];
const ttlMs = (VIRA_SETTINGS.statsCacheSec || 0) * 1000;

let hit = false;
if (ttlMs > 0 && entry && entry.ts && (nowMs - entry.ts) < ttlMs) {
  hit = true;
  // `fresh:true` (tombol Refresh) boleh menembus cache, TAPI tidak dalam 10
  // detik pertama — kalau tidak, menahan tombol Refresh jadi cara menguras
  // kuota Sheets dan menjatuhkan bot.
  if (j._req && j._req.fresh && (nowMs - entry.ts) >= 10000) hit = false;
}

return [{ json: {
  _cors: j._cors, _claims: c, _cacheHit: hit,
  doc_id: profile.sheetId, _tabs: profile.tabs, _nowMs: nowMs
}}];
"""

JS_FAN_OUT = r"""
/* Fan Out Tabs — satu item per tab yang perlu dibaca. Loop di bawah membaca
 * satu per satu supaya identitas tab tidak hilang di output Google Sheets. */
const j = $input.first().json;
const out = [];
for (let i = 0; i < j._tabs.length; i++) {
  out.push({ json: {
    __vd_fanout: true,
    doc_id: j.doc_id,
    tab: j._tabs[i]
  }});
}
return out;
"""

JS_TAG_ROWS = r"""
/* -------------------------------------------------------------------------
 * Tag Rows — menempelkan nama tab ke setiap baris hasil bacaan.
 *
 * Node Google Sheets membuang konteks inputnya, jadi tanpa penandaan ini
 * baris dari empat tab akan tercampur jadi satu tumpukan tanpa identitas.
 * ---------------------------------------------------------------------- */
const tab = $('Loop Over Tabs').first().json.tab;
const rows = $input.all();
const out = [];

for (let i = 0; i < rows.length; i++) {
  const r = rows[i].json || {};
  // Item passthrough saat node Sheets gagal (onError: continueRegularOutput)
  // atau saat tab kosong (alwaysOutputData) — bukan baris data.
  if (r.__vd_fanout === true) continue;
  if (Object.keys(r).length === 0) continue;
  out.push({ json: { _tab: tab, _row: r } });
}

// Loop tetap butuh minimal satu item agar iterasi berlanjut mulus.
if (out.length === 0) out.push({ json: { _tab: tab, _row: null } });
return out;
"""

JS_COLLECT = r"""
/* Collect Tabs — kelompokkan kembali baris per tab. */
const items = $input.all();
const tabs = {};
for (let i = 0; i < items.length; i++) {
  const j = items[i].json;
  if (!j || !j._tab) continue;
  if (!tabs[j._tab]) tabs[j._tab] = [];
  if (j._row) tabs[j._tab].push(j._row);
}
return [{ json: { _tabs_data: tabs } }];
"""

JS_BUILD_STATS = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Build Stats Response — satu-satunya tempat data mentah Sheets berubah
 * menjadi kontrak dashboard. Dua jalur masuk: cache hit dan pembacaan segar.
 * ---------------------------------------------------------------------- */
const cacheNode = $('Cache Check').first().json;
const c = cacheNode._claims;
const profile = VIRA_TENANTS[c.t];
const store = $getWorkflowStaticData('global');
if (!store.statsCache) store.statsCache = {};

let payload;

if (cacheNode._cacheHit && store.statsCache[c.t] && store.statsCache[c.t].payload) {
  payload = store.statsCache[c.t].payload;
  payload.cached = true;
} else {
  let tabsData = {};
  try {
    tabsData = $input.first().json._tabs_data || {};
  } catch (e) {
    tabsData = {};
  }
  payload = vdBuildPayload(profile, tabsData, { nowMs: Date.now(), cached: false });

  // Cache disimpan di workflow static data. Payload besar (ratusan lead) ikut
  // ditulis ke database n8n tiap kali menyegar, jadi ada batas atas supaya
  // tenant yang tumbuh tidak diam-diam membebani instance.
  try {
    const size = JSON.stringify(payload).length;
    if (VIRA_SETTINGS.statsCacheSec > 0 && size < 1500000) {
      store.statsCache[c.t] = { ts: Date.now(), payload: payload };
    } else if (size >= 1500000) {
      store.statsCache[c.t] = null;
      console.log('Payload ' + c.t + ' ' + size + ' byte — terlalu besar untuk cache, dilewati.');
    }
  } catch (e) {
    console.log('Gagal menyimpan cache: ' + e.message);
  }
}

return [{ json: { _cors: cacheNode._cors, _response: payload } }];
"""

JS_PREPARE_TOGGLE = LIB_TENANTS + r"""
/* -------------------------------------------------------------------------
 * Prepare Toggle — menerjemahkan permintaan client menjadi target sheet.
 * Client TIDAK PERNAH menyebut spreadsheet; tenant diambil dari token.
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const c = j._claims;
const profile = VIRA_TENANTS[c.t];
const mode = j._req.mode;
const key = String(j._req.key || '').trim();

if (mode !== 'ON' && mode !== 'OFF') {
  return [{ json: { _route: 'error', _cors: j._cors,
    _response: { ok: false, action: 'toggle_user', error: 'BAD_REQUEST',
                 message: 'Mode harus ON atau OFF.' } }}];
}
if (key === '') {
  return [{ json: { _route: 'error', _cors: j._cors,
    _response: { ok: false, action: 'toggle_user', error: 'BAD_REQUEST',
                 message: 'Nomor tujuan tidak dikirim.' } }}];
}

return [{ json: {
  _cors: j._cors, _claims: c,
  doc_id: profile.sheetId, tab: profile.statsTab,
  audit_tab: VIRA_SETTINGS.auditTab,
  key: key, mode: mode
}}];
"""

JS_FIND_ROW = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Find Row — mencari baris user memakai prinsip yang sama dengan bot:
 * No WA sebagai kunci primer, lid sebagai cadangan, DAN TIDAK PERNAH
 * jatuh ke rows[0]. Kalau tidak ketemu, permintaan ditolak — bukan menulis
 * ke baris asal yang akan mematikan bot untuk orang yang salah.
 * ---------------------------------------------------------------------- */
const prep = $('Prepare Toggle').first().json;
const profile = VIRA_TENANTS[prep._claims.t];
const wantRaw = prep.key;
const want = vdDigits(wantRaw);

const rows = $input.all().map(function (i) { return i.json; })
  .filter(function (r) { return r && typeof r === 'object'; });

let found = null;
for (let i = 0; i < rows.length; i++) {
  if (vdDigits(vdPick(rows[i], profile.map.wa)) === want && want !== '') { found = rows[i]; break; }
}
if (!found && want !== '') {
  for (let i = 0; i < rows.length; i++) {
    if (vdDigits(vdPick(rows[i], profile.map.lid)) === want) { found = rows[i]; break; }
  }
}

if (!found || !found.row_number) {
  return [{ json: { _route: 'error', _cors: prep._cors,
    _response: { ok: false, action: 'toggle_user', error: 'ROW_NOT_FOUND',
      message: 'Nomor ' + wantRaw + ' tidak ditemukan di data. Coba muat ulang dashboard.' } }}];
}

const before = String(vdPick(found, profile.map.bot_mode) || '').toUpperCase() === 'OFF' ? 'OFF' : 'ON';

return [{ json: {
  _route: 'ok', _cors: prep._cors, _claims: prep._claims,
  doc_id: prep.doc_id, tab: prep.tab, audit_tab: prep.audit_tab,
  key: prep.key, mode: prep.mode, before: before,
  row_number: found.row_number,
  ts_iso: new Date().toISOString()
}}];
"""

JS_PREPARE_ADD_LEAD = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Prepare Add Lead — pembungkus tipis di atas vdPrepareAddLead().
 * Seluruh keputusannya ada di src/build-payload.js supaya bisa diuji
 * qa/selftest.html. Node ini hanya mengurus bentuk item n8n.
 *
 * Client TIDAK PERNAH menyebut spreadsheet; tenant diambil dari klaim token.
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const c = j._claims;
const profile = VIRA_TENANTS[c.t];

const res = vdPrepareAddLead(profile, {
  key: j._req.key, nama: j._req.nama, mode: j._req.mode
});

if (!res.ok) {
  return [{ json: { _route: 'error', _cors: j._cors,
    _response: { ok: false, action: 'add_lead',
                 error: res.error, message: res.message } }}];
}

return [{ json: {
  _route: 'ok',
  _cors: j._cors, _claims: c,
  doc_id: profile.sheetId, tab: profile.statsTab,
  audit_tab: VIRA_SETTINGS.auditTab,
  key: res.key, nama: res.nama, mode: res.mode
}}];
"""

JS_FIND_DUPLICATE = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Find Duplicate — pembungkus tipis di atas vdCheckAddLead(), pagar terakhir
 * sebelum baris baru ditulis ke STATS. Lihat komentar fungsinya di
 * src/build-payload.js untuk alasan tiap penolakan.
 * ---------------------------------------------------------------------- */
const prep = $('Prepare Add Lead').first().json;
const profile = VIRA_TENANTS[prep._claims.t];

const rows = $input.all().map(function (i) { return i.json; });
const gate = vdCheckAddLead(profile, rows, prep.key, prep.tab);

if (!gate.ok) {
  return [{ json: { _route: 'error', _cors: prep._cors,
    _response: { ok: false, action: 'add_lead',
                 error: gate.error, message: gate.message } }}];
}

const cells = vdAddLeadCells(prep);

return [{ json: {
  _route: 'ok', _cors: prep._cors, _claims: prep._claims,
  doc_id: prep.doc_id, tab: prep.tab, audit_tab: prep.audit_tab,
  key: prep.key, nama: prep.nama, mode: prep.mode,
  ts_iso: new Date().toISOString(),
  // Nilai yang benar-benar menjadi sel. Awalan col_ memisahkannya dengan
  // jelas dari data kerja di item yang sama.
  col_wa: cells['No WA'],
  col_nama: cells['Nama'],
  col_bot: cells['bot_mode'],
  col_counter: cells['Counter']
}}];
"""

JS_BUILD_ADD_LEAD_RESPONSE = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Build Add Lead Response — membatalkan cache tenant, lalu mengembalikan
 * baris lead siap render lewat vdAddLeadRow() (jalur pembentukan yang sama
 * dengan `stats`, lihat alasannya di src/build-payload.js).
 * ---------------------------------------------------------------------- */
const f = $('Find Duplicate').first().json;
const profile = VIRA_TENANTS[f._claims.t];

const store = $getWorkflowStaticData('global');
if (store.statsCache) store.statsCache[f._claims.t] = null;

const row = vdAddLeadRow(profile, {
  'No WA': f.col_wa, 'Nama': f.col_nama,
  'bot_mode': f.col_bot, 'Counter': f.col_counter
});

const message = f.mode === 'OFF'
  ? 'Nomor ' + f.key + ' ditambahkan dengan bot OFF. VIRA belum akan membalas nomor ini.'
  : 'Nomor ' + f.key + ' ditambahkan dengan bot ON. VIRA akan membalas kalau nomor ini chat.';

return [{ json: { _cors: f._cors, _response: {
  ok: true, action: 'add_lead',
  key: f.key, bot_mode: f.mode, row: row, message: message
}}}];
"""

JS_BUILD_ADD_LEAD_FAILED = r"""
/* -------------------------------------------------------------------------
 * Build Add Lead Failed — cabang error node Append Lead.
 *
 * Ada supaya kegagalan tulis tidak berakhir sebagai request menggantung:
 * karena responseMode = responseNode, eksekusi yang berhenti sebelum Respond
 * membuat browser menunggu sampai timeout tanpa pesan apa pun.
 *
 * Sengaja TIDAK memakai continueRegularOutput: melaporkan "berhasil" padahal
 * baris tidak tertulis jauh lebih berbahaya daripada melaporkan gagal.
 *
 * PESAN ASLI DARI GOOGLE IKUT DIKIRIM. Alasannya konkret: workflow ini disetel
 * saveDataSuccessExecution:'none', dan eksekusi add_lead yang gagal-menulis
 * tetap dihitung SUKSES oleh n8n (ia membalas 200 berisi ok:false). Akibatnya
 * eksekusi itu tidak pernah tersimpan dan errornya tidak bisa dilihat di
 * Executions sama sekali. Tanpa pesan ini, satu-satunya jalan mendiagnosis
 * adalah menebak. Yang membacanya adalah pemilik sheet itu sendiri, dan
 * permintaan ini sudah lolos pemeriksaan token.
 * ---------------------------------------------------------------------- */
const prep = $('Prepare Add Lead').first().json;
const item = $input.first().json || {};

function pickError(o) {
  if (!o) return '';
  if (typeof o === 'string') return o;
  const cand = [
    o.message,
    o.description,
    o.error && o.error.message,
    o.error && o.error.description,
    o.error && o.error.error && o.error.error.message,
    typeof o.error === 'string' ? o.error : ''
  ];
  for (let i = 0; i < cand.length; i++) {
    if (cand[i]) return String(cand[i]);
  }
  try { return JSON.stringify(o); } catch (e) { return ''; }
}

const detail = pickError(item).slice(0, 300);
console.log('Append Lead gagal: ' + detail);

return [{ json: { _cors: prep._cors, _response: {
  ok: false, action: 'add_lead', error: 'WRITE_FAILED',
  detail: detail,
  message: 'Gagal menulis ke Google Sheets, jadi nomor ' + prep.key +
           ' BELUM tersimpan.' + (detail ? ' Kata Google: ' + detail : '')
}}}];
"""

JS_PREPARE_TOGGLE = LIB_TENANTS + r"""
/* -------------------------------------------------------------------------
 * Prepare Toggle — menerjemahkan permintaan client menjadi target sheet.
 * Client TIDAK PERNAH menyebut spreadsheet; tenant diambil dari token.
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const c = j._claims;
const profile = VIRA_TENANTS[c.t];
const mode = j._req.mode;
const key = String(j._req.key || '').trim();

if (mode !== 'ON' && mode !== 'OFF') {
  return [{ json: { _route: 'error', _cors: j._cors,
    _response: { ok: false, action: 'toggle_user', error: 'BAD_REQUEST',
                 message: 'Mode harus ON atau OFF.' } }}];
}
if (key === '') {
  return [{ json: { _route: 'error', _cors: j._cors,
    _response: { ok: false, action: 'toggle_user', error: 'BAD_REQUEST',
                 message: 'Nomor tujuan tidak dikirim.' } }}];
}

return [{ json: {
  _cors: j._cors, _claims: c,
  doc_id: profile.sheetId, tab: profile.statsTab,
  audit_tab: VIRA_SETTINGS.auditTab,
  key: key, mode: mode
}}];
"""

JS_FIND_ROW = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Find Row — mencari baris user memakai prinsip yang sama dengan bot:
 * No WA sebagai kunci primer, lid sebagai cadangan, DAN TIDAK PERNAH
 * jatuh ke rows[0]. Kalau tidak ketemu, permintaan ditolak — bukan menulis
 * ke baris asal yang akan mematikan bot untuk orang yang salah.
 * ---------------------------------------------------------------------- */
const prep = $('Prepare Toggle').first().json;
const profile = VIRA_TENANTS[prep._claims.t];
const wantRaw = prep.key;
const want = vdDigits(wantRaw);

const rows = $input.all().map(function (i) { return i.json; })
  .filter(function (r) { return r && typeof r === 'object'; });

let found = null;
for (let i = 0; i < rows.length; i++) {
  if (vdDigits(vdPick(rows[i], profile.map.wa)) === want && want !== '') { found = rows[i]; break; }
}
if (!found && want !== '') {
  for (let i = 0; i < rows.length; i++) {
    if (vdDigits(vdPick(rows[i], profile.map.lid)) === want) { found = rows[i]; break; }
  }
}

if (!found || !found.row_number) {
  return [{ json: { _route: 'error', _cors: prep._cors,
    _response: { ok: false, action: 'toggle_user', error: 'ROW_NOT_FOUND',
      message: 'Nomor ' + wantRaw + ' tidak ditemukan di data. Coba muat ulang dashboard.' } }}];
}

const before = String(vdPick(found, profile.map.bot_mode) || '').toUpperCase() === 'OFF' ? 'OFF' : 'ON';

return [{ json: {
  _route: 'ok', _cors: prep._cors, _claims: prep._claims,
  doc_id: prep.doc_id, tab: prep.tab, audit_tab: prep.audit_tab,
  key: prep.key, mode: prep.mode, before: before,
  row_number: found.row_number,
  ts_iso: new Date().toISOString()
}}];
"""

JS_PREPARE_ADD_LEAD = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Prepare Add Lead — pembungkus tipis di atas vdPrepareAddLead().
 * Seluruh keputusannya ada di src/build-payload.js supaya bisa diuji
 * qa/selftest.html. Node ini hanya mengurus bentuk item n8n.
 *
 * Client TIDAK PERNAH menyebut spreadsheet; tenant diambil dari klaim token.
 * ---------------------------------------------------------------------- */
const j = $input.first().json;
const c = j._claims;
const profile = VIRA_TENANTS[c.t];

const res = vdPrepareAddLead(profile, {
  key: j._req.key, nama: j._req.nama, mode: j._req.mode
});

if (!res.ok) {
  return [{ json: { _route: 'error', _cors: j._cors,
    _response: { ok: false, action: 'add_lead',
                 error: res.error, message: res.message } }}];
}

return [{ json: {
  _route: 'ok',
  _cors: j._cors, _claims: c,
  doc_id: profile.sheetId, tab: profile.statsTab,
  audit_tab: VIRA_SETTINGS.auditTab,
  key: res.key, nama: res.nama, mode: res.mode
}}];
"""

JS_FIND_DUPLICATE = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Find Duplicate — pembungkus tipis di atas vdCheckAddLead(), pagar terakhir
 * sebelum baris baru ditulis ke STATS. Lihat komentar fungsinya di
 * src/build-payload.js untuk alasan tiap penolakan.
 * ---------------------------------------------------------------------- */
const prep = $('Prepare Add Lead').first().json;
const profile = VIRA_TENANTS[prep._claims.t];

const rows = $input.all().map(function (i) { return i.json; });
const gate = vdCheckAddLead(profile, rows, prep.key, prep.tab);

if (!gate.ok) {
  return [{ json: { _route: 'error', _cors: prep._cors,
    _response: { ok: false, action: 'add_lead',
                 error: gate.error, message: gate.message } }}];
}

const cells = vdAddLeadCells(prep);

return [{ json: {
  _route: 'ok', _cors: prep._cors, _claims: prep._claims,
  doc_id: prep.doc_id, tab: prep.tab, audit_tab: prep.audit_tab,
  key: prep.key, nama: prep.nama, mode: prep.mode,
  ts_iso: new Date().toISOString(),
  // Nilai yang benar-benar menjadi sel. Awalan col_ memisahkannya dengan
  // jelas dari data kerja di item yang sama.
  col_wa: cells['No WA'],
  col_nama: cells['Nama'],
  col_bot: cells['bot_mode'],
  col_counter: cells['Counter']
}}];
"""

JS_BUILD_ADD_LEAD_RESPONSE = LIB_TENANTS + LIB_PAYLOAD + r"""
/* -------------------------------------------------------------------------
 * Build Add Lead Response — membatalkan cache tenant, lalu mengembalikan
 * baris lead siap render lewat vdAddLeadRow() (jalur pembentukan yang sama
 * dengan `stats`, lihat alasannya di src/build-payload.js).
 * ---------------------------------------------------------------------- */
const f = $('Find Duplicate').first().json;
const profile = VIRA_TENANTS[f._claims.t];

const store = $getWorkflowStaticData('global');
if (store.statsCache) store.statsCache[f._claims.t] = null;

const row = vdAddLeadRow(profile, {
  'No WA': f.col_wa, 'Nama': f.col_nama,
  'bot_mode': f.col_bot, 'Counter': f.col_counter
});

const message = f.mode === 'OFF'
  ? 'Nomor ' + f.key + ' ditambahkan dengan bot OFF. VIRA belum akan membalas nomor ini.'
  : 'Nomor ' + f.key + ' ditambahkan dengan bot ON. VIRA akan membalas kalau nomor ini chat.';

return [{ json: { _cors: f._cors, _response: {
  ok: true, action: 'add_lead',
  key: f.key, bot_mode: f.mode, row: row, message: message
}}}];
"""

JS_BUILD_ADD_LEAD_FAILED = r"""
/* -------------------------------------------------------------------------
 * Build Add Lead Failed — cabang error node Append Lead.
 *
 * Ada supaya kegagalan tulis tidak berakhir sebagai request menggantung:
 * karena responseMode = responseNode, eksekusi yang berhenti sebelum Respond
 * membuat browser menunggu sampai timeout tanpa pesan apa pun — persis
 * masalah yang tercatat di audit untuk node Update Bot Mode.
 *
 * Sengaja TIDAK memakai continueRegularOutput: melaporkan "berhasil" padahal
 * baris tidak tertulis jauh lebih berbahaya daripada melaporkan gagal.
 * ---------------------------------------------------------------------- */
const prep = $('Prepare Add Lead').first().json;
const err = $input.first().json || {};
console.log('Append Lead gagal: ' + String(err.error || '').slice(0, 200));

return [{ json: { _cors: prep._cors, _response: {
  ok: false, action: 'add_lead', error: 'WRITE_FAILED',
  message: 'Gagal menulis ke Google Sheets, jadi nomor ' + prep.key +
           ' BELUM tersimpan. Coba lagi sebentar lagi.'
}}}];
"""

JS_BUILD_TOGGLE_RESPONSE = r"""
/* Build Toggle Response — juga membatalkan cache tenant supaya angka di
 * dashboard tidak menampilkan status lama setelah tombol ditekan. */
const f = $('Find Row').first().json;
const store = $getWorkflowStaticData('global');
if (store.statsCache) store.statsCache[f._claims.t] = null;

const nomor = f.key;
const message = f.mode === 'OFF'
  ? 'Bot dimatikan untuk ' + nomor + '. Percakapan sekarang dipegang manual.'
  : 'Bot diaktifkan kembali untuk ' + nomor + '.';

return [{ json: { _cors: f._cors, _response: {
  ok: true, action: 'toggle_user', key: nomor, bot_mode: f.mode, message: message
}}}];
"""


# ------------------------------------------------------------------ nodes --

nodes = [
    {
        'parameters': {
            'httpMethod': 'POST',
            'path': WEBHOOK_PATH,
            'responseMode': 'responseNode',
            'options': {},
        },
        'id': 'webhook',
        'name': 'Webhook',
        'type': 'n8n-nodes-base.webhook',
        'typeVersion': 2,
        'position': [-1120, 300],
        'webhookId': WEBHOOK_ID,
    },

    code_node('Parse Request', JS_PARSE_REQUEST, [-900, 300]),

    {
        'parameters': {
            'rules': {'values': [
                {'conditions': {'options': {'caseSensitive': True, 'version': 2},
                                'conditions': [{'leftValue': '={{ $json._route }}',
                                                'rightValue': 'login',
                                                'operator': {'type': 'string', 'operation': 'equals'}}],
                                'combinator': 'and'},
                 'renameOutput': True, 'outputKey': 'login'},
                {'conditions': {'options': {'caseSensitive': True, 'version': 2},
                                'conditions': [{'leftValue': '={{ $json._route }}',
                                                'rightValue': 'auth',
                                                'operator': {'type': 'string', 'operation': 'equals'}}],
                                'combinator': 'and'},
                 'renameOutput': True, 'outputKey': 'auth'},
            ]},
            'options': {'fallbackOutput': 'extra', 'renameFallbackOutput': 'error'},
        },
        'id': 'route-action',
        'name': 'Route Action',
        'type': 'n8n-nodes-base.switch',
        'typeVersion': 3,
        'position': [-680, 300],
    },

    {
        'parameters': {
            'action': 'hash',
            'type': 'SHA256',
            'value': '={{ $json._pwInput }}',
            'dataPropertyName': '_pwHash',
            'encoding': 'hex',
        },
        'id': 'hash-password',
        'name': 'Hash Password',
        'type': 'n8n-nodes-base.crypto',
        'typeVersion': 1,
        'position': [-460, 100],
    },

    code_node('Verify Login', JS_VERIFY_LOGIN, [-240, 100]),

    {
        'parameters': {
            'action': 'hmac',
            'type': 'SHA256',
            'value': '={{ $json._payloadPart }}',
            'dataPropertyName': '_sigCalc',
            'secret': HMAC_SECRET,
            'encoding': 'hex',
        },
        'id': 'verify-token-hmac',
        'name': 'Verify Token HMAC',
        'type': 'n8n-nodes-base.crypto',
        'typeVersion': 1,
        'position': [-460, 460],
    },

    code_node('Check Token', JS_CHECK_TOKEN, [-240, 460]),

    {
        'parameters': {
            'rules': {'values': [
                {'conditions': {'options': {'caseSensitive': True, 'version': 2},
                                'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'stats',
                                                'operator': {'type': 'string', 'operation': 'equals'}}],
                                'combinator': 'and'},
                 'renameOutput': True, 'outputKey': 'stats'},
                {'conditions': {'options': {'caseSensitive': True, 'version': 2},
                                'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'toggle_user',
                                                'operator': {'type': 'string', 'operation': 'equals'}}],
                                'combinator': 'and'},
                 'renameOutput': True, 'outputKey': 'toggle_user'},
                {'conditions': {'options': {'caseSensitive': True, 'version': 2},
                                'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'me',
                                                'operator': {'type': 'string', 'operation': 'equals'}}],
                                'combinator': 'and'},
                 'renameOutput': True, 'outputKey': 'me'},
                {'conditions': {'options': {'caseSensitive': True, 'version': 2},
                                'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'switch_tenant',
                                                'operator': {'type': 'string', 'operation': 'equals'}}],
                                'combinator': 'and'},
                 'renameOutput': True, 'outputKey': 'switch_tenant'},
                {'conditions': {'options': {'caseSensitive': True, 'version': 2},
                                'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'add_lead',
                                                'operator': {'type': 'string', 'operation': 'equals'}}],
                                'combinator': 'and'},
                 'renameOutput': True, 'outputKey': 'add_lead'},
            ]},
            'options': {'fallbackOutput': 'extra', 'renameFallbackOutput': 'error'},
        },
        'id': 'route-authed',
        'name': 'Route Authed',
        'type': 'n8n-nodes-base.switch',
        'typeVersion': 3,
        'position': [-20, 460],
    },

    code_node('Build Me Response', JS_BUILD_ME, [220, 860]),
    code_node('Prepare Switch Tenant', JS_PREPARE_SWITCH, [220, 1000]),

    {
        'parameters': {
            'conditions': {'options': {'caseSensitive': True, 'version': 2},
                           'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'sign',
                                           'operator': {'type': 'string', 'operation': 'equals'}}],
                           'combinator': 'and'},
            'options': {},
        },
        'id': 'if-needs-signing',
        'name': 'IF Needs Signing',
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2,
        'position': [-20, 100],
    },

    {
        'parameters': {
            'action': 'hmac',
            'type': 'SHA256',
            'value': '={{ $json._claimsB64 }}',
            'dataPropertyName': '_sig',
            'secret': HMAC_SECRET,
            'encoding': 'hex',
        },
        'id': 'sign-token',
        'name': 'Sign Token',
        'type': 'n8n-nodes-base.crypto',
        'typeVersion': 1,
        'position': [220, 60],
    },

    code_node('Build Auth Response', JS_BUILD_AUTH_RESPONSE, [440, 60]),

    # ---- jalur stats ----
    code_node('Cache Check', JS_CACHE_CHECK, [220, 300]),

    {
        'parameters': {
            'conditions': {'options': {'caseSensitive': True, 'version': 2},
                           'conditions': [{'leftValue': '={{ $json._cacheHit }}', 'rightValue': True,
                                           'operator': {'type': 'boolean', 'operation': 'true',
                                                        'singleValue': True}}],
                           'combinator': 'and'},
            'options': {},
        },
        'id': 'if-cache-hit',
        'name': 'IF Cache Hit',
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2,
        'position': [440, 300],
    },

    code_node('Fan Out Tabs', JS_FAN_OUT, [660, 380]),

    {
        'parameters': {'batchSize': 1, 'options': {}},
        'id': 'loop-over-tabs',
        'name': 'Loop Over Tabs',
        'type': 'n8n-nodes-base.splitInBatches',
        'typeVersion': 3,
        'position': [880, 380],
    },

    sheets_read('Read Tab', [1100, 460]),
    code_node('Tag Rows', JS_TAG_ROWS, [1320, 460], always_output=True),
    code_node('Collect Tabs', JS_COLLECT, [1100, 300]),
    code_node('Build Stats Response', JS_BUILD_STATS, [1320, 220]),

    # ---- jalur toggle ----
    code_node('Prepare Toggle', JS_PREPARE_TOGGLE, [220, 620]),

    {
        'parameters': {
            'authentication': 'serviceAccount',
            'documentId': {'__rl': True, 'value': '={{ $json.doc_id }}', 'mode': 'id'},
            'sheetName': {'__rl': True, 'value': '={{ $json.tab }}', 'mode': 'name'},
            'options': {},
        },
        'id': 'read-stats-for-toggle',
        'name': 'Read STATS for Toggle',
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.5,
        'position': [440, 620],
        'credentials': {'googleApi': {'id': GOOGLE_CRED_ID, 'name': GOOGLE_CRED_NAME}},
    },

    code_node('Find Row', JS_FIND_ROW, [660, 620]),

    {
        'parameters': {
            'conditions': {'options': {'caseSensitive': True, 'version': 2},
                           'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'ok',
                                           'operator': {'type': 'string', 'operation': 'equals'}}],
                           'combinator': 'and'},
            'options': {},
        },
        'id': 'if-row-found',
        'name': 'IF Row Found',
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2,
        'position': [880, 620],
    },

    {
        'parameters': {
            'authentication': 'serviceAccount',
            'operation': 'update',
            'documentId': {'__rl': True, 'value': '={{ $json.doc_id }}', 'mode': 'id'},
            'sheetName': {'__rl': True, 'value': '={{ $json.tab }}', 'mode': 'name'},
            'columns': {
                'mappingMode': 'defineBelow',
                'value': {
                    'row_number': '={{ $json.row_number }}',
                    'bot_mode': '={{ $json.mode }}',
                },
                'matchingColumns': ['row_number'],
            },
            'options': {},
        },
        'id': 'update-bot-mode',
        'name': 'Update Bot Mode',
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.5,
        'position': [1100, 600],
        'credentials': {'googleApi': {'id': GOOGLE_CRED_ID, 'name': GOOGLE_CRED_NAME}},
    },

    sheets_append(
        'Append Audit', [1320, 600],
        "={{ $('Find Row').first().json.doc_id }}",
        "={{ $('Find Row').first().json.audit_tab }}",
        {
            'ts':    "={{ $('Find Row').first().json.ts_iso }}",
            'actor': "={{ $('Find Row').first().json._claims.u }}",
            'role':  "={{ $('Find Row').first().json._claims.r }}",
            'no_wa': "={{ $('Find Row').first().json.key }}",
            'from':  "={{ $('Find Row').first().json.before }}",
            'to':    "={{ $('Find Row').first().json.mode }}",
        },
        on_error='continueRegularOutput', always_output=True),

    code_node('Build Toggle Response', JS_BUILD_TOGGLE_RESPONSE, [1540, 600]),

    # ---- jalur add_lead ----
    code_node('Prepare Add Lead', JS_PREPARE_ADD_LEAD, [220, 1240]),

    # Nomor tidak valid adalah keadaan yang WAJAR di jalur ini (user mengetik),
    # bukan kelainan seperti di jalur toggle. Tanpa gerbang ini item error akan
    # masuk ke node Sheets dengan doc_id kosong, node gagal, eksekusi berhenti
    # sebelum Respond, dan browser menggantung sampai timeout tanpa pesan.
    {
        'parameters': {
            'conditions': {'options': {'caseSensitive': True, 'version': 2},
                           'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'ok',
                                           'operator': {'type': 'string', 'operation': 'equals'}}],
                           'combinator': 'and'},
            'options': {},
        },
        'id': 'if-add-lead-valid',
        'name': 'IF Add Lead Valid',
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2,
        'position': [440, 1240],
    },

    {
        'parameters': {
            'authentication': 'serviceAccount',
            'documentId': {'__rl': True, 'value': '={{ $json.doc_id }}', 'mode': 'id'},
            'sheetName': {'__rl': True, 'value': '={{ $json.tab }}', 'mode': 'name'},
            'options': {},
        },
        'id': 'read-stats-for-add',
        'name': 'Read STATS for Add',
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.5,
        'position': [660, 1240],
        # Kalau pembacaan gagal, jangan hentikan eksekusi sebelum Respond —
        # Find Duplicate yang memutuskan (dan menolak menulis buta).
        'alwaysOutputData': True,
        'onError': 'continueRegularOutput',
        'credentials': {'googleApi': {'id': GOOGLE_CRED_ID, 'name': GOOGLE_CRED_NAME}},
    },

    code_node('Find Duplicate', JS_FIND_DUPLICATE, [880, 1240]),

    {
        'parameters': {
            'conditions': {'options': {'caseSensitive': True, 'version': 2},
                           'conditions': [{'leftValue': '={{ $json._route }}', 'rightValue': 'ok',
                                           'operator': {'type': 'string', 'operation': 'equals'}}],
                           'combinator': 'and'},
            'options': {},
        },
        'id': 'if-can-append',
        'name': 'IF Can Append',
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2,
        'position': [1100, 1240],
    },

    # Gagal tulis harus sampai ke user sebagai gagal, bukan diam-diam jadi
    # "berhasil" — karena itu continueErrorOutput, bukan continueRegularOutput.
    sheets_append(
        'Append Lead', [1320, 1220],
        '={{ $json.doc_id }}', '={{ $json.tab }}',
        {
            'No WA':    '={{ $json.col_wa }}',
            'Nama':     '={{ $json.col_nama }}',
            'bot_mode': '={{ $json.col_bot }}',
            'Counter':  '={{ $json.col_counter }}',
        },
        on_error='continueErrorOutput'),

    # Audit itu catatan, bukan syarat. Barisnya sudah tertulis; gagal mencatat
    # tidak boleh membatalkan laporan sukses ke user.
    sheets_append(
        'Append Audit (Add)', [1540, 1220],
        "={{ $('Find Duplicate').first().json.doc_id }}",
        "={{ $('Find Duplicate').first().json.audit_tab }}",
        {
            'ts':    "={{ $('Find Duplicate').first().json.ts_iso }}",
            'actor': "={{ $('Find Duplicate').first().json._claims.u }}",
            'role':  "={{ $('Find Duplicate').first().json._claims.r }}",
            'no_wa': "={{ $('Find Duplicate').first().json.key }}",
            'from':  '(baru)',
            'to':    "={{ $('Find Duplicate').first().json.mode }}",
        },
        on_error='continueRegularOutput', always_output=True),

    code_node('Build Add Lead Response', JS_BUILD_ADD_LEAD_RESPONSE, [1760, 1220]),
    code_node('Build Add Lead Failed', JS_BUILD_ADD_LEAD_FAILED, [1540, 1400]),

    # ---- respons ----
    {
        'parameters': {
            'respondWith': 'json',
            'responseBody': '={{ JSON.stringify($json._response) }}',
            'options': {
                'responseCode': 200,
                'responseHeaders': {'entries': [
                    {'name': 'Content-Type', 'value': 'application/json; charset=utf-8'},
                    {'name': 'Access-Control-Allow-Origin', 'value': '={{ $json._cors }}'},
                    {'name': 'Vary', 'value': 'Origin'},
                    {'name': 'Cache-Control', 'value': 'no-store'},
                ]},
            },
        },
        'id': 'respond',
        'name': 'Respond',
        'type': 'n8n-nodes-base.respondToWebhook',
        'typeVersion': 1.1,
        'position': [2420, 300],
    },

    {
        'parameters': {
            'content': (
                '## VIRA Dashboard API\\n'
                'Di-generate dari `n8n/src/*.js` oleh `build_workflow.py`.\\n'
                '**Jangan edit Code node lewat UI** — perubahan akan hilang saat rebuild.\\n\\n'
                'Setelah import:\\n'
                '1. Pilih credential Google Sheets khusus dashboard di 7 node Sheets.\\n'
                '2. Isi `corsOrigins` di src/tenants.js dengan domain hasil deploy, rebuild, import ulang.\\n'
                '3. Buat tab `DASH_AUDIT` di kedua spreadsheet (header: ts, actor, role, no_wa, from, to).\\n'
                '4. Jalankan sekali (tambah lead dummy) supaya node Sheets bisa\\n'
                '   me-resolve kolomnya, lalu simpan ulang. Selama belum pernah\\n'
                '   dieksekusi, node tulis melapor "No columns found".\\n'
                '5. Aktifkan workflow.\\n\\n'
                'Workflow ini TIDAK memanggil AI. Rekomendasi topik dihitung\\n'
                'WF-B (Monthly Rollup) dan dibaca dari kolom `ai_insight_json`\\n'
                'di tab MONTHLY_SUMMARY.'
            ),
            'height': 320, 'width': 460, 'color': 4,
        },
        'id': 'sticky-readme',
        'name': 'Catatan Deploy',
        'type': 'n8n-nodes-base.stickyNote',
        'typeVersion': 1,
        'position': [-1120, -140],
    },
]

# ------------------------------------------------------------ connections --

def conn(target, index=0):
    return {'node': target, 'type': 'main', 'index': index}


connections = {
    'Webhook': {'main': [[conn('Parse Request')]]},
    'Parse Request': {'main': [[conn('Route Action')]]},
    'Route Action': {'main': [
        [conn('Hash Password')],        # login
        [conn('Verify Token HMAC')],    # auth
        [conn('Respond')],              # error (fallback)
    ]},

    'Hash Password': {'main': [[conn('Verify Login')]]},
    'Verify Login': {'main': [[conn('IF Needs Signing')]]},
    'Prepare Switch Tenant': {'main': [[conn('IF Needs Signing')]]},
    'IF Needs Signing': {'main': [
        [conn('Sign Token')],   # true
        [conn('Respond')],      # false -> _response sudah terisi
    ]},
    'Sign Token': {'main': [[conn('Build Auth Response')]]},
    'Build Auth Response': {'main': [[conn('Respond')]]},

    'Verify Token HMAC': {'main': [[conn('Check Token')]]},
    'Check Token': {'main': [[conn('Route Authed')]]},
    # Urutan WAJIB sama dengan urutan rules di node Route Authed.
    'Route Authed': {'main': [
        [conn('Cache Check')],            # stats
        [conn('Prepare Toggle')],         # toggle_user
        [conn('Build Me Response')],      # me
        [conn('Prepare Switch Tenant')],  # switch_tenant
        [conn('Prepare Add Lead')],       # add_lead
        [conn('Respond')],                # error (fallback)
    ]},

    'Build Me Response': {'main': [[conn('Respond')]]},

    'Cache Check': {'main': [[conn('IF Cache Hit')]]},
    'IF Cache Hit': {'main': [
        [conn('Build Stats Response')],  # true
        [conn('Fan Out Tabs')],          # false
    ]},
    'Fan Out Tabs': {'main': [[conn('Loop Over Tabs')]]},
    # splitInBatches: output 0 = done, output 1 = loop
    'Loop Over Tabs': {'main': [
        [conn('Collect Tabs')],
        [conn('Read Tab')],
    ]},
    'Read Tab': {'main': [[conn('Tag Rows')]]},
    'Tag Rows': {'main': [[conn('Loop Over Tabs')]]},
    'Collect Tabs': {'main': [[conn('Build Stats Response')]]},

    'Build Stats Response': {'main': [[conn('Respond')]]},

    'Prepare Toggle': {'main': [[conn('Read STATS for Toggle')]]},
    'Read STATS for Toggle': {'main': [[conn('Find Row')]]},
    'Find Row': {'main': [[conn('IF Row Found')]]},
    'IF Row Found': {'main': [
        [conn('Update Bot Mode')],  # true
        [conn('Respond')],          # false
    ]},
    'Update Bot Mode': {'main': [[conn('Append Audit')]]},
    'Append Audit': {'main': [[conn('Build Toggle Response')]]},
    'Build Toggle Response': {'main': [[conn('Respond')]]},

    'Prepare Add Lead': {'main': [[conn('IF Add Lead Valid')]]},
    'IF Add Lead Valid': {'main': [
        [conn('Read STATS for Add')],  # true
        [conn('Respond')],             # false -> _response sudah terisi
    ]},
    'Read STATS for Add': {'main': [[conn('Find Duplicate')]]},
    'Find Duplicate': {'main': [[conn('IF Can Append')]]},
    'IF Can Append': {'main': [
        [conn('Append Lead')],  # true
        [conn('Respond')],      # false -> _response sudah terisi
    ]},
    # onError continueErrorOutput: output 0 = sukses, output 1 = gagal tulis.
    'Append Lead': {'main': [
        [conn('Append Audit (Add)')],
        [conn('Build Add Lead Failed')],
    ]},
    'Append Audit (Add)': {'main': [[conn('Build Add Lead Response')]]},
    'Build Add Lead Response': {'main': [[conn('Respond')]]},
    'Build Add Lead Failed': {'main': [[conn('Respond')]]},
}

workflow = {
    'name': 'VIRA Dashboard API',
    'nodes': nodes,
    'connections': connections,
    'active': False,
    'settings': {
        'executionOrder': 'v1',
        'timezone': 'Asia/Jakarta',
        'saveManualExecutions': True,
        # Jangan simpan eksekusi sukses: body login memuat password plaintext,
        # dan riwayat eksekusi n8n bisa dibaca siapa pun yang punya akses UI.
        'saveDataSuccessExecution': 'none',
        'saveDataErrorExecution': 'all',
    },
    'pinData': {},
    'meta': {'instanceId': 'vira-dashboard'},
    'tags': [],
}


def main():
    if 'REPLACE_WITH' in GOOGLE_CRED_ID:
        print('[i] credential Google masih placeholder — pilih manual setelah import.')
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    size = os.path.getsize(OUT)
    print('[ok] %s  (%d node, %.1f KB)' % (os.path.basename(OUT), len(nodes), size / 1024.0))

    # Sanity check ringan; validasi penuh ada di qa/validate_workflow.py
    names = set(n['name'] for n in nodes)
    missing = []
    for src, spec in connections.items():
        if src not in names:
            missing.append(src)
        for group in spec['main']:
            for c in group:
                if c['node'] not in names:
                    missing.append(c['node'])
    if missing:
        print('[!] node tidak dikenal di connections: %s' % sorted(set(missing)))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
