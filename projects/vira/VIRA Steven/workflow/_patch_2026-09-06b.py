# -*- coding: utf-8 -*-
"""
_patch_2026-09-06b.py — gerbang identitas di Chat Counter.

Masukan : 2026-09-06-VIRA-Personal-Main-v3.1.json  (tidak diubah)
Keluaran: 2026-09-06-VIRA-Personal-Main-v3.2.json  (berkas baru)

H3. Kirimi mengirim event non-chat ke webhook yang sama dengan pesan masuk.
    Yang tertangkap di produksi 2026-09-06 11:25 WIB:

        { "event": "device.last_active", "deviceId": "D-BTUYM",
          "timestamp": 1788668758, "message": "Device last active updated",
          "datetime_wib": "2026-09-06 11:25:59" }

    Ini denyut nadi perangkat, bukan pesan orang. Tapi dia lolos SEMUA gerbang
    `Chat Counter` yang ada:
      - `messageType` tidak ada  -> '' -> tidak masuk DROP_TYPES
      - `body.message` ada isinya -> hasText true -> gerbang "bukan teks valid" lolos
      - `isFromGroup` / `isFromMe` tidak ada -> node IF sebelumnya meloloskan
    Lalu `from` dan `originLid` sama-sama tidak ada, jadi phone & lid kosong dan
    `Resolve User Row` melempar 'Identitas user kosong'. Karena denyut ini berkala,
    execution merahnya juga berkala — tidak ada hubungannya dengan chat sama sekali.

    Perbaikan: gerbang identitas paling depan di `Chat Counter`. Pesan dari manusia
    SELALU membawa pengenal; event perangkat tidak pernah. Jadi pengenal itu yang
    dipakai sebagai syarat, bukan daftar nama event — daftar nama akan basi begitu
    Kirimi menambah jenis event baru, sedangkan syarat ini tidak.

    Pengenal dicari di beberapa nama field sekaligus. Bentuk payload Kirimi sudah
    terbukti berbeda-beda antar event, dan satu-satunya kerugian dari mencari lebih
    luas adalah nol — sedangkan kalau nomor prospek ternyata datang di `senderAlt`
    dan tidak kita baca, chatnya tidak pernah dibalas dan kita tidak akan pernah tahu.

    `console.warn` mencatat nama event + daftar field payload, supaya kalau ada
    bentuk baru yang ikut terbuang, jejaknya ada di log tanpa memerahkan execution.

    Gerbang `Resolve User Row` (H1, 2026-09-06) sengaja DIBIARKAN. Sesudah patch ini
    dia tidak akan kena lagi untuk kasus ini, tapi dia tetap jaring terakhir kalau
    ada jalur lain yang lolos.

Jalankan: python _patch_2026-09-06b.py   (lalu python _uat_2026-09-06b.py)
"""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.1.json")
DST = os.path.join(DIR, "2026-09-06-VIRA-Personal-Main-v3.2.json")

with open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

nodes = {n["name"]: n for n in wf["nodes"]}
jejak = []


def ganti(teks, lama, baru, label):
    n = teks.count(lama)
    if n != 1:
        raise SystemExit("GAGAL [%s]: pola ditemukan %d kali (harus tepat 1)." % (label, n))
    jejak.append(label)
    return teks.replace(lama, baru)


LAMA = """// [V2.1] Gerbang 1 - tipe sistem/reaction selalu dibuang, walau membawa teks."""

BARU = """// [V3.2] Gerbang 0 - tanpa pengenal pengirim, ini bukan pesan orang.
// Webhook ini juga menerima event perangkat dari Kirimi, dan sebagiannya membawa
// field `message` berisi teks sehingga lolos gerbang "bukan teks valid" di bawah.
// Contoh nyata (2026-09-06 11:25 WIB):
//   { event:'device.last_active', deviceId:'D-BTUYM', message:'Device last active updated' }
// Syaratnya PENGENAL, bukan daftar nama event: pesan dari manusia selalu membawa
// salah satu field di bawah, event perangkat tidak pernah. Daftar nama event akan
// basi begitu Kirimi menambah jenis baru; syarat ini tidak.
const _idKandidat = [body.from, body.senderAlt, body.sender, body.remoteJid,
                     body.chatId, body.participant, body.author, body.originLid];
const _adaPengenal = _idKandidat.some(v => String(v ?? '').replace(/\\D/g, '') !== '');
if (!_adaPengenal) {
    // warn, bukan throw: execution tetap hijau, tapi bentuk payloadnya terekam.
    // Kalau suatu saat nomor prospek datang di field yang belum kita baca, jejaknya
    // ketahuan di sini sebelum ada chat yang diam-diam tidak terbalas.
    console.warn('STOP: payload tanpa pengenal pengirim - bukan pesan chat. event='
        + String(body.event || '(tidak ada)')
        + ' | field=' + Object.keys(body).join(','));
    return [];
}

// [V2.1] Gerbang 1 - tipe sistem/reaction selalu dibuang, walau membawa teks."""

kode = nodes["Chat Counter"]["parameters"]["jsCode"]
nodes["Chat Counter"]["parameters"]["jsCode"] = ganti(kode, LAMA, BARU, "H3 Chat Counter gerbang identitas")

wf["name"] = "VIRA Personal — Main"

with open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print("=" * 72)
print("PATCH 2026-09-06b selesai")
print("=" * 72)
print("  masukan : %s" % os.path.basename(SRC))
print("  keluaran: %s" % os.path.basename(DST))
print("  node    : %d" % len(wf["nodes"]))
print()
for j in jejak:
    print("  DITERAPKAN  %s" % j)
print()
print("Berikutnya: python _uat_2026-09-06b.py")
