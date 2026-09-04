from __future__ import annotations

import importlib
from pathlib import Path

import pytest


def _validation_api():
    validation = importlib.import_module("airbnb_supply_analysis.validation")
    return validation.validate_documentation_tree, validation.DocumentationContractError


def test_project_documentation_is_spanish_linked_and_privacy_safe(project_root: Path) -> None:
    validate_documentation_tree, _ = _validation_api()

    report = validate_documentation_tree(project_root)

    assert report["checked_files"] >= 8
    assert report["broken_local_links"] == []
    assert report["unsupported_claims"] == []
    assert report["pii_findings"] == []


def test_documentation_rejects_unsupported_claims_and_personal_data(tmp_path: Path) -> None:
    validate_documentation_tree, contract_error = _validation_api()
    docs = tmp_path / "docs"
    docs.mkdir()
    (tmp_path / "README.md").write_text(
        "# Informe\n\nEste resultado demuestra demanda. Contacto: persona@example.com.\n",
        encoding="utf-8",
    )

    with pytest.raises(contract_error):
        validate_documentation_tree(tmp_path)


def test_documentation_rejects_broken_local_links(tmp_path: Path) -> None:
    validate_documentation_tree, contract_error = _validation_api()
    (tmp_path / "README.md").write_text(
        "# Proyecto reproducible\n\n[Guía](docs/no-existe.md)\n",
        encoding="utf-8",
    )

    with pytest.raises(contract_error, match="enlace"):
        validate_documentation_tree(tmp_path)
