"""Convierte todos los PDF de BASE DE CONOCIMIENTO a Markdown dentro del vault de Obsidian.

Uso:  python pdf_to_md.py [--solo "subcarpeta"] [--forzar]

- Entrada (inmutable): BASE DE CONOCIMIENTO/**/*.pdf
- Salida: OBSIDIAN/Buscador Aceites/FUENTES_MD/<misma ruta>.md
- Cada .md lleva frontmatter YAML (origen, paginas, caracteres, estado) para que
  Obsidian/Dataview puedan listar y auditar las conversiones.
- Las tablas se convierten a tablas Markdown; el texto fuera de tablas va en orden de lectura.
- PDFs sin texto (escaneados) se marcan estado: sin_texto para tratarlos con OCR aparte.
- Informe final en OBSIDIAN/Buscador Aceites/FUENTES_MD/_informe_conversion.md
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pymupdf

RAIZ = Path(__file__).resolve().parent
ORIGEN = RAIZ / "BASE DE CONOCIMIENTO"
DESTINO = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "FUENTES_MD"
MIN_CHARS_POR_PAGINA = 40  # por debajo => probablemente escaneado


def tabla_a_md(filas):
    filas = [[(c or "").replace("\n", " ").replace("|", "/").strip() for c in f] for f in filas if f]
    if not filas:
        return ""
    n = max(len(f) for f in filas)
    filas = [f + [""] * (n - len(f)) for f in filas]
    out = ["| " + " | ".join(filas[0]) + " |", "|" + "---|" * n]
    out += ["| " + " | ".join(f) + " |" for f in filas[1:]]
    return "\n".join(out)


def pagina_a_md(pag):
    try:
        tablas = [] if os.environ.get("SIN_TABLAS") else pag.find_tables().tables
    except Exception:
        tablas = []
    cajas = [pymupdf.Rect(t.bbox) for t in tablas]
    items = []  # (y, x, texto)
    for b in pag.get_text("blocks"):
        x0, y0, x1, y1, txt, _, tipo = b[:7]
        if tipo != 0 or not txt.strip():
            continue
        centro = pymupdf.Point((x0 + x1) / 2, (y0 + y1) / 2)
        if any(c.contains(centro) for c in cajas):
            continue
        items.append((y0, x0, " ".join(txt.split())))
    for t, c in zip(tablas, cajas):
        try:
            filas = [[(" ".join(pag.get_textbox(pymupdf.Rect(c)).split()) if c else "") for c in r.cells]
                     for r in t.rows]
            md = tabla_a_md(filas)
        except Exception:
            md = ""
        if md:
            items.append((c.y0, c.x0, "\n" + md + "\n"))
    items.sort(key=lambda i: (round(i[0] / 4), i[1]))
    return "\n\n".join(i[2] for i in items)


def convertir(pdf: Path):
    rel = pdf.relative_to(ORIGEN)
    salida = (DESTINO / rel).with_suffix(".md")
    doc = pymupdf.open(pdf)
    paginas = []
    for i, pag in enumerate(doc, 1):
        paginas.append(f"<!-- pagina {i} -->\n" + pagina_a_md(pag))
    cuerpo = "\n\n".join(paginas)
    chars = len(cuerpo.replace("\n", "").replace(" ", ""))
    estado = "ok" if chars >= MIN_CHARS_POR_PAGINA * max(len(doc), 1) else "sin_texto"
    origen = str(rel).replace("\\", "/")
    fm = (
        "---\n"
        f'origen: "{origen}"\n'
        f"paginas: {len(doc)}\n"
        f"caracteres: {chars}\n"
        f"estado: {estado}\n"
        "tipo: fuente_pdf\n"
        "---\n\n"
        f"# {pdf.stem}\n\n"
    )
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(fm + cuerpo + "\n", encoding="utf-8")
    return origen, len(doc), chars, estado


def convertir_aislado(pdf: Path):
    """Convierte un PDF en un proceso aparte: si la libreria cae o se cuelga, solo falla ese PDF.
    Si cae, se reintenta sin detectar tablas (la deteccion es lo que suele provocar el fallo)."""
    for sin_tablas in (False, True):
        env = {**os.environ, **({"SIN_TABLAS": "1"} if sin_tablas else {})}
        r = subprocess.run([sys.executable, __file__, "--uno", str(pdf)], capture_output=True,
                           text=True, encoding="utf-8", timeout=600, env=env)
        if r.returncode == 0:
            if sin_tablas:  # dejar constancia en el propio .md
                md = (DESTINO / pdf.relative_to(ORIGEN)).with_suffix(".md")
                t = md.read_text(encoding="utf-8").replace("tipo: fuente_pdf", "tipo: fuente_pdf\nsin_tablas: true", 1)
                md.write_text(t, encoding="utf-8")
            return
    raise RuntimeError(f"codigo {r.returncode}: {r.stderr.strip()[-200:]}")


def informe():
    filas, sin = 0, []
    for f in sorted(DESTINO.rglob("*.md")):
        if f.name.startswith("_"):
            continue
        cab = f.read_text(encoding="utf-8")[:500]
        if "tipo: fuente_pdf" not in cab:
            continue
        filas += 1
        if "estado: ok" not in cab:
            sin.append(f.relative_to(DESTINO).as_posix())
    return filas, sin


def main():
    args = sys.argv[1:]
    if "--uno" in args:
        convertir(Path(args[args.index("--uno") + 1]))
        return
    solo = args[args.index("--solo") + 1] if "--solo" in args else None
    forzar = "--forzar" in args
    pdfs = sorted(p for p in ORIGEN.rglob("*.pdf") if not solo or solo.lower() in str(p).lower())
    pendientes = [p for p in pdfs if forzar or not (DESTINO / p.relative_to(ORIGEN)).with_suffix(".md").exists()]
    print(f"{len(pdfs)} PDF, {len(pendientes)} pendientes", flush=True)
    errores = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(convertir_aislado, p): p for p in pendientes}
        for n, f in enumerate(as_completed(futs), 1):
            try:
                f.result()
            except Exception as e:
                errores.append((futs[f].relative_to(ORIGEN).as_posix(), repr(e)))
            if n % 25 == 0:
                print(f"  {n}/{len(pendientes)}  ({time.time() - t0:.0f}s)", flush=True)

    DESTINO.mkdir(parents=True, exist_ok=True)
    total, sin = informe()
    inf = ["---", "tipo: informe", "---", "", "# Informe de conversión PDF → Markdown", "",
           f"PDF convertidos en total: {total} de {len(pdfs)} · Errores en la última pasada: {len(errores)}", "",
           f"## Sin texto (posible OCR): {len(sin)}", ""] + [f"- {x}" for x in sin]
    inf += ["", f"## Errores última pasada: {len(errores)}", ""] + [f"- {a}: {b}" for a, b in errores]
    (DESTINO / "_informe_conversion.md").write_text("\n".join(inf) + "\n", encoding="utf-8")
    print(f"Hecho en {time.time() - t0:.0f}s · total={total} sin_texto={len(sin)} errores={len(errores)}")


if __name__ == "__main__":
    main()
