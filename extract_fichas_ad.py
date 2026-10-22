"""Extrae por REGLAS (sin IA) datos fiables de las fichas tecnicas AD Parts ya convertidas a Markdown.

Uso:  python extract_fichas_ad.py

Entrada : OBSIDIAN/Buscador Aceites/FUENTES_MD/FICHAS TÉCNICAS/AD PARTS/{Aceites AD Normal,Aceites AD Standard}
Salida  : fichas_ad_extraidas.json  (lo lee build_wiki.py)  + resumen por pantalla

Solo se extrae lo que se puede leer sin ambiguedad: titulo, tipo de producto, grado SAE, especificaciones
y aprobaciones (ACEA/API/ILSAC/JASO + filas de homologaciones OEM), formatos y fecha.
NO se extraen propiedades numericas (densidad, viscosidades...): salen mezcladas en las tablas.
Cada campo que no se encuentra queda vacio; nada se rellena por deduccion.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
FICHAS = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "FUENTES_MD" / "FICHAS TÉCNICAS" / "AD PARTS"
CARPETAS = ["Aceites AD Normal", "Aceites AD Standard"]
SALIDA = RAIZ / "fichas_ad_extraidas.json"
RE_GRADO = re.compile(r"(\d{1,2}W-?\d{2,3}|(?<![\d.,])\d{2,3}(?![\d.,W]))")
RE_VISC_TITULO = re.compile(r"(?<![0-9A-Za-z])(\d{1,2}W-?\d{2,3})(?![0-9])", re.I)
CLAVES_ESTANDAR = {"ACEA": "acea", "API": "api", "ILSAC": "ilsac", "JASO": "jaso"}
MARCAS_COMPUESTAS = {"JOHN DEERE", "MASSEY FERGUSSON", "DETROIT DIESEL", "PARKER DENISON", "ARVIN MERITOR",
                     "MAG IAS", "ZF TE-ML", "PSA PEUGEOT CITROËN", "JAGUAR-LAND ROVER"}
CANON_MARCA = {"MB-APPROVAL": "MB", "PSA PEUGEOT CITROËN": "PSA"}  # solo cambios de escritura evidentes
PALABRAS_MARCA = set()  # se rellena en main() con las etiquetas simples frecuentes


def expandir(marca, valor):
    """'ZF' + 'TE-ML 04D/14A' -> ['ZF TE-ML 04D', 'ZF TE-ML 14A'] (las partes sin prefijo heredan el del primero)."""
    marca = CANON_MARCA.get(marca.upper(), marca)
    partes = [p.strip() for p in re.split(r"\s*[/,;]\s*", valor) if p.strip()]
    m = re.search(r"\d", partes[0]) if partes else None
    pref = partes[0][: m.start()] if m else ""
    out = []
    for i, p in enumerate(partes):
        if i and pref and re.fullmatch(r"\d[\w.\-]*", p):
            p = pref + p
        out.append(f"{marca} {p}")
    return out


def es_ambiguo(marca, valor):
    """Fila de celdas combinadas del PDF: varias marcas en la etiqueta o nombres de otras marcas dentro del valor."""
    if marca.upper() not in MARCAS_COMPUESTAS and len(marca.split()) >= 2:
        return True
    return bool(set(re.findall(r"[A-ZÁÉÍÓÚÑ]{2,}", valor)) & PALABRAS_MARCA)


def celdas(linea):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def texto_ficha(md):
    t = md.split("---", 2)[-1]
    return re.sub(r"<!-- pagina \d+ -->", "", t)


def trocear(valor):
    return [x.strip() for x in re.split(r"\s*(?:/|,|;)\s*", valor) if x.strip()]


def extraer(md):
    t = texto_ficha(md)
    lineas = [l.rstrip() for l in t.splitlines()]
    r = dict(titulo="", tipo_producto="", grado_sae="", acea=[], api=[], ilsac=[], jaso=[], oem=[],
             spec_texto="", formatos=[], fecha="", avisos=[])
    # titulo: primera linea con contenido que no sea ruido
    cuerpo = [l for l in lineas if l.strip() and l.strip() not in ("q", "´´") and not l.startswith("# ")]
    if cuerpo:
        r["titulo"] = cuerpo[0].strip()
    ti = t.find("INFORMACIÓN PRODUCTO")
    # zona de especificaciones: desde el titulo hasta la primera tabla de valores tipicos
    corte = [i for i in (t.find("Densidad a 15"), t.find("Grado de viscosidad"), t.find("Valores típicos")) if i >= 0]
    zona = t[: min(corte)] if corte else t[:600]
    # tipo de producto
    m = re.search(r"INFORMACIÓN PRODUCTO(.*?)(?:Especificaciones y aprobaciones|\n\|)", zona, re.S)
    if m:
        r["tipo_producto"] = " ".join(m.group(1).split())[:140]
    # (a) tabla etiqueta | valor
    for l in zona.splitlines():
        if l.startswith("|") and not l.startswith("|--") and not l.startswith("|---"):
            c = celdas(l)
            if len(c) >= 2 and c[0] and c[1]:
                etq = c[0].upper()
                if etq in CLAVES_ESTANDAR:
                    r[CLAVES_ESTANDAR[etq]] += trocear(c[1])
                else:
                    r["oem"].append({"marca": c[0], "valor": " ".join(c[1:]).strip()})
    # (b) texto libre "API SN RC ILSAC GF-6A Valores tipicos" antes de la tabla
    texto = " ".join(re.sub(r"\|.*", " ", zona.split("Especificaciones y aprobaciones", 1)[-1]).split()) if "Especificaciones y aprobaciones" in zona else ""
    texto = re.sub(r"\s*Valores típicos.*", "", texto)
    if texto:
        r["spec_texto"] = texto
        partes = re.split(r"\b(ACEA|API|ILSAC|JASO)\b", texto)
        for i in range(1, len(partes) - 1, 2):
            r[CLAVES_ESTANDAR[partes[i]]].append(" ".join(partes[i + 1].split()))
    # grado SAE
    m = re.search(r"Grado de viscosidad[^\n]*", t)
    if m:
        g = RE_GRADO.search(m.group(0).split("|", 2)[-1] if "|" in m.group(0) else m.group(0)[20:])
        if g:
            r["grado_sae"] = g.group(1).upper().replace("-", "")
    gt = RE_VISC_TITULO.search(r["titulo"])
    if gt and r["grado_sae"] and gt.group(1).upper().replace("-", "") != r["grado_sae"]:
        r["avisos"].append(f'grado del título ({gt.group(1)}) distinto del grado de la tabla ({r["grado_sae"]})')
    # formatos y fecha
    m = re.search(r"envases? de ([^.\n]+)", t, re.I)
    if m:
        r["formatos"] = [x.replace(",", ".") for x in re.findall(r"(\d+(?:[.,]\d+)?)\s*l\b", m.group(1), re.I)]
    m = re.search(r"Fecha:\s*(\d{1,2}/\d{4})", t)
    if m:
        r["fecha"] = m.group(1)
    # MIL dentro de la linea de especificaciones ("API GL-5 (LS) MIL L-2105-D") es otra norma, no parte del API
    api_limpio = []
    for v in r["api"]:
        m = re.match(r"(.*?)\s*\bMIL\b\s*(.*)", v)
        if m:
            if m.group(1):
                api_limpio.append(m.group(1))
            r["oem"].append({"marca": "MIL", "valor": m.group(2), "_de_texto": True})
        else:
            api_limpio.append(v)
    r["api"] = api_limpio
    for k in ("acea", "api", "ilsac", "jaso"):  # quitar duplicados conservando orden
        r[k] = list(dict.fromkeys(x for x in r[k] if x))
    return r


def main():
    datos = {}
    for car in CARPETAS:
        for md in sorted((FICHAS / car).glob("*.md")):
            datos[f"{car}/{md.stem}"] = extraer(md.read_text(encoding="utf-8"))
    import collections
    frec = collections.Counter(o["marca"].upper() for v in datos.values() for o in v["oem"] if len(o["marca"].split()) == 1)
    PALABRAS_MARCA.update({m for m, n in frec.items() if n >= 5 and m != "SAE"} | {"ACEA", "API", "ILSAC", "JASO", "MIL"})
    PATRONES = {
        "api": r"((?:S[A-Z]|C[A-Z]-?\d?|FA-4|GL-\d|PG-\d|MT-1)(?:\s+(?:Plus|PLUS|RC)\b|\s*\(LS\))*)",
        "acea": r"([A-E]\d{1,2}(?:-\d{2})?)",
        "ilsac": r"(GF-\d[A-Z]?)",
        "jaso": r"([A-Z]{2,3}\d?[A-Z]?)",
    }

    def tomar_tokens(valor, patron):
        """Toma del principio todos los codigos validos; lo que sobra (otras normas) se devuelve aparte."""
        s, out = valor.strip(), []
        while True:
            m = re.match(patron + r"(?:\s*[,;/]\s*|\s+|$)", s)
            if not m:
                break
            out.append(m.group(1))
            s = s[m.end():]
        return out, s.strip()

    def sin_repeticion(marca, valor):
        """El PDF repite a veces la etiqueta dentro del valor: 'C-3 ALLISON C-3' -> 'C-3'."""
        partes = re.split(r"\b" + re.escape(marca) + r"\b", valor)
        if len(partes) == 2 and partes[0].strip() and partes[0].strip() == partes[1].strip():
            return partes[0].strip()
        return valor

    for v in datos.values():
        resto_libre = []
        for campo, patron in PATRONES.items():
            limpios = []
            for x in v[campo]:
                toks, resto = tomar_tokens(x, patron)
                limpios += toks
                if resto:
                    resto_libre.append(resto)
            v[campo] = list(dict.fromkeys(limpios))
        for resto in resto_libre:  # p. ej. "PSA B71 2010": homologacion en texto libre, solo si empieza por una marca conocida
            if resto.split()[0].upper() in PALABRAS_MARCA - {"ACEA", "API", "ILSAC", "JASO"}:
                v["oem"].append({"marca": resto.split()[0], "valor": resto.split(None, 1)[1] if len(resto.split()) > 1 else "", "_de_texto": True})
            else:
                v["oem"].append({"marca": "TEXTO LIBRE", "valor": resto, "_ambiguo": True})
        ok, amb = [], []
        for o in v["oem"]:
            o["valor"] = sin_repeticion(o["marca"], o["valor"])
            (amb if es_ambiguo(o["marca"], o["valor"]) and not o.get("_de_texto") else ok).append(o)
        v["oem_ok"] = [x for o in ok for x in expandir(o["marca"], o["valor"])]
        v["oem_ambiguo"] = [f'{o["marca"]}: {o["valor"]}' for o in amb]
        v.pop("oem")
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    n = len(datos)
    cnt = lambda f: sum(1 for d in datos.values() if f(d))
    print(f"{n} fichas")
    print(f"  con título: {cnt(lambda d: d['titulo'])} · grado SAE: {cnt(lambda d: d['grado_sae'])} · formatos: {cnt(lambda d: d['formatos'])} · fecha: {cnt(lambda d: d['fecha'])}")
    print(f"  con ACEA: {cnt(lambda d: d['acea'])} · API: {cnt(lambda d: d['api'])} · ILSAC: {cnt(lambda d: d['ilsac'])} · OEM: {cnt(lambda d: d['oem_ok'])}")
    print(f"  sin ninguna especificación: {cnt(lambda d: not (d['acea'] or d['api'] or d['ilsac'] or d['jaso'] or d['oem_ok'] or d['oem_ambiguo'] or d['spec_texto']))}")
    print(f"  filas OEM ambiguas apartadas: {sum(len(d['oem_ambiguo']) for d in datos.values())} en {cnt(lambda d: d['oem_ambiguo'])} fichas")
    print(f"  con avisos: {cnt(lambda d: d['avisos'])}")


if __name__ == "__main__":
    main()
