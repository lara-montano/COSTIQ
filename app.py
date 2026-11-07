"""COSTIQ: interfaz web para costear equipo de proceso (Turton et al., 2018).

Ejecutar con:  streamlit run app.py
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from costiq import __version__
from costiq.data import (
    CATEGORIES, CEPCI, CEPCI_BASE, EQUIPMENT, EQUIPMENT_LIST, F_AUXILIARY,
    F_CONTINGENCY, F_FEE, METHOD_EQUATION, METHOD_SOURCE, TAG_PREFIX, TANKS,
    VESSEL_CA_M, VESSEL_E, VESSEL_S_BAR, VESSEL_TMIN_M,
)
from costiq.engine import (
    QUOTE_CATEGORY, QUOTE_KEY, VESSEL_GAUGE_OFFSET, CostError, CostResult, cost,
    plant_summary, quoted_cost, superheat_factor, tray_area, vessel_volume,
)
from ui import charts, theme

st.set_page_config(
    page_title="COSTIQ · Costeo de equipo de proceso",
    page_icon=":material/precision_manufacturing:",
    layout="wide",
    initial_sidebar_state="auto",
)
theme.inject()

ss = st.session_state
ss.setdefault("plant", [])
ss.setdefault("next_id", 1)
ss.setdefault("last_upload", None)

ENGINE_KEYS = ("equipment", "capacity", "material", "pressure", "pressure_option",
               "diameter", "length", "trays", "units", "fbm_override", "superheat")
QUOTE_KEYS = ("name", "capacity", "unit", "ref_cost", "ref_capacity", "ref_cepci",
              "exponent", "fbm", "units")

EXAMPLE_714 = [
    dict(tag="E-101", equipment="hx_floating_head", capacity=170, material="CS/CS",
         pressure=5.0, pressure_option="both"),
    dict(tag="E-102", equipment="hx_floating_head", capacity=205, material="CS/SS",
         pressure=18.0, pressure_option="both"),
    dict(tag="E-103", equipment="hx_double_pipe", capacity=10, material="CS/CS",
         pressure=5.0, pressure_option="all"),
    dict(tag="P-101 A/B", equipment="pump_centrifugal", capacity=5, material="CS",
         pressure=5.0, pressure_option="all", units=2),
    dict(tag="T-101", equipment="tower", material="CS", pressure=5.0, diameter=2.1,
         length=23.0),
    dict(tag="T-101 · platos", equipment="tray_sieve", capacity=round(tray_area(2.1), 4),
         material="SS", trays=32),
    dict(tag="V-101", equipment="vessel_horizontal", material="CS", pressure=5.0,
         diameter=1.8, length=6.0),
]


def run(spec: dict) -> CostResult:
    if spec.get("equipment") == QUOTE_KEY:
        return quoted_cost(**{k: spec[k] for k in QUOTE_KEYS if spec.get(k) is not None})
    return cost(**{k: spec[k] for k in ENGINE_KEYS if spec.get(k) is not None})


def pressure_text(spec: dict, r: CostResult) -> str:
    if not r.equipment.has_pressure:
        return "—"
    return f"{spec.get('pressure', 0.0):g} {r.equipment.pressure_unit}"


def next_tag(prefix: str, extra: list[str] = ()) -> str:
    nums = []
    for tag in [s["tag"] for s in ss.plant] + list(extra):
        m = re.match(rf"^{re.escape(prefix)}-(\d+)", tag)
        if m:
            nums.append(int(m.group(1)))
    return f"{prefix}-{max(nums) + 1 if nums else 101}"


def add_specs(specs: list[dict]) -> None:
    for spec in specs:
        ss.plant.append({**spec, "id": ss.next_id})
        ss.next_id += 1


def factor_name(method: str) -> str:
    return "F_M" if method in ("B1B2", "vessel") else "F_BM"


# ===========================================================================
# Barra lateral: parámetros del proyecto
# ===========================================================================

with st.sidebar:
    theme.eyebrow("Actualización de costos")
    years = sorted(CEPCI, reverse=True)
    cepci_choice = st.selectbox(
        "Índice CEPCI",
        years + ["custom"],
        format_func=lambda y: "Otro valor…" if y == "custom" else f"{y}  ·  {CEPCI[y]:.1f}",
        help="Chemical Engineering Plant Cost Index anual. Elige «Otro valor…» "
             "para usar un índice mensual o más reciente.",
    )
    if cepci_choice == "custom":
        cepci = st.number_input("Valor del CEPCI", min_value=100.0, max_value=5000.0,
                                value=CEPCI[years[0]], step=0.1, format="%.1f")
        cepci_text = f"{cepci:.1f}"
        cepci_year = None
    else:
        cepci = CEPCI[cepci_choice]
        cepci_text = f"{cepci_choice} · {cepci:.1f}"
        cepci_year = cepci_choice
    st.caption(f"Base de las correlaciones: {CEPCI_BASE:g} (mayo a septiembre de 2001). "
               f"Factor de actualización: ×{cepci / CEPCI_BASE:.3f}.")

    st.space("small")
    theme.eyebrow("Moneda")
    currency = st.segmented_control("Moneda", ["USD", "MXN"], default="USD",
                                    label_visibility="collapsed", key="currency") or "USD"
    fx = 1.0
    if currency == "MXN":
        fx = st.number_input("Tipo de cambio (MXN por USD)", min_value=1.0, max_value=100.0,
                             value=17.50, step=0.05, format="%.2f",
                             help="Usa el tipo de cambio FIX de Banxico de la fecha del estimado.")

    st.space("small")
    theme.eyebrow("Costo de planta")
    with st.expander("Factores de las Ecs. 7.15 y 7.16"):
        f_cont = st.number_input("Contingencia (% de C_BM)", 0.0, 100.0,
                                 F_CONTINGENCY * 100, 1.0, format="%.0f") / 100
        f_fee = st.number_input("Honorarios (% de C_BM)", 0.0, 50.0,
                                F_FEE * 100, 1.0, format="%.0f") / 100
        f_aux = st.number_input("Instalaciones auxiliares (% de C°_BM)", 0.0, 200.0,
                                F_AUXILIARY * 100, 5.0, format="%.0f") / 100
        st.caption("Valores del libro: 15 %, 3 % y 50 %. Las auxiliares van de 20 % a más "
                   "de 100 % según el sitio.")

    st.space("medium")
    st.caption(f"COSTIQ {__version__} · [Código fuente](https://github.com/lara-montano/COSTIQ)")


def fmt(v: float) -> str:
    return theme.money_short(v, 1.0)


# ===========================================================================
# Encabezado y pestañas
# ===========================================================================

theme.header(cepci_text, len(ss.plant))

tab_eq, tab_plant, tab_ref = st.tabs([
    ":material/tune: Equipo",
    ":material/factory: Planta",
    ":material/menu_book: Referencia",
])

METHOD_LABEL = {
    "B1B2": "Cp°(B₁ + B₂ F_M F_P)",
    "vessel": "Cp°(B₁ + B₂ F_M F_P), F_P por Ec. A.2",
    "FBM": "Cp° F_BM",
    "FBM_FP": "Cp° F_BM F_P",
    "tray": "Cp° N F_BM F_q",
}


# ===========================================================================
# Pestaña 1: un equipo
# ===========================================================================

with tab_eq:
    col_in, col_out = st.columns([0.36, 0.64], gap="large")

    # --- Entradas ---------------------------------------------------------
    with col_in:
        with st.container(border=True):
            theme.eyebrow("Equipo")
            category = st.selectbox("Categoría", list(CATEGORIES) + [QUOTE_CATEGORY],
                                    key="in_category",
                                    help="«Cotización propia» costea cualquier equipo a "
                                         "partir de un precio de referencia.")
            if category == QUOTE_CATEGORY:
                k = QUOTE_KEY
                theme.eyebrow("Equipo a costear")
                q_name = st.text_input("Nombre del equipo", value="Molino de martillos",
                                       key="q_name")
                c1, c2 = st.columns(2)
                q_unit = c1.text_input("Unidad de tamaño", value="t/h", key="q_unit",
                                       help="La que use tu cotización: t/h, kg/h, m², kW…")
                capacity = c2.number_input("Tamaño por unidad", min_value=1e-4, max_value=1e9,
                                           value=20.0, format="%.4g", key="q_cap")
                units = st.number_input("Unidades idénticas", min_value=1, max_value=50,
                                        value=1, step=1, key="units_custom")
                theme.eyebrow("Cotización de referencia")
                c1, c2 = st.columns(2)
                q_cost = c1.number_input(
                    "Precio de compra (USD)", min_value=1.0, max_value=1e10, value=50_000.0,
                    step=1_000.0, format="%.0f", key="q_cost",
                    help="En USD del año de la cotización. Si está en MXN, conviértela con "
                         "el tipo de cambio de esa fecha.")
                q_refcap = c2.number_input("Tamaño cotizado", min_value=1e-4, max_value=1e9,
                                           value=10.0, format="%.4g", key="q_refcap")
                q_year = st.selectbox(
                    "CEPCI de la cotización", years + ["custom"],
                    format_func=lambda y: "Otro valor…" if y == "custom"
                    else f"{y}  ·  {CEPCI[y]:.1f}", key="q_year")
                if q_year == "custom":
                    q_cepci = st.number_input("CEPCI de la cotización", min_value=100.0,
                                              max_value=5000.0, value=CEPCI[years[0]],
                                              step=0.1, format="%.1f", key="q_cepci")
                else:
                    q_cepci = CEPCI[q_year]
                c1, c2 = st.columns(2)
                q_n = c1.number_input(
                    "Exponente n", min_value=0.05, max_value=1.5, value=0.6, step=0.01,
                    format="%.2f", key="q_n",
                    help="0.6 es la regla de los seis décimos (Ec. 7.1). La Tabla 7.3 "
                         "del libro da de 0.30 a 0.84 según el equipo.")
                q_fbm = c2.number_input(
                    "F_BM", min_value=1.0, max_value=10.0, value=1.0, step=0.05,
                    format="%.2f", key="q_fbm",
                    help="1.0 = solo compra. En la Tabla A.7 los factores de instalación "
                         "van de 1.10 a 2.86.")
                st.caption("Para equipos sin correlación en el Apéndice A: molinos, "
                           "extrusores, membranas, túneles de congelación…")
                form = dict(equipment=QUOTE_KEY, name=q_name, capacity=capacity, unit=q_unit,
                            ref_cost=q_cost, ref_capacity=q_refcap, ref_cepci=q_cepci,
                            exponent=q_n, fbm=q_fbm, units=units)
                eq = None
                material, pressure, option, diameter, internals = "—", 0.0, None, None, None
                fname = "F_BM"
            else:
                eq_key = st.selectbox(
                    "Tipo", [e.key for e in CATEGORIES[category]],
                    format_func=lambda k: EQUIPMENT[k].name, key=f"in_type_{category}",
                    help="Nombre original en Turton: se muestra al pie del formulario.",
                )
                eq = EQUIPMENT[eq_key]
                k = eq.key

                theme.eyebrow("Tamaño")
                diameter = length = capacity = None
                if eq.method == "vessel":
                    c1, c2 = st.columns(2)
                    diameter = c1.number_input("Diámetro D (m)", min_value=0.1, max_value=20.0,
                                               value=2.0 if k == "tower" else 1.5, step=0.1,
                                               format="%.2f", key=f"D_{k}")
                    length = c2.number_input(
                        "Longitud L (m)" if eq.geometry == "horizontal" else "Altura H (m)",
                        min_value=0.1, max_value=200.0,
                        value=20.0 if k == "tower" else 5.0, step=0.5, format="%.2f",
                        key=f"L_{k}")
                    vol = vessel_volume(diameter, length)
                    inside = eq.a_min <= vol <= eq.a_max
                    st.caption(f"Volumen πD²L/4 = **{theme.num(vol)} m³** · rango de la "
                               f"correlación {eq.a_min:g}–{eq.a_max:g} m³"
                               + ("" if inside else " · **fuera de rango**"))
                else:
                    cap_default = theme.nice_default(eq.a_min, eq.a_max)
                    capacity = st.number_input(
                        f"{eq.attribute} ({eq.unit})", min_value=1e-4, max_value=1e7,
                        value=cap_default,
                        step=float(10 ** (math.floor(math.log10(cap_default)) - 1)),
                        format="%.4g", key=f"cap_{k}",
                        help="Por unidad. Puedes salir del rango; COSTIQ lo marca como extrapolación.")
                    st.caption(f"Rango de la correlación: {eq.a_min:g}–{eq.a_max:,g} {eq.unit} "
                               "(Tabla A.1)")
                units = st.number_input("Unidades idénticas", min_value=1, max_value=50, value=1,
                                        step=1, key=f"units_{k}",
                                        help="Equipos en paralelo o de respaldo, p. ej., P-101 A/B.")

                theme.eyebrow("Material y operación")
                mat_codes = [m.code for m in eq.materials]
                fname = factor_name(eq.method)
                material = st.selectbox(
                    "Material de construcción", mat_codes,
                    format_func=lambda c: f"{eq.material(c).label}  ·  {fname} {eq.material(c).factor:.2f}",
                    key=f"mat_{k}", disabled=len(mat_codes) == 1,
                )

                pressure, option = 0.0, None
                if eq.has_pressure:
                    if len(eq.pressure) > 1:
                        option = st.radio("Correlación de presión (Tabla A.2)",
                                          [o.key for o in eq.pressure],
                                          format_func=lambda o: eq.pressure_option(o).label,
                                          key=f"popt_{k}", horizontal=True)
                    elif eq.pressure:
                        option = eq.pressure[0].key
                    pressure = st.number_input(f"{eq.pressure_label} ({eq.pressure_unit})",
                                               min_value=-1.0, max_value=2000.0, value=0.0,
                                               step=1.0, format="%.2f", key=f"P_{k}")
                    if eq.method == "vessel":
                        st.caption("F_P por la Ec. A.2 (ASME), válida para pared delgada.")
                    else:
                        st.caption(f"Tabla A.2 válida hasta {eq.pressure_limit:g} "
                                   f"{eq.pressure_unit}.")
                elif eq.category == TANKS:
                    st.caption("Tanque atmosférico (P < 0.07 barg). Sin corrección por presión.")
                else:
                    st.caption("Este equipo no tiene corrección por presión en el libro.")

                trays = 1
                if eq.method == "tray":
                    trays = st.number_input("Número de platos o eliminadores", min_value=1,
                                            max_value=300, value=20, step=1, key=f"N_{k}",
                                            help="F_q = 1 para N ≥ 20 (Tabla A.5).")

                fbm_override = None
                if eq.fbm_editable:
                    fbm_override = st.number_input("F_BM supuesto", min_value=1.0, max_value=10.0,
                                                   value=float(eq.base_material.factor),
                                                   step=0.05, format="%.2f",
                                                   key=f"fbm_{k}", help=eq.note)

                superheat = 0.0
                if eq.superheat:
                    superheat = st.number_input(
                        "Sobrecalentamiento ΔT (°C)", min_value=0.0, max_value=400.0, value=0.0,
                        step=5.0, format="%.0f", key=f"dT_{k}",
                        help="F_T = 1 + 0.00184 ΔT − 0.00000335 ΔT² (Tabla A.5). "
                             "0 para vapor saturado.")

                internals = None
                if k == "tower":
                    theme.eyebrow("Internos de la torre")
                    kind = st.segmented_control("Internos", ["Ninguno", "Platos", "Empaque"],
                                                default="Platos", key="tower_kind",
                                                label_visibility="collapsed") or "Ninguno"
                    if kind == "Platos":
                        c1, c2 = st.columns(2)
                        tray_key = c1.selectbox("Tipo de plato", ["tray_sieve", "tray_valve"],
                                                format_func=lambda t: EQUIPMENT[t].name,
                                                key="tower_tray_type")
                        n_tr = c2.number_input("Platos", 1, 300, 30, 1, key="tower_n")
                        t_eq = EQUIPMENT[tray_key]
                        t_mat = st.selectbox(
                            "Material de los platos", [m.code for m in t_eq.materials],
                            format_func=lambda c: f"{t_eq.material(c).label}  ·  F_BM "
                                                  f"{t_eq.material(c).factor:.2f}",
                            key="tower_tray_mat")
                        internals = dict(equipment=tray_key, capacity=tray_area(diameter),
                                         material=t_mat, trays=n_tr, units=units,
                                         label="platos")
                        st.caption(f"Área de plato πD²/4 = {theme.num(tray_area(diameter))} m²")
                    elif kind == "Empaque":
                        c1, c2 = st.columns(2)
                        h_pk = c1.number_input("Altura empacada (m)", 0.1, 200.0,
                                               float(round(0.8 * length, 1)), 0.5,
                                               key="tower_pack_h")
                        p_eq = EQUIPMENT["packing"]
                        p_mat = c2.selectbox(
                            "Material", [m.code for m in p_eq.materials],
                            format_func=lambda c: p_eq.material(c).label, key="tower_pack_mat")
                        internals = dict(equipment="packing",
                                         capacity=tray_area(diameter) * h_pk,
                                         material=p_mat, units=units, label="empaque")
                        st.caption(f"Volumen de empaque = {theme.num(tray_area(diameter) * h_pk)} m³")

                form = dict(equipment=k, capacity=capacity, material=material,
                            pressure=pressure, pressure_option=option, diameter=diameter,
                            length=length, trays=trays, units=units,
                            fbm_override=fbm_override, superheat=superheat)

            st.space("small")
            prefix = TAG_PREFIX.get(category, "EQ")
            tag = st.text_input("Etiqueta en el DFP", value=next_tag(prefix),
                                key=f"tag_{k}_{ss.next_id}")
            add_clicked = st.button("Agregar a la planta", type="primary",
                                    icon=":material/add:", width="stretch")
            if eq is not None:
                st.caption(f"Turton: *{eq.name_en}* · {METHOD_SOURCE[eq.method]}")
            else:
                st.caption(METHOD_SOURCE["quote"])

    # --- Cálculo ------------------------------------------------------------
    main_spec = {"tag": tag, **form}
    specs = [main_spec]
    if internals:
        label = internals.pop("label")
        specs.append(dict(tag=f"{tag} · {label}", **internals))

    try:
        results = [run(s) for s in specs]
    except CostError as err:
        results = []
        with col_out:
            st.error(str(err), icon=":material/error:")

    if results and add_clicked:
        add_specs([{kk: v for kk, v in s.items() if v is not None} for s in specs])
        st.toast(f"{tag} agregado a la planta", icon=":material/check_circle:")
        st.rerun()

    # --- Resultados -----------------------------------------------------------
    if results:
        with col_out:
            main = results[0]
            eq = main.equipment
            total_now = sum(r.at(cepci) for r in results)
            internals_label = specs[1]["tag"].split(" · ")[-1] if len(specs) > 1 else None
            sub = [eq.name, f"{theme.num(main.capacity)} {eq.unit}",
                   main.material.label if len(eq.materials) > 1 else None,
                   f"{pressure:g} {eq.pressure_unit}" if eq.has_pressure else None,
                   f"{units} unidades" if units > 1 else None,
                   f"con {internals_label}" if internals_label else None]
            factors = [("C<sub>p</sub>° compra, USD 2001", theme.money(main.Cp0))]
            if eq.method == "quote":
                factors = [("C<sub>p</sub> escalado, USD base 397", theme.money(main.Cp0)),
                           ("S / S<sub>ref</sub>", f"{main.capacity / form['ref_capacity']:.3g}"),
                           ("n exponente", f"{form['exponent']:.2f}"),
                           ("F<sub>BM</sub> módulo", f"{main.FBM:.2f}")]
            elif eq.method in ("B1B2", "vessel"):
                factors += [("F<sub>M</sub> material", f"{main.FM:.2f}"),
                            ("F<sub>P</sub> presión", f"{main.FP:.3f}"),
                            ("F<sub>BM</sub> módulo", f"{main.FBM:.2f}")]
            elif eq.method == "FBM_FP":
                factors += [("F<sub>BM</sub> módulo", f"{main.FBM:.2f}"),
                            ("F<sub>P</sub> presión", f"{main.FP:.3f}")]
                if eq.superheat:
                    factors.append(("F<sub>T</sub> sobrecalentamiento", f"{main.FT:.3f}"))
            elif eq.method == "tray":
                factors += [("N platos", f"{main.trays}"), ("F<sub>q</sub> cantidad", f"{main.Fq:.3f}"),
                            ("F<sub>BM</sub> módulo", f"{main.FBM:.2f}")]
            else:
                factors += [("F<sub>BM</sub> módulo", f"{main.FBM:.2f}")]
            if main.thickness is not None:
                factors.append(("Espesor de pared", f"{main.thickness * 1000:,.1f} mm"))
            factors.append(("C°<sub>BM</sub> base",
                            theme.money_short(sum(r.CBM0 for r in results) * cepci / CEPCI_BASE, fx)))

            theme.hero(
                f"Costo de módulo desnudo · C<sub>BM</sub> · CEPCI {theme.esc(cepci_text)}",
                theme.money(total_now, fx), currency,
                " · ".join(s for s in sub if s), factors,
            )

            if len(results) > 1:
                st.space("small")
                st.dataframe(
                    pd.DataFrame([{
                        "Componente": s["tag"],
                        "Equipo": r.equipment.name,
                        "Tamaño": f"{theme.num(r.capacity)} {r.equipment.unit}",
                        "F_BM": round(r.FBM, 2),
                        f"C_BM ({currency})": round(r.at(cepci) * fx),
                    } for s, r in zip(specs, results)]),
                    hide_index=True, width="stretch",
                    column_config={f"C_BM ({currency})": st.column_config.NumberColumn(format="localized")},
                )

            seen = set()
            for r in results:
                for n in r.notices:
                    if n.text in seen:
                        continue
                    seen.add(n.text)
                    if n.level == "warning":
                        st.warning(n.text, icon=":material/warning:")
                    else:
                        theme.note(n.text)

            # Cascada
            theme.section("De dónde sale el costo",
                          "Compra a condiciones base, instalación, efecto del material y la presión, "
                          "e inflación hasta el CEPCI elegido.")
            steps = {}
            for r in results:
                for name, v in r.breakdown(cepci):
                    steps[name] = steps.get(name, 0.0) + v * fx
            st.plotly_chart(
                charts.waterfall(list(steps.items()), "C<sub>BM</sub> hoy", fmt, currency),
                config={"displayModeBar": False}, key="wf",
            )

            # Sensibilidad
            theme.section("Sensibilidad", "Cómo cambia el costo de módulo del equipo principal al "
                                          "mover una sola variable. La línea punteada es extrapolación.")
            options = ["Capacidad"]
            if eq.has_pressure:
                options.append("Presión")
            if len(eq.materials) > 1:
                options.append("Material")
            options.append("Año")
            view = st.segmented_control("Variable", options, default="Capacidad",
                                        key=f"sens_{k}", label_visibility="collapsed") or "Capacidad"

            y_title = f"C<sub>BM</sub> ({currency})"

            def sweep_cost(**over):
                return run({**main_spec, **over})

            if view == "Capacidad":
                lo, hi = min(eq.a_min, main.capacity), max(eq.a_max, main.capacity)
                log_x = hi / lo > 20
                n = 90
                xs = ([lo * (hi / lo) ** (i / (n - 1)) for i in range(n)] if log_x
                      else [lo + (hi - lo) * i / (n - 1) for i in range(n)])
                over = {"length": None} if eq.method == "vessel" else {}
                ys = [sweep_cost(capacity=x, **over).at(cepci) * fx for x in xs]
                valid = [eq.a_min <= x <= eq.a_max for x in xs]
                fig = charts.sweep(xs, ys, valid, (main.capacity, main.at(cepci) * fx),
                                   x_title=f"{eq.attribute} por unidad ({eq.unit})",
                                   y_title=y_title, log_x=log_x)
            elif view == "Presión":
                if eq.method == "vessel":
                    p_hi = max(40.0, 1.4 * pressure)
                else:
                    p_hi = max(1.3 * eq.pressure_limit, 1.15 * pressure)
                ps = [p_hi * i / 120 for i in range(121)]
                rs = [sweep_cost(pressure=p) for p in ps]
                if eq.method == "vessel":
                    valid = [(r.thickness or 0) <= 0.25 * diameter for r in rs]
                else:
                    valid = [p <= eq.pressure_option(option).p_max for p in ps]
                fig = charts.sweep(ps, [r.at(cepci) * fx for r in rs], valid,
                                   (pressure, main.at(cepci) * fx),
                                   x_title=f"{eq.pressure_label} ({eq.pressure_unit})",
                                   y_title=y_title, log_x=False,
                                   hover_extra=[f"<br>F_P = {r.FP:.3f}" for r in rs])
            elif view == "Material":
                rs = [sweep_cost(material=m.code) for m in eq.materials]
                fig = charts.material_bars([m.code for m in eq.materials],
                                           [r.at(cepci) * fx for r in rs], material, fmt,
                                           currency, fname, [m.factor for m in eq.materials])
            else:
                yrs = sorted(CEPCI)
                vals = [main.CBM * CEPCI[y] / CEPCI_BASE * fx for y in yrs]
                sel = (cepci_year, main.at(cepci) * fx) if cepci_year else None
                fig = charts.cepci_line(yrs, vals, sel, y_title, f"CEPCI {cepci_text}")
            st.plotly_chart(fig, config={"displayModeBar": False}, key=f"sens_fig_{view}")

            # Paso a paso
            with st.expander("Cálculo paso a paso", icon=":material/functions:"):
                if eq.method == "quote":
                    st.markdown("**1. Escalamiento de la cotización** (Ec. 7.1) y paso a la base "
                                "CEPCI = 397 (Ec. 7.4)")
                    st.latex(
                        rf"C_p = \${form['ref_cost']:,.0f}\left(\frac{{{theme.num(main.capacity)}}}"
                        rf"{{{theme.num(form['ref_capacity'])}}}\right)^{{{form['exponent']:.2f}}}"
                        rf"\frac{{397}}{{{form['ref_cepci']:.1f}}} = \${main.Cp0:,.0f}".replace(",", "{,}")
                    )
                    st.markdown("**2. Costo de módulo desnudo** con el F_BM que elegiste")
                    st.latex(rf"C_{{BM}}(2001) = {units}\times\${main.Cp0:,.0f}\times{main.FBM:.2f}"
                             rf" = \${main.CBM:,.0f}".replace(",", "{,}"))
                    st.markdown("**3. Actualización por inflación** (Ec. 7.4)")
                    st.latex(rf"C_{{BM}} = \${main.CBM:,.0f}\times\frac{{{cepci:.1f}}}{{397}} = "
                             rf"\${main.at(cepci):,.0f}\ \text{{USD}}".replace(",", "{,}"))
                else:
                    lA = math.log10(main.capacity)
                    st.markdown("**1. Costo de compra a condiciones base** (Ec. A.1, CEPCI = 397)")
                    st.latex(
                        rf"\log_{{10}} C_p^\circ = {eq.K1} {eq.K2:+} \log_{{10}}({theme.num(main.capacity)})"
                        rf" {eq.K3:+} [\log_{{10}}({theme.num(main.capacity)})]^2 = "
                        rf"{eq.K1 + eq.K2 * lA + eq.K3 * lA * lA:.4f}".replace(",", "{,}")
                    )
                    st.latex(rf"C_p^\circ = \${main.Cp0:,.0f}".replace(",", "{,}"))

                    st.markdown("**2. Factor de presión**")
                    if eq.method == "vessel":
                        if pressure < -0.5:
                            st.latex(r"P < -0.5\ \text{barg} \Rightarrow F_P = 1.25")
                        else:
                            Pd = pressure + VESSEL_GAUGE_OFFSET
                            st.latex(
                                rf"F_P = \frac{{\dfrac{{(P+1)\,D}}{{2\,[S E - 0.6\,(P+1)]}} + CA}}{{t_{{min}}}}"
                                rf" = \frac{{\dfrac{{{Pd:g}\times{diameter:g}}}{{2\,[{VESSEL_S_BAR:g}"
                                rf"\times{VESSEL_E:g} - 0.6\times{Pd:g}]}} + {VESSEL_CA_M}}}{{{VESSEL_TMIN_M}}}"
                                rf" = {main.FP:.3f}"
                            )
                            st.caption("Ec. A.2 con (P + 1), como en los Ejemplos 7.13 y 7.14. "
                                       "Si el resultado es menor que 1, F_P = 1.")
                    elif eq.has_pressure:
                        opt = eq.pressure_option(option)
                        band = next((b for b in opt.bands if pressure <= b.p_max), opt.bands[-1])
                        if pressure <= 0 or band.is_flat:
                            st.latex(rf"P = {pressure:g}\ \text{{{eq.pressure_unit}}} \Rightarrow F_P = 1")
                        else:
                            lP = math.log10(pressure)
                            st.latex(
                                rf"\log_{{10}} F_P = {band.C1:g} {band.C2:+g}\log_{{10}}({pressure:g})"
                                rf" {band.C3:+g}[\log_{{10}}({pressure:g})]^2"
                                rf" = {band.C1 + band.C2 * lP + band.C3 * lP * lP:.4f}"
                            )
                            st.latex(rf"F_P = {main.FP:.3f}")
                        st.caption(f"Tabla A.2 · {opt.label}.")
                    else:
                        st.markdown("No aplica para este equipo: F_P = 1.")

                    st.markdown("**3. Costo de módulo desnudo** (" + METHOD_SOURCE[eq.method] + ")")
                    st.latex(METHOD_EQUATION[eq.method])
                    if eq.method in ("B1B2", "vessel"):
                        st.latex(rf"F_{{BM}} = {eq.B1} + {eq.B2}\times{main.FM:.2f}\times{main.FP:.3f}"
                                 rf" = {main.FBM:.3f}")
                    elif eq.method == "tray":
                        st.latex(rf"N = {main.trays},\quad F_q = {main.Fq:.3f},\quad F_{{BM}} = {main.FBM:.2f}")
                    elif eq.superheat:
                        st.latex(rf"F_T = 1 + 0.00184\,({superheat:g}) - 0.00000335\,({superheat:g})^2"
                                 rf" = {main.FT:.4f}")
                        st.caption("Tabla A.5: C_BM = Cp° F_BM F_P F_T para calderas de vapor.")
                    st.latex(rf"C_{{BM}}(2001) = {units}\times\${main.CBM_unit:,.0f} = \${main.CBM:,.0f}"
                             .replace(",", "{,}"))

                    st.markdown("**4. Actualización por inflación** (Ec. 7.4)")
                    st.latex(rf"C_{{BM}} = \${main.CBM:,.0f}\times\frac{{{cepci:.1f}}}{{397}} = "
                             rf"\${main.at(cepci):,.0f}\ \text{{USD}}".replace(",", "{,}"))
                    if currency == "MXN":
                        st.latex(rf"\${main.at(cepci):,.0f}\ \text{{USD}}\times{fx:.2f} = "
                                 rf"\${main.at(cepci) * fx:,.0f}\ \text{{MXN}}".replace(",", "{,}"))


# ===========================================================================
# Pestaña 2: planta
# ===========================================================================

with tab_plant:
    if not ss.plant:
        theme.empty_state(
            "La planta todavía no tiene equipos",
            "Costea un equipo en la pestaña «Equipo» y agrégalo, abre un proyecto guardado "
            "o carga el Ejemplo 7.14 de Turton para ver cómo se arma un estimado completo.")
        _, c1, c2, _ = st.columns([1, 1.1, 1.1, 1])
        if c1.button("Cargar el Ejemplo 7.14", icon=":material/science:", width="stretch"):
            add_specs([dict(s) for s in EXAMPLE_714])
            st.rerun()
        with c2.popover("Abrir proyecto", icon=":material/folder_open:", width="stretch"):
            upload = st.file_uploader("Proyecto de COSTIQ (.json)", type=["json"],
                                      key="upload_empty")
    else:
        upload = None
        rows = []
        bad = []
        for spec in ss.plant:
            try:
                rows.append((spec, run(spec)))
            except (CostError, KeyError) as err:
                bad.append(f"{spec.get('tag', '?')}: {err}")
        for b in bad:
            st.error(f"No se pudo costear {b}", icon=":material/error:")

        results = [r for _, r in rows]
        s = plant_summary(results, cepci, f_cont, f_fee, f_aux)

        theme.kpis([
            dict(label="Módulo desnudo, ΣC<sub>BM</sub>", value=theme.money(s.CBM, fx),
                 currency=currency, detail=f"{len(rows)} partidas · CEPCI {theme.esc(cepci_text)}"),
            dict(label="Módulo total, C<sub>TM</sub>", value=theme.money(s.CTM, fx),
                 currency=currency,
                 detail=f"ΣC<sub>BM</sub> × (1 + {f_cont:.0%} + {f_fee:.0%}) · Ec. 7.15 · ampliaciones"),
            dict(label="Grassroots, C<sub>GR</sub>", value=theme.money(s.CGR, fx),
                 currency=currency, main=True,
                 detail=f"C<sub>TM</sub> + {f_aux:.0%} ΣC°<sub>BM</sub> · Ec. 7.16 · planta nueva"),
        ])

        theme.section("Composición del costo grassroots")
        st.plotly_chart(charts.composition([
            ("Módulo desnudo", s.CBM * fx, charts.SERIES_1),
            ("Contingencia y honorarios", (s.contingency + s.fee) * fx, charts.SERIES_2),
            ("Instalaciones auxiliares", s.auxiliary * fx, charts.SERIES_3),
        ], fmt, currency), config={"displayModeBar": False}, key="composition")

        theme.section("Inventario de equipos",
                      "Selecciona filas para quitarlas. Los costos se recalculan con el CEPCI y "
                      "la moneda de la barra lateral.")
        total_cbm = s.CBM or 1.0
        df = pd.DataFrame([{
            "Etiqueta": spec["tag"],
            "Equipo": r.equipment.name,
            "Tamaño": f"{theme.num(r.capacity)} {r.equipment.unit}",
            "Material": r.material.code,
            "Presión": pressure_text(spec, r),
            "Unid.": r.units,
            "F_BM": round(r.FBM, 2),
            f"C_BM ({currency})": round(r.at(cepci) * fx),
            f"C°_BM ({currency})": round(r.CBM0 * cepci / CEPCI_BASE * fx),
            "% de ΣC_BM": r.at(cepci) / total_cbm * 100,
        } for spec, r in rows])
        event = st.dataframe(
            df, hide_index=True, width="stretch", on_select="rerun",
            selection_mode="multi-row", key="plant_table",
            column_config={
                f"C_BM ({currency})": st.column_config.NumberColumn(format="localized"),
                f"C°_BM ({currency})": st.column_config.NumberColumn(format="localized"),
                "% de ΣC_BM": st.column_config.ProgressColumn(
                    format="%.1f %%", min_value=0, max_value=100, width="small"),
            },
        )
        selected_rows = event.selection.rows if event else []

        c1, c2, c3, c4, c5 = st.columns([1.15, 1, 1, 1.1, 1.1])
        if c1.button(f"Quitar ({len(selected_rows)})", icon=":material/delete:",
                     disabled=not selected_rows, width="stretch",
                     help="Quita las filas seleccionadas en la tabla."):
            ids = {rows[i][0]["id"] for i in selected_rows}
            ss.plant = [p for p in ss.plant if p["id"] not in ids]
            st.rerun()
        if c2.button("Vaciar planta", icon=":material/restart_alt:", width="stretch"):
            ss.plant = []
            st.rerun()

        export = pd.DataFrame([{
            "Etiqueta": spec["tag"], "Clave": r.equipment.key, "Equipo": r.equipment.name,
            "Categoría": r.equipment.category, "Capacidad": r.capacity,
            "Unidad": r.equipment.unit, "Unidades": r.units, "Material": r.material.code,
            "Presión": spec.get("pressure"), "Unidad de presión": r.equipment.pressure_unit,
            "Diámetro (m)": spec.get("diameter"),
            "Longitud (m)": spec.get("length"), "Platos": r.trays, "F_M": r.FM, "F_P": r.FP,
            "F_BM": r.FBM, "F_q": r.Fq, "Cp0 por unidad (USD 2001)": round(r.Cp0, 2),
            "C_BM (USD 2001)": round(r.CBM, 2), "C0_BM (USD 2001)": round(r.CBM0, 2),
            "CEPCI": cepci, f"C_BM ({currency})": round(r.at(cepci) * fx, 2),
        } for spec, r in rows])
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        c3.download_button("CSV", export.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"costiq_planta_{stamp}.csv", mime="text/csv",
                           icon=":material/table_view:", width="stretch")
        project = {"costiq": __version__, "fecha": datetime.now().isoformat(timespec="seconds"),
                   "cepci": cepci, "equipos": [{kk: v for kk, v in p.items() if kk != "id"}
                                               for p in ss.plant]}
        c4.download_button("Guardar proyecto", json.dumps(project, ensure_ascii=False, indent=2),
                           file_name=f"costiq_proyecto_{stamp}.json", mime="application/json",
                           icon=":material/save:", width="stretch")
        with c5.popover("Abrir proyecto", icon=":material/folder_open:", width="stretch"):
            upload = st.file_uploader("Proyecto de COSTIQ (.json)", type=["json"],
                                      key="upload_full")
            st.caption("Reemplaza la planta actual.")

        theme.section("¿Qué equipo pesa más?", "Costo de módulo por partida, de mayor a menor.")
        st.plotly_chart(charts.pareto([f"{spec['tag']} · {r.equipment.name}" for spec, r in rows],
                                      [r.at(cepci) * fx for _, r in rows], fmt, currency),
                        config={"displayModeBar": False}, key="pareto")

    if upload is not None and upload.file_id != ss.last_upload:
        ss.last_upload = upload.file_id
        try:
            data = json.loads(upload.getvalue().decode("utf-8"))
            items = data["equipos"] if isinstance(data, dict) else data
            for it in items:
                if it.get("equipment") not in EQUIPMENT and it.get("equipment") != QUOTE_KEY:
                    raise KeyError(f"equipo desconocido: {it.get('equipment')}")
                run(it)
            ss.plant = []
            add_specs(items)
            st.toast(f"Proyecto cargado: {len(items)} equipos", icon=":material/check_circle:")
            st.rerun()
        except (ValueError, KeyError, TypeError, CostError) as err:
            st.error(f"No se pudo abrir el proyecto: {err}", icon=":material/error:")


# ===========================================================================
# Pestaña 3: referencia
# ===========================================================================

with tab_ref:
    c1, c2 = st.columns([0.55, 0.45], gap="large")
    with c1:
        theme.section("Cómo calcula COSTIQ")
        st.markdown("**1. Costo de compra** a acero al carbón y presión ambiente (Ec. A.1, "
                    "Tabla A.1), en USD con CEPCI = 397.")
        st.latex(r"\log_{10} C_p^\circ = K_1 + K_2 \log_{10} A + K_3 (\log_{10} A)^2")
        st.markdown("**2. Factor de presión.** Recipientes y torres usan la Ec. A.2; el resto, "
                    "la Ec. A.3 con la Tabla A.2.")
        st.latex(r"F_{P} = \frac{\dfrac{(P+1)D}{2[SE-0.6(P+1)]} + CA}{t_{min}}")
        st.latex(r"\log_{10} F_P = C_1 + C_2 \log_{10} P + C_3 (\log_{10} P)^2")
        st.markdown("**3. Costo de módulo desnudo.** Intercambiadores, recipientes y bombas "
                    "usan la Ec. A.4; el resto, la Tabla A.5.")
        st.latex(r"C_{BM} = C_p^\circ(B_1 + B_2 F_M F_P)")
        st.latex(r"C_{BM} = C_p^\circ F_{BM} F_P \qquad C_{BM} = C_p^\circ N F_{BM} F_q")
        st.markdown("**4. Inflación** con el CEPCI elegido (Ec. 7.4).")
        st.latex(r"C_{BM}(\text{año}) = C_{BM}(2001)\,\frac{CEPCI_{\text{año}}}{397}")
        st.markdown("**5. Planta** (Ecs. 7.15 y 7.16). C°_BM es el costo de módulo con "
                    "F_M = F_P = 1, es decir, a condiciones base.")
        st.latex(r"C_{TM} = 1.18\sum C_{BM,i}")
        st.latex(r"C_{GR} = C_{TM} + 0.50\sum C^\circ_{BM,i}")

    with c2:
        theme.section("Decisiones y supuestos de esta versión")
        st.markdown("""
- **Ec. A.2 con (P + 1).** La 5.ª edición imprime P, pero sus Ejemplos 7.13 y 7.14 usan
  (P + 1). COSTIQ sigue los ejemplos y los reproduce dentro de 0.5 %.
- **Factores de figura.** F_M (Fig. A.18) y F_BM (Fig. A.19) se digitalizaron de las
  gráficas del libro, con ±0.03 a ±0.04 de resolución.
- **Fuera de rango.** Capacidad y presión fuera de la correlación se extrapolan y se
  marcan; F_P nunca baja al pasar el límite tabulado.
- **Tanques API.** El libro no da F_BM; COSTIQ supone 1.0 y permite cambiarlo.
- **Reactores.** F_BM = 4.0 es una estimación del libro (Tabla A.7).
- **Compresores.** Se costean sin accionamiento; el motor o la turbina va aparte.
- **Evaporadores.** La Tabla A.2 imprime «P < 0» para el primer tramo; la correlación
  da F_P = 1 en 10 barg, así que COSTIQ usa P < 10.
- **Calderas de vapor.** El libro no da F_BM; COSTIQ supone 2.16 (calentador de fluido
  térmico) y permite cambiarlo. F_T corrige por sobrecalentamiento.
- **Cotización propia.** Para equipos sin correlación (molinos, extrusores, membranas,
  túneles de congelación) se escala un precio de referencia con la Ec. 7.1.
""")
        theme.section("Cita")
        st.code("Turton, R., Shaeiwitz, J. A., Bhattacharyya, D., & Whiting, W. B. (2018).\n"
                "Analysis, Synthesis, and Design of Chemical Processes (5th ed.).\n"
                "Pearson. Appendix A.", language=None, wrap_lines=True)

    theme.section("Catálogo de equipos", f"{len(EQUIPMENT_LIST)} tipos en "
                                          f"{len(CATEGORIES)} categorías.")
    cat_filter = st.selectbox("Categoría", ["Todas"] + list(CATEGORIES), key="ref_cat",
                              label_visibility="collapsed")
    st.dataframe(pd.DataFrame([{
        "Categoría": e.category, "Equipo": e.name, "Nombre en Turton": e.name_en,
        "Atributo": f"{e.attribute} ({e.unit})", "Mín.": e.a_min, "Máx.": e.a_max,
        "K₁": e.K1, "K₂": e.K2, "K₃": e.K3, "Método": METHOD_LABEL[e.method],
        "Materiales": len(e.materials),
    } for e in EQUIPMENT_LIST if cat_filter in ("Todas", e.category)]),
        hide_index=True, width="stretch",
        column_config={"Método": st.column_config.TextColumn(width="medium"),
                       **{c: st.column_config.NumberColumn(format="%.5g")
                          for c in ("K₁", "K₂", "K₃", "Mín.", "Máx.")}})

    c1, c2 = st.columns([0.5, 0.5], gap="large")
    with c1:
        theme.section("Factores de material o de módulo",
                      "Con su identificador en las Tablas A.3 y A.6.")
        ref_key = st.selectbox("Equipo", [e.key for e in EQUIPMENT_LIST],
                               format_func=lambda x: f"{EQUIPMENT[x].category} · {EQUIPMENT[x].name}",
                               key="ref_eq", label_visibility="collapsed")
        re_eq = EQUIPMENT[ref_key]
        st.dataframe(pd.DataFrame([{
            "Material": m.label, "Código": m.code, factor_name(re_eq.method): m.factor,
            "Fuente": m.ref,
        } for m in re_eq.materials]), hide_index=True, width="stretch")
        if re_eq.pressure:
            st.dataframe(pd.DataFrame([{
                "Correlación": opt.label, f"Hasta ({re_eq.pressure_unit})": b.p_max,
                "C₁": b.C1, "C₂": b.C2, "C₃": b.C3,
            } for opt in re_eq.pressure for b in opt.bands]), hide_index=True, width="stretch",
                column_config={c: st.column_config.NumberColumn(format="%.6g")
                               for c in ("C₁", "C₂", "C₃")})
    with c2:
        theme.section("Índice CEPCI", "Promedios anuales; 2002–2024 pendientes de verificar "
                                       "contra la fuente primaria.")
        st.plotly_chart(charts.cepci_index(sorted(CEPCI), [CEPCI[y] for y in sorted(CEPCI)],
                                           CEPCI_BASE),
                        config={"displayModeBar": False}, key="cepci_ref")

theme.footer(__version__)
