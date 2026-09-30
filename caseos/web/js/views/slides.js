// Slides — handoff of the approved Story Package to the existing Executive Visual Storyteller, live run trace,
// and the resulting HTML deck with slide → claim → evidence lineage.
import { h, mount as put } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { idTag, statusChip, btn, empty, toast, thinking, hhmm, ago, confirmDialog } from "../ui/components.js";

const VENDORED_IN_APP = ["Inter", "Newsreader", "IBM Plex Mono"];
const loadedFonts = new Set();
function previewFont(family) {                          // only for the on-screen preview; the deck gets its own files
  if (!family || VENDORED_IN_APP.includes(family) || loadedFonts.has(family)) return;
  loadedFonts.add(family);
  document.head.append(h("link", { rel: "stylesheet", href: `https://fonts.googleapis.com/css2?family=${encodeURIComponent(family)}:wght@400;600&display=swap` }));
}

export async function mount(root) {
  let direction = "editorial", critic = true, open = null;
  const body = h("div");
  const style = { title_font: "", text_font: "", colors: {}, notes: "" };
  let styleReady = false;
  const styleBox = h("div.stylebox");
  const preview = h("div.stylepreview");
  const hasStyle = () => !!(style.title_font || style.text_font || style.notes || Object.keys(style.colors).length);
  const paintPreview = () => {
    const c = style.colors, bg = c.background || "#ffffff", ink = c.text || "#0b1220", ac = c.accent || "#1846f5", ac2 = c.accent_2 || "#c3cad4";
    previewFont(style.title_font); previewFont(style.text_font);
    const tf = style.title_font ? `'${style.title_font}', Georgia, serif` : "'Newsreader', Georgia, serif";
    const xf = style.text_font ? `'${style.text_font}', Arial, sans-serif` : "'Inter', Arial, sans-serif";
    put(preview, h("div.sp", { style: { background: bg, color: ink } },
      h("div.spk", { style: { fontFamily: xf, color: ink, opacity: .6 } }, "02 · DE DÓNDE VIENE"),
      h("div.sph", { style: { fontFamily: tf } }, "Los nuevos pagadores entran con un ticket menor que en 2022"),
      h("div.spb", h("i", { style: { height: "78%", background: ac2 } }), h("i", { style: { height: "46%", background: ac } }), h("i", { style: { height: "52%", background: ac2 } }),
        h("div.spa", { style: { fontFamily: xf, color: ink } }, "La mediana bajó de COP 63,0 mil a 36,8 mil")),
      h("div.spf", { style: { fontFamily: xf, color: ink, opacity: .5 } }, "Fuente: T-004 · CaseOS C-002")));
  };
  const paintStyle = (fonts, keys) => {
    const fontInput = (k, ph) => h("input", { value: style[k], placeholder: ph, list: "caseos-fonts", on: { input: e => { style[k] = e.target.value.trim(); paintPreview(); } } });
    const colorRow = k => {
      const cell = h("div.colorcell");
      const draw = () => put(cell, h("div.small.muted", keys[k]), style.colors[k]
        ? h("div.row", { style: { gap: "6px" } },
            h("input", { type: "color", value: style.colors[k], on: { input: e => { style.colors[k] = e.target.value; hex.value = e.target.value; paintPreview(); } } }),
            (hex = h("input.hex", { value: style.colors[k], on: { change: e => { const v = e.target.value.trim(); if (/^#?[0-9a-f]{6}$/i.test(v)) { style.colors[k] = v.startsWith("#") ? v : "#" + v; draw(); paintPreview(); } } } })),
            h("button.btn.ghost.sm", { type: "button", title: "Quitar", on: { click: () => { delete style.colors[k]; draw(); paintPreview(); } } }, "×"))
        : h("button.btn.sm", { type: "button", on: { click: () => { style.colors[k] = { background: "#ffffff", text: "#1e2a5a", accent: "#e4572e", accent_2: "#9aa5b8" }[k]; draw(); paintPreview(); } } }, "Elegir"));
      let hex;
      draw();
      return cell;
    };
    const notes = h("textarea", { placeholder: "En tus palabras: «sobrio, tipo consultora, mucho blanco; el naranja solo para lo importante»", on: { input: e => { style.notes = e.target.value; } } });
    notes.value = style.notes;
    put(styleBox,
      h("div.row.between", h("div", h("div", { style: { fontWeight: 620 } }, "Guía de formato (opcional)"),
        h("div.small.muted", "Tipografías y colores como los dirías. Si no pones nada, se usa la dirección elegida arriba.")),
        btn("Guardar guía", { sm: true, variant: "ghost", icon: "check", onClick: async () => {
          try { await api.cput("/slides/style", style); toast("Guía de formato guardada para este caso", "ok"); } catch (e) { toast(e.message, "err"); } } })),
      h("datalist#caseos-fonts", (fonts.suggested || []).map(f => h("option", { value: f }, (fonts.vendored || []).includes(f) ? "incluida en el renderer" : "Google Fonts"))),
      h("div.grid2", { style: { gap: "10px", marginTop: "10px" } },
        h("div.field", { style: { marginTop: 0 } }, h("label", "Tipografía de títulos"), fontInput("title_font", "Ej. Playfair Display")),
        h("div.field", { style: { marginTop: 0 } }, h("label", "Tipografía de texto"), fontInput("text_font", "Ej. Inter"))),
      h("div.colors", Object.keys(keys).map(colorRow)),
      h("div.field", h("label", "Notas de formato"), notes),
      h("div.small.faint", "Cualquier fuente de Google Fonts sirve: se descarga al preparar el deck para que el HTML quede autocontenido. El contraste se revisa solo y te digo si ajusté algo."),
      preview);
    paintPreview();
  };
  const paint = async () => {
    const [d, story] = await Promise.all([api.cget("/slides"), api.cget("/story")]);
    if (!styleReady) {
      const sv = d.style || {};
      Object.assign(style, { title_font: sv.title_font || "", text_font: sv.text_font || "", colors: { ...(sv.colors || {}) }, notes: sv.notes || "" });
      styleReady = true;
      paintStyle(d.fonts || {}, d.color_keys || {});
    }
    const ph = d.phase;
    const storyReady = story.phase.status === "ready";
    const decks = d.decks.slice().reverse();
    const cur = open ? decks.find(x => x.id === open) : decks.find(x => x.status === "completed") || decks[0];
    app.crumbs(["Slides"]);
    let job = null;
    if (cur && cur.job_id && cur.status === "running") { try { job = await api.cget(`/jobs/${cur.job_id}`); } catch (e) { job = null; } }
    put(body,
      h("div.head", h("div", h("div.eyebrow", "06 · Slides · Executive Visual Storyteller (capacidad existente, no reconstruida)"), h("h1.title", "Slides"),
        h("p.lede", "CaseOS prepara el handoff según el contrato del Storyteller — storyline pre-llenado desde el Story Package aprobado y las tablas como contrato de datos — y lo corre con sus propias skills: dirección visual, composición, render HTML, QA por screenshots.")),
        h("div.actions", statusChip(ph.status), btn(ph.status === "ready" ? "Deck aprobado" : "Mark Slides Ready", { variant: "human", human: true, disabled: ph.status === "ready" || !decks.some(x => x.status === "completed"), onClick: () => app.markReady("slides") }))),
      h("div.split",
        h("div.panel.pad.handoff", h("div.eyebrow.human", "Handoff · gate humano"),
          h("div.stack.mt",
            h("div.row", storyReady ? h("span.chip.good", "Story Ready") : h("span.chip.warn", "Story todavía no está Ready"), story.package ? h("span.small.muted", `Story Package v${story.package.version} · ${(story.package.claims || []).length} claims`) : h("span.small.muted", "sin Story Package")),
            h("div.small.muted", "Dirección visual (la elige Hugo; «elige tú» deja que el Storyteller decida y lo justifique):"),
            h("div.dirs", Object.entries(d.directions).map(([k, v]) => h("div.dir" + (direction === k ? ".on" : ""), { on: { click: () => { direction = k; paint(); } } }, h("div.n", k === "auto" ? "Elige tú" : k), h("div.small.muted", v.split(" — ")[1] || v)))),
            h("label.row", { style: { cursor: "pointer" } }, h("input", { type: "checkbox", checked: critic, on: { change: e => { critic = e.target.checked; } } }), h("span.small", "Crítica independiente final (agente independent-slide-critic)")),
            styleBox,
            h("div.row", h("span.spacer"), btn((d.decks || []).some(x => x.status === "running") ? "El Storyteller ya está trabajando" : "Enviar al Visual Storyteller", { variant: "human", human: true, icon: "send", disabled: !storyReady || (d.decks || []).some(x => x.status === "running"), onClick: async () => {
              const ok = await confirmDialog({ eyebrow: "Human gate", title: "Enviar el Story Package al Visual Storyteller", text: `Dirección ${direction}${hasStyle() ? " con tu guía de formato" : ""}. La corrida es larga (decenas de minutos) y consume tu plan; escribe solo dentro de la carpeta del deck.`, confirmLabel: "Enviar", human: true });
              if (!ok) return;
              try {
                const out = await api.cpost("/slides/handoff", { direction, critic, run: true, style: hasStyle() ? style : null }); open = out.deck.id;
                toast(`Handoff listo (${out.deck.slug}) · el Storyteller está trabajando`, "agent");
                ((out.deck.style || {}).notes || []).forEach(n => toast(n, "info", 9000));
                paint();
              }
              catch (e) { toast(e.message, "err", 8000); }
            } })),
            h("div.small.faint", "Skills enlazadas: ", d.links.filter(l => l.skill).map(l => h("span.chip" + (l.linked ? ".good" : ".bad"), { style: { marginRight: "4px" } }, l.skill))))),
        h("div.panel.pad", h("div.eyebrow", "Decks"), decks.length ? h("div.list.mt", decks.map(x => h("div.item", { style: { gridTemplateColumns: "1fr auto" }, on: { click: () => { open = x.id; paint(); } } },
          h("div.body", h("div.t", x.slug), h("div.m", h("span", `v${x.package_version} · ${x.direction}`), x.slides ? h("span", `${x.slides} slides`) : null, h("span", ago(x.created_at)), x.cost_usd ? h("span", `US$${Number(x.cost_usd).toFixed(2)} eq.`) : null)),
          x.status === "running" ? h("span.row", thinking(), statusChip("running")) : statusChip(x.status === "prepared" ? "draft" : x.status)))) : empty("Sin decks todavía", "El deck aparece aquí cuando envías el Story Package."))),
      cur ? deckView(cur, job, d.slides.filter(s => s.deck === cur.id), paint) : null);
  };
  put(root, body);
  await paint();
  const onJob = ev => { if (ev.job.kind === "storyteller") paint(); };
  app.on("job", onJob);
  return { update: paint, destroy: () => { app.listeners.job = (app.listeners.job || []).filter(f => f !== onJob); } };
}

function deckView(x, job, slides, paint) {
  const base = `/case-files/${app.caseId}/decks/${x.slug}/`;
  return h("div.mt2",
    h("div.row.between.mb", h("h2.sec", x.title || x.slug), h("div.row", x.presentation ? btn("Abrir presentación", { icon: "eye", onClick: () => window.open(base + "presentation.html", "_blank") }) : null,
      x.index ? btn("Viewer (←/→, G, N)", { variant: "ghost", onClick: () => window.open(base + "index.html", "_blank") }) : null,
      x.presentation && x.status !== "running" ? btn("Actualizar PDF", { variant: "ghost", icon: "refresh", onClick: async (ev) => {
        const b = ev.currentTarget; b.disabled = true; toast("Regenerando el PDF con tus cambios…", "info");
        try { const out = await api.cpost(`/slides/${x.id}/pdf`); toast(out.ok ? "PDF actualizado" : `No pude regenerar el PDF: ${out.error}`, out.ok ? "ok" : "err", 7000); }
        catch (e) { toast(e.message, "err", 7000); } finally { b.disabled = false; } } }) : null,
      x.presentation ? btn("Descargar PDF", { variant: "ghost", onClick: () => window.open(base + "renders/deck.pdf?v=" + Date.now(), "_blank") }) : null,
      x.status === "failed" || x.status === "interrupted" || x.status === "prepared" || x.status === "incomplete" ? btn(x.status === "prepared" ? "Correr el Storyteller" : "Reintentar", { icon: "refresh", onClick: async () => { await api.cpost(`/slides/${x.id}/run`); toast("Storyteller trabajando", "agent"); paint(); } }) : null)),
    x.status === "running" ? h("div.panel.pad.agentwork", h("div.row", thinking(), h("span", { style: { fontWeight: 560 } }, "El Visual Storyteller está trabajando"), h("span.small.muted", "Story → dirección → composición → render → QA → paquete")),
      h("div.progress.mt", { style: { maxHeight: "300px" } }, ((job || {}).progress || []).slice(-40).map(p => h("div", h("span.t", hhmm(p.t)), h("span", p.summary || p.kind))))) : null,
    x.status === "failed" || x.status === "interrupted" ? h("div.panel.pad.alert", h("div.eyebrow", { style: { color: "var(--bad-ink)" } }, x.status === "interrupted" ? "La corrida se interrumpió" : "La corrida falló"), h("p.prose", x.error || ""), h("div.small.muted", "El Story Package y la carpeta del deck se conservaron.")) : null,
    x.presentation ? h("div.deckframe", h("iframe#deckframe", { src: base + "presentation.html", title: "Deck" })) : null,
    x.presentation && x.status !== "running" ? orderEditor(x) : null,
    slides.length ? h("div.mt", h("h2.sec.mb", "Slides y linaje"), h("div.thumbs", slides.map(s => h("div.thumb", { on: { click: () => app.openEntity(s.id) } },
      s.render ? h("img", { src: `/case-files/${app.caseId}/decks/${s.render.split("/decks/")[1]}`, alt: s.title }) : h("div", { style: { aspectRatio: "16/9", display: "grid", placeItems: "center", color: "var(--ink-4)" } }, "sin render"),
      h("div.c", h("div.clamp2", s.title), h("div.row", { style: { marginTop: "6px" } }, idTag(s.id), s.claim_id ? idTag(s.claim_id) : null, s.qa_verdict ? h("span.chip" + (s.qa_verdict === "PASS" ? ".good" : ".warn"), s.qa_verdict) : null)))))) : null,
    x.final_message ? h("details.panel.pad.mt", h("summary.small", { style: { cursor: "pointer" } }, "Reporte final del Storyteller"), h("pre.raw.mt", x.final_message)) : null,
    h("div.small.faint.mt", `Carpeta: cases/${app.caseId}/${x.path}`));
}

/* ------------------------------------------------------------------ Hugo's own quick edits: order and text */
// The Storyteller builds the deck; these are the small fixes Hugo makes himself. Every change is logged in the case.
function reloadDeckFrame() {
  const f = document.getElementById("deckframe");
  if (f) f.src = f.src.split("?")[0] + "?v=" + Date.now();
}

function orderEditor(x) {
  const box = h("div.panel.pad.mt.deckedit");
  const base = `/case-files/${app.caseId}/decks/${x.slug}/`;
  let files = [], dirty = false, drag = null;
  const load = async () => { try { files = (await api.cget(`/slides/${x.id}/files`)).files; dirty = false; draw(); } catch (e) { put(box, h("div.small.muted", e.message)); } };
  const move = (from, to) => {
    if (from === null || from === to) return;
    const [it] = files.splice(from, 1);
    files.splice(to, 0, it);
    dirty = true; drag = null; draw();
  };
  const save = async () => {
    try {
      const out = await api.cpost(`/slides/${x.id}/order`, { order: files.map(f => f.file) });
      toast(`Orden guardado · ${out.moved} láminas cambiaron de lugar · presentación rearmada`, "ok");
      await load(); reloadDeckFrame();
    } catch (e) { toast(e.message, "err", 7000); }
  };
  const draw = () => put(box,
    h("div.row.between", h("div", h("div.eyebrow", "Tus ajustes al deck"),
      h("div.small.muted", "Arrastra las láminas para cambiar el orden. Haz clic en una para editar su texto. Todo queda en la bitácora del caso.")),
      h("div.row", dirty ? btn("Deshacer", { sm: true, variant: "ghost", onClick: load }) : null,
        btn(dirty ? "Guardar orden" : "Orden guardado", { sm: true, variant: "human", human: true, disabled: !dirty, onClick: save }))),
    h("div.dstrip", files.map((f, i) => h("div.dthumb" + (drag === i ? ".dragging" : ""), {
      draggable: "true", title: "Arrastra para mover · clic para editar el texto",
      on: {
        dragstart: e => { drag = i; e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", String(i)); },
        dragover: e => { e.preventDefault(); e.currentTarget.classList.add("over"); },
        dragleave: e => e.currentTarget.classList.remove("over"),
        drop: e => { e.preventDefault(); move(drag, i); },
        dragend: () => { drag = null; box.querySelectorAll(".over").forEach(n => n.classList.remove("over")); },
        click: () => { if (dirty) { toast("Guarda el orden antes de editar el texto", "info"); return; } slideEditor(x, f, load); },
      } },
      h("span.dn", String(i + 1)),
      f.render ? h("img", { src: base + f.render + "?v=" + f.v, alt: f.title, draggable: "false" }) : h("div.noimg", "sin render"),
      h("div.dt.clamp2", f.title)))));
  load();
  return box;
}

function slideEditor(x, f, onSaved) {
  const base = `/case-files/${app.caseId}/decks/${x.slug}/`;
  const orig = new Map();
  let editing = false;
  const frame = h("iframe.se-frame", { src: base + "slides/" + f.file.replace(".html", ".edit.html") + "?v=" + Date.now(), title: "Lámina " + f.n });
  const stage = h("div.se-stage", frame);
  const status = h("span.small.muted", "Cargando la lámina…");
  const fit = () => { const w = stage.clientWidth; frame.style.transform = `scale(${w / 1920})`; stage.style.height = (1080 * w / 1920) + "px"; };
  const dirtyCount = () => [...orig].filter(([el, html0]) => el.innerHTML !== html0).length;
  const close = () => {
    if (dirtyCount() && !window.confirm("Tienes cambios sin guardar en esta lámina. ¿Cerrar sin guardarlos?")) return;
    wrap.remove(); window.removeEventListener("resize", fit); document.removeEventListener("keydown", esc);
  };
  const esc = e => { if (e.key === "Escape" && !editing) close(); };
  // text written in the markup (data-ct) and text the slide's script paints (.prim-label), except axis and value labels
  const scan = async () => {
    const doc = frame.contentDocument;
    if (!doc) return;
    doc.querySelectorAll("[data-ct]").forEach(el => { if (!orig.has(el)) orig.set(el, el.innerHTML); });
    const painted = [...doc.querySelectorAll("main.slide .prim-label")].filter(el => !orig.has(el) && !el.closest("[data-ct]") && !["axis-label", "value-label"].includes(el.dataset.role));
    let skipped = 0;
    if (painted.length) {
      // only what can be found once in the slide's code is offered: a value repeated in a chart's data would be a guess
      const { found } = await api.cpost(`/slides/${x.id}/locate`, { file: f.file, texts: painted.map(el => ({ old: el.innerHTML, id: el.id || "" })) });
      painted.forEach((el, i) => { if (found[i]) orig.set(el, el.innerHTML); else skipped++; });
    }
    status.textContent = `${orig.size} textos editables` + (skipped ? ` · ${skipped} valores de gráfica se piden al Storyteller` : "")
      + " · las etiquetas de ejes y valores calculados salen de los datos";
  };
  const mark = async () => {
    const doc = frame.contentDocument;
    if (!doc) return;
    const st = doc.createElement("style");
    st.textContent = "[data-ce]{outline:1.5px dashed rgba(0,208,179,.75);outline-offset:3px;cursor:text}[data-ce]:focus{outline:2px solid #00d0b3;background:rgba(0,208,179,.06)}";
    doc.head.append(st);
    try { await doc.fonts.ready; } catch (e) { /* no font API: scan anyway */ }
    requestAnimationFrame(() => setTimeout(scan, 150));        // the slide paints its text once its fonts are in
  };
  const toggle = async () => {
    await scan();
    editing = !editing;
    orig.forEach((_, el) => { el.contentEditable = editing ? "true" : "false"; if (editing) el.dataset.ce = ""; else delete el.dataset.ce; });
    tbtn.textContent = editing ? "Terminar de editar" : "Editar texto";
  };
  const save = async () => {
    const edits = [];
    orig.forEach((html0, el) => {
      if (el.innerHTML === html0) return;
      if (el.dataset.ct !== undefined) edits.push({ k: Number(el.dataset.ct), html: el.innerHTML });
      else edits.push({ old: html0, new: el.innerHTML, id: el.id || "" });
    });
    if (!edits.length) { toast("No hay cambios que guardar", "info"); return; }
    try {
      const out = await api.cput(`/slides/${x.id}/text`, { file: f.file, edits, source: frame.contentDocument.documentElement.dataset.ctHash || "" });
      toast(`${out.changed.length} cambio(s) guardado(s) en la lámina ${f.n} · la presentación ya los tiene; la miniatura se actualiza en un minuto`
        + (out.failed.length ? ` · ${out.failed.length} no se pudieron ubicar` : ""), out.failed.length ? "err" : "ok", 8000);
      setTimeout(onSaved, 70000);                                   // refresh the strip when the new thumbnail is in
      out.failed.forEach(x => toast(`«${x.text}»: ${x.why}. Pídeselo al Storyteller.`, "err", 9000));
      wrap.remove(); window.removeEventListener("resize", fit); document.removeEventListener("keydown", esc);
      onSaved(); reloadDeckFrame();
    } catch (e) { toast(e.message, "err", 8000); }
  };
  const tbtn = btn("Editar texto", { sm: true, onClick: toggle });
  const wrap = h("div.se-wrap", h("div.se-box",
    h("div.row.between", h("div", h("div.eyebrow", `Lámina ${f.n} · tus ajustes`), h("div", { style: { fontWeight: 600 } }, f.title)),
      h("div.row", tbtn, btn("Guardar cambios", { sm: true, variant: "human", human: true, onClick: save }), btn("Cerrar", { sm: true, variant: "ghost", onClick: close }))),
    h("div.small.faint", "Si cambias una cifra, deja de venir de su tabla: el cambio queda registrado con el antes y el después."),
    stage, status));
  document.body.append(wrap);
  document.addEventListener("keydown", esc);
  window.addEventListener("resize", fit);
  requestAnimationFrame(fit);
  frame.addEventListener("load", mark);
}
