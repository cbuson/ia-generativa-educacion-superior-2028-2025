#!/usr/bin/env python3
"""
Construye un corpus compatible con IRaMuTeQ a partir de textos normalizados
y un archivo CSV de metadatos.

Columnas obligatorias del CSV
    id_documento
    nombre_archivo_procesado

Las variables suplementarias se seleccionan mediante --variables.
Los nombres y modalidades se normalizan para cumplir el formato de IRaMuTeQ.

Uso
    python 04_preparacion_iramuteq.py \
        --textos ../textos_normalizados \
        --metadatos ../datos/metadatos_corpus.csv \
        --salida ../corpus/corpus_iramuteq.txt \
        --variables anio categoria_analitica tipo_documento pais
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any


PATRON_NO_VALIDO = re.compile(r"[^a-z0-9_]+")
PATRON_GUIONES = re.compile(r"_+")


def configurar_registro(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def quitar_tildes(valor: str) -> str:
    normalizado = unicodedata.normalize("NFKD", valor)
    return "".join(
        caracter for caracter in normalizado
        if not unicodedata.combining(caracter)
    )


def normalizar_modalidad(valor: Any) -> str:
    """
    Convierte una modalidad a un identificador seguro para IRaMuTeQ.
    """
    texto = quitar_tildes(str(valor).strip().lower())
    texto = texto.replace("-", "_").replace(" ", "_")
    texto = PATRON_NO_VALIDO.sub("_", texto)
    texto = PATRON_GUIONES.sub("_", texto).strip("_")
    return texto or "sin_dato"


def normalizar_id(valor: Any) -> str:
    texto = normalizar_modalidad(valor)
    if texto[0].isdigit():
        texto = f"doc_{texto}"
    return texto


def leer_metadatos(ruta: Path) -> list[dict[str, str]]:
    with ruta.open("r", encoding="utf-8-sig", newline="") as manejador:
        lector = csv.DictReader(manejador)
        if not lector.fieldnames:
            raise ValueError("El archivo de metadatos no tiene cabecera")

        obligatorias = {"id_documento", "nombre_archivo_procesado"}
        faltantes = obligatorias.difference(lector.fieldnames)
        if faltantes:
            raise ValueError(
                "Faltan columnas obligatorias "
                + ", ".join(sorted(faltantes))
            )

        return [dict(fila) for fila in lector]


def localizar_texto(carpeta: Path, nombre: str) -> Path:
    candidato = carpeta / nombre
    if candidato.exists() and candidato.is_file():
        return candidato

    coincidencias = list(carpeta.rglob(nombre))
    if len(coincidencias) == 1:
        return coincidencias[0]
    if not coincidencias:
        raise FileNotFoundError(
            f"No se encontró el archivo procesado {nombre}"
        )
    raise RuntimeError(
        f"Existen varias coincidencias para {nombre}"
    )


def construir_cabecera(
    fila: dict[str, str],
    variables: list[str],
) -> str:
    identificador = normalizar_id(fila["id_documento"])
    partes = [f"*id_{identificador}"]

    for variable in variables:
        valor = normalizar_modalidad(fila.get(variable, ""))
        nombre = normalizar_modalidad(variable)
        partes.append(f"*{nombre}_{valor}")

    return "**** " + " ".join(partes)


def validar_ids(filas: list[dict[str, str]]) -> None:
    ids = [normalizar_id(fila["id_documento"]) for fila in filas]
    duplicados = sorted(
        identificador
        for identificador in set(ids)
        if ids.count(identificador) > 1
    )
    if duplicados:
        raise ValueError(
            "Existen identificadores duplicados "
            + ", ".join(duplicados)
        )


def procesar(
    carpeta_textos: Path,
    archivo_metadatos: Path,
    archivo_salida: Path,
    variables: list[str],
    registro: Path,
) -> int:
    filas = leer_metadatos(archivo_metadatos)
    validar_ids(filas)

    archivo_salida.parent.mkdir(parents=True, exist_ok=True)
    registro.parent.mkdir(parents=True, exist_ok=True)

    bloques = []
    control = []
    errores = 0

    for orden, fila in enumerate(filas, start=1):
        identificador = fila["id_documento"].strip()
        nombre_archivo = fila["nombre_archivo_procesado"].strip()

        try:
            ruta_texto = localizar_texto(
                carpeta_textos,
                nombre_archivo,
            )
            texto = ruta_texto.read_text(
                encoding="utf-8"
            ).strip()

            if not texto:
                raise ValueError("El texto procesado está vacío")

            cabecera = construir_cabecera(fila, variables)
            bloques.append(f"{cabecera}\n{texto}")

            control.append(
                {
                    "orden": orden,
                    "id_documento": identificador,
                    "archivo": str(
                        ruta_texto.relative_to(carpeta_textos)
                    ),
                    "cabecera": cabecera,
                    "caracteres": len(texto),
                    "estado": "correcto",
                    "observaciones": "",
                }
            )
            logging.info(
                "[%s/%s] %s",
                orden,
                len(filas),
                identificador,
            )
        except Exception as exc:
            errores += 1
            logging.exception(
                "Error con el documento %s",
                identificador,
            )
            control.append(
                {
                    "orden": orden,
                    "id_documento": identificador,
                    "archivo": nombre_archivo,
                    "cabecera": "",
                    "caracteres": "",
                    "estado": "error",
                    "observaciones": str(exc),
                }
            )

    if bloques:
        archivo_salida.write_text(
            "\n\n".join(bloques).strip() + "\n",
            encoding="utf-8",
            newline="\n",
        )

    with registro.open("w", encoding="utf-8", newline="") as manejador:
        campos = [
            "orden",
            "id_documento",
            "archivo",
            "cabecera",
            "caracteres",
            "estado",
            "observaciones",
        ]
        escritor = csv.DictWriter(manejador, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(control)

    logging.info(
        "Corpus generado | documentos %s | errores %s",
        len(bloques),
        errores,
    )
    return 1 if errores else 0


def analizar_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(
        description="Prepara un corpus compatible con IRaMuTeQ."
    )
    analizador.add_argument("--textos", type=Path, required=True)
    analizador.add_argument("--metadatos", type=Path, required=True)
    analizador.add_argument("--salida", type=Path, required=True)
    analizador.add_argument(
        "--variables",
        nargs="*",
        default=[
            "anio",
            "categoria_analitica",
            "tipo_documento",
            "pais",
        ],
    )
    analizador.add_argument(
        "--registro",
        type=Path,
        default=Path("registro_iramuteq.csv"),
    )
    analizador.add_argument("--verbose", action="store_true")
    return analizador.parse_args()


def main() -> int:
    argumentos = analizar_argumentos()
    configurar_registro(argumentos.verbose)

    if not argumentos.textos.exists():
        logging.error("La carpeta de textos no existe")
        return 2

    if not argumentos.metadatos.exists():
        logging.error("El archivo de metadatos no existe")
        return 2

    return procesar(
        argumentos.textos.resolve(),
        argumentos.metadatos.resolve(),
        argumentos.salida.resolve(),
        argumentos.variables,
        argumentos.registro.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
