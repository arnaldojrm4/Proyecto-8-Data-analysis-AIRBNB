# Quickstart: Panel avanzado interactivo y portable

## Prerrequisitos

- Docker Desktop con el daemon activo.
- Las seis fuentes registradas presentes en `data/raw/`.
- Puertos locales permitidos; el valor predeterminado del panel es `8501`.

## Recorrido contenido

Desde la raíz del repositorio:

```powershell
docker compose build
docker compose run --rm pipeline all --log-format json
docker compose up -d dashboard
```

Resultado esperado:

- el pipeline termina con estado correcto y publica ocho CSV;
- `docker compose ps` muestra `dashboard` como saludable;
- `http://localhost:8501` abre el resumen ejecutivo sin editar rutas.

Para finalizar:

```powershell
docker compose down
```

## Recorrido host para desarrollo

```powershell
uv sync --locked --group dev
uv run --locked airbnb-supply all --log-format json
uv run --locked streamlit run dashboard/app.py
```

## Validación funcional

1. Seleccionar una ciudad y confirmar que tipologías y barrios solo contienen valores compatibles.
2. Seleccionar varias tipologías y comprobar que indicadores, ranking y tabla usan la misma población.
3. Abrir un candidato y rastrear muestra, efecto, intervalo, valor ajustado y sensibilidad.
4. Consultar una asociación y confirmar que el texto niega causalidad, demanda e ingresos.
5. Restablecer filtros y comprobar que desaparecen selecciones dependientes.
6. Deshabilitar o ignorar el mapa y obtener el mismo primer candidato mediante el ranking.
7. Descargar resultados y comprobar que no aparecen claves técnicas ni campos restringidos.

## Validación automatizada

```powershell
uv run --locked pytest tests/unit -q
uv run --locked pytest tests/contract -q
uv run --locked pytest tests/integration/test_dashboard_app.py tests/integration/test_dashboard_reconciliation.py -q
uv run --locked ruff check .
docker compose config --quiet
```

La aceptación final añade el smoke test real del servicio cuando Docker está disponible.

## Recuperación esperada

Si el panel indica que falta o no está aprobado el build:

```powershell
docker compose run --rm pipeline all --log-format json
```

Reiniciar después `dashboard`. No editar manualmente los CSV ni cambiar el estado de publicación.

## Límites de la validación

El recorrido prueba ejecución local o en una red controlada. No autoriza exposición pública. Los datos
siguen sin fecha de snapshot, licencia, procedencia original ni moneda confirmadas; el panel no demuestra
demanda, reservas, ocupación, ingresos, margen o causalidad.

