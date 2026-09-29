@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"

set "WA=%~1"
if not defined WA set /p "WA=Nomor WA klien (contoh 6285171701168): "
if not defined WA (
  echo Nomor WA kosong. Batal.
  goto :akhir
)

echo.
echo Menyusun deck untuk %WA% ...
echo.
python buat_deck.py --wa %WA% --bersih
if errorlevel 1 (
  echo.
  echo GAGAL. Baca pesan error di atas.
  goto :akhir
)

echo.
echo Selesai. Membuka folder keluaran...
start "" "keluaran"

:akhir
echo.
pause
