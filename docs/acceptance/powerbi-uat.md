# UAT y accesibilidad Power BI — T104

## Prueba de tres minutos

**Resultado: PASS como revisión proxy reproducible.** El revisor fue Codex actuando sin consultar
la documentación funcional: recibió solo las capturas disponibles y la frase «identifica hasta tres
segmentos de Nueva York que convenga investigar para captación y explica una cautela». El recorrido
se repitió con cronómetro tras cargar la primera página: inicio
`2026-09-07T16:19:43.4617380+02:00`, fin `2026-09-07T16:19:53.5340199+02:00`, duración
**10,07 s**.

Respuesta resumida:

1. Bedford-Stuyvesant — Alojamiento entero: 1.591 anuncios, ranking 1.
2. Hell's Kitchen — Habitación privada: 672 anuncios, ranking 2.
3. East Flatbush — Alojamiento entero: 187 anuncios, ranking 3.

Cautela identificada: el ranking combina actividad histórica de reseñas, oferta relativa,
posición de precio y evidencia estadística; no prueba demanda, reservas, ocupación, ingresos,
margen ni causalidad.

Esta prueba comprueba descubribilidad y lenguaje, pero **no es un estudio formal con participantes
de negocio**. Antes de una implantación real conviene repetirla con al menos un directivo ajeno al
proyecto.

## Accesibilidad y fallback

| Control | Resultado | Evidencia |
|---|---|---|
| Contraste ≥ 4,5:1 | PASS | `theme.json` y contrato automatizado |
| Estado no comunicado solo por color | PASS | Etiquetas candidato/consolidado/observación/insuficiente |
| Texto alternativo en español | PASS | Validación de todos los visuales PBIR |
| Orden de tabulación | PASS | Filtros → hallazgo → evidencia → navegación |
| Cautelas fuera de tooltips | PASS | Textos visibles en las tres páginas |
| Azure Maps no disponible | PASS | Ranking y tabla agregada permanecen como fallback |
| Claves/PII/coordenadas individuales | PASS | Verificador externo y revisión del modelo |

## Incidencias y correcciones

- La primera tabla generaba combinaciones vacías porque `Estado de evidencia` devolvía texto sin
  filas de hecho. Se corrigió para devolver `BLANK()` cuando el contexto no contiene segmentos.
- El diagrama de dispersión no materializaba los ejes con columnas implícitas. Se sustituyeron por
  medidas explícitas.
- Azure Maps requirió autenticación. Se mantuvo como visual opcional y se añadió una instrucción
  visible para decidir con el ranking y la tabla.

No quedan incidencias bloqueantes para el uso local educativo.
