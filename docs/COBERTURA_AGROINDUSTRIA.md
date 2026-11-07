# Cobertura de COSTIQ para Operaciones Unitarias I y II (Ingeniería Agroindustrial, UAQ Amealco)

Versión 2.1.0, 2026-11-07. Temarios: OU I (U1–U7, 2026-2) y OU II (evaporación, secado, pasteurización y esterilización, refrigeración y congelación, 2026-1).

"Turton" significa que el equipo usa las correlaciones del Apéndice A, con la misma base (CEPCI = 397) y los mismos factores que el resto del catálogo. "Cotización propia" significa que el usuario captura un precio de referencia y COSTIQ lo escala con la Ec. 7.1 y lo actualiza con el CEPCI.

| Unidad | Equipo | En COSTIQ | Fuente |
|---|---|---|---|
| OU I-1 Transporte y almacenamiento de sólidos | Banda, tornillo, placas, neumático | Sí | Turton, Tablas A.1 y A.7 |
| | Elevador de cangilones, silos, tolvas | Cotización propia | — |
| OU I-2 Reducción de tamaño | Quebradoras, molinos | Cotización propia | — |
| OU I-3 Clasificación por tamaños | Criba curva, rotatoria, estacionaria, vibratoria | Sí | Turton, Tablas A.1 y A.7 |
| OU I-4 Filtración y ultrafiltración | Filtro prensa, de hojas, de tambor y disco, cartucho, gravedad, charola, mesa, tubular | Sí | Turton, Tablas A.1 y A.7 |
| | Membranas de ultrafiltración | Cotización propia | — |
| OU I-5 Sedimentación y flotación | Espesadores, clarificadores, celdas de flotación | Cotización propia | — |
| | Ciclones y colectores de polvo (separación gas–sólido) | Sí | Turton, Tablas A.1 y A.7 |
| OU I-6 Centrifugación | Separador centrífugo, tazón sólido, automático por lotes, criba oscilante | Sí | Turton, Tablas A.1 y A.7 |
| OU I-7 Extrusión | Extrusores | Cotización propia | — |
| OU II Evaporación | Película descendente, película agitada, circulación forzada, tubo corto, tubo largo | Sí, con material y presión | Turton, Tablas A.1, A.2 y A.6 |
| OU II Secado | Tambor, rotatorio de gas directo, charolas | Sí | Turton, Tablas A.1 y A.7 |
| | Secador por aspersión | Cotización propia | — |
| OU II Pasteurización y esterilización | Intercambiadores de placas y de coraza y tubos | Sí | Turton, Tablas A.1–A.4 |
| | Calderas de vapor, calentadores de agua caliente | Sí | Turton, Tablas A.1, A.2, A.5 y A.6 (F_BM de caldera supuesto) |
| | Marmitas enchaquetadas, autoclaves | Sí | Turton, Tablas A.1, A.2, A.6 y A.7 |
| OU II Refrigeración y congelación | Compresores, motores, ventiladores, intercambiadores | Sí | Turton |
| | Paquete de refrigeración, túneles y cámaras de congelación | Cotización propia | — |
| Transversales | Mezcladores, amasadoras, agitadores, cristalizadores, bombas, tanques | Sí | Turton, Tablas A.1 y A.7 |

## Supuestos de los equipos agregados en 2.1.0

- Los F_BM de evaporadores, vaporizadores y ventiladores se digitalizaron de la Figura A.19 (±0.04).
- La Tabla A.7 marca como estimaciones los F_BM de amasadoras, mezcladores de listones, agitadores de impulsor, transporte neumático, cribas curva, rotatoria y estacionaria, la mayoría de los filtros, dos centrífugas y todos los colectores de polvo. COSTIQ lo indica en la interfaz.
- La Tabla A.6 no da F_BM para calderas de vapor. COSTIQ supone 2.16, el del calentador de fluido térmico (ID 56), y permite cambiarlo.
- El primer tramo de presión de los evaporadores aparece impreso como "P < 0"; la correlación da F_P = 1.000 en 10 barg, así que COSTIQ usa P < 10 barg.
- Los ventiladores se corrigen por aumento de presión ΔP en kPa, no por presión manométrica.

## Siguiente paso posible

Los equipos marcados como "Cotización propia" podrían tener correlación propia tomando Towler y Sinnott (2021, Tabla 7.2) o Couper et al. (2009, Tabla 21.2). Ambos usan otra base de costo y otra definición de los factores de instalación. Para integrarlos sin volver inconsistente el C_GR, cada equipo debe declarar su fuente y su conversión.
