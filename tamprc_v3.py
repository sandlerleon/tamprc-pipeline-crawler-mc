#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tamprc_v3.py -- revision studies for the TAMPRC paper (imports tamprc_mc.py, unchanged, and tamprc_v2.py).

Added in this revision, in the order of the referee priorities:
  bench     benchmark of the melt models against an independent enthalpy-method Stefan solver (and the exact Neumann solution), code-to-code check of the conduction solver,
            intercomparison of three condensation representations
  hmodels   effect of the condensation representation (Nusselt external, Chato internal stratified, Chato with non-condensable gas at its lower bound) on range and thermal margin
  dynfilm   dynamic retained melt film, ds/dt = melt production - gravity drainage, coupled to the heat flux through the film
  sobol     global variance-based sensitivity (Sobol, Jansen estimator) of the pack temperature, the range and the steam use
  corr      sensitivity of the conclusions to correlation between inputs (Gaussian copula)
  design    constrained design search and Pareto set (range, steam per metre, hull size, thermal margin)
  envelope  feasible region against pipe size and pipe temperature
  ptcompat  steam saturation pressure against flange ratings; revised operating envelope

ALL INPUT DISTRIBUTIONS REMAIN ASSUMED.  Usage:  python tamprc_v3.py --all | --quick
"""
import argparse
import json
import math
import os
import time
from contextlib import contextmanager

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import brentq
from scipy.integrate import solve_ivp
from scipy.special import erf

import tamprc_mc as V1
import tamprc_v2 as T

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figures")
SEED = V1.SEED
C1, C2, C3, C4 = V1.C1, V1.C2, V1.C3, V1.C4
G = 9.81
RHO_L = 770.0           # kg/m3 molten paraffin (assumed)
MU_L = 4.0e-3           # Pa s molten paraffin (assumed, lognormal sigma 0.3 in the study)
SIN_AVG = 0.7           # mean of sin(theta) over the wall between crown and invert (assumed)


# ------------------------------------------------------------------------------------------------ condensation representations
_H_ORIG = V1.h_cond


def h_chato(Tsat, Tw, D, mult=1.0):
    """Chato (1962) condensation inside a horizontal tube at low vapour velocity, stratified flow: 0.555 [g rho_l (rho_l - rho_v) k_l^3 h'_fg / (mu_l D dT)]^(1/4), h'_fg = h_fg + 3/8 c_p dT."""
    s = V1.STEAM
    dT = np.maximum(Tsat - Tw, 1.0)
    hfgp = s["hfg"] + 0.375 * s["cp_l"] * dT
    return mult * 0.555 * ((V1.G * s["rho_l"] * (s["rho_l"] - s["rho_v"]) * s["k_l"] ** 3 * hfgp) / (s["mu_l"] * D * dT)) ** 0.25


@contextmanager
def use_h(model):
    """Swap the condensation coefficient used by the original thermal and melt functions.  'nusselt' is the original; 'chato' the internal stratified-flow correlation."""
    old = V1.h_cond
    try:
        V1.h_cond = _H_ORIG if model == "nusselt" else h_chato
        yield
    finally:
        V1.h_cond = old


# ------------------------------------------------------------------------------------------------ enthalpy-method Stefan solver (independent benchmark)
def neumann_lambda(St):
    """Root of lambda exp(lambda^2) erf(lambda) = St / sqrt(pi) (one-phase Neumann solution, liquid at the surface, solid initially at the melt temperature)."""
    f = lambda lam: lam * math.exp(lam * lam) * math.erf(lam) - St / math.sqrt(math.pi)
    return brentq(f, 1e-9, 6.0)


def stefan_enthalpy(h, Tsat, Tm, T0, thick, rho=850.0, c=2100.0, Lf=2.0e5, k=0.15, drain=False, ncell=200, t_max=4000.0, record=None):
    """1-D explicit enthalpy-method melting of a slab of thickness `thick` on an adiabatic wall.  Steam side: convective boundary h (Tsat - T_surface).
    drain=False: the melt stays (no drainage); drain=True: a cell that is fully liquid is removed at once (ablation).  Equal properties in both phases.
    Returns the time at which the whole thickness is melted (or removed), and the melted-front history if `record` is a list."""
    dx = thick / ncell
    alpha = k / (rho * c)
    dt = 0.4 * dx * dx / alpha
    Hs = rho * c * Tm              # enthalpy at the start of melting
    Hl = Hs + rho * Lf             # ... and at the end
    H = np.full(ncell, rho * c * T0)
    t = 0.0; removed = 0; steps = 0

    def temp(Hc):
        return np.where(Hc < Hs, Hc / (rho * c), np.where(Hc > Hl, Tm + (Hc - Hl) / (rho * c), Tm))
    while t < t_max:
        T_ = temp(H)
        nc = H.size
        flux = np.empty(nc + 1)
        flux[1:-1] = -k * (T_[1:] - T_[:-1]) / dx            # heat flux in +x (towards the wall), positive when T decreases with x
        flux[-1] = 0.0
        G0 = 1.0 / (1.0 / h + 0.5 * dx / k)
        if drain and T_[0] >= Tm - 1e-9:
            G0 = h                     # ablation: the exposed surface is at the melt temperature (no half-cell conduction resistance)
        flux[0] = G0 * (Tsat - T_[0])
        H = H + dt * (flux[:-1] - flux[1:]) / dx
        t += dt; steps += 1
        if drain:
            while H.size and H[0] >= Hl:
                H = H[1:]; removed += 1
            if H.size == 0:
                return t, record
        else:
            if record is not None and steps % 2000 == 0:
                record.append((t, float(np.sum(np.clip((H - Hs) / (Hl - Hs), 0, 1)) * dx)))
            if H.min() >= Hl:
                return t, record
    return float("inf"), record


# ------------------------------------------------------------------------------------------------ benchmarks
def bench_stefan():
    """Melting benchmarks: (1) the enthalpy solver against the exact Neumann solution; (2) the first suite's ablation formula and the no-drainage formula (Eq. 4 of the manuscript)
    against the enthalpy solver for the median parameters."""
    out = {}
    rho, c, Lf, k = 850.0, 2100.0, 2.0e5, 0.15
    Tm, Tsat = 58.0, 198.0
    St = c * (Tsat - Tm) / Lf
    lam = neumann_lambda(St)
    alpha = k / (rho * c)
    # (1) Neumann: very large h so that the surface is at Tsat; solid at Tm initially; thick slab (semi-infinite for the time considered)
    tcheck = 60.0
    X_exact = 2 * lam * math.sqrt(alpha * tcheck)
    rec = []
    thick = 0.02
    # run until t = tcheck by using a slab that is not fully melted: record the front, then interpolate
    dx = thick / 400; dt = 0.4 * dx * dx / alpha
    H = np.full(400, rho * c * Tm); Hs = rho * c * Tm; Hl = Hs + rho * Lf
    t = 0.0
    while t < tcheck:
        T_ = np.where(H < Hs, H / (rho * c), np.where(H > Hl, Tm + (H - Hl) / (rho * c), Tm))
        fl = np.empty(401); fl[1:-1] = -k * (T_[1:] - T_[:-1]) / dx; fl[-1] = 0.0; fl[0] = 1.0 / (0.5 * dx / k) * (Tsat - T_[0])
        H = H + dt * (fl[:-1] - fl[1:]) / dx; t += dt
    X_num = float(np.sum(np.clip((H - Hs) / (Hl - Hs), 0, 1)) * dx)
    out["neumann"] = dict(St=St, lam=lam, t_s=tcheck, X_exact_mm=X_exact * 1e3, X_numeric_mm=X_num * 1e3, rel_err=(X_num - X_exact) / X_exact,
                          X_quasi_steady_mm=math.sqrt(2 * St * alpha * tcheck) * 1e3, rel_err_quasi_steady=(math.sqrt(2 * St * alpha * tcheck) - X_exact) / X_exact)
    # (2) convective boundary with the median parameters (no heat-coupling loss: eta = 1 in both)
    T0 = 25.0
    rows = []
    for h in (1000.0, 3000.0, 10000.0):
        for thick in (0.003, 0.006, 0.012):
            e = rho * thick * (Lf + c * (Tm - T0))
            t_abl_formula = e / (h * (Tsat - Tm))
            t_nd_formula = rho * (Lf + c * (Tm - T0)) * (thick / h + thick ** 2 / (2 * k)) / (Tsat - Tm)
            t_abl, _ = stefan_enthalpy(h, Tsat, Tm, T0, thick, rho, c, Lf, k, drain=True, ncell=int(thick / 4e-6), t_max=5000.0)      # dx = 4 um resolves the ablation layer alpha/V (5-50 um)
            t_nd, _ = stefan_enthalpy(h, Tsat, Tm, T0, thick, rho, c, Lf, k, drain=False, ncell=120, t_max=20000.0)
            rows.append(dict(h=h, thick_mm=thick * 1e3, t_ablation_formula=t_abl_formula, t_ablation_numeric=t_abl, err_ablation=(t_abl_formula - t_abl) / t_abl,
                             t_nodrain_formula=t_nd_formula, t_nodrain_numeric=t_nd, err_nodrain=(t_nd_formula - t_nd) / t_nd))
    out["convective"] = rows
    # resolution of the ablation solution (h = 3000, 6 mm): melt time against cell size
    conv = []
    for dx_um in (16.0, 8.0, 4.0, 2.0):
        tt, _ = stefan_enthalpy(3000.0, Tsat, Tm, T0, 6e-3, rho, c, Lf, k, drain=True, ncell=int(6e-3 / (dx_um * 1e-6)), t_max=50.0)
        conv.append(dict(dx_um=dx_um, t_ablation_numeric=tt))
    out["ablation_resolution"] = conv
    out["St_median"] = St
    return out


def bench_conduction():
    """Code-to-code check of the conduction solver: the nominal deterministic composite wall integrated by the first suite's backward-Euler scheme and by an independent stiff ODE
    integrator (scipy BDF, rtol 1e-10) on the same spatial discretization, assembled here independently."""
    p = dict(t_a=np.array([0.04]), k_mult=np.array([1.0]), phi_br=np.array([0.175]), P_gen=np.array([70.0]), m_pack=np.array([16.0]), T0=np.array([25.0]), Tsat=np.array([198.0]),
             h_mult=np.array([1.0]), vac_lost=np.array([False]))
    r = V1.run_thermal(p, False, t_end=2700.0, dt=10.0)
    r_fine = V1.run_thermal(p, False, t_end=2700.0, dt=0.625, ns=2, na=16, nh=2)
    # independent assembly (single case)
    L = V1.GEOM["L"]; ns, na, nh = 2, 16, 2; n = ns + na + nh
    r0 = V1.GEOM["r_pack"]; r1 = r0 + V1.GEOM["t_shell"]; r2 = r1 + 0.04; r3 = r2 + V1.GEOM["t_hull"]
    f = np.concatenate([np.linspace(r0, r1, ns + 1), np.linspace(r1, r2, na + 1)[1:], np.linspace(r2, r3, nh + 1)[1:]])
    rc = 0.5 * (f[1:] + f[:-1]); vol = math.pi * (f[1:] ** 2 - f[:-1] ** 2)
    layer = np.array([0] * ns + [1] * na + [2] * nh)
    rhocp = np.where(layer == 0, V1.MAT["shell"][1], np.where(layer == 1, V1.MAT["aero_rhocp"], V1.MAT["hull"][1]))
    C = np.concatenate([[16.0 * 900.0 / L], rhocp * vol])
    kn = V1.k_aero(25.0, False); Gbr = 0.175 * 2 * math.pi * kn / math.log(r2 / r1)

    def rhs(t, T):
        Tc = T[1:]
        kc = np.where(layer == 1, V1.k_aero(Tc, False), np.where(layer == 0, V1.MAT["shell"][0], V1.MAT["hull"][0]))
        dT = np.zeros_like(T)
        # pack - cell 0
        R0 = math.log(rc[0] / r0) / (2 * math.pi * kc[0]) + 1.0 / (2 * math.pi * r0 * 15.0)
        q0 = (T[1] - T[0]) / R0
        dT[0] += q0; dT[1] -= q0
        for j in range(n - 1):
            rf = f[j + 1]
            R = math.log(rf / rc[j]) / (2 * math.pi * kc[j]) + math.log(rc[j + 1] / rf) / (2 * math.pi * kc[j + 1])
            q = (T[j + 2] - T[j + 1]) / R
            dT[j + 1] += q; dT[j + 2] -= q
        hs = min(float(V1.h_cond(198.0, T[-1], 2 * r3, 1.0)), 12000.0)
        Rs = math.log(r3 / rc[-1]) / (2 * math.pi * kc[-1]) + 1.0 / (2 * math.pi * r3 * hs)
        dT[-1] += (198.0 - T[-1]) / Rs
        dT[0] += 70.0 / L
        qb = Gbr * (T[-1] - T[0]); dT[0] += qb; dT[-1] -= qb
        return dT / C
    sol = solve_ivp(rhs, (0.0, 2700.0), np.full(n + 1, 25.0), method="BDF", rtol=1e-10, atol=1e-10)
    Tp_ode = float(sol.y[0, -1])
    return dict(Tp45_backward_euler_10s=float(r["Tp45"][0]), Tp45_backward_euler_0p625s=float(r_fine["Tp45"][0]), Tp45_independent_BDF=Tp_ode,
                diff_10s_K=float(r["Tp45"][0]) - Tp_ode, diff_0p625s_K=float(r_fine["Tp45"][0]) - Tp_ode)


# ------------------------------------------------------------------------------------------------ condensation models and the range
def study_hmodels(N):
    """Three representations of the condensation coefficient: Nusselt (original), Chato (internal, stratified), Chato with the non-condensable factor fixed at its lower bound (0.5)."""
    rows = {}
    for model, label in (("nusselt", "Nusselt (outside horizontal tube; first suite)"), ("chato", "Chato (inside horizontal tube, stratified)"), ("chato_ncg", "Chato, non-condensable factor at 0.5")):
        mm = "nusselt" if model == "nusselt" else "chato"
        with use_h(mm):
            rng = np.random.default_rng(SEED + 601)
            p, r = T.thermal(N, rng, 40.0, False)
            ok = int((r["Tp45"] <= 55).sum()); lo, hi = T.wilson(ok, N)
            t_run = np.minimum(r["t_crit"], 2700.0)
            res = dict(label=label, P_safe=ok / N, P_safe_ci=[lo, hi], Tp45_median=float(np.median(r["Tp45"])))
            for s_mm in (0.0, 0.2):
                B = T.deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=s_mm * 1e-3)
                if model == "chato_ncg":
                    # same draws, non-condensable factor fixed at 0.5 instead of U(0.5, 1)
                    scale = 0.5 / B["m_nc"]
                    h = B["h"] * scale
                    dT = p["Tsat"] - B["T_melt"]
                    q_film = dT / (1.0 / h + s_mm * 1e-3 / T.K_LIQ)
                    e_over = B["t_melt"] * B["q_eff"]                   # = e
                    t_m = e_over / (B["eta"] * q_film)
                    v = np.minimum(0.10, B["Lz"] / t_m); rg = v * t_run; vth = B["Lz"] / t_m
                else:
                    rg = B["range"]; vth = B["v_th"]
                res["range_median_m_s%g" % s_mm] = float(np.median(rg)); res["range_p05_m_s%g" % s_mm] = float(np.percentile(rg, 5)); res["range_p95_m_s%g" % s_mm] = float(np.percentile(rg, 95))
                res["v_th_median_cms_s%g" % s_mm] = float(np.median(vth) * 100)
        rows[model] = res
    # pointwise ratio of the coefficients
    d = np.array([40.0, 80.0, 140.0])
    ratio = {str(x): float(h_chato(200.4, 200.4 - x, V1.D_PIPE) / _H_ORIG(200.4, 200.4 - x, V1.D_PIPE)) for x in d}
    # steam-side coefficient on the hull (limit of no film resistance)
    return dict(models=rows, h_ratio_chato_to_nusselt=ratio)


# ------------------------------------------------------------------------------------------------ dynamic retained film
def dynfilm(Dm, Tsat, h_mult, D=V1.D_PIPE, mu_factor=1.0, ell_factor=1.0, s_res=0.0, k_l=T.K_LIQ, dt=0.02, t_cap=4000.0, rng=None, trace_idx=None, tau=0.0, sin_theta=SIN_AVG):
    """Melt time with a dynamic retained film.  Dm: the deposit draws of T.deposit_v2 (s = 0).  State per sample: melted thickness x and liquid layer thickness s.
        q = eta (Tsat - T_m) / (1/h + s/k_l)                       heat flux through the condensate film and the liquid layer
        dx/dt = q / (rho_d (L_f + c_d (T_m - T_0)))                 melt front recession
        ds/dt = (rho_d/rho_l) dx/dt - rho_l g sin(theta) (s - s_res)^3 / (3 mu ell)      production minus gravity drainage of a film on the wall (Nusselt film), ell = pi D / 4
    mu is lognormal (median 4 mPa s, sigma 0.3) times mu_factor.  Returns the melt time, the final s, and a trace for the sample trace_idx."""
    N = len(Dm["delta"])
    rng = rng or np.random.default_rng(SEED + 701)
    mu = MU_L * mu_factor * rng.lognormal(0.0, 0.3, N)
    ell = math.pi * D / 4.0 * ell_factor
    dT = Tsat - Dm["T_melt"]
    h = Dm["h"]
    # energy per unit area and rate constants (the original uses e = rho delta [L_f + c (T_m - T_0)])
    e_unit = Dm["t_melt"] * Dm["q_eff"] / Dm["delta"]       # J/m3 = rho_d [L_f + c_d (T_m - T_0)]
    cdr = RHO_L * G * sin_theta / (3.0 * mu * ell)
    csh = tau / (2.0 * mu * ell)                       # steam-shear contribution: film flux per unit width tau s^2 / (2 mu)
    x = np.zeros(N); s = np.zeros(N); t_done = np.full(N, np.nan); t = 0.0
    trace = []
    active = np.ones(N, bool)
    steps = int(t_cap / dt)
    for i in range(steps):
        q = Dm["eta"] * dT / (1.0 / h + s / k_l)
        dx = q / e_unit * dt
        prod = dx * 850.0 / RHO_L
        s_tmp = s + prod
        ex = np.maximum(s_tmp - s_res, 0.0)
        drain = (cdr * ex ** 3 + csh * ex ** 2) * dt
        s = np.maximum(s_tmp - np.minimum(drain, ex), 0.0)
        x = x + dx * active
        t += dt
        newly = active & (x >= Dm["delta"])
        if newly.any():
            frac = (x[newly] - Dm["delta"][newly]) / np.maximum(dx[newly], 1e-30)
            t_done[newly] = t - frac * dt
            active &= ~newly
        if trace_idx is not None and i % 50 == 0:
            trace.append((t, float(x[trace_idx]), float(s[trace_idx])))
        if not active.any():
            break
    # extrapolate any that did not finish
    if active.any():
        rate = np.maximum(dx, 1e-30) / dt
        t_done[active] = t + (Dm["delta"][active] - x[active]) / rate[active]
    return dict(t_melt=t_done, s_end=s, trace=trace, mu=mu)


def study_dynfilm(base, N):
    p, r = base["atm"]
    t_run = np.minimum(r["t_crit"], 2700.0)
    Dm = T.deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=0.0)
    out = {}
    i_nom = int(np.argmin(np.abs(Dm["delta"] - 6e-3) + 1e-3 * np.abs(Dm["T_melt"] - 58.0)))
    d0 = dynfilm(Dm, p["Tsat"], p["h_mult"], trace_idx=i_nom)
    vth = Dm["Lz"] / d0["t_melt"]; v = np.minimum(0.10, vth); rg = v * t_run
    out["baseline"] = dict(t_melt_median_s=float(np.median(d0["t_melt"])), t_melt_ablation_median_s=float(np.median(Dm["t_melt"])), ratio_median=float(np.median(d0["t_melt"] / Dm["t_melt"])),
                           v_th_median_cms=float(np.median(vth) * 100), range_median_m=float(np.median(rg)), range_p05_m=float(np.percentile(rg, 5)), range_p95_m=float(np.percentile(rg, 95)),
                           P_ge_100=float((rg >= 100).mean()), s_end_median_mm=float(np.median(d0["s_end"]) * 1e3), s_end_p05_mm=float(np.percentile(d0["s_end"], 5) * 1e3), s_end_p95_mm=float(np.percentile(d0["s_end"], 95) * 1e3),
                           mu_median_mPas=float(np.median(d0["mu"]) * 1e3), drain_path_m=math.pi * V1.D_PIPE / 4)
    sens = {}
    for lab, kw in (("viscosity x0.25", dict(mu_factor=0.25)), ("viscosity x4", dict(mu_factor=4.0)), ("drain path x0.25", dict(ell_factor=0.25)), ("drain path x4", dict(ell_factor=4.0)),
                    ("residual film 0.02 mm", dict(s_res=0.02e-3)), ("residual film 0.05 mm", dict(s_res=0.05e-3)),
                    ("steam shear 0.1 Pa", dict(tau=0.1)), ("steam shear 1 Pa", dict(tau=1.0)), ("steam shear 10 Pa", dict(tau=10.0)),
                    ("wall near the invert (sin 0.2)", dict(sin_theta=0.2)), ("wall at the spring line (sin 1.0)", dict(sin_theta=1.0))):
        d = dynfilm(Dm, p["Tsat"], p["h_mult"], **kw)
        vth_ = Dm["Lz"] / d["t_melt"]; rg_ = np.minimum(0.10, vth_) * t_run
        sens[lab] = dict(range_median_m=float(np.median(rg_)), s_end_median_mm=float(np.median(d["s_end"]) * 1e3), P_ge_100=float((rg_ >= 100).mean()))
    out["sensitivity"] = sens
    # steady state film for the median draw: melt production = drainage
    h_med = float(np.median(Dm["h"])); dT_med = float(np.median(p["Tsat"] - Dm["T_melt"])); eta_med = float(np.median(Dm["eta"]))
    e_med = float(np.median(Dm["t_melt"] * Dm["q_eff"] / Dm["delta"])); ell = math.pi * V1.D_PIPE / 4
    f = lambda s: eta_med * dT_med / (1 / h_med + s / T.K_LIQ) / e_med * 850.0 / RHO_L - RHO_L * G * SIN_AVG * s ** 3 / (3 * MU_L * ell)
    s_star = brentq(f, 1e-7, 5e-3)
    out["steady_film_median_params"] = dict(s_star_mm=s_star * 1e3, Pi_f=h_med * s_star / T.K_LIQ, flux_ratio=1.0 / (1.0 + h_med * s_star / T.K_LIQ))
    # steam velocity that produces a given interfacial shear: tau = 0.5 rho_v f u^2, f = 0.01 (assumed)
    out["shear_vs_velocity"] = [dict(tau_Pa=t_, u_steam_m_s=float(math.sqrt(2 * t_ / (V1.STEAM["rho_v"] * 0.01)))) for t_ in (0.1, 1.0, 10.0)]
    out["gravity_stress_Pa_at_median_film"] = float(RHO_L * G * SIN_AVG * out["steady_film_median_params"]["s_star_mm"] * 1e-3)
    mdot_med = float(np.median(Dm["q_raw"] * math.pi * V1.D_PIPE * Dm["Lz"] / (V1.STEAM["hfg"])))
    out["steam_velocity_for_condensation_m_s"] = mdot_med / (V1.STEAM["rho_v"] * math.pi / 4 * V1.D_PIPE ** 2)
    out["trace_nominal"] = dict(t=[a[0] for a in d0["trace"]], x_mm=[a[1] * 1e3 for a in d0["trace"]], s_mm=[a[2] * 1e3 for a in d0["trace"]], delta_mm=float(Dm["delta"][i_nom] * 1e3))
    # dimensionless retained-film resistance: range >= 100 m needs v_th >= 100 m / t_run; with q/q0 = 1/(1+Pi_f)
    return out, (Dm, d0, t_run, p)


def pi_f_100m(Dm, t_run):
    """Pi_f = h s / k_l at which the median range falls to 100 m (series-resistance model, same draws)."""
    f = lambda pf: float(np.median(np.minimum(0.10, Dm["v_th"] / (1.0 + pf)) * t_run)) - 100.0
    return brentq(f, 0.0, 50.0)


def study_coverage_dyn(base, bd, N):
    """Deployments and intervention time for the dynamic-film melt model (same stage-duration draws as T.study_coverage)."""
    Dm, d0, _, p0 = bd
    rngT = np.random.default_rng(SEED + 202)
    stage = dict(prep=rngT.uniform(3, 8, N), turn=rngT.uniform(1, 3, N), verify=rngT.uniform(1, 3, N), rts=rngT.uniform(2, 6, N))
    v = np.minimum(0.10, Dm["Lz"] / d0["t_melt"])
    out = {}
    for mission, (key, tmax) in {"45 min atmospheric": ("atm", 2700.0), "90 min evacuated": ("vac", 5400.0)}.items():
        t_run = np.minimum(base[key][1]["t_crit"], tmax)
        rg = v * t_run
        for L in (0.3, 10.0, 100.0, 300.0, 600.0, 1000.0):
            nd_ = np.ceil(L / rg); active = L / v / 3600.0
            total = stage["prep"] + active + (nd_ - 1) * stage["turn"] + stage["verify"] + stage["rts"]
            out["%s|dynamic film|%g" % (mission, L)] = dict(P_single=float((rg >= L).mean()), n_dep_median=float(np.median(nd_)), n_dep_p05=float(np.percentile(nd_, 5)), n_dep_p95=float(np.percentile(nd_, 95)),
                                                         active_h_median=float(np.median(active)), total_h_median=float(np.median(total)), total_h_p05=float(np.percentile(total, 5)), total_h_p95=float(np.percentile(total, 95)),
                                                         active_fraction_median=float(np.median(active / total)), range_median_m=float(np.median(rg)), range_max_m=float(rg.max()), naive_n_dep=float(L / np.median(rg)))
    return out


# ------------------------------------------------------------------------------------------------ Sobol indices
def sobol_indices(fun, ppfs, m=11, seed=3, nboot=200):
    """Jansen estimators of the first-order and total indices; ppfs: list of inverse CDFs on (0,1); fun(X) -> (N,) with X (N, k) in physical units."""
    k = len(ppfs)
    sam = stats.qmc.Sobol(d=2 * k, scramble=True, seed=seed).random_base2(m)
    A = sam[:, :k]; Bm = sam[:, k:]
    X = lambda U: np.column_stack([ppfs[i](np.clip(U[:, i], 1e-9, 1 - 1e-9)) for i in range(k)])
    fA = fun(X(A)); fB = fun(X(Bm))
    fAB = []
    for i in range(k):
        ABi = A.copy(); ABi[:, i] = Bm[:, i]
        fAB.append(fun(X(ABi)))
    N = len(fA)
    var = np.var(np.concatenate([fA, fB]))
    S1 = np.array([np.mean(fB * (fAB[i] - fA)) / var for i in range(k)])
    ST = np.array([0.5 * np.mean((fA - fAB[i]) ** 2) / var for i in range(k)])
    rng = np.random.default_rng(11); b1 = np.zeros((nboot, k)); bT = np.zeros((nboot, k))
    for b in range(nboot):
        ix = rng.integers(0, N, N)
        v = np.var(np.concatenate([fA[ix], fB[ix]]))
        for i in range(k):
            b1[b, i] = np.mean(fB[ix] * (fAB[i][ix] - fA[ix])) / v
            bT[b, i] = 0.5 * np.mean((fA[ix] - fAB[i][ix]) ** 2) / v
    return dict(S1=S1.tolist(), ST=ST.tolist(), S1_ci=[np.percentile(b1, [2.5, 97.5], axis=0)[0].tolist(), np.percentile(b1, [2.5, 97.5], axis=0)[1].tolist()],
                ST_ci=[np.percentile(bT, [2.5, 97.5], axis=0)[0].tolist(), np.percentile(bT, [2.5, 97.5], axis=0)[1].tolist()], N=int(N), variance=float(var))


def melt_model(delta, Tm, rho, Lf, Tpipe, eta, m_nc, Lz, Tsat, h_mult, s, D=V1.D_PIPE, t_run=2700.0, v_set=0.10):
    """Closed form of the first suite's deposit mobilisation with a retained film s (same equations as T.deposit_v2), for arrays."""
    h = V1.h_cond(Tsat, Tm, D, h_mult * m_nc)
    dT = Tsat - Tm
    q_film = dT / (1.0 / h + s / T.K_LIQ)
    e = rho * delta * (Lf + 2100.0 * (Tm - Tpipe))
    t_melt = e / (eta * q_film)
    v = np.minimum(v_set, Lz / t_melt)
    hfgp = V1.STEAM["hfg"] + 0.68 * V1.STEAM["cp_l"] * (Tsat - Tm)
    steam = q_film * math.pi * D * Lz / hfgp / v
    return v * t_run, steam, Lz / t_melt


def study_sobol(m_thermal=9, m_melt=13):
    out = {}
    nrm = stats.norm.ppf
    # thermal: pack temperature at 45 min, atmospheric aerogel 40 mm
    names_t = ["aerogel k multiplier", "aerogel thickness", "thermal-bridge fraction", "internal heat generation", "pack mass", "initial temperature", "steam temperature", "condensation multiplier"]
    ppf_t = [lambda u: np.exp(0.15 * nrm(u)), lambda u: 0.04 * (1 + 0.03 * nrm(u)), lambda u: 0.05 + 0.25 * u, lambda u: np.exp(np.log(70.0) + 0.35 * nrm(u)), lambda u: 16.0 + 1.2 * nrm(u),
             lambda u: 25.0 + 4.0 * nrm(u), lambda u: np.clip(198.0 + 3.0 * nrm(u), 185, 204), lambda u: np.exp(0.15 * nrm(u))]

    def f_t(X):
        p = dict(k_mult=X[:, 0], t_a=X[:, 1], phi_br=X[:, 2], P_gen=X[:, 3], m_pack=X[:, 4], T0=X[:, 5], Tsat=X[:, 6], h_mult=X[:, 7], vac_lost=np.zeros(len(X), bool))
        return V1.run_thermal(p, False, t_end=2700.0, dt=15.0)["Tp45"]
    r = sobol_indices(f_t, ppf_t, m=m_thermal)
    out["pack_temperature_45min"] = dict(names=names_t, **r)
    rh = sobol_indices(f_t, ppf_t, m=m_thermal - 1, nboot=20)
    out["convergence"] = {"pack_temperature_45min": dict(m_full=m_thermal, m_half=m_thermal - 1, max_abs_diff_ST=float(np.max(np.abs(np.array(r["ST"]) - np.array(rh["ST"])))), max_abs_diff_S1=float(np.max(np.abs(np.array(r["S1"]) - np.array(rh["S1"])))),
                                                       max_ci_halfwidth_ST=float(np.max(0.5 * (np.array(r["ST_ci"][1]) - np.array(r["ST_ci"][0])))))}
    # melt: range and steam per metre; the retained film is an assumed lognormal input (median 0.2 mm, sigma 1.0) in the first case and zero in the second
    names_m = ["deposit thickness", "melt point", "deposit density", "latent heat", "pipe temperature", "heat-coupling fraction", "non-condensable factor", "contact length", "steam temperature", "condensation multiplier", "retained film"]
    ppf_m = [lambda u: np.clip(np.exp(np.log(6e-3) + 0.5 * nrm(u)), 1e-3, 40e-3), lambda u: np.clip(58 + 8 * nrm(u), 40, 90), lambda u: 850 + 40 * nrm(u), lambda u: np.clip(2e5 + 3e4 * nrm(u), 1e5, 3e5),
             lambda u: 25 + 5 * nrm(u), lambda u: 0.15 + 0.35 * u, lambda u: 0.5 + 0.5 * u, lambda u: 0.3 + 0.5 * u, lambda u: np.clip(198 + 3 * nrm(u), 185, 204), lambda u: np.exp(0.15 * nrm(u)),
             lambda u: np.exp(np.log(0.2e-3) + 1.0 * nrm(u))]
    for tag, with_film in (("with_film", True), ("instant_removal", False)):
        def f_r(X, w=with_film):
            rg, st, _ = melt_model(*[X[:, i] for i in range(10)], X[:, 10] if w else 0.0)
            return np.log10(rg)

        def f_s(X, w=with_film):
            rg, st, _ = melt_model(*[X[:, i] for i in range(10)], X[:, 10] if w else 0.0)
            return np.log10(st)
        k = 11 if with_film else 10
        ppf = ppf_m if with_film else ppf_m[:10]
        nm = names_m if with_film else names_m[:10]
        out["range_" + tag] = dict(names=nm, **sobol_indices(lambda X: f_r(np.column_stack([X, np.zeros(len(X))]) if not with_film else X), ppf, m=m_melt))
        rh = sobol_indices(lambda X: f_r(np.column_stack([X, np.zeros(len(X))]) if not with_film else X), ppf, m=m_melt - 1, nboot=20)
        out["convergence"]["range_" + tag] = dict(m_full=m_melt, m_half=m_melt - 1, max_abs_diff_ST=float(np.max(np.abs(np.array(out["range_" + tag]["ST"]) - np.array(rh["ST"])))), max_abs_diff_S1=float(np.max(np.abs(np.array(out["range_" + tag]["S1"]) - np.array(rh["S1"])))),
                                                  max_ci_halfwidth_ST=float(np.max(0.5 * (np.array(out["range_" + tag]["ST_ci"][1]) - np.array(out["range_" + tag]["ST_ci"][0])))))
        out["steam_" + tag] = dict(names=nm, **sobol_indices(lambda X: f_s(np.column_stack([X, np.zeros(len(X))]) if not with_film else X), ppf, m=m_melt))
    return out


# ------------------------------------------------------------------------------------------------ correlated inputs
def study_corr(N):
    rows = []
    for rho_tp, rho_dm in ((0.0, 0.0), (0.6, 0.0), (-0.6, 0.0), (0.0, 0.6), (0.0, -0.6), (0.6, 0.6)):
        rng = np.random.default_rng(SEED + 801)
        old = V1.GEOM["r_pack"]
        p = V1.sample_thermal(N, rng, 40.0, False)
        if rho_tp:
            zT = (p["T0"] - 25.0) / 4.0; zP = np.log(p["P_gen"] / 70.0) / 0.35
            zP = rho_tp * zT + math.sqrt(1 - rho_tp ** 2) * zP
            p["P_gen"] = 70.0 * np.exp(0.35 * zP)
        r = V1.run_thermal(p, False, dt=15.0)
        ok = int((r["Tp45"] <= 55).sum()); lo, hi = T.wilson(ok, N)
        t_run = np.minimum(r["t_crit"], 2700.0)
        B = T.deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=0.0)
        Tm = B["T_melt"]
        if rho_dm:
            zd = np.log(B["delta"] / 6e-3) / 0.5; zm = (Tm - 58.0) / 8.0
            Tm = np.clip(58.0 + 8.0 * (rho_dm * zd + math.sqrt(1 - rho_dm ** 2) * zm), 40, 90)
        rg, st, vth = melt_model(B["delta"], Tm, 850.0 + 0 * Tm, 2e5 + 0 * Tm, 25.0 + 0 * Tm, B["eta"], B["m_nc"], B["Lz"], p["Tsat"], p["h_mult"], 0.0, t_run=t_run)
        rows.append(dict(rho_T0_Pgen=rho_tp, rho_thickness_meltpoint=rho_dm, P_safe=ok / N, P_safe_ci=[lo, hi], range_median_m=float(np.median(rg)), P_ge_100=float((rg >= 100).mean())))
    return dict(rows=rows)


# ------------------------------------------------------------------------------------------------ design search and Pareto set
def pareto_mask(F):
    """F: (n, m) objectives to MINIMISE; returns the non-dominated mask."""
    n = len(F); m = np.ones(n, bool)
    for i in range(n):
        d = np.all(F <= F[i], axis=1) & np.any(F < F[i], axis=1)
        if d.any():
            m[i] = False
    return m


def study_design(base_dyn, N):
    """Constrained design search at 12 in: aerogel thickness, jacket, mission length and speed set-point, for two melt-removal assumptions (instant removal; dynamic retained film).
    The thermal limit v_th depends on the deposit and the steam, not on the design variables; the design sets the mission through the pack temperature and the set-point caps the speed."""
    Dm, d0, _, p0 = base_dyn
    hfgp = V1.STEAM["hfg"] + 0.68 * V1.STEAM["cp_l"] * (p0["Tsat"] - Dm["T_melt"])
    e_unit = Dm["t_melt"] * Dm["q_eff"] / Dm["delta"]
    melt = {"instant removal": (Dm["v_th"], Dm["q_raw"] * math.pi * V1.D_PIPE * Dm["Lz"] / hfgp),
            "dynamic film": (Dm["Lz"] / d0["t_melt"], (Dm["delta"] * e_unit / (Dm["eta"] * d0["t_melt"])) * math.pi * V1.D_PIPE * Dm["Lz"] / hfgp)}
    designs = []
    ID = T.pipe_id(12)
    for vac in (False, True):
        for ta in (10, 15, 20, 25, 30, 35, 40, 45, 50, 60):
            rng = np.random.default_rng(SEED + 901)
            r_hull = V1.GEOM["r_pack"] + T_SHELL + ta * 1e-3 + T_HULL
            fits = bool(r_hull <= ID / 2 - T.CLEAR_NOM + 1e-9)
            p, r = T.thermal(N, rng, float(ta), vac, dt=15.0, t_end=7200.0)
            for mission in (30, 45, 60, 90):
                t_run = np.minimum(r["t_crit"], mission * 60.0)
                P_safe = float((r["t_crit"] >= mission * 60.0).mean())
                for mlab, (vth, mdot) in melt.items():
                    for vset in (0.05, 0.10, 0.20):
                        v = np.minimum(vset, vth); rg = v * t_run
                        designs.append(dict(melt=mlab, vac=vac, t_a_mm=ta, mission_min=mission, v_set=vset, hull_od_mm=2 * r_hull * 1e3, fits=fits, P_safe=P_safe, range_median_m=float(np.median(rg)),
                                            steam_kg_per_m=float(np.median(mdot / v)), energy_Wh=float(np.median(p["P_gen"]) * mission / 60.0)))
    out = dict(designs=designs, n_designs=len(designs), by_melt={},
               constraints="hull fits a 12 in bore with the first design's clearance; P(pack <= 55 C through the mission) >= 0.95; speed set-point at most 0.20 m/s; mission at most 90 min; the surge-speed constraint is not a function of these variables (Section 6.6)")
    for mlab in melt:
        feas = [d for d in designs if d["melt"] == mlab and d["fits"] and d["P_safe"] >= 0.95]
        F = np.array([[-d["range_median_m"], d["steam_kg_per_m"], d["hull_od_mm"], -d["P_safe"]] for d in feas])
        pm = pareto_mask(F)
        for d, f in zip(feas, pm):
            d["pareto"] = bool(f)
        best = max(feas, key=lambda d: d["range_median_m"])
        out["by_melt"][mlab] = dict(n_feasible=len(feas), n_pareto=int(pm.sum()), best_feasible=best,
                                    best_by_mission={str(m): max([d for d in feas if d["mission_min"] == m], key=lambda d: d["range_median_m"]) for m in (30, 45, 60, 90) if any(d["mission_min"] == m for d in feas)},
                                    range_span=[min(d["range_median_m"] for d in feas), max(d["range_median_m"] for d in feas)])
    return out


T_SHELL, T_HULL = T.T_SHELL, T.T_HULL


# ------------------------------------------------------------------------------------------------ feasible envelope
def study_envelope(N):
    nps_l = [8, 10, 12, 14, 16]; temps = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
    P = np.zeros((len(nps_l), len(temps)))
    for i, k in enumerate(nps_l):
        g = T.hull_geometry(k)
        for j, Ta in enumerate(temps):
            rng = np.random.default_rng(SEED + 1001)
            p, r = T.thermal(N, rng, g["t_a"] * 1e3, False, r_pack=g["r_pack"], m_scale=(g["r_pack"] / T.R_PACK_NOM) ** 2, T_shift=Ta - 25.0, dt=15.0)
            P[i, j] = float((r["Tp45"] <= 55).mean())
    return dict(nps=nps_l, temps=temps, P_safe=P.tolist())


# ------------------------------------------------------------------------------------------------ pressure-temperature compatibility
_IF97 = [0.11670521452767e4, -0.72421316703206e6, -0.17073846940092e2, 0.12020824702470e5, -0.32325550322333e7, 0.14915108613530e2, -0.48232657361591e4, 0.40511340542057e6, -0.23855557567849, 0.65017534844798e3]


def psat_MPa(Tc):
    """IAPWS-IF97 saturation pressure (region 4, Eq. 30); Tc in degrees C."""
    n = _IF97; T_ = np.asarray(Tc, float) + 273.15
    th = T_ + n[8] / (T_ - n[9]); A = th ** 2 + n[0] * th + n[1]; B = n[2] * th ** 2 + n[3] * th + n[4]; C = n[5] * th ** 2 + n[6] * th + n[7]
    return (2 * C / (-B + np.sqrt(B * B - 4 * A * C))) ** 4


# Approximate rated working pressures of Group 1.1 carbon-steel flanges (bar): temperature in C -> (Class 150, Class 300); rounded values, to be checked against the current edition and the line specification
RATING = {38: (19.6, 51.1), 100: (17.7, 46.6), 150: (15.8, 45.1), 200: (13.8, 43.8), 250: (12.1, 41.9)}


def study_ptcompat(base, N):
    Ts = np.arange(150, 206, 5.0)
    tt = np.array(sorted(RATING)); r150 = np.array([RATING[t][0] for t in tt]); r300 = np.array([RATING[t][1] for t in tt])
    rows = [dict(T=float(t), psat_bar=float(psat_MPa(t) * 10), class150_bar=float(np.interp(t, tt, r150)), class300_bar=float(np.interp(t, tt, r300))) for t in Ts]
    tgrid = np.linspace(150, 204, 541); ps = psat_MPa(tgrid) * 10
    ok150 = tgrid[ps <= np.interp(tgrid, tt, r150)]; ok300 = tgrid[ps <= np.interp(tgrid, tt, r300)]
    Tmax150 = float(ok150.max()); Tmax300 = float(ok300.max())
    out = dict(rows=rows, Tmax_class150_C=Tmax150, Tmax_class300_C=Tmax300, psat_198C_bar=float(psat_MPa(198.0) * 10), psat_200C_bar=float(psat_MPa(200.4) * 10), psat_Tmax150_bar=float(psat_MPa(Tmax150) * 10))
    # revised envelope: steam temperature N(Tmax150 - 3, 2) (truncated) instead of N(198, 3)
    res = {}
    for lab, Tc in (("original 198 C", None), ("revised, Class 150 limit", Tmax150 - 3.0)):
        rng = np.random.default_rng(SEED + 1101)
        p = V1.sample_thermal(N, rng, 40.0, False)
        if Tc is not None:
            # N(Tc, 2) truncated above at the pressure limit Tmax150 (inverse-CDF mapping of the same uniform draws): every sampled steam temperature respects the limit
            u = stats.norm.cdf((p["Tsat"] - 198.0) / 3.0)
            b = (Tmax150 - Tc) / 2.0
            p["Tsat"] = Tc + 2.0 * stats.norm.ppf(u * stats.norm.cdf(b))
        r = V1.run_thermal(p, False, dt=15.0)
        ok = int((r["Tp45"] <= 55).sum()); lo, hi = T.wilson(ok, N)
        t_run = np.minimum(r["t_crit"], 2700.0)
        B = T.deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=0.0)
        res[lab] = dict(Tsat_max=float(p["Tsat"].max()), frac_above_class150_limit=float((p["Tsat"] > Tmax150 + 1e-9).mean()), Tsat_median=float(np.median(p["Tsat"])), P_safe=ok / N, P_safe_ci=[lo, hi], range_median_m=float(np.median(B["range"])), v_th_median_cms=float(np.median(B["v_th"]) * 100),
                        t_melt_median_s=float(np.median(B["t_melt"])), steam_kg_per_m=float(np.median(B["steam_kg_per_m"])))
    out["revised_envelope"] = res
    return out


# ------------------------------------------------------------------------------------------------ uncapped range
def study_uncapped(base, N):
    p, r = base["atm"]
    t_run = np.minimum(r["t_crit"], 2700.0)
    B = T.deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=0.0)
    unc = B["v_th"] * t_run
    return dict(P_thermally_limited=float((B["v_th"] < 0.10).mean()), uncapped_range_median_m=float(np.median(unc)), uncapped_range_p95_m=float(np.percentile(unc, 95)), uncapped_range_p99_m=float(np.percentile(unc, 99)),
                capped_range_median_m=float(np.median(B["range"])), P_range_at_cap=float((B["v_th"] >= 0.10).mean()), cap_m=0.10 * 2700.0, P_uncapped_ge_300=float((unc >= 300).mean()), P_uncapped_ge_1000=float((unc >= 1000).mean()))


# ------------------------------------------------------------------------------------------------ figures
def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(FIG, name)); plt.close(fig)


def fig_dynfilm(dyn, flm):
    fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.9))
    tr = dyn["trace_nominal"]
    ax[0].plot(tr["t"], tr["s_mm"], color=C1, label="retained film s"); ax[0].set_xlabel("Time [s]"); ax[0].set_ylabel("Retained film [mm]", color=C1)
    a2 = ax[0].twinx(); a2.plot(tr["t"], tr["x_mm"], color=C2, label="melted thickness"); a2.axhline(tr["delta_mm"], color="0.5", ls=":", lw=1); a2.set_ylabel("Melted thickness [mm]", color=C2)
    ax[0].set_title("(a) one draw", fontsize=8.5)
    rows = flm["rows"]
    s_ = np.array([r["s_mm"] for r in rows]); rg = np.array([r["range_median_m"] for r in rows])
    ax[1].plot(np.maximum(s_, 0.02), rg, "o-", color=C1, label="constant film (median range)")
    ax[1].axhline(dyn["baseline"]["range_median_m"], color=C3, lw=1.6, label="dynamic film: median")
    ax[1].axhspan(dyn["baseline"]["range_p05_m"], dyn["baseline"]["range_p95_m"], color=C3, alpha=.15, lw=0)
    ax[1].axhline(flm["nodrain"]["range_nodrain_median_m"], color=C2, ls="--", lw=1, label="no drainage")
    ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlabel("Constant retained film [mm]"); ax[1].set_ylabel("Range per 45 min [m]"); ax[1].legend(frameon=False, fontsize=6.5, loc="lower left"); ax[1].set_title("(b) dynamic against constant film", fontsize=8.5)
    sens = dyn["sensitivity"]; labs = list(sens); vals = [sens[k]["range_median_m"] for k in labs]
    ax[2].barh(range(len(labs) + 1), [dyn["baseline"]["range_median_m"]] + vals, color=[C3] + [C4] * len(labs))
    ax[2].set_yticks(range(len(labs) + 1)); ax[2].set_yticklabels(["baseline"] + labs, fontsize=6.5); ax[2].set_xlabel("Median range [m]"); ax[2].set_title("(c) drainage assumptions", fontsize=8.5)
    save(fig, "Fig13_dynamic_film.png")


def fig_bench(bst, bcond, hm):
    fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.9))
    rows = bst["convective"]
    a = [r["t_ablation_numeric"] for r in rows]; b = [r["t_ablation_formula"] for r in rows]
    ax[0].loglog(a, b, "o", color=C1, label="ablation (formula)")
    c = [r["t_nodrain_numeric"] for r in rows]; d = [r["t_nodrain_formula"] for r in rows]
    ax[0].loglog(c, d, "s", color=C2, label="no drainage (Eq. 4)")
    lim = [min(a + c) * .8, max(a + c) * 1.2]; ax[0].plot(lim, lim, "k-", lw=.8); ax[0].set_xlabel("Enthalpy solver melt time [s]"); ax[0].set_ylabel("Formula melt time [s]"); ax[0].legend(frameon=False, fontsize=7)
    ax[0].set_title("(a) melt-time formulas", fontsize=8.5)
    dT = np.linspace(20, 160, 50)
    ax[1].plot(dT, V1.h_cond(200.4, 200.4 - dT, V1.D_PIPE) / 1e3, color=C1, label="Nusselt (first suite)")
    ax[1].plot(dT, h_chato(200.4, 200.4 - dT, V1.D_PIPE) / 1e3, color=C3, label="Chato (internal)")
    ax[1].plot(dT, 0.5 * h_chato(200.4, 200.4 - dT, V1.D_PIPE) / 1e3, color=C2, ls="--", label="Chato × 0.5 (non-condensable)")
    ax[1].set_xlabel("T$_{sat}$ − T$_{wall}$ [K]"); ax[1].set_ylabel("h [kW m$^{-2}$ K$^{-1}$]"); ax[1].legend(frameon=False, fontsize=6.5); ax[1].set_title("(b) condensation coefficient, 0.30 m bore", fontsize=8.5)
    mods = hm["models"]; names = ["Nusselt", "Chato", "Chato, NCG 0.5"]
    ax[2].bar(range(3), [mods[k]["range_median_m_s0"] for k in ("nusselt", "chato", "chato_ncg")], color=C1, width=.35, label="instant melt removal")
    ax[2].bar(np.arange(3) + .38, [mods[k]["range_median_m_s0.2"] for k in ("nusselt", "chato", "chato_ncg")], color=C3, width=.35, label="0.2 mm retained film")
    ax[2].set_xticks(np.arange(3) + .19); ax[2].set_xticklabels(names, fontsize=7); ax[2].set_ylabel("Median range [m]"); ax[2].legend(frameon=False, fontsize=6.5); ax[2].set_title("(c) effect on the range", fontsize=8.5)
    save(fig, "Fig14_benchmarks.png")


def fig_sobol(sob):
    fig, ax = plt.subplots(1, 3, figsize=(7.8, 2.9))
    for a, (key, title) in zip(ax, (("pack_temperature_45min", "(a) pack temperature, 45 min"), ("range_with_film", "(b) range (film assumed lognormal)"), ("steam_with_film", "(c) steam per metre"))):
        d = sob[key]; nm = d["names"]; ST = np.array(d["ST"]); S1 = np.array(d["S1"]); o = np.argsort(ST)
        a.barh(np.arange(len(nm)) + .2, ST[o], .38, color=C4, label="total"); a.barh(np.arange(len(nm)) - .2, S1[o], .38, color=C1, label="first order")
        a.set_yticks(range(len(nm))); a.set_yticklabels([nm[i] for i in o], fontsize=6.2); a.set_xlabel("Sobol index"); a.set_title(title, fontsize=8.5)
    ax[0].legend(frameon=False, fontsize=7, loc="lower right")
    save(fig, "Fig15_sobol.png")


def fig_pareto(des):
    fig, ax = plt.subplots(1, 3, figsize=(7.8, 2.9))
    ds = des["designs"]
    for a, mlab, ttl in ((ax[0], "instant removal", "(a) instant melt removal"), (ax[1], "dynamic film", "(b) dynamic retained film")):
        sub = [d for d in ds if d["melt"] == mlab]
        inf = [d for d in sub if not (d["fits"] and d["P_safe"] >= 0.95)]
        fe = [d for d in sub if d["fits"] and d["P_safe"] >= 0.95]
        a.plot([d["P_safe"] for d in inf], [d["range_median_m"] for d in inf], ".", color="0.82", ms=3, label="infeasible (fit or margin)")
        sc = a.scatter([d["P_safe"] for d in fe], [d["range_median_m"] for d in fe], c=[d["hull_od_mm"] for d in fe], cmap="viridis", s=12, label="feasible")
        pr = [d for d in fe if d.get("pareto")]
        a.plot([d["P_safe"] for d in pr], [d["range_median_m"] for d in pr], "o", mfc="none", mec=C2, ms=6, label="Pareto set")
        a.set_xlabel("P(pack ≤ 55 °C through the mission)"); a.set_xlim(-0.02, 1.02); a.set_ylabel("Median range per mission [m]"); a.set_title(ttl, fontsize=8.5); a.legend(frameon=False, fontsize=6.2)
    plt.colorbar(sc, ax=ax[1], label="hull OD [mm]")
    for lab, vac, col in (("atmospheric", False, C1), ("evacuated", True, C3)):
        for mission, ls in ((45, "-"), (90, ":")):
            pts = sorted([d for d in ds if d["melt"] == "instant removal" and d["vac"] == vac and d["mission_min"] == mission and d["v_set"] == 0.10], key=lambda d: d["t_a_mm"])
            ax[2].plot([d["t_a_mm"] for d in pts], [d["P_safe"] for d in pts], "o" + ls, color=col, ms=3, label="%s, %d min" % (lab, mission))
    ax[2].axhline(.95, color=C2, ls="--", lw=1); ax[2].axvline(40.5, color="0.5", ls=":", lw=1); ax[2].text(41, .08, "hull does not fit", fontsize=7, color="0.3")
    ax[2].set_xlabel("Aerogel thickness [mm]"); ax[2].set_ylabel("P(pack ≤ 55 °C through mission)"); ax[2].legend(frameon=False, fontsize=6, loc="center right"); ax[2].set_title("(c) thermal constraint", fontsize=8.5)
    save(fig, "Fig16_design_pareto.png")


def fig_envelope(env, pt):
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    P = np.array(env["P_safe"])
    im = ax.imshow(P, origin="lower", aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(env["temps"]))); ax.set_xticklabels([int(t) for t in env["temps"]]); ax.set_yticks(range(len(env["nps"]))); ax.set_yticklabels(env["nps"])
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            ax.text(j, i, "%d" % round(100 * P[i, j]), ha="center", va="center", fontsize=7)
    ax.set_xlabel("Pipe / fluid temperature [°C]"); ax.set_ylabel("Nominal pipe size [in]"); plt.colorbar(im, ax=ax, label="P(pack ≤ 55 °C, 45 min), %")
    save(fig, "Fig17_envelope.png")
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    rows = pt["rows"]
    ax.plot([r["T"] for r in rows], [r["psat_bar"] for r in rows], "-", color=C1, label="saturation pressure")
    ax.plot([r["T"] for r in rows], [r["class150_bar"] for r in rows], "--", color=C2, label="Class 150 rating (approx.)")
    ax.plot([r["T"] for r in rows], [r["class300_bar"] for r in rows], "--", color=C3, label="Class 300 rating (approx.)")
    ax.axvline(198, color="0.5", ls=":", lw=1); ax.text(150.5, 30, "model steam 198 °C", fontsize=7, color="0.3")
    ax.axvline(pt["Tmax_class150_C"], color=C2, ls=":", lw=1); ax.text(pt["Tmax_class150_C"] - 1, 4, "Class 150 limit", fontsize=7, color=C2, rotation=90, ha="right")
    ax.set_xlabel("Saturation temperature [°C]"); ax.set_ylabel("Pressure [bar]"); ax.legend(frameon=False, fontsize=6.5, loc="center left")
    save(fig, "Fig18_pressure_temperature.png")


def study_ice():
    """First-order thermal energy per metre of 12 in line for an ice-slurry route under stated assumptions (slurry volume as a fraction f_s of the line volume, ice fraction phi, latent heat 334 kJ/kg,
    ice density 917 kg/m3, carrier water cooled from 15 C, refrigeration coefficient of performance 2.5).  Illustrative bounds, not a model of ice pigging."""
    A = math.pi / 4 * T.pipe_id(12) ** 2
    rows = []
    for fs in (0.1, 0.3, 1.0):
        for phi in (0.1, 0.3):
            ice = fs * A * phi * 917.0
            water = fs * A * (1 - phi) * 1000.0
            q_th = ice * 334e3 + water * 4186.0 * 15.0
            rows.append(dict(f_s=fs, phi=phi, ice_kg_per_m=float(ice), thermal_MJ_per_m=float(q_th / 1e6), electric_MJ_per_m=float(q_th / 2.5 / 1e6)))
    boiler = V1.STEAM["hfg"] + 4186.0 * (198.0 - 15.0)
    return dict(rows=rows, pipe_volume_m3_per_m=float(A), steam_J_per_kg=float(boiler))


# ------------------------------------------------------------------------------------------------ the suite
def run_all(quick=False):
    os.makedirs(RES, exist_ok=True)
    N, Nsm = (300, 150) if quick else (3000, 800)
    t0 = time.time(); R = dict(seed=SEED, N=N, N_small=Nsm)
    base = T.study_baseline(N)
    R["bench_stefan"] = bench_stefan(); print("stefan", round(time.time() - t0, 1), flush=True)
    R["bench_conduction"] = bench_conduction(); print("cond", round(time.time() - t0, 1), flush=True)
    R["hmodels"] = study_hmodels(N); print("hmodels", round(time.time() - t0, 1), flush=True)
    flm, _, _ = T.study_film(base, N)
    dyn, bd = study_dynfilm(base, N); dyn["Pi_f_for_100m_median"] = pi_f_100m(bd[0], bd[2]); R["dynfilm"] = dyn; print("dynfilm", round(time.time() - t0, 1), flush=True)
    R["sobol"] = study_sobol(8 if quick else 9, 10 if quick else 13); print("sobol", round(time.time() - t0, 1), flush=True)
    R["corr"] = study_corr(N); print("corr", round(time.time() - t0, 1), flush=True)
    R["design"] = study_design(bd, N); print("design", round(time.time() - t0, 1), flush=True)
    R["envelope"] = study_envelope(Nsm // 2); print("envelope", round(time.time() - t0, 1), flush=True)
    R["ptcompat"] = study_ptcompat(base, N); R["uncapped"] = study_uncapped(base, N)
    R["coverage_dyn"] = study_coverage_dyn(base, bd, N); R["ice"] = study_ice()
    if not quick:
        fig_dynfilm(dyn, flm); fig_bench(R["bench_stefan"], R["bench_conduction"], R["hmodels"]); fig_sobol(R["sobol"]); fig_pareto(R["design"]); fig_envelope(R["envelope"], R["ptcompat"])
    R["runtime_s"] = round(time.time() - t0, 1)
    json.dump(R, open(os.path.join(RES, "results_quick_ext.json" if quick else "results_ext.json"), "w"), indent=1)
    return R


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true"); ap.add_argument("--quick", action="store_true"); ap.add_argument("--figures", action="store_true", help="regenerate the figures from results/results_ext.json and results/results.json")
    a = ap.parse_args()
    if a.figures:
        E = json.load(open(os.path.join(RES, "results_ext.json"))); R2 = json.load(open(os.path.join(RES, "results.json")))
        fig_dynfilm(E["dynfilm"], R2["film"]); fig_bench(E["bench_stefan"], E["bench_conduction"], E["hmodels"]); fig_sobol(E["sobol"]); fig_pareto(E["design"]); fig_envelope(E["envelope"], E["ptcompat"])
        print("figures written")
    else:
        R = run_all(quick=a.quick)
        print("done", R["runtime_s"], "s")
