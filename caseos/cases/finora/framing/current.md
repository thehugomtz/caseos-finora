# CURRENT FRAMING
> Versión 3 · actualizado 2026-09-29T00:26

## Executive Question
¿Qué explicaciones podemos defender ante el CRO y el CFO con los datos disponibles, qué sigue siendo solo una posibilidad y qué información permitiría elegir entre ellas?

## Hugo's Current Thinking
- “Lámina 1: las relaciones que te comenté” (Q-024)
- “¿Qué pasa si su suscripción creció de 100 a 130, pero tiene un descuento de 30 y sigue pagando 100? / Si un cliente pagaba 100 y ahora paga 80, ¿contrajo 20 o recibió un descuento? / ¿Y cuando desaparezca el descuento, eso cuenta como expansión?” (Q-025)
- “Inversión en Generación de Demanda para ToFu (Paid Media y Publicidad no web) / Team + Payroll Expenses + Travel / Habilitación ¿producto tal vez? (Software Tools + Freelance)” (N-023)
- “Entradas y Actividad económica de los clientes y de diferentes segmentos” (N-022)
- “No es posible determinar las métricas actuales, pero típicamente pensaría en abordar estos frameworks de Growth (MRR, ARR, ARPU, CAC, LTV, Churn, UCM)” (N-025)
- “¿Cómo separarías el valor de la suscripción del precio efectivamente pagado? ¿Qué campos, tablas o definiciones agregarías? → Propuesta de Modelo de datos / ¿Cómo clasificarías el inicio y el fin de un descuento…? También entra dentro de Propuesta de Modelo de datos” (N-029)
- “Revisar Data observable de pricing y comportamiento actual, observaciones generales // Finora quiere introducir descuentos temporales, ¿cómo debería de hacerlo? Mecanismo Propuesto / Implicaciones Multidisciplinarias” (N-028)
- “Assisted / Self Service / Executive” (N-024)
- “Decision Making” (N-027)
- “Por lo que se puede observar tienen un problema” (N-026)
- “el storytelling lo visualizo más o menos así: Sección 1 Overview… Sección 2 Growth… Revenue…” (N-021)
- “Finora crece mucho más en clientes (4,5×) que en ingreso (2,8×): el MRR por cliente activo cayó 38%, de COP 92,8 mil a COP 57,8 mil.” (N-020)

## Structured Interpretation
- **Q-024** ¿Qué relaciones van en la Lámina 1 de Growth? No están registradas en el caso y el brief también las marca «por precisar».
- **Q-025** Tres casos donde el pago observado no alcanza: una expansión compensada por descuento (100→130 con −30, y sigue pagando 100), contracción vs descuento (100→80) y fin de descuento vs expansión.
- **N-023** Agrupar el gasto de Marketing en tres bloques: generación de demanda ToFu (Paid Media + Publicidad no web), equipo (Payroll Expenses + Travel) y habilitación (Software Tools + Freelance). Queda abierta la duda de si habilitación es en realidad gasto de producto.
- **N-022** Lámina 2 de Growth: describir los primeros pagadores observados y su actividad económica (monto pagado) por segmento. Con los datos disponibles, el único segmento es industria.
- **N-025** Como no se conocen las métricas actuales de Finora, proponer métricas que hoy no existen partiendo de MRR, ARR, ARPU, CAC, LTV, Churn y UCM.
- **N-029** Una propuesta de modelo de datos que resuelva dos cosas: separar el valor de la suscripción del precio efectivamente pagado (campos, tablas, definiciones) y clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales.
- **N-028** Sección Revenue: primero, lo observable de pricing y comportamiento actual en los pagos; después, cómo introducir descuentos temporales (mecanismo propuesto) y sus implicaciones multidisciplinarias.
- **N-024** La Lámina 3 supone que Finora tiene tres motions distinguibles y que cada lead o cliente se puede asignar a una. El caso respalda self-service y proceso comercial asistido; «Executive» no aparece como ruta propia.
- **N-027** No sabemos qué decisiones quiere tomar el CRO con el funnel. La columna «Decision Making» de la solución está vacía.
- **N-026** Hugo lee que Finora tiene un problema de instrumentación comercial y digital (CRM y analítica).
- **N-021** Material de soporte en tres secciones: Overview (salud general que introduce lo demás) → Growth (L1 relaciones; L2 entradas, actividad económica y gasto; L3 funnel por motion; L4 concentración, hipótesis y solución analítica) → Revenue (pricing observable, mecanismo de descuentos, preguntas del CFO, modelo de datos).
- **N-020** Entre dos periodos aún sin fijar, los clientes activos observados crecen 4,5× y el monto pagado 2,8×. El monto pagado por cliente activo baja ~38% (≈COP 92,8 mil → 57,8 mil). Las tres cifras son una sola observación: el −38% sale de 2,8/4,5 ≈ 0,62.

## Facts
_—_

## Observations
- **N-004** U05 · Primera aparición como cliente nuevo _(propuesto)_
- **N-005** U08 · Self-serve, SQL directo y semanas estancado _(propuesto)_
- **N-011** U15 · Tu Parte 3 _(propuesto)_
- **N-020** Entre dos periodos aún sin fijar, los clientes activos observados crecen 4,5× y el monto pagado 2,8×. El monto pagado por cliente activo baja ~38% (≈COP 92,8 mil → 57,8 mil). Las tres cifras son una sola observación: el −38% sale de 2,8/4,5 ≈ 0,62. _(propuesto)_

## Hugo's Intuitions
- **N-001** U01 · Dos problemas conectados _(propuesto)_
- **N-003** U04 · Entraron muchos leads no calificados _(propuesto)_
- **N-026** Hugo lee que Finora tiene un problema de instrumentación comercial y digital (CRM y analítica). _(propuesto)_

## Assumptions
- **N-024** La Lámina 3 supone que Finora tiene tres motions distinguibles y que cada lead o cliente se puede asignar a una. El caso respalda self-service y proceso comercial asistido; «Executive» no aparece como ruta propia. _(propuesto)_

## Hypotheses
- **H-001** New creció, pero otras entradas bajaron. Entonces el total de personas que podrían comprar no creció tanto como parecía. _(propuesto)_
  - _Se debilita si:_ Si el total crece menos, corregimos la magnitud de la premisa. Si crece como esperaba el CRO, dejamos de usar falta de demanda total como explicación de la menor proporción que compra.
- **H-002** Aumentó la proporción de personas que históricamente compran menos o tardan más en hacerlo. _(propuesto)_
  - _Se debilita si:_ Si la mezcla nueva con el comportamiento habitual de cada grupo explica la diferencia, esa lectura gana fuerza. Si queda una diferencia dentro de grupos, pasamos a C3.
- **H-003** Hay más entradas recientes que todavía no tuvieron la misma oportunidad de comprar. _(propuesto)_
  - _Se debilita si:_ Si al igualar tiempo y perfil desaparece la diferencia, la juventud del grupo es una explicación compatible. Si no desaparece, «sólo necesitan más tiempo» deja de ser suficiente.
- **H-004** HC3a: al principio compran menos, pero después alcanzan un resultado parecido. HC3b: la diferencia sigue existiendo incluso con más seguimiento comparable. _(propuesto)_
  - _Se debilita si:_ Si se recupera, pierde fuerza la explicación de una caída persistente en ese periodo. Si no se recupera, el retraso pierde fuerza como explicación suficiente; aun así no demuestra que esas personas nunca comprarán.
- **H-005** Bajó la calidad de lo que genera la máquina de leads: al entrar, muestran menos necesidad, intención o ajuste. Es H-005 en palabras de Hugo. _(propuesto)_
  - _Se debilita si:_ Se debilita si las señales al entrar, medidas con el mismo criterio, no empeoraron. La opinión posterior de Sales no basta.
- **H-006** El volumen de entradas superó la capacidad instalada de SDRs y AEs, así que la atención se demora y la compra cae. Es H-006 con un mecanismo concreto: la capacidad. _(propuesto)_
  - _Se debilita si:_ Se debilita si la carga por SDR/AE no subió cuando creció New, si los tiempos a primer contacto no empeoraron o si la compra cae igual en las entradas atendidas a tiempo.
- **H-007** Con entradas y avance previo comparables, el deterioro aparece después de un punto del recorrido. _(propuesto)_
  - _Se debilita si:_ Si el tramo posterior está estable, esa ubicación pierde fuerza. Si cae, sabemos dónde mirar, no necesariamente por qué ocurre.
- **H-008** Cambios de producto, precio, condiciones o alternativas afectan la elección aunque intención inicial y atención sean parecidas. _(propuesto)_
  - _Se debilita si:_ Si no hay señales que lo sostengan, no dedicar tiempo a investigar el mercado en general. Si aparecen, precisar una pregunta externa concreta.
- **H-009** Entraron más o menos clientes, o entraron con suscripciones o tarifas distintas. _(propuesto)_
  - _Se debilita si:_ Si el valor antes de descuentos cambia, revisar cantidad, características y tarifa. Si ese valor no cambia pero el pago sí, mirar descuento o diferencia entre cobro y suscripción.
- **H-010** Hay descuentos documentados al entrar y cambió cuánto reducen el precio. _(propuesto)_
  - _Se debilita si:_ Si se documenta un descuento, puede investigarse su aporte. Si se confirma que no hubo, descartamos esa explicación histórica. No tener el campo no demuestra que no hubo descuentos.
- **H-011** Salieron más clientes o salieron clientes que aportaban más antes de descuentos. _(propuesto)_
  - _Se debilita si:_ Si terminó la relación, se sostiene hablar de salida. Si el cliente sigue activo, hay que retirar esa etiqueta aunque no haya pago observado.
- **H-012** Los clientes que salen ya pagaban menos por descuentos; el ingreso que desaparece es distinto del valor sin descuento. _(propuesto)_
  - _Se debilita si:_ Si se confirma, ese descuento pertenece al cálculo de esa salida. No se cuenta como fin de descuento de un cliente que permanece.
- **H-013** Cambió plan, cantidad, características o uso, manteniendo condiciones de tarifa comparables. _(propuesto)_
  - _Se debilita si:_ Cambio de uso o plan con tarifa comparable apoya esta explicación. Configuración estable la debilita.
- **H-014** La empresa cambió la tarifa aplicable a una suscripción comparable. _(propuesto)_
  - _Se debilita si:_ Tarifa distinta con características comparables apoya precio. Tarifa estable lo debilita.
- **H-015** El descuento empezó, aumentó, se redujo o terminó, cambiando el pago o compensando un cambio de suscripción. _(propuesto)_
  - _Se debilita si:_ Descuento distinto con suscripción estable apunta a ese componente comercial. Sin datos de descuento, no elegir una explicación por la forma del pago.
- **H-016** Al menos dos situaciones importantes para el CFO podrían producir el mismo pago observado. _(propuesto)_
  - _Se debilita si:_ Si hay al menos un contraejemplo relevante, la observación no identifica esa distinción. Si existen otros campos que lo resuelven, se corrige el planteamiento. Nada de esto prueba descuentos históricos.
- **H-017** Las definiciones y los datos permiten comparar montos y primeras apariciones sin distorsiones importantes. _(propuesto)_
  - _Se debilita si:_ Si hay contradicciones, ajustar los nombres y el alcance antes de interpretar. Si no sabemos que es MRR, llamarlo monto observado.
- **H-018** Se observa un cambio entre periodos comparables. _(propuesto)_
  - _Se debilita si:_ Cambio que se sostiene apoya describir un cambio de pagadores. Si desaparece al corregir datos, se retira esa lectura.
- **H-019** Una parte de los grupos explica buena parte del cambio observado. _(propuesto)_
  - _Se debilita si:_ Si hay concentración respaldada, enfocar ahí las siguientes preguntas. Si no, no fabricar grupos para forzar una historia.
- **H-020** El cambio se concentra en uno o varios de esos componentes observados. _(propuesto)_
  - _Se debilita si:_ Si no suma, corregir antes de interpretar. Si se compensan, no decir que no pasó nada porque el neto sea pequeño.
- **H-021** Los grupos que empezaron a pagar en distintos momentos difieren en sus pagos posteriores. _(propuesto)_
  - _Se debilita si:_ Si la diferencia persiste en una comparación justa, puede matizar la lectura económica. Si no hay seguimiento comparable, no concluir deterioro.
- **H-022** Gasto agregado y resultados pagados evolucionan de forma diferente. _(propuesto)_
  - _Se debilita si:_ Si no añade una conclusión que cambie la historia, dejarlo fuera. Si divergen, sólo describirlo, sin atribuir el resultado al gasto.

## Open Questions
- **Q-001** ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción? _(propuesto)_
- **Q-002** ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos? _(propuesto)_
- **Q-003** ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente? _(propuesto)_
- **Q-004** ¿Realmente aumentó igual la entrada total? _(propuesto)_
- **Q-005** ¿Cambió la gente que entra o el tiempo que ha tenido para comprar? _(propuesto)_
- **Q-006** ¿Personas similares están comprando menos o comprando más tarde? _(propuesto)_
- **Q-007** ¿Cuánto aportan los clientes que entran? _(propuesto)_
- **Q-008** ¿Cuánto dejan de aportar los clientes que salen? _(propuesto)_
- **Q-009** ¿Qué cambió en quienes permanecen? _(propuesto)_
- **Q-010** ¿Qué podemos nombrar y comparar válidamente? _(propuesto)_
- **Q-011** ¿El monto identifica los escenarios del CFO? _(propuesto)_
- **Q-012** ¿Qué cambió en los primeros pagadores observados? _(propuesto)_
- **Q-013** ¿Dónde se concentra el cambio del monto observado? _(propuesto)_
- **Q-014** ¿En qué segmentos se concentra la pérdida de crecimiento? Con los datos disponibles solo se puede mirar por industria y sobre pagadores observados; no sobre leads ni por canal. _(propuesto)_
- **Q-015** ¿Cambió la economía posterior de los nuevos pagadores? _(propuesto)_
- **Q-016** ¿Qué evidencia mínima permitiría distinguir las explicaciones del CRO? _(propuesto)_
- **Q-017** ¿Qué distinguiría los componentes del valor y la pertenencia recurrente? _(propuesto)_
- **Q-018** ¿Qué relación entre el gasto de Marketing por categoría y los nuevos pagadores o el monto pagado se puede describir cruzando fechas, y hasta dónde llega (asociación, no efecto)? _(propuesto)_
- **Q-019** ¿Qué cambió en la respuesta y qué sigue abierto? (volver a las hipótesis y escribir qué aprendimos) _(propuesto)_
- **Q-020** U02 · ¿Qué cambió y desde cuándo? _(propuesto)_
- **Q-021** U06 · Demanda, calidad, atención y post-SQL _(propuesto)_
- **Q-022** U07 · ¿La data actual da alguna pista? _(propuesto)_
- **Q-023** U12 · ¿Validar implica experimentos? _(propuesto)_
- **Q-024** ¿Qué relaciones van en la Lámina 1 de Growth? No están registradas en el caso y el brief también las marca «por precisar». _(propuesto)_
- **Q-025** Tres casos donde el pago observado no alcanza: una expansión compensada por descuento (100→130 con −30, y sigue pagando 100), contracción vs descuento (100→80) y fin de descuento vs expansión. _(propuesto)_

## Unknowns
- **N-013** Qué contamos como una persona o cuenta que entra. Un contacto, usuario, oportunidad y cliente no son necesariamente la misma unidad. _(propuesto)_
- **N-014** Qué entiende el CRO por adquirir un cliente: cerrar una venta, primer pago o suscripción activa. _(propuesto)_
- **N-015** Si primera transacción realmente significa cliente nuevo y si la historia y los IDs lo permiten. _(propuesto)_
- **N-016** Si el monto representa suscripción recurrente, facturación o cobro; y a qué periodo pertenece. _(propuesto)_
- **N-017** Si los meses están completos y la escala de Transactions ya fue multiplicada por 10.000 para llegar a COP. _(propuesto)_
- **N-018** Si Industry describe la industria actual o la de entonces, y qué clientes no tienen clasificación. _(propuesto)_
- **N-019** Si un resultado neto estable esconde aumentos y caídas que se compensan. _(propuesto)_
- **N-027** No sabemos qué decisiones quiere tomar el CRO con el funnel. La columna «Decision Making» de la solución está vacía. _(propuesto)_

## Proposals
- **N-002** U03 · Separar lo comercial del revenue _(propuesto)_
- **N-006** U09 · Primero ordenar canales, después medir _(propuesto)_
- **N-007** U10 · Agrupar clientes por pagos, churn y gasto _(propuesto)_
- **N-008** U11 · Trato analítico distinto por segmento _(propuesto)_
- **N-009** U13 · La herramienta ya construida _(propuesto)_
- **N-010** U14 · Antes, definiciones y fuentes claras _(propuesto)_
- **N-012** U16 · Tus pedidos posteriores _(propuesto)_
- **N-021** Material de soporte en tres secciones: Overview (salud general que introduce lo demás) → Growth (L1 relaciones; L2 entradas, actividad económica y gasto; L3 funnel por motion; L4 concentración, hipótesis y solución analítica) → Revenue (pricing observable, mecanismo de descuentos, preguntas del CFO, modelo de datos). _(propuesto)_
- **N-022** Lámina 2 de Growth: describir los primeros pagadores observados y su actividad económica (monto pagado) por segmento. Con los datos disponibles, el único segmento es industria. _(propuesto)_
- **N-023** Agrupar el gasto de Marketing en tres bloques: generación de demanda ToFu (Paid Media + Publicidad no web), equipo (Payroll Expenses + Travel) y habilitación (Software Tools + Freelance). Queda abierta la duda de si habilitación es en realidad gasto de producto. _(propuesto)_
- **N-025** Como no se conocen las métricas actuales de Finora, proponer métricas que hoy no existen partiendo de MRR, ARR, ARPU, CAC, LTV, Churn y UCM. _(propuesto)_
- **N-028** Sección Revenue: primero, lo observable de pricing y comportamiento actual en los pagos; después, cómo introducir descuentos temporales (mecanismo propuesto) y sus implicaciones multidisciplinarias. _(propuesto)_
- **N-029** Una propuesta de modelo de datos que resuelva dos cosas: separar el valor de la suscripción del precio efectivamente pagado (campos, tablas, definiciones) y clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales. _(propuesto)_

## Candidate Frames
- **CRO por cuánto entra, quién entra y cómo compra con el tiempo** ✓ elegido — Incluye rutas distintas sin asumir que sabemos quién comprará en el futuro. C1, C2 y C3.
  - _Cuándo gana:_ Es el corte elegido.
- **CFO por clientes que entran / salen / permanecen** ✓ elegido — Evita contar la misma cuenta en dos grupos entre las mismas fechas; dentro de cada grupo distinguimos suscripción y descuento.
  - _Cuándo gana:_ Es el corte elegido.
- **CRO por etapas comerciales** — Dónde se detiene el avance cuando sí hay historial de etapas.
  - _Cuándo gana:_ No sirve igual para self-serve ni entradas directas; las etapas quedan como lugar donde investigar dentro de C3.
- **CFO por comportamiento / precio / descuentos** — Se parece a la pregunta del ejecutivo.
  - _Cuándo gana:_ No separa causas limpiamente: un precio o descuento puede cambiar el comportamiento. Se investigan dentro de los grupos.

## Initial Storyline
- Situación (Overview): Finora suma clientes mucho más rápido que monto pagado (4,5× vs 2,8×; ~−38% por cliente activo, periodo por fijar). Esa brecha abre Growth y Revenue.
- Growth, lo que sí vemos: los primeros pagadores observados y su actividad económica por industria, y el gasto de Marketing por categoría en el tiempo, descritos sin atribuir ventas al gasto.
- Growth, lo que no vemos: no todos recorren el funnel igual (propuesta: Assisted, Self Service, Executive). Demanda, calidad, capacidad/atención y post-SQL quedan como explicaciones a contrastar, cada una con el dato que permitiría elegir.
- Growth, cómo operarlo: primero definiciones y fuentes comunes; después, seguimiento recurrente por foros (dashboards, análisis ad hoc, agentes), atado a decisiones del CRO que aún no están definidas.
- Revenue: con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento). Proponemos cómo introducir descuentos temporales y un modelo de datos que separe el valor de la suscripción del precio pagado.
- Qué tan seguros estamos y qué cambiaría: la separación de preguntas es defendible bajo las definiciones que explicamos. Para elegir causas faltan eventos de entradas y compras, y datos separados de suscripción, tarifa y descuento.

## Research Needed
- {'id': 'RN-W6', 'question': '¿Qué información mínima falta para contestar al CRO (entradas únicas con fecha, señales iniciales, recorrido, atención, vínculo con pago)?', 'why': 'HC1–HC3 tienen capacidad 0 con los datos actuales: sin esto la respuesta al CRO queda como propuesta.', 'links': ['Q-016', 'H-001', 'H-002', 'H-003'], 'status': 'pending', 'proposed_by': 'import (brief v0.3 W6)'}
- {'id': 'RN-W7', 'question': '¿Qué evidencia confirmaría vigencia, características contratadas, tarifa y descuento aplicado?', 'why': 'HF1–HF3 tienen capacidad 0: sin componentes explícitos no se separa suscripción, tarifa y descuento.', 'links': ['Q-017', 'H-009', 'H-010', 'H-011'], 'status': 'pending', 'proposed_by': 'import (brief v0.3 W7)'}
- {'id': 'RN-5eff9f', 'question': '¿Qué periodo, meses completos, escala a COP y definición de cliente activo están detrás del 4,5×, el 2,8× y el −38% del Overview?', 'why': 'Es el titular que abre toda la historia: si cambian el periodo o la definición, cambia la magnitud y quizá el mensaje.', 'links': ['H-017', 'H-018', 'N-016', 'N-017'], 'status': 'pending', 'proposed_by': 'framer', 'at': '2026-09-29T00:26:18-06:00'}
- {'id': 'RN-66535e', 'question': '¿Qué documenta el archivo de gasto de Marketing (unidad, moneda y periodo por categoría)? ¿Software Tools + Freelance es gasto de Marketing o de producto?', 'why': 'Decide si la Lámina 2 puede agrupar el gasto en los tres bloques de Hugo y cruzarlo por fechas con los nuevos pagadores, o si solo describe tendencias por separado.', 'links': ['H-022', 'Q-018'], 'status': 'pending', 'proposed_by': 'framer', 'at': '2026-09-29T00:26:18-06:00'}
- {'id': 'RN-86a650', 'question': '¿Qué dato mínimo separaría una capacidad comercial insuficiente de una caída de calidad: la carga por SDR/AE y el tiempo a primer contacto por cohorte de entrada, frente a las señales de ajuste al entrar?', 'why': 'Son las dos hipótesis de la Lámina 4 y llevan a acciones distintas: sumar o reasignar capacidad, o cambiar cómo se generan los leads.', 'links': ['H-005', 'H-006', 'Q-016', 'Q-021'], 'status': 'pending', 'proposed_by': 'framer', 'at': '2026-09-29T00:26:18-06:00'}

## Decisions Needed
- Qué unidad cuenta como entrada (contacto, usuario, oportunidad o cliente).
- Qué significa adquirir un cliente para el CRO: cerrar una venta, primer pago o suscripción activa.
- Qué es «Executive» en la Lámina 3: la ruta de entrada directa a SQL o un segmento de cuentas con KAM. Define si las columnas separan cómo compra el cliente o quién es.
- Qué decisiones del CRO asumimos explícitamente para la columna «Decision Making», dado que el caso no las define.

## Things We Should Not Claim Yet
- Que el monto sea MRR contratado: mientras la recurrencia no se confirme, se habla de monto pagado observado.
- Que la primera transacción sea la adquisición del cliente: mientras la historia no se confirme, es la primera aparición observada.
- Que una comparación sin cobertura completa describa al negocio: se detiene esa comparación.
- Que hubo descuentos en el histórico: el caso habla de introducirlos.
- Que una simulación de escenarios describe lo que ocurrió: prueba qué se puede distinguir, no qué pasó.
- Nada sobre conversión de leads o del funnel: los pagos no incluyen a quien no compró.
- Que la primera aparición sea el hito de adquisición del CRO (Won, primer pago o suscripción activa siguen por acordar).
- Etiquetas contractuales (alta, baja o expansión de suscripción) sin vigencia verificada.
- Descuentos a partir del tamaño de un salto del monto.
- Una lectura del puente si las contribuciones no concilian con el total.
- Una causa industrial, un canal o una fase del recorrido: la industria es una segmentación disponible, no un sustituto de canal o ruta.
- Un segmento fabricado por clustering cuando no hay concentración clara.
- La calidad de los leads a partir de lo que pasa después del pago.
- Retención contractual a partir de la continuidad de pago.
- Que Finora «tiene un problema» de CRM o analítica digital: que los datos del caso no traigan canal ni etapas no prueba que Finora no los registre.
- Valores de LTV o UCM (no hay margen ni costo por cliente) ni de CAC por canal (no hay canal). Un CAC combinado depende de documentar la unidad del gasto y de acordar qué es adquirir un cliente.
- Que una categoría de gasto (ToFu, Team, Habilitación) generó ventas porque las dos series se mueven en las mismas fechas.
- Que el ~−38% por cliente activo sea deterioro de la salud del negocio: todavía no separamos la mezcla de quienes entran, el precio y las salidas.

## Language Notes
- Hugo usa «monto observado» y «primer pagador observado» en lugar de MRR y cliente nuevo mientras la semántica no esté confirmada.
- Términos en inglés que Hugo usa tal cual: leads, funnel, churn, self-serve, SQL, MRR.
- Overview: «MRR pagado por cliente activo» (o «monto pagado por cliente activo») en lugar de «MRR» a secas; es el ARPU observado de Hugo.
- «Entradas» en la Lámina 2 = primeros pagadores observados; «entradas» y «leads» del funnel quedan para L3–L4.
- «Executive» se puede confundir con Account Executive (el rol que entra después de SQL en el caso), y «KAM» no aparece en el caso, que habla de SDRs y AEs. Conservar los términos de Hugo y definirlos en la lámina.
- «Foros» = espacios recurrentes donde se toman decisiones (p. ej., la revisión comercial semanal); se conserva el término.
