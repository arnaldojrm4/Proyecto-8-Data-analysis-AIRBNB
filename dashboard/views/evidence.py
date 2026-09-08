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
        "**H₀:** las distribuciones de actividad son iguales entre tipologías. "
        "**Población de referencia:** anuncios analizables de la ciudad activa. "
        "Kruskal–Wallis y comparaciones Mann–Whitney, con tamaños de efecto, intervalos y "
        "corrección de Holm."
    )
    st.subheader("H2 · ¿Difiere un barrio–tipología de su referencia local?")
    st.markdown(
        "**H₀:** el segmento y el resto de su ciudad-tipología tienen la misma distribución. "
        "**Población de referencia:** resto de la misma ciudad y tipología. Mann–Whitney con "
        "anfitrión como unidad inferencial, bootstrap por conglomerados y ajuste "
        "Benjamini–Hochberg."
    )
    st.subheader("H3 · ¿Se asocian precio o estancia mínima con la actividad histórica?")
    st.markdown(
        "**H₀:** la correlación monotónica es cero. **Población de referencia:** anuncios "
        "analizables dentro de la ciudad. La actividad es un indicio basado en reseñas, "
        "no reservas. "
        "Correlación de Spearman. Una asociación no implica causalidad ni demuestra demanda, "
        "ocupación o ingresos."
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
