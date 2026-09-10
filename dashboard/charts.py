"""Figuras Plotly puras y reutilizables del panel."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from dashboard.market_structure import pareto_curve


def _empty_figure() -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text="Sin datos para la selección",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    figure.update_layout(xaxis_visible=False, yaxis_visible=False)
    return figure


def activity_by_room_type_chart(
    listings: pd.DataFrame,
    room_types: pd.DataFrame,
) -> go.Figure:
    """Compara medianas del proxy sin mezclar ciudades ni monedas."""

    required = {"room_type_key", "activity_proxy"}
    if listings.empty or room_types.empty or not required.issubset(listings.columns):
        return _empty_figure()
    summary = (
        listings.groupby("room_type_key", observed=True)["activity_proxy"]
        .median()
        .rename("median")
        .reset_index()
        .merge(
            room_types[["room_type_key", "room_type_label_es"]],
            on="room_type_key",
            how="left",
            validate="one_to_one",
        )
        .sort_values("room_type_label_es", kind="stable")
    )
    figure = go.Figure(
        go.Bar(
            x=summary["room_type_label_es"],
            y=summary["median"],
            marker_color="#C44A32",
            hovertemplate="%{x}<br>Mediana: %{y:.2f}<extra></extra>",
        )
    )
    figure.update_layout(
        xaxis_title="Tipología",
        yaxis_title="Proxy de actividad histórica",
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
    )
    return figure


def opportunity_map_chart(opportunities: pd.DataFrame) -> go.Figure:
    """Representa solo centroides agregados; la tabla continúa siendo el fallback."""

    required = {"centroid_latitude", "centroid_longitude"}
    if opportunities.empty or not required.issubset(opportunities.columns):
        return _empty_figure()
    usable = opportunities.dropna(subset=list(required)).copy()
    if usable.empty:
        return _empty_figure()
    figure = go.Figure(
        go.Scattermap(
            lat=usable["centroid_latitude"],
            lon=usable["centroid_longitude"],
            mode="markers",
            text=usable["neighborhood_label"],
            customdata=usable[["room_type_label_es", "activity_median"]],
            marker={
                "size": usable["listing_count"].clip(lower=6).pow(0.5) * 4,
                "color": usable["activity_median"],
                "colorscale": "YlOrRd",
                "showscale": True,
            },
            hovertemplate=(
                "%{text}<br>%{customdata[0]}<br>Actividad mediana: "
                "%{customdata[1]:.2f}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        map={"style": "open-street-map", "zoom": 9},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=430,
    )
    return figure


def effect_interval_chart(statistics: pd.DataFrame) -> go.Figure:
    """Muestra estimaciones publicadas con sus intervalos, sin recalcularlos."""

    required = {"comparison", "estimate", "ci_low", "ci_high"}
    if statistics.empty or not required.issubset(statistics.columns):
        return _empty_figure()
    usable = statistics.dropna(subset=list(required)).copy()
    if usable.empty:
        return _empty_figure()
    estimates = pd.to_numeric(usable["estimate"])
    low = pd.to_numeric(usable["ci_low"])
    high = pd.to_numeric(usable["ci_high"])
    figure = go.Figure(
        go.Scatter(
            x=estimates,
            y=usable["comparison"],
            mode="markers",
            marker={"color": "#C44A32", "size": 9},
            error_x={
                "type": "data",
                "symmetric": False,
                "array": high - estimates,
                "arrayminus": estimates - low,
            },
            hovertemplate="%{y}<br>Efecto: %{x:.3f}<extra></extra>",
        )
    )
    figure.update_layout(
        xaxis_title="Estimación e intervalo de confianza del 95%",
        yaxis_title="Comparación",
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
    )
    return figure


def supply_activity_scatter(metrics: pd.DataFrame) -> go.Figure:
    """Relaciona oferta y actividad al grano de barrio."""

    if metrics.empty:
        return _empty_figure()
    figure = go.Figure(
        go.Scatter(
            x=metrics["listing_count"],
            y=metrics["activity_per_listing"],
            text=metrics["neighborhood_label"],
            customdata=metrics[["activity_coverage"]],
            mode="markers",
            marker={
                "size": metrics["listing_count"].pow(0.5).clip(8, 38),
                "color": metrics["activity_per_listing"],
                "colorscale": "YlOrRd",
                "line": {"color": "#17324D", "width": 0.7},
                "showscale": True,
                "colorbar": {"title": "Actividad"},
            },
            hovertemplate=(
                "<b>%{text}</b><br>Anuncios: %{x:,.0f}<br>Actividad: %{y:.2f}"
                "<br>Cobertura: %{customdata[0]:.1%}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        xaxis={"title": "Anuncios del barrio (escala log)", "type": "log"},
        yaxis={"title": "Reseñas/mes por anuncio", "rangemode": "tozero"},
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        height=460,
    )
    return figure


def neighborhood_activity_map(metrics: pd.DataFrame) -> go.Figure:
    """Dibuja centroides agregados y conserva oferta en el tamaño del punto."""

    required = ["centroid_latitude", "centroid_longitude"]
    usable = metrics.dropna(subset=required)
    if usable.empty:
        return _empty_figure()
    figure = go.Figure(
        go.Scattermap(
            lat=usable["centroid_latitude"],
            lon=usable["centroid_longitude"],
            text=usable["neighborhood_label"],
            customdata=usable[["listing_count", "activity_per_listing", "activity_coverage"]],
            mode="markers",
            marker={
                "size": usable["listing_count"].pow(0.5).clip(7, 32),
                "color": usable["activity_per_listing"],
                "colorscale": "YlOrRd",
                "showscale": True,
            },
            hovertemplate=(
                "<b>%{text}</b><br>Anuncios: %{customdata[0]:,.0f}"
                "<br>Actividad: %{customdata[1]:.2f}"
                "<br>Cobertura: %{customdata[2]:.1%}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        map={"style": "open-street-map", "zoom": 9},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=460,
    )
    return figure


def pareto_review_chart(listings: pd.DataFrame) -> go.Figure:
    """Representa la concentración acumulada de reseñas históricas."""

    curve = pareto_curve(listings)
    if curve.empty:
        return _empty_figure()
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=curve["listing_share"],
            y=curve["review_share"],
            mode="lines",
            line={"color": "#2F6B8A", "width": 3},
            name="Concentración observada",
            hovertemplate="Anuncios: %{x:.1%}<br>Reseñas: %{y:.1%}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines", name="Igualdad",
            line={"color": "#7B8794", "dash": "dash"}, hoverinfo="skip",
        )
    )
    figure.add_vline(x=0.2, line_dash="dot", line_color="#C76D3A")
    figure.add_hline(y=0.8, line_dash="dot", line_color="#C76D3A")
    figure.update_layout(
        xaxis={"title": "% acumulado de anuncios", "tickformat": ".0%"},
        yaxis={"title": "% acumulado de reseñas", "tickformat": ".0%"},
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        height=420,
    )
    return figure


def reviews_histogram_chart(listings: pd.DataFrame) -> go.Figure:
    """Muestra la cola de reseñas con transformación logarítmica declarada."""

    if listings.empty:
        return _empty_figure()
    values = pd.to_numeric(listings["number_of_reviews"], errors="coerce").fillna(0)
    figure = go.Figure(
        go.Histogram(x=np.log1p(values), nbinsx=35, marker_color="#77B5D9")
    )
    figure.update_layout(
        xaxis_title="log(1 + número de reseñas)",
        yaxis_title="Anuncios",
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        height=420,
        showlegend=False,
    )
    return figure


def portfolio_mix_chart(mix: pd.DataFrame) -> go.Figure:
    """Compara la composición de listings por grupo de cartera."""

    if mix.empty:
        return _empty_figure()
    colors = ["#77B5D9", "#2F6B8A", "#D8B365", "#C76D3A"]
    figure = go.Figure(
        go.Bar(
            x=mix["listing_share"],
            y=mix["portfolio_bucket"],
            orientation="h",
            marker_color=colors,
            text=mix["listing_share"].map(lambda value: f"{value:.1%}"),
            textposition="auto",
            customdata=mix[["listing_count"]],
            hovertemplate=(
                "Cartera %{y}<br>Anuncios: %{customdata[0]:,.0f}<br>Cuota: %{x:.1%}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        xaxis={"title": "Porcentaje de anuncios", "tickformat": ".0%", "rangemode": "tozero"},
        yaxis={
            "title": "Anuncios del host",
            "categoryorder": "array",
            "categoryarray": mix["portfolio_bucket"].tolist(),
        },
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        height=360,
    )
    return figure
