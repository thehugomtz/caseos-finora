# Brief — Finora Business Analytics Case

## Objetivo
Responder a Finora en tres bloques, con datos solo donde realmente ayudan: (1) Overview — entender la salud general del modelo y qué señales tener en mente antes de entrar a Growth y Revenue; (2) Growth / CRO — cómo definir y medir el funnel si no todos los clientes lo recorren igual, qué hipótesis podrían explicar “más leads, pero no más ventas” (qué sostiene la data, qué sigue siendo posibilidad y qué dato permitiría elegir) y qué solución analítica le permitiría al CRO operar el funnel de forma recurrente y qué decisiones tomar con ella; (3) Revenue / CFO — cómo introducir descuentos temporales sin que el MRR confunda comportamiento del cliente con decisiones comerciales: mecanismo, modelo de datos y clasificación correcta de los movimientos.

## Audiencia
- CEO — contexto de salud general del modelo (Overview) antes de Growth y Revenue; qué decide no está definido
- CRO — cómo definir, medir y operar de forma recurrente el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos
- CFO — cómo introducir descuentos temporales sin perder la respuesta a “¿por qué cambió nuestro MRR?”: mecanismo, modelo de datos y clasificación

## Contexto
Finora cobra suscripciones mensuales y opera con un modelo híbrido: algunos usuarios llegan directo al producto, se registran, lo usan y pagan sin necesariamente hablar con ventas; otros entran al proceso comercial por campañas, referidos, partners o prospección. Overview: Finora crece mucho más en clientes que en ingreso — clientes 4.5x, ingreso / MRR pagado 2.8x y MRR por cliente activo −38% (de ~COP 92.8 mil a ~COP 57.8 mil); el periodo de estas cifras sigue sin fijar. Growth / CRO: Finora plantea algo como “estamos generando más leads, pero no estamos vendiendo más”; el volumen en primeras etapas creció, sobre todo en New, pero los clientes nuevos no crecen al mismo ritmo. Funnel aproximado: New → Working → Engaged → SQL → Demo → Proposal → Won; los SDRs trabajan sobre todo las primeras etapas y después normalmente entra un Account Executive. No todos lo recorren igual: hay self-service, entradas directas a SQL, leads estancados semanas en alguna etapa y distintos canales o motions. La pregunta del caso toca demanda, calidad, velocidad de atención y conversión post-SQL. Revenue / CFO: la pregunta principal es “¿por qué cambió nuestro MRR?”. El valor de la suscripción puede cambiar según uso y características del cliente; hoy el histórico es cliente + mes + monto pagado y los cambios entre meses se clasifican como crecimiento, contracción, churn o reactivación. Con descuentos temporales ese modelo puede confundir comportamiento del cliente con decisiones comerciales (precio, descuentos): 100 → 80, ¿contrajo 20 o recibió 20 de descuento?; si la suscripción sube de 100 a 130 con 30 de descuento, sigue pagando 100 y el monto observado no muestra el crecimiento; cuando termina el descuento pasa de 100 a 130 pagado, ¿cuenta como expansión?

## Entregables
- Presentación ejecutiva ≤ 5 min para CEO, CRO y CFO: Situación → Hallazgo → Implicación → Decisión → Acción
- Material de soporte (propuesto, no final) · 1 Overview — observaciones generales y salud del negocio que introducen las secciones siguientes (p. ej. clientes 4,5× vs ingreso 2,8×; MRR por cliente activo −38%).
- Material de soporte (propuesto, no final)· 2 Growth — L1: las relaciones que comentó Hugo (por precisar). L2: entradas y actividad económica de clientes y segmentos; inversión de S&M por categoría (generación de demanda ToFu: Paid Media y publicidad no web · Team: Payroll Expenses y Travel · habilitación, ¿producto?: Software Tools y Freelance) y hasta dónde se puede relacionar con ventas cruzando fechas. L3: cómo definir y medir el funnel si no todos lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas): Assisted / Self Service / Executive, con canales (incl. digital, WoM, clientes que no requirieron KAM), funnel propuesto, AAARRR, conversion rate y métricas clave. L4: dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix; quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco volumen). L5: qué métricas propondrías que hoy no existen (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) y cómo medirlas. L6: hipótesis ToFu y BoFu (demanda, calidad, velocidad de atención, conversión post-SQL; p. ej. la capacidad comercial instalada no alcanza la demanda generada, la calidad de la máquina de leads bajó) y qué datos validan o descartan cada una. L7: solución analítica para que el CRO opere el funnel de forma recurrente y qué decisiones le permite tomar (técnica: pulir CRM, analítica digital · decision making: dashboards automatizados por foro, análisis ad hoc, agentes de IA).
- Material de soporte (propuesto, no final)· 3 Revenue — L1: qué data observable de pricing introductorio podemos sacar. L2: cómo debería Finora introducir descuentos temporales (mecanismo propuesto, implicaciones multidisciplinarias, preguntas del CFO contestadas con el modelo propuesto). L3: cómo separar el valor de la suscripción del precio efectivamente pagado: propuesta de modelo de datos (campos, tablas, definiciones). L4: cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales (Hugo: probablemente lo integra la misma propuesta de modelo de datos).
- Nota corta: prioridades, supuestos, información faltante, cambios al modelo, cómo se usó y validó la IA

## Restricciones
- No vamos a llamar “causa” a algo que sólo muestra una asociación.
- No hay datos de funnel: lo que pasa entre New y Won (etapas, canales, tipo de recorrido, velocidad de atención, conversión post-SQL) se responde como propuesta de medición, no como diagnóstico. Lo observable desde el primer pago (altas, churn, ticket, industria, mix) y el cruce por fechas con el gasto de S&M sí se puede diagnosticar, como asociación. (ajuste sobre notas del proyecto)
- Solución fuera de esta etapa: el esqueleto de láminas es storyline provisional; no construimos dashboards, métricas definitivas, modelo de datos ni deck final hasta que se decida.

## Criterios de éxito
- Preguntas separadas sin contar lo mismo dos veces; hipótesis con una explicación alternativa; evidencia que ayude a distinguirlas; tareas que sepamos cuándo cerrar. (brief v0.3 §01)
- Los casos del CFO se contestan con el modelo propuesto, sin ambigüedad: (a) la suscripción sube de 100 a 130 con un descuento de 30 y el cliente sigue pagando 100; (b) un cliente pasa de pagar 100 a 80: ¿contrajo 20 o recibió un descuento?; (c) cuando el descuento desaparece, ¿cuenta como expansión?
- La solución para el CRO (Growth L7) dice qué decisiones le permite tomar cada pieza, no sólo qué muestra.

## Datos disponibles
- Modelo de datos: Finora · modelo analítico (finora-eda · Business Exploration Workspace) — Raw 3 · Staging 3 · Mart · procesado 7; 7/7 checks de reconciliación OK.
- raw.transactions — Pagos mensuales por cliente tal cual llegaron: ID, month (M/D/AAAA) y amount sin escala (66.674 filas; grano fila del archivo · cliente × mes)
- raw.industry — Industria de cada cliente («Cliente N» → industria), tal cual llegó (1.962 filas; grano fila del archivo · cliente)
- raw.sm_spend — Gasto mensual de Sales & Marketing por rubro, en texto con «$» (unidad no documentada) (34 filas; grano fila del archivo · mes)
- mart.customer_month — Panel analítico: monto observado, MRR pagado, banderas (alta, churn observado, reactivación, expansión, contracción), movimientos, tenure, cohorte y cosecha (66.674 filas; grano cliente × mes)
- mart.monthly_metrics — Las métricas mensuales recalculadas en SQL desde customer_month; cuadran al centavo con la Fase 1 (34 filas; grano mes)
- mart.new_customers — Cada alta con su primer pago (M0), run-rate temprano, cohorte e industria (1.584 filas; grano alta)

## Stakeholders y fuentes de contexto
- SDRs — trabajan principalmente las primeras etapas del funnel
- Account Executives — normalmente entran después de los SDRs
- Áreas que tocan los descuentos temporales: revenue, pricing, billing, data, reporting y comercial

## Tiempos
Sin fechas: esfuerzo relativo. Reparto aproximado: una parte de análisis para entender qué se observa hoy → bastante definición de frameworks, propuestas, diseño de medición y diseño de modelo de datos → storytelling.

## Vacíos de información
- Qué canales o motions de adquisición existen realmente y si algún dato permite saber por cuál entró cada cliente: los datos disponibles no traen canal.
- Datos de funnel y de capacidad comercial (etapa por lead, tiempo en etapa, capacidad de SDRs y AEs, tiempos de atención, backlog) no están en los datos disponibles; sin ellos, capacidad comercial y conversión post-SQL no se pueden probar directamente. El gasto en Team / Payroll Expenses / Travel sería, a lo mucho, un proxy en dinero.
- Qué métricas usa hoy Finora y qué decisiones quiere tomar el CRO con el funnel.
- Hasta dónde es válido relacionar la inversión en Marketing por categoría con clientes nuevos o ingreso cruzando fechas; la unidad del gasto sigue sin documentar.
- Los datos disponibles no traen margen ni costo por cliente: pesa si se proponen LTV o UCM.
- Qué tiene ya definido Finora sobre los descuentos temporales, o si el mecanismo se propone desde cero.

## Enunciado original
Desafío Técnico - Alegra

Business Analytics:
del dato a la decisión
⏱️ Tiempo de entrega: 5 días
🎯 Análisis + Decisión
"No buscamos una única respuesta correcta. Queremos ver cómo tomas problemas ambiguos, los estructuras y los conviertes en mejores decisiones."
¡Bienvenido/a!
Imagina que acabas de incorporarte al equipo de Business Analytics de Finora, una compañía SaaS colombiana que desarrolla software de gestión financiera y operativa para PyMEs.

Finora es una empresa AI First: espera que las personas utilicen IA de forma natural para investigar, analizar, construir, automatizar y trabajar mejor.

En este reto vas a enfrentar dos preguntas reales de negocio, una del CRO y otra del CFO. Queremos observar cómo conviertes:

Ambigüedad → estructura
Cuestionas definiciones y ordenas el problema antes de calcular.
Datos → explicaciones
Encuentras dónde se concentra el cambio y por qué ocurre.
Explicaciones → decisiones
Propones qué hacer y cómo operarlo de forma recurrente.
El escenario
Finora opera con un modelo híbrido. Algunos usuarios llegan al producto, se registran, lo usan y pagan sin hablar con ventas. Otros entran al proceso comercial por campañas, referidos, partners o prospección.

El funnel comercial hoy se ve así. Los SDRs trabajan las primeras etapas y luego normalmente entra un Account Executive:

New
Working
Engaged
SQL
Demo
Proposal
Won
Etapas SDR
Etapas Account Executive
Cierre
Casos de negocio
2
Funnel comercial (CRO) y movimientos de MRR (CFO)
Etapas del funnel
7
De New a Won, con entradas directas desde producto
Fuentes de datos
3
Transactions, S&M spend e Industry (incompletas a propósito)
Video ejecutivo
≤ 5 min
Para CEO, CRO y CFO
Dos preguntas en tensión
Cada caso viene de un líder distinto, con una preocupación distinta. Ambos comparten el mismo fondo: hoy Finora ve números, pero no los entiende lo suficiente para decidir.

Caso 1 · Crecimiento
"Estamos generando más leads, pero no estamos vendiendo más"
El volumen en las primeras etapas creció, especialmente en New, pero los clientes nuevos no crecen al mismo ritmo.

Lo pide: CRO
Caso 2 · Revenue
"¿Por qué cambió nuestro MRR?"
Llegan los descuentos temporales y el modelo actual podría confundir comportamiento del cliente con decisiones comerciales.

Lo pide: CFO
Reglas del juego
Puedes usar IA de manera libre en donde la consideres útil, solo recuerda compartirnos tu proceso.
El reto
Abre cada caso para ver el contexto completo y lo que esperamos.

01Caso 1 — El funnel
+
El CRO te cuenta
"Aumentamos bastante el volumen en las primeras etapas del funnel, especialmente en New, pero los clientes nuevos no están creciendo al mismo ritmo. Marketing dice que está trayendo más demanda. Sales dice que la calidad bajó. Otros creen que atendemos lento o que el problema está después de SQL.

Además, hay usuarios que pagan directamente desde producto, otros entran casi directo a SQL y otros pueden durar semanas en una etapa. Hoy vemos volúmenes y conversiones, pero no tenemos una lectura suficientemente clara de dónde estamos perdiendo crecimiento ni por qué."

Tu reto
Hazte owner analítico del problema. Muéstranos cómo analizarías el funnel y qué solución analítica construirías para que el CRO pueda entenderlo, tomar decisiones y operar regularmente.

Queremos ver cómo pasas de esto a esto:

"Working → Engaged cayó 3 puntos"
→
"Esto es lo que cambió, aquí se concentra, estas son las hipótesis y esto deberíamos hacer."
¿Cómo definirías y medirías el funnel si no todos los clientes lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas)?
¿Dónde y en qué segmentos se concentra la pérdida de crecimiento? ¿Qué métricas propondrías que hoy no existen?
¿Qué hipótesis explicarían el fenómeno (demanda, calidad, velocidad de atención, conversión post-SQL) y qué datos usarías para validar o descartar cada una?
¿Qué solución analítica construirías para que el CRO opere el funnel de forma recurrente, y qué decisiones le permitiría tomar?
02Caso 2 — El MRR
+
El CFO pregunta
"Si un cliente pagaba 100 y ahora paga 80, ¿contrajo 20 o recibió un descuento? ¿Qué pasa si su suscripción creció de 100 a 130, pero tiene un descuento de 30 y sigue pagando 100? ¿Y cuando desaparezca el descuento, eso cuenta como expansión?

Quiero saber qué está pasando con el negocio subyacente y cuánto revenue estamos dejando de capturar por decisiones comerciales."

Finora cobra suscripciones mensuales cuyo valor puede cambiar con el uso y características de cada cliente. Hoy existe un histórico con cliente + mes + monto pagado, y los cambios entre meses se usan para clasificar movimientos como crecimiento, contracción, churn o reactivación. Ahora Finora quiere introducir descuentos temporales.

Tu reto
Evalúa si el modelo actual permite responder bien estas preguntas. Si no, muéstranos cómo debería evolucionar. Puedes modificar la estructura de datos, crear nuevas definiciones o proponer otro modelo.

¿Qué puede y qué no puede responder el modelo actual (cliente + mes + monto pagado)?
¿Cómo separarías el valor de la suscripción del precio efectivamente pagado? ¿Qué campos, tablas o definiciones agregarías?
¿Cómo clasificarías el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales?
Al final queremos poder responder consistentemente
¿Por qué cambió nuestro MRR? y ¿cuánto del cambio corresponde al comportamiento del cliente y cuánto a pricing o descuentos?

03Información disponible
+
Estas son algunas de las fuentes disponibles en Finora:

Transactions.csv
Histórico mensual de ingresos por cliente. Multiplica los valores por 10.000 para obtener COP.

S&M_spend.csv
Gasto mensual de Sales & Marketing.

Industry.csv
Industria de cada cliente.

📂 Accede a las fuentes aquí: Carpeta de fuentes en Google Drive
Como en una empresa real, la información puede ser incompleta o ambigua. Detectar lo que no puede concluirse también hace parte del reto.
Entregables
①
Video ejecutivo (máximo 5 minutos)
Dirigido al CEO, CRO y CFO. Queremos una historia clara que conecte el análisis con el negocio (argumento de negocio) y muestre por qué tu enfoque es sólido (argumento técnico):

Situación
→
Hallazgo
→
Implicación
→
Decisión
→
Acción
②
Demo y video de proceso con IA (máximo 5 minutos)
Entrega una demo (link) y un video corto donde nos cuentes cómo trabajaste con la IA en este proyecto: qué herramientas usaste, el paso a paso, etc.

③
Material de soporte
Comparte los artefactos que consideres necesarios para respaldar tu análisis y tu propuesta. El formato es libre:

HTML
Dashboard
Spreadsheet
Notebook
SQL
Modelo de datos
Visualizaciones
Prototipos
④
Nota corta
Incluye brevemente:

Qué preguntas priorizaste.
Qué supuestos hiciste.
Qué información hizo falta.
Qué cambiarías del modelo actual.
Cómo usaste la IA, qué validaste y cómo aseguraste la calidad de tus conclusiones.
📎 ¿Cómo entregar? Adjunto al correo donde te enviamos este reto encontrarás un formulario para anexar los links y archivos de tus soluciones.
Libertad creativa: Puedes entregar anexos de lo que consideres relevante. Diagramas, queries, modelos, prototipos — lo que demuestre tu pensamiento.
No buscamos una única respuesta correcta.
Queremos ver cómo piensas.

Convierte la ambigüedad en estructura y los datos en decisiones. Mucho éxito.

## Fuentes
- Brief de trabajo v0.3 en lenguaje claro (fuente de verdad, 28-sep-2026)
- Brief v0.4 corto (archivo)
- Notas del proyecto (memoria de sesión de Claude, 27–28 sep 2026)
