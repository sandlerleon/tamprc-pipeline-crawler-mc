#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automated checks (no test framework needed):  python tests/test_all.py

They verify (i) that the original model (tamprc_mc.py, unchanged) is intact and reproduces its published results, (ii) that every mechanism added in tamprc_v2.py reduces to the
original when switched off, (iii) limits and conservation properties of the added mechanisms, and (iv) that the committed results are consistent.  They do not validate the model
against measurements; no measurements exist for these inputs.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import tamprc_mc as V1       # noqa: E402
import tamprc_v2 as T        # noqa: E402
import tamprc_v3 as X        # noqa: E402

RESULTS = json.load(open(os.path.join(ROOT, "results", "results.json"), encoding="utf-8"))
EXT = json.load(open(os.path.join(ROOT, "results", "results_ext.json"), encoding="utf-8"))
V1R = json.load(open(os.path.join(ROOT, "results", "v1_results.json"), encoding="utf-8"))
N_OK = 0


def check(name, cond, info=""):
    global N_OK
    print(("ok    " if cond else "FAIL  ") + name + (("  " + info) if info else ""))
    if not cond:
        sys.exit(1)
    N_OK += 1


# ---- (i) the original model
sha = hashlib.sha256(open(os.path.join(ROOT, "tamprc_mc.py"), "rb").read()).hexdigest()
check("original file unchanged (sha256 of the submitted package)", sha.startswith("ede1fa88249dea49"), sha[:16])
check("original results: 98.9 % atmospheric, 99.7 % evacuated", abs(V1R["A_atmospheric"]["P_safe"] - 0.98867) < 1e-4 and abs(V1R["A_evacuated"]["P_safe"] - 0.99733) < 1e-4)
check("original results: median range 138 m, passive pig peak 3.0 m/s", abs(V1R["B"]["range_median_m"] - 138.47) < 0.01 and abs(V1R["C_passive"]["vpk_median"] - 3.0) < 0.1)
mf = V1.mean_field_fouled(np.array([0.8]), 0.8)
check("exact maintenance-lattice formula (x = 0.8, p = 0.8): before-pass fouled fraction", abs(mf[0][0] - (1 - math.exp(-0.8)) / (1 - 0.2 * math.exp(-0.8))) < 1e-12)

# ---- (ii) reductions to the original
N = 400
p1 = V1.sample_thermal(N, np.random.default_rng(5), 40.0, False); r1 = V1.run_thermal(p1, False)
p2, r2 = T.thermal(N, np.random.default_rng(5), 40.0, False)
check("thermal wrapper with default arguments equals the original (pack temperature histories)", np.array_equal(r1["Tp"], r2["Tp"]))
t_run = np.minimum(r1["t_crit"], 2700.0)
B1 = V1.deposit_mobilisation(N, np.random.default_rng(9), p1["Tsat"], p1["h_mult"], t_run)
B2 = T.deposit_v2(N, np.random.default_rng(9), p1["Tsat"], p1["h_mult"], t_run)
check("deposit_v2 with s_ret = 0 equals the original (speed, range, steam per metre, melt time)", all(np.allclose(B1[k], B2[k], rtol=1e-12, atol=0) for k in ("v_th", "range", "steam_kg_per_m", "t_melt")))
b = V1.sample_blockage(500, np.random.default_rng(3))
for mode, new in (("passive", "passive"), ("regen", "regen")):
    o1 = V1.run_dieseling(b, mode); o2 = T.run_surge(b, new, 0.0)
    check("run_surge '%s' equals the original model (peak speed)" % mode, np.allclose(o1["vpk"], o2["vpk"], rtol=1e-12, atol=0))
o3 = T.run_surge(b, "orifice", 0.0)
check("orifice mode with zero area equals the controller-only crawler", np.allclose(o3["vpk"], T.run_surge(b, "regen", 0.0)["vpk"], rtol=1e-12, atol=0))

# ---- (iii) limits and conservation
rows = RESULTS["film"]["rows"]
check("range decreases monotonically with the retained film thickness", all(rows[i]["range_median_m"] >= rows[i + 1]["range_median_m"] for i in range(len(rows) - 1)))
check("no-drainage limit is the slowest case (below every finite-film median)", RESULTS["film"]["nodrain"]["range_nodrain_median_m"] < rows[-1]["range_median_m"] * 2.0 or RESULTS["film"]["nodrain"]["range_nodrain_median_m"] < rows[4]["range_median_m"])
# analytic: for a single deterministic deposit the melt time scales as 1/q and a series resistance s/k adds to 1/h
h = float(V1.h_cond(198.0, 58.0, 0.30)); s = 0.2e-3
check("series-resistance flux: q(s)/q(0) = 1/(1 + h s / k_l)", abs((1.0 / (1 / h + s / T.K_LIQ)) / h - 1.0 / (1 + h * s / T.K_LIQ)) < 1e-12)
check("condensation coefficient scales as D^(-1/4)", abs(float(V1.h_cond(198.0, 58.0, 0.15)) / float(V1.h_cond(198.0, 58.0, 0.30)) - 2 ** 0.25) < 1e-12)
# orifice
check("orifice mass flow is zero at zero differential and choked below the critical pressure ratio", float(T.orifice_mdot(np.array(10e5), np.array(10e5), 1e-3)) == 0.0
      and abs(float(T.orifice_mdot(np.array(10e5), np.array(2e5), 1e-3)) - float(T.orifice_mdot(np.array(10e5), np.array(1e5), 1e-3))) < 1e-12)
o = T.run_surge(b, "orifice", 160.0)
check("pocket gas fraction stays in [0, 1] and speeds are finite", float(o["phi_end"].min()) >= 0.0 and float(o["phi_end"].max()) <= 1.0 and np.isfinite(o["vpk"]).all())
check("a larger bypass never raises the median peak speed", all(RESULTS["bypass"]["general"][i]["vpk_median"] >= RESULTS["bypass"]["general"][i + 1]["vpk_median"] - 1e-9 for i in range(len(RESULTS["bypass"]["general"]) - 1)))
vt = RESULTS["bypass"]["vent_time_median_ms"]
check("venting time scales with pocket volume (x10 volume, about x10 time) and falls with area", 8.0 < vt["10.0"]["80.0"] / vt["1.0"]["80.0"] < 12.0 and vt["1.0"]["20.0"] > vt["1.0"]["80.0"] > vt["1.0"]["320.0"])
a = [r["area_cm2"] for r in RESULTS["bypass"]["hold_area_cm2"]]
check("bypass area that holds the stall differential is proportional to the supply flow", abs(a[-1] / a[0] - 100.0) < 1e-6)
# geometry and steam budget
g = T.hull_geometry(12)
check("12 in hull reproduces the original design (pack radius 60 mm, aerogel 40 mm)", abs(g["r_pack"] - 0.060) < 1e-12 and abs(g["t_a"] - 0.040) < 1e-12 and abs(g["r_hull"] - 0.108) < 1e-9)
check("hull does not fit in 4 and 6 in pipe, fits from 8 in", (not T.hull_geometry(4)["feasible"]) and (not T.hull_geometry(6)["feasible"]) and T.hull_geometry(8)["feasible"])
w, mass = T.steam_wall_kg_per_m(12, 198.0, 25.0)
check("wall-heating steam equals m_steel c_p dT / h_fg (energy balance)", abs(w - mass * T.CP_S * (198.0 - 25.0) / V1.STEAM["hfg"]) < 1e-12)
check("12 in standard-wall pipe mass per metre is 73-75 kg", 72.0 < mass < 76.0, "%.1f kg/m" % mass)
# results consistency
check("baseline atmospheric 40 mm: probability within the original's 95 % interval", V1R["A_atmospheric"]["ci"][0] - 0.005 <= RESULTS["baseline_atm"]["P_safe"] <= V1R["A_atmospheric"]["ci"][1] + 0.005)
check("environment study: P(pack <= 55 C) falls monotonically with pipe temperature", all(RESULTS["env"]["rows"][i]["P_safe_atm"] >= RESULTS["env"]["rows"][i + 1]["P_safe_atm"] - 1e-9 for i in range(len(RESULTS["env"]["rows"]) - 1)))
m = RESULTS["verify"]["mesh"]
check("thermal mesh refinement converges (differences to the finest grid shrink monotonically, finest step 0.03 K or less)", abs(m[0]["diff_to_finest_K"]) > abs(m[1]["diff_to_finest_K"]) > abs(m[2]["diff_to_finest_K"]) and abs(m[0]["diff_to_finest_K"]) < 0.05)
cv = RESULTS["coverage"]["rows"]
check("coverage: no single 45 min deployment reaches 300 m in any sample (speed cap 0.1 m/s x 2,700 s = 270 m)", cv["45 min atmospheric|ablation|300"]["P_single"] == 0.0 and cv["45 min atmospheric|ablation|300"]["range_max_m"] <= 270.0 + 1e-9)
check("coverage: a 90 min mission is capped at 540 m", cv["90 min evacuated|ablation|1000"]["range_max_m"] <= 540.0 + 1e-9 and cv["90 min evacuated|ablation|1000"]["P_single"] == 0.0)

# ---- (v) revision studies (tamprc_v3.py)
nm = EXT["bench_stefan"]["neumann"]
check("enthalpy-method Stefan solver reproduces the exact Neumann front position within 0.1 %", abs(nm["rel_err"]) < 1e-3, "%.1e" % nm["rel_err"])
check("quasi-steady melt front overestimates the Neumann front at Stefan number 1.47 (the reason for the no-drainage bias)", 0.1 < nm["rel_err_quasi_steady"] < 0.3)
conv = EXT["bench_stefan"]["convective"]
check("ablation melt-time formula agrees with the resolved enthalpy solver within 5 % (h = 1-10 kW/m2 K, 3-12 mm)", max(abs(r["err_ablation"]) for r in conv) < 0.05, "max %.3f" % max(abs(r["err_ablation"]) for r in conv))
check("no-drainage formula is shorter than the solver by 18 +/- 2 % in every case (liquid sensible heat neglected)", all(abs(r["err_nodrain"] + 0.18) < 0.02 for r in conv))
ar = EXT["bench_stefan"]["ablation_resolution"]
check("ablation solution converges with cell size (2 um and 4 um agree within 1 %)", abs(ar[3]["t_ablation_numeric"] / ar[2]["t_ablation_numeric"] - 1) < 0.01)
bc = EXT["bench_conduction"]
check("conduction solver agrees with an independent stiff-ODE integration within 0.02 K (10 s backward Euler) and 0.002 K (0.625 s)", abs(bc["diff_10s_K"]) < 0.02 and abs(bc["diff_0p625s_K"]) < 0.002)
rat = EXT["hmodels"]["h_ratio_chato_to_nusselt"]
check("Chato coefficient is 0.74-0.77 of the Nusselt coefficient over 40-140 K", all(0.74 < v < 0.77 for v in rat.values()))
with X.use_h("chato"):
    swapped = V1.h_cond is not X._H_ORIG
check("use_h swaps the coefficient inside the context and restores it afterwards", swapped and V1.h_cond is X._H_ORIG)
pp = V1.sample_thermal(60, np.random.default_rng(2), 40.0, False)
Dm = T.deposit_v2(60, np.random.default_rng(9), pp["Tsat"], pp["h_mult"], np.full(60, 2700.0), s_ret=0.0)
d_fast = X.dynfilm(Dm, pp["Tsat"], pp["h_mult"], mu_factor=1e-9, dt=0.02)
check("dynamic film with vanishing viscosity (instant drainage) reproduces the ablation melt time within 1 %", float(np.max(np.abs(d_fast["t_melt"] / Dm["t_melt"] - 1))) < 0.01)
d_slow = X.dynfilm(Dm, pp["Tsat"], pp["h_mult"], mu_factor=1e6, dt=0.02)
check("dynamic film with no drainage is slower than ablation and close to the no-drainage limit (median ratio 0.8-1.2)", bool(np.all(d_slow["t_melt"] > Dm["t_melt"])) and 0.8 < float(np.median(d_slow["t_melt"] / Dm["t_melt_nodrain"])) < 1.2)
db = EXT["dynfilm"]["baseline"]
check("dynamic-film range lies between the instant-removal and the no-drainage ranges", EXT["hmodels"]["models"]["nusselt"]["range_median_m_s0"] > db["range_median_m"] > RESULTS["film"]["nodrain"]["range_nodrain_median_m"])
sf = EXT["dynfilm"]["steady_film_median_params"]
check("series-resistance identity: q/q0 = 1/(1 + Pi_f) at the steady film", abs(sf["flux_ratio"] - 1.0 / (1.0 + sf["Pi_f"])) < 1e-12)
check("median range falls to 100 m at Pi_f of about 0.34 (series-resistance model)", 0.25 < EXT["dynfilm"]["Pi_f_for_100m_median"] < 0.45)
check("IF97 saturation pressure: 1.5538 MPa at 200 C and 0.10142 MPa at 100 C (steam tables)", abs(float(X.psat_MPa(200.0)) - 1.5538) < 2e-3 and abs(float(X.psat_MPa(100.0)) - 0.10142) < 1e-4)
check("198 C corresponds to 1.49 MPa, not 1.55 MPa", abs(float(X.psat_MPa(198.0)) - 1.49) < 0.01)
r = X.sobol_indices(lambda Z: Z[:, 0] + 2 * Z[:, 1], [lambda u: u, lambda u: u], m=12, nboot=20)
check("Sobol estimator recovers the analytic indices of a linear test function (0.2, 0.8)", abs(r["S1"][0] - 0.2) < 0.02 and abs(r["S1"][1] - 0.8) < 0.02 and abs(r["ST"][1] - 0.8) < 0.02)
for k in ("pack_temperature_45min", "range_with_film", "steam_with_film"):
    check("Sobol first-order indices sum to about 1 (%s)" % k, 0.9 < sum(EXT["sobol"][k]["S1"]) < 1.1, "%.2f" % sum(EXT["sobol"][k]["S1"]))
check("Pareto mask removes a dominated point", list(X.pareto_mask(np.array([[1.0, 1.0], [2.0, 2.0], [0.5, 3.0]]))) == [True, False, True])
for m_ in EXT["design"]["by_melt"]:
    check("every Pareto design satisfies the constraints (%s)" % m_, all(d["fits"] and d["P_safe"] >= 0.95 for d in EXT["design"]["designs"] if d["melt"] == m_ and d.get("pareto")))
check("the dynamic film lowers the best feasible range below the instant-removal best", EXT["design"]["by_melt"]["dynamic film"]["best_feasible"]["range_median_m"] < EXT["design"]["by_melt"]["instant removal"]["best_feasible"]["range_median_m"])
pt = EXT["ptcompat"]
check("Class 150 steam-temperature limit lies below the model's 198 C", pt["Tmax_class150_C"] < 198.0, "%.0f C" % pt["Tmax_class150_C"])
check("uncapped range: the set-point cap binds exactly in the draws with v_th >= 0.10 m/s", abs(EXT["uncapped"]["P_range_at_cap"] - (1 - EXT["uncapped"]["P_thermally_limited"])) < 1e-12)
cr = EXT["corr"]["rows"]
check("positive correlation of starting temperature and heat generation lowers the thermal probability", cr[1]["P_safe"] < cr[0]["P_safe"] < cr[2]["P_safe"] + 1e-9)
print("\n%d checks passed" % N_OK)
