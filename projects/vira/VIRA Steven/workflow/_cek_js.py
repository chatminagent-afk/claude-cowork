# -*- coding: utf-8 -*-
"""Pemeriksa keseimbangan token JS: (){}[] di luar string/template/komentar/regex."""
import json, io, sys

BS = chr(92)  # backslash


def scan(src):
    i, n = 0, len(src)
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    prev_sig = ''
    line = 1

    def kulit_template(j):
        """Lanjutkan isi template literal dari posisi j. Kembalikan (j_baru, mode)."""
        nonlocal line
        while j < n:
            if src[j] == BS:
                j += 2
                continue
            if src[j] == '`':
                return j, 'tutup'
            if src.startswith('${', j):
                return j + 2, 'subst'
            if src[j] == '\n':
                line += 1
            j += 1
        return j, 'gagal'

    while i < n:
        c = src[i]
        if c == '\n':
            line += 1; i += 1; continue
        if c in ' \t\r':
            i += 1; continue
        if src.startswith('//', i):
            j = src.find('\n', i)
            i = n if j < 0 else j
            continue
        if src.startswith('/*', i):
            j = src.find('*/', i + 2)
            if j < 0:
                return 'komentar blok tidak ditutup (baris %d)' % line
            line += src.count('\n', i, j)
            i = j + 2
            continue
        if c in '"' + "'":
            q, j = c, i + 1
            while j < n:
                if src[j] == BS:
                    j += 2; continue
                if src[j] == q:
                    break
                if src[j] == '\n':
                    return 'string %s tidak ditutup (baris %d)' % (q, line)
                j += 1
            if j >= n:
                return 'string %s tidak ditutup (baris %d)' % (q, line)
            i = j + 1; prev_sig = 'x'; continue
        if c == '`':
            j, mode = kulit_template(i + 1)
            if mode == 'gagal':
                return 'template literal tidak ditutup (baris %d)' % line
            if mode == 'tutup':
                i = j + 1; prev_sig = 'x'; continue
            stack.append('${'); i = j; continue
        if c == '/' and prev_sig in ('', '(', ',', '=', ':', '[', '!', '&', '|', '?', '{', ';', 'return'):
            j = i + 1; incls = False
            while j < n:
                if src[j] == BS:
                    j += 2; continue
                if src[j] == '[':
                    incls = True
                elif src[j] == ']':
                    incls = False
                elif src[j] == '/' and not incls:
                    break
                elif src[j] == '\n':
                    return 'regex tidak ditutup (baris %d)' % line
                j += 1
            if j >= n:
                return 'regex tidak ditutup (baris %d)' % line
            i = j + 1
            while i < n and src[i].isalpha():
                i += 1
            prev_sig = 'x'; continue
        if c in '([{':
            stack.append(c); prev_sig = c; i += 1; continue
        if c in ')]}':
            if c == '}' and stack and stack[-1] == '${':
                stack.pop()
                j, mode = kulit_template(i + 1)
                if mode == 'gagal':
                    return 'template literal tidak ditutup setelah ${} (baris %d)' % line
                if mode == 'tutup':
                    i = j + 1; prev_sig = 'x'; continue
                stack.append('${'); i = j; continue
            if not stack or stack[-1] != pairs[c]:
                return '"%s" tidak berpasangan (baris %d)' % (c, line)
            stack.pop(); prev_sig = c; i += 1; continue
        j = i
        while j < n and (src[j].isalnum() or src[j] in '_$'):
            j += 1
        if j > i:
            kata = src[i:j]
            prev_sig = kata if kata == 'return' else 'x'
            i = j; continue
        prev_sig = c; i += 1
    if stack:
        return 'belum tertutup sampai akhir: %s' % stack
    return None


d = json.load(io.open(sys.argv[1], encoding='utf-8'))
gagal = total = 0
for nd in d['nodes']:
    js = nd.get('parameters', {}).get('jsCode')
    if not js:
        continue
    total += 1
    err = scan(js)
    if err:
        gagal += 1
        print('!! %s: %s' % (nd['name'], err))
print('code node diperiksa: %d | bermasalah: %d' % (total, gagal))
