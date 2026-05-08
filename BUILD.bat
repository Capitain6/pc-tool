@echo off
title PC Tool — Compilation
echo.
echo  ========================================
echo   PC Tool v4.0 — Compilation en .exe
echo  ========================================
echo.

:: 1. Installer les dependances
echo [1/4] Installation des dependances...
pip install pyinstaller pillow pystray customtkinter psutil --quiet
echo  OK

:: 2. Creer l'icone
echo [2/4] Creation de l'icone...
python make_icon.py
echo  OK

:: 3. Compiler avec PyInstaller
echo [3/4] Compilation en .exe (peut prendre 1-2 minutes)...
pyinstaller --noconfirm --onefile --windowed ^
  --name "PCTool" ^
  --icon "icon.ico" ^
  --add-data "icon.ico;." ^
  --hidden-import "pystray" ^
  --hidden-import "PIL" ^
  --hidden-import "customtkinter" ^
  --hidden-import "psutil" ^
  timop.py
echo  OK

:: 4. Creer l'installeur avec Inno Setup (si installe)
echo [4/4] Creation de l'installeur...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    echo  Installeur cree dans le dossier Output\
) else (
    echo  Inno Setup non trouve — installez-le sur https://jrsoftware.org/isinfo.php
    echo  Puis relancez ce script.
    echo  L'exe seul est disponible dans : dist\PCTool.exe
)

echo.
echo  ========================================
echo   TERMINE ! Fichiers generes :
echo   - dist\PCTool.exe  (executable seul)
echo   - Output\PCTool_Setup.exe  (installeur)
echo  ========================================
echo.
pause
