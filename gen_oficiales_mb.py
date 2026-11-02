"""Descripciones OFICIALES de las hojas de Mercedes-Benz (MB 2xx/3xx) a partir de mb_operating_fluids.json (operatingfluids.mercedes-benz.com).

Uso:  python gen_oficiales_mb.py      (antes: descarga con la API; ver BASE DE CONOCIMIENTO/CATALOGOS/Mercedes/)
Salida: descripciones_oficiales_mb.json   {"MB 229.52": {description, segment, tipo, fuente, productos_aprobados, titulo_en}}

La descripcion es la TRADUCCION del titulo oficial de la hoja (no se deduce nada mas) + el numero de productos aprobados que lista la propia web.
build_bridge.py usa este fichero para dar de alta normas MB que el buscador no conocia y para sustituir descripciones provisionales.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ORIGEN = RAIZ / "BASE DE CONOCIMIENTO" / "CATALOGOS" / "Mercedes" / "mb_operating_fluids.json"
SALIDA = RAIZ / "descripciones_oficiales_mb.json"

TRAD = {
    "Special additives for lubricants (vehicles and engines)": "Aditivos especiales para lubricantes (vehículos y motores)",
    "Engine Oil - Specified engine oils in cars & vans (service) - overview": "Resumen de los aceites de motor prescritos en turismos y furgonetas (servicio)",
    "Engine Oil - Viscosity classes of engine oils (car engines)": "Clases de viscosidad de los aceites de motor de turismos",
    "Multigrade Service Engine Oils": "Aceites de motor multigrado de servicio",
    "Low SPAsh Multigrade Service Engine Oils": "Aceites de motor multigrado de servicio de bajas cenizas (Low SPAsh)",
    "Multigrade Service Engine Oils - Historical": "Aceites de motor multigrado de servicio (hoja histórica)",
    "General information on gear oils": "Información general sobre aceites de engranajes",
    "Specified gear oils (cars, cross-country vehichles, vans) - overview": "Resumen de los aceites de engranajes prescritos (turismos, todoterreno y furgonetas)",
    "Gear Oils (Hypoid Gear) - Historical": "Aceites de engranajes hipoides (hoja histórica)",
    "Gear Oils (Steering / Manual Transmission)": "Aceites de engranajes para dirección y caja de cambios manual",
    "Gear Oils (Manual Transmission)": "Aceites de engranajes para caja de cambios manual",
    "Gear Oils (Transfer Case)": "Aceites de engranajes para caja de transferencia",
    "Gear Oils (Hypoid Gear)": "Aceites de engranajes hipoides",
    "Gear Oils (Hypoid Gearboxes Mineral Oil)": "Aceites de engranajes hipoides (aceite mineral)",
    "Gear Oils (FE Gear Oils)": "Aceites de engranajes de ahorro de combustible (FE)",
    "Gear Oils (Gear)": "Aceites de engranajes para cajas de cambio",
    "Gear Oils (Transfer Box)": "Aceites de engranajes para caja de transferencia",
    "Gear Oils (Rear Axle Gear)": "Aceites de engranajes para eje trasero",
    "Gear Oils (Automatic Shift Gear)": "Aceites de engranajes para caja de cambios automatizada",
    "Gear Oils (DCT Gear)": "Aceites de engranajes para caja de doble embrague (DCT)",
    "Gear Oils (Front Axle)": "Aceites de engranajes para eje delantero",
    "Automatic Transmission Fluids (ATF, 4/5 -Speed Automatic)": "Fluidos ATF para cajas automáticas de 4 y 5 velocidades",
    "Automatic Transmission Fluids (ATF, 5-Speed Automatic)": "Fluidos ATF para cajas automáticas de 5 velocidades",
    "Automatic Transmission Fluids (ATF, ZF/ AG4 Automatic)": "Fluidos ATF para cajas automáticas ZF / AG4",
    "Automatic Transmission Fluids (ATF, Transfer Box)": "Fluidos ATF para caja de transferencia",
    "Automatic transmission fluids (ATF, Transfer box)": "Fluidos ATF para caja de transferencia",
    "Automatic Transmission Fluids (ATF, CVT)": "Fluidos ATF para transmisiones de variación continua (CVT)",
    "Automatic Transmission Fluids (ATF, Transfer/Automatic)": "Fluidos ATF para caja de transferencia y caja automática",
    "Automatic Transmission Fluids (ATF, Transfer / 9-Speed Automatic)": "Fluidos ATF para caja de transferencia y caja automática de 9 velocidades",
    "Automatic Transmission Fluids (ATF, -speed Automatic)": "Fluidos ATF para cajas automáticas",
    "Automatic Transmission Fluids (ATF, Type A Suffix A)": "Fluidos ATF Tipo A Suffix A",
    "Automatic Transmission Fluids (ATF, 7-Speed DCT)": "Fluidos ATF para cajas de doble embrague (DCT) de 7 velocidades",
    "Automatic transmission fluids (ATF, 8F DCT transmission)": "Fluidos ATF para cajas de doble embrague (DCT) 8F",
    "Gear oil for electric drive system front axle": "Aceite de engranajes para el eje delantero del sistema de accionamiento eléctrico",
    "Transmission Oil (Manual Transmission, E-Drive System)": "Aceite de transmisión para caja manual y sistema de accionamiento eléctrico",
    "Automatic Transmission Fluids (ATF, Hydraulic System)": "Fluidos ATF para sistema hidráulico",
    "Automatic Transmission Fluids (ATF, GL-5 Hydraulic System)": "Fluidos ATF GL-5 para sistema hidráulico",
    "Automatic transmission fluids (ATF, 8F-eDCT transmission)": "Fluidos ATF para cajas de doble embrague eléctricas (eDCT) 8F",
    "Automatic Transmission Fluids (ATF, Hybride)": "Fluidos ATF para transmisiones híbridas",
    "Automatic Transmission Fluids (ATF, Allison) - Historical": "Fluidos ATF Allison (hoja histórica)",
    "Automatic Transmission Fluids (ATF) - Historical": "Fluidos ATF (hoja histórica)",
    "Automatic Transmission Fluids (ATF, Steering/Automatic)": "Fluidos ATF para dirección y caja automática",
    "Automatic Transmission Fluids (ATF, Automatic)": "Fluidos ATF para cajas automáticas",
    "Automatic Transmission Fluids (ATF, ZF Gear)": "Fluidos ATF para cajas ZF",
    "Automatic Transmission Fluids (ATF, Allison/Automatic)": "Fluidos ATF para cajas Allison y automáticas",
    "Gears Oil (e-Drive)": "Aceite de engranajes para accionamiento eléctrico (e-Drive)",
    "Transmission Oils Electric Drive Modules": "Aceites de transmisión para módulos de accionamiento eléctrico",
    "Transmission oils for electric drive modules": "Aceites de transmisión para módulos de accionamiento eléctrico",
    "Automatic Transmission Fluids (ATF, 7-Speed DCT Getrag 700.422)": "Fluidos ATF para cajas de doble embrague (DCT) Getrag 700.422 de 7 velocidades",
    "Automatic Transmission Fluids (ATF, 7-Speed DCT Getrag 700.423)": "Fluidos ATF para cajas de doble embrague (DCT) Getrag 700.423 de 7 velocidades",
    "Gear Oils (Rear Axel)": "Aceites de engranajes para eje trasero",
    "Gear Oils (Front Axel)": "Aceites de engranajes para eje delantero",
    "Axle Oil Light Metal Rear Axle (China Localization)": "Aceite para eje trasero de metal ligero (localización China)",
    "Axle Oil Rear Axle": "Aceite para eje trasero",
    "General information and specification on coolants": "Información general y especificación de refrigerantes",
    "Specified anticorrosion protection-antifreeze (Cars, VAN) - Overview -": "Resumen de los anticongelantes y anticorrosivos prescritos (turismos y furgonetas)",
    "Anticorrosion/Antifreeze Agents": "Concentrados anticorrosión y anticongelante",
    "Premixed Anticorrosion/Antifreeze Agents": "Anticongelantes anticorrosión premezclados",
    "General information on Grease": "Información general sobre grasas",
    "Grease (NLGI Class 00/000, Liquid Grease)": "Grasa (NLGI 00/000, grasa líquida)",
    "Grease (NLGI class 2, High Temperature Antifriction Bearing Grease)": "Grasa (NLGI 2, para rodamientos antifricción de alta temperatura)",
    "Grease (NLGI Class 1, Lubricating Grease)": "Grasa lubricante (NLGI 1)",
    "Grease (NLGI class 2, Long-Life Grease)": "Grasa de larga duración (NLGI 2)",
    "Grease (NLGI Class 2, Multi Purpose Grease)": "Grasa multiusos (NLGI 2)",
    "Grease (NLGI Class 2, Wheel Bearing Grease)": "Grasa para rodamientos de rueda (NLGI 2)",
    "Grease (NLGI Class 2, Complex Grease)": "Grasa compleja (NLGI 2)",
    "Brake Pad Paste": "Pasta para pastillas de freno",
    "Lubricants for Electrical Equipment": "Lubricantes para equipos eléctricos",
    "Specified hydraulic fluids) - overview": "Resumen de los fluidos hidráulicos prescritos",
    "Hydraulic Fluids (Tipper)": "Fluidos hidráulicos (volquetes)",
    "Hydraulic Fluids": "Fluidos hidráulicos",
    "Brake Fluid": "Líquido de frenos",
    "General information on brake fluid": "Información general sobre el líquido de frenos",
    "Refrigerant": "Refrigerante del aire acondicionado",
}
TIPO = {"motor": "motor", "transmision": "transmision", "refrigerante": "refrigerante", "grasa": "grasa", "hidraulico": "hidraulico"}


def main():
    d = json.loads(ORIGEN.read_text(encoding="utf-8"))
    out, sin = {}, []
    for cat, v in d["categorias"].items():
        if cat not in TIPO:
            continue  # combustible, frenos y aire acondicionado no son aceites del buscador
        for h in v["hojas"]:
            t = re.sub(r"\s+", " ", h["titulo_en"]).strip()
            es = TRAD.get(t)
            if not es:
                sin.append((h["hoja"], t))
                continue
            n = len(h["productos"])
            hist = " (hoja histórica)" in es
            desc = f"{es} (hoja MB {h['hoja']} de Mercedes-Benz)"
            if n:
                desc += f"; la lista oficial de Mercedes-Benz recoge {n} productos aprobados"
            if "transferred to Daimler Truck" in h["info_en"]:
                desc += "; hoja transferida a Daimler Truck AG"
            out[f"MB {h['hoja'].rstrip('H')}" if hist else f"MB {h['hoja']}"] = dict(
                description=desc, segment=("pesado" if h["hoja"].startswith("228") or "Daimler Truck" in h["info_en"] else "ligero"), tipo=TIPO[cat], fuente="operatingfluids.mercedes-benz.com", productos_aprobados=n, titulo_en=t, publicada=h["publicada"])
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(len(out), "hojas MB con descripción oficial; sin traducir:", sin)


if __name__ == "__main__":
    main()
