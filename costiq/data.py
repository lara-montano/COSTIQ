"""Datos de costeo de equipos de Turton et al. (2018), Apéndice A.

Turton, R., Shaeiwitz, J. A., Bhattacharyya, D., y Whiting, W. B. (2018).
*Analysis, Synthesis, and Design of Chemical Processes*, 5.ª ed. Pearson.

Fuentes por tipo de dato:

- K1, K2, K3 y rangos de capacidad: Tabla A.1 (texto del libro).
- C1, C2, C3 y rangos de presión: Tabla A.2 (texto del libro).
- B1, B2: Tabla A.4 (texto del libro).
- F_M de intercambiadores, recipientes y bombas: Figura A.18, con los
  identificadores de la Tabla A.3. Digitalizados de la figura (±0.03).
- F_BM del resto de equipos: Figura A.19, con los identificadores de la
  Tabla A.6. Digitalizados de la figura (±0.04).
- F_BM de reactores: Tabla A.7 (marcados en el libro como estimaciones).

Los costos de compra están referidos a CEPCI = 397 (promedio de mayo a
septiembre de 2001).
"""

from __future__ import annotations

from dataclasses import dataclass

CEPCI_BASE = 397.0
"""CEPCI de referencia de las correlaciones (promedio mayo-septiembre 2001)."""

# Promedios anuales del Chemical Engineering Plant Cost Index.
# 2001 es el promedio anual (394.3); la base de las correlaciones es 397.
# Pendiente: verificar 2002-2024 contra la revista Chemical Engineering.
CEPCI: dict[int, float] = {
    2001: 394.3,
    2002: 395.6,
    2003: 402.0,
    2004: 444.2,
    2005: 468.2,
    2006: 499.6,
    2007: 525.4,
    2008: 575.4,
    2009: 521.9,
    2010: 550.8,
    2011: 585.7,
    2012: 584.6,
    2013: 567.3,
    2014: 576.1,
    2015: 556.8,
    2016: 541.7,
    2017: 567.5,
    2018: 603.1,
    2019: 607.5,
    2020: 596.2,
    2021: 708.0,
    2022: 816.0,
    2023: 797.9,
    2024: 800.8,
}

# Parámetros de la Ec. A.2 (recipientes, código ASME), Sección A.2.1.
VESSEL_S_BAR = 944.0       # esfuerzo máximo permisible del acero al carbón
VESSEL_E = 0.9             # eficiencia de soldadura
VESSEL_CA_M = 0.00315      # tolerancia a corrosión (1/8 in)
VESSEL_TMIN_M = 0.0063     # espesor mínimo de pared (1/4 in)
VESSEL_VACUUM_P = -0.5     # por debajo de esta presión (barg), F_P = 1.25
VESSEL_VACUUM_FP = 1.25

# Factores de costo de módulo total y grassroots (Ecs. 7.15 y 7.16).
F_CONTINGENCY = 0.15
F_FEE = 0.03
F_AUXILIARY = 0.50


@dataclass(frozen=True)
class Material:
    """Opción de material con su factor y el identificador del libro."""

    code: str
    label: str
    factor: float
    ref: str = ""


@dataclass(frozen=True)
class PressureBand:
    """Tramo de la Ec. A.3: log10 F_P = C1 + C2 log10 P + C3 (log10 P)^2."""

    p_max: float
    C1: float = 0.0
    C2: float = 0.0
    C3: float = 0.0

    @property
    def is_flat(self) -> bool:
        return self.C1 == 0.0 and self.C2 == 0.0 and self.C3 == 0.0


@dataclass(frozen=True)
class PressureOption:
    """Correlación de presión aplicable (p. ej., "ambos lados" o "solo tubos")."""

    key: str
    label: str
    bands: tuple[PressureBand, ...]

    @property
    def p_max(self) -> float:
        return self.bands[-1].p_max


@dataclass(frozen=True)
class Equipment:
    """Un tipo de equipo con todo lo necesario para costearlo."""

    key: str
    category: str
    name: str
    name_en: str
    K1: float
    K2: float
    K3: float
    attribute: str
    unit: str
    a_min: float
    a_max: float
    method: str  # "B1B2", "vessel", "FBM", "FBM_FP", "tray"
    materials: tuple[Material, ...]
    B1: float | None = None
    B2: float | None = None
    pressure: tuple[PressureOption, ...] = ()
    pressure_label: str = "Presión de operación"
    geometry: str | None = None  # "horizontal" o "vertical" para recipientes
    note: str = ""

    @property
    def has_pressure(self) -> bool:
        return self.method == "vessel" or any(
            not band.is_flat for opt in self.pressure for band in opt.bands
        )

    @property
    def pressure_limit(self) -> float | None:
        """Máxima presión del rango tabulado (None si no aplica)."""
        if not self.pressure:
            return None
        return max(opt.p_max for opt in self.pressure)

    def material(self, code: str) -> Material:
        for m in self.materials:
            if m.code == code:
                return m
        raise KeyError(f"{self.name}: material desconocido '{code}'")

    def pressure_option(self, key: str | None) -> PressureOption | None:
        if not self.pressure:
            return None
        if key is None:
            return self.pressure[0]
        for opt in self.pressure:
            if opt.key == key:
                return opt
        raise KeyError(f"{self.name}: opción de presión desconocida '{key}'")

    @property
    def base_material(self) -> Material:
        """Material de condiciones base para C°_BM (factor mínimo)."""
        return min(self.materials, key=lambda m: m.factor)


# ---------------------------------------------------------------------------
# Factores de material, Figura A.18 / Tabla A.3 (usados con B1 y B2)
# ---------------------------------------------------------------------------

FM_SHELL_TUBE = (
    Material("CS/CS", "Coraza CS · tubos CS", 1.00, "Tabla A.3, ID 1"),
    Material("CS/Cu", "Coraza CS · tubos Cu", 1.35, "Tabla A.3, ID 2"),
    Material("Cu/Cu", "Coraza Cu · tubos Cu", 1.69, "Tabla A.3, ID 3"),
    Material("CS/SS", "Coraza CS · tubos SS", 1.81, "Tabla A.3, ID 4"),
    Material("SS/SS", "Coraza SS · tubos SS", 2.73, "Tabla A.3, ID 5"),
    Material("CS/Ni", "Coraza CS · tubos de aleación de Ni", 2.68, "Tabla A.3, ID 6"),
    Material("Ni/Ni", "Coraza y tubos de aleación de Ni", 3.73, "Tabla A.3, ID 7"),
    Material("CS/Ti", "Coraza CS · tubos Ti", 4.63, "Tabla A.3, ID 8"),
    Material("Ti/Ti", "Coraza Ti · tubos Ti", 11.38, "Tabla A.3, ID 9"),
)

FM_AIR_COOLER = (
    Material("CS", "Tubos de acero al carbón", 1.00, "Tabla A.3, ID 10"),
    Material("Al", "Tubos de aluminio", 1.42, "Tabla A.3, ID 11"),
    Material("SS", "Tubos de acero inoxidable", 2.93, "Tabla A.3, ID 12"),
)

FM_PLATE = (
    Material("CS", "Acero al carbón", 1.00, "Tabla A.3, ID 13"),
    Material("Cu", "Cobre", 1.35, "Tabla A.3, ID 14"),
    Material("SS", "Acero inoxidable", 2.45, "Tabla A.3, ID 15"),
    Material("Ni", "Aleación de níquel", 2.68, "Tabla A.3, ID 16"),
    Material("Ti", "Titanio", 4.63, "Tabla A.3, ID 17"),
)

FM_TEFLON = (Material("Teflon", "Teflón", 1.00, "Sin variación de material"),)

FM_VESSEL = (
    Material("CS", "Acero al carbón", 1.00, "Tabla A.3, ID 18"),
    Material("SS clad", "Recubierto de acero inoxidable", 1.74, "Tabla A.3, ID 19"),
    Material("SS", "Acero inoxidable", 3.11, "Tabla A.3, ID 20"),
    Material("Ni clad", "Recubierto de aleación de Ni", 3.62, "Tabla A.3, ID 21"),
    Material("Ni", "Aleación de níquel", 7.07, "Tabla A.3, ID 22"),
    Material("Ti clad", "Recubierto de titanio", 4.68, "Tabla A.3, ID 23"),
    Material("Ti", "Titanio", 9.40, "Tabla A.3, ID 24"),
)

FM_PUMP_RECIPROCATING = (
    Material("CI", "Hierro fundido", 1.00, "Tabla A.3, ID 25"),
    Material("CS", "Acero al carbón", 1.46, "Tabla A.3, ID 26"),
    Material("Cu alloy", "Aleación de cobre", 1.28, "Tabla A.3, ID 27"),
    Material("SS", "Acero inoxidable", 2.35, "Tabla A.3, ID 28"),
    Material("Ni", "Aleación de níquel", 3.95, "Tabla A.3, ID 29"),
    Material("Ti", "Titanio", 6.44, "Tabla A.3, ID 30"),
)

FM_PUMP_PD = (
    Material("CI", "Hierro fundido", 1.00, "Tabla A.3, ID 31"),
    Material("CS", "Acero al carbón", 1.41, "Tabla A.3, ID 32"),
    Material("Cu alloy", "Aleación de cobre", 1.28, "Tabla A.3, ID 33"),
    Material("SS", "Acero inoxidable", 2.67, "Tabla A.3, ID 34"),
    Material("Ni", "Aleación de níquel", 4.74, "Tabla A.3, ID 35"),
    Material("Ti", "Titanio", 10.66, "Tabla A.3, ID 36"),
)

FM_PUMP_CENTRIFUGAL = (
    Material("CI", "Hierro fundido", 1.00, "Tabla A.3, ID 37"),
    Material("CS", "Acero al carbón", 1.55, "Tabla A.3, ID 38"),
    Material("SS", "Acero inoxidable", 2.28, "Tabla A.3, ID 39"),
    Material("Ni", "Aleación de níquel", 4.36, "Tabla A.3, ID 40"),
)


def _fbm3(ids: tuple[int, int, int], values: tuple[float, float, float]):
    """F_BM para CS, SS y aleación de Ni (Figura A.19)."""
    labels = (("CS", "Acero al carbón"), ("SS", "Acero inoxidable"),
              ("Ni", "Aleación de níquel"))
    return tuple(
        Material(code, label, v, f"Tabla A.6, ID {i}")
        for (code, label), v, i in zip(labels, values, ids)
    )


def _fixed(value: float, ref: str, label: str = "Único (sin opción de material)"):
    return (Material("—", label, value, ref),)


# ---------------------------------------------------------------------------
# Correlaciones de presión, Tabla A.2
# ---------------------------------------------------------------------------

_ST_BOTH = PressureBand(140, 0.03881, -0.11272, 0.08183)
_ST_TUBE = PressureBand(140, -0.00164, -0.00627, 0.0123)
P_SHELL_TUBE = (
    PressureOption("both", "Ambos lados (coraza y tubos)", (PressureBand(5), _ST_BOTH)),
    PressureOption("tube", "Solo tubos", (PressureBand(5), _ST_TUBE)),
)
P_DOUBLE_PIPE = (
    PressureOption("all", "Presión de diseño", (
        PressureBand(40),
        PressureBand(100, 0.6072, -0.9120, 0.3327),
        PressureBand(300, 13.1467, -12.6574, 3.0705),
    )),
)
P_SPIRAL_TUBE = (
    PressureOption("both", "Ambos lados (coraza y tubos)", (
        PressureBand(150), PressureBand(400, -0.4045, 0.1859, 0.0))),
    PressureOption("tube", "Solo tubos", (
        PressureBand(150), PressureBand(400, -0.2115, 0.09717, 0.0))),
)
P_AIR_COOLER = (
    PressureOption("all", "Presión de diseño", (
        PressureBand(10), PressureBand(100, -0.1250, 0.15361, -0.02861))),
)
P_TEFLON = (PressureOption("all", "Presión de diseño", (PressureBand(15),)),)
P_PLATE = (PressureOption("all", "Presión de diseño", (PressureBand(19),)),)
P_PUMP_CENTRIFUGAL = (
    PressureOption("all", "Presión de descarga", (
        PressureBand(10), PressureBand(100, -0.3935, 0.3957, -0.00226))),
)
P_PUMP_OTHER = (
    PressureOption("all", "Presión de descarga", (
        PressureBand(10), PressureBand(100, -0.245382, 0.259016, -0.01363))),
)
P_TANK = (PressureOption("all", "Presión de operación", (PressureBand(0.07),)),)


def _furnace(C1, C2, C3):
    return (PressureOption("all", "Presión en tubos", (
        PressureBand(10), PressureBand(200, C1, C2, C3))),)


# ---------------------------------------------------------------------------
# Catálogo de equipos
# ---------------------------------------------------------------------------

HX = "Intercambiadores de calor"
VESSELS = "Recipientes de proceso"
TOWERS = "Torres"
INTERNALS = "Internos de torre"
PUMPS = "Bombas"
COMPRESSORS = "Compresores y sopladores"
DRIVES = "Accionamientos"
TURBINES = "Turbinas de recuperación"
FURNACES = "Hornos y calentadores"
REACTORS = "Reactores"
TANKS = "Tanques de almacenamiento"

AREA, VOLUME = ("Área", "m²"), ("Volumen", "m³")
SHAFT, FLUID, DUTY = ("Potencia de flecha", "kW"), ("Potencia de fluido", "kW"), ("Carga térmica", "kW")

_B_ST = dict(B1=1.63, B2=1.66)
_B_DP = dict(B1=1.74, B2=1.55)
_B_PLATE = dict(B1=0.96, B2=1.21)
_B_PUMP = dict(B1=1.89, B2=1.35)


def _eq(key, category, name, name_en, K, attr, a_range, method, materials, **kw):
    return Equipment(
        key=key, category=category, name=name, name_en=name_en,
        K1=K[0], K2=K[1], K3=K[2], attribute=attr[0], unit=attr[1],
        a_min=a_range[0], a_max=a_range[1], method=method, materials=materials,
        **kw,
    )


_REACTOR_NOTE = "F_BM = 4.0 es una estimación del libro (Tabla A.7, marcada con *)."
_TANK_NOTE = (
    "El Apéndice A no tabula F_BM para tanques API. COSTIQ usa 1.0 "
    "(solo costo de compra) como supuesto; ajústalo si tienes un dato mejor."
)

EQUIPMENT_LIST: tuple[Equipment, ...] = (
    # --- Intercambiadores de calor -------------------------------------
    _eq("hx_floating_head", HX, "Cabezal flotante", "Floating head",
        (4.8306, -0.8509, 0.3187), AREA, (10, 1000), "B1B2", FM_SHELL_TUBE,
        pressure=P_SHELL_TUBE, **_B_ST),
    _eq("hx_fixed_tube", HX, "Placa de tubos fija", "Fixed tube sheet",
        (4.3247, -0.3030, 0.1634), AREA, (10, 1000), "B1B2", FM_SHELL_TUBE,
        pressure=P_SHELL_TUBE, **_B_ST),
    _eq("hx_u_tube", HX, "Tubos en U", "U-tube",
        (4.1884, -0.2503, 0.1974), AREA, (10, 1000), "B1B2", FM_SHELL_TUBE,
        pressure=P_SHELL_TUBE, **_B_ST),
    _eq("hx_kettle", HX, "Hervidor tipo kettle", "Kettle reboiler",
        (4.4646, -0.5277, 0.3955), AREA, (10, 100), "B1B2", FM_SHELL_TUBE,
        pressure=P_SHELL_TUBE, **_B_ST),
    _eq("hx_bayonet", HX, "Bayoneta", "Bayonet",
        (4.2768, -0.0495, 0.1431), AREA, (10, 1000), "B1B2", FM_SHELL_TUBE,
        pressure=P_SHELL_TUBE, **_B_ST),
    _eq("hx_double_pipe", HX, "Doble tubo", "Double pipe",
        (3.3444, 0.2745, -0.0472), AREA, (1, 10), "B1B2", FM_SHELL_TUBE,
        pressure=P_DOUBLE_PIPE, **_B_DP),
    _eq("hx_multiple_pipe", HX, "Tubos múltiples", "Multiple pipe",
        (2.7652, 0.7282, 0.0783), AREA, (10, 100), "B1B2", FM_SHELL_TUBE,
        pressure=P_DOUBLE_PIPE, **_B_DP),
    _eq("hx_scraped_wall", HX, "Pared raspada", "Scraped wall",
        (3.7803, 0.8569, 0.0349), AREA, (2, 20), "B1B2", FM_SHELL_TUBE,
        pressure=P_DOUBLE_PIPE, **_B_DP),
    _eq("hx_spiral_tube", HX, "Tubo en espiral", "Spiral tube",
        (3.9912, 0.0668, 0.2430), AREA, (1, 100), "B1B2", FM_SHELL_TUBE,
        pressure=P_SPIRAL_TUBE, **_B_DP),
    _eq("hx_teflon", HX, "Tubos de teflón", "Teflon tube",
        (3.8062, 0.8924, -0.1671), AREA, (1, 10), "B1B2", FM_TEFLON,
        pressure=P_TEFLON, **_B_ST),
    _eq("hx_air_cooler", HX, "Enfriador de aire", "Air cooler",
        (4.0336, 0.2341, 0.0497), AREA, (10, 10000), "B1B2", FM_AIR_COOLER,
        pressure=P_AIR_COOLER, **_B_PLATE),
    _eq("hx_flat_plate", HX, "Placas planas", "Flat plate",
        (4.6656, -0.1557, 0.1547), AREA, (10, 1000), "B1B2", FM_PLATE,
        pressure=P_PLATE, **_B_PLATE),
    _eq("hx_spiral_plate", HX, "Placas en espiral", "Spiral plate",
        (4.6561, -0.2947, 0.2207), AREA, (1, 100), "B1B2", FM_PLATE,
        pressure=P_PLATE, **_B_PLATE),

    # --- Recipientes y torres -------------------------------------------
    _eq("vessel_horizontal", VESSELS, "Recipiente horizontal", "Horizontal vessel",
        (3.5565, 0.3776, 0.0905), VOLUME, (0.1, 628), "vessel", FM_VESSEL,
        B1=1.49, B2=1.52, geometry="horizontal"),
    _eq("vessel_vertical", VESSELS, "Recipiente vertical", "Vertical vessel",
        (3.4974, 0.4485, 0.1074), VOLUME, (0.3, 520), "vessel", FM_VESSEL,
        B1=2.25, B2=1.82, geometry="vertical"),
    _eq("tower", TOWERS, "Torre de platos o empaque", "Tray and packed tower",
        (3.4974, 0.4485, 0.1074), VOLUME, (0.3, 520), "vessel", FM_VESSEL,
        B1=2.25, B2=1.82, geometry="vertical",
        note="Solo la coraza. Platos y empaque se costean como internos."),

    # --- Internos de torre ----------------------------------------------
    _eq("tray_sieve", INTERNALS, "Platos perforados", "Sieve trays",
        (2.9949, 0.4465, 0.3961), AREA, (0.07, 12.30), "tray", (
            Material("CS", "Acero al carbón", 1.00, "Tabla A.6, ID 60"),
            Material("SS", "Acero inoxidable", 1.83, "Tabla A.6, ID 61"),
            Material("Ni", "Aleación de níquel", 5.58, "Tabla A.6, ID 62"),
        )),
    _eq("tray_valve", INTERNALS, "Platos de válvula", "Valve trays",
        (3.3322, 0.4838, 0.3434), AREA, (0.70, 10.50), "tray", (
            Material("CS", "Acero al carbón", 1.00, "Tabla A.6, ID 60"),
            Material("SS", "Acero inoxidable", 1.83, "Tabla A.6, ID 61"),
            Material("Ni", "Aleación de níquel", 5.58, "Tabla A.6, ID 62"),
        )),
    _eq("demister", INTERNALS, "Eliminador de niebla", "Demister pad",
        (3.2353, 0.4838, 0.3434), AREA, (0.70, 10.50), "tray", (
            Material("SS", "Acero inoxidable", 1.00, "Tabla A.6, ID 63"),
            Material("Fluorocarbon", "Fluorocarbono", 1.83, "Tabla A.6, ID 64"),
            Material("Ni", "Aleación de níquel", 5.58, "Tabla A.6, ID 65"),
        )),
    _eq("packing", INTERNALS, "Empaque aleatorio", "Loose packing",
        (2.4493, 0.9744, 0.0055), VOLUME, (0.03, 628), "FBM", (
            Material("PE", "Polietileno", 1.00, "Tabla A.6, ID 67"),
            Material("Ceramic", "Cerámica", 4.14, "Tabla A.6, ID 68"),
            Material("304SS", "Metal (304SS)", 7.09, "Tabla A.6, ID 66"),
        )),

    # --- Bombas ------------------------------------------------------------
    _eq("pump_centrifugal", PUMPS, "Centrífuga", "Centrifugal pump",
        (3.3892, 0.0536, 0.1538), SHAFT, (1, 300), "B1B2", FM_PUMP_CENTRIFUGAL,
        pressure=P_PUMP_CENTRIFUGAL, pressure_label="Presión de descarga", **_B_PUMP),
    _eq("pump_pd", PUMPS, "Desplazamiento positivo", "Positive displacement pump",
        (3.4771, 0.1350, 0.1438), SHAFT, (1, 100), "B1B2", FM_PUMP_PD,
        pressure=P_PUMP_OTHER, pressure_label="Presión de descarga", **_B_PUMP),
    _eq("pump_reciprocating", PUMPS, "Reciprocante", "Reciprocating pump",
        (3.8696, 0.3161, 0.1220), SHAFT, (0.1, 200), "B1B2", FM_PUMP_RECIPROCATING,
        pressure=P_PUMP_OTHER, pressure_label="Presión de descarga", **_B_PUMP),

    # --- Compresores (sin accionamiento) -----------------------------------
    _eq("comp_centrifugal", COMPRESSORS, "Centrífugo", "Centrifugal compressor",
        (2.2897, 1.3604, -0.1027), FLUID, (450, 3000), "FBM",
        _fbm3((1, 2, 3), (2.73, 5.75, 11.45)),
        note="Costo sin accionamiento; agrega el motor o turbina por separado."),
    _eq("comp_axial", COMPRESSORS, "Axial", "Axial compressor",
        (2.2897, 1.3604, -0.1027), FLUID, (450, 3000), "FBM",
        _fbm3((4, 5, 6), (3.83, 8.04, 15.93)),
        note="Costo sin accionamiento; agrega el motor o turbina por separado."),
    _eq("comp_reciprocating", COMPRESSORS, "Reciprocante", "Reciprocating compressor",
        (2.2897, 1.3604, -0.1027), FLUID, (450, 3000), "FBM",
        _fbm3((10, 11, 12), (3.37, 7.00, 13.89)),
        note="Costo sin accionamiento; agrega el motor o turbina por separado."),
    _eq("comp_rotary", COMPRESSORS, "Rotatorio", "Rotary compressor",
        (5.0355, -1.8002, 0.8253), FLUID, (18, 950), "FBM",
        _fbm3((7, 8, 9), (2.41, 5.04, 9.85)),
        note="Costo sin accionamiento; agrega el motor o turbina por separado."),

    # --- Accionamientos ------------------------------------------------------
    _eq("drive_electric_xp", DRIVES, "Motor eléctrico a prueba de explosión",
        "Electric drive, explosion-proof", (2.4604, 1.4191, -0.1798), SHAFT,
        (75, 2600), "FBM", _fixed(1.50, "Tabla A.6, ID 13")),
    _eq("drive_electric_tefc", DRIVES, "Motor eléctrico totalmente cerrado",
        "Electric drive, totally enclosed", (1.9560, 1.7142, -0.2282), SHAFT,
        (75, 2600), "FBM", _fixed(1.50, "Tabla A.6, ID 14")),
    _eq("drive_electric_odp", DRIVES, "Motor eléctrico abierto a prueba de goteo",
        "Electric drive, open/drip-proof", (2.9508, 1.0688, -0.1315), SHAFT,
        (75, 2600), "FBM", _fixed(1.50, "Tabla A.6, ID 15")),
    _eq("drive_gas_turbine", DRIVES, "Turbina de gas", "Gas turbine drive",
        (-21.7702, 13.2175, -1.5279), SHAFT, (7500, 23000), "FBM",
        _fixed(3.50, "Tabla A.6, ID 16")),
    _eq("drive_steam_turbine", DRIVES, "Turbina de vapor", "Steam turbine drive",
        (2.6259, 1.4398, -0.1776), SHAFT, (70, 7500), "FBM",
        _fixed(3.50, "Tabla A.6, ID 17")),
    _eq("drive_ic_engine", DRIVES, "Motor de combustión interna",
        "Internal combustion engine", (2.7635, 0.8574, -0.0098), SHAFT,
        (10, 10000), "FBM", _fixed(2.00, "Tabla A.6, ID 18")),

    # --- Turbinas de recuperación de potencia -------------------------------
    _eq("turbine_axial", TURBINES, "Turbina axial de gas", "Axial gas turbine",
        (2.7051, 1.4398, -0.1776), FLUID, (100, 4000), "FBM",
        _fbm3((57, 58, 59), (3.50, 6.12, 11.66))),
    _eq("turbine_radial", TURBINES, "Expansor radial de gas o líquido",
        "Radial gas/liquid expander", (2.2476, 1.4965, -0.1618), FLUID,
        (100, 1500), "FBM", _fbm3((57, 58, 59), (3.50, 6.12, 11.66))),

    # --- Hornos y calentadores a fuego directo ------------------------------
    *(
        _eq(key, FURNACES, name, name_en, K, DUTY, rng, "FBM_FP", (
            Material("CS", "Tubos de acero al carbón", 2.13, "Tabla A.6, ID 53"),
            Material("Alloy", "Tubos de acero aleado", 2.50, "Tabla A.6, ID 54"),
            Material("SS", "Tubos de acero inoxidable", 2.81, "Tabla A.6, ID 55"),
        ), pressure=_furnace(*C), pressure_label="Presión en tubos")
        for key, name, name_en, K, rng, C in (
            ("furnace_reformer", "Horno de reformado", "Reformer furnace",
             (3.0680, 0.6597, 0.0194), (3000, 100000), (0.1405, -0.2698, 0.1293)),
            ("furnace_pyrolysis", "Horno de pirólisis", "Pyrolysis furnace",
             (2.3859, 0.9721, -0.0206), (3000, 100000), (0.1017, -0.1957, 0.09403)),
            ("furnace_nonreactive", "Calentador a fuego directo", "Nonreactive fired heater",
             (7.3488, -1.1666, 0.2028), (1000, 100000), (0.1347, -0.2368, 0.1021)),
        )
    ),

    # --- Reactores -------------------------------------------------------------
    *(
        _eq(key, REACTORS, name, name_en, K, VOLUME, rng, "FBM",
            _fixed(4.0, "Tabla A.7 (estimación)"), note=_REACTOR_NOTE)
        for key, name, name_en, K, rng in (
            ("reactor_autoclave", "Autoclave", "Autoclave",
             (4.5587, 0.2986, 0.0020), (1, 15)),
            ("reactor_fermenter", "Fermentador", "Fermenter",
             (4.1052, 0.5320, -0.0005), (0.1, 35)),
            ("reactor_inoculum", "Tanque de inóculo", "Inoculum tank",
             (3.7957, 0.4593, 0.0160), (0.07, 1)),
            ("reactor_jacketed_agitated", "Enchaquetado con agitación",
             "Jacketed agitated", (4.1052, 0.5320, -0.0005), (0.1, 35)),
            ("reactor_jacketed_nonagitated", "Enchaquetado sin agitación",
             "Jacketed nonagitated", (3.3496, 0.7235, 0.0025), (5, 45)),
            ("reactor_mixer_settler", "Mezclador-sedimentador", "Mixer/settler",
             (4.7116, 0.4479, 0.0004), (0.04, 60)),
        )
    ),

    # --- Tanques -----------------------------------------------------------------
    _eq("tank_fixed_roof", TANKS, "API de techo fijo", "API fixed roof",
        (4.8509, -0.3973, 0.1445), VOLUME, (90, 30000), "FBM",
        _fixed(1.0, "Supuesto de COSTIQ (no tabulado)"), pressure=P_TANK,
        note=_TANK_NOTE),
    _eq("tank_floating_roof", TANKS, "API de techo flotante", "API floating roof",
        (5.9567, -0.7585, 0.1749), VOLUME, (1000, 40000), "FBM",
        _fixed(1.0, "Supuesto de COSTIQ (no tabulado)"), pressure=P_TANK,
        note=_TANK_NOTE),
)

EQUIPMENT: dict[str, Equipment] = {e.key: e for e in EQUIPMENT_LIST}

CATEGORIES: dict[str, list[Equipment]] = {}
for _e in EQUIPMENT_LIST:
    CATEGORIES.setdefault(_e.category, []).append(_e)

TAG_PREFIX: dict[str, str] = {
    HX: "E", VESSELS: "V", TOWERS: "T", INTERNALS: "T", PUMPS: "P",
    COMPRESSORS: "C", DRIVES: "D", TURBINES: "X", FURNACES: "H",
    REACTORS: "R", TANKS: "TK",
}

METHOD_EQUATION: dict[str, str] = {
    "B1B2": r"C_{BM} = C_p^\circ \left(B_1 + B_2\,F_M\,F_P\right)",
    "vessel": r"C_{BM} = C_p^\circ \left(B_1 + B_2\,F_M\,F_P\right)",
    "FBM": r"C_{BM} = C_p^\circ\,F_{BM}",
    "FBM_FP": r"C_{BM} = C_p^\circ\,F_{BM}\,F_P",
    "tray": r"C_{BM} = C_p^\circ\,N\,F_{BM}\,F_q",
}

METHOD_SOURCE: dict[str, str] = {
    "B1B2": "Ec. A.4, Tablas A.2–A.4, Fig. A.18",
    "vessel": "Ecs. A.2 y A.4, Tablas A.3–A.4, Fig. A.18",
    "FBM": "Tablas A.5–A.7, Fig. A.19",
    "FBM_FP": "Tablas A.2, A.5 y A.6, Fig. A.19",
    "tray": "Tablas A.5 y A.6, Fig. A.19",
}
