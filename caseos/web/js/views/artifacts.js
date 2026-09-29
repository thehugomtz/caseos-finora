// Artifacts — the case as files (what GitHub shows): brain.md, case.yaml, brief, framing, decisions, research,
// evidence, story, slides, audit, snapshots. Markdown renders on paper; YAML/JSON render as structured data.
import { h, mount as put } from "../core/dom.js";
import { api } from "../core/api.js";
import { app } from "../app.js";
import { idTag, statusChip, btn, empty, dataView, tabs, hhmm, ago, typeOf } from "../ui/components.js";
import { markdown } from "../ui/markdown.js";

export async function mount(root, param) {
  let tab = param === "decisions" ? "decisions" : param === "snapshots" ? "snapshots" : param === "activity" ? "activity" : "files";
  let path = param && !["decisions", "snapshots", "activity"].includes(param) ? param : "brain.md";
  let raw = false;
  const body = h("div");
  const paint = async () => {
    app.crumbs(["Artifacts", tab === "files" ? path : tab]);
    const head = h("div.head", h("div", h("div.eyebrow", "El repositorio es parte de la entrega"), h("h1.title", "Artifacts"),
      h("p.lede", `cases/${app.caseId}/ — todo el estado vive en archivos con ID y linaje. brain.md es la memoria ejecutiva; el resto se enlaza por ID.`)),
      h("div.actions", btn("Regenerar brain.md", { variant: "ghost", icon: "refresh", onClick: async () => { await api.cpost("/brain/refresh"); path = "brain.md"; tab = "files"; paint(); } })));
    const tb = tabs([{ id: "files", label: "Archivos" }, { id: "decisions", label: "Decision log" }, { id: "snapshots", label: "Snapshots" }, { id: "activity", label: "Activity" }], tab, t => { tab = t; paint(); });
    if (tab === "files") {
      const tree = (await api.cget("/tree")).tree;
      const preview = h("div");
      put(body, head, tb, h("div.files", h("div.panel.tight.tree", { style: { maxHeight: "calc(100vh - 260px)", overflowY: "auto" } }, tree.map(n => n.type === "file"
        ? h("a.f" + (n.path === path ? ".on" : ""), { on: { click: () => { path = n.path; paint(); } } }, n.path)
        : h("details.dir", { open: path.startsWith(n.path + "/") || ["brief", "framing", "decisions", "story"].includes(n.path) }, h("summary.dname", h("span", n.path + "/"), h("span.faint", String(n.count))),
          n.children.slice(0, 250).map(c => h("a.f" + (c.path === path ? ".on" : ""), { title: c.path, on: { click: () => { path = c.path; paint(); } } }, c.path.slice(n.path.length + 1)))))), preview));
      await filePreview(preview, path, raw, v => { raw = v; paint(); });
    } else if (tab === "decisions") {
      const st = app.entities.filter(e => e.type === "decision").sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
      const full = await Promise.all(st.map(d => api.cget("/entities/" + d.id).then(r => r.entity)));
      put(body, head, tb, full.length ? h("div.stack.dlog", full.map(d => h("div.panel.pad", { style: { cursor: "pointer" }, on: { click: () => app.openEntity(d.id) } },
        h("div.row.between", h("div.row.wrap", idTag(d.id), statusChip(d.status), h("span.chip.ghost", d.kind), h("span.small.muted", d.date)), h("span.small.faint", (d.origin || {}).actor === "hugo" ? "Hugo" : (d.origin || {}).actor)),
        h("div", { style: { fontSize: "15.5px", fontWeight: 560, margin: "10px 0 6px" } }, d.title),
        d.context ? h("div.small.muted", d.context) : null,
        d.options && Object.keys(d.options).length ? h("div.row.wrap.mt", Object.entries(d.options).map(([k, v]) => h("span.chip" + (d.user_choice && String(d.user_choice).startsWith(v) ? ".human" : ""), `${k}. ${v}`))) : null,
        d.user_choice ? h("div.small.mt", h("span.muted", "Elección: "), d.user_choice) : null,
        d.user_rationale ? h("div.small", h("span.muted", "Razón: "), d.user_rationale) : null,
        (d.affected_items || []).length ? h("div.row.wrap.mt", h("span.small.muted", "Afecta:"), d.affected_items.slice(0, 10).map(i => typeOf(i) ? idTag(i) : h("span.chip", i))) : null))) : empty("Sin decisiones"));
    } else if (tab === "snapshots") {
      const sn = (await api.cget("/snapshots")).snapshots;
      put(body, head, tb, sn.length ? h("div.list", sn.map(s => h("div.item", { style: { gridTemplateColumns: "auto 1fr auto" }, on: { click: () => { tab = "files"; path = s.path + "/brain.md"; paint(); } } },
        h("span.chip.human", s.phase), h("div.body", h("div.t.mono", s.name), h("div.m", s.path)), h("span.small.faint", "ver brain.md de ese momento")))) : empty("Sin snapshots", "Se crean en cada Mark Ready."));
    } else {
      const act = (await api.cget("/activity?limit=300")).activity;
      put(body, head, tb, h("div.panel.pad", h("div", { style: { fontFamily: "var(--mono)", fontSize: "12.5px" } }, act.map(a => h("div.tline" + (a.material ? ".material" : ""), h("span.ts", hhmm(a.ts)),
        h("span.ac." + (a.actor === "hugo" ? "hugo" : "agent"), a.actor === "hugo" ? "Hugo" : a.actor), h("span.su", a.summary))))));
    }
  };
  put(root, body);
  await paint();
  return {};
}

async function filePreview(box, path, raw, setRaw) {
  let d;
  try { d = await api.cget("/files?path=" + encodeURIComponent(path)); } catch (e) { put(box, empty("No se puede previsualizar", e.message)); return; }
  const header = h("div.row.between.mb", h("div.row", h("span.mono", path), h("span.chip.ghost", d.suffix || "")), h("div.row",
    ["", ".md"].includes(d.suffix) || d.data ? h("div.seg", h("button" + (!raw ? ".on" : ""), { on: { click: () => setRaw(false) } }, "Vista"), h("button" + (raw ? ".on" : ""), { on: { click: () => setRaw(true) } }, "Raw")) : null));
  let content;
  if (raw) content = h("div.panel.pad", h("pre.raw", d.text || JSON.stringify(d.data, null, 2)));
  else if (d.suffix === ".md") content = h("div.paper", markdown(d.text));
  else if (d.suffix === ".jsonl") content = h("div.panel.pad", (d.data || []).slice().reverse().slice(0, 120).map(r => h("div", { style: { padding: "6px 0", borderBottom: "1px solid var(--line)" } }, h("div.small.faint", r.ts || r.turn_id || ""), h("div.small", r.summary || r.message || r.question || JSON.stringify(r).slice(0, 300)))));
  else if (d.data) content = h("div.panel.pad.yaml", entityHeader(d.data), dataView(d.data));
  else if (d.suffix === ".html") content = h("div.panel.pad", h("p", "Documento HTML."), path.startsWith("brief/sources/") ? h("a", { href: `/case-files/${app.caseId}/sources/${path.split("/").pop()}`, target: "_blank" }, "Abrir en una pestaña") : null);
  else content = h("div.panel.pad", h("pre.raw", d.text || ""));
  put(box, header, content);
  box.querySelectorAll(".idref").forEach(x => x.addEventListener("click", () => app.openEntity(x.dataset.id)));
}

function entityHeader(d) {
  if (!d || !d.id || !typeOf(d.id)) return null;
  return h("div.row.mb", idTag(d.id), h("span.small.muted", "Este archivo es una entidad del caso."), btn("Abrir con linaje", { sm: true, variant: "ghost", onClick: () => app.openEntity(d.id) }));
}
