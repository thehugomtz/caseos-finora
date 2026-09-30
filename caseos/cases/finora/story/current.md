# CURRENT STORY — v2
> Generado 2026-09-29T17:25 · válido

## Audiencia
CEO: contexto de salud general del modelo (Overview) antes de Growth y Revenue. Qué decide todavía no está definido., CRO: cómo definir, medir y operar el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos., CFO: cómo introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»: mecanismo, modelo de datos y clasificación.

## Objetivo
BORRADOR 2 (D-017). Busca que las 8 preguntas del caso queden respondidas siguiendo tu guion (S1 Overview → S2 Growth → S3 Revenue). Cada lámina cierra con una propuesta concreta: qué definimos, qué medimos, qué decidiría el CRO o el CFO y con qué dato. Todo cita findings propuestos, así que queda pendiente de tu aceptación y el paquete no puede marcarse Ready. Framing sigue en needs_review. Las propuestas de diseño (catálogo de métricas, S2.7, S3.3 y S3.4) van como diseño, no como algo construido. Si D-018 destraba el choque entre D-007 y D-017 lo decides tú.

## De → A
- **Hoy creen:** Finora suma clientes mucho más rápido que monto pagado. Esa brecha se lee con explicaciones que los pagos no confirman: «más leads que no convierten» y «cambios de suscripción o descuentos».
- **Deben salir creyendo:** La brecha coincide con quién entra: más primeros pagadores, con menor ticket estabilizado, dentro de cada industria. No coincide con la base previa ni con salidas persistentes. El porqué del CRO y del CFO no está en los datos del caso, pero hay un diseño concreto para decidirlo: rutas Executive, Self Service e Hybrid con un loop de Reactivate, una matriz de causas con su dato, un catálogo de métricas por funnel y foro, y una Propuesta de Modelo de datos que separa lista, descuento y cobro.

## Governing thought
> La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos: proponemos medir por funnel y separar descuento de suscripción.

## Preguntas ejecutivas
- Q-003 (CEO) ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?
- Q-001 (CRO) ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- Q-002 (CFO) ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?
- Q-025 (CFO) Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿cómo se lee cada caso?
- Q-026 (CFO) ¿Qué pasa con el negocio subyacente y cuánto revenue dejamos de capturar por decisiones comerciales?

## Arco
SCR con pilares, siguiendo tu guion aprobado (Overview → Growth → Revenue) — Primero la respuesta, lámina por lámina: lo que vemos → lo que no vemos → propuesta concreta. En Overview, la brecha coincide con quién entra y no con la base previa. En Growth vemos más primeros pagadores, con menor ticket estabilizado dentro de cada industria, y un gasto que no se mueve con ellos. El porqué no está en los pagos, así que proponemos rutas con tus definiciones, un catálogo de métricas por funnel, una matriz de causas con su dato y foros atados a decisiones. En Revenue mostramos qué se puede leer del monto y qué no, el mecanismo de descuentos, el modelo de datos y la regla de clasificación. El remate responde uno por uno los casos del CFO.

### S1 · Overview
_Situación: Finora suma clientes mucho más rápido que monto pagado, y la caída por cliente activo coincide con quién entra. Abre Growth y Revenue y cierra con la propuesta de reportar por cosecha con una base de comparación fija._

**C-001 · Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8×**

Entre ene-22 y oct-24 (ventana completa), los clientes con pago en el mes pasan de 377 a 1.678 (4,5×) y el MRR pagado observado, de COP 35,0 millones a COP 97,0 millones (2,8×). El MRR pagado observado por cliente activo baja de COP 92,8 mil a COP 57,8 mil (−38%). Esa brecha abre Growth (quién entra) y Revenue (qué se paga y por qué cambia).

- Pregunta: ¿Qué tan sano está el modelo si suma clientes mucho más rápido que monto pagado?
- Rol: context · confianza high · fuerza pending
- Evidencia: F-071, F-072, F-001, F-002, F-074 · Tablas: T-026, T-027, T-001
- Intención visual: Una línea: MRR pagado por cliente activo, en COP, de ene-22 a oct-24 (T-027): de COP 92,8 mil a 57,8 mil (−38%). Si hace falta la comparación, en apoyo: clientes activos y MRR pagado en la misma gráfica, cada uno con ene-22 = 100 (T-001), las dos líneas juntas.
- Limitación: Pendiente de tu aceptación: F-071, F-072, F-001, F-002 y F-074 están propuestos.
- Limitación: Es monto pagado observado (campo amount con escala fija), no MRR contratado (F-082).
- Limitación: Cliente activo = pago mayor que cero en el mes. Un cliente sin pago puede estar cancelado, en pausa o atrasado (F-082).
- Limitación: Es stock con ventana completa desde ene-22; los flujos arrancan en mar-22 (F-074).
- Limitación: El −38% no se presenta como deterioro de la salud: todavía no separa la mezcla de entrada, el precio y las salidas.
- En palabras de Hugo: “Finora suma clientes mucho más rápido que monto pagado (4,5× vs 2,8×; ~−38% por cliente activo). Esa brecha abre Growth y Revenue.”

**C-002 · La caída por cliente se asocia a quién entra; la base previa sostiene su monto**

Con base ene-22, la descomposición por cosecha asigna a la composición de la base 108% del cambio del MRR pagado observado por cliente activo; con base dic-22, 84%. La cifra depende de la ventana, la dirección no. Los clientes activos en ene-22 pasan de COP 92,8 mil a COP 97,4 mil por cliente (+5%), mientras que las cosechas 2023 y 2024 ya son 65% de los activos y 50% del MRR en oct-24, con COP 46,3 mil y COP 43,0 mil por cliente. Propuesta: reportar el monto por cliente siempre partido en base previa y cosechas, con una base de comparación fija que decidas tú, para que el CEO no lea mezcla como deterioro.

- Pregunta: ¿El −38% por cliente viene de la base que ya teníamos o de quién entra?
- Rol: diagnosis · confianza high · fuerza pending
- Evidencia: F-075, F-076, F-056, F-058, F-097, F-092, F-019 · Tablas: T-030, T-031, T-041, T-027
- Intención visual: Mezcla que arrastra: la base previa se sostiene mientras las cosechas nuevas, de menor monto por cliente, ganan peso y bajan el promedio.
- Limitación: Pendiente de tu aceptación: F-075, F-076, F-056, F-058, F-097, F-092 y F-019 están propuestos.
- Limitación: Composición no es causa: no separa si las cosechas nuevas pagan menos por tipo de cliente, plan, tarifa o descuento; el panel no trae esas tablas (F-062).
- Limitación: La base de comparación (ene-22 o dic-22) es una decisión pendiente (X-060).
- Limitación: La salida de pocas cuentas grandes también baja el promedio (F-101, F-102) y aquí no está separada.
- Limitación: «Quién entra» describe primeros pagadores observados, no la calidad de los leads.
- En palabras de Hugo: “Observaciones generales y salud del negocio que introducen las secciones siguientes.”

### S2 · Growth
_Tres partes. Lo que sí vemos: primeros pagadores con menor ticket estabilizado y un gasto de S&M que no se mueve con ellos. Lo que no vemos: el funnel por ruta con tus definiciones y las causas ToFu/MoFu/BoFu, cada una con su dato. Cómo operarlo: semáforo y catálogo de métricas, fuentes comunes y foros atados a decisiones. Sigue tu orden S2.1–S2.7; S2.1 queda sin contenido._

**C-003 · Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias**

Los primeros pagadores observados pasan de 27,2 por mes en 2022 (mar–dic) a 54,7 desde ene-23. Es un escalón sin tendencia distinguible después: pendiente de +0,47 por mes, con intervalo de −0,40 a +1,33. Entre 2022 y 2024 suben +104% por mes, mientras el valor inicial que incorporan sube +6% (run-rate temprano) o +17% (monto habitual). Con ticket estabilizado, la mediana del segundo pago baja de COP 52,5 mil en 2022 a COP 36,8 mil en 2023 y COP 38,9 mil en 2024. El efecto dentro de cada industria explica 91% del cambio 2022→2023 y 96% del 2022→2024.

- Pregunta: ¿Qué cambió en quién entra y en qué industrias?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-110, F-039, F-113, F-045, F-037, F-160, F-161, F-162, F-163, F-164, F-114, F-030, F-192, F-193 · Tablas: T-016, T-019, T-062, T-066, T-020
- Intención visual: Outgrow: el conteo de primeros pagadores sube en escalón y se aplana, mientras el valor que traen crece mucho menos.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos; F-160 a F-163 tienen confianza media.
- Limitación: Primer pago observado no es adquisición: no es Won ni suscripción activa. El hito lo acuerda el CRO (X-052).
- Limitación: El escalón de inicios de 2023 puede ser en parte registro (H-024) o un cambio operativo (H-025, H-068). Sin confirmar.
- Limitación: El ticket estabilizado sigue siendo monto pagado: no separa tarifa, plan, empaquetamiento ni descuento (F-167).
- Limitación: La industria es la única segmentación disponible: no sustituye al canal ni a la ruta.
- En palabras de Hugo: “Revisar entradas y actividad económica de clientes y segmentos.”

**C-004 · Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas**

En 2023 jun–dic hay 60,6 primeros pagadores por mes, frente a 45,2 en ene–may. En esos mismos tramos, la Generación de Demanda (ToFu) baja de 1,73 u a 0,82 u por mes y el S&M total de 3,01 u a 1,44 u. La correlación en niveles entre S&M total y primeros pagadores del mismo mes es −0,57; en cambios mes a mes, el mayor valor absoluto es 0,27 (p mínimo 0,14). No hay una relación positiva que leer. El archivo viene en unidades reportadas (u), sin escala a COP, y hasta may-23 Team es un 12% fijo del total durante 17 meses. Propuesta: que Finora documente la unidad y la clasificación funcional del gasto y lo registre por canal y funnel. La inversión se decide con gasto por canal y experimentos, no cruzando fechas.

- Pregunta: ¿Hasta dónde se puede relacionar la Inversión en Marketing por categoría con las ventas cruzando fechas?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-214, F-220, F-219, F-221, F-217, F-107, F-118, F-023, F-024, F-063, F-066, F-115, F-065, F-068, F-119, F-207 · Tablas: T-101, T-107, T-106, T-108, T-104, T-013, T-024, T-008, T-005, T-009
- Intención visual: Dos paneles con los mismos meses (ene-22 a oct-24): arriba el S&M total por mes (unidad reportada), abajo las altas por mes; en 2023 jun-dic el gasto baja mientras las altas suben (T-101). Apoyo: dispersión de S&M contra altas con un mes de rezago (F-220, T-107) y barras por ventana de altas por mes y S&M por alta (T-108). Sin atribuir ventas al gasto.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Asociación no es efecto: no hay etapas con fecha ni fuente del lead que liguen gasto y clientes (F-119).
- Limitación: No se puede decidir si SoftwareTools y Freelance son habilitación comercial o producto (F-068).
- Limitación: PayrollExpenses es negativo en algunos meses (T-007) y el primer tramo parece una asignación de arriba hacia abajo.
- En palabras de Hugo: “inversión de S&M por categoría (ToFu: Paid Media y publicidad no web · Team: Payroll Expenses y Travel · habilitación: Software Tools y Freelance) y hasta dónde se puede relacionar con ventas cruzando fechas”

**C-005 · Proponemos rutas Executive, Self Service e Hybrid, más un loop de Reactivate**

Con tus definiciones. Executive es el funnel actual SDR→AE (New → Working SDR → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won); la entrada directa a SQL también es Executive, con etapa de entrada SQL. Self Service es el recorrido sin persona, con sus canales. Hybrid mezcla tramos sin persona y con persona: en A empezó solo y después intervino un SDR/AE; en B lo tocó una persona y terminó solo. Reactivate no es otra ruta: es un loop sobre leads estancados que se reactivan y se asignan a un funnel según el caso. Para que el mix sea MECE: la unidad es la cuenta; la puerta (Producto o CRM/Ventas) y el canal se fijan al entrar y no cambian; la ruta sale de quién movió cada tramo. El formulario de «hablar con ventas» es una entrada por la puerta CRM, y un lead que nadie contactó y compró solo es Self Service con bandera. Un episodio reactivado no cuenta como entrada nueva: conserva su fecha y su puerta originales, y su primer pago cuenta una sola vez, con bandera. El nudo común es el primer pago, como recomendación que decides tú. La vuelta de pagadores que se ve en los pagos no es Reactivate: es otro loop, del lado Revenue.

- Pregunta: ¿Cómo definir el funnel si no todos lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas)?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-209, F-210, F-211, F-212, F-213, F-188, F-190, F-140, F-155 · Tablas: —
- Intención visual: Split and converge: rutas que entran por puertas distintas y se juntan en el primer pago; Reactivate como flecha de retorno a la izquierda y la vuelta de pagadores aparte, a la derecha.
- Limitación: Pendiente de tu aceptación: F-209 a F-213, F-188, F-190, F-140 y F-155 están propuestos.
- Limitación: No hay CRM para probarla: hoy no se mide ninguna etapa antes del primer pago, ni la puerta (F-191).
- Limitación: Corrige lecturas previas: R-022 y R-023 leían Executive como cuentas nombradas o de KAM y Reactivate como ex-pagadores (F-187, F-189). Aquí mandan tus definiciones (N-033, N-035, N-037, N-038), y el «Assisted» del guion pasa a Hybrid.
- Limitación: Parámetros por decidir: qué cuenta como intervención (Q-063; R-029 propone solo la interacción de ida y vuelta con SDR/AE), el umbral de estancado (Q-064) y el nudo común (X-052).
- Limitación: No sabemos si en Finora existe Self Service como compra sin persona (Q-046). La ruta de un pagador no se infiere del monto.
- En palabras de Hugo: “«el funnel actual es New / Working SDR / Engaged SDR / SQL SDR / Demo Account Executie / Proposal Account Executive / Won /// ese es el punto de partida»; Self Service «con sus respectivos canales»; Hybrid «en alguna parte del funnel fue por Self Service y en algún otro fue intervenido por una persona»; Reactivate «los que dicen que están estancados pero hay formas de reactivarlos y asignarlos a un funnel de acuerdo al caso».”

**C-021 · Cada funnel tiene sus etapas, criterios de salida y dueño; los tramos se pueden saltar**

Executive, con dueño SDR hasta SQL y AE desde Demo: New → Working SDR → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won → primer pago. Se sale de cada etapa con un cambio fechado en el CRM; lo primero es acordar qué hace a un lead Engaged o SQL. Self Service, con dueño Producto/Growth: canal → registro → activación (si existe) → checkout → primer pago. Falta saber si hay prueba gratis, freemium o pago al registrarse. Hybrid usa las etapas del tramo que recorre, con dueño por tramo: la persona en los tramos con SDR/AE y el producto en los tramos que el cliente hace solo. Su primer tramo lo marca como A o B. Reactivate: estancado más allá del umbral de su etapa → reactivado (contacto de ida y vuelta o regreso por su cuenta) → asignado a un funnel, con dueño SDR o RevOps. Cada hito se mide como «alcanzó o superó», para que las etapas saltadas no rompan las tasas.

- Pregunta: ¿Qué etapas tiene cada funnel, con qué criterio se entra y se sale, y quién es el dueño?
- Rol: recommendation · confianza low · fuerza pending
- Evidencia: F-209, F-211, F-210, F-191, F-155 · Tablas: —
- Intención visual: Carriles paralelos: cada funnel en su carril con hitos, criterio de salida y dueño; los saltos están permitidos y todos llegan al primer pago.
- Limitación: Pendiente de tu aceptación: F-209, F-211, F-210, F-191 y F-155 están propuestos.
- Limitación: El brief da la secuencia y un traspaso SDR → AE que ocurre «sobre todo» y «normalmente». Los criterios de etapa no están definidos.
- Limitación: Las etapas de Self Service e Hybrid y los dueños son una propuesta, no las de Finora.
- Limitación: Parte de lo que parecen recorridos distintos puede ser cómo se registra en el CRM (H-051).
- En palabras de Hugo: “funnel propuesto, AAARRR, conversion rate y métricas clave”

**C-006 · Proponemos medir por cohorte de entrada con ventana fija y comparar entre puertas, no rutas**

La tasa que sirve es el % de las entradas de una cohorte que llega al primer pago dentro de una ventana fija, por puerta y canal, y solo en cohortes que ya cumplieron esa ventana. La tasa de periodo castiga a las entradas recientes. Antes del nudo, cada funnel se lee dentro de sí mismo. Entre funnels solo se compara del primer pago hacia la derecha: ticket estabilizado, permanencia temprana y churn observado y persistente. La conversión de Hybrid no mide lo que aporta la persona, porque los SDR/AE eligen a quién tocar. Por eso se compara entre puertas, que quedan fijas al entrar, y se reporta el mix de rutas dentro de cada puerta. AAARRR queda como vocabulario común, no como secuencia. La ventana se acuerda con Finora.

- Pregunta: ¿Cómo se mide la conversión si cada funnel tiene su unidad y sus tiempos?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-141, F-158, F-155, F-212, F-144, F-140, F-213 · Tablas: —
- Intención visual: Curvas por cohorte: alcance acumulado a primer pago por cohorte de entrada, una familia de curvas por puerta; las cohortes inmaduras, marcadas.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Hoy solo se miden el nudo y la vuelta de pagadores (F-213, F-159).
- Limitación: Ventanas y plazos no son estándar de mercado: se calibran con los datos de Finora.
- Limitación: Comparar entradas directas a SQL contra SQL del SDR no es un experimento: solo sirve ver cómo cambia cada grupo en el tiempo, y aun así es asociación.
- Limitación: La atribución reparte crédito, no prueba causa (F-144).
- En palabras de Hugo: “cómo definir y medir el funnel si no todos lo recorren igual”

**C-007 · La pérdida está en el monto por cliente de cosechas de menor ticket**

Está en el monto por cliente, no en el número de clientes: entre dic-22 y oct-24 los clientes activos suben en las 6 industrias y el MRR por cliente activo baja en las 6, de −46,6% en Servicios profesionales a −14,4% en Salud. Está dentro de cada industria: con el monto usual temprano, el efecto dentro explica 91% del cambio del ticket de entrada 2022→2023 y 96% del 2022→2024. Y está en las cosechas de menor ticket: la composición explica 84% del cambio del MRR por cliente activo desde dic-22 (108% desde ene-22; la ventana la decides tú). Las cosechas 2023 y 2024 ya son 65% de los activos, con COP 46,3 mil y COP 43,0 mil por cliente, frente a COP 97,4 mil de la base previa. Las salidas persistentes no la explican: el churn observado baja de 3,52% a 2,04% y el que no vuelve a pagar pasa de 0,98% a 0,96%.

- Pregunta: ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento?
- Rol: diagnosis · confianza medium · fuerza pending
- Evidencia: F-097, F-092, F-096, F-094, F-020, F-164, F-163, F-075, F-033, F-183, F-059, F-101, F-102 · Tablas: T-038, T-040, T-066, T-041, T-030, T-002
- Intención visual: Mezcla que arrastra: las cosechas nuevas de menor ticket ganan peso; por industria, todas bajan con distinta intensidad.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: La cifra de composición depende de la ventana (X-060).
- Limitación: El churn observado de 2024 tiene dos cifras en el caso (T-034 frente a T-002). Falta conciliarlas (X-099, X-101).
- Limitación: Por promedio, quienes se van pagaban más; por mediana, no: el efecto está en pocas cuentas grandes (F-101, F-102).
- Limitación: La cosecha 2022 también baja (F-059), y puede ser real o efecto de edad (X-062). No hay tamaño de cliente ni otra segmentación (F-106).
- En palabras de Hugo: “dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix)”

**C-008 · Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar**

Salud tiene el menor churn persistente (0,56 puntos mensuales), el ticket de entrada mediano de 2024 más alto por primer pago (COP 52,5 mil, igual que Restaurantes) y el menor volumen: 124 clientes activos en oct-24, frente a 459 en Restaurantes. También es la industria con menor caída del MRR por cliente (−14,4%) y aporta 11,7% del crecimiento del MRR. Con monto usual temprano, sostuvo COP 63,0 mil en 2023 y bajó a COP 48,8 mil en 2024. Propuesta: si con margen, costo de servir y canal se confirma, Salud es candidata a una prueba de Generación de Demanda dirigida. El CRO decidiría con la retención y el valor por cohorte de esa industria, frente a un grupo comparable.

- Pregunta: ¿Hay industrias de bajo churn, ticket alto y poco volumen?
- Rol: implication · confianza medium · fuerza pending
- Evidencia: F-104, F-099, F-103, F-105, F-165 · Tablas: T-048, T-049, T-067, T-047
- Intención visual: Outlier en la burbuja: churn persistente × ticket × volumen; Salud aparece con bajo churn, ticket alto y burbuja pequeña.
- Limitación: Pendiente de tu aceptación: F-104, F-099, F-103, F-105 y F-165 están propuestos, con confianza media.
- Limitación: Con pocos clientes activos, la señal puede moverse por unas cuantas cuentas.
- Limitación: El ticket de 2024 es por primer pago; con monto usual temprano, Salud también baja en 2024 (T-067).
- Limitación: Sin margen, costo de servir ni canal no hay economía por industria (F-138). H-044 sigue abierta y la industria no es causa.
- En palabras de Hugo: “quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco volumen”

**C-009 · Proponemos un árbol de ingreso recurrente con semáforo: qué se mide hoy y qué no**

En verde, lo que se calcula hoy con nombre honesto: MRR pagado observado y su puente, clientes activos, ARPA por cliente (lo que se pide como ARPU; no hay datos de usuarios), churn observado y retención por cohorte. En amarillo, los proxies con una regla por aprobar: churn persistente con ventana de gracia, MRR normalizado por mes de servicio y ARR solo como run-rate. En rojo, lo que pide datos nuevos: CAC en COP y por funnel o canal, payback, LTV con margen, LTV:CAC y UCM. El churn muestra por qué importa el nombre: el observado baja de 3,52% en 2022 a 2,04% en 2024, mientras el persistente pasa de 0,98% a 0,96%.

- Pregunta: ¿Qué métricas propondrías que hoy no existen (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) y cómo medirlas?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-135, F-136, F-139, F-033, F-137, F-138, F-183 · Tablas: T-002
- Intención visual: Árbol con semáforo: resultado → drivers → economía unitaria, cada nodo coloreado según qué tan medible es.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: El MRR normalizado y el churn con gracia son reglas que tienes que aprobar (F-136); se muestran junto al observado.
- Limitación: El MRR pagado observado no se compara con benchmarks de MRR contractual.
- Limitación: La cifra de churn observado de 2024 difiere entre T-034 y T-002 (X-101).
- En palabras de Hugo: “qué métricas propondrías que hoy no existen (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) y cómo medirlas, robustecerlo y bajar lo que tenga sentido”

**C-022 · Proponemos un catálogo por funnel: definición, si existe hoy, fuente faltante y foro**

Executive: SQL u oportunidades por cohorte, alcance SQL→Won en ventana fija, ciclo de venta con el % aún abierto, estancamientos por etapa y Won→primer pago. Falta el historial de etapas del CRM; se lee en el foro semanal. Self Service: registros por canal, activación (si existe) y registro→primer pago en ventana. Faltan los eventos de producto y el canal de origen; se lee en el foro mensual. Hybrid: tasa de escalamiento (entradas de producto que reciben a una persona antes de pagar), mix de rutas dentro de cada puerta, tiempo a primer contacto y carga por SDR/AE. Faltan las actividades de ida y vuelta y el roster; se lee en los foros semanal y mensual. Reactivate: estancados por etapa, reactivados, asignados y su primer pago con bandera; foro semanal. Desde el nudo, lo único que se calcula hoy con nombre honesto es: primeros pagos, ticket de entrada estabilizado, permanencia temprana, churn observado y persistente, MRR pagado observado y S&M por alta en unidades reportadas. Se lee en los foros mensual y trimestral.

- Pregunta: ¿Qué métricas mide cada funnel, cuáles se calculan hoy y en qué foro se leen?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-155, F-158, F-159, F-213, F-135, F-139, F-148 · Tablas: —
- Intención visual: Matriz funnel × métrica, con marca de «hoy / pedir» y el foro donde se lee.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: D-007 deja fuera las métricas definitivas; D-018 (propuesta, la decides tú) lo lee como «no construir en esta etapa». Esto es un catálogo propuesto, no construido.
- Limitación: Hoy no se calcula ninguna métrica por funnel ni nada antes del pago (F-159).
- Limitación: Los nombres siguen a X-032 (MRR pagado observado, S&M por alta, ARPA). Ventanas y umbrales se acuerdan con Finora.
- En palabras de Hugo: “cómo medirlas, robustecerlo y bajar lo que tenga sentido”

**C-010 · Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC**

El S&M total por alta pasa de 0,105 u en 2022 a 0,036 u en 2024 (−66%), en una unidad sin escala a COP. Su nivel depende de si Habilitación cuenta como gasto comercial: pesa 12% del S&M en 2022 y 4% en 2024, y el gasto por alta pasa de 0,11 a 0,04 incluyéndola y de 0,09 a 0,03 sin ella. Propuesta: para tener CAC en COP y por funnel, Finora documenta la unidad del gasto, acordamos qué es adquirir un cliente (Won, primer pago o suscripción activa) y el gasto se registra por canal y funnel. Con eso el CFO decide el payback por funnel.

- Pregunta: ¿Hay CAC hoy?
- Rol: limitation · confianza medium · fuerza pending
- Evidencia: F-081, F-108, F-069, F-070, F-022, F-137 · Tablas: T-036, T-011, T-012
- Intención visual: Cociente con advertencia: un ratio que baja, con la unidad marcada como no documentada.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: El −66% no es eficiencia comercial: la unidad del gasto no está documentada y el hito de adquisición no está acordado (X-005).
- Limitación: PayrollExpenses es negativo en algunos meses (T-007).
- En palabras de Hugo: “CAC y cómo medirlo”

**C-011 · Proponemos descartar primero artefactos de medición y después contrastar causas ToFu, MoFu y BoFu**

«Llega más gente» es lo que dice el CRO, no un dato del caso: los datos no traen leads. El paso 1 ya se hizo con los pagos. Sin oct-24, las altas por mes de 2024 son 56, frente a 54 en 2023. Altas y reactivaciones van en flujos separados: 1.476 clientes distintos con alta, 0 con pago previo y 468 reactivaciones aparte. El cambio de ID no se puede verificar, aunque en 2023 el emparejamiento por monto e industria con churns recientes (175) no supera al placebo (196). El estancamiento de altas queda como señal para contrastar con causas, no como artefacto. Después, en orden: artefactos del lado de leads (necesitan el CRM) → ToFu → MoFu → BoFu → después del cierre. En cada paso se comparan cohortes de entrada a igual edad y el cambio se parte en volumen, mezcla y tasa por funnel.

- Pregunta: ¿Qué hipótesis ToFu y BoFu podrían explicar «más leads, pero no más ventas» y en qué orden se descartan?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-196, F-197, F-201, F-202, F-203, F-125, F-126, F-127, F-204, F-205, F-208 · Tablas: T-093, T-094, T-100
- Intención visual: Escalera de descarte: cada peldaño cierra artefactos antes de pasar a causas.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Con los pagos solo se acotan los artefactos del lado de pagadores; los del lado de leads necesitan el CRM.
- Limitación: La premisa depende de la ventana: con pagos, la caída de primeros pagadores está en jul–oct 2024 (F-125, F-204, X-106). Hay que fijar el periodo con el CRO.
- Limitación: En 2024 el placebo casi no tiene pares (T-100), probablemente porque el panel termina en oct-24. La prueba de IDs solo sirve para 2022–2023.
- En palabras de Hugo: “Definir que hipótesis ToFu y BoFu podrían estar afectando su motor de acuerdo a su problema definido y qué datos validarían o descartarían cada una”

**C-023 · Proponemos una matriz de causas: qué la valida, qué la descarta y qué palanca mueve**

Artefacto · no-prospectos en New (clientes actuales por soporte o upgrade, duplicados, spam). Cierta si la brecha se cierra al quitarlos; se descarta si las entradas válidas crecen igual que New. Dato: leads marcados como duplicado, cliente actual o spam (pedir). Palanca: regla de conteo y formularios.
Artefacto · registro o definición (oportunidades creadas directo en SQL, leads sin estado de salida, estancados que vuelven como New). Cierta si la brecha coincide con un cambio fechado de definición, formulario o reparto. Dato: historial de etapas con autor y bitácora de cambios (pedir). Palanca: higiene del CRM.
Artefacto · tiempo. Cierta si la brecha desaparece al comparar cohortes a igual edad. Dato: fecha de entrada y de primer pago por cuenta (pedir). Palanca: esperar y volver a medir.
ToFu · demanda, rebotada: compradores que antes compraban solos ahora entran por ventas. Cierta si crece la puerta CRM y baja la de producto con el mismo perfil. Dato: puerta y canal por cuenta (pedir). Palanca: reparto entre funnels.
ToFu · calidad o mezcla. Cierta si empeora la mezcla de ajuste congelada al entrar y las tasas por banda se sostienen; se descarta si la caída ocurre dentro de cada banda. Dato: banda al entrar (pedir). Palanca: targeting y criterio de calificación.
MoFu · velocidad de atención y capacidad. Cierta si sube la carga por SDR/AE, cae la cobertura de primer contacto y la caída se concentra en entradas lentas. Dato: roster con ramp y tiempos de contacto (pedir). Palanca: capacidad, SLA y reparto.
MoFu · sin seguimiento a quien no compra en el momento. Cierta si crecen los estancados en Working o Engaged y cae su recuperación. Dato: fechas de etapa y estado de salida (pedir). Palanca: cadencias y Reactivate.
MoFu · meta del SDR en SQL o reuniones. Cierta si SQL→Won cae después de un cambio de meta. Dato: historia de metas y SQL→Won por origen (pedir). Palanca: regla de calificación y metas.
BoFu · post-SQL, rebotada: eligen otra opción por precio o plan, competidor o funcionalidad. Cierta si, con avance previo comparable, cae Demo→Won o Proposal→Won. Dato: historial de etapas, motivos de pérdida estructurados y bitácora de precio y plan (pedir). Palanca: oferta, precio o plan de entrada.
Después del cierre · Won que no llega a pagar o se cae al arrancar. Cierta si sube el % de Won sin pago en la ventana. Dato: Won fechado y enlazado al cobro (pedir); en los pagos, casi nadie deja de pagar el mes siguiente al alta. Palanca: cobro y onboarding.
Hoy ninguna se valida ni se descarta con los datos del caso.

- Pregunta: ¿Qué otras causas potenciales hay (por lo menos 3–5 más) y qué datos tendrían que ser ciertos para validar o descartar cada una?
- Rol: recommendation · confianza low · fuerza pending
- Evidencia: F-205, F-206, F-208, F-127, F-128, F-129, F-122, F-212 · Tablas: —
- Intención visual: Matriz etapa × causa con columnas: cierta si / se descarta si / dato mínimo / hoy o pedir / palanca del CRO.
- Limitación: Pendiente de tu aceptación: F-205, F-206, F-208, F-127, F-128, F-129, F-122 y F-212 están propuestos.
- Limitación: Mapa de IDs: no-prospectos H-052; registro o definición H-051, H-027 y H-069; tiempo H-003 y H-004; demanda rebotada H-053 (con H-001); calidad o mezcla H-005 y H-002; velocidad y capacidad H-006 y H-028; sin seguimiento H-055; meta del SDR H-054; post-SQL H-007, rebotada por H-056 (con H-008); después del cierre H-057. H-050 no es causa: es la trampa de leer la conversión de Hybrid como efecto.
- Limitación: Cambios en metas, comisiones, precio o competencia son candidatos sin evidencia en el caso.
- Limitación: La caída post-SQL puede nacer antes del traspaso (SQL inflados) o en la oferta: no se atribuye al AE.
- En palabras de Hugo: “generar más causas potenciales, por lo menos 3-5 más y definir que datos tendrian que ser ciertos para validar o descartar cada una”

**C-012 · Capacidad y calidad se separan comparando mezcla contra tasa por grupo de entrada**

Si empeora la mezcla de ajuste al entrar y la velocidad está estable, apunta a calidad. Si la mezcla está estable, suben la carga y la espera, y la caída se concentra en entradas lentas, apunta a capacidad. Si pasan ambas cosas, probablemente interactúan. Si no pasa ninguna, hay que mirar post-SQL o cambios de definición. El dato mínimo es una tabla de entradas con el ajuste congelado al entrar y el primer contacto humano, y un roster semanal de SDR/AE con su ramp. Todo esto es asociación: para saber si más capacidad recupera compras hace falta un experimento o experimentos naturales, como llegadas fuera de horario o reparto por turnos.

- Pregunta: ¿Cómo se separa una capacidad comercial insuficiente de una caída en la calidad de la máquina de leads?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-121, F-122, F-124, F-120, F-159 · Tablas: —
- Intención visual: Matriz 2×2: mezcla de ajuste × velocidad de atención, cada cuadrante con su lectura.
- Limitación: Pendiente de tu aceptación: F-121, F-122, F-124, F-120 y F-159 están propuestos.
- Limitación: No está sostenido usar Self Service como grupo de control (X-012).
- Limitación: El gasto de Team/Payroll no mide capacidad (X-014).
- Limitación: H-005, H-006 y H-028 siguen abiertas.
- En palabras de Hugo: “la capacidad comercial instalada no alcanza la demanda generada, la calidad de la máquina de leads bajó”

**C-013 · Proponemos primero definiciones y fuentes comunes, unidas por un ID de cuenta**

Capa de datos: un CRM con puerta, canal e historial de etapas fechado (quién movió cada tramo); analítica digital que registre el canal desde la primera visita; facturación con suscripción, tarifa, descuento y periodo de servicio; y un ID de cuenta que cruce CRM, producto y cobro. Desde el primer mes, con los pagos, se opera el nudo y el lado derecho: primeros pagos, ticket estabilizado, puente del MRR pagado observado, churn observado junto al persistente y la vuelta de pagadores. Hay que saber que hoy el cobro se confunde con churn y con expansión. Todo el lado izquierdo espera al CRM: entradas por puerta, conversión por cohorte, estancamientos, carga y tiempos. La prueba más rápida es que Finora etiquete hacia atrás, desde el CRM, a los pagadores observados.

- Pregunta: ¿Qué base técnica necesita el CRO para operar el funnel y qué puede operar desde el primer mes?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-145, F-146, F-144, F-191, F-213, F-136 · Tablas: —
- Intención visual: Capas: fuentes abajo unidas por un ID de cuenta y métricas gobernadas encima; lo que se enciende primero frente a lo que espera al CRM.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: D-007 deja fuera el modelo de datos y los dashboards; D-018 (propuesta, la decides tú) lo lee como «no construir en esta etapa». Esto es diseño propuesto, no construido.
- Limitación: Que los datos del caso no traigan canal ni etapas no prueba que Finora no los registre.
- Limitación: Para el lado Revenue, la primera pieza técnica es la facturación (F-145).
- En palabras de Hugo: “técnica: pulir CRM, analítica digital”

**C-014 · Proponemos un tablero por foro atado a decisiones: semanal, mensual y trimestral**

Semanal · pregunta: ¿qué entradas y oportunidades se están atorando? · métricas: estancamientos por etapa, cobertura de primer contacto y carga por SDR/AE · decisión: reasignar SDR/AE entre funnels, reactivar o descalificar · dueños: el CRO con los líderes de SDR y AE.
Mensual · pregunta: ¿qué funnel y qué canal traen clientes que se quedan? · métricas: alcance a primer pago por cohorte y puerta, ticket estabilizado y permanencia temprana por canal · decisión: mover inversión entre canales y ajustar la regla de calificación o de reparto · dueños: el CRO con Marketing y Finanzas.
Trimestral · pregunta: ¿dónde poner capacidad e inversión y qué pasa con el precio de entrada? · métricas: payback por funnel cuando exista CAC en COP, retención por cohorte y mix de rutas · decisión: revisar precio o plan de entrada, y contratar o reasignar capacidad · dueños: CEO, CFO y CRO.
Los análisis ad hoc se abren por hipótesis de la matriz. Los agentes de IA y la atribución van encima: trabajan solo sobre métricas gobernadas y entran con un piloto controlado, y la atribución reparte crédito, no prueba causa.

- Pregunta: ¿Qué decisiones le permite tomar al CRO y en qué foro?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-147, F-148, F-149, F-144 · Tablas: —
- Intención visual: Escalera de cadencia: foro → pregunta → métrica → decisión → dueño, de lo táctico a lo estratégico, con agentes y atribución como capa superior.
- Limitación: Pendiente de tu aceptación: F-147, F-148, F-149 y F-144 están propuestos.
- Limitación: D-007 deja fuera los dashboards; D-018 (propuesta, la decides tú) lo lee como «no construir en esta etapa». Es un tablero propuesto, no construido.
- Limitación: El brief no define las decisiones del CRO: las del tablero son una propuesta para validar con él.
- Limitación: El payback por funnel solo existe cuando haya CAC en COP.
- En palabras de Hugo: “decision making: dashboards automatizados por foro, análisis ad hoc, agentes de IA”

### S3 · Revenue
_Con solo el monto pagado, cada ejemplo del CFO admite lecturas distintas. Proponemos cómo introducir descuentos temporales, una Propuesta de Modelo de datos que separa el valor de la suscripción del precio pagado y una regla de clasificación. Cerramos respondiendo los casos del CFO con el modelo._

**C-015 · Lo observable es el primer y segundo pago; el descuento no es verificable**

La mediana del primer pago de las altas es COP 63,0 mil en 2022, COP 36,8 mil en 2023 y COP 42,0 mil en 2024. La del segundo pago, entre quienes lo hacen, es COP 52,5 mil, COP 36,8 mil y COP 38,9 mil. El segundo pago coincide exactamente con el primero en 73,5%, 90,3% y 77,3% de las altas, y el primer pago supera con holgura al segundo en 23,2%, 7,1% y 11,6%: la brecha inicial es sobre todo de 2022. Eso describe la forma del primer cobro, no un descuento: en los datos no hay lista, plan ni descuento.

- Pregunta: ¿Qué data observable de pricing introductorio podemos sacar?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-083, F-160, F-166, F-086, F-087, F-134, F-093 · Tablas: T-062, T-054, T-055, T-051
- Intención visual: Antes/después por cohorte: primer pago frente a segundo pago; la brecha se cierra después de 2022.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: T-053 da otras medianas del segundo pago para las mismas cohortes. Parece otra definición (incluir o no a quien no pagó): falta conciliar.
- Limitación: La huella de un descuento limpio casi no aparece (F-134), pero ausencia de evidencia no es evidencia de ausencia: el caso habla de introducir descuentos.
- Limitación: No se leen descuentos a partir del tamaño de un salto del monto.
- En palabras de Hugo: “qué data observable de pricing introductorio podemos sacar”

**C-024 · Con cliente, mes y monto se ve qué cambió, no por qué**

Se puede: clientes activos, MRR pagado observado y su puente, primeros pagos, ticket estabilizado, churn observado y persistente, y cohortes. Con cuidado, el puente, porque el cobro se mezcla con el movimiento: 29% del MRR de expansión se revierte al mes siguiente, 44% de los churns observados vuelve a pagar al mes siguiente y 42,6% del MRR de reactivación llega cubriendo los meses del hueco más el corriente. La contracción, en cambio, casi no revierte: 4,0% regresa al nivel previo y 88,9% sigue igual o más abajo. Eso no descarta que parte de la contracción sea cobro. Si llega justo después de un primer pago o de una reactivación que cubría varios meses, la baja es la vuelta al monto usual y se sostiene; separarla pide el periodo de servicio. No se puede: lista, tarifa, plan, descuento, estado de la suscripción ni nada antes del pago. Además, la vuelta de pagadores es un loop de Revenue, no el Reactivate del funnel.

- Pregunta: ¿Qué puede y qué no puede responder cliente + mes + monto?
- Rol: diagnosis · confianza medium · fuerza pending
- Evidencia: F-172, F-174, F-180, F-182, F-184, F-185, F-131, F-135, F-136, F-186, F-213 · Tablas: T-074, T-076, T-082, T-086
- Intención visual: Semáforo de observabilidad: se puede / con cuidado / no se puede, con el puente en amarillo y la contracción separada de la reactivación.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: R-011 ubica buena parte de la contracción justo después de un primer pago o una reactivación (X-037), y R-028 solo prueba la reversión al mes siguiente (X-100). Se reconcilian así, sin una cifra conjunta.
- Limitación: Una parte del MRR de reactivación no encaja en firmas de cobro (T-082). Podrían ser regresos reales (H-064).
- Limitación: El puente normalizado exacto no es medible sin periodo de servicio (F-186).
- En palabras de Hugo: “qué data observable podemos sacar”

**C-016 · Con solo el monto pagado, cada ejemplo del CFO admite lecturas distintas**

El dato es un monto por cliente y mes, sin lista, plan, descuento, crédito ni periodo de servicio. Una baja puede ser contracción o descuento, y un monto estable puede esconder una expansión compensada por un descuento. Además, el monto se comporta como caja: 25,3% del movimiento bruto sin altas vuelve exacto al nivel previo al mes siguiente, y 29% del MRR de expansión se revierte al mes siguiente. Por eso hoy no se puede asignar la caída por cliente entre precio de lista y descuento.

- Pregunta: ¿Por qué los ejemplos del CFO no se pueden leer con el monto pagado?
- Rol: diagnosis · confianza medium · fuerza pending
- Evidencia: F-093, F-090, F-073, F-130, F-082, F-062, F-177 · Tablas: T-058, T-061, T-028, T-074
- Intención visual: Misma observación, historias distintas: un mismo monto con lecturas alternativas lado a lado.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: F-130 tiene confianza baja y fuente sin verificar.
- Limitación: Es una prueba de observabilidad, no una lectura del histórico.
- En palabras de Hugo: “con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento)”

**C-017 · Proponemos que el descuento exista como objeto propio, con fecha de fin**

Mecanismo propuesto: cada descuento se registra como una concesión propia (tipo, valor, inicio, fin, motivo, canal y aprobador), separada del plan, la cantidad y el precio de lista, y se lee desde la factura. El puente de MRR suma líneas propias de «descuento nuevo o aumentado» y «descuento reducido o terminado». Hace falta porque las herramientas revisadas, usadas tal cual, mostrarían el fin de un descuento como expansión, y una expansión compensada por descuento como «sin cambio». Implicaciones multidisciplinarias: Ventas necesita reglas de aprobación y vencimiento; Finanzas, la convención de MRR y la conciliación con revenue y caja; Producto y Facturación, el objeto descuento y el periodo de servicio en la factura; Growth, marcar las cohortes con descuento y medirlas contra un grupo comparable.

- Pregunta: ¿Cómo debería Finora introducir descuentos temporales sin perder la respuesta a «¿por qué cambió el MRR?»?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-150, F-152, F-153, F-154 · Tablas: —
- Intención visual: Objeto separado: el descuento como capa propia con fecha de fin, encima de la suscripción y del precio de lista.
- Limitación: Pendiente de tu aceptación: F-150, F-152, F-153 y F-154 están propuestos.
- Limitación: Las herramientas revisadas (ChartMogul, Chargebee, Stripe) son contexto externo, no validado con Finora.
- Limitación: La evidencia externa asocia la adquisición con descuento a clientes de menor valor. Para Finora es una hipótesis (H-049).
- En palabras de Hugo: “mecanismo propuesto, implicaciones multidisciplinarias”

**C-018 · El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan**

No hay un estándar de mercado para tratar descuentos temporales en el MRR, y la convención «solo neto» borra justo lo que pregunta el CFO. Proponemos mostrar las capas de MRR de lista, descuento y MRR neto, más revenue reconocido y caja, y que el CFO declare cuál es la oficial. Qué vista aplica depende de si los contratos de Finora son mensuales cancelables o a plazo fijo, algo que el caso no dice.

- Pregunta: ¿Qué convención de MRR usar y qué vistas se separan cuando hay descuentos?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-151, F-153, F-154, F-132 · Tablas: —
- Intención visual: Capas apiladas: lista menos descuento igual a neto; revenue y caja al lado, desfasados.
- Limitación: Pendiente de tu aceptación: F-151, F-153, F-154 y F-132 están propuestos.
- Limitación: F-132 tiene confianza baja y fuente sin verificar.
- Limitación: H-048 (que el puente por capas separa los casos del CFO) sigue abierta hasta tener datos.
- En palabras de Hugo: “cómo introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»”

**C-019 · La Propuesta de Modelo de datos separa el valor en una escalera con vigencias**

Escalera por suscripción y mes, cada peldaño con su tabla y su vigencia. La lista, en price_book_entry: tarifa por versión de plan, periodo y moneda, con valid_from y valid_to. El precio pactado, en subscription_item_version: plan, cantidad, add-ons y precio unitario, en intervalos sin traslape. El descuento, en discount_grant: tipo, valor, inicio, fin, motivo, aprobador y el change_event que lo originó. Después vienen el MRR neto; lo facturado, en invoice_line (subtotal, descuento, neto y periodo de servicio); y lo cobrado, en payment_allocation (llave pago + factura). Todo cuelga de customer_id y subscription_id. Cada cambio nace de un change_event con fecha efectiva, fecha de registro y evidencia. subscription_month_snapshot es la foto al cierre de mes con lista, bruto, descuento, neto y caja. mrr_movement es la diferencia entre snapshots consecutivos, partida por componente: suscripción, tarifa, descuento, entrada y salida. Facturado y cobrado nunca generan movimientos de MRR, solo «efecto de cobro», y el panel actual queda como monto pagado observado, conciliado contra lo cobrado. A facturación se le pide primero: tarifas con vigencia, y plan o cantidad por cliente.

- Pregunta: ¿Cómo separar el valor de la suscripción del precio efectivamente pagado?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-130, F-132, F-133, F-151, F-152, F-168 · Tablas: —
- Intención visual: Escalera: lista → pactado → descuento → neto → facturado → cobrado, cada peldaño con su tabla, su llave y su vigencia.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos. F-130 y F-133 tienen fuente sin verificar.
- Limitación: D-007 deja fuera el modelo de datos; D-018 (propuesta, la decides tú) lo lee como «no construir en esta etapa». Es diseño propuesto, no construido.
- Limitación: Se sabe qué forma tiene la evidencia; no se sabe si Finora la tiene (F-133).
- Limitación: El histórico no se puede reconstruir en capas (F-168).
- En palabras de Hugo: “propuesta de modelo de datos (campos, tablas, definiciones)”

**C-020 · Si la suscripción no cambia, inicio o fin de descuento va a «Descuento»**

Se comparan cierres de mes consecutivos del mismo cliente, en este orden. a) ¿Cambió la lista o el precio pactado? → expansión, contracción o cambio de tarifa, con línea propia «Tarifa». b) ¿Cambió el descuento? → descuento nuevo o aumentado, o descuento reducido o terminado. c) ¿Solo cambió el cobro? → momento de cobro, fuera del MRR. El caso mixto se parte en líneas separadas, y cada mes los movimientos suman exactamente el cambio de bruto y de neto. Para los grupos del CFO: al entrar, el alta va por el bruto y el descuento inicial va en su propia línea. Quien sale, sale por su bruto, y su descuento se libera dentro del churn, nunca como fin de descuento. En quien continúa, solo el cambio de descuento va a la línea Descuento.

- Pregunta: ¿Cómo clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-150, F-152, F-151, F-131 · Tablas: —
- Intención visual: Árbol de decisión: lista → descuento → cobro; el caso mixto se parte en líneas que suman al neto.
- Limitación: Pendiente de tu aceptación: F-150, F-152, F-151 y F-131 están propuestos.
- Limitación: D-007 deja fuera el modelo de datos; D-018 (propuesta, la decides tú) lo lee como «no construir en esta etapa». Es una regla propuesta, no construida.
- Limitación: Cuando un descuento porcentual se aplica a un bruto que cambió, qué parte va a suscripción y qué parte a Descuento es una convención a documentar (R-011). Si Tarifa va en línea propia o dentro de expansión lo decide el CFO.
- Limitación: Solo aplica hacia adelante: el histórico no trae descuentos (F-093). Cubre los tres grupos de D-002.
- En palabras de Hugo: “probablemente lo integra la misma propuesta de modelo de datos”

**C-025 · Con el modelo propuesto, cada caso del CFO se lee en su capa**

Con las cifras del enunciado, como ejemplo. Si pagaba 100 y ahora paga 80, se mira la lista: si el bruto bajó a 80, es contracción; si sigue en 100, es un descuento nuevo en su línea. Si la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100, se registran una expansión de +30 en suscripción y un descuento nuevo de −30, y el neto no cambia. Si después desaparece el descuento y paga 130, esos +30 son fin de descuento, no expansión. El negocio subyacente se lee en el MRR de lista, y el revenue que se deja de capturar, en la capa de descuento, vigente y por vencer. Hacia atrás no se puede medir, porque el histórico no trae lista ni descuentos. El costo real de un descuento pide un grupo comparable, y la convención la decide el CFO. Hoy el puente de monto pagado ya confunde cobro con expansión y churn: 29% de la expansión se revierte al mes siguiente y 44% de los churns vuelve a pagar al mes siguiente. Lo que se ve es composición, no beneficio comercial.

- Pregunta: El CFO pregunta: si un cliente pagaba 100 y ahora paga 80, ¿es contracción o descuento? Si la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100, ¿qué pasó? ¿Y si desaparece el descuento? ¿Qué pasa con el negocio subyacente y cuánto revenue dejamos de capturar?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-168, F-172, F-174, F-177, F-178, F-150, F-151 · Tablas: T-074, T-076, T-080
- Intención visual: Libro de cuentas lado a lado: cada caso del CFO en capas lista/descuento/neto, frente a la lectura del panel actual.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Los casos son ejemplos construidos con las cifras del enunciado: prueban un límite del modelo, no describen lo que pasa en Finora.
- Limitación: R-027 no armó la simulación con datos: el panel no trae lista ni descuento (F-168).
- Limitación: F-177 y F-178 están en tensión (X-098): «composición» describe quién entra, no prueba que no haya precio o descuento detrás.
- Limitación: No hay cifra histórica de revenue no capturado (X-038). El costo del descuento pide un grupo comparable (H-049).
- En palabras de Hugo: “preguntas del CFO contestadas con el modelo propuesto”

## Recomendaciones
- Revisar y aceptar o rechazar los findings citados. Empezar por los de S1 y S2.4 (F-071, F-072, F-075, F-097, F-164) y los de diseño de S2.3 (F-209 a F-213). _(si Antes de marcar el paquete Ready: hoy ningún claim tiene evidencia aceptada.)_
- Confirmar o rechazar D-018. Si la confirmas, el catálogo de métricas, S2.7, S3.3 y S3.4 entran como diseño propuesto; si no, pasan a apéndice y esas láminas cierran en diagnóstico. _(si D-007 (activa) choca con D-017; decides tú.)_
- Fijar con Finora los parámetros del funnel: el nudo común (primer pago, X-052), qué cuenta como intervención (Q-063), el umbral de estancado y la caducidad del episodio (Q-064), y la ventana de conversión. _(si Antes de etiquetar rutas o calcular tasas.)_
- Elegir la base de comparación de la composición (ene-22 o dic-22) y usar la misma en S1 y S2.4 (X-060). _(si Mientras no se elija, mostrar el rango de ambas bases.)_
- Pedir a Finora, en una sola lista:
- Q-065: leads del CRM con fechas por etapa, puerta, canal y estado de salida.
- X-021: entradas únicas por mes y tipo.
- X-022: mezcla por canal, motion y segmento, con vínculo al pago.
- X-023: fecha de entrada y de primer pago por cuenta.
- X-024: señales de ajuste al entrar.
- X-025: historial de etapas, no solo el estado actual.
- X-026: motivos de pérdida estructurados.
- X-027: si «más leads» cuenta registros o entradas únicas, y en qué periodo.
- X-011: roster semanal de SDR/AE con ramp y tiempos de contacto.
- X-046: plan y cantidad por cliente.
- X-047: tarifas de lista con vigencia.
- Una bitácora con fecha de cambios comerciales: precio, plan, metas y comisiones, formularios y reglas de calificación y reparto (X-110).
- Además, la unidad y la escala del gasto de S&M (X-001). _(si Es la condición para pasar cualquier causa de la matriz de posible a validada o descartada, y para tener CAC en COP, capas de MRR y clasificación de descuentos.)_
- Pedir a Finora que etiquete hacia atrás, desde el CRM y solo con información previa al contacto, la puerta y la ruta de los pagadores observados. _(si Si una parte relevante queda «sin clasificar» (H-065), ajustar la regla antes de reportar el mix.)_
- Si la matriz apunta a capacidad (sube la carga y cae la cobertura), probar la palanca antes de contratar: con experimentos naturales (llegadas fuera de horario, reparto por turnos) o con un piloto de reparto al azar. _(si Solo después de cerrar los artefactos del lado de leads. La conversión de Hybrid por sí sola es asociación.)_
- Antes de lanzar descuentos temporales, que el CFO declare la convención de MRR y que facturación registre el descuento como objeto con fecha de fin, visible en la factura. _(si Si Finora decide introducir descuentos; si no, el modelo igual separa tarifa y plan.)_
- Lanzar los descuentos con cohortes marcadas y un grupo comparable sin descuento, idealmente asignado al azar, para medir su costo real en MRR de lista, retención y churn al vencer. _(si Si se lanzan descuentos (H-049).)_
- Conciliar las cifras que chocan: el churn observado de 2024 (T-034 frente a T-002) y las medianas del segundo pago (T-053 frente a T-062). _(si Antes de que S2.4, S2.5 y S3.1 pasen a láminas.)_
- Aprobar o no la regla de normalización (reparto de pagos multimes y ventana de gracia) para mostrar el MRR normalizado y el churn persistente junto al observado. _(si Si no se aprueba, el ARR no se muestra y el churn persistente va como proxy.)_
- Probar Generación de Demanda dirigida a Salud frente a un grupo comparable. _(si Solo si con margen, costo de servir y canal se confirma H-044; hoy es una señal descriptiva.)_

## Apéndice candidato
- Detalle del archivo de gasto de S&M — Sostiene los caveats de unidad, cortes y Habilitación; en la lámina distrae.
- Correlaciones gasto–altas — Respalda que no hay relación positiva sin cargar la lámina de gasto.
- Firmas de cobro en el monto — Sostiene el «con cuidado» del puente: montos fuera de grilla, subidas que revierten, huecos de un mes.
- Churn caro por promedio frente a mediana — Es un matiz del churn que no cambia la historia principal.
- Paso 1 en detalle (oct-24 y emparejamiento de IDs) — Acota los artefactos del lado de pagadores; el detalle es técnico.
- Catálogos completos de métricas y eventos de los especialistas — Fórmulas, granos y eventos para el equipo de datos; la lámina solo muestra el catálogo resumido.
- Ejemplos ilustrativos del modelo de datos — Filas de snapshot y mrr_movement para los casos A, B y C y para la salida con descuento; son ejemplos construidos.

## Preguntas sin resolver
- S2.1 · ¿Qué relaciones que comentaste deben mostrarse? Están por precisar; la lámina queda missing.
- ¿Cuál es el hito de adquisición y nudo común del CRO: Won, primer pago o suscripción activa? (X-052)
- ¿Qué cuenta como intervención humana (Q-063), y cuáles son el umbral de estancado y la caducidad del episodio (Q-064)?
- ¿Existe en Finora Self Service como compra sin persona (prueba gratis, freemium o pago al registrarse)? (Q-046)
- ¿Qué hace a un lead Engaged o SQL en Finora? El brief solo da la secuencia.
- ¿En qué periodo ve el CRO «más leads», y cuenta registros o entradas únicas? (X-016, X-027, X-106)
- ¿Qué decisiones quiere tomar el CRO y en qué foros? El tablero propone algunas y hay que validarlas con él.
- ¿Qué decide el CEO con el Overview? La audiencia lo deja sin definir.
- ¿Los contratos de Finora son mensuales cancelables o a plazo fijo? De eso depende qué vista de MRR, revenue y caja aplica (F-153).
- ¿Qué base de comparación usamos para la composición: ene-22 o dic-22? (X-060)
- ¿Cuál es el churn observado de 2024: el de T-034 o el de T-002? (X-099, X-101)
- ¿Por qué difieren las medianas del segundo pago entre T-053 y T-062?
- ¿Se confirma D-018 frente a D-007?
- ¿Cuál es la unidad y la escala del gasto de S&M, y SoftwareTools y Freelance van en Habilitación o en producto? (X-001, X-002)
- Framing está en needs_review: ¿lo revisas antes de pasar este paquete a láminas?

## Validación
- ⚠ C-024: lenguaje causal («porque») — la evidencia es observacional.
- ⚠ Láminas del guion sin evidencia todavía: S2.1 (van a research, no se rellenan).
