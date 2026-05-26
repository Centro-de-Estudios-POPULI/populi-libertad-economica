"""Build comparativa_pib.html with full Maddison data (169 countries, 1820-2022)"""
import json

with open('data/_tmp_countries.json', 'r', encoding='utf-8') as f:
    countries_json = f.read()
with open('data/_tmp_alldata.json', 'r') as f:
    data_json = f.read()

CSS = r'''    :root { --accent:#F59E0B; }
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
    .main-grid{display:grid;grid-template-columns:3fr 2fr;gap:16px}
    @media(max-width:900px){.main-grid{grid-template-columns:1fr}}
    @media(max-width:500px){.sec-title{font-size:1.2rem}}
    .chart-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;height:560px}
    [data-theme="dark"] .chart-card{background:#141414;border-color:var(--dark-border)}
    @media(max-width:900px){.chart-card{height:440px}}
    @media(max-width:500px){.chart-card{height:340px}}
    #chart{width:100%;height:100%}
    .panel{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column;height:560px}
    [data-theme="dark"] .panel{background:#141414;border-color:var(--dark-border)}
    @media(max-width:900px){.panel{height:440px}}
    @media(max-width:500px){.panel{height:340px}}
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
    .hz-btn.active{background:var(--accent);color:#fff;box-shadow:0 2px 8px rgba(0,0,0,.15)}'''

JS = r'''var QC = {1:'#10B981',2:'#3B82F6',3:'#F59E0B',4:'#EF4444'};
var QL = {1:'Cuartil Superior',2:'Segundo Cuartil',3:'Tercer Cuartil',4:'Cuartil Inferior'};
var PALETTE = ["#EF4444", "#10B981", "#3B82F6", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4", "#64748B", "#F97316", "#84CC16", "#A855F7", "#14B8A6", "#E11D48", "#0EA5E9", "#D946EF", "#FB923C"];
var selected = ["BOL", "CHL", "ARG", "VEN", "IRL", "SGP", "KOR", "USA"];
var colorMap = {};
var colorIdx = 0;
var scaleMode = 'log';

function getColor(iso) {
  if (!colorMap[iso]) { colorMap[iso] = PALETTE[colorIdx % PALETTE.length]; colorIdx++; }
  return colorMap[iso];
}
function getCountry(iso) { return COUNTRIES.find(function(c){return c.iso===iso}); }
function rebuildChart() { initChart(); }

function setScale(mode) {
  scaleMode = mode;
  document.getElementById('btn-log').className = 'hz-btn' + (mode==='log'?' active':'');
  document.getElementById('btn-nat').className = 'hz-btn' + (mode==='natural'?' active':'');
  initChart();
}

document.getElementById('btn-log').addEventListener('click', function(){ setScale('log'); });
document.getElementById('btn-nat').addEventListener('click', function(){ setScale('natural'); });

function initChart() {
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
  var series = selected.map(function(iso) {
    var c = getCountry(iso), col = getColor(iso), isBol = iso==='BOL';
    var raw = ALL_DATA[iso] || [];
    raw.forEach(function(p){ if(p[1]!=null) allVals.push(p[1]); });
    return {
      name: c ? c.name : iso, type:'line', data: raw,
      lineStyle: {width: isBol?3:2, color: col},
      itemStyle: {color: col},
      symbol:'none', z: isBol?10:5, connectNulls:true
    };
  });
  var isLog = scaleMode==='log';
  var yAxisCfg = {
    name:'PIB per capita\n(USD int. 2011)',nameLocation:'center',
    nameTextStyle:{fontSize:11,fontFamily:'Inter',color:nc},
    axisLabel:{color:lc,fontSize:10,fontFamily:'JetBrains Mono',
      formatter:function(v){return '$'+(v>=1000?Math.round(v/1000)+'k':v);}},
    splitLine:{lineStyle:{color:gc,type:'dashed'}},axisLine:{show:false}
  };
  if (isLog) {
    yAxisCfg.type = 'log'; yAxisCfg.min = 300; yAxisCfg.nameGap = 55;
  } else {
    var hi = allVals.length ? Math.max.apply(null,allVals) : 50000;
    yAxisCfg.type = 'value'; yAxisCfg.min = 0;
    yAxisCfg.max = Math.ceil(hi/10000)*10000; yAxisCfg.nameGap = 65;
  }
  chart.setOption({
    backgroundColor:'transparent',
    tooltip: {trigger:'axis',backgroundColor:isDk?'#1E1E1E':'#fff',
      borderColor:isDk?'#333':'#E2E8F0',
      textStyle:{color:isDk?'#E2E8F0':'#1E293B',fontSize:12,fontFamily:'Inter'},
      order:'valueDesc',
      formatter:function(params){
        var yr = params[0].value[0];
        var h = '<strong>'+yr+'</strong>';
        params.forEach(function(p){
          if(p.value[1]!=null){
            h += '<br/>'+p.marker+' '+p.seriesName+': <strong>$'+Math.round(p.value[1]).toLocaleString()+'</strong>';
          }
        });
        return h;
      }},
    legend: {show:false},
    grid: {left:80,right:20,bottom:32,top:16,containLabel:false},
    xAxis: {type:'value',
      min:1820, max:2025,
      axisLabel:{color:lc,fontSize:10,fontFamily:'JetBrains Mono',
        formatter:function(v){return Math.round(v);}},
      axisLine:{lineStyle:{color:ac}},axisTick:{show:false},
      splitLine:{show:false}},
    yAxis: yAxisCfg,
    series: series
  });
  window.addEventListener('resize',function(){chart.resize()});
}

function renderTags() {
  var html = '';
  selected.forEach(function(iso) {
    var c = getCountry(iso), col = getColor(iso);
    var qc = c && c.q ? QC[c.q] : '#999';
    var isBol = iso==='BOL';
    html += '<span class="tag'+(isBol?' tag-bol':'')+'">'
      + '<span class="q-dot" style="background:'+qc+'"></span>'
      + '<span style="border-bottom:2px solid '+col+'">'+(c?c.name:iso)+'</span>'
      + '<span class="q-score">'+(c&&c.score?c.score:'')+'</span>'
      + (isBol?'':' <span class="x" onclick="removeCountry(\''+iso+'\')">×</span>')
      + '</span>';
  });
  document.getElementById('tags').innerHTML = html;
}

function addCountry(iso) {
  if (selected.indexOf(iso)===-1) { selected.push(iso); renderTags(); initChart(); }
  document.getElementById('search').value = '';
  document.getElementById('dropdown').classList.remove('open');
}
function removeCountry(iso) {
  selected = selected.filter(function(s){return s!==iso});
  renderTags(); initChart();
}

var searchEl = document.getElementById('search');
var ddEl = document.getElementById('dropdown');
searchEl.addEventListener('input', function() {
  var q = this.value.toLowerCase().trim();
  if (!q) { ddEl.classList.remove('open'); return; }
  var matches = COUNTRIES.filter(function(c) {
    return (c.name.toLowerCase().indexOf(q)!==-1 || c.iso.toLowerCase().indexOf(q)!==-1)
      && selected.indexOf(c.iso)===-1;
  }).slice(0,8);
  if (!matches.length) { ddEl.classList.remove('open'); return; }
  ddEl.innerHTML = matches.map(function(c) {
    var bg = c.q ? QC[c.q] : '#999';
    var label = c.score ? c.score : '—';
    return '<div class="dd-item" onclick="addCountry(\''+c.iso+'\')">'
      + '<span class="q-badge" style="background:'+bg+'">'+label+'</span>'
      + '<span class="cname">'+c.name+'</span>'
      + '<span class="region">'+c.region+'</span></div>';
  }).join('');
  ddEl.classList.add('open');
});
searchEl.addEventListener('focus', function() { if(this.value) this.dispatchEvent(new Event('input')); });
document.addEventListener('click', function(e) {
  if (!e.target.closest('.search-box')) ddEl.classList.remove('open');
});

renderTags();
initChart();'''

BODY = '''
  <div class="sec-hd">
    <div class="sec-title"><span class="accent-bar" style="background:#F59E0B"></span>Evolucion del PIB per Capita</div>
    <div class="sec-sub">Selecciona paises para comparar &middot; Dolares internacionales de 2011, 1820-2022 &middot; Maddison Project Database 2023 &middot; 169 paises</div>
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
        <div class="pb"><div class="pb-lbl" style="color:#F59E0B">Como usar</div><div class="pb-desc">Use el buscador para <strong>agregar paises</strong> (169 disponibles). El badge de color indica el <strong>cuartil de libertad economica</strong> (EFW 2023): <span style="color:#10B981">&#9679; mas libre</span> a <span style="color:#EF4444">&#9679; menos libre</span>. Paises sin dato EFW aparecen en gris. Use el toggle <strong>Logaritmica/Natural</strong> para cambiar la escala.</div></div>
        <div class="pb"><div class="pb-lbl" style="color:#F59E0B">Dos siglos de divergencia</div><div class="pb-desc">En 1820, la <strong>brecha de ingresos entre paises era minima</strong>. Las trayectorias divergieron dramaticamente segun las instituciones adoptadas. La Revolucion Industrial beneficio primero a quienes adoptaron mercados libres y estado de derecho. Compare las trayectorias de <strong>Reino Unido, Estados Unidos</strong> (despegue temprano) contra <strong>Bolivia o Argentina</strong> (estancamiento relativo).</div></div>
        <div class="pb"><div class="pb-lbl" style="color:#F59E0B">Bolivia</div><div class="pb-desc">Bolivia (linea gruesa roja) tiene datos desde <strong>1846</strong> ($1,184). En 1950 tenia un PIB per capita similar al de Corea del Sur; hoy es <strong>6 veces menor</strong>. Su PIB per capita de 2022 ($6,481) es apenas <strong>5.5 veces</strong> lo que era hace 176 anos. Compare con Corea del Sur: de $854 en 1820 a $41,321 en 2022 (<strong>48 veces</strong>).</div></div>
        <div class="pb"><div class="pb-lbl" style="color:#F59E0B">El milagro asiatico</div><div class="pb-desc">Singapur, Corea del Sur, Hong Kong y Japon partieron de niveles similares o inferiores a America Latina. Sus reformas de <strong>apertura comercial, moneda sana y estado de derecho</strong> generaron el crecimiento mas rapido de la historia. En escala logaritmica se aprecia mejor la <strong>aceleracion exponencial</strong>.</div></div>
        <div class="ctx" style="border-left:3px solid #F59E0B"><p><strong>Fuente:</strong> Maddison Project Database 2023 (Bolt &amp; van Zanden). PIB per capita en dolares internacionales de 2011 (PPP). Los datos historicos previos a 1950 son estimaciones academicas con mayor incertidumbre.</p></div>
      </div>
    </div>
  </div>
  <div class="source"><span class="source-txt">Fuente: Maddison Project Database 2023 (Bolt &amp; van Zanden, 2024) &middot; Elaboracion: <a href="https://populi.org.bo" target="_blank">POPULI</a></span></div>'''

THEME_SCRIPT = '''
    window.addEventListener('message', function(e) {
      if (e.data && e.data.theme) {
        document.documentElement.setAttribute('data-theme', e.data.theme);
        if (typeof rebuildChart === 'function') rebuildChart();
      }
    });
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme:dark)').matches)
      document.documentElement.setAttribute('data-theme', 'dark');'''

html = f'''<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Comparativa de PIB per Capita - Populi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..800&family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>
{CSS}
  </style>
</head>
<body>
<div class="wrap">
{BODY}
<script>
var COUNTRIES = {countries_json};
var ALL_DATA = {data_json};
{JS}
</script>
</div>
<script>{THEME_SCRIPT}
</script>
</body></html>
'''

with open('embed/comparativa_pib.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Written: {len(html)/1024:.0f} KB')
print('Done!')
