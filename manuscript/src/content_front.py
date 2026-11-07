# -*- coding: utf-8 -*-
"""Manuscript front matter: title, author, highlights, abstract, keywords."""
from common import *

C12 = COV["45 min atmospheric|ablation|300"]
C1K = COV["45 min atmospheric|ablation|1000"]
add(("title", TITLE))
add(("author", "Leon Sandler"))
add(("small", "Independent Researcher, Northbrook, Illinois, USA"))
add(("small", "ORCID: https://orcid.org/0009-0007-4584-808X"))
add(("small", "Corresponding author: sandler.leon@gmail.com"))
add(("blank",))
add(("h1", "Highlights"))
HIGH = [
    "Probabilistic model of a steam-assisted pipeline crawler: heat shield, melt and surge",
    "An %s µm retained melt film already cuts the median range below 100 m" % n(F["s_median_below_100m_mm"] * 1000),
    "No single 45 min deployment cleans 300 m; a 1 km line needs about %s" % (n(C1K["n_dep_median"]) + " runs"),
    "Heating the pipe wall adds %s times the steam needed to melt the deposit" % n(STM[12]["wall_ratio"], 1),
    "A bypass valve closed at the stall cannot arrest the surge impulse",
]
for h in HIGH:
    assert len(h) <= 85, (len(h), h)
    add(("bullet", h))
add(("h1", "Abstract"))
add(("p0", "Steam-assisted tools could remove paraffin deposits from hydrocarbon pipelines without abrasives, but must shield their electronics from steam near 200 °C, melt the deposit fast enough to be useful, "
           "and control speed when a blockage releases. We evaluate a motorized steam-assisted pipeline crawler with a probabilistic reduced-order model: transient conduction through an aluminium–aerogel–titanium wall "
           "coupled to a lumped battery pack, film condensation on the deposit, a blockage-release transient with an orifice bypass, and a steam budget. Inputs are assumed design-stage distributions, and every added "
           "mechanism can be switched off to recover the original model exactly. With 40 mm of aerogel the pack stays at or below 55 °C for 45 min in %s of %s draws, but only in a cool pipe: the "
           "probability falls to %s at 35 °C and %s at 45 °C, and the hull does not fit pipes below 8 in. The cleaned range per deployment, a median of %s m when molten deposit is removed at once, falls to %s m with a "
           "retained melt film 0.2 mm thick and to %s m with none removed. No 45 min deployment reaches 300 m, so a 1 km line needs a median of %s deployments and about %s h under assumed logistics. Heating the pipe wall adds "
           "%s times the melting steam. A bypass that is closed at the stall cannot arrest the surge, because the tool reaches 1 m/s in about %s ms. The results rank the measurements needed; they are not validated "
           "performance."
           % (pc(A_ATM["P_safe"], 1), n(R["N"]), pc(ENV[35.0]["P_safe_atm"], 0), pc(ENV[45.0]["P_safe_atm"], 0), n(BB["range_median_m"]), n(FR[0.2]["range_median_m"]), n(ND["range_nodrain_median_m"]),
              n(C1K["n_dep_median"]), n(C1K["total_h_median"]), n(STM[12]["wall_ratio"], 1), n(BY["t_accel_1ms_median_ms"]))))
add(("h1", "Keywords"))
add(("p0", "Pipeline pigging; Paraffin deposition; Film condensation; Silica aerogel; Transient heat conduction; Monte Carlo simulation"))
