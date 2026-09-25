# -*- coding: utf-8 -*-
"""
_eval_2026-09-25.py - eval MODEL ASLI untuk insiden live 2026-09-25 ("Reza", iklan IG): prospek membalas
"Brp" atas sapaan yang menanyakan nama + nama usaha. v3.13 (= live) vs v3.14, sebelum deploy.

Rantai & model sama dengan _eval_2026-09-23b.py (dipakai ulang lewat import): kode node asli di V8,
DeepSeek ASLI lewat workflow "VIRA Eval — Balasan (sementara)" (deepseek-v4-pro, temperature 0.7,
maxTokens 3000 = parameter node DeepSeek Personal Chat live). Katalog dibaca dari sheet live, HANYA baca.
Tidak ada WA terkirim, tidak ada sheet yang ditulis.

Giliran 1 DIPAKSA = sapaan yang benar-benar terkirim ke Reza 12:12 (model tidak dipanggil), supaya
giliran 2 berangkat dari keadaan yang persis sama dengan live. Giliran 2 = pesan prospek, model asli.

Jalankan (dua proses paralel boleh):
  python _eval_2026-09-25.py --versi v3.13 --ulang 10 --json bagian_brp_v313.json
  python _eval_2026-09-25.py --versi v3.14 --ulang 10 --varian --json bagian_brp_v314.json
  python _eval_2026-09-25.py --gabung bagian_brp_v313.json bagian_brp_v314.json
Keluaran gabungan: 2026-09-25-hasil-eval-brp-v3.14.md (+ .json mentah)
"""
import argparse
import importlib.util
import io
import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("eval0923b", os.path.join(DIR, "_eval_2026-09-23b.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
E.WF["v3.14"] = os.path.join(DIR, "2026-09-25-VIRA-Personal-Main-v3.14.json")

OUT_MD = os.path.join(DIR, "2026-09-25-hasil-eval-brp-v3.14.md")
OUT_JSON = os.path.join(DIR, "2026-09-25-hasil-eval-brp-v3.14.json")

PESAN_1 = "Halo VIRA, aku lihat iklannya di IG, mau ngobrol soal AI customer service."
SAPAAN_REZA = ("Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia buat untuk "
               "kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang. Btw, boleh tau nama kakak siapa "
               "dan nama usahanya apa?")
HANYA_BASA_BASI = re.compile(r"^(?:(?:salam kenal|halo|hai|hi|oke+|ok|okay|siap|baik|sip|noted|makasih|terima kasih|"
                             r"thanks|maaf|wah|nah|oh)\b[\s,]*(?:(?:kak|kakak|ka)\b)?[\s,.!]*)+$", re.I)
FACTS_NAMA_TANYA = re.compile(r"\[FACTS[^\]]*\bnama\s*=\s*\"(brp|berapa|brapa)", re.I)

_model_asli = E.model
PAKSA_SAPAAN = [True]   # dimatikan untuk regresi S1-S7


def model_paksa_sapaan(messages, coba=3):
    """Giliran pertama (belum ada balasan asisten di memori) = sapaan live persis."""
    if PAKSA_SAPAAN[0] and not any(m["role"] == "assistant" for m in messages):
        return SAPAAN_REZA
    return _model_asli(messages, coba)


E.model = model_paksa_sapaan


def nilai(run):
    g1, g2 = run["giliran"][0], run["giliran"][1]
    kirim, mentah = g2["kirim"], g2["mentah"]
    jawab_harga = bool(re.search(r"\brp\.?\s?\d|\b(basic|premium)\b", kirim, re.I))
    return {
        "sapaan_terkirim_persis": g1["kirim"] == SAPAAN_REZA,
        "konteks_harga": g2["konteks_harga"],
        "jawab_harga": jawab_harga,
        "salam_kenal": bool(re.search(r"salam kenal", kirim, re.I)),
        "nama_tersimpan": run["stats_akhir"]["nama_lengkap"],
        "buntu": ("?" not in kirim and not jawab_harga) or bool(HANYA_BASA_BASI.match(kirim.strip())),
        "catatan_bocor": bool(E.CATATAN_BOCOR.search(kirim)),
        "facts_nama_tanya": bool(FACTS_NAMA_TANYA.search(mentah)),
        "kata": len(kirim.split()),
        "ringkas": g2["ringkas"],
    }


def jalankan(versi, ulang, varian):
    E.V8 = E.MiniRacer()
    E.V8.eval(E.SHIM)
    katalog = E.katalog_live()
    daftar = [("Brp", ulang)] + ([("brp kak?", 3), ("Berapa?", 3)] if varian else [])
    hasil = []
    for pesan2, n in daftar:
        for k in range(1, n + 1):
            no = "6285199%06d" % (len(hasil) + 1)
            run = E.simulasi(versi, katalog, [PESAN_1, pesan2], no)
            hasil.append({"versi": versi, "pesan2": pesan2, "ulang": k, "giliran": run["giliran"],
                          "stats_akhir": run["stats_akhir"], "nilai": nilai(run)})
            v = hasil[-1]["nilai"]
            print("  [%s] %-9s #%d  harga=%s salam_kenal=%s nama=%r buntu=%s | %s" % (
                versi, pesan2, k, v["jawab_harga"], v["salam_kenal"], v["nama_tersimpan"], v["buntu"],
                run["giliran"][1]["kirim"][:90]), flush=True)
    return hasil


def tulis(semua):
    json.dump(semua, io.open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    baris = ["# Eval model asli — insiden 'Brp' (Reza, 2026-09-25): v3.13 vs v3.14", "",
             "Model: deepseek-v4-pro, temperature 0.7, maxTokens 3000, thinking none (= node DeepSeek Personal Chat live), "
             "lewat workflow eval. Giliran 1 dipaksa = sapaan live persis; giliran 2 = pesan prospek, model asli. "
             "Katalog dari sheet live (baca saja). Tidak ada WA terkirim / sheet ditulis.", "",
             "| versi | pesan | n | sapaan persis | konteks harga | jawab harga | 'salam kenal' | nama tersimpan | buntu | catatan bocor | FACTS nama=kata tanya | kata (median) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    kelompok = {}
    for h in semua:
        kelompok.setdefault((h["versi"], h["pesan2"]), []).append(h["nilai"])
    for (versi, pesan), vs in sorted(kelompok.items()):
        n = len(vs)
        hit = lambda k: "%d/%d" % (sum(1 for v in vs if v[k]), n)  # noqa: E731
        kata = sorted(v["kata"] for v in vs)[n // 2]
        baris.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %d |" % (
            versi, pesan, n, hit("sapaan_terkirim_persis"), hit("konteks_harga"), hit("jawab_harga"),
            hit("salam_kenal"), hit("nama_tersimpan"), hit("buntu"), hit("catatan_bocor"), hit("facts_nama_tanya"), kata))
    baris += ["", "## Balasan terkirim (giliran 2)", ""]
    for h in semua:
        v = h["nilai"]
        baris.append("- **%s · %s #%d** — %s%s  \n  > %s" % (
            h["versi"], h["pesan2"], h["ulang"],
            "nama=%r " % v["nama_tersimpan"] if v["nama_tersimpan"] else "",
            "(dipangkas: %s)" % v["ringkas"] if v["ringkas"] else "",
            h["giliran"][1]["kirim"].replace("\n", " ")))
    io.open(OUT_MD, "w", encoding="utf-8").write("\n".join(baris) + "\n")
    print("OK ->", os.path.basename(OUT_MD))


EVAL_V313 = os.path.join(DIR, "2026-09-23-hasil-eval-balasan-v3.13.json")
OUT_REGRESI_MD = os.path.join(DIR, "2026-09-25-hasil-eval-regresi-v3.14.md")
OUT_REGRESI_JSON = os.path.join(DIR, "2026-09-25-hasil-eval-regresi-v3.14.json")


def putar_ulang():
    """Rekaman model eval v3.13 (S1-S7, 2026-09-23) diputar lewat kode node v3.14 - model tidak dipanggil.
    Membuktikan perubahan KODE v3.14 tidak mengubah balasan terkirim / STATS di skenario lama."""
    E.V8 = E.MiniRacer()
    E.V8.eval(E.SHIM)
    kat = E.katalog_live()
    lama = json.load(io.open(EVAL_V313, encoding="utf-8"))["v3.13"]
    beda = beda_stats = 0
    for s in lama:
        pesan = [g["pesan"] for g in s["giliran"]]
        no = "62800000%02d%02d" % ([j for j, _ in E.SKENARIO].index(s["judul"]), s["ulang"])
        r = E.simulasi("v3.14", kat, pesan, no, rekaman=[g["mentah"] for g in s["giliran"]])
        for i, (g0, g1) in enumerate(zip(s["giliran"], r["giliran"]), 1):
            if g0["kirim"] != g1["kirim"]:
                beda += 1
                print("BEDA %s u%d #%d\n  lama: %s\n  baru: %s" % (s["judul"][:3], s["ulang"], i, g0["kirim"], g1["kirim"]))
        if len(r["giliran"]) != len(s["giliran"]) or r["stats_akhir"] != s["stats_akhir"]:
            beda_stats += 1
            print("STATS/GILIRAN %s u%d: %s -> %s" % (s["judul"][:3], s["ulang"], s["stats_akhir"], r["stats_akhir"]))
    print("putar ulang %d percakapan: balasan terkirim berbeda = %d, STATS/giliran berbeda = %d"
          % (len(lama), beda, beda_stats), flush=True)


def regresi(ulang_ke, keluar):
    """S1-S7 (skenario eval v3.13) dengan model asli di v3.14 - menguji perubahan PROMPT."""
    PAKSA_SAPAAN[0] = False
    E.V8 = E.MiniRacer()
    E.V8.eval(E.SHIM)
    kat = E.katalog_live()
    daftar = []
    for i, (judul, pesan) in enumerate(E.SKENARIO):
        print("v3.14 | %s | ulang %d" % (judul, ulang_ke), flush=True)
        r = E.simulasi("v3.14", kat, pesan, "62800000%02d%02d" % (i, ulang_ke))
        r["judul"], r["ulang"] = judul, ulang_ke
        daftar.append(r)
    json.dump({"v3.14": daftar}, io.open(keluar, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("tulis:", keluar, flush=True)


def gabung_regresi(berkas):
    hasil = {"v3.13": json.load(io.open(EVAL_V313, encoding="utf-8"))["v3.13"], "v3.14": []}
    for p in berkas:
        hasil["v3.14"] += json.load(io.open(p, encoding="utf-8"))["v3.14"]
    E.OUT_MD, E.OUT_JSON = OUT_REGRESI_MD, OUT_REGRESI_JSON
    E.tulis_md(hasil)
    md = io.open(OUT_REGRESI_MD, encoding="utf-8").read()
    md = md.replace("# Hasil eval balasan VIRA v3.13 — model asli", "# Regresi eval balasan VIRA — v3.13 (×3, 23/09) vs v3.14 (×3, 25/09), model asli", 1)
    io.open(OUT_REGRESI_MD, "w", encoding="utf-8").write(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versi")
    ap.add_argument("--ulang", type=int, default=10)
    ap.add_argument("--varian", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--gabung", nargs="*")
    ap.add_argument("--putar-ulang", action="store_true", help="rekaman model eval v3.13 lewat kode v3.14")
    ap.add_argument("--regresi", type=int, metavar="ULANG_KE", help="S1-S7 model asli di v3.14, tulis --json")
    ap.add_argument("--gabung-regresi", nargs="*")
    a = ap.parse_args()
    if a.putar_ulang:
        return putar_ulang()
    if a.regresi:
        return regresi(a.regresi, a.json)
    if a.gabung_regresi:
        return gabung_regresi(a.gabung_regresi)
    if a.gabung:
        semua = []
        for p in a.gabung:
            semua += json.load(io.open(p, encoding="utf-8"))
        tulis(semua)
        return
    hasil = jalankan(a.versi, a.ulang, a.varian)
    json.dump(hasil, io.open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK ->", a.json, flush=True)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    os._exit(0)   # mesin V8 (MiniRacer) tidak menutup sendiri di Windows
