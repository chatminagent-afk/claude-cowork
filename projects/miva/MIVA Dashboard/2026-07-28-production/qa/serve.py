#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serve.py — server lokal untuk UAT.

Tiga peran sekaligus:
  1. Menyajikan berkas statis (app/, qa/, n8n/src/) apa adanya, sehingga yang
     diuji adalah file yang PERSIS akan di-deploy — bukan salinan yang diedit.
  2. Mock API `/api/vira-dash` yang mengikuti docs/2026-07-28-API-CONTRACT.md.
  3. Endpoint `/_save/<nama>.json` supaya selftest.html bisa menyimpan payload
     hasil normalizer JavaScript yang SEBENARNYA, lalu mock API menyajikannya.

Poin 3 itu penting: mock ini tidak menulis ulang logika normalisasi di Python
(dua implementasi pasti akan menyimpang). Ia menyajikan keluaran asli
`build-payload.js`, sehingga yang diuji end-to-end memang kode produksinya.

Token ditandatangani dengan HMAC-SHA256 memakai secret dan daftar akun yang
dibaca langsung dari n8n/src + build_workflow.py — jadi uji isolasi tenant
di sini menguji format token yang sama dengan produksi.

    python qa/serve.py            # http://localhost:8099
"""

import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SRC = os.path.join(ROOT, 'n8n', 'src')
FIX = os.path.join(HERE, 'fixtures')
PORT = int(os.environ.get('VD_PORT', '8099'))


# ------------------------------------------------- baca konfigurasi dari src

def _read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


TENANTS_JS = _read(os.path.join(SRC, 'tenants.js'))
BUILD_PY = _read(os.path.join(ROOT, 'n8n', 'build_workflow.py'))

SECRET = re.search(r"^HMAC_SECRET\s*=\s*'([^']+)'", BUILD_PY, re.M).group(1)

_ttl_expr = re.search(r'tokenTtlSec:\s*([0-9\s*]+),', TENANTS_JS).group(1)
TOKEN_TTL = 1
for part in _ttl_expr.split('*'):
    TOKEN_TTL *= int(part.strip())

USERS = {}
for m in re.finditer(
        r"username:\s*'([^']+)',\s*"
        r"display:\s*'([^']*)',\s*"
        r"role:\s*'([^']+)',\s*"
        r"tenants:\s*\[([^\]]*)\],\s*"
        r"salt:\s*'([^']+)',\s*"
        r"hash:\s*'([^']+)'", TENANTS_JS):
    USERS[m.group(1)] = {
        'username': m.group(1),
        'display': m.group(2),
        'role': m.group(3),
        'tenants': re.findall(r"'([^']+)'", m.group(4)),
        'salt': m.group(5),
        'hash': m.group(6),
    }

TENANT_META = {}
for m in re.finditer(
        r"id:\s*'([^']+)',\s*name:\s*'([^']+)',\s*product:\s*'([^']*)',\s*accent:\s*'([^']+)'",
        TENANTS_JS):
    TENANT_META[m.group(1)] = {'id': m.group(1), 'name': m.group(2),
                               'product': m.group(3), 'accent': m.group(4)}

if not USERS or not TENANT_META:
    print('[!] gagal membaca akun/tenant dari n8n/src/tenants.js')
    sys.exit(1)

# Salinan payload yang bisa diubah toggle, per tenant. Diisi saat request
# pertama dari berkas payload-<tenant>.json yang ditulis selftest.html.
LIVE = {}
LOGIN_FAILS = {}


# ------------------------------------------------------------------- token

def b64u(raw):
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def b64u_dec(s):
    pad = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def sign(payload):
    return hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def make_token(user, tenant, now=None):
    now = int(now or time.time())
    claims = {
        'u': user['username'], 'd': user['display'], 'r': user['role'],
        't': tenant, 'ts': list(user['tenants']),
        'iat': now, 'exp': now + TOKEN_TTL,
        'n': '%d-%s' % (now, os.urandom(4).hex()),
    }
    payload = b64u(json.dumps(claims, separators=(',', ':')).encode('utf-8'))
    return payload + '.' + sign(payload), claims


def read_token(token):
    """Return (claims, error_code). Meniru urutan pemeriksaan Check Token n8n."""
    if not token or not isinstance(token, str):
        return None, 'TOKEN_MISSING'
    if token.count('.') < 1:
        return None, 'TOKEN_MALFORMED'
    payload, _, sig = token.rpartition('.')
    if not re.fullmatch(r'[A-Za-z0-9\-_]+', payload or ''):
        return None, 'TOKEN_MALFORMED'
    if not re.fullmatch(r'[a-fA-F0-9]{64}', sig or ''):
        return None, 'TOKEN_MALFORMED'
    if not hmac.compare_digest(sign(payload), sig.lower()):
        return None, 'TOKEN_BAD_SIGNATURE'
    try:
        claims = json.loads(b64u_dec(payload))
    except Exception:                                     # noqa: BLE001
        return None, 'TOKEN_MALFORMED'
    if claims.get('exp', 0) <= time.time():
        return None, 'TOKEN_EXPIRED'
    user = USERS.get(claims.get('u'))
    if not user:
        return None, 'USER_UNKNOWN'
    if user['role'] != claims.get('r'):
        return None, 'ROLE_CHANGED'
    if claims.get('t') not in user['tenants']:
        return None, 'TENANT_FORBIDDEN'
    if claims.get('t') not in TENANT_META:
        return None, 'TENANT_UNKNOWN'
    return claims, None


def session_of(claims):
    return {
        'username': claims['u'], 'display': claims['d'], 'role': claims['r'],
        'tenant': claims['t'], 'exp': claims['exp'],
        'tenants': [{'id': t, 'name': TENANT_META.get(t, {}).get('name', t)}
                    for t in claims['ts']],
    }


def err(action, code, message):
    return {'ok': False, 'action': action, 'error': code, 'message': message}


def load_payload(tenant):
    if tenant in LIVE:
        return LIVE[tenant]
    p = os.path.join(FIX, 'payload-%s.json' % tenant)
    if not os.path.exists(p):
        return None
    with open(p, 'r', encoding='utf-8') as f:
        LIVE[tenant] = json.load(f)
    return LIVE[tenant]


# ----------------------------------------------------------------- handler

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        if '/api/' in (self.path or '') or '/_save/' in (self.path or ''):
            sys.stderr.write('  %s %s\n' % (self.command, self.path))

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        origin = self.headers.get('Origin') or '*'
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Vary', 'Origin')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        # Berkas statis tidak boleh di-cache browser selama UAT.
        if not self.path.startswith('/api/') and not self.path.startswith('/_save/'):
            self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin') or '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length).decode('utf-8', 'replace') if length else ''

        if self.path.startswith('/_save/'):
            name = os.path.basename(self.path[len('/_save/'):])
            if not re.fullmatch(r'[a-z0-9\-]+\.json', name):
                return self._send_json({'ok': False, 'error': 'nama tidak valid'}, 400)
            with open(os.path.join(FIX, name), 'w', encoding='utf-8') as f:
                f.write(raw)
            LIVE.clear()
            return self._send_json({'ok': True, 'saved': name, 'bytes': len(raw)})

        if self.path.rstrip('/') != '/api/vira-dash':
            return self._send_json({'ok': False, 'error': 'NOT_FOUND'}, 404)

        try:
            req = json.loads(raw)
        except Exception:                                 # noqa: BLE001
            return self._send_json(err('unknown', 'BAD_REQUEST',
                                       'Permintaan tidak dapat dibaca.'))
        return self._send_json(self.api(req))

    # ------------------------------------------------------------- API ----

    def api(self, req):
        action = str(req.get('action') or '')

        if action == 'login':
            username = str(req.get('username') or '').strip().lower()
            password = str(req.get('password') or '')
            if not username or not password:
                return err('login', 'BAD_CREDENTIALS', 'Username dan password wajib diisi.')

            rec = LOGIN_FAILS.get(username)
            if rec and rec['until'] > time.time():
                menit = int((rec['until'] - time.time()) / 60) + 1
                return err('login', 'LOCKED_OUT',
                           'Terlalu banyak percobaan gagal. Coba lagi dalam %d menit.' % menit)

            user = USERS.get(username)
            digest = hashlib.sha256(
                ((user['salt'] if user else 'no-such-user') + ':' + password).encode()
            ).hexdigest()
            if not user or not hmac.compare_digest(digest, user['hash']):
                r = LOGIN_FAILS.setdefault(username, {'fails': 0, 'until': 0})
                r['fails'] += 1
                if r['fails'] >= 5:
                    r['until'] = time.time() + 900
                return err('login', 'BAD_CREDENTIALS', 'Username atau password salah.')

            LOGIN_FAILS.pop(username, None)
            token, claims = make_token(user, user['tenants'][0])
            return {'ok': True, 'action': 'login', 'token': token,
                    'session': session_of(claims)}

        claims, code = read_token(req.get('token'))
        if code:
            msg = ('Sesi sudah berakhir. Silakan login ulang.'
                   if code == 'TOKEN_EXPIRED' else 'Sesi tidak valid. Silakan login ulang.')
            if code == 'TENANT_FORBIDDEN':
                msg = 'Akun ini tidak punya akses ke klien tersebut.'
            return err(action or 'unknown', code, msg)

        if action == 'me':
            return {'ok': True, 'action': 'me', 'session': session_of(claims)}

        if action == 'switch_tenant':
            target = str(req.get('tenant') or '')
            user = USERS[claims['u']]
            if target not in TENANT_META:
                return err('switch_tenant', 'TENANT_UNKNOWN', 'Klien tidak dikenal.')
            if target not in user['tenants']:
                return err('switch_tenant', 'TENANT_FORBIDDEN',
                           'Akun ini tidak punya akses ke klien tersebut.')
            token, c2 = make_token(user, target)
            return {'ok': True, 'action': 'switch_tenant', 'token': token,
                    'session': session_of(c2)}

        if action == 'stats':
            payload = load_payload(claims['t'])
            if payload is None:
                return err('stats', 'SHEET_ERROR',
                           'payload-%s.json belum dibuat — buka qa/selftest.html '
                           'lebih dulu.' % claims['t'])
            out = json.loads(json.dumps(payload))
            out['cached'] = False
            return out

        if action == 'toggle_user':
            payload = load_payload(claims['t'])
            if payload is None:
                return err('toggle_user', 'SHEET_ERROR', 'Data belum dimuat.')
            key = str(req.get('key') or '')
            mode = str(req.get('mode') or '').upper()
            if mode not in ('ON', 'OFF'):
                return err('toggle_user', 'BAD_REQUEST', 'Mode harus ON atau OFF.')
            for row in payload['leads']['rows']:
                if row['key'] == key:
                    row['bot_mode'] = mode
                    pesan = ('Bot dimatikan untuk %s. Percakapan sekarang dipegang manual.' % key
                             if mode == 'OFF' else 'Bot diaktifkan kembali untuk %s.' % key)
                    return {'ok': True, 'action': 'toggle_user', 'key': key,
                            'bot_mode': mode, 'message': pesan}
            return err('toggle_user', 'ROW_NOT_FOUND',
                       'Nomor %s tidak ditemukan di data. Coba muat ulang dashboard.' % key)

        return err(action or 'unknown', 'BAD_REQUEST', 'Perintah tidak dikenal.')


def main():
    os.chdir(ROOT)
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    print('  akun   : %s' % ', '.join(sorted(USERS)))
    print('  tenant : %s' % ', '.join(sorted(TENANT_META)))
    print('  ttl    : %d detik' % TOKEN_TTL)
    print()
    print('  unit test : http://localhost:%d/qa/selftest.html' % PORT)
    print('  dashboard : http://localhost:%d/app/index.html?api=http://localhost:%d/api/vira-dash'
          % (PORT, PORT))
    print()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
