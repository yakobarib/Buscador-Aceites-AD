"""Extrae las matrices de homologaciones de Castrol VEHICULO PESADO (Wallchart CVO) leyendo el PDF con posiciones y colores.

Uso:  python extract_homologaciones_castrol_pesado.py

Entrada : BASE DE CONOCIMIENTO/HOMOLOGACIONES/Castrol/Castrol - CVO Wallchart - Oct 2026.pdf (paginas 2 y 3: matrices)
          BASE DE CONOCIMIENTO/HOMOLOGACIONES/Castrol/Castrol - Codigos CVO - Oct 2026.pdf (codigo de material, nombre y EAN)
Salida  : homologaciones_castrol_pesado_extraidas.json  (lo lee build_wiki.py)

El PDF distingue por COLOR: negro = homologacion actual; verde = retrocompatible (leyenda de la propia tabla).
Eso se pierde al convertir a Markdown, por eso se lee el PDF directamente: cada celda se reconstruye por posicion
(columna = producto, fila = fabricante o norma). Una celda ancha que cubre varias columnas se asigna a todas ellas.
Las lineas con 'Meets', 'Warranted', 'Recommended', 'Cumple los requisitos' se guardan aparte como 'cumple' (no son homologacion formal).
"""
import json
import re
from pathlib import Path

import pymupdf

RAIZ = Path(__file__).resolve().parent
PDF = RAIZ / "BASE DE CONOCIMIENTO" / "HOMOLOGACIONES" / "Castrol" / "Castrol - CVO Wallchart - Oct 2026.pdf"
PDF_COD = RAIZ / "BASE DE CONOCIMIENTO" / "HOMOLOGACIONES" / "Castrol" / "Castrol - Codigos CVO - Oct 2026.pdf"
SALIDA = RAIZ / "homologaciones_castrol_pesado_extraidas.json"
VERDE = 36415
RE_VISC = re.compile(r"^(\d{1,2}W-\d{2,3}|\d{1,2}W|\d{2})(\s+(CV\d|CF.*))?$")
CALIF = re.compile(r"(?i)\b(meets|warranted|recommended|cumple|requeriments?|requirements?)\b")
MARCAS = {"ACEA": "acea", "API": "api", "JASO": "jaso", "Global": "global", "CAT": "cat", "Cummins": "cummins", "DAF": "daf",
          "Daimler Trucks": "daimler", "Deutz": "deutz", "Ford": "ford", "Mack": "mack", "MAN": "man", "MTU": "mtu",
          "Renault Trucks": "renault", "Scania": "scania", "Volvo": "volvo", "Other claims": "otros"}


def clave(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper().replace("+", "PLUS"))


def lineas(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt:
                continue
            col = max(l["spans"], key=lambda s: len(s["text"].strip()))["color"]
            x0, y0, x1, y1 = l["bbox"]
            out.append(dict(t=re.sub(r"\s+", " ", txt), x0=x0, x1=x1, y=(y0 + y1) / 2, color=col))
    return out


PREF = {"acea": "ACEA", "api": "API", "jaso": "JASO", "global": "GLOBAL", "cat": "CATERPILLAR", "cummins": "CUMMINS", "daimler": "DAIMLER TRUCK",
        "deutz": "DEUTZ", "ford": "FORD", "mack": "MACK", "scania": "SCANIA", "renault": "RENAULT", "volvo": "VOLVO"}
# tokens validos de las filas ACEA / API / JASO / Global
RE_NIVEL = re.compile(r"(?<![A-Za-z0-9-])(CF/CF-2|DHD-\d|DH-\d|F\d{2}|FA-4|C[A-K]-4|C[A-K]|E\d{1,2}|SLD5|[A-C]\d(?:/[A-C]\d)?)(?![A-Za-z0-9-])")


def literales(fila, texto):
    """Convierte un trozo de celda en ([literales con marca], resto sin reconocer)."""
    t = " " + re.sub(r"(?i)cumple los requisitos de|categor[ií]a de lubricantes", " ", texto) + " "
    # errata confirmada por Yakoba el 2026-10-30 (decisiones.json, CASTROL-CVO-M32775): el PDF dice M32775 y es MAN M 3277
    t = t.replace("M32775", "M3277")
    out = []

    def toma(patron, fabrica):
        nonlocal t
        out.extend(fabrica(m) for m in re.finditer(patron, t))
        t = re.sub(patron, " ", t)

    if fila in ("acea", "api", "jaso", "global"):
        out.extend(f"{PREF[fila]} {m.group(1)}" for m in RE_NIVEL.finditer(t))
        t = RE_NIVEL.sub(" ", t)
    elif fila == "cat":
        toma(r"ECF-\d[a-zA-Z]?", lambda m: f"CATERPILLAR {m.group(0)}")
    elif fila == "cummins":
        toma(r"CES\s?(\d{5})", lambda m: f"CUMMINS CES {m.group(1)}")
    elif fila == "daimler":
        toma(r"DTFR\s?(\d{2}[A-Z]\d{3})", lambda m: f"DAIMLER TRUCK DTFR {m.group(1)}")
    elif fila == "deutz":
        toma(r"DQC\s?([IV]+-\d{2}(?: LA)?)", lambda m: f"DEUTZ DQC {m.group(1)}")
    elif fila == "ford":
        toma(r"WSS-M2C\d{3}-[A-Z]\d?", lambda m: f"FORD {m.group(0)}")
    elif fila == "mack":
        toma(r"EOS-[\d.]+|EO-[A-Z](?: Premium Plus| Plus)?", lambda m: f"MACK {m.group(0).upper()}")
    elif fila == "man":
        toma(r"M\s?(\d{3,4}(?:-\d)?)(?!\d)", lambda m: f"MAN {m.group(1)}")
    elif fila == "mtu":
        toma(r"MTU\s?(\d(?:\.\d)?)", lambda m: f"MTU TYPE {m.group(1)}")
    elif fila == "renault":
        toma(r"RLD-?\s?(\d)", lambda m: f"RENAULT RLD-{m.group(1)}")
    elif fila == "scania":
        toma(r"LDF-?\s?(\d)", lambda m: f"SCANIA LDF-{m.group(1)}")
    elif fila == "volvo":
        toma(r"VDS-?\s?([\d.]+)", lambda m: f"VOLVO VDS-{m.group(1)}")
        toma(r"CNG", lambda m: "VOLVO CNG")
    elif fila == "otros":
        toma(r"(?:DFS|Powerguard)\s?(93K\d{3})", lambda m: f"DETROIT DIESEL DFS {m.group(1)}")
        toma(r"MB\s?(2\d{2}\.\d{1,2})", lambda m: f"MB {m.group(1)}")
        for m in re.finditer(r"MAN\s+((?:M\s?\d{3,4}(?:-\d)?[, ]*)+)", t):
            out.extend(f"MAN {x}" for x in re.findall(r"M\s?(\d{3,4}(?:-\d)?)(?!\d)", m.group(1)))
        t = re.sub(r"MAN\s+(?:M\s?\d{3,4}(?:-\d)?[, ]*)+", " ", t)
    resto = re.sub(r"[,;:]|\s+", " ", t).strip()
    return list(dict.fromkeys(out)), resto


def agrupar_y(ls, hueco=11.0):
    ls = sorted(ls, key=lambda l: l["y"])
    grupos, act = [], []
    for l in ls:
        if act and l["y"] - act[-1]["y"] > hueco:
            grupos.append(act)
            act = []
        act.append(l)
    if act:
        grupos.append(act)
    return grupos


def matriz(page):
    ls = lineas(page)
    # etiquetas de fila (columna izquierda)
    etiquetas = [l for l in ls if l["x1"] < 240 and l["t"] in set(MARCAS) | {"Renault", "Trucks", "Daimler", "Other", "claims"}]
    ancla = [l for l in etiquetas if l["t"] in ("ACEA", "API")]
    if not ancla:
        return None
    y_tabla = min(l["y"] for l in ancla) - 6
    grupos = agrupar_y(etiquetas, 11.0)
    filas = []
    for g in grupos:
        nombre = " ".join(l["t"] for l in g)
        if nombre in MARCAS:
            filas.append((sum(l["y"] for l in g) / len(g), MARCAS[nombre], nombre))
    # columnas: celdas de viscosidad de la banda de color (por encima de la tabla)
    cab = [l for l in ls if l["y"] < y_tabla and l["x0"] > 240 and RE_VISC.match(l["t"])]
    cab = sorted(cab, key=lambda l: l["x0"])
    if not cab:
        return None
    ycab = min(l["y"] for l in cab)
    cab = [l for l in cab if abs(l["y"] - ycab) < 4]
    cols = [dict(visc=l["t"], cx=(l["x0"] + l["x1"]) / 2) for l in cab]
    for c in cols:
        # subtitulo (E8/E11, SLD5, FA-4/F01...) y grupo (Long Drain, Plus, Multi)
        cerca = [l for l in ls if abs((l["x0"] + l["x1"]) / 2 - c["cx"]) < 45 and l["x0"] > 240]
        sub = [l for l in cerca if 8 < l["y"] - ycab < 26 and l["y"] < y_tabla]
        grp = [l for l in cerca if -34 < l["y"] - ycab < -8]
        c["sub"] = " ".join(l["t"] for l in sorted(sub, key=lambda l: l["y"]))
        c["grupo"] = " ".join(l["t"] for l in grp if l["t"] not in ("GAMA", "ULTIMATE", "ENHANCED", "ESSENTIAL")).strip()
    # contenido de celdas: lineas bajo la cabecera, a la derecha de las etiquetas
    cuerpo = [l for l in ls if l["y"] > y_tabla and l["x0"] > 240 and l["y"] < max(f[0] for f in filas) + 40]
    cuerpo = [l for l in cuerpo if not re.match(r"(?i)(El envase|Da con el|Visita Castrol|Tipo de lubricante)", l["t"])]
    res = {i: {} for i in range(len(cols))}
    for i, c in enumerate(cols):
        c["cells"] = res[i]
    # agrupar por trozos contiguos en vertical, dentro de cada columna "ancla" (centro mas cercano) -> celda
    por_celda = {}
    for l in cuerpo:
        cx = (l["x0"] + l["x1"]) / 2
        cubiertas = [i for i, c in enumerate(cols) if l["x0"] - 2 <= c["cx"] <= l["x1"] + 2] or [min(range(len(cols)), key=lambda i: abs(cols[i]["cx"] - cx))]
        por_celda.setdefault(tuple(cubiertas), []).append(l)
    for cubiertas, lst in por_celda.items():
        for g in agrupar_y(lst, 11.0):
            ycen = sum(l["y"] for l in g) / len(g)
            f_real = min(filas, key=lambda f: abs(f[0] - ycen))[1]
            toks = []
            if f_real in ("daf", "ford", "otros"):
                toks.append({"t": " ".join(l["t"] for l in sorted(g, key=lambda l: l["y"])), "estado": "actual"})
            else:
                for l in sorted(g, key=lambda l: l["y"]):
                    for t in re.split(r",\s*", l["t"]):
                        t = t.strip(" ,")
                        if t:
                            toks.append({"t": t, "estado": "retro" if l["color"] == VERDE else "actual"})
            for i in cubiertas:
                res[i].setdefault(f_real, []).extend(toks)
    return cols


def codigos():
    doc = pymupdf.open(PDF_COD)
    out = {}
    for pg in doc:
        for tb in pg.find_tables().tables:
            for fila in tb.extract():
                if not fila or not fila[0] or not fila[1]:
                    continue
                mat = fila[0].split()
                if not mat or not re.fullmatch(r"[0-9A-Z]{5,7}", mat[-1]):
                    continue
                out[mat[-1]] = dict(nombre=re.sub(r"\s+", " ", fila[1]).strip(), ean=(fila[2] or "").strip(), ean_caja=((fila[3] if len(fila) > 3 else "") or "").strip())
    return out


def main():
    doc = pymupdf.open(PDF)
    productos = {}
    for n in (1, 2):
        cols = matriz(doc[n])
        if not cols:
            print(f"pagina {n + 1}: sin matriz")
            continue
        for c in cols:
            nombre = " ".join(x for x in (c["grupo"], c["visc"], c["sub"]) if x)
            actual, retro, cumple, sin = [], [], [], []
            for fila, toks in c["cells"].items():
                for t in toks:
                    txt = t["t"]
                    m = CALIF.search(txt) or re.search(r"(?i)completely suitable|Warranted", txt)
                    antes, despues = (txt[:m.start()], txt[m.start():]) if m else (txt, "")
                    for parte, destino in ((antes, retro if t["estado"] == "retro" else actual), (despues, cumple)):
                        if not parte.strip():
                            continue
                        lits, resto = literales(fila, parte)
                        destino.extend(lits)
                        if resto and re.search(r"[A-Za-z0-9]{3,}", resto) and not re.fullmatch(r"(?i)(ddc|meets|warranted by|castrol|to be completely suitable|for use in vehicles where the|following specifications apply|for iveco trucks requiring|requirements? of|requeriments?|euro vi|dm|ace|a|and|psql 2\.4|px|daf|extended drain)( .*)?", resto.strip()):
                            sin.append(f"{fila}: {resto}")
            ordena = lambda l: list(dict.fromkeys(l))
            productos[clave(nombre)] = dict(columna=nombre, pagina=n + 1, grupo=c["grupo"], visc=c["visc"], sub=c["sub"],
                                            actual=ordena(actual), retro=ordena(retro), cumple=ordena(cumple), sin_enlazar=ordena(sin),
                                            celdas_brutas={f: [x["t"] for x in toks] for f, toks in c["cells"].items()})
    cods = codigos()
    SALIDA.write_text(json.dumps(dict(productos=productos, codigos=cods, fuente=PDF.name), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"columnas/productos={len(productos)} codigos={len(cods)}")
    for k, v in productos.items():
        print(f"  [{v['pagina']}] {v['columna']:40} actual={len(v['actual']):3} retro={len(v['retro']):3} cumple={len(v['cumple']):2} sin_enlazar={len(v['sin_enlazar'])}")


if __name__ == "__main__":
    main()
