"""Paso 5: dashboard HTML autocontenido (Leaflet + Plotly), datos incrustados como JSON."""
import base64
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW, PROC, FIG = BASE / "datos" / "raw", BASE / "datos" / "procesados", BASE / "figuras"
OUT = BASE / "dashboard"
OUT.mkdir(exist_ok=True)

res = json.loads((PROC / "resumen_poblacion.json").read_text(encoding="utf-8"))
dn = json.loads((PROC / "dnbr_incendio_190.json").read_text(encoding="utf-8"))
sens = pd.read_csv(PROC / "sensibilidad_dnbr_incendio_190.csv")
grad = pd.read_csv(PROC / "gradiente_definiciones.csv")
pdep = pd.read_csv(PROC / "poblacion_5km_por_departamento.csv").head(15)
pdist = pd.read_csv(PROC / "poblacion_5km_por_distrito.csv", dtype={"IDDIST": str})
act = pd.read_csv(PROC / "incendios_activos_poblacion.csv")

dist = gpd.read_file(RAW / "peru_distrital_simple.geojson")[["IDDIST", "geometry"]]
d = dist.merge(pdist[pdist.expuesta_5km > 0], on="IDDIST")
d["geometry"] = d.geometry.simplify(0.003)
dep = gpd.read_file(RAW / "peru_departamental_simple.geojson")[["NOMBDEP", "geometry"]]
dep["geometry"] = dep.geometry.simplify(0.01)

fires = act[["incendio_id", "lat", "lon", "n_focos", "huella_ha", "pob_5km", "urbano",
             "departamento", "provincia", "distrito", "inicio", "ultimo"]].round(4)
datos = {
    "distritos": json.loads(d.to_json()),
    "departamentos": json.loads(dep.to_json()),
    "incendios": fires.to_dict("records"),
    "dep": pdep.to_dict("records"),
    "grad": grad.to_dict("records"),
}
img = base64.b64encode((FIG / "mapa_dnbr_incendio_190.png").read_bytes()).decode()


def fmt(n):
    return f"{n:,.0f}".replace(",", " ")


filas_sens = "".join(
    f"<tr{' class=sel' if r.fecha_pre == dn['fecha_pre'] else ''}><td>{r.fecha_pre}</td><td>{r.fecha_post}</td>"
    f"<td>{r.ha_dnbr_027:.0f}</td><td>{r.ha_dnbr_010:.0f}</td></tr>" for r in sens.itertuples())

html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>¿A quién afectan los incendios?</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"></script>
<style>
:root {{ --crema:#F7F3EA; --carbon:#2B2B2B; --verde:#1F5F4A; --morado:#6A4C93; --linea:#e2dccf; --blanco:#fffdf8; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--crema); color:var(--carbon); font-family:system-ui,-apple-system,"Segoe UI",sans-serif; line-height:1.5; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:28px 16px 60px; }}
.eyebrow {{ color:var(--verde); font-weight:700; letter-spacing:.08em; text-transform:uppercase; font-size:.8rem; }}
h1 {{ color:var(--morado); font-size:clamp(1.7rem,4vw,2.6rem); margin:.2em 0 .3em; line-height:1.15; }}
h2 {{ color:var(--morado); margin:1.8em 0 .5em; font-size:1.35rem; }}
.lead {{ max-width:780px; font-size:1.05rem; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px; margin:22px 0; }}
.kpi {{ background:var(--blanco); border:1px solid var(--linea); border-top:4px solid var(--verde); border-radius:10px; padding:16px 18px; }}
.kpi.acento {{ border-top-color:var(--morado); }}
.kpi b {{ display:block; font-size:1.75rem; white-space:nowrap; color:var(--verde); line-height:1.1; }}
.kpi.acento b {{ color:var(--morado); }}
.kpi span {{ font-size:.92rem; }}
.card {{ background:var(--blanco); border:1px solid var(--linea); border-radius:10px; padding:16px; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
@media (max-width:820px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
#mapa {{ height:560px; border-radius:8px; }}
.ctrl {{ display:flex; flex-wrap:wrap; gap:18px; align-items:center; margin-bottom:10px; }}
.ctrl label {{ font-weight:600; }}
input[type=range] {{ accent-color:var(--verde); width:200px; }}
table {{ width:100%; border-collapse:collapse; font-size:.92rem; }}
th,td {{ padding:6px 8px; border-bottom:1px solid var(--linea); text-align:left; }}
th {{ color:var(--verde); }}
td.n,th.n {{ text-align:right; font-variant-numeric:tabular-nums; }}
tr.sel td {{ background:#efe8f6; font-weight:700; }}
.tabla-scroll {{ max-height:380px; overflow:auto; }}
.leyenda {{ background:var(--blanco); padding:8px 10px; border-radius:6px; font-size:.8rem; line-height:1.4; }}
.leyenda i {{ display:inline-block; width:14px; height:12px; margin-right:6px; vertical-align:middle; }}
img.full {{ width:100%; border-radius:8px; }}
ul.lim li {{ margin-bottom:.4em; }}
.nota {{ font-size:.85rem; color:#5a5a5a; }}
</style></head><body><div class="wrap">
<div class="eyebrow">Incendios en el Perú · opción D · focos VIIRS del 14 al 21 oct 2026</div>
<h1>¿A quién afectan los incendios activos?</h1>
<p class="lead">Personas que viven a <b>5 km o menos</b> de un incendio activo (con al menos un foco en las últimas 48 h), según WorldPop 2020,
y el área quemada de un incendio concreto, <b>Mazamari (Satipo, Junín)</b>, medida con Sentinel-2.</p>

<div class="kpis">
 <div class="kpi"><b>{fmt(res['personas_5km_vegetacion'])}</b><span>personas a ≤ 5 km de {res['incendios_activos_vegetacion']} incendios activos de vegetación ({str(res['pct_peru_vegetacion']).replace('.', ',')} % del Perú)</span></div>
 <div class="kpi acento"><b>{str(round(grad.personas_5km.iloc[0] / 1e6, 2)).replace('.', ',')} M → {grad.personas_5km.iloc[-1] / 1e3:.0f} mil</b><span>la cifra según la definición de «incendio»: todos los focos frente a solo los incendios de más de 100 ha</span></div>
 <div class="kpi"><b>{fmt(pdep.expuesta_5km.iloc[0])}</b><span>personas expuestas en {pdep.NOMBDEP.iloc[0].title()}, el departamento más afectado ({str(pdep.pct_expuesta.iloc[0]).replace('.', ',')} % de su población)</span></div>
 <div class="kpi acento"><b>{dn['ha_quemadas_dnbr_027']:.0f} ha</b><span>quemadas en Mazamari (dNBR ≥ 0,27), con {fmt(res['elegido']['personas_5km'])} personas a ≤ 5 km</span></div>
</div>

<h2>Mapa: distritos y personas expuestas</h2>
<div class="card">
 <div class="ctrl">
  <label for="minf">Mínimo de focos por incendio: <span id="minfv">1</span></label>
  <input id="minf" type="range" min="1" max="20" value="1">
  <label><input id="verurb" type="checkbox"> Mostrar fuentes urbanas/industriales excluidas</label>
  <span id="cuenta" class="nota"></span>
 </div>
 <div id="mapa"></div>
 <p class="nota">Color del distrito: personas a ≤ 5 km (sin las fuentes urbanas). Círculos: incendios activos, con tamaño según el número de focos. Haz clic en ellos para ver el detalle.</p>
</div>

<div class="grid2" style="margin-top:16px">
 <div class="card"><div id="g_dep" style="height:430px"></div></div>
 <div class="card"><div id="g_grad" style="height:430px"></div></div>
</div>

<h2>Incendios activos con más personas cerca</h2>
<div class="card tabla-scroll"><table id="tabla"><thead><tr><th>Distrito</th><th>Provincia</th><th>Departamento</th>
<th class="n">Focos</th><th class="n">Huella VIIRS (ha)</th><th class="n">Personas a ≤ 5 km</th></tr></thead><tbody></tbody></table></div>
<p class="nota">Las cifras por incendio se solapan entre vecinos y no se pueden sumar. El total nacional sí usa la unión de los radios de 5 km.</p>

<h2>Mazamari: ¿cuánto se quemó?</h2>
<div class="card"><img class="full" alt="dNBR de Mazamari: falso color antes, después y severidad" src="data:image/png;base64,{img}"></div>
<div class="grid2" style="margin-top:16px">
 <div class="card"><table><thead><tr><th>Imagen antes</th><th>Imagen después</th><th class="n">ha dNBR ≥ 0,27</th><th class="n">ha dNBR ≥ 0,10</th></tr></thead>
 <tbody>{filas_sens}</tbody></table>
 <p class="nota">En la zona de 1 km alrededor de los focos se enmascaró el {str(dn['pct_zona_enmascarada']).replace('.', ',')} % por nubes. La fila resaltada es la que se usó. Con la imagen del 8 oct se pierde la parte que ya ardía antes.</p></div>
 <div class="card"><b style="color:var(--morado)">¿Por qué Mazamari?</b>
 <p>Primero probé Cayna (Ambo, Huánuco), pero la única imagen posterior a su inicio (21 oct) estaba <b>100 % nublada</b>. De los incendios activos,
 solo Curahuasi y Mazamari habían quemado antes de una imagen limpia. Curahuasi era el ejemplo de la clase, así que elegí Mazamari.</p></div>
</div>

<h2>Limitaciones</h2>
<div class="card"><ul class="lim">
<li><b>Un foco de calor no es un incendio:</b> excluí la planta de gas de Pisco, otra fuente fija y 4 fuentes urbanas (Chimbote, Chincha, Pisco, Mollendo). Aun así, 172 incendios son de un solo foco, y varios focos costeros de una misma pasada podrían ser falsos positivos.</li>
<li><b>Las nubes esconden el fuego:</b> en la selva, un incendio puede no verse por días, ni en VIIRS ni en Sentinel-2.</li>
<li><b>Exposición no es daño:</b> vivir cerca no significa haber perdido algo. Los 5 km son una convención.</li>
<li>WorldPop 2020 es un modelo, no un censo. FIRMS de 7 días no ve el inicio de incendios más antiguos.</li>
</ul>
<p class="nota">Fuentes: NASA FIRMS VIIRS (S-NPP, NOAA-20, NOAA-21) · Sentinel-2 L2A (Microsoft Planetary Computer) · WorldPop 2020 1 km · INEI (juaneladio/peru-geojson).
Herramienta independiente: no reemplaza los reportes del COEN, INDECI, SERFOR ni SERNANP.</p></div>
</div>

<script>
const D = {json.dumps(datos, ensure_ascii=False)};
const fmt = n => Math.round(n).toLocaleString('es-PE').replace(/,/g, ' ');
const C = {{verde:'#1F5F4A', morado:'#6A4C93', carbon:'#2B2B2B', crema:'#F7F3EA'}};
const cortes = [100, 1000, 3000, 10000, 30000, 100000];
const colores = ['#ffffb2','#fed976','#feb24c','#fd8d3c','#f03b20','#bd0026','#800026'];
const color = v => colores[cortes.filter(c => v >= c).length];

const mapa = L.map('mapa', {{scrollWheelZoom:false}}).setView([-9.3, -75], 5);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',
  {{attribution:'Base: Esri, HERE, Garmin, © OpenStreetMap', maxZoom:16}}).addTo(mapa);
L.geoJSON(D.distritos, {{style: f => ({{fillColor:color(f.properties.expuesta_5km), fillOpacity:.75, color:'#999', weight:.4}}),
  onEachFeature:(f,l) => l.bindPopup(`<b>${{f.properties.NOMBDIST}}</b> (${{f.properties.NOMBPROV}}, ${{f.properties.NOMBDEP}})<br>`+
   `${{fmt(f.properties.expuesta_5km)}} personas a ≤ 5 km de ${{fmt(f.properties.poblacion)}} (${{f.properties.pct_expuesta}} %)`)}}).addTo(mapa);
L.geoJSON(D.departamentos, {{style:{{fill:false, color:C.carbon, weight:1}}, interactive:false}}).addTo(mapa);
const leyenda = L.control({{position:'bottomright'}});
leyenda.onAdd = () => {{ const d = L.DomUtil.create('div','leyenda');
  d.innerHTML = '<b>Personas a ≤ 5 km</b><br>' + colores.map((c,i) =>
    `<i style="background:${{c}}"></i>${{i===0?'< 100':(i===colores.length-1?'≥ '+fmt(cortes[i-1]):fmt(cortes[i-1])+' – '+fmt(cortes[i]))}}`).join('<br>');
  return d; }};
leyenda.addTo(mapa);

const capa = L.layerGroup().addTo(mapa);
function dibujar() {{
  const minf = +document.getElementById('minf').value, urb = document.getElementById('verurb').checked;
  document.getElementById('minfv').textContent = minf;
  capa.clearLayers();
  const sel = D.incendios.filter(f => f.n_focos >= minf && (urb || !f.urbano));
  sel.forEach(f => L.circleMarker([f.lat, f.lon], {{radius: 3 + Math.sqrt(f.n_focos)*1.6,
      color: f.urbano ? C.morado : (f.incendio_id === 190 ? C.morado : C.verde), weight: f.incendio_id === 190 ? 3 : 1.5,
      fillColor: f.urbano ? C.morado : C.verde, fillOpacity:.25}})
    .bindPopup(`<b>${{f.distrito}}</b>, ${{f.provincia}} (${{f.departamento}})${{f.urbano?'<br><i>Fuente urbana/industrial (excluida)</i>':''}}<br>`+
      `${{f.n_focos}} focos · huella VIIRS ${{fmt(f.huella_ha)}} ha<br><b>${{fmt(f.pob_5km)}} personas a ≤ 5 km</b><br>`+
      `<span style="font-size:.85em">${{f.inicio}} → ${{f.ultimo}} UTC</span>`).addTo(capa));
  document.getElementById('cuenta').textContent = `${{sel.length}} incendios en el mapa`;
  const tb = document.querySelector('#tabla tbody');
  tb.innerHTML = sel.filter(f => !f.urbano).sort((a,b) => b.pob_5km - a.pob_5km).slice(0, 40).map(f =>
    `<tr${{f.incendio_id===190?' class=sel':''}}><td>${{f.distrito}}</td><td>${{f.provincia}}</td><td>${{f.departamento}}</td>`+
    `<td class=n>${{f.n_focos}}</td><td class=n>${{fmt(f.huella_ha)}}</td><td class=n>${{fmt(f.pob_5km)}}</td></tr>`).join('');
}}
document.getElementById('minf').oninput = dibujar;
document.getElementById('verurb').onchange = dibujar;
dibujar();

const lay = t => ({{title:{{text:t, font:{{color:C.morado, size:15}}, x:0}}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
  font:{{color:C.carbon, family:'system-ui'}}, margin:{{l:110, r:20, t:50, b:60}}}});
const dep = [...D.dep].reverse();
Plotly.newPlot('g_dep', [{{type:'bar', orientation:'h', y:dep.map(d => d.NOMBDEP), x:dep.map(d => d.expuesta_5km),
  marker:{{color:C.verde}}, customdata:dep.map(d => [d.pct_expuesta, d.incendios_activos]),
  hovertemplate:'%{{y}}<br>%{{x:,.0f}} personas (%{{customdata[0]}} %)<br>%{{customdata[1]}} incendios activos<extra></extra>'}}],
  {{...lay('Personas a ≤ 5 km por departamento'), xaxis:{{title:'personas'}}}}, {{displayModeBar:false, responsive:true}});
Plotly.newPlot('g_grad', [{{type:'bar', x:['Todos los<br>focos activos','Sin fuentes<br>urbanas','Y con<br>≥ 3 focos','Y con huella<br>> 100 ha'], y:D.grad.map(g => g.personas_5km),
  marker:{{color:D.grad.map((g,i) => i===0 ? C.morado : C.verde)}}, text:D.grad.map(g => fmt(g.personas_5km)), textposition:'outside',
  customdata:D.grad.map(g => g.incendios), hovertemplate:'%{{x}}<br>%{{y:,.0f}} personas · %{{customdata}} incendios<extra></extra>'}}],
  {{...lay('El número depende de qué llamamos «incendio»'), margin:{{l:60, r:20, t:50, b:90}}, yaxis:{{title:'personas', range:[0, 1350000]}}}},
  {{displayModeBar:false, responsive:true}});
</script></body></html>"""
(OUT / "index.html").write_text(html, encoding="utf-8")
print(f"Dashboard: {OUT / 'index.html'} ({len(html) / 1e6:.1f} MB)")
