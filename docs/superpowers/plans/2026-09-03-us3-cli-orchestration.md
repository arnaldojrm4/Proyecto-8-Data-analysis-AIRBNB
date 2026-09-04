# US3 CLI Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar los comandos `test`, `notebooks`, `validate` y `all` con publicación segura.

**Architecture:** `validation.py` contiene validaciones puras; `cli.py` despacha etapas y publica
raíces temporales solo tras una validación correcta. Una exportación CSV mínima desbloquea el flujo
sin adelantar el dashboard.

**Tech Stack:** Python 3.13, pytest, Pandas, nbclient, PyArrow y argparse.

**Spec:** `docs/superpowers/specs/2026-09-03-us3-cli-orchestration-design.md`

## Global Constraints

- Mantener resultados y documentación visibles en español.
- No exponer nombres, IDs raw ni coordenadas en exportaciones o logs.
- Ejecutar las ocho etapas en el orden contractual y conservar el último build aceptado ante fallo.
- No iniciar artefactos de dashboard; la exportación adelantada solo satisface la dependencia de T079.

---

### Task 1: Pruebas y comando `test` (T076)

**Files:** `tests/integration/test_cli_commands.py`, `src/airbnb_supply_analysis/cli.py`

- [X] Escribir una prueba que simule pytest y compruebe selección, resumen y código no cero.
- [X] Ejecutarla en rojo por ausencia de `_test`.
- [X] Implementar `_test(args) -> dict[str, Any]` con `subprocess.run` y conteos de la salida pytest.
- [X] Ejecutar la prueba y Ruff; realizar commit atómico.

### Task 2: Comando `notebooks` (T077)

**Files:** `tests/integration/test_cli_commands.py`, `src/airbnb_supply_analysis/cli.py`

- [X] Escribir pruebas de salida bajo `executed_notebooks` y fallo narrativo con código 7.
- [X] Ejecutarlas en rojo.
- [X] Implementar `_notebooks(args)` usando `execute_notebooks` y `validate_notebook_narrative`.
- [X] Ejecutar pruebas y Ruff; realizar commit atómico.

### Task 3: Validación y exportación mínima (T078 + dependencia autorizada)

**Files:** `tests/contract/test_documentation.py`, `tests/integration/test_cli_commands.py`,
`src/airbnb_supply_analysis/validation.py`, `src/airbnb_supply_analysis/cli.py`

- [X] Ejecutar los contratos rojos de documentación y validación.
- [X] Implementar `validate_documentation_tree(root) -> dict[str, object]` y validaciones de
  artefactos existentes sin reconstrucción.
- [X] Implementar exportación mínima segura con ocho CSV y control de hashes.
- [X] Ejecutar contratos, Ruff y realizar commit atómico.

### Task 4: Transacción `all` (T079)

**Files:** `tests/integration/test_cli_all.py`, `tests/integration/test_performance.py`,
`src/airbnb_supply_analysis/cli.py`

- [X] Ejecutar contratos rojos de orden, idempotencia y fallo cerrado.
- [X] Implementar argumentos temporales, despacho secuencial, publicación final y limpieza ante error.
- [X] Ejecutar los contratos y el flujo completo; verificar rendimiento.
- [X] Actualizar tareas, aceptación y gestión de proyecto; realizar commit y publicar la PR.
