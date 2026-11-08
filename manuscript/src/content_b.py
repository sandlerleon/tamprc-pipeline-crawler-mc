# -*- coding: utf-8 -*-
"""Manuscript, part B: verification, benchmarks and results (Sections 5-6)."""
import math
from common import *

SW = V["A_sweep"]
MESH = R["verify"]["mesh"]
NTEST = 62
NM = BSF["neumann"]; CV_ = BSF["convective"]
ERR_A = [abs(r["err_ablation"]) for r in CV_]; ERR_N = [r["err_nodrain"] for r in CV_]
RV = PT["revised_envelope"]
RVO, RVN = RV["original 198 C"], RV["revised, Class 150 limit"]

# ============================================================================================ 5 Verification, benchmarks, applicability
add(("h1", "5. Verification, benchmarks and applicability"))
add(("h2", "5.1 Code verification"))
add(("p", fmt("<<nt>> automated checks run on the committed code and results (tests/test_all.py). They confirm that the first suite is intact (the file is byte-identical to the one submitted, and rerunning it reproduces its published results to the last digit); "
              "that every added mechanism reduces to the first suite when switched off (the extended thermal, melt and surge functions equal the originals draw for draw, and the orifice model with zero area equals the controller-only crawler; the dynamic film with instant "
              "drainage reproduces the ablation melt time); and the limiting and conservation properties of the added mechanisms. A deterministic nominal case refined from 20 to 160 cells and from 10 s to 1.25 s changes the pack temperature at 45 min from <<a>> °C to <<b>> °C, "
              "a difference of <<d>> K, and the differences to the finest grid fall monotonically. The exact mean-field solution of the maintenance lattice agrees with the lattice Monte Carlo within <<e>> percentage points for $\\gamma=0$. Numerical verification is not physical validation, "
              "which Section 5.2 addresses as far as the available references allow.",
              nt=n(NTEST), a=n(MESH[0]["Tp45"], 2), b=n(MESH[3]["Tp45"], 2), d=n(abs(MESH[0]["diff_to_finest_K"]), 2), e=n(100 * V["D"]["max_abs_err_gamma0"], 2))))
add(("h2", "5.2 Benchmarks against independent solutions"))
add(("p", fmt("The melt formulas are quasi-steady and the steam correlation is borrowed from another geometry, so each was checked against an independent reference (Table @T:bench@, Fig. @F:bench@). An enthalpy-method finite-volume solver of one-dimensional melting, written independently of the melt formulas, "
              "reproduces the exact Neumann solution for a liquid layer growing into a solid at its melting temperature, at a Stefan number $St=c\\Delta T/L_f=<<st>>$, to <<en>>% in the front position at 60 s [@Alexiades2018]. "
              "The solver is then run with the convective steam boundary and with the median parameters. For instant removal of the melt (cells removed as soon as they are liquid) the ablation formula agrees with the solver within <<ea>>% for $h=1$–10 kW/m²·K and deposit thicknesses of "
              "3–12 mm, once the cell size resolves the ablation layer (4 µm; the melt time changes by <<cr>>% between 4 and 2 µm). The no-drainage formula (Eq. 4), which neglects the sensible heat of the liquid, gives melt times shorter than the solver by <<en1>>%, "
              "the same in every case; the quasi-steady front of the Neumann problem is <<qs>>% ahead of the exact one at this Stefan number. The no-drainage limit is therefore optimistic by about a fifth, and the true no-drainage range is smaller than reported, "
              "which strengthens the conclusion that the range can collapse. The conduction solver, integrated with backward Euler at 10 s, differs from an independent stiff-ODE integration (BDF, relative tolerance $10^{-10}$) of the same equations by <<c1>> K at 45 min, and by <<c2>> K at 0.625 s.",
              st=n(NM["St"], 2), en=n(100 * abs(NM["rel_err"]), 3), ea=n(100 * max(ERR_A), 1), cr=n(100 * abs(BSF["ablation_resolution"][3]["t_ablation_numeric"] / BSF["ablation_resolution"][2]["t_ablation_numeric"] - 1), 2),
              en1=n(100 * abs(sum(ERR_N) / len(ERR_N)), 0), qs=n(100 * NM["rel_err_quasi_steady"], 0), c1=n(abs(BCD["diff_10s_K"]), 3), c2=n(abs(BCD["diff_0p625s_K"]), 3))))
add(("table", "Table @T:bench@. Benchmarks of the model components.", ["Component", "Reference", "Result"],
     [["Enthalpy-method Stefan solver", "Exact Neumann solution, $St$ = %s" % n(NM["St"], 2), "front position error %s%%" % n(100 * NM["rel_err"], 3)],
      ["Instant-removal (ablation) melt time", "enthalpy solver, 4 µm cells, h 1–10 kW/m²·K, 3–12 mm", "formula shorter by 0.2 to %s%%" % n(100 * max(ERR_A), 1)],
      ["No-drainage melt time, Eq. (4)", "enthalpy solver", "formula shorter by %s%% in every case" % n(100 * abs(sum(ERR_N) / len(ERR_N)), 0)],
      ["Quasi-steady melt front", "Neumann solution, $St$ = %s" % n(NM["St"], 2), "front ahead by %s%%" % n(100 * NM["rel_err_quasi_steady"], 0)],
      ["Conduction solver, pack at 45 min", "independent BDF integration, same equations", "%s K (10 s step); %s K (0.625 s)" % (n(BCD["diff_10s_K"], 3), n(BCD["diff_0p625s_K"], 3))],
      ["Condensation coefficient", "Chato internal stratified correlation", "Chato is %s of Nusselt at 40–140 K" % n(sum(X["hmodels"]["h_ratio_chato_to_nusselt"].values()) / 3, 2)],
      ["Saturation pressure", "IAPWS-IF97 saturation line", "1.554 MPa at 200 °C; 1.49 MPa at 198 °C"],
      ["Coupled model (all components)", "experiments with steam melting a deposit in a pipe", "none identified; not validated"]], [1.4, 1.6, 1.4]))
add(("fig", "Fig14_benchmarks.png", "Fig. @F:bench@. (a) Melt-time formulas against the enthalpy solver (the line is equality). (b) Nusselt, Chato and non-condensable-limited condensation coefficients in a 0.30 m bore. (c) Median range for the three coefficients, instant melt removal and a 0.2 mm retained film.", 6.4))
add(("p", "No published experiment that measures steam melting a paraffin deposit in a pipe, or the coupled system, was identified in the literature consulted for this study, and the coupled model is therefore not validated. The paraffin-melting experiments that were located are enclosure experiments, for example paraffin RT58 in a horizontal cylinder, in which conduction governs at first and natural convection later, and whose results are reported as phase-front contours [@Yadav2020]; they do not test a conduction-limited layer heated through a condensate film, and no front-position data suitable for a quantitative comparison with Eq. (4) were found. Reviews of paraffin phase-change materials [@Sharma2009] are the source for the kind of property (latent heat, liquid conductivity) that the model assumes; the assumed values were not fitted to a specific wax. The benchmarks above establish "
          "that the numerical solutions are correct for the stated equations and quantify the error of the quasi-steady formulas; they do not show that the stated equations describe a real deposit, a real steam path or a real tool. "
          "The model applies as a design-screening tool for a meltable paraffin deposit of millimetre thickness on a steel wall at melt-front Stefan numbers of order one, with the steam taken at rest. Wax solids that do not melt, gel structure, "
          "the thermal inertia of the pipe steel, steam velocity and shear, and two-phase flow of the melt are outside it."))

add(("h1", "6. Results"))
add(("h2", "6.1 Thermal shield"))
add(("fig", "Fig2_pack_temperature.png", "Fig. @F:fan@. Pack temperature against time for 40 mm of aerogel, atmospheric (left) and evacuated (right): median, 5–95% and 1–99% bands.", 6.3))
add(("p", fmt("At 45 min the pack median is <<ta>> °C (95th percentile <<tp>> °C) with atmospheric aerogel and <<tv>> °C (<<tvp>> °C) with the evacuated jacket (Fig. @F:fan@). The probability of staying at or below 55 °C is <<pa>> (95% interval <<ca>>) and <<pv>> (<<cv>>) "
              "respectively. The median time to reach 55 °C is <<ca1>> min (5th percentile <<ca2>> min) and <<cv1>> min (<<cv2>> min), and <<cen>> of the evacuated draws never reached it within the 120 min horizon. The first suite's 3,000 draws and the "
              "re-drawn 3,000 of the extended suite agree (<<pa2>> against <<pa>>). The diffusion time of aerogel across 40 mm is of the order of hours, so the wall has not reached steady state within the mission and the margin belongs to the thermal mass of the pack "
              "and to the starting temperature, not to the insulation alone (Section 6.5).",
              ta=n(A_ATM["Tp45_median"], 1), tp=n(A_ATM["Tp45_p95"], 1), tv=n(A_VAC["Tp45_median"], 1), tvp=n(A_VAC["Tp45_p95"], 1), pa=pc(A_ATM["P_safe"], 1), ca=ci(*A_ATM["ci"]), pv=pc(A_VAC["P_safe"], 1), cv=ci(*A_VAC["ci"]),
              ca1=n(A_ATM["t_crit_median_min"]), ca2=n(A_ATM["t_crit_p05_min"]), cv1=n(A_VAC["t_crit_median_min"]), cv2=n(A_VAC["t_crit_p05_min"]), cen=pc(A_VAC["frac_censored_120min"], 0), pa2=pc(R["baseline_atm"]["P_safe"], 1))))
add(("fig", "Fig4_design_sweep.png", "Fig. @F:sweep@. Probability of meeting the 55 °C limit against aerogel thickness (solid: 45 min; dotted: 90 min).", 3.9))
add(("p", fmt("A 95% target at 45 min requires roughly 30 mm of atmospheric aerogel (<<a30>>) or 15 mm of evacuated aerogel (<<v15>>) (Fig. @F:sweep@). The evacuated curve plateaus near 99% because of the assumed 5% vacuum-loss probability and the tails of "
              "initial temperature and heat generation. For a 90 min mission the probability at 40 mm falls to <<a90>> (atmospheric) and <<v90>> (evacuated).",
              a30=pc(SW["atmospheric"][4][0], 1), v15=pc(SW["evacuated"][2][0], 1), a90=pc(V["A_sweep90"]["atmospheric"][5], 0), v90=pc(V["A_sweep90"]["evacuated"][5], 0))))

add(("h2", "6.2 Melt kinetics with instant removal of the melt, and the speed cap"))
add(("p", fmt("With the first suite's assumption that molten deposit leaves the surface at once, the median condensation coefficient is <<h>> kW/m²·K and the film flux <<q>> kW/m². The melt time of a deposit has a median of <<tm>> s (95th percentile <<tm95>> s). "
              "The thermally limited speed $v_{th}$ has a median of <<v>> cm/s (5th percentile <<v5>> cm/s) and is below the 10 cm/s set-point in <<fl>> of the draws. The median cleaned range per 45 min deployment is <<rg>> m (5th to 95th percentile <<r5>> to <<r95>> m). "
              "The upper value, and every range above it, is the speed set-point and not a thermal limit: the cap of 0.1 m/s × 2,700 s = 270 m binds in <<cap>> of the draws, those with $v_{th}\\ge0.10$ m/s. Without the cap the thermally limited range $v_{th}t_{run}$ has a median of "
              "<<um>> m, a 95th percentile of <<u95>> m, and reaches 300 m in <<u300>> and 1 km in <<u1k>> of the draws. The 270 m of the first suite is therefore an input, and the thermal result is the distribution of $v_{th}$ (Fig. @F:melt@). "
              "The median steam use is <<s>> kg per metre (95th percentile <<s95>> kg/m), about <<c>> m³ of condensate per 100 m.",
              h=n(BB["h_cond_median"] / 1e3, 1), q=n(BB["q_raw_median_kWm2"]), tm=n(BB["t_melt_median_s"], 1), tm95=n(BB["t_melt_p95_s"]), v=n(BB["v_th_median_cms"], 1), v5=n(BB["v_th_p05_cms"], 1), fl=pc(BB["frac_thermally_limited"], 0),
              rg=n(BB["range_median_m"]), r5=n(BB["range_p05_m"]), r95=n(BB["range_p95_m"]), cap=pc(UNC["P_range_at_cap"], 0), um=n(UNC["uncapped_range_median_m"]), u95=n(UNC["uncapped_range_p95_m"]), u300=pc(UNC["P_uncapped_ge_300"], 0), u1k=pc(UNC["P_uncapped_ge_1000"], 1),
              s=n(BB["steam_kg_per_m_median"], 2), s95=n(BB["steam_kg_per_m_p95"], 1), c=n(BB["condensate_m3_per_100m_median"], 2))))
add(("fig", "Fig5_condensation_range.png", "Fig. @F:melt@. Condensation coefficient against temperature difference, melt-time distribution and exceedance of the cleaned range per deployment (instant removal of the melt; the vertical step at 270 m is the speed cap).", 6.3))

add(("h2", "6.3 Condensation representation"))
rows = []
for k, lab in (("nusselt", "Nusselt (first suite)"), ("chato", "Chato, internal stratified"), ("chato_ncg", "Chato, non-condensable factor 0.5")):
    m = HM[k]
    rows.append([lab, n(m["range_median_m_s0"]), "%s to %s" % (n(m["range_p05_m_s0"]), n(m["range_p95_m_s0"])), n(m["range_median_m_s0.2"], 1), pc(m["P_safe"], 1)])
add(("p", fmt("The Chato correlation gives a coefficient <<r>> of the Nusselt value (Fig. @F:bench@b), and the non-condensable limit half of that. With instant removal of the melt the median range falls from <<n0>> m to <<c0>> m and <<k0>> m (Table @T:hmod@), changes of <<dc>>% and <<dk>>%. "
              "With a 0.2 mm retained film the three representations give <<n2>>, <<c2>> and <<k2>> m: the film, with $\\Pi_f=hs/k_l\\approx<<pf>>$ at the median coefficient, dominates the resistance, and the condensation model matters little. "
              "The pack probability does not change (<<pp>>) because the steam-side coefficient on the hull is capped at 12 kW/m²·K and the aerogel dominates the resistance by two orders of magnitude, so the hull is insensitive to the condensation model; "
              "the case that is conservative for the pack, no condensate-film resistance at all, is covered by that cap.",
              r=n(sum(X["hmodels"]["h_ratio_chato_to_nusselt"].values()) / 3, 2), n0=n(HM["nusselt"]["range_median_m_s0"]), c0=n(HM["chato"]["range_median_m_s0"]), k0=n(HM["chato_ncg"]["range_median_m_s0"]),
              dc=n(100 * (1 - HM["chato"]["range_median_m_s0"] / HM["nusselt"]["range_median_m_s0"])), dk=n(100 * (1 - HM["chato_ncg"]["range_median_m_s0"] / HM["nusselt"]["range_median_m_s0"])),
              n2=n(HM["nusselt"]["range_median_m_s0.2"]), c2=n(HM["chato"]["range_median_m_s0.2"]), k2=n(HM["chato_ncg"]["range_median_m_s0.2"]), pf=n(BB["h_cond_median"] * 0.2e-3 / F["k_liq"], 1), pp=pc(HM["nusselt"]["P_safe"], 1))))
add(("table", "Table @T:hmod@. Effect of the condensation representation (3,000 draws, same random numbers; 45 min; 40 mm atmospheric aerogel).", ["Representation", "Median range, instant removal (m)", "5th to 95th percentile (m)", "Median range, 0.2 mm film (m)", "P(pack ≤ 55 °C)"], rows, [1.7, 1.2, 1.2, 1.2, 1.0]))

add(("h2", "6.4 The retained film: dimensionless resistance, constant film and dynamic film"))
rows = []
for s_ in (0.0, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0):
    r = FR[s_]
    rows.append([n(s_, 2) if s_ else "0 (instant removal)", n(s_ * 1e-3 * BB["h_cond_median"] / F["k_liq"], 2), n(r["v_th_median_cms"], 2 if r["v_th_median_cms"] < 1 else 1), n(r["range_median_m"], 1 if r["range_median_m"] < 100 else 0),
                 "%s to %s" % (n(r["range_p05_m"], 0 if r["range_p05_m"] > 10 else 1), n(r["range_p95_m"])), pc(r["P_ge_100"], 0)])
rows.append(["dynamic film (Eq. 5)", n(DY["steady_film_median_params"]["Pi_f"], 1), n(DY["baseline"]["v_th_median_cms"], 2), n(DY["baseline"]["range_median_m"], 1), "%s to %s" % (n(DY["baseline"]["range_p05_m"], 1), n(DY["baseline"]["range_p95_m"])), pc(DY["baseline"]["P_ge_100"], 0)])
rows.append(["no drainage (limit)", "–", n(ND["v_nodrain_median_cms"], 2), n(ND["range_nodrain_median_m"], 1), "–", pc(ND["P_ge_100"], 0)])
add(("p", fmt("Eq. (3) gives the generalization: the heat flux through a retained film is $q_0/(1+\\Pi_f)$ with $\\Pi_f=hs/k_l$, so a film of $s=k_l/h$, <<kh>> µm at the median coefficient, halves the flux. Because the median melt-limited speed of the "
              "first suite is only <<vr>> times the 3.7 cm/s that a 100 m range needs, the median range falls below 100 m at $\\Pi_f=<<pf>>$, a film of <<sx>> µm (Table @T:film@, Fig. @F:film@). A range of 100 m therefore needs $\\Pi_f\\lesssim0.3$, "
              "and a film resistance a third of the condensate film's is enough to lose it. For a constant film the median range falls to <<r005>> m at 0.05 mm, <<r02>> m at 0.2 mm and <<r1>> m at 1 mm. "
              "If none of the melt drains (Eq. 4), the median melt time is <<tnd>> s instead of <<tab>> s, a factor <<ratio>>, and the median range is <<rnd>> m; with the benchmark bias of Section 5.2 the true value is lower still.",
              kh=n(F["k_liq"] / BB["h_cond_median"] * 1e6), vr=n(BB["v_th_median_cms"] / 3.7, 1), pf=n(DY["Pi_f_for_100m_median"], 2), sx=n(F["s_median_below_100m_mm"] * 1000), r005=n(FR[0.05]["range_median_m"]), r02=n(FR[0.2]["range_median_m"]), r1=n(FR[1.0]["range_median_m"], 1),
              tnd=n(ND["t_melt_nodrain_median_s"]), tab=n(ND["t_melt_ablation_median_s"], 1), ratio=n(ND["ratio_median"]), rnd=n(ND["range_nodrain_median_m"], 1))))
add(("table", "Table @T:film@. Median speed and cleaned range per 45 min deployment against the retained film (atmospheric aerogel, 40 mm; same draws in every row). $\\Pi_f=hs/k_l$ at the median coefficient (for the dynamic film, at the median steady film).",
     ["s (mm)", "Π_f", "Median v_th (cm/s)", "Median range (m)", "5th to 95th percentile (m)", "P(range ≥ 100 m)"], rows, [1.4, 0.7, 1.0, 1.0, 1.3, 1.0]))
add(("fig", "Fig6_film.png", "Fig. @F:film@. (a) Cleaned range per 45 min deployment against the retained film (median and 5–95% band; dashed: no-drainage limit; dotted: 1 km). (b) Exceedance of the range for three film thicknesses.", 6.3))
add(("p", fmt("The dynamic film (Eq. 5) predicts instead of prescribing the film. Melt production raises the film to its quasi-steady value within seconds (Fig. @F:dyn@a), after which the front advances at the rate that film allows. For the median parameters the film settles at <<s>> mm "
              "($\\Pi_f=<<pi>>$, a flux reduced to <<fr>> of the film-free value); over the draws it has a median of <<se>> mm (5th to 95th percentile <<s5>> to <<s95>> mm), the melt time has a median of <<tm>> s (<<ratio>> times the instant-removal value), "
              "and the median range is <<rg>> m (<<r5>> to <<r95>> m), with <<p100>> of draws reaching 100 m. The prediction is the middle of the constant-film curve, close to the 0.5 mm case, and far from both limits (Fig. @F:dyn@b). "
              "It depends on the drainage assumptions through the group $\\mu_l\\ell$: a four times lower viscosity or drain path raises the median range to <<lo>> m, a four times higher one lowers it to <<hi>> m, and a residual wetting film of 0.02 or 0.05 mm gives "
              "<<w1>> and <<w2>> m (Fig. @F:dyn@c). The film is a few tenths of a millimetre because gravity drains a Nusselt film slowly at these viscosities: the cubic law makes the steady film scale as $(\\mu_l\\ell\\,\\dot{x})^{1/3}$, "
              "so even large changes of the drainage parameters move it by tens of percent. The drainage model is assumed, not measured, and a molten pool at the invert is outside it; the result that the range is of order 10 m and not 100 m holds across this sensitivity.",
              s=n(DY["steady_film_median_params"]["s_star_mm"], 2), pi=n(DY["steady_film_median_params"]["Pi_f"], 1), fr=pc(DY["steady_film_median_params"]["flux_ratio"], 0), se=n(DY["baseline"]["s_end_median_mm"], 2), s5=n(DY["baseline"]["s_end_p05_mm"], 2),
              s95=n(DY["baseline"]["s_end_p95_mm"], 2), tm=n(DY["baseline"]["t_melt_median_s"]), ratio=n(DY["baseline"]["ratio_median"], 1), rg=n(DY["baseline"]["range_median_m"]), r5=n(DY["baseline"]["range_p05_m"]), r95=n(DY["baseline"]["range_p95_m"]),
              p100=pc(DY["baseline"]["P_ge_100"], 1), lo=n(DY["sensitivity"]["viscosity x0.25"]["range_median_m"]), hi=n(DY["sensitivity"]["viscosity x4"]["range_median_m"]), w1=n(DY["sensitivity"]["residual film 0.02 mm"]["range_median_m"]),
              w2=n(DY["sensitivity"]["residual film 0.05 mm"]["range_median_m"]))))
add(("p", fmt("Three idealizations of the drainage model were examined. Wall orientation: the film drains by gravity along the wall between the crown and the invert, and the mean $\\sin\\theta$ of 0.7 stands for that path; for a wall near the invert ($\\sin\\theta=0.2$) the median range is <<o1>> m and for the spring line ($\\sin\\theta=1$) <<o2>> m, so orientation moves the result by a quarter. "
              "Steam shear: an interfacial shear $\\tau$ adds a film flux $\\tau s^2/2\\mu_l$. Gravity exerts a stress of about <<g>> Pa on the median film, whereas the steam that condensation alone feeds into the zone moves at about <<uc>> m/s and produces a shear of order $10^{-3}$ Pa, negligible; "
              "shears of 0.1, 1 and 10 Pa need steam velocities of about <<u1>>, <<u2>> and <<u3>> m/s (friction factor 0.01, assumed) and raise the median range to <<t1>>, <<t2>> and <<t3>> m. A forced steam flow through the zone could therefore help, but only at velocities far above those that condensation induces, and the interfacial shear on a viscous film "
              "is uncertain. Molten pool: the melt collects as a pool at the invert, ahead of the skirt. Where the pool covers the deposit it behaves as a layer that does not drain, and the range of that sector approaches the no-drainage limit (<<nd>> m) unless the skirt moves the pool ahead of the tool; "
              "since the whole circumference has to be cleaned, the dynamic-film value (<<rd>> m) is an upper bound for a tool whose pool covers part of the circumference, and the true median lies between it and the no-drainage limit. The pool and the shear are not modelled explicitly, and the range of 18 m is therefore a screening value with the sensitivity shown, not a prediction.",
              o1=n(DY["sensitivity"]["wall near the invert (sin 0.2)"]["range_median_m"]), o2=n(DY["sensitivity"]["wall at the spring line (sin 1.0)"]["range_median_m"]), g=n(DY["gravity_stress_Pa_at_median_film"], 1), uc=n(DY["steam_velocity_for_condensation_m_s"], 2),
              u1=n(DY["shear_vs_velocity"][0]["u_steam_m_s"], 1), u2=n(DY["shear_vs_velocity"][1]["u_steam_m_s"], 0), u3=n(DY["shear_vs_velocity"][2]["u_steam_m_s"], 0), t1=n(DY["sensitivity"]["steam shear 0.1 Pa"]["range_median_m"]), t2=n(DY["sensitivity"]["steam shear 1 Pa"]["range_median_m"]),
              t3=n(DY["sensitivity"]["steam shear 10 Pa"]["range_median_m"]), nd=n(ND["range_nodrain_median_m"], 1), rd=n(DY["baseline"]["range_median_m"]))))
add(("fig", "Fig13_dynamic_film.png", "Fig. @F:dyn@. Dynamic retained film. (a) Film thickness and melted thickness for one draw. (b) Median range of the dynamic model (band: 5–95%) against the constant-film curve and the no-drainage limit. (c) Median range for the drainage sensitivity cases.", 6.4))

add(("h2", "6.5 Global sensitivity, correlated inputs and model-form uncertainty"))
SP, SR, SS = SOB["pack_temperature_45min"], SOB["range_with_film"], SOB["steam_with_film"]
def top(d, k=3):
    o = sorted(range(len(d["names"])), key=lambda i: -d["ST"][i])[:k]
    return ", ".join("%s (%s)" % (d["names"][i], n(d["ST"][i], 2)) for i in o)
add(("p", fmt("Sobol indices (Fig. @F:sobol@; $2^{<<m1>>}$ base samples for the pack, $2^{<<m2>>}$ for the melt model; bootstrap intervals in the Supplementary Information) show that the pack temperature at 45 min is governed by two inputs, the total indices being <<tp>>; the first-order indices sum to <<sp>>, "
              "so the response is nearly additive. The range, with the retained film as an assumed lognormal input (median 0.2 mm, $\\sigma=1$), is governed by <<tr>>; the film alone carries <<fs>> of the variance. With instant removal the ranking is <<ti>>. "
              "The melting steam per metre depends on the deposit and the heat-coupling fraction (<<ts>>) and not on the film, because the film changes the speed and not the energy. The indices depend on the assumed input distributions, in particular on the film prior, "
              "and are conditional on them. Sampling adequacy was checked by halving the base sample: the total indices of the melt model change by at most <<dm>> and those of the pack by at most <<dp>>, the half-widths of the 95% bootstrap intervals are at most <<hm>> (melt model) and <<hp>> (pack), and the ranking of the leading inputs does not change.",
              m1=n(int(math.log2(SP["N"]))), m2=n(int(math.log2(SR["N"]))), tp=top(SP, 2), sp=n(sum(SP["S1"]), 2), tr=top(SR, 3), fs=pc(SR["S1"][10], 0), ti=top(SOB["range_instant_removal"], 3), ts=top(SS, 2), dm=n(max(SOB["convergence"][k]["max_abs_diff_ST"] for k in ("range_with_film", "range_instant_removal")), 3), dp=n(SOB["convergence"]["pack_temperature_45min"]["max_abs_diff_ST"], 3), hm=n(max(SOB["convergence"][k]["max_ci_halfwidth_ST"] for k in ("range_with_film", "range_instant_removal")), 3), hp=n(SOB["convergence"]["pack_temperature_45min"]["max_ci_halfwidth_ST"], 3))))
c0, cp, cm, cdp, cdm = CORR[0], CORR[1], CORR[2], CORR[3], CORR[4]
rngs = [HM["nusselt"]["range_median_m_s0"], HM["chato"]["range_median_m_s0"], HM["chato_ncg"]["range_median_m_s0"], FR[0.2]["range_median_m"], DY["baseline"]["range_median_m"], ND["range_nodrain_median_m"]]
add(("p", fmt("Physically plausible correlations were imposed through a Gaussian copula. A positive correlation of 0.6 between the starting temperature and the heat generation (a hot, heavily loaded tool) lowers the thermal probability from <<c0>> to <<cp>>, "
              "and a negative one raises it to <<cm>>; a correlation of ±0.6 between the deposit thickness and its melt point changes the median range by less than <<cd>>%. The thermal conclusion is therefore sensitive to the correlation of the two dominant inputs, "
              "not to the others. The two kinds of uncertainty differ greatly in size. Within the instant-removal model the 5th to 95th percentile of the range spans a factor of <<f1>> (<<r5>> to <<r95>> m) from parameter uncertainty alone. Across the model forms studied, "
              "the median range spans <<lo>> to <<hi>> m, a factor of <<f2>>, from the condensation correlation, the melt-removal model and the film treatment. The choice of model form is a larger source of uncertainty than the parameters within a model, "
              "which is why the claims below are stated against the model form.",
              c0=pc(c0["P_safe"], 1), cp=pc(cp["P_safe"], 1), cm=pc(cm["P_safe"], 1), cd=n(100 * max(abs(cdp["range_median_m"] / c0["range_median_m"] - 1), abs(cdm["range_median_m"] / c0["range_median_m"] - 1)), 1),
              f1=n(BB["range_p95_m"] / BB["range_p05_m"], 0), r5=n(BB["range_p05_m"]), r95=n(BB["range_p95_m"]), lo=n(min(rngs), 1), hi=n(max(rngs)), f2=n(max(rngs) / min(rngs), 0))))
add(("fig", "Fig15_sobol.png", "Fig. @F:sobol@. Sobol indices (total and first order) of (a) the pack temperature at 45 min, (b) the cleaned range with the retained film as an assumed lognormal input, and (c) the melting steam per metre.", 6.4))

add(("h2", "6.6 Pipe length, deployments and intervention time"))
def cv(m, c, L):
    return COV["%s|%s|%g" % (m, c, L)]
rows4 = []
for m_, lab in (("45 min atmospheric", "45 min, atmospheric"), ("90 min evacuated", "90 min, evacuated")):
    for c_, cl in (("ablation", "instant removal"), ("retained 0.5 mm", "0.5 mm film")):
        for L in (100.0, 300.0, 1000.0):
            d = cv(m_, c_, L)
            rows4.append([lab, cl, n(L), pc(d["P_single"], 0), "%s (%s)" % (n(d["n_dep_median"]), n(d["n_dep_p95"])), n(d["active_h_median"], 1), n(d["total_h_median"]), pc(d["active_fraction_median"], 0)])
for m_, lab in (("45 min atmospheric", "45 min, atmospheric"), ("90 min evacuated", "90 min, evacuated")):
    for L in (100.0, 300.0, 1000.0):
        d = CVD["%s|dynamic film|%g" % (m_, L)]
        rows4.append([lab, "dynamic film", n(L), pc(d["P_single"], 0), "%s (%s)" % (n(d["n_dep_median"]), n(d["n_dep_p95"])), n(d["active_h_median"], 1), n(d["total_h_median"]), pc(d["active_fraction_median"], 0)])
c3 = cv("45 min atmospheric", "ablation", 300.0); c10 = cv("45 min atmospheric", "ablation", 1000.0); e3 = cv("90 min evacuated", "ablation", 300.0); k10 = CVD["45 min atmospheric|dynamic film|1000"]; k90 = CVD["90 min evacuated|dynamic film|1000"]
add(("p", fmt("The brief names pipes from about 0.3 m to 1 km. The number of deployments depends decisively on the melt-removal assumption, and the two cases must not be mixed (Table @T:cov@, Fig. @F:cov@). With instant removal of the melt the median range is <<rg0>> m per deployment, and a 1 km line needs a median of <<n1>> deployments (95th percentile <<n1p>>); "
              "with the dynamic film, the baseline of this paper, the median range is <<rg1>> m and a 1 km line needs a median of <<k1>> deployments (5th to 95th percentile <<k5>> to <<k95>>), in agreement with the simple estimate of 1,000 m divided by the median range, <<nv>>. "
              "With a 0.5 mm constant film it needs <<n2>> and if no melt drains <<n3>>. Under the assumed logistics durations (Table @T:inputs@) the total intervention time for 1 km has a median of <<t1>> h with instant removal (<<a1>> h of active cleaning, <<f1>>) and <<tk>> h with the dynamic film (5th to 95th percentile <<tk5>> to <<tk95>> h; <<ak>> h active, <<fk>>). "
              "A 90 min evacuated mission needs <<k90>> deployments with the dynamic film. No draw cleans a 300 m line in one deployment (the 270 m of a 45 min mission is the set-point cap, Section 6.2; with a higher set-point the thermally limited speed with instant removal would allow 300 m in <<u300>> of the draws), and with the dynamic film the largest range in any draw is <<rmax>> m. "
              "The absolute hours depend on assumed durations, but the ratio does not: most of the intervention is not cleaning. Every extra deployment also requires that the tool is recovered through the same flow-aligned connection by which it entered, which the brief states as the only access; the model does not include recovery or the passage of the tool through bends, valves and diameter changes.",
              rg0=n(BB["range_median_m"]), n1=n(c10["n_dep_median"]), n1p=n(c10["n_dep_p95"]), rg1=n(k10["range_median_m"]), k1=n(k10["n_dep_median"]), k5=n(k10["n_dep_p05"]), k95=n(k10["n_dep_p95"]), nv=n(k10["naive_n_dep"]),
              n2=n(cv("45 min atmospheric", "retained 0.5 mm", 1000.0)["n_dep_median"]), n3=n(cv("45 min atmospheric", "no drainage", 1000.0)["n_dep_median"]), t1=n(c10["total_h_median"]), a1=n(c10["active_h_median"], 1), f1=pc(c10["active_fraction_median"], 0),
              tk=n(k10["total_h_median"]), tk5=n(k10["total_h_p05"]), tk95=n(k10["total_h_p95"]), ak=n(k10["active_h_median"], 0), fk=pc(k10["active_fraction_median"], 0), k90=n(k90["n_dep_median"]), u300=pc(UNC["P_uncapped_ge_300"], 0), rmax=n(k10["range_max_m"]))))
add(("table", "Table @T:cov@. Deployments and time to clean a line of length L (median; 95th percentile of the deployment count in parentheses). Durations of the non-cleaning stages are assumed (Table @T:inputs@).",
     ["Mission", "Melt removal", "L (m)", "P(one deployment)", "Deployments", "Active (h)", "Total (h)", "Active share"], rows4, [1.3, 1.1, 0.6, 1.0, 1.1, 0.8, 0.8, 0.8]))
add(("fig", "Fig7_coverage.png", "Fig. @F:cov@. (a) Probability that one deployment cleans a line against its length for three melt-removal cases (solid: 45 min atmospheric; dotted: 90 min evacuated). (b) Median active cleaning time (dark) and total intervention time (light), 45 min atmospheric.", 6.3))

add(("h2", "6.7 Pipe size, pipe temperature and the feasible envelope"))
d4, d6, d8, d10, d12 = DIA[4], DIA[6], DIA[8], DIA[10], DIA[12]
rows5 = []
for k in (4, 6, 8, 10, 12, 16):
    d = DIA[k]
    rows5.append([str(k), n(d["ID"] * 1000), "%s" % n(2 * d["r_hull"] * 1000) if d["r_hull"] > 0.02 else "–", n(d["t_a"] * 1000) if d["feasible"] else "does not fit", n(d["m_pack_nom"], 1) if d["feasible"] else "–",
                 pc(d["P_safe_atm"], 0) if d["P_safe_atm"] is not None else "–", pc(d["P_safe_vac"], 0) if d["P_safe_vac"] is not None else "–", n(d["force_3bar_kN"], 1), n(d["brake_ratio_3bar"], 1)])
add(("p", fmt("The brief covers 4 to 16 inches; the first design was sized for 12 in. Keeping the radial clearance of the first design (44 mm), the hull does not fit in a 4 or 6 in pipe, even with the aerogel removed down to a 25 mm pack. In an 8 in pipe the aerogel "
              "shrinks to <<ta8>> mm and the pack to <<m8>> kg, and the probability of keeping the pack at or below 55 °C for 45 min is <<p8>> (<<v8>> evacuated); in a 10 in pipe it is <<p10>> (<<v10>> evacuated); from 12 in upward it is <<p12>> (Table @T:dia@). "
              "The thermal margin therefore scales with the thermal mass of the pack, and the architecture as modelled covers about the upper third of the brief's diameter range. The surge force of a 3 bar break-through grows with the "
              "bore, from <<f8>> kN (8 in) to <<f16>> kN (16 in), against the same 2.5 kN of braking authority.",
              ta8=n(d8["t_a"] * 1000), m8=n(d8["m_pack_nom"], 1), p8=pc(d8["P_safe_atm"], 0), v8=pc(d8["P_safe_vac"], 0), p10=pc(d10["P_safe_atm"], 0), v10=pc(d10["P_safe_vac"], 0), p12=pc(d12["P_safe_atm"], 0), f8=n(d8["force_3bar_kN"]), f16=n(DIA[16]["force_3bar_kN"]))))
add(("table", "Table @T:dia@. Fit and thermal margin against nominal pipe size (standard wall; 45 min; 40 mm aerogel where it fits).",
     ["NPS (in)", "Bore (mm)", "Hull OD fitted (mm)", "Aerogel (mm)", "Pack (kg)", "P(≤ 55 °C) atm.", "P(≤ 55 °C) evac.", "Force at 3 bar (kN)", "Force / braking"], rows5, [0.6, 0.7, 1.0, 0.9, 0.7, 0.9, 0.9, 1.0, 0.9]))
e25, e35, e45, e55 = ENV[25.0], ENV[35.0], ENV[45.0], ENV[55.0]
add(("p", fmt("The pack starts at the pipe temperature, which is the dominant input (Section 6.5). Shifting the initial pack and pipe temperature with the same draws, the probability for the 12 in design falls from <<p25>> at 25 °C to <<p35>> at 35 °C, <<p45>> at 45 °C and "
              "<<p55>> at 55 °C (atmospheric; evacuated <<v25>>, <<v35>>, <<v45>> and <<v55>>), while the median range changes little (<<r25>> m at 25 °C, <<r45>> m at 45 °C) until the pack limit is reached early (Fig. @F:dia@). Fig. @F:env@ combines the two: a probability of at least 95% "
              "requires a pipe of 12 in or larger and a pipe temperature of about 30 °C or below, and no size in the brief's range is reliable at 40 °C. A line that still carries warm produced fluid, for example at 40 to 60 °C, "
              "must therefore be cooled and flushed before the tool enters, which is a preparation step that the intervention time of Table @T:cov@ only partly includes.",
              p25=pc(e25["P_safe_atm"], 0), p35=pc(e35["P_safe_atm"], 0), p45=pc(e45["P_safe_atm"], 0), p55=pc(e55["P_safe_atm"], 0), v25=pc(e25["P_safe_vac"], 0), v35=pc(e35["P_safe_vac"], 0), v45=pc(e45["P_safe_vac"], 0), v55=pc(e55["P_safe_vac"], 0),
              r25=n(e25["range_median_m"]), r45=n(e45["range_median_m"]))))
add(("fig", "Fig8_diameter_temperature.png", "Fig. @F:dia@. (a) Probability of keeping the pack at or below 55 °C for 45 min against nominal pipe size (crosses: the hull does not fit). (b) Fitted hull diameter, pipe bore and the first design's hull. (c) The same probability against pipe temperature, 12 in design.", 6.5))
add(("fig", "Fig17_envelope.png", "Fig. @F:env@. Feasible envelope: probability (%) of keeping the pack at or below 55 °C for 45 min against nominal pipe size and pipe temperature (atmospheric aerogel, 40 mm where it fits; 400 draws per cell).", 4.2))

add(("h2", "6.8 Pressure–temperature compatibility and the revised envelope"))
rows8 = [[n(r["T"]), n(r["psat_bar"], 1), n(r["class150_bar"], 1), n(r["class300_bar"], 1)] for r in PT["rows"] if r["T"] in (150.0, 170.0, 180.0, 190.0, 195.0, 200.0, 205.0)]
add(("p", fmt("The first design used saturated steam at 198 °C, whose pressure is <<ps>> bar. The rated working pressure of a Group 1.1 carbon-steel flange of Class 150 falls with temperature to about 13.8 bar at 200 °C [@ASMEB165], so the model's operating point exceeds it (Table @T:pt@, Fig. @F:pt@). "
              "The highest saturation temperature whose pressure is within the Class 150 rating is <<tm>> °C (<<pm>> bar); Class 300 would admit the whole range studied. The rated values used are rounded approximations of the standard's tables; the governing ratings "
              "must be taken from the current edition and the actual line specification. A revised operating envelope for a Class 150 line is saturated steam at <<tr>> °C, 3 °C below the limit. The check covers the whole sampled steam-temperature distribution, not its mean: in the first design <<fo>> of the sampled temperatures (maximum <<mo>> °C) exceed the limit. With the steam temperature redrawn as N(<<tr>>, 2) °C truncated at the limit (maximum sampled value <<mr>> °C, none above it) the median melt time rises from <<m0>> to <<m1>> s, "
              "the median range falls from <<r0>> to <<r1>> m (<<dr>>%) and the pack probability is unchanged (<<pk>>), because the aerogel, not the steam film, controls the heat reaching the pack. The pressure limit is therefore a constraint on the design, not a reason to reject it, "
              "provided the line is Class 150 or better at the temperature and the seals and elastomers are rated for it; a line of lower rating would need a lower steam temperature and a re-run of the study.",
              fo=pc(RVO["frac_above_class150_limit"], 0), mo=n(RVO["Tsat_max"]), mr=n(RVN["Tsat_max"], 1), ps=n(PT["psat_198C_bar"], 1), tm=n(PT["Tmax_class150_C"]), pm=n(PT["psat_Tmax150_bar"], 1), tr=n(PT["Tmax_class150_C"] - 3), m0=n(RVO["t_melt_median_s"], 1), m1=n(RVN["t_melt_median_s"], 1), r0=n(RVO["range_median_m"]), r1=n(RVN["range_median_m"]),
              dr=n(100 * (1 - RVN["range_median_m"] / RVO["range_median_m"]), 0), pk=pc(RVN["P_safe"], 1))))
add(("table", "Table @T:pt@. Saturation pressure of steam against approximate rated working pressure of Group 1.1 carbon-steel flanges (bar; rounded; verify against the current edition).", ["Temperature (°C)", "Saturation pressure (bar)", "Class 150 rating (bar)", "Class 300 rating (bar)"], rows8, [1.0, 1.2, 1.2, 1.2]))
add(("fig", "Fig18_pressure_temperature.png", "Fig. @F:pt@. Saturation pressure of steam (IAPWS-IF97) against the approximate pressure ratings of Class 150 and Class 300 flanges; dotted lines: the model's 198 °C and the Class 150 limit.", 4.2))

add(("h2", "6.9 Constrained design search and Pareto set"))
DI, DD = DES["by_melt"]["instant removal"], DES["by_melt"]["dynamic film"]
rows9 = []
for lab, dd in (("instant removal", DI), ("dynamic film", DD)):
    for m_, d in dd["best_by_mission"].items():
        rows9.append([lab, m_, "evacuated" if d["vac"] else "atmospheric", n(d["t_a_mm"]), n(d["v_set"], 2), n(d["hull_od_mm"]), pc(d["P_safe"], 1), n(d["range_median_m"], 1), n(d["steam_kg_per_m"], 2), n(d["energy_Wh"])])
add(("p", fmt("The constrained problem of Eq. (9) was evaluated on a grid of <<nd>> designs for each melt-removal assumption (aerogel 10–60 mm, two jackets, missions of 30, 45, 60 and 90 min, set-points of 0.05, 0.10 and 0.20 m/s). The hull constraint removes the thicknesses above 40 mm in a 12 in bore and the thermal constraint removes the thinner "
              "and the longer-mission designs; <<f1>> designs are feasible with instant removal and <<f2>> with the dynamic film. With instant removal the best feasible design is a <<b1>> mm <<j1>> jacket on a <<m1>> min mission at <<v1>> m/s, with a median range of <<r1>> m (Table @T:design@). With the dynamic film the feasible designs span only <<s0>> to <<s1>> m, the best is <<r2>> m, "
              "and the set-point does not matter because the thermally limited speed is below it. The Pareto set (<<p1>> and <<p2>> designs; Fig. @F:pareto@) is a trade between the range, the thermal probability and the hull size; the melting steam per metre is a property of the deposit and varies by only a few percent across the designs, "
              "so it does not trade off against them. The conclusion is that no choice of the thermal-protection variables restores the range lost to the film: the range is bounded by the melt model, not by the design variables.",
              nd=n(DES["n_designs"] // 2), f1=n(DI["n_feasible"]), f2=n(DD["n_feasible"]), b1=n(DI["best_feasible"]["t_a_mm"]), j1="evacuated" if DI["best_feasible"]["vac"] else "atmospheric", m1=n(DI["best_feasible"]["mission_min"]), v1=n(DI["best_feasible"]["v_set"], 2),
              r1=n(DI["best_feasible"]["range_median_m"]), s0=n(DD["range_span"][0]), s1=n(DD["range_span"][1]), r2=n(DD["best_feasible"]["range_median_m"]), p1=n(DI["n_pareto"]), p2=n(DD["n_pareto"]))))
add(("table", "Table @T:design@. Best feasible design for each mission length (constraints of Eq. 9; median range, melting steam per metre and battery energy at the median heat generation).",
     ["Melt removal", "Mission (min)", "Jacket", "Aerogel (mm)", "Set-point (m/s)", "Hull OD (mm)", "P(≤ 55 °C)", "Median range (m)", "Steam (kg/m)", "Energy (Wh)"], rows9, [1.1, 0.6, 0.9, 0.7, 0.7, 0.7, 0.8, 0.8, 0.7, 0.7]))
add(("fig", "Fig16_design_pareto.png", "Fig. @F:pareto@. Design search: median range against the thermal probability for (a) instant melt removal and (b) the dynamic film (colour: hull diameter; circles: Pareto set; grey: infeasible). (c) The thermal constraint against aerogel thickness.", 6.5))

add(("h2", "6.10 Surge on blockage release"))
add(("fig", "Fig9_anti_dieseling.png", "Fig. @F:surge@. Speed transient for a nominal 3 bar break-through (left) and Monte Carlo exceedance of the peak speed (right), first suite.", 6.3))
OM = BY["original_model"]; G7 = BY["general"][-1]
rows6 = [["Passive pig", n(CP["vpk_median"], 2), pc(CP["P_vpk_gt_1"], 0), pc(CP["P_vpk_gt_2"], 0), "first suite"],
         ["Crawler, braking only", n(CR["vpk_median"], 2), pc(CR["P_vpk_gt_1"], 0), pc(CR["P_vpk_gt_2"], 0), "first suite"],
         ["Crawler + relief as force factor β", n(CL["vpk_median"], 2), pc(CL["P_vpk_gt_1"], 0), pc(CL["P_vpk_gt_2"], 0), "first suite"]]
for g in BY["general"][2:]:
    rows6.append(["Crawler + orifice bypass %s cm²" % n(g["Ab_cm2"]), n(g["vpk_median"], 2), pc(g["P_gt_1"], 0), pc(g["P_gt_2"], 0), "this paper"])
vt = BY["vent_time_median_ms"]
add(("p", fmt("In the first suite the pressure force of a 3 bar break-through on a 12 in bore, $A\\,\\Delta P$ ≈ 21 kN, exceeds the 2.5 kN braking authority by about a factor of nine, so braking alone changes the median peak speed only from <<p0>> to <<p1>> m/s "
              "(Table @T:surge@, Fig. @F:surge@). Treating the bypass relief as a force factor $\\beta$, the median peak falls to <<p2>> m/s. Venting the gas pocket through an orifice (Eq. 7) gives a smaller benefit: with 80 cm² of bypass area, 11% of the bore, the median "
              "peak is <<o80>> m/s, and even with 320 cm², 45% of the bore, it is <<o320>> m/s with <<o2>> of the releases above 2 m/s, against <<f2>> in the force-factor model. The reason is a mismatch of time scales. The tool reaches 1 m/s in "
              "<<ta>> ms (5th percentile <<ta5>> ms), whereas a fully open bypass of 80 cm² needs <<v1>> ms to halve the differential across a 1 m³ pocket (<<v03>> ms for 0.3 m³, <<v10>> ms for 10 m³), and a valve lag of 5 to 30 ms adds to that. The relief therefore "
              "limits the duration of the surge, bringing the speed back to the set-point within about 0.3 s for 80 cm² (Fig. @F:bypass@b), but not its first peak. A bypass that is closed until the differential reaches the break-through value cannot arrest the "
              "impulse. The design alternative is a bypass that is already open during the stall, so that the pocket never charges: it holds a differential of 0.5 bar at 18 bar upstream if its area passes the supply flow, which requires <<h1>> cm² for 0.03 m³/s, <<h2>> cm² for 0.1 m³/s and "
              "<<h3>> cm² for 0.3 m³/s (assumed methane-like gas; Fig. @F:bypass@a). The price is that the differential that melts or breaks the deposit is then limited as well, so the deposit must be freed thermally rather than by pressure.",
              p0=n(CP["vpk_median"], 1), p1=n(CR["vpk_median"], 1), p2=n(CL["vpk_median"], 1), o80=n([g for g in BY["general"] if g["Ab_cm2"] == 80.0][0]["vpk_median"], 1), o320=n(G7["vpk_median"], 1), o2=pc(G7["P_gt_2"], 0), f2=pc(CL["P_vpk_gt_2"], 0),
              ta=n(BY["t_accel_1ms_median_ms"]), ta5=n(BY["t_accel_1ms_p05_ms"]), v1=n(vt["1.0"]["80.0"]), v03=n(vt["0.3"]["80.0"]), v10=n(vt["10.0"]["80.0"]), h1=n(BY["hold_area_cm2"][1]["area_cm2"]), h2=n(BY["hold_area_cm2"][2]["area_cm2"]), h3=n(BY["hold_area_cm2"][3]["area_cm2"]))))
add(("table", "Table @T:surge@. Peak speed after break-through (12 in bore; same draws; N = %s)." % n(R["N_surge"]), ["Configuration", "Median peak (m/s)", "P(> 1 m/s)", "P(> 2 m/s)", "Model"], rows6, [2.2, 1.1, 1.0, 1.0, 1.0]))
add(("fig", "Fig10_bypass.png", "Fig. @F:bypass@. (a) Probability of a peak speed above 1 m/s against the bypass area for four gas-pocket volumes (dotted: the first suite's force-factor model). (b) Speed after a nominal 3 bar break-through with a 1 m³ pocket.", 6.3))

add(("h2", "6.11 Steam budget"))
S12 = STM[12]
rows7 = [[str(k), n(STM[k]["steel_kg_per_m"]), n(STM[k]["clean_kg_per_m"], 2), n(STM[k]["wall_kg_per_m_25C"], 2), n(STM[k]["total_kg_per_m_25C"], 2), n(STM[k]["wall_kg_per_m_0C"], 2)] for k in (4, 6, 8, 10, 12, 14, 16)]
add(("p", fmt("Melting the deposit uses a median of <<c>> kg of steam per metre in a 12 in pipe (first suite). If the steam reaches the tool through the pipe behind it, the steel wall of the whole line must also be heated from 25 °C to the saturation temperature: for standard-wall "
              "12 in pipe of <<m>> kg/m this takes <<w>> kg of steam per metre, <<ratio>> times the melting steam, and the total is <<t>> kg/m, or about <<t>> t of steam (and of condensate) for a 1 km line, against the <<c1>> t that the melting alone would suggest (Table @T:steam@, Fig. @F:steam@). "
              "A pipe at 0 °C needs <<w0>> kg/m for the wall. The wall-heating term is a lower bound, because it ignores heat lost from the pipe to its surroundings during the intervention. A steam hose carried inside the pipe avoids heating the wall but adds "
              "tether drag over up to 1 km and a second line at the steam temperature to the tool. Either way the water use is larger than the melting alone suggests, which matters because reduced water use is one of the brief's nice-to-have criteria.",
              c=n(S12["clean_kg_per_m"], 2), m=n(S12["steel_kg_per_m"]), w=n(S12["wall_kg_per_m_25C"], 1), ratio=n(S12["wall_ratio"], 1), t=n(S12["total_kg_per_m_25C"], 1), c1=n(S12["clean_kg_per_m"], 1), w0=n(S12["wall_kg_per_m_0C"], 1))))
add(("table", "Table @T:steam@. Steam per metre of line: melting (median) and heating the pipe wall (standard wall, 25 °C start; last column 0 °C start).",
     ["NPS (in)", "Steel (kg/m)", "Melting (kg/m)", "Wall heating (kg/m)", "Total (kg/m)", "Wall heating from 0 °C (kg/m)"], rows7, [0.7, 0.9, 1.0, 1.1, 0.9, 1.3]))
add(("fig", "Fig11_steam_budget.png", "Fig. @F:steam@. Steam per metre of line against nominal pipe size: melting the deposit and heating the pipe wall.", 4.4))
