# CURRENT STORY — v4
> Generado 2026-09-30T11:03 · con problemas de validación

## Audiencia
CEO: contexto de salud general del modelo (Overview) antes de Growth y Revenue. Qué decide todavía no está definido., CRO: cómo definir, medir y operar el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos., CFO: cómo introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»: mecanismo, modelo de datos y clasificación.

## Objetivo
BORRADOR 4 para el deck de 5 minutos (N-055 a N-061, D-026). En Overview van C-001 y una lámina nueva que junta lo mejor de C-002, C-003 y C-004 y cierra conectando con Growth. En Growth van, en este orden: C-021 con la nota clave de C-005; una lámina nueva sobre cómo se mide cada funnel (sale de R-036 y usa tus definiciones de Hybrid B y Reactivate, que R-035 había cambiado); C-007; una lámina nueva con las métricas que hoy no existen, que incluye eficiencia y dice por qué proponemos cada una; C-023; una lámina nueva con el dato que valida o descarta cada hoja del árbol, en el mismo orden; y C-014 con la línea sobre cuenta común e historial de etapas. En Revenue van C-015, C-024, C-017, C-019 (que ya integra la regla de C-020) y C-025. Todo lo que sale de la presentación pasa a anexos. C-016 queda fuera porque la rechazaste. funnel-medicion y metricas-nuevas dependen de findings propuestos (F-243 a F-252). Quedan pendientes de aceptación, tuya o bajo tu delegación D-027, y el paquete no puede marcarse Ready hasta entonces.

## De → A
- **Hoy creen:** Finora suma clientes mucho más rápido que monto pagado. Esa brecha se lee con explicaciones que los pagos no confirman: «más leads que no convierten» y «cambios de suscripción o descuentos».
- **Deben salir creyendo:** La brecha coincide con quién entra: más primeros pagadores, con menor ticket estabilizado, dentro de cada industria. No coincide con la base previa, con las salidas persistentes ni con el gasto. El porqué del CRO y del CFO no está en los datos del caso, pero hay un diseño concreto para decidirlo: etapas por ruta, métricas por funnel y de eficiencia atadas a decisiones, un árbol con el dato de cada hoja, foros para operarlo y un modelo que separa el descuento de la suscripción.

## Governing thought
> La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos: proponemos medir por funnel y separar descuento de suscripción.

## Preguntas ejecutivas
- Q-003 (CEO) ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?
- Q-001 (CRO) ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- Q-002 (CFO) ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?
- Q-025 (CFO) Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿cómo se lee cada caso?
- Q-026 (CFO) ¿Qué pasa con el negocio subyacente y cuánto revenue dejamos de capturar por decisiones comerciales?

## Arco
SCR con pilares sobre tu guion aprobado (Overview → Growth → Revenue), en versión de 5 minutos — La respuesta va primero: la brecha coincide con quién entra. Overview la muestra y en una sola lámina junta las observaciones que la sostienen, hasta dejar la pregunta que los pagos no responden: por qué ruta, canal y etapa entra cada cliente. Growth contesta con una propuesta en este orden: cómo se recorre y cómo se mide cada funnel, dónde se concentra la pérdida, qué métricas faltan y para qué decisión, qué hipótesis hay y con qué dato se prueba cada una, y cómo se opera. Revenue va de lo que vemos a lo que no vemos, después al mecanismo y al modelo, y cierra con los casos del CFO resueltos con ese modelo.

### S1 · Overview
_Situación: Finora suma clientes mucho más rápido que monto pagado. En una lámina, las observaciones que lo acompañan: la base previa sostiene su monto, las cosechas nuevas lo diluyen y el gasto no acompaña a las altas. Cierra con la pregunta que abre Growth._

**C-001 · Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8×**

Entre ene-22 y oct-24 (ventana completa), los clientes con pago en el mes pasan de 377 a 1.678 (4,5×) y el MRR pagado observado, de COP 35,0 millones a COP 97,0 millones (2,8×). El MRR pagado observado por cliente activo baja de COP 92,8 mil a COP 57,8 mil (−38%). Esa brecha abre Growth (quién entra) y Revenue (qué se paga y por qué cambia).

- Pregunta: ¿Qué tan sano está el modelo si suma clientes mucho más rápido que monto pagado?
- Rol: context · confianza high · fuerza supported
- Evidencia: F-071, F-072, F-001, F-002, F-074 · Tablas: T-026, T-027, T-001
- Intención visual: Una línea: MRR pagado por cliente activo, en COP, de ene-22 a oct-24 (T-027): de COP 92,8 mil a 57,8 mil (−38%). Si hace falta la comparación, en apoyo: clientes activos y MRR pagado en la misma gráfica, cada uno con ene-22 = 100 (T-001), las dos líneas juntas.
- Limitación: Pendiente de tu aceptación: F-071, F-072, F-001, F-002 y F-074 están propuestos.
- Limitación: Es monto pagado observado (campo amount con escala fija), no MRR contratado (F-082).
- Limitación: Cliente activo = pago mayor que cero en el mes. Un cliente sin pago puede estar cancelado, en pausa o atrasado (F-082).
- Limitación: Es stock con ventana completa desde ene-22; los flujos arrancan en mar-22 (F-074).
- Limitación: El −38% no se presenta como deterioro de la salud: todavía no separa la mezcla de entrada, el precio y las salidas.
- En palabras de Hugo: “Finora suma clientes mucho más rápido que monto pagado (4,5× vs 2,8×; ~−38% por cliente activo). Esa brecha abre Growth y Revenue.”

**C-026 · La caída por cliente coincide con quién entra, y el gasto no acompaña las altas**

Mezcla: la base previa sostiene su monto (+5% por cliente entre ene-22 y oct-24, a COP 97,4 mil), mientras las cosechas 2023 y 2024 ya son 65% de los activos, con COP 46,3 mil y COP 43,0 mil por cliente. Entradas: los primeros pagadores observados pasan de 27,2 a 54,7 por mes en un escalón a inicios de 2023, y el ticket de entrada estabilizado baja (la mediana del segundo pago pasa de COP 52,5 mil en 2022 a COP 36,8 mil en 2023); según el monto usual temprano, 91% de ese cambio ocurre dentro de cada industria. Gasto: entre ene–may y jun–dic de 2023 el S&M por mes baja de 3,01 u a 1,44 u, mientras las altas suben de 45,2 a 60,6 por mes; además, la capacidad comercial pasa de 26% a 38% del S&M entre 2022 S1 y 2024 jul–oct, así que cruzar fechas no atribuye ventas. Lo que los pagos no dicen es por qué ruta, canal y etapa entra cada cliente, y esa pregunta abre Growth.

- Pregunta: ¿Qué observaciones sostienen los datos antes de entrar a Growth y qué dejan abierto?
- Rol: diagnosis · confianza medium · fuerza supported
- Evidencia: F-075, F-076, F-058, F-097, F-092, F-110, F-039, F-192, F-193, F-113, F-160, F-162, F-164, F-214, F-219, F-217, F-119, F-207, F-063 · Tablas: T-030, T-031, T-041, T-016, T-062, T-066, T-101, T-106, T-104
- Intención visual: Converge: tres observaciones (la base sostiene, las cosechas nuevas diluyen, el gasto va en sentido contrario a las altas) llevan a una sola pregunta abierta, por dónde y cómo entra cada cliente, que conecta con Growth.
- Limitación: Composición no es causa: no separa tipo de cliente, plan, tarifa ni descuento (F-093).
- Limitación: El peso de la composición depende de la base: 84% con dic-22 y 108% con ene-22. La dirección no cambia y la base la decides tú (X-060).
- Limitación: Primer pago observado no es adquisición. Won, primer pago o suscripción activa siguen por acordar (X-052).
- Limitación: El escalón de inicios de 2023 puede ser en parte registro (H-024) u operación (H-025, H-068): sin confirmar.
- Limitación: El ticket estabilizado sigue siendo monto pagado y no sigue bajando en 2024 (F-161).
- Limitación: El gasto está en unidad reportada, sin escala a COP (F-063), y Team queda fijo en 12% hasta may-23 (F-066). La asociación negativa en niveles no es efecto (F-119, F-219).
- Limitación: La industria es la única segmentación disponible: no sustituye al canal ni a la ruta.
- Limitación: El detalle de C-002, C-003 y C-004 queda en anexo.
- En palabras de Hugo: “«Las 3, 4 y 5 vamos a rescatar lo mejor para explicarlo en una lámina, para que vean que si llegué a las observaciones y conectar, para poder conectar con el siguiente bloque» (N-055).”

### S2 · Growth
_Cómo definir y medir el funnel si no todos lo recorren igual: etapas por ruta y cómo se mide cada funnel (S2.3). Dónde se concentra la pérdida (S2.4). Qué métricas nuevas proponemos y por qué (S2.5). El árbol de hipótesis y el dato que valida o descarta cada hoja (S2.6). Cómo operarlo (S2.7)._

**C-021 · Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño**

Proponemos una lista maestra, la del Executive (New → Working SDR → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won), y que cada ruta use solo las etapas que le aplican, con saltos permitidos y el canal como atributo de la entrada. El outbound del SDR recorre la lista completa, el inbound de «hablar con ventas» salta Working SDR y la entrada directa a SQL arranca en SQL. Self Service va New → Signup Self → Activated Self → Checkout Self → Won; Hybrid A arranca en producto y después suma etapas de SDR/AE, e Hybrid B arranca con SDR/AE y cierra por Checkout Self. Dueños propuestos: SDR hasta SQL, AE desde Demo, y Growth o Producto en los tramos sin persona. La ruta se clasifica al cierre según quién movió cada tramo: solo cuenta como intervención la interacción de ida y vuelta con SDR/AE, y el formulario de «hablar con ventas» es la entrada, no un tramo. Reactivate es un loop sobre estancados que conserva fecha y puerta, no una ruta más. Nota rescatada de la lámina de rutas: la puerta queda fija al entrar y es la única base para comparar tasas, porque la ruta se define por lo que pasó y eso sesga, por construcción, la conversión de Hybrid.

- Pregunta: ¿Qué etapas recorre cada ruta, por qué canal entra y quién es dueño de cada tramo?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-209, F-210, F-211, F-212, F-188, F-223, F-224, F-225, F-191, F-155, F-213 · Tablas: —
- Intención visual: Split: una lista maestra de etapas de la que cada ruta toma solo sus tramos, con el dueño de cada tramo y el canal como atributo de la entrada. Reactivate aparece como loop que devuelve estancados a su ruta.
- Limitación: Es una propuesta: el caso no trae CRM ni etapas, y hoy no se puede medir ninguna etapa antes del primer pago ni la puerta (F-223, F-191).
- Limitación: Las etapas del AE (Demo, Proposal) y la entrada por referido o partner están por confirmar contra el CRM de Finora.
- Limitación: No sabemos si Self Service existe como compra sin humano, ni si hay prueba gratis, freemium o pago al registrarse (Q-046).
- Limitación: Qué cuenta como intervención (Q-063) y el umbral de estancamiento por etapa (Q-064) son parámetros a acordar con Finora, no estándares de mercado.
- Limitación: Usa tus definiciones de Hybrid B y Reactivate. R-035 las había cambiado y aquí no se usa esa versión.
- Limitación: Una entrada que pide persona y que nadie atiende termina como Self Service con bandera (H-072).
- Limitación: Comparar la conversión de Hybrid con la de Self Service o Executive es asociación, no el aporte de la intervención (H-050).
- Limitación: La vuelta de pagadores que se ve en pagos es un loop de Revenue, no Reactivate (F-213).
- En palabras de Hugo: “Cómo definir y medir el funnel si no todos lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas). «6 se puede ir, pero si hay alguna nota importante plasmarla en 7, solo si es demasiado importante» (N-056).”

**C-027 · Proponemos medir cada funnel en sus etapas y compararlos solo en resultados comunes**

Cada funnel se mide con las mismas familias sobre sus propias etapas (volumen de entrada, alcance por etapa de la cohorte dentro de una ventana fija, tiempo por tramo y estancamiento), más la métrica de su mecanismo. En Executive: speed to lead del SDR y aceptación de SQL por el AE, separando la entrada por New de la entrada directa a SQL. En Self Service: alcance de New a Won sin persona. En Hybrid A: tasa de intervención y su uplift. En Hybrid B: salida a self-serve, brecha de MRR e incrementalidad del contacto. En Reactivate: tasa de reactivación, re-estancamiento y envejecimiento del pool. Entre funnels solo se compara la capa común (Won, MRR inicial, retención temprana, CAC y payback), cortada por funnel y conciliada contra las altas observadas en pagos. El funnel se asigna al cierre de la ventana con reglas explícitas: ¿nace de un estancado?, ¿quién inició?, ¿hubo toque humano?, ¿quién cerró? Hoy no se puede calcular ninguna métrica propia de funnel, porque el modelo empieza en el primer pago. Además, el uplift de los híbridos pide un holdout: comparar tocados contra no tocados reparte crédito, pero no prueba efecto.

- Pregunta: ¿Cómo se mide cada tipo de funnel y qué métricas específicas de cada familia mediríamos en cada uno?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-141, F-155, F-158, F-212, F-223, F-224, F-225, F-226, F-213, F-227, F-140, F-244, F-248, F-249, F-250, F-251, F-252 · Tablas: —
- Intención visual: Split y converge: a la izquierda, cada funnel con sus propias familias y la métrica de su mecanismo; todos convergen a la derecha en una capa común cortada por funnel. La conciliación con las altas en pagos cierra el lazo.
- Limitación: Pendiente de tu aceptación: F-248 a F-252 (R-036) y F-244 (R-035) están propuestos. Sin ellos el paquete no puede marcarse Ready.
- Limitación: R-035 cambió las definiciones de Hybrid B (entrada directa a SQL) y Reactivate (ex-clientes). De R-035 solo se reusa la capa común cortada por ruta de entrada.
- Limitación: La ventana, el múltiplo de estancamiento y el plazo del speed to lead son parámetros a acordar con Finora. Los benchmarks externos son contexto, no metas.
- Limitación: Won solo existe en las rutas con vendedor. Won y primer pago no son lo mismo, y la conciliación mide justamente esa brecha (X-052).
- Limitación: Las tasas de etapas intermedias no se comparan entre rutas (por ejemplo, SQL contra activación).
- Limitación: La «reactivación» de los pagos es la vuelta de clientes (loop de Revenue), no el Reactivate de leads (F-213, F-226).
- Limitación: El catálogo completo (fórmula, grano e hito por métrica) queda en anexo (R-036). Reemplaza a C-006.
- En palabras de Hugo: “«me gustaría saber como en cada tipo de funnel y que métricas especificas de cada una de esas categorias mediriamos por tipo de funnel, quiero otra propuesta de lámina ahi» (N-058).”

**C-007 · La pérdida está en el monto por cliente de cosechas de menor ticket**

Entre dic-22 y oct-24 el MRR pagado observado por cliente activo cambia −COP 31,7 mil (−35%). La descomposición asigna −COP 26,6 mil (84%) a la composición de cosechas y −COP 5,2 mil al efecto dentro de las cosechas. La caída aparece en las 6 industrias, pero es mayor en Servicios profesionales (−46,6%), Restaurantes (−45,6%) y Retail (−43,1%) que en Producción (−18,8%), Tecnología (−15,5%) y Salud (−14,4%); medido con el monto usual temprano, 96% del cambio del ticket de entrada 2022→2024 ocurre dentro de cada industria. No se asocia a salidas persistentes: el churn observado baja de 3,52% en 2022 a 2,04% en 2024, mientras el churn persistente pasa de 0,98% a 0,96%.

- Pregunta: ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento?
- Rol: diagnosis · confianza high · fuerza weak
- Evidencia: F-097, F-092, F-096, F-094, F-020, F-164, F-163, F-075, F-033, F-183, F-059, F-101, F-102 · Tablas: T-041, T-038, T-040, T-066, T-002, T-030
- Intención visual: Leak: el monto por cliente se diluye con la entrada de cosechas de menor ticket en todas las industrias, mientras las salidas persistentes se quedan planas.
- Limitación: El churn de 2024 cubre ene–jul, porque hace falta ventana de seguimiento. T-034 da 1,9% para 2024 con otra ventana (X-099, X-101).
- Limitación: Churn observado no es retención contractual. Persistente = no vuelve a pagar en el trimestre siguiente.
- Limitación: Quienes hacen churn pagan más en promedio, pero no en mediana: la salida de pocas cuentas grandes también baja el promedio (F-101, F-102).
- Limitación: La base de comparación (dic-22 o ene-22) está pendiente (X-060).
- Limitación: La industria es la única segmentación: no hay tamaño, canal ni ruta.
- Limitación: La burbuja de Salud (C-008) sale de la lámina por N-057 y queda en anexo como señal a validar.
- En palabras de Hugo: “Dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix).”

**C-028 · Proponemos métricas por ruta y de eficiencia, cada una atada a una decisión del CRO**

Hoy solo existe el lado del pago: MRR pagado observado y su puente, clientes activos, ARPA, churn observado y cohortes. La única eficiencia que se puede calcular es el S&M por alta en unidad reportada (0,105 u en 2022 y 0,036 u en 2024, −66%), y eso no es CAC. Proponemos sumar métricas en el orden del árbol, cada una por la decisión que habilita: entradas válidas y mezcla de ajuste al entrar (¿«más leads» es demanda comprable?); speed to lead, carga por SDR/AE y estancamiento por etapa (¿es capacidad o seguimiento?); aceptación de SQL por origen y tiempo de Won a primer pago (¿dónde se cae después del SQL?); y CAC en COP y payback por ruta y canal (¿dónde poner la siguiente unidad de S&M y de capacidad en el foro trimestral?). Para el CFO, el MRR contratado junto al pagado, el churn persistente con ventana de gracia y el ARPA de entrada estabilizado por cohorte y ruta dicen qué ruta trae MRR que se queda. El LTV con margen y el UCM esperan margen bruto y costo de servir.

- Pregunta: ¿Qué métricas proponemos que hoy no existen, incluida la eficiencia, y por qué cada una?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-135, F-136, F-137, F-138, F-139, F-081, F-141, F-144, F-146, F-148, F-227, F-231, F-232, F-246, F-247, F-249, F-252 · Tablas: T-036
- Intención visual: Split: cada métrica nueva conectada con la decisión del CRO o la hoja del árbol a la que sirve, con su semáforo de hoy frente al dato que falta.
- Limitación: Pendiente de tu aceptación: F-246, F-247, F-249 y F-252 están propuestos.
- Limitación: El CAC en COP y el payback piden documentar la unidad y moneda del gasto (F-063) y acordar qué es adquirir un cliente.
- Limitación: Sin ruta ni canal por cuenta no hay CAC por ruta ni por Digital/KAM (F-137, F-146). El magic number no tiene umbrales comparables (F-247).
- Limitación: Habilitación puede ser gasto comercial o de producto, y el nivel del S&M por alta cambia según cómo se cuente (F-068, F-069).
- Limitación: Lo que se pide como ARPU es ARPA: se mide por cliente, no por usuario (F-139). El ARR solo existe como run-rate, y solo si apruebas el MRR normalizado.
- Limitación: Reemplaza a C-009. C-009 y el proxy de CAC (C-010) quedan en anexo.
- En palabras de Hugo: “«por lo que veo falta lo de eficiencia pero por que proponemos esas métricas? tambien hay que dejarlo claro» (N-059).”

**C-023 · Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja**

Antes del árbol se fija qué es «venta» y qué ventana se compara, porque en los pagos la premisa cambia según la unidad y el trimestre que se elijan. Después, la brecha se reparte en orden por identidad (validez del lead, puerta, mezcla contra tasa, etapa y cobro) para que cada pedazo caiga en una sola hoja. Las ramas son: el aumento de New no es demanda comprable (no-prospectos, desfase o cambio de definición, misma demanda por otra puerta); entra peor mezcla (calidad al entrar); la caída está antes del SQL (capacidad y primer toque, estancados); está después del SQL (incentivos del SDR, decisión en Proposal); o está entre Won y el primer pago. Con el modelo del caso no se puede validar ni descartar ninguna hoja antes del cobro, y del cobro solo se ve el arranque: es una propuesta para correr con los datos del CRM.

- Pregunta: ¿Qué hipótesis ToFu y BoFu podrían explicar «más leads, pero no más ventas», ordenadas sin solapes?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-228, F-229, F-230, F-231, F-232, F-127, F-128, F-129, F-122, F-212, F-125 · Tablas: —
- Intención visual: Split: la brecha se reparte en ramas ordenadas y cada pedazo cae en una sola hoja. El Paso 0 (qué es venta y qué ventana) es la puerta de entrada al árbol.
- Limitación: Hojas e IDs: no-prospectos H-052, desfase o definición H-027/H-069, misma demanda por otra puerta H-053, calidad al entrar H-005, capacidad H-006, estancados H-055, incentivos del SDR H-054, decisión en Proposal H-056, Won → pago H-057.
- Limitación: La forma del árbol toca D-001 (tres ramas) y D-003. Si los reemplaza lo decides tú (X-150).
- Limitación: Metas o comisiones de SDR/AE, precio o competencia son causas candidatas sin evidencia en el caso.
- Limitación: La caída post-SQL no se atribuye al AE: puede nacer antes del traspaso (SQL inflados) o en la oferta.
- Limitación: Con los pagos solo se acotan artefactos del lado de pagadores; los del lado de leads piden el CRM.
- Limitación: El árbol completo con las palancas del CRO (R-032) y C-011 quedan en anexo.
- En palabras de Hugo: “Definir qué hipótesis ToFu y BoFu (demanda, calidad, velocidad de atención, conversión post-SQL) podrían estar afectando su motor; aquí no hay que hacer research en data, es una propuesta.”

**C-029 · Cada hoja del árbol tiene firma y dato propios; hoy no están en el caso**

Una hoja se valida si, al controlarla, la brecha se cierra en esa magnitud, y se descarta si queda igual; siempre con datos que no dependan de lo que Sales opine después. En el orden del árbol: venta y ventana, con la fecha de entrada y de venta por cuenta; no-prospectos, con el export de leads cruzado con customer_id (¿sube la proporción de duplicados, clientes actuales o spam?); desfase o definición, con una bitácora fechada de cambios de formulario, regla o reparto; misma demanda por otra puerta, con la puerta por cuenta y el cruce de identidad; calidad al entrar, con señales congeladas al crear el lead (empeora la mezcla de ajuste y no la tasa por banda); capacidad, con el primer contacto humano y un roster semanal de SDR/AE con ramp (la tasa cae en entradas lentas y en semanas de alta carga); estancados, con el historial de etapas y la última actividad (crece la bolsa y los retomados sí compran); incentivos del SDR, con la aceptación del AE por origen del SQL; decisión en Proposal, con motivos validados con compradores; y cobro, con la fecha de Won y la llave CRM ↔ customer_id. Ninguno de esos datos está en el caso (del cobro solo se ve el arranque en los pagos), y el gasto de Team no sirve como proxy de capacidad.

- Pregunta: ¿Qué datos usaríamos para validar o descartar cada hipótesis del árbol?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-121, F-122, F-127, F-128, F-129, F-228, F-229, F-230, F-231, F-232, F-207, F-225, F-191, F-120, F-124, F-126, F-159 · Tablas: —
- Intención visual: Split alineado: cada hoja del árbol, en el mismo orden, con su firma, qué la valida, qué la descarta, su dato mínimo y si ese dato existe hoy en el caso.
- Limitación: Es una propuesta: que esos datos no estén en el caso no prueba que Finora no los registre (H-076).
- Limitación: Los motivos de pérdida del CRM no alcanzan para la decisión en Proposal (F-129).
- Limitación: Separar capacidad de calidad con mezcla contra tasa es observacional. Probar la palanca (que más capacidad recupere compras) pide un experimento (F-159), y la priorización de los reps confunde la relación entre tiempo de contacto y compra (H-028).
- Limitación: La banda de ajuste se fija al entrar y se valida en el periodo base antes de usarla.
- Limitación: La ventana de deduplicación, los días de estancado y el SLA son propuestas a acordar con Finora.
- Limitación: Sigue las hojas y el orden de hipotesis-matriz. Reemplaza a C-012, que queda en anexo.
- En palabras de Hugo: “«y qué datos usarías para validar o descartar cada una? se deberia responder con 16 pero no me queda claro tampoco deben relacionarse estas 2» (N-060).”

**C-014 · Proponemos una vía formal por foro y otra de agentes para el día a día**

Vía formal: dashboards automatizados por foro sobre métricas gobernadas. El foro semanal decide oportunidades, estancamientos y handoffs; el mensual, la mezcla de ruta y canal; el trimestral, la inversión y la capacidad. Cuando un foro lo pida se suman análisis ad hoc por hoja del árbol. Vía del día a día: agentes de IA montados encima, que solo lean métricas gobernadas y entren con un piloto controlado; la atribución reparte crédito, pero para decidir presupuesto hacen falta experimentos. Antes de todo esto, operar el funnel pide la cuenta común (un ID que una CRM, producto, facturación y pagos) y el historial de etapas con fechas, que el CRM suele traer de forma nativa.

- Pregunta: ¿Qué solución analítica le permite al CRO operar el funnel de forma recurrente y qué decisiones le habilita?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-147, F-148, F-149, F-144, F-238, F-240, F-242, F-145 · Tablas: —
- Intención visual: Split: una vía formal que baja por foros atados a decisiones y una vía de agentes para el día a día, las dos encima de una base común (cuenta y etapas).
- Limitación: Las decisiones del CRO por foro son propuesta: todavía no están definidas con Finora.
- Limitación: La cuenta común y el historial de etapas no están en el caso: las tres fuentes de hoy son de después del pago (F-238). El as-is vs to-be completo queda en anexo (C-013, R-033).
- Limitación: Lo que no se capture desde ya no se reconstruye después, salvo que Finora tenga historial en sus sistemas (F-242).
- Limitación: Con pagos observados, el CRO confundiría el momento de cobro con churn y expansión. La facturación es la primera pieza técnica (F-145).
- Limitación: D-007 sigue activa y choca con D-018 (propuesta) sobre si las propuestas de diseño entran a la historia.
- En palabras de Hugo: “Proponemos dos vías: una formal y ejecutiva a través de dashboards adhoc a los foros recurrentes y otro para preguntas del día a día a través de agentes.”

### S3 · Revenue
_Con solo el monto pagado se ve qué cambió, pero no por qué. Proponemos que el descuento sea un objeto propio, con su origen, y una escalera de valor con su regla de clasificación. Con ese modelo respondemos los casos del CFO._

**C-015 · Lo observable es el primer y segundo pago; el descuento no es verificable**

Del histórico se saca el ticket de entrada: la mediana del primer pago observado de las altas es COP 63,0 mil en 2022, COP 36,8 mil en 2023 y COP 42,0 mil en 2024, y la del segundo pago, COP 52,5 mil, COP 36,8 mil y COP 38,9 mil. El segundo pago coincide exactamente con el primero en 73,5%, 90,3% y 77,3% de las altas. El primero supera con holgura al segundo en 23,2% de las altas de 2022, frente a 7,1% en 2023 y 11,6% en 2024, un patrón que no dice si el primer pago incluye un cargo inicial, un cobro atrasado o un precio distinto. Con cliente, mes y monto no se pueden separar lista, descuento, crédito ni pausa, y la huella de un descuento temporal limpio casi no aparece: eso es consistente con que los descuentos sean algo por introducir, pero no prueba que no existieran.

- Pregunta: ¿Qué data observable de pricing introductorio podemos sacar de los pagos?
- Rol: evidence · confianza medium · fuerza supported
- Evidencia: F-083, F-160, F-166, F-086, F-087, F-134, F-093 · Tablas: T-051, T-062, T-054, T-055
- Intención visual: Converge: el primer y el segundo pago se juntan después de 2022. Lista, descuento, crédito y pausa quedan fuera del dato.
- Limitación: Primer pago observado no es adquisición. El primer pago de 2022 incluye pagos iniciales grandes (F-166).
- Limitación: Es monto pagado, no MRR contratado: no hay catálogo de precios ni definición del campo (F-093).
- Limitación: Que la huella limpia de descuento sea escasa no prueba ausencia (F-134).
- Limitación: No se afirman descuentos a partir del tamaño de un salto del monto.
- En palabras de Hugo: “Qué data observable de pricing introductorio podemos sacar.”

**C-024 · Con cliente, mes y monto se ve qué cambió, no por qué**

Con cliente, mes y monto se arma el puente del MRR pagado observado, pero el monto mezcla fecha de cobro con mes de servicio. 29% del MRR de expansión se revierte al mes siguiente, 44% de los churns observados vuelve a pagar al mes siguiente y 42,6% del MRR de reactivación llega con un monto que cubre los meses del hueco más el corriente. La contracción no muestra esa firma (88,9% sigue igual o más abajo al mes siguiente), pero tampoco dice si fue suscripción, tarifa o descuento. Semáforo: en verde, el MRR pagado observado y su puente, los clientes activos, el ARPA, el churn observado y las cohortes; en amarillo, el MRR normalizado y el churn con ventana de gracia, que piden una regla que apruebes; en rojo, lista, descuento y MRR contratado.

- Pregunta: ¿Qué se puede leer hoy del MRR con cliente, mes y monto, y qué no?
- Rol: diagnosis · confianza high · fuerza supported
- Evidencia: F-172, F-174, F-180, F-182, F-184, F-185, F-135, F-136, F-186, F-213 · Tablas: T-074, T-076, T-082, T-086, T-087
- Intención visual: Split: lo que el monto deja ver (qué cambió) frente a lo que no separa (por qué), con el semáforo verde, amarillo y rojo.
- Limitación: La prueba de contracción solo mira el mes siguiente (X-100).
- Limitación: El 44% vuelve a pagar, pero no necesariamente con el mismo monto (X-102, X-145).
- Limitación: El puente normalizado exacto no se puede medir: no hay periodo devengado por pago (F-186).
- Limitación: No se usan etiquetas contractuales (alta, baja, expansión) sin vigencia verificada.
- En palabras de Hugo: “Revenue: con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento).”

**C-017 · El descuento se registra como objeto propio, con origen, source y fecha de fin**

Mecanismo propuesto: cada descuento vive como objeto propio (tipo, valor, inicio, fin pactado y real, alcance, motivo y aprobador) y tiene un solo origen: promoción con su oferta, código y canje; negociación; retención; o partner. Va separado de la cantidad contratada y del precio de lista, para que ni un precio especial ni un downgrade de retención escondan un descuento. El source se captura en la adquisición de todos los clientes, no solo en el código, y el código guarda aparte el canal asignado y su medio (digital, físico o QR). Además, sin estado de suscripción un mes gratis se confunde con churn, como pasa hoy, cuando 44% de los churns observados vuelve a pagar al mes siguiente. Implicaciones multidisciplinarias: Finanzas declara la convención de cómo pega el descuento en el MRR y qué vista usa (MRR neto, revenue o caja, según los contratos sean mensuales o a plazo fijo); Marketing marca las cohortes con descuento y las mide contra un grupo comparable; Ventas y CS registran aprobaciones y casos de retención; y Datos construye el modelo.

- Pregunta: ¿Cómo debería Finora introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-233, F-234, F-235, F-236, F-237, F-150, F-151, F-152, F-153, F-154, F-174 · Tablas: T-076
- Intención visual: Converge: todos los orígenes (promoción, negociación, retención, partner) desembocan en un solo objeto descuento, separado de la suscripción y del precio de lista, con sus implicaciones por área.
- Limitación: Funciona hacia adelante: el histórico no trae tarifas ni descuentos, y no hay cifra histórica de revenue no capturado.
- Limitación: La evidencia externa asocia la adquisición con descuento a clientes de menor valor, y el churn al vencer el descuento tiene otras causas posibles (F-154).
- Limitación: La convención «fin de descuento no es expansión» se aparta del default del mercado y hay que declararla (F-236).
- Limitación: Si el source solo vive en el código, el código se vuelve la única atribución (H-073). Sin la regla «precio especial = lista + descuento», parte de los descuentos quedaría como precio menor (H-074).
- Limitación: La lámina de convención y capas (C-018) queda en anexo; aquí queda en una línea.
- En palabras de Hugo: “Cómo debería Finora introducir descuentos temporales (mecanismo propuesto, implicaciones multidisciplinarias, preguntas del CFO contestadas con el modelo propuesto).”

**C-019 · La Propuesta de Modelo de datos separa el valor en una escalera con vigencias**

Proponemos una escalera por suscripción y mes, en la que cada peldaño tiene su fuente y su vigencia: tarifa de lista → precio pactado (plan, cantidad, add-ons) → descuento → MRR neto → facturado → cobrado. Los movimientos de MRR (nuevo, expansión, contracción, churn, reactivación, tarifa y «Descuento») se clasifican comparando cierres de mes sobre los peldaños de valor. Lo facturado y lo cobrado son caja y solo generan un efecto de cobro, y el panel actual queda como capa de monto pagado observado que se concilia contra lo cobrado. Regla de clasificación: si la suscripción no cambia, el inicio o el fin de un descuento va a la línea «Descuento», nunca a contracción ni a expansión. Si suscripción y descuento cambian el mismo mes, primero se mide el efecto de la suscripción con los términos de descuento previos y el resto va a «Descuento». Quien sale con un descuento vigente cuenta como churn, sin registrar un fin de descuento.

- Pregunta: ¿Cómo separar el valor de la suscripción del precio efectivamente pagado y clasificar el inicio y el fin de un descuento?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-130, F-132, F-133, F-150, F-151, F-152, F-168, F-234, F-236, F-240, F-241 · Tablas: —
- Intención visual: Escalera: del valor de lista al monto cobrado, peldaño por peldaño y con vigencia. Los movimientos de MRR se leen en los peldaños de arriba y la caja, abajo.
- Limitación: Las reglas que son decisiones de negocio tienen que quedar escritas antes de construir (F-241): convención del descuento, tarifa como línea propia, descuento porcentual que escala, recurrente contra único y mes gratis contra pausa.
- Limitación: Mide hacia adelante, salvo que Finora tenga historial en sus sistemas (F-242).
- Limitación: Los nombres de las tablas son ilustrativos (R-011, R-034).
- Limitación: Integra la regla de clasificación de C-020, que queda en anexo, como anticipaste en la nota de S3.4.
- En palabras de Hugo: “Cómo separar el valor de la suscripción del precio efectivamente pagado: propuesta de modelo de datos (campos, tablas, definiciones); la clasificación probablemente la integra la misma propuesta.”

**C-025 · Con el modelo propuesto, cada caso del CFO se lee en su capa**

Si paga 100 y luego 80, el modelo lo registra como contracción si bajó la suscripción, o como inicio de descuento si el valor de lista no cambió; hoy el panel marca los dos casos como contracción. Si la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100, se registran una expansión de +30 y un inicio de descuento de −30, y el neto no cambia; cuando el descuento desaparece, ese +30 va a «fin de descuento», no a expansión. El negocio subyacente se lee en el MRR de lista, y el revenue que dejamos de capturar, en la línea «Descuento» por origen, de aquí en adelante. Con el histórico solo se ve composición: el MRR pagado por cliente activo baja de COP 92,8 mil a COP 57,8 mil (−38%), con la base previa en +5%.

- Pregunta: (CFO) Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿cómo se lee cada caso, qué pasa con el negocio subyacente y cuánto revenue dejamos de capturar?
- Rol: recommendation · confianza medium · fuerza weak
- Evidencia: F-168, F-172, F-174, F-177, F-178, F-150, F-151 · Tablas: T-080, T-074, T-076
- Intención visual: Split por capas: cada caso del CFO cae en la capa que lo explica (suscripción, descuento, neto), frente a la lectura única que da hoy el monto pagado.
- Limitación: Los casos son ejemplos del enunciado, no observaciones de Finora: prueban qué se puede distinguir, no qué pasó (X-097).
- Limitación: Sin precios ni descuentos registrados, una lista mayor con descuento y un precio neto menor dan el mismo monto (F-177).
- Limitación: No hay cifra histórica de revenue no capturado ni puente histórico por tarifa y descuento.
- Limitación: La composición no es beneficio comercial (F-178). Q-026 junta dos preguntas distintas (X-072).
- En palabras de Hugo: “Preguntas del CFO contestadas con el modelo propuesto.”

## Recomendaciones
- Fijar la base de comparación del Overview (ene-22 o dic-22) y reportar siempre el monto por cliente partido en base previa y cosechas. _(si Antes de publicar el Overview.)_
- Definir qué es «venta» (Won, primer pago o suscripción activa) y con qué ventana se compara, como Paso 0 del árbol. _(si Antes de llevar el árbol al CRO: si no se fija, la premisa cambia según el trimestre que se compare.)_
- Pedir a Finora el export de leads (id, fecha, fuente, dominio) cruzable con customer_id, el historial de etapas con fechas y un roster semanal de SDR/AE con ramp. _(si Si existen en su CRM. Que no estén en el caso no prueba que no los registre.)_
- Etiquetar hacia atrás, desde el CRM, la puerta de los pagadores del periodo del caso, usando solo información previa al contacto. _(si Si el CRM conserva la información al entrar. Es la prueba más rápida para ver si la puerta se asocia a la mezcla de entrada.)_
- Acordar con Finora los parámetros del funnel: ventana por ruta, qué cuenta como intervención, umbral de estancamiento por etapa y plazo del speed to lead. _(si Antes de construir tableros: son parámetros de Finora, no estándares de mercado.)_
- Documentar la unidad y la moneda del archivo de S&M y si Habilitación es gasto comercial, para pasar de S&M por alta a CAC en COP y payback por ruta y canal. _(si Si el CFO quiere una eficiencia comparable: hoy es un proxy en unidad reportada.)_
- Probar el valor de la persona en los híbridos con un holdout: una muestra al azar de entradas que cumplen el disparador y no se contactan. _(si Si el CRO va a decidir capacidad por lo que aporta la intervención y no solo por repartir crédito.)_
- Levantar la cuenta común y el historial de etapas, y montar los foros semanal, mensual y trimestral sobre métricas gobernadas. Los agentes entran después, con un piloto controlado. _(si Una vez confirmadas las definiciones: lo que no se capture desde ya no se reconstruye.)_
- Que el CFO declare la convención del descuento en el MRR y apruebe por escrito las reglas del modelo: tarifa, descuento que escala, recurrente contra único y mes gratis contra pausa. _(si Antes del primer descuento temporal.)_
- Registrar desde el primer descuento el objeto descuento con origen, vigencia y aprobador, y capturar el source en todas las altas. _(si Si Finora lanza descuentos temporales: el histórico no se reconstruye.)_
- Aprobar o descartar una regla de normalización del monto con ventana de gracia antes de llamar churn o MRR a los movimientos observados. _(si Si quieres pasar el churn y el MRR normalizado del semáforo amarillo al verde.)_

## Apéndice candidato
- Observaciones de Overview y Growth fundidas en overview-observaciones — N-055: lo mejor de C-002 (overview-mezcla: mezcla por cosecha y base de comparación), C-003 (growth-entradas: escalón de altas y ticket estabilizado por industria) y C-004 (growth-gasto: S&M por categoría, correlaciones y las gráficas de R-030) pasa a una sola lámina. El detalle queda de respaldo.
- Rutas con puerta y canal fijos al entrar — N-056: sale de la presentación. Su nota más importante, que la puerta fija al entrar es la única base para comparar tasas, queda dentro de funnel-etapas (C-021).
- Versiones anteriores reemplazadas por láminas nuevas — C-006 (funnel-conversion) → funnel-medicion (N-058); C-009 (metricas-semaforo) → metricas-nuevas (N-059); C-012 (hipotesis-capacidad) → hipotesis-datos (N-060). Se conservan sin cambios.
- Láminas de Growth que salen por N-057 — C-008: Salud con menor churn persistente, ticket alto y poco volumen, señal a validar. C-022: cada métrica en un solo lugar, con dueño, fuente y foro. C-010: S&M por alta en unidad reportada, que no es CAC; su dato queda dentro de metricas-nuevas. C-011: primero se fija qué es venta; revisar la medición en pagos no cierra la brecha.
- Láminas de Revenue que salen por N-057 — C-018 (el CFO decide la convención; MRR neto, revenue y caja se separan) queda como una línea en descuento-objeto. C-020 (regla de inicio y fin de descuento) queda integrada en modelo-escalera y se aplica en cfo-casos.
- Modelo de datos del funnel, as-is vs to-be — No la mencionaste, así que va al anexo. operar-foros conserva la línea de que operar el funnel pide la cuenta común y el historial de etapas.
- Catálogos y diseños completos de los especialistas — Respaldo para preguntas: catálogo MECE de métricas por funnel con fórmula, grano e hito (R-036; R-035 usa otras definiciones de Hybrid B y Reactivate), etapas literales por ruta y canal (R-031), árbol completo con palancas del CRO (R-032), métricas con semáforo (R-018), modelo de precios y descuentos con casuísticas (R-034) y escalera de valor (R-011).

## Preguntas sin resolver
- S2.1 · ¿Qué relaciones concretas quieres mostrar en «Las relaciones que comentó Hugo»? La lámina queda missing y no se rellena.
- ¿Confirmas D-018 (las propuestas de diseño entran a la historia como propuesta) frente a D-007, que sigue activa? El paquete las incluye como propuesta.
- ¿El árbol de hipotesis-matriz reemplaza las tres ramas de D-001? ¿Y cómo queda D-003? (X-150)
- ¿Qué es «venta» para el CRO (Won, primer pago o suscripción activa) y con qué ventana se compara? (Paso 0 del árbol; X-052)
- ¿Existe Self Service como compra sin humano? ¿Hay prueba gratis, freemium o pago al registrarse? (Q-046)
- ¿Qué cuenta como intervención y cuál es el umbral de estancamiento por etapa? (Q-063, Q-064)
- ¿Cuáles son las etapas literales del AE (Demo, Proposal) y existe la entrada por referido o partner? Hay que confirmarlo contra el CRM.
- R-035 cambió las definiciones de Hybrid B y Reactivate; el paquete usa las tuyas (R-029, R-031, R-036). ¿Lo confirmas?
- ¿Qué unidad y moneda tiene el archivo de S&M? ¿Habilitación (SoftwareTools, Freelance) es gasto comercial o de producto? (X-002)
- ¿Qué base de comparación usa el Overview: ene-22 o dic-22? (X-060)
- Churn observado de 2024: 1,9% en T-034 frente a 2,04% en T-002. Hay que conciliar las ventanas antes de publicar (X-099, X-101).
- ¿Los contratos de Finora son mensuales cancelables o a plazo fijo? De eso depende qué vista aplica con descuentos: MRR neto, revenue o caja (F-153).
- ¿Qué parte del to-be ya existe en los sistemas de Finora, como un CRM con historial o la facturación? (H-076, X-160)
- Pendiente de aceptación: F-243 a F-252 (R-035, R-036), de los que dependen funnel-medicion y metricas-nuevas.

## Validación
- ✖ C-007: cifra(s) sin tabla que las respalde: −COP 31,7 mil, −COP 26,6 mil, −COP 5,2 mil.
- ✖ C-025: cifra(s) sin tabla que las respalde: +5%.
- ⚠ Láminas del guion sin evidencia todavía: S2.1 (van a research, no se rellenan).
- ⚠ Láminas del guion con evidencia parcial: S2.2.
