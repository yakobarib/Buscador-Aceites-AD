"""Genera en la wiki las paginas de los catalogos de Castrol que NO estan en la tarifa (moto, nautica y competicion, robotica
industrial y los productos agricolas sin referencia), a partir de los castrol_curado_*.json (transcritos leyendo cada PDF como imagen).

Uso:  python ingesta_catalogos_castrol.py

Salida: OBSIDIAN/Buscador Aceites/WIKI/conocimiento/Castrol - <area>.md  (build_wiki.py no borra la carpeta conocimiento/)
Cada producto lleva su pagina del PDF, sus niveles y homologaciones con enlaces [[...]] a las paginas de norma que ya existen,
lo que el PDF solo recomienda o declara que cumple (aparte) y las dudas de la transcripcion. Sin verificar a mano.
"""
import json
import re
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
WIKI = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "WIKI"
SALIDA = WIKI / "conocimiento"
AREAS = [
    ("moto", "Castrol - Gama moto (catálogos)", "motocicleta"),
    ("nautica", "Castrol - Náutica y competición (catálogos)", "nautica-competicion"),
    ("robotica", "Castrol - Robótica e industrial (catálogo)", "industrial"),
    ("agricola", "Castrol - Gama agrícola (catálogo)", "agricola"),
]


def normas_existentes():
    d = WIKI / "normas"
    return {p.stem.upper(): p.stem for p in d.glob("*.md")} if d.exists() else {}


def enlace(lit, existentes):
    """[[pagina]] si el literal coincide con una pagina de norma existente (sin tocar mayusculas); si no, texto plano."""
    k = lit.strip().upper()
    return f"[[{existentes[k]}]]" if k in existentes else lit


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    ex = normas_existentes()
    for clave_a, titulo, tema in AREAS:
        ruta = RAIZ / f"castrol_curado_{clave_a}.json"
        if not ruta.exists():
            continue
        d = json.loads(ruta.read_text(encoding="utf-8"))
        prods = d["productos"]
        fuentes = sorted({x.get("pdf") or d.get("fuente", "") for x in prods if (x.get("pdf") or d.get("fuente"))})
        fm = ["---", "tipo: conocimiento", f'titulo: "{titulo}"', f"fecha: {date.today()}", f'tema: "{tema}"', "origen: catálogos PDF de Castrol (lectura de página como imagen)",
              "verificado: false", "---", ""]
        cu = [f"# {titulo}", "",
              "Productos Castrol que **no figuran en la tarifa de abril 2026**; se guardan como conocimiento de referencia. Transcripción fiel del PDF "
              "(sin deducir): lo que el catálogo solo recomienda o dice que cumple va aparte. " +
              ("Fuentes: " + "; ".join(f"[[HOMOLOGACIONES/Castrol/{f.replace('.pdf', '')}]]" for f in fuentes) + "." if fuentes else ""), ""]
        for x in prods:
            cu += [f"## {x['nombre']}", ""]
            linea = [f"página {x['pagina']}" + (f" de {x['pdf']}" if x.get("pdf") else "")]
            if x.get("familia"):
                linea.insert(0, x["familia"])
            if x.get("viscosidad"):
                linea.append(x["viscosidad"])
            cu.append("*" + " · ".join(linea) + "*")
            if x.get("descripcion"):
                cu += ["", x["descripcion"]]
            cu.append("")
            if x.get("niveles"):
                cu.append("- **Niveles de industria:** " + " · ".join(enlace(n, ex) for n in x["niveles"]))
            if x.get("homologaciones"):
                cu.append("- **Homologaciones:** " + " · ".join(enlace(n, ex) for n in x["homologaciones"]))
            if x.get("cumple"):
                cu.append("- **Cumple, recomendado o apto para (no es homologación formal):** " + " · ".join(x["cumple"]))
            if x.get("formatos"):
                cu.append("- **Formatos:** " + ", ".join(x["formatos"]))
            if x.get("dudas"):
                cu.append("- **Dudas de la transcripción:** " + " | ".join(x["dudas"]))
            cu.append("")
        dg = d.get("dudas_generales") or []
        if dg:
            cu += ["## Notas de la transcripción", ""] + [f"- {t}" for t in dg] + [""]
        (SALIDA / f"{titulo}.md").write_text("\n".join(fm + cu), encoding="utf-8")
        print(f"{titulo}: {len(prods)} productos")


if __name__ == "__main__":
    main()
