"""Extrae por REGLAS (sin IA) los datos de las fichas tecnicas Repsol convertidas a Markdown.

Uso:  python extract_fichas_repsol.py

Entrada : OBSIDIAN/Buscador Aceites/FUENTES_MD/FICHAS TÉCNICAS/REPSOL/*  (cuatro carpetas)
Salida  : fichas_repsol_extraidas.json  (lo lee build_wiki.py)

Las fichas Repsol tienen dos bloques estructurados:
  1) "Niveles de calidad, homologaciones y recomendaciones": vinetas "• API: SN*", "• ACEA: A1/B1, C5"...
     El asterisco final marca una HOMOLOGACION FORMAL (leyenda "*Homologación formal"); sin asterisco es recomendacion.
  2) "Características técnicas": tabla propiedad | unidad | metodo | valor(es).
Se conserva cada valor tal cual viene (con coma decimal y signos < > ‹ ›): no se convierte nada.
Lo que no se puede leer con seguridad (texto libre en las vinetas) se aparta, no se enlaza.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
FICHAS = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "FUENTES_MD" / "FICHAS TÉCNICAS" / "REPSOL"
SALIDA = RAIZ / "fichas_repsol_extraidas.json"
MESES = "Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre"
ESTANDARES = ("ACEA", "API", "ILSAC", "JASO")
PROPIEDADES = [  # (campo, regex sobre la etiqueta de la fila)
    ("grado_sae", r"^grado sae"),
    ("densidad_15c", r"^densidad"),
    ("visc_40c", r"viscosidad.*\b40"),
    ("visc_100c", r"viscosidad.*\b100"),
    ("indice_viscosidad", r"[ií]ndice de viscosidad"),
    ("punto_inflamacion", r"inflamaci"),
    ("punto_vertido", r"vertido|congelaci"),
    ("tbn", r"^t\.? ?b\.? ?n"),
    ("cenizas_sulfatadas", r"cenizas"),
]


def celdas(linea):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def titulos(texto):
    """Nombres de producto de las dos primeras lineas con contenido ('Lubricantes Vehículo Pesado GIANT 1010 SAE 50')."""
    out = []
    for l in [l.strip() for l in texto.splitlines() if l.strip() and not l.startswith(("|", "#"))][:3]:
        m = re.search(r"\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9]{2,}\b.*)$", l)
        if m and not l.startswith(("Niveles", "Descripción", "Ficha")) and len(m.group(1)) <= 60 and not re.search(r"[•.]", m.group(1)):
            out.append(m.group(1).strip())
    return out[:2]


def niveles(texto):
    """Lista de {'literal', 'formal'} de la seccion de homologaciones. Devuelve (lista, texto_libre)."""
    cab = re.search(r"(Niveles de calidad, homologaciones y recomendaciones|Quality levels, approvals and recommendations)", texto)
    if not cab:
        return [], []
    sec = texto[cab.start():]
    fin = min([j for j in (sec.find("Características"), sec.find("Technical"), sec.find("Las fichas de datos"),
                           sec.find("Safety data"), sec.find("Ficha técnica Lubricantes")) if j > 0] or [len(sec)])
    sec = re.sub(r"(Niveles de calidad, homologaciones y recomendaciones|Quality levels, approvals and recommendations)", " ", sec[:fin])
    sec = re.sub(r"\*(Homologación formal|Formal approval)", " ", sec)
    sec = " ".join(sec.split())
    trozos = [t for t in re.split(r"\s*•\s*", sec) if t.strip()]
    if "•" not in sec:  # formato de motos: "- JASO M345 FD* - API TC - Aprilia DFI"
        trozos = [t for t in re.split(r"(?:^|\s)-\s+", sec) if t.strip()]
    lista, libre = [], []
    for t in trozos:
        t = t.strip()
        formal = t.endswith("*")
        t = t.rstrip("*").strip()
        t = re.sub(r"^([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ ]*?):\s*", lambda m: m.group(1) + " ", t)  # "API: SN" -> "API SN"
        if not t:
            continue
        if re.search(r"\b(que|para|según|requieren|recomend\w+)\b", t, re.I):
            libre.append(t)
        else:
            lista.append({"literal": t, "formal": formal})
    return lista, libre


def tabla(texto):
    filas, vistos = [], set()
    for l in texto.splitlines():
        if not l.startswith("|") or l.startswith("|--") or l.startswith("|---"):
            continue
        c = celdas(l)
        if len(c) < 4 or not c[0] or c[0].upper() in ("UNIDAD",):
            continue
        valores = [v for v in c[3:] if v]
        if not valores or len(c[0]) > 60:
            continue
        clave = (c[0], c[2], tuple(valores))
        if clave in vistos:
            continue
        vistos.add(clave)
        filas.append({"propiedad": c[0], "unidad": c[1], "metodo": c[2], "valores": valores})
    return filas


def extraer(md):
    t = md.split("---", 2)[-1]
    t = re.sub(r"<!-- pagina \d+ -->", "\n", t)
    r = {"titulos": titulos(t), "codigos_rp": list(dict.fromkeys(re.findall(r"RP_[0-9A-Z]{5}", t))), "fecha": "", "niveles": [],
         "texto_libre": [], "tabla": [], "props": {}, "avisos": []}
    m = re.search(rf"\b({MESES})\s+(?:de\s+)?(\d{{4}})", t)
    if m:
        r["fecha"] = f"{m.group(1)} {m.group(2)}"
    r["niveles"], r["texto_libre"] = niveles(t)
    r["tabla"] = tabla(t)
    for f in r["tabla"]:
        for campo, patron in PROPIEDADES:
            if campo not in r["props"] and re.search(patron, f["propiedad"], re.I):
                r["props"][campo] = f["valores"]
    if not r["tabla"]:
        r["avisos"].append("sin tabla de características")
    if not r["niveles"] and not r["texto_libre"]:
        r["avisos"].append("sin sección de homologaciones")
    return r


def main():
    datos = {}
    for md in sorted(FICHAS.rglob("*.md")):
        datos[f"{md.parent.name}/{md.stem}"] = extraer(md.read_text(encoding="utf-8"))
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    n = len(datos)
    cnt = lambda f: sum(1 for d in datos.values() if f(d))
    print(f"{n} fichas")
    print(f"  con título: {cnt(lambda d: d['titulos'])} · código RP: {cnt(lambda d: d['codigos_rp'])} · fecha: {cnt(lambda d: d['fecha'])}")
    print(f"  con homologaciones: {cnt(lambda d: d['niveles'])} · con tabla: {cnt(lambda d: d['tabla'])} · con grado SAE: {cnt(lambda d: 'grado_sae' in d['props'])}")
    print(f"  con texto libre apartado: {cnt(lambda d: d['texto_libre'])} · con avisos: {cnt(lambda d: d['avisos'])}")
    print("  por carpeta:", {c.name: sum(1 for k in datos if k.startswith(c.name + "/")) for c in FICHAS.iterdir() if c.is_dir()})


if __name__ == "__main__":
    main()
