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

    python generate_charts.py
"""
import json
import math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
OUT = RAIZ / 'embed'


def cargar(nombre):
    return json.loads((RAIZ / 'data' / nombre).read_text(encoding='utf-8'))


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
AREAS = [
    {'k': 'a1', 'nombre': 'Tamaño del gobierno', 'corto': 'Tamaño del gobierno'},
    {'k': 'a2', 'nombre': 'Sistema legal y derechos de propiedad', 'corto': 'Sistema legal'},
    {'k': 'a3', 'nombre': 'Moneda sana', 'corto': 'Moneda sana'},
    {'k': 'a4', 'nombre': 'Libertad para comerciar internacionalmente', 'corto': 'Comercio internacional'},
    {'k': 'a5', 'nombre': 'Regulación', 'corto': 'Regulación'},
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

FRASER = ('Fuente: <a href="https://www.fraserinstitute.org/economic-freedom" target="_blank" rel="noopener">Fraser Institute</a>, '
          f'Economic Freedom of the World: {INFORME} Annual Report · Elaboración: '
          '<a href="https://populi.org.bo" target="_blank" rel="noopener">Centro de Estudios POPULI</a>')
MADDISON = ('Fuente: <a href="https://www.rug.nl/ggdc/historicaldevelopment/maddison/" target="_blank" rel="noopener">Maddison Project Database 2023</a> '
            f'(Bolt y van Zanden, 2024); cuartil: Fraser Institute, EFW {INFORME} · Elaboración: '
            '<a href="https://populi.org.bo" target="_blank" rel="noopener">Centro de Estudios POPULI</a>')
EFW_QUE = ('El índice <strong>Economic Freedom of the World</strong> (EFW) del Fraser Institute califica de 0 a 10 a {n} '
           'jurisdicciones con 45 componentes agrupados en cinco áreas: tamaño del gobierno, sistema legal y derechos de '
           'propiedad, moneda sana, libertad para comerciar internacionalmente y regulación. Más puntaje es más libertad.')


# ── Utilidades ─────────────────────────────────────────────────────────────────────────────────
def num(x, dec=2):
    """Cifra es-BO para los textos: «6,05» · «41.321» · «−0,20» (menos tipográfico, sin «−0,00»).
    Redondea como PM.num en la página (mitad hacia afuera sobre el decimal más corto, la regla de Intl) y
    sobre el mismo valor que viaja en los datos (fino): el texto y la cifra del gráfico nunca difieren."""
    d = Decimal(repr(fino(x))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    s = f'{abs(d):,.{dec}f}'.translate(str.maketrans(',.', '.,'))
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


def js(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':'))


ORDINAL = {1: 'primera', 2: 'segunda', 3: 'tercera', 4: 'cuarta', 5: 'quinta', 6: 'sexta', 7: 'séptima'}
CARDINAL = {2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
# El acento va de fondo del botón activo: sostiene texto blanco (menta → turquesa, oro → su paso oscuro)
ACENTO = {'areas': '#005F73', 'evolucion': '#9B2226', 'bolivia': '#C71E1D', 'paises': '#0A9396', 'pib': '#A86E00'}


# ── Piezas comunes de las páginas ──────────────────────────────────────────────────────────────
CABEZA = r'''<!DOCTYPE html>
<html lang="es" data-theme="light" style="--acento:@@ACENTO@@">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>@@TITULO@@ · Populi</title>
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
      <h2 class="sec-title"><span class="accent-bar"></span>@@TITULO@@</h2>
      <p class="sec-sub">@@BAJADA@@</p>
    </div>
'''

PIE = r'''
    <div class="edu-grid" id="preguntas"></div>
    <div class="source"><span class="source-txt" id="fuente">@@FUENTE@@</span></div>
  </div>

  <script>
  (function () {
    var C = PM.C, D = @@DATOS@@;
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
    html = CABEZA + cuerpo + PIE
    for k, v in {'@@JS@@': js_pagina, '@@COMUN@@': comun, '@@ACENTO@@': acento, '@@TITULO@@': titulo,
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
          <span class="ref"><span class="raya"></span>Índice general</span>
        </div>
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span>Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t">Lectura del gráfico</span><span class="panel-hd-d" id="panel-fecha"></span></div>
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
        .concat([{ name: 'Índice general', color: PM.col(C.tinta), forma: 'area' }]);
    };
    PM.tablaDatos = function () {
      return { cols: ['Región', 'Países', 'Índice general'].concat(AREAS.map(function (a) { return a.nombre; })),
        filas: FILAS.map(function (f) { return [f.nombre, f.n, f.s].concat(f.a); }) };
    };

    function cifras() {
      var b = FILAS[0], w = FILAS[FILAS.length - 1], l = FILAS[D.lac];
      document.getElementById('kpis').innerHTML =
        PM.kpi({ color: C.turquesa, rotulo: 'Región más libre', valor: PM.num(b.s, 2), delta: b.nombre, serie: b.serie }) +
        PM.kpi({ color: C.rojo, rotulo: 'Región menos libre', valor: PM.num(w.s, 2), delta: w.nombre, serie: w.serie }) +
        PM.kpi({ color: C.oro, rotulo: 'América Latina y el Caribe', valor: PM.num(l.s, 2), delta: 'puesto ' + (D.lac + 1) + ' de ' + FILAS.length, serie: l.serie }) +
        PM.kpi({ color: C.petroleo, rotulo: 'Mayor brecha entre regiones', valor: PM.num(D.brecha.v, 2), delta: D.brecha.area });
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
        { name: 'Índice general', type: 'scatter', z: 2, symbol: 'rect', symbolSize: [3, chico ? 17 : 21],
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
          var f = FILAS[p.dataIndex], h = PM.ttTitulo(f.nombre, f.n + (f.n === 1 ? ' país' : ' países') + ' · ' + D.anio);
          act.forEach(function (a) { h += PM.ttFila(clave(a.color), a.nombre, PM.num(f.a[a.i], 2), 'area'); });
          return h + PM.ttTotal('Índice general', PM.num(f.s, 2));
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
        filas.append({
            'k': reg_en, 'nombre': reg_es, 'n': len(isos), 's': fino(media([panel[anio][i]['s'] for i in isos])),
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

    p = [
        ['Qué muestra', 'Cada fila es una región; cada punto, el promedio de sus países en una de las cinco áreas del '
         'índice (0 a 10: más es más libre), y la raya vertical, el índice general. Las filas van de la región más libre '
         'a la menos libre; la línea gris une su peor y su mejor área.'],
        ['Patrones clave', f'<strong>{filas[0]["nombre"]}</strong> ({num(filas[0]["s"])}) y <strong>{filas[1]["nombre"]}</strong> '
         f'({num(filas[1]["s"])}) encabezan; <strong>{filas[-2]["nombre"]}</strong> ({num(filas[-2]["s"])}) y '
         f'<strong>{filas[-1]["nombre"]}</strong> ({num(filas[-1]["s"])}) cierran. La mayor brecha entre regiones está en '
         f'<strong>{nom(ancha[3])}</strong> (de {num(ancha[1])} a {num(ancha[2])}) y la menor, en <strong>{nom(angosta[3])}</strong> '
         f'(de {num(angosta[1])} a {num(angosta[2])}), donde además el orden se invierte: {a1[0]["nombre"]} '
         f'({num(a1[0]["a"][0])}) y {a1[1]["nombre"]} ({num(a1[1]["a"][0])}) superan a {eca["nombre"]} ({num(eca["a"][0])}), '
         'porque esa área premia el gasto, las transferencias y los impuestos bajos.'],
        ['América Latina y el Caribe', f'Con <strong>{num(lac["s"])}</strong>, la región es la {ORDINAL[ilac + 1]} de '
         f'{CARDINAL[len(filas)]}. Su área más débil es <strong>{nom(lac_orden[0])}</strong> ({num(lac["a"][lac_orden[0]])}), '
         f'seguida de <strong>{nom(lac_orden[1])}</strong> ({num(lac["a"][lac_orden[1]])}); la mejor, '
         f'<strong>{nom(lac_orden[-1])}</strong> ({num(lac["a"][lac_orden[-1]])}).'],
        ['ctx', f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report (datos de {anio}): '
         f'{n_total} jurisdicciones, 5 áreas y 45 componentes. Promedio simple de los países de cada región (regiones del '
         f'Banco Mundial); {na["nombre"]} son solo {na_paises[0]} y {na_paises[1]}.'],
    ]
    preguntas = [
        ['¿Qué mide el índice de libertad económica?', EFW_QUE.format(n=n_total)],
        ['¿Por qué una región pobre puede puntuar alto en Tamaño del gobierno?',
         'Porque el área mide cuánto del ingreso pasa por el Estado: consumo e inversión pública, transferencias y '
         'subsidios, empresas estatales e impuestos marginales. Un Estado chico puntúa alto aunque el país sea pobre, y los '
         f'Estados de bienestar puntúan bajo: {eca["nombre"]} marca {num(eca["a"][0])} en esa área y {num(eca["a"][2])} en '
         'Moneda sana.'],
        ['¿Por qué promedios simples?',
         'Cada país pesa lo mismo: el promedio describe las políticas de los países de la región, no la experiencia de su '
         'población (en Asia del Sur, India no pesa más que Bután).'],
    ]
    datos = {
        'anio': anio, 'lac': ilac,
        'areas': [{'k': a['k'], 'i': j, 'nombre': a['nombre'], 'corto': a['corto'], 'color': a['color']} for j, a in enumerate(AREAS)],
        'regiones': [{'nombre': f['nombre'], 'n': f['n'], 's': f['s'], 'a': f['a'], 'serie': f['serie']} for f in filas],
        'brecha': {'v': fino(ancha[0]), 'area': AREAS[ancha[3]]['corto']},
        'panel': p, 'preguntas': preguntas,
    }
    pagina('areas_regiones.html', 'Calificación por Áreas del Índice de Libertad Económica',
           f'Promedio de cada región en las cinco áreas del índice, {anio} · de 0 a 10, más es más libre · {n_total} jurisdicciones',
           ACENTO['areas'], CUERPO_AREAS, datos, JS_AREAS.replace('@@PANEL@@', JS_PANEL), estilo=ESTILO_AREAS)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# 2 y 3. SERIES DE TIEMPO — evolución mundial y Bolivia (una plantilla: vista Índice / Áreas)
# ════════════════════════════════════════════════════════════════════════════════════════════════
CUERPO_SERIE = r'''
    <div class="hz-bar">
      <div class="hz-item"><span class="hz-lbl">Vista</span><div class="hz-grp" id="b-vista"></div></div>
    </div>

    <div class="kpi-grid" id="kpis"></div>

    <div class="main-grid">
      <div class="chart-card">
        <div class="chart-ctrl">
          <div class="tog-grp" id="pastillas-indice"></div>
          <div class="tog-grp" id="pastillas-areas" style="display:none"></div>
        </div>
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span>Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t">Lectura del gráfico</span><span class="panel-hd-d" id="panel-fecha"></span></div>
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
    PM.botonera(document.getElementById('b-vista'), [['indice', 'Índice'], ['areas', 'Áreas']], estado.vista, function (v) {
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
      return { cols: ['Año'].concat(vs.map(function (s) { return s.nombre; })),
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
    verificar(grandes[0] in bajo, 'el país más poblado puntúa por debajo del promedio simple')
    qp = [x for x in pond if x is not None]
    a_pico_p = [a for a, x in zip(anios, pond) if x is not None][qp.index(max(qp))]
    verificar(a_pico_p == a_pico and pond[-1] < pond[anios.index(2020)] < pond[anios.index(2019)],
              'el ponderado siguió el mismo camino: máximo en el mismo año y caída con el COVID-19')
    nom = lambda i: NOMBRE.get(i, meta.get(i, {}).get('name', i))
    lista = lambda xs: ', '.join(xs[:-1]) + ' y ' + xs[-1] if len(xs) > 1 else xs[0]

    p = [
        ['Tendencia general', f'El promedio cayó en los <strong>años 70</strong> (de {num(v(mundo, 1970))} en 1970 a '
         f'{num(v(mundo, 1975))} en 1975), con más gasto público e inflación. Las reformas de los 80 y 90 —Reagan, Thatcher, '
         f'la apertura asiática y la caída del socialismo— lo llevaron de {num(v(mundo, 1980))} en 1980 a {num(v(mundo, 2000))} '
         f'en 2000. El máximo llegó en <strong>{a_pico}</strong> ({num(pico)}).'],
        ['Siglo XXI', f'La liberalización siguió a ritmo moderado hasta {a_pico}. El <strong>COVID-19</strong> provocó la mayor '
         f'caída anual de la serie (de {num(v(mundo, 2019))} a {num(v(mundo, 2020))}), con más gasto, regulación y trabas al '
         f'comercio: el promedio volvió al nivel de {nivel}. Después, la inflación de 2021–2022 hundió a Moneda sana (de '
         f'{num(m3[2019])} en 2019 a {num(m3[a_m3])} en {a_m3}) y el promedio tocó fondo en {a_fondo} ({num(post[a_fondo])}). '
         f'<strong>Desde entonces se recupera</strong>: en {a_ult} marca {num(ultimo)}, por encima de 2020 pero todavía '
         f'{num(pico - ultimo)} por debajo del máximo de {a_pico}.'],
        ['Ponderado por población', f'Si cada país pesa según su población, el promedio es menor: <strong>{num(pond[-1])}</strong> '
         f'en {a_ult}, frente a {num(ultimo)} del promedio simple. Lo empuja hacia abajo <strong>{nom(grandes[0])}</strong>, el país '
         f'más poblado, con {num(panel[ULTIMO][grandes[0]]["s"])}, junto con {lista([nom(i) for i in bajo[1:]])}, también entre los '
         f'ocho más poblados y por debajo del promedio. Siguió el mismo camino: máximo en {a_pico_p} ({num(max(qp))}) y caída con '
         f'el COVID-19.'],
        ['Áreas', f'<strong>{AREAS[mejora]["nombre"]}</strong> es el área que más mejoró desde 1980 (de {num(v(area[ka], 1980))} '
         f'a {num(v(area[ka], a_ult))}); <strong>{AREAS[quieta]["nombre"]}</strong>, la que menos cambió (entre '
         f'{num(min(area[kq]))} y {num(max(area[kq]))} en toda la serie). La vista <strong>Áreas</strong> las muestra una por una.'],
        ['ctx', f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. Promedio simple '
         f'de las jurisdicciones con dato cada año: {n[0]} en 1970, {v(n, 1995)} en 1995, {v(n, 2000)} en 2000 y {n[-1]} desde '
         f'{a_tot}; la línea de los mismos {len(fijos)} países descuenta la entrada de países nuevos. El ponderado usa la '
         f'población del Maddison Project Database 2023 (la de 2022 para {a_ult}); quedan fuera {len(sin_pob)} jurisdicciones '
         f'sin ese dato, que suman menos del {max(1, round(peso_sin * 100 + 0.5))} % de la población. Cada área promedia los '
         f'países con dato en esa área. Hasta 2000 los datos son quinquenales.'],
    ]
    preguntas = [
        ['¿Qué mide el índice de libertad económica?', EFW_QUE.format(n=n[-1])],
        ['¿Por qué hay tres líneas?',
         f'El índice calificaba a {n[0]} países en 1970 y hoy a {n[-1]}. De los {len(nuevos)} que entraron después, {n_soc} son '
         f'de la antigua órbita socialista y {n_afr} de África Subsahariana, y en promedio puntúan más bajo: su entrada empuja '
         f'el promedio hacia abajo aunque ningún país empeore. La línea de los <strong>mismos {len(fijos)} países</strong> '
         f'calificados desde 1970 sigue siempre al mismo grupo: marca {num(fijo[-1])} en {a_ult}, frente a {num(ultimo)} del '
         f'promedio de todos, y dibuja la misma historia. La punteada pondera por población: describe la libertad económica '
         f'que vive la persona promedio, no el país promedio ({num(pond[-1])} en {a_ult}).'],
        ['¿Se recuperó después de 2020?',
         f'Sólo en parte. La inflación de 2021–2022 llevó a Moneda sana de {num(m3[2019])} en 2019 a {num(m3[a_m3])} en '
         f'{a_m3} y anuló la mejora de otras áreas (entre 2020 y {a_ult}, Libertad para comerciar internacionalmente subió '
         f'{num(rec["a4"])} puntos y Tamaño del gobierno, {num(rec["a1"])}). Con la inflación en baja, Moneda sana volvió a '
         f'{num(m3[a_ult])} en {a_ult}: sube {num(sube["a3"])} puntos desde {a_fondo}, y ninguna otra área subió más de '
         f'{num(otra)}. El promedio ({num(ultimo)}) ya supera al de 2020 ({num(v(mundo, 2020))}), pero no al de {a_pico} '
         f'({num(pico)}).'],
    ]
    datos = {
        'anios': anios, 'unidad': 'Índice EFW (0 a 10)', 'unidadCorta': 'Índice EFW',
        'indice': [
            {'k': 'mundo', 'nombre': 'Promedio mundial', 'color': GRANATE, 'ancho': 2.5, 'area': True,
             'v': [fino(x) for x in mundo]},
            {'k': 'fijo', 'nombre': f'Mismos {len(fijos)} países desde 1970', 'corto': f'Mismos {len(fijos)} países',
             'color': PIZARRA, 'ancho': 1.75, 'v': [fino(x) for x in fijo]},
            {'k': 'pond', 'nombre': 'Ponderado por población', 'color': '#EE9B00', 'ancho': 1.75, 'punteada': True,
             'v': [None if x is None else fino(x) for x in pond]},
        ],
        'areas': serie_areas(lambda k: area[k]),
        'total': {'nombre': 'Índice general', 'v': [fino(x) for x in mundo]},
        'pieTip': [f'{c} jurisdicciones con dato' for c in n],
        'hitos': [{'anio': 1989, 'largo': '1989 · cae el Muro de Berlín', 'corto': '1989', 'alinear': 'left'},
                  {'anio': 2020, 'largo': '2020 · COVID-19', 'corto': '2020', 'alinear': 'right'}],
        'cifras': [
            {'color': GRANATE, 'rotulo': f'Promedio mundial · {a_ult}', 'valor': fino(ultimo),
             'delta': f'▼ {num(pico - ultimo)} desde {a_pico}', 'tono': 'malo', 'serie': [fino(v(mundo, int(y))) for y in ANUALES]},
            {'color': '#0A9396', 'rotulo': 'Máximo de la serie', 'valor': fino(pico), 'delta': f'en {a_pico}'},
            {'color': '#EE9B00', 'rotulo': f'Ponderado por población · {a_ult}', 'valor': fino(pond[-1]),
             'delta': f'promedio simple {num(ultimo)}', 'serie': [fino(x) for x in pond if x is not None]},
            {'color': PIZARRA, 'rotulo': f'Jurisdicciones · {a_ult}', 'valor': n[-1], 'dec': 0, 'delta': f'{n[0]} en 1970'},
        ],
        'panel': p, 'preguntas': preguntas,
    }
    verificar(ultimo < pico, 'el promedio está por debajo de su máximo')
    pagina('evolucion_mundial.html', 'Evolución de la Libertad Económica en el Mundo',
           f'Promedio mundial del índice EFW y de sus cinco áreas, {anios[0]}–{a_ult} · de 0 a 10, más es más libre',
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

    p = [
        ['Trayectoria histórica', f'Bolivia se estancó en la franja baja durante los años 70 (de {num(bol[0])} en {anios[0]} a '
         f'{num(v(bol, 1980))} en 1980) y tocó su mínimo en <strong>1985</strong> ({num(piso)}), entre dictaduras militares e '
         f'hiperinflación: ese año Moneda sana marcó {num(m85)} de 10. El <strong>Plan de Estabilización de 1985</strong> '
         f'(DS 21060) marcó el giro: el puntaje subió hasta su máximo en <strong>{a_pico}</strong> ({num(pico)}), cuando '
         f'Bolivia ocupaba el puesto {p_pico} de {n_pico}.'],
        ['Período reciente', f'Tras el máximo, el puntaje retrocedió: {num(v(bol, 2005))} en 2005 y {num(v(bol, 2008))} en 2008, '
         f'ya con el modelo de mayor intervención estatal vigente desde 2006. Entre 2008 y {a_prev} osciló alrededor de 6 '
         f'(entre {num(min(meseta))} y {num(max(meseta))}). En <strong>{a_ult}</strong> cayó a <strong>{num(s_ult)}</strong>, '
         f'la mayor caída anual de la serie y el puntaje más bajo desde {desde}: Bolivia pasó del puesto {p_prev} al '
         f'<strong>{p_ult} de {n_ult}</strong>.'],
        [f'Qué cayó en {a_ult}', f'De los {num(caida)} puntos que perdió el índice, {num(baja["a4"] / 5)} vienen de '
         f'<strong>{AREAS[3]["nombre"]}</strong>, que se desplomó de {num(bola["a4"][-2])} a {num(bola["a4"][-1])} (puesto '
         f'{rk(a_prev, 4)} → {rk(a_ult, 4)} en esa área): la brecha entre el dólar oficial y el paralelo llevó a '
         f'<strong>cero</strong> el componente de mercado negro de divisas, que tuvo 10 de 10 hasta {a_prev}. '
         f'<strong>Moneda sana</strong> bajó de {num(bola["a3"][-2])} a {num(bola["a3"][-1])} con la inflación '
         f'({num(infl(a_prev), 1)} % en {a_prev}, {num(infl(a_ult), 1)} % en {a_ult}) y sigue siendo la mejor área.'],
        ['Comparativa', f'En {a_ult} Bolivia ({num(s_ult)}) está por debajo del promedio mundial ({num(mundo[-1])}) y del '
         f'latinoamericano ({num(lac[-1])}), y ocupa el puesto <strong>{p_ult} de {n_ult}</strong>. Frente a la región, la mayor '
         f'brecha está en <strong>{brecha["nombre"]}</strong> ({num(bola[brecha["k"]][-1])} frente a {num(lac_a[brecha["k"]])}) y '
         f'la única área en que Bolivia la supera es <strong>{sobre[0]["nombre"]}</strong> ({num(bola["a3"][-1])} frente a '
         f'{num(lac_a["a3"])}).'],
        ['ctx', f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. Promedios '
         f'simples: el latinoamericano reúne {n_lac} países en {a_ult}. Hasta 2000 los datos son quinquenales.'],
    ]
    preguntas = [
        ['¿Qué mide el índice de libertad económica?', EFW_QUE.format(n=n_ult)],
        ['¿Qué pasó en 1985?',
         f'La hiperinflación de 1984–1985 llevó a Moneda sana a {num(m85)} de 10 y al índice de Bolivia a su mínimo '
         f'({num(piso)}). El DS 21060 liberó precios, tipo de cambio y comercio, y frenó la emisión: Moneda sana volvió a '
         f'{num(v(bola["a3"], 1990))} en 1990 y a {num(v(bola["a3"], 1995))} en 1995, y el índice pasó del puesto '
         f'{v(pues, 1985)[0]} de {v(pues, 1985)[1]} en 1985 al {v(pues, 1995)[0]} de {v(pues, 1995)[1]} en 1995.'],
        ['¿Qué es el componente de mercado negro de divisas?',
         'Mide la brecha entre el tipo de cambio oficial y el del mercado paralelo: sin brecha, 10 de 10; con una brecha '
         'muy grande, 0. Es uno de los cuatro componentes de Libertad para comerciar internacionalmente, así que pasar de '
         f'{num(c4(a_prev), 0)} a {num(c4(a_ult), 0)} le restó {num((c4(a_prev) - c4(a_ult)) / 4)} puntos a esa área y '
         f'{num((c4(a_prev) - c4(a_ult)) / 20)} al índice general de Bolivia en {a_ult}.'],
        ['¿Por qué Moneda sana es la mejor área?',
         'El área mide el crecimiento del dinero, la inflación y su volatilidad, y la libertad para tener cuentas en moneda '
         f'extranjera. Con inflación baja ({num(infl(a_prev), 1)} % en {a_prev}) y cuentas en dólares permitidas, Bolivia '
         f'marcó {num(bola["a3"][-2])} en {a_prev}, puesto {rk(a_prev, 3)} del mundo en esa área. En {a_ult} bajó a '
         f'{num(bola["a3"][-1])} (puesto {rk(a_ult, 3)}). El índice todavía no recoge la inflación de {a_ult + 1}: llegará '
         f'con el informe {INFORME + 1}.'],
    ]
    datos = {
        'anios': anios, 'unidad': 'Índice EFW (0 a 10)', 'unidadCorta': 'Índice EFW',
        'indice': [
            {'k': 'bol', 'nombre': 'Bolivia', 'color': '#C71E1D', 'ancho': 2.5, 'area': True, 'v': [fino(x) for x in bol]},
            # América Latina en oro: con turquesa, frente al gris del promedio mundial no se distinguía (ΔE 11,9)
            {'k': 'lac', 'nombre': 'América Latina y el Caribe', 'corto': 'América Latina', 'color': '#EE9B00', 'ancho': 1.75,
             'v': [fino(x) for x in lac]},
            {'k': 'mundo', 'nombre': 'Promedio mundial', 'color': PIZARRA, 'ancho': 1.75, 'v': [fino(x) for x in mundo]},
        ],
        'areas': serie_areas(lambda k: bola[k]),
        'total': {'nombre': 'Índice de Bolivia', 'v': [fino(x) for x in bol]},
        'pieTip': [f'Bolivia: puesto {pp} de {nn}' for pp, nn in pues],
        'hitos': [{'anio': 1985, 'largo': '1985 · DS 21060', 'corto': '1985', 'alinear': 'left'},
                  {'anio': 2006, 'largo': '2006 · nuevo modelo económico', 'corto': '2006', 'alinear': 'left'}],
        'cifras': [
            {'color': '#C71E1D', 'rotulo': f'Bolivia · {a_ult}', 'valor': s_ult,
             'delta': f'▼ {num(caida)} en un año · puesto {p_ult} de {n_ult}', 'tono': 'malo',
             'serie': [v(bol, int(y)) for y in ANUALES]},
            {'color': '#005F73', 'rotulo': 'Máximo', 'valor': pico, 'delta': f'{a_pico} · puesto {p_pico}'},
            {'color': '#9B2226', 'rotulo': 'Mínimo', 'valor': piso, 'delta': f'en {a_piso}'},
            {'color': AREAS[mejor]['color'], 'rotulo': f'Mejor área · {a_ult}', 'valor': bola[AREAS[mejor]['k']][-1],
             'delta': AREAS[mejor]['corto'], 'serie': [v(bola[AREAS[mejor]['k']], int(y)) for y in ANUALES]},
        ],
        'panel': p, 'preguntas': preguntas,
    }
    pagina('bolivia_efw.html', 'Bolivia en el Índice de Libertad Económica',
           f'Puntaje general y por áreas, {anios[0]}–{a_ult}, frente al promedio mundial y al de América Latina y el Caribe',
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

CUERPO_COMP = r'''
    <div class="hz-bar">
      <div class="hz-item busca-item">
        <div class="busca" id="busca">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>
          <input type="text" id="buscar" placeholder="Agregar un país (hasta seis)…" autocomplete="off" spellcheck="false"
            role="combobox" aria-expanded="false" aria-controls="lista" aria-autocomplete="list" aria-label="Buscar un país para agregar" />
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
        <div class="grafico" id="chart"><div class="loading"><div class="spinner"></div><span>Cargando datos…</span></div></div>
      </div>
      <div class="panel">
        <div class="panel-hd"><span class="panel-hd-t">Lectura del gráfico</span><span class="panel-hd-d" id="panel-fecha"></span></div>
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
    PAISES.forEach(function (p) { PAIS[p.i] = p; p.b = plano(p.n + ' ' + p.i + ' ' + (p.al || '')); p.nb = plano(p.n); });
    PAISES.sort(function (a, b) { return a.n.localeCompare(b.n, 'es'); });
    var QN = { 1: 'cuartil 1 · más libre', 2: 'cuartil 2', 3: 'cuartil 3', 4: 'cuartil 4 · menos libre' };
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

    document.getElementById('ley-q').innerHTML = '<span class="ley-i">Cuartil EFW ' + D.anioQ + '</span>' + [1, 2, 3, 4].map(function (q) {
      return '<span class="ley-i"><span class="ley-d" style="background:' + qcol(q) + '"></span>' + (q === 1 ? '1 · más libre' : q === 4 ? '4 · menos libre' : q) + '</span>';
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
      return { cols: ['Año'].concat(vs.map(function (iso) { return PAIS[iso].n; })),
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
          (bol ? '<span class="pill fijo" aria-pressed="true" title="Bolivia queda siempre en el gráfico" style="' + vars + '">'
               : '<button type="button" class="pill" aria-pressed="' + on + '" title="Ocultar o mostrar ' + p.n + '" style="' + vars + '">') +
          '<span class="lp"></span>' + p.n + insignia(p) + (bol ? '</span>' : '</button>') +
          (bol ? '' : '<button type="button" class="tag-x" aria-label="Quitar ' + p.n + '" title="Quitar ' + p.n + '">×</button>') + '</span>';
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
      function abrir(si) { lst.classList.toggle('abierta', si); inp.setAttribute('aria-expanded', si); }
      function pintar() {
        var q = plano(inp.value.trim()), lleno = elegidos.length >= MAX;
        ops = PAISES.filter(function (p) { return elegidos.indexOf(p.i) < 0 && (!q || p.b.indexOf(q) >= 0); });
        if (q) ops.sort(function (a, b) {
          var ra = a.nb.indexOf(q) === 0 ? 0 : (' ' + a.nb).indexOf(' ' + q) >= 0 ? 1 : 2;
          var rb = b.nb.indexOf(q) === 0 ? 0 : (' ' + b.nb).indexOf(' ' + q) >= 0 ? 1 : 2;
          return ra - rb || a.n.localeCompare(b.n, 'es');
        });
        act = ops.length && !lleno ? 0 : -1;
        lst.innerHTML = (lleno ? '<div class="aviso">Ya hay seis países: quite uno para sumar otro.</div>' : '') +
          (ops.length ? ops.map(function (p, k) {
            var c = p.q ? qcol(p.q) : null;
            return '<button type="button" class="op' + (k === act ? ' activa' : '') + '" role="option" data-iso="' + p.i + '"' +
              (lleno ? ' aria-disabled="true"' : '') + '>' +
              '<span class="qd' + (c ? '' : ' sin') + '"' + (c ? ' style="background:' + c + ';color:' + PM.sobre(c) + '"' : '') + '>' + (p.q ? PM.num(p.s, 2) : '—') + '</span>' +
              '<span>' + p.n + '</span><span class="rg">' + p.r + '</span></button>';
          }).join('') : '<div class="aviso">Ningún país coincide con «' + inp.value.replace(/[<>&"]/g, '') + '».</div>');
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
          if (sin.length) h += PM.ttPie('Sin dato ese año: ' + sin.map(function (f) { return PAIS[f[0]].n; }).join(', '));
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
      return PM.ejeY({ unidad: chico ? 'Índice EFW' : 'Índice EFW (0 a 10)', fmt: PM.tick,
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
      var unidad = chico ? 'PIB per cápita (miles de $)' : 'PIB per cápita ($ de 2011, PPA)';
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


def js_comp(datos_pais):
    return JS_COMP.replace('@@DATOS_PAIS@@', datos_pais).replace('@@PANEL@@', JS_PANEL)


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

    p = [
        ['Cómo usar', 'Busque un país y agréguelo: hasta seis a la vez, con Bolivia fija. Pulse una pastilla para ocultar o '
         f'mostrar ese país y la × para quitarlo. La insignia es el puntaje EFW {ULTIMO} y su color, el cuartil: turquesa '
         'el más libre, después menta, oro y rojo.'],
        ['Divergencia histórica', f'En 1975 <strong>Chile</strong> ({num(s("CHL", 1975))}) y <strong>Bolivia</strong> '
         f'({num(s("BOL", 1975))}) puntuaban casi igual; en {ULTIMO} Chile marca {num(s("CHL", ULTIMO))} y Bolivia '
         f'{num(s("BOL", ULTIMO))}. <strong>Venezuela</strong> recorrió el camino inverso: de {num(s("VEN", 1970))} en 1970 a '
         f'{num(s("VEN", ULTIMO))} en {ULTIMO}, el último puesto de {n_ven}. Compare también Argentina y Singapur.'],
        ['Bolivia en contexto', f'Bolivia estuvo en la <strong>mitad superior</strong> del ranking entre {arriba[0]} y '
         f'{arriba[-1]}, tras las reformas de 1985 (puesto {p00} de {n00} en 2000); después volvió a la mitad inferior: '
         f'puesto <strong>{p_bol} de {n}</strong> en {ULTIMO}.'],
        ['ctx', f'<strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World: {INFORME} Annual Report. El cuartil es el '
         f'de {ULTIMO}, por puesto (con el puntaje a dos decimales, los empates comparten puesto). Hasta 2000 los datos son '
         'quinquenales; cada serie empieza cuando el país entra en el índice.'],
    ]
    preguntas = [
        ['¿Qué mide el índice de libertad económica?', EFW_QUE.format(n=n)],
        ['¿Qué es el cuartil?', f'Las {n} jurisdicciones de {ULTIMO}, ordenadas de más a menos libre y repartidas en cuatro '
         f'grupos: el cuartil 1 reúne a las {tam[0]} más libres y el 4, a las {tam[3]} menos libres. Lo indica el color de la '
         'insignia: turquesa, menta, oro y rojo, la misma escala del mapa.'],
        ['¿Por qué algunas series empiezan tarde?', f'El índice calificaba a {n70} países en 1970 y llegó a {n} en {a_tot}: '
         'cada país entra cuando hay datos suficientes para calificarlo. Hasta 1995 la serie es quinquenal y desde 2000, anual.'],
    ]
    datos = {
        'anios': anios, 'fecha': f'{anios[0]}–{anios[-1]}', 'anioQ': ULTIMO, 'inicial': ['BOL', 'CHL', 'ARG', 'VEN', 'SGP'],
        'colores': COLORES_PAIS, 'qc': QC,
        'paises': sorted(paises.values(), key=lambda d: d['i']), 'panel': p, 'preguntas': preguntas,
    }
    pagina('comparativa_paises.html', 'Comparativa Internacional de Libertad Económica',
           f'Índice EFW por país, {anios[0]}–{anios[-1]} · {n} jurisdicciones · de 0 a 10, más es más libre',
           ACENTO['paises'], CUERPO_COMP.replace('@@CONTROLES@@', ''), datos, js_comp(DATOS_EFW), estilo=ESTILO_COMP)


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
    p = [
        ['Cómo usar', f'Busque un país ({len(paises)} disponibles) y agréguelo: hasta seis a la vez, con Bolivia fija. La '
         f'insignia es el puntaje de libertad económica {ULTIMO} y su color, el cuartil; los países sin dato del índice no la '
         'llevan. En escala logarítmica, el mismo ritmo de crecimiento se ve con la misma pendiente.'],
        ['Dos siglos de divergencia', f'En {a0} el país más rico de la base ({NOMBRE[hi0[1]]}, {usd(hi0[0])}) tenía un ingreso '
         f'{num(hi0[0] / lo0[0], 1)} veces el del más pobre ({NOMBRE[lo0[1]]}, {usd(lo0[0])}); en {ultimo}, la distancia entre '
         f'{NOMBRE[hi1[1]]} y {NOMBRE[lo1[1]]} es de {num(hi1[0] / lo1[0], 0)} veces. <strong>Venezuela</strong> era más rica que '
         f'Chile en 1950 ({usd(g("VEN", 1950))} frente a {usd(g("CHL", 1950))}); en {ultimo} está por debajo de Bolivia.'],
        ['Bolivia', f'Bolivia tiene datos desde {a_bol} ({usd(g("BOL", a_bol))}). En 1950 su PIB per cápita '
         f'<strong>triplicaba</strong> al de Corea del Sur ({usd(g("BOL", 1950))} frente a {usd(g("KOR", 1950))}); en {ultimo} el '
         f'coreano es <strong>{num(rhoy, 1)} veces</strong> el boliviano ({usd(g("KOR", ultimo))} frente a '
         f'{usd(g("BOL", ultimo))}). En {ultimo - a_bol} años el ingreso boliviano se multiplicó por '
         f'{num(g("BOL", ultimo) / g("BOL", a_bol), 1)}; el coreano, por {num(g("KOR", ultimo) / g("KOR", a0), 0)} desde {a0}.'],
        ['El milagro asiático', 'Corea del Sur, Singapur, Hong Kong y Japón partieron en 1950 de niveles parecidos o inferiores '
         f'a los de América Latina: el más alto de los cuatro ({usd(max(g(i, 1950) for i in asia))}) no llegaba al de Argentina '
         f'({usd(g("ARG", 1950))}). Con apertura comercial, moneda sana y Estado de derecho lograron uno de los crecimientos más '
         'rápidos de la historia; en escala logarítmica se ve la aceleración.'],
        ['ctx', '<strong>Fuente:</strong> Maddison Project Database 2023 (Bolt y van Zanden, 2024). PIB per cápita en dólares '
         f'internacionales de 2011 (PPA). Antes de 1950 las cifras son reconstrucciones históricas, con años sueltos y más '
         f'incertidumbre: la base tiene {n0} países en {a0} y {n1} en {ultimo}.'],
    ]
    preguntas = [
        ['¿Qué son los dólares de 2011 (PPA)?', 'La producción por habitante medida a precios internacionales de 2011, con '
         'paridad de poder adquisitivo: un dólar compra lo mismo en todos los países y años, así que las cifras se comparan '
         'entre sí y en el tiempo. La base es el Maddison Project Database 2023, de la Universidad de Groningen.'],
        ['¿Por qué la escala logarítmica?', 'En escala logarítmica la misma distancia vertical es el mismo porcentaje: pasar '
         'de $1.000 a $2.000 ocupa lo mismo que de $20.000 a $40.000. Así se comparan ritmos de crecimiento entre países '
         'ricos y pobres; la escala natural muestra mejor las diferencias absolutas de hoy.'],
        ['¿Qué tan confiables son los datos antiguos?', f'Antes de 1950 las cifras son reconstrucciones históricas: muchos '
         f'países tienen años sueltos (Bolivia empieza en {a_bol} y salta a {a_bol2}) y el margen de error es mayor. Desde '
         '1950 la serie es anual para casi todos.'],
    ]
    controles = (
        '\n      <div class="hz-item"><span class="hz-lbl">Escala</span><div class="hz-grp" id="b-escala"></div></div>'
        '\n      <div class="hz-item"><span class="hz-lbl">Período</span><div class="hz-grp" id="b-periodo"></div></div>')
    periodos = [[str(a0), f'Desde {a0}'], ['1950', 'Desde 1950']]
    datos = {
        'ultimo': ultimo, 'fecha': f'{a0}–{ultimo}', 'anioQ': ULTIMO, 'inicial': ['BOL', 'KOR', 'CHL', 'ARG', 'VEN'],
        'colores': COLORES_PAIS, 'qc': QC, 'periodos': periodos,
        'controles': [{'id': 'b-escala', 'k': 'escala', 'ops': [['log', 'Logarítmica'], ['nat', 'Natural']]},
                      {'id': 'b-periodo', 'k': 'periodo', 'ops': periodos}],
        'paises': sorted(paises, key=lambda d: d['i']), 'panel': p, 'preguntas': preguntas,
    }
    pagina('comparativa_pib.html', 'Evolución del PIB per Cápita',
           f'PIB per cápita en dólares internacionales de 2011 (PPA), {a0}–{ultimo} · Maddison Project Database 2023',
           ACENTO['pib'], CUERPO_COMP.replace('@@CONTROLES@@', controles), datos, js_comp(DATOS_PIB),
           fuente=MADDISON, estilo=ESTILO_COMP)


if __name__ == '__main__':
    print('Generando los 5 gráficos complementarios (molde de monitores)…')
    gen_areas_regiones()
    gen_evolucion_mundial()
    gen_bolivia_efw()
    gen_comparativa_paises()
    gen_comparativa_pib()
    print('Listo.')
