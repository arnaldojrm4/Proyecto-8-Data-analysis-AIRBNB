"""Vista de oportunidades por barrio y tipología."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.charts import opportunity_map_chart
from dashboard.data import DashboardDataset
from dashboard.presentation import labeled_opportunities, opportunity_csv, opportunity_table


def render(dataset: DashboardDataset, opportunities: pd.DataFrame) -> None:
    st.header("Oportunidades de captación")
    st.caption("¿Dónde se concentra la oportunidad provisional?")
    if opportunities.empty:
        st.info(
            "Estado empty: no hay segmentos para esta selección. "
            "Restablece o amplía los filtros."
        )
        return
    display = labeled_opportunities(dataset, opportunities)
    table = opportunity_table(dataset, opportunities)
    st.subheader("Ranking transparente de oportunidades")
    st.dataframe(table, hide_index=True, width="stretch")
    st.download_button(
        "Descargar selección segura",
        data=opportunity_csv(table),
        file_name="oportunidades_filtradas.csv",
        mime="text/csv",
    )
    st.subheader("Centroides agregados de barrios")
    st.plotly_chart(opportunity_map_chart(display), width="stretch")
    st.caption("El ranking anterior conserva la lectura completa si el mapa no está disponible.")
