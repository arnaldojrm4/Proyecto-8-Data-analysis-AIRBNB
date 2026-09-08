"""Vista de resumen ejecutivo."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.charts import activity_by_room_type_chart
from dashboard.data import DashboardDataset
from dashboard.presentation import summary_metrics


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
    columns[3].metric("Actividad mediana", f"{metrics.median_activity:.2f}")
    columns[4].metric("Precio mediano local", f"{metrics.median_price:.2f}")
    st.subheader("Actividad histórica por tipología")
    st.plotly_chart(
        activity_by_room_type_chart(listings, dataset.room_types),
        width="stretch",
    )
    st.warning(
        "Son oportunidades provisionales. El proxy de reseñas no demuestra demanda, "
        "reservas, ocupación, ingresos ni rentabilidad."
    )

