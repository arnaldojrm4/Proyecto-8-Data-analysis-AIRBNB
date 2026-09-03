from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def canonical_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "listing_key": ["madrid:1", "madrid:2"],
            "city_key": ["madrid", "madrid"],
            "listing_id": [1, 2],
            "host_id": [10, 20],
            "neighborhood": ["Centro", "Centro"],
            "neighborhood_key": ["madrid:centro", "madrid:centro"],
            "room_type": ["private_room", "entire_home_apt"],
            "price": [75.0, 140.0],
            "minimum_nights": [2, 3],
            "number_of_reviews": [0, 8],
            "reviews_per_month_observed": [pd.NA, 1.2],
            "activity_proxy": [0.0, 1.2],
            "activity_proxy_derived_zero": [True, False],
            "activity_proxy_is_analyzable": [True, True],
        }
    )
