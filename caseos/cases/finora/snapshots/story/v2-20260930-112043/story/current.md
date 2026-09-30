# CURRENT STORY — v5
> Generado 2026-09-30T11:20 · válido

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

Proponemos medir cada funnel (Executive, Self Service, Hybrid A, Hybrid B y el loop de Reactivate) en sus propias etapas y con las mismas familias: volumen de entradas, alcance por etapa en cohorte de entrada con ventana fija (solo en cohortes que ya la cumplieron), tiempo por tramo, estancamiento y la métrica del mecanismo de cada ruta, como el speed to lead en Executive o el uplift de la intervención en Hybrid A, medido con holdout. Entre funnels solo se comparan resultados comunes desde el nudo (Won, MRR inicial, retención temprana, CAC y payback), siempre cortados por funnel, y las tasas se comparan por puerta, no por ruta. Con tus definiciones, Hybrid A empieza solo y luego interviene una persona, Hybrid B empieza con persona y termina solo, y Reactivate es el loop de los leads estancados; la vuelta de clientes que se ve en los pagos es otra población y se mide aparte. La clasificación sale de reglas explícitas al cierre de una ventana fija: si nace de un estancado, quién inició, si hubo toque humano y quién cerró. Hoy no se puede calcular ninguna métrica propia de funnel: el modelo empieza en el primer pago.

- Pregunta: ¿Cómo se mide cada funnel si no todos lo recorren igual, y qué se puede comparar entre ellos?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-141, F-155, F-158, F-212, F-223, F-224, F-225, F-226, F-213, F-227, F-140, F-244, F-248, F-249, F-250, F-251, F-252 · Tablas: —
- Intención visual: Split → converge: cada funnel se mide dentro de sus propias etapas y todos convergen en el nudo común, el único punto donde se comparan resultados.
- Limitación: Pendiente de aceptación: F-244, F-248, F-249, F-250, F-251 y F-252 están propuestos (R-035, R-036), tuya o bajo D-027.
- Limitación: Es propuesta: hoy no se puede calcular ninguna métrica propia de funnel (F-248, F-223).
- Limitación: La ventana fija, el nudo común (Q-050) y el umbral de estancamiento (Q-064) son parámetros a acordar con Finora, no estándar de mercado.
- Limitación: Comparar tocados contra no tocados en los híbridos asigna crédito, no prueba efecto: hace falta holdout (F-251, H-050).
- Limitación: Con la regla resumida, «¿quién cerró?» puede dejar sin ruta entradas que iniciaron con persona y no cierran en la ventana (H-078).
- Limitación: R-035 usa otras definiciones de Hybrid B y Reactivate; esta lámina sigue las tuyas (R-036).
- Limitación: Es el tercer catálogo del caso (R-031, R-035, R-036): falta consolidarlo en uno (X-170).
- En palabras de Hugo: “Mis definiciones: Hybrid A empezó solo y luego intervino una persona; Hybrid B empezó con persona y terminó solo; Reactivate es el loop de los estancados.”

**C-007 · La pérdida está en el monto por cliente de cosechas de menor ticket**

La pérdida no es sectorial: entre dic-22 y oct-24 el MRR pagado observado por cliente activo baja en las 6 industrias, con caídas de −46,6% en Servicios profesionales, −45,6% en Restaurantes y −43,1% en Retail, frente a −18,8% en Producción, −15,5% en Tecnología y −14,4% en Salud. Se concentra en las cosechas: la base previa sostiene su monto (COP 97,0 mil por cliente en dic-22 y COP 97,4 mil en oct-24), mientras las cosechas 2023 y 2024 llegan a oct-24 con COP 46,3 mil y COP 43,0 mil por cliente y ya son 34,0% y 31,2% de los activos. La descomposición asigna el cambio sobre todo a esa composición de cosechas; el efecto dentro de las cosechas es menor y se concentra en la cosecha 2022 (de COP 81,0 mil a COP 65,4 mil por cliente) y en las altas de feb-22 (de COP 85,8 mil a COP 69,9 mil). El menor ticket de entrada ocurre dentro de cada industria y no por el mix de industrias, y el churn persistente casi no se mueve (0,98% en 2022 y 0,96% en 2024) aunque el observado baje de 3,52% a 2,04%.

- Pregunta: ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento?
- Rol: diagnosis · confianza medium · fuerza supported
- Evidencia: F-097, F-092, F-096, F-094, F-020, F-164, F-163, F-075, F-033, F-183, F-059, F-101, F-102 · Tablas: T-041, T-038, T-040, T-066, T-002, T-030
- Intención visual: Split: la base previa se mantiene mientras las cosechas nuevas entran más abajo y ganan peso; por industria, la caída aparece en todas, con distinta intensidad.
- Limitación: Composición no es causa: no separa tipo de cliente, plan, tarifa ni descuento (F-093).
- Limitación: El peso de la composición depende de la base (dic-22 o ene-22); la dirección no cambia y la base la decides tú (X-060).
- Limitación: La descomposición va sin montos: sus totales no están como celda en ninguna tabla del claim; no agregarlos en la lámina (corrección D-026).
- Limitación: El efecto dentro de la cosecha 2022 puede ser real o reflejar pagos iniciales grandes de 2022 (H-042, X-062).
- Limitación: Quienes hacen churn pagaban más en promedio, pero no en mediana: la diferencia se concentra en pocas cuentas grandes (F-101, F-102).
- Limitación: El churn observado de 2024 no coincide entre T-034 y T-002; falta fijar el periodo (X-099, X-101).
- Limitación: La industria es la única segmentación disponible: no sustituye al canal ni a la ruta. La señal de Salud (C-008) va en anexo, a validar.
- Limitación: Es monto pagado observado, no MRR contratado.
- En palabras de Hugo: “Dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix; quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco volumen).”

**C-028 · Proponemos métricas por ruta y de eficiencia, cada una atada a una decisión del CRO**

Proponemos medir por ruta lo que hoy no existe y atar cada métrica a una decisión del CRO: entradas, alcance por etapa en cohorte y tiempo por tramo, para saber si falta volumen o tasa antes de pedir más SDR/AE o más gasto; tiempo a primer toque y carga por SDR/AE, para separar capacidad de calidad; estancamiento por etapa, para decidir qué tramo y qué dueño arreglar primero; valor y calidad por ruta (MRR inicial con run-rate y guardarraíles, no con el primer pago, y retención temprana), para decidir a qué puerta ponerle persona; y eficiencia (CAC y payback por ruta), para repartir el S&M entre rutas y canales. Hoy se calcula, con nombre honesto y solo en total, el MRR pagado observado y su puente, los clientes activos, el ARPA por cliente (lo que se pide como ARPU), el churn observado y las métricas de cohorte. La eficiencia hoy solo existe como S&M por alta en unidad reportada, 0,105 u en 2022 y 0,036 u en 2024 (−66%), y eso no es CAC: sin la unidad del gasto no hay CAC en COP ni payback, sin ruta ni canal no hay CAC por ruta, y el LTV con margen y el UCM necesitan margen bruto o costo de servir.

- Pregunta: ¿Qué métricas propondrías que hoy no existen, y para qué decisión sirve cada una?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-135, F-136, F-137, F-138, F-139, F-081, F-141, F-144, F-146, F-148, F-227, F-231, F-232, F-246, F-247, F-249, F-252 · Tablas: T-036
- Intención visual: Link: cada métrica nueva se conecta con la decisión del CRO que habilita, separando lo que hoy se calcula de lo que pide dato nuevo.
- Limitación: Pendiente de aceptación: F-246, F-247, F-249 y F-252 están propuestos (R-035, R-036).
- Limitación: Es propuesta: ninguna métrica propia de ruta se calcula hoy y ninguna métrica común se puede cortar por ruta (F-146).
- Limitación: El S&M por alta está en unidad reportada, sin escala a COP: no es CAC (F-137). Un CAC combinado depende de documentar la unidad del gasto y de acordar qué es adquirir un cliente.
- Limitación: Churn y MRR observados necesitan una regla de normalización y una ventana de gracia antes de llamarse así (F-136).
- Limitación: Las decisiones del CRO a las que se atan las métricas son propuesta: Finora aún no las define.
- Limitación: La «reactivación» del modelo actual es retorno de pago de clientes, no el Reactivate de leads (F-252).
- En palabras de Hugo: “Qué métricas propondrías que hoy no existen (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) y cómo medirlas, robustecerlo y bajar lo que tenga sentido.”

**C-023 · Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja**

Proponemos ordenar las causas de «más leads, pero no más ventas» por la identidad ventas/leads y no por áreas, para que cada pedazo de la brecha caiga en una sola hoja. Antes del árbol se fija qué es «venta» (Won o primer pago) y qué ventana se compara, por cohorte de entrada, porque en los pagos la premisa cambia según la ventana. Después, en este orden: primero los artefactos (el aumento de New no es demanda nueva comprable: no-prospectos y duplicados, un cambio de definición o la misma demanda que llega por otra puerta); luego la mezcla (calidad al entrar, ToFu, medida solo con señales congeladas al crear el lead); luego la caída antes del SQL (capacidad y tiempo a primer toque, leads estancados en Working o Engaged); luego la caída después del SQL (incentivos del SDR, decisión en Proposal, oferta o precio, BoFu); y al final el cobro (Won que no llega al primer pago). Demanda, calidad, velocidad de atención y conversión post-SQL quedan como explicaciones a contrastar, no como causas: con los datos del caso no se valida ni se descarta ninguna hoja.

- Pregunta: ¿Qué hipótesis ToFu y BoFu podrían explicar «más leads, pero no más ventas», y en qué orden se descartan?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-228, F-229, F-230, F-231, F-232, F-127, F-128, F-129, F-122, F-212, F-125 · Tablas: —
- Intención visual: Branch: la brecha se reparte en ramas ordenadas (artefactos → mezcla → antes del SQL → después del SQL → cobro) y cada pedazo cae en una sola hoja.
- Limitación: Es propuesta, como pide el guion: hoy no se puede validar ni descartar ninguna hoja, y del cobro solo se ve el arranque (F-230).
- Limitación: El árbol reordena las ramas del CRO de D-001: la calidad pasa a leerse como mezcla al entrar (X-150). Pendiente de tu decisión.
- Limitación: La premisa «no más ventas» depende de la ventana que se compare (F-125, F-229).
- Limitación: Las causas candidatas (metas o comisiones de SDR/AE, precio, competencia) no tienen evidencia en el caso.
- Limitación: Una caída después del SQL no es por sí sola un problema del AE: puede nacer antes del traspaso (SQL inflados) o en la oferta.
- Limitación: Cómo se reparte el término cruzado entre mezcla y tasa es una regla a fijar antes de ver resultados.
- En palabras de Hugo: “Definir qué hipótesis ToFu y BoFu (demanda, calidad, velocidad de atención, conversión post-SQL; p. ej. la capacidad comercial instalada no alcanza la demanda generada, la calidad de la máquina de leads bajó) podrían estar afectando su motor; aquí no hay que hacer research en data, es una propuesta.”

**C-029 · Cada hoja del árbol tiene firma y dato propios; hoy no están en el caso**

En el mismo orden del árbol, cada hoja tiene una firma y un dato mínimo. Artefactos: export de leads con fecha, fuente y dominio, cruzado con customer_id y con leads previos, para quitar no-prospectos y duplicados, y el cruce de identidad para ver la misma demanda por otra puerta; las entradas únicas con fecha (con canal, motion y segmento) y su vínculo con el pago bastan para separar conteo, mezcla y tiempo. Mezcla o calidad: señales de ajuste congeladas al crear el lead, comparando mezcla contra tasa dentro de cada puerta, nunca con lo que Sales opinó después. Antes del SQL: tiempo a primer toque humano y carga por SDR/AE, con un roster semanal que distinga ramp (capacidad), y la bolsa de estancados con fechas por etapa y lo que compran los retomados (estancamiento). Después del SQL: aceptación del AE según el origen del SQL (incentivos del SDR) y motivos validados con compradores (oferta o precio), porque las razones de pérdida del CRM no alcanzan. Cobro: Won ligado al primer pago. Nada de esto está en el caso: el modelo empieza en el primer pago, el gasto de S&M no sirve como proxy de capacidad ni de leads, y probar la palanca de capacidad pide un experimento; la prueba más rápida es que Finora etiquete hacia atrás, desde su CRM, a los pagadores ya observados.

- Pregunta: ¿Qué dato valida o descarta cada hoja del árbol, y lo tenemos hoy?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-121, F-122, F-127, F-128, F-129, F-228, F-229, F-230, F-231, F-232, F-207, F-225, F-191, F-120, F-124, F-126, F-159 · Tablas: —
- Intención visual: Match: cada hoja del árbol, en el mismo orden, se empareja con su firma y su dato mínimo; ninguna tiene hoy su dato.
- Limitación: Es propuesta: ninguna hoja tiene hoy su dato en el caso (F-230, F-126).
- Limitación: Que el caso no traiga canal ni etapas no prueba que Finora no los registre: parte puede estar en su CRM, aunque no siempre con historia (F-128, H-076).
- Limitación: Ventana de deduplicación, SLA y umbral de estancamiento son parámetros a acordar con Finora, no estándar de mercado.
- Limitación: Comparar tocados contra no tocados asigna crédito, no efecto; la palanca de capacidad pide experimento (F-159).
- Limitación: Comparar entradas directas a SQL contra SQL del SDR no es un experimento: solo sirve ver cómo cambia cada grupo en el tiempo, y sigue siendo asociación.
- Limitación: Con los pagos solo se acotan los artefactos del lado de pagadores; los del lado de leads necesitan el CRM.
- En palabras de Hugo: “…y qué datos validarían o descartarían cada una; aquí no hay que hacer research en data, es una propuesta.”

**C-014 · Proponemos una vía formal por foro y otra de agentes para el día a día**

Primero la capa técnica: una cuenta común que une CRM, producto y facturación; el historial de etapas del CRM, que suele venir de forma nativa; la puerta y el canal por cuenta desde la primera visita; el gasto por canal, y la facturación con estado de suscripción. Si Finora ya lo registra, se conecta; si no, se instrumenta, porque lo que no se capture desde ya no se reconstruye después. Encima, una vía formal por foro que lee el bowtie por motion: el semanal decide oportunidades, estancamientos y handoffs; el mensual, la mezcla de motion y canal; el trimestral, la inversión y la capacidad. Y otra vía para el día a día: Análisis Ad hoc por hipótesis y agentes de IA que trabajan solo sobre métricas gobernadas y entran con un piloto controlado. El lado Revenue ya se puede operar mes a mes, pero con pagos observados el CRO confundiría el momento del cobro con churn y expansión: la facturación es la primera pieza técnica.

- Pregunta: ¿Qué solución analítica le permite al CRO operar el funnel de forma recurrente y qué decisiones le permite tomar?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-147, F-148, F-149, F-144, F-238, F-240, F-242, F-145 · Tablas: —
- Intención visual: Stack: la capa técnica (cuenta común, historial de etapas, facturación) sostiene dos vías de uso, la formal por foro y la de agentes para el día a día.
- Limitación: Es propuesta: qué decide el CRO en cada foro aún no está definido por Finora.
- Limitación: No sabemos qué parte de la capa técnica ya existe en los sistemas de Finora; no se afirma que Finora tenga un problema de CRM o analítica digital (H-076).
- Limitación: La atribución reparte crédito, no prueba causa: para decidir presupuesto hacen falta experimentos (F-144, F-149).
- Limitación: Los agentes van encima de métricas gobernadas, no en la base, y entran con piloto controlado (F-149).
- Limitación: Lo que no se capture desde ya no se reconstruye: el to-be mide hacia adelante, salvo que Finora tenga historial (F-242).
- En palabras de Hugo: “Solución analítica para que el CRO opere el funnel de forma recurrente y qué decisiones le permite tomar (técnica: pulir CRM, analítica digital · decision making: dashboards automatizados por foro, análisis ad hoc, agentes de IA).”

### S3 · Revenue
_Con solo el monto pagado se ve qué cambió, pero no por qué. Proponemos que el descuento sea un objeto propio, con su origen, y una escalera de valor con su regla de clasificación. Con ese modelo respondemos los casos del CFO._

**C-015 · Lo observable es el primer y segundo pago; el descuento no es verificable**

Del pricing de entrada solo se observa lo que pagan las altas en sus primeros meses. La mediana del primer pago es COP 63,0 mil en 2022, COP 36,8 mil en 2023 y COP 42,0 mil en 2024, y la del segundo pago, COP 52,5 mil, COP 36,8 mil y COP 38,9 mil. En 2022 el primer pago supera con holgura al segundo en 23,2% de las altas, frente a 7,1% en 2023 y 11,6% en 2024, y el segundo pago repite exacto el primero en 73,5%, 90,3% y 77,3%: un patrón que coincide con pagos iniciales grandes o cobros retroactivos en 2022 más que con un cambio de tarifa. Precio de lista, descuento introductorio, crédito o pausa no se pueden separar: el dato es un monto por cliente y mes, sin catálogo de precios.

- Pregunta: ¿Qué data observable de pricing introductorio podemos sacar?
- Rol: evidence · confianza medium · fuerza supported
- Evidencia: F-083, F-160, F-166, F-086, F-087, F-134, F-093 · Tablas: T-051, T-062, T-054, T-055
- Intención visual: Compare: primer pago contra segundo pago por cohorte; la brecha de 2022 se cierra después y el descuento no aparece como dato.
- Limitación: Es monto pagado observado: no hay precio de lista, plan, descuento ni crédito (F-093).
- Limitación: Primer pago observado no es adquisición ni precio de entrada.
- Limitación: Las medianas del segundo pago son de las altas con segundo pago (T-062); los porcentajes son sobre todas las altas (T-054, T-055).
- Limitación: La huella de un descuento temporal limpio casi no aparece en el histórico; eso es consistente con que los descuentos sean algo por introducir, pero no prueba que no existieran (F-134).
- Limitación: No se infieren descuentos del tamaño de un salto del monto.
- En palabras de Hugo: “Qué data observable de pricing introductorio podemos sacar.”

**C-024 · Con cliente, mes y monto se ve qué cambió, no por qué**

Con el monto pagado se puede operar hoy el MRR pagado observado y su puente, pero el puente mezcla orígenes. En la expansión, 29% del MRR se revierte al mes siguiente, y 25,3% del movimiento bruto sin altas (que suma COP 282,8 millones entre mar-22 y sep-24) vuelve exacto al nivel previo. En el churn, 44% de los 751 churns observados vuelve a pagar al mes siguiente; en la reactivación, la parte cuyo monto cubre los meses del hueco más el corriente explica 42,6% del MRR, frente a 11,5% que regresa al monto usual, y el resto, 45,9%, no encaja en esas firmas. La contracción, en cambio, no muestra firma de cobro: 88,9% de su MRR sigue igual o más abajo al mes siguiente y 4,0% regresa al nivel previo. Sin estado de suscripción ni periodo de servicio no se sabe por qué cambió: antes de llamar churn o MRR a esos movimientos hace falta una regla de normalización y una ventana de gracia.

- Pregunta: Con solo cliente, mes y monto pagado, ¿qué podemos afirmar del ingreso y qué no?
- Rol: evidence · confianza high · fuerza supported
- Evidencia: F-172, F-174, F-180, F-182, F-184, F-185, F-135, F-136, F-186, F-213 · Tablas: T-074, T-076, T-082, T-086, T-087
- Intención visual: Separate: lo que el monto pagado muestra (qué cambió) frente a lo que no puede decir (por qué); dentro del puente, expansión y reactivación se revierten y la contracción se sostiene.
- Limitación: Es monto pagado observado: sin estado de suscripción, periodo de servicio ni fecha de factura, el puente normalizado exacto no es medible, solo se acota (F-186).
- Limitación: Las firmas de cobro son lecturas de patrón, no confirmación de atraso o prepago (F-136).
- Limitación: La prueba de la contracción solo mira el mes siguiente: no descarta cobros de primer pago o de reactivación que caen en la contracción (X-100).
- Limitación: El 44% dice que vuelve a pagar, no con qué monto (X-102, X-145).
- Limitación: La vuelta de pagadores es un loop de Revenue, no el Reactivate del CRO (F-213).
- En palabras de Hugo: “Qué data observable podemos sacar (S3.1): lo que vemos y lo que no vemos con cliente, mes y monto.”

**C-017 · El descuento se registra como objeto propio, con origen, source y fecha de fin**

Mecanismo Propuesto: cada descuento se registra como objeto propio, con tipo, valor, duración, fecha de inicio y de fin, motivo, aprobador y origen exclusivo (promoción digital o física, negociación, retención o partner), separado de la cantidad contratada y del precio de lista, y se lee desde la factura; el modelo separa la oferta, el código que la distribuye y el descuento aplicado con su vigencia. El source se captura en la adquisición de todos los clientes, no solo en el descuento, y el canal asignado al código se guarda aparte; negociación, retención y partner llevan registro propio, para que un precio especial no esconda un descuento ni un downgrade de retención se confunda con uno. Cómo pega el descuento en el MRR no es un estándar de mercado: es una convención que el CFO decide y declara, y las herramientas revisadas no separan por sí solas descuento de cambio de suscripción. Implicaciones Multidisciplinarias: con descuentos, MRR neto, revenue reconocido y caja pueden separarse según el tipo de contrato; el descuento cambia la composición de las cohortes, que hay que marcar y medir contra un grupo comparable; y el puente actual ya mezcla interrupciones con bajas (44% de los 751 churns observados vuelve a pagar al mes siguiente), lo mismo que un descuento que vence volvería a mezclar si no tiene fecha de fin.

- Pregunta: ¿Cómo debería Finora introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-233, F-234, F-235, F-236, F-237, F-150, F-151, F-152, F-153, F-154, F-174 · Tablas: T-076
- Intención visual: Separate: el descuento sale de lo contratado y del precio de lista como pieza propia, con su origen y su fecha de fin.
- Limitación: Es propuesta: el histórico no trae tarifas ni descuentos y no se afirma que hubo descuentos; el caso habla de introducirlos.
- Limitación: La convención de cómo pega el descuento en el MRR la decide y declara el CFO; la propuesta se aparta del default del mercado (F-236).
- Limitación: Qué vista aplica (MRR neto, revenue o caja) depende de si los contratos son mensuales cancelables o a plazo fijo: falta confirmarlo (F-153).
- Limitación: La relación entre descuento y clientes de menor valor es evidencia externa, no dato de Finora; se mide con cohortes marcadas y un grupo comparable (F-154).
- Limitación: Si el source no se captura para todos los clientes, el código de descuento quedaría como la única atribución (H-073).
- Limitación: El revenue que dejamos de capturar no tiene cifra histórica: se mide hacia adelante.
- En palabras de Hugo: “Cómo debería Finora introducir descuentos temporales (mecanismo propuesto, implicaciones multidisciplinarias, preguntas del CFO contestadas con el modelo propuesto).”

**C-019 · La Propuesta de Modelo de datos separa el valor en una escalera con vigencias**

Proponemos una escalera de valor por suscripción y mes, cada peldaño con su fuente y su vigencia: tarifa de lista, precio pactado (plan, cantidad y add-ons), descuento con inicio, fin y motivo, MRR neto recurrente, facturado y cobrado. El MRR bruto y el neto se clasifican comparando cierres de mes sobre lo contratado y el descuento; lo facturado y lo cobrado son caja y nunca generan movimientos de MRR, solo un efecto de cobro, y el monto pagado de hoy queda como capa observada que se concilia contra lo cobrado. Regla de clasificación: si la suscripción no cambia, el inicio o el fin de un descuento va a una línea propia «Descuento» y no es contracción ni expansión; si cambian suscripción y descuento el mismo mes, primero se calcula el efecto de la suscripción con los términos de descuento del mes anterior y el resto va a «Descuento»; a quien sale con descuento se le registra churn, no fin de descuento. Las reglas que son decisiones de negocio (base lista o neto del puente, mes gratis, pausa, descuento único, tarifa en línea propia) se escriben antes de construir.

- Pregunta: ¿Cómo separar el valor de la suscripción del precio efectivamente pagado, y cómo clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-130, F-132, F-133, F-150, F-151, F-152, F-168, F-234, F-236, F-240, F-241 · Tablas: —
- Intención visual: Ladder: el valor baja peldaño a peldaño, de la tarifa de lista a lo cobrado, y cada movimiento del mes se ubica en el peldaño donde nace.
- Limitación: Es propuesta: hoy el modelo es cliente × mes × monto pagado y no separa suscripción, tarifa, descuento ni momento de cobro (F-130).
- Limitación: Se sabe qué evidencia confirmaría cada componente; no se sabe si Finora la tiene (F-133).
- Limitación: La regla de «Descuento» es convención, no hecho: se aparta del default del mercado y el CFO la declara (F-236, F-151).
- Limitación: Las reglas que son decisiones de negocio quedan por escribir antes de construir (F-241).
- Limitación: Los ejemplos de clasificación son ilustrativos, no datos del caso.
- En palabras de Hugo: “Cómo separar el valor de la suscripción del precio efectivamente pagado: propuesta de modelo de datos (campos, tablas, definiciones); el inicio y fin de un descuento probablemente lo integra la misma propuesta de modelo de datos.”

**C-025 · Con el modelo propuesto, cada caso del CFO se lee en su capa**

Con el modelo propuesto, cada caso del enunciado (ejemplos, no datos de Finora) cae en su capa. Si paga 100 y luego 80, el modelo distingue una contracción real (lo contratado baja a 80) de un inicio de descuento (lo contratado sigue en 100 y la diferencia va a «Descuento»). Si la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100, el puente muestra expansión de 30 e inicio de descuento de −30, con el neto sin cambio; si después desaparece el descuento, la subida del pago va a fin de descuento, no a expansión. Hoy ese puente por capas no es construible (no hay lista, plan ni descuento en los datos), y el puente actual mezcla orígenes: 29% del MRR de expansión se revierte al mes siguiente y 44% de los 751 churns observados vuelve a pagar al mes siguiente. Sobre el negocio subyacente, lo que se observa es composición de la base, no un efecto separable de precio o descuento: el MRR pagado observado por cliente activo pasa de COP 92,8 mil en ene-22 a COP 57,8 mil en oct-24 (−38%), mientras el de la base previa cambia +5%; el revenue que dejamos de capturar por descuentos solo se medirá hacia adelante, con la capa de descuento.

- Pregunta: Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿cómo se lee cada caso y qué pasa con el negocio subyacente?
- Rol: recommendation · confianza medium · fuerza supported
- Evidencia: F-168, F-172, F-174, F-177, F-178, F-150, F-151, F-075 · Tablas: T-080, T-074, T-076, T-030
- Intención visual: Unfold: el mismo pago observado se abre en capas (contratado, descuento, neto) y cada caso del CFO cae en una capa distinta.
- Limitación: Los casos son los ejemplos del enunciado del CFO: prueban qué distingue el modelo, no describen lo que pasó en Finora.
- Limitación: El puente por capas (lista, descuento y neto) no es construible con los datos del caso (F-168).
- Limitación: No se puede repartir la caída por cliente entre un precio de lista distinto y un descuento: ambos coinciden en el mismo monto observado (F-177).
- Limitación: El −38% no se presenta como deterioro de la salud: todavía no se separan la mezcla de entrada, el precio y las salidas.
- Limitación: El revenue que dejamos de capturar no tiene cifra histórica: el histórico no trae tarifas ni descuentos; se mide hacia adelante.
- Limitación: La convención de cómo pega el descuento en el MRR la decide el CFO (F-151).
- En palabras de Hugo: “Preguntas del CFO contestadas con el modelo propuesto: qué pasa con el negocio subyacente y cuánto revenue dejamos de capturar por decisiones comerciales.”

## Recomendaciones
- Fijar con Finora la base del Overview (ene-22 o dic-22) y qué es adquirir un cliente (Won, primer pago o suscripción activa) antes de mostrar cifras de composición. _(si Antes de presentar: la dirección no cambia con la base, pero el peso de la composición sí (X-060).)_
- Pedir a Finora el export del CRM (entradas únicas con fecha, puerta, canal y dominio; historial de etapas; roster semanal de SDR/AE) y que etiquete hacia atrás, desde el CRM, a los pagadores ya observados. _(si Si Finora guarda esos datos, aunque sea sin historia completa (H-076); si no, se instrumentan hacia adelante.)_
- Acordar las reglas del funnel que son decisiones de negocio: qué cuenta como intervención (Q-063), cuándo un lead está estancado (Q-064), la ventana fija por puerta y el nudo común (Q-050). _(si Antes de construir el catálogo de métricas: son parámetros de Finora, no estándar de mercado.)_
- Recorrer el árbol en orden: cerrar primero los artefactos (conteo, definición, otra puerta) y abrir mezcla, capacidad, post-SQL y cobro solo con la brecha que quede. _(si Cuando llegue el export de leads; si los artefactos cierran la brecha, no se abre el resto.)_
- Si capacidad o calidad siguen vivas después del árbol, probar la palanca con un holdout o un experimento natural (llegadas fuera de horario, reparto por turnos) antes de sumar SDR/AE o gasto. _(si Si la tasa cae dentro de cada banda de ajuste y sobre todo en semanas de alta carga.)_
- Documentar la unidad y la escala del archivo de S&M, el gasto por canal y si Software Tools + Freelance es habilitación o producto, para pasar de «S&M por alta» a CAC y payback por ruta. _(si Antes de cualquier conversación de eficiencia con el CFO.)_
- Aprobar una regla de normalización y una ventana de gracia antes de llamar churn, reactivación o MRR a los movimientos del monto pagado. _(si Mientras no haya estado de suscripción ni periodo de servicio en los datos.)_
- Que el CFO decida y declare cómo pega el descuento en el MRR (mostrar lista y neto) y confirme si los contratos son mensuales cancelables o a plazo fijo. _(si Antes de lanzar el primer descuento temporal.)_
- Registrar el descuento como objeto propio (origen, source, inicio, fin y aprobador) y el source de adquisición de todos los clientes, y marcar las cohortes con descuento para medirlas contra un grupo comparable. _(si Si Finora introduce descuentos temporales: lo que no se capture desde ya no se reconstruye.)_
- Montar primero la capa técnica (cuenta común, historial de etapas, facturación con estado de suscripción) y después los foros; los agentes de IA, solo sobre métricas gobernadas y con piloto controlado. _(si Cuando Finora defina qué decide el CRO en cada foro.)_

## Apéndice candidato
- Overview en detalle: composición, entradas y gasto — La lámina de observaciones (C-026) rescata lo mejor de C-002, C-003 y C-004 (N-055); el detalle sostiene las preguntas del CEO y del CRO.
- Rutas, puertas y la medición anterior del funnel — C-021 lleva la nota clave de C-005 y C-027 reemplaza a C-006 con tus definiciones de Hybrid B y Reactivate.
- Salud: menor churn persistente, ticket alto y poco volumen — Es la matriz de burbuja que sugería S2.4; queda como señal a validar, fuera del deck de 5 minutos.
- Métricas comunes, S&M por alta y catálogo completo — C-028 integra lo esencial con eficiencia y la decisión que habilita cada métrica; el semáforo y los catálogos quedan de respaldo (X-170).
- Premisa de ventas en pagos y calidad frente a capacidad — El árbol (C-023) y su dato por hoja (C-029) los reemplazan en la presentación; los chequeos de artefactos con pagos quedan de respaldo.
- Modelo de datos del funnel: de cliente-mes a cuenta común — Su línea clave (cuenta común e historial de etapas) entra en C-014; el as-is contra to-be completo va como respaldo técnico.
- Convención del CFO y regla de clasificación del descuento — C-017 lleva la convención y C-019 integra la regla de C-020.

## Preguntas sin resolver
- Reconstrucción: la v4 que recibí se corta en las limitaciones de C-021. Desde ahí (resto de C-021, C-027, C-007, C-028, C-023, C-029, C-014, C-015, C-024, C-017, C-019, C-025, recomendaciones, anexos, referencias visuales y guion_map) lo rehíce desde el estado del caso con las mismas keys, orden, titulares, evidencia y tablas. Antes de aprobar: comparar contra la v4 guardada o aplicar solo las dos correcciones sobre ella.
- C-001 conserva la limitación de la v4 «Pendiente de tu aceptación: F-071, F-072, F-001, F-002 y F-074 están propuestos», pero en el estado actual esos findings figuran aceptados. ¿Se actualiza?
- C-026 escribe 65% y 91%: están en el mensaje de T-031 y T-066, no como celda. La validación no los marcó; si el criterio es por celda, como con el +5% de C-025, habría que decirlos como 34,0% y 31,2% (T-041) o sin cifra.
- F-243 a F-252 siguen por revisar: C-027 (funnel-medicion) y C-028 (metricas-nuevas) dependen de ellos, y el paquete no puede marcarse Ready hasta su aceptación.
- S2.1: ¿qué relaciones comentaste para esta lámina? El guion dice «por precisar».
- ¿Qué base usa el Overview para la composición, ene-22 o dic-22? (X-060)
- ¿Qué es adquirir un cliente para el CRO: Won, primer pago o suscripción activa? (Q-050, X-052)
- ¿Existe Self Service como compra sin intervención humana, con prueba gratis, freemium o pago al registrarse? (Q-046)
- ¿Qué cuenta como intervención (Q-063) y desde cuándo un lead está estancado (Q-064)?
- ¿Cuál es la unidad y la escala del archivo de S&M, y Software Tools + Freelance es habilitación o producto? (X-002)
- ¿Los contratos de Finora son mensuales cancelables o a plazo fijo? Define qué vista del descuento aplica (F-153).
- El churn observado de 2024 no coincide entre T-034 y T-002/T-085 (esta con 2024 ene–jul): ¿qué periodo queda? (X-099, X-101)
- ¿El árbol de C-023 reemplaza las tres ramas del CRO de D-001? (X-150)

## Validación
- ⚠ Láminas del guion con evidencia parcial: S2.1.
