# Informe de pruebas del buscador (2026-10-26)

Casos: 3085 · acierto global: **97.3 %** · tiempo: 12.3 s

Mide solo las búsquedas por reglas del buscador (la IA semántica del navegador no se ejecuta aquí). Un caso es acierto si la respuesta menciona alguna de las referencias esperadas.

| Herramienta | Categoría | Casos | Aciertos | % | "none" | Errores |
|---|---|---|---|---|---|
| búsqueda libre | ad_ref | 289 | 281 | 97.2 % | 218 | 0 |
| búsqueda libre | ref_competidor | 455 | 454 | 99.8 % | 448 | 0 |
| búsqueda libre | febi_ref | 253 | 249 | 98.4 % | 253 | 0 |
| búsqueda libre | oem_febi | 71 | 69 | 97.2 % | 0 | 0 |
| búsqueda libre | norma_ad | 258 | 242 | 93.8 % | 11 | 0 |
| homologaciones | norma_ad_hom | 258 | 246 | 95.3 % | 11 | 0 |
| búsqueda libre | visc_acea | 48 | 48 | 100.0 % | 0 | 0 |
| búsqueda libre | tcmatic_febi | 19 | 18 | 94.7 % | 19 | 0 |
| referencias cruzadas | xref_ad_a_otras | 172 | 172 | 100.0 % | 0 | 0 |
| referencias cruzadas | xref_otra_a_ad | 455 | 454 | 99.8 % | 0 | 0 |
| referencias cruzadas | xref_bloques | 487 | 454 | 93.2 % | 18 | 0 |
| referencias cruzadas | xref_febi_conocida | 253 | 249 | 98.4 % | 4 | 0 |
| referencias cruzadas | xref_tcm_a_febi | 19 | 18 | 94.7 % | 0 | 0 |
| referencias cruzadas | xref_febi_a_tcm | 12 | 11 | 91.7 % | 0 | 0 |
| búsqueda libre | ref_refrigerante | 36 | 36 | 100.0 % | 18 | 0 |

## Cambios respecto a la ejecución anterior

- Casos que mejoran: 0
- Casos que EMPEORAN: 0

## Fallos por categoría (hasta 15 por categoría)

### ad_ref — 8 fallos (none: 8)

- ad_ref-fc1f6739 «741050» → none
- ad_ref-b35ef1fe «741020» → none
- ad_ref-8209204c «821050» → none
- ad_ref-cd48b68b «821020» → none
- ad_ref-048fa388 «791050» → none
- ad_ref-f8c9732c «801050» → none
- ad_ref-c5a95a9c «811050» → none
- ad_ref-c17f4e89 «751050» → none

### ref_competidor — 1 fallos (none: 1)

- ref_competidor-d6923c36 «1612B5» → none

### febi_ref — 4 fallos (none: 4)

- febi_ref-af2baf04 «febi ADG05529» → none
- febi_ref-b8eb1677 «febi ADG05531» → none
- febi_ref-cfec26e1 «febi ADG05530» → none
- febi_ref-21e247cd «febi ADG05532» → none

### oem_febi — 2 fallos (redirect_formal: 2)

- oem_febi-2a306f3f «STJLR.03.5003» → redirect_formal
- oem_febi-091fb7e2 «G 052 171» → redirect_formal

### norma_ad — 16 fallos (none: 11, redirect_formal: 1, found: 4)

- norma_ad-721efaf0 «B712296-18» → none
- norma_ad-b9b6acc7 «93K218» → none
- norma_ad-50ca7158 «93K2115» → none
- norma_ad-d7c0640c «TO-2» → redirect_formal
- norma_ad-178e56db «ATF +3/+4» → found
- norma_ad-65272201 «ATF D II Multi» → found
- norma_ad-6383525f «ATF D III Multi» → found
- norma_ad-6fa7f8d7 «Suzuki ATF 3317» → found
- norma_ad-05ad28d4 «341 E-3» → none
- norma_ad-b839f1a4 «342 S1» → none
- norma_ad-ff93e787 «M1144» → none
- norma_ad-b057b916 «11158 HM» → none
- norma_ad-df74bab2 «ISO6743/4-HV» → none
- norma_ad-3a3270fa «11158 HV» → none
- norma_ad-7a8b1399 «48-691» → none

### norma_ad_hom — 12 fallos (none: 11, redirect_formal: 1)

- norma_ad_hom-bb31a290 «B712296-18» → none
- norma_ad_hom-e34e31b7 «93K218» → none
- norma_ad_hom-0095f8f9 «93K2115» → none
- norma_ad_hom-f752e016 «TO-2» → redirect_formal
- norma_ad_hom-55f2a175 «341 E-3» → none
- norma_ad_hom-e2c16cd4 «342 S1» → none
- norma_ad_hom-02d18c79 «M1144» → none
- norma_ad_hom-11d675e1 «11158 HM» → none
- norma_ad_hom-df39c1fc «ISO6743/4-HV» → none
- norma_ad_hom-9bb3bc0d «11158 HV» → none
- norma_ad_hom-20738ee9 «48-691» → none
- norma_ad_hom-be687ee2 «48-603 HV» → none

### tcmatic_febi — 1 fallos (none: 1)

- tcmatic_febi-d3e7b864 «109.000.0006» → none

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
