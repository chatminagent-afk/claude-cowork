---
name: store-python-appdata-redirect
description: Python dari Microsoft Store di laptop Steven me-redirect tulisan ke %APPDATA% ke dalam container MSIX — pakai path relatif home untuk config app Python
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3dbf5139-5c87-4392-877a-9d112e42f08f
  modified: 2026-07-31T04:21:32.254Z
---

Python di laptop Steven adalah versi Microsoft Store (`C:\Users\Steven\AppData\Local\Microsoft\WindowsApps\python.exe`, 3.13). Store Python jalan di dalam container MSIX yang **diam-diam me-redirect tulisan ke `%APPDATA%`** ke:

```
%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\Roaming\
```

`os.environ["APPDATA"]` tetap melaporkan `C:\Users\Steven\AppData\Roaming`, jadi tidak ada error — file cuma mendarat di tempat lain.

**Akibatnya:** lokasi config app Python jadi tergantung interpreter mana yang meluncurkannya. Dijalankan lewat `pythonw.exe` (alias Store) vs `python` biasa di PATH akan baca file yang berbeda, dan setting kelihatan "hilang".

**How to apply:** untuk app Python yang menyimpan config/log di laptop ini, jangan pakai `%APPDATA%`. Pakai path relatif home — `Path.home() / ".<appname>"` — yang **tidak** ter-redirect (sudah diverifikasi empiris: tulis ke `~/.probe` mendarat di `C:\Users\Steven\.probe` betulan). Sediakan juga env var override untuk testing.

Ditemukan saat membangun [[claude-token-monitor]].
