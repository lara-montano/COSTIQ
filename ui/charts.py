"""Gráficas de COSTIQ (Plotly).

Reglas de diseño: una sola escala vertical por gráfica, marcas delgadas,
retícula tenue, un color por serie y el gris para lo que no es el foco.
La paleta categórica pasó el validador de daltonismo (ΔE ≥ 9 entre vecinos).
"""

from __future__ import annotations

import plotly.graph_objects as go

SERIES_1 = "#2a78d6"   # azul: serie principal
SERIES_2 = "#eb6834"   # naranja
SERIES_3 = "#1baf7a"   # aqua
STRONG = "#184f95"     # azul profundo: totales
QUIET = "#c3c2b7"      # gris: elementos fuera de foco
NEGATIVE = "#898781"   # gris medio: decrementos
SURFACE = "#f8f7f4"
GRID = "#e6e3dc"
AXIS = "#c3c2b7"
INK_2 = "#4a4f57"
MUTED = "#7d7b75"
FONT = "IBM Plex Sans, system-ui, sans-serif"


def _layout(fig: go.Figure, height: int, *, x_title: str = "", y_title: str = "",
            showlegend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=16, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=INK_2),
        showlegend=showlegend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12)),
        hoverlabel=dict(font=dict(family=FONT, size=12), bgcolor="white",
                        bordercolor=GRID),
        barcornerradius=4,
        bargap=0.28,
    )
    fig.update_xaxes(title=dict(text=x_title, font=dict(size=12, color=MUTED)),
                     showgrid=False, linecolor=AXIS, ticks="outside", tickcolor=AXIS,
                     zeroline=False)
    fig.update_yaxes(title=dict(text=y_title, font=dict(size=12, color=MUTED)),
                     gridcolor=GRID, gridwidth=1, zeroline=False, linecolor=AXIS,
                     rangemode="tozero")
    return fig


def waterfall(steps: list[tuple[str, float]], total_label: str, fmt, currency: str
              ) -> go.Figure:
    labels = [s[0] for s in steps] + [total_label]
    values = [s[1] for s in steps]
    total = sum(values)
    fig = go.Figure(go.Waterfall(
        x=labels,
        y=values + [total],
        measure=["relative"] * len(values) + ["total"],
        text=[fmt(v) for v in values] + [fmt(total)],
        textposition="outside",
        textfont=dict(size=12, color=INK_2),
        cliponaxis=False,
        connector=dict(line=dict(color=AXIS, width=1)),
        increasing=dict(marker=dict(color=SERIES_1)),
        decreasing=dict(marker=dict(color=NEGATIVE)),
        totals=dict(marker=dict(color=STRONG)),
        hovertemplate="%{x}<br>%{text} " + currency + "<extra></extra>",
    ))
    _layout(fig, 330, y_title=currency)
    fig.update_yaxes(tickprefix="$", separatethousands=True)
    return fig


def material_bars(names: list[str], values: list[float], selected: str,
                  fmt, currency: str, factor_name: str, factors: list[float]) -> go.Figure:
    colors = [SERIES_1 if n == selected else QUIET for n in names]
    fig = go.Figure(go.Bar(
        x=names, y=values, marker=dict(color=colors, line=dict(width=0)),
        text=[fmt(v) for v in values], textposition="outside",
        textfont=dict(size=11, color=INK_2), cliponaxis=False,
        customdata=factors,
        hovertemplate="%{x}<br>%{text} " + currency + "<br>" + factor_name
                      + " = %{customdata:.2f}<extra></extra>",
    ))
    _layout(fig, 330, y_title=f"C<sub>BM</sub> ({currency})")
    fig.update_yaxes(tickprefix="$", separatethousands=True)
    return fig


def sweep(x: list[float], y: list[float], valid: list[bool], current: tuple[float, float],
          *, x_title: str, y_title: str, log_x: bool, hover_extra: list[str] | None = None,
          current_label: str = "Caso actual") -> go.Figure:
    """Línea de sensibilidad. Tramo válido sólido; extrapolación punteada."""
    fig = go.Figure()
    extra = hover_extra or [""] * len(x)

    def segment(mask_value: bool, name: str, dash: str):
        xs, ys, hs = [], [], []
        for i, (xi, yi, ok) in enumerate(zip(x, y, valid)):
            keep = ok == mask_value or (
                # une los tramos para que la línea sea continua
                (i > 0 and valid[i - 1] == mask_value) or
                (i + 1 < len(x) and valid[i + 1] == mask_value)
            )
            xs.append(xi if keep else None)
            ys.append(yi if keep else None)
            hs.append(extra[i])
        if any(v is not None for v in xs):
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines", name=name, customdata=hs,
                line=dict(color=SERIES_1, width=2, dash=dash),
                hovertemplate="%{x:,.4g}<br>$%{y:,.0f}%{customdata}<extra></extra>",
                connectgaps=False,
            ))

    segment(True, "Rango de la correlación", "solid")
    segment(False, "Extrapolación", "dot")
    fig.add_trace(go.Scatter(
        x=[current[0]], y=[current[1]], mode="markers", name=current_label,
        marker=dict(color=SERIES_1, size=11, line=dict(color=SURFACE, width=2.5)),
        hovertemplate=current_label + "<br>%{x:,.4g}<br>$%{y:,.0f}<extra></extra>",
    ))
    show_legend = not all(valid)
    _layout(fig, 330, x_title=x_title, y_title=y_title, showlegend=show_legend)
    fig.update_yaxes(tickprefix="$", separatethousands=True)
    if log_x:
        fig.update_xaxes(type="log", dtick=1, tickformat=",~g", minor=dict(ticks="outside",
                         ticklen=3, tickcolor=AXIS, showgrid=False))
    return fig


def cepci_line(years: list[int], values: list[float], selected: tuple[float, float] | None,
               y_title: str, label: str) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=years, y=values, mode="lines+markers",
        line=dict(color=SERIES_1, width=2),
        marker=dict(size=5, color=SERIES_1),
        hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
        name="Costo",
    ))
    if selected is not None:
        fig.add_trace(go.Scatter(
            x=[selected[0]], y=[selected[1]], mode="markers", name=label,
            marker=dict(color=STRONG, size=12, line=dict(color=SURFACE, width=2.5)),
            hovertemplate=label + "<br>$%{y:,.0f}<extra></extra>",
        ))
    _layout(fig, 330, x_title="Año", y_title=y_title)
    fig.update_yaxes(tickprefix="$", separatethousands=True, rangemode="normal")
    fig.update_xaxes(dtick=2)
    return fig


def cepci_index(years: list[int], values: list[float], base: float) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=years, y=values, mode="lines+markers", line=dict(color=SERIES_1, width=2),
        marker=dict(size=5), hovertemplate="%{x}<br>CEPCI %{y:.1f}<extra></extra>",
    ))
    fig.add_hline(y=base, line=dict(color=MUTED, width=1),
                  annotation_text=f"Base de las correlaciones = {base:g}",
                  annotation_position="top left",
                  annotation_font=dict(size=11, color=MUTED))
    _layout(fig, 300, x_title="Año", y_title="CEPCI")
    fig.update_yaxes(rangemode="normal")
    fig.update_xaxes(dtick=2)
    return fig


def composition(segments: list[tuple[str, float, str]], fmt, currency: str) -> go.Figure:
    """Barra segmentada horizontal: de qué se compone el costo grassroots."""
    total = sum(v for _, v, _ in segments) or 1.0
    fig = go.Figure()
    for name, value, color in segments:
        share = value / total
        fig.add_trace(go.Bar(
            y=[""], x=[value], name=name, orientation="h",
            marker=dict(color=color, line=dict(color=SURFACE, width=2)),
            text=[f"{name}<br><b>{fmt(value)}</b> · {share:.0%}"] if share > 0.12 else [""],
            textposition="inside", insidetextanchor="start",
            textfont=dict(color="white", size=12),
            hovertemplate=f"{name}<br>{fmt(value)} {currency} · {share:.1%}<extra></extra>",
        ))
    _layout(fig, 150, showlegend=True)
    fig.update_layout(barmode="stack", margin=dict(l=0, r=0, t=34, b=0), barcornerradius=6,
                      legend=dict(traceorder="normal"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def pareto(labels: list[str], values: list[float], fmt, currency: str) -> go.Figure:
    order = sorted(range(len(values)), key=lambda i: values[i])
    total = sum(values) or 1.0
    xs = [values[i] for i in order]
    ys = [labels[i] for i in order]
    fig = go.Figure(go.Bar(
        x=xs, y=ys, orientation="h",
        marker=dict(color=SERIES_1, line=dict(width=0)),
        text=[f"{fmt(v)} · {v / total:.0%}" for v in xs],
        textposition="outside", cliponaxis=False,
        textfont=dict(size=11, color=INK_2),
        hovertemplate="%{y}<br>$%{x:,.0f} " + currency + "<extra></extra>",
    ))
    _layout(fig, max(220, 34 * len(values) + 60), x_title=f"C<sub>BM</sub> ({currency})")
    fig.update_xaxes(tickprefix="$", separatethousands=True, showgrid=True,
                     gridcolor=GRID, range=[0, max(xs) * 1.28] if xs else None)
    fig.update_yaxes(showgrid=False, rangemode="normal", automargin=True, ticks="")
    return fig
