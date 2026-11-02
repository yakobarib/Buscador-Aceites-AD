"""Extrae por REGLAS (sin IA) las clases de lubricante de las listas ZF TE-ML (PDF ya convertidos a Markdown).

Uso:  python extract_zf_teml.py

Entrada : OBSIDIAN/Buscador Aceites/FUENTES_MD/CATALOGOS/ZF/TE-ML NN-ES.md  y  «Lubricantes ZF Segun Especificación.md»
Salida  : zf_teml_extraido.json  (clases, texto de cabecera, productos aprobados con su n.º de homologación ZF)
          descripciones_oficiales_zf.json  {"ZF TE-ML 05A": {description, segment, tipo, fuente, productos_aprobados}}

La descripcion de cada clase solo combina lo que dice la propia lista: la aplicacion de la lista (tabla «Lubricantes ZF según especificación»),
el texto de cabecera de la clase si lo tiene (tipo de aceite y clases de viscosidad) y el numero de productos comerciales aprobados.
No se deduce nada: si la clase no tiene texto de cabecera, solo lleva la aplicacion de la lista.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CARPETA = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "FUENTES_MD" / "CATALOGOS" / "ZF"
SAL1 = RAIZ / "zf_teml_extraido.json"
SAL2 = RAIZ / "descripciones_oficiales_zf.json"
RE_CLASE = re.compile(r"(?m)^Clase de lubricantes\s+(\d{2}[A-Z])\b[ \t]*(.*)$")
RE_PROD = re.compile(r"([A-ZÁÉÍÓÚÑÜ0-9&.,'()\- ]{3,}?/[A-Z]{2})\s+(.+?)\s+(ZF\d{6})")
TRAD_APLIC = {}  # se rellena leyendo la tabla del documento resumen


def aplicaciones():
    t = (CARPETA / "Lubricantes ZF Segun Especificación.md").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"\|\s*(.+?)\s*\|\s*TE-ML (\d{2})\s*\|\s*([\d.]+)\s*\|", t):
        out[m.group(2)] = re.sub(r"\s+", " ", m.group(1)).strip()
    return out


def tipo_de(txt, lista):
    t = txt.lower()
    if "atf" in t or "automatic transmission fluid" in t or lista in ("04", "11", "14", "20"):
        return "transmision"
    if "aceite de motor" in t or "aceites de motor" in t:
        return "motor"
    return "transmision"


def main():
    apl = aplicaciones()
    clases, descs = {}, {}
    for f in sorted(CARPETA.glob("TE-ML *-ES.md")):
        lista = re.search(r"TE-ML (\d{2})", f.name).group(1)
        txt = re.sub(r"<!-- pagina \d+ -->", "\n", f.read_text(encoding="utf-8"))
        # solo la parte de clases aprobadas (la ultima seccion): empieza en la primera cabecera de clase fuera del indice
        ms = [m for m in RE_CLASE.finditer(txt)]
        for i, m in enumerate(ms):
            fin = ms[i + 1].start() if i + 1 < len(ms) else len(txt)
            cuerpo = txt[m.end():fin]
            cab = re.split(r"Fabricante\s*\(", m.group(2) + " " + cuerpo[:600])[0]
            cab = re.sub(r"\s+", " ", cab).strip(" |-")
            prods = []
            for a, b, c2 in RE_PROD.findall(cuerpo):
                a = re.sub(r"\s+", " ", re.sub(r"^.*homologaci[oó]n de ZF\s+", "", a)).strip()
                a = re.sub(r"^\(\d{2}[A-Z]\)\s*", "", a).strip(" |")
                b = re.sub(r"\s+", " ", re.sub(r"\|", " ", re.sub(r"Denominaci[oó]n del producto \(\d{2}[A-Z]\)", " ", b))).strip()
                if a and b and not b.lower().startswith(("número", "fabricante")):
                    prods.append(dict(fabricante=a, producto=b, homologacion_zf=c2))
            n_cod = len(set(re.findall(r"ZF\d{6}", cuerpo)))
            cod = f"{lista}{m.group(1)[2:]}"
            if cod in clases and len(cab) < len(clases[cod]["cabecera"]):
                continue
            clases[cod] = dict(lista=lista, cabecera=cab[:400], n_homologaciones_zf=n_cod, archivo=f.name, productos=prods)
    for cod, c in clases.items():
        ap = apl.get(c["lista"], "")
        cab = c["cabecera"]
        partes = [f"Clase {cod} de la lista ZF TE-ML {c['lista']}" + (f" ({ap[0].lower() + ap[1:]})" if ap else "")]
        cab_ok = cab and not cab.lower().startswith(("nota", "(*)", "fabricante")) and len(cab) > 8
        if cab_ok:
            partes.append(cab[0].upper() + cab[1:])
        n = c["n_homologaciones_zf"]
        d = ": ".join(partes[:1]) + (f". {partes[1]}" if cab_ok else "")
        if n:
            d += f". La lista de ZF recoge {n} homologaciones de productos comerciales"
        descs[f"ZF TE-ML {cod}"] = dict(description=d, segment="pesado", tipo=tipo_de(cab, c["lista"]), fuente=c["archivo"].replace("-ES.md", ""), productos_aprobados=n)
    SAL1.write_text(json.dumps(dict(aplicaciones=apl, clases=clases), ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    SAL2.write_text(json.dumps(descs, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(f"{len(clases)} clases en {len({c['lista'] for c in clases.values()})} listas; productos totales: {sum(len(c['productos']) for c in clases.values())}")
    for k in ("ZF TE-ML 05A", "ZF TE-ML 14A", "ZF TE-ML 04D", "ZF TE-ML 25C"):
        print(k, "|", descs.get(k, {}).get("description"))


if __name__ == "__main__":
    main()
