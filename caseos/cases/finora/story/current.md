# CURRENT STORY — v1
> Generado 2026-09-29T11:54 · con problemas de validación

## Audiencia
CEO — contexto de salud general del modelo (Overview) antes de Growth y Revenue; qué decide no está definido, CRO — cómo definir, medir y operar el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos, CFO — cómo introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»

## Objetivo
BORRADOR para que Hugo vea la historia completa siguiendo su guion (Overview → Growth → Revenue) antes de revisar la evidencia. Ante el CEO, el CRO y el CFO se muestran tres cosas: qué explicaciones se pueden defender con los pagos y el gasto (la brecha se asocia a quién entra), qué huecos hay en su WoW (el lado izquierdo del funnel, las causas ToFu/BoFu, la tarifa y el descuento) y qué modelos se proponen para decidir mejor. No hay findings aceptados: todo queda pendiente de la aceptación de Hugo y el paquete no puede marcarse Ready.

## De → A
- **Hoy creen:** Finora suma clientes mucho más rápido que monto pagado y esa brecha se lee con explicaciones que los pagos no pueden confirmar: «más leads que no convierten» y «cambios de suscripción o descuentos».
- **Deben salir creyendo:** La brecha se asocia a quién entra: más primeros pagadores, con menor ticket y en todas las industrias. No se asocia a la base previa ni a más salidas persistentes. El porqué, tanto el del CRO como el del CFO, no está en los datos del caso. Hay modelos concretos para poder decidirlo: bowtie por puerta, árbol de métricas con semáforo, descuento como objeto propio y Propuesta de Modelo de datos.

## Governing thought
> La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos: proponemos medir por puerta y separar descuento de suscripción.

## Preguntas ejecutivas
- Q-003 (CEO) ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?
- Q-001 (CRO) ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- Q-002 (CFO) ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?

## Arco
SCR con pilares, siguiendo el guion aprobado de Hugo (Overview → Growth → Revenue) — Primero la respuesta, bloque por bloque. Overview: la brecha 4,5× vs 2,8× y el −38% por cliente activo se asocian a la composición de quién entra, no a la base previa; esa brecha abre las dos preguntas. Growth: lo que sí vemos (más primeros pagadores con menor ticket en todas las industrias, y un gasto que no se mueve con ellos) → lo que no vemos (el funnel por puerta y las causas ToFu/BoFu, cada una con el dato que la decidiría) → cómo medirlo y operarlo (semáforo de métricas, fuentes comunes, foros). Revenue: qué se observa del pricing de entrada y por qué el monto no separa suscripción de descuento → mecanismo de descuentos temporales → Propuesta de Modelo de datos → regla de clasificación. Cada bloque cierra con una propuesta porque los pagos llegan hasta «qué cambió» y no hasta «por qué».

### S1 · Overview
_Situación: Finora suma clientes mucho más rápido que monto pagado. El −38% por cliente activo se asocia a la composición de quién entra; la base previa sostiene su monto. Esa brecha abre Growth y Revenue._

**C-001 · Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8×**

Entre ene-22 y oct-24, los clientes con pago en el mes pasan de 377 a 1.678 (4,5×) y el MRR pagado observado, de COP 35,0 millones a COP 97,0 millones (2,8×). En consecuencia, el MRR pagado observado por cliente activo baja de COP 92,8 mil a COP 57,8 mil (−38%). Esa brecha abre Growth (quién entra) y Revenue (qué se paga y por qué cambia).

- Pregunta: ¿Qué tan sano está el modelo si suma clientes mucho más rápido que monto pagado?
- Rol: context · confianza high · fuerza pending
- Evidencia: F-071, F-072, F-001, F-002, F-074 · Tablas: T-026, T-027, T-001
- Intención visual: Diverge: clientes activos y MRR pagado observado parten de la misma base y se separan; el monto por cliente cae en espejo.
- Limitación: Pendiente de tu aceptación: F-071, F-072, F-001, F-002 y F-074 están propuestos.
- Limitación: Es monto pagado observado (campo amount con escala fija), no MRR contratado: la recurrencia no está confirmada (F-082).
- Limitación: Cliente activo = pago mayor que cero en el mes. Un cliente sin pago puede estar cancelado, pausado o en atraso (F-082).
- Limitación: Son métricas de stock con ventana completa desde ene-22; las de flujo arrancan en mar-22 (F-074).
- Limitación: El −38% no se presenta como deterioro de la salud del negocio: no separa la mezcla de quienes entran, el precio ni las salidas.
- En palabras de Hugo: “Finora suma clientes mucho más rápido que monto pagado (4,5× vs 2,8×; ~−38% por cliente activo). Esa brecha abre Growth y Revenue.”

**C-002 · La caída por cliente se asocia a quién entra; la base previa sostiene su monto**

Entre ene-22 y oct-24, la descomposición por cosecha asigna a la composición de la base 108% del cambio del MRR pagado observado por cliente activo, y −8% al efecto dentro de las cosechas; con base dic-22, a la composición le asigna 84%. Los clientes activos en ene-22 pasan de COP 92,8 mil a COP 97,4 mil por cliente (+5%). En cambio, las cosechas 2023 y 2024 ya son 65% de los activos y 50% del MRR en oct-24, con COP 46,3 mil y COP 43,0 mil por cliente.

- Pregunta: ¿El −38% por cliente viene de la base que ya teníamos o de quién entra?
- Rol: diagnosis · confianza high · fuerza pending
- Evidencia: F-075, F-076, F-056, F-058, F-097, F-019 · Tablas: T-030, T-031, T-041, T-027
- Intención visual: Mezcla que arrastra: la base previa se sostiene mientras las cosechas nuevas, de menor monto por cliente, ganan peso y bajan el promedio.
- Limitación: Pendiente de tu aceptación: F-075, F-076, F-056, F-058, F-097 y F-019 están propuestos.
- Limitación: Composición ≠ causa: no separa si las cosechas nuevas pagan menos por tipo de cliente, plan, tarifa o descuento; el panel no trae esas tablas (F-062).
- Limitación: La magnitud depende de la base (108% con ene-22, 84% con dic-22); la dirección se mantiene.
- Limitación: «Quién entra» describe primeros pagadores observados, no la calidad de los leads: H-005 no se evalúa con pagos.
- Limitación: La salida de pocas cuentas grandes también baja el promedio (F-101, F-102) y aquí no está separada.
- En palabras de Hugo: “Observaciones generales y salud del negocio: el −38% por cliente activo se asocia a la mezcla de quienes entran; la base previa no pierde monto por cliente.”

### S2 · Growth
_Lo que sí vemos: primeros pagadores, ticket, industria y gasto de S&M por categoría, sin atribuir ventas al gasto. Lo que no vemos: el funnel por puerta (Assisted, Self Service, Executive) y las hipótesis ToFu/BoFu, cada una con su dato. Cómo operarlo: primero definiciones y fuentes comunes, después foros. Sigue tu orden S2.1–S2.7; S2.1 queda sin contenido._

**C-003 · Entran más primeros pagadores, con menor ticket, en las 6 industrias**

Los primeros pagadores observados pasan de 27,2 por mes en 2022 (mar–dic) a 54,7 desde ene-23. Es un escalón a inicios de 2023, sin tendencia distinguible después (pendiente +0,47 por mes; intervalo de 95% de −0,40 a +1,33). El valor que traen crece menos: entre 2022 y 2024 los primeros pagadores por mes suben +104%, mientras el valor inicial incorporado por mes sube +6% (run-rate temprano) o +17% (monto habitual); la mediana del primer pago pasa de COP 63,0 mil en 2022 a COP 36,8 mil en 2023 y COP 42,0 mil en 2024. Pasa en las 6 industrias: 97% del cambio del ticket ocurre dentro de cada industria, no por mezcla.

- Pregunta: ¿Qué cambió en quién entra y en qué industrias?
- Rol: evidence · confianza high · fuerza pending
- Evidencia: F-110, F-039, F-077, F-113, F-045, F-037, F-112, F-043, F-053, F-114, F-100, F-030, F-078 · Tablas: T-016, T-019, T-018, T-020, T-044, T-033
- Intención visual: Outgrow: el conteo de primeros pagadores sube en escalón y se aplana, mientras el valor inicial que traen crece mucho menos. Volumen y valor se desacoplan.
- Limitación: Pendiente de tu aceptación: F-110, F-113, F-112, F-114, F-100, F-030 y los demás citados están propuestos (F-039, confianza media).
- Limitación: Primer pago observado ≠ adquisición: no es Won ni suscripción activa. El hito lo acuerda el CRO.
- Limitación: El escalón de inicios de 2023 puede ser en parte un efecto de registro (H-024) o un cambio operativo (H-025): sin confirmar.
- Limitación: Con la ventana mar–oct igualada el cambio se mantiene (F-043). La magnitud depende de la medida (F-046); por F-139, el ticket de entrada debería medirse con un monto estabilizado.
- Limitación: Entre 2023 y 2024 el ticket no siguió bajando (T-033). Eso concilia R-003 con R-010 (H-030, X-018).
- Limitación: Si las entradas del CRO siguieron creciendo después de ene-23, la meseta sería el tramo de «más leads, no más ventas». Las entradas no están en los datos (Q-001).
- Limitación: La industria es la única segmentación disponible: no sustituye al canal ni a la motion.
- En palabras de Hugo: “Revisar entradas y actividad económica de clientes y segmentos.”

**C-004 · Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas**

En 2023 jun–dic hay 60,6 primeros pagadores por mes, frente a 45,2 en ene–may. En esos mismos tramos, la Generación de Demanda (ToFu) baja de 1,73 u a 0,82 u por mes y el S&M total de 3,01 u a 1,44 u. La correlación en niveles entre el S&M total y los primeros pagadores del mismo mes es −0,57; en cambios mes a mes, el mayor valor absoluto es 0,27 (p mínimo 0,14): no aparece una relación positiva que leer. El archivo viene en unidades reportadas (u), sin escala a COP, y hasta may-23 Team es un 12% fijo del total durante 17 meses, como una asignación de arriba hacia abajo.

- Pregunta: ¿Hasta dónde se puede relacionar la Inversión en Marketing por categoría con las ventas cruzando fechas?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-107, F-118, F-023, F-024, F-063, F-066, F-115, F-065, F-068, F-119 · Tablas: T-013, T-024, T-008, T-005, T-009
- Intención visual: Divergencia sin causa: en 2023 el gasto por categoría baja mientras los primeros pagadores suben. Coinciden en fechas; ninguno mueve al otro.
- Limitación: Pendiente de tu aceptación: F-107, F-118, F-063, F-066 y los demás citados están propuestos (la mayoría, de confianza media).
- Limitación: Coincidir en fechas no es causa: no hay etapas del funnel con fechas ni fuente del lead que liguen el gasto de un mes con clientes concretos (F-119).
- Limitación: La unidad no está documentada: no se lee como COP ni se combina con el monto pagado (X-001).
- Limitación: PayrollExpenses es negativo en 5 meses y Freelance queda en cero desde mediados de 2023: el valle puede ser en parte contable (H-023). F-117 fecha ese cero en may-23 y T-009 marca jun-23 como último mes con valor: hay que reconciliarlo.
- Limitación: La columna «capacidad_por_mes» de T-013 es gasto de Team, no capacidad de SDR/AE (X-014): conviene renombrarla antes de mostrarla.
- Limitación: No se puede decidir con estos datos si SoftwareTools/Freelance son Habilitación o producto (F-068).
- En palabras de Hugo: “Inversión de S&M por categoría (Generación de Demanda ToFu: Paid Media y publicidad no web · Team: Payroll Expenses y Travel · Habilitación, ¿producto?: Software Tools y Freelance) y hasta dónde se puede relacionar con ventas cruzando fechas.”

**C-005 · Proponemos un bowtie por puertas: Self Service, Assisted y Executive con nudo común**

No es un funnel único: cada puerta tiene sus hitos a la izquierda. Self Service: visita por canal → registro → activación → primer pago. Assisted: entrada (pide ayuda, PQL derivado de Self Service u outbound que responde) → SQL → oportunidad → primer pago. Executive: cuenta objetivo → oportunidad directa, sin MQL → sponsor o business case → primer pago. Todas llegan a un nudo común y a un lado derecho común (retención, expansión, NRR), cortadas por Canal de adquisición (p. ej. Digital, WoM, outbound); la reactivación va aparte como otro tipo de entrada y AAARRR sirve como vocabulario común, no como secuencia.

- Pregunta: ¿Cómo definir y medir el funnel si no todos lo recorren igual?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-140, F-147, F-142, F-143 · Tablas: —
- Intención visual: Convergencia: caminos de entrada distintos, con hitos propios, que se juntan en un nudo y comparten el lado derecho.
- Limitación: Propuesta de especialista (R-016, R-019), pendiente de tu aceptación. F-140 y F-147 son de confianza media.
- Limitación: Los datos del caso no traen puerta, canal ni etapas, así que el lado izquierdo no se puede medir hoy (F-142, fuente sin verificar). Eso no prueba que Finora no los registre.
- Limitación: El hito del nudo (Won, primer pago o suscripción activa) está por acordar con el CRO.
- Limitación: La puerta no se infiere de los pagos y el primer pago no sirve como valor de entrada (F-143).
- En palabras de Hugo: “Cómo definir y medir el funnel si no todos lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas): Assisted / Self Service / Executive, con canales (incl. digital, WoM, clientes que no requirieron KAM).”

**C-006 · Proponemos medir conversión por cohorte de entrada y ventana fija, por puerta y canal**

La tasa es «% de las entradas del mes que pagan dentro de W días», por puerta y Canal de adquisición, calculada solo en las cohortes que ya cumplieron la ventana. La tasa de período y el promedio de solo los que convirtieron castigan a las entradas recientes y confunden «compran más tarde» con «compran menos», que es justo lo que hay que separar en la premisa del CRO (H-003, H-004). Para medirla hay que instrumentar en origen: fechas por etapa en el CRM, puerta y canal por cuenta, y gasto por canal.

- Pregunta: ¿Qué conversion rate usar si hay entradas recientes y leads que se estancan semanas?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-141, F-144 · Tablas: —
- Intención visual: Maduración: cada cohorte de entrada se compara solo cuando cumplió su ventana; las recientes todavía no son comparables.
- Limitación: Propuesta de especialista (R-016), pendiente de tu aceptación.
- Limitación: W y el umbral de «estancado» son parámetros a acordar con Finora, no estándares de mercado.
- Limitación: Con los datos del caso no se calcula ninguna conversión: los pagos no incluyen a quien no compró.
- Limitación: La atribución por canal reparte crédito; no prueba causa (F-144).
- En palabras de Hugo: “Funnel propuesto, AAARRR, conversion rate y métricas clave.”

**C-007 · La pérdida se concentra en cosechas de menor ticket, no en una industria**

Entre dic-22 y oct-24, el MRR pagado observado por cliente activo cambia −COP 31,7 mil (−35%): la descomposición asigna −COP 26,6 mil (84%) a la composición de cosechas y −COP 5,2 mil al efecto dentro de las cosechas. Bajó en las 6 industrias, más en Servicios profesionales (−46,6%), Restaurantes (−45,6%) y Retail (−43,1%) que en Producción (−18,8%), Tecnología (−15,5%) y Salud (−14,4%). La salida persistente no sube: el churn que no vuelve a pagar en un trimestre es 0,98% en 2022, 1,09% en 2023 y 0,96% en 2024.

- Pregunta: ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento?
- Rol: diagnosis · confianza high · fuerza pending
- Evidencia: F-097, F-092, F-096, F-094, F-020, F-059, F-033, F-079, F-101, F-102 · Tablas: T-041, T-040, T-038, T-002
- Intención visual: Partición: el cambio del monto por cliente se parte en composición de cosechas vs efecto dentro; las 6 industrias caen a la vez, con distinta intensidad.
- Limitación: Pendiente de tu aceptación: F-097, F-092, F-096, F-094, F-033 y F-079 están propuestos (F-094, confianza media).
- Limitación: La industria es la única segmentación: no hay tamaño de cliente, canal, precio, descuento ni motivo de churn (F-106). No se fabrican segmentos por clustering.
- Limitación: Churn persistente = no vuelve a pagar en un trimestre. Es un proxy con ventana de gracia, no retención contractual.
- Limitación: Quienes se van pagaban más en promedio, pero no en mediana: pesan pocas cuentas grandes (F-101, F-102).
- Limitación: Medido contra su propio primer pago, el nivel a M6 de las cohortes queda en un rango estrecho: la diferencia está en el punto de partida (R-006).
- En palabras de Hugo: “Dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix).”

**C-008 · Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar**

En 2024, Salud tiene el menor churn persistente (0,56 puntos porcentuales mensuales), el mayor ticket de entrada mediano (COP 52,5 mil, igual que Restaurantes) y 124 clientes activos en oct-24, frente a 459 en Restaurantes y 360 en Retail. En el otro extremo, Retail combina el mayor churn persistente (1,33) con el menor ticket mediano (COP 26,2 mil). Salud y Tecnología también muestran las menores caídas del MRR pagado observado por cliente activo entre dic-22 y oct-24 (−14,4% y −15,5%).

- Pregunta: ¿Hay industrias de bajo churn, ticket alto y poco volumen?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-104, F-099, F-103, F-105 · Tablas: T-048, T-049, T-047
- Intención visual: Trade-off: churn persistente vs ticket mediano, con el volumen como peso. Salud se aísla con buen perfil y poco volumen.
- Limitación: Pendiente de tu aceptación: F-104, F-099, F-103 y F-105 están propuestos, de confianza media.
- Limitación: Es una señal, no un segmento prioritario: poco volumen, un solo año, y el churn persistente de 2024 necesita un trimestre de seguimiento (hay que confirmar qué meses entran).
- Limitación: Benchmark ≠ recomendación: sin CAC ni margen por industria no se puede decir dónde conviene crecer.
- Limitación: F-052 (churn observado 2024: mínimo en Producción, máximo en Tecnología) no coincide con T-047 (mínimo en Restaurantes): hay que reconciliarlo antes de mostrar el churn observado por industria.
- Limitación: La industria no sustituye al canal ni a la motion.
- En palabras de Hugo: “Quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco volumen.”

**C-009 · Proponemos un árbol de ingreso recurrente con semáforo: qué se mide hoy y qué no**

En verde, con nombre honesto: MRR pagado observado y su puente, clientes activos, ARPA por cliente (lo que se pide como ARPU; no hay datos por usuario), churn observado junto a uno con ventana de gracia, NRR/GRR de la base y métricas por cohorte; el ARR, solo como run-rate anualizado. El churn muestra por qué importa el nombre: el observado baja de 3,52% en 2022 a 2,04% en 2024, mientras el que no vuelve a pagar en un trimestre pasa de 0,98% a 0,96%. En rojo, porque piden datos nuevos: CAC en COP y por motion o canal, payback, LTV con margen, LTV:CAC y UCM. Hoy solo cabe un «LTV empírico de ingreso» por cohorte, a horizonte fijo.

- Pregunta: ¿Qué métricas propondrías que hoy no existen y cuáles se pueden calcular ya?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-135, F-136, F-139, F-033, F-137, F-138 · Tablas: T-002, T-034
- Intención visual: Jerarquía: del resultado (MRR) a los drivers y la economía unitaria, con cada métrica marcada según qué tan medible es hoy.
- Limitación: Propuesta de especialista (R-018), pendiente de tu aceptación. F-137 y F-138 vienen de fuente sin verificar.
- Limitación: Churn observado 2024: T-002 da 2,04% y T-034, 1,9%. Hay que reconciliar la ventana o el denominador antes de mostrarlo.
- Limitación: NRR/GRR y retención se calculan sobre pagos observados, no son retención contractual.
- Limitación: Antes de llamar churn o MRR a lo observado hacen falta una regla de normalización y una ventana de gracia: los atrasos y los pagos multimes inflan churn, reactivación y expansión (F-136).
- Limitación: El ARPA de entrada se mide con monto estabilizado (segundo pago o monto usual), no con el primer pago (F-139).
- Limitación: D-007 (activa) dejó las métricas definitivas fuera de etapa: esto es una propuesta.
- En palabras de Hugo: “Qué métricas propondrías que hoy no existen (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) y cómo medirlas, robustecerlo y bajar lo que tenga sentido.”

**C-010 · Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC**

El S&M total por primer pagador observado pasa de 0,105 u en 2022 a 0,036 u en 2024 (−66%), en una unidad sin escala a COP. Su nivel depende de si SoftwareTools y Freelance cuentan como Habilitación comercial: sin ellos, queda en 0,093 u y 0,034 u. Leerlo como CAC o como mejora de eficiencia es prematuro: el gasto no se liga a clientes concretos y el denominador cuenta primeros pagos, no adquisiciones acordadas.

- Pregunta: ¿Tenemos hoy un CAC que podamos usar?
- Rol: limitation · confianza medium · fuerza pending
- Evidencia: F-081, F-108, F-069, F-070, F-022, F-137 · Tablas: T-036, T-011
- Intención visual: Advertencia: una cifra que cae pero no significa lo que parece (unidad sin escala, no es CAC).
- Limitación: Pendiente de tu aceptación: F-081, F-108, F-069, F-070 y F-022 están propuestos.
- Limitación: Sin unidad documentada no hay CAC en COP, payback ni LTV:CAC. Sin motion ni canal no hay CAC por Self Service/Assisted/Executive ni por Digital/KAM (F-137, fuente sin verificar).
- Limitación: El numerador puede tener efectos contables: Team fijo hasta may-23 y PayrollExpenses negativo (H-023, X-015).
- Limitación: No leer la caída como mejora de eficiencia (X-005).
- En palabras de Hugo: “CAC (de la lista MRR, ARR, ARPU, CAC, LTV, Churn, UCM): hoy solo existe como gasto de S&M por alta, en unidades sin escala.”

**C-011 · Proponemos descartar primero artefactos de medición y después contrastar causas ToFu y BoFu**

Antes de las causas, la premisa: con pagos, «no más ventas» se sostiene en jul–oct del último año frente al anterior, pero no en mar–oct, así que depende de la ventana. El árbol separa los artefactos —conteo, es decir, si la demanda creció de verdad (H-001); mezcla (H-002); y tiempo de exposición (H-003 y la parte de H-004 en que compran más tarde y terminan igual)— de las explicaciones a contrastar: calidad al entrar (H-005, ToFu), atención y capacidad (H-006), el tramo post-SQL (H-007, BoFu) y la oferta, es decir producto, precio o condiciones (H-008, BoFu). Las entradas únicas con fecha (con canal, motion y segmento) y su vínculo con el pago bastan para distinguir H-001 a H-004. H-005 a H-007 necesitan datos que suelen estar en un CRM, aunque no siempre con su historia, y H-008 pide más que las razones de pérdida.

- Pregunta: ¿Qué podría explicar «más leads, pero no más ventas» y qué dato validaría o descartaría cada explicación?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-125, F-126, F-127, F-128, F-129 · Tablas: —
- Intención visual: Descarte por eliminación: primero se podan los artefactos; lo que queda son causas, cada una con el dato que la decide.
- Limitación: Propuesta de especialista (R-010), pendiente de tu aceptación. F-126 viene de fuente sin verificar y F-129 es de confianza baja.
- Limitación: Con los datos del caso no se valida ni se descarta ninguna de H-001 a H-008: no hay entradas ni vínculo lead→pago.
- Limitación: H-004 no es toda artefacto: solo lo es «compran más tarde y terminan igual». «Compran menos aun con seguimiento comparable» es una diferencia real (X-017).
- Limitación: La caída del último tramo puede ser en parte un efecto de borde o de rezago de los pagos (H-029).
- Limitación: Calidad, atención, post-SQL y oferta son explicaciones a contrastar, no causas confirmadas (D-003).
- En palabras de Hugo: “Definir qué hipótesis ToFu y BoFu (demanda, calidad, velocidad de atención, conversión post-SQL) podrían estar afectando su motor y qué datos validarían o descartarían cada una; aquí no hay research en data, es una propuesta.”

**C-012 · Capacidad y calidad se separan comparando mezcla contra tasa por grupo de entrada**

Si empeora la mezcla de ajuste al entrar, apunta a calidad (H-005); si cae la tasa dentro de cada banda de ajuste, sobre todo en entradas atendidas lento y en semanas de alta carga, apunta a capacidad (H-006). El dato mínimo es una tabla de entradas con el ajuste congelado al entrar, la fecha del primer contacto humano y la compra en ventana fija, más un roster semanal de SDR/AE que distinga el ramp. H-028 plantea que ambas pueden operar a la vez (con más volumen, los equipos dejarían sin trabajar primero las entradas que perciben peores), así que la comparación se hace por grupo de entrada, entre un periodo base y el periodo de caída.

- Pregunta: ¿La capacidad comercial no alcanza la demanda generada, o bajó la calidad de la máquina de leads?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-121, F-122, F-124, F-120 · Tablas: —
- Intención visual: Partición: el cambio de compra se parte en mezcla de ajuste (calidad) vs tasa dentro de banda (capacidad), con la carga semanal como moderador.
- Limitación: Propuesta de especialista (R-014), pendiente de tu aceptación. F-120 viene de fuente sin verificar.
- Limitación: No se responde con los datos del caso: no hay entradas, grupo de entrada, SDR/AE ni tiempos de contacto.
- Limitación: El gasto de Team/Payroll no mide la capacidad de SDR/AE (X-011, X-014).
- Limitación: Self Service como grupo de control (F-123, fuente sin verificar) solo vale si existía sin SDR/AE en ambos periodos (X-012). Por eso queda fuera del claim.
- Limitación: Las bandas de ajuste se validan en el periodo base antes de usarlas; los experimentos naturales van antes que uno aleatorio.
- En palabras de Hugo: “P. ej. la capacidad comercial instalada no alcanza la demanda generada, o la calidad de la máquina de leads bajó.”

**C-013 · Proponemos primero definiciones y fuentes comunes, unidas por un ID de cuenta**

La capa técnica: CRM con motion e historial de etapas; analítica digital que registre el Canal de adquisición desde la primera visita; y facturación con MRR contratado y estado de suscripción. Todo se une por un ID de cuenta en el modelo analítico que ya existe. La facturación va primero: el lado Revenue ya se puede operar mes a mes, pero con pagos observados el CRO confundiría el momento del cobro con churn y expansión. El lado Growth no está en los datos del caso: sin motion, canal ni fechas de hitos no hay conversión ni CAC por motion, y hoy solo se ve la mezcla de gasto.

- Pregunta: ¿Qué hace falta en la capa técnica para que el CRO opere el funnel de forma recurrente?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-145, F-146, F-144 · Tablas: —
- Intención visual: Convergencia: CRM, analítica digital y facturación se unen por un ID de cuenta en un modelo común.
- Limitación: Propuesta de especialista (R-019), pendiente de tu aceptación. F-146 viene de fuente sin verificar.
- Limitación: Que los datos del caso no traigan canal ni etapas no prueba que Finora no los registre: antes de «pulir CRM» hay que saber qué existe.
- Limitación: D-007 (activa) dejó la solución fuera de etapa: hay que confirmar si sigue aplicando.
- En palabras de Hugo: “Técnica: pulir CRM, analítica digital.”

**C-014 · Proponemos un tablero por foro atado a decisiones: semanal, mensual y trimestral**

La base es un bowtie por motion (Self Service, Assisted, Executive con KAM en la post-venta) que mide volumen, alcance y tiempo por hito. Cada foro tiene su decisión: el semanal decide oportunidades, el mensual la mezcla de motion y Canal de adquisición, y el trimestral la inversión y la capacidad. El análisis ad hoc se abre por hipótesis (H-001 a H-008). Los agentes de IA y la atribución van encima, no en la base: solo sobre métricas gobernadas y con un piloto controlado; para decidir presupuesto hacen falta experimentos.

- Pregunta: ¿Qué decisiones le permite tomar al CRO y en qué foro?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-147, F-148, F-149 · Tablas: —
- Intención visual: Cadencia → decisión: cada foro con su pregunta y su métrica; los agentes, como capa superior sobre métricas gobernadas.
- Limitación: Propuesta de especialista (R-019), pendiente de tu aceptación (confianza media).
- Limitación: Las decisiones del CRO por foro todavía no están definidas: la cadencia se ajusta cuando se acuerden.
- Limitación: Depende de la capa técnica (operar-fuentes) y del historial de etapas del CRM.
- Limitación: La atribución reparte crédito; no reemplaza a los experimentos.
- En palabras de Hugo: “Decision making: dashboards automatizados por foro, análisis ad hoc, agentes de IA.”

### S3 · Revenue
_Con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento). Proponemos cómo introducir descuentos temporales y una Propuesta de Modelo de datos que separe el valor de la suscripción del precio pagado, con su regla de clasificación._

**C-015 · Lo observable es el primer y segundo pago; el descuento no es verificable**

La mediana del primer pago observado es COP 63,0 mil en 2022, COP 36,8 mil en 2023 y COP 42,0 mil en 2024; la del segundo pago queda por debajo: COP 46,2 mil, COP 35,0 mil y COP 37,8 mil. El segundo pago coincide exacto con el primero en 73,5%, 90,3% y 77,3% de los primeros pagadores. El primero supera al segundo 1,5× o más en 23,2%, 7,1% y 11,6%, y lo inverso ocurre en 1,1%, 1,5% y 0,9%. Son datos de comportamiento del monto, no de descuento: sin catálogo de precios, ninguno se puede leer como precio introductorio.

- Pregunta: ¿Qué data observable de pricing introductorio podemos sacar?
- Rol: evidence · confianza medium · fuerza pending
- Evidencia: F-083, F-085, F-086, F-087, F-134 · Tablas: T-053, T-051, T-054, T-055
- Intención visual: Comparación: primer vs segundo pago por cohorte. La mayoría queda igual y pocos saltan hacia arriba.
- Limitación: Pendiente de tu aceptación: F-083, F-085, F-086 y F-087 están propuestos (de confianza media, salvo F-083).
- Limitación: Solo cohortes de ventana limpia: las altas de feb-22 quedan fuera por su firma de pago atípica (F-026).
- Limitación: El primer pago puede incluir prorrateos, pagos multimes o ajustes: no es precio de lista (F-093).
- Limitación: Sin catálogo de precios, planes ni descuentos, el menor ticket no se asocia a lista, plan, empaquetamiento o descuento (F-062).
- Limitación: F-134 (confianza baja): la huella de un descuento temporal limpio es rara en el histórico. Es consistente con que los descuentos sean algo por introducir, pero no prueba que no existieran.
- En palabras de Hugo: “Qué data observable de pricing introductorio podemos sacar.”

**C-016 · Con solo el monto pagado, cada ejemplo del CFO admite lecturas distintas**

El dato es cliente × mes × monto pagado: en los ejemplos construidos del CFO, un cambio de suscripción y un descuento dan exactamente el mismo monto, y no hay catálogo de precios, descuentos, créditos ni pausas. Además, el monto es consistente con cobro más que con contrato: 25,3% del movimiento bruto sin primeros pagadores (COP 282,8 millones entre mar-22 y sep-24) vuelve exacto al nivel previo al mes siguiente. Es una prueba de lo que se puede distinguir, no una lectura de lo que pasó.

- Pregunta: ¿Por qué con los datos actuales no se puede contestar cuánto cambió el MRR por suscripción, tarifa o descuento?
- Rol: diagnosis · confianza high · fuerza pending
- Evidencia: F-093, F-090, F-073, F-130, F-082, F-062 · Tablas: T-058, T-061, T-028
- Intención visual: Mismo resultado, causas distintas: historias diferentes (cambia la suscripción vs empieza un descuento) que producen el mismo monto observado.
- Limitación: Pendiente de tu aceptación: F-093, F-090, F-073, F-130 y F-082 están propuestos. F-130 viene de fuente sin verificar.
- Limitación: Los ejemplos del CFO (Q-025) son construidos: prueban un límite del modelo, no describen a Finora.
- Limitación: No se afirma que hubo descuentos, ni se infieren del tamaño de un salto del monto.
- Limitación: No hay cifra histórica de revenue no capturado ni puente histórico por tarifa y descuento: se propone hacia adelante.
- En palabras de Hugo: “Con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento).”

**C-017 · Proponemos que el descuento exista como objeto propio, con fecha de fin**

Cada descuento se registra con tipo, monto, inicio, fin, motivo, Canal y aprobador, separado de la cantidad contratada y del precio de lista, y se lee desde la factura. El puente de MRR suma líneas propias de «descuento nuevo/aumentado» y «descuento reducido/terminado». Las herramientas revisadas (ChartMogul, Chargebee, Stripe), según cómo se configuren, lo mezclan con expansión o contracción o lo excluyen. Usadas tal cual, el fin de un descuento aparecería como expansión, y una subida de suscripción compensada por un descuento, como «sin cambio».

- Pregunta: ¿Cómo introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-150, F-152 · Tablas: —
- Intención visual: Separación: el descuento se desprende de la suscripción como objeto con inicio y fin, y el puente gana líneas propias.
- Limitación: Propuesta de especialista (R-021), pendiente de tu aceptación.
- Limitación: La revisión de herramientas es evidencia externa, no de Finora; no sabemos qué facturación usa.
- Limitación: Conviene revisar las trampas concretas que lista F-152 antes de mostrarlas.
- En palabras de Hugo: “Cómo debería Finora introducir descuentos temporales: mecanismo propuesto.”

**C-018 · El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan**

No hay un estándar para tratar los descuentos temporales en el MRR: es una decisión de definición que el CFO toma y declara. Para Finora, lo más útil es mostrar la capa de lista y la de neto. Con descuentos temporales, el MRR neto, el revenue reconocido y la caja pueden separarse, y cuál vista aplica depende de si los contratos son mensuales cancelables o a plazo fijo. Además, cambian las cohortes: la evidencia externa asocia la adquisición con descuento a clientes de menor valor, así que Finora tendría que marcar esas cohortes y medirlas contra un grupo comparable.

- Pregunta: ¿Qué implica, más allá del mecanismo, introducir descuentos temporales?
- Rol: implication · confianza medium · fuerza pending
- Evidencia: F-151, F-153, F-154, F-132 · Tablas: —
- Intención visual: Divergencia por capas: lista, neto, revenue y caja se separan cuando hay un descuento temporal.
- Limitación: Propuesta de especialista (R-021, R-011), pendiente de tu aceptación. F-132 viene de fuente sin verificar.
- Limitación: La asociación descuento → clientes de menor valor es evidencia externa; el churn al vencer el descuento tiene otras causas posibles (F-154).
- Limitación: No sabemos si los contratos de Finora son mensuales cancelables o a plazo fijo (F-153).
- Limitación: La convención oficial la decide el CFO; aquí solo se propone mostrar las dos capas.
- En palabras de Hugo: “Implicaciones multidisciplinarias; preguntas del CFO contestadas con el modelo propuesto.”

**C-019 · La Propuesta de Modelo de datos separa el valor en una escalera con vigencias**

El panel actual es cliente × mes × monto pagado: caja, no contrato. La propuesta registra, por suscripción y mes, cada peldaño de valor con su fuente y su vigencia: tarifa de lista (price_book_entry, por versión de plan, periodo y moneda, con valid_from/valid_to) → precio pactado (subscription_item_version: plan, cantidad, add-ons) → descuento con inicio, fin y motivo → MRR neto → facturado → cobrado. Así el MRR se guarda en bruto, descuento y neto por separado, y la convención oficial queda como decisión del CFO.

- Pregunta: ¿Cómo separar el valor de la suscripción del precio efectivamente pagado?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-130, F-132, F-133, F-151, F-152 · Tablas: —
- Intención visual: Cascada: de la tarifa de lista a lo cobrado, cada peldaño con su vigencia; la distancia entre peldaños es lo que hoy no se ve.
- Limitación: Propuesta de especialista (R-011), pendiente de tu aceptación. F-130, F-132 y F-133 vienen de fuente sin verificar (confianza baja); F-151 y F-152 (R-021) corroboran el principio de separar capas y tratar el descuento como objeto.
- Limitación: No sabemos si Finora tiene catálogo de precios, versiones de suscripción o facturas con líneas de descuento (F-133).
- Limitación: D-007 (activa) dejó el modelo de datos fuera de etapa: hay que confirmar si aplica.
- Limitación: El detalle de campos y tablas va al anexo.
- En palabras de Hugo: “Cómo separar el valor de la suscripción del precio efectivamente pagado: Propuesta de Modelo de datos (campos, tablas, definiciones).”

**C-020 · Si la suscripción no cambia, inicio o fin de descuento va a «Descuento»**

La clasificación compara cierres de mes por componente (suscripción, tarifa, descuento). Si la suscripción no cambia, el inicio o el fin de un descuento va a una línea «Descuento» del puente y no cuenta como contracción ni expansión; si cambian suscripción y descuento a la vez, cada efecto va a su línea. Hoy el puente observado no puede hacerlo: en 2024 registra COP 13,6 millones de expansión observada y −COP 21,5 millones de contracción observada con lectura indeterminada, y parte de esa contracción tiene forma de efecto de cobro (el cliente vuelve a su monto usual tras un mes más alto).

- Pregunta: ¿Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales?
- Rol: recommendation · confianza medium · fuerza pending
- Evidencia: F-150, F-152, F-131, F-041 · Tablas: T-003
- Intención visual: Reclasificación: lo que hoy cae en expansión o contracción observada se reparte entre suscripción, tarifa y descuento.
- Limitación: Propuesta de especialista (R-011, R-021), pendiente de tu aceptación.
- Limitación: T-003 es monto pagado observado por año calendario desde ene-22; los findings con inicio en mar-22 dan otros totales (F-047).
- Limitación: F-131 (confianza media): que la contracción tenga forma de efecto de cobro no descarta suscripciones más pequeñas.
- Limitación: Aplica hacia adelante: el histórico no trae tarifas ni descuentos para reclasificarlo.
- En palabras de Hugo: “Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales; probablemente lo integra la misma Propuesta de Modelo de datos.”

## Recomendaciones
- Pedir a Finora las entradas únicas con fecha, puerta (Self Service, Assisted, Executive), Canal de adquisición y segmento, con su vínculo al primer pago. _(si Si Finora las registra en su CRM o en su analítica digital (los datos del caso no las traen). Con ellas se distinguen H-001 a H-004.)_
- Pedir el roster semanal de SDR/AE con ramp y la fecha del primer contacto humano por entrada. _(si Solo si, descartados los artefactos (H-001 a H-004), queda una caída real de compra. Sirve para separar capacidad (H-006) de calidad (H-005).)_
- Confirmar qué pasó a inicios de 2023: si fue un cambio de registro (H-024) o de la operación comercial (H-025). _(si Antes de leer el escalón de primeros pagadores como más demanda o de usarlo como premisa de Q-001.)_
- Documentar la unidad y la escala del archivo de S&M, y la clasificación funcional de SoftwareTools y Freelance. _(si Antes de reportar cualquier CAC combinado o de leer el gasto por primer pagador como eficiencia.)_
- Acordar con el CRO el hito de adquisición (Won, primer pago o suscripción activa), la ventana W de conversión y el umbral de «estancado». _(si Antes de construir el bowtie y las tasas por cohorte: son parámetros de Finora, no estándares de mercado.)_
- Aplicar una regla de normalización (mes de servicio vs fecha de cobro) y una ventana de gracia, y rehacer el puente observado. _(si Mientras la facturación no traiga estado de suscripción. Si se confirma H-031, cambia la lectura de reactivación y contracción.)_
- Que el CFO decida y declare la convención de descuentos en el MRR, mostrando la capa de lista y la de neto. _(si Antes de lanzar el primer descuento temporal.)_
- Crear el descuento como objeto propio (tipo, monto, inicio, fin, motivo, Canal, aprobador) y sumar al puente las líneas de descuento nuevo/aumentado y reducido/terminado. _(si Si Finora decide introducir descuentos temporales y su facturación permite leerlos desde la factura.)_
- Marcar las cohortes adquiridas con descuento y compararlas con un grupo comparable sin descuento. _(si Si se introducen descuentos de adquisición.)_
- Arrancar los foros con lo que ya está en verde (MRR pagado observado y su puente, ARPA por cohorte, churn con ventana de gracia) y sumar el lado izquierdo del bowtie cuando exista la capa técnica. Agentes de IA, solo sobre métricas gobernadas y con piloto. _(si Una vez definidas las decisiones del CRO por foro.)_
- Tratar Salud como una señal a validar, no como un segmento prioritario. _(si Si con churn normalizado y más de un año de datos se mantiene su perfil, evaluar si amerita una prueba comercial.)_

## Apéndice candidato
- Calidad del archivo de S&M — Explica por qué el gasto no se lee como COP, como CAC ni como efecto por categoría: unidad sin escala, Team fijo en 12%, Freelance en cero y PayrollExpenses negativo.
- Puente del monto pagado observado — Contexto para el CFO: el puente concilia con el total y sus movimientos brutos superan varias veces el neto. Hay dos ventanas (ene-22 y mar-22) con totales distintos.
- Comportamiento del monto: reversiones, montos fuera de grilla y cobros retroactivos — Respalda que el monto es consistente con cobro más que con contrato; es la base de la regla de normalización.
- Robustez del ticket de entrada — La dirección se mantiene con promedio, mediana, cuantiles y segundo pago; la magnitud cambia y entre 2023 y 2024 se estabiliza.
- Correlaciones entre gasto y primeros pagadores — Detalle de las pruebas: ninguna relación positiva significativa. No va en el cuerpo porque no decide nada.
- Churn: observado vs persistente, promedio vs mediana — Matiza la lectura de las salidas y reúne las discrepancias por reconciliar (T-002 vs T-034; F-052 vs T-047).
- Cosechas y ventana de flujo — Explica por qué los flujos arrancan en mar-22 y da el detalle por cosecha y por base.
- Detalle por industria — Primeros pagadores, ticket y aporte al crecimiento por industria: soporta que la industria no concentra el cambio.
- Hipótesis ToFu/BoFu con su dato mínimo — Detalle de H-001 a H-008 y de H-028, con lo que validaría o descartaría cada una; es demasiado para una lámina.
- Propuesta de Modelo de datos: tablas y campos — Detalle técnico (tablas, campos, objeto descuento, líneas del puente) que no cabe en S3.3.

## Preguntas sin resolver
- S2.1 · «Las relaciones que comentó Hugo»: el guion dice «por precisar». ¿Qué relaciones son? No la relleno. Si son volumen vs valor de entrada, o gasto vs primeros pagadores, ya están en S2.2.
- Readiness: no hay findings aceptados. Orden sugerido de revisión: F-071, F-072, F-075 y F-097 (Overview y S2.4) → F-110, F-113, F-112 y F-107 (S2.2) → findings de R-010…R-021 (propuestas).
- D-007 (activa) deja la solución fuera de etapa (sin dashboards, métricas definitivas ni modelo de datos). Tu guion aprobado incluye S2.5, S2.7 y S3.3, y D-016 delegó este borrador. ¿D-007 aplicaba solo a Framing, o hay que superarla con una decisión nueva?
- Churn observado 2024: T-002 da 2,04% y T-034, 1,9%. ¿Distinta ventana o distinto denominador?
- Churn observado por industria 2024: F-052 (Producción mínimo, Tecnología máximo) no coincide con T-047 (Restaurantes 1,46 a Tecnología 2,57).
- Freelance: F-117 lo pone en cero desde may-23, pero T-006/T-009 marcan jun-23 como último mes con valor.
- ¿Qué pasó a inicios de 2023: efecto de registro (H-024) o cambio en la operación comercial (H-025)?
- Hito de adquisición del CRO (Won, primer pago o suscripción activa), ventana W y umbral de «estancado»: por acordar con Finora.
- Unidad y escala del archivo de S&M, y clasificación de SoftwareTools/Freelance: sin documentar (X-001, X-002).
- ¿Qué decide el CEO con el Overview y qué decisiones tiene el CRO en cada foro? Sin eso, S2.7 queda partial y Q-003 se contesta solo en parte.
- ¿Los contratos de Finora son mensuales cancelables o a plazo fijo? De eso depende qué vista aplica (F-153).
- ¿Qué registra hoy Finora en su CRM, su analítica digital y su facturación? Los datos del caso no lo dicen.
- T-053 muestra en mediana el primer pago por encima del segundo; eso parece ir contra la premisa de H-032. Conviene evaluar el impacto.
- Sugerencia, no cambio: poner S2.4 junto a S2.2 dejaría contiguo «lo que sí vemos». El paquete sigue tu orden.

## Validación
- ✖ C-007: cifra(s) sin tabla que las respalde: −COP 31,7 mil, −COP 26,6 mil, −COP 5,2 mil.
- ⚠ Láminas del guion sin evidencia todavía: S2.1 (van a research, no se rellenan).
- ⚠ Láminas del guion con evidencia parcial: S2.7.
