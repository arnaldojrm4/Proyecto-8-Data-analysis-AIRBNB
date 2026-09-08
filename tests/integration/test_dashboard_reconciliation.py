from __future__ import annotations


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

