# Evidencia final de release — T109

## Resultado consolidado

**PASS** para los niveles Esencial y Medio. La validación se realizó desde un checkout limpio con
los seis datasets originales.

| Control | Resultado aceptado |
|---|---|
| Ruff | PASS |
| Unitarias Docker | 26 aprobadas |
| Contractuales Docker | 43 aprobadas |
| Integración Docker | 25 aprobadas, 1 omitida por Docker CLI no disponible dentro del contenedor |
| Notebooks | 3 ejecutados de principio a fin |
| Pipeline `all` | PASS, 0 errores, 0 avisos |
| Validación de artefactos | PASS, 25 controles |
| Verificador Power BI | PASS; hashes, privacidad y conciliación cero |
| Validador PBIR oficial | 0 errores, 0 advertencias |
| Binarios Power BI | `.pbix` y `.pbit` válidos; plantilla sin datos importados |

La última ejecución unificada sobre el HEAD del PR #10 terminó con **94 aprobadas, 1 omitida y 0
fallos**. Se ejecutó después de cerrar las instancias de Power BI que producían contención.

## Rendimiento

El primer pase del test de flujo completo midió 302,99 s y falló el límite de 300 s durante varias
ejecuciones pesadas consecutivas. No hubo fallo funcional. Sin cambiar código ni umbral, la
repetición aislada aprobó en **298,37 s (4:58)**. Se conserva esta incidencia como evidencia de que
el margen de rendimiento es estrecho y puede variar con la contención del equipo.

El límite se mantiene en cinco minutos; no se amplió para obtener un resultado verde. El contenedor
declara 2 vCPU y 4 GB, y el test mantiene el RSS por debajo de 2 GB.

## Identidad y conciliación

- Build: `FDAAB53F8317CAD7`.
- Schema: `1.0.0`.
- Fuentes: 6 archivos / 220.031 filas.
- Anuncios importados y claves distintas: 220.031 / 220.031.
- Segmentos: 1.497; candidatos: 28.
- Diferencia de conciliación: 0.

## Evidencias relacionadas

- [Quickstart limpio](quickstart-validation.md)
- [Conciliación Power BI](powerbi-reconciliation.md)
- [UAT y accesibilidad](powerbi-uat.md)
- [Aceptación Nivel Medio](medium-level.md)
- [Rendimiento Esencial](performance.md)

Las conclusiones siguen limitadas a actividad histórica de reseñas y oferta relativa. No convierten
el proxy en demanda, reservas, ocupación, liquidez, ingreso, margen o causalidad.

El PR [#10](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/10) fue integrado en
`main` mediante `12466b3abd73d13f685546183aafbb0ad21f8c01`; el issue #6 y ambos elementos del
Project #2 quedaron en `Done`.
