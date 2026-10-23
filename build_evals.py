"""Genera evals/casos.json: consultas de prueba con respuesta conocida, sacadas SOLO de los Excel de origen.

Uso:  python build_evals.py      (despues:  node evals/run_evals.js)

Cada caso: {id, categoria, consulta, esperado: [referencias], modo: "alguno"|"todos", origen}
Un caso se da por bueno si la respuesta del buscador MENCIONA alguna (o todas) de las referencias esperadas.
Categorias (todas con respuesta verificable en los datos de origen, nada deducido):
  ad_ref          referencia AD Parts / AD Standard escrita tal cual -> ese producto
  ref_competidor  referencia de Castrol/Repsol/Shell/Eni (fila de la matriz de equivalencias) -> su equivalente AD
  febi_ref        "febi 170166" -> ese producto
  oem_febi        codigo OEM tal cual figura en el Excel de Febi (columna critica) -> los febi con ese OEM
  norma_ad        homologacion / ACEA / API del catalogo AD Parts -> alguna referencia AD de las familias que la cumplen
  visc_acea       viscosidad + ACEA de una familia AD -> alguna referencia de esa viscosidad y ACEA
  tcmatic_febi    referencia TC-Matic -> su febi equivalente (tabla de equivalencias)
"""
import json
import re
import sys
import zlib
from collections import defaultdict
from pathlib import Path

import build_wiki as bw

RAIZ = Path(__file__).resolve().parent


def main():
    for c in (bw.cargar_listas_simples, bw.cargar_febi, bw.cargar_tcmatic, bw.cargar_catalogo_ad,
              bw.cargar_equivalencias, bw.cargar_febi_tcmatic):
        c()
    casos, vistos = [], set()

    def anadir(cat, consulta, esperado, modo="alguno", origen="", herramienta="libre"):
        esperado = [e for e in dict.fromkeys(esperado) if e]  # sin repetidos, conservando el orden
        clave = (cat, herramienta, consulta.lower())
        if not consulta.strip() or not esperado or clave in vistos:
            return
        vistos.add(clave)
        casos.append(dict(id=f"{cat}-{zlib.crc32((herramienta + consulta.lower()).encode('utf-8')):08x}", categoria=cat, consulta=consulta, esperado=esperado, modo=modo, origen=origen,
                           herramienta=herramienta))

    # el buscador muestra FAMILIAS ("AD HSD 0W20", sku ADP61005), no referencias sueltas: lo esperado es el nombre de la familia
    # esperado = nombre de la familia O cualquiera de sus referencias (la pantalla muestra ADP + la referencia de 5 L): asi no depende
    # de como se escriba el nombre ("AD HHM 32" en la app, "AD HHM HM32" en el Excel)
    fam_de = {}
    for fam in bw.FAMILIAS:
        for r in fam["refs"]:
            fam_de[r] = ["nombre:" + re.sub(r"^AD\s+", "", f'{fam["producto"]} {fam["visc"]}').strip()] + fam["refs"]
    esperado_ad = lambda r: fam_de.get(r, [r])

    ad = [p for p in bw.PRODUCTOS if p["marca"] in ("AD Parts", "AD Standard")]
    for p in ad:
        # ademas del nombre de la familia del catalogo, vale el nombre del producto en la lista de precios (sin el formato): "SHT 0W30 High Tech"
        nombre_lista = "nombre:" + re.sub(r"\s+\d+[.,]?\d*\s*(?:L|KG)?\s*$", "", p["desc"].replace(" ", " "), flags=re.I).strip()
        anadir("ad_ref", p["ref"], esperado_ad(p["ref"]) + [nombre_lista], origen=f'{p["libro"]} fila {p["fila"]}')

    # referencia de otra marca -> equivalente AD (misma fila de la matriz)
    for eq in bw.EQUIV:
        ad_refs = [eq["marcas"].get(m, "") for m in ("AD Parts", "AD Standard")]
        ad_refs = [r for r in ad_refs if r and r.upper() not in bw.ESTADOS]
        if not ad_refs:
            continue
        for marca in ("Castrol", "Repsol", "Shell", "Eni"):
            r = eq["marcas"].get(marca, "")
            if r and r.upper() not in bw.ESTADOS:
                anadir("ref_competidor", r, [y for x in ad_refs for y in esperado_ad(x)], origen=f'{eq["libro"]} fila {eq["fila"]} ({marca})')

    febi = [p for p in bw.PRODUCTOS if p["marca"] == "febi"]
    for p in febi:
        anadir("febi_ref", f'febi {p["ref"]}', [p["ref"]], origen=f'{p["libro"]} fila {p["fila"]}')
    por_oem = defaultdict(list)
    for p in febi:
        for o in p["oem"]:
            por_oem[o].append(p["ref"])
    for o, refs in por_oem.items():
        anadir("oem_febi", o, refs, origen="Productos Febi Abril 2026.xlsx, columna OEM")

    # norma -> referencias AD de las familias del catalogo que la cumplen
    por_norma = defaultdict(set)
    for fam in bw.FAMILIAS:
        for tipo, lit in fam["normas"]:
            if tipo in ("homologacion", "acea", "api", "ilsac", "jaso"):
                por_norma[lit].update(["nombre:" + re.sub(r"^AD\s+", "", f'{fam["producto"]} {fam["visc"]}').strip()] + fam["refs"])
    for lit, refs in por_norma.items():
        if len(lit) > 35 or "," in lit or lit.count("/") > 1:  # cadenas compuestas del catalogo: nadie las escribiria asi
            continue
        anadir("norma_ad", lit, sorted(refs), origen="AD PARTS - Catalogo Lubricantes 2025.xlsx")
        anadir("norma_ad_hom", lit, sorted(refs), origen="AD PARTS - Catalogo Lubricantes 2025.xlsx (pestana Homologaciones)", herramienta="homologaciones")
    por_va = defaultdict(set)
    for fam in bw.FAMILIAS:
        visc = re.sub(r"[^0-9WwA-Za-z]", "", fam["visc"])
        if re.fullmatch(r"\d{1,2}W\d{2,3}", visc, re.I):
            for t, x in fam["normas"]:
                if t == "acea":
                    por_va[(visc.upper(), x.replace("ACEA ", ""))].update(["nombre:" + re.sub(r"^AD\s+", "", f'{fam["producto"]} {fam["visc"]}').strip()] + fam["refs"])
    for (visc, cod), nombres in por_va.items():
        anadir("visc_acea", f"{visc} {cod}", sorted(nombres), origen="catalogo AD, familias con esa viscosidad y ACEA")

    for r in bw.FEBI_TC:
        anadir("tcmatic_febi", r["tc"], [r["febi"]], origen="Equivalencias entre Febi y TC-Matic.xlsx")

    # ---- herramienta "referencias cruzadas" (pestana propia del buscador: crossReferenceSearch)
    bw.cargar_equiv_bloques()
    refs_real = lambda eq, ms: [eq["marcas"].get(m, "") for m in ms if eq["marcas"].get(m, "") and eq["marcas"][m].upper() not in bw.ESTADOS]
    for eq in bw.EQUIV:
        ads, comp = refs_real(eq, ("AD Parts", "AD Standard")), refs_real(eq, ("Castrol", "Repsol", "Shell", "Eni"))
        for r in ads:
            anadir("xref_ad_a_otras", r, comp, origen=f'{eq["libro"]} fila {eq["fila"]}', herramienta="xref")
        for r in comp:
            anadir("xref_otra_a_ad", r, ads, origen=f'{eq["libro"]} fila {eq["fila"]}', herramienta="xref")
    for eq in bw.EQUIV_B:  # grasas, hidraulicos, motor VI, transmision manual
        refs = [(m, r) for m, r, _, _ in eq["items"]]
        for m, r in refs:
            anadir("xref_bloques", r, [x for mm, x in refs if mm != m], origen=f'{eq["libro"]} fila {eq["fila"]} ({m})', herramienta="xref")
    for p in febi:
        anadir("xref_febi_conocida", p["ref"], [p["ref"]], modo="propia", origen=f'{p["libro"]} fila {p["fila"]}', herramienta="xref")
    for r in bw.FEBI_TC:
        anadir("xref_tcm_a_febi", r["tc"], [r["febi"]], origen="Equivalencias entre Febi y TC-Matic.xlsx", herramienta="xref")
        anadir("xref_febi_a_tcm", r["febi"], [r["tc"]], origen="Equivalencias entre Febi y TC-Matic.xlsx", herramienta="xref")

    # ---- refrigerantes de la tarifa (sin limpiaparabrisas, agua destilada ni AdBlue, que de momento no importan): su referencia debe llevar a su familia
    import subprocess
    bw.cargar_refrigerantes_ad()
    mapa_ad = json.loads((RAIZ / "bridge_ad_ref_familia.json").read_text(encoding="utf-8"))
    js = ("const {cargar}=require('./evals/buscador_headless');const b=cargar();"
          "process.stdout.write(JSON.stringify(b.llamar('AD_PARTS_CATALOG.map(p=>({sku:p.sku,ref:p.ref}))')))")
    nombre_de = {x["sku"]: x["ref"] for x in json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", cwd=RAIZ).stdout)}
    for p in bw.PRODUCTOS:
        if p["marca"] != "AD Refrigerantes" or re.search(r"LIMPIAPARABRISAS|ADBLUE|DESTILADA", p["desc"], re.I):
            continue
        clave_app = p["ref"][3:] if p["ref"].startswith("ADP") else p["ref"]
        if clave_app in mapa_ad and mapa_ad[clave_app][0] in nombre_de:
            anadir("ref_refrigerante", p["ref"], ["nombre:" + nombre_de[mapa_ad[clave_app][0]]], origen="Productos AD Parts Refrigerantes Abril 2026.xlsx")
            anadir("ref_refrigerante", clave_app, ["nombre:" + nombre_de[mapa_ad[clave_app][0]]], origen="Productos AD Parts Refrigerantes Abril 2026.xlsx")

    out = RAIZ / "evals" / "casos.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(len(casos), "casos:", dict(Counter(c["categoria"] for c in casos)))


if __name__ == "__main__":
    main()
