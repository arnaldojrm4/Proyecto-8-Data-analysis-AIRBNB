from __future__ import annotations

import tomllib
from pathlib import Path


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    lighter, darker = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_dashboard_theme_colors_meet_wcag_aa_for_normal_text(project_root: Path) -> None:
    config = tomllib.loads((project_root / ".streamlit" / "config.toml").read_text("utf-8"))
    theme = config["theme"]

    assert _contrast(theme["textColor"], theme["backgroundColor"]) >= 4.5
    assert _contrast(theme["textColor"], theme["secondaryBackgroundColor"]) >= 4.5
    assert _contrast(theme["primaryColor"], theme["backgroundColor"]) >= 4.5
    assert _contrast("#FFFFFF", theme["primaryColor"]) >= 4.5
