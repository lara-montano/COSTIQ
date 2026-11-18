@echo off
rem ============================================================
rem  COSTIQ - lanzador para Windows
rem  Haz doble clic en este archivo. La primera vez instala lo
rem  necesario, de 5 a 10 minutos; despues abre en segundos.
rem ============================================================
setlocal
title COSTIQ
cd /d "%~dp0"

echo.
echo  COSTIQ - Costos en Ingenieria Quimica
echo  =====================================
echo.

if not exist "app.py" goto :sin_zip

echo "%CD%" | find /i "OneDrive" >nul
if errorlevel 1 goto :buscar_python
echo  AVISO: esta carpeta esta dentro de OneDrive. Si la instalacion
echo  falla o tarda mucho, mueve la carpeta a Descargas y vuelve a intentar.
echo.

rem --- 1. Buscar Python 3.10 o mas reciente, de 64 bits -----------
:buscar_python
set "PY="
set "CHECK=import sys, sysconfig; sys.exit(not (sys.version_info >= (3, 10) and sysconfig.get_platform() == 'win-amd64'))"
py -3 -c "%CHECK%" <nul >nul 2>nul
if errorlevel 1 goto :probar_python
set "PY=py -3"
goto :tiene_python
:probar_python
python -c "%CHECK%" <nul >nul 2>nul
if errorlevel 1 goto :sin_python
set "PY=python"
:tiene_python
echo  Python encontrado:
%PY% --version

rem --- 2. Crear el entorno de COSTIQ, solo la primera vez -----------
if not exist ".venv" goto :crear_venv
".venv\Scripts\python.exe" -c "import sys" <nul >nul 2>nul
if not errorlevel 1 goto :revisar_paquetes
echo  El entorno anterior no funciona; lo vuelvo a crear.
rmdir /s /q ".venv"
:crear_venv
echo  Creando el entorno de COSTIQ...
%PY% -m venv .venv
if errorlevel 1 goto :error_venv

rem --- 3. Instalar los paquetes si faltan ------------------------
:revisar_paquetes
".venv\Scripts\python.exe" -c "import streamlit, plotly, pandas" <nul >nul 2>nul
if not errorlevel 1 goto :abrir
echo.
echo  Instalando los paquetes. La primera vez tarda de 5 a 10 minutos.
echo  No cierres esta ventana.
echo.
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :error_pip

rem --- 4. Abrir la app --------------------------------------------
:abrir
echo.
echo  Abriendo COSTIQ en tu navegador...
echo  Mientras uses la app, deja esta ventana abierta.
echo  Para cerrar COSTIQ, cierra esta ventana.
echo.
".venv\Scripts\python.exe" -m streamlit run app.py --server.address localhost --server.fileWatcherType none
goto :fin

:sin_zip
echo  No encuentro el archivo app.py junto a este lanzador.
echo  Primero extrae el ZIP: clic derecho sobre el ZIP y elige "Extraer todo".
echo  Despues abre la carpeta extraida y haz doble clic en iniciar_windows.bat.
goto :fin

:sin_python
echo  No encontre Python 3.10 o mas reciente, de 64 bits.
echo.
echo  1. Abre https://www.python.org/downloads/ y descarga el instalador
echo     "Windows installer (64-bit)". Usalo tambien si tu laptop es ARM.
echo  2. En la primera pantalla del instalador marca la casilla
echo     "Add python.exe to PATH" y luego "Install Now".
echo  3. Vuelve a hacer doble clic en este archivo.
start "" "https://www.python.org/downloads/"
goto :fin

:error_venv
echo.
echo  No se pudo crear el entorno de COSTIQ.
echo  Revisa la seccion "Problemas frecuentes" del manual.
goto :fin

:error_pip
echo.
echo  La instalacion de paquetes fallo.
echo  Revisa tu conexion a internet y vuelve a hacer doble clic en este archivo.
echo  Si se repite, consulta "Problemas frecuentes" en el manual.
goto :fin

:fin
echo.
pause
