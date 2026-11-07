#!/usr/bin/env python3
"""
tamprc_mc.py -- Monte Carlo suite for the Thermally Assisted Motorized Pipeline
Remediation Crawler (TAMPRC).

One file, numpy + scipy + matplotlib only (design contract borrowed from the
MyUncle maintenance-lattice framework: single importable file, seeded, one-call
figure suite, plain JSON/PNG/Markdown outputs).

Modules
  A  Transient thermal shield  : 1-D cylindrical conduction through shell /
     silica aerogel / Ti hull (finite volume, backward Euler) coupled to a lumped
     battery pack; steam film h from the Nusselt correlation.  Output: probability
     the pack stays <= T_crit for the 45 min mission; endurance-time distribution.
  B  Condensation / deposit mobilisation : film-condensation flux -> melt time ->
     thermally limited crawl speed -> range per deployment, steam use.
  C  Anti-dieseling : blockage break-through transient for (1) passive pig,
     (2) crawler with regenerative braking only, (3) crawler + seal-differential bypass relief.
  D  Deposit-maintenance lattice : fouling (erosion of order) vs crawler passes
     (repair) on a periodic lattice; kinetic MC checked against the exact
     mean-field result for the non-interacting case.

ALL INPUT DISTRIBUTIONS ARE ASSUMED/ILLUSTRATIVE design-stage values, not
measurements.  Replace them with test data before drawing engineering conclusions.

Usage:  python tamprc_mc.py --all            # full suite (figures + results.json)
        python tamprc_mc.py --quick          # small-N smoke test
"""
import json, os, sys, time, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

SEED = 20260601
OUT = "tamprc_out"

# ----------------------------------------------------------------------------
# Saturated steam properties near 1.55 MPa / 200 C (IAPWS-IF97 tabulated values)
# ----------------------------------------------------------------------------
G = 9.81
STEAM = dict(hfg=1940.7e3, rho_l=864.7, rho_v=7.86, k_l=0.663, mu_l=1.34e-4,
             cp_l=4.50e3)

def h_cond(Tsat, Tw, D, mult=1.0):
    """Nusselt film-condensation coefficient, as written in the framework (Eq. 2.2)."""
    s = STEAM
    hfgp = s["hfg"] + 0.68 * s["cp_l"] * (Tsat - Tw)
    dT = np.maximum(Tsat - Tw, 1.0)
    return mult * 0.728 * ((G * s["rho_l"] * (s["rho_l"] - s["rho_v"]) * s["k_l"] ** 3 * hfgp)
                           / (s["mu_l"] * D * dT)) ** 0.25

def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

# ----------------------------------------------------------------------------
# Module A : transient thermal shield
# ----------------------------------------------------------------------------
GEOM = dict(r_pack=0.060, t_shell=0.004, t_hull=0.004, L=1.2)   # m
D_PIPE = 0.30                                                   # m (12 in ID)
MAT = dict(  # k [W/mK], rho*cp [J/m3K]
    shell=(167.0, 2700 * 900.0), hull=(7.5, 4430 * 560.0), aero_rhocp=150 * 1000.0)

def k_aero(T, vacuum):
    if vacuum:
        return 0.0040 + 2.5e-5 * (T - 25.0)
    return 0.0180 + 8.0e-5 * (T - 25.0)          # atmospheric-pressure aerogel

def thomas(a, b, c, d):
    """Batched tridiagonal solve. a:(N,m-1) lower, b:(N,m), c:(N,m-1) upper, d:(N,m)."""
    m = b.shape[1]
    cp = np.empty((b.shape[0], m - 1)); dp = np.empty_like(d)
    cp[:, 0] = c[:, 0] / b[:, 0]; dp[:, 0] = d[:, 0] / b[:, 0]
    for i in range(1, m):
        den = b[:, i] - a[:, i - 1] * cp[:, i - 1]
        if i < m - 1:
            cp[:, i] = c[:, i] / den
        dp[:, i] = (d[:, i] - a[:, i - 1] * dp[:, i - 1]) / den
    x = np.empty_like(d); x[:, -1] = dp[:, -1]
    for i in range(m - 2, -1, -1):
        x[:, i] = dp[:, i] - cp[:, i] * x[:, i + 1]
    return x

def sample_thermal(N, rng, aero_mm=40.0, vacuum=False):
    p = {}
    p["t_a"] = aero_mm / 1000.0 * (1 + rng.normal(0, 0.03, N))
    p["k_mult"] = rng.lognormal(0, 0.15, N)                  # compaction / moisture / lot variation
    if vacuum:
        p["k_mult"] = p["k_mult"] * rng.lognormal(0, 0.30, N)
        p["vac_lost"] = rng.random(N) < 0.05                 # 5 % chance vacuum jacket degraded
    else:
        p["vac_lost"] = np.zeros(N, bool)
    p["phi_br"] = rng.uniform(0.05, 0.30, N)                 # thermal-bridge conductance fraction
    p["P_gen"] = rng.lognormal(np.log(70.0), 0.35, N)        # W, motors+electronics+cell I^2R
    p["m_pack"] = rng.normal(16.0, 1.2, N)                   # kg
    p["T0"] = rng.normal(25.0, 4.0, N)
    p["Tsat"] = np.clip(rng.normal(198.0, 3.0, N), 185, 204)
    p["h_mult"] = rng.lognormal(0, 0.15, N)                  # correlation uncertainty
    return p

def run_thermal(p, vacuum=False, t_end=7200.0, dt=10.0, ns=2, na=16, nh=2, Tcrit=55.0):
    N = len(p["t_a"]); n = ns + na + nh; L = GEOM["L"]
    r0 = np.full(N, GEOM["r_pack"]); r1 = r0 + GEOM["t_shell"]; r2 = r1 + p["t_a"]; r3 = r2 + GEOM["t_hull"]
    seg = lambda a, b, m: a[:, None] + (b - a)[:, None] * np.linspace(0, 1, m + 1)[None, :]
    f = np.concatenate([seg(r0, r1, ns), seg(r1, r2, na)[:, 1:], seg(r2, r3, nh)[:, 1:]], axis=1)
    rc = 0.5 * (f[:, 1:] + f[:, :-1]); vol = np.pi * (f[:, 1:] ** 2 - f[:, :-1] ** 2)
    layer = np.array([0] * ns + [1] * na + [2] * nh)
    rhocp = np.where(layer == 0, MAT["shell"][1], np.where(layer == 1, MAT["aero_rhocp"], MAT["hull"][1]))
    kfix = np.where(layer == 0, MAT["shell"][0], MAT["hull"][0]).astype(float)
    Cc = rhocp[None, :] * vol                                   # J/(m K)
    C = np.concatenate([(p["m_pack"] * 900.0 / L)[:, None], Cc], axis=1)
    T = np.concatenate([p["T0"][:, None], np.repeat(p["T0"][:, None], n, axis=1)], axis=1)
    h_in = 15.0
    # parallel bridge conductance (tracks, end caps) as fraction of nominal aerogel conductance
    kn = k_aero(25.0, False) * np.ones(N)
    Gbr = p["phi_br"] * 2 * np.pi * kn / np.log(r2 / r1)
    r_out = r3
    steps = int(t_end / dt); Tp_hist = np.empty((N, steps + 1)); Tp_hist[:, 0] = T[:, 0]
    k_eff_m = p["k_mult"]
    for s in range(steps):
        Tc = T[:, 1:]
        ka = k_aero(Tc, vacuum)
        if vacuum:   # degraded jacket -> atmospheric-pressure behaviour
            ka = np.where(p["vac_lost"][:, None], k_aero(Tc, False), ka)
        kc = np.where(layer[None, :] == 1, ka * k_eff_m[:, None], kfix[None, :])
        rf = f[:, 1:-1]
        R = np.log(rf / rc[:, :-1]) / (2 * np.pi * kc[:, :-1]) + np.log(rc[:, 1:] / rf) / (2 * np.pi * kc[:, 1:])
        Gm = 1.0 / R                                           # (N, n-1) between cells
        R0 = np.log(rc[:, 0] / r0) / (2 * np.pi * kc[:, 0]) + 1.0 / (2 * np.pi * r0 * h_in)
        G0 = 1.0 / R0
        hs = np.minimum(h_cond(p["Tsat"], T[:, -1], 2 * r_out, p["h_mult"]), 12000.0)
        Rs = np.log(r_out / rc[:, -1]) / (2 * np.pi * kc[:, -1]) + 1.0 / (2 * np.pi * r_out * hs)
        Gs = 1.0 / Rs
        m = n + 1
        d = C / dt; lo = np.zeros((N, m - 1)); up = np.zeros((N, m - 1)); rhs = C / dt * T
        # pack <-> cell0
        d[:, 0] += G0; d[:, 1] += G0; lo[:, 0] = -G0; up[:, 0] = -G0
        # cell j <-> j+1  (node indices j+1, j+2)
        d[:, 1:-1] += Gm; d[:, 2:] += Gm
        lo[:, 1:] = -Gm; up[:, 1:] = -Gm
        # steam BC on last cell
        d[:, -1] += Gs; rhs[:, -1] += Gs * p["Tsat"]
        # generation in pack
        rhs[:, 0] += p["P_gen"] / L
        # bridge (semi-implicit split)
        d[:, 0] += Gbr; d[:, -1] += Gbr
        rhs[:, 0] += Gbr * T[:, -1]; rhs[:, -1] += Gbr * T[:, 0]
        T = thomas(lo, d, up, rhs)
        Tp_hist[:, s + 1] = T[:, 0]
    t = np.arange(steps + 1) * dt
    over = Tp_hist >= Tcrit
    first = np.where(over.any(axis=1), over.argmax(axis=1), steps)
    t_crit = t[first].astype(float)
    t_crit[~over.any(axis=1)] = t_end
    i45 = int(2700 / dt)
    return dict(t=t, Tp=Tp_hist, t_crit=t_crit, Tp45=Tp_hist[:, i45], censored=~over.any(axis=1))

# ----------------------------------------------------------------------------
# Module B : condensation, deposit mobilisation, range
# ----------------------------------------------------------------------------
def deposit_mobilisation(N, rng, Tsat, h_mult, t_run, v_set=0.10):
    d = {}
    d["delta"] = np.clip(rng.lognormal(np.log(6e-3), 0.5, N), 1e-3, 40e-3)     # m
    d["T_melt"] = np.clip(rng.normal(58.0, 8.0, N), 40, 90)                   # C
    d["rho"] = rng.normal(850.0, 40.0, N)
    d["Lf"] = np.clip(rng.normal(200e3, 30e3, N), 100e3, 300e3)
    d["c"] = 2100.0
    d["T_pipe"] = rng.normal(25.0, 5.0, N)
    d["eta"] = rng.uniform(0.15, 0.50, N)                 # fraction of film flux reaching deposit
    d["m_nc"] = rng.uniform(0.5, 1.0, N)                  # non-condensable-gas degradation
    d["Lz"] = rng.uniform(0.3, 0.8, N)                    # steam contact zone length ahead of seal
    h = h_cond(Tsat, d["T_melt"], D_PIPE, h_mult * d["m_nc"])
    q_raw = h * (Tsat - d["T_melt"])
    q_eff = d["eta"] * q_raw
    e = d["rho"] * d["delta"] * (d["Lf"] + d["c"] * (d["T_melt"] - d["T_pipe"]))   # J/m2
    t_melt = e / q_eff
    v_th = d["Lz"] / t_melt
    v = np.minimum(v_set, v_th)
    rng_m = v * t_run
    hfgp = STEAM["hfg"] + 0.68 * STEAM["cp_l"] * (Tsat - d["T_melt"])
    mdot = q_raw * np.pi * D_PIPE * d["Lz"] / hfgp          # kg/s steam condensed
    steam_per_m = mdot / v
    return dict(h=h, q_raw=q_raw, q_eff=q_eff, t_melt=t_melt, v_th=v_th, v=v, range=rng_m,
                steam_kg_per_m=steam_per_m, delta=d["delta"], T_melt=d["T_melt"], eta=d["eta"],
                m_nc=d["m_nc"], Lz=d["Lz"])

# ----------------------------------------------------------------------------
# Module C : anti-dieseling transient
# ----------------------------------------------------------------------------
A_PIPE = np.pi / 4 * D_PIPE ** 2

def sample_blockage(N, rng):
    b = {}
    b["dPb"] = np.clip(rng.lognormal(np.log(3.0), 0.6, N), 0.5, 25.0) * 1e5     # Pa break-through
    b["Vg"] = np.clip(rng.lognormal(0.0, 0.7, N), 0.2, 10.0)                    # m3 upstream gas pocket
    b["Pd"] = rng.uniform(5, 30, N) * 1e5                                       # Pa downstream abs
    b["Ff"] = rng.lognormal(np.log(400.0), 0.3, N)                              # N seal friction
    b["cd"] = rng.lognormal(np.log(2000.0), 0.3, N)                             # N s2/m2 downstream drag
    b["m_pig"] = rng.normal(80.0, 8.0, N)
    b["m_cr"] = rng.normal(120.0, 10.0, N)
    b["Fb"] = np.clip(rng.normal(2500.0, 400.0, N), 500, None)                  # N regen brake limit
    b["Ft"] = np.clip(rng.normal(1500.0, 200.0, N), 300, None)                  # N traction limit
    b["beta_max"] = rng.uniform(0.85, 0.97, N)                                  # bypass relief authority
    b["tau_v"] = rng.uniform(0.005, 0.03, N)                                    # s relief-valve lag
    return b

def run_dieseling(b, mode, v_set=0.10, T=5.0, dt=0.001, gamma=1.3, keep_trace=False, idx=None):
    N = len(b["dPb"]); m = b["m_pig"] if mode == "passive" else b["m_cr"]
    v = np.full(N, v_set); x = np.zeros(N); I = np.zeros(N); beta = np.full(N, 0.05 if mode == "passive" else 0.0)
    vpk = v.copy(); t_over = np.zeros(N); Kp, Ki = 2e4, 2e4
    steps = int(T / dt); trace = []
    for s in range(steps):
        Pup = (b["Pd"] + b["dPb"]) * (b["Vg"] / (b["Vg"] + A_PIPE * x)) ** gamma
        F = A_PIPE * (Pup - b["Pd"]) * (1 - beta)
        e = v - v_set
        if mode == "passive":
            Fc = 0.0
        else:
            I = np.clip(I + Ki * e * dt, -b["Ft"], b["Fb"])
            Fc = np.clip(Kp * e + I, -b["Ft"], b["Fb"])
            if mode == "relief":     # seal-differential-triggered bypass relief (cracks at 0.5 bar)
                dPnow = Pup - b["Pd"]
                ub = np.clip(1 - 0.5e5 / np.maximum(dPnow, 1.0), 0, 1)
                beta = beta + dt * (b["beta_max"] * ub - beta) / b["tau_v"]
        a = (F - b["Ff"] - b["cd"] * v * v - Fc) / m
        v = np.maximum(v + a * dt, 0.0); x = x + v * dt
        vpk = np.maximum(vpk, v); t_over += (v > 5 * v_set) * dt
        if keep_trace and s % 5 == 0:
            trace.append(v[idx].copy() if idx is not None else v.copy())
    out = dict(vpk=vpk, t_over=t_over, v_end=v, x_end=x)
    if keep_trace:
        out["trace"] = np.array(trace); out["t"] = np.arange(0, steps, 5) * dt
    return out

# ----------------------------------------------------------------------------
# Module D : deposit-maintenance lattice (fouling erodes order, passes repair it)
# ----------------------------------------------------------------------------
def mean_field_fouled(x, p):
    """Exact periodic-pass steady state, non-interacting cells.
    x = r_f*T_c (fouling per cell per interval), p = P(pass clears a fouled cell).
    Returns (fouled fraction just before a pass, time-averaged fouled fraction)."""
    ex = np.exp(-x)
    fb = (1 - ex) / (1 - (1 - p) * ex)
    fa = (1 - p) * fb
    # time average over an interval starting at fa:  <f> = 1 - (1-fa)*(1-e^-x)/x
    fav = 1 - (1 - fa) * (1 - ex) / np.maximum(x, 1e-12)
    return fb, fav

def lattice_kmc(x, p, gamma, rng, nx=48, ny=24, passes=60, sub=10, burn=20, reps=3):
    """Discrete-time MC. Fouling prob per cell per sub-step = 1-exp(-(x/sub)(1+gamma*n_f/4)).
    Each pass clears each fouled cell with prob p. Returns (before-pass, time-avg)."""
    fb_all, fav_all = [], []
    for _ in range(reps):
        fouled = np.zeros((nx, ny), bool); fb_l, fav_l = [], []
        for k in range(passes):
            acc = 0.0
            for _s in range(sub):
                before = fouled.mean()
                nf = (np.roll(fouled, 1, 0).astype(int) + np.roll(fouled, -1, 0) + np.roll(fouled, 1, 1)
                      + np.roll(fouled, -1, 1))
                rate = (x / sub) * (1 + gamma * nf / 4.0)
                newly = (~fouled) & (rng.random((nx, ny)) < 1 - np.exp(-rate))
                fouled = fouled | newly
                acc += 0.5 * (before + fouled.mean())
            if k >= burn:
                fb_l.append(fouled.mean()); fav_l.append(acc / sub)
            clear = fouled & (rng.random((nx, ny)) < p)
            fouled = fouled & ~clear
        fb_all.append(np.mean(fb_l)); fav_all.append(np.mean(fav_l))
    return float(np.mean(fb_all)), float(np.mean(fav_all))

# ----------------------------------------------------------------------------
# Figures & the one-call suite
# ----------------------------------------------------------------------------
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": .25, "figure.dpi": 130,
                     "savefig.dpi": 300, "axes.spines.top": False, "axes.spines.right": False})
C1, C2, C3, C4 = "#1f4e9c", "#d1495b", "#2a9d8f", "#e9a23b"

def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name)); plt.close(fig)

def band(ax, t, Tp, color, label):
    q = np.percentile(Tp, [1, 5, 50, 95, 99], axis=0)
    ax.fill_between(t / 60, q[0], q[4], color=color, alpha=.12, lw=0)
    ax.fill_between(t / 60, q[1], q[3], color=color, alpha=.28, lw=0)
    ax.plot(t / 60, q[2], color=color, lw=1.6, label=label)

def reproduce_suite(N=5000, Nsweep=1500, Nd=20000, quick=False):
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED); R = {"seed": SEED, "N_thermal": N, "N_sweep": Nsweep, "N_dies": Nd}
    t0 = time.time()
    # ---------------- Module A: baseline (atm aerogel, 40 mm) and evacuated -----------
    res = {}
    for name, vac in (("atmospheric", False), ("evacuated", True)):
        p = sample_thermal(N, rng, 40.0, vac); r = run_thermal(p, vac); res[name] = (p, r)
        ok = int((r["Tp45"] <= 55.0).sum()); lo, hi = wilson(ok, N)
        R[f"A_{name}"] = dict(P_safe=ok / N, ci=[lo, hi], Tp45_median=float(np.median(r["Tp45"])),
                              Tp45_p95=float(np.percentile(r["Tp45"], 95)),
                              t_crit_median_min=float(np.median(r["t_crit"]) / 60),
                              t_crit_p05_min=float(np.percentile(r["t_crit"], 5) / 60),
                              frac_censored_120min=float(r["censored"].mean()))
    print("A done", round(time.time() - t0, 1), "s", R["A_atmospheric"]["P_safe"], R["A_evacuated"]["P_safe"])
    # Fig 2: fan chart
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1), sharey=True)
    for a, (name, col) in zip(ax, (("atmospheric", C1), ("evacuated", C3))):
        p, r = res[name]; band(a, r["t"], r["Tp"], col, "median")
        a.axhline(55, color=C2, ls="--", lw=1); a.axvline(45, color="k", ls=":", lw=1)
        a.set_xlim(0, 120); a.set_xlabel("Time [min]"); a.set_title(f"40 mm aerogel, {name}")
        a.text(2, 56.5, "T$_{crit}$ = 55 °C", color=C2, fontsize=8)
        a.text(46, a.get_ylim()[0] + 2, "45 min", fontsize=8)
    ax[0].set_ylabel("Battery-pack temperature [°C]")
    ax[0].set_ylim(15, 110)
    save(fig, "fig2_pack_temperature_fan.png")
    # Fig 3: endurance histograms
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    bins = np.linspace(0, 120, 49)
    for name, col in (("atmospheric", C1), ("evacuated", C3)):
        ax.hist(np.minimum(res[name][1]["t_crit"] / 60, 120), bins=bins, alpha=.55, color=col, label=name)
    ax.axvline(45, color="k", ls=":", lw=1); ax.set_xlabel("Time to reach 55 °C [min] (capped at 120)")
    ax.set_ylabel("Count"); ax.legend(frameon=False)
    save(fig, "fig3_endurance_histogram.png")
    # Fig 5: tornado (Spearman) for atmospheric baseline
    p, r = res["atmospheric"]
    keys = [("k_mult", "Aerogel k multiplier"), ("t_a", "Aerogel thickness"), ("phi_br", "Thermal-bridge fraction"),
            ("P_gen", "Internal heat generation"), ("m_pack", "Pack mass"), ("T0", "Initial temperature"),
            ("Tsat", "Steam saturation temp."), ("h_mult", "Condensation h multiplier")]
    rho = [(lab, stats.spearmanr(p[k], r["Tp45"])[0]) for k, lab in keys]
    rho.sort(key=lambda z: abs(z[1]))
    R["A_spearman_Tp45"] = {l: float(v) for l, v in rho}
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    ax.barh([l for l, _ in rho], [v for _, v in rho], color=[C2 if v > 0 else C1 for _, v in rho])
    ax.set_xlabel("Spearman ρ with pack temperature at 45 min"); ax.axvline(0, color="k", lw=.8)
    save(fig, "fig5_sensitivity_tornado.png")
    # Design sweep: thickness x scenario
    th = [5, 10, 15, 20, 30, 40, 50, 60]; sweep = {}; sweep90 = {}
    for name, vac in (("atmospheric", False), ("evacuated", True)):
        out = []; o90 = []
        for tmm in th:
            p = sample_thermal(Nsweep, rng, tmm, vac); r = run_thermal(p, vac, t_end=7200.0, dt=15.0)
            ok = int((r["Tp45"] <= 55).sum()); lo, hi = wilson(ok, Nsweep); out.append((ok / Nsweep, lo, hi))
            o90.append(float((r["t_crit"] >= 5400).mean()))
        sweep[name] = out; sweep90[name] = o90
    R["A_sweep90"] = sweep90
    R["A_sweep"] = {"thickness_mm": th, **{k: [list(map(float, v)) for v in vv] for k, vv in sweep.items()}}
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    for name, col in (("atmospheric", C1), ("evacuated", C3)):
        a_ = np.array(sweep[name]); ax.plot(th, a_[:, 0], "o-", color=col, label=name)
        ax.fill_between(th, a_[:, 1], a_[:, 2], color=col, alpha=.2, lw=0)
    ax.axhline(.95, color=C2, ls="--", lw=1); ax.text(6, .96, "95 % target", color=C2, fontsize=8)
    for name, col in (("atmospheric", C1), ("evacuated", C3)):
        ax.plot(th, sweep90[name], "x:", color=col, lw=1, label=f"{name}: 90 min")
    ax.set_xlabel("Aerogel thickness [mm]"); ax.set_ylabel("P(pack ≤ 55 °C)  [solid 45 min; dotted 90 min]"); ax.set_ylim(-.02, 1.05)
    ax.legend(frameon=False, loc="lower right", fontsize=6.5)
    save(fig, "fig4_design_sweep.png")
    print("sweep done", round(time.time() - t0, 1), "s")
    # Convergence figure
    ok = (res["atmospheric"][1]["Tp45"] <= 55).astype(float); ns = np.arange(50, N + 1, 50)
    cm = np.array([ok[:n].mean() for n in ns]); ci = np.array([wilson(ok[:n].sum(), n) for n in ns])
    fig, ax = plt.subplots(figsize=(3.8, 2.8))
    ax.plot(ns, cm, color=C1); ax.fill_between(ns, ci[:, 0], ci[:, 1], color=C1, alpha=.2, lw=0)
    ax.set_xlabel("Monte Carlo samples"); ax.set_ylabel("P$_{safe}$ (40 mm, atm.)")
    save(fig, "fig9_convergence.png")
    # ---------------- Module B -----------------
    p, r = res["atmospheric"]
    t_run = np.minimum(r["t_crit"], 2700.0)            # run ends at thermal limit or 45 min
    B = deposit_mobilisation(N, rng, p["Tsat"], p["h_mult"], t_run)
    R["B"] = dict(h_cond_median=float(np.median(B["h"])), q_raw_median_kWm2=float(np.median(B["q_raw"]) / 1e3),
                  t_melt_median_s=float(np.median(B["t_melt"])), t_melt_p95_s=float(np.percentile(B["t_melt"], 95)),
                  v_th_median_cms=float(np.median(B["v_th"]) * 100), v_th_p05_cms=float(np.percentile(B["v_th"], 5) * 100),
                  frac_thermally_limited=float((B["v_th"] < 0.10).mean()),
                  range_median_m=float(np.median(B["range"])), range_p05_m=float(np.percentile(B["range"], 5)),
                  range_p95_m=float(np.percentile(B["range"], 95)),
                  P_range_ge_100=float((B["range"] >= 100).mean()), P_range_ge_200=float((B["range"] >= 200).mean()),
                  P_range_ge_250=float((B["range"] >= 250).mean()),
                  steam_kg_per_m_median=float(np.median(B["steam_kg_per_m"])),
                  steam_kg_per_m_p95=float(np.percentile(B["steam_kg_per_m"], 95)),
                  condensate_m3_per_100m_median=float(np.median(B["steam_kg_per_m"]) * 100 / 1000))
    R["B_spearman_vth"] = {k: float(stats.spearmanr(B[k], B["v_th"])[0]) for k in ("delta", "T_melt", "eta", "m_nc", "Lz")}
    dTs = np.linspace(20, 160, 100)
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.7))
    ax[0].plot(dTs, h_cond(200.4, 200.4 - dTs, D_PIPE) / 1e3, color=C1)
    ax[0].set_xlabel("Tsat − T$_{wall}$ [K]"); ax[0].set_ylabel("h$_{cond}$ [kW m$^{-2}$ K$^{-1}$]")
    ax[1].hist(np.log10(B["t_melt"]), bins=40, color=C3, alpha=.8); ax[1].set_xlabel("log$_{10}$ melt time [s]")
    ax[1].set_ylabel("Count")
    xs = np.sort(B["range"]); ax[2].plot(xs, 1 - np.arange(len(xs)) / len(xs), color=C2)
    ax[2].set_xlabel("Cleaned range per deployment [m]"); ax[2].set_ylabel("P(range ≥ x)")
    save(fig, "fig6_condensation_range.png")
    # ---------------- Module C -----------------
    b = sample_blockage(Nd, rng); C = {}
    for mode in ("passive", "regen", "relief"):
        o = run_dieseling(b, mode); C[mode] = o
        R[f"C_{mode}"] = dict(P_vpk_gt_0p5=float((o["vpk"] > .5).mean()), P_vpk_gt_1=float((o["vpk"] > 1).mean()),
                              P_vpk_gt_2=float((o["vpk"] > 2).mean()), vpk_median=float(np.median(o["vpk"])),
                              vpk_p95=float(np.percentile(o["vpk"], 95)), t_over_median_s=float(np.median(o["t_over"])),
                              v_end_median=float(np.median(o["v_end"])))
    # representative traces (fixed event: dPb=3 bar, Vg=1 m3, Pd=15 bar, nominal others)
    nom = {k: np.array([v]) for k, v in dict(dPb=3e5, Vg=1.0, Pd=15e5, Ff=400.0, cd=2000.0, m_pig=80.0, m_cr=120.0,
                                            Fb=2500.0, Ft=1500.0, beta_max=.92, tau_v=.015).items()}
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    lab = {"passive": "Passive pig", "regen": "Crawler, regen brake only", "relief": "Crawler + bypass relief"}
    col = {"passive": C2, "regen": C4, "relief": C3}
    traces = {}
    for mode in ("passive", "regen", "relief"):
        o = run_dieseling(nom, mode, keep_trace=True); traces[mode] = float(o["vpk"][0])
        ax[0].plot(o["t"], o["trace"][:, 0], color=col[mode], label=lab[mode])
        xs = np.sort(C[mode]["vpk"]); ax[1].plot(xs, 1 - np.arange(len(xs)) / len(xs), color=col[mode], label=lab[mode])
    R["C_nominal_peak_speed"] = traces
    ax[0].set_xlabel("Time after break-through [s]"); ax[0].set_ylabel("Speed [m/s]"); ax[0].set_xlim(0, 2.5)
    ax[0].axhline(.1, color="k", ls=":", lw=1); ax[0].text(1.3, .15, "set-point 0.1 m/s", fontsize=8)
    ax[0].set_title("Nominal 3 bar break-through", fontsize=9); ax[0].legend(frameon=False, fontsize=7)
    ax[1].set_xscale("log"); ax[1].set_xlabel("Peak speed [m/s]"); ax[1].set_ylabel("P(peak speed ≥ x)")
    ax[1].set_title(f"Monte Carlo, N = {Nd}", fontsize=9)
    save(fig, "fig7_anti_dieseling.png")
    print("C done", round(time.time() - t0, 1), "s")
    # ---------------- Module D -----------------
    rng_d = np.random.default_rng(SEED + 7)
    xs = np.array([.05, .1, .2, .4, .8, 1.5, 3.0]) if not quick else np.array([.1, .8, 3.0])
    ps = [0.5, 0.8, 0.95]
    D = {"x": xs.tolist(), "p": ps, "mean_field_avg": {}, "kmc_gamma0_avg": {}, "kmc_gamma3_avg": {}}
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    xf = np.logspace(-1.5, .6, 100)
    for pi, pcl in enumerate(ps):
        c = [C1, C3, C4][pi]
        _, fav = mean_field_fouled(xf, pcl); ax[0].plot(xf, fav, color=c, lw=1.4, label=f"p = {pcl}")
        k0 = []; k3 = []
        for x in xs:
            k0.append(lattice_kmc(x, pcl, 0.0, rng_d, passes=40 if quick else 60, reps=2 if quick else 3)[1])
            k3.append(lattice_kmc(x, pcl, 3.0, rng_d, passes=40 if quick else 60, reps=2 if quick else 3)[1])
        _, fm = mean_field_fouled(xs, pcl)
        D["mean_field_avg"][str(pcl)] = fm.tolist(); D["kmc_gamma0_avg"][str(pcl)] = k0; D["kmc_gamma3_avg"][str(pcl)] = k3
        ax[0].plot(xs, k0, "o", color=c, ms=4); ax[1].plot(xs, k3, "s-", color=c, ms=4, label=f"p = {pcl}")
        ax[1].plot(xf, fav, color=c, lw=.8, ls="--")
    D["max_abs_err_gamma0"] = float(max(np.max(np.abs(np.array(D["mean_field_avg"][str(p_)]) - np.array(D["kmc_gamma0_avg"][str(p_)]))) for p_ in ps))
    ax[0].set_xscale("log"); ax[1].set_xscale("log")
    for a in ax:
        a.set_xlabel("Fouling per pass interval  x = r$_f$T$_c$"); a.set_ylabel("Time-averaged fouled fraction")
    ax[0].set_title("γ = 0: exact solution (line) vs lattice MC (dots)", fontsize=8.5)
    ax[1].set_title("γ = 3: neighbour-nucleated fouling (dashed = γ = 0)", fontsize=8.5); ax[1].legend(frameon=False, fontsize=7)
    save(fig, "fig8_maintenance_lattice.png")
    R["D"] = D
    # Fig 1 schematic
    fig, ax = plt.subplots(figsize=(3.4, 3.4)); ax.set_aspect("equal"); ax.axis("off")
    rr = [0.150, 0.108, 0.104 - 0.0001, 0.064, 0.060]
    for rad, col_, lab_ in ((0.150, "#d9d9d9", "Pipe wall / deposit"), (0.108, "#9aa5b1", "Ti hull"), (0.104, "#f4e3b0", "Silica aerogel"),
                            (0.064, "#c0c8d0", "Al shell"), (0.060, "#8ecae6", "Battery pack")):
        ax.add_patch(plt.Circle((0, 0), rad, color=col_, ec="k", lw=.5))
    ax.set_xlim(-.16, .16); ax.set_ylim(-.16, .16)
    for y, s in ((.128, "Ti hull (4 mm)"), (.084, "Silica aerogel (t$_a$)"), (.062, "Al shell"), (0.0, "Battery pack\n+ electronics")):
        pass
    ax.annotate("Steam film\nT$_{sat}$ = 200 °C", xy=(.1, .09), xytext=(.12, .13), fontsize=7, ha="left")
    ax.annotate("Ti hull", xy=(0, .106), xytext=(-.1, .14), fontsize=7, arrowprops=dict(arrowstyle="-", lw=.5))
    ax.annotate("Silica aerogel", xy=(0, .084), xytext=(-.15, .06), fontsize=7, arrowprops=dict(arrowstyle="-", lw=.5))
    ax.annotate("Al shell", xy=(0, -.062), xytext=(-.15, -.11), fontsize=7, arrowprops=dict(arrowstyle="-", lw=.5))
    ax.text(0, 0, "Pack\nT ≤ 55 °C", ha="center", va="center", fontsize=7)
    save(fig, "fig1_cross_section.png")
    R["runtime_s"] = round(time.time() - t0, 1)
    json.dump(R, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    return R

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true"); ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.quick:
        R = reproduce_suite(N=300, Nsweep=200, Nd=2000, quick=True)
    else:
        R = reproduce_suite(N=3000, Nsweep=800, Nd=10000)
    print(json.dumps(R, indent=1)[:6000])
