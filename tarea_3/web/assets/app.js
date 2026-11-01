/* Dashboard «¿Quién sostiene el fisco peruano?» — datos en data/*.json, generados por scripts/analizar_datos.py */

const NORDICOS = ["DNK", "FIN", "NOR", "SWE", "ISL"];
const GRUPOS = { OCDE: "Promedio OCDE", ALC: "Promedio ALC", NOR: "Promedio nórdico" };

const INDICADORES = {
  presion_tributaria: { lab: "Presión tributaria", u: "% del PIB",
    desc: "Recaudación tributaria total del gobierno general (incluye contribuciones sociales) como porcentaje del PIB." },
  iva_pct: { lab: "Peso del IVA/IGV en la recaudación", u: "% del total",
    desc: "Qué parte de la recaudación total proviene del impuesto al valor agregado (en el Perú, el IGV), que pagan todos al consumir." },
  renta_personas_pib: { lab: "Impuesto a la renta de personas", u: "% del PIB",
    desc: "Recaudación del impuesto a la renta de las personas (código OCDE 1100). Es el impuesto que más puede crecer con el ingreso." },
  renta_empresas_pct: { lab: "Peso de la renta de empresas", u: "% del total",
    desc: "Qué parte de la recaudación proviene del impuesto a la renta de las empresas (1200). En el Perú depende mucho de la minería." },
  propiedad_pib: { lab: "Impuestos a la propiedad", u: "% del PIB",
    desc: "Predial, patrimonio, herencias y transacciones financieras (código 4000), como porcentaje del PIB." },
  ratio_directos_indirectos: { lab: "Ratio directos / indirectos", u: "veces",
    desc: "(Renta + propiedad) ÷ bienes y servicios. Mayor a 1 = se recauda más con impuestos directos que con impuestos al consumo." },
  gasto_social_pib: { lab: "Gasto social público", u: "% del PIB",
    desc: "Gasto social público total (pensiones, salud, familias, desempleo, etc.), metodología SOCX de la OCDE. Perú desde 2012; sin promedio ALC." },
};

const COMPOSICION = [
  ["renta_personas_pct", "Renta de personas", "--c1"],
  ["renta_empresas_pct", "Renta de empresas", "--c2"],
  ["renta_otra", "Renta no asignable", "--c3"],
  ["contrib_seg_social_pct", "Contribuciones sociales", "--c4"],
  ["iva_pct", "IVA / IGV", "--c5"],
  ["bys_otros", "Otros impuestos al consumo", "--c6"],
  ["resto", "Propiedad y otros", "--c7"],
];

const DISP_LAB = {
  presion_tributaria: "Presión tributaria (% PIB)", gasto_social_pib: "Gasto social público (% PIB)",
  renta_personas_pib: "Renta de personas (% PIB)", iva_pct: "IVA/IGV (% de la recaudación)",
  ratio_directos_indirectos: "Ratio directos / indirectos", gini_bm: "Índice de Gini",
  top10_ingreso: "Ingreso del 10 % más rico (%)", top1_riqueza: "Riqueza del 1 % más rico (%)",
};

const PAISES_INICIALES = ["CHL", "COL", "BRA", "DNK", "SWE"];
const estado = { anio: 2023, grupo: "OCDE", indicador: "presion_tributaria", paises: [...PAISES_INICIALES],
  x: "presion_tributaria", y: "gini_bm" };
let PANEL = [], CX = [], IND = {}, POR = new Map();

const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt = (v, d = 1) => (v == null || Number.isNaN(v) ? "s. d." : v.toLocaleString("es-PE", { minimumFractionDigits: d, maximumFractionDigits: d }));
const fila = (iso, anio) => POR.get(iso + "|" + anio);

function val(iso, anio, col) {
  if (iso === "NOR") {
    const xs = NORDICOS.map((i) => val(i, anio, col)).filter((v) => v != null);
    return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;
  }
  const code = iso === "ALC" ? "A9" : iso === "OCDE" ? "OECD_REP" : iso;
  const f = fila(code, anio);
  if (!f) return null;
  if (["renta_otra", "bys_otros", "resto"].includes(col) && (f.renta_pct == null || f.bienes_servicios_pct == null)) return null;
  if (col === "renta_otra") return f.renta_pct - (f.renta_personas_pct ?? 0) - (f.renta_empresas_pct ?? 0);
  if (col === "bys_otros") return f.bienes_servicios_pct - (f.iva_pct ?? 0);
  if (col === "resto") {
    const usados = ["renta_pct", "contrib_seg_social_pct", "bienes_servicios_pct"].map((c) => f[c] ?? 0);
    return 100 - usados.reduce((a, b) => a + b, 0);
  }
  return f[col];
}

function baseLayout(extra = {}) {
  return Object.assign({
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "Inter, system-ui, sans-serif", color: css("--ink"), size: 12 },
    margin: { l: 50, r: 16, t: 10, b: 40 },
    xaxis: { gridcolor: css("--line"), zerolinecolor: css("--line"), linecolor: css("--line") },
    yaxis: { gridcolor: css("--line"), zerolinecolor: css("--line"), linecolor: css("--line") },
    hoverlabel: { bgcolor: css("--surface"), bordercolor: css("--line"), font: { color: css("--ink") } },
    legend: { orientation: "h", y: -0.18, x: 0 },
  }, extra);
}
const CONFIG = { displaylogo: false, responsive: true, modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"] };

/* ---------- KPIs ---------- */
function kpis() {
  const a = estado.anio, g = estado.grupo, gl = GRUPOS[g];
  const defs = [
    ["presion_tributaria", "Presión tributaria del Perú", "% PIB"],
    ["iva_pct", "Parte de la recaudación que viene del IGV", "% total"],
    ["renta_personas_pib", "Impuesto a la renta de personas", "% PIB"],
    ["gasto_social_pib", "Gasto social público", "% PIB"],
  ];
  document.getElementById("kpis").innerHTML = defs.map(([col, lab, u]) => {
    const p = val("PER", a, col), c = val(g, a, col);
    let cmp = `${gl}: <b>sin dato en ${a}</b>`;
    if (p != null && c != null) {
      const d = p - c;
      cmp = `${gl}: <b>${fmt(c)}</b> · diferencia <b>${d > 0 ? "+" : ""}${fmt(d)} p.p.</b>`;
    }
    const max = Math.max(p ?? 0, c ?? 0) * 1.15 || 1;
    const barra = p != null ? `<div class="barra" aria-hidden="true"><i style="width:${(p / max) * 100}%"></i>${c != null ? `<em style="left:${(c / max) * 100}%"></em>` : ""}</div>` : "";
    return `<article class="kpi"><div class="k-lab">${lab} (${a})</div>
      <div class="k-val">${fmt(p)}<small> ${u}</small></div><div class="k-cmp">${cmp}</div>${barra}</article>`;
  }).join("");
}

/* ---------- Mapa ---------- */
function mapa() {
  const ind = INDICADORES[estado.indicador];
  const filas = PANEL.filter((f) => f.anio === estado.anio && f.iso3.length === 3 && f[estado.indicador] != null);
  const seq = css("--seq").replace(/"/g, "").split(",");
  const escala = seq.map((c, i) => [i / (seq.length - 1), c.trim()]);
  document.getElementById("t-mapa").textContent = `${ind.lab} (${ind.u}), ${estado.anio}`;
  const tr = [{
    type: "choropleth", locations: filas.map((f) => f.iso3), z: filas.map((f) => f[estado.indicador]),
    text: filas.map((f) => f.pais), colorscale: escala,
    marker: { line: { color: filas.map((f) => (f.iso3 === "PER" ? css("--accent") : css("--surface"))), width: filas.map((f) => (f.iso3 === "PER" ? 2.5 : 0.5)) } },
    colorbar: { thickness: 10, len: 0.7, outlinewidth: 0, tickfont: { color: css("--ink-2") }, title: { text: ind.u, side: "right", font: { size: 11 } } },
    hovertemplate: `<b>%{text}</b><br>${ind.lab}: %{z:.1f} ${ind.u}<extra></extra>`,
  }];
  const lay = baseLayout({ margin: { l: 0, r: 0, t: 0, b: 0 },
    geo: { projection: { type: "natural earth" }, showframe: false, showcoastlines: false, bgcolor: "rgba(0,0,0,0)",
      landcolor: css("--surface-2"), showland: true, showcountries: true, countrycolor: css("--line"),
      lataxis: { range: [-58, 72] }, lonaxis: { range: [-125, 45] } } });
  Plotly.react("g-mapa", tr, lay, CONFIG);
}

/* ---------- Serie de tiempo ---------- */
function serie() {
  const ind = INDICADORES[estado.indicador], anios = [...Array(25).keys()].map((i) => 2000 + i);
  document.getElementById("t-serie").textContent = `${ind.lab} (${ind.u}), 2000–2024`;
  const series = [["PER", "Perú", "--accent", 3], ["ALC", "Promedio ALC", "--g-alc", 2],
    ["OCDE", "Promedio OCDE", "--g-ocde", 2], ["NOR", "Promedio nórdico", "--g-nor", 2]];
  const tr = series.map(([iso, nom, col, w]) => ({
    x: anios, y: anios.map((a) => val(iso, a, estado.indicador)), name: nom, mode: "lines+markers", connectgaps: false,
    line: { color: css(col), width: w }, marker: { size: iso === "PER" ? 6 : 4 },
    hovertemplate: `${nom}: %{y:.1f}<extra></extra>`,
  }));
  const lay = baseLayout({ hovermode: "x unified", yaxis: { title: { text: ind.u }, gridcolor: css("--line"), rangemode: "tozero" },
    shapes: [{ type: "line", x0: estado.anio, x1: estado.anio, yref: "paper", y0: 0, y1: 1, line: { color: css("--muted"), dash: "dot", width: 1 } }] });
  Plotly.react("g-serie", tr, lay, CONFIG);
}

/* ---------- Composición ---------- */
function composicion() {
  const lista = ["PER", "ALC", "OCDE", "NOR", ...estado.paises];
  const nombre = (iso) => GRUPOS[iso] || fila(iso, estado.anio)?.pais || PANEL.find((f) => f.iso3 === iso)?.pais || iso;
  const etiquetas = lista.map(nombre).reverse();
  const tr = COMPOSICION.map(([col, lab, color]) => ({
    type: "bar", orientation: "h", name: lab, y: etiquetas,
    x: lista.map((iso) => { const v = val(iso, estado.anio, col); return v != null ? Math.max(v, 0) : null; }).reverse(),
    marker: { color: css(color), line: { color: css("--surface"), width: 2 } },
    hovertemplate: `%{y}<br>${lab}: %{x:.1f} % del total<extra></extra>`,
  }));
  const lay = baseLayout({ barmode: "stack", margin: { l: 130, r: 16, t: 10, b: 40 },
    xaxis: { range: [0, 100], ticksuffix: " %", gridcolor: css("--line") },
    yaxis: { tickfont: { size: 12 } }, legend: { orientation: "h", y: -0.12, x: 0, traceorder: "normal" } });
  Plotly.react("g-comp", tr, lay, CONFIG);
  chips();
}

function chips() {
  const fijos = ["Perú", "Promedio ALC", "Promedio OCDE", "Promedio nórdico"].map((n) => `<span class="chip fijo">${n}</span>`);
  const vars = estado.paises.map((iso) => {
    const n = PANEL.find((f) => f.iso3 === iso)?.pais || iso;
    return `<span class="chip">${n}<button type="button" data-quitar="${iso}" aria-label="Quitar ${n}">×</button></span>`;
  });
  document.getElementById("chips").innerHTML = fijos.concat(vars).join("");
}

function agregarPais(iso) {
  if (!iso || iso === "PER" || estado.paises.includes(iso)) return;
  estado.paises.push(iso);
  if (estado.paises.length > 8) estado.paises.shift();
  composicion(); tabla();
}

/* ---------- Ranking ---------- */
function ranking() {
  const ind = INDICADORES[estado.indicador];
  document.getElementById("t-rank").textContent = `${ind.lab} (${ind.u}), ${estado.anio}`;
  const filas = PANEL.filter((f) => f.anio === estado.anio && f[estado.indicador] != null &&
    ["Perú", "América Latina y el Caribe", "Nórdicos", "Promedio"].includes(f.grupo))
    .sort((a, b) => a[estado.indicador] - b[estado.indicador]);
  const color = (f) => f.iso3 === "PER" ? css("--accent") : f.grupo === "Nórdicos" ? css("--g-nor") : f.grupo === "Promedio" ? css("--ink") : css("--g-alc");
  const tr = [{
    type: "bar", orientation: "h", y: filas.map((f) => f.pais), x: filas.map((f) => f[estado.indicador]),
    marker: { color: filas.map(color), line: { color: css("--surface"), width: 1 } },
    text: filas.map((f) => fmt(f[estado.indicador])), textposition: "outside", cliponaxis: false,
    textfont: { color: css("--ink-2"), size: 11 },
    hovertemplate: `<b>%{y}</b><br>${ind.lab}: %{x:.1f} ${ind.u}<extra></extra>`,
  }];
  const lay = baseLayout({ margin: { l: 150, r: 40, t: 10, b: 30 }, showlegend: false,
    xaxis: { title: { text: ind.u }, gridcolor: css("--line") }, yaxis: { automargin: true, tickfont: { size: 11 } },
    annotations: filas.length ? [] : [{ text: "Sin datos para este año", showarrow: false, xref: "paper", yref: "paper", x: 0.5, y: 0.5 }] });
  Plotly.react("g-rank", tr, lay, CONFIG);
}

/* ---------- Dispersión ---------- */
function rangos(xs) {
  const idx = xs.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]), r = Array(xs.length);
  for (let i = 0; i < idx.length;) {
    let j = i; while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++;
    for (let k = i; k <= j; k++) r[idx[k][1]] = (i + j) / 2 + 1;
    i = j + 1;
  }
  return r;
}
function spearman(xs, ys) {
  const rx = rangos(xs), ry = rangos(ys), n = xs.length, mx = (n + 1) / 2;
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) { num += (rx[i] - mx) * (ry[i] - mx); dx += (rx[i] - mx) ** 2; dy += (ry[i] - mx) ** 2; }
  return num / Math.sqrt(dx * dy);
}

function dispersion() {
  const { x, y } = estado, datos = CX.filter((d) => d[x] != null && d[y] != null);
  const grupos = [["América Latina y el Caribe", "--g-alc"], ["OCDE (otros)", "--g-ocde"], ["Nórdicos", "--g-nor"], ["Perú", "--accent"]];
  const tr = grupos.map(([g, col]) => {
    const d = datos.filter((r) => r.grupo === g);
    return { type: "scatter", mode: g === "Perú" ? "markers+text" : "markers", name: g === "OCDE (otros)" ? "Otros OCDE" : g,
      x: d.map((r) => r[x]), y: d.map((r) => r[y]), text: d.map((r) => r.pais), textposition: "top center",
      textfont: { color: css("--ink"), size: 13 },
      marker: { color: css(col), size: g === "Perú" ? 16 : 10, line: { color: css("--surface"), width: 2 } },
      hovertemplate: `<b>%{text}</b><br>${DISP_LAB[x]}: %{x:.2f}<br>${DISP_LAB[y]}: %{y:.1f}<extra></extra>` };
  });
  const rho = datos.length > 3 ? spearman(datos.map((d) => d[x]), datos.map((d) => d[y])) : null;
  document.getElementById("t-disp").textContent = `${DISP_LAB[x]} y ${DISP_LAB[y].toLowerCase()}`;
  document.getElementById("s-disp").textContent = rho == null ? "Muy pocos países con ambos datos."
    : `Correlación de Spearman ρ = ${fmt(rho, 2)} con ${datos.length} países. Es asociación, no causalidad: los países más ricos suelen recaudar más y ser menos desiguales.`;
  const lay = baseLayout({ xaxis: { title: { text: DISP_LAB[x] }, gridcolor: css("--line") },
    yaxis: { title: { text: DISP_LAB[y] }, gridcolor: css("--line") }, legend: { orientation: "h", y: -0.2, x: 0 } });
  Plotly.react("g-disp", tr, lay, CONFIG);
}

/* ---------- Desigualdad WID ---------- */
function wid() {
  const medidas = [["top1_riqueza", "Riqueza del 1 % más rico"], ["top10_ingreso", "Ingreso del 10 % más rico"],
    ["bottom50_ingreso", "Ingreso del 50 % más pobre"]];
  const per = CX.find((d) => d.iso3 === "PER"), nor = CX.filter((d) => NORDICOS.includes(d.iso3));
  const lat = CX.filter((d) => d.grupo === "América Latina y el Caribe" && d.top10_ingreso != null);
  const prom = (arr, c) => { const v = arr.map((d) => d[c]).filter((z) => z != null); return v.reduce((a, b) => a + b, 0) / v.length; };
  const tr = [["Perú", (c) => per[c], "--accent"], [`Otros 9 de ALC (promedio)`, (c) => prom(lat, c), "--g-alc"],
    ["Nórdicos (promedio)", (c) => prom(nor, c), "--g-nor"]].map(([nom, f, col]) => ({
    type: "bar", name: nom, x: medidas.map((m) => m[1]), y: medidas.map((m) => f(m[0])),
    marker: { color: css(col), line: { color: css("--surface"), width: 2 } },
    text: medidas.map((m) => fmt(f(m[0])) + " %"), textposition: "outside", cliponaxis: false, textfont: { color: css("--ink-2") },
    hovertemplate: `${nom}<br>%{x}: %{y:.1f} %<extra></extra>`,
  }));
  const lay = baseLayout({ barmode: "group", bargap: 0.25, yaxis: { ticksuffix: " %", gridcolor: css("--line"), range: [0, 85] } });
  Plotly.react("g-wid", tr, lay, CONFIG);
}

/* ---------- Hallazgos (cifras leídas de indicadores.json) ---------- */
function hallazgos() {
  const r = IND, p = r.presion_tributaria, iv = r.iva_pct, rp = r.renta_personas_pib, gs = r.gasto_social_pib;
  const d = r.desigualdad_PER_2019_2023, dn = r.desigualdad_nordicos_2019_2023;
  const cp = r.correlaciones_parciales_lnPIBpc, cs = r.correlaciones_spearman;
  const items = [
    { num: `${fmt(r.igv_sobre_renta_personas_PER)}×`, t: "El IGV sostiene más que la renta de las personas",
      p: `En ${r.anio_referencia}, el Perú recaudó ${fmt(p.PER)} % del PIB (ALC: ${fmt(p.ALC)} %; OCDE: ${fmt(p.OCDE)} %; nórdicos: ${fmt(p.Nordicos)} %), puesto ${r.ranking_presion_alc.puesto} de ${r.ranking_presion_alc.de} en ALC. El IGV aportó ${fmt(iv.PER)} % de la recaudación (OCDE: ${fmt(iv.OCDE)} %) y recaudó ${fmt(r.igv_sobre_renta_personas_PER)} veces lo que el impuesto a la renta de personas (${fmt(rp.PER, 2)} % del PIB frente a ${fmt(rp.OCDE)} % en la OCDE). Lo «directo» viene de la renta de empresas (${fmt(r.renta_empresas_pct.PER)} % del total), muy ligada a la minería.`,
      f: "OCDE, Global Revenue Statistics (2026)." },
    { num: `${fmt(d.top1_riqueza, 0)} %`, t: "Riqueza muy concentrada y poco gravada",
      p: `Según WID.world (promedio 2019–2023), el 1 % más rico del Perú tiene ${fmt(d.top1_riqueza)} % de la riqueza neta y el 10 % más rico ${fmt(d.top10_riqueza)} % (nórdicos: ${fmt(dn.top1_riqueza)} % y ${fmt(dn.top10_riqueza)} %). El 50 % de menores ingresos recibe ${fmt(d.bottom50_ingreso)} % del ingreso (nórdicos: ${fmt(dn.bottom50_ingreso)} %). Los impuestos a la propiedad recaudan ${fmt(r.propiedad_pib.PER, 2)} % del PIB (OCDE: ${fmt(r.propiedad_pib.OCDE, 2)} %).`,
      f: "WID.world; OCDE. Las estimaciones de WID son superiores a las oficiales (ver Alarco et al., 2019; Francke, 2017)." },
    { num: `${fmt(gs.PER)} %`, t: "Poco gasto social; importa cuánto se recauda y gasta",
      p: `El gasto social público del Perú fue ${fmt(gs.PER)} % del PIB en ${r.anio_referencia} (OCDE: ${fmt(gs.OCDE)} %; nórdicos: ${fmt(gs.Nordicos)} %). Entre ${cs["presion_tributaria~gini_bm"].n} países, a mayor presión tributaria, menor Gini (ρ = ${fmt(cs["presion_tributaria~gini_bm"].rho, 2)}); la asociación se mantiene al controlar por PIB per cápita (ρ parcial = ${fmt(cp["presion_tributaria~gini_bm"].rho, 2)}) y también para el gasto social (ρ parcial = ${fmt(cp["gasto_social_pib~gini_bm"].rho, 2)}). En cambio, la de la renta de personas desaparece (ρ parcial = ${fmt(cp["renta_personas_pib~gini_bm"].rho, 2)}, no significativa).`,
      f: "OCDE SOCX; Banco Mundial; cálculos propios. Asociación, no causalidad (ver Jaramillo, 2013)." },
  ];
  document.getElementById("lista-hallazgos").innerHTML = items.map((h) =>
    `<article class="hallazgo"><div class="num">${h.num}</div><h3>${h.t}</h3><p>${h.p}</p><div class="fuente">Fuente: ${h.f}</div></article>`).join("");
  document.getElementById("hero-veces").textContent = `${fmt(r.igv_sobre_renta_personas_PER)}×`;
  document.getElementById("hero-txt").textContent = `En ${r.anio_referencia}, el IGV recaudó ${fmt(r.igv_sobre_renta_personas_PER)} veces lo que el impuesto a la renta de las personas. En el promedio OCDE ocurre lo contrario: la renta de personas (${fmt(r.renta_personas_pib.OCDE)} % del PIB) supera al IVA (${fmt(r.iva_pib.OCDE)} %).`;
}

/* ---------- Tabla y descarga ---------- */
const COLS_TABLA = [["pais", "País"], ["grupo", "Grupo"], ["presion_tributaria", "Presión trib. % PIB"],
  ["renta_personas_pib", "Renta personas % PIB"], ["renta_empresas_pct", "Renta empresas % total"],
  ["iva_pct", "IVA/IGV % total"], ["propiedad_pib", "Propiedad % PIB"], ["ratio_directos_indirectos", "Directos/indirectos"],
  ["gasto_social_pib", "Gasto social % PIB"], ["gini_bm", "Gini"]];
function filasTabla() {
  return PANEL.filter((f) => f.anio === estado.anio).sort((a, b) => (b.presion_tributaria ?? -1) - (a.presion_tributaria ?? -1));
}
function tabla() {
  const filas = filasTabla();
  document.getElementById("tabla").innerHTML = `<thead><tr>${COLS_TABLA.map((c) => `<th>${c[1]}</th>`).join("")}</tr></thead><tbody>` +
    filas.map((f) => `<tr class="${f.iso3 === "PER" ? "peru" : ""}">${COLS_TABLA.map(([c], i) =>
      `<td>${i < 2 ? f[c] : fmt(f[c], c === "ratio_directos_indirectos" ? 2 : 1)}</td>`).join("")}</tr>`).join("") + "</tbody>";
}
function descargar() {
  const filas = filasTabla(), cols = ["iso3", "anio", ...COLS_TABLA.map((c) => c[0])];
  const csv = [cols.join(",")].concat(filas.map((f) => cols.map((c) => (f[c] == null ? "" : `"${String(f[c]).replace(/"/g, '""')}"`)).join(","))).join("\n");
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(new Blob(["﻿" + csv], { type: "text/csv" })), download: `fisco_${estado.anio}.csv` });
  a.click(); URL.revokeObjectURL(a.href);
}

/* ---------- Orquestación ---------- */
function todo() { kpis(); mapa(); serie(); composicion(); ranking(); dispersion(); wid(); tabla(); }

async function iniciar() {
  const [panel, cx, ind] = await Promise.all(["data/panel.json", "data/corte_transversal.json", "data/indicadores.json"]
    .map((u) => fetch(u).then((r) => r.json())));
  PANEL = panel; CX = cx; IND = ind;
  PANEL.forEach((f) => POR.set(f.iso3 + "|" + f.anio, f));

  const sel = document.getElementById("indicador");
  sel.innerHTML = Object.entries(INDICADORES).map(([k, v]) => `<option value="${k}">${v.lab} (${v.u})</option>`).join("");
  const paises = [...new Map(PANEL.filter((f) => f.iso3.length === 3 && f.iso3 !== "PER").map((f) => [f.iso3, f.pais])).entries()]
    .sort((a, b) => a[1].localeCompare(b[1], "es"));
  document.getElementById("agregar-pais").innerHTML += paises.map(([i, n]) => `<option value="${i}">${n}</option>`).join("");

  const anio = document.getElementById("anio");
  anio.addEventListener("input", () => { estado.anio = +anio.value; document.getElementById("anio-out").textContent = anio.value;
    kpis(); mapa(); serie(); composicion(); ranking(); tabla(); });
  document.getElementById("grupo").addEventListener("change", (e) => { estado.grupo = e.target.value; kpis(); });
  sel.addEventListener("change", (e) => { estado.indicador = e.target.value; descInd(); mapa(); serie(); ranking(); });
  document.getElementById("x-disp").addEventListener("change", (e) => { estado.x = e.target.value; dispersion(); });
  document.getElementById("y-disp").addEventListener("change", (e) => { estado.y = e.target.value; dispersion(); });
  document.getElementById("agregar-pais").addEventListener("change", (e) => { agregarPais(e.target.value); e.target.value = ""; });
  document.getElementById("reset-paises").addEventListener("click", () => { estado.paises = [...PAISES_INICIALES]; composicion(); });
  document.getElementById("chips").addEventListener("click", (e) => {
    const iso = e.target.dataset?.quitar; if (!iso) return;
    estado.paises = estado.paises.filter((p) => p !== iso); composicion();
  });
  document.getElementById("descargar").addEventListener("click", descargar);
  document.getElementById("tema").addEventListener("click", () => {
    const html = document.documentElement, oscuro = getComputedStyle(html).colorScheme === "dark";
    html.dataset.theme = oscuro ? "light" : "dark";
    try { localStorage.setItem("tema", html.dataset.theme); } catch (e) { /* sin almacenamiento */ }
    todo();
  });

  descInd(); hallazgos(); todo();
  document.getElementById("g-mapa").on("plotly_click", (ev) => agregarPais(ev.points?.[0]?.location));
}
function descInd() { document.getElementById("ind-desc").textContent = INDICADORES[estado.indicador].desc; }

try { const t = localStorage.getItem("tema"); if (t) document.documentElement.dataset.theme = t; } catch (e) { /* sin almacenamiento */ }
iniciar();
