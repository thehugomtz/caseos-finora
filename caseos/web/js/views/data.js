// Datos — the case's data model, for real: three layers (raw → staging → mart), each table with how it is built, its
// columns and a live sample; a read-only SQL console; and the reconciliation checks that prove the layers agree.
import { h, mount as put, autosize } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { btn, empty, toast } from "../ui/components.js";

const EXAMPLES = [
  ["Monto y clientes por mes", "SELECT month, active_customers, total_paid_mrr_cop, mrr_per_active_customer_cop\nFROM mart.monthly_metrics\nORDER BY month"],
  ["Altas por año", "SELECT year, COUNT(*) AS altas, MEDIAN(m0_cop) AS mediana_primer_pago_cop\nFROM mart.new_customers\nGROUP BY year\nORDER BY year"],
  ["Raw tal cual", "SELECT * FROM raw.transactions LIMIT 20"],
  ["Staging ↔ mart por mes", "WITH s AS (SELECT month, SUM(amount_cop) AS staging_cop FROM staging.stg_customer_month GROUP BY month)\n"
    + "SELECT s.month, s.staging_cop, m.total_paid_mrr_cop AS mart_cop, s.staging_cop - m.total_paid_mrr_cop AS diferencia\n"
    + "FROM s JOIN mart.monthly_metrics m USING (month)\nORDER BY s.month"],
];

export async function mount(root, param) {
  app.crumbs(["Datos"]);
  const meta = (app.summary || {}).meta || {};
  const models = (await api.get("/api/datamodels")).models || [];
  const bound = (meta.data_model || {}).id;
  const mid = param || bound || (models.find(m => m.available) || {}).id;
  if (!mid) { put(root, h("div.head", h("div", h("div.eyebrow", "Modelo de datos"), h("h1.title", "Datos"))), empty("Sin modelos de datos", "No encontré un workspace analítico junto a CaseOS.")); return {}; }
  const d = await api.get(`/api/datamodels/${mid}`);
  const cat = d.catalog, tables = cat.tables;
  const byId = Object.fromEntries(tables.map(t => [t.id, t]));
  const children = id => tables.filter(t => (t.parents || []).includes(id)).map(t => t.id);
  let sel = byId["mart.customer_month"] ? "mart.customer_month" : tables[0].id;

  const strip = h("div.lstrip");
  const detail = h("div.panel.pad");
  const sqlBox = autosize(h("textarea.sqlin", { spellcheck: "false" }));
  const results = h("div");
  sqlBox.value = EXAMPLES[0][1];
  sqlBox.addEventListener("keydown", e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) run(); });

  const run = async () => {
    put(results, h("div.small.muted", "Consultando…"));
    try {
      const r = await api.post(`/api/datamodels/${mid}/query`, { sql: sqlBox.value, limit: 500 });
      put(results, h("div.small.muted", { style: { margin: "10px 0 6px" } }, `${r.rows.length} fila(s)${r.truncated ? " · se muestran las primeras 500" : ""} · ${r.ms} ms · solo lectura`),
        resultTable(r.columns, r.rows));
    } catch (e) { put(results, h("div.qerr", e.message)); }
  };

  const paintStrip = () => {
    const rel = new Set([...(byId[sel].parents || []), ...children(sel)]);
    put(strip, cat.layers.map((l, i) => [i ? h("div.larrow2", icon("arrow")) : null,
      h("div.lcol", h("div.lh", h("span.ln", l.label), h("span.small.muted", `${tables.filter(t => t.schema === l.id).length} tablas`)), h("div.small.muted.lcd", l.desc),
        h("div.stack", { style: { gap: "6px", marginTop: "10px" } }, tables.filter(t => t.schema === l.id).map(t =>
          h("button.tchip" + (t.id === sel ? ".on" : "") + (rel.has(t.id) ? ".rel" : ""), { type: "button", on: { click: () => { sel = t.id; paintStrip(); paintDetail(); } } },
            h("span.tn", t.name), h("span.tr", `${fmt(t.rows)} · ${t.kind}`)))))]));
  };

  const paintDetail = async () => {
    const t = byId[sel];
    const sample = h("div", h("div.small.muted", "Cargando muestra…"));
    put(detail,
      h("div.row.between.wrap", h("div", h("div.eyebrow.accent", `${t.schema} · ${t.kind}`), h("h2", { style: { margin: "4px 0 2px", fontSize: "20px", fontFamily: "var(--mono)", fontWeight: 560 } }, t.id)),
        btn("Consultar esta tabla", { sm: true, icon: "play", onClick: () => { sqlBox.value = `SELECT *\nFROM ${t.id}\nLIMIT 50`; sqlBox.dispatchEvent(new Event("input")); run(); } })),
      h("p.prose", { style: { marginTop: "8px" } }, t.desc),
      h("div.kvline", h("span", h("b", "Grano: "), t.grain || "—"), h("span", h("b", "Filas: "), fmt(t.rows)), h("span", h("b", "Columnas: "), String(t.columns.length))),
      (t.parents || []).length ? h("div.small", { style: { marginTop: "6px" } }, h("span.muted", "Viene de: "), t.parents.map(p => h("button.linkish", { type: "button", on: { click: () => { sel = p; paintStrip(); paintDetail(); } } }, p)),
        t.via ? h("span.faint", ` · ${t.via}`) : null) : null,
      t.file ? h("div.small.muted", { style: { marginTop: "6px" } }, `Archivo ${t.file.file} · ${fmt(t.file.bytes)} bytes · sha256 ${t.file.sha256.slice(0, 16)}…${t.file.utf8_bom ? " · con BOM" : ""}`) : null,
      h("details.mt", h("summary.small", { style: { cursor: "pointer", fontWeight: 600 } }, "Cómo se construye"), h("pre.sql", t.definition)),
      h("h3.sub.mt", "Columnas"),
      h("div.tablewrap", h("table.tbl", h("thead", h("tr", h("th", "Columna"), h("th", "Tipo"), h("th", "Definición"))),
        h("tbody", t.columns.map(c => h("tr", h("td.mono", c.name), h("td.mono", c.type), h("td", c.definition || "—")))))),
      h("h3.sub.mt", "Muestra (20 filas, datos reales)"), sample);
    try {
      const r = await api.get(`/api/datamodels/${mid}/sample?table=${encodeURIComponent(t.id)}&limit=20`);
      put(sample, resultTable(r.columns, r.rows));
    } catch (e) { put(sample, h("div.qerr", e.message)); }
  };

  const checks = d.checks || [];
  const okN = checks.filter(c => c.status === "ok").length;
  put(root,
    h("div.head", h("div", h("div.eyebrow", "Modelo de datos · solo lectura"), h("h1.title", cat.label),
      h("p.lede", `${cat.source}. Tres capas reales: lo que llegó (raw), lo tipado (staging) y lo procesado (mart). Cada check trae su SQL para volverlo a correr.`)),
      h("div.actions",
        bound === mid ? h("span.chip.good", icon("check"), "enlazado a este caso")
          : btn("Usar en este caso", { variant: "human", human: true, icon: "check", onClick: async () => { await api.cpost("/datamodel", { model_id: mid }); toast(`${cat.label} enlazado al caso`, "ok"); await app.refresh(); app.go("#/data/" + mid); } }),
        h(`span.chip.${okN === checks.length ? "good" : "warn"}`, `${okN}/${checks.length} checks`))),
    strip,
    h("div.split.mt", { style: { alignItems: "start" } }, detail,
      h("div.stack.lg",
        h("div.panel.pad", h("div.row.between", h("h2.sec", "Consulta"), h("span.small.faint", "⌘↵ · una SELECT · raw.* staging.* mart.*")),
          h("div.row.wrap", { style: { gap: "6px", margin: "10px 0" } }, EXAMPLES.map(([l, q]) => h("button.chip", { type: "button", style: { cursor: "pointer" }, on: { click: () => { sqlBox.value = q; sqlBox.dispatchEvent(new Event("input")); run(); } } }, l))),
          h("div.qbox", sqlBox), h("div.row", { style: { marginTop: "10px" } }, h("span.spacer"), btn("Correr", { variant: "primary", icon: "play", onClick: run })), results),
        h("div.panel.pad", h("h2.sec", "Checks de reconciliación", h("span.count", `${okN}/${checks.length}`)),
          h("p.small.muted", { style: { margin: "6px 0 10px" } }, "Prueban que las tres capas dicen lo mismo. El mart lo construye el workspace desde la Fase 1; el staging se reconstruye aquí desde raw."),
          h("div.stack", { style: { gap: "8px" } }, checks.map(c => h("div.chk." + c.status,
            h("div.row", h("span.ci", icon(c.status === "ok" ? "check" : c.status === "warn" ? "flag" : "x")), h("span", { style: { fontWeight: 580 } }, c.title)),
            h("div.small.muted", { style: { marginLeft: "28px" } }, c.detail),
            h("details", { style: { marginLeft: "28px" } }, h("summary.small.faint", { style: { cursor: "pointer" } }, "Ver cómo se comprueba"), h("pre.sql", c.sql),
              c.sql.trim().toUpperCase().startsWith("SELECT") || c.sql.trim().toUpperCase().startsWith("WITH")
                ? btn("Correr en la consola", { sm: true, icon: "play", onClick: () => { sqlBox.value = c.sql; sqlBox.dispatchEvent(new Event("input")); run(); } }) : null))))))));
  paintStrip();
  paintDetail();
  return {};
}

function resultTable(cols, rows) {
  if (!rows.length) return h("div.small.muted", "Sin filas.");
  return h("div.tablewrap", { style: { maxHeight: "420px", overflow: "auto" } }, h("table.tbl", h("thead", h("tr", cols.map(c => h("th", c)))),
    h("tbody", rows.map(r => h("tr", r.map(v => h("td" + (typeof v === "number" ? ".n" : ""), v === null ? "–" : typeof v === "number" ? num(v) : String(v))))))));
}
const fmt = n => (n || 0).toLocaleString("es-MX").replace(/,/g, ".");
const num = v => Number.isInteger(v) ? fmt(v) : v.toLocaleString("es-MX", { maximumFractionDigits: 6 }).replace(/,/g, "·").replace(/\./g, ",").replace(/·/g, ".");
