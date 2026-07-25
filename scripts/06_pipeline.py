#!/usr/bin/env python3
"""
Ejecuta de forma ordenada la extracción, normalización, preparación y
validación del corpus.

Este archivo utiliza los otros scripts del directorio. Debe ejecutarse desde
la carpeta scripts o desde cualquier lugar indicando --proyecto.

Estructura esperada
    proyecto
        documentos_originales
        datos
            metadatos_corpus.csv
        config
            variantes.csv
        scripts
        textos_extraidos
        textos_normalizados
        corpus
        registros

Uso
    python 06_pipeline.py --proyecto ..
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path


def ejecutar(comando: list[str]) -> None:
    logging.info("Ejecutando %s", " ".join(comando))
    resultado = subprocess.run(comando, check=False)
    if resultado.returncode != 0:
        raise RuntimeError(
            f"El comando terminó con código {resultado.returncode}"
        )


def analizar_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(
        description="Ejecuta el flujo completo del corpus."
    )
    analizador.add_argument(
        "--proyecto",
        type=Path,
        required=True,
        help="Carpeta raíz del proyecto.",
    )
    analizador.add_argument(
        "--eliminar-stopwords",
        action="store_true",
    )
    analizador.add_argument(
        "--esperados",
        type=int,
        default=171,
    )
    analizador.add_argument("--verbose", action="store_true")
    return analizador.parse_args()


def main() -> int:
    argumentos = analizar_argumentos()
    logging.basicConfig(
        level=logging.DEBUG if argumentos.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    proyecto = argumentos.proyecto.resolve()
    scripts = Path(__file__).resolve().parent

    documentos = proyecto / "documentos_originales"
    extraidos = proyecto / "textos_extraidos"
    normalizados = proyecto / "textos_normalizados"
    datos = proyecto / "datos"
    config = proyecto / "config"
    corpus = proyecto / "corpus"
    registros = proyecto / "registros"

    registros.mkdir(parents=True, exist_ok=True)
    corpus.mkdir(parents=True, exist_ok=True)

    variantes = config / "variantes.csv"
    metadatos = datos / "metadatos_corpus.csv"

    comando_extraccion = [
        sys.executable,
        str(scripts / "01_extraccion_texto.py"),
        "--entrada",
        str(documentos),
        "--salida",
        str(extraidos),
        "--registro",
        str(registros / "extraccion.csv"),
    ]
    ejecutar(comando_extraccion)

    comando_normalizacion = [
        sys.executable,
        str(scripts / "02_normalizacion_corpus.py"),
        "--entrada",
        str(extraidos),
        "--salida",
        str(normalizados),
        "--registro",
        str(registros / "normalizacion.csv"),
    ]
    if variantes.exists():
        comando_normalizacion.extend(
            ["--variantes", str(variantes)]
        )
    if argumentos.eliminar_stopwords:
        comando_normalizacion.append("--eliminar-stopwords")
    ejecutar(comando_normalizacion)

    ejecutar(
        [
            sys.executable,
            str(scripts / "03_union_documentos.py"),
            "--entrada",
            str(normalizados),
            "--salida",
            str(corpus / "corpus_normalizado_unido.txt"),
            "--manifiesto",
            str(corpus / "manifiesto_union.csv"),
        ]
    )

    ejecutar(
        [
            sys.executable,
            str(scripts / "04_preparacion_iramuteq.py"),
            "--textos",
            str(normalizados),
            "--metadatos",
            str(metadatos),
            "--salida",
            str(corpus / "corpus_iramuteq.txt"),
            "--registro",
            str(registros / "preparacion_iramuteq.csv"),
        ]
    )

    ejecutar(
        [
            sys.executable,
            str(scripts / "05_validacion_corpus.py"),
            "--corpus",
            str(corpus / "corpus_iramuteq.txt"),
            "--metadatos",
            str(metadatos),
            "--informe-json",
            str(registros / "validacion.json"),
            "--esperados",
            str(argumentos.esperados),
        ]
    )

    logging.info("Flujo completo finalizado correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
