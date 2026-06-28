# CHECKPOINTS - Cierre universal de tareas

Este checklist es el criterio comun para dar por cerrada una tarea en
cualquier repo asistido por estos agentes.

Los repos de producto no necesitan tener un `CHECKPOINTS.md` local. El
checkpoint universal vive en `_contexto_agente_codificador/CHECKPOINTS.md` y se
inyecta en los agentes generados.

## C1 - Alcance y backlog

- [ ] La tarea o subtarea esta claramente identificada.
- [ ] Si existe `task.md` o `tasks.md`, el trabajo esta alineado con una unica
      tarea o fase.
- [ ] Si existe `progress/Current.md`, identifica la tarea/fase activa y el
      siguiente paso inmediato.
- [ ] No se marca un checkbox como completado sin revision aprobada y
      confirmacion del usuario cuando proceda.
- [ ] No se mezclan tareas distintas sin documentarlo y pedir aprobacion.

## C2 - Implementacion

- [ ] Los cambios se limitan al alcance acordado.
- [ ] La estructura respeta `docs/architecture.md` si existe.
- [ ] El codigo respeta `docs/conventions.md` si existe.
- [ ] No se introducen dependencias innecesarias.
- [ ] Si se anade una dependencia, la decision queda documentada.
- [ ] No se corrigen bugs colaterales sin comunicarlo y recibir aprobacion.

## C3 - Tests y verificacion

- [ ] Hay tests o comprobaciones proporcionales al riesgo del cambio.
- [ ] Se ejecuta `./init.sh` si existe.
- [ ] Si no existe `./init.sh`, se descubre y ejecuta el comando adecuado desde
      `README.md`, `Makefile`, `pyproject.toml`, `package.json` u otro archivo
      equivalente.
- [ ] La verificacion termina en verde.
- [ ] Si no se pudo verificar, se explica claramente el motivo y el riesgo.

## C4 - Documentacion

- [ ] Se reviso si procede actualizar `README.md`.
- [ ] Se reviso si procede actualizar `docs/architecture.md`.
- [ ] Se reviso si procede actualizar `docs/conventions.md`.
- [ ] Se reviso si procede actualizar `task.md` o `tasks.md`.
- [ ] Se reviso si procede actualizar `Historico_versiones.md` y `__version__`
      si el repo usa versionado en codigo.
- [ ] Si no se actualizo alguno de esos archivos, la omision esta justificada.

## C5 - Progreso local del repo

- [ ] Si existe `progress/Current.md`, refleja el estado real del trabajo,
      tarea/fase activa y siguiente paso inmediato.
- [ ] Si existe `progress/History.md`, se actualiza al cerrar trabajo terminado
      o una sesion relevante.
- [ ] Si existe `progress/Decisions.md`, registra decisiones tecnicas
      relevantes: que, por que y alternativas descartadas.
- [ ] Si existe `progress/Blockers.md`, registra impedimentos abiertos o
      resueltos con fecha.
- [ ] Los informes generados por agentes se guardan en `progress/` cuando
      existe.
- [ ] Si el cierre completa una user story o la feature, existe la
      retrospectiva correspondiente en `progress/Retrospectives.md` (ver C8).

## C6 - Memoria global del agente codificador

- [ ] Si aparece una preferencia estable del usuario, se propone registrarla en
      `_contexto_agente_codificador/memory/coding_preferences.md`.
- [ ] Si aparece una correccion recurrente, se propone registrarla en
      `_contexto_agente_codificador/memory/corrections.md`.
- [ ] Si aparece una decision global sobre agentes o flujo de trabajo, se
      propone registrarla en `_contexto_agente_codificador/memory/decisions.md`.
- [ ] Si aparece un patron reutilizable, se propone registrarlo en
      `_contexto_agente_codificador/memory/patterns.md`.
- [ ] No se modifica la memoria global sin aprobacion del usuario.

## C7 - Revision

- [ ] El revisor emite `APPROVED` o `CHANGES_REQUESTED`.
- [ ] El veredicto cita hallazgos concretos cuando hay cambios requeridos.
- [ ] No se aprueba con tests rojos.
- [ ] No se aprueba si la documentacion, versionado o progreso necesarios estan
      pendientes.
- [ ] El resultado de la revision queda documentado en `progress/` si existe.

## C8 - Retrospectivas

Aplica solo si el repo usa `progress/`. Las retros se escriben siempre en
`progress/Retrospectives.md` (append, con fecha y cabecera). Dos disparadores:

- **Fin de user story**: cuando todas las tareas de esa US pasan a `- [x]`,
  escribe una retro de user story.
- **Fin de feature**: cuando todas las tareas de `tasks.md` estan en `- [x]`
  (incluida la fase Polish/cross-cutting), escribe la retro de cierre.
  Precondicion: deben existir antes las retros de cada user story.

### Plantilla - retrospectiva de user story

```
Genera una retrospectiva de la User Story <N>. Apoyate en progress/Decisions.md,
progress/History.md, progress/Blockers.md y progress/Current.md, y en el diff
entre lo planeado (plan.md/tasks.md) y lo realmente implementado. Estructura:
- Que salio segun lo previsto
- Que se desvio del plan y por que
- Decisiones tomadas sobre la marcha y su impacto
- Impedimentos encontrados y como se resolvieron
- Aprendizajes para las siguientes user stories (o para el cierre, si es la ultima)
Escribe el resultado en progress/Retrospectives.md (append, con cabecera
"## <fecha> — User Story <N>: <titulo>").
```

### Plantilla - retrospectiva de cierre de feature

```
Precondicion: todas las tareas de tasks.md en [x] (incluida Polish) y existen las
retros por user story en progress/Retrospectives.md.
Genera la retrospectiva final de cierre de la feature <id>. NO repitas las retros
por user story; sintetizalas y centrate en lo que solo es visible con la feature
completa. Apoyate en: las retros de US ya escritas, todo progress/ (Decisions,
History, Blockers, Historico_versiones) y el contraste entre constitution.md,
plan.md y lo realmente implementado. Estructura:
- Sintesis de las retros de US: patrones comunes y aprendizajes repetidos
- Cumplimiento global de la constitution: repasa cada principio MUST de punta a
  punta (cuenta los principios desde constitution.md; no asumas un numero fijo)
- Evaluacion de la decision arquitectonica central: vista con todo terminado,
  ¿fue acertada? ¿coste acumulado real?
- Impedimentos recurrentes a nivel de feature
- Aprendizajes para futuras features y proyectos (que llevar a la siguiente
  constitution/plan)
Escribe el resultado en progress/Retrospectives.md (append, con cabecera
"## <fecha> — RETRO DE CIERRE — feature <id>").
```
