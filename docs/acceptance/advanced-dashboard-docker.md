# Aceptación del panel avanzado en Docker

**Fecha:** 2026-09-08  
**Rama:** `002-advanced-dashboard`  
**Imagen compartida:** `airbnb-supply-analysis:advanced`

## Recorrido validado

1. `docker compose build pipeline` construyó correctamente la imagen única usada por `pipeline` y
   `dashboard`.
2. `docker compose run --rm pipeline all --log-format json` finalizó con `status=success`,
   `error_count=0`, `schema_version=1.0.0` y build de datos `FDAAB53F8317CAD7`.
3. `docker compose up -d --force-recreate dashboard` inició Streamlit sin ejecutar de nuevo el
   pipeline.
4. `http://localhost:8501/_stcore/health` respondió HTTP 200 en 4,14 segundos y la página raíz
   respondió HTTP 200.
5. Docker declaró el contenedor `healthy`. El consumo puntual observado fue 93,45 MiB de un límite
   de 1 GiB, con el volumen `data/powerbi` montado como solo lectura.

El recorrido integral del pipeline duró aproximadamente 226 segundos en el equipo de validación.
La cifra es evidencia operativa de esta ejecución, no una garantía de rendimiento en otros equipos.

## Incidencia detectada y resolución

La primera ejecución integral falló únicamente en el contrato documental: el README enlazaba
`output/pdf/guia-estudio-airbnb.pdf`, pero la imagen no contenía el archivo. Se incorporó ese PDF de
forma explícita al `Dockerfile`, sin copiar salidas temporales, y se añadió un contrato que exige que
los dos servicios declaren la misma imagen. La repetición completa quedó aprobada.

## Criterio de aceptación

El panel puede construirse, arrancarse, comprobarse y reproducirse con los comandos documentados,
sin rutas personales, sin licencia de Power BI y sin permisos de escritura sobre los CSV publicados.

## Repetición final sin caché

Tras integrar robustez, accesibilidad y documentación se repitió la puerta completa:

- `docker compose build --no-cache pipeline`: aprobado;
- `docker compose run --rm pipeline all --log-format json`: `status=success`, 0 errores y unos 203 s;
- suite explícita dentro de la imagen: 125 aprobadas, 2 omitidas por evitar Docker dentro de Docker y
  8 de datos completos cubiertas en el host;
- panel recreado desde `airbnb-supply-analysis:advanced`: HTTP 200 en 4,07 s y estado `healthy`;
- usuario efectivo: `dashboard`; consumo puntual: 96,79 MiB de un límite de 1 GiB.
