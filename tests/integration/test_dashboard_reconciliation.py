from __future__ import annotations

import pytest


def test_dashboard_summary_and_ranking_reconcile_with_public_exports(
    powerbi_export_fixture,
) -> None:
    from dashboard.data import load_dashboard_dataset
    from dashboard.filters import FilterSelection, apply_listing_filters, apply_opportunity_filters
    from dashboard.presentation import opportunity_table, summary_metrics

    dataset = load_dashboard_dataset(powerbi_export_fixture.directory)
    private_key = dataset.room_types.loc[
        dataset.room_types["room_type"].eq("private_room"), "room_type_key"
    ].iat[0]
    selection = FilterSelection(city_key="madrid", room_type_keys=(private_key,))

    listings = apply_listing_filters(dataset.listings, selection)
    opportunities = apply_opportunity_filters(dataset.opportunities, selection)
    metrics = summary_metrics(listings, opportunities)
    ranking = opportunity_table(dataset, opportunities)

    assert metrics.listing_count == 1
    assert metrics.candidate_count == 1
    assert metrics.median_activity == 1.2
    assert ranking.loc[0, "Rango candidato"] == 1
    assert ranking.loc[0, "Actividad mediana"] == 1.2


def test_dashboard_evidence_reconciles_with_published_result(powerbi_export_fixture) -> None:
    from dashboard.data import load_dashboard_dataset
    from dashboard.presentation import evidence_table

    dataset = load_dashboard_dataset(powerbi_export_fixture.directory)
    table = evidence_table(dataset, dataset.statistics)

    assert len(table) == 1
    assert table.loc[0, "Efecto"] == 0.62
    assert table.loc[0, "Intervalo inferior"] == 0.54
    assert table.loc[0, "Intervalo superior"] == 0.70
    assert table.loc[0, "Valor p ajustado"] == 0.02


@pytest.mark.full_data
def test_real_dashboard_sample_matches_the_power_bi_acceptance(project_root) -> None:
    from dashboard.data import load_dashboard_dataset
    from dashboard.presentation import opportunity_table

    dataset = load_dashboard_dataset(project_root / "data" / "powerbi")
    madrid = dataset.cities.loc[dataset.cities["city_label_es"].eq("Madrid"), "city_key"].iat[0]
    private_room = dataset.room_types.loc[
        dataset.room_types["room_type_label_es"].eq("Habitación privada"), "room_type_key"
    ].iat[0]
    justicia = dataset.neighborhoods.loc[
        dataset.neighborhoods["neighborhood_label"].eq("Justicia"), "neighborhood_key"
    ].iat[0]
    sample = dataset.opportunities.loc[
        dataset.opportunities["city_key"].eq(madrid)
        & dataset.opportunities["room_type_key"].eq(private_room)
        & dataset.opportunities["neighborhood_key"].eq(justicia)
    ]
    row = opportunity_table(dataset, sample).iloc[0]

    assert row["Anuncios"] == 281
    assert row["Cuota con actividad"] == pytest.approx(0.7473309609)
    assert row["Percentil de precio local"] == pytest.approx(0.80859375)
    assert row["Probabilidad de superioridad"] == pytest.approx(0.5652568586)
    assert row["Valor p ajustado"] == pytest.approx(0.02032784077)
    assert row["Rango candidato"] == 1
