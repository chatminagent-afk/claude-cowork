# -*- coding: utf-8 -*-
"""
_patch_2026-09-06.py — pengerasan lanjutan sesudah dua error produksi 2026-09-06.

Masukan : 2026-09-05-VIRA-Personal-Main-v3.json    (tidak diubah)
Keluaran: 2026-09-06-VIRA-Personal-Main-v3.1.json  (berkas baru)

H1. `Resolve User Row` — berhenti diam-diam saat Chat Counter memang membuang pesan.
    Gejala di produksi:
      "Identitas user kosong (phone & lid tidak ada) - payload webhook tidak dikenal: null"
    Sebabnya `Read User STATS` bersetel alwaysOutputData:true. Ketika `Chat Counter`
    sengaja mengembalikan [] untuk reaction / status / protocol / call, node Sheets
    itu TETAP mengeluarkan satu item kosong, jadi alur berlanjut ke sini dan
    $('Chat Counter').first().json bernilai {}. Gerbang yang dibuat untuk MENDIAMKAN
    reaction justru memerahkan execution dan memicu Error Notifier.
    Perbaikan: bedakan dua keadaan yang sebelumnya digabung.
      - input dari Chat Counter kosong total ({} tanpa satu pun key)
        -> pesannya memang sudah dibuang di hulu. Berhenti tanpa error.
      - input berisi tapi tetap tidak ada phone/lid
        -> payload asing yang sungguhan. TETAP throw, persis seperti sebelumnya.
    Jadi "fail loud" yang disengaja tidak hilang, yang hilang cuma alarm palsunya.

H2. `Parse Config` — gagal keras dengan menyebut kunci yang kosong.
    Gejala di produksi:
      "Kirimi: kredensial tidak lengkap (user_code/secret/device_id)" di node
      `Send WA + Verify (Kirimi)` — enam node setelah penyebab aslinya.
    Penyebab sebenarnya satu sel di tab CONFIG (A10 tertimpa huruf 'f', sehingga
    baris kirimi_user_code hilang). `Read CONFIG` bersetel alwaysOutputData:true,
    jadi pembacaan yang kosong tidak pernah bersuara dan seluruh config diam-diam
    jatuh ke nilai default.
    Perbaikan: periksa di tempat kunci itu dirakit. Kalau tab CONFIG balik kosong,
    atau salah satu kredensial Kirimi kosong, hentikan di sini dengan pesan yang
    menyebut nama kunci yang harus diisi dan di tab mana.
    Nilai non-kritis (survey_slots, media_catalog, dst.) tetap boleh kosong.

Jalankan: python _patch_2026-09-06.py   (lalu python _uat_2026-09-06.py)
"""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-05-VIRA-Personal-Main-v3.json")
DST = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.1.json")

with open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

nodes = {n["name"]: n for n in wf["nodes"]}
jejak = []


def ganti(teks, lama, baru, label):
    """Ganti sekali, gagal keras kalau pola tidak ketemu atau ambigu."""
    n = teks.count(lama)
    if n != 1:
        raise SystemExit("GAGAL [%s]: pola ditemukan %d kali (harus tepat 1)." % (label, n))
    jejak.append(label)
    return teks.replace(lama, baru)


# ======================================================================
# H1 — Resolve User Row
# ======================================================================
LAMA_H1 = """if (!phone && !lid) {
  throw new Error('Identitas user kosong (phone & lid tidak ada) - payload webhook tidak dikenal: ' + JSON.stringify(cc.body?.from ?? null));
}"""

BARU_H1 = """// ── Dua keadaan yang dulu digabung (2026-09-06) ──
// `Read User STATS` bersetel alwaysOutputData:true. Jadi ketika `Chat Counter`
// sengaja mengembalikan [] untuk reaction / status / protocol / call, node Sheets
// di antaranya TETAP mengeluarkan satu item kosong dan alur sampai ke sini dengan
// cc = {}. Itu bukan payload rusak, itu pesan yang memang sudah dibuang di hulu —
// jadi jangan diperlakukan sebagai error. Kalau tidak dibedakan, setiap emoji
// reaction menghasilkan execution merah plus satu notifikasi error palsu.
const ccKosong = !cc || Object.keys(cc).length === 0;
if (!phone && !lid) {
  if (ccKosong) {
    console.log('Chat Counter membuang pesan ini di hulu (reaction/status/sistem) - berhenti tanpa error.');
    return [];
  }
  // Input BERISI tapi tetap tanpa identitas = payload yang benar-benar asing.
  // Ini tetap harus berisik: bentuk payload Kirimi berubah tanpa kita tahu.
  throw new Error('Identitas user kosong (phone & lid tidak ada) - payload webhook tidak dikenal: ' + JSON.stringify(cc.body?.from ?? null));
}"""

kode = nodes["Resolve User Row"]["parameters"]["jsCode"]
nodes["Resolve User Row"]["parameters"]["jsCode"] = ganti(kode, LAMA_H1, BARU_H1, "H1 Resolve User Row")


# ======================================================================
# H2 — Parse Config
# ======================================================================
LAMA_H2 = """};
return [{ json: { ...passthrough, config } }];"""

BARU_H2 = """};

// ── Gerbang kewarasan CONFIG (2026-09-06) ──
// `Read CONFIG` bersetel alwaysOutputData:true, jadi pembacaan tab CONFIG yang
// gagal atau kosong TIDAK memerahkan node itu — dia mengeluarkan satu item kosong,
// `raw` jadi {}, dan seluruh config diam-diam jatuh ke nilai default. Akibatnya
// error baru meledak enam node kemudian, di `Send WA + Verify (Kirimi)`, dengan
// pesan yang menuduh kredensial padahal yang salah adalah pembacaan sheet.
// Kejadian 2026-09-06: satu sel kunci di tab CONFIG tertimpa huruf 'f', jadi baris
// kirimi_user_code hilang; nilainya masih ada, namanya yang lenyap.
// Diperiksa di sini, di tempat kuncinya dirakit, supaya pesannya menunjuk penyebab.
if (rows.length === 0 || Object.keys(raw).length === 0) {
  throw new Error('Tab CONFIG terbaca kosong (' + rows.length + ' baris). '
    + 'Cek: (a) kolom judul baris 1 harus persis "key" dan "value", '
    + '(b) service account masih punya akses ke spreadsheet ' + (sheetId || '(sheet_id kosong)') + ', '
    + '(c) nama tab masih "CONFIG". Semua nilai config jatuh ke default kalau ini dibiarkan.');
}

// Kredensial Kirimi: tanpa ketiganya, TIDAK ADA pesan yang bisa keluar sama sekali —
// balasan ke prospek, notif brief deck, notif handover, notif UNKNOWN, semuanya.
// Jadi berhenti di sini dengan menyebut kunci mana yang harus diisi.
const WAJIB = ['kirimi_user_code', 'kirimi_secret', 'kirimi_device_id'];
const hilang = WAJIB.filter(k => !String(config[k] || '').trim());
if (hilang.length) {
  const adaBarisnya = WAJIB.filter(k => Object.prototype.hasOwnProperty.call(raw, k));
  throw new Error('Kunci wajib kosong di tab CONFIG: ' + hilang.join(', ') + '. '
    + 'Yang barisnya ketemu: ' + (adaBarisnya.join(', ') || '(tidak satu pun)') + '. '
    + 'Kalau nilainya terlihat ada di sheet tapi tetap dilaporkan kosong, '
    + 'yang salah nama kuncinya di kolom "key", bukan nilainya.');
}

return [{ json: { ...passthrough, config } }];"""

kode = nodes["Parse Config"]["parameters"]["jsCode"]
nodes["Parse Config"]["parameters"]["jsCode"] = ganti(kode, LAMA_H2, BARU_H2, "H2 Parse Config")


# ======================================================================
# Tulis keluaran
# ======================================================================
wf["name"] = "VIRA Personal — Main"

with open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print("=" * 72)
print("PATCH 2026-09-06 selesai")
print("=" * 72)
print("  masukan : %s" % os.path.basename(SRC))
print("  keluaran: %s" % os.path.basename(DST))
print("  node    : %d" % len(wf["nodes"]))
print()
for j in jejak:
    print("  DITERAPKAN  %s" % j)
print()
print("Berikutnya: python _uat_2026-09-06.py")
