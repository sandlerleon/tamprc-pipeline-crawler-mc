# -*- coding: utf-8 -*-
"""Cover letter for the submission to Applied Thermal Engineering (Elsevier); numbers from results/*.json, DOIs from dois.json.

    python build_cover_letter.py   -> manuscript/TAMPRC_Cover_Letter.docx
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt, Inches

from common import *

c10 = COV["45 min atmospheric|ablation|1000"]
RV = PT["revised_envelope"]
d = Document()
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(8)
for s in d.sections:
    s.left_margin = s.right_margin = Inches(1.0); s.top_margin = s.bottom_margin = Inches(0.75)


def para(t, bold=False, after=None):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


para("Leon Sandler", True, 0)
for t in ("Independent Researcher", "Northbrook, Illinois, USA", "sandler.leon@gmail.com", "ORCID 0009-0007-4584-808X"):
    para(t, after=0)
para("")
para(datetime.date.today().strftime("%d %B %Y").lstrip("0"))
para("The Editor-in-Chief", after=0); para("Applied Thermal Engineering", after=0); para("Elsevier")
para("Dear Editor,")
para("I submit the manuscript “%s” as a research article for consideration in Applied Thermal Engineering." % TITLE)
para("When steam is used to melt a deposit from a pipe wall, the heat reaches the solid through a condensate film and through any molten deposit that stays on the surface, and the same steam attacks the insulation that protects the equipment doing the work. "
     "The manuscript treats this coupled condensation–melting problem through one application, a tracked crawler for steam-assisted cleaning of hydrocarbon pipelines, with a probabilistic model that couples transient conduction through an aluminium, silica-aerogel and titanium wall "
     "to a lumped battery pack, film condensation, a melt model with a retained liquid film, an orifice model of the pressure relief, and a steam budget.")
para("The manuscript makes five contributions to the thermal-engineering literature. (i) The retained film is expressed through a dimensionless resistance Π_f = h s / k_l, so that the heat flux is q_0/(1 + Π_f), and is predicted by a dynamic balance of melt production and gravity "
     "drainage instead of being prescribed: the median range per deployment is %s m if the melt leaves at once, %s m with the dynamic film (%s mm) and %s m if none drains, and a range of 100 m needs Π_f below about %s. "
     "(ii) The quasi-steady melt formulas and the conduction solver are benchmarked against an independent enthalpy-method solver, the exact Neumann solution and an independent stiff-ODE integration (errors below %s%% for instant removal; the no-drainage formula is %s%% too fast), "
     "and the three condensation representations compared; the coupled model could not be validated, because no experiment was identified, and the manuscript says so. (iii) Global (Sobol) sensitivity and correlated-input analyses, and a separation of the spread caused by model form (a factor of %s in the median range) "
     "from the spread caused by parameters within a model. (iv) A constrained design search and Pareto set, and a pressure–temperature check that shows the first design's steam at 198 °C exceeding a Class 150 rating, with a revised envelope (%s °C) that costs %s%% of the range. "
     "(v) Deployment limits quantified: no 45 min deployment reaches 300 m at the set-point, the hull does not fit pipes below 8 in, the pack probability falls from %s at 25 °C to %s at 45 °C, "
     "and heating the pipe wall adds %s times the melting steam."
     % (n(BB["range_median_m"]), n(DY["baseline"]["range_median_m"]), n(DY["baseline"]["s_end_median_mm"], 2), n(ND["range_nodrain_median_m"], 1), n(DY["Pi_f_for_100m_median"], 1), n(100 * max(abs(r["err_ablation"]) for r in BSF["convective"]), 0),
        n(100 * abs(sum(r["err_nodrain"] for r in BSF["convective"]) / len(BSF["convective"])), 0),
        n(max(HM["nusselt"]["range_median_m_s0"], DY["baseline"]["range_median_m"], ND["range_nodrain_median_m"]) / ND["range_nodrain_median_m"], 0),
        n(PT["Tmax_class150_C"] - 3), n(100 * (1 - RV["revised, Class 150 limit"]["range_median_m"] / RV["original 198 C"]["range_median_m"]), 0), pc(A_ATM["P_safe"], 1), pc(ENV[45.0]["P_safe_atm"], 0), n(STM[12]["wall_ratio"], 1)))
para("The study is explicit about what it is. Every input distribution is an assumed design-stage value, because no published distribution of these deposits, steam conditions or tool was found; the numerical implementation is verified (the first suite is retained unchanged, every added mechanism "
     "reduces to it when switched off, and 53 automated checks pass) but the coupled model is not validated physically; and the success percentages are model probabilities under the assumed distributions, not field reliabilities. The conclusions rank the measurements that would matter most, "
     "beginning with the retained melt film on steel.")
para("The code and results are openly available at %s and archived at https://doi.org/%s (code, all versions); the manuscript and its Supplementary Information are archived at https://doi.org/%s "
     "(all versions). One command regenerates every number and figure." % (GITHUB, DOIS["code_concept"], DOIS["paper_concept"]))
para("Disclosure. The application was taken from a public industrial scouting challenge on a third-party innovation platform; I have no financial relationship with the seeker or the platform, and the work received no external funding.")
para("Author affiliation and email address. I am an independent researcher with no current institutional affiliation, and I am the sole author. The corresponding-author email address, sandler.leon@gmail.com, is my personal address.")
para("A generative AI tool (Claude, Anthropic) assisted with code development, numerical experiments, drafting and editing; I reviewed and checked all of it and take full responsibility for the content, as disclosed in the manuscript. "
     "The manuscript is original, has not been published elsewhere and is not under consideration at any other journal. I am the sole author and have no competing interests.")
para("Thank you for considering this submission.")
para("Sincerely,")
para("Leon Sandler", True)
out = os.path.join(OUT, "TAMPRC_Cover_Letter.docx")
d.save(out)
print("saved", out)
