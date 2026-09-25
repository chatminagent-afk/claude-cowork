# -*- coding: utf-8 -*-
"""
_patch_2026-09-25.py - v3.14: "Brp" (tanya harga disingkat) tidak lagi dibaca sebagai nama,
dan jaring tanya-ulang tidak lagi menyisakan balasan yang cuma basa-basi.

Masukan : 2026-09-23-VIRA-Personal-Main-v3.13.json   (= live; output Process All live 25/09 memuat
          `hargaBukanTanya`, field yang hanya ada di v3.13; md5 209432822771f95633ddbd6941eef793)
Keluaran: 2026-09-25-VIRA-Personal-Main-v3.14.json
          2026-09-25-system-prompt-VIRA-Personal-v3.14.md

INSIDEN LIVE 2026-09-25 (prospek iklan IG "Reza", 6285199701359)
  12:12 VIRA  : "Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, ... Btw, boleh tau nama
                kakak siapa dan nama usahanya apa?"
  12:19 Reza  : "Brp"
  12:20 VIRA  : "Salam kenal kak."          (model: "Salam kenal kak. Nama usahanya apa ya?")
  Process All : askingPrice=false, slotTertangkap="nama_lengkap", nama_lengkap_merged="Brp",
                ringkas="tanya-ulang".
Rantai penyebab:
  1. Preprocess: "brp" hanya dikenali kalau menempel ke kata harga ("brp harganya"); pola cadangannya
     hanya "berapa" utuh. "Brp" polos -> askingPrice=false, konteks harga tidak disuntikkan.
  2. Prompt: "prospek menjawab dengan satu kata -> kata itu jawaban pertanyaanku" (dua tempat). Rakit
     Konteks sudah memberi "format_balasan: dia sedang BERTANYA", tapi aturan prompt yang menang:
     model menganggap "Brp" nama dan membuka dengan "Salam kenal kak".
  3. Penangkap: daftar kata-pertama yang bukan nama orang tidak memuat kata tanya (daftar nama usaha,
     BUKAN_NAMA_USAHA, sudah memuat berapa|brp) -> "Brp" tersimpan sebagai nama_lengkap di STATS.
     [FACTS nama] dari model juga tidak pernah diperiksa - kalau model menulis [FACTS nama="Brp"]
     hasilnya sama.
  4. Jaring tanya-ulang: "Nama usahanya apa ya?" mirip pertanyaan balasan sebelumnya -> dibuang.
     Pengaman "+galian" tidak jalan karena prospek bertanya (PROSPEK_BERTANYA) -> terkirim "Salam
     kenal kak." saja, balasan buntu.

ISI PATCH (tidak ada node baru, tidak ada koneksi berubah)
  A. Preprocess: TANYA_HARGA_POLOS - baris yang isinya cuma berapa/brp/brapa/brpa (+ kak/ya/sih/...)
     = tanya harga. Dicek per baris (debounce menggabung pesan dengan baris baru). Catatan konteksnya
     tegas ("dia menanyakan harga VIRA, bukan menjawab pertanyaanmu"); catatan "Sepertinya ... Periksa
     dulu" tetap untuk kata harga lain yang memang bisa ambigu (kasus Rehan).
  B. Prompt: dua aturan "satu kata = jawaban" dikecualikan untuk kata tanya.
  C. Penangkap (blok bersama, identik di Process All & Rakit Konteks): BUKAN_NAMA_ORANG = daftar lama
     + kata tanya (sama dengan PROSPEK_BERTANYA / BUKAN_NAMA_USAHA).
  D. Process All: [FACTS nama] yang semua katanya ada di BUKAN_NAMA_ORANG tidak disimpan.
  E. Process All: saat prospek BERTANYA, tanya-ulang tidak membuang pertanyaan kalau sisanya cuma
     basa-basi. Saat prospek menjawab, perilaku v3.13 tetap (pertanyaan yang sudah dijawab dibuang).
  Tidak diubah: BUKAN_JAWABAN (dipakai semua kolom - "berapa ya, 50an" tetap jawaban jumlah chat),
  desain pengaman "+galian" (tetap tidak menempel galian saat prospek bertanya).
"""
import io
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json")
DST = os.path.join(DIR, "2026-09-25-VIRA-Personal-Main-v3.14.json")
MD = os.path.join(DIR, "2026-09-25-system-prompt-VIRA-Personal-v3.14.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

NODES = {n["name"]: n for n in wf["nodes"]}


def ganti(teks, lama, baru, label):
    n = teks.count(lama)
    assert n == 1, "%s: pola ditemukan %d kali (harus 1)" % (label, n)
    return teks.replace(lama, baru)


# =========================================================================
# A. PREPROCESS - "brp" / "berapa" polos = tanya harga
# =========================================================================
pre_node = NODES["Preprocess - Context Detection"]["parameters"]
pre = pre_node["jsCode"]

pre = ganti(pre,
r"""const askingPrice = (TANYA_HARGA_KITA && !(JAWAB_PERTANYAANKU && !MENYEBUT_KITA))
""",
r"""// ── "BRP" POLOS (2026-09-25, v3.14) ──
// Live 2026-09-25 ("Reza", iklan IG): sesudah sapaan yang menanyakan nama + nama usaha, dia cuma
// menulis "Brp". Pola di atas hanya mengenali brp/berapa yang menempel ke kata harga, jadi konteks
// harga tidak menyala dan model menganggap "Brp" namanya. Baris yang isinya CUMA kata "berapa"
// (plus sapaan/partikel) tidak mungkin jawaban galian - itu pertanyaan harga. Dicek per baris karena
// debounce menggabung pesan dengan baris baru ("Reza\nbrp"). "brp lama setupnya" / "berapa ya, 50an"
// tidak kena (ada kata lain).
const TANYA_HARGA_POLOS = message.split('\n').some(b =>
  /^\W*(berapa|brp|brapa|brpa)(\s+(kak|ka|kakak|ya|yaa|sih|nih|dong|min|bang|mas|mbak|bu|pak|itu|ini|tuh))*\W*$/i.test(b.trim()));
const askingPrice = TANYA_HARGA_POLOS
  || (TANYA_HARGA_KITA && !(JAWAB_PERTANYAANKU && !MENYEBUT_KITA))
""", "PRE askingPrice")

# Catatan konteks untuk "brp" polos: TEGAS, bukan "Sepertinya ... Periksa dulu". Eval model asli v3.14
# putaran 1 (catatan lama + pengecualian prompt): 3 dari 4 balasan "Itu jawaban untuk pertanyaan namaku
# atau nanya harga?" - catatan yang ragu kalah oleh aturan "satu kata = jawaban" dan baris SYSTEM_DATA
# "pesan prospek adalah tanggapan atas kalimat itu".
pre = ganti(pre,
"""if (askingPrice) aiContext += 'Sepertinya dia menanyakan harga.""",
"""// v3.14: "brp"/"berapa" polos tidak ambigu - catatannya tegas. Dengan catatan "Sepertinya ... Periksa dulu"
// model (eval asli) 3 dari 4 kali membalas "Itu jawaban untuk pertanyaan namaku atau nanya harga?".
if (TANYA_HARGA_POLOS) aiContext += 'Pesannya singkatan dari "berapa harganya?": dia menanyakan harga VIRA - BUKAN menjawab pertanyaanmu dan bukan namanya. Langsung sebut kisaran dari DATA PRODUK lalu arahkan ke Steven untuk angka final. Jangan menawar, jangan memberi diskon. Catatan ini hanya untukmu: jangan dikutip, jangan dikomentari di balasan. ';
else if (askingPrice) aiContext += 'Sepertinya dia menanyakan harga.""", "PRE catatan harga polos")
pre_node["jsCode"] = pre


# =========================================================================
# B. PROMPT - "satu kata = jawaban" tidak berlaku untuk kata tanya
# =========================================================================
agent = NODES["AI Agent"]["parameters"]["options"]
sp = agent["systemMessage"]
sp = ganti(sp,
"""pertanyaan dan prospek menjawab dengan satu kata, kata itu adalah jawaban pertanyaanku.
""",
"""pertanyaan dan prospek menjawab dengan satu kata, kata itu adalah jawaban pertanyaanku —
kecuali kata tanya (“brp”, “berapa”, “knp”, “gmn”): itu pertanyaan dia, jawab dulu.
""", "PROMPT satu kata (BALASAN TERAKHIR)")
sp = ganti(sp,
"""  Satu kata atau nama yang tidak kukenal, dikirim tepat setelah aku menanyakan namanya, nama bisnis,
""",
"""  Satu kata atau nama yang tidak kukenal (bukan kata tanya seperti “brp”), dikirim tepat setelah aku menanyakan namanya, nama bisnis,
""", "PROMPT satu kata (FACTS)")
agent["systemMessage"] = sp


# =========================================================================
# C. PENANGKAP JAWABAN - blok bersama, identik di dua node
# =========================================================================
pa_node = NODES["Process All"]["parameters"]
rk_node = NODES["Rakit Konteks"]["parameters"]
pa = pa_node["jsCode"]
rk = rk_node["jsCode"]

MULAI = "// ── PENANGKAP JAWABAN — MULAI ──"
SELESAI = "// ── PENANGKAP JAWABAN — SELESAI ──"


def blok(s):
    assert s.count(MULAI) == 1 and s.count(SELESAI) == 1
    return s[s.index(MULAI):s.index(SELESAI)]


blok_lama = blok(pa)
assert blok_lama == blok(rk), "blok penangkap v3.13 tidak identik di dua node"
b = blok_lama

b = ganti(b,
r"""const EKOR = /[\s,]+(kak|ka|kakak|ya|yaa|sih|kok|deh|aja|saja)\s*$/i;
""",
r"""const EKOR = /[\s,]+(kak|ka|kakak|ya|yaa|sih|kok|deh|aja|saja)\s*$/i;
// Kata yang tidak mungkin nama orang. v3.14 (live 2026-09-25 "Reza"): + kata tanya - "Brp" sesudah
// "boleh tau nama kakak siapa dan nama usahanya apa?" tersimpan sebagai nama_lengkap. Kata tanyanya
// sama dengan PROSPEK_BERTANYA / BUKAN_NAMA_USAHA. Process All memakainya juga untuk [FACTS nama].
const BUKAN_NAMA_ORANG = /^(aku|saya|kak|kakak|mau|mo|tanya|harga|terima|makasih|thanks|thank|sama|ama|dengan|dgn|ini|itu|nama|lagi|lg|siapa|udah|sudah|bisa|oke|ok|iya|ya|bot|admin|berapa|brp|brapa|brpa|apa|apakah|gimana|gmn|bagaimana|kenapa|knp|kapan|kpn|mana|dimana)$/i;
""", "BLOK BUKAN_NAMA_ORANG")

b = ganti(b,
r"""    if (/^(aku|saya|kak|kakak|mau|mo|tanya|harga|terima|makasih|thanks|thank|sama|ama|dengan|dgn|ini|itu|nama|lagi|lg|siapa|udah|sudah|bisa|oke|ok|iya|ya|bot|admin)$/i.test(kata[0])) return '';
""",
r"""    if (BUKAN_NAMA_ORANG.test(kata[0])) return '';
""", "BLOK nama pakai BUKAN_NAMA_ORANG")

pa = pa.replace(blok_lama, b)
rk = rk.replace(blok_lama, b)
assert blok(pa) == blok(rk) == b


# =========================================================================
# D. PROCESS ALL - [FACTS nama] dari model diperiksa daftar yang sama
# =========================================================================
pa = ganti(pa,
r"""const slotDitanyaLalu = [...slotDitanya(prev.last_bot_reply)];
""",
r"""// ── Nama orang dari model yang bukan nama (2026-09-25, v3.14) ──
// Prompt: satu kata sesudah aku menanyakan nama = jawabannya. Kalau model tetap menulis
// [FACTS nama="Brp"], [FACTS] selalu menang dan "Brp" jadi nama di STATS & cover deck. Ditolak kalau
// SEMUA katanya ada di BUKAN_NAMA_ORANG ("Kak Rina" tetap lolos). Nilai lama di STATS tidak disentuh.
const kataNamaFacts = String(facts.nama_lengkap || '').replace(/[^\p{L}\s'.-]/gu, ' ').split(/\s+/).filter(Boolean);
if (!KOSONG(facts.nama_lengkap) && kataNamaFacts.length && kataNamaFacts.every(w => BUKAN_NAMA_ORANG.test(w))) {
  console.warn('[FACTS] nama "' + facts.nama_lengkap + '" bukan nama orang - tidak disimpan.');
  merged.nama_lengkap  = BERSIH(prev.nama_lengkap, PANJANG.nama_lengkap);
  changed.nama_lengkap = false;
  delete facts.nama_lengkap;   // penangkap di bawah boleh menilai jawabannya sendiri
}

const slotDitanyaLalu = [...slotDitanya(prev.last_bot_reply)];
""", "PA FACTS nama")


# =========================================================================
# E. PROCESS ALL - tanya-ulang tidak menyisakan basa-basi saja
# =========================================================================
pa = ganti(pa,
r"""  if (sisa.length && sisa.length < kal.length) {
    cleanOutput = sisa.join(' ');
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+tanya-ulang' : 'tanya-ulang';
""",
r"""  // v3.14 (live 2026-09-25 "Reza"): "Brp" dibalas "Salam kenal kak. Nama usahanya apa ya?"; pertanyaan
  // kembarnya dibuang dan pengaman +galian di bawah tidak jalan karena dia bertanya -> terkirim
  // "Salam kenal kak." saja: pertanyaannya tidak dijawab, percakapan buntu. Kalau dia BERTANYA dan yang
  // tersisa cuma basa-basi, pertanyaan kembarnya dibiarkan. Kalau dia MENJAWAB, tetap dibuang walau
  // sisanya "Noted kak." (desain v3.13: jangan menanyakan lagi yang sudah dijawab - uji Rehan & Nadia).
  const HANYA_BASA_BASI = /^(?:(?:salam kenal|halo|hai|hi|oke+|ok|okay|siap|baik|sip|noted|makasih|terima kasih|thanks|maaf|wah|nah|oh)\b[\s,]*(?:(?:kak|kakak|ka)\b)?[\s,.!]*)+$/i;
  const buntu = PROSPEK_BERTANYA && HANYA_BASA_BASI.test(sisa.join(' '));
  if (sisa.length && sisa.length < kal.length && !buntu) {
    cleanOutput = sisa.join(' ');
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+tanya-ulang' : 'tanya-ulang';
""", "PA tanya-ulang buntu")

pa_node["jsCode"] = pa
rk_node["jsCode"] = rk

assert wf["settings"]["errorWorkflow"] == "0mp_AdLtInm68RxQUwLqV", wf["settings"]["errorWorkflow"]

with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8") as f:
    f.write(sp[1:] if sp.startswith("=") else sp)

print("OK ->", os.path.basename(DST), "| node:", len(wf["nodes"]))
print("OK ->", os.path.basename(MD), "| prompt:", len(sp), "karakter")
