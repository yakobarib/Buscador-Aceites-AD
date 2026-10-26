"""Sube la version del buscador en TODOS los sitios donde se muestra (pie de pagina, Acerca de y Changelog).

Uso:  python bump_version.py "Novedad 1" "Novedad 2" ...      -> v30 pasa a v31 (la siguiente), con la fecha de hoy
      python bump_version.py --version v35 "Novedad"          -> fija un numero concreto
      python bump_version.py --ver                            -> solo dice la version actual
      python bump_version.py --refrescar-fecha                -> misma version, fecha de hoy

Ejecutalo UNA vez por cada subida a la web, antes del commit. La version actual se lee del panel "Acerca de".
"""
import re
import sys
from datetime import date
from pathlib import Path

RUTA = Path(__file__).resolve().parent / "index.html"
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_CORTOS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def main():
    args = sys.argv[1:]
    html = RUTA.read_text(encoding="utf-8")
    actual = re.search(r'<span class="about-version">(v\d+)</span>', html).group(1)
    if "--ver" in args:
        print(actual)
        return
    if "--refrescar-fecha" in args:  # misma version, fecha de hoy (por si la subida se hace otro dia que el bump)
        hoy = date.today()
        pie = f"{actual} · {hoy.day} {MESES_CORTOS[hoy.month - 1]} {hoy.year}"
        html = re.sub(r'<span class="app-ver">.*?</span>', f'<span class="app-ver">{pie}</span>', html, count=1)
        html = re.sub(r'(<div class="changelog-version">' + actual + r' <span class="changelog-date">)[^<]*(</span>)',
                      lambda m: m.group(1) + f"{MESES[hoy.month - 1]} {hoy.year}" + m.group(2), html, count=1)
        RUTA.write_text(html, encoding="utf-8")
        print(f"fecha refrescada: {pie}")
        return
    nueva = None
    if "--version" in args:
        i = args.index("--version")
        nueva = args[i + 1]
        del args[i:i + 2]
    nueva = nueva or f"v{int(actual[1:]) + 1}"
    novedades = [a for a in args if a.strip()]
    if not novedades:
        sys.exit("Indica al menos una novedad entre comillas.")
    hoy = date.today()
    pie = f'{nueva} · {hoy.day} {MESES_CORTOS[hoy.month - 1]} {hoy.year}'
    # 1) pie de pagina
    html, n1 = re.subn(r'<span class="app-ver">.*?</span>', f'<span class="app-ver">{pie}</span>', html, count=1)
    if n1 == 0:
        html = html.replace("<code>DEMO</code> &nbsp;·&nbsp; Diseñado por",
                            f'<code>DEMO</code> &nbsp;·&nbsp; <span class="app-ver">{pie}</span> &nbsp;·&nbsp; Diseñado por', 1)
    # 2) Acerca de
    html = re.sub(r'<span class="about-version">v\d+</span>', f'<span class="about-version">{nueva}</span>', html, count=1)
    # 3) Changelog (entrada nueva arriba del todo)
    lis = "\n".join(f"            <li>{n}</li>" for n in novedades)
    entrada = (f'        <div class="changelog-entry">\n'
               f'          <div class="changelog-version">{nueva} <span class="changelog-date">{MESES[hoy.month - 1]} {hoy.year}</span></div>\n'
               f'          <ul class="changelog-list">\n{lis}\n          </ul>\n        </div>\n')
    ancla = '<div class="help-panel" data-panel="changelog">\n'
    assert ancla in html, "no encuentro el panel de changelog"
    html = html.replace(ancla, ancla + entrada, 1)
    RUTA.write_text(html, encoding="utf-8")
    print(f"{actual} -> {nueva} ({pie})")


if __name__ == "__main__":
    main()
