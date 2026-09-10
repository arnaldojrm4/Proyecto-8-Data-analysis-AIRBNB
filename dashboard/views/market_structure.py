"""Vista interactiva del EDA de estructura del mercado."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.charts import (
    neighborhood_activity_map,
    pareto_review_chart,
    portfolio_mix_chart,
    reviews_histogram_chart,
    supply_activity_scatter,
)
from dashboard.data import DashboardDataset
from dashboard.market_structure import neighborhood_metrics, pareto_metrics, portfolio_mix


def _rank_table(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame(columns=["Grupo", "Barrio", "Anuncios", "Actividad", "Cobertura"])
    count = min(10, len(metrics))
    high = metrics.nlargest(count, "activity_per_listing").assign(Grupo="Mayor actividad")
    low = metrics.nsmallest(count, "activity_per_listing").assign(Grupo="Menor actividad")
    return (
        pd.concat([high, low], ignore_index=True)
        .drop_duplicates("neighborhood_key")
        .rename(
            columns={
                "neighborhood_label": "Barrio",
                "listing_count": "Anuncios",
                "activity_per_listing": "Actividad",
                "activity_coverage": "Cobertura",
            }
        )[["Grupo", "Barrio", "Anuncios", "Actividad", "Cobertura"]]
    )


def render(dataset: DashboardDataset, listings: pd.DataFrame) -> None:
    st.header("Estructura del mercado")
    st.caption("¿Dónde coinciden oferta, actividad relativa y concentración?")
    minimum = st.slider(
        "Mínimo de anuncios por barrio",
        min_value=1,
        max_value=200,
        value=30,
        help="Se aplica al scatter, mapa y ranking para reducir extremos con muestras pequeñas.",
    )
    metrics = neighborhood_metrics(listings, dataset.neighborhoods, min_listings=minimum)
    pareto = pareto_metrics(listings)
    mix = portfolio_mix(listings)
    analyzable = listings["activity_proxy_is_analyzable"].fillna(False).astype(bool)
    activity = pd.to_numeric(listings.loc[analyzable, "activity_proxy"], errors="coerce").mean()
    coverage = analyzable.mean() if len(listings) else 0.0
    gt5_share = mix.loc[mix["portfolio_bucket"].isin(["6–10", ">10"]), "listing_share"].sum()

    columns = st.columns(5)
    columns[0].metric("Anuncios", f"{len(listings):,}".replace(",", "."))
    columns[1].metric("Actividad/anuncio", f"{activity:.2f}" if pd.notna(activity) else "—")
    columns[2].metric("Cobertura", f"{coverage:.1%}")
    columns[3].metric("Top 20 % reseñas", f"{pareto['top20_review_share']:.1%}")
    columns[4].metric("Carteras >5", f"{gt5_share:.1%}")

    st.subheader("Oferta frente a actividad relativa por barrio")
    st.caption(
        "Cada punto es un barrio. El tamaño representa anuncios, el color actividad y el tooltip "
        "incluye cobertura. La asociación no demuestra demanda insatisfecha ni sobreoferta."
    )
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            supply_activity_scatter(metrics), width="stretch", key="market_supply_activity"
        )
    with right:
        st.plotly_chart(
            neighborhood_activity_map(metrics), width="stretch", key="market_activity_map"
        )

    st.subheader("Barrios extremos")
    st.dataframe(
        _rank_table(metrics),
        hide_index=True,
        width="stretch",
        column_config={
            "Actividad": st.column_config.NumberColumn(format="%.2f"),
            "Cobertura": st.column_config.NumberColumn(format="percent"),
        },
    )

    st.subheader("Concentración de actividad histórica")
    st.caption(
        f"El 20 % con más reseñas concentra {pareto['top20_review_share']:.1%}; "
        f"{pareto['listing_share_for_80']:.1%} de los anuncios reúne el 80 %. "
        "Las reseñas acumuladas no equivalen a reservas."
    )
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            pareto_review_chart(listings), width="stretch", key="market_pareto"
        )
    with right:
        st.plotly_chart(
            reviews_histogram_chart(listings), width="stretch", key="market_histogram"
        )

    st.subheader("Tamaño de cartera observado")
    st.plotly_chart(portfolio_mix_chart(mix), width="stretch", key="market_portfolio")
    st.caption(
        "Los grupos describen anuncios asociados al mismo host en el snapshot. "
        "No identifican propiedad, profesionalidad ni estatus fiscal. En Tokio se deriva del "
        "conteo de anuncios observados por host."
    )
