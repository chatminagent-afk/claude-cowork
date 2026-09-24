# -*- coding: utf-8 -*-
"""
VERIFIKASI + SIMULASI HARGA — Persada Cisoka Residence
2026-07-20

Script ini TIDAK menyalin angka turunan dari pricelist.
Yang di-input hanya 3 hal per tipe:  harga jual, bonus cashback, bunga.
Uang muka / maksimal KPR / angsuran semuanya DIHITUNG ULANG dari rumus,
lalu dibandingkan ke angka pricelist untuk membuktikan rumusnya benar.

Jalankan:  python 2026-07-20-verifikasi-simulasi-harga-PCR.py
"""

# ============================================================
# 1. INPUT — hanya angka dasar (tidak ada angka turunan di sini)
# ============================================================
TIPE = [
    dict(nama="36/72",  kategori="Komersil", harga=383_004_784, bonus=20_000_000,
         dp_persen=0.05, bunga=0.0825, tenor=[15, 20, 25, 30]),
    dict(nama="36/81",  kategori="Komersil", harga=409_294_258, bonus=20_000_000,
         dp_persen=0.05, bunga=0.0825, tenor=[15, 20, 25, 30]),
    dict(nama="30/60",  kategori="Subsidi",  harga=185_000_000, bonus=0,
         dp_tetap=5_850_000, bunga=0.05,    tenor=[10, 15, 20]),
]

# Angka dari FOTO PRICELIST — dipakai HANYA sebagai pembanding, bukan sumber hitungan
PRICELIST = {
    "36/72": dict(um=18_150_239, kpr=344_854_545,
                  ang={15: 3_345_573, 20: 2_938_387, 25: 2_719_006, 30: 2_590_777}),
    "36/81": dict(um=19_464_713, kpr=369_829_545,
                  ang={15: 3_587_865, 20: 3_151_190, 25: 2_915_921, 30: 2_778_405}),
    "30/60": dict(um=5_850_000,  kpr=179_150_000,
                  ang={10: 1_900_164, 15: 1_416_707, 20: 1_182_311}),
}

# ============================================================
# 2. RUMUS
# ============================================================
def hitung(t):
    """Turunkan semua angka dari harga jual + bonus + bunga."""
    setelah_bonus = t["harga"] - t["bonus"]
    if "dp_tetap" in t:                      # subsidi: uang muka nominal tetap
        um = t["dp_tetap"]
    else:                                    # komersil: uang muka = 5% x harga setelah bonus
        um = round(setelah_bonus * t["dp_persen"])
    kpr = setelah_bonus - um
    return setelah_bonus, um, kpr

def anuitas(pokok, bunga_tahunan, tahun):
    """Angsuran bulanan metode anuitas."""
    i = bunga_tahunan / 12
    n = tahun * 12
    return pokok * i / (1 - (1 + i) ** -n)

def rp(x):
    return f"Rp{x:,.0f}".replace(",", ".")

# ============================================================
# 3. VERIFIKASI — hasil hitungan vs pricelist
# ============================================================
print("=" * 74)
print("VERIFIKASI RUMUS  (hasil hitung ulang  vs  angka di pricelist)")
print("=" * 74)

gagal = 0
for t in TIPE:
    setelah_bonus, um, kpr = hitung(t)
    p = PRICELIST[t["nama"]]
    print(f"\nTipe {t['nama']} ({t['kategori']})")
    for label, hitungan, acuan in (("Uang Muka", um, p["um"]),
                                   ("Maksimal KPR", kpr, p["kpr"])):
        selisih = hitungan - acuan
        status = "COCOK" if abs(selisih) <= 1 else f"BEDA {selisih:+,}"
        gagal += 0 if abs(selisih) <= 1 else 1
        print(f"  {label:<14} hitung {rp(hitungan):>18}  |  pricelist {rp(acuan):>18}  -> {status}")
    for th in t["tenor"]:
        a = round(anuitas(kpr, t["bunga"], th))
        acuan = p["ang"][th]
        selisih = a - acuan
        status = "COCOK" if abs(selisih) <= 1 else f"BEDA {selisih:+,}"
        gagal += 0 if abs(selisih) <= 1 else 1
        print(f"  Angsuran {th:>2} thn  hitung {rp(a):>18}  |  pricelist {rp(acuan):>18}  -> {status}")

print("\n" + "-" * 74)
print("HASIL: SEMUA COCOK" if gagal == 0 else f"HASIL: {gagal} angka TIDAK cocok")
print("-" * 74)

# ============================================================
# 4. SIMULASI — bentuk yang nanti dipakai VIRA menjawab user
# ============================================================
print("\n" + "=" * 74)
print("CONTOH SIMULASI  (format jawaban yang akan dipakai VIRA)")
print("=" * 74)

for t in TIPE:
    setelah_bonus, um, kpr = hitung(t)
    print(f"\n### Tipe {t['nama']} — {t['kategori']}")
    print(f"  Harga jual              {rp(t['harga']):>18}")
    if t["bonus"]:
        print(f"  Bonus cashback        - {rp(t['bonus']):>18}   <- POTONGAN HARGA, bukan uang tunai")
        print(f"  Harga setelah bonus     {rp(setelah_bonus):>18}")
    print(f"  Uang muka             - {rp(um):>18}"
          + ("   (5% dari harga setelah bonus)" if "dp_persen" in t else "   (nominal tetap pricelist)"))
    print(f"  ------------------------------------------------")
    print(f"  Maksimal KPR            {rp(kpr):>18}")
    print(f"  Bunga simulasi          {t['bunga']*100:.2f}% per tahun (anuitas)")
    print()
    print(f"  {'Tenor':<10}{'Angsuran/bln':>18}{'Total angsuran':>22}{'Total dibayar*':>22}")
    for th in t["tenor"]:
        a = anuitas(kpr, t["bunga"], th)
        total_ang = a * th * 12
        total_bayar = total_ang + um
        print(f"  {str(th)+' thn':<10}{rp(round(a)):>18}{rp(round(total_ang)):>22}{rp(round(total_bayar)):>22}")
    print("  *Total dibayar = uang muka + seluruh angsuran (belum termasuk biaya lain)")

# ============================================================
# 5. STUDI KASUS — pertanyaan yang sering ditanya user
# ============================================================
print("\n" + "=" * 74)
print("STUDI KASUS")
print("=" * 74)

k = TIPE[0]; _, um72, kpr72 = hitung(k)
print(f"""
KASUS 1 — "Cashback 20 juta saya terima kapan?"
  JAWABAN BENAR : tidak diterima sebagai uang tunai. Rp20.000.000 dipotong
                  dari harga jual DI DEPAN, sebelum uang muka dan plafon KPR
                  dihitung. Harga {rp(k['harga'])} jadi {rp(k['harga']-k['bonus'])}.
  JAWABAN SALAH : "setelah akad Kakak dapat cashback Rp20 juta"  <- ini bug 20 Juli

KASUS 2 — "Kalau tanpa cashback, cicilan saya jadi berapa?"
  Tanpa potongan 20jt, KPR = {rp(round(k['harga']*0.95))}
  Angsuran 20 thn = {rp(round(anuitas(k['harga']*0.95, k['bunga'], 20)))}
  Dengan cashback  = {rp(round(anuitas(kpr72, k['bunga'], 20)))}
  Jadi cashback menghemat {rp(round(anuitas(k['harga']*0.95,k['bunga'],20) - anuitas(kpr72,k['bunga'],20)))} per bulan
  selama 20 tahun = {rp(round((anuitas(k['harga']*0.95,k['bunga'],20)-anuitas(kpr72,k['bunga'],20))*240))} total.

KASUS 3 — "Budget cicilan saya maksimal 3 juta/bulan, bisa tipe apa?"
""")
for t in TIPE:
    _, _, kpr = hitung(t)
    cocok = [th for th in t["tenor"] if anuitas(kpr, t["bunga"], th) <= 3_000_000]
    if cocok:
        print(f"  Tipe {t['nama']:<7} -> BISA, tenor {'/'.join(str(x) for x in cocok)} thn "
              f"(mulai {rp(round(anuitas(kpr, t['bunga'], max(cocok))))}/bln)")
    else:
        print(f"  Tipe {t['nama']:<7} -> tidak masuk, termurah {rp(round(anuitas(kpr, t['bunga'], max(t['tenor']))))}/bln")

print(f"""
KASUS 4 — "Beda 36/72 sama 36/81 berapa per bulan?"
  Selisih harga      {rp(TIPE[1]['harga'] - TIPE[0]['harga'])}
  Selisih angsuran 20 thn {rp(round(anuitas(hitung(TIPE[1])[2], .0825, 20) - anuitas(hitung(TIPE[0])[2], .0825, 20)))} per bulan
  (bangunan sama-sama 36 m2, bedanya hanya luas tanah 72 vs 81 m2)
""")
