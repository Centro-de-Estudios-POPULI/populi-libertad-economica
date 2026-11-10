"""
generate_charts.py — los cinco gráficos complementarios del Monitor de Libertad Económica, sobre el
molde de monitores (embed/comun/, fuente única en populi-marca/monitor):

  1. areas_regiones.html     — puntos: las cinco áreas del índice por región, último año
  2. evolucion_mundial.html  — líneas: promedio mundial del índice y de sus áreas, 1970 al último año
  3. bolivia_efw.html        — líneas: Bolivia frente al mundo y a América Latina, y sus áreas
  4. comparativa_paises.html — buscador: índice EFW 1970 al último año de hasta seis países, con su cuartil
  5. comparativa_pib.html    — buscador: PIB per cápita (Maddison) 1820–2022 de hasta seis países

Los datos del índice salen de actualizar_efw.py (el archivo maestro del Fraser → data/).

Cada página lleva incrustado lo que dibuja, calculado acá desde data/. Ninguna cifra de los textos
se escribe a mano, y las frases del panel se verifican contra el dato al generar: si el dato deja
de sostener una, el generador se detiene y dice cuál (sin dato no se publica).

Dos idiomas (molde v2.4, populi-marca/monitor/GUIA_INGLES.md): cada texto visible lleva su pareja en inglés, escrita
acá con T('castellano', 'inglés') (ver la clase T) o con data-en en las plantillas; las cifras del inglés salen de
num_en(). Sin ?lang=en la página es la de siempre. Tienen pareja las cinco páginas y las piezas comunes (título,
bajada y fuente de pagina(), `var T = PM.t`, FRASER, MADDISON, AREAS, efw_que). En 4 y 5 los países y las regiones
salen en inglés con el nombre original de la fuente: las tablas EN y EN_REGION, que js_comp escribe desde data/.

    python generate_charts.py
"""
import json
import math
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
OUT = RAIZ / 'embed'


def cargar(nombre):
    return json.loads((RAIZ / 'data' / nombre).read_text(encoding='utf-8'))


class T(str):
    """Texto con su pareja en inglés (molde v2.4: con ?lang=en el gráfico sale en inglés; sin él, el castellano de siempre).

    Para el generador ES el texto en castellano (entra en una f-string, se compara, se ordena, se verifica) y lleva al
    lado el inglés en `.en`. Al salir a la página: dentro de los datos (js) es la llamada T("castellano","inglés"), que
    la página resuelve con `var T = PM.t`; en el marcado (pagina) es el atributo data-en. Un texto que no es T sale
    como antes, sin pareja. Las cifras del inglés se escriben con num_en(), nunca a mano."""

    def __new__(cls, es, en):
        o = super().__new__(cls, es)
        o.en = en
        return o


panel = cargar('efw_panel_map.json')          # {año: {iso: {s, a1..a5}}}
meta = cargar('efw_country_meta.json')        # {iso: {name, region}} de las 165 jurisdicciones
gdp = cargar('gdp_pc_maddison.json')          # {iso: {año: PIB per cápita}}
pob = cargar('poblacion_maddison.json')       # {iso: {año: población en miles}}, 2000–2022 (maddison_poblacion.py)
cons = cargar('consolidated.json')            # población actual (WDI): peso de las jurisdicciones sin dato en Maddison
COMP_BOL = cargar('efw_componentes_bol.json')['anios']   # {año: {componente: valor}} de Bolivia, hoja oficial
_es = cargar('paises_es.json')
NOMBRE = _es['iso']                           # ISO3 → nombre en español (incluye CSK/SUN/YUG)

# ── Índice y áreas ─────────────────────────────────────────────────────────────────────────────
# Nombres oficiales de las áreas; «corto» solo donde el largo no entra (pastillas en el teléfono, cifras).
# En inglés, el nombre oficial del informe EFW (el corto es una abreviación propia, como en castellano).
AREAS = [
    {'k': 'a1', 'nombre': T('Tamaño del gobierno', 'Size of Government'), 'corto': T('Tamaño del gobierno', 'Size of Government')},
    {'k': 'a2', 'nombre': T('Sistema legal y derechos de propiedad', 'Legal System and Property Rights'),
     'corto': T('Sistema legal', 'Legal System')},
    {'k': 'a3', 'nombre': T('Moneda sana', 'Sound Money'), 'corto': T('Moneda sana', 'Sound Money')},
    {'k': 'a4', 'nombre': T('Libertad para comerciar internacionalmente', 'Freedom to Trade Internationally'),
     'corto': T('Comercio internacional', 'International Trade')},
    {'k': 'a5', 'nombre': T('Regulación', 'Regulation'), 'corto': T('Regulación', 'Regulation')},
]
# Rampa categórica oficial de cinco (populi-marca/paleta.py → RAMPA_POR_N[5]), del rojo a la tinta en el
# orden de las áreas. La misma en los tres gráficos que muestran áreas; en oscuro la tinta se invierte sola.
RAMPA5 = ['#C71E1D', '#EE9B00', '#0A9396', '#005F73', '#001219']
for _a, _c in zip(AREAS, RAMPA5):
    _a['color'] = _c
PIZARRA = {'claro': '#5C6B70', 'oscuro': '#8A9699'}   # series de referencia: en oscuro, el gris que se lee
# Protagonista de la evolución mundial: granate (el acento) en claro; en oscuro el granate no llega a 3:1 sobre la
# tarjeta y sube al rojo de la misma familia (validate_palette: con el gris, ΔE 25 normal y 16 en daltonismo)
GRANATE = {'claro': '#9B2226', 'oscuro': '#C71E1D'}

REGION = {   # regiones del Banco Mundial, con los mismos nombres que las dispersiones
    'North America': 'Norteamérica', 'Europe & Central Asia': 'Europa y Asia Central',
    'East Asia & Pacific': 'Asia Oriental y Pacífico', 'Latin America & the Caribbean': 'América Latina y el Caribe',
    'South Asia': 'Asia del Sur', 'Middle East & North Africa': 'Medio Oriente y Norte de África',
    'Sub-Saharan Africa': 'África Subsahariana',
}
LAC = 'Latin America & the Caribbean'
# Países del Maddison que no están en el índice: región para el buscador (los tres históricos son el
# agregado de sus sucesores, que Maddison sigue hasta 2022)
REGION_EXTRA = {
    'AFG': 'Asia del Sur', 'CUB': 'América Latina y el Caribe', 'DMA': 'América Latina y el Caribe',
    'GNQ': 'África Subsahariana', 'LCA': 'América Latina y el Caribe', 'PRI': 'América Latina y el Caribe',
    'PRK': 'Asia Oriental y Pacífico', 'PSE': 'Medio Oriente y Norte de África', 'STP': 'África Subsahariana',
    'TKM': 'Europa y Asia Central', 'UZB': 'Europa y Asia Central',
    'CSK': 'Europa · agregado histórico', 'SUN': 'Europa y Asia · agregado histórico', 'YUG': 'Europa · agregado histórico',
}
# Antigua órbita socialista (declarado, no inferido): para contar quiénes entraron al índice después de 1970
EX_SOCIALISTAS = {'ALB', 'ARM', 'AZE', 'BGR', 'BIH', 'BLR', 'CZE', 'EST', 'GEO', 'HRV', 'HUN', 'KAZ', 'KGZ', 'LTU', 'LVA',
                  'MDA', 'MKD', 'MNE', 'MNG', 'POL', 'ROU', 'RUS', 'SRB', 'SVK', 'SVN', 'TJK', 'UKR', 'UZB', 'TKM'}

ANIOS = [y for y in sorted(panel, key=int) if int(y) >= 1970]   # quinquenal hasta 1995, anual desde 2000
ULTIMO = ANIOS[-1]
ANUALES = [y for y in ANIOS if int(y) >= 2000]                   # minilíneas de las cifras: tramo anual
INFORME = int(ULTIMO) + 2      # el informe sale con dos años de rezago (actualizar_efw.py lo comprueba con el archivo)

FRASER = T('Fuente: <a href="https://www.fraserinstitute.org/economic-freedom" target="_blank" rel="noopener">Fraser Institute</a>, '
           f'Economic Freedom of the World: {INFORME} Annual Report · Elaboración: '
           '<a href="https://populi.org.bo" target="_blank" rel="noopener">Centro de Estudios POPULI</a>',
           'Source: <a href="https://www.fraserinstitute.org/economic-freedom" target="_blank" rel="noopener">Fraser Institute</a>, '
           f'Economic Freedom of the World: {INFORME} Annual Report · Analysis: '
           '<a href="https://populi.org.bo" target="_blank" rel="noopener">Centro de Estudios POPULI</a>')
MADDISON = T('Fuente: <a href="https://www.rug.nl/ggdc/historicaldevelopment/maddison/" target="_blank" rel="noopener">Maddison Project Database 2023</a> '
             f'(Bolt y van Zanden, 2024); cuartil: Fraser Institute, EFW {INFORME} · Elaboración: '
             '<a href="https://populi.org.bo" target="_blank" rel="noopener">Centro de Estudios POPULI</a>',
             'Source: <a href="https://www.rug.nl/ggdc/historicaldevelopment/maddison/" target="_blank" rel="noopener">Maddison Project Database 2023</a> '
             f'(Bolt and van Zanden, 2024); quartile: Fraser Institute, EFW {INFORME} · Analysis: '
             '<a href="https://populi.org.bo" target="_blank" rel="noopener">Centro de Estudios POPULI</a>')
EFW_QUE = ('El índice <strong>Economic Freedom of the World</strong> (EFW) del Fraser Institute califica de 0 a 10 a {n} '
           'jurisdicciones con 45 componentes agrupados en cinco áreas: tamaño del gobierno, sistema legal y derechos de '
           'propiedad, moneda sana, libertad para comerciar internacionalmente y regulación. Más puntaje es más libertad.')
# La misma pregunta en inglés (las áreas, con su nombre oficial). EFW_QUE queda como estaba para quien todavía la usa
# sin pareja; efw_que(n) devuelve la pregunta y la respuesta con sus parejas.
EFW_QUE_EN = ("The Fraser Institute's <strong>Economic Freedom of the World</strong> (EFW) index rates {n} jurisdictions "
              'from 0 to 10 using 45 components grouped into five areas: Size of Government, Legal System and Property '
              'Rights, Sound Money, Freedom to Trade Internationally, and Regulation. A higher score means more freedom.')


def efw_que(n):
    """[pregunta, respuesta] de «¿Qué mide el índice?», las dos con su pareja en inglés."""
    return [T('¿Qué mide el índice de libertad económica?', 'What does the economic freedom index measure?'),
            T(EFW_QUE.format(n=n), EFW_QUE_EN.format(n=n))]


# ── Utilidades ─────────────────────────────────────────────────────────────────────────────────
def num(x, dec=2):
    """Cifra es-BO para los textos: «6,05» · «41.321» · «−0,20» (menos tipográfico, sin «−0,00»).
    Redondea como PM.num en la página (mitad hacia afuera sobre el decimal más corto, la regla de Intl) y
    sobre el mismo valor que viaja en los datos (fino): el texto y la cifra del gráfico nunca difieren."""
    d = Decimal(repr(fino(x))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    s = f'{abs(d):,.{dec}f}'.translate(str.maketrans(',.', '.,'))
    return '−' + s if d < 0 and s.strip('0.,') else s


def num_en(x, dec=2):
    """La misma cifra que num(), con el mismo redondeo, escrita en inglés para la pareja de cada texto:
    «6.05» · «41,321» · «−0.20» (punto decimal, coma de miles), como PM.num con ?lang=en."""
    d = Decimal(repr(fino(x))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    s = f'{abs(d):,.{dec}f}'
    return '−' + s if d < 0 and s.strip('0.,') else s


def usd(x):
    return '$' + num(x, 0)


def verificar(cierto, frase):
    if not cierto:
        raise SystemExit(f'✗ El dato ya no sostiene esta frase del panel: «{frase}». Revisar el texto antes de publicar.')


def media(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def fino(x):
    """Lo que viaja a la página: seis decimales (la página redondea al mostrar, nunca dos veces)."""
    return None if x is None else round(x, 6)


def valores(anio, k='s', region=None):
    return [d[k] for iso, d in panel[anio].items()
            if d.get(k) is not None and (region is None or (iso in meta and meta[iso]['region'] == region))]


def puesto(anio, iso):
    """Puesto de competencia (1 + cuántos puntúan más) y total de jurisdicciones con dato ese año."""
    s = panel[anio][iso]['s']
    todos = valores(anio)
    return 1 + sum(1 for v in todos if v > s), len(todos)


def cuartil(p, n):
    """Cuartil por puesto, con cortes en ⌈n/4⌉, ⌈n/2⌉ y ⌈3n/4⌉: 42, 41, 41 y 41 con 165 (el sobrante va arriba).
    Con el puntaje a dos decimales los empates comparten puesto y un empate en el corte queda entero arriba:
    puede diferir del ranking oficial, que desempata con más decimales."""
    return 1 if p <= math.ceil(n / 4) else 2 if p <= math.ceil(n / 2) else 3 if p <= math.ceil(3 * n / 4) else 4


def alias(iso):
    """Nombres en inglés con que también se puede buscar un país (el de la fuente y los de la tabla)."""
    nom = NOMBRE.get(iso)
    a = {meta[iso]['name']} if iso in meta else set()
    a |= {en for en, es in _es['en'].items() if es == nom}
    return ' '.join(sorted(x for x in a if x.lower() != (nom or '').lower()))


def con_pareja(x):
    """¿Hay algún texto con pareja (T) dentro de x?"""
    if isinstance(x, T):
        return True
    if isinstance(x, dict):
        return any(con_pareja(v) for v in x.values())
    return isinstance(x, (list, tuple)) and any(con_pareja(v) for v in x)


def js(x):
    """Lo que viaja a la página, en JSON compacto. Un texto con pareja (T) sale como la llamada
    T("castellano","inglés"), que la página resuelve según el idioma; donde no hay ninguno, es el JSON de siempre."""
    if isinstance(x, T):
        return f'T({json.dumps(str(x), ensure_ascii=False)},{json.dumps(x.en, ensure_ascii=False)})'
    if not con_pareja(x):
        return json.dumps(x, ensure_ascii=False, separators=(',', ':'))
    if isinstance(x, dict):
        return '{' + ','.join(json.dumps(str(k), ensure_ascii=False) + ':' + js(v) for k, v in x.items()) + '}'
    return '[' + ','.join(js(v) for v in x) + ']'


ORDINAL = {1: 'primera', 2: 'segunda', 3: 'tercera', 4: 'cuarta', 5: 'quinta', 6: 'sexta', 7: 'séptima'}
CARDINAL = {2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
ORDINAL_EN = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh'}
CARDINAL_EN = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'}
# Países en inglés: el nombre ORIGINAL de la fuente (efw_country_meta.json), sin traducir de vuelta desde el castellano.
# Dentro de una frase, a estos el inglés les antepone «the».
CON_THE = {'United States', 'United Kingdom', 'Netherlands', 'Philippines', 'United Arab Emirates', 'Dominican Republic',
           'Central African Republic', 'Kyrgyz Republic', 'Slovak Republic', 'Russian Federation', 'Syrian Arab Republic'}


def pais_en(iso, en_frase=False):
    """Nombre en inglés de un país: el de la fuente; con en_frase=True, con «the» donde hace falta."""
    n = meta.get(iso, {}).get('name', iso)
    return 'the ' + n if en_frase and n in CON_THE else n


# Países en castellano (paises_es.json) que dentro de una frase llevan artículo: los que se nombran con un sustantivo
# común («la República Centroafricana», «el Reino Unido», «los Países Bajos»). Los de uso optativo (Estados Unidos,
# India, Líbano…) van sin él, como en el resto de los textos.
CON_ARTICULO = {'República Centroafricana': 'la', 'República Dominicana': 'la', 'República del Congo': 'la',
                'R. D. del Congo': 'la', 'Unión Soviética': 'la', 'Reino Unido': 'el', 'Países Bajos': 'los',
                'Emiratos Árabes Unidos': 'los'}


def pais_es(iso, en_frase=False):
    """Nombre en castellano de un país; con en_frase=True, con su artículo donde el castellano lo pide (el país sale
    del dato: no se sabe de antemano cuál es). Tras «de» o «a», quien arma la frase contrae «el» (del, al)."""
    n = NOMBRE[iso]
    return f'{CON_ARTICULO[n]} {n}' if en_frase and n in CON_ARTICULO else n
# El acento va de fondo del botón activo: sostiene texto blanco (menta → turquesa, oro → su paso oscuro)
ACENTO = {'areas': '#005F73', 'evolucion': '#9B2226', 'bolivia': '#C71E1D', 'paises': '#0A9396', 'pib': '#A86E00'}


# ── Piezas comunes de las páginas ──────────────────────────────────────────────────────────────
CABEZA = r'''<!DOCTYPE html>
<html lang="es" data-theme="light" style="--acento:@@ACENTO@@">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title@@EN_TITLE@@>@@TITULO@@ · Populi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="comun/monitor.css" />
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <script src="comun/monitor.js"></script>
  <style>
    /* Pastillas con nombre largo (escritorio) y corto (teléfono) */
    .nc { display: none; }
    @media (max-width: 640px) { .nl { display: none; } .nc { display: inline; } }@@ESTILO@@
  </style>
</head>
<body>
  <div class="wrap">
    <div class="sec-hd">
      <h2 class="sec-title"@@EN_TITULO@@><span class="accent-bar"></span>@@TITULO@@</h2>
      <p class="sec-sub"@@EN_BAJADA@@>@@BAJADA@@</p>
    </div>
'''

PIE = r'''
    <div class="edu-grid" id="preguntas"></div>
    <div class="source"><span class="source-txt" id="fuente"@@EN_FUENTE@@>@@FUENTE@@</span></div>
  </div>

  <script>
  (function () {
    var C = PM.C, T = PM.t, D = @@DATOS@@;
@@COMUN@@
@@JS@@
  })();
  </script>
</body>
</html>
'''

# JavaScript que comparten las cuatro páginas de series de tiempo
JS_COMUN = r'''
    // ── Eje de años PROPORCIONAL (de valor, no de categorías) ─────────────────────────────────
    // El tramo quinquenal (1970, 1975… 2000) ocupa el ancho que le toca. Rótulos derechos cada 1, 2, 5,
    // 10, 20… años según el ancho del trazado, con el MISMO criterio que PM.ejeTiempo: el aire entre rótulos
    // sale del ancho del texto, y el ancho del trazado es el medido (PM.montar lo mide y, si el estimado no
    // coincidía, vuelve a armar el eje). Marcas menores por año o por lustro cuando entran.
    function ejeAnios(a0, a1, el, extra) {
      var chico = PM.pequeno(), dk = PM.dk(), fs = chico ? 10 : 10.5, car = fs * 0.6 + 0.15;
      var util = el._util && el._util.ancho === el.clientWidth ? el._util.util : Math.max(140, (el.clientWidth || 600) - 64);
      var px = util / Math.max(1, a1 - a0);
      var aire = 4 * car + (chico ? 12 : 14);
      var paso = [1, 2, 5, 10, 20, 40, 50, 100].filter(function (k) {
        return (a0 % k === 0 || (k % 10 === 0 && a0 % 10 === 0)) && k * px >= aire;
      })[0] || 100;
      var menor = [1, 5, 10].filter(function (m) { return paso % m === 0 && m < paso && m * px >= 9; })[0];
      var linea = dk ? '#3A4549' : '#C9CDCE';
      return PM.mezclar({
        type: 'value', min: a0, max: a1, interval: paso, _util: util,
        axisLine: { show: true, onZero: false, lineStyle: { color: linea } },
        axisTick: { show: true, length: 4, lineStyle: { color: linea } },
        minorTick: { show: !!menor, splitNumber: menor ? paso / menor : 1, length: 2, lineStyle: { color: linea } },
        splitLine: { show: false }, axisPointer: { snap: true },
        axisLabel: {
          margin: 9, hideOverlap: true,
          formatter: function (v) { var a = Math.round(v); return (a - a0) % paso === 0 ? '{a|' + a + '}' : ''; },
          rich: { a: { fontFamily: PM.mono(), fontSize: fs, lineHeight: fs + 4, fontWeight: 600,
            color: dk ? 'rgba(226,232,240,.9)' : 'rgba(0,18,25,.8)' } }
        }
      }, extra);
    }
    // Eje Y en pasos de 0,5, 1 o 2 (los que dejen 4 a 6 cortes), con base y techo en el paso
    function rangoY(vals, piso, techo) {
      var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), paso = 2;
      [0.5, 1, 2].some(function (p) { if ((Math.ceil(hi / p) - Math.floor(lo / p)) <= 6) { paso = p; return true; } });
      return { min: Math.max(piso, Math.floor(lo / paso) * paso), max: Math.min(techo, Math.ceil(hi / paso) * paso), interval: paso };
    }
    // Serie anual sobre el eje de años: pares [año, valor]; protagonista con relleno y punto final con halo
    function serieAnual(s, anios, vals) {
      var data = anios.map(function (a, i) { return [a, vals[i] == null ? null : vals[i]]; }), n = -1;
      data.forEach(function (d, i) { if (d[1] != null) n = i; });
      var o = PM.linea(s.color, { ancho: s.ancho, punteada: s.punteada, extra: {
        name: s.nombre, data: data, connectNulls: true, z: s.area ? 4 : 3,
        markPoint: n >= 0 ? PM.puntoFinal(s.color, data[n][0], data[n][1]) : undefined
      } });
      if (s.area) o.areaStyle = { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: PM.rgba(s.color, PM.dk() ? 0.16 : 0.10) }, { offset: 1, color: PM.rgba(s.color, 0) }]) };
      return o;
    }
    // Hitos: raya punteada de umbral (1,25 px pizarra) y rótulo derecho ARRIBA del trazado
    function hitos(lista, chico) {
      var pz = PM.dk() ? '#8A9699' : '#5C6B70';
      return { silent: true, symbol: 'none', animation: false,
        lineStyle: { color: pz, width: 1.25, type: [4, 3] },
        label: { show: true, position: 'end', distance: 7, color: pz, fontFamily: PM.inter(), fontSize: chico ? 10 : 10.5, fontWeight: 600 },
        data: lista.map(function (h) { return { xAxis: h.anio, label: { formatter: chico ? h.corto : h.largo, align: h.alinear } }; }) };
    }
    // Clave de color en el tooltip, que es de vidrio oscuro en los dos temas: la tinta se invierte como en oscuro
    function clave(c) { return String(PM.col(c)).toUpperCase() === '#001219' ? '#E2E8F0' : c; }
    // Nombre de pastilla: largo en escritorio, corto en el teléfono
    function rotulo(largo, corto) { return !corto || largo === corto ? largo : '<span class="nl">' + largo + '</span><span class="nc">' + corto + '</span>'; }
'''


def pagina(nombre, titulo, bajada, acento, cuerpo, datos, js_pagina, fuente=FRASER, estilo='', comun=JS_COMUN):
    """Arma y escribe una página. El título, la bajada y la fuente que llegan con pareja (T) llevan su inglés en el
    atributo data-en del marcado (PM.traducir lo pone con ?lang=en); los que llegan como texto simple salen sin él.
    En el guion, `T` es PM.t: los textos con pareja de los datos y de las plantillas salen como T('castellano', 'inglés')."""
    en = {'@@EN_TITLE@@': '', '@@EN_TITULO@@': '', '@@EN_BAJADA@@': '', '@@EN_FUENTE@@': ''}
    if isinstance(titulo, T):
        en['@@EN_TITLE@@'] = f' data-en="{escape(titulo.en)} · Populi"'
        # el data-en trae el contenido COMPLETO del elemento, con sus mismas etiquetas (comillas simples por fuera)
        en['@@EN_TITULO@@'] = f" data-en='<span class=\"accent-bar\"></span>{escape(titulo.en)}'"
    if isinstance(bajada, T):
        en['@@EN_BAJADA@@'] = f' data-en="{escape(bajada.en)}"'
    if isinstance(fuente, T):
        assert "'" not in fuente.en, 'la fuente en inglés va entre comillas simples: no puede traer una adentro'
        en['@@EN_FUENTE@@'] = f" data-en='{fuente.en}'"
    html = CABEZA + cuerpo + PIE
    for k, v in {'@@JS@@': js_pagina, '@@COMUN@@': comun, '@@ACENTO@@': acento, **en, '@@TITULO@@': titulo,
                 '@@BAJADA@@': bajada, '@@ESTILO@@': estilo, '@@FUENTE@@': fuente, '@@DATOS@@': js(datos)}.items():
        html = html.replace(k, v)
    assert '@@' not in html, nombre
    (OUT / nombre).write_text(html, encoding='utf-8')
    print(f'  OK {nombre}  ({len(html.encode("utf-8")) / 1024:.0f} KB)')


# Panel de lectura: bloques [rótulo, texto] o ['ctx', nota de fuente], escritos por el generador
JS_PANEL = r'''
    function panel() {
      document.getElementById('panel').innerHTML = D.panel.map(function (b) {
        return b[0] === 'ctx' ? PM.ctx(b[1]) : PM.pb(PM.var('--acento'), b[0], null, b[1]);
      }).join('');
    }
'''


# ════════════════════════════════════════════════════════════════════════════════════════════════
# 1. ÁREAS POR REGIÓN — gráfico de puntos
# ════════════════════════════════════════════════════════════════════════════════════════════════
CUERPO_AREAS = r'''
    <div class="kpi-grid" id="kpis"></div>

    <div class="main-grid">
      <div class="chart-card">
        <div class="chart-ctrl">
          <div class="tog-grp" id="pastillas"></div>
          <span class="ref" data-en='<span class="raya"></span>Overall index'><span class="raya"></span>Índice general</span>
        </div>
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span data-en="Loading data…">Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t" data-en="Reading the chart">Lectura del gráfico</span><span class="panel-hd-d" id="panel-fecha"></span></div>
        <div class="panel-body" id="panel"></div>
      </div>
    </div>
'''
ESTILO_AREAS = r'''
    /* el punto de cada área en su pastilla; la raya del índice general, vertical como en el gráfico */
    #pastillas .lp.area { border-radius: 50%; }
    .ref .raya { width: 3px; height: 13px; background: var(--tinta); flex: none; }'''

JS_AREAS = r'''
    var AREAS = D.areas, FILAS = D.regiones, activas = new Set(AREAS.map(function (a) { return a.k; })), grafico;

    document.getElementById('panel-fecha').textContent = D.anio;
    PM.pastillas(document.getElementById('pastillas'), AREAS.map(function (a) {
      return { k: a.k, nombre: rotulo(a.nombre, a.corto), color: a.color, forma: 'area' };
    }), activas, function () { grafico.redibujar(); });
    cifras(); panel();
    var el = document.getElementById('chart');
    el.innerHTML = '';
    grafico = PM.montar(el, opciones);
    PM.alCambiarTema(function () { cifras(); panel(); });
    PM.preguntas(document.getElementById('preguntas'), D.preguntas);

    // imagen y CSV: el gráfico no tiene eje de categorías en X ni una serie por fila
    PM.leyendaImagen = function () {
      return AREAS.filter(function (a) { return activas.has(a.k); })
        .map(function (a) { return { name: a.nombre, color: PM.col(a.color), forma: 'punto' }; })
        .concat([{ name: T('Índice general', 'Overall index'), color: PM.col(C.tinta), forma: 'area' }]);
    };
    PM.tablaDatos = function () {
      return { cols: [T('Región', 'Region'), T('Países', 'Countries'), T('Índice general', 'Overall index')].concat(AREAS.map(function (a) { return a.nombre; })),
        filas: FILAS.map(function (f) { return [f.nombre, f.n, f.s].concat(f.a); }) };
    };

    function cifras() {
      var b = FILAS[0], w = FILAS[FILAS.length - 1], l = FILAS[D.lac];
      document.getElementById('kpis').innerHTML =
        PM.kpi({ color: C.turquesa, rotulo: T('Región más libre', 'Freest region'), valor: PM.num(b.s, 2), delta: b.nombre, serie: b.serie }) +
        PM.kpi({ color: C.rojo, rotulo: T('Región menos libre', 'Least free region'), valor: PM.num(w.s, 2), delta: w.nombre, serie: w.serie }) +
        PM.kpi({ color: C.oro, rotulo: T('América Latina y el Caribe', 'Latin America & the Caribbean'), valor: PM.num(l.s, 2), delta: T('puesto ' + (D.lac + 1) + ' de ' + FILAS.length, 'rank ' + (D.lac + 1) + ' of ' + FILAS.length), serie: l.serie }) +
        PM.kpi({ color: C.petroleo, rotulo: T('Mayor brecha entre regiones', 'Widest gap between regions'), valor: PM.num(D.brecha.v, 2), delta: D.brecha.area });
    }
@@PANEL@@
    function opciones() {
      var dk = PM.dk(), chico = PM.pequeno(), card = PM.var('--card') || '#fff', tinta = PM.col(C.tinta);
      var act = AREAS.filter(function (a) { return activas.has(a.k); }), vals = [];
      FILAS.forEach(function (f) { vals.push(f.s); act.forEach(function (a) { vals.push(f.a[a.i]); }); });
      var x0 = Math.floor(Math.min.apply(null, vals)), x1 = Math.ceil(Math.max.apply(null, vals)), linea = dk ? '#3A4549' : '#C9CDCE';
      var extremos = function (f) { var v = act.map(function (a) { return f.a[a.i]; }).concat([f.s]); return [Math.min.apply(null, v), Math.max.apply(null, v)]; };
      var series = [
        // la línea gris une el área más baja con la más alta de cada región
        { name: '_rango', type: 'custom', silent: true, z: 1, tooltip: { show: false },
          renderItem: function (p, api) {
            var e = extremos(FILAS[p.dataIndex]), a = api.coord([e[0], p.dataIndex]), b = api.coord([e[1], p.dataIndex]);
            return { type: 'line', shape: { x1: a[0], y1: a[1], x2: b[0], y2: b[1] }, style: { stroke: linea, lineWidth: 2 } };
          },
          data: FILAS.map(function (f, i) { return [f.s, i]; }) },
        // el índice general: raya vertical de tinta, debajo de los puntos
        { name: T('Índice general', 'Overall index'), type: 'scatter', z: 2, symbol: 'rect', symbolSize: [3, chico ? 17 : 21],
          itemStyle: { color: tinta }, emphasis: { disabled: true }, data: FILAS.map(function (f, i) { return [f.s, i]; }) }
      ];
      act.forEach(function (a) {
        series.push({ name: a.nombre, type: 'scatter', z: 3, symbolSize: chico ? 10 : 12,
          itemStyle: { color: PM.col(a.color), borderColor: card, borderWidth: 1.5 }, emphasis: { scale: 1.3 },
          data: FILAS.map(function (f, i) { return [f.a[a.i], i]; }) });
      });
      return {
        grid: PM.grid({ top: 6, bottom: 2 }),
        xAxis: PM.ejeY({ extra: { type: 'value', min: x0, max: x1, interval: 1,
          axisLine: { show: true, lineStyle: { color: linea } } } }),
        // el nombre de la región va ARRIBA de su fila, dentro del trazado: todo el ancho es para los puntos
        yAxis: { type: 'category', inverse: true, data: FILAS.map(function (f) { return f.nombre; }),
          axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false },
          axisLabel: { inside: true, align: 'left', verticalAlign: 'bottom', margin: 0, padding: [0, 0, chico ? 8 : 11, 0],
            formatter: function (v, i) { return '{n|' + v + '}  {v|' + PM.num(FILAS[i].s, 2) + '}'; },
            rich: { n: { fontFamily: PM.inter(), fontSize: chico ? 10.5 : 11.5, fontWeight: 600, color: tinta },
                    v: { fontFamily: PM.mono(), fontSize: chico ? 10 : 10.5, fontWeight: 600, color: PM.var('--pizarra') } } } },
        tooltip: PM.tooltip(function (ps) {
          var p = ps.filter(function (q) { return q.seriesName && q.seriesName.charAt(0) !== '_'; })[0];
          if (!p) return '';
          var f = FILAS[p.dataIndex], h = PM.ttTitulo(f.nombre, T(f.n + (f.n === 1 ? ' país' : ' países') + ' · ' + D.anio, f.n + (f.n === 1 ? ' country' : ' countries') + ' · ' + D.anio));
          act.forEach(function (a) { h += PM.ttFila(clave(a.color), a.nombre, PM.num(f.a[a.i], 2), 'area'); });
          return h + PM.ttTotal(T('Índice general', 'Overall index'), PM.num(f.s, 2));
        }, { axisPointer: PM.sombraEje() }),
        series: series
      };
    }
'''


def gen_areas_regiones():
    anio = ULTIMO
    filas = []
    for reg_en, reg_es in REGION.items():
        isos = [i for i in panel[anio] if i in meta and meta[i]['region'] == reg_en and panel[anio][i].get('s') is not None]
        filas.append({   # la región, con su pareja: en inglés, el nombre original de la fuente
            'k': reg_en, 'nombre': T(reg_es, reg_en), 'n': len(isos), 's': fino(media([panel[anio][i]['s'] for i in isos])),
            'a': [fino(media([panel[anio][i].get(a['k']) for i in isos])) for a in AREAS],
            'serie': [fino(media(valores(y, 's', reg_en))) for y in ANUALES],
        })
    filas.sort(key=lambda f: -f['s'])
    n_total = len(valores(anio))
    ilac = next(i for i, f in enumerate(filas) if f['k'] == LAC)
    lac = filas[ilac]

    # brechas entre regiones por área: (rango, mínimo, máximo, área)
    rango = []
    for j in range(5):
        v = [f['a'][j] for f in filas]
        rango.append((max(v) - min(v), min(v), max(v), j))
    ancha, angosta = max(rango), min(rango)
    a1 = sorted(filas, key=lambda f: -f['a'][0])
    eca = next(f for f in filas if f['k'] == 'Europe & Central Asia')
    verificar(angosta[3] == 0, 'la menor brecha entre regiones está en Tamaño del gobierno')
    verificar(eca in filas[:2] and eca in a1[-2:] and eca not in a1[:2],
              f'en Tamaño del gobierno el orden se invierte: {a1[0]["nombre"]} y {a1[1]["nombre"]} superan a {eca["nombre"]}')
    lac_orden = sorted(range(5), key=lambda j: lac['a'][j])
    na = next(f for f in filas if f['k'] == 'North America')
    na_paises = sorted(NOMBRE[i] for i in panel[anio] if i in meta and meta[i]['region'] == 'North America')
    verificar(len(na_paises) == 2, 'Norteamérica son solo dos países')
    verificar(meta['IND']['region'] == meta['BTN']['region'], 'India y Bután son de la misma región')
    nom = lambda j: AREAS[j]['nombre']
    # Para la pareja en inglés de cada texto: las mismas cifras con num_en (ne), el nombre oficial del área (.en),
    # la región y los países con el nombre original de la fuente
    ne = num_en
    na_en = [pais_en(i, en_frase=True) for i in sorted((i for i in panel[anio] if i in meta and meta[i]['region'] == 'North America'),
                                                       key=lambda i: meta[i]['name'])]

    p = [
        [T('Qué muestra', 'What it shows'),
         T('Cada fila es una región; cada punto, el promedio de sus países en una de las cinco áreas del '
           'índice (0 a 10: más es más libre), y la raya vertical, el índice general. Las filas van de la región más libre '
           'a la menos libre; la línea gris une su peor y su mejor área.',
           'Each row is a region; each dot, the average of its countries in one of the five areas of the index (0 to 10: '
           'higher is freer); and the vertical bar, the overall index. The rows run from the freest region to the least '
           'free; the gray line joins its worst and its best area.')],
        [T('Patrones clave', 'Key patterns'),
         T(f'<strong>{filas[0]["nombre"]}</strong> ({num(filas[0]["s"])}) y <strong>{filas[1]["nombre"]}</strong> '
           f'({num(filas[1]["s"])}) encabezan; <strong>{filas[-2]["nombre"]}</strong> ({num(filas[-2]["s"])}) y '
           f'<strong>{filas[-1]["nombre"]}</strong> ({num(filas[-1]["s"])}) cierran. La mayor brecha entre regiones está en '
           f'<strong>{nom(ancha[3])}</strong> (de {num(ancha[1])} a {num(ancha[2])}) y la menor, en <strong>{nom(angosta[3])}</strong> '
           f'(de {num(angosta[1])} a {num(angosta[2])}), donde además el orden se invierte: {a1[0]["nombre"]} '
           f'({num(a1[0]["a"][0])}) y {a1[1]["nombre"]} ({num(a1[1]["a"][0])}) superan a {eca["nombre"]} ({num(eca["a"][0])}), '
           'porque esa área premia que el gasto, las transferencias y los impuestos sean bajos.',
           f'<strong>{filas[0]["nombre"].en}</strong> ({ne(filas[0]["s"])}) and <strong>{filas[1]["nombre"].en}</strong> '
           f'({ne(filas[1]["s"])}) lead; <strong>{filas[-2]["nombre"].en}</strong> ({ne(filas[-2]["s"])}) and '
           f'<strong>{filas[-1]["nombre"].en}</strong> ({ne(filas[-1]["s"])}) come last. The widest gap between regions is in '
           f'<strong>{nom(ancha[3]).en}</strong> (from {ne(ancha[1])} to {ne(ancha[2])}) and the narrowest, in '
           f'<strong>{nom(angosta[3]).en}</strong> (from {ne(angosta[1])} to {ne(angosta[2])}), where the order is also '
           f'reversed: {a1[0]["nombre"].en} ({ne(a1[0]["a"][0])}) and {a1[1]["nombre"].en} ({ne(a1[1]["a"][0])}) outscore '
           f'{eca["nombre"].en} ({ne(eca["a"][0])}), because that area rewards low spending, low transfers and low taxes.')],
        [T('América Latina y el Caribe', 'Latin America & the Caribbean'),
         T(f'Con <strong>{num(lac["s"])}</strong>, la región es la {ORDINAL[ilac + 1]} de '
           f'{CARDINAL[len(filas)]}. Su área más débil es <strong>{nom(lac_orden[0])}</strong> ({num(lac["a"][lac_orden[0]])}), '
           f'seguida de <strong>{nom(lac_orden[1])}</strong> ({num(lac["a"][lac_orden[1]])}); la mejor, '
           f'<strong>{nom(lac_orden[-1])}</strong> ({num(lac["a"][lac_orden[-1]])}).',
           f'At <strong>{ne(lac["s"])}</strong>, the region is the {ORDINAL_EN[ilac + 1]} of '
           f'{CARDINAL_EN[len(filas)]}. Its weakest area is <strong>{nom(lac_orden[0]).en}</strong> ({ne(lac["a"][lac_orden[0]])}), '
           f'followed by <strong>{nom(lac_orden[1]).en}</strong> ({ne(lac["a"][lac_orden[1]])}); its best, '
           f'<strong>{nom(lac_orden[-1]).en}</strong> ({ne(lac["a"][lac_orden[-1]])}).')],
        ['ctx',
         T(f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report (datos de {anio}): '
           f'{n_total} jurisdicciones, 5 áreas y 45 componentes. Promedio simple de los países de cada región (regiones del '
           f'Banco Mundial); {na["nombre"]} son solo {na_paises[0]} y {na_paises[1]}.',
           f'<strong>Source:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report ({anio} data): '
           f'{n_total} jurisdictions, 5 areas and 45 components. Simple average of the countries in each region (World Bank '
           f'regions); {na["nombre"].en} is only {na_en[0]} and {na_en[1]}.')],
    ]
    preguntas = [
        efw_que(n_total),
        [T('¿Por qué una región pobre puede puntuar alto en Tamaño del gobierno?', 'Why can a poor region score high in Size of Government?'),
         T('Porque el área mide cuánto del ingreso pasa por el Estado: consumo e inversión pública, transferencias y '
           'subsidios, empresas estatales y tasas marginales de impuestos. Un Estado chico puntúa alto aunque el país sea pobre, y los '
           f'Estados de bienestar puntúan bajo: {eca["nombre"]} marca {num(eca["a"][0])} en esa área y {num(eca["a"][2])} en '
           'Moneda sana.',
           'Because the area measures how much of income passes through the state: government consumption and investment, '
           'transfers and subsidies, state-owned enterprises and marginal tax rates. A small state scores high even if the '
           f'country is poor, and welfare states score low: {eca["nombre"].en} scores {ne(eca["a"][0])} in that area and '
           f'{ne(eca["a"][2])} in Sound Money.')],
        [T('¿Por qué promedios simples?', 'Why simple averages?'),
         T('Cada país pesa lo mismo: el promedio describe las políticas de los países de la región, no la experiencia de su '
           'población (en Asia del Sur, India no pesa más que Bután).',
           'Each country carries the same weight: the average describes the policies of the countries in the region, not '
           'the experience of its population (in South Asia, India weighs no more than Bhutan).')],
    ]
    datos = {
        'anio': anio, 'lac': ilac,
        'areas': [{'k': a['k'], 'i': j, 'nombre': a['nombre'], 'corto': a['corto'], 'color': a['color']} for j, a in enumerate(AREAS)],
        'regiones': [{'nombre': f['nombre'], 'n': f['n'], 's': f['s'], 'a': f['a'], 'serie': f['serie']} for f in filas],
        'brecha': {'v': fino(ancha[0]), 'area': AREAS[ancha[3]]['corto']},
        'panel': p, 'preguntas': preguntas,
    }
    pagina('areas_regiones.html',
           T('Calificación por Áreas del Índice de Libertad Económica', 'Ratings by Area of the Economic Freedom Index'),
           T(f'Promedio de cada región en las cinco áreas del índice, {anio} · de 0 a 10, más es más libre · {n_total} jurisdicciones',
             f'Average of each region in the five areas of the index, {anio} · from 0 to 10, higher is freer · {n_total} jurisdictions'),
           ACENTO['areas'], CUERPO_AREAS, datos, JS_AREAS.replace('@@PANEL@@', JS_PANEL), estilo=ESTILO_AREAS)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# 2 y 3. SERIES DE TIEMPO — evolución mundial y Bolivia (una plantilla: vista Índice / Áreas)
# ════════════════════════════════════════════════════════════════════════════════════════════════
CUERPO_SERIE = r'''
    <div class="hz-bar">
      <div class="hz-item"><span class="hz-lbl" data-en="View">Vista</span><div class="hz-grp" id="b-vista"></div></div>
    </div>

    <div class="kpi-grid" id="kpis"></div>

    <div class="main-grid">
      <div class="chart-card">
        <div class="chart-ctrl">
          <div class="tog-grp" id="pastillas-indice"></div>
          <div class="tog-grp" id="pastillas-areas" style="display:none"></div>
        </div>
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span data-en="Loading data…">Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t" data-en="Reading the chart">Lectura del gráfico</span><span class="panel-hd-d" id="panel-fecha"></span></div>
        <div class="panel-body" id="panel"></div>
      </div>
    </div>
'''

JS_SERIE = r'''
    // D.indice: series de la vista «Índice» (la primera es la protagonista: 2,5 px y único relleno);
    // D.areas: las cinco áreas (rampa oficial, 1,75 px). Todas sobre los mismos años D.anios.
    var A = D.anios, a0 = A[0], a1 = A[A.length - 1], estado = { vista: 'indice' }, grafico;
    var activas = { indice: new Set(D.indice.map(function (s) { return s.k; })), areas: new Set(D.areas.map(function (s) { return s.k; })) };
    var visibles = function () {
      return (estado.vista === 'indice' ? D.indice : D.areas).filter(function (s) { return activas[estado.vista].has(s.k); });
    };

    document.getElementById('panel-fecha').textContent = a0 + '–' + a1;
    PM.botonera(document.getElementById('b-vista'), [['indice', T('Índice', 'Index')], ['areas', T('Áreas', 'Areas')]], estado.vista, function (v) {
      estado.vista = v;
      document.getElementById('pastillas-indice').style.display = v === 'indice' ? '' : 'none';
      document.getElementById('pastillas-areas').style.display = v === 'areas' ? '' : 'none';
      grafico.redibujar();
    });
    ['indice', 'areas'].forEach(function (v) {
      PM.pastillas(document.getElementById('pastillas-' + v), D[v].map(function (s) {
        return { k: s.k, nombre: rotulo(s.nombre, s.corto), color: s.color, forma: s.punteada ? 'punteada' : 'linea' };
      }), activas[v], function () { grafico.redibujar(); });
    });
    cifras(); panel();
    var el = document.getElementById('chart');
    el.innerHTML = '';
    grafico = PM.montar(el, opciones);
    PM.alCambiarTema(function () { cifras(); panel(); });
    PM.preguntas(document.getElementById('preguntas'), D.preguntas);

    PM.leyendaImagen = function () {
      return visibles().map(function (s) { return { name: s.nombre, color: PM.col(s.color), forma: s.punteada ? 'punteada' : 'linea' }; });
    };
    PM.tablaDatos = function () {
      var vs = visibles();
      return { cols: [T('Año', 'Year')].concat(vs.map(function (s) { return s.nombre; })),
        filas: A.map(function (a, i) { return [a].concat(vs.map(function (s) { return s.v[i]; })); }) };
    };

    function cifras() {
      document.getElementById('kpis').innerHTML = D.cifras.map(function (k) {
        return PM.kpi({ color: k.color, rotulo: k.rotulo, valor: PM.num(k.valor, k.dec == null ? 2 : k.dec), delta: k.delta, tono: k.tono, serie: k.serie });
      }).join('');
    }
@@PANEL@@
    function opciones() {
      var chico = PM.pequeno(), el = document.getElementById('chart'), vs = visibles(), vals = [];
      vs.forEach(function (s) { s.v.forEach(function (x) { if (x != null) vals.push(x); }); });
      var series = vs.map(function (s) { return serieAnual(s, A, s.v); });
      if (series.length) series[0].markLine = hitos(D.hitos, chico);
      var esIndice = estado.vista === 'indice';
      return {
        grid: PM.grid({ top: 30, bottom: 2 }),
        xAxis: ejeAnios(a0, a1, el),
        yAxis: PM.ejeY({ unidad: chico ? D.unidadCorta : D.unidad, fmt: PM.tick,
          extra: PM.mezclar(rangoY(vals.length ? vals : [0, 10], 0, 10), { nameTextStyle: { align: 'left' } }) }),
        tooltip: PM.tooltip(function (ps) {
          var p = ps.filter(function (q) { return q.value && q.value[1] != null; });
          if (!p.length) return '';
          var i = A.indexOf(p[0].value[0]);
          if (i < 0) return '';
          var h = PM.ttTitulo(String(A[i]));
          vs.forEach(function (s) { if (s.v[i] != null) h += PM.ttFila(clave(s.color), s.nombre, PM.num(s.v[i], 2), s.punteada ? 'punteada' : 'linea'); });
          if (!esIndice) h += PM.ttTotal(D.total.nombre, PM.num(D.total.v[i], 2));
          else h += PM.ttPie(D.pieTip[i]);
          return h;
        }),
        series: series
      };
    }
'''


def serie_areas(fuente):
    """Las cinco áreas como series de la vista «Áreas»: fuente(k) → valores por año."""
    return [{'k': a['k'], 'nombre': a['nombre'], 'corto': a['corto'], 'color': a['color'], 'ancho': 1.75,
             'v': [fino(x) for x in fuente(a['k'])]} for a in AREAS]


def gen_evolucion_mundial():
    anios = [int(y) for y in ANIOS]
    mundo = [media(valores(y)) for y in ANIOS]
    n = [len(valores(y)) for y in ANIOS]
    fijos = [i for i, d in panel[ANIOS[0]].items()
             if d.get('s') is not None and all(panel[y].get(i, {}).get('s') is not None for y in ANIOS)]
    fijo = [media([panel[y][i]['s'] for i in fijos]) for y in ANIOS]
    area = {a['k']: [media(valores(y, a['k'])) for y in ANIOS] for a in AREAS}
    ix = {a: i for i, a in enumerate(anios)}
    v = lambda serie, a: serie[ix[a]]

    ultimo, a_ult = mundo[-1], anios[-1]
    pico = max(mundo); a_pico = anios[mundo.index(pico)]
    piso = min(mundo); a_piso = anios[mundo.index(piso)]
    # Años 70: cae el promedio, con más gasto (Tamaño del gobierno) e inflación (Moneda sana)
    verificar(v(mundo, 1975) < v(mundo, 1970) and v(area['a1'], 1975) < v(area['a1'], 1970)
              and v(area['a3'], 1975) < v(area['a3'], 1970), 'el promedio cayó en los 70 con más gasto e inflación')
    verificar(v(mundo, 2000) > v(mundo, 1990) > v(mundo, 1980), 'las reformas de los 80 y 90 lo llevaron hacia arriba')
    # COVID: la mayor caída anual desde que la serie es anual, por gasto, regulación y comercio
    caidas = [(mundo[i] - mundo[i - 1], anios[i]) for i in range(1, len(anios)) if anios[i - 1] >= 2000]
    verificar(min(caidas)[1] == 2020, 'el COVID-19 provocó la mayor caída anual de la serie')
    verificar(all(v(area[k], 2020) < v(area[k], 2019) for k in ('a1', 'a4', 'a5')), 'en 2020 cayeron gasto, comercio y regulación')
    nivel = max(a for a in anios if a < 2020 and v(mundo, a) <= v(mundo, 2020))
    m3 = {a: v(area['a3'], a) for a in anios if a >= 2019}
    a_m3 = min(m3, key=m3.get)
    verificar(a_m3 > 2020 and m3[2019] - m3[a_m3] > 0.5, 'la inflación de 2021–2022 hundió a Moneda sana')
    # Después del COVID: el promedio tocó fondo con la inflación y se recupera en parte, de la mano de Moneda sana
    post = {a: v(mundo, a) for a in anios if a >= 2020}
    a_fondo = min(post, key=post.get)
    verificar(a_fondo == a_m3 and a_fondo < a_ult, 'el promedio tocó fondo el mismo año que Moneda sana')
    verificar(v(mundo, 2020) < ultimo < pico, 'en el último año el promedio supera al de 2020, pero no al máximo')
    sube = {a['k']: v(area[a['k']], a_ult) - v(area[a['k']], a_fondo) for a in AREAS}
    otra = max(x for k, x in sube.items() if k != 'a3')
    verificar(sube['a3'] > 2 * otra and sube['a3'] / 5 > (ultimo - post[a_fondo]) / 2,
              'la recuperación la explica sobre todo Moneda sana')
    # «Ninguna otra área subió más de …»: la cota es el máximo de las otras áreas redondeado HACIA ARRIBA a dos
    # decimales (0,0637 → 0,07), para que la frase sea cierta también con todos los decimales del dato
    cota = float(Decimal(repr(fino(otra))).quantize(Decimal('0.01'), rounding=ROUND_CEILING))
    verificar(0 < otra <= cota, 'alguna otra área también subió, y no más que la cota del texto')
    mejora = max(range(5), key=lambda j: v(area[AREAS[j]['k']], a_ult) - v(area[AREAS[j]['k']], 1980))
    quieta = min(range(5), key=lambda j: max(area[AREAS[j]['k']]) - min(area[AREAS[j]['k']]))
    ka, kq = AREAS[mejora]['k'], AREAS[quieta]['k']
    rec = {k: v(area[k], a_ult) - v(area[k], 2020) for k in ('a1', 'a4')}
    verificar(rec['a4'] > 0 and rec['a1'] > 0, 'comercio y tamaño del gobierno mejoraron después de 2020')
    # los que entraron después de 1970: cuántos y de dónde, y que puntúan más bajo
    en_1970 = set(i for i, d in panel[ANIOS[0]].items() if d.get('s') is not None)
    nuevos = [i for i in panel[ULTIMO] if i not in en_1970 and panel[ULTIMO][i].get('s') is not None]
    n_soc = sum(1 for i in nuevos if i in EX_SOCIALISTAS)
    n_afr = sum(1 for i in nuevos if i in meta and meta[i]['region'] == 'Sub-Saharan Africa')
    verificar(fijo[-1] > ultimo and media([panel[ULTIMO][i]['s'] for i in nuevos]) < fijo[-1],
              'los países que entraron después puntúan más bajo')
    a_tot = min(a for a in anios if v(n, a) == n[-1])
    # Ponderado por población (desde 2000, cuando la serie es anual y la cobertura amplia): cada país pesa según
    # su población de Maddison (la de 2022, último año de esa base, para los años siguientes). Con el informe 2025
    # coincidía con el de Fraser al centésimo (6,37 en 2023).
    def ponderado(y):
        a = str(min(int(y), 2022))
        pares = [(d['s'], pob[i][a]) for i, d in panel[y].items() if d.get('s') is not None and pob.get(i, {}).get(a)]
        return sum(x * w for x, w in pares) / sum(w for _, w in pares)
    pond = [ponderado(y) if int(y) >= 2000 else None for y in ANIOS]
    verificar(all(q < m for q, m in zip(pond, mundo) if q is not None), 'ponderado por población, el promedio es menor')
    sin_pob = [i for i, d in panel[ULTIMO].items() if d.get('s') is not None and not pob.get(i, {}).get('2022')]
    pob_wdi = {c['iso']: c['population'] for c in cons if c.get('population')}
    peso_sin = sum(pob_wdi.get(i, 0) for i in sin_pob) / sum(pob_wdi.get(i, 0) for i, d in panel[ULTIMO].items() if d.get('s') is not None)
    verificar(peso_sin < 0.01, 'las jurisdicciones sin población en Maddison pesan menos del 1 %')
    grandes = sorted((i for i, d in panel[ULTIMO].items() if d.get('s') is not None and pob.get(i, {}).get('2022')),
                     key=lambda i: -pob[i]['2022'])[:8]
    bajo = [i for i in grandes if panel[ULTIMO][i]['s'] < ultimo]
    # El texto nombra a UNO DE LOS DOS más poblados que puntúe por debajo del promedio simple, sin decir que es «el más
    # poblado»: los pesos son la población de 2022 y la frase habla del último año del índice. Los demás van en la lista.
    gigantes = [i for i in grandes[:2] if i in bajo]
    verificar(gigantes, 'uno de los dos países más poblados puntúa por debajo del promedio simple')
    gigante = gigantes[0]
    otros_bajo = [i for i in bajo if i != gigante]
    verificar(otros_bajo, 'otros de los ocho más poblados también puntúan por debajo del promedio')
    # Años del índice posteriores al último de la base de población: son los que se ponderan con la población de 2022
    tras_pob = [a for a in anios if a > 2022]
    verificar(tras_pob and max(int(a) for a in pob[gigante]) == 2022, 'la población de Maddison llega a 2022 y el índice sigue')
    qp = [x for x in pond if x is not None]
    a_pico_p = [a for a, x in zip(anios, pond) if x is not None][qp.index(max(qp))]
    verificar(a_pico_p == a_pico and pond[-1] < pond[anios.index(2020)] < pond[anios.index(2019)],
              'el ponderado siguió el mismo camino: máximo en el mismo año y caída con el COVID-19')
    nom = lambda i: NOMBRE.get(i, meta.get(i, {}).get('name', i))
    lista = lambda xs: ', '.join(xs[:-1]) + ' y ' + xs[-1] if len(xs) > 1 else xs[0]
    # Para la pareja en inglés de cada texto: las mismas cifras con num_en (ne), el nombre oficial del área (.en)
    # y los países con el nombre original de la fuente
    ne = num_en
    nom_en = lambda i: pais_en(i, en_frase=True)
    lista_en = lambda xs: ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else xs[0]

    p = [
        [T('Tendencia general', 'Overall trend'),
         T(f'El promedio cayó en los <strong>años 70</strong> (de {num(v(mundo, 1970))} en 1970 a '
           f'{num(v(mundo, 1975))} en 1975), con más gasto público e inflación. Las reformas de los 80 y 90 —Reagan, Thatcher, '
           f'la apertura asiática y la caída del socialismo— lo llevaron de {num(v(mundo, 1980))} en 1980 a {num(v(mundo, 2000))} '
           f'en 2000. El máximo llegó en <strong>{a_pico}</strong> ({num(pico)}).',
           f'The average fell in the <strong>1970s</strong> (from {ne(v(mundo, 1970))} in 1970 to '
           f'{ne(v(mundo, 1975))} in 1975), with more public spending and inflation. The reforms of the 1980s and 1990s—Reagan, '
           f'Thatcher, the opening of Asia and the fall of socialism—took it from {ne(v(mundo, 1980))} in 1980 to '
           f'{ne(v(mundo, 2000))} in 2000. The maximum came in <strong>{a_pico}</strong> ({ne(pico)}).')],
        [T('Siglo XXI', '21st century'),
         T(f'La liberalización siguió a ritmo moderado hasta {a_pico}. El <strong>COVID-19</strong> provocó la mayor '
           f'caída anual de la serie (de {num(v(mundo, 2019))} a {num(v(mundo, 2020))}), con más gasto, regulación y trabas al '
           f'comercio: el promedio volvió al nivel de {nivel}. Después, la inflación de 2021–2022 hundió a Moneda sana (de '
           f'{num(m3[2019])} en 2019 a {num(m3[a_m3])} en {a_m3}) y el promedio tocó fondo en {a_fondo} ({num(post[a_fondo])}). '
           f'<strong>Desde entonces se recupera</strong>: en {a_ult} marca {num(ultimo)}, por encima de 2020 pero todavía '
           f'{num(pico - ultimo)} por debajo del máximo de {a_pico}.',
           f'Liberalization continued at a moderate pace until {a_pico}. <strong>COVID-19</strong> caused the largest '
           f'annual drop in the series (from {ne(v(mundo, 2019))} to {ne(v(mundo, 2020))}), with more spending, regulation and '
           f'barriers to trade: the average returned to its {nivel} level. Then the inflation of 2021–2022 sank Sound Money (from '
           f'{ne(m3[2019])} in 2019 to {ne(m3[a_m3])} in {a_m3}) and the average bottomed out in {a_fondo} ({ne(post[a_fondo])}). '
           f'<strong>It has been recovering since then</strong>: in {a_ult} it stands at {ne(ultimo)}, above 2020 but still '
           f'{ne(pico - ultimo)} below the {a_pico} maximum.')],
        [T('Ponderado por población', 'Population-weighted'),
         T(f'Si cada país pesa según su población, el promedio es menor: <strong>{num(pond[-1])}</strong> '
           f'en {a_ult}, frente a {num(ultimo)} del promedio simple. Lo empuja hacia abajo <strong>{nom(gigante)}</strong>, uno de los '
           f'dos países más poblados, con {num(panel[ULTIMO][gigante]["s"])}, junto con {lista([nom(i) for i in otros_bajo])}, también entre los '
           f'ocho más poblados y por debajo del promedio. Siguió el mismo camino: máximo en {a_pico_p} ({num(max(qp))}) y caída con '
           f'el COVID-19.',
           f'If each country is weighted by its population, the average is lower: <strong>{ne(pond[-1])}</strong> '
           f'in {a_ult}, compared with {ne(ultimo)} for the simple average. It is pulled down by <strong>{nom_en(gigante)}</strong>, '
           f'one of the two most populous countries, at {ne(panel[ULTIMO][gigante]["s"])}, along with {lista_en([nom_en(i) for i in otros_bajo])}, '
           f'also among the eight most populous and below the average. It followed the same path: a maximum in {a_pico_p} '
           f'({ne(max(qp))}) and a drop with COVID-19.')],
        [T('Áreas', 'Areas'),
         T(f'<strong>{AREAS[mejora]["nombre"]}</strong> es el área que más mejoró desde 1980 (de {num(v(area[ka], 1980))} '
           f'a {num(v(area[ka], a_ult))}); <strong>{AREAS[quieta]["nombre"]}</strong>, la que menos cambió (entre '
           f'{num(min(area[kq]))} y {num(max(area[kq]))} en toda la serie). La vista <strong>Áreas</strong> las muestra una por una.',
           f'<strong>{AREAS[mejora]["nombre"].en}</strong> is the area that has improved the most since 1980 (from '
           f'{ne(v(area[ka], 1980))} to {ne(v(area[ka], a_ult))}); <strong>{AREAS[quieta]["nombre"].en}</strong>, the one that '
           f'has changed the least (between {ne(min(area[kq]))} and {ne(max(area[kq]))} over the whole series). The '
           f'<strong>Areas</strong> view shows them one by one.')],
        ['ctx',
         T(f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. Promedio simple '
           f'de las jurisdicciones con dato cada año: {n[0]} en 1970, {v(n, 1995)} en 1995, {v(n, 2000)} en 2000 y {n[-1]} desde '
           f'{a_tot}; la línea de los mismos {len(fijos)} países descuenta la entrada de países nuevos. El ponderado usa la '
           f'población del Maddison Project Database 2023 (la de 2022 para {lista([str(a) for a in tras_pob])}); quedan fuera {len(sin_pob)} jurisdicciones '
           f'sin ese dato, que suman menos del {max(1, round(peso_sin * 100 + 0.5))} % de la población. Cada área promedia los '
           f'países con dato en esa área. Hasta 2000 los datos son quinquenales.',
           f'<strong>Source:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. Simple average '
           f'of the jurisdictions with data each year: {n[0]} in 1970, {v(n, 1995)} in 1995, {v(n, 2000)} in 2000 and {n[-1]} since '
           f'{a_tot}; the line for the same {len(fijos)} countries strips out the entry of new countries. The weighted average uses '
           f'the population from the Maddison Project Database 2023 (that of 2022 for {lista_en([str(a) for a in tras_pob])}); {len(sin_pob)} jurisdictions '
           f'without that data are left out, which add up to less than {max(1, round(peso_sin * 100 + 0.5))}% of the population. '
           f'Each area averages the countries with data in that area. Up to 2000 the data are five-yearly.')],
    ]
    preguntas = [
        efw_que(n[-1]),
        [T('¿Por qué hay tres líneas?', 'Why are there three lines?'),
         T(f'El índice calificaba a {n[0]} países en 1970 y hoy a {n[-1]}. De los {len(nuevos)} que entraron después, {n_soc} son '
           f'de la antigua órbita socialista y {n_afr} de África Subsahariana, y en promedio puntúan más bajo: su entrada empuja '
           f'el promedio hacia abajo aunque ningún país empeore. La línea de los <strong>mismos {len(fijos)} países</strong> '
           f'calificados desde 1970 sigue siempre al mismo grupo: marca {num(fijo[-1])} en {a_ult}, frente a {num(ultimo)} del '
           f'promedio de todos, y dibuja la misma historia. La punteada pondera por población: describe la libertad económica '
           f'que vive la persona promedio, no el país promedio ({num(pond[-1])} en {a_ult}).',
           f'The index rated {n[0]} countries in 1970 and rates {n[-1]} today. Of the {len(nuevos)} that joined later, {n_soc} are '
           f'from the former socialist bloc and {n_afr} from Sub-Saharan Africa, and on average they score lower: their entry pulls '
           f'the average down even if no country gets worse. The line for the <strong>same {len(fijos)} countries</strong> '
           f'rated since 1970 always follows the same group: it stands at {ne(fijo[-1])} in {a_ult}, compared with {ne(ultimo)} for '
           f'the average of all, and it tells the same story. The dashed line is weighted by population: it describes the economic '
           f'freedom experienced by the average person, not the average country ({ne(pond[-1])} in {a_ult}).')],
        [T('¿Se recuperó después de 2020?', 'Did it recover after 2020?'),
         T(f'Sólo en parte. La inflación de 2021–2022 llevó a Moneda sana de {num(m3[2019])} en 2019 a {num(m3[a_m3])} en '
           f'{a_m3} y anuló la mejora de otras áreas (entre 2020 y {a_ult}, Libertad para comerciar internacionalmente subió '
           f'{num(rec["a4"])} puntos y Tamaño del gobierno, {num(rec["a1"])}). Con la inflación en baja, Moneda sana volvió a '
           f'{num(m3[a_ult])} en {a_ult}: sube {num(sube["a3"])} puntos desde {a_fondo}, y ninguna otra área subió más de '
           f'{num(cota)}. El promedio ({num(ultimo)}) ya supera al de 2020 ({num(v(mundo, 2020))}), pero no al de {a_pico} '
           f'({num(pico)}).',
           f'Only in part. The inflation of 2021–2022 took Sound Money from {ne(m3[2019])} in 2019 to {ne(m3[a_m3])} in '
           f'{a_m3} and wiped out the improvement in other areas (between 2020 and {a_ult}, Freedom to Trade Internationally rose '
           f'{ne(rec["a4"])} points and Size of Government, {ne(rec["a1"])}). With inflation coming down, Sound Money returned to '
           f'{ne(m3[a_ult])} in {a_ult}: it is up {ne(sube["a3"])} points since {a_fondo}, and no other area rose by more than '
           f'{ne(cota)}. The average ({ne(ultimo)}) is already above that of 2020 ({ne(v(mundo, 2020))}), but not that of {a_pico} '
           f'({ne(pico)}).')],
    ]
    datos = {
        'anios': anios, 'unidad': T('Índice EFW (0 a 10)', 'EFW index (0 to 10)'), 'unidadCorta': T('Índice EFW', 'EFW index'),
        'indice': [
            {'k': 'mundo', 'nombre': T('Promedio mundial', 'World average'), 'color': GRANATE, 'ancho': 2.5, 'area': True,
             'v': [fino(x) for x in mundo]},
            {'k': 'fijo', 'nombre': T(f'Mismos {len(fijos)} países desde 1970', f'Same {len(fijos)} countries since 1970'),
             'corto': T(f'Mismos {len(fijos)} países', f'Same {len(fijos)} countries'),
             'color': PIZARRA, 'ancho': 1.75, 'v': [fino(x) for x in fijo]},
            {'k': 'pond', 'nombre': T('Ponderado por población', 'Population-weighted'), 'color': '#EE9B00', 'ancho': 1.75, 'punteada': True,
             'v': [None if x is None else fino(x) for x in pond]},
        ],
        'areas': serie_areas(lambda k: area[k]),
        'total': {'nombre': T('Índice general', 'Overall index'), 'v': [fino(x) for x in mundo]},
        'pieTip': [T(f'{c} jurisdicciones con dato', f'{c} jurisdictions with data') for c in n],
        'hitos': [{'anio': 1989, 'largo': T('1989 · cae el Muro de Berlín', '1989 · the Berlin Wall falls'), 'corto': '1989', 'alinear': 'left'},
                  {'anio': 2020, 'largo': '2020 · COVID-19', 'corto': '2020', 'alinear': 'right'}],
        'cifras': [
            {'color': GRANATE, 'rotulo': T(f'Promedio mundial · {a_ult}', f'World average · {a_ult}'), 'valor': fino(ultimo),
             'delta': T(f'▼ {num(pico - ultimo)} desde {a_pico}', f'▼ {ne(pico - ultimo)} since {a_pico}'), 'tono': 'malo',
             'serie': [fino(v(mundo, int(y))) for y in ANUALES]},
            {'color': '#0A9396', 'rotulo': T('Máximo de la serie', 'Series maximum'), 'valor': fino(pico),
             'delta': T(f'en {a_pico}', f'in {a_pico}')},
            {'color': '#EE9B00', 'rotulo': T(f'Ponderado por población · {a_ult}', f'Population-weighted · {a_ult}'), 'valor': fino(pond[-1]),
             'delta': T(f'promedio simple {num(ultimo)}', f'simple average {ne(ultimo)}'), 'serie': [fino(x) for x in pond if x is not None]},
            {'color': PIZARRA, 'rotulo': T(f'Jurisdicciones · {a_ult}', f'Jurisdictions · {a_ult}'), 'valor': n[-1], 'dec': 0,
             'delta': T(f'{n[0]} en 1970', f'{n[0]} in 1970')},
        ],
        'panel': p, 'preguntas': preguntas,
    }
    verificar(ultimo < pico, 'el promedio está por debajo de su máximo')
    pagina('evolucion_mundial.html',
           T('Evolución de la Libertad Económica en el Mundo', 'World Trends in Economic Freedom'),
           T(f'Promedio mundial del índice EFW y de sus cinco áreas, {anios[0]}–{a_ult} · de 0 a 10, más es más libre',
             f'World average of the EFW index and of its five areas, {anios[0]}–{a_ult} · from 0 to 10, higher is freer'),
           ACENTO['evolucion'], CUERPO_SERIE, datos, JS_SERIE.replace('@@PANEL@@', JS_PANEL))


def gen_bolivia_efw():
    anios_s = [y for y in ANIOS if 'BOL' in panel[y]]
    anios = [int(y) for y in anios_s]
    bol = [panel[y]['BOL']['s'] for y in anios_s]
    bola = {a['k']: [panel[y]['BOL'].get(a['k']) for y in anios_s] for a in AREAS}
    mundo = [media(valores(y)) for y in anios_s]
    lac = [media(valores(y, 's', LAC)) for y in anios_s]
    pues = [puesto(y, 'BOL') for y in anios_s]
    ix = {a: i for i, a in enumerate(anios)}
    v = lambda serie, a: serie[ix[a]]
    a_ult = anios[-1]
    s_ult, (p_ult, n_ult) = bol[-1], pues[-1]
    pico = max(bol); a_pico = anios[bol.index(pico)]
    piso = min(bol); a_piso = anios[bol.index(piso)]
    p_pico, n_pico = pues[bol.index(pico)]

    # Trayectoria: estancada en la franja baja en los 70, mínimo en 1985 (hiperinflación), giro del DS 21060
    setenta = [v(bol, a) for a in anios if a < 1985]
    verificar(a_piso == 1985 and min(setenta) > piso and max(setenta) - min(setenta) < 0.25,
              'en los 70 Bolivia se estancó en la franja baja y tocó su mínimo en 1985')
    m85 = v(bola['a3'], 1985)
    verificar(m85 < 1, 'en 1985 Moneda sana quedó casi en cero')
    verificar(a_pico > 1985 and v(bol, 1985) < v(bol, 1990) < v(bol, 1995), 'el DS 21060 marcó el giro')
    a_prev = anios[-2]
    meseta = [v(bol, a) for a in anios if 2008 <= a <= a_prev]
    verificar(max(meseta) - min(meseta) < 0.5 and abs(media(meseta) - 6) < 0.25, f'entre 2008 y {a_prev} osciló alrededor de 6')
    verificar(v(bol, 2005) < pico and v(bol, 2008) < v(bol, 2005), 'tras el máximo, el puntaje retrocedió')
    # El último año: la mayor caída anual de la serie, por debajo de la franja de los años anteriores
    caida = bol[-2] - s_ult
    anuales = [bol[i - 1] - bol[i] for i in range(1, len(anios)) if anios[i - 1] >= 2000]
    verificar(caida == max(anuales) and s_ult < min(meseta), f'en {a_ult}, la mayor caída anual de la serie')
    desde = max(a for a in anios[:-1] if v(bol, a) <= s_ult)
    p_prev = pues[-2][0]
    # Qué la movió: las áreas que más cayeron y, dentro de ellas, los componentes de la hoja oficial
    baja = {a['k']: bola[a['k']][-2] - bola[a['k']][-1] for a in AREAS}
    verificar(sorted(baja, key=baja.get)[-2:] == ['a3', 'a4'] and baja['a4'] / 5 > caida * 0.6,
              'la caída vino sobre todo de Comercio internacional, y después de Moneda sana')
    cb = lambda a, k: COMP_BOL[str(a)][k]
    c4 = lambda a: cb(a, '4C Black market exchange rates')
    infl = lambda a: cb(a, '3C Inflation · dato')
    rk = lambda a, n: int(cb(a, f'Area {n} Rank'))
    verificar(int(cb(a_ult, 'EFW RANK')) == p_ult, 'el puesto calculado es el oficial del informe')
    verificar(c4(a_prev) == 10 and c4(a_ult) == 0 and abs((c4(a_prev) - c4(a_ult)) / 4 - baja['a4']) < 0.05,
              'el componente de mercado negro de divisas pasó de 10 a 0 y explica la caída del área')
    verificar(infl(a_ult) > infl(a_prev) and cb(a_ult, '3D Foreign currency bank accounts') == 10,
              'subió la inflación; las cuentas en moneda extranjera siguen libres')
    mejor = max(range(5), key=lambda j: bola[AREAS[j]['k']][-1])
    verificar(AREAS[mejor]['k'] == 'a3', 'Moneda sana sigue siendo la mejor área')
    verificar(s_ult < mundo[-1] and s_ult < lac[-1], 'Bolivia está por debajo del promedio mundial y del latinoamericano')
    lac_a = {a['k']: media(valores(ULTIMO, a['k'], LAC)) for a in AREAS}
    dif = {a['k']: bola[a['k']][-1] - lac_a[a['k']] for a in AREAS}
    sobre = [a for a in AREAS if dif[a['k']] > 0]
    brecha = min(AREAS, key=lambda a: dif[a['k']])
    verificar(len(sobre) == 1 and sobre[0]['k'] == 'a3', 'la única área en que Bolivia supera a la región es Moneda sana')
    n_lac = len(valores(ULTIMO, 's', LAC))
    # Para la pareja en inglés de cada texto: las mismas cifras con num_en (ne) y el nombre oficial del área (.en).
    # El componente 4C va con el nombre del informe EFW: «Black-market exchange rates».
    ne = num_en

    p = [
        [T('Trayectoria histórica', 'Historical path'),
         T(f'Bolivia se estancó en la franja baja durante los años 70 (de {num(bol[0])} en {anios[0]} a '
           f'{num(v(bol, 1980))} en 1980) y tocó su mínimo en <strong>1985</strong> ({num(piso)}), tras las dictaduras militares y en '
           f'plena hiperinflación: ese año Moneda sana marcó {num(m85)} de 10. El <strong>Plan de Estabilización de 1985</strong> '
           f'(DS 21060) marcó el giro: el puntaje subió hasta su máximo en <strong>{a_pico}</strong> ({num(pico)}), cuando '
           f'Bolivia ocupaba el puesto {p_pico} de {n_pico}.',
           f'Bolivia stagnated in the low range during the 1970s (from {ne(bol[0])} in {anios[0]} to '
           f'{ne(v(bol, 1980))} in 1980) and hit its minimum in <strong>1985</strong> ({ne(piso)}), after the military dictatorships '
           f'and in the midst of hyperinflation: that year Sound Money scored {ne(m85)} out of 10. The <strong>1985 Stabilization Plan</strong> '
           f'(Supreme Decree 21060) marked the turning point: the score rose to its maximum in <strong>{a_pico}</strong> '
           f'({ne(pico)}), when Bolivia held rank {p_pico} of {n_pico}.')],
        [T('Período reciente', 'Recent period'),
         T(f'Tras el máximo, el puntaje retrocedió: {num(v(bol, 2005))} en 2005 y {num(v(bol, 2008))} en 2008, '
           f'ya con el modelo de mayor intervención estatal vigente desde 2006. Entre 2008 y {a_prev} osciló alrededor de 6 '
           f'(entre {num(min(meseta))} y {num(max(meseta))}). En <strong>{a_ult}</strong> cayó a <strong>{num(s_ult)}</strong>, '
           f'la mayor caída anual de la serie y el puntaje más bajo desde {desde}: Bolivia pasó del puesto {p_prev} al '
           f'<strong>{p_ult} de {n_ult}</strong>.',
           f'After the maximum, the score fell back: {ne(v(bol, 2005))} in 2005 and {ne(v(bol, 2008))} in 2008, '
           f'by then under the model of greater state intervention in force since 2006. Between 2008 and {a_prev} it hovered '
           f'around 6 (between {ne(min(meseta))} and {ne(max(meseta))}). In <strong>{a_ult}</strong> it fell to '
           f'<strong>{ne(s_ult)}</strong>, the largest annual drop in the series and the lowest score since {desde}: Bolivia '
           f'went from rank {p_prev} to <strong>{p_ult} of {n_ult}</strong>.')],
        [T(f'Qué cayó en {a_ult}', f'What fell in {a_ult}'),
         T(f'De los {num(caida)} puntos que perdió el índice, {num(baja["a4"] / 5)} vienen de '
           f'<strong>{AREAS[3]["nombre"]}</strong>, que se desplomó de {num(bola["a4"][-2])} a {num(bola["a4"][-1])} (puesto '
           f'{rk(a_prev, 4)} → {rk(a_ult, 4)} en esa área): la brecha entre el dólar oficial y el paralelo llevó a '
           f'<strong>cero</strong> el componente de mercado negro de divisas, que tuvo 10 de 10 hasta {a_prev}. '
           f'<strong>Moneda sana</strong> bajó de {num(bola["a3"][-2])} a {num(bola["a3"][-1])} con la inflación '
           f'({num(infl(a_prev), 1)} % en {a_prev}, {num(infl(a_ult), 1)} % en {a_ult}) y sigue siendo la mejor área.',
           f'Of the {ne(caida)} points the index lost, {ne(baja["a4"] / 5)} come from '
           f'<strong>{AREAS[3]["nombre"].en}</strong>, which plunged from {ne(bola["a4"][-2])} to {ne(bola["a4"][-1])} (rank '
           f'{rk(a_prev, 4)} → {rk(a_ult, 4)} in that area): the gap between the official dollar and the parallel dollar drove '
           f'the black-market exchange rates component to <strong>zero</strong>, after it had scored 10 out of 10 until {a_prev}. '
           f'<strong>Sound Money</strong> fell from {ne(bola["a3"][-2])} to {ne(bola["a3"][-1])} with inflation '
           f'({ne(infl(a_prev), 1)}% in {a_prev}, {ne(infl(a_ult), 1)}% in {a_ult}) and remains the best area.')],
        [T('Comparativa', 'Comparison'),
         T(f'En {a_ult} Bolivia ({num(s_ult)}) está por debajo del promedio mundial ({num(mundo[-1])}) y del '
           f'latinoamericano ({num(lac[-1])}), y ocupa el puesto <strong>{p_ult} de {n_ult}</strong>. Frente a la región, la mayor '
           f'brecha está en <strong>{brecha["nombre"]}</strong> ({num(bola[brecha["k"]][-1])} frente a {num(lac_a[brecha["k"]])}) y '
           f'la única área en que Bolivia la supera es <strong>{sobre[0]["nombre"]}</strong> ({num(bola["a3"][-1])} frente a '
           f'{num(lac_a["a3"])}).',
           f'In {a_ult} Bolivia ({ne(s_ult)}) is below the world average ({ne(mundo[-1])}) and the Latin American average '
           f'({ne(lac[-1])}), and holds rank <strong>{p_ult} of {n_ult}</strong>. Compared with the region, the widest gap is in '
           f'<strong>{brecha["nombre"].en}</strong> ({ne(bola[brecha["k"]][-1])} versus {ne(lac_a[brecha["k"]])}) and the only '
           f'area in which Bolivia outscores it is <strong>{sobre[0]["nombre"].en}</strong> ({ne(bola["a3"][-1])} versus '
           f'{ne(lac_a["a3"])}).')],
        ['ctx',
         T(f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. Promedios '
           f'simples: el latinoamericano reúne {n_lac} países en {a_ult}. Hasta 2000 los datos son quinquenales.',
           f'<strong>Source:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. Simple '
           f'averages: the Latin American one covers {n_lac} countries in {a_ult}. Up to 2000 the data are five-yearly.')],
    ]
    preguntas = [
        efw_que(n_ult),
        [T('¿Qué pasó en 1985?', 'What happened in 1985?'),
         T(f'La hiperinflación de 1984–1985 llevó a Moneda sana a {num(m85)} de 10 y al índice de Bolivia a su mínimo '
           f'({num(piso)}). El DS 21060 liberó precios, tipo de cambio y comercio, y frenó la emisión: Moneda sana volvió a '
           f'{num(v(bola["a3"], 1990))} en 1990 y a {num(v(bola["a3"], 1995))} en 1995, y el índice pasó del puesto '
           f'{v(pues, 1985)[0]} de {v(pues, 1985)[1]} en 1985 al {v(pues, 1995)[0]} de {v(pues, 1995)[1]} en 1995.',
           f'The hyperinflation of 1984–1985 took Sound Money to {ne(m85)} out of 10 and Bolivia\'s index to its minimum '
           f'({ne(piso)}). Supreme Decree 21060 freed prices, the exchange rate and trade, and halted money issuance: Sound '
           f'Money returned to {ne(v(bola["a3"], 1990))} in 1990 and to {ne(v(bola["a3"], 1995))} in 1995, and the index went '
           f'from rank {v(pues, 1985)[0]} of {v(pues, 1985)[1]} in 1985 to {v(pues, 1995)[0]} of {v(pues, 1995)[1]} in 1995.')],
        [T('¿Qué es el componente de mercado negro de divisas?', 'What is the black-market exchange rates component?'),
         T('Mide la brecha entre el tipo de cambio oficial y el del mercado paralelo: sin brecha, 10 de 10; con una brecha '
           'muy grande, 0. Es uno de los cuatro componentes de Libertad para comerciar internacionalmente, así que pasar de '
           f'{num(c4(a_prev), 0)} a {num(c4(a_ult), 0)} le restó {num((c4(a_prev) - c4(a_ult)) / 4)} puntos a esa área y '
           f'{num((c4(a_prev) - c4(a_ult)) / 20)} al índice general de Bolivia en {a_ult}.',
           'It measures the gap between the official exchange rate and the parallel market rate: with no gap, 10 out of 10; '
           'with a very large gap, 0. It is one of the four components of Freedom to Trade Internationally, so going from '
           f'{ne(c4(a_prev), 0)} to {ne(c4(a_ult), 0)} took {ne((c4(a_prev) - c4(a_ult)) / 4)} points off that area and '
           f'{ne((c4(a_prev) - c4(a_ult)) / 20)} off Bolivia\'s overall index in {a_ult}.')],
        [T('¿Por qué Moneda sana es la mejor área?', 'Why is Sound Money the best area?'),
         T('El área mide el crecimiento del dinero, la inflación y su volatilidad, y la libertad para tener cuentas en moneda '
           f'extranjera. Con inflación baja ({num(infl(a_prev), 1)} % en {a_prev}) y cuentas en dólares permitidas, Bolivia '
           f'marcó {num(bola["a3"][-2])} en {a_prev}, puesto {rk(a_prev, 3)} del mundo en esa área. En {a_ult} bajó a '
           f'{num(bola["a3"][-1])} (puesto {rk(a_ult, 3)}). El índice todavía no recoge la inflación de {a_ult + 1}: llegará '
           f'con el informe {INFORME + 1}.',
           'The area measures money growth, inflation and its volatility, and the freedom to own foreign currency bank '
           f'accounts. With low inflation ({ne(infl(a_prev), 1)}% in {a_prev}) and dollar accounts allowed, Bolivia '
           f'scored {ne(bola["a3"][-2])} in {a_prev}, rank {rk(a_prev, 3)} in the world in that area. In {a_ult} it fell to '
           f'{ne(bola["a3"][-1])} (rank {rk(a_ult, 3)}). The index does not yet reflect the inflation of {a_ult + 1}: that '
           f'will come with the {INFORME + 1} report.')],
    ]
    datos = {
        'anios': anios, 'unidad': T('Índice EFW (0 a 10)', 'EFW index (0 to 10)'), 'unidadCorta': T('Índice EFW', 'EFW index'),
        'indice': [
            {'k': 'bol', 'nombre': 'Bolivia', 'color': '#C71E1D', 'ancho': 2.5, 'area': True, 'v': [fino(x) for x in bol]},
            # América Latina en oro: con turquesa, frente al gris del promedio mundial no se distinguía (ΔE 11,9)
            {'k': 'lac', 'nombre': T('América Latina y el Caribe', LAC), 'corto': T('América Latina', 'Latin America'),
             'color': '#EE9B00', 'ancho': 1.75, 'v': [fino(x) for x in lac]},
            {'k': 'mundo', 'nombre': T('Promedio mundial', 'World average'), 'color': PIZARRA, 'ancho': 1.75, 'v': [fino(x) for x in mundo]},
        ],
        'areas': serie_areas(lambda k: bola[k]),
        'total': {'nombre': T('Índice de Bolivia', "Bolivia's index"), 'v': [fino(x) for x in bol]},
        'pieTip': [T(f'Bolivia: puesto {pp} de {nn}', f'Bolivia: rank {pp} of {nn}') for pp, nn in pues],
        'hitos': [{'anio': 1985, 'largo': T('1985 · DS 21060', '1985 · Supreme Decree 21060'), 'corto': '1985', 'alinear': 'left'},
                  {'anio': 2006, 'largo': T('2006 · nuevo modelo económico', '2006 · new economic model'), 'corto': '2006', 'alinear': 'left'}],
        'cifras': [
            {'color': '#C71E1D', 'rotulo': f'Bolivia · {a_ult}', 'valor': s_ult,
             'delta': T(f'▼ {num(caida)} en un año · puesto {p_ult} de {n_ult}', f'▼ {ne(caida)} in one year · rank {p_ult} of {n_ult}'),
             'tono': 'malo', 'serie': [v(bol, int(y)) for y in ANUALES]},
            {'color': '#005F73', 'rotulo': T('Máximo', 'Maximum'), 'valor': pico,
             'delta': T(f'{a_pico} · puesto {p_pico}', f'{a_pico} · rank {p_pico}')},
            {'color': '#9B2226', 'rotulo': T('Mínimo', 'Minimum'), 'valor': piso, 'delta': T(f'en {a_piso}', f'in {a_piso}')},
            {'color': AREAS[mejor]['color'], 'rotulo': T(f'Mejor área · {a_ult}', f'Best area · {a_ult}'), 'valor': bola[AREAS[mejor]['k']][-1],
             'delta': AREAS[mejor]['corto'], 'serie': [v(bola[AREAS[mejor]['k']], int(y)) for y in ANUALES]},
        ],
        'panel': p, 'preguntas': preguntas,
    }
    pagina('bolivia_efw.html',
           T('Bolivia en el Índice de Libertad Económica', 'Bolivia in the Economic Freedom Index'),
           T(f'Puntaje general y por áreas, {anios[0]}–{a_ult}, frente al promedio mundial y al de América Latina y el Caribe',
             f'Overall score and score by area, {anios[0]}–{a_ult}, compared with the world average and that of {LAC}'),
           ACENTO['bolivia'], CUERPO_SERIE, datos, JS_SERIE.replace('@@PANEL@@', JS_PANEL))


# ════════════════════════════════════════════════════════════════════════════════════════════════
# 4 y 5. COMPARATIVAS — buscador de países (hasta seis), insignia de cuartil, series sobre el eje de años
# ════════════════════════════════════════════════════════════════════════════════════════════════
# Seis colores como máximo: la regla de la marca (paleta.py: «hasta 6 series pasan todos») y lo que mide
# validate_palette en los dos temas con todos los pares. Bolivia, rojo; los demás, en este orden. En oscuro
# la tinta pasa a #F1F5F9 (y no a #E2E8F0): así se separa de la menta (ΔE 15,9 frente a 13,3).
# El color más débil de cada tema va al final (sólo aparece si el lector agrega un quinto país):
# en claro la menta (1,6:1 sobre blanco), en oscuro el petróleo (2,5:1 sobre #141414).
# Mismo conjunto de colores en los dos temas (validado), reasignado.
COLORES_PAIS = ['#0A9396', '#EE9B00', {'claro': '#005F73', 'oscuro': '#94D2BD'}, {'claro': '#001219', 'oscuro': '#F1F5F9'},
                {'claro': '#94D2BD', 'oscuro': '#005F73'}]
QC = ['#0A9396', '#94D2BD', '#EE9B00', '#C71E1D']   # cuartiles: escala ordinal de la marca (1, el más libre)

# ── Inglés de las comparativas (?lang=en) ──────────────────────────────────────────────────────
# Países: el nombre ORIGINAL de la fuente por código ISO3 (efw_country_meta.json → name, vía pais_en), el mismo de los
# demás gráficos del monitor; no se traduce de vuelta desde el castellano. Los del Maddison que no están en el índice no
# tienen nombre de Fraser: llevan el corriente en inglés, como en castellano («Corea del Norte», «Unión Soviética»).
NOMBRE_EN_EXTRA = {
    'AFG': 'Afghanistan', 'CUB': 'Cuba', 'DMA': 'Dominica', 'GNQ': 'Equatorial Guinea', 'LCA': 'Saint Lucia',
    'PRI': 'Puerto Rico', 'PRK': 'North Korea', 'PSE': 'Palestine', 'STP': 'São Tomé and Príncipe',
    'TKM': 'Turkmenistan', 'UZB': 'Uzbekistan', 'CSK': 'Czechoslovakia', 'SUN': 'Soviet Union', 'YUG': 'Yugoslavia',
}
# Regiones: REGION al revés devuelve el rótulo original del Banco Mundial; los agregados históricos son rótulos propios
REGION_EXTRA_EN = {'Europa · agregado histórico': 'Europe · historical aggregate',
                   'Europa y Asia · agregado histórico': 'Europe and Asia · historical aggregate'}


def nombre_en(iso, en_frase=False):
    """Nombre en inglés de un país de las comparativas: el de la fuente (pais_en) o, fuera del índice, el corriente.
    Un país nuevo del Maddison sin nombre declarado detiene el generador (KeyError): sin pareja no se publica."""
    return pais_en(iso, en_frase) if iso in meta else NOMBRE_EN_EXTRA[iso]


def usd_en(x):
    return '$' + num_en(x, 0)


def regiones_en(paises):
    """{región en castellano: región en inglés} de las regiones que usa la lista de países: las del Banco Mundial
    primero y los agregados históricos al final. Una región sin pareja detiene el generador (KeyError)."""
    tabla = {es: en for en, es in REGION.items()}
    tabla.update(REGION_EXTRA_EN)
    usadas = sorted({d['r'] for d in paises}, key=lambda r: (r in REGION_EXTRA_EN, r))
    return {r: tabla[r] for r in usadas}


def tabla_js(pares, ancho=118):
    """{clave: texto} → el interior de un objeto de JavaScript, con sangría de 6 y líneas de hasta `ancho`:
    `ARE: 'United Arab Emirates', ARG: 'Argentina', …`. La clave va sin comillas si es un identificador (ISO3)."""
    def q(s):
        return json.dumps(s, ensure_ascii=False) if "'" in s or '\\' in s else "'" + s + "'"
    filas, fila = [], ''
    for k, v in pares.items():
        x = (k if k.isascii() and k.isidentifier() else q(k)) + ': ' + q(v)
        if fila and len(fila) + len(x) + 2 > ancho:
            filas.append(fila.rstrip())
            fila = ''
        fila += x + ', '
    filas.append(fila.rstrip().rstrip(','))
    return '\n'.join('      ' + f for f in filas)


CUERPO_COMP = r'''
    <div class="hz-bar">
      <div class="hz-item busca-item">
        <div class="busca" id="busca">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>
          <input type="text" id="buscar" placeholder="Agregar un país (hasta seis)…" data-en-placeholder="Add a country (up to six)…" autocomplete="off" spellcheck="false"
            role="combobox" aria-expanded="false" aria-controls="lista" aria-autocomplete="list" aria-label="Buscar un país para agregar" data-en-aria-label="Search for a country to add" />
          <div class="lista" id="lista" role="listbox"></div>
        </div>
      </div>@@CONTROLES@@
    </div>

    <div class="main-grid">
      <div class="chart-card">
        <div class="chart-ctrl">
          <div class="tog-grp" id="sel"></div>
          <div class="ley" id="ley-q"></div>
        </div>
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span data-en="Loading data…">Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t" data-en="Reading the chart">Lectura del gráfico</span><span class="panel-hd-d" id="panel-fecha"></span></div>
        <div class="panel-body" id="panel"></div>
      </div>
    </div>
'''

ESTILO_COMP = r'''
    /* Buscador (molde v2.3: recto, grises fríos, foco en el acento) */
    .busca-item { flex: 1 1 240px; max-width: 340px; }
    .busca { position: relative; width: 100%; }
    .busca svg { position: absolute; left: 10px; top: 50%; width: 14px; height: 14px; transform: translateY(-50%); color: var(--muted); pointer-events: none; }
    .busca input {
      width: 100%; height: 33px; padding: 0 12px 0 31px; border: 1px solid var(--border); border-radius: var(--r-s);
      background: var(--card); color: var(--tinta); font: 500 .74rem/1 'Inter', sans-serif; outline: none;
      transition: border-color .2s, box-shadow .2s;
    }
    .busca input::placeholder { color: var(--muted); }
    .busca input:focus { border-color: var(--acento); box-shadow: 0 0 0 3px color-mix(in srgb, var(--acento) 16%, transparent); }
    .lista {
      position: absolute; top: calc(100% + 4px); left: 0; right: 0; z-index: 30; max-height: 286px; overflow-y: auto;
      background: var(--card); border: 1px solid var(--border); border-radius: var(--r-s);
      box-shadow: 0 16px 34px -14px rgba(0, 18, 25, .4); display: none; scrollbar-width: thin;
    }
    .lista.abierta { display: block; }
    .op {
      display: flex; align-items: center; gap: 9px; width: 100%; padding: 7px 10px; border: 0; background: none;
      cursor: pointer; text-align: left; font: 500 .74rem/1.3 'Inter', sans-serif; color: var(--tinta);
    }
    .op:hover, .op.activa { background: var(--suave); }
    .op[aria-disabled="true"] { cursor: default; opacity: .45; }
    .op .rg { margin-left: auto; padding-left: 10px; font-size: .62rem; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .qd { flex: none; min-width: 34px; padding: 2px 0; text-align: center; font: 700 .6rem/1.3 'JetBrains Mono', monospace; border-radius: var(--r-s); }
    .qd.sin { background: var(--suave); color: var(--muted); }
    .aviso { padding: 8px 10px; font: 500 .66rem/1.45 'Inter', sans-serif; color: var(--muted); border-bottom: 1px solid var(--border); }
    /* País elegido = pastilla (ocultar/mostrar) + botón para quitarlo; insignia de cuartil al final */
    .tag { display: inline-flex; align-items: stretch; }
    .tag .pill { border-right: 0; }
    .tag .pill.fijo { cursor: default; border-right: 1px solid var(--pb); }
    .tag-x {
      display: inline-flex; align-items: center; padding: 0 7px; border: 1px solid var(--border); border-left: 0;
      border-radius: var(--r-s); background: transparent; color: var(--muted); cursor: pointer; font: 600 .78rem/1 'Inter', sans-serif;
      transition: color .2s, background-color .2s, border-color .2s;
    }
    .tag-x:hover { color: var(--tinta); background: var(--suave); }
    .tag.on .tag-x { border-color: var(--pb); }
    .qb { display: inline-flex; align-items: center; gap: 4px; margin-left: 3px; font: 600 .6rem/1 'JetBrains Mono', monospace; color: var(--muted); }
    .qb i { width: 7px; height: 7px; display: inline-block; flex: none; }
    #ley-q .ley-d { border-radius: 0; width: 8px; height: 8px; }
    @media (max-width: 640px) {
      .busca-item { max-width: none; flex-basis: 100%; }
      .tag-x { padding: 0 6px; }
    }'''

JS_COMP = r'''
    // D.paises: [{i iso, n nombre, r región, s puntaje EFW del último año, q cuartil, p puesto, al alias} + datos].
    var PAISES = D.paises, PAIS = {}, MAX = 6, elegidos = D.inicial.slice(), ocultos = new Set(), colorDe = {}, grafico;
    var estado = { escala: 'log', periodo: D.periodos ? D.periodos[0][0] : null };
    var plano = function (t) { return String(t).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); };
    // ── Inglés (?lang=en): países y regiones con el nombre ORIGINAL de la fuente ───────────────────────
    // EN: por código ISO3, `name` de data/efw_country_meta.json (el nombre con que Fraser publica cada jurisdicción, el
    // mismo de los demás gráficos del monitor); no se traduce de vuelta desde el castellano. Los países del Maddison que
    // no están en el índice llevan su nombre corriente en inglés. EN_REGION: las regiones del Banco Mundial tal como
    // vienen en `region` de ese archivo (la tabla inversa de la que las pasó al castellano) y, en el PIB, los rótulos de
    // los agregados históricos. Las dos tablas las escribe el generador desde data/: no se editan a mano.
    var EN = {
@@EN@@
    };
    var EN_REGION = {
@@EN_REGION@@
    };
    // El nombre que se muestra (p.n) pasa a ser el de la fuente: pastillas, líneas, tooltip, lista, leyenda de la imagen y
    // CSV lo toman de ahí, y el orden alfabético y el buscador siguen al nombre mostrado. El nombre en castellano queda
    // como alias (p.al), así el buscador lo sigue encontrando también en inglés.
    if (PM.en) PAISES.forEach(function (p) {
      p.al = p.n + ' ' + (p.al || '');
      if (EN[p.i] != null) p.n = EN[p.i];
      if (EN_REGION[p.r] != null) p.r = EN_REGION[p.r];
    });
    PAISES.forEach(function (p) { PAIS[p.i] = p; p.b = plano(p.n + ' ' + p.i + ' ' + (p.al || '')); p.nb = plano(p.n); });
    PAISES.sort(function (a, b) { return a.n.localeCompare(b.n, PM.en ? 'en' : 'es'); });
    var QN = { 1: T('cuartil 1 · más libre', 'quartile 1 · freest'), 2: T('cuartil 2', 'quartile 2'), 3: T('cuartil 3', 'quartile 3'), 4: T('cuartil 4 · menos libre', 'quartile 4 · least free') };
    @@DATOS_PAIS@@

    // color estable por país: Bolivia, rojo; el resto toma el primer color libre y lo devuelve al salir
    function asignar() {
      var usados = {};
      Object.keys(colorDe).forEach(function (iso) { if (elegidos.indexOf(iso) < 0) delete colorDe[iso]; else usados[colorDe[iso]] = 1; });
      elegidos.forEach(function (iso) {
        if (colorDe[iso] != null) return;
        if (iso === 'BOL') { colorDe[iso] = -1; return; }
        for (var k = 0; k < D.colores.length; k++) if (!usados[k]) { colorDe[iso] = k; usados[k] = 1; return; }
      });
    }
    var color = function (iso) { return colorDe[iso] === -1 ? C.rojo : D.colores[colorDe[iso]]; };
    var qcol = function (q) { return D.qc[q - 1]; };
    var visibles = function () { return elegidos.filter(function (iso) { return !ocultos.has(iso); }); };

    document.getElementById('ley-q').innerHTML = '<span class="ley-i">' + T('Cuartil EFW ' + D.anioQ, 'EFW quartile ' + D.anioQ) + '</span>' + [1, 2, 3, 4].map(function (q) {
      return '<span class="ley-i"><span class="ley-d" style="background:' + qcol(q) + '"></span>' + (q === 1 ? T('1 · más libre', '1 · freest') : q === 4 ? T('4 · menos libre', '4 · least free') : q) + '</span>';
    }).join('');
    (D.controles || []).forEach(function (c) {
      PM.botonera(document.getElementById(c.id), c.ops, estado[c.k], function (v) { estado[c.k] = v; fecha(); grafico.redibujar(); });
    });
    function fecha() { document.getElementById('panel-fecha').textContent = estado.periodo ? estado.periodo + '–' + D.ultimo : D.fecha; }
    fecha();
    asignar(); fichas(); panel(); buscador();
    var el = document.getElementById('chart');
    el.innerHTML = '';
    grafico = PM.montar(el, opciones);
    PM.alCambiarTema(function () { fichas(); panel(); });
    PM.preguntas(document.getElementById('preguntas'), D.preguntas);

    PM.leyendaImagen = function () {
      return visibles().map(function (iso) { return { name: PAIS[iso].n, color: PM.col(color(iso)), forma: 'linea' }; });
    };
    PM.tablaDatos = function () {
      var vs = visibles();
      return { cols: [T('Año', 'Year')].concat(vs.map(function (iso) { return PAIS[iso].n; })),
        filas: anios(vs).map(function (a) { return [a].concat(vs.map(function (iso) { return valor(iso, a); })); }) };
    };

    function insignia(p) {
      return p.q ? '<span class="qb" title="' + QN[p.q] + ' · EFW ' + D.anioQ + '"><i style="background:' + qcol(p.q) + '"></i>' + PM.num(p.s, 2) + '</span>' : '';
    }
    // países elegidos: la pastilla oculta o muestra (la de Bolivia queda fija) y la × lo quita
    function fichas() {
      var cont = document.getElementById('sel'), dk = PM.dk();
      cont.innerHTML = elegidos.map(function (iso) {
        var p = PAIS[iso], on = !ocultos.has(iso), bol = iso === 'BOL', c = color(iso);
        var vars = '--pc:' + PM.col(c) + ';--pf:' + PM.rgba(c, dk ? 0.16 : 0.09) + ';--pb:' + PM.rgba(c, dk ? 0.6 : 0.45);
        return '<span class="tag' + (on ? ' on' : '') + '" data-iso="' + iso + '" style="' + vars + '">' +
          (bol ? '<span class="pill fijo" aria-pressed="true" title="' + T('Bolivia queda siempre en el gráfico', 'Bolivia always stays on the chart') + '" style="' + vars + '">'
               : '<button type="button" class="pill" aria-pressed="' + on + '" title="' + T('Ocultar o mostrar ' + p.n, 'Hide or show ' + p.n) + '" style="' + vars + '">') +
          '<span class="lp"></span>' + p.n + insignia(p) + (bol ? '</span>' : '</button>') +
          (bol ? '' : '<button type="button" class="tag-x" aria-label="' + T('Quitar ' + p.n, 'Remove ' + p.n) + '" title="' + T('Quitar ' + p.n, 'Remove ' + p.n) + '">×</button>') + '</span>';
      }).join('');
      cont.querySelectorAll('button.pill').forEach(function (b) {
        b.addEventListener('click', function () {
          var iso = b.parentNode.dataset.iso;
          if (ocultos.has(iso)) ocultos.delete(iso); else ocultos.add(iso);
          fichas(); grafico.redibujar();
        });
      });
      cont.querySelectorAll('.tag-x').forEach(function (b) {
        b.addEventListener('click', function () { quitar(b.parentNode.dataset.iso); });
      });
    }
    function agregar(iso) {
      if (elegidos.indexOf(iso) >= 0 || elegidos.length >= MAX) return;
      elegidos.push(iso); asignar(); fichas(); grafico.redibujar();
    }
    function quitar(iso) {
      elegidos = elegidos.filter(function (x) { return x !== iso; }); ocultos.delete(iso);
      asignar(); fichas(); grafico.redibujar();
    }

    // ── Buscador: sin tildes, por nombre en español, código o nombre en inglés; con teclado ──
    function buscador() {
      var inp = document.getElementById('buscar'), lst = document.getElementById('lista'), act = -1, ops = [];
      // la librería traduce title y aria-label del marcado, pero no placeholder: su pareja (data-en-placeholder) se pone acá
      inp.placeholder = T(inp.placeholder, inp.getAttribute('data-en-placeholder'));
      function abrir(si) { lst.classList.toggle('abierta', si); inp.setAttribute('aria-expanded', si); }
      function pintar() {
        var q = plano(inp.value.trim()), lleno = elegidos.length >= MAX;
        ops = PAISES.filter(function (p) { return elegidos.indexOf(p.i) < 0 && (!q || p.b.indexOf(q) >= 0); });
        if (q) ops.sort(function (a, b) {
          var ra = a.nb.indexOf(q) === 0 ? 0 : (' ' + a.nb).indexOf(' ' + q) >= 0 ? 1 : 2;
          var rb = b.nb.indexOf(q) === 0 ? 0 : (' ' + b.nb).indexOf(' ' + q) >= 0 ? 1 : 2;
          return ra - rb || a.n.localeCompare(b.n, PM.en ? 'en' : 'es');
        });
        act = ops.length && !lleno ? 0 : -1;
        lst.innerHTML = (lleno ? '<div class="aviso">' + T('Ya hay seis países: quite uno para sumar otro.', 'There are already six countries: remove one to add another.') + '</div>' : '') +
          (ops.length ? ops.map(function (p, k) {
            var c = p.q ? qcol(p.q) : null;
            return '<button type="button" class="op' + (k === act ? ' activa' : '') + '" role="option" data-iso="' + p.i + '"' +
              (lleno ? ' aria-disabled="true"' : '') + '>' +
              '<span class="qd' + (c ? '' : ' sin') + '"' + (c ? ' style="background:' + c + ';color:' + PM.sobre(c) + '"' : '') + '>' + (p.q ? PM.num(p.s, 2) : '—') + '</span>' +
              '<span>' + p.n + '</span><span class="rg">' + p.r + '</span></button>';
          }).join('') : '<div class="aviso">' + T('Ningún país coincide con «' + inp.value.replace(/[<>&"]/g, '') + '».', 'No country matches “' + inp.value.replace(/[<>&"]/g, '') + '”.') + '</div>');
        abrir(true);
      }
      function marcar(k) {
        var bs = lst.querySelectorAll('.op');
        if (!bs.length || elegidos.length >= MAX) return;
        act = (k + bs.length) % bs.length;
        bs.forEach(function (b, j) { b.classList.toggle('activa', j === act); });
        bs[act].scrollIntoView({ block: 'nearest' });
      }
      inp.addEventListener('input', pintar);
      inp.addEventListener('focus', pintar);
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown') { e.preventDefault(); if (!lst.classList.contains('abierta')) pintar(); else marcar(act + 1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); marcar(act - 1); }
        else if (e.key === 'Enter') { e.preventDefault(); if (act >= 0 && ops[act]) { agregar(ops[act].i); inp.value = ''; pintar(); } }
        else if (e.key === 'Escape') { abrir(false); inp.blur(); }
      });
      lst.addEventListener('mousedown', function (e) { e.preventDefault(); });   // el clic no le quita el foco al campo
      lst.addEventListener('click', function (e) {
        var b = e.target.closest('.op'); if (!b || b.getAttribute('aria-disabled') === 'true') return;
        agregar(b.dataset.iso); inp.value = ''; pintar();
      });
      document.addEventListener('click', function (e) { if (!e.target.closest('#busca')) abrir(false); });
    }
@@PANEL@@
    function opciones() {
      var chico = PM.pequeno(), dk = PM.dk(), el = document.getElementById('chart'), vs = visibles(), X = anios(vs), vals = [];
      var r = rango();
      // rótulo al final de cada línea (escritorio): el margen derecho mide el nombre más largo
      var conRotulo = !chico && el.clientWidth >= 520, der = 14;
      if (conRotulo) {
        var cv = (opciones.cv = opciones.cv || document.createElement('canvas').getContext('2d'));
        cv.font = '600 10.5px Inter, sans-serif';
        vs.forEach(function (iso) { der = Math.max(der, Math.ceil(cv.measureText(PAIS[iso].n).width) + 22); });
      }
      var series = vs.map(function (iso) {
        var p = PAIS[iso], bol = iso === 'BOL', col = color(iso), n = -1;
        var data = X.map(function (a) { return [a, valor(iso, a)]; });
        data.forEach(function (d, i) { if (d[1] != null) { n = i; vals.push(d[1]); } });
        var o = PM.linea(col, { ancho: bol ? 2.5 : 1.75, extra: {
          name: p.n, data: data, connectNulls: true, z: bol ? 5 : 3,
          markPoint: n >= 0 ? PM.puntoFinal(col, data[n][0], data[n][1]) : undefined,
          endLabel: { show: conRotulo, formatter: p.n, distance: 9, color: PM.tx(col), fontFamily: PM.inter(), fontSize: 10.5, fontWeight: 600 },
          labelLayout: { moveOverlap: 'shiftY' }
        } });
        if (bol) o.areaStyle = { origin: 'start', color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: PM.rgba(col, dk ? 0.14 : 0.08) }, { offset: 1, color: PM.rgba(col, 0) }]) };
        return o;
      });
      return {
        grid: PM.grid({ top: 28, bottom: 2, right: der }),
        xAxis: ejeAnios(r[0], r[1], el),
        yAxis: ejeValor(vals, chico),
        tooltip: PM.tooltip(function (ps) {
          var p = ps.filter(function (q) { return q.value && q.value[1] != null; });
          if (!p.length) return '';
          var a = p[0].value[0], filas = vs.map(function (iso) { return [iso, valor(iso, a)]; });
          var con = filas.filter(function (f) { return f[1] != null; }).sort(function (x, y) { return y[1] - x[1]; });
          var sin = filas.filter(function (f) { return f[1] == null; });
          var h = PM.ttTitulo(String(a));
          con.forEach(function (f) { h += PM.ttFila(clave(color(f[0])), PAIS[f[0]].n, fmt(f[1]), 'linea'); });
          // en inglés los nombres de la fuente traen coma («Korea, Rep.»): la lista se separa con punto y coma
          if (sin.length) h += PM.ttPie(T('Sin dato ese año: ' + sin.map(function (f) { return PAIS[f[0]].n; }).join(', '), 'No data that year: ' + sin.map(function (f) { return PAIS[f[0]].n; }).join('; ')));
          return h;
        }),
        series: series
      };
    }
'''

# EFW: valores alineados a D.anios
DATOS_EFW = r'''var A = D.anios;
    PAISES.forEach(function (p) { p.idx = {}; A.forEach(function (a, i) { if (p.v[i] != null) p.idx[a] = p.v[i]; }); });
    var valor = function (iso, a) { var v = PAIS[iso].idx[a]; return v == null ? null : v; };
    var fmt = function (v) { return PM.num(v, 2); };
    var rango = function () { return [A[0], A[A.length - 1]]; };
    // los años con dato de algún país visible (el cursor salta de dato en dato)
    function anios(vs) { return A.filter(function (a) { return vs.some(function (iso) { return PAIS[iso].idx[a] != null; }); }); }
    // eje en enteros (de 1 en 1, o de 2 en 2 si el rango es amplio), dentro de 0 a 10
    function ejeValor(vals, chico) {
      var lo = vals.length ? Math.floor(Math.min.apply(null, vals)) : 0, hi = vals.length ? Math.ceil(Math.max.apply(null, vals)) : 10;
      var paso = hi - lo > 6 ? 2 : 1;
      lo = Math.max(0, Math.floor(lo / paso) * paso); hi = Math.min(10, Math.max(lo + paso, Math.ceil(hi / paso) * paso));
      return PM.ejeY({ unidad: chico ? T('Índice EFW', 'EFW index') : T('Índice EFW (0 a 10)', 'EFW index (0 to 10)'), fmt: PM.tick,
        extra: { min: lo, max: hi, interval: paso, nameTextStyle: { align: 'left' } } });
    }'''

# PIB: tramos de años seguidos [año inicial, valor, diferencia, …] → {año: valor}
DATOS_PIB = r'''PAISES.forEach(function (p) {
      p.idx = {};
      p.d.forEach(function (t) { for (var j = 1, v = 0; j < t.length; j++) { v = j === 1 ? t[1] : v + t[j]; p.idx[t[0] + j - 1] = v; } });
    });
    var valor = function (iso, a) { var v = PAIS[iso].idx[a]; return v == null ? null : v; };
    var fmt = function (v) { return '$' + PM.num(v, 0); };
    var rango = function () { return [+estado.periodo, D.ultimo]; };
    function anios(vs) {
      var r = rango(), X = {};
      vs.forEach(function (iso) { Object.keys(PAIS[iso].idx).forEach(function (a) { a = +a; if (a >= r[0] && a <= r[1]) X[a] = 1; }); });
      return Object.keys(X).map(Number).sort(function (a, b) { return a - b; });
    }
    // logarítmica: cortes en potencias de 10; la base en 1, 2 o 5 × 10ⁿ (sin rótulo si no es potencia) y el techo
    // en la potencia siguiente, así siempre quedan tres décadas rotuladas
    function ejeValor(vals, chico) {
      var lo = vals.length ? Math.min.apply(null, vals) : 500, hi = vals.length ? Math.max.apply(null, vals) : 50000;
      // en el teléfono, en miles: «100» en lugar de «$100.000» le devuelve al trazado el ancho del eje
      var dolar = chico ? function (v) { return PM.tick(v / 1000); } : function (v) { return '$' + PM.tick(v); };
      var unidad = chico ? T('PIB per cápita (miles de $)', 'GDP per capita ($ thousands)') : T('PIB per cápita ($ de 2011, PPA)', 'GDP per capita (2011 $, PPP)');
      if (estado.escala === 'log') {
        var e0 = Math.pow(10, Math.floor(Math.log10(lo))), e1 = Math.pow(10, Math.floor(Math.log10(hi)));
        var base = [5, 2, 1].map(function (k) { return k * e0; }).filter(function (b) { return b <= lo; })[0] || e0;
        var techo = hi <= e1 ? e1 : e1 * 10;
        var pot = function (v) { return Math.abs(Math.log10(v) - Math.round(Math.log10(v))) < 1e-9; };
        return PM.ejeY({ unidad: unidad, fmt: dolar, extra: { type: 'log', logBase: 10, min: base, max: techo,
          nameTextStyle: { align: 'left' }, axisLabel: { showMinLabel: pot(base), showMaxLabel: pot(techo) } } });
      }
      var paso = [2000, 5000, 10000, 20000, 25000, 50000].filter(function (p) { return Math.ceil(hi / p) <= (chico ? 5 : 6); })[0] || 50000;
      return PM.ejeY({ unidad: unidad, fmt: dolar, extra: { min: 0, max: Math.ceil(hi / paso) * paso, interval: paso, nameTextStyle: { align: 'left' } } });
    }'''


def lista_paises():
    """Las jurisdicciones del índice con su puesto y cuartil del último año."""
    n = len(valores(ULTIMO))
    out = {}
    for iso in panel[ULTIMO]:
        if iso not in meta or panel[ULTIMO][iso].get('s') is None:
            continue
        p, _ = puesto(ULTIMO, iso)
        out[iso] = {'i': iso, 'n': NOMBRE[iso], 'r': REGION[meta[iso]['region']], 's': panel[ULTIMO][iso]['s'],
                    'q': cuartil(p, n), 'p': p, 'al': alias(iso)}
    return out, n


def js_comp(datos_pais, paises):
    """El guion de una comparativa: la plantilla con los datos propios de la página y, para ?lang=en, las tablas EN
    (nombre de la fuente por ISO3) y EN_REGION de los países que lleva esa página, escritas acá desde data/."""
    return (JS_COMP.replace('@@DATOS_PAIS@@', datos_pais).replace('@@PANEL@@', JS_PANEL)
            .replace('@@EN@@', tabla_js({d['i']: nombre_en(d['i']) for d in paises}))
            .replace('@@EN_REGION@@', tabla_js(regiones_en(paises))))


def gen_comparativa_paises():
    anios = [int(y) for y in ANIOS]
    paises, n = lista_paises()
    for iso, d in paises.items():
        d['v'] = [panel[y].get(iso, {}).get('s') for y in ANIOS]
    s = lambda iso, a: panel[str(a)][iso]['s']
    # Divergencia: Chile y Bolivia casi empatados en 1975; Venezuela, el camino inverso hasta el último puesto
    verificar(abs(s('CHL', 1975) - s('BOL', 1975)) < 0.2 and s('CHL', ULTIMO) - s('BOL', ULTIMO) > 1,
              'en 1975 Chile y Bolivia puntuaban casi igual')
    p_ven, n_ven = puesto(ULTIMO, 'VEN')
    verificar(p_ven == n_ven and s('VEN', 1970) > 6, 'Venezuela recorrió el camino inverso hasta el último puesto')
    # Bolivia en la mitad superior del ranking: un solo tramo de años seguidos de la serie
    arriba = [y for y in ANIOS if puesto(y, 'BOL')[0] <= puesto(y, 'BOL')[1] / 2]
    pos = [ANIOS.index(y) for y in arriba]
    verificar(arriba and pos == list(range(pos[0], pos[0] + len(pos))), 'Bolivia estuvo en la mitad superior en un solo tramo')
    p00, n00 = puesto('2000', 'BOL')
    p_bol, _ = puesto(ULTIMO, 'BOL')
    tam = [sum(1 for d in paises.values() if d['q'] == q) for q in (1, 2, 3, 4)]
    n70 = len(valores(ANIOS[0]))
    a_tot = min(int(y) for y in ANIOS if len(valores(y)) == n)
    # La serie es quinquenal hasta un año y anual desde entonces (1970, 1975 … 1995, 2000, 2001 …): el año sale del
    # dato y la frase es UNA, la misma en el panel y en la pregunta
    pasos = [b - a for a, b in zip(anios, anios[1:])]
    k_anual = pasos.index(1)
    verificar(k_anual > 0 and all(d == 5 for d in pasos[:k_anual]) and all(d == 1 for d in pasos[k_anual:]),
              'la serie es quinquenal hasta un año y anual desde entonces')
    a_anual = anios[k_anual]
    serie_es = f'Hasta {a_anual} la serie es quinquenal y desde entonces, anual'
    serie_en = f'Until {a_anual} the series is five-yearly and from then on, annual'

    # Cada texto con su pareja en inglés: T('castellano', 'inglés'); las cifras del inglés, con num_en()
    p = [
        [T('Cómo usar', 'How to use'),
         T('Busque un país y agréguelo: hasta seis a la vez, con Bolivia fija. Pulse una pastilla para ocultar o '
           f'mostrar ese país y la × para quitarlo. La insignia es el puntaje EFW {ULTIMO} y su color, el cuartil: turquesa '
           'el más libre, después menta, oro y rojo.',
           'Search for a country and add it: up to six at a time, with Bolivia fixed. Press a pill to hide or show that '
           f'country and the × to remove it. The badge is the {ULTIMO} EFW score and its color, the quartile: turquoise '
           'for the freest, then mint, gold and red.')],
        [T('Divergencia histórica', 'Historical divergence'),
         T(f'En 1975 <strong>Chile</strong> ({num(s("CHL", 1975))}) y <strong>Bolivia</strong> '
           f'({num(s("BOL", 1975))}) puntuaban casi igual; en {ULTIMO} Chile marca {num(s("CHL", ULTIMO))} y Bolivia '
           f'{num(s("BOL", ULTIMO))}. <strong>Venezuela</strong> recorrió el camino inverso: de {num(s("VEN", 1970))} en 1970 a '
           f'{num(s("VEN", ULTIMO))} en {ULTIMO}, el último puesto de {n_ven}. Compare también Argentina y Singapur.',
           f'In 1975 <strong>Chile</strong> ({num_en(s("CHL", 1975))}) and <strong>Bolivia</strong> '
           f'({num_en(s("BOL", 1975))}) scored almost the same; in {ULTIMO} Chile scores {num_en(s("CHL", ULTIMO))} and Bolivia '
           f'{num_en(s("BOL", ULTIMO))}. <strong>Venezuela</strong> went the opposite way: from {num_en(s("VEN", 1970))} in 1970 to '
           f'{num_en(s("VEN", ULTIMO))} in {ULTIMO}, ranked last of {n_ven}. Compare Argentina and Singapore as well.')],
        [T('Bolivia en contexto', 'Bolivia in context'),
         T(f'Bolivia estuvo en la <strong>mitad superior</strong> del ranking entre {arriba[0]} y '
           f'{arriba[-1]}, tras las reformas de 1985 (puesto {p00} de {n00} en 2000); después volvió a la mitad inferior: '
           f'puesto <strong>{p_bol} de {n}</strong> en {ULTIMO}.',
           f'Bolivia was in the <strong>top half</strong> of the ranking between {arriba[0]} and '
           f'{arriba[-1]}, after the 1985 reforms (rank {p00} of {n00} in 2000); it then returned to the bottom half: '
           f'rank <strong>{p_bol} of {n}</strong> in {ULTIMO}.')],
        ['ctx',
         T(f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. El cuartil es el '
           f'de {ULTIMO}, por puesto (con el puntaje a dos decimales, los empates comparten puesto). {serie_es}; '
           'cada serie empieza cuando el país entra en el índice.',
           f'<strong>Source:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. The quartile is '
           f'that of {ULTIMO}, by rank (with the score at two decimals, ties share a rank). {serie_en}; '
           'each series begins when the country enters the index.')],
    ]
    preguntas = [
        efw_que(n),
        [T('¿Qué es el cuartil?', 'What is the quartile?'),
         T(f'Las {n} jurisdicciones de {ULTIMO}, ordenadas de más a menos libre y repartidas en cuatro '
           f'grupos: el cuartil 1 reúne a las {tam[0]} más libres y el 4, a las {tam[3]} menos libres. Lo indica el color de la '
           'insignia: turquesa, menta, oro y rojo, la misma escala del mapa.',
           f'The {n} jurisdictions of {ULTIMO}, ordered from freest to least free and divided into four '
           f'groups: quartile 1 comprises the {tam[0]} freest and quartile 4, the {tam[3]} least free. It is shown by the color '
           'of the badge: turquoise, mint, gold and red, the same scale as the map.')],
        [T('¿Por qué algunas series empiezan tarde?', 'Why do some series start late?'),
         T(f'El índice calificaba a {n70} países en 1970 y llegó a {n} en {a_tot}: '
           f'cada país entra cuando hay datos suficientes para calificarlo. {serie_es}.',
           f'The index rated {n70} countries in 1970 and reached {n} in {a_tot}: '
           f'each country enters when there are enough data to rate it. {serie_en}.')],
    ]
    lista = sorted(paises.values(), key=lambda d: d['i'])
    datos = {
        'anios': anios, 'fecha': f'{anios[0]}–{anios[-1]}', 'anioQ': ULTIMO, 'inicial': ['BOL', 'CHL', 'ARG', 'VEN', 'SGP'],
        'colores': COLORES_PAIS, 'qc': QC,
        'paises': lista, 'panel': p, 'preguntas': preguntas,
    }
    pagina('comparativa_paises.html',
           T('Comparativa Internacional de Libertad Económica', 'International Economic Freedom Comparison'),
           T(f'Índice EFW por país, {anios[0]}–{anios[-1]} · {n} jurisdicciones · de 0 a 10, más es más libre',
             f'EFW index by country, {anios[0]}–{anios[-1]} · {n} jurisdictions · from 0 to 10, higher is freer'),
           ACENTO['paises'], CUERPO_COMP.replace('@@CONTROLES@@', ''), datos, js_comp(DATOS_EFW, lista), estilo=ESTILO_COMP)


def gen_comparativa_pib():
    efw, _ = lista_paises()

    def tramos(serie):
        """{año: valor} → [[año inicial, primer valor, diferencia, diferencia, …], …] por años seguidos: las
        diferencias año a año son más cortas que los valores (la página pesa una cuarta parte menos)."""
        out, cur = [], None
        for a in sorted(int(y) for y in serie):
            x = round(serie[str(a)])
            if cur and a == cur[0] + len(cur) - 1:
                cur.append(x)
            else:
                cur = [a, x]
                out.append(cur)
        return [t[:2] + [t[j] - t[j - 1] for j in range(2, len(t))] for t in out]

    paises = []
    for iso, serie in gdp.items():
        serie = {a: x for a, x in serie.items() if x}
        if not serie:
            continue
        d = dict(efw[iso]) if iso in efw else {'i': iso, 'n': NOMBRE[iso], 'r': REGION_EXTRA[iso], 'al': alias(iso)}
        d['d'] = tramos(serie)
        paises.append(d)
    g = lambda iso, a: gdp[iso].get(str(a))
    a0 = min(int(a) for x in gdp.values() for a in x)
    ultimo = max(int(a) for x in gdp.values() for a in x)
    # 1950 frente a hoy: Bolivia triplicaba a Corea; hoy Corea multiplica a Bolivia
    r50, rhoy = g('BOL', 1950) / g('KOR', 1950), g('KOR', ultimo) / g('BOL', ultimo)
    verificar(2.5 < r50 < 3.5 and rhoy > 5, 'en 1950 Bolivia triplicaba el PIB per cápita de Corea del Sur')
    a_bol = min(int(a) for a in gdp['BOL'])
    a_bol2 = min(int(a) for a in gdp['BOL'] if int(a) > a_bol)
    # Cuánto se multiplicó el ingreso de cada uno: cada lapso va explícito en la frase (primer año con dato de ese
    # país y último de la base), porque no son el mismo y sin los años no se pueden comparar
    a_kor = min(int(a) for a, x in gdp['KOR'].items() if x)
    verificar(g('BOL', a_bol) and g('BOL', ultimo) and g('KOR', ultimo), 'Bolivia y Corea del Sur tienen dato en los extremos de su lapso')
    verificar(g('VEN', 1950) > g('CHL', 1950) and g('VEN', ultimo) < g('BOL', ultimo) < g('CHL', ultimo),
              'Venezuela era más rica que Chile en 1950 y hoy está por debajo de Bolivia')
    asia, latam = ['KOR', 'SGP', 'HKG', 'JPN'], ['ARG', 'CHL', 'VEN', 'URY', 'MEX']
    verificar(max(g(i, 1950) for i in asia) < g('ARG', 1950) and
              min(g(i, ultimo) for i in asia) > max(g(i, ultimo) for i in latam),
              'el milagro asiático partió por debajo de la América Latina rica y hoy la supera')

    def extremos(a):
        v = [(x[str(a)], iso) for iso, x in gdp.items() if x.get(str(a))]
        return min(v), max(v), len(v)

    lo0, hi0, n0 = extremos(a0)
    lo1, hi1, n1 = extremos(ultimo)
    # Cada texto con su pareja en inglés: T('castellano', 'inglés'). Las cifras del inglés, con num_en() y usd_en(); los
    # países que salen del dato (el más rico y el más pobre), con nombre_en(); los que nombra la frase, a mano en los dos.
    p = [
        [T('Cómo usar', 'How to use'),
         T(f'Busque un país ({len(paises)} disponibles) y agréguelo: hasta seis a la vez, con Bolivia fija. La '
           f'insignia es el puntaje de libertad económica {ULTIMO} y su color, el cuartil; los países sin dato del índice no la '
           'llevan. En escala logarítmica, el mismo ritmo de crecimiento se ve con la misma pendiente.',
           f'Search for a country ({len(paises)} available) and add it: up to six at a time, with Bolivia fixed. The '
           f'badge is the {ULTIMO} economic freedom score and its color, the quartile; countries with no index data do not '
           'have one. On a log scale, the same growth rate shows up as the same slope.')],
        [T('Dos siglos de divergencia', 'Two centuries of divergence'),
         T(f'En {a0} el país más rico de la base ({NOMBRE[hi0[1]]}, {usd(hi0[0])}) tenía un ingreso '
           f'{num(hi0[0] / lo0[0], 1)} veces el del más pobre ({NOMBRE[lo0[1]]}, {usd(lo0[0])}); en {ultimo}, la distancia entre '
           f'{pais_es(hi1[1], True)} y {pais_es(lo1[1], True)} es de {num(hi1[0] / lo1[0], 0)} veces. <strong>Venezuela</strong> era más rica que '
           f'Chile en 1950 ({usd(g("VEN", 1950))} frente a {usd(g("CHL", 1950))}); en {ultimo} está por debajo de Bolivia.',
           f'In {a0} the richest country in the database ({nombre_en(hi0[1])}, {usd_en(hi0[0])}) had an income '
           f'{num_en(hi0[0] / lo0[0], 1)} times that of the poorest ({nombre_en(lo0[1])}, {usd_en(lo0[0])}); in {ultimo}, the gap between '
           f'{nombre_en(hi1[1], True)} and {nombre_en(lo1[1], True)} is {num_en(hi1[0] / lo1[0], 0)}-fold. <strong>Venezuela</strong> was '
           f'richer than Chile in 1950 ({usd_en(g("VEN", 1950))} versus {usd_en(g("CHL", 1950))}); in {ultimo} it is below Bolivia.')],
        ['Bolivia',
         T(f'Bolivia tiene datos desde {a_bol} ({usd(g("BOL", a_bol))}). En 1950 su PIB per cápita '
           f'<strong>triplicaba</strong> al de Corea del Sur ({usd(g("BOL", 1950))} frente a {usd(g("KOR", 1950))}); en {ultimo} el '
           f'coreano es <strong>{num(rhoy, 1)} veces</strong> el boliviano ({usd(g("KOR", ultimo))} frente a '
           f'{usd(g("BOL", ultimo))}). Entre {a_bol} y {ultimo} ({ultimo - a_bol} años) el ingreso boliviano se multiplicó por '
           f'{num(g("BOL", ultimo) / g("BOL", a_bol), 1)}; el coreano, entre {a_kor} y {ultimo} ({ultimo - a_kor} años), por '
           f'{num(g("KOR", ultimo) / g("KOR", a_kor), 0)}.',
           f'Bolivia has data since {a_bol} ({usd_en(g("BOL", a_bol))}). In 1950 its GDP per capita was '
           f'<strong>three times</strong> that of South Korea ({usd_en(g("BOL", 1950))} versus {usd_en(g("KOR", 1950))}); in {ultimo} '
           f"Korea's is <strong>{num_en(rhoy, 1)} times</strong> Bolivia's ({usd_en(g('KOR', ultimo))} versus "
           f'{usd_en(g("BOL", ultimo))}). Between {a_bol} and {ultimo} ({ultimo - a_bol} years) Bolivian income multiplied by '
           f'{num_en(g("BOL", ultimo) / g("BOL", a_bol), 1)}; Korean income, between {a_kor} and {ultimo} ({ultimo - a_kor} years), by '
           f'{num_en(g("KOR", ultimo) / g("KOR", a_kor), 0)}.')],
        [T('El milagro asiático', 'The Asian miracle'),
         T('Corea del Sur, Singapur, Hong Kong y Japón partieron en 1950 de niveles parecidos o inferiores '
           f'a los de América Latina: el más alto de los cuatro ({usd(max(g(i, 1950) for i in asia))}) no llegaba al de Argentina '
           f'({usd(g("ARG", 1950))}). Con apertura comercial, moneda sana y Estado de derecho lograron uno de los crecimientos más '
           'rápidos de la historia; en escala logarítmica se ve la aceleración.',
           'South Korea, Singapore, Hong Kong and Japan started out in 1950 from levels similar to or below '
           f'those of Latin America: the highest of the four ({usd_en(max(g(i, 1950) for i in asia))}) fell short of '
           f"Argentina's ({usd_en(g('ARG', 1950))}). With trade openness, sound money and the rule of law they achieved one of "
           'the fastest growth episodes in history; on a log scale the acceleration is visible.')],
        ['ctx',
         T('<strong>Fuente:</strong> Maddison Project Database 2023 (Bolt y van Zanden, 2024). PIB per cápita en dólares '
           f'internacionales de 2011 (PPA). Antes de 1950 las cifras son reconstrucciones históricas, con años sueltos y más '
           f'incertidumbre: la base tiene {n0} países en {a0} y {n1} en {ultimo}.',
           '<strong>Source:</strong> Maddison Project Database 2023 (Bolt and van Zanden, 2024). GDP per capita in 2011 '
           'international dollars (PPP). Before 1950 the figures are historical reconstructions, with scattered years and more '
           f'uncertainty: the database has {n0} countries in {a0} and {n1} in {ultimo}.')],
    ]
    preguntas = [
        [T('¿Qué son los dólares de 2011 (PPA)?', 'What are 2011 dollars (PPP)?'),
         T('La producción por habitante medida a precios internacionales de 2011, con '
           'paridad de poder adquisitivo: un dólar compra lo mismo en todos los países y años, así que las cifras se comparan '
           'entre sí y en el tiempo. La base es el Maddison Project Database 2023, de la Universidad de Groningen.',
           'Output per person measured at 2011 international prices, with purchasing power parity: a dollar buys the same '
           'in every country and year, so the figures can be compared with one another and over time. The database is the '
           'Maddison Project Database 2023, from the University of Groningen.')],
        [T('¿Por qué la escala logarítmica?', 'Why the log scale?'),
         T('En escala logarítmica la misma distancia vertical es el mismo porcentaje: pasar '
           'de $1.000 a $2.000 ocupa lo mismo que de $20.000 a $40.000. Así se comparan ritmos de crecimiento entre países '
           'ricos y pobres; la escala natural muestra mejor las diferencias absolutas de hoy.',
           'On a log scale the same vertical distance is the same percentage: going from $1,000 to $2,000 takes up as '
           'much space as going from $20,000 to $40,000. That is how growth rates are compared between rich and poor '
           "countries; the linear scale shows today's absolute differences better.")],
        [T('¿Qué tan confiables son los datos antiguos?', 'How reliable are the old data?'),
         T(f'Antes de 1950 las cifras son reconstrucciones históricas: muchos '
           f'países tienen años sueltos (Bolivia empieza en {a_bol} y salta a {a_bol2}) y el margen de error es mayor. Desde '
           '1950 la serie es anual para casi todos.',
           'Before 1950 the figures are historical reconstructions: many countries have scattered years (Bolivia starts '
           f'in {a_bol} and jumps to {a_bol2}) and the margin of error is larger. From 1950 the series is annual for almost '
           'all of them.')],
    ]
    controles = (
        '\n      <div class="hz-item"><span class="hz-lbl" data-en="Scale">Escala</span><div class="hz-grp" id="b-escala"></div></div>'
        '\n      <div class="hz-item"><span class="hz-lbl" data-en="Period">Período</span><div class="hz-grp" id="b-periodo"></div></div>')
    periodos = [[str(a0), T(f'Desde {a0}', f'Since {a0}')], ['1950', T('Desde 1950', 'Since 1950')]]
    lista = sorted(paises, key=lambda d: d['i'])
    datos = {
        'ultimo': ultimo, 'fecha': f'{a0}–{ultimo}', 'anioQ': ULTIMO, 'inicial': ['BOL', 'KOR', 'CHL', 'ARG', 'VEN'],
        'colores': COLORES_PAIS, 'qc': QC, 'periodos': periodos,
        'controles': [{'id': 'b-escala', 'k': 'escala', 'ops': [['log', T('Logarítmica', 'Log')], ['nat', T('Natural', 'Linear')]]},
                      {'id': 'b-periodo', 'k': 'periodo', 'ops': periodos}],
        'paises': lista, 'panel': p, 'preguntas': preguntas,
    }
    pagina('comparativa_pib.html',
           T('Evolución del PIB per Cápita', 'Evolution of GDP per Capita'),
           T(f'PIB per cápita en dólares internacionales de 2011 (PPA), {a0}–{ultimo} · Maddison Project Database 2023',
             f'GDP per capita in 2011 international dollars (PPP), {a0}–{ultimo} · Maddison Project Database 2023'),
           ACENTO['pib'], CUERPO_COMP.replace('@@CONTROLES@@', controles), datos, js_comp(DATOS_PIB, lista),
           fuente=MADDISON, estilo=ESTILO_COMP)


if __name__ == '__main__':
    print('Generando los 5 gráficos complementarios (molde de monitores)…')
    gen_areas_regiones()
    gen_evolucion_mundial()
    gen_bolivia_efw()
    gen_comparativa_paises()
    gen_comparativa_pib()
    print('Listo.')
