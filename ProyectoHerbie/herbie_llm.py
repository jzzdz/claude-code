"""
herbie_llm.py — Módulo LangChain para el chatbot Herbie
Proveedores soportados:
  - ollama      → llama3.2:3b (local, requiere `ollama` corriendo)
  - huggingface → meta-llama/Llama-3.2-3B-Instruct (cargado en memoria)
  - gemini      → Gemini via langchain-google-genai (api_key + model)

Objetos de langchain:

    [ Agent ]  ← decide
    ↓
    [ Tools ]  ← ejecuta acciones
    ↓
    [ Chain ]  ← flujo fijo
    ↓
    [ LLM ]    ← responde
"""

from __future__ import annotations

import torch
from typing import Any

##########################################################################################
# Funciones generales
##########################################################################################


def _detect_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

##########################################################################################
# Funciones para acceder a los LLMs
##########################################################################################

# Funciones que devuelven adaptadores para los difernentes providers

# ────────────────────────────────────────────────────────────────────────────
# Crear adaptader para usar modelos HuggingFace (carga en memoria)
# ────────────────────────────────────────────────────────────────────────────

_hf_cache: dict = {}

def _get_huggingface_llm(model_id: str = "meta-llama/Llama-3.2-3B-Instruct"):
    """
    Carga el modelo de HuggingFace en memoria y devuelve un objeto ChatHuggingFace (adaptador de Langchain para usar LLMs de hugging face ).
    El modelo se cachea: sólo se carga una vez por sesión.
    Requiere: `huggingface-cli login` si el modelo es gated. Es decir si e
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

    # Evita recargar el modelo cada vez que se usa
    if model_id in _hf_cache:
        return _hf_cache[model_id]

    device = _detect_device()
    dtype = torch.float16 if device != "cpu" else torch.float32

    # Cargo el tokenizador en memoria
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Cargao el modelo en memoria
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)

    # Creo el motor de inferencia = modelo + tokenizador + parámetros de uso del modelo
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
        device=device,
    )

    # Convierte el modelo HF (model + tokenizer → pipeline) en un ChatModel de LangChain:
    # pipeline → HuggingFacePipeline (wrapper) → ChatHuggingFace

    # chat_model es un objeto de tipo BaseChatModel (adaptador listo para usar con .invoke y mensajes) en este caso para usar modelos de Huggingface
    chat_model = ChatHuggingFace(llm=HuggingFacePipeline(pipeline=pipe))


    # Cargo el modelo en mi caché
    _hf_cache[model_id] = chat_model

    return chat_model

# ────────────────────────────────────────────────────────────────────────────
# Crear adaptader para usar modelos HuggingFace desde ollama (carga en memoria)
# ────────────────────────────────────────────────────────────────────────────

def _get_ollama_llm(model: str = "llama3.2:3b"):
    """Devuelve un ChatOllamaWithLogprobs listo para usar con LangChain.

    langchain-ollama 1.0.1 usa streaming por defecto. En streaming, los
    logprobs vienen en cada chunk intermedio pero NO en el chunk final
    (done=True), que es el que LangChain guarda en generation_info/response_metadata.
    Solución: forzar stream=False → la respuesta única incluye todos los
    logprobs directamente en el json final que LangChain convierte a response_metadata.
    """
    from langchain_ollama import ChatOllama
    from typing import Any

    # La clase "ChatOllama" es una clase langchain para conectar  LangChain con modelos que corren en Ollama

    class ChatOllamaWithLogprobs(ChatOllama):
        """
        Crea una clase que hereda de "ChatOllama" para modificar parámetros log-probabilidades y stream
        """

        # Se sobrescribe (override) el método "_chat_params" cambiando los parámetros logprobs y stream para que conserve las log probabilidades

        def _chat_params(
            self,
            messages: list,
            stop: list | None = None,
            **kwargs: Any,
        ) -> dict:
            params = super()._chat_params(messages, stop=stop, **kwargs)
            params["logprobs"] = True   # Pedir logprobs a Ollama
            params["stream"]   = False  # No-streaming → logprobs en la respuesta final
            return params

    return ChatOllamaWithLogprobs(model=model, temperature=0.7)
    
# ────────────────────────────────────────────────────────────────────────────
# Crear adaptador para usar modelos Gemini (no carga en memoria, uso vía API)
# ────────────────────────────────────────────────────────────────────────────

def _get_gemini_llm(api_key: str, model: str = "gemini-2.0-flash"):

    """Devuelve un ChatGoogleGenerativeAI listo para usar con LangChain."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)


# ────────────────────────────────────────────────────────────────────────────
# Devover el adaptador de langchain creado en función del provider
# ────────────────────────────────────────────────────────────────────────────

def get_llm(provider: str, **kwargs):
    """
    Devuelve una clase ChatOllama de langchain para usar un LLM como un chat

    Parámetros
    ----------
    provider : "ollama" | "huggingface" | "gemini"
    kwargs   :
        ollama      → model="llama3.2:3b"
        huggingface → model_id="meta-llama/Llama-3.2-3B-Instruct"
        gemini      → api_key="...", model="gemini-2.0-flash"
    """
    if provider == "ollama":
        return _get_ollama_llm(kwargs.get("model", "llama3.2:3b"))
    if provider == "deepseek":
        return _get_ollama_llm(kwargs.get("model", "deepseek-r1:8b"))
    if provider == "mistral":
        return _get_ollama_llm(kwargs.get("model", "mistral-small3.2"))
    if provider == "qwen3":
        return _get_ollama_llm(kwargs.get("model", "Qwen3.14b-ollama"))
    if provider == "gemma4":
        return _get_ollama_llm(kwargs.get("model", "gemma4"))
    if provider == "huggingface":
        return _get_huggingface_llm(kwargs.get("model_id", "meta-llama/Llama-3.2-3B-Instruct"))
    if provider == "gemini":
        return _get_gemini_llm(kwargs["api_key"], kwargs.get("model", "gemini-2.0-flash"))

    raise ValueError(f"Provider desconocido: '{provider}'. Usa ollama, huggingface o gemini.")



