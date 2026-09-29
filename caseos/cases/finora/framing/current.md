# FRAMING & SHAPING
> Versión 16 · actualizado 2026-09-29T10:31

## 1. Problema
Hay que definir nosotros diferentes propuestas de acuerdo a lo que se requiere, propuestas de medición, frameworks, etc.

**Situación.** La data actualmente no alcanza, debemos de responder en la medida de lo posible pero hay cosas que no y ahi es donde proponemos y lo dice textualmente el caso: Growth: ¿Cómo definirías y medirías el funnel si no todos los clientes lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas)?
¿Dónde y en qué segmentos se concentra la pérdida de crecimiento? (este si se podría investigar algo en la data) ¿Qué métricas propondrías que hoy no existen?
¿Qué hipótesis explicarían el fenómeno (demanda, calidad, velocidad de atención, conversión post-SQL) y qué datos usarías para validar o descartar cada una?
Revenue
Finora cobra suscripciones mensuales cuyo valor puede cambiar con el uso y características de cada cliente. Hoy existe un histórico con cliente + mes + monto pagado, y los cambios entre meses se usan para clasificar movimientos como crecimiento, contracción, churn o reactivación. Ahora Finora quiere introducir descuentos temporales.
Si un cliente pagaba 100 y ahora paga 80, ¿contrajo 20 o recibió un descuento? ¿Qué pasa si su suscripción creció de 100 a 130, pero tiene un descuento de 30 y sigue pagando 100? ¿Y cuando desaparezca el descuento, eso cuenta como expansión?

Quiero saber qué está pasando con el negocio subyacente y cuánto revenue estamos dejando de capturar por decisiones comerciales
¿Qué puede y qué no puede responder el modelo actual (cliente + mes + monto pagado)?
¿Cómo separarías el valor de la suscripción del precio efectivamente pagado? ¿Qué campos, tablas o definiciones agregarías?
¿Cómo clasificarías el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales?
Al final queremos poder responder consistentemente
¿Por qué cambió nuestro MRR? y ¿cuánto del cambio corresponde al comportamiento del cliente y cuánto a pricing o descuentos?

Mucho de eso se responde con propuestas por que no hay data

**Por qué importa.** Seguir presentando los mismos problemas que tenian, falta de visibilidad e incapacidad de tomar decisiones basadas en datos

**Dentro del alcance**
_—_

**Fuera del alcance (no-gos, rabbit holes)**
_—_

## 2. Pregunta ejecutiva
¿Qué explicaciones podemos defender ante el CRO y el CFO con los datos disponibles, qué huecos en su WoW y qué modelos se proponen para poder llegar a tomar mejores decisiones?

## 3. Guion de la historia
### S1 · Overview
_Situación (Overview): Finora suma clientes mucho más rápido que monto pagado (4,5× vs 2,8×; ~−38% por cliente activo, periodo por fijar). Esa brecha abre Growth y Revenue._

- **S1.1 Overview**
  - Debe mostrar: observaciones generales y salud del negocio que introducen las secciones siguientes (p. ej. clientes 4,5× vs ingreso 2,8×; MRR por cliente activo −38%)
  - Notas de Hugo: Migrado de Entregables del brief.

### S2 · Growth
_Growth, lo que sí vemos: los primeros pagadores observados y su actividad económica por industria, y el gasto de Marketing por categoría en el tiempo, descritos sin atribuir ventas al gasto._
_Growth, lo que no vemos: no todos recorren el funnel igual (propuesta: Assisted, Self Service, Executive). Demanda, calidad, capacidad/atención y post-SQL quedan como explicaciones a contrastar, cada una con el dato que permitiría elegir._
_Growth, cómo operarlo: primero definiciones y fuentes comunes; después, seguimiento recurrente por foros (dashboards, análisis ad hoc, agentes), atado a decisiones del CRO que aún no están definidas._

- **S2.1 Las relaciones que comentó Hugo**
  - Debe mostrar: las relaciones que comentó Hugo (por precisar)
  - Notas de Hugo: Migrado de Entregables del brief (L1).
- **S2.2 Entradas y actividad económica de clientes y segmentos**
  - Debe mostrar: Revisar entradas y actividad económica de clientes y segmentos; inversión de S&M por categoría (generación de demanda ToFu: Paid Media y publicidad no web · Team: Payroll Expenses y Travel · habilitación, ¿producto?: Software Tools y Freelance) y hasta dónde se puede relacionar con ventas cruzando fechas
  - Notas de Hugo: Migrado de Entregables del brief (L2).
- **S2.3 Cómo definir y medir el funnel si no todos lo recorren igual** — ¿Cómo definir y medir el funnel si no todos lo recorren igual?
  - Debe mostrar: cómo definir y medir el funnel si no todos lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas): Assisted / Self Service / Executive, con canales (incl. digital, WoM, clientes que no requirieron KAM), funnel propuesto, AAARRR, conversion rate y métricas clave, aqui se tiene que hacer un research alrededor del modelo de negocio y estructurar la propuesta
  - Notas de Hugo: Migrado de Entregables del brief (L3).
- **S2.4 Dónde y en qué segmentos se concentra la pérdida de crecimiento** — ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento?
  - Debe mostrar: dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix; quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco volumen)
  - Notas de Hugo: Migrado de Entregables del brief (L4).
- **S2.5 Qué métricas propondrías que hoy no existen** — ¿Qué métricas propondrías que hoy no existen?
  - Debe mostrar: qué métricas propondrías que hoy no existen (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) y cómo medirlas, robustecerlo y bajar lo que tenga sentido
  - Notas de Hugo: Migrado de Entregables del brief (L5).
- **S2.6 Hipótesis ToFu y BoFu**
  - Debe mostrar: Definir que hipótesis ToFu y BoFu (demanda, calidad, velocidad de atención, conversión post-SQL; p. ej. la capacidad comercial instalada no alcanza la demanda generada, la calidad de la máquina de leads bajó) podrían estar afectando su motor de acuerdo a su problema definido y qué datos validarían o descartarían cada una, aqui no hay que hacer research en data es una propuesta
  - Notas de Hugo: Migrado de Entregables del brief (L6).
- **S2.7 Solución analítica para que el CRO opere el funnel de forma recurrente y qué decisiones le permite tomar**
  - Debe mostrar: solución analítica para que el CRO opere el funnel de forma recurrente y qué decisiones le permite tomar (técnica: pulir CRM, analítica digital · decision making: dashboards automatizados por foro, análisis ad hoc, agentes de IA)
  - Notas de Hugo: Migrado de Entregables del brief (L7).

### S3 · Revenue
_Revenue: con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento). Proponemos cómo introducir descuentos temporales y un modelo de datos que separe el valor de la suscripción del precio pagado._

- **S3.1 Qué data observable de pricing introductorio podemos sacar** — ¿Qué data observable de pricing introductorio podemos sacar?
  - Debe mostrar: qué data observable de pricing introductorio podemos sacar
  - Notas de Hugo: Migrado de Entregables del brief (L1).
- **S3.2 Cómo debería Finora introducir descuentos temporales** — ¿Cómo debería Finora introducir descuentos temporales?
  - Debe mostrar: cómo debería Finora introducir descuentos temporales (mecanismo propuesto, implicaciones multidisciplinarias, preguntas del CFO contestadas con el modelo propuesto)
  - Notas de Hugo: Migrado de Entregables del brief (L2).
- **S3.3 Cómo separar el valor de la suscripción del precio efectivamente pagado** — ¿Cómo separar el valor de la suscripción del precio efectivamente pagado?
  - Debe mostrar: cómo separar el valor de la suscripción del precio efectivamente pagado: propuesta de modelo de datos (campos, tablas, definiciones)
  - Notas de Hugo: Migrado de Entregables del brief (L3).
- **S3.4 Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales** — ¿Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales?
  - Debe mostrar: cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales (Hugo: probablemente lo integra la misma propuesta de modelo de datos)
  - Notas de Hugo: Migrado de Entregables del brief (L4).

## 4. Hipótesis
- **H-001** New creció, pero otras entradas bajaron. Entonces el total de personas que podrían comprar no creció tanto como parecía.
  - _Se debilita si:_ Si el total crece menos, corregimos la magnitud de la premisa. Si crece como esperaba el CRO, dejamos de usar falta de demanda total como explicación de la menor proporción que compra.
- **H-002** Aumentó la proporción de personas que históricamente compran menos o tardan más en hacerlo.
  - _Se debilita si:_ Si la mezcla nueva con el comportamiento habitual de cada grupo explica la diferencia, esa lectura gana fuerza. Si queda una diferencia dentro de grupos, pasamos a C3.
- **H-003** Hay más entradas recientes que todavía no tuvieron la misma oportunidad de comprar.
  - _Se debilita si:_ Si al igualar tiempo y perfil desaparece la diferencia, la juventud del grupo es una explicación compatible. Si no desaparece, «sólo necesitan más tiempo» deja de ser suficiente.
- **H-004** HC3a: al principio compran menos, pero después alcanzan un resultado parecido. HC3b: la diferencia sigue existiendo incluso con más seguimiento comparable.
  - _Se debilita si:_ Si se recupera, pierde fuerza la explicación de una caída persistente en ese periodo. Si no se recupera, el retraso pierde fuerza como explicación suficiente; aun así no demuestra que esas personas nunca comprarán.
- **H-005** Bajó la calidad de lo que genera la máquina de leads: al entrar, muestran menos necesidad, intención o ajuste. Es H-005 en palabras de Hugo.
  - _Se debilita si:_ Se debilita si las señales al entrar, medidas con el mismo criterio, no empeoraron. La opinión posterior de Sales no basta.
- **H-006** El volumen de entradas superó la capacidad instalada de SDRs y AEs, así que la atención se demora y la compra cae. Es H-006 con un mecanismo concreto: la capacidad.
  - _Se debilita si:_ Se debilita si la carga por SDR/AE no subió cuando creció New, si los tiempos a primer contacto no empeoraron o si la compra cae igual en las entradas atendidas a tiempo.
- **H-007** Con entradas y avance previo comparables, el deterioro aparece después de un punto del recorrido.
  - _Se debilita si:_ Si el tramo posterior está estable, esa ubicación pierde fuerza. Si cae, sabemos dónde mirar, no necesariamente por qué ocurre.
- **H-008** Cambios de producto, precio, condiciones o alternativas afectan la elección aunque intención inicial y atención sean parecidas.
  - _Se debilita si:_ Si no hay señales que lo sostengan, no dedicar tiempo a investigar el mercado en general. Si aparecen, precisar una pregunta externa concreta.
- **H-009** Entraron más o menos clientes, o entraron con suscripciones o tarifas distintas.
  - _Se debilita si:_ Si el valor antes de descuentos cambia, revisar cantidad, características y tarifa. Si ese valor no cambia pero el pago sí, mirar descuento o diferencia entre cobro y suscripción.
- **H-010** Hay descuentos documentados al entrar y cambió cuánto reducen el precio.
  - _Se debilita si:_ Si se documenta un descuento, puede investigarse su aporte. Si se confirma que no hubo, descartamos esa explicación histórica. No tener el campo no demuestra que no hubo descuentos.
- **H-011** Salieron más clientes o salieron clientes que aportaban más antes de descuentos.
  - _Se debilita si:_ Si terminó la relación, se sostiene hablar de salida. Si el cliente sigue activo, hay que retirar esa etiqueta aunque no haya pago observado.
- **H-012** Los clientes que salen ya pagaban menos por descuentos; el ingreso que desaparece es distinto del valor sin descuento.
  - _Se debilita si:_ Si se confirma, ese descuento pertenece al cálculo de esa salida. No se cuenta como fin de descuento de un cliente que permanece.
- **H-013** Cambió plan, cantidad, características o uso, manteniendo condiciones de tarifa comparables.
  - _Se debilita si:_ Cambio de uso o plan con tarifa comparable apoya esta explicación. Configuración estable la debilita.
- **H-014** La empresa cambió la tarifa aplicable a una suscripción comparable.
  - _Se debilita si:_ Tarifa distinta con características comparables apoya precio. Tarifa estable lo debilita.
- **H-015** El descuento empezó, aumentó, se redujo o terminó, cambiando el pago o compensando un cambio de suscripción.
  - _Se debilita si:_ Descuento distinto con suscripción estable apunta a ese componente comercial. Sin datos de descuento, no elegir una explicación por la forma del pago.
- **H-016** Al menos dos situaciones importantes para el CFO podrían producir el mismo pago observado.
  - _Se debilita si:_ Si hay al menos un contraejemplo relevante, la observación no identifica esa distinción. Si existen otros campos que lo resuelven, se corrige el planteamiento. Nada de esto prueba descuentos históricos.
- **H-017** Las definiciones y los datos permiten comparar montos y primeras apariciones sin distorsiones importantes.
  - _Se debilita si:_ Si hay contradicciones, ajustar los nombres y el alcance antes de interpretar. Si no sabemos que es MRR, llamarlo monto observado.
- **H-018** Se observa un cambio entre periodos comparables.
  - _Se debilita si:_ Cambio que se sostiene apoya describir un cambio de pagadores. Si desaparece al corregir datos, se retira esa lectura.
- **H-019** Una parte de los grupos explica buena parte del cambio observado.
  - _Se debilita si:_ Si hay concentración respaldada, enfocar ahí las siguientes preguntas. Si no, no fabricar grupos para forzar una historia.
- **H-020** El cambio se concentra en uno o varios de esos componentes observados.
  - _Se debilita si:_ Si no suma, corregir antes de interpretar. Si se compensan, no decir que no pasó nada porque el neto sea pequeño.
- **H-021** Los grupos que empezaron a pagar en distintos momentos difieren en sus pagos posteriores.
  - _Se debilita si:_ Si la diferencia persiste en una comparación justa, puede matizar la lectura económica. Si no hay seguimiento comparable, no concluir deterioro.
- **H-022** Gasto agregado y resultados pagados evolucionan de forma diferente.
  - _Se debilita si:_ Si no añade una conclusión que cambie la historia, dejarlo fuera. Si divergen, sólo describirlo, sin atribuir el resultado al gasto.

## 5. Plan de investigación
- **RT-001** [Medición · Measurement · L2] ¿Qué hipótesis ToFu y BoFu podrían explicar «más leads, pero no más ventas»? ¿Y qué información mínima validaría o descartaría cada una (entradas únicas con fecha, señales iniciales, recorrido, atención, vínculo con pago)? → **R-010**
  - Por qué: Convierte «más leads, pero no más ventas» en hipótesis con el dato que las decide, y la que no tenga dato posible sale de la historia (versión mejorada de RT-001: suma S2.6, respuesta de arranque y pasos, sin research en data, como pediste).
  - Sirve a: Q-001, Q-004, Q-005, Q-006, Q-016, Q-021, Q-023, H-001, H-002, H-003, H-004, H-005, H-006, H-007, H-008, S2.6
- **RT-002** [Modelo de datos · Data Engineering · L2] ¿Cómo separar el valor de la suscripción del precio efectivamente pagado y clasificar el inicio y el fin de un descuento sin confundirlos con contracción o expansión reales? Propuesta de modelo de datos (campos, tablas, definiciones) y qué evidencia confirmaría vigencia, características contratadas, tarifa y descuento aplicado. → **R-011**
  - Por qué: Es lo que le da una sola lectura a cada ejemplo del CFO; sin esto, el MRR con descuentos sigue siendo ambiguo (versión mejorada de RT-002: la amplío a S3.3 y S3.4 porque la evidencia que pedía son justo los campos del modelo, y S3.4 va dentro, como dijiste).
  - Sirve a: N-029, N-030, Q-002, Q-009, Q-011, Q-017, Q-025, Q-026, H-012, H-013, H-014, H-015, H-016, S3.3, S3.4
- **RT-003** [Datos · Analytics] ¿Qué periodo, meses completos, escala a COP y definición de cliente activo están detrás del 4,5×, el 2,8× y el −38% del Overview? ¿Y qué señales de salud del modelo abren Growth y Revenue sin llamarlas deterioro? → **R-012**
  - Por qué: Si al fijar la ventana las cifras cambian de tamaño, cambia el arranque de toda la historia; si se sostienen, el Overview abre Growth y Revenue con números defendibles (versión mejorada de RT-003: suma S1.1, respuesta de arranque, pasos y la selección de señales).
  - Sirve a: N-020, N-021, H-017, H-018, Q-010, Q-020, S1.1
- **RT-004** [Datos · Analytics] ¿Qué documenta el archivo de gasto de S&M (unidad, moneda y meses por rubro)? ¿Software Tools + Freelance va en Habilitación comercial o en producto? → **R-013**
  - Por qué: Define si el cruce de S2.2 puede usar montos o solo formas en el tiempo, y si Habilitación se queda como gasto comercial o sale como producto (versión mejorada de RT-004: suma S2.2, respuesta de arranque y pasos).
  - Sirve a: N-023, Q-018, Q-022, S2.2
- **RT-005** [Medición · Measurement · L2] ¿Qué dato mínimo y qué comparación separarían una capacidad comercial insuficiente (H-006) de una caída en la calidad de la máquina de leads (H-005)? Por ejemplo, carga por SDR/AE y tiempo a primer contacto por grupo de entrada, frente a señales de ajuste al entrar. → **R-014**
  - Por qué: Capacidad y calidad llevan a decisiones opuestas (poner más gente o arreglar la máquina de leads), así que el dato que las separa es el más valioso para el CRO (versión mejorada de RT-005: suma S2.6, respuesta de arranque y pasos).
  - Sirve a: H-005, H-006, Q-016, Q-021, Q-023, S2.6
- **RT-015** [Datos · Analytics] ¿Qué muestran juntos los primeros pagadores observados por industria y el gasto de S&M por categoría (Generación de Demanda ToFu, Team, Habilitación) a lo largo del tiempo? ¿Hasta dónde se pueden relacionar cruzando fechas sin pasar de asociación a efecto? → **R-015**
  - Por qué: Si las series divergen, la lámina lo describe y justifica pedir atribución por canal; si no agrega nada que cambie la historia, sale (H-022).
  - Sirve a: Q-018, Q-022, Q-020, Q-012, H-022, N-022, N-023, S2.2
- **RT-016** [Medición · Measurement · L3] ¿Cómo definir y medir el funnel si no todos lo recorren igual (self-service, entrada directa a SQL, leads estancados semanas)? Qué puertas (Assisted / Self Service / Executive) y canales, qué funnel por puerta, cómo encaja AAARRR y con qué conversion rate y métricas clave. → **R-016**
  - Por qué: Es la columna de Growth: sin una definición por puerta no se puede medir ninguna hipótesis de S2.6 ni hay nada que operar en S2.7.
  - Sirve a: N-008, N-024, N-005, N-006, N-007, Q-001, Q-003, Q-016, H-003, S2.3
- **RT-017** [Datos · Analytics] ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento entre los pagadores observados (industria, banda de ticket de entrada, cosecha, churn observado)? ¿Hay industrias de bajo churn, ticket alto y poco volumen? → **R-017**
  - Por qué: Si la pérdida se concentra en un segmento, Growth tiene dónde enfocar y el CRO una prioridad; si está difundida, la lámina lo dice sin inventar grupos (H-019).
  - Sirve a: Q-014, Q-012, Q-015, Q-008, H-011, H-019, H-021, S2.4
- **RT-018** [Medición · Measurement · L2] ¿Qué métricas propondrías (MRR, ARR, ARPU, CAC, LTV, Churn, UCM), cómo se miden, cuáles se pueden calcular hoy con los datos del caso y cuáles necesitan datos nuevos? → **R-018**
  - Por qué: Separa lo que CEO, CRO y CFO pueden ver hoy de lo que requiere datos nuevos, y evita poner CAC, LTV o UCM en la lámina sin base.
  - Sirve a: N-025, Q-003, Q-010, H-017, S2.5
- **RT-019** [Medición · Measurement · L2] ¿Qué solución analítica le permitiría al CRO operar el funnel de forma recurrente y qué decisiones le permitiría tomar? Capa técnica (CRM, analítica digital) y capa de decision making (dashboards por foro, análisis ad hoc, agentes de IA). → **R-019**
  - Por qué: Sin decisiones del CRO, la solución es un catálogo de dashboards; atada a decisiones y foros, es la acción con la que cierra Growth.
  - Sirve a: N-009, N-010, N-027, Q-003, Q-016, S2.7
- **RT-020** [Datos · Analytics] ¿Qué data observable de pricing introductorio y de comportamiento del monto se puede sacar de los pagos, sin leerla como descuento? → **R-020**
  - Por qué: Si el monto muestra patrones que parecen precio de entrada, se vuelven preguntas concretas para Finora; si no, la lámina muestra el límite del monto y pasa directo al mecanismo de S3.2.
  - Sirve a: N-028, Q-011, Q-012, H-009, H-010, H-016, S3.1
- **RT-021** [Research · Business Research · L2] ¿Cómo debería Finora introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»? Mecanismo propuesto, implicaciones multidisciplinarias y las preguntas del CFO contestadas con el modelo. → **R-021**
  - Por qué: Es la decisión de Revenue: el mecanismo define si el CFO puede seguir respondiendo por qué cambió el MRR cuando existan descuentos, y cuánto revenue deja de capturar.
  - Sirve a: N-028, Q-002, Q-025, Q-026, H-015, S3.2

## 6. Lo que no afirmamos todavía
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
- Una cifra histórica de revenue no capturado ni un puente histórico por tarifa y descuento: el histórico no trae tarifas ni descuentos; eso se propone hacia adelante.
- Plazos o umbrales del funnel (días para «estancado», plazo para contar la compra) como si fueran estándar de mercado: son parámetros a acordar con Finora.
- Que los tres casos de Q-025 muestran lo que pasa en Finora: son ejemplos construidos que prueban un límite del modelo, no observaciones.

## 7. Decisiones necesarias
- Qué unidad cuenta como entrada (contacto, usuario, oportunidad o cliente).
- Qué significa adquirir un cliente para el CRO: cerrar una venta, primer pago o suscripción activa.
- Qué es «Executive» en la Lámina 3: la ruta de entrada directa a SQL o un segmento de cuentas con KAM. Define si las columnas separan cómo compra el cliente o quién es.
- Qué decisiones del CRO asumimos explícitamente para la columna «Decision Making», dado que el caso no las define.
- Cómo se arma el funnel híbrido: una secuencia con varias puertas de entrada, un funnel por motion que converge en el pago, o cohortes de entrada con plazo fijo (ver alternativas de este turno).
- Qué MRR es el titular cuando existan descuentos: el de antes de descuento (valor de la suscripción), el cobrado, o ambos con el descuento como línea del puente.
- Qué entra en «revenue que dejamos de capturar por decisiones comerciales»: solo descuentos temporales o también otras concesiones, como una tarifa negociada.
- Si el mecanismo de descuentos temporales se propone desde cero como supuesto declarado, dado que no sabemos qué tiene definido Finora.

## 8. Riesgos
- El esqueleto (Overview + 4 láminas de Growth + Revenue) es material de soporte; si se usa como la presentación de ≤5 min, no cabe.
- La Lámina 4 carga tres preguntas del brief (concentración + métricas, hipótesis + datos, solución analítica) y puede quedar como una lista de frameworks sin respuesta.
- El agente propio dentro de «Seguimiento» puede leerse como demo de herramienta si no se ata a una decisión concreta del CRO.
- Que las tareas de data_model y measurement terminen construyendo el modelo o métricas definitivas, contra D-007. El producto es la propuesta (qué campos, qué reglas, qué métricas), no la implementación.
- Catálogo de métricas sin decisión: mientras N-027 siga vacío, S2.5 puede volverse una lista. Cada métrica tiene que colgar de una decisión supuesta y declarada.
- Volumen: el plan queda en 14 tareas para un deck de ≤5 min. La mayoría alimenta el material de soporte; conviene priorizar por impacto × capacidad (D-005) y lanzar primero las que pueden ahorrar trabajo.

---
## Anexo · lo capturado en la conversación
### Lo que Hugo piensa
- “Quiero saber qué está pasando con el negocio subyacente y cuánto revenue estamos dejando de capturar por decisiones comerciales” (Q-026)
- “Hoy existe un histórico con cliente + mes + monto pagado, y los cambios entre meses se usan para clasificar movimientos como crecimiento, contracción, churn o reactivación.” (N-030)
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

### Hechos
- **N-030** Hoy el histórico de Finora tiene cliente + mes + monto pagado, y los cambios del monto entre meses se usan para clasificar movimientos: crecimiento, contracción, churn o reactivación. _(propuesto)_

### Observaciones
- **N-004** U05 · Primera aparición como cliente nuevo
- **N-005** U08 · Self-serve, SQL directo y semanas estancado
- **N-011** U15 · Tu Parte 3
- **N-020** Entre dos periodos aún sin fijar, los clientes activos observados crecen 4,5× y el monto pagado 2,8×. El monto pagado por cliente activo baja ~38% (≈COP 92,8 mil → 57,8 mil). Las tres cifras son una sola observación: el −38% sale de 2,8/4,5 ≈ 0,62.

### Intuiciones de Hugo
- **N-001** U01 · Dos problemas conectados
- **N-003** U04 · Entraron muchos leads no calificados
- **N-026** Hugo lee que Finora tiene un problema de instrumentación comercial y digital (CRM y analítica).

### Supuestos
- **N-024** La Lámina 3 supone que Finora tiene tres motions distinguibles y que cada lead o cliente se puede asignar a una. El caso respalda self-service y proceso comercial asistido; «Executive» no aparece como ruta propia.

### Preguntas abiertas
- **Q-001** ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- **Q-002** ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?
- **Q-003** ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?
- **Q-004** ¿Realmente aumentó igual la entrada total?
- **Q-005** ¿Cambió la gente que entra o el tiempo que ha tenido para comprar?
- **Q-006** ¿Personas similares están comprando menos o comprando más tarde?
- **Q-007** ¿Cuánto aportan los clientes que entran?
- **Q-008** ¿Cuánto dejan de aportar los clientes que salen?
- **Q-009** ¿Qué cambió en quienes permanecen?
- **Q-010** ¿Qué podemos nombrar y comparar válidamente?
- **Q-011** ¿El monto identifica los escenarios del CFO?
- **Q-012** ¿Qué cambió en los primeros pagadores observados?
- **Q-013** ¿Dónde se concentra el cambio del monto observado?
- **Q-014** ¿En qué segmentos se concentra la pérdida de crecimiento? Con los datos disponibles solo se puede mirar por industria y sobre pagadores observados; no sobre leads ni por canal.
- **Q-015** ¿Cambió la economía posterior de los nuevos pagadores?
- **Q-016** ¿Qué evidencia mínima permitiría distinguir las explicaciones del CRO?
- **Q-017** ¿Qué distinguiría los componentes del valor y la pertenencia recurrente?
- **Q-018** ¿Qué relación entre el gasto de Marketing por categoría y los nuevos pagadores o el monto pagado se puede describir cruzando fechas, y hasta dónde llega (asociación, no efecto)?
- **Q-019** ¿Qué cambió en la respuesta y qué sigue abierto? (volver a las hipótesis y escribir qué aprendimos)
- **Q-020** U02 · ¿Qué cambió y desde cuándo?
- **Q-021** U06 · Demanda, calidad, atención y post-SQL
- **Q-022** U07 · ¿La data actual da alguna pista?
- **Q-023** U12 · ¿Validar implica experimentos?
- **Q-024** ¿Qué relaciones van en la Lámina 1 de Growth? No están registradas en el caso y el brief también las marca «por precisar».
- **Q-025** Tres casos donde el pago observado no alcanza: una expansión compensada por descuento (100→130 con −30, y sigue pagando 100), contracción vs descuento (100→80) y fin de descuento vs expansión.
- **Q-026** ¿Qué está pasando con el negocio subyacente (el valor de la suscripción antes de descuentos) y cuánto revenue deja de capturar Finora por decisiones comerciales, como los descuentos temporales? _(propuesto)_

### Desconocidos
- **N-013** Qué contamos como una persona o cuenta que entra. Un contacto, usuario, oportunidad y cliente no son necesariamente la misma unidad.
- **N-014** Qué entiende el CRO por adquirir un cliente: cerrar una venta, primer pago o suscripción activa.
- **N-015** Si primera transacción realmente significa cliente nuevo y si la historia y los IDs lo permiten.
- **N-016** Si el monto representa suscripción recurrente, facturación o cobro; y a qué periodo pertenece.
- **N-017** Si los meses están completos y la escala de Transactions ya fue multiplicada por 10.000 para llegar a COP.
- **N-018** Si Industry describe la industria actual o la de entonces, y qué clientes no tienen clasificación.
- **N-019** Si un resultado neto estable esconde aumentos y caídas que se compensan.
- **N-027** No sabemos qué decisiones quiere tomar el CRO con el funnel. La columna «Decision Making» de la solución está vacía.

### Propuestas
- **N-002** U03 · Separar lo comercial del revenue
- **N-006** U09 · Primero ordenar canales, después medir
- **N-007** U10 · Agrupar clientes por pagos, churn y gasto
- **N-008** U11 · Trato analítico distinto por segmento
- **N-009** U13 · La herramienta ya construida
- **N-010** U14 · Antes, definiciones y fuentes claras
- **N-012** U16 · Tus pedidos posteriores
- **N-021** Material de soporte en tres secciones: Overview (salud general que introduce lo demás) → Growth (L1 relaciones; L2 entradas, actividad económica y gasto; L3 funnel por motion; L4 concentración, hipótesis y solución analítica) → Revenue (pricing observable, mecanismo de descuentos, preguntas del CFO, modelo de datos).
- **N-022** Lámina 2 de Growth: describir los primeros pagadores observados y su actividad económica (monto pagado) por segmento. Con los datos disponibles, el único segmento es industria.
- **N-023** Agrupar el gasto de Marketing en tres bloques: generación de demanda ToFu (Paid Media + Publicidad no web), equipo (Payroll Expenses + Travel) y habilitación (Software Tools + Freelance). Queda abierta la duda de si habilitación es en realidad gasto de producto.
- **N-025** Como no se conocen las métricas actuales de Finora, proponer métricas que hoy no existen partiendo de MRR, ARR, ARPU, CAC, LTV, Churn y UCM.
- **N-028** Sección Revenue: primero, lo observable de pricing y comportamiento actual en los pagos; después, cómo introducir descuentos temporales (mecanismo propuesto) y sus implicaciones multidisciplinarias.
- **N-029** Una propuesta de modelo de datos que resuelva dos cosas: separar el valor de la suscripción del precio efectivamente pagado (campos, tablas, definiciones) y clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales.
- **N-031** Hipótesis de diseño para S3.3: el descuento temporal se guarda como registro propio ligado a la suscripción (monto o %, fecha de inicio, fecha de fin y motivo), separado del valor de la suscripción. Valor de la suscripción − descuento = lo cobrado. Es un punto de partida para la tarea de data_model, no una conclusión. _(propuesto)_
- **N-032** Hipótesis de diseño para S3.4: el inicio, el cambio y el fin de un descuento son movimientos propios del puente, no contracción ni expansión. Así, 100→80 es contracción solo si baja el valor de la suscripción; si el valor sigue en 100 y hay un descuento de 20, es «inicio de descuento». 100→130 con −30 es expansión +30 y descuento −30, y lo cobrado no cambia. Cuando el descuento termina, el +30 es «fin de descuento», no expansión. _(propuesto)_

### Frames candidatos
- **CRO por cuánto entra, quién entra y cómo compra con el tiempo** ✓ elegido — Incluye rutas distintas sin asumir que sabemos quién comprará en el futuro. C1, C2 y C3.
- **CFO por clientes que entran / salen / permanecen** ✓ elegido — Evita contar la misma cuenta en dos grupos entre las mismas fechas; dentro de cada grupo distinguimos suscripción y descuento.
- **CRO por etapas comerciales** — Dónde se detiene el avance cuando sí hay historial de etapas.
- **CFO por comportamiento / precio / descuentos** — Se parece a la pregunta del ejecutivo.

### Notas de lenguaje
- Hugo usa «monto observado» y «primer pagador observado» en lugar de MRR y cliente nuevo mientras la semántica no esté confirmada.
- Términos en inglés que Hugo usa tal cual: leads, funnel, churn, self-serve, SQL, MRR.
- Overview: «MRR pagado por cliente activo» (o «monto pagado por cliente activo») en lugar de «MRR» a secas; es el ARPU observado de Hugo.
- «Entradas» en la Lámina 2 = primeros pagadores observados; «entradas» y «leads» del funnel quedan para L3–L4.
- «Executive» se puede confundir con Account Executive (el rol que entra después de SQL en el caso), y «KAM» no aparece en el caso, que habla de SDRs y AEs. Conservar los términos de Hugo y definirlos en la lámina.
- «Foros» = espacios recurrentes donde se toman decisiones (p. ej., la revisión comercial semanal); se conserva el término.
- Usar «cobrado» para lo que efectivamente se paga y «valor de la suscripción» o «antes de descuento» para lo contratado. Evitar «neto» para esto, porque en el caso «neto» ya se usa para el resultado del puente.
- «Estancado» es una bandera de tiempo en etapa, no una etapa del funnel.
- Hugo pega las preguntas literales del caso: pueden quedar tal cual como pregunta de cada lámina. «Negocio subyacente» y «revenue que dejamos de capturar» vienen del texto del caso; conservarlas.
