// Ejecuta evals/casos.json contra la logica REAL de index.html (sin navegador) y escribe un informe.
// Mide lo que el usuario VE en pantalla (texto pintado por renderFreeResult). Si freeSearch devuelve 'none', el navegador real
// lanzaria la IA semantica (no ejecutable aqui): se cuenta como fallo de las reglas.
// Uso:  node evals/run_evals.js [ruta/a/otro_index.html]
// Salida: evals/resultados.json, evals/informe.md  (y compara con la ejecucion anterior para detectar regresiones)
// OJO: solo mide las busquedas por REGLAS (freeSearch). La busqueda semantica con IA del navegador no se puede ejecutar aqui,
//      asi que los casos "none" podrian rescatarse en el navegador real.
const fs = require('fs');
const path = require('path');
const { cargar } = require('./buscador_headless');

const dir = __dirname;
const casos = JSON.parse(fs.readFileSync(path.join(dir, 'casos.json'), 'utf8'));
const b = cargar(process.argv[2] ? path.resolve(process.argv[2]) : undefined);
if (b.errores.length) console.error('Avisos al cargar el buscador:', b.errores.slice(0, 3));

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
function menciona(texto, esperado) {
  if (esperado.startsWith('nombre:')) {  // nombre de familia ("AD HSD 0W20"): se compara sin espacios ni mayusculas
    const n = (x) => x.replace(/\s+/g, '').toUpperCase();
    return n(texto).includes(n(esperado.slice(7)));
  }
  const refs = [esperado, 'ADP' + esperado];  // "61005" tambien se acepta como "ADP61005" (asi lo muestra la pantalla)
  return refs.some((v) => new RegExp('(?<![0-9A-Za-z.])' + esc(v) + '(?![0-9A-Za-z])', 'i').test(texto));
}

const normRef = (x) => String(x == null ? '' : x).toUpperCase().replace(/[\s\-.]/g, '').replace(/^(ADP|ADS|CAT|REP|SHE|ENI|FEB|TCM)(?=\d|[A-Z]\d)/, '');
function refsDe(obj, out = []) {  // todas las referencias ("ref") que muestra el resultado de referencias cruzadas
  if (Array.isArray(obj)) obj.forEach((o) => refsDe(o, out));
  else if (obj && typeof obj === 'object') { if (obj.ref != null) out.push(normRef(obj.ref)); Object.values(obj).forEach((v) => typeof v === 'object' && refsDe(v, out)); }
  return out;
}

process.on('unhandledRejection', () => {});  // la IA semantica (sin red) rechaza su promesa: se ignora
const t0 = Date.now();
const res = casos.map((c) => {
  let r, error = null, texto = '';
  const xref = c.herramienta === 'xref';
  try { r = xref ? b.crossReferenceSearch(c.consulta) : b.freeSearch(c.consulta); } catch (e) { error = e.message; }
  let tipo = error ? 'ERROR' : xref ? (r ? (r.noBridgeFound ? 'sin_cruce' : 'cruce') : 'none') : (r && r.match) || 'null';
  let halladas = [];
  if (!error && xref && r) {
    const refs = refsDe(r.matches || r);
    halladas = c.esperado.filter((e) => refs.includes(normRef(e)));
    if (c.modo === 'propia') halladas = refs.includes(normRef(c.consulta)) ? [c.consulta] : [];
  } else if (!error && !xref) {
    const v = c.herramienta === 'homologaciones' ? b.buscarHomologacion(c.consulta) : b.buscarLibre(c.consulta);  // flujo completo de la pestaña (incluye, en la rama puente, el paso por referencias cruzadas)
    if (v.error) error = 'al pintar: ' + v.error;
    // lo que el usuario VE, sin el eco de su propia consulta (para que repetir lo escrito no cuente como acierto)
    texto = v.texto.replace(new RegExp('(?<![0-9A-Za-z])' + esc(c.consulta) + '(?![0-9A-Za-z])', 'ig'), ' ');
    halladas = error ? [] : c.esperado.filter((e) => menciona(texto, e));
  }
  const ok = c.modo === 'todos' ? halladas.length === c.esperado.length : halladas.length > 0;
  return { id: c.id, categoria: c.categoria, herramienta: c.herramienta || 'libre', consulta: c.consulta, ok, tipo, esperadas: c.esperado.length, halladas: halladas.length, error };
});

const previo = fs.existsSync(path.join(dir, 'resultados.json')) ? JSON.parse(fs.readFileSync(path.join(dir, 'resultados.json'), 'utf8')) : null;
fs.writeFileSync(path.join(dir, 'resultados.json'), JSON.stringify(res, null, 1));

const cats = [...new Set(res.map((r) => r.categoria))];
const pct = (a, n) => (n ? ((100 * a) / n).toFixed(1) + ' %' : '-');
let md = `# Informe de pruebas del buscador (${new Date().toISOString().slice(0, 10)})\n\n`;
md += `Casos: ${res.length} · acierto global: **${pct(res.filter((r) => r.ok).length, res.length)}** · tiempo: ${((Date.now() - t0) / 1000).toFixed(1)} s\n\n`;
md += `Mide solo las búsquedas por reglas del buscador (la IA semántica del navegador no se ejecuta aquí). Un caso es acierto si la respuesta menciona alguna de las referencias esperadas.\n\n`;
md += `| Herramienta | Categoría | Casos | Aciertos | % | "none" | Errores |\n|---|---|---|---|---|---|\n`;
for (const c of cats) {
  const rs = res.filter((r) => r.categoria === c);
  md += `| ${({ xref: 'referencias cruzadas', homologaciones: 'homologaciones' })[rs[0].herramienta] || 'búsqueda libre'} | ${c} | ${rs.length} | ${rs.filter((r) => r.ok).length} | ${pct(rs.filter((r) => r.ok).length, rs.length)} | ${rs.filter((r) => r.tipo === 'none').length} | ${rs.filter((r) => r.error).length} |\n`;
}
if (previo) {
  const antes = new Map(previo.map((r) => [r.id, r.ok]));
  const empeoran = res.filter((r) => antes.get(r.id) === true && !r.ok);
  const mejoran = res.filter((r) => antes.get(r.id) === false && r.ok);
  md += `\n## Cambios respecto a la ejecución anterior\n\n- Casos que mejoran: ${mejoran.length}\n- Casos que EMPEORAN: ${empeoran.length}${empeoran.length ? '\n' + empeoran.slice(0, 30).map((r) => `  - ${r.id} «${r.consulta}»`).join('\n') : ''}\n`;
}
md += `\n## Fallos por categoría (hasta 15 por categoría)\n`;
for (const c of cats) {
  const f = res.filter((r) => r.categoria === c && !r.ok);
  if (!f.length) continue;
  const tipos = {};
  f.forEach((r) => { tipos[r.tipo] = (tipos[r.tipo] || 0) + 1; });
  md += `\n### ${c} — ${f.length} fallos (${Object.entries(tipos).map(([k, v]) => `${k}: ${v}`).join(', ')})\n\n`;
  md += f.slice(0, 15).map((r) => `- ${r.id} «${r.consulta}» → ${r.tipo}${r.error ? ' (' + r.error + ')' : ''}`).join('\n') + '\n';
}
fs.writeFileSync(path.join(dir, 'informe.md'), md);
console.log(md.split('\n').slice(0, 16).join('\n'));
