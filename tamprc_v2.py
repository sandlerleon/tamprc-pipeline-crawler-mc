#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tamprc_v2.py -- second-generation studies for the Thermally Assisted Motorized Pipeline Remediation Crawler (TAMPRC).

The original single-file suite (tamprc_mc.py, unchanged) is imported and extended.  Every added mechanism can be switched off, and with all of them off the functions below
reproduce the original model draw for draw (tests/test_all.py).

Added over the original (each answers a question raised by the published challenge brief, YPF "Innovative Pipeline Cleaning Solutions"):
  film      retained melt film: the original melt model removes molten deposit instantly (ablation, an upper bound on the speed); a retained liquid layer of thickness s
            adds a conduction resistance s/k_l in series with the condensate film.  s = 0 recovers the original.
  coverage  pipe length 0.3 m - 1 km, deployments per line, active time against total intervention time (preparation, isolation, cleaning, residue handling,
            verification, return to service).
  diameter  NPS 4-16 in: fit of the hull in the bore, thermal mass, surge force.
  env       pipe/fluid temperature 0-55 C.
  bypass    seal-bypass relief as an orifice (compressible flow, finite opening time) that vents the upstream gas pocket, instead of a multiplicative force reduction.
  steam     steam budget including the heating of the pipe wall when steam reaches the tool through the line.

ALL INPUT DISTRIBUTIONS REMAIN ASSUMED, concept-stage values; nothing here is a measurement.

Usage:  python tamprc_v2.py --all       # full suite: results/results.json + figures/
        python tamprc_v2.py --quick     # small-N smoke test (does not overwrite the committed results)
"""
import argparse
import json
import math
import os
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import tamprc_mc as V1

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figures")
SEED = V1.SEED
C1, C2, C3, C4 = V1.C1, V1.C2, V1.C3, V1.C4

# Steel line pipe, standard wall: (outside diameter, wall thickness) in m
NPS = {4: (0.1143, 0.00602), 6: (0.1683, 0.00711), 8: (0.2191, 0.00818), 10: (0.2730, 0.00927), 12: (0.3239, 0.00953), 14: (0.3556, 0.00953), 16: (0.4064, 0.00953)}
RHO_S, CP_S = 7850.0, 490.0
R_PACK_NOM, T_SHELL, T_HULL = 0.060, 0.004, 0.004
CLEAR_NOM = 0.5 * (NPS[12][0] - 2 * NPS[12][1]) - (R_PACK_NOM + T_SHELL + 0.040 + T_HULL)   # radial clearance (tracks, cleats, skirt) of the original design in a 12 in pipe
R_PACK_MIN = 0.025                                                                          # smallest pack radius considered
K_LIQ = 0.15                                                                                # W/m K, molten paraffin (assumed)


def pipe_id(nps):
    od, w = NPS[nps]
    return od - 2 * w


def wilson(k, n):
    lo, hi = V1.wilson(k, n)
    return float(lo), float(hi)


# ------------------------------------------------------------------------------------------------ thermal wrapper
def thermal(N, rng, aero_mm=40.0, vac=False, r_pack=None, m_scale=1.0, T_shift=0.0, dt=10.0, t_end=7200.0):
    """Original module A with optional pack radius / mass scaling and an ambient shift of the initial temperature.  Defaults reproduce the original draw for draw."""
    old = V1.GEOM["r_pack"]
    try:
        if r_pack is not None:
            V1.GEOM["r_pack"] = r_pack
        p = V1.sample_thermal(N, rng, aero_mm, vac)
        p["m_pack"] = p["m_pack"] * m_scale
        p["T0"] = p["T0"] + T_shift
        r = V1.run_thermal(p, vac, t_end=t_end, dt=dt)
    finally:
        V1.GEOM["r_pack"] = old
    return p, r


# ------------------------------------------------------------------------------------------------ module B, extended
def deposit_v2(N, rng, Tsat, h_mult, t_run, D=V1.D_PIPE, s_ret=0.0, T_shift=0.0, v_set=0.10, k_l=K_LIQ):
    """Original deposit mobilisation (same draws in the same order) with (i) the pipe diameter as an argument, (ii) a retained melt film of thickness s_ret [m] whose conduction
    resistance s_ret/k_l is in series with the condensate film (s_ret = 0: original, instant removal of the melt), (iii) a shift of the pipe temperature.
    Also returns the no-drainage limit, in which the liquid layer grows from 0 to the full thickness."""
    d = {}
    d["delta"] = np.clip(rng.lognormal(np.log(6e-3), 0.5, N), 1e-3, 40e-3)
    d["T_melt"] = np.clip(rng.normal(58.0, 8.0, N), 40, 90)
    d["rho"] = rng.normal(850.0, 40.0, N)
    d["Lf"] = np.clip(rng.normal(200e3, 30e3, N), 100e3, 300e3)
    d["c"] = 2100.0
    d["T_pipe"] = rng.normal(25.0, 5.0, N) + T_shift
    d["eta"] = rng.uniform(0.15, 0.50, N)
    d["m_nc"] = rng.uniform(0.5, 1.0, N)
    d["Lz"] = rng.uniform(0.3, 0.8, N)
    h = V1.h_cond(Tsat, d["T_melt"], D, h_mult * d["m_nc"])
    dT = Tsat - d["T_melt"]
    s = np.broadcast_to(np.asarray(s_ret, float), (N,))
    q_raw = h * dT
    q_film = q_raw if not np.any(s) else dT / (1.0 / h + s / k_l)
    q_eff = d["eta"] * q_film
    e = d["rho"] * d["delta"] * (d["Lf"] + d["c"] * (d["T_melt"] - d["T_pipe"]))
    t_melt = e / q_eff
    v_th = d["Lz"] / t_melt
    v = np.minimum(v_set, v_th)
    hfgp = V1.STEAM["hfg"] + 0.68 * V1.STEAM["cp_l"] * (Tsat - d["T_melt"])
    mdot = q_film * np.pi * D * d["Lz"] / hfgp
    # no-drainage limit: liquid layer s grows 0 -> delta, flux = eta*dT/(1/h + s/k_l)
    ev = d["rho"] * (d["Lf"] + d["c"] * (d["T_melt"] - d["T_pipe"]))
    t_nd = ev * (d["delta"] / h + d["delta"] ** 2 / (2 * k_l)) / (d["eta"] * dT)
    v_nd = np.minimum(v_set, d["Lz"] / t_nd)
    return dict(h=h, q_raw=q_raw, q_eff=q_eff, t_melt=t_melt, v_th=v_th, v=v, range=v * t_run, steam_kg_per_m=mdot / v, delta=d["delta"], T_melt=d["T_melt"], eta=d["eta"],
                m_nc=d["m_nc"], Lz=d["Lz"], t_melt_nodrain=t_nd, v_nodrain=v_nd, range_nodrain=v_nd * t_run)


# ------------------------------------------------------------------------------------------------ module C, orifice bypass
R_GAS, T_GAS, GAMMA = 518.0, 300.0, 1.3          # methane-like gas in the pocket (assumed)
R_CRIT = (2.0 / (GAMMA + 1.0)) ** (GAMMA / (GAMMA - 1.0))


def orifice_mdot(P1, P2, CdA):
    """Isentropic compressible mass flow through an orifice, choked below the critical pressure ratio."""
    r = np.maximum(np.clip(P2 / P1, 0.0, 1.0), R_CRIT)
    f = np.sqrt(np.maximum(r ** (2.0 / GAMMA) - r ** ((GAMMA + 1.0) / GAMMA), 0.0))
    return CdA * P1 * np.sqrt(2.0 * GAMMA / ((GAMMA - 1.0) * R_GAS * T_GAS)) * f


def run_surge(b, mode, Ab_cm2=0.0, D=V1.D_PIPE, v_set=0.10, T=5.0, dt=0.001, Cd=0.7, crack=0.5e5, keep_trace=False):
    """Blockage release with an orifice bypass.  The upstream gas pocket (mass fraction phi of the original, adiabatic) expands as the tool moves and vents through the
    bypass; P = P0 (phi V0 / V)**gamma.  mode: 'passive' (5 % seal leakage, no controller), 'regen' (controller only), 'orifice' (controller + bypass of area Ab_cm2).
    Ab_cm2 = 0 and mode 'passive' or 'regen' reproduce the original model exactly."""
    N = len(b["dPb"]); A = math.pi / 4 * D ** 2
    m = b["m_pig"] if mode == "passive" else b["m_cr"]
    leak = 0.05 if mode == "passive" else 0.0
    v = np.full(N, v_set); x = np.zeros(N); I = np.zeros(N)
    P0 = b["Pd"] + b["dPb"]; V0 = b["Vg"]; m0 = P0 * V0 / (R_GAS * T_GAS); phi = np.ones(N); u = np.zeros(N)
    vpk = v.copy(); t_over = np.zeros(N); Kp, Ki = 2e4, 2e4
    CdA = Cd * Ab_cm2 * 1e-4
    steps = int(T / dt); trace = []
    for s in range(steps):
        P = P0 * (phi * V0 / (V0 + A * x)) ** GAMMA
        dP = P - b["Pd"]
        F = A * dP * (1 - leak)
        e = v - v_set
        if mode == "passive":
            Fc = 0.0
        else:
            I = np.clip(I + Ki * e * dt, -b["Ft"], b["Fb"])
            Fc = np.clip(Kp * e + I, -b["Ft"], b["Fb"])
        if mode == "orifice" and CdA > 0:
            ucmd = np.clip((dP - crack) / crack, 0.0, 1.0)
            u = u + dt * (ucmd - u) / b["tau_v"]
            mdot = orifice_mdot(P, b["Pd"], CdA * np.clip(u, 0, 1))
            phi = np.maximum(phi - mdot * dt / m0, 0.0)
        a = (F - b["Ff"] - b["cd"] * v * v - Fc) / m
        v = np.maximum(v + a * dt, 0.0); x = x + v * dt
        vpk = np.maximum(vpk, v); t_over += (v > 5 * v_set) * dt
        if keep_trace and s % 5 == 0:
            trace.append(v.copy())
    out = dict(vpk=vpk, t_over=t_over, v_end=v, x_end=x, phi_end=phi)
    if keep_trace:
        out["trace"] = np.array(trace); out["t"] = np.arange(0, steps, 5) * dt
    return out


def vent_time(b, Ab_cm2, frac=0.5, Cd=0.7, T=3.0, dt=0.0005):
    """Time for a fully open bypass of area Ab_cm2 to remove the fraction `frac` of the break-through differential from a tool held at x = 0 (valve open from t = 0, no lag):
    the lower bound on the time a bypass needs to act.  Returns seconds (T if not reached)."""
    N = len(b["dPb"]); P0 = b["Pd"] + b["dPb"]; m0 = P0 * b["Vg"] / (R_GAS * T_GAS); phi = np.ones(N); t_hit = np.full(N, T)
    CdA = Cd * Ab_cm2 * 1e-4
    for s in range(int(T / dt)):
        P = P0 * phi ** GAMMA
        hit = (P - b["Pd"]) <= (1.0 - frac) * b["dPb"]
        t_hit = np.where(hit & (t_hit == T), s * dt, t_hit)
        phi = np.maximum(phi - orifice_mdot(P, b["Pd"], CdA) * dt / m0, 0.0)
    return t_hit


def hold_area_cm2(Qs, P1, dP, Cd=0.7):
    """Bypass flow area that passes the volumetric supply flow Qs [m3/s, at the upstream pressure P1 and T_GAS] with a steady differential dP [Pa] (the design relation
    for a bypass that is open during the stall)."""
    rho = P1 / (R_GAS * T_GAS)
    unit = orifice_mdot(np.array(P1), np.array(P1 - dP), 1.0)           # kg/s per m2 of CdA
    return float(rho * Qs / (Cd * unit) * 1e4)


# ------------------------------------------------------------------------------------------------ geometry of the hull in the bore
def hull_geometry(nps):
    """Hull of the original design (pack + 4 mm shell + aerogel + 4 mm hull) fitted in a pipe of nominal size nps with the same radial clearance as in the 12 in case."""
    ID = pipe_id(nps)
    r_hull = ID / 2 - CLEAR_NOM
    r_pack = min(R_PACK_NOM, r_hull - T_SHELL - 0.040 - T_HULL)
    t_a = 0.040
    if r_pack < R_PACK_MIN:
        r_pack = R_PACK_MIN
        t_a = r_hull - T_SHELL - T_HULL - r_pack
    return dict(nps=nps, ID=ID, r_hull=r_hull, r_pack=r_pack, t_a=t_a, feasible=bool(t_a >= 0.005), m_pack_nom=16.0 * (r_pack / R_PACK_NOM) ** 2)


def steam_wall_kg_per_m(nps, Tsat=198.0, T_pipe=25.0):
    od, w = NPS[nps]
    A_s = math.pi * (od - w) * w
    return RHO_S * A_s * CP_S * (Tsat - T_pipe) / V1.STEAM["hfg"], RHO_S * A_s


# ------------------------------------------------------------------------------------------------ studies
def study_baseline(N, tag=""):
    """Baseline thermal draws (atmospheric and evacuated, 40 mm) shared by the range, coverage and film studies."""
    rng = np.random.default_rng(SEED + 1)
    out = {}
    for name, vac in (("atm", False), ("vac", True)):
        p, r = thermal(N, rng, 40.0, vac)
        out[name] = (p, r)
    return out


def study_film(base, N):
    """Range against the retained-film thickness (CRN across thicknesses)."""
    p, r = base["atm"]
    t_run = np.minimum(r["t_crit"], 2700.0)
    sweep = [0.0, 0.05e-3, 0.1e-3, 0.2e-3, 0.5e-3, 1.0e-3, 2.0e-3, 5.0e-3]
    rows = []; ex = {}
    for s in sweep:
        B = deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=s)
        rg = B["range"]
        rows.append(dict(s_mm=s * 1e3, v_th_median_cms=float(np.median(B["v_th"]) * 100), range_median_m=float(np.median(rg)), range_p05_m=float(np.percentile(rg, 5)),
                         range_p95_m=float(np.percentile(rg, 95)), P_ge_100=float((rg >= 100).mean()), P_ge_200=float((rg >= 200).mean()), P_ge_250=float((rg >= 250).mean()),
                         frac_thermally_limited=float((B["v_th"] < 0.10).mean()), steam_kg_per_m_median=float(np.median(B["steam_kg_per_m"]))))
        ex[s] = rg
    B0 = deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=0.0)
    nd = dict(v_nodrain_median_cms=float(np.median(B0["v_nodrain"]) * 100), range_nodrain_median_m=float(np.median(B0["range_nodrain"])),
              range_nodrain_p95_m=float(np.percentile(B0["range_nodrain"], 95)), P_ge_100=float((B0["range_nodrain"] >= 100).mean()), t_melt_nodrain_median_s=float(np.median(B0["t_melt_nodrain"])),
              t_melt_ablation_median_s=float(np.median(B0["t_melt"])),
              ratio_median=float(np.median(B0["t_melt_nodrain"] / B0["t_melt"])))
    # smallest retained film that takes the median range below 100 m
    ss = np.logspace(-5, -2, 61); med = []
    for s in ss:
        Bs = deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=s)
        med.append(float(np.median(Bs["range"])))
    med = np.array(med); idx = int(np.argmax(med < 100.0)) if np.any(med < 100.0) else None
    s100 = float(ss[idx] * 1e3) if idx is not None else None
    return dict(rows=rows, nodrain=nd, s_median_below_100m_mm=s100, k_liq=K_LIQ), ex, (ss, med)


def study_coverage(base, N):
    """Deployments per line and intervention time against pipe length, for three melt-removal cases and two missions."""
    rngT = np.random.default_rng(SEED + 202)
    lengths = [0.3, 10.0, 100.0, 300.0, 600.0, 1000.0]
    cases = {"ablation": dict(s=0.0, nd=False), "retained 0.5 mm": dict(s=0.5e-3, nd=False), "no drainage": dict(s=0.0, nd=True)}
    out = {}
    stage = dict(prep=rngT.uniform(3, 8, N), turn=rngT.uniform(1, 3, N), verify=rngT.uniform(1, 3, N), rts=rngT.uniform(2, 6, N))     # h, assumed
    for mission, (key, tmax) in {"45 min atmospheric": ("atm", 2700.0), "90 min evacuated": ("vac", 5400.0)}.items():
        p, r = base[key]
        t_run = np.minimum(r["t_crit"], tmax)
        for cname, c in cases.items():
            B = deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, s_ret=c["s"])
            v = B["v_nodrain"] if c["nd"] else B["v"]
            rg = v * t_run
            for L in lengths:
                nd_ = np.ceil(L / rg)
                active = L / v / 3600.0
                total = stage["prep"] + active + (nd_ - 1) * stage["turn"] + stage["verify"] + stage["rts"]
                out["%s|%s|%g" % (mission, cname, L)] = dict(P_single=float((rg >= L).mean()), n_dep_median=float(np.median(nd_)), n_dep_p95=float(np.percentile(nd_, 95)), active_h_median=float(np.median(active)),
                                                          total_h_median=float(np.median(total)), total_h_p05=float(np.percentile(total, 5)), total_h_p95=float(np.percentile(total, 95)),
                                                          active_fraction_median=float(np.median(active / total)), range_median_m=float(np.median(rg)), range_max_m=float(rg.max()))
    return dict(lengths=lengths, cases=list(cases), missions=["45 min atmospheric", "90 min evacuated"], rows=out,
                stage_assumptions_h=dict(prep="U(3,8)", turnaround="U(1,3)", verification="U(1,3)", return_to_service="U(2,6)"))


def study_diameter(N):
    """Fit and thermal margin against nominal pipe size."""
    rows = []
    for nps in sorted(NPS):
        g = hull_geometry(nps)
        row = dict(g)
        for name, vac in (("atm", False), ("vac", True)):
            if g["feasible"]:
                rng = np.random.default_rng(SEED + 303)
                p, r = thermal(N, rng, g["t_a"] * 1e3, vac, r_pack=g["r_pack"], m_scale=(g["r_pack"] / R_PACK_NOM) ** 2, dt=15.0)
                ok = int((r["Tp45"] <= 55).sum()); lo, hi = wilson(ok, N)
                row["P_safe_" + name] = ok / N; row["P_safe_%s_ci" % name] = [lo, hi]; row["Tp45_median_" + name] = float(np.median(r["Tp45"]))
            else:
                row["P_safe_" + name] = None
        A = math.pi / 4 * g["ID"] ** 2
        row["force_3bar_kN"] = A * 3e5 / 1e3
        row["brake_ratio_3bar"] = A * 3e5 / 2500.0
        # condensation coefficient scale and steam per meter scale relative to 12 in
        row["h_scale"] = float((g["ID"] / pipe_id(12)) ** -0.25)
        row["steam_scale"] = float(g["ID"] / pipe_id(12))
        rows.append(row)
    return dict(rows=rows, clearance_m=CLEAR_NOM, r_pack_min=R_PACK_MIN)


def study_env(N):
    """Pipe / fluid temperature (shifts the initial pack and pipe temperatures; same random draws)."""
    temps = [0.0, 10.0, 25.0, 35.0, 45.0, 55.0]
    rows = []
    for Ta in temps:
        row = dict(T_amb=Ta)
        for name, vac in (("atm", False), ("vac", True)):
            rng = np.random.default_rng(SEED + 404)
            p, r = thermal(N, rng, 40.0, vac, T_shift=Ta - 25.0, dt=15.0)
            ok = int((r["Tp45"] <= 55).sum()); lo, hi = wilson(ok, N)
            row["P_safe_" + name] = ok / N; row["P_safe_%s_ci" % name] = [lo, hi]; row["Tp45_median_" + name] = float(np.median(r["Tp45"]))
            if name == "atm":
                t_run = np.minimum(r["t_crit"], 2700.0)
                B = deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, T_shift=Ta - 25.0)
                row["range_median_m"] = float(np.median(B["range"])); row["t_melt_median_s"] = float(np.median(B["t_melt"]))
        rows.append(row)
    return dict(rows=rows)


def study_bypass(Nd):
    """Peak speed against bypass area and pocket volume (orifice model)."""
    rng = np.random.default_rng(SEED + 505)
    b = V1.sample_blockage(Nd, rng)
    areas = [0.0, 5.0, 10.0, 20.0, 40.0, 80.0, 160.0, 320.0]
    out = dict(areas_cm2=areas, pipe_area_cm2=V1.A_PIPE * 1e4, by_volume={}, general=[])
    for Ab in areas:
        o = run_surge(b, "orifice", Ab)
        out["general"].append(dict(Ab_cm2=Ab, vpk_median=float(np.median(o["vpk"])), vpk_p95=float(np.percentile(o["vpk"], 95)), P_gt_1=float((o["vpk"] > 1).mean()), P_gt_2=float((o["vpk"] > 2).mean()),
                                    phi_end_median=float(np.median(o["phi_end"]))))
    for Vg in (0.3, 1.0, 3.0, 10.0):
        bb = dict(b); bb["Vg"] = np.full(Nd, Vg)
        rows = []
        for Ab in areas:
            o = run_surge(bb, "orifice", Ab)
            rows.append(dict(Ab_cm2=Ab, vpk_median=float(np.median(o["vpk"])), P_gt_1=float((o["vpk"] > 1).mean()), P_gt_2=float((o["vpk"] > 2).mean())))
        out["by_volume"][str(Vg)] = rows
    # reference: the original multiplicative model on the same draws
    ref = {}
    for mode in ("passive", "regen", "relief"):
        o = V1.run_dieseling(b, mode)
        ref[mode] = dict(vpk_median=float(np.median(o["vpk"])), P_gt_1=float((o["vpk"] > 1).mean()), P_gt_2=float((o["vpk"] > 2).mean()))
    out["original_model"] = ref
    # time scales: acceleration to 1 m/s against the time a fully open bypass needs to halve the differential
    F0 = V1.A_PIPE * b["dPb"] - b["Ff"]
    t_acc = b["m_cr"] * 1.0 / np.maximum(F0, 1.0)
    out["t_accel_1ms_median_ms"] = float(np.median(t_acc) * 1e3); out["t_accel_1ms_p05_ms"] = float(np.percentile(t_acc, 5) * 1e3)
    vt = {}
    for Vg in (0.3, 1.0, 3.0, 10.0):
        bb = dict(b); bb["Vg"] = np.full(Nd, Vg); row = {}
        for Ab in (20.0, 80.0, 320.0):
            row[str(Ab)] = float(np.median(vent_time(bb, Ab)) * 1e3)
        vt[str(Vg)] = row
    out["vent_time_median_ms"] = vt
    out["hold_area_cm2"] = [dict(Qs_m3_s=q, area_cm2=hold_area_cm2(q, 18e5, 0.5e5)) for q in (0.01, 0.03, 0.1, 0.3, 1.0)]
    out["hold_pressure_bar"] = 0.5; out["hold_upstream_bar"] = 18.0
    # the nominal event for the figure
    nom = {k: np.array([v]) for k, v in dict(dPb=3e5, Vg=1.0, Pd=15e5, Ff=400.0, cd=2000.0, m_pig=80.0, m_cr=120.0, Fb=2500.0, Ft=1500.0, beta_max=.92, tau_v=.015).items()}
    tr = {}
    for lab, mode, Ab in (("passive", "passive", 0.0), ("regen", "regen", 0.0), ("orifice 20 cm2", "orifice", 20.0), ("orifice 80 cm2", "orifice", 80.0)):
        o = run_surge(nom, mode, Ab, keep_trace=True); tr[lab] = dict(t=o["t"].tolist(), v=o["trace"][:, 0].tolist(), vpk=float(o["vpk"][0]))
    out["nominal"] = tr
    return out


def study_steam(base, N):
    """Steam per meter: deposit melting (original, by size) plus heating the pipe wall when steam reaches the tool through the line."""
    p, r = base["atm"]; t_run = np.minimum(r["t_crit"], 2700.0)
    rows = []
    for nps in sorted(NPS):
        D = pipe_id(nps)
        B = deposit_v2(N, np.random.default_rng(SEED + 101), p["Tsat"], p["h_mult"], t_run, D=D)
        clean = float(np.median(B["steam_kg_per_m"]))
        w25, mass_m = steam_wall_kg_per_m(nps, 198.0, 25.0)
        w0, _ = steam_wall_kg_per_m(nps, 198.0, 0.0)
        rows.append(dict(nps=nps, ID=D, steel_kg_per_m=mass_m, clean_kg_per_m=clean, wall_kg_per_m_25C=w25, wall_kg_per_m_0C=w0, total_kg_per_m_25C=clean + w25, total_t_per_km_25C=(clean + w25),
                         clean_t_per_km=clean, wall_ratio=w25 / clean))
    return dict(rows=rows, hose_note="a steam hose carried inside the pipe avoids heating the pipe wall but adds a tether drag and a second 200 C line to the tool")


def study_verify(Nd=2000):
    """Mesh refinement of the thermal model for the deterministic nominal case, and the equivalence checks."""
    p = dict(t_a=np.array([0.04]), k_mult=np.array([1.0]), phi_br=np.array([0.175]), P_gen=np.array([70.0]), m_pack=np.array([16.0]), T0=np.array([25.0]), Tsat=np.array([198.0]),
             h_mult=np.array([1.0]), vac_lost=np.array([False]))
    rows = []
    for ns, na, nh, dt in ((2, 16, 2, 10.0), (4, 32, 4, 5.0), (8, 64, 8, 2.5), (16, 128, 16, 1.25)):
        r = V1.run_thermal(p, False, t_end=2700.0, dt=dt, ns=ns, na=na, nh=nh)
        rows.append(dict(cells=ns + na + nh, dt=dt, Tp45=float(r["Tp45"][0])))
    ref = rows[-1]["Tp45"]
    for rw in rows:
        rw["diff_to_finest_K"] = rw["Tp45"] - ref
    return dict(mesh=rows)


# ------------------------------------------------------------------------------------------------ figures
def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(FIG, name)); plt.close(fig)


def fig_film(film, ex, curve):
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    rows = film["rows"]; s = np.array([r["s_mm"] for r in rows]); eps = 0.02
    xs = np.maximum(s, 0.02)
    ax[0].fill_between(xs, [r["range_p05_m"] for r in rows], [r["range_p95_m"] for r in rows], color=C1, alpha=.2, lw=0)
    ax[0].plot(xs, [r["range_median_m"] for r in rows], "o-", color=C1, label="median")
    ax[0].axhline(film["nodrain"]["range_nodrain_median_m"], color=C2, ls="--", lw=1); ax[0].text(0.025, film["nodrain"]["range_nodrain_median_m"] * 1.25, "no drainage (median)", color=C2, fontsize=7)
    ax[0].axhline(1000, color="k", ls=":", lw=1); ax[0].text(0.025, 1.12e3, "1 km (brief)", fontsize=7)
    ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_xlabel("Retained melt film  s  [mm]  (s = 0 plotted at 0.02)"); ax[0].set_ylabel("Cleaned range per 45 min [m]")
    ax[0].set_ylim(0.3, 3000); ax[0].legend(frameon=False, fontsize=7, loc="lower left")
    for sv, col in ((0.0, C1), (0.2e-3, C3), (1.0e-3, C4)):
        xv = np.sort(ex[sv]); ax[1].plot(xv, 1 - np.arange(len(xv)) / len(xv), color=col, label="s = %g mm" % (sv * 1e3))
    ax[1].axvline(300, color="k", ls=":", lw=1); ax[1].text(305, .55, "300 m", fontsize=7)
    ax[1].set_xscale("log"); ax[1].set_xlabel("Cleaned range per deployment [m]"); ax[1].set_ylabel("P(range ≥ x)"); ax[1].legend(frameon=False, fontsize=7)
    save(fig, "Fig6_film.png")


def fig_coverage(cov):
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    L = cov["lengths"]; cols = {"ablation": C1, "retained 0.5 mm": C3, "no drainage": C2}
    for cname in cov["cases"]:
        ax[0].plot(L[1:], [cov["rows"]["45 min atmospheric|%s|%g" % (cname, l)]["P_single"] for l in L[1:]], "o-", color=cols[cname], label=cname)
        ax[0].plot(L[1:], [cov["rows"]["90 min evacuated|%s|%g" % (cname, l)]["P_single"] for l in L[1:]], "x:", color=cols[cname], lw=1)
    ax[0].set_xscale("log"); ax[0].set_xlabel("Pipe length [m]  (dotted: 90 min evacuated)"); ax[0].set_ylabel("P(one deployment cleans the line)"); ax[0].legend(frameon=False, fontsize=7)
    ax[0].set_ylim(-.03, 1.03)
    w = 0.25; xs = np.arange(len(L))
    for i, cname in enumerate(cov["cases"]):
        act = [cov["rows"]["45 min atmospheric|%s|%g" % (cname, l)]["active_h_median"] for l in L]
        tot = [cov["rows"]["45 min atmospheric|%s|%g" % (cname, l)]["total_h_median"] for l in L]
        ax[1].bar(xs + (i - 1) * w, tot, w, color=cols[cname], alpha=.45)
        ax[1].bar(xs + (i - 1) * w, act, w, color=cols[cname], label=cname)
    ax[1].set_xticks(xs); ax[1].set_xticklabels(["%g" % l for l in L]); ax[1].set_yscale("log"); ax[1].set_xlabel("Pipe length [m]"); ax[1].set_ylabel("Median time [h]  (dark: active cleaning; light: total)")
    ax[1].legend(frameon=False, fontsize=7)
    save(fig, "Fig7_coverage.png")


def fig_diameter(dia, env):
    fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.9))
    rows = dia["rows"]; nps = [r["nps"] for r in rows]
    for name, col, lab in (("atm", C1, "atmospheric"), ("vac", C3, "evacuated")):
        ys = [r["P_safe_" + name] if r["P_safe_" + name] is not None else np.nan for r in rows]
        ax[0].plot(nps, ys, "o-", color=col, label=lab)
    for r in rows:
        if not r["feasible"]:
            ax[0].plot([r["nps"]], [0.02], "x", color=C2, ms=8)
    ax[0].axhline(.95, color=C2, ls="--", lw=1); ax[0].set_xlabel("Nominal pipe size [in]"); ax[0].set_ylabel("P(pack ≤ 55 °C, 45 min)"); ax[0].legend(frameon=False, fontsize=7); ax[0].set_ylim(-.03, 1.05)
    ax[0].text(4.1, .08, "× hull does not fit", color=C2, fontsize=7)
    ax[1].plot(nps, [2 * r["r_hull"] * 1e3 for r in rows], "o-", color=C4, label="hull OD fitted")
    ax[1].plot(nps, [r["ID"] * 1e3 for r in rows], "s--", color="0.4", label="pipe bore")
    ax[1].plot(nps, [2 * (R_PACK_NOM + 0.048) * 1e3] * len(nps), ":", color="k", label="original hull (216 mm)")
    ax[1].set_xlabel("Nominal pipe size [in]"); ax[1].set_ylabel("Diameter [mm]"); ax[1].legend(frameon=False, fontsize=7)
    t = [r["T_amb"] for r in env["rows"]]
    for name, col, lab in (("atm", C1, "atmospheric"), ("vac", C3, "evacuated")):
        ax[2].plot(t, [r["P_safe_" + name] for r in env["rows"]], "o-", color=col, label=lab)
    ax[2].axhline(.95, color=C2, ls="--", lw=1); ax[2].set_xlabel("Pipe / fluid temperature [°C]"); ax[2].set_ylabel("P(pack ≤ 55 °C, 45 min)"); ax[2].legend(frameon=False, fontsize=7); ax[2].set_ylim(-.03, 1.05)
    save(fig, "Fig8_diameter_temperature.png")


def fig_bypass(byp):
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
    cols = {"0.3": C2, "1.0": C4, "3.0": C3, "10.0": C1}
    for Vg, rows in byp["by_volume"].items():
        a = np.array([r["Ab_cm2"] for r in rows]); y = [r["P_gt_1"] for r in rows]
        ax[0].plot(np.maximum(a, 2.5), y, "o-", color=cols[Vg], label="V$_g$ = %s m³" % Vg)
    ax[0].set_xscale("log"); ax[0].set_xlabel("Bypass flow area [cm²]  (0 plotted at 2.5)"); ax[0].set_ylabel("P(peak speed > 1 m/s)"); ax[0].legend(frameon=False, fontsize=7); ax[0].set_ylim(-.03, 1.03)
    ax[0].axhline(byp["original_model"]["relief"]["P_gt_1"], color="k", ls=":", lw=1); ax[0].text(2.6, byp["original_model"]["relief"]["P_gt_1"] + .02, "original relief model", fontsize=7)
    for lab, col in (("passive", C2), ("regen", C4), ("orifice 20 cm2", C3), ("orifice 80 cm2", C1)):
        d = byp["nominal"][lab]; ax[1].plot(d["t"], d["v"], color=col, label=lab.replace("cm2", "cm²"))
    ax[1].set_xlim(0, 2.5); ax[1].set_xlabel("Time after break-through [s]"); ax[1].set_ylabel("Speed [m/s]"); ax[1].legend(frameon=False, fontsize=7); ax[1].set_title("Nominal 3 bar break-through, 1 m³ pocket", fontsize=8.5)
    save(fig, "Fig10_bypass.png")


def fig_steam(st):
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    n_ = [r["nps"] for r in st["rows"]]
    ax.bar(n_, [r["clean_kg_per_m"] for r in st["rows"]], color=C1, label="melting the deposit")
    ax.bar(n_, [r["wall_kg_per_m_25C"] for r in st["rows"]], bottom=[r["clean_kg_per_m"] for r in st["rows"]], color=C4, label="heating the pipe wall (25 → 198 °C)")
    ax.set_xlabel("Nominal pipe size [in]"); ax.set_ylabel("Steam per meter of line [kg/m]"); ax.legend(frameon=False, fontsize=7)
    save(fig, "Fig11_steam_budget.png")


# ------------------------------------------------------------------------------------------------ the suite
def run_all(quick=False):
    os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
    N, Nd = (300, 1500) if quick else (3000, 10000)
    Nsm = 200 if quick else 800
    t0 = time.time(); R = dict(seed=SEED, N=N, N_surge=Nd, N_small=Nsm)
    base = study_baseline(N)
    for k in ("atm", "vac"):
        r = base[k][1]; ok = int((r["Tp45"] <= 55).sum()); lo, hi = wilson(ok, N)
        R["baseline_" + k] = dict(P_safe=ok / N, ci=[lo, hi], Tp45_median=float(np.median(r["Tp45"])), t_crit_median_min=float(np.median(r["t_crit"]) / 60))
    print("baseline", round(time.time() - t0, 1))
    film, ex, curve = study_film(base, N); R["film"] = film; fig_film(film, ex, curve); print("film", round(time.time() - t0, 1))
    R["coverage"] = study_coverage(base, N); fig_coverage(R["coverage"]); print("coverage", round(time.time() - t0, 1))
    R["diameter"] = study_diameter(Nsm); print("diameter", round(time.time() - t0, 1))
    R["env"] = study_env(Nsm); fig_diameter(R["diameter"], R["env"]); print("env", round(time.time() - t0, 1))
    R["bypass"] = study_bypass(Nd if not quick else 600); fig_bypass(R["bypass"]); print("bypass", round(time.time() - t0, 1))
    R["steam"] = study_steam(base, N); fig_steam(R["steam"])
    R["verify"] = study_verify()
    R["runtime_s"] = round(time.time() - t0, 1)
    out = os.path.join(RES, "results_quick.json" if quick else "results.json")
    json.dump(R, open(out, "w"), indent=1)
    return R


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true"); ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    R = run_all(quick=a.quick)
    print(json.dumps({k: R[k] for k in ("baseline_atm", "baseline_vac")}, indent=1))
