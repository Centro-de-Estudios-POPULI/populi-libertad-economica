"""
Generate 5 additional ECharts embeds matching the premium scatter-plot design:
1. areas_regiones.html  — Grouped bar: EFW areas by world region (2023)
2. evolucion_mundial.html — Line: global EFW average 1970-2023
3. bolivia_efw.html — Line: Bolivia EFW score + 5 areas 1970-2023
4. comparativa_paises.html — Interactive multi-line EFW, country selector + quartile badges
5. comparativa_pib.html — Interactive multi-line GDP pc, country selector + quartile badges
"""
import json

with open('data/efw_panel_map.json') as f:
    panel = json.load(f)
with open('data/efw_country_meta.json') as f:
    meta = json.load(f)
with open('data/gdp_pc_maddison.json') as f:
    gdp_raw = json.load(f)

OUT = 'embed'

AREA_NAMES = ['Tamano del Gobierno', 'Sistema Legal', 'Moneda Sana',
              'Comercio Internacional', 'Regulacion']
AREA_COLORS = ['#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
AREA_NAMES_ES = ['Tamano del Gobierno', 'Sistema Legal y Derechos de Propiedad',
                 'Moneda Sana', 'Libertad para Comerciar Internacionalmente', 'Regulacion']

REGION_SHORT = {
    'East Asia & Pacific': 'Asia Oriental y Pacifico',
    'Europe & Central Asia': 'Europa y Asia Central',
    'Latin America & the Caribbean': 'America Latina y el Caribe',
    'Middle East & North Africa': 'Medio Oriente y N. de Africa',
    'North America': 'Norteamerica',
    'South Asia': 'Asia del Sur',
    'Sub-Saharan Africa': 'Africa Subsahariana'
}

QC = {1:'#10B981', 2:'#3B82F6', 3:'#F59E0B', 4:'#EF4444'}
QL = {1:'Cuartil Superior', 2:'Segundo Cuartil', 3:'Tercer Cuartil', 4:'Cuartil Inferior'}

PALETTE = ['#EF4444','#10B981','#3B82F6','#8B5CF6','#F59E0B','#EC4899',
           '#06B6D4','#64748B','#F97316','#84CC16','#A855F7','#14B8A6',
           '#E11D48','#0EA5E9','#D946EF','#FB923C']

# ── Shared CSS (matches scatter_*.html) ─────────────────────
BASE_CSS = '''
    :root {
      --populi:#8B1A1A; --populi-light:#C00000;
      --cream:#F5EFE0; --brown-dark:#3D2B1F;
      --navy:#0D1B2A; --navy-light:#1A2940; --slate:#475569; --slate-light:#64748B;
      --warm-white:#FAF8F3; --light-gray:#F1EDE5; --border:#E2DDD3; --dark-border:#2A3A50;
      --bg:var(--warm-white); --card:#FFFFFF; --text:var(--brown-dark); --muted:var(--slate-light);
      --radius:12px;
    }
    [data-theme="dark"] {
      --bg:#080808; --card:#141414; --text:#E2E8F0; --muted:#64748B;
      --border:#2A3A50; --light-gray:#1A1A1A; --cream:#1A2940;
    }
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased;transition:background .25s,color .25s}
    .wrap{max-width:1200px;margin:0 auto;padding:20px 16px}
    .sec-hd{margin-bottom:12px}
    .sec-title{font-family:'Playfair Display',Georgia,serif;font-size:1.55rem;font-weight:700;color:var(--navy);display:flex;align-items:center;gap:10px;line-height:1.15}
    [data-theme="dark"] .sec-title{color:#fff}
    .accent-bar{width:4px;height:26px;border-radius:2px;flex-shrink:0}
    .sec-sub{font-size:.78rem;color:var(--muted);padding-left:14px;margin-top:2px}
    [data-theme="dark"] .sec-sub{color:rgba(255,255,255,.4)}
    .legend-bar{display:flex;flex-wrap:wrap;gap:4px 10px;padding:2px 14px 10px;align-items:center}
    .leg-item{display:flex;align-items:center;gap:3px;font-size:.58rem;font-weight:600;color:var(--muted);white-space:nowrap}
    .leg-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
    .leg-line{width:16px;height:0;flex-shrink:0}
    .main-grid{display:grid;grid-template-columns:3fr 2fr;gap:16px}
    @media(max-width:900px){.main-grid{grid-template-columns:1fr}}
    @media(max-width:500px){.sec-title{font-size:1.2rem}}
    .chart-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;height:560px}
    [data-theme="dark"] .chart-card{background:#141414;border-color:var(--dark-border)}
    @media(max-width:900px){.chart-card{height:440px}}
    @media(max-width:500px){.chart-card{height:340px}}
    #chart{width:100%;height:100%}
    .panel{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
    [data-theme="dark"] .panel{background:#141414;border-color:var(--dark-border)}
    .panel-hd{padding:10px 14px;display:flex;align-items:center;justify-content:space-between}
    .panel-hd-t{font-size:.56rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.8)}
    .panel-body{padding:14px;flex:1;overflow-y:auto}
    .pb{margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid var(--border)}
    [data-theme="dark"] .pb{border-color:var(--dark-border)}
    .pb:last-child{border-bottom:none;margin-bottom:0;padding-bottom:0}
    .pb-lbl{font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px}
    .pb-desc{font-size:.68rem;line-height:1.5;color:var(--muted)}
    [data-theme="dark"] .pb-desc{color:rgba(255,255,255,.45)}
    .pb-desc strong{color:var(--navy)}
    [data-theme="dark"] .pb-desc strong{color:#E2E8F0}
    .ctx{background:var(--cream);border-radius:6px;padding:8px 10px;margin-top:6px}
    [data-theme="dark"] .ctx{background:var(--navy-light)}
    .ctx p{font-size:.68rem;line-height:1.5;color:var(--muted)}
    [data-theme="dark"] .ctx p{color:#94A3B8}
    .source{display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding:0 2px}
    .source-txt{font-size:.6rem;color:var(--muted)}
    .source-txt a{color:var(--populi);font-weight:600;text-decoration:none}
    .source-txt a:hover{text-decoration:underline}
    .kpi-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;padding-left:14px}
    .kpi{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 14px;min-width:110px}
    [data-theme="dark"] .kpi{background:#141414;border-color:var(--dark-border)}
    .kpi-label{font-size:.52rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:2px}
    .kpi-val{font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:700}
    .kpi-delta{font-size:.6rem;font-family:'JetBrains Mono',monospace}
'''

SELECTOR_CSS = '''
    .controls-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;padding-left:14px;flex-wrap:wrap}
    .search-box{position:relative;flex:1;min-width:200px;max-width:360px}
    .search-box input{width:100%;padding:8px 12px 8px 32px;border:1px solid var(--border);border-radius:8px;
      font-size:.82rem;font-family:Inter,sans-serif;background:var(--card);color:var(--text);outline:none}
    .search-box input:focus{border-color:#10B981;box-shadow:0 0 0 2px rgba(16,185,129,.15)}
    .search-icon{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}
    .dropdown{position:absolute;top:100%;left:0;right:0;max-height:260px;overflow-y:auto;
      background:var(--card);border:1px solid var(--border);border-radius:10px;margin-top:4px;z-index:50;
      box-shadow:0 8px 24px rgba(0,0,0,.1);display:none}
    .dropdown.open{display:block}
    .dd-item{display:flex;align-items:center;gap:8px;padding:8px 12px;cursor:pointer;
      font-size:.8rem;transition:background .15s}
    .dd-item:hover{background:rgba(16,185,129,.08)}
    .dd-item .q-badge{font-size:.6rem;font-weight:700;color:#fff;padding:2px 6px;border-radius:4px;
      font-family:'JetBrains Mono',monospace;min-width:36px;text-align:center}
    .dd-item .cname{flex:1;color:var(--text)}
    .dd-item .region{font-size:.65rem;color:var(--muted)}
    .tags{display:flex;flex-wrap:wrap;gap:6px;padding:0 14px 12px;min-height:28px}
    .tag{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:20px;
      font-size:.72rem;font-weight:600;cursor:default;border:1px solid var(--border);
      background:var(--card);color:var(--text);transition:all .15s}
    [data-theme="dark"] .tag{border-color:var(--dark-border)}
    .tag .q-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
    .tag .q-score{font-family:'JetBrains Mono',monospace;font-size:.62rem;font-weight:700;opacity:.7}
    .tag .x{cursor:pointer;opacity:.4;font-size:.85rem;margin-left:1px;transition:opacity .15s}
    .tag .x:hover{opacity:1}
    .tag:hover{border-color:var(--muted)}
    .tag-bol{border-color:#EF4444;border-width:1.5px}
    .hz-lbl{font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
    .hz-grp{display:flex;flex-wrap:wrap;gap:0;background:var(--light-gray);border-radius:8px;padding:2px;border:1px solid var(--border)}
    [data-theme="dark"] .hz-grp{background:#1A1A1A;border-color:var(--dark-border)}
    .hz-btn{padding:5px 14px;border:none;border-radius:6px;font-family:'Inter',sans-serif;font-size:.68rem;font-weight:600;cursor:pointer;background:transparent;color:var(--muted);transition:all .2s}
    .hz-btn:hover{color:var(--text)}
    .hz-btn.active{background:var(--accent);color:#fff;box-shadow:0 2px 8px rgba(0,0,0,.15)}
'''

THEME_SYNC_JS = '''
    window.addEventListener('message', function(e) {
      if (e.data && e.data.theme) {
        document.documentElement.setAttribute('data-theme', e.data.theme);
        if (typeof rebuildChart === 'function') rebuildChart();
      }
    });
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme:dark)').matches)
      document.documentElement.setAttribute('data-theme', 'dark');
'''


def html_start(title, accent, extra_css=''):
    return f'''<!DOCTYPE html>
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
    :root {{ --accent:{accent}; }}
{BASE_CSS}{extra_css}
  </style>
</head>
<body>
<div class="wrap">
'''

HTML_FOOT = f'''</div>
<script>{THEME_SYNC_JS}</script>
</body></html>'''


def source_footer(sources):
    return f'<div class="source"><span class="source-txt">Fuente: {sources} · Elaboracion: <a href="https://populi.org.bo" target="_blank">POPULI</a></span></div>'


# Helpers
def compute_world_avg(year):
    ss = [d['s'] for d in panel[year].values() if d.get('s') is not None]
    return round(sum(ss)/len(ss), 2) if ss else None

def compute_region_avg(year, region):
    ss = [panel[year][iso]['s'] for iso in panel[year]
          if iso in meta and meta[iso]['region']==region and panel[year][iso].get('s') is not None]
    return round(sum(ss)/len(ss), 2) if ss else None

def build_country_list():
    year = '2023'
    scored = []
    for iso, d in panel[year].items():
        if iso not in meta or d.get('s') is None: continue
        scored.append((iso, meta[iso]['name'], meta[iso]['region'], d['s']))
    scored.sort(key=lambda x: -x[3])
    n = len(scored)
    result = []
    for i, (iso, name, region, score) in enumerate(scored):
        rank = i + 1
        q = 1 if rank <= n/4 else (2 if rank <= n/2 else (3 if rank <= 3*n/4 else 4))
        result.append({'iso':iso, 'name':name, 'region':REGION_SHORT.get(region,region),
                       'score':round(score,2), 'q':q, 'rank':rank})
    return result


# ============================================================
# 1. AREAS POR REGION
# ============================================================
def gen_areas_regiones():
    year = '2023'
    accent = '#3B82F6'
    region_data = {}
    for iso, d in panel[year].items():
        if iso not in meta: continue
        reg = meta[iso]['region']
        if reg not in region_data:
            region_data[reg] = {f'a{i+1}':[] for i in range(5)}
        for ai in range(5):
            k = f'a{ai+1}'
            if d.get(k) is not None:
                region_data[reg][k].append(d[k])

    order = ['North America','Europe & Central Asia','East Asia & Pacific',
             'Middle East & North Africa','Latin America & the Caribbean',
             'South Asia','Sub-Saharan Africa']
    cats = json.dumps([REGION_SHORT[r] for r in order])

    # Global averages per area
    area_avgs = {}
    for ai in range(5):
        k = f'a{ai+1}'
        all_vals = []
        for r in order:
            all_vals.extend(region_data[r][k])
        area_avgs[k] = round(sum(all_vals)/len(all_vals), 2) if all_vals else 0

    # LAC values
    lac_vals = {}
    for ai in range(5):
        k = f'a{ai+1}'
        v = region_data['Latin America & the Caribbean'][k]
        lac_vals[k] = round(sum(v)/len(v), 2) if v else 0

    series_js = []
    for ai in range(5):
        k = f'a{ai+1}'
        vals = []
        for r in order:
            v = region_data[r][k]
            vals.append(round(sum(v)/len(v),2) if v else 0)
        series_js.append(
            f"{{name:'{AREA_NAMES[ai]}',type:'bar',data:{json.dumps(vals)},"
            f"itemStyle:{{color:'{AREA_COLORS[ai]}',borderRadius:[3,3,0,0]}},barMaxWidth:18}}"
        )

    # Compute best/worst region
    reg_overall = {}
    for r in order:
        all_s = []
        for iso, d in panel[year].items():
            if iso in meta and meta[iso]['region']==r and d.get('s') is not None:
                all_s.append(d['s'])
        reg_overall[r] = round(sum(all_s)/len(all_s),2) if all_s else 0
    best_reg = max(reg_overall, key=reg_overall.get)
    worst_reg = min(reg_overall, key=reg_overall.get)

    html = html_start('Calificacion por Areas — Regiones del Mundo', accent)
    html += f'''
  <div class="sec-hd">
    <div class="sec-title"><span class="accent-bar" style="background:{accent}"></span>Calificacion por Areas del Indice de Libertad Economica</div>
    <div class="sec-sub">Promedio regional por area, {year} &middot; Fraser Institute EFW &middot; 165 jurisdicciones</div>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="kpi-label">Region mas libre</div><div class="kpi-val" style="color:#10B981;font-size:.9rem">{REGION_SHORT[best_reg]}</div><div class="kpi-delta" style="color:#10B981">{reg_overall[best_reg]}/10</div></div>
    <div class="kpi"><div class="kpi-label">Region menos libre</div><div class="kpi-val" style="color:#EF4444;font-size:.9rem">{REGION_SHORT[worst_reg]}</div><div class="kpi-delta" style="color:#EF4444">{reg_overall[worst_reg]}/10</div></div>
    <div class="kpi"><div class="kpi-label">Am. Latina</div><div class="kpi-val" style="color:#F59E0B;font-size:.9rem">{reg_overall["Latin America & the Caribbean"]}</div><div class="kpi-delta" style="color:var(--muted)">de 10</div></div>
  </div>
  <div class="legend-bar">
    {''.join(f'<span class="leg-item"><span class="leg-dot" style="background:{AREA_COLORS[i]}"></span>{AREA_NAMES[i]}</span>' for i in range(5))}
  </div>
  <div class="main-grid">
    <div class="chart-card"><div id="chart"></div></div>
    <div class="panel">
      <div class="panel-hd" style="background:#1E40AF"><span class="panel-hd-t">Lectura del grafico</span></div>
      <div class="panel-body">
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Que muestra</div><div class="pb-desc">Cada grupo de barras representa el <strong>promedio regional</strong> en las 5 areas del Indice de Libertad Economica del Fraser Institute. Las areas miden: tamano del gobierno, sistema legal, estabilidad monetaria, apertura comercial y regulacion.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Patrones clave</div><div class="pb-desc"><strong>Norteamerica y Europa</strong> lideran consistentemente, mientras que <strong>Asia del Sur y Africa Subsahariana</strong> muestran los puntajes mas bajos. El area de <strong>Moneda Sana</strong> es donde mas regiones convergen; las mayores brechas estan en <strong>Sistema Legal</strong> y <strong>Regulacion</strong>.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">America Latina</div><div class="pb-desc">La region tiene un desempeno <strong>intermedio-bajo</strong>. Su area mas debil es <strong>Sistema Legal</strong> ({lac_vals['a2']}/10), reflejando debilidades institucionales, seguida de <strong>Regulacion</strong> ({lac_vals['a5']}/10). Su mejor area es <strong>Moneda Sana</strong> ({lac_vals['a3']}/10).</div></div>
        <div class="ctx" style="border-left:3px solid {accent}"><p><strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World {year}. 165 jurisdicciones, 5 areas, 45 variables.</p></div>
      </div>
    </div>
  </div>
  {source_footer('<a href="https://www.fraserinstitute.org/economic-freedom" target="_blank">Fraser Institute</a>')}
<script>
function rebuildChart() {{ initChart(); }}
function initChart() {{
  var isDk = document.documentElement.getAttribute('data-theme')==='dark';
  var tc = isDk?'#E2E8F0':'#1E293B';
  var gc = isDk?'#1E293B':'#F0EDE6';
  var ac = isDk?'#334155':'#D5CFC5';
  var lc = isDk?'#64748B':'#94A3B8';
  var el = document.getElementById('chart');
  if(window._chart) window._chart.dispose();
  var chart = echarts.init(el);
  window._chart = chart;
  chart.setOption({{
    backgroundColor:'transparent',
    tooltip:{{trigger:'axis',axisPointer:{{type:'shadow'}},
      backgroundColor:isDk?'#1E1E1E':'#fff',borderColor:isDk?'#333':'#E2E8F0',
      textStyle:{{color:tc,fontSize:12,fontFamily:'Inter'}}}},
    legend:{{show:false}},
    grid:{{left:55,right:20,bottom:70,top:16,containLabel:false}},
    xAxis:{{type:'category',data:{cats},
      axisLabel:{{color:lc,fontSize:10,interval:0,rotate:25,fontFamily:'Inter'}},
      axisLine:{{lineStyle:{{color:ac}}}},axisTick:{{show:false}}}},
    yAxis:{{type:'value',min:0,max:10,
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono'}},
      splitLine:{{lineStyle:{{color:gc,type:'dashed'}}}},axisLine:{{show:false}}}},
    series:[{','.join(series_js)}]
  }});
  window.addEventListener('resize',function(){{chart.resize()}});
}}
initChart();
</script>
'''
    html += HTML_FOOT
    with open(f'{OUT}/areas_regiones.html','w',encoding='utf-8') as f: f.write(html)
    print('  OK areas_regiones.html')


# ============================================================
# 2. EVOLUCION MUNDIAL
# ============================================================
def gen_evolucion_mundial():
    accent = '#8B5CF6'
    yrs = [y for y in sorted(panel.keys()) if int(y)>=1970]
    yrs_int = [int(y) for y in yrs]
    world_avg = []
    area_s = {f'a{i+1}':[] for i in range(5)}
    counts = []
    for y in yrs:
        ss = [d['s'] for d in panel[y].values() if d.get('s') is not None]
        world_avg.append(round(sum(ss)/len(ss),3) if ss else None)
        counts.append(len(ss))
        for ai in range(5):
            k = f'a{ai+1}'
            vs = [d[k] for d in panel[y].values() if d.get(k) is not None]
            area_s[k].append(round(sum(vs)/len(vs),3) if vs else None)

    # KPIs
    latest = world_avg[-1]
    peak_val = max(v for v in world_avg if v)
    peak_yr = yrs_int[world_avg.index(peak_val)]
    low_val = min(v for v in world_avg if v)
    low_yr = yrs_int[world_avg.index(low_val)]

    area_series_js = []
    for ai in range(5):
        k = f'a{ai+1}'
        area_series_js.append(
            f"{{name:'{AREA_NAMES[ai]}',type:'line',data:{json.dumps(area_s[k])},"
            f"lineStyle:{{width:1.5,color:'{AREA_COLORS[ai]}',type:'dashed'}},"
            f"itemStyle:{{color:'{AREA_COLORS[ai]}'}},symbol:'none',z:5}}"
        )

    html = html_start('Evolucion de la Libertad Economica Mundial', accent)
    html += f'''
  <div class="sec-hd">
    <div class="sec-title"><span class="accent-bar" style="background:{accent}"></span>Evolucion de la Libertad Economica en el Mundo</div>
    <div class="sec-sub">Promedio mundial del EFW y sus 5 areas, 1970-2023 &middot; Fraser Institute</div>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="kpi-label">EFW Global 2023</div><div class="kpi-val" style="color:{accent}">{latest}</div><div class="kpi-delta" style="color:var(--muted)">de 10</div></div>
    <div class="kpi"><div class="kpi-label">Maximo historico</div><div class="kpi-val" style="color:#10B981">{peak_val}</div><div class="kpi-delta" style="color:#10B981">{peak_yr}</div></div>
    <div class="kpi"><div class="kpi-label">Minimo historico</div><div class="kpi-val" style="color:#EF4444">{low_val}</div><div class="kpi-delta" style="color:#EF4444">{low_yr}</div></div>
    <div class="kpi"><div class="kpi-label">Jurisdicciones 2023</div><div class="kpi-val">{counts[-1]}</div></div>
  </div>
  <div class="legend-bar">
    <span class="leg-item"><span class="leg-line" style="border-top:3px solid var(--text)"></span>EFW Global</span>
    {''.join(f'<span class="leg-item"><span class="leg-line" style="border-top:1.5px dashed {AREA_COLORS[i]}"></span>{AREA_NAMES[i]}</span>' for i in range(5))}
  </div>
  <div class="main-grid">
    <div class="chart-card"><div id="chart"></div></div>
    <div class="panel">
      <div class="panel-hd" style="background:#6D28D9"><span class="panel-hd-t">Lectura del grafico</span></div>
      <div class="panel-body">
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Tendencia general</div><div class="pb-desc">La libertad economica mundial cayo en los <strong>anos 70</strong> por la expansion del gasto publico e inflacion. Las reformas de los <strong>80 y 90</strong> (Reagan, Thatcher, apertura asiatica, caida del socialismo) impulsaron un ascenso sostenido hasta alcanzar su <strong>maximo en {peak_yr}</strong>.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Siglo XXI</div><div class="pb-desc">La liberalizacion continuo a ritmo moderado. El <strong>COVID-19</strong> (2020) provoco un fuerte retroceso por aumento del gasto publico y regulacion, eliminando casi <strong>dos decadas de avance</strong>. La recuperacion posterior ha sido parcial.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Areas</div><div class="pb-desc">Active las 5 areas en la leyenda para ver su evolucion individual. <strong>Moneda Sana</strong> fue el area de mayor mejora desde los 80. <strong>Tamano del Gobierno</strong> muestra la menor variacion temporal.</div></div>
        <div class="ctx" style="border-left:3px solid {accent}"><p><strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World 2024. Promedio no ponderado de todas las jurisdicciones disponibles cada ano.</p></div>
      </div>
    </div>
  </div>
  {source_footer('<a href="https://www.fraserinstitute.org/economic-freedom" target="_blank">Fraser Institute</a>')}
<script>
function rebuildChart() {{ initChart(); }}
function initChart() {{
  var isDk = document.documentElement.getAttribute('data-theme')==='dark';
  var tc = isDk?'#F8FAFC':'#1E293B';
  var gc = isDk?'#1E293B':'#F0EDE6';
  var ac = isDk?'#334155':'#D5CFC5';
  var lc = isDk?'#64748B':'#94A3B8';
  var nc = isDk?'#94A3B8':'#64748B';
  var el = document.getElementById('chart');
  if(window._chart) window._chart.dispose();
  var chart = echarts.init(el);
  window._chart = chart;
  chart.setOption({{
    backgroundColor:'transparent',
    tooltip:{{trigger:'axis',backgroundColor:isDk?'#1E1E1E':'#fff',
      borderColor:isDk?'#333':'#E2E8F0',textStyle:{{color:isDk?'#E2E8F0':'#1E293B',fontSize:12,fontFamily:'Inter'}}}},
    legend:{{
      data:['EFW Global',{','.join(["'"+n+"'" for n in AREA_NAMES])}],
      bottom:0,textStyle:{{color:lc,fontSize:10}},itemWidth:16,itemHeight:8,itemGap:10,
      selected:{{
        'EFW Global':true,
        {','.join(["'"+n+"':false" for n in AREA_NAMES])}
      }}
    }},
    grid:{{left:55,right:20,bottom:50,top:16,containLabel:false}},
    xAxis:{{type:'category',data:{json.dumps(yrs_int)},
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono'}},
      axisLine:{{lineStyle:{{color:ac}}}},axisTick:{{show:false}}}},
    yAxis:{{type:'value',min:4,max:8.5,
      name:'Indice EFW',nameLocation:'center',nameGap:38,
      nameTextStyle:{{fontSize:11,fontFamily:'Inter',color:nc}},
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono'}},
      splitLine:{{lineStyle:{{color:gc,type:'dashed'}}}},axisLine:{{show:false}}}},
    series:[
      {{name:'EFW Global',type:'line',data:{json.dumps(world_avg)},
        lineStyle:{{width:3,color:tc}},itemStyle:{{color:tc}},
        symbol:'circle',symbolSize:5,z:10,
        areaStyle:{{color:new echarts.graphic.LinearGradient(0,0,0,1,[
          {{offset:0,color:isDk?'rgba(139,92,246,.15)':'rgba(139,92,246,.1)'}},
          {{offset:1,color:'transparent'}}
        ])}}}},
      {','.join(area_series_js)}
    ]
  }});
  window.addEventListener('resize',function(){{chart.resize()}});
}}
initChart();
</script>
'''
    html += HTML_FOOT
    with open(f'{OUT}/evolucion_mundial.html','w',encoding='utf-8') as f: f.write(html)
    print('  OK evolucion_mundial.html')


# ============================================================
# 3. BOLIVIA EFW
# ============================================================
def gen_bolivia_efw():
    accent = '#EF4444'
    yrs = [y for y in sorted(panel.keys()) if int(y)>=1970 and 'BOL' in panel[y]]
    yrs_int = [int(y) for y in yrs]
    bol_s = [panel[y]['BOL'].get('s') for y in yrs]
    bol_a = {f'a{i+1}':[panel[y]['BOL'].get(f'a{i+1}') for y in yrs] for i in range(5)}
    w_avg = [compute_world_avg(y) for y in yrs]
    lac = [compute_region_avg(y, 'Latin America & the Caribbean') for y in yrs]

    latest = bol_s[-1]
    # Find Bolivia's rank in 2023
    y23 = panel['2023']
    scores_23 = sorted([d['s'] for d in y23.values() if d.get('s') is not None], reverse=True)
    bol_rank = scores_23.index(latest) + 1 if latest in scores_23 else '?'
    peak_val = max(v for v in bol_s if v)
    peak_yr = yrs_int[bol_s.index(peak_val)]
    low_val = min(v for v in bol_s if v)
    low_yr = yrs_int[bol_s.index(low_val)]

    # Best/worst area 2023
    bol_23 = panel['2023']['BOL']
    areas_23 = {AREA_NAMES[i]: bol_23.get(f'a{i+1}',0) for i in range(5)}
    best_a = max(areas_23, key=areas_23.get)
    worst_a = min(areas_23, key=areas_23.get)

    area_js = []
    for ai in range(5):
        k = f'a{ai+1}'
        area_js.append(
            f"{{name:'{AREA_NAMES[ai]}',type:'line',data:{json.dumps(bol_a[k])},"
            f"lineStyle:{{width:1.5,color:'{AREA_COLORS[ai]}'}},itemStyle:{{color:'{AREA_COLORS[ai]}'}},"
            f"symbol:'none',z:3}}"
        )
    sel = ','.join([f"'{n}':false" for n in AREA_NAMES])

    html = html_start('Bolivia en el Indice de Libertad Economica', accent)
    html += f'''
  <div class="sec-hd">
    <div class="sec-title"><span class="accent-bar" style="background:{accent}"></span>Bolivia en el Indice de Libertad Economica</div>
    <div class="sec-sub">Puntaje general y por areas, 1970-2023 &middot; Comparado con promedio mundial y regional</div>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="kpi-label">Bolivia 2023</div><div class="kpi-val" style="color:{accent}">{latest}</div><div class="kpi-delta" style="color:var(--muted)">#{bol_rank} de {len(scores_23)}</div></div>
    <div class="kpi"><div class="kpi-label">Maximo</div><div class="kpi-val" style="color:#10B981">{peak_val}</div><div class="kpi-delta" style="color:#10B981">{peak_yr}</div></div>
    <div class="kpi"><div class="kpi-label">Minimo</div><div class="kpi-val" style="color:#EF4444">{low_val}</div><div class="kpi-delta" style="color:#EF4444">{low_yr}</div></div>
    <div class="kpi"><div class="kpi-label">Mejor area</div><div class="kpi-val" style="color:#10B981;font-size:.8rem">{best_a}</div><div class="kpi-delta" style="color:#10B981">{areas_23[best_a]}/10</div></div>
  </div>
  <div class="legend-bar">
    <span class="leg-item"><span class="leg-line" style="border-top:3px solid #EF4444"></span>Bolivia</span>
    <span class="leg-item"><span class="leg-line" style="border-top:2px dashed #64748B"></span>Promedio Mundial</span>
    <span class="leg-item"><span class="leg-line" style="border-top:2px dotted #F59E0B"></span>Promedio LAC</span>
    {''.join(f'<span class="leg-item"><span class="leg-line" style="border-top:1.5px solid {AREA_COLORS[i]}"></span>{AREA_NAMES[i]}</span>' for i in range(5))}
  </div>
  <div class="main-grid">
    <div class="chart-card"><div id="chart"></div></div>
    <div class="panel">
      <div class="panel-hd" style="background:#991B1B"><span class="panel-hd-t">Lectura del grafico</span></div>
      <div class="panel-body">
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Trayectoria historica</div><div class="pb-desc">Bolivia mostro un <strong>deterioro constante hasta 1985</strong>, coincidiendo con dictaduras militares y la hiperinflacion. El <strong>Plan de Estabilizacion de 1985</strong> (DS 21060) marco un punto de inflexion con medidas de liberalizacion que impulsaron el puntaje hasta su maximo en <strong>{peak_yr} ({peak_val})</strong>.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Periodo reciente</div><div class="pb-desc">A partir de 2006, el modelo de mayor intervencion estatal revirtio parcialmente los avances. Las areas mas debiles son <strong>{worst_a}</strong> ({areas_23[worst_a]}/10) y el sistema legal, mientras que <strong>{best_a}</strong> ({areas_23[best_a]}/10) se mantiene relativamente alta gracias a la estabilidad de precios.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Comparativa</div><div class="pb-desc">Bolivia se ubica <strong>por debajo del promedio mundial y regional (LAC)</strong>. Active las 5 areas en la leyenda para ver en que dimensiones Bolivia tiene mas rezago respecto a la region.</div></div>
        <div class="ctx" style="border-left:3px solid {accent}"><p><strong>Fuente:</strong> Fraser Institute, Economic Freedom of the World 2024. Bolivia ocupa el puesto #{bol_rank} de {len(scores_23)} jurisdicciones en 2023.</p></div>
      </div>
    </div>
  </div>
  {source_footer('<a href="https://www.fraserinstitute.org/economic-freedom" target="_blank">Fraser Institute</a>')}
<script>
function rebuildChart() {{ initChart(); }}
function initChart() {{
  var isDk = document.documentElement.getAttribute('data-theme')==='dark';
  var gc = isDk?'#1E293B':'#F0EDE6';
  var ac = isDk?'#334155':'#D5CFC5';
  var lc = isDk?'#64748B':'#94A3B8';
  var nc = isDk?'#94A3B8':'#64748B';
  var el = document.getElementById('chart');
  if(window._chart) window._chart.dispose();
  var chart = echarts.init(el);
  window._chart = chart;
  chart.setOption({{
    backgroundColor:'transparent',
    tooltip:{{trigger:'axis',backgroundColor:isDk?'#1E1E1E':'#fff',
      borderColor:isDk?'#333':'#E2E8F0',
      textStyle:{{color:isDk?'#E2E8F0':'#1E293B',fontSize:12,fontFamily:'Inter'}}}},
    legend:{{
      data:['Bolivia (EFW)','Promedio Mundial','Promedio LAC',{','.join(["'"+n+"'" for n in AREA_NAMES])}],
      bottom:0,textStyle:{{color:lc,fontSize:10}},itemWidth:16,itemHeight:8,itemGap:8,
      selected:{{'Promedio Mundial':true,'Promedio LAC':true,'Bolivia (EFW)':true,{sel}}}
    }},
    grid:{{left:55,right:20,bottom:52,top:16,containLabel:false}},
    xAxis:{{type:'category',data:{json.dumps(yrs_int)},
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono'}},
      axisLine:{{lineStyle:{{color:ac}}}},axisTick:{{show:false}}}},
    yAxis:{{type:'value',min:3,max:10,
      name:'Indice EFW',nameLocation:'center',nameGap:38,
      nameTextStyle:{{fontSize:11,fontFamily:'Inter',color:nc}},
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono'}},
      splitLine:{{lineStyle:{{color:gc,type:'dashed'}}}},axisLine:{{show:false}}}},
    series:[
      {{name:'Bolivia (EFW)',type:'line',data:{json.dumps(bol_s)},
        lineStyle:{{width:3,color:'#EF4444'}},itemStyle:{{color:'#EF4444'}},
        symbol:'circle',symbolSize:6,z:10}},
      {{name:'Promedio Mundial',type:'line',data:{json.dumps(w_avg)},
        lineStyle:{{width:2,color:'#64748B',type:'dashed'}},itemStyle:{{color:'#64748B'}},
        symbol:'none',z:5}},
      {{name:'Promedio LAC',type:'line',data:{json.dumps(lac)},
        lineStyle:{{width:2,color:'#F59E0B',type:'dotted'}},itemStyle:{{color:'#F59E0B'}},
        symbol:'none',z:5}},
      {','.join(area_js)}
    ]
  }});
  window.addEventListener('resize',function(){{chart.resize()}});
}}
initChart();
</script>
'''
    html += HTML_FOOT
    with open(f'{OUT}/bolivia_efw.html','w',encoding='utf-8') as f: f.write(html)
    print('  OK bolivia_efw.html')


# ============================================================
# 4. COMPARATIVA PAISES EFW (Interactive)
# ============================================================
def gen_comparativa_paises():
    accent = '#06B6D4'
    yrs = [y for y in sorted(panel.keys()) if int(y)>=1970]
    yrs_int = [int(y) for y in yrs]
    countries = build_country_list()

    all_data = {}
    for iso in [c['iso'] for c in countries]:
        vals = []
        for y in yrs:
            v = panel[y].get(iso,{}).get('s')
            vals.append(v)
        all_data[iso] = vals

    defaults = ['BOL','CHL','ARG','VEN','IRL','SGP','NZL','USA']

    html = html_start('Comparativa Internacional — Libertad Economica', accent, SELECTOR_CSS)
    html += f'''
  <div class="sec-hd">
    <div class="sec-title"><span class="accent-bar" style="background:{accent}"></span>Comparativa Internacional de Libertad Economica</div>
    <div class="sec-sub">Selecciona paises para comparar su evolucion en el EFW, 1970-2023 &middot; 165 jurisdicciones disponibles</div>
  </div>
  <div class="controls-row">
    <div class="search-box">
      <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="search" placeholder="Buscar pais para agregar..." autocomplete="off">
      <div class="dropdown" id="dropdown"></div>
    </div>
  </div>
  <div class="tags" id="tags"></div>
  <div class="main-grid">
    <div class="chart-card"><div id="chart"></div></div>
    <div class="panel">
      <div class="panel-hd" style="background:#0E7490"><span class="panel-hd-t">Lectura del grafico</span></div>
      <div class="panel-body">
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Como usar</div><div class="pb-desc">Use el buscador para <strong>agregar paises</strong> a la comparativa. Cada etiqueta muestra el <strong>puntaje EFW 2023</strong> con un badge de color segun su cuartil: <span style="color:#10B981">&#9679; Q1 (mas libre)</span>, <span style="color:#3B82F6">&#9679; Q2</span>, <span style="color:#F59E0B">&#9679; Q3</span>, <span style="color:#EF4444">&#9679; Q4 (menos libre)</span>. Haga clic en &times; para remover.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Divergencia historica</div><div class="pb-desc">Paises que partieron de niveles similares de libertad economica en los 70 tomaron <strong>caminos radicalmente distintos</strong>. Compare Bolivia y Chile, o Argentina y Singapur, para ver como las <strong>decisiones institucionales</strong> generan trayectorias divergentes a lo largo de decadas.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Bolivia en contexto</div><div class="pb-desc">Bolivia (linea gruesa roja) se mantiene consistentemente en la <strong>mitad inferior</strong> del ranking mundial. Su breve periodo de reformas (1985-2000) es visible como una mejora parcial que no logro consolidarse.</div></div>
        <div class="ctx" style="border-left:3px solid {accent}"><p><strong>Fuente:</strong> Fraser Institute, EFW 2024. El badge de cuartil refleja la posicion en 2023. Las series comienzan segun disponibilidad de datos por pais.</p></div>
      </div>
    </div>
  </div>
  {source_footer('<a href="https://www.fraserinstitute.org/economic-freedom" target="_blank">Fraser Institute</a>')}
<script>
var YEARS = {json.dumps(yrs_int)};
var COUNTRIES = {json.dumps(countries)};
var ALL_DATA = {json.dumps(all_data)};
var QC = {{1:'#10B981',2:'#3B82F6',3:'#F59E0B',4:'#EF4444'}};
var QL = {{1:'Cuartil Superior',2:'Segundo Cuartil',3:'Tercer Cuartil',4:'Cuartil Inferior'}};
var PALETTE = {json.dumps(PALETTE)};
var selected = {json.dumps(defaults)};
var colorMap = {{}};
var colorIdx = 0;

function getColor(iso) {{
  if (!colorMap[iso]) {{ colorMap[iso] = PALETTE[colorIdx % PALETTE.length]; colorIdx++; }}
  return colorMap[iso];
}}
function getCountry(iso) {{ return COUNTRIES.find(function(c){{return c.iso===iso}}); }}
function rebuildChart() {{ initChart(); }}

function initChart() {{
  var isDk = document.documentElement.getAttribute('data-theme')==='dark';
  var gc = isDk?'#1E293B':'#F0EDE6';
  var ac = isDk?'#334155':'#D5CFC5';
  var lc = isDk?'#64748B':'#94A3B8';
  var nc = isDk?'#94A3B8':'#64748B';
  var el = document.getElementById('chart');
  if(window._chart) window._chart.dispose();
  var chart = echarts.init(el);
  window._chart = chart;
  var series = []; var allVals = [];
  selected.forEach(function(iso) {{
    var c = getCountry(iso), col = getColor(iso), isBol = iso==='BOL';
    var data = ALL_DATA[iso] || [];
    data.forEach(function(v){{ if(v!=null) allVals.push(v); }});
    series.push({{
      name: c ? c.name : iso, type:'line', data: data,
      lineStyle: {{width: isBol?3:2, color: col}},
      itemStyle: {{color: col}},
      symbol: isBol?'circle':'none', symbolSize: isBol?5:0, z: isBol?10:5
    }});
  }});
  var yMin = allVals.length ? Math.max(0, Math.floor(Math.min.apply(null,allVals)-0.5)) : 2;
  var yMax = allVals.length ? Math.min(10, Math.ceil(Math.max.apply(null,allVals)+0.3)) : 10;
  chart.setOption({{
    backgroundColor:'transparent',
    tooltip: {{trigger:'axis',backgroundColor:isDk?'#1E1E1E':'#fff',
      borderColor:isDk?'#333':'#E2E8F0',
      textStyle:{{color:isDk?'#E2E8F0':'#1E293B',fontSize:12,fontFamily:'Inter'}},
      order:'valueDesc'}},
    legend: {{show:false}},
    grid: {{left:55,right:20,bottom:32,top:16,containLabel:false}},
    xAxis: {{type:'category',data:YEARS,
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono'}},
      axisLine:{{lineStyle:{{color:ac}}}},axisTick:{{show:false}}}},
    yAxis: {{type:'value',min:yMin,max:yMax,
      name:'Indice EFW',nameLocation:'center',nameGap:38,
      nameTextStyle:{{fontSize:11,fontFamily:'Inter',color:nc}},
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono'}},
      splitLine:{{lineStyle:{{color:gc,type:'dashed'}}}},axisLine:{{show:false}}}},
    series: series
  }});
  window.addEventListener('resize',function(){{chart.resize()}});
}}

function renderTags() {{
  var html = '';
  selected.forEach(function(iso) {{
    var c = getCountry(iso), col = getColor(iso);
    var qc = c ? QC[c.q] : '#999';
    var isBol = iso==='BOL';
    html += '<span class="tag'+(isBol?' tag-bol':'')+'">'
      + '<span class="q-dot" style="background:'+qc+'"></span>'
      + '<span style="border-bottom:2px solid '+col+'">'+(c?c.name:iso)+'</span>'
      + '<span class="q-score">'+(c?c.score:'')+'</span>'
      + (isBol?'':' <span class="x" onclick="removeCountry(\\x27'+iso+'\\x27)">&times;</span>')
      + '</span>';
  }});
  document.getElementById('tags').innerHTML = html;
}}

function addCountry(iso) {{
  if (selected.indexOf(iso)===-1) {{ selected.push(iso); renderTags(); initChart(); }}
  document.getElementById('search').value = '';
  document.getElementById('dropdown').classList.remove('open');
}}
function removeCountry(iso) {{
  selected = selected.filter(function(s){{return s!==iso}});
  renderTags(); initChart();
}}

var searchEl = document.getElementById('search');
var ddEl = document.getElementById('dropdown');
searchEl.addEventListener('input', function() {{
  var q = this.value.toLowerCase().trim();
  if (!q) {{ ddEl.classList.remove('open'); return; }}
  var matches = COUNTRIES.filter(function(c) {{
    return (c.name.toLowerCase().indexOf(q)!==-1 || c.iso.toLowerCase().indexOf(q)!==-1)
      && selected.indexOf(c.iso)===-1;
  }}).slice(0,8);
  if (!matches.length) {{ ddEl.classList.remove('open'); return; }}
  ddEl.innerHTML = matches.map(function(c) {{
    return '<div class="dd-item" onclick="addCountry(\\x27'+c.iso+'\\x27)">'
      + '<span class="q-badge" style="background:'+QC[c.q]+'">'+c.score+'</span>'
      + '<span class="cname">'+c.name+'</span>'
      + '<span class="region">'+c.region+'</span></div>';
  }}).join('');
  ddEl.classList.add('open');
}});
searchEl.addEventListener('focus', function() {{ if(this.value) this.dispatchEvent(new Event('input')); }});
document.addEventListener('click', function(e) {{
  if (!e.target.closest('.search-box')) ddEl.classList.remove('open');
}});

renderTags();
initChart();
</script>
'''
    html += HTML_FOOT
    with open(f'{OUT}/comparativa_paises.html','w',encoding='utf-8') as f: f.write(html)
    print('  OK comparativa_paises.html')


# ============================================================
# 5. COMPARATIVA PIB PER CAPITA (Interactive)
# ============================================================
def gen_comparativa_pib():
    accent = '#F59E0B'
    yrs = list(range(1950, 2023))
    countries = build_country_list()

    isos_with_gdp = set(gdp_raw.keys())
    gdp_all = {}
    for iso in isos_with_gdp:
        vals = []
        for y in yrs:
            v = gdp_raw[iso].get(str(y))
            vals.append(round(v) if v else None)
        gdp_all[iso] = vals

    countries_gdp = [c for c in countries if c['iso'] in isos_with_gdp]
    defaults = ['BOL','CHL','ARG','VEN','IRL','SGP','KOR','USA']

    html = html_start('Comparativa de PIB per Capita', accent, SELECTOR_CSS)
    html += f'''
  <div class="sec-hd">
    <div class="sec-title"><span class="accent-bar" style="background:{accent}"></span>Evolucion del PIB per Capita</div>
    <div class="sec-sub">Selecciona paises para comparar &middot; Dolares internacionales de 2011, 1950-2022 &middot; Maddison Project Database 2023</div>
  </div>
  <div class="controls-row">
    <div class="search-box">
      <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="search" placeholder="Buscar pais para agregar..." autocomplete="off">
      <div class="dropdown" id="dropdown"></div>
    </div>
    <span class="hz-lbl">Escala:</span>
    <div class="hz-grp">
      <button class="hz-btn active" id="btn-log">Logaritmica</button>
      <button class="hz-btn" id="btn-nat">Natural</button>
    </div>
  </div>
  <div class="tags" id="tags"></div>
  <div class="main-grid">
    <div class="chart-card"><div id="chart"></div></div>
    <div class="panel">
      <div class="panel-hd" style="background:#B45309"><span class="panel-hd-t">Lectura del grafico</span></div>
      <div class="panel-body">
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Como usar</div><div class="pb-desc">Use el buscador para <strong>agregar paises</strong>. El badge de color indica el <strong>cuartil de libertad economica</strong> (EFW 2023): <span style="color:#10B981">&#9679; mas libre</span> a <span style="color:#EF4444">&#9679; menos libre</span>. Use el toggle <strong>Logaritmica/Natural</strong> para cambiar la escala del eje Y.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Divergencia de ingresos</div><div class="pb-desc">En 1950, la <strong>brecha de ingresos entre paises era mucho menor</strong>. Las trayectorias divergieron dramaticamente segun las instituciones adoptadas. Compare Corea del Sur (libre) con Bolivia, o Irlanda con Argentina, para ver el impacto acumulado de decadas de <strong>politicas mas o menos libres</strong>.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:{accent}">Bolivia</div><div class="pb-desc">Bolivia (linea gruesa roja) muestra un <strong>crecimiento lento y volatil</strong>. En 1950 tenia un PIB per capita similar al de Corea del Sur; hoy es <strong>6 veces menor</strong>. El estancamiento refleja decadas de instituciones debiles y baja libertad economica.</div></div>
        <div class="ctx" style="border-left:3px solid {accent}"><p><strong>Fuente:</strong> Maddison Project Database 2023 (Bolt & van Zanden). PIB per capita en dolares internacionales de 2011 (PPP). Alterne entre escala logaritmica y natural.</p></div>
      </div>
    </div>
  </div>
  {source_footer('Maddison Project Database 2023 (Bolt & van Zanden, 2024)')}
<script>
var YEARS = {json.dumps(yrs)};
var COUNTRIES = {json.dumps(countries_gdp)};
var ALL_DATA = {json.dumps(gdp_all)};
var QC = {{1:'#10B981',2:'#3B82F6',3:'#F59E0B',4:'#EF4444'}};
var QL = {{1:'Cuartil Superior',2:'Segundo Cuartil',3:'Tercer Cuartil',4:'Cuartil Inferior'}};
var PALETTE = {json.dumps(PALETTE)};
var selected = {json.dumps(defaults)};
var colorMap = {{}};
var colorIdx = 0;
var scaleMode = 'log';

function getColor(iso) {{
  if (!colorMap[iso]) {{ colorMap[iso] = PALETTE[colorIdx % PALETTE.length]; colorIdx++; }}
  return colorMap[iso];
}}
function getCountry(iso) {{ return COUNTRIES.find(function(c){{return c.iso===iso}}); }}
function rebuildChart() {{ initChart(); }}

function setScale(mode) {{
  scaleMode = mode;
  document.getElementById('btn-log').className = 'hz-btn' + (mode==='log'?' active':'');
  document.getElementById('btn-nat').className = 'hz-btn' + (mode==='natural'?' active':'');
  initChart();
}}

document.getElementById('btn-log').addEventListener('click', function(){{ setScale('log'); }});
document.getElementById('btn-nat').addEventListener('click', function(){{ setScale('natural'); }});

function initChart() {{
  var isDk = document.documentElement.getAttribute('data-theme')==='dark';
  var gc = isDk?'#1E293B':'#F0EDE6';
  var ac = isDk?'#334155':'#D5CFC5';
  var lc = isDk?'#64748B':'#94A3B8';
  var nc = isDk?'#94A3B8':'#64748B';
  var el = document.getElementById('chart');
  if(window._chart) window._chart.dispose();
  var chart = echarts.init(el);
  window._chart = chart;
  var allVals = [];
  var series = selected.map(function(iso) {{
    var c = getCountry(iso), col = getColor(iso), isBol = iso==='BOL';
    var data = ALL_DATA[iso] || [];
    data.forEach(function(v){{ if(v!=null) allVals.push(v); }});
    return {{
      name: c ? c.name : iso, type:'line', data: data,
      lineStyle: {{width: isBol?3:2, color: col}},
      itemStyle: {{color: col}},
      symbol:'none', z: isBol?10:5, connectNulls:true
    }};
  }});
  var isLog = scaleMode==='log';
  var yAxisCfg = {{
    name:'PIB per capita (USD 2011)',nameLocation:'center',
    nameTextStyle:{{fontSize:11,fontFamily:'Inter',color:nc}},
    axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono',
      formatter:function(v){{return '$'+(v>=1000?Math.round(v/1000)+'k':v);}}}},
    splitLine:{{lineStyle:{{color:gc,type:'dashed'}}}},axisLine:{{show:false}}
  }};
  if (isLog) {{
    yAxisCfg.type = 'log'; yAxisCfg.min = 500; yAxisCfg.nameGap = 50;
  }} else {{
    var hi = allVals.length ? Math.max.apply(null,allVals) : 50000;
    yAxisCfg.type = 'value'; yAxisCfg.min = 0;
    yAxisCfg.max = Math.ceil(hi/5000)*5000; yAxisCfg.nameGap = 60;
  }}
  chart.setOption({{
    backgroundColor:'transparent',
    tooltip: {{trigger:'axis',backgroundColor:isDk?'#1E1E1E':'#fff',
      borderColor:isDk?'#333':'#E2E8F0',
      textStyle:{{color:isDk?'#E2E8F0':'#1E293B',fontSize:12,fontFamily:'Inter'}},
      order:'valueDesc',
      valueFormatter:function(v){{return v?'$'+Math.round(v).toLocaleString():'Sin datos';}}}},
    legend: {{show:false}},
    grid: {{left:65,right:20,bottom:32,top:16,containLabel:false}},
    xAxis: {{type:'category',data:YEARS,
      axisLabel:{{color:lc,fontSize:10,fontFamily:'JetBrains Mono',interval:9}},
      axisLine:{{lineStyle:{{color:ac}}}},axisTick:{{show:false}}}},
    yAxis: yAxisCfg,
    series: series
  }});
  window.addEventListener('resize',function(){{chart.resize()}});
}}

function renderTags() {{
  var html = '';
  selected.forEach(function(iso) {{
    var c = getCountry(iso), col = getColor(iso);
    var qc = c ? QC[c.q] : '#999';
    var isBol = iso==='BOL';
    html += '<span class="tag'+(isBol?' tag-bol':'')+'">'
      + '<span class="q-dot" style="background:'+qc+'"></span>'
      + '<span style="border-bottom:2px solid '+col+'">'+(c?c.name:iso)+'</span>'
      + '<span class="q-score">'+(c?c.score:'')+'</span>'
      + (isBol?'':' <span class="x" onclick="removeCountry(\\x27'+iso+'\\x27)">&times;</span>')
      + '</span>';
  }});
  document.getElementById('tags').innerHTML = html;
}}

function addCountry(iso) {{
  if (selected.indexOf(iso)===-1) {{ selected.push(iso); renderTags(); initChart(); }}
  document.getElementById('search').value = '';
  document.getElementById('dropdown').classList.remove('open');
}}
function removeCountry(iso) {{
  selected = selected.filter(function(s){{return s!==iso}});
  renderTags(); initChart();
}}

var searchEl = document.getElementById('search');
var ddEl = document.getElementById('dropdown');
searchEl.addEventListener('input', function() {{
  var q = this.value.toLowerCase().trim();
  if (!q) {{ ddEl.classList.remove('open'); return; }}
  var matches = COUNTRIES.filter(function(c) {{
    return (c.name.toLowerCase().indexOf(q)!==-1 || c.iso.toLowerCase().indexOf(q)!==-1)
      && selected.indexOf(c.iso)===-1;
  }}).slice(0,8);
  if (!matches.length) {{ ddEl.classList.remove('open'); return; }}
  ddEl.innerHTML = matches.map(function(c) {{
    return '<div class="dd-item" onclick="addCountry(\\x27'+c.iso+'\\x27)">'
      + '<span class="q-badge" style="background:'+QC[c.q]+'">'+c.score+'</span>'
      + '<span class="cname">'+c.name+'</span>'
      + '<span class="region">'+c.region+'</span></div>';
  }}).join('');
  ddEl.classList.add('open');
}});
searchEl.addEventListener('focus', function() {{ if(this.value) this.dispatchEvent(new Event('input')); }});
document.addEventListener('click', function(e) {{
  if (!e.target.closest('.search-box')) ddEl.classList.remove('open');
}});

renderTags();
initChart();
</script>
'''
    html += HTML_FOOT
    with open(f'{OUT}/comparativa_pib.html','w',encoding='utf-8') as f: f.write(html)
    print('  OK comparativa_pib.html')


# ============================================================
if __name__ == '__main__':
    print('Generating 5 embeds (premium design)...')
    gen_areas_regiones()
    gen_evolucion_mundial()
    gen_bolivia_efw()
    gen_comparativa_paises()
    gen_comparativa_pib()
    print('\nDone!')
