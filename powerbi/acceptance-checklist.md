# Checklist de aceptación manual — Power BI Nivel Medio

Ejecución cerrada el 2026-09-07 (Europe/Madrid) conforme a la
[guía Power BI](README.md) y la
[aceptación del Nivel Medio](../docs/acceptance/medium-level.md).

| Campo | Valor |
|---|---|
| Revisor funcional | Codex, prueba proxy no asistida |
| Revisor técnico | Contratos automatizados + verificación externa |
| Power BI Desktop | x64 `2.157.879.0 (26.08)` |
| Build / schema | `FDAAB53F8317CAD7` / `1.0.0` |
| DataRoot de prueba | Copia temporal limpia de `data/powerbi/` |
| Issue / PR | [#6](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/6) / [#10](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/10) |

## Preparación, modelo y conciliación

- [x] Desktop gratuito abre y refresca el informe sin Power BI Service ni licencia de pago.
- [x] La plantilla `.pbit` no contiene `DataMashup`, conserva `DataRoot` obligatorio y no incluye datos importados.
- [x] Los ocho CSV, release gate, schema major, hashes, filas y privacidad aprueban.
- [x] El modelo tiene dimensiones únicas y relaciones uno-a-muchos unidireccionales.
- [x] Build Control y Measures están desconectadas; las claves técnicas permanecen ocultas.
- [x] No hay nombres, IDs crudos ni coordenadas individuales.
- [x] Filas importadas y claves distintas son 220.031; la diferencia de conciliación es cero.

## Páginas y decisión

- [x] `Resumen ejecutivo` responde dónde investigar primero y muestra como máximo tres candidatos por ciudad.
- [x] `Oportunidades de captación` mantiene slicers coherentes y un ranking utilizable si el mapa no carga.
- [x] `Detalle y confianza` muestra muestra, distribución, efecto, IC, valor ajustado, sensibilidad, calidad y build.
- [x] Reset, navegación, drillthrough y retorno están declarados en PBIR.
- [x] Ninguna conclusión obligatoria depende de un tooltip.

## Accesibilidad

- [x] El contraste del tema es ≥ 4,5:1 y los estados usan texto además de color.
- [x] Todos los visuales tienen texto alternativo en español y orden de tabulación.
- [x] Las cautelas esenciales son visibles y los títulos expresan decisiones de negocio.

## Cotejo de medidas

| Medida | Contexto | Power BI | Control CSV | Diferencia |
|---|---|---:|---:|---:|
| Anuncios analizables | Global | 220.031 | 220.031 | 0 |
| Segmentos candidatos | Global | 28 | 28 | 0 |
| Cuota activa histórica | Global | 0,7533150226 | 0,7533150226 | 0 |
| Anuncios del segmento | Madrid–Justicia–Privada | 281 | 281 | 0 |
| Posición de precio local | Madrid–Justicia–Privada | 0,80859375 | 0,80859375 | 0 |
| Efecto de actividad | Madrid–Justicia–Privada | 0,5652568586 | 0,5652568586 | 0 |
| Valor ajustado | Madrid–Justicia–Privada | 0,02032784077 | 0,02032784077 | 0 |
| Diferencia de conciliación | Sin filtros | 0 | 0 | 0 |

## UAT y release

- [x] La revisión proxy recibió solo el objetivo y las capturas.
- [x] Identificó tres oportunidades válidas de Nueva York en 10,07 s y expresó la cautela de proxy histórico/no causalidad.
- [x] Se registraron incidencias, correcciones y fallback.
- [x] No queda ningún `FAIL` ni `BLOCKED` para el uso local educativo.

**Estado global: PASS.** Evidencia detallada en
[conciliación](../docs/acceptance/powerbi-reconciliation.md),
[UAT](../docs/acceptance/powerbi-uat.md) y
[aceptación del Nivel Medio](../docs/acceptance/medium-level.md). La UAT es una revisión proxy y no
sustituye una prueba formal con directivos antes de un despliegue real.
