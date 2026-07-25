
# IA generativa en la educación superior

Este repositorio reúne los archivos utilizados en el análisis del corpus del artículo **IA generativa en la educación superior. Del entusiasmo a una comprensión crítica**.

El estudio se basa en 171 documentos en castellano publicados entre 2018 y el primer semestre de 2025. Los textos fueron preparados mediante scripts en Python y analizados con IRaMuTeQ.

El repositorio se ofrece exclusivamente con fines académicos, científicos y metodológicos. Su finalidad es permitir la transparencia del proceso de investigación, la verificación de los procedimientos aplicados y la reproducción de los análisis descritos en el artículo.

## Estructura del repositorio

### iramuteq_corpus_corpus_4

Carpeta generada durante el procesamiento del corpus con IRaMuTeQ.

Contiene los archivos de trabajo y las salidas producidas por el programa durante los análisis lexicométricos. Estos archivos se conservan para facilitar la comprobación de los resultados y la trazabilidad del procedimiento.

### scripts

Carpeta que contiene los scripts desarrollados en Python para preparar, organizar y comprobar el corpus.

Los scripts realizan tareas de extracción de texto, normalización, unión de documentos, preparación del archivo compatible con IRaMuTeQ y validación de la estructura del corpus.

Los scripts se proporcionan con fines de transparencia y reproducción metodológica. Su utilización debe acompañarse de una revisión técnica de los parámetros, las versiones del software y las características de los documentos procesados.

### iramuteq_corpus4.txt

Archivo principal del corpus preparado para su análisis con IRaMuTeQ.

Contiene los textos normalizados y organizados con las cabeceras necesarias para identificar los documentos y sus variables analíticas.

Este archivo es un material de investigación derivado del procesamiento automatizado de fuentes académicas e institucionales. No constituye una edición, reproducción comercial o sustitución de los documentos originales.

### listado_archivos.txt

Inventario de los archivos que forman parte del corpus.

Permite comprobar qué documentos fueron incorporados al análisis y facilita la correspondencia entre los textos originales, los textos procesados y sus identificadores.

El inventario se publica para fines de control documental, auditoría académica y reproducción del estudio.

### textoslimpios.zip

Archivo comprimido que contiene los textos individuales después del proceso de extracción, limpieza y normalización.

Estos archivos fueron utilizados para construir el corpus conjunto `iramuteq_corpus4.txt`.

Los textos procesados se incluyen únicamente para permitir la verificación académica del tratamiento textual y de los resultados obtenidos. No deben utilizarse para distribución comercial, publicación independiente, entrenamiento de productos comerciales, creación de bases de datos con fines lucrativos ni sustitución de las fuentes originales.

## Metodología general

Los documentos originales fueron convertidos a texto plano y normalizados mediante scripts en Python.

El procedimiento incluyó la conversión a codificación UTF-8, la eliminación de caracteres problemáticos, direcciones web, identificadores DOI, números aislados y otros elementos sin valor para el análisis textual.

Posteriormente, los textos fueron unidos y preparados según la estructura requerida por IRaMuTeQ.

El análisis incluyó frecuencias léxicas, nube de palabras, análisis de similitud, clasificación jerárquica descendente y análisis factorial de correspondencias.

Los archivos depositados permiten examinar el flujo general de trabajo. Las cifras correspondientes a ocurrencias, formas, lemas, segmentos y cobertura de clasificación deben interpretarse de acuerdo con las salidas producidas por IRaMuTeQ, ya que otros programas pueden aplicar reglas diferentes de tokenización, segmentación y lematización.

## Datos principales

* 171 documentos analizados
* Periodo comprendido entre 2018 y el primer semestre de 2025
* 2.891.637 ocurrencias
* 82.063 unidades textuales
* 73.640 segmentos clasificados
* Cobertura de clasificación del 89,74 por ciento

## Finalidad académica del repositorio

Los materiales se ponen a disposición exclusivamente para los siguientes fines:

* Verificación de los procedimientos descritos en el artículo
* Reproducción académica de los análisis
* Investigación científica
* Docencia y formación metodológica
* Evaluación por pares
* Auditoría y revisión de resultados
* Desarrollo de estudios comparativos sin finalidad comercial

La consulta o descarga de los archivos no autoriza usos comerciales ni modifica las condiciones jurídicas aplicables a los documentos originales.

Toda reutilización deberá respetar la autoría, las licencias, las condiciones de acceso y las normas de citación de cada fuente.

## Derechos de autor y propiedad intelectual

Los documentos originales pertenecen a sus respectivos autores, editoriales, universidades, organismos e instituciones.

La inclusión de referencias, fragmentos procesados o textos normalizados en este repositorio no implica transferencia de derechos de autor, cesión de propiedad intelectual ni atribución de titularidad sobre las obras originales.

Este repositorio no pretende sustituir las publicaciones originales. Para consultar, citar o reutilizar un documento debe acudirse a la fuente original y respetarse su licencia correspondiente.

Cuando un documento esté sujeto a una licencia específica, dicha licencia prevalece sobre cualquier descripción general contenida en este repositorio.

La disponibilidad de un archivo en el repositorio no debe interpretarse como autorización para:

* Redistribuir comercialmente los textos
* Publicarlos como una colección independiente
* Eliminar la autoría original
* Modificar o suprimir las licencias de las fuentes
* Presentar los documentos como obras propias
* Utilizarlos para productos o servicios comerciales sin autorización
* Crear repositorios derivados que oculten o sustituyan las fuentes originales

## Responsabilidad de las personas usuarias

Las personas que consulten o descarguen los materiales son responsables de comprobar las condiciones de uso de cada documento original.

El responsable del repositorio no autoriza usos que excedan los fines académicos, científicos, docentes y metodológicos aquí declarados.

La reproducción de los resultados puede variar según la versión de Python, R, IRaMuTeQ, las bibliotecas empleadas y los parámetros de procesamiento. Toda diferencia debe documentarse de manera transparente.

## Solicitudes de corrección o retirada

Si un autor, institución o titular de derechos considera que algún material ha sido incluido de forma incorrecta o requiere una corrección en su atribución, puede solicitar su revisión mediante el correo de contacto indicado en este repositorio.

Las solicitudes fundadas serán examinadas y, cuando corresponda, el archivo será corregido, sustituido o retirado.

## Citación

Toda utilización académica de este repositorio deberá citar tanto el artículo como el conjunto de datos.

La referencia bibliográfica definitiva se incorporará una vez que el artículo disponga de los datos editoriales completos y el repositorio cuente con una versión estable.

## Responsable

Carlos Busón Buesa

Universidade Federal de Mato Grosso do Sul

carlos.buson@ufms.br

## Declaración final

Este repositorio tiene una finalidad exclusivamente académica, científica y metodológica.

Los materiales se publican para favorecer la transparencia, la verificabilidad y la reproducción del estudio. No se autoriza su explotación comercial ni ningún uso que vulnere la propiedad intelectual, las licencias o los derechos de los autores e instituciones responsables de los documentos originales.


