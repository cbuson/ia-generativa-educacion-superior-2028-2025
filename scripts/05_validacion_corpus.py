#!/usr/bin/env python3
"""
Valida la integridad documental del corpus preparado para IRaMuTeQ.

El script verifica
    Codificación UTF-8
    Número de cabeceras
    Identificadores duplicados
    Cabeceras mal formadas
    Documentos vacíos
    Coincidencia básica con los metadatos
    Huella SHA-256 del corpus

Importante
    Las cifras de ocurrencias, formas, lemas, segmentos y cobertura de la CHD
    deben verificarse con las salidas originales de IRaMuTeQ. El conteo local
    de tokens incluido aquí es únicamente diagnóstico y no sustituye las
    estadísticas del software.

Uso
    python 05_validacion_corpus.py \
        --corpus ../corpus/corpus_iramuteq.txt \
        --metadatos ../datos/metadatos_corpus.csv \
        --informe-json ../registros/validacion.json \
        --esperados 171
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any


PATRON_CABECERA = re.compile(r"(?m)^\*\*\*\*\s+(.+)$")
PATRON_ID = re.compile(r"(?:^|\s)\*id_([a-z0-9_]+)(?:\s|$)")
PATRON_TOKEN = re.compile(r"\b[\wáéíóúüñç]+\b", re.IGNORECASE)


def configurar_registro(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def sha256_archivo(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as manejador:
        for bloque in iter(lambda: manejador.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def leer_ids_metadatos(ruta: Path) -> list[str]:
    with ruta.open("r", encoding="utf-8-sig", newline="") as manejador:
        lector = csv.DictReader(manejador)
        if not lector.fieldnames or "id_documento" not in lector.fieldnames:
            raise ValueError(
                "Los metadatos deben contener id_documento"
            )
        return [
            (fila.get("id_documento") or "").strip().lower()
            for fila in lector
            if (fila.get("id_documento") or "").strip()
        ]


def separar_documentos(texto: str) -> list[tuple[str, str]]:
    coincidencias = list(PATRON_CABECERA.finditer(texto))
    documentos = []

    for indice, coincidencia in enumerate(coincidencias):
        inicio_texto = coincidencia.end()
        fin_texto = (
            coincidencias[indice + 1].start()
            if indice + 1 < len(coincidencias)
            else len(texto)
        )
        cabecera = coincidencia.group(1).strip()
        cuerpo = texto[inicio_texto:fin_texto].strip()
        documentos.append((cabecera, cuerpo))

    return documentos


def normalizar_id_metadato(valor: str) -> str:
    valor = valor.lower().strip()
    valor = re.sub(r"[^a-z0-9_]+", "_", valor)
    return re.sub(r"_+", "_", valor).strip("_")


def validar(
    corpus: Path,
    metadatos: Path | None,
    esperados: int | None,
) -> dict[str, Any]:
    texto = corpus.read_text(encoding="utf-8")
    documentos = separar_documentos(texto)

    cabeceras_invalidas = []
    documentos_vacios = []
    ids = []

    for numero, (cabecera, cuerpo) in enumerate(documentos, start=1):
        coincidencia_id = PATRON_ID.search(" " + cabecera + " ")
        if not coincidencia_id:
            cabeceras_invalidas.append(numero)
            continue

        identificador = coincidencia_id.group(1)
        ids.append(identificador)

        if not cuerpo:
            documentos_vacios.append(identificador)

    conteo_ids = Counter(ids)
    ids_duplicados = sorted(
        identificador
        for identificador, cantidad in conteo_ids.items()
        if cantidad > 1
    )

    tokens = PATRON_TOKEN.findall(texto)
    formas_diagnosticas = {
        token.lower()
        for token in tokens
        if not token.startswith("id_")
    }

    informe: dict[str, Any] = {
        "archivo_corpus": str(corpus),
        "sha256": sha256_archivo(corpus),
        "bytes": corpus.stat().st_size,
        "documentos_detectados": len(documentos),
        "ids_detectados": len(ids),
        "ids_duplicados": ids_duplicados,
        "cabeceras_invalidas": cabeceras_invalidas,
        "documentos_vacios": documentos_vacios,
        "tokens_diagnosticos": len(tokens),
        "formas_diagnosticas": len(formas_diagnosticas),
        "advertencia_estadisticas": (
            "Los tokens y formas diagnósticos no equivalen a las "
            "ocurrencias, formas, lemas o segmentos calculados por IRaMuTeQ."
        ),
        "validacion_correcta": True,
        "errores": [],
        "advertencias": [],
    }

    if esperados is not None and len(documentos) != esperados:
        informe["errores"].append(
            f"Se esperaban {esperados} documentos y se detectaron "
            f"{len(documentos)}"
        )

    if ids_duplicados:
        informe["errores"].append(
            "Existen identificadores duplicados"
        )

    if cabeceras_invalidas:
        informe["errores"].append(
            "Existen cabeceras sin identificador válido"
        )

    if documentos_vacios:
        informe["errores"].append(
            "Existen documentos sin contenido"
        )

    if metadatos is not None:
        ids_metadatos = {
            normalizar_id_metadato(valor)
            for valor in leer_ids_metadatos(metadatos)
        }
        ids_corpus = set(ids)

        informe["ids_solo_en_metadatos"] = sorted(
            ids_metadatos - ids_corpus
        )
        informe["ids_solo_en_corpus"] = sorted(
            ids_corpus - ids_metadatos
        )

        if informe["ids_solo_en_metadatos"]:
            informe["errores"].append(
                "Hay identificadores presentes en metadatos "
                "pero ausentes en el corpus"
            )

        if informe["ids_solo_en_corpus"]:
            informe["errores"].append(
                "Hay identificadores presentes en el corpus "
                "pero ausentes en metadatos"
            )

    informe["validacion_correcta"] = not informe["errores"]
    return informe


def analizar_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(
        description="Valida un corpus preparado para IRaMuTeQ."
    )
    analizador.add_argument("--corpus", type=Path, required=True)
    analizador.add_argument("--metadatos", type=Path, default=None)
    analizador.add_argument(
        "--informe-json",
        type=Path,
        required=True,
    )
    analizador.add_argument(
        "--esperados",
        type=int,
        default=None,
        help="Número esperado de documentos.",
    )
    analizador.add_argument("--verbose", action="store_true")
    return analizador.parse_args()


def main() -> int:
    argumentos = analizar_argumentos()
    configurar_registro(argumentos.verbose)

    if not argumentos.corpus.exists():
        logging.error("El archivo de corpus no existe")
        return 2

    if argumentos.metadatos and not argumentos.metadatos.exists():
        logging.error("El archivo de metadatos no existe")
        return 2

    informe = validar(
        argumentos.corpus.resolve(),
        argumentos.metadatos.resolve()
        if argumentos.metadatos else None,
        argumentos.esperados,
    )

    argumentos.informe_json.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    argumentos.informe_json.write_text(
        json.dumps(informe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(informe, ensure_ascii=False, indent=2))
    return 0 if informe["validacion_correcta"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
