#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_sheets_schema.py — ambil daftar kolom hasil resolusi n8n dari workflow
yang SUDAH JALAN, simpan ke sheets-schema.json supaya build berikutnya
membawanya sejak awal.

Kenapa ini ada
--------------
Node Google Sheets menyimpan `columns.schema`: daftar kolom yang dibaca n8n
dari spreadsheet sungguhan. Isinya tidak bisa ditebak dari kode — field
Document/Sheet di workflow ini diisi ekspresi (`{{ $json.doc_id }}`), jadi saat
node dibuka di UI n8n belum tahu spreadsheet mana yang dimaksud dan melapor
"No columns found in Google Sheets".

Akibatnya, setiap import workflow hasil generate MENIMPA hasil resolusi itu
dengan kosong, dan orang yang deploy harus mengulang ritual: eksekusi sekali →
Retry → publish ulang, untuk tiap node tulis. Itu yang terjadi pada deploy
2026-09-06.

Cara pakai
----------
Setiap kali struktur kolom sheet berubah, atau setelah ritual di atas dijalankan:

    1. n8n → workflow yang jalan → Download → simpan sebagai
       n8n/VIRA Dashboard API.json
    2. python n8n/sync_sheets_schema.py
    3. python n8n/build_workflow.py

Kalau sheets-schema.json tidak ada, build_workflow.py tetap jalan — node append
hanya dibangun tanpa blok schema, persis seperti node Update Bot Mode yang
selama ini bekerja tanpa blok itu.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT = os.path.join(HERE, 'VIRA Dashboard API.json')
OUT = os.path.join(HERE, 'sheets-schema.json')


def main():
    if not os.path.exists(EXPORT):
        print('[!] tidak menemukan %s' % os.path.basename(EXPORT))
        print('    Download workflow yang sedang jalan dari n8n ke folder ini dulu.')
        return 1

    with open(EXPORT, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    out = {}
    for node in wf.get('nodes', []):
        if node.get('type') != 'n8n-nodes-base.googleSheets':
            continue
        schema = (node.get('parameters', {}).get('columns', {}) or {}).get('schema')
        if not schema:
            continue
        # Disimpan APA ADANYA, bukan cuma nama kolomnya. n8n menyisipkan
        # penanda seperti `removed: false` pada kolom yang tidak dipetakan;
        # menirunya dengan aturan buatan sendiri hanya akan meleset lagi.
        out[node['name']] = schema

    if not out:
        print('[!] tidak ada node Sheets dengan schema di ekspor itu.')
        print('    Jalankan dulu tiap node tulis sekali di n8n, lalu simpan & ekspor ulang.')
        return 1

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('[ok] %s' % os.path.basename(OUT))
    for name in sorted(out):
        print('     %-24s %d kolom' % (name, len(out[name])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
