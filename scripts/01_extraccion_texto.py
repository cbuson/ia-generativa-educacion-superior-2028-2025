#!/usr/bin/env python3
"""
Extrae texto de archivos PDF y guarda un TXT por documento.

El script no aplica OCR. Los PDF escaneados o sin capa de texto se registran
como archivos con extracción vacía o insuficiente para que puedan revisarse
manualmente.

Uso
    python 01_extraccion_texto.py \
        --entrada ../documentos_originales \
        --salida ../textos_extraidos \
        --registro ../registros/extraccion.csv
"""

from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


def configurar_registro(verbose: bool) -> None:
    nivel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def descubrir_pdf(carpeta: Path) -> Iterable[Path]:
    """Devuelve todos los PDF de la carpeta y sus subcarpetas."""
    yield from sorted(
        ruta for ruta in carpeta.rglob("*")
        if ruta.is_file() and ruta.suffix.lower() == ".pdf"
    )


def extraer_pdf(ruta_pdf: Path) -> tuple[str, int, int]:
    """
    Extrae texto de un PDF.

    Retorna
        texto
        numero de paginas
        numero de paginas sin texto extraible
    """
    lector = PdfReader(str(ruta_pdf))
    paginas = []
    paginas_vacias = 0

    for pagina in lector.pages:
        contenido = pagina.extract_text() or ""
        contenido = contenido.replace("\x00", "")
        if not contenido.strip():
            paginas_vacias += 1
        paginas.append(contenido.strip())

    texto = "\n\n".join(paginas).strip()
    return texto, len(lector.pages), paginas_vacias


def construir_destino(
    archivo: Path,
    carpeta_entrada: Path,
    carpeta_salida: Path,
) -> Path:
    """Conserva la estructura relativa de carpetas."""
    relativo = archivo.relative_to(carpeta_entrada).with_suffix(".txt")
    return carpeta_salida / relativo


def guardar_texto(destino: Path, texto: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8", newline="\n")


def procesar(
    carpeta_entrada: Path,
    carpeta_salida: Path,
    registro_csv: Path,
    minimo_caracteres: int,
) -> int:
    archivos = list(descubrir_pdf(carpeta_entrada))
    if not archivos:
        logging.error("No se encontraron archivos PDF en %s", carpeta_entrada)
        return 1

    registro_csv.parent.mkdir(parents=True, exist_ok=True)
    filas = []

    for indice, archivo in enumerate(archivos, start=1):
        destino = construir_destino(archivo, carpeta_entrada, carpeta_salida)
        estado = "correcto"
        mensaje = ""
        paginas = 0
        paginas_vacias = 0
        caracteres = 0

        try:
            texto, paginas, paginas_vacias = extraer_pdf(archivo)
            caracteres = len(texto)

            if caracteres < minimo_caracteres:
                estado = "revisar"
                mensaje = (
                    "La extracción contiene menos caracteres que el mínimo "
                    "establecido. Puede ser un PDF escaneado."
                )

            guardar_texto(destino, texto)
            logging.info(
                "[%s/%s] %s | %s caracteres",
                indice,
                len(archivos),
                archivo.name,
                caracteres,
            )
        except Exception as exc:
            estado = "error"
            mensaje = str(exc)
            logging.exception("Error al procesar %s", archivo)

        filas.append(
            {
                "archivo_origen": str(archivo.relative_to(carpeta_entrada)),
                "archivo_salida": str(
                    destino.relative_to(carpeta_salida)
                ) if destino.exists() else "",
                "paginas": paginas,
                "paginas_sin_texto": paginas_vacias,
                "caracteres_extraidos": caracteres,
                "estado": estado,
                "observaciones": mensaje,
            }
        )

    with registro_csv.open("w", encoding="utf-8", newline="") as manejador:
        campos = [
            "archivo_origen",
            "archivo_salida",
            "paginas",
            "paginas_sin_texto",
            "caracteres_extraidos",
            "estado",
            "observaciones",
        ]
        escritor = csv.DictWriter(manejador, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)

    errores = sum(fila["estado"] == "error" for fila in filas)
    revisar = sum(fila["estado"] == "revisar" for fila in filas)

    logging.info(
        "Proceso finalizado | archivos %s | errores %s | revisar %s",
        len(filas),
        errores,
        revisar,
    )
    return 1 if errores else 0


def analizar_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(
        description="Extrae texto de PDF sin utilizar OCR."
    )
    analizador.add_argument(
        "--entrada",
        type=Path,
        required=True,
        help="Carpeta con los PDF originales.",
    )
    analizador.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Carpeta de destino de los TXT extraídos.",
    )
    analizador.add_argument(
        "--registro",
        type=Path,
        default=Path("registro_extraccion.csv"),
        help="CSV de control de la extracción.",
    )
    analizador.add_argument(
        "--minimo-caracteres",
        type=int,
        default=200,
        help="Mínimo de caracteres para considerar válida la extracción.",
    )
    analizador.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra información detallada.",
    )
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
        argumentos.registro.resolve(),
        argumentos.minimo_caracteres,
    )


if __name__ == "__main__":
    raise SystemExit(main())
