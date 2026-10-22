# Informe de pruebas del buscador (2026-10-22)

Casos: 2791 · acierto global: **61.2 %** · tiempo: 8.2 s

Mide solo las búsquedas por reglas del buscador (la IA semántica del navegador no se ejecuta aquí). Un caso es acierto si la respuesta menciona alguna de las referencias esperadas.

| Herramienta | Categoría | Casos | Aciertos | % | "none" | Errores |
|---|---|---|---|---|---|
| búsqueda libre | ad_ref | 289 | 56 | 19.4 % | 218 | 0 |
| búsqueda libre | ref_competidor | 455 | 0 | 0.0 % | 451 | 0 |
| búsqueda libre | febi_ref | 253 | 0 | 0.0 % | 253 | 0 |
| búsqueda libre | oem_febi | 71 | 69 | 97.2 % | 0 | 0 |
| búsqueda libre | norma_ad | 258 | 176 | 68.2 % | 55 | 0 |
| búsqueda libre | visc_acea | 48 | 48 | 100.0 % | 0 | 0 |
| búsqueda libre | tcmatic_febi | 19 | 0 | 0.0 % | 19 | 0 |
| referencias cruzadas | xref_ad_a_otras | 172 | 172 | 100.0 % | 0 | 0 |
| referencias cruzadas | xref_otra_a_ad | 455 | 454 | 99.8 % | 0 | 0 |
| referencias cruzadas | xref_bloques | 487 | 454 | 93.2 % | 18 | 0 |
| referencias cruzadas | xref_febi_conocida | 253 | 249 | 98.4 % | 4 | 0 |
| referencias cruzadas | xref_tcm_a_febi | 19 | 18 | 94.7 % | 0 | 0 |
| referencias cruzadas | xref_febi_a_tcm | 12 | 11 | 91.7 % | 0 | 0 |

## Fallos por categoría (hasta 15 por categoría)

### ad_ref — 233 fallos (none: 218, direct_product: 15)

- ad_ref-0001 «61001» → none
- ad_ref-0003 «61208» → none
- ad_ref-0005 «67208» → none
- ad_ref-0007 «78208» → none
- ad_ref-0009 «79208» → none
- ad_ref-0010 «73208» → none
- ad_ref-0012 «711000» → none
- ad_ref-0013 «71208» → none
- ad_ref-0016 «68208» → direct_product
- ad_ref-0017 «331000» → none
- ad_ref-0018 «33600» → none
- ad_ref-0019 «33208» → none
- ad_ref-0020 «33050» → none
- ad_ref-0021 «33020» → none
- ad_ref-0023 «33001» → none

### ref_competidor — 455 fallos (none: 451, needs_clarification: 4)

- ref_competidor-0290 «15F249» → none
- ref_competidor-0291 «RPP0100DBA» → none
- ref_competidor-0292 «104410» → none
- ref_competidor-0293 «15F872» → none
- ref_competidor-0294 «RPP0100DGB» → none
- ref_competidor-0295 «550056348» → none
- ref_competidor-0296 «104483» → none
- ref_competidor-0297 «RPP0100DHA» → none
- ref_competidor-0298 «550056346» → none
- ref_competidor-0299 «104481» → none
- ref_competidor-0300 «103623» → none
- ref_competidor-0301 «15CC97» → none
- ref_competidor-0302 «RPP0008DBA» → none
- ref_competidor-0303 «103610» → none
- ref_competidor-0304 «15F6EB» → none

### febi_ref — 253 fallos (none: 253)

- febi_ref-0745 «febi 171331» → none
- febi_ref-0746 «febi 171335» → none
- febi_ref-0747 «febi 46329» → none
- febi_ref-0748 «febi 171336» → none
- febi_ref-0749 «febi 171337» → none
- febi_ref-0750 «febi 171338» → none
- febi_ref-0751 «febi 08971» → none
- febi_ref-0752 «febi 30017» → none
- febi_ref-0753 «febi 194478» → none
- febi_ref-0754 «febi 14738» → none
- febi_ref-0755 «febi 29738» → none
- febi_ref-0756 «febi 194472» → none
- febi_ref-0757 «febi 22806» → none
- febi_ref-0758 «febi 30018» → none
- febi_ref-0759 «febi 194477» → none

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

### tcmatic_febi — 19 fallos (none: 19)

- tcmatic_febi-1375 «109.000.0013» → none
- tcmatic_febi-1376 «109.000.0019» → none
- tcmatic_febi-1377 «109.000.0006» → none
- tcmatic_febi-1378 «109.000.0007» → none
- tcmatic_febi-1379 «109.000.0004» → none
- tcmatic_febi-1380 «109.000.0009» → none
- tcmatic_febi-1381 «109.000.0022» → none
- tcmatic_febi-1382 «109.000.0020» → none
- tcmatic_febi-1383 «109.000.0031» → none
- tcmatic_febi-1384 «109.000.0001» → none
- tcmatic_febi-1385 «109.000.0010» → none
- tcmatic_febi-1386 «109.000.0012» → none
- tcmatic_febi-1387 «109.000.0008» → none
- tcmatic_febi-1388 «109.000.0002» → none
- tcmatic_febi-1389 «109.000.0018» → none

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
