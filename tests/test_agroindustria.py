"""Equipos agregados en la v2.1 (Tablas A.1, A.2, A.5–A.7) y cotización propia.

Los valores esperados se calculan a mano a partir de las constantes del libro,
de forma independiente del motor.
"""

import math

import pytest

from costiq import (
    CATEGORIES, EQUIPMENT, CostError, cost, plant_summary, pressure_factor,
    quoted_cost, superheat_factor,
)


def lp(c1, c2, c3, x):
    lx = math.log10(x)
    return 10 ** (c1 + c2 * lx + c3 * lx * lx)


# --- Factores de presión nuevos (Tabla A.2) --------------------------------

def test_evaporator_pressure_factor():
    eq = EQUIPMENT["evap_falling_film"]
    assert pressure_factor(eq, 5)[0] == 1.0
    # El primer tramo termina en 10 barg aunque el libro imprime "P < 0".
    assert pressure_factor(eq, 10)[0] == pytest.approx(1.0, abs=1e-3)
    assert pressure_factor(eq, 50)[0] == pytest.approx(lp(0.1578, -0.2992, 0.1413, 50))
    assert pressure_factor(eq, 50)[0] == pytest.approx(1.141, rel=1e-3)


@pytest.mark.parametrize("key,limit", [("fan_radial", 16), ("fan_axial_vane", 4)])
def test_fan_pressure_in_kpa(key, limit):
    eq = EQUIPMENT[key]
    assert eq.pressure_unit == "kPa"
    assert pressure_factor(eq, 0.5)[0] == 1.0
    assert pressure_factor(eq, 3)[0] == pytest.approx(lp(0.0, 0.20899, -0.0328, 3))
    fp, notes = pressure_factor(eq, limit + 2)
    assert notes and "kPa" in notes[0].text


def test_thermal_fluid_heater_and_boiler_pressure():
    assert pressure_factor(EQUIPMENT["heater_hot_water"], 50)[0] == pytest.approx(
        lp(-0.01633, 0.056875, -0.00876, 50))
    boiler = EQUIPMENT["steam_boiler"]
    assert pressure_factor(boiler, 20)[0] == pytest.approx(1.0, abs=1e-3)
    assert pressure_factor(boiler, 30)[0] == pytest.approx(
        lp(2.594072, -4.23476, 1.722404, 30))


def test_vaporizer_pressure_factor():
    eq = EQUIPMENT["vaporizer_jacketed"]
    assert pressure_factor(eq, 100)[0] == pytest.approx(lp(-0.16742, 0.13428, 0.15058, 100))


# --- Ecuaciones de la Tabla A.5 -------------------------------------------------

def test_superheat_factor():
    assert superheat_factor(0) == 1.0
    assert superheat_factor(100) == pytest.approx(1 + 0.184 - 0.0335)
    with pytest.raises(CostError):
        superheat_factor(-5)


def test_steam_boiler_bare_module():
    r = cost("steam_boiler", 5000, pressure=30, superheat=100)
    Cp0 = lp(6.9617, -1.4800, 0.3161, 5000)
    FP = lp(2.594072, -4.23476, 1.722404, 30)
    assert r.CBM == pytest.approx(Cp0 * 2.16 * FP * superheat_factor(100))
    assert r.CBM0 == pytest.approx(Cp0 * 2.16)
    assert r.FT == pytest.approx(superheat_factor(100))
    edited = cost("steam_boiler", 5000, fbm_override=2.5)
    assert edited.FBM == 2.5


def test_evaporator_material_and_pressure():
    r = cost("evap_forced", 100, "SS", pressure=50)
    Cp0 = lp(5.0238, 0.3475, 0.0703, 100)
    assert r.FBM == 5.08
    assert r.CBM == pytest.approx(Cp0 * 5.08 * lp(0.1578, -0.2992, 0.1413, 50))
    assert r.CBM0 == pytest.approx(Cp0 * 2.90)


def test_fan_bare_module():
    r = cost("fan_backward", 20, "SS", pressure=8)
    Cp0 = lp(3.3471, -0.0734, 0.3090, 20)
    assert r.CBM == pytest.approx(Cp0 * 5.75 * lp(0.0, 0.20899, -0.0328, 8))


# --- Factores de la Tabla A.7 y de la Fig. A.19 ----------------------------------

@pytest.mark.parametrize("key,fbm,estimate", [
    ("conveyor_belt", 1.25, False), ("conveyor_screw", 1.10, False),
    ("conveyor_pneumatic", 1.25, True), ("screen_vibrating", 1.34, False),
    ("filter_plate_frame", 1.80, False), ("filter_leaf", 1.65, False),
    ("filter_cartridge", 1.65, True), ("centrifuge_solid_bowl", 1.27, False),
    ("centrifuge_separator", 1.57, False), ("dryer_drum", 1.60, False),
    ("dryer_tray", 1.25, False), ("crystallizer_batch", 1.60, False),
    ("mixer_propeller", 1.38, False), ("blender_kneader", 1.12, True),
    ("dust_baghouse", 2.86, True),
])
def test_table_a7_factors(key, fbm, estimate):
    eq = EQUIPMENT[key]
    assert eq.method == "FBM"
    assert eq.materials[0].factor == fbm
    assert ("estimación" in eq.materials[0].ref) is estimate


@pytest.mark.parametrize("key,material,fbm", [
    ("evap_long_tube", "CS", 2.90), ("evap_falling_film", "Ti", 11.25),
    ("vaporizer_jacketed", "SS", 4.80), ("vaporizer_coil", "Ti", 15.16),
    ("fan_radial", "Fiberglass", 4.97), ("heater_diphenyl", "—", 2.16),
])
def test_figure_a19_factors(key, material, fbm):
    assert EQUIPMENT[key].material(material).factor == fbm


def test_new_categories_present():
    for cat in ("Evaporadores", "Secadores", "Calentadores y calderas",
                "Vaporizadores y marmitas", "Mezcladores y agitadores",
                "Cristalizadores", "Transporte de sólidos", "Cribas", "Filtros",
                "Centrífugas", "Colectores de polvo", "Ventiladores"):
        assert CATEGORIES[cat]


# --- Cotización propia (Ec. 7.1) ----------------------------------------------------

def test_quote_reproduces_example_7_5():
    """Ejemplo 7.5: intercambiador de 100 m² a $10,000; n = 0.59; 180 m² → $14,100."""
    r = quoted_cost("Intercambiador", 180, "m²", 10_000, 100, ref_cepci=397, exponent=0.59)
    assert r.Cp0 == pytest.approx(14_100, rel=0.005)


def test_quote_six_tenths_doubling_example_7_3():
    """Ejemplo 7.3: duplicar la capacidad con n = 0.6 sube el costo 52 %."""
    one = quoted_cost("Molino", 10, "t/h", 50_000, 10, 397)
    two = quoted_cost("Molino", 20, "t/h", 50_000, 10, 397)
    assert two.Cp0 / one.Cp0 == pytest.approx(1.516, rel=1e-3)


def test_quote_cepci_fbm_units_and_plant():
    r = quoted_cost("Extrusor", 500, "kg/h", 120_000, 500, ref_cepci=800.8, fbm=2.0, units=2)
    assert r.Cp0 == pytest.approx(120_000 * 397 / 800.8)
    assert r.at(800.8) == pytest.approx(2 * 2.0 * 120_000)
    assert r.CBM0 == r.CBM
    s = plant_summary([r], 800.8)
    assert s.CGR == pytest.approx(1.18 * s.CBM + 0.5 * s.CBM)
    assert sum(v for _, v in r.breakdown(800.8)) == pytest.approx(r.at(800.8))


def test_quote_warnings_and_validation():
    far = quoted_cost("Membrana", 500, "m²", 10_000, 10, 397, exponent=1.2)
    texts = " ".join(n.text for n in far.notices if n.level == "warning")
    assert "orden de magnitud" in texts and "Tabla 7.3" in texts
    with pytest.raises(CostError):
        quoted_cost("X", 1, "u", 0, 1, 397)
    with pytest.raises(CostError):
        quoted_cost("X", 1, "u", 100, 1, 397, fbm=0.5)
