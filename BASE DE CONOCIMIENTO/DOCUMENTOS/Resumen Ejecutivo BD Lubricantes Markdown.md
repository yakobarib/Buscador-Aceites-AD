# Resumen Ejecutivo

Se propone una **base de conocimientos** que integre datos oficiales sobre lubricantes de motor y transmisión para vehículos ligeros y pesados, enfocándose en las marcas **AD Parts, Repsol, Castrol, Eni (Enilive) y Shell**, pero sin limitarse a ellas. El objetivo es indexar especificaciones técnicas, homologaciones y equivalencias de productos para que un GPT personalizado pueda responder consultas de forma precisa. Se recopilarán fuentes oficiales (fabricantes de vehículos, asociaciones y fichas técnicas de marcas) y se generarán tablas normalizadas (CSV/JSON) de homologaciones, especificaciones OEM, equivalencias de referencias y catálogos. También se crearán tablas comparativas (API, ACEA, SAE, ILSAC, JASO, ATF, etc.) con ejemplos de equivalencias de viscosidad. El paquete final incluirá resúmenes ejecutivos temáticos, ejemplos de prompts y respuestas esperadas, esquema de ingestión con metadatos, recomendaciones para gestionar la granularidad y notas legales. A continuación se detalla cada componente:

## 1\. Homologaciones y especificaciones OEM

Las **homologaciones** son certificaciones otorgadas por fabricantes de vehículos que avalan la calidad de un lubricante y su compatibilidad con los requisitos técnicos del vehículo. Según Repsol, “las homologaciones son certificaciones emitidas por los fabricantes que avalan la calidad y eficacia de los lubricantes”【10†L399-L404】, garantizando que el producto no dañará componentes clave (motor, transmisiones, etc.) y prolongará la vida útil del vehículo. El proceso de homologación implica ensayos de laboratorio y campo; por ejemplo, Repsol indica que cada nuevo producto pasa por ensayos exhaustivos antes de obtener la certificación【10†L415-L424】. Cada fabricante (OEM) tiene requisitos específicos: pueden emitirse homologaciones globales o por país/planta【10†L431-L439】.

Los datos de homologaciones se obtendrán de fuentes primarias:

* **Sitios web oficiales de fabricantes OEM** (p.ej. Toyota, VW, Mercedes, etc.) que publican listas de lubricantes aprobados por modelo/motor.
* **Manuales de servicio de vehículos** (contienen especificaciones de aceite).
* **Etiquetas y fichas técnicas oficiales** de productos (recolectables en portales como el de Repsol Lubricantes【10†L452-L460】).  
Por ejemplo, AD Parts destaca que sus lubricantes cuentan “con más de 400 referencias avaladas por homologaciones certificadas por \[los fabricantes]”【1†L18-L22】, y Castrol enfatiza la importancia del manual de vehículo o buscadores oficiales para elegir aceite【13†L111-L113】.

【54†embed\_image】Un técnico inspecciona la parte inferior de un vehículo durante el mantenimiento del sistema de lubricación. Las homologaciones son certificaciones emitidas por fabricantes que avalan la calidad y eficacia del lubricante【10†L399-L404】, garantizando la compatibilidad con los requisitos técnicos de cada marca automotriz. En la práctica, el GPT podrá extraer estas homologaciones (ej. “cumple con VW 504.00/507.00” o “aprobado MB 229.5”) de fichas técnicas o bases de datos de fabricantes.

## 2\. Fichas técnicas y catálogos de productos

Se recopilarán **datos de producto** para las marcas prioridad (AD Parts, Repsol, Castrol, Eni, Shell) incluyendo sus catálogos de aceites de motor y transmisión. Esto incluye:

* **Líneas de producto** (por ejemplo, Repsol *Leader*, *Elite*, Castrol *Edge*, *Vecton*, Eni *i-Sint*, *i-Sigma*, Shell *Helix*, *Spirax*, AD Parts genéricos, etc.).
* **Especificaciones técnicas**: viscosidad SAE, normas API/ACEA/ILSAC/JASO cumplidas, niveles OEM, composición (mineral/sintético), aplicaciones (gasolina, diésel, turbodiesel, transmisiones automáticas/manuales).
* **Características de rendimiento** y **beneficios** resumidos (p.ej. ahorro de combustible, limpieza de motor).

Por ejemplo, la ficha técnica de **Repsol Leader C2 C3 5W-30** indica “niveles de calidad, homologaciones y recomendaciones: ACEA C2/C3, API SN/CF”【29†L35-L42】. La de **Repsol Leader Inyección 15W-40** muestra homologaciones “API SL/CF, ACEA A3/B4, MB 229.1”【30†L29-L32】. La ficha de **Castrol EDGE 5W-40 A3/B4** lista “ACEA A3/B3, A3/B4; API SN/CF; BMW LL-01; MB 226.5/229.5; Porsche A40; Renault RN0700/RN0710; VW 502.00/505.00”【32†L57-L64】. Estos datos servirán para normalizar en tablas (p.ej. JSON con campos: *marca, producto, SAE, API, ACEA, OEMs*, etc.).

La normalización de datos implicará:

* Conversión de PDF y HTML oficiales a formatos estructurados (CSV/JSON).
* Unificación de nomenclaturas (p. ej. `VW 504.00/507.00` y `VW 504.00 / 507.00` se considerarán idénticas).
* Eliminación de duplicados (varias fichas con la misma especificación).  
Cada archivo normalizado (homologaciones, especificaciones OEM, equivalencias de referencias, catálogos de marcas) incluirá metadatos (p.ej. identificador único, fuente, fecha, marca, tipo de vehículo).

## 3\. Tablas comparativas de especificaciones y equivalencias

Se construirán **tablas comparativas** que aclaren las relaciones entre diferentes estándares y especificaciones. Ejemplos de contenido:

* **Tabla de especificaciones API vs ACEA vs OEM**: resumen de qué niveles API (SN, CK-4, etc.) cubren qué categorías ACEA (A3/B4, C3, etc.) y qué homologaciones OEM (Mercedes, VW, BMW). Por ejemplo, en la tabla siguiente se comparan niveles típicos:

|Visocidad SAE|API (gasolina/diésel)|ACEA (vehículos ligeros)|Ejemplos de aprobaciones OEM|
|-|-|-|-|
|5W-20|SN, SP (ILSAC GF-6A)|A1/B1, A5/B5|VW 504.00/507.00 (sintético Low SAPS)|
|5W-30|SN, SP (ILSAC GF-6A)|A3/B4, C3|BMW LL-01; MB 229.3/229.5|
|10W-40|SN, SN Plus|A3/B4|MAN 3477; VW 502.00 (diésel con DPF)|
|15W-40 (truck)|CK-4, CJ-4 (Euro VI/C)|E6/E9 (diesel pesados)|MAN 3477; Volvo VDS-4; MTU Clase 3|
|ATF (transm.)|-- (no API)|JASO 1A / ILSAC GF-6|Allison TES-389; MB 236.14; Toyota WS|

*(Ejemplo ilustrativo basado en fuentes de fabricantes y normas)*

* **Equivalencias de viscosidad**: tabla que muestre, por viscosidad SAE, los niveles API/ACEA más comunes (e.g. SAE 5W-30 suele cumplir API SN y ACEA A3/B4【32†L57-L64】【30†L29-L32】).
* **Equivalencias de referencias cruzadas**: permitirán al GPT buscar un lubricante equivalente en otra marca. Por ejemplo, una tabla con *Referencias AD Parts – Referencias Repsol – Referencias Castrol* para productos similares, indicando viscosidad y normativas compartidas. (Estas equivalencias pueden obtenerse comparando fichas técnicas o bases de datos de distribuidores autorizados).

Además, se generarán **diagramas de flujo** Mermaid para la ingestión de datos y **diagrama entidad-relación** para el esquema de metadatos (ver sección 7).

## 4\. Fuentes oficiales priorizadas

Se listan y ordenan las fuentes según su autoridad y relevancia:

* **Asociaciones y estándares globales**:

  * **API (American Petroleum Institute)** – sitio oficial de normas de aceite (API SN/SP/CF para gasolina y diésel)【36†L79-L81】.
  * **ACEA (Association des Constructeurs Européens d’Automobiles)** – normas europeas (categorías A/B/C/E)【34†L71-L74】.
  * **ILSAC** (normas para motores de gasolina USA-Japón, e.g. GF-6A/GF-6B).
  * **JASO** – normas japonesas, especialmente para motos (MA, MB)【39†L103-L110】.
  * **SAE** – viscosidad (J300 para motor, J306 para engranajes); tablas oficiales como referencia【48†L175-L184】【48†L203-L210】.
* **Fabricantes OEM de vehículos**: buscar listas de lubricantes aprobados en sitios como Mercedes-Benz, BMW, Volkswagen, PSA, Toyota, etc. Estas fuentes suelen detallar qué aceite (API/ACEA) cumple cada especificación del motor. (Por ejemplo, Mercedes publica tablas MB 229.3, 229.5, 229.51, 226.5, etc. Volkswagen publica 504.00, 507.00, 503.01, etc.)
* **Marcas de lubricantes** (fichas técnicas y portales):

  * **Repsol Lubricantes** – portal de fichas de producto y blog técnico【10†L452-L460】【29†L35-L42】.
  * **Castrol** – buscador de productos y fichas (ejemplo: *Castrol EDGE 5W-40*【32†L57-L64】, webs locales).
  * **Eni (Agip)** – sitio *oilproducts.eni.com* con fichas de *Eni i-Sint*, *i-Sigma*, *Agip Novecento*, etc.【27†L331-L339】【27†L348-L350】.
  * **Shell Lubricants** – catálogos (Shell Helix, Rimula, Spirax) y documentos (p.ej. Shell Spirax para transmisiones)【18†L193-L202】.
  * **AD Parts** – catálogo corporativo y datos de homologaciones genéricos【1†L18-L22】.
  * Otras marcas relevantes (valores de confiabilidad): **Motul, TotalEnergies/Elf, Mobil, Valvoline, Kixx, Liqui Moly**. Incluir sus manuales o portales si están disponibles en español o inglés.
* **Otros recursos técnicos**:

  * Blogs y artículos de expertos (p.ej. TotalEnergies sobre ACEA)【34†L71-L74】.
  * Manuales ISO y SAE (SAE J300, J306).
  * Publicaciones de laboratorios independientes que comparan productos (con precaución por copyright).

Cada fuente se citará en el PDF final para referencia. Se priorizarán contenidos en español; si no existen, se traducirán/conversiones pertinentes.

## 5\. Recomendaciones para evitar sobrecarga de la base

Para mantener la base manejable y útil, se sugieren criterios de inclusión y limpieza:

* **Relevancia y granularidad**: Incluir solo especificaciones oficiales y datos técnicos clave (viscosidades, normas, aprobaciones). Evitar duplicar datos semánticamente idénticos o muy detallados (no almacenar párrafos explicativos completos de fichas, sino los valores y códigos relevantes).
* **Criterios de inclusión**: Priorizar información oficial y de fabricantes de primera línea. Por ejemplo, no indexar post de redes sociales o foros no verificados. Cada entrada debe indicar fuente y fecha.
* **Metadatos bien definidos**: Cada elemento (lubricante, homologación, especificación) tendrá metadatos consistentes: p.ej. `{id, marca, familia, nombre, SAE, API, ACEA, JASO, ILSAC, OEMs, uso (gasolina/diésel/caja cambios), docFuente}`. Esto facilita búsquedas avanzadas (“filtra por ACEA C3” o “aceite 15W-40 aprobado VW”).
* **Normalización y control de calidad**: Unificar nomenclaturas (p.ej. “5W30” vs “5W-30”), verificar coherencia (un mismo lubricante no debe tener dos viscosidades distintas), y validación cruzada entre fuentes.
* **Deduplicación**: Si dos fuentes proporcionan la misma homologación o especificación (p.ej. dos distribuidoras listan el mismo aceite), se conservará una sola entrada normalizada.
* **Limitación de actualizaciones**: Si la base crece muy rápido, establecer reglas de caducidad o de prioridad para nueva información (p.ej. actualizar homologaciones solo cuando el fabricante las renueve).
* **Metadatos de versiones**: Mantener historial de cambios de especificaciones (p.ej. las versiones nuevas de ACEA o API) para consultas históricas.
* **Balance de idiomas**: Incluir idioma original de la fuente (p.ej. marcas internacionales usan inglés) en metadatos, pero traducir resúmenes al español en la interfaz del GPT.

## 6\. Ejemplos de prompts y respuestas esperadas

1. **Prompt:** *“¿Qué aceite de motor 5W-30 recomiendan para un VW Golf 1.6 TDI (2019) con filtro de partículas?”*  
**Respuesta esperada:** *Debe cumplir **ACEA C3** y <b>VW 507.00</b>, por lo que se recomienda un aceite sintético 5W-30 con esas especificaciones. Por ejemplo, el Repsol <b>Leader C2/C3 5W-30</b> cumple ACEA C3【29†L35-L42】 y está homologado VW 504.00/507.00. Verificar siempre el manual del vehículo o etiquetas.*
2. **Prompt:** *“¿Cuál es la equivalencia del aceite **Castrol Edge 5W-40 A3/B4** en la marca Shell?”*  
**Respuesta esperada:** *Castrol Edge 5W-40 A3/B4 cumple API SN/CF y ACEA A3/B3/B4【32†L57-L64】. Un equivalente en Shell sería **Shell Helix Ultra 5W-40** (que tiene aprobaciones similares: API SN y ACEA A3/B4, además de BMW LL-01/LL-04). Ambos son aceites 100% sintéticos de alto rendimiento para gasolina y diésel.*
3. **Prompt:** *“Mostrarme las principales diferencias entre **API SN** y <b>ACEA C3</b>.”*  
**Respuesta esperada:** *API SN es una categoría del API enfocada en motores de gasolina actuales (control de depósitos, protección alta temperatura)【36†L79-L81】. ACEA C3 es una categoría europea para motores gasolina/diésel con DPF, exigente en limpieza de motor y compatibilidad con sistemas de post-tratamiento. En general, un aceite con ACEA C3 también cumple API SN o superior. Sin embargo, ACEA C3 tiene límites de viscosidad HTHS más estrictos para ahorrar combustible y proteger filtros.*
4. **Prompt:** *“¿Qué homologaciones debe tener un aceite de transmisión automática para un Mercedes Benz?”*  
**Respuesta esperada:** *Mercedes-Benz publica su estándar **MB 236.14 / 236.17** para transmisiones automáticas. Un aceite ATF aprobado puede listar “MB 236.14” en su ficha técnica. También comúnmente se incluye “BMW 8325.2” si aplica. La ficha técnica o etiqueta del aceite (p.ej. Shell M-1375.4) indicará estas homologaciones.*

Estos ejemplos reflejan respuestas que combinan datos normalizados (especificaciones numéricas) con recomendaciones prácticas, apoyadas en fuentes confiables.

## 7\. Plan de ingestión y esquema de metadatos

Se propone un flujo de ingestión **ETL (extracción, transformación, carga)** descrito mediante Mermaid:

```mermaid
flowchart LR
    A\\\[Fuentes de datos<br/>(sitios OEM, fichas PDF, APIs)] --> B\\\[Extracción<br/>(scraping/PDF to text)];
    B --> C\\\[Transformación<br/>(parser, normalización)];
    C --> D\\\[(Base de datos estructurada)];  
    D --> E\\\[Indexación<br/>(motores de búsqueda / embeddings)];
    E --> F\\\[GPT personalizado<br/>implementado sobre índice];
    F --> G\\\[Consultas de usuarios y generación de respuestas].
```

En este flujo, los **metadatos** definidos incluyen, para cada lubricante:

* `id` (clave única), `marca`, `gama/serie`, `nombre\\\_producto`
* `sector` (vehículo ligero, pesado, moto, etc.)
* `SAE` (p.ej. “5W-30”), `API` (SN, CK-4, etc.), `ACEA` (C3, A5/B5, etc.), `JASO` (MA, MB), `ILSAC`
* `OEM\\\_homologaciones` (lista de códigos: p.ej. “VW 504.00”, “MB 229.51”, “Toyota 0W-30 TOYOTA”, “MAN 3277”, etc.)
* `viscosidad\\\_HTHS`, `SAPS` (low/normal), `biodegradable` (sí/no), `tipo\\\_base` (mineral/sintético/semi)
* `aplicaciones` (gasolina, diésel, transmisiones, etc.), `volumen` (litros típicos), `EAN\\\_producto` (si aplica)
* `fuente\\\_url` o `documento\\\_origen`.

El modelo de datos puede representarse con un diagrama ER:

```mermaid
erDiagram
    LUBRICANTE }|..|| MARCA : pertenece\\\_a
    LUBRICANTE ||--o{ HOMOLOGACION : tiene
    HOMOLOGACION ||--|| OEM : emitida\\\_por
    LUBRICANTE ||--|| SAE : determinado\\\_por
    LUBRICANTE ||--|| API : determinado\\\_por
    LUBRICANTE ||--|| ACEA : determinado\\\_por
    MOTOR ||--|{ ESPECIFICACION\\\_OEM : requiere
    VEHICULO ||--o{ MOTOR : equipa
    LUBRICANTE ||--o{ ESPECIFICACION\\\_OEM : cumple
```

Así, un **ítem Lubricante** se vincula a múltiples especificaciones/API/ACEA y homologaciones emitidas por fabricantes OEM. Cada **Vehículo** o **Motor** puede requerir especificaciones OEM concretas. Este esquema permitirá búsquedas del tipo “encuentra aceite que cumpla \[Norma X] y sea recomendado para \[Vehículo Y]”.

Para indexación se sugiere usar **motores de búsqueda de texto** junto con representaciones vectoriales (embeddings) de documentos/preguntas, de forma que el GPT personalizado pueda encontrar rápidamente fragmentos relevantes (fichas técnicas, manuales) para cada consulta.

## 8\. Aspectos legales y de derechos de autor

Al utilizar fichas técnicas y catálogos (material típicamente protegido por derechos de autor de los fabricantes), es importante seguir buenas prácticas:

* Usar los datos principalmente para **extraer valores de especificaciones** (por ejemplo, “cumple ACEA C3”) en lugar de reproducir largos pasajes literales. Citar breves definiciones o requisitos (como hicimos con \[10], \[32]) puede considerarse uso legítimo si se da crédito.
* Las imágenes o tablas oficiales (por ejemplo, logotipos API/ACEA o diagramas de SAE) deben citarse adecuadamente o redibujarse. En este informe se incluyen tablas y diagramas simplificados propios, no contenidos íntegros protegidos.
* Incluir siempre referencia a la fuente (como URLs oficiales) cuando sea posible, para dar transparencia y permitir verificar la información.
* Verificar licencias específicas: algunos fabricantes permiten uso informativo de sus datos técnicos si se cita la marca. En cualquier caso, se recomienda asesoría legal antes de distribuir copias completas de fichas PDF.
* Asegurar que la base final es para **consulta informativa interna**; no publicar directamente las fichas originales.

\---

**Fuentes:** Se han utilizado documentos y sitios oficiales como Repsol Lubricantes【10†L399-L404】【29†L35-L42】【30†L29-L32】, Castrol【13†L111-L113】【32†L57-L64】, Eni Oil Products【27†L331-L339】【27†L348-L350】, Shell Lubricants【18†L193-L200】 y AD Parts【1†L18-L22】. También se citan guías de asociaciones (API【36†L79-L81】, ACEA【34†L71-L74】, JASO【39†L103-L110】) para definir normas. En los anexos del paquete PDF se incluirán los archivos CSV/JSON normalizados con sus respectivas fuentes.

