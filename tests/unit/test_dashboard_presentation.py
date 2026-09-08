from __future__ import annotations


def test_summary_metrics_are_derived_from_the_filtered_population() -> None:
    import pandas as pd

    from dashboard.presentation import summary_metrics

    listings = pd.DataFrame(
        {
            "neighborhood_key": ["centro", "centro", "sur"],
            "activity_proxy": [0.0, 1.0, 2.0],
            "price": [50.0, 100.0, 150.0],
        }
    )
    opportunities = pd.DataFrame({"opportunity_label": ["candidate", "observation"]})

    metrics = summary_metrics(listings, opportunities)

    assert metrics.listing_count == 3
    assert metrics.neighborhood_count == 2
    assert metrics.candidate_count == 1
    assert metrics.median_activity == 1.0
    assert metrics.median_price == 100.0


def test_opportunity_table_uses_labels_and_a_strict_safe_allowlist(
    powerbi_export_fixture,
) -> None:
    from dashboard.data import load_dashboard_dataset
    from dashboard.presentation import opportunity_table

    dataset = load_dashboard_dataset(powerbi_export_fixture.directory)
    table = opportunity_table(dataset)

    assert table.loc[0, "Ciudad"] == "Madrid"
    assert table.loc[0, "Barrio"] == "Centro"
    assert table.loc[0, "Tipología"] == "Habitación privada"
    assert table.loc[0, "Rango candidato"] == 1
    normalized = {column.casefold() for column in table.columns}
    assert not any("_key" in column for column in normalized)
    assert not any("latitud" in column or "longitud" in column for column in normalized)
    assert "listing_key" not in normalized


def test_opportunity_csv_contains_only_the_visible_safe_projection(
    powerbi_export_fixture,
) -> None:
    from dashboard.data import load_dashboard_dataset
    from dashboard.presentation import opportunity_csv, opportunity_table

    table = opportunity_table(load_dashboard_dataset(powerbi_export_fixture.directory))
    payload = opportunity_csv(table).decode("utf-8")

    assert payload.startswith("Ciudad,Barrio,Tipología")
    assert "listing_key" not in payload
    assert "centroid_latitude" not in payload

