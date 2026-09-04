"""Genera los notebooks narrativos versionados sin edición manual de JSON."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def write_notebook(name: str, cells: list) -> None:
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.13"},
        },
    )
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, NOTEBOOKS / name)


def audit_notebook() -> None:
    cells = [
        markdown(
            """
            # Auditoría de las seis fuentes

            ## tl;dr

            Las fuentes contienen **220.031 registros** de seis ciudades. Su identidad se valida
            mediante nombre, cabecera, bytes, filas y SHA-256 antes de cualquier análisis. La
            procedencia, licencia, moneda y fecha de extracción permanecen desconocidas.
            """
        ),
        markdown(
            """
            ## Contexto y métodos

            ### Supuestos clave

            Cada fila representa un anuncio dentro de su ciudad. Se comprueba la clave candidata
            `city_key + id`, pero no se presupone que `id` sea global. Los outliers válidos se
            conservan y se señalan mediante IQR; no se limpian de forma silenciosa.
            """
        ),
        markdown("### 1. Cargar evidencia de inventario y calidad"),
        code(
            """
            import json
            from pathlib import Path
            import pandas as pd

            ROOT = Path("..").resolve()
            inventory_path = ROOT / "artifacts/quality/source-inventory.json"
            inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
            profile = pd.read_parquet(ROOT / "artifacts/quality/source-profile.parquet")
            findings = pd.read_parquet(ROOT / "artifacts/quality/findings.parquet")
            inventory_table = pd.DataFrame(inventory["sources"])[
                ["city_key", "file_name", "parsed_row_count", "byte_size", "identity_status"]
            ]
            inventory_table
            """
        ),
        markdown(
            """
            **Conclusión.** La suma esperada es 220.031 y todos los archivos deben aparecer como
            `identity_verified`. Esta comprobación respalda la integridad técnica de la copia, no la
            autoridad ni la actualidad de la fuente.
            """
        ),
        markdown("### 2. Revisar completitud y hallazgos por ciudad"),
        code(
            """
            null_summary = (
                profile.query("null_count > 0")
                .sort_values(["null_rate", "source_id"], ascending=[False, True])
                [["source_id", "field", "row_count", "null_count", "null_rate"]]
            )
            open_findings = findings.query("failed_count > 0")[
                ["source_id", "check_id", "severity", "failed_count", "failed_rate", "impact"]
            ].sort_values(["severity", "failed_rate"], ascending=[True, False])
            display(null_summary.head(30))
            display(open_findings.head(30))
            """
        ),
        markdown(
            """
            **Conclusión.** Los nulos y valores extremos se cuantifican por fuente y campo. Los
            faltantes estructurales de columnas se distinguirán de un valor cero; los outliers se
            retienen para análisis robusto. La utilidad de cada métrica depende de estas tasas y no
            solo del volumen total.
            """
        ),
        markdown(
            """
            ## Takeaways

            La base es apta para construir un modelo canónico siempre que se preserve el linaje y se
            mantengan explícitas las ausencias. No permite inferir actividad reciente, divisa,
            reservas ni representatividad del mercado completo.
            """
        ),
    ]
    write_notebook("01_data_audit.ipynb", cells)


def etl_notebook() -> None:
    cells = [
        markdown(
            """
            # ETL y dataset canónico

            ## tl;dr

            El proceso transforma las seis fuentes sin eliminar registros: **220.031 entradas y
            220.031 filas canónicas**. Los datos raw permanecen inmutables y cada regla registra las
            filas evaluadas y modificadas.
            """
        ),
        markdown(
            """
            ## Contexto y métodos

            ### Supuestos clave

            `reviews_per_month` se conserva como observada. Solo se deriva cero cuando falta y
            `number_of_reviews == 0`; si hay reseñas positivas y falta la tasa, la actividad queda
            desconocida. No se usan sentinelas de fecha ni ceros para columnas ausentes.
            """
        ),
        markdown("### 1. Cargar el build canónico y su conciliación"),
        code(
            """
            import json
            from pathlib import Path
            import pandas as pd

            ROOT = Path("..").resolve()
            listings = pd.read_parquet(ROOT / "data/processed/listings.parquet")
            transformations = pd.read_parquet(ROOT / "artifacts/quality/transformations.parquet")
            reconciliation_path = ROOT / "artifacts/quality/row-reconciliation.json"
            reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
            reconciliation
            """
        ),
        markdown(
            """
            **Conclusión.** El build es aceptable únicamente si la diferencia es cero y la clave
            canónica es única. La conciliación demuestra cobertura del proceso, no exactitud del
            contenido declarado por cada anuncio.
            """
        ),
        markdown("### 2. Cuantificar tratamientos y disponibilidad analítica"),
        code(
            """
            activity_quality = pd.Series({
                "filas": len(listings),
                "actividad_analizable": int(listings["activity_proxy_is_analyzable"].sum()),
                "ceros_derivados": int(listings["activity_proxy_derived_zero"].sum()),
                "actividad_desconocida": int((~listings["activity_proxy_is_analyzable"]).sum()),
                "precio_invalido": int((~listings["price_is_valid"]).sum()),
            }).to_frame("conteo")
            display(activity_quality)
            transformation_columns = [
                "source_id", "field", "rows_evaluated", "rows_changed", "rule"
            ]
            display(transformations[transformation_columns])
            """
        ),
        markdown(
            """
            **Conclusión.** Se derivan 54.248 ceros respaldados por ausencia de reseñas y quedan 123
            tasas desconocidas pese a existir reseñas positivas. Hay 50 precios no positivos que se
            excluyen solo de métricas de precio. Las filas se conservan para el resto del análisis.
            """
        ),
        markdown("### 3. Verificar composición por ciudad y tipología"),
        code(
            """
            city_counts = listings.groupby("city_key", observed=True).size().rename("filas")
            room_counts = listings.groupby("room_type", observed=True).size().rename("filas")
            display(city_counts.to_frame())
            display(room_counts.to_frame())
            """
        ),
        markdown(
            """
            **Conclusión.** Los tamaños de ciudad son muy distintos, por lo que se usarán cuotas y
            comparaciones dentro de ciudad. La tipología mayoritaria global no constituye por sí
            sola una oportunidad de captación.
            """
        ),
        markdown(
            """
            ## Takeaways

            El dataset canónico está conciliado y conserva indicadores de disponibilidad. Su diseño
            permite EDA y estadística sin convertir ausencias en actividad, precio o actualidad.
            """
        ),
    ]
    write_notebook("02_etl.ipynb", cells)


def executive_eda_notebook() -> None:
    cells = [
        markdown(
            """
            # EDA ejecutivo y oportunidades de captación

            ## tl;dr

            Con los umbrales bloqueados se identifican **29 segmentos candidatos** en cinco de las
            seis ciudades; Londres no conserva candidatos tras las sensibilidades. Son prioridades
            provisionales para investigar captación, no estimaciones de demanda, reservas, ocupación
            o margen.
            """
        ),
        markdown(
            """
            ## Contexto y métodos

            ### Pregunta de decisión

            ¿Qué tipologías conviene investigar primero para captar nuevos anfitriones y en qué
            barrios? La unidad es `ciudad + barrio + tipología`. Se comparan actividad histórica,
            cuota de oferta, tamaño, precio local y evidencia estadística por separado.

            ### Supuestos clave

            La tasa de reseñas es un proxy histórico. Todos los contrastes y precios se interpretan
            dentro de ciudad. Se usan alfa 0,05, IC 95 %, efectos, correcciones Holm/BH y
            sensibilidades de casos completos, outliers y concentración por anfitrión.
            """
        ),
        markdown("### 1. Cargar resultados aceptados"),
        code(
            """
            from pathlib import Path
            import pandas as pd
            from IPython.display import display
            from airbnb_supply_analysis.visualization import (
                activity_by_room_type,
                association_effects,
                opportunity_scatter,
            )

            ROOT = Path("..").resolve()
            listings = pd.read_parquet(ROOT / "data/processed/listings.parquet")
            results = pd.read_parquet(ROOT / "data/processed/statistical_results.parquet")
            segments = pd.read_parquet(ROOT / "data/processed/opportunity_segments.parquet")
            {"anuncios": len(listings), "segmentos": len(segments), "resultados": len(results)}
            """
        ),
        markdown(
            """
            **Conclusión.** Los tres artefactos comparten build y derivan de 220.031 anuncios. La
            cobertura permite comparar patrones internos, pero no garantiza representatividad del
            mercado completo.
            """
        ),
        markdown("### 2. Distribución de actividad por tipología"),
        code(
            """
            room_summary = (
                listings.dropna(subset=["room_type", "activity_proxy"])
                .groupby(["city_key", "room_type"], observed=True)
                .agg(
                    anuncios=("listing_key", "size"),
                    actividad_mediana=("activity_proxy", "median"),
                    cuota_positiva=("activity_proxy", lambda values: values.gt(0).mean()),
                )
                .reset_index()
            )
            display(room_summary)
            activity_by_room_type(listings)
            """
        ),
        markdown(
            """
            **Conclusión.** Las tipologías difieren en escala, mediana y probabilidad de actividad.
            Una mediana mayor no basta para recomendar captación: se exige contraste dentro de
            ciudad, efecto, precisión, corrección y cuota relativa de oferta.
            """
        ),
        markdown("### 3. Contrastes y asociaciones dentro de ciudad"),
        code(
            """
            room_tests = results.query("method == 'kruskal_wallis'")[
                ["city_key", "sample_size", "estimate", "p_value_adjusted"]
            ]
            associations = results.query("method == 'spearman'")[
                ["city_key", "metric", "estimate", "ci_low", "ci_high", "p_value_adjusted"]
            ]
            display(room_tests)
            display(associations)
            association_effects(results)
            """
        ),
        markdown(
            """
            **Conclusión.** La relación entre precio publicado y actividad es débil en todas las
            ciudades observadas; cambia de signo en Tokio. Las noches mínimas muestran asociaciones
            negativas de magnitud variable. Aunque muchos valores ajustados son pequeños por el gran
            tamaño muestral, las correlaciones no implican causalidad ni rentabilidad.
            """
        ),
        markdown("### 4. Matriz de oportunidades y top tres por ciudad"),
        code(
            """
            candidates = segments.query("opportunity_label == 'candidate'").copy()
            candidate_counts = candidates.groupby("city_key", observed=True).size()
            top_columns = [
                "city_key", "neighborhood", "room_type", "listing_count",
                "activity_median", "probability_superiority", "effect_ci_low",
                "q_value", "neighborhood_room_type_share", "room_type_city_share",
                "candidate_rank",
            ]
            top_candidates = (
                candidates.sort_values(["city_key", "candidate_rank"])[top_columns]
                .groupby("city_key", observed=True)
                .head(3)
            )
            display(candidate_counts.to_frame("segmentos_candidatos"))
            display(top_candidates)
            """
        ),
        markdown(
            """
            **Conclusión.** El primer foco por escala es Justicia-habitación privada en Madrid,
            CENTRALE-alojamiento completo en Milán, Bedford-Stuyvesant-alojamiento completo en Nueva
            York, Leichhardt-habitación privada en Sídney y Nakano Ku-habitación privada en Tokio.
            Londres queda sin candidato robusto; no se rebajan reglas para forzar un top tres.
            """
        ),
        markdown("### 5. Explorar actividad relativa frente a cuota local"),
        code(
            """
            opportunity_scatter(segments)
            """
        ),
        markdown(
            """
            **Conclusión.** La oportunidad aparente combina evidencia de actividad superior y cuota
            local inferior a la ciudad, manteniendo escala y precisión visibles. El gráfico permite
            explorar excepciones, pero la etiqueta procede de reglas versionadas y no de selección
            visual.
            """
        ),
        markdown(
            """
            ## Takeaways

            Se recomienda investigar primero los candidatos mostrados y validar la oportunidad con
            búsquedas, reservas, ocupación, conversión, ingresos y capacidad real de captación. Los
            resultados actuales sirven para priorizar investigación comercial; no justifican una
            expansión automática ni una promesa de margen.
            """
        ),
    ]
    write_notebook("03_executive_eda.ipynb", cells)


if __name__ == "__main__":
    audit_notebook()
    etl_notebook()
    executive_eda_notebook()
