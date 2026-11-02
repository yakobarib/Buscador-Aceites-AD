"""Genera 'Productos Castrol Septiembre 2026.xlsx' (SIN precios) a partir de la tarifa de Castrol de septiembre de 2026.

Uso:  python gen_castrol_sept.py
Entrada : la tarifa enviada por Castrol (ruta fija de abajo; contiene precios y condiciones: NO se copia nada de eso)
Salida  : BASE DE CONOCIMIENTO/PRODUCTOS Y REFERENCIAS/Productos Castrol Septiembre 2026.xlsx
          columnas: REF | PRODUCTO | LITROS | SEGMENTO | GAMA | FAMILIA   (misma forma que las demas listas de producto)
"""
import re
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent
ENTRADA = Path("C:/Users/RIB/Documents/DOCUMENTOS RIB/COMERCIAL/PRODUCTOS/ACEITES/TARIFAS/2026/CASTROL/09 SEPTIEMBRE/Tarifa Castrol  septiembre 2026 - Formato Castrol - ENVIADA.xlsx")
SALIDA = RAIZ / "BASE DE CONOCIMIENTO" / "PRODUCTOS Y REFERENCIAS" / "Productos Castrol Septiembre 2026.xlsx"


def main():
    ws = openpyxl.load_workbook(ENTRADA, data_only=True).worksheets[0]
    filas = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        ref, desc, vol, seg, gama, fam = (str(r[i]).strip() if r[i] is not None else "" for i in (2, 3, 4, 5, 6, 7))
        if not ref or not desc:
            continue
        nombre, _, resto = desc.partition(",")
        pack = resto.strip().split(" ")[0] if resto.strip() else ""
        producto = re.sub(r"\s+", " ", f"{nombre.strip()} {pack}").strip()
        try:
            litros = float(vol)
            litros = int(litros) if litros == int(litros) else litros
        except ValueError:
            litros = vol
        filas.append((ref, producto, litros, seg, gama, fam))
    wb = openpyxl.Workbook()
    w = wb.active
    w.title = "REFERENCIAS y DESCRIPCIONES"
    w.append(["CASTROL (tarifa septiembre 2026, sin precios)"])
    w.append(["REF", "PRODUCTO", "LITROS", "SEGMENTO", "GAMA", "FAMILIA"])
    for f in filas:
        w.append(list(f))
    wb.save(SALIDA)
    print(f"{len(filas)} productos -> {SALIDA.name}")


if __name__ == "__main__":
    main()
