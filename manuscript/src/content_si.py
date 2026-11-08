# -*- coding: utf-8 -*-
"""Supplementary information."""
from common import *

NTEST = 62
adds(("title", "Supplementary Information"))
adds(("small", TITLE))
adds(("author", "Leon Sandler"))
adds(("small", "Independent Researcher, Northbrook, Illinois, USA. sandler.leon@gmail.com"))
adds(("blank",))
adds(("h1", "S1. Thermal sweep and Monte Carlo behavior (first suite)"))
SW = V["A_sweep"]
rows = []
for i, t in enumerate(SW["thickness_mm"]):
    rows.append([n(t), "%s (%s)" % (pc(SW["atmospheric"][i][0], 1), ci(SW["atmospheric"][i][1], SW["atmospheric"][i][2], 1)), pc(V["A_sweep90"]["atmospheric"][i], 0),
                 "%s (%s)" % (pc(SW["evacuated"][i][0], 1), ci(SW["evacuated"][i][1], SW["evacuated"][i][2], 1)), pc(V["A_sweep90"]["evacuated"][i], 0)])
adds(("table", "Table S1. P(pack ≤ 55 °C) against aerogel thickness, 45 min (Wilson 95% interval) and 90 min.", ["Aerogel (mm)", "Atmospheric, 45 min", "Atmospheric, 90 min", "Evacuated, 45 min", "Evacuated, 90 min"], rows, [0.8, 1.6, 0.9, 1.6, 0.9]))
adds(("fig", "SI_endurance_histogram.png", "Fig. S1. Time to reach 55 °C for atmospheric and evacuated aerogel, 40 mm (capped at 120 min).", 3.6))
adds(("fig", "SI_convergence.png", "Fig. S2. Convergence of the Monte Carlo estimate of P(pack ≤ 55 °C) with the number of draws (40 mm, atmospheric); band: Wilson 95% interval.", 3.8))
adds(("fig", "Fig3_sensitivity.png", "Fig. S3. Spearman rank correlation of each input with the 45 min pack temperature (first suite; global Sobol indices are in Fig. @F:sobol@ of the main text).", 4.2))

adds(("h1", "S2. Benchmarks: all cases"))
rows = [[n(r["h"]), n(r["thick_mm"]), n(r["t_ablation_formula"], 2), n(r["t_ablation_numeric"], 2), n(100 * r["err_ablation"], 1), n(r["t_nodrain_formula"], 1), n(r["t_nodrain_numeric"], 1), n(100 * r["err_nodrain"], 1)] for r in BSF["convective"]]
adds(("table", "Table S2. Melt time (s) from the formulas and from the enthalpy-method solver (equal properties in both phases, T0 = 25 °C, Tm = 58 °C, steam at 198 °C, no heat-coupling loss). Errors are formula minus solver, in percent of the solver.",
      ["h (W/m²·K)", "Thickness (mm)", "Ablation formula", "Ablation solver", "Error (%)", "No-drainage formula", "No-drainage solver", "Error (%)"], rows, [0.8, 0.8, 0.9, 0.9, 0.7, 1.0, 1.0, 0.7], 15))
rows = [[n(a["dx_um"], 0), n(a["t_ablation_numeric"], 3)] for a in BSF["ablation_resolution"]]
adds(("table", "Table S3. Ablation melt time of the enthalpy solver against cell size (h = 3 kW/m²·K, 6 mm).", ["Cell size (µm)", "Melt time (s)"], rows, [1.0, 1.0]))

adds(("h1", "S3. Global sensitivity: Sobol indices with 95% bootstrap intervals"))
for key, title in (("pack_temperature_45min", "pack temperature at 45 min"), ("range_with_film", "log10 range, retained film lognormal"), ("range_instant_removal", "log10 range, instant removal"), ("steam_with_film", "log10 melting steam per meter, retained film lognormal")):
    d = SOB[key]; rows = []
    for i, nm_ in enumerate(d["names"]):
        rows.append([nm_, "%s (%s to %s)" % (n(d["S1"][i], 2), n(d["S1_ci"][0][i], 2), n(d["S1_ci"][1][i], 2)), "%s (%s to %s)" % (n(d["ST"][i], 2), n(d["ST_ci"][0][i], 2), n(d["ST_ci"][1][i], 2))])
    adds(("table", "Table S4. Sobol indices of the %s (N = %s base samples)." % (title, n(d["N"])), ["Input", "First order", "Total"], rows, [1.6, 1.4, 1.4]))
adds(("h1", "S4. Correlated inputs"))
rows = [[n(r["rho_T0_Pgen"], 1), n(r["rho_thickness_meltpoint"], 1), "%s (%s)" % (pc(r["P_safe"], 1), ci(*r["P_safe_ci"], 1)), n(r["range_median_m"], 1), pc(r["P_ge_100"], 0)] for r in CORR]
adds(("table", "Table S5. Gaussian-copula correlation of starting temperature with heat generation and of deposit thickness with melt point (3,000 draws).", ["ρ (T0, P_gen)", "ρ (thickness, melt point)", "P(pack ≤ 55 °C) (95% interval)", "Median range (m)", "P(range ≥ 100 m)"], rows, [0.9, 1.1, 1.8, 0.9, 0.9]))

adds(("h1", "S5. Dynamic film and design search"))
rows = [["baseline", n(DY["baseline"]["range_median_m"], 1), n(DY["baseline"]["s_end_median_mm"], 2), pc(DY["baseline"]["P_ge_100"], 1)]]
for k, v in DY["sensitivity"].items():
    rows.append([k, n(v["range_median_m"], 1), n(v["s_end_median_mm"], 2), pc(v["P_ge_100"], 1)])
adds(("table", "Table S6. Dynamic film: sensitivity of the median range and of the final film to the drainage assumptions.", ["Case", "Median range (m)", "Median film (mm)", "P(range ≥ 100 m)"], rows, [1.6, 1.0, 1.0, 1.0]))
for mlab in ("instant removal", "dynamic film"):
    pts = sorted([d for d in DES["designs"] if d["melt"] == mlab and d.get("pareto")], key=lambda d: -d["range_median_m"])[:20]
    rows = [["evacuated" if d["vac"] else "atmospheric", n(d["t_a_mm"]), n(d["mission_min"]), n(d["v_set"], 2), n(d["hull_od_mm"]), pc(d["P_safe"], 1), n(d["range_median_m"], 1), n(d["steam_kg_per_m"], 2), n(d["energy_Wh"])] for d in pts]
    adds(("table", "Table S7. Pareto-optimal feasible designs for %s (up to 20, by range)." % mlab, ["Jacket", "Aerogel (mm)", "Mission (min)", "Setpoint (m/s)", "Hull OD (mm)", "P(≤ 55 °C)", "Range (m)", "Steam (kg/m)", "Energy (Wh)"], rows, [0.9, 0.7, 0.7, 0.7, 0.7, 0.8, 0.7, 0.7, 0.7], 15))
rows = [[str(k)] + [pc(v, 0) for v in row] for k, row in zip(ENVL["nps"], ENVL["P_safe"])]
adds(("table", "Table S8. Feasible envelope: P(pack ≤ 55 °C, 45 min) by nominal pipe size (rows) and pipe temperature (columns, °C), 400 draws per cell.", ["NPS (in)"] + [n(t) for t in ENVL["temps"]], rows, [0.7] + [0.6] * len(ENVL["temps"])))

adds(("h1", "S6. Pipe length and logistics (all cases)"))
rows = []
for m_ in ("45 min atmospheric", "90 min evacuated"):
    for c_ in R["coverage"]["cases"]:
        for L in R["coverage"]["lengths"]:
            d = COV["%s|%s|%g" % (m_, c_, L)]
            rows.append([m_, c_, n(L, 1 if L < 1 else 0), pc(d["P_single"], 0), n(d["n_dep_median"]), n(d["n_dep_p95"]), n(d["active_h_median"], 2), "%s (%s–%s)" % (n(d["total_h_median"], 1), n(d["total_h_p05"], 1), n(d["total_h_p95"], 1)), n(d["range_median_m"], 1)])
for m_ in ("45 min atmospheric", "90 min evacuated"):
    for L in R["coverage"]["lengths"]:
        d = CVD["%s|dynamic film|%g" % (m_, L)]
        rows.append([m_, "dynamic film", n(L, 1 if L < 1 else 0), pc(d["P_single"], 0), n(d["n_dep_median"]), n(d["n_dep_p95"]), n(d["active_h_median"], 2), "%s (%s–%s)" % (n(d["total_h_median"], 1), n(d["total_h_p05"], 1), n(d["total_h_p95"], 1)), n(d["range_median_m"], 1)])
adds(("table", "Table S9. Deployments, active time and total intervention time by mission, melt-removal case and pipe length (median; total with 5th–95th percentile).",
      ["Mission", "Melt removal", "L (m)", "P(one)", "Dep. median", "Dep. p95", "Active (h)", "Total (h)", "Range (m)"], rows, [1.2, 1.1, 0.5, 0.6, 0.6, 0.6, 0.7, 1.4, 0.7], 15))

adds(("h1", "S7. Pipe size and temperature (detail)"))
rows = []
for k in sorted(DIA):
    d = DIA[k]
    rows.append([str(k), n(d["ID"] * 1000, 1), n(d["r_hull"] * 2000, 0) if d["r_hull"] > 0.02 else "–", n(d["r_pack"] * 1000, 0), n(d["t_a"] * 1000, 0) if d["feasible"] else "does not fit",
                 "%s (%s)" % (pc(d["P_safe_atm"], 1), ci(*d["P_safe_atm_ci"], 1)) if d["P_safe_atm"] is not None else "–", "%s (%s)" % (pc(d["P_safe_vac"], 1), ci(*d["P_safe_vac_ci"], 1)) if d["P_safe_vac"] is not None else "–",
                 n(d["h_scale"], 2), n(d["steam_scale"], 2)])
adds(("table", "Table S10. Fit and thermal margin by nominal pipe size (800 draws; Wilson interval). h scale: condensation coefficient relative to 12 in; steam scale: melting steam per meter relative to 12 in.",
      ["NPS (in)", "Bore (mm)", "Hull OD (mm)", "Pack radius (mm)", "Aerogel (mm)", "P atm.", "P evac.", "h scale", "Steam scale"], rows, [0.6, 0.7, 0.7, 0.8, 0.8, 1.7, 1.7, 0.6, 0.7], 15))
rows = [[n(e["T_amb"]), "%s (%s)" % (pc(e["P_safe_atm"], 1), ci(*e["P_safe_atm_ci"], 1)), "%s (%s)" % (pc(e["P_safe_vac"], 1), ci(*e["P_safe_vac_ci"], 1)), n(e["Tp45_median_atm"], 1), n(e["t_melt_median_s"], 1), n(e["range_median_m"], 0)] for e in R["env"]["rows"]]
adds(("table", "Table S11. Pipe / fluid temperature (12 in design, 40 mm aerogel; 800 draws): probability, median pack temperature at 45 min (atmospheric), median melt time and range.",
      ["Temperature (°C)", "P atm. (95% interval)", "P evac. (95% interval)", "Median pack T at 45 min (°C)", "Melt time (s)", "Range (m)"], rows, [0.8, 1.8, 1.8, 1.0, 0.8, 0.7], 15))

adds(("h1", "S8. Bypass: peak speed by pocket volume"))
rows = []
for Vg, lst in BY["by_volume"].items():
    rows.append([n(float(Vg), 1)] + [pc(x["P_gt_1"], 0) for x in lst])
adds(("table", "Table S12. P(peak speed > 1 m/s) against bypass area (cm²; columns) for four gas-pocket volumes (rows, m³); other inputs sampled.", ["V_g (m³)"] + [n(a) for a in BY["areas_cm2"]], rows, [0.8] + [0.6] * len(BY["areas_cm2"]), 15))
rows = [[n(float(Vg_), 1)] + [n(vt_[a], 0) for a in ("20.0", "80.0", "320.0")] for Vg_, vt_ in BY["vent_time_median_ms"].items()]
adds(("table", "Table S13. Median time for a fully open bypass to halve the breakthrough differential (ms), tool held at rest, against pocket volume and bypass area.", ["V_g (m³)", "20 cm²", "80 cm²", "320 cm²"], rows, [0.8, 0.8, 0.8, 0.8]))
rows = [[n(h["Qs_m3_s"], 2), n(h["area_cm2"], 1)] for h in BY["hold_area_cm2"]]
adds(("table", "Table S14. Bypass flow area that holds a 0.5 bar differential at 18 bar upstream (assumed methane-like gas, C_d = 0.7) for a supply flow Q_s.", ["Q_s (m³/s at upstream conditions)", "Bypass area (cm²)"], rows, [1.6, 1.2]))

adds(("h1", "S9. Maintenance lattice (first suite)"))
adds(("fig", "Fig12_maintenance_lattice.png", "Fig. S4. Time-averaged fouled fraction against fouling per pass interval for three clearing probabilities: non-interacting case (left) and neighbor-nucleated fouling, γ = 3 (right).", 6.3))
adds(("p", "For $\\gamma=0$ the lattice Monte Carlo agrees with the exact solution within %s percentage points. Neighbor-nucleated fouling raises the fouled fraction substantially: for $x=0.8$ and $p=0.8$ it rises from %s to %s, so a cleaning interval that suffices "
           "for independent fouling may fail when deposits nucleate on existing deposits. The lattice is not calibrated to any deposit growth rate and is reported as a planning illustration only."
           % (n(100 * V["D"]["max_abs_err_gamma0"], 2), n(V["D"]["kmc_gamma0_avg"]["0.8"][4], 2), n(V["D"]["kmc_gamma3_avg"]["0.8"][4], 2))))
adds(("h1", "S10. Automated checks"))
adds(("p0", "tests/test_all.py runs %s checks. First suite: unchanged (sha256) and reproduces its published results; the maintenance-lattice formula. Extension: the extended thermal, melt and surge functions equal the first suite when the added "
            "mechanisms are off; monotonic range with retained film; the no-drainage limit; the series-resistance flux; the $D^{-1/4}$ scaling of the condensation coefficient; zero and choked orifice flow; gas-fraction bounds; monotonic bypass benefit; venting-time scaling; "
            "proportionality of the holding area to the supply flow; the 12 in hull; the fit in 4, 6 and 8 in pipes; the wall-heating energy balance; mesh convergence; the 270 m and 540 m caps. Revision: the enthalpy solver against the exact Neumann solution; "
            "the ablation formula and the no-drainage bias against the solver; convergence of the ablation solution; the conduction solver against an independent stiff-ODE integration; the Chato to Nusselt ratio; restoration of the swapped condensation coefficient; "
            "the dynamic film in its two limits; the series-resistance identity and the Π_f threshold; IF97 saturation pressures; the Sobol estimator on a function with known indices and the sums of the computed first-order indices; the Pareto mask; the constraints of the "
            "design search; the Class 150 limit; the speed-cap accounting; and the sign of the correlation effect." % n(NTEST)))
adds(("refs",))
