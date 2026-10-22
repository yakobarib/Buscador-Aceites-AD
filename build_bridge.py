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


def skus_de_la_app():
    js = ("const {cargar}=require('./evals/buscador_headless');const b=cargar();"
          "process.stdout.write(JSON.stringify(b.llamar('AD_PARTS_CATALOG.map(p=>({sku:p.sku,ref:p.ref,formats:p.formats,visc:p.viscosity}))')))")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
    return json.loads(r.stdout)


def codigo_y_sufijo(ref):
    for s in SUFIJOS:
        if ref.endswith(s) and len(ref) > len(s):
            return ref[: -len(s)], s
    return None, None


def main():
    bw.cargar_listas_simples()
    bw.cargar_catalogo_ad()
    app = {a["sku"][3:]: a for a in skus_de_la_app()}  # "61005" -> {sku:"ADP61005", ...}
    informe, mapa, codigo_de_sku = [], {}, {}
    for fam in bw.FAMILIAS:
        sku_app = next((r for r in fam["refs"] if r in app), None)
        if not sku_app:
            informe.append(f'familia del catálogo sin sku en la app: {fam["producto"]} {fam["visc"]} (refs {", ".join(fam["refs"])})')
            continue
        codigos = {codigo_y_sufijo(r)[0] for r in fam["refs"] if codigo_y_sufijo(r)[0]}
        if len(codigos) != 1:
            informe.append(f'código de familia ambiguo: {fam["producto"]} {fam["visc"]} {sorted(codigos)}')
            continue
        codigo = codigos.pop()
        codigo_de_sku["ADP" + sku_app] = codigo
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
    (RAIZ / "bridge_ad_ref_familia.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    (RAIZ / "build_bridge_informe.txt").write_text("\n".join(informe) + "\n", encoding="utf-8")
    print(f"AD_REF_FAMILIA: {len(mapa)} referencias -> {len(set(v[0] for v in mapa.values()))} familias · sin enlazar: {len(informe)}")
    if "--solo-json" in sys.argv:
        return
    ruta = RAIZ / "index.html"
    html = ruta.read_text(encoding="utf-8")
    bloque = f"{INI}\nconst AD_REF_FAMILIA = {json.dumps(mapa, ensure_ascii=False, sort_keys=True, separators=(',', ':'))};\n{FIN}"
    if INI in html:
        html = re.sub(re.escape(INI) + r".*?" + re.escape(FIN), lambda m: bloque, html, count=1, flags=re.S)
    else:
        ancla = "// Convierte lo escrito en la búsqueda libre en una consulta"
        assert ancla in html, "no encuentro el punto de inserción en index.html"
        html = html.replace(ancla, bloque + "\n\n" + ancla, 1)
    ruta.write_text(html, encoding="utf-8")
    print("index.html actualizado")


if __name__ == "__main__":
    main()
