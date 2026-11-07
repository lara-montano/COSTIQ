# Auditoría de COSTIQ v1.0.0

Fecha: 2026-11-07. Versión auditada: commit `b6e478b` (`app.py` 1,110 líneas, `data.py` 544 líneas).
Fuente de verdad: Turton, Shaeiwitz, Bhattacharyya y Whiting (2018), *Analysis, Synthesis, and Design of Chemical Processes*, 5.ª ed., Apéndice A y Sección 7.3.

## 1. Método

1. Comparé cada constante de `data.py` contra el texto de las Tablas A.1, A.2, A.4, A.5 y A.7.
2. Las Figuras A.18 (factor de material, F_M) y A.19 (factor de módulo desnudo, F_BM) solo existen como gráficas. Las digitalicé a partir de la imagen del libro, con detección automática de cada punto. La resolución es de ±0.03 en F_M y ±0.04 en F_BM. Los puntos que el libro cita en texto (F_M = 2.73, 3.11, 1.81, 1.55; F_BM = 1.83) coinciden con la digitalización dentro de esa tolerancia.
3. Ejecuté el motor de cálculo original sobre el Ejemplo 7.14 del libro (columna con condensador, rehervidor, enfriador, bombas, platos y tanque de reflujo), que reporta F_P, F_M, F_BM, C_p°, C_BM y C°_BM para siete equipos.

## 2. Resultado global

Las 36 ternas K₁–K₃ y todas las constantes C₁–C₃ de presión coinciden con el libro. Los errores están en los factores de material, en los factores de módulo, en la presión de recipientes y en la definición del costo grassroots.

Contra el Ejemplo 7.14, el código original subestima ΣC_BM(2001) en 3.1 % (772,278 frente a 797,000 USD). Lo que la app llama "C_GR" subestima el C_GR del libro en 26.5 % (1,244,126 frente a 1,692,000 USD de 2016).

| Equipo | F_M v1 | F_P v1 | C_BM v1 (USD 2001) | Libro | Desviación |
|---|---:|---:|---:|---:|---:|
| E-101 cabezal flotante | 1.00 | 1.000 | 108,495 | 108,500 | 0.0 % |
| E-102 cabezal flotante | 1.81 | 1.062 | 177,804 | 177,900 | −0.1 % |
| E-103 doble tubo | 1.00 | 1.000 | 12,271 | 12,300 | −0.2 % |
| P-101 A/B centrífuga (×2) | 1.35 | 1.000 | 23,578 | 25,200 | −6.4 % |
| T-101 torre | 1.00 | 1.484 | 271,020 | 290,700 | −6.8 % |
| 32 platos perforados SS | — | — | 131,432 | 131,200 | +0.2 % |
| V-101 horizontal | 1.00 | 1.343 | 47,678 | 51,200 | −6.9 % |

## 3. Hallazgos de cálculo

Severidad: **bloqueante** (resultado incorrecto que un usuario no puede detectar), **mayor** (resultado incorrecto en casos frecuentes o etiqueta engañosa), **menor** (precisión, consistencia o ergonomía).

### 3.1 Bloqueantes

**B1. "C_GR" no es el costo grassroots.** `app.py:520` y `app.py:718` calculan C_BM × (1 + f₁ + f₂). Esa es la definición del costo de módulo total, C_TM (Ec. 7.15, con 15 % de contingencia y 3 % de honorarios). El costo grassroots es C_GR = C_TM + 0.50 ΣC°_BM (Ec. 7.16), donde C°_BM es el costo de módulo a condiciones base (acero al carbón, presión ambiente). Falta el término de instalaciones auxiliares, que en el Ejemplo 7.14 vale 408,000 USD de 2016 (24 % del C_GR).

**B2. Factores de material de intercambiadores, enfriadores de aire, recipientes y bombas.** `data.py:248-309`. Valores de v1 frente a la Figura A.18:

| Tabla | Material | v1 | Fig. A.18 (ID) |
|---|---|---:|---:|
| Coraza y tubos | CS/Ti | 3.17 | 4.63 (8) |
| Coraza y tubos | Ti/Ti | 4.63 | 11.38 (9) |
| Enfriador de aire | Al | 1.00 | 1.42 (11) |
| Enfriador de aire | SS | 2.17 | 2.93 (12) |
| Recipientes | Ni alloy | 6.44 | 7.07 (22) |
| Recipientes | Ti | 7.89 | 9.40 (24) |
| Bomba centrífuga | CS | 1.35 | 1.55 (38) |
| Bomba centrífuga | SS | 2.00 | 2.28 (39) |
| Bomba centrífuga | Ni alloy | 3.50 | 4.36 (40) |
| Bomba desplaz. positivo | Cu alloy / SS / Ni / Ti | 1.50 / 2.20 / 3.50 / 9.60 | 1.28 / 2.67 / 4.74 / 10.66 (33–36) |
| Bomba reciprocante | CS / Cu / SS / Ni / Ti | 1.40 / 1.50 / 2.20 / 3.50 / 9.60 | 1.46 / 1.28 / 2.35 / 3.95 / 6.44 (26–30) |

En v1, las tablas de bombas de desplazamiento positivo y reciprocantes son idénticas. En el libro no lo son.

**B3. Factores de módulo de compresores, turbinas y platos.** `data.py:346-420`. Frente a la Figura A.19:

| Equipo | v1 (CS / SS / Ni) | Fig. A.19 (CS / SS / Ni) |
|---|---|---|
| Compresor centrífugo | 2.15 / 5.80 / 11.50 | 2.73 / 5.75 / 11.45 |
| Compresor axial | (mismo que centrífugo) | 3.83 / 8.04 / 15.93 |
| Compresor reciprocante | (mismo que centrífugo) | 3.37 / 7.00 / 13.89 |
| Compresor rotatorio | 2.15 / 5.80 / 11.50 | 2.41 / 5.04 / 9.85 |
| Turbinas de recuperación | 3.40 / 6.10 / 11.70 | 3.50 / 6.12 / 11.66 |
| Platos perforados y de válvula, Ni | 3.20 | 5.58 |
| Eliminador de niebla, Ni | 2.40 | 5.58 |

v1 agrupa los compresores centrífugos, axiales y reciprocantes en un solo equipo. Comparten la correlación de C_p°, pero el libro les asigna F_BM distintos; el axial con CS cuesta 78 % más que lo que reporta v1.

La turbina de vapor (`data.py:203`) está como turbina de recuperación de potencia con opción de material. En el libro es un *accionamiento* (Tabla A.6, ID 17) con F_BM = 3.5 fijo.

### 3.2 Mayores

**M1. Factor de presión de recipientes con P manométrica en lugar de (P + 1).** `app.py:41-58`. El código implementa la Ec. A.2 tal como se imprimió en la 5.ª edición, con P. Los Ejemplos 7.13 y 7.14 del mismo libro, y la 4.ª edición, usan (P + 1). Con P la torre T-101 da F_P = 1.484; con (P + 1) da 1.682, el valor del libro. El paréntesis vacío "0.6(P)" de la ecuación impresa sugiere que el "+1" se perdió en la edición. v2 adopta (P + 1) para reproducir los ejemplos y documenta la discrepancia.

**M2. Presión fuera de rango produce F_P = 1.** `app.py:79-107`. Si P supera el rango tabulado (p. ej., 150 barg en un intercambiador), `get_fp` devuelve 1.0. El costo *baja* al aumentar la presión, y la gráfica de sensibilidad a presión muestra un salto. El libro pide extrapolar "con extrema precaución", no anular el efecto. v2 extrapola con la última correlación y lo marca como advertencia visible.

**M3. Validez de la Ec. A.2.** `app.py:51-56` devuelve F_P = 50 por encima de ~1,417 barg. El libro limita la ecuación a espesores menores que D/4, unos 320 barg para D entre 0.3 y 4 m. v2 calcula el espesor y advierte cuando t > D/4.

**M4. Volumen y diámetro independientes.** En recipientes y torres el usuario escribe el volumen y, por separado, el diámetro. Nada impide un recipiente de 0.3 m³ con 4 m de diámetro. v2 pide D y longitud o altura, y calcula V = πD²L/4, como hacen los ejemplos del libro.

**M5. Etiquetas de lado de presión en intercambiadores.** `app.py:424-431`. Las opciones "shell" y "tube" corresponden en la Tabla A.2 a "ambos lados (coraza y tubos)" y "solo tubos". No existe una correlación para "solo coraza". v2 usa las etiquetas del libro.

**M6. Torre y platos desconectados.** El libro costea la torre y sus platos por separado y los suma (Ejemplo 7.13). En v1 el usuario debe calcular a mano el área del plato y agregar dos equipos sin relación. v2 permite costear la torre con sus platos en un solo paso y usa el mismo diámetro para ambos.

### 3.3 Menores

**m1. CEPCI 2001.** `data.py:11`. La entrada "2001: 397.0" es el promedio de mayo a septiembre de 2001 (la base del libro), no el promedio anual (394.3). v2 separa la base del índice anual y permite escribir un CEPCI propio (p. ej., el mensual de 2026). Los valores de 2002 a 2024 no los pude verificar contra *Chemical Engineering*; quedan marcados como tales en el código.

**m2. Hornos.** F_BM de v1: 2.19 / 2.47 / 2.75. Fig. A.19: 2.13 / 2.50 / 2.81. Diferencia de 3 % o menos.

**m3. Tanques API.** El Apéndice A no tabula F_BM para tanques. v1 usa 1.0 sin decirlo. v2 conserva 1.0, lo declara como supuesto y deja editar el valor.

**m4. Reactores.** El F_BM = 4.0 de la Tabla A.7 está marcado en el libro como estimación. v2 lo indica en la interfaz.

**m5. Capacidad fuera de rango bloqueada.** El campo de capacidad no acepta valores fuera del rango de la correlación. El libro recomienda usar varias unidades en paralelo. v2 agrega el número de unidades idénticas (p. ej., P-101 A/B) y advierte la extrapolación en lugar de bloquearla.

**m6. Enlace de reporte de errores.** `app.py:1106` apunta a `estimador_costos/issues`, el repositorio predecesor.

## 4. Hallazgos de ingeniería de software

1. **Motor y UI mezclados.** Todo el cálculo vive en `app.py` junto con Streamlit. No se puede importar ni probar sin levantar la app. Es la condición de reactivación que dejaste en el `plan.md` del artículo: "paquete importable con tests".
2. **Sin pruebas.** Ningún caso del libro se verifica de forma automática. Los errores B2 y B3 habrían aparecido con un solo caso de prueba.
3. **Datos duplicados.** Las bandas de presión de cinco intercambiadores están copiadas cinco veces (`data.py:429-458`). Un error al corregir una copia no se propaga a las demás.
4. **Sin trazabilidad.** Ningún valor indica de qué tabla o identificador del libro viene.
5. **Dependencias sin acotar.** `requirements.txt` fija solo mínimos. Con Streamlit ≥ 1.47, `use_container_width` emite advertencias de obsolescencia en cada gráfica.

## 5. Hallazgos de diseño visual y de interacción

1. **Tema roto en modo claro.** Las tarjetas usan fondos oscuros fijos (`#0e1117`, `#161b22`) y las gráficas fuerzan `plotly_dark`, pero no hay archivo de tema. En modo claro aparecen bloques negros sobre fondo blanco.
2. **Sin jerarquía.** Siete métricas del mismo tamaño compiten por la atención. El dato principal, C_BM, pesa lo mismo que el CEPCI.
3. **Paleta sin sistema.** El encabezado usa un degradado azul petróleo, las tarjetas de totales verde, azul y morado, la gráfica de pastel diez colores. El rojo marca el material seleccionado, cuando el rojo comunica error.
4. **Pastel para comparar costos.** Con más de cuatro equipos, las rebanadas no se pueden comparar y las etiquetas exteriores se enciman. Una barra horizontal ordenada (Pareto) comunica mejor qué equipo domina el costo.
5. **Inventario sin encabezados.** Cada fila es un `st.columns` independiente: no hay encabezados, las columnas no se alinean y el botón de borrar es un emoji.
6. **Emojis como iconografía.** Catorce emojis en pestañas, botones y avisos. Se ven distintos en cada sistema operativo y restan seriedad a una herramienta técnica.
7. **No se explica el costo.** Se muestran factores sueltos, pero no cómo se pasa de C_p° a C_BM de hoy. Una cascada de costos (compra, instalación base, material y presión, inflación) explica el número en una sola vista.

## 6. Qué cambia en v2

| Área | Cambio |
|---|---|
| Datos | F_M y F_BM corregidos con trazabilidad al ID de Tabla A.3/A.6; compresores separados por tipo; accionamientos como categoría propia; empaque de torre, tanque de inóculo y mezclador-sedimentador agregados. |
| Cálculo | C_TM y C_GR según Ecs. 7.15 y 7.16; F_P de recipientes con (P + 1); extrapolación de presión y capacidad con advertencia; espesor y validez t < D/4; torre con platos; unidades en paralelo; CEPCI propio. |
| Software | Paquete `costiq/` importable (`data`, `engine`), UI separada, 164 pruebas con `pytest` que reproducen los Ejemplos 7.10 a 7.14. |
| Interfaz | Tema claro y oscuro con tokens de color, tipografía IBM Plex, jerarquía de una cifra principal, cascada de costos, Pareto del inventario, tabla de inventario editable, iconos Material en lugar de emojis. |

## 7. Lo que v2 no resuelve

1. Los F_M y F_BM digitalizados tienen ±0.03–0.04 de incertidumbre. Si tienes la hoja CAPCOST 2017, conviene comparar contra sus valores exactos.
2. Los CEPCI 2002–2024 siguen sin verificarse contra la fuente primaria.
3. Ventiladores, evaporadores, vaporizadores y calentadores de fluido térmico no están incluidos. Sus correlaciones están en las Tablas A.1 y A.2 y son la siguiente ampliación natural.
4. Dos rasgos de las correlaciones del libro se conservan tal cual: el F_P de doble tubo, tubos múltiples y pared raspada baja 2.5 % entre 100 y 130 barg, y F_q salta de 1.04 a 1.00 entre 19 y 20 platos. Ambos están documentados en las pruebas.

## 8. Resultado de v2 contra el Ejemplo 7.14

Con CEPCI = 542, v2 obtiene ΣC_BM = 1,088,399 USD, C_TM = 1,284,311 USD y C_GR = 1,692,466 USD. El libro reporta 1,088,100, 1,284,000 y 1,692,000 USD (diferencia de 0.03 % o menos, atribuible al redondeo de C_p° en el libro).
