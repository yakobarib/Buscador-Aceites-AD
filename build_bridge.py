"""Puente WIKI/Excel -> index.html: genera AD_REF_FAMILIA y lo inserta en index.html entre marcas (idempotente).

Uso:  python build_bridge.py            (escribe en index.html de la rama actual)
      python build_bridge.py --solo-json (solo genera bridge_ad_ref_familia.json, sin tocar index.html)

AD_REF_FAMILIA = { "61208": ["ADP61005", "208"], ... }   referencia AD (cualquier formato) -> [sku de la familia en el catalogo de la app, sufijo de formato]
Origen de los datos (nada se deduce a ojo):
  1) familias del catalogo AD Parts (xlsx): sus "Referencias disponibles" -> la familia de cada referencia
  2) refs de las listas de precios AD (Productos AD Parts Abril 2026.xlsx) que no estan en (1): se asignan SOLO si
     codigo-de-familia + sufijo-de-formato las reconstruye de forma UNICA (p. ej. 331000 = familia 33 + formato 1000)
  3) el sku de la familia en la app (AD_PARTS_CATALOG) se lee ejecutando index.html; solo se enlazan familias que existan alli.
Lo que no se puede enlazar con seguridad se lista en build_bridge_informe.txt.
"""
import difflib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import build_wiki as bw

RAIZ = Path(__file__).resolve().parent
SUFIJOS = ["1000", "600", "208", "050", "020", "005", "002", "001"]
INI, FIN = "// <<AD_REF_FAMILIA:inicio>>", "// <<AD_REF_FAMILIA:fin>>"
HTML_LIMPIO = RAIZ / "evals" / "_limpio.html"


def preparar_html_limpio():
    """Copia de index.html SIN los bloques que genera este script: asi lo que el buscador 'ya conoce' es lo suyo de siempre,
    no el resultado de la pasada anterior (si no, el generador se leeria a si mismo)."""
    html = (RAIZ / "index.html").read_text(encoding="utf-8")
    for ini, fin in ((INI, FIN), ("// <<AD_NORMAS_PUENTE:inicio>>", "// <<AD_NORMAS_PUENTE:fin>>")):
        html = re.sub(re.escape(ini) + r".*?" + re.escape(fin), "", html, count=1, flags=re.S)
    HTML_LIMPIO.write_text(html, encoding="utf-8")


def skus_de_la_app():
    js = ("const {cargar}=require('./evals/buscador_headless');const b=cargar('"+HTML_LIMPIO.as_posix()+"');"
          "process.stdout.write(JSON.stringify(b.llamar('AD_PARTS_CATALOG.map(p=>({sku:p.sku,ref:p.ref,formats:p.formats,visc:p.viscosity,segment:p.segment,tipo:p.type,alt:p.altSkus||[]}))')))")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
    return json.loads(r.stdout)


def resolver_en_app(literales):
    """Pregunta al propio buscador (intelligentSearch) como resuelve cada norma y como la normaliza (normalizeDesc)."""
    js = ("const {cargar}=require('./evals/buscador_headless');const b=cargar('"+HTML_LIMPIO.as_posix()+"');const nd=b.llamar('normalizeDesc');"
          "const L=JSON.parse(require('fs').readFileSync(0,'utf8'));"
          "const out=L.map(l=>{let r=null;try{r=b.intelligentSearch(l)}catch(e){};"
          "return {l, norm:nd(l), match:r&&r.match, canonical:r&&r.canonical||null};});"
          "process.stdout.write(JSON.stringify(out))")
    r = subprocess.run(["node", "-e", js], input=json.dumps(literales), capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
    return {x["l"]: x for x in json.loads(r.stdout)}


def claves_specs_db():
    js = ("const {cargar}=require('./evals/buscador_headless');const b=cargar('"+HTML_LIMPIO.as_posix()+"');"
          "process.stdout.write(JSON.stringify(b.llamar('Object.keys(SPECS_DB)')))")
    return json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", cwd=RAIZ).stdout)


def es_fiable(lit):
    """Una norma NUEVA solo entra si parece una norma entera: sin comas ni cadenas compuestas y empezando por el nombre de quien la emite."""
    t = lit.split()
    return bool(t) and "," not in lit and lit.count("/") <= 1 and len(lit) <= 35 and len(t[0]) >= 2 and t[0].replace("-", "").isalpha()


def errata_de(lit, conocidas):
    """Si una sola palabra difiere de una norma que el buscador ya conoce ("ALISON C4" / "ALLISON C-4"), devuelve esa norma."""
    tk = lit.split()
    for c in conocidas:
        ck = c.split()
        if len(ck) != len(tk):
            continue
        dif = [(x, y) for x, y in zip(tk, ck) if bw.clave(x) != bw.clave(y)]
        if len(dif) == 1 and dif[0][0].isalpha() and dif[0][1].isalpha() and min(len(dif[0][0]), len(dif[0][1])) >= 3                 and difflib.SequenceMatcher(None, dif[0][0].upper(), dif[0][1].upper()).ratio() >= 0.8 and bw.clave(lit) != bw.clave(c):
            return c
    return None


def puente_normas(app, fam_sku):
    """Normas individuales de cada familia (catalogo xlsx) traducidas al nombre que usa el buscador.
    Devuelve {specs: {sku: [canonicas]}, nuevas: {canonica: {...}}, alias: {normalizado: canonica}} y un informe."""
    por_sku = {a["sku"]: a for a in app.values()}
    lits = sorted({lit for fam, _ in fam_sku for t, lit in fam["normas"] if t in ("acea", "api", "ilsac", "jaso", "homologacion")})
    res = resolver_en_app(lits)
    conocidas = claves_specs_db()
    specs, nuevas, alias, informe = defaultdict(set), {}, {}, []
    usado_en = defaultdict(set)
    excluidas = set()
    for fam, sku in fam_sku:
        a = por_sku[sku]
        for t, lit in fam["normas"]:
            if t not in ("acea", "api", "ilsac", "jaso", "homologacion"):
                continue
            r = res[lit]
            if r["canonical"] and r["match"] in ("exact", "alias", "category"):
                destino = r["canonical"]
            else:
                destino = bw.canon_lit(lit)
                if bw.clave(destino) in {bw.clave(x) for x in bw._alias_cfg.get("_excluir_del_puente", [])}:
                    if lit not in excluidas:
                        excluidas.add(lit)
                        informe.append(f"norma NO incorporada (excluida a mano en normas_alias.json): «{lit}»")
                    continue
                fix = errata_de(destino, conocidas)
                if fix:
                    informe.append(f"errata corregida: «{lit}» se trata como «{fix}»")
                    destino = fix
                elif not es_fiable(destino):
                    if lit not in excluidas:
                        excluidas.add(lit)
                        informe.append(f"norma NO incorporada (fragmento, cadena compuesta o posible errata; revisar la fuente): «{lit}»")
                    continue
                elif destino not in nuevas:
                    nuevas[destino] = {"description": f"Norma {destino} (dato del catálogo AD Parts; sin descripción curada todavía)",
                                       "segment": a.get("segment") or "ligero", "tipo": a.get("tipo") or "motor"}
                    informe.append(f"norma nueva para el buscador: «{destino}» (leída como «{lit}»)")
                for variante in {lit, destino}:
                    k = res[lit]["norm"] if variante == lit else resolver_en_app([variante])[variante]["norm"]
                    alias.setdefault(k, destino)
            specs[sku].add(destino)
            usado_en[destino].add(f'{fam["producto"]} {fam["visc"]}'.strip())
    return {"specs": {k: sorted(v) for k, v in specs.items()}, "nuevas": nuevas, "alias": alias}, informe, usado_en


RUTA_DESC = RAIZ / "BASE DE CONOCIMIENTO" / "NORMATIVAS" / "Descripciones de normas para curar.xlsx"
EMISORES = {"ACEA": "Asociación de Constructores Europeos de Automóviles (ACEA)", "API": "American Petroleum Institute (API)",
            "ILSAC": "ILSAC (fabricantes japoneses y americanos)", "JASO": "JASO (Japón)", "DIN": "DIN (Alemania)", "ISO": "ISO",
            "ASTM": "ASTM", "MIL": "Especificación militar de EE. UU.", "SAE": "SAE"}


def aplicar_descripciones(nuevas, usado_en, informe):
    """Las normas nuevas salen con una descripcion generica. Se vuelcan en un Excel para que Yakoba escriba la buena; al volver a ejecutar,
    lo que ya haya escrito (descripcion, segmento, tipo) se respeta y se usa en el buscador. Nada se pisa."""
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    previas = {}
    if RUTA_DESC.exists():
        try:
            for fila in openpyxl.load_workbook(RUTA_DESC, data_only=True)["Normas"].iter_rows(min_row=2, values_only=True):
                if fila and fila[0]:
                    previas[str(fila[0]).strip()] = (str(fila[3] or "").strip(), str(fila[4] or "").strip(), str(fila[5] or "").strip())
        except Exception as e:
            informe.append(f"no se pudo leer {RUTA_DESC.name}: {e}")
    hechas = 0
    for k, v in nuevas.items():
        d, seg, tipo = previas.get(k, ("", "", ""))
        if d:
            v["description"] = d
            hechas += 1
        if seg:
            v["segment"] = seg
        if tipo:
            v["tipo"] = tipo
    wb = openpyxl.Workbook()
    ws0 = wb.active
    ws0.title = "Instrucciones"
    ejemplos = [(k, v.get("description", "")) for k, v in list(subprocess_specs_db_ejemplos().items())[:4]]
    texto = ["Descripciones de las normas que el buscador no conocía (vienen de tu catálogo AD Parts).",
             "",
             "Qué hay que hacer: en la hoja «Normas», rellenar la columna D (Descripción) de cada norma. Lo demás es opcional.",
             "Qué es una descripción: la frase que el buscador enseña debajo del nombre de la norma en la pestaña Homologaciones.",
             "Ejemplos reales del buscador:"] + [f"   {k}  →  {d}" for k, d in ejemplos] + [
             "",
             "Segmento: ligero, pesado, moto... · Tipo: motor, transmision, hidraulico... (ya vienen rellenados con lo que dice el catálogo; corrígelos si hace falta).",
             "Mientras la descripción esté vacía, el buscador enseña: «Norma X (dato del catálogo AD Parts; sin descripción curada todavía)».",
             "Se vuelve a generar con `python build_bridge.py`: lo que escribas aquí se conserva."]
    for i, t in enumerate(texto, 1):
        ws0.cell(i, 1, t)
    ws0.column_dimensions["A"].width = 140
    ws = wb.create_sheet("Normas")
    cab = ["Norma", "Qué es (automático)", "Familias AD que la citan", "Descripción (RELLENAR)", "Segmento", "Tipo"]
    ws.append(cab)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="DDEBF7")
    for k in sorted(nuevas, key=lambda x: (x.split()[0].upper(), x)):
        v = nuevas[k]
        primera = k.split()[0].upper()
        que = EMISORES.get(primera, f"Especificación del fabricante o entidad «{k.split()[0]}»")
        d, _, _ = previas.get(k, ("", "", ""))
        ws.append([k, que, "; ".join(sorted(usado_en.get(k, []))), d, v.get("segment", ""), v.get("tipo", "")])
    for col, w in zip("ABCDEF", (28, 46, 60, 80, 12, 16)):
        ws.column_dimensions[col].width = w
    for fila in ws.iter_rows(min_row=2):
        for c in fila:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "B2"
    try:
        wb.save(RUTA_DESC)
        informe.append(f"descripciones de normas: {hechas} de {len(nuevas)} escritas por Yakoba en «{RUTA_DESC.name}»")
    except PermissionError:
        informe.append(f"«{RUTA_DESC.name}» está abierto en Excel: ciérralo y vuelve a ejecutar para actualizarlo")


def subprocess_specs_db_ejemplos():
    js = ("const {cargar}=require('./evals/buscador_headless');const b=cargar('" + HTML_LIMPIO.as_posix() + "');"
          "const o={};['MB 229.5','API SN','VW 504.00','ACEA C3'].forEach(k=>{if(SPECS_DB_HAS(k))o[k]=1});"
          "process.stdout.write(JSON.stringify(b.llamar('Object.fromEntries([\"MB 229.5\",\"API SN\",\"VW 504.00\",\"ACEA C3\"].filter(k=>SPECS_DB[k]).map(k=>[k,SPECS_DB[k]]))')))")
    js = js.replace("const o={};['MB 229.5','API SN','VW 504.00','ACEA C3'].forEach(k=>{if(SPECS_DB_HAS(k))o[k]=1});", "")
    try:
        r = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
        return {k: v for k, v in json.loads(r.stdout).items()}
    except Exception:
        return {}


def codigo_y_sufijo(ref):
    for s in SUFIJOS:
        if ref.endswith(s) and len(ref) > len(s):
            return ref[: -len(s)], s
    return None, None


def main():
    preparar_html_limpio()
    bw.cargar_listas_simples()
    bw.cargar_refrigerantes_ad()
    bw.cargar_catalogo_ad()
    app = {a["sku"][3:]: a for a in skus_de_la_app()}  # "61005" -> {sku:"ADP61005", ...}
    informe, mapa, codigo_de_sku, fam_sku = [], {}, {}, []
    for fam in bw.FAMILIAS:
        sku_app = next((r for r in fam["refs"] if r in app), None)
        if not sku_app:
            informe.append(f'familia del catálogo sin sku en la app: {fam["producto"]} {fam["visc"]} (refs {", ".join(fam["refs"])})')
            continue
        codigos = {codigo_y_sufijo(r)[0] for r in fam["refs"] if codigo_y_sufijo(r)[0]}
        if len(codigos) != 1:
            # familias (p. ej. las grasas) cuyas referencias no siguen "codigo + formato en litros": se enlazan una a una, sin formato
            for r in fam["refs"]:
                mapa[r] = ["ADP" + sku_app, ""]
            fam_sku.append((fam, "ADP" + sku_app))
            informe.append(f'familia sin código de formato ({fam["producto"]} {fam["visc"]}): enlazadas sus {len(fam["refs"])} referencias sin formato')
            continue
        codigo = codigos.pop()
        codigo_de_sku["ADP" + sku_app] = codigo
        fam_sku.append((fam, "ADP" + sku_app))
        for r in fam["refs"]:
            c, s = codigo_y_sufijo(r)
            if c == codigo:
                mapa[r] = ["ADP" + sku_app, s]
    # familias que la app tiene y el catalogo xlsx no recoge (p. ej. SHT 0W30, codigo 33): su codigo sale del sku (codigo + sufijo de formato)
    visc_de_sku = {}
    for a in app.values():
        visc_de_sku[a["sku"]] = a.get("visc") or ""
        c, suf = codigo_y_sufijo(a["sku"][3:])
        if c and a["sku"] not in codigo_de_sku:
            codigo_de_sku[a["sku"]] = c
    # refs de las listas de precios que el catalogo no recoge: codigo de familia + sufijo, solo si es unica
    por_codigo = defaultdict(list)
    for sku, c in codigo_de_sku.items():
        por_codigo[c].append(sku)
    for p in bw.PRODUCTOS:
        if p["marca"] != "AD Parts" or p["ref"] in mapa:
            continue
        cands = []
        for c, skus in por_codigo.items():
            if p["ref"].startswith(c) and p["ref"][len(c):] in SUFIJOS:
                cands.append((c, skus[0], p["ref"][len(c):]))
        if len(cands) == 1:
            v_desc, v_fam = bw.visc_de(p["desc"]), re.sub(r"[^0-9A-Za-z]", "", visc_de_sku.get(cands[0][1], "")).upper()
            if v_desc and v_fam and v_desc != v_fam:  # la viscosidad de la descripcion debe coincidir con la de la familia
                informe.append(f'ref {p["ref"]} «{p["desc"]}»: la familia {cands[0][1]} es {v_fam}, no se enlaza')
                continue
            mapa[p["ref"]] = [cands[0][1], cands[0][2]]
        elif len(cands) > 1:
            informe.append(f'ref de la lista de precios ambigua ({p["ref"]}): ' + ", ".join(c[1] for c in cands))
        else:
            informe.append(f'ref de la lista de precios sin familia en el catálogo: {p["ref"]} «{p["desc"]}»')
    # familias de refrigerante de la tarifa que el buscador no tenia (datos de sus fichas, en refrigerantes_nuevos.json)
    nuevas_fam = json.loads((RAIZ / "refrigerantes_nuevos.json").read_text(encoding="utf-8"))["familias"]
    por_alt = {}
    for a in app.values():
        for alt in a.get("alt", []):
            por_alt[alt] = a["sku"]
    for f in nuevas_fam:
        app[f["sku"][3:]] = {"sku": f["sku"], "ref": f["ref"], "formats": f["formats"], "segment": "ligero", "tipo": "refrigerante", "alt": f["altSkus"]}
        for alt in f["altSkus"]:
            por_alt[alt] = f["sku"]
        fam_sku.append(({"producto": f["ref"], "visc": "", "normas": [("homologacion", n) for n in f["normas"]], "refs": []}, f["sku"]))
    # refrigerantes, AdBlue y DOT 4: la referencia de la tarifa es el sku de la familia en la app o una de sus referencias alternativas (altSkus)
    for p in bw.PRODUCTOS:
        if p["marca"] == "AD Refrigerantes":
            clave_app = p["ref"][3:] if p["ref"].startswith("ADP") else p["ref"]
            if clave_app in app and clave_app not in mapa:
                mapa[clave_app] = [app[clave_app]["sku"], ""]
            elif "ADP" + clave_app in por_alt and clave_app not in mapa:
                mapa[clave_app] = [por_alt["ADP" + clave_app], ""]
            elif clave_app not in app and "ADP" + clave_app not in por_alt:
                informe.append(f'refrigerante de la tarifa sin familia en el buscador: {p["ref"]} «{p["desc"]}»')
    # formatos (litros) que la tarifa o el catalogo dan para cada familia: se SUMAN a los que ya tenia la app (no se quita ninguno)
    por_sku_app = {a["sku"]: a for a in app.values()}
    formatos = defaultdict(set)
    for r, (sku, suf) in mapa.items():
        if suf and por_sku_app[sku].get("tipo") != "grasa":
            formatos[sku].add(int(suf))
            if int(suf) not in por_sku_app[sku]["formats"]:
                informe.append(f'formato añadido: {por_sku_app[sku]["ref"]} {int(suf)} L (ref {r}, ' + ("tarifa de abril" if r in {q["ref"] for q in bw.PRODUCTOS if q["marca"] == "AD Parts"} else "solo en el catálogo") + ")")
    for f in nuevas_fam:  # sus normas se ponen al cargar via AD_NORMAS_PUENTE (con nombres que el buscador reconozca)
        informe.append(f'familia de refrigerante AÑADIDA al buscador: {f["ref"]} ({f["sku"]}, alt. {", ".join(f["altSkus"])}) · fuente: {f["fuente"][:90]}')
    normas, informe_n, usado_en = puente_normas(app, fam_sku)
    informe += informe_n
    aplicar_descripciones(normas["nuevas"], usado_en, informe)
    (RAIZ / "bridge_normas.json").write_text(json.dumps(normas, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    (RAIZ / "bridge_ad_ref_familia.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    (RAIZ / "build_bridge_informe.txt").write_text("\n".join(informe) + "\n", encoding="utf-8")
    print(f"AD_NORMAS_PUENTE: {sum(len(v) for v in normas['specs'].values())} normas en {len(normas['specs'])} familias · {len(normas['nuevas'])} normas nuevas · {len(normas['alias'])} alias")
    print(f"AD_REF_FAMILIA: {len(mapa)} referencias -> {len(set(v[0] for v in mapa.values()))} familias · sin enlazar: {len(informe)}")
    if "--solo-json" in sys.argv:
        return
    ruta = RAIZ / "index.html"
    html = ruta.read_text(encoding="utf-8")
    cod_f = """(function () {
  // formatos (litros) de cada familia segun la tarifa/catalogo: se suman a los que la app ya tenia
  AD_PARTS_CATALOG.forEach(p => {
    if (!Array.isArray(p.formats)) return;  // hay familias (refrigerantes...) sin lista de formatos
    (AD_FORMATOS[p.sku] || []).forEach(x => { if (!p.formats.includes(x)) p.formats.push(x); });
    p.formats.sort((a, b) => a - b);
  });
})();"""
    fmts = json.dumps({k: sorted(v) for k, v in formatos.items()}, sort_keys=True, separators=(",", ":"))
    fam_nuevas_js = json.dumps([{"ref": f["ref"], "sku": f["sku"], "altSkus": f["altSkus"], "viscosity": "-", "type": "refrigerante", "segment": "ligero",
                                 "formats": f["formats"], "specs": []} for f in nuevas_fam], ensure_ascii=False, separators=(",", ":"))
    bloque = (INI + chr(10) + "const AD_REF_FAMILIA = " + json.dumps(mapa, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + ";" + chr(10)
              + "const AD_FORMATOS = " + fmts + ";" + chr(10) + cod_f + chr(10)
              + "// familias de refrigerante de la tarifa que el buscador no tenia (datos: refrigerantes_nuevos.json)" + chr(10)
              + "(" + fam_nuevas_js + ").forEach(f => { if (!AD_PARTS_CATALOG.some(p => p.sku === f.sku)) AD_PARTS_CATALOG.push(f); });" + chr(10) + FIN)
    if INI in html:
        html = re.sub(re.escape(INI) + r".*?" + re.escape(FIN), lambda m: bloque, html, count=1, flags=re.S)
    else:
        ancla = "// Convierte lo escrito en la búsqueda libre en una consulta"
        assert ancla in html, "no encuentro el punto de inserción en index.html"
        html = html.replace(ancla, bloque + "\n\n" + ancla, 1)
    INI2, FIN2 = "// <<AD_NORMAS_PUENTE:inicio>>", "// <<AD_NORMAS_PUENTE:fin>>"
    cod = """(function () {
  // las normas nuevas y sus alias se anaden SOLO si el buscador no las conocia; las normas de cada familia se SUMAN a las que ya tenia
  Object.entries(AD_NORMAS_PUENTE.nuevas).forEach(([k, v]) => { if (!SPECS_DB[k]) SPECS_DB[k] = v; });
  Object.entries(AD_NORMAS_PUENTE.alias).forEach(([k, v]) => { if (!SPEC_ALIASES[k]) SPEC_ALIASES[k] = v; });
  AD_PARTS_CATALOG.forEach(p => (AD_NORMAS_PUENTE.specs[p.sku] || []).forEach(s => {
    if (!p.specs.some(x => x.toUpperCase() === s.toUpperCase())) p.specs.push(s);
  }));
})();"""
    datos = json.dumps(normas, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    bloque2 = INI2 + chr(10) + "const AD_NORMAS_PUENTE = " + datos + ";" + chr(10) + cod + chr(10) + FIN2
    if INI2 in html:
        html = re.sub(re.escape(INI2) + r".*?" + re.escape(FIN2), lambda m: bloque2, html, count=1, flags=re.S)
    else:
        html = html.replace(FIN, FIN + chr(10) + chr(10) + bloque2, 1)
    ruta.write_text(html, encoding="utf-8")
    print("index.html actualizado")


if __name__ == "__main__":
    main()
