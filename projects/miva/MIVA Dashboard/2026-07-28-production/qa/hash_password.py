#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hash_password.py — hitung salt + hash untuk sebuah password dashboard.

    python qa/hash_password.py "password-baru"

Salin dua baris keluarannya ke entri user di n8n/src/tenants.js, lalu jalankan
`python n8n/build_workflow.py` dan import ulang workflow.

Password TIDAK disimpan di mana pun oleh script ini.
"""

import hashlib
import secrets
import sys


def main():
    if len(sys.argv) < 2 or not sys.argv[1]:
        print(__doc__)
        return 2
    password = sys.argv[1]
    if len(password) < 12:
        print('[!] password kurang dari 12 karakter — untuk kontrol yang bisa')
        print('    mematikan bot produksi, pakai minimal 16 karakter acak.')
    salt = secrets.token_hex(8)
    digest = hashlib.sha256((salt + ':' + password).encode('utf-8')).hexdigest()
    print()
    print("    salt: '%s'," % salt)
    print("    hash: '%s'" % digest)
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
