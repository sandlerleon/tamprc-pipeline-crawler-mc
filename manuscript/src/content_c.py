# -*- coding: utf-8 -*-
"""Manuscript, part C: discussion, conclusions, declarations, references (Sections 7-8)."""
import math
from common import *

c3 = COV["45 min atmospheric|ablation|300"]; c10 = COV["45 min atmospheric|ablation|1000"]
S12 = STM[12]; vt = BY["vent_time_median_ms"]
RV = PT["revised_envelope"]; DI, DD = DES["by_melt"]["instant removal"], DES["by_melt"]["dynamic film"]

add(("h1", "7. Discussion"))
add(("h2", "7.1 A regime map for thermal cleaning with a retained melt film"))
add(("p", fmt("The crawler is the application; the transferable result is the role of the dimensionless group $\\Pi_f=hs/k_l$. For $\\Pi_f\\ll1$ the melt leaves the surface, the heat flux is that of the condensate film, and the speed is set by the energy needed to melt the deposit "
              "(here <<r0>> m per 45 min, capped by the set-point in <<cap>> of draws). For $\\Pi_f\\gtrsim1$ the liquid layer controls the flux, the speed falls as $1/(1+\\Pi_f)$, and the condensation correlation becomes irrelevant (Section 6.3). The dynamic balance of Eq. (5) places the median "
              "draw at $\\Pi_f\\approx<<pi>>$, well inside the second regime, because gravity drains a viscous film slowly; a range of 100 m needs $\\Pi_f\\lesssim<<p100>>$. Any thermal cleaning concept in which molten deposit must leave a surface that the heat reaches through "
              "that deposit is in this situation, and the retained film, not the heat source, is what a test should measure. The group can be reduced only by removing the melt as it forms: by mechanical scraping at the melt front, by a flow that shears the film, or by orienting the heating so that "
              "the melt falls away. These are design features the present model does not contain and the proposed bench test (Section 7.2) would evaluate.", r0=n(BB["range_median_m"]), cap=pc(UNC["P_range_at_cap"], 0), pi=n(DY["steady_film_median_params"]["Pi_f"], 1), p100=n(DY["Pi_f_for_100m_median"], 1))))
add(("h2", "7.2 What the concept has to demonstrate"))
add(("p", fmt("The brief states six must-have requirements [@YPF2026]. Table @T:reqs@ sets what this study can and cannot say about each. The strongest statement is negative and quantitative: with the assumptions of the first design, the concept does not by itself meet the length, "
              "diameter, temperature and access conditions of the brief, and its reach is governed by a quantity, the retained melt film, that nobody has measured. The strongest positive statement is narrower: for a 12 in pipe at 25 °C, 40 mm of "
              "aerogel keeps the pack below 55 °C for 45 min in <<p>> of the draws under the assumed distributions, so the thermal shield is not the first obstacle, provided the pipe is cool. "
              "The measurements that would change the conclusion most, in order, are: the retained film and the heat flux when condensing steam melts paraffin of known melting point on a steel wall (it decides whether the range is of order 10 m or 100 m); "
              "the thermal soak of a sealed aerogel module with a dissipating pack in saturated steam at several starting temperatures (it replaces the assumed heat generation and bridge conductance); a steam-delivery test in a short pipe loop (condensate and wall-heating mass per metre); "
              "a bypass and seal rig for the stall and release, with the valve open before the stall; and the characterization of the deposits that a line actually contains, in particular the fraction that does not melt.", p=pc(A_ATM["P_safe"], 0))))
add(("table", "Table @T:reqs@. Requirements of the published brief [@YPF2026] and the evidence of this study.",
     ["Requirement", "What the simulation shows", "What is missing"],
     [["Effective removal, with evidence and limits", "Range per 45 min deployment: %s m (instant melt removal), %s m (dynamic film), %s m (no drainage); the film decides" % (n(BB["range_median_m"]), n(DY["baseline"]["range_median_m"]), n(ND["range_nodrain_median_m"], 1)),
       "Measured melt removal on steel; deposit composition (solid fraction); scale and sediment are not melted"],
      ["Compatibility with operating conditions, connections and recovery", "No single 45 min deployment reaches 300 m at the set-point; a 1 km line needs a median of %s deployments; hull does not fit below 8 in" % n(c10["n_dep_median"]),
       "A tool-recovery route through a flow-aligned connection; steam path; bends, valves and diameter changes"],
      ["Operational safety and integrity", "Surge peak not arrested by a bypass closed at the stall (tool at 1 m/s in %s ms); pack margin falls above 35 °C; steam at 198 °C exceeds the Class 150 rating, revised envelope %s °C" % (n(BY["t_accel_1ms_median_ms"]), n(PT["Tmax_class150_C"] - 3)),
       "Explosive-atmosphere protection, seal elastomers in hydrocarbon and steam, cell-level battery analysis, stalled-tool recovery"],
      ["Limited disruption, with a full timeline", "Active cleaning is %s to %s of the intervention (assumed logistics); steam is %s kg/m including the wall" % (pc(c3["active_fraction_median"], 0), pc(c10["active_fraction_median"], 0), n(S12["total_kg_per_m_25C"], 1)),
       "Real preparation, isolation and return-to-service durations"],
      ["Detailed proof-of-concept plan", "Section 7.2 lists the tests, in order of how much each one changes the answer", "Costs and schedule are not estimated here"],
      ["Credibility of the solver", "Computational study only; the author is an independent researcher with no hardware or field experience in pipeline cleaning", "A partner with pipeline-intervention experience"]], [1.3, 2.0, 1.7]))
add(("h2", "7.3 Safety, condensate and recovery"))
add(("p", fmt("Three engineering conditions that the thermal model does not contain are part of the feasibility envelope. (i) Pressure: the steam temperature must be compatible with the pressure rating of the line, flanges, seals and elastomers; at Class 150 the limit is about <<tm>> °C (Section 6.8), "
              "and a lower-rated line, a vacuum-jacket seal or a hydrocarbon-swollen elastomer would lower it further. (ii) Explosive atmosphere: electrical equipment in a hydrocarbon line needs a protection concept suitable for the zone [@IEC60079], "
              "which for a sealed pressure vessel means certified enclosures, cable entries and battery, and a purge of the line before steam is admitted so that the steam does not meet an explosive mixture. (iii) Condensate and residue: melting and wall heating produce about <<cond>> m³ of condensate per kilometre in a 12 in line, "
              "mixed with molten deposit and hydrocarbon, which must be collected and separated at the connection through which the tool is recovered, and treated as contaminated material. A stalled tool is the principal recovery case: at a residual differential of 0.5 bar on a 12 in bore the force to pull it back is about <<pull>> kN "
              "including seal friction, which needs a tether or a reverse differential across the skirt, and a bypass that is open during the stall (Section 6.10) both reduces that force and prevents the surge on release.",
              tm=n(PT["Tmax_class150_C"]), cond=n(S12["total_kg_per_m_25C"], 1), pull=n(0.5e5 * math.pi / 4 * 0.30 ** 2 / 1e3 + 0.4, 1))))
add(("h2", "7.4 Limitations"))
add(("p", "(i) All inputs are assumed, and the retained-film drainage parameters, the liquid conductivity, the heat-coupling fraction and the logistics durations are the least constrained. (ii) The coupled model is not validated against experiment; the benchmarks of Section 5.2 verify the numerical solutions and quantify the error of the quasi-steady formulas. "
          "(iii) The conduction model is radial; axial conduction, end caps and track mounts enter through a bridge fraction. (iv) The condensation correlations are used outside their derivation ranges and the steam is taken at rest; the effect of steam shear and of a defined steam path is not modelled. "
          "(v) The surge model is reduced-order: a gas pocket vented to a constant downstream pressure, with a quadratic drag standing for the compressibility downstream; liquid-filled lines, which would surge differently, are not modelled, and no safe speed is justified. "
          "(vi) The pack is lumped, with no cell-level thermal runaway analysis. (vii) The steam delivery path, the recovery of the tool, bends, valves and diameter changes are not modelled. (viii) Deposits are meltable paraffin only. "
          "(ix) The comparison with ice-slurry pigging [@Quarini2002;@Quarini2010], which the brief names as of particular interest, is not made. The results are a design-screening tool and not a validated prediction."))

add(("h1", "8. Conclusions"))
add(("num", fmt("Heat transfer through a retained melt film governs the reach. The film adds the dimensionless resistance $\\Pi_f=hs/k_l$ to the condensate film; a range of 100 m needs $\\Pi_f\\lesssim<<p100>>$. A dynamic balance of melt production and gravity drainage predicts a film of <<s>> mm and a median range of <<rd>> m per 45 min deployment, "
                 "against <<r0>> m if the melt leaves at once and <<rn>> m if none drains; the prediction rests on assumed drainage parameters (median range <<lo>> to <<hi>> m across a factor-of-four change of the drainage group).", p100=n(DY["Pi_f_for_100m_median"], 1), s=n(DY["baseline"]["s_end_median_mm"], 2),
                 rd=n(DY["baseline"]["range_median_m"]), r0=n(BB["range_median_m"]), rn=n(ND["range_nodrain_median_m"], 1), lo=n(DY["sensitivity"]["viscosity x4"]["range_median_m"]), hi=n(DY["sensitivity"]["viscosity x0.25"]["range_median_m"]))))
add(("num", fmt("The numerical solutions are correct for their equations, and the formulas have known errors. The enthalpy solver reproduces the Neumann solution to <<en>>%, the instant-removal formula agrees with it within <<ea>>%, and the no-drainage formula is <<en1>>% too fast; "
                 "the coupled model has no experimental validation. The condensation correlation changes the instant-removal range by <<ch>>% (Chato) or <<ck>>% (non-condensable limit) and matters little once a film is present.",
                 en=n(100 * abs(NM["rel_err"]), 3) if False else n(100 * abs(BSF["neumann"]["rel_err"]), 3), ea=n(100 * max(abs(r["err_ablation"]) for r in BSF["convective"]), 1), en1=n(100 * abs(sum(r["err_nodrain"] for r in BSF["convective"]) / len(BSF["convective"])), 0),
                 ch=n(100 * (1 - HM["chato"]["range_median_m_s0"] / HM["nusselt"]["range_median_m_s0"])), ck=n(100 * (1 - HM["chato_ncg"]["range_median_m_s0"] / HM["nusselt"]["range_median_m_s0"])))))
add(("num", fmt("The thermal shield works in a cool pipe and fails in a warm one. With 40 mm of atmospheric aerogel the pack stays at or below 55 °C for 45 min in <<p>> of the draws at 25 °C, <<p35>> at 35 °C and <<p45>> at 45 °C. Sobol indices attribute the pack temperature almost entirely to the starting temperature and the heat generation, "
                 "and a positive correlation between them lowers the probability. These are model probabilities, not field reliabilities.", p=pc(A_ATM["P_safe"], 1), p35=pc(ENV[35.0]["P_safe_atm"], 0), p45=pc(ENV[45.0]["P_safe_atm"], 0))))
add(("num", fmt("Against the brief the concept as designed fails on length, diameter and temperature. No 45 min deployment reaches 300 m at the 0.10 m/s set-point (a cap, not a thermal limit); a 1 km line needs a median of <<n1>> deployments; the hull does not fit pipes below 8 in; and heating the pipe wall makes the steam budget <<w>> times the melting steam. "
                 "A constrained design search shows that no thermal-protection choice restores the range lost to the film (best feasible <<b1>> m with instant removal, <<b2>> m with the dynamic film).", n1=n(c10["n_dep_median"]), w=n(S12["wall_ratio"], 1), b1=n(DI["best_feasible"]["range_median_m"]), b2=n(DD["best_feasible"]["range_median_m"]))))
add(("num", fmt("The steam pressure is a constraint, not a reason to reject the concept. Steam at 198 °C (<<ps>> bar) exceeds the Class 150 rating, whose limit is about <<tm>> °C; a revised envelope at <<tr>> °C costs <<dr>>% of the range and leaves the pack probability unchanged.",
                 ps=n(PT["psat_198C_bar"], 1), tm=n(PT["Tmax_class150_C"]), tr=n(PT["Tmax_class150_C"] - 3), dr=n(100 * (1 - RV["revised, Class 150 limit"]["range_median_m"] / RV["original 198 C"]["range_median_m"]), 0))))
add(("num", fmt("A bypass that is closed at the stall cannot arrest the first surge peak, because the tool reaches 1 m/s in about <<ta>> ms while a fully open 80 cm² bypass needs about <<v1>> ms to halve the differential over a 1 m³ gas pocket; a bypass that is open during the stall, sized to the supply flow, is the design alternative.",
                 ta=n(BY["t_accel_1ms_median_ms"]), v1=n(vt["1.0"]["80.0"]))))
add(("num", "These are the results of assumed inputs, and the largest uncertainty is the model form, not the parameters within a model. Their value is to identify what to measure first: melt removal on steel, a thermal soak in steam, steam delivery and a bypass rig, then deposit characterization."))

add(("h1", "Declarations"))
add(("p0", "Author contributions (CRediT): Leon Sandler, sole author: conceptualization, methodology, software, formal analysis, writing – original draft, writing – review and editing."))
add(("p0", "Funding: this work received no external funding."))
add(("p0", "Competing interests: the author declares no competing interests. The concept was prepared as a response to a public scouting challenge [@YPF2026]; the author has no financial relationship with its seeker or platform."))
add(("p0", "Data and code availability: the code, the data of every figure and table and the manuscript are archived at https://doi.org/%s (software, all versions) and https://doi.org/%s (manuscript, all versions), and are available at %s. "
           "One command per script regenerates every number and figure; the results quoted in the text are read from the JSON files that the scripts write." % (DOIS["code_concept"], DOIS["paper_concept"], GITHUB)))
add(("p0", "Use of generative AI: a generative AI tool (Claude, Anthropic) assisted with code development, numerical experiments, drafting and editing. The author checked all of it and takes full responsibility for the content."))
add(("refs",))
