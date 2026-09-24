#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_wfb.py — tempelkan cabang rekomendasi AI ke workflow "Monthly Rollup (WF-B)".

Basisnya adalah ekspor workflow yang SEDANG JALAN (`Monthly Rollup (WF-B).json`).
Script ini tidak menulis ulang workflow itu dari nol: ia memuat apa adanya, lalu
menambahkan cabang baru. Node dan koneksi lama tidak disentuh sama sekali.

BENTUK YANG DIPILIH — dan kenapa

    Rollup Bulan Lalu ─┬─→ Write MONTHLY_SUMMARY        (jalur lama, utuh)
                       └─→ Read STATS → Build Insight Request
                             → Ask Anthropic → Write AI Column

Cabang AI berdiri SEJAJAR, bukan menyisip di tengah. Konsekuensinya penting:
apa pun yang terjadi pada Anthropic — mati, lambat, membalas ngawur — baris
rekap bulanan tetap tertulis. Rekap itu fitur yang sudah berjalan sejak Agustus;
menambah rekomendasi tidak boleh membuatnya bergantung pada layanan luar.

Penulisan kolom AI memakai appendOrUpdate yang mencocokkan `bulan`, sama seperti
node aslinya, jadi ia MEMPERBARUI baris bulan yang sama — bukan menambah baris
kedua. Ini juga yang membuat menjalankan ulang workflow aman: hasilnya idempoten.

Tab apa saja yang dibaca, dan kenapa
    PROGRAM  katalog produk: batch, kuota, harga, deadline, status. Ini yang
             mengubah "IELTS banyak ditanya" menjadi keputusan yang bisa
             diambil pemilik usaha.
    UNKNOWN  pertanyaan yang tidak terjawab bulan itu.
    FAQ      pertanyaannya saja, supaya model berhenti menyarankan membuat
             jawaban yang SUDAH ada.
    CONFIG   TIDAK PERNAH dibaca. Aturan keras proyek ini.

    Sebaran hari & jam diambil dari TOPIC_LOG (kolom last_ts, epoch milidetik),
    bukan dari STATS. STATS memuat seluruh lead sepanjang masa; memakainya
    membuat angka bulanan berdiri di sebelah angka sepanjang masa, dan yang
    membacanya pasti mengira keduanya satu periode.

Jalankan ulang setiap kali src/*.js berubah:
    python n8n/build_wfb.py
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
BASE = os.path.join(HERE, 'Monthly Rollup (WF-B).json')
OUT = os.path.join(HERE, 'Monthly-Rollup-WF-B.json')

# Kredensial Google milik WF-B — SA bot, BUKAN SA dashboard. Diambil dari node
# yang sudah ada di workflow supaya tidak mungkin salah ketik.
ANTHROPIC_CRED_ID = 'oO9D2lMQoz5UOhu8'
ANTHROPIC_CRED_NAME = 'Anthropic The Scholars'

# Sonnet 4.6: model yang sudah terbukti jalan di akun Anthropic ini (dipakai
# Topic Harvester). Jangan diganti tanpa menjalankan WF-B manual sekali dulu —
# id model yang tidak dikenali membuat node gagal tanpa pesan di dashboard.
ANTHROPIC_MODEL = 'claude-sonnet-4-6'

TENANT_ID = 'thescholars'


def read_src(name):
    with open(os.path.join(SRC, name), 'r', encoding='utf-8') as f:
        code = f.read()
    code = re.sub(r"\nif \(typeof module !== 'undefined'.*?\n\}\n?$", '\n', code, flags=re.S)
    return code.rstrip() + '\n'


LIB_TENANTS = read_src('tenants.js')
LIB_PAYLOAD = read_src('build-payload.js')
LIB_INSIGHT = read_src('insight.js')

BANNER = (
    "// === DI-GENERATE OLEH n8n/build_wfb.py — JANGAN EDIT DI UI n8n ===\n"
    "// Sumbernya ada di n8n/src/*.js. Edit di sana lalu jalankan ulang script.\n"
)

CONST = "const AI_MODEL = '%s';\nconst AI_TENANT = '%s';\n" % (ANTHROPIC_MODEL, TENANT_ID)


JS_BUILD_REQUEST = LIB_TENANTS + LIB_PAYLOAD + LIB_INSIGHT + CONST + r"""
/* -------------------------------------------------------------------------
 * Build Insight Request — susun fakta bulan sasaran menjadi permintaan.
 *
 * SEMUA angka dibatasi ke bulan yang sama. Versi pertama mencampur topik
 * bulanan dengan sebaran hari sepanjang masa, dan hasilnya menyesatkan.
 * Sebaran hari/jam sekarang dihitung dari TOPIC_LOG bulan itu saja.
 *
 * Mengembalikan NOL ITEM kalau bulan itu tidak punya topik. n8n memperlakukan
 * cabang tanpa item sebagai selesai, jadi node Anthropic di belakangnya tidak
 * dijalankan — tidak ada permintaan, tidak ada biaya.
 * ---------------------------------------------------------------------- */
const rollup = $('Rollup Bulan Lalu').first().json;
const profile = VIRA_TENANTS[AI_TENANT];

let topik = [];
try { topik = JSON.parse(rollup.top_json || '[]'); } catch (e) { topik = []; }

function rowsOf(nodeName) {
  try {
    return $(nodeName).all().map(i => i.json).filter(r => r && typeof r === 'object');
  } catch (e) {
    console.log('Tab ' + nodeName + ' tidak terbaca, dilewati.');
    return [];
  }
}

const facts = vdInsightFacts({
  bulan: vdMonthLabel(rollup.bulan),
  bulanKey: rollup.bulan,
  bisnis: profile.aiContext,
  klien: profile.name,
  catatan_cakupan: rollup.coverage_note,
  total_user: rollup.total_user_unik,
  total_pesan: rollup.total_pesan,
  topik: topik,
  labelMap: profile.topicLabels,
  topicLogRows: rowsOf('Read TOPIC_LOG'),
  programRows: rowsOf('Read PROGRAM'),
  unknownRows: rowsOf('Read UNKNOWN'),
  faqRows: rowsOf('Read FAQ')
});

if (!facts) {
  console.log('Tidak ada topik bulan ' + rollup.bulan + ' — AI dilewati.');
  return [];
}

console.log('Fakta siap: ' + facts.topik.length + ' topik, ' +
            facts.program.length + ' program, ' +
            facts.belum_terjawab.length + ' pertanyaan belum terjawab.');

return [{ json: { _facts: facts, _body: vdInsightBody(facts, AI_MODEL) } }];
"""


JS_WRITE_AI = LIB_TENANTS + LIB_PAYLOAD + LIB_INSIGHT + CONST + r"""
/* -------------------------------------------------------------------------
 * Prepare AI Column — ubah balasan Anthropic menjadi isi sel `ai_insight_json`.
 *
 * Mengembalikan NOL ITEM kalau tidak ada satu pun butir yang utuh, sehingga
 * node tulis di belakangnya tidak berjalan dan kolomnya dibiarkan apa adanya.
 * Menulis blok setengah jadi lebih berbahaya daripada tidak menulis: yang
 * membacanya akan mengira saran yang terpotong itu utuh.
 *
 * Alasan kegagalan SELALU ditulis ke console. Tanpa itu, node ini hanya
 * mengeluarkan larik kosong dan tidak ada cara tahu kenapa — persis yang
 * terjadi pada percobaan 2026-09-06, ketika balasan terpotong karena jatah
 * token habis dan tidak ada satu pun petunjuk di layar.
 * ---------------------------------------------------------------------- */
const rollup = $('Rollup Bulan Lalu').first().json;
const raw = $input.first().json || {};

const stop = String(raw.stop_reason || '');
const teks = (raw.content && raw.content[0] && raw.content[0].text) || '';

if (raw.error || (!teks && !raw.content)) {
  console.log('Anthropic tidak menjawab: ' +
    JSON.stringify(raw.error || raw).slice(0, 300));
  return [];
}
if (stop === 'max_tokens') {
  console.log('Balasan terpotong (max_tokens habis). Butir yang utuh tetap dipungut.');
}

const parsed = vdInsightParse(raw, AI_MODEL);

if (!parsed) {
  console.log('Rekomendasi dilewati: tidak ada butir utuh. stop_reason=' + stop +
              ' | awal balasan: ' + String(teks).slice(0, 200));
  return [];
}

console.log('Rekomendasi siap: ' + parsed.items.length + ' butir untuk ' +
            rollup.bulan + (parsed.truncated ? ' (dipungut dari balasan terpotong)' : ''));

return [{ json: {
  bulan: rollup.bulan,
  ai_insight_json: JSON.stringify(parsed)
}}];
"""


def code_node(name, js, position):
    return {
        'parameters': {'jsCode': BANNER + js},
        'id': name.lower().replace(' ', '-'),
        'name': name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': position,
    }


def main():
    if not os.path.exists(BASE):
        print('[!] tidak menemukan %s' % os.path.basename(BASE))
        print('    Download workflow "Monthly Rollup (WF-B)" dari n8n ke folder ini dulu.')
        return 1

    with open(BASE, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    by_name = {n['name']: n for n in wf['nodes']}
    for need in ('Rollup Bulan Lalu', 'Write MONTHLY_SUMMARY', 'Read TOPIC_LOG'):
        if need not in by_name:
            print('[!] node "%s" tidak ada di basis — struktur WF-B berubah.' % need)
            return 1

    # Kredensial Google diambil dari node yang sudah ada: WF-B memakai service
    # account bot (bukan milik dashboard), dan menyalinnya menghindari salah id.
    gcred = by_name['Read TOPIC_LOG']['credentials']
    doc_id = by_name['Write MONTHLY_SUMMARY']['parameters']['documentId']['value']

    base_pos = by_name['Rollup Bulan Lalu']['position']
    x0, y0 = base_pos[0], base_pos[1] + 260

    def sheet_node(name, params, dx, dy=0, tolerant=False):
        node = {
            'parameters': params,
            'id': name.lower().replace(' ', '-'),
            'name': name,
            'type': 'n8n-nodes-base.googleSheets',
            'typeVersion': 4.5,
            'position': [x0 + dx, y0 + dy],
            'credentials': gcred,
        }
        if tolerant:
            # Hanya untuk node BACA. Tab kosong atau gagal dibaca tidak boleh
            # mematikan cabang: fakta yang hilang cukup membuat sarannya kurang
            # tajam, bukan hilang.
            node['alwaysOutputData'] = True
            node['onError'] = 'continueRegularOutput'
        return node

    def read_node(name, tab, dx):
        return sheet_node(name, {
            'authentication': 'serviceAccount',
            'documentId': {'__rl': True, 'value': doc_id, 'mode': 'id'},
            'sheetName': {'__rl': True, 'value': tab, 'mode': 'name'},
            'options': {},
        }, dx, tolerant=True)

    new_nodes = [
        # Tab CONFIG SENGAJA tidak pernah dibaca — aturan keras proyek ini.
        read_node('Read PROGRAM', 'PROGRAM', 0),
        read_node('Read UNKNOWN', 'UNKNOWN', 220),
        read_node('Read FAQ', 'FAQ', 440),

        code_node('Build Insight Request', JS_BUILD_REQUEST, [x0 + 660, y0]),

        {
            'parameters': {
                'method': 'POST',
                'url': 'https://api.anthropic.com/v1/messages',
                'authentication': 'predefinedCredentialType',
                'nodeCredentialType': 'anthropicApi',
                'sendHeaders': True,
                'headerParameters': {'parameters': [
                    {'name': 'anthropic-version', 'value': '2023-06-01'},
                    {'name': 'content-type', 'value': 'application/json'},
                ]},
                'sendBody': True,
                'specifyBody': 'json',
                'jsonBody': '={{ JSON.stringify($json._body) }}',
                'options': {'timeout': 120000},
            },
            'id': 'ask-anthropic',
            'name': 'Ask Anthropic',
            'type': 'n8n-nodes-base.httpRequest',
            'typeVersion': 4.2,
            'position': [x0 + 880, y0],
            # Rekomendasi itu tambahan, bukan syarat. Kegagalannya tidak boleh
            # menjatuhkan eksekusi — baris rekap sudah tertulis di cabang lain.
            'alwaysOutputData': True,
            'onError': 'continueRegularOutput',
            'credentials': {'anthropicApi': {'id': ANTHROPIC_CRED_ID,
                                             'name': ANTHROPIC_CRED_NAME}},
        },

        code_node('Prepare AI Column', JS_WRITE_AI, [x0 + 1100, y0]),

        sheet_node('Write AI Column', {
            'authentication': 'serviceAccount',
            'operation': 'appendOrUpdate',
            'documentId': {'__rl': True, 'value': doc_id, 'mode': 'id'},
            'sheetName': {'__rl': True, 'value': 'MONTHLY_SUMMARY', 'mode': 'name'},
            'columns': {
                'mappingMode': 'defineBelow',
                'value': {
                    'bulan': '={{ $json.bulan }}',
                    'ai_insight_json': '={{ $json.ai_insight_json }}',
                },
                # Mencocokkan `bulan` seperti node aslinya: baris bulan itu
                # DIPERBARUI, bukan ditambah lagi. Menjalankan ulang aman.
                'matchingColumns': ['bulan'],
                'schema': [],
                'attemptToConvertTypes': False,
                'convertFieldsToString': False,
            },
            'options': {},
        # SENGAJA tanpa onError: baris rekap sudah tertulis di cabang lain,
        # jadi gagal di sini tidak menghilangkan apa pun yang penting — tapi
        # tetap harus terlihat lewat errorWorkflow, bukan ditelan diam-diam.
        }, 1320),
    ]

    existing = set(by_name)
    for n in new_nodes:
        if n['name'] in existing:
            print('[!] node "%s" sudah ada di basis — hentikan supaya tidak menimpa.' % n['name'])
            return 1
    wf['nodes'].extend(new_nodes)

    # Rollup bercabang dua. Write MONTHLY_SUMMARY disebut DULUAN supaya baris
    # rekap tertulis lebih dulu, sebelum cabang AI menyentuh apa pun.
    def conn(name):
        return {'node': name, 'type': 'main', 'index': 0}

    wf['connections']['Rollup Bulan Lalu'] = {'main': [[
        conn('Write MONTHLY_SUMMARY'),
        conn('Read PROGRAM'),
    ]]}
    wf['connections']['Read PROGRAM'] = {'main': [[conn('Read UNKNOWN')]]}
    wf['connections']['Read UNKNOWN'] = {'main': [[conn('Read FAQ')]]}
    wf['connections']['Read FAQ'] = {'main': [[conn('Build Insight Request')]]}
    wf['connections']['Build Insight Request'] = {'main': [[conn('Ask Anthropic')]]}
    wf['connections']['Ask Anthropic'] = {'main': [[conn('Prepare AI Column')]]}
    wf['connections']['Prepare AI Column'] = {'main': [[conn('Write AI Column')]]}

    # Di-import dalam keadaan non-aktif: ini cron produksi, aktifkan manual
    # setelah dijalankan sekali dan hasilnya diperiksa.
    wf['active'] = False

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)

    print('[ok] %s  (%d node, %.1f KB)' % (
        os.path.basename(OUT), len(wf['nodes']), os.path.getsize(OUT) / 1024.0))

    names = set(n['name'] for n in wf['nodes'])
    missing = []
    for src, spec in wf['connections'].items():
        if src not in names:
            missing.append(src)
        for group in spec.get('main', []):
            for c in group:
                if c['node'] not in names:
                    missing.append(c['node'])
    if missing:
        print('[!] node tidak dikenal di connections: %s' % sorted(set(missing)))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
