# Aceptación del Nivel Avanzado

**Feature:** `002-advanced-dashboard`  
**Fecha de corte:** 2026-09-08  
**Estado:** validación técnica aprobada; recorrido humano final indicado al cierre.

## Entrega y trazabilidad

| Alcance | Requisitos | Implementación | Evidencia |
|---|---|---|---|
| Vistas y filtros coordinados | FR-001–FR-013 | `dashboard/app.py`, `filters.py`, vistas | unitarias, AppTest y conciliación |
| Hipótesis y cautelas | FR-014–FR-023 | vista `evidence`, tablas y figuras precalculadas | contratos estadísticos y AppTest H1–H3 |
| Build confiable | FR-024–FR-027 | `dashboard/data.py` | ocho códigos de rechazo y recuperación |
| Privacidad y descargas | FR-028–FR-029 | listas positivas de presentación | rechazo `restricted_export_field` |
| Portabilidad y operación | FR-030–FR-032, FR-034 | imagen única, Compose y guías | `advanced-dashboard-docker.md` |
| Accesibilidad | FR-033 | controles nativos, etiquetas, ranking alternativo y tema | contrato WCAG y revisión proxy |

## Resultados medibles

- **SC-002/SC-004:** las muestras automatizadas de KPIs, tablas, filtros y evidencia concilian con los
  CSV aprobados; no se recalculan pruebas por filtro.
- **SC-003:** las fichas publicadas incluyen población, método, muestra, efecto, intervalo, valor p
  ajustado, corrección, sensibilidad y cautela causal.
- **SC-005:** sobre el conjunto de referencia de 220.031 anuncios, AppTest midió una carga inicial de
  1,457 s y p95 de 0,216 s en 20 acciones de filtro; el umbral era 2 s.
- **SC-006/SC-011:** la imagen compartida ejecuta pipeline o Streamlit mediante entrypoints distintos;
  el servicio web consume `data/powerbi` como solo lectura y arrancó en 4,14 s.
- **SC-007:** archivo ausente, esquema incompatible, gate rechazado, build mixto, recuento incorrecto,
  clave duplicada, relación huérfana y campo de descarga restringido producen bloqueo estable.
- **SC-008:** tablas y descargas usan listas positivas sin nombres, IDs originales, claves técnicas ni
  coordenadas de anuncios.
- **SC-010:** el ranking tabular conserva la lectura principal aunque el mapa no se represente.
- **SC-012:** Ruff aprobó y la regresión completa del host finalizó con 138 pruebas aprobadas en
  318,14 s. Dentro de la imagen se aprobaron 128, se omitieron 2 smoke tests anidados y se excluyeron
  las 8 pruebas de datos completos ya cubiertas en host. El pipeline contenido finalizó con 0 errores.

## Accesibilidad y vista estrecha

Los controles Streamlit tienen etiquetas visibles y orden lógico: navegación, ciudad, tipología,
barrio, evidencia y restablecimiento. El flujo crítico dispone de controles nativos de teclado y el
mapa nunca es la única vía de lectura. El layout ancho de Streamlit reorganiza columnas en anchuras
reducidas y mantiene las tablas desplazables.

El contrato de tema verifica WCAG AA para texto normal. Ratios calculados: texto/fondo 14,10:1,
texto/fondo secundario 12,49:1, primario/fondo 4,85:1 y blanco/primario 5,28:1. Se oscureció el color
primario de `#C44A32` a `#BC432E` al detectar que el primero alcanzaba solo 4,42:1.

La inspección visual controlada mediante navegador integrado no estuvo disponible en el entorno de
ejecución. AppTest cubre orden, etiquetas, navegación, fallback, estados y ausencia de excepciones; la
prueba humana de teclado, foco y comprensión se conserva como cierre explícito y no se sustituye por
una afirmación automática.

## Conciliación y limitaciones

La fuente única de verdad son los ocho CSV de `data/powerbi`, identificados por `build_id` y gate
`pass`. Streamlit y Power BI son consumidores; el pipeline Python es el único productor de reglas,
oportunidades y estadística. Las fuentes no acreditan demanda, reservas, ocupación, ingresos,
rentabilidad, moneda o actualidad comercial.

La muestra Madrid–Justicia–Habitación privada se leyó mediante la proyección real del panel y se
comparó con el cotejo independiente conservado para Power BI. Las diferencias fueron cero: 281
anuncios, cuota activa 0,7473309609, percentil local de precio 0,80859375, probabilidad de
superioridad 0,5652568586, valor p ajustado 0,02032784077 y rango candidato 1.
