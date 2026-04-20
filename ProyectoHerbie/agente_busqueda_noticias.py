"""
agente_busqueda_noticias.py — Busca una empresa o cumple un objetivo en webs configuradas
Ejecutar: streamlit run agente_busqueda_noticias.py

Modos:
  1. Buscar texto    → búsqueda determinista de una empresa en el HTML
  2. Cumplir objetivo → loop agéntico: el LLM decide qué acciones Playwright ejecutar

Flujo común:
  1. Playwright renderiza cada URL (JS incluido)
  2. Se extrae el HTML y el texto visible completo

Flujo "Buscar texto":
  3. Búsqueda determinista: párrafos que contienen la empresa
  4. Se muestra el párrafo y el link más cercano

Flujo "Cumplir objetivo":
  3. El LLM recibe el texto de la página + links disponibles + objetivo
  4. El LLM decide la próxima acción (click, navegar, extraer, fin)
  5. Playwright ejecuta la acción
  6. Se repite hasta que el LLM devuelve "fin" o se alcanza el máximo de pasos
"""

import os
import re
import json
import sys
from urllib.parse import urljoin

import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

# Añadir el directorio del fichero al path para importar herbie_llm
sys.path.insert(0, os.path.dirname(__file__))
from herbie_llm import get_llm


# ─────────────────────────────────────────
#  region 1 - Configuración
# ─────────────────────────────────────────

#################################################################################
# region 1.1 - Constantes
#################################################################################


URLS_FILE       = os.path.join(os.path.dirname(__file__), "URLs.xlsx")
MIN_CHARS_PARRAFO = 10    # ignorar líneas muy cortas (menús, botones, etc.)
MAX_PASOS_AGENTE  = 10    # máximo de acciones que puede encadenar el agente

# endregion 1.1

#################################################################################
# region 1.2 - Prompts
#################################################################################

# Acciones disponibles que el LLM puede ordenar a Playwright
ACCIONES_DISPONIBLES = """
- click: hace click en el elemento cuyo texto visible coincide con "parametro"
- escribir: escribe el texto de "parametro" en el campo de búsqueda activo y pulsa Enter (usar para rellenar inputs y buscadores)
- navegar: navega a la URL indicada en "parametro"
- scroll: hace scroll hacia abajo para ver más contenido (ignorar "parametro")
- extraer: extrae el texto visible actual de la página como resultado final
- fin: termina el proceso sin extraer nada más
"""

# Prompt que recibe el LLM en cada iteración del loop agéntico
_PROMPT_AGENTE = """
Eres un agente que navega páginas web para cumplir un objetivo.
En cada paso recibes el estado actual de la página y decides la siguiente acción.

OBJETIVO: {objetivo}

URL ACTUAL: {url_actual}

LINKS DISPONIBLES EN LA PÁGINA (texto → url):
{links}

TEXTO VISIBLE DE LA PÁGINA (primeros 3000 caracteres):
{texto}

HISTORIAL DE ACCIONES YA EJECUTADAS:
{historial}

ACCIONES DISPONIBLES:
{acciones}

Responde ÚNICAMENTE con un JSON válido, sin markdown ni texto extra:
{{
  "razonamiento": "explica brevemente por qué eliges esta acción",
  "accion": "click" | "navegar" | "scroll" | "extraer" | "fin",
  "parametro": "texto del elemento a clickar, URL a navegar, o vacío si no aplica"
}}
"""
# endregion 1.2

# endregion 1


# ────────────────────────────────────────────────────────────────────────────
# region 2 - Helpers para navegar y acceder al HTML
# ────────────────────────────────────────────────────────────────────────────



#################################################################################
# region 2.1 - Buscar texto con beautifullsoup dentro de una página web
#################################################################################

def _buscar_texto_beautifulsoup(html: str, empresa: str, base_url: str) -> list[dict]:
    """
    Busca el texto en el HTML usando beautifylsoap y devuelve lista de:
      { "parrafo": str, "link": str | None }

    Para cada nodo de texto que contiene la empresa, sube por el DOM
    buscando el <a href> más cercano (hasta 8 niveles).
    """

    # Crea un objeto "soup" que representa el HTML parseado y estructurado .
    # BeautifulSoup es una clase de la librería BeautifulSoup Se usa para leer HTML como árbol
    soup = BeautifulSoup(html, "html.parser")

    # Limpiar HTML: Recorre el DOM eliminando del HTML el javascript, estitlos y metadatos
    for tag in soup(["script", "style", "noscript", "head"]):
        # Elimina completamente el elemento del árbol
        tag.decompose()

    # Paso a minúsculas la empresa a buscar
    empresa_lower = empresa.lower()

    # Inicializo la variable de resultados
    resultados: list[dict] = []

    # Inicializo la variable de vistos que sirve para evitar duplicados por texto
    vistos: set[str] = set()

    # Busca en el HTML nodos de texto (no etiquetas) que contengan el nombre de la empresa, sin importar mayúsculas/minúsculas, y devuelve esos nodos.
    # Devuelve en nodo objetos tipo objetos tipo NavigableString que son texto dentro del DOM
    # Es decir, Recorre todo el texto del HTML y devuelve los fragmentos donde aparece el nombre de la empresa, ignorando mayúsculas/minúscula

    for nodo in soup.find_all(string=re.compile(re.escape(empresa), re.IGNORECASE)):

        # Obtiene el texto del nodo
        parrafo = nodo.strip()

        # Valida la longitud del texto del nodo
        if len(parrafo) < MIN_CHARS_PARRAFO:
            continue
        if parrafo in vistos:
            continue
        vistos.add(parrafo)

        # Buscar el <a href> más cercano subiendo por el DOM
        link = None
        elemento = nodo.parent
        for _ in range(8):
            if elemento is None:
                break
            if elemento.name == "a" and elemento.get("href"):
                link = urljoin(base_url, elemento["href"])
                break
            # buscar <a> hijo directo
            a = elemento.find("a", href=True)
            if a:
                link = urljoin(base_url, a["href"])
                break
            elemento = elemento.parent

        # Devuelve el téxto del nodo y el link más cercano
        resultados.append({"parrafo": parrafo, "link": link})

    return resultados

# endregion 2.1

#################################################################################
# region 2.2 - Buscar texto con playwright dentro de una página web
#################################################################################

def _buscar_texto_playwright(empresa: str, base_url: str, page) -> list[dict]:
    """
    Busca el texto en la página usando Playwright y devuelve lista de:
      { "parrafo": str, "link": str | None }

    Usa page.locator para encontrar elementos que contienen la empresa
    y sube por el DOM con xpath para encontrar el <a href> más cercano.
    """

    # Inicializo la variable de resultados
    resultados: list[dict] = []

    # Inicializo la variable de vistos que sirve para evitar duplicados por texto
    vistos: set[str] = set()

    # Localiza todos los elementos del DOM que contienen el texto de la empresa
    # get_by_text con re.compile hace búsqueda case-insensitive en Python Playwright
    elementos = page.get_by_text(re.compile(re.escape(empresa), re.IGNORECASE))

    for el in elementos.all():
        # Obtiene el texto visible del elemento
        parrafo = el.inner_text().strip()

        # Valida la longitud del texto del nodo
        if len(parrafo) < MIN_CHARS_PARRAFO:
            continue
        if parrafo in vistos:
            continue
        vistos.add(parrafo)

        # Buscar el <a href> más cercano subiendo por el DOM con xpath
        link = None
        try:
            # ancestor::a busca el <a> más cercano hacia arriba en el árbol DOM
            a = el.locator("xpath=ancestor::a").last
            href = a.get_attribute("href")
            if href:
                link = urljoin(base_url, href)
        except Exception:
            pass

        # Devuelve el texto del elemento y el link más cercano
        resultados.append({"parrafo": parrafo, "link": link})

    return resultados
# endregion 2.2

#################################################################################
# region 2.3 - Acceder al HTML de una página con playwright
#################################################################################

def _fetch_html(url: str, page) -> str | None:
    """Renderiza la página con Playwright y devuelve el HTML completo."""

    try:
        # Espera hasta que toda la página (javascript incluido) esté cargada
        page.goto(url, timeout=30_000, wait_until="networkidle")

        # Devuelve el contenido HTML actual del DOM de la página en ese momento, es decir, incluyendo el javascript generado
        return page.content()

    except Exception:
        return None

# endregion 2.3

# endregion (2)

# ────────────────────────────────────────────────────────────────────────────
# region 3 - Helpers "cumplir objetivo"
# ────────────────────────────────────────────────────────────────────────────

    ##################################################################################
    # region 3.1 - Definir herramienta para extraer los links de una página con playwright
    ##################################################################################

def _extraer_links_pagina(page, base_url: str) -> dict[str, str]:
    """
    Extrae todos los links visibles de la página actual.
    Devuelve un dict { texto_del_link: url_absoluta }.
    """
    links = {}
    # Obtiene todos los elementos <a> con href de la página
    elementos_a = page.locator("a[href]").all()
    for el in elementos_a:
        try:
            texto = el.inner_text().strip()
            href  = el.get_attribute("href")
            if texto and href:
                # Convierte href relativo a URL absoluta
                links[texto[:80]] = urljoin(base_url, href)
        except Exception:
            pass
    return links

    # endregion 3.1

    ##################################################################################
    # region 3.2 . Definir acciones que se puede ejecutar con playwright (click, escribir...)
    ##################################################################################

def _ejecutar_accion(accion: str, parametro: str, page) -> str | bool:
    """
    Ejecuta la acción indicada por el LLM usando Playwright.
    Devuelve True si la acción se ejecutó correctamente, False si falló.
    """
    try:
        if accion == "click":
            # Hace click en el primer elemento que contiene el texto del parámetro
            page.get_by_text(parametro).first.click()
            # Espera a que la página se estabilice tras el click
            page.wait_for_load_state("networkidle", timeout=15_000)

        elif accion == "escribir":
            # Escribe el texto en el campo de búsqueda que esté enfocado o visible
            # Busca el primer input visible de tipo texto/search
            page.locator("input:visible").first.click()
            page.locator("input:visible").first.fill(parametro)
            # Pulsa Enter para lanzar la búsqueda
            page.keyboard.press("Enter")
            # Espera a que la página cargue los resultados
            page.wait_for_load_state("networkidle", timeout=15_000)

        elif accion == "navegar":
            # Navega a la URL indicada
            page.goto(parametro, timeout=30_000, wait_until="networkidle")

        elif accion == "scroll":
            # Hace scroll hasta el final de la página para cargar contenido lazy
            page.keyboard.press("End")
            page.wait_for_timeout(1_000)

        elif accion == "extraer":
            return page.inner_text("body")

        elif accion == "fin":
            pass

        return True

    except Exception as e:
        return False

    # endregion 3.2
 
# endregion

##################################################################################
# region 4 - Definir proceso
##################################################################################


##################################################################################
# region 4.1 - Definir proceso con python de cumplir con el objetivo
##################################################################################

def ejecutar_objetivo_python(page, llm, objetivo: str, url_inicial: str, st_container) -> str | None:
    """
    Loop agéntico implementado en Python puro.
    El LLM decide qué acciones ejecutar en Playwright para cumplir el objetivo dado.

    Devuelve el texto extraído si el LLM llama a "extraer", o None si termina sin resultado.

    Parámetros:
      page          → instancia de página de Playwright ya abierta y en url_inicial
      llm           → modelo LangChain listo para invocar
      objetivo      → string con el objetivo en lenguaje natural
      url_inicial   → URL de partida (ya cargada en page)
      st_container  → contenedor de Streamlit donde mostrar el progreso
    """
    from langchain_core.messages import HumanMessage

    # Inicializo la variable historial parar guardar el historial de acciones ejecutadas para que el LLM no repita pasos
    historial: list[str] = []

    # Controla el número de pasos de agente para que no se embucle
    for paso in range(MAX_PASOS_AGENTE):

        st_container.write(f"🤖 Paso {paso + 1}/{MAX_PASOS_AGENTE}...")

        # Obtiene la URL actual del navegador (puede haber cambiado tras navegar/click)
        url_actual = page.url

        # Obtiene el texto visible actual de la página
        texto_pagina = page.inner_text("body")

        # Extrae los links disponibles en la página actual
        links = _extraer_links_pagina(page, url_actual)

        # Formatea los links como texto para el prompt (máx. 30 links para no saturar)
        links_texto = "\n".join(
            f"  - {texto} → {url}" for texto, url in list(links.items())[:30]
        )

        # Construye el prompt para el LLM con el estado actual de la página
        prompt = _PROMPT_AGENTE.format(
            objetivo   = objetivo,
            url_actual = url_actual,
            links      = links_texto or "(no se encontraron links)",
            texto      = texto_pagina[:3000],
            historial  = "\n".join(historial) or "(ninguna aún)",
            acciones   = ACCIONES_DISPONIBLES,
        )

        # Invoca el LLM para que decida la siguiente acción
        respuesta = llm.invoke([HumanMessage(content=prompt)])

        # Intenta parsear el JSON que devuelve el LLM
        try:
            # Limpia posibles bloques markdown que el LLM añada alrededor del JSON
            contenido = re.sub(r"```json|```", "", respuesta.content).strip()
            decision  = json.loads(contenido)
        except Exception:
            st_container.warning(f"⚠️ El LLM no devolvió JSON válido: {respuesta.content[:200]}")
            break

        accion     = decision.get("accion", "fin")
        parametro  = decision.get("parametro", "")
        razon      = decision.get("razonamiento", "")

        # Muestra el razonamiento y la acción elegida por el LLM
        st_container.write(f"💭 {razon}")
        st_container.write(f"▶️ Acción: **{accion}** — `{parametro}`")

        # Guarda la acción en el historial para evitar bucles
        historial.append(f"Paso {paso+1}: {accion}({parametro}) — {razon}")

        # Si el LLM decide terminar sin extraer nada
        if accion == "fin":
            return None

        # Ejecuta la acción (para "extraer" devuelve el texto; para el resto, bool)
        resultado = _ejecutar_accion(accion, parametro, page)

        if accion == "extraer":
            return resultado

        if resultado is False:
            st_container.warning(f"⚠️ No se pudo ejecutar: {accion}({parametro})")

    # Si se alcanza el máximo de pasos sin llegar a "extraer" o "fin"
    st_container.warning("⚠️ Se alcanzó el máximo de pasos sin completar el objetivo.")
    return None

# endregion 4.1

##################################################################################
# region 4.2 - Definir proceso con langgraph de cumplir con el objetivo (con python y langgraph)
##################################################################################



def ejecutar_objetivo_langgraph(page, llm, objetivo: str, url_inicial: str, st_container) -> str | None:
    """
    Loop agéntico implementado con LangGraph.

    Esto es una máquina de estados implementado manualmente con un enfoque react

    El grafo tiene tres nodos:
      - observar  → lee la página, invoca el LLM y decide la siguiente acción
      - ejecutar  → ejecuta la acción en Playwright y actualiza el historial
      - END       → nodo final de LangGraph (sale del grafo)

    Parámetros: igual que ejecutar_objetivo_python.
    """
    from typing import TypedDict, Annotated
    from langchain_core.messages import HumanMessage
    from langgraph.graph import StateGraph, END
    import operator

    ############################################################
    # region 4.2.1 - Defino MEMORIA del grafo = el Estado del grafo 
    ############################################################

    # TypedDict que define los campos que comparte el estado entre nodos.
    # "operator.add" en historial indica que cada nodo AÑADE entradas en vez de reemplazarlas.

    class Estado(TypedDict):
        objetivo:     str               # objetivo en lenguaje natural (inmutable)
        historial:    Annotated[list[str], operator.add]  # acciones ejecutadas
        accion:       str               # última acción decidida por el LLM
        parametro:    str               # parámetro de la acción
        razonamiento: str               # razonamiento del LLM
        resultado:    str | None        # texto extraído al final (None si no hay)
        pasos:        int               # contador de pasos para evitar bucles

    # endregion 4.2.1

    ############################################################
    # region 4.2.2 - Defino los nodos
    ############################################################

    """ Un nodo es un función que recibe un estado y devuelve cambios en el estado """
    """ En LangGraph los nodos NO devuelven el estado completo """
    """ solo los cambios (updates) del estado """

    # region 4.2.2.1 - Defino Nodo el CEREBRO "observar" 
        
        # Lee el estado actual de la página, construye el prompt, invoca el LLM
        # y actualiza el estado con la acción decidida.

    def nodo_observar(estado: Estado) -> dict:
        """
        Lee la página, llama al LLM y devuelve la acción a ejecutar

        Recibe el estado actual y devuelve : 
            - Acción: "click" | "navegar" | "scroll" | "extraer" | "fin"....
            - Parámetro: "texto del elemento a clickar, URL a navegar, o vacío si no aplica"
            - Razonamiento: explicación de lo que ha hecho
            - Pasos: número de paso
        """

        ###############################################################
        # Construye el prompt con el estado actual de la página
        ###############################################################

        # Obtiene la URL actual del navegador
        url_actual = page.url

        # Obtiene el texto visible actual de la página
        texto_pagina = page.inner_text("body")

        # Extrae los links disponibles en la página
        links = _extraer_links_pagina(page, url_actual)
        links_texto = "\n".join(
            f"  - {texto} → {url}" for texto, url in list(links.items())[:30]
        )

        # Crea la variable prompt
        prompt = _PROMPT_AGENTE.format(
            objetivo   = estado["objetivo"],
            url_actual = url_actual,
            links      = links_texto or "(no se encontraron links)",
            texto      = texto_pagina[:3000],
            historial  = "\n".join(estado["historial"]) or "(ninguna aún)",
            acciones   = ACCIONES_DISPONIBLES,
        )

        ###############################################################
        # Invoca el LLM
        ###############################################################

        respuesta = llm.invoke([HumanMessage(content=prompt)])

        ###############################################################
        # Parsea el JSON de la respuesta
        ###############################################################

        # Accede al contenido

        try:
            contenido = re.sub(r"```json|```", "", respuesta.content).strip()
            decision  = json.loads(contenido)
        except Exception:
            # Si el LLM no devuelve JSON válido, terminamos
            st_container.warning(f"⚠️ El LLM no devolvió JSON válido: {respuesta.content[:200]}")
            decision = {"accion": "fin", "parametro": "", "razonamiento": "JSON inválido"}

        # Estrae la acción, parámetro y razón devuelto por el LLM

        accion     = decision.get("accion", "fin")
        parametro  = decision.get("parametro", "")
        razon      = decision.get("razonamiento", "")

        ###############################################################
        # Muestra pasos realizados
        ###############################################################

        # Muestra el paso y el razonamiento del LLM en Streamlit
        st_container.write(f"🤖 Paso {estado['pasos'] + 1}/{MAX_PASOS_AGENTE}...")
        st_container.write(f"💭 {razon}")
        st_container.write(f"▶️ Acción: **{accion}** — `{parametro}`")

        ###############################################################
        # Devuelve los campos del estado que este nodo actualiza
        ###############################################################

        return {
            "accion":       accion,
            "parametro":    parametro,
            "razonamiento": razon,
            "pasos":        estado["pasos"] + 1,
        }

    # endregion 4.2.2.1

    #  region 4.2.2.2 - Defino HERRAMIENTAS = Nodo "ejecutar"  (ejecuta acciones)
        # Ejecuta en Playwright la acción decidida por el LLM y actualiza el historial.

    def nodo_ejecutar(estado: Estado) -> dict:
        """Ejecuta la acción decidida por el nodo observar y actualiza el historial."""
        """Recibe el estado actual, ejecuta la acción y devuelve : historial"""

        accion    = estado["accion"]
        parametro = estado["parametro"]

        # Ejecuta la acción (para "extraer" devuelve el texto; para el resto, bool)
        resultado = _ejecutar_accion(accion, parametro, page)

        if accion == "extraer":
            return {"resultado": resultado}

        if resultado is False:
            st_container.warning(f"⚠️ No se pudo ejecutar: {accion}({parametro})")

        # Añade la acción al historial (operator.add la concatena automáticamente)
        entrada_historial = f"Paso {estado['pasos']}: {accion}({parametro}) — {estado['razonamiento']}"
        return {"historial": [entrada_historial]}

    # endregion 4.2.2.2

    # endregion 4.2.2

    ############################################################
    # region 4.2.3 - Defino las transiciones
    ############################################################

    # ── Función de enrutamiento (arista condicional) ──────────────────────────
    # Decide a qué nodo ir después de "observar" en función de la acción del LLM.

    def continuar_o_terminar(estado: Estado) -> str:
        """Después de ejecutar, decide si seguir observando o terminar."""

        # Si ya tenemos resultado (extraer) o la acción fue "fin" → terminar
        if estado.get("resultado") is not None or estado["accion"] in ("fin",):
            return END

        # Si se alcanzó el máximo de pasos → terminar
        if estado["pasos"] >= MAX_PASOS_AGENTE:
            st_container.warning("⚠️ Se alcanzó el máximo de pasos sin completar el objetivo.")
            return END

        # Si no → volver a observar la página
        return "observar"

    # endregion 4.2.3

    ############################################################
    # region 4.2.4 Construcción del grafo
    ############################################################

    # Creo el objeto que representa un nodo en ejecución
    grafo = StateGraph(Estado)

    # Añade los dos nodos creados (observar y ejecutar) al grafo
    grafo.add_node("observar", nodo_observar)
    grafo.add_node("ejecutar", nodo_ejecutar)

    # Define el nodo de entrada del grafo
    grafo.set_entry_point("observar")

    # Indico que después de observar, se vaya a ejecutar = crear una Arista fija: observar → ejecutar (siempre) 
    grafo.add_edge("observar", "ejecutar")

    # Indico que después de ejecutar, se dedica si continuar (llamando al nodo observar o finalizar) = crear una arista condicional: ejecutar → observar | END según el estado
    grafo.add_conditional_edges("ejecutar", continuar_o_terminar)

    # Compila el grafo en un objeto ejecutable (Runnable de LangChain)
    app_grafo = grafo.compile()

    # endregion 4.2.4

    ############################################################
    #  region 4.2.5 - Ejecución del grafo 
    ############################################################

    # Defino el Estado inicial con el objetivo y contadores a cero
    estado_inicial = {
        "objetivo":     objetivo,
        "historial":    [],
        "accion":       "",
        "parametro":    "",
        "razonamiento": "",
        "resultado":    None,
        "pasos":        0,
    }

    # Ejecuta el grafo hasta que llegue a END
    estado_final = app_grafo.invoke(estado_inicial)

    # Devuelve el texto extraído o None si no se completó el objetivo
    return estado_final.get("resultado")

    # endregion 4.2.5

# endregion 4.2

# endregion 4

# ────────────────────────────────────────────────────────────────────────────
# region 5- UI Streamlit
# ────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Agente Noticias", page_icon="📰", layout="wide")
st.title("📰 Agente Búsqueda de Noticias")
st.caption("Busca menciones de una empresa o cumple un objetivo en las webs configuradas en URLs.xlsx")

############################################################
#  SECCIÓN.UI: Sidebar 
############################################################

with st.sidebar:
    st.header("⚙️ Configuración")

    # Selector de modelo LLM (solo necesario en modo "Cumplir objetivo") 
    st.subheader("🧠 Modelo LLM")
    st.caption("Usado en el modo 'Cumplir objetivo'")

    provider = st.selectbox(
        "Proveedor",
        options=["ollama", "mistral", "qwen3", "gemma4", "gemini"],
        format_func=lambda p: {
            "ollama":  "🦙 Ollama — llama3.2:3b",
            "mistral": "🦙 Ollama — mistral-small3.2",
            "qwen3":   "🦙 Ollama — Qwen3.14b",
            "gemma4":  "🦙 Ollama — gemma4",
            "gemini":  "✨ Gemini (API)",
        }[p],
    )

    # Parámetros específicos de cada proveedor
    llm_kwargs: dict = {}
    if provider == "ollama":
        llm_kwargs = {"model": st.text_input("Modelo Ollama", value="llama3.2:3b")}
    elif provider == "mistral":
        llm_kwargs = {"model": st.text_input("Modelo Mistral", value="mistral-small3.2")}
    elif provider == "qwen3":
        llm_kwargs = {"model": st.text_input("Modelo Qwen3", value="Qwen3.14b-ollama")}
    elif provider == "gemma4":
        llm_kwargs = {"model": st.text_input("Modelo Gemma4", value="gemma4")}
    elif provider == "gemini":
        llm_kwargs = {
            "api_key": st.text_input("API Key", value="AIzaSyCfJty50M3F-UB18o-AZscU-id5RsYQZZQ", type="password"),
            "model":   st.text_input("Modelo", value="gemini-2.0-flash"),
        }

    st.divider()

    #  URLs cargadas desde el fichero ──
    st.caption("URLs cargadas desde **URLs.xlsx**")
    try:
        df_urls = pd.read_excel(URLS_FILE)
        df_urls["url"] = df_urls["url"].apply(
            lambda u: u if str(u).startswith("http") else f"https://{u}"
        )
        urls = df_urls["url"].dropna().tolist()
        for u in urls:
            st.caption(f"• {u}")
    except Exception as e:
        st.error(f"Error cargando URLs.xlsx: {e}")
        urls = []

############################################################
#  SECCIÓN.UI: Panel principal 
############################################################

# Selector de modo: búsqueda determinista o agente con objetivo
modo = st.radio(
    "Modo",
    options=["Buscar texto", "Cumplir objetivo"],
    horizontal=True,
)

st.divider()

# Inputs según el modo seleccionado
if modo == "Buscar texto":
    # Modo búsqueda: el usuario introduce el nombre de la empresa
    empresa = st.text_input("🏢 Empresa a buscar", placeholder="Ej: Telefónica, Repsol, Apple...")
    objetivo = None
    listo = bool(empresa)

else:
    # Modo objetivo: el usuario describe en lenguaje natural qué quiere conseguir
    empresa = None
    objetivo = st.text_area(
        "🎯 Objetivo",
        placeholder=(
            "Ej: descarga el texto de la columna de opinión de Ignacio Camacho\n"
            "Ej: encuentra el enlace al Annual Report de Uber"
        ),
        height=100,   # ~3 líneas de texto
    )
    listo = bool(objetivo)

# Botón de acción — deshabilitado si no hay input
buscar = st.button("🔍 Ejecutar", type="primary", disabled=not listo)

############################################################
#  SECCIÓN.UI: Proceso principal 
############################################################

if buscar and listo and urls:

    from playwright.sync_api import sync_playwright

    # Inicializo la variable resultado según el modo
        # Buscar texto  → url: lista de { parrafo, link }
        # Cumplir obj.  → url: texto extraído (str)
    resultados: dict = {}

    # p es el objeto Playwright
    with sync_playwright() as p:

        # Creo el objeto browser de Playwright tipo Chromium. Representa la instancia del navegador abierto.
        browser = p.chromium.launch(headless=False)

        # Abro una página en el browser
        page = browser.new_page()

        # Aplico políticas de "stealth" para que el navegador no detecte el scraping
        # Modifica el navegador para que parezca un usuario real y no un bot
        from playwright_stealth.stealth import Stealth
        Stealth().apply_stealth_sync(page)

        # Cargo el LLM solo si estamos en modo objetivo (no es necesario en búsqueda)
        llm = None
        if modo == "Cumplir objetivo":
            with st.spinner("Cargando modelo LLM..."):
                try:
                    llm = get_llm(provider, **llm_kwargs)
                except Exception as e:
                    st.error(f"Error cargando LLM: {e}")
                    st.stop()

        barra = st.progress(0, text="Iniciando...")

        # Recorro las páginas a buscar
        for i, url_web in enumerate(urls):
            barra.progress(i / len(urls), text=f"🌐 {url_web}")

            # En modo "Cumplir objetivo" mantenemos el bloque expandido para ver los pasos del agente
            expandido = (modo == "Cumplir objetivo")

            with st.status(f"🌐 {url_web}", expanded=expandido) as status:

                st.write("Descargando y renderizando...")

                ##################################################################################################
                # Obtengo el html (dom) de la página web a usar
                ##################################################################################################

                # Obtengo el HTML actual de la página una vez que ha cargado entera (incluyendo lo generado por javascript)
                html = _fetch_html(url_web, page)

                # Si fetch_html falla, en modo "Cumplir objetivo" intentamos continuar igualmente
                # porque Playwright puede tener algo cargado aunque haya habido timeout parcial
                if html is None and modo == "Buscar texto":
                    status.update(label=f"❌ {url_web} — error al cargar", state="error")
                    continue

                if html is None:
                    st.warning("⚠️ No se pudo obtener el HTML completo — intentando continuar con lo cargado")

                # Muestra la longitud de caractéres de HTML extraido (puede ser None si falló la carga)
                if html:
                    st.write(f"HTML extraído: {len(html):,} caracteres")

                # Mostrar texto completo para depuración
                texto_debug = page.inner_text("body")
                st.text_area("Texto completo", texto_debug, height=300)

                ##################################################################################################
                # Bifurcación según el modo
                ##################################################################################################

                if modo == "Buscar texto":

                    ##################################################################################################
                    # Buscar texto dentro de una página y mostrar la URL a la que se accede
                    ##################################################################################################

                    # Buscar menciones del texto en el HTML de la página (vía BeautifulSoup)
                    menciones = _buscar_texto_beautifulsoup(html, empresa, url_web)

                    # Buscar menciones del texto en la página (vía Playwright)
                    # menciones = _buscar_texto_playwright(empresa, url_web, page)

                    # Muestra las menciones encontradas
                    st.write(f"Menciones encontradas: {len(menciones)}")

                    if menciones:
                        resultados[url_web] = menciones
                        status.update(label=f"✅ {url_web} — {len(menciones)} menciones", state="complete")
                    else:
                        status.update(label=f"⚪ {url_web} — sin menciones", state="complete")

                else:  # modo == "Cumplir objetivo"

                    ##################################################################################################
                    # Navegar una página en búsqueda de un obejtivo
                    ##################################################################################################

                    # El LLM navega la página paso a paso para cumplir el objetivo
                    # Cada iteración del loop agéntico decide una acción y la ejecuta con Playwright
                    # Pasamos "status" para que los pasos aparezcan dentro del bloque expandido

                    # Implementación con Python puro (loop for)
                    #resultado_obj = ejecutar_objetivo_python(page, llm, objetivo, url_web, status)

                    # Implementación con LangGraph (grafo de nodos con estado)
                    resultado_obj = ejecutar_objetivo_langgraph(page, llm, objetivo, url_web, status)

                    if resultado_obj:
                        resultados[url_web] = resultado_obj
                        status.update(label=f"✅ {url_web} — objetivo completado", state="complete")
                    else:
                        status.update(label=f"⚪ {url_web} — objetivo no completado", state="complete")

        browser.close()

    barra.progress(1.0, text="✅ Proceso completado")
    ##################################################################################################
    # SECCIÓN.UI: Resultados 
    ##################################################################################################

    st.divider()

    if not resultados:
        st.warning("No se encontraron resultados.")

    elif modo == "Buscar texto":
        # Muestra las menciones encontradas con el párrafo y el link
        total = sum(len(v) for v in resultados.values())
        st.success(f"**{total}** menciones de **{empresa}** en {len(resultados)} fuentes")

        for url_web, menciones in resultados.items():
            st.subheader(f"🌐 {url_web}")
            for m in menciones:
                # Resalta el nombre de la empresa en negrita dentro del párrafo
                destacado = re.sub(
                    re.escape(empresa),
                    f"**{empresa}**",
                    m["parrafo"],
                    flags=re.IGNORECASE,
                )
                if m["link"]:
                    st.markdown(f"> {destacado}  \n> [🔗 Ver artículo]({m['link']})")
                else:
                    st.markdown(f"> {destacado}")
            st.divider()

    else:  # modo == "Cumplir objetivo"
        # Muestra el texto extraído por el agente para cada URL
        st.success(f"Objetivo completado en {len(resultados)} fuentes")

        for url_web, texto_extraido in resultados.items():
            st.subheader(f"🌐 {url_web}")
            st.text_area("Contenido extraído", texto_extraido, height=400)
            st.divider()

# endregion 5