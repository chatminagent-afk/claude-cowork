# -*- coding: utf-8 -*-
"""Validasi struktural VIRA Steven Main terhadap skema sheet."""
import json, io, re, sys, openpyxl

WF = r'D:\Documents\Claude Cowork\VIRA Steven\workflow\2026-08-15-VIRA-Steven-Main.json'
# Unduhan spreadsheet LIVE. Steven mengganti nama filenya 2026-08-16 saat menarik
# versi yang sedang berjalan; jangan kembalikan ke nama lama.
XL = r'D:\Documents\Claude Cowork\VIRA Steven\sheet\VIRA Database.xlsx'

d = json.load(io.open(WF, encoding='utf-8'))
N = {n['name']: n for n in d['nodes']}
raw = json.dumps(d, ensure_ascii=False)
wb = openpyxl.load_workbook(XL, read_only=True)
TABS = {ws.title: [c.value for c in next(ws.iter_rows(min_row=1, max_row=1)) if c.value]
        for ws in wb.worksheets}
masalah = []


def cek(judul, fn):
    print('--- %s ---' % judul)
    fn()
    print()


def c1():
    for n in d['nodes']:
        if not n['type'].endswith('googleSheets'):
            continue
        p = n['parameters']
        sn = p.get('sheetName')
        sn = sn.get('value') if isinstance(sn, dict) else sn
        if not isinstance(sn, str):
            masalah.append('%s: sheetName bukan nama tab (%r)' % (n['name'], sn)); continue
        if sn not in TABS:
            masalah.append('%s: tab "%s" tidak ada di sheet' % (n['name'], sn)); continue
        cols = p.get('columns', {}).get('value')
        if not isinstance(cols, dict):
            continue
        for c in cols:
            if c == 'row_number':
                continue
            if c != c.strip():
                masalah.append('%s: kolom "%s" ada spasi di ujung' % (n['name'], c))
            elif c not in TABS[sn]:
                masalah.append('%s: kolom "%s" tidak ada di tab %s' % (n['name'], c, sn))
        mc = p.get('columns', {}).get('matchingColumns') or []
        for c in mc:
            if c not in TABS[sn]:
                masalah.append('%s: matching "%s" tidak ada di tab %s' % (n['name'], c, sn))
    print('  node Sheets diperiksa:', sum(1 for n in d['nodes'] if n['type'].endswith('googleSheets')))


def c2():
    bad = [n['name'] for n in d['nodes']
           if isinstance(n.get('parameters', {}).get('documentId'), dict)
           and n['parameters']['documentId'].get('value') != '1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk']
    if bad:
        masalah.append('documentId bukan sheet VIRA Steven: %s' % bad)
    print('  documentId seragam:', not bad)


def c3():
    sysmsg = N['AI Agent']['parameters']['options']['systemMessage']
    rakit = N['Rakit Konteks']['parameters']['jsCode']
    for v in ['prospect_context', 'about_context', 'program_context',
              'links_context', 'faq_context', 'brief_context']:
        pakai = ('{{ $json.%s }}' % v) in sysmsg
        prod = re.search(r'^\s{4}%s,\s*$' % v, rakit, re.M) is not None
        print('   %-18s prompt=%-5s Rakit=%s' % (v, pakai, prod))
        if not (pakai and prod):
            masalah.append('variabel konteks %s putus' % v)


def c4():
    pa = N['Process All']['parameters']['jsCode']
    for r in sorted(set(re.findall(r"\$\('Process All'\)\.first\(\)\.json\.([A-Za-z_][A-Za-z0-9_]*)", raw))):
        if not re.search(r'\b%s\s*[,:]' % re.escape(r), pa):
            masalah.append('Process All tidak memproduksi "%s" padahal dirujuk' % r)
    ru = N['Resolve User Row']['parameters']['jsCode']
    for r in sorted(set(re.findall(r"\$\('Resolve User Row'\)\.first\(\)\.json\.([A-Za-z_][A-Za-z0-9_]*)", raw))):
        if not re.search(r'\b%s:' % re.escape(r), ru):
            masalah.append('Resolve User Row tidak memproduksi "%s" padahal dirujuk' % r)
    mb = N['Merge Brief']['parameters']['jsCode']
    for r in sorted(set(re.findall(r"\$\('Merge Brief'\)\.first\(\)\.json\.([A-Za-z_][A-Za-z0-9_]*)", raw))):
        if r not in mb:
            masalah.append('Merge Brief tidak memproduksi "%s"' % r)
    print('  referensi antar-node: %d rujukan diperiksa' %
          len(set(re.findall(r"\$\('[^']+'\)\.first\(\)\.json", raw))))


def c5():
    """setiap $('X') di KODE AKTIF harus menunjuk node yang ada (komentar diabaikan)"""
    aktif = []
    for n in d['nodes']:
        js = n.get('parameters', {}).get('jsCode')
        if not js:
            aktif.append(json.dumps(n.get('parameters', {}), ensure_ascii=False)); continue
        bersih = re.sub(r'/\*.*?\*/', '', js, flags=re.S)
        bersih = '\n'.join(re.sub(r'//.*$', '', b) for b in bersih.split('\n'))
        aktif.append(bersih)
    dirujuk = set(re.findall(r"\$\('([^']+)'\)", '\n'.join(aktif)))
    for nm in sorted(dirujuk):
        if nm not in N:
            masalah.append("referensi ke node yang tidak ada: $('%s')" % nm)
    print('  node yang dirujuk dari kode aktif:', len(dirujuk))


def c6():
    rantai = ['IF Deck Request', 'Read REQUESTS', 'Merge Brief', 'Write REQUESTS',
              'Wait Deck', 'Update STATS Brief', 'Notify Admin Deck']
    for a, b in zip(rantai, rantai[1:]):
        t = [c['node'] for br in d['connections'].get(a, {}).get('main', []) for c in (br or [])]
        ok = b in t
        print('   %-20s -> %-20s %s' % (a, b, 'ok' if ok else '!! PUTUS'))
        if not ok:
            masalah.append('rantai deck putus: %s -> %s' % (a, b))
    src = [c['node'] for br in d['connections']['Process All']['main'] for c in (br or [])]
    print('   Process All -> IF Deck Request:', 'ok' if 'IF Deck Request' in src else '!! PUTUS')
    if 'IF Deck Request' not in src:
        masalah.append('Process All tidak menyambung ke IF Deck Request')


def c7():
    sisa = []
    for n in d['nodes']:
        s = json.dumps(n, ensure_ascii=False)
        for pat in ['[PCR]', 'PCR_Database', 'Persada Cisoka', 'field_team_phone',
                    'media_team_phone', 'pending_survey_tanggal ', 'SCHEDULE_SURVEY',
                    'REQUEST_CALL', 'Read LINGKUNGAN Data']:
            if pat in s:
                sisa.append('%s :: %s' % (n['name'], pat))
    for x in sisa:
        print('   sisa:', x)
    if not sisa:
        print('   tidak ada sisa penanda Persada di jalur aktif')


for j, f in [('1. kolom tulis vs skema sheet', c1), ('2. documentId', c2),
             ('3. variabel konteks', c3), ('4. field antar-node', c4),
             ('5. referensi node', c5), ('6. rantai DECK_REQUEST', c6),
             ('7. sisa jejak Persada', c7)]:
    cek(j, f)

print('=' * 60)
if masalah:
    print('MASALAH (%d):' % len(masalah))
    for m in masalah:
        print('  !!', m)
    sys.exit(1)
print('SEMUA PEMERIKSAAN LOLOS')
