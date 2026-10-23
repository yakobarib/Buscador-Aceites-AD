// Carga la logica REAL de index.html en Node (sin navegador) con un DOM simulado y expone las funciones de busqueda.
// Uso: const { cargar } = require('./buscador_headless'); const b = cargar(); b.freeSearch('mb 229.5')
const fs = require('fs');
const vm = require('vm');
const path = require('path');

function dom() {  // objeto "comodin": cualquier propiedad/llamada devuelve otro comodin
  const f = function () {};
  const p = new Proxy(f, {
    get: (t, k) => (k === Symbol.toPrimitive ? () => '' : k === 'length' ? 0 : k === 'then' ? undefined : p),
    apply: () => p, construct: () => p, set: () => true,
  });
  return p;
}

function elemento(id) {  // elemento DOM simulado: recuerda lo que se le escribe en innerHTML/textContent; el resto de llamadas no hace nada
  const base = { id, innerHTML: '', textContent: '', value: '', style: {}, dataset: {}, children: [],
                 classList: { add() {}, remove() {}, toggle() {}, contains: () => false } };
  const noop = dom();
  return new Proxy(base, { get: (t, k) => (k in t ? t[k] : noop), set: (t, k, v) => { t[k] = v; return true; } });
}

function cargar(rutaHtml = path.join(__dirname, '..', 'index.html')) {
  const html = fs.readFileSync(rutaHtml, 'utf8');
  const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  const comodin = dom();
  const sandbox = {
    console: { log() {}, warn() {}, error() {}, info() {}, debug() {} },
    document: null, window: undefined, navigator: { userAgent: 'node', language: 'es' },
    localStorage: { getItem: () => null, setItem() {}, removeItem() {} }, sessionStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    indexedDB: comodin, fetch: () => Promise.reject(new Error('sin red')), setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0,
    requestAnimationFrame: () => 0, addEventListener() {}, location: { href: '', search: '', hash: '' }, performance: { now: () => Date.now() },
  };
  const els = {};
  const getEl = (id) => (els[id] = els[id] || elemento(id));
  sandbox.document = new Proxy({ getElementById: getEl, querySelector: (q) => getEl('q:' + q), querySelectorAll: () => [],
                                 createElement: () => elemento('nuevo'), body: elemento('body'), addEventListener() {} },
                               { get: (t, k) => (k in t ? t[k] : comodin) });
  sandbox.window = sandbox; sandbox.self = sandbox; sandbox.globalThis = sandbox;
  const ctx = vm.createContext(sandbox);
  const errores = [];
  scripts.forEach((s, i) => {
    try { vm.runInContext(s, ctx, { filename: `script${i}.js` }); } catch (e) { errores.push(`script ${i}: ${e.message}`); }
  });
  const llamar = (expr) => vm.runInContext(expr, ctx);
  return {
    errores,
    existe: (n) => llamar(`typeof ${n}`) !== 'undefined',
    freeSearch: (q) => { sandbox.__q = q; return llamar('freeSearch(__q)'); },
    crossReferenceSearch: (q) => { sandbox.__q = q; return llamar('crossReferenceSearch(__q)'); },
    intelligentSearch: (q) => { sandbox.__q = q; return llamar('intelligentSearch(__q)'); },
    ctx, llamar,
    // flujo COMPLETO de la pestaña "Homologaciones" (searchByDesc)
    buscarHomologacion: (q) => {
      els['results-section'] = elemento('results-section');
      getEl('input-desc').value = q;
      try { llamar('currentVehicle = null'); llamar('searchByDesc()'); } catch (e) { return { error: e.message, texto: '' }; }
      const html = els['results-section'].innerHTML || '';
      return { texto: html.replace(/<style[\s\S]*?<\/style>/g, ' ').replace(/<[^>]*>/g, ' ').replace(/&[a-z#0-9]+;/g, ' ').replace(/\s+/g, ' ').trim(), html };
    },
    // flujo COMPLETO de la pestaña "Búsqueda libre" (searchByFree): escribe en el campo, busca y devuelve el texto que se pinta
    buscarLibre: (q) => {
      els['results-section'] = elemento('results-section');
      getEl('input-free').value = q;
      try { llamar('currentVehicle = null'); llamar('searchByFree()'); } catch (e) { return { error: e.message, texto: '' }; }
      const html = els['results-section'].innerHTML || '';
      return { texto: html.replace(/<style[\s\S]*?<\/style>/g, ' ').replace(/<[^>]*>/g, ' ').replace(/&[a-z#0-9]+;/g, ' ').replace(/\s+/g, ' ').trim(), html };
    },
    // lo que la pantalla muestra al usuario para un resultado de freeSearch (texto visible del contenedor de resultados)
    pintar: (r) => {
      els['results-section'] = elemento('results-section');
      sandbox.__r = r;
      try { llamar('renderFreeResult(__r)'); } catch (e) { return { error: e.message, texto: '' }; }
      const html = els['results-section'].innerHTML || '';
      return { texto: html.replace(/<style[\s\S]*?<\/style>/g, ' ').replace(/<[^>]*>/g, ' ').replace(/&[a-z#0-9]+;/g, ' ').replace(/\s+/g, ' ').trim(), html };
    },
  };
}
module.exports = { cargar };

if (require.main === module) {
  const b = cargar();
  console.log = (...a) => process.stdout.write(a.join(' ') + '\n');
  console.log('errores de carga:', b.errores.length, b.errores.slice(0, 3));
  for (const n of ['freeSearch', 'intelligentSearch', 'AD_PARTS_CATALOG', 'HUMAN_EQUIV', 'OEM_INDEX', 'SPECS_DB']) console.log(n, b.existe(n));
  for (const q of ['mb 229.5', '61005', 'febi 170166', '5w30 c3', 'G 060 162 A2']) {
    let r; try { r = b.freeSearch(q); } catch (e) { r = 'ERROR ' + e.message; }
    console.log('\n>', q, '=>', typeof r === 'string' ? r : (r && r.match), (JSON.stringify(r) || '').length, 'bytes');
  }
}
