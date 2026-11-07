# Registro de cambios

## 2.0.0 — 2026-11-07

### Correcciones de cálculo

- El costo grassroots ahora es C_GR = C_TM + 0.50 ΣC°_BM (Ec. 7.16). La v1 llamaba "C_GR" al costo de módulo total.
- Factores de material corregidos según la Fig. A.18: coraza y tubos con Ti, enfriadores de aire con Al y SS, recipientes de Ni y Ti, y las tres tablas de bombas.
- Factores de módulo corregidos según la Fig. A.19: compresores (ahora separados en centrífugo, axial, reciprocante y rotatorio), turbinas, platos y eliminadores de Ni y hornos.
- F_P de recipientes con (P + 1), como en los Ejemplos 7.13 y 7.14.
- Fuera del rango de la Tabla A.2, F_P se extrapola y se marca; ya no cae a 1.0.
- Advertencia de pared gruesa cuando el espesor supera D/4.
- La turbina de vapor pasa a "Accionamientos" con F_BM = 3.5.

### Nuevo

- Paquete `costiq` importable, separado de la interfaz, con 164 pruebas.
- Accionamientos (6 tipos), empaque de torre, tanque de inóculo y mezclador-sedimentador: 46 equipos en total.
- Recipientes y torres por diámetro y longitud; torre con platos o empaque en un solo paso.
- Unidades en paralelo, capacidad fuera de rango con advertencia, CEPCI propio y factores de planta editables.
- Cascada de costos, sensibilidad por capacidad, presión, material y año, Pareto de la planta y composición del C_GR.
- Proyectos en JSON (guardar y abrir), exportación a CSV y carga del Ejemplo 7.14.
- Interfaz rediseñada: tema propio, tipografía IBM Plex, paleta validada para daltonismo, iconos Material y diseño adaptable a teléfono.

## 1.0.0 — 2026-04-07

Versión inicial.
