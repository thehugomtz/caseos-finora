# Finora · Fase 1 · Notas de trabajo del análisis exploratorio

> **Entender primero. Explicar después. Decidir al final.**
> Este documento describe qué contienen los datos y cómo se comportan. No diagnostica los problemas del CRO ni del CFO.

Generado el 28 sep 2026, 18:48 por `finora_eda.py`. Cada cifra se recalcula desde los archivos crudos; ninguna se escribe a mano.

---

## 0. Entregables

| Archivo | Qué es |
|---|---|
| `finora_eda.html` | Workspace de exploración autocontenido. Solo usa Google Fonts de forma opcional; abre sin conexión. |
| `finora_analytical_dataset.csv` | Tabla analítica cliente-mes: 66.674 filas, una por cliente y mes. |
| `finora_monthly_metrics.csv` | Métricas mensuales de la empresa: clientes, puente de MRR, valor, tasas, rubros y grupos de S&M, eficiencia. |
| `finora_eda_notes.md` | Este archivo: definiciones, transformaciones, supuestos, anomalías, preguntas y limitaciones. |
| `finora_eda.py` | Pipeline reproducible (Python 3.13.7 · pandas 3.0.3 · numpy 2.4.4 · scipy 1.17.1). |
| `supporting/*.csv`, `supporting/data_audit.json` | Tablas de industrias, cohortes, correlaciones, descomposición, puentes y auditoría que usa el workspace. |
| `brain/` | Conocimiento del negocio en archivos versionados: catálogo de métricas, problemas de datos conocidos, preguntas doradas, glosario, reglas de lenguaje y linaje de cada tarjeta. `brain/evidence/canonical_findings.yaml` lo genera el pipeline. |
| `templates/` | Plantillas HTML, JS y Markdown que llena el pipeline. |

Para reproducir: `python3 finora_eda.py` (lee `data/raw/` y `brain/`, y escribe todo lo anterior).

### Cómo leer los estados

Cada afirmación del workspace lleva un estado (eje 1) y, cuando aplica, un marcador (eje 2).

| Estado | Significado |
|---|---|
| Hecho observado | Se lee directamente de los datos, sin supuestos. |
| Evidencia fuerte | Resultado de un método con prueba de robustez (por ejemplo, descomposición con bootstrap y variantes). |
| Direccional | Patrón consistente, pero con n pequeño o sin identificación causal. |
| Hipótesis | Lectura razonable que hay que validar con Finora. |
| No evaluable | No se puede responder con estos archivos. |

Marcadores: **Explorando** (el título es una pregunta abierta), **Precaución** (hay una advertencia sobre el dato) y **Método** (explica cómo se calcula).

---

## 1. Auditoría de las fuentes

### 1.1 `Transactions.csv`: una foto cliente × mes, no transacciones

| Revisión | Resultado |
|---|---|
| Columnas | `ID`, `month`, `amount` (UTF-8 con BOM) |
| Filas | 66.674 = 1.961 clientes × 34 meses → **panel completo y balanceado** |
| Grano | una fila por cliente y mes calendario (`month` es una fecha de fin de mes en texto `M/D/AAAA`) |
| Rango de fechas | ene-22 → oct-24 |
| Duplicados | 0 en (`ID`, `month`); 0 filas completas duplicadas |
| Faltantes o ilegibles | 0 |
| Montos negativos | 0 |
| Montos en cero | 33.703 filas (50,5%): los meses inactivos vienen como ceros explícitos |
| Montos positivos | 32.971 filas; rango COP 1,4 mil a COP 8,48 millones; mediana COP 52,5 mil; P99 COP 325,8 mil |
| Valores extremos | 614 meses-cliente (130 clientes) por encima de Q3 + 3·RIC (COP 227,3 mil). Se conservan. |
| Precisión | hasta 6 decimales (6.024 filas con 6 decimales) → se comparan exactamente como micro-unidades enteras |
| Nombre | el archivo se llama “Transactions”, pero el grano es una foto mensual por cliente |

### 1.2 `Industry.csv`

| Revisión | Resultado |
|---|---|
| Columnas | `ID`, `Industria` (UTF-8 con BOM; encabezados en dos idiomas) |
| Filas | 1.962 leídas → se elimina 1 fila final completamente vacía → 1.961 |
| Llave | `"Cliente N"` → `N` (regex `^Cliente (\d+)$`); única; contigua de 1 a 1.961 |
| Valores | 6 industrias sin variantes de mayúsculas, acentos ni espacios: Restaurantes, Producción, Retail, Tecnología, Servicios profesionales, Salud |
| Cruce con Transactions | 100% en ambos sentidos, sin excepciones |

### 1.3 `S&M_spend.csv`

| Revisión | Resultado |
|---|---|
| Columnas | `Month` (`AAAA-MM`) + `PaidMedia`, `Travel`, `PublicidadNoWeb`, `Freelance`, `SoftwareTools`, `Team`, `PayrollExpenses` |
| Filas | 34 meses, idénticos a los de Transactions; sin duplicados ni faltantes |
| Formato | texto con prefijo `$` y `.` como separador decimal (`"$1.040"`, `"$0.120"`); negativos como `"-$0.016"` |
| Unidad | **no documentada**: no hay factor de escala, así que el gasto no se puede convertir a COP. Se conserva en unidades reportadas (**u**). |
| Estructura | En 17 de 34 meses cada rubro es un porcentaje entero del total mensual → consistente con una asignación de arriba hacia abajo |
| `Team` | exactamente 12,0% del S&M total en 17 meses consecutivos (hasta may-23); desde jun-23 es una serie independiente que sube despacio |
| `PayrollExpenses` | negativo en 5 meses (nov-23, dic-23, feb-24, mar-24, jul-24); después de jun-23 se comporta como partida de ajuste |
| `Freelance` | cero desde may-23 (17 de los últimos 18 meses; excepción: jun-23) |
| Cambio de nivel | S&M total 3,45 u (may-23) → 1,10 u (ago-23), −68%; Paid Media −71% |

### 1.4 Consistencia entre fuentes

- Cada `ID` de Transactions tiene exactamente una industria, y viceversa (100%).
- Los tres archivos cubren los mismos 34 meses (ene-22 → oct-24).
- Ningún cliente está siempre en cero: todos tienen al menos un mes con pago.

---

## 2. Transformaciones

1. **Leer el texto crudo** con `utf-8-sig` (quita el BOM) y conservar cada valor como texto primero, para que la auditoría vea exactamente lo que llegó. Se registra el SHA-256 de cada archivo.
2. **Llave de industria**: eliminar la fila vacía; extraer `N` de `"Cliente N"`; verificar unicidad y cruce completo.
3. **Transactions**: `ID` → entero, `month` → periodo mensual, `amount` → decimal y luego **micro-unidades enteras** (`round(amount × 1.000.000)`), para que las comparaciones de igualdad y orden sean exactas.
4. **Panel**: pivotear a clientes × meses (completo, sin huecos que rellenar). Derivar MRR del mes anterior, banderas de movimiento, valores de movimiento, antigüedad y cohorte (definiciones en §3).
5. **COP**: `paid_mrr_cop = observed_amount × 10.000` (1 micro-unidad = COP 0,01).
6. **Métricas mensuales**: agregar banderas y valores por mes; agregar tasas, percentiles y promedios móviles.
7. **S&M**: quitar `$`, leer decimales con signo, conservar los 7 rubros, agregar grupos analíticos y totales, unir por mes.
8. **Vistas**: industrias, cohortes, correlaciones con rezago, descomposición mix/dentro, puentes y diagnóstico de movimientos.
9. **Validaciones** (el pipeline se detiene si alguna falla):
   - identidad por fila `actual − anterior = Nuevo + Expansión + Reactivación + Contracción + Churn` en cada mes-cliente;
   - el puente mensual de MRR cuadra (residuo máximo = COP 0,00) y el puente de clientes cuadra exactamente;
   - los puentes anuales y el del último mes cuadran;
   - MRR pagado total = suma de montos crudos × 10.000; meses-cliente activos = filas positivas;
   - los cortes por industria suman los totales de la empresa; las banderas de movimiento son mutuamente excluyentes;
   - mix + dentro de Shapley = cambio total (a 1e-6);
   - el registro de afirmaciones (§11);
   - el brain: cada métrica, problema y afirmación que cita una tarjeta existe.

---

## 3. Definiciones

### 3.1 Tres capas separadas

| Capa | Contenido |
|---|---|
| **Observado** | `observed_amount` exactamente como llegó. Nunca se sobrescribe. |
| **Derivado** | `paid_mrr_cop` y cada bandera, tasa y agregado de abajo. Mecánico, documentado y reproducible. |
| **Interpretado** | Solo en texto (HTML y este archivo) y siempre marcado como hipótesis. Nunca se codifica como campo. |

> **Estas categorías describen movimientos del monto pagado observado.** Con los datos actuales no podemos distinguir si una expansión o contracción proviene de uso, plan, pricing, descuento, créditos u otra decisión comercial.

### 3.2 Catálogo de métricas (`brain/semantic/metrics.yaml`)

Fuente única de definiciones para el workspace, estas notas y, después, el agente. Ventana completa = ene-22 → oct-24; ventana limpia = mar-22 → oct-24.

| Métrica | Definición | Fórmula | Ventana |
|---|---|---|---|
| Clientes activos (`active_customers`) | Clientes con MRR pagado mayor que cero en el mes. | `count(cliente) donde paid_mrr_cop > 0` | completa |
| Altas (clientes nuevos) (`new_customers`) | Clientes con MRR pagado mayor que cero en el mes y que nunca antes habían pagado. | `curr > 0 y ningún mes anterior > 0` | limpia |
| Churn observado (clientes) (`churned_customers`) | Clientes que pagaban el mes anterior y este mes pagan cero. Es churn observado, no cancelación confirmada. | `prev > 0 y curr = 0` | limpia |
| Reactivaciones (`reactivated_customers`) | Clientes que vuelven a pagar después de al menos un mes en cero. | `curr > 0, prev = 0 y algún mes anterior > 0` | limpia |
| Altas netas (`net_customer_adds`) | Altas más reactivaciones menos churn observado. Es igual al cambio de clientes activos (validado). | `altas + reactivaciones − churn` | limpia |
| MRR pagado (`total_paid_mrr_cop`) | Suma del monto pagado en el mes, multiplicado por 10.000 para expresarlo en COP. Es monto observado; la lectura "cobrado" es hipótesis. | `Σ amount × 10.000` | completa |
| MRR nuevo (`new_mrr_cop`) | MRR pagado en su primer mes por los clientes nuevos. | `Σ curr en filas de alta` | limpia |
| Expansión (`expansion_mrr_cop`) | Aumento del monto pagado de clientes que ya pagaban (curr > prev > 0). | `Σ (curr − prev) en filas de expansión` | limpia |
| MRR de reactivación (`reactivation_mrr_cop`) | Monto pagado por los clientes que se reactivan en el mes. | `Σ curr en filas de reactivación` | limpia |
| Contracción (`contraction_mrr_cop`) | Disminución del monto pagado de clientes que siguen pagando (0 < curr < prev). Negativo por convención. | `Σ (curr − prev) en filas de contracción` | limpia |
| MRR de churn (`churned_mrr_cop`) | Monto que dejan de pagar los clientes con churn observado. Negativo por convención. | `Σ (−prev) en filas de churn` | limpia |
| Cambio neto de MRR (`net_mrr_change_cop`) | Suma de los cinco movimientos. Es igual al cambio del MRR pagado (validado al centavo). | `nuevo + expansión + reactivación + contracción + churn` | limpia |
| MRR por cliente activo (`mrr_per_active_customer_cop`) | MRR pagado dividido entre clientes activos. | `MRR pagado ÷ clientes activos` | completa |
| Ticket de entrada (M0) (`entry_ticket`) | MRR pagado por un cliente nuevo en su primer mes. Se reporta como promedio (MRR nuevo ÷ altas), mediana y percentiles. | `promedio = MRR nuevo ÷ altas; mediana y P25/P75/P90 sobre los mismos montos` | limpia |
| Churn mensual observado (logos) (`logo_churn_rate`) | Churn observado del mes dividido entre clientes activos del mes anterior. | `churn(t) ÷ activos(t−1)` | limpia |
| MRR por cliente por cosecha (`vintage_arpa`) | MRR pagado de los clientes de una cosecha (año de alta) dividido entre los que siguen activos. | `MRR de la cosecha ÷ activos de la cosecha` | completa |
| Retención de logos de la cohorte (`cohort_logo_retention`) | Porcentaje de la cohorte con MRR pagado mayor que cero en el mes k desde su primer pago. Solo cuenta clientes con al menos k meses de historia. | `activos en Mk ÷ observables en Mk` | limpia |
| Retención de ingreso de la cohorte (`cohort_revenue_retention`) | MRR de la cohorte en el mes k dividido entre el MRR de esos mismos clientes en su primer mes. | `MRR en Mk ÷ MRR en M0 (mismos clientes observables)` | limpia |
| S&M total (`total_sm_spend`) | Suma de los siete rubros del archivo de gasto, en las unidades reportadas. | `PaidMedia + PublicidadNoWeb + Team + PayrollExpenses + Travel + SoftwareTools + Freelance` | completa |
| Generación de demanda (`demand_gen_spend`) | PaidMedia + PublicidadNoWeb. | `PaidMedia + PublicidadNoWeb` | completa |
| Capacidad comercial (`sales_capacity_spend`) | Team + PayrollExpenses + Travel. | `Team + PayrollExpenses + Travel` | completa |
| Habilitación (`enablement_spend`) | SoftwareTools + Freelance. | `SoftwareTools + Freelance` | completa |
| Paid Media (`paid_media`) | Rubro PaidMedia tal como viene en el archivo. | `PaidMedia` | completa |
| Gasto por cliente nuevo (`sm_per_new_customer`) | Gasto del periodo dividido entre las altas del periodo (S&M total, generación de demanda o Paid Media). | `gasto ÷ altas; anual = Σ gasto ÷ Σ altas` | limpia |
| Gasto por COP 1 millón de MRR nuevo (`sm_per_new_mrr_mm`) | Gasto del periodo dividido entre el MRR nuevo del periodo en millones de COP. | `gasto ÷ (MRR nuevo ÷ 1.000.000)` | limpia |

### 3.3 Tabla cliente-mes (`finora_analytical_dataset.csv`)

`actual` = MRR pagado en el mes t; `anterior` = MRR pagado en t−1. Las comparaciones son exactas (micro-unidades).

| Columna | Definición |
|---|---|
| `customer_id` | ID numérico (de `"Cliente N"`) |
| `industry` | industria tal como llegó (fija por cliente) |
| `month`, `month_index` | mes calendario (`AAAA-MM`) y 0…33 |
| `observed_amount` | monto crudo |
| `paid_mrr_cop` | observed_amount × 10.000 |
| `active_customer` | 1 si actual > 0 |
| `previous_month_mrr` | anterior (vacío en ene-22) |
| `mrr_change` | actual − anterior (vacío en ene-22) |
| `first_positive_month` = `cohort_month` | primer mes con actual > 0 |
| `cohort_flag` | `left_censored` (primer pago = ene-22), `suspected_spillover` (feb-22), `clean` |
| `tenure_month` | meses desde el mes de cohorte (M0 = mes de cohorte); vacío antes |
| `movement_type` | uno de: `window_start_active`, `window_start_inactive`, `new`, `expansion`, `contraction`, `flat`, `churn`, `reactivation`, `not_yet_active`, `inactive_after_churn` |
| `new_customer` | actual > 0 y nunca > 0 antes (no identificable en ene-22) |
| `churned_customer` | anterior > 0 y actual = 0 (churn observado) |
| `reactivated_customer` | actual > 0, anterior = 0 y positivo en algún mes previo |
| `expanded_customer` | actual > anterior > 0 |
| `contracted_customer` | 0 < actual < anterior |
| `flat_customer` | actual = anterior > 0 |
| `new_mrr_cop`, `reactivation_mrr_cop` | actual en filas de alta / reactivación |
| `expansion_mrr_cop`, `contraction_mrr_cop` | actual − anterior en filas de expansión (positivo) / contracción (negativo) |
| `churned_mrr_cop` | −anterior en filas de churn (negativo) |
| `months_to_return` | filas de churn: meses hasta el siguiente mes con pago (vacío si no vuelve antes de oct-24) |
| `returned_next_month`, `returned_same_amount_next_month` | filas de churn: 1 si paga en t+1 (con el mismo monto) |
| `reverts_next_month` | filas de expansión/contracción: 1 si el monto de t+1 es igual al anterior (pico o baja de un mes) |
| `usual_amount_cop` | el monto positivo más frecuente del cliente (empates → el menor) |
| `amount_vs_usual_ratio` | actual ÷ monto usual |
| `multi_month_payment_signature` | k (2…12) cuando actual = k × monto usual (±0,5%) y el monto usual aparece ≥ 3 veces; si no, 0 |

Identidad del puente (cada fila con mes anterior): `mrr_change = new + expansion + reactivation + contraction + churned`.

### 3.4 Métricas mensuales adicionales (`finora_monthly_metrics.csv`)

| Métrica | Definición |
|---|---|
| Clientes con expansión / contracción / sin cambio | conteos de las banderas |
| Tasa de churn bruto de MRR / contracción / expansión | movimiento(t) ÷ MRR(t−1) |
| Tasa de reactivación | reactivados(t) ÷ grupo latente(t−1) (inactivos en t−1 pero con pagos antes) |
| Retención neta de MRR (existentes) | (MRR(t−1) + expansión + contracción + churn) ÷ MRR(t−1) |
| Quick ratio | (nuevo + expansión + reactivación) ÷ −(contracción + churn) |
| `window_flag` | `left_censored_start` (ene-22), `suspected_spillover` (feb-22), `clean` |
| `*_3m_avg` | promedios móviles de 3 meses (flujos solo dentro de la ventana limpia) |

### 3.5 Grupos de S&M

| Grupo | Rubros | Razón (hipótesis, no verdad contable) |
|---|---|---|
| Generación de demanda | PaidMedia + PublicidadNoWeb | gasto pensado para crear demanda |
| Capacidad comercial | Team + PayrollExpenses + Travel | personas y capacidad de campo para convertir la demanda |
| Habilitación | SoftwareTools + Freelance | herramientas y apoyo externo |
| S&M total | los siete | tal como llegó |
| S&M total sin PayrollExpenses | total − PayrollExpenses | solo como sensibilidad |

**Por qué se conservan los siete rubros en el S&M total, y cuándo conviene excluir uno.** Nada prueba que un rubro no sea S&M, así que se conservan todos. Hay razones técnicas para probar una alternativa: `PayrollExpenses` tiene 5 meses negativos, se comporta como partida de ajuste después de jun-23 y puede traslaparse con `Team` (de ahí `total_sm_ex_payroll`). `Team` tiene un quiebre de definición en jun-23 (de asignación fija de 12% a serie independiente), así que las tendencias a través de ese mes no son comparables. `Freelance`, `SoftwareTools` y `Travel` pueden incluir costos que no son de S&M; los datos no permiten separarlos.

### 3.6 Eficiencia

Mensual: gasto (u) ÷ altas, y gasto (u) ÷ MRR nuevo en millones de COP, para S&M total, generación de demanda y Paid Media. Las versiones de últimos 3 meses suman tres meses limpios. También se entregan los inversos (altas o MRR nuevo por unidad de gasto). No se calcula en ene-22 (altas no identificables) ni en feb-22 (arrastre); ningún mes limpio tiene denominador cero. Las cifras anuales agregan sumas (Σ gasto ÷ Σ resultado).

### 3.7 Relaciones con rezago

Para gasto ∈ {Paid Media, generación de demanda, S&M total}, resultado ∈ {altas, MRR nuevo} y rezago k ∈ {0, 1, 2, 3}: pares (gasto(t−k), resultado(t)) para los meses de resultado dentro de la ventana limpia (n = 30–32). r de Pearson y ρ de Spearman con valores p, en niveles y en cambios mes a mes (ambas series diferenciadas). La sensibilidad que incluye feb-22 está en `supporting/lag_correlations_incl_feb22.csv`. El lenguaje es solo de asociación.

### 3.8 Descomposición mix vs. efecto dentro

Ticket de entrada promedio `A = Σ sᵢ·aᵢ` (sᵢ = participación de la industria en las altas; aᵢ = MRR promedio del primer mes en la industria). Descomposición de **Shapley (punto medio)** de dos factores, exacta y sin residuo:

- mix = Σ (sᵢ¹ − sᵢ⁰) · (aᵢ⁰ + aᵢ¹)/2
- dentro = Σ (aᵢ¹ − aᵢ⁰) · (sᵢ⁰ + sᵢ¹)/2

La versión de Laspeyres (mix a tasas base, dentro con el mix base, más interacción) se reporta como verificación. Incertidumbre: 2.000 remuestreos bootstrap de las altas dentro de cada periodo (semilla fija) → intervalos de 90%. Variantes: M0 (principal), M0 winsorizado en el P99 conjunto (COP 595,2 mil), run-rate temprano (mediana de los montos positivos en M0–M2). Periodos: 2022 (mar–dic), 2023, 2024 (ene–oct); evolución semestral contra la base 2022.

### 3.9 Cohortes

Cohorte = primer mes con pago. Los 377 clientes activos en ene-22 están censurados a la izquierda y se siguen aparte en tiempo calendario; las altas de feb-22 se marcan. Retención de logos en Mₖ = porcentaje de la cohorte con MRR pagado > 0 en la antigüedad k (foto puntual; un cliente puede volver). Retención de ingreso en Mₖ = MRR de la cohorte en Mₖ ÷ MRR de esos mismos clientes en M0. MRR por cliente original = MRR de la cohorte en Mₖ ÷ clientes observables en Mₖ. Cada Mₖ usa solo clientes con al menos k meses de historia (censura a la derecha). Las cohortes trimestrales agrupan cohortes mensuales; 2022 T1 = solo mar y 2024 T4 = solo oct.

---

## 4. Supuestos explícitos

1. `amount × 10.000 = COP`, como indicó Finora. Se aplica sin cuestionar el factor.
2. Un cliente está **activo** en un mes si y solo si el monto pagado es > 0.
3. **Censura a la izquierda**: los clientes que pagan en ene-22 pudieron entrar antes; no se asigna ningún movimiento a ene-22.
4. **Arrastre**: el 30% de las altas de feb-22 paga exactamente 2 veces su segundo monto (frente a 3,0% en cohortes posteriores) y feb-22 tiene 4,0× el promedio mensual de altas de 2022. Las altas de feb-22 se marcan y se excluyen de tasas de adquisición, correlaciones y tendencias de cohortes. Ventana limpia de flujos: mar-22 → oct-24.
5. **Sin tolerancia** para "sin cambio": cualquier cambio en el monto pagado cuenta como expansión o contracción.
6. **La industria es fija** por cliente.
7. **Unidad de S&M desconocida**: se conserva como viene; las razones de eficiencia son relativas en el tiempo, no un CAC en COP.
8. El papel de cada grupo de S&M (qué representan Team, Travel y Freelance) es una hipótesis.
9. **Los valores extremos se conservan**; su influencia se prueba (variantes winsorizadas y medianas).
10. **Censura a la derecha**: el churn cercano a oct-24 puede ser temporal; "sin volver a oct-24" está censurado.

---

## 5. Anomalías y patrones contraintuitivos (investigados antes de reportarse)

1. **`amount` se comporta como cobro mensual, no como MRR contratado.** 512 meses-cliente (325 clientes) equivalen a 2–12 veces el monto usual del cliente; 44% de 751 churns observados vuelven al mes siguiente (62% en algún momento); el 29% del MRR de expansión se revierte al mes siguiente; el 13% del MRR de contracción es el regreso a lo normal después de un pico de un mes. Ejemplos en el HTML (clientes 14, 40, 516 y 637).
2. **Arrastre de feb-22** (supuesto 4).
3. **Escalón del ticket de entrada en ene-23**: desde ene-23, cada mediana mensual del ticket de entrada está por debajo de la mediana de 2022 (COP 63,0 mil). Promedio COP 128,7 mil (2022) → COP 50,8 mil (2024); mediana COP 63,0 mil → COP 42,0 mil.
4. **Picos del primer mes en 2022**: el 15% de las altas de 2022 pagó en M0 más de 1,5 veces su segundo mes (4% en 2023, 9% en 2024) → el ticket promedio de 2022 y la retención de ingreso de 2022 basada en M0 están distorsionados. Las métricas robustas achican la caída (−18% a −60% según la métrica), pero nunca la invierten.
5. **Gasto abajo, adquisición arriba**: el S&M total cayó 68% (may-23 → ago-23) mientras las altas por mes pasaban de 27 (2022) a 54 (2023) y 55 (2024).
6. **Correlación negativa en niveles** entre gasto y altas (S&M total, rezago 0: r = −0,57); desaparece en cambios mes a mes (|r| máximo = 0,27).
7. **Archivo de S&M construido de arriba hacia abajo** (participaciones en porcentajes enteros; Team fijo en 12% hasta may-23; Freelance → 0 cuando Team salta en jun-23; PayrollExpenses negativo).
8. **Ajustes pequeños y montos fuera de la grilla**: las expansiones menores a 10% pasaron de 9% (2022 S1) a 75% (2024 S2); las contracciones, de 9% a 56%. Porcentaje de montos pagados en la grilla de COP 2.100: 81% (2022 S2) → 58% (2024 S2).
9. **Concentración arriba**: la cuenta más grande (cliente 94, Restaurantes) paga una mediana de COP 3,1 millones al mes, 60× la mediana de los meses-cliente; algunos clientes muestran pagos grandes periódicos (por ejemplo, COP 2,14 millones aproximadamente una vez al año).
10. **El MRR mensual es ruidoso**: cayó frente al mes anterior en 10 de 33 meses (por ejemplo, −20% en jun-22) mientras los clientes seguían creciendo; los movimientos brutos (COP 404 millones) son 6,5× el cambio neto (COP 62 millones).
11. **Caso CFO: contracción o descuento.** El puente actual no puede distinguir una contracción del cliente de un descuento, ni una expansión real de un descuento que vence. Para separar las tres capas (negocio subyacente, decisión comercial y cobro) se necesitarían seis campos por cliente y mes: `list_mrr`, `recurring_discount`, `temporary_discount`, `temporary_discount_end`, `credits` y `subscription_status` (tarjeta 9.6 del workspace).

---

## 6. Hallazgos descriptivos por dominio

**Resultado.** Clientes activos 377 → 1.678 (4,5×); MRR pagado COP 35,0 millones → COP 97,0 millones (2,8×); MRR por cliente activo COP 92,8 mil → COP 57,8 mil (−38%). Altas netas positivas en 32 de 33 meses (negativas solo en jun-22). Cambio neto anual del MRR: 2022 COP 27,4 millones, 2023 COP 15,5 millones, 2024 COP 19,1 millones.

**Adquisición.** Altas por mes: 27 (2022), 54 (2023), 55 (2024). El ticket de entrada bajó desde ene-23; el 97% de la caída del promedio ocurre dentro de las industrias.

**Monetización de la base.** Los clientes activos en ene-22 conservaron su MRR por cliente (COP 92,8 mil → COP 97,4 mil). En oct-24, MRR por cliente por cosecha: 2022 COP 65,4 mil, 2023 COP 46,3 mil, 2024 COP 43,0 mil. Las cosechas 2023–24 son 65% de los clientes activos y 50% del MRR.

**Retención.** Retención de logos al M1: trimestres de 2022 89%–95%; trimestres completos de 2023–24 95%–98%. Retención de logos al M12: 83%–91%. Retención de ingreso al M1: trimestres de 2022 ≤ 47% (picos en M0); 2023–24 ≥ 80%. Base previa: el 79% sigue pagando en oct-24 y conserva el 83% de su MRR de ene-22. Churn mensual de logos observado: 3,5% (2022), 2,2% (2023), 1,9% (2024).

**Inversión comercial.** S&M total mensual promedio: 2022 2,87 u, 2023 2,09 u, 2024 1,98 u (−31% frente a 2022). S&M total por alta: 0,105 u → 0,039 u → 0,036 u (−66%); por COP 1 millón de MRR nuevo: 0,82 u → 0,81 u → 0,70 u (−14%).

**Gasto y adquisición.** Niveles contra altas: r de −0,60 a −0,26 (todas negativas). Niveles contra MRR nuevo: |r| ≤ 0,14. Cambios mes a mes: |r| ≤ 0,27, menor p = 0,14. 9 de 48 pruebas tienen p < 0,05 (2,4 esperadas solo por azar); las 9 son correlaciones negativas en niveles con las altas.

**Industrias.** Participación de Retail en las altas: 18% (2022) → 26% (2023) → 24% (2024); ticket de entrada de Retail en 2024: COP 36,9 mil. Participación de Restaurantes en el MRR: 39% (dic-22) → 32% (oct-24). El ticket de entrada promedio bajó en 6 de 6 industrias entre 2022 y 2024 (la mediana, en 6 de 6); el MRR por cliente activo bajó en 6 de 6 entre dic-22 y oct-24.

**Mix vs. efecto dentro.** Ticket de entrada promedio 2022 → 2024: COP 128,7 mil → COP 50,8 mil (−60%). Dentro de las industrias −COP 75,4 mil (97%); mix −COP 2,4 mil (3%); intervalo de 90% de la parte "dentro": 91–102%; 96%–97% entre variantes. Con el mix de 2022, el ticket de 2024 habría sido COP 52,1 mil. Parte "dentro" 2022 → 2023: 95%. 2023 → 2024: COP 2,9 mil (intervalo de 90% del efecto dentro: −COP 3,2 mil a COP 6,9 mil).

**Movimientos de MRR.** sep-24 → oct-24: COP 92,7 millones + COP 2,2 millones de altas + COP 2,1 millones de expansión + COP 4,5 millones de reactivación − COP 2,1 millones de contracción − COP 2,3 millones de churn = COP 97,0 millones (residuo COP 0,00).

---

## 7. Lo que sabemos · sospechamos · no podemos saber

**Sabemos**: el panel está completo y es consistente; clientes 4,5× frente a MRR 2,8×; las altas por mes se duplicaron y el MRR nuevo por mes no; el ticket de entrada bajó en ene-23 en todas las industrias y el 97% de la caída ocurre dentro de ellas; la base de ene-22 conservó su MRR por cliente; el S&M cayó con fuerza a mitad de 2023 mientras la adquisición subía; gasto y adquisición no se asocian positivamente en ningún rezago probado; las cohortes recientes retienen igual o mejor al inicio; el 44% de los churns observados vuelve al mes siguiente; todos los puentes cuadran.

**Sospechamos** (por validar): `amount` es el monto cobrado o facturado por mes; parte de las altas de feb-22 son clientes previos que regresan; el escalón de ene-23 es consistente con un cambio de precios o empaquetamiento, descuentos o clientes más pequeños dentro de cada industria; el aumento de altas en el segundo semestre de 2023 es consistente con canales fuera del archivo de S&M, rezagos de más de tres meses o un precio de entrada menor; el archivo de S&M se asignó de arriba hacia abajo y Freelance se reclasificó a Team; los ajustes pequeños son consistentes con indexación, descuentos, prorrateos o componentes por uso; los picos del primer mes en 2022 son cargos de instalación o prepagos.

**No podemos saber** (no está en los archivos; nunca se rellena con supuestos): etapas del funnel (New → Working → Engaged → SQL → Demo → Proposal → Won) y su conversión; fechas por etapa, speed to lead, tiempo de respuesta, velocidad de cierre; fuente del lead y atribución; SDR o AE dueño; venta self-serve frente a asistida; precios, planes, precio de lista frente a pagado, valor del contrato o suscripción, frecuencia de facturación; descuentos, promociones y créditos; motivos de churn, downgrade o reactivación; si `amount` es facturado, cobrado o contratado; la unidad y las reglas de asignación del S&M; tamaño o geografía del cliente; la historia antes de ene-22 y después de oct-24.

---

## 8. Problemas de datos conocidos (`brain/data/known_quality_issues.yaml`)

| ID | Problema | Estado | Tratamiento |
|---|---|---|---|
| `CV-AMOUNT-COBRO` | `amount` se comporta como monto cobrado, no como MRR contractual | Hipótesis | Se mantienen las definiciones pedidas y se marca la ambigüedad. El modelo en tres capas (arquitectura §10) es la solución de fondo. |
| `CV-VENTANA` | Ventana limpia de flujos desde mar-22 | Hecho observado | Ene-22 sin movimientos; feb-22 marcado y excluido de tasas; sombreado común en las gráficas mensuales. |
| `CV-CHURN-PAUSAS` | El churn observado incluye pausas y atrasos | Hecho observado | Se reporta como churn observado; para proyecciones se necesita churn neto de retornos. |
| `CV-M0-PICOS-2022` | El ticket de entrada de 2022 incluye pagos iniciales grandes | Hecho observado | Se muestran variantes robustas (mediana, winsorizado, run-rate temprano). |
| `CV-OUTLIERS` | Montos extremos y concentración en pocas cuentas | Hecho observado | Se conservan (son montos reales) y se prueba su influencia. |
| `CV-SM-UNIDAD` | La unidad del gasto de S&M no está documentada | Hecho observado | Se reportan en unidades (u); las eficiencias son comparables en el tiempo, no un CAC en pesos. |
| `CV-SM-ASIGNACION` | El archivo de S&M parece construido de arriba hacia abajo | Hipótesis | Los rubros no son mediciones independientes antes de jun-23; se leen como asignación. |
| `CV-PAYROLL-NEG` | PayrollExpenses es negativo en algunos meses | Hecho observado | Se incluye en el total y se ofrece la serie de sensibilidad sin Payroll. |
| `CV-FREELANCE-CERO` | Freelance en cero desde may-23 | Hecho observado | Se conserva; la lectura de reclasificación es hipótesis. |
| `CV-SIN-FUNNEL` | No hay funnel, atribución, precios ni descuentos | No evaluable | Toda hipótesis que los requiera se marca No evaluable. |

---

## 9. Preguntas que surgieron (para Finora)

Fuente: `brain/business/stakeholder_questions.yaml`.

1. ¿Qué es exactamente `amount`: monto facturado, cobrado o MRR contratado? ¿Los planes bimestrales, anuales o prepagados se cobran por adelantado?
2. ¿Qué cambió en ene-23: lista de precios, empaquetamiento, un plan de entrada nuevo, descuentos, un canal o segmento nuevo?
3. ¿Cuál es la unidad de S&M_spend y cómo se definen Team, PayrollExpenses y Freelance? ¿Por qué Team es 12% del total hasta may-23?
4. ¿Hubo actividades de adquisición fuera de este archivo (alianzas, referidos, orgánico, eventos) en el segundo semestre de 2023?
5. ¿Los PayrollExpenses negativos son reversos de provisiones anteriores?
6. ¿Un mes en cero seguido de un pago doble es un cobro atrasado, una pausa o un ciclo de facturación? ¿Debe contar como churn?
7. ¿Los clientes que entran en feb-22 tienen fecha de inicio de contrato anterior a 2022?
8. ¿Qué descuentos temporales se planean (caso CFO) y cómo aparecerían en `amount`?
9. ¿Existe algún atributo del cliente además de la industria (tamaño, plan, ciudad, canal) que se pueda cruzar por ID?

---

## 10. Limitaciones

- **Series cortas.** 34 meses; las correlaciones usan n = 30–32. Las series tienen autocorrelación y tendencia, lo que infla las correlaciones en niveles; los cambios mes a mes son la lectura más estricta.
- **Pruebas múltiples.** 48 pruebas de correlación → cerca de 2,4 con p < 0,05 esperadas por azar.
- **Semántica de `amount`.** Si es cobro y no MRR contratado, cada categoría de movimiento mezcla eventos comerciales con el timing del cobro.
- **Censura.** A la izquierda (adquisición antes de ene-22 desconocida; arrastre hacia feb-22) y a la derecha (el churn reciente puede ser temporal; las cohortes tardías tienen historias cortas).
- **Segmentación.** La industria es el único atributo; los efectos "dentro de la industria" pueden esconder efectos de mix en dimensiones no observadas (tamaño, plan, canal).
- **Datos de S&M.** Unidad desconocida, construcción tipo asignación, quiebre de definición en jun-23, meses de nómina negativos.
- **Sin identificación causal.** Nada aquí separa el efecto del gasto, el precio o el producto de otros cambios que ocurrieron al mismo tiempo.

---

## 11. Afirmaciones verificadas (aserciones en `finora_eda.py`)

Cada título con conclusión del workspace está respaldado por una de estas verificaciones. Si los datos cambian y una afirmación deja de ser cierta, el pipeline se detiene en lugar de publicarla. El registro también se escribe en `brain/evidence/canonical_findings.yaml` con `revision_humana: pendiente`.

| ID | Dominio | Estado | Afirmación | Verificación |
|---|---|---|---|---|
| `C-RES-01` | Resultado | Hecho observado | Los clientes activos crecieron más rápido que el MRR pagado entre ene-22 y oct-24. | ✅ verificado |
| `C-RES-02` | Resultado | Hecho observado | El MRR por cliente activo de oct-24 es más de 30% menor que el de ene-22. | ✅ verificado |
| `C-RES-03` | Resultado | Hecho observado | Las altas netas fueron negativas en un solo mes. | ✅ verificado |
| `C-RES-04` | Resultado | Hecho observado | Los movimientos brutos de MRR superan 5 veces el cambio neto del periodo. | ✅ verificado |
| `C-RES-05` | Resultado | Hecho observado | En el último mes, la reactivación fue la mayor entrada de MRR. | ✅ verificado |
| `C-RES-06` | Resultado | Hecho observado | Restaurantes sigue siendo el mayor bloque de MRR, con menor participación en oct-24 que en dic-22. | ✅ verificado |
| `C-RES-07` | Resultado | Hecho observado | Retail tiene mayor participación en los clientes activos en oct-24 que en dic-22. | ✅ verificado |
| `C-ADQ-01` | Adquisición | Hecho observado | La mediana del ticket de entrada es menor en 2023 y en 2024 que en 2022. | ✅ verificado |
| `C-ADQ-02` | Adquisición | Hecho observado | Todas las métricas de ticket de entrada (promedio, mediana, winsorizado, run-rate temprano y M1) son menores en 2024 que en 2022. | ✅ verificado |
| `C-ADQ-03` | Adquisición | Hecho observado | El mes del escalón (desde el cual toda mediana mensual del ticket queda bajo la de 2022) cae en el primer trimestre de 2023. | ✅ verificado |
| `C-ADQ-04` | Adquisición | Evidencia fuerte | El efecto dentro de las industrias explica más de 80% del cambio del ticket 2022→2024 en las tres variantes, y el límite inferior del intervalo bootstrap de 90% supera 50%. | ✅ verificado |
| `C-ADQ-05` | Adquisición | Hecho observado | El ticket de entrada (promedio y mediana) bajó en las seis industrias entre 2022 y 2024. | ✅ verificado |
| `C-ADQ-06` | Adquisición | Hecho observado | Restaurantes y Producción aportan más de la mitad del MRR nuevo en cada año. | ✅ verificado |
| `C-RET-01` | Retención | Hecho observado | La menor retención de logos al M1 entre los trimestres completos de 2023–24 supera la mayor entre los trimestres completos de 2022. | ✅ verificado |
| `C-RET-02` | Retención | Hecho observado | Más de 40% de los churns observados vuelve a pagar al mes siguiente. | ✅ verificado |
| `C-MON-01` | Monetización de la base | Hecho observado | El MRR por cliente de la base previa en oct-24 está dentro de ±10% del de ene-22. | ✅ verificado |
| `C-MON-02` | Monetización de la base | Hecho observado | En oct-24, las cosechas 2023 y 2024 tienen menor MRR por cliente que la cosecha 2022 y que la base previa. | ✅ verificado |
| `C-MON-03` | Monetización de la base | Hecho observado | El MRR por cliente original de las cohortes 2023 está por debajo del de las cohortes 2022 en M1, M6 y M12. | ✅ verificado |
| `C-MON-04` | Monetización de la base | Evidencia fuerte | Los clientes existentes no pagan menos y las cosechas 2023–24, de menor ticket, ya son la mayoría de los clientes activos. | ✅ verificado |
| `C-MON-05` | Monetización de la base | Hecho observado | El MRR por cliente activo bajó en las seis industrias entre dic-22 y oct-24. | ✅ verificado |
| `C-INV-01` | Inversión comercial | Hecho observado | El S&M total cayó más de 60% entre su pico y su valle de 2023. | ✅ verificado |
| `C-INV-02` | Inversión comercial | Hecho observado | El S&M total por cliente nuevo es más de 50% menor en 2024 que en 2022. | ✅ verificado |
| `C-INV-03` | Inversión comercial | Direccional | Las correlaciones en niveles entre gasto y altas (rezagos 0–1) son todas negativas, y ninguna correlación de cambios mes a mes alcanza \|r\| ≥ 0,3 ni p < 0,05. | ✅ verificado |
| `C-INV-04` | Inversión comercial | Direccional | Toda correlación con p < 0,05 es una correlación negativa en niveles con las altas. | ✅ verificado |
| `C-DAT-01` | Datos | Hecho observado | Team equivale a 12,0% del S&M total en todos los meses hasta may-23. | ✅ verificado |
| `C-DAT-02` | Datos | Hecho observado | Las altas de feb-22 muestran la firma de pago doble a más de 5 veces la tasa conjunta de las cohortes posteriores. | ✅ verificado |
| `C-DAT-03` | Datos | Hecho observado | Más de 25% del MRR de expansión se revierte al mes siguiente. | ✅ verificado |
| `C-DAT-04` | Datos | Hecho observado | Los ajustes menores a 10% pasaron de menos de 15% a más de 60% de los eventos de expansión entre el primer y el último semestre. | ✅ verificado |
| `C-DAT-05` | Datos | Hecho observado | La proporción de meses-cliente activos con montos fuera de la grilla de COP 2.100 es mayor en 2024 S2 que en 2022 S2. | ✅ verificado |
| `C-ADQ-07` | Adquisición | Hecho observado | El aumento de altas por mes entre 2022 y 2024 corresponde a clientes con run-rate inicial menor que la mediana de 2022; por encima de esa mediana, las altas por mes no aumentaron. | ✅ verificado |
| `C-RES-08` | Resultado | Hecho observado | Todo el aumento del monto pagado entre ene-22 y oct-24 proviene de clientes que empezaron a pagar después de ene-22; los clientes activos en ene-22 terminan con menos monto que al inicio. | ✅ verificado |
| `C-DAT-06` | Datos | Hecho observado | Más de 20% del movimiento bruto del monto pagado entre mar-22 y sep-24, sin contar altas, se revierte exactamente al nivel previo al mes siguiente. | ✅ verificado |
| `C-RET-03` | Retención | Hecho observado | El churn observado bajó más de un punto entre 2022 y 2024, mientras el churn que no vuelve a pagar en tres meses cambió menos de 0,3 puntos. | ✅ verificado |
| `C-DAT-07` | Datos | Hecho observado | Más de 200 clientes muestran un ajuste sincronizado con cobro retroactivo exacto: el monto sube k veces un porcentaje y al mes siguiente queda en ese porcentaje. | ✅ verificado |
| `C-DAT-08` | Datos | Hecho observado | Más de 25% de los retornos después de meses sin pago liquidan exactamente los meses pendientes (±1%). | ✅ verificado |
| `C-DAT-09` | Datos | Hecho observado | En jun-22 los churns observados fueron más del doble de la mediana mensual y más de 70% volvió a pagar al mes siguiente. | ✅ verificado |
| `C-ADQ-08` | Adquisición | Hecho observado | El valor inicial incorporado por mes creció menos que las altas entre 2022 y 2024 en las tres normalizaciones probadas, y entre 2023 y 2024 cambió menos de 10% en todas. | ✅ verificado |
| `C-RET-04` | Retención | Direccional | En las cohortes de 2023, la retención de logos al M12 de las altas bajo la mediana de 2022 está a menos de 5 puntos de la de las altas por encima. | ✅ verificado |
| `C-ADQ-09` | Adquisición | Direccional | Las altas por mes se duplicaron con un escalón a inicios de 2023 y desde ene-23 no muestran una tendencia distinguible de cero. | ✅ verificado |

---

## 12. Reproducibilidad

- Comando: `python3 finora_eda.py` (opcional: `--raw-dir`, `--out-dir`).
- Entorno: Python 3.13.7, pandas 3.0.3, numpy 2.4.4, scipy 1.17.1, PyYAML. Semilla del bootstrap fija.
- SHA-256 de las entradas:
  - `Transactions.csv` `2dcbe59e9ac497c441f3c019963b11e9848ce4916e5773d257a36f83d953ae95`
  - `Industry.csv` `b4330fc6d7df60429849b3b176746f5389c65931f281308eb8224c8efd440ff5`
  - `S&M_spend.csv` `41fbb6499f2b0ad4565ccc0e96ec490c72599e15fd46d64086fd98e3443c4c13`
