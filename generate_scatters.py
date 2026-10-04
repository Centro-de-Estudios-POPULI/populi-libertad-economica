"""
generate_scatters.py — las 11 dispersiones del Monitor de Libertad Económica (libertad económica
vs un indicador de bienestar), sobre el molde de monitores (embed/comun/, fuente única en
populi-marca/monitor). Una plantilla, once archivos: los textos y formatos de cada indicador
están en la lista; las cifras del panel que dependen del dato ({razon}, {dif}, {lat}) y las de la
fila de cifras las calcula la página desde data/consolidated.json.

    python generate_scatters.py
"""
import json, os

EMBED_DIR = 'embed'

scatters = [
    {
        'file': 'scatter_gdp.html',
        'var': 'gdp_pc_ppp',
        'title': 'Libertad Económica y Renta per Cápita',
        'subtitle': 'Promedio EFW 2000–2023 vs PIB per cápita PPP (USD constantes)',
        'y_label': 'PIB per cápita PPP (USD)',
        'y_format': "v => '$' + (v >= 1000 ? Math.round(v).toLocaleString('es-BO') : v.toFixed(0))",
        'y_axis_fmt': "v => v >= 1000 ? '$'+(v/1000).toFixed(0)+'k' : '$'+v",
        'log_y': True,
        'y_min': 'null', 'y_max': 'null',
        'reg_order': 2,
        'accent': '#C71E1D',
        'panel_hd_bg': '#C71E1D', 'panel_hd_bg_dark': '#2A1211',
        'relation': 'Los países con <strong>mayor libertad económica sostenida</strong> muestran niveles de ingreso per cápita significativamente más altos. El cuartil más libre (EFW de {corte} o más) tiene un PIB per cápita promedio <strong>{razon} veces mayor</strong> que el menos libre.',
        'theory': 'La libertad económica —derechos de propiedad, moneda sana, libre comercio, regulación eficiente y gobierno limitado— facilita la <strong>acumulación de capital</strong>, la <strong>innovación</strong> y la <strong>asignación eficiente de recursos</strong>, motores fundamentales del crecimiento a largo plazo.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW promedio: <strong>{efw}</strong>, cuartil {q}) tiene un PIB per cápita PPP de <strong>{yval}</strong>. Se ubica en el rango medio-bajo de libertad económica, y su ingreso está por debajo del promedio latinoamericano ({lat}).",
    },
    {
        'file': 'scatter_poverty.html',
        'var': 'poverty_365',
        'title': 'Libertad Económica y Pobreza',
        'subtitle': 'Promedio EFW 2000–2023 vs tasa de pobreza (menos de US$ 4,20 al día, PPA 2021)',
        'y_label': 'Pobreza (% de la población, < US$ 4,20 al día)',
        'y_format': "v => v.toFixed(1) + '%'",
        'y_axis_fmt': "v => v.toFixed(0) + '%'",
        'log_y': False,
        'y_min': '0', 'y_max': '95',
        'reg_type': 'exp',
        'reg_order': 2,
        'accent': '#0A9396',
        'panel_hd_bg': '#005F73', 'panel_hd_bg_dark': '#0A2429',
        'relation': 'Existe una <strong>relación inversa</strong> entre libertad económica y pobreza. El cuartil más libre tiene tasas cercanas a cero (<strong>{q1}</strong> en promedio), mientras que el menos libre concentra las mayores (<strong>{q4}</strong>).',
        'theory': 'La apertura comercial, los derechos de propiedad seguros y la estabilidad monetaria generan <strong>empleos formales</strong>, <strong>inversión productiva</strong> y <strong>acceso a bienes importados baratos</strong>, reduciendo la pobreza absoluta a través del crecimiento inclusivo.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank Poverty & Inequality Platform',
        'bol_text': "En Bolivia (EFW: <strong>{efw}</strong>), el <strong>{yval}</strong> de la población vive con menos de US$ 4,20 al día (PPA 2021). A pesar del crecimiento del PIB, el nivel limitado de libertad económica frena una reducción más rápida de la pobreza.",
    },
    {
        'file': 'scatter_life_exp.html',
        'var': 'life_exp',
        'title': 'Libertad Económica y Esperanza de Vida',
        'subtitle': 'Promedio EFW 2000–2023 vs Esperanza de vida al nacer (años)',
        'y_label': 'Esperanza de vida (años)',
        'y_format': "v => v.toFixed(1)",
        'y_axis_fmt': "v => v.toFixed(0)",
        'log_y': False,
        'y_min': '52', 'y_max': '87',
        'reg_order': 2,
        'accent': '#EE9B00',
        'panel_hd_bg': '#A86E00', 'panel_hd_bg_dark': '#2A1F08',
        'relation': 'En los países del cuartil más libre se vive en promedio <strong>{dif} años más</strong> que en los del menos libre. La relación se concentra en el rango medio y alto del índice: con un EFW de 6 o más, cada punto adicional se asocia a <strong>{pend} años</strong> más de vida; por debajo de 6 no se observa una relación clara.',
        'theory': 'Mayor ingreso per cápita permite <strong>mejor nutrición, saneamiento e infraestructura médica</strong>. La libertad de comercio facilita el acceso a medicamentos e insumos. La competencia en servicios de salud mejora la calidad y reduce costos.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una esperanza de vida de <strong>{yval}</strong> años, por debajo del promedio latinoamericano ({lat} años). Restricciones a la competencia en salud y bajo ingreso limitan el progreso sanitario.",
    },
    {
        'file': 'scatter_infant_mort.html',
        'var': 'infant_mort',
        'title': 'Libertad Económica y Mortalidad Infantil',
        'subtitle': 'Promedio EFW 2000–2023 vs Mortalidad infantil (por 1000 nacidos vivos)',
        'y_label': 'Mortalidad infantil (por 1000)',
        'y_format': "v => v.toFixed(1)",
        'y_axis_fmt': "v => v.toFixed(0)",
        'log_y': False,
        'y_min': '0', 'y_max': '75',
        'reg_type': 'exp',
        'reg_order': 2,
        'accent': '#005F73',
        'panel_hd_bg': '#00323D', 'panel_hd_bg_dark': '#08191E',
        'relation': 'La mortalidad infantil <strong>cae drásticamente</strong> conforme aumenta la libertad económica. El cuartil más libre tiene tasas de mortalidad infantil <strong>{razon} veces menores</strong> que el cuartil menos libre.',
        'theory': 'El mecanismo opera a través de <strong>mayor ingreso familiar</strong> (mejor nutrición materna), <strong>inversión en salud pública</strong> financiada por crecimiento, y <strong>acceso a tecnología médica</strong> facilitado por la apertura comercial.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una mortalidad infantil de <strong>{yval} por mil</strong>. Aunque ha mejorado significativamente, sigue por encima del promedio latinoamericano ({lat}), reflejando limitaciones en acceso a salud y nutrición.",
    },
    {
        'file': 'scatter_satisfaction.html',
        'var': 'life_satisfaction',
        'title': 'Libertad Económica y Satisfacción de Vida',
        'subtitle': 'Promedio EFW 2000–2023 vs Evaluación de vida (Cantril Ladder 0-10)',
        'y_label': 'Satisfacción de vida (0-10)',
        'y_format': "v => v.toFixed(2)",
        'y_axis_fmt': "v => v.toFixed(1)",
        'log_y': False,
        'y_min': '3', 'y_max': '8',
        'reg_order': 2,
        'accent': '#DF5D25',
        'panel_hd_bg': '#9B2226', 'panel_hd_bg_dark': '#2A1410',
        'relation': 'Las personas en países económicamente libres reportan <strong>mayor satisfacción vital</strong>. La relación es robusta incluso controlando por ingreso, sugiriendo que la libertad económica contribuye al bienestar subjetivo por vías adicionales al ingreso.',
        'theory': 'La libertad económica aporta bienestar subjetivo a través de: <strong>sentido de autonomía</strong> sobre decisiones económicas propias, <strong>oportunidades de emprendimiento</strong>, <strong>menor corrupción</strong> y <strong>mayor confianza institucional</strong>.',
        'source_detail': 'Fraser Institute EFW 2025, World Happiness Report 2026 (Cantril Ladder)',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una satisfacción de vida de <strong>{yval}</strong>/10. Se ubica por debajo del promedio latinoamericano, una región que tradicionalmente reporta alta satisfacción relativa a su ingreso.",
    },
    {
        'file': 'scatter_epi.html',
        'var': 'epi_score',
        'title': 'Libertad Económica y Desempeño Ambiental',
        'subtitle': 'Promedio EFW 2000–2023 vs Environmental Performance Index 2024',
        'y_label': 'EPI Score (0-100)',
        'y_format': "v => v.toFixed(1)",
        'y_axis_fmt': "v => v.toFixed(0)",
        'log_y': False,
        'y_min': '22', 'y_max': '78',
        'reg_order': 2,
        'accent': '#94D2BD',
        'panel_hd_bg': '#0A9396', 'panel_hd_bg_dark': '#10262B',
        'relation': 'Los países más libres tienen <strong>mejor desempeño ambiental</strong>, contradiciendo la narrativa de que la liberalización económica destruye el medio ambiente. Los países del cuartil más libre puntúan en promedio <strong>{dif} puntos más</strong> en el EPI.',
        'theory': 'La <strong>Curva de Kuznets Ambiental</strong>: mayor ingreso permite invertir en tecnología limpia y regulación ambiental efectiva. Los <strong>derechos de propiedad claros</strong> internalizan externalidades. La <strong>apertura comercial</strong> difunde tecnologías limpias.',
        'source_detail': 'Fraser Institute EFW 2025, Yale Environmental Performance Index 2024',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un EPI de <strong>{yval}</strong>/100. El bajo puntaje refleja desafíos en protección de ecosistemas y calidad del aire, áreas donde la inseguridad jurídica y la falta de derechos de propiedad claros son factores clave.",
    },
    {
        'file': 'scatter_corruption.html',
        'var': 'cpi_score',
        'title': 'Libertad Económica y Ausencia de Corrupción',
        'subtitle': 'Promedio EFW 2000–2023 vs Corruption Perceptions Index 2024',
        'y_label': 'CPI Score (0-100, mayor = menos corrupto)',
        'y_format': "v => v.toFixed(0)",
        'y_axis_fmt': "v => v.toFixed(0)",
        'log_y': False,
        'y_min': '5', 'y_max': '95',
        'reg_order': 2,
        'accent': '#9B2226',
        'panel_hd_bg': '#6B1A1D', 'panel_hd_bg_dark': '#24100F',
        'relation': 'La correlación entre libertad económica y transparencia es de las <strong>más fuertes del análisis</strong>. El cuartil más libre promedia un CPI de <strong>{q1}</strong>, contra <strong>{q4}</strong> en el menos libre.',
        'theory': 'La libertad económica reduce la corrupción al <strong>limitar el poder discrecional</strong> de funcionarios. Menos regulaciones = menos oportunidades de soborno. <strong>Estado de derecho</strong> y <strong>derechos de propiedad</strong> refuerzan instituciones transparentes.',
        'source_detail': 'Fraser Institute EFW 2025, Transparency International CPI 2024',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un CPI de <strong>{yval}</strong>/100, en el tercio inferior mundial. La concentración de poder estatal en la economía y la debilidad del Estado de derecho facilitan la corrupción sistémica.",
    },
    {
        'file': 'scatter_personal_freedom.html',
        'var': 'pf_score',
        'title': 'Libertad Económica y Libertad Personal',
        'subtitle': 'Promedio EFW 2000–2023 vs Personal Freedom Score (HFI 2024)',
        'y_label': 'Libertad Personal (0-10)',
        'y_format': "v => v.toFixed(2)",
        'y_axis_fmt': "v => v.toFixed(0)",
        'log_y': False,
        'y_min': '2', 'y_max': '10',
        'reg_order': 1,
        'accent': '#005F73',
        'panel_hd_bg': '#0C4A6E', 'panel_hd_bg_dark': '#082F49',
        'relation': 'Las libertades económica y personal están <strong>positivamente correlacionadas</strong>. Los países que protegen la propiedad privada y el comercio libre tienden a proteger también la libertad de expresión, religión y asociación.',
        'theory': '<strong>Hayek y Friedman</strong> argumentaron que la libertad económica es <strong>condición necesaria</strong> (aunque no suficiente) para la libertad política. La independencia económica del Estado reduce la capacidad del gobierno de reprimir la disidencia.',
        'source_detail': 'Fraser Institute EFW 2025, Human Freedom Index (Cato/Fraser) 2024',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un índice de libertad personal de <strong>{yval}</strong>/10. La libertad de prensa y la independencia judicial son áreas de preocupación, correlacionadas con el bajo puntaje de libertad económica.",
    },
    {
        'file': 'scatter_hours.html',
        'var': 'hours_worked',
        'title': 'Libertad Económica y Horas Trabajadas',
        'subtitle': 'Promedio EFW 2000–2023 vs Horas trabajadas anuales por trabajador',
        'y_label': 'Horas trabajadas/año',
        'y_format': "v => Math.round(v).toLocaleString('es-BO')",
        'y_axis_fmt': "v => Math.round(v).toLocaleString('es-BO')",
        'log_y': False,
        'y_min': '1300', 'y_max': '2700',
        'reg_order': 1,
        'accent': '#9B2226',
        'panel_hd_bg': '#701A75', 'panel_hd_bg_dark': '#4A044E',
        'relation': 'Los países más libres tienden a trabajar <strong>menos horas</strong> por año. Mayor productividad por hora permite alcanzar el mismo (o mayor) ingreso con menos tiempo de trabajo, liberando tiempo para ocio y familia.',
        'theory': 'La <strong>alta productividad</strong> de economías libres (capital abundante, tecnología, eficiencia institucional) permite la <strong>reducción gradual de jornada</strong> sin sacrificar ingreso — el \\"dividendo de la libertad\\" en forma de tiempo.',
        'source_detail': 'Fraser Institute EFW 2025, Penn World Table 11.0',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un promedio de <strong>{yval}</strong> horas trabajadas al año por trabajador, por encima del promedio latinoamericano ({lat}). La baja productividad obliga a jornadas extensas para subsistir.",
    },
    {
        'file': 'scatter_income_bottom10.html',
        'var': 'income_bottom10',
        'title': 'Libertad Económica e Ingreso del 10% más Pobre',
        'subtitle': 'Promedio EFW 2000–2023 vs Participación del decil inferior en el ingreso',
        'y_label': 'Ingreso del 10% más pobre (% del total)',
        'y_format': "v => v.toFixed(1) + '%'",
        'y_axis_fmt': "v => v.toFixed(1) + '%'",
        'log_y': False,
        'y_min': '0.5', 'y_max': '5',
        'reg_order': 1,
        'accent': '#0A9396',
        'panel_hd_bg': '#115E59', 'panel_hd_bg_dark': '#0D3D3B',
        'relation': 'La participación del decil más pobre en el ingreso nacional es <strong>similar</strong> independientemente del nivel de libertad económica. Sin embargo, dado que el PIB per cápita es mucho mayor en países libres, el <strong>ingreso absoluto</strong> de los más pobres es muy superior.',
        'theory': 'Los pobres en países libres tienen <strong>mayor ingreso absoluto</strong> (PIB per cápita alto × participación estable). La movilidad social y el acceso a mercados competitivos permiten que los ingresos bajos crezcan con la economía.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI',
        'bol_text': "En Bolivia (EFW: <strong>{efw}</strong>), el 10% más pobre recibe el <strong>{yval}</strong> del ingreso, en línea con el promedio latinoamericano ({lat}), una de las regiones más desiguales del mundo. Con un ingreso per cápita bajo, ese decil sigue siendo muy pobre en términos absolutos.",
    },
    {
        'file': 'scatter_democracy.html',
        'var': 'democracy',
        'title': 'Libertad Económica y Democracia',
        'subtitle': 'Promedio EFW 2000–2023 vs Índice de Democracia Electoral (V-Dem v16)',
        'y_label': 'Democracia Electoral (0-1)',
        'y_format': "v => v.toFixed(2)",
        'y_axis_fmt': "v => v.toFixed(1)",
        'log_y': False,
        'y_min': '0', 'y_max': '1',
        'reg_order': 1,
        'accent': '#E57D22',
        'panel_hd_bg': '#7C2D12', 'panel_hd_bg_dark': '#431407',
        'relation': 'La relación es <strong>positiva pero con excepciones notables</strong>: países como Singapur (alta libertad económica, democracia limitada) y otros con democracias formales pero baja libertad económica. La correlación sugiere complementariedad, no causalidad directa.',
        'theory': 'La libertad económica crea una <strong>clase media independiente</strong> que demanda participación política. La <strong>descentralización del poder económico</strong> dificulta la consolidación autocrática. Sin embargo, la causalidad puede operar en ambas direcciones.',
        'source_detail': 'Fraser Institute EFW 2025, V-Dem v16 (2025)',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un índice de democracia electoral de <strong>{yval}</strong>. A pesar de elecciones regulares, la concentración de poder económico en el Estado debilita los contrapesos democráticos.",
    },
]


# Formato de cada indicador (es-BO, vía el molde): valor y rótulo de eje
FORMATO = {
    'gdp_pc_ppp':        ("function (v) { return '$' + PM.num(v, 0); }", "function (v) { return '$' + PM.tick(v); }"),
    'poverty_365':       ("function (v) { return PM.pct(v, 1); }",       "function (v) { return PM.tick(v) + '%'; }"),
    'life_exp':          ("function (v) { return PM.num(v, 1); }",       "PM.tick"),
    'infant_mort':       ("function (v) { return PM.num(v, 1); }",       "PM.tick"),
    'life_satisfaction': ("function (v) { return PM.num(v, 2); }",       "PM.tick"),
    'epi_score':         ("function (v) { return PM.num(v, 1); }",       "PM.tick"),
    'cpi_score':         ("function (v) { return PM.num(v, 0); }",       "PM.tick"),
    'pf_score':          ("function (v) { return PM.num(v, 2); }",       "PM.tick"),
    'hours_worked':      ("function (v) { return PM.num(v, 0); }",       "PM.tick"),
    'income_bottom10':   ("function (v) { return PM.pct(v, 1); }",       "function (v) { return PM.tick(v) + '%'; }"),
    'democracy':         ("function (v) { return PM.num(v, 2); }",       "PM.tick"),
}
# Nombre corto para el eje (el largo queda en la bajada) y piso/techo naturales del indicador
EJE = {
    'gdp_pc_ppp': ('PIB per cápita PPP (USD)', '500', '200000'),      # escala log: sin la década vacía de $1.000.000
    'poverty_365': ('Pobreza (% de la población)', '0', 'null'),
    'life_exp': ('Esperanza de vida (años)', '50', '90'),
    'infant_mort': ('Mortalidad infantil (por 1.000)', '0', 'null'),
    'life_satisfaction': ('Satisfacción de vida (0–10)', 'null', 'null'),
    'epi_score': ('Desempeño ambiental (EPI, 0–100)', 'null', 'null'),
    'cpi_score': ('Percepción de corrupción (CPI, 0–100)', 'null', 'null'),
    'pf_score': ('Libertad personal (0–10)', 'null', 'null'),
    'hours_worked': ('Horas trabajadas al año', 'null', 'null'),
    'income_bottom10': ('Ingreso del 10% más pobre (% del total)', '0', 'null'),
    'democracy': ('Democracia electoral (0–1)', '0', '1'),
}
# En el teléfono, el eje que se come el ancho pasa a una unidad más corta («$100.000» → «100»)
EJE_MOVIL = {
    'gdp_pc_ppp': ("function (v) { return PM.tick(v / 1000); }", 'PIB per cápita PPP (miles de USD)'),
}
# El acento va de fondo del botón activo: tiene que sostener texto blanco (≥ 3:1)
ACENTO = {'#EE9B00': '#A86E00', '#94D2BD': '#0A9396', '#E57D22': '#DF5D25'}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es" data-theme="light" style="--acento:@@ACENTO@@">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>@@TITLE@@ · Populi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="comun/monitor.css" />
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <script src="comun/monitor.js"></script>
</head>
<body>
  <div class="wrap">
    <div class="sec-hd">
      <div class="sec-title"><span class="accent-bar"></span>@@TITLE@@</div>
      <div class="sec-sub">@@SUBTITLE@@</div>
    </div>

    <div class="hz-bar">
      <div class="hz-item"><span class="hz-lbl">Color</span><div class="hz-grp" id="b-color"></div></div>
    </div>

    <div class="kpi-grid" id="kpis"></div>

    <div class="main-grid">
      <div class="chart-card">
        <div class="chart-ctrl">
          <div class="ley" id="leyenda"></div>
          <div class="tog-grp" id="regiones" style="display:none"></div>
        </div>
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span>Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t">Lectura del indicador</span><span class="panel-hd-d">EFW 2000–2023</span></div>
        <div class="panel-body" id="panel"></div>
      </div>
    </div>

    <div class="edu-grid" id="preguntas"></div>
    <div class="source"><span class="source-txt" id="fuente"></span></div>
  </div>

  <script>
  (function () {
    var C = PM.C;
    var VAR = '@@VAR@@', Y_CORTO = '@@Y_CORTO@@', LOG = @@LOG@@, Y_MIN = @@Y_MIN@@, Y_MAX = @@Y_MAX@@;
    var REG_TIPO = '@@REG_TYPE@@', REG_ORDEN = @@REG_ORDER@@, ACENTO = '@@ACENTO@@';
    var FMT = @@FMT@@, FMT_EJE = @@FMT_EJE@@, FMT_EJE_M = @@FMT_EJE_M@@, Y_CORTO_M = '@@Y_CORTO_M@@';
    var RELACION = @@RELACION@@, TEORIA = @@TEORIA@@, BOL_TXT = @@BOL_TXT@@, FUENTE_DET = @@FUENTE_DET@@;
    // Cuartiles del índice: escala ORDINAL de la marca (la misma del mapa), del más libre (turquesa)
    // al menos libre (rojo). Por región: modo Foco (la región elegida en rojo, el resto en gris tenue):
    // siete colores no se distinguen entre sí cuando las burbujas se mezclan.
    var QC = { 1: C.turquesa, 2: C.menta, 3: C.oro, 4: C.rojo };
    var QN = { 1: 'Cuartil 1 · más libre', 2: 'Cuartil 2', 3: 'Cuartil 3', 4: 'Cuartil 4 · menos libre' };
    var REGIONES = [['Latin America & the Caribbean', 'América Latina y el Caribe'], ['North America', 'Norteamérica'],
      ['Europe & Central Asia', 'Europa y Asia Central'], ['East Asia & Pacific', 'Asia Oriental y Pacífico'],
      ['South Asia', 'Asia del Sur'], ['Middle East & North Africa', 'Medio Oriente y Norte de África'],
      ['Sub-Saharan Africa', 'África Subsahariana']];
    var REGION = {};
    REGIONES.forEach(function (r) { REGION[r[0]] = r[1]; });
    var estado = { color: 'cuartil', region: 'Latin America & the Caribbean' };
    var PTS, BOL, AJ, CORTES, CORTE_Q1, NOMBRE = {}, grafico;
    var nombre = function (x) { return NOMBRE[x.iso] || x.country; };

    var media = function (a) { return a.length ? a.reduce(function (s, v) { return s + v; }, 0) / a.length : null; };
    var valores = function (f) { return PTS.filter(f).map(function (x) { return x[VAR]; }); };
    var tenue = function () { return PM.dk() ? '#3A4549' : '#C9CDCE'; };
    var tipoAjuste = function (masc) { return REG_TIPO === 'exp' ? 'exponencial' : REG_ORDEN === 2 ? (masc ? 'cuadrático' : 'cuadrática') : 'lineal'; };
    function poblacion(n) {
      if (n >= 1e9) return PM.num(n / 1e9, 2) + ' mil millones';
      if (n >= 1e6) return PM.num(n / 1e6, 1) + ' millones';
      return PM.num(n / 1e3, 0) + ' mil';
    }

    // ── tendencia: polinómica (sobre log10 si el eje es logarítmico) o exponencial ────────────
    function regresion(pts, orden) {
      var n = pts.length, xs = pts.map(function (p) { return p[0]; }), ys = pts.map(function (p) { return p[1]; });
      var ym = ys.reduce(function (s, v) { return s + v; }, 0) / n, ssTot = ys.reduce(function (s, v) { return s + (v - ym) * (v - ym); }, 0), f, i;
      if (orden <= 1) {
        var sx = 0, sy = 0, sxy = 0, sx2 = 0;
        for (i = 0; i < n; i++) { sx += xs[i]; sy += ys[i]; sxy += xs[i] * ys[i]; sx2 += xs[i] * xs[i]; }
        var b = (n * sxy - sx * sy) / (n * sx2 - sx * sx), a = (sy - b * sx) / n;
        f = function (x) { return a + b * x; };
      } else {
        var s = [0, 0, 0, 0, 0], t = [0, 0, 0];
        for (i = 0; i < n; i++) { var x = xs[i], y = ys[i], x2 = x * x; s[0]++; s[1] += x; s[2] += x2; s[3] += x * x2; s[4] += x2 * x2; t[0] += y; t[1] += x * y; t[2] += x2 * y; }
        var A = [[s[0], s[1], s[2]], [s[1], s[2], s[3]], [s[2], s[3], s[4]]];
        var det = function (m) { return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]); };
        var D = det(A);
        var c0 = det([[t[0], A[0][1], A[0][2]], [t[1], A[1][1], A[1][2]], [t[2], A[2][1], A[2][2]]]) / D;
        var c1 = det([[A[0][0], t[0], A[0][2]], [A[1][0], t[1], A[1][2]], [A[2][0], t[2], A[2][2]]]) / D;
        var c2 = det([[A[0][0], A[0][1], t[0]], [A[1][0], A[1][1], t[1]], [A[2][0], A[2][1], t[2]]]) / D;
        f = function (x) { return c0 + c1 * x + c2 * x * x; };
      }
      var ssRes = pts.reduce(function (acc, p) { var e = p[1] - f(p[0]); return acc + e * e; }, 0);
      return { f: f, r2: ssTot > 0 ? 1 - ssRes / ssTot : 0 };
    }
    function regresionExp(pts) {
      var n = pts.length, xs = pts.map(function (p) { return p[0]; }), ys = pts.map(function (p) { return p[1]; });
      var ym = ys.reduce(function (s, v) { return s + v; }, 0) / n, ssTot = ys.reduce(function (s, v) { return s + (v - ym) * (v - ym); }, 0);
      var ly = ys.map(function (v) { return Math.log(Math.max(v, 0.1)); }), sx = 0, sl = 0, sxl = 0, sx2 = 0, i;
      for (i = 0; i < n; i++) { sx += xs[i]; sl += ly[i]; sxl += xs[i] * ly[i]; sx2 += xs[i] * xs[i]; }
      var b = (n * sxl - sx * sl) / (n * sx2 - sx * sx), a = Math.exp((sl - b * sx) / n);
      for (var it = 0; it < 30; it++) {
        var g00 = 0, g01 = 0, g11 = 0, r0 = 0, r1 = 0;
        for (i = 0; i < n; i++) { var e = Math.exp(b * xs[i]), res = ys[i] - a * e; g00 += e * e; g01 += a * xs[i] * e * e; g11 += a * a * xs[i] * xs[i] * e * e; r0 += e * res; r1 += a * xs[i] * e * res; }
        var dt = g00 * g11 - g01 * g01;
        if (Math.abs(dt) < 1e-30) break;
        a += (g11 * r0 - g01 * r1) / dt; b += (g00 * r1 - g01 * r0) / dt;
      }
      var f = function (x) { return Math.max(0, a * Math.exp(b * x)); };
      var ssRes = pts.reduce(function (acc, p) { var r = p[1] - f(p[0]); return acc + r * r; }, 0);
      return { f: f, r2: ssTot > 0 ? 1 - ssRes / ssTot : 0 };
    }
    function ajuste() {
      if (REG_TIPO === 'exp') return regresionExp(PTS.map(function (x) { return [x.efw_avg, x[VAR]]; }));
      return regresion(PTS.map(function (x) { return [x.efw_avg, LOG ? Math.log10(x[VAR]) : x[VAR]]; }), REG_ORDEN);
    }

    PM.cargar(['consolidated.json', 'paises_es.json']).then(function (r) {
      NOMBRE = r[1].iso;
      PTS = r[0].filter(function (x) { return x[VAR] != null && x.efw_avg != null && x.population != null; });
      BOL = PTS.filter(function (x) { return x.iso === 'BOL'; })[0];
      AJ = ajuste();
      // Cortes entre cuartiles del índice, desde el dato (los 165 países, no sólo los que tienen este
      // indicador): punto medio entre el máximo de un cuartil y el mínimo del siguiente
      var todos = r[0].filter(function (x) { return x.efw_avg != null && x.efw_quartile; });
      var lim = function (q, f) { return f.apply(null, todos.filter(function (x) { return x.efw_quartile === q; }).map(function (x) { return x.efw_avg; })); };
      CORTES = [(lim(4, Math.max) + lim(3, Math.min)) / 2, (lim(3, Math.max) + lim(2, Math.min)) / 2, (lim(2, Math.max) + lim(1, Math.min)) / 2];
      CORTE_Q1 = lim(1, Math.min);
      PM.botonera(document.getElementById('b-color'), [['cuartil', 'Cuartil EFW'], ['region', 'Región']], estado.color, function (v) {
        estado.color = v; document.getElementById('regiones').style.display = v === 'region' ? '' : 'none'; leyenda(); grafico.redibujar();
      });
      pastillasRegion();
      leyenda(); cifras(); panel();
      var el = document.getElementById('chart');
      el.innerHTML = '';
      grafico = PM.montar(el, opciones);
      PM.alCambiarTema(function () { leyenda(); cifras(); panel(); });
      PM.preguntas(document.getElementById('preguntas'), PREGUNTAS);
      // descargas: la leyenda de la imagen repite la del gráfico; el CSV trae una fila por país
      PM.leyendaImagen = function () {
        var it = estado.color === 'cuartil'
          ? [1, 2, 3, 4].map(function (q) { return { name: QN[q], color: PM.col(QC[q]), forma: 'punto' }; })
          : [{ name: REGION[estado.region], color: C.rojo, forma: 'punto' }, { name: 'Resto del mundo', color: tenue(), forma: 'punto' }];
        it.push({ name: 'Tendencia ' + tipoAjuste() + ' · R² ' + PM.num(AJ.r2, 2), color: PM.dk() ? '#C9CDCE' : '#5C6B70', forma: 'punteada' });
        return it;
      };
      PM.tablaDatos = function () {
        return {
          cols: ['País', 'ISO3', 'Región', 'Cuartil EFW', 'EFW promedio 2000-2023', Y_CORTO, 'Población'],
          filas: PTS.slice().sort(function (a, b) { return b.efw_avg - a.efw_avg; }).map(function (x) {
            return [nombre(x), x.iso, REGION[x.region] || x.region, x.efw_quartile, x.efw_avg, x[VAR], x.population];
          })
        };
      };
      document.getElementById('fuente').innerHTML = 'Fuente: ' + FUENTE_DET.replace('Fraser Institute', '<a href="https://www.fraserinstitute.org/economic-freedom" target="_blank" rel="noopener">Fraser Institute</a>') + ' · Elaboración: Centro de Estudios POPULI';
    }).catch(function (e) { console.error(e); PM.error(document.getElementById('chart')); });

    function pastillasRegion() {
      var el = document.getElementById('regiones');
      el.innerHTML = REGIONES.map(function (r) { return '<button type="button" class="pill" data-r="' + r[0] + '"><span class="lp area"></span>' + r[1] + '</button>'; }).join('');
      el.querySelectorAll('.pill').forEach(function (b) {
        b.addEventListener('click', function () { estado.region = b.dataset.r; pintarRegiones(); leyenda(); grafico.redibujar(); });
      });
      pintarRegiones();
      PM.alCambiarTema(pintarRegiones);
    }
    function pintarRegiones() {
      var dk = PM.dk();
      document.querySelectorAll('#regiones .pill').forEach(function (b) {
        var on = b.dataset.r === estado.region;
        b.style.setProperty('--pc', on ? C.rojo : tenue());
        b.style.setProperty('--pf', on ? PM.rgba(C.rojo, dk ? 0.16 : 0.09) : 'transparent');
        b.style.setProperty('--pb', on ? PM.rgba(C.rojo, dk ? 0.6 : 0.45) : 'var(--border)');
        b.setAttribute('aria-pressed', on);
      });
    }

    function leyenda() {
      var items = estado.color === 'cuartil'
        ? [1, 2, 3, 4].map(function (q) { return [PM.col(QC[q]), QN[q]]; })
        : [[C.rojo, REGION[estado.region]], [tenue(), 'Resto del mundo']];
      document.getElementById('leyenda').innerHTML = items.map(function (it) {
        return '<span class="ley-i"><span class="ley-d" style="background:' + it[0] + '"></span>' + it[1] + '</span>';
      }).join('') + '<span class="ley-i"><span class="ley-l"></span>Tendencia ' + tipoAjuste() + ' · <span class="ley-r2">R² ' + PM.num(AJ.r2, 2) + '</span></span>';
    }

    function cifras() {
      var q1 = valores(function (x) { return x.efw_quartile === 1; }), q4 = valores(function (x) { return x.efw_quartile === 4; });
      document.getElementById('kpis').innerHTML =
        PM.kpi({ color: C.turquesa, rotulo: 'Cuartil más libre', valor: FMT(media(q1)), delta: 'promedio · ' + q1.length + ' países', tono: 'neutro' }) +
        PM.kpi({ color: C.rojo, rotulo: 'Cuartil menos libre', valor: FMT(media(q4)), delta: 'promedio · ' + q4.length + ' países', tono: 'neutro' }) +
        PM.kpi({ color: C.tinta, rotulo: 'Bolivia', valor: BOL ? FMT(BOL[VAR]) : '—', delta: BOL ? 'EFW ' + PM.num(BOL.efw_avg, 2) + ' · cuartil ' + BOL.efw_quartile : 'sin dato', tono: 'neutro' }) +
        PM.kpi({ color: C.pizarra, rotulo: 'Tendencia', valor: 'R² ' + PM.num(AJ.r2, 2), delta: 'ajuste ' + tipoAjuste(true), tono: 'neutro' });
    }

    // Cifras del texto que dependen del dato: {q1} y {q4} (promedio de los cuartiles extremos), {razon}
    // (cuántas veces), {dif} (diferencia), {lat} (promedio de América Latina y el Caribe), {corte} (EFW
    // mínimo del cuartil más libre), {pend} (pendiente con EFW de 6 o más), {efw}, {q}, {yval} (Bolivia)
    function pendiente(desde) {
      var p = PTS.filter(function (x) { return x.efw_avg >= desde; }), n = p.length, sx = 0, sy = 0, sxy = 0, sx2 = 0;
      p.forEach(function (x) { sx += x.efw_avg; sy += x[VAR]; sxy += x.efw_avg * x[VAR]; sx2 += x.efw_avg * x.efw_avg; });
      return (n * sxy - sx * sy) / (n * sx2 - sx * sx);
    }
    function conDatos(t) {
      var m1 = media(valores(function (x) { return x.efw_quartile === 1; })), m4 = media(valores(function (x) { return x.efw_quartile === 4; }));
      var lat = media(valores(function (x) { return x.region === 'Latin America & the Caribbean'; }));
      t = t.replace('{q1}', FMT(m1)).replace('{q4}', FMT(m4)).replace('{corte}', PM.num(CORTE_Q1, 2))
        .replace('{razon}', PM.num(Math.max(m1, m4) / Math.min(m1, m4), 1)).replace('{dif}', PM.num(Math.abs(m1 - m4), 1)).replace('{lat}', FMT(lat));
      if (t.indexOf('{pend}') >= 0) t = t.replace('{pend}', PM.num(pendiente(6), 1));
      if (BOL) t = t.replace('{efw}', PM.num(BOL.efw_avg, 2)).replace('{q}', BOL.efw_quartile).replace('{yval}', FMT(BOL[VAR]));
      return t;
    }
    function panel() {
      document.getElementById('panel').innerHTML =
        PM.pb(ACENTO, 'Relación observada', null, conDatos(RELACION)) +
        PM.pb(ACENTO, 'Marco teórico', null, TEORIA) +
        PM.pb(ACENTO, 'Bolivia', null, BOL ? conDatos(BOL_TXT) : 'Sin dato para Bolivia en este indicador.') +
        PM.ctx('<strong>Fuente:</strong> ' + FUENTE_DET + '. El tamaño de cada burbuja es la población del país.');
    }

    function opciones() {
      var dk = PM.dk(), card = PM.var('--card') || '#fff', chico = PM.pequeno(), linea = dk ? '#3A4549' : '#C9CDCE';
      var maxPop = Math.max.apply(null, PTS.map(function (x) { return x.population; })), minB = chico ? 3 : 4, maxB = chico ? 30 : 44;
      var datos = PTS.map(function (x) {
        var foco = estado.color !== 'region' || x.region === estado.region, esBol = x.iso === 'BOL';
        return {
          value: [x.efw_avg, x[VAR], x.population, nombre(x), x.iso, x.efw_quartile, x.region],
          symbolSize: minB + Math.sqrt(x.population / maxPop) * maxB,
          itemStyle: {
            color: estado.color === 'cuartil' ? PM.col(QC[x.efw_quartile]) : (foco ? C.rojo : tenue()),
            opacity: esBol ? 1 : foco ? 0.7 : 0.6,
            borderColor: esBol ? (dk ? '#F1F5F9' : '#001219') : card, borderWidth: esBol ? 2 : 0.8
          },
          label: esBol ? { show: true, formatter: 'Bolivia', position: 'top', distance: 5, fontFamily: PM.inter(), fontSize: chico ? 10 : 11,
            fontWeight: 700, color: dk ? '#F1F5F9' : '#001219', textBorderColor: card, textBorderWidth: 3 } : { show: false },
          z: esBol ? 5 : foco ? 3 : 2
        };
      });
      datos.sort(function (a, b) { return a.z - b.z; });     // el contexto abajo, la región elegida y Bolivia arriba
      var xs = PTS.map(function (x) { return x.efw_avg; }), x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), tendencia = [];
      for (var i = 0; i < 80; i++) { var x = x0 + (x1 - x0) * i / 79, y = AJ.f(x); tendencia.push([x, LOG ? Math.pow(10, y) : Math.max(0, y)]); }
      // franjas de los cuartiles del índice: cortes calculados desde el dato, colores de la escala ordinal
      // (en el modo región, el color ya codifica la región: las franjas pasan a gris alterno)
      var franjas = [[3, CORTES[0], C.rojo], [CORTES[0], CORTES[1], C.oro], [CORTES[1], CORTES[2], C.menta], [CORTES[2], 9, C.turquesa]].map(function (b, i) {
        var fondo = estado.color === 'cuartil' ? PM.rgba(b[2], dk ? 0.08 : 0.06) : (i % 2 ? 'rgba(0,0,0,0)' : PM.rgba(C.gris, dk ? 0.08 : 0.07));
        return [{ xAxis: b[0] }, { xAxis: b[1], itemStyle: { color: fondo } }];
      });
      return {
        grid: PM.grid({ top: 28, bottom: chico ? 24 : 28 }),
        xAxis: PM.ejeY({ fmt: PM.tick, extra: {
          type: 'value', min: 3, max: 9, interval: 1, splitNumber: 6,
          name: chico ? 'Libertad económica (EFW, 0 a 10)' : 'Libertad económica · índice EFW, promedio 2000–2023 (0 a 10)',
          nameLocation: 'middle', nameGap: 26, nameTextStyle: { align: 'center' },
          splitLine: { show: false }, axisLine: { show: true, lineStyle: { color: linea } }, axisTick: { show: true, length: 4, lineStyle: { color: linea } }
        } }),
        yAxis: PM.ejeY({ unidad: chico ? Y_CORTO_M : Y_CORTO, fmt: chico ? FMT_EJE_M : FMT_EJE, extra: {
          type: LOG ? 'log' : 'value', min: Y_MIN, max: Y_MAX, scale: !LOG && Y_MIN === null, nameTextStyle: { align: 'left' },
          axisLabel: LOG ? { showMinLabel: false, showMaxLabel: false } : {}
        } }),
        tooltip: PM.tooltip(function (p) {
          if (p.seriesIndex !== 0) return '';
          // las tres filas describen la misma burbuja: sin claves; el cuartil, con su color, en el pie
          var v = p.value;
          return PM.ttTitulo(v[3] + ' · ' + v[4], REGION[v[6]] || v[6]) +
            PM.ttFila(null, 'Libertad económica (EFW)', PM.num(v[0], 2)) +
            PM.ttFila(null, Y_CORTO, FMT(v[1])) +
            PM.ttFila(null, 'Población', poblacion(v[2])) +
            PM.ttPie('<span style="display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;background:' +
              PM.col(QC[v[5]]) + '"></span>' + QN[v[5]] + ' de libertad económica');
        }, { trigger: 'item' }),
        series: [
          { type: 'scatter', data: datos, markArea: { silent: true, data: franjas }, emphasis: { focus: 'self', itemStyle: { opacity: 1 } } },
          { type: 'line', data: tendencia, symbol: 'none', smooth: true, silent: true, z: 4, tooltip: { show: false },
            lineStyle: { color: dk ? 'rgba(226,232,240,.55)' : 'rgba(0,18,25,.45)', width: 1.5, type: [6, 4] } }
        ]
      };
    }

    var PREGUNTAS = [
      ['¿Qué mide el índice de libertad económica?', 'El índice <strong>Economic Freedom of the World</strong> (EFW) del Fraser Institute califica de 0 a 10 a 165 jurisdicciones en cinco áreas: tamaño del gobierno, sistema legal y derechos de propiedad, moneda sana, libertad para comerciar internacionalmente y regulación. Este gráfico usa el <strong>promedio 2000–2023</strong> de cada país, que resume dos décadas y no un año suelto.'],
      ['¿Cómo se lee este gráfico?', 'Cada burbuja es un país: cuanto más a la derecha, más libertad económica; la altura es el indicador y el tamaño, la población. Las franjas del fondo marcan los <strong>cuartiles</strong> del índice (cada uno reúne a una cuarta parte de los países) y la línea punteada es la <strong>tendencia ajustada</strong>: su R² dice qué parte de las diferencias entre países acompaña a la libertad económica.'],
      ['¿Correlación es causalidad?', 'No necesariamente. El gráfico muestra una <strong>asociación entre países</strong>. Otros factores —instituciones, geografía, historia, capital humano— también influyen, y la relación puede operar en ambos sentidos. Se lee como evidencia de una regularidad, no como prueba de una causa única.']
    ];
  })();
  </script>
</body>
</html>
"""

for s in scatters:
    fmt, fmt_eje = FORMATO[s['var']]
    corto, ymin, ymax = EJE[s['var']]
    reemplazos = {
        '@@TITLE@@': s['title'], '@@SUBTITLE@@': s['subtitle'], '@@VAR@@': s['var'],
        '@@ACENTO@@': ACENTO.get(s['accent'], s['accent']), '@@Y_CORTO@@': corto,
        '@@LOG@@': 'true' if s['log_y'] else 'false', '@@Y_MIN@@': ymin, '@@Y_MAX@@': ymax,
        '@@REG_TYPE@@': s.get('reg_type', 'poly'), '@@REG_ORDER@@': str(s['reg_order']),
        '@@FMT@@': fmt, '@@FMT_EJE@@': fmt_eje,
        '@@FMT_EJE_M@@': EJE_MOVIL.get(s['var'], (fmt_eje, corto))[0], '@@Y_CORTO_M@@': EJE_MOVIL.get(s['var'], (fmt_eje, corto))[1],
        '@@RELACION@@': json.dumps(s['relation'], ensure_ascii=False),
        '@@TEORIA@@': json.dumps(s['theory'], ensure_ascii=False),
        '@@BOL_TXT@@': json.dumps(s['bol_text'], ensure_ascii=False),
        '@@FUENTE_DET@@': json.dumps(s['source_detail'], ensure_ascii=False),
    }
    html = TEMPLATE
    for k, v in reemplazos.items():
        html = html.replace(k, v)
    assert '@@' not in html, s['file']
    with open(os.path.join(EMBED_DIR, s['file']), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  OK {s['file']}")

print(f"\n{len(scatters)} embeds generados en {EMBED_DIR}/")
