# Contratos de reproducibilidad de US3

## Alcance

Este bloque cubre exclusivamente T070–T074: gobernanza de la rama y definición ejecutable de los
contratos de reproducibilidad. No implementa el comportamiento descrito por las pruebas; esa labor
corresponde a T075–T079.

## Contratos añadidos

- Los tres notebooks deben ejecutarse en el orden `01`, `02`, `03`, cada uno con un cliente y un
  kernel nuevos, y deben cumplir el contrato narrativo de Markdown y conclusiones explícitas.
- El comando `all` debe ejecutar `inventory`, `audit`, `build`, `analyze`, `export`, `test`,
  `notebooks` y `validate` en ese orden; además, debe ser idempotente y fallar de forma cerrada sin
  sustituir el último resultado aceptado por una publicación parcial.
- La documentación debe estar enlazada, ser visible en español y no contener afirmaciones no
  sustentadas ni datos personales.
- El ETL debe terminar en 60 segundos o menos y el flujo completo en 5 minutos o menos, con un pico
  de RSS máximo de 2 GB. El contrato del contenedor exige 2 vCPU y 4 GB.

## Evidencia TDD

Comando ejecutado desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\integration\test_notebooks.py `
  tests\integration\test_cli_all.py tests\contract\test_documentation.py `
  tests\integration\test_performance.py -q --tb=line
```

Resultado inicial: **2 pruebas aprobadas y 8 fallidas de forma esperada**. Las pruebas aprobadas
confirman el aislamiento actual de clientes NBClient y el presupuesto del ETL. Los fallos describen
la implementación pendiente: orquestación y validación de notebooks (T075), validación documental
(T078) y orquestación transaccional de `all` (T079). El presupuesto del flujo completo solo podrá
evaluarse cuando `all` deje de responder `not_implemented`.

La regresión previa a este bloque se verificó de forma separada: **49 pruebas aprobadas** y Ruff sin
incidencias. Ruff también aprobó los cuatro archivos contractuales nuevos.

## Criterio de interpretación

Los ocho fallos son la línea base roja de TDD, no una aceptación funcional de US3. T070–T074 quedan
completas al versionar y publicar estos contratos; US3 permanecerá abierta hasta implementar y
poner en verde T075–T085.
