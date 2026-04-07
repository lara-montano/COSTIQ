"""
Estimador de Costos de Equipos de Proceso — COSTIQ
Basado en Turton et al. (2018) - Apéndice A
Analysis, Synthesis, and Design of Chemical Processes, 5th Edition.
Desarrollado con Streamlit + Plotly
"""

import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

from data import (
    CEPCI, CEPCI_BASE, EQUIPMENT, B1B2, FM_MAP,
    FBM_FIXED, PRESSURE_FACTORS, COST_METHOD,
)

# ============================================================
# Funciones de cálculo
# ============================================================

def calc_cp0(K1, K2, K3, A):
    """Costo base de compra (Eq. A.1). Cp° en USD (CEPCI=397)."""
    log_A = math.log10(A)
    log_Cp = K1 + K2 * log_A + K3 * log_A**2
    return 10**log_Cp


def calc_fp_equation(C1, C2, C3, P):
    """Factor de presión con Eq. A.3. P en barg."""
    if P <= 0:
        return 1.0
    log_P = math.log10(P)
    log_FP = C1 + C2 * log_P + C3 * log_P**2
    FP = 10**log_FP
    return max(FP, 1.0)


def calc_fp_vessel(P, D):
    """Factor de presión para recipientes (Eq. A.2).
    P en barg, D en metros.
    FP = ((P*D)/(2*(850-0.6*P)) + 0.00315) / 0.0063
    donde 0.0063 = espesor mínimo de pared (m).
    """
    if P < -0.5:
        return 1.25  # Vacío según Turton
    if P <= 0:
        return 1.0
    # Guardia: denominador 2*(850 - 0.6*P) → cero cuando P ≈ 1416.67 barg
    # Para P > ~1400 barg la ecuación pierde validez física (singularidad ASME)
    denom = 2 * (850 - 0.6 * P)
    if denom <= 0:
        return 50.0  # Valor alto seguro; ecuación no válida a esta presión
    numerator = (P * D) / denom + 0.00315
    FP = numerator / 0.0063
    return max(FP, 1.0)


def calc_fq(N):
    """Factor de cantidad para platos (Fq). N = número de platos."""
    if N >= 20:
        return 1.0
    if N <= 0:
        return 1.0
    log_N = math.log10(N)
    log_Fq = 0.4771 + 0.08516 * log_N - 0.3473 * log_N**2
    return 10**log_Fq


# Equipos shell-and-tube con FP separado para shell y tube
HX_WITH_SIDES = {
    "Floating head", "Fixed tube sheet", "U-tube",
    "Bayonet", "Kettle reboiler", "Spiral tube",
}


def get_fp(category, equip_name, P, D=None, pressure_side="shell"):
    """Obtiene el factor de presión para un equipo dado."""
    method = COST_METHOD.get(category, "")

    if method == "vessel":
        if D is None:
            D = 1.0
        return calc_fp_vessel(P, D)

    if category in PRESSURE_FACTORS and equip_name in PRESSURE_FACTORS[category]:
        pf_list = PRESSURE_FACTORS[category][equip_name]

        if equip_name in HX_WITH_SIDES:
            for pf in pf_list:
                if pf.get("side") == pressure_side:
                    pmin, pmax = pf["range"]
                    if pmin <= P <= pmax:
                        return calc_fp_equation(pf["C1"], pf["C2"], pf["C3"], P)
            return 1.0

        for pf in pf_list:
            if "side" not in pf:
                pmin, pmax = pf["range"]
                if pmin <= P <= pmax:
                    return calc_fp_equation(pf["C1"], pf["C2"], pf["C3"], P)

        return 1.0

    return 1.0


def get_materials_list(category, equip_name):
    """Retorna la lista de materiales disponibles para un equipo."""
    method = COST_METHOD[category]
    if method in ("B1B2", "vessel"):
        fm_table = FM_MAP.get(category, {}).get(equip_name, {})
        return list(fm_table.keys()) if fm_table else ["CS"]
    elif method in ("FBM", "FBM_FP", "tray"):
        fbm_table = FBM_FIXED.get(category, {}).get(equip_name, {})
        return list(fbm_table.keys()) if fbm_table else ["Default"]
    return ["Default"]


def calc_cost(category, equip_name, A, material, P, D, N, cepci_year,
              pressure_side="shell"):
    """Calcula el costo de módulo desnudo (CBM) actualizado."""
    equip_data = EQUIPMENT[category][equip_name]
    K1, K2, K3 = equip_data["K1"], equip_data["K2"], equip_data["K3"]

    Cp0 = calc_cp0(K1, K2, K3, A)

    method = COST_METHOD[category]
    FP = 1.0
    FM = 1.0
    FBM = 1.0
    Fq = 1.0

    if method == "B1B2":
        b = B1B2[category][equip_name]
        B1, B2 = b["B1"], b["B2"]
        fm_table = FM_MAP.get(category, {}).get(equip_name, {})
        FM = fm_table.get(material, 1.0)
        FP = get_fp(category, equip_name, P, pressure_side=pressure_side)
        FBM = B1 + B2 * FM * FP
        CBM = Cp0 * FBM

    elif method == "vessel":
        b = B1B2[category][equip_name]
        B1, B2 = b["B1"], b["B2"]
        fm_table = FM_MAP.get(category, {}).get(equip_name, {})
        FM = fm_table.get(material, 1.0)
        FP = calc_fp_vessel(P, D)
        FBM = B1 + B2 * FM * FP
        CBM = Cp0 * FBM

    elif method == "FBM":
        fbm_table = FBM_FIXED.get(category, {}).get(equip_name, {})
        FBM = fbm_table.get(material, list(fbm_table.values())[0] if fbm_table else 1.0)
        CBM = Cp0 * FBM

    elif method == "FBM_FP":
        fbm_table = FBM_FIXED.get(category, {}).get(equip_name, {})
        FBM = fbm_table.get(material, list(fbm_table.values())[0] if fbm_table else 1.0)
        FP = get_fp(category, equip_name, P)
        CBM = Cp0 * FBM * FP

    elif method == "tray":
        fbm_table = FBM_FIXED.get(category, {}).get(equip_name, {})
        FBM = fbm_table.get(material, list(fbm_table.values())[0] if fbm_table else 1.0)
        Fq = calc_fq(N)
        CBM = Cp0 * N * FBM * Fq

    else:
        CBM = Cp0

    cepci_target = CEPCI.get(cepci_year, CEPCI_BASE)
    CBM_updated = CBM * (cepci_target / CEPCI_BASE)

    return {
        "Cp0": Cp0,
        "FM": FM,
        "FP": FP,
        "FBM": FBM,
        "Fq": Fq,
        "N": N,
        "CBM_base": CBM,
        "CEPCI_base": CEPCI_BASE,
        "CEPCI_target": cepci_target,
        "CBM_updated": CBM_updated,
        "method": method,
    }


def cost_evolution(category, equip_name, A, material, P, D, N,
                   pressure_side="shell"):
    """Calcula la evolución del costo a través de los años."""
    years = sorted(CEPCI.keys())
    costs = []
    for year in years:
        result = calc_cost(category, equip_name, A, material, P, D, N, year,
                           pressure_side=pressure_side)
        costs.append(result["CBM_updated"])
    return years, costs


# ============================================================
# Configuración de página
# ============================================================

st.set_page_config(
    page_title="COSTIQ — Costeo de Equipos",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS ---
st.markdown("""
<style>
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.7rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .main-header .subtitle {
        color: #a8d0e6;
        margin: 0.25rem 0 0 0;
        font-size: 0.88rem;
    }
    .main-header .badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
        color: #d5e8f0;
        margin-top: 0.5rem;
        letter-spacing: 0.03em;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 18px;
        transition: border-color 0.3s;
    }
    [data-testid="stMetric"]:hover {
        border-color: #2e86c1;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem;
        color: #8b949e;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.25rem;
        font-weight: 600;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0e14;
    }
    [data-testid="stSidebar"] hr {
        border-color: #1e3a5f;
    }

    /* Section labels */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #2e86c1;
        margin-bottom: 0.3rem;
    }

    /* Total plant card */
    .total-card {
        background: linear-gradient(135deg, #1a3a2a 0%, #0d2818 100%);
        border: 2px solid #27ae60;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.8rem 0;
        text-align: center;
    }
    .total-card h3 {
        color: #27ae60;
        margin: 0 0 0.3rem 0;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .total-card .amount {
        color: #2ecc71;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    .total-card .sub {
        color: #7dcea0;
        font-size: 0.8rem;
        margin: 0.2rem 0 0 0;
    }

    /* Equipment list item */
    .equip-item {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .equip-item .name {
        font-size: 0.85rem;
        color: #c9d1d9;
    }
    .equip-item .cost {
        font-size: 0.9rem;
        font-weight: 600;
        color: #2e86c1;
    }

    /* Credits */
    .credits {
        text-align: center;
        color: #6e7681;
        font-size: 0.75rem;
        margin-top: 0.5rem;
        padding-top: 0.8rem;
        border-top: 1px solid #21262d;
        line-height: 1.7;
    }
    .credits a {
        color: #2e86c1;
        text-decoration: none;
    }
    .credits a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>⚙️ COSTIQ — Costeo de Equipos de Proceso</h1>
    <p class="subtitle">
        Estimación de costos de módulo desnudo (C<sub>BM</sub>) y grassroots (C<sub>GR</sub>)
        basada en Turton et al. (2018) — Apéndice A
    </p>
    <span class="badge">CEPCI base = 397 · Sept. 2001 · 5ª Edición</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# Inicializar inventario de equipos en session_state
# ============================================================
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []
if "next_equip_id" not in st.session_state:
    st.session_state.next_equip_id = 1

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown('<p class="section-label">Configuración del equipo</p>',
                unsafe_allow_html=True)

    category = st.selectbox("Categoría", list(EQUIPMENT.keys()),
                            help="Tipo de equipo según Turton et al.")
    equip_name = st.selectbox("Tipo de equipo", list(EQUIPMENT[category].keys()))

    equip_data = EQUIPMENT[category][equip_name]

    st.markdown("---")
    st.markdown(f"**Parámetro:** {equip_data['units']}")
    st.markdown(f"**Rango válido:** {equip_data['min']:g} – {equip_data['max']:g}")

    A = st.number_input(
        f"Capacidad ({equip_data['units']})",
        min_value=float(equip_data["min"]),
        max_value=float(equip_data["max"]),
        value=float(equip_data["min"]),
        format="%.4f",
    )

    # Material
    materials = get_materials_list(category, equip_name)
    material = st.selectbox("Material de construcción", materials)

    st.markdown("---")
    st.markdown('<p class="section-label">Condiciones de operación</p>',
                unsafe_allow_html=True)

    # Presión
    method = COST_METHOD[category]
    needs_pressure = method in ("B1B2", "vessel", "FBM_FP")
    if needs_pressure and (
        (category in PRESSURE_FACTORS and equip_name in PRESSURE_FACTORS.get(category, {}))
        or method == "vessel"
    ):
        P = st.number_input("Presión de operación (barg)", value=0.0, format="%.2f")
    else:
        P = 0.0

    # Selección shell/tube
    pressure_side = "shell"
    if (category == "Intercambiadores de calor" and equip_name in HX_WITH_SIDES
            and needs_pressure):
        pressure_side = st.radio(
            "Lado de la presión",
            options=["shell", "tube"],
            horizontal=True,
            help="Lado del intercambiador donde se aplica la presión de diseño",
        )

    # Diámetro
    if method == "vessel":
        D = st.number_input(
            "Diámetro del recipiente (m)", value=1.0, min_value=0.1, format="%.2f"
        )
    else:
        D = 1.0

    # Número de platos
    if method == "tray":
        N = st.number_input("Número de platos", value=10, min_value=1, max_value=500)
    else:
        N = 1

    st.markdown("---")
    st.markdown('<p class="section-label">Actualización temporal</p>',
                unsafe_allow_html=True)

    cepci_year = st.selectbox(
        "Año CEPCI", sorted(CEPCI.keys(), reverse=True)
    )

    # Tipo de cambio
    st.markdown("---")
    st.markdown('<p class="section-label">Moneda</p>', unsafe_allow_html=True)
    show_mxn = st.toggle("Mostrar en MXN", value=False,
                         help="Convierte los costos usando el tipo de cambio indicado")
    if show_mxn:
        tc_mxn = st.number_input("Tipo de cambio (MXN/USD)", value=17.50,
                                 min_value=1.0, max_value=50.0, format="%.2f")
    else:
        tc_mxn = 1.0

    # Contingency y fees para Grassroots
    st.markdown("---")
    st.markdown('<p class="section-label">Costo Grassroots</p>', unsafe_allow_html=True)
    with st.expander("Factores de contingencia", expanded=False):
        st.caption("C_GR = C_BM × (1 + f₁ + f₂)")
        f_contingency = st.slider("Contingencia (f₁)", 0.0, 0.5, 0.15, 0.01,
                                  help="Típicamente 15%")
        f_fees = st.slider("Honorarios (f₂)", 0.0, 0.3, 0.03, 0.01,
                           help="Típicamente 3%")

    # Instrucciones
    with st.expander("📖 Instrucciones"):
        st.markdown("""
1. **Seleccione** la categoría y tipo de equipo.
2. **Ingrese** la capacidad dentro del rango válido.
3. **Elija** el material de construcción.
4. Si aplica, ingrese la **presión** (barg) y el **lado** (shell/tube).
5. Para recipientes/torres, ingrese el **diámetro** (m).
6. Para platos, indique el **número** de platos.
7. Seleccione el **año CEPCI**.
8. Use **"Agregar al inventario"** para costear múltiples equipos.

**Ecuaciones principales:**
- *Eq. A.1:* Costo base Cp° con K₁, K₂, K₃
- *Eq. A.2:* Factor de presión FP (recipientes, ASME)
- *Eq. A.3:* Factor de presión FP (otros equipos)
- *Eq. A.4:* Costo de módulo desnudo CBM
""")

# ============================================================
# Cálculo principal
# ============================================================
result = calc_cost(category, equip_name, A, material, P, D, N, cepci_year,
                   pressure_side=pressure_side)

# Advertencia si la presión está fuera de rango
if needs_pressure and P != 0.0 and result["FP"] == 1.0:
    if method == "vessel" and P > 0:
        pass  # vessel siempre calcula FP, no hay rango tabular
    elif category in PRESSURE_FACTORS and equip_name in PRESSURE_FACTORS.get(category, {}):
        pf_list = PRESSURE_FACTORS[category][equip_name]
        in_range = False
        for pf in pf_list:
            pmin, pmax = pf["range"]
            if pmin <= P <= pmax:
                in_range = True
                break
        if not in_range:
            st.warning(f"⚠️ La presión {P:.1f} barg está fuera del rango tabulado "
                       f"para {equip_name}. F_P se asume como 1.0.")

currency = "MXN" if show_mxn else "USD"
fx = tc_mxn if show_mxn else 1.0
CBM_display = result["CBM_updated"] * fx
CGR_display = CBM_display * (1 + f_contingency + f_fees)

# ============================================================
# Layout principal con tabs
# ============================================================
tab_single, tab_inventory, tab_charts, tab_reference = st.tabs([
    "📊 Equipo individual",
    "📋 Inventario de planta",
    "📈 Análisis gráfico",
    "📚 Referencia",
])

# ============================================================
# TAB 1: Equipo individual
# ============================================================
with tab_single:
    col_res, col_eq = st.columns([3, 2])

    with col_res:
        # Metrics row 1
        c1, c2, c3 = st.columns(3)
        cp0_label = "Cp° base (USD, 2001)" if show_mxn else "Cp° base (2001)"
        c1.metric(cp0_label, f"${result['Cp0']:,.0f} USD")
        c2.metric(f"C_BM ({cepci_year})", f"${CBM_display:,.0f} {currency}")
        c3.metric(f"C_GR ({cepci_year})",
                  f"${CGR_display:,.0f} {currency}",
                  help=f"Grassroots = CBM × (1 + {f_contingency:.0%} + {f_fees:.0%})")

        # Metrics row 2
        c4, c5, c6 = st.columns(3)
        c4.metric("F_M (material)", f"{result['FM']:.4f}")
        c5.metric("F_P (presión)", f"{result['FP']:.4f}")
        c6.metric("F_BM (módulo)", f"{result['FBM']:.4f}")

        if result["method"] == "tray":
            c7, c8, c9 = st.columns(3)
            c7.metric("N (platos)", f"{N}")
            c8.metric("F_q (cantidad)", f"{result['Fq']:.4f}")
            c9.metric(f"CEPCI {cepci_year}", f"{result['CEPCI_target']:.1f}")
        else:
            c7, _, _ = st.columns(3)
            c7.metric(f"CEPCI {cepci_year}", f"{result['CEPCI_target']:.1f}")

        # Desglose
        st.markdown("##### Desglose del cálculo")
        K1, K2, K3 = equip_data["K1"], equip_data["K2"], equip_data["K3"]
        breakdown = {
            "Variable": [
                "A (capacidad)", "K₁", "K₂", "K₃",
                "Cp° (USD, 2001)",
                "F_M", "F_P", "F_BM",
            ],
            "Valor": [
                f"{A:,.4f}", f"{K1}", f"{K2}", f"{K3}",
                f"${result['Cp0']:,.2f}",
                f"{result['FM']:.4f}", f"{result['FP']:.4f}", f"{result['FBM']:.4f}",
            ],
        }
        if result["method"] == "tray":
            breakdown["Variable"].extend(["N (platos)", "F_q"])
            breakdown["Valor"].extend([f"{N}", f"{result['Fq']:.4f}"])

        breakdown["Variable"].extend([
            f"C_BM base ({currency}, 2001)",
            f"CEPCI {cepci_year}",
            f"C_BM actualizado ({currency}, {cepci_year})",
            f"C_GR ({currency}, {cepci_year})",
        ])
        breakdown["Valor"].extend([
            f"${result['CBM_base'] * fx:,.2f}",
            f"{result['CEPCI_target']:.1f}",
            f"${CBM_display:,.2f}",
            f"${CGR_display:,.2f}",
        ])

        df_bd = pd.DataFrame(breakdown)
        st.dataframe(df_bd, use_container_width=True, hide_index=True)

        # Botón agregar al inventario
        st.markdown("")
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("➕ Agregar al inventario de planta", use_container_width=True,
                         type="primary"):
                item = {
                    "id": st.session_state.next_equip_id,
                    "category": category,
                    "equip_name": equip_name,
                    "A": A,
                    "units": equip_data["units"],
                    "material": material,
                    "P": P,
                    "D": D,
                    "N": N,
                    "pressure_side": pressure_side,
                    "Fq": result["Fq"],
                }
                st.session_state.next_equip_id += 1
                st.session_state.equipment_list.append(item)
                st.toast(f"✅ {equip_name} agregado al inventario", icon="✅")
                st.rerun()

    with col_eq:
        # Ecuaciones
        st.markdown("##### Ecuaciones utilizadas")

        st.latex(r"\log_{10}(C_p^\circ) = K_1 + K_2 \log_{10}(A) + K_3 [\log_{10}(A)]^2")
        st.caption(f"K₁ = {K1}, K₂ = {K2}, K₃ = {K3}, A = {A:g}")

        if result["method"] == "B1B2":
            b = B1B2[category][equip_name]
            st.latex(r"C_{BM} = C_p^\circ \left(B_1 + B_2 \, F_M \, F_P\right)")
            st.caption(f"B₁ = {b['B1']}, B₂ = {b['B2']}, "
                       f"F_M = {result['FM']:.4f}, F_P = {result['FP']:.4f}")
        elif result["method"] == "vessel":
            b = B1B2[category][equip_name]
            st.latex(
                r"F_P = \frac{\dfrac{P \cdot D}{2\,(850 - 0.6\,P)} + 0.00315}{0.0063}"
            )
            st.latex(r"C_{BM} = C_p^\circ \left(B_1 + B_2 \, F_M \, F_P\right)")
            st.caption(f"B₁ = {b['B1']}, B₂ = {b['B2']}, "
                       f"F_M = {result['FM']:.4f}, F_P = {result['FP']:.4f}")
        elif result["method"] == "FBM":
            st.latex(r"C_{BM} = C_p^\circ \cdot F_{BM}")
            st.caption(f"F_BM = {result['FBM']:.4f}")
        elif result["method"] == "FBM_FP":
            st.latex(r"C_{BM} = C_p^\circ \cdot F_{BM} \cdot F_P")
            st.caption(f"F_BM = {result['FBM']:.4f}, F_P = {result['FP']:.4f}")
        elif result["method"] == "tray":
            st.latex(r"C_{BM} = C_p^\circ \cdot N \cdot F_{BM} \cdot F_q")
            st.caption(f"N = {N}, F_BM = {result['FBM']:.4f}, F_q = {result['Fq']:.4f}")

        cepci_val = result["CEPCI_target"]
        st.latex(
            r"C_{actualizado} = C_{BM} \times "
            r"\frac{CEPCI_{" + str(cepci_year) + r"}}{CEPCI_{2001}} = "
            r"C_{BM} \times \frac{" + f"{cepci_val:.1f}" + r"}{397}"
        )

        st.latex(
            r"C_{GR} = C_{BM} \times (1 + f_1 + f_2)"
        )
        st.caption(f"f₁ = {f_contingency:.2f} (contingencia), f₂ = {f_fees:.2f} (honorarios)")

        # Material comparison mini-chart
        st.markdown("##### Comparación por material")
        mat_list = get_materials_list(category, equip_name)
        if len(mat_list) > 1:
            mat_costs = []
            mat_names = []
            for m in mat_list:
                r = calc_cost(category, equip_name, A, m, P, D, N, cepci_year,
                              pressure_side=pressure_side)
                mat_costs.append(r["CBM_updated"] * fx)
                mat_names.append(m)

            colors = ["#2e86c1" if m != material else "#e74c3c" for m in mat_names]
            fig_mat = go.Figure(go.Bar(
                x=mat_names, y=mat_costs,
                marker_color=colors,
                text=[f"${c:,.0f}" for c in mat_costs],
                textposition="outside",
                textfont=dict(size=10),
            ))
            fig_mat.update_layout(
                yaxis_title=f"C_BM ({currency})",
                template="plotly_dark",
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(size=10),
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_mat, use_container_width=True)
        else:
            st.info("Solo un material disponible para este equipo.")


# ============================================================
# TAB 2: Inventario de planta
# ============================================================
with tab_inventory:
    if not st.session_state.equipment_list:
        st.info("El inventario está vacío. Usa el botón **'Agregar al inventario'** "
                "en la pestaña de equipo individual para comenzar a costear tu planta.")
    else:
        equip_list = st.session_state.equipment_list

        # Recalcular todos los costos dinámicamente con el CEPCI year actual
        inv_results = []
        for e in equip_list:
            r = calc_cost(
                e["category"], e["equip_name"], e["A"], e["material"],
                e["P"], e["D"], e["N"], cepci_year,
                pressure_side=e.get("pressure_side", "shell"),
            )
            cbm = r["CBM_updated"]
            cgr = cbm * (1 + f_contingency + f_fees)
            inv_results.append({
                **e,
                "Cp0": r["Cp0"],
                "FM": r["FM"],
                "FP": r["FP"],
                "FBM": r["FBM"],
                "Fq": r["Fq"],
                "CBM": cbm,
                "CGR": cgr,
            })

        # Totales
        total_cbm = sum(ir["CBM"] for ir in inv_results) * fx
        total_cgr = sum(ir["CGR"] for ir in inv_results) * fx

        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.markdown(f"""
            <div class="total-card">
                <h3>Costo Total C_BM</h3>
                <p class="amount">${total_cbm:,.0f} {currency}</p>
                <p class="sub">{len(equip_list)} equipo(s) · CEPCI {cepci_year}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"""
            <div class="total-card" style="border-color: #2980b9;
                background: linear-gradient(135deg, #1a2a3a 0%, #0d1828 100%);">
                <h3 style="color: #2980b9;">Costo Grassroots C_GR</h3>
                <p class="amount" style="color: #3498db;">${total_cgr:,.0f} {currency}</p>
                <p class="sub" style="color: #7db8d4;">
                    Contingencia {f_contingency:.0%} + Honorarios {f_fees:.0%}
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_t3:
            if show_mxn and fx != 1.0:
                st.markdown(f"""
                <div class="total-card" style="border-color: #8e44ad;
                    background: linear-gradient(135deg, #2a1a3a 0%, #180d28 100%);">
                    <h3 style="color: #8e44ad;">Equivalente USD</h3>
                    <p class="amount" style="color: #9b59b6;">
                        ${total_cgr / fx:,.0f} USD
                    </p>
                    <p class="sub" style="color: #bb8fce;">TC: {tc_mxn:.2f} MXN/USD</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                n_cats = len(set(e["category"] for e in equip_list))
                st.markdown(f"""
                <div class="total-card" style="border-color: #8e44ad;
                    background: linear-gradient(135deg, #2a1a3a 0%, #180d28 100%);">
                    <h3 style="color: #8e44ad;">Resumen</h3>
                    <p class="amount" style="color: #9b59b6;">{len(equip_list)} equipos</p>
                    <p class="sub" style="color: #bb8fce;">{n_cats} categoría(s)</p>
                </div>
                """, unsafe_allow_html=True)

        # Tabla de inventario con botón de eliminar por equipo
        st.markdown("##### Lista de equipos")
        for idx, ir in enumerate(inv_results):
            col_id, col_cat, col_eq, col_cap, col_mat, col_cbm, col_cgr, col_del = \
                st.columns([0.4, 1.2, 1.2, 1.0, 0.8, 1.0, 1.0, 0.5])
            col_id.markdown(f"**{ir['id']}**")
            col_cat.markdown(f"{ir['category']}")
            col_eq.markdown(f"{ir['equip_name']}")
            col_cap.markdown(f"{ir['A']:,.2f} {ir['units']}")
            col_mat.markdown(f"{ir['material']}")
            col_cbm.markdown(f"${ir['CBM'] * fx:,.0f}")
            col_cgr.markdown(f"${ir['CGR'] * fx:,.0f}")
            if col_del.button("❌", key=f"del_{ir['id']}",
                              help=f"Eliminar {ir['equip_name']}"):
                st.session_state.equipment_list.pop(idx)
                st.rerun()

        # Gráfica de distribución de costos
        st.markdown("##### Distribución de costos por equipo")
        fig_dist = go.Figure(go.Pie(
            labels=[f"{ir['equip_name']} ({ir['material']})" for ir in inv_results],
            values=[ir["CBM"] * fx for ir in inv_results],
            hole=0.45,
            textinfo="label+percent",
            textposition="outside",
            marker=dict(
                colors=[
                    "#2e86c1", "#e67e22", "#27ae60", "#e74c3c", "#8e44ad",
                    "#1abc9c", "#f39c12", "#3498db", "#e91e63", "#00bcd4",
                ] * 5  # cycle colors
            ),
        ))
        fig_dist.update_layout(
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(size=11),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        # Botones de acción
        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            # Exportar a CSV — recalculado dinámicamente
            csv_data = pd.DataFrame([
                {
                    "ID": ir["id"],
                    "Categoría": ir["category"],
                    "Equipo": ir["equip_name"],
                    "Capacidad": ir["A"],
                    "Unidades": ir["units"],
                    "Material": ir["material"],
                    "P (barg)": ir["P"],
                    "D (m)": ir["D"],
                    "N (platos)": ir["N"],
                    "CEPCI año": cepci_year,
                    "Cp0 (USD)": round(ir["Cp0"], 2),
                    "FM": round(ir["FM"], 4),
                    "FP": round(ir["FP"], 4),
                    "FBM": round(ir["FBM"], 4),
                    "Fq": round(ir["Fq"], 4),
                    "CBM (USD)": round(ir["CBM"], 2),
                    "CGR (USD)": round(ir["CGR"], 2),
                    "f_contingencia": f_contingency,
                    "f_honorarios": f_fees,
                }
                for ir in inv_results
            ])
            csv_bytes = csv_data.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Descargar CSV",
                data=csv_bytes,
                file_name=f"costeo_equipos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_b:
            if st.button("🗑️ Eliminar último", use_container_width=True):
                if st.session_state.equipment_list:
                    st.session_state.equipment_list.pop()
                    st.rerun()
        with col_c:
            if st.button("🧹 Limpiar inventario", use_container_width=True):
                st.session_state.equipment_list = []
                st.rerun()


# ============================================================
# TAB 3: Análisis gráfico
# ============================================================
with tab_charts:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Evolución temporal
        st.markdown("##### Evolución temporal del costo")
        years, costs = cost_evolution(
            category, equip_name, A, material, P, D, N,
            pressure_side=pressure_side,
        )
        costs_display = [c * fx for c in costs]

        fig_evo = go.Figure()
        fig_evo.add_trace(go.Scatter(
            x=years, y=costs_display,
            mode="lines+markers",
            name="C_BM",
            line=dict(color="#2e86c1", width=2.5),
            marker=dict(size=4),
            fill="tozeroy",
            fillcolor="rgba(46, 134, 193, 0.08)",
        ))
        fig_evo.add_trace(go.Scatter(
            x=[cepci_year], y=[CBM_display],
            mode="markers",
            name=f"Año {cepci_year}",
            marker=dict(color="#e74c3c", size=14, symbol="diamond",
                        line=dict(width=2, color="white")),
        ))
        fig_evo.update_layout(
            xaxis_title="Año",
            yaxis_title=f"C_BM ({currency})",
            template="plotly_dark",
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(size=11),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_evo, use_container_width=True)

    with chart_col2:
        # Sensibilidad al tamaño
        st.markdown("##### Sensibilidad al tamaño (capacidad)")
        A_min = equip_data["min"]
        A_max = equip_data["max"]
        n_points = 60
        if A_max / A_min > 100:
            A_values = [A_min * (A_max / A_min) ** (i / (n_points - 1))
                        for i in range(n_points)]
        else:
            step = (A_max - A_min) / (n_points - 1)
            A_values = [A_min + i * step for i in range(n_points)]

        costs_sens = []
        for a_val in A_values:
            r = calc_cost(category, equip_name, a_val, material, P, D, N, cepci_year,
                          pressure_side=pressure_side)
            costs_sens.append(r["CBM_updated"] * fx)

        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(
            x=A_values, y=costs_sens,
            mode="lines",
            name="C_BM vs Capacidad",
            line=dict(color="#e67e22", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(230, 126, 34, 0.08)",
        ))
        fig_sens.add_trace(go.Scatter(
            x=[A], y=[CBM_display],
            mode="markers",
            name="Punto actual",
            marker=dict(color="#e74c3c", size=14, symbol="star",
                        line=dict(width=2, color="white")),
        ))
        fig_sens.update_layout(
            xaxis_title=equip_data["units"],
            yaxis_title=f"C_BM ({currency})",
            template="plotly_dark",
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(size=11),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        if A_max / A_min > 100:
            fig_sens.update_xaxes(type="log")
        st.plotly_chart(fig_sens, use_container_width=True)

    # Sensibilidad a presión (solo si aplica)
    if needs_pressure and (
        (category in PRESSURE_FACTORS and equip_name in PRESSURE_FACTORS.get(category, {}))
        or method == "vessel"
    ):
        st.markdown("##### Sensibilidad a la presión")

        # Determine pressure range (incluyendo P=0)
        if method == "vessel":
            P_values = [0.0] + [i * 2 for i in range(1, 76)]  # 0 to 150 barg
        elif category in PRESSURE_FACTORS and equip_name in PRESSURE_FACTORS[category]:
            pf_list = PRESSURE_FACTORS[category][equip_name]
            p_max = max(pf["range"][1] for pf in pf_list)
            P_values = [0.0] + [i * p_max / 60 for i in range(1, 61)]
        else:
            P_values = [float(i) for i in range(0, 101)]

        costs_p = []
        fps = []
        for p_val in P_values:
            r = calc_cost(category, equip_name, A, material, p_val, D, N, cepci_year,
                          pressure_side=pressure_side)
            costs_p.append(r["CBM_updated"] * fx)
            fps.append(r["FP"])

        fig_p = make_subplots(specs=[[{"secondary_y": True}]])
        fig_p.add_trace(go.Scatter(
            x=P_values, y=costs_p,
            mode="lines",
            name=f"C_BM ({currency})",
            line=dict(color="#27ae60", width=2.5),
        ), secondary_y=False)
        fig_p.add_trace(go.Scatter(
            x=P_values, y=fps,
            mode="lines",
            name="F_P",
            line=dict(color="#8e44ad", width=2, dash="dash"),
        ), secondary_y=True)
        # Current point
        fig_p.add_trace(go.Scatter(
            x=[P], y=[CBM_display],
            mode="markers",
            name="Presión actual",
            marker=dict(color="#e74c3c", size=14, symbol="diamond",
                        line=dict(width=2, color="white")),
        ), secondary_y=False)
        fig_p.update_layout(
            xaxis_title="Presión (barg)",
            template="plotly_dark",
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(size=11),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_p.update_yaxes(title_text=f"C_BM ({currency})", secondary_y=False)
        fig_p.update_yaxes(title_text="F_P", secondary_y=True)
        st.plotly_chart(fig_p, use_container_width=True)


# ============================================================
# TAB 4: Referencia
# ============================================================
with tab_reference:
    ref_col1, ref_col2 = st.columns(2)

    with ref_col1:
        st.markdown("##### Índices CEPCI (2001–2024)")
        cepci_df = pd.DataFrame({
            "Año": list(CEPCI.keys()),
            "CEPCI": list(CEPCI.values()),
            "Ratio vs 2001": [v / CEPCI_BASE for v in CEPCI.values()],
        })
        st.dataframe(cepci_df, use_container_width=True, hide_index=True)

        # CEPCI chart
        fig_cepci = go.Figure()
        fig_cepci.add_trace(go.Bar(
            x=list(CEPCI.keys()),
            y=list(CEPCI.values()),
            marker_color=["#2e86c1" if y != cepci_year else "#e74c3c"
                          for y in CEPCI.keys()],
        ))
        fig_cepci.update_layout(
            xaxis_title="Año",
            yaxis_title="CEPCI",
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_cepci, use_container_width=True)

    with ref_col2:
        st.markdown("##### Catálogo de equipos disponibles")
        equip_count = []
        for cat, equips in EQUIPMENT.items():
            for eq_name, eq_data in equips.items():
                equip_count.append({
                    "Categoría": cat,
                    "Equipo": eq_name,
                    "Unidades": eq_data["units"],
                    "Mín": eq_data["min"],
                    "Máx": eq_data["max"],
                    "Método": COST_METHOD[cat],
                })
        df_catalog = pd.DataFrame(equip_count)
        st.dataframe(df_catalog, use_container_width=True, hide_index=True, height=400)

        st.markdown("##### Métodos de costeo")
        st.markdown("""
| Método | Ecuación | Aplica a |
|--------|----------|----------|
| **B1B2** | C_BM = Cp° × (B₁ + B₂·F_M·F_P) | HX, Bombas |
| **vessel** | F_P por Eq. A.2 + B1B2 | Torres, Recipientes |
| **FBM** | C_BM = Cp° × F_BM | Compresores, Turbinas, Reactores, Tanques |
| **FBM_FP** | C_BM = Cp° × F_BM × F_P | Hornos |
| **tray** | C_BM = Cp° × N × F_BM × F_q | Platos |
""")

        st.markdown("##### Referencia bibliográfica")
        st.info(
            "Turton, R., Shaeiwitz, J.A., Bhattacharyya, D., Whiting, W.B. "
            "*Analysis, Synthesis, and Design of Chemical Processes*, 5th Ed. "
            "Prentice Hall, 2018. **Apéndice A.**"
        )


# ============================================================
# Pie de página
# ============================================================
st.markdown("---")
st.markdown("""
<div class="credits">
    <strong>COSTIQ — Costeo de Equipos de Proceso</strong><br>
    Desarrollado por:
    Oscar Daniel Lara-Montaño ·
    Fernando Israel Gómez-Castro ·
    Sergio Iván Martínez-Guido<br>
    Universidad Autónoma de Querétaro · Universidad de Guanajuato<br><br>
    <em>Si encuentra algún error o bug, por favor repórtelo en
    <a href="https://github.com/lara-montano/estimador_costos/issues">
    github.com/lara-montano/estimador_costos/issues</a></em>
</div>
""", unsafe_allow_html=True)
