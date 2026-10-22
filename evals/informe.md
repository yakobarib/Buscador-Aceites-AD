# Informe de pruebas del buscador (2026-10-22)

Casos: 2791 · acierto global: **94.6 %** · tiempo: 9.3 s

Mide solo las búsquedas por reglas del buscador (la IA semántica del navegador no se ejecuta aquí). Un caso es acierto si la respuesta menciona alguna de las referencias esperadas.

| Herramienta | Categoría | Casos | Aciertos | % | "none" | Errores |
|---|---|---|---|---|---|
| búsqueda libre | ad_ref | 289 | 268 | 92.7 % | 218 | 0 |
| búsqueda libre | ref_competidor | 455 | 454 | 99.8 % | 451 | 0 |
| búsqueda libre | febi_ref | 253 | 249 | 98.4 % | 253 | 0 |
| búsqueda libre | oem_febi | 71 | 69 | 97.2 % | 0 | 0 |
| búsqueda libre | norma_ad | 258 | 176 | 68.2 % | 55 | 0 |
| búsqueda libre | visc_acea | 48 | 48 | 100.0 % | 0 | 0 |
| búsqueda libre | tcmatic_febi | 19 | 18 | 94.7 % | 19 | 0 |
| referencias cruzadas | xref_ad_a_otras | 172 | 172 | 100.0 % | 0 | 0 |
| referencias cruzadas | xref_otra_a_ad | 455 | 454 | 99.8 % | 0 | 0 |
| referencias cruzadas | xref_bloques | 487 | 454 | 93.2 % | 18 | 0 |
| referencias cruzadas | xref_febi_conocida | 253 | 249 | 98.4 % | 4 | 0 |
| referencias cruzadas | xref_tcm_a_febi | 19 | 18 | 94.7 % | 0 | 0 |
| referencias cruzadas | xref_febi_a_tcm | 12 | 11 | 91.7 % | 0 | 0 |

## Cambios respecto a la ejecución anterior

- Casos que mejoran: 0
- Casos que EMPEORAN: 0

## Fallos por categoría (hasta 15 por categoría)

### ad_ref — 21 fallos (none: 21)

- ad_ref-0027 «18600» → none
- ad_ref-0028 «18208» → none
- ad_ref-0029 «18050» → none
- ad_ref-0030 «18020» → none
- ad_ref-0031 «18005» → none
- ad_ref-0087 «35600» → none
- ad_ref-0090 «35020» → none
- ad_ref-0103 «57600» → none
- ad_ref-0106 «57020» → none
- ad_ref-0136 «32600» → none
- ad_ref-0162 «28600» → none
- ad_ref-0194 «20600» → none
- ad_ref-0240 «39600» → none
- ad_ref-0252 «741050» → none
- ad_ref-0253 «741020» → none

### ref_competidor — 1 fallos (none: 1)

- ref_competidor-0434 «1612B5» → none

### febi_ref — 4 fallos (none: 4)

- febi_ref-0762 «febi ADG05529» → none
- febi_ref-0766 «febi ADG05531» → none
- febi_ref-0775 «febi ADG05530» → none
- febi_ref-0780 «febi ADG05532» → none

### oem_febi — 2 fallos (redirect_formal: 2)

- oem_febi-1035 «STJLR.03.5003» → redirect_formal
- oem_febi-1045 «G 052 171» → redirect_formal

### norma_ad — 82 fallos (redirect_formal: 17, none: 55, needs_clarification: 5, found: 4, direct_product: 1)

- norma_ad-1070 «ILSAC GF-5» → redirect_formal
- norma_ad-1073 «ACEA B1» → none
- norma_ad-1084 «DEXOS D» → none
- norma_ad-1098 «JLR STJLR.03.5007» → none
- norma_ad-1100 «ACEA B5» → none
- norma_ad-1104 «JLR STJLR.03.5004» → none
- norma_ad-1106 «JLR STJLR.03.5005» → none
- norma_ad-1115 «Stellantis FPW9.55535» → redirect_formal
- norma_ad-1116 «Stellantis FPW03» → none
- norma_ad-1117 «ACEA A3» → redirect_formal
- norma_ad-1118 «ACEA B4» → none
- norma_ad-1126 «Ford WSS-M2C-913-C/D» → redirect_formal
- norma_ad-1128 «JLR STJLR 03.5003» → none
- norma_ad-1145 «Renault 0700» → needs_clarification
- norma_ad-1146 «Renault 0710» → needs_clarification

### tcmatic_febi — 1 fallos (none: 1)

- tcmatic_febi-1377 «109.000.0006» → none

### xref_otra_a_ad — 1 fallos (cruce: 1)

- xref_otra_a_ad-1591 «1612B5» → cruce

### xref_bloques — 33 fallos (none: 18, cruce: 15)

- xref_bloques-2022 «6029984» → none
- xref_bloques-2026 «6029944» → none
- xref_bloques-2029 «6029958» → none
- xref_bloques-2047 «6082827» → none
- xref_bloques-2051 «6082846» → none
- xref_bloques-2054 «6082857» → none
- xref_bloques-2058 «6082890» → none
- xref_bloques-2064 «6016226» → none
- xref_bloques-2068 «6016246» → none
- xref_bloques-2072 «6016257» → none
- xref_bloques-2076 «6016294» → none
- xref_bloques-2080 «6030026» → none
- xref_bloques-2085 «6030058» → none
- xref_bloques-2088 «9092127» → none
- xref_bloques-2090 «RPP8056EJC» → cruce

### xref_febi_conocida — 4 fallos (none: 4)

- xref_febi_conocida-2525 «ADG05529» → none
- xref_febi_conocida-2529 «ADG05531» → none
- xref_febi_conocida-2538 «ADG05530» → none
- xref_febi_conocida-2543 «ADG05532» → none

### xref_tcm_a_febi — 1 fallos (sin_cruce: 1)

- xref_tcm_a_febi-2764 «109.000.0006» → sin_cruce

### xref_febi_a_tcm — 1 fallos (sin_cruce: 1)

- xref_febi_a_tcm-2765 «29934» → sin_cruce
