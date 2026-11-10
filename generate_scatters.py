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

# El período del promedio, la edición del informe y el número de jurisdicciones salen del dato (actualizar_efw.py
# arma data/), no se escriben a mano: el informe sale con dos años de rezago (2026 → datos de 2024)
with open(os.path.join('data', 'efw_panel_map.json'), encoding='utf-8') as _f:
    _panel = json.load(_f)
ULT = max(int(a) for a in _panel)
N_JUR = sum(1 for d in _panel[str(ULT)].values() if d.get('s') is not None)
DESDE = 2000
PERIODO = f'{DESDE}–{ULT}'

scatters = [
    {
        'file': 'scatter_gdp.html',
        'var': 'gdp_pc_ppp',
        'title': 'Libertad Económica y Renta per Cápita',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs PIB per cápita PPA (USD constantes)',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW promedio: <strong>{efw}</strong>, cuartil {q}) tiene un PIB per cápita PPA de <strong>{yval}</strong>. Se ubica en el rango medio-bajo de libertad económica, y su ingreso está por debajo del promedio latinoamericano ({lat}).",
        # inglés (?lang=en): la pareja de cada texto de arriba
        'title_en': 'Per Capita Income and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. GDP per capita, PPP (constant USD)',
        'relation_en': 'Countries with <strong>greater sustained economic freedom</strong> show significantly higher levels of per capita income. The most free quartile (EFW of {corte} or higher) has an average GDP per capita <strong>{razon} times higher</strong> than the least free.',
        'theory_en': 'Economic freedom—property rights, sound money, free trade, efficient regulation and limited government—facilitates <strong>capital accumulation</strong>, <strong>innovation</strong> and the <strong>efficient allocation of resources</strong>, the fundamental drivers of long-term growth.',
        'bol_text_en': 'Bolivia (average EFW: <strong>{efw}</strong>, quartile {q}) has a GDP per capita (PPP) of <strong>{yval}</strong>. It sits in the lower-middle range of economic freedom, and its income is below the Latin American average ({lat}).',
    },
    {
        'file': 'scatter_poverty.html',
        # ⚠️ El nombre engaña: `poverty_365` es la línea de US$ 4,20 al día en PPA 2021 (la que el Banco Mundial publica
        # desde junio de 2025 en WDI SI.POV.LMIC y la PIP), NO la vieja de US$ 3,65 en PPA 2017. Comprobado el 10-nov-2026
        # contra la PIP: coincide exacto en Nigeria, Sudáfrica, Etiopía, Egipto, Filipinas, Turquía y Kenia.
        'var': 'poverty_365',
        'title': 'Libertad Económica y Pobreza',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Tasa de pobreza (menos de US$ 4,20 al día, PPA 2021)',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, World Bank Poverty & Inequality Platform',
        'bol_text': "En Bolivia (EFW: <strong>{efw}</strong>), el <strong>{yval}</strong> de la población vive con menos de US$ 4,20 al día (PPA 2021). A pesar del crecimiento del PIB, el nivel limitado de libertad económica frena una reducción más rápida de la pobreza.",
        'title_en': 'Poverty and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Poverty rate (less than US$4.20 a day, 2021 PPP)',
        'relation_en': 'There is an <strong>inverse relationship</strong> between economic freedom and poverty. The most free quartile has rates close to zero (<strong>{q1}</strong> on average), while the least free concentrates the highest (<strong>{q4}</strong>).',
        'theory_en': 'Trade openness, secure property rights and monetary stability generate <strong>formal jobs</strong>, <strong>productive investment</strong> and <strong>access to cheap imported goods</strong>, reducing absolute poverty through inclusive growth.',
        'bol_text_en': 'In Bolivia (EFW: <strong>{efw}</strong>), <strong>{yval}</strong> of the population lives on less than US$4.20 a day (2021 PPP). Despite GDP growth, the limited level of economic freedom holds back a faster reduction of poverty.',
    },
    {
        'file': 'scatter_life_exp.html',
        'var': 'life_exp',
        'title': 'Libertad Económica y Esperanza de Vida',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Esperanza de vida al nacer (años)',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una esperanza de vida de <strong>{yval}</strong> años, por debajo del promedio latinoamericano ({lat} años). Restricciones a la competencia en salud y bajo ingreso limitan el progreso sanitario.",
        'title_en': 'Life Expectancy and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Life expectancy at birth (years)',
        'relation_en': 'In the countries of the most free quartile, people live on average <strong>{dif} years longer</strong> than in those of the least free. The relationship is concentrated in the middle and upper range of the index: with an EFW of 6 or higher, each additional point is associated with <strong>{pend} more years</strong> of life; below 6, no clear relationship is observed.',
        'theory_en': 'Higher per capita income allows for <strong>better nutrition, sanitation and medical infrastructure</strong>. Freedom to trade facilitates access to medicines and supplies. Competition in health services improves quality and reduces costs.',
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) has a life expectancy of <strong>{yval}</strong> years, below the Latin American average ({lat} years). Restrictions on competition in health care and low income limit progress in health.',
    },
    {
        'file': 'scatter_infant_mort.html',
        'var': 'infant_mort',
        'title': 'Libertad Económica y Mortalidad Infantil',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Mortalidad infantil (por 1.000 nacidos vivos)',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, World Bank WDI 2023',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una mortalidad infantil de <strong>{yval} por mil</strong>. Aunque ha mejorado significativamente, sigue por encima del promedio latinoamericano ({lat}), reflejando limitaciones en acceso a salud y nutrición.",
        'title_en': 'Infant Mortality and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Infant mortality (per 1,000 live births)',
        'relation_en': 'Infant mortality <strong>falls dramatically</strong> as economic freedom increases. The most free quartile has infant mortality rates <strong>{razon} times lower</strong> than the least free quartile.',
        'theory_en': 'The mechanism works through <strong>higher family income</strong> (better maternal nutrition), <strong>investment in public health</strong> financed by growth, and <strong>access to medical technology</strong> facilitated by trade openness.',
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) has an infant mortality rate of <strong>{yval} per thousand</strong>. Although it has improved significantly, it remains above the Latin American average ({lat}), reflecting limitations in access to health care and nutrition.',
    },
    {
        'file': 'scatter_satisfaction.html',
        'var': 'life_satisfaction',
        'title': 'Libertad Económica y Satisfacción de Vida',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Evaluación de vida (Cantril Ladder 0–10)',
        'y_label': 'Satisfacción de vida (0-10)',
        'y_format': "v => v.toFixed(2)",
        'y_axis_fmt': "v => v.toFixed(1)",
        'log_y': False,
        'y_min': '3', 'y_max': '8',
        'reg_order': 2,
        'accent': '#DF5D25',
        'panel_hd_bg': '#9B2226', 'panel_hd_bg_dark': '#2A1410',
        'relation': 'Las personas en países económicamente libres reportan <strong>mayor satisfacción vital</strong>, lo que sugiere que la libertad económica contribuye al bienestar subjetivo.',
        'theory': 'La libertad económica aporta bienestar subjetivo a través de: <strong>sentido de autonomía</strong> sobre decisiones económicas propias, <strong>oportunidades de emprendimiento</strong>, <strong>menor corrupción</strong> y <strong>mayor confianza institucional</strong>.',
        'source_detail': 'Fraser Institute EFW @@EDICION@@, World Happiness Report 2026 (Cantril Ladder)',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene una satisfacción de vida de <strong>{yval}</strong>/10. Se ubica {vs_lat} promedio latinoamericano, una región que tradicionalmente reporta alta satisfacción relativa a su ingreso.",
        'title_en': 'Life Satisfaction and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Life evaluation (Cantril Ladder 0–10)',
        'relation_en': 'People in economically free countries report <strong>greater life satisfaction</strong>, which suggests that economic freedom contributes to subjective well-being.',
        'theory_en': "Economic freedom contributes to subjective well-being through: a <strong>sense of autonomy</strong> over one's own economic decisions, <strong>entrepreneurial opportunities</strong>, <strong>less corruption</strong> and <strong>greater institutional trust</strong>.",
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) has a life satisfaction of <strong>{yval}</strong>/10. It sits {vs_lat} Latin American average, a region that traditionally reports high satisfaction relative to its income.',
    },
    {
        'file': 'scatter_epi.html',
        'var': 'epi_score',
        'title': 'Libertad Económica y Desempeño Ambiental',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Environmental Performance Index 2024',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, Yale Environmental Performance Index 2024',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un EPI de <strong>{yval}</strong>/100. El puntaje refleja desafíos en protección de ecosistemas y calidad del aire, áreas donde la inseguridad jurídica y la falta de derechos de propiedad claros son factores clave.",
        'title_en': 'Environmental Performance and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Environmental Performance Index 2024',
        'relation_en': 'The freest countries have <strong>better environmental performance</strong>, contradicting the narrative that economic liberalization destroys the environment. The countries in the most free quartile score on average <strong>{dif} points higher</strong> on the EPI.',
        'theory_en': 'The <strong>Environmental Kuznets Curve</strong>: higher income makes it possible to invest in clean technology and effective environmental regulation. <strong>Clear property rights</strong> internalize externalities. <strong>Trade openness</strong> spreads clean technologies.',
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) has an EPI of <strong>{yval}</strong>/100. The score reflects challenges in ecosystem protection and air quality, areas where legal uncertainty and the lack of clear property rights are key factors.',
    },
    {
        'file': 'scatter_corruption.html',
        'var': 'cpi_score',
        'title': 'Libertad Económica y Ausencia de Corrupción',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Corruption Perceptions Index 2024',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, Transparency International CPI 2024',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un CPI de <strong>{yval}</strong>/100, en el tercio inferior mundial. La concentración de poder estatal en la economía y la debilidad del Estado de derecho facilitan la corrupción sistémica.",
        'title_en': 'Absence of Corruption and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Corruption Perceptions Index 2024',
        'relation_en': 'The correlation between economic freedom and transparency is among the <strong>strongest in the analysis</strong>. The most free quartile averages a CPI of <strong>{q1}</strong>, against <strong>{q4}</strong> in the least free.',
        'theory_en': 'Economic freedom reduces corruption by <strong>limiting the discretionary power</strong> of officials. Fewer regulations = fewer opportunities for bribery. The <strong>rule of law</strong> and <strong>property rights</strong> reinforce transparent institutions.',
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) has a CPI of <strong>{yval}</strong>/100, in the bottom third worldwide. The concentration of state power in the economy and the weakness of the rule of law facilitate systemic corruption.',
    },
    {
        'file': 'scatter_personal_freedom.html',
        'var': 'pf_score',
        'title': 'Libertad Económica y Libertad Personal',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Personal Freedom Score (HFI 2024)',
        'y_label': 'Libertad Personal (0-10)',
        'y_format': "v => v.toFixed(2)",
        'y_axis_fmt': "v => v.toFixed(0)",
        'log_y': False,
        'y_min': '2', 'y_max': '10',
        'reg_order': 1,
        'accent': '#005F73',
        'panel_hd_bg': '#0C4A6E', 'panel_hd_bg_dark': '#082F49',
        'relation': 'Las libertades económica y personal están <strong>positivamente correlacionadas</strong>. Los países que protegen la propiedad privada y el comercio libre tienden a proteger también la libertad de expresión, religión y asociación.',
        'theory': '<strong>Hayek y Friedman</strong> argumentaron que la libertad económica es <strong>condición necesaria</strong> (aunque no suficiente) para la libertad política. La independencia económica respecto del Estado reduce la capacidad del gobierno de reprimir la disidencia.',
        'source_detail': 'Fraser Institute EFW @@EDICION@@, Human Freedom Index (Cato/Fraser) 2024',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un índice de libertad personal de <strong>{yval}</strong>/10. La libertad de prensa y la independencia judicial son áreas de preocupación, correlacionadas con el bajo puntaje de libertad económica.",
        'title_en': 'Personal Freedom and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Personal Freedom Score (HFI 2024)',
        'relation_en': 'Economic and personal freedoms are <strong>positively correlated</strong>. Countries that protect private property and free trade tend to also protect freedom of expression, religion and association.',
        'theory_en': "<strong>Hayek and Friedman</strong> argued that economic freedom is a <strong>necessary condition</strong> (though not a sufficient one) for political freedom. Economic independence from the state reduces the government's ability to repress dissent.",
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) has a personal freedom index of <strong>{yval}</strong>/10. Press freedom and judicial independence are areas of concern, correlated with the low economic freedom score.',
    },
    {
        'file': 'scatter_hours.html',
        'var': 'hours_worked',
        'title': 'Libertad Económica y Horas Trabajadas',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Horas trabajadas anuales por trabajador',
        'y_label': 'Horas trabajadas/año',
        'y_format': "v => Math.round(v).toLocaleString('es-BO')",
        'y_axis_fmt': "v => Math.round(v).toLocaleString('es-BO')",
        'log_y': False,
        'y_min': '1300', 'y_max': '2700',
        'reg_order': 1,
        'accent': '#9B2226',
        'panel_hd_bg': '#701A75', 'panel_hd_bg_dark': '#4A044E',
        'relation': 'Los países más libres tienden a trabajar <strong>menos horas</strong> por año. Mayor productividad por hora permite alcanzar el mismo (o mayor) ingreso con menos tiempo de trabajo, liberando tiempo para ocio y familia.',
        'theory': 'La <strong>alta productividad</strong> de economías libres (capital abundante, tecnología, eficiencia institucional) permite la <strong>reducción gradual de jornada</strong> sin sacrificar ingreso — el «dividendo de la libertad» en forma de tiempo.',
        'source_detail': 'Fraser Institute EFW @@EDICION@@, Penn World Table 11.0',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un promedio de <strong>{yval}</strong> horas trabajadas al año por trabajador, por encima del promedio latinoamericano ({lat}). La baja productividad obliga a jornadas extensas para subsistir.",
        'title_en': 'Hours Worked and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Annual hours worked per worker',
        'relation_en': 'The freest countries tend to work <strong>fewer hours</strong> per year. Higher productivity per hour makes it possible to reach the same (or higher) income with less working time, freeing up time for leisure and family.',
        'theory_en': 'The <strong>high productivity</strong> of free economies (abundant capital, technology, institutional efficiency) allows the <strong>gradual reduction of working hours</strong> without sacrificing income — the "freedom dividend" in the form of time.',
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) averages <strong>{yval}</strong> hours worked per year per worker, above the Latin American average ({lat}). Low productivity forces long working hours in order to subsist.',
    },
    {
        'file': 'scatter_income_bottom10.html',
        'var': 'income_bottom10',
        'title': 'Libertad Económica e Ingreso del 10% más Pobre',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Participación del decil inferior en el ingreso',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, World Bank WDI',
        'bol_text': "En Bolivia (EFW: <strong>{efw}</strong>), el 10% más pobre recibe el <strong>{yval}</strong> del ingreso, en línea con el promedio de América Latina ({lat}), una de las regiones más desiguales del mundo. Con un ingreso per cápita bajo, ese decil sigue siendo muy pobre en términos absolutos.",
        'title_en': 'Income of the Poorest 10% and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Share of the bottom decile in income',
        'relation_en': 'The share of the poorest decile in national income is <strong>similar</strong> regardless of the level of economic freedom. However, since GDP per capita is much higher in free countries, the <strong>absolute income</strong> of the poorest is far higher.',
        'theory_en': 'The poor in free countries have <strong>higher absolute income</strong> (high GDP per capita × stable share). Social mobility and access to competitive markets allow low incomes to grow with the economy.',
        'bol_text_en': 'In Bolivia (EFW: <strong>{efw}</strong>), the poorest 10% receives <strong>{yval}</strong> of income, in line with the average for Latin America ({lat}), one of the most unequal regions in the world. With a low per capita income, that decile remains very poor in absolute terms.',
    },
    {
        'file': 'scatter_democracy.html',
        'var': 'democracy',
        'title': 'Libertad Económica y Democracia',
        'subtitle': 'Promedio EFW @@PERIODO@@ vs Índice de Democracia Electoral (V-Dem v16)',
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
        'source_detail': 'Fraser Institute EFW @@EDICION@@, V-Dem v16 (2025)',
        'bol_text': "Bolivia (EFW: <strong>{efw}</strong>) tiene un índice de democracia electoral de <strong>{yval}</strong>. A pesar de elecciones regulares, la concentración de poder económico en el Estado debilita los contrapesos democráticos.",
        'title_en': 'Democracy and Economic Freedom',
        'subtitle_en': 'EFW average @@PERIODO@@ vs. Electoral Democracy Index (V-Dem v16)',
        'relation_en': 'The relationship is <strong>positive but with notable exceptions</strong>: countries such as Singapore (high economic freedom, limited democracy) and others with formal democracies but low economic freedom. The correlation suggests complementarity, not direct causality.',
        'theory_en': 'Economic freedom creates an <strong>independent middle class</strong> that demands political participation. The <strong>decentralization of economic power</strong> hinders autocratic consolidation. However, causality may run in both directions.',
        'bol_text_en': 'Bolivia (EFW: <strong>{efw}</strong>) has an electoral democracy index of <strong>{yval}</strong>. Despite regular elections, the concentration of economic power in the state weakens democratic checks and balances.',
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
# Nombre corto para el eje (el largo queda en la bajada), piso/techo naturales del indicador y, al final,
# el mismo nombre corto en inglés (?lang=en)
EJE = {
    'gdp_pc_ppp': ('PIB per cápita PPA (USD)', '500', '200000', 'GDP per capita, PPP (USD)'),      # escala log: sin la década vacía de $1.000.000
    'poverty_365': ('Pobreza (% de la población)', '0', 'null', 'Poverty (% of population)'),
    'life_exp': ('Esperanza de vida (años)', '50', '90', 'Life expectancy (years)'),
    'infant_mort': ('Mortalidad infantil (por 1.000)', '0', 'null', 'Infant mortality (per 1,000)'),
    'life_satisfaction': ('Satisfacción de vida (0–10)', 'null', 'null', 'Life satisfaction (0–10)'),
    'epi_score': ('Desempeño ambiental (EPI, 0–100)', 'null', 'null', 'Environmental performance (EPI, 0–100)'),
    'cpi_score': ('Ausencia de corrupción (CPI, 0–100)', 'null', 'null', 'Absence of corruption (CPI, 0–100)'),   # en el CPI, más puntaje es menos corrupción
    'pf_score': ('Libertad personal (0–10)', 'null', 'null', 'Personal freedom (0–10)'),
    'hours_worked': ('Horas trabajadas al año', 'null', 'null', 'Hours worked per year'),
    'income_bottom10': ('Ingreso del 10% más pobre (% del total)', '0', 'null', 'Income of the poorest 10% (% of total)'),
    'democracy': ('Democracia electoral (0–1)', '0', '1', 'Electoral democracy (0–1)'),
}
# En el teléfono, el eje que se come el ancho pasa a una unidad más corta («$100.000» → «100»): formato, nombre
# corto en castellano y nombre corto en inglés
EJE_MOVIL = {
    'gdp_pc_ppp': ("function (v) { return PM.tick(v / 1000); }", 'PIB per cápita PPA (miles de USD)', 'GDP per capita, PPP (thousands of USD)'),
}
# El acento va de fondo del botón activo: tiene que sostener texto blanco (≥ 3:1)
ACENTO = {'#EE9B00': '#A86E00', '#94D2BD': '#0A9396', '#E57D22': '#DF5D25'}

# Dos idiomas (molde v2.4, populi-marca/monitor/GUIA_INGLES.md): con ?lang=en el gráfico sale en inglés; sin el
# parámetro, en castellano como siempre. En la plantilla, el marcado lleva su pareja en `data-en` y el código en
# T('castellano', 'inglés'); lo propio de cada indicador viene de los campos `*_en` de la lista y de EJE/EJE_MOVIL.
# Países y regiones: en inglés se muestran los nombres ORIGINALES de la fuente (Fraser): `x.country` y la clave de
# REGIONES; el diccionario paises_es.json y los nombres de región en castellano sólo se usan en castellano.
TEMPLATE = r"""<!DOCTYPE html>
<html lang="es" data-theme="light" style="--acento:@@ACENTO@@">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title data-en="@@TITLE_EN@@ · Populi">@@TITLE@@ · Populi</title>
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
      <div class="sec-title" data-en='<span class="accent-bar"></span>@@TITLE_EN@@'><span class="accent-bar"></span>@@TITLE@@</div>
      <div class="sec-sub" data-en="@@SUBTITLE_EN@@">@@SUBTITLE@@</div>
    </div>

    <div class="hz-bar">
      <div class="hz-item"><span class="hz-lbl" data-en="Color">Color</span><div class="hz-grp" id="b-color"></div></div>
    </div>

    <div class="kpi-grid" id="kpis"></div>

    <div class="main-grid">
      <div class="chart-card">
        <div class="chart-ctrl">
          <div class="ley" id="leyenda"></div>
          <div class="tog-grp" id="regiones" style="display:none"></div>
        </div>
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span data-en="Loading data…">Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t" data-en="Reading the indicator">Lectura del indicador</span><span class="panel-hd-d" data-en="EFW @@PERIODO@@">EFW @@PERIODO@@</span></div>
        <div class="panel-body" id="panel"></div>
      </div>
    </div>

    <div class="edu-grid" id="preguntas"></div>
    <div class="source"><span class="source-txt" id="fuente"></span></div>
  </div>

  <script>
  (function () {
    var C = PM.C, T = PM.t;   // T('castellano', 'inglés'): con ?lang=en el gráfico sale en inglés
    var VAR = '@@VAR@@', Y_CORTO = T('@@Y_CORTO@@', '@@Y_CORTO_EN@@'), LOG = @@LOG@@, Y_MIN = @@Y_MIN@@, Y_MAX = @@Y_MAX@@;
    var REG_TIPO = '@@REG_TYPE@@', REG_ORDEN = @@REG_ORDER@@, ACENTO = '@@ACENTO@@';
    var FMT = @@FMT@@, FMT_EJE = @@FMT_EJE@@, FMT_EJE_M = @@FMT_EJE_M@@, Y_CORTO_M = T('@@Y_CORTO_M@@', '@@Y_CORTO_M_EN@@');
    var RELACION = T(@@RELACION@@, @@RELACION_EN@@), TEORIA = T(@@TEORIA@@, @@TEORIA_EN@@), BOL_TXT = T(@@BOL_TXT@@, @@BOL_TXT_EN@@), FUENTE_DET = @@FUENTE_DET@@;
    // Cuartiles del índice: escala ORDINAL de la marca (la misma del mapa), del más libre (turquesa)
    // al menos libre (rojo). Por región: modo Foco (la región elegida en rojo, el resto en gris tenue):
    // siete colores no se distinguen entre sí cuando las burbujas se mezclan.
    var QC = { 1: C.turquesa, 2: C.menta, 3: C.oro, 4: C.rojo };
    var QN = { 1: T('Cuartil 1 · más libre', 'Quartile 1 · most free'), 2: T('Cuartil 2', 'Quartile 2'), 3: T('Cuartil 3', 'Quartile 3'), 4: T('Cuartil 4 · menos libre', 'Quartile 4 · least free') };
    // pie del tooltip: el cuartil con la frase entera en cada idioma
    var QPIE = { 1: T('Cuartil 1 de libertad económica · el más libre', 'Economic freedom: Quartile 1 · most free'), 2: T('Cuartil 2 de libertad económica', 'Economic freedom: Quartile 2'),
      3: T('Cuartil 3 de libertad económica', 'Economic freedom: Quartile 3'), 4: T('Cuartil 4 de libertad económica · el menos libre', 'Economic freedom: Quartile 4 · least free') };
    var REGIONES = [['Latin America & the Caribbean', T('América Latina y el Caribe', 'Latin America & the Caribbean')], ['North America', T('Norteamérica', 'North America')],
      ['Europe & Central Asia', T('Europa y Asia Central', 'Europe & Central Asia')], ['East Asia & Pacific', T('Asia Oriental y Pacífico', 'East Asia & Pacific')],
      ['South Asia', T('Asia del Sur', 'South Asia')], ['Middle East & North Africa', T('Medio Oriente y Norte de África', 'Middle East & North Africa')],
      ['Sub-Saharan Africa', T('África Subsahariana', 'Sub-Saharan Africa')]];
    var REGION = {};
    REGIONES.forEach(function (r) { REGION[r[0]] = r[1]; });
    var estado = { color: 'cuartil', region: 'Latin America & the Caribbean' };
    var PTS, BOL, AJ, CORTES, CORTE_Q1, NOMBRE = {}, grafico;
    var nombre = function (x) { return T(NOMBRE[x.iso] || x.country, x.country); };

    var media = function (a) { return a.length ? a.reduce(function (s, v) { return s + v; }, 0) / a.length : null; };
    var valores = function (f) { return PTS.filter(f).map(function (x) { return x[VAR]; }); };
    var tenue = function () { return PM.dk() ? '#3A4549' : '#C9CDCE'; };
    var tipoAjuste = function (masc) { return REG_TIPO === 'exp' ? T('exponencial', 'Exponential') : REG_ORDEN === 2 ? (masc ? T('cuadrático', 'Quadratic') : T('cuadrática', 'Quadratic')) : T('lineal', 'Linear'); };
    function poblacion(n) {
      if (n >= 1e9) return T(PM.num(n / 1e9, 2) + ' mil millones', PM.num(n / 1e9, 2) + ' billion');
      if (n >= 1e6) return T(PM.num(n / 1e6, 1) + ' millones', PM.num(n / 1e6, 1) + ' million');
      return T(PM.num(n / 1e3, 0) + ' mil', PM.num(n / 1e3, 0) + ' thousand');
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
      PM.botonera(document.getElementById('b-color'), [['cuartil', T('Cuartil EFW', 'EFW quartile')], ['region', T('Región', 'Region')]], estado.color, function (v) {
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
      PM.imagen = { proporcion: 1 };   // imagen de descarga cuadrada: la nube necesita alto
      PM.leyendaImagen = function () {
        var it = estado.color === 'cuartil'
          ? [1, 2, 3, 4].map(function (q) { return { name: QN[q], color: PM.col(QC[q]), forma: 'punto' }; })
          : [{ name: REGION[estado.region], color: C.rojo, forma: 'punto' }, { name: T('Resto del mundo', 'Rest of the world'), color: tenue(), forma: 'punto' }];
        it.push({ name: T('Tendencia ' + tipoAjuste() + ' · R² ' + PM.num(AJ.r2, 2), tipoAjuste() + ' trend · R² ' + PM.num(AJ.r2, 2)), color: PM.dk() ? '#C9CDCE' : '#5C6B70', forma: 'punteada' });
        return it;
      };
      PM.tablaDatos = function () {
        return {
          cols: [T('País', 'Country'), 'ISO3', T('Región', 'Region'), T('Cuartil EFW', 'EFW quartile'), T('EFW promedio @@PERIODO@@', 'EFW average @@PERIODO@@'), Y_CORTO, T('Población', 'Population')],
          filas: PTS.slice().sort(function (a, b) { return b.efw_avg - a.efw_avg; }).map(function (x) {
            return [nombre(x), x.iso, REGION[x.region] || x.region, x.efw_quartile, x.efw_avg, x[VAR], x.population];
          })
        };
      };
      document.getElementById('fuente').innerHTML = T('Fuente: ' + FUENTE_DET.replace('Fraser Institute', '<a href="https://www.fraserinstitute.org/economic-freedom" target="_blank" rel="noopener">Fraser Institute</a>') + ' · Elaboración: Centro de Estudios POPULI',
        'Source: ' + FUENTE_DET.replace('Fraser Institute', '<a href="https://www.fraserinstitute.org/economic-freedom" target="_blank" rel="noopener">Fraser Institute</a>') + ' · Analysis: Centro de Estudios POPULI');
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
        : [[C.rojo, REGION[estado.region]], [tenue(), T('Resto del mundo', 'Rest of the world')]];
      document.getElementById('leyenda').innerHTML = items.map(function (it) {
        return '<span class="ley-i"><span class="ley-d" style="background:' + it[0] + '"></span>' + it[1] + '</span>';
      }).join('') + T('<span class="ley-i"><span class="ley-l"></span>Tendencia ' + tipoAjuste() + ' · <span class="ley-r2">R² ' + PM.num(AJ.r2, 2) + '</span></span>',
        '<span class="ley-i"><span class="ley-l"></span>' + tipoAjuste() + ' trend · <span class="ley-r2">R² ' + PM.num(AJ.r2, 2) + '</span></span>');
    }

    function cifras() {
      var q1 = valores(function (x) { return x.efw_quartile === 1; }), q4 = valores(function (x) { return x.efw_quartile === 4; });
      document.getElementById('kpis').innerHTML =
        PM.kpi({ color: C.turquesa, rotulo: T('Cuartil más libre', 'Most free quartile'), valor: FMT(media(q1)), delta: T('promedio · ' + q1.length + ' países', 'average · ' + q1.length + ' countries'), tono: 'neutro' }) +
        PM.kpi({ color: C.rojo, rotulo: T('Cuartil menos libre', 'Least free quartile'), valor: FMT(media(q4)), delta: T('promedio · ' + q4.length + ' países', 'average · ' + q4.length + ' countries'), tono: 'neutro' }) +
        PM.kpi({ color: C.tinta, rotulo: 'Bolivia', valor: BOL ? FMT(BOL[VAR]) : '—', delta: BOL ? T('EFW ' + PM.num(BOL.efw_avg, 2) + ' · cuartil ' + BOL.efw_quartile, 'EFW ' + PM.num(BOL.efw_avg, 2) + ' · quartile ' + BOL.efw_quartile) : T('sin dato', 'no data'), tono: 'neutro' }) +
        PM.kpi({ color: C.pizarra, rotulo: T('Tendencia', 'Trend'), valor: 'R² ' + PM.num(AJ.r2, 2), delta: T('ajuste ' + tipoAjuste(true), tipoAjuste(true).toLowerCase() + ' fit'), tono: 'neutro' });
    }

    // Cifras del texto que dependen del dato: {q1} y {q4} (promedio de los cuartiles extremos), {razon}
    // (cuántas veces), {dif} (diferencia), {lat} (promedio de América Latina y el Caribe), {corte} (EFW
    // mínimo del cuartil más libre), {pend} (pendiente con EFW de 6 o más), {efw}, {q}, {yval} (Bolivia),
    // {vs_lat} (Bolivia «por debajo del», «por encima del» o «en línea con el» promedio de América Latina)
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
      // la comparación con la región la decide el dato, al redondeo con que se muestra
      if (BOL && t.indexOf('{vs_lat}') >= 0) t = t.replace('{vs_lat}', FMT(BOL[VAR]) === FMT(lat) ? T('en línea con el', 'in line with the') : BOL[VAR] < lat ? T('por debajo del', 'below the') : T('por encima del', 'above the'));
      return t;
    }
    function panel() {
      document.getElementById('panel').innerHTML =
        PM.pb(ACENTO, T('Relación observada', 'Observed relationship'), null, conDatos(RELACION)) +
        PM.pb(ACENTO, T('Marco teórico', 'Theoretical framework'), null, TEORIA) +
        PM.pb(ACENTO, 'Bolivia', null, BOL ? conDatos(BOL_TXT) : T('Sin dato para Bolivia en este indicador.', 'No data for Bolivia on this indicator.')) +
        PM.ctx(T('<strong>Fuente:</strong> ' + FUENTE_DET + '. El tamaño de cada burbuja es la población del país.', '<strong>Source:</strong> ' + FUENTE_DET + '. The size of each bubble is the population of the country.'));
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
          name: chico ? T('Libertad económica (EFW, 0 a 10)', 'Economic freedom (EFW, 0 to 10)') : T('Libertad económica · índice EFW, promedio @@PERIODO@@ (0 a 10)', 'Economic freedom · EFW index, @@PERIODO@@ average (0 to 10)'),
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
            PM.ttFila(null, T('Libertad económica (EFW)', 'Economic freedom (EFW)'), PM.num(v[0], 2)) +
            PM.ttFila(null, Y_CORTO, FMT(v[1])) +
            PM.ttFila(null, T('Población', 'Population'), poblacion(v[2])) +
            PM.ttPie('<span style="display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;background:' +
              PM.col(QC[v[5]]) + '"></span>' + QPIE[v[5]]);
        }, { trigger: 'item' }),
        series: [
          { type: 'scatter', data: datos, markArea: { silent: true, data: franjas }, emphasis: { focus: 'self', itemStyle: { opacity: 1 } } },
          { type: 'line', data: tendencia, symbol: 'none', smooth: true, silent: true, z: 4, tooltip: { show: false },
            lineStyle: { color: dk ? 'rgba(226,232,240,.55)' : 'rgba(0,18,25,.45)', width: 1.5, type: [6, 4] } }
        ]
      };
    }

    var PREGUNTAS = [
      [T('¿Qué mide el índice de libertad económica?', 'What does the economic freedom index measure?'), T('El índice <strong>Economic Freedom of the World</strong> (EFW) del Fraser Institute califica de 0 a 10 a @@N_JUR@@ jurisdicciones en cinco áreas: tamaño del gobierno, sistema legal y derechos de propiedad, moneda sana, libertad para comerciar internacionalmente y regulación. Este gráfico usa el <strong>promedio @@PERIODO@@</strong> de cada país, que resume @@N_ANIOS@@ años y no uno suelto.',
        'The <strong>Economic Freedom of the World</strong> (EFW) index of the Fraser Institute rates @@N_JUR@@ jurisdictions from 0 to 10 in five areas: Size of Government, Legal System and Property Rights, Sound Money, Freedom to Trade Internationally, and Regulation. This chart uses the <strong>@@PERIODO@@ average</strong> of each country, which summarizes @@N_ANIOS@@ years rather than a single one.')],
      [T('¿Cómo se lee este gráfico?', 'How do you read this chart?'), T('Cada burbuja es un país: cuanto más a la derecha, más libertad económica; la altura es el indicador y el tamaño, la población. Las franjas del fondo marcan los <strong>cuartiles</strong> del índice (cada uno reúne a una cuarta parte de los países) y la línea punteada es la <strong>tendencia ajustada</strong>: su R² dice qué parte de las diferencias entre países acompaña a la libertad económica.',
        'Each bubble is a country: the farther to the right, the more economic freedom; the height is the indicator and the size is the population. The bands in the background mark the <strong>quartiles</strong> of the index (each one groups a quarter of the countries) and the dashed line is the <strong>fitted trend</strong>: its R² tells what share of the differences between countries goes along with economic freedom.')],
      [T('¿Correlación es causalidad?', 'Is correlation causation?'), T('No necesariamente. El gráfico muestra una <strong>asociación entre países</strong>. Otros factores —instituciones, geografía, historia, capital humano— también influyen, y la relación puede operar en ambos sentidos. Se lee como evidencia de una regularidad, no como prueba de una causa única.',
        'Not necessarily. The chart shows an <strong>association across countries</strong>. Other factors—institutions, geography, history, human capital—also play a role, and the relationship may run in both directions. It should be read as evidence of a regularity, not as proof of a single cause.')]
    ];
  })();
  </script>
</body>
</html>
"""

for s in scatters:
    fmt, fmt_eje = FORMATO[s['var']]
    corto, ymin, ymax, corto_en = EJE[s['var']]
    movil = EJE_MOVIL.get(s['var'], (fmt_eje, corto, corto_en))
    # estas parejas van dentro de atributos data-en y de cadenas JS entre comillas simples: sin comillas adentro
    assert not set('\'"') & set(s['title_en'] + s['subtitle_en'] + corto_en + movil[2]), s['file']
    reemplazos = {
        '@@TITLE@@': s['title'], '@@SUBTITLE@@': s['subtitle'], '@@VAR@@': s['var'],
        '@@TITLE_EN@@': s['title_en'], '@@SUBTITLE_EN@@': s['subtitle_en'],
        '@@ACENTO@@': ACENTO.get(s['accent'], s['accent']), '@@Y_CORTO@@': corto, '@@Y_CORTO_EN@@': corto_en,
        '@@LOG@@': 'true' if s['log_y'] else 'false', '@@Y_MIN@@': ymin, '@@Y_MAX@@': ymax,
        '@@REG_TYPE@@': s.get('reg_type', 'poly'), '@@REG_ORDER@@': str(s['reg_order']),
        '@@FMT@@': fmt, '@@FMT_EJE@@': fmt_eje,
        '@@FMT_EJE_M@@': movil[0], '@@Y_CORTO_M@@': movil[1], '@@Y_CORTO_M_EN@@': movil[2],
        '@@RELACION@@': json.dumps(s['relation'], ensure_ascii=False),
        '@@TEORIA@@': json.dumps(s['theory'], ensure_ascii=False),
        '@@BOL_TXT@@': json.dumps(s['bol_text'], ensure_ascii=False),
        '@@RELACION_EN@@': json.dumps(s['relation_en'], ensure_ascii=False),
        '@@TEORIA_EN@@': json.dumps(s['theory_en'], ensure_ascii=False),
        '@@BOL_TXT_EN@@': json.dumps(s['bol_text_en'], ensure_ascii=False),
        '@@FUENTE_DET@@': json.dumps(s['source_detail'], ensure_ascii=False),
        # al final: también se reemplazan dentro de los textos ya insertados (bajada, fuente)
        '@@PERIODO@@': PERIODO, '@@EDICION@@': str(ULT + 2), '@@N_JUR@@': str(N_JUR), '@@N_ANIOS@@': str(ULT - DESDE + 1),
    }
    html = TEMPLATE
    for k, v in reemplazos.items():
        html = html.replace(k, v)
    assert '@@' not in html, s['file']
    with open(os.path.join(EMBED_DIR, s['file']), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  OK {s['file']}")

print(f"\n{len(scatters)} embeds generados en {EMBED_DIR}/")
