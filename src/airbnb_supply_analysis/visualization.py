"""Visualizaciones reproducibles y seguras para notebooks y entregables."""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
from matplotlib import MatplotlibDeprecationWarning
from matplotlib.figure import Figure

plt.switch_backend("Agg")


PALETTE = {
    "entire_home_apt": "#2F5D8A",
    "private_room": "#D99B2B",
    "shared_room": "#A35D34",
    "hotel_room": "#7C7C6C",
}


def activity_by_room_type(frame: pd.DataFrame) -> Figure:
    sample = frame.dropna(subset=["room_type", "activity_proxy"]).copy()
    figure, axis = plt.subplots(figsize=(9, 5))
    order = (
        sample.groupby("room_type", observed=True)["activity_proxy"]
        .median()
        .sort_values()
        .index
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", MatplotlibDeprecationWarning)
        sns.boxplot(
            data=sample,
            x="room_type",
            y="activity_proxy",
            order=order,
            palette=PALETTE,
            hue="room_type",
            legend=False,
            showfliers=False,
            ax=axis,
        )
    axis.set_title("Distribución del proxy de actividad histórica por tipología")
    axis.set_xlabel("Tipología de alojamiento")
    axis.set_ylabel("Reseñas mensuales (proxy histórico)")
    figure.tight_layout()
    return figure


def opportunity_scatter(segments: pd.DataFrame):
    return px.scatter(
        segments,
        x="neighborhood_room_type_share",
        y="probability_superiority",
        size="listing_count",
        color="opportunity_label",
        hover_name="neighborhood",
        hover_data={
            "city_key": True,
            "room_type": True,
            "listing_count": True,
            "q_value": ":.3g",
            "segment_key": False,
        },
        labels={
            "neighborhood_room_type_share": "Cuota de tipología en el barrio",
            "probability_superiority": "Probabilidad de superioridad de actividad histórica",
            "listing_count": "Anuncios",
        },
        title="Evidencia de actividad histórica y cuota local por segmento",
        template="plotly_white",
    )


def room_type_mix_by_city(frame: pd.DataFrame) -> Figure:
    mix = pd.crosstab(frame["city_key"], frame["room_type"], normalize="index")
    figure, axis = plt.subplots(figsize=(10, 5))
    mix.plot(
        kind="barh",
        stacked=True,
        color=[PALETTE.get(column, "#777777") for column in mix.columns],
        ax=axis,
    )
    axis.set_title("Composición de tipologías dentro de cada ciudad")
    axis.set_xlabel("Cuota de anuncios")
    axis.set_ylabel("Ciudad")
    axis.legend(title="Tipología", bbox_to_anchor=(1.02, 1), loc="upper left")
    figure.tight_layout()
    return figure


def top_neighborhood_activity(frame: pd.DataFrame) -> Figure:
    summary = (
        frame.dropna(subset=["activity_proxy", "neighborhood"])
        .groupby(["city_key", "neighborhood"], observed=True)
        .agg(activity_median=("activity_proxy", "median"), listings=("listing_key", "size"))
        .query("listings >= 30")
        .reset_index()
    )
    top = (
        summary.sort_values(
            ["city_key", "activity_median", "listings"],
            ascending=[True, False, False],
        )
        .groupby("city_key", observed=True)
        .head(3)
    )
    top["label"] = top["city_key"] + " · " + top["neighborhood"]
    top = top.sort_values("activity_median")
    figure, axis = plt.subplots(figsize=(10, 8))
    axis.barh(top["label"], top["activity_median"], color="#2F5D8A")
    axis.set_title("Tres barrios con mayor mediana de actividad histórica por ciudad")
    axis.set_xlabel("Reseñas mensuales medianas (proxy histórico)")
    axis.set_ylabel("")
    figure.tight_layout()
    return figure


def association_effects(statistical: pd.DataFrame) -> Figure:
    """Compara asociaciones estandarizadas por ciudad, nunca importes monetarios."""

    associations = statistical.loc[statistical["method"].eq("spearman")].copy()
    figure, axis = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=associations,
        x="city_key",
        y="estimate",
        hue="metric",
        palette={
            "price_vs_activity": "#2F5D8A",
            "minimum_nights_vs_activity": "#D99B2B",
        },
        ax=axis,
    )
    axis.axhline(0, color="#444444", linewidth=0.8)
    axis.set_title("Asociaciones intra-ciudad con la actividad histórica")
    axis.set_xlabel("Ciudad")
    axis.set_ylabel("Coeficiente de Spearman")
    axis.legend(title="Asociación")
    figure.tight_layout()
    return figure


def save_core_figures(
    listings: pd.DataFrame,
    segments: pd.DataFrame,
    destination: Path,
    statistical: pd.DataFrame | None = None,
) -> list[dict[str, str]]:
    destination.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict[str, str]] = []
    static_figures = {
        "activity_by_room_type.png": activity_by_room_type(listings),
        "room_type_mix_by_city.png": room_type_mix_by_city(listings),
        "top_neighborhood_activity.png": top_neighborhood_activity(listings),
    }
    if statistical is not None:
        static_figures["association_effects.png"] = association_effects(statistical)
    for filename, figure in static_figures.items():
        path = destination / filename
        figure.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(figure)
        artifacts.append({"path": _manifest_path(path), "type": "png"})
    interactive_path = destination / "opportunity_scatter.html"
    opportunity_scatter(segments).write_html(
        interactive_path, include_plotlyjs=True, full_html=True
    )
    artifacts.append({"path": _manifest_path(interactive_path), "type": "html"})
    return artifacts


def _manifest_path(path: Path) -> str:
    """Evita rutas personales cuando el artefacto pertenece al proyecto."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()
