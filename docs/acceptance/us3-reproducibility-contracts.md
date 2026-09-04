# Contratos de reproducibilidad de US3

## Alcance

Este bloque cubre T070–T079: gobernanza de la rama, contratos ejecutables, notebooks, orquestación
CLI, validación y publicación transaccional. US3 todavía requiere las tareas de documentación y
aceptación T080–T085 para cerrar el Nivel Esencial.

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
confirmaron el aislamiento actual de clientes NBClient y el presupuesto del ETL. Los fallos
describieron la implementación pendiente: orquestación y validación de notebooks (T075), validación
documental (T078) y orquestación transaccional de `all` (T079).

Tras implementar T075, `tests/integration/test_notebooks.py` aprobó **5 pruebas**: ejecución en el
orden contractual, kernel nuevo por ejecución, ausencia de notebook contractual y reglas narrativas
de título, `tl;dr`, contexto y métodos, conclusiones y `Takeaways`. El presupuesto del flujo completo
solo podrá evaluarse cuando `all` deje de responder `not_implemented`.

Tras implementar T076–T079, la CLI ejecuta suites seleccionadas, notebooks, validación documental y
de artefactos, y el orden completo en un directorio temporal. Se adelantó, con autorización, una
exportación CSV mínima y segura de las ocho tablas para que el flujo pueda validar y publicar el build
sin iniciar el dashboard de US4. Para cumplir el RSS máximo, cada etapa pesada de `all` se ejecuta en
un proceso aislado; la etapa `test` se ejecuta desde el coordinador para no añadir un proceso Python
intermedio durante pytest.

Evidencia final: Ruff aprobado y **64 pruebas aprobadas** en 7 min 19 s. El contrato de rendimiento
aprobó en **4 min 38 s**: ETL ≤60 s, flujo completo ≤5 min y RSS pico ≤2 GB.

La regresión previa a este bloque se verificó de forma separada: **49 pruebas aprobadas** y Ruff sin
incidencias. Ruff también aprobó los cuatro archivos contractuales nuevos.

## Criterio de interpretación

T070–T079 quedan completas y la suite está en verde. US3 permanece abierta hasta completar la
documentación, reproducción Docker, mediciones, conciliación de gobernanza y aceptación T080–T085.
