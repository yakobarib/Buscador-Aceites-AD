"""Convierte los Excel (.xlsx) y Word (.docx) de BASE DE CONOCIMIENTO a Markdown en el vault.

Uso:  python office_to_md.py

- xlsx: UN fichero .md por hoja  ->  FUENTES_MD/<ruta>/<libro> [hoja].md
        Cada fila lleva su numero de fila ORIGINAL de Excel (columna "fila") para poder
        citar "libro > hoja > fila N" como fuente de cualquier dato de la wiki.
        Se quitan filas y columnas totalmente vacias; el resto se respeta tal cual.
- docx: UN fichero .md con encabezados, parrafos y tablas en orden.
- El original NO se toca: sigue siendo la fuente de verdad.
"""
import re
import sys
from pathlib import Path

import openpyxl
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

RAIZ = Path(__file__).resolve().parent
ORIGEN = RAIZ / "BASE DE CONOCIMIENTO"
DESTINO = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "FUENTES_MD"


def celda(v):
    if v is None:
        return ""
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return " ".join(str(v).replace("|", "/").split())


def nombre_seguro(s):
    return re.sub(r'[\\/:*?"<>|]', "-", s).strip()


def tabla_md(cabecera, filas):
    n = len(cabecera)
    out = ["| " + " | ".join(cabecera) + " |", "|" + "---|" * n]
    out += ["| " + " | ".join(f + [""] * (n - len(f))) + " |" for f in filas]
    return "\n".join(out)


def convertir_xlsx(path: Path):
    rel = path.relative_to(ORIGEN)
    origen = rel.as_posix()
    wb = openpyxl.load_workbook(path, data_only=True)
    hechos = []
    for ws in wb.worksheets:
        filas = []
        for i, fila in enumerate(ws.iter_rows(values_only=True), 1):
            vals = [celda(v) for v in fila]
            if any(vals):
                filas.append((i, vals))
        if not filas:
            continue
        ncols = max(len(v) for _, v in filas)
        usadas = [c for c in range(ncols) if any(c < len(v) and v[c] for _, v in filas)]
        cuerpo = [[str(i)] + [v[c] if c < len(v) else "" for c in usadas] for i, v in filas]
        letras = [openpyxl.utils.get_column_letter(c + 1) for c in usadas]
        cab = ["fila"] + letras  # letra de columna Excel original, para citar celdas exactas
        md = (
            "---\n"
            f'origen: "{origen}"\n'
            f'hoja: "{ws.title}"\n'
            f"filas: {len(filas)}\n"
            f"columnas: {len(usadas)}\n"
            f"estado: {'ok' if ws.sheet_state == 'visible' else 'hoja_oculta'}\n"
            "tipo: fuente_xlsx\n"
            "---\n\n"
            f"# {path.stem} · {ws.title}\n\n"
            "> Primera columna = nº de fila original en Excel; las demás llevan la letra de columna original.\n\n"
            + tabla_md(cab, cuerpo)
            + "\n"
        )
        salida = DESTINO / rel.parent / f"{nombre_seguro(path.stem)} - {nombre_seguro(ws.title)}.md"
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(md, encoding="utf-8")
        hechos.append((origen, ws.title, len(filas), "ok"))
    return hechos


def recorrer_docx(doc):
    for hijo in doc.element.body.iterchildren():
        if hijo.tag.endswith("}p"):
            yield Paragraph(hijo, doc)
        elif hijo.tag.endswith("}tbl"):
            yield Table(hijo, doc)


def convertir_docx(path: Path):
    rel = path.relative_to(ORIGEN)
    origen = rel.as_posix()
    doc = Document(path)
    partes = []
    ntab = 0
    for el in recorrer_docx(doc):
        if isinstance(el, Paragraph):
            t = " ".join(el.text.split())
            if not t:
                continue
            m = re.match(r"(?:Heading|Título|Titulo)\s*(\d)", el.style.name or "", re.I)
            partes.append(("#" * (int(m.group(1)) + 1) + " " + t) if m else t)
        else:
            ntab += 1
            filas = [[celda(c.text) for c in r.cells] for r in el.rows]
            filas = [f for f in filas if any(f)]
            if filas:
                n = max(len(f) for f in filas)
                filas = [f + [""] * (n - len(f)) for f in filas]
                partes.append(tabla_md(filas[0], filas[1:]))
    cuerpo = "\n\n".join(partes)
    chars = len(cuerpo.replace("\n", "").replace(" ", ""))
    md = (
        "---\n"
        f'origen: "{origen}"\n'
        f"tablas: {ntab}\n"
        f"caracteres: {chars}\n"
        f"estado: {'ok' if chars > 100 else 'sin_texto'}\n"
        "tipo: fuente_docx\n"
        "---\n\n"
        f"# {path.stem}\n\n" + cuerpo + "\n"
    )
    salida = (DESTINO / rel).with_suffix(".md")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(md, encoding="utf-8")
    return [(origen, "(documento)", ntab, "ok" if chars > 100 else "sin_texto")]


def main():
    resultados, errores = [], []
    ficheros = sorted(p for p in ORIGEN.rglob("*") if p.suffix.lower() in (".xlsx", ".docx") and not p.name.startswith("~$"))
    for p in ficheros:
        try:
            resultados += convertir_xlsx(p) if p.suffix.lower() == ".xlsx" else convertir_docx(p)
        except Exception as e:
            errores.append((p.relative_to(ORIGEN).as_posix(), repr(e)))
    print(f"{len(ficheros)} ficheros -> {len(resultados)} .md · errores: {len(errores)}")
    for r in resultados:
        print(f"  {r[3]:9} {r[0]} [{r[1]}] ({r[2]})")
    for e in errores:
        print("  ERROR", e)


if __name__ == "__main__":
    main()
