# Checklist de aceptación manual — Power BI Nivel Medio

Este documento registra la aceptación manual del informe descrito en el
[contrato Power BI](../specs/001-supply-opportunity-analysis/contracts/powerbi-report.md). No se
marca una comprobación sin evidencia enlazada. Los estados permitidos son `PASS`, `FAIL`, `BLOCKED`
y `N/A` con justificación.

## Identificación de la ejecución

| Campo | Valor |
|---|---|
| Revisor no técnico | Pendiente |
| Revisor técnico | Pendiente |
| Fecha y zona horaria | Pendiente — Europe/Madrid |
| Versión Power BI Desktop | Pendiente |
| Ruta limpia usada como `DataRoot` | Pendiente |
| Build ID / schema version | Pendiente |
| Commit y PR | Pendiente |

## 1. Preparación, licencia y refresh

- [ ] Power BI Desktop gratuito abre el `.pbix` sin solicitar Power BI Pro, Premium o Fabric.
- [ ] La plantilla `.pbit` no contiene datos importados y solicita `DataRoot` al abrirse.
- [ ] `DataRoot` es la única ruta configurable y apunta a una copia limpia de `data/powerbi/`.
- [ ] El refresh carga exactamente los ocho CSV requeridos sin rutas personales ni rutas internas
  del contenedor.
- [ ] La ausencia de un archivo, un schema major incompatible o un release gate distinto de `pass`
  produce un mensaje claro y bloquea el refresh.
- [ ] Se registran captura del refresh, versión de Desktop, duración y resultado.

## 2. Modelo y conciliación

- [ ] Las dimensiones Ciudad, Barrio y Tipología tienen claves únicas y relaciones uno-a-muchos,
  unidireccionales, hacia los hechos aplicables.
- [ ] `Build Control` y la tabla de medidas están desconectadas.
- [ ] Las claves técnicas están ocultas y no aparecen en visuales, tooltips, texto alternativo ni
  exportaciones normales.
- [ ] No existen nombres de anuncio/anfitrión, IDs crudos ni coordenadas por anuncio en el modelo.
- [ ] `Diferencia de conciliación` permanece en cero al retirar todos los filtros.
- [ ] Filas importadas, anuncios distintos, segmentos y hashes coinciden con `build_control.csv` y
  con la verificación externa.

## 3. Página “Resumen ejecutivo”

- [ ] La página responde antes de interactuar dónde conviene investigar captación primero.
- [ ] Presenta `Anuncios analizables` y `Segmentos candidatos` con población y denominador claros.
- [ ] Muestra como máximo tres candidatos válidos o el estado explícito “menos de tres cualificados”.
- [ ] Separa evidencia de actividad histórica, cuota de oferta, precio local, escala y confianza.
- [ ] La recomendación es provisional, está en español y no presenta causalidad, demanda, ocupación,
  ingresos ni margen como observados.
- [ ] Las cautelas esenciales son visibles sin depender del hover.

## 4. Página “Oportunidades de captación”

- [ ] Los slicers globales se limitan a Ciudad, Tipología y Estado de evidencia y ocupan una posición
  consistente.
- [ ] La vista ranking permite tomar la decisión completa aunque Azure Maps esté deshabilitado o sin
  conexión.
- [ ] El mapa, cuando funciona, usa centroides agregados y nunca puntos de anuncios individuales.
- [ ] Ranking y mapa comunican `candidate`, `consolidated`, `watch` e `insufficient_evidence` también
  mediante texto o iconos, no solo color.
- [ ] La selección de barrio ocurre mediante ranking/mapa y el drillthrough abre el detalle correcto.

## 5. Página “Detalle y confianza”

- [ ] Identifica el segmento sin mostrar IDs de anuncio o anfitrión.
- [ ] Expone tamaño muestral, positivos, ceros/faltantes, mediana, IQR y mediana positiva.
- [ ] Expone efecto, IC 95 %, valores crudo/ajustado, familia de corrección y sensibilidad.
- [ ] Muestra flags de calidad, exclusiones, población, denominador y limitación no causal.
- [ ] Muestra build ID, schema, fecha de generación, filas fuente/importadas y diferencia de
  conciliación.
- [ ] El botón Volver conserva únicamente el contexto compatible.

## 6. Interacción y reset

- [ ] Los tres slicers globales afectan solo a páginas y medidas con la misma semántica.
- [ ] Elegibilidad y exclusiones inválidas están bloqueadas y no pueden desactivarse accidentalmente.
- [ ] Reset devuelve filtros y selecciones al estado inicial documentado.
- [ ] Navegación, drillthrough y regreso funcionan mediante ratón y teclado.
- [ ] Ningún tooltip contiene la única copia de una conclusión o advertencia obligatoria.

## 7. Accesibilidad y claridad ejecutiva

- [ ] Texto y elementos esenciales alcanzan contraste mínimo 4,5:1.
- [ ] Cada visual significativo dispone de texto alternativo en español; es dinámico cuando cambia
  el significado con el filtro.
- [ ] El orden de tabulación sigue: filtros, hallazgo principal, evidencia, detalle y navegación.
- [ ] Los títulos expresan una pregunta o conclusión de negocio y evitan nombres de tipos de gráfico.
- [ ] Cada página conserva una sola decisión principal y un número limitado de visuales.
- [ ] La página sigue siendo comprensible al simular deficiencias de percepción del color.

## 8. Cotejo de medidas

Para cada muestra se adjuntan filtro, valor Power BI, valor recalculado desde CSV/Parquet, diferencia
y evidencia. No se acepta redondeo que cambie la conclusión.

| Medida | Contexto/filtro | Power BI | Control externo | Diferencia | Estado/evidencia |
|---|---|---:|---:|---:|---|
| Anuncios analizables | Pendiente | — | — | — | Pendiente |
| Segmentos candidatos | Pendiente | — | — | — | Pendiente |
| Cuota activa histórica | Pendiente | — | — | — | Pendiente |
| Actividad histórica mediana | Pendiente | — | — | — | Pendiente |
| Precio local mediano | Pendiente | — | — | — | Pendiente |
| Cuota de oferta | Pendiente | — | — | — | Pendiente |
| Efecto de actividad | Pendiente | — | — | — | Pendiente |
| Diferencia de conciliación | Sin filtros | — | 0 | — | Pendiente |

## 9. Prueba no asistida de tres minutos

- [ ] Se entrega al revisor únicamente el informe y una frase de objetivo, sin instrucciones de uso.
- [ ] El cronómetro comienza al abrir la primera página ya refrescada.
- [ ] En menos de tres minutos identifica hasta tres oportunidades que realmente cumplen las reglas.
- [ ] Para cada oportunidad explica al menos una cautela de evidencia o calidad.
- [ ] Si hay menos de tres candidatos, reconoce correctamente ese estado sin inventar alternativas.
- [ ] Se registran tiempo, respuestas literales resumidas, errores de interpretación y correcciones.

| Revisor | Inicio | Fin | Duración | Resultado | Evidencia |
|---|---|---|---:|---|---|
| Pendiente | — | — | — | `BLOCKED` hasta disponer del `.pbix` | Pendiente |

## 10. Decisión de release

- [ ] No queda ningún `FAIL` ni `BLOCKED`.
- [ ] Las incidencias corregidas enlazan commit y nueva evidencia.
- [ ] Revisor técnico y revisor no técnico firman la aceptación.
- [ ] La evidencia final se enlaza en `docs/acceptance/powerbi-uat.md` y en el PR de US4.

**Estado global actual**: `BLOCKED` — el checklist está preparado, pero su ejecución requiere los
artefactos `.pbix`/`.pbit` de T095–T101.
