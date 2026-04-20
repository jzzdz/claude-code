# ProyectoHerbie — Instrucciones de Proyecto

## Stack

- **Framework UI**: Streamlit (interfaz web para búsqueda y agente)
- **Automatización web**: Playwright (renderizado JS, navegación, scraping)
- **Orquestación agéntica**: LangGraph (máquina de estados con nodos)
- **LLMs**: LangChain + múltiples proveedores:
  - Ollama (local: llama3.2, mistral, qwen, gemma)
  - Gemini (API)
  - Hugging Face (descargado en memoria)
- **Parsing HTML**: BeautifulSoup
- **Datos**: pandas, Excel (URLs.xlsx)

## Archivos Principales

| Archivo | Propósito |
|---------|-----------|
| `agente_busqueda_noticias.py` | App principal Streamlit. Dos modos: búsqueda determinista y agente LLM |
| `herbie_llm.py` | Factory de LLMs. Abstracción sobre proveedores (ollama, gemini, huggingface) |
| `wiki_retriever.py` | Recuperación de contexto de wiki. Discovery + Answer en dos fases |
| `herbie_app.py` | App alternativa (experimental) |
| `URLs.xlsx` | Lista de URLs para búsqueda. Cargadas dinámicamente en Streamlit |
| `cowork_instrucciones.md` | Instrucciones de uso |

## Ejecutar

```bash
# Agente de búsqueda (principal)
streamlit run agente_busqueda_noticias.py

# App alternativa
streamlit run herbie_app.py
```

## Arquitectura del Agente

### Flujos

#### 1. "Buscar texto" (determinista)
```
URL → Playwright renderiza → BeautifulSoup parsea → 
Busca empresa en texto → Extrae párrafos + links más cercanos
```

#### 2. "Cumplir objetivo" (agéntico)
```
LLM observa página → decide acción → Playwright ejecuta → 
LLM observa resultado → repite hasta "extraer" o "fin"
```

### Grafo (LangGraph)

**Construcción**: `crear_grafo_agente(page, llm, st_container)`
- Define Estado (TypedDict): objetivo, historial, accion, parametro, razonamiento, resultado, pasos
- Nodos: `nodo_observar` (LLM decide), `nodo_ejecutar` (Playwright actúa)
- Transiciones: observar → ejecutar → [observar | END] (condicional)

**Ejecución**: `ejecutar_objetivo_langgraph(page, llm, objetivo, url_inicial, st_container)`
- Crea el grafo
- Inicializa estado
- Invoca hasta END

### Acciones disponibles

El LLM puede ordenar:
- `click` — hace click en elemento con texto coincidente
- `escribir` — rellena input + Enter
- `navegar` — va a URL
- `scroll` — scroll al final
- `extraer` — captura texto visible (resultado final)
- `fin` — termina sin resultado

## Convenciones

### Nombres
- Funciones internas: `_nombre_funcion()` (guion bajo)
- Constantes: `MAYUSCULAS_CON_GUIONES`
- Variables de estado: nombres descriptivos (accion, parametro, razonamiento)

### Código
- Comentarios en español
- Docstrings explicando entrada/salida
- Regions con `# region X.Y - Descripción` para estructura
- Máximo 120 caracteres por línea

### Git
- Ramas: `feature/<nombre>` o `refactor/<nombre>`
- Commits: mensaje en español, resumen de sesión completa
- PRs: descripción de cambios + test plan

## Notas Técnicas

### LangGraph
- TypedDict para estado tipado
- `operator.add` en historial → concatena automáticamente
- Nodos devuelven solo cambios (updates), no estado completo
- Transiciones condicionales con funciones que devuelven nombre de nodo o END

### Playwright
- `page.goto(url, wait_until="networkidle")` → espera JS completo
- `page.inner_text("body")` → texto visible
- `page.get_by_text(regex)` → localiza por texto (case-insensitive)
- Aplicar stealth para evitar detección de bots

### LLM Prompts
- Formato JSON para respuestas (razonamiento, accion, parametro)
- Máximo 3000 caracteres de texto visible (contexto)
- Máximo 30 links por página (para no saturar)
- Historial de acciones previas (evitar bucles)

## Flujo de Trabajo (este proyecto)

1. **Plan antes de código** — piensa, explica, espera validación
2. **Rama por tarea** — `git checkout -b <rama>`
3. **Commit en rama** — resumen en español
4. **PR en GitHub** — título + descripción con test plan
5. **Merge después de validar**

## Próximas Tareas

- [ ] Añadir tools con `@tool` que ejecuta el LLM
- [ ] Cambiar aristas por `add_conditional_edges` (ya usado en código actual)
- [ ] Refactor completo de responsabilidades
- [ ] Probar Ghostty

## Ritual de Commit

**Antes de cada commit, actualizar este CLAUDE.md:**
1. Marcar tareas completadas en "Próximas Tareas"
2. Añadir nuevas tareas descubiertas
3. Actualizar "Notas Técnicas" con cambios en arquitectura
4. Commitear archivo + cambios juntos

Esto mantiene el proyecto documentado y sincronizado con la realidad.
