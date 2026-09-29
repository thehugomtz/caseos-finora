// REST + SSE client. Every call is scoped to the active case.
export class ApiError extends Error { constructor(status, detail) { super(detail); this.status = status; } }

async function req(method, path, body) {
  const r = await fetch(path, { method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined });
  let data = null;
  try { data = await r.json(); } catch (e) { data = null; }
  if (!r.ok) throw new ApiError(r.status, (data && data.detail) || r.statusText);
  return data;
}

export const api = {
  get: p => req("GET", p),
  post: (p, b) => req("POST", p, b || {}),
  patch: (p, b) => req("PATCH", p, b || {}),
  c: null,                                   // active case id
  cp: p => `/api/cases/${api.c}${p}`,
  cget: p => req("GET", api.cp(p)),
  cpost: (p, b) => req("POST", api.cp(p), b || {}),
  cpatch: (p, b) => req("PATCH", api.cp(p), b || {}),
  cput: (p, b) => req("PUT", api.cp(p), b || {}),
  cdel: p => req("DELETE", api.cp(p)),
  action: (id, action, payload) => req("POST", api.cp(`/entities/${id}/actions/${action}`), { payload: payload || {} }),
};

export function events(caseId, onEvent) {
  const es = new EventSource(`/api/cases/${caseId}/events`);
  es.onmessage = e => { try { onEvent(JSON.parse(e.data)); } catch (err) { /* ignore */ } };
  return es;
}
