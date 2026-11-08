# -*- coding: utf-8 -*-
"""Manuscript front matter: title, author, highlights, abstract, keywords."""
from common import *

C1K = COV["45 min atmospheric|ablation|1000"]
RV = X["ptcompat"]["revised_envelope"]
add(("title", TITLE))
add(("author", "Leon Sandler"))
add(("small", "Independent Researcher, Northbrook, Illinois, USA"))
add(("small", "ORCID: https://orcid.org/0009-0007-4584-808X"))
add(("small", "Corresponding author: sandler.leon@gmail.com"))
add(("blank",))
add(("h1", "Highlights"))
HIGH = [
    "Retained melt-film resistance, not insulation, limits steam pipeline cleaning",
    "A dynamic film model predicts a %s mm film and %s m median range per deployment" % (n(DY["baseline"]["s_end_median_mm"], 2), n(DY["baseline"]["range_median_m"])),
    "Melt-time formulas are benchmarked against an enthalpy solver and Neumann",
    "A 1 km line needs %s deployments with the dynamic film, %s with instant removal" % (n(CVD["45 min atmospheric|dynamic film|1000"]["n_dep_median"]), n(C1K["n_dep_median"])),
    "Class 150 steam limit (%s °C) costs only %s%% of the range" % (n(PT["Tmax_class150_C"]), n(100 * (1 - RV["revised, Class 150 limit"]["range_median_m"] / RV["original 198 C"]["range_median_m"]))),
]
for h in HIGH:
    assert len(h) <= 85, (len(h), h)
    add(("bullet", h))
add(("h1", "Abstract"))
add(("p0", fmt("Steam-assisted pipeline cleaning couples condensation heat transfer, melting of a deposit and a thermally protected tool, and the coupling, not any single component, sets its limits. We study a motorized steam-assisted crawler with a probabilistic "
               "model: transient conduction through an aluminum–aerogel–titanium wall into a lumped battery pack, film condensation, a melt model with a retained liquid film whose resistance is the dimensionless group $\\Pi_f=hs/k_l$, a dynamic film balancing melt "
               "production and gravity drainage, an orifice model of the bypass relief, and a steam budget. The conduction and melt formulas are benchmarked against an independent solver and the Neumann solution; no experiment was available for the coupled model. "
               "Under assumed input distributions, with 40 mm of aerogel the pack stays at or below 55 °C for 45 min in <<p>> of draws at 25 °C but <<p45>> at 45 °C. The median range per deployment is <<r0>> m if molten deposit leaves at once, <<rd>> m with the dynamic "
               "film (<<s>> mm) and <<rn>> m with none removed; Sobol indices attribute <<sf>> of the range variance to the film. The condensation correlation changes the instant-removal range by <<ch>>%, a Class 150 steam limit of <<tm>> °C by <<rv>>%. "
               "A 1 km line needs a median of <<d1>> deployments with the dynamic film (<<d0>> with instant removal), and the hull does not fit pipes below 8 in. These are model probabilities, not field reliabilities.",
               p=pc(A_ATM["P_safe"], 1), p45=pc(ENV[45.0]["P_safe_atm"], 0), r0=n(BB["range_median_m"]), rd=n(DY["baseline"]["range_median_m"]), s=n(DY["baseline"]["s_end_median_mm"], 2), rn=n(ND["range_nodrain_median_m"]),
               sf=pc(SOB["range_with_film"]["ST"][10], 0), ch=n(100 * (1 - HM["chato"]["range_median_m_s0"] / HM["nusselt"]["range_median_m_s0"])), tm=n(PT["Tmax_class150_C"]),
               rv=n(100 * (1 - RV["revised, Class 150 limit"]["range_median_m"] / RV["original 198 C"]["range_median_m"])), d1=n(CVD["45 min atmospheric|dynamic film|1000"]["n_dep_median"]), d0=n(C1K["n_dep_median"]))))
add(("h1", "Keywords"))
add(("p0", "Condensation heat transfer; Melting with drainage; Paraffin deposition; Silica aerogel; Pipeline pigging; Global sensitivity analysis"))
