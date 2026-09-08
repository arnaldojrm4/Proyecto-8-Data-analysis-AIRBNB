/** Build the technical deck from the reviewed evidence snapshot.
 * Requires the Codex bundled presentation runtime. See docs/presentation/technical-presentation.md.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const root = process.cwd();
const modules = process.env.RUNTIME_NODE_MODULES;
const skill = process.env.PRESENTATION_SKILL_DIR;
const python = process.env.RUNTIME_PYTHON;
if (!modules || !skill || !python) throw new Error('Set RUNTIME_NODE_MODULES, PRESENTATION_SKILL_DIR and RUNTIME_PYTHON.');
const requireRuntime = createRequire(path.join(modules, '__runtime__.cjs'));
const { Presentation, PresentationFile, FileBlob } = await import(pathToFileURL(requireRuntime.resolve('@oai/artifact-tool')).href);
const { applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const data = JSON.parse(await fs.readFile(path.join(root, 'docs/presentation/technical-evidence.json'), 'utf8'));
const build = path.join(root, 'tmp/technical-presentation');
const finalPath = path.join(root, 'output/presentation/airbnb-desarrollo-tecnico.pptx');
await fs.mkdir(build, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const C = { navy: '#142D3B', teal: '#087E8B', coral: '#BC432E', gray: '#526471', pale: '#F4F7F8', white: '#FFFFFF' };
const font = 'Arial';
const cities = Object.keys(data.cities);
const room = { entire_home_apt: 'Alojamiento completo', private_room: 'Habitación privada', shared_room: 'Habitación compartida' };
const fmt = (n, digits = 0) => Number(n).toLocaleString('es-ES', { minimumFractionDigits: digits, maximumFractionDigits: digits, useGrouping: 'always' });
const chapters = [];
const charts = [];
const tables = [];
function text(slide, value, x, y, w, h, size = 27, color = C.navy, bold = false) {
  const shape = slide.shapes.add({ geometry: 'textbox', position: { left: x, top: y, width: w, height: h }, fill: 'none', line: { fill: 'none', width: 0 } });
  shape.text = value;
  shape.text.style = { typeface: font, fontSize: size, color, bold, autoFit: 'none', verticalAlignment: 'top' };
  return shape;
}
function slide(title, note, source = 'notebooks/03_executive_eda.ipynb', dark = false) {
  const s = deck.slides.add();
  s.background.fill = dark ? C.navy : C.white;
  text(s, title, 64, 47, 1152, 104, 43, dark ? C.white : C.navy, true);
  text(s, String(chapters.length + 1).padStart(2, '0'), 1160, 664, 56, 30, 18, dark ? '#BED3DB' : C.gray);
  s.speakerNotes.textFrame.setText(`${note}\n\nFuentes del repositorio: ${source}. Build ${data.build_id}. Revisión ${data.review_date}.`);
  chapters.push({ title, note, source, content: [] });
  return s;
}
function paragraph(s, value, y = 175, h = 370, size = 29, w = 1136, x = 72) {
  text(s, value, x, y, w, h, size);
  chapters.at(-1).content.push(value);
}
function foot(s, value) { text(s, value, 72, 594, 1100, 62, 21, C.gray); chapters.at(-1).content.push(value); }
function table(s, values, widths, { top = 176, height = 350, size = 24 } = {}) {
  const t = s.tables.add({ rows: values.length, columns: values[0].length, left: 72, top, width: 1136, height, columnWidths: widths, values });
  t.borders.assign({ fill: '#DCE4E7', width: 0.5, style: 'solid' });
  for (let r = 0; r < values.length; r++) {
    t.rows[r].height = height / values.length;
    for (let c = 0; c < values[r].length; c++) {
      const cell = t.getCell(r, c);
      cell.fill = r === 0 ? C.navy : (r % 2 ? C.white : C.pale);
      cell.text.style = { typeface: font, fontSize: size, color: r === 0 ? C.white : C.navy, bold: r === 0 };
    }
  }
  tables.push(chapters.length);
  const markdownRows = values.map(row => '| ' + row.map(value => String(value).replaceAll('\n', '<br>')).join(' | ') + ' |');
  markdownRows.splice(1, 0, '| ' + values[0].map(() => '---').join(' | ') + ' |');
  chapters.at(-1).content.push(markdownRows.join('\n'));
  return t;
}
function bar(s, categories, values, { max, format = '0', label = '', color = C.teal, left = 72, width = 1136, height = 375, top = 179 } = {}) {
  const ch = s.charts.add('bar', {
    position: { left, top, width, height }, categories,
    series: [{ name: label || 'Valor', values, fill: color, valuesFormatCode: format }],
    barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 100 },
    hasLegend: false, chartFill: C.white, plotAreaFill: C.white,
    xAxis: { textStyle: { fontSize: 23, fill: C.navy }, majorGridlines: null },
    yAxis: { min: 0, ...(max === undefined ? {} : { max }), numberFormatCode: format, textStyle: { fontSize: 20, fill: C.gray }, majorGridlines: { fill: '#E0E8EA', width: 1 } },
    dataLabels: { showValue: true, position: 'outEnd', numberFormatCode: format, textStyle: { fontSize: 24, fill: C.navy, bold: true } },
  });
  applyPresentationChartFont(ch, { fontFamily: font });
  charts.push(chapters.length);
  chapters.at(-1).content.push(categories.map((name, i) => `- ${name.replaceAll('\n', ' ')}: ${values[i]}`).join('\n'));
  return ch;
}

let s = slide('Análisis de oferta Airbnb', 'Presentación técnica del proyecto educativo. El resultado es una priorización reproducible para investigación comercial. Las fuentes no permiten estimar demanda actual ni resultados económicos.', 'README.md; pyproject.toml', true);
text(s, 'Desarrollo técnico y\nconclusiones del análisis', 72, 208, 1080, 180, 64, C.white, true);
text(s, '220.031 anuncios en seis ciudades', 76, 445, 1000, 54, 34, '#87D5D7');
text(s, 'Arnaldo  ·  Proyecto 8A  ·  8 septiembre 2026', 76, 553, 1000, 40, 24, '#BED3DB');

s = slide('Objetivos y unidad de decisión', 'La pregunta combina ciudad, barrio y tipología. El trabajo integra fuentes heterogéneas, conserva su trazabilidad, estudia la actividad histórica y comunica la incertidumbre. La decisión final requiere investigación comercial con datos vigentes.', 'README.md; config/analysis.yml');
paragraph(s, 'Identificar qué combinaciones de ciudad, barrio y tipología conviene investigar para captar nueva oferta.', 178, 122, 36);
text(s, 'Objetivo analítico', 72, 338, 490, 50, 29, C.teal, true);
text(s, 'Comparar actividad histórica y cuota de oferta con muestra, efecto e incertidumbre visibles.', 72, 398, 510, 150, 28);
text(s, 'Objetivo técnico', 654, 338, 490, 50, 29, C.teal, true);
text(s, 'Reproducir el recorrido desde los CSV hasta notebooks, Power BI y el panel web.', 654, 398, 530, 150, 28);
foot(s, 'reviews_per_month es una señal histórica de reseñas. No equivale a reservas.');

s = slide('Fuentes y cobertura', 'Las seis fuentes contienen 220.031 anuncios. Sus tamaños son desiguales. No se conoce la fecha de extracción ni la representatividad del mercado completo. El SHA-256 valida la identidad de la copia recibida, no su actualidad.', 'config/source-manifest.json; notebooks/01_data_audit.ipynb');
bar(s, cities.map(c => data.cities[c]), cities.map(c => data.listing_counts[c]), { max: 100000, format: '#,##0', label: 'Anuncios' });
foot(s, 'Seis CSV públicos. Comparaciones dentro de ciudad y conservación de todas las filas.');

s = slide('Desarrollo del pipeline', 'La CLI coordina las etapas inventory, audit, build, analyze y export. La publicación pasa por validación y los consumidores leen resultados ya calculados. Los notebooks documentan y visualizan el build. Los datos raw permanecen inmutables.', 'src/airbnb_supply_analysis/cli.py; README.md');
table(s, [['Etapa', 'Resultado'], ['Inventario y auditoría', 'Identidad, esquema, nulos y hallazgos por fuente'], ['ETL y modelo canónico', 'Tipos armonizados, linaje y Parquet de anuncios'], ['EDA y estadística', 'Contrastes, sensibilidades y matriz de segmentos'], ['Exportación y validación', 'Ocho CSV para Power BI y Streamlit'], ['Comunicación', 'Notebooks, visualizaciones y presentación']], [350, 786], { height: 390, size: 25 });
foot(s, 'Build analizado: FDAAB53F8317CAD7. Clave del anuncio: ciudad + identificador.');

s = slide('Tecnologías utilizadas', 'La lista describe dependencias y componentes presentes en el repositorio. Python 3.13 y uv.lock fijan el entorno. Pandera valida datos y PyArrow permite Parquet. SciPy y statsmodels implementan estadística. El panel Streamlit utiliza las exportaciones seguras del pipeline.', 'pyproject.toml; uv.lock; Dockerfile; powerbi/README.md');
table(s, [['Función', 'Tecnologías'], ['Entorno y procesamiento', 'Python 3.13, uv, pandas, NumPy'], ['Contratos y almacenamiento', 'Pandera, PyArrow, Parquet, CSV, SHA-256'], ['Estadística', 'SciPy y statsmodels'], ['Exploración y gráficos', 'Jupyter, nbformat, nbclient, Matplotlib, Seaborn, Plotly'], ['Consumo analítico', 'Power BI Desktop, modelo semántico y Streamlit'], ['Calidad y distribución', 'pytest, Ruff, Git, GitHub, Docker y Compose']], [340, 796], { height: 420, size: 24 });

s = slide('ETL sin pérdida de registros', 'Se conservan 220.031 entradas. La clave listing_key es única. Se derivan ceros únicamente cuando falta la tasa y el número de reseñas es cero. Las 123 tasas desconocidas tienen reseñas positivas. Los precios no positivos quedan fuera solo de métricas de precio y los outliers se conservan con indicadores.', 'notebooks/02_etl.ipynb; src/airbnb_supply_analysis/etl.py');
table(s, [['Control', 'Resultado', 'Tratamiento'], ['Conciliación de filas', '220.031 / 220.031', 'Ningún anuncio eliminado'], ['Actividad derivada a cero', '54.248', 'Solo cuando no hay reseñas'], ['Actividad desconocida', '123', 'Permanece ausente'], ['Precio no válido', '50', 'Excluir solo de métricas de precio']], [380, 230, 526], { height: 330, size: 26 });
foot(s, '219.908 anuncios tienen actividad analizable. Los nulos estructurales siguen siendo nulos.');

s = slide('Notebooks y reproducibilidad', 'Los notebooks consumen los artefactos del pipeline. La ejecución se realiza en orden y en kernels separados. El generador conserva ahora la exploración geográfica y las conclusiones revisadas. Una prueba compara su contenido con los notebooks versionados para evitar pérdidas al regenerar.', 'notebooks/; scripts/generate_notebooks.py; src/airbnb_supply_analysis/notebooks.py');
table(s, [['Notebook', 'Pregunta y evidencia'], ['01 · Auditoría', '¿Qué contienen las fuentes y qué calidad tienen?'], ['02 · ETL', '¿Cómo se armonizan y concilian las 220.031 filas?'], ['03 · EDA ejecutivo', '¿Qué segmentos cumplen las reglas y dónde están?']], [365, 771], { height: 288, size: 27 });
paragraph(s, 'El generador conserva las nuevas celdas geográficas.\nCada ejecución usa los artefactos del build y un kernel limpio.', 500, 95, 27);

s = slide('Métodos estadísticos', 'H1 compara tipologías por ciudad con Kruskal-Wallis y epsilon cuadrado, ajustando por Holm. H2 compara las medianas de actividad por anfitrión del segmento y del resto de la misma ciudad y tipología mediante Mann-Whitney, superioridad e IC bootstrap por anfitrión, con BH. H3 estudia asociaciones de Spearman. El modelo en dos partes complementa la sensibilidad, sin interpretación causal. Un mismo anfitrión podría aparecer en ambos grupos locales y merece revisión adicional de dependencia.', 'src/airbnb_supply_analysis/statistics.py; config/analysis.yml');
table(s, [['Pregunta', 'Método', 'Lectura'], ['H1 · Tipología', 'Kruskal-Wallis + Holm', 'Diferencia global y epsilon²'], ['H2 · Segmento local', 'Mann-Whitney + BH', 'Superioridad e IC 95 % por anfitrión'], ['H3 · Asociaciones', 'Spearman + BH', 'Precio y noches mínimas frente a actividad']], [295, 350, 491], { height: 295, size: 25 });
foot(s, 'Sensibilidad: casos completos, outliers y unidad anfitrión. El modelo en dos partes separa presencia e intensidad de actividad.');

s = slide('Reglas para clasificar un segmento', 'La clasificación exige al menos 30 anuncios analizables y 10 con actividad positiva. La evidencia exige superioridad de al menos 0,56, límite inferior del IC mayor que 0,5, q menor que 0,05 y sensibilidades robustas. Una cuota local menor que la de ciudad distingue candidate de consolidated. El orden entre candidatos se basa primero en número de anuncios, después en efecto y clave de desempate.', 'src/airbnb_supply_analysis/opportunity.py; config/analysis.yml');
paragraph(s, 'Muestra: ≥ 30 anuncios analizables y ≥ 10 positivos\nEvidencia: superioridad ≥ 0,56, IC inferior > 0,50, q < 0,05\nEstabilidad: sensibilidades robustas', 163, 168, 28);
table(s, [['Estado', 'Interpretación', 'Segmentos'], ['candidate', 'Evidencia robusta y menor cuota local', '28'], ['consolidated', 'Evidencia robusta sin menor cuota local', '19'], ['watch', 'Muestra elegible, evidencia incompleta', '586'], ['insufficient_evidence', 'Muestra insuficiente', '864']], [325, 645, 166], { top: 353, height: 235, size: 23 });
foot(s, 'La matriz contiene 1.497 segmentos. Las etiquetas no estiman rentabilidad.');

s = slide('28 candidatos en cinco ciudades', 'El recuento actualizado es 28 y corrige el 29 del resumen anterior del notebook. Sídney aporta 13 y Nueva York 12. Juntas representan 25/28, el 89,3 %. La concentración describe las fuentes y las reglas aplicadas, no una cuota de mercado ni una comparación causal entre ciudades.', 'data/processed/opportunity_segments.parquet; notebooks/03_executive_eda.ipynb');
bar(s, cities.map(c => data.cities[c]), cities.map(c => data.candidate_counts[c]), { max: 15, label: 'Segmentos candidatos' });
foot(s, 'Nueva York y Sídney reúnen el 89,3 %. Londres no supera simultáneamente todas las reglas.');

s = slide('Primer candidato por ciudad', 'La selección usa el rango oficial dentro de cada ciudad. N cuenta anuncios, mientras que el contraste y la superioridad usan medianas por anfitrión. Los cinco candidatos cumplen q menor que 0,05 y sensibilidades robustas. El efecto de Nakano Ku es mayor, pero su N de 55 y el IC más ancho deben permanecer visibles.', 'data/processed/opportunity_segments.parquet; src/airbnb_supply_analysis/statistics.py');
table(s, [['Ciudad y barrio', 'Tipología', 'N', 'Superioridad', 'IC 95 %'], ...data.top_candidates.map(r => [data.cities[r.city_key]+'\n'+r.neighborhood, room[r.room_type], fmt(r.listing_count), fmt(r.probability_superiority,3), `${fmt(r.effect_ci_low,3)}–${fmt(r.effect_ci_high,3)}`])], [355, 265, 95, 185, 236], { top: 155, height: 405, size: 23 });
foot(s, 'Rango por escala dentro de ciudad. Superioridad = comparación de medianas por anfitrión, con empates a medias.');

s = slide('Nueva lectura: brecha de cuota local', 'La brecha compara la cuota de una tipología entre los anuncios de toda la ciudad con su cuota entre los anuncios del barrio. Se resta cuota barrio a cuota ciudad y se multiplica por 100. Los valores exactos provienen del Parquet. Una menor presencia relativa no prueba escasez de oferta, saturación o necesidades comerciales sin cubrir.', 'notebooks/03_executive_eda.ipynb, sección 6; data/processed/opportunity_segments.parquet');
bar(s, ['Justicia', 'CENTRALE', 'Bedford-\nStuyvesant', 'Leichhardt', 'Nakano Ku'], data.top_candidates.map(r => Number(r.supply_gap_pp.toFixed(1))), { max: 12, format: '0.0', label: 'Brecha de cuota (puntos porcentuales)', color: C.coral });
foot(s, 'Puntos porcentuales = cuota de la tipología en la ciudad menos cuota en el barrio. CENTRALE cumple con una brecha de 2,4 puntos.');

s = slide('Exploración geográfica de los candidatos', 'El notebook incorpora una matriz de brechas de hasta tres candidatos por ciudad y un mapa interactivo de los 28 centroides disponibles. Cada centroide se obtiene de coordenadas válidas agregadas mediante mediana. Las combinaciones no seleccionadas permanecen vacías en la matriz. La nueva selección elimina el sesgo de ordenar por ciudad y aplicar head(12) globalmente. Se retira el score ad hoc porque mezclaba actividad, cuota, efecto y tamaño sin validación.', 'notebooks/03_executive_eda.ipynb, secciones 6 y 7; src/airbnb_supply_analysis/opportunity.py');
text(s, '28 de 28', 72, 171, 520, 110, 72, C.teal, true);
text(s, 'candidatos con centroides disponibles', 76, 287, 510, 95, 32);
text(s, 'La matriz conserva hasta tres candidatos por ciudad según su rango oficial.', 658, 189, 500, 133, 31);
text(s, 'El mapa muestra ubicación agregada. La tabla conserva muestra, intervalo y cobertura geográfica.', 658, 359, 500, 155, 29);
foot(s, 'Los estados watch mantienen su categoría. Las celdas vacías de la matriz no equivalen a cero.');

s = slide('Significación y tamaño del efecto', 'Los contrastes globales por tipología tienen p ajustada inferior a 0,05 en las seis ciudades. Sin embargo, epsilon cuadrado es casi nulo en Londres y Nueva York. Los resultados globales no sustituyen los contrastes locales: Nueva York conserva 12 candidatos pese al efecto global mínimo. Epsilon cuadrado se muestra como magnitud descriptiva de efecto, sin convertirlo en explicación causal.', 'data/processed/statistical_results.parquet, method=kruskal_wallis');
bar(s, cities.map(c => data.cities[c]), cities.map(c => Number(data.room_tests.find(r => r.city_key === c).estimate.toFixed(4))), { max: 0.1, format: '0.0000', label: 'Epsilon cuadrado' });
foot(s, 'Un valor p pequeño no garantiza relevancia práctica. La decisión local necesita barrio y tipología.');

s = slide('Precio y estancia mínima: asociaciones', 'Las correlaciones son de Spearman y se calculan dentro de cada ciudad. El precio tiene asociación negativa en cinco ciudades y positiva en Tokio. Las noches mínimas se asocian negativamente en las seis, con mayor magnitud en Sídney. La tabla no estima cambios de reservas provocados por reducir precio o estancia mínima.', 'data/processed/statistical_results.parquet, method=spearman');
table(s, [['Ciudad', 'Precio / actividad', 'Noches mínimas / actividad'], ...cities.map(c => [data.cities[c], fmt(data.associations.find(r => r.city_key===c && r.metric==='price_vs_activity').estimate,3), fmt(data.associations.find(r => r.city_key===c && r.metric==='minimum_nights_vs_activity').estimate,3)])], [310, 366, 460], { height: 392, size: 26 });
foot(s, 'Coeficiente rho de Spearman. Son asociaciones históricas, sin interpretación causal.');

s = slide('Dashboard y distribución del análisis', 'Power BI Desktop utiliza ocho CSV y un modelo estrella. Streamlit lee las mismas exportaciones seguras con filtros coordinados y vistas de resumen, oportunidad y evidencia. El panel no recalcula pruebas sobre selecciones arbitrarias. Docker Compose separa pipeline y dashboard y monta data/powerbi en solo lectura para el panel.', 'powerbi/README.md; dashboard/app.py; compose.yaml');
text(s, 'Power BI Desktop', 72, 182, 530, 55, 35, C.teal, true);
text(s, 'Modelo estrella y filtros por ciudad, barrio, tipología y estado de evidencia.', 72, 259, 510, 170, 31);
text(s, 'Streamlit', 650, 182, 530, 55, 35, C.teal, true);
text(s, 'Resumen, oportunidades y confianza estadística sobre las mismas exportaciones.', 650, 259, 530, 170, 31);
paragraph(s, 'Docker Compose distribuye el pipeline y el panel.\nEl dashboard lee data/powerbi/ en modo de solo lectura.', 483, 100, 28);

s = slide('Reproducir y mantener el proyecto', 'Para repetir todo el flujo hacen falta Python 3.13, uv y las seis fuentes en data/raw. uv sync usa el lockfile. all ejecuta el flujo integrado. notebooks vuelve a ejecutar los tres notebooks sobre artefactos existentes. pytest incluye pruebas de datos completos y comprobaciones Docker que requieren su entorno operativo. El generador se conserva junto con la prueba de paridad de contenido.', 'README.md; pyproject.toml; tests/; scripts/generate_notebooks.py');
table(s, [['Paso', 'Comando'], ['Preparar entorno', 'uv sync --locked --group dev'], ['Ejecutar el pipeline', 'uv run --locked airbnb-supply all --log-format json'], ['Repetir notebooks', 'uv run --locked airbnb-supply notebooks'], ['Verificar código', 'uv run --locked pytest -q\nuv run --locked ruff check .']], [310, 826], { height: 360, size: 24 });
foot(s, 'Conservar fuentes, configuración, uv.lock y build. Revisar las cifras narrativas cuando cambie el build.');

s = slide('Conclusiones y límites', 'La entrega identifica 28 candidatos mediante reglas explícitas. La nueva exploración geográfica añade ubicación y brecha de cuota sin modificar el criterio estadístico. La captación debe contrastarse con información interna actual sobre búsquedas, reservas, conversión, ocupación, costes y capacidad real. No se conoce moneda comparable, fecha de extracción, licencia ni universo completo. El precio solo se compara dentro de ciudad.', 'README.md; docs/analysis/executive-findings.md; notebooks/03_executive_eda.ipynb');
paragraph(s, 'Investigar los candidatos con evidencia robusta, empezando por el rango de cada ciudad.', 174, 120, 37);
text(s, 'Qué añade el notebook', 72, 330, 530, 53, 30, C.teal, true);
text(s, 'Centroides y brechas de cuota local.\n25 de 28 candidatos en Nueva York y Sídney.', 72, 399, 525, 155, 29);
text(s, 'Qué falta para decidir', 650, 330, 530, 53, 30, C.coral, true);
text(s, 'Datos internos vigentes de reservas, conversión, ocupación y costes.', 650, 399, 530, 155, 29);
foot(s, 'Fuentes de fecha y representatividad desconocidas. Los resultados priorizan investigación comercial.');

if (!process.argv.includes('--notes-only')) {
const draft = path.join(build, 'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(draft);
console.log(`Draft exported: ${chapters.length} slides`);
for (let i = 0; i < deck.slides.items.length; i++) {
  const page = deck.slides.items[i];
  const png = await deck.export({ slide: page, format: 'png', scale: 1 });
  await fs.writeFile(path.join(build, `slide-${String(i+1).padStart(2,'0')}.png`), new Uint8Array(await png.arrayBuffer()));
}
const result = await finalizePresentation({
  workspaceDir: root, candidatePath: draft, finalPath,
  pythonExecutable: python,
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-heading-fit', ...tables.flatMap(n => ['--require-native-table-slide', String(n)])],
  requiredNativeTableOwnerSlides: tables,
  requiredNativeChartOwnerSlides: charts,
  materializeLiteralChartWorkbooks: true,
  fontPolicy: { basis: 'design', families: [font] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(build, `validation-${Date.now()}.json`),
});
console.log(JSON.stringify(result));
const finalDeck = await PresentationFile.importPptx(await FileBlob.load(finalPath));
for (let i = 0; i < finalDeck.slides.items.length; i++) {
  const png = await finalDeck.export({ slide: finalDeck.slides.items[i], format: 'png', scale: 1 });
  await fs.writeFile(path.join(build, `final-${String(i+1).padStart(2,'0')}.png`), new Uint8Array(await png.arrayBuffer()));
}
}
const intro = '# Presentación técnica del análisis de oferta Airbnb\n\n18 diapositivas. Guion para una exposición técnica de unos 20 minutos.\n\n[Descargar PowerPoint](../../output/presentation/airbnb-desarrollo-tecnico.pptx)\n\nBuild: '+data.build_id+'. Revisión: '+data.review_date+'. Las cifras describen estas fuentes históricas, de fecha de extracción desconocida.\n';
const markdown = intro + chapters.map((c,i) => `\n## ${i+1}. ${c.title}\n\n${c.content.join('\n\n')}\n\n${c.note}\n\nFuentes: ${c.source}.\n`).join('') + '\n## Regeneración del entregable\n\nEl script `scripts/create_technical_presentation.mjs` lee `docs/presentation/technical-evidence.json`, una instantánea agregada del build. Requiere el runtime de presentaciones de Codex y las variables `RUNTIME_NODE_MODULES`, `PRESENTATION_SKILL_DIR` y `RUNTIME_PYTHON`. Ejecutar desde la raíz con el Node de ese runtime. El finalizador exige que el archivo de salida todavía no exista. Para otro build, actualizar primero la instantánea y revisar todas las cifras y conclusiones.\n';
await fs.writeFile(path.join(root, 'docs/presentation/technical-presentation.md'), markdown);
