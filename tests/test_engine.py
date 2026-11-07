"""Pruebas de consistencia del motor y de integridad del catálogo."""

import math

import pytest

from costiq import (
    CEPCI, CEPCI_BASE, EQUIPMENT, EQUIPMENT_LIST, CostError, cost,
    plant_summary, pressure_factor, tray_quantity_factor,
    vessel_pressure_factor,
)


def _sample_kwargs(eq, capacity):
    kw = dict(equipment=eq, capacity=capacity)
    if eq.method == "vessel":
        kw["diameter"] = 1.0
    if eq.method == "tray":
        kw["trays"] = 10
    return kw


# --- Integridad del catálogo ---------------------------------------------

def test_catalog_size_and_unique_keys():
    assert len(EQUIPMENT_LIST) == len(EQUIPMENT) == 46


@pytest.mark.parametrize("eq", EQUIPMENT_LIST, ids=lambda e: e.key)
def test_equipment_definition_is_complete(eq):
    assert eq.a_min < eq.a_max
    assert eq.materials
    assert eq.base_material.factor >= 1.0 or eq.method in ("FBM", "FBM_FP")
    if eq.method in ("B1B2", "vessel"):
        assert eq.B1 is not None and eq.B2 is not None
        assert eq.base_material.factor == 1.0
    for opt in eq.pressure:
        limits = [b.p_max for b in opt.bands]
        assert limits == sorted(limits)


@pytest.mark.parametrize("eq", EQUIPMENT_LIST, ids=lambda e: e.key)
def test_every_material_costs_at_least_the_base(eq):
    for a in (eq.a_min, math.sqrt(eq.a_min * eq.a_max), eq.a_max):
        for m in eq.materials:
            r = cost(material=m.code, **_sample_kwargs(eq, a))
            assert r.Cp0 > 0 and math.isfinite(r.CBM)
            assert r.CBM >= r.CBM0 * (1 - 1e-12)
            assert r.CBM0 >= r.Cp_base * (1 - 1e-12)
            assert not [n for n in r.notices if n.level == "warning"]


def test_cepci_table_is_contiguous():
    years = sorted(CEPCI)
    assert years == list(range(years[0], years[-1] + 1))
    assert CEPCI_BASE == 397.0


# --- Factores de material y de módulo corregidos en v2 -------------------

@pytest.mark.parametrize("key,material,value", [
    ("hx_floating_head", "CS/Ti", 4.63),
    ("hx_floating_head", "Ti/Ti", 11.38),
    ("hx_air_cooler", "Al", 1.42),
    ("vessel_vertical", "Ni", 7.07),
    ("vessel_vertical", "Ti", 9.40),
    ("pump_centrifugal", "CS", 1.55),
    ("pump_pd", "SS", 2.67),
    ("pump_reciprocating", "Ti", 6.44),
    ("comp_centrifugal", "CS", 2.73),
    ("comp_axial", "CS", 3.83),
    ("tray_sieve", "Ni", 5.58),
    ("drive_steam_turbine", "—", 3.50),
])
def test_corrected_factors(key, material, value):
    assert EQUIPMENT[key].material(material).factor == value


# --- Factor de presión -----------------------------------------------------

def test_pressure_factor_flat_band_and_vacuum():
    eq = EQUIPMENT["hx_floating_head"]
    assert pressure_factor(eq, 3, "both")[0] == 1.0
    assert pressure_factor(eq, -0.3, "both")[0] == 1.0


def test_pressure_factor_continuous_at_band_edge():
    eq = EQUIPMENT["hx_floating_head"]
    assert pressure_factor(eq, 5.0, "both")[0] == pytest.approx(1.0, abs=1e-3)


@pytest.mark.parametrize("eq", [e for e in EQUIPMENT_LIST if e.pressure],
                         ids=lambda e: e.key)
def test_pressure_factor_never_drops_beyond_range(eq):
    """Fuera del rango tabulado, F_P nunca baja (v1 caía a 1.0)."""
    for opt in eq.pressure:
        ps = [opt.p_max * (1 + i / 50) for i in range(51)]
        values = [pressure_factor(eq, p, opt.key)[0] for p in ps]
        assert all(b >= a - 1e-9 for a, b in zip(values, values[1:]))


def test_double_pipe_dip_is_the_books_correlation():
    """La correlación de la Tabla A.2 para doble tubo baja ~2.5 % entre 100 y
    130 barg. Es un rasgo del ajuste del libro; COSTIQ lo conserva."""
    eq = EQUIPMENT["hx_double_pipe"]
    fp_100 = pressure_factor(eq, 100)[0]
    fp_115 = pressure_factor(eq, 115)[0]
    assert fp_100 == pytest.approx(1.300, rel=1e-3)
    assert 0.97 < fp_115 / fp_100 < 1.0


def test_pressure_above_range_is_flagged_and_extrapolated():
    eq = EQUIPMENT["hx_floating_head"]
    fp_limit, notes_limit = pressure_factor(eq, 140, "both")
    fp_high, notes_high = pressure_factor(eq, 200, "both")
    assert not notes_limit
    assert fp_high > fp_limit > 1.0
    assert notes_high and notes_high[0].level == "warning"


def test_tank_above_atmospheric_is_flagged():
    r = cost("tank_fixed_roof", 1000, pressure=1.0)
    assert any("atmosféricos" in n.text for n in r.notices)


# --- Recipientes -------------------------------------------------------------

def test_vessel_vacuum_factor():
    fp, t, notes = vessel_pressure_factor(-0.8, 2.0)
    assert fp == 1.25 and t is None


def test_vessel_low_pressure_floors_at_one():
    assert vessel_pressure_factor(0.0, 0.5)[0] == 1.0


def test_vessel_thick_wall_warning():
    fp, t, notes = vessel_pressure_factor(450, 1.0)
    assert t > 0.25
    assert any(n.level == "warning" for n in notes)


def test_vessel_requires_geometry():
    with pytest.raises(CostError):
        cost("vessel_vertical", 10)
    with pytest.raises(CostError):
        cost("vessel_vertical", diameter=1.0)


def test_vessel_volume_from_geometry():
    r = cost("vessel_horizontal", diameter=2.0, length=5.0)
    assert r.capacity == pytest.approx(math.pi * 4 * 5 / 4)


# --- Platos -----------------------------------------------------------------

def test_tray_quantity_factor():
    assert tray_quantity_factor(1) == pytest.approx(3.0, rel=1e-3)
    assert tray_quantity_factor(20) == 1.0
    # La Tabla A.5 tiene un salto de ~4 % entre N = 19 y N = 20.
    assert tray_quantity_factor(19) == pytest.approx(1.043, abs=1e-3)
    with pytest.raises(CostError):
        tray_quantity_factor(0)


# --- Capacidad y unidades ------------------------------------------------------

def test_capacity_out_of_range_is_flagged_not_blocked():
    r = cost("pump_centrifugal", 500)
    assert r.Cp0 > 0
    assert any("unidades en paralelo" in n.text for n in r.notices)


def test_units_scale_linearly():
    one = cost("pump_centrifugal", 50, "SS", pressure=20)
    two = cost("pump_centrifugal", 50, "SS", pressure=20, units=2)
    assert two.CBM == pytest.approx(2 * one.CBM)
    assert two.CBM0 == pytest.approx(2 * one.CBM0)


def test_fbm_override():
    r = cost("tank_fixed_roof", 1000, fbm_override=1.4)
    assert r.FBM == 1.4 and r.CBM == pytest.approx(1.4 * r.Cp0)


# --- Cascada y costo de planta --------------------------------------------------

@pytest.mark.parametrize("key", ["hx_u_tube", "pump_pd", "tower", "tray_valve",
                                 "comp_axial", "furnace_reformer"])
def test_breakdown_sums_to_updated_cost(key):
    eq = EQUIPMENT[key]
    mat = max(eq.materials, key=lambda m: m.factor).code
    kw = _sample_kwargs(eq, math.sqrt(eq.a_min * eq.a_max))
    r = cost(material=mat, pressure=30, **kw)
    steps = r.breakdown(800.8)
    assert sum(v for _, v in steps) == pytest.approx(r.at(800.8))
    assert all(v >= 0 for _, v in steps)


def test_plant_summary_definitions():
    items = [cost("hx_fixed_tube", 80, "SS/SS", pressure=20, pressure_option="tube"),
             cost("comp_centrifugal", 1200, "SS")]
    s = plant_summary(items, 600.0)
    r = 600.0 / CEPCI_BASE
    assert s.CBM == pytest.approx(sum(i.CBM for i in items) * r)
    assert s.CTM == pytest.approx(1.18 * s.CBM)
    assert s.CGR == pytest.approx(s.CTM + 0.5 * s.CBM0)
    assert s.CBM0 < s.CBM


def test_unknown_material_raises():
    with pytest.raises(KeyError):
        cost("hx_floating_head", 100, "Unobtainium")
