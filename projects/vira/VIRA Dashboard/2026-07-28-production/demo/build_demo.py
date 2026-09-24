#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_demo.py — merakit demo satu-berkas dari aplikasi yang sesungguhnya.

Hasilnya: `demo/VIRA-Dashboard-DEMO.html`, satu file HTML yang bisa dibuka
dengan klik dua kali. Tanpa server, tanpa n8n, tanpa internet.

Yang dipakai di dalamnya adalah CSS dan JavaScript dari `app/` **apa adanya** —
bukan versi khusus demo. Yang ditambahkan hanya satu lapis tipis:
  1. data contoh yang ditanam di dalam file
  2. `window.__VD_MOCK__` yang menjawab request alih-alih jaringan
  3. banner tetap "MODE DEMO" supaya tidak ada yang mengira ini data asli

Artinya kalau demo terlihat benar, aplikasi produksinya juga benar — yang
berbeda hanya sumber datanya.

    python demo/build_demo.py
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
APP = os.path.join(ROOT, 'app revamp')
FIX = os.path.join(ROOT, 'qa', 'fixtures')
OUT = os.path.join(HERE, 'VIRA-Dashboard-DEMO.html')

# Kata sandi demo. Sengaja sepele dan sama untuk semua akun — file ini memang
# untuk dibagikan/dilihat-lihat, tidak ada data asli di dalamnya.
DEMO_PASSWORD = 'demo'


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def inline_icons(html):
    """
    Ubah tiap rujukan `icons/xxx` menjadi data URI.

    Tanpa ini demo tidak benar-benar satu berkas: logo VIRA dan logo tenant
    tetap menunjuk folder `icons/` yang tidak ikut dibawa, sehingga begitu
    file-nya dipindahkan atau dikirim ke orang lain semua logonya pecah.
    Rujukannya muncul di dua tempat berbeda — atribut src di index.html dan
    string peta logo di config.js — maka penggantiannya dilakukan atas teks
    hasil rakitan, bukan per berkas.
    """
    import base64
    mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml', '.webp': 'image/webp'}

    def sub(m):
        name = m.group(1)
        src = os.path.join(APP, 'icons', name)
        ext = os.path.splitext(name)[1].lower()
        if not os.path.isfile(src) or ext not in mime:
            return m.group(0)
        with open(src, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
        return 'data:%s;base64,%s' % (mime[ext], b64)

    return re.sub(r'\.?/?icons/([A-Za-z0-9._-]+)', sub, html)


def main():
    missing = [p for p in (
        os.path.join(APP, 'index.html'),
        os.path.join(APP, 'css', 'app.css'),
        os.path.join(FIX, 'payload-thescholars.json'),
        os.path.join(FIX, 'payload-persada.json'),
    ) if not os.path.exists(p)]
    if missing:
        print('[!] belum ada: %s' % ', '.join(missing))
        print('    jalankan qa/serve.py lalu buka qa/selftest.html untuk membuat payload.')
        return 1

    html = read(os.path.join(APP, 'index.html'))
    css = read(os.path.join(APP, 'css', 'app.css'))

    payloads = {}
    for tid in ('thescholars', 'persada'):
        payloads[tid] = json.loads(read(os.path.join(FIX, 'payload-%s.json' % tid)))

    # Akun demo. Bentuknya sama dengan VIRA_USERS produksi supaya perilaku
    # pemilih tenant dan penguncian akses identik dengan yang sebenarnya.
    users = {
        'steven':   {'display': 'Steven',                  'role': 'super',
                     'tenants': ['thescholars', 'persada']},
        'sam':      {'display': 'Sam — The Scholars',      'role': 'owner',
                     'tenants': ['thescholars']},
        'sulianto': {'display': 'Om Sulianto — Persada',   'role': 'owner',
                     'tenants': ['persada']},
    }

    shim = DEMO_SHIM \
        .replace('/*__DATA__*/', json.dumps(payloads, ensure_ascii=False)) \
        .replace('/*__USERS__*/', json.dumps(users, ensure_ascii=False)) \
        .replace('/*__PASSWORD__*/', json.dumps(DEMO_PASSWORD))

    # --- CSS masuk ke dalam berkas -----------------------------------------
    html = html.replace(
        '<link rel="stylesheet" href="css/app.css" />',
        '<style>\n' + css + '\n</style>')

    # Manifest & ikon menunjuk berkas terpisah; tidak relevan untuk satu berkas.
    html = re.sub(r'\n\s*<link rel="(manifest|apple-touch-icon|icon)"[^>]*/>', '', html)
    html = html.replace('<title>VIRA Dashboard</title>',
                        '<title>VIRA Dashboard — DEMO</title>')

    # --- JavaScript masuk ke dalam berkas ----------------------------------
    # Urutan penting: config.js -> shim -> sisanya. Shim harus sempat mengubah
    # VDConfig sebelum api.js membaca API_URL saat dimuat.
    order = ['config.js', None, 'api.js', 'charts.js', 'render.js', 'app.js']
    blocks = []
    for name in order:
        if name is None:
            blocks.append('<script>\n' + shim + '\n</script>')
        else:
            blocks.append('<script>\n' + read(os.path.join(APP, 'js', name)) + '\n</script>')

    old_scripts = re.search(
        r'<script src="js/config\.js"></script>.*?<script src="js/app\.js"></script>',
        html, re.S)
    if not old_scripts:
        print('[!] blok <script> di app/index.html tidak dikenali — periksa build_demo.py')
        return 1
    html = html.replace(old_scripts.group(0), '\n'.join(blocks))

    # Dilakukan TERAKHIR, setelah CSS dan JS menyatu, supaya rujukan ikon di
    # dalam config.js ikut tertangkap — bukan hanya yang di index.html.
    html = inline_icons(html)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    kb = os.path.getsize(OUT) / 1024.0
    leads = sum(len(p['leads']['rows']) for p in payloads.values())
    print('[ok] %s  (%.0f KB, %d lead di %d klien)'
          % (os.path.basename(OUT), kb, leads, len(payloads)))
    print('     buka dengan klik dua kali. Akun: %s / kata sandi: %s'
          % (', '.join(sorted(users)), DEMO_PASSWORD))
    return 0


DEMO_SHIM = r"""
/* ============================================================================
 * LAPIS DEMO — hanya ada di berkas ini, tidak ada di aplikasi produksi.
 *
 * Menjawab setiap request di dalam browser memakai data contoh yang ditanam
 * di bawah. Tidak ada koneksi keluar sama sekali.
 *
 * Ini BUKAN implementasi keamanan. Token di sini hanya penanda sesi biasa —
 * pemeriksaan tanda tangan yang sesungguhnya ada di n8n. Yang ditiru di sini
 * adalah *perilaku* yang dilihat pengguna: siapa boleh melihat klien mana.
 * ========================================================================== */
(function (g) {
  'use strict';

  var DATA  = /*__DATA__*/;
  var USERS = /*__USERS__*/;
  var PASSWORD = /*__PASSWORD__*/;

  var C = g.VDConfig;

  /* Matikan jalur jaringan sepenuhnya, termasuk kalau mock gagal dipasang. */
  C.API_URL = '';
  C.isTestEndpoint = function () { return true; };
  C.apiHost = function () { return 'data contoh'; };
  C.TEXT.testModePrefix = 'MODE DEMO — tidak terhubung ke sistem asli, ini';
  C.TEXT.testModeReset = 'Muat ulang';

  var NAMES = {};
  Object.keys(DATA).forEach(function (id) { NAMES[id] = DATA[id].tenant.name; });

  function tenantList(ids) {
    return ids.map(function (id) { return { id: id, name: NAMES[id] || id }; });
  }

  function makeToken(username, tenant) {
    return ['demo', username, tenant, String(Date.now())].join('~');
  }

  function readToken(token) {
    var p = String(token || '').split('~');
    if (p.length !== 4 || p[0] !== 'demo') return null;
    var u = USERS[p[1]];
    if (!u) return null;
    if (u.tenants.indexOf(p[2]) === -1) return null;
    return { username: p[1], user: u, tenant: p[2] };
  }

  function session(username, tenant) {
    var u = USERS[username];
    return {
      username: username, display: u.display, role: u.role, tenant: tenant,
      tenants: tenantList(u.tenants),
      exp: Math.floor(Date.now() / 1000) + 12 * 3600
    };
  }

  function fail(action, code, message) {
    return { ok: false, action: action, error: code, message: message };
  }

  function handle(req) {
    var action = req.action;

    if (action === 'login') {
      var name = String(req.username || '').trim().toLowerCase();
      var u = USERS[name];
      if (!u || String(req.password || '') !== PASSWORD) {
        return fail('login', 'BAD_CREDENTIALS',
          'Username atau kata sandi salah. Di demo ini kata sandinya "' + PASSWORD + '".');
      }
      var t0 = u.tenants[0];
      return { ok: true, action: 'login', token: makeToken(name, t0),
               session: session(name, t0) };
    }

    var s = readToken(req.token);
    if (!s) return fail(action, 'TOKEN_MALFORMED', 'Sesi demo tidak valid. Muat ulang halaman.');

    if (action === 'me') {
      return { ok: true, action: 'me', session: session(s.username, s.tenant) };
    }

    if (action === 'switch_tenant') {
      var target = String(req.tenant || '');
      if (!DATA[target]) return fail(action, 'TENANT_UNKNOWN', 'Klien tidak dikenal.');
      /* Aturan yang sama dengan produksi: owner terkunci ke kliennya sendiri. */
      if (s.user.tenants.indexOf(target) === -1) {
        return fail(action, 'TENANT_FORBIDDEN', 'Akun ini tidak punya akses ke klien tersebut.');
      }
      return { ok: true, action: 'switch_tenant', token: makeToken(s.username, target),
               session: session(s.username, target) };
    }

    if (action === 'stats') {
      var p = DATA[s.tenant];
      p.generated_at = Date.now();
      p.cached = false;
      return p;
    }

    if (action === 'toggle_user') {
      var mode = String(req.mode || '').toUpperCase();
      if (mode !== 'ON' && mode !== 'OFF') {
        return fail(action, 'BAD_REQUEST', 'Mode harus ON atau OFF.');
      }
      var rows = DATA[s.tenant].leads.rows;
      for (var i = 0; i < rows.length; i++) {
        if (rows[i].key === String(req.key || '')) {
          rows[i].bot_mode = mode;
          return { ok: true, action: 'toggle_user', key: rows[i].key, bot_mode: mode,
                   message: mode === 'OFF'
                     ? 'Bot dimatikan untuk ' + rows[i].key + '. (demo — tidak ada yang benar-benar berubah)'
                     : 'Bot diaktifkan kembali untuk ' + rows[i].key + '. (demo)' };
        }
      }
      return fail(action, 'ROW_NOT_FOUND', 'Nomor tidak ditemukan di data contoh.');
    }

    return fail(action || 'unknown', 'BAD_REQUEST', 'Perintah tidak dikenal.');
  }

  /* Jeda kecil supaya indikator memuat sempat terlihat, seperti request nyata. */
  g.__VD_MOCK__ = function (req) {
    return new Promise(function (resolve) {
      setTimeout(function () { resolve(handle(req)); }, 180);
    });
  };

  /* Petunjuk akun di layar masuk. Hanya menambah elemen, tidak menghapus
   * apa pun, supaya tidak mengganggu inisialisasi aplikasi. */
  document.addEventListener('DOMContentLoaded', function () {
    var screen = document.getElementById('screenLogin');
    var card = screen && screen.querySelector('.login-card');
    if (!card) return;

    var box = document.createElement('div');
    box.style.cssText = 'margin-top:18px;padding:12px 14px;border-radius:12px;' +
      'background:rgba(255,159,10,.10);border:1px solid rgba(255,159,10,.28);' +
      'font-size:12.5px;line-height:1.7;color:#e8eaed';

    var head = document.createElement('div');
    head.style.cssText = 'font-weight:700;margin-bottom:6px;color:#ff9f0a';
    head.textContent = 'Akun demo — kata sandi: ' + PASSWORD;
    box.appendChild(head);

    Object.keys(USERS).forEach(function (name) {
      var u = USERS[name];
      var row = document.createElement('div');
      var b = document.createElement('b');
      b.textContent = name;
      row.appendChild(b);
      row.appendChild(document.createTextNode(
        ' — ' + (u.role === 'super'
          ? 'melihat semua klien, bisa berpindah'
          : 'hanya ' + (NAMES[u.tenants[0]] || u.tenants[0]))));
      box.appendChild(row);
    });

    var note = document.createElement('div');
    note.style.cssText = 'margin-top:8px;opacity:.7';
    note.textContent = 'Semua angka di dalam demo ini dibuat-buat. ' +
      'Tidak ada nomor WhatsApp atau nama pelanggan yang asli.';
    box.appendChild(note);

    card.appendChild(box);
  });

})(window);
"""


if __name__ == '__main__':
    sys.exit(main())
