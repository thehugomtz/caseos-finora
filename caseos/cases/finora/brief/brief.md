# Brief — Business Analytics: del dato a la decisión

## Objetivo
Entender qué explicaciones podríamos defender ante CRO y CFO, qué sigue siendo una posibilidad y qué información permitiría elegir entre ellas.

## Audiencia
CEO, CRO, CFO

## Contexto
Caso 1 · CRO: más volumen arriba del funnel (New → Working → Engaged → SQL → Demo → Proposal → Won, con entradas self-serve, entradas directas a SQL y leads estancados) sin que los clientes nuevos crezcan al mismo ritmo. Caso 2 · CFO: ¿el modelo cliente + mes + monto permite separar el comportamiento del cliente del precio y de los descuentos temporales que se van a introducir? El caso relata más entradas en primeras etapas y menor crecimiento relativo de clientes nuevos; también plantea introducir descuentos temporales. Todavía no fijamos el periodo ni el signo del cambio económico.

## Entregables
- Video ejecutivo ≤ 5 min para CEO, CRO y CFO: Situación → Hallazgo → Implicación → Decisión → Acción
- Link a la demo + video ≤ 5 min del proceso con IA
- Material de soporte
- Nota corta: prioridades, supuestos, información faltante, cambios al modelo, cómo se usó y validó la IA

## Restricciones
- El reto original da cinco días; no sabemos cuánto queda. Esfuerzo relativo, no fechas. (brief v0.3 §01)
- No vamos a llamar “causa” a algo que sólo muestra una asociación. (brief v0.3 §01)
- No hay datos de funnel: el Caso 1 se responde como propuesta de medición, no como diagnóstico. (notas del proyecto)
- Solución fuera de esta etapa: sin dashboards, métricas definitivas, modelo de datos ni deck hasta que se decida. (brief v0.3 §11)

## Datos disponibles
- Transactions.csv — cliente · mes · monto (COP)
- Industry.csv — industria del cliente
- S&M_spend.csv — gasto mensual por rubro (unidad sin documentar)
- Workspace de exploración (finora-eda) con el análisis de la Fase 1, 39 hallazgos canónicos verificados en código y respuestas W0–W5

## Criterios de éxito
- Preguntas separadas sin contar lo mismo dos veces; hipótesis con una explicación alternativa; evidencia que ayude a distinguirlas; tareas que sepamos cuándo cerrar. (brief v0.3 §01)

## Vacíos de información declarados
- El texto literal del enunciado de Alegra no está en el repositorio: este brief se reconstruyó desde las notas del proyecto (27-sep) y el brief v0.3. Pendiente adjuntar el enunciado original.
- Qué entiende el CRO por adquirir un cliente: cerrar una venta, primer pago o suscripción activa (sin fijar).
- Si el monto representa suscripción recurrente, facturación o cobro; y a qué periodo pertenece (sin confirmar).

## Fuentes
- Brief de trabajo v0.3 en lenguaje claro (fuente de verdad, 28-sep-2026)
- Brief v0.4 corto (archivo)
- Notas del proyecto (memoria de sesión de Claude, 27–28 sep 2026)
