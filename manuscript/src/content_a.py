# -*- coding: utf-8 -*-
"""Manuscript, part A: Introduction, concept and operating envelope, model, methodology (Sections 1-4)."""
from common import *

# ============================================================================================ 1 Introduction
add(("h1", "1. Introduction"))
add(("p", "Wax, asphaltene, scale and sediment deposits narrow the bore of upstream hydrocarbon pipelines, raise the pressure loss and degrade the product. Wax deposition has been studied extensively [@Aiyejina2011;@Huang2016], and the usual "
          "remedies are high-volume flushing, chemical treatment and mechanical pigging. Each has a known cost: abrasive or mechanical cleaning can wear the wall and generates solid waste, and a passive pig can stall behind a heavy deposit "
          "and then surge, because the gas stored behind it expands when the blockage lets go [@Kim2022]; bypass valves that vent the gas are used to control the speed of pigs in gas lines [@Nguyen2001;@Zhu2014]. Ice-slurry pigging has been developed for water mains and process plant [@Quarini2002;@Quarini2010]. A scouting challenge "
          "published by an energy company has recently asked for cleaning solutions for pipelines of 4 to 16 inches and up to 1 km that have no dedicated launcher or receiver and can be reached only through a connection aligned with the flow [@YPF2026]."))
add(("p", "Thermal mobilization with steam is an obvious alternative to abrasion, because condensation delivers a large heat flux at a modest temperature difference. A tool that carries steam into a line and melts the deposit ahead of itself "
          "is a coupled heat-transfer system: steam condenses on a cold, wax-covered wall; the heat is conducted through the condensate film and through any molten deposit that stays on the surface before it melts the solid; the melt either leaves the surface or "
          "does not; and the same steam attacks the insulation that protects the tool's battery. This paper studies that coupling for one concept, a tracked, self-propelled crawler with an elastomeric sealing skirt (the Thermally Assisted Motorized Pipeline "
          "Remediation Crawler, TAMPRC), and asks which of its limits are set by heat transfer and which by the tool and the line."))
add(("p", "The first suite of the study (thermal shield, melt kinetics, surge, maintenance lattice) was written as a design-screening model and is retained unchanged in the repository. This paper re-examines its assumptions in the order that matters "
          "for a thermal-engineering reader. (i) The melt model assumed that molten deposit leaves the surface at once. Allowing a retained liquid film adds a conduction resistance, which we express as a dimensionless group $\\Pi_f=hs/k_l$, "
          "and we predict the film with a dynamic balance of melt production and gravity drainage instead of prescribing it. (ii) The condensation correlation was derived for the outside of a horizontal tube; we compare it with an internal-flow correlation and "
          "a noncondensable-gas limit. (iii) The melt-time formulas and the conduction solver are benchmarked against an independent enthalpy-method solver, the exact Neumann solution and an independent stiff-ODE integration. "
          "(iv) Sensitivity is analyzed globally (Sobol indices) and for correlated inputs, and the spread caused by the choice of model form is separated from the spread caused by parameter uncertainty. "
          "(v) The design variables are searched under constraints and the Pareto set is reported. (vi) The steam pressure is checked against flange ratings and a revised operating envelope is derived. Deployment limits (pipe length, size, temperature), "
          "the surge on blockage release and the steam budget complete the study. With every added mechanism switched off the extended model reproduces the first suite draw for draw (Section 5). "
          "All input distributions are assumed, and no measurement of these deposits, steam conditions or tool was available; the paper therefore reports model probabilities under assumed inputs, not field reliabilities, and ranks the measurements that would matter."))

# ============================================================================================ 2 Concept and envelope
add(("h1", "2. Concept and operating envelope"))
add(("p", "The tool (Fig. @F:arch@) is a crawler of about 120 kg with cleated tracks and an elastomeric sealing skirt. Steam condenses on the deposit face ahead of the skirt, delivers latent heat and melts the deposit in place, and the skirt sweeps the "
          "liquefied residue forward. The battery pack, motors and electronics sit in a sealed vessel inside a concentric stack of aluminum shell, silica aerogel [@Koebel2012] and titanium hull; an evacuated (vacuum-jacketed) variant is also evaluated. "
          "Brushless motors drive the tracks and act as regenerative brakes against a speed setpoint of 0.10 m/s, and a seal-differential bypass valve is added to relieve the pressure when a blockage releases."))
add(("fig", "Fig1_cross_section.png", "Fig. @F:arch@. Cross-section of the crawler hull (not to scale): pack, aluminum shell, silica aerogel, titanium hull and the steam film.", 2.6))
add(("p", "Table @T:envelope@ lists the operating envelope that the brief states [@YPF2026] next to what the modeled tool assumes. The tool modeled here is at concept stage (technology readiness level 2 to 3), below the 4 to 6 that the brief "
          "requires, and this paper does not claim otherwise."))
add(("table", "Table @T:envelope@. Operating envelope in the published brief and in the model.", ["Item", "Brief [@YPF2026]", "Modeled tool"],
     [["Pipe diameter", "4 to 16 in", "12 in (0.30 m bore) baseline; 4 to 16 in studied in Section 6.7"],
      ["Pipe length", "about 0.3 m to 1 km", "one 45 min deployment; 0.3 m to 1 km studied in Section 6.6"],
      ["Material", "carbon steel", "carbon steel, standard wall"],
      ["Deposits", "paraffin, sediment, scale, sludge, residue", "meltable paraffin only (melt point 58 ± 8 °C); solids not modeled"],
      ["Access", "connection aligned with the flow; no fixed launcher or receiver", "not modeled; tool recovery and steam path are open design items"],
      ["Stages", "preparation, isolation, cleaning, residue collection, verification, return to service", "active cleaning and assumed logistics durations (Section 6.6)"],
      ["Readiness", "technology readiness level 4 to 6", "level 2 to 3 (simulation only)"]], [1.0, 2.0, 2.6]))
add(("p", "Steam delivery. Fig. @F:path@ shows the three ways in which steam can reach the deposit face. The model assumes arrangement (a): steam is fed through a line that passes through the tool and discharges ahead of the sealing skirt into a steam zone of length "
          "$L_z$ (0.3 to 0.8 m) between the skirt and the deposit face. The skirt closes the zone, so the steam condenses on the deposit face and on the pipe wall inside the zone, the melt drains along the wall and collects as a pool at the invert, and the hull is exposed to saturated steam "
          "only in that zone. In arrangement (b) steam travels through the pipe behind the tool and reaches the zone through ports in the skirt, and it heats the whole pipe wall on the way (Section 6.11); in (c) a hose carried inside the pipe feeds the lance, which avoids "
          "the wall heating at the price of tether drag over up to 1 km and a second line at the steam temperature. In all three, steam must enter the line through the connection by which the tool enters, which needs a pressure-sealed gland or hose and is not designed here. "
          "The choice changes the steam budget and the hull exposure, not the melt model of Section 3, which depends only on the steam temperature and contact length at the deposit face."))
add(("fig", "Fig2_steam_path.png", "Fig. @F:path@. Steam delivery to the deposit face: (a) forward lance through the tool (assumed by the model), (b) steam through the pipe behind the tool and ports in the skirt, (c) hose inside the pipe feeding a lance. Not to scale.", 5.6))
add(("p", "The saturation temperature must be compatible with the pressure rating of the line: the first design used steam at 198 °C, which is 1.49 MPa, and Section 6.8 shows that this exceeds the rating "
          "of a Class 150 carbon-steel flange at that temperature and derives a revised envelope. Equipment protection for explosive atmospheres [@IEC60079] and the recovery of a stalled tool are discussed in Section 7.3."))

# ============================================================================================ 3 Model
add(("h1", "3. Mathematical model"))
add(("h2", "3.1 Transient conduction in the composite wall"))
add(("p", "The radial temperature $T(r,t)$ in the composite wall (aluminum shell, silica aerogel, titanium hull) obeys one-dimensional cylindrical conduction,"))
add(("eq", r"\rho\,c_{p}(T)\,\frac{\partial T}{\partial t}=\frac{1}{r}\frac{\partial}{\partial r}\left[r\,k(T)\,\frac{\partial T}{\partial r}\right]", 1))
add(("p", "with density $\\rho$, specific heat $c_{p}$ and conductivity $k$. For atmospheric-pressure aerogel $k=k_{0}[1+\\alpha(T-25)]$ with $k_{0}=0.018$ W/m·K and a slope of $8\\times10^{-5}$ W/m·K$^{2}$; for the evacuated jacket "
          "$k=0.0040+2.5\\times10^{-5}(T-25)$ W/m·K. Both are multiplied by a lognormal factor for compaction, moisture and lot variation. The outer boundary exchanges heat with saturated steam through a film coefficient capped at 12 kW/m²·K, the inner boundary "
          "with a lumped battery pack (heat capacity $m_{pack}c_{p}/L$ per unit length, source $P_{gen}/L$), and a parallel bridge conductance (tracks, end caps) equal to a fraction $\\phi\\sim U(0.05,0.30)$ of the nominal aerogel conductance joins "
          "hull and pack. The pack limit is $T_{crit}=55$ °C; this is an assumed design limit, conservative relative to the onset of self-heating reported for lithium-ion cells [@Feng2018], and no cell-level analysis is made. Eq. (1) is discretized by "
          "finite volumes (2 shell, 16 aerogel and 2 hull cells) and integrated with backward Euler at 10 s, with the conductivity lagged one step."))
add(("h2", "3.2 Film condensation: three representations"))
add(("p", "The first suite used the Nusselt film correlation [@Nusselt1916;@Incropera2007], derived for the outside of a horizontal tube, with a conduit diameter $D$,"))
add(("eq", r"h=0.728\left[\frac{g\,\rho_{l}(\rho_{l}-\rho_{v})\,k_{l}^{3}\,h'_{fg}}{\mu_{l}\,D\,(T_{sat}-T_{w})}\right]^{1/4},\qquad h'_{fg}=h_{fg}+0.68\,c_{p,l}(T_{sat}-T_{w})", 2))
add(("p", "with saturated-water properties near 1.55 MPa, a lognormal multiplier ($\\sigma=0.15$) and a noncondensable-gas factor $U(0.5,1)$. Inside a horizontal tube at low vapor velocity the condensate drains to the invert and the film is stratified; "
          "the correlation of Chato [@Chato1962;@Dobson1998] has the same form with the coefficient 0.555 and $h'_{fg}=h_{fg}+\\tfrac{3}{8}c_{p,l}(T_{sat}-T_{w})$. A third, conservative representation for the range fixes the noncondensable factor at its lower bound 0.5. "
          "All three scale as $D^{-1/4}$. They are compared in Sections 5 and 6.3. An impingement model is not applied, because the steam path (a forward lance or annulus) is not defined; the steam-side coefficient on the hull is capped at 12 kW/m²·K in every case."))
add(("h2", "3.3 Deposit melting and the retained-film resistance"))
add(("p", "A deposit of thickness $\\delta$ and melt point $T_{m}$ needs the energy per unit area $e=\\rho_{d}\\delta[L_{f}+c_{d}(T_{m}-T_{0})]$. The first suite assumed that molten deposit leaves the surface at once (ablation), so that the heat flux is "
          "that of the condensate film at the melt temperature, $q=h(T_{sat}-T_{m})$. A liquid layer of thickness $s$ that stays on the surface adds a conduction resistance in series with the condensate film. With the liquid conductivity $k_{l}$ "
          "and a fraction $\\eta\\sim U(0.15,0.50)$ of the flux reaching the deposit,"))
add(("eq", r"q_{eff}=\eta\,\frac{T_{sat}-T_{m}}{1/h+s/k_{l}}=\frac{q_{0}}{1+\Pi_{f}},\qquad \Pi_{f}=\frac{h\,s}{k_{l}},\qquad t_{m}=\frac{e}{q_{eff}},\qquad v=\min\left(v_{set},\frac{L_{z}}{t_{m}}\right)", 3))
add(("p", "where $q_{0}$ is the flux without a film, $L_{z}\\sim U(0.3,0.8)$ m is the steam contact length and $v_{set}=0.10$ m/s. The dimensionless group $\\Pi_{f}$ is the ratio of the film's conduction resistance to the condensate film's: for $\\Pi_{f}=1$ the retained "
          "film halves the heat flux. Setting $s=0$ recovers the first suite exactly. The opposite limit, in which no melt drains and the layer grows from 0 to $\\delta$, gives"))
add(("eq", r"t_{nd}=\frac{\rho_{d}[L_{f}+c_{d}(T_{m}-T_{0})]\,(\delta/h+\delta^{2}/2k_{l})}{\eta\,(T_{sat}-T_{m})}", 4))
add(("p", "The liquid conductivity is assumed ($k_{l}=0.15$ W/m·K). The cleaned range of a deployment is $v\\,\\min(t_{crit},t_{run})$, where $t_{crit}$ is the first time the pack reaches 55 °C and $t_{run}$ the mission length (45 min). Both the instant-removal and "
          "no-drainage formulas are quasi-steady and are benchmarked in Section 5."))
add(("h2", "3.4 Dynamic retained film"))
add(("p", "Instead of prescribing $s$, a surface element in the steam zone is advanced in time. The melted thickness $x$ grows at the rate set by the flux through the film, and the film thickness is the difference between the volume of melt produced and the volume that drains "
          "under gravity as a Nusselt film along the wall between the crown and the invert (path $\\ell=\\pi D/4$, mean $\\sin\\theta=0.7$),"))
add(("eq", r"\frac{dx}{dt}=\frac{q_{eff}(s)}{\rho_{d}[L_{f}+c_{d}(T_{m}-T_{0})]},\qquad \frac{ds}{dt}=\frac{\rho_{d}}{\rho_{l}}\frac{dx}{dt}-\frac{\rho_{l}\,g\sin\theta\,(s-s_{res})^{3}}{3\,\mu_{l}\,\ell}", 5))
add(("p", "with the molten-paraffin density $\\rho_{l}=770$ kg/m$^{3}$ and viscosity $\\mu_{l}$ lognormal with median 4 mPa·s and $\\sigma=0.3$ (assumed), and a residual wetting film $s_{res}$ (zero in the baseline, 0.02 and 0.05 mm in the sensitivity study). "
          "The element is melted through when $x=\\delta$, which gives $t_{m}$ and $v_{th}=L_{z}/t_{m}$. The model is a quasi-steady conduction film with gravity drainage; it ignores the molten pool at the invert, which the skirt pushes ahead, "
          "the shear of the steam on the film, and the temperature dependence of the viscosity. Its two limits are exact: for instant drainage it reproduces the ablation time, and for no drainage it approaches Eq. (4) (Section 5). "
          "Wall orientation (through $\\sin\\theta$), an interfacial steam shear $\\tau$ (adding a film flux $\\tau s^{2}/2\\mu_l$ to the gravity term) and the molten pool are examined in Section 6.4."))
add(("h2", "3.5 Blockage release with an orifice bypass"))
add(("p", "From breakthrough the tool of mass $m$ obeys"))
add(("eq", r"m\,\frac{dv}{dt}=A\,\Delta P\,(1-\beta)-F_{f}-c_{d}v^{2}-F_{c}", 6))
add(("p", "with pipe area $A$, seal friction $F_{f}$, downstream drag $c_{d}$ and controller force $F_{c}$ (PI on speed, limited to the braking and traction authority). The first suite represented the bypass relief by a factor $\\beta\\to\\beta_{max}[1-0.5\\ \\mathrm{bar}/\\Delta P]$ "
          "(0.85 to 0.97) with a 5 to 30 ms lag, that is, as a force reduction without a flow. Here the upstream gas pocket (initial volume $V_{0}$, pressure $P_{0}=P_{d}+\\Delta P_{b}$) expands adiabatically as the tool advances a distance $x$ and "
          "loses its gas through the bypass,"))
add(("eq", r"P_{u}=P_{0}\left(\frac{\varphi V_{0}}{V_{0}+A\,x}\right)^{\gamma},\qquad \frac{d\varphi}{dt}=-\frac{\dot{m}_{b}}{m_{0}},\qquad \dot{m}_{b}=C_{d}A_{b}\,u\,P_{u}\sqrt{\frac{2\gamma}{(\gamma-1)RT}}\sqrt{r^{2/\gamma}-r^{(\gamma+1)/\gamma}}", 7))
add(("p", "where $\\varphi$ is the remaining gas fraction, $m_{0}=P_{0}V_{0}/RT$, $r=\\max(P_{d}/P_{u},r_{c})$ with $r_{c}$ the critical ratio (choked flow), $A_{b}$ the bypass flow area, $C_{d}=0.7$ and $u\\in[0,1]$ the valve opening, which follows "
          "the demand $(\\Delta P-0.5\\ \\mathrm{bar})/(0.5\\ \\mathrm{bar})$ with the same 5 to 30 ms lag. The gas is methane-like ($R=518$ J/kg·K, $T=300$ K, $\\gamma=1.3$, assumed) and the downstream pressure is held constant. With $A_{b}=0$ the "
          "model reduces to the first suite's crawler without relief."))
add(("h2", "3.6 Pipe length, logistics and steam budget"))
add(("p", "For a line of length $L$ and a deployment range $R_{dep}=v\\,t_{run}$, the number of deployments is the smallest integer not below $L/R_{dep}$, the active cleaning time is $L/v$, and the total intervention time adds preparation and isolation, "
          "turnaround between deployments, verification and return to service, whose durations are assumed (Table @T:inputs@). If steam reaches the tool through the pipe, it must also heat the steel wall of the whole line behind it,"))
add(("eq", r"\dot{m}'_{s}=\frac{\rho_{s}A_{s}c_{s}\,(T_{sat}-T_{p})}{h_{fg}}+\dot{m}'_{melt}", 8))
add(("p", "per meter of line, with the steel cross-section $A_{s}$ of standard-wall pipe ($\\rho_{s}=7{,}850$ kg/m$^{3}$, $c_{s}=490$ J/kg·K), the pipe temperature $T_{p}$ and the melting steam $\\dot{m}'_{melt}$ of Section 3.3. "
          "The radial clearance (tracks, cleats, skirt) is that of the first design in a 12 in pipe, 44 mm; the hull is scaled for other sizes by reducing the pack radius, and then the aerogel, down to a 25 mm pack. "
          "The saturation pressure is computed from the IAPWS-IF97 saturation line [@Wagner1998]. The maintenance lattice of the first suite (a periodic $48\\times24$ lattice of wall cells fouled at a rate $r_{f}(1+\\gamma n_{f}/4)$ and cleared "
          "with probability $p$ per pass, checked against its exact solution for $\\gamma=0$ [@MyUncle]) is retained and reported in the Supplementary Information; it is not calibrated to any deposit."))
add(("h2", "3.7 Global sensitivity and constrained design"))
add(("p", "For a scalar output $Y=f(\\mathbf{X})$ of independent inputs, the first-order and total Sobol indices are $S_{i}=\\mathrm{Var}[E(Y|X_{i})]/\\mathrm{Var}(Y)$ and $S_{Ti}=E[\\mathrm{Var}(Y|\\mathbf{X}_{\\sim i})]/\\mathrm{Var}(Y)$ [@Sobol2001;@Saltelli2008]. They are estimated with the "
          "Jansen estimators [@Jansen1999;@Saltelli2010] on scrambled Sobol sequences, with bootstrap intervals. The design search is the constrained problem"))
add(("eq", r"\max_{\mathbf{x}}\ \mathrm{median}(R_{dep})\quad\mathrm{subject\ to}\quad P(T_{pack}\le55\,^{\circ}\mathrm{C}\ \mathrm{through}\ t_{run})\ge0.95,\ \ D_{hull}\le D_{fit},\ \ v_{set}\le0.20\ \mathrm{m/s},\ \ t_{run}\le90\ \mathrm{min}", 9))
add(("p", "over the aerogel thickness (10 to 60 mm), the jacket (atmospheric or evacuated), the mission length and the speed setpoint, for each melt-removal assumption. The Pareto set is taken over the median range (maximize), the melting steam per meter (minimize), the hull diameter "
          "(minimize) and the thermal probability (maximize). A surge-speed constraint $v_{peak}\\le v_{safe}$ is not imposed on this search, because the surge depends on the blockage and the bypass, not on these variables (Section 6.10), and a safe speed has not been justified for any line."))

# ============================================================================================ 4 Methodology
add(("h1", "4. Monte Carlo methodology"))
add(("p", "Input uncertainty is propagated by Monte Carlo sampling [@Metropolis1949]. All inputs are sampled independently from the distributions in Table @T:inputs@ with fixed seeds, except where correlation is studied (Section 6.5, Gaussian copula). The thermal studies use %s draws per scenario (800 for the sweeps), the surge study %s, and probabilities carry Wilson 95%% intervals [@Wilson1927]. "
          "Common random numbers are used across the retained-film, coverage, condensation-model and steam studies, so differences between cases are not sampling noise. The distributions are assumed design-stage values, not measurements; "
          "no published distribution of these quantities for the deposits, steam conditions or tool was found. Two kinds of uncertainty are kept apart: the spread within a model caused by uncertain parameters (the 5th to 95th percentile of a case) and the spread "
          "between models caused by the choice of model form (condensation correlation, melt-removal model). The success percentages are model probabilities under the assumed distributions; without calibration they are not field reliabilities." % (n(R["N"]), n(R["N_surge"]))))
add(("table", "Table @T:inputs@. Principal sampled or assumed inputs.", ["Input", "Distribution or value"],
     [["Aerogel thickness; k multiplier", "40 mm × (1 + N(0, 0.03)) (swept 5–60 mm); lognormal σ = 0.15 (× lognormal σ = 0.30 and 5% vacuum loss when evacuated)"],
      ["Pack mass; heat generation; initial temperature", "N(16, 1.2) kg; lognormal, median 70 W, σ = 0.35; N(25, 4) °C (shifted 0–55 °C in Section 6.7)"],
      ["Thermal-bridge fraction; condensation multiplier; noncondensable factor", "U(0.05, 0.30); lognormal σ = 0.15; U(0.5, 1.0)"],
      ["Steam saturation temperature", "N(198, 3) °C truncated to 185–204 °C (revised envelope: Section 6.8)"],
      ["Deposit thickness; melt point; density; latent heat", "lognormal, median 6 mm, σ = 0.5 (1–40 mm); N(58, 8) °C; N(850, 40) kg/m³; N(200, 30) kJ/kg"],
      ["Pipe temperature; heat-coupling fraction η; contact length", "N(25, 5) °C; U(0.15, 0.50); U(0.3, 0.8) m"],
      ["Retained melt film s; liquid conductivity", "swept 0–5 mm, or lognormal (median 0.2 mm, σ = 1.0) in the Sobol study; dynamic in Section 6.4; 0.15 W/m·K"],
      ["Molten-paraffin viscosity; density; drain path", "lognormal, median 4 mPa·s, σ = 0.3; 770 kg/m³; πD/4 (sensitivity ×0.25 and ×4)"],
      ["Breakthrough ΔP; gas-pocket volume; downstream pressure", "lognormal, median 3 bar, σ = 0.6 (0.5–25 bar); lognormal, median 1 m³, σ = 0.7 (0.2–10 m³); U(5, 30) bar"],
      ["Seal friction; downstream drag; masses", "lognormal, median 400 N; lognormal, median 2,000 N s²/m²; N(80, 8) kg pig, N(120, 10) kg crawler"],
      ["Braking limit; traction limit; relief lag", "N(2.5, 0.4) kN; N(1.5, 0.2) kN; U(5, 30) ms"],
      ["Bypass area; discharge coefficient; crack differential", "swept 0–320 cm² (pipe 707 cm²); 0.7; 0.5 bar"],
      ["Assumed logistics durations (h)", "preparation and isolation U(3, 8); turnaround between deployments U(1, 3); verification U(1, 3); return to service U(2, 6)"]], [1.4, 3.0]))
