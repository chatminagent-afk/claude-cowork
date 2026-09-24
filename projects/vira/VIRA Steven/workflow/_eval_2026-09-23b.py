# -*- coding: utf-8 -*-
"""
_eval_2026-09-23b.py - eval MODEL ASLI untuk v3.13, sebelum deploy. Turunan _eval_2026-09-23.py.

Beda dari versi sebelumnya:
  - Skenario S6 = uji live Steven 2026-09-23 13:22-13:45 ("Rehan", sewa raket padel), pesan persis.
  - Skenario S7 = minta ngobrol dengan Steven dalam bahasa singkat (uji live 14:05). Simulasi berhenti
    begitu bot dimatikan, sama dengan live.
  - Preprocess dijalankan dengan Resolve User Row (balasan terakhir) - v3.13 memakainya untuk tahu
    apakah pesan ini menjawab pertanyaan VIRA soal alur / pertanyaan pelanggan. v3.12 mengabaikannya.
  - Metrik baru: harga VIRA disebut tanpa diminta, catatan konteks dikutip ke prospek, pertanyaan
    yang sama dalam 2 balasan terakhir, STATS S6.
  - Bisa dijalankan paralel: satu proses per (versi, ulangan) menulis --json, lalu --gabung.

Rantai (kode node asli dari file workflow, di V8, sama dengan UAT):
  Cek_user_status -> Detect Lead Source -> Preprocess -> FAQ Retrieve -> Rakit Konteks
      -> [DeepSeek ASLI, lewat workflow "VIRA Eval — Balasan (sementara)"]
      -> Process All -> STATS & memori tiruan untuk giliran berikutnya
Katalog (FAQ/PROGRAM/LINKS/ABOUT_STEVEN) dibaca dari sheet live, HANYA baca. Tidak ada WA terkirim,
tidak ada sheet yang ditulis. Pesan prospek tiap skenario TETAP (bukan dikarang model).

Jalankan:
  python _eval_2026-09-23b.py --versi v3.13 --ulang-ke 1 --json bagian_v313_1.json
  python _eval_2026-09-23b.py --gabung bagian_*.json
Keluaran gabungan: 2026-09-23-hasil-eval-balasan-v3.13.md (+ .json mentah)
"""
import argparse
import glob
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

WF = {
    "v3.12": os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.12.json"),
    "v3.13": os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json"),
}
EVAL_WF = os.path.join(DIR, "2026-09-23-VIRA-Eval-Balasan-sementara.json")
N8N = "https://n8n.srv1270416.hstgr.cloud/webhook/"
OUT_MD = os.path.join(DIR, "2026-09-23-hasil-eval-balasan-v3.13.md")
OUT_JSON = os.path.join(DIR, "2026-09-23-hasil-eval-balasan-v3.13.json")

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
    ("S6 Padel — ulang uji live Steven 23/09 13:22 (Rehan, sewa raket padel)", [
        "Halo VIRA, aku lihat website-nya dan mau coba ngobrol soal AI customer service buat bisnisku.",
        "rehan\nusahaku sewa raket padel",
        "persewaan aja sih",
        "balesin chat 1 1 sih\nsuka tenggelem",
        "10-20 an",
        "gimana prosedurnya dan lain-lain",
        "harga dulu, trs klo udah aman baru ke payment",
        "okee",
    ]),
    ("S7 Laundry — minta ngobrol dengan Steven, bahasa singkat (uji live 14:05)", [
        "halo",
        "Dimas, Laundry Kilat",
        "chat numpuk tiap pagi, sering telat bales",
        "kpn bs ngmng sm steven?",
        "oke",
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
V8 = None


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


def model(messages, coba=3):
    url, token = _eval_akses()
    body = json.dumps({"messages": messages}).encode("utf-8")
    for i in range(coba):
        try:
            req = urllib.request.Request(url, data=body, method="POST",
                                         headers={"content-type": "application/json", "x-eval-token": token})
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
HARGA_VIRA = re.compile(r"\brp\.?\s?\d|\b(basic|premium)\b", re.I)
HARGA_DIMINTA = re.compile(r"\?|\bharga\w*\s+berapa\b|\bberapa\s+harga", re.I)
CATATAN_BOCOR = re.compile(r"yang dia ceritakan|bukan (nanya|menanyakan|tanya) harga|\bcatatan\b|\[context", re.I)


def kata_isi(s):
    ws = re.sub(r"[^\w\s]", " ", s.lower()).split()
    ws = [NORM.get(re.sub(r"(?<=[a-z])\d+$", "", w), re.sub(r"(?<=[a-z])\d+$", "", w)) for w in ws]
    return [w for w in ws if w and w not in SEPELE]


def kalimat(t):
    return [k for k in re.split(r"(?<=[.?!])\s+|\n+", t.strip()) if k.strip()]


def mirip(a, b):
    x, y = set(kata_isi(a)), set(kata_isi(b))
    sama = len(x & y)
    return sama >= 3 and sama / max(1, min(len(x), len(y))) >= 0.7


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
            "gema": gema, "promosi": promosi, "prospek_bertanya": tanya_prospek,
            "harga_tak_diminta": bool(HARGA_VIRA.search(balasan)) and not HARGA_DIMINTA.search(pesan),
            "catatan_bocor": bool(CATATAN_BOCOR.search(balasan))}


# ── simulasi satu percakapan ─────────────────────────────────────────────────
def simulasi(versi, katalog, pesan_list, no_wa, rekaman=None):
    """rekaman = keluaran model yang sudah pernah direkam (mode --putar-ulang): model tidak dipanggil."""
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
        pr = jalan(nodes, "Preprocess - Context Detection", {"Parse Config": [item(config=cfg())],
                                                             "Resolve User Row": [item(**resolve)]}, [item(**ld)])
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
        mentah = rekaman[len(giliran)] if rekaman is not None else model(msgs)
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
            "askingPrice": bool(pr.get("askingPrice")), "konteks_harga": "menanyakan harga" in teks,
            "ringkas": pa.get("ringkas", ""), "deck": bool(pa.get("deckNotify")),
            "talk": bool(pa.get("isTalkToAdmin")), "matikan": bool(pa.get("matikanBot")),
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
                                                 "%.0fs" % detik), flush=True)
        if stats["bot_mode"] == "OFF":
            break
    return {"giliran": giliran, "stats_akhir": {k: stats[k] for k in (
        "nama_lengkap", "nama_bisnis", "industri", "masalah_utama", "volume_chat", "deck_requested")}}


def katalog_live():
    import vira_sheet  # noqa: E402
    kat = {}
    for kunci, tab in (("faq", "FAQ"), ("program", "PROGRAM"), ("links", "LINKS"), ("about", "ABOUT_STEVEN")):
        _, baris = vira_sheet.baris_dict(tab)
        kat[kunci] = [{k: v for k, v in b.items() if k != "_baris"} for b in baris]
    return kat


VOL_DISEBUT = re.compile(r"(^|[^a-z\d])\d+\s*(an)?\s*(chat|pesan)|(sehari|per ?hari)[^.?!]{0,25}\d|\d+(an)?[^.?!]{0,25}(sehari|per ?hari)", re.I)
VOL_DITANYA = re.compile(r"berapa\s+(chat|pesan)|(chat|pesan)[^.?!]{0,25}berapa|berapa[^.?!]{0,25}(chat|pesan)", re.I)
# S2 sengaja tidak dihitung: "Dapur Nadia" dikirim di giliran yang skripnya belum tentu menanyakannya.
# S6: Rehan tidak pernah menyebut nama usaha -> yang benar KOSONG.
NAMA_USAHA_BENAR = {"S1": "humanizer", "S3": "Klinik Sehat Gigi", "S4": "Bimbel Cerdas Mandiri", "S5": "Kopi Senja", "S6": "",
                    "S7": "Laundry Kilat"}
NAMA_USAHA_SAH = ("humanizer", "dapur nadia", "klinik sehat gigi", "bimbel cerdas mandiri", "kopi senja", "laundry kilat")


def ringkas_versi(hasil):
    perk = [s["giliran"][0] for s in hasil]
    lanjut = [g for s in hasil for g in s["giliran"][1:]]
    galian = [g for g in lanjut if not g["m_kirim"]["prospek_bertanya"]]
    tanya_ulang_vol = kembar = kembar2 = 0
    for s in hasil:
        disebut = False
        riwayat = []
        for g in s["giliran"]:
            disebut = disebut or bool(VOL_DISEBUT.search(g["pesan"]))
            if disebut and VOL_DITANYA.search(g["kirim"]):
                tanya_ulang_vol += 1
            tanya = [k for k in kalimat(g["kirim"]) if "?" in k]
            lalu1 = riwayat[-1] if riwayat else []
            lalu2 = [t for r in riwayat[-2:] for t in r]
            if any(mirip(q, t) for q in tanya for t in lalu1):
                kembar += 1
            if any(mirip(q, t) for q in tanya for t in lalu2):
                kembar2 += 1
            riwayat.append(tanya)
    s6 = [s for s in hasil if s["judul"][:2] == "S6"]
    s7 = [s for s in hasil if s["judul"][:2] == "S7"]
    mati = [g for s in hasil for g in s["giliran"] if g.get("matikan")]
    return {
        "balasan (tanpa perkenalan)": len(lanjut),
        "median kata": statistics.median(g["m_kirim"]["kata"] for g in lanjut),
        "maks kata": max(g["m_kirim"]["kata"] for g in lanjut),
        "median kata saat prospek tidak bertanya": statistics.median(g["m_kirim"]["kata"] for g in galian),
        "membuka dengan merangkum (gema)": sum(g["m_kirim"]["gema"] for g in lanjut),
        "promosi VIRA tanpa ditanya": sum(g["m_kirim"]["promosi"] for g in lanjut),
        "HARGA VIRA disebut tanpa diminta": sum(g["m_kirim"]["harga_tak_diminta"] for g in lanjut),
        "catatan konteks dikutip ke prospek": sum(g["m_kirim"]["catatan_bocor"] for s in hasil for g in s["giliran"]),
        "konteks harga menyala": "%d (dari %d giliran)" % (sum(g["konteks_harga"] for s in hasil for g in s["giliran"]),
                                                           sum(len(s["giliran"]) for s in hasil)),
        "> 2 kalimat saat prospek tidak bertanya": sum(1 for g in galian if g["m_kirim"]["kalimat"] > 2),
        "> 1 pertanyaan dalam satu balasan": sum(1 for g in lanjut if g["m_kirim"]["tanya"] > 1),
        "jumlah chat ditanya padahal sudah disebut": tanya_ulang_vol,
        "pertanyaan kembar dengan balasan sebelumnya": kembar,
        "pertanyaan kembar dalam 2 balasan terakhir": kembar2,
        "perkenalan: median kata": statistics.median(g["m_kirim"]["kata"] for g in perk),
        "perkenalan: > 1 pertanyaan": sum(1 for g in perk if g["m_kirim"]["tanya"] > 1),
        "dipangkas jaring (RINGKAS/HARGA)": sum(1 for s in hasil for g in s["giliran"] if g["ringkas"]),
        "dipangkas karena harga": sum(1 for s in hasil for g in s["giliran"] if "harga" in g["ringkas"].split("+")),
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
                                      and s["stats_akhir"]["nama_bisnis"].lower() not in NAMA_USAHA_SAH),
        "S6 STATS (nama_bisnis | industri)": "; ".join("%s | %s" % (s["stats_akhir"]["nama_bisnis"] or "-",
                                                                   s["stats_akhir"]["industri"] or "-") for s in s6),
        "S7 'kpn bs ngmng sm steven?' -> bot dimatikan": "%d/%d" % (
            sum(1 for s in s7 if any(g.get("matikan") for g in s["giliran"])), len(s7)),
        "handover: balasan mengonfirmasi": "%d/%d" % (sum(1 for g in mati if re.search(
            r"sudah aku sambungkan|aku sambungkan ke steven|steven[^.?!]{0,40}\b(akan|bakal)\b[^.?!]{0,20}(menghubungi|hubungi)",
            g["kirim"], re.I)), len(mati)),
        "handover: balasan masih menawarkan 'sambungkan?'": sum(
            1 for g in mati if re.search(r"\bmau\b[^?]{0,40}sambung[^?]*\?", g["kirim"], re.I)),
    }


def tulis_md(hasil):
    L = ["# Hasil eval balasan VIRA v3.13 — model asli (%s)" % time.strftime("%Y-%m-%d %H:%M"), "",
         "DeepSeek `deepseek-v4-pro` asli, temperature 0.7, lewat workflow eval sementara. "
         "Kode node asli dari file workflow; katalog dari sheet live (baca saja). "
         "Pesan prospek sama persis untuk semua versi. Metrik dihitung dari teks yang TERKIRIM.", "",
         "## Ringkasan", "", "| Metrik | " + " | ".join(hasil) + " |", "|---|" + "---|" * len(hasil)]
    rv = {v: ringkas_versi(h) for v, h in hasil.items()}
    for k in rv[next(iter(rv))]:
        L.append("| %s | %s |" % (k, " | ".join(str(rv[v][k]) for v in hasil)))
    for versi, daftar in hasil.items():
        banyak = len({s["ulang"] for s in daftar}) > 1
        L += ["", "## %s" % versi]
        for s in daftar:
            L += ["", "### %s%s" % (s["judul"], " (ulang %d)" % s["ulang"] if banyak else ""), "",
                  "STATS akhir: " + ", ".join("%s=%s" % (k, v or "-") for k, v in s["stats_akhir"].items()), "",
                  "| # | Prospek | VIRA (terkirim) | kata | catatan |", "|---|---|---|---|---|"]
            for i, g in enumerate(s["giliran"], 1):
                cat = []
                if g["ringkas"]:
                    cat.append("dipangkas jaring: %s (model %d kata)" % (g["ringkas"], g["m_mentah"]["kata"]))
                if g["konteks_harga"]:
                    cat.append("konteks harga")
                if g["m_kirim"]["harga_tak_diminta"]:
                    cat.append("HARGA TANPA DIMINTA")
                if g["m_kirim"]["catatan_bocor"]:
                    cat.append("CATATAN BOCOR")
                if g["m_kirim"]["gema"]:
                    cat.append("GEMA")
                if g["m_kirim"]["promosi"]:
                    cat.append("PROMOSI")
                if g.get("matikan"):
                    cat.append("HANDOVER (bot OFF)")
                if g["deck"]:
                    cat.append("brief/deck")
                if g["galian"]:
                    cat.append("galian: " + g["galian"][:40])
                L.append("| %d | %s | %s | %d | %s |" % (i, g["pesan"].replace("\n", " / ").replace("|", "/"),
                                                         g["kirim"].replace("\n", " ").replace("|", "/"),
                                                         g["m_kirim"]["kata"], "; ".join(cat)))
    io.open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(hasil, io.open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nRINGKASAN")
    for v, r in rv.items():
        print(" ", v, json.dumps(r, ensure_ascii=False))
    print("tulis:", os.path.basename(OUT_MD))


def main():
    global V8
    ap = argparse.ArgumentParser()
    ap.add_argument("--versi")
    ap.add_argument("--ulang-ke", type=int, default=1)
    ap.add_argument("--json")
    ap.add_argument("--gabung", nargs="*")
    ap.add_argument("--putar-ulang", help="JSON gabungan: jalankan ulang keluaran model yang terekam lewat kode versi SEKARANG")
    a = ap.parse_args()
    if a.gabung:
        hasil = {}
        for pola in a.gabung:
            for p in sorted(glob.glob(pola)):
                for v, daftar in json.load(io.open(p, encoding="utf-8")).items():
                    hasil.setdefault(v, []).extend(daftar)
        hasil = {v: hasil[v] for v in sorted(hasil)}
        tulis_md(hasil)
        return
    V8 = MiniRacer()
    V8.eval(SHIM)
    kat = katalog_live()
    if a.putar_ulang:
        # Keluaran model yang sama diputar ulang lewat kode node versi SEKARANG: membuktikan perubahan
        # kode sesudah eval tidak mengubah balasan terkirim di luar yang disengaja.
        hasil = json.load(io.open(a.putar_ulang, encoding="utf-8"))
        beda = 0
        for versi, daftar in hasil.items():
            for s in daftar:
                pesan = [g["pesan"] for g in s["giliran"]]
                no = "62800000%02d%02d" % ([j for j, _ in SKENARIO].index(s["judul"]), s["ulang"])
                r = simulasi(versi, kat, pesan, no, rekaman=[g["mentah"] for g in s["giliran"]])
                for i, (g0, g1) in enumerate(zip(s["giliran"], r["giliran"]), 1):
                    if g0["kirim"] != g1["kirim"]:
                        beda += 1
                        print("BEDA %s %s u%d #%d\n  lama: %s\n  baru: %s" % (versi, s["judul"][:3], s["ulang"], i,
                                                                          g0["kirim"], g1["kirim"]))
                if len(r["giliran"]) != len(s["giliran"]) or r["stats_akhir"] != s["stats_akhir"]:
                    print("STATS/GILIRAN %s %s u%d: %s -> %s" % (versi, s["judul"][:3], s["ulang"], s["stats_akhir"], r["stats_akhir"]))
                s["giliran"], s["stats_akhir"] = r["giliran"], r["stats_akhir"]
        print("balasan terkirim yang berbeda:", beda)
        tulis_md(hasil)
        return
    print("katalog live: faq=%d program=%d links=%d about=%d" % tuple(len(kat[k]) for k in ("faq", "program", "links", "about")))
    daftar = []
    for i, (judul, pesan) in enumerate(SKENARIO):
        print("%s | %s | ulang %d" % (a.versi, judul, a.ulang_ke), flush=True)
        r = simulasi(a.versi, kat, pesan, "62800000%02d%02d" % (i, a.ulang_ke))
        r["judul"] = judul
        r["ulang"] = a.ulang_ke
        daftar.append(r)
    json.dump({a.versi: daftar}, io.open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("tulis:", a.json)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    os._exit(0)   # mesin V8 (MiniRacer) tidak menutup sendiri di Windows
