# Conciliación del informe Power BI — T103

## Resultado

**PASS**. El informe se refrescó en Power BI Desktop gratuito x64
`2.157.879.0 (26.08)` desde una copia limpia de los ocho CSV. No se usó Power BI Service ni una
licencia de pago.

| Control | Resultado |
|---|---:|
| Build | `FDAAB53F8317CAD7` |
| Schema | `1.0.0` |
| Archivos de datos | 8 |
| Filas importadas de anuncios | 220.031 |
| Claves de anuncio distintas | 220.031 |
| Segmentos de oportunidad | 1.497 |
| Segmentos candidatos | 28 |
| Candidatos mostrados con ranking ≤ 3 | 9 |
| Diferencia de conciliación | 0 |
| Hashes / privacidad | PASS / PASS |

El refresh se ejecutó contra una copia temporal limpia cuyo `DataRoot` apuntaba a su carpeta
`data/powerbi`. El proyecto PBIP versionado conserva `DataRoot` vacío y obligatorio, sin rutas
personales. La entrega poblada `.pbix` es una instantánea reproducible del build indicado.

## Cotejo independiente

Se consultó el modelo cargado mediante DAX y se recalcularon los mismos valores desde los CSV. La
muestra de Madrid — Justicia — Habitación privada coincidió exactamente:

| Medida | Power BI | CSV | Diferencia |
|---|---:|---:|---:|
| Anuncios del segmento | 281 | 281 | 0 |
| Cuota activa histórica | 0,7473309609 | 0,7473309609 | 0 |
| Posición de precio local | 0,80859375 | 0,80859375 | 0 |
| Probabilidad de superioridad | 0,5652568586 | 0,5652568586 | 0 |
| Valor ajustado (`q`) | 0,02032784077 | 0,02032784077 | 0 |
| Ranking candidato | 1 | 1 | 0 |

El control automatizado se repite con:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_powerbi.ps1 -DataRoot data/powerbi
```

## Evidencia visual

- [Resumen ejecutivo](evidence/powerbi/01-resumen-ejecutivo.png)
- [Detalle y confianza](evidence/powerbi/03-detalle-confianza.png)

La página intermedia se verificó estructuralmente en PBIR y durante el recorrido interactivo, pero
no se conserva una captura: Azure Maps pidió inicio de sesión y las capturas automatizadas de esa
instancia quedaron incompletas. El escenario valida el fallback previsto: la tabla y el ranking son
la superficie decisional y el informe no muestra coordenadas por anuncio.

## Límites

Las reseñas mensuales son un proxy histórico de actividad; no miden reservas, demanda, ocupación o
liquidez. El precio es publicado, con moneda y fecha desconocidas, y solo se compara localmente. El
resultado prioriza segmentos para investigar y no demuestra causalidad, margen ni rentabilidad.
