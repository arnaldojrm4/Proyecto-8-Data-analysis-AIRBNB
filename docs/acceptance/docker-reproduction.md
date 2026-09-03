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

## Evidencia de esta sesión — bloqueada

El 2026-09-03, `docker version --format '{{.Server.Version}}'` no pudo acceder a
`C:\Users\Arnal\.docker\config.json` ni al daemon `npipe:////./pipe/docker_engine`. No hay versión
de servidor, duración ni salida de contenedor que pueda afirmarse como válida.

## Acción para desbloquear

1. Iniciar Docker Desktop y confirmar que el daemon está disponible.
2. Ejecutar `docker version` y registrar Client y Server.
3. Ejecutar los comandos del contrato desde la raíz.
4. Registrar duración, resumen JSON y código de salida.
5. Sustituir este bloqueo por evidencia aprobada y cerrar T082.

US4 permanece bloqueada mientras falte esta evidencia.
