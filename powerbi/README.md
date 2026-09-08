# Guía del informe Power BI Desktop

> **Panel complementario avanzado:** el repositorio también incluye una aplicación web portable en
> `dashboard/` que consume estos mismos ocho CSV validados. Power BI continúa siendo la entrega BI de
> escritorio; el panel web añade despliegue Docker sin alterar el modelo ni recalcular la estadística.
> Consulta la sección “Panel web avanzado” del README principal para ejecutarlo.

Esta carpeta contiene la definición y la documentación del informe ejecutivo local para explorar
oportunidades provisionales de captación de alojamientos. El informe consume únicamente los ocho
CSV validados de `data/powerbi/`; las reglas estadísticas y de oportunidad pertenecen al pipeline
Python y no se recalculan en Power BI.

## Coste, alcance y versión

Power BI Desktop se descarga gratuitamente y permite crear, abrir, actualizar y editar archivos
locales `.pbix` y `.pbit`. Este proyecto no requiere Power BI Pro, Premium, Fabric ni un workspace
de Power BI Service. La publicación y distribución centralizada o las actualizaciones programadas
quedan fuera del alcance.

- **Entorno detectado el 2026-09-07**: Power BI Desktop x64 `2.157.879.0 (26.08)`.
- **Versión base para construir el informe**: `2.157.879.0 (26.08)` o posterior.
- **Versión mínima compatible verificada mediante refresh**: `2.157.879.0 (26.08)`.

El `.pbix` se abrió y refrescó desde un `DataRoot` limpio con esa versión. Microsoft
publica Power BI Desktop mensualmente y solo soporta la versión más reciente; ante un problema no
reproducible se debe volver a probar con la versión x64 actual.

Requisitos oficiales relevantes: Windows 10 o Windows Server 2016 o posterior, .NET 4.7.2,
Microsoft Edge, 2 GB de RAM disponibles —4 GB recomendados— y pantalla mínima 1440×900 o 1600×900.
Consulta la [descarga y requisitos oficiales](https://learn.microsoft.com/es-es/power-bi/fundamentals/desktop-get-the-desktop).

## Artefactos

| Artefacto | Contenido | Estado actual |
|---|---|---|
| `airbnb-supply-opportunity.pbix` | Informe editable con datos importados | Completo (T095–T100) |
| `airbnb-supply-opportunity.pbit` | Plantilla sin datos importados | Completo (T101) |
| `theme.json` | Tema accesible validado con el esquema oficial 2.157 | Completo (T094) |
| `acceptance-checklist.md` | Lista de aceptación manual | PASS (T103–T105) |

Una plantilla `.pbit` conserva consultas, parámetros, modelo, medidas, páginas y formato, pero no
incluye los datos importados. Al abrirla, Power BI Desktop solicita los parámetros y crea un informe
que se guarda como `.pbix`. Véase la guía oficial para
[crear y usar plantillas](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-templates).

El tema reserva los cuatro primeros colores y sus iconos para `candidate`, `consolidated`, `watch`
y `insufficient`. Todos superan un contraste 4,5:1 sobre blanco. Cada visual debe conservar también
las etiquetas `Candidato`, `Consolidado`, `En observación` o `Evidencia insuficiente`; el color nunca
es la única señal. El contrato automatizado está en
`tests/contract/test_powerbi_theme.py` y el archivo referencia el esquema oficial de la versión
Desktop probada.

## Preparar los datos

Desde la raíz del repositorio:

```powershell
uv run --locked airbnb-supply export --log-format json
uv run --locked airbnb-supply validate --log-format json
```

La alternativa reproducible en Docker es:

```powershell
docker compose run --rm pipeline all --log-format json
```

La ejecución aceptada deja exactamente estos archivos bajo `data/powerbi/`:

```text
build_control.csv
dim_city.csv
dim_neighborhood.csv
dim_room_type.csv
fact_listings.csv
fact_opportunity_segments.csv
fact_quality_summary.csv
fact_statistical_results.csv
```

No se debe editar manualmente ninguno. `build_control.csv` registra la identidad del build, versión
de esquema, conteos y hashes. `validate` vuelve a comprobarlos sin reconstruir el análisis.

## Configurar `DataRoot`

`DataRoot` es un parámetro de texto obligatorio de Power Query. Contiene la ruta absoluta del host a
la carpeta `data/powerbi/` de este checkout, nunca una ruta interna del contenedor ni una ruta propia
del equipo del autor.

Ejemplo:

```text
C:\proyectosF5\Proyecto 8A\data\powerbi
```

En Power BI Desktop:

1. Abre `airbnb-supply-opportunity.pbit` o el `.pbix` de trabajo.
2. Si aparece **Introducir parámetros**, escribe la ruta en `DataRoot`.
3. Para cambiarla después, abre **Transformar datos > Administrar parámetros**.
4. Confirma que el tipo sea `Texto`, que sea obligatorio y que la carpeta exista.
5. Selecciona **Inicio > Actualizar**.

Todas las consultas construyen su archivo a partir de `DataRoot`; no contienen rutas absolutas
adicionales. Microsoft explica este mecanismo en
[Uso de parámetros](https://learn.microsoft.com/en-us/power-query/power-query-query-parameters).

## Actualizar y guardar

1. Ejecuta `airbnb-supply export` o `all` y confirma `status: success`.
2. Abre la plantilla, introduce `DataRoot` y actualiza en modo **Importación**.
3. Comprueba que `release_gate_status = pass` y que la versión mayor del esquema sea `1`.
4. En `Detalle y confianza`, confirma que `Diferencia de conciliación = 0`.
5. Contrasta una muestra de medidas con los CSV aceptados.
6. Guarda el resultado como `powerbi/airbnb-supply-opportunity.pbix`.

Power BI Desktop admite Texto/CSV y Carpeta como fuentes de archivo, según su documentación de
[orígenes de datos](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-sources).
Los datos quedan importados como instantánea local: cambiar un CSV no actualiza el informe hasta
ejecutar otro refresh.

## Modelo semántico esperado

| Tabla | Papel | Relaciones |
|---|---|---|
| `DimCity` | Ciudad, etiqueta y cautelas | 1→* hacia barrios, anuncios y oportunidades |
| `DimNeighborhood` | Barrio y centroide agregado | 1→* hacia anuncios y oportunidades |
| `DimRoomType` | Tipología, etiqueta y orden | 1→* hacia anuncios y oportunidades |
| `FactListings` | Una fila segura por anuncio | Recibe filtros de las tres dimensiones |
| `FactOpportunitySegments` | Evidencia por ciudad, barrio y tipología | Recibe filtros de las tres dimensiones |
| `FactStatisticalResults` | Efectos, intervalos y valores ajustados | Segmento como contexto analítico |
| `FactQualitySummary` | Calidad agregada | Sin evidencia a nivel de anuncio |
| `BuildControl` | Build, esquema, filas y hashes | Desconectada del modelo analítico |
| `Measures` | Medidas DAX explícitas | Tabla de presentación sin relación |

Las relaciones son uno-a-muchos y unidireccionales desde las dimensiones. Las claves técnicas se
ocultan. No se habilitan medidas implícitas para campos visibles ni se duplican en DAX las reglas de
elegibilidad, efectos, intervalos, sensibilidad o etiquetas calculadas por Python.

## Límites

- `reviews_per_month` aproxima actividad histórica mediante reseñas; no mide demanda, reservas,
  ocupación, liquidez ni rotación real.
- `price` es un precio publicado de moneda y fecha desconocidas; solo se interpreta dentro de cada
  ciudad y no representa ingresos, margen o rentabilidad.
- Las fechas de snapshot son desconocidas; el informe no describe la situación como actual.
- Las recomendaciones son oportunidades provisionales para investigar, no decisiones causales.
- El mapa usa centroides agregados. Sin Azure Maps o red, el ranking debe permitir la misma decisión.
- El `.pbix` es una copia editable con datos importados. Sin Power BI Service no existen publicación
  web, acceso centralizado, auditoría del servicio ni actualización programada.
- La plantilla `.pbit` no incluye los datos importados, pero puede conservar metadatos y selecciones;
  debe revisarse antes de compartirla.

## Resolución de errores

| Síntoma | Comprobación | Acción |
|---|---|---|
| Falta un archivo | Revisa `DataRoot` y los ocho nombres | Regenera con `export`; no renombres CSV |
| La ruta apunta a `/app/...` | Es una ruta del contenedor | Usa la ruta absoluta del host |
| Solicitud de privacidad del origen | Los CSV son locales y comparten carpeta | Configura el origen local y actualiza |
| Esquema mayor incompatible | Revisa `schema_version` | Detén el refresh y usa una plantilla compatible |
| Gate distinto de `pass` | El build no está aceptado | Ejecuta `validate`, corrige y regenera |
| Hash o conteo incorrecto | Hay edición o mezcla de builds | Regenera juntos los ocho CSV derivados |
| Relación huérfana | Dimensión y hecho no coinciden | Regenera; nunca combines carpetas |
| Conciliación distinta de cero | Importación, filtros o control difieren | Quita filtros, actualiza y bloquea la entrega |
| El mapa no carga | Azure Maps o red no disponibles | Usa el ranking accesible |
| Una versión antigua no abre el archivo | No hay compatibilidad hacia atrás garantizada | Actualiza Desktop x64 y registra la versión |

No se desactiva una validación para completar el refresh. Ante un error, la última exportación que
haya aprobado el pipeline continúa siendo la autorizada.

## Aceptación y referencias

- [Checklist manual](acceptance-checklist.md)
- [Aceptación del Nivel Medio](../docs/acceptance/medium-level.md)
- [Conciliación del informe](../docs/acceptance/powerbi-reconciliation.md)
- [Validación reproducible](../docs/acceptance/quickstart-validation.md)
- [Evidencia contractual T087–T092](../docs/acceptance/powerbi-contracts-red.md)
- [Conciliación T103](../docs/acceptance/powerbi-reconciliation.md)
- [UAT y accesibilidad T104](../docs/acceptance/powerbi-uat.md)
- [Aceptación Nivel Medio T105](../docs/acceptance/medium-level.md)

El informe, la plantilla y la fuente PBIP se aceptaron con build `FDAAB53F8317CAD7`, schema `1.0.0`
y diferencia de conciliación cero.
