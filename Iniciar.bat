@echo off
title RedLocalBlock - Lanzador
setlocal EnableDelayedExpansion

:: 1. Comprobar si se ejecuta con permisos de Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Solicitando elevacion de permisos mediante UAC de Windows...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: 2. Posicionarse en la carpeta raíz del proyecto
cd /d "%~dp0"

:: 3. Seleccionar el intérprete de Python (entorno virtual o sistema)
set "PYTHON_EXE="
if exist "venv\Scripts\pythonw.exe" (
    set "PYTHON_EXE=venv\Scripts\pythonw.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    where pythonw >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=pythonw"
    ) else (
        set "PYTHON_EXE=python"
    )
)

:: 4. Iniciar la aplicación sin dejar consola negra de fondo
start "" "!PYTHON_EXE!" -m src.main
exit /b 0
