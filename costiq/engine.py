"""Motor de cálculo de COSTIQ (método de módulo de Turton et al., 2018).

Todas las funciones son puras: no dependen de Streamlit y se pueden usar
desde un script, un cuaderno o una prueba.

Ecuaciones implementadas:

- Ec. A.1   log10 Cp° = K1 + K2 log10 A + K3 (log10 A)^2
- Ec. A.2   F_P de recipientes (código ASME); ver `vessel_pressure_factor`
- Ec. A.3   log10 F_P = C1 + C2 log10 P + C3 (log10 P)^2
- Ec. A.4   C_BM = Cp° (B1 + B2 F_M F_P)
- Tabla A.5 C_BM = Cp° F_BM,  Cp° F_BM F_P,  Cp° N F_BM F_q
- Ec. 7.15  C_TM = (1 + f_cont + f_fee) Σ C_BM
- Ec. 7.16  C_GR = C_TM + f_aux Σ C°_BM
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .data import (
    CEPCI_BASE, EQUIPMENT, F_AUXILIARY, F_CONTINGENCY, F_FEE, VESSEL_CA_M,
    VESSEL_E, VESSEL_S_BAR, VESSEL_TMIN_M, VESSEL_VACUUM_FP, VESSEL_VACUUM_P,
    Equipment, Material, PressureOption,
)

VESSEL_GAUGE_OFFSET = 1.0
"""Se suma a la presión manométrica en la Ec. A.2.

La Ec. A.2 impresa en el Apéndice A de la 5.ª edición usa P. Los Ejemplos
7.13 y 7.14 del mismo libro, y la Ec. A.2 de la 4.ª edición, usan (P + 1).
COSTIQ adopta (P + 1) para reproducir los ejemplos resueltos. Con 0 se
obtiene la ecuación tal como está impresa.
"""


class CostError(ValueError):
    """Entrada fuera de lo que el método puede calcular."""


@dataclass(frozen=True)
class Notice:
    """Advertencia o nota asociada a un resultado."""

    level: str  # "warning" o "info"
    text: str


# ---------------------------------------------------------------------------
# Correlaciones elementales
# ---------------------------------------------------------------------------

def log_poly(c0: float, c1: float, c2: float, x: float) -> float:
    """10 ** (c0 + c1 log10 x + c2 (log10 x)^2)."""
    lx = math.log10(x)
    return 10.0 ** (c0 + c1 * lx + c2 * lx * lx)


def purchased_cost(eq: Equipment, capacity: float) -> tuple[float, list[Notice]]:
    """Costo de compra Cp° a CS y presión ambiente, USD con CEPCI = 397 (Ec. A.1)."""
    if capacity <= 0:
        raise CostError(f"La capacidad debe ser positiva ({eq.attribute}, {eq.unit}).")
    notes: list[Notice] = []
    rango = f"{eq.a_min:g}–{eq.a_max:g} {eq.unit}"
    if capacity < eq.a_min:
        notes.append(Notice(
            "warning",
            f"La capacidad ({capacity:,.4g} {eq.unit}) está por debajo del rango de la "
            f"correlación ({rango}). Cp° es una extrapolación.",
        ))
    elif capacity > eq.a_max:
        notes.append(Notice(
            "warning",
            f"La capacidad ({capacity:,.4g} {eq.unit}) supera el rango de la correlación "
            f"({rango}). Cp° es una extrapolación; Turton recomienda dividir la capacidad "
            "en varias unidades en paralelo.",
        ))
    return log_poly(eq.K1, eq.K2, eq.K3, capacity), notes


def _band_factor(option: PressureOption, P: float) -> tuple[float, bool]:
    """F_P de una opción de la Tabla A.2. Devuelve (F_P, extrapolado)."""
    if P <= 0:
        return 1.0, False
    for band in option.bands:
        if P <= band.p_max:
            if band.is_flat:
                return 1.0, False
            return max(1.0, log_poly(band.C1, band.C2, band.C3, P)), False
    # Fuera de rango: se extrapola con el último tramo, sin dejar que F_P baje
    # respecto del valor en el límite tabulado.
    last = option.bands[-1]
    if last.is_flat:
        return 1.0, True
    at_limit = log_poly(last.C1, last.C2, last.C3, last.p_max)
    return max(1.0, at_limit, log_poly(last.C1, last.C2, last.C3, P)), True


def pressure_factor(eq: Equipment, P: float, option: str | None = None
                    ) -> tuple[float, list[Notice]]:
    """F_P para equipos con correlación de la Tabla A.2 (Ec. A.3). P en barg."""
    opt = eq.pressure_option(option)
    if opt is None:
        return 1.0, []
    notes: list[Notice] = []
    fp, extrapolated = _band_factor(opt, P)
    if extrapolated:
        if all(b.is_flat for b in opt.bands):
            text = (f"La presión ({P:g} barg) supera el máximo tabulado para este equipo "
                    f"({opt.p_max:g} barg). El libro no da corrección por presión; "
                    "F_P = 1 no representa el costo real.")
            if eq.category.startswith("Tanques"):
                text = (f"Los tanques API son atmosféricos (P < {opt.p_max:g} barg). "
                        f"Para {P:g} barg usa un recipiente de proceso.")
        else:
            text = (f"La presión ({P:g} barg) supera el rango de la Tabla A.2 "
                    f"({opt.p_max:g} barg). F_P se extrapoló; el libro pide usarlo con "
                    "extrema precaución.")
        notes.append(Notice("warning", text))
    return fp, notes


def vessel_thickness(P: float, D: float) -> float:
    """Espesor de pared requerido (m) según la Ec. A.2, con corrosión incluida."""
    Pd = P + VESSEL_GAUGE_OFFSET
    denom = 2.0 * (VESSEL_S_BAR * VESSEL_E - 0.6 * Pd)
    if denom <= 0:
        raise CostError(f"La Ec. A.2 no tiene solución para P = {P:g} barg.")
    return max(Pd, 0.0) * D / denom + VESSEL_CA_M


def vessel_pressure_factor(P: float, D: float) -> tuple[float, float | None, list[Notice]]:
    """F_P de recipientes horizontales y verticales (Ec. A.2).

    Devuelve (F_P, espesor en m, notas). P en barg, D en m.
    """
    if D <= 0:
        raise CostError("El diámetro debe ser positivo.")
    if P < VESSEL_VACUUM_P:
        return VESSEL_VACUUM_FP, None, [Notice(
            "info", f"Vacío (P < {VESSEL_VACUUM_P:g} barg): el libro fija F_P = 1.25.")]
    t = vessel_thickness(P, D)
    fp = max(1.0, t / VESSEL_TMIN_M)
    notes: list[Notice] = []
    if t > 0.25 * D:
        notes.append(Notice(
            "warning",
            f"El espesor calculado ({t * 1000:,.0f} mm) supera D/4. La Ec. A.2 solo es "
            "válida para pared delgada (≈320 barg o menos para D de 0.3 a 4 m).",
        ))
    return fp, t, notes


def tray_quantity_factor(N: int) -> float:
    """Factor de cantidad F_q para platos (Tabla A.5)."""
    if N < 1:
        raise CostError("El número de platos debe ser al menos 1.")
    if N >= 20:
        return 1.0
    lx = math.log10(N)
    return 10.0 ** (0.4771 + 0.08516 * lx - 0.3473 * lx * lx)


def vessel_volume(D: float, L: float) -> float:
    """Volumen de un cilindro, πD²L/4 (m³)."""
    return math.pi * D * D * L / 4.0


def tray_area(D: float) -> float:
    """Área de plato igual a la sección transversal de la torre, πD²/4 (m²)."""
    return math.pi * D * D / 4.0


# ---------------------------------------------------------------------------
# Costo de módulo desnudo de un equipo
# ---------------------------------------------------------------------------

@dataclass
class CostResult:
    """Resultado del costeo de un equipo. Costos en USD con CEPCI = 397."""

    equipment: Equipment
    capacity: float
    units: int
    material: Material
    pressure: float
    pressure_option: str | None
    diameter: float | None
    length: float | None
    trays: int
    Cp0: float
    FM: float
    FP: float
    FBM: float
    Fq: float
    CBM_unit: float
    CBM0_unit: float
    Cp_base_unit: float
    thickness: float | None = None
    notices: list[Notice] = field(default_factory=list)

    @property
    def CBM(self) -> float:
        return self.units * self.CBM_unit

    @property
    def CBM0(self) -> float:
        return self.units * self.CBM0_unit

    @property
    def Cp_base(self) -> float:
        return self.units * self.Cp_base_unit

    def at(self, cepci: float) -> float:
        """C_BM total actualizado al CEPCI indicado."""
        return self.CBM * cepci / CEPCI_BASE

    def breakdown(self, cepci: float) -> list[tuple[str, float]]:
        """Cascada de costos (USD) que suma C_BM actualizado.

        1. Compra a condiciones base (CS, presión ambiente).
        2. Instalación a condiciones base (C°_BM − compra).
        3. Material y presión (C_BM − C°_BM).
        4. Actualización CEPCI (C_BM × (CEPCI/397 − 1)).
        """
        return [
            ("Compra base", self.Cp_base),
            ("Instalación", self.CBM0 - self.Cp_base),
            ("Material y presión", self.CBM - self.CBM0),
            ("Inflación (CEPCI)", self.CBM * (cepci / CEPCI_BASE - 1.0)),
        ]


def cost(
    equipment: Equipment | str,
    capacity: float | None = None,
    material: str | None = None,
    pressure: float = 0.0,
    pressure_option: str | None = None,
    diameter: float | None = None,
    length: float | None = None,
    trays: int = 1,
    units: int = 1,
    fbm_override: float | None = None,
) -> CostResult:
    """Costo de módulo desnudo de un equipo (Ec. A.4 o Tabla A.5).

    Parámetros:
        equipment: objeto `Equipment` o su clave en `EQUIPMENT`.
        capacity: atributo de tamaño por unidad (área, volumen, potencia...).
            Para recipientes puede omitirse si se dan `diameter` y `length`.
        material: código de material; por omisión, el material base.
        pressure: presión de operación o de diseño en barg.
        pressure_option: clave de `PressureOption` (p. ej., "both" o "tube").
        diameter, length: geometría de recipientes y torres (m).
        trays: número de platos (solo método "tray").
        units: número de unidades idénticas en paralelo.
        fbm_override: F_BM definido por el usuario (solo método "FBM").
    """
    eq = EQUIPMENT[equipment] if isinstance(equipment, str) else equipment
    if units < 1:
        raise CostError("El número de unidades debe ser al menos 1.")

    notes: list[Notice] = []
    if eq.method == "vessel":
        if diameter is None:
            raise CostError("Los recipientes requieren el diámetro.")
        if capacity is None:
            if length is None or length <= 0:
                raise CostError("Indica la longitud o la altura del recipiente.")
            capacity = vessel_volume(diameter, length)
    if capacity is None:
        raise CostError("Falta la capacidad del equipo.")

    mat = eq.material(material) if material else eq.base_material
    Cp0, cap_notes = purchased_cost(eq, capacity)
    notes += cap_notes

    FM = FP = Fq = 1.0
    thickness = None
    method = eq.method

    if method in ("B1B2", "vessel"):
        FM = mat.factor
        if method == "vessel":
            FP, thickness, p_notes = vessel_pressure_factor(pressure, diameter)
        else:
            FP, p_notes = pressure_factor(eq, pressure, pressure_option)
        notes += p_notes
        FBM = eq.B1 + eq.B2 * FM * FP
        FBM0 = eq.B1 + eq.B2
        CBM_unit = Cp0 * FBM
        CBM0_unit = Cp0 * FBM0
        Cp_base_unit = Cp0
    elif method == "FBM":
        FBM = fbm_override if fbm_override is not None else mat.factor
        FBM0 = fbm_override if fbm_override is not None else eq.base_material.factor
        _, p_notes = pressure_factor(eq, pressure, pressure_option)
        notes += p_notes
        CBM_unit = Cp0 * FBM
        CBM0_unit = Cp0 * FBM0
        Cp_base_unit = Cp0
    elif method == "FBM_FP":
        FBM = mat.factor
        FP, p_notes = pressure_factor(eq, pressure, pressure_option)
        notes += p_notes
        CBM_unit = Cp0 * FBM * FP
        CBM0_unit = Cp0 * eq.base_material.factor
        Cp_base_unit = Cp0
    elif method == "tray":
        if trays < 1:
            raise CostError("El número de platos debe ser al menos 1.")
        FBM = mat.factor
        Fq = tray_quantity_factor(trays)
        CBM_unit = Cp0 * trays * FBM * Fq
        CBM0_unit = Cp0 * trays * eq.base_material.factor * Fq
        Cp_base_unit = Cp0 * trays * Fq
    else:  # pragma: no cover - el catálogo solo define los métodos anteriores
        raise CostError(f"Método desconocido: {method}")

    if eq.note:
        notes.append(Notice("info", eq.note))

    return CostResult(
        equipment=eq, capacity=capacity, units=units, material=mat,
        pressure=pressure, pressure_option=pressure_option,
        diameter=diameter, length=length, trays=trays if method == "tray" else 1,
        Cp0=Cp0, FM=FM, FP=FP, FBM=FBM, Fq=Fq,
        CBM_unit=CBM_unit, CBM0_unit=CBM0_unit, Cp_base_unit=Cp_base_unit,
        thickness=thickness, notices=notes,
    )


# ---------------------------------------------------------------------------
# Costo de planta
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PlantSummary:
    """Costos de planta actualizados al CEPCI indicado (USD)."""

    cepci: float
    CBM: float
    CBM0: float
    contingency: float
    fee: float
    CTM: float
    auxiliary: float
    CGR: float
    f_contingency: float
    f_fee: float
    f_auxiliary: float


def plant_summary(
    results: list[CostResult],
    cepci: float,
    f_contingency: float = F_CONTINGENCY,
    f_fee: float = F_FEE,
    f_auxiliary: float = F_AUXILIARY,
) -> PlantSummary:
    """Costo de módulo total (Ec. 7.15) y grassroots (Ec. 7.16)."""
    r = cepci / CEPCI_BASE
    cbm = sum(x.CBM for x in results) * r
    cbm0 = sum(x.CBM0 for x in results) * r
    contingency = f_contingency * cbm
    fee = f_fee * cbm
    ctm = cbm + contingency + fee
    aux = f_auxiliary * cbm0
    return PlantSummary(
        cepci=cepci, CBM=cbm, CBM0=cbm0, contingency=contingency, fee=fee,
        CTM=ctm, auxiliary=aux, CGR=ctm + aux,
        f_contingency=f_contingency, f_fee=f_fee, f_auxiliary=f_auxiliary,
    )
