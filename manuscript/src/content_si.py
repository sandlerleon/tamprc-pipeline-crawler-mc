# -*- coding: utf-8 -*-
"""Supplementary information."""
from common import *

adds(("title", "Supplementary Information"))
adds(("small", TITLE))
adds(("author", "Leon Sandler"))
adds(("small", "Independent Researcher, Northbrook, Illinois, USA. sandler.leon@gmail.com"))
adds(("blank",))
adds(("h1", "S1. Thermal sweep (first suite, 3,000 draws per case; 800 per thickness)"))
SW = V["A_sweep"]
rows = []
for i, t in enumerate(SW["thickness_mm"]):
    rows.append([n(t), "%s (%s)" % (pc(SW["atmospheric"][i][0], 1), ci(SW["atmospheric"][i][1], SW["atmospheric"][i][2], 1)), pc(V["A_sweep90"]["atmospheric"][i], 0),
                 "%s (%s)" % (pc(SW["evacuated"][i][0], 1), ci(SW["evacuated"][i][1], SW["evacuated"][i][2], 1)), pc(V["A_sweep90"]["evacuated"][i], 0)])
adds(("table", "Table S1. P(pack ≤ 55 °C) against aerogel thickness, 45 min (Wilson 95% interval) and 90 min.", ["Aerogel (mm)", "Atmospheric, 45 min", "Atmospheric, 90 min", "Evacuated, 45 min", "Evacuated, 90 min"], rows, [0.8, 1.6, 0.9, 1.6, 0.9]))
adds(("fig", "SI_endurance_histogram.png", "Fig. S1. Time to reach 55 °C for atmospheric and evacuated aerogel, 40 mm (capped at 120 min).", 3.6))
adds(("fig", "SI_convergence.png", "Fig. S2. Convergence of the Monte Carlo estimate of P(pack ≤ 55 °C) with the number of draws (40 mm, atmospheric); band: Wilson 95% interval.", 3.8))

adds(("h1", "S2. Pipe length and logistics (all cases)"))
rows = []
for m_ in ("45 min atmospheric", "90 min evacuated"):
    for c_ in R["coverage"]["cases"]:
        for L in R["coverage"]["lengths"]:
            d = COV["%s|%s|%g" % (m_, c_, L)]
            rows.append([m_, c_, n(L, 1 if L < 1 else 0), pc(d["P_single"], 0), n(d["n_dep_median"]), n(d["n_dep_p95"]), n(d["active_h_median"], 2), "%s (%s–%s)" % (n(d["total_h_median"], 1), n(d["total_h_p05"], 1), n(d["total_h_p95"], 1)), n(d["range_median_m"], 1)])
adds(("table", "Table S2. Deployments, active time and total intervention time by mission, melt-removal case and pipe length (median; total with 5th–95th percentile).",
      ["Mission", "Melt removal", "L (m)", "P(one)", "Dep. median", "Dep. p95", "Active (h)", "Total (h)", "Range (m)"], rows, [1.2, 1.1, 0.5, 0.6, 0.6, 0.6, 0.7, 1.4, 0.7], 15))

adds(("h1", "S3. Pipe size and temperature (detail)"))
rows = []
for k in sorted(DIA):
    d = DIA[k]
    rows.append([str(k), n(d["ID"] * 1000, 1), n(d["r_hull"] * 2000, 0) if d["r_hull"] > 0.02 else "–", n(d["r_pack"] * 1000, 0), n(d["t_a"] * 1000, 0) if d["feasible"] else "does not fit",
                 "%s (%s)" % (pc(d["P_safe_atm"], 1), ci(*d["P_safe_atm_ci"], 1)) if d["P_safe_atm"] is not None else "–", "%s (%s)" % (pc(d["P_safe_vac"], 1), ci(*d["P_safe_vac_ci"], 1)) if d["P_safe_vac"] is not None else "–",
                 n(d["h_scale"], 2), n(d["steam_scale"], 2)])
adds(("table", "Table S3. Fit and thermal margin by nominal pipe size (800 draws; Wilson interval). h scale: condensation coefficient relative to 12 in; steam scale: melting steam per metre relative to 12 in.",
      ["NPS (in)", "Bore (mm)", "Hull OD (mm)", "Pack radius (mm)", "Aerogel (mm)", "P atm.", "P evac.", "h scale", "Steam scale"], rows, [0.6, 0.7, 0.7, 0.8, 0.8, 1.7, 1.7, 0.6, 0.7], 15))
rows = [[n(e["T_amb"]), "%s (%s)" % (pc(e["P_safe_atm"], 1), ci(*e["P_safe_atm_ci"], 1)), "%s (%s)" % (pc(e["P_safe_vac"], 1), ci(*e["P_safe_vac_ci"], 1)), n(e["Tp45_median_atm"], 1), n(e["t_melt_median_s"], 1), n(e["range_median_m"], 0)] for e in R["env"]["rows"]]
adds(("table", "Table S4. Pipe / fluid temperature (12 in design, 40 mm aerogel; 800 draws): probability, median pack temperature at 45 min (atmospheric), median melt time and range.",
      ["Temperature (°C)", "P atm. (95% interval)", "P evac. (95% interval)", "Median pack T at 45 min (°C)", "Melt time (s)", "Range (m)"], rows, [0.8, 1.8, 1.8, 1.0, 0.8, 0.7], 15))

adds(("h1", "S4. Bypass: peak speed by pocket volume"))
rows = []
for Vg, lst in BY["by_volume"].items():
    rows.append([n(float(Vg), 1)] + [pc(x["P_gt_1"], 0) for x in lst])
adds(("table", "Table S5. P(peak speed > 1 m/s) against bypass area (cm²; columns) for four gas-pocket volumes (rows, m³); other inputs sampled.", ["V_g (m³)"] + [n(a) for a in BY["areas_cm2"]], rows, [0.8] + [0.6] * len(BY["areas_cm2"]), 15))
rows = [[n(float(Vg_), 1)] + [n(vt_[a], 0) for a in ("20.0", "80.0", "320.0")] for Vg_, vt_ in BY["vent_time_median_ms"].items()]
adds(("table", "Table S6. Median time for a fully open bypass to halve the break-through differential (ms), tool held at rest, against pocket volume and bypass area.", ["V_g (m³)", "20 cm²", "80 cm²", "320 cm²"], rows, [0.8, 0.8, 0.8, 0.8]))
rows = [[n(h["Qs_m3_s"], 2), n(h["area_cm2"], 1)] for h in BY["hold_area_cm2"]]
adds(("table", "Table S7. Bypass flow area that holds a 0.5 bar differential at 18 bar upstream (assumed methane-like gas, C_d = 0.7) for a supply flow Q_s.", ["Q_s (m³/s at upstream conditions)", "Bypass area (cm²)"], rows, [1.6, 1.2]))

adds(("h1", "S5. Automated checks"))
adds(("p0", "tests/test_all.py runs 27 checks: the first suite is unchanged (sha256) and reproduces its published results; the maintenance-lattice formula; the extended thermal, melt and surge functions equal the first suite when the added "
            "mechanisms are off (pack temperature histories, speed, range, steam per metre and melt time, peak speeds for the passive and controller-only crawlers, and the zero-area orifice); monotonic range with retained film; the no-drainage limit; the series-resistance "
            "flux; the $D^{-1/4}$ scaling of the condensation coefficient; zero and choked orifice flow; the gas fraction bounds; monotonic bypass benefit; venting-time scaling with volume; proportionality of the holding area to the supply flow; the 12 in hull; "
            "the fit in 4, 6 and 8 in pipes; the wall-heating energy balance; the standard-wall pipe mass; the baseline probability against the first suite's interval; monotonic temperature dependence; mesh convergence; and the 270 m and 540 m "
            "range caps implied by the speed set-point."))
adds(("refs",))
