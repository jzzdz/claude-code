"""
herbie_app.py — Chatbot Herbie con Streamlit
Ejecutar: streamlit run herbie_app.py
"""
import math

import streamlit as st

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from typing import Any, List, Optional

# importo la función para obtener el adaptador del LLM en función del provider
from herbie_llm import get_llm

# importo el recuperador de contexto de la wiki (modo Cerebro)
from wiki_retriever import recuperar_contexto_wiki

# ────────────────────────────────────────────────────────────────────────────
# region Configuración
# ────────────────────────────────────────────────────────────────────────────

# Ruta raíz de la wiki personal (modo Cerebro)
WIKI_PATH = "/Users/javierzazo/Library/CloudStorage/GoogleDrive-javizzdz76@gmail.com/Mi unidad/context/ProyectoCerebro/wiki"

# endregion

# ────────────────────────────────────────────────────────────────────────────
# region Helper cálculo métricas
# ────────────────────────────────────────────────────────────────────────────

# Calcular la perplejidad

def _calcular_perplejidad(msg) -> float | None:
    """Calcula la perplejidad a partir de los logprobs del mensaje (solo Ollama).
    Perplejidad = exp(-media(logprobs)) → cuanto más baja, más seguro está el modelo.

    Ollama en modo no-streaming devuelve logprobs como lista directa:
        response_metadata["logprobs"] = [{"token": "¡", "logprob": -1.46, ...}, ...]
    """
    logprobs_raw = (msg.response_metadata or {}).get("logprobs")
    if not logprobs_raw:
        return None
    # No-streaming → lista directa; streaming acumulado → {"content": [...]}
    tokens = logprobs_raw if isinstance(logprobs_raw, list) else logprobs_raw.get("content", [])
    if not tokens:
        return None
    avg_logprob = sum(t["logprob"] for t in tokens) / len(tokens)
    return round(math.exp(-avg_logprob), 2)

# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Helper del modo Chat
# ────────────────────────────────────────────────────────────────────────────

def _chat(
    llm,
    history: List[BaseMessage],
    user_input: str,
    system_prompt: str = "Eres Herbie, un asistente amigable y útil.",
) -> tuple[str, List[BaseMessage]]:

    """
    Envía un mensaje al LLM manteniendo el historial.

    Devuelve (respuesta_str, historial_actualizado).

    Clases de langchain usadas:
        - SystemMessage("Eres un asistente útil") = instrucciones generales para el LLM
        - HumanMessage("Hola") = Mensaje del usuario al LLM
        - AIMessage = Respuesta del LLM al usuarios
    """

    # Si NO hay conversación previa, inicializa el historial con el system prompt
    if not history:
        history = [SystemMessage(content=system_prompt)]

    # Añadir el mensaje del usuario al historial
    history.append(HumanMessage(content=user_input))

    # Llamada al LLM a través del interfaz de LangChain
    # invoke es el método que se encarga de llamar al LLM
    response: AIMessage = llm.invoke(history)

    # Actualizar historial
    history.append(response)

    return response.content, history
# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Helper del modo Cerebro
# ────────────────────────────────────────────────────────────────────────────

def _chat_cerebro(
    llm,
    history: List[BaseMessage],
    user_input: str,
    system_prompt: str,
    wiki_path: str,
) -> tuple[str, List[BaseMessage], dict]:
    """
    Modo Cerebro: antes de llamar al LLM, recupera contexto relevante de la wiki
    usando el paradigma de dos fases de Karpathy:
        Fase 1 — Discovery: el LLM identifica qué páginas de la wiki son relevantes.
        Fase 2 — Answer:    se inyectan solo esas páginas como contexto.

    Devuelve (respuesta_str, historial_actualizado, cerebro_meta).
    cerebro_meta contiene métricas de la recuperación para mostrar en la UI.
    """
    
    # ── Fase 1: recuperar contexto relevante de la wiki ──────────────────────
    wiki_result = recuperar_contexto_wiki(llm, wiki_path, user_input)

    # ── Construir system prompt enriquecido con el contexto de la wiki ────────
    contexto_wiki = wiki_result["contexto_str"]
    system_enriquecido = (contexto_wiki + system_prompt) if contexto_wiki else system_prompt

    # ── Fase 2: llamar al LLM con el contexto inyectado ──────────────────────
    if not history:
        history = [SystemMessage(content=system_enriquecido)]
    else:
        # Actualizar el SystemMessage inicial con el nuevo contexto
        history[0] = SystemMessage(content=system_enriquecido)

    history.append(HumanMessage(content=user_input))

    # Envío la pregunta al LLM
    response: AIMessage = llm.invoke(history)
    
    history.append(response)

    # ── Métricas de la llamada de respuesta ──────────────────────────────────
    u = response.usage_metadata or {}
    cerebro_meta = {
        "slugs_usados":      wiki_result["slugs_usados"],
        "tokens_discovery":  wiki_result["tokens_discovery"],
        "tokens_answer": {
            "input":  u.get("input_tokens", 0),
            "output": u.get("output_tokens", 0),
            "total":  u.get("total_tokens", 0),
        },
        "error": wiki_result["error"],
    }

    return response.content, history, cerebro_meta

# endregion

# ────────────────────────────────────────────────────────────────────────────
# region Helper del modo Agente
# ────────────────────────────────────────────────────────────────────────────

def _chat_agente(agent, user_input: str) -> tuple[str, dict]:
    """
    Invoca el agente de LangChain y devuelve (respuesta_str, agent_steps).

    agent_steps es un dict con:
        - tools_usadas:          lista de tool_calls detectados en los AIMessages
        - intermediate_messages: mensajes intermedios (sin el HumanMessage inicial ni el final)
        - all_messages:          todos los mensajes para debug
        - usage:                 metadatos de tokens del último mensaje
        - timing:                response_metadata del último mensaje (tiempos Ollama)
        - perplexidad:           perplejidad calculada a partir de logprobs (solo Ollama)
    """
    # Invoca al agente; result["messages"] contiene toda la traza de la conversación
    result = agent.invoke({"messages": [HumanMessage(content=user_input)]})

    # Último mensaje = respuesta final del agente
    ultimo_msg = result["messages"][-1]

    # Detectar todas las tools que el agente decidió invocar
    tools_usadas = [
        tc
        for msg in result["messages"]
        if isinstance(msg, AIMessage)
        for tc in (msg.tool_calls or [])
    ]

    # Métricas de tokens y tiempos
    u = ultimo_msg.usage_metadata or {}
    perplexidad = _calcular_perplejidad(ultimo_msg)

    agent_steps = {
        "tools_usadas":          tools_usadas,
        "intermediate_messages": result["messages"][1:-1],
        "all_messages":          result["messages"],
        "usage":                 u,
        "timing":                ultimo_msg.response_metadata,
        "perplexidad":           perplexidad,
    }

    return ultimo_msg.content, agent_steps


    # region Pintar los pasos y la respuesta del agente

def _render_agent_steps(agent_steps: dict) -> None:
    """Pinta el expander de tools + pasos a partir de los datos guardados en display."""

    tools_usadas = agent_steps["tools_usadas"]

    if not tools_usadas:
        return

    with st.expander(f"🔧 Tools usadas ({len(tools_usadas)}) · pasos del agente"):

        for msg in agent_steps["intermediate_messages"]:
            if isinstance(msg, AIMessage):
                if msg.content:
                    st.markdown("**💭 Pensamiento:**")
                    st.markdown(msg.content)
                for tc in (msg.tool_calls or []):
                    st.markdown(f"**⚡ Acción:** llama a `{tc['name']}`")
                    st.json(tc["args"])
            elif isinstance(msg, ToolMessage):
                st.markdown(f"**👁️ Observación** (resultado de `{msg.name}`):")
                st.markdown(msg.content)
            st.divider()

        # ── Resultado raw completo ───────────────────────────────────────────────
        if agent_steps.get("all_messages"):
            st.divider()
            st.markdown("**🔍 Resultado completo (debug)**")
            for i, msg in enumerate(agent_steps["all_messages"]):
                tipo = type(msg).__name__
                with st.expander(f"`[{i}]` {tipo}"):
                    st.json(msg.model_dump())

        st.divider()

        # Métricas
        st.markdown("**📊 Métricas**")
        col1, col2, col3 = st.columns(3)
        with col1:
            u = agent_steps.get("usage")
            if u:
                st.markdown("**Tokens**")
                st.table({
                    "Input":  [u.get("input_tokens", "-")],
                    "Output": [u.get("output_tokens", "-")],
                    "Total":  [u.get("total_tokens", "-")],
                })
        with col2:
            meta = agent_steps.get("timing", {})
            if any(k in meta for k in ("total_duration", "eval_duration")):
                st.markdown("**Tiempos (ms)**")
                st.table({
                    "Total":             [round(meta.get("total_duration", 0) / 1e6, 1)],
                    "Carga modelo":      [round(meta.get("load_duration", 0) / 1e6, 1)],
                    "Procesar input":    [round(meta.get("prompt_eval_duration", 0) / 1e6, 1)],
                    "Generar respuesta": [round(meta.get("eval_duration", 0) / 1e6, 1)],
                })
        with col3:
            p = agent_steps.get("perplexidad")
            if p is not None:
                st.markdown("**Perplejidad**")
                nivel = "🟢 Seguro" if p < 5 else ("🟡 Normal" if p < 20 else "🔴 Dudando")
                st.metric("", p)
                st.caption(nivel)
    # endregion 


    # ────────────────────────────────────────────────────────────────────────────
    # region Tools del modo agente
    # ────────────────────────────────────────────────────────────────────────────

    #
    #Crea funciones de langchain, internamente langchain usa function calling y convierte las funciones en algo así:
    #{
    #  "tool": "get_weather",
    #  "args": {"city": "Madrid"}
    #}


@tool("contar_letras")
def _contar_letras(palabra: str) -> str:
    """Usa esta función solamente, SIEMPRE que el usuario pregunte por número de letras sin pedir que se cuenten las letras de una palabra específica."""
    total = len(palabra.replace(" ", ""))
    detalle = ", ".join(f"'{c}': {palabra.count(c)}" for c in sorted(set(palabra)) if c != " ")
    return f"'{palabra}' tiene {total} letras. Desglose: {detalle}."

@tool("contar_letra_en_palabra")
def _contar_letra_en_palabra(letra: str, palabra: str) -> str:
    """Usa esta función solamente, SIEMPRE que el usuario pregunte cuántas veces aparece una letra concreta en una palabra."""
    letra = letra.lower()
    palabra_lower = palabra.lower()
    count = palabra_lower.count(letra)
    if count == 0:
        return f"La letra '{letra}' no aparece en '{palabra}'."
    posiciones = [i for i, c in enumerate(palabra_lower) if c == letra]
    return f"La letra '{letra}' aparece {count} vez/veces en '{palabra}'. Posiciones: {posiciones}."

@tool("buscar_noticias")
def _buscar_noticias(query: str) -> str:
    """Busca noticias recientes sobre un tema usando el RSS público de Google News. Úsala SIEMPRE que el usuario pregunte por noticias, actualidad o eventos recientes."""
    import httpx
    import xml.etree.ElementTree as ET

    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=es&gl=ES&ceid=ES:es"
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:5]
        if not items:
            return f"No se encontraron noticias sobre '{query}'."
        return "\n\n".join(
            f"- **{item.find('title').text}**\n  {item.find('pubDate').text}"
            for item in items
        )
    except Exception as e:
        return f"Error al buscar noticias sobre '{query}': {e}"

@tool("obtener_tiempo_ciudad")
def _obtener_tiempo_ciudad(ciudad: str) -> str:
    """Obtiene el tiempo actual de una ciudad por su nombre. Úsala SIEMPRE que el usuario pregunte por el tiempo, clima o meteorología de cualquier lugar."""
    import httpx

    try:
        # 1. Geocodificar ciudad → coordenadas
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ciudad, "count": 1, "language": "es"},
            timeout=10,
        ).json()
        if not geo.get("results"):
            return f"No se encontró la ciudad '{ciudad}'."
        loc = geo["results"][0]
        lat = float(loc["latitude"])
        lon = float(loc["longitude"])

        # 2. Obtener tiempo actual con coordenadas numéricas
        w = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
            },
            timeout=10,
        ).json()
        c = w["current"]
        return (
            f"Tiempo en {loc['name']} ({loc.get('country', '')}):\n"
            f"- Temperatura: {c['temperature_2m']}°C\n"
            f"- Humedad: {c['relative_humidity_2m']}%\n"
            f"- Viento: {c['wind_speed_10m']} km/h\n"
            f"- Precipitación: {c['precipitation']} mm"
        )
    except Exception as e:
        return f"Error al obtener el tiempo para '{ciudad}': {e}"

@tool("fetch_url")
def _fetch_url(url: str) -> str:
    """Descarga el contenido de una URL y lo devuelve en texto plano.
    Úsala SIEMPRE que el usuario pida leer, resumir o extraer información de una página web o enlace."""
    import httpx
    from html.parser import HTMLParser

    class _StripHTML(HTMLParser):
        """Parser mínimo que extrae solo el texto visible de un HTML."""
        def __init__(self):
            super().__init__()
            self._parts: list[str] = []
            self._skip_tags = {"script", "style", "head", "noscript"}
            self._current_skip = 0

        def handle_starttag(self, tag, attrs):
            if tag in self._skip_tags:
                self._current_skip += 1

        def handle_endtag(self, tag):
            if tag in self._skip_tags:
                self._current_skip = max(0, self._current_skip - 1)

        def handle_data(self, data):
            if self._current_skip == 0 and data.strip():
                self._parts.append(data.strip())

        def get_text(self) -> str:
            return "\n".join(self._parts)

    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        parser = _StripHTML()
        parser.feed(resp.text)
        text = parser.get_text()
        return text[:6000] + ("…[recortado]" if len(text) > 6000 else "")
    except Exception as e:
        return f"Error al descargar '{url}': {e}"

# ── Grupos de tools estáticas (disponibles siempre) ─────────────────────────
TOOLS_TEXTO    = [_contar_letras, _contar_letra_en_palabra]
TOOLS_NOTICIAS = [_buscar_noticias]
TOOLS_TIEMPO   = [_obtener_tiempo_ciudad]
TOOLS_WEB      = [_fetch_url]


def _get_all_tools() -> list:
    """Devuelve todas las tools disponibles para el agente."""
    return TOOLS_TEXTO + TOOLS_NOTICIAS + TOOLS_TIEMPO + TOOLS_WEB

    # endregion 
# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Configuración de la página
# ────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Herbie", page_icon="🤖", layout="wide")

# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Estado de sesión — inicializado ANTES del sidebar
# ────────────────────────────────────────────────────────────────────────────

if "history" not in st.session_state:               # historial de la conversación
    st.session_state.history: list = []
if "display" not in st.session_state:               # Historial que se muestra en pantalla
    # Cada entrada es un dict: {"role": str, "content": str, "agent_steps": dict|None}
    st.session_state.display: list = []
if "current_provider" not in st.session_state:      # Proveedor usado
    st.session_state.current_provider = None
if "current_kwargs" not in st.session_state:        # Argumentos del LLM
    st.session_state.current_kwargs = {}
if "current_modo" not in st.session_state:          # Modo agente o chat
    st.session_state.current_modo = None
if "llm" not in st.session_state:                   # LLM usado
    st.session_state.llm = None
if "agent" not in st.session_state:                 # Agente creado
    st.session_state.agent = None
if "tokens_input" not in st.session_state:          # Tokens
    st.session_state.tokens_input = 0
if "tokens_output" not in st.session_state:         # Tokens
    st.session_state.tokens_output = 0
if "tokens_total" not in st.session_state:          # Tokens
    st.session_state.tokens_total = 0
if "perplexidad" not in st.session_state:           # Perplejidad del último turno (solo Ollama)
    st.session_state.perplexidad = None
if "cerebro_meta" not in st.session_state:          # Metadatos del último turno en modo Cerebro
    st.session_state.cerebro_meta = None

# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Frame: Sidebar
# ────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Configuración")

    # Modelos que NO soportan function calling → no pueden usar modo agente
    PROVIDERS_SIN_TOOLS = {"deepseek"}

    # Selección de modelo LLM (va antes que modo para poder condicionar las opciones)
    provider = st.selectbox(
        "Modelo LLM",
        options=["ollama", "deepseek", "mistral", "qwen3", "gemma4", "huggingface", "gemini"],
        format_func=lambda p: {
            "ollama":       "🦙 Ollama — llama3.2:3b (local)",
            "deepseek":     "🦙 Ollama — deepseek-r1:8b (razonamiento)",
            "mistral":      "🦙 Ollama — mistral-small3.2 (local)",
            "qwen3":        "🦙 Ollama — Qwen3.14b-ollama (razonamiento + tools)",
            "gemma4":       "🦙 Ollama — gemma4 (local)",
            "huggingface":  "🤗 HuggingFace — Llama-3.2-3B (en memoria)",
            "gemini":       "✨ Gemini (API)",
        }[p],
    )

    # Selección del modo de interacción
    _modos_disponibles = ["chat"] if provider in PROVIDERS_SIN_TOOLS else ["chat", "agente", "cerebro"]
    modo = st.selectbox(
        "Modo de interacción",
        options=_modos_disponibles,
        format_func=lambda m: {"chat": "💬 Chat", "agente": "🤖 Agente", "cerebro": "🧠 Cerebro (wiki)"}[m],
    )
    if provider in PROVIDERS_SIN_TOOLS:
        st.caption("⚠️ Este modelo no soporta tools — solo modo Chat disponible.")

    # Información del modo Cerebro (la ruta se configura en la constante WIKI_PATH)
    if modo == "cerebro":
        st.caption("🧠 Modo Cerebro: recupera contexto de tu wiki antes de cada respuesta (paradigma Karpathy).")

    llm_kwargs: dict = {}

    if provider == "ollama":
        ollama_model = st.text_input("Nombre del modelo Ollama", value="llama3.2:3b")
        llm_kwargs = {"model": ollama_model}

    elif provider == "deepseek":
        deepseek_model = st.text_input("Nombre del modelo DeepSeek", value="deepseek-r1:8b")
        llm_kwargs = {"model": deepseek_model}
        st.info("Modelo de razonamiento: genera un bloque `<think>` antes de responder.")

    elif provider == "mistral":
        mistral_model = st.text_input("Nombre del modelo Mistral", value="mistral-small3.2")
        llm_kwargs = {"model": mistral_model}

    elif provider == "qwen3":
        qwen3_model = st.text_input("Nombre del modelo Qwen3", value="Qwen3.14b-ollama")
        llm_kwargs = {"model": qwen3_model}
        st.info("Razonamiento + tools: genera un bloque `<think>` y puede llamar a herramientas.")

    elif provider == "gemma4":
        gemma4_model = st.text_input("Nombre del modelo Gemma4", value="gemma4")
        llm_kwargs = {"model": gemma4_model}

    elif provider == "huggingface":
        hf_model = st.text_input(
            "Model ID de HuggingFace",
            value="meta-llama/Llama-3.2-3B-Instruct",
            help="Requiere `huggingface-cli login` si el modelo es gated.",
        )
        llm_kwargs = {"model_id": hf_model}
        st.info("El modelo se cargará en memoria la primera vez que envíes un mensaje.")

    elif provider == "gemini":
        gemini_key = st.text_input("API Key", value="AIzaSyCfJty50M3F-UB18o-AZscU-id5RsYQZZQ", type="password")
        gemini_model = st.text_input("Modelo", value="gemini-2.0-flash")
        llm_kwargs = {"api_key": gemini_key, "model": gemini_model}

    st.divider()

    # Establece prompt del sistema
    system_prompt = st.text_area(
        "System prompt",
        value="Eres Herbie, un asistente amigable y útil. Responde siempre en el mismo idioma que el usuario. No inventes información que no tengas certeza de su veracidad. Usa herramientas solo cuando sea necesario.",
        height=220,
    )

    # Botón de limpiar conversación
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.history = []
        st.session_state.display = []
        st.session_state.tokens_input = 0
        st.session_state.tokens_output = 0
        st.session_state.tokens_total = 0
        st.session_state.perplexidad = None
        st.rerun()

    st.divider()

    # Muestra estadísticas de tokens
    st.markdown("**📊 Tokens de la sesión**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Input",  st.session_state.tokens_input)
    col2.metric("Output", st.session_state.tokens_output)
    col3.metric("Total",  st.session_state.tokens_total)

    # Muestra perplejidad del último turno (solo disponible con Ollama)
    if st.session_state.perplexidad is not None:
        st.divider()
        p = st.session_state.perplexidad
        nivel = "🟢 Seguro" if p < 5 else ("🟡 Normal" if p < 20 else "🔴 Dudando")
        st.markdown("**🎲 Perplejidad (último turno)**")
        st.metric("", p, help="Solo disponible con Ollama. Mide la incertidumbre del modelo al generar la respuesta.\n< 5 seguro · 5–20 normal · > 20 dudando")
        st.caption(nivel)

    # Muestra mensaje
    st.divider()
    st.caption("Herbie usa LangChain internamente. El historial se mantiene en sesión.")

# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Frame: Cabecera
# ────────────────────────────────────────────────────────────────────────────

st.title("🤖 Herbie")
_PROVIDER_LABEL = {"ollama": "Ollama — llama3.2:3b", "deepseek": "Ollama — deepseek-r1:8b", "mistral": "Ollama — mistral-small3.2", "qwen3": "Ollama — Qwen3.14b-ollama", "gemma4": "Ollama — gemma4", "huggingface": "HuggingFace — Llama-3.2-3B", "gemini": "Gemini"}
_MODO_LABEL = {"chat": "💬 Chat", "agente": "🤖 Agente", "cerebro": "🧠 Cerebro (wiki)"}
st.caption(f"Modo: **{_MODO_LABEL.get(modo, modo)}** · Powered by **{_PROVIDER_LABEL.get(provider, provider)}** · LangChain")

# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Frame: Historial de chat — se repinta en cada rerun desde display
# ────────────────────────────────────────────────────────────────────────────

for entry in st.session_state.display:  # Recorre los mensajes guardados de la conversación

    with st.chat_message(entry["role"]):  # Bloque de chat para examinar el role ("user" o "assistant")

        # Muestra el contenido del mensaje
        st.markdown(entry["content"])

        # Muestra las tools usadas, pasos del agente, tokens y tiempos usados
        if entry.get("agent_steps"):
            _render_agent_steps(entry["agent_steps"])

        # Muestra las páginas de wiki consultadas (modo cerebro — historial)
        if entry.get("cerebro_meta"):
            _cm = entry["cerebro_meta"]
            slugs = _cm.get("slugs_usados", [])
            td = _cm.get("tokens_discovery") or {}
            ta = _cm.get("tokens_answer") or {}
            with st.expander(f"🧠 Wiki consultada · {len(slugs)} página(s)"):
                if _cm.get("error"):
                    st.warning(f"Error al acceder a la wiki: {_cm['error']}")
                if slugs:
                    st.markdown("**Páginas cargadas:**  " + "  ·  ".join(f"`{s}`" for s in slugs))
                else:
                    st.caption("No se encontraron páginas relevantes — respuesta sin contexto de wiki.")
                if td or ta:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Tokens Fase 1 (discovery)**")
                        st.table({"Input": [td.get("input", 0)], "Output": [td.get("output", 0)], "Total": [td.get("total", 0)]})
                    with col2:
                        st.markdown("**Tokens Fase 2 (respuesta)**")
                        st.table({"Input": [ta.get("input", 0)], "Output": [ta.get("output", 0)], "Total": [ta.get("total", 0)]})

# endregion 

# ────────────────────────────────────────────────────────────────────────────
# region Frame: Input del usuario
# ────────────────────────────────────────────────────────────────────────────

user_input = st.chat_input("Escribe tu mensaje...")

if user_input:

    # ── Validar config de Gemini ─────────────────────────────────────────────
    if provider == "gemini" and not llm_kwargs.get("api_key"):
        st.error("Introduce la API Key de Gemini en el panel lateral.")
        st.stop()

    # ── Cargar / refrescar LLM si cambió el proveedor, kwargs o modo ─────────
    config_changed = (
        st.session_state.current_provider != provider
        or st.session_state.current_kwargs != llm_kwargs
        or st.session_state.current_modo != modo
    )

    if config_changed or st.session_state.llm is None:
        with st.spinner("Cargando modelo..."):
            try:
                st.session_state.llm = get_llm(provider, **llm_kwargs)
                st.session_state.current_provider = provider
                st.session_state.current_kwargs = dict(llm_kwargs)
                st.session_state.current_modo = modo
                st.session_state.history = []
                st.session_state.display = []

                # Creo el agente (solo en modo agente)
                if modo == "agente":
                    st.session_state.agent = create_agent(
                        model=st.session_state.llm,
                        tools=_get_all_tools(),
                        system_prompt=system_prompt,
                    )
                else:
                    st.session_state.agent = None

            except Exception as e:
                st.error(f"Error al cargar el modelo: {e}")
                st.stop()

    
    # Mostramos la pregunta del usuario

    with st.chat_message("user"):
        st.markdown(user_input)

    # Abrimos la burbuja del asistente y lanzamos el LLM dentro del spinner.
    # El usuario verá: pregunta → "Pensando..." → respuesta, en ese orden.

    # Enviamos la pregunta al LLM (modo chat o agente) y mostramos la respuesta

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                if modo == "chat":

                    # Llamo a mi función chat que se encarga de llamar al LLM
                    response, st.session_state.history = _chat(
                        llm=st.session_state.llm,
                        history=st.session_state.history,
                        user_input=user_input,
                        system_prompt=system_prompt,
                    )

                    # Acumular tokens usados en la llamada al LLM
                    ultimo_chat_msg = st.session_state.history[-1]
                    u = ultimo_chat_msg.usage_metadata
                    if u:
                        st.session_state.tokens_input  += u.get("input_tokens", 0)
                        st.session_state.tokens_output += u.get("output_tokens", 0)
                        st.session_state.tokens_total  += u.get("total_tokens", 0)

                    # Calcular perplejidad del último mensaje (solo Ollama devuelve logprobs)
                    st.session_state.perplexidad = _calcular_perplejidad(ultimo_chat_msg)

                    agent_steps = None
                    st.session_state.cerebro_meta = None

                elif modo == "cerebro":

                    # Modo Cerebro: recuperación de wiki en dos fases (paradigma Karpathy)
                    # Fase 1 → el LLM lee el índice y elige páginas relevantes
                    # Fase 2 → se inyectan esas páginas como contexto antes de responder

                    response, st.session_state.history, cerebro_meta = _chat_cerebro(
                        llm=st.session_state.llm,
                        history=st.session_state.history,
                        user_input=user_input,
                        system_prompt=system_prompt,
                        wiki_path=WIKI_PATH,
                    )
                    st.session_state.cerebro_meta = cerebro_meta

                    # Acumular tokens de la fase de respuesta
                    ta = cerebro_meta["tokens_answer"]
                    st.session_state.tokens_input  += ta.get("input", 0)
                    st.session_state.tokens_output += ta.get("output", 0)
                    st.session_state.tokens_total  += ta.get("total", 0)

                    # Acumular también los tokens de discovery (Fase 1)
                    td = cerebro_meta.get("tokens_discovery") or {}
                    st.session_state.tokens_input  += td.get("input", 0)
                    st.session_state.tokens_output += td.get("output", 0)
                    st.session_state.tokens_total  += td.get("total", 0)

                    # Calcular perplejidad del último mensaje del historial
                    st.session_state.perplexidad = _calcular_perplejidad(st.session_state.history[-1])

                    agent_steps = None

                else:  # Modo agente

                    response, agent_steps = _chat_agente(st.session_state.agent, user_input)

                    # Acumular tokens usados en la llamada al LLM
                    u = agent_steps.get("usage") or {}
                    st.session_state.tokens_input  += u.get("input_tokens", 0)
                    st.session_state.tokens_output += u.get("output_tokens", 0)
                    st.session_state.tokens_total  += u.get("total_tokens", 0)

                    st.session_state.perplexidad = agent_steps.get("perplexidad")

            except Exception as e:
                st.error(f"Error al llamar al LLM: {e}")
                st.stop()


        # Muestra los pasos del agente (modo agente)
        if agent_steps:
            _render_agent_steps(agent_steps)

        # Muestra las páginas de wiki consultadas (modo cerebro)
        if modo == "cerebro" and st.session_state.cerebro_meta:
            _cm = st.session_state.cerebro_meta
            slugs = _cm.get("slugs_usados", [])
            td = _cm.get("tokens_discovery") or {}
            ta = _cm.get("tokens_answer") or {}
            with st.expander(f"🧠 Wiki consultada · {len(slugs)} página(s)"):
                if _cm.get("error"):
                    st.warning(f"Error al acceder a la wiki: {_cm['error']}")
                if slugs:
                    st.markdown("**Páginas cargadas:**  " + "  ·  ".join(f"`{s}`" for s in slugs))
                else:
                    st.caption("No se encontraron páginas relevantes — respuesta sin contexto de wiki.")
                if td or ta:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Tokens Fase 1 (discovery)**")
                        st.table({"Input": [td.get("input", 0)], "Output": [td.get("output", 0)], "Total": [td.get("total", 0)]})
                    with col2:
                        st.markdown("**Tokens Fase 2 (respuesta)**")
                        st.table({"Input": [ta.get("input", 0)], "Output": [ta.get("output", 0)], "Total": [ta.get("total", 0)]})

        # Muestra la respuesta
        st.markdown(response)

    # ── FASE 2: Persistencia ─────────────────────────────────────────────────
    # Guardamos ambos mensajes en display para que el historial sea correcto
    # en futuros reruns. El usuario ya ha visto todo en la Fase 1.

    st.session_state.display.append({"role": "user", "content": user_input, "agent_steps": None, "cerebro_meta": None})
    st.session_state.display.append({"role": "assistant", "content": response, "agent_steps": agent_steps, "cerebro_meta": st.session_state.cerebro_meta})

    # Rerun solo para actualizar los tokens del sidebar.
    # El chat ya es visible — el rerun no añade nada nuevo visualmente.
    st.rerun()

# endregion 

