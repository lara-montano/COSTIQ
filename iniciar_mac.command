#!/bin/bash
# ============================================================
#  COSTIQ - lanzador para macOS
#  Uso: abre Terminal, escribe "bash " (con espacio), arrastra
#  este archivo a la ventana y presiona Enter.
#  La primera vez instala lo necesario (de 5 a 10 minutos);
#  después abre la app en segundos.
# ============================================================
cd "$(dirname "$0")" || exit 1

pausa() { echo; read -r -p "  Presiona Enter para cerrar esta ventana..." _; }

echo
echo "  COSTIQ - Costos en Ingeniería Química"
echo "  ====================================="
echo

if [ ! -f app.py ]; then
  echo "  No encuentro app.py junto a este archivo."
  echo "  Primero descomprime el ZIP (doble clic sobre él) y usa el"
  echo "  iniciar_mac.command que queda dentro de la carpeta."
  pausa; exit 1
fi

case "$PWD" in
  *"Mobile Documents"*|*CloudStorage*|*Dropbox*|*OneDrive*)
    echo "  AVISO: esta carpeta está en iCloud, Dropbox u OneDrive."
    echo "  Si la instalación falla o tarda mucho, mueve la carpeta a Descargas."
    echo ;;
esac

# --- 1. Buscar Python 3.10 o más reciente ---------------------------
es_valido() {
  "$1" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1 </dev/null
}
PY=""
for c in python3.15 python3.14 python3.13 python3.12 python3.11 python3.10 \
         /Library/Frameworks/Python.framework/Versions/3.1{5,4,3,2,1,0}/bin/python3 \
         /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
  ruta=$(command -v "$c" 2>/dev/null) || continue
  # El python3 de Apple es antiguo y puede pedir instalar herramientas de Xcode.
  [ "$ruta" = /usr/bin/python3 ] && continue
  if es_valido "$ruta"; then PY="$ruta"; break; fi
done

if [ -z "$PY" ]; then
  echo "  No encontré Python 3.10 o más reciente."
  echo
  echo "  1. Descarga Python desde https://www.python.org/downloads/"
  echo "     (botón amarillo «Download Python») e instálalo."
  echo "  2. Vuelve a ejecutar este archivo."
  open "https://www.python.org/downloads/" 2>/dev/null
  pausa; exit 1
fi
echo "  Python encontrado: $("$PY" --version 2>&1)"

# --- 2. Crear el entorno de COSTIQ, solo la primera vez -------------
VPY=.venv/bin/python
if [ -e .venv ] && ! "$VPY" -c 'import sys' >/dev/null 2>&1; then
  echo "  El entorno anterior no funciona; lo vuelvo a crear."
  rm -rf .venv
fi
if [ ! -e .venv ]; then
  echo "  Creando el entorno de COSTIQ..."
  "$PY" -m venv .venv || { echo "  No se pudo crear el entorno."; pausa; exit 1; }
fi

# --- 3. Instalar los paquetes si faltan ------------------------------
if ! "$VPY" -c 'import streamlit, plotly, pandas' >/dev/null 2>&1; then
  echo
  echo "  Instalando los paquetes. La primera vez tarda de 5 a 10 minutos."
  echo "  No cierres esta ventana."
  echo
  if ! "$VPY" -m pip install --disable-pip-version-check -r requirements.txt; then
    echo
    echo "  La instalación de paquetes falló."
    echo "  Revisa tu conexión a internet y vuelve a ejecutar este archivo."
    pausa; exit 1
  fi
fi

# --- 4. Abrir la app ---------------------------------------------------
echo
echo "  Abriendo COSTIQ en tu navegador..."
echo "  Mientras uses la app, deja esta ventana abierta."
echo "  Para cerrar COSTIQ, presiona Control + C en esta ventana."
echo
"$VPY" -m streamlit run app.py --server.address localhost --server.fileWatcherType none
