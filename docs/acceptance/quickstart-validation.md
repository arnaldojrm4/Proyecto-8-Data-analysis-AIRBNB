# Validación del quickstart — T108

## Entorno limpio

- Fecha: 2026-09-07, Europe/Madrid.
- Checkout: worktree temporal separado, HEAD detached desde `feat/medium-powerbi-report`.
- Docker Engine: activo; imagen construida desde `python:3.13-slim` y `uv.lock`.
- Fuentes: seis CSV versionados, 220.031 registros y build `FDAAB53F8317CAD7`.

## Comandos y resultados

| Comando del quickstart | Resultado |
|---|---|
| `git branch --show-current` / `git status --short` | Checkout limpio y detached para aceptación |
| `docker compose build` | PASS |
| `docker compose run --rm pipeline inventory` | PASS; 6 archivos, 220.031 filas |
| `docker compose run --rm pipeline test --suite unit` | PASS; 26/26 |
| `docker compose run --rm pipeline test --suite contract` | PASS; 43/43 |
| `docker compose run --rm pipeline all --log-format json` | PASS; schema `1.0.0`, 0 errores/avisos |
| `docker compose run --rm pipeline notebooks --log-format json` | PASS; 3/3 |
| `docker compose run --rm pipeline validate --log-format json` | PASS; 25 controles, 0 errores/avisos |

## Incidencias descubiertas y corregidas

La primera ejecución contractual del checkout limpio produjo 9 fallos y 4 errores porque la imagen
no copiaba `powerbi/`. Tras añadir `COPY powerbi ./powerbi`, quedaron tres fallos: `.dockerignore`
seguía excluyendo `.pbix` y `.pbit`. Los commits `048bcb1` y `706c96d` corrigen cada causa por
separado. La repetición final aprobó 43/43 contratos.

Ruff detectó orden no canónico en los imports de los tres notebooks y en el nuevo contrato del
verificador. Se corrigieron únicamente esos bloques; la estructura `nbformat` v4 permanece válida y
las copias ejecutadas se regeneraron desde los fuentes corregidos.

## Conclusión

El quickstart es ejecutable desde cero con Docker. No necesita rutas personales, estado previo de
Python, Power BI Service ni una licencia de pago. Los datos derivados se regeneran y no se versionan.
