#!/usr/bin/env python3
"""
Une los textos normalizados en un archivo continuo y genera un manifiesto.

Este archivo no añade cabeceras de IRaMuTeQ. Para crear el corpus analítico
debe utilizarse 04_preparacion_iramuteq.py.

Uso
    python 03_union_documentos.py \
        --entrada ../textos_normalizados \
        --salida ../corpus/corpus_normalizado_unido.txt \
        --manifiesto ../corpus/manifiesto_union.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
from pathlib import Path
from typing import Iterable


def configurar_registro(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def descubrir_txt(carpeta: Path) -> Iterable[Path]:
    yield from sorted(
        ruta for ruta in carpeta.rglob("*")
        if ruta.is_file() and ruta.suffix.lower() == ".txt"
    )


def hash_sha256(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def procesar(
    carpeta_entrada: Path,
    archivo_salida: Path,
    manifiesto: Path,
    separador: str,
) -> int:
    archivos = list(descubrir_txt(carpeta_entrada))
    if not archivos:
        logging.error("No se encontraron archivos TXT")
        return 1

    archivo_salida.parent.mkdir(parents=True, exist_ok=True)
    manifiesto.parent.mkdir(parents=True, exist_ok=True)

    bloques = []
    filas = []

    for orden, archivo in enumerate(archivos, start=1):
        relativo = archivo.relative_to(carpeta_entrada)
        contenido = archivo.read_text(encoding="utf-8").strip()
        contenido_bytes = contenido.encode("utf-8")

        bloques.append(contenido)
        filas.append(
            {
                "orden": orden,
                "archivo": str(relativo),
                "caracteres": len(contenido),
                "bytes_utf8": len(contenido_bytes),
                "sha256": hash_sha256(contenido_bytes),
            }
        )

    texto_unido = separador.join(bloques).strip() + "\n"
    archivo_salida.write_text(
        texto_unido,
        encoding="utf-8",
        newline="\n",
    )

    with manifiesto.open("w", encoding="utf-8", newline="") as manejador:
        escritor = csv.DictWriter(
            manejador,
            fieldnames=[
                "orden",
                "archivo",
                "caracteres",
                "bytes_utf8",
                "sha256",
            ],
        )
        escritor.writeheader()
        escritor.writerows(filas)

    logging.info(
        "Se unieron %s documentos en %s",
        len(archivos),
        archivo_salida,
    )
    return 0


def analizar_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(
        description="Une archivos TXT normalizados."
    )
    analizador.add_argument("--entrada", type=Path, required=True)
    analizador.add_argument("--salida", type=Path, required=True)
    analizador.add_argument("--manifiesto", type=Path, required=True)
    analizador.add_argument(
        "--separador",
        default="\n\n",
        help="Separador entre documentos.",
    )
    analizador.add_argument("--verbose", action="store_true")
    return analizador.parse_args()


def main() -> int:
    argumentos = analizar_argumentos()
    configurar_registro(argumentos.verbose)

    if not argumentos.entrada.exists():
        logging.error("La carpeta de entrada no existe")
        return 2

    return procesar(
        argumentos.entrada.resolve(),
        argumentos.salida.resolve(),
        argumentos.manifiesto.resolve(),
        argumentos.separador,
    )


if __name__ == "__main__":
    raise SystemExit(main())
