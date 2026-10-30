"""Ingesta a la wiki los Markdown que la tarea programada deja en BASE DE CONOCIMIENTO/WIKI DESCARGADOS.

Uso:  python ingesta_descargados.py

Cada archivo debe empezar con un bloque de metadatos entre '---' con: titulo, fecha (AAAA-MM-DD), tema y fuentes
(una o mas URL https, una por linea con '- '). Sin fuentes verificables el archivo se RECHAZA (carpeta rechazados/).
Los aceptados se copian a OBSIDIAN/Buscador Aceites/WIKI/conocimiento/ con su procedencia y enlaces [[...]] a las
paginas de norma que ya existen en la wiki; el original pasa a WIKI DESCARGADOS/procesados/.
build_wiki.py NO borra la carpeta conocimiento/ (solo regenera productos, familias, equivalencias, normas y oem).
NO toca index.html ni publica nada: lo que llegue al buscador sigue necesitando una decision expresa de Yakoba.
"""
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ENTRADA = RAIZ / "BASE DE CONOCIMIENTO" / "WIKI DESCARGADOS"
WIKI = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "WIKI"
SALIDA = WIKI / "conocimiento"
RE_URL = re.compile(r"https?://[^\s)>\]]+")


def leer_meta(texto):
    m = re.match(r"\s*---\s*\n(.*?)\n---\s*\n?(.*)", texto, re.S)
    if not m:
        return None, texto
    meta, clave_act = {}, None
    for linea in m.group(1).splitlines():
        if re.match(r"^\s*-\s+", linea) and clave_act:
            meta.setdefault(clave_act, []).append(re.sub(r"^\s*-\s+", "", linea).strip())
        elif ":" in linea:
            k, v = linea.split(":", 1)
            clave_act = k.strip().lower()
            v = v.strip().strip('"')
            meta[clave_act] = [] if not v else v
    return meta, m.group(2)


def nombres_de_normas():
    """Nombres de pagina de norma ya existentes en la wiki (para enlazarlos)."""
    d = WIKI / "normas"
    return sorted((p.stem for p in d.glob("*.md") if len(p.stem) >= 4), key=len, reverse=True) if d.exists() else []


def enlazar(cuerpo, normas):
    usadas = []
    bajo = cuerpo.lower()
    for n in normas:
        if re.search(r"(?<![\w.])" + re.escape(n.lower()) + r"(?![\w.])", bajo):
            usadas.append(n)
    return usadas[:40]


def nombre_seguro(s):
    return re.sub(r'[\\/:*?"<>|#^\[\]]+', " ", s).strip()[:90]


def main():
    ENTRADA.mkdir(parents=True, exist_ok=True)
    (ENTRADA / "procesados").mkdir(exist_ok=True)
    (ENTRADA / "rechazados").mkdir(exist_ok=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    normas = nombres_de_normas()
    registro, ok, mal = [], 0, 0
    for f in sorted(ENTRADA.glob("*.md")):
        if f.name.startswith("_"):
            continue
        texto = f.read_text(encoding="utf-8", errors="replace")
        meta, cuerpo = leer_meta(texto)
        motivo = None
        if not meta:
            motivo = "sin bloque de metadatos"
        else:
            fuentes = meta.get("fuentes") or []
            fuentes = fuentes if isinstance(fuentes, list) else [fuentes]
            urls = [u for s in fuentes for u in RE_URL.findall(s)]
            if not meta.get("titulo") or not isinstance(meta.get("titulo"), str):
                motivo = "falta titulo"
            elif not urls:
                motivo = "sin ninguna fuente https"
            elif len(cuerpo.strip()) < 300:
                motivo = "contenido demasiado corto"
        if motivo:
            shutil.move(str(f), str(ENTRADA / "rechazados" / f.name))
            registro.append(f"- RECHAZADO `{f.name}`: {motivo}")
            mal += 1
            continue
        titulo = meta["titulo"]
        fecha = meta.get("fecha") if isinstance(meta.get("fecha"), str) else str(date.today())
        tema = meta.get("tema") if isinstance(meta.get("tema"), str) else "general"
        rel = enlazar(titulo + "\n" + cuerpo, normas)
        fm = ["---", "tipo: conocimiento", f'titulo: "{titulo}"', f"fecha: {fecha}", f'tema: "{tema}"',
              f"ingerido: {date.today()}", "origen: internet (tarea programada)", "fuentes:"] + [f"  - {u}" for u in urls] + ["---", ""]
        pie = ["", "## Procedencia", "",
               f"Descargado de internet el {fecha} y añadido a la wiki el {date.today()} sin verificación manual. "
               "Si contradice una ficha técnica o una decisión confirmada, mandan estas últimas.", ""]
        pie += [f"- {u}" for u in urls]
        if rel:
            pie += ["", "## Normas relacionadas en la wiki", ""] + [f"- [[{n}]]" for n in rel]
        destino = SALIDA / f"{fecha} {nombre_seguro(titulo)}.md"
        destino.write_text("\n".join(fm) + f"# {titulo}\n\n" + cuerpo.strip() + "\n" + "\n".join(pie) + "\n", encoding="utf-8")
        shutil.move(str(f), str(ENTRADA / "procesados" / f.name))
        registro.append(f"- OK `{f.name}` → [[{destino.stem}]] ({len(urls)} fuentes, {len(rel)} normas enlazadas)")
        ok += 1
    # indice por tema
    por_tema = defaultdict(list)
    for p in sorted(SALIDA.glob("*.md")):
        if p.name == "index.md":
            continue
        m, _ = leer_meta(p.read_text(encoding="utf-8"))
        por_tema[(m or {}).get("tema", "general")].append(p.stem)
    idx = ["---", "tipo: indice", "---", "", "# Conocimiento descargado de internet", "",
           "Páginas añadidas por la tarea programada nocturna. Cada una cita sus fuentes; no están verificadas una a una.", ""]
    for t in sorted(por_tema):
        idx += [f"## {t}", ""] + [f"- [[{n}]]" for n in reversed(por_tema[t])] + [""]
    (SALIDA / "index.md").write_text("\n".join(idx), encoding="utf-8")
    if registro:
        log = ENTRADA / "_registro.md"
        previo = log.read_text(encoding="utf-8") if log.exists() else "# Registro de ingestas\n"
        log.write_text(previo + f"\n## {date.today()}\n\n" + "\n".join(registro) + "\n", encoding="utf-8")
    print(f"ingeridos={ok} rechazados={mal}")


if __name__ == "__main__":
    sys.exit(main())
