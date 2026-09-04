# Reproducción Docker de US3

## Contrato

El servicio `pipeline` usa `Dockerfile`, monta `data/raw/` como solo lectura y limita recursos a 2
vCPU y 4 GB mediante `compose.yaml`.

```powershell
docker compose build
docker compose run --rm pipeline all --log-format json
```

La aceptación requiere código 0, resumen JSON exitoso, notebooks ejecutados y publicación solo tras
validación.

## Evidencia aprobada — 2026-09-04

- Docker Desktop 4.89.0, Engine 29.7.2, API 1.55 y Compose 5.5.0 sobre Linux/WSL2.
- Configuración efectiva: 2 vCPU, 4 GB y `data/raw/` en solo lectura.
- Suite independiente: 65 aprobadas, 1 omitida y 0 fallos en 495,91 s. La prueba omitida comprueba
  Docker desde host y no es aplicable dentro del propio contenedor.
- Test de presupuesto `all`: aprobado en 203,21 s; verificó duración <=300 s y RSS <=2 GB.
- Ejecución final `all`: código 0, `status=success`, build `FDAAB53F8317CAD7` y 201,34 s.
- Publicación: 3 Parquet procesados, 8 CSV/control para Power BI, 5 visualizaciones, 7 archivos de
  calidad y 3 notebooks ejecutados sin salidas de error.
- Limpieza transaccional: 0 directorios `.airbnb-supply-publish` residuales.

La sesión Codex creó los directorios de salida del worktree con ACL incompatibles con Docker
Desktop. Para aislar esa incidencia del entorno se usó un override temporal que mantuvo los mismos
destinos internos y límites, redirigiendo únicamente los tres bind mounts de salida a un directorio
temporal accesible. El código validado soporta tanto el renombrado atómico de host como el reemplazo
con rollback requerido por raíces de volumen no renombrables.

T082 queda aprobada. La puerta Esencial conserva pendiente únicamente la integración formal de los
PR y el cierre de T085.
