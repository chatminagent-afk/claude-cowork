# -*- coding: utf-8 -*-
"""
cek_request.py — daftar brief deck di REQUESTS: mana yang siap digenerate, mana
yang decknya sudah dikirim, mana yang briefnya masih terlalu tipis.

    python cek_request.py           semua baris, terbaru dulu
    python cek_request.py --belum   hanya yang decknya belum dikirim
"""
import argparse
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import vira_sheet as vs

DIR = os.path.dirname(os.path.abspath(__file__))
TINGKAT1 = ("nama_bisnis", "industri", "masalah_utama")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--belum", action="store_true", help="hanya yang belum dikirim")
    a = ap.parse_args()

    header, baris = vs.baris_dict("REQUESTS")
    baris = [d for d in baris if str(d.get("no_wa") or "").strip()]
    baris.sort(key=lambda d: str(d.get("update_terakhir") or d.get("ts") or ""), reverse=True)

    n = 0
    for d in baris:
        terkirim = str(d.get("deck_dikirim_ts") or "").strip()
        if a.belum and terkirim:
            continue
        n += 1
        terisi = sum(1 for k, v in d.items() if k != "_baris" and str(v).strip())
        kurang = [k for k in TINGKAT1 if not str(d.get(k) or "").strip()]
        pdf = os.path.join(DIR, "keluaran",
                           __import__("re").sub(r"[^\w-]+", "-",
                                                d.get("nama_bisnis") or "tanpa-nama").strip("-").lower() + ".pdf")
        print("%s  %s" % (vs.digits(d.get("no_wa")), d.get("nama_bisnis") or "(tanpa nama bisnis)"))
        print("   nama      : %s | industri: %s" % (d.get("nama") or "-", d.get("industri") or "-"))
        print("   update    : %s | field terisi: %d/%d" % (d.get("update_terakhir") or d.get("ts") or "-",
                                                           terisi, len(header)))
        print("   deck      : %s | PDF lokal: %s"
              % (("dikirim " + terkirim) if terkirim else "BELUM dikirim",
                 "ada" if os.path.exists(pdf) else "belum digenerate"))
        if kurang:
            print("   kurang    : %s  (slide custom bisa hilang)" % ", ".join(kurang))
        print()
    if not n:
        print("Tidak ada baris yang cocok.")


if __name__ == "__main__":
    main()
