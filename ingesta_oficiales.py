"""Paginas de indice en la wiki con TODAS las hojas oficiales de Mercedes-Benz y TODAS las clases ZF TE-ML.

Uso:  python ingesta_oficiales.py     (despues de gen_oficiales_mb.py y extract_zf_teml.py)
Salida: OBSIDIAN/Buscador Aceites/WIKI/conocimiento/Mercedes-Benz - hojas oficiales.md  y  ZF - clases TE-ML (listas oficiales).md
"""
import json
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
WIKI = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "WIKI"
SAL = WIKI / "conocimiento"


def paginas_norma():
    return {p.stem for p in (WIKI / "normas").glob("*.md")}


def enlace(n, pags):
    return f"[[{n}]]" if n in pags else n


def main():
    SAL.mkdir(parents=True, exist_ok=True)
    pags = paginas_norma()
    mb = json.loads((RAIZ / "BASE DE CONOCIMIENTO" / "CATALOGOS" / "Mercedes" / "mb_operating_fluids.json").read_text(encoding="utf-8"))
    of = json.loads((RAIZ / "descripciones_oficiales_mb.json").read_text(encoding="utf-8"))
    L = ["---", "tipo: conocimiento", 'titulo: "Mercedes-Benz - hojas oficiales"', f"fecha: {date.today()}", 'tema: "normativas"',
         f"origen: operatingfluids.mercedes-benz.com (descargado {mb['descargado']})", "---", "",
         "# Mercedes-Benz - hojas oficiales de betriebsstoffe", "",
         "Todas las hojas de Mercedes-Benz Operating Fluids (motor, transmisión, refrigerante, grasa e hidráulico). Datos tomados de la API pública de "
         "operatingfluids.mercedes-benz.com; la lista de productos aprobados de cada hoja está en `BASE DE CONOCIMIENTO/CATALOGOS/Mercedes/mb_operating_fluids.json`.", ""]
    for cat, v in mb["categorias"].items():
        L += [f"## {cat} ({v['nombre_de']})", "", "| Hoja | Título oficial (EN) | Descripción en español | Productos aprobados |", "|---|---|---|---|"]
        for h in v["hojas"]:
            k = f"MB {h['hoja'].rstrip('H')}"
            d = of.get(k, {}).get("description", "")
            L.append(f"| {enlace(k, pags)} | {h['titulo_en'].strip()} | {d.split(' (hoja')[0]} | {len(h['productos'])} |")
        L.append("")
    (SAL / "Mercedes-Benz - hojas oficiales.md").write_text("\n".join(L), encoding="utf-8")
    zf = json.loads((RAIZ / "zf_teml_extraido.json").read_text(encoding="utf-8"))
    L = ["---", "tipo: conocimiento", 'titulo: "ZF - clases TE-ML (listas oficiales)"', f"fecha: {date.today()}", 'tema: "normativas"',
         "origen: listas de lubricantes ZF TE-ML (edición 01.07.2018) en BASE DE CONOCIMIENTO/CATALOGOS/ZF", "---", "",
         "# ZF - clases de lubricante TE-ML", "",
         "Resumen automático (reglas, sin IA) de las listas ZF TE-ML. Las listas completas, con los productos comerciales aprobados y su número de homologación ZF, están en los documentos enlazados.", ""]
    for lista, ap in sorted(zf["aplicaciones"].items()):
        L += [f"## TE-ML {lista}: {ap}", ""]
        for cod, c in sorted(zf["clases"].items()):
            if c["lista"] != lista:
                continue
            n = f"ZF TE-ML {cod}"
            cab = c["cabecera"] if c["cabecera"] and not c["cabecera"].lower().startswith(("nota", "(*)")) else ""
            L.append(f"- {enlace(n, pags)} · {cab or 'sin texto de cabecera en la lista'} · {c['n_homologaciones_zf']} homologaciones ZF de productos comerciales")
        L += ["", f"Documento: [[CATALOGOS/ZF/TE-ML {lista}-ES]]", ""]
    (SAL / "ZF - clases TE-ML (listas oficiales).md").write_text("\n".join(L), encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
