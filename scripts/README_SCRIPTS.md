# Scripts de preparación del corpus

Estos archivos constituyen una reconstrucción documentada del flujo descrito
en el artículo. No deben presentarse como los scripts originales si estos no se
conservan.

## Archivos

`01_extraccion_texto.py`

Extrae la capa textual de los PDF y genera un registro de control. No utiliza
OCR.

`02_normalizacion_corpus.py`

Normaliza Unicode, elimina URL, DOI, números aislados y caracteres de control.
También permite aplicar un diccionario verificable de variantes y eliminar
palabras vacías en castellano, portugués e inglés.

`03_union_documentos.py`

Une los TXT normalizados y genera un manifiesto con huellas SHA-256.

`04_preparacion_iramuteq.py`

Construye el corpus con cabeceras compatibles con IRaMuTeQ a partir de un CSV
de metadatos.

`05_validacion_corpus.py`

Valida el número de documentos, las cabeceras, los identificadores, los
documentos vacíos y la correspondencia con los metadatos.

`06_pipeline.py`

Ejecuta el flujo completo.

## Instalación

```bash
python -m venv .venv
```

En Windows

```bash
.venv\Scripts\activate
```

En Linux o macOS

```bash
source .venv/bin/activate
```

Instalación de dependencias

```bash
pip install -r requirements.txt
```

## Estructura mínima

```text
proyecto/
├── documentos_originales/
├── datos/
│   └── metadatos_corpus.csv
├── config/
│   └── variantes.csv
├── scripts/
├── textos_extraidos/
├── textos_normalizados/
├── corpus/
└── registros/
```

## Metadatos obligatorios

El archivo `metadatos_corpus.csv` debe contener al menos

```csv
id_documento,nombre_archivo_procesado,anio,categoria_analitica,tipo_documento,pais
DOC001,DOC001.txt,2023,institucional,informe,internacional
```

## Diccionario de variantes

El archivo opcional `variantes.csv` debe utilizar esta estructura

```csv
variante,forma_unificada
chat gpt,chatgpt
inteligencia artificial generativa,ia_generativa
```

No deben añadirse equivalencias que no hayan formado parte real del proceso de
normalización.

## Ejecución completa

Desde la carpeta `scripts`

```bash
python 06_pipeline.py --proyecto .. --esperados 171
```

La eliminación de palabras vacías solamente se activa cuando se añade

```bash
python 06_pipeline.py --proyecto .. --esperados 171 --eliminar-stopwords
```

## Verificación de las cifras

El script de validación ofrece controles documentales y conteos diagnósticos.
Las cifras de ocurrencias, formas, lemas, segmentos y cobertura de la
clasificación jerárquica descendente deben verificarse con las salidas
originales de IRaMuTeQ.

No debe afirmarse que los conteos de Python reproducen las estadísticas de
IRaMuTeQ porque aplican reglas distintas de tokenización, lematización y
segmentación.
