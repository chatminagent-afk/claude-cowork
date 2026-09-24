# -*- coding: utf-8 -*-
"""
_patch_2026-08-30.py — Paket A, B, C, D, E untuk VIRA Personal Main.

Masukan : 2026-08-28-VIRA-Personal-Main.json  (tidak diubah)
Keluaran: 2026-08-30-VIRA-Personal-Main.json  (file baru)

PAKET A — hentikan kehilangan data
  A1. Gerbang TINGKAT 1 di `Process All` hanya menahan NOTIFIKASI, bukan penyimpanan.
      Brief setengah jadi tetap ditulis ke REQUESTS. Yang dibuang hanya blok kosong total.
  A2. Tidak ada lagi ekspresi $('NodeLain') yang menyeberangi node `Wait Deck`.
      Urutan baru: Write REQUESTS -> Update STATS Brief -> Siapkan Notif Deck
                   -> Wait Deck -> IF Brief Layak -> Notify Admin Deck
      `Update STATS Brief` sekarang menulis brief_terisi SEBELUM Wait.
      Jeda 20 detik tetap ada persis sebelum kirim WA ke admin (maksud aslinya).

PAKET C — dua angka ROI naik ke tingkat yang boleh ditanya
  C1. `nilai_transaksi` + `prospek_per_bulan` pindah dari TINGKAT 3 ke TINGKAT 2B,
      dengan gerbang waktu: baru ditanya setelah prospek setuju dibuatkan pitch deck.
  C2-C4. Jumlah tingkat jadi empat; TINGKAT 1 bukan lagi gerbang emisi tag (ikut A1);
      syarat pemicu tag dilonggarkan + rem "jangan emisikan kalau tidak ada info baru".

PAKET B — 11 kolom baru di REQUESTS (32 -> 43)
  B1-B8. 6 field diisi AI (kota, jumlah_admin, sudah_pakai_chatbot, integrasi_dibutuhkan,
      data_tersedia, kutipan_asli) -> DECK_FIELDS jadi 33, ikut ke tag/FIELDS/LABEL/
      Write REQUESTS. 2 kolom diisi sistem (sumber_prospek, brief_jumlah).

PAKET D — sheet bisa dibaca sendiri
  D1. ts/update_terakhir jadi "YYYY-MM-DD HH:MM:SS" WIB supaya bisa diurutkan.
  D2. Menghasilkan sheet/2026-08-30-import/REQUESTS-header.tsv + _KAMUS_BRIEF.csv.

PAKET E — outcome tracking
  3 kolom diisi Steven manual (deck_dikirim_ts, hasil, alasan_kalah). SENGAJA tidak
  dipetakan di Write REQUESTS supaya isian tangan tidak pernah ditimpa workflow.

Jalankan: python _patch_2026-08-30.py  (lalu python _qa_2026-08-30.py)
"""
import json
import os
import uuid

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-08-28-VIRA-Personal-Main.json")
DST = os.path.join(DIR, "2026-08-30-VIRA-Personal-Main.json")

with open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

nodes = {n["name"]: n for n in wf["nodes"]}
conns = wf["connections"]
jejak = []


def ganti(teks, lama, baru, label):
    """Ganti sekali, gagal keras kalau pola tidak ketemu atau ambigu."""
    n = teks.count(lama)
    if n != 1:
        raise SystemExit("GAGAL [%s]: pola ditemukan %d kali (harus tepat 1)." % (label, n))
    jejak.append(label)
    return teks.replace(lama, baru)


# ─────────────────────────────────────────────────────────────
# A1 — gerbang TINGKAT 1 di Process All
# ─────────────────────────────────────────────────────────────
pa = nodes["Process All"]
kode = pa["parameters"]["jsCode"]

LAMA_GATE = """  // GATE TINGKAT 1 — brief tanpa ketiganya tidak cukup untuk menyusun deck
  deckMissing = ['nama_bisnis', 'industri', 'masalah_utama'].filter(f => !deckRequest[f]);
  if (deckMissing.length) {
    isDeckRequest = false;
    deckRejected = true;
    console.warn('DECK_REQUEST ditolak, tingkat 1 belum lengkap: ' + deckMissing.join(', '));
  }"""

BARU_GATE = """  // GATE TINGKAT 1 — sejak 2026-08-30 hanya menahan NOTIFIKASI, bukan penyimpanan.
  // Sebelumnya brief yang belum punya nama_bisnis/industri/masalah_utama dibuang UTUH,
  // ikut membuang field lain yang sudah disebut prospek (volume, budget, deadline, dst).
  // Sekarang: apa pun yang sudah tertangkap tetap ditulis ke REQUESTS; kolom `kelengkapan`
  // yang membedakan brief matang dari brief mentah. Yang masih dibuang hanya blok kosong total.
  deckMissing = ['nama_bisnis', 'industri', 'masalah_utama'].filter(f => !deckRequest[f]);
  deckRejected = deckMissing.length > 0;
  isDeckRequest = DECK_FIELDS.some(f => deckRequest[f]);
  if (deckRejected) {
    console.warn('DECK_REQUEST tingkat 1 belum lengkap — tetap disimpan, notifikasi ditahan: '
                 + deckMissing.join(', '));
  }
  if (!isDeckRequest) {
    console.warn('DECK_REQUEST kosong total, tidak ada satu pun field terisi — tidak disimpan.');
  }"""

kode = ganti(kode, LAMA_GATE, BARU_GATE, "A1 gerbang tingkat 1")

# A1b — `isDeckRequest` sekarang bernilai true juga untuk brief mentah, jadi ia tidak lagi
# boleh dipakai sebagai penanda "prospek ini minta deck". Flag itu dipisah jadi `deckLayak`.
kode = ganti(
    kode,
    "    isDeckRequest, deckRequest, deckRejected, deckMissing,",
    "    isDeckRequest, deckRequest, deckRejected, deckMissing,\n"
    "    // deckLayak = tingkat 1 lengkap. Ini yang menandai 'benar-benar minta deck'\n"
    "    // (dipakai kolom STATS.deck_requested + gerbang notifikasi admin).\n"
    "    deckLayak: isDeckRequest && !deckRejected,",
    "A1b flag deckLayak",
)
pa["parameters"]["jsCode"] = kode


# ─────────────────────────────────────────────────────────────
# A2a — Merge Brief membawa deck_layak
# ─────────────────────────────────────────────────────────────
mb = nodes["Merge Brief"]
kode_mb = mb["parameters"]["jsCode"]

kode_mb = ganti(
    kode_mb,
    "    brief_terisi: terisi.join(','),\n    brief_jumlah: terisi.length,",
    "    brief_terisi: terisi.join(','),\n"
    "    brief_jumlah: terisi.length,\n"
    "    // Tingkat 1 lengkap? Dipakai `IF Brief Layak` untuk memutuskan notifikasi admin.\n"
    "    deck_layak: pa.deckLayak === true,",
    "A2a deck_layak di Merge Brief",
)
mb["parameters"]["jsCode"] = kode_mb


# ─────────────────────────────────────────────────────────────
# A1c — kolom STATS.deck_requested ikut flag baru, bukan isDeckRequest
# ─────────────────────────────────────────────────────────────
uts = nodes["Update to STATS"]["parameters"]["columns"]["value"]
LAMA_DR = (
    "={{ $('Process All').first().json.isDeckRequest ? 'Y' : "
    "($('Resolve User Row').first().json.deck_requested || '') }}"
)
BARU_DR = (
    "={{ $('Process All').first().json.deckLayak ? 'Y' : "
    "($('Resolve User Row').first().json.deck_requested || '') }}"
)
if uts.get("deck_requested") != LAMA_DR:
    raise SystemExit("GAGAL [A1c]: ekspresi deck_requested tidak seperti yang diharapkan.")
uts["deck_requested"] = BARU_DR
jejak.append("A1c deck_requested di Update to STATS")


# ─────────────────────────────────────────────────────────────
# A2b — node baru: Siapkan Notif Deck (Code) + IF Brief Layak
# ─────────────────────────────────────────────────────────────
pos_wait = nodes["Wait Deck"]["position"]
pos_notif = nodes["Notify Admin Deck"]["position"]

siapkan = {
    "parameters": {
        "jsCode": (
            "// ── Siapkan Notif Deck ──\n"
            "// Semua nilai yang masih dibutuhkan SETELAH `Wait Deck` dikemas di sini.\n"
            "// Alasannya: ekspresi $('NodeLain') yang menyeberangi node Wait rapuh — kalau\n"
            "// gagal resolve, hasilnya string kosong dan node HTTP tetap jalan dengan pesan\n"
            "// kosong (gejala brief_terisi & notif admin kosong). Setelah node ini, semua\n"
            "// node hilir cukup baca $json.*  (2026-08-30)\n"
            "const mb  = $('Merge Brief').first().json;\n"
            "const cfg = $('Parse Config').first().json.config;\n"
            "\n"
            "return [{\n"
            "  json: {\n"
            "    deck_layak:  mb.deck_layak === true,\n"
            "    notif_text:  String(mb.notif_text || ''),\n"
            "    brief_terisi: String(mb.brief_terisi || ''),\n"
            "    admin_phone: cfg.admin_phone,\n"
            "    user_code:   cfg.kirimi_user_code,\n"
            "    secret:      cfg.kirimi_secret,\n"
            "    device_id:   cfg.kirimi_device_id,\n"
            "  }\n"
            "}];\n"
        )
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": nodes["Merge Brief"]["typeVersion"],
    "position": [pos_wait[0], pos_wait[1] - 140],
    "id": str(uuid.uuid4()),
    "name": "Siapkan Notif Deck",
}

if_layak = {
    "parameters": {
        "conditions": {
            "options": {
                "caseSensitive": True,
                "leftValue": "",
                "typeValidation": "strict",
                "version": 3,
            },
            "conditions": [
                {
                    "id": "deck-layak-cond-0001",
                    "leftValue": "={{ $json.deck_layak }}",
                    "rightValue": "",
                    "operator": {
                        "type": "boolean",
                        "operation": "true",
                        "singleValue": True,
                    },
                }
            ],
            "combinator": "and",
        },
        "options": {},
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": nodes["IF Deck Request"]["typeVersion"],
    "position": [
        int((pos_wait[0] + pos_notif[0]) / 2),
        pos_notif[1],
    ],
    "id": str(uuid.uuid4()),
    "name": "IF Brief Layak",
}

for baru in (siapkan, if_layak):
    if baru["name"] in nodes:
        raise SystemExit("GAGAL: node '%s' sudah ada." % baru["name"])
    wf["nodes"].append(baru)
    nodes[baru["name"]] = baru
jejak.append("A2b node Siapkan Notif Deck + IF Brief Layak")


# ─────────────────────────────────────────────────────────────
# A2c — Update STATS Brief pindah ke SEBELUM Wait, pakai referensi yang aman
# ─────────────────────────────────────────────────────────────
usb = nodes["Update STATS Brief"]["parameters"]["columns"]["value"]
if usb.get("brief_terisi") != "={{ $('Merge Brief').first().json.brief_terisi }}":
    raise SystemExit("GAGAL [A2c]: ekspresi brief_terisi tidak seperti yang diharapkan.")
# Setelah rewiring node ini persis di hilir Write REQUESTS (tidak lagi lewat Wait),
# tapi referensi langsung ke Merge Brief tetap diganti agar tidak rapuh.
usb["brief_terisi"] = "={{ $('Merge Brief').item.json.brief_terisi }}"
# deck_requested tidak lagi ditulis 'Y' tanpa syarat — brief mentah tidak boleh
# menandai prospek sebagai "minta deck" (kolom itu yang mengeluarkannya dari jeda follow-up).
if usb.get("deck_requested") != "Y":
    raise SystemExit("GAGAL [A2c]: deck_requested tidak lagi bernilai literal 'Y'.")
usb["deck_requested"] = BARU_DR
jejak.append("A2c brief_terisi + deck_requested di Update STATS Brief")


# ─────────────────────────────────────────────────────────────
# A2d — Notify Admin Deck baca $json.* saja
# ─────────────────────────────────────────────────────────────
params = nodes["Notify Admin Deck"]["parameters"]["bodyParameters"]["parameters"]
PETA = {
    "user_code": "={{ $json.user_code }}",
    "secret": "={{ $json.secret }}",
    "device_id": "={{ $json.device_id }}",
    "phone": "={{ $json.admin_phone }}",
    "message": "={{ $json.notif_text }}",
}
terpakai = set()
for p in params:
    if p["name"] not in PETA:
        raise SystemExit("GAGAL [A2d]: parameter tak dikenal '%s'." % p["name"])
    p["value"] = PETA[p["name"]]
    terpakai.add(p["name"])
if terpakai != set(PETA):
    raise SystemExit("GAGAL [A2d]: parameter kurang: %s" % (set(PETA) - terpakai))
jejak.append("A2d Notify Admin Deck pakai $json.*")


# ─────────────────────────────────────────────────────────────
# A2e — rewiring cabang deck
# ─────────────────────────────────────────────────────────────
def satu(nama_tujuan):
    return {"main": [[{"node": nama_tujuan, "type": "main", "index": 0}]]}


HARUS = {
    "Write REQUESTS": "Wait Deck",
    "Wait Deck": "Update STATS Brief",
    "Update STATS Brief": "Notify Admin Deck",
}
for asal, tujuan_lama in HARUS.items():
    aktual = conns.get(asal, {}).get("main", [[]])[0]
    if [t["node"] for t in aktual] != [tujuan_lama]:
        raise SystemExit(
            "GAGAL [A2e]: '%s' seharusnya menuju '%s', ternyata %s"
            % (asal, tujuan_lama, [t["node"] for t in aktual])
        )

conns["Write REQUESTS"] = satu("Update STATS Brief")
conns["Update STATS Brief"] = satu("Siapkan Notif Deck")
conns["Siapkan Notif Deck"] = satu("Wait Deck")
conns["Wait Deck"] = satu("IF Brief Layak")
# IF: output 0 = true -> notify, output 1 = false -> berhenti (brief mentah, tetap tersimpan)
conns["IF Brief Layak"] = {
    "main": [[{"node": "Notify Admin Deck", "type": "main", "index": 0}], []]
}
jejak.append("A2e rewiring cabang deck")


# ─────────────────────────────────────────────────────────────
# C1 — MENGGALI: dua angka ROI naik ke TINGKAT 2B
# ─────────────────────────────────────────────────────────────
LAMA_T2 = """TINGKAT 3 — hanya kucatat kalau dia menyebutnya sendiri, TIDAK PERNAH kutanyakan:
jabatannya, siapa pelanggannya, jam operasionalnya, biaya admin sekarang, sistem yang dipakai
sekarang, dari mana leadsnya datang, pertanyaan yang paling sering masuk, nilai rata-rata satu
transaksi, jumlah prospek per bulan, dan anggarannya."""

BARU_T2 = """TINGKAT 2B — angka. Semuanya baru boleh kutanyakan SETELAH dia setuju dibuatkan pitch deck,
tidak pernah sebelum itu. Tanyakan sebagai syarat hitungan, bukan sebagai pertanyaan jualan.
Aturan satu pertanyaan per balasan tetap berlaku, jadi ditanya di giliran yang berbeda-beda.
Kalau dia tidak mau menyebut, jangan pernah diulang — tulis "belum disebut" dan lanjut.
Angka kasar sudah cukup; kisaran juga boleh.

- Rata-rata nilai satu closing, dan kira-kira berapa prospek masuk per bulan.
  Contoh: "biar hitungannya nggak ngarang, rata-rata satu closing di tempat kakak kira-kira
  berapa?"
- Kalau chat mereka dibalas admin (bukan ownernya sendiri): berapa orang adminnya, dan
  kira-kira berapa biaya admin per bulan. Kalau ownernya yang balas sendiri, LEWATI dua ini
  dan jangan tanyakan sama sekali.

TINGKAT 3 — hanya kucatat kalau dia menyebutnya sendiri, TIDAK PERNAH kutanyakan:
jabatannya, siapa pelanggannya, jam operasionalnya, sistem yang dipakai sekarang, dari mana
leadsnya datang, pertanyaan yang paling sering masuk, anggarannya, kotanya, apakah dia pernah
pakai chatbot lain dan kenapa berhenti, sistem apa yang harus disambung, dan apakah bahan
datanya (FAQ, price list, katalog) sudah ada."""

sm = nodes["AI Agent"]["parameters"]["options"]["systemMessage"]
sm = ganti(sm, LAMA_T2, BARU_T2, "C1 MENGGALI tingkat 2B")

# C2 — jumlah tingkat berubah dari tiga jadi empat
sm = ganti(
    sm,
    "Ada tiga tingkat informasi. Tingkat 1 dan 2 boleh kutanyakan, tingkat 3 tidak pernah.",
    "Ada empat tingkat informasi. Tingkat 1, 2, dan 2B boleh kutanyakan; tingkat 3 tidak pernah.",
    "C2 jumlah tingkat",
)

# C3 — TINGKAT 1 bukan lagi gerbang emisi tag.
# Setelah A1, brief setengah jadi tetap disimpan; menunda tag hanya membuang informasi.
sm = ganti(
    sm,
    """TINGKAT 1 — wajib, dan `[DECK_REQUEST]` tidak boleh keluar sebelum ketiganya terisi:
nama bisnisnya, industrinya, masalah terbesarnya sekarang.""",
    """TINGKAT 1 — tiga hal yang membuat brief cukup matang untuk menyusun deck:
nama bisnisnya, industrinya, masalah terbesarnya sekarang. Ini yang paling kukejar duluan.
Tapi selama belum lengkap pun brief tetap tersimpan, jadi aku tidak menunda `[DECK_REQUEST]`
cuma karena salah satunya belum keluar.""",
    "C3 TINGKAT 1 bukan gerbang emisi",
)

# C4 — syarat pemicu tag ikut dilonggarkan, plus rem supaya tidak diemisikan berulang sia-sia
sm = ganti(
    sm,
    """`[DECK_REQUEST]`
  Dipakai saat dia setuju dibuatkan pitch deck khusus, ATAU saat aku sudah tahu ketiga hal
  TINGKAT 1: nama bisnisnya, industrinya, dan masalah utamanya.""",
    """`[DECK_REQUEST]`
  Dipakai saat dia setuju dibuatkan pitch deck khusus, saat aku sudah tahu ketiga hal
  TINGKAT 1 (nama bisnisnya, industrinya, masalah utamanya), ATAU saat dia sudah menyebut
  minimal tiga hal apa pun tentang bisnisnya — walaupun nama bisnisnya belum keluar.
  Brief setengah jadi tetap berguna; yang hilang justru kalau tidak kucatat sama sekali.

  Tapi jangan mengeluarkan tag ini kalau tidak ada satu pun informasi baru sejak tag terakhir.""",
    "C4 syarat pemicu tag",
)

nodes["AI Agent"]["parameters"]["options"]["systemMessage"] = sm


# ═════════════════════════════════════════════════════════════
# PAKET B + D + E
# ═════════════════════════════════════════════════════════════
# 6 field baru yang diisi AI (masuk DECK_FIELDS, tag, dan Merge Brief)
FIELD_AI_BARU = [
    ("kota", "Kota"),
    ("jumlah_admin", "Jumlah admin"),
    ("sudah_pakai_chatbot", "Pernah pakai chatbot"),
    ("integrasi_dibutuhkan", "Integrasi dibutuhkan"),
    ("data_tersedia", "Data siap"),
    ("kutipan_asli", "Kutipan asli"),
]
# Diisi sistem, bukan AI — ikut ditulis Write REQUESTS tapi tidak ada di tag
KOL_SISTEM = ["sumber_prospek", "brief_jumlah"]
# Diisi Steven manual — kolomnya ada di sheet, sengaja TIDAK dipetakan di Write REQUESTS
# supaya isian tangan tidak pernah ditimpa workflow
KOL_MANUAL = ["deck_dikirim_ts", "hasil", "alasan_kalah"]

nama_ai_baru = [f for f, _ in FIELD_AI_BARU]

# ── B1 — DECK_FIELDS di Process All ──
kode = pa["parameters"]["jsCode"]
kode = ganti(
    kode,
    "  'prospek_per_bulan', 'minat_paket', 'budget_range', 'deadline', 'urgensi', "
    "'bahasa_deck', 'catatan'];",
    "  'prospek_per_bulan', 'minat_paket', 'budget_range', 'deadline', 'urgensi', "
    "'bahasa_deck', 'catatan',\n"
    "  // Paket B (2026-08-30) — 6 field tambahan untuk deck\n"
    "  " + ", ".join("'%s'" % f for f in nama_ai_baru) + "];",
    "B1 DECK_FIELDS +6",
)

# ── B2 — kutipan_asli boleh lebih panjang dari field lain ──
kode = ganti(
    kode,
    "    deckRequest[k] = KOSONG(m[2]) ? '' : BERSIH(m[2], 500);",
    "    // kutipan_asli menampung 3-5 kalimat mentah, jadi batasnya lebih longgar\n"
    "    deckRequest[k] = KOSONG(m[2]) ? '' : BERSIH(m[2], k === 'kutipan_asli' ? 900 : 500);",
    "B2 batas panjang kutipan_asli",
)
pa["parameters"]["jsCode"] = kode

# ── B3 — FIELDS + LABEL di Merge Brief ──
kode_mb = mb["parameters"]["jsCode"]
kode_mb = ganti(
    kode_mb,
    '"urgensi", "bahasa_deck", "catatan"];',
    '"urgensi", "bahasa_deck", "catatan", '
    + ", ".join('"%s"' % f for f in nama_ai_baru)
    + "];",
    "B3a FIELDS +6",
)
kode_mb = ganti(
    kode_mb,
    '"bahasa_deck": "Bahasa", "catatan": "Catatan"};',
    '"bahasa_deck": "Bahasa", "catatan": "Catatan", '
    + ", ".join('"%s": "%s"' % (f, lab) for f, lab in FIELD_AI_BARU)
    + "};",
    "B3b LABEL +6",
)

# ── B4 — sumber_prospek + D1 timestamp ISO ──
kode_mb = ganti(
    kode_mb,
    "const stamp = new Date().toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' });",
    "// Paket D — ISO-ish WIB (YYYY-MM-DD HH:MM:SS) supaya kolom ts/update_terakhir bisa\n"
    "// diurutkan dan dihitung selisihnya. Format lama 'D/M/YYYY, HH.MM.SS' tidak bisa keduanya.\n"
    "const stamp = new Date(Date.now() + 7 * 3600 * 1000).toISOString().slice(0, 19)\n"
    "                .replace('T', ' ');\n"
    "\n"
    "// Paket B — sumber_prospek = dari mana dia sampai ke VIRA (IG / landing / referral).\n"
    "// Beda dari `sumber_leads`, yang artinya sumber leads milik BISNIS DIA.\n"
    "// Diambil dari STATS.lead_source; sekali terisi, dipertahankan.\n"
    "const rur = $('Resolve User Row').first().json || {};\n"
    "const sumber_prospek = String(lama['sumber_prospek'] ?? '').trim()\n"
    "                    || String(rur.lead_source_db ?? '').trim();",
    "B4 sumber_prospek + D1 stamp ISO",
)
kode_mb = ganti(
    kode_mb,
    "    brief_terisi: terisi.join(','),\n    brief_jumlah: terisi.length,",
    "    brief_terisi: terisi.join(','),\n"
    "    brief_jumlah: terisi.length,\n"
    "    sumber_prospek,",
    "B4b sumber_prospek di keluaran",
)
mb["parameters"]["jsCode"] = kode_mb

# ── F1 — notifikasi WA menyertakan kesiapan deck + perintah generate ──
# Tanpa ini Steven cuma tahu "14/33" — tidak tahu apakah itu cukup untuk menyusun deck.
# Enam slide di deck butuh data klien; sisanya (23 slide) berdiri sendiri.
kode_mb = ganti(
    kode_mb,
    """const notif_text =
  `📋 [VIRA Steven] BRIEF DECK${revisi}\\n` +
  `${hasil.nama_bisnis || '(nama bisnis belum disebut)'} — ${hasil.industri || '-'}\\n` +
  `WA: ${key}\\n` +
  `Kelengkapan: ${terisi.length}/${FIELDS.length}\\n\\n` +
  terisi.map(f => `${LABEL[f] || f}: ${hasil[f]}`).join('\\n') +
  `\\n\\nBelum tergali: ${kosong.map(f => LABEL[f] || f).join(', ') || '(lengkap)'}`;""",
    """// ── Kesiapan deck ──
// 23 dari 29 slide berdiri tanpa data klien. Enam sisanya butuh field tertentu;
// kalau fieldnya kosong, generator MEMBUANG slide itu (tidak pernah menebak isinya).
// Daftar ini harus sama dengan atribut data-butuh di deck/template.html.
const SLIDE_KHUSUS = [
  ['Konteks bisnis',        ['deskripsi_bisnis']],
  ['Pain Points',           ['masalah_utama']],
  ['The Flow (mockup)',     ['aksi_utama', 'pertanyaan_tersering']],
  ['#1 Time Freedom',       ['volume_chat_harian']],
  ['#2 Zero Leaking Profit',['industri']],
  ['#3 Scalability',        ['volume_chat_harian']],
];
const siap   = SLIDE_KHUSUS.filter(([, f]) => f.every(k => hasil[k]));
const belum  = SLIDE_KHUSUS.filter(([, f]) => !f.every(k => hasil[k]));
const deckSiap = belum.length === 0;

const rincianSlide = SLIDE_KHUSUS.map(([nama, f]) => {
  const kurang = f.filter(k => !hasil[k]);
  return kurang.length
    ? `  ✗ ${nama} — perlu: ${kurang.map(k => LABEL[k] || k).join(', ')}`
    : `  ✓ ${nama}`;
}).join('\\n');

const notif_text =
  `📋 [VIRA Personal] BRIEF DECK${revisi}\\n` +
  `${hasil.nama_bisnis || '(nama bisnis belum disebut)'} — ${hasil.industri || '-'}\\n` +
  `WA: ${key}\\n` +
  `Kelengkapan: ${terisi.length}/${FIELDS.length}\\n` +
  `Slide khusus siap: ${siap.length}/${SLIDE_KHUSUS.length}` +
  `${deckSiap ? '  → DECK SIAP DIGENERATE' : ''}\\n\\n` +
  rincianSlide + `\\n\\n` +
  terisi.map(f => `${LABEL[f] || f}: ${hasil[f]}`).join('\\n') +
  `\\n\\nBelum tergali: ${kosong.map(f => LABEL[f] || f).join(', ') || '(lengkap)'}` +
  `\\n\\nGenerate deck:\\npython buat_deck.py --wa ${key}`;""",
    "F1 notif kesiapan deck + perintah generate",
)
mb["parameters"]["jsCode"] = kode_mb


# ── B5 — Write REQUESTS memetakan kolom baru (kecuali kolom manual) ──
wr = nodes["Write REQUESTS"]["parameters"]["columns"]["value"]
for f in nama_ai_baru + KOL_SISTEM:
    if f in wr:
        raise SystemExit("GAGAL [B5]: kolom '%s' sudah dipetakan." % f)
    wr[f] = "={{ $json['%s'] }}" % f
for f in KOL_MANUAL:
    if f in wr:
        raise SystemExit("GAGAL [B5]: kolom manual '%s' tidak boleh dipetakan." % f)
jejak.append("B5 Write REQUESTS +%d kolom" % (len(nama_ai_baru) + len(KOL_SISTEM)))

# ── B6 — 6 baris baru di blok tag ──
sm = nodes["AI Agent"]["parameters"]["options"]["systemMessage"]
sm = ganti(
    sm,
    "  catatan: ...\n  [/DECK_REQUEST]",
    "  catatan: ...\n"
    + "".join("  %s: ...\n" % f for f in nama_ai_baru)
    + "  [/DECK_REQUEST]",
    "B6 blok tag +6 baris",
)

# ── B7 — aturan pengisian kutipan_asli ──
sm = ganti(
    sm,
    """  jangan dilewati barisnya. Isi setiap baris dengan kalimatnya sendiri, bukan kutipan mentah,
  maksimal dua kalimat per baris.""",
    """  jangan dilewati barisnya. Isi setiap baris dengan kalimatnya sendiri, bukan kutipan mentah,
  maksimal dua kalimat per baris.

  Satu pengecualian: `kutipan_asli` justru diisi kutipan MENTAH — 3 sampai 5 kalimat miliknya
  sendiri yang paling menggambarkan masalahnya dan cara dia bicara, disalin apa adanya dan
  dipisah dengan " | ". Ini yang dipakai Steven menulis contoh percakapan di deck, jadi nilainya
  justru ada di kalimat aslinya. Jangan pernah memasukkan nomor telepon, alamat, nama orang lain,
  atau data pribadi apa pun ke dalam kutipan.""",
    "B7 aturan kutipan_asli",
)

# B8 sudah dilebur ke C1 — daftar TINGKAT 3 final (termasuk 5 field Paket B) ditulis
# sekaligus di sana, supaya `biaya admin` dan `jumlah admin` tidak muncul di dua tingkat.
nodes["AI Agent"]["parameters"]["options"]["systemMessage"] = sm


# ─────────────────────────────────────────────────────────────
# Simpan + laporan
# ─────────────────────────────────────────────────────────────
if os.path.exists(DST):
    raise SystemExit("GAGAL: %s sudah ada. Hapus dulu kalau memang mau ditimpa." % DST)

with open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────
# PAKET D — berkas untuk sheet: header REQUESTS + tab _KAMUS_BRIEF
# ─────────────────────────────────────────────────────────────
IMPORT_DIR = os.path.join(os.path.dirname(DIR), "sheet", "2026-08-30-import")
os.makedirs(IMPORT_DIR, exist_ok=True)

# Urutan kolom REQUESTS: 32 kolom lama TIDAK bergeser, semua yang baru ditempel di kanan.
HEADER_REQUESTS = list(wr.keys()) + KOL_MANUAL
if len(HEADER_REQUESTS) != len(set(HEADER_REQUESTS)):
    raise SystemExit("GAGAL: ada nama kolom REQUESTS yang dobel.")

with open(os.path.join(IMPORT_DIR, "REQUESTS-header.tsv"), "w", encoding="utf-8") as f:
    f.write("\t".join(HEADER_REQUESTS) + "\n")

# field, tingkat, bagian deck, slide, diisi oleh, contoh isi
KAMUS = [
    ("ts", "sistem", "Meta", "-", "workflow", "2026-08-30 23:04:11", "Waktu brief pertama masuk (WIB). Tidak berubah setelah itu."),
    ("update_terakhir", "sistem", "Meta", "-", "workflow", "2026-08-30 23:41:02", "Kapan terakhir diperkaya."),
    ("no_wa", "sistem", "Meta", "-", "workflow", "628xxxxxxxxxx", "Kunci pencocokan baris. Format kolom harus Plain text."),
    ("nama", "1", "A. Identitas", "1, 31", "AI", "Budi", "Nama orang yang chat."),
    ("jabatan", "3", "A. Identitas", "1", "AI", "Owner", "Menentukan sudut pandang deck & siapa pengambil keputusan."),
    ("nama_bisnis", "1", "A. Identitas", "1, 31", "AI", "Akademi Arsi", "Cover & judul deck."),
    ("industri", "1", "A. Identitas", "1", "AI", "edukasi software arsitek", "Menentukan seluruh konteks pain point."),
    ("deskripsi_bisnis", "3", "A. Identitas", "2-3", "AI", "kursus software arsitek untuk calon siswa", "Slide pembuka konteks."),
    ("target_pelanggan", "3", "A. Identitas", "4-5, 8-15", "AI", "calon siswa yang mau belajar software arsitek", "Pain point & mockup percakapan."),
    ("channel", "2", "B. Situasi", "4-5", "AI", "Instagram; WhatsApp", "Pain point multi-platform."),
    ("sumber_leads", "3", "B. Situasi", "4-5", "AI", "iklan IG + organik", "Seberapa mahal satu leads hilang. BEDA dari sumber_prospek."),
    ("volume_chat_harian", "2", "B. Situasi", "4-5, 27", "AI", "10 chat per hari", "Pain point + slide scalability."),
    ("jam_operasional", "3", "B. Situasi", "4-5", "AI", "09.00-17.00", "Pain point 'di luar jam kerja'."),
    ("siapa_balas_chat", "2", "B. Situasi", "4-5", "AI", "owner menangani sendiri", "Pain point 'owner overload'."),
    ("biaya_admin_bulanan", "3", "B. Situasi", "21-22, 25-26", "AI", "Rp3.000.000", "Slide biaya & perbandingan."),
    ("sistem_sekarang", "3", "B. Situasi", "27, 29", "AI", "catat manual di Excel", "Slide human error + integrasi."),
    ("masalah_utama", "1", "C. Masalah", "4-5", "AI", "chat calon siswa masuk 24/7, tidak kekejar", "Satu masalah terbesar menurut dia sendiri."),
    ("pain_points", "3", "C. Masalah", "4-5", "AI", "telat balas; lupa follow-up", "Keluhan lain, dipisah titik koma."),
    ("aksi_utama", "2", "D. Alur & fitur", "8-15", "AI", "pendaftaran kelas", "Konversi yang dikejar. Mengganti slide 'Automated Booking'."),
    ("alur_setelah_chat", "3", "D. Alur & fitur", "8-15", "AI", "tanya jadwal -> daftar -> bayar", "Slide The Flow + menentukan fitur mana yang dibuang."),
    ("pertanyaan_tersering", "3", "D. Alur & fitur", "8-15", "AI", "kapan buka kelas, cara daftar", "Bahan FAQ + mockup percakapan."),
    ("fitur_diminati", "3", "D. Alur & fitur", "20", "AI", "follow-up otomatis; kirim brosur", "Slide perbandingan Basic vs Premium."),
    ("nilai_transaksi", "2B", "E. ROI", "25-26", "AI", "Rp2.500.000", "Rata-rata nilai satu closing. Baru ditanya setelah setuju dibuatkan deck."),
    ("prospek_per_bulan", "2B", "E. ROI", "25-26", "AI", "50", "Prospek masuk per bulan. Baru ditanya setelah setuju dibuatkan deck."),
    ("minat_paket", "3", "F. Komersial", "20-22", "AI", "Premium", "Basic / Premium / belum tahu."),
    ("budget_range", "3", "F. Komersial", "21-22", "AI", "3-5 juta per bulan", "Kisaran anggaran yang dia sebut sendiri."),
    ("deadline", "2", "F. Komersial", "29", "AI", "September 2026", "Kapan dia ingin mulai jalan."),
    ("urgensi", "3", "F. Komersial", "29", "AI", "batch kelas baru buka Oktober", "Kenapa sekarang, bukan nanti."),
    ("bahasa_deck", "3", "G. Meta", "semua", "AI", "ID", "ID / EN / campur, mengikuti bahasa yang dia pakai."),
    ("catatan", "3", "G. Meta", "-", "AI", "sempat coba chatbot gratisan, menyerah", "Apa pun yang penting tapi tidak masuk field lain."),
    ("kelengkapan", "sistem", "G. Meta", "-", "workflow", "14/33", "Untuk dibaca manusia. Untuk sortir pakai brief_jumlah."),
    ("status_followup", "manual", "G. Meta", "-", "Steven", "BARU", "BARU / DIHUBUNGI / DEAL / BATAL."),
    ("kota", "3", "A. Identitas", "1, 29", "AI", "Jakarta Selatan", "Konteks lokal, zona waktu, dan pengaturan meeting."),
    ("jumlah_admin", "3", "B. Situasi", "4-5, 25-26", "AI", "1", "Angka. Basis hitungan ROI; siapa_balas_chat isinya teks bebas."),
    ("sudah_pakai_chatbot", "3", "C. Masalah", "19-20", "AI", "pernah, chatbot gratisan, berhenti karena kaku", "Menentukan objection mana yang perlu dijawab di deck."),
    ("integrasi_dibutuhkan", "3", "D. Alur & fitur", "27, 29", "AI", "belum ada; cukup WhatsApp", "Sistem yang harus disambung. Menentukan scope build."),
    ("data_tersedia", "3", "D. Alur & fitur", "29", "AI", "sudah ada price list, FAQ belum", "Menentukan timeline implementasi. Tanpa ini, tanggal cuma tebakan."),
    ("kutipan_asli", "selalu", "D. Alur & fitur", "8-15", "AI", "chat numpuk pas lagi ngajar | sering kelewat", "3-5 kalimat mentah, dipisah ' | '. Bahan mockup percakapan."),
    ("sumber_prospek", "sistem", "Funnel Steven", "-", "workflow", "Organik", "Dari mana dia sampai ke VIRA (IG / landing / referral). Disalin dari STATS.lead_source."),
    ("brief_jumlah", "sistem", "G. Meta", "-", "workflow", "14", "Angka. Dipakai sortir 'brief mana yang paling matang'."),
    ("deck_dikirim_ts", "manual", "Outcome", "-", "Steven", "2026-09-02", "Kapan deck dikirim. Kosong = belum dikirim."),
    ("hasil", "manual", "Outcome", "-", "Steven", "DEAL", "DEAL / KALAH / NO_RESPONSE / MASIH_JALAN."),
    ("alasan_kalah", "manual", "Outcome", "-", "Steven", "harga di atas budget", "Diisi hanya kalau hasil = KALAH. Ini umpan balik untuk memperbaiki deck."),
]

kamus_fields = [r[0] for r in KAMUS]
if kamus_fields != HEADER_REQUESTS:
    hilang = [f for f in HEADER_REQUESTS if f not in kamus_fields]
    lebih = [f for f in kamus_fields if f not in HEADER_REQUESTS]
    raise SystemExit(
        "GAGAL: _KAMUS_BRIEF tidak sinkron dengan header REQUESTS.\n"
        "  belum ada di kamus: %s\n  tidak ada di header: %s\n"
        "  urutan sama? %s" % (hilang, lebih, sorted(kamus_fields) == sorted(HEADER_REQUESTS))
    )

with open(os.path.join(IMPORT_DIR, "_KAMUS_BRIEF.csv"), "w", encoding="utf-8", newline="") as f:
    import csv as _csv

    w = _csv.writer(f)
    w.writerow(["field", "tingkat", "bagian_deck", "slide", "diisi_oleh", "contoh_isi", "catatan"])
    w.writerows(KAMUS)

print("OK -> %s" % os.path.basename(DST))
print("Node: %d (dari %d)" % (len(wf["nodes"]), len(wf["nodes"]) - 2))
print("REQUESTS: %d kolom (dari 32)" % len(HEADER_REQUESTS))
print("Field AI (kelengkapan): %d" % (27 + len(nama_ai_baru)))
print("-> sheet/2026-08-30-import/REQUESTS-header.tsv")
print("-> sheet/2026-08-30-import/_KAMUS_BRIEF.csv")
for j in jejak:
    print("  - %s" % j)
