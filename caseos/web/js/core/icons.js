// Stroke icons (24px grid, 1.6 stroke). Inline SVG so the app has zero external assets.
const P = {
  home: "M3 10.5 12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z",
  brief: "M7 3h7l5 5v12a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14 3v5h5M9 13h7M9 17h5",
  compass: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM15.5 8.5l-2 5-5 2 2-5z",
  search: "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.3-4.3",
  orbit: "M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM4.9 19.1C1.9 16.1 3.5 9.6 8.5 4.6M19.1 4.9c3 3 1.4 9.5-3.6 14.5M4.9 4.9C7.9 1.9 14.4 3.5 19.4 8.5M19.1 19.1c-3 3-9.5 1.4-14.5-3.6",
  story: "M4 6h16M4 12h10M4 18h13",
  slides: "M3 5h18v12H3zM8 21h8M12 17v4",
  agents: "M12 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM5 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM12 8v4M12 12l-5 4.5M12 12l5 4.5",
  files: "M4 4h6l2 2h8v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z",
  chart: "M4 20V10M10 20V4M16 20v-7M22 20H2",
  globe: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3 12h18M12 3c2.5 3 2.5 15 0 18M12 3c-2.5 3-2.5 15 0 18",
  ruler: "M3 17 17 3l4 4L7 21zM7 13l2 2M10 10l2 2M13 7l2 2",
  db: "M12 8c4.4 0 8-1.3 8-3s-3.6-3-8-3-8 1.3-8 3 3.6 3 8 3zM4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
  route: "M6 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM18 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM6 15V9a4 4 0 0 1 4-4h6M18 9v6a4 4 0 0 1-4 4H8",
  hood: "M4 7l8-4 8 4-8 4zM4 12l8 4 8-4M4 17l8 4 8-4",
  play: "M7 4v16l13-8z",
  x: "M6 6l12 12M18 6 6 18",
  check: "M4 12.5 9 17.5 20 6.5",
  arrow: "M5 12h14M13 6l6 6-6 6",
  back: "M19 12H5M11 18l-6-6 6-6",
  plus: "M12 5v14M5 12h14",
  spark: "M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6",
  refresh: "M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7",
  flag: "M5 21V4h11l-2 4 2 4H5",
  diamond: "M12 2 22 12 12 22 2 12z",
  eye: "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
  link: "M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1",
  demo: "M4 5h16v10H4zM9 19h6M12 15v4M10 8.5v3.5l3-1.75z",
  layers: "M12 3 2 8l10 5 10-5zM2 16l10 5 10-5M2 12l10 5 10-5",
  bolt: "M13 2 4 14h7l-1 8 9-12h-7z",
  undo: "M9 14 4 9l5-5M4 9h11a5 5 0 0 1 0 10h-3",
  send: "M22 2 11 13M22 2 15 22l-4-9-9-4z",
  sun: "M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4",
  moon: "M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z",
  table: "M3 5h18v14H3zM3 10h18M3 15h18M9 5v14",
  check2: "M20 6 9 17l-5-5",
  edit: "M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4",
};

export function icon(name, cls) {
  const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  s.setAttribute("viewBox", "0 0 24 24");
  s.setAttribute("fill", "none");
  s.setAttribute("stroke-width", "1.6");
  s.setAttribute("stroke-linecap", "round");
  s.setAttribute("stroke-linejoin", "round");
  s.setAttribute("aria-hidden", "true");
  if (cls) s.setAttribute("class", cls);
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
  p.setAttribute("d", P[name] || P.spark);
  s.appendChild(p);
  return s;
}

export function brandMark() {
  const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  s.setAttribute("viewBox", "0 0 32 32");
  s.setAttribute("class", "mark");
  s.innerHTML = `<defs><linearGradient id="bm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" style="stop-color:var(--accent)"/><stop offset="1" style="stop-color:var(--agent)"/></linearGradient></defs>
    <circle cx="16" cy="16" r="13.5" fill="none" stroke="url(#bm)" stroke-width="1.4" opacity=".55"/>
    <ellipse cx="16" cy="16" rx="13.5" ry="5.2" fill="none" stroke="url(#bm)" stroke-width="1.2" transform="rotate(-28 16 16)" opacity=".9"/>
    <circle cx="16" cy="16" r="3.6" style="fill:var(--human)"/><circle cx="27.4" cy="10.2" r="1.7" style="fill:var(--agent)"/>`;
  return s;
}
