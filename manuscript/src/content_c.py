# -*- coding: utf-8 -*-
"""Manuscript, part C: discussion, conclusions, declarations, references (Sections 7-8)."""
from common import *

c3 = COV["45 min atmospheric|ablation|300"]; c10 = COV["45 min atmospheric|ablation|1000"]
S12 = STM[12]; vt = BY["vent_time_median_ms"]

add(("h1", "7. Discussion"))
add(("h2", "7.1 What the concept has to demonstrate"))
add(("p", fmt("The brief states six must-have requirements [@YPF2026]. Table 8 sets what this study can and cannot say about each. The strongest statement is negative and quantitative: with the assumptions of the first design, the concept does not by itself meet the length, "
              "diameter, temperature and access conditions of the brief, and its reach is governed by a quantity, the retained melt film, that nobody has measured. The strongest positive statement is narrower: for a 12 in pipe at 25 °C, 40 mm of "
              "aerogel keeps the pack below 55 °C for 45 min in <<p>> of the draws, so the thermal shield is not the first obstacle, provided the pipe is cool.", p=pc(A_ATM["P_safe"], 0))))
add(("table", "Table 8. Requirements of the published brief [@YPF2026] and the evidence of this study.",
     ["Requirement", "What the simulation shows", "What is missing"],
     [["Effective removal, with evidence and limits", "Range of %s m (instant melt removal) falling to %s m (0.2 mm retained film) and %s m (no drainage) per 45 min deployment" % (n(BB["range_median_m"]), n(FR[0.2]["range_median_m"]), n(ND["range_nodrain_median_m"], 1)),
       "Measured melt removal on steel; deposit composition (solid fraction); scale and sediment are not melted"],
      ["Compatibility with operating conditions, connections and recovery", "No single 45 min deployment reaches 300 m; a 1 km line needs a median of %s deployments; hull does not fit below 8 in" % n(c10["n_dep_median"]),
       "A tool-recovery route through a flow-aligned connection; steam path; bends, valves and diameter changes"],
      ["Operational safety and integrity", "Surge peak not arrested by a bypass that is closed at the stall (tool at 1 m/s in %s ms); pack margin falls above 35 °C" % n(BY["t_accel_1ms_median_ms"]),
       "Explosive-atmosphere protection, steam pressure against the line rating, seal elastomers in hydrocarbon and steam, cell-level battery analysis"],
      ["Limited disruption, with a full timeline", "Active cleaning is %s to %s of the intervention (assumed logistics); steam is %s kg/m including the wall" % (pc(c3["active_fraction_median"], 0), pc(c10["active_fraction_median"], 0), n(S12["total_kg_per_m_25C"], 1)),
       "Real preparation, isolation and return-to-service durations"],
      ["Detailed proof-of-concept plan", "Section 7.2 lists the tests, in order of how much each one changes the answer", "Costs and schedule are not estimated here"],
      ["Credibility of the solver", "Computational study only; the author is an independent researcher with no hardware or field experience in pipeline cleaning", "A partner with pipeline-intervention experience"]], [1.3, 2.0, 1.7]))
add(("h2", "7.2 Measurements that matter, in order"))
add(("p", "The Monte Carlo study shows where a measurement changes the conclusion most. First, melt removal: a bench test in which paraffin of known melting point on a steel wall is melted by condensing steam, with the retained film thickness and the heat flux measured. "
          "It decides whether the range is of the order of 100 m or of a few metres (Section 6.3). Second, the thermal soak of a sealed aerogel module with a dissipating pack in saturated steam, at several starting temperatures, which would replace the assumed "
          "heat generation and bridge conductance and settle the 55 °C margin (Sections 6.1 and 6.5). Third, a steam-delivery test in a short pipe loop, which measures the condensate and wall-heating mass per metre and shows how steam reaches the tool (Section 6.7). "
          "Fourth, a bypass and seal rig for the stall and release, with the valve open before the stall, which measures the differential that can be held and the first-peak speed (Section 6.6). Fifth, characterization of the deposits that the line actually "
          "contains, in particular the fraction that does not melt: steam alone does not remove scale or sediment, and the model does not represent the mechanical removal of such solids by the skirt and tracks."))
add(("h2", "7.3 Limitations"))
add(("p", "(i) All inputs are assumed, and the retained film thickness, the liquid conductivity, the heat-coupling fraction and the logistics durations are the least constrained. (ii) The conduction model is radial; axial conduction, end caps and track mounts enter "
          "through a bridge fraction. (iii) The Nusselt correlation is used outside its derivation range and the steam is taken at rest. (iv) The surge model is reduced-order: a gas pocket vented to a constant downstream pressure, with a quadratic drag standing "
          "for the compressibility downstream; liquid-filled lines, which would surge differently, are not modelled. (v) The pack is lumped, with no cell-level thermal runaway analysis. (vi) The steam delivery path, the recovery of the tool, bends, valves "
          "and diameter changes are not modelled. (vii) Deposits are meltable paraffin only. (viii) The comparison with ice-slurry pigging [@Quarini2002;@Quarini2010], which the brief names as of particular interest, is not made. The results are a design-screening tool "
          "and not a validated prediction."))

add(("h1", "8. Conclusions"))
add(("num", "The thermal shield is credible but depends on a cool start. With 40 mm of atmospheric aerogel the pack stays at or below 55 °C for 45 min in %s of the draws in a 25 °C pipe, and the probability falls to %s at 35 °C and %s at 45 °C; an evacuated jacket helps little at 45 °C (%s)." % (pc(A_ATM["P_safe"], 1), pc(ENV[35.0]["P_safe_atm"], 0), pc(ENV[45.0]["P_safe_atm"], 0), pc(ENV[45.0]["P_safe_vac"], 0))))
add(("num", "The reach per deployment is governed by whether molten deposit leaves the surface. The median range is %s m with instant removal, %s m with a retained film of 0.2 mm and %s m if none drains; a film of %s µm already brings the median below 100 m. The retained film should be measured before any reach is claimed." % (n(BB["range_median_m"]), n(FR[0.2]["range_median_m"]), n(ND["range_nodrain_median_m"], 1), n(F["s_median_below_100m_mm"] * 1000))))
add(("num", "Against the brief the concept fails on length, diameter and temperature as modelled: no 45 min deployment reaches 300 m, a 1 km line needs a median of %s deployments, the hull does not fit pipes below 8 in, and heating the pipe wall makes the steam budget %s times the melting steam." % (n(c10["n_dep_median"]), n(S12["wall_ratio"], 1))))
add(("num", "A bypass valve that is closed at the stall cannot arrest the first surge peak, because the tool reaches 1 m/s in about %s ms while a fully open 80 cm² bypass needs about %s ms to halve the differential over a 1 m³ gas pocket; a bypass that is open during the stall, sized to the supply flow, is the design alternative." % (n(BY["t_accel_1ms_median_ms"]), n(vt["1.0"]["80.0"]))))
add(("num", "These are the results of assumed inputs. Their value is to rank the measurements: melt removal, a thermal soak in steam, steam delivery and a bypass rig, then deposit characterization."))

add(("h1", "Declarations"))
add(("p0", "Author contributions (CRediT): Leon Sandler, sole author: conceptualization, methodology, software, formal analysis, writing – original draft, writing – review and editing."))
add(("p0", "Funding: this work received no external funding."))
add(("p0", "Competing interests: the author declares no competing interests. The concept was prepared as a response to a public scouting challenge [@YPF2026]; the author has no financial relationship with its seeker or platform."))
add(("p0", "Data and code availability: the code, the data of every figure and table and the manuscript are archived at https://doi.org/%s (software, all versions) and https://doi.org/%s (manuscript, all versions), and are available at %s. "
           "One command per script regenerates every number and figure; the results quoted in the text are read from the JSON files that the scripts write." % (DOIS["code_concept"], DOIS["paper_concept"], GITHUB)))
add(("p0", "Use of generative AI: a generative AI tool (Claude, Anthropic) assisted with code development, numerical experiments, drafting and editing. The author checked all of it and takes full responsibility for the content."))
add(("refs",))
