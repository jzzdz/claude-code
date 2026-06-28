# _template_repo

`_template_repo` es un sistema de plantillas y skills para crear repos nuevos
preparados para desarrollo asistido por agentes de codificacion.

No es un repo de producto final. Su funcion es conservar templates genericas,
manifiestos verificables y skills que guian a un agente al crear y planificar
repos destino.

## Componentes

| Componente | Funcion |
| --- | --- |
| `_template_repo` | Contiene templates, manifests y skills reutilizables. No contiene memoria viva de productos. |
| Repo destino | Repo nuevo generado desde una template. Ahi vive el producto real. |
| `_contexto_agente_codificador` | Define el marco global de agentes, checkpoints y preferencias compartidas. |
| Agentes globales | Roles como `leader`, `lector`, `implementador` y `revisor`. No se copian aqui. |
| Skills | Instrucciones reutilizables que explican un flujo de trabajo para agentes. |
| Templates | Estructuras base copiables para distintos tipos de repos. |
| `scripts/bootstrap_repo.py` | Generador reproducible de repos destino desde una template. |
| `init.sh` | Verificacion del propio `_template_repo` y de sus templates. |
| `feature_list.json` | Backlog local del repo destino. La template lo inicializa con F000. |
| `progress/` | Memoria operativa local del repo destino. No debe contener datos personales en la template. |

## Templates disponibles

Las templates viven en `templates/repo/`.

- `python_basic`: proyecto Python sencillo, sin dependencias externas, con
  estructura minima de codigo, tests, documentacion y progreso.
- `langgraph_agent`: proyecto base para agentes runtime basados en LangGraph,
  con modulos separados para grafo, prompts, memoria, tools y utilidades.

Cada template debe tener:

- `TEMPLATE.md`: descripcion operativa de la template.
- `template_manifest.json`: lista de archivos, directorios, placeholders y
  comando de verificacion.
- `files/`: contenido que se copia o genera en el repo destino.

## Skills disponibles

Las skills viven en `skills/`.

- `bootstrap_repo`: crea el esqueleto de un repo destino desde una template.
- `plan_product_features`: convierte una idea de producto en una epica y
  features granulares dentro del `feature_list.json` del repo destino.

## Uso de `bootstrap_repo`

Usa esta skill cuando el usuario pida crear un nuevo repo, inicializar un
proyecto, generar estructura base o preparar un repo para trabajo con agentes.

Flujo resumido:

1. Identificar nombre del repo destino.
2. Elegir `python_basic` o `langgraph_agent`.
3. Leer `templates/repo/<template_id>/TEMPLATE.md`.
4. Leer `templates/repo/<template_id>/template_manifest.json`.
5. Ejecutar `scripts/bootstrap_repo.py` para copiar `files/`, sustituir
   `{{project_name}}`, `{{package_name}}` y `{{template_id}}`, validar contra
   el manifest y ejecutar el comando de verificacion del repo generado.
6. Revisar `progress/current.md` del repo destino.

Esta skill crea el continente del repo, no el producto completo.

Ejemplo:

```bash
python3 scripts/bootstrap_repo.py langgraph_agent agente_prueba
```

## Verificar `_template_repo`

Ejecuta:

```bash
./init.sh
```

La verificacion comprueba que cada template tiene `TEMPLATE.md`,
`template_manifest.json`, archivos y directorios requeridos, que no hay
`.DS_Store` y que el script de bootstrap puede generar repos verificables en un
directorio temporal.

## Uso de `plan_product_features`

Usa esta skill despues del bootstrap o cuando el usuario describa un producto
complejo que debe convertirse en backlog.

Flujo resumido:

1. Leer `AGENTS.md`, `docs/architecture.md`, `docs/conventions.md` y
   `feature_list.json` del repo destino.
2. Crear una epica inicial, por ejemplo `EPIC-001 - Construccion inicial del
   producto`.
3. Dividir la idea en features pequenas y ejecutables.
4. Actualizar `feature_list.json` sin implementar todas las features.
5. Actualizar `progress/current.md` con epica, features, siguiente feature,
   decisiones pendientes y riesgos.

Esta skill crea el plan de producto, no ejecuta todo el producto.

## Crear un repo usando `_instrucciones_iniciales.md`

Cuando exista un archivo `_instrucciones_iniciales.md` en el workspace o el
usuario lo aporte como prompt:

1. Leer sus requisitos de producto y restricciones.
2. Activar `bootstrap_repo` para crear el repo destino desde la template
   adecuada.
3. Ejecutar la verificacion indicada por el manifest.
4. Activar `plan_product_features` para convertir la idea en epica y features.
5. Dejar el repo destino listo para que el `leader` delegue la primera feature
   al `implementador`.

No se debe crear el repo destino dentro de `_template_repo`.
