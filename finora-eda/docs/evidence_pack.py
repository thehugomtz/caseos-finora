"""Evidence pack · pruebas de sensibilidad de los hallazgos verificados (sep-2026).

    python3 docs/evidence_pack.py

Solo lee `data/raw/` con las mismas funciones del pipeline (panel exacto en micro-unidades) e imprime las
tablas de sensibilidad. Las cifras canónicas están en el registro de afirmaciones (finora_eda.py ·
verification_views → C-ADQ-07..09, C-RES-08, C-RET-03..04, C-DAT-06..09). Montos en COP nominales
(amount × 10.000); el gasto de S&M queda en su unidad reportada (u), sin convertir.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from finora_eda import (audit_industry, audit_transactions, build_customer_month, read_raw,  # noqa: E402
                        verification_views)

pd.set_option("display.width", 220)
raw = read_raw(REPO / "data" / "raw")
industry, _ = audit_industry(raw["industry"])
tx, _ = audit_transactions(raw["transactions"])
cm, ar = build_customer_month(tx.assign(customer_id=tx.customer_id.astype(int)), industry)
A, first, ind = ar["A"], ar["first_idx"], np.asarray(ar["ind"])
COP = A / 100.0
months = [str(m) for m in ar["months"]]
n, T = A.shape
CLEAN = 2
yr = np.array([m[:4] for m in months])


def period(t, kind):
    y, mm = months[t][:4], int(months[t][5:])
    return y if kind == "y" else f"{y}S{1 if mm <= 6 else 2}" if kind == "h" else f"{y}Q{(mm - 1) // 3 + 1}"


def med_pos(seg):
    p = seg[seg > 0]
    return float(np.median(p)) if p.size else np.nan


rows = []
for i in np.where(first >= CLEAN)[0]:
    f = first[i]
    rows.append({"i": i, "f": f, "cohort": months[f], "y": period(f, "y"), "h": period(f, "h"), "q": period(f, "q"),
                 "m0": COP[i, f], "m1": COP[i, f + 1] if f + 1 < T else np.nan, "rr": med_pos(COP[i, f:f + 3]),
                 "m1to3": med_pos(COP[i, f + 1:f + 4]) if f + 1 < T else np.nan,
                 "usual": ar["usual"][i] / 100.0, "industry": ind[i]})
NC = pd.DataFrame(rows)
MO = {k: NC.groupby(k).cohort.nunique() for k in ("y", "h", "q")}
MED22 = NC.loc[NC.y == "2022", "rr"].median()


def section(title):
    print("\n" + "=" * 100 + f"\n{title}\n" + "=" * 100)


# ---------------------------------------------------------------------------------------------- canónicas
section("Cifras canónicas (verification_views, las mismas del registro)")
V = verification_views(ar, CLEAN)
for k, v in V.items():
    print(f"  {k:28s} {v:,.4f}" if isinstance(v, float) else f"  {k:28s} {v}")

# ---------------------------------------------------------------------------------------------- 1 · altas por nivel
section("1 · ¿De dónde viene el aumento de altas? (altas por mes)")
pm = lambda mask, k="y": NC[mask].groupby(k).size().reindex(MO[k].index, fill_value=0) / MO[k]
tot = pm(NC.i >= 0)
print("altas por mes:", tot.round(1).to_dict())
print("\nA. corte = mediana de 2022 de cada medida (parte 2022 en 50/50)")
for meas in ("rr", "usual", "m0", "m1to3", "m1"):
    s = NC.dropna(subset=[meas])
    if meas == "m1to3":
        s = s[s.f + 3 <= T - 1]                       # M1..M3 observables (cohortes hasta jul-24)
    mo = s.groupby("y").cohort.nunique()
    med = s.loc[s.y == "2022", meas].median()
    hi, lo = s[s[meas] >= med].groupby("y").size() / mo, s[s[meas] < med].groupby("y").size() / mo
    tt = hi + lo
    print(f"  {meas:6s} mediana2022 COP {med:>8,.0f} | arriba {hi.round(1).to_dict()} | abajo {lo.round(1).to_dict()} | "
          f"% del aumento 2022→2024 desde abajo {(lo['2024'] - lo['2022']) / (tt['2024'] - tt['2022']):.0%}")
print("\nB. bandas por cuartiles de 2022 (run-rate M0–M2)")
q = NC.loc[NC.y == "2022", "rr"].quantile([.25, .5, .75]).to_list()
NC["qb"] = pd.cut(NC.rr, [-1, q[0], q[1], q[2], 1e12], labels=["Q1", "Q2", "Q3", "Q4"], right=False)
for k in ("y", "h"):
    tab = NC.groupby([k, "qb"], observed=False).size().unstack().div(MO[k], axis=0)
    print(tab.round(1).to_string())
inc = NC[NC.y == "2024"].qb.value_counts() / 10 - NC[NC.y == "2022"].qb.value_counts() / 10
print("participación de cada cuartil en el aumento 2022→2024:", (inc / inc.sum()).round(2).sort_index().to_dict(), "| cortes COP", [round(x) for x in q])
print("\nC. umbrales fijos: altas por mes por encima (2022 → 2023 → 2024)")
for thr in (21000, 31500, 42000, 52500, 63000, 84000, 105000):
    print(f"  ≥ COP {thr:>7,}: " + " | ".join(f"{meas}: " + " → ".join(f"{v:.1f}" for v in pm(NC[meas] >= thr).values)
                                          for meas in ("rr", "usual", "m1")))
print("\nD. percentiles del run-rate por año (COP)")
print(NC.groupby("y").rr.quantile([.1, .25, .5, .75, .9]).unstack().round(0).to_string())
print("\nE. medianas por cliente nuevo (COP):", NC.groupby("y")[["m0", "rr", "usual", "m1to3"]].median().round(0).to_dict("index"))

# ---------------------------------------------------------------------------------------------- 2 · valor
section("2 · Valor inicial incorporado por mes (COP millones)")
for k in ("y", "h", "q"):
    t = pd.DataFrame({meas: NC.groupby(k)[meas].sum() / MO[k] / 1e6 for meas in ("m0", "rr", "usual")})
    s3 = NC[NC.f + 3 <= T - 1]
    t["m1to3*"] = s3.groupby(k).m1to3.sum() / s3.groupby(k).cohort.nunique() / 1e6
    t["altas/mes"] = NC.groupby(k).size() / MO[k]
    print(t.round(2).to_string(), "\n")
print("* m1to3: cohortes hasta jul-24")
mon = NC.groupby("cohort").agg(rr=("rr", "sum"), n=("i", "size")).reindex(months[CLEAN:], fill_value=0)
for col in ("rr", "n"):
    for lab, a in (("mar-22..oct-24", 0), ("ene-23..oct-24", 10)):
        y = mon[col].to_numpy()[a:] / (1e6 if col == "rr" else 1)
        x = np.arange(len(y), dtype=float)
        X = np.c_[np.ones_like(x), x]
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        se = np.sqrt(((y - X @ b) @ (y - X @ b)) / (len(y) - 2) * np.linalg.inv(X.T @ X)[1, 1])
        print(f"  tendencia {col:2s} {lab}: media {y.mean():.2f} | pendiente {b[1]:+.3f}/mes (IC95 {b[1] - 1.96 * se:+.3f} a {b[1] + 1.96 * se:+.3f})")

# ---------------------------------------------------------------------------------------------- 3 · retención por nivel
section(f"3 · Retención de logos por nivel (corte: mediana 2022 del run-rate, COP {MED22:,.0f})")
NC["nivel"] = np.where(NC.rr >= MED22, "alto", "bajo")
for k in (3, 6, 12, 18):
    sub = NC[NC.f + k + 1 <= T - 1].copy()
    sub["act"] = [COP[i, f + k] > 0 for i, f in zip(sub.i, sub.f)]
    sub["act2"] = [(COP[i, f + k] > 0) or (COP[i, f + k + 1] > 0) for i, f in zip(sub.i, sub.f)]
    for y in ("2022", "2023", "2024"):
        s = sub[sub.y == y]
        a, b = s[s.nivel == "bajo"], s[s.nivel == "alto"]
        if len(a) < 20 or len(b) < 20:
            continue
        d = a.act.mean() - b.act.mean()
        se = np.sqrt(a.act.mean() * (1 - a.act.mean()) / len(a) + b.act.mean() * (1 - b.act.mean()) / len(b))
        print(f"  M{k:<2} cohorte {y}: bajo {a.act.mean():.0%} (n={len(a)}) vs alto {b.act.mean():.0%} (n={len(b)}) → "
              f"dif {d:+.1%} [IC95 {d - 1.96 * se:+.1%}, {d + 1.96 * se:+.1%}] | activo en Mk o Mk+1: {a.act2.mean():.0%} vs {b.act2.mean():.0%}")

# ---------------------------------------------------------------------------------------------- 4 · expansión
section("4 · Expansión: monto pagado de la cohorte en Mk frente a su base (churn cuenta como cero)")
for k in (6, 12, 18, 24):
    for y in ("2022", "2023"):
        sub = NC[(NC.y == y) & (NC.f + k + 1 <= T - 1)]
        if len(sub) < 30:
            continue
        num = np.array([COP[i, f + k] for i, f in zip(sub.i, sub.f)])
        for base in ("rr", "m1"):
            den = sub[base].fillna(0).to_numpy()
            alive = num > 0
            print(f"  M{k:<2} cohortes {y} (n={len(sub)}) base {base:2s}: {num.sum() / den.sum():.0%} | "
                  f"solo activos en Mk {num[alive].sum() / den[alive].sum():.0%} | logos activos {alive.mean():.0%}")
print("  (la base M1 de 2022 está deprimida: 8% de las altas de 2022 no paga en M1 y 15% paga en M0 más de 1,5× M1)")
base = first == 0
surv = base & (A[:, 0] > 0) & (A[:, -1] > 0)
print(f"\n  contabilidad ene-22 → oct-24: total {COP[:, 0].sum() / 1e6:.1f} → {COP[:, -1].sum() / 1e6:.1f} M | base previa "
      f"{COP[base, 0].sum() / 1e6:.1f} → {COP[base, -1].sum() / 1e6:.1f} M | clientes posteriores {COP[~base, -1].sum() / 1e6:.1f} M")
print(f"  supervivientes de la base: {surv.sum()} ({surv.sum() / base.sum():.0%}); monto oct-24/ene-22 {COP[surv, -1].sum() / COP[surv, 0].sum():.2f}× "
      f"| promedios de 3 meses {COP[surv, -3:].mean(1).sum() / COP[surv, :3].mean(1).sum():.2f}×")

# ---------------------------------------------------------------------------------------------- 5 · firmas de cobro
section("5 · Firmas de cobro en `amount`")
E = []
for t in range(CLEAN, T):
    for i in np.where((A[:, t - 1] > 0) & (A[:, t] == 0))[0]:
        nxt = np.flatnonzero(A[i, t + 1:] > 0)
        E.append({"t": t, "i": i, "ret": (int(nxt[0]) + 1) if nxt.size else np.nan})
E = pd.DataFrame(E)
obs = E[E.t < T - 1]
r1 = obs[obs.ret == 1]
dbl = np.mean([abs(A[i, t + 1] - 2 * A[i, t - 1]) <= 0.02 * A[i, t - 1] for i, t in zip(r1.i, r1.t)])
same = np.mean([A[i, t + 1] == A[i, t - 1] for i, t in zip(r1.i, r1.t)])
print(f"  churns con mes siguiente observable: {len(obs)}; vuelven al mes siguiente {len(r1) / len(obs):.0%} "
      f"(con el mismo monto {same:.0%}; con el doble ±1% {dbl:.0%})")
print(f"  retornos que liquidan exactamente los meses pendientes ((g+1)× el monto previo, ±1%): {V['catchup_returns']} de {V['catchup_n']} ({V['catchup_share']:.0%})")
sig = ar["signature"]
print(f"  meses-cliente = k× el monto usual (k=2..12; usual visto ≥3 veces; ±0,5%): {int((sig > 0).sum())} en {int((sig > 0).any(axis=1).sum())} clientes")
print(f"  jun-22: {V['jun22_churn']} churns (mediana mensual {V['churn_month_median']:.0f}); vuelven al mes siguiente {V['jun22_back_next']:.0%}")

# ---------------------------------------------------------------------------------------------- 6 · idas y vueltas
section("6 · Idas y vueltas de un mes en el movimiento bruto (sin altas)")
eb = ar["ever_before"]
M = []
for t in range(CLEAN, T):
    a0, a1 = A[:, t - 1], A[:, t]
    for i in np.where((a0 != a1) & ((a0 > 0) | eb[:, t]))[0]:
        k = "expansión" if a0[i] > 0 and a1[i] > a0[i] else "contracción" if a0[i] > 0 and a1[i] > 0 else "churn" if a0[i] > 0 else "reactivación"
        M.append((i, t, k, int(a0[i]), int(a1[i]), abs(int(a1[i]) - int(a0[i])) / 100.0))
M = pd.DataFrame(M, columns=["i", "t", "tipo", "a0", "a1", "v"])


def close(x, y, tol):
    return x == y if (tol == 0 or x == 0 or y == 0) else abs(x - y) <= tol * y


def classify(tol, last):
    out = []
    for i, t, a0, a1 in zip(M.i, M.t, M.a0, M.a1):
        if t > last:
            out.append("fuera")
        elif (t + 1 < T and close(A[i, t + 1], a0, tol)) or (t - 1 >= CLEAN and close(a1, A[i, t - 2], tol) and not close(A[i, t - 1], A[i, t - 2], tol)):
            out.append("ida y vuelta")
        elif t + 1 >= T:
            out.append("sin observar")
        elif close(A[i, t + 1], a1, tol):
            out.append("persiste ≥1 mes")
        else:
            out.append("vuelve a cambiar")
    return out


for tol in (0, 0.01, 0.02):
    for lab, last in (("mar-22..sep-24", T - 2), ("mar-22..oct-24", T - 1)):
        M["c"] = classify(tol, last)
        W = M[M.c != "fuera"]
        sh = (W.groupby("c").v.sum() / W.v.sum()).round(3).to_dict()
        bt = W.assign(r=W.c == "ida y vuelta").groupby("tipo").apply(lambda g: g.v[g.r].sum() / g.v.sum(), include_groups=False).round(2).to_dict()
        print(f"  tol {tol:.0%} · {lab}: bruto COP {W.v.sum() / 1e6:.1f} M | {sh} | por tipo {bt}")
M["c"] = classify(0, T - 2)
W = M[M.c != "fuera"].copy()
W["y"] = [yr[t] for t in W.t]
print("  por año (exacto):", W.groupby("y").apply(lambda g: round(g.v[g.c == "ida y vuelta"].sum() / g.v.sum(), 3), include_groups=False).to_dict())
W2 = W[~W.t.isin([months.index("2022-06"), months.index("2022-07")])]
print(f"  sin jun-22/jul-22: {W2.v[W2.c == 'ida y vuelta'].sum() / W2.v.sum():.1%}")
ret2 = [(c == "ida y vuelta") or (t + 2 < T and A[i, t + 2] == a0) for i, t, a0, c in zip(W.i, W.t, W.a0, W.c)]
print(f"  variante: vuelve exacto al nivel previo en ≤2 meses: {W.v[np.array(ret2)].sum() / W.v.sum():.1%}")

# ---------------------------------------------------------------------------------------------- 7 · churn
section("7 · Churn observado vs durable (Σ eventos / Σ activos del mes previo)")
act_prev = {t: int((A[:, t - 1] > 0).sum()) for t in range(CLEAN, T)}
for h in (1, 2, 3, 4, 6):
    out = []
    for y in ("2022", "2023", "2024"):
        ts = [t for t in range(CLEAN, T - h) if yr[t] == y]
        den = sum(act_prev[t] for t in ts)
        e = E[E.t.isin(ts)]
        dur = (e.ret.isna() | (e.ret > h)).sum() / den
        out.append(f"{y}: obs {len(e) / den:.2%} · vuelve≤{h} {len(e) / den - dur:.2%} · durable {dur:.2%}")
    print(f"  h={h} (eventos hasta {months[T - 1 - h]}): " + " | ".join(out))
for lab, sel in (("mismos meses mar–jul", lambda t: int(months[t][5:]) in (3, 4, 5, 6, 7)), ("2022 sin jun-22", lambda t: months[t] != "2022-06")):
    out = []
    for y in ("2022", "2023", "2024"):
        ts = [t for t in range(CLEAN, T - 3) if yr[t] == y and sel(t)]
        den = sum(act_prev[t] for t in ts)
        e = E[E.t.isin(ts)]
        out.append(f"{y}: obs {len(e) / den:.2%} · durable(3) {(e.ret.isna() | (e.ret > 3)).sum() / den:.2%}")
    print(f"  {lab}: " + " | ".join(out))

# ---------------------------------------------------------------------------------------------- 8 · ajustes sincronizados
section("8 · Ajustes sincronizados con cobro retroactivo (sube k·x, al mes siguiente queda en +x y persiste; tol 0,05 pp)")
F = []
for t in range(CLEAN, T - 1):
    for i in np.where((A[:, t - 1] > 0) & (A[:, t] > 0) & (A[:, t + 1] > 0) & (A[:, t] != A[:, t - 1]))[0]:
        p, a, nx = float(A[i, t - 1]), float(A[i, t]), float(A[i, t + 1])
        r1, r2 = a / p - 1, nx / p - 1
        if r2 < 0.001 or not ((t + 2 >= T) or A[i, t + 2] == A[i, t + 1]):
            continue
        for k in (2, 3, 4, 5, 6):
            if abs(r1 - k * r2) <= 0.0005 * k:
                F.append({"mes": months[t], "k": k, "neto_%": round(r2 * 100, 2), "primer_%": round(r1 * 100, 2), "i": i,
                          "base_cop": p / 100, "neto_cop": (nx - p) / 100, "industria": ind[i]})
                break
F = pd.DataFrame(F)
g = F.groupby(["mes", "k", "neto_%"]).agg(clientes=("i", "size"), primer=("primer_%", "first"), bases_distintas=("base_cop", "nunique"),
                                          industrias=("industria", "nunique"), neto_cop=("neto_cop", "sum"))
print(g[g.clientes >= 3].round(2).to_string())
print(f"  total: {len(F)} eventos en {F.i.nunique()} clientes")
O = []
for t in range(CLEAN, T - 1):
    for i in np.where((A[:, t - 1] > 0) & (A[:, t] > A[:, t - 1]) & (A[:, t + 1] == A[:, t]))[0]:
        O.append({"mes": months[t], "pct": round((A[i, t] / A[i, t - 1] - 1) * 100, 2), "i": i, "d": (A[i, t] - A[i, t - 1]) / 100})
O = pd.DataFrame(O)
O["n"] = O.groupby(["mes", "pct"]).i.transform("size")
print("\n  subidas de un paso que persisten, mismo % en ≥5 clientes el mismo mes:")
print(O[O.n >= 5].groupby(["mes", "pct"]).agg(clientes=("i", "size"), cop=("d", "sum")).round(0).to_string())
t1, t2 = months.index("2022-12"), months.index("2023-06")
okb = (A[:, t1] > 0) & (A[:, t2] > 0)
print(f"\n  alcance 2023: activos en dic-22 y jun-23 {okb.sum()} | jun-23/dic-22 = 1,0545 (±0,05 pp) {int((np.abs(A[okb, t2] / A[okb, t1] - 1.0545) <= 0.0005).sum())} "
      f"| sin cambio {int((A[okb, t2] == A[okb, t1]).sum())}")
print(f"  peso en el puente: tramo de subida = {V['retro_exp_share_2023']:.1%} (2023) y {V['retro_exp_share_2024']:.1%} (2024) de la expansión del año; "
      f"aumento neto que persiste COP {V['retro_net_2023'] / 1e3:,.0f} mil y {V['retro_net_2024'] / 1e3:,.0f} mil")

# ---------------------------------------------------------------------------------------------- 9 · lectura temporal
section("9 · Lectura temporal (altas, valor run-rate, S&M en u)")
mm = pd.read_csv(REPO / "finora_monthly_metrics.csv")
mm = mm[mm.window_flag == "clean"].set_index("month")
df = pd.DataFrame({"altas": mm.new_customers, "valor_rr_M": NC.groupby("cohort").rr.sum().reindex(mm.index, fill_value=0) / 1e6,
                   "paid_media_u": mm.paid_media, "sm_total_u": mm.total_sm_spend})
df["mes"], df["y"] = df.index.str[5:].astype(int), df.index.str[:4]
P = []
for lab, sel in (("2022 mar–jun", (df.y == "2022") & (df.mes <= 6)), ("2022 jul–dic", (df.y == "2022") & (df.mes >= 7)),
                 ("2023 ene–jun", (df.y == "2023") & (df.mes <= 6)), ("2023 jul–dic", (df.y == "2023") & (df.mes >= 7)),
                 ("2024 ene–jun", (df.y == "2024") & (df.mes <= 6)), ("2024 jul–oct", (df.y == "2024") & (df.mes >= 7)),
                 ("2023 jul–oct", (df.y == "2023") & df.mes.between(7, 10)), ("ene-23..jun-24", (df.index >= "2023-01") & (df.index <= "2024-06"))):
    P.append({"periodo": lab, "meses": int(sel.sum()), **df[sel][["altas", "valor_rr_M", "paid_media_u", "sm_total_u"]].mean().round(2).to_dict()})
print(pd.DataFrame(P).set_index("periodo").to_string())
post = df[df.index >= "2023-01"].altas
h2 = df[(df.index >= "2023-07") & (df.index <= "2023-12")].altas
rest = post.drop(h2.index)
print(f"  ene-23..oct-24: media {post.mean():.1f}, DE mensual {post.std():.1f} | jul–dic 2023 vs resto: {h2.mean() - rest.mean():+.1f} altas/mes "
      f"= {(h2.mean() - rest.mean()) / (rest.std() / np.sqrt(len(h2))):.1f} errores estándar")
print(f"  pendiente desde ene-23 (registro): {V['plateau_slope']:+.2f}/mes (IC95 {V['plateau_lo']:+.2f} a {V['plateau_hi']:+.2f})")
print("  media móvil de 6 meses de altas:", df.altas.rolling(6).mean().dropna().round(1).iloc[::3].to_dict())

# ---------------------------------------------------------------------------------------------- 10 · industria
section("10 · ¿Mezcla de industrias? (participación de altas bajo la mediana 2022)")
NC["bajo"] = NC.rr < MED22
sh = NC.groupby(["industry", "y"]).bajo.mean().unstack()
cnt = NC.groupby(["industry", "y"]).size().unstack()
print((sh * 100).round(0).to_string())
w0, w1 = cnt["2022"] / cnt["2022"].sum(), cnt["2024"] / cnt["2024"].sum()
s0, s1 = sh["2022"], sh["2024"]
print(f"  {(w0 * s0).sum():.1%} → {(w1 * s1).sum():.1%} = mezcla {((w1 - w0) * (s0 + s1) / 2).sum():+.1%} + dentro {((s1 - s0) * (w0 + w1) / 2).sum():+.1%}")
