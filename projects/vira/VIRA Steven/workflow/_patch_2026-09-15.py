# -*- coding: utf-8 -*-
"""
_patch_2026-09-15.py - nama hanya disimpan (selalu "kak"), dan pertanyaan prospek dijawab dulu.

Masukan : 2026-09-14-VIRA-Personal-Main-v3.8.json   (tidak diubah; versi live)
Keluaran: 2026-09-15-VIRA-Personal-Main-v3.9.json
          2026-09-15-system-prompt-VIRA-Personal-v3.9.md

INSIDEN 2026-09-15 14:08-14:11 (nomor uji, v3.8 live)
  VIRA : ...Btw boleh tau namanya siapa kak?
  user : dengan aldi / mo ty ini bs apa aj / apa sm ky chatbot biasa?
  VIRA : Halo Aldi, senang kenal sama kamu. Jadi Aldi mau tanya soal AI customer service
         buat bisnis, usahanya di bidang apa kak?
  STATS: nama_lengkap = "Dengan Aldi"
Tiga cacat v3.8:
  1. VIRA memanggil nama. GAYA masih berbunyi "kecuali dia menyebutkan namanya - setelah
     itu pakai namanya", dan bagian NAMA v3.8 menyuruh "panggil dia dengan nama itu".
     KEPUTUSAN STEVEN: nama hanya disimpan untuk catatan, TIDAK dipakai menyapa. Selalu "kak".
  2. Penangkap jawaban tidak membuang kata "dengan" -> "Dengan Aldi".
  3. Pertanyaan prospek tidak dijawab: galian_berikutnya (bidang usaha) didahulukan.

ISI PATCH
  A. Prompt: GAYA, NAMA LAWAN BICARA, spek [FACTS] - nama tidak pernah dipakai di balasan;
     "kamu" di contoh perkenalan dan LARANGAN diganti "kakak".
  B. Process All:
     B1. penangkap nama membuang "dengan/sama/ini/..." di depan nama (2 baris diganti).
     B2. jaring terakhir: nama yang tersimpan dihapus dari balasan sebelum dikirim
         ("Halo Aldi" -> "Halo kak", "kak Aldi" -> "kak"). Nama yang juga bagian nama
         usaha, nama < 3 huruf, dan nama yang juga kata umum tidak disentuh.
  C. Rakit Konteks:
     C1. galian ditunda kalau pesan prospek giliran ini berisi pertanyaan (nama di
         pesan perkenalan tetap ditanyakan). Jendela giliran dilebarkan satu.
     C2. baris `panggilan: kak` di DATA PROSPEK begitu nama_lengkap ada.

Node yang diubah: AI Agent, Process All, Rakit Konteks. 86 node lain identik dengan v3.8.

Jalankan: python _patch_2026-09-15.py
"""
import io
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-14-VIRA-Personal-Main-v3.8.json")
DST = os.path.join(DIR, "2026-09-15-VIRA-Personal-Main-v3.9.json")
MD = os.path.join(DIR, "2026-09-15-system-prompt-VIRA-Personal-v3.9.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

NODES = {n["name"]: n for n in wf["nodes"]}


def ganti(teks, lama, baru, label):
    n = teks.count(lama)
    assert n == 1, "%s: pola ditemukan %d kali (harus 1)" % (label, n)
    return teks.replace(lama, baru)


# =========================================================================
# A. PROMPT
# =========================================================================
agent = NODES["AI Agent"]
sp0 = agent["parameters"]["options"]["systemMessage"]
assert sp0.startswith("=")
EKSPRESI = re.findall(r"\{\{[^}]+\}\}", sp0)
assert len(EKSPRESI) == 6

sp = ganti(sp0,
    "Panggil lawan bicara \"kak\", kecuali dia menyebutkan namanya — setelah itu pakai namanya.\n",
    "Panggil lawan bicara \"kak\" atau \"kakak\", bukan \"kamu\" — juga sesudah dia menyebutkan namanya.\n"
    "Namanya hanya dicatat untuk Steven dan TIDAK PERNAH dipakai di balasan: bukan \"halo Aldi\",\n"
    "bukan \"kak Aldi\", cukup \"kak\".\n",
    "A1-gaya")

sp = ganti(sp,
    "Begitu dia menyebut namanya — di pesan mana pun, ditanya atau tidak — catat lewat `[FACTS nama=\"...\"]`,\n"
    "panggil dia dengan nama itu, dan jangan pernah menanyakannya lagi.\n",
    "Begitu dia menyebut namanya — di pesan mana pun, ditanya atau tidak — catat lewat `[FACTS nama=\"...\"]`\n"
    "dan jangan pernah menanyakannya lagi. Nama itu catatan untuk Steven, BUKAN untuk menyapa: di balasan\n"
    "tetap panggil \"kak\", tanpa nama. Cukup \"salam kenal kak\", lalu jawab pertanyaannya.\n",
    "A2-nama")

sp = ganti(sp,
    "  `nama` adalah nama orangnya, bukan nama bisnisnya — pakai tag ini begitu dia menyebutkan namanya,\n"
    "  supaya aku bisa memanggilnya dengan nama itu di percakapan berikutnya.\n",
    "  `nama` adalah nama orangnya, bukan nama bisnisnya — pakai tag ini begitu dia menyebutkan namanya,\n"
    "  supaya Steven tahu sedang berhubungan dengan siapa. Nama itu tidak pernah dipakai di balasan.\n",
    "A3-facts")

sp = ganti(sp,
    "namanya VIRA. Jadi kalau kamu penasaran hasilnya kayak apa, kamu lagi ngobrol sama contohnya sekarang.\"\n",
    "namanya VIRA. Jadi kalau kakak penasaran hasilnya kayak apa, kakak lagi ngobrol sama contohnya sekarang.\"\n",
    "A4-perkenalan-kamu")

sp = ganti(sp,
    "juga yang akan kujaga kalau kamu jadi klien.\n",
    "juga yang akan kujaga kalau kakak jadi klien.\n",
    "A5-larangan-kamu")


# =========================================================================
# B. PROCESS ALL
# =========================================================================
pa_node = NODES["Process All"]
pa0 = pa_node["parameters"]["jsCode"]

pa = ganti(pa0,
    r"""      .replace(/^(nama\s*(ku|saya|aku|gue|gw)|namaku|aku|saya|gue|gw|panggil(\s+(aja|saja))?|biasa\s+dipanggil|dipanggil|kenalin)\s+/i, '')
""",
    r"""      .replace(/^(?:(?:nama\s*(?:ku|saya|aku|gue|gw)|namaku|aku|saya|gue|gw|ini|dengan|dgn|sama|ama|panggil(?:\s+(?:aja|saja))?|biasa\s+dipanggil|dipanggil|kenalin)\s+)+/i, '')
""",
    "B1a-awalan-nama")

pa = ganti(pa,
    r"""    if (/^(aku|saya|kak|kakak|mau|tanya|harga|terima|makasih|thanks|thank|sama|lagi|lg|siapa|udah|sudah|bisa|oke|ok|iya|ya|bot|admin)$/i.test(kata[0])) return '';
""",
    r"""    if (/^(aku|saya|kak|kakak|mau|mo|tanya|harga|terima|makasih|thanks|thank|sama|ama|dengan|dgn|ini|itu|nama|lagi|lg|siapa|udah|sudah|bisa|oke|ok|iya|ya|bot|admin)$/i.test(kata[0])) return '';
""",
    "B1b-stop-nama")

B2_LAMA = "\nreturn [{\n  json: {\n    ...chatCounter, ...preprocess, ...item.json,\n"
B2_BARU = r"""
// ── NAMA TIDAK DIPAKAI MENYAPA (2026-09-15) ──
// Keputusan Steven: nama prospek hanya disimpan untuk catatan, tidak pernah dipakai
// di balasan - selalu "kak". Larangan di prompt saja terbukti tidak cukup (insiden
// 2026-09-15 14:11: "Halo Aldi, senang kenal sama kamu. Jadi Aldi mau tanya...").
// Jaring terakhir: nama yang tersimpan dihapus dari teks sebelum dikirim.
// Tidak disentuh: nama yang juga bagian nama usaha ("Andi" di "Andi Bakery"),
// nama di bawah 3 huruf, dan nama yang juga kata umum di balasan ("Indah", "Jaya").
const KATA_UMUM_NAMA = /^(indah|sari|bintang|cahaya|mulia|jaya|baik|berkah|tenang|damai|harapan|kasih|cinta|suci|murni|maju|sukses|abadi|bagus|pintar|cerdas|setia|aman|lancar|ramah|senang|bahagia|tulus|rajin|hebat|vira|steven)$/i;
const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const namaSimpan = String(merged.nama_lengkap || '').trim();
const bisnisSimpan = String(merged.nama_bisnis || '').toLowerCase();
let namaDihapus = false;
if (namaSimpan) {
  const potongan = [...new Set([namaSimpan, ...namaSimpan.split(/\s+/)])]
    .filter(n => n.length >= 3 && !KATA_UMUM_NAMA.test(n) && !bisnisSimpan.includes(n.toLowerCase()))
    .sort((a, b) => b.length - a.length);
  for (const n of potongan) {
    const pola = escRe(n);
    const sebelum = cleanOutput;
    cleanOutput = cleanOutput
      .replace(new RegExp('\\b(kak|kakak|ka|mas|mbak|pak|bu|bapak|ibu|bang|sis|bro)\\s+' + pola + '\\b', 'gi'), '$1')
      .replace(new RegExp('\\b(halo|hai|hi|hallo|makasih|terima kasih|thanks|thank you|salam kenal|selamat datang|oke|siap|baik|nah|wah)(\\s*,?\\s+)' + pola + '\\b', 'gi'), '$1$2kak')
      .replace(new RegExp('\\b' + pola + '\\b', 'gi'), 'kakak');
    if (cleanOutput !== sebelum) namaDihapus = true;
  }
  if (namaDihapus) {
    cleanOutput = cleanOutput
      .replace(/\bkakak\s+kak\b/gi, 'kak').replace(/\bkak\s+kakak\b/gi, 'kak')
      .replace(/(^|\n)([a-z])/g, (m, p1, p2) => p1 + p2.toUpperCase());
    console.warn('Nama prospek dihapus dari balasan (aturan: selalu "kak").');
  }
}

return [{
  json: {
    ...chatCounter, ...preprocess, ...item.json,
"""
pa = ganti(pa, B2_LAMA, B2_BARU, "B2-hapus-nama")

pa = ganti(pa,
    "    slotTertangkap,\n",
    "    slotTertangkap,\n    namaDihapus,\n",
    "B3-keluaran")
pa_node["parameters"]["jsCode"] = pa


# =========================================================================
# C. RAKIT KONTEKS
# =========================================================================
rk = NODES["Rakit Konteks"]
rk0 = rk["parameters"]["jsCode"]

rk1 = ganti(rk0,
    "const ditanyaLalu = slotDitanya(stats['last_bot_reply']);\n",
    "const ditanyaLalu = slotDitanya(stats['last_bot_reply']);\n"
    "// Pesan prospek giliran ini (2026-09-15). Kalau dia sedang BERTANYA, galian ditunda\n"
    "// supaya pertanyaannya dijawab dulu - insiden 2026-09-15 14:11: prospek bertanya\n"
    "// \"bisa apa aja, sama kayak chatbot biasa?\", VIRA tidak menjawab dan langsung\n"
    "// menanyakan bidang usaha. Nama di pesan perkenalan tetap ditanyakan.\n"
    "// Jendela giliran dilebarkan satu supaya galian yang tertunda masih kebagian.\n"
    "let pesanProspek = '';\n"
    "try { pesanProspek = String($('Preprocess - Context Detection').first().json.actualUserMessage || ''); }\n"
    "catch (e) { pesanProspek = ''; }\n"
    "const pesanBertanya = /\\?|\\b(apa|apakah|gimana|gmn|bagaimana|berapa|brp|kenapa|knp|kapan|mana)\\b/i.test(pesanProspek);\n",
    "C1a-pesan-bertanya")

rk1 = ganti(rk1,
    "    boleh: () => !pesanPerkenalan && giliran >= 2 && giliran <= 4 },\n",
    "    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 5 },\n",
    "C1b-industri")
rk1 = ganti(rk1,
    "    boleh: () => !pesanPerkenalan && giliran >= 2 && giliran <= 6 && (!!txt(stats['industri']) || giliran > 4) },\n",
    "    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 7 && (!!txt(stats['industri']) || giliran > 5) },\n",
    "C1c-masalah")
rk1 = ganti(rk1,
    "    boleh: () => !pesanPerkenalan && giliran >= 3 && giliran <= 8 && !!txt(stats['masalah_utama']) },\n",
    "    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 3 && giliran <= 9 && !!txt(stats['masalah_utama']) },\n",
    "C1d-volume")

rk1 = ganti(rk1,
    "if (galian) barisProspek.push(`galian_berikutnya: ${galian.teks}`);\n",
    "if (galian) barisProspek.push(`galian_berikutnya: ${galian.teks}`);\n"
    "// Nama hanya catatan untuk Steven (keputusan Steven 2026-09-15) - selalu \"kak\".\n"
    "if (txt(stats['nama_lengkap'])) {\n"
    "  barisProspek.push('panggilan: kak — nama_lengkap hanya catatan untuk Steven, JANGAN dipakai di balasan');\n"
    "}\n",
    "C2-panggilan")
rk["parameters"]["jsCode"] = rk1


# =========================================================================
# PEMERIKSAAN AKHIR
# =========================================================================
assert sp.startswith("=") and re.findall(r"\{\{[^}]+\}\}", sp) == EKSPRESI
assert "setelah itu pakai namanya" not in sp and "panggil dia dengan nama itu" not in sp
assert "memanggilnya dengan nama itu" not in sp
assert not re.findall(r'(?<!")\bkamu\b(?!")', sp), "masih ada 'kamu' di luar kutipan"
assert "kalau boleh tau nama usahanya apa ya kak?." in sp
assert pa.count("replyOverridden = true") == pa0.count("replyOverridden = true")
assert pa.count("\nreturn [{") == 1 and len(wf["nodes"]) == 89

agent["parameters"]["options"]["systemMessage"] = sp

with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
    f.write(sp[1:])

print("DST    : %s" % os.path.basename(DST))
print("MD     : %s" % os.path.basename(MD))
print("prompt : %d -> %d | PA: %d -> %d | RK: %d -> %d"
      % (len(sp0), len(sp), len(pa0), len(pa), len(rk0), len(rk1)))
print("node   : %d (diubah 3: AI Agent, Process All, Rakit Konteks)" % len(wf["nodes"]))
