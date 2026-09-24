# -*- coding: utf-8 -*-
"""
kirim_deck.py — kirim PDF deck ke WhatsApp lewat Kirimi, dengan rem tangan.

Pakai:
    python kirim_deck.py --wa 628xxxxxxxxxx                 (PRATINJAU saja, tidak mengirim)
    python kirim_deck.py --wa 628xxxxxxxxxx --ke-admin --kirim   (kirim ke Steven dulu)
    python kirim_deck.py --wa 628xxxxxxxxxx --kirim         (kirim ke KLIEN)

Prinsip:
  * Tanpa --kirim, skrip ini TIDAK PERNAH mengirim apa pun. Default = pratinjau.
  * Menolak kalau deck_dikirim_ts sudah terisi (pakai --ulang kalau memang sengaja).
  * Menolak kalau PDF lebih tua dari update_terakhir brief — artinya brief berubah
    setelah deck dirender, jadi yang mau dikirim sudah basi.
  * Kredensial dibaca dari tab CONFIG dan tidak pernah dicetak.
  * Menolak kirim ke KLIEN kalau nama_bisnis / industri / masalah_utama kosong, kecuali
    Steven mengizinkannya lewat --lanjut-tanpa (gerbang yang sama dengan buat_deck.py).
"""
import argparse
import os
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import vira_sheet as vs
import buat_deck as bd

DIR = os.path.dirname(os.path.abspath(__file__))
KELUARAN = os.path.join(DIR, "keluaran")
CAPTION = os.path.join(DIR, "caption-deck.txt")
URL_FILE = "https://api.kirimi.id/v1/send-message-file"


def waktu_ke_epoch(s):
    """'2026-09-06 19:42:26' -> epoch. Kembalikan None kalau tidak terbaca."""
    import datetime
    s = str(s or "").strip()
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.datetime.strptime(s, f).timestamp()
        except ValueError:
            continue
    return None


def susun_caption(d, berkas_caption=None):
    path = berkas_caption or CAPTION
    with open(path, encoding="utf-8") as f:
        teks = f.read().strip()
    nama = (d.get("nama") or "").strip()
    bisnis = (d.get("nama_bisnis") or "").strip() or "bisnisnya"
    teks = teks.replace("{nama}", nama).replace("{nama_bisnis}", bisnis)
    # nama kosong -> "Halo kak, ..." bukan "Halo kak , ..."
    teks = re.sub(r"[ 	]+([,.!?])", r"\1", teks)
    return re.sub(r"[ 	]{2,}", " ", teks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wa", required=True, help="no_wa baris REQUESTS")
    ap.add_argument("--file", help="path PDF (default: keluaran/<slug nama_bisnis>.pdf)")
    ap.add_argument("--caption-file", help="file caption lain")
    ap.add_argument("--ke-admin", action="store_true",
                    help="kirim ke admin_phone (Steven), bukan ke klien")
    ap.add_argument("--kirim", action="store_true", help="benar-benar kirim")
    ap.add_argument("--ulang", action="store_true", help="izinkan walau deck_dikirim_ts sudah ada")
    ap.add_argument("--lanjut-tanpa", default="",
                    help="field wajib yang SUDAH DIIZINKAN Steven untuk kosong (%s)"
                         % ", ".join(bd.FIELD_BLOKIR))
    a = ap.parse_args()
    izin = bd.baca_izin(a.lanjut_tanpa)

    header, d = vs.cari_request(a.wa)
    cfg = vs.config()

    pdf = a.file or os.path.join(KELUARAN, bd.slug_berkas(d) + ".pdf")
    if not os.path.exists(pdf):
        raise SystemExit("PDF tidak ada: %s\nGenerate dulu: python buat_deck.py --wa %s --bersih"
                         % (pdf, a.wa))

    tujuan_klien = vs.digits(d.get("no_wa"))
    tujuan = vs.digits(cfg.get("admin_phone")) if a.ke_admin else tujuan_klien
    caption = susun_caption(d, a.caption_file)
    ukuran = os.path.getsize(pdf) / 1024.0

    sudah = str(d.get("deck_dikirim_ts") or "").strip()
    brief_ts = waktu_ke_epoch(d.get("update_terakhir") or d.get("ts"))
    basi = brief_ts is not None and os.path.getmtime(pdf) < brief_ts

    print("TUJUAN   : %s (%s)" % (tujuan, "ADMIN / Steven" if a.ke_admin else "KLIEN"))
    print("KLIEN    : %s — %s" % (d.get("nama") or "(tanpa nama)", d.get("nama_bisnis") or "(tanpa nama bisnis)"))
    print("BERKAS   : %s (%.0f KB)" % (os.path.basename(pdf), ukuran))
    print("BRIEF    : baris %d, update terakhir %s" % (d["_baris"], d.get("update_terakhir") or d.get("ts") or "-"))
    print("TERKIRIM : %s" % (sudah or "belum"))
    print("CAPTION  :")
    for baris in caption.splitlines():
        print("  | " + baris)
    tahan = bd.cetak_kelengkapan(bd.cek_kelengkapan(d, bd.slug_berkas(d)), izin)

    if tahan and not a.ke_admin:
        print("\nDIBLOKIR ke klien: %s kosong. Lengkapi REQUESTS lalu render ulang," % ", ".join(tahan))
        print("            atau kirim hanya kalau Steven sudah mengizinkan: --lanjut-tanpa %s"
              % ",".join(tahan))
        if a.kirim:
            raise SystemExit("Dihentikan — deck dengan field wajib kosong tidak dikirim ke klien.")

    if basi:
        print("\nPERINGATAN: brief lebih baru daripada PDF-nya. Render ulang dulu:")
        print("            python buat_deck.py --wa %s --bersih" % a.wa)
        if a.kirim and not a.ulang:
            raise SystemExit("Dihentikan. Pakai --ulang kalau memang mau kirim PDF ini.")

    if sudah and not a.ke_admin and not a.ulang:
        print("\nDeck ke nomor ini sudah tercatat terkirim %s." % sudah)
        if a.kirim:
            raise SystemExit("Dihentikan. Pakai --ulang kalau memang mau kirim lagi.")

    if not a.kirim:
        print("\nPRATINJAU saja — belum ada yang dikirim.")
        print("Kirim ke Steven : python kirim_deck.py --wa %s --ke-admin --kirim" % a.wa)
        if tahan:
            print("Kirim ke klien  : DIBLOKIR sampai field wajib lengkap atau diizinkan Steven")
        else:
            print("Kirim ke klien  : python kirim_deck.py --wa %s --kirim%s"
                  % (a.wa, (" --lanjut-tanpa " + ",".join(sorted(izin))) if izin else ""))
        return

    import requests
    for k in ("kirimi_user_code", "kirimi_secret", "kirimi_device_id"):
        if not cfg.get(k):
            raise SystemExit("CONFIG.%s kosong — tidak bisa kirim." % k)

    with open(pdf, "rb") as f:
        r = requests.post(URL_FILE,
                          data={"user_code": cfg["kirimi_user_code"],
                                "secret": cfg["kirimi_secret"],
                                "device_id": cfg["kirimi_device_id"],
                                "phone": tujuan,
                                "message": caption},
                          files={"file": (os.path.basename(pdf), f, "application/pdf")},
                          timeout=180)
    ok = r.ok
    try:
        badan = r.json()
        ok = ok and (badan.get("status") is not False)
    except Exception:
        badan = r.text[:300]
    if not ok:
        print("\nGAGAL kirim (%s): %s" % (r.status_code, badan))
        raise SystemExit(1)
    print("\nTERKIRIM ke %s. Balasan Kirimi: %s" % (tujuan, badan))

    if a.ke_admin:
        print("Tidak mencatat apa pun ke sheet — ini baru kiriman review ke Steven.")
        return

    ts = vs.waktu_wib()
    vs.tulis_sel("REQUESTS", header, d["_baris"], "deck_dikirim_ts", ts)
    vs.tambah_event(tujuan_klien, d.get("nama") or "", "deck_terkirim",
                    "%s (%.0f KB) via kirim_deck.py" % (os.path.basename(pdf), ukuran))
    print("SHEET    : REQUESTS.deck_dikirim_ts = %s, EVENTS +1 baris" % ts)

    # STATS.deck_terkirim_ts -- kolom inilah yang dibaca VIRA (node Rakit Konteks)
    # dan workflow Follow-up. Epoch detik, mengikuti konvensi semua kolom *_ts di
    # STATS; sengaja beda nama dari REQUESTS.deck_dikirim_ts yang berformat WIB.
    # Decknya SUDAH terkirim di titik ini, jadi gagal mencatat TIDAK BOLEH raise --
    # itu akan terbaca seperti gagal kirim. Dicetak keras, lalu jalan terus.
    try:
        epoch = str(int(time.time()))
        h_stats, baris_stats = vs.cari_stats(tujuan_klien)
        vs.tulis_sel("STATS", h_stats, baris_stats["_baris"], "deck_terkirim_ts", epoch)
        print("SHEET    : STATS.deck_terkirim_ts = %s (baris %d)" % (epoch, baris_stats["_baris"]))
    except Exception as e:
        print("PERINGATAN: deck TERKIRIM, tapi STATS.deck_terkirim_ts GAGAL ditulis: %s" % e)
        print("            VIRA belum akan tahu decknya sudah sampai, dan follow-up masih")
        print("            menganggapnya menunggu deck. Isi manual di tab STATS.")


if __name__ == "__main__":
    main()
