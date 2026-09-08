"""Vista de hipótesis y confianza estadística."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.charts import effect_interval_chart
from dashboard.data import DashboardDataset
from dashboard.presentation import evidence_csv, evidence_summary, evidence_table


def render(dataset: DashboardDataset, statistics: pd.DataFrame) -> None:
    st.header("Evidencia estadística")
    st.caption("¿Con qué confianza podemos sostener las observaciones?")
    st.subheader("H1 · ¿Difiere la actividad histórica entre tipologías?")
    st.markdown(
        "Kruskal–Wallis y comparaciones Mann–Whitney dentro de ciudad, con tamaños de efecto, "
        "intervalos y corrección de Holm."
    )
    st.subheader("H2 · ¿Difiere un barrio–tipología de su referencia local?")
    st.markdown(
        "Mann–Whitney con anfitrión como unidad inferencial, bootstrap por conglomerados y "
        "ajuste Benjamini–Hochberg."
    )
    st.subheader("H3 · ¿Se asocian precio o estancia mínima con el proxy?")
    st.markdown(
        "Correlación de Spearman dentro de ciudad. Una asociación no implica causalidad ni "
        "demuestra demanda, ocupación o ingresos."
    )
    if statistics.empty:
        st.info(
            "Estado insufficient: no existe evidencia precalculada compatible con esta "
            "selección. Amplía o restablece los filtros."
        )
        return
    st.plotly_chart(effect_interval_chart(statistics), width="stretch")
    table = evidence_table(dataset, statistics)
    st.dataframe(table, hide_index=True, width="stretch")
    st.download_button(
        "Descargar evidencia segura",
        data=evidence_csv(table),
        file_name="evidencia_filtrada.csv",
        mime="text/csv",
    )
    selected = st.selectbox(
        "Resultado para interpretar",
        list(statistics.index),
        format_func=lambda index: str(statistics.loc[index, "comparison"]),
    )
    st.info(evidence_summary(statistics.loc[selected]))
