# QA — Finora · La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos

> Producido por `slide-critic` (autor) sobre la corrida retomada del 2026-09-29. El reporte automático vive en `renders/qa-summary.md`; los renders previos a cada revisión quedan como `renders/NN.v1.png`. La crítica independiente (agente `independent-slide-critic`) se registra al final.

## Resumen

- **Estado final: 25 PASS** tras aplicar la crítica independiente (11 PASS · 14 PATCH · 0 RECOMPOSE); 0 ✖ en el QA automático final.
- 25 láminas (portada + 24 del guion). Autor, antes de la crítica independiente: 25 PASS tras 1–2 iteraciones.
- ⚠ restantes, justificados: `near-miss-alignment` en S07 y S18 (etiquetas de valor al final de barras de distinto largo: la posición la dicta el dato); `sparse` en S18 (lámina de respiro).
- Láminas de la corrida anterior (S00–S08): conservadas; parcheadas S02, S04, S05, S06, S07 y S08. Nuevas (S09–S24): renderizadas, revisadas y corregidas en esta corrida.
- Riesgos residuales: S03 compite entre el «6 de 6» (96 px, tinta) y las barras lima; S14 y S20 están en el tope de palabras (134/135 y 130/130); S18 usa la mediana M1 de FIN-F-160, que no coincide con FIN-F-086/087 (anotado en storyline §7).

## Deck

- Variedad: 25 composiciones distintas (100%); 0 grillas de cards; ninguna familia tres veces seguida.
- Ritmo: Overview con evidencia (S01–S04) → propuesta de rutas (S05–S06) → diagnóstico (S07–S08) → tramo denso de diseño (S09–S17) con respiros en S12 (fórmula) y S15 (firmas) → Revenue alterna evidencia (S18–S19) y modelo (S20–S23) → cierre con casos (S24).
- Sistema: kicker «Sección · subtema (· propuesta)», título Open Sans 56 px a la izquierda, pie «Fuente/Propuesta … · IDs» + página; hairlines 1,5 px; punteado = propuesto/no existe; lima = una marca de insight por lámina; texto del acento en tinta (o #687e44) por contraste.
- Nivel deck del QA automático: sin hallazgos.

| Tramo | Láminas | Densidad | Familias |
|---|---|---|---|
| Portada + Overview | S00–S02 | ligera → media | editorial · evidence · economics |
| Growth · lo que vemos | S03–S04 | media–densa | evidence ×2 (small multiples de distinto tipo) |
| Growth · definir funnel | S05–S06 | densa | process · comparison |
| Growth · dónde está la pérdida | S07–S08 | media · ligera | economics · comparison |
| Growth · medir | S09–S12 | densa → ligera | process · logic · relationships · economics |
| Growth · hipótesis | S13–S15 | media–densa | process · logic · comparison |
| Growth · operarlo | S16–S17 | densa | operating_model ×2 (as-is/to-be y cadencia: gramáticas distintas) |
| Revenue | S18–S24 | ligera → densa → media | comparison · economics · process · evidence · economics · logic · comparison |

## Láminas

### S00 — La brecha clientes–monto se asocia a quién entra
- Lectura a ciegas: primero la frase con «quién entra» marcado; luego el tracker Overview → Growth → Revenue. Coincide con el governing thought.
- Scores: story 5 · focal 5 · fidelity 4 · economy 4 · craft 5 · system 5. Veredicto: PASS (sin cambios).

### S01 — Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8×
- Lectura: la cuña lima entre las dos líneas; luego −38% por cliente. Coincide (C-001).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS (sin cambios).

### S02 — La caída por cliente se asocia a quién entra; la base previa sostiene su monto
- Lectura: cosechas 2023–24 en lima, bajas y anchas; base previa alta. Coincide (C-002).
- Scores: 5 · 4 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): la etiqueta de la llave «Cosechas 2023–24» pasa a una línea (antes rozaba el pie).

### S03 — Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias
- Lectura: barras lima del ticket 2023–24 y el «6 de 6»; luego el escalón de primeros pagadores. Coincide (C-003).
- Scores: 4 · 3 · 4 · 4 · 4 · 4. PASS con riesgo: el «6 de 6» compite con el foco lima. Queda para el crítico independiente.

### S04 — Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas
- Lectura: franja lima 2023 jun–dic donde el gasto baja y los pagadores suben. Coincide (C-004).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): ⚠ low-contrast resuelto (etiqueta de la franja en tinta).

### S05 — Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar
- Lectura: cuatro rutas que salen de una entrada y convergen en el nudo; «Fijos al entrar» en lima. Coincide (C-005).
- Scores: 4 · 4 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): la etiqueta del nudo cruzaba la curva de Self Service → movida a la derecha, bajo la flecha; zona «antes del nudo» como franja gris (sin caja punteada cortada por las curvas); 146 → 120 palabras; ⚠ near-miss resuelto.

### S06 — Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño
- Lectura: la fila Executive · outbound en lima y los puntos de etapa por ruta. Coincide (C-021).
- Scores: 5 · 5 · 5 · 4 · 5 · 5. PASS.
- Cambios (it. 1–2): «tu secuencia literal» (dirigido a Hugo) → «secuencia literal del brief», en segunda línea para no pisar la línea lima; nota inferior recortada; 117 → 106 palabras.

### S07 — La pérdida está en el monto por cliente de cosechas de menor ticket
- Lectura: el paso lima de composición (−26,6; 84%) en el puente. Coincide (C-007).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): pie en una sola línea. ⚠ near-miss justificado (etiquetas al final de barras).

### S08 — Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar
- Lectura: burbuja lima de Salud en el cuadrante bajo churn · ticket alto. Coincide (C-008).
- Scores: 4 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1–2): la anotación de Salud cruzaba el título del eje y la etiqueta del cuadrante → abajo a la izquierda con líder corto y fondo; contraste de etiquetas resuelto; nota de churn observado a las notas; 109 → 95 palabras; pie en una línea.

### S09 — Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento
- Lectura: franja lima del nudo (Won y primer pago) y seis filas que llegan a ella. Coincide (C-006).
- Scores: 4 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): más aire bajo el título; filas a 88 px (las etiquetas se rozaban); contraste sobre gris; 118 → 114 palabras.

### S10 — Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta
- Lectura: rama Eficiencia en lima con casi todo en ○. Coincide (C-009).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): clave del semáforo abajo con la regla MECE (antes se pisaba); churn observado vs persistente en tres líneas; 130 → 125 palabras.

### S11 — Cada métrica vive en un solo lugar del catálogo, con dueño, fuente y foro
- Lectura: el registro con «un nombre · una fórmula · un lugar» en lima; entradas y salidas. Coincide (C-022).
- Scores: 4 · 5 · 4 · 4 · 4 · 5. PASS.
- Cambios (it. 1): conectores de entrada convergen al registro; controles en notación compacta; 114 → 103 palabras.

### S12 — Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC
- Lectura: «no es CAC» entre la fórmula de hoy (sólida) y la del CAC (punteada); la pendiente con y sin Habilitación. Coincide (C-010).
- Scores: 5 · 4 · 5 · 5 · 4 · 5. PASS.
- Cambios (it. 1): fila «peso de Habilitación» chocaba con los años; trazos sueltos quitados; «CAC · no existe hoy»; 91 → 85 palabras.

### S13 — Primero se fija qué es venta; revisar la medición en pagos no cierra la brecha
- Lectura: Paso 0 en lima que alimenta la premisa; tres compuertas; «la brecha sigue en pie». Coincide (C-011).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1–2): columnas alineadas al poste de cada compuerta; etiqueta «Premisa» fuera del poste; corte de línea «jul–oct» protegido; 115 → 109 palabras.

### S14 — Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja
- Lectura: la regla de orden en lima y el árbol medición | negocio con su palanca. Coincide (C-023).
- Scores: 4 · 4 · 5 · 3 · 4 · 5. PASS (economía justa: 134/135).
- Cambios (it. 1–2): la identidad de la raíz se desbordaba sobre el árbol; dos conectores rectos no se dibujaban; los corchetes de palancas pisaban hojas; palanca larga dentro del margen.

### S15 — Calidad y capacidad se separan con mezcla contra tasa, dentro de cada puerta
- Lectura: pendientes lima que se mueven (mezcla en calidad; tasa, carga y espera en capacidad). Coincide (C-012).
- Scores: 5 · 5 · 5 · 5 · 4 · 5. PASS.
- Cambios (it. 1): «base/caída» chocaban con la regla; subtítulos redundantes fuera; 119 → 97 palabras.

### S16 — Proponemos pasar de pagos por cliente-mes a una cuenta común con demanda, funnel y suscripción
- Lectura: la espina lima `account · account_xref` con tres capas punteadas encima; as-is aislado a la izquierda. Coincide (C-013).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1–2): nombres de tablas una por línea (desbordaban y dejaban «·» huérfanos); bordes alineados; 122 → 118 palabras.

### S17 — Proponemos dos vías: dashboards para los foros recurrentes y agentes de IA para el día a día
- Lectura: escalera semanal → trimestral con la decisión marcada en lima; carril diario debajo. Coincide (C-014).
- Scores: 5 · 4 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): el subrayado con gradiente se leía como tachado (⚠ gradient) → barra lima vertical; carril diario sin marcas de regla; 123 → 120 palabras.

### S18 — Lo observable es el primer y segundo pago; el descuento no es verificable
- Lectura: la brecha lima de 2022 entre primer y segundo pago; 2023–24 juntos. Coincide (C-015).
- Scores: 5 · 5 · 5 · 5 · 4 · 5. PASS. ⚠ near-miss y sparse justificados.
- Cambios (it. 1): pie en una línea; 2023 (valores iguales) como aro concéntrico con «iguales».

### S19 — Con cliente, mes y monto se ve qué cambió, no por qué
- Lectura: segmentos lima de firma de cobro en churn, reactivación y expansión; contracción oscura (se sostiene). Coincide (C-024).
- Scores: 5 · 5 · 5 · 5 · 4 · 5. PASS.
- Cambios (it. 1): 102 → 84 palabras (cifras repetidas y «al mes siguiente» fuera; nota sintetizada).

### S20 — El descuento se registra como objeto propio, con origen, source y fecha de fin
- Lectura: `discount_grant` en lima donde convergen los cinco orígenes; sale a «Descuento (inicio/fin)»; contrato en carril aparte. Coincide (C-017).
- Scores: 5 · 5 · 5 · 3 · 4 · 5. PASS (economía justa: 130/130).
- Cambios (it. 1–2): `acquisition_touch` quedaba tapado por una etiqueta de conector; conector en S hacia el puente → flecha recta; carril de contrato separado del grant.

### S21 — El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan
- Lectura: el bloque lima del descuento entre lista y neto; caja en su carril; mecanismo en tres pasos. Coincide (C-018).
- Scores: 4 · 5 · 4 · 4 · 4 · 5. PASS.
- Cambios (it. 1): la caja (punteada) se confundía con la etiqueta «MRR neto» → carril propio de barras esquemáticas; 129 → 118 palabras.

### S22 — La propuesta de modelo de datos separa el valor en una escalera con vigencias
- Lectura: escalera que baja de la lista a lo cobrado; MRR neto en lima; llaves MRR vs caja. Coincide (C-019).
- Scores: 5 · 5 · 5 · 5 · 4 · 5. PASS.
- Cambios (it. 1): ✖ text-overlap (`subscription_item_version` × `discount_grant`) resuelto cortando en «_»; nombres dentro de cada peldaño; pie en una línea.

### S23 — Si la suscripción no cambia, inicio o fin de descuento va a «Descuento»
- Lectura: la rama «No» lleva al bloque lima «Descuento (inicio/fin/cambio)». Coincide (C-020).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): bloque lima más angosto; 127 → 124 palabras.

### S24 — Con el modelo propuesto, cada caso del CFO se lee en su capa
- Lectura: el −30 lima del caso 2 (que hoy se vería «sin cambio»). Coincide (C-025).
- Scores: 5 · 5 · 5 · 4 · 4 · 5. PASS.
- Cambios (it. 1): ✖ text-overlap (nota del caso 1 × «Hoy») resuelto reacomodando la vertical; etiquetas de categoría separadas; 130 → 124 palabras.

## Crítica independiente (agente `independent-slide-critic`, contexto fresco, sin edición)

Veredicto: **11 PASS · 14 PATCH · 0 RECOMPOSE**. Ninguna composición mal elegida; tres tipos de problema: etiquetas que permiten leer mal el dato, jerarquía donde un gris o un número le gana a la lima, y deriva del contrato de codificación (lima y punteado con otro significado). Todo se aplicó salvo lo marcado como no aplicado.

| Lámina | Veredicto del crítico | Aplicado |
|---|---|---|
| S03 | PATCH | «6 de 6» de 96 a 56 px; primeros pagadores en gris claro; rótulos por medida (ticket de entrada = primer pago; barra = monto usual temprano); rótulo de la barra encima de ella; «ene-23» sin corte. Escalado a Hugo en storyline §7: el «6 de 6» se mide en M0, no en ticket estabilizado. |
| S04 | PATCH | paneles 40 px más abajo (aire bajo el título); nota de correlación «ninguna significativa (\|r\| ≤ 0,27)», p mínimo a notas. |
| S05 | PATCH | «Fijos al entrar» sobre la línea de entrada; «la ruta se clasifica al final» junto al nudo; clave con/sin persona en la esquina del panel; loop Reactivate sólido. |
| S07 | PATCH | título del panel: «MRR por cliente activo, variación dic-22 → oct-24» (antes se podía leer como caída del MRR de la industria). |
| S08 | PATCH | zona del cuadrante en gris (una sola marca lima: Salud); anotación de Salud recortada, más angosta y lejos del eje; v2 tapaba una burbuja → v3 corregida. |
| S09 | PATCH | filas en el orden del título; «MRR de entrada por Won» fuera de la franja; «por etapa» ambiguos fuera. |
| S10 | PATCH | lima solo en la rama Eficiencia (no en el lomo); churn observado/persistente a las notas; segunda frase de la regla MECE fuera (S11 la dice). |
| S12 | PATCH (casi recomposición) | sin la pendiente que dramatizaba el −66%: fórmula de hoy contra CAC, término contra término, con las tres brechas rotuladas y «no es CAC» al centro; la sensibilidad en una línea. |
| S16 | PATCH | `discount` → `discount_grant`; columnas «Funnel comercial» y «Suscripción y facturación», como el título. |
| S17 | PATCH | sin las tres barras lima (acento sin usar, a propósito); la vía del día a día con más peso (línea 3 px, texto 24 px). |
| S19 | PATCH | 88,9% de tinta a gris medio (la lima vuelve a ser el foco); el 7,1% sin rotular en el mismo gris claro del resto. Opcional de redacción no aplicado (sube a 87/85 palabras). |
| S21 | PATCH | la línea de MRR neto se ve (10 px bajo la lista fuera de la ventana) y lleva su etiqueta; marcadores de inicio y fin sólidos; «revenue reconocido» explícito. |
| S22 | PATCH | «Descuento recurrente» como peldaño sólido gris claro (el punteado se leía como «deducción»). |
| S23 | PATCH | signos como prefijo (− inicio · + fin · ± cambio) para que no se lea como fórmula. |
| S14, S15, S24 | PASS con opcionales | aplicados: fórmula de la raíz con cortes explícitos (S14); «periodo base / periodo de caída» (S15); «el −38% no se puede repartir entre lista y descuento» (S24). |
| S06, S11, S13 | PASS con opcionales | no aplicados: el dueño repetido en llaves y sufijos (S06) y «no cruzados» (S11) quedan como están; «la premisa se sostiene» (S13) pasaría el tope de palabras. |
| S00, S01, S02, S18, S20 | PASS | sin cambios. |

Nivel deck, aplicado: una sola marca lima por lámina (S08, S10, S17); punteado solo para «propuesto» (S05, S21, S22); foco en la lima y no en el gris oscuro (S03, S19); vocabulario `discount_grant`; pies sin códigos Q-/D-/X- (S09, S14). No aplicado (riesgo residual, bajo): posición única de leyendas en todo el deck y unificar «altas» / «primeros pagadores» (solo el pie de S13 define «altas» como primer pago observado; S18 y S19 usan «altas» sin definirlo).

**Escalación por tope de iteraciones:** S08, S12, S14, S16 y S24 pasaron de 3 iteraciones del autor con el parche de la crítica independiente (permitido una vez). S12 es el caso a mirar: el crítico lo marcó PATCH, pero quitar la pendiente cambió el exhibit (de fórmula + pendiente a solo fórmula); queda documentado en `slide-specs/S12.yaml › revision_note`.

## Iteration log

| Lámina | v1 (render previo) | Cambios | Estado |
|---|---|---|---|
| S02 | renders/02.v1.png | etiqueta de la llave en una línea | v2 PASS |
| S04 | renders/04.v1.png | contraste de la franja | v2 PASS |
| S05 | renders/05.v1.png | colisión del nudo, zona, loop, −26 palabras | v2 PASS |
| S06 | renders/06.v1.png | «tu» → «del brief», nota recortada; v2 pisaba la línea lima → v3 en dos líneas | v3 PASS |
| S07 | renders/07.v1.png | pie en una línea | v2 PASS |
| S08 | renders/08.v1.png | anotación de Salud, contraste, −14 palabras, pie; v3 con fondo y borde alineado | v3 PASS |
| S09 | renders/09.v1.png | aire, filas, contraste, palabras | v2 PASS |
| S10 | renders/10.v1.png | clave del semáforo, anotación de churn, palabras | v2 PASS |
| S11 | renders/11.v1.png | conectores, palabras | v2 PASS |
| S12 | renders/12.v1.png | fila de Habilitación, trazos, palabras | v3 PASS |
| S13 | renders/13.v1.png | alineación, «Premisa», Paso 0 conectado, palabras | v3 PASS |
| S14 | renders/14.v1.png | raíz desbordada, conectores, corchetes, margen | v3 PASS |
| S15 | renders/15.v1.png | base/caída, −22 palabras | v2 PASS |
| S16 | renders/16.v1.png | tablas una por línea, alto de cajas | v3 PASS |
| S17 | renders/17.v1.png | marcador sin gradiente, carril, palabras | v2 PASS |
| S18 | renders/18.v1.png | pie, 2023 «iguales» | v2 PASS |
| S19 | renders/19.v1.png | −18 palabras | v2 PASS |
| S20 | renders/20.v1.png | `acquisition_touch`, conector recto, carril | v3 PASS |
| S21 | renders/21.v1.png | carril de caja, palabras | v2 PASS |
| S22 | renders/22.v1.png | ✖ text-overlap, nombres dentro, pie | v2 PASS |
| S23 | renders/23.v1.png | ancho del bloque, palabras | v2 PASS |
| S24 | renders/24.v1.png | ✖ text-overlap, etiquetas | v3 PASS |
| S03 | renders/03.v1.png | (crítica independiente) jerarquía y rótulos por medida; v2 el rótulo de la barra la pisaba → v3 | v3 PASS |

Tras la crítica independiente se sumó una iteración en S04, S05, S07, S09, S10, S14–S17, S19 y S21–S24, y dos en S03, S08 y S12 (la segunda corrigió una regresión: rótulo sobre la barra en S03, burbuja tapada en S08 y chip pegado a la tercera brecha en S12). Todas vueltas a revisar como imagen.
