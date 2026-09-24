# -*- coding: utf-8 -*-
"""
_patch_2026-09-23b.py - v3.13: harga VIRA hanya kalau ditanya, jawaban alur tidak lagi dibaca
sebagai pertanyaan harga, "usahaku sewa X" tidak lagi jadi nama usaha.

Masukan : 2026-09-23-VIRA-Personal-Main-v3.12.json   (= live, dicek MCP 2026-09-23 12:19 WIB; tidak diubah)
Keluaran: 2026-09-23-VIRA-Personal-Main-v3.13.json
          2026-09-23-system-prompt-VIRA-Personal-v3.13.md

UJI LIVE STEVEN 2026-09-23 13:22-13:45 (nomor sendiri, berperan "Rehan", sewa raket padel)
  MSG_BUFFER : Halo VIRA, aku lihat website-nya ... / rehan / usahaku sewa raket padel /
               persewaan aja sih / balesin chat 1 1 sih / suka tenggelem / 10-20 an /
               gimana prosedurnya dan lain-lain / harga dulu, trs klo udah aman baru ke payment / okee
  EVENTS 13:42 RINGKAS "tanya-ulang", asli:
      "Oh itu alur bisnis kakak yang dia ceritakan kak, bukan nanya harga VIRA. Noted. Kalau kakak
       nanya harga VIRA, kisarannya: Basic mulai Rp3.000.000 per bulan, Premium Rp5.000.000 per
       bulan, setup-nya sekarang gratis. Angka finalnya menyesuaikan kompleksitas alur bisnis
       kakak, jadi nanti dibicarakan langsung sama Steven. Dari chat sampai akhirnya jadi sewa,
       biasanya lewat langkah apa aja kak?"
      terkirim: sama, tanpa pertanyaan terakhir (48 kata).
  STATS 13:44 last_bot_reply (sesudah "okee"): "Dari chat sampai akhirnya jadi sewa, biasanya
      lewat langkah apa aja kak?" - pertanyaan yang sudah dia jawab.
  STATS: nama_bisnis = "sewa raket padel", industri = "persewaan aja".
Cacat:
  1. Preprocess: "harga" di jawaban ALUR menyalakan konteks harga (tidak ada gerbang untuk
     jawaban atas pertanyaan kita sendiri). Model mengutip catatan itu dan menyebut harga.
  2. Process All: jaring RINGKAS melewati balasan yang menyebut Rp/basic/premium/Steven
     (LEWATI_RINGKAS), jadi harga yang tidak ditanya lolos; tanya-ulang malah membuang
     satu-satunya bagian yang relevan.
  3. Penangkap: "usahaku sewa raket padel" -> nama_bisnis (sewa/persewaan tidak dikenal sebagai
     jenis usaha); EKOR hanya membuang SATU kata ekor -> industri "persewaan aja".

ISI PATCH
  A. Preprocess: gerbang JAWAB_PERTANYAANKU - kalimat tanya di last_bot_reply (teks yang benar-
     benar terkirim) menanyakan alur/langkah penjualannya atau apa yang biasa ditanyakan
     pelanggannya, dan pesannya tanpa "?" -> bukan pertanyaan harga (kecuali ditujukan ke kita:
     vira/kamu/kalian/...). Keluaran baru `hargaBukanTanya`. Catatan konteks harga: + contoh alur,
     + "jangan dikutip, jangan dikomentari".
  B. Prompt # HARGA: satu kalimat - alur penjualan ("harga dulu, terus ... transfer") bukan
     pertanyaan harga; jangan menyinggung harga VIRA dan jangan mengomentarinya.
  C. Process All: jaring HARGA TANPA DITANYA sebelum RINGKAS - di giliran yang prospeknya tidak
     bertanya dan tidak menanyakan harga, kalimat PERNYATAAN yang menyebut harga VIRA dibuang
     (kalimat tanya tidak pernah). Alasan 'gema' kini ditambahkan, bukan menimpa.
  D. Penangkap (blok bersama, identik di Process All & Rakit Konteks):
     - DAGANGAN + sewa/nyewa*/menyewakan/persewaan/penyewaan; JENIS_USAHA + sewa/persewaan/penyewaan
       -> "usahaku sewa raket padel" = industri, nama usahanya ditanya ulang.
     - Jawaban atas pertanyaan nama usaha: dagangan ("sewa raket padel aja") dan "gaada/blm/ngga ..."
       bukan nama.
     - Dagangan yang SEMUA katanya berhuruf besar ("Sewa Raket Padel", "Persewaan Tenda Berkah")
       tetap dianggap nama merek, di perkenalan maupun di jawaban pertanyaan nama usaha.
     - EKOR_SEMUA untuk industri & jumlah chat: "persewaan aja sih" -> "persewaan".
       Nama usaha tetap memakai EKOR (satu kata): "X aja sih" sengaja ditolak BUKAN_NAMA_USAHA.
     - "rental" / "jasa" SENGAJA tidak ditambahkan ke DAGANGAN: "Rental Mobil Jaya" nama usaha asli.
  E. settings.errorWorkflow = 0mp_AdLtInm68RxQUwLqV (GLOBAL notifier, sama dengan live).

LANJUTAN UJI LIVE STEVEN (masih v3.12) 13:58-14:06, sesudah deck dikirim 13:53:
  "basic deh" -> notif admin "BRIEF DECK (diperbarui) ... DECK SIAP DIGENERATE" (30 baris) lagi.
  "kpn y bs ngmngnya?" (14:00) -> tidak pernah sampai ke MSG_BUFFER (temuan terpisah, lihat log n8n).
  "kpn bs ngmng sm steven?" -> [TALK_TO_ADMIN] keluar (notif terkirim), tapi bot TIDAK dimatikan
      (NIAT_BICARA tidak kenal "ngmng"/"sm") dan balasannya "Mau aku sambungkan...?".
KEPUTUSAN STEVEN 2026-09-23: gabung ke v3.13; permintaan bicara yang jelas -> langsung disambungkan;
sesudah deck terkirim cukup notif singkat "update prospek".
  F. Handover: NIAT_BICARA (+ salinannya di Rakit Konteks) mengenali bahasa chat yang diarahkan ke
     Steven; "kapan bisa ngomong..." dihitung kalau pesan / balasan terakhir menyebut Steven; model
     lupa tag -> handover dinyalakan dari kode (hanya untuk permintaan, bukan pertanyaan identitas);
     TAWARAN_DISKUSI + tawaran "sambungkan"; saat bot dimatikan, pertanyaan "mau aku sambungkan?"
     dibuang dan kalimat konfirmasi dipastikan ada. Prompt # TAG: satu kalimat.
  G. Merge Brief: sesudah deck terkirim (REQUESTS.deck_dikirim_ts / STATS.deck_terkirim_ts), notif
     hanya "UPDATE PROSPEK" singkat berisi isian baru / perubahan komersial; tidak ada -> tanpa notif.

TEMUAN EVAL MODEL ASLI v3.13 putaran 1 (ikut diperbaiki):
  H1. Prospek menyebut nama usaha tanpa ditanya, model mencatatnya di [FACTS], tapi jaring tetap
      menempelkan "Oh iya, nama usahanya apa kak?" (galian disusun sebelum giliran ini tersimpan).
      -> pertanyaan galian hanya ditempel kalau kolomnya MASIH kosong (GALIAN_TERBUKA).
  H2. "boleh dong dibuatin deck" -> brief diteruskan, tapi balasannya menawarkan deck lagi.
      -> tawaran deck di giliran itu dibuang; kalimat kabar ditambahkan kalau belum ada.
  H3. (putaran 2) "persewaan aja sih" -> model menulis [FACTS nama_bisnis="persewaan"]; [FACTS] selalu
      menang atas penangkap. -> nama usaha dari [FACTS] / blok brief yang cuma jenis usaha / dagangan
      huruf kecil tidak disimpan sebagai nama (pindah ke industri kalau kosong).

Node yang diubah: AI Agent, Preprocess - Context Detection, Process All, Rakit Konteks, Merge Brief.
Node & koneksi baru: tidak ada. 86 node lain identik.

Jalankan: python _patch_2026-09-23b.py
"""
import io
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.12.json")
DST = os.path.join(DIR, "2026-09-23-VIRA-Personal-Main-v3.13.json")
MD = os.path.join(DIR, "2026-09-23-system-prompt-VIRA-Personal-v3.13.md")

with io.open(SRC, encoding="utf-8") as f:
    wf = json.load(f)

NODES = {n["name"]: n for n in wf["nodes"]}


def ganti(teks, lama, baru, label):
    n = teks.count(lama)
    assert n == 1, "%s: pola ditemukan %d kali (harus 1)" % (label, n)
    return teks.replace(lama, baru)


# =========================================================================
# A. PREPROCESS - jawaban atas pertanyaanku bukan pertanyaan harga
# =========================================================================
pre_node = NODES["Preprocess - Context Detection"]["parameters"]
pre = pre_node["jsCode"]

pre = ganti(pre,
r"""const askingPrice = TANYA_HARGA_KITA
  || (KATA_HARGA.test(message) && !CERITA_ORANG_LAIN && !MILIK_DIA)
  || (/\bberapa\b[^?]{0,20}\b(harga|biaya|duit|rupiah|bulan|bulanan)/i.test(message)
      && !CERITA_ORANG_LAIN && !MILIK_DIA);
""",
r"""// ── JAWABAN ATAS PERTANYAANKU (2026-09-23, v3.13) ──
// Uji Steven 2026-09-23 13:41 ("Rehan", sewa raket padel). VIRA bertanya "Dari chat sampai
// akhirnya jadi sewa, biasanya lewat langkah apa aja kak?", dia menjawab "harga dulu, trs klo
// udah aman baru ke payment". Kata `harga` di situ bagian ALUR PENJUALANNYA - tapi tidak ada kata
// tanya pelanggan (CERITA_ORANG_LAIN) dan bukan angka miliknya (MILIK_DIA), jadi konteks harga
// menyala. VIRA lalu mengutip catatan itu ("Oh itu alur bisnis kakak yang dia ceritakan kak,
// bukan nanya harga VIRA") dan tetap menyebut Basic/Premium tanpa ditanya.
// Gerbang ketiga: pesan ini MENJAWAB pertanyaanku soal alur penjualannya, atau soal apa yang biasa
// ditanyakan pelanggannya (uji 21/09 Jacob: "Harga sewa, cara sewa, ongkir berapa"). Sumbernya
// kalimat tanya di last_bot_reply - teks yang BENAR-BENAR terkirim. Pesan yang memuat "?" tidak
// pernah dianggap jawaban, dan pertanyaan yang jelas ditujukan ke kita ("harga vira berapa",
// "paket kalian") tetap menyalakan konteks harga. Pertanyaanku yang menawarkan penjelasan
// ("mau aku jelasin alur kerja VIRA?") bukan pertanyaan alur penjualannya.
const BALASAN_LALU = (() => {
  try { return String($('Resolve User Row').first().json.last_bot_reply || '').toLowerCase(); }
  catch (e) { return ''; }
})();
const TANYA_LALU = BALASAN_LALU.match(/[^.?!\n]+\?/g) || [];
const tanyaAlur = (k) => /\b(langkah|alur|tahap)\w*\b|\bsampai\s+(jadi|akhirnya)\b/.test(k)
  && /\b(biasanya|pelanggan|customer|pembeli|calon|closing)\b|\bdari\s+chat\b|\bchat\s+(pertama|masuk)\b|\bsampai\s+(jadi|akhirnya)\b/.test(k)
  && !/\b(vira|jelas\w*)\b/.test(k);
const tanyaPertanyaanPelanggan = (k) =>
     /\b(sering|paling|biasanya|banyak)\b[^?]{0,25}\bditanya\w*/.test(k)
  || /\b(pelanggan|customer|pembeli|konsumen|klien|calon|mereka|orang|murid|pasien|penyewa)\w*\b[^?]{0,30}\b(nanya|tanya)\w*/.test(k)
  || /\bpertanyaan\w*\b[^?]{0,25}\b(sering|tersering|paling)\b/.test(k);
const JAWAB_PERTANYAANKU = !/\?/.test(message)
  && TANYA_LALU.some(k => tanyaAlur(k) || tanyaPertanyaanPelanggan(k));
const MENYEBUT_KITA = /\b(vira|kamu|kalian|lo|lu|situ|steven)\b/.test(message);
const BUKAN_TANYA_HARGA = CERITA_ORANG_LAIN || MILIK_DIA || JAWAB_PERTANYAANKU;

const askingPrice = (TANYA_HARGA_KITA && !(JAWAB_PERTANYAANKU && !MENYEBUT_KITA))
  || (KATA_HARGA.test(message) && !BUKAN_TANYA_HARGA)
  || (/\bberapa\b[^?]{0,20}\b(harga|biaya|duit|rupiah|bulan|bulanan)/i.test(message)
      && !BUKAN_TANYA_HARGA);
// Pesan menyebut harga, tapi gerbang di atas memutuskan dia TIDAK menanyakan harga VIRA.
// Process All memakainya untuk membuang kalimat harga VIRA yang tidak ditanya (v3.13).
const hargaBukanTanya = !askingPrice && (KATA_HARGA.test(message)
  || /\bberapa\b[^?]{0,20}\b(harga|biaya|duit|rupiah|bulan|bulanan)/i.test(message));
""", "PRE askingPrice")

pre = ganti(pre,
"""if (askingPrice) aiContext += 'Sepertinya dia menanyakan harga. Periksa dulu pesannya: kalau dia memang menanyakan harga VIRA, sebut kisaran dari DATA PRODUK lalu arahkan ke Steven untuk angka final. Kalau kata harga muncul karena dia sedang menceritakan pertanyaan pelanggannya sendiri atau menyebut angka bisnisnya sendiri, JANGAN sebut angka apa pun. Jangan menawar, jangan memberi diskon. ';
""",
"""// 2026-09-23 (v3.13): + alur penjualan, dan larangan mengutip catatan ini - model sempat menulis
// "Oh itu alur bisnis kakak yang dia ceritakan kak, bukan nanya harga VIRA" ke prospek.
if (askingPrice) aiContext += 'Sepertinya dia menanyakan harga. Periksa dulu pesannya: kalau dia memang menanyakan harga VIRA, sebut kisaran dari DATA PRODUK lalu arahkan ke Steven untuk angka final. Kalau kata harga muncul karena dia sedang menceritakan pertanyaan pelanggannya sendiri, alur penjualannya ("harga dulu, terus transfer"), atau angka bisnisnya sendiri, JANGAN sebut angka apa pun dan jangan menyinggung harga VIRA sama sekali. Jangan menawar, jangan memberi diskon. Catatan ini hanya untukmu: jangan dikutip, jangan dikomentari di balasan. ';
""", "PRE aiContext harga")

pre = ganti(pre, "  askingPrice,\n", "  askingPrice,\n  hargaBukanTanya,\n", "PRE keluaran")
pre_node["jsCode"] = pre


# =========================================================================
# B. PROMPT # HARGA
# =========================================================================
agent = NODES["AI Agent"]["parameters"]["options"]
sp = agent["systemMessage"]
sp = ganti(sp,
"""500rb”): itu jawaban atas pertanyaanku, bukan pertanyaan tentang paket.
""",
"""500rb”): itu jawaban atas pertanyaanku, bukan pertanyaan tentang paket.
Sama halnya waktu dia menceritakan alur penjualannya (“harga dulu, terus kalau cocok baru
transfer”): itu jawaban soal alurnya — jangan menyinggung harga VIRA sama sekali, dan jangan
mengomentari bahwa itu bukan pertanyaan harga.
""", "PROMPT HARGA alur")
agent["systemMessage"] = sp


# =========================================================================
# D. PENANGKAP JAWABAN - blok bersama, identik di dua node
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
assert blok_lama == blok(rk), "blok penangkap v3.12 tidak identik di dua node"
b = blok_lama

b = ganti(b,
r"""const EKOR = /[\s,]+(kak|ka|kakak|ya|yaa|sih|kok|deh|aja|saja)\s*$/i;
""",
r"""const EKOR = /[\s,]+(kak|ka|kakak|ya|yaa|sih|kok|deh|aja|saja)\s*$/i;
// SEMUA kata ekor di ujung, bukan cuma satu (uji 2026-09-23 "Rehan": "persewaan aja sih" tersimpan
// sebagai industri "persewaan aja"). Hanya untuk bidang usaha & jumlah chat. Nama usaha tetap
// memakai EKOR: di sana "X aja sih" sengaja ditolak BUKAN_NAMA_USAHA (artinya: belum ada nama).
const EKOR_SEMUA = /(?:[\s,]+(?:kak|ka|kakak|ya|yaa|sih|kok|deh|aja|saja))+\s*$/i;
""", "BLOK EKOR_SEMUA")

b = ganti(b,
r"""    if (/^(belum|masih|rahasia|nanti|gak|nggak|tidak|kok)\b/i.test(s)) return '';
    if (BUKAN_NAMA_USAHA.test(s) || NAMA_USAHA_MUSTAHIL.test(s) || VOLUME_SPONTAN.test(s)) return '';   // 2026-09-23
""",
r"""    if (/^(belum|blm|masih|rahasia|nanti|gak|ga|gk|nggak|ngga|tidak|tdk|gaada|gada|nggada|tanpa|kok)\b/i.test(s)) return '';
    if (BUKAN_NAMA_USAHA.test(s) || NAMA_USAHA_MUSTAHIL.test(s) || VOLUME_SPONTAN.test(s)) return '';   // 2026-09-23
    // Dagangan ("sewa raket padel aja", "jualan kue") menjawab APA usahanya, bukan namanya
    // (v3.13). Sesudah "usahaku sewa raket padel" masuk industri, nama usahanya ditanya ulang;
    // jawaban seperti ini tidak boleh jadi cover deck. Hanya untuk jawaban atas pertanyaan nama
    // usaha saja: jawaban perkenalan (ambilNamaDanUsaha) memindahkan dagangan ke industri.
    // Semua kata berhuruf besar ("Sewa Kamera Jogja", "Persewaan Tenda Berkah") = nama merek.
    if (!dariPerkenalan && DAGANGAN.test(s) && !HURUF_BESAR_SEMUA(s)) return '';
""", "BLOK nama usaha")

b = ganti(b, "const ambilJawaban = (kolom, pesan) => {\n",
          "const ambilJawaban = (kolom, pesan, dariPerkenalan) => {\n", "BLOK ambilJawaban param")
b = ganti(b, "    const isi = ambilJawaban('nama_bisnis', bersih);\n",
          "    const isi = ambilJawaban('nama_bisnis', bersih, true);\n", "BLOK perkenalan panggil")

b = ganti(b,
r"""      .replace(/^(bergerak\s+)?(di\s+)?(bidang|industri|sektor)\s+/i, '')
      .replace(EKOR, '').trim();
""",
r"""      .replace(/^(bergerak\s+)?(di\s+)?(bidang|industri|sektor)\s+/i, '')
      .replace(EKOR_SEMUA, '').trim();
""", "BLOK industri ekor")

b = ganti(b,
r"""    const s = baris1.replace(EKOR, '').trim();
""",
r"""    const s = baris1.replace(EKOR_SEMUA, '').trim();
""", "BLOK volume ekor")

b = ganti(b,
r"""  return baris ? BERSIH(baris.replace(LEPAS_AWAL, '').replace(EKOR, ''), 120) : '';
""",
r"""  return baris ? BERSIH(baris.replace(LEPAS_AWAL, '').replace(EKOR_SEMUA, ''), 120) : '';
""", "BLOK volume spontan ekor")

b = ganti(b, "percetakan|konveksi|bengkel|rental|properti|",
          "percetakan|konveksi|bengkel|rental|sewa|persewaan|penyewaan|properti|", "BLOK JENIS_USAHA")

b = ganti(b,
r"""const DAGANGAN = /^(jualan|jual)\s+\S/i;
""",
r"""// v3.13 (uji 2026-09-23 "Rehan"): "usahaku sewa raket padel" tersimpan sebagai NAMA usaha.
// Kata kerja sewa/menyewakan dan persewaan/penyewaan = jenis usaha -> industri, nama ditanya ulang.
// "rental" / "jasa" sengaja TIDAK di sini: "Rental Mobil Jaya" / "Jasa Kirim Cepat" nama asli.
// Dagangan yang SEMUA katanya diawali huruf besar ("Sewa Raket Padel", "Persewaan Tenda Berkah")
// diperlakukan sebagai nama merek. Keyboard HP hanya membesarkan huruf pertama pesan, jadi
// "Sewa raket padel" tetap dagangan.
const DAGANGAN = /^(jualan|jual|sewa|nyewa|nyewain|nyewakan|menyewakan|persewaan|penyewaan)\s+\S/i;
const HURUF_BESAR_SEMUA = (s) => String(s || '').split(/\s+/).filter(Boolean).every(w => /^[\p{Lu}\d]/u.test(w));
""", "BLOK DAGANGAN")

b = ganti(b,
r"""    if (JENIS_USAHA.test(isi) || DAGANGAN.test(isi)) { if (!hasil.industri) hasil.industri = isi; continue; }
""",
r"""    if (JENIS_USAHA.test(isi) || (DAGANGAN.test(isi) && !HURUF_BESAR_SEMUA(isi))) { if (!hasil.industri) hasil.industri = isi; continue; }
""", "BLOK perkenalan dagangan")

pa = pa.replace(blok_lama, b)
rk = rk.replace(blok_lama, b)
assert blok(pa) == blok(rk) == b


# =========================================================================
# C. PROCESS ALL - jaring HARGA TANPA DITANYA
# =========================================================================
pa = ganti(pa,
"""  if (kal.length < jumlahAwal) ringkasAlasan = 'gema';
""",
"""  if (kal.length < jumlahAwal) ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+gema' : 'gema';
""", "PA gema ditambahkan")

HARGA = r"""// ── HARGA TANPA DITANYA (2026-09-23, v3.13) ──
// Uji Steven 2026-09-23 13:42 ("Rehan", sewa raket padel): jawaban alur "harga dulu, trs klo udah
// aman baru ke payment" dibalas "Oh itu alur bisnis kakak yang dia ceritakan kak, bukan nanya harga
// VIRA. Noted. Kalau kakak nanya harga VIRA, kisarannya: Basic mulai Rp3.000.000 per bulan, ...
// Angka finalnya ... dibicarakan langsung sama Steven. <pertanyaan>" - 48 kata. Jaring RINGKAS di
// bawah melewatinya karena LEWATI_RINGKAS (Rp / basic / premium / Steven + langsung).
// Keputusan Steven 2026-09-23: harga & promosi VIRA hanya kalau ditanya (prompt # HARGA: "Jangan
// pernah menyebut angkanya lebih dulu - termasuk saat menawarkan deck").
// Jalan kalau prospek TIDAK bertanya (PROSPEK_BERTANYA), Preprocess memutuskan dia TIDAK menanyakan
// harga (askingPrice), dan pesannya tidak menyinggung uang sama sekali ATAU Preprocess yakin kata
// harganya milik cerita dia sendiri (hargaBukanTanya: cerita pelanggan, angka bisnisnya, jawaban
// soal alur). Pesan yang menyinggung uang tanpa terbaca bertanya ("budgetku 2jt cukup ga") tidak
// disentuh - jawaban harga lebih baik lolos daripada terpotong.
// Yang dibuang HANYA kalimat pernyataan yang menyebut harga VIRA. Kalimat tanya tidak pernah
// (pertanyaan soal harga/nilai transaksi DIA sah). Kalau semua kalimatnya pernyataan harga,
// balasan dibiarkan - tidak pernah mengirim teks kosong.
const KALIMAT_HARGA_VIRA = /\brp\.?\s?\d|\d\s?(rb|ribu|jt|juta)\b|\b(basic|premium)\b[^.?!\n]{0,40}\b(mulai|rp|per\s*bulan|sebulan|bulanan)\b|\bsetup\b[^.?!\n]{0,25}\bgratis\b|\b(angka|harga)\s+(final|pasti)\w*|\b(harga|biaya|tarif|kisaran)\w*\b[^.?!\n]{0,20}\b(vira|paket\w*|langganan)\b|\b(vira|paket\w*|langganan)\b[^.?!\n]{0,20}\b(harga|biaya|tarif|kisaran)\w*/i;
const UANG_DISINGGUNG = /\b(harga|hrg|biaya|tarif|langganan|paket|basic|premium|mahal|murah|diskon|setup|nego|pricelist|budget|bujet|anggaran|duit|uang|dana|bayar)\w*|\bprice\s?list|\brp\.?\s?\d|\d\s?(rb|ribu|k|jt|juta)\b/i.test(PESAN_USER);
const hargaTakDitanya = !(preprocess && preprocess.askingPrice === true)
  && (!UANG_DISINGGUNG || (preprocess && preprocess.hargaBukanTanya === true));
if (!cadangan && !isNewUser && !PROSPEK_BERTANYA && hargaTakDitanya && !mintaDeck
    && !isTalkToAdmin && !isUnknown && !isSendMedia && !replyOverridden) {
  const kal = pecahKalimat(cleanOutput);
  const sisa = kal.filter(k => /\?/.test(k) || !KALIMAT_HARGA_VIRA.test(k));
  if (sisa.length && sisa.length < kal.length) {
    cleanOutput = sisa.join(' ').replace(/^([a-z])/, (m) => m.toUpperCase());
    ringkasAlasan = 'harga';
    console.log('HARGA tanpa ditanya: ' + (kal.length - sisa.length) + ' kalimat harga VIRA dibuang');
  }
}
"""
pa = ganti(pa, "let ringkasAlasan = cadangan;\n", "let ringkasAlasan = cadangan;\n" + HARGA, "PA HARGA")


# =========================================================================
# F. HANDOVER - permintaan bicara dengan Steven langsung disambungkan
# =========================================================================
import re as _re
NIAT_LAMA = _re.search(r"const NIAT_BICARA = (/.+?/);\n", pa).group(1)
assert rk.count(NIAT_LAMA) == 1, "salinan NIAT_BICARA di Rakit Konteks tidak tunggal"
# Kata kerja bicara (termasuk singkatan chat) yang langsung diarahkan ke Steven.
NIAT_STEVEN = (r"\b(ngobrol|ngbrl|ngobrl|ngomong|ngmng|ngmg|omong|bicara|bcr|diskusi|telpon|telepon|telp|telfon"
               r"|call|chat|hubungi|kontak)\w*\s+((langsung|lgsg|lgsung)\s+)?((sama|sm|ama|dgn|dg|dengan|ke)\s+)?stev")
NIAT_BARU = NIAT_LAMA[:-1] + "|" + NIAT_STEVEN + "/"
pa = ganti(pa, "const NIAT_BICARA = " + NIAT_LAMA + ";\n",
           "// v3.13 (uji live 2026-09-23 14:05): + bahasa chat yang langsung diarahkan ke Steven\n"
           "// (\"kpn bs ngmng sm steven?\", \"hubungi steven\") - dulu tidak dikenali, bot tidak dimatikan.\n"
           "const NIAT_BICARA = " + NIAT_BARU + ";\n", "PA NIAT_BICARA")
rk = ganti(rk, NIAT_LAMA, NIAT_BARU, "RK NIAT_BICARA (salinan)")

pa = ganti(pa,
r"""const TAWARAN_DISKUSI = /\b(diskusi|ngobrol|bicara|ngomong|meeting|ketemu|jadwal\w*|telepon|telpon|call)\b[^.?!\n]{0,40}\b(steven|langsung|aslinya|orangnya)\b|\b(steven|langsung|orangnya)\b[^.?!\n]{0,40}\b(diskusi|ngobrol|bicara|ngomong|meeting|ketemu)\b/.test(BALASAN_LALU);
""",
r"""// v3.13: + tawaran menyambungkan ("Mau aku sambungkan supaya dia langsung menghubungi kakak?",
// uji live 2026-09-23 14:06) - dulu jawaban "iya" atas kalimat itu tidak dianggap setuju.
const TAWARAN_DISKUSI = /\b(diskusi|ngobrol|bicara|ngomong|meeting|ketemu|jadwal\w*|telepon|telpon|call)\b[^.?!\n]{0,40}\b(steven|langsung|aslinya|orangnya)\b|\b(steven|langsung|orangnya)\b[^.?!\n]{0,40}\b(diskusi|ngobrol|bicara|ngomong|meeting|ketemu)\b|\b(di)?(sambung|nyambung)\w*\b[^.?!\n]{0,40}\b(steven|dia)\b|\bsteven\b[^.?!\n]{0,40}\b(di)?(sambung|nyambung)\w*/.test(BALASAN_LALU);
""", "PA TAWARAN_DISKUSI")

pa = ganti(pa,
"""const mintaBicara = (preprocess && preprocess.wantsHuman === true)
                  || NIAT_BICARA.test(PESAN_USER)
                  || SETUJU_DISKUSI;
""",
r"""// ── Minta bicara dengan Steven dalam bahasa chat (2026-09-23, v3.13) ──
// Uji live Steven 14:00-14:06, sesudah VIRA bilang "Nanti Steven yang bantu bahas detailnya
// langsung": "kpn y bs ngmngnya?" lalu "kpn bs ngmng sm steven?". Yang kedua membuat model menulis
// [TALK_TO_ADMIN] (notif terkirim), tapi NIAT_BICARA tidak mengenali "ngmng"/"sm", jadi bot TIDAK
// dimatikan dan VIRA membalas "Mau aku sambungkan...?". Keputusan Steven 2026-09-23: permintaan yang
// jelas langsung disambungkan - bot OFF, notif, balasan mengonfirmasi. Dua pola, keduanya sempit:
//   - PERMINTAAN (mau/bisa/bs/kapan/tolong/... tepat di depannya) + kata kerja bicara (termasuk
//     singkatan) yang langsung diarahkan ke Steven: "kpn bs ngmng sm steven?", "mau hubungi steven";
//   - "kapan bisa ngobrol / ngomong / call / dihubungi" - HANYA kalau pesan ini atau balasan
//     terakhirku menyebut Steven.
// Kalau model lupa menulis tag, handover dinyalakan dari sini (sama dengan SETUJU_DISKUSI).
// Tidak pernah dinyalakan dari sini: pesan yang menolak ("ga usah ngobrol sama steven") dan
// pertanyaan identitas ("ini lagi chat sama steven?", "beneran steven atau bot?") - tanpa kata
// permintaan, atau memuat bot/AI/beneran. Yang itu tetap diputuskan model (bagian IDENTITAS).
const MINTA_STEVEN = /\b(mau|pengen|pgn|pingin|ingin|minta|bisa|bs|boleh|tolong|kapan|kpn|gimana|gmn|cara|butuh|perlu)\b[^.?!\n]{0,12}""" + NIAT_STEVEN + r"""/;
const TANYA_KAPAN_BICARA = /\b(kapan|kpn)\b[^.?!\n]{0,20}\b(ngobrol|ngbrl|ngomong|ngmng|ngmg|omong|bicara|diskusi|call|telpon|telepon|telp|ketemu|meeting|zoom|dihubungi|hubungi)\w*/;
const NEGASI_BICARA = /\b(ga|gak|nggak|ngga|gk|tidak|tdk|jangan|belum|blm)\b[^.?!\n]{0,15}\b(ngobrol|ngbrl|ngomong|ngmng|ngmg|omong|bicara|diskusi|telpon|telepon|telp|call|chat|hubungi|kontak|ketemu)/;
const TANYA_IDENTITAS = /\b(beneran|bneran|bot|robot|ai)\b/;
const mintaSteven = !NEGASI_BICARA.test(PESAN_USER) && !TANYA_IDENTITAS.test(PESAN_USER)
  && (MINTA_STEVEN.test(PESAN_USER)
      || (TANYA_KAPAN_BICARA.test(PESAN_USER) && (/\bstev/.test(PESAN_USER) || /\bsteven\b/.test(BALASAN_LALU))));
if (mintaSteven && !mintaDeck && !isTalkToAdmin) {
  console.warn('Prospek minta bicara dengan Steven tapi model tidak menulis [TALK_TO_ADMIN]. '
             + 'Handover dinyalakan dari gerbang deterministik: ' + PESAN_USER.slice(0, 120));
  isTalkToAdmin = true;
}

const mintaBicara = (preprocess && preprocess.wantsHuman === true)
                  || NIAT_BICARA.test(PESAN_USER)
                  || SETUJU_DISKUSI
                  || mintaSteven;
""", "PA mintaSteven")

HANDOVER = r"""// ── HANDOVER: balasan wajib mengonfirmasi (2026-09-23, v3.13) ──
// Uji live Steven 14:06: [TALK_TO_ADMIN] keluar (Steven sudah dinotifikasi) tapi balasannya "Steven
// biasanya balas begitu sedang online kak. Mau aku sambungkan supaya dia langsung menghubungi
// kakak?" - prospek ditanya lagi padahal sudah disambungkan. Keputusan Steven 2026-09-23: permintaan
// yang jelas langsung disambungkan. Kalau bot dimatikan (matikanBot):
//  - model MENULIS tag: kalimat tanya yang menawarkan menyambungkan dibuang, dan kalimat
//    konfirmasi ditambahkan di depan kalau belum ada. Kalimat lain tidak disentuh.
//  - handover dinyalakan KODE (model tidak menulis tag - mintaSteven / SETUJU_DISKUSI): teks model
//    tidak ditulis untuk handover ("Kalau ada yang mau ditanyakan, aku di sini"), jadi balasannya
//    diganti utuh dengan kalimat konfirmasi.
const KALIMAT_HANDOVER = 'Siap kak, sudah aku sambungkan ke Steven. Dia yang akan menghubungi kakak langsung di nomor ini ya.';
const KONFIRMASI_HANDOVER = /\b(sudah|udah|sdh)\b[^.?!\n]{0,25}\b(aku\s+)?(sambung|terus|teruskan|kabar|hubung|sampai)\w*|\baku\s+(sambung|terus|sampai|kabar)\w*\s+(ke\s+)?steven|\bsteven\b[^.?!\n]{0,40}\b(akan|bakal|segera|nanti)\b[^.?!\n]{0,20}\b(menghubungi|hubungi|kontak|chat|telpon|telepon)\w*/i;
const TAWAR_SAMBUNG = /\b(mau|boleh|perlu|gimana|bagaimana|oke|ok|setuju)\b[^?]{0,40}\b(di)?(sambung|hubung|terus|kontak|telpon|telepon|call)\w*/i;
// Sapaan pendek ("Siap kak.", "Boleh banget kak.") dibuang kalau kalimat konfirmasi ditambahkan di
// depan - tanpa ini jadinya "Siap kak, sudah aku sambungkan ... Siap kak." (dipakai juga blok DECK).
const SAPAAN_PENDEK = /^(boleh|siap|oke|ok|okay|baik|sip|noted|tentu|bisa)\b[^.?!]{0,20}[.!]?$/i;
if (matikanBot) {
  const kal = pecahKalimat(cleanOutput);
  const sisa = kal.filter(k => !(/\?/.test(k) && TAWAR_SAMBUNG.test(k)));
  const hasilHandover = !aiOutput.includes('[TALK_TO_ADMIN]') ? KALIMAT_HANDOVER   // = isTalkToAdmin awal
    : (sisa.some(k => KONFIRMASI_HANDOVER.test(k)) ? sisa
       : [KALIMAT_HANDOVER, ...sisa.filter(k => !SAPAAN_PENDEK.test(k))]).join(' ').trim();
  if (hasilHandover !== kal.join(' ')) {
    cleanOutput = hasilHandover;
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+handover' : 'handover';
    console.log('HANDOVER: balasan dipastikan mengonfirmasi, tawaran menyambungkan dibuang');
  }
}

"""
pa = ganti(pa, "// ── RESOLVE MEDIA URL + caption dari LINKS ──",
           HANDOVER + "// ── RESOLVE MEDIA URL + caption dari LINKS ──", "PA HANDOVER")


# =========================================================================
# H. TEMUAN EVAL MODEL ASLI v3.13 (putaran 1)
# =========================================================================
# H1. Pertanyaan galian tidak ditempel kalau kolomnya baru saja terisi di giliran ini.
pa = ganti(pa,
"""const GALIAN_KOLOM = (() => { try { return String($('Rakit Konteks').first().json.galian_kolom || ''); } catch (e) { return ''; } })();
""",
"""const GALIAN_KOLOM = (() => { try { return String($('Rakit Konteks').first().json.galian_kolom || ''); } catch (e) { return ''; } })();
// Galian yang kolomnya MASIH kosong sesudah giliran ini (v3.13). Rakit Konteks menyusun galian
// sebelum jawaban giliran ini tersimpan; eval v3.13 S2: prospek menyebut "Dapur Nadia" tanpa ditanya,
// model mencatatnya di [FACTS], pertanyaan kembarnya dibuang, lalu jaring menempelkan "Oh iya, nama
// usahanya apa kak?". Dipakai di dua tempat yang MENAMBAH pertanyaan galian (sudah-tahu & +galian).
const GALIAN_TERBUKA = GALIAN_KOLOM && !merged[GALIAN_KOLOM] ? GALIAN_KOLOM : '';
""", "PA GALIAN_TERBUKA")
pa = ganti(pa,
"""  if (kalBaru.length < kal.length && (kalBaru.length || TANYA_GALIAN[GALIAN_KOLOM])) {
    kal = kalBaru.length ? kalBaru : [TANYA_GALIAN[GALIAN_KOLOM]];
""",
"""  if (kalBaru.length < kal.length && (kalBaru.length || TANYA_GALIAN[GALIAN_TERBUKA])) {
    kal = kalBaru.length ? kalBaru : [TANYA_GALIAN[GALIAN_TERBUKA]];
""", "PA sudah-tahu galian terbuka")
pa = ganti(pa,
"""if (ringkasAlasan && !cadangan && !isNewUser && !PROSPEK_BERTANYA && TANYA_GALIAN[GALIAN_KOLOM]
""",
"""if (ringkasAlasan && !cadangan && !isNewUser && !PROSPEK_BERTANYA && TANYA_GALIAN[GALIAN_TERBUKA]
""", "PA +galian terbuka (syarat)")
pa = ganti(pa,
"""  cleanOutput = cleanOutput.trim() + ' ' + TANYA_GALIAN[GALIAN_KOLOM];
""",
"""  cleanOutput = cleanOutput.trim() + ' ' + TANYA_GALIAN[GALIAN_TERBUKA];
""", "PA +galian terbuka (isi)")

# H2. Minta deck yang briefnya sudah diteruskan tidak dibalas tawaran deck lagi.
DECK_DITERUSKAN = r"""// ── DECK SUDAH DITERUSKAN (2026-09-23, v3.13) ──
// Eval v3.13 S5: "boleh dong dibuatin deck" -> [DECK_REQUEST] keluar dan brief diteruskan, tapi
// balasannya "Boleh banget kak. Mau aku mintakan Steven buatkan deck khusus buat Kopi Senja? Nanti
// Steven sendiri yang susun dan hubungi kakak langsung." - menawarkan lagi yang barusan diminta.
// Di giliran minta deck yang briefnya benar-benar diteruskan (mintaDeck && isDeckRequest), kalimat
// tanya yang MENAWARKAN deck dibuang; kalau tidak ada kalimat yang mengabarkan Steven akan
// menyusun / menghubungi, kalimat kabar ditambahkan di depan. Kalimat lain tidak disentuh.
const KALIMAT_DECK = 'Siap kak, sudah aku teruskan ke Steven. Dia sendiri yang akan menyusun decknya dan menghubungi kakak langsung.';
const TAWAR_DECK = /\bmau\b[^?]{0,30}\b(mintakan|dimintakan|dibuatkan|dibuatin|dibikinin|buatkan|bikinin)\b[^?]*\?/i;
const KABAR_DECK = /\b(sudah|udah|sdh)\b[^.?!\n]{0,25}\b(aku\s+)?(terus|teruskan|sampaikan|kabar|catat)\w*|\bsteven\b[^.?!\n]{0,40}\b(susun|menyusun|buat|bikin|hubungi|menghubungi)\w*/i;
if (mintaDeck && isDeckRequest && !isTalkToAdmin) {
  const kal = pecahKalimat(cleanOutput);
  const sisa = kal.filter(k => !(/\?/.test(k) && TAWAR_DECK.test(k)));
  if (sisa.length < kal.length) {
    cleanOutput = (sisa.some(k => KABAR_DECK.test(k)) ? sisa
                   : [KALIMAT_DECK, ...sisa.filter(k => !SAPAAN_PENDEK.test(k))]).join(' ').trim();
    ringkasAlasan = ringkasAlasan ? ringkasAlasan + '+deck' : 'deck';
    console.log('DECK: brief sudah diteruskan - tawaran deck di balasan dibuang');
  }
}

"""
pa = ganti(pa, "// ── RESOLVE MEDIA URL + caption dari LINKS ──",
           DECK_DITERUSKAN + "// ── RESOLVE MEDIA URL + caption dari LINKS ──", "PA DECK DITERUSKAN")

# H3. Nama usaha dari model ([FACTS] / blok brief) yang cuma jenis usaha bukan nama (eval putaran 2).
pa = ganti(pa,
"""// ── PENANGKAP JAWABAN — SELESAI ──

const slotDitanyaLalu = [...slotDitanya(prev.last_bot_reply)];
""",
"""// ── PENANGKAP JAWABAN — SELESAI ──

// ── Nama usaha dari model yang cuma jenis usaha (2026-09-23, v3.13) ──
// Eval v3.13 S6: nama usahanya ditanya ulang, prospek menjawab "persewaan aja sih" (= belum ada
// nama), model menulis [FACTS nama_bisnis="persewaan"]. Penangkap kode sudah menolaknya, tapi
// [FACTS] selalu menang, jadi cover deck bisa berbunyi "persewaan". Aturannya sama dengan
// penangkap: jenis usaha / dagangan huruf kecil bukan nama ("Sewa Raket Padel" = nama merek).
// Nilainya dipindah ke bidang usaha kalau bidang usahanya masih kosong. Berlaku juga untuk blok
// [DECK_REQUEST] (di bawah). Nilai lama di STATS tidak disentuh.
const JENIS_BUKAN_NAMA = (s) => { const x = String(s || '').trim();
  return !!x && (JENIS_USAHA.test(x) || (DAGANGAN.test(x) && !HURUF_BESAR_SEMUA(x))); };
if (!KOSONG(facts.nama_bisnis) && JENIS_BUKAN_NAMA(BERSIH(facts.nama_bisnis, 120))) {
  console.warn('[FACTS] nama_bisnis "' + facts.nama_bisnis + '" = jenis usaha, bukan nama - tidak disimpan sebagai nama.');
  if (!merged.industri) { merged.industri = BERSIH(facts.nama_bisnis, 120); changed.industri = true; }
  merged.nama_bisnis  = BERSIH(prev.nama_bisnis, 120);
  changed.nama_bisnis = false;
  delete facts.nama_bisnis;   // penangkap di bawah boleh menilai jawabannya sendiri
}

const slotDitanyaLalu = [...slotDitanya(prev.last_bot_reply)];
""", "PA FACTS nama jenis")
pa = ganti(pa,
"""  // GATE TINGKAT 1 — sejak 2026-08-30 hanya menahan NOTIFIKASI, bukan penyimpanan.
""",
"""  // v3.13: nama usaha di blok brief yang cuma jenis usaha bukan nama (lihat JENIS_BUKAN_NAMA). Live
  // 2026-09-23: REQUESTS mencatat nama_bisnis "sewa raket padel" - tercetak di cover deck.
  if (JENIS_BUKAN_NAMA(deckRequest.nama_bisnis)) {
    if (!deckRequest.industri) deckRequest.industri = deckRequest.nama_bisnis;
    deckRequest.nama_bisnis = merged.nama_bisnis && !JENIS_BUKAN_NAMA(merged.nama_bisnis) ? merged.nama_bisnis : '';
  }
  // GATE TINGKAT 1 — sejak 2026-08-30 hanya menahan NOTIFIKASI, bukan penyimpanan.
""", "PA DECK nama jenis")

pa_node["jsCode"] = pa
rk_node["jsCode"] = rk

# prompt # TAG: tag handover berarti SUDAH disambungkan
sp = ganti(sp,
"""  Sertai kalimat yang memberi tahu bahwa Steven akan menghubunginya.
""",
"""  Sertai kalimat yang memberi tahu bahwa Steven akan menghubunginya.
  Dia sudah minta, jadi langsung sambungkan — jangan bertanya lagi "mau aku sambungkan?".
  Permintaan yang ditulis singkat ("kpn bs ngmng sm steven?") sama artinya.
""", "PROMPT TAG handover")
agent["systemMessage"] = sp


# =========================================================================
# G. MERGE BRIEF - sesudah deck terkirim: notif singkat UPDATE PROSPEK
# =========================================================================
mb_node = NODES["Merge Brief"]["parameters"]
mb = mb_node["jsCode"]
mb = ganti(mb,
"""const bertambah   = terisi.length > jumlahLama;
""",
"""const bertambah   = terisi.length > jumlahLama;

// ── Sesudah deck terkirim (2026-09-23, v3.13) ──
// Uji live Steven: deck dikirim 13:53, prospek menjawab "basic deh" 13:58, model menulis ulang blok
// brief (minat_paket = Basic) -> notif lengkap "BRIEF DECK (diperbarui) ... DECK SIAP DIGENERATE"
// terkirim lagi ke admin. Keputusan Steven 2026-09-23: sesudah deck terkirim cukup notif SINGKAT
// "UPDATE PROSPEK" berisi yang baru saja: isian yang dulu kosong, atau isian komersial yang
// berubah (paket, budget, deadline, urgensi, nilai transaksi, prospek/bulan). Deskripsi yang cuma
// ditulis ulang model tidak dihitung; kutipan asli tidak pernah dihitung. Tidak ada yang baru ->
// tidak ada notif. REQUESTS tetap diperbarui seperti biasa. Permintaan deck eksplisit
// (deckDiminta) tetap memakai notif lengkap. Sumber "sudah terkirim": REQUESTS.deck_dikirim_ts
// (ditulis kirim_deck.py), cadangannya STATS.deck_terkirim_ts.
const KOMERSIAL = ['minat_paket', 'budget_range', 'deadline', 'urgensi', 'nilai_transaksi', 'prospek_per_bulan'];
const deckDikirim = String(lama['deck_dikirim_ts'] || '').trim()
  || String((rur.userRow || {})['deck_terkirim_ts'] || '').trim();
const updateSesudahDeck = !!deckDikirim && !pertamaKali && pa.deckDiminta !== true;
const berubah = FIELDS.filter(f => f !== 'kutipan_asli' && hasil[f]
  && (!String(lama[f] ?? '').trim() || (KOMERSIAL.includes(f) && norm(hasil[f]) !== norm(lama[f]))));
const notif_update =
  `🔄 [VIRA Personal] UPDATE PROSPEK — deck sudah terkirim\\n` +
  `${hasil.nama_bisnis || '(nama bisnis belum disebut)'} · ${hasil.nama || 'nama belum disebut'} · WA: ${key}\\n\\n` +
  berubah.map(f => `${LABEL[f] || f}: ${hasil[f]}`).join('\\n');
""", "MB update sesudah deck")
mb = ganti(mb,
"""    deck_layak: pa.deckLayak === true || pa.deckDiminta === true
                || (pa.isDeckRequest === true && (pertamaKali || bertambah)),
    notif_text,
""",
"""    // v3.13: sesudah deck terkirim, notif hanya kalau ada yang baru (lihat updateSesudahDeck).
    deck_layak: updateSesudahDeck ? berubah.length > 0
      : (pa.deckLayak === true || pa.deckDiminta === true
         || (pa.isDeckRequest === true && (pertamaKali || bertambah))),
    notif_text: updateSesudahDeck ? notif_update : notif_text,
""", "MB gerbang notif")
mb_node["jsCode"] = mb


# =========================================================================
# E. SETTINGS
# =========================================================================
assert wf["settings"]["errorWorkflow"] == "P_ECOTzcz99B1siU-BcDW", wf["settings"]["errorWorkflow"]
wf["settings"]["errorWorkflow"] = "0mp_AdLtInm68RxQUwLqV"

with io.open(DST, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
with io.open(MD, "w", encoding="utf-8") as f:
    f.write(sp[1:] if sp.startswith("=") else sp)

print("OK ->", os.path.basename(DST), "| node:", len(wf["nodes"]))
print("OK ->", os.path.basename(MD), "| prompt:", len(sp), "karakter")
