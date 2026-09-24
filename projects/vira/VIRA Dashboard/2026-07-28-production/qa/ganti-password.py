#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ganti-password.py — ganti password satu akun dashboard.

Klik dua kali `ganti-password.bat`, atau:
    python qa/ganti-password.py

Daftar akun dibaca langsung dari n8n/src/tenants.js, jadi kalau nanti ada
akun baru dia ikut muncul sendiri tanpa perlu mengubah file ini.

Password TIDAK dikirim ke mana pun dan TIDAK disimpan. Yang keluar hanya
nama akun + salt + hash.
"""

import getpass
import hashlib
import os
import re
import secrets
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TENANTS = os.path.join(HERE, '..', 'n8n', 'src', 'tenants.js')


def baca_akun():
    """Ambil username + display dari VIRA_USERS di tenants.js."""
    try:
        with open(TENANTS, encoding='utf-8') as f:
            src = f.read()
    except IOError:
        return []
    blok = re.search(r'var VIRA_USERS = \{(.*?)\n\};', src, re.S)
    if not blok:
        return []
    out = []
    for m in re.finditer(r"username: '([^']+)',\s*\n\s*display: '([^']+)'", blok.group(1)):
        out.append((m.group(1), m.group(2)))
    return out


def main():
    akun = baca_akun()
    if not akun:
        print('  [!] Tidak bisa membaca daftar akun dari tenants.js.')
        print('      Pastikan file ini dijalankan dari dalam folder proyek.')
        return 2

    print()
    print('  Ganti password dashboard VIRA')
    print('  ' + '-' * 46)
    print('  Password milik SIAPA yang mau diganti?')
    print()
    for i, (u, d) in enumerate(akun, 1):
        print('    %d. %-12s %s' % (i, u, d))
    print()

    try:
        pilih = input('  Nomor (1-%d): ' % len(akun)).strip()
    except EOFError:
        return 2
    if not pilih.isdigit() or not (1 <= int(pilih) <= len(akun)):
        print('\n  [!] Pilihan tidak dikenal. Dibatalkan.')
        return 2
    username, display = akun[int(pilih) - 1]

    print()
    print('  Mengganti password untuk: %s (%s)' % (username, display))
    print('  Ketikanmu tidak akan terlihat. Itu normal.')
    print()

    pw = getpass.getpass('  Password baru        : ')
    if not pw:
        print('\n  [!] Kosong. Dibatalkan.')
        return 2
    if getpass.getpass('  Ketik sekali lagi    : ') != pw:
        print('\n  [!] Dua ketikan tidak sama. Ulangi dari awal.')
        return 2

    if len(pw) < 12:
        print()
        print('  [!] Cuma %d karakter. Tetap jalan, tapi password ini menjaga' % len(pw))
        print('      nomor WA customer dan tombol matikan-bot. Frasa panjang')
        print('      seperti "kopi-susu-jam-tiga" lebih kuat dan tetap mudah.')

    salt = secrets.token_hex(8)
    digest = hashlib.sha256((salt + ':' + pw).encode('utf-8')).hexdigest()

    print()
    print('  ' + '=' * 66)
    print('  SALIN SEMUA DI BAWAH INI, KIRIM KE CLAUDE:')
    print('  ' + '=' * 66)
    print()
    print('    untuk akun: %s' % username)
    print("    salt: '%s'," % salt)
    print("    hash: '%s'" % digest)
    print()
    print('  ' + '=' * 66)
    print('  Passwordnya sendiri JANGAN dikirim. Simpan sendiri.')
    print()
    return 0


if __name__ == '__main__':
    code = main()
    try:
        input('  Tekan Enter untuk menutup...')
    except EOFError:
        pass
    sys.exit(code)
