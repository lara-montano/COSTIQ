"""Reproduce los ejemplos resueltos de Turton et al. (2018), Sección 7.3.

El libro redondea Cp° a tres cifras significativas y lee los factores de
figuras, por lo que las tolerancias son relativas (0.5 % a 1.5 %).
"""

import math

import pytest

from costiq import cost, plant_summary, tray_area

CEPCI_2016 = 542.0  # valor que usa el libro para 2016


def rel(x, ref, tol):
    return x == pytest.approx(ref, rel=tol)


# --- Ejemplos 7.10 a 7.12: cabezal flotante de 100 m² -----------------------

def test_ex_7_10_base_case_fbm():
    r = cost("hx_floating_head", 100, "CS/CS", pressure=1, pressure_option="both")
    assert r.FP == 1.0
    assert rel(r.FBM, 3.29, 0.002)


def test_ex_7_11_pressure_factor_100_barg():
    r = cost("hx_floating_head", 100, "CS/CS", pressure=100, pressure_option="both")
    assert rel(r.FP, 1.383, 0.001)
    assert rel(r.FBM, 3.93, 0.003)


def test_ex_7_12a_stainless_ambient():
    r = cost("hx_floating_head", 100, "SS/SS", pressure=1, pressure_option="both")
    assert r.FM == 2.73
    assert rel(r.FBM, 6.16, 0.002)


def test_ex_7_12b_stainless_100_barg():
    r = cost("hx_floating_head", 100, "SS/SS", pressure=100, pressure_option="both")
    assert rel(r.FBM, 7.90, 0.002)


# --- Ejemplo 7.13: torre SS de 3 m × 30 m con 40 platos perforados SS ------

def test_ex_7_13_tower_shell():
    r = cost("tower", material="SS", pressure=20, diameter=3, length=30)
    assert rel(r.capacity, 212.1, 0.001)
    assert rel(r.Cp0, 132_500, 0.002)
    assert rel(r.FP, 6.47, 0.002)
    assert r.FM == 3.11
    assert rel(r.FBM, 38.87, 0.002)
    assert rel(r.at(CEPCI_2016), 7_031_400, 0.005)


def test_ex_7_13_trays():
    r = cost("tray_sieve", tray_area(3), "SS", trays=40)
    assert rel(r.capacity, 7.0686, 0.0001)
    assert rel(r.Cp0, 4570, 0.002)
    assert r.Fq == 1.0
    assert rel(r.at(CEPCI_2016), 456_770, 0.003)


# --- Ejemplo 7.14: ampliación con columna, intercambiadores y bombas -------

E714 = [
    # (etiqueta, kwargs, FP, FM, FBM, Cp°, C_BM, C°_BM) — Tabla E7.14(b)
    ("E-101", dict(equipment="hx_floating_head", capacity=170, material="CS/CS",
                   pressure=5, pressure_option="both"),
     1.0, 1.0, 3.29, 33_000, 108_500, 108_500),
    ("E-102", dict(equipment="hx_floating_head", capacity=205, material="CS/SS",
                   pressure=18, pressure_option="both"),
     1.062, 1.81, 4.82, 36_900, 177_900, 121_300),
    ("E-103", dict(equipment="hx_double_pipe", capacity=10, material="CS/CS",
                   pressure=5),
     1.0, 1.0, 3.29, 3_700, 12_300, 12_300),
    ("P-101A/B", dict(equipment="pump_centrifugal", capacity=5, material="CS",
                      pressure=5, units=2),
     1.0, 1.55, 3.98, 3_200, 2 * 12_600, 2 * 10_300),
    ("T-101", dict(equipment="tower", material="CS", pressure=5, diameter=2.1,
                   length=23),
     1.68, 1.0, 5.31, 54_700, 290_700, 222_800),
    ("32 platos", dict(equipment="tray_sieve", capacity=tray_area(2.1),
                       material="SS", trays=32),
     1.0, None, 1.83, 2_200, 131_200, 71_700),
    ("V-101", dict(equipment="vessel_horizontal", material="CS", pressure=5,
                   diameter=1.8, length=6),
     1.513, 1.0, 3.79, 13_500, 51_200, 40_600),
]


@pytest.fixture(scope="module")
def e714_results():
    return {tag: cost(**kw) for tag, kw, *_ in E714}


@pytest.mark.parametrize("tag,kw,FP,FM,FBM,Cp0,CBM,CBM0", E714, ids=[r[0] for r in E714])
def test_ex_7_14_rows(e714_results, tag, kw, FP, FM, FBM, Cp0, CBM, CBM0):
    r = e714_results[tag]
    assert rel(r.FP, FP, 0.003)
    if FM is not None:
        assert rel(r.FM, FM, 0.001)
    assert rel(r.FBM, FBM, 0.003)
    assert rel(r.Cp0, Cp0, 0.025)  # el libro da Cp° con 2-3 cifras
    assert rel(r.CBM, CBM, 0.012)
    assert rel(r.CBM0, CBM0, 0.012)


def test_ex_7_14_totals(e714_results):
    results = list(e714_results.values())
    assert rel(sum(r.CBM for r in results), 797_000, 0.005)
    assert rel(sum(r.CBM0 for r in results), 597_800, 0.005)
    s = plant_summary(results, CEPCI_2016)
    assert rel(s.CBM, 1_088_100, 0.005)
    assert rel(s.CTM, 1_284_000, 0.005)
    assert rel(s.CGR, 1_692_000, 0.005)


def test_vessel_printed_equation_differs_from_examples(monkeypatch):
    """Con la Ec. A.2 tal como está impresa (P, no P + 1), T-101 no da 1.68."""
    from costiq import engine

    monkeypatch.setattr(engine, "VESSEL_GAUGE_OFFSET", 0.0)
    r = cost("tower", material="CS", pressure=5, diameter=2.1, length=23)
    assert math.isclose(r.FP, 1.484, rel_tol=0.002)
