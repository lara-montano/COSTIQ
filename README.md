# COSTIQ

**COSTIQ** (*Costos en Ingeniería Química*) estima el costo de equipo de proceso con el método de módulo de Turton et al. (2018), Apéndice A. Incluye un paquete de Python importable (`costiq`) y una interfaz web en Streamlit.

**Úsala en línea, sin instalar nada: [costiq.streamlit.app](https://costiq.streamlit.app)**

## Qué calcula

- Costo de compra C_p° de 96 tipos de equipo en 23 categorías (Tabla A.1), incluidos evaporadores, secadores, filtros, centrífugas, cribas, transportadores, mezcladores, calderas y marmitas.
- Factores de presión por la Ec. A.2 (recipientes y torres) y la Ec. A.3 con la Tabla A.2.
- Factores de material (Fig. A.18) y de módulo desnudo (Fig. A.19, Tabla A.7), con el identificador del libro de cada valor.
- Costo de módulo desnudo C_BM (Ec. A.4 y Tabla A.5), torres con platos o empaque, y unidades en paralelo.
- Cotización propia: cualquier equipo sin correlación (molinos, extrusores, membranas…) se escala desde un precio de referencia con la Ec. 7.1.
- Costo de módulo total C_TM y costo grassroots C_GR (Ecs. 7.15 y 7.16).
- Actualización con el CEPCI anual (2001–2024) o con un valor propio; conversión a MXN.
- Sensibilidad a capacidad, presión, material y año; cascada de costos; proyecto guardable en JSON y exportable a CSV.

## Instalación y uso

Para estudiantes hay un [manual de instalación y uso](docs/manual/manual_costiq.pdf) (PDF, Windows y Mac).

La forma más rápida es la versión en línea, [costiq.streamlit.app](https://costiq.streamlit.app), publicada en Streamlit Community Cloud desde la rama `main`. Si nadie la usa en 12 horas se duerme; cualquiera la despierta con el botón «Yes, get this app back up!».

Para usarla sin internet, instálala en tu computadora:

1. Instala Python 3.10 o más reciente desde [python.org](https://www.python.org/downloads/). En Windows usa el instalador de 64 bits y marca «Add python.exe to PATH».
2. Descarga el [ZIP de COSTIQ](https://github.com/lara-montano/COSTIQ/archive/refs/heads/main.zip) y descomprímelo.
3. Abre COSTIQ con el lanzador:
   - Windows: doble clic en `iniciar_windows.bat`.
   - Mac: en Terminal escribe `bash ` (con espacio), arrastra `iniciar_mac.command` a la ventana y presiona Enter.

La primera vez, el lanzador crea un entorno en `.venv` e instala los paquetes (5 a 10 minutos). Después abre la app en segundos, en `http://localhost:8501`.

Con terminal:

```bash
git clone https://github.com/lara-montano/COSTIQ.git
cd COSTIQ
pip install -r requirements.txt
streamlit run app.py
```

Desde Python, sin interfaz:

```python
from costiq import cost, plant_summary

e102 = cost("hx_floating_head", 205, material="CS/SS", pressure=18, pressure_option="both")
t101 = cost("tower", material="CS", pressure=5, diameter=2.1, length=23)
print(e102.FBM, t101.FP)            # 4.82, 1.68
s = plant_summary([e102, t101], cepci=800.8)
print(s.CTM, s.CGR)
```

## Validación

```bash
pip install pytest
python -m pytest
```

Las pruebas reproducen los Ejemplos 7.3, 7.5 y 7.10 a 7.14 del libro. En el Ejemplo 7.14 (siete equipos), COSTIQ obtiene ΣC_BM = 1,088,399 USD, C_TM = 1,284,311 USD y C_GR = 1,692,466 USD con CEPCI = 542; el libro reporta 1,088,100, 1,284,000 y 1,692,000 USD.

## Supuestos que conviene conocer

- **Ec. A.2 con (P + 1).** La Ec. A.2 impresa en la 5.ª edición usa P; los Ejemplos 7.13 y 7.14 usan (P + 1). COSTIQ sigue los ejemplos (`costiq.engine.VESSEL_GAUGE_OFFSET`).
- **Factores leídos de figuras.** F_M y F_BM se digitalizaron de las Figuras A.18 y A.19, con resolución de ±0.03 a ±0.04.
- **Tanques API.** El Apéndice A no tabula F_BM para tanques; COSTIQ usa 1.0 y permite cambiarlo.
- **CEPCI.** Los promedios anuales 2002–2024 aún no se verifican contra la fuente primaria.
- **Equipos de la v2.1.** Varios F_BM de la Tabla A.7 son estimaciones del libro; el F_BM de calderas de vapor es un supuesto (2.16). Detalle en [docs/COBERTURA_AGROINDUSTRIA.md](docs/COBERTURA_AGROINDUSTRIA.md).

La auditoría completa de la versión 1 y la justificación de cada cambio están en [docs/AUDITORIA_v1.md](docs/AUDITORIA_v1.md).

## Estructura

```
costiq/        paquete de cálculo (sin dependencias)
  data.py      constantes del Apéndice A con su fuente
  engine.py    ecuaciones y costo de planta
ui/            estilos y gráficas de la interfaz
app.py         interfaz Streamlit
tests/         pruebas contra los ejemplos del libro
docs/manual/   manual para estudiantes (Typst y PDF)
iniciar_windows.bat, iniciar_mac.command   lanzadores que instalan y abren la app
```

## Referencia

Turton, R., Shaeiwitz, J. A., Bhattacharyya, D., & Whiting, W. B. (2018). *Analysis, Synthesis, and Design of Chemical Processes* (5th ed.). Pearson. Appendix A.

## Autores

- Oscar Daniel Lara-Montaño, Universidad Autónoma de Querétaro
- Fernando Israel Gómez-Castro, Universidad de Guanajuato
- Sergio Iván Martínez-Guido, Universidad de Guanajuato

## Licencia

MIT. Ver [LICENSE](LICENSE).
