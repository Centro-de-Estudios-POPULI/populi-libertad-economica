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
        'accent': '#10B981',
        'panel_hd_bg': '#065F46', 'panel_hd_bg_dark': '#1A3A2A',
        'relation': 'Los países con <strong>mayor libertad económica sostenida</strong> muestran niveles de ingreso per cápita significativamente más altos. El cuartil superior (EFW > 7.5) tiene un PIB per cápita promedio <strong>6 veces mayor</strong> que el cuartil inferior.',
        'theory': 'La libertad económica —derechos de propiedad, moneda sana, libre comercio, regulación eficiente y gobierno limitado— facilita la <strong>acumulación de capital</strong>, la <strong>innovación</strong> y la <strong>asignación eficiente de recursos</strong>, motores fundamentales del crecimiento a largo plazo.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW promedio: <strong>{efw}</strong>, Cuartil {q}) tiene un PIB per cápita PPP de <strong>{yval}</strong>. Se ubica en el rango medio-bajo de libertad económica, por debajo del promedio regional latinoamericano.",
    },
    {
        'file': 'scatter_poverty.html',
        'var': 'poverty_365',
        'title': 'Libertad Económica y Pobreza',
        'subtitle': 'Promedio EFW 2000–2023 vs Tasa de pobreza (<$3.65/día)',
        'y_label': 'Pobreza (% población < $3.65/día)',
        'y_format': "v => v.toFixed(1) + '%'",
        'y_axis_fmt': "v => v.toFixed(0) + '%'",
        'log_y': False,
        'y_min': '0', 'y_max': '95',
        'reg_type': 'exp',
        'reg_order': 2,
        'accent': '#EF4444',
        'panel_hd_bg': '#7F1D1D', 'panel_hd_bg_dark': '#3A1515',
        'relation': 'Existe una relación <strong>inversamente proporcional</strong> entre libertad económica y pobreza extrema. Los países del cuartil más libre tienen tasas de pobreza cercanas a cero, mientras que los menos libres concentran las mayores tasas.',
        'theory': 'La apertura comercial, los derechos de propiedad seguros y la estabilidad monetaria generan <strong>empleos formales</strong>, <strong>inversión productiva</strong> y <strong>acceso a bienes importados baratos</strong>, reduciendo la pobreza absoluta a través del crecimiento inclusivo.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank Poverty & Inequality Platform',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una tasa de pobreza de <strong>{yval}</strong> de su población bajo $3.65/día. A pesar del crecimiento del PIB, el nivel de libertad económica limitado frena la reducción acelerada de la pobreza.",
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
        'accent': '#8B5CF6',
        'panel_hd_bg': '#4C1D95', 'panel_hd_bg_dark': '#2D1065',
        'relation': 'Los países económicamente más libres viven en promedio <strong>15 años más</strong> que los menos libres. La relación es particularmente fuerte en el rango bajo de EFW (4-6), donde pequeñas mejoras se asocian a grandes ganancias en salud.',
        'theory': 'Mayor ingreso per cápita permite <strong>mejor nutrición, saneamiento e infraestructura médica</strong>. La libertad de comercio facilita el acceso a medicamentos e insumos. La competencia en servicios de salud mejora la calidad y reduce costos.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una esperanza de vida de <strong>{yval}</strong> años, por debajo del promedio latinoamericano (~75 años). Restricciones a la competencia en salud y bajo ingreso limitan el progreso sanitario.",
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
        'accent': '#EC4899',
        'panel_hd_bg': '#831843', 'panel_hd_bg_dark': '#4A0E25',
        'relation': 'La mortalidad infantil <strong>cae drásticamente</strong> conforme aumenta la libertad económica. El cuartil más libre tiene tasas de mortalidad infantil <strong>7 veces menores</strong> que el cuartil menos libre.',
        'theory': 'El mecanismo opera a través de <strong>mayor ingreso familiar</strong> (mejor nutrición materna), <strong>inversión en salud pública</strong> financiada por crecimiento, y <strong>acceso a tecnología médica</strong> facilitado por la apertura comercial.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una mortalidad infantil de <strong>{yval} por mil</strong>. Aunque ha mejorado significativamente, sigue por encima del promedio regional, reflejando limitaciones en acceso a salud y nutrición.",
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
        'accent': '#F59E0B',
        'panel_hd_bg': '#78350F', 'panel_hd_bg_dark': '#3D1A08',
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
        'accent': '#059669',
        'panel_hd_bg': '#064E3B', 'panel_hd_bg_dark': '#022C22',
        'relation': 'Los países más libres tienen <strong>mejor desempeño ambiental</strong>, contradiciendo la narrativa de que la liberalización económica destruye el medio ambiente. Los países del cuartil superior puntuan en promedio <strong>20 puntos más</strong> en el EPI.',
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
        'accent': '#6366F1',
        'panel_hd_bg': '#312E81', 'panel_hd_bg_dark': '#1E1B4B',
        'relation': 'La correlación entre libertad económica y transparencia es de las <strong>más fuertes del análisis</strong>. Los países del cuartil más libre promedian CPI de <strong>65+</strong>, contra menos de <strong>27</strong> en el cuartil inferior.',
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
        'accent': '#0EA5E9',
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
        'accent': '#D946EF',
        'panel_hd_bg': '#701A75', 'panel_hd_bg_dark': '#4A044E',
        'relation': 'Los países más libres tienden a trabajar <strong>menos horas</strong> por año. Mayor productividad por hora permite alcanzar el mismo (o mayor) ingreso con menos tiempo de trabajo, liberando tiempo para ocio y familia.',
        'theory': 'La <strong>alta productividad</strong> de economías libres (capital abundante, tecnología, eficiencia institucional) permite la <strong>reducción gradual de jornada</strong> sin sacrificar ingreso — el \\"dividendo de la libertad\\" en forma de tiempo.',
        'source_detail': 'Fraser Institute EFW 2025, Penn World Table 11.0',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un promedio de <strong>{yval}</strong> horas trabajadas al año por trabajador, de las más altas de la región. La baja productividad obliga a jornadas extensas para subsistir.",
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
        'accent': '#14B8A6',
        'panel_hd_bg': '#115E59', 'panel_hd_bg_dark': '#0D3D3B',
        'relation': 'La participación del decil más pobre en el ingreso nacional es <strong>similar</strong> independientemente del nivel de libertad económica. Sin embargo, dado que el PIB per cápita es mucho mayor en países libres, el <strong>ingreso absoluto</strong> de los más pobres es muy superior.',
        'theory': 'Los pobres en países libres tienen <strong>mayor ingreso absoluto</strong> (PIB per cápita alto × participación estable). La movilidad social y el acceso a mercados competitivos permiten que los ingresos bajos crezcan con la economía.',
        'source_detail': 'Fraser Institute EFW 2025, World Bank WDI',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una participación del 10% más pobre de <strong>{yval}</strong>. Aunque relativamente equitativo en distribución, el bajo nivel absoluto de ingreso per cápita significa que el decil inferior sigue siendo muy pobre en términos absolutos.",
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
        'accent': '#F97316',
        'panel_hd_bg': '#7C2D12', 'panel_hd_bg_dark': '#431407',
        'relation': 'La relación es <strong>positiva pero con excepciones notables</strong>: países como Singapur (alta libertad económica, democracia limitada) y otros con democracias formales pero baja libertad económica. La correlación sugiere complementariedad, no causalidad directa.',
        'theory': 'La libertad económica crea una <strong>clase media independiente</strong> que demanda participación política. La <strong>descentralización del poder económico</strong> dificulta la consolidación autocrática. Sin embargo, la causalidad puede operar en ambas direcciones.',
        'source_detail': 'Fraser Institute EFW 2025, V-Dem v16 (2025)',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un índice de democracia electoral de <strong>{yval}</strong>. A pesar de elecciones regulares, la concentración de poder económico en el Estado debilita los contrapesos democráticos.",
    },
]

TEMPLATE = '''<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} - Populi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..800&family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>
    :root {{
      --populi:#8B1A1A; --populi-light:#C00000;
      --cream:#F5EFE0; --brown-dark:#3D2B1F;
      --navy:#0D1B2A; --navy-light:#1A2940; --slate:#475569; --slate-light:#64748B;
      --warm-white:#FAF8F3; --light-gray:#F1EDE5; --border:#E2DDD3; --dark-border:#2A3A50;
      --bg:var(--warm-white); --card:#FFFFFF; --text:var(--brown-dark); --muted:var(--slate-light);
      --accent:{accent};
      --radius:12px;
    }}
    [data-theme="dark"] {{
      --bg:#080808; --card:#141414; --text:#E2E8F0; --muted:#64748B;
      --border:#2A3A50; --light-gray:#1A1A1A; --cream:#1A2940;
    }}
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased;transition:background .25s,color .25s}}
    .wrap{{max-width:1200px;margin:0 auto;padding:20px 16px}}
    .sec-hd{{margin-bottom:12px}}
    .sec-title{{font-family:'Playfair Display',Georgia,serif;font-size:1.55rem;font-weight:700;color:var(--navy);display:flex;align-items:center;gap:10px;line-height:1.15}}
    [data-theme="dark"] .sec-title{{color:#fff}}
    .accent-bar{{width:4px;height:26px;background:var(--accent);border-radius:2px;flex-shrink:0}}
    .sec-sub{{font-size:.78rem;color:var(--muted);padding-left:14px;margin-top:2px}}
    [data-theme="dark"] .sec-sub{{color:rgba(255,255,255,.4)}}
    .controls-row{{display:flex;align-items:center;gap:8px;margin-bottom:6px;padding-left:14px;flex-wrap:wrap}}
    .hz-lbl{{font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}
    .hz-grp{{display:flex;flex-wrap:wrap;gap:0;background:var(--light-gray);border-radius:8px;padding:2px;border:1px solid var(--border)}}
    [data-theme="dark"] .hz-grp{{background:#1A1A1A;border-color:var(--dark-border)}}
    .hz-btn{{padding:5px 14px;border:none;border-radius:6px;font-family:'Inter',sans-serif;font-size:.68rem;font-weight:600;cursor:pointer;background:transparent;color:var(--muted);transition:all .2s}}
    .hz-btn:hover{{color:var(--text)}}
    .hz-btn.active{{background:var(--accent);color:#fff;box-shadow:0 2px 8px {accent}40}}
    .legend-bar{{display:flex;flex-wrap:wrap;gap:4px 10px;padding:2px 14px 10px;align-items:center}}
    .leg-item{{display:flex;align-items:center;gap:3px;font-size:.58rem;font-weight:600;color:var(--muted);white-space:nowrap}}
    .leg-dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0}}
    .leg-line{{width:16px;height:0;flex-shrink:0}}
    .leg-r2{{font-family:'JetBrains Mono',monospace;font-size:.52rem;opacity:.7}}
    .main-grid{{display:grid;grid-template-columns:3fr 2fr;gap:16px}}
    @media(max-width:900px){{.main-grid{{grid-template-columns:1fr}}}}
    @media(max-width:500px){{.sec-title{{font-size:1.2rem}}.hz-btn{{padding:4px 10px;font-size:.6rem}}}}
    .chart-card{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;height:560px}}
    [data-theme="dark"] .chart-card{{background:#141414;border-color:var(--dark-border)}}
    @media(max-width:900px){{.chart-card{{height:440px}}}}
    @media(max-width:500px){{.chart-card{{height:340px}}}}
    #chart{{width:100%;height:100%}}
    .panel{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}}
    [data-theme="dark"] .panel{{background:#141414;border-color:var(--dark-border)}}
    .panel-hd{{background:{panel_hd_bg};padding:10px 14px;display:flex;align-items:center;justify-content:space-between}}
    [data-theme="dark"] .panel-hd{{background:{panel_hd_bg_dark}}}
    .panel-hd-t{{font-size:.56rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.8)}}
    .panel-body{{padding:14px;flex:1;overflow-y:auto}}
    .pb{{margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid var(--border)}}
    [data-theme="dark"] .pb{{border-color:var(--dark-border)}}
    .pb:last-child{{border-bottom:none;margin-bottom:0;padding-bottom:0}}
    .pb-lbl{{font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px;color:var(--accent)}}
    .pb-desc{{font-size:.68rem;line-height:1.5;color:var(--muted)}}
    [data-theme="dark"] .pb-desc{{color:rgba(255,255,255,.45)}}
    .pb-desc strong{{color:var(--navy)}}
    [data-theme="dark"] .pb-desc strong{{color:#E2E8F0}}
    .ctx{{background:var(--cream);border-radius:6px;padding:8px 10px;border-left:3px solid var(--accent);margin-top:6px}}
    [data-theme="dark"] .ctx{{background:var(--navy-light)}}
    .ctx p{{font-size:.68rem;line-height:1.5;color:var(--muted)}}
    [data-theme="dark"] .ctx p{{color:#94A3B8}}
    .source{{display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding:0 2px}}
    .source-txt{{font-size:.6rem;color:var(--muted)}}
    .source-txt a{{color:var(--populi);font-weight:600;text-decoration:none}}
    .source-txt a:hover{{text-decoration:underline}}
    .loading{{display:flex;align-items:center;justify-content:center;height:300px;flex-direction:column;gap:12px;color:var(--muted)}}
    .spinner{{width:32px;height:32px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
  </style>
</head>
<body>
  <div class="wrap" id="app">
    <div class="loading" id="loader"><div class="spinner"></div><span style="font-size:.8rem">Cargando datos...</span></div>
  </div>
  <script>
    const DATA_URL = '../data/consolidated.json';
    const VAR_KEY = '{var_key}';
    const TITLE = '{title}';
    const SUBTITLE = '{subtitle}';
    const Y_LABEL = '{y_label}';
    const Y_FORMAT = {y_format};
    const Y_AXIS_FMT = {y_axis_fmt};
    const LOG_Y = {log_y};
    const Y_MIN = {y_min};
    const Y_MAX = {y_max};
    const ACCENT = '{accent}';
    const REG_ORDER = {reg_order};
    const REG_TYPE = '{reg_type}';

    const Q_COLORS = {{ 1:'#10B981', 2:'#3B82F6', 3:'#F59E0B', 4:'#EF4444' }};
    const Q_LABELS = {{ 1:'Cuartil 1 (mas libre)', 2:'Cuartil 2', 3:'Cuartil 3', 4:'Cuartil 4 (menos libre)' }};
    const R_COLORS = {{
      'East Asia & Pacific':'#3B82F6','Europe & Central Asia':'#8B5CF6',
      'Latin America & the Caribbean':'#F59E0B','Middle East & North Africa':'#EF4444',
      'North America':'#10B981','South Asia':'#EC4899','Sub-Saharan Africa':'#6366F1'
    }};
    const R_SHORT = {{
      'East Asia & Pacific':'Asia Pacifico','Europe & Central Asia':'Europa y Asia Central',
      'Latin America & the Caribbean':'Latinoamerica','Middle East & North Africa':'Medio Oriente',
      'North America':'Norteamerica','South Asia':'Asia del Sur','Sub-Saharan Africa':'Africa Subsahariana'
    }};

    let DATA, chart, colorMode = 'quartile', _r2 = 0;
    function dk(){{ return document.documentElement.getAttribute('data-theme') === 'dark'; }}

    function regress(pts, order) {{
      const n = pts.length;
      const xs = pts.map(p=>p[0]), ys = pts.map(p=>p[1]);
      const yMean = ys.reduce((s,v)=>s+v,0)/n;
      const ssTot = ys.reduce((s,v)=>s+(v-yMean)**2,0);
      let evalFn;
      if(order <= 1) {{
        let sx=0,sy=0,sxy=0,sx2=0;
        for(let i=0;i<n;i++){{ sx+=xs[i]; sy+=ys[i]; sxy+=xs[i]*ys[i]; sx2+=xs[i]*xs[i]; }}
        const b=(n*sxy-sx*sy)/(n*sx2-sx*sx), a=(sy-b*sx)/n;
        evalFn = x => a + b*x;
      }} else {{
        let s=[0,0,0,0,0], t=[0,0,0];
        for(let i=0;i<n;i++){{
          const x=xs[i],y=ys[i],x2=x*x;
          s[0]++;s[1]+=x;s[2]+=x2;s[3]+=x*x2;s[4]+=x2*x2;
          t[0]+=y;t[1]+=x*y;t[2]+=x2*y;
        }}
        const A=[[s[0],s[1],s[2]],[s[1],s[2],s[3]],[s[2],s[3],s[4]]];
        function det(m){{return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]);}}
        const D=det(A);
        const c0=det([[t[0],A[0][1],A[0][2]],[t[1],A[1][1],A[1][2]],[t[2],A[2][1],A[2][2]]])/D;
        const c1=det([[A[0][0],t[0],A[0][2]],[A[1][0],t[1],A[1][2]],[A[2][0],t[2],A[2][2]]])/D;
        const c2=det([[A[0][0],A[0][1],t[0]],[A[1][0],A[1][1],t[1]],[A[2][0],A[2][1],t[2]]])/D;
        evalFn = x => c0 + c1*x + c2*x*x;
      }}
      const ssRes = pts.reduce((s,p)=>s+(p[1]-evalFn(p[0]))**2,0);
      return {{ evalFn, r2: ssTot > 0 ? 1 - ssRes/ssTot : 0 }};
    }}

    function expRegress(pts) {{
      const n = pts.length;
      const xs = pts.map(p=>p[0]), ys = pts.map(p=>p[1]);
      const yMean = ys.reduce((s,v)=>s+v,0)/n;
      const ssTot = ys.reduce((s,v)=>s+(v-yMean)**2,0);
      const lys = ys.map(v => Math.log(Math.max(v, 0.1)));
      let sx=0,sl=0,sxl=0,sx2=0;
      for(let i=0;i<n;i++){{sx+=xs[i];sl+=lys[i];sxl+=xs[i]*lys[i];sx2+=xs[i]*xs[i];}}
      let b=(n*sxl-sx*sl)/(n*sx2-sx*sx), a=Math.exp((sl-b*sx)/n);
      for(let it=0;it<30;it++){{
        let g00=0,g01=0,g11=0,r0=0,r1=0;
        for(let i=0;i<n;i++){{
          const e=Math.exp(b*xs[i]), res=ys[i]-a*e;
          g00+=e*e; g01+=a*xs[i]*e*e; g11+=a*a*xs[i]*xs[i]*e*e;
          r0+=e*res; r1+=a*xs[i]*e*res;
        }}
        const det=g00*g11-g01*g01;
        if(Math.abs(det)<1e-30) break;
        a+=(g11*r0-g01*r1)/det;
        b+=(g00*r1-g01*r0)/det;
      }}
      const evalFn = x => Math.max(0, a*Math.exp(b*x));
      const ssRes = pts.reduce((s,p)=>s+(p[1]-evalFn(p[0]))**2,0);
      return {{ evalFn, r2: ssTot>0 ? 1-ssRes/ssTot : 0 }};
    }}

    async function init(){{
      const r = await fetch(DATA_URL);
      DATA = await r.json();
      document.getElementById('loader').style.display = 'none';
      render();
    }}

    function render(){{
      const app = document.getElementById('app');
      app.innerHTML = `
        <div class="sec-hd">
          <div class="sec-title"><span class="accent-bar"></span>${{TITLE}}</div>
          <div class="sec-sub">${{SUBTITLE}}</div>
        </div>
        <div class="controls-row">
          <span class="hz-lbl">Color:</span>
          <div class="hz-grp">
            <button class="hz-btn${{colorMode==='quartile'?' active':''}}" onclick="setColor('quartile')">Cuartil EFW</button>
            <button class="hz-btn${{colorMode==='region'?' active':''}}" onclick="setColor('region')">Region</button>
          </div>
        </div>
        <div class="legend-bar" id="legend"></div>
        <div class="main-grid">
          <div class="chart-card"><div id="chart"></div></div>
          <div class="panel">
            <div class="panel-hd"><span class="panel-hd-t">Lectura del indicador</span></div>
            <div class="panel-body">
              <div class="pb"><div class="pb-lbl">Relacion observada</div><div class="pb-desc">{relation}</div></div>
              <div class="pb"><div class="pb-lbl">Marco teorico</div><div class="pb-desc">{theory}</div></div>
              <div class="pb"><div class="pb-lbl">Bolivia</div><div class="pb-desc" id="bol-desc"></div></div>
              <div class="ctx"><p><strong>Fuente:</strong> {source_detail}. Tamano de burbuja = poblacion.</p></div>
            </div>
          </div>
        </div>
        <div class="source"><span class="source-txt">Fuente: <a href="https://www.fraserinstitute.org/economic-freedom" target="_blank">Fraser Institute</a> - Elaboracion: <a href="https://populi.org.bo" target="_blank">POPULI</a></span></div>
      `;
      buildChart();
      updateBol();
    }}

    function updateBol(){{
      const bol = DATA.find(d => d.iso === 'BOL');
      const el = document.getElementById('bol-desc');
      if(bol && el){{
        const yv = bol[VAR_KEY];
        const yStr = yv != null ? Y_FORMAT(yv) : 'N/D';
        el.innerHTML = `{bol_text}`.replace('{{efw}}', bol.efw_avg.toFixed(2)).replace('{{q}}', bol.efw_quartile).replace('{{yval}}', yStr);
      }}
    }}

    function buildChart(){{
      const el = document.getElementById('chart');
      chart = echarts.init(el, null, {{renderer:'canvas'}});
      const isDk = dk();
      const pts = DATA.filter(d => d[VAR_KEY] != null && d.efw_avg != null && d.population != null);
      const maxPop = Math.max(...pts.map(d => d.population));
      const minB = 4, maxB = 44;

      function getColor(d){{
        if(colorMode === 'quartile') return Q_COLORS[d.efw_quartile] || '#999';
        return R_COLORS[d.region] || '#999';
      }}

      const scatterData = pts.map(d => ({{
        value: [d.efw_avg, d[VAR_KEY], d.population, d.country, d.iso, d.efw_quartile, d.region],
        symbolSize: minB + (Math.sqrt(d.population)/Math.sqrt(maxPop)) * maxB,
        itemStyle: {{
          color: getColor(d),
          opacity: d.iso === 'BOL' ? 1 : 0.55,
          borderColor: d.iso === 'BOL' ? ACCENT : 'transparent',
          borderWidth: d.iso === 'BOL' ? 2.5 : 0
        }},
        label: d.iso === 'BOL' ? {{
          show:true, formatter:'BOL', position:'top', distance:4,
          fontSize:9, fontWeight:700, fontFamily:'JetBrains Mono',
          color:isDk?'#fff':'#1E293B',
          textBorderColor:isDk?'rgba(0,0,0,.6)':'rgba(255,255,255,.8)', textBorderWidth:2
        }} : {{show:false}}
      }}));

      let evalFn, r2Val;
      if(REG_TYPE === 'exp') {{
        ({{evalFn, r2: r2Val}} = expRegress(pts.map(d => [d.efw_avg, d[VAR_KEY]])));
      }} else {{
        const regPts = pts.map(d => [d.efw_avg, LOG_Y ? Math.log10(d[VAR_KEY]) : d[VAR_KEY]]);
        ({{evalFn, r2: r2Val}} = regress(regPts, REG_ORDER));
      }}
      _r2 = r2Val;

      const xArr = pts.map(d => d.efw_avg);
      const xMin = Math.min(...xArr), xMax = Math.max(...xArr);
      const trendData = Array.from({{length:80}}, (_, i) => {{
        const x = xMin + (xMax - xMin) * i / 79;
        const yFit = evalFn(x);
        return [x, LOG_Y ? Math.pow(10, yFit) : Math.max(0, yFit)];
      }});

      const gridColor = isDk ? '#1E293B' : '#F0EDE6';
      const axisColor = isDk ? '#334155' : '#D5CFC5';
      const labelColor = isDk ? '#64748B' : '#94A3B8';
      const nameColor = isDk ? '#94A3B8' : '#64748B';
      const mc = isDk ? '#94A3B8' : '#64748B';

      const qBands = [
        [{{xAxis:3.5}},{{xAxis:5.5, itemStyle:{{color:isDk?'rgba(239,68,68,.06)':'rgba(239,68,68,.04)'}}}}],
        [{{xAxis:5.5}},{{xAxis:6.5, itemStyle:{{color:isDk?'rgba(245,158,11,.06)':'rgba(245,158,11,.04)'}}}}],
        [{{xAxis:6.5}},{{xAxis:7.5, itemStyle:{{color:isDk?'rgba(59,130,246,.06)':'rgba(59,130,246,.04)'}}}}],
        [{{xAxis:7.5}},{{xAxis:9.2, itemStyle:{{color:isDk?'rgba(16,185,129,.06)':'rgba(16,185,129,.04)'}}}}]
      ];

      chart.setOption({{
        backgroundColor:'transparent',
        grid:{{ left:68, right:24, top:18, bottom:58, containLabel:false }},
        xAxis:{{
          type:'value', min:3.5, max:9.2,
          name:'Libertad Economica (EFW promedio 2000-2023)',
          nameLocation:'center', nameGap:36,
          nameTextStyle:{{ fontSize:11, fontFamily:'Inter', color:nameColor }},
          axisLabel:{{ fontSize:10, fontFamily:'JetBrains Mono', color:labelColor }},
          splitLine:{{ lineStyle:{{ color:gridColor, type:'dashed' }} }},
          axisLine:{{ lineStyle:{{ color:axisColor }} }}
        }},
        yAxis:{{
          type: LOG_Y ? 'log' : 'value',
          name:Y_LABEL, nameLocation:'center', nameGap:52,
          nameTextStyle:{{ fontSize:11, fontFamily:'Inter', color:nameColor }},
          min: Y_MIN, max: Y_MAX,
          axisLabel:{{ fontSize:10, fontFamily:'JetBrains Mono', color:labelColor, formatter: Y_AXIS_FMT }},
          splitLine:{{ lineStyle:{{ color:gridColor, type:'dashed' }} }},
          axisLine:{{ lineStyle:{{ color:axisColor }} }}
        }},
        tooltip:{{
          trigger:'item', confine:true,
          backgroundColor:isDk?'#1E293B':'#fff',
          borderColor:isDk?'#334155':'#E2E8F0',
          borderRadius:10, padding:[12,14],
          textStyle:{{ color:isDk?'#E2E8F0':'#1E293B', fontSize:12, fontFamily:'Inter' }},
          formatter: p => {{
            if(p.seriesIndex!==0) return '';
            const [efw,yv,pop,name,iso,q,reg] = p.value;
            const qc = Q_COLORS[q]||'#999';
            const ql = Q_LABELS[q]||'';
            return `<div style="min-width:190px">`
              +`<div style="font-weight:700;font-size:13px;margin-bottom:6px">${{name}} <span style="font-weight:400;font-size:11px;color:${{mc}}">${{iso}}</span></div>`
              +`<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">`
              +`<span style="background:${{qc}};color:#fff;padding:2px 10px;border-radius:5px;font-size:12px;font-weight:700;font-family:JetBrains Mono,monospace">${{efw.toFixed(2)}}</span>`
              +`<span style="font-size:10px;color:${{mc}}">${{ql}}</span></div>`
              +`<div style="display:flex;justify-content:space-between;margin-bottom:3px"><span style="font-size:11px;color:${{mc}}">${{Y_LABEL}}</span><span style="font-size:11px;font-weight:700">${{Y_FORMAT(yv)}}</span></div>`
              +`<div style="display:flex;justify-content:space-between;margin-bottom:3px"><span style="font-size:11px;color:${{mc}}">Poblacion</span><span style="font-size:11px;font-weight:700">${{pop>1e6?(pop/1e6).toFixed(1)+'M':(pop/1e3).toFixed(0)+'k'}}</span></div>`
              +`<div style="font-size:10px;color:${{mc}};margin-top:4px;border-top:1px solid ${{isDk?'#334155':'#E2E8F0'}};padding-top:4px">${{R_SHORT[reg]||reg}}</div></div>`;
          }}
        }},
        series:[
          {{ type:'scatter', data:scatterData, animationDuration:800, animationEasing:'cubicOut', z:2,
             markArea:{{ silent:true, data:qBands }} }},
          {{ type:'line', data:trendData, smooth:true, symbol:'none',
             lineStyle:{{ color:isDk?'rgba(255,255,255,.25)':'rgba(0,0,0,.18)', width:2.5, type:'dashed' }},
             tooltip:{{show:false}}, z:1, silent:true }}
        ]
      }});
      window.addEventListener('resize', () => chart.resize());
      renderLegend();
    }}

    function renderLegend(){{
      const el = document.getElementById('legend');
      let html = '';
      if(colorMode==='quartile'){{
        html = Object.entries(Q_LABELS).map(([q,l])=>`<span class="leg-item"><span class="leg-dot" style="background:${{Q_COLORS[q]}}"></span>${{l}}</span>`).join('');
      }} else {{
        html = Object.entries(R_SHORT).map(([r,l])=>`<span class="leg-item"><span class="leg-dot" style="background:${{R_COLORS[r]}}"></span>${{l}}</span>`).join('');
      }}
      const regLabel = REG_TYPE === 'exp' ? 'exponencial' : REG_ORDER === 2 ? 'cuadratica' : 'lineal';
      const dkC = dk() ? 'rgba(255,255,255,.3)' : 'rgba(0,0,0,.22)';
      html += `<span class="leg-item"><span class="leg-line" style="border-top:2.5px dashed ${{dkC}}"></span>Tendencia ${{regLabel}} <span class="leg-r2">(R²=${{_r2.toFixed(2)}})</span></span>`;
      el.innerHTML = html;
    }}

    function setColor(mode){{ colorMode=mode; render(); }}

    window.addEventListener('message', e => {{
      if(e.data && e.data.theme){{
        document.documentElement.setAttribute('data-theme', e.data.theme);
        if(chart){{ chart.dispose(); buildChart(); }}
      }}
    }});
    init();
  </script>
</body>
</html>'''

os.makedirs(EMBED_DIR, exist_ok=True)
for s in scatters:
    html = TEMPLATE.format(
        title=s['title'],
        subtitle=s['subtitle'],
        y_label=s['y_label'],
        y_format=s['y_format'],
        y_axis_fmt=s['y_axis_fmt'],
        log_y='true' if s['log_y'] else 'false',
        y_min=s['y_min'],
        y_max=s['y_max'],
        reg_order=s['reg_order'],
        reg_type=s.get('reg_type', 'poly'),
        accent=s['accent'],
        panel_hd_bg=s['panel_hd_bg'],
        panel_hd_bg_dark=s['panel_hd_bg_dark'],
        var_key=s['var'],
        relation=s['relation'],
        theory=s['theory'],
        source_detail=s['source_detail'],
        bol_text=s['bol_text'],
    )
    path = os.path.join(EMBED_DIR, s['file'])
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  OK {s['file']}")

print(f"\n{len(scatters)} embeds generados en {EMBED_DIR}/")
