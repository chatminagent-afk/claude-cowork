# -*- coding: utf-8 -*-
"""
_patch_2026-09-23.py - balasan to the point: tidak merangkum, tidak berjualan tiap giliran,
tidak menanyakan yang sudah dijawab.

Masukan : 2026-09-22-VIRA-Personal-Main-v3.11.json   (= live, dicek lewat MCP 2026-09-23; tidak diubah)
Keluaran: 2026-09-23-VIRA-Personal-Main-v3.12.json
          2026-09-23-system-prompt-VIRA-Personal-v3.12.md

UJI STEVEN 2026-09-23 09:03-09:26 (nomor sendiri, berperan "abdul", owner Humanizer, parfum)
  user : abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1
  VIRA : Salam kenal kak. Jadi Humanizer ini jualan parfum ya, wajar sih ribet, chat parfum
         biasanya banyak yang nanya aroma, ... Nah itu justru yang bisa dipegang VIRA. ...
         Btw nama usahanya Humanizer itu sendiri ya kak, atau itu nama brand parfumnya?   (58 kata)
  user : keduanya          -> VIRA: "Oke, Humanizer itu nama brand sekaligus usahanya. ..."
  user : semua             -> VIRA: "... VIRA bisa pegang itu semua ... biar aku kebayang bebannya?"
  user : 100 an chat       -> VIRA: "100 chat sehari itu lumayan berat buat dibales sendiri, ..."
  user : tanya2 dlu, trs minta pricelist, dan pesen
                           -> VIRA: "Alurnya jelas, tanya dulu, minta pricelist, terus pesen. ..."
  STATS sesudahnya: nama_lengkap, industri, masalah_utama KOSONG walau sudah disebut.
Cacat:
  1. Hampir tiap balasan = [rangkuman ucapan prospek] + [promosi VIRA] + [pertanyaan].
     Prompt v3.10 sendiri mendorongnya: "satu yang menanggapi, satu yang bertanya" dan
     "tanggapan harus MENAMBAH satu hal dari sisi VIRA"; contoh "pas" #2 ikut menggemakan
     jawaban prospek ("Lumayan buat dibalas sendiri sambil ngurus pesanan...").
  2. Tidak ada jaring di kode - panjang 100% bergantung kepatuhan model.
  3. Pertanyaan yang tidak perlu: galian disusun dari STATS SEBELUM jawaban giliran itu
     tersimpan, dan penangkap perkenalan salah baca pesan 4 baris ("aku" sendirian dikira
     penanda nama -> nama kosong; "jualan parfum" tidak dikenal -> industri kosong;
     keluhan tidak pernah dicatat).

KEPUTUSAN STEVEN 2026-09-23
  - Balasan to the point: yang ditanya saja, tanpa merangkum dan tanpa promosi tiap giliran.
  - Promosi VIRA hanya kalau ditanya + satu kalimat di tawaran deck.
  - Jaring pengaman deterministik di kode disetujui (membalik keputusan lama "panjang
    hanya lewat prompt").

ISI PATCH
  A. Prompt: ALUR 10, PERKENALAN (lebih pendek, tanpa basa-basi/pilihan), GAYA (bentuk
     default = satu kalimat tanya; larangan merangkum/menjelaskan balik/promosi/ekor alasan;
     contoh baru), MENGGALI (contoh galian bidang tanpa "boleh cerita sedikit").
  B. Penangkap jawaban (Process All): definisinya dikumpulkan jadi SATU blok bertanda,
     disalin IDENTIK ke Rakit Konteks. Perbaikan di ambilNamaDanUsaha: kata ganti sendirian
     dibuang, "jualan X" -> industri, bagian berisi keluhan -> masalah_utama (dan tidak pernah
     jadi nama/nama usaha), nama jatuh ke bagian polos kalau penanda diri kosong.
  C. Rakit Konteks: galian memakai STATS + fakta dari pesan giliran ini (penangkap yang sama);
     fakta itu ikut tampil di DATA PROSPEK; baris format_balasan per giliran; galian bidang
     tanpa "cerita singkat".
  D. Process All: jaring RINGKAS - di giliran galian biasa (prospek tidak bertanya, bukan
     perkenalan/deck/handover/unknown/media/harga) buang kalimat yang menggemakan pesan
     prospek, lalu kalau masih > 2 kalimat / > 30 kata sisakan pengakuan pendek + kalimat
     tanya terakhir; buang ekor alasan ", biar aku ...?".
  E. Node baru: IF Ringkas Dipangkas -> Log EVENTS Ringkas (event RINGKAS di tab EVENTS).
     Cabang paling bawah dari Process All, jadi jalan SESUDAH kirim WA; onError lanjut.
  F. settings.availableInMCP = true (sudah dinyalakan Steven di live; ikut dibawa file).

Node yang diubah: AI Agent, Process All, Rakit Konteks. Node baru: 2. 86 node lain identik.

Jalankan: python _patch_2026-09-23.py
"""
import copy
import io
import json
import os
import uuid

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-22-VIRA-Personal-Main-v3.11.json")
DST = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.12.json")
MD = os.path.join(DIR, "2026-09-23-system-prompt-VIRA-Personal-v3.12.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

NODES = {n["name"]: n for n in wf["nodes"]}


def ganti(teks, lama, baru, label):
    n = teks.count(lama)
    assert n == 1, "%s: pola ditemukan %d kali (harus 1)" % (label, n)
    return teks.replace(lama, baru)


def potong(teks, awal, akhir, label):
    """Kembalikan (sebelum, isi, sesudah): isi dimulai di `awal`, berhenti tepat sebelum `akhir`."""
    assert teks.count(awal) == 1 and teks.count(akhir) == 1, "%s: anchor tidak tunggal" % label
    i = teks.index(awal)
    j = teks.index(akhir)
    assert i < j, label
    return teks[:i], teks[i:j], teks[j:]


# =========================================================================
# A. PROMPT
# =========================================================================
agent = NODES["AI Agent"]["parameters"]["options"]
sp = agent["systemMessage"]

sp = ganti(sp,
"""10. Sebelum mengirim: buang kalimat yang cuma mengulang atau merangkum ucapannya (lihat GAYA),
    lalu hitung kalimat yang DIBACA PROSPEK saja.""",
"""10. Sebelum mengirim: buang kalimat yang cuma mengulang atau merangkum ucapannya, kalimat yang
    menjelaskan balik keadaannya, dan kalimat promosi VIRA yang tidak dia tanyakan (lihat GAYA),
    lalu hitung kalimat yang DIBACA PROSPEK saja.""", "ALUR 10")

sp = ganti(sp,
""""Halo, aku Steven versi AI. Aku dibangun sama Steven pakai sistem yang sama yang dia bikin untuk kliennya —
namanya VIRA. Jadi kalau kakak penasaran hasilnya kayak apa, kakak lagi ngobrol sama contohnya sekarang."
""",
""""Halo kak, aku Steven versi AI, dibangun Steven pakai VIRA, sistem yang sama yang dia bikin untuk
kliennya. Jadi kakak lagi ngobrol sama contoh hasilnya sekarang."
""", "PERKENALAN contoh")

sp = ganti(sp,
"""Pesan perkenalan ini satu-satunya pengecualian batas 3 kalimat: perkenalan seperti di atas, jawaban
singkat kalau dia bertanya, lalu pertanyaan nama dan nama usaha.
Kalau dia belum bertanya apa-apa, cukup perkenalan lalu pertanyaan itu. Selain nama dan nama usaha,
""",
"""Pesan perkenalan ini satu-satunya pengecualian batas 2 kalimat: perkenalan seperti di atas, jawaban
singkat kalau dia bertanya, lalu pertanyaan nama dan nama usaha.
Kalau dia belum bertanya apa-apa, cukup perkenalan lalu pertanyaan itu — tiga kalimat, sekitar 40 kata.
Tanpa basa-basi tambahan ("senang kakak tertarik", "makasih sudah mampir") dan tanpa menawarkan
pilihan ("mau cerita dulu atau langsung tanya?"). Selain nama dan nama usaha,
""", "PERKENALAN aturan")

GAYA_LAMA_AWAL = "Panjang yang kuincar: DUA kalimat, kira-kira 20 sampai 35 kata"
GAYA_LAMA_AKHIR = "\n\nIni WhatsApp, jadi: tanpa markdown"
_a, _gaya_lama, _b = potong(sp, GAYA_LAMA_AWAL, GAYA_LAMA_AKHIR, "GAYA")
assert _gaya_lama.rstrip().endswith('biasanya lewat langkah apa aja kak?"'), _gaya_lama[-80:]
GAYA_BARU = """Bentuk balasan yang kuincar kalau dia sedang menjawab pertanyaanku atau bercerita: SATU kalimat
tanya, boleh didahului pengakuan pendek maksimal empat kata ("Siap kak.", "Noted kak.", "Salam
kenal kak."). Kalimat tanggapan tidak wajib — orang di WhatsApp langsung bertanya, tidak merangkum
dulu. Batas keras 2 kalimat, sekitar 25 kata. Pengakuan itu pilihan, bukan kewajiban: sering kali
langsung bertanya lebih wajar, dan jangan pakai pengakuan yang sama di dua balasan berturut-turut.
Satu balasan hanya boleh punya SATU pertanyaan.
Kalau dia BERTANYA, jawab pertanyaannya langsung dulu, maksimal 3 kalimat termasuk satu pertanyaan
galian kalau masih muat. Boleh sampai 5 kalimat HANYA kalau dia eksplisit minta dijelaskan detail
atau membandingkan paket. Kalau jawaban dan pertanyaan galian tidak muat, buang pertanyaan
galiannya — tanya di giliran berikutnya. Menjawab pendek lebih penting daripada menggali.
Kalau DATA PROSPEK memuat `format_balasan`, ikuti baris itu untuk balasan ini.

JANGAN MENGULANG UCAPANNYA, DAN JANGAN BERJUALAN DI SETIAP BALASAN. Dia tahu apa yang barusan dia
tulis, dan dia sudah tahu aku menawarkan VIRA. Yang tidak boleh ada di balasan:
- merangkum atau memparafrasekan jawabannya ("Jadi ...", "Berarti ...", "Paham, berarti ...",
  "Alurnya jelas, ...", "Oke, X itu ...", "Semua jenis chat itu ...");
- menjelaskan balik keadaan yang dia alami sendiri ("wajar sih ribet, chat X biasanya ...",
  "50 chat sehari itu lumayan berat buat dibalas sendiri");
- menjelaskan kemampuan VIRA yang tidak dia tanyakan ("VIRA bisa pegang itu semua ...", "bagian
  itu yang paling bisa diotomasi", "jadi kakak tinggal fokus ke ...");
- ekor alasan di pertanyaan ("..., biar aku kebayang bebannya?").
Kemampuan VIRA baru kujelaskan kalau dia menanyakannya, atau dalam SATU kalimat di balasan yang
menawarkan deck — dikaitkan dengan masalah yang dia sebut sendiri.

Contoh. Dia: "50an chat sehari"
Terlalu panjang, mengulang lalu berjualan: "50 chat sehari itu lumayan berat buat dibalas sendiri,
apalagi sambil ngurus pesanan. VIRA bisa pegang semuanya 24 jam, jadi kakak tinggal fokus ke yang
siap order. Dari chat pertama sampai jadi pesan, biasanya lewat langkah apa aja kak?"
Pas: "Dari chat pertama sampai jadi pesan, biasanya lewat langkah apa aja kak?"
Contoh lain yang pas. Dia: "biasanya tanya dulu, minta katalog, baru order" — "Yang paling sering
ditanyain biasanya apa aja kak?\""""
sp = _a + GAYA_BARU + _b

sp = ganti(sp,
"""ulang: "oh iya, nama usahanya apa kak?"; untuk bidang usaha: "usahanya bergerak di bidang apa kak,
boleh cerita sedikit?"; untuk masalah:""",
"""ulang: "oh iya, nama usahanya apa kak?"; untuk bidang usaha: "usahanya bergerak di bidang apa kak?";
untuk masalah:""", "MENGGALI contoh bidang")

agent["systemMessage"] = sp


# =========================================================================
# B. PENANGKAP JAWABAN - satu blok, identik di dua node
# =========================================================================
pa_node = NODES["Process All"]["parameters"]
pa = pa_node["jsCode"]

AWAL_A = "// ── JAWABAN ATAS PERTANYAAN GALIAN (2026-09-14) ──"
AWAL_B = "const slotDitanyaLalu = [...slotDitanya(prev.last_bot_reply)];"
AWAL_C = "// ── JAWABAN PERKENALAN: nama DAN nama usaha sekaligus (2026-09-18) ──"
AWAL_D = "if (slotDitanyaLalu.includes('nama_lengkap') && slotDitanyaLalu.includes('nama_bisnis')) {"
AKHIR_D = "// bahasa - dari kata fungsi"
pa_sebelum, blok_a, _ = potong(pa, AWAL_A, AWAL_B, "PA A")
_, blok_b, _ = potong(pa, AWAL_B, AWAL_C, "PA B")
_, blok_c, _ = potong(pa, AWAL_C, AWAL_D, "PA C")
_, blok_d, pa_sesudah = potong(pa, AWAL_D, AKHIR_D, "PA D")

# --- perbaikan ambilNamaDanUsaha (uji 2026-09-23) ---
blok_c = ganti(blok_c,
"""// Uji 2026-09-17: "Nadia kak, bisnis aku katering, chat suka numpuk pas malem"
//   -> nama_lengkap = Nadia, industri = katering, nama_bisnis tetap kosong.
""",
"""// Uji 2026-09-17: "Nadia kak, bisnis aku katering, chat suka numpuk pas malem"
//   -> nama_lengkap = Nadia, industri = katering, nama_bisnis tetap kosong.
// Uji 2026-09-23: "abdul / aku owner humanizer / jualan parfum / kdg ribet balesin org ty 1 1"
//   -> dulu nama & industri kosong ("aku" sendirian dibaca penanda nama; "jualan parfum" tidak
//   dikenal) dan keluhannya tidak tercatat, jadi VIRA menanyakan lagi yang sudah dia sebut.
//   Sekarang: nama = Abdul, nama_bisnis = humanizer, industri = jualan parfum,
//   masalah_utama = keluhannya. Bagian berisi keluhan tidak pernah jadi nama / nama usaha.
""", "PA C komentar")
blok_c = ganti(blok_c,
"const JENIS_USAHA = /^((usaha|bisnis|jualan|jual|di\\s+bidang|bidang)\\s+)?(katering|catering|kuliner|makanan|minuman|kue|bakery|kafe|cafe|coffee shop|resto|restoran|warung|fashion|baju|pakaian|hijab|skincare|kosmetik|kecantikan|salon|barbershop|laundry|properti|",
"const JENIS_USAHA = /^((usaha|bisnis|jualan|jual|di\\s+bidang|bidang)\\s+)?(katering|catering|kuliner|makanan|minuman|kue|bakery|kafe|cafe|coffee shop|resto|restoran|warung|fashion|baju|pakaian|hijab|skincare|kosmetik|kecantikan|parfum|aksesoris|sepatu|tas|frozen food|snack|herbal|salon|barbershop|laundry|interior|furniture|percetakan|konveksi|bengkel|rental|properti|",
"PA JENIS_USAHA")
blok_c = ganti(blok_c,
"""const PENANDA_USAHA = /^(dari|owner|pemilik|founder|punya|(nama\\s+)?(usaha|bisnis|toko|brand|olshop|perusahaan)(ku|nya|kami)?)\\b/i;
""",
"""const PENANDA_USAHA = /^(dari|owner|pemilik|founder|punya|(nama\\s+)?(usaha|bisnis|toko|brand|olshop|perusahaan)(ku|nya|kami)?)\\b/i;
const KATA_GANTI_SAJA = /^(aku|saya|gue|gw|ane|sy)$/i;
// Jawaban atas pertanyaan nama usaha yang jelas BUKAN nama (eval 2026-09-23: "makasih kak",
// "boleh dong dibuatin deck", "sekitar 20-30 chat sehari" sempat tersimpan sebagai nama_bisnis).
const NAMA_USAHA_MUSTAHIL = /\\b(makasih|terima\\s*kasih|thanks?|thx|tq|sip|oke|ok|siap|deck|dibuatin|dibikinin|entar)\\b/i;
// Pesan pertama yang memperkenalkan diri ("aku Rina dari Kopi Senja", "saya owner ...").
// "aku lihat / mau / lagi / cari ..." bukan perkenalan diri.
const KENALAN_DIRI = /(^|[\\s,.!])(aku|saya|gue|gw)\\s+(?!(mau|mo|mw|lagi|lg|lihat|liat|cari|nyari|pengen|pgn|pingin|ingin|butuh|punya|tertarik|udah|sudah|baru|juga|tadi|dari|penasaran|bingung|coba|nanya|tanya|bisa|kira|rasa|pikir|sempat|sempet|dapat|dapet|kenal|minta|perlu|ada|nemu|denger|dengar|tau|tahu|mo|boleh)\\b)\\p{L}{2,}|\\bnama\\s*(ku|saya|aku|gue)\\b|\\b(owner|pemilik|founder)\\b/iu;
const KELUHAN = /\\b(ribet|repot|kerepotan|kewalahan|keteteran|keteter|numpuk|menumpuk|kelewat\\w*|telat|lambat|capek|cape|pusing|susah|kesulitan|tenggelam|tenggelem|overwhelm\\w*|(gak|ga|nggak|tidak|gk)\\s+(sempet|sempat|keburu))\\b/i;
const DAGANGAN = /^(jualan|jual)\\s+\\S/i;
""", "PA penanda baru")
blok_c = ganti(blok_c,
"""    .flatMap(pecahDiPenanda).map(s => s.trim()).filter(Boolean).slice(0, 4);
  const diri  = bagian.filter(s => PENANDA_DIRI.test(s));
  const usaha = bagian.filter(s => !PENANDA_DIRI.test(s) && PENANDA_USAHA.test(s));
  const polos = bagian.filter(s => !PENANDA_DIRI.test(s) && !PENANDA_USAHA.test(s));
  const calonNama = diri[0] || polos.shift() || '';
  const nama = calonNama ? ambilJawaban('nama_lengkap', calonNama) : '';
  if (nama) hasil.nama_lengkap = nama;
""",
"""    .flatMap(pecahDiPenanda).map(s => s.trim()).filter(Boolean)
    .filter(s => !KATA_GANTI_SAJA.test(s)).slice(0, 6);
  const keluhan = bagian.find(s => KELUHAN.test(s));
  const masalah = keluhan ? ambilJawaban('masalah_utama', keluhan) : '';
  if (masalah) hasil.masalah_utama = masalah;
  const calon = bagian.filter(s => !KELUHAN.test(s));
  const diri  = calon.filter(s => PENANDA_DIRI.test(s));
  const usaha = calon.filter(s => !PENANDA_DIRI.test(s) && PENANDA_USAHA.test(s));
  const polos = calon.filter(s => !PENANDA_DIRI.test(s) && !PENANDA_USAHA.test(s));
  let nama = diri[0] ? ambilJawaban('nama_lengkap', diri[0]) : '';
  if (!nama) {
    const i = polos.findIndex(s => !DAGANGAN.test(s) && !JENIS_USAHA.test(s));
    if (i >= 0) nama = ambilJawaban('nama_lengkap', polos.splice(i, 1)[0]);
  }
  if (nama) hasil.nama_lengkap = nama;
""", "PA ambilNamaDanUsaha kepala")
blok_c = ganti(blok_c,
"""    if (JENIS_USAHA.test(isi)) { if (!hasil.industri) hasil.industri = isi; continue; }
""",
"""    if (JENIS_USAHA.test(isi) || DAGANGAN.test(isi)) { if (!hasil.industri) hasil.industri = isi; continue; }
""", "PA dagangan -> industri")
blok_c = ganti(blok_c,
"""    if (!hasil.nama_bisnis) hasil.nama_bisnis = isi;
  }
  return hasil;
};
""",
"""    if (!hasil.nama_bisnis) hasil.nama_bisnis = isi;
  }
  // Nama usaha yang sudah menyebut jenisnya ("Klinik Sehat Gigi", "Bimbel Cerdas Mandiri"):
  // bidangnya tidak perlu ditanya lagi (eval 2026-09-23: "Kliniknya bergerak di bidang apa aja?").
  if (hasil.nama_bisnis && !hasil.industri) {
    const j = hasil.nama_bisnis.match(JENIS_DI_NAMA);
    if (j) hasil.industri = j[1].toLowerCase();
  }
  return hasil;
};
// Jumlah chat yang disebut tanpa ditanya (eval 2026-09-23: prospek menulis "100 an chat",
// VIRA membalas "Kira-kira sehari berapa chat masuk kak?"). Hanya angka yang berdiri sendiri
// dan menempel ke kata chat/pesan atau ke satuan waktu - "tanya2", "paket 2", "2 admin" tidak.
const VOLUME_SPONTAN = /(^|[^\\p{L}\\d])\\d+(\\s*-\\s*\\d+)?\\s*(an)?\\s*(chat|pesan|dm|inbox|inquiry|wa)\\b|\\b(sehari|per\\s*hari|perhari|seminggu|sebulan|per\\s*(minggu|bulan))\\b[^.?!\\n]{0,25}(^|[^\\p{L}\\d])\\d+|(^|[^\\p{L}\\d])\\d+(\\s*-\\s*\\d+)?\\s*(an)?\\b[^.?!\\n]{0,25}\\b(sehari|per\\s*hari|perhari|seminggu|sebulan)\\b/iu;
// Baris yang bertanya atau bicara harga/jam/admin bukan jumlah chat ("3 juta sebulan?", "buka jam 8").
const BUKAN_VOLUME = /\\?|\\b(rp|juta|jt|rb|ribu|harga|biaya|paket|bayar|admin|jam)\\b/i;
const ambilVolumeSpontan = (pesan) => {
  const baris = String(pesan || '').split('\\n').map(s => s.trim())
    .find(s => VOLUME_SPONTAN.test(s) && !BUKAN_VOLUME.test(s));
  return baris ? BERSIH(baris.replace(LEPAS_AWAL, '').replace(EKOR, ''), 120) : '';
};
""", "PA jenis di nama + volume spontan")
blok_c = ganti(blok_c,
"""const DAGANGAN = /^(jualan|jual)\\s+\\S/i;
""",
"""const DAGANGAN = /^(jualan|jual)\\s+\\S/i;
const JENIS_DI_NAMA = /\\b(katering|catering|bakery|kafe|cafe|kopi|coffee|resto|restoran|warung|laundry|salon|barbershop|klinik|apotek|bimbel|kursus|sekolah|travel|konveksi|percetakan|bengkel|rental|properti|kontraktor|konsultan|skincare|parfum|hijab|kosmetik|furniture|interior)\\b/i;
""", "PA JENIS_DI_NAMA")
blok_a = ganti(blok_a,
"""    if (!/\\d|\\b(puluhan|belasan|ratusan|ribuan|seratus|sepuluh|sedikit|dikit|banyak|lumayan)\\b/i.test(baris1)) return '';
""",
"""    if (!/(^|[^\\p{L}])\\d|\\b(puluhan|belasan|ratusan|ribuan|seratus|sepuluh|sedikit|dikit|banyak|lumayan)\\b/iu.test(baris1)) return '';
""", "PA volume angka berdiri sendiri")
blok_a = ganti(blok_a,
"""    if (/^(belum|masih|rahasia|nanti|gak|nggak|tidak|kok)\\b/i.test(s)) return '';
""",
"""    if (/^(belum|masih|rahasia|nanti|gak|nggak|tidak|kok)\\b/i.test(s)) return '';
    if (BUKAN_NAMA_USAHA.test(s) || NAMA_USAHA_MUSTAHIL.test(s) || VOLUME_SPONTAN.test(s)) return '';   // 2026-09-23
""", "PA nama usaha mustahil")
blok_d = blok_d + """// Perkenalan diri di pesan PERTAMA (2026-09-23). Dulu hanya tercatat kalau model menulis
// [FACTS]; eval: v3.12 tidak menulisnya, menanyakan lagi, lalu jawaban lain ("makasih")
// tersimpan sebagai nama usaha. Hanya jalan kalau ada penanda perkenalan diri (KENALAN_DIRI).
if (isNewUser) {
  const pesanPertama = (preprocess && preprocess.actualUserMessage) || originalMessage;
  if (KENALAN_DIRI.test(pesanPertama)) {
    for (const [kolom, nilai] of Object.entries(ambilNamaDanUsaha(pesanPertama))) {
      if (!KOSONG(facts[kolom]) || merged[kolom]) continue;
      merged[kolom]  = BERSIH(nilai, PANJANG[kolom] || 120);
      changed[kolom] = true;
      slotTertangkap = slotTertangkap ? slotTertangkap + ',' + kolom : kolom;
    }
  }
}
"""
blok_d = blok_d + """// Jumlah chat yang disebut tanpa ditanya (2026-09-23) - lihat ambilVolumeSpontan.
if (!merged.volume_chat && KOSONG(facts.volume_chat)) {
  const vol = ambilVolumeSpontan((preprocess && preprocess.actualUserMessage) || originalMessage);
  if (vol) {
    merged.volume_chat  = vol;
    changed.volume_chat = true;
    slotTertangkap = slotTertangkap ? slotTertangkap + ',volume_chat' : 'volume_chat';
    console.log('Jumlah chat disebut tanpa ditanya: ' + vol);
  }
}

"""

TANDA_MULAI = ("// ── PENANGKAP JAWABAN — MULAI ──\n"
               "// IDENTIK di Process All dan Rakit Konteks (2026-09-23) - UAT seksi R memeriksanya.\n"
               "// Process All memakainya untuk MENYIMPAN jawaban; Rakit Konteks memakainya supaya\n"
               "// galian tidak menanyakan sesuatu yang sudah dijawab di pesan giliran ini.\n")
TANDA_SELESAI = "// ── PENANGKAP JAWABAN — SELESAI ──\n\n"
BLOK_BERSAMA = TANDA_MULAI + blok_a + blok_c + TANDA_SELESAI
pa = pa_sebelum + BLOK_BERSAMA + blok_b + blok_d + pa_sesudah

# =========================================================================
# D. PROCESS ALL - jaring RINGKAS
# =========================================================================
RINGKAS = r"""// ── RINGKAS (2026-09-23) ──
// Uji Steven 2026-09-23 ("abdul", parfum): 6 balasan 28-60 kata, hampir semuanya
// [merangkum jawaban prospek] + [promosi VIRA] + [pertanyaan], padahal prompt sudah melarang
// merangkum dan membatasi 2 kalimat. Prompt tetap tuas utamanya; ini jaring terakhir yang
// deterministik, HANYA untuk giliran galian biasa: prospek tidak sedang bertanya (jawaban
// atas pertanyaannya tidak boleh terpotong), bukan perkenalan, bukan brief/deck/diskusi,
// bukan handover, bukan [UNKNOWN], bukan media, tidak menyebut harga, dan balasannya
// memuat pertanyaan (yang disisakan pertanyaan terakhirnya).
//  1. Kalimat pernyataan yang menggemakan pesan prospek dibuang.
//  2. Lebih dari satu kalimat tanya -> sisakan satu: yang menanyakan galian_berikutnya, kalau
//     tidak ada, yang terakhir.
//  3. Masih > 2 kalimat atau > 30 kata -> pengakuan pendek (<= 4 kata) + kalimat tanya.
//  4. Ekor alasan di kalimat tanya dibuang: ", biar aku kebayang bebannya?" -> "?".
// Blok [DECK_REQUEST] sendiri tidak mengecualikan: model juga menulisnya sebagai pembaruan brief
// diam-diam (eval 2026-09-23). Balasan yang benar-benar menawarkan/mengabarkan deck sudah
// dikecualikan lewat LEWATI_RINGKAS (kata deck / Steven + teruskan) dan mintaDeck.
// Pesan perkenalan punya aturan sendiri di bawah: hanya pertanyaan nama + nama usaha yang tinggal.
// Setiap pemangkasan dicatat ke EVENTS lewat node Log EVENTS Ringkas.
const RINGKAS_MAKS_KALIMAT = 2, RINGKAS_MAKS_KATA = 30, PENGAKUAN_MAKS_KATA = 4;
// Sama dengan `pesanBertanya` di Rakit Konteks.
const PROSPEK_BERTANYA = /\?|\b(apa|apakah|gimana|gmn|bagaimana|berapa|brp|kenapa|knp|kapan|mana)\b/i.test(PESAN_USER);
const LEWATI_RINGKAS = /\brp\s?\d|\d\s?(rb|ribu|jt|juta)\b|\b(deck|pitch|proposal|basic|premium|landing page|link|brosur|katalog)\b|\bsteven\b[^.?!\n]{0,40}\b(teruskan|terusin|sambung\w*|hubung\w*|diskusi|ngobrol|bicara|langsung)\b|\b(teruskan|terusin|sambung\w*|hubungkan)\b[^.?!\n]{0,40}\bsteven\b/i;
const pecahKalimat = (t) => String(t || '').split(/(?<=[.?!])\s+|\n+/).map(s => s.trim()).filter(Boolean);
const hitungKata = (t) => String(t || '').split(/\s+/).filter(Boolean).length;
const NORMAL_KATA = { dlu: 'dulu', dl: 'dulu', trs: 'terus', trus: 'terus', sm: 'sama', yg: 'yang',
  gk: 'gak', ga: 'gak', nggak: 'gak', bs: 'bisa', org: 'orang', pesen: 'pesan', bales: 'balas',
  balesin: 'balas', dibales: 'balas', dibalas: 'balas', ty: 'tanya', tny: 'tanya', nanya: 'tanya',
  ditanya: 'tanya', ditanyain: 'tanya', kdg: 'kadang', kadang2: 'kadang' };
const KATA_SEPELE = /^(aku|saya|kak|kakak|ka|ya|yaa|iya|dan|atau|yang|itu|ini|di|ke|dari|ada|aja|saja|sih|kok|deh|dong|juga|udah|sudah|lagi|mau|bisa|gak|tidak|buat|untuk|sama|dengan|biasanya|kalau|kalo|klo|jadi|terus|nah|oke|ok|baru|an|nya|pun|lah|kah|kadang|semua)$/;
const kataIsi = (s) => String(s || '').toLowerCase()
  .replace(/[^\p{L}\p{N}\s]/gu, ' ').split(/\s+/)
  .map(w => w.replace(/(\p{L})\d+$/u, '$1'))
  .map(w => w.replace(/^(\d+)an$/, '$1'))
  .map(w => NORMAL_KATA[w] || w)
  .filter(w => w && !KATA_SEPELE.test(w));
const menggema = (kalimat, pesan) => {
  const isiPesan = new Set(kataIsi(pesan));
  if (!isiPesan.size) return false;
  const sama = [...new Set(kataIsi(kalimat))].filter(w => isiPesan.has(w)).length;
  return sama >= 3 || (sama >= 2 && sama / isiPesan.size >= 0.5);
};
const GALIAN_KOLOM = (() => { try { return String($('Rakit Konteks').first().json.galian_kolom || ''); } catch (e) { return ''; } })();
// Balasan model yang isinya CUMA tag (eval 2026-09-23: jawaban nama dibalas "[FACTS ...]" saja,
// prospek menerima "Maaf, ada kendala sebentar"). Kalau giliran ini punya galian, kirim
// pertanyaan galiannya dengan kalimat contoh dari prompt (bagian MENGGALI).
const TANYA_GALIAN = {
  nama_bisnis: 'Oh iya, nama usahanya apa kak?',
  industri: 'Usahanya bergerak di bidang apa kak?',
  masalah_utama: 'Soal chat, yang paling bikin repot sekarang apa kak?',
  volume_chat: 'Kira-kira sehari ada berapa chat masuk kak?',
};
const hanyaTag = !aiOutput
  .replace(/\[\s*DECK_REQUEST\s*\][\s\S]*?\[\s*\/\s*DECK_REQUEST\s*\]/gi, '')
  .replace(/\[[^\]]*\]/g, '').trim();
let cadangan = '';
if (hanyaTag && !isUnknown && !isNewUser && !isTalkToAdmin && !isSendMedia && TANYA_GALIAN[GALIAN_KOLOM]) {
  cleanOutput = (changed.nama_lengkap ? 'Salam kenal kak. ' : '') + TANYA_GALIAN[GALIAN_KOLOM];
  cadangan = 'cadangan-galian';
  console.warn('Model hanya menulis tag - dikirim pertanyaan galian ' + GALIAN_KOLOM);
}
const teksSebelumRingkas = cadangan ? aiOutput : cleanOutput;
let ringkasAlasan = cadangan;
const bolehRingkas = !cadangan && !isNewUser && !PROSPEK_BERTANYA && !mintaDeck
  && !isTalkToAdmin && !isUnknown && !isSendMedia && !replyOverridden
  && /\?/.test(cleanOutput) && !LEWATI_RINGKAS.test(cleanOutput);
if (bolehRingkas) {
  let kal = pecahKalimat(cleanOutput);
  const jumlahAwal = kal.length;
  kal = kal.filter(k => /\?/.test(k) || !menggema(k, PESAN_USER));
  if (kal.length < jumlahAwal) ringkasAlasan = 'gema';
  // Pertanyaan tentang hal yang SUDAH diketahui (eval 2026-09-23: "Usahanya bergerak di bidang
  // apa kak?" padahal bidangnya katering; jumlah chat ditanya sesudah dia menyebutnya) dibuang.
  // Kalau itu satu-satunya kalimat, diganti pertanyaan galian giliran ini (kalau ada).
  // masalah_utama tidak dihitung: pertanyaan lanjutan soal akibatnya ("bagian mananya?") disengaja.
  const DIKETAHUI = ['nama_lengkap', 'nama_bisnis', 'industri', 'volume_chat'].filter(k => merged[k]);
  const sudahTahu = (k) => { const s = [...slotDitanya(k)]; return s.length > 0 && s.every(x => DIKETAHUI.includes(x)); };
  const kalBaru = kal.filter(k => !(/\?/.test(k) && sudahTahu(k)));
  if (kalBaru.length < kal.length && (kalBaru.length || TANYA_GALIAN[GALIAN_KOLOM])) {
    kal = kalBaru.length ? kalBaru : [TANYA_GALIAN[GALIAN_KOLOM]];
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+sudah-tahu' : 'sudah-tahu';
  }
  const iTanyaSemua = kal.map((k, i) => (/\?/.test(k) ? i : -1)).filter(i => i >= 0);
  if (iTanyaSemua.length > 1) {
    const cocok = GALIAN_KOLOM ? iTanyaSemua.find(i => slotDitanya(kal[i]).has(GALIAN_KOLOM)) : undefined;
    const pilih = cocok !== undefined ? cocok : iTanyaSemua[iTanyaSemua.length - 1];
    kal = kal.filter((k, i) => !/\?/.test(k) || i === pilih);
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+satu-tanya' : 'satu-tanya';
  }
  if (kal.length > RINGKAS_MAKS_KALIMAT || hitungKata(kal.join(' ')) > RINGKAS_MAKS_KATA) {
    const iTanya = kal.map(k => /\?/.test(k)).lastIndexOf(true);
    const pengakuan = (iTanya > 0 && !/\?/.test(kal[0]) && hitungKata(kal[0]) <= PENGAKUAN_MAKS_KATA) ? kal[0] : '';
    let tanya = kal[iTanya];
    if (!pengakuan) tanya = tanya.replace(/^(btw|nah|terus|trus|jadi|oh iya|ngomong-ngomong)[\s,]+/i, '');
    kal = [pengakuan, tanya].filter(Boolean);
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+panjang' : 'panjang';
  }
  const iAkhir = kal.length - 1;
  const tanpaEkor = kal[iAkhir].replace(/,?\s+(biar|supaya|agar)\s+(aku|saya|steven|kita)\b[^?]{0,60}\?\s*$/i, '?');
  if (tanpaEkor !== kal[iAkhir]) {
    kal[iAkhir] = tanpaEkor;
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+ekor' : 'ekor';
  }
  if (ringkasAlasan) {
    cleanOutput = kal.join(' ').replace(/^([a-z])/, (m) => m.toUpperCase());
    console.log('RINGKAS (' + ringkasAlasan + '): ' + hitungKata(teksSebelumRingkas) + ' -> '
              + hitungKata(cleanOutput) + ' kata');
  }
}
// Pertanyaan yang hampir sama dengan pertanyaan balasan sebelumnya tidak diulang - kalau dia
// tidak menjawabnya, biarkan (eval 2026-09-23: "makasih kak" dibalas pertanyaan yang sama; jumlah
// chat ditanya lagi di balasan berikutnya). Berlaku juga saat prospek bertanya: yang dibuang
// hanya pertanyaan kembarnya, jawabannya tidak disentuh. Pertanyaan galian dikecualikan: tanya
// ulang nama usaha memang disengaja (jeda & jendelanya diatur Rakit Konteks). Kalau yang tersisa
// cuma pertanyaan itu, balasan dibiarkan - tidak pernah mengirim teks kosong.
if (!cadangan && !isNewUser && !mintaDeck && !isTalkToAdmin && !isUnknown && !isSendMedia && !replyOverridden
    && /\?/.test(cleanOutput)) {
  const tanyaLalu = pecahKalimat(prev.last_bot_reply).filter(k => /\?/.test(k));
  const mirip = (a, b) => {
    const x = new Set(kataIsi(a)), y = new Set(kataIsi(b));
    const sama = [...x].filter(w => y.has(w)).length;
    return sama >= 3 && sama / Math.min(x.size, y.size) >= 0.7;
  };
  const kal = pecahKalimat(cleanOutput);
  const sisa = kal.filter(k => !(/\?/.test(k) && !(GALIAN_KOLOM && slotDitanya(k).has(GALIAN_KOLOM))
                                  && tanyaLalu.some(t => mirip(k, t))));
  if (sisa.length && sisa.length < kal.length) {
    cleanOutput = sisa.join(' ');
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+tanya-ulang' : 'tanya-ulang';
    console.log('RINGKAS (tanya-ulang): pertanyaan yang sama dengan balasan sebelumnya dibuang');
  }
}
// Kalau pengaman di atas membuang satu-satunya pertanyaan dan giliran ini punya galian, pertanyaan
// galiannya yang dikirim - percakapan tidak berhenti di "Noted kak." (eval 2026-09-23).
if (ringkasAlasan && !cadangan && !isNewUser && !PROSPEK_BERTANYA && TANYA_GALIAN[GALIAN_KOLOM]
    && /\?/.test(teksSebelumRingkas) && !/\?/.test(cleanOutput)) {
  cleanOutput = cleanOutput.trim() + ' ' + TANYA_GALIAN[GALIAN_KOLOM];
  ringkasAlasan += '+galian';
}
// Perkenalan: satu-satunya pertanyaan adalah nama + nama usaha (eval 2026-09-23: 3 dari 10
// perkenalan menambah "mau tanya bagian mana?" / "bidang apa?" di bubble yang sama). Kalimat
// pernyataan - termasuk jawaban atas pertanyaannya - tidak disentuh.
//  - ada pertanyaan nama/nama usaha -> pertanyaan lain dibuang;
//  - tidak ada, padahal nama/nama usaha belum diketahui (eval: 1 dari 15 perkenalan lupa, lalu
//    nama & usahanya tidak pernah tercatat) -> pertanyaan lain diganti pertanyaan baku dari prompt;
//  - keduanya sudah diketahui (dia memperkenalkan diri) -> sisakan pertanyaan terakhir saja.
if (isNewUser && !mintaDeck && !isTalkToAdmin && !isUnknown && !isSendMedia && !replyOverridden) {
  const kal = pecahKalimat(cleanOutput);
  const tanyaKenalan = (k) => { const s = slotDitanya(k); return s.has('nama_lengkap') || s.has('nama_bisnis'); };
  const tanyaSemua = kal.filter(k => /\?/.test(k));
  const kurangNama = !merged.nama_lengkap, kurangUsaha = !merged.nama_bisnis;
  let sisa = kal;
  if (tanyaSemua.some(tanyaKenalan)) {
    sisa = kal.filter(k => !/\?/.test(k) || tanyaKenalan(k));
  } else if (kurangNama || kurangUsaha) {
    const baku = kurangNama && kurangUsaha ? 'Btw boleh tau nama kakak siapa, dan nama usahanya apa?'
      : kurangNama ? 'Btw boleh tau nama kakak siapa?' : 'Btw nama usahanya apa kak?';
    sisa = [...kal.filter(k => !/\?/.test(k)), baku];
  } else if (tanyaSemua.length > 1) {
    sisa = kal.filter(k => !/\?/.test(k) || k === tanyaSemua[tanyaSemua.length - 1]);
  }
  if (sisa.join(' ') !== kal.join(' ')) {
    cleanOutput = sisa.join(' ');
    ringkasAlasan = 'perkenalan';
    console.log('RINGKAS (perkenalan): hanya pertanyaan kenalan yang tinggal');
  }
}

"""
pa = ganti(pa, "// ── RESOLVE MEDIA URL + caption dari LINKS ──",
           RINGKAS + "// ── RESOLVE MEDIA URL + caption dari LINKS ──", "PA RINGKAS")
pa = ganti(pa, "    namaDihapus,\n",
           "    namaDihapus,\n"
           "    ringkas: ringkasAlasan,\n"
           "    ringkas_asli: ringkasAlasan ? teksSebelumRingkas : '',\n"
           "    needs_ringkas_log: ringkasAlasan ? 'true' : 'false',\n", "PA output")
pa_node["jsCode"] = pa

# =========================================================================
# C. RAKIT KONTEKS
# =========================================================================
rk_node = NODES["Rakit Konteks"]["parameters"]
rk = rk_node["jsCode"]

BERSIH_PA = pa[pa.index("const BERSIH = "):pa.index("\n// nilai yang artinya")]
rk = ganti(rk, "// ── GALIAN BERIKUTNYA (2026-09-14) ──",
           "// util - SAMA dengan Process All (dipakai penangkap jawaban di bawah)\n"
           + BERSIH_PA + "\n\n" + BLOK_BERSAMA
           + "// ── GALIAN BERIKUTNYA (2026-09-14) ──", "RK blok bersama")

rk = ganti(rk,
"""const pesanBertanya = /\\?|\\b(apa|apakah|gimana|gmn|bagaimana|berapa|brp|kenapa|knp|kapan|mana)\\b/i.test(pesanProspek);
""",
"""const pesanBertanya = /\\?|\\b(apa|apakah|gimana|gmn|bagaimana|berapa|brp|kenapa|knp|kapan|mana)\\b/i.test(pesanProspek);
// Fakta yang ada di pesan giliran ini (2026-09-23). Galian disusun SEBELUM Process All
// menyimpan jawaban giliran ini; tanpa ini VIRA menanyakan lagi yang barusan dijawab (uji
// 2026-09-23: "aku owner humanizer" dibalas "nama usahanya Humanizer itu sendiri ya kak, atau
// itu nama brand parfumnya?"). Penangkapnya identik dengan Process All dan urutannya sama
// (satu slot dulu, lalu jawaban perkenalan), jadi yang dianggap diketahui di sini = yang
// disimpan di sana. Hanya mengisi kolom yang masih kosong.
const faktaPesanIni = {};
if (!pesanPerkenalan && pesanProspek) {
  const lalu = [...ditanyaLalu];
  if (lalu.length === 1 && !txt(stats[lalu[0]])) {
    const v = ambilJawaban(lalu[0], pesanProspek);
    if (v) faktaPesanIni[lalu[0]] = BERSIH(v, 120);
  }
  if (ditanyaLalu.has('nama_lengkap') && ditanyaLalu.has('nama_bisnis')) {
    for (const [k, v] of Object.entries(ambilNamaDanUsaha(pesanProspek))) {
      if (!txt(stats[k]) && !faktaPesanIni[k]) faktaPesanIni[k] = BERSIH(v, 120);
    }
  }
  if (!txt(stats['volume_chat']) && !faktaPesanIni.volume_chat) {
    const vol = ambilVolumeSpontan(pesanProspek);
    if (vol) faktaPesanIni.volume_chat = vol;
  }
} else if (pesanPerkenalan && pesanProspek && KENALAN_DIRI.test(pesanProspek)) {
  // Pesan pertama yang memperkenalkan diri ("aku Rina dari Kopi Senja"): perkenalan hanya
  // menanyakan yang belum dia sebut - sama dengan penangkap di Process All.
  for (const [k, v] of Object.entries(ambilNamaDanUsaha(pesanProspek))) {
    if (!txt(stats[k])) faktaPesanIni[k] = BERSIH(v, 120);
  }
}
const statsGalian = { ...stats, ...faktaPesanIni };
for (const [k, v] of Object.entries(faktaPesanIni)) {
  barisProspek.push(`${k}: ${v} (baru dia sebut di pesan ini)`);
}
""", "RK faktaPesanIni")

# galian memakai statsGalian (STATS + fakta pesan ini)
rk = ganti(rk,
"""// karena ada giliran tanya ulang nama usaha: bidang 2-6, masalah 2-8, jumlah chat 3-10.
""",
"""// karena ada giliran tanya ulang nama usaha: bidang 2-6, masalah 2-8, jumlah chat 3-10.
// 2026-09-23: "cerita singkat" dibuang dari galian bidang usaha - satu hal per pertanyaan.
""", "RK komentar")
rk = ganti(rk,
"""      + 'lalu tanyakan bidang usahanya sekaligus minta cerita singkat',""",
"""      + 'lalu tanyakan bidang usahanya',""", "RK teks tanya ulang")
rk = ganti(rk,
"""  { kolom: 'industri',      teks: 'bidang usahanya, sekaligus minta dia cerita singkat tentang usahanya',""",
"""  { kolom: 'industri',      teks: 'bidang usahanya',""", "RK teks bidang")
rk = ganti(rk,
"""giliran >= 2 && giliran <= 8 && (!!txt(stats['industri']) || giliran > 6) },""",
"""giliran >= 2 && giliran <= 8 && (!!txt(statsGalian['industri']) || giliran > 6) },""", "RK masalah")
rk = ganti(rk,
"""giliran >= 3 && giliran <= 10 && !!txt(stats['masalah_utama']) },""",
"""giliran >= 3 && giliran <= 10 && !!txt(statsGalian['masalah_utama']) },""", "RK volume")
rk = ganti(rk,
"""  const kurang = GALIAN.filter(g => g.boleh() && !txt(stats[g.kolom])).map(g => g.teks);""",
"""  const kurang = GALIAN.filter(g => g.boleh() && !txt(statsGalian[g.kolom])).map(g => g.teks);""", "RK perkenalan")
rk = ganti(rk,
"""    if (txt(stats[g.kolom]) || !g.boleh()) continue;""",
"""    if (txt(statsGalian[g.kolom]) || !g.boleh()) continue;""", "RK loop")

import re as _re
_pa_rx = lambda pola: _re.search(pola, pa).group(1)
RX_NIAT_DECK = _pa_rx(r"const NIAT_DECK   = (/.+?/);\n")
RX_NIAT_BICARA = _pa_rx(r"const NIAT_BICARA = (/.+?/);\n")
RX_TAWARAN_DECK = _pa_rx(r"const TAWARAN_DECK  = (/.+?/)\.test\(BALASAN_LALU\);")
RX_SETUJU = _pa_rx(r"const SETUJU_PENDEK = PESAN_USER\.length <= 40\n  && (/.+?/)\.test\(PESAN_USER\);")
rk = ganti(rk,
"""if (galian) barisProspek.push(`galian_berikutnya: ${galian.teks}`);
""",
"""// Pesan ini MEMINTA / MENYETUJUI deck (2026-09-23). Regex disalin dari Process All (NIAT_DECK,
// TAWARAN_DECK, SETUJU_PENDEK, NIAT_BICARA - UAT memeriksa kesamaannya). Eval: dengan format
// "SATU kalimat tanya", model sempat membalas "boleh dong dibuatin deck" dengan menawarkan deck
// lagi, bukan mengabarkan briefnya sudah diteruskan. ALUR 8: giliran ini galian dilewati.
const pesanKecil = pesanProspek.toLowerCase().trim();
const mintaDeckPesan = !pesanPerkenalan && txt(stats['deck_requested']) !== 'Y'
  && (""" + RX_NIAT_DECK + """.test(pesanKecil)
      || (""" + RX_TAWARAN_DECK + """.test(String(stats['last_bot_reply'] || '').toLowerCase())
          && pesanKecil.length <= 40 && """ + RX_SETUJU + """.test(pesanKecil)))
  && !""" + RX_NIAT_BICARA + """.test(pesanKecil);
if (mintaDeckPesan) galian = null;
if (galian) barisProspek.push(`galian_berikutnya: ${galian.teks}`);
// Bentuk balasan giliran ini (2026-09-23) - ditaruh di data per giliran karena bagian ini
// yang paling dekat dengan saat model menulis, dan berubah mengikuti pesan prospek.
if (!pesanPerkenalan) {
  barisProspek.push(mintaDeckPesan
    ? 'format_balasan: dia MINTA / SETUJU dibuatkan deck — keluarkan [DECK_REQUEST] dan kabari briefnya '
      + 'sudah diteruskan ke Steven (lihat TAG), 1-2 kalimat; BUKAN pertanyaan dan BUKAN tawaran deck lagi'
    : pesanBertanya
    ? 'format_balasan: dia sedang BERTANYA — jawab langsung, maksimal 3 kalimat, tanpa merangkum pertanyaannya'
    : 'format_balasan: dia tidak sedang bertanya — cukup SATU kalimat tanya'
      // Eval 2026-09-23: dengan batas satu pertanyaan, model sempat memilih pertanyaan "akibat"
      // dan melewatkan galian tanya ulang nama usaha (yang dipakai di cover deck).
      + (galian ? ', dan pertanyaan itu adalah galian_berikutnya di atas (bukan pertanyaan lain)' : '')
      + ', boleh diawali pengakuan maksimal 4 kata; tanpa merangkum ucapannya dan tanpa menjelaskan VIRA. '
      + 'Kecuali balasan yang menawarkan deck atau mengabarkan brief sudah diteruskan (lihat TAG)');
}
""", "RK format_balasan")
rk = ganti(rk,
"""if (txt(stats['nama_lengkap'])) {""",
"""if (txt(statsGalian['nama_lengkap'])) {""", "RK panggilan")
rk = ganti(rk, "    deck_context,\n",
           "    deck_context,\n"
           "    // kolom galian giliran ini - dipakai jaring RINGKAS di Process All untuk memilih\n"
           "    // pertanyaan yang disisakan kalau model menulis lebih dari satu (2026-09-23)\n"
           "    galian_kolom: (galian && galian.kolom) || '',\n", "RK galian_kolom")
rk_node["jsCode"] = rk

# =========================================================================
# E. NODE BARU: IF Ringkas Dipangkas -> Log EVENTS Ringkas
# =========================================================================
if_node = copy.deepcopy(NODES["IF Unknown"])
if_node["name"] = "IF Ringkas Dipangkas"
if_node["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "vira-personal/v3.12/if-ringkas"))
if_node["position"] = [-91408, 1216]
kond = if_node["parameters"]["conditions"]["conditions"][0]
kond["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "vira-personal/v3.12/if-ringkas/kondisi"))
kond["leftValue"] = "={{ $json.needs_ringkas_log }}"

log_node = copy.deepcopy(NODES["Log EVENTS Delegated"])
log_node["name"] = "Log EVENTS Ringkas"
log_node["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "vira-personal/v3.12/log-ringkas"))
log_node["position"] = [-91184, 1216]
log_node["maxTries"] = 2
log_node["waitBetweenTries"] = 3000
log_node["onError"] = "continueRegularOutput"
log_node["parameters"]["columns"]["value"] = {
    "no_wa": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "nama": "={{ $('Process All').first().json.nama_lengkap_merged || $('Chat Counter').first().json.user_name }}",
    "event": "RINGKAS",
    "detail": "={{ 'dipangkas: ' + $('Process All').first().json.ringkas"
              " + ' | terkirim: ' + $('Process All').first().json.cleanOutput"
              " + ' | asli: ' + String($('Process All').first().json.ringkas_asli || '').slice(0, 600) }}",
    "ts": "={{ Math.floor(Date.now()/1000) }}",
}
wf["nodes"].extend([if_node, log_node])

conns = wf["connections"]
conns["Process All"]["main"][0].append({"node": "IF Ringkas Dipangkas", "type": "main", "index": 0})
conns["IF Ringkas Dipangkas"] = {"main": [[{"node": "Log EVENTS Ringkas", "type": "main", "index": 0}]]}

# =========================================================================
# F. SETTINGS
# =========================================================================
wf["settings"]["availableInMCP"] = True

with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8") as f:
    f.write(sp[1:] if sp.startswith("=") else sp)

print("OK ->", os.path.basename(DST), "| node:", len(wf["nodes"]))
print("OK ->", os.path.basename(MD), "| prompt:", len(sp), "karakter")
