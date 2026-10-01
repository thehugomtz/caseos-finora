# Finora · Fase 1 · Notas de trabajo del análisis exploratorio

> **Entender primero. Explicar después. Decidir al final.**
> Este documento describe qué contienen los datos y cómo se comportan. No diagnostica los problemas del CRO ni del CFO.

Generado el {{generated}} por `finora_eda.py`. Cada cifra se recalcula desde los archivos crudos; ninguna se escribe a mano.

---

## 0. Entregables

| Archivo | Qué es |
|---|---|
| `finora_eda.html` | Workspace de exploración autocontenido. Solo usa Google Fonts de forma opcional; abre sin conexión. |
| `finora_analytical_dataset.csv` | Tabla analítica cliente-mes: {{n_rows_tx}} filas, una por cliente y mes. |
| `finora_monthly_metrics.csv` | Métricas mensuales de la empresa: clientes, puente de MRR, valor, tasas, rubros y grupos de S&M, eficiencia. |
| `finora_eda_notes.md` | Este archivo: definiciones, transformaciones, supuestos, anomalías, preguntas y limitaciones. |
| `finora_eda.py` | Pipeline reproducible (Python {{py_version}} · pandas {{pandas_version}} · numpy {{numpy_version}} · scipy {{scipy_version}}). |
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
| Filas | {{n_rows_tx}} = {{n_customers}} clientes × {{n_months}} meses → **panel completo y balanceado** |
| Grano | una fila por cliente y mes calendario (`month` es una fecha de fin de mes en texto `M/D/AAAA`) |
| Rango de fechas | {{window_start}} → {{window_end}} |
| Duplicados | 0 en (`ID`, `month`); 0 filas completas duplicadas |
| Faltantes o ilegibles | 0 |
| Montos negativos | 0 |
| Montos en cero | {{zero_rows}} filas ({{zero_share}}): los meses inactivos vienen como ceros explícitos |
| Montos positivos | {{pos_rows}} filas; rango {{amount_min_cop}} a {{amount_max_cop}}; mediana {{amount_p50_cop}}; P99 {{amount_p99_cop}} |
| Valores extremos | {{rows_above_fence}} meses-cliente ({{customers_above_fence}} clientes) por encima de Q3 + 3·RIC ({{iqr_fence_cop}}). Se conservan. |
| Precisión | hasta 6 decimales ({{rows_6_decimals}} filas con 6 decimales) → se comparan exactamente como micro-unidades enteras |
| Nombre | el archivo se llama “Transactions”, pero el grano es una foto mensual por cliente |

### 1.2 `Industry.csv`

| Revisión | Resultado |
|---|---|
| Columnas | `ID`, `Industria` (UTF-8 con BOM; encabezados en dos idiomas) |
| Filas | {{ind_rows_read}} leídas → se elimina {{ind_blank_rows}} fila final completamente vacía → {{ind_valid}} |
| Llave | `"Cliente N"` → `N` (regex `^Cliente (\d+)$`); única; contigua de 1 a {{ind_valid}} |
| Valores | {{n_industries}} industrias sin variantes de mayúsculas, acentos ni espacios: Restaurantes, Producción, Retail, Tecnología, Servicios profesionales, Salud |
| Cruce con Transactions | {{id_match_rate}} en ambos sentidos, sin excepciones |

### 1.3 `S&M_spend.csv`

| Revisión | Resultado |
|---|---|
| Columnas | `Month` (`AAAA-MM`) + `PaidMedia`, `Travel`, `PublicidadNoWeb`, `Freelance`, `SoftwareTools`, `Team`, `PayrollExpenses` |
| Filas | 34 meses, idénticos a los de Transactions; sin duplicados ni faltantes |
| Formato | texto con prefijo `$` y `.` como separador decimal (`"$1.040"`, `"$0.120"`); negativos como `"-$0.016"` |
| Unidad | **no documentada**: no hay factor de escala, así que el gasto no se puede convertir a COP. Se conserva en unidades reportadas (**u**). |
| Estructura | En {{whole_pct_months}} de 34 meses cada rubro es un porcentaje entero del total mensual → consistente con una asignación de arriba hacia abajo |
| `Team` | exactamente 12,0% del S&M total en {{team_fixed_months}} meses consecutivos (hasta {{team_fixed_until}}); desde {{team_break}} es una serie independiente que sube despacio |
| `PayrollExpenses` | negativo en {{payroll_neg_n}} meses ({{payroll_neg_list}}); después de {{team_break}} se comporta como partida de ajuste |
| `Freelance` | cero desde {{freelance_zero_from}} ({{freelance_zero_n}} de los últimos {{freelance_months_since}} meses; excepción: {{freelance_exceptions}}) |
| Cambio de nivel | S&M total {{sm_peak}} ({{sm_peak_month}}) → {{sm_trough}} ({{sm_trough_month}}), {{sm_drop}}; Paid Media {{pm_drop}} |

### 1.4 Consistencia entre fuentes

- Cada `ID` de Transactions tiene exactamente una industria, y viceversa ({{id_match_rate}}).
- Los tres archivos cubren los mismos 34 meses ({{window_start}} → {{window_end}}).
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
   - el puente mensual de MRR cuadra (residuo máximo = COP {{bridge_max_diff}}) y el puente de clientes cuadra exactamente;
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

Fuente única de definiciones para el workspace, estas notas y, después, el agente. Ventana completa = {{window_start}} → {{window_end}}; ventana limpia = mar-22 → {{window_end}}.

| Métrica | Definición | Fórmula | Ventana |
|---|---|---|---|
<!--METRICS-->

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
| `previous_month_mrr` | anterior (vacío en {{window_start}}) |
| `mrr_change` | actual − anterior (vacío en {{window_start}}) |
| `first_positive_month` = `cohort_month` | primer mes con actual > 0 |
| `cohort_flag` | `left_censored` (primer pago = {{window_start}}), `suspected_spillover` (feb-22), `clean` |
| `tenure_month` | meses desde el mes de cohorte (M0 = mes de cohorte); vacío antes |
| `movement_type` | uno de: `window_start_active`, `window_start_inactive`, `new`, `expansion`, `contraction`, `flat`, `churn`, `reactivation`, `not_yet_active`, `inactive_after_churn` |
| `new_customer` | actual > 0 y nunca > 0 antes (no identificable en {{window_start}}) |
| `churned_customer` | anterior > 0 y actual = 0 (churn observado) |
| `reactivated_customer` | actual > 0, anterior = 0 y positivo en algún mes previo |
| `expanded_customer` | actual > anterior > 0 |
| `contracted_customer` | 0 < actual < anterior |
| `flat_customer` | actual = anterior > 0 |
| `new_mrr_cop`, `reactivation_mrr_cop` | actual en filas de alta / reactivación |
| `expansion_mrr_cop`, `contraction_mrr_cop` | actual − anterior en filas de expansión (positivo) / contracción (negativo) |
| `churned_mrr_cop` | −anterior en filas de churn (negativo) |
| `months_to_return` | filas de churn: meses hasta el siguiente mes con pago (vacío si no vuelve antes de {{window_end}}) |
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
| `window_flag` | `left_censored_start` ({{window_start}}), `suspected_spillover` (feb-22), `clean` |
| `*_3m_avg` | promedios móviles de 3 meses (flujos solo dentro de la ventana limpia) |

### 3.5 Grupos de S&M

| Grupo | Rubros | Razón (hipótesis, no verdad contable) |
|---|---|---|
| Generación de demanda | PaidMedia + PublicidadNoWeb | gasto pensado para crear demanda |
| Capacidad comercial | Team + PayrollExpenses + Travel | personas y capacidad de campo para convertir la demanda |
| Habilitación | SoftwareTools + Freelance | herramientas y apoyo externo |
| S&M total | los siete | tal como llegó |
| S&M total sin PayrollExpenses | total − PayrollExpenses | solo como sensibilidad |

**Por qué se conservan los siete rubros en el S&M total, y cuándo conviene excluir uno.** Nada prueba que un rubro no sea S&M, así que se conservan todos. Hay razones técnicas para probar una alternativa: `PayrollExpenses` tiene {{payroll_neg_n}} meses negativos, se comporta como partida de ajuste después de {{team_break}} y puede traslaparse con `Team` (de ahí `total_sm_ex_payroll`). `Team` tiene un quiebre de definición en {{team_break}} (de asignación fija de 12% a serie independiente), así que las tendencias a través de ese mes no son comparables. `Freelance`, `SoftwareTools` y `Travel` pueden incluir costos que no son de S&M; los datos no permiten separarlos.

### 3.6 Eficiencia

Mensual: gasto (u) ÷ altas, y gasto (u) ÷ MRR nuevo en millones de COP, para S&M total, generación de demanda y Paid Media. Las versiones de últimos 3 meses suman tres meses limpios. También se entregan los inversos (altas o MRR nuevo por unidad de gasto). No se calcula en {{window_start}} (altas no identificables) ni en feb-22 (arrastre); ningún mes limpio tiene denominador cero. Las cifras anuales agregan sumas (Σ gasto ÷ Σ resultado).

### 3.7 Relaciones con rezago

Para gasto ∈ {Paid Media, generación de demanda, S&M total}, resultado ∈ {altas, MRR nuevo} y rezago k ∈ {0, 1, 2, 3}: pares (gasto(t−k), resultado(t)) para los meses de resultado dentro de la ventana limpia (n = {{corr_n_min}}–{{corr_n_levels}}). r de Pearson y ρ de Spearman con valores p, en niveles y en cambios mes a mes (ambas series diferenciadas). La sensibilidad que incluye feb-22 está en `supporting/lag_correlations_incl_feb22.csv`. El lenguaje es solo de asociación.

### 3.8 Descomposición mix vs. efecto dentro

Ticket de entrada promedio `A = Σ sᵢ·aᵢ` (sᵢ = participación de la industria en las altas; aᵢ = MRR promedio del primer mes en la industria). Descomposición de **Shapley (punto medio)** de dos factores, exacta y sin residuo:

- mix = Σ (sᵢ¹ − sᵢ⁰) · (aᵢ⁰ + aᵢ¹)/2
- dentro = Σ (aᵢ¹ − aᵢ⁰) · (sᵢ⁰ + sᵢ¹)/2

La versión de Laspeyres (mix a tasas base, dentro con el mix base, más interacción) se reporta como verificación. Incertidumbre: 2.000 remuestreos bootstrap de las altas dentro de cada periodo (semilla fija) → intervalos de 90%. Variantes: M0 (principal), M0 winsorizado en el P99 conjunto ({{winsor_cap}}), run-rate temprano (mediana de los montos positivos en M0–M2). Periodos: 2022 (mar–dic), 2023, 2024 (ene–oct); evolución semestral contra la base 2022.

### 3.9 Cohortes

Cohorte = primer mes con pago. Los {{base_size}} clientes activos en {{window_start}} están censurados a la izquierda y se siguen aparte en tiempo calendario; las altas de feb-22 se marcan. Retención de logos en Mₖ = porcentaje de la cohorte con MRR pagado > 0 en la antigüedad k (foto puntual; un cliente puede volver). Retención de ingreso en Mₖ = MRR de la cohorte en Mₖ ÷ MRR de esos mismos clientes en M0. MRR por cliente original = MRR de la cohorte en Mₖ ÷ clientes observables en Mₖ. Cada Mₖ usa solo clientes con al menos k meses de historia (censura a la derecha). Las cohortes trimestrales agrupan cohortes mensuales; 2022 T1 = solo mar y 2024 T4 = solo oct.

---

## 4. Supuestos explícitos

1. `amount × 10.000 = COP`, como indicó Finora. Se aplica sin cuestionar el factor.
2. Un cliente está **activo** en un mes si y solo si el monto pagado es > 0.
3. **Censura a la izquierda**: los clientes que pagan en {{window_start}} pudieron entrar antes; no se asigna ningún movimiento a {{window_start}}.
4. **Arrastre**: el {{feb_sig_share}} de las altas de feb-22 paga exactamente 2 veces su segundo monto (frente a {{later_sig_share}} en cohortes posteriores) y feb-22 tiene {{feb_vs_typical_new}} el promedio mensual de altas de 2022. Las altas de feb-22 se marcan y se excluyen de tasas de adquisición, correlaciones y tendencias de cohortes. Ventana limpia de flujos: mar-22 → {{window_end}}.
5. **Sin tolerancia** para "sin cambio": cualquier cambio en el monto pagado cuenta como expansión o contracción.
6. **La industria es fija** por cliente.
7. **Unidad de S&M desconocida**: se conserva como viene; las razones de eficiencia son relativas en el tiempo, no un CAC en COP.
8. El papel de cada grupo de S&M (qué representan Team, Travel y Freelance) es una hipótesis.
9. **Los valores extremos se conservan**; su influencia se prueba (variantes winsorizadas y medianas).
10. **Censura a la derecha**: el churn cercano a {{window_end}} puede ser temporal; "sin volver a oct-24" está censurado.

---

## 5. Anomalías y patrones contraintuitivos (investigados antes de reportarse)

1. **`amount` se comporta como cobro mensual, no como MRR contratado.** {{multi_sig_rows}} meses-cliente ({{multi_sig_customers}} clientes) equivalen a 2–12 veces el monto usual del cliente; {{churn_back_1m}} de {{churn_events}} churns observados vuelven al mes siguiente ({{churn_back_any}} en algún momento); el {{exp_mrr_revert}} del MRR de expansión se revierte al mes siguiente; el {{con_mrr_post_spike}} del MRR de contracción es el regreso a lo normal después de un pico de un mes. Ejemplos en el HTML (clientes 14, 40, 516 y 637).
2. **Arrastre de feb-22** (supuesto 4).
3. **Escalón del ticket de entrada en {{step_month}}**: desde {{step_month}}, cada mediana mensual del ticket de entrada está por debajo de la mediana de 2022 ({{m0_median_2022}}). Promedio {{m0_mean_2022}} (2022) → {{m0_mean_2024}} (2024); mediana {{m0_median_2022}} → {{m0_median_2024}}.
4. **Picos del primer mes en 2022**: el {{spike_share_2022}} de las altas de 2022 pagó en M0 más de 1,5 veces su segundo mes ({{spike_share_2023}} en 2023, {{spike_share_2024}} en 2024) → el ticket promedio de 2022 y la retención de ingreso de 2022 basada en M0 están distorsionados. Las métricas robustas achican la caída ({{m1_mean_chg_22_24}} a {{m0_mean_chg_22_24}} según la métrica), pero nunca la invierten.
5. **Gasto abajo, adquisición arriba**: el S&M total cayó {{sm_drop_abs}} ({{sm_peak_month}} → {{sm_trough_month}}) mientras las altas por mes pasaban de {{new_avg_2022}} (2022) a {{new_avg_2023}} (2023) y {{new_avg_2024}} (2024).
6. **Correlación negativa en niveles** entre gasto y altas (S&M total, rezago 0: r = {{r_new_sm_l0}}); desaparece en cambios mes a mes (|r| máximo = {{r_mom_absmax}}).
7. **Archivo de S&M construido de arriba hacia abajo** (participaciones en porcentajes enteros; Team fijo en 12% hasta {{team_fixed_until}}; Freelance → 0 cuando Team salta en {{team_break}}; PayrollExpenses negativo).
8. **Ajustes pequeños y montos fuera de la grilla**: las expansiones menores a 10% pasaron de {{small_exp_first}} ({{small_half_first}}) a {{small_exp_last}} ({{small_half_last}}); las contracciones, de {{small_con_first}} a {{small_con_last}}. Porcentaje de montos pagados en la grilla de COP 2.100: {{grid_2022h2}} (2022 S2) → {{grid_2024h2}} (2024 S2).
9. **Concentración arriba**: la cuenta más grande (cliente {{top_account_id}}, {{top_account_industry}}) paga una mediana de {{top_account_median}} al mes, {{top_account_x_median}} la mediana de los meses-cliente; algunos clientes muestran pagos grandes periódicos (por ejemplo, {{periodic_amount}} aproximadamente una vez al año).
10. **El MRR mensual es ruidoso**: cayó frente al mes anterior en {{mrr_mom_negative_months}} de 33 meses (por ejemplo, {{mrr_jun22_change}} en jun-22) mientras los clientes seguían creciendo; los movimientos brutos ({{gross_movement}}) son {{gross_net_ratio}} el cambio neto ({{net_movement}}).
11. **Caso CFO: contracción o descuento.** El puente actual no puede distinguir una contracción del cliente de un descuento, ni una expansión real de un descuento que vence. Para separar las tres capas (negocio subyacente, decisión comercial y cobro) se necesitarían seis campos por cliente y mes: `list_mrr`, `recurring_discount`, `temporary_discount`, `temporary_discount_end`, `credits` y `subscription_status` (tarjeta 9.6 del workspace).

---

## 6. Hallazgos descriptivos por dominio

**Resultado.** Clientes activos {{active_start}} → {{active_end}} ({{active_multiple}}); MRR pagado {{mrr_start}} → {{mrr_end}} ({{mrr_multiple}}); MRR por cliente activo {{arpa_start}} → {{arpa_end}} ({{arpa_change}}). Altas netas positivas en {{net_adds_positive_months}} de {{months_with_flows}} meses (negativas solo en {{net_adds_negative_list}}). Cambio neto anual del MRR: 2022 {{ab_net_2022}}, 2023 {{ab_net_2023}}, 2024 {{ab_net_2024}}.

**Adquisición.** Altas por mes: {{new_avg_2022}} (2022), {{new_avg_2023}} (2023), {{new_avg_2024}} (2024). El ticket de entrada bajó desde {{step_month}}; el {{dec_within_share}} de la caída del promedio ocurre dentro de las industrias.

**Monetización de la base.** Los clientes activos en {{window_start}} conservaron su MRR por cliente ({{base_arpa_start}} → {{base_arpa_end}}). En oct-24, MRR por cliente por cosecha: 2022 {{v2022_arpa_end}}, 2023 {{v2023_arpa_end}}, 2024 {{v2024_arpa_end}}. Las cosechas 2023–24 son {{recent_vintage_customer_share}} de los clientes activos y {{recent_vintage_mrr_share}} del MRR.

**Retención.** Retención de logos al M1: trimestres de 2022 {{m1_logo_2022_min}}–{{m1_logo_2022_max}}; trimestres completos de 2023–24 {{m1_logo_recent_min}}–{{m1_logo_recent_max}}. Retención de logos al M12: {{m12_logo_min}}–{{m12_logo_max}}. Retención de ingreso al M1: trimestres de 2022 ≤ {{rev_m1_2022_max}} (picos en M0); 2023–24 ≥ {{rev_m1_recent_min}}. Base previa: el {{base_logo_end}} sigue pagando en oct-24 y conserva el {{base_rev_end}} de su MRR de ene-22. Churn mensual de logos observado: {{churn_rate_2022}} (2022), {{churn_rate_2023}} (2023), {{churn_rate_2024}} (2024).

**Inversión comercial.** S&M total mensual promedio: 2022 {{sm_avg_2022}}, 2023 {{sm_avg_2023}}, 2024 {{sm_avg_2024}} ({{sm_chg_22_24}} frente a 2022). S&M total por alta: {{cac_sm_2022}} → {{cac_sm_2023}} → {{cac_sm_2024}} ({{total_sm_per_new_customer_chg}}); por COP 1 millón de MRR nuevo: {{sm_per_mrr_2022}} → {{sm_per_mrr_2023}} → {{sm_per_mrr_2024}} ({{total_sm_per_new_mrr_mm_chg}}).

**Gasto y adquisición.** Niveles contra altas: r de {{r_new_levels_min}} a {{r_new_levels_max}} (todas negativas). Niveles contra MRR nuevo: |r| ≤ {{r_mrr_levels_absmax}}. Cambios mes a mes: |r| ≤ {{r_mom_absmax}}, menor p = {{r_mom_minp}}. {{n_corr_sig}} de {{n_corr_tests}} pruebas tienen p < 0,05 ({{n_corr_false_pos}} esperadas solo por azar); las {{n_corr_sig}} son correlaciones negativas en niveles con las altas.

**Industrias.** Participación de Retail en las altas: {{retail_new_share_2022}} (2022) → {{retail_new_share_2023}} (2023) → {{retail_new_share_2024}} (2024); ticket de entrada de Retail en 2024: {{retail_ticket_2024}}. Participación de Restaurantes en el MRR: {{rest_mrr_share_2022}} (dic-22) → {{rest_mrr_share_2024}} (oct-24). El ticket de entrada promedio bajó en {{industries_ticket_fell_22_24}} de 6 industrias entre 2022 y 2024 (la mediana, en {{industries_median_fell_22_24}} de 6); el MRR por cliente activo bajó en {{industries_arpa_fell}} de 6 entre dic-22 y oct-24.

**Mix vs. efecto dentro.** Ticket de entrada promedio 2022 → 2024: {{dec_a0}} → {{dec_a1}} ({{dec_delta_pct}}). Dentro de las industrias {{dec_within}} ({{dec_within_share}}); mix {{dec_mix}} ({{dec_mix_share}}); intervalo de 90% de la parte "dentro": {{dec_within_ci}}; {{dec_within_share_min}}–{{dec_within_share_max}} entre variantes. Con el mix de 2022, el ticket de 2024 habría sido {{dec_cf}}. Parte "dentro" 2022 → 2023: {{dec23_within_share}}. 2023 → 2024: {{dec34_delta}} (intervalo de 90% del efecto dentro: {{dec34_ci}}).

**Movimientos de MRR.** {{lb_from}} → {{lb_to}}: {{lb_opening_mrr_cop}} + {{lb_new_mrr_cop}} de altas + {{lb_expansion_mrr_cop}} de expansión + {{lb_reactivation_mrr_cop}} de reactivación − {{lb_contraction_abs}} de contracción − {{lb_churn_abs}} de churn = {{lb_closing_mrr_cop}} (residuo COP {{lb_check}}).

---

## 7. Lo que sabemos · sospechamos · no podemos saber

**Sabemos**: el panel está completo y es consistente; clientes {{active_multiple}} frente a MRR {{mrr_multiple}}; las altas por mes se duplicaron y el MRR nuevo por mes no; el ticket de entrada bajó en {{step_month}} en todas las industrias y el {{dec_within_share}} de la caída ocurre dentro de ellas; la base de {{window_start}} conservó su MRR por cliente; el S&M cayó con fuerza a mitad de 2023 mientras la adquisición subía; gasto y adquisición no se asocian positivamente en ningún rezago probado; las cohortes recientes retienen igual o mejor al inicio; el {{churn_back_1m}} de los churns observados vuelve al mes siguiente; todos los puentes cuadran.

**Sospechamos** (por validar): `amount` es el monto cobrado o facturado por mes; parte de las altas de feb-22 son clientes previos que regresan; el escalón de {{step_month}} es consistente con un cambio de precios o empaquetamiento, descuentos o clientes más pequeños dentro de cada industria; el aumento de altas en el segundo semestre de 2023 es consistente con canales fuera del archivo de S&M, rezagos de más de tres meses o un precio de entrada menor; el archivo de S&M se asignó de arriba hacia abajo y Freelance se reclasificó a Team; los ajustes pequeños son consistentes con indexación, descuentos, prorrateos o componentes por uso; los picos del primer mes en 2022 son cargos de instalación o prepagos.

**No podemos saber** (no está en los archivos; nunca se rellena con supuestos): etapas del funnel (New → Working → Engaged → SQL → Demo → Proposal → Won) y su conversión; fechas por etapa, speed to lead, tiempo de respuesta, velocidad de cierre; fuente del lead y atribución; SDR o AE dueño; venta self-serve frente a asistida; precios, planes, precio de lista frente a pagado, valor del contrato o suscripción, frecuencia de facturación; descuentos, promociones y créditos; motivos de churn, downgrade o reactivación; si `amount` es facturado, cobrado o contratado; la unidad y las reglas de asignación del S&M; tamaño o geografía del cliente; la historia antes de {{window_start}} y después de {{window_end}}.

---

## 8. Problemas de datos conocidos (`brain/data/known_quality_issues.yaml`)

| ID | Problema | Estado | Tratamiento |
|---|---|---|---|
<!--ISSUES-->

---

## 9. Preguntas que surgieron (para Finora)

Fuente: `brain/business/stakeholder_questions.yaml`.

<!--QUESTIONS-->

---

## 10. Limitaciones

- **Series cortas.** {{n_months}} meses; las correlaciones usan n = {{corr_n_min}}–{{corr_n_levels}}. Las series tienen autocorrelación y tendencia, lo que infla las correlaciones en niveles; los cambios mes a mes son la lectura más estricta.
- **Pruebas múltiples.** {{n_corr_tests}} pruebas de correlación → cerca de {{n_corr_false_pos}} con p < 0,05 esperadas por azar.
- **Semántica de `amount`.** Si es cobro y no MRR contratado, cada categoría de movimiento mezcla eventos comerciales con el timing del cobro.
- **Censura.** A la izquierda (adquisición antes de {{window_start}} desconocida; arrastre hacia feb-22) y a la derecha (el churn reciente puede ser temporal; las cohortes tardías tienen historias cortas).
- **Segmentación.** La industria es el único atributo; los efectos "dentro de la industria" pueden esconder efectos de mix en dimensiones no observadas (tamaño, plan, canal).
- **Datos de S&M.** Unidad desconocida, construcción tipo asignación, quiebre de definición en {{team_break}}, meses de nómina negativos.
- **Sin identificación causal.** Nada aquí separa el efecto del gasto, el precio o el producto de otros cambios que ocurrieron al mismo tiempo.

---

## 11. Afirmaciones verificadas (aserciones en `finora_eda.py`)

Cada título con conclusión del workspace está respaldado por una de estas verificaciones. Si los datos cambian y una afirmación deja de ser cierta, el pipeline se detiene en lugar de publicarla. El registro también se escribe en `brain/evidence/canonical_findings.yaml` con `revision_humana: pendiente`.

| ID | Dominio | Estado | Afirmación | Verificación |
|---|---|---|---|---|
<!--CLAIMS-->

---

## 12. Reproducibilidad

- Comando: `python3 finora_eda.py` (opcional: `--raw-dir`, `--out-dir`).
- Entorno: Python {{py_version}}, pandas {{pandas_version}}, numpy {{numpy_version}}, scipy {{scipy_version}}, PyYAML. Semilla del bootstrap fija.
- SHA-256 de las entradas:
  - `Transactions.csv` `{{hash_tx}}`
  - `Industry.csv` `{{hash_ind}}`
  - `S&M_spend.csv` `{{hash_sm}}`
