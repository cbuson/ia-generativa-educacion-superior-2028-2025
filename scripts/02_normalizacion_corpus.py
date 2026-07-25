#!/usr/bin/env python3
"""
Normaliza los textos extraídos antes de preparar el corpus para IRaMuTeQ.

Operaciones disponibles
    Normalización Unicode NFKC
    Eliminación de caracteres de control
    Reparación básica de palabras cortadas al final de línea
    Eliminación de URL
    Eliminación de DOI
    Eliminación opcional de correos electrónicos
    Eliminación opcional de números aislados
    Sustitución opcional de variantes léxicas
    Eliminación opcional de palabras vacías en castellano, portugués e inglés

La eliminación de palabras vacías se activa únicamente mediante
--eliminar-stopwords. El script conserva siempre una copia independiente
de los textos extraídos.

Uso
    python 02_normalizacion_corpus.py \
        --entrada ../textos_extraidos \
        --salida ../textos_normalizados \
        --registro ../registros/normalizacion.csv \
        --variantes ../config/variantes.csv \
        --eliminar-stopwords
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import unicodedata
from pathlib import Path
from typing import Iterable

try:
    from stopwordsiso import stopwords
except ImportError:
    stopwords = None


PATRON_URL = re.compile(
    r"""(?ix)
    \b(
        https?://[^\s<>()]+
        |
        www\.[^\s<>()]+
    )
    """
)

PATRON_DOI = re.compile(
    r"""(?ix)
    \b(?:doi\s*:\s*)?
    10\.\d{4,9}/[-._;()/:a-z0-9]+
    """
)

PATRON_CORREO = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    flags=re.IGNORECASE,
)

PATRON_CONTROL = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"
)

PATRON_NUMERO_AISLADO = re.compile(
    r"(?<![\w.,])\d+(?:[.,]\d+)?(?![\w.,])"
)

PATRON_ESPACIOS = re.compile(r"[ \t]+")
PATRON_LINEAS = re.compile(r"\n{3,}")
PATRON_TOKEN = re.compile(r"\b[\wáéíóúüñç]+\b", re.IGNORECASE)


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


def cargar_variantes(ruta: Path | None) -> dict[str, str]:
    """
    Lee un CSV UTF-8 con columnas variante y forma_unificada.

    Ejemplo
        variante,forma_unificada
        chat gpt,chatgpt
        inteligencia artificial generativa,ia_generativa
    """
    if ruta is None:
        return {}

    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo de variantes {ruta}")

    variantes: dict[str, str] = {}
    with ruta.open("r", encoding="utf-8-sig", newline="") as manejador:
        lector = csv.DictReader(manejador)
        esperadas = {"variante", "forma_unificada"}
        if not lector.fieldnames or not esperadas.issubset(lector.fieldnames):
            raise ValueError(
                "El CSV de variantes debe contener las columnas "
                "variante y forma_unificada"
            )

        for fila in lector:
            origen = (fila.get("variante") or "").strip()
            destino = (fila.get("forma_unificada") or "").strip()
            if origen and destino:
                variantes[origen] = destino

    return variantes


def reparar_cortes_de_linea(texto: str) -> str:
    """
    Une palabras partidas mediante guion al final de línea.

    No modifica guiones internos normales.
    """
    return re.sub(
        r"(?<=\w)-\s*\n\s*(?=\w)",
        "",
        texto,
    )


def aplicar_variantes(texto: str, variantes: dict[str, str]) -> str:
    for origen in sorted(variantes, key=len, reverse=True):
        destino = variantes[origen]
        patron = re.compile(
            rf"(?<!\w){re.escape(origen)}(?!\w)",
            flags=re.IGNORECASE,
        )
        texto = patron.sub(destino, texto)
    return texto


def construir_stopwords(idiomas: list[str]) -> set[str]:
    if not idiomas:
        return set()

    if stopwords is None:
        raise RuntimeError(
            "Debe instalarse stopwordsiso para eliminar palabras vacías"
        )

    resultado: set[str] = set()
    for idioma in idiomas:
        resultado.update(palabra.lower() for palabra in stopwords(idioma))
    return resultado


def eliminar_stopwords_de_texto(
    texto: str,
    palabras_vacias: set[str],
) -> str:
    if not palabras_vacias:
        return texto

    def reemplazo(coincidencia: re.Match[str]) -> str:
        token = coincidencia.group(0)
        return "" if token.lower() in palabras_vacias else token

    return PATRON_TOKEN.sub(reemplazo, texto)


def normalizar_texto(
    texto: str,
    variantes: dict[str, str],
    eliminar_correos: bool,
    eliminar_numeros: bool,
    palabras_vacias: set[str],
) -> str:
    texto = unicodedata.normalize("NFKC", texto)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = PATRON_CONTROL.sub(" ", texto)
    texto = reparar_cortes_de_linea(texto)

    texto = PATRON_URL.sub(" ", texto)
    texto = PATRON_DOI.sub(" ", texto)

    if eliminar_correos:
        texto = PATRON_CORREO.sub(" ", texto)

    if eliminar_numeros:
        texto = PATRON_NUMERO_AISLADO.sub(" ", texto)

    texto = aplicar_variantes(texto, variantes)
    texto = eliminar_stopwords_de_texto(texto, palabras_vacias)

    lineas = []
    for linea in texto.splitlines():
        linea = PATRON_ESPACIOS.sub(" ", linea).strip()
        lineas.append(linea)

    texto = "\n".join(lineas)
    texto = PATRON_LINEAS.sub("\n\n", texto)
    return texto.strip()


def guardar_texto(destino: Path, texto: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8", newline="\n")


def procesar(
    carpeta_entrada: Path,
    carpeta_salida: Path,
    registro_csv: Path,
    variantes: dict[str, str],
    eliminar_correos: bool,
    eliminar_numeros: bool,
    palabras_vacias: set[str],
) -> int:
    archivos = list(descubrir_txt(carpeta_entrada))
    if not archivos:
        logging.error("No se encontraron archivos TXT")
        return 1

    registro_csv.parent.mkdir(parents=True, exist_ok=True)
    filas = []
    errores = 0

    for indice, archivo in enumerate(archivos, start=1):
        relativo = archivo.relative_to(carpeta_entrada)
        destino = carpeta_salida / relativo
        estado = "correcto"
        observaciones = ""

        try:
            original = archivo.read_text(encoding="utf-8")
            normalizado = normalizar_texto(
                original,
                variantes,
                eliminar_correos,
                eliminar_numeros,
                palabras_vacias,
            )
            guardar_texto(destino, normalizado)

            filas.append(
                {
                    "archivo": str(relativo),
                    "caracteres_originales": len(original),
                    "caracteres_normalizados": len(normalizado),
                    "reduccion_caracteres": len(original) - len(normalizado),
                    "estado": estado,
                    "observaciones": observaciones,
                }
            )
            logging.info(
                "[%s/%s] %s",
                indice,
                len(archivos),
                relativo,
            )
        except Exception as exc:
            errores += 1
            estado = "error"
            observaciones = str(exc)
            logging.exception("Error al normalizar %s", archivo)
            filas.append(
                {
                    "archivo": str(relativo),
                    "caracteres_originales": "",
                    "caracteres_normalizados": "",
                    "reduccion_caracteres": "",
                    "estado": estado,
                    "observaciones": observaciones,
                }
            )

    with registro_csv.open("w", encoding="utf-8", newline="") as manejador:
        campos = [
            "archivo",
            "caracteres_originales",
            "caracteres_normalizados",
            "reduccion_caracteres",
            "estado",
            "observaciones",
        ]
        escritor = csv.DictWriter(manejador, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)

    logging.info(
        "Normalización finalizada | archivos %s | errores %s",
        len(filas),
        errores,
    )
    return 1 if errores else 0


def analizar_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(
        description="Normaliza textos para su análisis con IRaMuTeQ."
    )
    analizador.add_argument("--entrada", type=Path, required=True)
    analizador.add_argument("--salida", type=Path, required=True)
    analizador.add_argument(
        "--registro",
        type=Path,
        default=Path("registro_normalizacion.csv"),
    )
    analizador.add_argument(
        "--variantes",
        type=Path,
        default=None,
        help="CSV opcional con variante y forma_unificada.",
    )
    analizador.add_argument(
        "--eliminar-correos",
        action="store_true",
    )
    analizador.add_argument(
        "--conservar-numeros",
        action="store_true",
        help="Conserva números aislados. Por defecto se eliminan.",
    )
    analizador.add_argument(
        "--eliminar-stopwords",
        action="store_true",
        help="Elimina palabras vacías en es, pt y en.",
    )
    analizador.add_argument(
        "--idiomas-stopwords",
        nargs="+",
        default=["es", "pt", "en"],
    )
    analizador.add_argument("--verbose", action="store_true")
    return analizador.parse_args()


def main() -> int:
    argumentos = analizar_argumentos()
    configurar_registro(argumentos.verbose)

    if not argumentos.entrada.exists():
        logging.error("La carpeta de entrada no existe")
        return 2

    variantes = cargar_variantes(argumentos.variantes)
    palabras_vacias = (
        construir_stopwords(argumentos.idiomas_stopwords)
        if argumentos.eliminar_stopwords
        else set()
    )

    return procesar(
        argumentos.entrada.resolve(),
        argumentos.salida.resolve(),
        argumentos.registro.resolve(),
        variantes,
        argumentos.eliminar_correos,
        not argumentos.conservar_numeros,
        palabras_vacias,
    )


if __name__ == "__main__":
    raise SystemExit(main())
