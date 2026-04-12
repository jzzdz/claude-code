"""
wiki_retriever.py — Recuperación de contexto de la wiki siguiendo el paradigma LLM Wiki de Karpathy.

Flujo de dos fases para minimizar tokens:
    Fase 1 (Discovery): LLM recibe solo el índice + query → devuelve slugs relevantes
    Fase 2 (Answer):    Se cargan solo esos archivos y se construye el contexto final
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage


# ──────────────────────────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────────────────────────

# Número máximo de páginas a cargar para no desbordar el contexto
MAX_PAGINAS = 4

# Prompt para la fase de descubrimiento
_DISCOVERY_SYSTEM = """Eres un selector de documentación. Tu única tarea es identificar qué páginas de una wiki son relevantes para responder la consulta del usuario.

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con una lista de slugs separados por comas (los identificadores entre [[ ]] del índice).
2. Devuelve como máximo 4 slugs, ordenados por relevancia.
3. Si ninguna página es relevante, responde con la palabra: NINGUNA
4. NO añadas explicaciones, texto extra ni puntuación adicional.

Ejemplo de respuesta válida: llms-como-funcionan, redes-neuronales, ml-overview"""


# ──────────────────────────────────────────────────────────────────────────────
# Funciones de recuperación
# ──────────────────────────────────────────────────────────────────────────────

def cargar_indice(wiki_path: str) -> str:
    """Lee el archivo index.md de la wiki y devuelve su contenido."""
    ruta = Path(wiki_path) / "index.md"
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el índice en: {ruta}")
    return ruta.read_text(encoding="utf-8")


def identificar_paginas_relevantes(
    llm,
    indice: str,
    query: str,
) -> list[str]:
    """
    Fase 1 — Discovery.

    Envía el índice + la consulta al LLM para que identifique
    los slugs de las páginas más relevantes.

    Devuelve una lista de slugs (puede estar vacía si no hay relevancia).
    """
    prompt = f"""# Índice de la wiki

{indice}

# Consulta del usuario

{query}"""

    mensajes = [
        SystemMessage(content=_DISCOVERY_SYSTEM),
        HumanMessage(content=prompt),
    ]

    respuesta = llm.invoke(mensajes)
    texto = respuesta.content.strip()

    # Extraer tokens de uso para métricas
    tokens_discovery = None
    u = respuesta.usage_metadata
    if u:
        tokens_discovery = {
            "input":  u.get("input_tokens", 0),
            "output": u.get("output_tokens", 0),
            "total":  u.get("total_tokens", 0),
        }

    # Parsear slugs de la respuesta
    if not texto or texto.upper() == "NINGUNA":
        return [], tokens_discovery

    # Extraer solo los slugs válidos (alfanuméricos con guiones)
    slugs_raw = [s.strip() for s in texto.split(",")]
    slugs = [s for s in slugs_raw if re.match(r'^[a-zA-Z0-9\-]+$', s)][:MAX_PAGINAS]

    return slugs, tokens_discovery


def cargar_paginas(wiki_path: str, slugs: list[str]) -> tuple[str, list[str]]:
    """
    Carga el contenido de los archivos de la wiki correspondientes a los slugs.

    Devuelve una tupla (texto_concatenado, lista_de_slugs_encontrados).
    Solo carga los archivos que existen; ignora los que no existen.
    """
    wiki = Path(wiki_path)
    partes = []
    slugs_cargados = []

    for slug in slugs:
        ruta = wiki / f"{slug}.md"
        if ruta.exists():
            contenido = ruta.read_text(encoding="utf-8")
            partes.append(f"## [{slug}]\n\n{contenido}")
            slugs_cargados.append(slug)

    texto = "\n\n---\n\n".join(partes)
    return texto, slugs_cargados


def construir_contexto_wiki(paginas_texto: str) -> str:
    """
    Formatea el contexto de la wiki para inyectarlo en el system prompt.
    """
    if not paginas_texto.strip():
        return ""

    return f"""# Contexto extraído de la wiki personal

A continuación tienes información relevante de la wiki del usuario.
Úsala como base para responder. Si la información de la wiki contradice tu conocimiento general,
prioriza la wiki (es conocimiento específico del usuario).

{paginas_texto}

---
"""


# ──────────────────────────────────────────────────────────────────────────────
# Función principal orquestadora
# ──────────────────────────────────────────────────────────────────────────────

def recuperar_contexto_wiki(
    llm,
    wiki_path: str,
    query: str,
) -> dict:
    """
    Orquesta las dos fases de recuperación.

    Devuelve un diccionario con:
        - contexto_str:     texto listo para inyectar en el prompt
        - slugs_usados:     lista de slugs cargados
        - tokens_discovery: dict con tokens de la Fase 1
        - error:            mensaje de error si algo falló (o None)
    """
    resultado = {
        "contexto_str":     "",
        "slugs_usados":     [],
        "tokens_discovery": None,
        "error":            None,
    }

    try:
        # Fase 1 — Cargar índice e identificar páginas relevantes
        indice = cargar_indice(wiki_path)
        slugs, tokens_discovery = identificar_paginas_relevantes(llm, indice, query)
        resultado["tokens_discovery"] = tokens_discovery

        if not slugs:
            # Sin páginas relevantes: responder sin contexto de wiki
            return resultado

        # Fase 2 — Cargar páginas seleccionadas
        paginas_texto, slugs_cargados = cargar_paginas(wiki_path, slugs)
        resultado["slugs_usados"] = slugs_cargados

        # Construir contexto final
        resultado["contexto_str"] = construir_contexto_wiki(paginas_texto)

    except Exception as e:
        resultado["error"] = str(e)

    return resultado
