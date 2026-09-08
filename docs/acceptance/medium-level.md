# Aceptación del Nivel Medio — T105

## Decisión

**Nivel Medio: APROBADO** para uso local, educativo y sin licencia de pago. El Nivel Esencial ya
estaba aceptado y no se ha iniciado alcance Avanzado/Experto.

La aceptación independiente se apoya en controles externos al lienzo: contratos de Python,
validador PBIR oficial, verificador PowerShell, consulta DAX del modelo cargado, cotejo directo con
CSV y revisión visual de las tres páginas. La UAT de descubribilidad es proxy y su limitación queda
registrada.

## Entrega enlazada

- Informe poblado: [`powerbi/airbnb-supply-opportunity.pbix`](../../powerbi/airbnb-supply-opportunity.pbix)
- Plantilla sin datos: [`powerbi/airbnb-supply-opportunity.pbit`](../../powerbi/airbnb-supply-opportunity.pbit)
- Fuente versionable: [`powerbi/AirbnbSupplyOpportunity.pbip`](../../powerbi/AirbnbSupplyOpportunity.pbip)
- Guía de refresh: [`powerbi/README.md`](../../powerbi/README.md)
- Conciliación: [powerbi-reconciliation.md](powerbi-reconciliation.md)
- UAT y accesibilidad: [powerbi-uat.md](powerbi-uat.md)
- Contratos iniciales: [powerbi-contracts-red.md](powerbi-contracts-red.md)
- Issue: [#6](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/6)
- PR: [#10](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/10)

## Puerta de aceptación

| Criterio | Estado |
|---|---|
| Tres páginas orientadas a decisión | PASS |
| Filtros de ciudad, tipología y evidencia | PASS |
| Ranking y detalle estadístico | PASS |
| Mapa agregado con fallback completo | PASS |
| Medidas explícitas y conciliación cero | PASS |
| Release gate, schema y build únicos | PASS |
| Privacidad y ausencia de rutas personales | PASS |
| `.pbit` sin datos y `DataRoot` parametrizado | PASS |
| Accesibilidad y cautelas visibles | PASS |
| Uso local sin Power BI Service/licencia de pago | PASS |

## Resultado de negocio que puede estudiarse

El informe permite priorizar combinaciones ciudad–barrio–tipología con evidencia estadística,
escala y baja oferta relativa. Identifica 28 candidatos en el build aceptado; muestra como máximo
tres por ciudad. Son hipótesis de captación para validar con datos internos vigentes, no promesas de
demanda o rentabilidad.
