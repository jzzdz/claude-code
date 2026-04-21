# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **Framework UI**: Streamlit (interfaz web para búsqueda y agente)
- **Automatización web**: Playwright + playwright-stealth (renderizado JS, scraping anti-bot)
- **Orquestación agéntica**: LangGraph (máquina de estados con nodos)
- **LLMs**: LangChain + múltiples proveedores:
  - Ollama (local: llama3.2, mistral-small3.2, Qwen3.14b, gemma4, deepseek-r1)
  - Gemini (API: gemini-2.0-flash)
  - Hugging Face (cargado en memoria con transformers)
- **Parsing HTML**: BeautifulSoup
- **Datos**: pandas, Excel (URLs.xlsx)

## Ejecutar

```bash
# App principal
streamlit run agente_busqueda_noticias.py

# App alternativa (experimental)
streamlit run herbie_app.py
```

## Archivos Principales

| Archivo | Propósito |
|---------|-----------|
| `agente_busqueda_noticias.py` | App principal Streamlit. Dos modos: búsqueda determinista y agente LLM |
| `herbie_llm.py` | Factory de LLMs. `get_llm(provider, **kwargs)` devuelve ChatModel de LangChain |
| `wiki_retriever.py` | RAG de dos fases sobre archivos markdown locales |
| `herbie_app.py` | App alternativa (experimental, sin documentar) |
| `URLs.xlsx` | Lista de URLs para búsqueda. Requiere columna `url` |

## Arquitectura del Agente (`agente_busqueda_noticias.py`)

### Flujo "Buscar texto" (determinista)
```
URL → _fetch_html (Playwright networkidle) → BeautifulSoup →
_buscar_texto_beautifulsoup → párrafos + link más cercano (hasta 8 niveles DOM)
```

### Flujo "Cumplir objetivo" (agéntico con LangGraph)
```
_ejecutar_objetivo_langgraph
  └─ _crear_grafo_agente → StateGraph compilado
       ├─ nodo_observar: lee página → construye prompt → LLM decide acción
       └─ nodo_ejecutar: Playwright ejecuta → actualiza historial
            └─ transicionar → [observar | END]
```

**Estado TypedDict**: `objetivo`, `historial` (Annotated con operator.add), `accion`, `parametro`, `razonamiento`, `resultado`, `pasos`

**Separación de responsabilidades** (refactor Apr-2026):
- `_crear_grafo_agente(page, llm, st_container)` → construye y compila el grafo (puro)
- `_ejecutar_objetivo_langgraph(page, llm, objetivo, url_inicial, st_container)` → inicializa estado e invoca

### Acciones disponibles para el LLM

`click` · `escribir` · `navegar` · `scroll` · `extraer` (resultado final) · `fin` (sin resultado)

## Arquitectura Wiki Retriever (`wiki_retriever.py`)

RAG de dos fases sobre archivos `.md` locales (paradigma LLM Wiki de Karpathy):

- **Fase 1 — Discovery**: LLM recibe solo `index.md` + query → devuelve hasta 4 slugs relevantes (CSV, sin explicaciones)
- **Fase 2 — Answer**: se cargan solo los archivos `{slug}.md` que existen → se concatena el texto para inyectar en el prompt

`recuperar_contexto_wiki(llm, wiki_path, query)` → devuelve `{contexto_str, slugs_usados, tokens_discovery, error}`

## Factory de LLMs (`herbie_llm.py`)

`get_llm(provider, **kwargs)` soporta: `ollama`, `mistral`, `qwen3`, `gemma4`, `deepseek`, `huggingface`, `gemini`

- Ollama usa `ChatOllamaWithLogprobs` (subclase con `logprobs=True, stream=False`)
- HuggingFace se cachea en `_hf_cache` (solo se carga una vez por sesión)
- Todos devuelven un `BaseChatModel` de LangChain (`.invoke([HumanMessage(...)])`)

## Convenciones

### Nombres
- Funciones internas: `_nombre_funcion()` (prefijo guion bajo)
- Constantes: `MAYUSCULAS_CON_GUIONES`
- Variables de estado LangGraph: nombres descriptivos sin abreviaciones

### Código
- Comentarios en español
- Estructura con `# region X.Y - Descripción` / `# endregion X.Y`
- Máximo 120 caracteres por línea

### Git
- Ramas: `feature/<nombre>` o `refactor/<nombre>`
- Commits: mensaje en español, resumen de sesión completa
- PRs: descripción de cambios + test plan

## Notas Técnicas

### Migración de directorio (Apr-2026)
- El proyecto fue migrado de `ProyectoHerbie/` a `ProyectoHerbie_test/` para permitir iteración experimental
- El directorio padre (`context/claude-code/`) es el repositorio git raíz
- Nuevos archivos en el padre: `.agents/` (definiciones de agentes), `.claude/` (config Claude Code), `skills-lock.json`, `llm-council-master/`

### LangGraph
- `operator.add` en historial → cada nodo concatena, no reemplaza
- Nodos devuelven solo los campos que cambian (updates parciales)
- `add_conditional_edges("ejecutar", transicionar)` ya implementado
- Grafo compilado con `grafo.compile()` → Runnable de LangChain

### Playwright
- `page.goto(url, wait_until="networkidle")` → espera JS completo
- `playwright_stealth.Stealth().apply_stealth_sync(page)` → evasión de detección
- `page.locator("a[href]").all()` → todos los links; `page.get_by_text(texto).first.click()` → click por texto

### LLM Prompts
- Respuesta siempre en JSON: `{razonamiento, accion, parametro}`
- Límites: 3000 chars de texto visible, 30 links por página
- Historial de acciones previas incluido para evitar bucles

## Próximas Tareas

- [x] Refactorizar `_ejecutar_accion` para centralizar extracción de contenido
- [x] Separar construcción del grafo (`_crear_grafo_agente`) de su ejecución
- [x] Crear CLAUDE.md del proyecto con documentación completa
- [x] Usar `add_conditional_edges` (ya implementado)
- [x] Migrar proyecto de `ProyectoHerbie/` a `ProyectoHerbie_test/`
- [ ] Añadir tools con `@tool` que ejecuta el LLM
- [ ] Refactor completo de responsabilidades
- [ ] Probar Ghostty
- [ ] Explorar integración con `llm-council-master` (disponible en directorio padre)

## Ritual de Commit (OBLIGATORIO)

**ANTES DE CADA COMMIT, ACTUALIZAR ESTE CLAUDE.MD:**

1. Marcar tareas completadas con `[x]` en "Próximas Tareas"
2. Documentar cambios de arquitectura en "Notas Técnicas"
3. Incluir CLAUDE.md en el mismo commit

**Ejemplo de mensaje:**
```
Refactor: separar grafo de ejecución + actualizar docs

- _crear_grafo_agente() para construcción
- _ejecutar_objetivo_langgraph() solo ejecuta
- CLAUDE.md: corregir nombres de funciones y marcar tareas
```
