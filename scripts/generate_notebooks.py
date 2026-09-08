"""Genera los notebooks narrativos versionados sin edición manual de JSON."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent, indent

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def find_project_root(start: Path) -> Path:
    """Return the nearest ancestor that identifies this repository."""
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise FileNotFoundError("No se encontró la raíz del proyecto desde el directorio actual.")


def notebook_project_root_setup() -> str:
    """Emit runtime-safe root discovery for notebooks run from an IDE or nbconvert."""
    return dedent(
        """
        def find_project_root(start: Path) -> Path:
            for candidate in (start.resolve(), *start.resolve().parents):
                if (candidate / "pyproject.toml").is_file():
                    return candidate
            raise FileNotFoundError(
                "No se encontró la raíz del proyecto; abre el notebook dentro del repositorio."
            )

        ROOT = find_project_root(Path.cwd())
        """
    ).strip()


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
            f"""
            import json
            import os
            from pathlib import Path

            import pandas as pd


            {indent(notebook_project_root_setup(), "            ").lstrip()}
            ARTIFACTS = Path(os.environ.get("AIRBNB_SUPPLY_ARTIFACTS_DIR", ROOT / "artifacts"))
            inventory_path = ARTIFACTS / "quality/source-inventory.json"
            inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
            profile = pd.read_parquet(ARTIFACTS / "quality/source-profile.parquet")
            findings = pd.read_parquet(ARTIFACTS / "quality/findings.parquet")
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
            f"""
            import json
            import os
            from pathlib import Path

            import pandas as pd


            {indent(notebook_project_root_setup(), "            ").lstrip()}
            PROCESSED = Path(os.environ.get("AIRBNB_SUPPLY_PROCESSED_DIR", ROOT / "data/processed"))
            ARTIFACTS = Path(os.environ.get("AIRBNB_SUPPLY_ARTIFACTS_DIR", ROOT / "artifacts"))
            listings = pd.read_parquet(PROCESSED / "listings.parquet")
            transformations = pd.read_parquet(ARTIFACTS / "quality/transformations.parquet")
            reconciliation_path = ARTIFACTS / "quality/row-reconciliation.json"
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

            Con los umbrales bloqueados se identifican **28 segmentos candidatos** en cinco de las
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
            f"""
            import os
            from pathlib import Path

            import pandas as pd
            from IPython.display import display

            from airbnb_supply_analysis.visualization import (
                activity_by_room_type,
                association_effects,
                opportunity_scatter,
            )


            {indent(notebook_project_root_setup(), "            ").lstrip()}
            PROCESSED = Path(os.environ.get("AIRBNB_SUPPLY_PROCESSED_DIR", ROOT / "data/processed"))
            listings = pd.read_parquet(PROCESSED / "listings.parquet")
            results = pd.read_parquet(PROCESSED / "statistical_results.parquet")
            segments = pd.read_parquet(PROCESSED / "opportunity_segments.parquet")
            {{"anuncios": len(listings), "segmentos": len(segments), "resultados": len(results)}}
            """
        ),
        markdown(
            """
            **Conclusión.** Los artefactos del build FDAAB53F8317CAD7 contienen 220.031 anuncios,
            1.497 segmentos y 690 resultados estadísticos. La
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
            candidate_counts = (
                candidates.groupby("city_key", observed=True).size()
                .reindex(sorted(segments["city_key"].unique()), fill_value=0)
            )
            top_columns = [
                "city_key", "neighborhood", "room_type", "listing_count",
                "activity_median", "probability_superiority", "effect_ci_low", "effect_ci_high",
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
            ### 6. Distribución geográfica y brecha de oferta de los candidatos

            Se conserva la exploración local por `ciudad + barrio + tipología`. La brecha es
            `100 × (cuota de la tipología en la ciudad − cuota en el barrio)`, en puntos
            porcentuales. Una brecha positiva describe menor presencia relativa, no demuestra
            falta de oferta, saturación ni demanda insatisfecha.

            La selección usa únicamente `candidate` y el rango oficial dentro de cada ciudad.
            Se retira el score exploratorio que multiplicaba actividad, superioridad, brecha y
            tamaño: carecía de validación y mezclaba escalas históricas entre ciudades.
            Los estados `watch` conservan su carácter de observación y no entran en esta selección.
            """
        ),
        code(
            """
            import matplotlib.pyplot as plt
            import plotly.express as px
            import seaborn as sns

            local_candidates = candidates.copy()
            local_candidates["supply_gap_pp"] = 100 * (
                local_candidates["room_type_city_share"]
                - local_candidates["neighborhood_room_type_share"]
            )
            priority_segments = (
                local_candidates.sort_values(["city_key", "candidate_rank"])
                .groupby("city_key", observed=True).head(3).copy()
            )
            display(priority_segments[[
                "city_key", "neighborhood", "room_type", "listing_count",
                "candidate_rank", "supply_gap_pp", "probability_superiority",
                "effect_ci_low", "effect_ci_high", "q_value",
            ]])
            heatmap_source = priority_segments.assign(
                neighborhood_label=lambda frame: (
                    frame["city_key"].astype(str) + " / " + frame["neighborhood"].astype(str)
                )
            )
            heatmap = heatmap_source.pivot(
                index="neighborhood_label", columns="room_type", values="supply_gap_pp"
            )
            fig_heatmap, ax_heatmap = plt.subplots(figsize=(10, 7))
            sns.heatmap(
                heatmap, mask=heatmap.isna(), cmap="YlGnBu", annot=True, fmt=".1f",
                vmin=0, linewidths=0.5,
                cbar_kws={"label": "Brecha de cuota (puntos porcentuales)"}, ax=ax_heatmap,
            )
            ax_heatmap.set_title("Brecha de oferta de los tres primeros candidatos por ciudad")
            ax_heatmap.set_xlabel("Tipología")
            ax_heatmap.set_ylabel("Ciudad / barrio")
            fig_heatmap.tight_layout()
            plt.show()
            """
        ),
        markdown(
            """
            **Conclusión.** La brecha del primer candidato es 10,3 puntos en Justicia, 2,4 en
            CENTRALE, 9,1 en Bedford-Stuyvesant, 6,7 en Leichhardt y 7,2 en Nakano Ku.
            CENTRALE sigue siendo candidato con una brecha pequeña porque cumple también los
            criterios de evidencia. Las celdas vacías no representan cero, sino combinaciones
            ausentes de esta selección. No se construye un ranking comercial entre ciudades.

            ### 7. Localizar los candidatos sin perder cobertura por ciudad

            Se dibujan los centroides de todos los candidatos con coordenadas válidas. El tamaño
            refleja anuncios y el color la tipología. Son ubicaciones agregadas, no direcciones
            de inmuebles ni áreas de demanda. El mapa interactivo requiere acceso al recurso
            geográfico de Plotly en el navegador; la tabla anterior permite la lectura sin mapa.
            """
        ),
        code(
            """
            geo = local_candidates.dropna(
                subset=["centroid_latitude", "centroid_longitude"]
            ).copy()
            display(pd.Series({
                "candidatos_totales": len(local_candidates),
                "candidatos_con_coordenadas": len(geo),
                "candidatos_sin_coordenadas": len(local_candidates) - len(geo),
            }).to_frame("conteo"))
            if geo.empty:
                print("No hay candidatos con coordenadas válidas. Consulta la tabla anterior.")
            else:
                geo["segment_label"] = (
                    geo["city_key"].astype(str) + " / "
                    + geo["neighborhood"].astype(str) + " / " + geo["room_type"].astype(str)
                )
                fig_geo = px.scatter_geo(
                    geo, lat="centroid_latitude", lon="centroid_longitude",
                    color="room_type", size="listing_count", hover_name="segment_label",
                    hover_data={
                        "candidate_rank": True, "listing_count": True,
                        "supply_gap_pp": ":.1f", "probability_superiority": ":.3f",
                        "effect_ci_low": ":.3f", "effect_ci_high": ":.3f",
                        "coordinate_coverage": ":.1%",
                    },
                    projection="natural earth", template="plotly_white",
                    title="Centroides de los candidatos por barrio y tipología",
                )
                fig_geo.show()
            """
        ),
        markdown(
            """
            **Conclusión.** Los 28 candidatos tienen centroides disponibles. Sídney aporta 13
            y Nueva York 12: juntas reúnen 25 de 28 (89,3 %). Madrid, Milán y Tokio aportan uno
            cada una. Esta concentración describe los candidatos de las fuentes, sin demostrar
            concentración de demanda. Nakano Ku combina superioridad 0,704 con solo 55 anuncios
            y un IC 95 % de [0,629; 0,777], por lo que el efecto debe leerse junto con su precisión.
            """
        ),
        markdown(
            """
            ## Takeaways

            Se recomienda investigar primero los candidatos mostrados y validar la oportunidad con
            búsquedas, reservas, ocupación, conversión, ingresos y capacidad real de captación. Los
            resultados actuales sirven para priorizar investigación comercial; no justifican una
            expansión automática ni una promesa de margen.

            La exploración geográfica añade la ubicación y la brecha de oferta de cada candidato.
            Mantiene los umbrales estadísticos y las comparaciones dentro de ciudad. Las cifras
            narrativas corresponden al build FDAAB53F8317CAD7 y deben revisarse con cada nuevo
            build.
            """
        ),
    ]
    write_notebook("03_executive_eda.ipynb", cells)


if __name__ == "__main__":
    audit_notebook()
    etl_notebook()
    executive_eda_notebook()
