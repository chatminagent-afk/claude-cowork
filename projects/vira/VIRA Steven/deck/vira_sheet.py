# -*- coding: utf-8 -*-
"""
vira_sheet.py — baca & tulis "VIRA Steven Database" langsung dari Google Sheets.

Dipakai buat_deck.py (--live) dan kirim_deck.py, supaya tidak ada lagi langkah
"unduh sheet dulu" sebelum bikin deck. Kalau service account tidak tersedia,
pemanggilnya boleh jatuh balik ke VIRA Database.xlsx — tapi jatuhnya harus
DICETAK, jangan diam-diam, karena beda sumber = beda isi deck.

Kredensial tidak pernah dicetak. config() mengembalikan nilainya, tapi pemakainya
yang wajib menjaga jangan sampai masuk log.
"""
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SHEET_ID = "1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk"  # VIRA Steven Database
API = "https://sheets.googleapis.com/v4/spreadsheets/" + SHEET_ID
LINGKUP = ["https://www.googleapis.com/auth/spreadsheets"]

SA_KANDIDAT = [
    os.environ.get("VIRA_SA_JSON", ""),
    os.path.join(DIR, "service-account.json"),
    os.path.join(os.path.dirname(os.path.dirname(DIR)), "vira-506713-9304db011c49.json"),
]


class SheetError(RuntimeError):
    pass


def _berkas_sa():
    for p in SA_KANDIDAT:
        if p and os.path.exists(p):
            return p
    raise SheetError(
        "Service account tidak ketemu. Taruh JSON-nya di deck/service-account.json "
        "atau set VIRA_SA_JSON ke path-nya.")


_sesi_cache = {}


def _sesi():
    if "s" in _sesi_cache:
        return _sesi_cache["s"]
    try:
        import requests
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError as e:
        raise SheetError("Modul kurang: %s. Jalankan: python -m pip install requests google-auth" % e.name)
    kredensial = service_account.Credentials.from_service_account_file(_berkas_sa(), scopes=LINGKUP)
    s = AuthorizedSession(kredensial)
    _sesi_cache["s"] = s
    return s


def _huruf(i):
    """0 -> A, 25 -> Z, 26 -> AA."""
    h = ""
    i += 1
    while i:
        i, sisa = divmod(i - 1, 26)
        h = chr(65 + sisa) + h
    return h


def digits(s):
    if isinstance(s, float) and s.is_integer():
        s = int(s)
    return re.sub(r"\D", "", str(s or ""))


def baca(tab):
    """Seluruh tab jadi (header, list baris mentah). Baris = list nilai kolom."""
    r = _sesi().get("%s/values/%s" % (API, tab), params={"valueRenderOption": "FORMATTED_VALUE"})
    if r.status_code == 403:
        raise SheetError("Service account belum di-share ke spreadsheet-nya (403). "
                         "Bagikan sheet ke email service account sebagai Editor.")
    if not r.ok:
        raise SheetError("Gagal baca tab %s: %s %s" % (tab, r.status_code, r.text[:200]))
    nilai = r.json().get("values", [])
    if not nilai:
        raise SheetError("Tab %s kosong." % tab)
    header = [str(c).strip() for c in nilai[0]]
    return header, nilai[1:]


def baris_dict(tab):
    header, baris = baca(tab)
    keluar = []
    for i, r in enumerate(baris):
        r = list(r) + [""] * (len(header) - len(r))
        d = dict(zip(header, r))
        d["_baris"] = i + 2          # nomor baris di sheet (header = 1)
        keluar.append(d)
    return header, keluar


def config():
    """Tab CONFIG (key/value) jadi dict. JANGAN dicetak."""
    _, baris = baca("CONFIG")
    return {str(r[0]).strip(): (str(r[1]).strip() if len(r) > 1 and r[1] is not None else "")
            for r in baris if r and r[0]}


def cari_request(no_wa):
    """Satu baris REQUESTS berdasarkan no_wa. Kunci identitas = nomor, bukan urutan."""
    header, baris = baris_dict("REQUESTS")
    for d in baris:
        if digits(d.get("no_wa")) == digits(no_wa):
            return header, d
    raise SheetError("Tidak ada baris REQUESTS dengan no_wa %s" % no_wa)


def cari_stats(no_wa):
    """Satu baris STATS berdasarkan nomor. No WA primer, lid cadangan.

    Kunci identitas = nomor, bukan urutan. JANGAN pernah jatuh ke baris[0]:
    salah baris berarti mencatat deck ke orang lain, dan gagalnya diam-diam.
    """
    target = digits(no_wa)
    if not target:
        raise SheetError("Nomor kosong - tidak bisa mencari baris STATS.")
    header, baris = baris_dict("STATS")
    for d in baris:
        if digits(d.get("No WA")) == target:
            return header, d
    for d in baris:
        if digits(d.get("lid")) == target:
            return header, d
    raise SheetError("Tidak ada baris STATS dengan No WA maupun lid %s" % no_wa)


def tulis_sel(tab, header, nomor_baris, kolom, nilai):
    if kolom not in header:
        raise SheetError("Kolom '%s' tidak ada di tab %s" % (kolom, tab))
    a1 = "%s!%s%d" % (tab, _huruf(header.index(kolom)), nomor_baris)
    r = _sesi().put("%s/values/%s" % (API, a1),
                    params={"valueInputOption": "RAW"},
                    json={"values": [[nilai]]})
    if not r.ok:
        raise SheetError("Gagal tulis %s: %s %s" % (a1, r.status_code, r.text[:200]))
    return a1


def tambah_event(no_wa, nama, event, detail):
    r = _sesi().post("%s/values/EVENTS:append" % API,
                     params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
                     json={"values": [[waktu_wib(), str(no_wa), nama, event, detail]]})
    if not r.ok:
        raise SheetError("Gagal tulis EVENTS: %s %s" % (r.status_code, r.text[:200]))


def waktu_wib():
    import datetime
    wib = datetime.timezone(datetime.timedelta(hours=7))
    return datetime.datetime.now(wib).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    # Uji sambungan — sengaja tidak mencetak satu pun nilai kredensial.
    import sys
    print("service account :", os.path.basename(_berkas_sa()))
    c = config()
    print("CONFIG          : %d kunci terbaca" % len(c))
    for k in ("kirimi_user_code", "kirimi_secret", "kirimi_device_id", "admin_phone"):
        print("  %-18s %s" % (k, "ada" if c.get(k) else "KOSONG"))
    header, baris = baris_dict("REQUESTS")
    print("REQUESTS        : %d baris, %d kolom" % (len(baris), len(header)))
    if len(sys.argv) > 1:
        _, d = cari_request(sys.argv[1])
        terisi = [k for k, v in d.items() if str(v).strip() and k != "_baris"]
        print("  %s -> baris %d, %s (%d field terisi)"
              % (sys.argv[1], d["_baris"], d.get("nama_bisnis") or "(tanpa nama bisnis)", len(terisi)))
