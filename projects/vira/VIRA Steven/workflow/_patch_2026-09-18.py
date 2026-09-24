# -*- coding: utf-8 -*-
"""
_patch_2026-09-18.py - nama usaha ditanya di perkenalan, dan balasan lebih ringkas.

Masukan : VIRA Personal — Main.json                      (export live 2026-09-16 = v3.9; tidak diubah)
Keluaran: 2026-09-18-VIRA-Personal-Main-v3.10.json
          2026-09-18-system-prompt-VIRA-Personal-v3.10.md

UJI STEVEN 2026-09-17 19:46-19:50 (nomor sendiri, berperan "Nadia", katering)
  VIRA : ...Boleh cerita dulu bisnis kakak di bidang apa, dan apa yang bikin kakak tertarik
         cari AI customer service? Btw, boleh tau namanya siapa kak?
  user : Nadia kak, bisnis aku katering, chat suka numpuk pas malem
  VIRA : Salam kenal Nadia. Chat katering memang paling ramai pas malam hari, apalagi ...
  ... (4 giliran galian, tiap balasan membuka dengan mengulang jawaban prospek)
  VIRA : ...Mau aku mintakan Steven buatkan deck khusus buat bisnis katering kakak?
  user : mau dong / thankyou
  VIRA : Siap, sudah aku teruskan ke Steven. ... nama usaha kateringnya apa kak?
  REQUESTS.nama_bisnis kosong -> deck terkirim sebagai "tanpa-nama.pdf" (EVENTS 19:58:27).
Cacat:
  1. Nama usaha sengaja tidak digali (Rakit Konteks: "ditanyakan di kalimat tawaran deck"),
     dan model juga lupa menanyakannya di kalimat tawaran -> baru ditanya sesudah deck disetujui.
  2. Perkenalan menanyakan 3 hal (bidang, alasan tertarik, nama). Detektor membaca 2 slot,
     penangkap deterministik hanya jalan untuk 1 slot -> nama tidak tersimpan giliran itu ->
     jaring penghapus nama tidak punya nama untuk dihapus -> "Salam kenal Nadia".
  3. Balasan bertele-tele: membuka dengan merangkum jawaban prospek lalu menjelaskan balik.

KEPUTUSAN STEVEN 2026-09-18
  - Pesan 1: nama DAN nama usaha. Pesan 2: bidang usaha + boleh cerita. Sisanya mundur satu.
  - Kalau nama usaha belum dijawab di pesan 1: tanya ulang sekali di pesan 2, bidang mundur ke 3.
  - "Apa yang bikin tertarik cari AI CS" dibuang.
  - Balasan lebih ringkas, tapi tidak sependek VIRA TS (TS: default 1 kalimat, maks 2).

ISI PATCH
  A. Prompt: ALUR 3/7/10, PERKENALAN, NAMA LAWAN BICARA, GAYA (panjang + larangan mengulang),
     MENGGALI (contoh galian + TINGKAT 1), spek [FACTS].
  B. Detektor galian (Process All & Rakit Konteks, identik): pertanyaan nama orang dinilai
     juga per klausa, supaya "nama kakak siapa, dan nama usahanya apa?" terbaca dua slot.
  C. Process All:
     C1. penangkap jawaban perkenalan: nama + nama usaha (+ jenis usaha -> industri).
     C2. jaring nama: nama yang disebut di pesan ini tapi belum tersimpan ikut dihapus
         sesudah sapaan/panggilan ("Salam kenal Nadia" -> "Salam kenal kak").
  D. Rakit Konteks: urutan galian baru + jendela giliran dilebarkan satu.

Node yang diubah: AI Agent, Process All, Rakit Konteks. 86 node lain identik dengan export live.

Jalankan: python _patch_2026-09-18.py
"""
import io
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "VIRA Personal — Main.json")
DST = os.path.join(DIR, "2026-09-18-VIRA-Personal-Main-v3.10.json")
MD = os.path.join(DIR, "2026-09-18-system-prompt-VIRA-Personal-v3.10.md")

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
    "   Pesan perkenalan itu juga menanyakan namanya (lihat NAMA LAWAN BICARA).\n",
    "   Pesan perkenalan itu juga menanyakan namanya dan nama usahanya, dalam satu kalimat\n"
    "   (lihat NAMA LAWAN BICARA).\n",
    "A1-alur3")

sp = ganti(sp,
    "   Nama, bidang usaha, masalah utama, dan jumlah chat per hari hanya kutanyakan lewat baris itu.\n",
    "   Nama, nama usaha, bidang usaha, masalah utama, dan jumlah chat per hari hanya kutanyakan lewat baris itu.\n",
    "A2-alur7")

sp = ganti(sp,
    "10. Sebelum mengirim: hitung kalimat yang DIBACA PROSPEK saja (lihat GAYA). TAG tidak pernah\n"
    "    ikut dihitung dan tidak pernah dipotong, walau balasannya cuma satu kalimat.\n",
    "10. Sebelum mengirim: buang kalimat yang cuma mengulang atau merangkum ucapannya (lihat GAYA),\n"
    "    lalu hitung kalimat yang DIBACA PROSPEK saja. TAG tidak pernah ikut dihitung dan tidak pernah\n"
    "    dipotong, walau balasannya cuma satu kalimat.\n",
    "A3-alur10")

sp = ganti(sp,
    "Lalu langsung jawab pertanyaannya, dan tutup dengan menanyakan namanya dalam satu kalimat pendek,\n"
    "misalnya \"btw boleh tau namanya siapa kak?\". Pesan perkenalan ini satu-satunya pengecualian batas\n"
    "3 kalimat: perkenalan seperti di atas, jawaban singkat kalau dia bertanya, lalu pertanyaan nama.\n"
    "Kalau dia belum bertanya apa-apa, cukup perkenalan lalu tanyakan namanya; apa yang bikin dia tertarik\n"
    "kutanyakan sesudah dia menjawab. Kalau dia sudah menyebut namanya di pesan pertama, jangan ditanyakan.\n",
    "Lalu langsung jawab pertanyaannya, dan tutup dengan SATU kalimat pendek yang menanyakan namanya\n"
    "sekaligus nama usahanya, misalnya \"btw boleh tau nama kakak siapa, dan nama usahanya apa?\".\n"
    "Pesan perkenalan ini satu-satunya pengecualian batas 3 kalimat: perkenalan seperti di atas, jawaban\n"
    "singkat kalau dia bertanya, lalu pertanyaan nama dan nama usaha.\n"
    "Kalau dia belum bertanya apa-apa, cukup perkenalan lalu pertanyaan itu. Selain nama dan nama usaha,\n"
    "JANGAN menanyakan apa pun di pesan ini — bukan bidang usahanya, bukan masalahnya, bukan kenapa dia\n"
    "tertarik. Semua itu menyusul satu per satu lewat `galian_berikutnya`.\n"
    "Kalau dia sudah menyebut namanya atau nama usahanya di pesan pertama, tanyakan yang belum saja.\n",
    "A4-perkenalan")

sp = ganti(sp,
    "Aku ingin tahu sedang bicara dengan siapa, dan Steven juga — namanya ikut masuk ke setiap catatan\n"
    "yang kuteruskan ke dia. Namanya kutanyakan SEKALI, di pesan perkenalan. Kalau dia tidak menjawab\n"
    "atau mengalihkan, jangan ditanyakan lagi — panggil \"kak\" saja.\n"
    "\n"
    "Tanyakan dalam satu kalimat pendek yang ringan dan selalu pakai kata \"siapa\", misalnya\n"
    "\"btw boleh tau namanya siapa kak?\". Jangan digabung dengan pertanyaan nama usaha di balasan yang\n"
    "sama — jawaban satu kata jadi tidak bisa kubedakan nama orang atau nama usahanya.\n",
    "Aku ingin tahu sedang bicara dengan siapa dan usahanya apa, dan Steven juga — namanya ikut masuk\n"
    "ke setiap catatan yang kuteruskan ke dia, dan nama usahanya jadi judul di cover decknya. Keduanya\n"
    "kutanyakan bersamaan, di pesan perkenalan. Namanya kutanyakan SEKALI: kalau dia tidak menjawab\n"
    "atau mengalihkan, jangan ditanyakan lagi — panggil \"kak\" saja. Nama usahanya boleh kutanyakan\n"
    "ulang satu kali, hanya kalau `galian_berikutnya` memintanya dan dia memang belum menyebutnya.\n"
    "\n"
    "Tanyakan dalam SATU kalimat pendek yang ringan: nama orang dengan kata \"siapa\", nama usaha dengan\n"
    "kata \"apa\", misalnya \"btw boleh tau nama kakak siapa, dan nama usahanya apa?\". Jangan dipecah\n"
    "jadi dua kalimat tanya, dan jangan ditambah pertanyaan lain.\n"
    "\n"
    "Cara membaca jawabannya: bagian yang menyebut dirinya (\"aku Rina\", \"Rina kak\") adalah `nama`;\n"
    "bagian yang menyebut usahanya (\"usahaku Dapur Mama\", \"dari Dapur Mama\", atau bagian sesudah koma)\n"
    "adalah `nama_bisnis`. Kalau yang dia sebut ternyata jenis usahanya, bukan namanya (\"katering\",\n"
    "\"jualan skincare\"), itu `industri` — nama usahanya berarti belum dia sebut. Kalau dia cuma menjawab\n"
    "satu nama, anggap itu namanya.\n",
    "A5-nama")

sp = ganti(sp,
    "Maksimal 3 kalimat per balasan. Ini batas keras, bukan target rata-rata.\n"
    "Boleh sampai 5 kalimat HANYA kalau dia eksplisit minta dijelaskan detail atau membandingkan paket.\n"
    "Kalau jawaban dan pertanyaan galian tidak muat dalam 3 kalimat, buang pertanyaan galiannya —\n"
    "tanya di giliran berikutnya. Menjawab pendek lebih penting daripada menggali.\n",
    "Panjang yang kuincar: DUA kalimat, kira-kira 20 sampai 35 kata — satu yang menanggapi, satu yang\n"
    "bertanya atau memajukan obrolan. Satu kalimat juga boleh kalau memang cukup. Maksimal 3 kalimat;\n"
    "itu batas keras, bukan target. Boleh sampai 5 kalimat HANYA kalau dia eksplisit minta dijelaskan\n"
    "detail atau membandingkan paket. Kalau jawaban dan pertanyaan galian tidak muat, buang pertanyaan\n"
    "galiannya — tanya di giliran berikutnya. Menjawab pendek lebih penting daripada menggali.\n"
    "\n"
    "JANGAN MENGULANG UCAPANNYA. Dia tahu apa yang barusan dia tulis. Jangan membuka dengan merangkum\n"
    "atau memparafrasekan jawabannya (\"Jadi alurnya ada dua...\", \"Berarti kebutuhannya...\", \"Paham,\n"
    "berarti...\", \"Nah itu dua pertanyaan yang...\"), dan jangan menjelaskan balik keadaan yang dia\n"
    "alami sendiri (\"chat katering memang paling ramai pas malam, apalagi kalau...\"). Kalimat tanggapan\n"
    "harus MENAMBAH sesuatu yang belum dia sebut — satu hal dari sisi VIRA, atau akibat yang belum dia\n"
    "lihat — atau cukup pengakuan singkat beberapa kata. Kalau tidak ada yang bisa ditambah, langsung\n"
    "ke pertanyaannya.\n"
    "\n"
    "Contoh. Dia: \"betul, tanya2 dl klo sdh fix lsg order juga kdg\"\n"
    "Terlalu panjang, mengulang ucapannya lalu menjelaskan: \"Jadi alurnya ada dua: yang tanya-tanya dulu\n"
    "sampai yakin, dan yang langsung order begitu tahu harganya. Itu justru bagus buat AI, karena yang\n"
    "tanya-tanya bisa dijawab otomatis tanpa nunggu kakak online, dan yang siap order bisa langsung\n"
    "diarahkan.\"\n"
    "Pas: \"Dua-duanya bisa dipegang AI kak, yang masih tanya dijawab otomatis dan yang siap order\n"
    "langsung diarahkan.\"\n"
    "Contoh lain yang pas. Dia: \"sekitar 20-30 chat biasanya sih\" — \"Lumayan buat dibalas sendiri\n"
    "sambil ngurus pesanan. Dari chat pertama sampai jadi pesan, biasanya lewat langkah apa aja kak?\"\n",
    "A6-gaya-ringkas")

sp = ganti(sp,
    "kususun sendiri: satu kalimat, ringan, diakhiri tanda tanya. Contoh untuk bidang usaha: \"usahanya di\n"
    "bidang apa kak?\"; untuk masalah:",
    "kususun sendiri: satu kalimat, ringan, diakhiri tanda tanya. Contoh untuk nama usaha yang ditanya\n"
    "ulang: \"oh iya, nama usahanya apa kak?\"; untuk bidang usaha: \"usahanya bergerak di bidang apa kak,\n"
    "boleh cerita sedikit?\"; untuk masalah:",
    "A7-contoh-galian")

sp = ganti(sp,
    "Nama usahanya tidak — itu yang pasti harus kutanyakan sengaja, dan tanpa itu cover\n"
    "decknya jadi generik. Momen paling wajar: saat menawarkan decknya, karena memang di situ\n"
    "namanya dipakai. Contoh: \"biar Steven tulis di decknya, usahanya namanya apa kak?\"\n",
    "Nama usahanya tidak — itu yang pasti harus kutanyakan sengaja, dan tanpa itu cover\n"
    "decknya jadi generik. Karena itu nama usahanya kutanyakan di pesan perkenalan bersama\n"
    "namanya, lalu sekali lagi lewat `galian_berikutnya` kalau belum dia jawab. Kalau sampai\n"
    "menawarkan deck masih kosong juga, tanyakan di kalimat tawarannya (lihat `[DECK_REQUEST]`).\n",
    "A8-tingkat1")

sp = ganti(sp,
    "  menanyakan namanya → `nama`; nama usahanya → `nama_bisnis`; bidang usahanya → `industri`.\n",
    "  menanyakan namanya → `nama`; nama usahanya → `nama_bisnis`; bidang usahanya → `industri`;\n"
    "  nama dan nama usahanya sekaligus → dua-duanya, dibaca seperti di NAMA LAWAN BICARA.\n",
    "A9-facts")


# =========================================================================
# B. DETEKTOR GALIAN — identik di Process All dan Rakit Konteks
# =========================================================================
def detektor_baru(kode, label):
    awal = "    const namaMilikLain =\n"
    akhir = "hasil.add('nama_lengkap');\n"
    assert kode.count(awal) == 1, label
    i = kode.index(awal)
    j = kode.index(akhir, i) + len(akhir)
    lama = kode[i:j]
    b = lama.split("\n")
    assert b[3] == "    if (namaUsaha) hasil.add('nama_bisnis');" and b[4] == "    if (!namaMilikLain && (", b
    assert len(b) == 12 and b[10].endswith(".test(k))) hasil.add('nama_lengkap');") and b[11] == "", b
    milik = [x.replace(".test(k)", ".test(s)") for x in b[1:3]]
    orang = [x.replace(".test(k)", ".test(s)") for x in b[5:10]]
    orang.append(b[10].replace(".test(k))) hasil.add('nama_lengkap');", ".test(s));"))
    baru = "\n".join(
        ["    // Nama orang dinilai per kalimat DAN per klausa (2026-09-18): \"nama kakak siapa, dan",
         "    // nama usahanya apa?\" menanyakan dua hal - \"nama usaha\" di klausa lain tidak boleh",
         "    // menggugurkan pertanyaan nama orangnya.",
         "    const namaMilikLain = (s) =>"] + milik
        + ["    const tanyaNamaOrang = (s) => !namaMilikLain(s) && ("] + orang
        + ["    if (namaUsaha) hasil.add('nama_bisnis');",
           "    if (tanyaNamaOrang(k) || k.split(/[,;]|\\s(?:dan|serta)\\s/).some(tanyaNamaOrang)) hasil.add('nama_lengkap');",
           ""])
    assert ".test(k)" not in "\n".join(milik + orang)
    return kode[:i] + baru + kode[j:]


# =========================================================================
# C. PROCESS ALL
# =========================================================================
pa_node = NODES["Process All"]
pa0 = pa_node["parameters"]["jsCode"]
pa = detektor_baru(pa0, "PA-detektor")

C1_LAMA = (
    "      console.log('Jawaban galian ditangkap tanpa [FACTS]: ' + kolomLalu + ' = ' + merged[kolomLalu]);\n"
    "    }\n"
    "  }\n"
    "}\n")
C1_BARU = C1_LAMA + r"""
// ── JAWABAN PERKENALAN: nama DAN nama usaha sekaligus (2026-09-18) ──
// Keputusan Steven: nama usaha ditanya di pesan perkenalan bersama nama orangnya
// ("btw boleh tau nama kakak siapa, dan nama usahanya apa?"). Jawabannya dipecah di
// koma / titik / baris baru / " - " / "dari" / "usahaku" dst. Bagian yang menyebut diri
// = nama, bagian yang menyebut usaha = nama usaha, bagian tanpa penanda diisi berurutan
// (nama dulu). Jenis usaha ("katering") BUKAN nama usaha - masuk industri, supaya nama
// usahanya ditanya ulang di pesan berikutnya. Hanya mengisi kolom yang masih kosong.
// Uji 2026-09-17: "Nadia kak, bisnis aku katering, chat suka numpuk pas malem"
//   -> nama_lengkap = Nadia, industri = katering, nama_bisnis tetap kosong.
const JENIS_USAHA = /^((usaha|bisnis|jualan|jual|di\s+bidang|bidang)\s+)?(katering|catering|kuliner|makanan|minuman|kue|bakery|kafe|cafe|coffee shop|resto|restoran|warung|fashion|baju|pakaian|hijab|skincare|kosmetik|kecantikan|salon|barbershop|laundry|properti|kontraktor|konsultan|kursus|les|bimbel|edukasi|pendidikan|sekolah|klinik|apotek|travel|tour|jasa|toko online|online shop|olshop|reseller|dropship)(\s+(rumahan|online|lokal|kecil|harian|sehat|anak|muslim|wanita|pria|kiloan|premium|kekinian))?$/i;
const BUKAN_NAMA_USAHA = /\?|\b(tanya|nanya|ty|tny|harga|harganya|berapa|brp|gimana|gmn|bagaimana|apa|apakah|bisa|bs|boleh|minta|tolong|ini|itu|aja|aj|yang|yg|suka|sering|biasanya|kalau|kalo|klo|soalnya|karena|chat|pesan|numpuk|rame|ramai|banget|sih|dong)\b|^(mau|mo|lagi|lg|udah|sudah|belum|blm|gak|ga|nggak|enggak|masih|rahasia|nanti|ntar)\b/i;
const PENANDA_DIRI = /^(nama\s*(ku|saya|aku|gue|gw)|namaku|aku|saya|gue|gw|panggil)\b/i;
const PENANDA_USAHA = /^(dari|owner|pemilik|founder|punya|(nama\s+)?(usaha|bisnis|toko|brand|olshop|perusahaan)(ku|nya|kami)?)\b/i;
// "aku Rina dari Dapur Mama" -> "aku Rina" | "dari Dapur Mama": dipecah sekali, di penanda
// pertama. Bagian yang sudah diawali penanda usaha tidak dipecah lagi ("dari Toko X").
const pecahDiPenanda = (s) => {
  if (PENANDA_USAHA.test(s)) return [s];
  const m = s.match(/^(.+?)\s((?:dari|owner|pemilik|founder|punya|(?:nama\s+)?(?:usaha|bisnis|toko|brand|olshop)(?:ku|nya)?)\s.+)$/i);
  return m ? [m[1], m[2]] : [s];
};
const ambilNamaDanUsaha = (pesan) => {
  const hasil = {};
  const bagian = String(pesan || '').trim().replace(LEPAS_AWAL, '')
    .split(/\n|[,;]|\.\s+|\s+-\s+/).map(s => s.trim()).filter(Boolean)
    .flatMap(pecahDiPenanda).map(s => s.trim()).filter(Boolean).slice(0, 4);
  const diri  = bagian.filter(s => PENANDA_DIRI.test(s));
  const usaha = bagian.filter(s => !PENANDA_DIRI.test(s) && PENANDA_USAHA.test(s));
  const polos = bagian.filter(s => !PENANDA_DIRI.test(s) && !PENANDA_USAHA.test(s));
  const calonNama = diri[0] || polos.shift() || '';
  const nama = calonNama ? ambilJawaban('nama_lengkap', calonNama) : '';
  if (nama) hasil.nama_lengkap = nama;
  const calonUsaha = [...usaha.map(s => [s, 6]), ...polos.slice(0, 2).map(s => [s, 4])];
  for (const [s, maksKata] of calonUsaha) {
    const lewatDari = /^dari\s/i.test(s);
    const bersih = s.replace(/^(dari|owner|pemilik|founder|punya)\s+/i, '')
      .replace(/^((?:nama\s+)?(?:usaha|bisnis|toko|brand|olshop|perusahaan)(?:ku|nya|kami)?)\s+(?:aku|saya|gue|gw|kami)\s+/i, '$1 ');
    if (BUKAN_NAMA_USAHA.test(bersih)) continue;
    const isi = ambilJawaban('nama_bisnis', bersih);
    if (!isi || isi.split(' ').length > maksKata || /^(kak|kakak|ka|nya)$/i.test(isi)) continue;
    if (JENIS_USAHA.test(isi)) { if (!hasil.industri) hasil.industri = isi; continue; }
    if (lewatDari && isi.split(' ').length === 1) continue;   // "dari Surabaya": lebih mungkin kota
    if (!hasil.nama_bisnis) hasil.nama_bisnis = isi;
  }
  return hasil;
};
if (slotDitanyaLalu.includes('nama_lengkap') && slotDitanyaLalu.includes('nama_bisnis')) {
  const dapat = ambilNamaDanUsaha((preprocess && preprocess.actualUserMessage) || originalMessage);
  const tertangkap = [];
  for (const [kolom, nilai] of Object.entries(dapat)) {
    if (!KOSONG(facts[kolom]) || merged[kolom]) continue;
    merged[kolom]  = BERSIH(nilai, PANJANG[kolom] || 120);
    changed[kolom] = true;
    tertangkap.push(kolom);
  }
  if (tertangkap.length) {
    slotTertangkap = tertangkap.join(',');
    console.log('Jawaban perkenalan ditangkap tanpa [FACTS]: ' + tertangkap.map(k => k + ' = ' + merged[k]).join(', '));
  }
}
"""
pa = ganti(pa, C1_LAMA, C1_BARU, "C1-perkenalan")

C2_LAMA = r"""let namaDihapus = false;
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
"""
C2_BARU = r"""// Nama yang disebut di pesan ini tapi TIDAK tersimpan (uji 2026-09-17: perkenalan
// menanyakan bidang usaha + nama, model tidak menulis [FACTS], lalu "Salam kenal Nadia"
// terkirim). Belum pasti nama, jadi hanya dihapus sesudah sapaan/panggilan.
const namaTebakan = (!namaSimpan && slotDitanyaLalu.includes('nama_lengkap'))
  ? ambilJawaban('nama_lengkap', (preprocess && preprocess.actualUserMessage) || originalMessage) : '';
let namaDihapus = false;
for (const [nama, dimanaSaja] of [[namaSimpan, true], [namaTebakan, false]]) {
  if (!nama) continue;
  const potongan = [...new Set([nama, ...nama.split(/\s+/)])]
    .filter(n => n.length >= 3 && !KATA_UMUM_NAMA.test(n) && !bisnisSimpan.includes(n.toLowerCase()))
    .sort((a, b) => b.length - a.length);
  for (const n of potongan) {
    const pola = escRe(n);
    const sebelum = cleanOutput;
    cleanOutput = cleanOutput
      .replace(new RegExp('\\b(kak|kakak|ka|mas|mbak|pak|bu|bapak|ibu|bang|sis|bro)\\s+' + pola + '\\b', 'gi'), '$1')
      .replace(new RegExp('\\b(halo|hai|hi|hallo|makasih|terima kasih|thanks|thank you|salam kenal|selamat datang|oke|siap|baik|nah|wah)(\\s*,?\\s+)' + pola + '\\b', 'gi'), '$1$2kak');
    if (dimanaSaja) cleanOutput = cleanOutput.replace(new RegExp('\\b' + pola + '\\b', 'gi'), 'kakak');
    if (cleanOutput !== sebelum) namaDihapus = true;
  }
}
if (namaDihapus) {
  cleanOutput = cleanOutput
    .replace(/\bkakak\s+kak\b/gi, 'kak').replace(/\bkak\s+kakak\b/gi, 'kak')
    .replace(/(^|\n)([a-z])/g, (m, p1, p2) => p1 + p2.toUpperCase());
  console.warn('Nama prospek dihapus dari balasan (aturan: selalu "kak").');
}
"""
pa = ganti(pa, C2_LAMA, C2_BARU, "C2-nama-tebakan")
pa_node["parameters"]["jsCode"] = pa


# =========================================================================
# D. RAKIT KONTEKS
# =========================================================================
rk = NODES["Rakit Konteks"]
rk0 = rk["parameters"]["jsCode"]
rk1 = detektor_baru(rk0, "RK-detektor")

rk1 = ganti(rk1,
    "// - nama_bisnis: tidak di sini - ditanyakan di kalimat tawaran deck (aturan prompt).\n",
    "// - nama_bisnis: di pesan perkenalan bersama nama, lalu tanya ulang SEKALI di pesan 2\n"
    "//   kalau belum dijawab (keputusan Steven 2026-09-18). Kalimat tawaran deck tetap\n"
    "//   jaring terakhir (aturan prompt).\n",
    "D1-komentar")

D2_LAMA = r"""const GALIAN = [
  { kolom: 'nama_lengkap',  teks: 'namanya — tanyakan di pesan perkenalan ini (lihat NAMA LAWAN BICARA)',
    boleh: () => pesanPerkenalan },
  { kolom: 'industri',      teks: 'bidang usahanya',
    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 5 },
  { kolom: 'masalah_utama', teks: 'masalah terbesarnya soal chat sekarang',
    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 7 && (!!txt(stats['industri']) || giliran > 5) },
  { kolom: 'volume_chat',   teks: 'kira-kira berapa chat masuk per hari',
    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 3 && giliran <= 9 && !!txt(stats['masalah_utama']) },
];
let galian = null;
for (const g of GALIAN) {
  if (txt(stats[g.kolom]) || !g.boleh()) continue;
  if (ditanyaLalu.has(g.kolom)) break;   // baru saja ditanyakan dan belum terjawab: jeda satu balasan
  galian = g;
  break;
}
"""
D2_BARU = r"""// Urutan 2026-09-18 (keputusan Steven): pesan 1 nama + nama usaha dalam SATU kalimat;
// pesan 2 nama usaha ditanya ulang sekali kalau belum dijawab, kalau sudah langsung bidang
// usaha + cerita singkat; lalu masalah, lalu jumlah chat. Jendela giliran dilebarkan satu
// karena ada giliran tanya ulang nama usaha: bidang 2-6, masalah 2-8, jumlah chat 3-10.
const GALIAN = [
  { kolom: 'nama_lengkap',  teks: 'namanya',
    boleh: () => pesanPerkenalan },
  { kolom: 'nama_bisnis',   teks: 'nama usahanya',
    boleh: () => pesanPerkenalan },
  // Baris ini disusun SEBELUM jawaban giliran ini tersimpan (itu terjadi di Process All),
  // jadi bisa saja nama usahanya ada di pesan yang sedang dibalas - modelnya yang memutuskan.
  { kolom: 'nama_bisnis',   teks: 'nama usahanya — tanya ulang SEKALI ini saja, singkat, karena belum tercatat. '
      + 'Kalau ternyata di pesan ini dia sudah menyebut nama usahanya, jangan ditanyakan: catat lewat [FACTS], '
      + 'lalu tanyakan bidang usahanya sekaligus minta cerita singkat',
    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 3,
    ulangSesudahPerkenalan: true },
  { kolom: 'industri',      teks: 'bidang usahanya, sekaligus minta dia cerita singkat tentang usahanya',
    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 6 },
  { kolom: 'masalah_utama', teks: 'masalah terbesarnya soal chat sekarang',
    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 2 && giliran <= 8 && (!!txt(stats['industri']) || giliran > 6) },
  { kolom: 'volume_chat',   teks: 'kira-kira berapa chat masuk per hari',
    boleh: () => !pesanPerkenalan && !pesanBertanya && giliran >= 3 && giliran <= 10 && !!txt(stats['masalah_utama']) },
];
let galian = null;
if (pesanPerkenalan) {
  // Semua yang belum diketahui di perkenalan ditanyakan bersama, dalam SATU kalimat.
  const kurang = GALIAN.filter(g => g.boleh() && !txt(stats[g.kolom])).map(g => g.teks);
  if (kurang.length) {
    galian = { teks: kurang.join(' dan ')
      + (kurang.length > 1 ? ' — tanyakan bersama dalam SATU kalimat' : ' — tanyakan')
      + ' di pesan perkenalan ini (lihat NAMA LAWAN BICARA)' };
  }
} else {
  for (const g of GALIAN) {
    if (txt(stats[g.kolom]) || !g.boleh()) continue;
    if (ditanyaLalu.has(g.kolom)) {
      if (g.ulangSesudahPerkenalan) {
        if (giliran === 2) { galian = g; break; }   // perkenalan menanyakannya, belum dijawab: ulang sekali
        continue;                                   // sudah diulang sekali: lanjut ke bidang usaha
      }
      break;   // baru saja ditanyakan dan belum terjawab: jeda satu balasan
    }
    galian = g;
    break;
  }
}
"""
rk1 = ganti(rk1, D2_LAMA, D2_BARU, "D2-galian")
rk["parameters"]["jsCode"] = rk1


# =========================================================================
# PEMERIKSAAN AKHIR
# =========================================================================
assert sp.startswith("=") and re.findall(r"\{\{[^}]+\}\}", sp) == EKSPRESI
assert "apa yang bikin dia tertarik" not in sp
assert "Jangan digabung dengan pertanyaan nama usaha" not in sp
assert "Momen paling wajar: saat menawarkan decknya" not in sp
assert "kalau boleh tau nama usahanya apa ya kak?." in sp          # kalimat tawaran (suntingan live) tetap
assert not re.findall(r'(?<!")\bkamu\b(?!")', sp), "masih ada 'kamu' di luar kutipan"
_det = lambda s: s[s.index("// ── Detektor pertanyaan galian"):s.index("\n};\n", s.index("// ── Detektor pertanyaan galian")) + 4]
assert _det(pa) == _det(rk1), "detektor Process All dan Rakit Konteks harus identik"
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
