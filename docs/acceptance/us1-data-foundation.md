# Aceptación US1 — Base de datos confiable

**Fecha**: 2026-09-02  
**Build**: `FDAAB53F8317CAD7`

## Resultado independiente

Los comandos `inventory`, `audit` y `build` finalizaron con estado `success`. Se verificaron seis
fuentes, 220.031 filas de entrada y 220.031 filas canónicas con 220.031 claves únicas. No se rechazó
ni puso en cuarentena ninguna fila.

## Identidad de fuentes

| Fuente | Filas | SHA-256 verificado |
|---|---:|---|
| Londres | 85.068 | `766A8AB23C1A469F8C95F5DDE0DD21FF8583C676AFF33E6806CDD872CFFD5977` |
| Madrid | 19.618 | `5F8012389BFFF705B0B8F2B2A19FAC4D80C6EEE52B6694FE99A5F63FAE2D3799` |
| Milán | 18.322 | `F815FA5F93265AEE95CB61479B123D77A52A7E46162010A780EF4E9F666E04F7` |
| Nueva York | 48.895 | `E420DB40FF10FCB40EFC1B5B1648EE0B18A48F4E4537155CECC59FE95D18783A` |
| Sídney | 36.662 | `2ABC21647378F06EF6225805152BF87F5819A66D4AE6BFFEDD87D92FA3FD90D3` |
| Tokio | 11.466 | `33D049A365D820E111125A1D56937A81999AFAD9BFB5FDB59DBECAC01E305AAE` |

Los hashes de las copias coinciden con los archivos de origen antes y después del build.

## Evidencia de calidad y ETL

- 219.908 filas tienen actividad histórica analizable.
- 54.248 ceros se derivan exclusivamente de tasa ausente y cero reseñas.
- 123 filas con reseñas positivas y tasa ausente permanecen desconocidas.
- 50 precios no positivos se excluyen solo de cálculos de precio.
- Los notebooks `01_data_audit.ipynb` y `02_etl.ipynb` se ejecutaron de principio a fin en kernels
  nuevos y produjeron copias bajo `artifacts/executed_notebooks/`.
- La suite acumulada terminó con 25 pruebas aprobadas y `ruff` sin hallazgos.

## Limitaciones

La conciliación y los hashes demuestran integridad del procesamiento, no procedencia oficial,
actualidad, representatividad ni exactitud de lo declarado en los anuncios. Moneda, licencia y fecha
de extracción siguen registradas como desconocidas.

## Trazabilidad externa

La evidencia está enlazada al issue
[#3](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/3) y a la pull request
[#1](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/1). La tarea T025 permanece
abierta porque el trabajo se consolidó en `feat/essential-foundation`, no en la rama prevista, y el
movimiento a `Done` depende de la revisión, integración y conciliación del tablero.
