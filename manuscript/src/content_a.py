# -*- coding: utf-8 -*-
"""Manuscript, part A: Introduction, concept and operating envelope, model, methodology (Sections 1-4)."""
from common import *

# ============================================================================================ 1 Introduction
add(("h1", "1. Introduction"))
add(("p", "Wax, asphaltene, scale and sediment deposits narrow the bore of upstream hydrocarbon pipelines, raise the pressure loss and degrade the product. Wax deposition has been studied extensively [@Aiyejina2011;@Huang2016], and the usual "
          "remedies are high-volume flushing, chemical treatment and mechanical pigging. Each has a known cost: abrasive or mechanical cleaning can wear the wall and generates solid waste, and a passive pig can stall behind a heavy deposit "
          "and then surge, because the gas stored behind it expands when the blockage lets go [@Kim2022]; bypass valves that vent the gas are used to control the speed of pigs in gas lines [@Nguyen2001;@Zhu2014]. Ice-slurry pigging has been developed for water mains and process plant [@Quarini2002;@Quarini2010]. A scouting challenge "
          "published by an energy company has recently asked for cleaning solutions for pipelines of 4 to 16 inches and up to 1 km that have no dedicated launcher or receiver and can be reached only through a connection aligned with the flow [@YPF2026]."))
add(("p", "Thermal mobilization with steam is an obvious alternative to abrasion, because condensation delivers a large heat flux at a modest temperature difference. It raises three engineering questions that this paper tests for one concept, "
          "a tracked, self-propelled crawler with an elastomeric sealing skirt that melts deposit with steam ahead of it (the Thermally Assisted Motorized Pipeline Remediation Crawler, TAMPRC). First, can the battery and electronics of a tool that "
          "sits in saturated steam near 200 °C be kept below a safe temperature for a useful mission? Second, how fast can the deposit be melted, and therefore how far can the tool clean in one deployment? Third, can the on-board drive control the surge "
          "when a blockage releases, or is a pressure-relief path needed? A fourth question comes from the published brief: does the concept fit the bore, the length, the ambient temperature and the access that the brief states?"))
add(("p", "The paper evaluates these questions with a Monte Carlo model, organized as a single seeded script in the spirit of the MyUncle maintenance-lattice framework [@MyUncle] and propagating assumed input distributions [@Metropolis1949]. "
          "The first suite (thermal shield, melt kinetics, surge, maintenance lattice) was written as a design-screening study and is retained unchanged in the repository. This paper re-examines its assumptions against the brief and adds five "
          "mechanisms that can each be switched off: a retained melt film that resists heat flow, a pipe-length and logistics model, a diameter and ambient-temperature study, an orifice model of the bypass relief that vents the upstream gas, and a steam "
          "budget that includes heating the pipe wall. With all of them off the extended model reproduces the first suite draw for draw (Section 5). The contribution that can be defended is a set of quantified limits of the concept, and a list of "
          "the measurements that would remove them, not a predicted performance: all inputs are assumed, and no measurement of these deposits, steam conditions or tool was available."))

# ============================================================================================ 2 Concept and envelope
add(("h1", "2. Concept and operating envelope"))
add(("p", "The tool (Fig. 1) is a crawler of about 120 kg with cleated tracks and an elastomeric sealing skirt. Steam condenses on the deposit face ahead of the skirt, delivers latent heat and melts the deposit in place, and the skirt sweeps the "
          "liquefied residue forward. The battery pack, motors and electronics sit in a sealed vessel inside a concentric stack of aluminium shell, silica aerogel [@Koebel2012] and titanium hull; an evacuated (vacuum-jacketed) variant is also evaluated. "
          "Brushless motors drive the tracks and act as regenerative brakes against a speed set-point of 0.10 m/s, and a seal-differential bypass valve is added to relieve the pressure when a blockage releases."))
add(("fig", "Fig1_cross_section.png", "Fig. 1. Cross-section of the crawler hull (not to scale): pack, aluminium shell, silica aerogel, titanium hull and the steam film.", 2.6))
add(("p", "Table 1 lists the operating envelope that the brief states [@YPF2026] next to what the modelled tool assumes. The brief asks for evidence of removal, compatibility with the connection and recovery arrangements, safety, limited disruption "
          "and a proof-of-concept plan, and it excludes purely conceptual proposals and solutions that depend on permanent pigging facilities. The tool modelled here is at concept stage (technology readiness level 2 to 3), below the 4 to 6 that the brief "
          "requires, and this paper does not claim otherwise."))
add(("table", "Table 1. Operating envelope in the published brief and in the model.", ["Item", "Brief [@YPF2026]", "Modelled tool"],
     [["Pipe diameter", "4 to 16 in", "12 in (0.30 m bore) baseline; 4 to 16 in studied in Section 6.5"],
      ["Pipe length", "about 0.3 m to 1 km", "one 45 min deployment; 0.3 m to 1 km studied in Section 6.4"],
      ["Material", "carbon steel", "carbon steel, standard wall"],
      ["Deposits", "paraffin, sediment, scale, sludge, residue", "meltable paraffin only (melt point 58 ± 8 °C); solids not modelled"],
      ["Access", "connection aligned with the flow; no fixed launcher or receiver", "not modelled; tool recovery and steam path are open design items"],
      ["Stages", "preparation, isolation, cleaning, residue collection, verification, return to service", "active cleaning and assumed logistics durations (Section 6.4)"],
      ["Readiness", "technology readiness level 4 to 6", "level 2 to 3 (simulation only)"]], [1.0, 2.0, 2.6]))
add(("p", "Two limitations of the concept are stated at the outset because they decide the interpretation of the results. First, the steam must reach a tool that is sealed against the deposit it is melting; this needs a defined forward path "
          "(a lance or bypass annulus) or a steam line behind the tool, and the latter heats the whole pipe wall (Section 6.7). Second, the electronics of a tool in a hydrocarbon line need equipment protection suitable for explosive atmospheres [@IEC60079], "
          "and the saturation pressure at 198 °C, 1.55 MPa, exceeds the pressure rating of a Class 150 carbon-steel flange at 200 °C, which is of the order of 14 bar [@ASMEB165]; neither point is modelled."))

# ============================================================================================ 3 Model
add(("h1", "3. Mathematical model"))
add(("h2", "3.1 Transient conduction in the composite wall"))
add(("p", "The radial temperature $T(r,t)$ in the composite wall (aluminium shell, silica aerogel, titanium hull) obeys one-dimensional cylindrical conduction,"))
add(("eq", r"\rho\,c_{p}(T)\,\frac{\partial T}{\partial t}=\frac{1}{r}\frac{\partial}{\partial r}\left[r\,k(T)\,\frac{\partial T}{\partial r}\right]", 1))
add(("p", "with density $\\rho$, specific heat $c_{p}$ and conductivity $k$. For atmospheric-pressure aerogel $k=k_{0}[1+\\alpha(T-25)]$ with $k_{0}=0.018$ W/m·K and a slope of $8\\times10^{-5}$ W/m·K$^{2}$; for the evacuated jacket "
          "$k=0.0040+2.5\\times10^{-5}(T-25)$ W/m·K. Both are multiplied by a lognormal factor for compaction, moisture and lot variation. The outer boundary exchanges heat with saturated steam through a film coefficient, the inner boundary "
          "with a lumped battery pack (heat capacity $m_{pack}c_{p}/L$ per unit length, source $P_{gen}/L$), and a parallel bridge conductance (tracks, end caps) equal to a fraction $\\phi\\sim U(0.05,0.30)$ of the nominal aerogel conductance joins "
          "hull and pack. The pack limit is $T_{crit}=55$ °C; this is an assumed design limit, conservative relative to the onset of self-heating reported for lithium-ion cells [@Feng2018], and no cell-level analysis is made. Eq. (1) is discretized by "
          "finite volumes (2 shell, 16 aerogel and 2 hull cells) and integrated with backward Euler at 10 s, with the conductivity lagged one step."))
add(("h2", "3.2 Film condensation"))
add(("p", "The condensation coefficient is the Nusselt film correlation [@Nusselt1916;@Incropera2007], adapted to a conduit of diameter $D$,"))
add(("eq", r"h=0.728\left[\frac{g\,\rho_{l}(\rho_{l}-\rho_{v})\,k_{l}^{3}\,h'_{fg}}{\mu_{l}\,D\,(T_{sat}-T_{w})}\right]^{1/4},\qquad h'_{fg}=h_{fg}+0.68\,c_{p,l}(T_{sat}-T_{w})", 2))
add(("p", "with saturated-water properties near 1.55 MPa. It was derived for outside horizontal tubes, so its use in a conduit is an assumption, covered by a lognormal multiplier ($\\sigma=0.15$) and a non-condensable-gas factor $U(0.5,1)$. "
          "It scales as $D^{-1/4}$, which the tests verify."))
add(("h2", "3.3 Deposit melting, and the retained melt film"))
add(("p", "A deposit of thickness $\\delta$ and melt point $T_{m}$ needs the energy per unit area $e=\\rho_{d}\\delta[L_{f}+c_{d}(T_{m}-T_{0})]$. The first suite assumed that molten deposit leaves the surface at once (ablation), so that the heat flux is "
          "that of the condensate film at the melt temperature, $q=h(T_{sat}-T_{m})$. A liquid layer that stays on the surface adds a conduction resistance in series. With a retained layer of thickness $s$ and liquid conductivity $k_{l}$, "
          "and a fraction $\\eta\\sim U(0.15,0.50)$ of the flux reaching the deposit,"))
add(("eq", r"q_{eff}=\eta\,\frac{T_{sat}-T_{m}}{1/h+s/k_{l}},\qquad t_{m}=\frac{e}{q_{eff}},\qquad v_{th}=\frac{L_{z}}{t_{m}},\qquad v=\min(v_{set},v_{th})", 3))
add(("p", "where $L_{z}\\sim U(0.3,0.8)$ m is the steam contact length and $v_{set}=0.10$ m/s. Setting $s=0$ recovers the first suite exactly. The opposite limit, in which no melt drains and the layer grows from 0 to $\\delta$, gives"))
add(("eq", r"t_{nd}=\frac{\rho_{d}[L_{f}+c_{d}(T_{m}-T_{0})]\,(\delta/h+\delta^{2}/2k_{l})}{\eta\,(T_{sat}-T_{m})}", 4))
add(("p", "The liquid conductivity is assumed ($k_{l}=0.15$ W/m·K). The cleaned range of a deployment is $v\\,\\min(t_{crit},t_{run})$, where $t_{crit}$ is the first time the pack reaches 55 °C and $t_{run}$ the mission length (45 min)."))
add(("h2", "3.4 Blockage release with an orifice bypass"))
add(("p", "From break-through the tool of mass $m$ obeys"))
add(("eq", r"m\,\frac{dv}{dt}=A\,\Delta P\,(1-\beta)-F_{f}-c_{d}v^{2}-F_{c}", 5))
add(("p", "with pipe area $A$, seal friction $F_{f}$, downstream drag $c_{d}$ and controller force $F_{c}$ (PI on speed, limited to the braking and traction authority). The first suite represented the bypass relief by a factor $\\beta\\to\\beta_{max}[1-0.5\\ \\mathrm{bar}/\\Delta P]$ "
          "(0.85 to 0.97) with a 5 to 30 ms lag, that is, as a force reduction without a flow. Here the upstream gas pocket (initial volume $V_{0}$, pressure $P_{0}=P_{d}+\\Delta P_{b}$) expands adiabatically as the tool advances a distance $x$ and "
          "loses its gas through the bypass,"))
add(("eq", r"P_{u}=P_{0}\left(\frac{\varphi V_{0}}{V_{0}+A\,x}\right)^{\gamma},\qquad \frac{d\varphi}{dt}=-\frac{\dot{m}_{b}}{m_{0}},\qquad \dot{m}_{b}=C_{d}A_{b}\,u\,P_{u}\sqrt{\frac{2\gamma}{(\gamma-1)RT}}\sqrt{r^{2/\gamma}-r^{(\gamma+1)/\gamma}}", 6))
add(("p", "where $\\varphi$ is the remaining gas fraction, $m_{0}=P_{0}V_{0}/RT$, $r=\\max(P_{d}/P_{u},r_{c})$ with $r_{c}$ the critical ratio (choked flow), $A_{b}$ the bypass flow area, $C_{d}=0.7$ and $u\\in[0,1]$ the valve opening, which follows "
          "the demand $(\\Delta P-0.5\\ \\mathrm{bar})/(0.5\\ \\mathrm{bar})$ with the same 5 to 30 ms lag. The gas is methane-like ($R=518$ J/kg·K, $T=300$ K, $\\gamma=1.3$, assumed) and the downstream pressure is held constant. With $A_{b}=0$ the "
          "model reduces to the first suite's crawler without relief, and with $\\varphi=1$ the pocket pressure is the same function of $x$."))
add(("h2", "3.5 Pipe length, logistics and steam budget"))
add(("p", "For a line of length $L$ and a deployment range $R_{dep}=v\\,t_{run}$, the number of deployments is the smallest integer not below $L/R_{dep}$, the active cleaning time is $L/v$, and the total intervention time adds preparation and isolation, "
          "turnaround between deployments, verification and return to service, whose durations are assumed (Table 2). If steam reaches the tool through the pipe, it must also heat the steel wall of the whole line behind it,"))
add(("eq", r"\dot{m}'_{s}=\frac{\rho_{s}A_{s}c_{s}\,(T_{sat}-T_{p})}{h_{fg}}+\dot{m}'_{melt}", 7))
add(("p", "per metre of line, with the steel cross-section $A_{s}$ of standard-wall pipe ($\\rho_{s}=7{,}850$ kg/m$^{3}$, $c_{s}=490$ J/kg·K), the pipe temperature $T_{p}$ and the melting steam $\\dot{m}'_{melt}$ of Section 3.3. "
          "The radial clearance (tracks, cleats, skirt) is that of the first design in a 12 in pipe, 44 mm; the hull is scaled for other sizes by reducing the pack radius, and then the aerogel, down to a 25 mm pack. "
          "The maintenance lattice of the first suite (a periodic $48\\times24$ lattice of wall cells fouled at a rate $r_{f}(1+\\gamma n_{f}/4)$ and cleared with probability $p$ per pass, checked against its exact solution for $\\gamma=0$ [@MyUncle]) is retained "
          "and reported in Section 6.8; it is not calibrated to any deposit."))

# ============================================================================================ 4 Methodology
add(("h1", "4. Monte Carlo methodology"))
add(("p", "All inputs are sampled independently from the distributions in Table 2 with fixed seeds. The thermal studies use %s draws per scenario (800 for the sweeps), the surge study %s, and probabilities carry Wilson 95%% intervals [@Wilson1927]. "
          "Sensitivity is reported as the Spearman rank correlation of each input with the output [@Saltelli2008]. Common random numbers are used across the retained-film, coverage and steam studies, so differences between cases are not sampling noise. "
          "The distributions are assumed design-stage values, not measurements; no published distribution of these quantities for the deposits, steam conditions or tool was found." % (n(R["N"]), n(R["N_surge"]))))
add(("table", "Table 2. Principal sampled or assumed inputs.", ["Input", "Distribution or value"],
     [["Aerogel thickness; k multiplier", "40 mm × (1 + N(0, 0.03)) (swept 5–60 mm); lognormal σ = 0.15 (× lognormal σ = 0.30 and 5% vacuum loss when evacuated)"],
      ["Pack mass; heat generation; initial temperature", "N(16, 1.2) kg; lognormal, median 70 W, σ = 0.35; N(25, 4) °C (shifted 0–55 °C in Section 6.5)"],
      ["Thermal-bridge fraction; condensation multiplier; non-condensable factor", "U(0.05, 0.30); lognormal σ = 0.15; U(0.5, 1.0)"],
      ["Steam saturation temperature", "N(198, 3) °C truncated to 185–204 °C"],
      ["Deposit thickness; melt point; density; latent heat", "lognormal, median 6 mm, σ = 0.5 (1–40 mm); N(58, 8) °C; N(850, 40) kg/m³; N(200, 30) kJ/kg"],
      ["Pipe temperature; heat-coupling fraction η; contact length", "N(25, 5) °C; U(0.15, 0.50); U(0.3, 0.8) m"],
      ["Retained melt film s; liquid conductivity", "swept 0–5 mm (not sampled); 0.15 W/m·K"],
      ["Break-through ΔP; gas-pocket volume; downstream pressure", "lognormal, median 3 bar, σ = 0.6 (0.5–25 bar); lognormal, median 1 m³, σ = 0.7 (0.2–10 m³); U(5, 30) bar"],
      ["Seal friction; downstream drag; masses", "lognormal, median 400 N; lognormal, median 2,000 N s²/m²; N(80, 8) kg pig, N(120, 10) kg crawler"],
      ["Braking limit; traction limit; relief lag", "N(2.5, 0.4) kN; N(1.5, 0.2) kN; U(5, 30) ms"],
      ["Bypass area; discharge coefficient; crack differential", "swept 0–320 cm² (pipe 707 cm²); 0.7; 0.5 bar"],
      ["Assumed logistics durations (h)", "preparation and isolation U(3, 8); turnaround between deployments U(1, 3); verification U(1, 3); return to service U(2, 6)"]], [1.4, 3.0]))
