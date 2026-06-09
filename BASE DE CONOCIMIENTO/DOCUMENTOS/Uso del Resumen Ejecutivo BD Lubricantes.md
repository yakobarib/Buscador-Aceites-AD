# **Uso del Resumen Ejecutivo**

El resumen ejecutivo sirve como **guía de implementación** . Para utilizarlo:







**Extraer objetivos:** Cada sección del resumen corresponde a un paso práctico (ej. recopilar fichas
técnicas, normalizar datos, generar tablas comparativas).
**Organizar tareas:** Traduzca las recomendaciones en un plan de acción (recopilar datos,
procesarlos, validar, indexar). Por ejemplo, al leer la sección de homologaciones se sabe que hay
que extraer “niveles de calidad, homologaciones y recomendaciones” de las fichas [1](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_C2_C3_5W-30_ES.pdf#:~:text=Niveles%20de%20calidad%2C%20homologaciones%20y,30) [2](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_INYECCION_15W-40_ES.pdf#:~:text=Niveles%20de%20calidad%2C%20homologaciones%20y,MB%20229.1) .
**Aplicar criterios:** Use las recomendaciones (inclusión de datos oficiales, evitar duplicados,
metadatos, etc.) para filtrar qué información entra en la base. El resumen indica qué campos son
clave (SAE, API, OEM, etc.) y cómo priorizar fuentes.
**Herramientas sugeridas:** Como referencia, emplee librerías de programación (ej.
Python+Pandas) o ETL (Talend, Apache NiFi) para procesar los datos. Use herramientas OCR/PDF
(PyPDF2, Tabula) para convertir fichas a texto/tablas, y APIs web para descargar catálogos.







[1](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_C2_C3_5W-30_ES.pdf#:~:text=Niveles%20de%20calidad%2C%20homologaciones%20y,30) [2](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_INYECCION_15W-40_ES.pdf#:~:text=Niveles%20de%20calidad%2C%20homologaciones%20y,MB%20229.1)












- **Flujo de trabajo:** Siga el flujo ETL planteado: obtención de datos → normalización/limpieza →



generación de CSV/JSON → carga en índice de búsqueda. Cada paso del resumen se convierte en
una tarea de ingeniería.

# **Generación de archivos CSV/JSON normalizados**


Los documentos de conocimiento para el GPT son básicamente **archivos de datos estructurados** con
las tablas y metadatos obtenidos. En la práctica se generarían así:


`BeautifulSoup` ) para extraer texto.

    - **Normalización de columnas:** Cree un DataFrame (p.ej. en Pandas) con las columnas





aprobaciones OEM (como listas) y complete los campos de rendimiento. Para generar
equivalencias de producto entre marcas, use criterios como viscosidad, especificación y familia
de producto; por ejemplo, si dos aceites distintos comparten SAE/API/ACEA, se considera
equivalencia funcional.

- **Exportar archivos:** Finalmente, exporte el DataFrame a CSV


para cada tabla solicitada (homologaciones, especificaciones OEM, equivalencias referencias,
catálogos resumidos).

- **Metadatos:** Asegúrese de incluir en cada archivo (CSV/JSON) los metadatos requeridos. Por

ejemplo, en JSON cada objeto tendrá propiedades idénticas a las columnas de CSV. Estos
archivos son los que el GPT leerá para responder.


1


## **Ejemplos de archivos normalizados**

A continuación se muestran ejemplos con **10 filas** de muestra (datos ficticios) en CSV y JSON, siguiendo
el formato solicitado:


**Ejemplo de CSV (** **`lubricantes.csv`** **):**

```
 id,marca,producto,SAE,API,ACEA,JASO,ILSAC,OEM_homologaciones,viscosidad_HTHS,SAPS,tipo_base,ap
 LUB1,Repsol,Leader C3 5W-30,5W-30,SN, C2/C3,,GF-5,["VW 504.00/507.00","BMW
 LL-04"],3.5,Bajo,Sintético,"Gasolina/Diesel",8410247123456,https://
 lubricants.repsol.com/productos/leader-c3-5w30,2021-07-01,es
 LUB2,Castrol,EDGE 5W-40 A3/B4,5W-40,SN, A3/B3/B4,,GF-5,["MB 226.5","VW
 502.00"],3.7,Bajo,Sintético,"Gasolina/Diesel",5010394105678,https://
 www.castrol.com/edge-5w40,2021-08-15,es
 LUB3,Eni,i-Sint Tech 5W-30,5W-30,SN, A1/B1,,GF-5,["FIAT 9.55535-DS1"],
 3.2,Medio,Sintético,"Gasolina",8001299001234,https://oilproducts.eni.com/es/
 productos/lubricantesi-sint,2021-06-10,es
 LUB4,Shell,Helix Ultra 10W-40,10W-40,SM, A3/B4,,GF-5,["Renault RN0700","MB
 229.1"],4.0,Alto,Sintético,"Gasolina",S/ABE687C4B,https://www.shell.com/
 helix-ultra-10w40,2021-05-20,es
 LUB5,AD Parts,Generic 15W-40,15W-40,CI-4, E7/E9,,GF-5,["MAN 3277","VOLVO
 VDS-3"],4.5,Medio,Convencional,"Diesel",6291100456783,http://www.adparts.com/
 lubricantes,2021-09-01,es
 LUB6,Repsol,Elite F. 0W-20,0W-20,SN Plus, A5/B5,,GF-6,["VW 508.00/509.00"],
 3.0,Muy Bajo,Sintético,"Gasolina",8410247123345,https://
 lubricants.repsol.com/productos/elite-f-0w20,2021-07-01,es
 LUB7,Castrol,AGRAS 15W-40,15W-40,CI-4, E7/E9,,GF-5,["DEUTZ DQC III-10"],
 4.4,Alto,Semisintético,"Diesel",5010394501237,https://www.castrol.com/
 agras-15w40,2021-08-15,es
 LUB8,Eni,Spirax S6 GXME 80W-90,80W-90,,EP-2,,,"ANSI/AGMA 9005-E02",
 18.5,Alto,Sintético,"Engranajes",8001299006789,https://oilproducts.eni.com/
 es/products/spirax-s6-gxme,2021-06-10,es
 LUB9,Shell,Rimula R4 X 10W-40,10W-40,CK-4, E6/E9,,GF-5,["MB 228.31","MAN
 3275"],4.2,Alto,Sintético,"Diesel pesada",S/ABCD123456,https://www.shell.com/
 rimula-r4-10w40,2021-05-20,es
 LUB10,Repsol,Leader Injection 15W-40,15W-40,SL, A3/B4,,GF-5,["MB 229.1"],
 4.0,Alto,Convencional,"Gasolina/Diesel",8410247123567,https://
 lubricants.repsol.com/productos/leader-inyeccion-15w40,2021-07-01,es

```

_(Cada fila es un producto con sus especificaciones normalizadas.)_


**Ejemplo de JSON (** **`lubricantes.json`** **):**

```
 [
  {
   "id": "LUB1",
   "marca": "Repsol",
   "producto": "Leader C3 5W-30",
   "SAE": "5W-30",

```

2


```
   "API": "SN",
   "ACEA": "C2/C3",
   "JASO": "",
   "ILSAC": "GF-5",
   "OEM_homologaciones": ["VW 504.00/507.00", "BMW LL-04"],
   "viscosidad_HTHS": 3.5,
   "SAPS": "Bajo",
   "tipo_base": "Sintético",
   "aplicaciones": "Gasolina/Diesel",
   "EAN": "8410247123456",
   "fuente_url": "https://lubricants.repsol.com/productos/leader-c3-5w30",
   "fecha_fuente": "2021-07-01",
   "idioma_fuente": "es"
  },
  {
   "id": "LUB2",
   "marca": "Castrol",
   "producto": "EDGE 5W-40 A3/B4",
   "SAE": "5W-40",
   "API": "SN",
   "ACEA": "A3/B3/B4",
   "JASO": "",
   "ILSAC": "GF-5",
   "OEM_homologaciones": ["MB 226.5", "VW 502.00"],
   "viscosidad_HTHS": 3.7,
   "SAPS": "Bajo",
   "tipo_base": "Sintético",
   "aplicaciones": "Gasolina/Diesel",
   "EAN": "5010394105678",
   "fuente_url": "https://www.castrol.com/edge-5w40",
   "fecha_fuente": "2021-08-15",
   "idioma_fuente": "es"
  }
  /* Se omiten filas 3-10 por brevedad; seguirían el mismo formato con datos
 de Eni, Shell, AD Parts, etc. */
 ]

```

Estos ejemplos ilustran la estructura. En la entrega final real, se incluirían archivos completos (CSV y
JSON) con todas las filas recopiladas.

# **Plan ETL y Pipeline de Ingestión**


Para implementar la carga de estos datos en el sistema del GPT, se propone el siguiente pipeline (pasos
con herramientas sugeridas):



1.



**Descarga de datos:** usar Python y librerías HTTP (por ejemplo `requests` - `selenium` ) para

descargar fichas PDF y páginas web oficiales. Por ejemplo:


3


```
import requests
url = "https://lubricants.repsol.com/productos/leader-c3-5w30"
html = requests.get(url).text

```


1.



**Extracción de contenido:** convertir las fichas descargadas a texto o tablas. Ejemplo con PDF:


```
 import pdfplumber
 pdf = pdfplumber.open("Leader_C3_5W30.pdf")
 text = ""
 for page in pdf.pages:
   text += page.extract_text()

```

Para tablas complejas, usar `tabula-py` - `camelot` .

3. **Parsing y normalización:** analizar el texto extraído con expresiones regulares o heurísticas para
extraer los campos clave (SAE, API, ACEA, homologaciones OEM, etc.). Por ejemplo, identificar líneas que
contienen “ACEA” o “API” y separar sus valores.
4. **Construcción de DataFrames:** llenar los DataFrames de Pandas con los valores extraídos. Por
ejemplo:

```
 import pandas as pd
 df = pd.DataFrame(columns=["id","marca","producto","SAE",...])
 df.loc[0] = ["LUB1","Repsol","Leader C3 5W-30","5W-30","SN","C2/C3",...]

```


1.


2.



**Validación de datos:** comprobar que no haya filas duplicadas ( `df.drop_duplicates()` ), que

los formatos sean correctos (SAE con “W”, listas JSON bien formateadas para OEM, etc.) y que los
valores numéricos (viscosidad) estén en rango plausible.
**Exportación:** guardar los datos en archivos:


```
df.to_csv("lubricantes.csv", index=False, encoding="utf-8")
df.to_json("lubricantes.json", orient="records", force_ascii=False)

```


1.


2.



**Indexación para GPT:** cargar estos archivos en el repositorio del GPT. Esto puede hacerse
ingiriendo los CSV/JSON a una base de datos (SQL o NoSQL) o a un índice de búsqueda. Por
ejemplo, usar Elasticsearch o un buscador vectorial: los textos (por ejemplo, concatenando
campos relevantes) se transforman en embeddings y se guardan para consultas rápidas.
**Integración con el GPT:** los prompts del GPT pueden llamar a un buscador interno que lea estos
datos. Al construirse el corpus con los CSV/JSON, cada consulta puede filtrarse con metadatos
(por ejemplo, buscando por `producto` - `marca` ) y devolver la respuesta basada en esos

datos normalizados.


# **Checklist de Validación de Datos**

Antes de finalizar, verifique lo siguiente:


   - Todos los campos requeridos existen en cada fila de CSV/JSON.

   - Los valores numéricos (viscosidad_HTHS, etc.) tienen la unidad correcta y decimales apropiados.


4


- Las listas ( `OEM_homologaciones` ) están entre corchetes y con comillas según JSON estándar.

- No hay registros duplicados (mismos `id` - mismo `producto` ).







Las relaciones de equivalencia tienen sentido (mismos SAE/API implican producto equivalente
entre marcas).











“Mineral”/“Sintético”).

# **Entrega del paquete y descarga**


El paquete final se entregaría en formato comprimido (ZIP) que incluiría:








**Informe PDF** con el contenido analítico (resúmenes, tablas, diagramas, checklist, citas).
**Anexos CSV/JSON separados** por cada conjunto de datos (homologaciones, equivalencias, etc.),
listos para indexar.
**Sección de fuentes** que documente todos los enlaces citados.







En este entorno no podemos crear enlaces de descarga reales. Sin embargo, en la práctica el receptor
recibiría un enlace (por ejemplo, Google Drive o correo electrónico) con los archivos adjuntos. Los
ejemplos de CSV/JSON mostrados arriba podrían copiarse en archivos `.csv` y `.json` .


**Nota:** El asistente puede generar el contenido estructurado (ejemplos, tablas y pseudocódigo) tal como
se ve aquí, pero los archivos finales con todos los datos reales requerirían extracción automática o
manual desde las fuentes (lo cual está descrito en la sección de pipeline). Los fragmentos de CSV/JSON
proporcionados son muestras de formato, y su contenido completo dependería de la recolección real
de datos.



[1](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_C2_C3_5W-30_ES.pdf#:~:text=Niveles%20de%20calidad%2C%20homologaciones%20y,30)



Ficha técnica LEADER C2 C3 5W-30



[https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_C2_C3_5W-30_ES.pdf)

[LEADER_C2_C3_5W-30_ES.pdf](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_C2_C3_5W-30_ES.pdf)



[2](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_INYECCION_15W-40_ES.pdf#:~:text=Niveles%20de%20calidad%2C%20homologaciones%20y,MB%20229.1)



Ficha técnica LEADER INYECCION 15W-40



[https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_INYECCION_15W-40_ES.pdf)

[LEADER_INYECCION_15W-40_ES.pdf](https://lubricants.repsol.com/content/dam/repsol-lubricantes/es/productos-y-servicios/lubricantes-documentos/LEADER_INYECCION_15W-40_ES.pdf)


5


