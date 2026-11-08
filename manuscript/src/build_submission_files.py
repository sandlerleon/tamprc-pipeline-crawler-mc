# -*- coding: utf-8 -*-
"""Separate submission files in the usual Elsevier layout: highlights (3-5 bullets, at most 85 characters each, own file) and a title page with the author details and declarations.
The layout follows the usual Elsevier conventions; the current guide for authors of the journal could not be fetched while preparing this version and must be checked before upload.

    python build_submission_files.py   -> manuscript/TAMPRC_Highlights.docx, manuscript/TAMPRC_Title_Page.docx
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt, Inches

from common import *
import content_front                                   # noqa: E402,F401   (defines the highlights)

HIGH = content_front.HIGH


def new_doc():
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(6)
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(1.0); s.top_margin = s.bottom_margin = Inches(0.9)
    return d


d = new_doc()
p = d.add_paragraph(); r = p.add_run("Highlights"); r.bold = True; r.font.size = Pt(14)
d.add_paragraph(TITLE)
for h in HIGH:
    assert len(h) <= 85
    d.add_paragraph(h, style="List Bullet")
d.save(os.path.join(OUT, "TAMPRC_Highlights.docx"))

d = new_doc()
p = d.add_paragraph(); r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(14)
d.add_paragraph("Leon Sandler")
d.add_paragraph("Independent Researcher, Northbrook, Illinois, USA")
d.add_paragraph("ORCID: https://orcid.org/0009-0007-4584-808X")
d.add_paragraph("Corresponding author: Leon Sandler, sandler.leon@gmail.com")
for t in ("Author contributions (CRediT): Leon Sandler, sole author: conceptualization, methodology, software, formal analysis, writing – original draft, writing – review and editing.",
          "Funding: This work received no external funding.",
          "Declaration of competing interest: the author declares no competing interests. The concept was prepared as a response to a public scouting challenge; the author has no financial relationship with its seeker or platform.",
          "Declaration of generative AI and AI-assisted technologies in the writing process: a generative AI tool (Claude, Anthropic) assisted with code development, numerical experiments, drafting and editing. The author checked all of it and takes full responsibility for the content.",
          "Data availability: the code, the data of every figure and table and the manuscript are archived at https://doi.org/%s (software, all versions) and https://doi.org/%s (manuscript, all versions), and are available at %s." % (DOIS["code_concept"], DOIS["paper_concept"], GITHUB)):
    d.add_paragraph(t)
d.save(os.path.join(OUT, "TAMPRC_Title_Page.docx"))
print("saved highlights and title page")
