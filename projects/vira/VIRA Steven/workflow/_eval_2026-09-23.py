# -*- coding: utf-8 -*-
"""
_eval_2026-09-23.py - uji panjang & gaya balasan dengan MODEL ASLI, sebelum deploy.

UAT (_uat_*.py) menjalankan kode node asli tapi output modelnya dipalsukan, jadi tidak bisa
menilai apakah DeepSeek benar-benar menulis ringkas. Berkas ini menutup celah itu:

  Cek_user_status -> Detect Lead Source -> Preprocess -> FAQ Retrieve -> Rakit Konteks
      -> [DeepSeek ASLI, lewat workflow "VIRA Eval — Balasan (sementara)"]
      -> Process All -> STATS & memori tiruan untuk giliran berikutnya

Semua kode node diambil dari file workflow (v3.11 dan v3.12) dan dijalankan di V8, persis
seperti UAT. Katalog (FAQ/PROGRAM/LINKS/ABOUT_STEVEN) dibaca dari sheet live, HANYA baca.
Tidak ada WA yang terkirim dan tidak ada sheet yang ditulis.

Pesan prospek tiap skenario TETAP (bukan dikarang model), supaya v3.11 dan v3.12 dinilai
dengan masukan yang sama persis.

Jalankan: python _eval_2026-09-23.py [--versi v3.12] [--ulang 2]
Keluaran: 2026-09-23-hasil-eval-balasan.md (+ .json mentah)
"""
import argparse
import io
import json
import os
import re
import statistics
import sys
import time
import urllib.request

from py_mini_racer import MiniRacer

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(DIR), "deck"))
import vira_sheet  # noqa: E402

WF = {
    "v3.11": os.path.join(DIR, "2026-09-22-VIRA-Personal-Main-v3.11.json"),
    "v3.12": os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.12.json"),
}
EVAL_WF = os.path.join(DIR, "2026-09-23-VIRA-Eval-Balasan-sementara.json")
N8N = "https://n8n.srv1270416.hstgr.cloud/webhook/"
OUT_MD = os.path.join(DIR, "2026-09-23-hasil-eval-balasan.md")
OUT_JSON = os.path.join(DIR, "2026-09-23-hasil-eval-balasan.json")

SKENARIO = [
    ("S1 Humanizer — ulang uji Steven 23/09 (jawaban pendek-pendek)", [
        "Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku.",
        "abdul\naku owner humanizer\njualan parfum\nkdg ribet balesin org ty 1 1",
        "100 an chat",
        "tanya2 dlu, trs minta pricelist, dan pesen",
        "aroma, ketahanan, sama ready stok ga",
        "iya kadang ada yg kelewat",
    ]),
    ("S2 Katering — ulang uji 17/09", [
        "Halo kak, mau tanya soal chatbot",
        "Nadia kak, bisnis aku katering, chat suka numpuk pas malem",
        "Dapur Nadia",
        "sekitar 20-30 chat sehari",
        "biasanya tanya menu dulu, trus harga, baru pesen",
        "ada yg sampe kelewat sih kak kadang",
    ]),
    ("S3 Klinik — prospek banyak BERTANYA (jawaban tidak boleh terpotong)", [
        "Halo, ini bisa buat apa aja ya?",
        "Budi, Klinik Sehat Gigi",
        "harganya berapa kak?",
        "bisa connect ke IG juga ga?",
        "oke, chat masuk sehari 50an",
    ]),
    ("S4 Bimbel — prospek bercerita panjang", [
        "halo",
        "Sari dari Bimbel Cerdas Mandiri",
        "bimbel SD SMP, muridnya kebanyakan dari sekitar rumah, orang tua suka nanya jadwal sama biaya lewat WA, aku sendiri yang bales",
        "sehari bisa 40 chat kalo lagi musim daftar",
        "tanya biaya, jadwal, trus daftar lewat form",
    ]),
    ("S5 Kopi — sampai minta deck", [
        "Halo kak, aku Rina dari Kopi Senja, lagi cari AI buat bales chat",
        "coffee shop kak, chat reservasi numpuk pas weekend",
        "100an chat pas weekend",
        "boleh dong dibuatin deck",
        "makasih kak",
    ]),
]

# ── mesin V8, sama dengan harness UAT ────────────────────────────────────────
SHIM = r"""
globalThis.__run = function (code, ctx) {
  const bungkus = (items) => {
    const o = { all: () => items, first: () => (items.length ? items[0] : undefined),
                last: () => (items.length ? items[items.length - 1] : undefined) };
    o.item = items.length ? items[0] : undefined;
    return o;
  };
  const $ = (name) => {
    if (!Object.prototype.hasOwnProperty.call(ctx.nodes, name)) throw new Error("NODE TIDAK ADA: " + name);
    return bungkus(ctx.nodes[name]);
  };
  const $input = bungkus(ctx.input || []);
  const logs = [];
  const tulis = (lvl) => function () { logs.push(lvl + ": " + Array.prototype.slice.call(arguments).join(" ")); };
  const konsol = { log: tulis("log"), warn: tulis("warn"), error: tulis("error"), info: tulis("info") };
  let out = null, err = null;
  try {
    const fn = new Function("$", "$input", "$json", "$getWorkflowStaticData", "$vars", "console", code);
    out = fn($, $input, $input.item ? $input.item.json : {}, () => ({}), {}, konsol);
    if (out === undefined) out = null;
  } catch (e) { err = String((e && e.message) || e); }
  return { out: out, err: err, logs: logs };
};
"""
V8 = MiniRacer()
V8.eval(SHIM)


def item(**kw):
    return {"json": kw}


def jalan(nodes_wf, nama, nodes, inp):
    r = V8.call("__run", nodes_wf[nama]["parameters"]["jsCode"], {"nodes": nodes, "input": inp})
    if r["err"]:
        raise RuntimeError("%s: %s" % (nama, r["err"]))
    o = r["out"]
    o = o[0] if isinstance(o, list) else o
    return (o or {}).get("json", o)


def cfg():
    return {"sheet_id": "SHEET", "client_name": "Steven", "bot_name": "Vira",
            "admin_phone": "6285171701168", "whitelist_enabled": False, "whitelist_numbers": [],
            "blocklist_numbers": [], "bot_wa_number": "6285155202354", "ignore_self_number": True,
            "rate_limit_max": 15, "rate_limit_window_sec": 60, "debounce_seconds": 60,
            "vision_mode": "full", "vision_max_images": 3, "katalog_cache_minutes": 10,
            "fact_ttl_days": 60, "lead_source_map": []}


# ── model asli ───────────────────────────────────────────────────────────────
def _eval_akses():
    wf = json.load(io.open(EVAL_WF, encoding="utf-8"))
    n = {x["name"]: x for x in wf["nodes"]}
    token = re.search(r"const TOKEN = 'REDACTED'", n["Cek Token & Susun Body"]["parameters"]["jsCode"]).group(1)
    return N8N + n["Eval Masuk"]["parameters"]["path"], token


URL, TOKEN = _eval_akses()


def model(messages, coba=3):
    body = json.dumps({"messages": messages}).encode("utf-8")
    for i in range(coba):
        try:
            req = urllib.request.Request(URL, data=body, method="POST",
                                         headers={"content-type": "application/json", "x-eval-token": TOKEN})
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.loads(r.read().decode("utf-8"))
            if isinstance(d, list):
                d = d[0]
            return d["choices"][0]["message"]["content"]
        except Exception as e:  # noqa: BLE001
            if i == coba - 1:
                raise RuntimeError("eval webhook gagal: %s" % e)
            time.sleep(5)


# ── metrik ────────────────────────────────────────────────────────────────────
SEPELE = set("aku saya kak kakak ka ya yaa iya dan atau yang itu ini di ke dari ada aja saja sih kok deh dong "
             "juga udah sudah lagi mau bisa gak tidak buat untuk sama dengan biasanya kalau kalo klo jadi terus "
             "nah oke ok baru an nya pun lah kah kadang semua".split())
NORM = {"dlu": "dulu", "trs": "terus", "sm": "sama", "yg": "yang", "pesen": "pesan", "bales": "balas",
        "balesin": "balas", "dibales": "balas", "ty": "tanya", "nanya": "tanya", "kdg": "kadang"}


def kata_isi(s):
    ws = re.sub(r"[^\w\s]", " ", s.lower()).split()
    ws = [NORM.get(re.sub(r"(?<=[a-z])\d+$", "", w), re.sub(r"(?<=[a-z])\d+$", "", w)) for w in ws]
    return [w for w in ws if w and w not in SEPELE]


def kalimat(t):
    return [k for k in re.split(r"(?<=[.?!])\s+|\n+", t.strip()) if k.strip()]


def metrik(balasan, pesan):
    kal = kalimat(balasan)
    isi_pesan = set(kata_isi(pesan))
    k0 = kal[0] if kal else ""
    sama = len(set(kata_isi(k0)) & isi_pesan)
    gema = ("?" not in k0) and bool(isi_pesan) and (sama >= 3 or (sama >= 2 and sama / len(isi_pesan) >= 0.5))
    tanya_prospek = bool(re.search(r"\?|\b(apa|apakah|gimana|gmn|bagaimana|berapa|brp|kenapa|knp|kapan|mana)\b", pesan, re.I))
    promosi = (not tanya_prospek) and bool(re.search(
        r"\b(vira|ai)\b[^.?!]{0,60}\b(bisa|otomatis|pegang|jawab|bantu|24 jam)|\bbisa diotomasi|tinggal fokus", balasan, re.I))
    return {"kata": len(balasan.split()), "kalimat": len(kal), "tanya": balasan.count("?"),
            "gema": gema, "promosi": promosi, "prospek_bertanya": tanya_prospek}


# ── simulasi satu percakapan ─────────────────────────────────────────────────
def simulasi(versi, katalog, pesan_list, no_wa):
    wf = json.load(io.open(WF[versi], encoding="utf-8"))
    nodes = {n["name"]: n for n in wf["nodes"]}
    sistem_tpl = nodes["AI Agent"]["parameters"]["options"]["systemMessage"]
    k_memori = nodes["Simple Memory"]["parameters"].get("contextWindowLength", 5)
    stats = {"No WA": no_wa, "Nama": "Prospek", "greeting_sent": "", "Counter": "", "bot_mode": "ON",
             "nama_lengkap": "", "nama_bisnis": "", "industri": "", "masalah_utama": "", "volume_chat": "",
             "budget_range": "", "minat_paket": "", "bahasa": "", "deck_requested": "", "brief_terisi": "",
             "last_bot_reply": "", "last_bot_reply_ts": "", "deck_terkirim_ts": ""}
    memori, giliran = [], []
    for pesan in pesan_list:
        now_s = int(time.time())
        cc = {"user_phone": no_wa, "user_wa": no_wa, "user_lid": "", "user_name": "Prospek",
              "process_start_ts": now_s * 1000, "original_message": pesan, "stats_message": pesan,
              "media_url": "", "media_kind": "none", "formatted_time": "10:00:00"}
        resolve = dict(stats, resolved_key=no_wa, userRow=dict(stats), lead_source_db="Organik")
        cu = jalan(nodes, "Cek_user_status", {
            "Chat Counter": [item(**cc)], "Resolve User Row": [item(**resolve)],
            "Parse Config": [item(config=cfg())],
            "Re-Read STATS Debounce": [item(**dict(stats, buffer_done_ts=0))],
            "Read MSG_BUFFER": [item(ts=now_s * 1000, message=pesan, media_url="", media_type="")],
        }, [item()])
        ld = jalan(nodes, "Detect Lead Source", {"Resolve User Row": [item(**resolve)],
                                                 "Parse Config": [item(config=cfg())]}, [item(**cu)])
        pr = jalan(nodes, "Preprocess - Context Detection", {"Parse Config": [item(config=cfg())]}, [item(**ld)])
        fq = jalan(nodes, "FAQ Retrieve", {"Preprocess - Context Detection": [item(**pr)],
                                           "Read FAQ": [], "Read PRODUK Data": []}, [item(katalog=katalog)])
        rk = jalan(nodes, "Rakit Konteks", {"Parse Config": [item(config=cfg())],
                                            "Resolve User Row": [item(**resolve)],
                                            "Preprocess - Context Detection": [item(**pr)]}, [item(**fq)])
        sistem = re.sub(r"\{\{\s*\$json\.(\w+)\s*\}\}", lambda m: str(rk.get(m.group(1), "")), sistem_tpl)
        sistem = sistem[1:] if sistem.startswith("=") else sistem
        teks = rk["ai_input_text"]
        msgs = [{"role": "system", "content": sistem}]
        for h, a in memori[-k_memori:]:
            msgs += [{"role": "user", "content": h}, {"role": "assistant", "content": a}]
        msgs.append({"role": "user", "content": teks})
        t0 = time.time()
        mentah = model(msgs)
        detik = round(time.time() - t0, 1)
        pa = jalan(nodes, "Process All", {
            "Chat Counter": [item(**cc)], "Preprocess - Context Detection": [item(**pr)],
            "Parse Config": [item(config=cfg())], "Resolve User Row": [item(**resolve)],
            "Rakit Konteks": [item(**rk)]}, [item(output=mentah)])
        kirim = pa["cleanOutput"]
        galian = re.search(r"^galian_berikutnya: (.*)$", rk.get("prospect_context", ""), re.M)
        giliran.append({
            "pesan": pesan, "mentah": mentah, "kirim": kirim, "detik": detik,
            "galian": galian.group(1) if galian else "",
            "ringkas": pa.get("ringkas", ""), "deck": bool(pa.get("deckNotify")),
            "talk": bool(pa.get("isTalkToAdmin")),
            "m_kirim": metrik(kirim, pesan), "m_mentah": metrik(re.sub(r"\[[^\]]*\]", "", mentah), pesan),
        })
        memori.append((teks, mentah))
        stats.update({
            "Counter": str(int(stats["Counter"] or 0) + 1), "greeting_sent": "Y",
            "nama_lengkap": pa.get("nama_lengkap_merged") or "",
            "nama_bisnis": pa.get("nama_bisnis_merged") or stats["nama_bisnis"],
            "industri": pa.get("industri_merged") or stats["industri"],
            "masalah_utama": pa.get("masalah_utama_merged") or stats["masalah_utama"],
            "volume_chat": pa.get("volume_chat_merged") or stats["volume_chat"],
            "bahasa": pa.get("bahasa_merged") or stats["bahasa"],
            "deck_requested": "Y" if pa.get("deckNotify") else stats["deck_requested"],
            "bot_mode": "OFF" if pa.get("matikanBot") else "ON",
            "last_bot_reply": kirim, "last_bot_reply_ts": str(int(time.time())),
        })
        print("  [%s] %-38s -> %2d kata %s%s" % (versi, pesan.replace("\n", " / ")[:38],
                                                 len(kirim.split()), "(dipangkas: %s) " % pa["ringkas"] if pa.get("ringkas") else "",
                                                 "%.0fs" % detik))
        if stats["bot_mode"] == "OFF":
            break
    return {"giliran": giliran, "stats_akhir": {k: stats[k] for k in (
        "nama_lengkap", "nama_bisnis", "industri", "masalah_utama", "volume_chat", "deck_requested")}}


def katalog_live():
    kat = {}
    for kunci, tab in (("faq", "FAQ"), ("program", "PROGRAM"), ("links", "LINKS"), ("about", "ABOUT_STEVEN")):
        _, baris = vira_sheet.baris_dict(tab)
        kat[kunci] = [{k: v for k, v in b.items() if k != "_baris"} for b in baris]
    return kat


VOL_DISEBUT = re.compile(r"(^|[^a-z\d])\d+\s*(an)?\s*(chat|pesan)|(sehari|per ?hari)[^.?!]{0,25}\d|\d+(an)?[^.?!]{0,25}(sehari|per ?hari)", re.I)
VOL_DITANYA = re.compile(r"berapa\s+(chat|pesan)|(chat|pesan)[^.?!]{0,25}berapa|berapa[^.?!]{0,25}(chat|pesan)", re.I)


def ringkas_versi(hasil):
    perk = [s["giliran"][0] for s in hasil]
    lanjut = [g for s in hasil for g in s["giliran"][1:]]
    galian = [g for g in lanjut if not g["m_kirim"]["prospek_bertanya"]]
    tanya_ulang_vol = kembar = 0
    for s in hasil:
        disebut = False
        tanya_lalu = []
        for g in s["giliran"]:
            disebut = disebut or bool(VOL_DISEBUT.search(g["pesan"]))
            if disebut and VOL_DITANYA.search(g["kirim"]):
                tanya_ulang_vol += 1
            tanya = [k for k in kalimat(g["kirim"]) if "?" in k]
            for q in tanya:
                x = set(kata_isi(q))
                if any(len(x & set(kata_isi(t))) >= 3 and len(x & set(kata_isi(t))) / max(1, min(len(x), len(set(kata_isi(t))))) >= 0.7
                       for t in tanya_lalu):
                    kembar += 1
                    break
            tanya_lalu = tanya
    return {
        "balasan (tanpa perkenalan)": len(lanjut),
        "median kata": statistics.median(g["m_kirim"]["kata"] for g in lanjut),
        "maks kata": max(g["m_kirim"]["kata"] for g in lanjut),
        "median kata saat prospek tidak bertanya": statistics.median(g["m_kirim"]["kata"] for g in galian),
        "membuka dengan merangkum (gema)": sum(g["m_kirim"]["gema"] for g in lanjut),
        "promosi VIRA tanpa ditanya": sum(g["m_kirim"]["promosi"] for g in lanjut),
        "> 2 kalimat saat prospek tidak bertanya": sum(1 for g in galian if g["m_kirim"]["kalimat"] > 2),
        "> 1 pertanyaan dalam satu balasan": sum(1 for g in lanjut if g["m_kirim"]["tanya"] > 1),
        "jumlah chat ditanya padahal sudah disebut": tanya_ulang_vol,
        "pertanyaan kembar dengan balasan sebelumnya": kembar,
        "perkenalan: median kata": statistics.median(g["m_kirim"]["kata"] for g in perk),
        "perkenalan: > 1 pertanyaan": sum(1 for g in perk if g["m_kirim"]["tanya"] > 1),
        "dipangkas jaring RINGKAS": sum(1 for s in hasil for g in s["giliran"] if g["ringkas"]),
        "minta deck dibalas tawaran deck lagi": sum(
            1 for s in hasil for g in s["giliran"]
            if re.search(r"\b(deck|pitch|proposal)\b|dibuat(in|kan)", g["pesan"], re.I)
            and re.search(r"mau aku mintakan", g["kirim"], re.I)),
        "balasan 'Maaf, ada kendala'": sum(1 for s in hasil for g in s["giliran"] if g["kirim"].startswith("Maaf, ada kendala")),
        "STATS nama usaha benar": "%d/%d" % (
            sum(1 for s in hasil if s["judul"][:2] in NAMA_USAHA_BENAR
                and s["stats_akhir"]["nama_bisnis"].lower() == NAMA_USAHA_BENAR[s["judul"][:2]].lower()),
            sum(1 for s in hasil if s["judul"][:2] in NAMA_USAHA_BENAR)),
        "STATS nama usaha kotor": sum(1 for s in hasil if s["stats_akhir"]["nama_bisnis"]
                                      and s["stats_akhir"]["nama_bisnis"].lower()
                                      not in ("humanizer", "dapur nadia", "klinik sehat gigi", "bimbel cerdas mandiri", "kopi senja")),
    }


# S2 sengaja tidak dihitung: "Dapur Nadia" dikirim di giliran yang skripnya belum tentu menanyakannya.
NAMA_USAHA_BENAR = {"S1": "humanizer", "S3": "Klinik Sehat Gigi", "S4": "Bimbel Cerdas Mandiri", "S5": "Kopi Senja"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versi", nargs="*", default=["v3.11", "v3.12"])
    ap.add_argument("--ulang", type=int, default=1)
    a = ap.parse_args()
    kat = katalog_live()
    print("katalog live: faq=%d program=%d links=%d about=%d" % tuple(len(kat[k]) for k in ("faq", "program", "links", "about")))
    hasil = {}
    for versi in a.versi:
        hasil[versi] = []
        for u in range(1 if versi == "v3.11" else a.ulang):   # pembanding cukup sekali
            for i, (judul, pesan) in enumerate(SKENARIO):
                print("%s | %s | ulang %d" % (versi, judul, u + 1))
                r = simulasi(versi, kat, pesan, "62800000%02d%02d" % (i, u))
                r["judul"] = judul
                r["ulang"] = u + 1
                hasil[versi].append(r)
    json.dump(hasil, io.open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    L = ["# Hasil eval balasan VIRA — model asli (%s)" % time.strftime("%Y-%m-%d %H:%M"), "",
         "DeepSeek `deepseek-v4-pro` asli, temperature 0.7, lewat workflow eval sementara. "
         "Kode node asli dari file workflow; katalog dari sheet live (baca saja). "
         "Pesan prospek sama persis untuk semua versi.", "", "## Ringkasan", "",
         "| Metrik | " + " | ".join(hasil) + " |", "|---|" + "---|" * len(hasil)]
    rv = {v: ringkas_versi(h) for v, h in hasil.items()}
    for k in rv[next(iter(rv))]:
        L.append("| %s | %s |" % (k.replace("_", " "), " | ".join(str(rv[v][k]) for v in hasil)))
    for versi, daftar in hasil.items():
        L += ["", "## %s" % versi]
        for s in daftar:
            L += ["", "### %s%s" % (s["judul"], " (ulang %d)" % s["ulang"] if versi != "v3.11" and a.ulang > 1 else ""), "",
                  "STATS akhir: " + ", ".join("%s=%s" % (k, v or "-") for k, v in s["stats_akhir"].items()), "",
                  "| # | Prospek | VIRA (terkirim) | kata | catatan |", "|---|---|---|---|---|"]
            for i, g in enumerate(s["giliran"], 1):
                cat = []
                if g["ringkas"]:
                    cat.append("dipangkas jaring: %s (model %d kata)" % (g["ringkas"], g["m_mentah"]["kata"]))
                if g["m_kirim"]["gema"]:
                    cat.append("GEMA")
                if g["m_kirim"]["promosi"]:
                    cat.append("PROMOSI")
                if g["deck"]:
                    cat.append("brief/deck")
                if g["galian"]:
                    cat.append("galian: " + g["galian"][:40])
                L.append("| %d | %s | %s | %d | %s |" % (i, g["pesan"].replace("\n", " / ").replace("|", "/"),
                                                         g["kirim"].replace("\n", " ").replace("|", "/"),
                                                         g["m_kirim"]["kata"], "; ".join(cat)))
    io.open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\nRINGKASAN")
    for v, r in rv.items():
        print(" ", v, json.dumps(r))
    print("tulis:", os.path.basename(OUT_MD))


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    os._exit(0)   # mesin V8 (MiniRacer) tidak menutup sendiri di Windows
