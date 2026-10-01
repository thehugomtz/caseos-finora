# Cómo trabajé con IA en el caso Finora

**Los agentes hacen el trabajo; yo soy dueño del juicio.** Ninguna fase avanzó sola. Yo aprobé el planteamiento, acepté
o rechacé la evidencia, decidí entre alternativas, aprobé la historia y marqué cada fase como lista. Cuando delegué
algo, quedó registrado como delegación.

## Las herramientas

1. **Business Exploration Workspace (27–28 de septiembre).** Primero entender los datos:
   - **Fase 1.** Un pipeline reproducible recalcula todo desde los tres CSV de Finora.
   - **Capa agéntica.** Un agente investiga preguntas de negocio con SQL de solo lectura sobre DuckDB.
   - **Validador en código.** Revisa cada respuesta: que no haya cifras escritas a mano, ni lenguaje causal sin
     descomposición, y que cada conclusión tenga su gráfica. Hay 94 evaluaciones automáticas.
2. **CaseOS (28–30 de septiembre).** Un case room sobre el Claude Agent SDK.
   - **Agentes.** Briefer, Framer, un router de research, cuatro especialistas (Business Research, Measurement, Data
     Engineering y Analytics), un Chief of Staff y el Visual Storyteller.
   - **Compuertas.** Cada fase tiene compuertas que solo yo abro.
   - **Linaje.** Cada pieza conserva su linaje: pregunta → hipótesis → investigación → evidencia → decisión →
     afirmación → lámina.
   - **Validaciones en código.** Una cifra de la historia tiene que existir en una tabla. Una cita cuenta solo si su
     URL se recuperó en la corrida. Una cifra del modelo de datos cuenta solo si su consulta corrió.
3. **Executive Visual Storyteller.** Mis skills para decks ejecutivos en HTML. El flujo va de storyline a dirección
   visual, de ahí a la composición de cada lámina, luego al HTML y al final a un loop de QA con un crítico independiente.
   CaseOS las enlaza; no las reconstruye.
4. **Claude Code, con Opus 5.5, como constructor y coordinador.**
   - **Construyó.** Escribió el código de las herramientas, con pruebas: 87 en CaseOS y 94 evaluaciones en el
     workspace.
   - **Ejecutó lo que delegué.** Cuando le delegué la operación, ejecutó acciones en CaseOS a mi nombre: hay 25 en la
     bitácora, todas marcadas «vía Claude».
   - **Las delegaciones.** Son decisiones registradas: D-016 (armar y lanzar el plan de investigación), D-017
     (responder las 8 preguntas del caso), D-023 (aceptar la historia con su evidencia) y D-027 (aprobar la historia v4
     y lanzar el deck).

## Cómo avanzó el caso

| Fecha | Qué pasó |
|---|---|
| 27 sep | **EDA.** Fase 1 del workspace y la primera rebanada agéntica, con la pregunta dorada «¿Por qué disminuyó el MRR por cliente?». |
| 28 sep | **Workspace y CaseOS.** «Respuesta primero» y «Preparar narrativa» en el workspace. CaseOS construido y validado de punta a punta. Finora importado. |
| 29 sep | **Del brief al primer deck.** Briefing y Framing con sus agentes. Plan de investigación desde el guion de la historia. 36 investigaciones; el Chief of Staff evaluó cada una y abrió alertas. Story Package y deck v3. |
| 30 sep | **El deck de 5 minutos.** Revisé el deck (D-026: estructura para 5 minutos, ajustes hechos por los agentes) y salió el deck v5. Agregué un editor de láminas y los cambios puntuales del Storyteller. |

## Qué decidí yo

- **Decisiones.** Tomé 23 de las 29 del caso. Las que propusieron los agentes siguen como propuestas.
- **Evidencia.** Hay 155 hallazgos aceptados y 97 se quedaron por revisar. Los rechazados salen de la historia.
- **Estructura.** La historia (Overview → Growth → Revenue), mis definiciones de los funnels, qué entra al deck de 5
  minutos y la paleta.

## Qué cuidé que la IA no hiciera

- Inventar cifras o fuentes. El código bloquea la historia si una cifra no existe en una tabla.
- Avanzar fases o aceptar evidencia por su cuenta. En el código, solo `hugo` puede hacerlo.
- Mezclar hechos con intuiciones. El Framer separa nueve tipos (hecho, observación, intuición, supuesto, hipótesis,
  pregunta, propuesta, decisión, desconocido) y conserva mis palabras junto a la versión estructurada.

## En números

| | |
|---|---|
| Corridas de agentes de CaseOS | 70, con `claude-opus-5-5` en esfuerzo `max`: US$154 equivalentes |
| Corridas del Visual Storyteller | 2: US$28.7 el deck v3 y US$22.9 el v5, en 49 minutos |
| Corridas del agente de EDA | 27, con `claude-opus-5` |
| Eventos en la bitácora | más de 2,200 |
| Entidades del caso | 252 hallazgos, 109 tablas, 78 hipótesis, 110 preguntas, 36 investigaciones, 171 alertas, 29 decisiones y 29 afirmaciones |

Los costos son los que reporta el SDK. Con suscripción no se cobra por corrida. Cómo verificar cada número:
[EVIDENCIA.md](EVIDENCIA.md).
