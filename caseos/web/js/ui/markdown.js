// Compact Markdown → DOM (headings, paragraphs, lists, quotes, code, tables, emphasis, links) with clickable case IDs.
import { esc } from "../core/dom.js";

const ID_RE = /\b([QHNRFTDXCSA]-\d{3,})\b/g;

function inline(s, ids) {
  let t = esc(s);
  t = t.replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`);
  t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/(^|[\s(])_([^_]+)_(?=[\s).,;:]|$)/g, "$1<em>$2</em>");
  t = t.replace(/(^|[\s(])\*([^*]+)\*(?=[\s).,;:]|$)/g, "$1<em>$2</em>");
  t = t.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  if (ids) t = t.replace(ID_RE, '<span class="idref" data-id="$1">$1</span>');
  return t;
}

export function markdown(src, { ids = true } = {}) {
  const lines = String(src || "").replace(/\r/g, "").split("\n");
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const ln = lines[i];
    if (/^```/.test(ln)) {
      const buf = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
      i++;
      out.push(`<pre><code>${esc(buf.join("\n"))}</code></pre>`);
      continue;
    }
    if (/^\s*$/.test(ln)) { i++; continue; }
    const hm = ln.match(/^(#{1,4})\s+(.*)$/);
    if (hm) { out.push(`<h${hm[1].length}>${inline(hm[2], ids)}</h${hm[1].length}>`); i++; continue; }
    if (/^\s*(---|\*\*\*)\s*$/.test(ln)) { out.push("<hr/>"); i++; continue; }
    if (/^\s*\|.*\|\s*$/.test(ln)) {
      const rows = [];
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) rows.push(lines[i++]);
      const cells = r => r.trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim());
      const body = rows.filter(r => !/^\s*\|[\s:|-]+\|\s*$/.test(r));
      const head = cells(body[0] || "");
      out.push("<table><thead><tr>" + head.map(c => `<th>${inline(c, ids)}</th>`).join("") + "</tr></thead><tbody>" +
        body.slice(1).map(r => "<tr>" + cells(r).map(c => `<td>${inline(c, ids)}</td>`).join("") + "</tr>").join("") + "</tbody></table>");
      continue;
    }
    if (/^\s*>/.test(ln)) {
      const buf = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) buf.push(lines[i++].replace(/^\s*>\s?/, ""));
      out.push(`<blockquote>${inline(buf.join(" "), ids)}</blockquote>`);
      continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(ln)) {
      const ordered = /^\s*\d+\./.test(ln);
      const items = [];
      while (i < lines.length && (/^\s*([-*]|\d+\.)\s+/.test(lines[i]) || /^\s{2,}\S/.test(lines[i]))) {
        const l = lines[i++];
        if (/^\s*([-*]|\d+\.)\s+/.test(l) && !/^\s{2,}[-*]/.test(l)) items.push(l.replace(/^\s*([-*]|\d+\.)\s+/, ""));
        else if (items.length) items[items.length - 1] += "<br/>" + l.trim().replace(/^[-*]\s+/, "· ");
      }
      out.push(`<${ordered ? "ol" : "ul"}>` + items.map(x => `<li>${x.includes("<br/>") ? x.split("<br/>").map(p => inline(p, ids)).join("<br/>") : inline(x, ids)}</li>`).join("") + `</${ordered ? "ol" : "ul"}>`);
      continue;
    }
    const buf = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#{1,4}\s|```|\s*>|\s*([-*]|\d+\.)\s+|\s*\|)/.test(lines[i])) buf.push(lines[i++]);
    out.push(`<p>${inline(buf.join(" "), ids)}</p>`);
  }
  const div = document.createElement("div");
  div.innerHTML = out.join("\n");
  return div;
}
