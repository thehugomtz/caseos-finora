# QA — Business case: Finora (deck v5)

> Producido por `slide-critic` (Visual Storyteller) y revisado por el crítico independiente (`independent-slide-critic`,
> contexto nuevo, sin permiso de edición). El reporte automático vive en `renders/qa-summary.md`.
> Estado: EN REVISIÓN. La revisión del autor (iteración 3) está completa; faltan los veredictos del crítico independiente.

## Resumen

- 34 láminas: portada, 3 separadores de sección, 14 láminas de cuerpo, portada final, separador de anexos y 14 anexos.
- QA automático: 0 errores ✖; 1 advertencia ⚠ (lámina 14, `near-miss-alignment`), justificada abajo.
- Corrida retomada: la anterior se cortó (SIGTERM) mientras el crítico independiente revisaba; sus veredictos no llegaron.
  Esta corrida volvió a renderizar todo, revisó cada render de a una lámina y aplicó una iteración de parches antes de
  pasar el deck a un crítico nuevo.

## Deck (hoja de contactos)

- **Sistema:** kicker, título, pie y márgenes idénticos en las láminas de contenido; acento turquesa solo en el insight;
  coral solo en «lo que no existe hoy» (07, 09, 11); separadores de color sólido solo con el nombre.
- **Variedad:** 14 composiciones distintas en las 14 láminas del cuerpo; 0 card grids; ninguna familia tres veces seguida.
- **Ritmo:** Growth tiene siete láminas densas seguidas (06–12) porque el guion pone siete preguntas; el respiro es el
  separador de Revenue (13). Excepción documentada en storyline §7 (opción: C-029 a anexo).
- **Hilo visual:** 10 → 11 comparten la espina numerada 1–5; 06 → 07 comparten el grosor «con persona».
- **Vocabulario y cifras cruzadas (revisado en esta corrida):** 91% (04, 2022→2023) contra 96% (22, 2022→2024): ambos
  están en FIN-F-164; la 04 ahora dice su periodo. Nudo: la 07 ya no lo fija («por acordar», Q-050); los anexos 24–25
  conservan «primer pago» de la medición anterior (su kicker lo dice). IDs de archivo (`FIN-F-…`) fuera de las fuentes
  de 28, 30 y 32: ahora citan sus tablas (T-…).

## Revisión del autor, lámina por lámina (iteración 3)

Scores: story · focal · fidelity · economy · craft · system.

| # | Lectura a ciegas (primero veo → entiendo) | Scores | Veredicto | Cambios |
|---|---|---|---|---|
| 01 | título «Business case: Finora» | — | PASS | — |
| 02 | «Overview» sobre turquesa | — | PASS | — |
| 03 | la cuña turquesa entre dos líneas → los clientes crecen más que el monto | 4·5·5·5·5·5 | PASS | cuña cortada exactamente donde las líneas se cruzan (antes rellenaba astillas donde el MRR supera a los clientes) |
| 04 | marimekko y la pregunta a la derecha → tres observaciones llevan a «¿por qué ruta, canal y etapa?» | 4·4·4·4·4·5 | PASS tras parche | «2022» centrado bajo las dos barras grises (feb-22 quedaba sin rótulo); «Abre Growth →» fuera del acento; el 91% dice su periodo (2022→2023); «Cruzar fechas no atribuye ventas» (texto del claim); 119 palabras |
| 05 | «Growth» sobre menta | — | PASS | — |
| 06 | fila turquesa de punta a punta → cada ruta toma tramos de una lista maestra | 4·5·4·4·4·5 | PASS | — |
| 07 | nudo turquesa y zona de resultados comunes → se mide dentro, se compara solo en el nudo | 4·4·4·4·4·5 | PASS tras parche | lista con viñetas → espina que sale del nudo y alimenta cada resultado; «Won» bajo el nudo → «por acordar» (el claim no fija el nudo, Q-050) |
| 08 | cosechas 2023–24 abajo en turquesa → las cosechas nuevas entran con menos monto | 4·4·4·4·4·5 | PASS | — |
| 09 | «Eficiencia» resaltada → cada métrica nueva habilita una decisión | 4·4·4·4·4·5 | PASS | — |
| 10 | espina 1→5 → árbol ordenado con paso 0 | 4·4·4·4·4·5 | PASS | — |
| 11 | espina 1–5 y columna «no» → ningún dato está hoy | 4·4·4·4·4·5 | PASS tras parche | guías punteadas sueltas eliminadas (no tocaban ni el texto ni el «no») |
| 12 | escalera de foros sobre la capa técnica → dos vías sobre una base; facturación primero | 4·4·4·4·4·5 | PASS | — |
| 13 | «Revenue» sobre lima | — | PASS | — |
| 14 | pesa 2022 en turquesa → en 2022 el primer pago supera al segundo | 4·4·4·5·4·5 | PASS | ⚠ `near-miss-alignment` justificado: los valores van rotulados al final de cada barra (rotulación directa); 73,5% y 77,3% quedan a 7 px por sus longitudes |
| 15 | segmentos turquesa en cada barra → parte del puente es firma de cobro | 4·4·4·4·4·5 | PASS | — |
| 16 | objeto Descuento (encabezado turquesa) → registro propio con un solo origen | 4·5·4·4·4·5 | PASS tras parche | conector punteado suelto → llave que agrupa oferta → código → descuento aplicado, atada al objeto |
| 17 | peldaño Descuento en turquesa → la escalera separa lista, pactado, descuento, neto y caja | 4·4·4·4·4·5 | PASS | — |
| 18 | −30 turquesa en el caso 2 → cada caso cae en su capa | 4·4·4·4·4·5 | PASS tras parche | ranuras de 108 → 128 px («Expansión» y «Descuento (inicio)» se tocaban); escala 1,9 → 1,75 (los valores rozaban el título del caso); «no precio ni descuento» → «no un efecto separable de precio o descuento» (texto del claim); 130 palabras |
| 19 | portada repetida | — | PASS | — |
| 20 | «Anexos» sobre tinta | — | PASS | — |
| 21–34 | anexos del v3 re-tematizados | 4+ en todas | PASS | fuentes: «Finora ·F-223» → «Finora · F-223» (25); `FIN-F-…` → T-036, T-011, T-012 (28), T-093, T-094, T-100, T-089 (30), T-096 (32); «los churn» → «los churns» (32) |

## Crítico independiente

(pendiente)

## Registro de iteraciones

| Lámina | Iteración | Render guardado | Qué se vio | Cambio |
|---|---|---|---|---|
| S04 | 1 (corrida anterior) | sobrescrito | rótulos de periodo sobre la línea; fuente en dos líneas; 129/115 palabras; «2023» inexacto para 54,7 | una línea base para los periodos; «desde 2023»; fuente corta; 120 palabras |
| S06 | 1 | — | 122/120 palabras | rótulo de Reactivate más corto |
| S07 | 1 | renders/07.v1.png | la curva de Self Service pisaba «uplift, con holdout»; Reactivate salía del panel; 138/125 palabras | rótulo entre carriles; Reactivate en dos líneas; 120 palabras |
| S08 | 1 | renders/08.v1.png | el tamaño casi no se leía; «−46,6%» fuera del margen; 125/100 palabras | radio 44·√share; barras más angostas; 110 palabras |
| S09 | 1 | renders/09.v1.png | 154/120 palabras | columnas más cercanas; 125 palabras |
| S10 | 1 | renders/10.v1.png | flecha Brecha → Paso 0 casi invisible; 131 palabras | raíz más angosta; 120 palabras |
| S11 | 1 | renders/11.v1.png | «Dato mínimo» no coincidía con «firma» del título; 141 palabras | encabezado «Firma y dato mínimo»; 130 palabras |
| S12 | 1 | renders/12.v1.png | texto de los escalones sobre los verticales; 131 palabras | texto desplazado; 124 palabras |
| S14–S18 | 1 | 16.v1, 17.v1 | palabras sobre el presupuesto; contraste 2,05:1 en el peldaño MRR neto (17) | recortes; peldaño en ink-2 con texto blanco |
| S03 | 3 (esta corrida) | renders/03.v1.png | la cuña rellenaba astillas donde el MRR supera a los clientes | cruces interpolados |
| S04 | 3 | renders/04.v1.png | barra feb-22 sin rótulo; «Abre Growth» en acento; 91% sin periodo frente al 96% del anexo | ver tabla de arriba |
| S07 | 3 | renders/07.v2.png | lista con viñetas en caja tintada; «Won» fijaba el nudo | espina desde el nudo; «por acordar» |
| S11 | 3 | renders/11.v2.png | guías punteadas sueltas | eliminadas |
| S16 | 3 | renders/16.v2.png | conector punteado que no tocaba nada | llave + línea sólida |
| S18 | 3 | renders/18.v1.png | «Expansión» y «Descuento (inicio)» a 6 px; valores pegados al título; frase más fuerte que el claim | ranuras, escala y texto |
| 25, 28, 30, 32 | 3 | — | fuentes con nombres de archivo o sin espacio | IDs de tabla |
