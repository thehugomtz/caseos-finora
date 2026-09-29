// Agents — interactive topology of the case room and the agent card (role, purpose, status, task, skills, tools,
// inputs, outputs, guardrails, recent activity, artifacts). Gold diamonds on edges are Hugo's gates.
import { h, mount as put } from "../core/dom.js";
import { api } from "../core/api.js";
import { app } from "../app.js";
import { idTag, statusChip, btn, hhmm, ids } from "../ui/components.js";
import { markdown } from "../ui/markdown.js";

const W = 1200, H = 760;
const NODES = [
  { id: "hugo", x: 600, y: 52, w: 250, h: 50, kind: "human", tag: "HUMAN", name: "Hugo", sub: "owns the judgment" },
  { id: "core", x: 600, y: 146, w: 330, h: 58, kind: "core", tag: "CASEOS", name: "Case state · brain.md", sub: "IDs, linaje, fases, decisiones" },
  { id: "framer", x: 190, y: 290, w: 220, h: 66, kind: "agent", tag: "AGENT · FRAMING", name: "Framer", sub: "thinking partner" },
  { id: "router", x: 600, y: 290, w: 220, h: 66, kind: "agent", tag: "AGENT · RESEARCH", name: "Research Router", sub: "intensidad · especialista · skills" },
  { id: "cos", x: 1010, y: 290, w: 220, h: 66, kind: "agent", tag: "AGENT · SYNTHESIS", name: "Chief of Staff", sub: "estado, impacto, decisiones" },
  { id: "analytics", x: 330, y: 440, w: 170, h: 60, kind: "agent", tag: "SPECIALIST", name: "Analytics", sub: "datos del caso" },
  { id: "business_research", x: 510, y: 440, w: 170, h: 60, kind: "agent", tag: "SPECIALIST", name: "Business Research", sub: "web + fuentes" },
  { id: "measurement", x: 690, y: 440, w: 170, h: 60, kind: "agent", tag: "SPECIALIST", name: "Measurement", sub: "cómo medir" },
  { id: "data_engineering", x: 870, y: 440, w: 170, h: 60, kind: "agent", tag: "SPECIALIST", name: "Data Engineering", sub: "cómo modelar" },
  { id: "workspace", x: 330, y: 575, w: 190, h: 56, kind: "asset", tag: "EXISTING · REUSED", name: "Exploration Workspace", sub: "finora-eda" },
  { id: "skills", x: 560, y: 575, w: 190, h: 56, kind: "asset", tag: "SKILLS", name: "Specialist skills", sub: "dinámicas, bajo demanda" },
  { id: "package", x: 1010, y: 470, w: 200, h: 56, kind: "artifact", tag: "CONTRACT", name: "Story Package", sub: "claims · tablas · límites" },
  { id: "visual_storyteller", x: 1010, y: 590, w: 220, h: 62, kind: "agent", tag: "EXISTING AGENT", name: "Visual Storyteller", sub: "storyline → HTML → QA" },
  { id: "deck", x: 1010, y: 700, w: 180, h: 48, kind: "artifact", tag: "OUTPUT", name: "HTML deck", sub: "presentation.html" },
];
const EDGES = [
  ["hugo", "core"], ["core", "framer"], ["core", "cos"], ["framer", "router", "Framing Ready"], ["router", "analytics"], ["router", "business_research"],
  ["router", "measurement"], ["router", "data_engineering"], ["analytics", "workspace"], ["business_research", "skills"], ["measurement", "skills"],
  ["analytics", "cos"], ["business_research", "cos"], ["measurement", "cos"], ["data_engineering", "cos"], ["cos", "package", "Story Ready"],
  ["package", "visual_storyteller", "Handoff"], ["visual_storyteller", "deck"], ["cos", "framer"],
];
const AGENT_IDS = ["framer", "router", "cos", "analytics", "business_research", "measurement", "data_engineering", "visual_storyteller"];

export async function mount(root, param) {
  let sel = param || "framer";
  const topo = h("div.topo");
  const panel = h("div");
  let status = {};
  const paint = async () => {
    const st = await api.cget("/agents");
    status = st.agents;
    app.crumbs(["Agents"]);
    drawTopo();
    await paintPanel();
  };
  const drawTopo = () => {
    const byId = Object.fromEntries(NODES.map(n => [n.id, n]));
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.innerHTML = `<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="rgba(255,255,255,.35)"/></marker></defs>`;
    const running = new Set(AGENT_IDS.filter(a => (status[a] || {}).status === "running"));
    EDGES.forEach(([a, b, gate]) => {
      const A = byId[a], B = byId[b];
      const x1 = A.x, y1 = A.y + (B.y > A.y ? A.h / 2 : B.y < A.y ? -A.h / 2 : 0), x2 = B.x, y2 = B.y + (B.y > A.y ? -B.h / 2 : B.y < A.y ? B.h / 2 : 0);
      let d;
      if (a === "cos" && b === "framer") d = `M${A.x - A.w / 2} ${A.y - 10} C ${A.x - 260} ${A.y - 70}, ${B.x + 260} ${B.y - 70}, ${B.x + B.w / 2} ${B.y - 10}`;
      else if (b === "cos" && a !== "core") d = `M${x1} ${A.y + A.h / 2} C ${x1} ${A.y + 90}, ${B.x - 60} ${B.y + 120}, ${B.x - 40} ${B.y + B.h / 2}`;
      else { const my = (y1 + y2) / 2; d = `M${x1} ${y1} C ${x1} ${my}, ${x2} ${my}, ${x2} ${y2}`; }
      const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      p.setAttribute("d", d);
      p.setAttribute("class", "edge" + (running.has(a) || running.has(b) ? " flow" : ""));
      p.setAttribute("marker-end", "url(#ar)");
      if (a === "cos" && b === "framer") p.setAttribute("stroke-dasharray", "3 5");
      svg.appendChild(p);
      if (gate) {
        const mx = a === "framer" ? (A.x + B.x) / 2 : (x1 + x2) / 2, my = a === "framer" ? A.y : (y1 + y2) / 2;
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "gate");
        g.innerHTML = `<rect x="${mx - 7}" y="${my - 7}" width="14" height="14" transform="rotate(45 ${mx} ${my})" rx="2"/><text x="${mx + 14}" y="${my + 4}">${gate.toUpperCase()}</text>`;
        svg.appendChild(g);
      }
    });
    NODES.forEach(n => {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      const st = (status[n.id] || {}).status;
      g.setAttribute("class", `node ${st || ""} ${sel === n.id ? "sel" : ""}`);
      g.style.cursor = "pointer";
      const fill = n.kind === "human" ? "rgba(233,196,106,.12)" : n.kind === "core" ? "rgba(143,164,255,.1)" : n.kind === "asset" ? "rgba(255,255,255,.03)" : n.kind === "artifact" ? "rgba(240,168,104,.06)" : "rgba(16,18,26,.92)";
      const stroke = n.kind === "human" ? "rgba(233,196,106,.6)" : n.kind === "core" ? "rgba(143,164,255,.5)" : n.kind === "asset" ? "rgba(255,255,255,.14)" : n.kind === "artifact" ? "rgba(240,168,104,.4)" : null;
      g.innerHTML = `<rect class="halo" x="${n.x - n.w / 2 - 6}" y="${n.y - n.h / 2 - 6}" width="${n.w + 12}" height="${n.h + 12}" rx="${n.kind === "human" ? 30 : 18}"/>
        <rect class="box" x="${n.x - n.w / 2}" y="${n.y - n.h / 2}" width="${n.w}" height="${n.h}" rx="${n.kind === "human" ? 25 : 14}" style="fill:${fill};${stroke ? "stroke:" + stroke + ";" : ""}${n.kind === "asset" ? "stroke-dasharray:4 4;" : ""}"/>
        <text class="tag" x="${n.x - n.w / 2 + 14}" y="${n.y - n.h / 2 + 17}">${n.tag}</text>
        <text x="${n.x - n.w / 2 + 14}" y="${n.y + (n.h > 55 ? 4 : 6)}" style="font-size:${n.kind === "human" ? 15 : 14.5}px;font-weight:620">${n.name}</text>
        <text class="sub" x="${n.x - n.w / 2 + 14}" y="${n.y + (n.h > 55 ? 21 : 20)}">${n.sub}</text>
        ${AGENT_IDS.includes(n.id) ? `<circle cx="${n.x + n.w / 2 - 14}" cy="${n.y - n.h / 2 + 14}" r="4" fill="${st === "running" ? "#5ee0c8" : st === "waiting" ? "#e9c46a" : "#545b6b"}"/>` : ""}`;
      g.addEventListener("click", () => { sel = n.id; history.replaceState(null, "", "#/agents/" + n.id); drawTopo(); paintPanel(); });
      svg.appendChild(g);
    });
    put(topo, svg);
  };
  const paintPanel = async () => {
    if (!AGENT_IDS.includes(sel)) { put(panel, nodeInfo(sel)); return; }
    const card = await api.get("/api/agents/" + sel);
    const st = status[sel] || {};
    const s = k => card.sections[k] ? h("div.prose", markdown(card.sections[k], { ids: false })) : h("div.small.faint", "—");
    const bySkillMode = {};
    card.skills.forEach(x => (bySkillMode[x.binding.mode] ||= []).push(x));
    put(panel, h("div.panel.pad.agentcard",
      h("div.row.between", h("div", h("div.eyebrow.accent", card.title || card.short), h("h2", { style: { margin: "6px 0 2px", fontSize: "24px", letterSpacing: "-.015em" } }, card.name),
        h("div.small.muted", `${card.doc_path} · modelo ${card.model} · effort ${card.effort || "—"}`)),
        h("div.row", statusChip(st.status === "running" ? "running" : st.status === "waiting" ? "waiting" : "idle", st.status === "running" ? "agent" : st.status === "waiting" ? "human" : "ghost"),
          btn("Under the hood", { sm: true, icon: "hood", onClick: () => app.toggleHood() }))),
      st.current_task ? h("div.sec", h("h4", "Tarea actual"), h("div", st.current_task)) : null,
      h("div.grid2", h("div.sec", h("h4", "Role"), s("Role")), h("div.sec", h("h4", "Purpose"), s("Purpose"))),
      h("div.sec", h("h4", "Skills"), card.skills.length ? ["core", "dynamic", "lens", "challenge", "linked", "reference"].filter(m => bySkillMode[m]).map(m => h("div", bySkillMode[m].map(x => h("div.skillrow",
        h("span.mode." + m, m), h("span", h("b", x.id), h("span.small.muted", " — " + (x.purpose || ""))), h("span.small.faint", x.kind))))) : h("div.small.faint", "Usa las del workspace existente (brain/, playbooks).")),
      h("div.grid2", h("div.sec", h("h4", "Tools"), s("Tools")), h("div.sec", h("h4", "Allowed decisions"), s("Allowed decisions"))),
      h("div.grid2", h("div.sec", h("h4", "Inputs"), s("Inputs")), h("div.sec", h("h4", "Outputs"), s("Outputs"))),
      h("div.grid2", h("div.sec", h("h4", "Guardrails"), s("Guardrails")), h("div.sec", h("h4", "Requiere aprobación de Hugo"), s("User approval required"))),
      h("div.sec", h("h4", "Actividad reciente"), (st.recent || []).length ? h("div", st.recent.slice(0, 8).map(a => h("div.tline", { style: { gridTemplateColumns: "48px 1fr" } }, h("span.ts", hhmm(a.ts)), h("span.su", a.summary)))) : h("div.small.faint", "Sin actividad en este caso todavía.")),
      h("div.sec", h("h4", "Artefactos producidos"), (st.artifacts || []).length ? ids(st.artifacts, 16) : h("div.small.faint", "—"))));
  };
  put(root, h("div.head", h("div", h("div.eyebrow", "Topología · un caso, un estado, agentes especializados"), h("h1.title", "Agents"),
    h("p.lede", "No son chats pegados: todos trabajan sobre el mismo caso con IDs y linaje. Los agentes proponen; los rombos dorados son los gates donde Hugo decide.")),
    h("div.actions", h("span.small.muted", "clic en un nodo"))), topo, h("div.mt2", panel));
  await paint();
  return { update: paint };
}

function nodeInfo(id) {
  const info = {
    hugo: ["Hugo · owns the judgment", "Aprueba el framing, decide entre alternativas, decide cuándo la investigación es suficiente, acepta o rechaza findings, aprueba cambios de storyline y el Story Package, y controla el avance entre fases. Solo Hugo marca Ready o reabre una fase."],
    core: ["CaseOS · case state", "Un estado por caso en archivos (YAML/Markdown) con IDs (Q/H/N/R/F/T/D/X/C/S/A) y linaje. brain.md se regenera ante cada cambio material. Snapshots en cada Mark Ready, versiones previas de cada entidad en audit/versions/."],
    workspace: ["Business Exploration Workspace (reutilizado)", "finora-eda: pipeline de la Fase 1, mart DuckDB, capa semántica, catálogo cerrado de análisis, registro de evidencia inmutable, validador, gramática visual y UI completa — montado en /ws/finora sin cambiar su código."],
    skills: ["Specialist skills", "Se cargan solo cuando la pregunta lo pide (máx. 3): competitive-intel, market-research, product-research, commercial-skills, pricing-strategist, commercial-policy, saas-metrics-coach; más lentes C-level. Ver SKILLS.md."],
    package: ["Story Package", "Contrato entre el COS y el Visual Storyteller: audiencia, objetivo, governing thought, preguntas ejecutivas, arco, claims con evidencia/tablas/límites/intención visual, recomendaciones, apéndice, preguntas sin resolver, perfil de lenguaje. Validado en código."],
    deck: ["HTML deck", "presentation.html de un solo archivo + PDF, producidos por el Visual Storyteller. Cada slide conserva el claim que prueba."],
  }[id] || [id, ""];
  return h("div.panel.pad", h("div.eyebrow", "Nodo"), h("h2", { style: { margin: "6px 0 8px", fontSize: "22px" } }, info[0]), h("p.prose", info[1]),
    id === "core" ? btn("Abrir brain.md", { icon: "arrow", onClick: () => app.go("#/artifacts/brain.md") }) : id === "package" ? btn("Abrir Story", { icon: "arrow", onClick: () => app.go("#/story") })
      : id === "deck" ? btn("Abrir Slides", { icon: "arrow", onClick: () => app.go("#/slides") }) : id === "workspace" ? btn("Abrir Analytics", { icon: "arrow", onClick: () => app.go("#/analytics") }) : null);
}
