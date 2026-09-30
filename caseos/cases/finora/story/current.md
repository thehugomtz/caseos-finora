# CURRENT STORY — v3
> Generado 2026-09-29T20:10 · con problemas de validación

## Audiencia
CEO: contexto de salud general del modelo (Overview) antes de Growth y Revenue. Qué decide todavía no está definido., CRO: cómo definir, medir y operar el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos., CFO: cómo introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»: mecanismo, modelo de datos y clasificación.

## Objetivo
BORRADOR 3 (N-050 a N-054). Incorpora tus cambios: C-021 con las etapas literales por ruta y canal, y su dueño (R-031); C-006 rehecho como «cómo se mide cada funnel», por familia y con fórmula; C-009 con las métricas que faltaban y una regla MECE; C-023 como árbol MECE por niveles, sin «artefacto» (medición contra negocio, R-032); C-013 con el modelo de datos as-is vs to-be (R-033); C-017 con el modelo de precios y descuentos y sus casuísticas (R-034). Ajustes que se derivan de esos cambios: C-005 (el canal pasa a ser atributo de la entrada), C-011 y C-012 (coherentes con el árbol), C-014 (usa los nombres nuevos de las métricas), C-022 (gobierna el catálogo sin duplicar métricas), C-019 y C-020 (coherentes con C-017), y C-020 y C-024 sin F-131 (choca con F-184, X-100). C-001 y C-004 conservan las gráficas que elegiste. Todo cita findings propuestos: queda pendiente de tu aceptación y el paquete no puede marcarse Ready. El choque entre D-007 y D-018 lo decides tú.

## De → A
- **Hoy creen:** Finora suma clientes mucho más rápido que monto pagado. Esa brecha se lee con explicaciones que los pagos no confirman: «más leads que no convierten» y «cambios de suscripción o descuentos».
- **Deben salir creyendo:** La brecha coincide con quién entra: más primeros pagadores, con menor ticket estabilizado, dentro de cada industria. No coincide con la base previa ni con salidas persistentes. El porqué del CRO y del CFO no está en los datos del caso, pero hay un diseño concreto para decidirlo: rutas con sus etapas literales por canal y dueño, métricas por funnel y comunes sin duplicados, un árbol MECE de la brecha con su dato y su palanca, y modelos de datos as-is vs to-be para el funnel y para precios y descuentos.

## Governing thought
> La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos: proponemos medir por funnel y separar descuento de suscripción.

## Preguntas ejecutivas
- Q-003 (CEO) ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?
- Q-001 (CRO) ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- Q-002 (CFO) ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?
- Q-025 (CFO) Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿cómo se lee cada caso?
- Q-026 (CFO) ¿Qué pasa con el negocio subyacente y cuánto revenue dejamos de capturar por decisiones comerciales?

## Arco
SCR con pilares, siguiendo tu guion aprobado (Overview → Growth → Revenue) — La respuesta va primero y cada lámina sigue el orden lo que vemos → lo que no vemos → propuesta concreta. En Overview, la brecha coincide con quién entra y no con la base previa. En Growth vemos más primeros pagadores, con menor ticket estabilizado dentro de cada industria, y un gasto que no se mueve con ellos. El porqué no está en los pagos, así que proponemos: rutas con etapas literales por canal (S2.3), métricas por funnel y comunes sin duplicados (S2.5), un árbol MECE de la brecha (S2.6) y un modelo de datos as-is vs to-be con foros atados a decisiones (S2.7). En Revenue mostramos qué se lee del monto y qué no, el mecanismo y el modelo de descuentos por origen, la escalera de valor y la regla de clasificación. El cierre responde los casos del CFO con el modelo.

### S1 · Overview
_Situación: Finora suma clientes mucho más rápido que monto pagado, y la caída por cliente activo coincide con quién entra. La sección abre Growth y Revenue y cierra con la propuesta de reportar por cosecha con una base de comparación fija._

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

Con base ene-22, la descomposición por cosecha asigna 108% del cambio del MRR pagado observado por cliente activo a la composición de la base; con base dic-22, 84%. La cifra depende de la ventana; la dirección no. Los clientes activos en ene-22 pasan de COP 92,8 mil a COP 97,4 mil por cliente (+5%), mientras que las cosechas 2023 y 2024 ya son 65% de los activos y 50% del MRR en oct-24, con COP 46,3 mil y COP 43,0 mil por cliente. Propuesta: reportar el monto por cliente siempre partido en base previa y cosechas, con una base de comparación fija que decidas tú.

- Pregunta: ¿El −38% por cliente viene de la base que ya teníamos o de quién entra?
- Rol: diagnosis · confianza high · fuerza pending
- Evidencia: F-075, F-076, F-056, F-058, F-097, F-092, F-019 · Tablas: T-030, T-031, T-041, T-027
- Intención visual: Mezcla que arrastra: la base previa sostiene su monto mientras las cosechas nuevas, con menos monto por cliente, ganan peso y bajan el promedio.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Composición no es causa: no separa tipo de cliente, plan, tarifa ni descuento; el panel no trae esas tablas (F-062).
- Limitación: La base de comparación (ene-22 o dic-22) es una decisión pendiente (X-060).
- Limitación: La salida de pocas cuentas grandes también baja el promedio (F-101, F-102) y aquí no se separa.
- Limitación: «Quién entra» describe primeros pagadores observados, no la calidad de los leads.
- En palabras de Hugo: “Observaciones generales y salud del negocio que introducen las secciones siguientes.”

### S2 · Growth
_Lo que sí vemos (S2.2, S2.4): más primeros pagadores con menor ticket estabilizado y un gasto de S&M que no se mueve con ellos. Lo que no vemos (S2.3, S2.6): rutas con sus etapas literales por canal y un árbol MECE de la brecha, cada hoja con su dato. Cómo operarlo (S2.5, S2.7): métricas por funnel y comunes sin duplicados, un modelo de datos as-is vs to-be y foros atados a decisiones. S2.1 queda sin contenido._

**C-003 · Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias**

Los primeros pagadores observados pasan de 27,2 por mes en 2022 (mar–dic) a 54,7 desde ene-23. Es un escalón sin tendencia distinguible después: pendiente de +0,47 por mes, con intervalo de −0,40 a +1,33. Entre 2022 y 2024 suben +104% por mes, mientras el valor inicial que incorporan sube +6% (run-rate temprano) o +17% (monto habitual). Con ticket estabilizado, la mediana del segundo pago baja de COP 52,5 mil en 2022 a COP 36,8 mil en 2023 y COP 38,9 mil en 2024. El efecto dentro de cada industria explica 91% del cambio 2022→2023 y 96% del cambio 2022→2024.

- Pregunta: ¿Qué cambió en quién entra y en qué industrias?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-110, F-039, F-113, F-045, F-037, F-160, F-161, F-162, F-163, F-164, F-114, F-030, F-192, F-193 · Tablas: T-016, T-019, T-062, T-066, T-020
- Intención visual: Outgrow: el conteo de primeros pagadores sube en escalón y se aplana, mientras el valor que traen crece mucho menos.
- Limitación: Pendiente de tu aceptación; F-160 a F-163 tienen confianza media.
- Limitación: Primer pago observado no es adquisición (ni Won ni suscripción activa); el hito lo acuerda el CRO (X-052).
- Limitación: El escalón de inicios de 2023 puede ser en parte registro (H-024) o un cambio operativo (H-025, H-068). Sin confirmar.
- Limitación: El ticket estabilizado sigue siendo monto pagado: no separa tarifa, plan, empaquetamiento ni descuento (F-167).
- Limitación: La industria es la única segmentación disponible: no sustituye al canal ni a la ruta.
- En palabras de Hugo: “Revisar entradas y actividad económica de clientes y segmentos.”

**C-004 · Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas**

En 2023 jun–dic hay 60,6 primeros pagadores por mes, frente a 45,2 en ene–may. En esos mismos tramos, la Generación de Demanda (ToFu) baja de 1,73 u a 0,82 u por mes y el S&M total, de 3,01 u a 1,44 u. La correlación en niveles entre S&M total y primeros pagadores del mismo mes es −0,57; en cambios mes a mes, el mayor valor absoluto es 0,27 (p mínimo 0,14): no hay una relación positiva que leer. El archivo viene en unidades reportadas (u), sin escala a COP, y hasta may-23 Team es un 12% fijo del total durante 17 meses. Propuesta: que Finora documente la unidad del gasto y lo registre por canal y campaña (campaign_spend, C-013), para leer el gasto contra entradas y Won por cohorte y canal, no cruzando fechas.

- Pregunta: ¿Hasta dónde se puede relacionar la Inversión en Marketing por categoría con las ventas cruzando fechas?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-214, F-220, F-219, F-221, F-217, F-107, F-118, F-023, F-024, F-063, F-066, F-115, F-065, F-068, F-119, F-207 · Tablas: T-101, T-107, T-106, T-108, T-104, T-013, T-024, T-008, T-005, T-009
- Intención visual: Dos paneles con los mismos meses (ene-22 a oct-24): arriba el S&M total por mes (unidad reportada), abajo las altas por mes; en 2023 jun-dic el gasto baja mientras las altas suben (T-101). Apoyo: dispersión de S&M contra altas con un mes de rezago (F-220, T-107) y barras por ventana de altas por mes y S&M por alta (T-108). Sin atribuir ventas al gasto.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: La unidad del gasto no está documentada (F-063): no se puede leer como COP.
- Limitación: Hasta may-23 el archivo se comporta como una asignación de arriba hacia abajo (F-066); PayrollExpenses es negativo en 5 meses y Freelance queda en cero desde jun-23 (T-009).
- Limitación: No se puede decidir si SoftwareTools y Freelance son Habilitación o producto (F-068).
- Limitación: Es coincidencia temporal, no efecto (F-119, F-222). El valle de ago-23 y el corte de jun-23 pueden ser contables (H-023, H-070, H-071).
- En palabras de Hugo: “Inversión de S&M por categoría (generación de demanda ToFu: Paid Media y publicidad no web · Team: Payroll Expenses y Travel · habilitación, ¿producto?: Software Tools y Freelance) y hasta dónde se puede relacionar con ventas cruzando fechas.”

**C-005 · Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar**

La unidad es el journey: cuenta × intento (varias personas de una misma empresa son un solo journey). Al entrar se fijan dos atributos que ya no cambian: la puerta (producto o CRM/Ventas) y el canal (outbound SDR, inbound «hablar con ventas», referido o partner, o signup por paid media, publicidad no web u orgánico). La ruta se clasifica al final, por eventos: Executive si arranca con persona y nunca pasa por Checkout Self; Self Service si nunca interviene una persona; Hybrid A si arranca en el producto y después entra una persona; Hybrid B si arranca con persona y cierra por Checkout Self. Mientras el journey está abierto, la ruta es provisional. Reactivate no es otra ruta: es un loop para journeys estancados, con bandera, que no crea un New nuevo. Los clientes que vuelven a pagar son un loop de Revenue y se miden aparte.

- Pregunta: ¿Cómo definir el funnel si no todos lo recorren igual?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-209, F-210, F-211, F-212, F-213, F-188, F-190, F-140, F-155, F-223, F-224, F-226 · Tablas: —
- Intención visual: Split y converge: una entrada con puerta y canal fijos se abre en rutas según quién mueve cada tramo, y todas llegan al mismo nudo. Reactivate aparece como un loop que devuelve el journey a la etapa donde se estancó.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Es propuesta: hoy el modelo no tiene leads, etapas, dueños, canal ni ruta (F-223).
- Limitación: Qué cuenta como intervención de persona sigue abierto (Q-063). Con la regla actual, una entrada que pide persona y que nadie atiende termina como Self Service (H-072).
- Limitación: No sabemos si existe compra self-serve sin persona, ni si hay prueba gratis, freemium o pago al registrarse (Q-046).
- Limitación: La ruta no se infiere del monto. La tasa de Hybrid refleja a quién eligen tocar SDR/AE (H-050): por eso las tasas se comparan entre puertas, no entre rutas.
- En palabras de Hugo: “Assisted / Self Service / Executive, con canales (incl. digital, WoM, clientes que no requirieron KAM), funnel propuesto.”

**C-021 · Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño**

Por ruta y canal, en orden y con dueño. Es propuesta; solo Executive outbound es literal tuyo. EXECUTIVE · outbound SDR: New → Working SDR → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won; el SDR es dueño hasta SQL SDR y el AE desde Demo AE · inbound «hablar con ventas» (paid media, publicidad no web u orgánico): New → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won; se salta Working SDR porque la cuenta levantó la mano · referido o partner (tu WoM, por confirmar): New → Demo AE → Proposal AE → Won, solo con AE. SELF SERVICE · signup en producto (paid media, publicidad no web u orgánico): New → Signup Self → Activated Self → Checkout Self → Won; dueño Growth/Producto, por confirmar; si no hay prueba ni registro antes del pago, queda New → Checkout Self → Won. HYBRID A · signup en producto: New → Signup Self → Activated Self → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won; pasa de Growth/Producto al SDR y al AE; la persona entra por una señal de uso, fit o intención, o porque la cuenta pide ayuda; Engaged SDR y SQL SDR se pueden saltar; variante: la persona ayuda y la cuenta paga sola por Checkout Self. HYBRID B · outbound SDR: New → Working SDR → Engaged SDR → SQL SDR → Demo AE → Checkout Self → Won; pasa del SDR al AE y la cuenta cierra sola; Demo AE se puede saltar · inbound «hablar con ventas»: lo mismo, sin Working SDR. REACTIVATE (loop): un journey estancado en cualquier etapa abierta entra al loop y, si se re-engancha, vuelve a su etapa con su puerta y su ruta. QUÉ DEL EXECUTIVE APLICA A LOS OTROS: New y Won aplican a todas las rutas. Working SDR solo donde hay prospección outbound (Executive e Hybrid B outbound). Engaged SDR, SQL SDR y Demo AE aplican a Executive, a Hybrid A (se pueden saltar) y a Hybrid B. Proposal AE aplica a Executive y a Hybrid A; en Hybrid B la reemplaza Checkout Self. Self Service no usa ninguna etapa de SDR ni de AE: las cambia por Signup Self, Activated Self y Checkout Self.

- Pregunta: ¿Qué etapas aplican a cada funnel, por canal, literalmente como las del Executive?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-209, F-210, F-211, F-223, F-224, F-225, F-191, F-155 · Tablas: —
- Intención visual: Reusar o reemplazar: qué etapas del Executive reusa cada ruta, cuáles salta y cuáles cambia por etapas de producto, con el traspaso de dueño (SDR → AE → cliente) visible en cada ruta.
- Limitación: Pendiente de tu aceptación: F-209 a F-211 y F-223 a F-225 están propuestos.
- Limitación: No afirmamos que Finora tenga criterios de etapa definidos: el brief da la secuencia y un traspaso SDR → AE que ocurre «sobre todo» y «normalmente». Demo y Proposal hay que confirmarlas contra el CRM.
- Limitación: Las etapas de Self Service e Hybrid son propuesta. Activated Self se define con Producto, y no sabemos si hay prueba, freemium o pago al registrarse (Q-046).
- Limitación: La frontera entre Executive inbound e Hybrid A depende de Q-063. Una variante de Hybrid B (el SDR contacta y la cuenta se registra sola) es Hybrid B con la regla laxa y Self Service con la estricta.
- Limitación: Faltan por confirmar el canal referido/partner y el dueño de Self Service. Parte de los saltos de etapa puede ser registro del CRM (H-051).
- En palabras de Hugo: “«queria ver una prouesta aterrizada por casuistica de canal literalmente de los funeles asi como te pase la de new, working, SDR, engaged, bla bla quiero ver cuales aplican para los otros»”

**C-007 · La pérdida está en el monto por cliente de cosechas de menor ticket**

No se concentra en una industria: el MRR pagado observado por cliente activo bajó en las 6 entre dic-22 y oct-24. Cayó más en Servicios profesionales (−46,6%), Restaurantes (−45,6%) y Retail (−43,1%) que en Producción (−18,8%), Tecnología (−15,5%) y Salud (−14,4%). Se asocia a cosechas: con base dic-22, la composición explica 84% del cambio, y el menor ticket de entrada ocurre dentro de cada industria (96% del cambio 2022→2024). No se asocia a salidas persistentes: el churn observado baja de 3,52% a 2,04%, mientras que el de quienes no vuelven a pagar en un trimestre queda en 0,98% y 0,96%.

- Pregunta: ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento?
- Rol: diagnosis · confianza high · fuerza pending
- Evidencia: F-097, F-092, F-096, F-094, F-020, F-164, F-163, F-075, F-033, F-183, F-059, F-101, F-102 · Tablas: T-038, T-040, T-066, T-041, T-030, T-002
- Intención visual: Difusión contra concentración: la caída aparece en todas las industrias con distinta intensidad, mientras que el peso de las cosechas de menor ticket es lo que la concentra.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: La industria es una segmentación disponible, no un sustituto de canal ni de ruta; no se afirma una causa industrial.
- Limitación: No hay tamaño de cliente, motivos de churn ni estado de suscripción (F-106).
- Limitación: Quienes se van pagaban más en promedio, pero no en mediana: la salida de pocas cuentas grandes también baja el promedio (F-101, F-102).
- Limitación: La cifra de composición depende de la base elegida (X-060).
- En palabras de Hugo: “Dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix).”

**C-008 · Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar**

Salud combina el menor churn persistente (0,56 puntos porcentuales mensuales), el ticket de entrada mediano más alto de 2024 (COP 52,5 mil, empatado con Restaurantes) y poco volumen: 124 clientes activos en oct-24 frente a 459 en Restaurantes. Es además de las industrias con menor caída del MRR por cliente entre dic-22 y oct-24 (−14,4%) y aporta 11,7% del crecimiento del MRR. En 2024 el churn observado por industria va de 1,46 a 2,57 puntos mensuales: un rango estrecho. Es una señal para validar con tamaño, canal y motivos de salida, no un segmento.

- Pregunta: ¿Hay industrias de bajo churn, ticket alto y poco volumen que valga la pena mirar?
- Rol: implication · confianza medium · fuerza pending
- Evidencia: F-104, F-099, F-103, F-105, F-165 · Tablas: T-048, T-049, T-067, T-047
- Intención visual: Trade-off: churn persistente contra ticket de entrada, con el tamaño de la base como volumen; Salud queda aislada en bajo churn, ticket alto y poco volumen.
- Limitación: Pendiente de tu aceptación: F-104, F-099, F-103, F-105 y F-165 están propuestos (confianza media).
- Limitación: Con pocos clientes por industria, las medianas se mueven con pocas altas.
- Limitación: Salud es la excepción del tramo 2022→2023: su ticket baja recién en 2024 (T-067).
- Limitación: No se fabrica un segmento por clustering: no hay concentración clara (H-044 sigue abierta).
- En palabras de Hugo: “Quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco volumen.”

**C-006 · Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento**

Sale directo de las etapas de C-021. Notación: journey = cuenta × intento; cohorte = los journeys con New en el mes; W = ventana fija desde New, que Finora calibra con su ciclo real. Toda tasa se lee por cohorte y solo cuando la cohorte ya cumplió W. CAPA COMÚN, por puerta y canal (es la única que se compara entre funnels). Volumen: entradas = journeys con New en el mes, por puerta y canal (p. ej., leads digitales = entradas con canal paid media u orgánico); Won por puerta y ruta, con su mezcla = Won de la ruta ÷ Won de la puerta. Calidad al entrar: entradas válidas = entradas menos duplicados, clientes actuales y ex-clientes (se marcan aparte) y spam; tasa de no-prospectos = lo quitado ÷ entradas; mezcla de ajuste = entradas de ajuste alto ÷ entradas válidas, con criterios congelados al crear el lead. Conversión: win rate de cohorte = journeys de la cohorte con Won dentro de W ÷ journeys de la cohorte (p. ej., CR digital = ese cociente para las entradas digitales). Velocidad: tiempo de cierre = mediana y P75 de los días de New a Won de los ganados, siempre por ruta y junto al win rate; Won → primer pago = mediana del tiempo entre ambos y parte de los Won sin pago en el plazo acordado. Valor: MRR de entrada por Won = mediana del MRR contratado y del primer pago; MRR nuevo = Won × MRR de entrada por Won. POR RUTA, sobre sus etapas literales (se lee solo dentro de la ruta). Volumen por etapa = journeys que alcanzan o se saltan la etapa. Conversión por etapa = de quienes alcanzaron una etapa, los que alcanzan la siguiente en N días ÷ quienes la alcanzaron. Tiempo en etapa = mediana y P75 de los días entre entrar y salir. Estancamiento = abiertos en la etapa sin cambio ni actividad por más de su umbral ÷ abiertos en la etapa. Calidad del handoff = lo que acepta el siguiente dueño ÷ lo que recibe (p. ej., SQL aceptados por el AE ÷ SQL SDR). En Executive pesan el tiempo de cierre y el estancamiento de SQL SDR a Proposal AE; en Self Service, Signup → Activated → Checkout Self, sin handoff; en Hybrid A, además, el paso de producto a SDR; en Hybrid B, Demo AE → Checkout Self. LOOP REACTIVATE: entradas al loop; re-enganche = los que vuelven a moverse de etapa ÷ los que entraron; tiempo a re-enganche; Won y MRR atribuidos al loop; stock de estancados sin tocar. HOY no se calcula nada de esto antes del pago: solo existen, sin puerta ni ruta, el total de primeros pagos observados y su monto (C-003). La retención y el costo por Won viven en las métricas comunes (C-009).

- Pregunta: ¿Cómo se mide cada funnel, más allá de la conversión?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-223, F-224, F-225, F-226, F-227, F-141, F-158, F-155, F-212, F-144, F-213 · Tablas: —
- Intención visual: Converge: cada funnel lleva sus métricas por familia en su propio tramo, y todos desembocan en el mismo nudo (Won y primer pago), el único lugar donde se comparan por puerta.
- Limitación: Pendiente de tu aceptación: F-223 a F-227 y los demás findings citados están propuestos.
- Limitación: Hoy no se calcula ninguna métrica antes del pago (F-223): es diseño.
- Limitación: W, el umbral de estancamiento por etapa y el plazo Won → pago son parámetros a acordar con Finora, no estándares de mercado (Q-064).
- Limitación: Won o primer pago como hito de adquisición sigue por acordar con el CRO.
- Limitación: La conversión de Hybrid refleja a quién eligen tocar SDR/AE, no lo que aporta la persona (H-050). Las tasas de etapas intermedias no se comparan entre rutas (SQL contra activación).
- En palabras de Hugo: “«¿cada funnel? ¿cómo lo mides? no me refiero a solo medir la connversión, ¿que metricas hay en todo eso? Ej. Digital podría tener digital leads y CR digital, algo asi, Executive ya sabes que tiens New, pero tambien puedes tener métricas de tiempo de cierre»”

**C-009 · Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta**

A tu lista (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) se suman el churn persistente, las capas de lista, descuento y neto, el quick ratio, NRR/GRR, el payback y LTV:CAC. Regla MECE: cada métrica vive en un solo lugar. Lo que pasa hasta Won y el primer pago está en el funnel (C-006); lo que pasa con la cuenta que ya paga está aquí, como común. Puerta, ruta, canal, industria y cohorte son cortes, no métricas nuevas. Semáforo: verde = se calcula hoy con nombre honesto; amarillo = proxy con una regla por aprobar; rojo = falta el dato. RESULTADO · MRR pagado observado = suma de lo pagado en el mes (verde) · MRR normalizado = cada pago repartido entre los meses que cubre (amarillo) · ARR run-rate = MRR normalizado anualizado (amarillo) · MRR de lista, descuento recurrente y MRR neto = lista − descuento; el descuento es el revenue que dejamos de capturar (rojo, se detalla en S3). MOVIMIENTO · puente: MRR nuevo + expansión + reactivación − contracción − churn = cambio del MRR (verde sobre monto pagado, se lee con cuidado); en el to-be suma la línea Descuento y deja el efecto de cobro fuera del MRR · quick ratio = entradas ÷ salidas del puente, trimestral (verde). CLIENTES · clientes activos = clientes con pago en el mes (verde) · churn de logos observado = los que dejan de pagar ÷ activos del mes previo (verde) · churn persistente = los que no vuelven a pagar en un trimestre ÷ activos del mes previo (amarillo): 3,52% contra 0,98% en 2022 y 2,04% contra 0,96% en 2024 · reactivaciones, como loop de Revenue (verde) · ARPA = MRR ÷ clientes activos, por cohorte; es lo que se pide como ARPU (verde; por usuario, rojo). RETENCIÓN POR COHORTE DE PRIMER PAGO · logos que siguen pagando en M3, M6 y M12 (verde) · NRR = MRR actual de la cohorte ÷ su MRR inicial · GRR = lo mismo sin expansión (verdes sobre monto pagado, no contractuales). EFICIENCIA · CAC = gasto de S&M ÷ nuevas cuentas; por canal y ruta = gasto del canal ÷ Won del canal (hoy solo el proxy de C-010) · payback = CAC ÷ (valor de entrada × margen bruto), en meses (rojo) · LTV empírico de ingreso = ingreso acumulado por alta a horizonte fijo, por cohorte (verde) · LTV con margen y LTV:CAC (rojos) · UCM = ARPA − costo variable de servir (rojo).

- Pregunta: ¿Qué otras métricas hay que proponer y cómo se mide cada una?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-135, F-136, F-139, F-033, F-137, F-138, F-183, F-175, F-079, F-239, F-240 · Tablas: T-002, T-085, T-034
- Intención visual: Árbol de ingreso recurrente: el resultado se abre en movimiento, clientes, retención y eficiencia; cada hoja está en un solo lugar, con su color de semáforo.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: El monto pagado mezcla fecha de cobro y mes de servicio: el churn, la reactivación y la expansión observados salen inflados (F-136). La retención aquí es «sigue pagando», no retención contractual.
- Limitación: El churn observado de 2024 no coincide entre tablas: 2,04% en T-002 y T-085 (ventana ene–jul) y 1,9% en T-034. Hay que fijar una sola cifra (X-101).
- Limitación: CAC en COP, payback, LTV con margen, LTV:CAC y UCM no tienen valor: faltan unidad del gasto, canal, margen y costo de servir (F-137, F-138).
- Limitación: El as-is no separa cancelación de mora, prepago de expansión ni plan de precio y descuento (F-239).
- En palabras de Hugo: “«C-009 ¿hay otras métricas que debean de proponerse? De todo eso hay que ser explicitos en como se miden y siempre siempre ser MECE» · MRR, ARR, ARPU, CAC, LTV, Churn, UCM y cómo medirlas.”

**C-022 · Cada métrica vive en un solo lugar del catálogo, con dueño, fuente y foro**

El catálogo no suma métricas: gobierna las del funnel (C-006) y las comunes (C-009). Cada métrica entra una sola vez con nombre, fórmula versionada, grano, dueño, semáforo de hoy, el evento o la tabla que le falta en el to-be (C-013) y el foro que la usa (C-014). Reglas MECE: un nombre, una fórmula y un lugar; puerta, ruta, canal, industria y cohorte son cortes; las tasas de etapa se leen dentro de su ruta y solo la capa común se compara entre puertas. Controles de cada mes: las entradas por puerta suman el total; los primeros pagos por ruta, más los que no se cruzan con el CRM, igualan los primeros pagos del mes; y los puentes de clientes y de MRR cierran.

- Pregunta: ¿Cómo se evita que una métrica aparezca en dos lugares o con dos fórmulas?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-155, F-158, F-159, F-213, F-135, F-139, F-148, F-224 · Tablas: —
- Intención visual: Una casilla por métrica: cada métrica del funnel y de las comunes cae en un solo lugar, conectada a su fuente y a su foro.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Es diseño: los dueños de cada métrica se definen con Finora.
- Limitación: Construirlo choca con D-007 tal como está redactada; D-018 lo decides tú.
- En palabras de Hugo: “«siempre siempre ser MECE»”

**C-010 · Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC**

Lo único que se puede calcular es el S&M total por primer pagador observado, en la unidad del archivo: 0,105 u en 2022 y 0,036 u en 2024 (−66%). No es CAC: la unidad del gasto no está documentada, no hay canal ni ruta, y el primer pago no es el hito de adquisición acordado. Además, depende de qué rubros se cuenten: Habilitación pesa 12% del S&M en 2022, 7% en 2023 y 4% en 2024, y el gasto por alta baja de 0,11 a 0,04 si se incluye y de 0,09 a 0,03 si se excluye. En las métricas comunes (C-009) queda como proxy del CAC, en rojo hasta tener la unidad y el canal.

- Pregunta: ¿Podemos calcular el CAC hoy?
- Rol: limitation · confianza medium · fuerza pending
- Evidencia: F-081, F-108, F-069, F-070, F-022, F-137 · Tablas: T-036, T-011, T-012
- Intención visual: Sensibilidad: el mismo cociente cambia según qué rubros entren; muestra lo frágil del proxy más que su nivel.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: El −66% no se lee como más eficiencia comercial: puede venir de cómo se arma el archivo (X-005, H-070).
- Limitación: No hay CAC por canal ni por ruta; no se da ningún valor de CAC en COP.
- En palabras de Hugo: “CAC (qué métricas propondrías que hoy no existen).”

**C-011 · Primero se fija qué es venta; revisar la medición en pagos no cierra la brecha**

Paso 0 del árbol (C-023): fijar qué es «venta» (Won o primer pago) y qué ventana se compara, porque en los pagos la respuesta cambia: la premisa «no más ventas» se sostiene en jul–oct 2024 y no en mar–oct. Del lado de los pagadores, tres revisiones de medición no cambian la lectura. Sin oct-24, las altas por mes de 2024 son 56 frente a 54 en 2023 (55 con octubre). Altas y reactivaciones son flujos separados: 1.476 clientes con alta, 468 reactivaciones y 0 meses marcados como ambos. Y las altas que coinciden en monto e industria con un churn reciente no superan al emparejamiento placebo (175 de 650 frente a 196 en 2023). Lo que falta revisar del lado de los leads (no-prospectos, duplicados, cambios de definición) necesita el CRM.

- Pregunta: ¿Cuánto de «no más ventas» depende de cómo se cuenta y cuánto es negocio?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-196, F-197, F-201, F-202, F-203, F-125, F-126, F-204, F-205, F-229, F-230, F-192 · Tablas: T-093, T-094, T-100, T-089
- Intención visual: Filtro: la premisa pasa por las revisiones de medición del lado de pagos y la brecha sigue en pie; lo del lado de leads queda en espera del CRM.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: No se afirma que la medición quedó descartada: con los pagos solo se acotan las revisiones del lado de pagadores.
- Limitación: No se puede verificar si un primer pagador es un negocio que ya pagaba con otro ID (F-202). En 2024 el placebo no sirve porque hay pocos churns posteriores.
- Limitación: Primer pago no es Won. La ventana jul–oct 2024 es corta y puede incluir compra adelantada (H-066, H-075).
- En palabras de Hugo: “Definir qué hipótesis ToFu y BoFu podrían estar afectando su motor y qué datos validarían o descartarían cada una.”

**C-023 · Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja**

Paso 0, antes del árbol: fijar qué es venta (Won o primer pago), una ventana W igual para el periodo base y el del aumento, cohortes por fecha de creación y New separado de Reactivate. Identidad: ventas = Σ por puerta de las entradas válidas × la conversión de cada etapa dentro de W. La brecha se reparte en este orden, cada nivel con su regla de corte, y cada pedazo cae en una sola hoja. MEDICIÓN · Validez, ¿el aumento de New es demanda nueva que puede comprar? Hojas: no-prospectos, si sube la parte de duplicados, clientes actuales, ex-clientes o spam (H-052); desfase o cambio de definición, si la ventana es más corta que el ciclo o cambió qué se registra como New (H-003, H-004, H-027, H-069); misma demanda por otra puerta, si compradores que antes entraban solos por producto ahora pasan por Ventas (H-053). NEGOCIO · Mezcla, con entradas válidas, ¿cambió quién entra o cuánto convierte cada grupo? Efecto mezcla = Σ cambio de mezcla × tasa base; efecto tasa = Σ mezcla nueva × cambio de tasa; el término cruzado se asigna con una regla fija. Hoja: entra peor mezcla (H-002, H-005), medida con señales congeladas al crear el lead. Antes del SQL, si es tasa: capacidad, si el tiempo a primer toque sube con la carga por SDR/AE (H-006); estancados sin seguimiento, si crece la bolsa de estancados y los retomados sí compran (H-054 no, H-055). Después del SQL: SQL menos maduros por la meta del SDR, si la aceptación del AE y la caída posterior empeoran solo en los SQL del SDR frente a otros orígenes (H-054); decisión en Demo o Proposal por precio, plan, competidor o funcionalidad, con motivos validados con compradores (H-056, H-008). Cobro: el Won no llega a pagar o se cae en el arranque (H-057). H-007 no es hoja: es la regla que ubica la etapa antes o después del SQL. PALANCA DEL CRO: validez → definición de lead válido, deduplicación y ruteo · mezcla → scoring y mezcla de fuentes con el CMO · antes del SQL → capacidad, SLA y cadencias de seguimiento · después del SQL → criterio de SQL y comisiones, o pricing y respuesta a la competencia con CFO y CPO · cobro → handoff a cobro y onboarding. Hoy no se valida ni se descarta ninguna hoja de validez, mezcla o etapa; de cobro solo se ve el arranque.

- Pregunta: ¿Qué podría explicar «más leads, pero no más ventas», ordenado sin que una causa aparezca en dos lugares?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-228, F-229, F-230, F-231, F-232, F-127, F-128, F-129, F-122, F-212 · Tablas: —
- Intención visual: Descomposición: la brecha se parte en orden (validez → puerta → mezcla contra tasa → etapa → cobro); cada pedazo cae en una sola hoja con su dato y su palanca, con la medición separada del negocio.
- Limitación: Pendiente de tu aceptación: F-228 a F-232 y los demás findings citados están propuestos.
- Limitación: Reordena las tres ramas de D-001 (cantidad, mezcla, compra según tiempo). Si lo adoptas, hace falta una decisión nueva que referencie D-001 (X-150); no se sobrescribe en silencio.
- Limitación: Las hojas son causas candidatas: no afirmamos que en Finora cambiaron metas, comisiones, precio o competencia. La caída post-SQL no se atribuye al AE.
- Limitación: Comparar SQL directos contra SQL del SDR no es un experimento: vienen de orígenes distintos; solo sirve ver cómo cambia cada grupo en el tiempo, y aun así es asociación.
- Limitación: Si aparecen a la vez las firmas de mezcla y de capacidad, se reportan como interacción (H-028), no como hoja nueva.
- En palabras de Hugo: “«lo mismo en C-023mucho artefacto pero no hay nada MECE, me confunde»”

**C-012 · Calidad y capacidad se separan con mezcla contra tasa, dentro de cada puerta**

En el árbol (C-023), la calidad es la hoja de mezcla y la capacidad es una hoja de antes del SQL. Se separan por puerta, entre el periodo base y el de la caída. Si empeora la mezcla de ajuste al entrar y la velocidad de atención está estable, apunta a calidad (H-005). Si la mezcla está estable, suben la carga y la espera y la caída se concentra en entradas atendidas tarde, apunta a capacidad (H-006). Si pasan ambas cosas, apunta a las dos a la vez (H-028). Dato mínimo: entradas con su banda de ajuste congelada al crearse y su primer contacto humano, más un roster semanal de SDR/AE con su ramp; el gasto de Team no mide capacidad. Con datos observados es asociación, porque SDR/AE eligen a quién tocar: para probar la palanca hacen falta experimentos naturales (llegadas fuera de horario, reparto por turnos) o un piloto.

- Pregunta: ¿Cómo se sabe si falta capacidad comercial o si bajó la calidad de la máquina de leads?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-121, F-122, F-124, F-120, F-159, F-231, F-232 · Tablas: —
- Intención visual: Dos firmas distintas: calidad mueve la mezcla con la velocidad quieta; capacidad mueve la carga y la espera con la mezcla quieta.
- Limitación: Pendiente de tu aceptación; F-120 tiene confianza baja.
- Limitación: Hoy no se puede separar H-005 de H-006: faltan entradas, reps y tiempos de contacto (F-120).
- Limitación: No usamos Self Service como grupo de control: depende de que haya existido sin SDR/AE en ambos periodos (X-012).
- Limitación: Las bandas de ajuste deben validarse antes en el periodo base. La capacidad también puede estar en el AE, no solo en el SDR (X-153).
- En palabras de Hugo: “La capacidad comercial instalada no alcanza la demanda generada, la calidad de la máquina de leads bajó.”

**C-013 · Proponemos pasar de pagos por cliente-mes a una cuenta común con demanda, funnel y suscripción**

AS-IS: tres fuentes, todas de después del pago. Pagos, con grano cliente × mes (ID, mes y monto sin escala → customer_id, month y amount_cop): responde cuánto pagó cada cliente cada mes, el puente de monto pagado y las cohortes por primer pago. No responde nada de quien no pagó, ni plan, precio o descuento, ni si un cero es cancelación, mora o desfase (44% de los churn observados vuelve a pagar al mes siguiente), ni si un pico es prepago o expansión. Industria, con grano cliente (ID en otro formato): responde el corte por industria; no responde tamaño, segmento ni cambios en el tiempo. Gasto S&M, con grano mes × rubro y sin unidad: responde el gasto por rubro y una eficiencia agregada; no responde canal ni campaña. Ninguna de las tres responde canal, puerta, etapa, intervención, tiempo de cierre ni estancamiento. TO-BE: una espina y tres capas. Espina: account (una fila por cuenta; llave account_id) y account_xref (llave: sistema + ID de origen + inicio de vigencia), que une CRM, producto, facturación y los IDs de hoy. Demanda: channel (canal × versión de la regla source/medium), campaign, touch (un toque con UTMs; llave touch_id), campaign_member (persona × campaña) y campaign_spend (gasto por campaña, con moneda). Comercial: person, lead, opportunity, stage_history (un cambio de etapa: de, a, cuándo y quién), activity y assignment. Producto y facturación: product_event, subscription, subscription_item_version (lo contratado), discount (lo descontado), invoice (lo facturado) y payment (lo cobrado). Marts: funnel_entry, una fila por entrada con puerta, ruta y fecha de cada hito, que alimenta C-006; y account_month, cuenta × mes con MRR de lista y neto y estado de suscripción, que alimenta C-009 y se concilia cada mes con el monto pagado de hoy. BRECHA → MÉTRICA QUE HABILITA: llave común → cruzar entrada, toque y pago de una misma cuenta · touch, channel y campaign_spend → entradas, win rate y costo por Won por canal · puerta y ruta en funnel_entry → cohortes y win rate por puerta · stage_history → volumen y conversión por etapa · fechas de hitos → tiempo de cierre y Won → primer pago · activity y assignment → calidad del handoff, carga por SDR/AE y estancamiento · estado de suscripción → churn por cancelación separado de mora · contratado, descontado, facturado y cobrado → MRR de lista y neto, línea Descuento y efecto de cobro (S3).

- Pregunta: ¿Qué modelo de datos se propone para operar el funnel, as-is vs to-be?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-238, F-239, F-240, F-241, F-242, F-145, F-146, F-144, F-191, F-213, F-136, F-199 · Tablas: T-096
- Intención visual: From → to: tres fuentes aisladas de después del pago pasan a una espina de cuenta que une demanda, funnel y suscripción; cada brecha que se cierra enciende una métrica.
- Limitación: Pendiente de tu aceptación: F-238 a F-242 y los demás findings citados están propuestos.
- Limitación: Es diseño, no algo construido; si entra a la historia bajo D-007 depende de D-018.
- Limitación: R-033 trata Reactivate como puerta y usa las rutas self_serve_puro, hybrid y sales_assisted; C-005 (R-031) lo trata como loop, con las rutas Executive, Self Service, Hybrid A y B. Hay que alinearlos antes de construir.
- Limitación: Varias reglas son decisiones de negocio y deben quedar escritas antes (F-241): orden de puerta, cuándo una entrada es nueva, estados New/Working/Engaged, ventana W, umbral de estancamiento y base del puente (lista o neto).
- Limitación: Mide hacia adelante, salvo que Finora tenga historial en sus sistemas (F-242). Que el caso no traiga canal ni etapas no prueba que Finora no los registre.
- En palabras de Hugo: “«C-013, quiero ver explicitamente el modelo de datos que se propone, as is vs to be» · técnica: pulir CRM, analítica digital.”

**C-014 · Proponemos un tablero por foro atado a decisiones: semanal, mensual y trimestral**

Cada foro trae sus métricas (C-006, C-009) y la decisión que habilita. Semanal (CRO, líderes de SDR/AE y RevOps): estancamiento por etapa, calidad del handoff, tiempo en etapa, carga por SDR/AE y stock sin tocar del loop Reactivate → qué journeys avanzar, retomar o descalificar, y dónde reasignar capacidad. Mensual de Growth & Revenue (CRO, Marketing, CS/KAM y Finanzas): entradas y win rate de cohorte por puerta y canal, mezcla de Won por ruta, tiempo de cierre, MRR de entrada, puente de MRR y churn persistente → mover la Inversión en Marketing entre canales y ajustar el ruteo entre rutas. Trimestral (CEO, CFO y CRO): CAC y costo por Won por canal y ruta, payback, NRR/GRR por cohorte y MRR de lista contra neto → repartir entre Generación de Demanda, Team y Habilitación. Por encima van el Análisis Ad hoc por hoja del árbol (C-023) y agentes de IA que trabajan solo sobre métricas gobernadas (vigilancia de estancamientos, pre-lectura del foro, higiene del CRM), con un piloto controlado.

- Pregunta: ¿Cómo opera el CRO el funnel de forma recurrente y qué decide en cada foro?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-147, F-148, F-149, F-144 · Tablas: —
- Intención visual: Cadencia a decisión: cada foro conecta pocas métricas con una decisión concreta, de lo operativo (semanal) a la inversión (trimestral).
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Las decisiones del CRO aún no están definidas; los foros son propuesta.
- Limitación: La atribución reparte crédito, no prueba causa: para decidir presupuesto hacen falta experimentos (F-149).
- Limitación: Depende del modelo de C-013; mientras tanto solo existen las métricas verdes de C-009.
- En palabras de Hugo: “Decision making: dashboards automatizados por foro, análisis ad hoc, agentes de IA.”

### S3 · Revenue
_Con solo el monto pagado, cada ejemplo del CFO admite lecturas distintas. Proponemos cómo introducir descuentos temporales: el descuento como objeto propio, con su origen y su source, una escalera de valor que separa la suscripción del precio pagado y una regla de clasificación. Cerramos respondiendo los casos del CFO con el modelo._

**C-015 · Lo observable es el primer y segundo pago; el descuento no es verificable**

Lo observable del pricing introductorio es el primer y el segundo pago de cada alta. La mediana del primer pago baja de COP 63,0 mil en 2022 a COP 36,8 mil en 2023 y COP 42,0 mil en 2024; la del segundo, de COP 52,5 mil a COP 36,8 mil y COP 38,9 mil. El segundo pago repite el primero en 73,5%, 90,3% y 77,3% de las altas, y el primero supera con holgura al segundo en 23,2%, 7,1% y 11,6%. Eso se asocia a pagos iniciales grandes en 2022, pero no dice si hubo descuento: sin lista ni descuento registrados, no es verificable.

- Pregunta: ¿Qué data observable de pricing introductorio podemos sacar?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-083, F-160, F-166, F-086, F-087, F-134, F-093 · Tablas: T-051, T-062, T-054, T-055
- Intención visual: Estabilización: el primer pago se acerca al segundo después de 2022; la brecha inicial se cierra.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: No se afirma que hubo descuentos en el histórico; el caso habla de introducirlos (F-134 no prueba ausencia).
- Limitación: No se infieren descuentos del tamaño de un salto del monto.
- En palabras de Hugo: “Qué data observable de pricing introductorio podemos sacar.”

**C-024 · Con cliente, mes y monto se ve qué cambió, no por qué**

Se ve cuánto cambió el monto pagado y en qué movimiento del puente, pero parte de ese movimiento es calendario de cobro. 25,3% del movimiento bruto sin altas vuelve exacto al nivel previo al mes siguiente, 29% del MRR de expansión se revierte al mes siguiente y 44% de los churn observados vuelve a pagar al mes siguiente. En la reactivación, 42,6% llega con un monto que cubre los meses del hueco más el corriente y 11,5% regresa al monto usual. En la contracción, solo 4,0% vuelve al nivel previo y 88,9% sigue igual o más abajo. Lo que no se ve es el porqué: suscripción, tarifa, descuento o cobro.

- Pregunta: ¿Qué se puede leer del monto pagado y qué no?
- Rol: diagnosis · confianza high · fuerza pending
- Evidencia: F-172, F-174, F-180, F-182, F-184, F-185, F-135, F-136, F-186, F-213 · Tablas: T-074, T-076, T-082, T-086, T-087
- Intención visual: Ruido contra señal: una parte del movimiento del puente se deshace al mes siguiente; la reactivación la concentra y la contracción no.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: F-131 salió de este claim: su lectura de la contracción choca con F-184 (X-100). Aquí se usa F-184 y la tensión queda abierta.
- Limitación: El reparto exacto de un pago entre los meses que cubre no se puede medir; solo se acota (F-186).
- Limitación: Las etiquetas del puente describen el monto pagado, no altas, bajas ni expansiones contractuales.
- En palabras de Hugo: “Qué data observable de pricing introductorio podemos sacar.”

**C-016 · Con solo el monto pagado, cada ejemplo del CFO admite lecturas distintas**

Con cliente, mes y monto, pasar de 100 a 80 puede ser una suscripción más chica, un descuento o un cobro que cambió de mes. Seguir en 100 con la suscripción en 130 no se distingue de «sin cambio», y el fin del descuento se vería como expansión. En los datos pasa algo parecido: 25,3% del movimiento bruto sin altas vuelve exacto al nivel previo al mes siguiente, 29% del MRR de expansión se revierte, 32% de los retornos tras meses sin pago liquida exactamente los meses pendientes y hay 260 eventos de ajuste con cobro retroactivo exacto. El monto no trae lista, descuento, crédito ni pausa.

- Pregunta: Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿se puede leer cada caso con el monto pagado?
- Rol: evidence · confianza high · fuerza pending
- Evidencia: F-093, F-090, F-073, F-130, F-082, F-062, F-177 · Tablas: T-058, T-061, T-028, T-074
- Intención visual: Una observación, varias lecturas: el mismo monto pagado se abre en lecturas distintas que hoy no se pueden separar.
- Limitación: Pendiente de tu aceptación; F-130 tiene la fuente sin verificar.
- Limitación: Los casos del CFO son ejemplos del enunciado, no observaciones de Finora.
- Limitación: Es una prueba de observabilidad, no una lectura de lo que ocurrió.
- En palabras de Hugo: “Con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento).”

**C-017 · El descuento se registra como objeto propio, con origen, source y fecha de fin**

AS-IS: un solo monto por cliente y mes, con transacciones → cliente-mes en COP → movimientos del monto con banderas de expansión, contracción, churn y reactivación, monto usual y firmas de pago multimes. Responde cuánto pagó el cliente y cómo se movió el monto. No guarda lista, plan, contratado, descuento, origen, source ni la diferencia entre factura y pago, así que un descuento se vería igual que una contracción, un pago multimes o un mes sin cobro (44% de los churn observados vuelve a pagar al mes siguiente). TO-BE por bloques. Lista y contrato: price_list_version (precio por plan y frecuencia, con vigencia) y subscription_item_version (plan × cantidad × precio acordado, sin descuentos), que solo cambia con un subscription_change_event. Descuento: discount_grant, con tipo, valor, duración, vigencia pactada y real, alcance, apilamiento, motivo, aprobación y un solo origen (promoción, negociación, retención o partner). Atribución: campaign (con su rubro de S&M) → promotion (la oferta) → promo_code (código, link o QR, con medio, canal asignado, UTM y landing) → promo_redemption (el canje, ligado a la sesión), más acquisition_touch con el source observado de todo cliente, tenga o no descuento. Aplicación: discount_application (cuánto descontó cada grant en cada línea de factura y en qué orden). Medición: una foto de cierre por suscripción y mes con lista, contratado, descuento recurrente, neto, descuento único, facturado y cobrado. CASUÍSTICA → PUENTE (C-020). Promoción digital: código con UTM y landing, canje en la sesión y source del alta en acquisition_touch → «Descuento (inicio)» con origen promoción y, al vencer, «Descuento (fin)», nunca expansión. Promoción física: un código por pieza, evento o punto, o un QR con UTM → la misma línea, con origen promoción física, comparable con la digital en retención y MRR neto. Descuento negociado: grant ligado al deal y a su aprobación, con precio especial = lista + descuento → «Descuento» con origen negociación, no menor MRR de entrada. Retención: si el cliente acepta un descuento → «Descuento» con origen retención; si baja de plan → Contracción real. Partner: grant ligado al partner → «Descuento» con origen partner. Apilados: cada grant con su orden y su propia línea. Mes gratis: descuento total con bandera sin cobro, no churn. Pausa: estado de la suscripción, no descuento.

- Pregunta: ¿Cómo se registra un descuento según su origen (promoción digital con su source, promoción física, negociado, retención, partner o apilado) y cómo pega en el puente?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-233, F-234, F-235, F-236, F-237, F-150, F-152, F-153, F-154, F-174 · Tablas: T-076
- Intención visual: Trazabilidad: cada peso de descuento se sigue desde la oferta y su canal hasta su línea del puente, separado de lo contratado; lo digital y lo físico llegan al mismo objeto con distinto source.
- Limitación: Pendiente de tu aceptación: F-233 a F-237 y los demás findings citados están propuestos.
- Limitación: No afirmamos que hubo descuentos en el histórico: el diseño es hacia adelante. Los ejemplos de promociones de R-034 son ilustrativos, no datos de Finora.
- Limitación: No sabemos si Finora captura hoy el source en el alta de todos los clientes. Si no, el código de descuento se volvería la única atribución (H-073).
- Limitación: Sin la regla «precio especial = lista + descuento», los descuentos negociados, de partner o de retención quedarían como precio menor (H-074).
- Limitación: Los efectos comerciales del descuento (cohortes de menor valor, churn al vencer) son evidencia externa, no de Finora (F-154, H-049).
- En palabras de Hugo: “«C-017 lo mismo quiero ver un modelo de datos y considera mas casuisticas, un descuento podría provenir de una promocion tanto digital como fisica y si es digital hay que considerar el source tambiem»”

**C-018 · El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan**

Mecanismo Propuesto: el CFO declara la convención, porque no hay un estándar de mercado y la de C-020 se aparta del default de herramientas como ChartMogul · el MRR se reporta en dos capas, lista y neto, y el descuento es la diferencia: el revenue que dejamos de capturar, abierto por origen · las cohortes que entren con descuento se marcan y se comparan con cohortes sin descuento. Con descuentos, el MRR neto, el revenue reconocido y la caja se separan; cuál vista manda depende de si los contratos son mensuales cancelables o a plazo fijo. Implicaciones Multidisciplinarias: Finanzas fija la convención y el reconocimiento; Marketing y Ventas crean promociones, códigos y aprobaciones; Producto y Billing registran el descuento con su vigencia; Data arma la foto de cierre y el puente.

- Pregunta: ¿Cómo debería Finora introducir descuentos temporales sin perder el porqué del MRR?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-151, F-153, F-154, F-132, F-236 · Tablas: —
- Intención visual: Dos capas que se separan: el MRR de lista y el neto divergen por el descuento, y la caja se aparta de ambos.
- Limitación: Pendiente de tu aceptación; F-132 tiene la fuente sin verificar.
- Limitación: No sabemos si los contratos de Finora son mensuales cancelables o a plazo fijo.
- Limitación: La comparación de cohortes con y sin descuento necesita un grupo comparable; con datos observados es asociación (H-049).
- En palabras de Hugo: “Cómo debería Finora introducir descuentos temporales (Mecanismo Propuesto, Implicaciones Multidisciplinarias, preguntas del CFO contestadas con el modelo propuesto).”

**C-019 · La Propuesta de Modelo de datos separa el valor en una escalera con vigencias**

Por suscripción y mes, cada peldaño lleva su fuente y su vigencia: lista (price_list_version, precio por plan y frecuencia) → contratado (subscription_item_version: plan, cantidad y precio acordado, sin descuentos) → descuento recurrente (discount_grant) → MRR neto = contratado − descuento recurrente → facturado (línea de factura, con el descuento aplicado vía discount_application) → cobrado (pago asignado a la factura). Lo contratado solo cambia con un subscription_change_event. El MRR, de lista y neto, se clasifica sobre los primeros peldaños comparando fotos de cierre (subscription_month_snapshot); facturado y cobrado son caja y solo generan un «efecto de cobro», nunca movimientos de MRR. El monto pagado de hoy sigue como capa de «monto pagado observado» y se concilia contra lo cobrado.

- Pregunta: ¿Cómo separar el valor de la suscripción del precio efectivamente pagado?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-130, F-132, F-133, F-151, F-152, F-168, F-234, F-240 · Tablas: —
- Intención visual: Escalera: el valor baja peldaño a peldaño de la lista a lo cobrado, y cada diferencia tiene nombre y dueño.
- Limitación: Pendiente de tu aceptación; F-130, F-132 y F-133 tienen la fuente sin verificar.
- Limitación: El puente por capas no se puede construir con el histórico (F-168): mide hacia adelante.
- Limitación: Las reglas del modelo son decisiones por escribir antes de construir (F-241).
- En palabras de Hugo: “Propuesta de modelo de datos (campos, tablas, definiciones).”

**C-020 · Si la suscripción no cambia, inicio o fin de descuento va a «Descuento»**

Regla base: New, Expansión, Contracción, Churn y Reactivación se definen sobre el MRR contratado y el estado de la suscripción entre cierres de mes, nunca sobre el monto pagado. La línea «Descuento» se define sobre cambios en los términos de los descuentos y lleva su origen (promoción digital o física, negociación, retención o partner). Si la suscripción no cambia, el inicio de un descuento es «Descuento (inicio)», con signo negativo, y su fin es «Descuento (fin)», positivo: nunca Contracción ni Expansión. Si cambian las dos cosas el mismo mes, se aplica una regla secuencial: primero el efecto suscripción, con los términos de descuento del mes anterior; lo que resta es efecto descuento. Además: cambio de términos → «Descuento (cambio)»; descuento único → fuera del MRR, resta solo en lo facturado; mes gratis → «Descuento (inicio)» con bandera sin cobro, no churn; pausa → estado de suscripción, no descuento; downgrade de retención → Contracción; quien sale con descuento → Churn por su neto, sin «Descuento (fin)». Control: por suscripción y mes, la suma de líneas iguala el cambio del MRR neto.

- Pregunta: ¿Cómo clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-150, F-152, F-151, F-236, F-237 · Tablas: —
- Intención visual: Separación: el cambio del MRR neto se reparte entre la línea de suscripción y la línea de descuento, sin que una contamine a la otra.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Es una convención por declarar: ChartMogul, por defecto, manda el inicio y el fin a contracción y expansión (F-236).
- Limitación: Recurrente contra único, mes gratis y pausa son decisiones, no hechos.
- Limitación: F-131 salió del claim: su lectura de la contracción choca con F-184 (X-100).
- En palabras de Hugo: “Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales (probablemente lo integra la misma propuesta de modelo de datos).”

**C-025 · Con el modelo propuesto, cada caso del CFO se lee en su capa**

Con el modelo (C-019, C-020), los ejemplos del enunciado se separan. De 100 a 80: si bajó lo contratado, es Contracción; si lo contratado sigue en 100 y empezó un descuento, es «Descuento (inicio)»; si solo cambió el mes del cobro, es efecto de cobro, fuera del MRR. De 100 a 130 con descuento de 30: Expansión por el paso de 100 a 130 y «Descuento (inicio)» por 30, con el neto en 100. Cuando desaparece el descuento: «Descuento (fin)» por 30, no Expansión. Hoy, con el monto pagado, el segundo caso se vería «sin cambio» y el tercero como expansión, y el puente ya mezcla cobro: 29% del MRR de expansión se revierte al mes siguiente y 44% de los churn observados vuelve a pagar al mes siguiente. Para Q-026, hacia adelante: MRR de lista (negocio subyacente) − MRR neto = revenue que dejamos de capturar, por origen. Hoy el −38% por cliente activo no se puede repartir entre lista y descuento.

- Pregunta: Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿cómo se lee cada caso con el modelo propuesto?
- Rol: implication · confianza medium · fuerza pending
- Evidencia: F-168, F-172, F-174, F-177, F-178, F-150, F-151 · Tablas: T-074, T-076, T-080
- Intención visual: Cada caso en su capa: el mismo monto pagado se descompone en suscripción, descuento y cobro, y se ve qué línea se mueve en cada ejemplo.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Los casos son ejemplos del enunciado, no observaciones de Finora.
- Limitación: No damos una cifra histórica de revenue no capturado: el histórico no trae tarifas ni descuentos.
- Limitación: La lectura depende de la convención que declare el CFO (C-018).
- En palabras de Hugo: “Preguntas del CFO contestadas con el modelo propuesto.”

## Recomendaciones
- Revisa y acepta o rechaza los findings que sostienen el paquete. Empieza por los de las láminas que cambiaste: R-031 (C-021, C-006), R-032 (C-023), R-033 (C-013) y R-034 (C-017), y F-072 y F-214, de las gráficas que elegiste. _(si Sin findings aceptados el paquete no puede marcarse Ready.)_
- Decidir D-018 (leer D-007 como «no construir en esta etapa») para que los diseños de métricas, del modelo de datos y de descuentos entren a la historia como propuesta. _(si Mientras D-007 siga activa con su redacción actual, esos claims chocan con ella.)_
- Decidir si el árbol de C-023 reemplaza las tres ramas de D-001. Recomiendo adoptarlo con una decisión nueva que referencie D-001: conserva cantidad, mezcla y tiempo dentro de sus niveles (validez, mezcla, desfase) y evita que una causa caiga en dos ramas (X-150). _(si Si adoptas el árbol por identidad.)_
- Pedir a Finora el export del CRM (leads y oportunidades con fecha de creación, historial de etapas con fecha, dueño, origen y actividades) y confirmar sus etapas literales, si existe la compra self-serve sin persona (Q-046) y si hay referidos o partners. _(si Para confirmar C-021 y poder calcular C-006 y el árbol de C-023.)_
- Acordar con Finora los parámetros del funnel: qué cuenta como intervención de persona (Q-063), la ventana W, el umbral de estancamiento por etapa (Q-064) y el hito de adquisición (Won o primer pago). _(si Antes de calcular tasas o construir funnel_entry: son parámetros de Finora, no estándares de mercado.)_
- Alinear R-033 con C-005. Recomiendo quedarse con las rutas de C-005 (Executive, Self Service, Hybrid A y B, con Reactivate como loop) y ajustar puerta y ruta en funnel_entry. _(si Antes de construir el modelo de datos del funnel.)_
- Correr el árbol en orden con los datos del CRM: primero Paso 0 y validez; solo si la brecha sigue con entradas válidas, mezcla contra tasa; y para capacidad (H-006), experimentos naturales o un piloto de SLA antes de leer la asociación como efecto. _(si Si el export del CRM trae fechas de creación, etapas y actividades.)_
- Que el CFO declare la convención del descuento: dos capas (lista y neto), inicio y fin a la línea «Descuento» con su origen, descuento único fuera del MRR, y mes gratis y pausa como casos propios. _(si Si Finora va a introducir descuentos temporales.)_
- Capturar desde ya el source (UTM, landing, referrer) en el alta de todos los clientes, usar un código por pieza en promociones físicas y aplicar la regla «precio especial = lista + descuento». _(si Si Finora lanza promociones o descuentos negociados antes de tener el modelo completo: lo que no se capture no se reconstruye (F-242, H-073, H-074).)_
- Pedir la unidad y la escala del archivo de S&M, su asignación por canal y campaña, y si Software Tools y Freelance son Habilitación o producto. _(si Para pasar del proxy «S&M por alta en u» a CAC y costo por Won por canal.)_
- Fijar una sola cifra de churn observado 2024 (2,04% con ventana ene–jul o 1,9%) y una base de comparación del monto por cliente (ene-22 o dic-22). _(si Antes de publicar C-002, C-007 y C-009.)_

## Apéndice candidato
- Mapa completo de etapas por ruta y canal, con variantes y dueños — C-021 muestra la versión ejecutiva; las variantes (saltos, regla laxa o estricta de Q-063) van al anexo.
- Catálogo de métricas con fórmula, grano, hito y estado de hoy — C-006 y C-009 dan la definición; el detalle de las métricas y sus eventos no cabe en la lámina.
- Modelo de datos del funnel: entidades, llaves, reglas y ejemplos — Sostiene C-013; los ejemplos de R-033 son ilustrativos salvo los IDs legados.
- Modelo de precios y descuentos: entidades, reglas de clasificación y ejemplos ilustrativos — Sostiene C-017, C-019 y C-020; los ejemplos de promociones no son datos de Finora.
- Árbol MECE completo: qué valida, qué descarta y dato mínimo por hoja — C-023 da la estructura; la tabla hoja por hoja es de consulta.
- Calidad del archivo de S&M — La unidad sin documentar, Team fijo hasta may-23, PayrollExpenses negativo y el corte de Freelance condicionan C-004 y C-010.
- Momento de cobro en el puente — Detalle de reactivación y contracción por firma de cobro que respalda C-024.

## Preguntas sin resolver
- S2.1: ¿qué relaciones comentaste que debe mostrar la lámina? Sigue sin contenido.
- Q-063: ¿qué cuenta como intervención de persona? Define la frontera entre Executive inbound e Hybrid A, y la variante de Hybrid B.
- Q-064: ¿cuál es el umbral de estancamiento por etapa y cuándo caduca un episodio?
- Q-046: ¿existe compra self-serve sin persona? ¿Hay prueba gratis, freemium o pago al registrarse?
- ¿El hito de adquisición del CRO es Won, primer pago o suscripción activa?
- ¿Existen referidos o partners como canal? ¿Quién es dueño de Self Service?
- ¿Reactivate es puerta (R-033) o loop (R-031)? Hay que alinearlo antes de construir.
- ¿El árbol de C-023 reemplaza las tres ramas de D-001? (X-150)
- ¿Finora captura hoy el source (UTM, landing) en el alta de todos los clientes? (H-073)
- ¿Cuál es la unidad del gasto de S&M? ¿Software Tools y Freelance son Habilitación o producto? (Q-022)
- ¿Los contratos de Finora son mensuales cancelables o a plazo fijo? Define qué vista manda: MRR neto, revenue o caja.
- ¿Qué base de comparación usamos para el monto por cliente: ene-22 o dic-22? (X-060)
- ¿Qué cifra de churn observado 2024 usamos: 2,04% o 1,9%? (X-101)
- D-018 contra D-007: ¿entran los diseños a la historia como propuesta?

## Validación
- ✖ C-016: cifra(s) sin tabla que las respalde: 32%, 260.
- ⚠ C-011: lenguaje causal («porque») — la evidencia es observacional.
- ⚠ Láminas del guion sin evidencia todavía: S2.1 (van a research, no se rellenan).
