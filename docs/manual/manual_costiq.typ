// COSTIQ: manual de instalación y uso para estudiantes
// Compilar: typst compile docs/manual/manual_costiq.typ

#let azul = rgb("#1c5cab")
#let azul-claro = rgb("#e8eef7")
#let naranja = rgb("#b4591f")
#let naranja-claro = rgb("#fbefe6")
#let gris = rgb("#5b6067")
#let borde = rgb("#e2dfd7")
#let fondo = rgb("#f6f5f1")

#let version = "2.1"
#let fecha = "18 de noviembre de 2026"
#let repo = "https://github.com/lara-montano/COSTIQ"
#let zip = "https://github.com/lara-montano/COSTIQ/archive/refs/heads/main.zip"

#set document(
  title: "COSTIQ: manual de instalación y uso",
  author: ("Oscar Daniel Lara-Montaño",),
)
#set page(
  paper: "us-letter",
  margin: (x: 2.2cm, top: 2.2cm, bottom: 2.4cm),
  footer: context {
    set text(size: 8.5pt, fill: gris)
    grid(columns: (1fr, auto),
      [COSTIQ #version · Manual para estudiantes],
      counter(page).display("1 de 1", both: true),
    )
  },
)
#set text(font: "IBM Plex Sans", size: 10.5pt, lang: "es", fill: rgb("#16191d"))
#set par(leading: 0.62em, spacing: 0.95em, justify: false)
#set enum(spacing: 0.75em, indent: 0.2em)
#set list(spacing: 0.7em, indent: 0.2em, marker: text(fill: azul)[•])
#show link: set text(fill: azul)
#show raw: set text(font: "IBM Plex Mono", size: 9.2pt)
#show raw.where(block: true): it => block(
  width: 100%, fill: fondo, stroke: 0.5pt + borde, radius: 4pt, inset: 8pt, it,
)
#show heading.where(level: 1): it => block(above: 1.6em, below: 0.9em,
  text(size: 15pt, weight: "bold", fill: azul, it.body))
#show heading.where(level: 2): it => block(above: 1.2em, below: 0.6em,
  text(size: 11.5pt, weight: "bold", it.body))
#show figure.caption: it => text(size: 9pt, fill: gris, it)

// --- Piezas reutilizables -------------------------------------------------

// Nombre de un botón, menú o campo tal como aparece en pantalla.
#let ui(t) = text(weight: "semibold")[«#t»]
// Tecla del teclado.
#let tecla(t) = box(
  inset: (x: 3.5pt, y: 0pt), outset: (y: 2.5pt), radius: 2.5pt,
  stroke: 0.6pt + luma(170), fill: luma(248),
  text(font: "IBM Plex Mono", size: 8.8pt, t),
)
// Etiqueta pequeña junto al título de un paso.
#let etiqueta(t) = box(
  inset: (x: 5pt, y: 2pt), outset: (y: 1pt), radius: 8pt, fill: azul-claro,
  text(size: 8.5pt, weight: "medium", fill: azul, t),
)
// Encabezado numerado de un paso.
#let paso(n, titulo, cuando) = block(above: 1.8em, below: 0.9em, breakable: false,
  grid(columns: (auto, 1fr), column-gutter: 9pt, align: horizon,
    box(width: 24pt, height: 24pt, radius: 12pt, fill: azul,
      align(center + horizon, text(fill: white, weight: "bold", size: 12pt, str(n)))),
    [
      #show heading.where(level: 1): it => text(size: 15pt, weight: "bold", fill: azul, it.body)
      #heading(level: 1)[Paso #n. #titulo] #h(6pt) #etiqueta(cuando)
    ],
  ))
// Dos columnas: instrucciones para Windows y para Mac.
#let panel(sistema, cuerpo) = block(
  width: 100%, height: auto, stroke: 0.6pt + borde, radius: 5pt, clip: true,
  stack(
    block(width: 100%, fill: fondo, inset: (x: 9pt, y: 6pt),
      text(weight: "bold", size: 10.5pt, sistema)),
    block(width: 100%, inset: (x: 9pt, top: 7pt, bottom: 9pt), cuerpo),
  ),
)
#let sistemas(win, mac) = grid(columns: (1fr, 1fr), column-gutter: 10pt,
  panel("Windows", win), panel("Mac", mac))
// Recuadros de nota y de aviso.
#let recuadro(color, fondo-color, titulo, cuerpo) = block(
  width: 100%, fill: fondo-color, inset: (x: 10pt, y: 8pt), radius: (right: 4pt),
  stroke: (left: 3pt + color),
  [#text(weight: "bold", fill: color, titulo) #h(4pt) #cuerpo],
)
#let nota(titulo, cuerpo) = recuadro(azul, azul-claro, titulo, cuerpo)
#let aviso(titulo, cuerpo) = recuadro(naranja, naranja-claro, titulo, cuerpo)
// Captura de pantalla con marco.
#let captura(ruta, alt, pie) = figure(
  box(stroke: 0.6pt + borde, radius: 4pt, clip: true, image(ruta, width: 100%, alt: alt)),
  caption: pie,
)

// --- Portada --------------------------------------------------------------

#block(below: 1.4em)[
  #text(size: 26pt, weight: "bold", fill: azul)[COSTIQ]
  #v(-0.6em)
  #text(size: 14pt, weight: "medium")[Manual de instalación y uso para estudiantes]
  #v(-0.3em)
  #text(size: 9.5pt, fill: gris)[Windows y Mac · COSTIQ #version · #fecha]
]

COSTIQ estima el costo de equipo de proceso con el método de módulo de Turton et al. (2018). Corre en tu computadora y se usa desde el navegador. No necesitas saber programar: sigue los cuatro pasos de este manual.

#nota("Antes de empezar.")[
  Necesitas una computadora con Windows 10 u 11, o una Mac con macOS 12 o más reciente; conexión a internet para la primera instalación; unos 600 MB libres; y 15 minutos. Después de la primera vez, COSTIQ abre en segundos.
]

#v(0.6em)
#let caja(n, t, c) = block(width: 100%, height: 66pt, fill: fondo, stroke: 0.6pt + borde, radius: 5pt,
  inset: (x: 8pt, y: 8pt), [
    #text(size: 18pt, weight: "bold", fill: azul, str(n)) \
    #text(weight: "semibold", t) \
    #text(size: 8.5pt, fill: gris, c)
  ])
#let flecha = align(center + horizon, text(size: 14pt, fill: gris, sym.arrow.r))
#grid(columns: (1fr, 14pt, 1fr, 14pt, 1fr, 14pt, 1fr), align: horizon,
  caja(1, "Instalar Python", "Una sola vez · 5 min"), flecha,
  caja(2, "Descargar COSTIQ", "Una sola vez · 2 min"), flecha,
  caja(3, "Abrir COSTIQ", "Cada vez que la uses"), flecha,
  caja(4, "Usar COSTIQ", "Guarda antes de cerrar"),
)

// --- Paso 1 ---------------------------------------------------------------

#paso(1, "Instalar Python", "Una sola vez")

Si ya tienes Python 3.10 o más reciente, por ejemplo con Anaconda, salta al paso 2.

#sistemas(
  [
    + Abre #link("https://www.python.org/downloads/")[python.org/downloads].
    + Debajo del botón amarillo, en la frase «Or get the standalone installer for Python 3.15.x», haz clic en el enlace #ui("Python 3.15.x").
    + Abre el archivo descargado, `python-3.15.x-amd64.exe`.
    + En la primera pantalla marca la casilla #ui("Add python.exe to PATH") y haz clic en #ui("Install Now").
    + Cuando aparezca «Setup was successful», haz clic en #ui("Close").

    #text(size: 9pt, fill: gris)[Usa este instalador de 64 bits aunque tu laptop tenga procesador ARM (Snapdragon).]
  ],
  [
    + Abre #link("https://www.python.org/downloads/")[python.org/downloads].
    + Haz clic en el botón amarillo #ui("Download Python 3.15.x").
    + Abre el archivo descargado (`.pkg`) y sigue el asistente: #ui("Continuar"), #ui("Aceptar") e #ui("Instalar"). Te pedirá la contraseña de tu Mac.
    + Al terminar se abre una carpeta de Python. Ciérrala, y cierra el instalador.
  ],
)

// --- Paso 2 ---------------------------------------------------------------

#paso(2, "Descargar COSTIQ de GitHub", "Una sola vez")

+ Abre #link(repo)[github.com/lara-montano/COSTIQ].
+ Haz clic en el botón verde #ui("<> Code") y luego en #ui("Download ZIP"). También puedes descargar el ZIP directo desde #link(zip)[este enlace].
+ Descomprime el archivo `COSTIQ-main.zip`:
  - *Windows:* en Descargas, haz clic derecho sobre el ZIP, elige #ui("Extraer todo…") y luego #ui("Extraer").
  - *Mac:* haz doble clic sobre el ZIP. Si usas Safari, ya viene descomprimido.
+ Entra a la carpeta `COSTIQ-main` hasta ver `app.py`, `iniciar_windows.bat` e `iniciar_mac.command`. En Windows puede haber una carpeta `COSTIQ-main` dentro de otra.

#aviso("Dónde guardar la carpeta.")[
  Déjala en Descargas o en otra carpeta de tu disco. Evita OneDrive, iCloud y Dropbox: la instalación crea miles de archivos y la sincronización la vuelve lenta o la rompe.
]

// --- Paso 3 ---------------------------------------------------------------

#paso(3, "Abrir COSTIQ", "Cada vez que la uses")

#sistemas(
  [
    + En la carpeta `COSTIQ-main`, haz doble clic en `iniciar_windows.bat`. Puede aparecer solo como «iniciar_windows».
    + Si Windows muestra un aviso de seguridad:
      - en «Windows protegió tu PC», haz clic en #ui("Más información") y luego en #ui("Ejecutar de todas formas");
      - en «Advertencia de seguridad», haz clic en #ui("Ejecutar").
    + Se abre una ventana negra. La primera vez instala los paquetes de COSTIQ, de 5 a 10 minutos.
    + Al terminar, tu navegador abre COSTIQ.
  ],
  [
    + Abre Terminal: presiona #tecla("⌘") + #tecla("espacio"), escribe `Terminal` y presiona #tecla("Enter").
    + Escribe `bash` seguido de un espacio. Todavía no presiones #tecla("Enter").
    + Arrastra el archivo `iniciar_mac.command` desde la carpeta `COSTIQ-main` hasta la ventana de Terminal. Ahora presiona #tecla("Enter").
    + La primera vez instala los paquetes de COSTIQ, de 5 a 10 minutos. Al terminar, tu navegador abre COSTIQ.

    #text(size: 9pt, fill: gris)[No uses doble clic: macOS bloquea los archivos de comandos descargados de internet. Con `bash` se evita ese bloqueo.]
  ],
)

#v(0.4em)
Sabrás que funcionó cuando el navegador muestre COSTIQ en la dirección `http://localhost:8501` (Figura 1). Si el navegador no se abre solo, copia esa dirección en él.

#aviso("No cierres la ventana negra ni Terminal.")[
  Esa ventana es la que hace funcionar COSTIQ. Si la cierras, la app se detiene.
]

== Cerrar y volver a abrir

- *Antes de cerrar*, guarda tu proyecto con #ui("Guardar proyecto") (paso 4).
- *Cerrar:* en Windows, cierra la ventana negra. En Mac, presiona #tecla("control") + #tecla("C") en Terminal y luego cierra la ventana. Cerrar la pestaña del navegador no apaga COSTIQ.
- *Volver a abrir:* repite este paso 3. Ya no instala nada y abre en segundos.

#captura("img/app_equipo.png",
  "Pantalla de COSTIQ en la pestaña Equipo, con la barra lateral a la izquierda y el costo del equipo a la derecha.",
  [COSTIQ recién abierto. A la izquierda, la barra lateral con el CEPCI y la moneda. Arriba, las pestañas Equipo, Planta y Referencia. A la derecha, el costo de módulo del equipo elegido y la cascada que lo explica.],
)

// --- Paso 4 ---------------------------------------------------------------

#paso(4, "Usar COSTIQ", "Guarda antes de cerrar")

COSTIQ tiene una barra lateral y tres pestañas.

#table(
  columns: (auto, 1fr),
  stroke: none,
  inset: (x: 6pt, y: 5pt),
  table.hline(stroke: 0.8pt),
  table.header([*Zona*], [*Para qué sirve*]),
  table.hline(stroke: 0.5pt),
  [Barra lateral], [Año del CEPCI u #ui("Otro valor…"); moneda USD o MXN con tipo de cambio; factores de las Ecs. 7.15 y 7.16.],
  [Equipo], [Costear un equipo: categoría, tipo, tamaño, material y presión. Muestra el costo de módulo C#sub[BM], sus factores, la sensibilidad y el #ui("Cálculo paso a paso").],
  [Planta], [Lista de equipos agregados y costos de planta: ΣC#sub[BM], C#sub[TM] y C#sub[GR]. Guardar, abrir y exportar.],
  [Referencia], [Catálogo de equipos del Apéndice A, factores de material y de módulo, e índices CEPCI.],
  table.hline(stroke: 0.8pt),
)

== Costear una planta

+ En la barra lateral, elige el año del CEPCI y la moneda.
+ En la pestaña #ui("Equipo"), elige la #ui("Categoría") y el #ui("Tipo"). Escribe el tamaño y las #ui("Unidades idénticas").
+ Elige el material de construcción y la presión de operación. Lee las advertencias que aparezcan, por ejemplo cuando el tamaño queda fuera del rango de la correlación.
+ Revisa el resultado a la derecha. Abre #ui("Cálculo paso a paso") para ver las ecuaciones con tus números.
+ Escribe la #ui("Etiqueta en el DFP"), por ejemplo E-101, y haz clic en #ui("Agregar a la planta").
+ Repite los pasos 2 a 5 con cada equipo.
+ En la pestaña #ui("Planta"), revisa ΣC#sub[BM], C#sub[TM] (para ampliaciones) y C#sub[GR] (para una planta nueva).
+ Guarda tu trabajo con #ui("Guardar proyecto"). Se descarga un archivo `.json` que puedes abrir después con #ui("Abrir proyecto"). El botón #ui("CSV") descarga la tabla para Excel.

#aviso("COSTIQ no guarda solo.")[
  Si cierras la ventana o recargas la página sin usar #ui("Guardar proyecto"), pierdes la planta.
]

#captura("img/app_planta.png",
  "Pestaña Planta con siete equipos, los costos de planta, la composición del costo grassroots y el inventario.",
  [Pestaña Planta con el Ejemplo 7.14 de Turton cargado: costos de planta arriba, composición del C#sub[GR] y el inventario de equipos con los botones para quitar, guardar y exportar.],
)

== Consejos

- Para practicar, abre la pestaña #ui("Planta") vacía y haz clic en #ui("Cargar el Ejemplo 7.14").
- Para un equipo sin correlación en el Apéndice A, como un molino o un extrusor, usa la categoría #ui("Cotización propia"). COSTIQ escala un precio de referencia con la Ec. 7.1.
- Para quitar equipos, selecciona sus filas en el inventario y usa #ui("Quitar"). #ui("Vaciar planta") borra todos.
- Si cambias el CEPCI o la moneda, COSTIQ recalcula toda la planta.

// --- Problemas ------------------------------------------------------------

= Problemas frecuentes

#table(
  columns: (0.85fr, 1.15fr),
  stroke: none,
  inset: (x: 6pt, y: 5.5pt),
  table.hline(stroke: 0.8pt),
  table.header([*Lo que ves*], [*Qué hacer*]),
  table.hline(stroke: 0.5pt),
  [«No encontré Python 3.10 o más reciente»],
  [Instala Python (paso 1). En Windows usa el instalador de 64 bits. Luego abre COSTIQ otra vez.],
  table.hline(stroke: 0.3pt + borde),
  [«No encuentro app.py»],
  [Abriste el lanzador desde dentro del ZIP. Extrae el ZIP (paso 2) y usa el lanzador de la carpeta extraída.],
  table.hline(stroke: 0.3pt + borde),
  [La instalación se detiene con un error de conexión],
  [Revisa tu internet. Algunas redes escolares bloquean descargas: prueba otra red. Abre COSTIQ otra vez y la instalación continúa.],
  table.hline(stroke: 0.3pt + borde),
  [La instalación tarda mucho o falla en OneDrive, iCloud o Dropbox],
  [Mueve la carpeta `COSTIQ-main` a Descargas y abre COSTIQ otra vez.],
  table.hline(stroke: 0.3pt + borde),
  [Mac: «no se puede abrir porque proviene de un desarrollador no identificado»],
  [Lo abriste con doble clic. Usa Terminal con `bash` (paso 3).],
  table.hline(stroke: 0.3pt + borde),
  [Mac: una ventana pide instalar «herramientas de desarrollo»],
  [Haz clic en #ui("Cancelar") e instala Python desde python.org (paso 1).],
  table.hline(stroke: 0.3pt + borde),
  [El navegador dice «No se puede acceder a este sitio»],
  [Se cerró la ventana negra o Terminal. Abre COSTIQ otra vez (paso 3).],
  table.hline(stroke: 0.3pt + borde),
  [La app abre en `localhost:8502` y no en `8501`],
  [Ya tenías COSTIQ abierto en otra ventana. Usa la dirección que muestra la ventana nueva, o cierra la anterior.],
  table.hline(stroke: 0.3pt + borde),
  [Perdí mi planta],
  [COSTIQ no guarda solo. Usa #ui("Guardar proyecto") y después #ui("Abrir proyecto").],
  table.hline(stroke: 0.3pt + borde),
  [Mi Mac tiene macOS 11 o anterior],
  [Los paquetes de COSTIQ requieren macOS 12 o más reciente. Usa otra computadora.],
  table.hline(stroke: 0.3pt + borde),
  [Otro error],
  [Toma una captura de toda la ventana negra o de Terminal y envíala a tu profesor.],
  table.hline(stroke: 0.8pt),
)

// --- Anexo ----------------------------------------------------------------

= Anexo: instalación con git y terminal

Esta sección es opcional, para quien ya usa git. Después de clonar el repositorio también puedes usar los lanzadores del paso 3.

```
git clone https://github.com/lara-montano/COSTIQ.git
cd COSTIQ
```

#block(breakable: false)[
  *Windows*, en PowerShell:

  ```
  py -m venv .venv
  .venv\Scripts\python -m pip install -r requirements.txt
  .venv\Scripts\python -m streamlit run app.py
  ```
]

#block(breakable: false)[
  *Mac*, en Terminal. Antes revisa que `python3 --version` muestre 3.10 o más reciente:

  ```
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
  .venv/bin/python -m streamlit run app.py
  ```
]

Para actualizar a la versión más reciente, ejecuta `git pull` dentro de la carpeta `COSTIQ`.

#v(1.2em)
#line(length: 100%, stroke: 0.5pt + borde)
#text(size: 8.5pt, fill: gris)[
  COSTIQ #version · Oscar Daniel Lara-Montaño (Universidad Autónoma de Querétaro), Fernando Israel Gómez-Castro y Sergio Iván Martínez-Guido (Universidad de Guanajuato). Licencia MIT. Método: Turton, R., Shaeiwitz, J. A., Bhattacharyya, D. y Whiting, W. B. (2018). _Analysis, Synthesis, and Design of Chemical Processes_, 5.ª ed., Pearson, Apéndice A. Código fuente: #link(repo)[github.com/lara-montano/COSTIQ].
]
