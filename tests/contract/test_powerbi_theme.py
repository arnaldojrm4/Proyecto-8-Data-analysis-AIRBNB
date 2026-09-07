"""Contrato de accesibilidad y semántica visual del tema Power BI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THEME_PATH = PROJECT_ROOT / "powerbi" / "theme.json"
STATUS_CONTRACT = {
    "candidate": (0, "Candidato"),
    "consolidated": (1, "Consolidado"),
    "watch": (2, "En observación"),
    "insufficient": (3, "Evidencia insuficiente"),
}


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


@pytest.fixture(scope="module")
def theme() -> dict[str, object]:
    assert THEME_PATH.is_file(), "Falta el tema versionado de Power BI"
    return json.loads(THEME_PATH.read_text(encoding="utf-8"))


def test_theme_exists_and_uses_supported_powerbi_keys(theme: dict[str, object]) -> None:
    assert theme["name"] == "Airbnb — oportunidades de captación accesibles"
    assert theme["background"] == "#FFFFFF"
    assert theme["foreground"] == "#1A1A1A"
    assert len(theme["dataColors"]) >= 8
    assert "visualStyles" in theme
    assert "textClasses" in theme


def test_all_semantic_status_colors_meet_aa_contrast_on_white(
    theme: dict[str, object],
) -> None:
    for status, (color_index, _) in STATUS_CONTRACT.items():
        assert _contrast_ratio(theme["dataColors"][color_index], "#FFFFFF") >= 4.5, status


def test_status_is_never_encoded_only_by_color(theme: dict[str, object]) -> None:
    icons = theme["icons"]
    assert set(STATUS_CONTRACT).issubset(icons)
    cues = {
        (label, icons[status]["description"], icons[status]["url"])
        for status, (_, label) in STATUS_CONTRACT.items()
    }
    assert len(cues) == len(STATUS_CONTRACT)
    assert all(
        label in description and url.startswith("data:image/svg+xml")
        for label, description, url in cues
    )


def test_text_classes_meet_aa_contrast(theme: dict[str, object]) -> None:
    for class_name, definition in theme["textClasses"].items():
        color = definition.get("color", theme["foreground"])
        assert _contrast_ratio(color, theme["background"]) >= 4.5, class_name
