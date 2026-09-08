"""Figuras Plotly puras y reutilizables del panel."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


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
