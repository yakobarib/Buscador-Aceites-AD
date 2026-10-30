"""Extrae por REGLAS (sin IA) las homologaciones de las tablas de gama de Castrol (turismo) ya convertidas a Markdown.

Uso:  python extract_homologaciones_castrol.py

Entrada : OBSIDIAN/Buscador Aceites/FUENTES_MD/HOMOLOGACIONES/Castrol/Castrol Homologaciones Gama {Edge,GTX,Magnatec}.md
Salida  : homologaciones_castrol_extraidas.json  (lo lee build_wiki.py)  + resumen por pantalla

Cada fila de la tabla es un producto; cada columna, una marca de vehiculo. De cada celda se separan:
  - 'formal'   : lo que figura sin calificativo (aprobacion / homologacion que Castrol declara)
  - 'cumple'   : lo que Castrol califica como «Meets», «Warranted by Castrol», «Recommended for use» o «SFU»
                 (cumple o recomienda, pero NO es una homologacion formal)
  - 'sin_enlazar': texto de la celda que no se reconoce como norma (no se descarta ni se inventa: se deja tal cual)
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CARPETA = RAIZ / "OBSIDIAN" / "Buscador Aceites" / "FUENTES_MD" / "HOMOLOGACIONES" / "Castrol"
ARCHIVOS = ["Castrol Homologaciones Gama Edge", "Castrol Homologaciones Gama GTX", "Castrol Homologaciones Gama Magnatec"]
SALIDA = RAIZ / "homologaciones_castrol_extraidas.json"
CALIF = re.compile(r"(Warranted by Castrol|Recommended for use|Meets|SFU|Cumple|Recomendado)\s*:?", re.I)


def clave(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper().replace("+", "PLUS"))


def normaliza_oem(marca, texto):
    """Devuelve (lista de literales con marca, texto restante que no se pudo enlazar)."""
    t = " " + texto.replace("\xa0", " ") + " "
    out = []

    def toma(patron, fabrica):
        nonlocal t
        for m in list(re.finditer(patron, t, re.I)):
            out.append(fabrica(m))
        t = re.sub(patron, " ", t, flags=re.I)

    if marca == "VAG":
        toma(r"VWC\s*(\d{5})", lambda m: f"VW C {m.group(1)}")
        toma(r"(?<!\d)(5\d{2})[ .](\d{2})(?!\d)", lambda m: f"VW {m.group(1)}.{m.group(2)}")
    elif marca == "MERCEDES":
        toma(r"(?<!\d)(2\d{2}\.\d{1,2})(?!\d)", lambda m: f"MB {m.group(1)}")
    elif marca == "BMW":
        toma(r"LL-\s?(\d{2})\s?(FE\+?)?", lambda m: f"BMW LL-{m.group(1)}" + (m.group(2).upper() if m.group(2) else ""))
    elif marca == "PORSCHE":
        toma(r"(?<![A-Z0-9])([AC]\d{2})(?![A-Z0-9])", lambda m: f"PORSCHE {m.group(1).upper()}")
    elif marca == "OPEL":
        toma(r"dexos1\s*Gen\s*(\d)", lambda m: f"GM DEXOS1 GEN{m.group(1)}")
        for m in re.finditer(r"OV\s?040\s?1547\s?-\s?([A-Z]\d{2})((?:\s?/\s?[A-Z]\d{2})*)", t, re.I):
            for x in [m.group(1)] + re.findall(r"[A-Z]\d{2}", m.group(2).upper()):
                out.append(f"OPEL OV 040 1547-{x.upper()}")
        t = re.sub(r"OV\s?040\s?1547\s?-\s?[A-Z]\d{2}(?:\s?/\s?[A-Z]\d{2})*", " ", t, flags=re.I)
    elif marca == "FORD":
        for m in re.finditer(r"WSS-?\s?M2C\s?(\d{3})-?\s?([A-Z]\d?)((?:\s?/\s?[A-Z]\d?(?![A-Z0-9]))*)", t, re.I):
            for x in [m.group(2)] + re.findall(r"[A-Z]\d?", m.group(3).upper()):
                out.append(f"FORD WSS-M2C{m.group(1)}-{x.upper()}")
        t = re.sub(r"WSS-?\s?M2C\s?\d{3}-?\s?[A-Z]\d?(?:\s?/\s?[A-Z]\d?(?![A-Z0-9]))*", " ", t, flags=re.I)
        toma(r"(?<![A-Z0-9-])M2C\s?(\d{3})-?\s?([A-Z]\d?)", lambda m: f"FORD WSS-M2C{m.group(1)}-{m.group(2).upper()}")
    elif marca == "RENAULT":
        toma(r"RN\s?(\d{4}|17\w*)", lambda m: f"RENAULT RN{m.group(1).upper()}")
    elif marca == "FIAT":
        toma(r"9\.55535-([A-Z0-9]+)", lambda m: f"FIAT 9.55535-{m.group(1).upper()}")
    elif marca in ("JAGUAR-LR", "JAGUAR"):
        toma(r"STJLR\.?\s?(\d{2})\.(\d{4})", lambda m: f"JLR STJLR.{m.group(1)}.{m.group(2)}")
    elif marca == "VOLVO":
        toma(r"VCC\s?([A-Z0-9\-]+)", lambda m: f"VOLVO VCC {m.group(1).upper()}")
        toma(r"(?<!\d)(9520\d{4})(?!\d)", lambda m: f"VOLVO {m.group(1)}")
    elif marca == "CHRYSLER":
        toma(r"MS[\s\-]?(\d{4,5})", lambda m: f"CHRYSLER MS-{m.group(1)}")
    elif marca in ("PSA PEUGEOT CITROËN", "PSA", "PSA PEUGEOT CITROEN"):
        toma(r"B71\s?(\d{4})", lambda m: f"PSA B71 {m.group(1)}")
        toma(r"STELLANTIS\s?FPW\s?9\.55535\s?/\s?(\d{2})", lambda m: f"STELLANTIS FPW9.55535/{m.group(1)}")
    resto = re.sub(r"(?i)\b(MB-?\s?Approval|MB|Approval|VW|Audi|Opel|Ford|Renault|Fiat|BMW|Porsche|Volvo|Chrysler)\b|[/;,*]|\s-\s|\s-$", " ", t)
    resto = re.sub(r"\s+", " ", resto).strip(" -")
    return out, resto


def partir_celda(texto):
    """Separa el texto en [(calificativo|None, fragmento)]."""
    texto = re.sub(r"(\w)-\s+(\w)", r"\1\2", texto)
    partes, ultimo, calif = [], 0, None
    for m in CALIF.finditer(texto):
        if m.start() > ultimo:
            partes.append((calif, texto[ultimo:m.start()]))
        calif, ultimo = m.group(1).lower(), m.end()
    partes.append((calif, texto[ultimo:]))
    return [(c, f.strip()) for c, f in partes if f.strip()]


def acea(texto):
    return [f"ACEA {x}" for x in re.findall(r"[ABCE]\d{1,2}(?:/[ABCE]\d{1,2})?", texto.upper().replace(",", " "))]


def api_ilsac(texto):
    api = [f"API {x}" for x in re.findall(r"\b(S[A-Z]|C[A-Z]\d?)\b", texto.upper().replace("/", " ")) if x not in ("GF",)]
    ils = [f"ILSAC {x}" for x in re.findall(r"GF-?\s?\d[AB]?", texto.upper())]
    return api, [i.replace("GF ", "GF-") if "GF-" not in i else i for i in ils]


def main():
    res, n_prod, avisos = {}, 0, []
    for nombre in ARCHIVOS:
        f = CARPETA / f"{nombre}.md"
        if not f.exists():
            avisos.append(f"falta {nombre}.md (ejecuta pdf_to_md.py)")
            continue
        filas = [l for l in f.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
        cab = None
        for l in filas:
            cel = [c.strip() for c in l.strip().strip("|").split("|")]
            if cab is None:
                if cel and cel[0].upper().startswith("PRODUCT"):
                    cab = [c.upper().split("(")[0].strip() for c in cel]
                continue
            if set("".join(cel)) <= set("-: "):
                continue
            if len(cel) != len(cab) or not cel[0]:
                avisos.append(f"{nombre}: fila con {len(cel)} celdas (cabecera {len(cab)}): {cel[0][:40]!r}")
                continue
            prod = re.sub(r"\s+", " ", cel[0]).strip()
            d = {"producto": prod, "archivo": f.name, "acea": [], "api": [], "ilsac": [], "formal": [], "cumple": [], "sin_enlazar": [], "celdas": {}}
            for col, txt in zip(cab[1:], cel[1:]):
                if not txt:
                    continue
                d["celdas"][col] = txt
                if col == "ACEA":
                    d["acea"] += acea(txt)
                elif col.startswith("API"):
                    a, i = api_ilsac(txt)
                    d["api"] += a
                    d["ilsac"] += i
                else:
                    marca = col.replace("(VW/AUDI/ SKODA/SEAT)", "").replace("(VW/ AUDI/SKODA/ SEAT)", "").strip()
                    marca = "VAG" if marca.startswith("VAG") else ("MERCEDES" if marca.startswith("MERCEDES") else marca)
                    for calif, frag in partir_celda(txt):
                        lits, resto = normaliza_oem(marca, frag)
                        (d["formal"] if calif is None else d["cumple"]).extend(lits)
                        if resto and not re.fullmatch(r"[\W\d]*", resto):
                            d["sin_enlazar"].append(f"{marca}: {resto}")
            for k in ("acea", "api", "ilsac", "formal", "cumple"):
                d[k] = list(dict.fromkeys(d[k]))
            res.setdefault(clave(prod), []).append(d)
            n_prod += 1
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"productos={n_prod} claves={len(res)}")
    print(f"con ACEA: {sum(1 for v in res.values() if v[0]['acea'])} · con API: {sum(1 for v in res.values() if v[0]['api'])} · con OEM formal: {sum(1 for v in res.values() if v[0]['formal'])} · con 'cumple': {sum(1 for v in res.values() if v[0]['cumple'])}")
    print(f"con texto sin enlazar: {sum(1 for v in res.values() if v[0]['sin_enlazar'])}")
    for a in avisos:
        print("AVISO:", a)


if __name__ == "__main__":
    main()
