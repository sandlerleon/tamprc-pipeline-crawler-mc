# -*- coding: utf-8 -*-
"""Manuscript, part B: verification and results (Sections 5-6)."""
from common import *

SW = V["A_sweep"]; TH = SW["thickness_mm"]
MESH = R["verify"]["mesh"]
SP = {k: V["A_spearman_Tp45"][k] for k in V["A_spearman_Tp45"]}

# ============================================================================================ 5 Verification
add(("h1", "5. Verification"))
add(("p", fmt("The model is verified numerically; it is not validated physically, because no measurement exists for these inputs. Twenty-seven automated checks run on the committed code and results (tests/test_all.py). They confirm that the first suite is "
              "intact (the file is byte-identical to the one submitted, and rerunning it reproduces its published results to the last digit); that every added mechanism reduces to the first suite when switched off (the extended thermal, "
              "melt and surge functions equal the originals draw for draw, and the orifice model with zero area equals the controller-only crawler); and limiting and conservation properties of the added mechanisms: the series-resistance flux, the "
              "$D^{-1/4}$ scaling of the condensation coefficient, zero flow at zero differential and choking below the critical ratio, a gas fraction that stays between 0 and 1, venting times that scale with pocket volume, and the energy balance of "
              "the wall-heating steam. A deterministic nominal case refined from 20 to 160 cells and from 10 s to 1.25 s changes the pack temperature at 45 min from <<a>> °C to <<b>> °C, a difference of <<d>> K, and the differences to the finest grid "
              "fall monotonically (<<d0>>, <<d1>> and <<d2>> K). The exact mean-field solution of the maintenance lattice agrees with the lattice Monte Carlo within <<e>> percentage points for $\\gamma=0$.",
              a=n(MESH[0]["Tp45"], 2), b=n(MESH[3]["Tp45"], 2), d=n(abs(MESH[0]["diff_to_finest_K"]), 2), d0=n(abs(MESH[0]["diff_to_finest_K"]), 3), d1=n(abs(MESH[1]["diff_to_finest_K"]), 3), d2=n(abs(MESH[2]["diff_to_finest_K"]), 3),
              e=n(100 * V["D"]["max_abs_err_gamma0"], 2))))

# ============================================================================================ 6 Results
add(("h1", "6. Results"))
add(("h2", "6.1 Thermal shield"))
add(("fig", "Fig2_pack_temperature.png", "Fig. 2. Pack temperature against time for 40 mm of aerogel, atmospheric (left) and evacuated (right): median, 5–95% and 1–99% bands.", 6.3))
add(("p", fmt("At 45 min the pack median is <<ta>> °C (95th percentile <<tp>> °C) with atmospheric aerogel and <<tv>> °C (<<tvp>> °C) with the evacuated jacket (Fig. 2). The probability of staying at or below 55 °C is <<pa>> (95% interval <<ca>>) and <<pv>> (<<cv>>) "
              "respectively. The median time to reach 55 °C is <<ca1>> min (5th percentile <<ca2>> min) and <<cv1>> min (<<cv2>> min), and <<cen>> of the evacuated draws never reached it within the 120 min horizon. The first suite's 3,000 draws and the "
              "re-drawn 3,000 of the extended suite agree (<<pa2>> against <<pa>>).",
              ta=n(A_ATM["Tp45_median"], 1), tp=n(A_ATM["Tp45_p95"], 1), tv=n(A_VAC["Tp45_median"], 1), tvp=n(A_VAC["Tp45_p95"], 1), pa=pc(A_ATM["P_safe"], 1), ca=ci(*A_ATM["ci"]), pv=pc(A_VAC["P_safe"], 1), cv=ci(*A_VAC["ci"]),
              ca1=n(A_ATM["t_crit_median_min"]), ca2=n(A_ATM["t_crit_p05_min"]), cv1=n(A_VAC["t_crit_median_min"]), cv2=n(A_VAC["t_crit_p05_min"]), cen=pc(A_VAC["frac_censored_120min"], 0), pa2=pc(R["baseline_atm"]["P_safe"], 1))))
add(("fig", "Fig3_sensitivity.png", "Fig. 3. Sensitivity of the 45 min pack temperature (atmospheric case): Spearman rank correlation with each input.", 4.2))
add(("p", fmt("Initial temperature ($\\rho$ = <<r1>>) and internal heat generation (<<r2>>) dominate; pack mass is next (<<r3>>), and aerogel conductivity (<<r4>>), bridge fraction (<<r5>>) and thickness (<<r6>>) are weaker at the 40 mm design point, because "
              "the diffusion time of aerogel across 40 mm is of the order of hours, so the wall has not reached steady state within the mission (Fig. 3). The thermal margin therefore belongs to the thermal mass of the pack and to the starting temperature, "
              "not to the insulation alone.", r1=n(SP["Initial temperature"], 2), r2=n(SP["Internal heat generation"], 2), r3=n(SP["Pack mass"], 2), r4=n(SP["Aerogel k multiplier"], 2), r5=n(SP["Thermal-bridge fraction"], 2), r6=n(SP["Aerogel thickness"], 2))))
add(("fig", "Fig4_design_sweep.png", "Fig. 4. Probability of meeting the 55 °C limit against aerogel thickness (solid: 45 min; dotted: 90 min).", 3.9))
add(("p", fmt("A 95% reliability target at 45 min requires roughly 30 mm of atmospheric aerogel (<<a30>>) or 15 mm of evacuated aerogel (<<v15>>) (Fig. 4). The evacuated curve plateaus near 99% because of the assumed 5% vacuum-loss probability and the tails of "
              "initial temperature and heat generation. For a 90 min mission the probability at 40 mm falls to <<a90>> (atmospheric) and <<v90>> (evacuated).",
              a30=pc(SW["atmospheric"][4][0], 1), v15=pc(SW["evacuated"][2][0], 1), a90=pc(V["A_sweep90"]["atmospheric"][5], 0), v90=pc(V["A_sweep90"]["evacuated"][5], 0))))

add(("h2", "6.2 Melt kinetics and range, with instant removal of the melt"))
add(("p", fmt("With the first suite's assumption that molten deposit leaves the surface at once, the median condensation coefficient is <<h>> kW/m²·K and the film flux <<q>> kW/m². The melt time of a deposit has a median of <<tm>> s (95th percentile <<tm95>> s). "
              "The thermally limited speed has a median of <<v>> cm/s (5th percentile <<v5>> cm/s) and is below the 10 cm/s set-point in <<fl>> of the draws. Deposit thickness is its strongest driver ($\\rho$ = <<rd>>), followed by the heat-coupling "
              "fraction (<<re>>) and the contact length (<<rl>>). The median cleaned range per 45 min deployment is <<rg>> m (5th to 95th percentile <<r5>> to <<r95>> m; the upper value is the set-point cap of 0.1 m/s × 2,700 s). "
              "The probability of a range of at least 100, 200 and 250 m is <<p1>>, <<p2>> and <<p3>>. The median steam use is <<s>> kg per metre (95th percentile <<s95>> kg/m), about <<c>> m³ of condensate per 100 m (Fig. 5).",
              h=n(BB["h_cond_median"] / 1e3, 1), q=n(BB["q_raw_median_kWm2"]), tm=n(BB["t_melt_median_s"], 1), tm95=n(BB["t_melt_p95_s"]), v=n(BB["v_th_median_cms"], 1), v5=n(BB["v_th_p05_cms"], 1), fl=pc(BB["frac_thermally_limited"], 0),
              rd=n(V["B_spearman_vth"]["delta"], 2), re=n(V["B_spearman_vth"]["eta"], 2), rl=n(V["B_spearman_vth"]["Lz"], 2), rg=n(BB["range_median_m"]), r5=n(BB["range_p05_m"]), r95=n(BB["range_p95_m"]), p1=pc(BB["P_range_ge_100"], 0),
              p2=pc(BB["P_range_ge_200"], 0), p3=pc(BB["P_range_ge_250"], 0), s=n(BB["steam_kg_per_m_median"], 2), s95=n(BB["steam_kg_per_m_p95"], 1), c=n(BB["condensate_m3_per_100m_median"], 2))))
add(("fig", "Fig5_condensation_range.png", "Fig. 5. Condensation coefficient against temperature difference, melt-time distribution and exceedance of the cleaned range per deployment (instant removal of the melt).", 6.3))

add(("h2", "6.3 The retained melt film decides the range"))
rows = []
for s_ in (0.0, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0):
    r = FR[s_]
    rows.append([n(s_, 2) if s_ else "0 (ablation)", n(r["v_th_median_cms"], 2 if r["v_th_median_cms"] < 1 else 1), n(r["range_median_m"], 1 if r["range_median_m"] < 100 else 0), "%s to %s" % (n(r["range_p05_m"], 0 if r["range_p05_m"] > 10 else 1), n(r["range_p95_m"])),
                 pc(r["P_ge_100"], 0), pc(r["frac_thermally_limited"], 0)])
rows.append(["no drainage (limit)", n(ND["v_nodrain_median_cms"], 2), n(ND["range_nodrain_median_m"], 1), "–", pc(ND["P_ge_100"], 0), "100%"])
add(("p", fmt("The first suite's melt model is the optimistic bound of a family. Molten paraffin that stays on the surface adds the resistance $s/k_{l}$ to the condensate film $1/h$ (Eq. 3), and since $k_{l}/h$ = <<kh>> mm, a retained layer thicker than about "
              "<<kh2>> µm already halves the heat flux. Table 3 and Fig. 6 give the range against the retained thickness for the same draws. The median range falls to <<r005>> m at 0.05 mm, <<r02>> m at 0.2 mm and <<r1>> m at 1 mm; the "
              "median range drops below 100 m at a retained film of only <<sx>> µm. If none of the melt drains (Eq. 4), the median melt time is <<tnd>> s instead of <<tab>> s, a factor <<ratio>>, and the median range is <<rnd>> m. The "
              "heat-coupling fraction $\\eta$ is applied on top of the film, so these ranges include the first suite's unexplained heat loss as well; they are not a calibrated prediction. They show that whether the melt leaves the surface "
              "is the single most influential unmeasured assumption of the concept: the reported 138 m is its upper end and not an expected value.",
              kh=n(F["k_liq"] / BB["h_cond_median"] * 1e3, 3), kh2=n(F["k_liq"] / BB["h_cond_median"] * 1e6), r005=n(FR[0.05]["range_median_m"]), r02=n(FR[0.2]["range_median_m"]), r1=n(FR[1.0]["range_median_m"], 1), sx=n(F["s_median_below_100m_mm"] * 1000),
              tnd=n(ND["t_melt_nodrain_median_s"]), tab=n(ND["t_melt_ablation_median_s"], 1), ratio=n(ND["ratio_median"]), rnd=n(ND["range_nodrain_median_m"], 1))))
add(("table", "Table 3. Median speed and cleaned range per 45 min deployment against the retained melt film s (atmospheric aerogel, 40 mm; same draws in every row).",
     ["s (mm)", "Median v_th (cm/s)", "Median range (m)", "5th to 95th percentile (m)", "P(range ≥ 100 m)", "Thermally limited"], rows, [1.3, 1.1, 1.1, 1.4, 1.1, 1.1]))
add(("fig", "Fig6_film.png", "Fig. 6. (a) Cleaned range per 45 min deployment against the retained melt film (median and 5–95% band; dashed: no-drainage limit; dotted: 1 km). (b) Exceedance of the range for three film thicknesses.", 6.3))

add(("h2", "6.4 Pipe length, deployments and intervention time"))
def cv(m, c, L):
    return COV["%s|%s|%g" % (m, c, L)]
rows4 = []
for m_, lab in (("45 min atmospheric", "45 min, atmospheric"), ("90 min evacuated", "90 min, evacuated")):
    for c_, cl in (("ablation", "instant removal"), ("retained 0.5 mm", "0.5 mm film")):
        for L in (100.0, 300.0, 1000.0):
            d = cv(m_, c_, L)
            rows4.append([lab, cl, n(L), pc(d["P_single"], 0), "%s (%s)" % (n(d["n_dep_median"]), n(d["n_dep_p95"])), n(d["active_h_median"], 1), n(d["total_h_median"]), pc(d["active_fraction_median"], 0)])
c3 = cv("45 min atmospheric", "ablation", 300.0); c10 = cv("45 min atmospheric", "ablation", 1000.0); e3 = cv("90 min evacuated", "ablation", 300.0); e10 = cv("90 min evacuated", "ablation", 1000.0)
add(("p", fmt("The brief names pipes from about 0.3 m to 1 km. Under the assumed set-point of 0.10 m/s, a 45 min deployment cannot exceed 270 m in any draw, so no draw cleans a 300 m line in one deployment, even with instant removal of the melt (Table 4, Fig. 7). "
              "A 1 km line needs a median of <<n1>> deployments (95th percentile <<n1p>>) with instant removal, <<n2>> with a 0.5 mm retained film and <<n3>> if no melt drains. A 90 min evacuated mission raises the cap to 540 m and the one-deployment probability "
              "for 300 m to <<pe>>, but still does not reach 1 km. With the assumed logistics durations (Table 2) the total intervention time for 1 km has a median of <<t1>> h, of which only <<a1>> h (<<f1>>) is active cleaning; "
              "for 100 m it is <<t0>> h. Because the logistics durations are assumed, the absolute hours matter less than the ratio: most of the intervention is not cleaning. Moreover, every extra deployment requires "
              "that the tool is recovered through the same flow-aligned connection by which it entered, which the brief states as the only access; the model does not include recovery or the passage of the tool through bends, valves and diameter changes.",
              n1=n(c10["n_dep_median"]), n1p=n(c10["n_dep_p95"]), n2=n(cv("45 min atmospheric", "retained 0.5 mm", 1000.0)["n_dep_median"]), n3=n(cv("45 min atmospheric", "no drainage", 1000.0)["n_dep_median"]), pe=pc(e3["P_single"], 0),
              t1=n(c10["total_h_median"]), a1=n(c10["active_h_median"], 1), f1=pc(c10["active_fraction_median"], 0), t0=n(cv("45 min atmospheric", "ablation", 100.0)["total_h_median"]))))
add(("table", "Table 4. Deployments and time to clean a line of length L (median; 95th percentile of the deployment count in parentheses). Durations of the non-cleaning stages are assumed (Table 2).",
     ["Mission", "Melt removal", "L (m)", "P(one deployment)", "Deployments", "Active (h)", "Total (h)", "Active share"], rows4, [1.3, 1.1, 0.6, 1.0, 1.1, 0.8, 0.8, 0.8]))
add(("fig", "Fig7_coverage.png", "Fig. 7. (a) Probability that one deployment cleans a line against its length for three melt-removal cases (solid: 45 min atmospheric; dotted: 90 min evacuated). (b) Median active cleaning time (dark) and total intervention time (light), 45 min atmospheric.", 6.3))

add(("h2", "6.5 Pipe size and pipe temperature"))
d4, d6, d8, d10, d12 = DIA[4], DIA[6], DIA[8], DIA[10], DIA[12]
rows5 = []
for k in (4, 6, 8, 10, 12, 16):
    d = DIA[k]
    rows5.append([str(k), n(d["ID"] * 1000), "%s" % n(2 * d["r_hull"] * 1000) if d["r_hull"] > 0.02 else "–", n(d["t_a"] * 1000) if d["feasible"] else "does not fit", n(d["m_pack_nom"], 1) if d["feasible"] else "–",
                 pc(d["P_safe_atm"], 0) if d["P_safe_atm"] is not None else "–", pc(d["P_safe_vac"], 0) if d["P_safe_vac"] is not None else "–", n(d["force_3bar_kN"], 1), n(d["brake_ratio_3bar"], 1)])
add(("p", fmt("The brief covers 4 to 16 inches; the first design was sized for 12 in. Keeping the radial clearance of the first design (44 mm), the hull does not fit in a 4 or 6 in pipe, even with the aerogel removed down to a 25 mm pack. In an 8 in pipe the aerogel "
              "shrinks to <<ta8>> mm and the pack to <<m8>> kg, and the probability of keeping the pack at or below 55 °C for 45 min is <<p8>> (<<v8>> evacuated); in a 10 in pipe it is <<p10>> (<<v10>> evacuated); from 12 in upward it is <<p12>> (Table 5, Fig. 8). "
              "The thermal margin therefore scales with the thermal mass of the pack, and the architecture as modelled covers about the upper third of the brief's diameter range. The surge force of a 3 bar break-through grows with the "
              "bore, from <<f8>> kN (8 in) to <<f16>> kN (16 in), against the same 2.5 kN of braking authority.",
              ta8=n(d8["t_a"] * 1000), m8=n(d8["m_pack_nom"], 1), p8=pc(d8["P_safe_atm"], 0), v8=pc(d8["P_safe_vac"], 0), p10=pc(d10["P_safe_atm"], 0), v10=pc(d10["P_safe_vac"], 0), p12=pc(d12["P_safe_atm"], 0), f8=n(d8["force_3bar_kN"]), f16=n(DIA[16]["force_3bar_kN"]))))
add(("table", "Table 5. Fit and thermal margin against nominal pipe size (standard wall; 45 min; 40 mm aerogel where it fits).",
     ["NPS (in)", "Bore (mm)", "Hull OD fitted (mm)", "Aerogel (mm)", "Pack (kg)", "P(≤ 55 °C) atm.", "P(≤ 55 °C) evac.", "Force at 3 bar (kN)", "Force / braking"], rows5, [0.6, 0.7, 1.0, 0.9, 0.7, 0.9, 0.9, 1.0, 0.9]))
e25, e35, e45, e55 = ENV[25.0], ENV[35.0], ENV[45.0], ENV[55.0]
add(("p", fmt("The pack starts at the pipe temperature, which is the dominant input (Section 6.1). Shifting the initial pack and pipe temperature with the same draws, the probability for the 12 in design falls from <<p25>> at 25 °C to <<p35>> at 35 °C, <<p45>> at 45 °C and "
              "<<p55>> at 55 °C (atmospheric; evacuated <<v25>>, <<v35>>, <<v45>> and <<v55>>), while the median range changes little (<<r25>> m at 25 °C, <<r45>> m at 45 °C) until the pack limit is reached early. A line that still carries warm produced fluid, for example at 40 to 60 °C, "
              "must therefore be cooled and flushed before the tool enters, which is a preparation step that the intervention time of Table 4 only partly includes.",
              p25=pc(e25["P_safe_atm"], 0), p35=pc(e35["P_safe_atm"], 0), p45=pc(e45["P_safe_atm"], 0), p55=pc(e55["P_safe_atm"], 0), v25=pc(e25["P_safe_vac"], 0), v35=pc(e35["P_safe_vac"], 0), v45=pc(e45["P_safe_vac"], 0), v55=pc(e55["P_safe_vac"], 0),
              r25=n(e25["range_median_m"]), r45=n(e45["range_median_m"]))))
add(("fig", "Fig8_diameter_temperature.png", "Fig. 8. (a) Probability of keeping the pack at or below 55 °C for 45 min against nominal pipe size (crosses: the hull does not fit). (b) Fitted hull diameter, pipe bore and the first design's hull. (c) The same probability against pipe temperature, 12 in design.", 6.5))

add(("h2", "6.6 Surge on blockage release"))
add(("fig", "Fig9_anti_dieseling.png", "Fig. 9. Speed transient for a nominal 3 bar break-through (left) and Monte Carlo exceedance of the peak speed (right), first suite.", 6.3))
OM = BY["original_model"]; G0 = BY["general"][0]; G7 = BY["general"][-1]
rows6 = [["Passive pig", n(CP["vpk_median"], 2), pc(CP["P_vpk_gt_1"], 0), pc(CP["P_vpk_gt_2"], 0), "first suite"],
         ["Crawler, braking only", n(CR["vpk_median"], 2), pc(CR["P_vpk_gt_1"], 0), pc(CR["P_vpk_gt_2"], 0), "first suite"],
         ["Crawler + relief as force factor β", n(CL["vpk_median"], 2), pc(CL["P_vpk_gt_1"], 0), pc(CL["P_vpk_gt_2"], 0), "first suite"]]
for g in BY["general"][2:]:
    rows6.append(["Crawler + orifice bypass %s cm²" % n(g["Ab_cm2"]), n(g["vpk_median"], 2), pc(g["P_gt_1"], 0), pc(g["P_gt_2"], 0), "this paper"])
vt = BY["vent_time_median_ms"]
add(("p", fmt("In the first suite the pressure force of a 3 bar break-through on a 12 in bore, $A\\,\\Delta P$ ≈ 21 kN, exceeds the 2.5 kN braking authority by about a factor of nine, so braking alone changes the median peak speed only from <<p0>> to <<p1>> m/s "
              "(Table 6, Fig. 9). Treating the bypass relief as a force factor $\\beta$, the median peak falls to <<p2>> m/s. Venting the gas pocket through an orifice (Eq. 6) gives a smaller benefit: with 80 cm² of bypass area, 11% of the bore, the median "
              "peak is <<o80>> m/s, and even with 320 cm², 45% of the bore, it is <<o320>> m/s with <<o2>> of the releases above 2 m/s, against <<f2>> in the force-factor model. The reason is a mismatch of time scales. The tool reaches 1 m/s in "
              "<<ta>> ms (5th percentile <<ta5>> ms), whereas a fully open bypass of 80 cm² needs <<v1>> ms to halve the differential across a 1 m³ pocket (<<v03>> ms for 0.3 m³, <<v10>> ms for 10 m³), and a 20 ms valve lag is added to that. The relief therefore "
              "limits the duration of the surge, bringing the speed back to the set-point within about 0.3 s for 80 cm² (Fig. 10b), but not its first peak. A bypass that is closed until the differential reaches the break-through value cannot arrest the "
              "impulse. The design alternative is a bypass that is already open during the stall, so that the pocket never charges: it holds a differential of 0.5 bar at 18 bar upstream if its area passes the supply flow, which requires <<h1>> cm² for 0.03 m³/s, <<h2>> cm² for 0.1 m³/s and "
              "<<h3>> cm² for 0.3 m³/s (assumed methane-like gas; Fig. 10a). The price is that the differential that melts or breaks the deposit is then limited as well, so the deposit must be freed thermally rather than by pressure.",
              p0=n(CP["vpk_median"], 1), p1=n(CR["vpk_median"], 1), p2=n(CL["vpk_median"], 1), o80=n([g for g in BY["general"] if g["Ab_cm2"] == 80.0][0]["vpk_median"], 1), o320=n(G7["vpk_median"], 1), o2=pc(G7["P_gt_2"], 0), f2=pc(CL["P_vpk_gt_2"], 0),
              ta=n(BY["t_accel_1ms_median_ms"]), ta5=n(BY["t_accel_1ms_p05_ms"]), v1=n(vt["1.0"]["80.0"]), v03=n(vt["0.3"]["80.0"]), v10=n(vt["10.0"]["80.0"]), h1=n(BY["hold_area_cm2"][1]["area_cm2"]), h2=n(BY["hold_area_cm2"][2]["area_cm2"]), h3=n(BY["hold_area_cm2"][3]["area_cm2"]))))
add(("table", "Table 6. Peak speed after break-through (12 in bore; same draws; N = %s)." % n(R["N_surge"]), ["Configuration", "Median peak (m/s)", "P(> 1 m/s)", "P(> 2 m/s)", "Model"], rows6, [2.2, 1.1, 1.0, 1.0, 1.0]))
add(("fig", "Fig10_bypass.png", "Fig. 10. (a) Probability of a peak speed above 1 m/s against the bypass area for four gas-pocket volumes (dotted: the first suite's force-factor model). (b) Speed after a nominal 3 bar break-through with a 1 m³ pocket.", 6.3))

add(("h2", "6.7 Steam budget"))
S12 = STM[12]; S4 = STM[4]; S16 = STM[16]
rows7 = [[str(k), n(STM[k]["steel_kg_per_m"]), n(STM[k]["clean_kg_per_m"], 2), n(STM[k]["wall_kg_per_m_25C"], 2), n(STM[k]["total_kg_per_m_25C"], 2), n(STM[k]["wall_kg_per_m_0C"], 2)] for k in (4, 6, 8, 10, 12, 14, 16)]
add(("p", fmt("Melting the deposit uses a median of <<c>> kg of steam per metre in a 12 in pipe (first suite). If the steam reaches the tool through the pipe behind it, the steel wall of the whole line must also be heated from 25 °C to the saturation temperature: for standard-wall "
              "12 in pipe of <<m>> kg/m this takes <<w>> kg of steam per metre, <<ratio>> times the melting steam, and the total is <<t>> kg/m, or about <<t>> t of steam (and of condensate) for a 1 km line, against the <<c1>> t that the melting alone would suggest (Table 7, Fig. 11). "
              "A pipe at 0 °C needs <<w0>> kg/m for the wall. The wall-heating term is a lower bound, because it ignores heat lost from the pipe to its surroundings during the intervention. A steam hose carried inside the pipe avoids heating the wall but adds "
              "tether drag over up to 1 km and a second 200 °C line to the tool. Either way the water use is larger than the melting alone suggests, which matters because reduced water use is one of the brief's nice-to-have criteria.",
              c=n(S12["clean_kg_per_m"], 2), m=n(S12["steel_kg_per_m"]), w=n(S12["wall_kg_per_m_25C"], 1), ratio=n(S12["wall_ratio"], 1), t=n(S12["total_kg_per_m_25C"], 1), c1=n(S12["clean_kg_per_m"], 1), w0=n(S12["wall_kg_per_m_0C"], 1))))
add(("table", "Table 7. Steam per metre of line: melting (median) and heating the pipe wall (standard wall, 25 °C start; last column 0 °C start).",
     ["NPS (in)", "Steel (kg/m)", "Melting (kg/m)", "Wall heating (kg/m)", "Total (kg/m)", "Wall heating from 0 °C (kg/m)"], rows7, [0.7, 0.9, 1.0, 1.1, 0.9, 1.3]))
add(("fig", "Fig11_steam_budget.png", "Fig. 11. Steam per metre of line against nominal pipe size: melting the deposit and heating the pipe wall.", 4.4))

add(("h2", "6.8 Maintenance lattice"))
D = V["D"]
add(("fig", "Fig12_maintenance_lattice.png", "Fig. 12. Time-averaged fouled fraction against fouling per pass interval for three clearing probabilities: non-interacting case (left) and neighbor-nucleated fouling, γ = 3 (right).", 6.3))
add(("p", fmt("For $\\gamma=0$ the lattice Monte Carlo agrees with the exact solution within <<e>> percentage points. Neighbor-nucleated fouling raises the fouled fraction substantially: for $x=0.8$ and $p=0.8$ it rises from <<a>> to <<b>>, so a cleaning interval that suffices "
              "for independent fouling may fail when deposits nucleate on existing deposits (Fig. 12). The lattice is not calibrated to any deposit growth rate and is reported as a planning illustration only.",
              e=n(100 * D["max_abs_err_gamma0"], 2), a=n(D["kmc_gamma0_avg"]["0.8"][4], 2), b=n(D["kmc_gamma3_avg"]["0.8"][4], 2))))
