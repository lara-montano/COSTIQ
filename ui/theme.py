"""Estilos, formato numérico y componentes HTML de la interfaz de COSTIQ."""

from __future__ import annotations

import html
import math

import streamlit as st

# Tokens de color. Deben coincidir con .streamlit/config.toml y ui/charts.py.
INK = "#16191d"
INK_2 = "#4a4f57"
MUTED = "#7d7b75"
LINE = "#e2dfd7"
SURFACE = "#fcfcfb"
PRIMARY = "#1c5cab"

_CSS = f"""
<style>
:root {{
  --cq-ink: {INK};
  --cq-ink-2: {INK_2};
  --cq-muted: {MUTED};
  --cq-line: {LINE};
  --cq-surface: {SURFACE};
  --cq-primary: {PRIMARY};
  --cq-primary-soft: #e9f0fa;
}}

.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1360px; }}
header[data-testid="stHeader"] {{ background: transparent; }}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.4rem; }}

/* Pestañas */
div[data-baseweb="tab-list"] {{ gap: 0.25rem; border-bottom: 1px solid var(--cq-line); }}
button[data-baseweb="tab"] {{ padding: 0.55rem 0.9rem; }}
button[data-baseweb="tab"] p {{ font-size: 0.95rem; font-weight: 500; }}

/* Encabezado */
.cq-header {{ display: flex; align-items: center; justify-content: space-between;
  gap: 1rem; flex-wrap: wrap; margin-bottom: 0.4rem; }}
.cq-brand {{ display: flex; align-items: center; gap: 0.85rem; }}
.cq-brand svg {{ flex: none; }}
.cq-title {{ font-size: 1.45rem; font-weight: 650; letter-spacing: -0.01em;
  color: var(--cq-ink); line-height: 1.15; margin: 0; }}
.cq-subtitle {{ color: var(--cq-ink-2); font-size: 0.9rem; margin: 0.1rem 0 0 0; }}
.cq-chips {{ display: flex; gap: 0.4rem; flex-wrap: wrap; }}
.cq-chip {{ font-size: 0.78rem; color: var(--cq-ink-2); background: var(--cq-surface);
  border: 1px solid var(--cq-line); border-radius: 999px; padding: 0.22rem 0.7rem;
  white-space: nowrap; }}
.cq-chip b {{ color: var(--cq-ink); font-weight: 600; }}

/* Etiquetas de sección */
.cq-eyebrow {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--cq-muted); margin: 0.2rem 0 0.35rem 0; }}
.cq-section {{ font-size: 1.02rem; font-weight: 600; color: var(--cq-ink);
  margin: 1.4rem 0 0.15rem 0; }}
.cq-section-sub {{ font-size: 0.85rem; color: var(--cq-ink-2); margin: 0 0 0.4rem 0; }}

/* Cifra principal */
.cq-hero {{ background: var(--cq-surface); border: 1px solid var(--cq-line);
  border-radius: 14px; padding: 1.3rem 1.5rem 1.1rem 1.5rem; }}
.cq-hero-value {{ font-size: 2.55rem; font-weight: 600; letter-spacing: -0.02em;
  color: var(--cq-ink); line-height: 1.1; margin-top: 0.15rem; }}
.cq-hero-value .cur {{ font-size: 1rem; font-weight: 500; color: var(--cq-muted);
  margin-left: 0.4rem; letter-spacing: 0; }}
.cq-hero-sub {{ color: var(--cq-ink-2); font-size: 0.9rem; margin-top: 0.35rem; }}
.cq-factors {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.6rem 0.8rem; margin-top: 1.05rem; padding-top: 0.95rem;
  border-top: 1px solid var(--cq-line); }}
.cq-factor .k {{ font-size: 0.74rem; color: var(--cq-muted); line-height: 1.3;
  min-height: 1.95em; }}
.cq-factor .v {{ font-size: 1.02rem; font-weight: 600; color: var(--cq-ink);
  font-variant-numeric: tabular-nums; white-space: nowrap; }}

/* Tarjetas de totales de planta */
.cq-kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem; }}
.cq-kpi {{ background: var(--cq-surface); border: 1px solid var(--cq-line);
  border-radius: 14px; padding: 1rem 1.2rem; }}
.cq-kpi.main {{ border-color: var(--cq-primary); box-shadow: inset 0 0 0 1px var(--cq-primary); }}
.cq-kpi .k {{ font-size: 0.82rem; color: var(--cq-ink-2); }}
.cq-kpi .v {{ font-size: 1.7rem; font-weight: 600; color: var(--cq-ink);
  letter-spacing: -0.015em; margin-top: 0.15rem; line-height: 1.15; }}
.cq-kpi .v .cur {{ font-size: 0.85rem; color: var(--cq-muted); font-weight: 500; margin-left: 0.3rem; }}
.cq-kpi .d {{ font-size: 0.78rem; color: var(--cq-muted); margin-top: 0.25rem; }}

/* Notas */
.cq-note {{ display: flex; gap: 0.5rem; align-items: flex-start; font-size: 0.84rem;
  color: var(--cq-ink-2); margin: 0.35rem 0; }}
.cq-note .i {{ color: var(--cq-muted); font-weight: 600; flex: none; }}

/* Estado vacío */
.cq-empty {{ text-align: center; padding: 2.2rem 1rem 1rem 1rem; }}
.cq-empty h3 {{ font-size: 1.15rem; font-weight: 600; margin: 0.8rem 0 0.3rem 0; color: var(--cq-ink); }}
.cq-empty p {{ color: var(--cq-ink-2); font-size: 0.92rem; max-width: 520px; margin: 0 auto; }}

/* Pie */
.cq-footer {{ margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid var(--cq-line);
  font-size: 0.8rem; color: var(--cq-muted); line-height: 1.7; }}
.cq-footer a {{ color: var(--cq-primary); text-decoration: none; }}
.cq-footer a:hover {{ text-decoration: underline; }}

/* Tablas markdown de la pestaña Referencia */
.cq-ref table {{ font-size: 0.86rem; }}
</style>
"""

_LOGO = f"""
<svg width="42" height="42" viewBox="0 0 42 42" aria-hidden="true">
  <rect width="42" height="42" rx="10" fill="{PRIMARY}"/>
  <path d="M11 27.5a10 10 0 1 1 20 0" fill="none" stroke="#fff" stroke-width="2.4"
        stroke-linecap="round"/>
  <path d="M21 27.5 27 18.5" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>
  <circle cx="21" cy="27.5" r="2.6" fill="#fff"/>
  <path d="M13.5 31.5h15" stroke="#9ec5f4" stroke-width="2" stroke-linecap="round"/>
</svg>
"""


def inject() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)  # CSS: la sangría no importa


def _html(markup: str) -> None:
    """Inserta HTML sin sangría (Markdown trata 4 espacios como bloque de código)."""
    flat = "\n".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(flat, unsafe_allow_html=True)


def esc(text: object) -> str:
    # "$" se escapa para que Streamlit no lo interprete como LaTeX.
    return html.escape(str(text)).replace("$", "&#36;")


# ---------------------------------------------------------------------------
# Formato numérico
# ---------------------------------------------------------------------------

def money(value_usd: float, fx: float = 1.0) -> str:
    return f"${value_usd * fx:,.0f}"


def money_short(value_usd: float, fx: float = 1.0) -> str:
    v = value_usd * fx
    a = abs(v)
    if a >= 1e9:
        return f"${v / 1e9:,.2f} B"
    if a >= 1e6:
        return f"${v / 1e6:,.2f} M"
    if a >= 1e4:
        return f"${v / 1e3:,.0f} k"
    return f"${v:,.0f}"


def num(x: float, digits: int = 4) -> str:
    """Número con cifras significativas y separador de miles."""
    if x == 0 or not math.isfinite(x):
        return f"{x:g}"
    mag = math.floor(math.log10(abs(x)))
    decimals = max(0, digits - 1 - mag)
    return f"{x:,.{decimals}f}"


def nice_default(a_min: float, a_max: float) -> float:
    """Valor inicial representativo dentro del rango (1, 2 o 5 × 10^n)."""
    gm = math.sqrt(a_min * a_max)
    exp = math.floor(math.log10(gm))
    for m in (1, 2, 5, 10):
        if m * 10 ** exp >= gm:
            return float(min(max(m * 10 ** exp, a_min), a_max))
    return float(gm)


# ---------------------------------------------------------------------------
# Componentes
# ---------------------------------------------------------------------------

def header(cepci_text: str, n_items: int) -> None:
    _html(
        f"""
<div class="cq-header">
  <div class="cq-brand">{_LOGO}
    <div>
      <p class="cq-title">COSTIQ</p>
      <p class="cq-subtitle">Costeo de equipo de proceso por el método de módulo · Turton et al. (2018)</p>
    </div>
  </div>
  <div class="cq-chips">
    <span class="cq-chip">CEPCI <b>{esc(cepci_text)}</b></span>
    <span class="cq-chip">Planta <b>{n_items}</b> equipo{'s' if n_items != 1 else ''}</span>
  </div>
</div>
""")


def eyebrow(text: str) -> None:
    _html(f'<p class="cq-eyebrow">{esc(text)}</p>')


def section(title: str, subtitle: str | None = None) -> None:
    sub = f'<p class="cq-section-sub">{esc(subtitle)}</p>' if subtitle else ""
    _html(f'<p class="cq-section">{esc(title)}</p>{sub}')


def hero(label_html: str, value: str, currency: str, sub: str,
         factors: list[tuple[str, str]]) -> None:
    chips = "".join(
        f'<div class="cq-factor"><div class="k">{k}</div><div class="v">{esc(v)}</div></div>'
        for k, v in factors
    )
    _html(
        f"""
<div class="cq-hero">
  <div class="cq-eyebrow">{label_html}</div>
  <div class="cq-hero-value">{esc(value)}<span class="cur">{esc(currency)}</span></div>
  <div class="cq-hero-sub">{esc(sub)}</div>
  <div class="cq-factors">{chips}</div>
</div>
""")


def kpis(cards: list[dict]) -> None:
    body = "".join(
        f"""<div class="cq-kpi{' main' if c.get('main') else ''}">
  <div class="k">{c['label']}</div>
  <div class="v">{esc(c['value'])}<span class="cur">{esc(c['currency'])}</span></div>
  <div class="d">{c.get('detail', '')}</div>
</div>"""
        for c in cards
    )
    _html(f'<div class="cq-kpis">{body}</div>')


def note(text: str, mark: str = "i") -> None:
    _html(f'<div class="cq-note"><span class="i">{esc(mark)}</span><span>{esc(text)}</span></div>')


def empty_state(title: str, text: str) -> None:
    _html(
        f"""
<div class="cq-empty">
  <svg width="56" height="56" viewBox="0 0 56 56" aria-hidden="true">
    <rect x="1" y="1" width="54" height="54" rx="14" fill="#e9f0fa" stroke="#cde2fb"/>
    <rect x="15" y="30" width="6" height="12" rx="2" fill="#86b6ef"/>
    <rect x="25" y="22" width="6" height="20" rx="2" fill="#3987e5"/>
    <rect x="35" y="14" width="6" height="28" rx="2" fill="{PRIMARY}"/>
  </svg>
  <h3>{esc(title)}</h3>
  <p>{esc(text)}</p>
</div>
""")


def footer(version: str) -> None:
    _html(
        f"""
<div class="cq-footer">
  <b>COSTIQ {esc(version)}</b> · Oscar Daniel Lara-Montaño (Universidad Autónoma de Querétaro),
  Fernando Israel Gómez-Castro y Sergio Iván Martínez-Guido (Universidad de Guanajuato).<br>
  Correlaciones de Turton, Shaeiwitz, Bhattacharyya y Whiting (2018), <i>Analysis, Synthesis,
  and Design of Chemical Processes</i>, 5.ª ed., Apéndice A. Es un estimado preliminar
  de estudio; no sustituye una cotización.<br>
  Código y reporte de errores:
  <a href="https://github.com/lara-montano/COSTIQ/issues" target="_blank">github.com/lara-montano/COSTIQ</a>
</div>
""")
