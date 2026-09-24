# -*- coding: utf-8 -*-
"""
Uji logika parser [DECK_REQUEST] / [FACTS] / pembersihan tag.
Pola regex disalin PERSIS dari jsCode 'Process All' yang dihasilkan _transform.py,
lalu dijalankan dengan padanan Python. Yang diuji: perilaku parser, bukan runtime n8n.
"""
import re, json, io, sys

WF = r'D:\Documents\Claude Cowork\VIRA Steven\workflow\2026-08-15-VIRA-Steven-Main.json'
d = json.load(io.open(WF, encoding='utf-8'))
PA = next(n for n in d['nodes'] if n['name'] == 'Process All')['parameters']['jsCode']

# pastikan pola di bawah memang yang dipakai node-nya
for pola in [r"/\[\s*DECK_REQUEST\s*\]([\s\S]*?)\[\s*\/\s*DECK_REQUEST\s*\]/i",
             r"/^\s*([A-Za-z_]+)\s*:\s*(.*)$/",
             '/(^|[\\s\\[])nama\\s*=\\s*"([^"]*)"/i']:
    if pola not in PA:
        print('!! pola tidak ditemukan di Process All:', pola); sys.exit(1)

DECK_FIELDS = ['nama','jabatan','nama_bisnis','industri','deskripsi_bisnis','target_pelanggan',
 'channel','sumber_leads','volume_chat_harian','jam_operasional','siapa_balas_chat',
 'biaya_admin_bulanan','sistem_sekarang','masalah_utama','pain_points','aksi_utama',
 'alur_setelah_chat','pertanyaan_tersering','fitur_diminati','nilai_transaksi',
 'prospek_per_bulan','minat_paket','budget_range','deadline','urgensi','bahasa_deck','catatan']
FACT_FIELDS = ['nama_lengkap','nama_bisnis','industri','masalah_utama','volume_chat','budget_range','minat_paket']


def bersih(s, mx=200):
    s = ''.join(c for c in str(s or '') if ord(c) >= 32)
    return re.sub(r'\s+', ' ', s).strip()[:mx]


def kosong(s):
    t = re.sub(r'[.\s]+$', '', bersih(s).lower())
    return t in ('', '-', '...', 'belum disebut', 'belum tahu', 'tidak disebut', 'n/a', 'na', 'null', 'undefined')


def parse(ai, prev):
    facts = {}
    fm = re.search(r'\[\s*FACTS\b([^\]]*)\]', ai, re.I)
    if fm and fm.group(1):
        isi = fm.group(1)
        for f in FACT_FIELDS:
            m = re.search(f + r'\s*=\s*"([^"]*)"', isi, re.I)
            if m:
                facts[f] = m.group(1)
        mn = re.search(r'(^|[\s\[])nama\s*=\s*"([^"]*)"', isi, re.I)
        if mn and 'nama_lengkap' not in facts:
            facts['nama_lengkap'] = mn.group(2)
    merged, changed = {}, {}
    for f in FACT_FIELDS:
        mx = 300 if f == 'masalah_utama' else (60 if f == 'nama_lengkap' else 120)
        baru = '' if kosong(facts.get(f)) else bersih(facts.get(f), mx)
        lama = bersih(prev.get(f), mx)
        merged[f] = baru or lama
        changed[f] = merged[f] != '' and merged[f] != lama

    deck = {f: '' for f in DECK_FIELDS}
    is_deck, ditolak, kurang = False, False, []
    blk = re.search(r'\[\s*DECK_REQUEST\s*\]([\s\S]*?)\[\s*/\s*DECK_REQUEST\s*\]', ai, re.I)
    if blk:
        is_deck = True
        for baris in blk.group(1).split('\n'):
            m = re.match(r'^\s*([A-Za-z_]+)\s*:\s*(.*)$', baris)
            if not m:
                continue
            k = m.group(1).lower()
            if k not in deck:
                continue
            deck[k] = '' if kosong(m.group(2)) else bersih(m.group(2), 500)
        if not deck['nama'] and merged['nama_lengkap']:
            deck['nama'] = merged['nama_lengkap']
        for dk, fk in [('nama_bisnis','nama_bisnis'),('industri','industri'),('masalah_utama','masalah_utama'),
                       ('minat_paket','minat_paket'),('budget_range','budget_range'),('volume_chat_harian','volume_chat')]:
            if not deck[dk] and merged[fk]:
                deck[dk] = merged[fk]
        kurang = [f for f in ('nama_bisnis','industri','masalah_utama') if not deck[f]]
        if kurang:
            is_deck, ditolak = False, True

    out = ai
    out = re.sub(r'\[\s*DECK_REQUEST\s*\][\s\S]*?\[\s*/\s*DECK_REQUEST\s*\]', '', out, flags=re.I)
    out = re.sub(r'\[\s*/?\s*DECK_REQUEST\s*\][\s\S]*$', '', out, flags=re.I)
    out = re.sub(r'\[\s*SEND_MEDIA\s*(?::[^\]]*)?\]', '', out, flags=re.I)
    out = re.sub(r'\[TALK_TO_ADMIN\]', '', out, flags=re.I)
    out = re.sub(r'\[UNKNOWN\]', '', out, flags=re.I)
    out = re.sub(r'\[\s*FACTS\b[^\]]*\]', '', out, flags=re.I)
    return dict(deck=deck, is_deck=is_deck, ditolak=ditolak, kurang=kurang,
                merged=merged, changed=changed, clean=out.strip())


gagal = []


def uji(nama, syarat):
    print(('  OK   ' if syarat else '  GAGAL') + '  ' + nama)
    if not syarat:
        gagal.append(nama)


print('=== 1. brief lengkap, prospek baru ===')
ai1 = """[DECK_REQUEST]
nama: Rina
jabatan: owner
nama_bisnis: Rasa Nusantara
industri: F&B / katering
deskripsi_bisnis: Katering harian untuk kantor di Jakarta Selatan.
target_pelanggan: HR dan admin kantor
channel: WhatsApp dan Instagram DM
sumber_leads: belum disebut
volume_chat_harian: sekitar 40
jam_operasional: 08.00-17.00
siapa_balas_chat: dua admin bergantian
biaya_admin_bulanan: belum disebut
sistem_sekarang: catat manual di Excel
masalah_utama: Chat malam hari tidak terbalas, order jadi lari.
pain_points: sering salah catat pesanan; lupa follow up
aksi_utama: order katering harian
alur_setelah_chat: tanya menu, kirim daftar harga, konfirmasi jumlah porsi, invoice
pertanyaan_tersering: harga per porsi dan minimum order
fitur_diminati: follow-up otomatis, invoice
nilai_transaksi: sekitar 2 juta per order
prospek_per_bulan: belum disebut
minat_paket: Premium
budget_range: 5 juta
deadline: bulan depan
urgensi: mau siap sebelum musim ramai akhir tahun
bahasa_deck: ID
catatan: -
[/DECK_REQUEST]
Siap kak, aku susunkan dulu. Nanti Steven yang kabari langsung yaa.
[FACTS nama="Rina" nama_bisnis="Rasa Nusantara" industri="F&B" volume_chat="40"]"""
r1 = parse(ai1, {})
uji('tag diterima', r1['is_deck'] is True)
uji('placeholder "belum disebut" -> kosong', r1['deck']['sumber_leads'] == '' and r1['deck']['prospek_per_bulan'] == '')
uji('"-" -> kosong', r1['deck']['catatan'] == '')
uji('27 field terbaca', set(r1['deck']) == set(DECK_FIELDS))
uji('field terisi = 23 (4 placeholder dibuang)', sum(1 for f in DECK_FIELDS if r1['deck'][f]) == 23)
uji('FACTS nama -> nama_lengkap', r1['merged']['nama_lengkap'] == 'Rina')
uji('FACTS nama_bisnis tidak tertukar dgn nama', r1['merged']['nama_bisnis'] == 'Rasa Nusantara')
uji('blok tag hilang dari balasan', 'DECK_REQUEST' not in r1['clean'] and 'FACTS' not in r1['clean'])
uji('balasan tersisa utuh', r1['clean'] == 'Siap kak, aku susunkan dulu. Nanti Steven yang kabari langsung yaa.')

print()
print('=== 2. brief tingkat 1 belum lengkap -> ditolak ===')
ai2 = """[DECK_REQUEST]
nama: Budi
nama_bisnis: belum disebut
industri: belum disebut
masalah_utama: belum disebut
catatan: baru nanya harga
[/DECK_REQUEST]
Oke kak, nanti aku susunkan decknya dan Steven hubungi kamu."""
r2 = parse(ai2, {})
uji('ditolak', r2['is_deck'] is False and r2['ditolak'] is True)
uji('3 field tingkat 1 dilaporkan kurang', r2['kurang'] == ['nama_bisnis', 'industri', 'masalah_utama'])
uji('balasan menjanjikan deck -> terdeteksi',
    bool(re.search(r'(deck|proposal|penawaran)', r2['clean'], re.I))
    and bool(re.search(r'(susun|siapkan|buatkan|kirim|hubungi|kabari)', r2['clean'], re.I)))

print()
print('=== 3. tingkat 1 ditambal dari FACTS lama di STATS ===')
prev3 = {'nama_bisnis': 'Toko Sinar', 'industri': 'retail', 'masalah_utama': 'chat numpuk'}
ai3 = """[DECK_REQUEST]
nama: Andi
nama_bisnis: belum disebut
industri: belum disebut
masalah_utama: belum disebut
minat_paket: Basic
[/DECK_REQUEST]
Noted kak."""
r3 = parse(ai3, prev3)
uji('diterima setelah ditambal', r3['is_deck'] is True)
uji('nama_bisnis dari STATS', r3['deck']['nama_bisnis'] == 'Toko Sinar')
uji('industri dari STATS', r3['deck']['industri'] == 'retail')

print()
print('=== 4. blok terpotong / tidak ditutup ===')
ai4 = "Baik kak, aku catat.\n[DECK_REQUEST]\nnama: Sari\nnama_bisnis: Kopi Sari"
r4 = parse(ai4, {})
uji('tanpa penutup -> tidak dianggap brief', r4['is_deck'] is False and r4['ditolak'] is False)
uji('sisa blok tidak bocor ke prospek', r4['clean'] == 'Baik kak, aku catat.')

print()
print('=== 5. merge lintas emisi (Merge Brief) ===')
lama = {f: '' for f in DECK_FIELDS}
lama.update({'nama': 'Rina', 'nama_bisnis': 'Rasa Nusantara', 'industri': 'F&B',
             'masalah_utama': 'chat malam tidak terbalas', 'minat_paket': 'Premium'})
baru = {f: '' for f in DECK_FIELDS}
baru.update({'nama_bisnis': 'Rasa Nusantara', 'industri': 'F&B',
             'masalah_utama': 'chat malam tidak terbalas',
             'nilai_transaksi': '2 juta per order', 'minat_paket': ''})
hasil = {f: (baru[f] or lama[f]) for f in DECK_FIELDS}
uji('field baru masuk', hasil['nilai_transaksi'] == '2 juta per order')
uji('field lama tidak terhapus oleh kosong', hasil['minat_paket'] == 'Premium' and hasil['nama'] == 'Rina')
uji('kelengkapan naik', sum(1 for f in DECK_FIELDS if hasil[f]) == 6)

print()
print('=== 6. anti-bocor tag lain ===')
ai6 = "[TALK_TO_ADMIN]\nAku sambungkan ke Steven yaa kak. [SEND_MEDIA: deck-vira]"
r6 = parse(ai6, {})
uji('tag dibersihkan semua', '[' not in r6['clean'])

print()
print('=' * 56)
if gagal:
    print('GAGAL (%d): %s' % (len(gagal), '; '.join(gagal)))
    sys.exit(1)
print('SEMUA UJI PARSER LOLOS')
