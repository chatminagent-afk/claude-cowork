# -*- coding: utf-8 -*-
"""
_patch_2026-09-14.py - kolom fakta STATS benar-benar terisi, dan VIRA menanyakan nama di perkenalan.

Masukan : 2026-09-07-VIRA-Personal-Main-v3.6.json   (tidak diubah)
Keluaran: 2026-09-14-VIRA-Personal-Main-v3.8.json
          2026-09-14-system-prompt-VIRA-Personal-v3.8.md
(v3.7 - versi dengan kolom penghitung nama_ditanya - dibatalkan Steven sebelum deploy.
 Versi ini TIDAK menambah kolom apa pun.)

LATAR - audit sheet live 2026-09-14
Dari 530 baris STATS, 5 yang pernah dibalas VIRA. Di kelimanya kolom nama_lengkap,
nama_bisnis, industri, masalah_utama, volume_chat, budget_range, minat_paket, bahasa
dan brief_terisi KOSONG 100% - termasuk percakapan 15 giliran yang sudah sampai
tawaran deck dan VIRA sudah bertanya "Usahanya namanya apa kak?". Tiga sebab:
  1. Satu-satunya jalan masuk fakta ke STATS adalah tag [FACTS], dan model tidak
     menulisnya. Isi blok [DECK_REQUEST] pun tidak pernah mengalir balik ke STATS.
  2. bahasa hanya diisi dari baris bahasa_deck blok [DECK_REQUEST] - di luar itu tidak pernah.
  3. Nama orang tidak pernah ditanyakan; bidang usaha, masalah, dan jumlah chat tidak
     punya urutan tanya yang jelas.
Karena fakta kosong, brief tidak pernah terbentuk (brief_terisi & REQUESTS kosong)
walau deck_requested=Y - Steven kemungkinan besar tidak menerima notif brief.

KEPUTUSAN STEVEN (2026-09-14)
  - Tidak ada kolom baru.
  - Nama ditanyakan SEKALI, di pesan perkenalan, dan disimpan ke nama_lengkap.
  - budget_range dan minat_paket TIDAK ditanyakan; hanya dicatat kalau prospek menyebut sendiri.

ISI PATCH
  A. Process All
     A1. Detektor pertanyaan galian + penangkap jawaban: kalau balasan TERAKHIR yang
         terkirim menanyakan satu kolom dan model tidak menulis [FACTS] untuk kolom itu,
         jawaban prospek disimpan langsung. Hanya mengisi yang kosong, tidak menimpa.
     A2. Isi blok [DECK_REQUEST] mengisi kolom STATS yang masih kosong.
     A3. bahasa dideteksi dari kata fungsi di pesan prospek (satu baris diganti).
     Semua sisanya sisipan; kode lama utuh.
  B. Rakit Konteks: baris `galian_berikutnya` di DATA PROSPEK - satu hal yang digali di
     balasan ini, dari kolom yang masih kosong + giliran ke berapa (STATS.Counter).
     Tiap galian punya jendela giliran dan tidak diulang di balasan tepat sesudahnya,
     jadi tidak cerewet tanpa kolom penghitung.
  C. Prompt: perkenalan + tanya nama, bagian # NAMA LAWAN BICARA, ALUR 7 mengikuti
     `galian_berikutnya`, contoh kalimat galian, dan [FACTS] wajib saat menjawab galian.
  D. Notif ke Steven memakai nama asli (nama akun WA jadi keterangan): Merge Brief,
     Notify Admin Unknown, Format Media Notif, Log EVENTS Delegated.

Node yang diubah: 7 dari 89. Update to STATS TIDAK diubah - semua kolomnya sudah dipetakan.
UAT seksi R membuktikan 82 node lain identik byte per byte.

Catatan teknis: prefix "=" systemMessage dipertahankan (expression mode n8n),
dan keenam ekspresi {{ }} harus tetap utuh.

Jalankan: python _patch_2026-09-14.py
"""
import io
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-07-VIRA-Personal-Main-v3.6.json")
DST = os.path.join(DIR, "2026-09-14-VIRA-Personal-Main-v3.8.json")
MD = os.path.join(DIR, "2026-09-14-system-prompt-VIRA-Personal-v3.8.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

NODES = {n["name"]: n for n in wf["nodes"]}


def ganti(teks, lama, baru, label):
    n = teks.count(lama)
    assert n == 1, "%s: pola ditemukan %d kali (harus 1)" % (label, n)
    return teks.replace(lama, baru)


# Detektor dipakai DUA node (Process All membaca jawaban, Rakit Konteks memilih galian).
# Satu sumber teks supaya keduanya tidak pernah berbeda pendapat; UAT R memeriksanya.
DETEKTOR = r"""// ── Detektor pertanyaan galian (2026-09-14) ──
// SAMA PERSIS di Process All dan Rakit Konteks - UAT seksi R memeriksanya.
// Membaca teks yang benar-benar terkirim ke prospek, per kalimat tanya, dan
// mengembalikan kolom STATS yang ditanyakan. Nama orang ditanya dengan "siapa",
// nama usaha dengan "apa"; kalimat tanpa tanda tanya tidak pernah dihitung.
const slotDitanya = (teks) => {
  const hasil = new Set();
  const kalimat = String(teks || '').toLowerCase().match(/[^.?!\n]+[.?!]*/g) || [];
  for (const k of kalimat) {
    if (!/\?/.test(k)) continue;
    const namaUsaha =
         /\bnama(nya)?\s+(usaha|bisnis|brand|toko|perusahaan|lembaga|kantor|olshop|merek|merk|klinik|sekolah|kursus|bimbel)\w*\b[^.?!\n]{0,20}\b(apa|siapa)\b/.test(k)
      || /\b(usaha|bisnis|brand|toko|perusahaan|lembaga|kantor|olshop|merek|merk|klinik|sekolah|kursus|bimbel)\w*\s+nama(nya)?\s+(apa|siapa)\b/.test(k);
    const namaMilikLain =
         /\bnama(nya)?\s+(usaha|bisnis|brand|toko|perusahaan|lembaga|kantor|olshop|merek|merk|klinik|sekolah|kursus|bimbel|produk|pelanggan|customer|admin|murid|klien|pasien|tamu)/.test(k)
      || /\b(usaha|bisnis|brand|toko|perusahaan|lembaga|kantor|olshop|merek|merk|klinik|sekolah|kursus|bimbel|produk|pelanggan|customer|admin|murid|klien|pasien|tamu)\w*\s+nama(nya)?\b/.test(k);
    if (namaUsaha) hasil.add('nama_bisnis');
    if (!namaMilikLain && (
         /\bnama(nya|mu)?\b[^.?!\n]{0,25}\bsiapa\b/.test(k)
      || /\bsiapa\b[^.?!\n]{0,12}\bnama(nya|mu)?\b/.test(k)
      || /\b(panggil|manggil)(nya|an|annya)?\b[^.?!\n]{0,20}\b(siapa|apa)\b/.test(k)
      || /\b(boleh|mau|yuk|ayo)\b[^.?!\n]{0,10}\bkenalan\b/.test(k)
      || /\b(ngobrol|bicara|chat|chatan|ngomong)\s+(sama|dengan|dgn|ama)\s+siapa\b/.test(k)
      || /\bdengan\s+(kak|kakak|bapak|ibu|pak|bu|mas|mbak)\s+siapa\b/.test(k))) hasil.add('nama_lengkap');
    if (!namaUsaha && (
         /\b(bidang|jenis|industri|sektor)\b[^.?!\n]{0,25}\b(apa|apaan)\b/.test(k)
      || /\b(jualan|jual|bergerak)\b[^.?!\n]{0,20}\b(apa|apaan)\b/.test(k)
      || /\b(usaha|bisnis)(nya|mu)?\s+((kakak|kak)\s+)?(apa|apaan)\b/.test(k))) hasil.add('industri');
    if (/\b(kendala|masalah|repot|ribet|kewalahan|pusing|tantangan|keluhan|capek|susah)(nya)?\b/.test(k)
        && !/\b(lain|lainnya|kelewat|akibat\w*)\b/.test(k)) hasil.add('masalah_utama');
    if (/\b(berapa|brp)\b/.test(k) && /\b(chat|pesan|dm|leads?|inquiry)/.test(k)
        && /\b(hari|sehari|harian|perhari|minggu|seminggu|bulan|sebulan)/.test(k)) hasil.add('volume_chat');
  }
  return hasil;
};
"""


# =========================================================================
# A. PROCESS ALL
# =========================================================================
pa_node = NODES["Process All"]
pa0 = pa_node["parameters"]["jsCode"]

A1_LAMA = (
    "  merged[f]  = baru || lama;\n"
    "  changed[f] = merged[f] !== '' && merged[f] !== lama;\n"
    "}\n"
    "\n"
    "// ── TAG: [DECK_REQUEST] ... [/DECK_REQUEST] ──\n"
)
A1_BARU = (
    "  merged[f]  = baru || lama;\n"
    "  changed[f] = merged[f] !== '' && merged[f] !== lama;\n"
    "}\n"
    "\n"
    + DETEKTOR + r"""
// ── JAWABAN ATAS PERTANYAAN GALIAN (2026-09-14) ──
// Sheet live 2026-09-14: kolom fakta STATS kosong di SEMUA percakapan, termasuk
// percakapan 15 giliran yang sudah sampai tawaran deck - karena satu-satunya jalan
// masuk fakta adalah tag [FACTS], dan model tidak menulisnya. Ini jaring
// deterministiknya: kalau balasan TERAKHIR yang terkirim menanyakan tepat satu
// kolom, dan model tidak menulis [FACTS] untuk kolom itu, jawaban prospek disimpan
// langsung. Hanya mengisi kolom yang masih kosong - tidak pernah menimpa.
// Pesan mentah dipakai (bukan BERSIH) karena BERSIH menghapus baris baru tanpa
// menyisakan spasi, dan buffer debounce memisahkan pesan dengan baris baru.
const LEPAS_AWAL = /^\W*(?:(?:boleh|oke+|ok|iya+|ya+|sip|siap|mau|halo|hallo|hai|hi|oh|ah|eh|wah|wow|yah|anu|hm+|ehm+|em+|hehe\w*|wkwk\w*|haha\w*)\b[\s,.!]*(?:(?:kak|ka|kakak)\b[\s,.!]*)?)+/i;
const BUKAN_JAWABAN = /^\W*(gak|ga|nggak|enggak|engga|tidak|belum|rahasia|nanti|ntar|skip|no|nope|kenapa|buat apa|untuk apa|maksud\w*|bentar|sebentar|males|malas|aman|lancar|gimana|bagaimana)\b/i;
const EKOR = /[\s,]+(kak|ka|kakak|ya|yaa|sih|kok|deh|aja|saja)\s*$/i;
const ambilJawaban = (kolom, pesan) => {
  const mentah = String(pesan || '').trim().replace(LEPAS_AWAL, '').trim();
  const p = BERSIH(mentah.replace(/\s+/g, ' '), 400);
  if (!p || BUKAN_JAWABAN.test(p)) return '';
  if (/\?\s*$/.test(p) && p.split(' ').length <= 8) return '';   // dia balik bertanya
  const baris1 = BERSIH(mentah.split('\n')[0].replace(/\s+/g, ' '), 200);
  if (kolom === 'nama_lengkap') {
    const s = baris1.split(/[,.!?;:]/)[0]
      .replace(/^(nama\s*(ku|saya|aku|gue|gw)|namaku|aku|saya|gue|gw|panggil(\s+(aja|saja))?|biasa\s+dipanggil|dipanggil|kenalin)\s+/i, '')
      .split(/\s+(?:dari|di|owner|pemilik|founder|kak|ka|kakak|mas|mbak|pak|bu|ya|yaa|aja|saja|kok|deh|hehe\w*|wkwk\w*)(?=\s|$)/i)[0]
      .replace(/[^\p{L}\s'.-]/gu, '').replace(/\s+/g, ' ').trim();
    const kata = s.split(' ').filter(Boolean);
    if (!kata.length || kata.length > 3 || s.length < 2 || s.length > 40) return '';
    if (/^(aku|saya|kak|kakak|mau|tanya|harga|terima|makasih|thanks|thank|sama|lagi|lg|siapa|udah|sudah|bisa|oke|ok|iya|ya|bot|admin)$/i.test(kata[0])) return '';
    return kata.map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }
  if (kolom === 'nama_bisnis') {
    const s = baris1.replace(/[.!?]+$/, '')
      .replace(/^(nama(nya)?\s+)?((usaha|bisnis|brand|toko|olshop|perusahaan)(ku|nya|kami)?\s+)?((namanya|nama)\s+)?/i, '')
      .replace(EKOR, '').trim();
    const n = s.split(' ').filter(Boolean).length;
    if (!n || n > 6 || s.length < 2 || s.length > 60) return '';
    if (/^(belum|masih|rahasia|nanti|gak|nggak|tidak|kok)\b/i.test(s)) return '';
    return s;
  }
  if (kolom === 'industri') {
    const s = baris1.replace(/[.!?]+$/, '')
      .replace(/^(aku|saya|gue|gw|kami|kita)\s+/i, '')
      .replace(/^(usaha|bisnis)(ku|nya|kami)?\s+/i, '')
      .replace(/^(bergerak\s+)?(di\s+)?(bidang|industri|sektor)\s+/i, '')
      .replace(EKOR, '').trim();
    const n = s.split(' ').filter(Boolean).length;
    if (!n || n > 10 || s.length < 3 || s.length > 100) return '';
    return s;
  }
  if (kolom === 'masalah_utama') {
    return p.split(' ').length >= 3 ? p : '';
  }
  if (kolom === 'volume_chat') {
    if (!/\d|\b(puluhan|belasan|ratusan|ribuan|seratus|sepuluh|sedikit|dikit|banyak|lumayan)\b/i.test(baris1)) return '';
    const s = baris1.replace(EKOR, '').trim();
    return s.length <= 120 ? s : '';
  }
  return '';
};
const slotDitanyaLalu = [...slotDitanya(prev.last_bot_reply)];
let slotTertangkap = '';
if (slotDitanyaLalu.length === 1) {
  const kolomLalu = slotDitanyaLalu[0];
  if (KOSONG(facts[kolomLalu]) && !merged[kolomLalu]) {
    const nilai = ambilJawaban(kolomLalu,
      (preprocess && preprocess.actualUserMessage) || originalMessage);
    if (nilai) {
      merged[kolomLalu]  = BERSIH(nilai, PANJANG[kolomLalu] || 120);
      changed[kolomLalu] = true;
      slotTertangkap = kolomLalu;
      console.log('Jawaban galian ditangkap tanpa [FACTS]: ' + kolomLalu + ' = ' + merged[kolomLalu]);
    }
  }
}

// bahasa - dari kata fungsi, bukan kata pinjaman: "customer service" dan
// "price list" dipakai orang yang menulis Bahasa Indonesia.
const deteksiBahasa = (pesan) => {
  const kata = String(pesan || '').toLowerCase().match(/[a-z]+/g) || [];
  const ID = /^(yang|dan|di|ke|dari|ini|itu|aku|saya|kamu|kak|kakak|gak|nggak|ga|enggak|tidak|bisa|mau|apa|berapa|gimana|bagaimana|ada|udah|sudah|belum|dong|sih|ya|iya|juga|buat|untuk|sama|dengan|tapi|kalau|kalo|lagi|banget|aja|saja|tanya|soal|boleh|minta|kok|deh|nih|gitu|kayak|seperti|punya|usaha|jualan|harganya|terima|kasih|makasih)$/;
  const EN = /^(the|and|is|are|am|i|you|your|my|we|our|what|how|can|could|would|do|does|want|need|please|thanks|thank|yes|it|this|that|for|with|to|of|about|much|many|will|have|has|be|if|when|where|which|who|just|also|but|or|any|get|know)$/;
  const id = kata.filter(w => ID.test(w)).length;
  const en = kata.filter(w => EN.test(w)).length;
  if (en >= 3 && id <= 1) return 'EN';
  if (en >= 3 && id >= 2) return 'campur';
  if (id >= 2) return 'ID';
  return '';
};

// ── TAG: [DECK_REQUEST] ... [/DECK_REQUEST] ──
"""
)
pa = ganti(pa0, A1_LAMA, A1_BARU, "A1-penangkap")

A2_LAMA = "// ── Jaring niat deck (2026-09-04) ──\n"
A2_BARU = r"""// ── Isi blok [DECK_REQUEST] ikut mengisi STATS (2026-09-14) ──
// Sampai v3.6 arahnya cuma satu: fakta STATS -> blok brief. Model yang menulis blok
// lengkap tapi lupa [FACTS] meninggalkan kolom STATS kosong selamanya.
// Hanya mengisi kolom yang masih kosong.
const DARI_DECK = [['nama_lengkap', 'nama'], ['nama_bisnis', 'nama_bisnis'], ['industri', 'industri'],
                   ['masalah_utama', 'masalah_utama'], ['volume_chat', 'volume_chat_harian'],
                   ['minat_paket', 'minat_paket'], ['budget_range', 'budget_range']];
for (const [fk, dk] of DARI_DECK) {
  if (!merged[fk] && deckRequest[dk]) {
    merged[fk]  = BERSIH(deckRequest[dk], PANJANG[fk] || 120);
    changed[fk] = true;
  }
}

// ── Jaring niat deck (2026-09-04) ──
"""
pa = ganti(pa, A2_LAMA, A2_BARU, "A2-dari-deck")

A3_LAMA = "                     || BERSIH(prev.bahasa, 20);\n"
A3_BARU = "                     || deteksiBahasa(PESAN_USER) || BERSIH(prev.bahasa, 20);\n"
pa = ganti(pa, A3_LAMA, A3_BARU, "A3-bahasa")

A4_LAMA = "    nama_lengkap_changed: changed.nama_lengkap,\n"
A4_BARU = (
    "    nama_lengkap_changed: changed.nama_lengkap,\n"
    "    slotDitanyaLalu,\n"
    "    slotTertangkap,\n"
)
pa = ganti(pa, A4_LAMA, A4_BARU, "A4-keluaran")
pa_node["parameters"]["jsCode"] = pa


# =========================================================================
# B. RAKIT KONTEKS - galian_berikutnya
# =========================================================================
rk = NODES["Rakit Konteks"]
rk0 = rk["parameters"]["jsCode"]
B_LAMA = "if (txt(stats['deck_requested']) === 'Y') barisProspek.push('sudah_minta_pitch_deck: ya');\n"
B_BARU = (
    "if (txt(stats['deck_requested']) === 'Y') barisProspek.push('sudah_minta_pitch_deck: ya');\n"
    "\n"
    + DETEKTOR + r"""
// ── GALIAN BERIKUTNYA (2026-09-14) ──
// Satu hal yang perlu digali di balasan ini, dari kolom STATS yang masih kosong dan
// giliran ke berapa (Counter sebelum giliran ini + 1). Tanpa kolom penghitung:
// tiap galian punya jendela giliran, dan tidak pernah diulang di balasan tepat
// sesudah balasan yang sudah menanyakannya (jeda satu balasan).
// - nama_lengkap: HANYA di pesan perkenalan (keputusan Steven 2026-09-14).
// - nama_bisnis: tidak di sini - ditanyakan di kalimat tawaran deck (aturan prompt).
// - budget_range & minat_paket: SENGAJA tidak pernah digali (keputusan Steven
//   2026-09-14); hanya dicatat kalau prospek menyebut sendiri.
// Definisi pesan perkenalan harus sama dengan `baru` di bawah dan Cek_user_status.
const pesanPerkenalan = txt(stats['greeting_sent']).toUpperCase() !== 'Y';
const giliran = (parseInt(txt(stats['Counter']) || '0', 10) || 0) + 1;
const ditanyaLalu = slotDitanya(stats['last_bot_reply']);
const GALIAN = [
  { kolom: 'nama_lengkap',  teks: 'namanya — tanyakan di pesan perkenalan ini (lihat NAMA LAWAN BICARA)',
    boleh: () => pesanPerkenalan },
  { kolom: 'industri',      teks: 'bidang usahanya',
    boleh: () => !pesanPerkenalan && giliran >= 2 && giliran <= 4 },
  { kolom: 'masalah_utama', teks: 'masalah terbesarnya soal chat sekarang',
    boleh: () => !pesanPerkenalan && giliran >= 2 && giliran <= 6 && (!!txt(stats['industri']) || giliran > 4) },
  { kolom: 'volume_chat',   teks: 'kira-kira berapa chat masuk per hari',
    boleh: () => !pesanPerkenalan && giliran >= 3 && giliran <= 8 && !!txt(stats['masalah_utama']) },
];
let galian = null;
for (const g of GALIAN) {
  if (txt(stats[g.kolom]) || !g.boleh()) continue;
  if (ditanyaLalu.has(g.kolom)) break;   // baru saja ditanyakan dan belum terjawab: jeda satu balasan
  galian = g;
  break;
}
if (galian) barisProspek.push(`galian_berikutnya: ${galian.teks}`);
"""
)
rk["parameters"]["jsCode"] = ganti(rk0, B_LAMA, B_BARU, "B-galian")


# =========================================================================
# C. PROMPT
# =========================================================================
agent = NODES["AI Agent"]
sp0 = agent["parameters"]["options"]["systemMessage"]
assert sp0.startswith("="), "systemMessage harus expression mode"
EKSPRESI = re.findall(r"\{\{[^}]+\}\}", sp0)
assert len(EKSPRESI) == 6, "ekspresi {{ }} berubah: %d" % len(EKSPRESI)

C1_LAMA = "3. Kalau `IS_NEW_USER` true — buka dengan PERKENALAN, digabung dengan jawaban dalam satu pesan.\n"
C1_BARU = (
    "3. Kalau `IS_NEW_USER` true — buka dengan PERKENALAN, digabung dengan jawaban dalam satu pesan.\n"
    "   Pesan perkenalan itu juga menanyakan namanya (lihat NAMA LAWAN BICARA).\n"
)
sp = ganti(sp0, C1_LAMA, C1_BARU, "C1-alur3")

C2_LAMA = "7. Kalau ada peluang wajar, gali satu hal tentang bisnisnya (lihat MENGGALI). Satu saja, jangan menginterogasi.\n"
C2_BARU = (
    "7. Kalau DATA PROSPEK memuat `galian_berikutnya`, itu SATU-SATUNYA pertanyaan galian di balasan ini —\n"
    "   tanyakan sesudah pertanyaannya terjawab, dan lewati kalau tidak muat atau dia sedang buru-buru.\n"
    "   Nama, bidang usaha, masalah utama, dan jumlah chat per hari hanya kutanyakan lewat baris itu.\n"
    "   Kalau baris itu tidak ada, gali satu hal lain tentang bisnisnya (lihat MENGGALI). Satu saja, jangan menginterogasi.\n"
)
sp = ganti(sp, C2_LAMA, C2_BARU, "C2-alur7")

C3_LAMA = "Lalu langsung jawab pertanyaannya. Kalau dia belum bertanya apa-apa, tanya balik apa yang bikin dia tertarik.\n"
C3_BARU = (
    "Lalu langsung jawab pertanyaannya, dan tutup dengan menanyakan namanya dalam satu kalimat pendek,\n"
    "misalnya \"btw boleh tau namanya siapa kak?\". Pesan perkenalan ini satu-satunya pengecualian batas\n"
    "3 kalimat: perkenalan seperti di atas, jawaban singkat kalau dia bertanya, lalu pertanyaan nama.\n"
    "Kalau dia belum bertanya apa-apa, cukup perkenalan lalu tanyakan namanya; apa yang bikin dia tertarik\n"
    "kutanyakan sesudah dia menjawab. Kalau dia sudah menyebut namanya di pesan pertama, jangan ditanyakan.\n"
)
sp = ganti(sp, C3_LAMA, C3_BARU, "C3-perkenalan")

C4_LAMA = "\n# GAYA\n"
C4_BARU = (
    "\n# NAMA LAWAN BICARA\n"
    "\n"
    "Aku ingin tahu sedang bicara dengan siapa, dan Steven juga — namanya ikut masuk ke setiap catatan\n"
    "yang kuteruskan ke dia. Namanya kutanyakan SEKALI, di pesan perkenalan. Kalau dia tidak menjawab\n"
    "atau mengalihkan, jangan ditanyakan lagi — panggil \"kak\" saja.\n"
    "\n"
    "Tanyakan dalam satu kalimat pendek yang ringan dan selalu pakai kata \"siapa\", misalnya\n"
    "\"btw boleh tau namanya siapa kak?\". Jangan digabung dengan pertanyaan nama usaha di balasan yang\n"
    "sama — jawaban satu kata jadi tidak bisa kubedakan nama orang atau nama usahanya.\n"
    "\n"
    "Begitu dia menyebut namanya — di pesan mana pun, ditanya atau tidak — catat lewat `[FACTS nama=\"...\"]`,\n"
    "panggil dia dengan nama itu, dan jangan pernah menanyakannya lagi.\n"
    "\n"
    "`nama_wa` di DATA PROSPEK adalah nama akun WhatsApp-nya — sering nama toko, julukan, atau asal isi.\n"
    "Itu BUKAN nama yang dia sebutkan: jangan dipakai memanggilnya, dan jangan dianggap aku sudah tahu namanya.\n"
    "\n"
    "# GAYA\n"
)
sp = ganti(sp, C4_LAMA, C4_BARU, "C4-bagian-nama")

C5_LAMA = "Ada empat tingkat informasi. Tingkat 1, 2, dan 2B boleh kutanyakan; tingkat 3 tidak pernah.\n"
C5_BARU = (
    "Ada empat tingkat informasi. Tingkat 1, 2, dan 2B boleh kutanyakan; tingkat 3 tidak pernah.\n"
    "\n"
    "Baris `galian_berikutnya` di DATA PROSPEK disusun sistem dari data yang masih kosong. Kalimat tanyanya\n"
    "kususun sendiri: satu kalimat, ringan, diakhiri tanda tanya. Contoh untuk bidang usaha: \"usahanya di\n"
    "bidang apa kak?\"; untuk masalah: \"soal chat, yang paling bikin repot sekarang apa kak?\"; untuk jumlah\n"
    "chat: \"kira-kira sehari ada berapa chat masuk kak?\".\n"
)
sp = ganti(sp, C5_LAMA, C5_BARU, "C5-galian")

C6_LAMA = "Nama usahanya tidak — itu satu-satunya yang harus kutanyakan sengaja, dan tanpa itu cover\n"
C6_BARU = "Nama usahanya tidak — itu yang pasti harus kutanyakan sengaja, dan tanpa itu cover\n"
sp = ganti(sp, C6_LAMA, C6_BARU, "C6-tingkat1")

C7_LAMA = (
    "  Satu kata atau nama yang tidak kukenal, dikirim tepat setelah aku menanyakan nama bisnis atau\n"
    "  bidang usahanya, adalah JAWABAN atas pertanyaan itu — bukan pertanyaan baru. Catat lewat tag ini,\n"
    "  jangan tanya balik apa maksudnya.\n"
)
C7_BARU = (
    "  Satu kata atau nama yang tidak kukenal, dikirim tepat setelah aku menanyakan namanya, nama bisnis,\n"
    "  atau bidang usahanya, adalah JAWABAN atas pertanyaan itu — bukan pertanyaan baru. Catat lewat tag ini,\n"
    "  jangan tanya balik apa maksudnya. BALASAN TERAKHIRMU yang menentukan atributnya: sesudah aku\n"
    "  menanyakan namanya → `nama`; nama usahanya → `nama_bisnis`; bidang usahanya → `industri`.\n"
    "  Setiap kali dia menjawab pertanyaan galianku, tulis `[FACTS]` untuk atribut itu di balasan yang sama.\n"
)
sp = ganti(sp, C7_LAMA, C7_BARU, "C7-facts")


# =========================================================================
# D. NOTIF KE STEVEN - nama asli dulu, nama akun WA jadi keterangan
# =========================================================================
mb = NODES["Merge Brief"]
mb["parameters"]["jsCode"] = ganti(
    mb["parameters"]["jsCode"],
    "  `WA: ${key}\\n` +\n",
    "  `WA: ${key} · ${hasil.nama || 'nama belum disebut'}\\n` +\n",
    "D1-merge-brief")

un = NODES["Notify Admin Unknown"]
_body = [p for p in un["parameters"]["bodyParameters"]["parameters"] if p.get("name") == "message"]
assert len(_body) == 1, "field message Notify Admin Unknown tidak tunggal"
_body[0]["value"] = ganti(
    _body[0]["value"],
    "$('Chat Counter').first().json.user_name",
    "($('Process All').first().json.nama_lengkap_merged "
    "? $('Process All').first().json.nama_lengkap_merged + \" (akun WA: \" + $('Chat Counter').first().json.user_name + \")\" "
    ": $('Chat Counter').first().json.user_name + \" (nama akun WA)\")",
    "D2-unknown")

fm = NODES["Format Media Notif"]
fm["parameters"]["jsCode"] = ganti(
    fm["parameters"]["jsCode"],
    "const nama = cc.user_name || '';\n",
    "// 2026-09-14: nama yang dia sebutkan sendiri didahulukan; nama akun WA sering\n"
    "// nama toko atau julukan, jadi hanya jadi keterangan.\n"
    "const namaAsli = String(pa.nama_lengkap_merged || '').trim();\n"
    "const namaWa = String(cc.user_name || '').trim();\n"
    "const nama = namaAsli\n"
    "  ? namaAsli + (namaWa && namaWa !== namaAsli ? ' (akun WA: ' + namaWa + ')' : '')\n"
    "  : (namaWa ? namaWa + ' (nama akun WA)' : '');\n",
    "D3-media")

ev = NODES["Log EVENTS Delegated"]["parameters"]["columns"]["value"]
assert ev["nama"] == "={{ $('Chat Counter').first().json.user_name }}", ev["nama"]
ev["nama"] = "={{ $('Process All').first().json.nama_lengkap_merged || $('Chat Counter').first().json.user_name }}"


# =========================================================================
# PEMERIKSAAN AKHIR
# =========================================================================
assert sp.startswith("="), "prefix = hilang"
assert re.findall(r"\{\{[^}]+\}\}", sp) == EKSPRESI, "ekspresi {{ }} berubah"
assert "kalau boleh tau nama usahanya apa ya kak?." in sp, "suntingan live v3.6 hilang"
assert "adalah JAWABAN atas pertanyaan itu" in sp
assert pa.count(DETEKTOR) == 1 and rk["parameters"]["jsCode"].count(DETEKTOR) == 1
assert pa.count("replyOverridden = true") == pa0.count("replyOverridden = true")
assert pa.count("\nreturn [{") == 1
assert "nama_ditanya" not in json.dumps(wf, ensure_ascii=False), "sisa v3.7"
assert len(wf["nodes"]) == 89

agent["parameters"]["options"]["systemMessage"] = sp

with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
    f.write(sp[1:])

print("DST    : %s" % os.path.basename(DST))
print("MD     : %s" % os.path.basename(MD))
print("prompt : %d -> %d karakter" % (len(sp0), len(sp)))
print("PA     : %d -> %d karakter" % (len(pa0), len(pa)))
print("RK     : %d -> %d karakter" % (len(rk0), len(rk["parameters"]["jsCode"])))
print("node   : %d (diubah 7: AI Agent, Process All, Rakit Konteks, Merge Brief, "
      "Notify Admin Unknown, Format Media Notif, Log EVENTS Delegated)" % len(wf["nodes"]))
