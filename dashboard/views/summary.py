"""Vista de resumen ejecutivo."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.charts import activity_by_room_type_chart
from dashboard.data import DashboardDataset
from dashboard.presentation import opportunity_table, summary_metrics


def render(
    dataset: DashboardDataset,
    listings: pd.DataFrame,
    opportunities: pd.DataFrame,
) -> None:
    st.header("Resumen ejecutivo")
    st.caption("¿Qué segmentos conviene investigar primero?")
    metrics = summary_metrics(listings, opportunities)
    columns = st.columns(5)
    columns[0].metric("Anuncios", f"{metrics.listing_count:,}".replace(",", "."))
    columns[1].metric("Barrios", str(metrics.neighborhood_count))
    columns[2].metric("Candidatos", str(metrics.candidate_count))
    columns[3].metric("Actividad histórica (reseñas)", f"{metrics.median_activity:.2f}")
    columns[4].metric("Precio mediano local", f"{metrics.median_price:.2f}")
    st.subheader("Actividad histórica por tipología")
    st.plotly_chart(
        activity_by_room_type_chart(listings, dataset.room_types),
        width="stretch",
    )
    candidates = opportunities.loc[opportunities["opportunity_label"].eq("candidate")]
    st.subheader("Candidatos prioritarios")
    if candidates.empty:
        st.info("No hay candidatos en la selección; revisa las observaciones en Oportunidades.")
    else:
        priority = opportunity_table(dataset, candidates).head(5)
        visible = [
            column
            for column in (
                "Rango candidato",
                "Barrio",
                "Tipología",
                "Anuncios",
                "Actividad mediana",
                "Sensibilidad",
            )
            if column in priority
        ]
        st.dataframe(priority[visible], hide_index=True, width="stretch")
    st.warning(
        "Son oportunidades provisionales. Una reseña es solo un indicio de actividad: "
        "no equivale a una reserva y no demuestra demanda, ocupación, ingresos ni rentabilidad."
    )
