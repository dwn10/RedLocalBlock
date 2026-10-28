@echo off
title RedLocalBlock - Compilador a Ejecutable Portable (.exe)
setlocal EnableDelayedExpansion

cd /d "%~dp0"

echo =======================================================
echo   RedLocalBlock - Compilador PyInstaller a .EXE
echo =======================================================
echo.

:: 1. Comprobar si PyInstaller esta instalado
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] PyInstaller no esta instalado. Instalando dependencias de compilacion...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo instalar PyInstaller. Verifica tu conexion a Internet.
        pause
        exit /b 1
    )
)

echo [1/3] Limpiando compilaciones previas...
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"

echo [2/3] Compilando aplicacion con CustomTkinter y Scapy...
python -m PyInstaller --noconfirm --clean ^
    --onefile ^
    --windowed ^
    --name "RedLocalBlock" ^
    --collect-all "customtkinter" ^
    --collect-all "scapy" ^
    --collect-all "pystray" ^
    --hidden-import "pystray._win32" ^
    --hidden-import "src" ^
    --hidden-import "src.ui.components" ^
    --hidden-import "src.services" ^
    --hidden-import "src.models" ^
    --hidden-import "src.core" ^
    --hidden-import "src.utils" ^
    src\main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un fallo durante la compilacion.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo [3/3] Compilacion exitosa!
echo El ejecutable portable se encuentra en:
echo   %~dp0dist\RedLocalBlock.exe
echo =======================================================
echo.
pause
exit /b 0
