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
d = Document()
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(8)
for s in d.sections:
    s.left_margin = s.right_margin = Inches(1.0); s.top_margin = s.bottom_margin = Inches(0.8)


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
para("Steam-assisted tools are an attractive alternative to abrasive cleaning of hydrocarbon pipelines, but a tool that works in saturated steam near 200 °C must keep its battery and electronics cool, melt the deposit fast enough to "
     "matter, and control its speed when a blockage releases. The manuscript treats these three problems for one concept, a motorized, tracked crawler with a sealing skirt, with a probabilistic reduced-order model: transient conduction "
     "through an aluminium, silica-aerogel and titanium wall coupled to a lumped battery pack, Nusselt film condensation on the deposit, a blockage-release transient with an orifice bypass, and a steam budget. It then tests the concept "
     "against the operating envelope of a published industrial scouting challenge (pipes of 4 to 16 inches and up to 1 km, no fixed launcher, access through a connection aligned with the flow).")
para("The manuscript makes four contributions. (i) A thermal result with its condition: with 40 mm of aerogel the pack stays at or below 55 °C for 45 min in %s of %s draws, but the probability falls to %s at 35 °C and %s at 45 °C, "
     "and the hull does not fit pipes below 8 in. (ii) A finding about melt kinetics: the cleaned range of %s m per deployment that follows from instant removal of the molten deposit falls to %s m with a retained film 0.2 mm thick and to "
     "%s m if none drains, so a quantity nobody has measured, the retained melt film, decides the reach. (iii) A finding about logistics: no 45 min deployment reaches 300 m, a 1 km line needs a median of %s deployments, and heating the pipe "
     "wall adds %s times the melting steam. (iv) A finding about surge control: a bypass valve that is closed at the stall cannot arrest the first surge peak, because the tool reaches 1 m/s in about %s ms, a time scale that the earlier "
     "force-factor treatment of the relief hid; a bypass that is open during the stall is the design alternative."
     % (pc(A_ATM["P_safe"], 1), n(R["N"]), pc(ENV[35.0]["P_safe_atm"], 0), pc(ENV[45.0]["P_safe_atm"], 0), n(BB["range_median_m"]), n(FR[0.2]["range_median_m"]), n(ND["range_nodrain_median_m"]), n(c10["n_dep_median"]),
        n(STM[12]["wall_ratio"], 1), n(BY["t_accel_1ms_median_ms"])))
para("The study is explicit about what it is. Every input distribution is an assumed design-stage value, because no published distribution of these deposits, steam conditions or tool was found; the model is verified numerically "
     "(the first suite is retained unchanged, every added mechanism reduces to it when switched off, and 27 automated checks pass) but not validated physically; and the conclusions rank the measurements that would matter, rather than "
     "predicting performance. The concept is at technology readiness level 2 to 3, and the manuscript says so.")
para("The code and results are openly available at %s and archived at https://doi.org/%s (code, all versions); the manuscript and its Supplementary Information are archived at https://doi.org/%s "
     "(all versions). One command regenerates every number and figure." % (GITHUB, DOIS["code_concept"], DOIS["paper_concept"]))
para("Disclosure. The concept was prepared as a response to a public scouting challenge on a third-party innovation platform. I have no financial relationship with the seeker or the platform, and the work received no external funding.")
para("Author affiliation and email address. I am an independent researcher with no current institutional affiliation, and I am the sole author. The corresponding-author email address, sandler.leon@gmail.com, is my personal address.")
para("A generative AI tool (Claude, Anthropic) assisted with code development, numerical experiments, drafting and editing; I reviewed and checked all of it and take full responsibility for the content, as disclosed in the manuscript. "
     "The manuscript is original, has not been published elsewhere and is not under consideration at any other journal. I am the sole author and have no competing interests.")
para("Thank you for considering this submission.")
para("Sincerely,")
para("Leon Sandler", True)
out = os.path.join(OUT, "TAMPRC_Cover_Letter.docx")
d.save(out)
print("saved", out)
