# Informe de pruebas del buscador (2026-10-22)

Casos: 3049 · acierto global: **61.7 %** · tiempo: 11.3 s

Mide solo las búsquedas por reglas del buscador (la IA semántica del navegador no se ejecuta aquí). Un caso es acierto si la respuesta menciona alguna de las referencias esperadas.

| Herramienta | Categoría | Casos | Aciertos | % | "none" | Errores |
|---|---|---|---|---|---|
| búsqueda libre | ad_ref | 289 | 56 | 19.4 % | 218 | 0 |
| búsqueda libre | ref_competidor | 455 | 0 | 0.0 % | 451 | 0 |
| búsqueda libre | febi_ref | 253 | 0 | 0.0 % | 253 | 0 |
| búsqueda libre | oem_febi | 71 | 69 | 97.2 % | 0 | 0 |
| búsqueda libre | norma_ad | 258 | 176 | 68.2 % | 55 | 0 |
| homologaciones | norma_ad_hom | 258 | 174 | 67.4 % | 55 | 0 |
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

- ad_ref-a59442e1 «61001» → none
- ad_ref-dfcc2e2b «61208» → none
- ad_ref-faa771f7 «67208» → none
- ad_ref-9fa44811 «78208» → none
- ad_ref-27182f74 «79208» → none
- ad_ref-48a5cf10 «73208» → none
- ad_ref-49881c0c «711000» → none
- ad_ref-e2ac079b «71208» → none
- ad_ref-a2c461a1 «68208» → direct_product
- ad_ref-a8d90d7a «331000» → none
- ad_ref-b4f7493e «33600» → none
- ad_ref-bd2569d0 «33208» → none
- ad_ref-cd0dc1c9 «33050» → none
- ad_ref-824c570e «33020» → none
- ad_ref-c77d051a «33001» → none

### ref_competidor — 455 fallos (none: 451, needs_clarification: 4)

- ref_competidor-22bfc704 «15F249» → none
- ref_competidor-cf6ed807 «RPP0100DBA» → none
- ref_competidor-8b7dbf0e «104410» → none
- ref_competidor-93d7c899 «15F872» → none
- ref_competidor-2b107df8 «RPP0100DGB» → none
- ref_competidor-a70a9bb4 «550056348» → none
- ref_competidor-c3b655fd «104483» → none
- ref_competidor-3581308d «RPP0100DHA» → none
- ref_competidor-40b2b6b3 «550056346» → none
- ref_competidor-2db834d1 «104481» → none
- ref_competidor-a70a51a0 «103623» → none
- ref_competidor-2a0920fb «15CC97» → none
- ref_competidor-c186234d «RPP0008DBA» → none
- ref_competidor-152e53d9 «103610» → none
- ref_competidor-7aaf8bb1 «15F6EB» → none

### febi_ref — 253 fallos (none: 253)

- febi_ref-ab75773d «febi 171331» → none
- febi_ref-ac18b324 «febi 171335» → none
- febi_ref-2136f01c «febi 46329» → none
- febi_ref-3511e29e «febi 171336» → none
- febi_ref-4216d208 «febi 171337» → none
- febi_ref-d2a9cf99 «febi 171338» → none
- febi_ref-4a52d84e «febi 08971» → none
- febi_ref-78aeb34d «febi 30017» → none
- febi_ref-3b64524b «febi 194478» → none
- febi_ref-2aca1eec «febi 14738» → none
- febi_ref-9f00bce1 «febi 29738» → none
- febi_ref-dbb1bb55 «febi 194472» → none
- febi_ref-8fc80219 «febi 22806» → none
- febi_ref-e811aedc «febi 30018» → none
- febi_ref-abdb4fda «febi 194477» → none

### oem_febi — 2 fallos (redirect_formal: 2)

- oem_febi-2a306f3f «STJLR.03.5003» → redirect_formal
- oem_febi-091fb7e2 «G 052 171» → redirect_formal

### norma_ad — 82 fallos (redirect_formal: 17, none: 55, needs_clarification: 5, found: 4, direct_product: 1)

- norma_ad-3ee6edb1 «ILSAC GF-5» → redirect_formal
- norma_ad-a1e9c39b «ACEA B1» → none
- norma_ad-ea933334 «DEXOS D» → none
- norma_ad-3bec3e46 «JLR STJLR.03.5007» → none
- norma_ad-a6840782 «ACEA B5» → none
- norma_ad-a2e56ffc «JLR STJLR.03.5004» → none
- norma_ad-d5e25f6a «JLR STJLR.03.5005» → none
- norma_ad-531d7889 «Stellantis FPW9.55535» → redirect_formal
- norma_ad-f766eefd «Stellantis FPW03» → none
- norma_ad-64caf174 «ACEA A3» → redirect_formal
- norma_ad-d1833714 «ACEA B4» → none
- norma_ad-09b972b4 «Ford WSS-M2C-913-C/D» → redirect_formal
- norma_ad-290be86d «JLR STJLR 03.5003» → none
- norma_ad-85cdf704 «Renault 0700» → needs_clarification
- norma_ad-9cd6c645 «Renault 0710» → needs_clarification

### norma_ad_hom — 84 fallos (redirect_formal: 17, none: 55, needs_clarification: 5, found: 6, direct_product: 1)

- norma_ad_hom-f7c9b5d1 «ILSAC GF-5» → redirect_formal
- norma_ad_hom-f1b64a3a «ACEA B1» → none
- norma_ad_hom-baccba95 «DEXOS D» → none
- norma_ad_hom-1853e160 «JLR STJLR.03.5007» → none
- norma_ad_hom-f6db8e23 «ACEA B5» → none
- norma_ad_hom-815ab0da «JLR STJLR.03.5004» → none
- norma_ad_hom-f65d804c «JLR STJLR.03.5005» → none
- norma_ad_hom-91ab3963 «Stellantis FPW9.55535» → redirect_formal
- norma_ad_hom-91de770a «Stellantis FPW03» → none
- norma_ad_hom-349578d5 «ACEA A3» → redirect_formal
- norma_ad_hom-81dcbeb5 «ACEA B4» → none
- norma_ad_hom-68073f08 «Ford WSS-M2C-913-C/D» → redirect_formal
- norma_ad_hom-0ab4374b «JLR STJLR 03.5003» → none
- norma_ad_hom-85808c4a «Renault 0700» → needs_clarification
- norma_ad_hom-9c9bbd0b «Renault 0710» → needs_clarification

### tcmatic_febi — 19 fallos (none: 19)

- tcmatic_febi-ba967daa «109.000.0013» → none
- tcmatic_febi-5a4394b4 «109.000.0019» → none
- tcmatic_febi-d3e7b864 «109.000.0006» → none
- tcmatic_febi-a4e088f2 «109.000.0007» → none
- tcmatic_febi-3de9d948 «109.000.0004» → none
- tcmatic_febi-4358a5f5 «109.000.0009» → none
- tcmatic_febi-e6bc1eff «109.000.0022» → none
- tcmatic_febi-08b27fd3 «109.000.0020» → none
- tcmatic_febi-66ae7e04 «109.000.0031» → none
- tcmatic_febi-4d832dc7 «109.000.0001» → none
- tcmatic_febi-239f2c10 «109.000.0010» → none
- tcmatic_febi-cd914d3c «109.000.0012» → none
- tcmatic_febi-345f9563 «109.000.0008» → none
- tcmatic_febi-d48a7c7d «109.000.0002» → none
- tcmatic_febi-2d44a422 «109.000.0018» → none

### xref_otra_a_ad — 1 fallos (cruce: 1)

- xref_otra_a_ad-276b6b5b «1612B5» → cruce

### xref_bloques — 33 fallos (none: 18, cruce: 15)

- xref_bloques-59306771 «6029984» → none
- xref_bloques-f585287d «6029944» → none
- xref_bloques-e5285517 «6029958» → none
- xref_bloques-a6a52bd6 «6082827» → none
- xref_bloques-87f8bcc6 «6082846» → none
- xref_bloques-e9e4bd11 «6082857» → none
- xref_bloques-db3567be «6082890» → none
- xref_bloques-5e476bb0 «6016226» → none
- xref_bloques-081dcc36 «6016246» → none
- xref_bloques-6601cde1 «6016257» → none
- xref_bloques-53bdd357 «6016294» → none
- xref_bloques-0268b362 «6030026» → none
- xref_bloques-aa9108a2 «6030058» → none
- xref_bloques-625c4900 «9092127» → none
- xref_bloques-52389bef «RPP8056EJC» → cruce

### xref_febi_conocida — 4 fallos (none: 4)

- xref_febi_conocida-6722516b «ADG05529» → none
- xref_febi_conocida-70e2e818 «ADG05531» → none
- xref_febi_conocida-07e5d88e «ADG05530» → none
- xref_febi_conocida-e9ebb9a2 «ADG05532» → none

### xref_tcm_a_febi — 1 fallos (sin_cruce: 1)

- xref_tcm_a_febi-a2d6f7f1 «109.000.0006» → sin_cruce

### xref_febi_a_tcm — 1 fallos (sin_cruce: 1)

- xref_febi_a_tcm-ec837fdc «29934» → sin_cruce
