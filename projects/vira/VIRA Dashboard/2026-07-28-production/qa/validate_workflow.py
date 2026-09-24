#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_workflow.py — gerbang statis sebelum deploy.

Memeriksa hal-hal yang tidak akan ketahuan dari melihat dashboard di browser:
struktur workflow n8n, kebocoran rahasia, dan apakah frontend benar-benar
generik (tidak diam-diam hardcode salah satu klien).

    python qa/validate_workflow.py

Keluar dengan kode 1 kalau ada satu saja kegagalan.
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
WF = os.path.join(ROOT, 'n8n', 'VIRA-Dashboard-API.json')
SRC = os.path.join(ROOT, 'n8n', 'src')
APP = os.path.join(ROOT, 'app revamp')

results = []


def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    return bool(ok)


# --------------------------------------------------------------- utilitas --

# Karakter yang, kalau muncul terakhir sebelum "/", menandakan "/" itu awal
# regex literal dan bukan operator bagi. Tanpa ini, `replace(/\//g, '_')`
# terbaca sebagai komentar `//` dan sisa barisnya ikut hilang.
_REGEX_PRECEDERS = set('(,=:[!&|?{};+-*%~^<>')


def strip_js(code):
    """
    Ganti string literal, regex literal, dan komentar dengan spasi, sambil
    MEMPERTAHANKAN newline supaya nomor baris tetap benar saat melapor.
    """
    out = []
    i, n = 0, len(code)
    last_sig = ''          # karakter berarti terakhir yang sudah dikeluarkan

    def blank(chunk):
        out.append(''.join('\n' if ch == '\n' else ' ' for ch in chunk))

    while i < n:
        c = code[i]

        # string / template literal
        if c in ('"', "'", '`'):
            q, start = c, i
            i += 1
            while i < n:
                if code[i] == '\\':
                    i += 2
                    continue
                if code[i] == q:
                    i += 1
                    break
                i += 1
            blank(code[start:i])
            last_sig = q
            continue

        # komentar baris
        if c == '/' and i + 1 < n and code[i + 1] == '/' and last_sig not in _REGEX_PRECEDERS:
            start = i
            while i < n and code[i] != '\n':
                i += 1
            blank(code[start:i])
            continue

        # komentar blok
        if c == '/' and i + 1 < n and code[i + 1] == '*':
            start = i + 2
            i += 2
            while i + 1 < n and not (code[i] == '*' and code[i + 1] == '/'):
                i += 1
            blank(code[start:i])
            i += 2
            continue

        # regex literal
        if c == '/' and (last_sig == '' or last_sig in _REGEX_PRECEDERS):
            start, j = i, i + 1
            in_class = False
            closed = False
            while j < n and code[j] != '\n':
                if code[j] == '\\':
                    j += 2
                    continue
                if code[j] == '[':
                    in_class = True
                elif code[j] == ']':
                    in_class = False
                elif code[j] == '/' and not in_class:
                    j += 1
                    closed = True
                    break
                j += 1
            if closed:
                while j < n and code[j].isalpha():   # flag: g i m s u y
                    j += 1
                blank(code[start:j])
                i = j
                last_sig = 'x'
                continue

        out.append(c)
        if not c.isspace():
            last_sig = c
        i += 1
    return ''.join(out)


def balanced(code):
    """Cek keseimbangan kurung pada kode yang sudah dibersihkan."""
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in strip_js(code):
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack


def walk_files(root, exts):
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                yield os.path.join(dirpath, f)


# ------------------------------------------------------ 1. struktur workflow

if not os.path.exists(WF):
    check('workflow ada', False, WF)
    print('workflow belum dibuat — jalankan: python n8n/build_workflow.py')
    sys.exit(1)

with open(WF, 'r', encoding='utf-8') as f:
    raw_wf = f.read()

try:
    wf = json.loads(raw_wf)
    check('workflow JSON valid', True)
except Exception as e:                                   # noqa: BLE001
    check('workflow JSON valid', False, str(e))
    print('JSON rusak, berhenti.')
    sys.exit(1)

nodes = wf['nodes']
conns = wf['connections']
by_name = {}
dupes = []
for nd in nodes:
    if nd['name'] in by_name:
        dupes.append(nd['name'])
    by_name[nd['name']] = nd

check('nama node unik', not dupes, ', '.join(dupes))

# semua referensi di connections menunjuk node yang ada
bad_refs = []
for src, spec in conns.items():
    if src not in by_name:
        bad_refs.append('sumber:' + src)
    for group in spec.get('main', []):
        for c in group:
            if c['node'] not in by_name:
                bad_refs.append('%s -> %s' % (src, c['node']))
check('connections menunjuk node yang ada', not bad_refs, ', '.join(bad_refs))

# reachability dari Webhook
adj = {}
for src, spec in conns.items():
    adj.setdefault(src, [])
    for group in spec.get('main', []):
        for c in group:
            adj[src].append(c['node'])

seen = set()
stack = ['Webhook']
while stack:
    cur = stack.pop()
    if cur in seen:
        continue
    seen.add(cur)
    for nxt in adj.get(cur, []):
        stack.append(nxt)

unreachable = sorted(
    nd['name'] for nd in nodes
    if nd['type'] != 'n8n-nodes-base.stickyNote' and nd['name'] not in seen)
check('semua node terjangkau dari Webhook', not unreachable, ', '.join(unreachable))

# tepat satu respond node, dan semua jalur berujung di sana
responders = [nd['name'] for nd in nodes if nd['type'] == 'n8n-nodes-base.respondToWebhook']
check('tepat satu Respond to Webhook', len(responders) == 1, str(responders))

dead_ends = sorted(
    nd['name'] for nd in nodes
    if nd['type'] not in ('n8n-nodes-base.stickyNote', 'n8n-nodes-base.respondToWebhook')
    and not adj.get(nd['name']))
check('tidak ada cabang buntu (semua berujung di Respond)', not dead_ends, ', '.join(dead_ends))

# switch/if: jumlah output tersambung tidak melebihi yang dideklarasikan
branch_problems = []
for nd in nodes:
    if nd['type'] == 'n8n-nodes-base.switch':
        declared = len(nd['parameters'].get('rules', {}).get('values', []))
        has_fallback = nd['parameters'].get('options', {}).get('fallbackOutput') is not None
        expect = declared + (1 if has_fallback else 0)
        actual = len(conns.get(nd['name'], {}).get('main', []))
        if actual != expect:
            branch_problems.append('%s: %d output disambung, %d diharapkan'
                                   % (nd['name'], actual, expect))
    if nd['type'] == 'n8n-nodes-base.if':
        actual = len(conns.get(nd['name'], {}).get('main', []))
        if actual != 2:
            branch_problems.append('%s: IF harus punya 2 output, ada %d' % (nd['name'], actual))
check('output Switch/IF tersambung lengkap', not branch_problems, ' | '.join(branch_problems))

# ----------------------------------------------- 2. isi Code node & ekspresi

code_nodes = [nd for nd in nodes if nd['type'] == 'n8n-nodes-base.code']
check('ada Code node', len(code_nodes) > 0, '%d node' % len(code_nodes))

unbalanced = [nd['name'] for nd in code_nodes
              if not balanced(nd['parameters'].get('jsCode', ''))]
check('kurung seimbang di semua Code node', not unbalanced, ', '.join(unbalanced))

# $('Nama Node') harus menunjuk node yang benar-benar ada
ref_problems = []
ref_re = re.compile(r"\$\(\s*'([^']+)'\s*\)")
for nd in nodes:
    blob = json.dumps(nd.get('parameters', {}), ensure_ascii=False)
    for m in ref_re.finditer(blob):
        if m.group(1) not in by_name:
            ref_problems.append("%s -> $('%s')" % (nd['name'], m.group(1)))
check("referensi $('Node') valid", not ref_problems, ', '.join(sorted(set(ref_problems))))

# setiap node Google Sheets harus punya credential
sheets = [nd for nd in nodes if nd['type'] == 'n8n-nodes-base.googleSheets']
no_cred = [nd['name'] for nd in sheets if not nd.get('credentials', {}).get('googleApi')]
check('semua node Sheets punya credential', not no_cred, ', '.join(no_cred))
check('ada node Google Sheets', len(sheets) >= 3, '%d node' % len(sheets))

# Setiap node Sheets WAJIB menyatakan authentication: 'serviceAccount'.
#
# Tanpa baris itu node memakai OAuth2 (bawaan n8n), padahal credential yang
# dipasang bertipe service account — node tidak pernah tersambung ke kredensial
# yang benar. Ini yang membuat operasi tulis gagal pada deploy 2026-09-06,
# sementara node yang sudah pernah dibuka di UI diam-diam sudah benar karena
# n8n menuliskannya sendiri.
wrong_auth = [nd['name'] for nd in sheets
              if nd['parameters'].get('authentication') != 'serviceAccount']
check('semua node Sheets memakai serviceAccount', not wrong_auth,
      ', '.join(wrong_auth) if wrong_auth else '%d node' % len(sheets))

# Node append sebaiknya membawa blok `schema` hasil resolusi n8n.
#
# Bukan syarat runtime (Update Bot Mode bekerja tanpanya), tapi tanpa blok itu
# UI n8n melapor "No columns found" dan orang yang deploy harus mengulang
# ritual eksekusi-Retry-publish. Isinya disinkronkan oleh sync_sheets_schema.py
# dari workflow yang sudah jalan — tidak boleh ditulis tangan.
appends = [nd for nd in sheets
           if nd['parameters'].get('operation') in ('append', 'appendOrUpdate')]
no_schema = [nd['name'] for nd in appends
             if not (nd['parameters'].get('columns', {}) or {}).get('schema')]
check('node append membawa schema hasil sinkronisasi', not no_schema,
      ', '.join(no_schema) + ' -- jalankan n8n/sync_sheets_schema.py' if no_schema
      else '%d node append' % len(appends))

# riwayat eksekusi sukses tidak disimpan (body login memuat password plaintext)
check('eksekusi sukses tidak disimpan',
      wf.get('settings', {}).get('saveDataSuccessExecution') == 'none',
      str(wf.get('settings', {}).get('saveDataSuccessExecution')))

check('workflow di-import dalam keadaan non-aktif', wf.get('active') is False,
      'aktifkan manual setelah credential dipilih')

# ----------------------------------------------------- 3. build masih segar

stale = []
for name in ('tenants.js', 'auth.js', 'build-payload.js'):
    p = os.path.join(SRC, name)
    with open(p, 'r', encoding='utf-8') as f:
        body = f.read()
    # ambil beberapa baris penanda yang pasti unik
    markers = [ln.strip() for ln in body.split('\n')
               if ln.strip().startswith('function ') or ln.strip().startswith('var VIRA_')]
    missing = [m for m in markers[:12] if m not in raw_wf]
    if missing:
        stale.append('%s (%d penanda hilang)' % (name, len(missing)))
check('workflow sinkron dengan src/*.js', not stale,
      (', '.join(stale) + ' — jalankan ulang build_workflow.py') if stale else '')

# ------------------------------------------------------ 4. kebocoran rahasia

LEAK_PATTERNS = [
    ('private key Google', r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    ('secret Kirimi', r'\buser_code\b|\bdevice_id\b|api\.kirimi\.id'),
    ('kredensial Anthropic', r'sk-ant-[A-Za-z0-9\-_]{10,}'),
]
leaks = []
for label, pat in LEAK_PATTERNS:
    if re.search(pat, raw_wf):
        leaks.append(label)
check('tidak ada rahasia pihak ketiga di workflow', not leaks, ', '.join(leaks))

# password plaintext yang di-generate tidak boleh nyasar ke workflow / app
CRED_FILE = os.path.join(ROOT, 'docs', 'KREDENSIAL-JANGAN-DIBAGIKAN.txt')
plaintexts = []
if os.path.exists(CRED_FILE):
    with open(CRED_FILE, 'r', encoding='utf-8') as f:
        for m in re.finditer(r'password\s*:\s*(\S+)', f.read(), re.I):
            plaintexts.append(m.group(1))

pw_leaks = []
for pw in plaintexts:
    if len(pw) < 8:
        continue
    if pw in raw_wf:
        pw_leaks.append('workflow')
    for p in walk_files(APP, {'.js', '.html', '.css', '.json', '.webmanifest'}):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            if pw in f.read():
                pw_leaks.append(os.path.relpath(p, ROOT))
check('password plaintext tidak bocor ke workflow/app', not pw_leaks,
      ', '.join(sorted(set(pw_leaks))))

# ------------------------------------------------------- 5. aturan tenant --

with open(os.path.join(SRC, 'tenants.js'), 'r', encoding='utf-8') as f:
    tenants_js = f.read()

check("CORS tidak pernah '*'", "'*'" not in
      re.search(r'corsOrigins:\s*\[(.*?)\]', tenants_js, re.S).group(1),
      'wildcard membuat token bisa dipakai halaman mana pun')

tabs_blocks = re.findall(r'tabs:\s*\[(.*?)\]', tenants_js, re.S)
check('tab CONFIG tidak pernah dibaca',
      all("'CONFIG'" not in b for b in tabs_blocks),
      'CONFIG di Persada memuat private key service account')

check('ada minimal 2 tenant terdaftar', tenants_js.count('sheetId:') >= 2,
      '%d sheetId' % tenants_js.count('sheetId:'))

# ---------------------------------------------- 6. frontend harus generik --

if not os.path.isdir(APP):
    check('folder app/ ada', False, APP)
else:
    check('folder app/ ada', True)

    FORBIDDEN = [
        'thescholars', 'the scholars', 'persada', 'cisoka', 'sulianto',
        'kelas_anak', 'program_interest', 'unit_interest', 'gform',
        'mock_interview', 'lead_source', 'survey_status',
        '1tejyays0pq', '1pzgurzbdxc',
    ]
    hits = []
    app_files = list(walk_files(APP, {'.js', '.html', '.css', '.webmanifest', '.json'}))
    for p in app_files:
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            low = f.read().lower()
        for word in FORBIDDEN:
            if word in low:
                hits.append('%s: "%s"' % (os.path.relpath(p, ROOT), word))
    check('frontend tidak hardcode klien/skema tertentu', not hits, ' | '.join(hits))

    # tidak ada dependensi eksternal
    ext = []
    url_re = re.compile(r'https?://[^\s"\'<>)]+', re.I)
    ALLOW_HOST = ('n8n.srv1270416.hstgr.cloud', 'localhost', '127.0.0.1',
                  'www.w3.org', 'schema.org')
    for p in app_files:
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            body = f.read()
        for m in url_re.finditer(body):
            u = m.group(0)
            if not any(h in u for h in ALLOW_HOST):
                ext.append('%s: %s' % (os.path.relpath(p, ROOT), u[:70]))
    check('tidak ada dependensi eksternal di frontend', not ext, ' | '.join(sorted(set(ext))))

    # service worker tidak boleh menyimpan respons API
    swp = os.path.join(APP, 'sw.js')
    if os.path.exists(swp):
        with open(swp, 'r', encoding='utf-8', errors='ignore') as f:
            sw = f.read()
        check('service worker tidak meng-cache API',
              ('vira-dash' in sw or 'api' in sw.lower()),
              'sw.js harus secara eksplisit melewati request API (network-only)')
    else:
        check('sw.js ada', False)

# ------------------------------------------------------------------ hasil --

print()
width = max(len(r[0]) for r in results) + 2
failed = 0
for name, ok, detail in results:
    mark = 'PASS' if ok else 'GAGAL'
    line = '  [%-5s] %s' % (mark, name.ljust(width))
    if detail and not ok:
        line += '  -> ' + detail[:300]
    elif detail and ok:
        line += '  (' + detail[:80] + ')'
    print(line)
    if not ok:
        failed += 1

print()
print('  %d pemeriksaan, %d gagal' % (len(results), failed))
sys.exit(1 if failed else 0)
