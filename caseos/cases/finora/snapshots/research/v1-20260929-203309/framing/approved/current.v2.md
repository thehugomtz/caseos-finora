# FRAMING & SHAPING
> Versión 23 · actualizado 2026-09-29T18:23

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
- **H-017** Las definiciones y los datos permiten comparar montos y primeras apariciones sin distorsiones importantes. ⚠ needs_review
  - _Se debilita si:_ Si hay contradicciones, ajustar los nombres y el alcance antes de interpretar. Si no sabemos que es MRR, llamarlo monto observado.
- **H-018** Se observa un cambio entre periodos comparables.
  - _Se debilita si:_ Cambio que se sostiene apoya describir un cambio de pagadores. Si desaparece al corregir datos, se retira esa lectura.
- **H-019** Una parte de los grupos explica buena parte del cambio observado. ⚠ needs_review
  - _Se debilita si:_ Si hay concentración respaldada, enfocar ahí las siguientes preguntas. Si no, no fabricar grupos para forzar una historia.
- **H-020** El cambio se concentra en uno o varios de esos componentes observados.
  - _Se debilita si:_ Si no suma, corregir antes de interpretar. Si se compensan, no decir que no pasó nada porque el neto sea pequeño.
- **H-021** Los grupos que empezaron a pagar en distintos momentos difieren en sus pagos posteriores.
  - _Se debilita si:_ Si la diferencia persiste en una comparación justa, puede matizar la lectura económica. Si no hay seguimiento comparable, no concluir deterioro.
- **H-022** Gasto agregado y resultados pagados evolucionan de forma diferente.
  - _Se debilita si:_ Si no añade una conclusión que cambie la historia, dejarlo fuera. Si divergen, sólo describirlo, sin atribuir el resultado al gasto.
- **H-023** El valle del S&M total en ago-23 (1,10 u) refleja en parte movimientos contables (PayrollExpenses negativo, fin de Freelance) y no solo menos gasto. _(propuesto)_
  - _Se debilita si:_ Si PayrollExpenses no es negativo entre may-23 y ago-23 y la caída desde may-23 se mantiene al excluir PayrollExpenses y Freelance, el valle es menos gasto registrado y el agregado puede cruzar el corte de jun-23.
- **H-024** Parte del salto de primeras apariciones de dic-22 (26) a ene-23 (60) no es entrada nueva, sino un efecto de registro: pagadores que ya existían y reaparecen con otro identificador o por un cambio de sistema de cobro. _(propuesto)_ ⚠ needs_review
  - _Se debilita si:_ Se descarta si no hay salidas observadas en nov–dic-22 que coincidan en industria y monto con las primeras apariciones de ene-23, y si Finora confirma que no cambiaron el sistema de cobro ni los identificadores.
- **H-025** El aumento de primeras apariciones en jun–dic-23 frente a ene–may-23 y la caída del S&M registrado desde may-23 vienen de un mismo cambio en la operación comercial a mitad de 2023 (por ejemplo, un giro hacia Self Service o una reorganización de Team), y no de que menos gasto traiga más pagadores. _(propuesto)_
  - _Se debilita si:_ Se descarta si Finora confirma que en may/jun-23 solo cambió cómo se registra el gasto y no la operación, o si la serie mensual muestra que el aumento fue gradual a lo largo de 2023 y no se concentra alrededor de may/jun-23.
- **H-026** El volumen extra de primeras apariciones entre 2022 y 2024 es sobre todo de ticket bajo: las entradas de ticket alto por mes no crecen al ritmo del total (+104%). _(propuesto)_
  - _Se debilita si:_ Se descarta si, con bandas de ticket fijas en COP según los cortes de 2022, las primeras apariciones por mes de la banda alta crecen en una proporción parecida al total. En ese caso, la caída del ticket sería una baja pareja de todos los tickets y no un cambio de mezcla.
- **H-027** Parte del aumento de entradas y de la peor mezcla viene de un cambio en cómo se cuentan o se reparten (definición de lead, formulario, regla de calificación o reparto), no de más demanda ni de una máquina de leads que genere peor. _(propuesto)_
  - _Se debilita si:_ El enunciado o Finora confirman que la definición de lead, el formulario, la regla de calificación y el reparto no cambiaron entre el periodo base y el de caída, o que ningún cambio coincide con el salto de entradas.
- **H-028** H-005 y H-006 pueden operar a la vez: con más volumen, los SDR/AE dejan sin trabajar primero las entradas que perciben peores (R-014, citando a Sabnis et al., 2013). La palanca cambia según si esas entradas comprarían al ser atendidas: si no comprarían, más capacidad no las recupera; si comprarían, la capacidad importa. _(propuesto)_
  - _Se debilita si:_ La mezcla de ajuste al entrar no empeora entre periodos, o, dentro de una misma banda de ajuste, ni el primer contacto humano ni la compra cambian entre semanas de más y menos carga.
- **H-029** El −19% de jul–oct 2024 en primeros pagadores observados es, al menos en parte, un efecto de borde o de rezago: octubre-24 incompleto en los pagos, o más tiempo entre Won y primer pago en 2024 que en 2023. _(propuesto)_ ⚠ needs_review
  - _Se debilita si:_ Si la caída se mantiene parecida al comparar jul–sep 2024 con 2023 (sin octubre) y el vínculo CRM→pago muestra que el tiempo entre Won y primer pago no cambió de 2023 a 2024, la hipótesis cae.
- **H-030** El ticket de entrada bajó antes de 2024 y se mantuvo de 2023 a 2024. Eso haría compatibles el primer pago menor de R-003/R-009 con «el monto por alta no cayó» de R-010. _(propuesto)_
  - _Se debilita si:_ Si T-004, con el mismo estadístico y la misma ventana que R-010, muestra el ticket de 2024 por debajo del de 2023, no hay reconciliación y queda una contradicción que registrar.
- **H-031** Una parte relevante de la reactivación y la contracción del puente observado (T-003) desaparece al aplicar una ventana de gracia y repartir los pagos que cubren varios meses. _(propuesto)_
  - _Se debilita si:_ Con la regla que apruebes en H-017, la reactivación y la contracción de T-003 quedan en niveles parecidos a los observados.
- **H-032** El primer pago de los nuevos pagadores queda por debajo de su monto usual, y esa brecha es mayor en las cohortes 2023–2024 que en 2022. Si es así, parte de la caída del ticket de entrada (T-018) es de medición. _(propuesto)_ ⚠ needs_review
  - _Se debilita si:_ Medido con M1 o con el monto usual, el ticket de entrada cae entre 2022 y 2023–2024 en una proporción parecida a la del primer pago.
- **H-033** Más de la mitad del COP de contracción observada es momento de cobro —un primer pago o una reactivación que cubre más de un mes, cargos iniciales o atrasos—, no suscripciones que se achican. _(propuesto)_
  - _Se debilita si:_ Se descarta si Finora confirma que cada fila es el valor del periodo de servicio (no el pago recibido) y que no cobra varios meses juntos, cargos de instalación ni atrasos. También se descarta si su facturación muestra cambios de plan o cantidad en la mayoría de esas 366 contracciones.
- **H-034** Los meses en cero seguidos de un pago del doble son atrasos, no bajas seguidas de un regreso: inflan el churn observado de ese mes y la reactivación. _(propuesto)_
  - _Se debilita si:_ Se descarta si la política de mora de Finora no permite pagar meses atrasados, o si la facturación muestra esas suscripciones como canceladas o suspendidas en el mes en cero.
- **H-035** Parte de la caída del ticket de entrada (T-018: mediana COP 63,0 mil en 2022 y 36,8 mil en 2023) se debe a un cambio en la forma del primer cobro, no a suscripciones de entrada más pequeñas. _(propuesto)_
  - _Se debilita si:_ Se descarta si, midiendo la entrada con el monto usual del cliente (su segundo mes pagado, comparando solo a quienes lo tienen), la caída de 2022 a 2023 se mantiene con una magnitud parecida. También si la proporción de primeros pagos seguidos de una bajada es similar entre años.
- **H-036** Puente Growth–Revenue para Q-003: la mezcla de entradas se movió hacia una puerta de menor valor (por ejemplo, Self Service, si existe como compra sin intervención humana). Eso explicaría a la vez más primeros pagadores observados con primer pago menor (R-003) y la caída del monto por cliente activo concentrada en quién entra (R-009). Une H-002 y H-009. Hoy no es evaluable, porque los pagos no traen la puerta (F-143). _(propuesto)_
  - _Se debilita si:_ Con la puerta etiquetada por cuenta y unida a los pagos, la participación de la puerta de menor valor entre los primeros pagadores no sube de 2022 a 2023–2024, o la caída del primer pago y del monto por cliente aparece con la misma fuerza dentro de cada puerta.
- **H-037** En el nudo, «clientes nuevos» cambia según se cuenten o no las reactivaciones observadas (según R-016, equivalen al 18–38% de las entradas a pago). Si su peso se movió en el período, parte de lo que el CRO lee como «nuevos que no crecen en la misma proporción» sería un efecto de la definición, no del desempeño. Es el análogo de H-001 del lado del pago y se puede revisar con los datos del caso. _(propuesto)_ ⚠ needs_review
  - _Se debilita si:_ Con los pagos, el peso de las reactivaciones observadas en las entradas a pago es estable entre 2022 y 2024, y la tendencia de las entradas a pago es la misma con y sin ellas.
- **H-038** La caída del ticket de entrada de los nuevos pagadores observados (T-004, T-018) viene sobre todo de un cambio de mezcla hacia motions o canales de adquisición de menor ticket, no de una baja dentro de cada motion. Self Service o Digital serían candidatos, si pagan menos. Es el tipo de conexión Growth–Revenue que pide Q-003, y el ID de cuenta de R-019 permitiría probarla. _(propuesto)_
  - _Se debilita si:_ Con motion y canal por cuenta unidos a la facturación, el ticket de entrada baja en proporción parecida dentro de cada motion y canal. O bien la participación de las entradas de menor ticket no sube entre 2022 y 2024.
- **H-039** La mayor parte del churn observado que vuelve al mes siguiente con el mismo monto (44%, DM-4) es un desfase del cobro con la suscripción vigente, no una baja seguida de una nueva alta. Si se confirma, dice cuánto del ruido del lado Revenue se resuelve con la facturación que propone R-019. _(propuesto)_
  - _Se debilita si:_ Con el estado de suscripción de la facturación, la mayoría de esos huecos de un mes muestran una cancelación y una suscripción nueva.
- **H-040** Una parte importante de los movimientos que se deshacen al mes siguiente (meses sin pago seguidos de un regreso, subidas que duran un mes) son efectos del calendario de cobro: atrasos que se ponen al día y pagos dobles o parciales, no bajas, pausas ni cambios de suscripción. _(propuesto)_
  - _Se debilita si:_ En el panel, el pago de regreso tras un mes sin pago no se parece a la suma de lo que se dejó de pagar (por ejemplo, cerca del doble del monto previo), y las subidas que se revierten no aparecen junto a un mes sin pago o con pago parcial. Aun si la hipótesis se sostiene, sería un patrón y no una verificación: el estado real del cliente solo lo confirma Finora.
- **H-041** Parte de las primeras apariciones de pago de 2022, sobre todo en mar–may-22, son clientes anteriores al panel que no pagaron en ene–feb-22. Eso inflaría el ticket de entrada de 2022 (COP 128,7 mil de promedio) y exageraría su caída hacia 2023. _(propuesto)_
  - _Se debilita si:_ El ticket de entrada de 2022 (promedio y mediana) se mantiene al excluir mar–may-22, o esas primeras apariciones no tienen un ticket distinto del resto de 2022.
- **H-042** Parte de la caída del ticket de entrada 2022→2024 y de la baja de la cosecha 2022 se debe a pagos iniciales grandes en 2022 (primer pago por encima del pago recurrente), no a un cambio en lo que el cliente paga mes a mes. _(propuesto)_
  - _Se debilita si:_ Se descarta si, midiendo desde el segundo pago, la mediana 2022→2024 cae en una proporción parecida a la del primer pago (COP 63,0 → 42,0 mil) y el efecto dentro de las cosechas de F-097 sigue siendo negativo.
- **H-043** El «churn caro» por promedio (F-101) viene en buena parte de cuentas grandes que se saltan pagos y vuelven, no de salidas. _(propuesto)_
  - _Se debilita si:_ Se descarta si la razón de promedios medida solo sobre churn persistente sigue por encima de 1, con el límite inferior del intervalo también por encima de 1.
- **H-044** Salud tiene mejor economía observada por cliente que el resto: menor churn persistente, el ticket de entrada mediano más alto de 2024 (empatado con Restaurantes) y la menor caída del MRR por cliente, pero con poco volumen (124 clientes activos en oct-24). _(propuesto)_
  - _Se debilita si:_ Se descarta como señal si, con intervalos como los de F-100, el churn persistente y el ticket de entrada de Salud se solapan con los de las demás industrias.
- **H-045** Hacia inicios de 2023 hubo un cambio general en la entrada, de oferta, de plan de entrada, de Canal de adquisición (por ejemplo, más Self Service) o de forma del primer cobro. Ese cambio movió a la vez el número de altas observadas y el ticket de entrada, en todas las industrias (Q-003). _(propuesto)_
  - _Se debilita si:_ Se descarta si, mes a mes en la ventana limpia, la mediana del primer pago no baja de nivel en los mismos meses en que saltan las altas (de 26 en dic-22 a 60 en ene-23, T-016). También se descarta si la baja es gradual a lo largo de 2022–2024. Con información de Finora, se descarta si en ese momento no hubo cambio de oferta, plan, canal ni forma de cobro.
- **H-046** Parte de la caída del ticket de entrada medida con el primer pago viene de lo que incluye ese primer cobro (importes que no se repiten en el 2.º pago), no de un nivel recurrente más bajo. En 2022, el 23,2% de las altas de ventana limpia pagó el primer mes bastante más que el segundo, frente al 11,6% en 2024 (F-086) (Q-012). _(propuesto)_
  - _Se debilita si:_ Se descarta si, en la misma población de ventana limpia, el ticket de entrada medido con el 2.º pago o con el monto usual de los meses 2–3 cae entre 2022 y 2024 en una magnitud parecida a la del 1.er pago: −33% en mediana y −60% en promedio (F-084).
- **H-047** El aumento de montos fuera de la grilla (de 19% a 42%) y de ajustes pequeños (de 9% a 75% de los eventos de expansión) refleja un cambio general en la forma de cobrar, que afecta a la vez a clientes nuevos y antiguos, y no un cambio en lo que contratan los clientes. Si es así, la expansión observada en 2024 no equivale a ampliar lo contratado (H-017). _(propuesto)_
  - _Se debilita si:_ Se descarta si los montos fuera de la grilla y los ajustes pequeños se concentran en pocos clientes, o si su frecuencia sigue la antigüedad de cada cosecha y no el mes calendario.
- **H-048** Un puente de tres capas (MRR de lista, descuento y MRR neto), con líneas propias de «descuento nuevo/aumentado» y «descuento reducido/terminado», separa los tres casos de Q-025 y el descuento del 100%, y sigue cuadrando con el monto pagado observado. _(propuesto)_ ⚠ needs_review
  - _Se debilita si:_ En una simulación con esos cuatro casos, dos situaciones distintas dan las mismas líneas del puente, o la suma de las líneas no cuadra con el MRR neto. La simulación prueba lo que el modelo distingue, no lo que pasó en Finora.
- **H-049** De aquí en adelante, las cohortes que Finora consiga con descuento temporal van a tener menos MRR de lista a igual antigüedad que cohortes comparables sin descuento, como sugiere la evidencia externa de F-154. _(propuesto)_
  - _Se debilita si:_ Con cohortes marcadas y un grupo de control, a igual antigüedad no hay diferencia de MRR de lista entre cohortes con y sin descuento. No se puede probar con los datos del caso: es la prueba que el modelo propuesto haría posible.
- **H-050** La conversión de Hybrid va a reflejar sobre todo a quién eligen tocar los SDR/AE (los que ya venían bien o los que se atoraron), no lo que aporta la intervención. _(propuesto)_
  - _Se debilita si:_ Se debilita si la intervención sigue una regla fija que no depende de cómo va el lead (por ejemplo, todo registro con la misma señal de uso), o si frente a un grupo sin contacto elegido al azar la diferencia de compra se mantiene.
- **H-051** Parte de lo que se ve como recorridos distintos podría ser cómo se registra en el CRM: oportunidades creadas directo en SQL, leads sin estado de salida que se ven estancados porque nadie los cerró, y clientes Self Service que solo aparecen cuando pagan. _(propuesto)_
  - _Se debilita si:_ Se debilita si las entradas directas a SQL tienen un origen propio registrado (partner, referido, demo pedida) y los estancados tienen actividad registrada en el periodo.
- **H-052** [Paso 1 · artefacto] Parte del aumento en New no son prospectos que puedan comprar: clientes actuales que usan el formulario para soporte o upgrade, duplicados de la misma persona o empresa que entra por varios canales, spam o bots. Inflan los leads sin poder volverse clientes nuevos. Tendría que ser cierto: sube la proporción de New que coincide con un cliente actual (correo, dominio o identificador fiscal), que es duplicado o que se descalifica como «no es prospecto», y al quitarlos los leads y los clientes nuevos crecen parecido. Dato mínimo: leads del CRM con fecha, correo o dominio y motivo de descalificación, más la lista de clientes; no está en el caso. _(propuesto)_
  - _Se debilita si:_ Se descarta si esa proporción es baja y estable entre periodos, o si al quitarlos la brecha entre leads y clientes nuevos se mantiene.
- **H-053** [ToFu · rebota «demanda»] Parte de los leads nuevos son compradores que antes compraban solos por Self Service y ahora pasan por el funnel comercial (por ejemplo, un formulario o un contacto en el registro); o al revés, leads trabajados que terminan comprando solos y no quedan como Won (el caso B de Hybrid sin registrar). En los dos casos el funnel comercial ve más leads sin que crezca la demanda total. Tendría que ser cierto: sube la proporción de New que ya tenía registro en el producto (misma cuenta) antes de entrar como lead, y bajan los primeros pagadores sin intervención cuando suben los leads comerciales. Dato mínimo: CRM y producto unidos por cuenta (N-041). Los pagos del caso dan el total de primeros pagadores de todas las puertas, pero no por cuál entraron. Cercana a H-051, pero aquí cambia por dónde compran, no solo cómo se registra. _(propuesto)_
  - _Se debilita si:_ Se descarta si los New que explican el aumento no tenían registro previo en el producto y los primeros pagadores sin intervención no bajan cuando suben los leads comerciales.
- **H-054** [MoFu · rebota «calidad» y «post-SQL»] Si la meta del SDR se mide en SQL o reuniones (y quizá subió junto con los leads), el SDR pasa SQL menos maduros aunque el criterio escrito no cambie. La caída se nota después de SQL, pero nace antes del traspaso. Tendría que ser cierto: la proporción de leads que llega a SQL sube o se mantiene mientras SQL → Demo y Demo → Won bajan; sube la proporción de SQL que el AE regresa o descalifica; hubo un cambio de metas o comisiones del SDR cerca del inicio de la caída; y las entradas directas a SQL, si de verdad no pasan por el SDR, no muestran la misma caída post-SQL (comparando cómo cambia cada grupo en el tiempo, no su nivel). Dato mínimo: historial de etapas con dueño, origen del SQL y rechazo del AE, más el historial de metas; no está en el caso. _(propuesto)_
  - _Se debilita si:_ Se descarta si la conversión post-SQL cambia igual en las entradas directas a SQL que en los SQL del SDR, o si la proporción de SQL que el AE acepta no cambia.
- **H-055** [MoFu · rebota «velocidad de atención»] El primer contacto puede seguir siendo rápido, pero los leads que no compran en ese momento no tienen seguimiento: se quedan estancados en Working o Engaged y se pierden. Con más volumen, esa bolsa crece y nadie la retoma. Tendría que ser cierto: en cada cohorte de entrada crece la proporción sin actividad por más de los días que se acuerden (Q-064), el tiempo al primer contacto no empeoró, y los estancados que alguien retoma (Reactivate) compran a una tasa que no es despreciable. Dato mínimo: fechas de etapa y actividades por lead; no está en el caso. _(propuesto)_
  - _Se debilita si:_ Se descarta si la proporción de estancados por cohorte no cambia entre periodos, o si los estancados que se retoman casi no compran.
- **H-056** [BoFu · rebota «conversión post-SQL»] Los prospectos llegan a demo o propuesta, pero eligen otra opción o no compran: un cambio de precio o plan, un competidor, o funcionalidad que falta para los tipos de cliente que están entrando. Tendría que ser cierto: la caída se concentra en Proposal → Won (después de ver el precio) más que en SQL → Demo; baja el win rate (de las propuestas, cuántas se ganan) mientras el ciclo se alarga; suben los motivos de pérdida «precio», «competidor» o «falta funcionalidad»; y el momento coincide con un cambio de oferta o precio (Q-031, Q-057). Dato mínimo: motivos de pérdida y fechas por etapa en el CRM, e historial de precio y plan (Q-043); no está en el caso. Research externo solo si Finora nombra competidores. _(propuesto)_
  - _Se debilita si:_ Se descarta si Proposal → Won no cambia, si la mezcla de motivos de pérdida se mantiene, o si la caída es igual donde la oferta no cambió.
- **H-057** [Después del cierre] El funnel sí cierra, pero parte de los Won no llega al primer pago o se cae en el arranque: fricción de cobro, medio de pago, onboarding o arrepentimiento. Solo explica la brecha si para el CRO «venta» es cliente pagando; si es Won, no aplica. Tendría que ser cierto: sube la proporción de Won sin primer pago dentro del plazo que se acuerde, o suben los intentos de cobro fallidos antes del primer pago. Es distinta de H-029: allá pagan más tarde; aquí no pagan. Dato mínimo: Won del CRM unido a facturación por cuenta; los pagos del caso solo muestran a quien sí pagó. _(propuesto)_
  - _Se debilita si:_ Se descarta si casi todos los Won pagan dentro del plazo y esa proporción es estable, o si el CRO mide «venta» como Won.
- **H-058** El peso de las reactivaciones en las entradas a pago (30,4% en 2022 feb–dic, 17,7% en 2023, 22,6% en 2024 ene–oct) se mueve sobre todo porque cambian las Nuevas, no las reactivaciones, que por mes se mantienen en un rango estrecho (T-035). Si es así, H-037 funciona por dilución: una parte casi fija dentro de «clientes nuevos» frena su crecimiento cuando las Nuevas crecen. _(propuesto)_ ⚠ needs_review
  - _Se debilita si:_ Con los pagos de hoy y la definición de R-022, dejar las Nuevas fijas en su nivel de 2022 y recalcular el peso con las reactivaciones de cada año. Si así se reproduce buena parte del cambio observado, el movimiento viene de las reactivaciones y la hipótesis cae.
- **H-059** La mayoría de las reactivaciones observadas en pagos no pasa por el loop de Reactivate del CRO: son vueltas tras un solo mes en cero sin intervención comercial. _(propuesto)_
  - _Se debilita si:_ Con CRM y facturación cruzados por ID de cuenta: si la mayoría de las vueltas a pago tiene, antes del pago de regreso, una entrada Reactivate, una oportunidad o actividad de SDR/AE, la hipótesis cae.
- **H-060** El escalón 2022→2023 del ticket estabilizado se explica porque más primeros pagadores entran pagando un monto bajo que ya existía (36,8 mil), no porque bajaran los montos que ya se cobraban. Indicio: en la cohorte 2023 la mediana es exactamente 36,8 mil con el primer pago, con el 2.º pago y con el monto usual temprano, lo que sugiere un monto muy repetido. La hipótesis describe montos observados; no distingue plan, tarifa ni descuento (R-002, F-167). _(propuesto)_
  - _Se debilita si:_ Queda descartada si 36,8 mil casi no aparece como 2.º pago en la cohorte 2022 y en 2023 aparece de golpe, o si los montos más frecuentes de 2022 reaparecen en 2023 con valores más bajos. En ese caso cambió el monto cobrado, no la elección entre montos que ya existían.
- **H-061** El monto del panel se registra por fecha de cobro (caja), no por mes de servicio. Ese solo mecanismo explicaría a la vez las subidas de un mes que se revierten (F-171), los churns que vuelven a pagar al mes siguiente, los retornos que liquidan exactamente los meses pendientes (F-174) y los primeros pagos por encima del recurrente (F-166). _(propuesto)_
  - _Se debilita si:_ Cae si la definición documentada de Finora dice que el monto es el valor del mes de servicio. También cae si una muestra de facturas muestra que cada monto aparece en su periodo facturado y no en la fecha de pago; por ejemplo, un pago atrasado registrado en su mes de servicio.
- **H-062** La baja del churn observado entre 2022 y 2024 es casi toda baja de interrupciones temporales. En F-175 el persistente se queda cerca de 1%, y la parte que vuelve a pagar pasa de unos 2,5 a unos 1,1 puntos (resta propia sobre F-175). La hipótesis es que esa baja viene del cambio general en la forma de cobrar que plantea H-047 y ocurre dentro de todos los clientes, no solo por la mezcla de cosechas. _(propuesto)_
  - _Se debilita si:_ Cae si la cohorte 2022 mantiene su tasa de interrupciones temporales y la baja total se explica solo por la entrada de cosechas nuevas; eso apunta a mezcla o a un cambio en la entrada como H-045. También cae si la baja empieza antes del aumento de montos fuera de la grilla (T-059). O si desaparece al igualar el plazo de seguimiento entre años: los últimos meses de 2024 tienen menos seguimiento y eso subestima los retornos.
- **H-063** Casi toda la baja del churn observado 2022→2024 está en las interrupciones temporales de pago, porque el churn que no vuelve en el trimestre casi no se movió (F-183). Esa baja de interrupciones viene de un cambio en la forma o el calendario de cobro (en línea con H-047), no solo de que entraron cosechas que se atrasan menos. _(propuesto)_
  - _Se debilita si:_ Se cae si la tasa de meses en cero que vuelven a pagar dentro del trimestre no baja al mismo tiempo en cosechas de distinta antigüedad (2022 y 2023). En ese caso sería mezcla de cosechas o antigüedad, no un cambio en el cobro.
- **H-064** El 45,9% del MRR de reactivación que no encaja en firmas de cobro (F-180) son regresos reales después de una baja: huecos de más de un mes y montos distintos al usual. Si es así, esa es la reactivación que le toca medir al loop de Reactivate del CRO. _(propuesto)_
  - _Se debilita si:_ Se cae si la mayor parte de ese 45,9% viene de huecos de un mes o de pagos que cubren solo parte de los meses del hueco (liquidación parcial). Eso también sería momento de cobro, no regreso.
- **H-065** Si Finora etiqueta hacia atrás a los pagadores 2022–2024 solo con información previa al contacto (F-191, F-188), una parte relevante quedaría en «sin clasificar». La razón sería que el CRM no guarda con fecha de entrada el tamaño, la intención, el ajuste ni el canal. Si es así, el primer hueco del WoW del CRO es capturar esos campos al entrar, antes que medir puertas. _(propuesto)_
  - _Se debilita si:_ Finora muestra esos campos, con fecha anterior al primer contacto, para la mayoría de las cuentas, y el etiquetado deja «sin clasificar» como un residuo menor.
- **H-066** La caída de primeros pagadores es un escalón que empieza en jul-24, justo después de jun-24, el mes más alto de la serie (T-016). No sería un desgaste gradual del nivel alcanzado tras jun-23, que pasa de 63,0 por mes en jul–dic-23 a 58,5 en ene–jun-24 y a 50,8 en jul–oct-24 (cálculo con R-025 y el total 2023 de T-100). _(propuesto)_
  - _Se debilita si:_ Se descarta si la serie mes a mes no muestra un escalón en jun–jul-24, o si la baja ya viene de ene–may-24. En ese caso, la bitácora de cambios hay que pedirla desde jul-23 y no solo desde mitad de 2024.
- **H-067** La caída de jul–oct 2024 revierte sobre todo volumen de ticket bajo, el que más creció desde 2023, en especial en Retail: 49 altas en 2022 mar–dic y 169 en 2023 (T-017), con un ticket mediano de COP 26,2 mil en 2024 (T-043). Si es así, la caída pesa bastante menos en MRR nuevo observado que en el conteo de «clientes nuevos». _(propuesto)_
  - _Se debilita si:_ Se descarta si, en jul–oct-24 frente a jul–oct-23, las altas de ticket estabilizado bajo caen en la misma proporción que las de ticket alto (el ticket mediano no sube). Si además la caída en Retail+Producción no supera el peso de esas industrias en las altas, tampoco se sostiene la parte «en especial en Retail».
- **H-068** El escalón 2022→2023 que resume R-024 (27 → 54 altas por mes) son dos movimientos distintos: (1) un pico de un mes en ene-23 (60 altas, por encima del promedio de 45,2 de ene–may-23, que lo incluye; T-016 y T-013); (2) un cambio de nivel hacia mitad de 2023 (60,6 por mes en jun–dic-23). Si es así, H-024 (registro) solo podría explicar el pico y H-025 (cambio en la operación comercial a mitad de 2023), el cambio de nivel: no compiten entre sí. _(propuesto)_
  - _Se debilita si:_ Se cae si la serie mensual de 2023 sube de forma gradual de febrero a diciembre, sin un salto hacia jun-23. Y el pico deja de apuntar a registro si ene-24 también se separa de feb–may-24: en ese caso sería calendario.
- **H-069** Es un caso particular de H-027: parte del crecimiento de New (H-001) sería reclasificación y no más gente. Serían leads estancados que regresan y que el CRM registra como New y no como Reactivate, porque no hay regla de caducidad del episodio (Q-064) o porque esa regla cambió. A diferencia de H-052, aquí sí son prospectos que pueden comprar, pero no son nuevos. Si las «otras entradas» de H-001 incluyen Reactivate, New subiría y Reactivate bajaría sin que llegue más gente. _(propuesto)_
  - _Se debilita si:_ Con el CRM, cruzar los New de cada mes con registros anteriores de la misma cuenta (empresa, dominio o email). Se descarta si la proporción de New con historia previa no sube en el periodo en que creció New, o si Reactivate no bajó en ese mismo periodo.
- **H-070** Además del valle de ago-23 (H-023), la caída del S&M en el corte de jun-23 es en parte un cambio en cómo se arma el archivo, no solo menos gasto. Hasta may-23 Team es un 12% fijo del total (F-218, F-115), señal de reparto de arriba hacia abajo. Si es así, el «menos gasto, más primeros pagadores» de F-214 y el «mismo cambio» de H-025 se apoyan en un corte de registro. _(propuesto)_
  - _Se debilita si:_ Cae si Finora documenta que el total de S&M se registra con el mismo criterio antes y después de jun-23. También cae si el desglose por rubro muestra que la caída de may-23 a ago-23 viene de rubros registrados igual en ambos tramos, y no de Team ni de PayrollExpenses.
- **H-071** La asociación negativa de −0,57 entre S&M y primeros pagadores (F-219) sale sobre todo del cambio de nivel entre los dos tramos del archivo (hasta may-23 y desde jun-23). Dentro de cada tramo es bastante más débil. _(propuesto)_
  - _Se debilita si:_ Cae si dentro de mar-22–may-23 y dentro de jun-23–oct-24 la correlación, en niveles o en cambios mes a mes, es negativa y de magnitud parecida a −0,57.

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
- **RT-022** [Medición · Measurement · L2] ¿Qué métricas MECE le corresponden a cada casuística de funnel (Executive, Self Service, Hybrid y el loop de Reactivate), cómo se calcula cada una y cuáles se pueden comparar entre funnels? → **R-022**
  - Por qué: Es lo que Hugo pidió explícitamente y lo que convierte el mix en algo que el CRO puede operar. Sin la identidad de estados, las métricas por ruta no cuadran con el total y no responden a «más leads, pero no más ventas».
  - Sirve a: H-004, H-005, H-006, H-007, H-028, H-037, Q-023, Q-050, N-025, N-027, S2.3, S2.5
- **RT-023** [Medición · Measurement · L3] ¿Cómo definir y medir el funnel si no todos lo recorren igual? El mix MECE de funnels (Executive, Self Service, Hybrid y Reactivate), las etapas de cada uno y la regla que pone a cada lead en uno solo. → **R-023**
  - Por qué: Reformula RT-016 (ya investigada en R-016). Es la pregunta que el caso hace literalmente y la base de las métricas (S2.5), de las hipótesis ToFu/BoFu (S2.6) y de la solución (S2.7). Si la regla no es MECE, la suma por ruta no cuadra con el total del nudo y la comparación de «más leads, pero no más ventas» se rompe.
  - Sirve a: N-005, N-006, N-008, N-013, N-024, Q-046, Q-050, H-006, H-028, H-036, H-037, C-005, S2.3, S2.7
- **RT-024** [Datos · Analytics] Paso 1 de C-011 con los pagos: ¿cuánto del «no más clientes nuevos» que se ve en los primeros pagadores observados es artefacto (octubre-24 incompleto, reactivaciones contadas como altas, reapariciones con otro ID) y cuánto queda para contrastar con causas? → **R-024**
  - Por qué: Es la única parte de C-011 que se puede hacer hoy con los datos del caso. Sin ella, el paso 2 se contrasta sobre una brecha que puede estar inflada o desinflada por cómo se cuenta. Se apoya en RT-003 para saber qué meses están completos; aquí el foco es el conteo de nuevos.
  - Sirve a: H-024, H-029, H-037, Q-036, Q-051, C-011, S2.6
- **RT-025** [Medición · Measurement · L2] ¿Qué causas potenciales —las cuatro que trae el caso (demanda, calidad, velocidad de atención, conversión post-SQL) y al menos 3–5 más— podrían explicar «más leads, pero no más ventas», en el orden de C-011 (primero artefactos de medición, después causas ToFu y BoFu)? ¿Qué tendría que ser cierto en los datos para validar o descartar cada una? → **R-025**
  - Por qué: Reformula RT-001 (ya investigada en R-010). El caso da cuatro explicaciones que mezclan causas con un lugar del funnel. Sin más causas que compitan o se encadenen, y sin saber qué dato las separa, S2.6 queda como una lista y la columna «Decision Making» de S2.7 sigue vacía (N-027).
  - Sirve a: Q-001, Q-016, Q-021, H-005, H-006, H-024, H-027, H-028, H-029, H-037, H-051, N-027, C-011, N-044, H-052, H-053, H-054, H-055, H-056, H-057, Q-065, S2.6, S2.7
- **RT-026** [Datos · Analytics] ¿Cuál es el ticket de entrada estabilizado —el segundo pago o el monto usual, no el primer pago— por año de alta y por industria, en cohortes de ventana limpia? ¿Se sostiene la caída 2022→2023 de T-018 y el «menor ticket» de C-007? → **R-026**
  - Por qué: Lo pidió el COS en su revisión de cobertura de las 8 preguntas (D-017), acción 3: C-003 y C-007 se apoyan en el primer pago, que no sirve como valor de entrada.
  - Sirve a: C-003, C-007, T-004, T-018, T-053, T-054, T-055, H-035, H-041, H-042, H-046, F-139, F-143, S2.4, S2.2
- **RT-027** [Datos · Analytics] Simulación ilustrativa con las cifras del enunciado del CFO: ¿cómo se leen los tres casos (paga 100 y luego 80; lista de 100 a 130 con descuento de 30 y pago de 100; fin de ese descuento) y el caso mixto en un puente de tres capas —MRR de lista, descuento y MRR neto—, frente a cómo los lee hoy el puente de monto pagado? → **R-027**
  - Por qué: Lo pidió el COS en su revisión de cobertura de las 8 preguntas (D-017), acción 4: es el remate (Q8) y la regla de Q7; hoy ni H-048 ni C-020 tienen tabla.
  - Sirve a: Q-025, Q-026, H-048, H-049, C-016, C-018, C-020, D-002, R-011, R-021, X-072, S3.4, S3.3
- **RT-028** [Datos · Analytics] ¿Qué parte de la reactivación y de la contracción del puente observado (T-003) es solo momento de cobro? Puente normalizado: un mes sin pago con regreso al monto usual no cuenta como baja ni reactivación, y un pago que cubre varios meses se reparte. → **R-028**
  - Por qué: Lo pidió el COS en su revisión de cobertura de las 8 preguntas (D-017), acción 8 (opcional): refuerza Q5 y le da tabla a X-037.
  - Sirve a: T-003, X-037, H-031, H-033, H-034, H-039, H-040, R-011, C-009, C-016, S3.1
- **RT-029** [Medición · Measurement · L2] Con las definiciones textuales de Hugo, ¿cuál es el mix MECE de funnels —Executive (el funnel actual SDR→AE), Self Service con sus canales, Hybrid (casos A y B) y Reactivate (leads estancados que se reactivan y se asignan a un funnel)—, las etapas de cada uno, la regla que pone a cada lead en uno solo y las métricas de cada casuística? → **R-029**
  - Por qué: La revisión de RT-023 (Challenge de Hugo, 13:43) perdió sus palabras textuales por un error de la plataforma, ya corregido: el especialista no las vio y cambió las definiciones de Executive y Reactivate. Se reformula con sus palabras.
  - Sirve a: R-023, R-022, N-033, N-034, N-035, N-037, N-038, Q-063, Q-064, C-005, X-052, X-080, H-050, H-051, F-189, F-199, S2.3, S2.5
- **RT-030** [Medición · Measurement · L2] ¿Qué etapas aplican a cada funnel —Executive, Self Service, Hybrid A y B, Reactivate— por canal de entrada, literalmente como el Executive (New → Working SDR → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won), y cómo se mide cada funnel con un catálogo MECE de métricas explícitas (volumen, conversión por etapa, velocidad como el tiempo de cierre, valor, calidad y estancamiento)? → **R-031**
  - Por qué: Hugo en el chat (29-sep, revisión del Story v2): C-021 va bien pero falta la propuesta aterrizada por canal con las etapas de cada funnel; C-006 no se entiende y debe salir de C-021; C-009 debe proponer más métricas, explícitas y MECE.
  - Sirve a: C-021, C-006, C-009, C-005, R-029, R-022, R-023, N-033, N-037, N-038, N-050, Q-063, Q-064, S2.3, S2.5
- **RT-031** [Medición · Measurement · L2] ¿Cómo se ordenan las causas de «más leads, pero no más ventas» en un árbol MECE —cada brecha observada en una sola rama—, con qué tendría que ser cierto para validar o descartar cada hoja, el dato mínimo y la palanca del CRO? → **R-032**
  - Por qué: Hugo en el chat (29-sep, revisión del Story v2): en C-023 hay mucho artefacto pero nada MECE, y confunde.
  - Sirve a: C-023, C-011, R-025, R-010, H-052, H-053, H-054, H-055, H-056, H-057, H-005, H-006, H-007, N-051, S2.6
- **RT-032** [Modelo de datos · Data Engineering · L2] Propuesta de modelo de datos para operar el funnel, as-is vs to-be: ¿qué tablas hay hoy (cliente-mes-monto, industria, gasto de S&M) y qué responden, qué entidades se agregan (cuenta, lead, canal y fuente, campaña, oportunidad, historial de etapas, actividades de SDR/AE, eventos de producto, asignación, suscripción) con llaves y grano, y qué métrica de C-006 y C-009 habilita cada una? → **R-033**
  - Por qué: Hugo en el chat (29-sep, revisión del Story v2): C-013 debe mostrar explícitamente el modelo de datos propuesto, as-is vs to-be.
  - Sirve a: C-013, C-014, C-006, C-009, R-019, R-029, N-052, S2.7
- **RT-033** [Modelo de datos · Data Engineering · L2] Propuesta de modelo de datos de precios y descuentos, as-is vs to-be, con más casuísticas: ¿cómo se registra un descuento según su origen —promoción digital o física, negociación comercial, retención o partner—, si es digital con su source (canal, campaña, código, landing), y con su tipo, duración, alcance, apilamiento y aprobador, sin confundirlo con cambios de suscripción? → **R-034**
  - Por qué: Hugo en el chat (29-sep, revisión del Story v2): C-017 debe mostrar un modelo de datos as-is vs to-be y más casuísticas: promociones digitales y físicas, y el source si es digital.
  - Sirve a: C-017, C-019, C-020, C-025, R-011, R-021, D-002, N-053, S3.3, S3.2

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
- Que la conversión de Hybrid frente a Self Service o Executive mide lo que aporta la intervención humana: los SDR/AE eligen a quién tocar, así que sin un grupo sin contacto elegido al azar es solo asociación.
- Las etapas propuestas de Self Service (activación, señal de compra) o de Hybrid como si fueran las de Finora: son propuesta. Ni siquiera sabemos si hay prueba gratis, freemium o pago al registrarse.
- Que el funnel de ejecutivos tiene criterios de etapa definidos: el brief da la secuencia y un traspaso SDR → AE que ocurre «sobre todo» y «normalmente»; qué hace a un lead Engaged o SQL no está definido.
- Tasas de etapas intermedias comparadas entre rutas (SQL contra activación) como si midieran lo mismo.
- La ruta de un pagador (Self Service, Hybrid o Executive) inferida del monto o del ticket de entrada.
- Que «más leads» es más demanda: sin quitar no-prospectos, duplicados y compradores que cambiaron de puerta, son más registros.
- Que un artefacto de medición quedó descartado con los datos del caso: con los pagos solo se acotan los del lado de pagadores; los del lado de leads necesitan el CRM.
- Que la caída post-SQL es un problema del AE: puede nacer antes del traspaso (SQL inflados) o en la oferta.
- Que en Finora cambiaron las metas o comisiones de SDR/AE, el precio o la competencia: son causas candidatas sin evidencia en el caso.
- Que comparar entradas directas a SQL contra SQL del SDR es un experimento: vienen de orígenes distintos; solo sirve comparar cómo cambia cada grupo en el tiempo, y aun así es asociación.

## 7. Decisiones necesarias
- Qué unidad cuenta como entrada (contacto, usuario, oportunidad o cliente).
- Qué significa adquirir un cliente para el CRO: cerrar una venta, primer pago o suscripción activa.
- Qué es «Executive» en la Lámina 3: la ruta de entrada directa a SQL o un segmento de cuentas con KAM. Define si las columnas separan cómo compra el cliente o quién es.
- Qué decisiones del CRO asumimos explícitamente para la columna «Decision Making», dado que el caso no las define.
- Cómo se arma el funnel híbrido: una secuencia con varias puertas de entrada, un funnel por motion que converge en el pago, o cohortes de entrada con plazo fijo (ver alternativas de este turno).
- Qué MRR es el titular cuando existan descuentos: el de antes de descuento (valor de la suscripción), el cobrado, o ambos con el descuento como línea del puente.
- Qué entra en «revenue que dejamos de capturar por decisiones comerciales»: solo descuentos temporales o también otras concesiones, como una tarifa negociada.
- Si el mecanismo de descuentos temporales se propone desde cero como supuesto declarado, dado que no sabemos qué tiene definido Finora.
- Nombres en C-005: ¿Hybrid ocupa el lugar de Assisted y Executive queda como el funnel de ejecutivos (SDR → AE)? Si es así, se cierra la duda de si Executive era la entrada directa a SQL o cuentas con KAM, y C-005 pasaría a tener dos puertas (producto y comercial), tres rutas, un loop de Reactivate y el nudo común.
- Regla de asignación: medir la conversión por puerta (fija al entrar) y usar la ruta Self Service / Hybrid / Executive para describir cómo llegaron al nudo, o tratar cada ruta como cohorte propia.
- Qué cuenta como intervención de una persona en Hybrid (cualquier contacto registrado de SDR/AE, o solo conversación real: llamada conectada, demo, propuesta) y si un formulario de «hablar con ventas» cuenta como tramo sin persona.
- Reactivate: loop con marca que reasigna a una ruta sin crear entrada nueva, o cuarta ruta con cohortes propias.
- Dónde va el lead de campaña que nadie contactó y compró solo: Self Service con puerta comercial, o una categoría propia de «no trabajado» (le sirve a H-006).
- Si S2.3 se abre en varias láminas (mix y regla · etapas por ruta · métricas por ruta) o se queda en una sola lámina con tabla.
- C-011: ¿«descartar» o «acotar» los artefactos de medición? Con los datos del caso solo se acotan los del lado de pagadores.
- C-011: ¿mantener ToFu/BoFu o pasar a ToFu · MoFu · BoFu · después del cierre? Velocidad de atención, capacidad, SQL inflados y estancados viven en el medio; Won que no paga, después.
- Cómo se presentan las causas en S2.6: como rivales (cuál gana) o como cadena (primera etapa que pierde conversión por cohorte de entrada).
- Si la calidad del lead se define con lo que se sabe al entrar (fuente, tamaño, industria, cargo, intención) y no con la conversión.
- Qué llega a los 5 minutos y qué se queda en el material de soporte. Propuesta: en los 5 minutos, solo la secuencia y el pedido de datos; y S2.6 se abre en dos láminas (paso 1 · paso 2) en el material de soporte.

## 8. Riesgos
- El esqueleto (Overview + 4 láminas de Growth + Revenue) es material de soporte; si se usa como la presentación de ≤5 min, no cabe.
- La Lámina 4 carga tres preguntas del brief (concentración + métricas, hipótesis + datos, solución analítica) y puede quedar como una lista de frameworks sin respuesta.
- El agente propio dentro de «Seguimiento» puede leerse como demo de herramienta si no se ata a una decisión concreta del CRO.
- Que las tareas de data_model y measurement terminen construyendo el modelo o métricas definitivas, contra D-007. El producto es la propuesta (qué campos, qué reglas, qué métricas), no la implementación.
- Catálogo de métricas sin decisión: mientras N-027 siga vacío, S2.5 puede volverse una lista. Cada métrica tiene que colgar de una decisión supuesta y declarada.
- Volumen: el plan queda en 14 tareas para un deck de ≤5 min. La mayoría alimenta el material de soporte; conviene priorizar por impacto × capacidad (D-005) y lanzar primero las que pueden ahorrar trabajo.
- Sobre-diseño: tres rutas × 5–7 etapas × cuatro familias de métricas sin saber qué decide el CRO (N-027). Puede salir una taxonomía que Finora no pueda instrumentar ni usar.
- Si CRM y producto no comparten ID de cuenta, Hybrid no se puede medir y la propuesta se queda en puertas (N-010).
- Si Reactivate cuenta como entrada, infla «más leads» con los mismos leads; es el mismo tipo de error que H-037.
- RT-016 ya estaba enviada: si el especialista ya arrancó con la respuesta anterior, pueden circular dos versiones del mix.
- Con más de diez causas, S2.6 puede volverse una lista; priorizar por la palanca del CRO que cambiaría.
- El paso 1 puede frenar todo si espera el CRM de Finora; por eso, un solo extracto para los dos pasos.
- Las seis causas nuevas pueden repetir alguna de H-001 a H-008 (su texto completo no está a la vista en este turno); revisar antes de aprobar.
- RT-005 compara capacidad contra calidad (H-006 vs H-005); los SQL inflados y los estancados sin seguimiento pueden confundir esa comparación si no se tienen a la vista.
- Cualquier comparación entre leads trabajados y no trabajados mezcla a quién eligió el SDR con lo que aporta el contacto (H-028, H-050).

---
## Anexo · lo capturado en la conversación
### Lo que Hugo piensa
- “con estas bservaciones hay cosas que cambian de los otros claims, no deberia de ser mucho pero consideralo, en general va por muy buen camino” (N-054)
- “C-013, quiero ver explicitamente el modelo de datos que se propone, as is vs to be” (N-052)
- “C-017 lo mismo quiero ver un modelo de datos y considera mas casuisticas, un descuento podría provenir de una promocion tanto digital como fisica y si es digital hay que considerar el source tambiem, como te digo, propuesta de modelo de datos, asi is vs to be tambien” (N-053)
- “C-021 está bien pero queria ver una prouesta aterrizada por casuistica de canal literalmente de los funeles asi como te pase la de new, working, SDR, engaged, bla bla quiero ver cuales aplican para los otros, la C-006 no la entiendo, pero tendria que relacionarse directamente con C-021 , ¿cada funnel? ¿cómo lo mides? no me refiero a solo medir la connversión, ¿que metricas hay en todo eso? Ej. Digital podría tener digital leads y CR digital, algo asi, Executive ya sabes que tiens New, pero tambien puedes tener métricas de tiempo de cierre, hay que hacer ese análisis, C-009 ¿hay otras métricas que debean de proponerse? De todo eso hay que ser explicitos en como se miden y siempre siempre ser MECE” (N-050)
- “lo mismo en C-023mucho artefacto pero no hay nada MECE, me confunde” (N-051)
- “faltan 2 cosas: en primer lugar rebotar más esas nos las pasarond e inicio, entonces hay que generar más causas potenciales, por lo menos 3-5 más y definir que datos tendrian que ser ciertos para validar o descartar cada una” (N-044)
- “Sobre C-011: Proponemos descartar primero artefactos de medición y después contrastar causas ToFu y BoFu” (N-045)
- “hay que bajar bien esa definición” (Q-063)
- “los que dicen que están estancados” (Q-064)
- “tambien tenemos otros Self Service con sus respectivos canales” (N-035)
- “y el otro era el funnel tradicionald e ejecutivos, lo importante es que cada uno tiene sus estapas, el de ejecutivos ya está bien definido y te lo acabo de pasar” (N-034)
- “tal vez añadir un reactivate que son los que dicen que están estancados pero hay formas de reactivarlos y asignarlos a un funnel de acuerdo al caso” (N-038)

### Hechos
- **N-030** Hoy el histórico de Finora tiene cliente + mes + monto pagado, y los cambios del monto entre meses se usan para clasificar movimientos: crecimiento, contracción, churn o reactivación. _(propuesto)_
- **N-033** El funnel comercial aproximado del brief es New → Working → Engaged → SQL → Demo → Proposal → Won. Los SDRs trabajan sobre todo las primeras etapas y después normalmente entra un Account Executive. _(propuesto)_
- **N-035** El brief describe la ruta sin ventas: algunos usuarios llegan directo al producto, se registran, lo usan y pagan sin necesariamente hablar con ventas. Otros entran al proceso comercial por campañas, referidos, partners o prospección. _(propuesto)_

### Observaciones
- **N-004** U05 · Primera aparición como cliente nuevo
- **N-005** U08 · Self-serve, SQL directo y semanas estancado
- **N-011** U15 · Tu Parte 3
- **N-020** Entre dos periodos aún sin fijar, los clientes activos observados crecen 4,5× y el monto pagado 2,8×. El monto pagado por cliente activo baja ~38% (≈COP 92,8 mil → 57,8 mil). Las tres cifras son una sola observación: el −38% sale de 2,8/4,5 ≈ 0,62.
- **N-036** El «sin necesariamente hablar con ventas» del brief ya deja espacio a Hybrid: algunos de los que entran por el producto sí hablan con una persona. Es el caso A de Hugo. _(propuesto)_

### Intuiciones de Hugo
- **N-001** U01 · Dos problemas conectados
- **N-003** U04 · Entraron muchos leads no calificados
- **N-026** Hugo lee que Finora tiene un problema de instrumentación comercial y digital (CRM y analítica).

### Supuestos
- **N-024** La Lámina 3 supone que Finora tiene tres motions distinguibles y que cada lead o cliente se puede asignar a una. El caso respalda self-service y proceso comercial asistido; «Executive» no aparece como ruta propia.
- **N-041** Para medir Hybrid hay que unir, por la misma cuenta, los toques de SDR/AE (CRM) y los pasos en el producto (registro, uso, pago). Los datos del caso no traen nada de eso y no sabemos si Finora lo tiene. _(propuesto)_
- **N-042** Self Service no genera oportunidad ni Won en el CRM. Si es así, el nudo común no puede ser Won y queda entre primer pago y suscripción activa. _(propuesto)_

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
- **Q-027** ¿PayrollExpenses y Team se solapan (los dos suenan a costo de personas)? ¿Los 5 meses con PayrollExpenses negativo son reversos o reclasificaciones, y en qué meses caen? _(propuesto)_
- **Q-028** ¿Qué le pedimos a Finora para cerrar el gasto (moneda y factor de escala, centro de costo y proveedor por rubro, método de asignación antes y después de jun-23)? ¿Lo contamos como hueco de su WoW en la respuesta? _(propuesto)_
- **Q-029** F-070 da el gasto por primer pagador con dos decimales, y en 2024 la diferencia con y sin Habilitación (0,04 vs 0,03 u) es del tamaño del redondeo. ¿Se reporta como índice 2022 = 100? _(propuesto)_
- **Q-030** Para Finora: ¿en qué unidad y moneda está el archivo de S&M? ¿Qué cambió en may/jun-23, cuando Team deja de ser un porcentaje fijo y Freelance pasa a cero: cambió lo que incluye el archivo o cambió la operación? _(propuesto)_
- **Q-031** Para Finora: ¿qué pasó alrededor de ene-23 y de jun-23? Por ejemplo: plan o precio de entrada, empuje de Self Service, cambios en Team, sistema de cobro o identificadores. _(propuesto)_
- **Q-032** Para el CRO: ¿cómo mide «ventas» (conteo de Won, primeros pagos o valor nuevo) y a qué periodo se refiere con «más leads, pero no más ventas»? _(propuesto)_
- **Q-033** ¿Qué significa 'New' en H-006: entradas o clientes nuevos? (La misma palabra aparece en H-001.) ¿Y qué meses son 'la caída'? Sin eso, la comparación de R-014 no tiene periodo base ni periodo de caída. R-012 (en curso) puede ayudar si fija el periodo del 4,5×, el 2,8× y el −38%. _(propuesto)_
- **Q-034** ¿Qué cuenta como 'compra' en la ventana fija de R-014: Won, primer pago o suscripción activa? El framing lo deja por acordar, y la prueba depende de eso. _(propuesto)_
- **Q-035** ¿El enunciado dice algo sobre Self Service (si existía sin SDR/AE en ambos periodos) o sobre cambios en la definición de lead, el formulario, la calificación o el reparto? Es el chequeo más barato antes de tratarlos como supuestos. _(propuesto)_
- **Q-036** ¿Octubre-24 está completo en los pagos? ¿Cómo queda jul–sep 2024 frente a 2023 sin octubre? _(propuesto)_
- **Q-037** ¿El tramo de 2023 con más primeros pagadores por mes que señala R-015 cae en jul–oct? Si es así, el −19% se compara contra un pico. _(propuesto)_
- **Q-038** ¿Qué hito usa el CRO como «venta» (Won, primer pago o suscripción activa)? ¿Habla de nivel («no más ventas») o de proporción («no crecen en la misma proporción»)? _(propuesto)_
- **Q-039** Si apruebas la regla de H-017: ¿cuántos meses sin pago se toleran antes de contar una salida, y cómo se reparte un pago que cubre varios meses? _(propuesto)_
- **Q-040** D-007 (activa) deja fuera las métricas definitivas y el modelo de datos. ¿Aplicaba solo a Framing? Si ya no aplica, ¿confirmas D-015 para que R-018, R-011, R-019 y R-021 entren al caso como propuestas trazables? _(propuesto)_
- **Q-041** ¿Pedimos ya a Finora la unidad y moneda del S&M, el margen o costo de servir, la facturación con periodo de servicio y el motion y canal de cada cliente? ¿O esos campos se quedan solo en la Propuesta de Modelo de datos? _(propuesto)_
- **Q-042** ¿Qué representa cada fila de raw.transactions (factura emitida, pago recibido o valor del periodo de servicio) y a qué fecha corresponde month? Es la pregunta a Finora que más desbloquea: decide si el monto se puede leer alguna vez como MRR. _(propuesto)_
- **Q-043** ¿Tiene Finora facturación o CRM con plan, cantidad, tarifa de lista con fechas y descuentos por suscripción? ¿Desde qué mes? ¿Hubo descuentos o cambios de tarifa entre 2022 y 2024? _(propuesto)_
- **Q-044** ¿Cómo cobra Finora: frecuencia de facturación, cargos de instalación, pagos parciales y política de mora? _(propuesto)_
- **Q-045** Para el CRO: ¿cómo calcula hoy «más leads, pero no más ventas» (conteos de período o cohortes con ventana cumplida)? ¿Desde cuándo llega más gente? ¿Cuánto tarda cada puerta en llegar al primer pago? Las tres respuestas deciden cuánto espacio tiene H-003. _(propuesto)_
- **Q-046** ¿Cómo define Finora cada puerta y existe Self Service real (compra sin intervención humana)? F-140 tiene confianza media justo en ese punto. Si no hay Self Service, el bowtie queda en dos puertas y la hipótesis puente se formula con la de menor valor. _(propuesto)_
- **Q-047** ¿Qué tabla respalda el 90–96% de activos en M3 por cosecha y el 18–38% de reactivaciones sobre entradas a pago que cita R-016? No veo ninguna tabla listada que los nombre (¿sale de T-002?). Sin tabla, esas cifras no entran a la story. _(propuesto)_
- **Q-048** ¿El gasto de S&M entra como cuarta fuente de la capa técnica, con unidad, clasificación funcional y, si se puede, desglose por motion y canal? Sin eso, los foros mensual (Inversión en Marketing) y trimestral (reparto entre Generación de Demanda, Team y Habilitación) de R-019 no tienen base. El archivo actual no documenta unidad (R-013, T-005) y en su primer tramo se comporta como una asignación de arriba hacia abajo (T-008, T-021). Además, según F-149, mover presupuesto pide experimentos, no solo tablero. _(propuesto)_
- **Q-049** ¿Qué explicaciones del CRO (H-001 a H-008) quedan contrastables con las fuentes de R-019? ¿Qué campos hay que añadir para H-005, H-006 y H-008, usando el dato mínimo que ya definen R-010 y R-014? _(propuesto)_
- **Q-050** ¿Cuál es el nudo del bowtie: Won, primer pago o suscripción activa? El framing lo deja por acordar, R-016 usa primer pago y la capa de decisión de R-019 depende de esa elección. _(propuesto)_
- **Q-051** ¿A qué periodo y a qué hito se refiere el CRO con «más leads, pero no más ventas»? Si es 2023 → 2024 y el hito es el primer pago, la meseta de primeras apariciones (54,2 → 55,4 por mes, F-078) es el tramo observado que le corresponde. Si es 2022 → 2024, el panel muestra lo contrario (27,2 → 55,4). _(propuesto)_
- **Q-052** ¿Qué cambió en Finora entre dic-22 y ene-23 (oferta, precio, canal de entrada, sistema de cobro o identificadores de cliente)? Ahí están el escalón de primeras apariciones (F-110/T-016) y la caída del ticket de entrada. Solo Finora lo puede contestar. _(propuesto)_
- **Q-053** Tomando solo a los clientes activos tanto en ene-22 como en oct-24, ¿su pago promedio sube o baja? Eso dice si el 97,4 mil significa que pagan más o que se fueron los que pagaban menos. Es un chequeo rápido con el propio panel. _(propuesto)_
- **Q-054** ¿Finora tiene tamaño de cliente (empleados, sedes) o plan contratado por cliente? Es lo mínimo para segmentar más allá de la industria (F-106). _(propuesto)_
- **Q-055** ¿Qué eran los pagos iniciales grandes de 2022 (setup, prepago, anualidad u otro)? Define si el ticket de entrada de 2022 es comparable con el de 2024. _(propuesto)_
- **Q-056** ¿Hay gasto de Generación de Demanda o leads por industria? Sin eso, la señal de Salud (F-104, F-105) no dice si conviene buscar más clientes ahí. _(propuesto)_
- **Q-057** Para Finora: ¿hubo algún cambio de oferta, plan de entrada, Canal de adquisición o forma de cobro hacia ene-23? Ese mes las altas observadas pasan de 26 a 60 (T-016), y la mediana del ticket de entrada baja de COP 63,0 mil a 36,8 mil entre 2022 y 2023 (F-083). _(propuesto)_
- **Q-058** Para Finora: ¿qué incluye el primer cobro de un cliente (prorrateo, cargo inicial, meses adelantados)? Sin saberlo, el ticket de entrada medido con el 1.er pago no es del todo comparable entre años (Q-012). _(propuesto)_
- **Q-059** Para Finora: ¿qué representa el monto del archivo de pagos: cobro emitido, pago recibido o neto de créditos? De eso depende cómo leer en el bloque CFO las reversiones y los ajustes retroactivos de F-090. _(propuesto)_
- **Q-060** ¿Finora tiene plan, cantidad y precio de lista, con fechas, en algún sistema (facturación o CRM)? Según R-021, es la condición para separar cantidad de tarifa en Q-002, con o sin descuentos. Si hay historial, quizá una parte del pasado sí se pueda descomponer. _(propuesto)_
- **Q-061** ¿Los contratos de Finora son mensuales cancelables o a plazo fijo? De eso depende si el descuento se lee en MRR neto, en revenue reconocido o en caja (F-153). _(propuesto)_
- **Q-062** ¿El monto de raw.transactions es lo facturado o lo cobrado, y un mes en cero genera fila? Chequeo mínimo con lo que ya tenemos: contar las filas con monto 0 y ver cuántas reactivaciones del puente (R-004) vuelven tras un solo mes de hueco y al mismo monto. _(propuesto)_
- **Q-063** ¿Qué cuenta como intervención de una persona para Hybrid: cualquier contacto registrado de SDR/AE o solo una conversación real (llamada conectada, demo, propuesta)? ¿Llenar un formulario de «hablar con ventas» cuenta como tramo sin persona? _(propuesto)_
- **Q-064** ¿Desde cuántos días sin actividad, y en qué etapa, un lead cuenta como estancado y entra a Reactivate? Es un parámetro que hay que acordar con Finora, no un estándar de mercado. _(propuesto)_
- **Q-065** Para Finora: ¿su CRM guarda, por lead, la fecha de creación y el origen (incluida la entrada directa a SQL), el dueño y la fecha de cada etapa, el motivo de descalificación y de pérdida, y un ID de cuenta que se una con facturación y con el registro en producto? ¿Cambiaron en el periodo las metas o comisiones de SDR y AE? Es el pedido único que sirve a los dos pasos de C-011. _(propuesto)_
- **Q-066** ¿De qué sistema sale el conteo de «clientes nuevos» del CRO (Won en el CRM o primer pago en facturación)? ¿Incluye cuentas que ya pagaron antes y qué ventana compara? La respuesta decide si H-037 aplica y en qué dirección. _(propuesto)_
- **Q-067** En el CRM de Finora, ¿«Reactivate» es un tipo de entrada como New (H-001) o un estado de cuenta? ¿Incluye a quien nunca pagó? _(propuesto)_
- **Q-068** ¿Qué regla de gracia usamos en el nudo para que una vuelta tras un solo mes en cero no cuente como entrada a pago? Condiciona el conteo MECE (F-156), el peso de Reactivate y el puente (T-003). _(propuesto)_
- **Q-069** ¿La mediana del 2.º pago de los primeros pagadores de jun–dic-22 sigue cerca de 52,5 mil si se sacan los de mar–may-22? Si baja hacia 36,8 mil, la base 2022 de R-026 incluye clientes previos al panel (H-041). _(propuesto)_
- **Q-070** ¿En qué mes de alta cae el escalón del ticket estabilizado: en dic-22/ene-23, junto con el salto de primeras apariciones de T-016 (H-024, H-045), o en jun-23 (H-025)? _(propuesto)_
- **Q-071** ¿Con qué monto se calcula el +6% de valor inicial incorporado de T-019? Si es con el primer pago, ¿cuánto da con el 2.º pago? _(propuesto)_
- **Q-072** ¿Qué representa el monto registrado: cobro por fecha de pago, factura o valor del mes de servicio? Es una pregunta para Finora y el chequeo más barato del caso: define la conciliación de H-048 y ordena H-031, H-034, H-039 y H-040. _(propuesto)_
- **Q-073** ¿La reactivación supera al MRR nuevo también fuera de oct-24 (F-176)? Ese es el mes de borde que H-029 marca como posiblemente incompleto; hay que verlo en el resto de 2024 antes de llevarlo a la story. _(propuesto)_
- **Q-074** ¿F-170 (COP 404 millones brutos y 62 netos) y R-004/T-003 son el mismo puente? Si los dos van de ene-22 a oct-24 con 62 de neto, las líneas de R-004 darían un churn de unos COP 69 millones y un bruto de unos 379, no 404 (cálculo propio). Puede ser una diferencia de ventana o de líneas; conviene cerrarlo antes de que la story cite ambos. _(propuesto)_
- **Q-075** ¿Qué parte del COP de contracción ocurre el mes siguiente a una reactivación que liquidó el hueco, o a un primer pago que es múltiplo exacto del pago siguiente? ¿En esos casos el cliente baja a su monto usual o por debajo? Es el corte que decide H-033 y la tensión entre R-011 y R-028. _(propuesto)_
- **Q-076** ¿El 44% de F-182 («vuelve a pagar al mes siguiente») es la misma medida que el de DM-4 en H-039 («con el mismo monto»)? ¿Cómo se reparte entre mismo monto, liquidación del hueco y otro monto, en conteo y en MRR? _(propuesto)_
- **Q-077** ¿Qué cifra de churn observado 2024 lleva la story: 1,9% (F-079, T-034) o 2,04% (F-175/T-077, F-183/T-085)? ¿Qué ventana y qué forma de promediar usa cada una? _(propuesto)_
- **Q-078** ¿Con qué definición entra Reactivate a la regla de prioridad: cualquier mes en cero, 2 o más meses, o meses en cero sin contar a quien paga exactamente los meses faltantes? La firma de atraso aparece en al menos 30% de los regresos tras 1 mes y en 29% tras 2 (R-023), así que exigir 2 o más meses no la limpia del todo. Es decisión tuya y de Finora; conviene resolverla junto con X-080. _(propuesto)_
- **Q-079** ¿Qué ventana usa la story para el peso de las reactivaciones en 2022? R-023 da 30,4% (feb–dic según H-058), R-016 llega a 38% y T-097 (mar–dic) da ~39%. Falta una tabla con las dos definiciones sobre la ventana limpia (mar-22 a oct-24, T-081). _(propuesto)_
- **Q-080** ¿Las etiquetas y el orden de R-023 significan lo mismo que tus definiciones textuales en R-029, donde Executive es el funnel actual SDR→AE? R-022 había puesto la carga por SDR/AE en Hybrid. Si no coinciden, cambian el orden de prioridad y la puerta donde se prueban H-006 y H-028. _(propuesto)_
- **Q-081** Para Finora: ¿qué cambió, y en qué fecha, entre dic-22 y oct-24 en la definición de lead, el formulario, la regla de calificación, el reparto, la cuota o meta del SDR, los precios y los planes? ¿Cuántos SDR y AE había cada mes? (Pone a H-027, H-054, H-056 y H-006 contra ene-23, jun-23 y jul-24.) _(propuesto)_
- **Q-082** ¿La caída de jul–oct 2024 en Retail+Producción es mayor que el peso de esas industrias en las altas de jul–oct-23, o solo refleja su tamaño? _(propuesto)_
- **Q-083** ¿Cómo se reparte la caída de jul–oct 2024 mes a mes: es pareja, se concentra en jul–ago justo después del pico de jun-24 (T-016) o ya se veía en ene–may-24? _(propuesto)_
- **Q-084** ¿La meseta 2023→2024 se sostiene comparando los mismos meses (ene–oct 2024 contra ene–oct 2023)? R-024 compara diez meses de 2024 con 2023 completo, y X-016 trae otra cifra con otros meses. _(propuesto)_
- **Q-085** ¿Las salidas observadas de dic-22 y ene-23 superan a las de los meses vecinos? ¿Las altas de ene-23 coinciden en monto e industria con churns recientes más que en la comparación de control, aunque el año 2023 completo no lo haga? (revisión mes a mes de H-024) _(propuesto)_
- **Q-086** ¿Enero trae su propio pico de primeros pagos? ¿ene-24 se separa de feb–may-24 igual que ene-23 de feb–may-23? _(propuesto)_
- **Q-087** ¿Finora aceptaría un holdout, es decir, dejar sin contacto de SDR/AE durante un periodo acotado a una muestra al azar de las entradas de una misma puerta? Es la forma de medir lo que aporta la intervención: comparar por puerta evita el sesgo de H-050, pero no mide ese aporte. _(propuesto)_
- **Q-088** Antes de un holdout: dentro de una misma puerta, ¿las entradas que los SDR/AE eligen tocar ya traían más señales de compra antes del contacto (actividad en producto, tamaño, fuente)? Es el chequeo observacional más barato de H-050. _(propuesto)_
- **Q-089** ¿Dónde quedan registrados quienes empiezan solos en el Self Service y no compran (registro, prueba, checkout)? ¿Hay una llave entre esa cuenta, la del CRM y el customer_id de pagos? Sin eso, la puerta Self Service no tiene denominador y F-212 no puede comparar su tasa. _(propuesto)_
- **Q-090** ¿Cómo se armó el archivo de S&M antes y después de jun-23? ¿El total hasta may-23 es gasto registrado o un monto repartido por porcentajes (Team 12% fijo)? ¿Hubo reversos o reclasificaciones de PayrollExpenses o Freelance en jun–ago-23? _(propuesto)_
- **Q-091** Con la misma data de R-030: ¿cuánto son el S&M por mes y los primeros pagadores por mes en mar-22–may-23, jun-23–jun-24 y jul–oct-24? ¿Cuánto da la correlación dentro de los dos tramos largos, en niveles y en cambios mes a mes? _(propuesto)_
- **Q-092** ¿Cuánto cambian F-214, F-215 y F-219 si se excluyen o netean los meses con PayrollExpenses negativo? ¿Ago-23 es uno de esos 5 meses? _(propuesto)_

### Desconocidos
- **N-013** Qué contamos como una persona o cuenta que entra. Un contacto, usuario, oportunidad y cliente no son necesariamente la misma unidad.
- **N-014** Qué entiende el CRO por adquirir un cliente: cerrar una venta, primer pago o suscripción activa.
- **N-015** Si primera transacción realmente significa cliente nuevo y si la historia y los IDs lo permiten.
- **N-016** Si el monto representa suscripción recurrente, facturación o cobro; y a qué periodo pertenece.
- **N-017** Si los meses están completos y la escala de Transactions ya fue multiplicada por 10.000 para llegar a COP.
- **N-018** Si Industry describe la industria actual o la de entonces, y qué clientes no tienen clasificación.
- **N-019** Si un resultado neto estable esconde aumentos y caídas que se compensan.
- **N-027** No sabemos qué decisiones quiere tomar el CRO con el funnel. La columna «Decision Making» de la solución está vacía.
- **N-043** No sabemos si Self Service tiene prueba gratis con fecha de fin, freemium o pago al registrarse. Eso cambia las etapas entre el registro y el pago. _(propuesto)_

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
- **N-034** Executive = el funnel tradicional de ejecutivos: las etapas del brief, con Working, Engaged y SQL a cargo del SDR, y Demo y Proposal a cargo del AE. Para Hugo ya está definido. Si lo confirma, se cierra la duda de si «Executive» era la entrada directa a SQL o un segmento de cuentas con KAM. _(propuesto)_
- **N-037** Hybrid = en el recorrido hubo al menos un tramo sin persona (Self Service) y al menos uno intervenido por una persona. Dos casos: A) empezó solo arriba y lo intervinieron abajo; B) lo contactaron como New y terminó solo. Falta definir qué cuenta como «intervención». _(propuesto)_
- **N-038** Reactivate (tentativo): leads estancados en alguna etapa que se pueden reactivar y reasignar a un funnel según el caso. _(propuesto)_
- **N-039** Regla MECE propuesta, en dos preguntas. 1) Puerta, fija al entrar: el registro nace en el producto o en el proceso comercial. 2) Intervención antes del nudo, contando tramos (pasar de una etapa a la siguiente): si ninguno lo movió una persona, es Self Service; si todos, Executive; si algunos, Hybrid. Reactivate es un loop con marca, no una ruta ni una entrada nueva, y sus acciones cuentan como intervención solo si las hace un SDR/AE. El canal es un atributo que cruza las tres rutas. La conversión se mide por cohorte de puerta y la ruta describe cómo llegaron al nudo. _(propuesto)_
- **N-040** Métricas MECE por ruta. En cada cohorte de entrada, a una fecha dada cada lead está en un solo estado: llegó al nudo, activo en una etapa, estancado, en Reactivate, perdido o descalificado. La suma da 100%. Encima, cuatro familias de métricas iguales para todas las rutas: volumen, conversión con plazo fijo, velocidad y valor al nudo. Entre rutas solo se comparan entrada, nudo y valor; las etapas intermedias se comparan dentro de cada ruta a lo largo del tiempo. _(propuesto)_
- **N-044** Ir más allá de las cuatro explicaciones que trae el caso (demanda, calidad, velocidad de atención, conversión post-SQL): rebotarlas (darles vueltas para sacar más) y sumar al menos 3–5 causas potenciales, cada una con lo que tendría que ser cierto en los datos para validarla o descartarla. _(propuesto)_
- **N-045** Orden para las explicaciones del CRO: primero descartar artefactos de medición (lo que se ve en los números por cómo se cuenta, no porque haya pasado en el negocio) y después contrastar causas ToFu y BoFu. _(propuesto)_
- **N-046** Ajuste propuesto a C-011, leído como orden de lectura y no de recolección: (1) acotar los artefactos, es decir, medir cuánto de la brecha explican, en vez de prometer que se descartan; con los pagos solo se acotan los del lado de pagadores (octubre-24, reactivaciones, IDs) y los del lado de leads (conteo, registro CRM, no-prospectos) necesitan el CRM; (2) pedir un solo extracto de datos que sirva a los dos pasos; (3) contrastar causas en ToFu (quién entra), MoFu (cómo se trabaja el lead), BoFu (si compra) y después del cierre (si paga). _(propuesto)_
- **N-047** Tratar «conversión post-SQL» como el lugar donde se nota la caída, no como causa. Detrás pueden estar SQL que llegan inflados desde antes del traspaso, capacidad del AE (H-006) u oferta, precio o competencia; cada una tiene una palanca distinta. _(propuesto)_
- **N-048** Definir la calidad del lead con lo que se sabe al entrar (fuente, tamaño, industria, cargo, señal de intención), no con si compró, y separar si cambió la mezcla de fuentes o si empeoró dentro de cada fuente. Si la calidad se define por la conversión, «bajó la calidad» explica cualquier caída y no se puede descartar. _(propuesto)_
- **N-049** Probar las causas como posible cadena, no como rivales: por cohorte de entrada con plazo fijo, localizar la primera etapa donde cambia la conversión. Las causas que viven en esa etapa o antes quedan en juego; las caídas de más abajo se leen primero como posible consecuencia. _(propuesto)_
- **N-050** Funnels por canal con sus etapas literales, y métricas MECE explícitas por funnel (no solo conversión): C-021, C-006 y C-009. _(propuesto)_
- **N-051** Las causas de C-023 deben ordenarse de forma MECE; tanto «artefacto» confunde. _(propuesto)_
- **N-052** C-013 debe mostrar explícitamente el modelo de datos propuesto, as-is vs to-be. _(propuesto)_
- **N-053** C-017 debe mostrar un modelo de datos as-is vs to-be con más casuísticas de descuento: promociones digitales y físicas, y el source si es digital. _(propuesto)_
- **N-054** Con estas observaciones cambian otros claims (poco); en general el Story va por buen camino. _(propuesto)_

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
- «Reactivate» (leads estancados, antes del nudo) no es la «reactivación» de mart.customer_month (pagadores que vuelven: H-034, H-037, H-039). En las láminas, «Reactivate de leads» frente a «reactivación de pagadores».
- «Executive», para Hugo, es el funnel de ejecutivos (SDR → AE). Un lector en inglés puede entenderlo como C-level o enterprise, así que la primera vez conviene escribir «Executive (SDR → AE)».
- Tres palabras para tres ejes, sin usarlas como sinónimos: puerta = por dónde nació el registro (producto o comercial); ruta = quién lo movió hasta el nudo (Self Service, Hybrid, Executive); canal = de dónde vino (Digital, WoM, partners, campañas…).
- «Tramo sin persona» = el cliente avanza solo en el producto; «intervención» = contacto registrado de SDR/AE. Llenar un formulario no es tramo sin persona (propuesta, por confirmar).
- «Rebotar», como lo usa Hugo, es darle vueltas a algo para sacar más ideas; mantenerlo.
- «Artefacto de medición» (término de Hugo): lo que se ve en los números por cómo se cuenta, no porque haya pasado en el negocio.
- Mantener ToFu y BoFu. Si se agrega el medio, «MoFu» lleva su significado en llano la primera vez: cómo se trabaja el lead entre New y SQL.
- Decir «causas potenciales», no «drivers»; «estancados» y «Reactivate» como los usa Hugo.
- «Acotar» (medir cuánto pesa) en vez de «descartar» cuando no se puede probar que un artefacto no existe.
