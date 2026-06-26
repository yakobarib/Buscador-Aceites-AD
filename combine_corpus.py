import json

BASE = r"C:\Users\RIB\Documents\DOCUMENTOS RIB\DOCUMENTOS\CLAUDE\Proyectos\Buscador Aceites\BASE DE CONOCIMIENTO"

with open(BASE + r"\corpus_embeddings_adparts.json", encoding="utf-8") as f:
    adparts = json.load(f)
with open(BASE + r"\corpus_embeddings_febi_tcmatic.json", encoding="utf-8") as f:
    febi_tcm = json.load(f)
with open(BASE + r"\corpus_embeddings_marcas.json", encoding="utf-8") as f:
    marcas_extra = json.load(f)
with open(BASE + r"\corpus_embeddings_normativas.json", encoding="utf-8") as f:
    normativas = json.load(f)
with open(BASE + r"\corpus_embeddings_fichas.json", encoding="utf-8") as f:
    fichas = json.load(f)
with open(BASE + r"\corpus_embeddings_repsol_pesado.json", encoding="utf-8") as f:
    repsol_pesado = json.load(f)

# ── Trigger map for AD Parts by tipo/segmento ────────────────────────────────
def adparts_trigger(p):
    tipo = p.get("tipo","").lower()
    seg  = p.get("segmento","").lower()
    visc = p.get("viscosidad","")
    sku  = p.get("sku","")
    # Direct SKU trigger is most precise — freeSearch handles it
    if sku: return sku
    if tipo == "motor":
        base = "aceite camion" if seg in ("pesado","industrial") else "aceite motor"
        return f"{base} {visc}".strip()
    if tipo == "hidraulico":
        return f"HHM {visc}" if "HM" in visc else f"HHV {visc}" if "HV" in visc else "aceite hidráulico"
    if tipo in ("transmision","transmisión"):
        return f"caja cambios {visc}".strip()
    if tipo == "atf": return f"ATF {visc}".strip()
    if tipo == "agricola": return "aceite tractor"
    if tipo == "grasa": return "grasa"
    if tipo == "refrigerante": return "refrigerante"
    if tipo == "compresor": return "aceite compresor"
    return tipo

def adparts_text(p):
    parts = []
    nombre = p.get("nombre","")
    tipo   = p.get("tipo","")
    seg    = p.get("segmento","")
    visc   = p.get("viscosidad","")
    specs  = p.get("specs",[])
    oem    = p.get("oem",[])
    aplic  = p.get("aplicacion","")
    sku    = p.get("sku","")

    if nombre: parts.append(nombre)
    if tipo:   parts.append(tipo)
    if seg:    parts.append(seg)
    if visc:   parts.append(visc)
    if specs:  parts.append(" ".join(specs))
    if oem:    parts.append(" ".join(oem[:15]))  # cap at 15 OEMs
    if aplic:  parts.append(aplic[:300])
    if sku:    parts.append(sku)
    return " ".join(parts)

# Convert AD Parts to unified format
adparts_unified = []
for p in adparts:
    sku = p.get("sku","")
    entry = {
        "id": sku,
        "marca": "adparts",
        "triggerQuery": adparts_trigger(p),
        "text": adparts_text(p)
    }
    adparts_unified.append(entry)

# Combine: AD Parts PDF corpus, Febi/TC-Matic, brand catalogs
# Deduplicate brand catalog entries by ID (keep first occurrence)
seen_ids = set()
all_entries = adparts_unified + febi_tcm + marcas_extra + normativas + fichas + repsol_pesado
combined = []
for e in all_entries:
    if e["id"] not in seen_ids:
        seen_ids.add(e["id"])
        combined.append(e)

dupes_count = len(all_entries) - len(combined)

print(f"AD Parts PDF:   {len(adparts_unified)}")
print(f"Febi+TC-Matic:  {len(febi_tcm)}")
print(f"Marcas (Castrol/Shell/Repsol/Eni/AD): {len(marcas_extra)}")
print(f"Normativas:     {len(normativas)}")
print(f"Fichas técnicas:{len(fichas)}")
print(f"Repsol Motor Pesado+ATF+Trans:{len(repsol_pesado)}")
print(f"Duplicates removed: {dupes_count}")
print(f"Total:          {len(combined)}")
print("No duplicate IDs" if dupes_count == 0 else f"Removed {dupes_count} duplicates")

# Save combined
out = BASE + r"\corpus_embeddings_completo.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)
print(f"Saved: {out}")

# Distribution
from collections import Counter
marcas = Counter(e["marca"] for e in combined)
triggers = Counter(e["triggerQuery"] for e in combined)
print("\nPor marca:", dict(sorted(marcas.items())))
print("\nTop 25 triggers:")
for t, n in triggers.most_common(25):
    print(f"  {n:3d}x  {t}")
